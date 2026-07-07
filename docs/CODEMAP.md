# Codemap

Carte du code pour une IA qui intervient sur le projet : où trouver quoi, sans
relire tout le repo. Mise à jour par Claude dès qu'un module change de rôle,
qu'un fichier est ajouté/déplacé, ou qu'une couche change de contrat.

## Vue d'ensemble en une phrase par fichier

| Fichier | Rôle |
|---|---|
| `app.py` | Interface Streamlit — UI seule, zéro règle métier. |
| `src/facturx_generator/models.py` | Modèle métier (`Invoice`, `InvoiceLine`, `Party`, `TaxBreakdown`) + calcul des totaux. Seule source de vérité des montants. |
| `src/facturx_generator/mapping.py` | Table statique BT EN16931 → chemins CII/UBL. Documentation vivante affichée par l'UI ; **n'est lue par aucun sérialiseur**. |
| `src/facturx_generator/cii.py` | Sérialisation `Invoice` → XML CII (Factur-X/ZUGFeRD, profil EN16931). |
| `src/facturx_generator/ubl.py` | Sérialisation `Invoice` → XML UBL 2.1 (profil EN16931 / PEPPOL BIS). |
| `src/facturx_generator/profiles.py` | Factures de test prêtes à l'emploi (`PROFILES` dict) + `get_profile()`. |
| `src/facturx_generator/generator.py` | Façade : `generate(invoice, fmt)` bascule vers `cii.py` ou `ubl.py` selon `Format`. Point d'entrée unique pour produire un XML. |
| `src/facturx_generator/cli.py` | CLI `facturx-gen` (argparse) : profil → format → stdout/fichier. |
| `src/facturx_generator/__init__.py` | Surface publique du package (`Invoice`, `InvoiceLine`, `Party`, `TaxBreakdown`, `__version__`). |
| `tools/export_project.py` | Export du repo en `.txt` curé (IA) ou `.zip` (sauvegarde) — hors exploitation. |
| `tools/generate_changelog.py` | Régénère `CHANGELOG.md` depuis les commits de release — hors exploitation. |

## Flux de données (génération d'un XML)

```
Party / InvoiceLine  ──►  Invoice (models.py)
                              │
                    calcule line_total, tax_breakdowns,
                    tax_total, grand_total, due_payable
                              │
                              ▼
                    generator.generate(invoice, fmt)
                         /            \
                  cii.to_cii_xml   ubl.to_ubl_xml
                        │                │
                        ▼                ▼
                  XML CII (rsm/ram)  XML UBL (cac/cbc)
```

- **Un seul point d'entrée pour générer un XML** : `generator.generate()`. Ne jamais appeler `to_cii_xml`/`to_ubl_xml` directement depuis `app.py` ou `cli.py` — passer par la façade, seul endroit qui connaît le mapping `Format → sérialiseur`.
- **`Invoice` est la seule source des totaux.** `cii.py`/`ubl.py` ne recalculent jamais un montant : ils lisent les propriétés déjà arrondies (`line_total`, `tax_breakdowns`, `tax_total`, `tax_basis_total`, `grand_total`, `due_payable`) et se contentent de les formater (`f"{x:.2f}"`).
- **`mapping.py` est un artefact de documentation/UI, pas un mécanisme de sérialisation.** Modifier `cii.py`/`ubl.py` ne nécessite pas de toucher `mapping.py`, et réciproquement — les deux peuvent diverger sans casser la génération (le mapping n'est qu'un affichage pédagogique dans l'onglet Streamlit « Mapping BT ↔ CII/UBL »).

## Invariants à connaître avant de modifier le code

- **Tous les montants sont des `Decimal`, jamais des `float`** (précision financière). Toute nouvelle valeur monétaire doit passer par `_money()` (`models.py`) qui arrondit à 2 décimales en `ROUND_HALF_UP` — ne pas réimplémenter un arrondi ailleurs.
- **`InvoiceLine.__post_init__` normalise `quantity`/`unit_price`/`vat_rate` en `Decimal`** même si l'appelant passe un `int`/`float`/`str` — les profils et l'UI peuvent construire une ligne sans caster explicitement.
- **`tax_breakdowns` agrège par `(vat_category, vat_rate)`**, pas ligne à ligne : plusieurs lignes au même taux fusionnent leur base imposable avant calcul de la TVA (évite les écarts d'arrondi ligne par ligne).
- **Couche UI strictement étanche** : `app.py` n'importe que la surface publique de `facturx_generator` (modèle, `generate`, `PROFILES`, `BT_MAPPINGS`) — aucune logique de calcul ou de sérialisation n'y vit. Un futur point d'entrée (API REST, batch) doit suivre le même principe : consommateur de `facturx_generator`, jamais dépositaire de règles métier.
- **`Format` (`generator.py`) est la seule liste des formats de sortie supportés.** Ajouter une syntaxe (ex. futur profil PEPPOL spécifique) = nouveau membre d'enum + nouveau module `xxx.py` avec une fonction `to_xxx_xml(invoice) -> bytes` + branchement dans `generate()` — jamais un `if` dispersé dans `app.py`/`cli.py`.

## Ajouter un profil de facture de test

1. `src/facturx_generator/profiles.py` : fonction `build_xxx() -> Invoice`.
2. L'enregistrer dans `PROFILES`.
3. Apparaît automatiquement dans l'UI (sélecteur) et la CLI (`facturx-gen xxx`) — aucune autre modification nécessaire.
4. Ajouter un test dans `tests/` validant ses totaux (`tax_basis_total`, `tax_total`, `grand_total`).

## Ajouter/corriger une Business Term dans le mapping

- `src/facturx_generator/mapping.py` : ajouter une entrée `BTMapping(bt, label, cii_path, ubl_path)` dans `BT_MAPPINGS`. N'affecte que l'onglet de documentation de l'UI, jamais la génération XML elle-même (cf. invariant ci-dessus).

## Tests (`tests/`)

Miroir de `src/facturx_generator/` : `test_models.py` (totaux/arrondis), `test_cii.py`, `test_ubl.py` (structure XML par XPath). Un changement dans `models.py` qui touche un calcul de total doit être couvert ici avant `cii.py`/`ubl.py` (les deux sérialiseurs ne font que lire ces valeurs).
