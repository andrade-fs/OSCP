# LOLBAS: OneDriveStandaloneUpdater.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Download`

OneDrive Standalone Updater

## Comandos

### Download a file from the Internet without executing any anomalous executables with suspicious arguments

Download · priv: User · T1105

```cmd
OneDriveStandaloneUpdater
```

Download a file from the web address specified in `HKCU\Software\Microsoft\OneDrive\UpdateOfficeConfig\UpdateRingSettingURLFromOC`. `ODSUUpdateXMLUrlFromOC` and `UpdateXMLUrlFromOC` must be equal to non-empty string values in that same registry key. `UpdateOfficeConfigTimestamp` is a UNIX epoch time which must be set to a large QWORD such as 99999999999 (in decimal) to indicate the URL cache is good. The downloaded file will be in `%localappdata%\OneDrive\StandaloneUpdater\PreSignInSettingsConfig.json`.

