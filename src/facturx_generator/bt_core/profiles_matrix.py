"""Matrice de couverture des Business Terms par profil Factur-X.

Croise chaque BT modélisé dans :mod:`facturx_generator.bt_core.model` avec les
5 profils Factur-X (du plus restreint au plus complet : MINIMUM, BASIC WL,
BASIC, EN16931, EXTENDED) pour déterminer son niveau d'exigence dans chaque
profil.

Le profil EXTENDED n'ajoute, dans la norme, que des Business Terms hors
périmètre EN16931 « core » (non modélisés ici) — il reprend donc exactement
les mêmes niveaux d'exigence que EN16931 pour tous les BT de cette matrice.

Simplification pédagogique assumée : la matrice officielle Factur-X (annexe
FNFE-MPE) est plus fine sur certaines conditions (ex. présence d'une remise).
Cette table donne une classification de référence suffisante pour piloter un
outil de test, pas une implémentation certifiée conforme.
"""

from __future__ import annotations

from enum import StrEnum


class FacturXProfile(StrEnum):
    """Les 5 profils Factur-X, du plus restreint au plus complet."""

    MINIMUM = "MINIMUM"
    BASIC_WL = "BASIC WL"
    BASIC = "BASIC"
    EN16931 = "EN 16931"
    EXTENDED = "EXTENDED"


#: Ordre de restriction croissante — utile pour des comparaisons ("au moins BASIC").
PROFILE_ORDER: tuple[FacturXProfile, ...] = (
    FacturXProfile.MINIMUM,
    FacturXProfile.BASIC_WL,
    FacturXProfile.BASIC,
    FacturXProfile.EN16931,
    FacturXProfile.EXTENDED,
)


class BTRequirement(StrEnum):
    """Niveau d'exigence d'un BT au sein d'un profil donné."""

    MANDATORY = "mandatory"  # Toujours présent
    CONDITIONAL = "conditional"  # Présent selon une règle métier (cf. validation.py)
    OPTIONAL = "optional"  # Peut être présent, jamais requis
    NOT_APPLICABLE = "not_applicable"  # Le profil n'inclut pas ce BT


_M = BTRequirement.MANDATORY
_C = BTRequirement.CONDITIONAL
_O = BTRequirement.OPTIONAL
_N = BTRequirement.NOT_APPLICABLE

# Raccourci de lisibilité : (MINIMUM, BASIC_WL, BASIC, EN16931, EXTENDED).
_Row = tuple[BTRequirement, BTRequirement, BTRequirement, BTRequirement, BTRequirement]

