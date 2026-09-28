# WADComs: Impacket-Services

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[WADComs|Índice WADComs]]

> Fuente: [https://wadcoms.github.io/](https://wadcoms.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

WADComs — comandos para Active Directory, ordenados por lo que TENES.

**Lo que tenés:** `Password`, `Username`

**Sistema:** `Linux`, `Windows`

## Descripción

Impacket's services.py communicates with Windows services using the MSRPC interface. It can perform many different actions on any service.

Command Reference:

	Target IP: 10.10.10.1

	Domain: test.local

	Username: john

	Password: password123

	Action: list

## Comando

```bash
python3 services.py test.local/john:password123@10.10.10.1 list
```

## Referencias

- https://github.com/SecureAuthCorp/impacket/blob/master/examples/services.py
- https://www.hackingarticles.in/impacket-guide-smb-msrpc/
