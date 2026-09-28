# LOLBAS: dotnet-trace.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Execute`

.NET diagnostic tool for collecting runtime traces from .NET applications. Installed via 'dotnet tool install --global dotnet-trace' (.NET SDK required).

## Comandos

### Execute a child process under the guise of a legitimate .NET diagnostic tool.

Execute · priv: User · T1127

```cmd
dotnet-trace.exe collect --duration 00:00:01 -- {PATH:.exe}
```

Launches the specified executable as a child process while collecting runtime trace data for 1 second during execution.

