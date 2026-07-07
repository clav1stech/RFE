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

Tenir le [CHANGELOG.md](CHANGELOG.md) à jour à chaque release.

### Publier une release

```bash
git checkout main && git pull
# mettre à jour la version dans pyproject.toml + CHANGELOG.md
git commit -am "chore: release v0.1.0"
git tag -a v0.1.0 -m "v0.1.0 — premier POC fonctionnel"
git push origin main --tags
```

Puis créer la release depuis l'interface GitHub (onglet *Releases*) en pointant
sur le tag.
