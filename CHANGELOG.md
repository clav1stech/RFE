# Changelog

Toutes les modifications notables de ce projet sont documentées ici.

Le format s'inspire de [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/)
et le projet suit le [Semantic Versioning](https://semver.org/lang/fr/).

## [Non publié]

### Ajouté
- (à compléter au fil des développements)

## [0.1.0] — 2026-07-07

### Ajouté
- Modèle de facture métier (`Invoice`, `InvoiceLine`, `Party`, `TaxBreakdown`)
  avec calcul des totaux et ventilation de TVA (BG-22 / BG-23).
- Sérialisation **CII** (Factur-X, profil EN16931).
- Sérialisation **UBL 2.1** (profil EN16931).
- Table de mapping des Business Terms EN16931 ↔ CII / UBL.
- Trois profils de factures de test : `standard_fr`, `multi_vat`, `zero_vat`.
- Façade de génération et CLI `facturx-gen`.
- Interface Streamlit (`app.py`) découplée de la logique métier.
- Outillage : `uv` + `uv.lock`, `.python-version`, `requirements.txt`,
  tests `pytest`, lint `ruff`, CI GitHub Actions.

[Non publié]: https://github.com/clav1stech/rfe/compare/v0.1...HEAD
[0.1.0]: https://github.com/clav1stech/rfe/releases/tag/v0.1
