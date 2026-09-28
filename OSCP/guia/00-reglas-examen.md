# 00 — Reglas del examen

> Fuente primaria: *OSCP+ Exam Guide* de OffSec (help.offsec.com, artículo 360040165632,
> página fechada **20 de abril de 2026**) y *OSCP+ Exam FAQ*.
> Los textos entre comillas son **verbatim** del documento oficial.

---

## Estructura y puntaje

El examen simula una red viva en una VPN privada:

> "The OSCP+ certification exam simulates a live network in a private VPN, which contains a
> small number of vulnerable machines."

| Componente | Puntaje | Detalle |
| --- | --- | --- |
| 3 máquinas independientes | **60 pts** | 20 pts cada una: 10 acceso inicial + 10 escalada |
| 1 set de Active Directory (3 máquinas) | **40 pts** | 10 + 10 + 20 |
| **Total** | **100 pts** | |

### Aprobación: 70 / 100

Escenarios válidos según la guía:

- 40 pts AD + 3 `local.txt` = 70
- 40 pts AD + 2 `local.txt` + 1 `proof.txt` = 70
- 20 pts AD + 3 `local.txt` + 2 `proof.txt` = 70
- 10 pts AD + 3 máquinas independientes completas = 70

### El set de AD es *assumed breach*

> "For the Active Directory exam set, learners will be provided with a username and password,
> simulating a breach scenario."

**Esto es un cambio de fondo respecto del examen viejo.** Ya no hay que conseguir el primer
pie: te dan credenciales y arrancás desde adentro. Antes había un compromiso previo
("gating") que había que romper para poder entrar. Lo eliminaron.

**Implicancia para tu preparación**: media hora de "recon inicial contra el perímetro del set AD"
es tiempo tirado. Arrancás enumerando el dominio con credenciales válidas.

### Puntaje parcial de AD

El set de AD **NO es todo o nada**. Los 40 puntos se reparten 10 / 10 / 20 y **se otorgan
parcialmente**. Si te trabás en la tercera máquina, ya cobraste 20 puntos de las dos primeras.

Dato histórico que te sirve para calibrar: el sistema viejo daba **puntos bonus** por completar
ejercicios del laboratorio. **Eso ya no existe.** No hay colchón: los 70 puntos salen todos
del examen.

---

## Restricciones: qué NO podés usar

Verbatim, sección "Exam Restrictions":

> "You cannot use any of the following on the exam:
> - Spoofing (IP, ARP, DNS, NBNS, etc)
> - Commercial tools or services (Metasploit Pro, Burp Pro, etc.)
> - Automatic exploitation tools (e.g. db_autopwn, browser_autopwn, SQLmap, SQLninja etc.)
> - Mass vulnerability scanners (e.g. Nessus, NeXpose, OpenVAS, Canvas, Core Impact, SAINT, etc.)
> - AI Chatbots (OffSec KAI, ChatGPT, YouChat, etc.)
> - Features in other tools that utilize either forbidden or restricted exam limitations"

Ojo con la última línea: **"Features in other tools that utilize either forbidden or restricted
exam limitations"**. No alcanza con que la herramienta no esté en la lista — si *internamente*
usa algo prohibido, está prohibida. El propio documento lo dice:

> "You are ultimately responsible for knowing what features or external utilities any chosen
> tool is using."

### Lo que SÍ está permitido

> "You may however, use tools such as Nmap (and its scripting engine), Nikto, Burp Free,
> DirBuster etc. against any of your target systems."

Nmap con su scripting engine completo, Nikto, Burp Free, DirBuster. Explotación manual
con scripts propios o de exploit-db: permitido.

### Sobre buscar información: SÍ se puede

Esta nota es importante y suele malinterpretarse:

> "NOTE: While you may use Discord as a resource for **searching for information** during the
> exam, under no circumstances are you permitted to **seek or receive assistance from others**
> on the platform."

La línea es clara:

- **Buscar información** → permitido.
- **Pedir ayuda a otra persona** → falta.

Tus propias notas, cheatsheets y este playbook entran en la primera categoría. Ahí no hay gris.

---

## Metasploit: la restricción que más gente pierde puntos por malinterpretar

> "The usage of Metasploit and the Meterpreter payload are restricted during the exam. You may
> only use Metasploit modules (Auxiliary, Exploit, and Post) or the Meterpreter payload against
> **one** single target machine of your choice."

### Las reglas exactas

1. **Una sola máquina** para todo el uso de Metasploit (módulos Auxiliary, Exploit, Post) *y*
   Meterpreter. La elegís vos, una vez.
