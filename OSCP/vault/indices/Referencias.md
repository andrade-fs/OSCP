# Referencias

[[00-inicio|Inicio]] · [[Puertos|Puertos]] · [[Servicios|Servicios]] · [[Tecnicas|Tecnicas]] · [[Maquinas|Maquinas]]

Dos capas: **espejos locales** (funcionan sin internet y son buscables en Obsidian)
y **enlaces online** (para cuando necesitás algo más profundo).

---

## 1. Espejos locales — buscables offline

Estos están **dentro del vault**, convertidos a notas. `Ctrl+O` y buscás el
nombre. No dependen de internet.

| Espejo | Notas | Para qué |
| --- | --- | --- |
| [[GTFOBins]] | 458 binarios | Binarios Unix: cómo sacar shell o leer archivos con sudo/SUID |
| [[WADComs]] | 103 recetas | Comandos de Active Directory, ordenados por **lo que tenés** |
| [[LOLBAS]] | 248 binarios | Binarios legítimos de Windows usables como atacante |

### Por qué estos tres y no un link

Durante el examen, **depender de internet es un punto único de falla**. Y Obsidian
no indexa sitios web: buscar `certutil` en el vault no encontraría nada que esté
solo en LOLBAS. Con los espejos locales, `Ctrl+O "certutil"` te lleva directo a
los comandos.

Los tres son **GPL-3.0** con licencia explícita, así que espejarlos localmente es
legal. Cada nota lleva la atribución y el link al original.

### El detalle que se pierde cuando copiás de memoria

GTFOBins da **código distinto según el contexto**. Mirá el caso de `find`:

| Contexto | Comando |
| --- | --- |
| `sudo` | `find . -exec /bin/sh \; -quit` |
| `suid` | `find . -exec /bin/sh **-p** \; -quit` |

Ese `-p` es la diferencia entre shell de root y shell de usuario común. **Por eso
copiá desde la nota del binario, no de memoria.**

---

## 2. Enlaces online — curados por propósito

### Notas de un OSCP completo (todo en uno)

| Recurso | URL | Para qué |
| --- | --- | --- |
| **oscp.adot8.com** | https://oscp.adot8.com/ | Notas de un OSCP real: **enumeración por servicio/puerto**, web apps, AD, LPE Windows/Linux. Su sección *Services* alimenta [`02-enumeracion-servicios.md`](../../guia/02-enumeracion-servicios.md). |
| **oscp.adot8.com — llms.txt** | https://oscp.adot8.com/llms.txt | Índice completo (203 páginas) para consultar/descargar |

### Cuando estás trabado en Active Directory

| Recurso | URL | Para qué |
| --- | --- | --- |
| **The Hacker Recipes** | https://www.thehacker.recipes/ | La referencia de AD más ordenada. Por ataque, con pasos. |
| **ADSecurity.org** | https://adsecurity.org/ | Sean Metcalf. Lo más profundo en AD y Kerberos. |
| **HackTricks — AD Methodology** | https://book.hacktricks.wiki/en/windows-hardening/active-directory-methodology/index.html | Checklist de enumeración y ataque |
| **GOAD** | https://github.com/Orange-Cyberdefense/GOAD | Laboratorio de AD vulnerable, para practicar los caminos completos |

### Cuando tenés shell en Windows

| Recurso | URL | Para qué |
| --- | --- | --- |
| **HackTricks — Windows Local Privilege Escalation** | https://book.hacktricks.wiki/en/windows-hardening/windows-local-privilege-escalation/index.html | El listado más completo de vectores de LPE |
| **LOLBAS** (online) | https://lolbas-project.github.io/ | Versión web, con más contexto que el espejo |
| **Ultimate AppLocker Bypass List** | https://github.com/api0cradle/UltimateAppLockerByPassList | Bypass de AppLocker |
| **Privilege Escalation Checklist** | https://github.com/netbiosX/Checklists/blob/master/Windows-Privilege-Escalation.md | Checklist ordenada |

### Cuando tenés shell en Linux

| Recurso | URL | Para qué |
| --- | --- | --- |
| **HackTricks — Linux Privilege Escalation** | https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/index.html | El listado más completo de vectores |
| **GTFOBins** (online) | https://gtfobins.github.io/ | Versión web, con buscador |
| **linux-exploit-suggester** | https://github.com/mzet-/linux-exploit-suggester | Exploits de kernel según versión |

### Cuando necesitás un payload o una shell

| Recurso | URL | Para qué |
| --- | --- | --- |
| **revshells.com** | https://www.revshells.com/ | Generador de reverse shells, con URL-encoding y base64 |
| **PayloadsAllTheThings** | https://github.com/swisskyrepo/PayloadsAllTheThings | Payloads por tipo de vulnerabilidad |
| **0xdf cheatsheets** | https://0xdf.gitlab.io/cheatsheets/ | Ya están parcialmente en el vault (ver más abajo) |

### Cuando tenés un hash o algo cifrado

