# Entorno verificado

> Verificación ejecutada contra los binarios reales de esta máquina.
> Todo lo marcado como **[VERIFICADO]** fue comprobado ejecutando el comando, no leyendo documentación.
>
> **Última verificación: 23 de septiembre de 2026.**
>
> **Esta máquina es la Kali del examen.** Todo debe funcionar aquí; no hay que copiar nada.

---

## Chequeo rápido (hacelo antes de rendir)

```bash
bash ~/OSCP/_sistema/herramientas/verificar-entorno.sh
```

Comprueba de golpe **comandos, módulos Python, wordlists, toolkits (Linux/Windows) y vault**
(167 comprobaciones). Si termina con **`TODO OK … 0 fallos`** y exit code `0`, estás listo.

---

## Plataforma

| Dato | Valor |
| --- | --- |
| Distro | Kali GNU/Linux Rolling |
| Versión | **2026.3** |
| Arquitectura | x86_64 |
| Python sistema | **3.14.7** (`/usr/bin/python3`) — también hay `python3.13` |
| Ruby | 3.3.8 |

> Esta es una versión más nueva que la del doc original (2025.3). Varios "problemas conocidos"
> que figuraban antes **ya no existen** y están corregidos más abajo.

---

## Estado de los problemas históricos

### `nxc` — **RESUELTO**

**[VERIFICADO]** `nxc` funciona sin problemas. Resuelve a `/usr/bin/nxc`
(NetExec **1.5.1 "Yippie-Ki-Yay"**). Ya **no** hay shim roto de pipx en `~/.local/bin`,
y la base de datos se inicializó limpia: `nxc smb -L` lista **89 módulos** sin
`schema mismatch`.

**No hace falta** usar ruta absoluta ni tocar pipx. `nxc` a secas está bien.

### Impacket — cambio de empaquetado

**[VERIFICADO]** En este Kali, Impacket **0.14.0.dev0** se instala con **61 wrappers
`impacket-<nombre>`** en `/usr/bin` y los scripts `.py` en
`/usr/share/doc/python3-impacket/examples/`. Ya **no** vienen en `~/.local/bin`.

Para que los comandos del playbook (que usan `secretsdump.py`, `GetUserSPNs.py`, etc.)
funcionen **tal cual están escritos**, se crearon **symlinks `.py` en `~/.local/bin`**
que apuntan a los wrappers o a los ejemplos. Verificado que corren.

```bash
# Ambos funcionan:
impacket-secretsdump -h
secretsdump.py -h          # symlink → wrapper impacket-secretsdump
```

Si algo faltara, el original siempre está en:

```bash
ls /usr/bin/impacket-*                          # 61 wrappers
ls /usr/share/doc/python3-impacket/examples/    # 68 scripts .py
```

> **`dacledit.py` ahora SÍ está en el `PATH`** (vía symlink en `~/.local/bin`).
> El alias manual que antes era necesario ya no hace falta:
> `dacledit.py -action read ...` funciona directo.

### Certipy — v5, no v4 (**sigue vigente**)

**[VERIFICADO]** Certipy **v5.1.0**. La mayoría del material online documenta v4.
El binario es **`certipy-ad`**, no `certipy`.

```text
{account, auth, ca, cert, find, parse, forge, relay, req, shadow, template}
```

Ver `../cheatsheets/certipy.md`. **Regla**: confirmá con `certipy-ad <subcomando> --help`.

### `proxychains4` — **CORREGIDO**

**[VERIFICADO]** El archivo `/etc/proxychains4.conf` venía en `strict_chain` apuntando
**solo a Tor** (`socks4 127.0.0.1 9050`), que no es lo que usa el pivoting del playbook.
Se corrigió para que apunte al SOCKS5 local del túnel:

```text
[ProxyList]
#socks4 127.0.0.1 9050   # Tor (desactivado; se usa SOCKS5 local para pivoting)
socks5 127.0.0.1 1080
```

Backup del original: `/etc/proxychains4.conf.bak-20260923`.

Así, `ssh -D 1080 -N -f user@pivote` y `chisel ... R:socks` funcionan con `proxychains4`
sin tocar nada más.

### Nombres de los binarios de Ligolo-ng

**[VERIFICADO]** El paquete instala **`ligolo-proxy`** y **`ligolo-agent`**
(no `proxy` ni `agent` como en la documentación upstream).

### `droopescan` — **NO INSTALABLE**

