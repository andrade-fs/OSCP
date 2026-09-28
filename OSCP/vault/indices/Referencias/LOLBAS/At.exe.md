# LOLBAS: At.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Execute`

Schedule periodic tasks

## Comandos

### Create a recurring task, to eg. to keep reverse shell session(s) alive

Execute · priv: Local Admin · T1053.002

```cmd
C:\Windows\System32\at.exe 09:00 /interactive /every:m,t,w,th,f,s,su {CMD}
```

Create a recurring task to execute every day at a specific time.

