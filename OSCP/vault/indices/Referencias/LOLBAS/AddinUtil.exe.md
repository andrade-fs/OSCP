# LOLBAS: AddinUtil.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Execute`

.NET Tool used for updating cache files for Microsoft Office Add-Ins.

## Comandos

### Proxy execution of malicious serialized payload

Execute · priv: User · T1218

```cmd
C:\Windows\Microsoft.NET\Framework\v4.0.30319\AddinUtil.exe -AddinRoot:.
```

AddinUtil is executed from the directory where the 'Addins.Store' payload exists, AddinUtil will execute the 'Addins.Store' payload.

