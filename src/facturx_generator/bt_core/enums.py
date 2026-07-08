"""Listes de codes fermées EN16931 utilisées par le modèle pivot BT/BG.

Chaque Enum correspond à une liste de codes référencée par la norme (UNTDID,
UN/ECE Rec 20...). On ne couvre que les valeurs utiles à l'outil pédagogique,
pas l'intégralité des listes officielles (souvent longues de plusieurs
dizaines d'entrées) — étendre au besoin, sans viser l'exhaustivité.
"""

from __future__ import annotations

from enum import StrEnum


class InvoiceTypeCode(StrEnum):
    """BT-3 — code type de document (UNTDID 1001, sous-ensemble Factur-X/CII)."""

    COMMERCIAL_INVOICE = "380"  # Facture commerciale
    CREDIT_NOTE = "381"  # Avoir
    CORRECTED_INVOICE = "384"  # Facture rectificative
    PREPAYMENT_INVOICE = "386"  # Facture d'acompte
    SELF_BILLED_INVOICE = "389"  # Facture d'autofacturation


class VatCategoryCode(StrEnum):
    """BT-118/BT-151 — code catégorie de TVA (UNTDID 5305)."""

    STANDARD = "S"  # Taux normal
    ZERO_RATED = "Z"  # Taux zéro
    EXEMPT = "E"  # Exonéré de TVA
    REVERSE_CHARGE = "AE"  # Autoliquidation (domestique)
    INTRA_COMMUNITY = "K"  # Livraison intracommunautaire (autoliquidation UE)
    EXPORT = "G"  # Exonéré — export hors UE
    OUT_OF_SCOPE = "O"  # Hors champ de TVA
    CANARY_ISLANDS = "L"  # IGIC (Canaries)
    CEUTA_MELILLA = "M"  # IPSI (Ceuta/Melilla)


class UnitOfMeasureCode(StrEnum):
    """BT-130/BT-150 — code unité de mesure (UN/ECE Recommendation 20), sous-ensemble courant."""

    UNIT = "C62"  # Unité (pièce)
    HOUR = "HUR"
    DAY = "DAY"
    KILOGRAM = "KGM"
    LITRE = "LTR"
    METRE = "MTR"
    SQUARE_METRE = "MTK"
    CUBIC_METRE = "MTQ"
    TONNE = "TNE"


class PaymentMeansCode(StrEnum):
    """BT-81 — code moyen de paiement (UNTDID 4461), sous-ensemble courant."""

    INSTRUMENT_NOT_DEFINED = "1"
    CREDIT_TRANSFER = "30"
    PAYMENT_TO_BANK_ACCOUNT = "42"
    BANK_CARD = "48"
    DIRECT_DEBIT = "49"
    SEPA_CREDIT_TRANSFER = "58"
    SEPA_DIRECT_DEBIT = "59"


# BT-40/BT-55 — pays membres de l'UE (ISO 3166-1 alpha-2), utilisé pour
# qualifier la typologie client France/UE/Hors UE dans les règles de validation.
EU_COUNTRY_CODES: frozenset[str] = frozenset(
    {
        "AT", "BE", "BG", "CY", "CZ", "DE", "DK", "EE", "ES", "FI",
        "FR", "GR", "HR", "HU", "IE", "IT", "LT", "LU", "LV", "MT",
        "NL", "PL", "PT", "RO", "SE", "SI", "SK",
    }
)  # fmt: skip
