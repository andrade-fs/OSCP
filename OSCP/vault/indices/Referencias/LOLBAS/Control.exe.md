# LOLBAS: Control.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `ADS`, `Execute`

Binary used to launch controlpanel items in Windows

## Comandos

### Can be used to evade defensive countermeasures or to hide as a persistence mechanism

ADS · priv: User · T1218.002

```cmd
control.exe {PATH_ABSOLUTE}:evil.dll
```

Execute evil.dll which is stored in an Alternate Data Stream (ADS).

### Use to execute code and bypass application whitelisting

Execute · priv: User · T1218.002

```cmd
control.exe {PATH_ABSOLUTE:.cpl}
```

Execute .cpl file. A CPL is a DLL file with CPlApplet export function)

