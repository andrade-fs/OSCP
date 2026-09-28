# LOLBAS: Runonce.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Execute`

Executes a Run Once Task that has been configured in the registry

## Comandos

### Persistence, bypassing defensive counter measures

Execute · priv: Administrator · T1218

```cmd
Runonce.exe /AlternateShellStartup
```

Executes a Run Once Task that has been configured in the registry.

