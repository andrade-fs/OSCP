#!/usr/bin/env python3
"""
construir-vault.py — Arma el vault de Obsidian sobre el corpus.

Genera:
    OSCP/00-inicio.md            mapa de contenido (punto de entrada)
    OSCP/indices/Puertos/<n>.md   indice inverso: puerto -> maquinas
    OSCP/indices/Puertos.md       lista de todos los puertos
    OSCP/indices/Servicios/<s>.md  indice por servicio
    OSCP/indices/Servicios.md     lista de todos los servicios
    OSCP/indices/Tecnicas/<t>.md  indice por tecnica
    OSCP/indices/Tecnicas.md      lista de todas las tecnicas
    OSCP/indices/Maquinas.md      lista de maquinas
    OSCP/.obsidian/              configuracion del vault

El indice por PUERTO es la pieza clave para el examen: dado un puerto abierto,
muestra que maquinas lo tenian, que corria de verdad ahi (segun el encabezado
del writeup, no segun la etiqueta de nmap) y si esta en el listado OSCP.

Uso:
    python3 construir-vault.py
"""
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
INDICES = os.path.join(ROOT, "vault", "indices")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from corpus_comun import limpiar_para_contar  # noqa: E402

SIN_SECCION = "(sin seccion con ese puerto)"


def esc(s):
    """Escapa el pipe dentro de una celda de tabla markdown."""
    return str(s).replace("|", "\\|")



def nombre_archivo(nombre):
    """Nombre seguro para archivo, preservando el original para mostrar.

    Sin esto, un servicio llamado "ssl/ldap" crea Servicios/ssl/ldap.md y el
    link [[ssl/ldap]] no resuelve nunca (la nota se llama "ldap").
    """
    limpio = re.sub(r'[/\\:*?"<>|]', "-", nombre).strip()
    # Espacios -> guiones: "password spraying" -> "password-spraying".
    # Sin esto las notas quedaban con espacios y las recetas con guiones, y el
    # cruce fallaba en silencio.
    return re.sub(r"\s+", "-", limpio) or "desconocido"


def escribir(path, contenido):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(contenido)


def cabecera(titulo, extra=""):
    return (f"# {titulo}\n\n"
            f"[[00-inicio|Inicio]] · [[Entorno|Entorno]] · [[Puertos|Puertos]] · "
            f"[[Servicios|Servicios]] · [[Tecnicas|Tecnicas]] · [[Maquinas|Maquinas]] · "
            f"[[Referencias|Referencias]]\n\n"
            f"{extra}")


# --------------------------------------------------------------------------
def cargar_puertos():
    out = subprocess.run(
        [sys.executable, os.path.join(ROOT, "_sistema", "herramientas", "extraer-puertos.py")],
        capture_output=True, text=True, cwd=ROOT)
    return json.loads(out.stdout)


