#!/usr/bin/env python3
"""
corpus_comun.py — Utilidades compartidas por buscar.py e indice.py.

El problema que resuelve:

  El conversor reescribe los links relativos a URLs absolutas, asi que CADA
  archivo contiene "0xdf.gitlab.io" en decenas de lugares. Contando texto a lo
  bruto, "gitlab" daba 566/566 archivos y "x11" daba 168: ruido de plantilla, no
  contenido.

  Solucion: calcular los tramos de cada linea que son URLs (destino de un link
  markdown, o URL suelta) y saltear los matches que caen adentro.
"""

import os
import re

# Destino de un link markdown: ]( ... )
RX_LINK = re.compile(r"\]\(([^)]*)\)")
# URL suelta o en campo de frontmatter
RX_URL = re.compile(r"https?://\S+")
RX_FRONT = re.compile(r"^---\n.*?\n---\n", re.S)

# Nombres de archivo de imagen: tambien son ruido
RX_IMAGEN = re.compile(r"!\[[^\]]*\]\([^)]*\)")


def tramos_url(linea):
    """Devuelve [(ini, fin)] de los tramos de la linea que son URL."""
    tramos = []
    for rx in (RX_LINK, RX_URL, RX_IMAGEN):
        for m in rx.finditer(linea):
            # para RX_LINK nos interesa solo el destino, no el texto del link
            if rx is RX_LINK:
                tramos.append((m.start(1), m.end(1)))
            else:
                tramos.append((m.start(), m.end()))
    return tramos


def en_url(pos, tramos):
    return any(a <= pos < b for a, b in tramos)


def quitar_frontmatter(texto):
    return RX_FRONT.sub("", texto, count=1)


def limpiar_para_contar(texto):
    """Version del texto sin URLs, para contar ocurrencias sin ruido."""
    t = quitar_frontmatter(texto)
    t = RX_IMAGEN.sub(" ", t)
    t = RX_LINK.sub("] ", t)
    t = RX_URL.sub(" ", t)
    return t


def hay_match_util(linea, rx):
    """¿Hay al menos un match de rx que NO caiga dentro de una URL?"""
    tramos = tramos_url(linea)
    for m in rx.finditer(linea):
        if not en_url(m.start(), tramos):
            return True
    return False


def leer_frontmatter(path):
    """Lee el frontmatter YAML simple que escribimos nosotros."""
    meta = {}
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            if f.readline().strip() != "---":
                return meta
            for line in f:
                if line.strip() == "---":
                    break
                if ":" in line:
                    k, _, v = line.partition(":")
                    v = v.strip()
                    if v.startswith('"') and v.endswith('"'):
                        v = v[1:-1]
                    meta[k.strip()] = v
    except OSError:
        pass
    return meta


def listar_corpus(raiz):
    """Devuelve [(path, nombre_archivo)] de todo el corpus."""
    salida = []
    for base in ("htb", "otros"):
        d = os.path.join(raiz, "vault", "corpus", base)
        if not os.path.isdir(d):
            continue
        for name in sorted(os.listdir(d)):
            if name.endswith(".md"):
                salida.append((os.path.join(d, name), name))
    return salida
