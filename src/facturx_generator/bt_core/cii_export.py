"""Génération du XML CII à partir du modèle pivot Pydantic (bt_core.model.Invoice).

Réécrit avec lxml (échappement XML automatique, pas de concaténation de
chaînes manuelle comme dans le classeur VBA d'origine) et corrige deux bugs
qui y avaient été identifiés :

1. Variable de description d'article non déclarée (``artDescription``) —
   ici un seul nom cohérent, :attr:`InvoiceLine.item_description` (BT-154),
   utilisé partout où la description de l'article est manipulée.
2. Ambiguïté sur BT-131 utilisé à la fois pour la quantité et le montant net
   de ligne — corrigée en respectant la norme AFNOR/EN16931 : BT-129 pour la
   quantité (``ram:BilledQuantity``) et BT-131 pour le seul montant net de
   ligne (``ram:LineTotalAmount``), jamais confondus.

La facture est validée (:func:`facturx_generator.bt_core.validation.validate_invoice`)
avant sérialisation : ce module ne produit jamais de XML pour une facture
métier incohérente.
"""

from __future__ import annotations

from lxml import etree

from facturx_generator.bt_core.model import BuyerParty, Invoice, InvoiceLine, SellerParty
from facturx_generator.bt_core.validation import validate_invoice

# Espaces de noms CII (D16B), alignés sur facturx_generator.cii (existant).
NSMAP = {
    "rsm": "urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100",
    "ram": "urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100",
    "udt": "urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100",
}

GUIDELINE_ID = "urn:cen.eu:en16931:2017"


def _q(prefix: str, tag: str) -> str:
    return f"{{{NSMAP[prefix]}}}{tag}"


def _sub(parent: etree._Element, prefix: str, tag: str, text: str | None = None) -> etree._Element:
    el = etree.SubElement(parent, _q(prefix, tag))
    if text is not None:
        el.text = text
    return el


def _date(parent: etree._Element, prefix: str, tag: str, value) -> etree._Element:
    wrapper = _sub(parent, prefix, tag)
    date_str = _sub(wrapper, "udt", "DateTimeString", value.strftime("%Y%m%d"))
    date_str.set("format", "102")
    return wrapper


def _seller(parent: etree._Element, seller: SellerParty) -> None:
    _sub(parent, "ram", "Name", seller.name)
    if seller.trading_name:
        legal = _sub(parent, "ram", "SpecifiedLegalOrganization")
        _sub(legal, "ram", "TradingBusinessName", seller.trading_name)
        if seller.legal_registration_id:
            _sub(legal, "ram", "ID", seller.legal_registration_id)
    elif seller.legal_registration_id:
        legal = _sub(parent, "ram", "SpecifiedLegalOrganization")
        _sub(legal, "ram", "ID", seller.legal_registration_id)
    for identifier in seller.identifiers:
        _sub(parent, "ram", "GlobalID", identifier)
    if seller.additional_legal_info:
        _sub(parent, "ram", "Description", seller.additional_legal_info)

    address = _sub(parent, "ram", "PostalTradeAddress")
    if seller.post_code:
        _sub(address, "ram", "PostcodeCode", seller.post_code)
    if seller.address_line1:
        _sub(address, "ram", "LineOne", seller.address_line1)
    if seller.address_line2:
        _sub(address, "ram", "LineTwo", seller.address_line2)
    if seller.city:
        _sub(address, "ram", "CityName", seller.city)
    _sub(address, "ram", "CountryID", seller.country_code)
    if seller.country_subdivision:
        _sub(address, "ram", "CountrySubDivisionName", seller.country_subdivision)

    if seller.electronic_address:
        electronic = _sub(parent, "ram", "URIUniversalCommunication")
        _sub(electronic, "ram", "URIID", seller.electronic_address)

    if seller.vat_id:
        reg = _sub(parent, "ram", "SpecifiedTaxRegistration")
        _sub(reg, "ram", "ID", seller.vat_id).set("schemeID", "VA")
    if seller.tax_registration_id:
        reg = _sub(parent, "ram", "SpecifiedTaxRegistration")
        _sub(reg, "ram", "ID", seller.tax_registration_id).set("schemeID", "FC")


