#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urlparse, parse_qs

SERIES_DIR = Path("docs/series")

TAB_HDR = re.compile(r'^===\s+"([^"]+)"\s*$')

SPOTIFY_PLAYLIST_RE = re.compile(r'https?://open\.spotify\.com/playlist/([A-Za-z0-9]+)', re.I)
SPOTIFY_EMBED_RE    = re.compile(r'https?://open\.spotify\.com/embed/playlist/([A-Za-z0-9]+)', re.I)

YOUTUBE_PLAYLIST_RE = re.compile(r'https?://(?:www\.)?youtube\.com/playlist\?[^ \n]*list=([A-Za-z0-9_-]+)', re.I)
YOUTUBE_EMBED_LIST_RE = re.compile(r'https?://www\.youtube\.com/embed/videoseries\?[^ \n]*list=([A-Za-z0-9_-]+)', re.I)
YOUTUBE_EMBED_RE = re.compile(r'https?://www\.youtube\.com/embed\?[^ \n]*list=([A-Za-z0-9_-]+)', re.I)

def spotify_urls_from_text(text: str) -> tuple[str | None, str | None]:
    """Return (playlist_url, embed_url)"""
    m = SPOTIFY_PLAYLIST_RE.search(text)
    if m:
        pid = m.group(1)
        return (f"https://open.spotify.com/playlist/{pid}", f"https://open.spotify.com/embed/playlist/{pid}")

    m = SPOTIFY_EMBED_RE.search(text)
    if m:
        pid = m.group(1)
        return (f"https://open.spotify.com/playlist/{pid}", f"https://open.spotify.com/embed/playlist/{pid}")

    return (None, None)

def youtube_list_id_from_any_url(text: str) -> str | None:
    # playlist page
    m = YOUTUBE_PLAYLIST_RE.search(text)
    if m:
        return m.group(1)

    # embed videoseries
    m = YOUTUBE_EMBED_LIST_RE.search(text)
    if m:
        return m.group(1)

    # embed ?list=
    m = YOUTUBE_EMBED_RE.search(text)
    if m:
        return m.group(1)

    # generic parse attempt (in case there is a shortened URL)
    for url in re.findall(r'https?://[^\s\)"]+', text):
        try:
            u = urlparse(url)
            qs = parse_qs(u.query)
            if "list" in qs and qs["list"]:
                return qs["list"][0]
        except Exception:
            pass
    return None

def build_spotify_block(embed_url: str, playlist_url: str) -> list[str]:
    # IMPORTANT: every line in tab content must be indented 4 spaces
    return [
        '    <iframe',
        f'      src="{embed_url}"',
        '      title="Spotify playlist player"',
        '      style="width:100%; aspect-ratio:21/9; border:0; border-radius:12px; overflow:hidden; display:block;"',
        '      allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"',
        '      loading="lazy">',
        '    </iframe>',
        '    ',
        '    <div class="playlist-actions" markdown>',
        f'    [▶ Abrir en Spotify]({playlist_url}){{ .md-button .md-button--primary }}',
        '    </div>',
    ]

def build_youtube_block(list_id: str) -> list[str]:
    playlist_url = f"https://www.youtube.com/playlist?list={list_id}"
    embed_url = f"https://www.youtube.com/embed?listType=playlist&list={list_id}"
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

def upgrade_md(md_path: Path) -> bool:
    text = md_path.read_text(encoding="utf-8")

    sp_playlist, sp_embed = spotify_urls_from_text(text)
    yt_list_id = youtube_list_id_from_any_url(text)

    lines = text.splitlines()
    out: list[str] = []
    i = 0
    changed = False

    while i < len(lines):
        line = lines[i]
        m = TAB_HDR.match(line)
        if not m:
            out.append(line)
            i += 1
            continue

        tab_name = m.group(1).strip().lower()
        out.append(line)
        i += 1

        # Consume current tab block until next tab header or EOF
        start_i = i
        block: list[str] = []
        while i < len(lines) and not TAB_HDR.match(lines[i]):
            block.append(lines[i])
            i += 1

        if tab_name == "spotify" and sp_playlist and sp_embed:
            # Replace entire spotify tab content with standardized block
            out.extend(build_spotify_block(sp_embed, sp_playlist))
            changed = True
        elif tab_name == "youtube":
            if yt_list_id:
                out.extend(build_youtube_block(yt_list_id))
                changed = True
            else:
                # Keep a clean placeholder, properly indented
                out.extend([
                    '    *(pendiente: añade el link de YouTube a esta playlist)*'
                ])
                # If old block had messy stuff, this is still a change:
                if block != ['    *(pendiente: añade el link de YouTube a esta playlist)*']:
                    changed = True
        else:
            # Other tabs (if any): keep block, but ensure indent safety
            out.extend(block)

    new_text = "\n".join(out).rstrip() + "\n"

    # Cleanup: remove repeated blank lines (but keep tabs formatting)
    new_text = re.sub(r"\n{4,}", "\n\n\n", new_text)

    if new_text != text:
        md_path.write_text(new_text, encoding="utf-8")
        return True
    return changed

def main():
    changed_files = 0
    scanned = 0

    for md in SERIES_DIR.rglob("*.md"):
        if md.name.lower() in ("index.md", ".pages"):
            continue
        scanned += 1
        if upgrade_md(md):
            changed_files += 1

    print(f"✅ Escaneados: {scanned}")
    print(f"✅ Modificados: {changed_files}")

if __name__ == "__main__":
    main()
