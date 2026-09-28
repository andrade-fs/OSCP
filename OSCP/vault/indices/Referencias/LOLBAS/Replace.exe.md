# LOLBAS: Replace.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Copy`, `Download`

Used to replace file with another file

## Comandos

### Copy files

Copy · priv: User · T1105

```cmd
replace.exe {PATH_ABSOLUTE:.cab} {PATH_ABSOLUTE:folder} /A
```

Copy .cab file to destination

### Download file

Download · priv: User · T1105

```cmd
replace.exe {PATH_SMB:.exe} {PATH_ABSOLUTE:folder} /A
```

Download/Copy executable to specified folder

