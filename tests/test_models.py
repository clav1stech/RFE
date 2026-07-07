"""Tests des calculs de totaux du modèle métier."""

from decimal import Decimal

from facturx_generator.profiles import build_multi_vat, build_standard_fr


def test_standard_totals():
    inv = build_standard_fr()
    # 10 * 80 + 1 * 150 = 950 HT
    assert inv.line_total == Decimal("950.00")
    assert inv.tax_basis_total == Decimal("950.00")
    # TVA 20 % => 190.00
    assert inv.tax_total == Decimal("190.00")
    assert inv.grand_total == Decimal("1140.00")
    assert inv.due_payable == Decimal("1140.00")


def test_multi_vat_breakdown():
    inv = build_multi_vat()
    breakdowns = inv.tax_breakdowns
    assert len(breakdowns) == 2
    # Trié par taux croissant : 5.5 % puis 20 %.
    rates = [b.rate for b in breakdowns]
    assert rates == sorted(rates)
    # 50 * 3.20 = 160 @ 5.5 % => 8.80
    low = next(b for b in breakdowns if b.rate == Decimal("5.5"))
    assert low.taxable_amount == Decimal("160.00")
    assert low.tax_amount == Decimal("8.80")
    # 2 * 120 = 240 @ 20 % => 48.00
    high = next(b for b in breakdowns if b.rate == Decimal("20"))
    assert high.taxable_amount == Decimal("240.00")
    assert high.tax_amount == Decimal("48.00")
    assert inv.tax_total == Decimal("56.80")
    assert inv.grand_total == Decimal("456.80")
