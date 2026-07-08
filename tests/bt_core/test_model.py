"""Tests du modèle pivot BT/BG (facturx_generator.bt_core.model)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from facturx_generator.bt_core import (
    BuyerParty,
    DocumentTotals,
    Invoice,
    InvoiceLine,
    InvoiceTypeCode,
    SellerParty,
    VatBreakdown,
    VatCategoryCode,
)


def _minimal_seller() -> SellerParty:
    return SellerParty(name="Fournitures Alpes SAS", country_code="FR")


def _minimal_buyer() -> BuyerParty:
    return BuyerParty(name="Grenoble-Alpes Métropole", country_code="FR")


def _minimal_line() -> InvoiceLine:
    return InvoiceLine(
        line_id="1",
        quantity=Decimal("10"),
        unit_code="HUR",
        net_amount=Decimal("800.00"),
        net_price=Decimal("80.00"),
        vat_category_code=VatCategoryCode.STANDARD,
        vat_rate=Decimal("20"),
        item_name="Prestation de conseil",
    )


def _minimal_vat_breakdown() -> VatBreakdown:
    return VatBreakdown(
        taxable_amount=Decimal("800.00"),
        tax_amount=Decimal("160.00"),
        category_code=VatCategoryCode.STANDARD,
        rate=Decimal("20"),
    )


def _minimal_totals() -> DocumentTotals:
    return DocumentTotals(
        tax_basis_total=Decimal("800.00"),
        tax_total=Decimal("160.00"),
        grand_total=Decimal("960.00"),
        due_payable_amount=Decimal("960.00"),
    )


def build_minimal_invoice(**overrides: object) -> Invoice:
    fields: dict[str, object] = {
        "invoice_number": "FA-2026-0001",
        "issue_date": date(2026, 1, 15),
        "invoice_type_code": InvoiceTypeCode.COMMERCIAL_INVOICE,
        "currency_code": "EUR",
        "seller": _minimal_seller(),
        "buyer": _minimal_buyer(),
        "vat_breakdown": [_minimal_vat_breakdown()],
        "lines": [_minimal_line()],
        "totals": _minimal_totals(),
    }
    fields.update(overrides)
    return Invoice(**fields)


def test_minimal_invoice_is_valid() -> None:
    invoice = build_minimal_invoice()
    assert invoice.invoice_number == "FA-2026-0001"
    assert invoice.seller.country_code == "FR"
    assert invoice.lines[0].net_amount == Decimal("800.00")


def test_invoice_requires_at_least_one_line() -> None:
    with pytest.raises(ValidationError):
        build_minimal_invoice(lines=[])


def test_invoice_requires_at_least_one_vat_breakdown() -> None:
    with pytest.raises(ValidationError):
        build_minimal_invoice(vat_breakdown=[])


def test_country_code_must_be_two_letters() -> None:
    with pytest.raises(ValidationError):
        SellerParty(name="Vendeur", country_code="FRA")


def test_extra_fields_are_rejected() -> None:
    with pytest.raises(ValidationError):
        SellerParty(name="Vendeur", country_code="FR", unknown_field="x")
