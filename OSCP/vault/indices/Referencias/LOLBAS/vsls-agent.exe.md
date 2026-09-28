# LOLBAS: vsls-agent.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Execute`

Agent for Visual Studio Live Share (Code Collaboration)

## Comandos

### Execute proxied payload with Microsoft signed binary

Execute · priv: User · T1218

```cmd
vsls-agent.exe --agentExtensionPath {PATH_ABSOLUTE:.dll}
```

Load a library payload using the --agentExtensionPath parameter (32-bit)

