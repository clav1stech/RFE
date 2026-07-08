"""Règles de cohérence métier, génériques (non liées à Comarch).

Réécriture en Python pur de règles identifiées dans le classeur Excel/VBA
d'origine : là où le VBA se contentait d'un ``MsgBox`` pour signaler une
incohérence, ces fonctions lèvent des exceptions Python typées, porteuses du
Business Term concerné et de la règle violée.

Règles couvertes :
    a) Avoir/facture rectificative (BT-3 = 381/384) → BT-25 et BT-26 requis.
    b) Facture normale (BT-3 = 380) → BT-25 et BT-26 doivent être absents.
    c) Cohérence entre code catégorie de TVA (BT-118/BT-151), taux
       (BT-119/BT-152) et typologie du client (France/UE/Hors UE, déduite de
       BT-40 vendeur et BT-55 acheteur).
"""

from __future__ import annotations

from enum import StrEnum

from facturx_generator.bt_core.enums import EU_COUNTRY_CODES, VatCategoryCode
from facturx_generator.bt_core.model import BuyerParty, Invoice, SellerParty

#: Codes catégorie de TVA dont le taux doit être nul (exonération/autoliquidation).
_ZERO_RATE_CATEGORIES = frozenset(
    {
        VatCategoryCode.ZERO_RATED,
        VatCategoryCode.EXEMPT,
        VatCategoryCode.REVERSE_CHARGE,
        VatCategoryCode.INTRA_COMMUNITY,
        VatCategoryCode.EXPORT,
        VatCategoryCode.OUT_OF_SCOPE,
    }
)


class ClientZone(StrEnum):
    """Typologie du client, relative au pays du vendeur."""

    DOMESTIC = "domestic"  # France (même pays que le vendeur)
    INTRA_EU = "intra_eu"  # Union européenne, hors pays du vendeur
    EXPORT_NON_EU = "export_non_eu"  # Hors Union européenne


class InvoiceValidationError(ValueError):
    """Erreur de cohérence métier — base commune, porte le BT concerné et la règle violée."""

    def __init__(self, bt: str, rule_id: str, message: str) -> None:
        self.bt = bt
        self.rule_id = rule_id
        super().__init__(f"[{bt}] ({rule_id}) {message}")


class PrecedingInvoiceReferenceRequiredError(InvoiceValidationError):
    """BT-25/BT-26 manquants alors que le type de document est un avoir/facture rectificative."""

    def __init__(self, bt: str, invoice_type_code: str) -> None:
        super().__init__(
            bt,
            rule_id="preceding_invoice_required",
            message=(
                f"obligatoire lorsque BT-3 = {invoice_type_code!r} "
                "(avoir ou facture rectificative)."
            ),
        )


class PrecedingInvoiceReferenceNotAllowedError(InvoiceValidationError):
    """BT-25/BT-26 renseignés alors que le type de document est une facture normale."""

    def __init__(self, bt: str) -> None:
        super().__init__(
            bt,
            rule_id="preceding_invoice_not_allowed",
            message="doit être vide lorsque BT-3 = '380' (facture normale).",
        )


class VatCategoryInconsistentError(InvoiceValidationError):
    """Incohérence entre code catégorie de TVA, taux et typologie du client."""

    def __init__(self, bt: str, message: str) -> None:
        super().__init__(bt, rule_id="vat_category_consistency", message=message)


def classify_client_zone(seller: SellerParty, buyer: BuyerParty) -> ClientZone:
    """BT-40/BT-55 — classe l'acheteur en France / UE / Hors UE, relatif au pays du vendeur."""
    if buyer.country_code == seller.country_code:
        return ClientZone.DOMESTIC
    if buyer.country_code in EU_COUNTRY_CODES:
        return ClientZone.INTRA_EU
    return ClientZone.EXPORT_NON_EU