| Recurso | URL | Para qué |
| --- | --- | --- |
| **CrackStation** | https://crackstation.net/ | Rainbow tables, hashes comunes |
| **Hashes.com** | https://hashes.com/en/decrypt/hash | Ídem, con API |
| **CyberChef** | https://gchq.github.io/CyberChef/ | Decodificar cualquier cosa: base64, hex, JWT, XOR |
| **Hashcat example hashes** | https://hashcat.net/wiki/doku.php?id=example_hashes | **Identificar** un hash: buscás el prefijo y sabés el `-m` |

### Cuando necesitás encontrar un exploit

| Recurso | URL | Para qué |
| --- | --- | --- |
| **Exploit-DB** | https://www.exploit-db.com/ | La misma base que `searchsploit` |
| **NVD** | https://nvd.nist.gov/ | El CVE oficial, con CVSS y referencias |
| **GitHub Advisory** | https://github.com/advisories | Avisos de dependencias |

### Para aprender de writeups

| Recurso | URL | Para qué |
| --- | --- | --- |
| **0xdf** | https://0xdf.gitlab.io/ | **Ya está en el vault**: `vault/corpus/htb/` |
| **IppSec** | https://www.youtube.com/@ippsec | Video-writeups. Buscá la máquina, mirá el razonamiento |
| **HTB writeups oficiales** | https://app.hackthebox.com/machines | Solo máquinas retiradas |

---

## 3. Lo que ya tenés local y quizá no sabías

El vault ya contiene material de referencia que no necesita internet:

| Recurso | Dónde | Qué es |
| --- | --- | --- |
| Writeups de 565 máquinas | `vault/corpus/htb/` | 28.963 bloques de código |
| Chuletas de 0xdf | `vault/corpus/otros/chuleta-*` | `smb-enum`, `tunneling`, `chisel`, `offsec` |
| Índice por puerto | [[Puertos]] | 498 puertos → qué máquinas lo tenían |
| Índice por técnica | [[Tecnicas]] | 165 técnicas, 23 con recetario de comandos |
| Chuletas de herramientas | `cheatsheets/` | nxc, impacket, certipy v5 |

---

## 4. ADVERTENCIA DE CUMPLIMIENTO — leé esto

De la guía oficial del examen, textual:

> "using LLMs and AI chatbots (OffSec KAI, ChatGPT, Deepseek, Gemini, etc.) is
> strictly prohibited. This is considered receiving third-party help and
> sharing exam information, both of which violate our Academic Policy."

### Qué significa en la práctica

| Permitido | Prohibido |
| --- | --- |
| Leer documentación: HackTricks, WADComs, GTFOBins, este vault | Usar un chatbot: ChatGPT, Claude, Gemini, DeepSeek |
| Buscar en Google/DuckDuckGo | Usar un asistente de IA integrado en cualquier sitio |
| Leer un writeup de 0xdf | Pedirle ayuda a una persona (Discord, foro, chat) |
| Buscar información en Discord | |

El propio reglamento lo aclara:

> "While you may use Discord as a resource for **searching for information**
> during the exam, under no circumstances are you permitted to **seek or receive
> assistance from others** on the platform."

**Buscar información = permitido. Pedir ayuda a una persona o a una IA = falta.**

### Sobre estas fuentes específicamente

- **HackTricks**, **WADComs**, **GTFOBins**, **LOLBAS** son **documentación**.
  Leerlas es exactamente "searching for information". Está permitido.
- HackTricks **vende cursos de seguridad de IA** — eso es publicidad, no una
  función del sitio. No encontré un asistente de IA integrado en el sitio.
- ⚠️ **Pero existen wrappers de terceros que envuelven el contenido de HackTricks
  en un chat con IA.** Si el sitio que abrís tiene una caja de chat, **no la uses**.
  No importa que el contenido de fondo sea el mismo.

### La regla práctica

> **Si tiene una caja donde escribís una pregunta en lenguaje natural y te
> responde, es una IA. No la uses.**

Los espejos locales del punto 1 existen justamente para esto: no te tienta a
usar una IA, y no dependen de internet.

---

## 5. Mantenimiento

```bash
cd ~/OSCP

# Regenerar los espejos desde los datos locales
python3 _sistema/herramientas/construir-referencias.py

# Actualizar los datos desde los repos oficiales (los tres son GPL-3.0)
cd /tmp
for r in WADComs/WADComs.github.io GTFOBins/GTFOBins.github.io LOLBAS-Project/LOLBAS; do
  curl -sL "https://github.com/$r/archive/refs/heads/master.tar.gz" -o "$(basename $r).tar.gz"
done
```

Los datos crudos viven en `_sistema/datos/referencias/` (3,4 MB): los YAML y markdown
originales de los tres proyectos.

---

## Atribución

| Proyecto | Autoría | Licencia |
| --- | --- | --- |
| GTFOBins | [GTFOBins](https://gtfobins.github.io/) (Emilio Pinna y colaboradores) | GPL-3.0 |
| WADComs | [WADComs](https://wadcoms.github.io/) | GPL-3.0 |
| LOLBAS | [LOLBAS Project](https://lolbas-project.github.io/) (Oddvar Moe y colaboradores) | GPL-3.0 |

Los espejos locales son copias derivadas con licencia GPL-3.0. Cada nota lleva el
link al original.
