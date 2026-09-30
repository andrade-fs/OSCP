#!/usr/bin/env python3
"""
verificar-enlaces.py — Chequeo estructural y de enlaces de documentacion.

Solo biblioteca estandar de Python: funciona offline y sin instalar nada.

Que comprueba (scope `first-slice`):

  1. ENLACES    Todo enlace Markdown relativo [texto](ruta) apunta a un archivo que existe.
  2. WIKILINKS  Todo wikilink [[Nombre]] resuelve a una nota .md que existe en el vault.
  3. RUTAS      Toda ruta .md escrita en codigo (inline o bloque) existe; tambien cubre
                los comandos copiables de las guias.
  4. VACIAS     Todo .md enlazado o referenciado que exista pero este EN BLANCO (solo NUL
                y espacios) es un error: el enlace parece valido y abre vacio.
  5. PLANTILLAS Las tarjetas de `plantillas/` tienen los 7 encabezados obligatorios y
                exactamente una etiqueta de alcance valida.
  6. FRAGMENTOS Todo fragmento `#ancla` de un enlace Markdown (`ruta.md#ancla`), de un
                enlace al propio archivo (`#ancla`) o de un wikilink (`[[nota#ancla]]`,
                `[[#ancla]]`) corresponde a un encabezado real del archivo destino. Un
                ancla rota abre la nota en el lugar equivocado: es un error, no un aviso.

Que agrega el scope `ad-slice` (ODG-05A):

  Los cuatro playbooks de `playbooks/` se validan con los MISMOS chequeos 1-4 y 6, y ademas
  con el contrato 5 (7 encabezados + exactamente una etiqueta de alcance permitida).
  El scope `first-slice` conserva su comportamiento: no incluye los playbooks.

Que agrega el scope `core-services-a` (ODG-05B1a):

  Suma los tres playbooks de servicio core (`playbooks/http-web.md`, `playbooks/smb.md` y
  `playbooks/ldap.md`) a los documentos de `first-slice` y `ad-slice`, y les aplica los MISMOS
  chequeos 1-4 y 6 mas el contrato 5. Es un superset explicito: `first-slice` y `ad-slice`
  conservan su comportamiento y su salida.

Que agrega el scope `core-services-b` (ODG-05B1b):

  Suma los tres playbooks de servicio core de la rebanada B (`playbooks/nfs.md`,
  `playbooks/mssql.md` y `playbooks/winrm.md`) a los documentos de `first-slice`, `ad-slice` y
  `core-services-a`, y les aplica los MISMOS chequeos 1-4 y 6 mas el contrato 5 de encabezados y
  etiqueta. Es el superset de todos los scopes anteriores: ninguno cambia su comportamiento ni su
  salida.

Que agrega el scope `windows-privesc` (ODG-05B2a):

  Suma el playbook de escalada Windows (`playbooks/windows-privesc.md`) a los documentos de
  `first-slice`, `ad-slice`, `core-services-a` y `core-services-b`, y le aplica los MISMOS
  chequeos 1-4 y 6 mas el contrato 5 de encabezados y etiqueta. Es el superset estricto de
  `core-services-b`: los scopes anteriores conservan su comportamiento y su salida.

Normalizacion de anclas (determinista, y documentada porque el resultado depende de ella):

  El vault usa un estilo simple en espanol (`### 9 — Kerberos y entorno`,
  `## Rutas canónicas — estado, no promesa`) y los enlaces escriben el ancla al estilo
  GitHub/Obsidian. Se compara el ancla declarada contra cada encabezado del destino
  aplicando la MISMA funcion `normalizar_ancla()` a las dos partes:

    1. Decodifica los escapes porcentuales (`%20`, UTF-8) del ancla declarada.
    2. Pasa todo a minusculas (Unicode, sin perder acentos: `ó` sigue siendo `ó`).
    3. Borra la puntuacion: todo lo que no sea letra, digito, `_`, `-` o espacio. Asi
       desaparecen `—`, `(`, `)`, `,`, `:` y `.`.
    4. Reemplaza cada espacio por un guion, uno por uno y SIN colapsar: los dos espacios
       que quedan alrededor de un `—` borrado producen `--`, y por eso
       `### 9 — Kerberos y entorno` normaliza a `9--kerberos-y-entorno`.

  Consecuencias: la comparacion no distingue mayusculas, y la puntuacion sobrante no
  rompe el match; los acentos NO se normalizan (`canonicas` no matchea `canónicas`).
  Las referencias de bloque (`#^id`) se ignoran: no son encabezados.

Que NO comprueba (y por eso no afirma que el vault este sano):

  - NO valida la salud de la capa generada (`vault/indices/**`). Solo mira los objetivos
    enlazados por los documentos del scope; no audita el resto del arbol.
  - NO valida URLs externas: no hay red en este chequeo.
  - NO valida rutas con placeholders (`<ALGO>`), absolutas (`~/`, `/`), con comodines
    (`*`) ni variables (`$VAR`): un placeholder no es una promesa.
  - NO valida las referencias de bloque de Obsidian (`#^id`), solo encabezados.
  - NO depende de `_sistema/datos/`, del generador del vault ni de dependencias externas.

Uso:
    python3 verificar-enlaces.py
    python3 verificar-enlaces.py --scope first-slice
    python3 verificar-enlaces.py --scope ad-slice
    python3 verificar-enlaces.py --scope core-services-a
    python3 verificar-enlaces.py --scope core-services-b
    python3 verificar-enlaces.py --scope windows-privesc

Salida: diagnostico por archivo y linea. Exit code 0 si no hay errores; 1 si hay alguno.
El contador `referencias chequeadas` cuenta las referencias que nombran un archivo (enlace
con ruta, wikilink con nombre o token de codigo); las anclas al propio archivo se validan
pero no se cuentan, para que el numero siga siendo comparable con corridas anteriores.
"""
import argparse
import os
import re
import sys
import urllib.parse

