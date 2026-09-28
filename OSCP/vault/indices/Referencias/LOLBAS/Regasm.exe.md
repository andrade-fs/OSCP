# LOLBAS: Regasm.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `AWL Bypass`, `Execute`

Part of .NET

## Comandos

### Execute code and bypass Application whitelisting

AWL Bypass · priv: Local Admin · T1218.009

```cmd
regasm.exe {PATH:.dll}
```

Loads the target .NET DLL file and executes the RegisterClass function.

### Execute code and bypass Application whitelisting

Execute · priv: User · T1218.009

```cmd
regasm.exe /U {PATH:.dll}
```

Loads the target .DLL file and executes the UnRegisterClass function.

