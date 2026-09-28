# LOLBAS: Regini.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `ADS`

Used to manipulate the registry

## Comandos

### Write to registry

ADS · priv: User · T1564.004

```cmd
regini.exe {PATH}:hidden.ini
```

Write registry keys from data inside the Alternate data stream.

