#!/usr/bin/env python3
from __future__ import annotations
import re
from pathlib import Path

SERIES_DIR = Path("docs/series")

# --- Regex helpers ---
SPOTIFY_IFRAME_RE = re.compile(r"<iframe[^>]*src=\"(https://open\.spotify\.com/embed/[^\"]+)\"[^>]*></iframe>", re.I)
YOUTUBE_IFRAME_RE = re.compile(r"<iframe[^>]*src=\"(https://www\.youtube\.com/embed/[^\"]+)\"[^>]*></iframe>", re.I)

SPOTIFY_LINK_RE = re.compile(r"\[Abrir en Spotify\]\((https://open\.spotify\.com/playlist/[^\)]+)\)", re.I)
YOUTUBE_LINK_RE = re.compile(r"\[Abrir en YouTube\]\((https?://[^\)]+youtube[^\)]+)\)", re.I)

def make_spotify_iframe(src: str) -> str:
    # Spotify se ve mejor más “banner”: 21/9 suele quedar perfecto
    return f"""<iframe
  src="{src}"
  title="Spotify playlist player"
  style="width:100%; aspect-ratio:21/9; border:0; border-radius:12px; overflow:hidden; display:block;"
  allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
  loading="lazy">
</iframe>"""

def make_youtube_iframe(src: str) -> str:
    return f"""<iframe
  src="{src}"
  title="YouTube playlist player"
  style="width:100%; aspect-ratio:16/9; border:0; border-radius:12px; overflow:hidden; display:block;"
  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
  allowfullscreen
  loading="lazy">
</iframe>"""

def make_buttons(spotify_url: str | None, youtube_url: str | None) -> str:
    btns = ['<div class="playlist-actions" markdown>']
    if spotify_url:
        btns.append(f'[▶ Abrir en Spotify]({spotify_url}){{ .md-button .md-button--primary }}')
    if youtube_url:
        btns.append(f'[▶ Abrir playlist en YouTube]({youtube_url}){{ .md-button }}')
    btns.append("</div>")
    return "\n".join(btns)

def upgrade_file(md: Path) -> bool:
    text = md.read_text(encoding="utf-8")

    # 1) Modernize iframes (preservando src)
    def rep_sp(m):
        return make_spotify_iframe(m.group(1))
    def rep_yt(m):
        return make_youtube_iframe(m.group(1))

    text2 = SPOTIFY_IFRAME_RE.sub(rep_sp, text)
    text2 = YOUTUBE_IFRAME_RE.sub(rep_yt, text2)

    # 2) Extraer links existentes (si estaban) para convertirlos a botones
    spotify_url = None
    youtube_url = None

    msp = SPOTIFY_LINK_RE.search(text2)
    if msp:
        spotify_url = msp.group(1)
        text2 = SPOTIFY_LINK_RE.sub("", text2)

    myt = YOUTUBE_LINK_RE.search(text2)
    if myt:
        youtube_url = myt.group(1)
        text2 = YOUTUBE_LINK_RE.sub("", text2)

    # 3) Insertar bloque de botones: lo ponemos justo después del último iframe (si hay)
    if (spotify_url or youtube_url) and ("playlist-actions" not in text2):
        # busca el último </iframe>
        idx = text2.lower().rfind("</iframe>")
        if idx != -1:
            idx_end = idx + len("</iframe>")
            text2 = text2[:idx_end] + "\n\n" + make_buttons(spotify_url, youtube_url) + text2[idx_end:]

    # Limpieza de líneas vacías excesivas
    text2 = re.sub(r"\n{3,}", "\n\n", text2).strip() + "\n"

    if text2 != text:
        md.write_text(text2, encoding="utf-8")
        return True
    return False

def main():
    if not SERIES_DIR.exists():
        raise SystemExit(f"No existe {SERIES_DIR}")

    changed = 0
    scanned = 0
    for md in SERIES_DIR.rglob("*.md"):
        if md.name.lower() in ("index.md", ".pages"):
            continue
        scanned += 1
        if upgrade_file(md):
            changed += 1

    print(f"✅ Escaneados: {scanned}")
    print(f"✅ Modificados: {changed}")

if __name__ == "__main__":
    main()
