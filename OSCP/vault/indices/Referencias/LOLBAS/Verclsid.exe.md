# LOLBAS: Verclsid.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Execute`

Used to verify a COM object before it is instantiated by Windows Explorer

## Comandos

### Run a COM object created in registry to evade defensive counter measures

Execute · priv: User · T1218.012

```cmd
verclsid.exe /S /C {CLSID}
```

Used to verify a COM object before it is instantiated by Windows Explorer

