# WADComs: NetExec-SMB-Timeroasting

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[WADComs|Índice WADComs]]

> Fuente: [https://wadcoms.github.io/](https://wadcoms.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

WADComs — comandos para Active Directory, ordenados por lo que TENES.

**Lo que tenés:** `Hash`, `Username`

**Sistema:** `Linux`, `Windows`

## Descripción

NetExec (formerly CrackMapExec) performs a Timeroasting attack via the SMB service.
This command targets the remote Windows host and abuses the Kerberos protocol by 
manipulating ticket lifetimes or requesting renewable service tickets. 
It can help attackers obtain long-lived Kerberos tickets for offline cracking 
or later lateral movement.

Command Reference:

	Target IP: 10.10.10.1
	Module: timeroast

## Comando

```bash
nxc smb 10.10.10.1 -M timeroast
```

## Referencias

- https://github.com/Pennyw0rth/NetExec
- https://cybersecurity.bureauveritas.com/blog/timeroasting-attacking-trust-accounts-in-active-directory
