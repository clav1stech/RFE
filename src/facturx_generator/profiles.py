"""Profils de factures de test prêts à l'emploi.

Pour ajouter un nouveau profil : écrire une fonction `build_*() -> Invoice`,
puis l'enregistrer dans le dictionnaire ``PROFILES``. Il sera automatiquement
proposé dans l'interface Streamlit et la CLI.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import date
from decimal import Decimal

from facturx_generator.models import Invoice, InvoiceLine, Party


def _seller_fr() -> Party:
    return Party(
        name="Fournitures Alpes SAS",
        line_one="12 rue de la République",
        city="Grenoble",
        post_code="38000",
        country_code="FR",
        vat_id="FR40123456789",
        legal_id="12345678900012",
    )


def _buyer_metro() -> Party:
    return Party(
        name="Grenoble-Alpes Métropole",
        line_one="3 rue Malakoff",
        city="Grenoble",
        post_code="38000",
        country_code="FR",
        vat_id="FR97200040715",
        legal_id="20004071500019",
    )


def build_standard_fr() -> Invoice:
    """Facture standard française, TVA 20 %, deux lignes."""
    return Invoice(
        invoice_number="FA-2026-0001",
        issue_date=date(2026, 1, 15),
        due_date=date(2026, 2, 14),
        invoice_type_code="380",
        currency="EUR",
        buyer_reference="SERVICE-ACHATS-01",
        note="Facture de test — profil standard FR.",
        seller=_seller_fr(),
        buyer=_buyer_metro(),
        lines=[
            InvoiceLine(
                line_id="1",
                name="Prestation de conseil",
                description="Accompagnement dématérialisation.",
                quantity=Decimal("10"),
                unit_code="HUR",  # heure
                unit_price=Decimal("80.00"),
                vat_rate=Decimal("20"),
            ),
            InvoiceLine(
                line_id="2",
                name="Licence logicielle (mensuelle)",
                quantity=Decimal("1"),
                unit_code="C62",  # unité
                unit_price=Decimal("150.00"),
                vat_rate=Decimal("20"),
            ),
        ],
    )


def build_multi_vat() -> Invoice:
    """Facture avec taux de TVA mixtes (20 % et 5,5 %)."""
    return Invoice(
        invoice_number="FA-2026-0002",
        issue_date=date(2026, 3, 1),
        due_date=date(2026, 3, 31),
        invoice_type_code="380",
        currency="EUR",
        buyer_reference="SERVICE-RESTO",
        note="Facture de test — taux de TVA multiples.",
        seller=_seller_fr(),
        buyer=_buyer_metro(),
        lines=[
            InvoiceLine(
                line_id="1",
                name="Denrées alimentaires",
                quantity=Decimal("50"),
                unit_code="KGM",
                unit_price=Decimal("3.20"),
                vat_rate=Decimal("5.5"),
            ),
            InvoiceLine(
                line_id="2",
                name="Matériel de cuisine",
                quantity=Decimal("2"),
                unit_code="C62",
                unit_price=Decimal("120.00"),
                vat_rate=Decimal("20"),
            ),
        ],
    )


def build_zero_vat() -> Invoice:
    """Facture exonérée de TVA (catégorie E, taux 0 %)."""
    return Invoice(
        invoice_number="FA-2026-0003",
        issue_date=date(2026, 4, 10),
        due_date=date(2026, 5, 10),
        invoice_type_code="380",
        currency="EUR",
        buyer_reference="SERVICE-FORMATION",
        note="Facture de test — exonération de TVA (art. 261-4-4 CGI).",
        seller=_seller_fr(),
        buyer=_buyer_metro(),
        lines=[
            InvoiceLine(
                line_id="1",
                name="Formation professionnelle",
                quantity=Decimal("3"),
                unit_code="DAY",
                unit_price=Decimal("600.00"),
                vat_rate=Decimal("0"),
                vat_category="E",  # exonéré
            ),
        ],
    )


PROFILES: dict[str, Callable[[], Invoice]] = {
    "standard_fr": build_standard_fr,
    "multi_vat": build_multi_vat,
    "zero_vat": build_zero_vat,
}


def get_profile(name: str) -> Invoice:
    """Retourne la facture d'un profil enregistré."""
    if name not in PROFILES:
        raise KeyError(f"Profil inconnu : {name!r}. Profils disponibles : {sorted(PROFILES)}")
    return PROFILES[name]()
