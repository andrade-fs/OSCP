# Playbook — Credenciales y movimiento lateral

Cómo manejar **material de credencial** (contraseña, hash NTLM, tique o certificado): de dónde
salió, cómo se usa sin romper nada, y cómo decidir el movimiento a la siguiente máquina. La
validación es **controlada, de a un servicio por vez**. Este playbook **no** contiene
instrucciones de spraying masivo.

- Formato de la tarjeta: [`../plantillas/como-usar-plantillas.md`](../plantillas/como-usar-plantillas.md).
- Movimiento lateral por fases: [`../guia/05-active-directory.md`](../guia/05-active-directory.md) Fase 5.
- Recorrido del set: [`../guia/walkthroughs/AD-walkthrough.md`](../guia/walkthroughs/AD-walkthrough.md) Bloques 3–5.

---

## Entrada

Abrí esta tarjeta con **una** observación concreta:

- Tenés **material reutilizable** en la mano y no sabés en qué host ni con qué protocolo usarlo
  primero.
- Conseguiste un usuario/contraseña, un hash NTLM, un `.ccache`/`.kirbi` o un certificado y hay
  que moverlo por el set.
- Ya usaste una credencial en un host y querés decidir el próximo salto sin repetir intentos ni
  bloquear cuentas.

Si todavía no clasificaste el material, empezá por [`kerberos-y-tickets.md`](kerberos-y-tickets.md).

---

## Primeras acciones

1. **Registrar la procedencia**: de dónde salió, en qué host, con qué usuario y cuándo.
2. **Clasificar el material** con la tabla de abajo: el tipo decide la herramienta, no al revés.
3. **Probar primero donde la credencial ya se usó**: un host conocido es la validación más barata
   y la que menos ruido hace.
4. **Validar de a un servicio por vez**: un host, un protocolo, un intento, y leé el resultado
   antes de ampliar. Nunca "todo contra todo" de una.
5. **Actualizar la matriz** `usuario × máquina` en cuanto cambia un resultado.
6. Recién cuando la validación controlada da verde, elegí el **método de ejecución** y movete.

```bash
# Validación controlada: UN host, UN protocolo, UN intento (secciones SMB/WinRM de ../cheatsheets/nxc.md)
nxc smb   "$TARGET" -u "$USER" -p "$PASS" -d "$DOMAIN"
nxc winrm "$TARGET" -u "$USER" -p "$PASS" -d "$DOMAIN" -x whoami

# Hash NTLM y tique (../cheatsheets/impacket.md)
psexec.py -hashes :"$NTHASH" "$DOMAIN/$USER@$TARGET"
export KRB5CCNAME="$PWD/ticket.ccache"     # PtT: ../guia/05-active-directory.md §5.2
```

> **Sobre spraying.** Este playbook **no** da recetas de spraying. La política de bloqueo manda y
> el spray controlado se decide **leyendo primero** la política de contraseñas, según lo ya
> documentado en [`../guia/05-active-directory.md`](../guia/05-active-directory.md) §2.3 y
> [`../cheatsheets/nxc.md`](../cheatsheets/nxc.md). Acá solo se valida **una** credencial que ya
> tenés.

---

## Puntos de decisión

Tabla material → uso directo. Elegí por **tipo**, no por costumbre:

| Material | Cómo se usa | Herramienta canónica | Dónde |
| --- | --- | --- | --- |
| Contraseña | Login normal | `nxc`, Impacket | [`../cheatsheets/nxc.md`](../cheatsheets/nxc.md) |
| Hash NTLM | Pass-the-Hash | `nxc -H`, `psexec -hashes` | [`../cheatsheets/impacket.md`](../cheatsheets/impacket.md) |
| Tique `.ccache`/`.kirbi` | Pass-the-Ticket | `KRB5CCNAME` + `-k -no-pass` | [`../guia/05-active-directory.md`](../guia/05-active-directory.md) §5.2 |
| Clave AES | Pass-the-Key | `getTGT -aesKey` | [`../cheatsheets/impacket.md`](../cheatsheets/impacket.md) |
| Certificado `.pfx` | Auth por certificado | `certipy-ad auth` | [`certipy-y-adcs.md`](certipy-y-adcs.md) |

