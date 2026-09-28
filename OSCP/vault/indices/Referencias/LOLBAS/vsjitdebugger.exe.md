# LOLBAS: vsjitdebugger.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Execute`

Just-In-Time (JIT) debugger included with Visual Studio

## Comandos

### Execution of local PE file as a subprocess of Vsjitdebugger.exe.

Execute · priv: User · T1127

```cmd
Vsjitdebugger.exe {PATH:.exe}
```

Executes specified executable as a subprocess of Vsjitdebugger.exe.

