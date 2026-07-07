"""Tests de la sérialisation UBL 2.1."""

from lxml import etree

from facturx_generator.profiles import build_multi_vat, build_standard_fr
from facturx_generator.ubl import NSMAP, to_ubl, to_ubl_xml

# lxml refuse un préfixe None dans find(); on nomme l'espace par défaut.
_NS = {"inv": NSMAP[None], "cac": NSMAP["cac"], "cbc": NSMAP["cbc"]}


def test_ubl_is_well_formed():
    xml = to_ubl_xml(build_standard_fr())
    parsed = etree.fromstring(xml)
    assert parsed.tag == f"{{{NSMAP[None]}}}Invoice"


def test_ubl_contains_core_bt():
    root = to_ubl(build_standard_fr())
    assert root.find("cbc:ID", namespaces=_NS).text == "FA-2026-0001"  # BT-1
    assert root.find("cbc:IssueDate", namespaces=_NS).text == "2026-01-15"  # BT-2
    payable = root.find("cac:LegalMonetaryTotal/cbc:PayableAmount", namespaces=_NS)
    assert payable.text == "1140.00"  # BT-115
    assert payable.get("currencyID") == "EUR"


def test_ubl_tax_subtotals():
    root = to_ubl(build_multi_vat())
    subtotals = root.findall("cac:TaxTotal/cac:TaxSubtotal", namespaces=_NS)
    assert len(subtotals) == 2
