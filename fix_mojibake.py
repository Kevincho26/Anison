from pathlib import Path

docs = Path("docs")
fixed_count = 0

for p in docs.rglob("*.md"):
    txt = p.read_text(encoding="utf-8")
    if "Ã" in txt or "Â" in txt:
        try:
            fixed = txt.encode("latin1").decode("utf-8")
        except UnicodeError:
            continue
        p.write_text(fixed, encoding="utf-8")
        print("fixed:", p)
        fixed_count += 1

print("Done. Files fixed:", fixed_count)
