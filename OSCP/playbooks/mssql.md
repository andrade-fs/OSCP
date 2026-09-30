# Playbook — MSSQL (1433)

Camino de decisión para cuando **MSSQL responde** y todavía no sabés qué autenticación acepta,
qué contexto y rol tenés, si podés leer o escribir archivos o si llegaste a ejecución de
comandos. Ordena el trabajo por **autenticación → contexto → rol → archivos → ejecución** y fija
cuándo conviene parquear. El detalle de consultas y payloads vive en las guías y cheatsheets
canónicas.

- Formato de la tarjeta: [`../plantillas/como-usar-plantillas.md`](../plantillas/como-usar-plantillas.md).
- Enumeración del puerto: [`../guia/02-enumeracion-servicios.md`](../guia/02-enumeracion-servicios.md#1433--mssql).
- Chuleta de la técnica: [`../cheatsheets/mssql-injection.md`](../cheatsheets/mssql-injection.md).

---

## Entrada

Abrí esta tarjeta con **una** observación concreta:

- El puerto **1433** está abierto y todavía no sabés con qué credenciales responde.
- Tenés credenciales de dominio o locales y querés validarlas contra MSSQL.
- Conseguiste acceso a la instancia y todavía no sabés si sos `sysadmin`, si podés impersonar o
  si podés leer y escribir archivos.
- Todavía **no** determinaste si el camino es inyección web, autenticación directa o ejecución de
  comandos.

Si la base aparece **detrás de una web** por inyección, el punto de entrada es
[escenario 2](../guia/router-escenarios.md#2--objetivo-web) y su chuleta; esta tarjeta decide qué
hacer una vez que tenés sesión o credenciales de MSSQL.

---

## Primeras acciones

1. **Determinar qué autenticación acepta**: credencial de dominio, usuario SQL local (`sa`) o
   Windows auth. La ruta cambia según el modo; no mezcles `--local-auth` con un login de dominio.
2. **Confirmar el contexto real**: versión, base actual, usuario efectivo y si es `sysadmin`.
   `SELECT user_name()` responde por la base; `SELECT SYSTEM_USER` por el login de servidor.
3. **Mapear el rol y los permisos** con `IS_SRVROLEMEMBER('sysadmin')` y
   `fn_my_permissions(NULL, 'SERVER')`.
4. **Buscar impersonación** antes de descartar la instancia: una cuenta sin rol `sysadmin` puede
   tener `IMPERSONATE` sobre una que sí lo tiene. Es el puente más común.
5. **Evaluar el acceso a archivos** (`OpenRowset`/`BULK`) y, si sos `sysadmin`, la ejecución de
   comandos. Registrá cada intento con su salida.
6. **Revisar enlaces (*linked servers*)** si los hay: habilitan ejecución en otra instancia.

```bash
# Validar credenciales (cheatsheet nxc.md, sección MSSQL)
/usr/bin/nxc mssql <IP> -u <USER> -p <PASS> -d <dominio> -q "SELECT @@version"
/usr/bin/nxc mssql <IP> -u sa -p '<PASS>' --local-auth

# Shell interactiva (guía 02-enumeracion-servicios.md, sección 1433)
mssqlclient.py <dominio>/<USER>:<PASS>@<IP> -windows-auth
```

Dentro de la sesión, las consultas de contexto, rol, impersonación, archivos y `xp_cmdshell`
están en [`../guia/02-enumeracion-servicios.md#1433--mssql`](../guia/02-enumeracion-servicios.md#1433--mssql)
y en [`../cheatsheets/mssql-injection.md`](../cheatsheets/mssql-injection.md). No inventes sintaxis.

---

## Puntos de decisión

Cada fila es una observación con su destino. No saltes de fila sin registrar la evidencia.

| Observación después de enumerar | Ruta | Documento |
| --- | --- | --- |
| `sa` con contraseña débil o vacía | Login directo y validar rol | [`../cheatsheets/nxc.md`](../cheatsheets/nxc.md#mssql) |
| Credencial de dominio válida | Validar en MSSQL y reutilizarla en otros protocolos | [`credenciales-y-movimiento.md`](credenciales-y-movimiento.md) |
| Autenticación rechazada en modo dominio | Probar Windows auth o login SQL local (`--local-auth`) | [`../guia/02-enumeracion-servicios.md`](../guia/02-enumeracion-servicios.md#1433--mssql) |
| Sos `sysadmin` | Ejecución de comandos con `xp_cmdshell` | [`../cheatsheets/mssql-injection.md`](../cheatsheets/mssql-injection.md) |
| No sos `sysadmin` pero podés `IMPERSONATE` | `EXECUTE AS` y encadenar hasta un `sysadmin` | [`../cheatsheets/mssql-injection.md`](../cheatsheets/mssql-injection.md) |
| Impersonación sin `sysadmin` alcanzable | Buscar enlaces y permisos de escritura | [`../cheatsheets/mssql-injection.md`](../cheatsheets/mssql-injection.md) |
| Necesitás leer o escribir un archivo | `OpenRowset`/`BULK` con el permiso correspondiente | [`../cheatsheets/mssql-injection.md`](../cheatsheets/mssql-injection.md) |
| Hay *linked servers* | Ejecutar en la instancia remota vía `EXECUTE ... AT` | [`../cheatsheets/mssql-injection.md`](../cheatsheets/mssql-injection.md) |
| Obtuviste ejecución de comandos | Revisar el privilegio del service account para escalar | [`../guia/lpe/LPE-Windows.md`](../guia/lpe/LPE-Windows.md) |
| El service account tiene `SeImpersonate` | Familia Potato en el host | [`../cheatsheets/potatoes.md`](../cheatsheets/potatoes.md) |
| La misma credencial sirve en otro host | Movimiento lateral (WinRM / SMB) | [`../guia/05-active-directory.md`](../guia/05-active-directory.md#fase-5--movimiento-lateral) |
| Sin acceso ni impersonación | Parquear y volver por enumeración | [escenario 1](../guia/router-escenarios.md#1--puertos-abiertos-triage) |

Dos reglas que ordenan el resto:

- **Contexto antes que payload.** `user_name()` y `IS_SRVROLEMEMBER` deciden qué consulta tiene
  sentido; copy-paste sin contexto es como enumerar sin mirar.
- **La instancia suele correr como usuario de servicio.** Si llegás a comandos, esa identidad con
  `SeImpersonate` es la escalada, no el final.

---

## Evidencia

Capturá evidencia **en cada pivote**, no al final:

- Modo de autenticación que funcionó (dominio, SQL local, Windows auth) y el comando exacto.
- Salida de `SELECT @@version`, `SYSTEM_USER`, `user_name()` y
  `IS_SRVROLEMEMBER('sysadmin')`.
- Resultado de `fn_my_permissions(NULL, 'SERVER')` y de la búsqueda de `IMPERSONATE`.
- La consulta que dio ejecución o lectura de archivos y su salida cruda.
- Identidad del service account y si tiene `SeImpersonate`, con la evidencia que lo prueba.
- Captura del acceso obtenido con la **IP de la víctima** en el mismo cuadro
  ([`../guia/08-reporte-y-evidencia.md`](../guia/08-reporte-y-evidencia.md)).

---

## Parqueo

- **Regla de 45–90 minutos sin progreso verificable**: parqueá la ruta actual, escribí el estado
  y aplicá el [escenario 11](../guia/router-escenarios.md#11--estoy-trabado). Volvés después.
- Parqueás cuando el modo de autenticación, el contexto, el rol y la impersonación ya están
  probados y anotados, y no queda login ni enlace sin revisar.
- Antes de parquear, dejá escrito: qué credencial probaste, con qué modo, qué salida dio y qué
  login o enlace sigue vivo.
- Si la base también es alcanzable desde una web sin probar, no estás bloqueado: estás incompleto.

---

## Enlaces

- Router, escenario 1 (triage de puertos): [`../guia/router-escenarios.md#1--puertos-abiertos-triage`](../guia/router-escenarios.md#1--puertos-abiertos-triage)
- Router, escenario 2 (objetivo web): [`../guia/router-escenarios.md#2--objetivo-web`](../guia/router-escenarios.md#2--objetivo-web)
- Router, escenario 11 (estoy trabado): [`../guia/router-escenarios.md#11--estoy-trabado`](../guia/router-escenarios.md#11--estoy-trabado)
- Enumeración 1433: [`../guia/02-enumeracion-servicios.md#1433--mssql`](../guia/02-enumeracion-servicios.md#1433--mssql)
- Chuletas: [`../cheatsheets/mssql-injection.md`](../cheatsheets/mssql-injection.md) · [`../cheatsheets/nxc.md#mssql`](../cheatsheets/nxc.md#mssql) · [`../cheatsheets/impacket.md`](../cheatsheets/impacket.md)
- Escalada Windows: [`../guia/lpe/LPE-Windows.md`](../guia/lpe/LPE-Windows.md) · [`../guia/04-privesc-windows.md`](../guia/04-privesc-windows.md) · [`../cheatsheets/potatoes.md`](../cheatsheets/potatoes.md)
- Inyección SQL manual: [`../guia/09-web.md#44-sql-injection-manual`](../guia/09-web.md#44-sql-injection-manual)
- Movimiento con la credencial: [`credenciales-y-movimiento.md`](credenciales-y-movimiento.md)
- Otras tarjetas de servicios: [`http-web.md`](http-web.md) · [`smb.md`](smb.md) · [`ldap.md`](ldap.md)

---

## Alcance

Etiqueta: pendiente-politica

La etiqueta de alcance obligatoria es `pendiente-politica` porque no hay, registrada localmente,
una fuente con URL **y** estado de recuperación observado que permita clasificar el alcance de
estas técnicas. Motivo y estado: [`../_sistema/SALUD-DOCUMENTAL.md`](../_sistema/SALUD-DOCUMENTAL.md).
