#!/usr/bin/env python3
"""
arreglar-frontmatter.py — Backfill de los campos tipo / en_lista_oscp /
oscp_seccion en archivos ya descargados, sin volver a bajarlos.

Necesario porque la primera version de frontmatter() no los emitia.

Uso:
    python3 arreglar-frontmatter.py            # arreglar
    python3 arreglar-frontmatter.py --dry-run  # solo contar
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CORPUS = os.path.join(ROOT, "vault", "corpus")
LISTA = os.path.join(ROOT, "_sistema", "datos", "lista-oscp.json")

sec2slugs = {}
if os.path.exists(LISTA):
    d = json.load(open(LISTA, encoding="utf-8"))
    sec2slugs = {k: {m["slug"] for m in v} for k, v in d.get("secciones", {}).items()}


def main():
    dry = "--dry-run" in sys.argv
    arreglados = ok = 0
    for base in ("htb", "otros"):
        d = os.path.join(CORPUS, base)
        if not os.path.isdir(d):
            continue
        for name in sorted(os.listdir(d)):
            if not name.endswith(".md"):
                continue
            p = os.path.join(d, name)
            txt = open(p, encoding="utf-8", errors="replace").read()
            m = re.match(r"^---\n(.*?)\n---\n", txt, re.S)
            if not m:
                continue
            fm = m.group(1)
            if "en_lista_oscp:" in fm:
                ok += 1
                continue

            slug = name[:-3]
            maq = re.sub(r"^htb-", "", slug).lower()
            tipo = "htb" if slug.startswith("htb-") else "otro"
            sec = next((k for k, v in sec2slugs.items() if maq in v), "")

            extra = (f'\ntipo: "{tipo}"\nen_lista_oscp: '
                     f'{"true" if sec else "false"}\noscp_seccion: "{sec}"')
            nuevo = txt[: m.end(1)] + extra + txt[m.end(1):]
            if not dry:
                open(p, "w", encoding="utf-8").write(nuevo)
            arreglados += 1

    print(f"arreglados: {arreglados}   ya estaban bien: {ok}", file=sys.stderr)
    if dry:
        print("(dry-run: no se escribio nada)", file=sys.stderr)


if __name__ == "__main__":
    main()
