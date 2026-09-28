# WADComs: bloodyAD-Wite-Properties

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[WADComs|Índice WADComs]]

> Fuente: [https://wadcoms.github.io/](https://wadcoms.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

WADComs — comandos para Active Directory, ordenados por lo que TENES.

**Lo que tenés:** `Username`, `Password`

**Sistema:** `Linux`

## Descripción

BloodyAD can be used to set, write and delete properties of objects in AD. Given a user:pass, you can use bloodyAD to which objects and what properties of
those objects are writeable to the user:pass given. Thus if you use -u john -p john, this command will show you what objects and properties
can john write to

Command Reference:
  Target IP: 10.10.10.1

	Domain: test.local

  Username: john

	Password: password123

## Comando

```bash
bloodyAD --host 10.10.10.1 -d test.local -u john -p password123 -d test.local get writable --detail
```

## Referencias

- https://github.com/CravateRouge/bloodyAD
- https://adminions.ca/books/active-directory-enumeration-and-exploitation/page/bloodyad
