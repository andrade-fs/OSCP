# LOLBAS: Nmcap.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Reconnaissance`

Command-line packet capture utility from Microsoft Network Monitor 3.x.

## Comandos

### Capture network traffic on windows to collect sensitive data.

Reconnaissance · priv: Administrator · T1040

```cmd
nmcap.exe /network * /capture /file {PATH_ABSOLUTE:.cap}
```

Start capture on all network adapters and save to specified .cap (circular) file.
Optionally, one can add:
- `/TerminateWhen /TimeAfter 30 seconds` to auto-terminate after a relative times (e.g. 30 seconds);
- `/TerminateWhen /Time 04:52:00 AM 9/17/2025` to auto-terminate after a specific date/time;
- `/TerminateWhen /KeyPress x` to terminate when a specific key is pressed.

