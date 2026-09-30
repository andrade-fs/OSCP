# Playbook — WinRM (5985/5986)

Camino de decisión para cuando **WinRM responde** y todavía no sabés quién puede autenticarse ni
qué privilegio tenés. Ordena el trabajo por **acceso → autenticación → contexto del host →
pivote de credencial o privilegio** y fija cuándo conviene parquear. El detalle de comandos vive
en las guías y cheatsheets canónicas.

- Formato de la tarjeta: [`../plantillas/como-usar-plantillas.md`](../plantillas/como-usar-plantillas.md).
- Enumeración del puerto: [`../guia/02-enumeracion-servicios.md`](../guia/02-enumeracion-servicios.md#5985--winrm).
- Chuleta de la herramienta: [`../cheatsheets/nxc.md`](../cheatsheets/nxc.md#winrm--shell-de-verdad).

---

## Entrada

Abrí esta tarjeta con **una** observación concreta:

- El puerto **5985** o **5986** está abierto y todavía no sabés si tus credenciales sirven.
- Tenés usuario y contraseña, un hash NTLM o un tique/ccache y querés validarlo contra WinRM.
- WinRM **validó** y ya tenés shell, pero todavía no sabés qué privilegio real tenés en ese host.
- Todavía **no** definiste si el objetivo es ejecutar un comando puntual, quedarte con una shell
  interactiva o pivotar a otro host.

Si el material de credencial es lo que estás eligiendo (hash, tique o `.pfx`), pasá primero por
[escenario 6](../guia/router-escenarios.md#6--hashes-tgt-y-pfx) y por
[`credenciales-y-movimiento.md`](credenciales-y-movimiento.md).

---

## Primeras acciones

1. **Validar antes de abrir shell**: un comando suelto (`-x whoami`) confirma credencial y
   ejecución sin gastar una sesión interactiva.
2. **Elegir el tipo de autenticación según el material**: contraseña, hash (pass-the-hash) o
   tique Kerberos. No conviertas un hash si el servicio lo acepta directo.
3. **Confirmar el contexto del host**: nombre, sistema y usuario efectivo dentro de la sesión,
   con `whoami` y `whoami /all`. Un WinRM válido no implica administrador local.
4. **Separar los dos niveles de acceso**: miembro de `Administrators` y miembro de
   `Remote Management Users` dan privilegios muy distintos sobre el mismo host.
5. **Decidir el objetivo**: comando puntual, shell interactiva (`evil-winrm`) o pivote a otro
   host con la misma credencial.
6. **Registrar cada validación con su salida**, incluso las que fallaron.

```bash
# Validar y ejecutar sin shell interactiva (cheatsheet nxc.md, sección WinRM)
/usr/bin/nxc winrm <IP> -u <USER> -p <PASS> -d <dominio> -x whoami
/usr/bin/nxc winrm <IP> -u <USER> -H <NTHASH> -d <dominio>

# Shell interactiva (guía 02-enumeracion-servicios.md, sección 5985)
evil-winrm -i <IP> -u <USER> -p '<PASS>'
evil-winrm -i <IP> -u <USER> -H <NTHASH>
evil-winrm -i <IP> -u <USER> -p '<PASS>' -s /opt/scripts -e /opt/exes
evil-winrm -i <IP> -u <USER> -K ticket.ccache -r <dominio.local>
```

Alternativas de comando puntual (WMI, SMB, PsExec) y su requisito por método:
[`../guia/05-active-directory.md#54-ejecución-remota-qué-elegir`](../guia/05-active-directory.md#54-ejecución-remota-qué-elegir).
No inventes flags.

---

## Puntos de decisión

Cada fila es una observación con su destino. No saltes de fila sin registrar la evidencia.

| Observación después de validar | Ruta | Documento |
| --- | --- | --- |
| La credencial no valida | Probar hash o tique; revisar dominio vs local | [`credenciales-y-movimiento.md`](credenciales-y-movimiento.md) |
| Valida con comando suelto | Abrir shell interactiva con `evil-winrm` | [`../cheatsheets/nxc.md`](../cheatsheets/nxc.md#winrm--shell-de-verdad) |
| Valida con hash | Pass-the-hash; no crackees si el servicio lo acepta | [`../guia/04-privesc-windows.md`](../guia/04-privesc-windows.md#pass-the-hash) |
| Valida con tique/ccache | Ajustar `KRB5CCNAME` y realm antes de usarlo | [`kerberos-y-tickets.md`](kerberos-y-tickets.md) |
| Sos miembro de `Administrators` | Dump de SAM/LSA, alta de usuario o pivote a otros hosts | [`../guia/04-privesc-windows.md`](../guia/04-privesc-windows.md) |
| Sos de `Remote Management Users` pero no admin | Enumerar el host y evaluar escalada local | [`../guia/lpe/LPE-Windows.md`](../guia/lpe/LPE-Windows.md#1-enumeración-inicial--el-bloque-que-no-se-saltea) |
| `whoami /priv` con `SeImpersonate` | Familia Potato en el host | [`../cheatsheets/potatoes.md`](../cheatsheets/potatoes.md) |
| La misma credencial sirve en otro host | Movimiento lateral con la matriz `usuario × máquina` | [`../guia/05-active-directory.md`](../guia/05-active-directory.md#fase-5--movimiento-lateral) |
| El host es el DC | Tratar el acceso como camino a DCSync, no como shell suelta | [`ad-desde-credenciales.md`](ad-desde-credenciales.md) |
| No valida en ningún host probado | Parquear y volver por enumeración | [escenario 1](../guia/router-escenarios.md#1--puertos-abiertos-triage) |

Dos reglas que ordenan el resto:

- **Validar no es ser admin.** WinRM puede dar shell a un usuario común: medí el privilegio antes
  de asumir que tenés el host.
- **La credencial es el activo reutilizable.** Si algo validó en WinRM, anotalo en la matriz
  `usuario × máquina` antes de seguir, porque suele servir en SMB o MSSQL.

---

## Evidencia

Capturá evidencia **en cada pivote**, no al final:

- Material de credencial usado (contraseña, hash o tique), con su origen.
- Comando de validación exacto y su salida cruda, incluidos los intentos fallidos.
- `whoami` y `whoami /all` dentro del host, con grupos y privilegios.
- Método elegido y por qué (`-x` puntual vs. shell interactiva vs. `-s`/`-e`).
- Actualización de la matriz `usuario × máquina` con el resultado por host
  ([`../examen/ad-credenciales.md`](../examen/ad-credenciales.md)).
- Captura del acceso obtenido con la **IP de la víctima** en el mismo cuadro
  ([`../guia/08-reporte-y-evidencia.md`](../guia/08-reporte-y-evidencia.md)).

---

## Parqueo

- **Regla de 45–90 minutos sin progreso verificable**: parqueá la ruta actual, escribí el estado
  y aplicá el [escenario 11](../guia/router-escenarios.md#11--estoy-trabado). Volvés después.
- Parqueás cuando el material está validado (o descartado) en cada host relevante y el privilegio
  real del usuario en ese host quedó medido y anotado.
- Antes de parquear, dejá escrito: qué credencial probaste, en qué hosts, con qué resultado y qué
  material sigue sin probar.
- Si hay una credencial sin probar en SMB, LDAP o MSSQL, no estás bloqueado: estás incompleto.

---

## Enlaces

- Router, escenario 1 (triage de puertos): [`../guia/router-escenarios.md#1--puertos-abiertos-triage`](../guia/router-escenarios.md#1--puertos-abiertos-triage)
- Router, escenario 6 (hashes, TGT y PFX): [`../guia/router-escenarios.md#6--hashes-tgt-y-pfx`](../guia/router-escenarios.md#6--hashes-tgt-y-pfx)
- Router, escenario 11 (estoy trabado): [`../guia/router-escenarios.md#11--estoy-trabado`](../guia/router-escenarios.md#11--estoy-trabado)
- Enumeración 5985/5986: [`../guia/02-enumeracion-servicios.md#5985--winrm`](../guia/02-enumeracion-servicios.md#5985--winrm)
- Chuletas: [`../cheatsheets/nxc.md#winrm--shell-de-verdad`](../cheatsheets/nxc.md#winrm--shell-de-verdad) · [`../cheatsheets/potatoes.md`](../cheatsheets/potatoes.md) · [`../cheatsheets/impacket.md`](../cheatsheets/impacket.md)
- Escalada Windows: [`../guia/lpe/LPE-Windows.md`](../guia/lpe/LPE-Windows.md) · [`../guia/04-privesc-windows.md`](../guia/04-privesc-windows.md)
- Movimiento: [`credenciales-y-movimiento.md`](credenciales-y-movimiento.md) · [`kerberos-y-tickets.md`](kerberos-y-tickets.md) · [`ad-desde-credenciales.md`](ad-desde-credenciales.md)
- Otras tarjetas de servicios: [`http-web.md`](http-web.md) · [`smb.md`](smb.md) · [`ldap.md`](ldap.md)

---

## Alcance

Etiqueta: pendiente-politica

La etiqueta de alcance obligatoria es `pendiente-politica` porque no hay, registrada localmente,
una fuente con URL **y** estado de recuperación observado que permita clasificar el alcance de
estas técnicas. Motivo y estado: [`../_sistema/SALUD-DOCUMENTAL.md`](../_sistema/SALUD-DOCUMENTAL.md).
