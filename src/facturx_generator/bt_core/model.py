"""Modèle pivot Pydantic des Business Terms / Business Groups EN16931.

Contrairement à :mod:`facturx_generator.models` (modèle métier simplifié,
dataclasses, utilisé par la génération XML actuelle), ce module vise à
représenter fidèlement la structure hiérarchique BT/BG de la norme — groupes
(BG-x) et termes (BT-x) avec leurs cardinalités documentées (0..1, 1..1,
0..n, 1..n) — comme socle indépendant du client final (Comarch) et de la
syntaxe de sortie (CII/UBL).

Ne couvre que les groupes indépendants des décisions Comarch encore en
attente : en-tête document, vendeur (BG-4/BG-5), acheteur (BG-7/BG-8/BG-9),
lignes de facture (BG-25 et ses sous-groupes prix/TVA/article), ventilation
de TVA (BG-23), totaux (BG-22) et instructions de paiement (BG-16).
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from facturx_generator.bt_core.enums import InvoiceTypeCode, PaymentMeansCode, VatCategoryCode

CountryCode = Annotated[str, Field(pattern=r"^[A-Z]{2}$")]
CurrencyCode = Annotated[str, Field(pattern=r"^[A-Z]{3}$")]


class BTModel(BaseModel):
    """Base commune : interdit les champs non déclarés (fidélité au mapping BT)."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class SellerParty(BTModel):
    """BG-4 — VENDEUR (1..1 sur la facture)."""

    name: str = Field(..., description="BT-27 — nom du vendeur (1..1)")
    trading_name: str | None = Field(None, description="BT-28 — nom commercial (0..1)")
    identifiers: list[str] = Field(default_factory=list, description="BT-29 — identifiants (0..n)")
    legal_registration_id: str | None = Field(
        None, description="BT-30 — identifiant légal, SIREN/SIRET (0..1)"
    )
    vat_id: str | None = Field(None, description="BT-31 — n° TVA intracommunautaire (0..1)")
    tax_registration_id: str | None = Field(
        None, description="BT-32 — identifiant d'immatriculation fiscale (0..1)"
    )
    additional_legal_info: str | None = Field(
        None, description="BT-33 — informations légales complémentaires (0..1)"
    )
    electronic_address: str | None = Field(
        None, description="BT-34 — adresse électronique du vendeur (0..1)"
    )

    # BG-5 — ADRESSE POSTALE DU VENDEUR (1..1), champs aplatis ici.
    address_line1: str | None = Field(None, description="BT-35 — ligne d'adresse 1 (0..1)")
    address_line2: str | None = Field(None, description="BT-36 — ligne d'adresse 2 (0..1)")
    city: str | None = Field(None, description="BT-37 — ville (0..1)")
    post_code: str | None = Field(None, description="BT-38 — code postal (0..1)")
    country_subdivision: str | None = Field(
        None, description="BT-39 — subdivision de pays, ex. région (0..1)"
    )
    country_code: CountryCode = Field(
        ..., description="BT-40 — code pays ISO 3166-1 alpha-2 (1..1)"
    )


class BuyerParty(BTModel):
    """BG-7 — ACHETEUR (1..1 sur la facture)."""

    name: str = Field(..., description="BT-44 — nom de l'acheteur (1..1)")
    trading_name: str | None = Field(None, description="BT-45 — nom commercial (0..1)")
    identifiers: list[str] = Field(default_factory=list, description="BT-46 — identifiants (0..n)")
    legal_registration_id: str | None = Field(
        None, description="BT-47 — identifiant légal, SIREN/SIRET (0..1)"
    )
    vat_id: str | None = Field(None, description="BT-48 — n° TVA intracommunautaire (0..1)")

    # BG-8 — ADRESSE POSTALE DE L'ACHETEUR (1..1), champs aplatis ici.
    address_line1: str | None = Field(None, description="BT-50 — ligne d'adresse 1 (0..1)")
    address_line2: str | None = Field(None, description="BT-51 — ligne d'adresse 2 (0..1)")
    city: str | None = Field(None, description="BT-52 — ville (0..1)")
    post_code: str | None = Field(None, description="BT-53 — code postal (0..1)")
    country_subdivision: str | None = Field(
        None, description="BT-54 — subdivision de pays, ex. région (0..1)"
    )
    country_code: CountryCode = Field(
        ..., description="BT-55 — code pays ISO 3166-1 alpha-2 (1..1)"
    )

    # BG-9 — COORDONNÉES DE CONTACT DE L'ACHETEUR (0..1), champs aplatis ici.
    contact_point: str | None = Field(None, description="BT-56 — point de contact (0..1)")
    contact_phone: str | None = Field(None, description="BT-57 — téléphone de contact (0..1)")
    contact_email: str | None = Field(None, description="BT-58 — email de contact (0..1)")


