# LOLBAS: Msbuild.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `AWL Bypass`, `Execute`

Used to compile and execute code

## Comandos

### Compile and run code

AWL Bypass · priv: User · T1127.001

```cmd
msbuild.exe {PATH:.xml}
```

Build and execute a C# project stored in the target XML file.

### Compile and run code

Execute · priv: User · T1127.001

```cmd
msbuild.exe {PATH:.csproj}
```

Build and execute a C# project stored in the target csproj file.

### Execute DLL

Execute · priv: User · T1127.001

```cmd
msbuild.exe /logger:TargetLogger,{PATH_ABSOLUTE:.dll};MyParameters,Foo
```

Executes generated Logger DLL file with TargetLogger export.

### Execute project file that contains XslTransformation tag parameters

Execute · priv: User · T1127.001

```cmd
msbuild.exe {PATH:.proj}
```

Execute JScript/VBScript code through XML/XSL Transformation. Requires Visual Studio MSBuild v14.0+.

### Bypass command-line based detections

Execute · priv: User · T1036

```cmd
msbuild.exe @{PATH:.rsp}
```

By putting any valid msbuild.exe command-line options in an RSP file and calling it as above will interpret the options as if they were passed on the command line.

