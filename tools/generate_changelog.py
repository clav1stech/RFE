"""Régénère CHANGELOG.md à partir des commits de versioning (`vX.Y.Z — résumé`).

Usage : uv run python tools/generate_changelog.py

Source de vérité = messages de commit, pas une saisie manuelle séparée. Idempotent :
n'ajoute que les versions absentes du fichier existant, sans toucher aux entrées déjà
présentes (utile après un merge de branche qui apporte plusieurs commits de version
d'un coup, ou avant un tag de release pour vérifier que rien n'a été oublié).

Préserve l'en-tête existant (titre, chapô, section [Non publié]) : les nouvelles
entrées sont insérées juste avant la première version déjà publiée. Met aussi à
jour les liens de comparaison en pied de fichier (style Keep a Changelog) à partir
de l'URL du dépôt déclarée dans pyproject.toml.
"""

import re
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CHANGELOG_PATH = BASE_DIR / "CHANGELOG.md"
PYPROJECT_PATH = BASE_DIR / "pyproject.toml"

DEFAULT_PREAMBLE = """# Changelog

Toutes les modifications notables de ce projet sont documentées ici.

Le format s'inspire de [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/)
et le projet suit le [Semantic Versioning](https://semver.org/lang/fr/).

## [Non publié]

### Ajouté
- (à compléter au fil des développements)
"""

VERSION_RE = re.compile(r"^v(\d+\.\d+\.\d+)\s*[—-]\s*(.+)$")
RELEASED_HEADING_RE = re.compile(r"\n(## \[\d+\.\d+\.\d+\])")
LINK_LINE_RE = re.compile(r"^\[[^\]]+\]:\s")
COMMIT_SEP = "\x1f"  # séparateur improbable dans un message de commit
ENTRY_SEP = "\x1e"


def _repo_url() -> str:
    """URL du dépôt déclarée dans pyproject.toml (`[project.urls] Repository = "..."`)."""
    text = PYPROJECT_PATH.read_text(encoding="utf-8")
    m = re.search(r'^Repository\s*=\s*"([^"]+)"', text, re.MULTILINE)
    return m.group(1).rstrip("/") if m else ""


def _existing_versions() -> set[str]:
    if not CHANGELOG_PATH.exists():
        return set()
    return set(re.findall(r"^## \[(\d+\.\d+\.\d+)\]", CHANGELOG_PATH.read_text(), re.MULTILINE))


def _commits() -> list[tuple[str, str, str, str]]:
    """Retourne (version, date, résumé, corps) pour chaque commit vX.Y.Z, du plus récent au plus ancien."""
    fmt = f"%H{COMMIT_SEP}%ad{COMMIT_SEP}%s{COMMIT_SEP}%b{ENTRY_SEP}"
    raw = subprocess.run(
        ["git", "log", "main", "--date=short", f"--pretty=format:{fmt}"],
        cwd=BASE_DIR, capture_output=True, text=True, check=True,
    ).stdout
    out = []
    for entry in raw.split(ENTRY_SEP):
        entry = entry.strip("\n")
        if not entry:
            continue
        _hash, date, subject, body = entry.split(COMMIT_SEP, 3)
        m = VERSION_RE.match(subject.strip())
        if not m:
            continue
        version, summary = m.groups()
        out.append((version, date, summary.strip(), body.strip()))
    return out


def _insert_entries(content: str, blocks: list[str]) -> str:
    """Insère les blocs juste avant la première version déjà publiée (ou en fin de fichier).

    Chaque bloc se termine déjà par une ligne vide (cf. `main`) : on les concatène tels
    quels, sans séparateur additionnel, pour éviter une double ligne vide avant la suite.
    """
    m = RELEASED_HEADING_RE.search(content)
    insert_at = m.start() + 1 if m else len(content)
    return content[:insert_at] + "".join(blocks) + content[insert_at:]


def _update_footer_links(content: str, new_entries: list[tuple[str, str, str, str]]) -> str:
    """Ajoute les liens `[X.Y.Z]: .../releases/tag/vX.Y.Z` et met à jour `[Non publié]`."""
    repo_url = _repo_url()
    if not repo_url or not new_entries:
        return content

    lines = content.rstrip("\n").split("\n")
    footer_start = len(lines)
    for i in range(len(lines) - 1, -1, -1):
        if LINK_LINE_RE.match(lines[i]) or lines[i].strip() == "":
            footer_start = i
        else:
            break
    body_lines, footer_lines = lines[:footer_start], lines[footer_start:]
    while footer_lines and footer_lines[0].strip() == "":
        footer_lines.pop(0)

    newest_version = new_entries[0][0]
    unreleased_link = f"[Non publié]: {repo_url}/compare/v{newest_version}...HEAD"
    new_links = [f"[{v}]: {repo_url}/releases/tag/v{v}" for v, *_ in new_entries]

    unreleased_idx = next(
        (i for i, line in enumerate(footer_lines) if line.startswith("[Non publié]:")), None
    )
    if unreleased_idx is not None:
        footer_lines[unreleased_idx] = unreleased_link
        footer_lines = footer_lines[: unreleased_idx + 1] + new_links + footer_lines[unreleased_idx + 1 :]
    else:
        footer_lines = [unreleased_link, *new_links, *footer_lines]

    return "\n".join(body_lines) + "\n\n" + "\n".join(footer_lines) + "\n"


def main() -> None:
    known = _existing_versions()
    commits = _commits()
    new_entries = [c for c in commits if c[0] not in known]
    if not new_entries:
        print("CHANGELOG.md déjà à jour, rien à ajouter.")
        return

    blocks = []
    for version, date, summary, body in new_entries:
        block = f"## [{version}] - {date}\n{summary}.\n"
        if body:
            block += f"\n{body}\n"
        blocks.append(block + "\n")  # ligne vide de séparation avant l'entrée suivante

    content = CHANGELOG_PATH.read_text() if CHANGELOG_PATH.exists() else DEFAULT_PREAMBLE
    content = _insert_entries(content, blocks)
    content = _update_footer_links(content, new_entries)
    CHANGELOG_PATH.write_text(content.rstrip() + "\n")
    print(f"{len(new_entries)} entrée(s) ajoutée(s) : {', '.join(v for v, *_ in new_entries)}")


if __name__ == "__main__":
    main()