def nota_puerto(num, regs):
    n_maq = len(regs)
    n_oscp = sum(1 for r in regs if r["oscp"])
    etiquetas = {}
    for r in regs:
        etiquetas[r["etiqueta"]] = etiquetas.get(r["etiqueta"], 0) + 1
    top_label = max(etiquetas, key=etiquetas.get) if etiquetas else ""
    reales = [r["real"] for r in regs if r["real"] and r["real"] != SIN_SECCION]

    extra = f"**{n_maq} máquina(s)** con **{num}** abierto"
    if n_oscp:
        extra += f" · **{n_oscp} en el listado OSCP**"
    extra += "\n\n"

    # El aviso mas util: cuando la etiqueta de nmap NO es lo que corria.
    # OJO: contar, no deduplicar. Con un set, 17 valores distintos de 7 formas
    # daban n_igual=10 y el aviso nunca se disparaba.
    reales_count = {}
    for r in regs:
        v = r["real"]
        if v and v != SIN_SECCION:
            reales_count[v] = reales_count.get(v, 0) + 1
    if top_label and reales_count:
        top_real = max(reales_count, key=reales_count.get)
        n_igual = sum(1 for r in regs
                      if r.get("real") and r["real"].lower() == top_label.lower())
        if top_real.lower() != top_label.lower() and n_igual <= len(reales_count) / 2:
            extra += (f"> ⚠️ **nmap lo etiqueta `{top_label}` "
                      f"({etiquetas.get(top_label, 0)} de {n_maq} casos), pero eso "
                      f"no es lo que corría.**\n"
                      f"> Lo más común era **{esc(top_real)}** "
                      f"({reales_count[top_real]} de {sum(reales_count.values())} "
                      f"casos identificados).\n"
                      f"> No te guíes por la etiqueta de nmap: mirá la columna *Real*.\n\n")

    # Estados que importan
    filtrados = [r for r in regs if r["estado"] != "open"]
    if filtrados:
        extra += (f"> ℹ️ {len(filtrados)} caso(s) en estado "
                  f"`{filtrados[0]['estado']}`: no lo alcanzás desde donde estás. "
                  f"Es pista de **pivoting**, no de explotación directa.\n\n")

    regs_ord = sorted(regs, key=lambda r: (not r["oscp"], r["maquina"].lower()))

    t = cabecera(f"Puerto {num}", extra)
    t += "| Máquina | SO | Dif. | Estado | nmap dice | Qué era realmente | OSCP |\n"
    t += "|---|---|---|---|---|---|---|\n"
    for r in regs_ord:
        real = r["real"] if r["real"] and r["real"] != SIN_SECCION else "—"
        t += (f"| [[{r['archivo']}\\|{esc(r['maquina'])}]] | {r.get('os','')} | "
              f"{r.get('dificultad','')} | `{r['estado']}` | "
              f"`{esc(r['etiqueta'])}` | {esc(real)} | "
              f"{'**sí**' if r['oscp'] else '—'} |\n")

    t += "\n## Cómo profundizar\n\n```bash\n"
    t += f"python3 _sistema/herramientas/buscar.py '{num}/tcp' -v\n"
    t += f"python3 _sistema/herramientas/buscar.py '{num}' -v --oscp\n```\n\n"

    if reales:
        t += "## Qué corría, agrupado\n\n"
        grupos = {}
        for r in regs:
            if r["real"] and r["real"] != SIN_SECCION:
                grupos.setdefault(r["real"], []).append(r)
        for nombre, rs in sorted(grupos.items(), key=lambda x: -len(x[1])):
            enlaces = ", ".join(f"[[{r['archivo']}\\|{esc(r['maquina'])}]]" for r in rs)
            t += f"- **{esc(nombre)}** ({len(rs)}): {enlaces}\n"
        t += "\n"

    return t


def nota_servicio(nombre, regs, puertos_del_servicio):
    n_maq = len(regs)
    n_oscp = sum(1 for r in regs if r["oscp"])
    extra = f"**{n_maq} máquina(s)** exponen `{nombre}`"
    if n_oscp:
        extra += f" · **{n_oscp} en el listado OSCP**"
    extra += "\n\n"
    if puertos_del_servicio:
        pl = ", ".join(f"[[{p}]]" for p in sorted(puertos_del_servicio, key=int))
        extra += f"Puertos donde aparece: {pl}\n\n"

    t = cabecera(f"Servicio: {nombre}", extra)
    t += "| Máquina | Puerto | Estado | Qué era realmente | OSCP |\n"
    t += "|---|---|---|---|---|\n"
    for r in sorted(regs, key=lambda r: (not r["oscp"], r["maquina"].lower())):
        real = r["real"] if r["real"] and r["real"] != SIN_SECCION else "—"
        t += (f"| [[{r['archivo']}\\|{esc(r['maquina'])}]] | [[{r['puerto']}]] | "
              f"`{r['estado']}` | {esc(real)} | {'**sí**' if r['oscp'] else '—'} |\n")
    t += f"\n## Cómo profundizar\n\n```bash\n"
    t += f"python3 _sistema/herramientas/buscar.py '{nombre}' -v\n```\n"
    return t



