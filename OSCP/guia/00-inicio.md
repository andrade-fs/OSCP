# OSCP — punto de entrada

Vault de estudio y consulta. **565 writeups de máquinas HTB**, indexados por
**puerto**, **servicio** y **técnica**.

---

## Durante el examen: el router

**La lógica de decisión no vive acá.** Vive en un único lugar:
[`router-escenarios.md`](router-escenarios.md). Entrás con una **observación** y salís con el
documento correcto, la evidencia a registrar y la condición de parqueo.

| Observación | Escenario del router |
| --- | --- |
| Puertos abiertos, sin prioridad clara | 1 — Triage |
| Web, panel o API | 2 — Objetivo web |
| Shell Linux / Windows | 3 y 4 — Escalada |
| Set de AD con credenciales | 5 — AD con credenciales |
| Hash NTLM, TGT o PFX | 6 — Hashes, TGT y PFX |
| Una segunda red visible | 7 — Pivoting |
| Subir o bajar archivos | 8 — Transferencia y payloads |
| Kerberos con errores raros | 9 — Kerberos y entorno |
| Capturar evidencia | 10 — Reporte y evidencia |
| Bloqueo | 11 — Estoy trabado |

Si agregás un camino de decisión, va en el router, no acá. Este documento es el **manual de
uso**: cómo buscar, cómo leer y cómo escribir en el vault.

### El insumo que más se usa: la nota de puerto

`Ctrl+O` (quick switcher) → el número → Enter.

```
Ctrl+O  →  "5000"  →  vault/indices/Puertos/5000.md
```

Leé la columna **Real**, no la etiqueta de nmap: nmap adivina por heurística y **se equivoca
mucho**.

| Puerto | nmap dice | Lo que corría de verdad |
| --- | --- | --- |
| 5000 | `upnp` (21 de 23 veces) | Website, HTTP, **Docker Registry**, **GitLab**, keystone |
| 445 | `microsoft-ds` (123 de 123) | SMB |
| 8080 | `http-proxy` | Tomcat, GitBucket, Teampass, icinga |

La columna *Real* sale del **encabezado de la sección** del writeup
(`### Let's Chat - TCP 5000`), no de la etiqueta de nmap. Es lo que el autor
encontró al enumerar.

---

## Leer el vault SIN Obsidian (desde la terminal)

Si todavía no instalaste Obsidian, **todo el contenido es legible igual**. Los
enlaces `[[...]]` no se van a renderizar como links, pero el texto y los comandos
están completos.

```bash
cd ~/OSCP

# 1) Ver un puerto: ¿qué máquinas lo tenían y qué era realmente?
less vault/indices/Puertos/5000.md

# 2) Buscar una técnica con contexto en todo el corpus
python3 _sistema/herramientas/buscar.py PrintSpoofer -v
python3 _sistema/herramientas/buscar.py kerberoasting -v --oscp

# 3) Ver un binario de Windows en las referencias (LOLBAS está generado)
less vault/indices/Referencias/LOLBAS/Certutil.exe.md

# 4) GTFOBins: SOLO existe el índice, no las notas por binario
less vault/indices/Referencias/GTFOBins.md

# 5) Buscar a lo bruto en todo el vault (rápido, con ripgrep)
rg -l 'seimpersonate' .                       # qué archivos lo mencionan
rg -n -C 3 'PrintSpoofer' vault/indices/Tecnicas/           # con contexto
rg -l 'GodPotato|JuicyPotato' vault/indices/Referencias/    # regex

# 6) Los índices maestros
less Puertos.md Tecnicas.md Servicios.md Maquinas.md Referencias.md
```

### Instalar Obsidian

Está en el repositorio de Kali:

```bash
sudo apt install -y obsidian
```

Después abrí Obsidian y elegí **"Open folder as vault"** → tu copia del vault. La
configuración ya está puesta en `.obsidian/`, así que va a tomar el tema, los
marcadores y el grafo sin que toques nada.

> **Rutas no conciliadas**: esta guía y el resto de la documentación nombran `~/OSCP`; el
> instalador (`OSCP-setup/lib.sh`) crea `~/Documentos/OSCP`. Verificá cuál existe en tu máquina
> antes de copiar cualquier comando con ruta. Estado: [`../_sistema/SALUD-DOCUMENTAL.md`](../_sistema/SALUD-DOCUMENTAL.md).

### Atajos que sirven con Obsidian abierto

