# LOLBAS: dtutil.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Copy`

Microsoft command line utility used to manage SQL Server Integration Services packages.

## Comandos

### Use to copies the source file to the destination file

Copy · priv: Administrator · T1105

```cmd
dtutil.exe /FILE {PATH_ABSOLUTE:.source.ext} /COPY FILE;{PATH_ABSOLUTE:.dest.ext}
```

Copy file from source to destination

