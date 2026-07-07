"""Façade de génération : point d'entrée unique pour produire un format donné."""

from __future__ import annotations

from enum import StrEnum

from facturx_generator.cii import to_cii_xml
from facturx_generator.models import Invoice
from facturx_generator.ubl import to_ubl_xml


class Format(StrEnum):
    """Formats de sortie supportés."""

    CII = "cii"  # UN/CEFACT CII (données Factur-X)
    UBL = "ubl"  # OASIS UBL 2.1


def generate(invoice: Invoice, fmt: Format | str) -> bytes:
    """Génère le XML de la facture dans le format demandé."""
    fmt = Format(fmt)
    if fmt is Format.CII:
        return to_cii_xml(invoice)
    if fmt is Format.UBL:
        return to_ubl_xml(invoice)
    raise ValueError(f"Format non supporté : {fmt!r}")
