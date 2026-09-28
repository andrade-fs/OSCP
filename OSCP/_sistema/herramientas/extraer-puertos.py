#!/usr/bin/env python3
"""
extraer-puertos.py — Extrae la relacion maquina -> puertos desde el corpus.

Por que existe:

  Buscar "5000" a texto plano devuelve ruido (IPs, --min-rate 10000, hashes).
  Durante el examen lo que se necesita es lo contrario: dado un puerto abierto,
  que maquinas lo tenian, que era REALMENTE, y donde se exploto.

Que extrae por maquina:

  1. Las lineas de la tabla de nmap: puerto, protocolo, estado y etiqueta.
  2. Los encabezados de seccion que nombran un puerto. Esto es la clave: 0xdf
     titula "### Let's Chat - TCP 5000" o "### HTTP - TCP 5000", o sea que el
     encabezado dice QUE ERA, no lo que nmap adivino. nmap etiqueta el 5000 como
     "upnp" casi siempre, y casi nunca lo es.

Salida: JSON con la estructura completa, para que otros scripts armen el vault.

Uso:
    python3 extraer-puertos.py > puertos.json
    python3 extraer-puertos.py --puerto 5000     # inspeccionar uno solo
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CORPUS = os.path.join(ROOT, "vault", "corpus")

# 5000/tcp  open  upnp        |  5000/tcp filtered upnp
RX_PUERTO = re.compile(
    r"^(\d{1,5})/(tcp|udp)\s+(open\|filtered|open|filtered|closed)\s*(\S*)\s*(.*)$"
)
# ### HTTP - TCP 5000   |   #### 5000 - something
# Acepta "### HTTP - TCP 5000" y "### HTTP - Port 5000" (ambas formas existen)
# El grupo de puertos puede traer VARIOS: "SMB - TCP 139/445" o "TCP 445 / 139".
# Con (\d{1,5}) solo se capturaba el primero y el resto se perdia.
RX_H_TCP = re.compile(r"^#{2,5}\s+(.*?)\b(?:TCP|Port)\s+([0-9]{1,5}(?:\s*[/,y]\s*[0-9]{1,5})*)\b", re.I)
RX_H_NUM = re.compile(r"^#{2,5}\s+(\d{1,5})\s*[-–—:]\s*(.+)$")
RX_HEAD = re.compile(r"^(#{2,5})\s+(.+)$")

# "finds three open TCP ports, SSH (22) and two HTTP (5000 and 8000)"
RX_INTRO = re.compile(r"finds?\s+.*?TCP ports?,\s*(.+?):", re.I)

# Puertos efimeros de RPC de Windows: ruido, no son superficie de ataque.
EFIMEROS = re.compile(r"^49[0-9]{3}$")

# Encabezados de reconocimiento. Una mencion del puerto debajo de uno de estos
# NO dice nada del servicio: es la salida cruda del nmap. Inferir de ahi daba
# "real=nmap", que es peor que dejarlo vacio porque engania.
RX_RECON = re.compile(
    r"^(nmap|recon|initial|scan|scanning|enumeration|footprint|discovery|"
    r"port\s*scan|service\s*scan|host\s*info)", re.I)


def leer_frontmatter(path):
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


def analizar(path):
    meta = leer_frontmatter(path)
    txt = open(path, encoding="utf-8", errors="replace").read()
    lineas = txt.split("\n")

    puertos = {}     # num -> {proto, estado, etiqueta}
    secciones = {}   # num -> titulo de la seccion que lo nombra
    intro = ""

    for i, ln in enumerate(lineas):
        s = ln.rstrip()

        # --- tabla de nmap ---
        m = RX_PUERTO.match(s)
        if m:
            num, proto, estado, etiqueta = m.group(1), m.group(2), m.group(3), m.group(4)
            if int(num) < 1024 or not EFIMEROS.match(num):
                puertos.setdefault(num, {
                    "proto": proto,
                    "estado": estado,
                    "etiqueta": etiqueta.strip("?"),
                    "linea": i + 1,
                })
            continue

        # --- encabezado que nombra un puerto ---
        m = RX_H_TCP.match(s)
        if m:
            nombre = m.group(1).strip(" -–—:").strip()
            # Puede nombrar varios puertos: asignar el nombre a cada uno.
            for num in re.findall(r"[0-9]{1,5}", m.group(2)):
                secciones.setdefault(num, nombre)
            continue
        m = RX_H_NUM.match(s)
        if m:
            num = m.group(1)
            secciones.setdefault(num, m.group(2).strip(" -–—:").strip())
            continue

        # --- linea de intro del recon ---
        if not intro:
            m = RX_INTRO.search(s)
            if m:
                intro = m.group(1).strip()

    # --- Sin inferencias, a proposito ---
    #
    # Se probo un respaldo que, cuando ningun encabezado nombra el puerto,
    # tomaba el encabezado mas cercano a cualquier mencion. Subia la cobertura
    # de 46% a 99%, pero la mitad era basura: "Network", "More UDP",
    # "Tech Stack", "Directory Brute Force", y hasta IPs como "172.16.20.1".
    #
    # Para una referencia de examen la fiabilidad gana: un dato inventado te
    # hace perder tiempo buscando algo que no existe. Un guion significa
    # honestamente "este writeup no tiene seccion dedicada a ese puerto".
    # La maquina sigue enlazada, que es el camino de entrada util.

    return {
        "archivo": os.path.basename(path)[:-3],
        "maquina": meta.get("maquina", ""),
        "os": meta.get("os", ""),
        "dificultad": meta.get("dificultad", ""),
        "oscp": meta.get("en_lista_oscp") == "true",
        "oscp_seccion": meta.get("oscp_seccion", ""),
        "url": meta.get("url", ""),
        "intro": intro,
        "puertos": puertos,
        "secciones": secciones,
    }


def main():
    solo = None
    if "--puerto" in sys.argv:
        solo = sys.argv[sys.argv.index("--puerto") + 1]

    d = os.path.join(CORPUS, "htb")
    analisis = [analizar(os.path.join(d, f))
                for f in sorted(os.listdir(d)) if f.endswith(".md")]

    if solo:
        for a in analisis:
            if solo in a["puertos"]:
                p = a["puertos"][solo]
                sec = a["secciones"].get(solo, "(sin seccion con ese puerto)")
                print(f"  {a['maquina']:22s} {p['estado']:9s} nmap={p['etiqueta']:12s} "
                      f"real={sec}")
        return

    # indice inverso
    indice = {}
    for a in analisis:
        for num, p in a["puertos"].items():
            indice.setdefault(num, []).append({
                "archivo": a["archivo"],
                "maquina": a["maquina"],
                "os": a["os"],
                "dificultad": a["dificultad"],
                "oscp": a["oscp"],
                "estado": p["estado"],
                "etiqueta": p["etiqueta"],
                "real": a["secciones"].get(num, ""),
                "url": a["url"],
            })

    json.dump({"maquinas": analisis, "indice": indice},
              sys.stdout, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        try:
            sys.stdout.close()
        except Exception:  # noqa: BLE001
            pass