Depende de `cement` 2.x, que importa el módulo `imp` **eliminado en Python ≥3.12**.
Con Python 3.13/3.14 es imposible correrlo y el proyecto está abandonado.
Se descartó. Para Drupal usá `whatweb`, plantillas de `nuclei`, o enumeración manual.

---

## Herramientas verificadas como funcionales

### Red y enumeración

| Herramienta | Versión / ruta | Nota |
| --- | --- | --- |
| `nmap` | 7.99 | |
| `nxc` | NetExec 1.5.1 | `/usr/bin/nxc` |
| `crackmapexec` | — | **eliminado**, reemplazado por `nxc` |
| `enum4linux` | 0.9.1 | |
| `enum4linux-ng` | 1.3.10 | |
| `smbmap`, `smbclient`, `rpcclient` | OK | Samba 4.24.6 |
| `ldapsearch` | OpenLDAP 2.6.14 | |
| `responder` | OK | `/usr/sbin/responder` |
| `bloodhound-python` | OK | |
| `pypykatz` | 0.6.13 | |
| `mitm6` | 0.3.0 | |
| `coercer` | 2.4.3 | coerción unificada (PetitPotam, PrinterBug, DFSCoerce…) |
| `krbrelayx` | OK | incluye `printerbug`, `addspn`, `dnstool` |
| `PetitPotam.py` | OK | `~/.local/bin/PetitPotam.py` |

### AD — Impacket (0.14.0.dev0)

61 wrappers `impacket-*` en `/usr/bin` + 55 symlinks `.py` en `~/.local/bin`.
Verificados: `secretsdump.py`, `GetNPUsers.py`, `GetUserSPNs.py`, `getTGT.py`, `getST.py`,
`addcomputer.py`, `rbcd.py`, `ticketer.py`, `dacledit.py`, `ntlmrelayx.py`,
`smbclient.py`, `mssqlclient.py`, `findDelegation.py`, `Get-GPPPassword.py`, `lookupsid.py`.

### Herramientas AD extra (verificadas)

| Herramienta | Para qué |
| --- | --- |
| `kinit`, `klist`, `kdestroy`, `ktutil` | cliente Kerberos (`krb5-user`) |
| `ntpdate` (ntpsec) · `rdate` | sincronizar reloj con el DC (evita `KRB_AP_ERR_SKEW`) |
| `bloodyAD` (2.5.5, pipx) | abuso de ACLs / LDAP (alternativa a `dacledit`) |
| `ldeep` (2.0.3, pipx) | enumeración LDAP/AD |
| `pyLAPS.py` | leer LAPS |
| `gMSADumper.py` | leer la contraseña de un gMSA |
| `targetedKerberoast.py` | targeted Kerberoasting |
| `certipy-ad`, `coercer`, `mitm6`, `krbrelayx` | **fuera de alcance** (labs) |

### Web

| Herramienta | Versión | Nota |
| --- | --- | --- |
| `whatweb` | 0.6.4 | |
| `nikto` | 2.6.1 | |
| `nuclei` | v3.11.1 | |
| `ffuf` | 2.1.0-dev | `/usr/bin/ffuf` |
| `gobuster` | OK | |
| `feroxbuster` | 2.13.1 | |
| `wpscan` | OK | WordPress |
| `joomscan` | 0.0.7 | Joomla |
| `wapiti` | OK | |
| `sqlmap` | OK | ⚠️ **prohibido en el examen** (herramienta automática) |

### Pivoting y transferencia

| Herramienta | Versión | Nota |
| --- | --- | --- |
| `proxychains4` | OK | configurado a `socks5 127.0.0.1 1080` |
| `socat` | OK | |
| `ssh` | OK | port forwarding nativo |
| `chisel` | 1.12.1 | |
| `ligolo-ng` | 0.9.1 | binarios `ligolo-proxy` / `ligolo-agent` |
| `ncat` | 7.99 | |
| `rlwrap` | 0.47 | |
| `sshpass` | 1.10 | |
| `nc` | OK | |
| `xfreerdp3` | 3.31.1 | cliente RDP |
| `vncviewer` | TightVNC 1.3.10 | |
| `smbserver.py`, `pyftpdlib`, `uploadserver` | OK | servidores para subir/bajar |

### Cracking y post-explotación