def _buyer(parent: etree._Element, buyer: BuyerParty) -> None:
    _sub(parent, "ram", "Name", buyer.name)
    if buyer.trading_name:
        legal = _sub(parent, "ram", "SpecifiedLegalOrganization")
        _sub(legal, "ram", "TradingBusinessName", buyer.trading_name)
        if buyer.legal_registration_id:
            _sub(legal, "ram", "ID", buyer.legal_registration_id)
    elif buyer.legal_registration_id:
        legal = _sub(parent, "ram", "SpecifiedLegalOrganization")
        _sub(legal, "ram", "ID", buyer.legal_registration_id)
    for identifier in buyer.identifiers:
        _sub(parent, "ram", "GlobalID", identifier)

    address = _sub(parent, "ram", "PostalTradeAddress")
    if buyer.post_code:
        _sub(address, "ram", "PostcodeCode", buyer.post_code)
    if buyer.address_line1:
        _sub(address, "ram", "LineOne", buyer.address_line1)
    if buyer.address_line2:
        _sub(address, "ram", "LineTwo", buyer.address_line2)
    if buyer.city:
        _sub(address, "ram", "CityName", buyer.city)
    _sub(address, "ram", "CountryID", buyer.country_code)
    if buyer.country_subdivision:
        _sub(address, "ram", "CountrySubDivisionName", buyer.country_subdivision)

    if buyer.vat_id:
        reg = _sub(parent, "ram", "SpecifiedTaxRegistration")
        _sub(reg, "ram", "ID", buyer.vat_id).set("schemeID", "VA")

    if buyer.contact_point or buyer.contact_phone or buyer.contact_email:
        contact = _sub(parent, "ram", "DefinedTradeContact")
        if buyer.contact_point:
            _sub(contact, "ram", "PersonName", buyer.contact_point)
        if buyer.contact_phone:
            phone = _sub(contact, "ram", "TelephoneUniversalCommunication")
            _sub(phone, "ram", "CompleteNumber", buyer.contact_phone)
        if buyer.contact_email:
            email = _sub(contact, "ram", "EmailURIUniversalCommunication")
            _sub(email, "ram", "URIID", buyer.contact_email)


def _line_item(parent: etree._Element, line: InvoiceLine) -> None:
    item = _sub(parent, "ram", "IncludedSupplyChainTradeLineItem")

    doc_line = _sub(item, "ram", "AssociatedDocumentLineDocument")
    _sub(doc_line, "ram", "LineID", line.line_id)  # BT-126
    if line.note:
        note = _sub(doc_line, "ram", "IncludedNote")  # BT-127
        _sub(note, "ram", "Content", line.note)

    product = _sub(item, "ram", "SpecifiedTradeProduct")
    _sub(product, "ram", "Name", line.item_name)  # BT-153
    if line.item_description:  # BT-154 — nom de variable unique et cohérent
        _sub(product, "ram", "Description", line.item_description)

    agreement = _sub(item, "ram", "SpecifiedLineTradeAgreement")
    if line.gross_price is not None:  # BT-148
        gross = _sub(agreement, "ram", "GrossPriceProductTradePrice")
        _sub(gross, "ram", "ChargeAmount", f"{line.gross_price:.2f}")
        if line.price_discount is not None:  # BT-147
            charge = _sub(gross, "ram", "AppliedTradeAllowanceCharge")
            _sub(charge, "ram", "ActualAmount", f"{line.price_discount:.2f}")
    net_price_el = _sub(agreement, "ram", "NetPriceProductTradePrice")
    _sub(net_price_el, "ram", "ChargeAmount", f"{line.net_price:.2f}")  # BT-146
    if line.price_base_quantity is not None:  # BT-149/BT-150
        base_qty = _sub(net_price_el, "ram", "BasisQuantity", f"{line.price_base_quantity:.2f}")
        if line.price_base_quantity_unit_code:
            base_qty.set("unitCode", line.price_base_quantity_unit_code)

    delivery = _sub(item, "ram", "SpecifiedLineTradeDelivery")
    quantity = _sub(delivery, "ram", "BilledQuantity", f"{line.quantity:.2f}")  # BT-129
    quantity.set("unitCode", line.unit_code)  # BT-130

    settlement = _sub(item, "ram", "SpecifiedLineTradeSettlement")
    line_tax = _sub(settlement, "ram", "ApplicableTradeTax")
    _sub(line_tax, "ram", "TypeCode", "VAT")
    _sub(line_tax, "ram", "CategoryCode", line.vat_category_code)  # BT-151
    if line.vat_rate is not None:  # BT-152
        _sub(line_tax, "ram", "RateApplicablePercent", f"{line.vat_rate:.2f}")
    summation = _sub(settlement, "ram", "SpecifiedTradeSettlementLineMonetarySummation")
    _sub(
        summation, "ram", "LineTotalAmount", f"{line.net_amount:.2f}"
    )  # BT-131 — distinct de BT-129


