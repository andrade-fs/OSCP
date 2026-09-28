# LOLBAS: Colorcpl.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Copy`

Binary that handles color management

## Comandos

### Copies file(s) to a subfolder of a generally trusted folder (c:\Windows\System32), which can be used to hide files or make them blend into the environment.

Copy · priv: User · T1036.005

```cmd
colorcpl {PATH}
```

Copies the referenced file to C:\Windows\System32\spool\drivers\color\.

