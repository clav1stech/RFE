"""Tests de la matrice des profils Factur-X (facturx_generator.bt_core.profiles_matrix)."""

from __future__ import annotations

import pytest

from facturx_generator.bt_core.profiles_matrix import (
    PROFILE_MATRIX,
    PROFILE_ORDER,
    BTRequirement,
    FacturXProfile,
    bts_for_profile,
    requirement_for,
)


def test_every_row_has_one_requirement_per_profile() -> None:
    for bt, row in PROFILE_MATRIX.items():
        assert len(row) == len(PROFILE_ORDER), bt


def test_requirement_for_known_bt() -> None:
    assert requirement_for("BT-1", FacturXProfile.MINIMUM) is BTRequirement.MANDATORY
    assert requirement_for("BT-126", FacturXProfile.MINIMUM) is BTRequirement.NOT_APPLICABLE
    assert requirement_for("BT-126", FacturXProfile.BASIC) is BTRequirement.MANDATORY


def test_requirement_for_unknown_bt_raises_key_error() -> None:
    with pytest.raises(KeyError):
        requirement_for("BT-9999", FacturXProfile.EN16931)


def test_minimum_profile_excludes_invoice_lines() -> None:
    minimum_bts = bts_for_profile(FacturXProfile.MINIMUM)
    line_bts = ["BT-126", "BT-129", "BT-130", "BT-131", "BT-146", "BT-151", "BT-153"]
    for bt in line_bts:
        assert minimum_bts[bt] is BTRequirement.NOT_APPLICABLE


def test_basic_wl_excludes_lines_but_includes_vat_breakdown() -> None:
    basic_wl_bts = bts_for_profile(FacturXProfile.BASIC_WL)
    assert basic_wl_bts["BT-126"] is BTRequirement.NOT_APPLICABLE
    assert basic_wl_bts["BT-116"] is BTRequirement.MANDATORY


def test_extended_matches_en16931_for_modeled_bts() -> None:
    en16931_bts = bts_for_profile(FacturXProfile.EN16931)
    extended_bts = bts_for_profile(FacturXProfile.EXTENDED)
    assert en16931_bts == extended_bts