2. **`check` cuenta como uso.**
   > "Metasploit/Meterpreter should not be used to test vulnerabilities on multiple machines
   > before selecting your one target machine (this includes the use of `check`)."
3. **Se bloquea al primer uso.**
   > "the use of Metasploit and Meterpreter becomes locked in as soon as you decide to use
   > either one of them."
4. **No hay segunda oportunidad.**
   > "If you decide to use Metasploit or Meterpreter on a specific target and the attack fails,
   > then you may not attempt to use it on a second target."
5. **No se puede usar para pivoting.**
   > "Metasploit cannot be used for pivoting, because it would thereby be used on more than one target."

### Lo que queda exento

> "You may use the following against all of the target machines with the exception that
> meterpreter payload could be used only against one target machine:
> - multi handler (aka exploit/multi/handler)
> - msfvenom"

**Leelo de nuevo, porque es la parte que casi nadie aprovecha bien:**

- `exploit/multi/handler` → **sin restricción**, en todas las máquinas.
- `msfvenom` → **sin restricción**, en todas las máquinas. Generá los payloads que quieras.
- Lo restringido es el *payload* `meterpreter`, que sigue limitado a una máquina.

O sea: podés usar `msfvenom` para generar un `windows/x64/shell_reverse_tcp` para cada máquina,
y levantar el handler con `multi/handler`. Eso no consume tu única carta. Lo que consume la
carta es usar un **módulo exploit aux/post de Metasploit** o el **payload meterpreter**.

### Aplica también a las interfaces

> "All the above limitations also apply to different interfaces that make use of Metasploit
> (such as Armitage, Cobalt Strike, Metasploit Community Edition, etc)."

### Sanción

> "You will receive no points for a specific target for the following: [...] Using a restricted
> tool [...] Using Metasploit Auxiliary, Exploit, or Post modules on multiple machines [...]"

Cero puntos en esa máquina. No es un descuento, es cero.

---

## Pruebas y capturas: donde se pierden puntos por prolijidad

### Los archivos

| Archivo | Quién lo lee | Ubicación |
| --- | --- | --- |
| `local.txt` | usuario sin privilegios | — |
| `proof.txt` | root / Administrator | `/root/` o Desktop del Administrator |

### Regla de oro para leerlos

> "The valid way to provide the contents of the proof files is in an interactive shell on the
> target machine with the `type` or `cat` command **from their original location**."
> "Obtaining the contents of the proof files in any other way will result in zero points for
> the target machine; **this includes any type of web-based shell**."

**Traducción operativa**: no copies el flag a otro directorio, no lo leas con un `find -exec`,
no lo pases por un script. `cat /root/proof.txt` en una shell interactiva. Nada más.

Y **una shell web NO es válida**: te da cero en esa máquina. Si tu acceso inicial fue vía
webshell, tenés que conseguir una reverse shell real antes de tocar el flag.

### Las capturas

Cada captura de `local.txt` y `proof.txt` debe mostrar:

1. El contenido del archivo.
2. La IP de la máquina víctima, vía `ipconfig`, `ifconfig` o `ip addr`.

Las dos cosas en la misma captura. Un comando que sirve:

```bash
cat /root/proof.txt; ip addr
```

```powershell
type C:\Users\Administrator\Desktop\proof.txt; ipconfig
```

### Niveles de shell requeridos

- **Windows**: shell con permisos de `SYSTEM`, `Administrator`, o usuario con privilegios de Administrator.
- **Linux**: shell de **root**.

Acceso a archivos sin shell con ese nivel no alcanza.

### Envío

Los flags se envían en el **panel de control antes de que termine el examen**. El panel **no te
dice si el flag es correcto** — enviá con cuidado, transcribilo bien.

---

## Tiempo

| Fase | Duración |
| --- | --- |
| Examen | **23 h 45 min** |
| Reporte (después) | **24 h** |

El reporte se sube después de terminado el examen.

> "once your exam report is submitted, your submission is final. If any screenshots or other
> information is missing, you will not be allowed to send them and we will not request them."

**No hay segunda instancia para corregir el reporte.** Si falta una captura, se pierde. Esto
convierte la disciplina de documentación *durante* el examen en algo no negociable.

Ver `08-reporte-y-evidencia.md` para el flujo de captura continua.

## Reverts

> "You have a limit of 24 reverts. This limit can be reset once during the exam."

24 reverts, reiniciables una vez. Las máquinas arrancan ya revertidas. Un click por intento.

**Cuidado**: revertir borra todo tu progreso en esa máquina. No lo hagas por reflejo.
