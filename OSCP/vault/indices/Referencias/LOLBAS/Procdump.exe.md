# LOLBAS: Procdump.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Execute`

SysInternals Memory Dump Tool

## Comandos

### Performs execution of unsigned DLL.

Execute · priv: User · T1202

```cmd
procdump.exe -md {PATH:.dll} explorer.exe
```

Loads the specified DLL where DLL is configured with a 'MiniDumpCallbackRoutine' exported function. Valid process must be provided as dump still created.

### Performs execution of unsigned DLL.

Execute · priv: User · T1202

```cmd
procdump.exe -md {PATH:.dll} foobar
```

Loads the specified DLL where configured with DLL_PROCESS_ATTACH execution, process argument can be arbitrary.

