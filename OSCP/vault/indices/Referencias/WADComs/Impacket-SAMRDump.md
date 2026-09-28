# WADComs: Impacket-SAMRDump

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[WADComs|Índice WADComs]]

> Fuente: [https://wadcoms.github.io/](https://wadcoms.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

WADComs — comandos para Active Directory, ordenados por lo que TENES.

**Lo que tenés:** `Password`, `Username`

**Sistema:** `Linux`, `Windows`

## Descripción

Impacket's samrdump.py communicates with the Security Account Manager Remote (SAMR) interface to list system user accounts, available resource shares, and other sensitive information.

Command Reference:

	Target IP: 10.10.10.1

	Domain: test.local

	Username: john

	Password: password123

## Comando

```bash
python3 samrdump.py test.local/john:password123@10.10.10.1
```

## Referencias

- https://github.com/SecureAuthCorp/impacket/blob/master/examples/samrdump.py
- https://www.hackingarticles.in/impacket-guide-smb-msrpc/