# ---------------------------------------------------------------- constantes

# Directorios que no forman parte del vault consultable.
IGNORAR_DIRS = {".git", ".obsidian", ".atl", ".engram", "__pycache__", "node_modules"}

# Archivos creados o editados por la primera rebanada de ODG-04.
PRIMERA_REBANADA = (
    "README.md",
    "guia/00-inicio.md",
    "guia/03-privesc-linux.md",
    "guia/lpe/LPE-Linux.md",
    "guia/router-escenarios.md",
    "plantillas/como-usar-plantillas.md",
    "plantillas/tarjeta-servicio.md",
    "plantillas/tarjeta-tecnica.md",
    "_sistema/SALUD-DOCUMENTAL.md",
    "_sistema/herramientas/verificar-enlaces.py",
)

# Tarjetas que deben cumplir el contrato de encabezados.
TARJETAS = (
    "plantillas/tarjeta-servicio.md",
    "plantillas/tarjeta-tecnica.md",
)

# Playbooks de decision de la rebanada AD (ODG-05A). Se validan con el mismo contrato de
# encabezados y etiqueta que las tarjetas de `plantillas/`, sin tocar el scope first-slice.
REBANADA_AD = (
    "playbooks/ad-desde-credenciales.md",
    "playbooks/kerberos-y-tickets.md",
    "playbooks/certipy-y-adcs.md",
    "playbooks/credenciales-y-movimiento.md",
)

# Scopes disponibles: la primera rebanada, la primera rebanada + los playbooks de AD, y
# primera rebanada + AD + los playbooks de servicios core A (ODG-05B1a) y B (ODG-05B1b).
REBANADA_CORE_A = (
    "playbooks/http-web.md",
    "playbooks/smb.md",
    "playbooks/ldap.md",
)

REBANADA_CORE_B = (
    "playbooks/nfs.md",
    "playbooks/mssql.md",
    "playbooks/winrm.md",
)

# Playbook de escalada Windows (ODG-05B2a). Suma `playbooks/windows-privesc.md` a todos los
# scopes anteriores y le aplica el MISMO contrato de encabezados y etiqueta.
REBANADA_WINDOWS_PRIVESC = (
    "playbooks/windows-privesc.md",
)

SCOPES = ("first-slice", "ad-slice", "core-services-a", "core-services-b", "windows-privesc")

ENCABEZADOS_OBLIGATORIOS = (
    "## Entrada",
    "## Primeras acciones",
    "## Puntos de decisión",
    "## Evidencia",
    "## Parqueo",
    "## Enlaces",
    "## Alcance",
)

