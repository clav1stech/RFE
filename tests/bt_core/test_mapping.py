"""Tests du mapping BT -> XML (facturx_generator.bt_core.mapping)."""

from __future__ import annotations

import pytest

from facturx_generator.bt_core.mapping import BT_XML_MAPPINGS, UBL_PENDING_DECISION, get_mapping
from facturx_generator.bt_core.model import Invoice
from facturx_generator.bt_core.profiles_matrix import PROFILE_MATRIX, PROFILE_ORDER


def test_all_bt_from_profile_matrix_are_mapped() -> None:
    assert set(BT_XML_MAPPINGS) == set(PROFILE_MATRIX)


def test_required_by_profile_matches_profile_matrix() -> None:
    for bt, mapping in BT_XML_MAPPINGS.items():
        for index, profile in enumerate(PROFILE_ORDER):
            assert mapping.required_by_profile[profile] == PROFILE_MATRIX[bt][index]


def test_every_mapping_has_a_cii_xpath() -> None:
    for mapping in BT_XML_MAPPINGS.values():
        assert mapping.xpath_cii


def test_ubl_paths_are_left_as_pending_placeholder() -> None:
    for mapping in BT_XML_MAPPINGS.values():
        assert mapping.xpath_ubl == UBL_PENDING_DECISION
        assert mapping.ubl_pending


def test_get_mapping_unknown_bt_raises_key_error() -> None:
    with pytest.raises(KeyError):
        get_mapping("BT-9999")


def test_root_invoice_bt_fields_are_covered_by_mapping() -> None:
    """Chaque BT porté directement par le modèle racine doit apparaître dans le mapping."""
    root_bts = {
        info.description.split(" —")[0].strip()
        for info in Invoice.model_fields.values()
        if info.description and info.description.startswith("BT-")
    }
    assert root_bts  # sanity check : la collecte n'est pas vide
    assert root_bts <= set(BT_XML_MAPPINGS)