def to_cii(invoice: Invoice) -> etree._Element:
    """Construit l'arbre XML CII de la facture à partir du modèle pivot BT/BG."""
    validate_invoice(invoice)

    root = etree.Element(_q("rsm", "CrossIndustryInvoice"), nsmap=NSMAP)

    context = _sub(root, "rsm", "ExchangedDocumentContext")
    guideline = _sub(context, "ram", "GuidelineSpecifiedDocumentContextParameter")
    _sub(guideline, "ram", "ID", GUIDELINE_ID)

    doc = _sub(root, "rsm", "ExchangedDocument")
    _sub(doc, "ram", "ID", invoice.invoice_number)  # BT-1
    _sub(doc, "ram", "TypeCode", invoice.invoice_type_code)  # BT-3
    _date(doc, "ram", "IssueDateTime", invoice.issue_date)  # BT-2
    if invoice.note:
        note = _sub(doc, "ram", "IncludedNote")  # BT-22
        _sub(note, "ram", "Content", invoice.note)

    tx = _sub(root, "rsm", "SupplyChainTradeTransaction")

    for line in invoice.lines:  # BG-25
        _line_item(tx, line)

    agreement = _sub(tx, "ram", "ApplicableHeaderTradeAgreement")
    if invoice.buyer_reference:
        _sub(agreement, "ram", "BuyerReference", invoice.buyer_reference)  # BT-10
    _seller(_sub(agreement, "ram", "SellerTradeParty"), invoice.seller)  # BG-4/BG-5
    _buyer(_sub(agreement, "ram", "BuyerTradeParty"), invoice.buyer)  # BG-7/BG-8/BG-9

    _sub(tx, "ram", "ApplicableHeaderTradeDelivery")

    settlement = _sub(tx, "ram", "ApplicableHeaderTradeSettlement")
    _sub(settlement, "ram", "InvoiceCurrencyCode", invoice.currency_code)  # BT-5

    if invoice.preceding_invoice_reference:  # BT-25/BT-26
        preceding = _sub(settlement, "ram", "InvoiceReferencedDocument")
        _sub(preceding, "ram", "IssuerAssignedID", invoice.preceding_invoice_reference)
        if invoice.preceding_invoice_issue_date is not None:
            _date(preceding, "ram", "FormattedIssueDateTime", invoice.preceding_invoice_issue_date)

    if invoice.payment_instructions is not None:  # BG-16
        pay = invoice.payment_instructions
        if pay.remittance_info:
            _sub(settlement, "ram", "PaymentReference", pay.remittance_info)  # BT-83
        means = _sub(settlement, "ram", "SpecifiedTradeSettlementPaymentMeans")
        _sub(means, "ram", "TypeCode", pay.means_code)  # BT-81
        if pay.means_text:
            _sub(means, "ram", "Information", pay.means_text)  # BT-82
        if pay.payment_account_id:
            account = _sub(means, "ram", "PayeePartyCreditorFinancialAccount")
            _sub(account, "ram", "IBANID", pay.payment_account_id)  # BT-84
            if pay.payment_account_name:
                _sub(account, "ram", "AccountName", pay.payment_account_name)  # BT-85
        if pay.payment_service_provider_id:
            institution = _sub(means, "ram", "PayeeSpecifiedCreditorFinancialInstitution")
            _sub(institution, "ram", "BICID", pay.payment_service_provider_id)  # BT-86

    for breakdown in invoice.vat_breakdown:  # BG-23
        tax = _sub(settlement, "ram", "ApplicableTradeTax")
        _sub(tax, "ram", "CalculatedAmount", f"{breakdown.tax_amount:.2f}")  # BT-117
        _sub(tax, "ram", "TypeCode", "VAT")
        if breakdown.exemption_reason_text:
            _sub(tax, "ram", "ExemptionReason", breakdown.exemption_reason_text)  # BT-120
        _sub(tax, "ram", "BasisAmount", f"{breakdown.taxable_amount:.2f}")  # BT-116
        if breakdown.exemption_reason_code:
            _sub(tax, "ram", "ExemptionReasonCode", breakdown.exemption_reason_code)  # BT-121
        _sub(tax, "ram", "CategoryCode", breakdown.category_code)  # BT-118
        if breakdown.rate is not None:
            _sub(tax, "ram", "RateApplicablePercent", f"{breakdown.rate:.2f}")  # BT-119

    if invoice.due_date is not None:
        terms = _sub(settlement, "ram", "SpecifiedTradePaymentTerms")
        _date(terms, "ram", "DueDateDateTime", invoice.due_date)  # BT-9

    totals = _sub(settlement, "ram", "SpecifiedTradeSettlementHeaderMonetarySummation")
    _sub(totals, "ram", "TaxBasisTotalAmount", f"{invoice.totals.tax_basis_total:.2f}")  # BT-109
    tax_total = _sub(totals, "ram", "TaxTotalAmount", f"{invoice.totals.tax_total:.2f}")  # BT-110
    tax_total.set("currencyID", invoice.currency_code)
    _sub(totals, "ram", "GrandTotalAmount", f"{invoice.totals.grand_total:.2f}")  # BT-112
    if invoice.totals.paid_amount is not None:
        _sub(totals, "ram", "TotalPrepaidAmount", f"{invoice.totals.paid_amount:.2f}")  # BT-113
    if invoice.totals.rounding_amount is not None:
        _sub(totals, "ram", "RoundingAmount", f"{invoice.totals.rounding_amount:.2f}")  # BT-114
    _sub(totals, "ram", "DuePayableAmount", f"{invoice.totals.due_payable_amount:.2f}")  # BT-115

    return root


def to_cii_xml(invoice: Invoice) -> bytes:
    """Sérialise la facture (modèle pivot BT/BG) en XML CII indenté (UTF-8)."""
    root = to_cii(invoice)
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", pretty_print=True)
