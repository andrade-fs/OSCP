# Playbook — SMB (445/139)

Camino de decisión para cuando **SMB responde** y todavía no sabés si hay sesión anónima, shares
accesibles o credenciales reutilizables. Ordena el trabajo por **nivel de acceso** (anónimo →
autenticado → permisos de share → archivos → escalada) y fija cuándo conviene parquear. El detalle
de comandos vive en las guías y cheatsheets canónicas.

- Formato de la tarjeta: [`../plantillas/como-usar-plantillas.md`](../plantillas/como-usar-plantillas.md).
- Enumeración del puerto: [`../guia/02-enumeracion-servicios.md`](../guia/02-enumeracion-servicios.md#445--smb).
- Chuleta de la herramienta: [`../cheatsheets/nxc.md`](../cheatsheets/nxc.md).

---

## Entrada

Abrí esta tarjeta con **una** observación concreta:

- El puerto **445** (o 139) está abierto y SMB responde al banner.
- Tenés usuario y contraseña —o un hash— y querés ver qué shares y qué hosts alcanzás.
- Todavía **no** sabés si hay null session, guest, shares con lectura, shares con escritura o
  archivos con credenciales.

Si ya validaste una credencial y estás decidiendo el **movimiento**, no es esta tarjeta: pasá por
[`credenciales-y-movimiento.md`](credenciales-y-movimiento.md) y por el
[escenario 6](../guia/router-escenarios.md#6--hashes-tgt-y-pfx).

---

## Primeras acciones

1. **Confirmar el nivel de acceso**: null session y guest primero. Es la validación más barata y
   decide el resto del camino.
2. **Leer la política de contraseñas** (`--pass-pol`) **antes** de cualquier intento con listas.
   Un umbral bajo significa que el spraying bloquea cuentas del examen.
3. **Enumerar shares y sus permisos** y anotar cuáles permiten lectura y cuáles escritura.
4. **Leer lo accesible**: configs, backups, `web.config`, `unattend.xml`, scripts, bases KeePass.
   Buscá contraseñas, rutas internas y usuarios.
5. **Probar credenciales reutilizadas** de otros servicios (FTP, web, correo) y las que
   encontraste en los shares.
6. Con credenciales válidas: **enumerar usuarios, grupos y equipos**, y recién después decidir
   movimiento o dump.

```bash
# Nivel de acceso (cheatsheet nxc.md, sección SMB)
nxc smb <IP>
nxc smb <IP> -u '' -p ''            # null session
nxc smb <IP> -u 'guest' -p ''      # guest

# Con credenciales: shares y política
nxc smb <IP> -u <USER> -p <PASS> -d <dominio> --shares
nxc smb <IP> -u <USER> -p <PASS> -d <dominio> --pass-pol

# Alternativa si no hay NetExec
smbclient -L //<IP>/ -N
```

Sintaxis completa: [`../cheatsheets/nxc.md`](../cheatsheets/nxc.md). No inventes flags.

---

## Puntos de decisión

Cada fila es una observación con su destino. No saltes de fila sin registrar la evidencia.

| Observación después de enumerar | Ruta | Documento |
| --- | --- | --- |
| Null session o guest listan shares | Leer los shares y buscar configs, backups y credenciales | [`../guia/02-enumeracion-servicios.md`](../guia/02-enumeracion-servicios.md#445--smb) |
| Share con **lectura** | Descargar y grepear por `passw`, `cred`, `*.config`, `*.xml` | [`../cheatsheets/nxc.md`](../cheatsheets/nxc.md) |
| Share con **escritura** | Evaluar ejecución o DLL hijack; **no** escribas sin poder revertir | [`../guia/02-enumeracion-servicios.md`](../guia/02-enumeracion-servicios.md#445--smb) |
| Política de bloqueo baja (≤3) | No spraying: usá credenciales ya obtenidas | [`../cheatsheets/nxc.md`](../cheatsheets/nxc.md) |
| Credenciales válidas (de un share o reutilizadas) | Validar en SMB; sumar usuarios, grupos y equipos | [`credenciales-y-movimiento.md`](credenciales-y-movimiento.md) |
| Sos admin local de un host | Dump SAM/LSA y localizar sesiones de admin | [`../cheatsheets/nxc.md`](../cheatsheets/nxc.md) |
| Varios hosts sin firma SMB | Candidatos a relay (ver `--gen-relay-list`) | [`../cheatsheets/nxc.md`](../cheatsheets/nxc.md) |
| Share interesante pero sin permiso | Registrar el hallazgo y probar otra credencial | [`credenciales-y-movimiento.md`](credenciales-y-movimiento.md) |
| Nada accesible anónimo ni autenticado | Parquear y volver por enumeración | [escenario 1](../guia/router-escenarios.md#1--puertos-abiertos-triage) |

Dos reglas que ordenan el resto:

- **La política de bloqueo manda.** Leela antes de disparar listas; una cuenta bloqueada en el
  DC del examen es un problema real.
- **La reutilización de credenciales es el camino más frecuente.** Lo que aparece en un share
  suele servir en WinRM, LDAP, MSSQL o RDP.

---

## Evidencia

Capturá evidencia **en cada pivote**, no al final:

- Nivel de acceso observado (anónimo, guest o autenticado) con el comando y la salida cruda.
- Lista de shares con **permisos por share** (lectura/escritura) y la ruta guardada.
- Archivo con el secreto, su ruta exacta dentro del share y el origen de la credencial.
- Matriz `usuario × máquina`: en qué hosts y protocolos se probó cada credencial y el resultado
  por host ([`../examen/ad-credenciales.md`](../examen/ad-credenciales.md)).
- Política de contraseñas leída, con su salida, para justificar lo que **no** se hizo.
- Captura del acceso obtenido con la **IP de la víctima** en el mismo cuadro
  ([`../guia/08-reporte-y-evidencia.md`](../guia/08-reporte-y-evidencia.md)).

---

## Parqueo

- **Regla de 45–90 minutos sin progreso verificable**: parqueá la ruta actual, escribí el estado
  y aplicá el [escenario 11](../guia/router-escenarios.md#11--estoy-trabado). Volvés después.
- Parqueás cuando ya probaste el nivel de acceso anónimo, los shares accesibles y la credencial
  vigente, y no queda share con permiso sin leer.
- Antes de parquear, dejá escrito: qué shares viste, con qué permiso, qué buscaste y qué
  credencial sigue viva.
- Si hay una credencial sin probar en otro protocolo, no estás bloqueado: estás incompleto.

---

## Enlaces

- Router, escenario 1 (triage de puertos): [`../guia/router-escenarios.md#1--puertos-abiertos-triage`](../guia/router-escenarios.md#1--puertos-abiertos-triage)
- Router, escenario 6 (hashes, TGT y PFX): [`../guia/router-escenarios.md#6--hashes-tgt-y-pfx`](../guia/router-escenarios.md#6--hashes-tgt-y-pfx)
- Enumeración 445/139: [`../guia/02-enumeracion-servicios.md#445--smb`](../guia/02-enumeracion-servicios.md#445--smb)
- Chuletas: [`../cheatsheets/nxc.md`](../cheatsheets/nxc.md) · [`../cheatsheets/impacket.md`](../cheatsheets/impacket.md)
- Movimiento lateral: [`credenciales-y-movimiento.md`](credenciales-y-movimiento.md)
- Otras tarjetas de servicios: [`http-web.md`](http-web.md) · [`ldap.md`](ldap.md)

---

## Alcance

Etiqueta: pendiente-politica

La etiqueta de alcance obligatoria es `pendiente-politica` porque no hay, registrada localmente,
una fuente con URL **y** estado de recuperación observado que permita clasificar el alcance de
estas técnicas. Motivo y estado: [`../_sistema/SALUD-DOCUMENTAL.md`](../_sistema/SALUD-DOCUMENTAL.md).
