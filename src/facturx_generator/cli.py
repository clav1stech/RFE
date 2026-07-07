"""Interface en ligne de commande minimale : génère un XML de test sur stdout."""

from __future__ import annotations

import argparse
import sys

from facturx_generator.generator import Format, generate
from facturx_generator.profiles import PROFILES, get_profile


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="facturx-gen",
        description="Génère une facture de test Factur-X (CII) ou UBL.",
    )
    parser.add_argument(
        "profile",
        choices=sorted(PROFILES),
        help="Profil de facture de test à générer.",
    )
    parser.add_argument(
        "-f",
        "--format",
        choices=[f.value for f in Format],
        default=Format.CII.value,
        help="Format de sortie (défaut : cii).",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Fichier de sortie (défaut : stdout).",
    )
    args = parser.parse_args(argv)

    invoice = get_profile(args.profile)
    xml = generate(invoice, args.format)

    if args.output:
        with open(args.output, "wb") as fh:
            fh.write(xml)
    else:
        sys.stdout.buffer.write(xml)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
