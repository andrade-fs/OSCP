#!/usr/bin/env bash
# verificar-entorno.sh — valida en segundos que el entorno del examen está listo.
#
# Uso:
#   bash herramientas/verificar-entorno.sh          # desde la raíz del vault
#   bash ~/Documentos/OSCP/herramientas/verificar-entorno.sh
#
# Devuelve 0 si todo está OK, 1 si falta algo.

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TOOLS="$HOME/examen/tools"
fallos=0
ok=0

rojo()  { printf '\033[91m%s\033[0m\n' "$*"; }
verde() { printf '\033[92m%s\033[0m\n' "$*"; }
gris()  { printf '\033[90m%s\033[0m\n' "$*"; }

seccion() { printf '\n\033[1m== %s ==\033[0m\n' "$*"; }

check_cmd() {
  if command -v "$1" >/dev/null 2>&1; then ok=$((ok+1)); else rojo "  ✗ FALTA comando: $1"; fallos=$((fallos+1)); fi
}
check_file() {
  if [ -s "$2" ]; then ok=$((ok+1)); else rojo "  ✗ FALTA archivo: $2  ($1)"; fallos=$((fallos+1)); fi
}
check_py() {
  if python3 -c "import $1" >/dev/null 2>&1; then ok=$((ok+1)); else rojo "  ✗ FALTA módulo Python: $1"; fallos=$((fallos+1)); fi
}

seccion "Comandos — AD"
for c in nxc evil-winrm bloodhound-python ldapsearch rpcclient smbclient smbmap \
         enum4linux enum4linux-ng kerbrute pypykatz bloodyAD ldeep \
         dacledit.py owneredit.py addcomputer.py rbcd.py getST.py getTGT.py \
         GetUserSPNs.py GetNPUsers.py secretsdump.py ticketer.py ticketConverter.py \
         lookupsid.py findDelegation.py Get-GPPPassword.py mssqlclient.py smbclient.py \
         psexec.py wmiexec.py smbexec.py atexec.py dcomexec.py ntlmrelayx.py \
         pyLAPS.py gMSADumper.py targetedKerberoast.py; do check_cmd "$c"; done

seccion "Comandos — Kerberos / reloj"
for c in kinit klist kdestroy ktutil ntpdate rdate; do check_cmd "$c"; done

seccion "Comandos — Web"
for c in whatweb ffuf gobuster feroxbuster nikto nuclei wpscan joomscan searchsploit curl wget; do check_cmd "$c"; done

seccion "Comandos — Linux LPE / sistema"
for c in gcc make python3 openssl getcap capsh setcap debugfs screen tmux script nc ncat socat rlwrap; do check_cmd "$c"; done

seccion "Comandos — Pivoting"
for c in proxychains4 chisel ligolo-proxy ligolo-agent ssh sshpass vncviewer tcpdump; do check_cmd "$c"; done

seccion "Comandos — Cracking / payloads / misc"
for c in hashcat john msfvenom msfconsole jq uploadserver smbserver.py x86_64-w64-mingw32-gcc; do check_cmd "$c"; done

seccion "Módulos Python"
for m in impacket ldap3 pwn pypykatz uploadserver pyftpdlib requests bs4; do check_py "$m"; done

seccion "Wordlists y reglas"
check_file "rockyou"    /usr/share/wordlists/rockyou.txt
check_file "seclists"   /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
check_file "vhosts"     /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt
check_file "best64"     /usr/share/hashcat/rules/best64.rule
check_file "dirb"       /usr/share/wordlists/dirb/common.txt

seccion "Toolkit Linux"
for f in linpeas.sh pspy64 pspy32 chisel ligolo-agent linux-exploit-suggester.sh lse.sh deepce.sh traitor; do
  check_file "$f" "$TOOLS/linux/$f"
done

seccion "Toolkit Windows"
for f in winPEASx64.exe winPEASx86.exe winPEAS.bat PowerUp.ps1 PowerView.ps1 \
         Seatbelt.exe SharpUp.exe Watson.exe accesschk64.exe accesschk.exe Snaffler.exe \
         mimikatz/x64/mimikatz.exe mimikatz/Win32/mimikatz.exe SafetyKatz.exe SharpDump.exe \
         SharpDPAPI.exe SharpChrome.exe procdump64.exe procdump.exe LaZagne.exe Koh.exe \
         GodPotato.exe SigmaPotato.exe PrintSpoofer64.exe PrintSpoofer32.exe JuicyPotato.exe \
         JuicyPotatoNG.exe RoguePotato.exe RogueWinRM.exe RemotePotato0.exe \
         potato_check64.exe potato_check32.exe FullPowers.exe SeManageVolumeExploit.exe \
         Rubeus.exe Certify.exe SharpWMI.exe SharpHound.exe SharpHound.ps1 SharpLAPS.exe \
         LockLess.exe RestrictedAdmin.exe chisel.exe ligolo-agent.exe nc.exe nc64.exe \
         powercat.ps1 Invoke-Mimikatz.ps1 DecryptAutoLogon.exe Procmon.exe; do
  check_file "$(basename "$f")" "$TOOLS/win/$f"
done

seccion "Vault"
for f in README.md guia/00-inicio.md guia/05-active-directory.md guia/lpe/LPE-Windows.md \
         guia/lpe/LPE-Linux.md guia/walkthroughs/AD-walkthrough.md guia/walkthroughs/Standalone-walkthrough.md \
         vault/indices/Puertos.md vault/indices/Tecnicas.md guia/verificado-2026.md .obsidian/app.json; do
  check_file "$f" "$ROOT/$f"
done

printf '\n============================================\n'
if [ "$fallos" -eq 0 ]; then
  verde "TODO OK — $ok comprobaciones correctas, 0 fallos."
  exit 0
else
  rojo "FALLOS: $fallos (OK: $ok)"
  exit 1
fi
