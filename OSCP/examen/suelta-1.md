# 🖥️ Suelta 1 — `<IP>`

> **Estado**: ⬜ sin empezar · 🟡 en curso · ✅ comprometida
> **Puntos**: acceso ☐ (10) · escalada ☐ (10) → **☐ 20**

[[00-dashboard|Panel]] · [[01-metodologia|Metodología]] · [[LPE-Linux]] · [[LPE-Windows]] · [[08-reporte-y-evidencia|Reporte]]

---

## 0. Datos rápidos

| Dato | Valor |
| --- | --- |
| IP | |
| SO | Linux / Windows |
| Hostname | |
| Puertos clave | |
| Vector de entrada | |
| Vector de escalada | |
| Tiempo invertido | |

## 🔑 Credenciales / hashes de ESTA máquina

| Usuario | Contraseña | Hash | Servicio | Notas |
| --- | --- | --- | --- | --- |
| | | | | |

---

## 1. Recon

```bash
export IP=''
export TU_IP=$(ip -4 addr show tun0 | awk '/inet /{print $2}' | cut -d/ -f1)
mkdir -p ~/examen/evidencia/$IP ~/examen/nmap
```

```bash
sudo nmap -p- --min-rate 5000 -T4 -oA ~/examen/nmap/$IP-alltcp $IP
```
```text
▶ OUTPUT
```

```bash
ports=$(grep -oP '^\d+' ~/examen/nmap/$IP-alltcp.nmap | sort -u | paste -sd,)
sudo nmap -sCV -p$ports -oA ~/examen/nmap/$IP-services $IP
```
```text
▶ OUTPUT
```

```bash
sudo nmap -sU --top-ports 50 -oA ~/examen/nmap/$IP-udp $IP
```
```text
▶ OUTPUT
```

**Si hay web (80/443):**
```bash
whatweb -a 3 http://$IP
curl -sI http://$IP
ffuf -u http://$IP/FUZZ -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt -mc 200,204,301,302,307,401,403 -t 50
ffuf -u http://$IP/ -H "Host: FUZZ.<dominio>" -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt -mc 200,301,302,401,403 -fs <default>
```
```text
▶ OUTPUT
```
📸 Captura: `______`

> Detalle por puerto: [[02-enumeracion-servicios]] · Ataques web: [[09-web]]

---

## 2. Enumeración por servicio

| Puerto | Servicio | Qué probé | Resultado |
| --- | --- | --- | --- |
| | | | |

```bash
# ▶ comando por servicio (FTP/SMB/LDAP/NFS/MySQL/MSSQL/Redis...)
```
```text
▶ OUTPUT
```
📸 Captura: `______`

**Notas / hallazgos:**

---

## 3. Foothold

- [ ] Credenciales reutilizadas / por defecto
- [ ] Vulnerabilidad de servicio (`searchsploit`)
- [ ] Web (LFI / upload / cmd-injection / SQLi / SSTI)

```bash
# ▶ comando de explotación
```
```text
▶ OUTPUT
```

**Shell conseguida:**
```bash
# Linux: python3 -c 'import pty; pty.spawn("/bin/bash")'  + stty raw -echo; fg
# Windows: evil-winrm / nxc
```
📸 Captura del acceso: `______`

---

## 4. `local.txt`

```bash
cat local.txt; ip addr
```
```text
▶ OUTPUT
```
```cmd
type C:\Users\<user>\Desktop\local.txt & ipconfig
```
📸 **Captura (contenido + IP):** `______` ✅

---

## 5. Enumeración local + LPE

### Si es Linux → [[LPE-Linux]]
```bash
id; sudo -l; uname -a; getcap -r / 2>/dev/null
```
```text
▶ OUTPUT
```
- [ ] `sudo -l` → GTFOBins
- [ ] SUID/SGID (`find / -perm -4000 -type f 2>/dev/null`) → GTFOBins
- [ ] Capabilities (`getcap -r /`)
- [ ] Credenciales en archivos / historiales
- [ ] Procesos root escribibles / cron (`pspy64 -pf -i 1000`)
- [ ] Servicios/systemd · grupos (docker/lxd/disk) · NFS · wildcard
- [ ] Kernel (último)

### Si es Windows → [[LPE-Windows]]
```cmd
whoami /all & whoami /priv
```
```text
▶ OUTPUT
```
- [ ] `SeImpersonate` → `potato_check64.exe` + `GodPotato.exe -cmd "cmd /c whoami"`
- [ ] Servicios (rutas sin comillas, binarios escribibles)
- [ ] Tareas programadas / autoruns
- [ ] Credenciales guardadas (`cmdkey /list`, unattend, GPP, web.config)
- [ ] `AlwaysInstallElevated` · `SeBackup/SeDebug` · UAC · kernel

```bash
# ▶ comando de escalada
```
```text
▶ OUTPUT
```
📸 Captura de root/SYSTEM: `______`

---

## 6. `proof.txt`

```bash
cat /root/proof.txt; ip addr
```
```text
▶ OUTPUT
```
```cmd
type C:\Users\Administrator\Desktop\proof.txt & ipconfig
```
📸 **Captura (contenido + IP):** `______` ✅

---

## 7. Loot y notas

**Credenciales/hashes nuevos** (copiar también a [[00-dashboard]]):
```
```

**Próximos pasos / pendientes:**
```

```
