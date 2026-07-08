"""Modèle pivot BT/BG EN16931 (Pydantic), indépendant de la syntaxe de sortie.

Socle de travail exploratoire, en parallèle de :mod:`facturx_generator.models`
(modèle métier actuellement branché sur l'UI/CLI) — cf. docs/CODEMAP.md.
"""

from facturx_generator.bt_core.enums import (
    InvoiceTypeCode,
    PaymentMeansCode,
    UnitOfMeasureCode,
    VatCategoryCode,
)
from facturx_generator.bt_core.model import (
    BuyerParty,
    DocumentTotals,
    Invoice,
    InvoiceLine,
    PaymentInstructions,
    SellerParty,
    VatBreakdown,
)

__all__ = [
    "BuyerParty",
    "DocumentTotals",
    "Invoice",
    "InvoiceLine",
    "InvoiceTypeCode",
    "PaymentInstructions",
    "PaymentMeansCode",
    "SellerParty",
    "UnitOfMeasureCode",
    "VatBreakdown",
    "VatCategoryCode",
]
