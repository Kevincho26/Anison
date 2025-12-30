#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

DOCS = Path("docs")
SERIES_DIR = DOCS / "series"
THUMBS_REPORT = Path("thumbs_report.csv")

LETTERS_ORDER = ["0-9","A","B","C","D","E","F","G","H","J","K","L","M","N","O","P","R","S","T","U","V","W"]

def read_first_h1(md_path: Path) -> str | None:
    for line in md_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return None

def load_thumbs(report_path: Path) -> dict[str, str]:
    with report_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        cols = [c.lower().strip() for c in (reader.fieldnames or [])]

        def pick(*names):
            for n in names:
                if n in cols:
                    return n
            return None

        col_title = pick("titulo","title","name")
        col_file  = pick("thumb_file","thumb","file","filename")
        if not col_title or not col_file:
            raise SystemExit(f"thumbs_report.csv headers not compatible: {reader.fieldnames}")

        m = {}
        for row in reader:
            t = (row.get(col_title) or "").strip()
            fn = (row.get(col_file) or "").strip()
            if t and fn:
                m[t] = fn
        return m

def main():
    thumbs = load_thumbs(THUMBS_REPORT)

    entries = {}
    for letter in LETTERS_ORDER:
        letter_dir = SERIES_DIR / letter
        if not letter_dir.exists():
            continue

        for md in letter_dir.glob("*.md"):
            if md.name.lower() in ("index.md", ".pages"):
                continue

            title = read_first_h1(md)
            if not title:
                continue

            # use_directory_urls: true  -> /series/A/naruto/
            url = f"series/{letter}/{md.stem}/"

            thumb_file = thumbs.get(title, "")
            if thumb_file:
                thumb = f"assets/thumbs/{thumb_file}"
                entries[url] = {"title": title, "thumb": thumb}

    out1 = DOCS / "assets" / "search_thumbs.json"
    out2 = DOCS / "series" / "assets" / "search_thumbs.json"

    out1.parent.mkdir(parents=True, exist_ok=True)
    out2.parent.mkdir(parents=True, exist_ok=True)

    data = json.dumps(entries, ensure_ascii=False)
    out1.write_text(data, encoding="utf-8")
    out2.write_text(data, encoding="utf-8")

    print(f"✅ Wrote {out1} and {out2} with {len(entries)} entries")

if __name__ == "__main__":
    main()
