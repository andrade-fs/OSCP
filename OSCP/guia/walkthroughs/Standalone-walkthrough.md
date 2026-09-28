# Standalone Walkthrough — las 3 máquinas independientes (60 pts)

Guía **secuencial** para las máquinas sueltas del OSCP+ (no el set de AD). Qué hacer, en qué
orden, y **cómo decidir** en cada bifurcación.

- Cada máquina vale **20 pts = 10 (acceso inicial) + 10 (escalada)**.
- **No te dan credenciales**: arrancás de una IP.
- Pueden ser **Linux o Windows** → el LPE cambia (ver [`LPE-Linux.md`](../lpe/LPE-Linux.md) /
  [`LPE-Windows.md`](../lpe/LPE-Windows.md)).
- El set de AD está en [`AD-walkthrough.md`](AD-walkthrough.md).

> **Alcance**: sin relay ni certificados. Para el resto, todo vale salvo lo prohibido en
> [`00-reglas-examen.md`](../00-reglas-examen.md).

---

## El modelo

```text
1 IP desconocida
   → recon completo (TODOS los puertos)
      → enumerar cada servicio en profundidad
         → foothold (credenciales / vulnerabilidad)
            → shell interactiva
               → local.txt
                  → enumeración local → LPE
                     → proof.txt
                        → loot (credenciales) → reutilizar en otras sueltas
```

### Idea fuerza

**Nunca explotes antes de enumerar.** El 90% de los bloqueos largos es enumeración incompleta,
no falta de skill. Y **sacá la captura del flag en el momento** (el reporte es final).

---

## Tiempo objetivo (por máquina)

| Bloque | Duración | Foco |
| --- | --- | --- |
| 0. Preparación | 2 min | variables, carpeta de evidencias |
| 1. Recon | 10–20 min | nmap completo + web |
| 2. Enumeración por servicio | 20–40 min | a fondo, antes de explotar |
| 3. Foothold | 10–40 min | creds / vuln / web |
| 4. `local.txt` | 5 min | shell interactiva + captura |
| 5. LPE | 20–60 min | Linux o Windows |
| 6. `proof.txt` | 5 min | captura |
| 7. Cierre | 5 min | documentar + reutilizar loot |

> Regla de las **1 h 30 min**: si te trabás, anotá qué probaste y **cambiá de máquina**.

---

## Bloque 0 — Preparación (2 min)

```bash
export IP='10.10.10.10'
export TU_IP=$(ip -4 addr show tun0 | awk '/inet /{print $2}' | cut -d/ -f1)

mkdir -p ~/examen/evidencia/$IP ~/examen/nmap
script -a ~/examen/evidencia/$IP/sesion.log
```

---

## Bloque 1 — Recon y triage (de TODAS primero)

Si tenés las 3 sueltas a la vez, **enumerá las tres antes de atacar**: te deja elegir la más
fácil y bajar la ansiedad cobrando puntos temprano.

```bash
# 1) TODOS los puertos TCP, rápido (nunca el default de 1000)
sudo nmap -p- --min-rate 5000 -T4 -oA ~/examen/nmap/$IP-alltcp "$IP"

# 2) Servicios y versiones sobre lo abierto
ports=$(grep -oP '^\d+' ~/examen/nmap/$IP-alltcp.nmap | sort -u | paste -sd,)
sudo nmap -sCV -p"$ports" -oA ~/examen/nmap/$IP-services "$IP"

# 3) UDP en lo que importa (lento, no barras todo)
sudo nmap -sU --top-ports 50 -oA ~/examen/nmap/$IP-udp "$IP"
```

**Si aparece 80/443, disparará de inmediato:**

```bash
whatweb "http://$IP"
curl -sI "http://$IP"
curl -s "http://$IP/robots.txt"; curl -s "http://$IP/sitemap.xml"

# Virtual hosts (cambia el juego más seguido de lo que creés)
ffuf -u "http://$IP/" -H "Host: FUZZ.<dominio>" \
  -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt \
  -mc 200,301,302,401,403 -fs <tamaño_default>

# Directorios y archivos
ffuf -u "http://$IP/FUZZ" \
  -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt \
  -mc 200,204,301,302,307,401,403 -t 50 -o ~/examen/evidencia/$IP/ffuf.json
```

**Checkpoint**: mapa de puertos + servicios + vhosts por máquina. **Elegí la que más rinda.**

---

## Bloque 2 — Enumeración por servicio (a fondo)

> Detalle de cada puerto en [`02-enumeracion-servicios.md`](../02-enumeracion-servicios.md).

