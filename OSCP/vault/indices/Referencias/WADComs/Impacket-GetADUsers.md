# WADComs: Impacket-GetADUsers

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[WADComs|Índice WADComs]]

> Fuente: [https://wadcoms.github.io/](https://wadcoms.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

WADComs — comandos para Active Directory, ordenados por lo que TENES.

**Lo que tenés:** `Username`, `Password`

**Sistema:** `Linux`, `Windows`

## Descripción

Impacket's GetADUsers.py will attempt to gather data about the domain's users and their corresponding email addresses.

Command Reference:

	Target IP: 10.10.10.1

	Domain: test.local

	Username: john

	Password: password123

## Comando

```bash
python3 GetADUsers.py -all test.local/john:password123 -dc-ip 10.10.10.1
```

## Referencias

- https://github.com/SecureAuthCorp/impacket/blob/master/examples/GetADUsers.py
