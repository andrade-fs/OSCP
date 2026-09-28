#!/usr/bin/env python3
"""
indice.py — Genera los indices navegables del corpus.

Produce, en corpus/_indice/:
  README.md      como buscar (comandos listos)
  maquinas.md    tabla de todas las maquinas con metadatos
  tecnicas.md    indice inverso: tecnica -> en que maquinas aparece

Uso:
    python3 indice.py
"""
import os
import re
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from corpus_comun import leer_frontmatter, limpiar_para_contar  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CORPUS = os.path.join(ROOT, "vault", "corpus")
TECNICAS = os.path.join(ROOT, "_sistema", "datos", "tecnicas.txt")
SALIDA = os.path.join(CORPUS, "_indice")




def cargar():
    docs = []
    for base in ("htb", "otros"):
        d = os.path.join(CORPUS, base)
        if not os.path.isdir(d):
            continue
        for name in sorted(os.listdir(d)):
            if name.endswith(".md"):
                p = os.path.join(d, name)
                docs.append((p, name, leer_frontmatter(p)))
    return docs



def compilar_patron(pat):
    """Compila con limites de palabra.

    Sin esto, "iis" matchea dentro de blobs base64 y "x11" dentro del
    User-Agent de curl. El limite solo se pone en los extremos que son
    caracteres de palabra, para no romper patrones como "cve-".
    """
    # Limite de INICIO siempre: evita que "iis" matchee dentro de "skiis" o de
    # un blob base64.
    izq = r"\b" if re.match(r"\w", pat) else ""
    # Limite de FIN solo en patrones cortos. Ponerlo siempre rompe prefijos
    # legitimos: "seassignprimarytoken" dejaria de matchear
    # "SeAssignPrimaryTokenPrivilege", que es exactamente lo que se busca.
    der = r"\b" if (len(pat) <= 3 and re.search(r"\w$", pat)) else ""
    return re.compile(izq + re.escape(pat) + der, re.IGNORECASE)