| Puerto | Primeros comandos |
| --- | --- |
| **21 FTP** | `ftp $IP` (anonymous), `nxc ftp $IP -u anonymous -p ''` |
| **22 SSH** | reutilizar creds/claves; `ssh user@$IP`, `ssh -i id_rsa` |
| **25/465/587 SMTP** | `smtp-user-enum -M VRFY -U names.txt -t $IP` |
| **53 DNS** | `dig axfr @$IP <dominio>` (¡probar siempre!) |
| **80/443 HTTP** | whatweb, ffuf, vhosts, código fuente, `.git`, `.env` |
| **111 NFS** | `showmount -e $IP` (mirar `no_root_squash`) |
| **445 SMB** | `nxc smb $IP`, `--shares`, `--users`, null/guest, `smbclient -L` |
| **389 LDAP** | `ldapsearch -x -H ldap://$IP -s base namingcontexts` |
| **1433 MSSQL** | `nxc mssql`, `mssqlclient.py` (`xp_cmdshell`, impersonate) |
| **3306 MySQL** | `mysql -u root -h $IP -p` (root sin pass, FILE→webshell) |
| **3389 RDP** | `nxc rdp`, `xfreerdp3` |
| **5985 WinRM** | `evil-winrm` con creds/hash |
| **6379 Redis** | `redis-cli -h $IP` (CONFIG SET dir/dbfilename → webshell) |

**Qué buscar siempre**: login anónimo, credenciales por defecto, **reutilización** de la misma
contraseña entre servicios, versiones vulnerables (`searchsploit <servicio> <versión>`), backups,
configs, `.bak`, `.old`, tickets en web.

**Atajo**: `python3 ../_sistema/herramientas/buscar.py <servicio> -v --oscp` para ver cómo se atacó ese
puerto en las máquinas del corpus.

**Checkpoint**: al menos una hipótesis concreta de foothold (no "probar exploits a ver").

---

## Bloque 3 — Foothold

### Ruta A — Credenciales (reuso / default / encontradas)

```
¿Encontraste usuario:contraseña en FTP / web / SMB / configs?
   → probalo en SSH, SMB, WinRM, RDP, base de datos
   → probá el MISMO usuario/contraseña en TODOS los servicios
```

```bash
sshpass -p '<PASS>' ssh <user>@$IP
nxc smb   $IP -u '<USER>' -p '<PASS>'
nxc winrm $IP -u '<USER>' -p '<PASS>'
evil-winrm -i $IP -u '<USER>' -p '<PASS>'
```

### Ruta B — Vulnerabilidad de servicio

```bash
searchsploit <servicio> <version>
# y leé el exploit: adaptá LHOST/LPORT, no lo tires a ciegas
```

### Ruta C — Web

> **El ataque más común es LFI.** Si hay un parámetro que incluye ficheros, probalo primero.

```text
LFI (?file=, ?page=, ?path=, ?include=) → /etc/passwd, wrappers, logs → RCE   ← EL MÁS COMÚN
File upload                  → webshell Y DESPUÉS reverse shell real
Command injection            → ; id, | id, $(id), `id`
SSTI ({{7*7}} → 49)          → RCE (Jinja2/Twig)
Deserialización              → gadget chains
SQLi a mano                  → (sqlmap PROHIBIDO en el examen)
```

> **SQLi**: toda la explotación (union/error/blind/time, por motor) está en
> [PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings) — para MSSQL, en
> [`../cheatsheets/mssql-injection.md`](../../cheatsheets/mssql-injection.md). LFI→RCE completo en
> [`../cheatsheets/lfi-rce.md`](../../cheatsheets/lfi-rce.md).
>
> **Chuleta web completa** (checklist, upload, SQLi por motor, SSTI, APIs, Hydra):
> [`../cheatsheets/web.md`](../../cheatsheets/web.md).

Detalle por puerto: [`02-enumeracion-servicios.md`](../02-enumeracion-servicios.md).

### Ruta D — Shell estable y transferencia

Reverse shells y transferencia: [`06-payloads-shells-transferencia.md`](../06-payloads-shells-transferencia.md).

```bash
# Linux: TTY completa
python3 -c 'import pty; pty.spawn("/bin/bash")'
# Ctrl+Z; stty raw -echo; fg; Enter Enter; export TERM=xterm
```

> **Si el único acceso es una webshell, NO alcanza para los flags.** Necesitás reverse shell
> interactiva. Leer el flag desde webshell = **0 puntos**.

---

## Bloque 4 — `local.txt` (antes de escalar)

En cuanto tengas shell interactiva **y el nivel correcto** (usuario sin privilegios para
`local.txt`), sacá la captura.

```bash
cat local.txt; ip addr          # Linux
```

```cmd
type C:\Users\<user>\Desktop\local.txt & ipconfig    :: Windows
```

**Regla**: `cat`/`type` en shell interactiva, **desde su ubicación original**, y la captura debe
mostrar **contenido + IP de la víctima**. Documentalo ya (ver [`08-reporte-y-evidencia.md`](../08-reporte-y-evidencia.md)).

---

## Bloque 5 — Enumeración local y LPE

### Paso 0 — Triaje de 10 segundos

```bash
id; sudo -l; uname -a; getcap -r / 2>/dev/null      # Linux
```
```cmd
whoami /all & whoami /priv                           :: Windows
```

