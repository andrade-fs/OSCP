# Playbook — Certipy y ADCS

Qué hacer cuando **aparece una CA, una plantilla, un certificado o un `.pfx`**: inventariar
primero, interpretar después, recién entonces decidir. Explica los conceptos de Certipy en
castellano y qué artefacto esperar en cada paso.

> **Aviso de alcance, explícito.** La documentación local del vault marca hoy los
> **certificados/ADCS como fuera de alcance** y la **coerción como prohibida**
> ([`../guia/05-active-directory.md`](../guia/05-active-directory.md) §"Fuera de alcance / prohibido").
> Esa clasificación **no está verificada** contra una fuente accesible con URL y estado de
> recuperación observado. Por eso este playbook **no afirma política de examen**: es una guía de
> **reconocimiento y de práctica en labs**, con etiqueta `pendiente-politica`. No trates ESC,
> relay ni coerción como *verificado-examen*.

- Formato de la tarjeta: [`../plantillas/como-usar-plantillas.md`](../plantillas/como-usar-plantillas.md).
- Referencia de herramienta (v5, verificada): [`../cheatsheets/certipy.md`](../cheatsheets/certipy.md).
- Mapa de ESC: [`../cheatsheets/adcs-esc.md`](../cheatsheets/adcs-esc.md).

---

## Entrada

Abrí esta tarjeta con **una** observación concreta:

- Enumerás el dominio y aparece una **CA** o un servidor con rol **ADCS** (endpoint de enrolamiento
  HTTP/RPC, objeto de CA, plantillas).
- BloodHound marca una arista hacia objetos **PKI/ADCS** (plantilla, CA, contenedores).
- Encontrás un **`.pfx` / `.pem` / certificado** reutilizable, o una **plantilla** de certificado
  con permisos interesantes.
- Tenés un **certificado** y no sabés qué hacer con él (autenticar, convertir a hash, forjar).

Si lo que tenés es una credencial normal y no hay CA ni certificado, no es esta tarjeta: volvé a
[`ad-desde-credenciales.md`](ad-desde-credenciales.md).

**Conceptos de Certipy, en castellano.** Leé esta tabla antes de interpretar el inventario.

| Concepto | Qué es | Artefacto esperado |
| --- | --- | --- |
| **CA** | Autoridad de Certificación: emite los certificados del dominio | nombre de la CA; objeto PKI |
| **Plantilla** | Molde con permisos, EKU y sujeto: define quién puede pedir qué | nombre de plantilla |
| **Enrolamiento** | El acto de **pedir** un certificado contra una plantilla | `.pfx` (certificado + clave) |
| **PFX** | Archivo con el certificado **y su clave privada** | `*.pfx`, con contraseña opcional |
| **ESC\*** | Familias de **configuraciones débiles** documentadas | reporte del inventario (`-text`/`-json`) |
| **Autenticar con el certificado** | Canjear el certificado por acceso | `.ccache` de Kerberos y/o **hash NT** |

---

## Primeras acciones

1. **Inventariar antes de pedir nada.** El primer paso siempre es el inventario, nunca una
   solicitud de certificado.
2. **Interpretar** el resultado: ¿hay CA?, ¿qué plantillas?, ¿qué requisito pide cada una?
3. **Elegir la referencia documentada** local (`../cheatsheets/certipy.md` o `../cheatsheets/adcs-esc.md`).
   La v5 que tenés **no** coincide con casi todo el material online (v4): copiar de internet
   falla.
4. **Validar antes de solicitar**: confirmar la sintaxis exacta de tu versión y el nombre real de
   la CA y de la plantilla. Si vas a **modificar** una plantilla, backup primero.
5. **Solicitar solo con el prerrequisito confirmado**, documentar el resultado y **restaurar** el
   estado original.

```bash
# Inventario ADCS (verificado en ../cheatsheets/certipy.md §1)
certipy-ad find -u "$USER@$DOMAIN" -p "$PASS" -dc-ip "$DC_IP" -vulnerable -stdout

# Confirmar la sintaxis de TU versión antes de pedir (v5 != v4)
certipy-ad req --help
```

Regla dura de la casa: verificar siempre con `certipy-ad <subcomando> --help`
([`../cheatsheets/certipy.md`](../cheatsheets/certipy.md)).

---

## Puntos de decisión

| Observación en el inventario | Qué significa | Requisito a confirmar **antes** de pedir | Referencia |
| --- | --- | --- | --- |
| Plantilla con `ENROLLEE_SUPPLIES_SUBJECT` + auth de cliente | Candidata a **ESC1** | poder enrolar en esa plantilla | [`../cheatsheets/certipy.md`](../cheatsheets/certipy.md) §2 |
| Plantilla con EKU `Any Purpose` o sin EKU | Candidata a **ESC2** | poder enrolar | [`../cheatsheets/adcs-esc.md`](../cheatsheets/adcs-esc.md) |
| `WriteDacl`/`GenericWrite` sobre la plantilla | Candidata a **ESC4** | escritura + **backup** | [`../cheatsheets/certipy.md`](../cheatsheets/certipy.md) §3 |
| Rol `ManageCA` / `ManageCertificates` | Candidata a **ESC7** | ser oficial de CA | [`../cheatsheets/adcs-esc.md`](../cheatsheets/adcs-esc.md) |
| Relay al endpoint HTTP/RPC de la CA | Candidata a **ESC8/ESC11** | forzar autenticación | ver aviso de abajo |
| Plantillas enumeradas pero **ninguna** con requisito alcanzable | No forzar el camino | — | parquear y volver por enumeración |
| Un `.pfx` suelto, sin CA accesible | Puede autenticar igual | probar `auth` en un host | [`../cheatsheets/certipy.md`](../cheatsheets/certipy.md) §2 |

