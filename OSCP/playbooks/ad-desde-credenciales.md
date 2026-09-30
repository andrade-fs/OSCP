# Playbook AD — desde credenciales válidas

Cadena de triage para cuando el set de AD arranca en modo *assumed breach*: **te dieron usuario y
contraseña de dominio** y todavía no elegiste ruta. Este documento decide el **orden** y los
**cortes**; el detalle de cada comando vive en las guías y cheatsheets canónicas.

- Formato de la tarjeta: [`../plantillas/como-usar-plantillas.md`](../plantillas/como-usar-plantillas.md).
- Referencia por fases: [`../guia/05-active-directory.md`](../guia/05-active-directory.md).
- Recorrido secuencial: [`../guia/walkthroughs/AD-walkthrough.md`](../guia/walkthroughs/AD-walkthrough.md).

---

## Entrada

Abrí esta tarjeta con **una** observación concreta:

- Tenés credenciales de dominio (usuario + contraseña) y la autenticación devuelve `[+]` contra
  el DC en SMB o LDAP.
- El dominio y el DC objetivo ya están identificados, y todavía **no** elegiste el vector de
  escalada.
- Todavía no sabés si el camino al Domain Admin pasa por ACLs, delegación, un SPN débil, una
  sesión de admin o un servicio vulnerable.

