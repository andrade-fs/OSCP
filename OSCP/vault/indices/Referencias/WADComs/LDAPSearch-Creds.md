# WADComs: LDAPSearch-Creds

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[WADComs|Índice WADComs]]

> Fuente: [https://wadcoms.github.io/](https://wadcoms.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

WADComs — comandos para Active Directory, ordenados por lo que TENES.

**Lo que tenés:** `Username`, `Password`

**Sistema:** `Linux`

## Descripción

ldapsearch is a Linux based tool that opens a connection to an LDAP server, binds, and performs a search using specified parameters. The following command will attempt to find sensitive information (such as leaked creds), by querying all LDAP objects, essentially dumping all the data that an anonymous user can access.

Command Reference:

	Domain: test.local
  
	Username: ldap
  
	Password: password123

## Comando

```bash
ldapsearch -h test.local -D 'ldap@test.local' -w password123 -b 'dc=test,dc=local'
```

## Referencias

- https://linux.die.net/man/1/ldapsearch
