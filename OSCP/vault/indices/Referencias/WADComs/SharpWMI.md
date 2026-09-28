# WADComs: SharpWMI

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[WADComs|Índice WADComs]]

> Fuente: [https://wadcoms.github.io/](https://wadcoms.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

WADComs — comandos para Active Directory, ordenados por lo que TENES.

**Lo que tenés:** `Shell`

**Sistema:** `Windows`

## Descripción

SharpWMI.exe is part of the GhostPack suite of tools that provides WMI functionality, such as local/remote WMI queries, remote WMI process creation, and remote execution of arbitrary VBS through WMI events. The following command will simply list all processes running on the local system.

Command Reference:

	Get all processes: "select * from win32_process"

## Comando

```bash
SharpWMI.exe action=query query="select * from win32_process"
```

## Referencias

- https://github.com/GhostPack/SharpWMI
- https://www.harmj0y.net/blog/redteaming/ghostpack/
