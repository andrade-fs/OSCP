# Playbook — Kerberos y tickets

Cómo distinguir, con lo que tenés **en la mano**, entre contraseña, hash, clave y tique; y cómo
elegir el flujo correcto (AS-REP, Kerberoast, TGT, TGS) sin confundir un problema de entorno con
una credencial inválida. Los comandos están en las chuletas canónicas; acá está la decisión.

- Formato de la tarjeta: [`../plantillas/como-usar-plantillas.md`](../plantillas/como-usar-plantillas.md).
- Fuente de verdad de la fase Kerberos: [`../guia/05-active-directory.md`](../guia/05-active-directory.md) §6.
- Errores de entorno: [`../guia/Entorno.md`](../guia/Entorno.md) y [`../guia/05-active-directory.md`](../guia/05-active-directory.md) §6.

---

## Entrada

Abrí esta tarjeta con **una** observación concreta:

- Tenés un archivo o un valor que **no sabés clasificar**: ¿es una contraseña, un hash, una clave
  AES o un tique?
- Apareció un **hash con prefijo Kerberos** (AS-REP o TGS) y hay que decidir si se crackea o se
  usa.
- Kerberos **falla** con un error raro y no sabés si el problema es la credencial, el reloj, el
  DNS o el realm.

Tabla de reconocimiento (leela antes de tocar el material):

| Lo que ves | Qué **es** | Qué **no** es | Va a |
| --- | --- | --- | --- |
| `$krb5asrep$23$...` | hash AS-REP crackeable offline | una sesión válida | AS-REP |
| `$krb5tgs$23$*svc...$` | hash TGS de servicio (Kerberoast) | una credencial usable directa | Kerberoast |
| `*.ccache` / `*.kirbi` | tique ya emitido | un hash | Pass-the-Ticket |
| 32 hex o `aad3b...:` | hash NTLM | un tique | PtH / Overpass-the-Hash |
| clave de 128/256 bits etiquetada AES | clave Kerberos | una contraseña | Pass-the-Key |
| `KRB_AP_ERR_SKEW`, `Cannot contact any KDC` | problema de **entorno** | credencial inválida | reloj / DNS |

---

## Primeras acciones

Orden fijo: **reloj → DNS/nombre → realm → recién ahí la credencial.**

1. Descartá el **reloj** primero: es la causa más frecuente y la más barata de arreglar.
2. Verificá **DNS y resolución de nombre**: usá el FQDN del dominio, no la IP, en los comandos
   Kerberos.
3. Confirmá el **realm** en mayúsculas y la configuración de `krb5.conf`.
4. **Clasificá el material** con la tabla de Entrada y anotá su origen antes de usarlo.
5. Elegí el flujo (AS-REP / Kerberoast / TGT / TGS) y escribí a qué te lleva.
6. Si hay que crackear, dejalo corriendo en paralelo pero **no bloquees** la ruta de uso directo.

```bash
kinit "$USER@$REALM"        # pedir TGT y klist/kdestroy: ../guia/05-active-directory.md §6
export KRB5CCNAME="$PWD/ticket.ccache"    # usar un tique ya emitido

# AS-REP y Kerberoast (sintaxis verificada en ../cheatsheets/impacket.md)
GetNPUsers.py "$DOMAIN/$USER:$PASS" -dc-ip "$DC_IP" -request -outputfile asrep.txt
GetUserSPNs.py "$DOMAIN/$USER:$PASS" -dc-ip "$DC_IP" -request -outputfile kerb.txt

# Convertir un hash NTLM en TGT (Pass-the-Key): ../cheatsheets/impacket.md
getTGT.py "$DOMAIN/$USER" -hashes :"$NTHASH" -dc-ip "$DC_IP"
```

Alternativas por NetExec: [`../cheatsheets/nxc.md`](../cheatsheets/nxc.md) (secciones SMB y LDAP).
No inventes flags.

---

## Puntos de decisión

