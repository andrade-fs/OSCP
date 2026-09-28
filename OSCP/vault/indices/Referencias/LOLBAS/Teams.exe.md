# LOLBAS: Teams.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Execute`

Electron runtime binary which runs the Teams application

## Comandos

### Execute JavaScript code

Execute · priv: User · T1218.015

```cmd
teams.exe
```

Generate JavaScript payload and package.json, and save to "%LOCALAPPDATA%\\Microsoft\\Teams\\current\\app\\" before executing.

### Execute JavaScript code

Execute · priv: User · T1218.015

```cmd
teams.exe
```

Generate JavaScript payload and package.json, archive in ASAR file and save to "%LOCALAPPDATA%\\Microsoft\\Teams\\current\\app.asar" before executing.

### Executes a process under a trusted Microsoft signed binary

Execute · priv: User · T1218.015

```cmd
teams.exe --disable-gpu-sandbox --gpu-launcher="{CMD} &&"
```

Teams spawns cmd.exe as a child process of teams.exe and executes the ping command

