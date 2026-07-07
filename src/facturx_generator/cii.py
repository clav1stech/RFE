"""Sérialisation d'une :class:`Invoice` en CII (UN/CEFACT Cross Industry Invoice).

Le CII est la syntaxe XML portée par la partie « données » d'une facture
Factur-X / ZUGFeRD. On produit ici un XML conforme au profil EN16931.
"""

from __future__ import annotations

from lxml import etree

from facturx_generator.models import Invoice, Party

# Espaces de noms CII (D16B).
NSMAP = {
    "rsm": "urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100",
    "ram": "urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100",
    "udt": "urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100",
}

# Identifiant du profil EN16931 (« comfort »).
GUIDELINE_ID = "urn:cen.eu:en16931:2017"


def _q(prefix: str, tag: str) -> str:
    return f"{{{NSMAP[prefix]}}}{tag}"


def _sub(parent: etree._Element, prefix: str, tag: str, text: str | None = None) -> etree._Element:
    el = etree.SubElement(parent, _q(prefix, tag))
    if text is not None:
        el.text = text
    return el


def _party(parent: etree._Element, party: Party) -> None:
    _sub(parent, "ram", "Name", party.name)
    if party.legal_id:
        legal = _sub(parent, "ram", "SpecifiedLegalOrganization")
        _sub(legal, "ram", "ID", party.legal_id)
    address = _sub(parent, "ram", "PostalTradeAddress")
    if party.post_code:
        _sub(address, "ram", "PostcodeCode", party.post_code)
    if party.line_one:
        _sub(address, "ram", "LineOne", party.line_one)
    if party.city:
        _sub(address, "ram", "CityName", party.city)
    _sub(address, "ram", "CountryID", party.country_code)
    if party.vat_id:
        reg = _sub(parent, "ram", "SpecifiedTaxRegistration")
        vat = _sub(reg, "ram", "ID", party.vat_id)
        vat.set("schemeID", "VA")


def to_cii(invoice: Invoice) -> etree._Element:
    """Construit l'arbre XML CII de la facture."""
    root = etree.Element(_q("rsm", "CrossIndustryInvoice"), nsmap=NSMAP)

    # --- Contexte / profil (BG-2) ---
    context = _sub(root, "rsm", "ExchangedDocumentContext")
    guideline = _sub(context, "ram", "GuidelineSpecifiedDocumentContextParameter")
    _sub(guideline, "ram", "ID", GUIDELINE_ID)

    # --- En-tête document (BT-1, BT-2, BT-3) ---
    doc = _sub(root, "rsm", "ExchangedDocument")
    _sub(doc, "ram", "ID", invoice.invoice_number)
    _sub(doc, "ram", "TypeCode", invoice.invoice_type_code)
    issue = _sub(doc, "ram", "IssueDateTime")
    issue_str = _sub(issue, "udt", "DateTimeString", invoice.issue_date.strftime("%Y%m%d"))
    issue_str.set("format", "102")
    if invoice.note:
        note = _sub(doc, "ram", "IncludedNote")
        _sub(note, "ram", "Content", invoice.note)

    # --- Transaction ---
    tx = _sub(root, "rsm", "SupplyChainTradeTransaction")

    # Lignes (BG-25)
    for line in invoice.lines:
        item = _sub(tx, "ram", "IncludedSupplyChainTradeLineItem")
        doc_line = _sub(item, "ram", "AssociatedDocumentLineDocument")
        _sub(doc_line, "ram", "LineID", line.line_id)
        product = _sub(item, "ram", "SpecifiedTradeProduct")
        _sub(product, "ram", "Name", line.name)
        if line.description:
            _sub(product, "ram", "Description", line.description)
        agreement = _sub(item, "ram", "SpecifiedLineTradeAgreement")
        price = _sub(agreement, "ram", "NetPriceProductTradePrice")
        _sub(price, "ram", "ChargeAmount", f"{line.unit_price:.2f}")
        delivery = _sub(item, "ram", "SpecifiedLineTradeDelivery")
        qty = _sub(delivery, "ram", "BilledQuantity", f"{line.quantity:.2f}")
        qty.set("unitCode", line.unit_code)
        settlement = _sub(item, "ram", "SpecifiedLineTradeSettlement")
        line_tax = _sub(settlement, "ram", "ApplicableTradeTax")
        _sub(line_tax, "ram", "TypeCode", "VAT")
        _sub(line_tax, "ram", "CategoryCode", line.vat_category)
        _sub(line_tax, "ram", "RateApplicablePercent", f"{line.vat_rate:.2f}")
        summation = _sub(settlement, "ram", "SpecifiedTradeSettlementLineMonetarySummation")
        _sub(summation, "ram", "LineTotalAmount", f"{line.line_net_amount:.2f}")

    # Parties (BG-4 vendeur, BG-7 acheteur)
    agreement = _sub(tx, "ram", "ApplicableHeaderTradeAgreement")
    if invoice.buyer_reference:
        _sub(agreement, "ram", "BuyerReference", invoice.buyer_reference)
    _party(_sub(agreement, "ram", "SellerTradeParty"), invoice.seller)
    _party(_sub(agreement, "ram", "BuyerTradeParty"), invoice.buyer)

    _sub(tx, "ram", "ApplicableHeaderTradeDelivery")

    # Règlement (BG-22)
    settlement = _sub(tx, "ram", "ApplicableHeaderTradeSettlement")
    _sub(settlement, "ram", "InvoiceCurrencyCode", invoice.currency)

    for tb in invoice.tax_breakdowns:
        tax = _sub(settlement, "ram", "ApplicableTradeTax")
        _sub(tax, "ram", "CalculatedAmount", f"{tb.tax_amount:.2f}")
        _sub(tax, "ram", "TypeCode", "VAT")
        _sub(tax, "ram", "BasisAmount", f"{tb.taxable_amount:.2f}")
        _sub(tax, "ram", "CategoryCode", tb.category)
        _sub(tax, "ram", "RateApplicablePercent", f"{tb.rate:.2f}")

    if invoice.due_date is not None:
        terms = _sub(settlement, "ram", "SpecifiedTradePaymentTerms")
        due = _sub(terms, "ram", "DueDateDateTime")
        due_str = _sub(due, "udt", "DateTimeString", invoice.due_date.strftime("%Y%m%d"))
        due_str.set("format", "102")

    totals = _sub(settlement, "ram", "SpecifiedTradeSettlementHeaderMonetarySummation")
    _sub(totals, "ram", "LineTotalAmount", f"{invoice.line_total:.2f}")
    _sub(totals, "ram", "TaxBasisTotalAmount", f"{invoice.tax_basis_total:.2f}")
    tax_total = _sub(totals, "ram", "TaxTotalAmount", f"{invoice.tax_total:.2f}")
    tax_total.set("currencyID", invoice.currency)
    _sub(totals, "ram", "GrandTotalAmount", f"{invoice.grand_total:.2f}")
    _sub(totals, "ram", "DuePayableAmount", f"{invoice.due_payable:.2f}")

    return root


def to_cii_xml(invoice: Invoice) -> bytes:
    """Sérialise la facture en XML CII indenté (UTF-8)."""
    root = to_cii(invoice)
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", pretty_print=True)
