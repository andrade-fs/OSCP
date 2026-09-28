# WADComs: Kerbrute-BruteUser

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[WADComs|Índice WADComs]]

> Fuente: [https://wadcoms.github.io/](https://wadcoms.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

WADComs — comandos para Active Directory, ordenados por lo que TENES.

**Lo que tenés:** `Username`

**Sistema:** `Linux`, `Windows`

## Descripción

ropnop's kerbrute bruteforces and enumerates valid Active Directory accounts through Kerberos Pre-Authentication. The following command will bruteforce an account against a list of provided passwords given a username.

Command Reference:

	Domain: test.local

	Password List: passwords.txt

	Username: john

## Comando

```bash
kerbrute bruteuser -d test.local passwords.txt john
```

## Referencias

- https://github.com/ropnop/kerbrute
