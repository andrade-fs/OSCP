# WADComs: Responder-Analyze

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[WADComs|Índice WADComs]]

> Fuente: [https://wadcoms.github.io/](https://wadcoms.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

WADComs — comandos para Active Directory, ordenados por lo que TENES.

**Lo que tenés:** `No_Creds`

**Sistema:** `Linux`, `Windows`

## Descripción

Responder is an LLMNR, NBT-NS, and MDNS poisoner. It will answer to specific NBT-NS (NetBIOS Name Service) queries based on their name suffix. By default, the tool will only answer to File Server Service request, which is for SMB. The following command will put Responder in analyze mode, listening for NBT-NS, BROWSER, and LLMNR requests without responding.

Command Reference:

	Interface: eth0

## Comando

```bash
Responder -I eth0 -A
```

## Referencias

- https://github.com/lgandx/Responder
- https://www.ivoidwarranties.tech/posts/pentesting-tuts/responder/cheatsheet/
