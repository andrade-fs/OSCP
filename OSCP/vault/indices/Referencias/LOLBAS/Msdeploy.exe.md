# LOLBAS: Msdeploy.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `AWL Bypass`, `Copy`, `Execute`

Microsoft tool used to deploy Web Applications.

## Comandos

### Local execution of batch file using msdeploy.exe.

Execute · priv: User · T1218

```cmd
msdeploy.exe -verb:sync -source:RunCommand -dest:runCommand="{PATH_ABSOLUTE:.bat}"
```

Launch .bat file via msdeploy.exe.

### Local execution of batch file using msdeploy.exe.

AWL Bypass · priv: User · T1218

```cmd
msdeploy.exe -verb:sync -source:RunCommand -dest:runCommand="{PATH_ABSOLUTE:.bat}"
```

Launch .bat file via msdeploy.exe.

### Copy file.

Copy · priv: User · T1105

```cmd
msdeploy.exe -verb:sync -source:filePath={PATH_ABSOLUTE:.source.ext} -dest:filePath={PATH_ABSOLUTE:.dest.ext}
```

Copy file from source to destination.

