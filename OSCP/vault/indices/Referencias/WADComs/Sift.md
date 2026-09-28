# WADComs: Sift

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[WADComs|Índice WADComs]]

> Fuente: [https://wadcoms.github.io/](https://wadcoms.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

WADComs — comandos para Active Directory, ordenados por lo que TENES.

**Lo que tenés:** `Username`, `Password`

**Sistema:** `Windows`

## Descripción

Sift finds credentials, secrets and sensitive files on accessible SMB shares. This command discovers domain computers over LDAP and scans their shares using the supplied account.

Command Reference:

  Domain: test.local

  Domain Controller: 10.10.10.1

  Username: john

  Password: password123

## Comando

```bash
.\sift.exe domain --username john --password password123 --domain test.local --domain-controller 10.10.10.1 --output sift-findings.log
```

## Referencias

- https://github.com/Stratus-Security/Sift
