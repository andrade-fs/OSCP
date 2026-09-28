# LOLBAS: Explorer.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Execute`

Binary used for managing files and system components within Windows

## Comandos

### Performs execution of specified file with explorer parent process breaking the process tree, can be used for defense evasion.

Execute · priv: User · T1202

```cmd
explorer.exe /root,"{PATH_ABSOLUTE:.exe}"
```

Execute specified .exe with the parent process spawning from a new instance of explorer.exe

### Performs execution of specified file with explorer parent process breaking the process tree, can be used for defense evasion.

Execute · priv: User · T1202

```cmd
explorer.exe {PATH_ABSOLUTE:.exe}
```

Execute notepad.exe with the parent process spawning from a new instance of explorer.exe

