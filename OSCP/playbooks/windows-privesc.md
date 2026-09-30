# Playbook — Shell Windows de bajo privilegio (triage manual)

Camino de decisión para cuando tenés **ejecución como usuario común en Windows** y todavía no
sos `Administrator` ni `SYSTEM`. La idea es un **triage manual ordenado** —contexto, token,
grupos, servicios, tareas, autoruns, credenciales y archivos— que corre **antes o en paralelo**
a winPEAS, no después ni en su lugar. winPEAS orienta ("qué mirar"); vos decidís, confirmás a
mano y registrás. Las rutas de privilegio puntuales (Potato, AlwaysInstallElevated, SeBackup,
UAC, kernel) van **últimas** y solo cuando el triage dejó un hallazgo con condición de
ejecución real.

- Formato de la tarjeta: [`../plantillas/como-usar-plantillas.md`](../plantillas/como-usar-plantillas.md).
- Paso a paso con comandos: [`../guia/lpe/LPE-Windows.md#2-orden-de-ataque--checklist-rápido`](../guia/lpe/LPE-Windows.md#2-orden-de-ataque--checklist-rápido).
- Referencia profunda por técnica: [`../guia/04-privesc-windows.md#orden-de-ataque--resumen-ejecutivo`](../guia/04-privesc-windows.md#orden-de-ataque--resumen-ejecutivo).
- Router, escenario 4: [`../guia/router-escenarios.md#4--shell-windows--escalada`](../guia/router-escenarios.md#4--shell-windows--escalada).

---

## Entrada

Abrí esta tarjeta con **una** observación concreta:

- Tenés shell como usuario común en Windows (cmd, PowerShell o WinRM) y **no** sos
  `Administrator`/`SYSTEM`.
- Todavía no corriste enumeración manual: estás por arrancar el triage.
- winPEAS/PowerUp ya marcaron hallazgos en rojo o amarillo y no sabés cuál priorizar.
- `whoami /groups` muestra `Administrators` pero con **Medium Mandatory Level** (token filtrado
  por UAC): sos admin local, pero no tenés token completo. Es un branch aparte, al final del
  triage.

Si el acceso vino por un puerto de servicio, pasá primero por
[escenario 1](../guia/router-escenarios.md#1--puertos-abiertos-triage) y por el playbook de ese
servicio ([`winrm.md`](winrm.md), [`smb.md`](smb.md), [`mssql.md`](mssql.md)); esta tarjeta
asume que ya tenés el host y el usuario efectivo.

---

## Primeras acciones

Corré el triage en este orden. Cada escalón es barato y descarta o habilita el siguiente; no
saltees al final.

1. **Contexto e identidad.** Versión, arquitectura y parches: `whoami /all`, `hostname`,
   `systeminfo`, `systeminfo | findstr /B /C:"OS Name" /C:"OS Version" /C:"System Type"`,
   `wmic qfe get Captcha,HotFixID,InstalledOn`. La *build* decide qué Potato y qué CVE aplican;
   los parches deciden los exploits de kernel. Detalle:
   [`LPE-Windows.md#11-identidad-y-sistema`](../guia/lpe/LPE-Windows.md#11-identidad-y-sistema).
2. **Privilegios de token.** `whoami /priv`. Es el chequeo de 5 segundos que define la mitad de
   los caminos. Muchos privilegios aparecen `Disabled` pero tu propio proceso puede habilitarlos
   al usarlos. Detalle:
   [`LPE-Windows.md#12-privilegios--whoami-priv-lo-más-rentable`](../guia/lpe/LPE-Windows.md#12-privilegios--whoami-priv-lo-más-rentable)
   y [`04-privesc-windows.md#1-privilegios-de-token--el-vector-más-directo`](../guia/04-privesc-windows.md#1-privilegios-de-token--el-vector-más-directo).
3. **Grupos y nivel de integridad.** `whoami /groups` y `net localgroup administrators`.
   `Backup`, `Server`, `Account` y `Print Operators`, `DnsAdmins`, `Hyper-V Administrators`
   cambian la ruta por completo. Si sos `Administrators` con `Medium Mandatory Level`, anotá el
   token filtrado: eso es UAC, no escalada. Detalle:
   [`LPE-Windows.md#13-grupos`](../guia/lpe/LPE-Windows.md#13-grupos) y
   [`04-privesc-windows.md#1b-grupos-de-windows-que-dan-escalada`](../guia/04-privesc-windows.md#1b-grupos-de-windows-que-dan-escalada).
4. **Servicios y rutas escribibles.** `wmic service get name,displayname,pathname,startmode,startname`,
   `sc query state= all`, `icacls "C:\ruta\del\servicio.exe"`, `accesschk.exe -uwcqv "Users" *`.
   Buscá **ruta sin comillas**, **binario escribible** o **config modificable**
   (`SERVICE_CHANGE_CONFIG`). En paralelo, directorios escribibles:
   `accesschk.exe -uwdqs "Users" C:\` y `accesschk.exe -uwqs "Users" C:\*.*`. Detalle:
   [`LPE-Windows.md#152-servicios`](../guia/lpe/LPE-Windows.md#152-servicios) y
   [`04-privesc-windows.md#2-servicios-mal-configurados`](../guia/04-privesc-windows.md#2-servicios-mal-configurados).
5. **Tareas programadas.** `schtasks /query /fo LIST /v` o
   `Get-ScheduledTask | Where-Object {$_.TaskPath -notlike "\Microsoft*"}`. Buscá una tarea que
   corra como SYSTEM/Administrador ejecutando un script o binario que **vos podés editar**, y
   credenciales dentro de los argumentos. Detalle:
   [`LPE-Windows.md#153-tareas-programadas-schtasks`](../guia/lpe/LPE-Windows.md#153-tareas-programadas-schtasks).
6. **Registro: Run/RunOnce y Winlogon/AutoLogon.** Primero los autoruns:
   `reg query HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run`,
   `reg query HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce`,
   `reg query HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run`,
   `wmic startup get caption,command`. Después el branch de Winlogon con la ubicación que ya
   está documentada en [`04-privesc-windows.md#4-autoruns-y-tareas-programadas`](../guia/04-privesc-windows.md#4-autoruns-y-tareas-programadas)
   y [`LPE-Windows.md#154-autoruns--registro`](../guia/lpe/LPE-Windows.md#154-autoruns--registro):
   `reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"`.
   **Branch Winlogon/AutoLogon**: esa misma clave resuelve dos preguntas distintas.
   Si `AutoAdminLogon=1` y hay `DefaultPassword`, el objetivo es la **credencial del login
   automático** (a veces en claro, a veces cifrada: volcala con la herramienta ya documentada en
   [`verificado-2026.md`](../guia/verificado-2026.md)). Si **no** hay `DefaultPassword` pero
   `Userinit` o `Shell` apuntan a un binario o script escribible, el objetivo es un **hook de
   logon**: reemplazás el destino y esperás el próximo login. Decidí cuál de los dos es **antes**
   de tocar nada; no copies payloads genéricos, el payload se arma para el host.
7. **Credenciales guardadas.** `cmdkey /list`; si hay credenciales, probá ejecutar como esa
   credencial con la receta documentada (`runas /savecred`). Buscá además
   `unattend.xml`/`sysprep.xml`, GPP `cpassword`, historial de PowerShell y perfiles WiFi. Detalle:
   [`LPE-Windows.md#16-credenciales-almacenadas`](../guia/lpe/LPE-Windows.md#16-credenciales-almacenadas) y
   [`04-privesc-windows.md#5-credenciales-almacenadas`](../guia/04-privesc-windows.md#5-credenciales-almacenadas).
8. **Archivos.** Archivos escribibles y secretos: `dir /s /b C:\ 2>nul | findstr /i "pass backup .kdbx id_rsa .ovpn .rdp"`,
   configs con credenciales (`web.config`, `*.config`) y el historial de PSReadLine de todos los
   usuarios. Detalle: [`LPE-Windows.md#17-sistema-de-archivos`](../guia/lpe/LPE-Windows.md#17-sistema-de-archivos).
9. **Solo ahora, rutas de privilegio puntuales.** Cuando un escalón anterior dejó un hallazgo
   confirmado: `SeImpersonate`/`SeAssignPrimaryToken` → `potato_check64.exe` y la variante que
   corresponde a la build; `AlwaysInstallElevated` con **las dos** claves en `0x1`; UAC
   **solo** si ya sos Administrador local; kernel/CVE **último** y con riesgo de crashear. No
   dispares una ruta de privilegio sin un hallazgo que la habilite.

> **winPEAS como orientación, no como decisión.** Corré `.\winPEASx64.exe` (o `PowerUp.ps1` con
> `Invoke-AllChecks`, solo para chequear) en paralelo al triage: te marca rojo/amarillo, pero
> cada hallazgo se confirma con el comando manual del escalón correspondiente. PowerUp se usa
> **solo para enumerar**; la explotación se hace a mano.

---

## Puntos de decisión

Cada fila es una observación con su siguiente paso, su evidencia y su regla de parqueo. No saltes
de fila sin registrar.

| Observación | Qué inspeccionar después | Evidencia a capturar | Parqueo (45–90 min) |
| --- | --- | --- | --- |
| Contexto incompleto: no tenés build/arquitectura/parches | Completar `systeminfo` y `wmic qfe` antes de cualquier CVE | `systeminfo.txt` y salida de `wmic qfe` | Si en 45 min no fijaste build y parches, parqueá la rama CVE y seguí con token/servicios |
| `whoami /priv` con `SeImpersonate`/`SeAssignPrimaryToken` | `potato_check64.exe` y elegir la variante por build y servicios | Salida del detector y la tabla build → variante | Si la variante elegida falla o no aplica, parqueá la rama Potato y volvé al triage (no cambies de Potato en loop) |
| `whoami /priv` sin privilegios útiles | Seguir con grupos, servicios, tareas, autoruns, credenciales y archivos | `whoami /priv` crudo | 45 min por bloque: si dos bloques consecutivos no dan hallazgo, reordená y seguí |
| Grupo privilegiado (`Backup`/`Server`/`Account`/`Print Operators`, `DnsAdmins`, `Hyper-V Administrators`) | Leer la ruta del grupo concreto; la ruta cambia por completo | `whoami /groups` y la membresía observada | Si el grupo requiere un control remoto o un prerrequisito que no tenés, parqueá y anotá el faltante |
| Servicio con ruta sin comillas o binario/config escribible | Confirmar el permiso con `icacls`/`accesschk` y elegir el vector (intermedio, binario o config) | Salida de `wmic service`, `icacls` y `accesschk` | Si no podés reiniciar el servicio o el servicio no arranca, parqueá la ruta de servicio |
| Directorio escribible bajo una ruta que ejecuta SYSTEM | Buscar el proceso, servicio o tarea que ejecute desde ahí | `accesschk` y la lista de procesos con su ruta | Sin un proceso que ejecute desde ese directorio, es escritura sin efecto: parqueá |
| Tarea programada como SYSTEM con script o binario escribible | Volcar la acción, `schtasks /query /tn "<TASK>" /xml` y buscar credenciales en los argumentos | XML de la tarea y `findstr` de credenciales | Si el trigger no es alcanzable en el examen, parqueá y documentá el trigger |
| `Run`/`RunOnce` apuntando a un ejecutable escribible | Confirmar el permiso sobre el destino y decidir el reemplazo | `reg query` del autorun y `icacls` del destino | Si no podés alcanzar el arranque o el login, parqueá la ruta de autorun |
| Winlogon con `AutoAdminLogon=1` y `DefaultPassword` | Volcar y, si está cifrado, descifrar la credencial; probar reutilización antes de atacar | `reg query` de Winlogon, el valor y la prueba por host | Si la credencial no valida ni en el host ni en el dominio, parqueá |
| Winlogon sin `DefaultPassword` pero `Userinit`/`Shell` escribible | Branch hook de logon: reemplazar el destino y esperar el login | `reg query ... /v Userinit`, `/v Shell` e `icacls` del destino | Si no podés forzar un login, parqueá el branch de hook |
| Credenciales guardadas (`cmdkey`, `unattend.xml`, GPP, historial, WiFi) | Probar reutilización en el resto del examen antes de crackear | Salida de `cmdkey`, el `cpassword` y el resultado por host | Credencial probada y fallida en todos los hosts probados = parqueo documentado |
| Archivos con secretos (`.kdbx`, `id_rsa`, `.rdp`, configs) | Abrir el archivo y decidir si es una credencial utilizable | Ruta, hash y contenido del archivo | Si el formato exige una clave que no tenés, parqueá y anotá la dependencia |
| `Administrators` con `Medium Mandatory Level` | UAC bypass, **solo** si ya sos Administrador local | `whoami /groups` con el nivel de integridad | Si el bypass no da token completo, parqueá; sin ser admin local, UAC no aplica y no es escalada |
| `AlwaysInstallElevated` con las dos claves en `0x1` | Instalar el MSI como SYSTEM | `reg query` de **ambas** claves | Si solo una clave está en `1`, no aplica: parqueá la rama |
| Triage completo recorrido y anotado sin hallazgo | Recién ahora kernel/CVE, con la versión exacta y riesgo asumido | `systeminfo`, `wmic qfe` y el exploit elegido para esa build | Parqueo obligatorio: kernel es último; si puede tumbar la máquina, parqueá y volvé por enumeración |
| winPEAS marcó algo que no confirmaste | Volver al comando manual del escalón correspondiente | Salida del comando manual | No persigas un rojo de winPEAS sin reproducción manual: 45 min por hallazgo |

---

## Evidencia

Capturá evidencia **en cada escalón**, no al final:

- Contexto del host: `hostname`, `systeminfo` y `wmic qfe` (build, arquitectura y parches).
- Token y grupos: `whoami /all`, `whoami /priv` y `whoami /groups` crudos, con el nivel de
  integridad.
- Enumeración local cruda por bloque: servicios, tareas programadas (`LIST /v` y el XML de la
  tarea elegida), autoruns y Winlogon, credenciales guardadas y archivos escribibles.
- Salida de winPEAS/PowerUp como **orientación**, marcando qué confirmaste a mano.
- Por cada vector elegido: el comando exacto, su salida y el resultado (`éxito` / `sin efecto` /
  `falló`) con el mensaje literal.
- Prueba de privilegio en el mismo cuadro que la flag (`whoami`/`whoami /groups` + IP de la
  víctima): [`08-reporte-y-evidencia.md#qué-debe-mostrar-cada-captura`](../guia/08-reporte-y-evidencia.md#qué-debe-mostrar-cada-captura).
- Ruta y hash de los archivos de evidencia de la máquina.

---

## Parqueo

- **Regla de 45–90 minutos sin progreso verificable**: parqueá el bloque actual, escribí el
  estado y aplicá el [escenario 11](../guia/router-escenarios.md#11--estoy-trabado). Volvés
  después.
- Parqueás cuando el triage completo está **recorrido y anotado por bloque**, incluso sin
  hallazgo: el reporte necesita ver el recorrido, no solo el éxito.
- Reglas específicas: no cambies de Potato en loop (si no aplica, volvé al triage);
  `AlwaysInstallElevated` necesita las **dos** claves; UAC solo aplica si ya sos Administrador
  local; kernel/CVE es último y con riesgo de crashear la máquina.
- Antes de parquear, dejá escrito: qué bloque probaste, qué output obtuviste, qué descartaste y
  por qué, y qué credencial o hallazgo queda sin probar.
- Si hay una credencial sin probar en SMB, WinRM o MSSQL, no estás bloqueado: estás incompleto.

---

## Enlaces

- Router, escenario 4 (shell Windows + escalada): [`../guia/router-escenarios.md#4--shell-windows--escalada`](../guia/router-escenarios.md#4--shell-windows--escalada)
- Router, escenario 1 (triage de puertos): [`../guia/router-escenarios.md#1--puertos-abiertos-triage`](../guia/router-escenarios.md#1--puertos-abiertos-triage)
- Router, escenario 11 (estoy trabado): [`../guia/router-escenarios.md#11--estoy-trabado`](../guia/router-escenarios.md#11--estoy-trabado)
- Triage paso a paso: [`../guia/lpe/LPE-Windows.md`](../guia/lpe/LPE-Windows.md) · [`../guia/lpe/LPE-Windows.md#3-explotación-por-vector-comandos`](../guia/lpe/LPE-Windows.md#3-explotación-por-vector-comandos)
- Referencia profunda por técnica: [`../guia/04-privesc-windows.md`](../guia/04-privesc-windows.md) · [`../guia/04-privesc-windows.md#7-uac-si-sos-administrador-local-pero-con-token-filtrado`](../guia/04-privesc-windows.md#7-uac-si-sos-administrador-local-pero-con-token-filtrado) · [`../guia/04-privesc-windows.md#8-exploits-de-kernel`](../guia/04-privesc-windows.md#8-exploits-de-kernel)
- Familia Potato: [`../cheatsheets/potatoes.md#0-qué-potato-me-sirve-en-esta-máquina-potato_checkexe`](../cheatsheets/potatoes.md#0-qué-potato-me-sirve-en-esta-máquina-potato_checkexe) · [`../cheatsheets/potatoes.md#2-elección-rápida-tldr`](../cheatsheets/potatoes.md#2-elección-rápida-tldr) · [`../cheatsheets/potatoes.md#3-matriz-de-compatibilidad-build--variante`](../cheatsheets/potatoes.md#3-matriz-de-compatibilidad-build--variante)
- Recetas del vault: [`../vault/indices/Tecnicas/seimpersonate.md`](../vault/indices/Tecnicas/seimpersonate.md) · [`../vault/indices/Tecnicas/token-impersonation.md`](../vault/indices/Tecnicas/token-impersonation.md) · [`../vault/indices/Tecnicas/unquoted-service-path.md`](../vault/indices/Tecnicas/unquoted-service-path.md) · [`../vault/indices/Tecnicas/scheduled-task.md`](../vault/indices/Tecnicas/scheduled-task.md) · [`../vault/indices/Tecnicas/alwaysinstallelevated.md`](../vault/indices/Tecnicas/alwaysinstallelevated.md) · [`../vault/indices/Tecnicas/gpp.md`](../vault/indices/Tecnicas/gpp.md) · [`../vault/indices/Tecnicas/uac-bypass.md`](../vault/indices/Tecnicas/uac-bypass.md) · [`../vault/indices/Tecnicas/kernel-exploit.md`](../vault/indices/Tecnicas/kernel-exploit.md)
- Transferencia de herramientas: [`../guia/06-payloads-shells-transferencia.md#3-transferencia-de-archivos`](../guia/06-payloads-shells-transferencia.md#3-transferencia-de-archivos)
- Reporte: [`../guia/08-reporte-y-evidencia.md`](../guia/08-reporte-y-evidencia.md)
- Formato de la tarjeta: [`../plantillas/como-usar-plantillas.md`](../plantillas/como-usar-plantillas.md)
- Otras tarjetas de servicio: [`winrm.md`](winrm.md) · [`smb.md`](smb.md) · [`mssql.md`](mssql.md) · [`nfs.md`](nfs.md)

---

## Alcance

Etiqueta: pendiente-politica

La etiqueta obligatoria es `pendiente-politica` porque no hay, registrada localmente, una fuente
con URL **y** estado de recuperación observado que permita clasificar el alcance de estas
técnicas. Motivo y estado: [`../_sistema/SALUD-DOCUMENTAL.md`](../_sistema/SALUD-DOCUMENTAL.md).
