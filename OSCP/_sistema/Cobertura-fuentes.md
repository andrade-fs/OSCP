# Cobertura de fuentes — técnicas, tácticas y estrategias

> Auditoría hecha el **23-sep-2026** sobre los enlaces aportados, comparando contra lo que ya
> había en el vault. Sirve para saber **qué está cubierto y qué no** antes de estudiar.
>
> Leyenda: **✔** cubierto · **◐** parcial · **✘** faltaba (y qué se hizo) · **—** estrategia/no técnico

---

## Tabla resumen

| # | Fuente | Aporta | Estado | Dónde / qué se hizo |
| --- | --- | --- | --- | --- |
| 1 | [Potatoes — Jorge Lajara](https://jlajara.gitlab.io/Potatoes_Windows_Privesc) | Hot/Rotten/Lonely/Juicy/Rogue/Sweet/Generic Potato + matriz | ◐ | Se creó `../cheatsheets/potatoes.md`; enlazado desde `04` |
| 2 | [PrivEscAssist Windows](https://daniel10barredo.github.io/PrivEscAssist_Windows/) | Checklist de privesc Windows | ◐ | Se amplió `04`: privilegios y grupos que faltaban |
| 3 | [WADComs](https://wadcoms.github.io/) | 103 recetas AD | ✔ | Espejado en `vault/indices/Referencias/WADComs/` (103 notas) |
| 4 | [PATT — MSSQL Injection](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/SQL%20Injection/MSSQL%20Injection.md) | Inyección MSSQL completa | ✘ | Se creó `../cheatsheets/mssql-injection.md`; enlazado desde `02` |
| 5 | [adot8 — Code execution via Windows Library](https://oscp.adot8.com/cool/client-side-attacks/code-execution-via-windows-library) | Client-side: Library-ms, entrega por email | ✘ | Se añadió sección 6 a `06` (client-side y phishing) |
| 5b | [oscp.adot8.com — Services](https://oscp.adot8.com/services/inital-scans) | Enumeración por servicio/puerto (22 páginas) | ✘ | Volcado a `02-enumeracion-servicios.md`: nuevas secciones IDENT/WebDAV/Port Knocking/Web Sockets/Misc + trucos (wget FTP, ssh2john, SNMP MIBs, ldapdomaindump, smbclient mget, MySQL --skip-ssl, MSSQL bulk insert, etc.) y referencias por puerto |
| 5c | [oscp.adot8.com — Web Applications](https://oscp.adot8.com/web-applications/checklist) | Ataques web (24 páginas) | ✘ | Nuevo `cheatsheets/web.md`: checklist, directory traversal/LFI/RFI, PHP wrappers, file upload, command injection, **SQLi manual (MySQL/MSSQL/Postgres) → RCE**, SSRF, XSS/SSTI, APIs, Hydra, compilar exploits, payloads |
| 6 | [itresit — Shadow Snapshots](https://labs.itresit.es/2025/06/11/remote-windows-credential-dump-with-shadow-snapshots-exploitation-and-detection/) | Dump remoto de SAM vía Shadow Copy | ✘ | Se añadió a `04` §6 (`-use-remoteSSMethod`) |
| 7 | [OffSec — Exam Guide](https://help.offsec.com/hc/en-us/articles/360040165632-OSCP-Exam-Guide) | Reglas del examen | ✔ | `00-reglas-examen.md` (verbatim) |
| 8 | [The Hacker Recipes](https://www.thehacker.recipes/) | AD/web/pivoting/privesc enciclopedia | ◐ | Se crearon `../cheatsheets/rpc-coercion.md`, `adcs-esc.md`, `ad-avanzado.md`, `lfi-rce.md` |
| 9 | [s4mu51/phpinfo-checker](https://github.com/s4mu51/phpinfo-checker) | Analizador de `phpinfo()` | ✘ | Instalado en `~/examen/tools/web/phpinfo-checker.py` |
| 10 | [adot8 — Challenge 0 Secura](https://xn--ec6b17t.com/OSCP/Challenge-Labs/Challenge-0---Secura) | Writeup de lab | — | **Ahora privado** (el autor pide contacto); sin contenido |
| 11 | [brightio/penelope](https://github.com/brightio/penelope) | Shell handler con PTY, sesiones, módulos | ✘ | Añadido a `06`; instalable con `apt install penelope` |
| 12 | [OffSec — Access PG Play](https://help.offsec.com/hc/en-us/articles/360048613751-Access-PG-Play) | Info de Proving Grounds | — | Estrategia; cubierto conceptualmente en `README`/`01` |
| 13 | [N1NJ10/Offsec-Practice-Labs](https://github.com/N1NJ10/Offsec-Practice-Labs) | Arsenal de labs/recursos | — | Estrategia; no aporta técnicas nuevas |
| 14 | [omurugur OSCP Notes (PDF)](https://github.com/omurugur/OSCP/blob/main/OSCP_Notes_1619461464.pdf) | Notas generales por servicio | ✔ | Ya cubierto por `vault/indices/Puertos/` + `vault/indices/Servicios/` + playbook |
| 15 | [Hackerdna — OSCP+ Roadmap](https://hackerdna.com/blog/oscp-preparation-guide) | Guía de preparación y plan | — | Estrategia; alineado con `01-metodologia.md` |
| 16 | [HackMD @roger102](https://hackmd.io/@roger102/rkV6SE6Akx) | Notas | — | Requiere JS/sesión; no accesible |
| 17 | [Scribd — Challenge 2 Relia](https://es.scribd.com/document/949095958/OSCP-Challenge-2-Relia) | Writeup de lab | — | Paywall; no accesible |

---

## Detalle de lo añadido (los vacíos reales)

### Windows privesc (`04-privesc-windows.md` + `../cheatsheets/potatoes.md`)

- **Familia Potato completa**: Hot, Rotten, Lonely, Juicy, Rogue, Sweet, Generic y SigmaPotato,
  con **matriz de compatibilidad** por versión de Windows y **árbol de elección**.
- **Privilegios nuevos**: `SeManageVolumePrivilege`, `SeCreateTokenPrivilege`, `SeTcbPrivilege`.
- **Grupos que escalan**: Backup Operators, Server Operators, Account Operators, Print Operators,
  **DnsAdmins**, Exchange Windows Permissions, Organization Management, Hyper-V Administrators.
- **Shadow Snapshots** para dumpear SAM/SYSTEM/SECURITY en remoto sin tocar los hives.
- **CVEs**: CVE-2024-26229, CVE-2019-1388 (además de los que ya había).

### AD / Kerberos (cheatsheets nuevos)

- **`rpc-coercion.md`**: MS-EFSR/MS-RPRN/MS-DFSNM/MS-FSRVP, WebClient, PushSubscription, uso con
  `coercer`, relay ESC8, Rubeus, captura de hash.
- **`adcs-esc.md`**: mapa **completo** de ESC (incluye ESC5, ESC9, ESC10, ESC11, ESC12, ESC13,
  ESC14, ESC15) + **Certifried** (CVE-2022-26923) + reglas de backup/restore.
- **`ad-avanzado.md`**: Diamond/Sapphire tickets, **Bronze Bit** (CVE-2020-17049), **UnPAC the hash**,
  Dollar ticket / **sAMAccountName spoofing** (noPac), **Timeroasting**, **Pass-the-Certificate**,
  **SPN-jacking**, Exchange (ProxyLogon/ProxyShell), SCCM/MECM, DHCPv6.

### Web (cheatsheet nuevo)

- **`lfi-rce.md`**: LFI → RCE (log poisoning, PHP wrappers, PHP session, phpinfo, `/proc`, RFI,
  filter chains) y variantes (CRLF, HPP, null byte, content-type juggling, open redirect).

### MSSQL (`../cheatsheets/mssql-injection.md`)

- Union/error/blind/time, **stacked queries**, lectura/escritura de archivos, `xp_cmdshell`,
  Python externo, **OOB** (DNS exfiltration + UNC path → Responder), **Trusted Links**,
  impersonación, hashes de logins y OPSEC (`sp_password`).

### Entrega y shells (`06`)

- **Penelope** como handler moderno (auto-PTY, sesiones, transferencia, módulos).
- **Client-side**: `config.Library-ms`, Evil Icon, macros/HTA/ISO, `swaks`, `wsgidav`, `Responder`.

---

## Vacíos que quedan (baja prioridad OSCP)

Anotados para que decidas si los querés:

| Tema | Fuente | Por qué no está |
| --- | --- | --- |
| **WSL** (privesc desde Windows Subsystem for Linux) | thehacker.recipes | poco frecuente en OSCP |
| **Vulnerable drivers** (detalle de carga y PoCs) | thehacker.recipes / PrivEscAssist | raro; cubierto a nivel de privilegio |
| **Living off the land** (LOLBAS) | thehacker.recipes | espejo LOLBAS ya está en `vault/indices/Referencias/LOLBAS/` |
| **SCCM/MECM** (detalle) | thehacker.recipes | fuera del temario; solo resumen |
| **Exchange** (PoCs) | thehacker.recipes | fuera del temario; solo resumen |
| **AV evasion** (dropper/loader/EDR) | thehacker.recipes | fuera del temario OSCP |

---

## Cómo mantener esto

Cuando aparezca una fuente nueva:

1. Extraer las técnicas que menciona.
2. Comparar contra `vault/indices/Tecnicas/`, `../cheatsheets/` y `02`–`08` (usar la función de grep del playbook).
3. Si falta, crear/extender una nota **curada** (no `vault/indices/Tecnicas/`, que se regenera).
4. Registrarlo en esta tabla y alimentar Engram.
