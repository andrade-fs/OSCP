# WADComs: SMBMap-Enum-File

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[WADComs|Índice WADComs]]

> Fuente: [https://wadcoms.github.io/](https://wadcoms.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

WADComs — comandos para Active Directory, ordenados por lo que TENES.

**Lo que tenés:** `Username`, `Password`

**Sistema:** `Linux`, `Windows`

## Descripción

SMBMap is a tool used to enumerate SMB share drives, including listing share drive permissions, share contents, upload/download functionality, file name enumeration, and remote command execution. The following command will enumerate a list of SMB hosts for files and filenames containing the keyword 'password'.

Command Reference:

	Domain: test.local

	SMB Hosts: smb-hosts.txt

	Username: john

	Password: password123

## Comando

```bash
python3 smbmap.py --host-file smb-hosts.txt -u john -p 'password123' -d test.local -F password
```

## Referencias

- https://github.com/ShawnDEvans/smbmap
- https://www.nopsec.com/blog/smbmap-wield-it-like-the-creator/