| Atajo | Para qué |
| --- | --- |
| `Ctrl+O` | **El más importante**: escribir un puerto, una técnica o un binario y saltar ahí |
| `Ctrl+Shift+F` | Búsqueda full-text en todo el vault |
| `Ctrl+P` | Paleta de comandos |
| `Ctrl+E` | Alternar entre edición y vista previa |

---

## Atajos operativos (sin lógica de decisión)

Esto no es un árbol de decisión: es la lista de documentos que vas a usar en el examen. Para
**qué hacer** según lo que observás, andá al [router](router-escenarios.md).

| Documento | Para qué |
| --- | --- |
| [router-escenarios.md](router-escenarios.md) | **La decisión**: observación → documento correcto |
| `vault/indices/Puertos/<número>` | Precedentes de un puerto: qué corría de verdad |
| `vault/indices/Servicios/<nombre>` | Precedentes por etiqueta de servicio |
| `vault/indices/Tecnicas/<nombre>` | Precedentes por técnica + receta (¡muchas están en blanco!) |
| [LPE-Linux](lpe/LPE-Linux.md) · [LPE-Windows](lpe/LPE-Windows.md) | Orden de ataque al escalar |
| [AD-walkthrough](walkthroughs/AD-walkthrough.md) | Recorrido del set de AD, de cero a DA |
| [Standalone-walkthrough](walkthroughs/Standalone-walkthrough.md) | Recorrido de las 3 sueltas |
| [00-dashboard](../examen/00-dashboard.md) | Panel de examen: 1 doc por máquina |
| [08-reporte-y-evidencia](08-reporte-y-evidencia.md) | Qué capturar y cuándo |
| [plantillas/](../plantillas/como-usar-plantillas.md) | Tarjetas para registrar algo nuevo |
| [Entorno](Entorno.md) | Kerberos, DNS, `/etc/hosts`, proxychains |

> **Aviso sobre la capa generada**: el `vault/` conserva notas en blanco (217 en total) y el
espejo GTFOBins por binario **no existe**. Si un enlace abre vacío, no es tu error: usá el
cheatsheet o la guía canónica. Detalle y conteos: [`../_sistema/SALUD-DOCUMENTAL.md`](../_sistema/SALUD-DOCUMENTAL.md).

---

## Comandos copy-paste

**23 técnicas figuran con recetario** en su propia nota, en la sección *Comandos*.
En [[Tecnicas]] la columna **Receta** te marca cuáles lo tienen.

> ⚠️ **Pero 6 de esas 23 notas están en blanco** en la capa generada: `kerberoasting`,
> `pass-the-hash`, `dcsync`, `delegacion-restringida`, `suid` y `lsass`. El enlace existe y
> abre vacío. Para esos temas, usá el cheatsheet correspondiente
> ([impacket](../cheatsheets/impacket.md), [nxc](../cheatsheets/nxc.md),
> [adcs-esc](../cheatsheets/adcs-esc.md)) o la guía canónica.

Con recetario:

| Categoría | Técnicas |
| --- | --- |
| **Credenciales AD** | kerberoasting · asreproast · password-spraying · pass-the-hash · pass-the-ticket · dcsync · gpp |
| **Estructura AD** | rbcd · delegacion-sin-restriccion · delegacion-restringida · shadow-credentials · adcs |
| **LPE Linux** | sudo · suid · capabilities · cron · nfs-no_root_squash · docker-group · credenciales-en-archivos |
| **LPE Windows** | seimpersonate · unquoted-service-path · alwaysinstallelevated · lsass |

*(En negrita no: las 6 listadas arriba están en blanco en disco.)*

---

## Referencias externas — qué está espejado y qué no

**El espejo está incompleto.** Estos son los números reales:

| Espejo | Índice | Notas individuales | Estado |
| --- | --- | --- | --- |
| [[GTFOBins]] | ✔ | **0 de 458** | El directorio por binario **no existe**: no hay referencia local por binario. |
| [[WADComs]] | ✔ | 103 (35 **en blanco**) | Parcial: 68 abren con contenido. |
| [[LOLBAS]] | ✔ | 248 (81 **en blanco**) | Parcial: 167 abren con contenido. |

**Por qué local igual sirve parcialmente**: internet durante el examen es un punto único
de falla, y Obsidian no indexa sitios web. Buscar `certutil` en el vault no
encontraría nada que esté solo en LOLBAS.

**Alternativa para GTFOBins**: el índice lista los binarios y sus funciones, pero el código por
contexto (`sudo`/`suid`/`capabilities`) **no está en el vault**. Para eso, ver las alternativas
documentadas en [`03-privesc-linux.md`](03-privesc-linux.md) y [`lpe/LPE-Linux.md`](lpe/LPE-Linux.md).

