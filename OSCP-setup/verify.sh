#!/usr/bin/env bash
# verify.sh — comprueba que el arsenal esté listo. exit 0 = todo OK.
SETUP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
source "${SETUP_DIR}/lib.sh"

fallos=0; oks=0; avisos=0
rojo()  { printf '\033[91m%s\033[0m\n' "$*"; }
verde() { printf '\033[92m%s\033[0m\n' "$*"; }
amar()  { printf '\033[93m%s\033[0m\n' "$*"; }
seccion(){ printf '\n\033[1m== %s ==\033[0m\n' "$*"; }
ck()   { if command -v "$1" >/dev/null 2>&1; then oks=$((oks+1)); else rojo "  ✗ FALTA cmd: $1"; fallos=$((fallos+1)); fi; }
cf()   { if [ -s "$2" ]; then oks=$((oks+1)); else rojo "  ✗ FALTA archivo: $2"; fallos=$((fallos+1)); fi; }
cmpy() { if python3 -c "import $1" >/dev/null 2>&1; then oks=$((oks+1)); else rojo "  ✗ FALTA módulo py: $1"; fallos=$((fallos+1)); fi; }
avisar(){ amar "  ~ no disponible (conocido): $1"; avisos=$((avisos+1)); }

seccion "Comandos — AD / Kerberos"
for c in nxc evil-winrm bloodhound-python ldapsearch rpcclient smbclient smbmap \
         enum4linux enum4linux-ng kerbrute pypykatz bloodyAD ldeep \
         dacledit.py owneredit.py addcomputer.py rbcd.py getST.py getTGT.py \
         GetUserSPNs.py GetNPUsers.py secretsdump.py ticketer.py ticketConverter.py \
         lookupsid.py findDelegation.py Get-GPPPassword.py mssqlclient.py smbclient.py \
         psexec.py wmiexec.py smbexec.py atexec.py dcomexec.py ntlmrelayx.py \
         pyLAPS.py gMSADumper.py targetedKerberoast.py ldapsearch-ad.py PetitPotam.py \
         kinit klist kdestroy ktutil ntpdate rdate; do ck "$c"; done

seccion "Comandos — Web / recon"
for c in whatweb ffuf gobuster feroxbuster nikto nuclei wpscan joomscan searchsploit \
         subfinder httpx naabu katana dnsx; do ck "$c"; done

seccion "Comandos — Cracking / payloads / red"
for c in hashcat john hydra msfvenom msfconsole jq nmap masscan socat nc ncat rlwrap \
         ssh sshpass proxychains4 chisel ligolo-proxy tcpdump responder; do ck "$c"; done

seccion "Comandos — Sistema / LPE"
for c in gcc make python3 openssl getcap capsh setcap debugfs screen tmux script; do ck "$c"; done

seccion "Módulos Python"
for m in impacket ldap3 pwn pypykatz uploadserver pyftpdlib requests bs4; do cmpy "$m"; done

seccion "Wordlists y reglas"
cf "rockyou"  /usr/share/wordlists/rockyou.txt
cf "seclists" /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
cf "vhosts"   /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt
cf "best64"   /usr/share/hashcat/rules/best64.rule
cf "dirb"     /usr/share/wordlists/dirb/common.txt

seccion "Toolkit Linux (víctimas, amd64)"
for f in linpeas.sh pspy64 pspy32 chisel ligolo-agent linux-exploit-suggester.sh lse.sh LinEnum.sh deepce.sh traitor unix-privesc-check.sh; do
  cf "$f" "${LINUX_DIR}/$f"
done

seccion "Toolkit Windows (víctimas, x86_64)"
for f in winPEASx64.exe winPEASx86.exe winPEAS.bat PowerUp.ps1 PowerView.ps1 \
         Seatbelt.exe SharpUp.exe Watson.exe accesschk64.exe accesschk.exe Snaffler.exe \
         mimikatz/x64/mimikatz.exe mimikatz/Win32/mimikatz.exe SafetyKatz.exe SharpDump.exe \
         SharpDPAPI.exe SharpChrome.exe procdump64.exe procdump.exe LaZagne.exe \
         GodPotato.exe SigmaPotato.exe PrintSpoofer64.exe PrintSpoofer32.exe JuicyPotato.exe \
         JuicyPotatoNG.exe RoguePotato.exe RogueWinRM.exe RemotePotato0.exe \
         FullPowers.exe SeManageVolumeExploit.exe \
         Rubeus.exe Certify.exe SharpWMI.exe SharpHound.exe SharpHound.ps1 SharpLAPS.exe \
         LockLess.exe chisel.exe ligolo-agent.exe nc.exe nc64.exe \
         powercat.ps1 Invoke-Mimikatz.ps1 Procmon.exe; do
  cf "$f" "${WIN_DIR}/$f"
done
for f in DecryptAutoLogon.exe Koh.exe potato_check64.exe potato_check32.exe RestrictedAdmin.exe; do
  [ -s "${WIN_DIR}/$f" ] || avisar "$f"
done

seccion "Arsenal completo (perfil full) — aviso si falta"
for c in hashcat hcxpcapngtool hcxdumptool hydra medusa patator crunch cewl cupp \
         masscan netdiscover arp-scan bettercap mitmproxy sshuttle testssl \
         ghidra radare2 gdb gdb-multiarch binwalk exiftool foremost \
         aircrack-ng wireshark tcpdump; do
  if command -v "$c" >/dev/null 2>&1; then oks=$((oks+1)); else avisar "comando: $c"; fi
done

seccion "Config"
if grep -qE '^\s*socks5\s+127\.0\.0\.1\s+1080' /etc/proxychains4.conf 2>/dev/null; then oks=$((oks+1)); else rojo "  ✗ proxychains sin socks5 127.0.0.1 1080"; fallos=$((fallos+1)); fi
[ -s "${HOME}/.local/bin/secretsdump.py" ] && oks=$((oks+1)) || { rojo "  ✗ impacket links"; fallos=$((fallos+1)); }
[ -d "${VAULT}" ] && oks=$((oks+1)) || { rojo "  ✗ vault en ${VAULT}"; fallos=$((fallos+1)); }

printf '\n============================================\n'
if [ "$fallos" -eq 0 ]; then
  verde "TODO OK — $oks OK, $avisos avisos (no disponibles), 0 fallos."
  exit 0
else
  rojo "FALLOS: $fallos  (OK: $oks, avisos: $avisos)"
  exit 1
fi