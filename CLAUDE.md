# Instructions Claude

## Général
- Toujours répondre en **français**, sauf si l'utilisateur demande explicitement une autre langue.
- Développement avec Claude Code dans VSC sur PC ou Mac.

## Tenir ce fichier à jour
- Dès que tu **détectes une règle générale** du projet (invariant, convention, contrainte, préférence récurrente de l'utilisateur, piège à éviter), **ajoute-la ici** dans la section adéquate — ne la laisse pas seulement dans un commentaire de code ou dans l'échange.
- Ne consigner que les règles **durables et générales**, pas un détail ponctuel propre à une seule tâche. En cas de doute sur la portée, demander avant d'inscrire.
- Préférer **mettre à jour** une consigne existante plutôt que d'en empiler une quasi-identique ; garder ce fichier concis et sans doublon.
- Ce fichier consigne les règles générales ; `docs/CODEMAP.md` consigne la **structure du code** (rôle de chaque fichier, flux de données, invariants d'implémentation). Un changement d'architecture (fichier renommé/déplacé, nouvelle dépendance entre modules, nouveau invariant de calcul) se met à jour là-bas, pas ici.

## Vue d'ensemble du projet
`facturx-generator` : générateur de factures de test **Factur-X (CII) / UBL 2.1** avec mapping des Business Terms **EN 16931**. Outil pédagogique pour la dématérialisation des factures (e-invoicing, Chorus Pro, PDP).
- `app.py` : **point d'entrée** de l'interface Streamlit — UI uniquement, aucune logique métier.
- `src/facturx_generator/` : logique métier découplée de l'UI (réutilisable en CLI/API) — `models.py` (modèle facture + totaux), `mapping.py` (table BT EN16931 ↔ CII/UBL), `cii.py`/`ubl.py` (sérialisation par syntaxe), `profiles.py` (profils de factures de test), `generator.py` (façade de choix du format), `cli.py` (point d'entrée `facturx-gen`) — carte complète (flux de données, invariants, checklists d'ajout) dans `docs/CODEMAP.md`. **Lire la codemap avant d'intervenir** plutôt que de parcourir tout le code (fiabilité + économie de tokens).
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
- **Versionnage sémantique X.Y.Z À CHAQUE COMMIT SIGNIFICATIF poussé sur `main`** (pas seulement à la publication d'une release) — source de vérité unique : `__version__` dans `src/facturx_generator/__init__.py` (affiché dans l'UI Streamlit ; `pyproject.toml` la reprend dynamiquement via `[tool.hatch.version]`, jamais dupliquée en dur) :
  - **Z** : cas par défaut, tout changement significatif normal. **Jamais** pour un commit purement interne (doc, typo, commentaire, `tools/` sans impact utilisateur).
  - **Y** : réservé aux gros changements nécessitant une branche dédiée (chantier structurant) — remet Z à 0.
  - **X** : jamais décidé par Claude, uniquement sur demande explicite de l'utilisateur.
  Le commit qui bump la version déroge au tableau Conventional Commits : message `vX.Y.Z — résumé` (pas de préfixe de type), qui sert de **source de vérité unique** à `tools/generate_changelog.py` — ne jamais éditer `CHANGELOG.md` à la main, relancer ce script (idempotent : n'ajoute que les versions absentes).
- **Tags et releases GitHub : un seul tag/release par version Y** (ex. `v0.1`, `v0.2`), pas un par Z. Le tag `vX.Y` est **mobile** : à chaque bump Z sur cette ligne, on le retague (`git tag -f`/suppression+recréation) sur le nouveau commit plutôt que de créer `vX.Y.Z`. Le corps de la release s'enrichit au fil des Z (ne pas écraser l'historique des sections précédentes). Ne créer un nouveau tag/release que pour un nouveau Y.
- **Passage en « Latest » : uniquement sur demande explicite de l'utilisateur.** Ne jamais promouvoir une release de sa propre initiative, même après un bump Z.
- **`CHANGELOG.md`** suit Keep a Changelog : une entrée `## [X.Y.Z] - date` insérée par `tools/generate_changelog.py` juste avant la précédente version publiée (le chapô et la section `[Non publié]` en tête sont préservés), avec mise à jour des liens de comparaison en pied de fichier (pointant vers le tag mobile `vX.Y`, pas `vX.Y.Z`).
- **Fichiers jamais versionnés** : `.venv/`, `__pycache__/`. `uv.lock` et `requirements.txt` sont au contraire **committés** (reproductibilité de l'environnement / compatibilité Community Cloud).
- **Piège `uv.lock` + version dynamique** : `uv lock`/`uv sync` (uv 0.11.28) **omet systématiquement le champ `version`** du bloc `[[package]] name = "facturx-generator"` (version dynamique lue depuis `__init__.py`). Ce champ absent fait planter le parsing TOML sur Streamlit Community Cloud (« Failed to parse `uv.lock` … missing field `version` »). Après tout `uv lock`/`uv sync` qui régénère `uv.lock`, **vérifier que ce bloc contient bien `version = "X.Y.Z"`** (alignée sur `__init__.py`) et le rajouter à la main sinon, avant de committer.
  - Ce champ ajouté à la main rend le lockfile committé différent de ce que régénérerait `uv lock` — **le CI utilise donc `uv sync --frozen`** (installe depuis le lockfile tel quel) et non `--locked` (qui exigerait une correspondance exacte et échouerait à cause de ce champ). Ne pas repasser en `--locked` tant que ce workaround est en place.

## Environnement
```bash
uv sync                # installe dépendances + dev
uv run pytest          # tests
uv run ruff check .    # lint
uv run ruff format .   # formatage
uv run streamlit run app.py   # lancer l'app en local
```
