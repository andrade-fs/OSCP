#!/usr/bin/env python3
"""
marcar-oscp.py — Recalcula el campo `en_lista_oscp` del corpus.

Regla (y por que):

  Un writeup HTB queda marcado como parte del listado OSCP si su nombre aparece en
  la seccion `htb` de la lista, **o** en la seccion `vulnlab`.

  Lo segundo es a proposito: Vulnlab se migro a HackTheBox en 2025, asi que una
  maquina como `sendai` o `bamboo` es la MISMA maquina que figura en la lista bajo
  "Vulnlab". Se guarda la seccion de origen en `oscp_seccion` para poder auditarlo.

  Lo que NO se marca: un nombre HTB que solo coincide con una maquina de
  Proving Grounds Practice/Play. `nibbles`, `craft`, `vault`, `zipper`, `pc` y `sea`
  existen en PG Practice pero son maquinas DISTINTAS de las de HTB con igual nombre.
  Marcarlas inflaria la lista de prioridades y te haria estudiar la maquina
  equivocada.

Uso:
    python3 marcar-oscp.py --dry-run
    python3 marcar-oscp.py
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CORPUS = os.path.join(ROOT, "vault", "corpus")
LISTA = os.path.join(ROOT, "_sistema", "datos", "lista-oscp.json")

# Solo estas secciones pueden legitimamente coincidir con un writeup de HTB.
SECCIONES_VALIDAS_HTB = ("htb", "vulnlab")


def cargar_lista():
    d = json.load(open(LISTA, encoding="utf-8"))
    return {k: {m["slug"]: m["nombre"] for m in v}
            for k, v in d.get("secciones", {}).items()}


def seccion_de(slug, tipo, secs):
    """Devuelve la seccion del listado a la que pertenece, o ''."""
    if tipo == "otro":
        return ""
    for sec in SECCIONES_VALIDAS_HTB:
        if slug in secs.get(sec, {}):
            return sec
    return ""


def main():
    dry = "--dry-run" in sys.argv
    secs = cargar_lista()

    cambios = 0
    stats = {}
    falsos = []

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

            slug_raw = name[:-3]
            tipo = "htb" if slug_raw.startswith("htb-") else "otro"
            slug = re.sub(r"^htb-", "", slug_raw).lower()

            sec = seccion_de(slug, tipo, secs)
            # Detectar coincidencia SOLO en PG: es un falso positivo conocido
            if tipo == "htb" and not sec:
                for s in ("pg_practice", "pg_play"):
                    if slug in secs.get(s, {}):
                        falsos.append((slug, s))
                        break

            nuevo_flag = "true" if sec else "false"
            actual = re.search(r"^en_lista_oscp:\s*(\S+)", fm, re.M)
            actual_val = actual.group(1) if actual else ""
            actual_sec = re.search(r'^oscp_seccion:\s*"([^"]*)"', fm, re.M)
            actual_sec_val = actual_sec.group(1) if actual_sec else ""

            if actual_val == nuevo_flag and actual_sec_val == sec:
                stats[sec or "(ninguna)"] = stats.get(sec or "(ninguna)", 0) + 1
                continue

            fm2 = re.sub(r"^en_lista_oscp:\s*\S+", f"en_lista_oscp: {nuevo_flag}", fm, flags=re.M)
            if actual_sec:
                fm2 = re.sub(r'^oscp_seccion:\s*"[^"]*"', f'oscp_seccion: "{sec}"', fm2, flags=re.M)
            else:
                fm2 += f'\noscp_seccion: "{sec}"'

            if not dry:
                open(p, "w", encoding="utf-8").write(txt[: m.start(1)] + fm2 + txt[m.end(1):])
            cambios += 1
            stats[sec or "(ninguna)"] = stats.get(sec or "(ninguna)", 0) + 1

    modo = " (dry-run)" if dry else ""
    print(f"archivos actualizados: {cambios}{modo}")
    for k in sorted(stats):
        print(f"  {k:12s} {stats[k]}")
    if falsos:
        print(f"\ncoincidencias descartadas con PG (maquinas distintas, mismo nombre): "
              f"{len(falsos)}")
        for s, sec in sorted(falsos):
            print(f"    {s:12s} (existe en {sec})")


if __name__ == "__main__":
    main()
