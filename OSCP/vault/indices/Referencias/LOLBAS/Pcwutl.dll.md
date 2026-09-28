# LOLBAS: Pcwutl.dll

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Execute`

Microsoft HTML Viewer

## Comandos

### Launch an executable.

Execute · priv: User · T1218.011

```cmd
rundll32.exe pcwutl.dll,LaunchApplication {PATH:.exe}
```

Launch executable by calling the LaunchApplication function.

