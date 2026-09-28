# WADComs: Impacket-addcomputer-SMB

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[WADComs|Índice WADComs]]

> Fuente: [https://wadcoms.github.io/](https://wadcoms.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

WADComs — comandos para Active Directory, ordenados por lo que TENES.

**Lo que tenés:** `Username`, `Password`

**Sistema:** `Linux`, `Windows`

## Descripción

Impacket's addcomputer.py will add a computer account to the domain and set its password. The following command will create a new computer over the SMB by specifying the `SAMR` method.

Command Reference:

	Target IP: 10.10.10.1

	Domain: test.local

	New Computer Password: TestPassword123

	New Computer Name: testComputer

	Username: john

	Password: password123

## Comando

```bash
python3 addcomputer.py -method SAMR -dc-ip 10.10.10.1 -computer-pass TestPassword321 -computer-name testComputer test.local/john:password123
```

## Referencias

- https://github.com/SecureAuthCorp/impacket/blob/master/examples/addcomputer.py
- http://blog.redxorblue.com/2019/12/no-shells-required-using-impacket-to.html
