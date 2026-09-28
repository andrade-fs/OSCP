# LOLBAS: wuauclt.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Execute`

Windows Update Client

## Comandos

### Execute dll via attach/detach methods

Execute · priv: User · T1218

```cmd
wuauclt.exe /UpdateDeploymentProvider {PATH_ABSOLUTE:.dll} /RunHandlerComServer
```

Loads and executes DLL code on attach.

