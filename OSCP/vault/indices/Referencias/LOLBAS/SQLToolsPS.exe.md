# LOLBAS: SQLToolsPS.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Execute`

Tool included with Microsoft SQL that loads SQL Server cmdlts. A replacement for sqlps.exe. Successor to sqlps.exe in SQL Server 2016+.

## Comandos

### Execute PowerShell command.

Execute · priv: User · T1218

```cmd
SQLToolsPS.exe -noprofile -command Start-Process {PATH:.exe}
```

Run a SQL Server PowerShell mini-console without Module and ScriptBlock Logging.

