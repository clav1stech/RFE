"""Tests de la génération XML CII depuis le modèle pivot (bt_core.cii_export)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from lxml import etree

from facturx_generator.bt_core.cii_export import NSMAP, to_cii, to_cii_xml
from facturx_generator.bt_core.model import (
    BuyerParty,
    DocumentTotals,
    Invoice,
    InvoiceLine,
    PaymentInstructions,
    SellerParty,
    VatBreakdown,
)
from facturx_generator.bt_core.validation import PrecedingInvoiceReferenceRequiredError


def _seller_fr() -> SellerParty:
    return SellerParty(
        name="Fournitures Alpes SAS",
        country_code="FR",
        address_line1="12 rue de la République",
        city="Grenoble",
        post_code="38000",
        vat_id="FR40123456789",
        legal_registration_id="12345678900012",
    )


def _buyer_fr() -> BuyerParty:
    return BuyerParty(
        name="Grenoble-Alpes Métropole",
        country_code="FR",
        address_line1="3 rue Malakoff",
        city="Grenoble",
        post_code="38000",
        vat_id="FR97200040715",
        legal_registration_id="20004071500019",
    )


def _france_vat_invoice(**overrides: object) -> Invoice:
    fields: dict[str, object] = {
        "invoice_number": "FA-2026-0001",
        "issue_date": date(2026, 1, 15),
        "invoice_type_code": "380",
        "currency_code": "EUR",
        "seller": _seller_fr(),
        "buyer": _buyer_fr(),
        "payment_instructions": PaymentInstructions(
            means_code="58",
            payment_account_id="FR7630006000011234567890189",
        ),
        "vat_breakdown": [
            VatBreakdown(
                taxable_amount=Decimal("800.00"),
                tax_amount=Decimal("160.00"),
                category_code="S",
                rate=Decimal("20"),
            )
        ],
        "lines": [
            InvoiceLine(
                line_id="1",
                quantity=Decimal("10"),
                unit_code="HUR",
                net_amount=Decimal("800.00"),
                net_price=Decimal("80.00"),
                vat_category_code="S",
                vat_rate=Decimal("20"),
                item_name="Prestation de conseil",
                item_description="Accompagnement dématérialisation.",
            )
        ],
        "totals": DocumentTotals(
            tax_basis_total=Decimal("800.00"),
            tax_total=Decimal("160.00"),
            grand_total=Decimal("960.00"),
            due_payable_amount=Decimal("960.00"),
        ),
    }
    fields.update(overrides)
    return Invoice(**fields)


def _findtext(root: etree._Element, path: str) -> str | None:
    el = root.find(path, namespaces=NSMAP)
    return el.text if el is not None else None


def test_france_vat_invoice_header_fields() -> None:
    root = to_cii(_france_vat_invoice())
    assert _findtext(root, ".//rsm:ExchangedDocument/ram:ID") == "FA-2026-0001"
    assert _findtext(root, ".//rsm:ExchangedDocument/ram:TypeCode") == "380"


def test_quantity_and_line_net_amount_are_distinct_elements() -> None:
    """Non-régression du bug VBA : BT-129 (quantité) != BT-131 (montant net)."""
    root = to_cii(_france_vat_invoice())
    quantity = root.find(".//ram:SpecifiedLineTradeDelivery/ram:BilledQuantity", namespaces=NSMAP)
    net_amount = root.find(
        ".//ram:SpecifiedTradeSettlementLineMonetarySummation/ram:LineTotalAmount",
        namespaces=NSMAP,
    )
    assert quantity.text == "10.00"
    assert net_amount.text == "800.00"
    assert quantity.text != net_amount.text


def test_item_description_is_serialized_from_single_consistent_field() -> None:
    """Non-régression du bug VBA : plus de variable artDescription non déclarée."""
    root = to_cii(_france_vat_invoice())
    description = _findtext(root, ".//ram:SpecifiedTradeProduct/ram:Description")
    assert description == "Accompagnement dématérialisation."


def test_totals_are_serialized_from_pivot_totals() -> None:
    root = to_cii(_france_vat_invoice())
    assert _findtext(root, ".//ram:TaxBasisTotalAmount") == "800.00"
    assert _findtext(root, ".//ram:TaxTotalAmount") == "160.00"
    assert _findtext(root, ".//ram:GrandTotalAmount") == "960.00"
    assert _findtext(root, ".//ram:DuePayableAmount") == "960.00"


def test_xml_special_characters_are_escaped() -> None:
    invoice = _france_vat_invoice(note="Facture <test> & 'validation' \"qualité\"")
    xml_bytes = to_cii_xml(invoice)
    # Le texte brut ne doit jamais apparaître non échappé dans la sortie sérialisée.
    assert b"<test>" not in xml_bytes
    root = etree.fromstring(xml_bytes)
    note = _findtext(root, ".//rsm:ExchangedDocument/ram:IncludedNote/ram:Content")
    assert note == "Facture <test> & 'validation' \"qualité\""


def test_to_cii_xml_produces_well_formed_xml() -> None:
    xml_bytes = to_cii_xml(_france_vat_invoice())
    etree.fromstring(xml_bytes)  # ne doit pas lever


def test_to_cii_rejects_invalid_invoice() -> None:
    """La génération XML délègue la validation métier — pas de XML pour une facture incohérente."""
    invoice = _france_vat_invoice(invoice_type_code="381")  # avoir sans BT-25/BT-26
    with pytest.raises(PrecedingInvoiceReferenceRequiredError):
        to_cii(invoice)
