# LOLBAS: fltMC.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Tamper`

Filter Manager Control Program used by Windows

## Comandos

### Defense evasion

Tamper · priv: Admin · T1562.001

```cmd
fltMC.exe unload SysmonDrv
```

Unloads a driver used by security agents

