# LOLBAS: winget.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `AWL Bypass`, `Download`, `Execute`

Windows Package Manager tool

## Comandos

### Download and execute an arbitrary file from the internet

Execute · priv: Local Administrator - required to enable local manifest setting · T1105

```cmd
winget.exe install --manifest {PATH:.yml}
```

Downloads a file from the web address specified in .yml file and executes it on the system. Local manifest setting must be enabled in winget for it to work: `winget settings --enable LocalManifestFiles`

### Download and install software from Microsoft Store, even if Microsoft Store App is blocked

Download · priv: User · T1105

```cmd
winget.exe install --accept-package-agreements -s msstore {name or ID}
```

Download and install any software from the Microsoft Store using its name or Store ID, even if the Microsoft Store App itself is blocked on the machine. For example, use "Sysinternals Suite" or `9p7knl5rwt25` for obtaining ProcDump, PsExec via the Sysinternals Suite. Note: a Microsoft account is required for this.

### Download and install software from Microsoft Store, even if Microsoft Store App is blocked, and AppLocker is activated on the machine

AWL Bypass · priv: User · T1105

```cmd
winget.exe install --accept-package-agreements -s msstore {name or ID}
```

Download and install any software from the Microsoft Store using its name or Store ID, even if the Microsoft Store App itself is blocked on the machine, and even if AppLocker is active on the machine. For example, use "Sysinternals Suite" or `9p7knl5rwt25` for obtaining ProcDump, PsExec via the Sysinternals Suite. Note: a Microsoft account is required for this.

