# Instructions Claude

## Général
- Toujours répondre en **français**, sauf si l'utilisateur demande explicitement une autre langue.
- Développement avec Claude Code dans VSC sur PC ou Mac.

## Tenir ce fichier à jour
- Dès que tu **détectes une règle générale** du projet (invariant, convention, contrainte, préférence récurrente de l'utilisateur, piège à éviter), **ajoute-la ici** dans la section adéquate — ne la laisse pas seulement dans un commentaire de code ou dans l'échange.
- Ne consigner que les règles **durables et générales**, pas un détail ponctuel propre à une seule tâche. En cas de doute sur la portée, demander avant d'inscrire.
- Préférer **mettre à jour** une consigne existante plutôt que d'en empiler une quasi-identique ; garder ce fichier concis et sans doublon.

## Vue d'ensemble du projet
`facturx-generator` : générateur de factures de test **Factur-X (CII) / UBL 2.1** avec mapping des Business Terms **EN 16931**. Outil pédagogique pour la dématérialisation des factures (e-invoicing, Chorus Pro, PDP).
- `app.py` : **point d'entrée** de l'interface Streamlit — UI uniquement, aucune logique métier.
- `src/facturx_generator/` : logique métier découplée de l'UI (réutilisable en CLI/API) — `models.py` (modèle facture + totaux), `mapping.py` (table BT EN16931 ↔ CII/UBL), `cii.py`/`ubl.py` (sérialisation par syntaxe), `profiles.py` (profils de factures de test), `generator.py` (façade de choix du format), `cli.py` (point d'entrée `facturx-gen`).
- `tests/` : tests pytest (miroir de `src/facturx_generator/`).
- `tools/` : utilitaires hors exploitation (jamais importés par `app.py`/`src/`) — `generate_changelog.py` (régénère `CHANGELOG.md` depuis les commits de release) et `export_project.py` (export `.txt` curé pour IA ou `.zip` de sauvegarde dans `Export/`, gitignoré).
- `CONTRIBUTING.md` : référence canonique et détaillée des conventions (commits, branches, SemVer) — ce fichier en reprend l'essentiel et ajoute les règles propres à Claude.

## Architecture (règles)
- **UI ↔ logique métier étanche** : `app.py` ne contient aucune règle métier (calcul, mapping, sérialisation) — tout vit dans `src/facturx_generator/`, importable indépendamment de Streamlit (CLI, futurs tests d'intégration, API).
- **Ajouter un profil de facture de test** : fonction `build_xxx() -> Invoice` dans `profiles.py`, enregistrée dans le dict `PROFILES` — apparaît alors automatiquement dans l'UI et la CLI ; toujours accompagner d'un test de ses totaux.
- **Mapping EN16931 centralisé** dans `mapping.py` : toute nouvelle Business Term se déclare là, pas dispersée dans `cii.py`/`ubl.py`.
- **`requirements.txt` est dérivé, jamais édité à la main** : régénéré depuis `uv.lock` après toute modification de dépendances (`uv export --no-dev --no-hashes --no-emit-project --format requirements-txt -o requirements.txt`) — nécessaire pour Streamlit Community Cloud qui ne lit pas encore `uv.lock`.

## Conventions de travail (commits / branches / releases)
Détail complet dans `CONTRIBUTING.md` ; résumé opérationnel pour Claude :
- **Conventional Commits** (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`), résumé court à l'impératif. Un commit = **une unité de travail logique et testée** (tests + lint OK), jamais un gros commit fourre-tout.
- **Ne jamais committer, pousser, taguer ou créer une release sans demande explicite de l'utilisateur.** Projet mono-développeur mais historique tenu comme un projet pro — chaque action git visible (push, tag, release) reste une décision de l'utilisateur.
- **`main` toujours verte** (tests + lint OK), considérée protégée. Chaque `push` sur `main` **redéploie automatiquement** l'app sur Streamlit Community Cloud — ne pousser sur `main` qu'un état réellement déployable.
- **Développement sur branches `feature/xxx` ou `fix/xxx`**, mergées dans `main` seulement quand la CI passe.
- **SemVer** (`vMAJOR.MINOR.PATCH`) : PATCH = correctif rétro-compatible, MINOR = fonctionnalité rétro-compatible, MAJOR = rupture de compatibilité.
- **Tag + release GitHub uniquement quand une fonctionnalité complète et stable est livrée** — pas à chaque commit. Le commit de release déroge au tableau Conventional Commits : message `vX.Y.Z — résumé` (pas de préfixe `chore:`), qui sert de **source de vérité unique** à `tools/generate_changelog.py` — ne jamais éditer `CHANGELOG.md` à la main, relancer ce script (idempotent : n'ajoute que les versions absentes). Puis tag annoté (`git tag -a vX.Y.Z -m "..."`) et `git push origin main --tags`. La release GitHub se crée ensuite depuis l'interface en pointant sur ce tag.
- **`CHANGELOG.md`** suit Keep a Changelog : une entrée `## [X.Y.Z] - date` insérée par `tools/generate_changelog.py` juste avant la précédente version publiée (le chapô et la section `[Non publié]` en tête sont préservés), avec mise à jour des liens de comparaison en pied de fichier.
- **Fichiers jamais versionnés** : `.venv/`, `__pycache__/`. `uv.lock` et `requirements.txt` sont au contraire **committés** (reproductibilité de l'environnement / compatibilité Community Cloud).

## Environnement
```bash
uv sync                # installe dépendances + dev
uv run pytest          # tests
uv run ruff check .    # lint
uv run ruff format .   # formatage
uv run streamlit run app.py   # lancer l'app en local
```
