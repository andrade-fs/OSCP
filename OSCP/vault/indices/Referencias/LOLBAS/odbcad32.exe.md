# LOLBAS: odbcad32.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `UAC Bypass`

ODBC Data Source Administrator to manage User/System DSNs and ODBC drivers.

## Comandos

### Execute a binary as a high-integrity process without a UAC prompt.

UAC Bypass · priv: User · T1548.002

```cmd
odbcad32.exe
```

Launch odbcad32.exe GUI, click 'Tracing' tab, click 'Browsing' button, enter abitrary command in the File Dialog's path, press enter.

