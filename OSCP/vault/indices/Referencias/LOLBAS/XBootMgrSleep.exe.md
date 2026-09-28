# LOLBAS: XBootMgrSleep.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Execute`

Windows Performance Toolkit binary used for tracing and analyzing system performance during sleep and resume transitions.

## Comandos

### Performs execution of specified executable, can be used as a defense evasion

Execute · priv: User · T1202

```cmd
xbootmgrsleep.exe 1000 {PATH:.exe}
```

Execute executable via XBootMgrSleep, with a 1 second (=1000 milliseconds) delay. Alternatively, it is also possible to replace the delay with any string for immediate execution.

