# LOLBAS: Dotnet.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `AWL Bypass`, `Execute`

dotnet.exe comes with .NET Framework

## Comandos

### Execute code bypassing AWL

AWL Bypass · priv: User · T1218

```cmd
dotnet.exe {PATH:.dll}
```

dotnet.exe will execute any DLL even if applocker is enabled.

### Execute DLL

Execute · priv: User · T1218

```cmd
dotnet.exe {PATH:.dll}
```

dotnet.exe will execute any DLL.

### Execute arbitrary F# code

Execute · priv: User · T1059

```cmd
dotnet.exe fsi
```

dotnet.exe will open a console which allows for the execution of arbitrary F# commands

### Execute code bypassing AWL

AWL Bypass · priv: User · T1218

```cmd
dotnet.exe msbuild {PATH:.csproj}
```

dotnet.exe with msbuild (SDK Version) will execute unsigned code

