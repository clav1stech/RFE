# 🧾 facturx-generator

Générateur de **factures de test Factur-X / UBL** avec mapping des *Business
Terms* de la norme **EN 16931**. Outil pédagogique et de test pour la
dématérialisation des factures (réforme e-invoicing, Chorus Pro, PDP).

- **Deux syntaxes normées** : CII (UN/CEFACT — données Factur-X/ZUGFeRD) et
  UBL 2.1 (OASIS).
- **Profils de test** prêts à l'emploi (standard FR, TVA mixte, exonéré).
- **Logique métier découplée de l'UI** : moteur réutilisable en CLI / API,
  interface Streamlit par-dessus.

## 🚀 Application en ligne

L'application est déployée gratuitement sur **Streamlit Community Cloud** :

> 🔗 **https://clav1stech-rfe.streamlit.app** *(à activer, voir section déploiement)*

Chaque `push` sur `main` redéploie automatiquement l'application.

## ⚡ Quickstart (démarrage à froid, 3 commandes)

Prérequis unique : [`uv`](https://docs.astral.sh/uv/) (le seul outil à installer
au préalable — il gère Python et toutes les dépendances).

```bash
git clone https://github.com/clav1stech/rfe.git
cd rfe
uv sync
```

Puis lancer l'application :

```bash
uv run streamlit run app.py
```

`uv sync` installe **exactement** les versions figées dans `uv.lock` et la
version Python de `.python-version` : environnement 100 % reproductible sur
n'importe quelle machine, sans installation Python préalable.

### Générer un XML en ligne de commande

```bash
uv run facturx-gen standard_fr --format cii            # CII sur stdout
uv run facturx-gen multi_vat  --format ubl -o out.xml  # UBL dans un fichier
```

### Lancer les tests et le lint

```bash
uv run pytest
uv run ruff check .
```

## 📁 Structure du repo

```
rfe/
├── app.py                      # Interface Streamlit (UI uniquement)
├── src/facturx_generator/      # Logique métier (aucune dépendance UI)
│   ├── models.py               # Modèle de facture + calcul des totaux
│   ├── mapping.py              # Table BT EN16931 ↔ CII / UBL
│   ├── cii.py                  # Sérialisation CII (Factur-X)
│   ├── ubl.py                  # Sérialisation UBL 2.1
│   ├── profiles.py             # Profils de factures de test
│   ├── generator.py            # Façade de génération (choix du format)
│   └── cli.py                  # Point d'entrée CLI `facturx-gen`
├── tests/                      # Tests pytest
├── pyproject.toml              # Métadonnées + dépendances (PEP 621)
├── uv.lock                     # Verrou de dépendances (committé)
├── requirements.txt            # Généré depuis le lock (Community Cloud)
├── .python-version             # Version Python figée
└── .github/workflows/ci.yml    # CI : ruff + pytest
```

## ➕ Ajouter un profil de facture de test

1. Ouvrir `src/facturx_generator/profiles.py`.
2. Écrire une fonction `build_mon_profil() -> Invoice` qui retourne une
   instance `Invoice` (voir les profils existants comme modèle).
3. L'enregistrer dans le dictionnaire `PROFILES` :

   ```python
   PROFILES = {
       ...
       "mon_profil": build_mon_profil,
   }
   ```

4. Il apparaît **automatiquement** dans l'UI Streamlit et la CLI. Ajouter un
   test dans `tests/` pour valider ses totaux.

## ☁️ Déploiement sur Streamlit Community Cloud

1. Pousser le repo sur GitHub (branche `main`).
2. Se connecter sur **https://share.streamlit.io** avec le compte GitHub.
3. **New app** → **From existing repo**.
4. Renseigner :
   - **Repository** : `clav1stech/rfe`
   - **Branch** : `main`
   - **Main file path** : `app.py`
5. **Deploy**. Community Cloud lit `requirements.txt` pour installer les
   dépendances, puis lance `app.py`.
6. Redéploiement automatique à chaque `push` sur `main`.

> `requirements.txt` est fourni pour la compatibilité Community Cloud (qui
> n'utilise pas encore `uv.lock`). Le régénérer après toute modification de
> dépendances :
>
> ```bash
> uv export --no-dev --no-hashes --no-emit-project --format requirements-txt -o requirements.txt
> ```

## 🤝 Contribuer / conventions

Voir [CONTRIBUTING.md](CONTRIBUTING.md) : Conventional Commits, branches
`feature/xxx`, SemVer, tenue du [CHANGELOG.md](CHANGELOG.md).

## 📄 Licence

[MIT](LICENSE).
