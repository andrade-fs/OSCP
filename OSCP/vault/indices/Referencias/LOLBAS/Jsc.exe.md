# LOLBAS: Jsc.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Compile`

Binary file used by .NET to compile JavaScript code to .exe or .dll format

## Comandos

### Compile attacker code on system. Bypass defensive counter measures.

Compile · priv: User · T1127

```cmd
jsc.exe {PATH:.js}
```

Use jsc.exe to compile JavaScript code stored in the provided .JS file and generate a .EXE file with the same name.

### Compile attacker code on system. Bypass defensive counter measures.

Compile · priv: User · T1127

```cmd
jsc.exe /t:library {PATH:.js}
```

Use jsc.exe to compile JavaScript code stored in the .JS file and generate a DLL file with the same name.

