# LOLBAS: Fsutil.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Execute`, `Tamper`

File System Utility

## Comandos

### Can be used to forensically erase a file

Tamper · priv: User · T1485

```cmd
fsutil.exe file setZeroData offset=0 length=9999999999 {PATH_ABSOLUTE}
```

Zero out a file

### Can be used to hide file creation activity

Tamper · priv: User · T1485

```cmd
fsutil.exe usn deletejournal /d c:
```

Delete the USN journal volume to hide file creation activity

### Spawn a pre-planted executable from fsutil.exe.

Execute · priv: User · T1218

```cmd
fsutil.exe trace decode
```

Executes a pre-planted binary named netsh.exe from the current directory.

