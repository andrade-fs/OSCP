# LOLBAS: Ntsd.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Execute`

Symbolic Debugger for Windows.

## Comandos

### Executes an executable under a trusted microsoft signed binary.

Execute · priv: User · T1127

```cmd
ntsd.exe -g {CMD}
```

Launches command through the debugging process; optionally add `-G` to exit the debugger automatically.

