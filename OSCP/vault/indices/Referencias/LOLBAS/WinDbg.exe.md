# LOLBAS: WinDbg.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Execute`

Windows Debugger for advanced user-mode and kernel-mode debugging.

## Comandos

### Executes an executable under a trusted microsoft signed binary.

Execute · priv: User · T1127

```cmd
windbg.exe -g {CMD}
```

Launches a command line through the debugging process; optionally add `-G` to exit the debugger automatically.

