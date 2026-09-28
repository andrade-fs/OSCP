# WADComs: PyLDAPmonitor

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[WADComs|Índice WADComs]]

> Fuente: [https://wadcoms.github.io/](https://wadcoms.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

WADComs — comandos para Active Directory, ordenados por lo que TENES.

**Lo que tenés:** `Password`, `Username`, `Hash`

**Sistema:** `Linux`

## Descripción

ldapmonitor.py allows you to monitor creation, deletion and changes to LDAP objects live during your pentest.

Command Reference:

	Target IP: 10.10.10.1

	Attacker IP: 10.10.10.2

	Domain: test.local

	Username: john

	Password: password123

## Comando

```bash
python3 ldapmonitor.py -u 'john' -d 'TEST.local' -p 'password123' --dc-ip 10.10.10.1
```

## Referencias

- https://github.com/p0dalirius/LDAPmonitor/tree/master/python
