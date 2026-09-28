# WADComs: NetExec-Creds-coerce_plus

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[WADComs|Índice WADComs]]

> Fuente: [https://wadcoms.github.io/](https://wadcoms.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

WADComs — comandos para Active Directory, ordenados por lo que TENES.

**Lo que tenés:** `Username`, `Password`

**Sistema:** `Linux`, `Windows`

## Descripción

"NetExec (a.k.a nxc) is a network pentesting suite that has many modules that can be listed via nxc <protocol> -L. The coerece_plus module will enumarate a target ip, dnsname, list of targets or ip range for different coherence attacks. It will indicate in the output which a target is vulnrable to. Providing you also a means for exploit by adding where your listener/reciving system is(-LISTENER=10.10.10.1) and which exploit you want it to use. The module was recently updated 7 days ago to work on the latest windows build"

  Command Reference:

      Target IP: 10.10.10.1

      Username: john

      Password: password123

## Comando

```bash
nxc smb 10.10.10.1 -u john -p password123 -M coerce_plus
```

## Referencias

- https://blog.redteam-pentesting.de/2025/windows-coercion/
- https://github.com/Pennyw0rth/NetExec
- https://www.netexec.wiki/smb-protocol/scan-for-vulnerabilities
