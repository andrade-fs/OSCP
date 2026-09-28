#!/usr/bin/env python3
"""
construir-referencias.py — Convierte las bases de datos de GTFOBins, WADComs y
LOLBAS a notas de Obsidian, buscables y funcionales OFFLINE.

Por que local y no solo un link:

  Durante el examen, depender de internet es un punto unico de falla. Ademas,
  Obsidian no indexa sitios web: buscar "certutil" en el vault no encuentra nada
  que este en LOLBAS. Con las notas locales, Ctrl+O "certutil" te lleva directo.

  Las tres fuentes son GPL-3.0, asi que redistribuirlas localmente es legal
  (con atribucion, que va en cada nota).

Salida:
    Referencias.md                    indice + links curados
    Referencias/GTFOBins.md           indice de binarios
    Referencias/GTFOBins/<bin>.md     uno por binario
    Referencias/WADComs.md            indice
    Referencias/WADComs/<nombre>.md   uno por receta
    Referencias/LOLBAS.md             indice
    Referencias/LOLBAS/<bin>.md       uno por binario

Uso:
    python3 construir-referencias.py
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import yaml  # noqa: E402
from corpus_comun import leer_frontmatter  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATOS = os.path.join(ROOT, "_sistema", "datos", "referencias")
SALIDA = os.path.join(ROOT, "vault", "indices", "Referencias")

NAV = "[[00-inicio|Inicio]] · [[Referencias|Referencias]]"

FUENTES = {
    "GTFOBins": ("https://gtfobins.github.io/", "GPL-3.0",
                 "GTFOBins — binarios Unix y como abusarlos. Por contexto: sudo, SUID, capabilities."),
    "WADComs": ("https://wadcoms.github.io/", "GPL-3.0",
                "WADComs — comandos para Active Directory, ordenados por lo que TENES."),
    "LOLBAS": ("https://lolbas-project.github.io/", "GPL-3.0",
               "LOLBAS — binarios legitimos de Windows usables como atacante (living off the land)."),
}


def esc(s):
    return str(s).replace("|", "\\|")


def nombre_archivo(nombre):
    limpio = re.sub(r'[/\\:*?"<>|]', "-", str(nombre)).strip()
    return re.sub(r"\s+", "-", limpio) or "desconocido"


def escribir(path, contenido):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(contenido)


def cabecera(titulo, fuente, extra=""):
    url, lic, desc = FUENTES[fuente]
    return (f"# {titulo}\n\n{NAV} · [[{fuente}|Índice {fuente}]]\n\n"
            f"> Fuente: [{url}]({url}) · Licencia: **{lic}** · "
            f"Espejo local generado desde el repositorio oficial.\n\n"
            f"{desc}\n\n{extra}")


def yaml_front(texto):
    """Extrae y parsea el frontmatter YAML de un archivo de Jekyll."""
    m = re.match(r"^---\n(.*?)\n(?:---|\.\.\.)\s*$", texto, re.S | re.M)
    if not m:
        # archivo puro YAML (LOLBAS)
        try:
            return yaml.safe_load(texto) or {}
        except yaml.YAMLError:
            return {}
    try:
        return yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as e:
        print(f"    YAML invalido: {e}", file=sys.stderr)
        return {}


# --------------------------------------------------------------------------
# GTFOBins
# --------------------------------------------------------------------------
def nota_gtfobins(binario, datos):
    ctx_globales = set()
    bloques = []

    funciones = datos.get("functions") or {}
    for fn, entradas in funciones.items():
        if not isinstance(entradas, list):
            continue
        partes = []
        for ent in entradas:
            if not isinstance(ent, dict):
                continue
            code = (ent.get("code") or "").strip()
            comment = (ent.get("comment") or "").strip()
            ctxs = ent.get("contexts") or {}
            ctx_globales.update(ctxs.keys())

            # Código específico por contexto (para SUID suele necesitar -p)
            especificos = {}
            for cname, cval in (ctxs or {}).items():
                if isinstance(cval, dict) and cval.get("code"):
                    especificos.setdefault(cval["code"].strip(), []).append(cname)

            generales = [c for c in (ctxs or {})
                         if not (isinstance(ctxs.get(c), dict) and ctxs[c].get("code"))]

            if code:
                etiqueta = ", ".join(f"`{c}`" for c in generales) or "—"
                partes.append(f"**{etiqueta}**\n\n```bash\n{code}\n```\n")
            for cspec, nombres in especificos.items():
                et = ", ".join(f"`{n}`" for n in nombres)
                partes.append(f"**{et}** (código específico)\n\n```bash\n{cspec}\n```\n")
            if comment:
                partes.append(f"> {comment}\n")

        if partes:
            bloques.append((fn, "\n".join(partes)))

    extra = ""
    if datos.get("comment"):
        extra = f"> {str(datos['comment']).strip()}\n\n"
    if ctx_globales:
        extra += ("**Contextos:** " +
                  ", ".join(f"`{c}`" for c in sorted(ctx_globales)) + "\n\n")

    t = cabecera(f"GTFOBins: {binario}", "GTFOBins", extra)

    # Ordenar con shell primero: es lo que más se busca
    orden = {"shell": 0, "reverse-shell": 1, "file-read": 2, "file-write": 3,
             "file-upload": 4, "download": 5, "upload": 6, "library-load": 7,
             "privilege-escalation": 8, "command": 9}
    bloques.sort(key=lambda x: (orden.get(x[0], 50), x[0]))

    for fn, cuerpo in bloques:
        t += f"## {fn}\n\n{cuerpo}\n"
    return t


# --------------------------------------------------------------------------
# WADComs
# --------------------------------------------------------------------------
def nota_wadcoms(nombre, datos):
    desc = str(datos.get("description") or "").strip()
    cmd = str(datos.get("command") or "").strip()
    items = datos.get("items") or []
    sistemas = datos.get("OS") or []
    refs = datos.get("references") or []

    extra = ""
    if items:
        extra += "**Lo que tenés:** " + ", ".join(f"`{i}`" for i in items) + "\n\n"
    if sistemas:
        extra += "**Sistema:** " + ", ".join(f"`{o}`" for o in sistemas) + "\n\n"

    t = cabecera(f"WADComs: {nombre}", "WADComs", extra)
    if desc:
        t += f"## Descripción\n\n{desc}\n\n"
    if cmd:
        t += f"## Comando\n\n```bash\n{cmd}\n```\n\n"
    if refs:
        t += "## Referencias\n\n"
        for r in refs:
            if isinstance(r, dict):
                for k, v in r.items():
                    t += f"- [{k}]({v})\n"
            else:
                t += f"- {r}\n"
    return t


# --------------------------------------------------------------------------
# LOLBAS
# --------------------------------------------------------------------------
def nota_lolbas(nombre, datos):
    desc = str(datos.get("Description") or "").strip()
    cmds = datos.get("Commands") or []

    cats = sorted({str(c.get("Category", "")) for c in cmds
                   if isinstance(c, dict) and c.get("Category")})
    extra = ""
    if cats:
        extra += "**Categorías:** " + ", ".join(f"`{c}`" for c in cats) + "\n\n"

    t = cabecera(f"LOLBAS: {nombre}", "LOLBAS", extra)
    if desc:
        t += f"{desc}\n\n"

    t += "## Comandos\n\n"
    for c in cmds:
        if not isinstance(c, dict):
            continue
        comando = str(c.get("Command") or "").strip()
        d = str(c.get("Description") or "").strip()
        use = str(c.get("Usecase") or "").strip()
        priv = str(c.get("Privileges") or "").strip()
        mitre = str(c.get("MitreID") or "").strip()
        cat = str(c.get("Category") or "").strip()

        meta = " · ".join(x for x in (cat, f"priv: {priv}" if priv else "",
                                      mitre) if x)
        t += f"### {use or cat or 'comando'}\n\n"
        if meta:
            t += f"{meta}\n\n"
        if comando:
            t += f"```cmd\n{comando}\n```\n\n"
        if d:
            t += f"{d}\n\n"
    return t


# --------------------------------------------------------------------------
def construir_gtfobins(conteo):
    d = os.path.join(DATOS, "gtfobins")
    idx = []
    for name in sorted(os.listdir(d)):
        p = os.path.join(d, name)
        if not os.path.isfile(p):
            continue
        datos = yaml_front(open(p, encoding="utf-8", errors="replace").read())
        if not datos.get("functions"):
            continue
        try:
            escribir(os.path.join(SALIDA, "GTFOBins", f"{nombre_archivo(name)}.md"),
                     nota_gtfobins(name, datos))
        except OSError:
            continue
        fns = sorted((datos.get("functions") or {}).keys())
        idx.append((name, fns))

    t = cabecera("GTFOBins — índice",
                 "GTFOBins",
                 f"**{len(idx)}** binarios. Buscá con `Ctrl+O`.\n\n"
                 "`shell` = obtener shell. `file-read` = leer archivos. "
                 "`suid`/`sudo` cambian el comando: **mirá la nota del binario**, "
                 "no copies a ciegas.\n\n")
    t += "| Binario | Funciones |\n|---|---|\n"
    for name, fns in idx:
        t += (f"| [[{nombre_archivo(name)}\\\\|{esc(name)}]] | "
              f"{esc(', '.join(fns))} |\n")
    escribir(os.path.join(SALIDA, "GTFOBins.md"), t)
    conteo["GTFOBins"] = len(idx)


def construir_wadcoms(conteo):
    d = os.path.join(DATOS, "wadcoms")
    idx = []
    for name in sorted(os.listdir(d)):
        if not name.endswith(".md"):
            continue
        p = os.path.join(d, name)
        datos = yaml_front(open(p, encoding="utf-8", errors="replace").read())
        if not datos:
            continue
        titulo = name[:-3]
        try:
            escribir(os.path.join(SALIDA, "WADComs", f"{nombre_archivo(titulo)}.md"),
                     nota_wadcoms(titulo, datos))
        except OSError:
            continue
        items = datos.get("items") or []
        idx.append((titulo, items if isinstance(items, list) else []))

    # agrupar por "lo que tenés"
    por_item = {}
    for titulo, items in idx:
        for it in items:
            por_item.setdefault(str(it), []).append(titulo)

    t = cabecera("WADComs — índice",
                 "WADComs",
                 f"**{len(idx)}** recetas para Active Directory.\n\n"
                 "Organizado por **lo que tenés en la mano**, que es como se piensa "
                 "el ataque en AD: tenés un usuario, una contraseña, un hash, un TGT…\n\n")
    for it in sorted(por_item):
        t += f"## Tenés: {it}\n\n"
        t += ", ".join(f"[[{nombre_archivo(x)}\\\\|{esc(x)}]]" for x in sorted(por_item[it]))
        t += "\n\n"
    escribir(os.path.join(SALIDA, "WADComs.md"), t)
    conteo["WADComs"] = len(idx)


def construir_lolbas(conteo):
    base = os.path.join(DATOS, "lolbas")
    idx = []
    for dp, dn, fn in os.walk(base):
        for name in fn:
            if not name.endswith((".yml", ".yaml")):
                continue
            p = os.path.join(dp, name)
            datos = yaml_front(open(p, encoding="utf-8", errors="replace").read())
            if not isinstance(datos, dict) or not datos.get("Name"):
                continue
            titulo = str(datos["Name"])
            try:
                escribir(os.path.join(SALIDA, "LOLBAS", f"{nombre_archivo(titulo)}.md"),
                         nota_lolbas(titulo, datos))
            except OSError:
                continue
            cats = sorted({str(c.get("Category", ""))
                           for c in (datos.get("Commands") or [])
                           if isinstance(c, dict) and c.get("Category")})
            idx.append((titulo, cats, len(datos.get("Commands") or [])))

    idx.sort(key=lambda x: x[0].lower())
    por_cat = {}
    for titulo, cats, _n in idx:
        for c in cats:
            por_cat.setdefault(c, []).append(titulo)

    t = cabecera("LOLBAS — índice",
                 "LOLBAS",
                 f"**{len(idx)}** binarios de Windows.\n\n"
                 "Binarios **legítimos** que podés usar como atacante: descargar "
                 "archivos, ejecutar código, persistir. Sirven cuando no podés subir "
                 "herramientas.\n\n")
    t += "| Binario | Comandos | Categorías |\n|---|---|---|\n"
    for titulo, cats, n in idx:
        t += (f"| [[{nombre_archivo(titulo)}\\\\|{esc(titulo)}]] | {n} | "
              f"{esc(', '.join(cats))} |\n")
    t += "\n## Por categoría\n\n"
    for c in sorted(por_cat):
        t += (f"**{c}**: " +
              ", ".join(f"[[{nombre_archivo(x)}\\\\|{x}]]" for x in sorted(por_cat[c])) +
              "\n\n")
    escribir(os.path.join(SALIDA, "LOLBAS.md"), t)
    conteo["LOLBAS"] = len(idx)


def main():
    conteo = {}
    construir_gtfobins(conteo)
    construir_wadcoms(conteo)
    construir_lolbas(conteo)
    for k, v in conteo.items():
        print(f"  {k:10s} {v:4d} notas", file=sys.stderr)
    print(f"  salida: {SALIDA}", file=sys.stderr)


if __name__ == "__main__":
    main()
