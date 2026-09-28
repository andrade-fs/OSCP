# LOLBAS: Csc.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Compile`

Binary file used by .NET Framework to compile C# code

## Comandos

### Compile attacker code on system. Bypass defensive counter measures.

Compile · priv: User · T1127

```cmd
csc.exe -out:{PATH:.exe} {PATH:.cs}
```

Use csc.exe to compile C# code, targeting the .NET Framework, stored in the specified .cs file and output the compiled version to the specified .exe path.

### Compile attacker code on system. Bypass defensive counter measures.

Compile · priv: User · T1127

```cmd
csc -target:library {PATH:.cs}
```

Use csc.exe to compile C# code, targeting the .NET Framework, stored in the specified .cs file and output the compiled version to a DLL file with the same name.

