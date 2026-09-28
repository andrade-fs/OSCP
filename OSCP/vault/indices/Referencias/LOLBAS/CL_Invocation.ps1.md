# LOLBAS: CL_Invocation.ps1

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Execute`

Aero diagnostics script

## Comandos

### Proxy execution

Execute · priv: User · T1216

```cmd
. C:\Windows\diagnostics\system\AERO\CL_Invocation.ps1   \nSyncInvoke {CMD}
```

Import the PowerShell Diagnostic CL_Invocation script and call SyncInvoke to launch an executable.

