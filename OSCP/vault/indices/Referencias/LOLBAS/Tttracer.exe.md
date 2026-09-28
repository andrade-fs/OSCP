# LOLBAS: Tttracer.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Dump`, `Execute`

Used by Windows 1809 and newer to Debug Time Travel

## Comandos

### Spawn process using other binary

Execute · priv: Administrator · T1127

```cmd
tttracer.exe {PATH_ABSOLUTE:.exe}
```

Execute specified executable from tttracer.exe. Requires administrator privileges.

### Dump process by PID

Dump · priv: Administrator · T1003

```cmd
TTTracer.exe -dumpFull -attach {PID}
```

Dumps process using tttracer.exe. Requires administrator privileges

