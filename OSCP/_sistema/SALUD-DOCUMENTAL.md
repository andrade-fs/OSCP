# Salud documental — estado observado de la capa generada

> **Este documento describe defectos observados. No es un plan de arreglo y no afirma salud.**
>
> Re-observación: **2026-09-30**, sobre el checkout de trabajo
> (`/private/tmp/OSCP`, rama `docs/oscp-exam-decision-guide`).
> Auditoría previa registrada: **2026-03-13** (ODG-01, ODG-02, ODG-03).
>
> Alcance: solo la capa **generada** de `vault/` y sus dependencias. Este archivo vive en
> `_sistema/` y está excluido del índice de Obsidian (`userIgnoreFilters`).

---

## Resumen

| # | Defecto observado | Estado | Efecto en el examen |
| --- | --- | --- | --- |
| 1 | Falta `_sistema/datos/` (entradas del generador) | Ausente | La capa generada **no es reproducible**. |
| 2 | Notas de técnica/puerto/referencia en blanco | 217 archivos | Enlaces que abren vacío. |
| 3 | Falta el directorio destino de GTFOBins | Ausente (458 notas) | No hay referencia por binario. |
| 4 | Puntos de entrada duplicados | 2+ | Flujos divergentes entre sí. |
| 5 | Deriva de rutas (docs vs. instalador) | 5 divergencias | Comandos que escriben en rutas que no existen. |

**Verificación de este documento**: los conteos se obtuvieron contando archivos en el checkout.
No hay verificación automática que mantenga estos números al día: si la capa generada cambia,
este documento queda obsoleto y hay que volver a medirlo.

---

## 1. Falta `_sistema/datos/` — la capa generada no es reproducible

`_sistema/datos/` **no existe** en el repositorio. Es la entrada de prácticamente todo el
pipeline:

| Script | Entrada que falta |
| --- | --- |
| `_sistema/herramientas/construir-referencias.py` | `_sistema/datos/referencias/` |
| `_sistema/herramientas/construir-vault.py` | `_sistema/datos/comandos/` |
| `_sistema/herramientas/buscar.py` | `_sistema/datos/tecnicas.txt` |
| `_sistema/herramientas/indice.py` | `_sistema/datos/tecnicas.txt` |
| `_sistema/herramientas/marcar-oscp.py` | `_sistema/datos/lista-oscp.json` |
| `_sistema/herramientas/arreglar-frontmatter.py` | `_sistema/datos/lista-oscp.json` |
| `_sistema/herramientas/raspar.py` | `_sistema/datos/lista-oscp.json` |

Consecuencias observadas:

- El `vault/indices/` que está en disco **se conserva**, pero es un artefacto histórico: no se
  puede reconstruir a partir del repositorio.
- `buscar.py` degrada explícitamente cuando falta su entrada
  (`(falta _sistema/datos/tecnicas.txt)`), así que la búsqueda por técnica no puede filtrar
  contra la lista canónica de técnicas.
- Cualquier corrección de contenido en `vault/` se perdería en la próxima regeneración. Por eso
  la capa generada se trata como **solo lectura** hasta que se recuperen los datos.

### Regla segura (obligatoria)

> **No ejecutes los generadores del vault mientras falte `_sistema/datos/`.**
>
> En concreto: no corras `construir-vault.py`, `construir-referencias.py`, `indice.py`,
> `marcar-oscp.py` ni `arreglar-frontmatter.py`. Sin sus entradas, producen salida parcial,
> vacía o inconsistente, y **sobrescriben** la capa generada que hoy sí es utilizable.
>
> Primero hay que **recuperar y versionar `_sistema/datos/`**. Recién después tiene sentido
> regenerar, y antes de hacerlo hay que respaldar `vault/indices/`.

El único script de mantenimiento que no depende de `_sistema/datos/` es el raspador del corpus
(`raspar.py --solo-htb`), que además necesita internet y no se ejecuta en este trabajo.

---

## 2. Notas en blanco en la capa generada

Se cuentan como **en blanco** los archivos cuyo contenido es únicamente bytes NUL y espacios:
no contienen texto, solo relleno del tamaño esperado. Medición del 2026-09-30:

| Directorio | En blanco | Total |
| --- | --- | --- |
| `vault/indices/Tecnicas/` | **52** | 165 |
| `vault/indices/Puertos/` | **49** | 498 |
| `vault/indices/Referencias/` | **116** | 354 |
| `vault/indices/Servicios/` | 0 | 221 |
| **Total** | **217** | 1.238 |

Dentro de `Referencias/`: `LOLBAS/` tiene **81 en blanco de 248** y `WADComs/` **35 de 103**.

Los índices maestros (`Tecnicas.md`, `Puertos.md`, `Servicios.md`, `Referencias.md` y los
índices `GTFOBins.md`, `LOLBAS.md`, `WADComs.md`) **no** están en blanco: listan y enlazan a
las notas individuales, y son justamente los que sí funcionan.

Técnicas en blanco de **alto tráfico** (la lista completa se puede recalcular con el comando de
abajo): `suid`, `kerberoasting`, `pass-the-hash`, `mimikatz`, `lsass`, `ldap`, `smb`, `ssh`,
`hashcat`, `john-the-ripper`, `evil-winrm`, `winpeas`, `dcsync`, `certipy`, `esc1`, `esc8`,
`smbmap`, `rdp`, `snmp`, `smtp`, `mssql`, `nfs`, `public-exploit`, `buffer-overflow`.

Efecto concreto: `[[kerberoasting]]` o `Ctrl+O` → `kerberoasting` abre una nota vacía. El router
y las guías nuevas **no enlazan** a esas notas: derivan al cheatsheet o a la guía canónica.

