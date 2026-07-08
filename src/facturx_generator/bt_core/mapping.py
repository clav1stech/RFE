"""Chargeur du mapping BT → XML (``mapping_data.json``).

Contrairement à :mod:`facturx_generator.mapping` (table Python en dur, dédiée
à l'onglet de documentation de l'UI actuelle), ce mapping vit dans un fichier
de configuration séparé du code — format pivot, indépendant du langage,
pensé pour être relu/édité sans toucher au code Python.

``required_by_profile`` est dérivé de
:data:`facturx_generator.bt_core.profiles_matrix.PROFILE_MATRIX` au moment de
la génération du fichier JSON (source de vérité unique des niveaux
d'exigence) — cf. test de cohérence dans ``tests/bt_core/test_mapping.py``.

Les chemins ``xpath_ubl`` sont volontairement laissés en placeholder tant que
le choix CII/UBL n'est pas tranché avec Fabienne (cf. réunion de cadrage).
"""

from __future__ import annotations

import json
from importlib import resources
from typing import NamedTuple

from facturx_generator.bt_core.profiles_matrix import BTRequirement, FacturXProfile

UBL_PENDING_DECISION = "TODO: à valider avec Fabienne si UBL est requis"


class BTXmlMapping(NamedTuple):
    """Correspondance d'un Business Term vers les syntaxes XML et son exigence par profil."""

    bt: str
    label: str
    required_by_profile: dict[FacturXProfile, BTRequirement]
    xpath_cii: str
    xpath_ubl: str

    @property
    def ubl_pending(self) -> bool:
        """True tant que le chemin UBL n'a pas été validé (placeholder TODO)."""
        return self.xpath_ubl == UBL_PENDING_DECISION


def _load(path: resources.abc.Traversable) -> dict[str, BTXmlMapping]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    mappings: dict[str, BTXmlMapping] = {}
    for bt, entry in raw.items():
        mappings[bt] = BTXmlMapping(
            bt=bt,
            label=entry["label"],
            required_by_profile={
                FacturXProfile(profile): BTRequirement(requirement)
                for profile, requirement in entry["required_by_profile"].items()
            },
            xpath_cii=entry["xpath_cii"],
            xpath_ubl=entry["xpath_ubl"],
        )
    return mappings


#: Table complète BT → mapping XML, indexée par identifiant de Business Term.
BT_XML_MAPPINGS: dict[str, BTXmlMapping] = _load(
    resources.files("facturx_generator.bt_core").joinpath("mapping_data.json")
)


def get_mapping(bt: str) -> BTXmlMapping:
    """Retourne le mapping d'un Business Term, lève ``KeyError`` s'il est inconnu."""
    try:
        return BT_XML_MAPPINGS[bt]
    except KeyError as exc:
        raise KeyError(f"Business Term absent du mapping BT → XML : {bt!r}") from exc
