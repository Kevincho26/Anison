from pathlib import Path

LETTERS = ["0-9","A","B","C","D","E","F","G","H","J","K","L","M","N","O","P","R","S","T","U","V","W"]

docs = Path("docs")
series = docs / "series"

for letter in LETTERS:
    folder = series / letter
    folder.mkdir(parents=True, exist_ok=True)

    anchor = f"az-{letter.lower()}"       # az-a, az-b, az-0-9
    target = f"../#{anchor}"              # desde /series/A/ -> /series/#az-a

    content = f"""---
hide:
  - toc
---

<meta http-equiv="refresh" content="0; url={target}">
<p>Redirigiendo al catálogo… <a href="{target}">Abrir {letter}</a></p>
"""

    (folder / "index.md").write_text(content, encoding="utf-8")

print("✅ Redirects creados/actualizados para índices por letra.")
