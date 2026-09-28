# LOLBAS: Sftp.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Execute`

sftp.exe is a Windows command-line utility that uses the Secure File Transfer Protocol (SFTP) to securely transfer files between a local machine and a remote server.

## Comandos

### Proxy execution of specified command, can be used as a defensive evasion.

Execute · priv: User · T1202

```cmd
sftp -o ProxyCommand="{CMD}" .
```

Spawns ssh.exe which in turn spawns the specified command line. See also this project's entry for ssh.exe.

### Proxy execution of specified command, can be used as a defensive evasion.

Execute · priv: User · T1202

```cmd
sftp -D "{CMD}"
```

Spawns ssh.exe which in turn spawns the specified command line. See also this project's entry for ssh.exe.

