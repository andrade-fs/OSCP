#!/usr/bin/env python3
"""
raspar.py — Descarga los writeups de 0xdf y los convierte a markdown buscable.

Estrategia:
  * Usa el sitemap.xml oficial del sitio (la via que el autor publica para crawlers).
  * Rate-limited: por defecto 1 request cada 1.5 s. No lo bajemos, es el blog de
    una persona.
  * Reanudable: si el .md ya existe y esta completo, lo saltea.
  * Marca en el frontmatter si la maquina esta en el listado OSCP (TJ Null PWK V3).

Uso:
    python3 raspar.py --listar                 # que va a bajar, sin bajar
    python3 raspar.py                          # raspar todo
    python3 raspar.py --solo-htb               # solo maquinas HTB
    python3 raspar.py --limite 20              # prueba con 20
    python3 raspar.py --delay 1.5
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from html2md import convert, frontmatter, extract_metadata  # noqa: E402

SITE = "https://0xdf.gitlab.io"
SITEMAP = SITE + "/sitemap.xml"
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CORPUS = os.path.join(ROOT, "vault", "corpus")


def fetch(url, tries=3, timeout=30):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": UA,
                "Accept": "text/html,application/xhtml+xml",
                "Accept-Language": "en-US,en;q=0.9",
            })
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode("utf-8", errors="replace")
        except Exception as e:                      # noqa: BLE001
            last = e
            if i < tries - 1:
                time.sleep(2 * (i + 1))
    raise last


def sitemap_urls():
    xml = fetch(SITEMAP)
    urls = re.findall(r"<loc>([^<]+)</loc>", xml)
    # Descartar la portada y cualquier URL sin slug real: no son articulos.
    return [u for u in urls
            if u.rstrip("/") != SITE
            and u.rstrip("/").rsplit("/", 1)[-1].replace(".html", "") not in ("", "index")]


def classify(url):
    """Devuelve (tipo, slug, carpeta)."""
    slug = url.rstrip("/").rsplit("/", 1)[-1].replace(".html", "")

    # Las chuletas NO son writeups de maquina. "htb-interactive" empieza con
    # htb- pero es /cheatsheets/: una tabla JS, sin writeup real.
    if "/cheatsheets/" in url:
        return "chuleta", slug, "otros"

    # Un writeup de maquina vive en /YYYY/MM/DD/. Sin fecha no es un writeup.
    if slug.startswith("htb-") and re.search(r"/\d{4}/\d{2}/\d{2}/", url):
        # Mismo nombre de maquina puede tener mas de un writeup: nos quedamos
        # con el mas reciente (la URL trae la fecha), asi que deduplicamos aparte.
        return "htb", slug, "htb"

    return "otro", slug, "otros"


def normalize_machine(slug):
    """htb-blackfield -> blackfield. Para cruzar contra el listado OSCP."""
    return re.sub(r"^htb-", "", slug).lower()


def load_oscp_list():
    """Devuelve {seccion: {slug: nombre}}.

    OJO: hay que mantener las secciones SEPARADAS. Un nombre de PG Practice
    ("Access") colisiona con un HTB del mismo nombre, y cruzar todo junto
    produce falsos positivos.
    """
    p = os.path.join(ROOT, "_sistema", "datos", "lista-oscp.json")
    if not os.path.exists(p):
        return {}
    d = json.load(open(p, encoding="utf-8"))
    return {sec: {it["slug"]: it["nombre"] for it in items}
            for sec, items in d.get("secciones", {}).items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--listar", action="store_true", help="solo listar, sin bajar")
    ap.add_argument("--solo-htb", action="store_true")
    ap.add_argument("--limite", type=int, default=0)
    ap.add_argument("--delay", type=float, default=1.5)
    ap.add_argument("--forzar", action="store_true", help="re-bajar aunque exista")
    ap.add_argument("--workers", type=int, default=1,
                    help="descargas concurrentes (default 1; el delay se aplica por worker)")
    args = ap.parse_args()

    print("leyendo sitemap...", file=sys.stderr)
    urls = sitemap_urls()
    print(f"  {len(urls)} URLs en el sitemap", file=sys.stderr)

    # Ordenar y deduplicar: quedarse con la URL mas reciente por slug
    entries = {}
    for u in urls:
        tipo, slug, carpeta = classify(u)
        if args.solo_htb and tipo != "htb":
            continue
        prev = entries.get(slug)
        if prev is None or u > prev[0]:
            entries[slug] = (u, tipo, carpeta)

    items = sorted(entries.values(), key=lambda x: x[0])
    if args.limite:
        items = items[: args.limite]

    oscp = load_oscp_list()

    if args.listar:
        for u, tipo, carpeta in items:
            m = normalize_machine(u.rstrip("/").rsplit("/", 1)[-1].replace(".html", ""))
            sec = next((k for k, v in oscp.items() if m in v), "")
            flag = f" [OSCP:{sec}]" if sec else ""
            print(f"{tipo:5s} {u}{flag}")
        print(f"\ntotal: {len(items)}", file=sys.stderr)
        return

    os.makedirs(os.path.join(CORPUS, "htb"), exist_ok=True)
    os.makedirs(os.path.join(CORPUS, "otros"), exist_ok=True)

    ok = skip = fail = 0
    fallos = []
    pendientes = []
    for u, tipo, carpeta in items:
        slug = u.rstrip("/").rsplit("/", 1)[-1].replace(".html", "")
        out = os.path.join(CORPUS, carpeta, slug + ".md")
        if os.path.exists(out) and os.path.getsize(out) > 500 and not args.forzar:
            skip += 1
            continue
        pendientes.append((u, tipo, carpeta, slug, out))

    print(f"  a bajar: {len(pendientes)}  ya estaban: {skip}", file=sys.stderr)

    def trabajar(job):
        u, tipo, carpeta, slug, out = job
        html = fetch(u)
        meta, body = convert(html, u)
        meta["tipo"] = tipo
        m = normalize_machine(slug)
        # Cruzar contra la seccion que le corresponde a ESTE tipo de objetivo
        sec = next((k for k, v in oscp.items() if m in v), "")
        meta["en_lista_oscp"] = bool(sec)
        meta["oscp_seccion"] = sec
        doc = frontmatter(meta) + "\n\n" + body + "\n"
        with open(out, "w", encoding="utf-8") as f:
            f.write(doc)
        return u

    def con_delay(job):
        try:
            r = trabajar(job)
            return ("ok", r, None)
        except Exception as e:                       # noqa: BLE001
            return ("fail", job[0], repr(e))
        finally:
            time.sleep(args.delay)

    total = len(pendientes)
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = [ex.submit(con_delay, j) for j in pendientes]
        for i, fut in enumerate(as_completed(futs), 1):
            estado, quien, err = fut.result()
            if estado == "ok":
                ok += 1
            else:
                fail += 1
                fallos.append((quien, err))
                print(f"  FALLO {quien}: {err}", file=sys.stderr)
            if i % 25 == 0 or i == total:
                print(f"  [{i}/{total}] ok={ok} fail={fail}", file=sys.stderr)

    print(f"\nRESUMEN: ok={ok} salteados={skip} fallos={fail}", file=sys.stderr)
    if fallos:
        p = os.path.join(CORPUS, "_fallos.txt")
        with open(p, "w", encoding="utf-8") as f:
            for u, e in fallos:
                f.write(f"{u}\t{e}\n")
        print(f"  fallos en {p}", file=sys.stderr)


if __name__ == "__main__":
    main()
