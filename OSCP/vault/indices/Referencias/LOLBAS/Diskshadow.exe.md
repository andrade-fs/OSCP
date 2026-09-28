# LOLBAS: Diskshadow.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Dump`, `Execute`

Diskshadow.exe is a tool that exposes the functionality offered by the volume shadow copy Service (VSS).

## Comandos

### Use diskshadow to exfiltrate data from VSS such as NTDS.dit

Dump · priv: User · T1003.003

```cmd
diskshadow.exe /s {PATH:.txt}
```

Execute commands using diskshadow.exe from a prepared diskshadow script.

### Use diskshadow to bypass defensive counter measures

Execute · priv: User · T1202

```cmd
diskshadow> exec {PATH:.exe}
```

Execute commands using diskshadow.exe to spawn child process

