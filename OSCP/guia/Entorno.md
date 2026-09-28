# Entorno — preparación antes de atacar

Todo lo de esta nota se hace **una vez** al empezar a trabajar contra un dominio.
Sin esto, los ataques de Kerberos fallan con errores que no te dicen nada.

---

## Convención de placeholders

En todo el recetario de comandos:

| Placeholder | Significa | Ejemplo |
| --- | --- | --- |
| `<DC_IP>` | IP del Domain Controller | `10.10.10.5` |
| `<DOMINIO>` | Dominio en **minúsculas** | `gesuga.local` |
| `<REALM>` | Dominio en **MAYÚSCULAS** | `GESUGA.LOCAL` |
| `<USER>` / `<PASS>` | Credenciales válidas | `juan` / `P@ssw0rd` |
| `<TU_IP>` | Tu IP de Kali en la VPN | `10.10.14.15` |
| `<IP>` | Cualquier objetivo | `10.10.10.10` |
| `<NTHASH>` | Hash NTLM (32 hex) | `aad3b435b51404ee...` |

---

## 1. `/etc/hosts` — el paso que más veces se olvida

**Kerberos necesita NOMBRES, no IPs.** Muchos ataques fallan simplemente porque
el nombre del dominio no resuelve.

```bash
echo '<DC_IP>  <dominio> <hostname>.<dominio> <HOSTNAME>' | sudo tee -a /etc/hosts

# Verificar
getent hosts <dominio>
getent hosts <hostname>.<dominio>
```

Formato práctico, con los tres alias que suelen hacer falta:

```bash
echo '10.10.10.5  gesuga.local dc01.gesuga.local dc01 GESUGA' | sudo tee -a /etc/hosts
```

> Si el dominio tiene varios hosts (un set de AD con 3 máquinas), agregá **todos**.
> Vas a necesitar resolver cada nombre cuando hagas Pass-the-Ticket.

---

## 2. DNS

`/etc/resolv.conf` apunta por defecto a la red de tu laboratorio, no al DC.

```bash
# Opción A — apuntar al DC (funciona, pero rompe tu resolución normal)
echo 'nameserver <DC_IP>' | sudo tee /etc/resolv.conf

# Opción B — RECOMENDADA: dejar el DNS como está y usar /etc/hosts
#   Es más estable y sobrevive a reconexiones de la VPN.
```

La opción B es la que conviene: con `/etc/hosts` no dependés de que el DNS del
objetivo esté configurado, y no rompés tu propia resolución.

Y si una herramienta igual necesita DNS, casi todas aceptan que se lo pases:

```bash
/usr/bin/nxc ldap <DC_IP> -u '<USER>' -p '<PASS>' -d <DOMINIO> --dns-server <DC_IP>
certipy-ad find -u '<USER>@<DOMINIO>' -p '<PASS>' -dc-ip <DC_IP> -ns <DC_IP> -vulnerable -stdout
```

---

## 3. `krb5.conf` — la configuración de Kerberos

### Estado actual de tu máquina

Ya tenés un `/etc/krb5.conf` configurado **para `GESUGA.LOCAL`** (de una práctica
anterior). La **estructura es correcta** — incluido `udp_preference_limit = 0`,
que fuerza TCP y te sirve muchísimo cuando atacás a través de un túnel. Solo hay
que cambiar el dominio.

### Plantilla completa — reemplazá `<REALM>`, `<dominio>` y `<dc>`

```ini
[libdefaults]
    default_realm = <REALM>
    dns_lookup_realm = false
    dns_lookup_kdc = false
    rdns = false
    dns_canonicalize_hostname = false
    ticket_lifetime = 24h
    forwardable = true
    udp_preference_limit = 0

[realms]
    <REALM> = {
        kdc = <dc>.<dominio>
        admin_server = <dc>.<dominio>
        default_domain = <dominio>
    }

[domain_realm]
    .<dominio> = <REALM>
    <dominio> = <REALM>
```

### Por qué cada opción importa

| Opción | Por qué |
| --- | --- |
| `dns_lookup_kdc = false` | Evita que Kerberos busque el KDC por DNS. Con `/etc/hosts` alcanza y es más predecible. |
| `dns_lookup_realm = false` | Ídem para el realm. |
| `udp_preference_limit = 0` | **Fuerza TCP.** Indispensable cuando atacás a través de un túnel: UDP no pasa por SOCKS. |
| `rdns = false` | Evita resolución inversa, que en una VPN suele fallar y mete ruido. |
| `dns_canonicalize_hostname = false` | No normaliza el nombre del host contra DNS. |
| `forwardable = true` | Permite delegar el tique (necesario para S4U). |

### Aplicar la plantilla rápida

```bash
# Backup primero
sudo cp /etc/krb5.conf /etc/krb5.conf.bak

sudo tee /etc/krb5.conf > /dev/null <<'KINICIO'
[libdefaults]
    default_realm = DOMINIO.LOCAL
    dns_lookup_realm = false
    dns_lookup_kdc = false
    rdns = false
    dns_canonicalize_hostname = false
    ticket_lifetime = 24h
    forwardable = true
    udp_preference_limit = 0

[realms]
    DOMINIO.LOCAL = {
        kdc = dc01.dominio.local
        admin_server = dc01.dominio.local
        default_domain = dominio.local
    }

[domain_realm]
    .dominio.local = DOMINIO.LOCAL
    dominio.local = DOMINIO.LOCAL
KINICIO
```

