# LOLBAS: WorkFolders.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Execute`

Work Folders

## Comandos

### Can be used to evade defensive countermeasures or to hide as a persistence mechanism

Execute · priv: User · T1218

```cmd
WorkFolders
```

Execute `control.exe` in the current working directory

### Proxy execution of a malicious payload via App Paths registry hijacking.

Execute · priv: User · T1218

```cmd
WorkFolders
```

`WorkFolders` attempts to execute `control.exe`. By modifying the default value of the App Paths registry key for `control.exe` in `HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\control.exe`, an attacker can achieve proxy execution.