ETIQUETAS_VALIDAS = (
    "verificado-examen",
    "solo-laboratorio",
    "prohibido",
    "pendiente-politica",
)

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Raiz del repositorio (un nivel arriba del vault): permite rutas tipo `OSCP/guia/...`.
RAIZ_REPO = os.path.dirname(ROOT)

RE_LINK = re.compile(r"\[[^\]]*\]\(\s*<?([^)>\s]+)>?(?:\s+\"[^\"]*\")?\s*\)")
# El nombre puede estar vacio: `[[#ancla]]` es un ancla a la propia nota.
RE_WIKI = re.compile(r"\[\[([^\[\]#|]*)(?:#([^\[\]|]*))?(?:\|[^\[\]]*)?\]\]")
# Encabezados ATX, ya sin bloques de codigo (los playbooks tienen `#` en bloques bash).
RE_ENCABEZADO = re.compile(r"^#{1,6}[ \t]+(.+?)[ \t]*$", re.MULTILINE)
# Puntuacion que no forma parte de un ancla: se borra antes de comparar (ver docstring).
RE_ANCLA_BASURA = re.compile(r"[^\w\s-]", re.UNICODE)
# Cada espacio se cambia por un guion, uno por uno y sin colapsar (ver docstring).
RE_ANCLA_ESPACIO = re.compile(r"\s", re.UNICODE)
RE_FENCE = re.compile(r"^[ \t]*(```|~~~).*?^[ \t]*\1[ \t]*$", re.MULTILINE | re.DOTALL)
RE_INLINE_CODE = re.compile(r"`[^`\n]+`")
RE_MD_TOKEN = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_./-]*\.md")
RE_ETIQUETA = re.compile(r"^Etiqueta:\s*(\S+)\s*$", re.MULTILINE)

# Un token es "promesa de ruta" solo si no es placeholder, comodin, ruta absoluta ni variable.
NO_ES_PROMESA = re.compile(r"[<>*$~]|^[/~]")
# Notacion de rango en un arbol o listado (p. ej. `suelta-1/2/3.md`): no es una ruta.
ES_RANGO = re.compile(r"\d/\d")


# ---------------------------------------------------------------- utilidades

def quitar_bloques(texto):
    """Devuelve (texto_sin_bloques, bloques) para no parsear sintaxis dentro de codigo."""
    bloques = []

    def _guardar(m):
        bloques.append(m.group(0))
        return "\n" * m.group(0).count("\n")

    return RE_FENCE.sub(_guardar, texto), bloques


def lineas_con(texto, pos):
    return texto.count("\n", 0, pos) + 1


def esta_en_blanco(ruta):
    """True si el archivo solo tiene NUL y espacios (nota generada vacia)."""
    try:
        crudo = open(ruta, "rb").read()
    except OSError:
        return False
    return crudo.replace(b"\x00", b"").decode("utf-8", "replace").strip() == ""


# Cache de anclas por archivo: el router es destino de muchos fragmentos en una corrida.
_CACHE_ANCLAS = {}


def normalizar_ancla(texto):
    """Ancla canonica: minusculas, sin puntuacion y con un guion por espacio.

    Paso 4 del docstring: los espacios se reemplazan uno por uno y sin colapsar, para que
    `### 9 — Kerberos y entorno` y `#9--kerberos-y-entorno` (los dos espacios que rodean al
    `—` borrado) coincidan. Los acentos se conservan tal cual.
    """
    texto = urllib.parse.unquote(texto.strip().lower())
    return RE_ANCLA_ESPACIO.sub("-", RE_ANCLA_BASURA.sub("", texto))


def anclas_de(ruta):
    """Conjunto de anclas normalizadas de un .md, sin mirar dentro de bloques de codigo."""
    clave = os.path.normpath(os.path.abspath(ruta))
    if clave not in _CACHE_ANCLAS:
        try:
            texto = open(ruta, encoding="utf-8", errors="replace").read()
        except OSError:
            texto = ""
        sin_bloques, _ = quitar_bloques(texto)
        _CACHE_ANCLAS[clave] = {normalizar_ancla(h) for h in RE_ENCABEZADO.findall(sin_bloques)}
    return _CACHE_ANCLAS[clave]


