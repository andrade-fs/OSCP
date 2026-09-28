# WADComs: SMBClient-Enum-Share-Anonymous

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[WADComs|Índice WADComs]]

> Fuente: [https://wadcoms.github.io/](https://wadcoms.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

WADComs — comandos para Active Directory, ordenados por lo que TENES.

**Lo que tenés:** `No_Creds`

**Sistema:** `Linux`

## Descripción

Smbclient is a tool used to communicate with SMB servers. The following command will connect to an SMB share `public` using anonymous login.

Command Reference:

	Target IP: 10.10.10.1

	Domain: test.local

	SMB Share: public

## Comando

```bash
smbclient \\\\test.local\\public -I 10.10.10.1 -N
```

## Referencias

- https://www.samba.org/samba/docs/current/man-html/smbclient.1.html
- https://www.madirish.net/59
