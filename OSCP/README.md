# Playbook OSCP+

Documentación de consulta para el examen **OSCP+**, organizada **por técnica** —no por
máquina— y pensada para leerse sin internet.

El **corpus sí está en disco**, pero las **entradas del generador no**: falta
`_sistema/datos/`. Por eso la capa `vault/indices/` se conserva **solo lectura** y hoy **no es
reproducible**. Estado completo: [`_sistema/SALUD-DOCUMENTAL.md`](_sistema/SALUD-DOCUMENTAL.md).

> **Las rutas no están conciliadas.** Esta documentación nombra `~/OSCP` y `~/examen/tools/`;
el instalador (`OSCP-setup/lib.sh`) crea `~/Documentos/OSCP` y `~/Documentos/Tools`. Ninguna de
las dos es "la correcta" todavía. Verificá cuál existe antes de copiar un comando.

```bash
cd ~/Documentos/OSCP   # o ~/OSCP: las dos rutas circulan, no están conciliadas
obsidian .             # abrir el vault
```

---

## Empezá por acá

| Quiero… | Ir a |
| --- | --- |
| **Saber qué hacer con lo que observé** (el caso central) | [`guia/router-escenarios.md`](guia/router-escenarios.md) — **el router único** |
| **Entender cómo se usa el vault durante el examen** | [`guia/00-inicio.md`](guia/00-inicio.md) |
| **Repasar las reglas/restricciones** antes de rendir | [`guia/00-reglas-examen.md`](guia/00-reglas-examen.md) |
| **Buscar una técnica** (kerberoast, SUID, PrintSpoofer…) | `Ctrl+O` → nombre, o [`vault/indices/Tecnicas.md`](vault/indices/Tecnicas.md) |
| **Ver qué corría en un puerto** | `Ctrl+O` → `5000`, o [`vault/indices/Puertos.md`](vault/indices/Puertos.md) |
| **Comandos rápidos de una herramienta** | [`cheatsheets/`](cheatsheets/) |
| **Registrar algo nuevo sin inventar formato** | [`plantillas/`](plantillas/) |
| **Saber qué está roto o ausente** | [`_sistema/SALUD-DOCUMENTAL.md`](_sistema/SALUD-DOCUMENTAL.md) |
| **Saber qué técnicas ya están cubiertas** | [`_sistema/Cobertura-fuentes.md`](_sistema/Cobertura-fuentes.md) |

---

## Estructura

```
OSCP/
├── README.md                 ← portada (este archivo)
│
├── guia/                     ← EL PLAYBOOK: leer en orden
│   ├── router-escenarios.md  ← 🎯 EL ROUTER: observación → qué hacer
│   ├── 00-inicio … 09-web
│   ├── Entorno.md · verificado-2026.md
│   ├── walkthroughs/         ← AD-walkthrough, Standalone-walkthrough
│   └── lpe/                  ← LPE-Linux, LPE-Windows
│
├── cheatsheets/              ← chuletas por herramienta y técnica
│
├── plantillas/               ← tarjetas reutilizables (servicio, técnica)
│
├── vault/                    ← GENERADO: conservado, NO reproducible
│   ├── indices/              ← Puertos/Servicios/Técnicas/Máquinas/Referencias
│   └── corpus/               ← 565 writeups de HTB + índices de texto
│
├── _sistema/                 ← INTERNO (excluido de Obsidian)
│   ├── datos/                ← ❌ AUSENTE: entradas del generador
│   ├── herramientas/         ← scripts de regeneración + verificar-enlaces.py
│   ├── SALUD-DOCUMENTAL.md   ← defectos observados de la capa generada
│   └── Cobertura-fuentes.md
│
├── examen/                   ← 🎯 documentos de examen (1 por máquina)
│   ├── 00-dashboard.md       panel: estado, tiempo, creds globales
│   ├── suelta-1/2/3.md       máquinas independientes (Linux/Windows)
│   ├── ad-miembro-1/2.md     clientes del AD
│   ├── ad-dc.md              Domain Controller
│   └── ad-credenciales.md    creds/loot global del AD
│
├── Inbox/                    ← notas nuevas (entrada de Obsidian)
└── Adjuntos/                 ← imágenes/adjuntos
```