def revisar_fragmento(rel, linea, etiqueta, fragmento, rutas, rep):
    """Valida `#fragmento` contra los encabezados del destino.

    No reporta nada si el enlace ya se reporto por otro motivo (destino inexistente o nota
    vacia) ni si el destino no es Markdown: ahi un `#ancla` no es un encabezado.
    """
    if not fragmento or fragmento.startswith("^"):
        return
    objetivos = [r for r in rutas if r.endswith(".md") and os.path.exists(r) and not esta_en_blanco(r)]
    if not objetivos:
        return
    ancla = normalizar_ancla(fragmento)
    if any(ancla in anclas_de(r) for r in objetivos):
        return
    rep.error(rel, linea, f"fragmento sin encabezado en {etiqueta}: #{fragmento}")


def indexar_vault():
    """basename (con .md) -> [rutas], para resolver wikilinks como Obsidian."""
    indice = {}
    for raiz, dirs, archivos in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in IGNORAR_DIRS]
        for nombre in archivos:
            if nombre.endswith(".md"):
                indice.setdefault(nombre, []).append(os.path.join(raiz, nombre))
    return indice


def documentos_del_scope(scope):
    """Documentos cuyos enlaces se validan para el scope pedido."""
    if scope == "first-slice":
        return PRIMERA_REBANADA
    if scope == "ad-slice":
        return PRIMERA_REBANADA + REBANADA_AD
    if scope == "core-services-a":
        return PRIMERA_REBANADA + REBANADA_AD + REBANADA_CORE_A
    if scope == "core-services-b":
        return PRIMERA_REBANADA + REBANADA_AD + REBANADA_CORE_A + REBANADA_CORE_B
    return (
        PRIMERA_REBANADA + REBANADA_AD + REBANADA_CORE_A + REBANADA_CORE_B
        + REBANADA_WINDOWS_PRIVESC
    )


def tarjetas_del_scope(scope):
    """Tarjetas/playbooks que deben cumplir encabezados + etiqueta permitida."""
    if scope == "first-slice":
        return TARJETAS
    if scope == "ad-slice":
        return TARJETAS + REBANADA_AD
    if scope == "core-services-a":
        return TARJETAS + REBANADA_AD + REBANADA_CORE_A
    if scope == "core-services-b":
        return TARJETAS + REBANADA_AD + REBANADA_CORE_A + REBANADA_CORE_B
    return TARJETAS + REBANADA_AD + REBANADA_CORE_A + REBANADA_CORE_B + REBANADA_WINDOWS_PRIVESC


def resolver_token(token, base):
    """Resuelve una ruta .md relativa al archivo, al vault o a la raiz del repo."""
    if NO_ES_PROMESA.search(token) or ES_RANGO.search(token):
        return []
    candidatos = [
        os.path.normpath(os.path.join(base, token)),
        os.path.normpath(os.path.join(ROOT, token)),
        os.path.normpath(os.path.join(RAIZ_REPO, token)),
    ]
    vistos = []
    for c in candidatos:
        if c not in vistos:
            vistos.append(c)
    return vistos


# ---------------------------------------------------------------- chequeos

class Reporte:
    def __init__(self):
        self.errores = 0
        self.avisos = 0
        self.chequeados = 0

    def error(self, archivo, linea, mensaje):
        self.errores += 1
        print(f"  FALLA  {archivo}:{linea}  {mensaje}")

    def aviso(self, archivo, linea, mensaje):
        self.avisos += 1
        print(f"  aviso  {archivo}:{linea}  {mensaje}")

    def ok(self, archivo, cantidad):
        self.chequeados += cantidad
        print(f"  ok     {archivo}  ({cantidad} referencias)")