**Después reemplazá `DOMINIO.LOCAL` y `dominio.local` por los reales.** Editá con
`sudo nano /etc/krb5.conf`.

### Verificar que funciona

```bash
# Pedir un tique con credenciales
kinit <USER>@<REALM>
klist

# Y limpiar
kdestroy
```

Si `kinit` te devuelve un tique y `klist` lo muestra, Kerberos está bien
configurado y podés usar `-k` en todas las herramientas de Impacket.

---

## 4. Reloj — la causa #1 de errores confusos

Kerberos **rechaza tiques con más de 5 minutos de desfase**. Es la causa de
`KRB_AP_ERR_SKEW`, un error que no explica nada.

```bash
# Ver la hora de tu Kali y del DC
date
rdate -n <DC_IP>

# Sincronizar
sudo ntpdate <DC_IP>

# Verificar
date && rdate -n <DC_IP>
```

`ntpdate` y `rdate` están instalados. `chronyc` no.

> Si `ntpdate` falla porque el puerto 123/UDP está bloqueado, ajustá la hora a
> mano con `sudo date -s "YYYY-MM-DD HH:MM:SS"` usando la del DC.

---

## 5. `proxychains4.conf` — sin proxy configurado

Tu `/etc/proxychains4.conf` tiene la sección `[ProxyList]` **vacía**. Hay que
agregarle el proxy, y está en `strict_chain` (bien: evita fugas).

```bash
# Agregar el SOCKS al final del archivo
echo 'socks5 127.0.0.1 1080' | sudo tee -a /etc/proxychains4.conf

# Verificar
tail -3 /etc/proxychains4.conf
```

### Uso correcto

```bash
# SIEMPRE -sT -Pn: proxychains solo enruta TCP y el ping no pasa
proxychains4 nmap -sT -Pn -p 445,3389,5985 <IP_INTERNA>

proxychains4 /usr/bin/nxc smb <IP_INTERNA> -u '<USER>' -p '<PASS>'
proxychains4 evil-winrm -i <IP_INTERNA> -u '<USER>' -p '<PASS>'
```

Ver [[07-pivoting]] para montar el túnel (chisel o ligolo-ng).

---

## 6. Directorios de trabajo

Armalos **antes** de empezar. Perder tiempo buscando dónde guardaste algo no es
opcional en un examen cronometrado.

```bash
mkdir -p ~/OSCP/examen/{nmap,evidencia,tools/linux,tools/win,loot}
cd ~/OSCP/examen

# Un directorio por objetivo
for t in stand1 stand2 stand3 dc01 dc02 dc03; do
  mkdir -p evidencia/$t
done
```

Guardá ahí las herramientas de escalada **antes** del examen:

```text
tools/linux/   linpeas.sh  pspy64  linux-exploit-suggester.sh
tools/win/     winPEASx64.exe  PowerUp.ps1  GodPotato.exe  PrintSpoofer64.exe
               accesschk.exe  procdump.exe
```

---

## 7. Verificación final del entorno

Corré esto antes de empezar a atacar. Si algo falla, arreglalo ahora, no cuando
estés trabado.

```bash
echo "--- nombre del dominio ---"; getent hosts <dominio>
echo "--- kerberos ---"; klist 2>&1 | head -3
echo "--- reloj ---"; rdate -n <DC_IP>
echo "--- herramientas ---"
for t in /usr/bin/nxc certipy-ad evil-winrm GetUserSPNs.py secretsdump.py; do
  command -v $t >/dev/null && echo "  OK $t" || echo "  FALTA $t"
done
echo "--- proxychains ---"; grep -A2 '^\[ProxyList\]' /etc/proxychains4.conf | tail -1
```

### Errores y su causa real

| Error | Causa | Arreglo |
| --- | --- | --- |
| `KRB_AP_ERR_SKEW` | Reloj desfasado | `sudo ntpdate <DC_IP>` |
| `Cannot contact any KDC` | El nombre no resuelve | `/etc/hosts` |
| `KDC_ERR_C_PRINCIPAL_UNKNOWN` | Usuario o realm mal | Revisá `<REALM>` en mayúsculas |
| `Server not found in Kerberos database` | El SPN no existe o el DNS falla | `/etc/hosts` con el host exacto |
| `Connection refused` con `-k` | `KRB5CCNAME` mal o el tique caducó | `export KRB5CCNAME=...` y `klist` |
| Todo funciona pero `nxc` falla | Instalación vieja | En este Kali `nxc` ya funciona: `nxc --version` → 1.5.1 — ver [[verificado-2026]] |
| Kerberos falla solo a través del túnel | UDP no pasa por SOCKS | `udp_preference_limit = 0` en `krb5.conf` |

---

## Referencias

| Recurso | Para qué |
| --- | --- |
| [[WADComs]] | Comandos de AD por lo que tenés en la mano |
| [The Hacker Recipes](https://www.thehacker.recipes/) | La referencia de AD mejor ordenada. Kerberos, delegación, ADCS. |
| [ADSecurity.org](https://adsecurity.org/) | Sean Metcalf. Lo más profundo en Kerberos |
| [CyberChef](https://gchq.github.io/CyberChef/) | Decodificar base64, hex, JWT — útil con blobs de LDAP |

> **Todo esto es documentación; leerla está permitido en el examen.** Lo que está
> prohibido es un chatbot. Si el sitio tiene una caja de chat, no la uses —
> ver el aviso completo en [[Referencias]].