Cómo volver a medirlo (solo lectura, no escribe nada):

```bash
python3 - <<'PY'
import os
for base in ("Tecnicas", "Puertos", "Servicios", "Referencias"):
    d = os.path.join("OSCP/vault/indices", base)
    n = b = 0
    for dp, _, fs in os.walk(d):
        for f in fs:
            if not f.endswith(".md"):
                continue
            n += 1
            raw = open(os.path.join(dp, f), "rb").read()
            if raw.replace(b"\x00", b"").decode("utf-8", "replace").strip() == "":
                b += 1
    print(f"{base}: en blanco={b} total={n}")
PY
```

---

## 3. Falta el directorio destino de GTFOBins

- Referenciado por la documentación: `vault/indices/Referencias/GTFOBins/` (**no existe**).
- Existente: `vault/indices/Referencias/GTFOBins.md` (índice, 18.869 bytes, en blanco: no).
- `construir-referencias.py` declara esa salida (`SALIDA = vault/indices/Referencias`), pero sin
  `_sistema/datos/referencias/` no la puede producir.
- El índice anuncia **458** binarios. En disco hay **0** notas por binario: el espejo de
  referencias tiene **351 de las 809 notas prometidas** (248 LOLBAS + 103 WADComs), y las 458
  que faltan son exactamente el conjunto de GTFOBins. La afirmación «809 notas» de
  `README.md` no se corresponde con el contenido en disco.

Consecuencia: no hay referencia local **por binario** para escalada Linux. Los directorios
hermanos `LOLBAS/` y `WADComs/` sí existen, pero tienen notas en blanco (ver §2).

Estado de la reparación en esta rebanada: las promesas de `guia/03-privesc-linux.md`,
`guia/lpe/LPE-Linux.md`, `guia/00-inicio.md` y `README.md` se corrigieron para no anunciar el
espejo inexistente y conservar las alternativas útiles (índice + referencia online documentada).
La capa generada **no se tocó**.

---

## 4. Puntos de entrada duplicados

| Documento | Rol | Problema observado |
| --- | --- | --- |
| `OSCP/README.md` | Portada del repo | Repetía el **mismo flujo de decisión** que `00-inicio.md`, con tablas distintas. |
| `OSCP/guia/00-inicio.md` | Punto de entrada del vault | Repetía el flujo y su propia tabla de decisión. |
| `vault/indices/Puertos.md` | Índice generado | Es otra entrada equivalente al índice por servicio (`Servicios.md`) para el mismo caso de uso. |

Consecuencia: el lector podía seguir dos caminos con criterios distintos y no coincidentes.

Estado en esta rebanada: `README.md` y `guia/00-inicio.md` dejan de duplicar el flujo y derivan
al router único, [`guia/router-escenarios.md`](../guia/router-escenarios.md). **No** se modificó
`vault/indices/**`.

---

## 5. Deriva de rutas (documentación vs. instalador)

Fuente del instalador: `OSCP-setup/lib.sh` (`DOCS`, `VAULT`, `TOOLS`, `LINUX_DIR`, `WIN_DIR`).
**No se modificaron los scripts de setup**: la deriva se documenta, no se parchea.

| Qué | Documentación dice | Instalador crea | Estado |
| --- | --- | --- | --- |
| Vault | `~/OSCP` | `${HOME}/Documentos/OSCP` | Divergente |
| Toolkits | `~/examen/tools/{linux,win}` | `${HOME}/Documentos/Tools/{linux,win,kali,repos}` | Divergente |
| Evidencia | `~/examen/evidencia/<maquina>/` | — (no lo crea) | Sin origen |
| Entradas del generador | `_sistema/datos/` | — (no existe en el repo) | Ausente |
| Verificador de entorno | `~/OSCP/_sistema/herramientas/verificar-entorno.sh` | `OSCP-setup/verify.sh` | Divergente |

Observaciones adicionales:

- `OSCP/README.md` afirmaba a la vez `~/OSCP` **y** `/home/kali/Documentos/OSCP` en la misma
  frase, lo que ya era una contradicción interna.
- `install.sh` crea `${TOOLS}/plantillas` (plantillas de `krb5.conf`), que **no** es
  `OSCP/plantillas/` (tarjetas de documentación). Son dos cosas distintas con el mismo nombre.
- `verificar-entorno.sh` asume `$HOME/examen/tools`, es decir el nombre que la documentación
  promete, no el que crea el instalador.

**La conciliación sigue pendiente.** El router lo declara explícitamente en su sección
[«Rutas canónicas — estado, no promesa»](../guia/router-escenarios.md#rutas-canónicas--estado-no-promesa).

---

## Lo que este documento NO afirma

- **No** afirma que la capa generada esté sana, completa o verificada.
- **No** afirma que el instalador y la documentación coincidan: dice lo contrario.
- **No** afirma que los conteos sigan vigentes: son una medición con fecha.
- **No** autoriza a regenerar nada ni a editar `vault/indices/**`.
- **No** clasifica política de examen: eso vive en
  [`guia/00-reglas-examen.md`](../guia/00-reglas-examen.md) y su fuente oficial no se pudo
  recuperar (HTTP 403).

---

## Verificación disponible hoy

```bash
# Estructura y enlaces de la primera rebanada de documentación (stdlib, offline)
python3 OSCP/_sistema/herramientas/verificar-enlaces.py --scope first-slice
```

Ese verificador **no** valida la salud de la capa generada: solo comprueba que los documentos de
la primera rebanada no enlacen a objetivos ausentes o en blanco, y que las plantillas respeten
su contrato de encabezados. La capa generada sigue sin verificación automática.

---

## Alcance

`pendiente-politica` — documento de estado técnico del repositorio. No contiene reglas de
examen ni afirmaciones de política.
