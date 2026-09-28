# WADComs: Kerbrute-BruteForce

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[WADComs|Índice WADComs]]

> Fuente: [https://wadcoms.github.io/](https://wadcoms.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

WADComs — comandos para Active Directory, ordenados por lo que TENES.

**Lo que tenés:** `No_Creds`

**Sistema:** `Linux`

## Descripción

ropnop's kerbrute bruteforces and enumerates valid Active Directory accounts through Kerberos Pre-Authentication. The following command will attempt to brute force valid username and passwords logins given a list of credentials (in the format `username:password`).

Command Reference:

	Domain: test.local

	Credential List: credentials.txt

## Comando

```bash
cat credentials.txt | kerbrute_linux_amd64 -d test.local bruteforce -
```

## Referencias

- https://github.com/ropnop/kerbrute
