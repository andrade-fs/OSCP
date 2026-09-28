# LOLBAS: Gpscript.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Execute`

Used by group policy to process scripts

## Comandos

### Add local group policy logon script to execute file and hide from defensive counter measures

Execute · priv: Administrator · T1218

```cmd
Gpscript /logon
```

Executes logon scripts configured in Group Policy.

### Add local group policy logon script to execute file and hide from defensive counter measures

Execute · priv: Administrator · T1218

```cmd
Gpscript /startup
```

Executes startup scripts configured in Group Policy

