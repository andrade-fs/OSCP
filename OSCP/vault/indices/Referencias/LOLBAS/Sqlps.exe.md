# LOLBAS: Sqlps.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Execute`

Tool included with Microsoft SQL Server that loads SQL Server cmdlets. Microsoft SQL Server\100 and 110 are Powershell v2. Microsoft SQL Server\120 and 130 are Powershell version 4. Replaced by SQLToolsPS.exe in SQL Server 2016, but will be included with installation for compatability reasons.

## Comandos

### Execute PowerShell commands without ScriptBlock logging.

Execute · priv: User · T1218

```cmd
Sqlps.exe -noprofile
```

Run a SQL Server PowerShell mini-console without Module and ScriptBlock Logging.