El catálogo de enlaces online, con la advertencia de cumplimiento sobre IA, está en
**[[Referencias]]**. Conteos y defectos: [`../_sistema/SALUD-DOCUMENTAL.md`](../_sistema/SALUD-DOCUMENTAL.md).

### Antes de copiar y pegar

Los comandos usan placeholders. Reemplazalos **siempre**:

| Placeholder | Significa |
| --- | --- |
| `<DC_IP>` | IP del Domain Controller |
| `<TU_IP>` | Tu IP de Kali en la VPN |
| `<DOMINIO>` | Dominio en minúsculas: `gesuga.local` |
| `<USER>` / `<PASS>` | Credenciales válidas |
| `<IP>` | Cualquier objetivo |
| `<NTHASH>` | Hash NTLM (32 hex) |

Detalle completo y los errores típicos de cada uno: **[[Entorno]]**.

> Un comando copiado sin entender **falla en el peor momento** y no lo podés
> adaptar cuando el objetivo se comporta distinto. Cada receta incluye una tabla
> de *errores típicos* justamente para eso.

---

## Lo que este vault NO te da

Te lo digo derecho, porque es la diferencia entre usarlo bien y confiar de más.

**Un puerto abierto no te dice cuál es la vulnerabilidad.** Te dice *dónde
enumerar*. Que el 5000 esté abierto no significa "explotá X": significa "en 23
máquinas el 5000 alojaba estas apps, y así se atacaron".

El vault te da **precedentes**, no respuestas. Vos seguís teniendo que:

1. Enumerar la aplicación concreta que está corriendo ahí.
2. Decidir si el precedente aplica a **esta** versión, con **esta** configuración.

Un writeup de otra máquina con el mismo puerto no implica la misma vulnerabilidad.
Implica que vale la pena mirar en esa dirección.

---

## Búsqueda por texto (para estudio)

Cuando no sabés el nombre exacto de lo que buscás:

```bash
cd ~/OSCP

# Todas las referencias a una técnica, con el comando y el output alrededor
python3 _sistema/herramientas/buscar.py PrintSpoofer -v

# Solo máquinas del listado OSCP
python3 _sistema/herramientas/buscar.py kerberoasting -v --oscp

# Regex
python3 _sistema/herramientas/buscar.py "GodPotato|JuicyPotato|PrintSpoofer" --nombres

# Frases con espacios: busca también las variantes con guion y guion bajo
python3 _sistema/herramientas/buscar.py "pass the hash" --nombres
```

**El valor no es el comando, es cuándo falla.** Ejemplo real del corpus:

> Buscá `PrintSpoofer` → **Cereal**. El writeup explica que PrintSpoofer **no
> funcionó**: Server Core, sin servicio de spooler, sin 135/TCP saliente. Terminó
> usando GenericPotato.

Un cheatsheet te da el comando. El writeup te da el criterio.

---

## Estructura del vault

```
OSCP/
├── README.md              ← portada / índice general
│
├── guia/                  ← EL PLAYBOOK (leer en orden)
│   ├── router-escenarios.md     ← 🎯 EL ROUTER (observación → qué hacer)
│   ├── 00-inicio.md             ← estás acá (manual de uso)
│   ├── 00-reglas-examen.md      restricciones (leer antes de rendir)
│   ├── 01-metodologia.md        el bucle de trabajo y las 23 h 45 min
│   ├── 02-enumeracion-servicios.md
│   ├── 03-privesc-linux.md
│   ├── 04-privesc-windows.md
│   ├── 05-active-directory.md   40 pts
│   ├── 06-payloads-shells-transferencia.md
│   ├── 07-pivoting.md
│   ├── 08-reporte-y-evidencia.md
│   ├── 09-web.md                ataques web (LFI, SQLi, upload, APIs…)
│   ├── Entorno.md               krb5.conf, /etc/hosts, DNS, proxychains
│   ├── verificado-2026.md       entorno verificado (versiones, toolkit)
│   ├── walkthroughs/
│   │   ├── AD-walkthrough.md          set de 3 máquinas: de cero a Domain Admin
│   │   └── Standalone-walkthrough.md  las sueltas: recon → foothold → LPE → flags
│   └── lpe/
│       ├── LPE-Linux.md          orden de ataque (Linux)
│       └── LPE-Windows.md        orden de ataque (Windows)
│
├── cheatsheets/           ← chuletas (nxc, impacket, potatoes, web…)
│
├── plantillas/            ← tarjetas reutilizables (servicio, técnica)
│
├── vault/                 ← GENERADO: conservado, NO reproducible
│   ├── indices/                (217 notas en blanco; GTFOBins por binario ausente)
│   │   ├── Puertos.md + Puertos/         puerto → máquinas
│   │   ├── Servicios.md + Servicios/     etiqueta nmap → máquinas
│   │   ├── Tecnicas.md + Tecnicas/       técnica → máquinas + receta
│   │   ├── Maquinas.md                   565 máquinas + marca OSCP
│   │   └── Referencias.md + Referencias/ solo WADComs y LOLBAS (parciales)
│   └── corpus/                 ← 565 writeups + _indice/
│
├── _sistema/              ← INTERNO (scripts, cobertura, salud documental)
│   └── datos/             ← ❌ AUSENTE: entradas del generador
├── Inbox/ · Adjuntos/     ← uso de Obsidian
```

