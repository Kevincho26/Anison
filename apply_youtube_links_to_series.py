#!/usr/bin/env python3
from __future__ import annotations

import csv
from pathlib import Path
from urllib.parse import urlparse, parse_qs

DOCS = Path("docs")
SERIES_DIR = DOCS / "series"
CSV_PATH = Path("youtube_playlist_links.csv")

TAB_HDR = '=== "'
YOUTUBE_TAB_LINE = '=== "YouTube"'

# ✅ Aliases: títulos del CSV -> títulos reales (H1) en tus páginas
TITLE_ALIASES = {
    "Bocchi the Rock!": "Bocchi the Rock",
    "Dan da dan": "Dandadan",
    "One Piece Film Red": "One Piece Film: Red",
    "Psycho-Pass": "Psycho Pass",
    "SPY FAMILY": "Spy x Family",
    "Super Campeones 2002": "Super Campeones",
}


# ---------- Helpers ----------

def read_first_h1(md_path: Path) -> str | None:
    for line in md_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return None


def norm_title(s: str) -> str:
    return " ".join((s or "").strip().lower().split())


def get_list_id(url: str) -> str | None:
    """
    Extract YouTube playlist ID from common URL formats:
      - https://www.youtube.com/playlist?list=PL...
      - https://www.youtube.com/watch?v=...&list=PL...
      - https://youtu.be/VIDEO?list=PL...
      - https://www.youtube.com/embed/videoseries?list=PL...
    """
    url = (url or "").strip()
    if not url:
        return None

    try:
        u = urlparse(url)
        qs = parse_qs(u.query)
        if "list" in qs and qs["list"]:
            return qs["list"][0]
    except Exception:
        return None

    return None


def is_embedable_youtube_list(list_id: str) -> bool:
    # Embeds que suelen funcionar:
    # PL... (playlists normales), UU... (uploads), OLAK5uy... (music)
    # Todo lo demás lo tratamos como "solo botón" para evitar "video unavailable".
    return list_id.startswith(("PL", "UU", "OLAK5uy"))


def build_youtube_tab_embed(list_id: str) -> list[str]:
    # ✅ Mejor embed para playlists (evita muchos "This video is unavailable")
    playlist_url = f"https://www.youtube.com/playlist?list={list_id}"
    embed_url = f"https://www.youtube.com/embed/videoseries?list={list_id}&rel=0"

    return [
        '    <iframe',
        f'      src="{embed_url}"',
        '      title="YouTube playlist player"',
        '      style="width:100%; aspect-ratio:16/9; border:0; border-radius:12px; overflow:hidden; display:block;"',
        '      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"',
        '      allowfullscreen',
        '      loading="lazy">',
        '    </iframe>',
        '    ',
        '    <div class="playlist-actions" markdown>',
        f'    [▶ Ver playlist en YouTube]({playlist_url}){{ .md-button }}',
        '    </div>',
    ]


def build_youtube_tab_button_only(list_id: str, note: str | None = None) -> list[str]:
    playlist_url = f"https://www.youtube.com/playlist?list={list_id}"

    lines = [
        '    <div class="playlist-actions" markdown>',
        f'    [▶ Ver playlist en YouTube]({playlist_url}){{ .md-button }}',
        '    </div>',
    ]
    if note:
        lines.append('    ')
        lines.append(f'    *{note}*')
    return lines


def replace_or_add_youtube_tab(md_path: Path, new_content_lines: list[str]) -> bool:
    """
    Replace content of === "YouTube" tab if present.
    Otherwise append a YouTube tab at end.
    """
    text = md_path.read_text(encoding="utf-8")
    lines = text.splitlines()

    out: list[str] = []
    i = 0
    changed = False
    found_youtube = False

    while i < len(lines):
        line = lines[i]

        if line.strip() == YOUTUBE_TAB_LINE:
            found_youtube = True
            out.append(line)
            i += 1

            # consume old YouTube tab block until next tab header or EOF
            while i < len(lines) and not lines[i].startswith(TAB_HDR):
                i += 1

            out.extend(new_content_lines)
            changed = True
            continue

        out.append(line)
        i += 1

    if not found_youtube:
        out.append("")
        out.append(YOUTUBE_TAB_LINE)
        out.extend(new_content_lines)
        changed = True

    new_text = "\n".join(out).rstrip() + "\n"
    if new_text != text:
        md_path.write_text(new_text, encoding="utf-8")
        return True

    return changed


# ---------- Main ----------

def main():
    if not CSV_PATH.exists():
        raise SystemExit(
            f"No encuentro {CSV_PATH}.\n"
            f"Pon el CSV en la raíz del repo (junto a mkdocs.yml)."
        )

    # Map: title -> md path
    md_by_title: dict[str, Path] = {}
    md_by_norm: dict[str, Path] = {}

    for md in SERIES_DIR.rglob("*.md"):
        if md.name.lower() in ("index.md", ".pages"):
            continue
        title = read_first_h1(md)
        if not title:
            continue
        md_by_title[title] = md
        md_by_norm[norm_title(title)] = md

    updated = 0
    missing_pages: list[str] = []
    bad_urls: list[tuple[str, str]] = []
    mix_lists: list[tuple[str, str]] = []

    with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)

        if not reader.fieldnames:
            raise SystemExit("CSV vacío o sin encabezados.")

        # tolerate Title/URL variants
        fields = {h.strip().lower(): h for h in reader.fieldnames}
        title_col = fields.get("title")
        url_col = fields.get("url")

        if not title_col or not url_col:
            raise SystemExit(f"CSV debe tener columnas 'title' y 'url'. Encontré: {reader.fieldnames}")

        for row in reader:
            raw_title = (row.get(title_col) or "").strip()
            raw_url = (row.get(url_col) or "").strip()
            if not raw_title or not raw_url:
                continue

            # ✅ aplicar alias si existe
            raw_title = TITLE_ALIASES.get(raw_title, raw_title)

            list_id = get_list_id(raw_url)
            if not list_id:
                bad_urls.append((raw_title, raw_url))
                continue

            md = md_by_title.get(raw_title) or md_by_norm.get(norm_title(raw_title))
            if not md:
                missing_pages.append(raw_title)
                continue

            # Build content: embed or button-only
            if is_embedable_youtube_list(list_id):
                new_content = build_youtube_tab_embed(list_id)
            else:
                mix_lists.append((raw_title, list_id))
                new_content = build_youtube_tab_button_only(
                    list_id,
                    note="Este enlace parece ser un Mix/Radio de YouTube (a veces no se puede embeber)."
                )

            if replace_or_add_youtube_tab(md, new_content):
                updated += 1

    print(f"✅ Páginas actualizadas: {updated}")

    if missing_pages:
        print("\n⚠️ No encontré página para estos títulos (revisa si el H1 coincide):")
        for t in missing_pages:
            print(" -", t)

    if bad_urls:
        print("\n⚠️ URLs sin parámetro ?list= (no pude sacar el ID):")
        for t, u in bad_urls:
            print(f" - {t}: {u}")

    if mix_lists:
        print("\nℹ️ Detecté listas tipo Mix/Radio (solo puse botón, sin embed):")
        for t, lid in mix_lists:
            print(f" - {t}: {lid}")


if __name__ == "__main__":
    main()