COMANDOS_DIR = os.path.join(ROOT, "_sistema", "datos", "comandos")



# Que referencia externa corresponde a cada receta. La clave es el nombre
# normalizado de la receta (datos/comandos/<clave>.md).
REFS_RECETA = {
    "suid":                 ["GTFOBins"],
    "sudo":                 ["GTFOBins"],
    "capabilities":         ["GTFOBins"],
    "cron":                 ["GTFOBins"],
    "nfs-no_root_squash":   ["HackTricks"],
    "docker-group":         ["HackTricks"],
    "credenciales-en-archivos": ["HackTricks"],
    "seimpersonate":        ["LOLBAS", "HackTricks"],
    "unquoted-service-path": ["LOLBAS", "HackTricks"],
    "alwaysinstallelevated": ["LOLBAS", "HackTricks"],
    "lsass":                ["LOLBAS", "HackTricks"],
    "kerberoasting":        ["WADComs", "The Hacker Recipes"],
    "asreproast":           ["WADComs", "The Hacker Recipes"],
    "dcsync":               ["WADComs", "The Hacker Recipes"],
    "rbcd":                 ["WADComs", "The Hacker Recipes"],
    "delegacion-restringida":     ["WADComs", "The Hacker Recipes"],
    "delegacion-sin-restriccion": ["WADComs", "The Hacker Recipes"],
    "shadow-credentials":   ["WADComs", "The Hacker Recipes"],
    "pass-the-hash":        ["WADComs"],
    "pass-the-ticket":      ["WADComs"],
    "password-spraying":    ["WADComs"],
    "adcs":                 ["WADComs", "The Hacker Recipes"],
    "gpp":                  ["WADComs"],
}

# Como se enlaza cada referencia, y a que URL online corresponde
REFS_ENLACE = {
    "GTFOBins":          ("[[GTFOBins|GTFOBins (espejo local)]]",
                          "https://gtfobins.github.io/"),
    "WADComs":           ("[[WADComs|WADComs (espejo local)]]",
                          "https://wadcoms.github.io/"),
    "LOLBAS":            ("[[LOLBAS|LOLBAS (espejo local)]]",
                          "https://lolbas-project.github.io/"),
    "HackTricks":        ("[HackTricks](https://book.hacktricks.wiki/)", ""),
    "The Hacker Recipes": ("[The Hacker Recipes](https://www.thehacker.recipes/)", ""),
}


def bloque_referencias(clave_receta):
    """Devuelve el bloque '## Referencias' para una receta, o ''."""
    refs = REFS_RECETA.get(clave_receta)
    if not refs:
        return ""
    lineas = ["## Referencias\n"]
    for r in refs:
        etiqueta, url = REFS_ENLACE.get(r, (r, ""))
        extra = f" — {url}" if url else ""
        lineas.append(f"- {etiqueta}{extra}")
    return "\n".join(lineas) + "\n"


def buscar_comandos(patrones):
    """Busca una receta para la tecnica, probando TODOS sus alias.

    Hace falta probar todos: varias tecnicas tienen el nombre principal en
    espanol ("delegacion restringida") y el archivo esta con el alias en ingles
    ("constrained-delegation").
    """
    for pat in patrones:
        for cand in (nombre_archivo(pat), pat.strip()):
            ruta = os.path.join(COMANDOS_DIR, f"{cand}.md")
            if os.path.isfile(ruta):
                return open(ruta, encoding="utf-8").read().strip(), cand
    return "", ""


