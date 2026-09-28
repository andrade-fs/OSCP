# LOLBAS: AppCert.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Execute`

Windows App Certification Kit command-line tool.

## Comandos

### Performs execution of specified file, can be used as a defense evasion

Execute · priv: Administrator · T1127

```cmd
appcert.exe test -apptype desktop -setuppath {PATH_ABSOLUTE:.exe} -reportoutputpath {PATH_ABSOLUTE:.xml}
```

Execute an executable file via the Windows App Certification Kit command-line tool.

### Execute custom made MSI file with malicious code

Execute · priv: Administrator · T1218.007

```cmd
appcert.exe test -apptype desktop -setuppath {PATH_ABSOLUTE:.msi} -setupcommandline /q -reportoutputpath {PATH_ABSOLUTE:.xml}
```

Install an MSI file via an msiexec instance spawned via appcert.exe as parent process.

