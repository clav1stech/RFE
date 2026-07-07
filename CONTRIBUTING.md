# Contribuer

Projet mono-développeur, mais tenu avec un historique propre et professionnel.

## Environnement

```bash
uv sync            # installe tout (dépendances + dev)
uv run pytest      # tests
uv run ruff check .    # lint
uv run ruff format .   # formatage
```

## Convention de commits — Conventional Commits

Format : `type: résumé court à l'impératif`.

| Type       | Usage                                              |
|------------|----------------------------------------------------|
| `feat:`    | nouvelle fonctionnalité                            |
| `fix:`     | correction de bug                                  |
| `docs:`    | documentation seule                                |
| `refactor:`| refactoring sans changement de comportement        |
| `test:`    | ajout / modification de tests                      |
| `chore:`   | outillage, config, dépendances                     |

**Règle d'or** : un commit = **une unité de travail logique et testée**. Pas de
gros commit fourre-tout. On commite dès qu'un incrément est stable et que les
tests passent.

**Exception — commit de bump de version** : `vX.Y.Z — résumé` (sans préfixe
de type), cf. § Versioning ci-dessous. C'est le seul commit qui déroge à ce
tableau ; il sert de source de vérité à la régénération automatique du
changelog.

## Branches

- `main` : toujours verte (tests + lint OK). Considérée protégée.
- Développement sur des branches `feature/xxx` (ou `fix/xxx`).
- Merge dans `main` **seulement** quand la CI passe.

## Versioning — SemVer

`__version__` dans `src/facturx_generator/__init__.py` est la **source de
vérité unique** (affichée dans le titre du dashboard Streamlit ;
`pyproject.toml` la reprend dynamiquement via `[tool.hatch.version]`, jamais
une valeur dupliquée à la main).

**Le versioning se fait à chaque commit significatif poussé sur `main`**, pas
seulement à la publication d'une release :

- **Z (patch)** : cas par défaut, tout changement significatif normal
  (`feat:`, `fix:`, changement de comportement visible de l'app ou de la CLI).
  **Jamais** pour un commit purement interne (doc, typo, commentaire,
  outillage `tools/` sans impact utilisateur).
- **Y (minor)** : réservé aux gros changements nécessitant une branche dédiée
  (`feature/xxx`, chantier structurant) — remet Z à 0. Fusionné dans `main`
  seulement quand la CI passe (cf. § Branches).
- **X (major)** : jamais décidé seul, uniquement sur demande explicite.

Le commit qui bump la version a pour message `vX.Y.Z — résumé court à
l'impératif ou au nom` (seul commit à déroger au tableau Conventional
Commits, cf. ci-dessus) : [CHANGELOG.md](CHANGELOG.md) se régénère
**automatiquement** à partir de ce message via `tools/generate_changelog.py`
— pas de saisie manuelle séparée.

### Bumper la version (à chaque commit significatif)

```bash
# éditer __version__ dans src/facturx_generator/__init__.py
git commit -am "v0.1.1 — description du changement"
uv run python tools/generate_changelog.py   # régénère CHANGELOG.md, idempotent
git add CHANGELOG.md && git commit -m "docs: changelog v0.1.1"
git push
```

Relancer `tools/generate_changelog.py` avant un tag (ou après un merge
apportant plusieurs commits de version d'un coup) pour vérifier qu'aucune
entrée n'a été oubliée — le script est idempotent, il n'ajoute que les
versions absentes.

### Tags et releases GitHub — un seul tag par Y

Contrairement au bump de version (à chaque Z), **un seul tag/release par
palier Y** (ex. `v0.1`, `v0.2`), jamais un par Z. Le tag `vX.Y` est **mobile** :
à chaque bump Z sur cette ligne, on le retague sur le nouveau commit plutôt
que de créer `vX.Y.Z` :

```bash
git tag -f vX.Y HEAD
git push origin vX.Y --force
```

Le corps de la release s'enrichit au fil des Z (ne pas écraser l'historique
des sections précédentes). Nouveau tag/release **uniquement** pour un nouveau
Y. Ne jamais faire passer une release en « Latest » de sa propre initiative —
uniquement sur demande explicite.

## Exporter le projet

`tools/export_project.py` génère un instantané du dépôt, utile hors du
contrôle de version :

```bash
uv run python tools/export_project.py            # .txt curé pour une IA
uv run python tools/export_project.py --backup    # .zip complet pour sauvegarde
uv run python tools/export_project.py --only src/facturx_generator/cii.py
```

Les fichiers sont écrits dans `Export/` (gitignoré, jamais commité).
