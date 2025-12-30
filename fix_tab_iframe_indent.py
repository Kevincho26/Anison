from pathlib import Path
import re

SERIES_DIR = Path("docs/series")

tab_header = re.compile(r'^===\s+"', re.M)

def fix_file(p: Path) -> bool:
    lines = p.read_text(encoding="utf-8").splitlines()
    out = []
    in_tab = False

    for i, line in enumerate(lines):
        if line.startswith('=== "'):
            in_tab = True
            out.append(line)
            continue

        # si empieza otra sección sin indent, ya no estamos en el contenido de tab
        if in_tab and line and not line.startswith("    "):
            # OJO: esto solo se activa cuando sales del bloque por falta de indent
            # pero no apaga tabs para el resto del archivo (pueden venir más tabs)
            pass

        # Arregla </iframe> fuera de indent dentro de tabs
        if in_tab and line.strip() == "</iframe>" and not line.startswith("    "):
            out.append("    </iframe>")
        else:
            out.append(line)

    new_text = "\n".join(out).rstrip() + "\n"
    old_text = "\n".join(lines).rstrip() + "\n"
    if new_text != old_text:
        p.write_text(new_text, encoding="utf-8")
        return True
    return False

changed = 0
for md in SERIES_DIR.rglob("*.md"):
    if md.name.lower() in ("index.md", ".pages"):
        continue
    if fix_file(md):
        changed += 1

print("✅ Archivos corregidos:", changed)
