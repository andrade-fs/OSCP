# LOLBAS: Setres.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Execute`

Configures display settings

## Comandos

### Executes arbitrary code

Execute · priv: User · T1218

```cmd
setres.exe -w 800 -h 600
```

Sets the resolution and then launches 'choice' command from the working directory.

