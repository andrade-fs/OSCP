# OSCP — punto de entrada

Vault de estudio y consulta. **565 writeups de máquinas HTB**, indexados por
**puerto**, **servicio** y **técnica**.

---

## Durante el examen: el flujo

Tenés un puerto abierto y no sabés qué hacer con él. Tres pasos.

### 1. Abrí la nota del puerto

`Ctrl+O` (quick switcher) → escribí el número → Enter.

```
Ctrl+O  →  "5000"  →  vault/indices/Puertos/5000.md
```

### 2. Leé la columna **Real**, no la etiqueta de nmap

Esta es la parte que importa. nmap adivina por heurística y **se equivoca mucho**.

| Puerto | nmap dice | Lo que corría de verdad |
| --- | --- | --- |
| 5000 | `upnp` (21 de 23 veces) | Website, HTTP, **Docker Registry**, **GitLab**, keystone |
| 445 | `microsoft-ds` (123 de 123) | SMB |
| 8080 | `http-proxy` | Tomcat, GitBucket, Teampass, icinga |

La columna *Real* sale del **encabezado de la sección** del writeup
(`### Let's Chat - TCP 5000`), no de la etiqueta de nmap. Es lo que el autor
encontró al enumerar.

### 3. Abrí la máquina que se parezca

Si el *Real* dice `Docker Registry`, abrí esa máquina y mirá cómo la atacó. Si tu
objetivo tiene un Docker Registry en el 5000, ahí tenés el camino.

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

# 3) Ver un binario en las referencias
less vault/indices/Referencias/LOLBAS/Certutil.exe.md
less vault/indices/Referencias/GTFOBins/find.md

# 4) Buscar a lo bruto en todo el vault (rápido, con ripgrep)
rg -l 'seimpersonate' .                       # qué archivos lo mencionan
rg -n -C 3 'PrintSpoofer' vault/indices/Tecnicas/           # con contexto
rg -l 'GodPotato|JuicyPotato' vault/indices/Referencias/    # regex