| Herramienta | Versión |
| --- | --- |
| `hashcat` | v7.1.2 (**última release**) |
| `john` | 1.9.0-jumbo-1+bleeding **2026-08-02** (compilado desde `bleeding-jumbo`; el de Kali era de 2021) |
| `hydra` | OK |
| `hashid`, `hash-identifier` | OK |
| `pwntools` | 4.15.0 |
| `evil-winrm` | v4.1 |
| `kerbrute` | v1.0.3 (`/usr/local/bin`) |
| `msfconsole` / `msfvenom` | OK |
| `searchsploit` | OK (no acepta `--version`) |
| `jq` | 1.8.2 |
| `tmux`, `screen`, `tcpdump` | OK |
| `gdb`, `gdbserver` | 17.2 |

### Wordlists y reglas

| Ruta | Estado |
| --- | --- |
| `/usr/share/wordlists/rockyou.txt` | ✓ **descomprimido** (14.344.392 líneas; venía solo `.gz`) |
| `/usr/share/seclists/` | ✓ **instalado** (2025.3-0kali1) — `Discovery/Web-Content`, `Discovery/DNS`, `Usernames`… |
| `/usr/share/hashcat/rules/best64.rule` | ✓ copiado (hashcat trae `best66.rule`; `best64` venía en John) |
| `/usr/share/hashcat/rules/best66.rule` | ✓ por defecto |
| `/usr/share/wordlists/dirb`, `dirbuster`, `wfuzz` | ✓ (symlinks) |

---

## Toolkit de ataque listo para el examen

**[VERIFICADO]** Preparado en `~/examen/tools/` (creado el 23-sep-2026).
El playbook pide tenerlo listo **antes** del examen, no descargarlo el día del examen.

### `~/examen/tools/linux/`

| Archivo | Para qué |
| --- | --- |
| `linpeas.sh` | enumeración automática Linux |
| `pspy64`, `pspy32` | observar cron y procesos sin permisos |
| `chisel` | cliente/servidor de túnel (Linux) |
| `ligolo-agent` | agente de pivoting (Linux) |
| `linux-exploit-suggester.sh` | sugerir exploits de kernel |
| `lse.sh` | enumeración por niveles (linux-smart-enumeration) |
| `deepce.sh` | enumeración/escape de contenedores |
| `traitor` | auto-explotación de varios vectores LPE |

### `~/examen/tools/win/`

**Enumeración y escalada**

| Archivo | Para qué |
| --- | --- |
| `winPEASx64.exe`, `winPEASx86.exe`, `winPEAS.bat` | enumeración automática |
| `PowerUp.ps1`, `PowerView.ps1` | enumeración y escalada / AD |
| `Seatbelt.exe`, `SharpUp.exe` | enumeración local |
| `Watson.exe` | sugerir CVEs de kernel según parches |
| `accesschk64.exe`, `accesschk.exe` | permisos de servicios/objetos |
| `Snaffler.exe` | buscar secretos en shares |
| `Procmon.exe` | Process Monitor: ver procesos/registro/ficheros en vivo |

**Credenciales**

| Archivo | Para qué |
| --- | --- |
| `mimikatz/x64/mimikatz.exe`, `mimikatz/Win32/mimikatz.exe` | credenciales en memoria |
| `SafetyKatz.exe`, `SharpDump.exe` | variantes de volcado de LSASS |
| `SharpDPAPI.exe`, `SharpChrome.exe` | secretos DPAPI / navegadores |
| `procdump64.exe`, `procdump.exe` | volcado de LSASS |
| `LaZagne.exe` | credenciales de aplicaciones |
| `Koh.exe` | robo de tokens |
| `DecryptAutoLogon.exe` | descifrar la contraseña de AutoLogon del registro (`DefaultPassword`) |

**Potatoes (`SeImpersonatePrivilege`)**

| Archivo | Para qué |
| --- | --- |
| `GodPotato.exe`, `SigmaPotato.exe` | los más amplios (empezá por acá) |
| `PrintSpoofer64.exe`, `PrintSpoofer32.exe` | Spooler |
| `JuicyPotato.exe`, `JuicyPotatoNG.exe` | por versión de Windows |
| `RoguePotato.exe`, `RogueWinRM.exe`, `RemotePotato0.exe` | alternativas |
| `potato_check64.exe`, `potato_check32.exe` | **diagnóstico**: dice qué Potato aplica |
| `FullPowers.exe` | recuperar privilegios tras un token restringido |
| `SeManageVolumeExploit.exe` | `SeManageVolumePrivilege` |

**AD / Kerberos**

