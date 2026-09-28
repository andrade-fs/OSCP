# LOLBAS: Pnputil.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Execute`

Used for installing drivers

## Comandos

### Add malicious driver

Execute · priv: Administrator · T1547

```cmd
pnputil.exe -i -a {PATH_ABSOLUTE:.inf}
```

Used for installing drivers

