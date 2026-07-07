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

**Exception — commit de release** : `vX.Y.Z — résumé` (sans préfixe de type),
cf. § Versioning ci-dessous. C'est le seul commit qui déroge à ce tableau ; il
sert de source de vérité à la régénération automatique du changelog.

## Branches

- `main` : toujours verte (tests + lint OK). Considérée protégée.
- Développement sur des branches `feature/xxx` (ou `fix/xxx`).
- Merge dans `main` **seulement** quand la CI passe.

## Versioning — SemVer

Tags `vMAJOR.MINOR.PATCH` :

- **PATCH** : correction rétro-compatible.
- **MINOR** : fonctionnalité rétro-compatible.
- **MAJOR** : rupture de compatibilité.

On crée un tag + une release GitHub **uniquement** quand une fonctionnalité
complète et stable est livrée. Exemples :

- `v0.1.0` — premier POC fonctionnel.
- `v1.0.0` — version jugée production-ready.

Le commit de release a pour message `vX.Y.Z — résumé court à l'impératif ou au
nom` (pas de préfixe `chore:` sur ce commit précis) : [CHANGELOG.md](CHANGELOG.md)
se régénère **automatiquement** à partir de ce message via
`tools/generate_changelog.py`, source de vérité unique — pas de saisie
manuelle séparée.

### Publier une release

```bash
git checkout main && git pull
# mettre à jour la version dans pyproject.toml
git commit -am "v0.1.0 — premier POC fonctionnel"
uv run python tools/generate_changelog.py   # régénère CHANGELOG.md, idempotent
git add CHANGELOG.md && git commit -m "docs: changelog v0.1.0"
git tag -a v0.1.0 -m "v0.1.0 — premier POC fonctionnel"
git push origin main --tags
```

Puis créer la release depuis l'interface GitHub (onglet *Releases*) en pointant
sur le tag. Relancer `tools/generate_changelog.py` avant un tag (ou après un
merge apportant plusieurs commits de version d'un coup) pour vérifier qu'aucune
entrée n'a été oubliée — le script est idempotent, il n'ajoute que les
versions absentes.

## Exporter le projet

`tools/export_project.py` génère un instantané du dépôt, utile hors du
contrôle de version :

```bash
uv run python tools/export_project.py            # .txt curé pour une IA
uv run python tools/export_project.py --backup    # .zip complet pour sauvegarde
uv run python tools/export_project.py --only src/facturx_generator/cii.py
```

Les fichiers sont écrits dans `Export/` (gitignoré, jamais commité).