### Si es Linux → [`LPE-Linux.md`](../lpe/LPE-Linux.md)

Orden rápido:

```text
sudo -l → SUID/SGID (GTFOBins) → getcap -r / → credenciales en archivos
→ procesos root escribibles → cron (pspy) → servicios/systemd → grupos
→ NFS no_root_squash → wildcard injection → kernel
```

### Si es Windows → [`LPE-Windows.md`](../lpe/LPE-Windows.md)

```cmd
potato_check64.exe          :: si tenés SeImpersonate, dice qué Potato aplica
GodPotato.exe -cmd "cmd /c whoami"
```

```text
SeImpersonate → Potato → SYSTEM
procesos/services/tareas → rutas sin comillas, binarios escribibles, schtasks
credenciales guardadas → cmdkey, unattend, GPP, web.config
AlwaysInstallElevated → SeBackup/SeDebug → UAC (si admin local) → kernel
```

> **Si el foothold fue un web server o MSSQL**, revisá `SeImpersonatePrivilege` primero: suele
> estar y el SYSTEM es inmediato.

---

## Bloque 6 — `proof.txt` (root/SYSTEM)

```bash
cat /root/proof.txt; ip addr          # Linux (root)
```
```cmd
type C:\Users\Administrator\Desktop\proof.txt & ipconfig    :: Windows (SYSTEM/Administrator)
```

- Shell requerida: **Linux root**, **Windows SYSTEM/Administrator**.
- Captura con **contenido + IP**.
- Aprovechá para el **loot**: hashes, credenciales, tiques → reutilizables en las otras sueltas
  (y a veces en el set de AD).

---

## Bloque 7 — Cierre de la máquina

- [ ] `local.txt` y `proof.txt` con captura (contenido + IP).
- [ ] Comandos y outputs pegados en la bitácora de esa máquina.
- [ ] Credenciales/hashes guardados en un fichero común para reutilizar.
- [ ] Puntos enviados en el panel **antes** de que termine el examen.

```bash
# Fichero de loot compartido entre máquinas
echo "<IP> <user>:<pass>" >> ~/examen/loot.txt
```

---

## La estrategia de las 3 sueltas

```text
1. Recon de las 3 (solo mapa, sin explotar)
2. Atacá la que parezca MÁS FÁCIL primero  → cobrar 20 pts temprano
3. Loot → probar credenciales en las otras
4. La difícil al final (ya tenés el colchón)
```

**Reparto sugerido dentro de las 23 h 45 min**: ver [`01-metodologia.md`](../01-metodologia.md)
(triage → AD → sueltas → dormir → cierre → reporte).

---

## Árbol de decisión (resumen)

```text
IP
│
├─ Recon completo (nmap -p- + versiones + UDP + web/vhosts)
│
├─ ¿Servicio con vuln conocida o login débil?
│    → explotar / creds → shell
│
├─ ¿Web con LFI/upload/prototipo?
│    → RCE → shell interactiva
│
├─ ¿Credenciales filtradas en un servicio?
│    → reutilizarlas en TODOS los servicios
│
├─ shell → local.txt (captura ya)
│
├─ ¿Linux o Windows?
│    ├─ Linux   → LPE-Linux    (sudo → SUID → caps → cron → grupos → kernel)
│    └─ Windows → LPE-Windows  (potato_check → Potato → services → tareas → creds)
│
├─ root / SYSTEM → proof.txt (captura ya) → loot
│
└─ reutilizar loot en las otras sueltas / en el set de AD
```

---

## Errores típicos

| Error | Por qué duele |
| --- | --- |
| Saltear `-p-` en nmap | no ves el servicio que era la entrada |
| Ignorar virtual hosts | no ves la aplicación vulnerable |
| Webshell como shell de trabajo | **0 puntos** en esa máquina |
| Documentar al final | el reporte es final; lo que falta, falta |
| Ir directo al kernel exploit | puede tumbar la máquina y quemar un revert |
| No reutilizar credenciales | gastás tiempo reexplotando lo que ya tenías |
| No hacer LPE antes de buscar el `proof.txt` | no lo podés leer sin root/SYSTEM |
| Quemar Metasploit aquí | ver `00-reglas-examen.md` |

---

## Chuletas relacionadas

- [`02-enumeracion-servicios.md`](../02-enumeracion-servicios.md) — por puerto
- [`LPE-Linux.md`](../lpe/LPE-Linux.md) · [`LPE-Windows.md`](../lpe/LPE-Windows.md)
- [`06-payloads-shells-transferencia.md`](../06-payloads-shells-transferencia.md) — shells y transferencia
- [`../cheatsheets/lfi-rce.md`](../../cheatsheets/lfi-rce.md) · [`../cheatsheets/mssql-injection.md`](../../cheatsheets/mssql-injection.md)
- [`08-reporte-y-evidencia.md`](../08-reporte-y-evidencia.md) — capturas y evidencias