> **Coerción y relay (ESC8/ESC11).** Estas variantes necesitan **forzar** la autenticación de la
> víctima, y el vault documenta la coerción como **prohibida** para el examen. No lo tomes como
> política verificada: la clasificación sigue `pendiente-politica`. Si tu intención es
> reconocimiento o práctica de lab, la referencia es
> [`../cheatsheets/rpc-coercion.md`](../cheatsheets/rpc-coercion.md) (marcada para labs) y
> [`../cheatsheets/adcs-esc.md`](../cheatsheets/adcs-esc.md). No lo uses como si estuviera
> habilitado en el examen.
>
> Y la limitación de red, siempre: un relay necesita que la víctima **vuelva a vos**. A través de
> un SOCKS proxy **no funciona**; ver [`../guia/07-pivoting.md`](../guia/07-pivoting.md).

Higiene de estado (obligatoria antes de modificar cualquier objeto PKI):

| Acción | Comando documentado | Por qué |
| --- | --- | --- |
| Backup de la plantilla | `certipy-ad template ... -save-configuration <archivo>.json` | poder revertir |
| Restaurar al terminar | `certipy-ad template ... -write-configuration <archivo>.json` | dejar el entorno como estaba |
| Limpiar Shadow Credentials | `certipy-ad shadow remove` / `shadow clear` | no dejar credenciales colgadas |

---

## Evidencia

Capturá evidencia **en cada pivote**:

- Salida **cruda** del inventario con su formato (`-text`, `-json`, `-csv`) y su **ruta**.
- Nombre exacto de la **CA** y de la **plantilla**, con el escenario que interpretaste.
- Si tocaste algo: el `.json` de **backup**, los cambios hechos y la **confirmación de la
  restauración**.
- Cada artefacto obtenido (`.pfx`, `.ccache`, hash NT) con su **ruta y hash** del archivo, y a
  quién suplanta.
- Nombre de archivo real de la herramienta en tu máquina (`certipy-ad`), para que el reporte sea
  reproducible.

---

## Parqueo

- **Regla de 45–90 minutos sin progreso verificable**: si el inventario no da ningún requisito
  alcanzable, parqueá ADCS y volvé por enumeración
  ([escenario 11](../guia/router-escenarios.md#11--estoy-trabado)).
- Parqueás cuando el inventario está leído e interpretado, o cuando no podés modificar el entorno
  sin poder revertirlo.
- Antes de parquear: dejá el entorno **como lo encontraste** y anotá qué se tocó y qué se
  restauró.
- Si la duda es **política** (¿entra o no en el examen?) y no hay fuente accesible, no inventes
  la respuesta: registralo como `pendiente-politica` y seguí por el camino estándar.

---

## Enlaces

- Router, escenario 5 (AD con credenciales): [`../guia/router-escenarios.md#5--ad-con-credenciales`](../guia/router-escenarios.md#5--ad-con-credenciales)
- Guía AD, alcance y prohibiciones: [`../guia/05-active-directory.md`](../guia/05-active-directory.md)
- Chuletas: [`../cheatsheets/certipy.md`](../cheatsheets/certipy.md) · [`../cheatsheets/adcs-esc.md`](../cheatsheets/adcs-esc.md) · [`../cheatsheets/rpc-coercion.md`](../cheatsheets/rpc-coercion.md)
- Pivoting (límite del relay): [`../guia/07-pivoting.md`](../guia/07-pivoting.md)
- Estado de la documentación y etiquetas: [`../_sistema/SALUD-DOCUMENTAL.md`](../_sistema/SALUD-DOCUMENTAL.md)
- Playbooks de esta rebanada: [`ad-desde-credenciales.md`](ad-desde-credenciales.md) · [`credenciales-y-movimiento.md`](credenciales-y-movimiento.md) · [`kerberos-y-tickets.md`](kerberos-y-tickets.md)

---

## Alcance

Etiqueta: pendiente-politica

La etiqueta de alcance obligatoria es `pendiente-politica`: la guía local marca ADCS como fuera de
alcance, pero **esa clasificación no está verificada** contra una fuente accesible (la *OSCP+ Exam
Guide* devolvió HTTP 403) y por lo tanto **no** puede subirse a `verificado-examen`. Motivo y
estado: [`../_sistema/SALUD-DOCUMENTAL.md`](../_sistema/SALUD-DOCUMENTAL.md).