Si la credencial **no** autentica, no es este playbook: pasá por el escenario 9 del
[`router`](../guia/router-escenarios.md#9--kerberos-y-entorno) (entorno, reloj, DNS) o por el
escenario 6 (material de credencial).

---

## Primeras acciones

1. Fijar el **contexto** antes de tocar nada: dominio, realm, IP del DC, `/etc/hosts`, DNS y
   reloj sincronizado. Un reloj desfasado convierte cualquier intento Kerberos en un error
   confuso.
2. **Validar** la credencial y tu identidad en el dominio: qué sos, a qué llegás y cuál es la
   política de bloqueo.
3. **Enumerar de una pasada** y guardar la salida a archivo: shares, usuarios, grupos, equipos,
   sesiones y política.
4. **BloodHound primero, atacar después**: recolectar, marcarte como *Owned* y correr
   *Shortest Paths from Owned Principals*. Ese camino, si existe, es el plan.
5. **Mapear relaciones**: ACLs sobre objetos, delegación (constrained/RBCD/unconstrained),
   cuentas con SPN, sesiones de admin por host.
6. **Elegir una ruta** y escribirla antes de ejecutar. Si no hay ruta clara, volver a enumerar:
   el bloqueo casi siempre es enumeración incompleta, no falta de técnica.

```bash
export DOMAIN='<dominio.local>' REALM='<DOMINIO.LOCAL>' DC_IP='<DC_IP>'
# DNS + reloj: ver ../guia/Entorno.md y ../guia/05-active-directory.md ("Configuración previa")

# Enumeración de una pasada (cheatsheet SMB de ../cheatsheets/nxc.md)
nxc smb "$DC_IP" -u "$USER" -p "$PASS" -d "$DOMAIN" \
    --shares --users --groups --computers --loggedon-users --pass-pol

# Recolección para el grafo (../guia/05-active-directory.md, Fase 1.2)
bloodhound-python -u "$USER" -p "$PASS" -d "$DOMAIN" -ns "$DC_IP" -c all --zip
```

Referencia de sintaxis: [`../cheatsheets/nxc.md`](../cheatsheets/nxc.md) y
[`../cheatsheets/impacket.md`](../cheatsheets/impacket.md). No inventes flags: están verificados
en esas chuletas.

---

## Puntos de decisión

Cada fila es una observación con su destino. No saltes de fila sin registrar la evidencia.

| Observación después de enumerar | Ruta | Documento |
| --- | --- | --- |
| Camino corto *Owned* → DA en BloodHound | Abuso de ACLs o delegación | [`../guia/05-active-directory.md`](../guia/05-active-directory.md) Fases 3–4 |
| Usuario con SPN y hash débil | Kerberoast → crackeo offline | [`kerberos-y-tickets.md`](kerberos-y-tickets.md) |
| Cuenta sin preautenticación | AS-REP roasting | [`kerberos-y-tickets.md`](kerberos-y-tickets.md) |
| `Domain Users` es admin local en algún host | PtH / ejecución directa en ese host | [`credenciales-y-movimiento.md`](credenciales-y-movimiento.md) |
| Sesión de admin localizada en un host | Harvest (SAM/LSA/LSASS) | [`../guia/walkthroughs/AD-walkthrough.md`](../guia/walkthroughs/AD-walkthrough.md) Bloque 4 |
| Plantilla de certificado, CA o `.pfx` | Inventario ADCS | [`certipy-y-adcs.md`](certipy-y-adcs.md) |
| Derechos `DCSync` sobre el dominio | DCSync | [`../guia/05-active-directory.md`](../guia/05-active-directory.md) Fase 6.1 |
| Ya sos Domain Admin | Cerrar evidencia y pasar al siguiente set | [`../guia/08-reporte-y-evidencia.md`](../guia/08-reporte-y-evidencia.md) |
| Nada claro todavía | Crackear lo que tengas y volver a enumerar | [`../guia/walkthroughs/AD-walkthrough.md`](../guia/walkthroughs/AD-walkthrough.md) Bloque 2 |

Dos reglas que ordenan el resto:

- **Cobrá puntos parciales primero.** El set de AD no es todo o nada: 10 + 10 antes de pelear el
  DC.
- **No modifiques el entorno sin poder revertirlo.** Si vas a tocar una ACL o una plantilla,
  hacé backup antes y restaurá al terminar.

---

## Evidencia

Capturá evidencia **en cada pivote**, no al final:

- Credencial usada (usuario/dominio) y **en qué hosts y protocolos** se probó, con el resultado
  por host.
- Salida **cruda** de cada enumeración, guardada a archivo y con su ruta.
- El `.zip` de BloodHound y el **camino elegido** escrito con tus palabras.
- Credenciales o hashes nuevos, con su origen, en el documento global de credenciales:
  [`../examen/ad-credenciales.md`](../examen/ad-credenciales.md).
- Fecha/hora del hallazgo y de cada intento relevante.

Atajo ya documentado para no perder salida: [`../guia/05-active-directory.md`](../guia/05-active-directory.md)
§12.

---

## Parqueo

Condición explícita para dejar de insistir y moverte:

- **Regla de 45–90 minutos sin progreso verificable**: parqueá la ruta actual, escribí el estado
  y aplicá el [escenario 11](../guia/router-escenarios.md#11--estoy-trabado). Volvés después.
- Parqueás cuando el camino elegido está **bloqueado** y existe un **segundo camino documentado
  sin explorar**.
- Antes de parquear, dejá escrito: qué probé, qué falló, qué queda pendiente y qué credencial
  sigue viva.
- Si ya cobraste 10 + 10, parquear el DC no es perder: es asegurar lo ganado y decidir el resto
  con la cabeza fría.

---

## Enlaces

- Router, escenario 5: [`../guia/router-escenarios.md#5--ad-con-credenciales`](../guia/router-escenarios.md#5--ad-con-credenciales)
- Guía AD por fases: [`../guia/05-active-directory.md`](../guia/05-active-directory.md)
- Walkthrough del set: [`../guia/walkthroughs/AD-walkthrough.md`](../guia/walkthroughs/AD-walkthrough.md)
- Entorno (reloj, DNS): [`../guia/Entorno.md`](../guia/Entorno.md)
- Cheatsheets: [`../cheatsheets/nxc.md`](../cheatsheets/nxc.md) · [`../cheatsheets/impacket.md`](../cheatsheets/impacket.md)
- Credenciales globales: [`../examen/ad-credenciales.md`](../examen/ad-credenciales.md) · [`../examen/00-dashboard.md`](../examen/00-dashboard.md)
- Playbooks de esta rebanada: [`kerberos-y-tickets.md`](kerberos-y-tickets.md) · [`certipy-y-adcs.md`](certipy-y-adcs.md) · [`credenciales-y-movimiento.md`](credenciales-y-movimiento.md)

---

## Alcance

Etiqueta: pendiente-politica

La etiqueta de alcance obligatoria es `pendiente-politica` porque no hay, registrada localmente,
una fuente con URL **y** estado de recuperación observado que permita clasificar el alcance de
estas técnicas. Motivo y estado: [`../_sistema/SALUD-DOCUMENTAL.md`](../_sistema/SALUD-DOCUMENTAL.md).
