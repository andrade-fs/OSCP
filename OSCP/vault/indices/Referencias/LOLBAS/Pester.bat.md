# LOLBAS: Pester.bat

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Execute`

Used as part of the Powershell pester

## Comandos

### Proxy execution

Execute · priv: User · T1216

```cmd
Pester.bat [/help|?|-?|/?] "$null; {CMD}"
```

Execute code using Pester. The third parameter can be anything. The fourth is the payload.

### Proxy execution

Execute · priv: User · T1216

```cmd
Pester.bat ;{PATH:.exe}
```

Execute code using Pester. Example here executes specified executable.

