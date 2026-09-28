# LOLBAS: Tracker.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `AWL Bypass`, `Execute`

Tool included with Microsoft .Net Framework.

## Comandos

### Injection of locally stored DLL file into target process.

Execute · priv: User · T1127

```cmd
Tracker.exe /d {PATH:.dll} /c C:\Windows\write.exe
```

Use tracker.exe to proxy execution of an arbitrary DLL into another process. Since tracker.exe is also signed it can be used to bypass application whitelisting solutions.

### Injection of locally stored DLL file into target process.

AWL Bypass · priv: User · T1127

```cmd
Tracker.exe /d {PATH:.dll} /c C:\Windows\write.exe
```

Use tracker.exe to proxy execution of an arbitrary DLL into another process. Since tracker.exe is also signed it can be used to bypass application whitelisting solutions.