Y una vez validada la credencial, la decisión de **movimiento**:

| Condición observada | Siguiente paso |
| --- | --- |
| Valida en SMB pero no en WinRM | El vector es SMB: buscá ejecución que SMB permita |
| Valida y sos admin local de un host | Ejecutá ahí; después harvest de SAM/LSA/LSASS |
| Hash válido pero NTLM bloqueado | Overpass-the-Hash → [`kerberos-y-tickets.md`](kerberos-y-tickets.md) |
| Tique presente | Usalo directo; **no** lo crackees |
| Hay sesión de admin localizada en un host | Priorizá ese host (objetivo: robar su hash/tique) |
| Un certificado autentica | Pasá a [`certipy-y-adcs.md`](certipy-y-adcs.md) |
| El material falla en todos los hosts probados | Registralo como intento **antes** de descartarlo |
| No avanzo y ya probé los hosts obvios | Parqueá y volvé por enumeración |

Higiene para no romper el set:

- **No repitas** un intento ya registrado: repetir es lo que bloquea cuentas.
- **No cambies** contraseñas si podés evitar la vía destructiva.
- Si modificás una ACL o una plantilla, backup antes y restaurá al terminar.

---

## Evidencia

Capturá evidencia **en cada pivote**:

- Tabla de procedencia: material, tipo, origen, hosts probados, resultado por host.
- El **comando exacto** y su output por cada validación.
- La **matriz `usuario × máquina`** actualizada en
  [`../examen/ad-credenciales.md`](../examen/ad-credenciales.md), y el estado global en
  [`../examen/00-dashboard.md`](../examen/00-dashboard.md).
- Captura del acceso obtenido con la **IP de la víctima** en el mismo cuadro
  ([`../guia/08-reporte-y-evidencia.md`](../guia/08-reporte-y-evidencia.md)).
- Ruta y hash de los archivos de material (`.ccache`, `.pfx`, dumps).

---

## Parqueo

- **Regla de 45–90 minutos sin progreso verificable**: parqueá el movimiento y volvé por
  enumeración ([escenario 11](../guia/router-escenarios.md#11--estoy-trabado)).
- Parqueás cuando el material está **registrado** y probado en cada host relevante.
- Un hash probado y fallido **igual** va al reporte como intento documentado: dejarlo afuera es
  perder evidencia.
- Los puntos del set son parciales: cobrá las máquinas que ya cerraste antes de insistir en la
  siguiente.

---

## Enlaces

- Router, escenario 6 (hashes, TGT y PFX): [`../guia/router-escenarios.md#6--hashes-tgt-y-pfx`](../guia/router-escenarios.md#6--hashes-tgt-y-pfx)
- Guía AD por fases: [`../guia/05-active-directory.md`](../guia/05-active-directory.md)
- Walkthrough del set: [`../guia/walkthroughs/AD-walkthrough.md`](../guia/walkthroughs/AD-walkthrough.md)
- Chuletas: [`../cheatsheets/impacket.md`](../cheatsheets/impacket.md) · [`../cheatsheets/nxc.md`](../cheatsheets/nxc.md)
- Credenciales y panel: [`../examen/ad-credenciales.md`](../examen/ad-credenciales.md) · [`../examen/00-dashboard.md`](../examen/00-dashboard.md)
- Reporte: [`../guia/08-reporte-y-evidencia.md`](../guia/08-reporte-y-evidencia.md)
- Playbooks de esta rebanada: [`ad-desde-credenciales.md`](ad-desde-credenciales.md) · [`kerberos-y-tickets.md`](kerberos-y-tickets.md) · [`certipy-y-adcs.md`](certipy-y-adcs.md)

---

## Alcance

Etiqueta: pendiente-politica

La etiqueta de alcance obligatoria es `pendiente-politica` porque no hay, registrada localmente,
una fuente con URL **y** estado de recuperación observado que permita clasificar el alcance de
estas técnicas. Motivo y estado: [`../_sistema/SALUD-DOCUMENTAL.md`](../_sistema/SALUD-DOCUMENTAL.md).
