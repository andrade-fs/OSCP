# LOLBAS: write.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Execute`

Windows Write

## Comandos

### Execute binary through legitimate proxy. This might be utilized to confuse detection solutions that rely on parent-child relationships.

Execute · priv: User · T1218

```cmd
write.exe
```

Executes a binary provided in default value of `HKCU\Software\Microsoft\Windows\CurrentVersion\App Paths\wordpad.exe`.

