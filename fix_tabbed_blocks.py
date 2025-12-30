from pathlib import Path
import re

SERIES_DIR = Path("docs/series")
TAB_HDR = re.compile(r'^(===\s+"[^"]+"\s*)$')

def fix_file(path: Path) -> bool:
    lines = path.read_text(encoding="utf-8").splitlines()
    out = []
    in_tabs = False
    changed = False

    for i, line in enumerate(lines):
        if TAB_HDR.match(line):
            in_tabs = True
            out.append(line)
            continue

        if in_tabs:
            # si empieza otro tab header, lo detectará arriba en la siguiente iteración
            # aquí forzamos indentación 4 espacios en TODO el contenido
            if line.startswith("    ") or line.strip() == "":
                # incluso las vacías: las dejamos como "    " para que sigan dentro del tab
                out.append("    " if line.strip() == "" else line)
            else:
                out.append("    " + line)
                changed = True
        else:
            out.append(line)

    new_text = "\n".join(out).rstrip() + "\n"
    old_text = "\n".join(lines).rstrip() + "\n"
    if new_text != old_text:
        path.write_text(new_text, encoding="utf-8")
        return True
    return False

def main():
    changed_files = 0
    scanned = 0
    for md in SERIES_DIR.rglob("*.md"):
        if md.name.lower() in ("index.md", ".pages"):
            continue
        scanned += 1
        if fix_file(md):
            changed_files += 1

    print(f"Escaneados: {scanned}")
    print(f"Modificados: {changed_files}")

if __name__ == "__main__":
    main()
