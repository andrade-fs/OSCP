# LOLBAS: Zipfldr.dll

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Execute`

Compressed Folder library

## Comandos

### Launch an executable.

Execute · priv: User · T1218.011

```cmd
rundll32.exe zipfldr.dll,RouteTheCall {PATH:.exe}
```

Launch an executable payload by calling RouteTheCall.

### Launch an executable.

Execute · priv: User · T1218.011

```cmd
rundll32.exe zipfldr.dll,RouteTheCall file://^C^:^/^W^i^n^d^o^w^s^/^s^y^s^t^e^m^3^2^/^c^a^l^c^.^e^x^e
```

Launch an executable payload by calling RouteTheCall (obfuscated).

