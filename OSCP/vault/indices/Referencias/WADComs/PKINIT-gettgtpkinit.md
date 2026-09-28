# WADComs: PKINIT-gettgtpkinit

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[WADComs|Índice WADComs]]

> Fuente: [https://wadcoms.github.io/](https://wadcoms.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

WADComs — comandos para Active Directory, ordenados por lo que TENES.

**Lo que tenés:** `Username`, `Password`, `PFX`

**Sistema:** `Linux`, `Windows`

## Descripción

PKINIT gettgtpkinit.py request a TGT using a PFX file, either as file or as base64 encoded blob, or PEM files for cert+key. This uses Kerberos PKINIT and will output a TGT into the specified ccache. It will also print the AS-REP encryption key which you may need for the getnthash.py tool.

Command Reference:

  Domain: test.local

  Host that you got the certificate from: DC01

  PFX file: crt.pfx

  PFX file password: password123

  TGT requested: out.ccache

## Comando

```bash
python3 gettgtpkinit.py test.local/DC01\$ -cert-pfx crt.pfx -pfx-pass password123 out.ccache
```

## Referencias

- https://github.com/dirkjanm/PKINITtools
- https://dirkjanm.io/ntlm-relaying-to-ad-certificate-services/
