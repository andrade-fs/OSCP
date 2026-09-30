# Playbook — LDAP (389/636/3269)

Camino de decisión para cuando **LDAP o LDAPS responde** y querés enumerar el dominio, sea de forma
**anónima** o con **credenciales**. Ordena el trabajo desde el *naming context* hasta el mapeo de
relaciones (usuarios, grupos, equipos, cuentas atacables y delegación) y fija cuándo conviene
parquear. El detalle de comandos vive en las guías y cheatsheets canónicas.

- Formato de la tarjeta: [`../plantillas/como-usar-plantillas.md`](../plantillas/como-usar-plantillas.md).
- Enumeración del puerto: [`../guia/02-enumeracion-servicios.md`](../guia/02-enumeracion-servicios.md#389--ldap).
- Guía AD por fases: [`../guia/05-active-directory.md`](../guia/05-active-directory.md).

---

## Entrada

Abrí esta tarjeta con **una** observación concreta:

- El puerto **389**, **636** o **3269** responde y no sabés si acepta bind anónimo.
- Tenés credenciales de dominio y querés enumerar usuarios, grupos, equipos y política **por
  LDAP** en vez de por SMB.
- Necesitás el *naming context* o la base del dominio para armar consultas y recolectar para el
  grafo.
- Todavía **no** mapeaste las relaciones: quién es miembro de qué, qué cuentas tienen SPN o qué
  objetos delegan.

Si ya tenés credenciales y estás eligiendo el **camino al Domain Admin**, el orden completo está
en [`ad-desde-credenciales.md`](ad-desde-credenciales.md).

---

## Primeras acciones

1. **Obtener el naming context** con una búsqueda `base`. Es el punto de partida de toda consulta.
2. **Probar bind anónimo o null bind** antes de asumir que hace falta credencial.
3. **Enumerar de una pasada** y guardar la salida a archivo: usuarios, grupos y equipos.
4. **Volcar cómodo** el dominio (HTML/JSON) y **recolectar para el grafo** (BloodHound) si hay
   credenciales: el grafo revela el camino más corto mejor que una lista.
5. **Mapear relaciones**: membresías de grupos privilegiados, cuentas sin preautenticación,
   cuentas con SPN y objetos con delegación.
6. **Leer los campos de texto libre** (`description`, `info`, `comment`): contraseñas pegadas
   aparecen más seguido de lo que debería.

```bash
# Naming context y bind anónimo (guía 02-enumeracion-servicios.md, sección 389)
ldapsearch -x -H ldap://<IP> -s base namingcontexts
ldapsearch -x -H ldap://<IP> -b "DC=<dominio>,DC=<tld>" -s sub "(objectClass=user)" sAMAccountName

# Con credenciales: usuarios, grupos y equipos (cheatsheet nxc.md, sección LDAP)
nxc ldap <IP> -u <USER> -p <PASS> -d <dominio> --users
nxc ldap <IP> -u <USER> -p <PASS> -d <dominio> --groups
nxc ldap <IP> -u <USER> -p <PASS> -d <dominio> --computers

# Volcado cómodo y recolección para el grafo
ldapdomaindump ldap://<IP> -u '<dominio>\<USER>' -p '<PASS>'
nxc ldap <IP> -u <USER> -p <PASS> -d <dominio> --bloodhound --collection All --dns-server <IP>
```

Sintaxis y opciones completas: [`../cheatsheets/nxc.md`](../cheatsheets/nxc.md) y
[`../cheatsheets/impacket.md`](../cheatsheets/impacket.md). No inventes flags.

---

## Puntos de decisión

Cada fila es una observación con su destino. No saltes de fila sin registrar la evidencia.

| Observación después de enumerar | Ruta | Documento |
| --- | --- | --- |
| Bind anónimo devuelve naming contexts | Enumerar la base del dominio y buscar `description` | [`../guia/02-enumeracion-servicios.md`](../guia/02-enumeracion-servicios.md#389--ldap) |
| `description`/`info` con contraseñas pegadas | Registrar y probar reutilización de a un host | [`credenciales-y-movimiento.md`](credenciales-y-movimiento.md) |
| Usuarios sin preautenticación | AS-REP roasting → crackeo offline | [`kerberos-y-tickets.md`](kerberos-y-tickets.md) |
| Cuentas con SPN | Kerberoasting → crackeo offline | [`kerberos-y-tickets.md`](kerberos-y-tickets.md) |
| Grupos privilegiados (Backup/Account Operators, Helpdesk) | Mapear membresías y ACLs sobre objetos | [`../guia/05-active-directory.md`](../guia/05-active-directory.md) |
| Delegación (constrained, unconstrained o RBCD) | `--find-delegation` y ruta de abuso | [`ad-desde-credenciales.md`](ad-desde-credenciales.md) |
| Necesitás el camino más corto al DA | BloodHound primero, atacar después | [`ad-desde-credenciales.md`](ad-desde-credenciales.md) |
| LDAPS/3269 expone una CA | Inventario ADCS | [`certipy-y-adcs.md`](certipy-y-adcs.md) |
| Nada accesible anónimo ni autenticado | Parquear y volver por enumeración | [escenario 1](../guia/router-escenarios.md#1--puertos-abiertos-triage) |

Dos reglas que ordenan el resto:

- **Enumerá de una pasada y guardá la salida.** El bloqueo casi siempre es enumeración incompleta,
  no falta de técnica.
- **El grafo antes que la lista.** BloodHound convierte usuarios y grupos sueltos en un camino
  concreto.

---

## Evidencia

Capturá evidencia **en cada pivote**, no al final:

- *Naming context* observado y la base usada en cada consulta.
- Qué bind funcionó: anónimo, null o con credencial (`usuario@dominio`).
- Salida cruda de usuarios, grupos y equipos, guardada a archivo con su ruta.
- El archivo de `ldapdomaindump` y el `.zip` de BloodHound, más el camino elegido escrito con tus
  palabras.
- Credenciales halladas en `description`/`info`, con su origen, en
  [`../examen/ad-credenciales.md`](../examen/ad-credenciales.md).
- Captura del acceso obtenido con la **IP de la víctima** en el mismo cuadro
  ([`../guia/08-reporte-y-evidencia.md`](../guia/08-reporte-y-evidencia.md)).

---

## Parqueo

- **Regla de 45–90 minutos sin progreso verificable**: parqueá la ruta actual, escribí el estado
  y aplicá el [escenario 11](../guia/router-escenarios.md#11--estoy-trabado). Volvés después.
- Parqueás cuando el dominio ya está enumerado por LDAP (usuarios, grupos, equipos) y las
  relaciones mapeadas, y el camino elegido está bloqueado con un **segundo camino documentado sin
  explorar**.
- Antes de parquear, dejá escrito: qué bind usaste, qué enumeraste, qué hallaste y qué credencial
  sigue viva.
- Si SMB todavía no se enumeró por completo, no estás bloqueado: estás incompleto.

---

## Enlaces

- Router, escenario 1 (triage de puertos): [`../guia/router-escenarios.md#1--puertos-abiertos-triage`](../guia/router-escenarios.md#1--puertos-abiertos-triage)
- Router, escenario 5 (AD con credenciales): [`../guia/router-escenarios.md#5--ad-con-credenciales`](../guia/router-escenarios.md#5--ad-con-credenciales)
- Enumeración 389/636: [`../guia/02-enumeracion-servicios.md#389--ldap`](../guia/02-enumeracion-servicios.md#389--ldap)
- Guía AD por fases: [`../guia/05-active-directory.md`](../guia/05-active-directory.md)
- Chuletas: [`../cheatsheets/nxc.md`](../cheatsheets/nxc.md) · [`../cheatsheets/impacket.md`](../cheatsheets/impacket.md)
- Playbooks de AD: [`ad-desde-credenciales.md`](ad-desde-credenciales.md) · [`kerberos-y-tickets.md`](kerberos-y-tickets.md) · [`certipy-y-adcs.md`](certipy-y-adcs.md) · [`credenciales-y-movimiento.md`](credenciales-y-movimiento.md)
- Otras tarjetas de servicios: [`http-web.md`](http-web.md) · [`smb.md`](smb.md)

---

## Alcance

Etiqueta: pendiente-politica

La etiqueta de alcance obligatoria es `pendiente-politica` porque no hay, registrada localmente,
una fuente con URL **y** estado de recuperación observado que permita clasificar el alcance de
estas técnicas. Motivo y estado: [`../_sistema/SALUD-DOCUMENTAL.md`](../_sistema/SALUD-DOCUMENTAL.md).
