# LOLBAS: winfile.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Execute`

Windows File Manager executable

## Comandos

### Performs execution of specified file, can be used as a defense evasion

Execute · priv: User · T1202

```cmd
winfile.exe {PATH:.exe}
```

Execute an executable file with WinFile as a parent process.

