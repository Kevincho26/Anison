#!/usr/bin/env python3
from __future__ import annotations

import zipfile, shutil
from pathlib import Path
from PIL import Image, ImageOps, ImageFilter

IN_ZIP = Path("heroes_raw.zip")                 # tu zip con imágenes
OUT_DIR = Path("docs/assets/heroes")            # destino en tu sitio
TARGET_W, TARGET_H = 1920, 1080                 # 16:9 real

def make_hero_fit_pad(img_path: Path, out_path: Path):
    im = Image.open(img_path)
    im = ImageOps.exif_transpose(im).convert("RGB")

    # Fondo: blur de la misma imagen para “rellenar” bonito
    bg = im.copy()
    bg = bg.resize((TARGET_W, TARGET_H), Image.Resampling.LANCZOS)
    bg = bg.filter(ImageFilter.GaussianBlur(radius=18))

    # Imagen principal: encaja SIN recortar
    im_fit = ImageOps.contain(im, (TARGET_W, TARGET_H), Image.Resampling.LANCZOS)

    # Pegar centrado sobre el fondo
    x = (TARGET_W - im_fit.size[0]) // 2
    y = (TARGET_H - im_fit.size[1]) // 2
    bg.paste(im_fit, (x, y))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    bg.save(out_path, "JPEG", quality=88, optimize=True, progressive=True)

def main():
    if not IN_ZIP.exists():
        raise SystemExit(f"No encuentro {IN_ZIP}. Pon el zip en la raíz del repo o cambia IN_ZIP.")

    tmp = Path("_heroes_tmp_extract")
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(IN_ZIP, "r") as z:
        z.extractall(tmp)

    imgs = [p for p in tmp.rglob("*") if p.suffix.lower() in (".jpg",".jpeg",".png",".webp")]
    if not imgs:
        raise SystemExit("No encontré imágenes en el zip.")

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for p in imgs:
        # Respeta el nombre del archivo (para que heroes_report.csv siga funcionando)
        out_name = p.stem + ".jpg"
        make_hero_fit_pad(p, OUT_DIR / out_name)

    shutil.rmtree(tmp)
    print(f"✅ Heroes regenerados en: {OUT_DIR} (fit+pad, sin recorte)")

if __name__ == "__main__":
    main()
