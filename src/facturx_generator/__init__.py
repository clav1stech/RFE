"""facturx_generator — génération de factures de test Factur-X / UBL (EN16931).

Ce package sépare strictement la logique métier (modèle de facture, mapping des
Business Terms EN16931, sérialisation CII et UBL) de toute couche d'interface.
"""

from facturx_generator.models import (
    Invoice,
    InvoiceLine,
    Party,
    TaxBreakdown,
)

__all__ = [
    "Invoice",
    "InvoiceLine",
    "Party",
    "TaxBreakdown",
    "__version__",
]

__version__ = "0.1.2"
