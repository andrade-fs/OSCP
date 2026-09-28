# WADComs: SMBClient-List-Shares

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[WADComs|Índice WADComs]]

> Fuente: [https://wadcoms.github.io/](https://wadcoms.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

WADComs — comandos para Active Directory, ordenados por lo que TENES.

**Lo que tenés:** `Username`, `Password`

**Sistema:** `Linux`

## Descripción

Smbclient is a tool used to communicate with SMB servers. The following command will list out all available shares on the target server using valid credentials.

Command Reference:

	Target IP: 10.10.10.1

	Domain: test.local

	Username: john

	Password: password123

## Comando

```bash
smbclient -L \\test.local -I 10.10.10.1 -U john password123
```

## Referencias

- https://www.samba.org/samba/docs/current/man-html/smbclient.1.html