| Carpeta | Qué hay | Cómo se regenera |
| --- | --- | --- |
| `guia/` | playbook 00–09 + `router-escenarios.md` + `Entorno.md` + `verificado-2026.md` + `walkthroughs/` + `lpe/` | **a mano** |
| `cheatsheets/` | nxc, impacket, certipy, potatoes, mssql, coerción, ADCS, AD avanzado, LFI, web | **a mano** |
| `plantillas/` | tarjetas de servicio y técnica (sin comandos) | **a mano** |
| `vault/indices/Puertos/` · `Servicios/` · `Tecnicas/` | 884 notas índice, de las cuales **217 están en blanco** | ⚠️ `construir-vault.py` — **no correr**: falta `_sistema/datos/` |
| `vault/indices/Referencias/` | **351** de las 809 anunciadas (248 LOLBAS + 103 WADComs); el espejo GTFOBins por binario **no existe** | ⚠️ `construir-referencias.py` — **no correr**: falta `_sistema/datos/` |
| `vault/indices/Maquinas.md` | 565 máquinas con SO, dificultad y marca OSCP | ⚠️ `construir-vault.py` — **no correr**: falta `_sistema/datos/` |
| `vault/corpus/htb/` | 565 writeups | `_sistema/herramientas/raspar.py` (necesita internet) |
| `vault/corpus/_indice/` | índices de texto del corpus | ⚠️ `indice.py` — **no correr**: falta `_sistema/datos/` |
| `_sistema/` | scripts, cobertura de fuentes y salud documental (`datos/` **ausente**) | — |
| `examen/` | 🎯 documentos de examen: 1 por máquina + panel + creds AD | **a mano (durante el examen)** |
| `Inbox/` · `Adjuntos/` | notas nuevas y adjuntos de Obsidian | — |

> `_sistema/` está **excluido del índice de Obsidian** (`userIgnoreFilters`) para que sus `.md`
> crudos no dupliquen notas en el buscador ni en el grafo.

> **`vault/` es generado y hoy no es reproducible.** Si editás algo ahí, se pierde; pero
> tampoco lo vas a poder regenerar, porque falta `_sistema/datos/`. Mientras siga así:
> **no corras los generadores** y tratá `vault/indices/` como **solo lectura**. Ver
> [`_sistema/SALUD-DOCUMENTAL.md`](_sistema/SALUD-DOCUMENTAL.md).
>
> **Qué falla offline, concretamente**: los índices por puerto/servicio/técnica listan y enlazan
> bien, pero **217 notas individuales están en blanco** y el espejo GTFOBins por binario **no
> existe**. No es un problema de internet: es un defecto de la capa generada.
>
> **Chequeo estructural disponible** (solo stdlib, offline):
> `python3 _sistema/herramientas/verificar-enlaces.py --scope first-slice`. Valida enlaces y
> encabezados de la primera rebanada de documentación. **No** valida la salud del vault generado.

---

## Índice de contenido

### 1. Guía — el playbook, en orden

| # | Documento | Para qué |
| --- | --- | --- |
| — | [Router de escenarios](guia/router-escenarios.md) | **Empezá acá durante el examen**: observación → documento correcto |
| — | [00-inicio](guia/00-inicio.md) | **Manual de uso** del vault |
| 00 | [Reglas del examen](guia/00-reglas-examen.md) | Restricciones, Metasploit, proofs, reverts, sanciones |
| 01 | [Metodología y tiempo](guia/01-metodologia.md) | El bucle de trabajo y cómo sobrevivir 23 h 45 min |
| 02 | [Enumeración por servicio](guia/02-enumeracion-servicios.md) | Tenés puertos y no sabés por dónde entrar |
| 03 | [Escalada en Linux](guia/03-privesc-linux.md) | Tenés shell, sos usuario común |
| 04 | [Escalada en Windows](guia/04-privesc-windows.md) | Tenés shell, sos usuario común |
| 05 | [Active Directory](guia/05-active-directory.md) | **40 pts** — el set completo, de inicio a fin |
| — | [AD Walkthrough](guia/walkthroughs/AD-walkthrough.md) | **Set de 3 máquinas de cero a DA**, integrando el LPE |
| — | [Standalone Walkthrough](guia/walkthroughs/Standalone-walkthrough.md) | **Las 3 máquinas sueltas**: recon → foothold → LPE → flags |
| 06 | [Payloads y shells](guia/06-payloads-shells-transferencia.md) | Generar/subir/bajar payloads, client-side |
| 07 | [Pivoting y túneles](guia/07-pivoting.md) | Atravesar un host para llegar al siguiente |
| 08 | [Reporte y evidencia](guia/08-reporte-y-evidencia.md) | Desde el minuto cero, no al final |
| 09 | [Ataques web](guia/09-web.md) | Cómo abordar un objetivo web: LFI, upload, SQLi, SSRF, SSTI, APIs |
| — | [Entorno](guia/Entorno.md) | `krb5.conf`, `/etc/hosts`, DNS, reloj, proxychains |
| — | [LPE-Linux](guia/lpe/LPE-Linux.md) · [LPE-Windows](guia/lpe/LPE-Windows.md) | Checklists de orden de ataque |

