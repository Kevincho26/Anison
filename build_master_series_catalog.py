#!/usr/bin/env python3
from __future__ import annotations

import csv
from pathlib import Path

REPO_ROOT = Path(".")
DOCS = REPO_ROOT / "docs"
SERIES_DIR = DOCS / "series"
THUMBS_REPORT = REPO_ROOT / "thumbs_report.csv"  # mapping titulo -> thumb_file

# Ajusta este orden si quieres incluir otras letras
LETTERS_ORDER = ["0-9","A","B","C","D","E","F","G","H","J","K","L","M","N","O","P","R","S","T","U","V","W"]

def read_first_h1(md_path: Path) -> str | None:
    for line in md_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return None

def load_thumbs(report_path: Path) -> dict[str, str]:
    """
    Expects CSV with columns for title+thumb file.
    Accepts flexible headers:
      title: titulo / title / name
      file:  thumb_file / thumb / file / filename
    """
    if not report_path.exists():
        raise SystemExit(f"thumbs_report.csv not found at: {report_path}")

    with report_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise SystemExit("thumbs_report.csv has no headers.")

        cols = [c.lower().strip() for c in reader.fieldnames]

        def pick(*names: str) -> str | None:
            for n in names:
                if n in cols:
                    return n
            return None

        col_title = pick("titulo", "title", "name")
        col_file = pick("thumb_file", "thumb", "file", "filename")

        if not col_title or not col_file:
            raise SystemExit(
                f"thumbs_report.csv must have title+file columns. Found: {reader.fieldnames}"
            )

        mapping: dict[str, str] = {}
        for row in reader:
            t = (row.get(col_title) or "").strip()
            fn = (row.get(col_file) or "").strip()
            if t and fn:
                mapping[t] = fn
        return mapping

def main() -> None:
    thumbs = load_thumbs(THUMBS_REPORT)

    if not SERIES_DIR.exists():
        raise SystemExit(f"Series dir not found: {SERIES_DIR}")

    # letter -> [(title, rel_md, rel_thumb)]
    grouped: dict[str, list[tuple[str, str, str]]] = {k: [] for k in LETTERS_ORDER}

    # collect pages per letter folder
    for letter_dir in SERIES_DIR.iterdir():
        if not letter_dir.is_dir():
            continue

        letter = letter_dir.name
        if letter not in grouped:
            # ignore any unexpected folder
            continue

        for md in letter_dir.glob("*.md"):
            if md.name.lower() in ("index.md", ".pages"):
                continue

            title = read_first_h1(md)
            if not title:
                continue

            # link from docs/series/index.md -> docs/series/<LETTER>/<page>.md
            rel_md = f"{letter}/{md.name}"

            # image from docs/series/index.md -> docs/assets/thumbs/<file>
            thumb_file = thumbs.get(title, "")
            rel_thumb = f"../assets/thumbs/{thumb_file}" if thumb_file else ""

            grouped[letter].append((title, rel_md, rel_thumb))

        grouped[letter].sort(key=lambda x: x[0].lower())

    # Build docs/series/index.md
    out: list[str] = []
    out += [
        "---",
        "hide:",
        "  - toc",
        "---",
        "",
        "# Catálogo de Series (A–Z)",
        "",
        "Explora por letra. Cada sección muestra un grid con miniaturas y títulos.",
        "",
    ]

    for letter in LETTERS_ORDER:
        items = grouped.get(letter, [])
        if not items:
            continue

        count = len(items)
        label = "serie" if count == 1 else "series"

        # Create stable anchor id for nav linking
        # examples: az-a, az-b, az-0-9
        anchor = f"az-{letter.lower()}"

        # Category ONLY as title, with anchor
        out.append(f"## {letter} {{#{anchor}}}")
        out.append("")

        # Summary ONLY count (details open by default)
        out.append('<details class="az-block" open markdown>')
        out.append(f'<summary class="az-summary">{count} {label}</summary>')
        out.append("")
        out.append('<div class="grid cards az-grid" markdown>')
        out.append("")

        # Compact cards: one bullet per card, minimal whitespace
        for title, rel_md, rel_thumb in items:
            if rel_thumb:
                out.append(
                    f"-   [![{title}]({rel_thumb}){{ .az-thumb }}]({rel_md})  "
                    f"**[{title}]({rel_md})**"
                )
            else:
                out.append(f"-   **[{title}]({rel_md})**")

        out.append("")
        out.append("</div>")
        out.append("")
        out.append("</details>")
        out.append("")

    target = SERIES_DIR / "index.md"
    target.write_text("\n".join(out).rstrip() + "\n", encoding="utf-8")
    print(f"✅ Generated: {target}")

if __name__ == "__main__":
    main()
