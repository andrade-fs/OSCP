# LOLBAS: Ieframe.dll

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Execute`

Internet Browser DLL for translating HTML code.

## Comandos

### Load an executable payload by calling a .url file with or without quotes. The .url file extension can be renamed.

Execute · priv: User · T1218.011

```cmd
rundll32.exe ieframe.dll,OpenURL {PATH_ABSOLUTE:.url}
```

Launch an executable payload via proxy through a(n) URL (information) file by calling OpenURL.

