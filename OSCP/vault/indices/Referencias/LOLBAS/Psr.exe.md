# LOLBAS: Psr.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Reconnaissance`

Windows Problem Steps Recorder, used to record screen and clicks.

## Comandos

### Can be used to take screenshots of the user environment

Reconnaissance · priv: User · T1113

```cmd
psr.exe /start /output {PATH_ABSOLUTE:.zip} /sc 1 /gui 0
```

Record a user screen without creating a GUI. You should use "psr.exe /stop" to stop recording and create output file.

