# WADComs: NetExec-Exec-SMB

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[WADComs|Índice WADComs]]

> Fuente: [https://wadcoms.github.io/](https://wadcoms.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

WADComs — comandos para Active Directory, ordenados por lo que TENES.

**Lo que tenés:** `Username`, `Password`

**Sistema:** `Linux`

## Descripción

"NetExec (a.k.a nxc) is a network service exploitation tool that helps automate assessing the security of large networks." - https://www.netexec.wiki/. This command will execute a powershell command on the target machine if the user has Administrator privileges. using "-x" will execute from cmd.

Command Reference:

	Target IP: 10.10.10.1

	Username: john

	Password: password123

## Comando

```bash
nxc smb 10.10.10.1 -u 'john' -p 'password123' -X '$Host'
```

## Referencias

- https://github.com/Pennyw0rth/NetExec
- https://www.netexec.wiki/
