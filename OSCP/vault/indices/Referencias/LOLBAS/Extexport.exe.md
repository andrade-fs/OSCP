# LOLBAS: Extexport.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Execute`

Load a DLL located in the c:\test folder with a specific name.

## Comandos

### Execute dll file

Execute · priv: User · T1218

```cmd
Extexport.exe {PATH_ABSOLUTE:folder} foo bar
```

Load a DLL located in the specified folder with one of the following names mozcrt19.dll, mozsqlite3.dll, or sqlite.dll.

