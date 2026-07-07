"""Modèle de données d'une facture, indépendant du format de sortie (CII / UBL).

Les champs sont annotés avec leur Business Term EN16931 (BT-xx) afin que le
mapping vers les formats XML reste traçable et documenté.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import ROUND_HALF_UP, Decimal


def _money(value: Decimal | int | float | str) -> Decimal:
    """Normalise un montant sur 2 décimales (arrondi commercial)."""
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


@dataclass
class Party:
    """Un tiers de la facture (vendeur BG-4 ou acheteur BG-7)."""

    name: str  # BT-27 (vendeur) / BT-44 (acheteur)
    country_code: str  # BT-40 / BT-55 (code pays ISO 3166-1 alpha-2)
    line_one: str = ""  # BT-35 / BT-50
    city: str = ""  # BT-37 / BT-52
    post_code: str = ""  # BT-38 / BT-53
    vat_id: str = ""  # BT-31 (vendeur) / BT-48 (acheteur) — n° TVA intracom.
    legal_id: str = ""  # BT-30 / BT-47 — identifiant légal (SIREN/SIRET)


@dataclass
class InvoiceLine:
    """Une ligne de facture (BG-25)."""

    line_id: str  # BT-126
    name: str  # BT-153 — nom de l'article
    quantity: Decimal  # BT-129
    unit_code: str  # BT-130 — code unité (UN/ECE Rec 20), ex. "C62"
    unit_price: Decimal  # BT-146 — prix unitaire net
    vat_rate: Decimal  # BT-152 — taux de TVA de la ligne (%)
    vat_category: str = "S"  # BT-151 — code catégorie TVA (S, Z, E, AE, ...)
    description: str = ""  # BT-154

    def __post_init__(self) -> None:
        self.quantity = Decimal(str(self.quantity))
        self.unit_price = Decimal(str(self.unit_price))
        self.vat_rate = Decimal(str(self.vat_rate))

    @property
    def line_net_amount(self) -> Decimal:
        """BT-131 — montant net de la ligne (quantité × prix unitaire)."""
        return _money(self.quantity * self.unit_price)


@dataclass
class TaxBreakdown:
    """Une ventilation de TVA (BG-23), agrégée par catégorie et taux."""

    category: str  # BT-118
    rate: Decimal  # BT-119
    taxable_amount: Decimal  # BT-116 — base imposable
    tax_amount: Decimal  # BT-117 — montant de TVA


@dataclass
class Invoice:
    """Facture complète, agrégat racine du modèle métier."""

    invoice_number: str  # BT-1
    issue_date: date  # BT-2
    invoice_type_code: str  # BT-3 — ex. "380" (facture commerciale)
    currency: str  # BT-5 — code devise ISO 4217
    seller: Party  # BG-4
    buyer: Party  # BG-7
    lines: list[InvoiceLine] = field(default_factory=list)
    due_date: date | None = None  # BT-9
    buyer_reference: str = ""  # BT-10 — référence acheteur
    note: str = ""  # BT-22

    # --- Totaux calculés (BG-22) ---
    @property
    def line_total(self) -> Decimal:
        """BT-106 — somme des montants nets de lignes."""
        return _money(sum((line.line_net_amount for line in self.lines), Decimal("0")))

    @property
    def tax_breakdowns(self) -> list[TaxBreakdown]:
        """Ventilation de la TVA par (catégorie, taux)."""
        buckets: dict[tuple[str, Decimal], Decimal] = {}
        for line in self.lines:
            key = (line.vat_category, line.vat_rate)
            buckets[key] = buckets.get(key, Decimal("0")) + line.line_net_amount

        breakdowns: list[TaxBreakdown] = []
        for (category, rate), base in sorted(buckets.items(), key=lambda kv: kv[0][1]):
            taxable = _money(base)
            tax = _money(taxable * rate / Decimal("100"))
            breakdowns.append(
                TaxBreakdown(
                    category=category,
                    rate=rate,
                    taxable_amount=taxable,
                    tax_amount=tax,
                )
            )
        return breakdowns

    @property
    def tax_total(self) -> Decimal:
        """BT-110 — montant total de TVA."""
        return _money(sum((b.tax_amount for b in self.tax_breakdowns), Decimal("0")))

    @property
    def tax_basis_total(self) -> Decimal:
        """BT-109 — total hors taxes."""
        return self.line_total

    @property
    def grand_total(self) -> Decimal:
        """BT-112 — total toutes taxes comprises."""
        return _money(self.tax_basis_total + self.tax_total)

    @property
    def due_payable(self) -> Decimal:
        """BT-115 — net à payer."""
        return self.grand_total
