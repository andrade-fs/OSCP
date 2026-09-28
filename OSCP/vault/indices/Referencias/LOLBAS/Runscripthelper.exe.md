# LOLBAS: Runscripthelper.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Execute`

Execute target PowerShell script

## Comandos

### Bypass constrained language mode and execute Powershell script

Execute · priv: User · T1218

```cmd
runscripthelper.exe surfacecheck \\?\{PATH_ABSOLUTE:.txt} {PATH_ABSOLUTE:folder}
```

Execute the PowerShell script with .txt extension

