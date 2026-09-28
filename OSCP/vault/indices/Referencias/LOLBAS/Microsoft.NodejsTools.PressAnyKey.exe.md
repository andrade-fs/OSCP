# LOLBAS: Microsoft.NodejsTools.PressAnyKey.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Execute`

Part of the NodeJS Visual Studio tools.

## Comandos

### Spawn a new process via Microsoft.NodejsTools.PressAnyKey.exe.

Execute · priv: User · T1127

```cmd
Microsoft.NodejsTools.PressAnyKey.exe normal 1 {PATH:.exe}
```

Launch specified executable as a subprocess of Microsoft.NodejsTools.PressAnyKey.exe.

