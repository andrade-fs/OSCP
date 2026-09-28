# WADComs: Impacket-atexec-Creds

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[WADComs|Índice WADComs]]

> Fuente: [https://wadcoms.github.io/](https://wadcoms.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

WADComs — comandos para Active Directory, ordenados por lo que TENES.

**Lo que tenés:** `Password`, `Username`

**Sistema:** `Linux`, `Windows`

## Descripción

Impacket's atexec.py uses the Task Scheduler service on the remote Windows host to execute the given command. It will create a windows task with a random name, trigger the task, and then delete it. The following command executes `whoami` on the remote Windows host.

Command Reference:

	Target IP: 10.10.10.1

	Domain: test.local

	Username: john

	Password: password123

	Command Executed: whoami

## Comando

```bash
python3 atexec.py test.local/john:password123@10.10.10.1 whoami
```

## Referencias

- https://github.com/SecureAuthCorp/impacket/blob/master/examples/atexec.py
- https://u0041.co/blog/post/1