class InvoiceLine(BTModel):
    """BG-25 — LIGNE DE FACTURE (1..n sur la facture).

    Regroupe aussi, aplatis, BG-29 (détails de prix) et BG-30 (TVA de ligne).
    """

    line_id: str = Field(..., description="BT-126 — identifiant de la ligne (1..1)")
    note: str | None = Field(None, description="BT-127 — note de ligne (0..1)")
    quantity: Decimal = Field(..., description="BT-129 — quantité facturée (1..1)")
    unit_code: str = Field(..., description="BT-130 — code unité de mesure (UN/ECE Rec 20) (1..1)")
    net_amount: Decimal = Field(
        ...,
        description="BT-131 — montant net de la ligne (quantité × prix net, remises incl.) (1..1)",
    )

    # BG-29 — DÉTAILS DE PRIX (1..1)
    net_price: Decimal = Field(..., description="BT-146 — prix unitaire net de l'article (1..1)")
    price_discount: Decimal | None = Field(
        None, description="BT-147 — remise sur le prix de l'article (0..1)"
    )
    gross_price: Decimal | None = Field(
        None, description="BT-148 — prix unitaire brut de l'article (0..1)"
    )
    price_base_quantity: Decimal | None = Field(
        None, description="BT-149 — quantité de base du prix (0..1)"
    )
    price_base_quantity_unit_code: str | None = Field(
        None, description="BT-150 — code unité de la quantité de base du prix (0..1)"
    )

    # BG-30 — INFORMATIONS TVA DE LA LIGNE (1..1)
    vat_category_code: VatCategoryCode = Field(
        ..., description="BT-151 — code catégorie de TVA de la ligne (1..1)"
    )
    vat_rate: Decimal | None = Field(
        None, description="BT-152 — taux de TVA de la ligne, % (0..1, absent si exonéré)"
    )

    # BG-31 — INFORMATIONS SUR L'ARTICLE (1..1)
    item_name: str = Field(..., description="BT-153 — nom de l'article facturé (1..1)")
    item_description: str | None = Field(
        None, description="BT-154 — description de l'article facturé (0..1)"
    )


class VatBreakdown(BTModel):
    """BG-23 — VENTILATION DE LA TVA (1..n), une entrée par couple (catégorie, taux)."""

    taxable_amount: Decimal = Field(
        ..., description="BT-116 — base imposable de la catégorie (1..1)"
    )
    tax_amount: Decimal = Field(..., description="BT-117 — montant de TVA de la catégorie (1..1)")
    category_code: VatCategoryCode = Field(..., description="BT-118 — code catégorie de TVA (1..1)")
    rate: Decimal | None = Field(
        None, description="BT-119 — taux de TVA de la catégorie, % (0..1, absent si exonéré)"
    )
    exemption_reason_text: str | None = Field(
        None, description="BT-120 — motif d'exonération de TVA, texte libre (0..1)"
    )
    exemption_reason_code: str | None = Field(
        None, description="BT-121 — motif d'exonération de TVA, code (0..1)"
    )


class DocumentTotals(BTModel):
    """BG-22 — TOTAUX DU DOCUMENT (1..1), sous-ensemble BT-109 à BT-115."""

    tax_basis_total: Decimal = Field(..., description="BT-109 — total hors taxes (1..1)")
    tax_total: Decimal = Field(..., description="BT-110 — montant total de TVA (1..1)")
    grand_total: Decimal = Field(..., description="BT-112 — total toutes taxes comprises (1..1)")
    paid_amount: Decimal | None = Field(None, description="BT-113 — montant déjà payé (0..1)")
    rounding_amount: Decimal | None = Field(None, description="BT-114 — montant d'arrondi (0..1)")
    due_payable_amount: Decimal = Field(..., description="BT-115 — net à payer (1..1)")


class PaymentInstructions(BTModel):
    """BG-16 — INSTRUCTIONS DE PAIEMENT (0..1)."""

    means_code: PaymentMeansCode = Field(..., description="BT-81 — code moyen de paiement (1..1)")
    means_text: str | None = Field(
        None, description="BT-82 — moyen de paiement, texte libre (0..1)"
    )
    remittance_info: str | None = Field(
        None, description="BT-83 — information de rapprochement (référence de virement) (0..1)"
    )
    payment_account_id: str | None = Field(
        None, description="BT-84 — identifiant du compte de paiement (IBAN) (0..1)"
    )
    payment_account_name: str | None = Field(
        None, description="BT-85 — nom du compte de paiement (0..1)"
    )
    payment_service_provider_id: str | None = Field(
        None, description="BT-86 — identifiant du prestataire de service de paiement (0..1)"
    )


class Invoice(BTModel):
    """BG-1 — FACTURE, agrégat racine du modèle pivot BT/BG."""

    invoice_number: str = Field(..., description="BT-1 — numéro de facture (1..1)")
    issue_date: date = Field(..., description="BT-2 — date d'émission (1..1)")
    invoice_type_code: InvoiceTypeCode = Field(
        ..., description="BT-3 — code type de document (1..1)"
    )
    currency_code: CurrencyCode = Field(
        ..., description="BT-5 — code devise de la facture, ISO 4217 (1..1)"
    )
    due_date: date | None = Field(None, description="BT-9 — date d'échéance de paiement (0..1)")
    buyer_reference: str | None = Field(None, description="BT-10 — référence acheteur (0..1)")
    note: str | None = Field(None, description="BT-22 — note libre sur la facture (0..1)")

    # Conditionnel : uniquement pour un avoir/facture rectificative (cf. validation.py).
    preceding_invoice_reference: str | None = Field(
        None, description="BT-25 — référence de la facture antérieure (0..1, conditionnel)"
    )
    preceding_invoice_issue_date: date | None = Field(
        None, description="BT-26 — date de la facture antérieure (0..1, conditionnel)"
    )

    seller: SellerParty = Field(..., description="BG-4 — vendeur (1..1)")
    buyer: BuyerParty = Field(..., description="BG-7 — acheteur (1..1)")
    payment_instructions: PaymentInstructions | None = Field(
        None, description="BG-16 — instructions de paiement (0..1)"
    )
    vat_breakdown: list[VatBreakdown] = Field(
        ..., min_length=1, description="BG-23 — ventilation de la TVA (1..n)"
    )
    lines: list[InvoiceLine] = Field(
        ..., min_length=1, description="BG-25 — lignes de facture (1..n)"
    )
    totals: DocumentTotals = Field(..., description="BG-22 — totaux du document (1..1)")