def revisar_enlaces(rel, texto, indice, rep):
    """Enlaces Markdown y rutas .md en codigo."""
    sin_bloques, bloques = quitar_bloques(texto)
    base = os.path.dirname(os.path.join(ROOT, rel))
    vistos = 0

    for m in RE_LINK.finditer(sin_bloques):
        destino = m.group(1).strip()
        if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", destino):
            continue
        linea = lineas_con(sin_bloques, m.start())
        if destino.startswith("#"):
            # Ancla a la propia nota: no nombra archivo, pero el encabezado debe existir.
            revisar_fragmento(rel, linea, rel, destino[1:], [os.path.join(ROOT, rel)], rep)
            continue
        destino, _, fragmento = destino.partition("#")
        if not destino:
            continue
        if destino.startswith("/"):
            continue
        ruta = os.path.normpath(os.path.join(base, destino))
        vistos += 1
        if not os.path.exists(ruta):
            rep.error(rel, linea, f"enlace a objetivo inexistente: {destino}")
        elif ruta.endswith(".md") and esta_en_blanco(ruta):
            rep.error(rel, linea, f"enlace a nota VACIA: {destino}")
        else:
            revisar_fragmento(rel, linea, f"{destino}#{fragmento}", fragmento, [ruta], rep)

    # Rutas .md escritas como codigo (bloques y spans), para cubrir comandos copiables.
    # Solo se exigen las que son rutas explicitas (con `/`): un nombre suelto en un arbol
    # de directorios es una mencion, no una promesa de ruta.
    for fragmento, linea in _fragmentos_de_codigo(texto, bloques):
        for m in RE_MD_TOKEN.finditer(fragmento):
            token = m.group(0)
            if NO_ES_PROMESA.search(token) or ES_RANGO.search(token):
                continue
            if "/" not in token:
                candidatos = indice.get(os.path.basename(token), [])
                if candidatos and all(esta_en_blanco(c) for c in candidatos):
                    rep.error(rel, linea, f"nombre de nota VACIA en codigo: {token}")
                continue
            candidatos = resolver_token(token, base)
            vistos += 1
            existente = next((c for c in candidatos if os.path.exists(c)), None)
            if existente is None:
                rep.error(rel, linea, f"ruta .md inexistente en codigo: {token}")
            elif esta_en_blanco(existente):
                rep.error(rel, linea, f"ruta .md apunta a nota VACIA: {token}")
    return vistos


def _fragmentos_de_codigo(texto, bloques):
    """(fragmento, linea) de cada fragmento de codigo, para reportar con contexto."""
    for bloque in bloques:
        pos = texto.find(bloque)
        yield bloque, (lineas_con(texto, pos) if pos >= 0 else 0)
    sin_bloques = RE_FENCE.sub("", texto)
    for m in RE_INLINE_CODE.finditer(sin_bloques):
        yield m.group(0), lineas_con(sin_bloques, m.start())


def revisar_wikilinks(rel, texto, indice, rep):
    """Wikilinks: deben resolver a una nota existente y no vacia."""
    sin_bloques, _ = quitar_bloques(texto)
    sin_codigo = RE_INLINE_CODE.sub(" ", sin_bloques)
    vistos = 0
    for m in RE_WIKI.finditer(sin_codigo):
        nombre = m.group(1).strip()
        fragmento = (m.group(2) or "").strip()
        if not nombre and not fragmento:
            continue
        if nombre.startswith("^"):
            continue
        linea = lineas_con(sin_codigo, m.start())
        if not nombre:
            # Ancla a la propia nota: `[[#encabezado]]`.
            revisar_fragmento(rel, linea, rel, fragmento, [os.path.join(ROOT, rel)], rep)
            continue
        vistos += 1
        candidatos = indice.get(nombre + ".md", [])
        if not candidatos and "/" in nombre:
            ruta = os.path.normpath(os.path.join(ROOT, nombre + ".md"))
            candidatos = [ruta] if os.path.exists(ruta) else []
        if not candidatos:
            rep.error(rel, linea, f"wikilink sin destino en el vault: [[{nombre}]]")
            continue
        if len(candidatos) > 1:
            rep.aviso(rel, linea, f"wikilink ambiguo ({len(candidatos)} notas): [[{nombre}]]")
        if all(esta_en_blanco(c) for c in candidatos):
            rep.error(rel, linea, f"wikilink a nota VACIA: [[{nombre}]]")
            continue
        # Con destino ambiguo alcanza con que UNA de las notas tenga el encabezado.
        revisar_fragmento(rel, linea, f"{nombre}#{fragmento}", fragmento, candidatos, rep)
    return vistos


