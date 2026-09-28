#!/usr/bin/env python3
"""
extraer-lista-oscp.py — Extrae los nombres de maquina de la pestana
"PWK V3 (PEN 200 Latest Version)" del listado de TJ Null.

Salida: JSON con las secciones HTB y PG, normalizado a slugs comparables
contra las URLs de los writeups.

Uso:
    python3 extraer-lista-oscp.py wb.xlsx > lista-oscp.json
"""
import json
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"


def colnum(ref):
    m = re.match(r"([A-Z]+)", ref)
    n = 0
    for ch in m.group(1):
        n = n * 26 + ord(ch) - 64
    return n


def load_sheet(zf, path, shared):
    root = ET.fromstring(zf.read(path))
    out = []
    for row in root.iter(NS + "row"):
        cells = {}
        for c in row.findall(NS + "c"):
            ty = c.get("t")
            v = c.find(NS + "v")
            isn = c.find(NS + "is")
            val = ""
            if ty == "s" and v is not None:
                val = shared[int(v.text)]
            elif ty == "inlineStr" and isn is not None:
                val = "".join(x.text or "" for x in isn.iter(NS + "t"))
            elif v is not None:
                val = v.text or ""
            if val and val.strip():
                cells[colnum(c.get("r"))] = val.strip()
        if cells:
            out.append((int(row.get("r")), cells))
    return out


def clean_name(raw):
    """Limpia anotaciones entre corchetes/parentesis y espacios."""
    n = re.sub(r"\[[^\]]*\]", "", raw)
    n = re.sub(r"\([^)]*\)", "", n)
    n = re.sub(r"\s+", " ", n).strip()
    return n


def slug(name):
    """Normaliza a slug comparable con las URLs de 0xdf."""
    s = name.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "", s)
    return s


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "wb.xlsx"
    with zipfile.ZipFile(path) as zf:
        shared = []
        if "xl/sharedStrings.xml" in zf.namelist():
            for si in ET.fromstring(zf.read("xl/sharedStrings.xml")).findall(NS + "si"):
                shared.append("".join(x.text or "" for x in si.iter(NS + "t")))

        # sheet1.xml = PWK V3 (verificado contra xl/workbook.xml)
        rows = load_sheet(zf, "xl/worksheets/sheet1.xml", shared)

    result = {"htb": {}, "pg_practice": {}, "pg_play": {}, "vulnlab": {}}
    section = None
    headers = {}

    # Limites de seccion por numero de fila (verificados)
    for rn, cells in rows:
        c1 = cells.get(1, "")

        # Encabezados de plataforma
        if rn == 5 and "hackthebox" in c1.lower():
            section = "htb"
            continue
        if rn == 41 and "proving grounds practice" in c1.lower():
            section = "pg_practice"
            headers = {}
            continue
        if rn == 84 and "proving grounds play" in c1.lower():
            section = "pg_play"
            headers = {}
            continue
        if rn == 117 and "vulnlab" in c1.lower():
            section = "vulnlab"
            headers = {}
            continue
        if rn == 136 and "other labs" in c1.lower():
            section = None
            continue

        # Fila de titulos de columna
        if section and rn in (6, 42, 85, 118):
            for col, txt in cells.items():
                headers[col] = clean_name(txt).lower()
            continue

        if not section:
            continue

        for col, txt in cells.items():
            if col in (2, 3) and rn in (1, 2, 3, 5):
                continue
            cat = headers.get(col, f"col{col}")
            if "post oscp" in cat:
                continue  # fuera del temario del examen
            if "prolab" in cat:
                continue  # labs largos, no maquinas sueltas
            name = clean_name(txt)
            if not name or len(name) < 2:
                continue
            if name.lower() in ("linux boxes", "windows boxes", "windows active ad",
                                "windows active directory boxes", "linux", "windows"):
                continue
            if "http" in name.lower():
                continue
            sl = slug(name)
            if not sl:
                continue
            result[section].setdefault(sl, name)

    out = {
        "fuente": "TJ Null / NetSec Focus - pestana PWK V3 (PEN 200 Latest Version)",
        "actualizado_hoja": "2026-07-18",
        "secciones": {k: [{"slug": s, "nombre": v} for s, v in sorted(d.items())]
                      for k, d in result.items()},
    }
    out["totales"] = {k: len(v) for k, v in out["secciones"].items()}
    json.dump(out, sys.stdout, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
