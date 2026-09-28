# WADComs: SafetyKatz

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[WADComs|Índice WADComs]]

> Fuente: [https://wadcoms.github.io/](https://wadcoms.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

WADComs — comandos para Active Directory, ordenados por lo que TENES.

**Lo que tenés:** `Shell`

**Sistema:** `Windows`

## Descripción

SafetyKatz.exe is part of the GhostPack suite of tools and is a combination of SharpDump and Mimikatz. The following command will dump the LSASS process and run Mimikatz to extract credentials from the dumped process. Safetykatz also supports a number of mimikatz native commands such as "sekurlsa::evasive-keys" etc. The evasive switch in lab and production enviroments up to windows 2016 has been noted to successfully run where the non "evasive" switches had not

## Comando

```bash
safetykatz.exe "privilege::debug" "sekurlsa::evasive-logonpasswords" "exit"
```

## Referencias

- https://github.com/GhostPack/SafetyKatz
- https://www.harmj0y.net/blog/redteaming/ghostpack/
