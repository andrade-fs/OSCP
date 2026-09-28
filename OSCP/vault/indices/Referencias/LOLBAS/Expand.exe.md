# LOLBAS: Expand.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `ADS`, `Copy`, `Download`

Binary that expands one or more compressed files

## Comandos

### Use to copies the source file to the destination file

Download · priv: User · T1105

```cmd
expand {PATH_SMB:.bat} {PATH_ABSOLUTE:.bat}
```

Copies source file to destination.

### Copies files from A to B

Copy · priv: User · T1105

```cmd
expand {PATH_ABSOLUTE:.source.ext} {PATH_ABSOLUTE:.dest.ext}
```

Copies source file to destination.

### Copies files from A to B

ADS · priv: User · T1564.004

```cmd
expand {PATH_SMB:.bat} {PATH_ABSOLUTE}:file.bat
```

Copies source file to destination Alternate Data Stream (ADS)

