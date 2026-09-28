# LOLBAS: SettingSyncHost.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Execute`

Host Process for Setting Synchronization

## Comandos

### Can be used to evade defensive countermeasures or to hide as a persistence mechanism

Execute · priv: User · T1218

```cmd
SettingSyncHost -LoadAndRunDiagScript {PATH:.exe}
```

Execute file specified in %COMSPEC%

### Can be used to evade defensive countermeasures or to hide as a persistence mechanism. Additionally, effectively act as a -WindowStyle Hidden option (as there is in PowerShell) for any arbitrary batch file.

Execute · priv: User · T1218

```cmd
SettingSyncHost -LoadAndRunDiagScriptNoCab {PATH:.bat}
```

Execute a batch script in the background (no window ever pops up) which can be subverted to running arbitrary programs by setting the current working directory to %TMP% and creating files such as reg.bat/reg.exe in that directory thereby causing them to execute instead of the ones in C:\Windows\System32.