**Marcas en las tablas**:

- **sí** en la columna OSCP = la máquina está en el listado de TJ Null (pestaña PWK V3)
- **[OSCP]** en los listados = lo mismo
- Son 68 en total: 54 de HTB más 14 de Vulnlab (que migró a HTB en 2025)

---

## Advertencias que no son opcionales

### Nada de IA durante el examen

De la guía oficial de OffSec, textual:

> "using LLMs and AI chatbots (OffSec KAI, ChatGPT, Deepseek, Gemini, etc.) is
> strictly prohibited"

Este vault **no tiene plugins de IA** y no los agregues. Obsidian con búsqueda
normal es una herramienta de notas: está permitido. Un plugin que consulte un
modelo, no.

También dice:

> "While you may use Discord as a resource for searching for information during
> the exam, under no circumstances are you permitted to seek or receive
> assistance from others"

Buscar **información** está permitido. Pedir **ayuda a una persona**, no. Tus notas
entran en la primera categoría.

### Antes de rendir

1. Repasá `00-reglas-examen.md` — sobre todo la restricción de Metasploit (una
   sola máquina, y `check` cuenta como uso).
2. Verificá que las herramientas del examen estén instaladas y funcionando
   (`../guia/verificado-2026.md`): `ligolo-ng`, `chisel`, `ncat`, `sshpass`,
   `kerbrute`, `coercer`, `enum4linux-ng`. Ya están todas puestas y verificadas.
3. Verificá el **toolkit de escalada** (`~/examen/tools/`), sobre todo
   `win/potato_check64.exe` (dice qué Potato aplica según la máquina) y
   `win/FullPowers.exe` (recuperar privilegios de un token restringido).
   > ⚠️ Ruta **no conciliada**: el instalador crea `~/Documentos/Tools`. Verificá cuál existe.
4. Verificá que `nxc` responde: `nxc --version` → 1.5.1. Ya no hay shim roto.
5. Probá este vault **offline**. Que Obsidian abra y que `Ctrl+O` encuentre un puerto.
6. Tené el plan B de contingencia (la guía de OffSec lo pide explícitamente):
   internet alternativo, la VM respaldada, energía asegurada.

---

## Mantenimiento

> ⚠️ **No ejecutes los generadores mientras falte `_sistema/datos/`.** Producen salida parcial o
> vacía y **sobrescriben** la capa generada que hoy sí sirve. Primero recuperá y versioná
> `_sistema/datos/`; después respaldá `vault/indices/` y recién entonces regenerá. Ver
> [`../_sistema/SALUD-DOCUMENTAL.md`](../_sistema/SALUD-DOCUMENTAL.md).

| Quiero… | Comando |
| --- | --- |
| Verificar enlaces y estructura de la primera rebanada (seguro, offline) | `python3 _sistema/herramientas/verificar-enlaces.py --scope first-slice` |
| Ver el estado de la capa generada | leer [`../_sistema/SALUD-DOCUMENTAL.md`](../_sistema/SALUD-DOCUMENTAL.md) |
| Actualizar el corpus con writeups nuevos | `python3 _sistema/herramientas/raspar.py --solo-htb --workers 4` |
| Regenerar los índices de texto | ❌ **no ejecutar**: falta `_sistema/datos/` (`indice.py`) |
| Regenerar puertos/servicios/técnicas | ❌ **no ejecutar**: falta `_sistema/datos/` (`construir-vault.py`) |
| Recalcular la marca OSCP | ❌ **no ejecutar**: falta `_sistema/datos/` (`marcar-oscp.py`) |

El raspador es **reanudable**: solo baja lo que falta, así que podés correrlo
cuando quieras sin miedo a repetir trabajo.
