# LOLBAS: Schtasks.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Execute`

Schedule periodic tasks

## Comandos

### Create a recurring task to keep reverse shell session(s) alive

Execute · priv: User · T1053.005

```cmd
schtasks /create /sc minute /mo 1 /tn "Reverse shell" /tr "{CMD}"
```

Create a recurring task to execute every minute.

### Create a remote task to run daily relative to the the time of creation

Execute · priv: Administrator · T1053.005

```cmd
schtasks /create /s targetmachine /tn "MyTask" /tr "{CMD}" /sc daily
```

Create a scheduled task on a remote computer for persistence/lateral movement

