# LOLBAS: Register-cimprovider.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Execute`

Used to register new wmi providers

## Comandos

### Execute code within dll file

Execute · priv: User · T1218

```cmd
Register-cimprovider -path {PATH_ABSOLUTE:.dll}
```

Load the target .DLL.

