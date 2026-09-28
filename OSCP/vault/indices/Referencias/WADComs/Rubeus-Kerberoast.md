# WADComs: Rubeus-Kerberoast

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[WADComs|Índice WADComs]]

> Fuente: [https://wadcoms.github.io/](https://wadcoms.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

WADComs — comandos para Active Directory, ordenados por lo que TENES.

**Lo que tenés:** `Shell`

**Sistema:** `Windows`

## Descripción

Rubeus' `kerberoast` module will attempt to fetch Service Principal Names that are associated with normal user accounts. What is returned is a ticket that is encrypted with the user account's password, which can then be bruteforced offline. The following command is run on a Windows machine in the victim domain.

Command Reference:

	Output File: hashes.txt

## Comando

```bash
Rubeus.exe kerberoast /outfile:hashes.txt
```

## Referencias

- https://github.com/GhostPack/Rubeus
- https://github.com/GhostPack/Rubeus#kerberoast
