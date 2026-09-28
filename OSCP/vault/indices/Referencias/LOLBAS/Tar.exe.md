# LOLBAS: Tar.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `ADS`, `Copy`

Used by Windows to extract and create archives.

## Comandos

### Can be used to evade defensive countermeasures, or to hide as part of a persistence mechanism

ADS · priv: User · T1564.004

```cmd
tar -cf {PATH}:ads {PATH_ABSOLUTE:folder}
```

Compress one or more files to an alternate data stream (ADS).

### Can be used to evade defensive countermeasures, or to hide as part of a persistence mechanism

ADS · priv: User · T1564.004

```cmd
tar -xf {PATH}:ads
```

Decompress a compressed file from an alternate data stream (ADS).

### Copy files

Copy · priv: User · T1105

```cmd
tar -xf {PATH_SMB:.tar}
```

Extracts archive.tar from the remote (internal) host to the current host.

