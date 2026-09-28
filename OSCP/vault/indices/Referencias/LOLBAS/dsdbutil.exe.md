# LOLBAS: dsdbutil.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Dump`

Dsdbutil is a command-line tool that is built into Windows Server. It is available if you have the AD LDS server role installed. Can be used as a command line utility to export Active Directory.

## Comandos

### Snapshoting of Active Directory NTDS.dit database

Dump · priv: Administrator · T1003.003

```cmd
dsdbutil.exe "activate instance ntds" "snapshot" "create" "quit" "quit"
```

dsdbutil supports VSS snapshot creation

### Mounting the snapshot to access the ntds.dit with `copy c:\<Snap Volume>\windows\ntds\ntds.dit c:\users\administrator\desktop\ntds.dit.bak`

Dump · priv: Administrator · T1003.003

```cmd
dsdbutil.exe "activate instance ntds" "snapshot" "mount {GUID}" "quit" "quit"
```

Mounting the snapshot with its GUID

### Deletes the snapshot

Dump · priv: Administrator · T1003.003

```cmd
dsdbutil.exe "activate instance ntds" "snapshot" "delete {GUID}" "quit" "quit"
```

Deletes the mount of the snapshot

### Mounting the snapshot identifier 1 and accessing it with `copy c:\<Snap Volume>\windows\ntds\ntds.dit c:\users\administrator\desktop\ntds.dit.bak`

Dump · priv: Administrator · T1003.003

```cmd
dsdbutil.exe "activate instance ntds" "snapshot" "create" "list all" "mount 1" "quit" "quit"
```

Mounting with snapshot identifier

### deletes the snapshot

Dump · priv: Administrator · T1003.003

```cmd
dsdbutil.exe "activate instance ntds" "snapshot" "list all" "delete 1" "quit" "quit"
```

Deletes the mount of the snapshot

