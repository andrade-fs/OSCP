# LOLBAS: Wab.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Execute`

Windows address book manager

## Comandos

### Execute dll file. Bypass defensive counter measures

Execute · priv: Administrator · T1218

```cmd
wab.exe
```

Change HKLM\Software\Microsoft\WAB\DLLPath and execute DLL of choice

