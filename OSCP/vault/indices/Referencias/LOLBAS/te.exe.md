# LOLBAS: te.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Execute`

Testing tool included with Microsoft Test Authoring and Execution Framework (TAEF).

## Comandos

### Execute Visual Basic script stored in local Windows Script Component file.

Execute · priv: User · T1127

```cmd
te.exe {PATH:.wsc}
```

Run COM Scriptlets (e.g. VBScript) by calling a Windows Script Component (WSC) file.

### Execute DLL file.

Execute · priv: User · T1127

```cmd
te.exe {PATH:.dll}
```

Execute commands from a DLL file with Test Authoring and Execution Framework (TAEF) tests. See resources section for required structures.