### 2. Chuletas — consulta rápida

| Documento | Contenido |
| --- | --- |
| [nxc.md](cheatsheets/nxc.md) | NetExec 1.5.1 — SMB, LDAP, WinRM, MSSQL |
| [impacket.md](cheatsheets/impacket.md) | Impacket 0.14.0.dev0 — suite completa |
| [certipy.md](cheatsheets/certipy.md) | **Certipy v5.1.0** (¡no es la sintaxis de v4!) |
| [potatoes.md](cheatsheets/potatoes.md) | Familia Potato + matriz de compatibilidad |
| [mssql-injection.md](cheatsheets/mssql-injection.md) | Inyección MSSQL, OOB, Trusted Links |
| [rpc-coercion.md](cheatsheets/rpc-coercion.md) | Coerción (PetitPotam, PrinterBug, DFSCoerce…) |
| [adcs-esc.md](cheatsheets/adcs-esc.md) | Mapa completo de ESC + Certifried |
| [ad-avanzado.md](cheatsheets/ad-avanzado.md) | Kerberos avanzado, persistencia, SCCM/Exchange |
| [lfi-rce.md](cheatsheets/lfi-rce.md) | LFI→RCE y variantes de inyección web |
| [web.md](cheatsheets/web.md) | **Ataques web**: checklist, LFI/RFI, upload, SQLi (MySQL/MSSQL/Postgres), SSTI, APIs, Hydra |

### 3. Meta

| Documento | Contenido |
| --- | --- |
| [verificado-2026.md](guia/verificado-2026.md) | Versiones reales verificadas, toolkit, huecos |
| [Cobertura-fuentes.md](_sistema/Cobertura-fuentes.md) | Qué fuente aporta qué y qué falta |

---

## Índices generados — qué responden

**El caso central** (ves un puerto abierto y no sabés qué hacer) **no se resuelve acá**: está en
el router, [`guia/router-escenarios.md`](guia/router-escenarios.md). Este README no duplica ese
flujo de decisión.

Los índices de `vault/` son la referencia de **precedentes**, no de decisiones:

| Índice | Qué responde |
| --- | --- |
| [vault/indices/Puertos.md](vault/indices/Puertos.md) | puerto → máquinas que lo tenían |
| [vault/indices/Servicios.md](vault/indices/Servicios.md) | etiqueta de nmap → máquinas |
| [vault/indices/Tecnicas.md](vault/indices/Tecnicas.md) | técnica → máquinas + receta de comandos |
| [vault/indices/Maquinas.md](vault/indices/Maquinas.md) | 565 máquinas + marca OSCP |
| [vault/indices/Referencias.md](vault/indices/Referencias.md) | índice de WADComs y LOLBAS (el espejo GTFOBins por binario **no existe**) |

> Leé siempre la columna **Real** de la nota de puerto (lo que corría de verdad), **no** la
> etiqueta de nmap: el 5000 aparece como `upnp` pero en 21 de 23 máquinas era otra cosa
> (Docker Registry, GitLab, HTTP…).

```bash
# Atajos con Obsidian abierto
#   Ctrl+O        → saltar a un puerto/técnica/binario por nombre
#   Ctrl+Shift+F  → búsqueda full-text en todo el vault
#   Ctrl+E        → alternar edición / vista previa
```

---

## Datos duros del examen