PROFILE_MATRIX: dict[str, _Row] = {
    # --- En-tête document ---
    "BT-1": (_M, _M, _M, _M, _M),
    "BT-2": (_M, _M, _M, _M, _M),
    "BT-3": (_M, _M, _M, _M, _M),
    "BT-5": (_M, _M, _M, _M, _M),
    "BT-9": (_O, _O, _O, _O, _O),
    "BT-10": (_N, _O, _O, _O, _O),
    "BT-22": (_N, _O, _O, _O, _O),
    "BT-25": (_N, _C, _C, _C, _C),
    "BT-26": (_N, _C, _C, _C, _C),
    # --- Vendeur (BG-4/BG-5) ---
    "BT-27": (_M, _M, _M, _M, _M),
    "BT-28": (_N, _O, _O, _O, _O),
    "BT-29": (_N, _O, _O, _O, _O),
    "BT-30": (_C, _C, _C, _C, _C),
    "BT-31": (_C, _C, _C, _C, _C),
    "BT-32": (_N, _O, _O, _O, _O),
    "BT-33": (_N, _O, _O, _O, _O),
    "BT-34": (_N, _O, _O, _O, _O),
    "BT-35": (_N, _M, _M, _M, _M),
    "BT-36": (_N, _O, _O, _O, _O),
    "BT-37": (_N, _M, _M, _M, _M),
    "BT-38": (_N, _M, _M, _M, _M),
    "BT-39": (_N, _O, _O, _O, _O),
    "BT-40": (_N, _M, _M, _M, _M),
    # --- Acheteur (BG-7/BG-8/BG-9) ---
    "BT-44": (_M, _M, _M, _M, _M),
    "BT-45": (_N, _O, _O, _O, _O),
    "BT-46": (_N, _O, _O, _O, _O),
    "BT-47": (_C, _C, _C, _C, _C),
    "BT-48": (_C, _C, _C, _C, _C),
    "BT-50": (_N, _M, _M, _M, _M),
    "BT-51": (_N, _O, _O, _O, _O),
    "BT-52": (_N, _M, _M, _M, _M),
    "BT-53": (_N, _M, _M, _M, _M),
    "BT-54": (_N, _O, _O, _O, _O),
    "BT-55": (_N, _M, _M, _M, _M),
    "BT-56": (_N, _O, _O, _O, _O),
    "BT-57": (_N, _O, _O, _O, _O),
    "BT-58": (_N, _O, _O, _O, _O),
    # --- Ventilation de TVA (BG-23) ---
    "BT-116": (_N, _M, _M, _M, _M),
    "BT-117": (_N, _M, _M, _M, _M),
    "BT-118": (_N, _M, _M, _M, _M),
    "BT-119": (_N, _C, _C, _C, _C),
    "BT-120": (_N, _C, _C, _C, _C),
    "BT-121": (_N, _C, _C, _C, _C),
    # --- Totaux (BG-22) ---
    "BT-109": (_M, _M, _M, _M, _M),
    "BT-110": (_M, _M, _M, _M, _M),
    "BT-112": (_M, _M, _M, _M, _M),
    "BT-113": (_N, _O, _O, _O, _O),
    "BT-114": (_N, _O, _O, _O, _O),
    "BT-115": (_M, _M, _M, _M, _M),
    # --- Lignes de facture (BG-25 et sous-groupes) ---
    "BT-126": (_N, _N, _M, _M, _M),
    "BT-127": (_N, _N, _O, _O, _O),
    "BT-129": (_N, _N, _M, _M, _M),
    "BT-130": (_N, _N, _M, _M, _M),
    "BT-131": (_N, _N, _M, _M, _M),
    "BT-146": (_N, _N, _M, _M, _M),
    "BT-147": (_N, _N, _O, _O, _O),
    "BT-148": (_N, _N, _O, _O, _O),
    "BT-149": (_N, _N, _O, _O, _O),
    "BT-150": (_N, _N, _O, _O, _O),
    "BT-151": (_N, _N, _M, _M, _M),
    "BT-152": (_N, _N, _C, _C, _C),
    "BT-153": (_N, _N, _M, _M, _M),
    "BT-154": (_N, _N, _O, _O, _O),
    # --- Paiement (BG-16) ---
    "BT-81": (_N, _C, _C, _C, _C),
    "BT-82": (_N, _O, _O, _O, _O),
    "BT-83": (_N, _O, _O, _O, _O),
    "BT-84": (_N, _C, _C, _C, _C),
    "BT-85": (_N, _O, _O, _O, _O),
    "BT-86": (_N, _O, _O, _O, _O),
}


def requirement_for(bt: str, profile: FacturXProfile) -> BTRequirement:
    """Niveau d'exigence d'un Business Term pour un profil Factur-X donné."""
    try:
        row = PROFILE_MATRIX[bt]
    except KeyError as exc:
        raise KeyError(f"Business Term inconnu de la matrice de profils : {bt!r}") from exc
    return row[PROFILE_ORDER.index(profile)]


def bts_for_profile(profile: FacturXProfile) -> dict[str, BTRequirement]:
    """Sous-ensemble de la matrice restreint à un profil (BT → exigence)."""
    index = PROFILE_ORDER.index(profile)
    return {bt: row[index] for bt, row in PROFILE_MATRIX.items()}
