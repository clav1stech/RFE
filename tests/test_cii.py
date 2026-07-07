"""Tests de la sérialisation CII (Factur-X)."""

from lxml import etree

from facturx_generator.cii import NSMAP, to_cii, to_cii_xml
from facturx_generator.profiles import build_standard_fr


def test_cii_is_well_formed():
    xml = to_cii_xml(build_standard_fr())
    # Doit se re-parser sans erreur.
    parsed = etree.fromstring(xml)
    assert parsed.tag == f"{{{NSMAP['rsm']}}}CrossIndustryInvoice"


def test_cii_contains_core_bt():
    root = to_cii(build_standard_fr())

    def find(path: str) -> str:
        el = root.find(path, namespaces=NSMAP)
        assert el is not None, f"introuvable : {path}"
        return el.text

    assert find(".//rsm:ExchangedDocument/ram:ID") == "FA-2026-0001"  # BT-1
    assert find(".//rsm:ExchangedDocument/ram:TypeCode") == "380"  # BT-3
    grand = root.find(
        ".//ram:SpecifiedTradeSettlementHeaderMonetarySummation/ram:GrandTotalAmount",
        namespaces=NSMAP,
    )
    assert grand.text == "1140.00"  # BT-112


def test_cii_line_count():
    root = to_cii(build_standard_fr())
    lines = root.findall(".//ram:IncludedSupplyChainTradeLineItem", namespaces=NSMAP)
    assert len(lines) == 2
