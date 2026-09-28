# LOLBAS: Wlrmdr.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Execute`

Windows Logon Reminder executable

## Comandos

### Use wlrmdr as a proxy binary to evade defensive countermeasures

Execute · priv: User · T1202

```cmd
wlrmdr.exe -s 3600 -f 0 -t _ -m _ -a 11 -u {PATH:.exe}
```

Execute executable with wlrmdr.exe as parent process

