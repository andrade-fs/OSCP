# LOLBAS: Conhost.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Execute`

Console Window host

## Comandos

### Use conhost.exe as a proxy binary to evade defensive counter-measures

Execute · priv: User · T1202

```cmd
conhost.exe {CMD}
```

Execute a command line with conhost.exe as parent process

### Specify --headless parameter to hide child process window (if applicable)

Execute · priv: User · T1202

```cmd
conhost.exe --headless {CMD}
```

Execute a command line with conhost.exe as parent process

