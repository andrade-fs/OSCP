# LOLBAS: ComputerDefaults.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `UAC Bypass`

ComputerDefaults.exe is a Windows system utility for managing default applications for tasks like web browsing, emailing, and media playback.

## Comandos

### Execute a binary or script as a high-integrity process without a UAC prompt.

UAC Bypass · priv: User · T1548.002

```cmd
ComputerDefaults.exe
```

Upon execution, ComputerDefaults.exe checks two registry values at HKEY_CURRENT_USER\Software\Classes\ms-settings\Shell\open\command; if these are set by an attacker, the set command will be executed as a high-integrity process without a UAC prompt being displayed to the user. See 'resources' for which registry keys/values to set.