# 5) Los índices maestros
less Puertos.md Tecnicas.md Servicios.md Maquinas.md Referencias.md
```

### Instalar Obsidian

Está en el repositorio de Kali:

```bash
sudo apt install -y obsidian
```

Después abrí Obsidian y elegí **"Open folder as vault"** → `~/OSCP`. La
configuración ya está puesta en `.obsidian/`, así que va a tomar el tema, los
marcadores y el grafo sin que toques nada.

### Atajos que sirven con Obsidian abierto

| Atajo | Para qué |
| --- | --- |
| `Ctrl+O` | **El más importante**: escribir un puerto, una técnica o un binario y saltar ahí |
| `Ctrl+Shift+F` | Búsqueda full-text en todo el vault |
| `Ctrl+P` | Paleta de comandos |
| `Ctrl+E` | Alternar entre edición y vista previa |

---

## Tabla de decisión

| Lo que ves | Dónde ir |
| --- | --- |
| Un puerto abierto | `vault/indices/Puertos/<número>` |
| Un servicio (SMB, LDAP, WinRM…) | `vault/indices/Servicios/<nombre>` |
| Una técnica (kerberoast, SUID, PrintSpoofer…) | `vault/indices/Tecnicas/<nombre>` |
| Un **puerto filtrado** | `vault/indices/Puertos/<n>` → la nota te avisa: es **pivoting**, no explotación directa |
| Tengo shell y soy usuario común | [[LPE-Linux]] o [[LPE-Windows]] |
| Kerberos falla con errores raros | [[Entorno]] |
| No sé por dónde empezar | [[Maquinas]] → filtrá por OSCP |
| Estoy en el set de AD (40 pts) | [[AD-walkthrough]] — recorrido de cero a DA |
| **Empiezo el examen** | [[00-dashboard]] — panel de examen (1 doc por máquina) |
| Tengo una máquina suelta (20 pts) | [[Standalone-walkthrough]] — recon → foothold → LPE → flags |
| Tengo una web y no sé por dónde | [[09-web]] — ataques web (LFI, upload, SQLi, APIs…) |
| Un binario y querés sacarle shell | `vault/indices/Referencias/GTFOBins/<binario>` |
| Un binario de Windows para descargar/ejecutar | `vault/indices/Referencias/LOLBAS/<binario>` |
| Tenés un hash, un TGT o un PFX | `vault/indices/Referencias/WADComs/` |
| Necesitás algo más profundo | [[Referencias]] |

---

## Comandos copy-paste

**23 técnicas tienen recetario completo** en su propia nota, en la sección
*Comandos*. Buscás la técnica y tenés los comandos exactos más las máquinas donde
se usó.

En [[Tecnicas]] la columna **Receta** te marca cuáles lo tienen.

Con recetario:

| Categoría | Técnicas |
| --- | --- |
| **Credenciales AD** | kerberoasting · asreproast · password-spraying · pass-the-hash · pass-the-ticket · dcsync · gpp |
| **Estructura AD** | rbcd · delegacion-sin-restriccion · delegacion-restringida · shadow-credentials · adcs |
| **LPE Linux** | sudo · suid · capabilities · cron · nfs-no_root_squash · docker-group · credenciales-en-archivos |
| **LPE Windows** | seimpersonate · unquoted-service-path · alwaysinstallelevated · lsass |

---

## Referencias externas — espejadas localmente

Tres bases de datos convertidas a notas, **buscables offline**. `Ctrl+O` y el
nombre del binario.

| Espejo | Notas | Para qué |
| --- | --- | --- |
| [[GTFOBins]] | 458 binarios | Binarios Unix: shell y lectura por contexto (`sudo`, `suid`, `capabilities`) |
| [[WADComs]] | 103 recetas | Comandos de AD ordenados por **lo que tenés** |
| [[LOLBAS]] | 248 binarios | Binarios legítimos de Windows usables como atacante |

**Por qué local y no solo un link**: internet durante el examen es un punto único
de falla, y Obsidian no indexa sitios web. Buscar `certutil` en el vault no
encontraría nada que esté solo en LOLBAS.

El catálogo completo de enlaces online, con la advertencia de cumplimiento sobre
IA, está en **[[Referencias]]**.

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
│   ├── 00-inicio.md             ← estás acá (flujo de examen)
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
├── vault/                 ← GENERADO: no editar a mano
│   ├── indices/
│   │   ├── Puertos.md + Puertos/      puerto → máquinas  ← FLUJO DE EXAMEN
│   │   ├── Servicios.md + Servicios/  etiqueta nmap → máquinas
│   │   ├── Tecnicas.md + Tecnicas/    técnica → máquinas + receta
│   │   ├── Maquinas.md                565 máquinas + marca OSCP
│   │   └── Referencias.md + Referencias/  GTFOBins, WADComs, LOLBAS
│   └── corpus/                ← 565 writeups + _indice/
│
├── _sistema/              ← INTERNO (datos, scripts, cobertura)
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
4. Verificá que `nxc` responde: `nxc --version` → 1.5.1. Ya no hay shim roto.
5. Probá este vault **offline**. Que Obsidian abra y que `Ctrl+O` encuentre un puerto.
6. Tené el plan B de contingencia (la guía de OffSec lo pide explícitamente):
   internet alternativo, la VM respaldada, energía asegurada.

---

## Mantenimiento

| Quiero… | Comando |
| --- | --- |
| Actualizar el corpus con writeups nuevos | `python3 _sistema/herramientas/raspar.py --solo-htb --workers 4` |
| Regenerar los índices de texto | `python3 _sistema/herramientas/indice.py` |
| Regenerar puertos/servicios/técnicas | `python3 _sistema/herramientas/construir-vault.py` |
| Recalcular la marca OSCP | `python3 _sistema/herramientas/marcar-oscp.py` |
| Agregar técnicas a vigilar | editar `_sistema/datos/tecnicas.txt` y regenerar |

El raspador es **reanudable**: solo baja lo que falta, así que podés correrlo
cuando quieras sin miedo a repetir trabajo.
