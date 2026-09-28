# WADComs: Nmap-Krb5-Enum-Users

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[WADComs|Índice WADComs]]

> Fuente: [https://wadcoms.github.io/](https://wadcoms.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

WADComs — comandos para Active Directory, ordenados por lo que TENES.

**Lo que tenés:** `No_Creds`

**Sistema:** `Linux`, `Windows`

## Descripción

Nmap's `krb5-enum-users` script attempts to bruteforce and enumerate valid Active Directory accounts through Kerberos Pre-Authentication. The following command will attempt to enumerate valid usernames given a list of usernames to try.

Command Reference:

	Target IP: 10.10.10.1

	Domain: test.local

	Username List: usernames.txt

## Comando

```bash
nmap -p 88 --script=krb5-enum-users --script-args krb5-enum-users.realm='test.local',userdb=usernames.txt 10.10.10.1
```

## Referencias

- https://nmap.org/download.html
- https://nmap.org/nsedoc/scripts/krb5-enum-users.html
