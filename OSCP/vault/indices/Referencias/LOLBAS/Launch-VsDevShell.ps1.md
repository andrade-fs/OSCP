# LOLBAS: Launch-VsDevShell.ps1

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Execute`

Locates and imports a Developer PowerShell module and calls the Enter-VsDevShell cmdlet

## Comandos

### Proxy execution

Execute · priv: User · T1216

```cmd
powershell -ep RemoteSigned -f .\Launch-VsDevShell.ps1 -VsWherePath {PATH_ABSOLUTE:.exe}
```

Execute binaries from the context of the signed script using the "VsWherePath" flag.

### Proxy execution

Execute · priv: User · T1216

```cmd
powershell -ep RemoteSigned -f .\Launch-VsDevShell.ps1 -VsInstallationPath "/../../../../../; {PATH:.exe} ;"
```

Execute binaries and commands from the context of the signed script using the "VsInstallationPath" flag.

