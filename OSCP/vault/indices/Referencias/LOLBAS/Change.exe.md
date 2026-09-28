# LOLBAS: Change.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Execute`

Remote Desktop Services MultiUser Change Utility

## Comandos

### Execute an arbitrary executable via trusted system executable.

Execute · priv: User · T1218

```cmd
change.exe user
```

Once executed, `change.exe` will execute `chgusr.exe` in the same folder. Thus, if `change.exe` is copied to a folder and an arbitrary executable is renamed to `chgusr.exe`, `change.exe` will spawn it. Instead of `user`, it is also possible to use `port` or `logon` as command-line option.