def validate_preceding_invoice_reference(invoice: Invoice) -> None:
    """Règles a) et b) : cohérence entre BT-3 et BT-25/BT-26."""
    is_credit_or_corrected = invoice.invoice_type_code in ("381", "384")

    if is_credit_or_corrected:
        if not invoice.preceding_invoice_reference:
            raise PrecedingInvoiceReferenceRequiredError("BT-25", invoice.invoice_type_code)
        if invoice.preceding_invoice_issue_date is None:
            raise PrecedingInvoiceReferenceRequiredError("BT-26", invoice.invoice_type_code)
    elif invoice.invoice_type_code == "380":
        if invoice.preceding_invoice_reference:
            raise PrecedingInvoiceReferenceNotAllowedError("BT-25")
        if invoice.preceding_invoice_issue_date is not None:
            raise PrecedingInvoiceReferenceNotAllowedError("BT-26")


def _check_category_rate_consistency(
    bt_category: str, bt_rate: str, category: VatCategoryCode, rate: object
) -> None:
    if category == VatCategoryCode.STANDARD:
        if rate is None or rate <= 0:
            raise VatCategoryInconsistentError(
                bt_rate,
                f"un taux strictement positif est requis pour la catégorie "
                f"{VatCategoryCode.STANDARD.value!r} (taux normal), reçu {rate!r}.",
            )
    elif category in _ZERO_RATE_CATEGORIES:
        if rate not in (None, 0):
            raise VatCategoryInconsistentError(
                bt_rate,
                f"le taux doit être nul (ou absent) pour la catégorie {category.value!r}, "
                f"reçu {rate!r}.",
            )


def _check_category_zone_consistency(
    bt_category: str, category: VatCategoryCode, zone: ClientZone
) -> None:
    if category == VatCategoryCode.INTRA_COMMUNITY and zone is not ClientZone.INTRA_EU:
        raise VatCategoryInconsistentError(
            bt_category,
            f"la catégorie {VatCategoryCode.INTRA_COMMUNITY.value!r} (autoliquidation "
            f"intracommunautaire) suppose un acheteur dans l'UE hors pays du vendeur, "
            f"typologie détectée : {zone.value!r}.",
        )
    if category == VatCategoryCode.EXPORT and zone is not ClientZone.EXPORT_NON_EU:
        raise VatCategoryInconsistentError(
            bt_category,
            f"la catégorie {VatCategoryCode.EXPORT.value!r} (export) suppose un acheteur "
            f"hors UE, typologie détectée : {zone.value!r}.",
        )
    if category == VatCategoryCode.REVERSE_CHARGE and zone is not ClientZone.DOMESTIC:
        raise VatCategoryInconsistentError(
            bt_category,
            f"la catégorie {VatCategoryCode.REVERSE_CHARGE.value!r} (autoliquidation "
            f"domestique) suppose un acheteur dans le même pays que le vendeur, "
            f"typologie détectée : {zone.value!r}.",
        )


def validate_vat_category_consistency(invoice: Invoice) -> None:
    """Règle c) : cohérence catégorie/taux de TVA avec la typologie du client.

    Contrôle à la fois la ventilation de TVA (BG-23, BT-118/BT-119) et chaque
    ligne de facture (BT-151/BT-152).
    """
    zone = classify_client_zone(invoice.seller, invoice.buyer)

    for breakdown in invoice.vat_breakdown:
        _check_category_rate_consistency(
            "BT-118", "BT-119", breakdown.category_code, breakdown.rate
        )
        _check_category_zone_consistency("BT-118", breakdown.category_code, zone)

    for line in invoice.lines:
        _check_category_rate_consistency("BT-151", "BT-152", line.vat_category_code, line.vat_rate)
        _check_category_zone_consistency("BT-151", line.vat_category_code, zone)


def validate_invoice(invoice: Invoice) -> None:
    """Exécute l'ensemble des règles de cohérence métier sur une facture.

    Lève la première :class:`InvoiceValidationError` rencontrée.
    """
    validate_preceding_invoice_reference(invoice)
    validate_vat_category_consistency(invoice)
