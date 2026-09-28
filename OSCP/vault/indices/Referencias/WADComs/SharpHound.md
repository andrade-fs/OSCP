# WADComs: SharpHound

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[WADComs|Índice WADComs]]

> Fuente: [https://wadcoms.github.io/](https://wadcoms.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

WADComs — comandos para Active Directory, ordenados por lo que TENES.

**Lo que tenés:** `Shell`

**Sistema:** `Windows`

## Descripción

SharpHound.exe and SharpHound.ps1 are the official data collector for BloodHound, written in C# or Powershell and uses Windows API functions and LDAP namespace functions to collect data from domain controllers and domain-joined Windows systems. This data can then be fed into BloodHound to enumerate potential paths of privilege escalation. The following command peforms all collection methods and stores the output in a zip file that can be directly placed in the BloodHound GUI.

Command Reference:

	Output File: output.zip

## Comando

```bash
SharpHound.exe --CollectionMethods All --ZipFileName output.zip
#Using PowerShell module
powershell -ep bypass 
.\SharpHound.ps1
Invoke-BloodHound -CollectionMethod All -Domain domain.tld -ZipFileName output.zip
```

## Referencias

- https://github.com/BloodHoundAD/SharpHound3
- https://bloodhound.specterops.io/collect-data/ce-collection/sharphound
- https://github.com/ZishanAdThandar/pentest/blob/main/notes/ActiveDirectory.md#bloodhound
