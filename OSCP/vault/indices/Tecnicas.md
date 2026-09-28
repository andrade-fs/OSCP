# Técnicas

[[00-inicio|Inicio]] · [[Entorno|Entorno]] · [[Puertos|Puertos]] · [[Servicios|Servicios]] · [[Tecnicas|Tecnicas]] · [[Maquinas|Maquinas]] · [[Referencias|Referencias]]

Ordenado por cuántas máquinas del **listado OSCP** la usan.

Índice inverso: técnica → máquinas donde aparece.

La columna **Receta** marca las que tienen comandos copy-paste listos
(en la propia nota, sección *Comandos*).

| Técnica | Máquinas | de ellas OSCP | Receta |
|---|---|---|---|
| [[metasploit\|metasploit]] | 79 | — | — |
| [[nmap\|nmap]] | 534 | **68** | — |
| [[sudo\|sudo]] | 377 | **48** | **sí** |
| [[buffer-overflow\|buffer overflow]] | 41 | — | — |
| [[netexec\|netexec]] | 142 | **40** | — |
| [[smb\|smb]] | 160 | **39** | — |
| [[ldap\|ldap]] | 141 | **38** | — |
| [[ssh\|ssh]] | 413 | **38** | — |
| [[ssti\|ssti]] | 34 | — | — |
| [[kerberos\|kerberos]] | 128 | **33** | — |
| [[wordpress\|wordpress]] | 33 | — | — |
| [[reverse-shell\|reverse shell]] | 348 | **33** | — |
| [[hashcat\|hashcat]] | 192 | **33** | — |
| [[evil-winrm\|evil-winrm]] | 122 | **31** | — |
| [[cve-\|cve-]] | 215 | **26** | — |
| [[impacket\|impacket]] | 97 | **23** | — |
| [[socat\|socat]] | 22 | — | — |
| [[docker\|docker]] | 151 | **22** | — |
| [[apache\|apache]] | 255 | **20** | — |
| [[bloodhound\|bloodhound]] | 62 | **19** | — |
| [[mysql\|mysql]] | 182 | **18** | — |
| [[iis\|iis]] | 93 | **18** | — |
| [[xxe\|xxe]] | 18 | — | — |
| [[idor\|idor]] | 17 | — | — |
| [[ffuf\|ffuf]] | 131 | **14** | — |
| [[kerberoasting\|kerberoasting]] | 33 | **13** | **sí** |
| [[sqli\|sqli]] | 186 | **13** | — |
| [[rdp\|rdp]] | 54 | **12** | — |
| [[mssql\|mssql]] | 47 | **12** | — |
| [[sgid\|sgid]] | 11 | — | — |
| [[ftp\|ftp]] | 110 | **11** | — |
| [[kubernetes\|kubernetes]] | 11 | — | — |
| [[genericall\|genericall]] | 24 | **10** | — |
| [[systemd\|systemd]] | 114 | **10** | — |
| [[docker-group\|docker group]] | 10 | — | **sí** |
| [[tunnel\|tunnel]] | 136 | **10** | — |
| [[nginx\|nginx]] | 152 | **10** | — |
| [[log4shell\|log4shell]] | 10 | — | — |
| [[responder\|responder]] | 41 | **9** | — |
| [[adcs\|adcs]] | 32 | **9** | **sí** |
| [[capabilities\|capabilities]] | 67 | **9** | **sí** |
| [[joomla\|joomla]] | 9 | — | — |
| [[smbmap\|smbmap]] | 38 | **9** | — |
| [[machineaccountquota\|machineaccountquota]] | 21 | **8** | — |
| [[sedebugprivilege\|sedebugprivilege]] | 8 | — | — |
| [[potato\|potato]] | 32 | **8** | — |
| [[scheduled-task\|scheduled task]] | 42 | **8** | — |
| [[cron\|cron]] | 169 | **8** | **sí** |
| [[smtp\|smtp]] | 78 | **8** | — |
| [[file-upload\|file upload]] | 68 | **8** | — |
| [[seimpersonate\|seimpersonate]] | 38 | **7** | **sí** |
| [[chisel\|chisel]] | 59 | **7** | — |
| [[x11-forwarding\|x11 forwarding]] | 7 | — | — |
| [[xss\|xss]] | 104 | **7** | — |
| [[asreproast\|asreproast]] | 11 | **6** | **sí** |
| [[dcsync\|dcsync]] | 22 | **6** | **sí** |
| [[certipy\|certipy]] | 26 | **6** | — |
| [[certificate-template\|certificate template]] | 27 | **6** | — |
| [[setakeownershipprivilege\|setakeownershipprivilege]] | 6 | — | — |
| [[psexec\|psexec]] | 24 | **6** | — |
| [[snmp\|snmp]] | 33 | **6** | — |
| [[gobuster\|gobuster]] | 128 | **6** | — |
| [[delegacion-sin-restriccion\|delegacion sin restriccion]] | 5 | — | **sí** |
| [[writeowner\|writeowner]] | 15 | **5** | — |
| [[seassignprimarytoken\|seassignprimarytoken]] | 20 | **5** | — |
| [[printspoofer\|printspoofer]] | 5 | — | — |
| [[applocker-bypass\|applocker bypass]] | 5 | — | — |
| [[suid\|suid]] | 84 | **5** | **sí** |
| [[wmiexec\|wmiexec]] | 19 | **5** | — |
| [[proxychains\|proxychains]] | 35 | **5** | — |
| [[jenkins\|jenkins]] | 12 | **5** | — |
| [[elasticsearch\|elasticsearch]] | 5 | — | — |
| [[command-injection\|command injection]] | 112 | **5** | — |
| [[struts\|struts]] | 5 | — | — |
| [[silver-ticket\|silver ticket]] | 9 | **4** | — |
| [[genericwrite\|genericwrite]] | 16 | **4** | — |
| [[forcechangepassword\|forcechangepassword]] | 15 | **4** | — |
| [[gmsa\|gmsa]] | 17 | **4** | — |
| [[esc1\|esc1]] | 17 | **4** | — |
| [[esc8\|esc8]] | 4 | — | — |
| [[sebackupprivilege\|sebackupprivilege]] | 15 | **4** | — |
| [[serestoreprivilege\|serestoreprivilege]] | 13 | **4** | — |
| [[uac-bypass\|uac bypass]] | 4 | — | — |
| [[mimikatz\|mimikatz]] | 14 | **4** | — |
| [[rubeus\|rubeus]] | 18 | **4** | — |
| [[ld_preload\|ld_preload]] | 4 | — | — |
| [[ssrf\|ssrf]] | 42 | **4** | — |
| [[shellshock\|shellshock]] | 4 | — | — |
| [[delegacion-restringida\|delegacion restringida]] | 14 | **3** | **sí** |
| [[rbcd\|rbcd]] | 15 | **3** | **sí** |
| [[shadow-credentials\|shadow credentials]] | 12 | **3** | **sí** |
| [[lsass\|lsass]] | 15 | **3** | **sí** |
| [[sevendll\|sevendll]] | 3 | — | — |
| [[gtfobins\|gtfobins]] | 34 | **3** | — |
| [[pivoting\|pivoting]] | 21 | **3** | — |
| [[imap\|imap]] | 32 | **3** | — |
| [[rsync\|rsync]] | 15 | **3** | — |
| [[samba\|samba]] | 32 | **3** | — |
| [[lfi\|lfi]] | 55 | **3** | — |
| [[rfi\|rfi]] | 14 | **3** | — |
| [[deserialization\|deserialization]] | 53 | **3** | — |
| [[john-the-ripper\|john the ripper]] | 3 | — | — |
| [[password-spraying\|password spraying]] | 7 | **2** | **sí** |
| [[pass-the-hash\|pass the hash]] | 11 | **2** | **sí** |
| [[golden-ticket\|golden ticket]] | 5 | **2** | — |
| [[writedacl\|writedacl]] | 8 | **2** | — |
| [[addmember\|addmember]] | 6 | **2** | — |
| [[dnstool\|dnstool]] | 9 | **2** | — |
| [[laps\|laps]] | 9 | **2** | — |
| [[esc2\|esc2]] | 4 | **2** | — |
| [[esc3\|esc3]] | 6 | **2** | — |
| [[esc6\|esc6]] | 2 | — | — |
| [[alwaysinstallelevated\|alwaysinstallelevated]] | 2 | — | **sí** |
| [[autorun\|autorun]] | 9 | **2** | — |
| [[sam-dump\|sam dump]] | 14 | **2** | — |
| [[procdump\|procdump]] | 3 | **2** | — |
| [[path-hijack\|path hijack]] | 9 | **2** | — |
| [[kernel-exploit\|kernel exploit]] | 16 | **2** | — |
| [[dirty-pipe\|dirty pipe]] | 2 | — | — |
| [[pwnkit\|pwnkit]] | 23 | **2** | — |
| [[dcomexec\|dcomexec]] | 2 | — | — |
| [[nfs\|nfs]] | 30 | **2** | — |
| [[postgresql\|postgresql]] | 29 | **2** | — |
| [[redis\|redis]] | 40 | **2** | — |
| [[tomcat\|tomcat]] | 28 | **2** | — |
| [[vnc\|vnc]] | 13 | **2** | — |
| [[jira\|jira]] | 2 | — | — |
| [[webdav\|webdav]] | 12 | **2** | — |
| [[csrf\|csrf]] | 47 | **2** | — |
| [[searchsploit\|searchsploit]] | 50 | **2** | — |
| [[winpeas\|winpeas]] | 16 | **2** | — |
| [[pass-the-ticket\|pass the ticket]] | 3 | **1** | **sí** |
| [[ntlm-relay\|ntlm relay]] | 16 | **1** | — |
| [[responder-poisoning\|responder poisoning]] | 10 | **1** | — |
| [[esc4\|esc4]] | 5 | **1** | — |
| [[esc7\|esc7]] | 3 | **1** | — |
| [[golden-certificate\|golden certificate]] | 1 | — | — |
| [[seloaddriverprivilege\|seloaddriverprivilege]] | 8 | **1** | — |
| [[unquoted-service-path\|unquoted service path]] | 1 | — | **sí** |
| [[dll-hijack\|dll hijack]] | 2 | **1** | — |
| [[token-impersonation\|token impersonation]] | 1 | — | — |
| [[amsi-bypass\|amsi bypass]] | 1 | — | — |
| [[wmic\|wmic]] | 7 | **1** | — |
| [[nfs-no_root_squash\|nfs no_root_squash]] | 1 | — | **sí** |
| [[lxd\|lxd]] | 40 | **1** | — |
| [[wildcard-injection\|wildcard injection]] | 3 | **1** | — |
| [[linpeas\|linpeas]] | 25 | **1** | — |
| [[pspy\|pspy]] | 60 | **1** | — |
| [[ssh-tunnel\|ssh tunnel]] | 36 | **1** | — |
| [[pop3\|pop3]] | 20 | **1** | — |
| [[mongodb\|mongodb]] | 12 | **1** | — |
| [[cups\|cups]] | 10 | **1** | — |
| [[gitlab\|gitlab]] | 30 | **1** | — |
| [[confluence\|confluence]] | 1 | — | — |
| [[grafana\|grafana]] | 10 | **1** | — |
| [[drupal\|drupal]] | 8 | **1** | — |
| [[phpmyadmin\|phpmyadmin]] | 15 | **1** | — |
| [[jwt\|jwt]] | 51 | **1** | — |
| [[gpp\|gpp]] | 3 | **1** | **sí** |
| [[bind-shell\|bind shell]] | 1 | — | — |
| [[public-exploit\|public exploit]] | 27 | **1** | — |
| [[hydra\|hydra]] | 28 | **1** | — |
| [[msfvenom\|msfvenom]] | 59 | **1** | — |
| [[enum4linux\|enum4linux]] | 3 | **1** | — |
| [[credenciales-en-archivos\|credenciales en archivos]] | 0 | — | **sí** |