def nota_tecnica(nombre, patrones, hits):
    comandos, clave_receta = buscar_comandos(patrones)

    extra = f"**{len(hits)} máquina(s)** mencionan esta técnica.\n\n"
    otras = patrones[1:]
    if otras:
        extra += f"Alias buscados: {', '.join('`'+p+'`' for p in otras)}\n\n"
    if comandos:
        extra += ("> Esta técnica tiene **recetario de comandos**. "
                  "Está más abajo, después de la lista de máquinas.\n\n")

    t = cabecera(f"Técnica: {nombre}", extra)

    # Los comandos van primero: es lo que se busca bajo presion en el examen.
    if comandos:
        t += "## Comandos\n\n" + comandos + "\n\n"
        t += bloque_referencias(clave_receta) + "\n---\n\n"

    t += "## Máquinas\n\n"
    for arch, meta, n in hits:
        maq = meta.get("maquina") or arch
        cab = " · ".join(x for x in (meta.get("os", ""), meta.get("dificultad", "")) if x)
        oscp = " **[OSCP]**" if meta.get("en_lista_oscp") == "true" else ""
        t += f"- [[{arch}\\|{esc(maq)}]]{oscp} — {n} mención(es)" + (f" · {esc(cab)}" if cab else "") + "\n"

    t += f"\n## Cómo ver el contexto\n\n```bash\n"
    t += f"python3 _sistema/herramientas/buscar.py '{nombre}' -v\n"
    t += f"python3 _sistema/herramientas/buscar.py '{nombre}' -v --oscp\n```\n"
    return t


