# LOLBAS: Runexehelper.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Execute`

Launcher process

## Comandos

### Executes arbitrary code

Execute · priv: User · T1218

```cmd
runexehelper.exe {PATH_ABSOLUTE:.exe}
```

Launches the specified exe. Prerequisites: (1) diagtrack_action_output environment variable must be set to an existing, writable folder; (2) runexewithargs_output.txt file cannot exist in the folder indicated by the variable.