| Material / síntoma | Decisión | Destino |
| --- | --- | --- |
| Hash `$krb5asrep$` | crackeo offline → credencial nueva | [`ad-desde-credenciales.md`](ad-desde-credenciales.md) |
| Hash `$krb5tgs$` | crackeo offline; priorizá **cuentas de servicio** | [`credenciales-y-movimiento.md`](credenciales-y-movimiento.md) |
| Contraseña o hash + puerto 88 con NTLM bloqueado | Overpass-the-Hash → TGT | [`../cheatsheets/impacket.md`](../cheatsheets/impacket.md) |
| Tique `.ccache`/`.kirbi` presente | **usarlo** (PtT); no crackear | [`../guia/05-active-directory.md`](../guia/05-active-directory.md) §5.2 |
| TGS vía S4U / delegación | `getST -impersonate` | [`../guia/05-active-directory.md`](../guia/05-active-directory.md) Fase 4 |
| `-impersonate` ausente en S4U | el tique es de tu usuario: **no escala** | volver a elegir la variante |
| El crackeo no termina y hay uso directo | dejar corriendo y seguir con el uso directo | este documento, Parqueo |
| Error de entorno | documentarlo y corregir reloj/DNS | tabla de caveats, abajo |

Caveats explícitos de **reloj y DNS** (no los saltees: son la mitad de los "Kerberos no anda"):

| Síntoma | Causa probable | Verificar |
| --- | --- | --- |
| `KRB_AP_ERR_SKEW` | reloj desfasado (>5 min) | hora local vs. la del DC; `ntpdate`/`rdate` |
| `Cannot contact any KDC` | el nombre no resuelve | `/etc/hosts` y `/etc/resolv.conf` |
| `KDC_ERR_C_PRINCIPAL_UNKNOWN` | usuario o realm mal | `$REALM` en **mayúsculas** |
| `Server not found in Kerberos DB` | SPN o DNS | hostname **exacto** en `/etc/hosts` |
| `Connection refused` con `-k` | `KRB5CCNAME` mal o vencido | `export` + `klist` |
| Kerberos falla tras el túnel | UDP no pasa por SOCKS | `udp_preference_limit = 0` en `krb5.conf` |

---

## Evidencia

Capturá evidencia **en cada pivote**:

- **Mensaje de error literal**, tal cual salió, con el comando exacto que lo produjo.
- Reloj local vs. reloj del DC, y el contenido de `krb5.conf`.
- Cada archivo de material con su **ruta y hash**: `asrep.txt`, `kerb.txt`, `*.ccache`, `*.kirbi`.
- A qué usuario/dominio corresponde cada tique y en qué hosts se usó.
- Cada credencial o hash nuevo, con su origen, en
  [`../examen/ad-credenciales.md`](../examen/ad-credenciales.md).

---

## Parqueo

- **Regla de 45–90 minutos sin progreso verificable**: si el crackeo no avanzó y no tenés una
  ruta de uso directo, parqueá el material y volvé por enumeración
  ([escenario 11](../guia/router-escenarios.md#11--estoy-trabado)).
- Parqueás cuando el material está clasificado, registrado con su origen y probado, o cuando el
  error está identificado como **entorno** (no como credencial inválida) y anotado.
- Un hash probado y fallido **igual** va al reporte como intento documentado: no lo descartes en
  silencio.
- No repitas un intento ya registrado: repetir es lo que bloquea cuentas.

---

## Enlaces

- Router, escenario 6 (hashes, TGT y PFX): [`../guia/router-escenarios.md#6--hashes-tgt-y-pfx`](../guia/router-escenarios.md#6--hashes-tgt-y-pfx)
- Router, escenario 9 (Kerberos y entorno): [`../guia/router-escenarios.md#9--kerberos-y-entorno`](../guia/router-escenarios.md#9--kerberos-y-entorno)
- Guía AD, trucos Kerberos: [`../guia/05-active-directory.md`](../guia/05-active-directory.md)
- Entorno: [`../guia/Entorno.md`](../guia/Entorno.md)
- Chuletas: [`../cheatsheets/impacket.md`](../cheatsheets/impacket.md) · [`../cheatsheets/nxc.md`](../cheatsheets/nxc.md) · [`../cheatsheets/ad-avanzado.md`](../cheatsheets/ad-avanzado.md)
- Playbooks de esta rebanada: [`ad-desde-credenciales.md`](ad-desde-credenciales.md) · [`credenciales-y-movimiento.md`](credenciales-y-movimiento.md) · [`certipy-y-adcs.md`](certipy-y-adcs.md)

---

## Alcance

Etiqueta: pendiente-politica

La etiqueta de alcance obligatoria es `pendiente-politica` porque no hay, registrada localmente,
una fuente con URL **y** estado de recuperación observado que permita clasificar el alcance de
estas técnicas. Motivo y estado: [`../_sistema/SALUD-DOCUMENTAL.md`](../_sistema/SALUD-DOCUMENTAL.md).