# --------------------------------------------------------------------------
def main():
    datos = cargar_puertos()
    indice = datos["indice"]
    maquinas = {m["archivo"]: m for m in datos["maquinas"]}

    # ---------- Puertos ----------
    print(f"  puertos: {len(indice)}", file=sys.stderr)
    filas = []
    for num, regs in indice.items():
        escribir(os.path.join(INDICES, "Puertos", f"{num}.md"), nota_puerto(num, regs))
        filas.append((num, len(regs), sum(1 for r in regs if r["oscp"])))
    filas.sort(key=lambda x: -x[1])

    t = cabecera("Puertos", "Índice inverso: puerto → máquinas que lo tenían.\n\n"
                            "**Durante el examen**: ves un puerto abierto, abrís "
                            "`Ctrl+O` en Obsidian, escribís el número, y entrás.\n\n")
    t += "| Puerto | Máquinas | OSCP | Puerto | Máquinas | OSCP |\n"
    t += "|---|---|---|---|---|---|\n"
    mitad = (len(filas) + 1) // 2
    izq, der = filas[:mitad], filas[mitad:]
    for i in range(mitad):
        a = izq[i]
        c = der[i] if i < len(der) else ("", "", "")
        cel_a = f"[[{a[0]}]] | {a[1]} | {a[2] or '—'}"
        cel_b = f"[[{c[0]}]] | {c[1]} | {c[2] or '—'}" if c[0] else "| |"
        t += f"| {cel_a} | {cel_b} |\n"
    escribir(os.path.join(INDICES, "Puertos.md"), t)

    # ---------- Servicios ----------
    servicios = {}
    puertos_por_servicio = {}
    for num, regs in indice.items():
        for r in regs:
            et = r["etiqueta"] or "desconocido"
            servicios.setdefault(et, []).append({**r, "puerto": num})
            puertos_por_servicio.setdefault(et, set()).add(num)
    print(f"  servicios: {len(servicios)}", file=sys.stderr)

    filas_s = []
    for nombre, regs in servicios.items():
        escribir(os.path.join(INDICES, "Servicios", f"{nombre_archivo(nombre)}.md"),
                 nota_servicio(nombre, regs, puertos_por_servicio.get(nombre, set())))
        filas_s.append((nombre, len(regs), sum(1 for r in regs if r["oscp"])))
    filas_s.sort(key=lambda x: -x[1])

    t = cabecera("Servicios", "Índice por la etiqueta que devuelve nmap.\n\n")
    t += "| Servicio | Máquinas | OSCP |\n|---|---|---|\n"
    for n, c, o in filas_s:
        t += f"| [[{nombre_archivo(n)}\\|{esc(n)}]] | {c} | {o or '—'} |\n"
    escribir(os.path.join(INDICES, "Servicios.md"), t)

    # ---------- Tecnicas ----------
    from indice import cargar_tecnicas, compilar_patron, cargar_contenido
    tecnicas = cargar_tecnicas()
    contenido = cargar_contenido()
    print(f"  tecnicas: {len(tecnicas)}", file=sys.stderr)

    filas_t = []
    con_receta = []
    for nombre, sec, patrones in tecnicas:
        regs = [compilar_patron(p) for p in patrones]
        hits = []
        for arch, texto in contenido.items():
            n = sum(len(rx.findall(texto)) for rx in regs)
            if n:
                hits.append((arch, maquinas.get(arch, {}), n))
        hits.sort(key=lambda x: -x[2])
        # OJO: no saltear si hay recetario. Una tecnica puede tener 0 menciones
        # en los writeups (porque los alias estan en espanol y el corpus en
        # ingles) y aun asi tener comandos que valen. El recetario no depende
        # de las menciones.
        if not hits and not buscar_comandos(patrones)[0]:
            continue
        escribir(os.path.join(INDICES, "Tecnicas", f"{nombre_archivo(nombre)}.md"),
                 nota_tecnica(nombre, patrones, hits))
        filas_t.append((nombre, sec, len(hits), sum(1 for _, m, _ in hits
                                                    if m.get("oscp"))))
        if buscar_comandos(patrones)[0]:
            con_receta.append(nombre)
    filas_t.sort(key=lambda x: -x[3] or -x[2])

    t = cabecera("Técnicas", "Ordenado por cuántas máquinas del "
                            "**listado OSCP** la usan.\n\n")
    con_set = set(con_receta)
    t += ("Índice inverso: técnica → máquinas donde aparece.\n\n"
          "La columna **Receta** marca las que tienen comandos copy-paste listos\n"
          "(en la propia nota, sección *Comandos*).\n\n")
    t += "| Técnica | Máquinas | de ellas OSCP | Receta |\n|---|---|---|---|\n"
    for n, sec, c, o in filas_t:
        marca = "**sí**" if n in con_set else "—"
        t += f"| [[{nombre_archivo(n)}\\|{esc(n)}]] | {c} | " \
             f"{'**' + str(o) + '**' if o else '—'} | {marca} |\n"
    escribir(os.path.join(INDICES, "Tecnicas.md"), t)

    # ---------- Maquinas ----------
    filas_m = []
    for arch, m in maquinas.items():
        filas_m.append((arch, m))
    filas_m.sort(key=lambda x: (not x[1].get("oscp"),
                                (x[1].get("maquina") or "").lower()))

    n_oscp = sum(1 for _, m in filas_m if m.get("oscp"))
    t = cabecera("Máquinas",
                 f"**{len(filas_m)}** máquinas con writeup público. "
                 f"**{n_oscp}** están en el listado OSCP de TJ Null "
                 f"(pestaña PWK V3).\n\n"
                 f"Ordenadas por relevancia OSCP y luego alfabético.\n\n")
    t += "| Máquina | SO | Dificultad | OSCP | Puerto destacado |\n|---|---|---|---|---|\n"
    for arch, m in filas_m:
        ps = sorted(m.get("puertos", {}).keys(), key=int)
        # mostrar los puertos mas "de ataque", no los de infraestructura
        destacados = [p for p in ps if p in ("21", "22", "80", "139", "443", "445",
                                             "1433", "3000", "3306", "3389", "5000",
                                             "5432", "5985", "8000", "8080", "8443")]
        cel = ", ".join(f"[[{p}]]" for p in destacados[:6]) or "—"
        t += (f"| [[{arch}\\|{esc(m.get('maquina',''))}]] | {m.get('os','')} | "
              f"{m.get('dificultad','')} | "
              f"{'**sí**' if m.get('oscp') else '—'} | {cel} |\n")
    escribir(os.path.join(INDICES, "Maquinas.md"), t)

    print(f"  escritos: {len(indice)} puertos, {len(servicios)} servicios, "
          f"{len(filas_t)} tecnicas, {len(filas_m)} maquinas", file=sys.stderr)
    print(f"  tecnicas con recetario de comandos: {len(con_receta)} -> "
          f"{', '.join(con_receta[:8])}...", file=sys.stderr)


if __name__ == "__main__":
    main()
