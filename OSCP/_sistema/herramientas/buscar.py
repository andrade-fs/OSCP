#!/usr/bin/env python3
"""
buscar.py — Busca una palabra clave o tecnica en todo el corpus y muestra
TODAS las referencias, agrupadas por maquina.

Es la herramienta central: la pregunta tipica no es "que maquina es esta" sino
"donde se uso PrintSpoofer" o "que maquinas involucran Kerberoasting".

Uso:
    python3 buscar.py kerberoasting                 # resumen: cuantas y cuales
    python3 buscar.py kerberoasting -v              # + contexto de cada match
    python3 buscar.py kerberoasting -vv             # + mas contexto
    python3 buscar.py "seimpersonate" --oscp        # solo de la lista OSCP
    python3 buscar.py "GodPotato|JuicyPotato"       # regex
    python3 buscar.py --listar-tecnicas             # que tecnicas conoce
    python3 buscar.py --nombres                     # solo nombres de maquina

Opciones:
    -v / -vv        nivel de contexto (0/6/12 lineas)
    --oscp          filtrar a maquinas del listado OSCP (TJ Null PWK V3)
    --os LINUX      filtrar por sistema operativo
    --dificil X     filtrar por dificultad (Easy/Medium/Hard)
    --limite N      maximo de maquinas a mostrar
    --case          busqueda sensible a mayusculas
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from corpus_comun import leer_frontmatter, hay_match_util  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CORPUS = os.path.join(ROOT, "vault", "corpus")
TECNICAS = os.path.join(ROOT, "_sistema", "datos", "tecnicas.txt")




def cargar_corpus(solo_oscp=False, osfiltro="", dif=""):
    docs = []
    for base in ("htb", "otros"):
        d = os.path.join(CORPUS, base)
        if not os.path.isdir(d):
            continue
        for name in sorted(os.listdir(d)):
            if not name.endswith(".md"):
                continue
            p = os.path.join(d, name)
            meta = leer_frontmatter(p)
            if solo_oscp and meta.get("en_lista_oscp") != "true":
                continue
            if osfiltro and osfiltro.lower() not in meta.get("os", "").lower():
                continue
            if dif and dif.lower() not in meta.get("dificultad", "").lower():
                continue
            docs.append((p, meta))
    return docs


def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("patron", nargs="?", default="")
    ap.add_argument("-v", action="count", default=0)
    ap.add_argument("--oscp", action="store_true")
    ap.add_argument("--os", dest="osf", default="")
    ap.add_argument("--dificil", dest="dif", default="")
    ap.add_argument("--limite", type=int, default=0)
    ap.add_argument("--case", action="store_true")
    ap.add_argument("--con-urls", action="store_true",
                    help="incluir matches dentro de URLs (ruido de plantilla)")
    ap.add_argument("--nombres", action="store_true")
    ap.add_argument("--listar-tecnicas", action="store_true")
    args = ap.parse_args()

    if args.listar_tecnicas:
        if os.path.exists(TECNICAS):
            for line in open(TECNICAS, encoding="utf-8"):
                line = line.strip()
                if line and not line.startswith("#"):
                    print(" ", line)
        else:
            print("(falta _sistema/datos/tecnicas.txt)", file=sys.stderr)
        return

    if not args.patron:
        ap.print_help()
        return

    flags = 0 if args.case else re.IGNORECASE
    try:
        rx = re.compile(args.patron, flags)
    except re.error as e:
        print(f"regex invalida: {e}", file=sys.stderr)
        return
    # Patron literal -> tambien buscamos la forma sin espacios, util para
    # "pass the hash" vs "passthehash"
    rx2 = None
    if " " in args.patron and not any(c in args.patron for c in "|()[]\\"):
        rx2 = re.compile(args.patron.replace(" ", r"[\s_-]*"), flags)

    docs = cargar_corpus(args.oscp, args.osf, args.dif)
    if not docs:
        print("corpus vacio. Corre raspar.py primero.", file=sys.stderr)
        return

    ctx = {0: 0, 1: 6, 2: 12}.get(args.v, 12)

    total_maquinas = 0
    total_matches = 0
    resultados = []

    for path, meta in docs:
        try:
            lines = open(path, encoding="utf-8", errors="replace").read().split("\n")
        except OSError:
            continue
        hits = []
        for i, line in enumerate(lines):
            if not (rx.search(line) or (rx2 and rx2.search(line))):
                continue
            if not args.con_urls:
                # Saltear ruido de plantilla: "gitlab" esta en cada link.
                util = hay_match_util(line, rx)
                if not util and rx2 is not None:
                    util = hay_match_util(line, rx2)
                if not util:
                    continue
            hits.append(i)
        if not hits:
            continue

        total_maquinas += 1
        total_matches += len(hits)
        resultados.append((path, meta, lines, hits))

    if args.limite:
        resultados = resultados[: args.limite]

    etiqueta = meta_txt = ""
    filtros = []
    if args.oscp:
        filtros.append("lista OSCP")
    if args.osf:
        filtros.append(f"OS={args.osf}")
    if args.dif:
        filtros.append(f"dif={args.dif}")
    if filtros:
        meta_txt = " [" + ", ".join(filtros) + "]"

    print(f"\n  '{args.patron}'{meta_txt}")
    print(f"  {total_matches} referencias en {total_maquinas} maquinas"
          f" (de {len(docs)} en el corpus)\n")

    if args.nombres:
        for path, meta, _, hits in resultados:
            n = meta.get("maquina") or os.path.basename(path)[:-3]
            marca = " *" if meta.get("en_lista_oscp") == "true" else ""
            print(f"  {n}{marca} ({len(hits)})")
        print("\n  * = en el listado OSCP (TJ Null PWK V3)")
        return

    for path, meta, lines, hits in resultados:
        nombre = meta.get("maquina") or os.path.basename(path)[:-3]
        dif = meta.get("dificultad", "")
        so = meta.get("os", "")
        oscp = " [OSCP]" if meta.get("en_lista_oscp") == "true" else ""
        cab = " · ".join(x for x in (so, dif) if x)
        print("─" * 78)
        print(f"  {nombre}{oscp}" + (f"   ({cab})" if cab else ""))
        print(f"  {os.path.relpath(path, ROOT)}")
        print("─" * 78)

        if ctx == 0:
            for i in hits:
                print(f"    {i+1}: {lines[i].strip()[:150]}")
        else:
            mostrados = []
            for i in hits:
                lo = max(0, i - ctx)
                hi = min(len(lines), i + ctx + 1)
                # evitar solapamiento entre bloques
                if mostrados and lo <= mostrados[-1][1]:
                    mostrados[-1] = (mostrados[-1][0], max(mostrados[-1][1], hi))
                else:
                    mostrados.append((lo, hi))
            for lo, hi in mostrados:
                print()
                for j in range(lo, hi):
                    mark = ">>" if j in hits else "  "
                    print(f"  {mark} {j+1:5d} │ {lines[j]}")
        print()

    print(f"  total: {total_matches} referencias en {total_maquinas} maquinas\n")


if __name__ == "__main__":
    main()