| Archivo | Para qué |
| --- | --- |
| `Rubeus.exe` | Kerberos (TGT, S4U, delegación, golden) |
| `Certify.exe` | ADCS (fuera de alcance, labs) |
| `SharpWMI.exe` | ejecución/enum vía WMI |
| `SharpHound.exe`, `SharpHound.ps1` | recolección BloodHound desde Windows |
| `SharpLAPS.exe` | leer LAPS desde Windows |
| `LockLess.exe`, `RestrictedAdmin.exe` | bypass de UAC / RDP restringido |

**Pivoting, transferencia y scripts**

| Archivo | Para qué |
| --- | --- |
| `chisel.exe`, `ligolo-agent.exe` | túnel desde Windows |
| `nc.exe`, `nc64.exe` | transferencia y shells |
| `powercat.ps1`, `Invoke-Mimikatz.ps1` | shells / mimikatz en PowerShell |

> **Sin binario (compilar desde fuente):** `SweetPotato`, `EfsPotato`, `SharpEfsPotato`,
> `DCOMPotato` (0 releases) y `SharpGPOAbuse` (requiere NuGet). Cubiertos por
> `GodPotato`/`SigmaPotato`/`RogueWinRM`.
>
> Fuente de algunos binarios: [s4mu51/OSCP-Tools](https://github.com/s4mu51/OSCP-Tools)
> (verificado con su `CHECKSUMS.sha256`). `Inveigh` y `shell.aspx` **no se añadieron** (checksum
> no coincidía); además **Inveigh hace spoofing/poisoning, prohibido en el examen**.

> **Antes de rendir**: copiá la carpeta a `/tmp/` de tu Kali de examen y arrancá
> `python3 -m http.server 8000` desde ahí. No improvises la ruta el minuto 14.

---

## Huecos y limitaciones conocidas

| Cosa | Estado | Alternativa |
| --- | --- | --- |
| `droopescan` | **incompatible** con Python 3.14 | `whatweb`, `nuclei`, manual |
| `SweetPotato.exe` | sin release binario | usar `GodPotato` / `RoguePotato` |
| `SharpEfsPotato.exe` | sin release binario | `GodPotato` (EFSRPC está en la familia Potato) |
| `GMSAPasswordReader.exe` | sin release binario (0 assets) | `gMSADumper.py` (Linux) |
| `crackmapexec` | eliminado | `nxc` |
| `freerdp3-x11` | ya presente como `xfreerdp3` | — |

**No instales nada durante el examen.** Prepará y verificá el entorno antes.

---

## Instalación desde cero (para una Kali nueva)

```bash
# Paquetes base que el playbook necesita
sudo apt update
sudo apt install -y enum4linux-ng mitm6 coercer krbrelayx joomscan \
                    python3-pwntools python3-pyftpdlib \
                    chisel ligolo-ng ncat rlwrap sshpass jq freerdp3-x11

# kerbrute (NO está en apt)
cd /tmp
curl -sLO https://github.com/ropnop/kerbrute/releases/latest/download/kerbrute_linux_amd64
sudo install -m 0755 kerbrute_linux_amd64 /usr/local/bin/kerbrute

# Impacket .py names para que los comandos del playbook funcionen
for f in /usr/share/doc/python3-impacket/examples/*.py; do
  b=$(basename "$f"); base="${b%.py}"
  [ -x "$f" ] && ln -sf "$f" "$HOME/.local/bin/$b"
  [ -x "/usr/bin/impacket-$base" ] && [ ! -e "$HOME/.local/bin/$b" ] && ln -sf "/usr/bin/impacket-$base" "$HOME/.local/bin/$b"
done

# uploadserver (para `python3 -m uploadserver`)
sudo pip3 install --break-system-packages uploadserver
```

---

## Cómo mantener esto vivo

Cuando corras `apt upgrade`, estas versiones cambian. Antes de una sesión de práctica
seria, volvé a correr esta verificación:

```bash
/usr/bin/nxc --version
certipy-ad --version
python3 -c "import importlib.metadata as m; print(m.version('impacket'))"
evil-winrm --version
hashcat --version
chisel --version
ligolo-proxy --version
kerbrute 2>&1 | head -1

# Que el SOCKS siga apuntando al túnel
tail -3 /etc/proxychains4.conf
```

Si Certipy salta a v6, **toda la sección de ADCS del playbook necesita revisión**:
está escrita para v5.1.0.
