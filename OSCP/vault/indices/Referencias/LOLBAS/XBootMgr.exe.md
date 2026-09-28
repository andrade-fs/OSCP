# LOLBAS: XBootMgr.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Execute`

Windows Performance Toolkit binary used to start performance traces.

## Comandos

### Executes code as part of post-trace automation flow.

Execute · priv: Administrator · T1202

```cmd
xbootmgr.exe -trace "{boot|hibernate|standby|shutdown|rebootCycle}" -callBack {PATH:.exe}
```

Executes an executable after the trace is complete using the callBack parameter.

### Executes code as part of pre-trace automation or staging.

Execute · priv: Administrator · T1202

```cmd
xbootmgr.exe -trace "{boot|hibernate|standby|shutdown|rebootCycle}" -preTraceCmd {PATH:.exe}
```

Executes an executable before each trace run using the preTraceCmd parameter.

