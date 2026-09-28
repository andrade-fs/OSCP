# WADComs: Sift-Network-Creds

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[WADComs|Índice WADComs]]

> Fuente: [https://wadcoms.github.io/](https://wadcoms.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

WADComs — comandos para Active Directory, ordenados por lo que TENES.

**Lo que tenés:** `Username`, `Password`

**Sistema:** `Windows`

## Descripción

Sift can scan SMB hosts without Active Directory discovery. This command scans a subnet using domain credentials.

Command Reference:

  Target Subnet: 10.10.10.0/24

  Domain: test.local

  Username: john

  Password: password123

## Comando

```bash
.\sift.exe network --subnet 10.10.10.0/24 --username john --password password123 --domain test.local --output sift-findings.log
```

## Referencias

- https://github.com/Stratus-Security/Sift