def cargar_tecnicas():
    """Devuelve [(etiqueta, seccion, [patrones...])] preservando el orden."""
    if not os.path.exists(TECNICAS):
        return []
    out = []
    seccion = "general"
    for line in open(TECNICAS, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        if line.startswith("# seccion:"):
            seccion = line.split(":", 1)[1].strip()
            continue
        if line.startswith("#"):
            continue
        partes = [p.strip() for p in line.split("|") if p.strip()]
        if partes:
            out.append((partes[0], seccion, partes))
    return out



def cargar_contenido(docs=None):
    """{nombre_archivo: texto} de todo el corpus.

    Contamos sobre texto LIMPIO (sin URLs ni imagenes). A lo bruto, "gitlab"
    matcheaba los 566 archivos por el footer del sitio, y "x11" 168 veces por el
    User-Agent de curl.
    """
    if docs is None:
        docs = cargar()
    contenido = {}
    for p, name, _meta in docs:
        try:
            contenido[name[:-3] if name.endswith(".md") else name] = limpiar_para_contar(
                open(p, encoding="utf-8", errors="replace").read())
        except OSError:
            pass
    return contenido


def main():
    docs = cargar()
    if not docs:
        print("corpus vacio", file=sys.stderr)
        return 1
    os.makedirs(SALIDA, exist_ok=True)

    # ---------- cargar contenido en memoria ----------
    contenido = cargar_contenido(docs)

    # ---------- maquinas.md ----------
    filas = []
    for p, name, meta in docs:
        if meta.get("tipo") != "htb":
            continue
        maq = meta.get("maquina") or name[:-3]
        filas.append({
            "maq": maq,
            "arch": name,
            "os": meta.get("os", ""),
            "dif": meta.get("dificultad", ""),
            "oscp": meta.get("en_lista_oscp") == "true",
            "rel": meta.get("release", ""),
            "url": meta.get("htb_url", ""),
        })
    filas.sort(key=lambda r: (not r["oscp"], r["maq"].lower()))

    with open(os.path.join(SALIDA, "maquinas.md"), "w", encoding="utf-8") as f:
        f.write("# Maquinas en el corpus\n\n")
        f.write(f"Total: **{len(filas)}** maquinas de HTB con writeup publico.\n\n")
        n_oscp = sum(1 for r in filas if r["oscp"])
        f.write(f"Marcadas como parte del listado OSCP (TJ Null, pestana PWK V3): "
                f"**{n_oscp}**.\n\n")
        f.write("Ordenadas por relevancia OSCP y luego alfabetico.\n\n")
        f.write("| Maquina | SO | Dificultad | OSCP | Release | Writeup |\n")
        f.write("|---|---|---|---|---|---|\n")
        for r in filas:
            f.write(f"| {r['maq']} | {r['os']} | {r['dif']} | "
                    f"{'**si**' if r['oscp'] else '—'} | {r['rel']} | "
                    f"[[{r['arch'][:-3]}]] |\n")

    # ---------- tecnicas.md ----------
    tecnicas = cargar_tecnicas()
    por_seccion = defaultdict(list)
    for etiqueta, sec, patrones in tecnicas:
        hits = []
        # Compilamos una vez por tecnica, con limites de palabra.
        regs = [compilar_patron(pat) for pat in patrones]
        for name in contenido:
            texto = contenido[name]
            n = 0
            for rx in regs:
                n += len(rx.findall(texto))
            if n:
                hits.append((name, n))
        hits.sort(key=lambda x: -x[1])
        por_seccion[sec].append((etiqueta, patrones, hits))

    with open(os.path.join(SALIDA, "tecnicas.md"), "w", encoding="utf-8") as f:
        f.write("# Indice de tecnicas\n\n")
        f.write("Para cada tecnica, las maquinas donde aparece y cuantas veces.\n\n")
        f.write("Para ver el **contexto** de una tecnica:\n\n")
        f.write("```bash\n")
        f.write("python3 _sistema/herramientas/buscar.py kerberoasting -v\n")
        f.write("python3 _sistema/herramientas/buscar.py kerberoasting -v --oscp\n")
        f.write("```\n\n")
        f.write("---\n\n")

        for sec in por_seccion:
            f.write(f"## {sec}\n\n")
            for etiqueta, patrones, hits in por_seccion[sec]:
                if not hits:
                    continue
                otras = [p for p in patrones[1:]]
                extra = f" _(tambien: {', '.join(otras)})_" if otras else ""
                f.write(f"### {etiqueta}{extra}\n\n")
                f.write(f"{len(hits)} maquinas.\n\n")
                # las claves de contenido ya vienen SIN .md: si no, el link
                # apunta a "nota.md" y Obsidian no lo resuelve
                enlaces = ", ".join(f"[[{n}]] ({c})" for n, c in hits[:60])
                f.write(enlaces + "\n")
                if len(hits) > 60:
                    f.write(f"\n_(y {len(hits)-60} mas)_\n")
                f.write("\n")
            f.write("\n")

    # ---------- README ----------
    vacias = [e for s in por_seccion for e, _, h in por_seccion[s] if not h]
    with open(os.path.join(SALIDA, "README.md"), "w", encoding="utf-8") as f:
        f.write("""# Como buscar en el corpus

Corpus de writeups publicos de 0xdf, descargados desde el `sitemap.xml` del sitio
y convertidos a markdown. Cada archivo tiene frontmatter con metadatos
(maquina, SO, dificultad, si esta en el listado OSCP, URL original).

## Busqueda por palabra clave (recomendado)

```bash
cd ~/OSCP

# Todas las referencias a una tecnica, agrupadas por maquina
python3 _sistema/herramientas/buscar.py PrintSpoofer

# Con contexto: ver el comando y el output alrededor
python3 _sistema/herramientas/buscar.py PrintSpoofer -v

# Mas contexto todavia
python3 _sistema/herramientas/buscar.py PrintSpoofer -vv

# Solo maquinas del listado OSCP
python3 _sistema/herramientas/buscar.py kerberoasting -v --oscp

# Solo Linux, o solo una dificultad
python3 _sistema/herramientas/buscar.py "sudo -l" -v --os Linux
python3 _sistema/herramientas/buscar.py seimpersonate -v --dificil Hard

# Regex
python3 _sistema/herramientas/buscar.py "GodPotato|JuicyPotato|PrintSpoofer"

# Solo los nombres de maquina (vista rapida)
python3 _sistema/herramientas/buscar.py kerberoasting --nombres

# Que tecnicas conoce el diccionario
python3 _sistema/herramientas/buscar.py --listar-tecnicas
```

## Busqueda cruda (ripgrep)

```bash
# Lista de maquinas que mencionan algo
rg -l 'kerberoast' corpus/ | sort

# Con numero de linea y contexto
rg -n -C 4 'PrintSpoofer' corpus/

# Solo bloques de codigo (comandos)
rg -n -A 6 '^```' corpus/htb/ -g '*.md' | rg -A 6 'impacket'
```

## Indices

| Archivo | Contenido |
|---|---|
| [[maquinas]] | Tabla de las 566 maquinas con SO, dificultad y marca OSCP |
| [[tecnicas]] | Indice inverso: tecnica -> maquinas donde aparece |

## En Obsidian

Apuntalo como vault a `~/OSCP/corpus`. Funcionan:

- **Busqueda global** (`Ctrl+Shift+F`): full-text sobre todo el corpus.
- **Propiedades**: filtrar por `os`, `dificultad`, `en_lista_oscp`.
  Ejemplo de busqueda: `["en_lista_oscp":"true"] seimpersonate`
- **Grafo**: los enlaces `[[maquina]]` de los indices arman la red.
- **Backlinks**: desde una maquina, que tecnicas la referencian.

> Las imagenes de los writeups **no** se descargaron: el markdown conserva los
> enlaces a las originales. El corpus esta pensado para busqueda de TEXTO.
""")

    print(f"maquinas: {len(filas)} (OSCP: {n_oscp})", file=sys.stderr)
    print(f"tecnicas con al menos un match: "
          f"{sum(1 for s in por_seccion for _, _, h in por_seccion[s] if h)}"
          f"/{len(tecnicas)}", file=sys.stderr)
    if vacias:
        print(f"tecnicas sin ningun match ({len(vacias)}): "
              f"{', '.join(vacias[:20])}", file=sys.stderr)
    print(f"escrito en {SALIDA}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
