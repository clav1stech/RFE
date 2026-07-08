"""Tests des règles de validation métier (facturx_generator.bt_core.validation)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from facturx_generator.bt_core.model import (
    BuyerParty,
    DocumentTotals,
    Invoice,
    InvoiceLine,
    SellerParty,
    VatBreakdown,
)
from facturx_generator.bt_core.validation import (
    ClientZone,
    PrecedingInvoiceReferenceNotAllowedError,
    PrecedingInvoiceReferenceRequiredError,
    VatCategoryInconsistentError,
    classify_client_zone,
    validate_invoice,
    validate_preceding_invoice_reference,
    validate_vat_category_consistency,
)

SELLER_FR = SellerParty(name="Fournitures Alpes SAS", country_code="FR")
BUYER_FR = BuyerParty(name="Grenoble-Alpes Métropole", country_code="FR")
BUYER_DE = BuyerParty(name="Kunde GmbH", country_code="DE")
BUYER_US = BuyerParty(name="Acme Corp", country_code="US")


def _line(
    category: str, rate: Decimal | None, net_amount: Decimal = Decimal("100.00")
) -> InvoiceLine:
    return InvoiceLine(
        line_id="1",
        quantity=Decimal("1"),
        unit_code="C62",
        net_amount=net_amount,
        net_price=net_amount,
        vat_category_code=category,
        vat_rate=rate,
        item_name="Article",
    )


def _breakdown(
    category: str, rate: Decimal | None, amount: Decimal = Decimal("100.00")
) -> VatBreakdown:
    tax_amount = amount * rate / Decimal("100") if rate else Decimal("0")
    return VatBreakdown(
        taxable_amount=amount,
        tax_amount=tax_amount,
        category_code=category,
        rate=rate,
    )


def _invoice(
    *,
    buyer: BuyerParty = BUYER_FR,
    invoice_type_code: str = "380",
    preceding_invoice_reference: str | None = None,
    preceding_invoice_issue_date: date | None = None,
    vat_category: str = "S",
    vat_rate: Decimal | None = Decimal("20"),
) -> Invoice:
    return Invoice(
        invoice_number="FA-2026-0001",
        issue_date=date(2026, 1, 15),
        invoice_type_code=invoice_type_code,
        currency_code="EUR",
        seller=SELLER_FR,
        buyer=buyer,
        preceding_invoice_reference=preceding_invoice_reference,
        preceding_invoice_issue_date=preceding_invoice_issue_date,
        vat_breakdown=[_breakdown(vat_category, vat_rate)],
        lines=[_line(vat_category, vat_rate)],
        totals=DocumentTotals(
            tax_basis_total=Decimal("100.00"),
            tax_total=Decimal("20.00"),
            grand_total=Decimal("120.00"),
            due_payable_amount=Decimal("120.00"),
        ),
    )


# --- classify_client_zone ---


def test_classify_client_zone_domestic() -> None:
    assert classify_client_zone(SELLER_FR, BUYER_FR) is ClientZone.DOMESTIC


def test_classify_client_zone_intra_eu() -> None:
    assert classify_client_zone(SELLER_FR, BUYER_DE) is ClientZone.INTRA_EU


def test_classify_client_zone_export_non_eu() -> None:
    assert classify_client_zone(SELLER_FR, BUYER_US) is ClientZone.EXPORT_NON_EU


# --- Règle a) avoir/facture rectificative -> BT-25/BT-26 requis ---


def test_credit_note_with_preceding_reference_is_valid() -> None:
    invoice = _invoice(
        invoice_type_code="381",
        preceding_invoice_reference="FA-2025-0099",
        preceding_invoice_issue_date=date(2025, 12, 1),
    )
    validate_preceding_invoice_reference(invoice)  # ne doit pas lever


def test_credit_note_without_preceding_reference_raises() -> None:
    invoice = _invoice(invoice_type_code="381")
    with pytest.raises(PrecedingInvoiceReferenceRequiredError) as exc_info:
        validate_preceding_invoice_reference(invoice)
    assert exc_info.value.bt == "BT-25"


def test_corrected_invoice_without_preceding_date_raises() -> None:
    invoice = _invoice(
        invoice_type_code="384",
        preceding_invoice_reference="FA-2025-0099",
    )
    with pytest.raises(PrecedingInvoiceReferenceRequiredError) as exc_info:
        validate_preceding_invoice_reference(invoice)
    assert exc_info.value.bt == "BT-26"


# --- Règle b) facture normale -> BT-25/BT-26 doivent être vides ---


def test_normal_invoice_without_preceding_reference_is_valid() -> None:
    invoice = _invoice(invoice_type_code="380")
    validate_preceding_invoice_reference(invoice)  # ne doit pas lever


def test_normal_invoice_with_preceding_reference_raises() -> None:
    invoice = _invoice(invoice_type_code="380", preceding_invoice_reference="FA-2025-0099")
    with pytest.raises(PrecedingInvoiceReferenceNotAllowedError) as exc_info:
        validate_preceding_invoice_reference(invoice)
    assert exc_info.value.bt == "BT-25"


# --- Règle c) cohérence catégorie/taux de TVA / typologie client ---


def test_domestic_standard_vat_is_valid() -> None:
    invoice = _invoice(buyer=BUYER_FR, vat_category="S", vat_rate=Decimal("20"))
    validate_vat_category_consistency(invoice)  # ne doit pas lever


def test_intra_community_reverse_charge_is_valid() -> None:
    invoice = _invoice(buyer=BUYER_DE, vat_category="K", vat_rate=Decimal("0"))
    validate_vat_category_consistency(invoice)  # ne doit pas lever


def test_intra_community_category_for_domestic_buyer_raises() -> None:
    invoice = _invoice(buyer=BUYER_FR, vat_category="K", vat_rate=Decimal("0"))
    with pytest.raises(VatCategoryInconsistentError) as exc_info:
        validate_vat_category_consistency(invoice)
    assert exc_info.value.bt == "BT-118"


def test_standard_category_with_zero_rate_raises() -> None:
    invoice = _invoice(buyer=BUYER_FR, vat_category="S", vat_rate=Decimal("0"))
    with pytest.raises(VatCategoryInconsistentError) as exc_info:
        validate_vat_category_consistency(invoice)
    assert exc_info.value.bt == "BT-119"


def test_export_category_for_eu_buyer_raises() -> None:
    invoice = _invoice(buyer=BUYER_DE, vat_category="G", vat_rate=Decimal("0"))
    with pytest.raises(VatCategoryInconsistentError):
        validate_vat_category_consistency(invoice)


# --- validate_invoice() : orchestration ---


def test_validate_invoice_valid_case_does_not_raise() -> None:
    invoice = _invoice()
    validate_invoice(invoice)


def test_validate_invoice_raises_on_first_violated_rule() -> None:
    invoice = _invoice(invoice_type_code="381")  # BT-25/BT-26 manquants
    with pytest.raises(PrecedingInvoiceReferenceRequiredError):
        validate_invoice(invoice)
