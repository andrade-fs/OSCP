# LOLBAS: Atbroker.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Execute`

Helper binary for Assistive Technology (AT)

## Comandos

### Executes code defined in registry for a new AT. Modifications must be made to the system registry to either register or modify an existing Assistive Technology (AT) service entry.

Execute · priv: User · T1218

```cmd
ATBroker.exe /start malware
```

Start a registered Assistive Technology (AT).