| Dato | Valor |
| --- | --- |
| Máquinas independientes | 3 × 20 pts = **60 pts** |
| Set de Active Directory | 10 + 10 + 20 = **40 pts** |
| Aprobación | **70 / 100** |
| Duración | **23 h 45 min** |
| Reporte (posterior) | **24 h** |
| Reverts | 24 (reiniciables 1 vez) |
| AD | modelo *assumed breach* — **te dan usuario y contraseña** |
| AD parcial | **sí**, los 40 pts se otorgan por partes |
| Puntos bonus | **NO existen** |

---

## Por qué está indexado por técnica

Las máquinas del examen son **propias de OffSec** y no las viste nunca. Un archivo de
writeups indexado por nombre de máquina no sirve durante el examen, porque ninguna de
esas máquinas va a aparecer.

Lo que sí se consulta bajo presión es una técnica: *"¿cómo escalo desde un servicio con
configuración escribible?"*. Por eso el playbook está indexado por **problema**, no por
**objetivo**.

El corpus son **565 writeups de HTB** descargados del `sitemap.xml` de 0xdf.
**68 están en el listado OSCP** de TJ Null (54 HTB + 14 Vulnlab, que migró a HTB en 2025);
el frontmatter lo marca con `en_lista_oscp`.

El valor no es el comando suelto, sino **cuándo funciona y cuándo no**. Ejemplo real:

> Buscá `PrintSpoofer` → máquina **Cereal**: explica que **falló** porque era Server Core,
> sin spooler y sin 135/TCP saliente; terminó usando **GenericPotato**.

```bash
python3 _sistema/herramientas/buscar.py PrintSpoofer -v
python3 _sistema/herramientas/buscar.py kerberoasting -v --oscp
```

---

## Mantenimiento

> ⚠️ **No corras ningún generador mientras falte `_sistema/datos/`.** Sin sus entradas producen
> salida parcial o vacía y **sobrescriben** la capa generada que hoy sí sirve. Primero hay que
> recuperar y versionar `_sistema/datos/`; después, respaldar `vault/indices/` y recién entonces
> regenerar. Ver [`_sistema/SALUD-DOCUMENTAL.md`](_sistema/SALUD-DOCUMENTAL.md).

```bash
# Verificación de enlaces y estructura de la primera rebanada (segura, solo lectura)
python3 _sistema/herramientas/verificar-enlaces.py --scope first-slice

# ⚠️ NO ejecutar: falta _sistema/datos/ (sobrescribe la capa generada)
#   python3 _sistema/herramientas/construir-vault.py
#   python3 _sistema/herramientas/construir-referencias.py
#   python3 _sistema/herramientas/indice.py
#   python3 _sistema/herramientas/marcar-oscp.py

# Bajar/actualizar writeups (necesita internet, es reanudable). No usa _sistema/datos/.
python3 _sistema/herramientas/raspar.py --solo-htb --workers 4
```

> **Fuente de las reglas**: *OSCP+ Exam Guide* de OffSec (página del 20-abr-2026). Las citas
> de `guia/00-reglas-examen.md` son verbatim. Verificá contra el original:
> `help.offsec.com/hc/en-us/articles/360040165632`
>
> **Estado de recuperación: HTTP 403** (observado el 30-sep-2026). La página no es accesible, así
> que el contenido de reglas no se pudo reverificar contra el original. Por eso todo el material
> **nuevo** del vault se etiqueta `pendiente-politica` y no se derivan conclusiones de política a
> partir de esta fuente. Ver [`_sistema/SALUD-DOCUMENTAL.md`](_sistema/SALUD-DOCUMENTAL.md).

---

## Advertencia de honestidad intelectual

Este playbook fue redactado con asistencia de IA a partir de documentación verificada y de
los binarios instalados en esta máquina.

La política de OffSec prohíbe el uso de IA **durante el examen**. Este documento no se
consulta así: es material de estudio previo. Este vault **no tiene plugins de IA** y no los
agregues.

La regla que te protege de verdad no es la procedencia del texto, es esta:
**si no entendés una línea, no la uses.** Un comando copiado sin comprensión falla en el
peor momento y no lo podés adaptar cuando el objetivo se comporta distinto.

Cada comando de este playbook es tuyo en el momento en que lo corriste, lo rompiste, lo
arreglaste y lo entendiste. Hasta entonces, es texto ajeno.
