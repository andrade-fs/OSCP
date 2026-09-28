# LOLBAS: Provlaunch.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Execute`

Launcher process

## Comandos

### Executes arbitrary command

Execute · priv: Administrator · T1218

```cmd
provlaunch.exe LOLBin
```

Executes command defined in the Registry. Requires 3 levels of the key structure containing some keywords. Such keys may be created with two reg.exe commands, e.g. `reg.exe add HKLM\SOFTWARE\Microsoft\Provisioning\Commands\LOLBin\dummy1 /v altitude /t REG_DWORD /d 0` and `reg add HKLM\SOFTWARE\Microsoft\Provisioning\Commands\LOLBin\dummy1\dummy2 /v Commandline /d calc.exe`. Registry keys are deleted after successful execution.

