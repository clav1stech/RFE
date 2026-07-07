"""Sérialisation d'une :class:`Invoice` en UBL 2.1 (OASIS Universal Business Language).

Produit un XML conforme au profil EN16931 (PEPPOL BIS / Chorus Pro UBL).
"""

from __future__ import annotations

from lxml import etree

from facturx_generator.models import Invoice, Party

NSMAP = {
    None: "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2",
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
}

CUSTOMIZATION_ID = "urn:cen.eu:en16931:2017"
PROFILE_ID = "urn:fdc:peppol.eu:2017:poacc:billing:01:1.0"


def _q(prefix: str | None, tag: str) -> str:
    if prefix is None:
        return f"{{{NSMAP[None]}}}{tag}"
    return f"{{{NSMAP[prefix]}}}{tag}"


def _sub(parent: etree._Element, prefix: str, tag: str, text: str | None = None) -> etree._Element:
    el = etree.SubElement(parent, _q(prefix, tag))
    if text is not None:
        el.text = text
    return el


def _party(parent: etree._Element, prefix_tag: str, party: Party) -> None:
    wrapper = _sub(parent, "cac", prefix_tag)
    party_el = _sub(wrapper, "cac", "Party")
    address = _sub(party_el, "cac", "PostalAddress")
    if party.line_one:
        _sub(address, "cbc", "StreetName", party.line_one)
    if party.city:
        _sub(address, "cbc", "CityName", party.city)
    if party.post_code:
        _sub(address, "cbc", "PostalZone", party.post_code)
    country = _sub(address, "cac", "Country")
    _sub(country, "cbc", "IdentificationCode", party.country_code)
    if party.vat_id:
        tax_scheme = _sub(party_el, "cac", "PartyTaxScheme")
        _sub(tax_scheme, "cbc", "CompanyID", party.vat_id)
        scheme = _sub(tax_scheme, "cac", "TaxScheme")
        _sub(scheme, "cbc", "ID", "VAT")
    legal = _sub(party_el, "cac", "PartyLegalEntity")
    _sub(legal, "cbc", "RegistrationName", party.name)
    if party.legal_id:
        _sub(legal, "cbc", "CompanyID", party.legal_id)


def to_ubl(invoice: Invoice) -> etree._Element:
    """Construit l'arbre XML UBL de la facture."""
    root = etree.Element(_q(None, "Invoice"), nsmap=NSMAP)

    _sub(root, "cbc", "CustomizationID", CUSTOMIZATION_ID)
    _sub(root, "cbc", "ProfileID", PROFILE_ID)
    _sub(root, "cbc", "ID", invoice.invoice_number)  # BT-1
    _sub(root, "cbc", "IssueDate", invoice.issue_date.isoformat())  # BT-2
    if invoice.due_date is not None:
        _sub(root, "cbc", "DueDate", invoice.due_date.isoformat())  # BT-9
    _sub(root, "cbc", "InvoiceTypeCode", invoice.invoice_type_code)  # BT-3
    if invoice.note:
        _sub(root, "cbc", "Note", invoice.note)  # BT-22
    _sub(root, "cbc", "DocumentCurrencyCode", invoice.currency)  # BT-5
    if invoice.buyer_reference:
        _sub(root, "cbc", "BuyerReference", invoice.buyer_reference)  # BT-10

    _party(root, "AccountingSupplierParty", invoice.seller)  # BG-4
    _party(root, "AccountingCustomerParty", invoice.buyer)  # BG-7

    # Ventilation de TVA (BG-23)
    tax_total = _sub(root, "cac", "TaxTotal")
    _sub(tax_total, "cbc", "TaxAmount", f"{invoice.tax_total:.2f}").set(
        "currencyID", invoice.currency
    )
    for tb in invoice.tax_breakdowns:
        subtotal = _sub(tax_total, "cac", "TaxSubtotal")
        _sub(subtotal, "cbc", "TaxableAmount", f"{tb.taxable_amount:.2f}").set(
            "currencyID", invoice.currency
        )
        _sub(subtotal, "cbc", "TaxAmount", f"{tb.tax_amount:.2f}").set(
            "currencyID", invoice.currency
        )
        category = _sub(subtotal, "cac", "TaxCategory")
        _sub(category, "cbc", "ID", tb.category)
        _sub(category, "cbc", "Percent", f"{tb.rate:.2f}")
        scheme = _sub(category, "cac", "TaxScheme")
        _sub(scheme, "cbc", "ID", "VAT")

    # Totaux (BG-22)
    totals = _sub(root, "cac", "LegalMonetaryTotal")
    _sub(totals, "cbc", "LineExtensionAmount", f"{invoice.line_total:.2f}").set(
        "currencyID", invoice.currency
    )
    _sub(totals, "cbc", "TaxExclusiveAmount", f"{invoice.tax_basis_total:.2f}").set(
        "currencyID", invoice.currency
    )
    _sub(totals, "cbc", "TaxInclusiveAmount", f"{invoice.grand_total:.2f}").set(
        "currencyID", invoice.currency
    )
    _sub(totals, "cbc", "PayableAmount", f"{invoice.due_payable:.2f}").set(
        "currencyID", invoice.currency
    )

    # Lignes (BG-25)
    for line in invoice.lines:
        inv_line = _sub(root, "cac", "InvoiceLine")
        _sub(inv_line, "cbc", "ID", line.line_id)
        _sub(inv_line, "cbc", "InvoicedQuantity", f"{line.quantity:.2f}").set(
            "unitCode", line.unit_code
        )
        _sub(inv_line, "cbc", "LineExtensionAmount", f"{line.line_net_amount:.2f}").set(
            "currencyID", invoice.currency
        )
        item = _sub(inv_line, "cac", "Item")
        _sub(item, "cbc", "Name", line.name)
        if line.description:
            _sub(item, "cbc", "Description", line.description)
        item_tax = _sub(item, "cac", "ClassifiedTaxCategory")
        _sub(item_tax, "cbc", "ID", line.vat_category)
        _sub(item_tax, "cbc", "Percent", f"{line.vat_rate:.2f}")
        scheme = _sub(item_tax, "cac", "TaxScheme")
        _sub(scheme, "cbc", "ID", "VAT")
        price = _sub(inv_line, "cac", "Price")
        _sub(price, "cbc", "PriceAmount", f"{line.unit_price:.2f}").set(
            "currencyID", invoice.currency
        )

    return root


def to_ubl_xml(invoice: Invoice) -> bytes:
    """Sérialise la facture en XML UBL indenté (UTF-8)."""
    root = to_ubl(invoice)
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", pretty_print=True)
