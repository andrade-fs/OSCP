# WADComs: SharpLDAPmonitor

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[WADComs|Índice WADComs]]

> Fuente: [https://wadcoms.github.io/](https://wadcoms.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

WADComs — comandos para Active Directory, ordenados por lo que TENES.

**Lo que tenés:** `Password`, `Username`

**Sistema:** `Windows`

## Descripción

SharpLDAPmonitor.exe allows you to monitor creation, deletion and changes to LDAP objects live during your pentest.

Command Reference:

	Target IP: 10.10.10.1

	Attacker IP: 10.10.10.2

	Domain: test.local

	Username: john

	Password: password123

## Comando

```bash
SharpLDAPmonitor.exe /dcip:10.10.10.1 /user:TEST.local\john /pass:password123
```

## Referencias

- https://github.com/p0dalirius/LDAPmonitor/tree/master/csharp