def revisar_plantilla(rel, texto, rep):
    """Contrato de la tarjeta: encabezados obligatorios + una etiqueta de alcance."""
    sin_bloques, _ = quitar_bloques(texto)
    encabezados = re.findall(r"^##[ \t]+(.+?)[ \t]*$", sin_bloques, re.MULTILINE)
    presentes = {"## " + e for e in encabezados}
    for requerido in ENCABEZADOS_OBLIGATORIOS:
        if requerido not in presentes:
            rep.error(rel, 0, f"falta el encabezado obligatorio: {requerido}")

    etiquetas = RE_ETIQUETA.findall(sin_bloques)
    if len(etiquetas) != 1:
        rep.error(rel, 0, f"debe haber exactamente una linea 'Etiqueta: <valor>' (hay {len(etiquetas)})")
    elif etiquetas[0] not in ETIQUETAS_VALIDAS:
        rep.error(rel, 0, f"etiqueta de alcance invalida: {etiquetas[0]}")
    else:
        print(f"  ok     {rel}  encabezados y etiqueta '{etiquetas[0]}'")


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(
        description="Verifica enlaces y estructura de la documentacion (solo stdlib).",
    )
    ap.add_argument(
        "--scope",
        default="first-slice",
        choices=list(SCOPES),
        help="conjunto de documentos a verificar (default: first-slice)",
    )
    args = ap.parse_args()

    documentos = documentos_del_scope(args.scope)
    tarjetas = tarjetas_del_scope(args.scope)

    print("verificar-enlaces.py — verificacion de enlaces y estructura")
    print(f"raiz del vault : {ROOT}")
    print(f"scope          : {args.scope}")
    print(f"documentos     : {len(documentos)}")
    alcance = {
        "first-slice": "solo enlaces y estructura de esta rebanada.",
        "ad-slice": "primera rebanada + playbooks de la rebanada AD.",
        "core-services-a": "primera rebanada + playbooks de AD + playbooks de servicios core A.",
        "core-services-b": (
            "primera rebanada + playbooks de AD + playbooks de servicios core A + core B."
        ),
        "windows-privesc": (
            "primera rebanada + playbooks de AD + servicios core A y B + escalada Windows."
        ),
    }[args.scope]
    print(f"alcance real   : {alcance}")
    print("NO verifica    : salud de la capa generada (vault/indices/**) ni URLs externas.")
    print("-" * 72)

    rep = Reporte()
    indice = indexar_vault()

    for rel in documentos:
        ruta = os.path.join(ROOT, rel)
        if not os.path.exists(ruta):
            rep.error(rel, 0, "documento del scope inexistente")
            continue
        if rel.endswith(".py"):
            print(f"  ok     {rel}  (script del scope, sin enlaces que validar)")
            continue
        try:
            texto = open(ruta, encoding="utf-8", errors="replace").read()
        except OSError as exc:
            rep.error(rel, 0, f"no se pudo leer: {exc}")
            continue
        n = revisar_enlaces(rel, texto, indice, rep)
        n += revisar_wikilinks(rel, texto, indice, rep)
        rep.ok(rel, n)

    print("-" * 72)
    for rel in tarjetas:
        ruta = os.path.join(ROOT, rel)
        if os.path.exists(ruta):
            texto = open(ruta, encoding="utf-8", errors="replace").read()
            revisar_plantilla(rel, texto, rep)

    print("-" * 72)
    print(f"referencias chequeadas : {rep.chequeados}")
    print(f"errores                : {rep.errores}")
    print(f"avisos                 : {rep.avisos}")
    if rep.errores:
        print("RESULTADO: FALLA — corregi los errores y volve a correr.")
        return 1
    resultado = {
        "first-slice": "enlaces y estructura de la primera rebanada consistentes.",
        "ad-slice": "enlaces y estructura de first-slice + ad-slice consistentes.",
        "core-services-a": (
            "enlaces y estructura de first-slice + ad-slice + core-services-a consistentes."
        ),
        "core-services-b": (
            "enlaces y estructura de first-slice + ad-slice + core-services-a + core-services-b "
            "consistentes."
        ),
        "windows-privesc": (
            "enlaces y estructura de first-slice + ad-slice + core-services-a + core-services-b "
            "+ windows-privesc consistentes."
        ),
    }[args.scope]
    print(f"RESULTADO: OK — {resultado}")
    print("Recordatorio: esto NO dice que la capa generada del vault este sana.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
