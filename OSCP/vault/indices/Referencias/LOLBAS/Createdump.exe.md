# LOLBAS: Createdump.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Dump`

Microsoft .NET Runtime Crash Dump Generator (included in .NET Core)

## Comandos

### Dump process memory contents using PID.

Dump · priv: SYSTEM · T1003

```cmd
createdump.exe -n -f {PATH:.dmp} {PID}
```

Dump process by PID and create a minidump file. If "-f dump.dmp" is not specified, the file is created as '%TEMP%\dump.%p.dmp' where %p is the PID of the target process.

