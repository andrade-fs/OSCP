# Router de escenarios — qué hacer según lo que observás

**Un solo router para el examen.** No es material nuevo de ataque: es navegación.

Entrás acá con una **observación** (un puerto abierto, una web, una shell, un hash) y salís con
el **documento correcto del vault** y la condición de parqueo. El detalle de comandos vive en
las guías y cheatsheets canónicas, no acá.

- Punto de entrada operativo: [`00-inicio.md`](00-inicio.md).
- Reglas y restricciones del examen: [`00-reglas-examen.md`](00-reglas-examen.md).
- Estado real de la documentación (huecos, capa generada): [`SALUD-DOCUMENTAL`](../_sistema/SALUD-DOCUMENTAL.md).

---

## Cómo se usa (30 segundos)

1. Buscá tu observación en la **tabla de ruteo rápido**.
2. Abrí el escenario. Leé **Entrada** y **Primeras acciones**.
3. Antes de irte del escenario, registrá la **Evidencia** y verificá la **Condición de parqueo**.

> **Regla de 90 minutos**: si un escenario no avanza en 90 min, aplicá el
> [escenario 11 — estoy trabado](#11--estoy-trabado) y cambiá de máquina. Volvés después.

---

## Etiquetas de alcance (obligatorias)

Toda pieza del vault lleva **una sola** etiqueta:

| Etiqueta | Significa |
| --- | --- |
| `verificado-examen` | Contenido contrastado contra una fuente con **URL y estado de recuperación observado**, ambos registrados localmente. |
| `solo-laboratorio` | Sirve para practicar (HTB, PG, labs propios), no para el examen. |
| `prohibido` | La regla vigente lo excluye del examen. |
| `pendiente-politica` | Todavía no hay fuente accesible que permita clasificarlo. |

**Todo lo nuevo en este documento es `pendiente-politica`.** Motivo concreto: la *OSCP+ Exam
Guide* oficial no se pudo recuperar (HTTP 403) y ningún otro documento del repo registra a la
vez una URL y un estado de recuperación observado. Sin eso, `verificado-examen` sería una
afirmación inventada. `verificado-examen` queda reservado para una rebanada futura, cuando esa
evidencia exista localmente.

---

## Tabla de ruteo rápido

| Lo que observás | Escenario |
| --- | --- |
| nmap devolvió puertos y no sabés qué priorizar | [1 — Puertos abiertos (triage)](#1--puertos-abiertos-triage) |
| Hay un servicio HTTP/HTTPS o una app web | [2 — Objetivo web](#2--objetivo-web) |
| Tenés shell en Linux y sos usuario común | [3 — Shell Linux + escalada](#3--shell-linux--escalada) |
| Tenés shell en Windows y sos usuario común | [4 — Shell Windows + escalada](#4--shell-windows--escalada) |
| El set de AD te dio usuario y contraseña | [5 — AD con credenciales](#5--ad-con-credenciales) |
| Tenés un hash NTLM, un TGT/ccache o un PFX/PEM | [6 — Hashes, TGT y PFX](#6--hashes-tgt-y-pfx) |
| Ves una segunda red desde un host comprometido | [7 — Pivoting](#7--pivoting) |
| Necesitás subir o bajar un archivo/payload | [8 — Transferencia y payloads](#8--transferencia-y-payloads) |
| Kerberos falla con errores raros | [9 — Kerberos y entorno](#9--kerberos-y-entorno) |
| Conseguiste acceso o root/SYSTEM y hay que capturar | [10 — Reporte y evidencia](#10--reporte-y-evidencia) |
| Estás trabado y no sabés para dónde seguir | [11 — Estoy trabado](#11--estoy-trabado) |

> **Puertos que no aparecen acá**: el índice por puerto sigue siendo la referencia rápida de
> *precedentes* (`Ctrl+O` → número). Este router te dice **qué hacer**; el índice te dice **qué
> se hizo** en otras máquinas. Ver [`../vault/indices/Puertos.md`](../vault/indices/Puertos.md).

---

## Escenarios

Cada escenario tiene la misma forma: **Entrada · Primeras acciones · Puntos de decisión ·
Evidencia · Parqueo · Enlaces · Alcance**.

### 1 — Puertos abiertos (triage)

| Campo | Contenido |
| --- | --- |
| **Entrada** | Terminó el escaneo inicial y tenés una lista de puertos abiertos. Aún no decidiste por dónde entrar. |
| **Primeras acciones** | 1. Confirmá que el escaneo cubrió **todos** los TCP y el UDP que importa. 2. Anotá para cada puerto el **banner real**, no la etiqueta de nmap. 3. Ordená por probabilidad de acceso inicial, no por número de puerto. 4. Chequeá virtual hosts y `Host:` distintos antes de descartar un puerto web. |
| **Puntos de decisión** | ¿El puerto es un servicio conocido con enumeración documentada? → [`02-enumeracion-servicios.md`](02-enumeracion-servicios.md). ¿Es web? → [escenario 2](#2--objetivo-web). ¿Está filtrado o inalcanzable? → [escenario 7](#7--pivoting). |
| **Evidencia** | Comando de escaneo, rango de puertos, output crudo por máquina, fecha/hora y el `Host:`/nombre resuelto en `/etc/hosts`. |
| **Parqueo** | Parqueás cuando el mapa de puertos está completo y cada puerto tiene **una** hipótesis escrita. Parar antes de eso es enumeración incompleta, no bloqueo. |
| **Enlaces** | [`01-metodologia.md`](01-metodologia.md) · [`02-enumeracion-servicios.md`](02-enumeracion-servicios.md) · [`../playbooks/smb.md`](../playbooks/smb.md) · [`../playbooks/ldap.md`](../playbooks/ldap.md) · [`../playbooks/nfs.md`](../playbooks/nfs.md) · [`../playbooks/mssql.md`](../playbooks/mssql.md) · [`../playbooks/winrm.md`](../playbooks/winrm.md) · [`../cheatsheets/nxc.md`](../cheatsheets/nxc.md) · [`../vault/indices/Puertos.md`](../vault/indices/Puertos.md) · [`../vault/indices/Servicios.md`](../vault/indices/Servicios.md) · [`../examen/00-dashboard.md`](../examen/00-dashboard.md) |
| **Alcance** | `pendiente-politica` |

### 2 — Objetivo web

| Campo | Contenido |
| --- | --- |
| **Entrada** | Encontraste un sitio, un panel, una API o un vhost nuevo. Todavía no sabés la vulnerabilidad. |
| **Primeras acciones** | 1. Fijate qué **producto y versión** responde. 2. Revisá código fuente y archivos de configuración expuestos. 3. Fuzzeá directorios y archivos con la wordlist del cheatsheet. 4. Probá credenciales por defecto y reutilización de credenciales del resto del examen. 5. Buscá el CVE del producto **antes** de improvisar. |
| **Puntos de decisión** | ¿Panel con login? → reutilización de credenciales y spray. ¿App conocida con versión? → CVE/exploit público. ¿Parámetro reflejado o file path? → LFI/inyección. ¿Upload? → revisá las reglas de ejecución del directorio destino. |
| **Evidencia** | URL completa, `Host:`, versión detectada, salida de la enumeración web, captura de la vulnerabilidad y el request exacto que la disparó. |
| **Parqueo** | Parqueás cuando ya probaste el checklist completo del cheatsheet web y ninguno de los vectores tiene condición de ejecución alcanzable. Sacá captura del checklist y volvé por el [escenario 1](#1--puertos-abiertos-triage). |
| **Enlaces** | [`09-web.md`](09-web.md) · [`../playbooks/http-web.md`](../playbooks/http-web.md) · [`../playbooks/mssql.md`](../playbooks/mssql.md) · [`../cheatsheets/web.md`](../cheatsheets/web.md) · [`../cheatsheets/lfi-rce.md`](../cheatsheets/lfi-rce.md) · [`../cheatsheets/mssql-injection.md`](../cheatsheets/mssql-injection.md) · [`02-enumeracion-servicios.md`](02-enumeracion-servicios.md) |
| **Alcance** | `pendiente-politica` |

### 3 — Shell Linux + escalada

| Campo | Contenido |
| --- | --- |
| **Entrada** | Tenés ejecución como usuario común en Linux. No sos root. |
| **Primeras acciones** | 1. Estabilizá la TTY antes de cualquier otra cosa. 2. Corré la enumeración automatizada y guardá el output. 3. Recorré el orden de ataque de `LPE-Linux`: `sudo` → SUID/SGID → capabilities → credenciales en archivos → servicios root escribibles → cron → grupos → NFS. 4. Revisá grupos y membresías antes de mirar exploits de kernel. |
| **Puntos de decisión** | ¿El binario permitido tiene código distinto por `sudo`, `suid` o `capabilities`? → leé el **contexto**, no copies a ciegas. ¿Root ejecuta algo que podés escribir? → ese es el camino. ¿Nada de lo anterior aplica? → recién ahí kernel/CVE, y sabiendo que puede tumbar la máquina. |
| **Evidencia** | `id`, `sudo -l`, lista SUID/SGID, `getcap -r /`, el vector elegido con su output, `whoami` final y `local.txt`/`proof.txt` con la IP en el mismo cuadro. |
| **Parqueo** | Parqueás cuando el orden de ataque completo de `LPE-Linux` está recorrido y documentado sin hallazgo. Dejá escrito qué probaste: sirve para el reporte y para no repetir. |
| **Enlaces** | [`lpe/LPE-Linux.md`](lpe/LPE-Linux.md) · [`03-privesc-linux.md`](03-privesc-linux.md) · [`../playbooks/nfs.md`](../playbooks/nfs.md) · [`08-reporte-y-evidencia.md`](08-reporte-y-evidencia.md) · [`../examen/suelta-1.md`](../examen/suelta-1.md) |
| **Alcance** | `pendiente-politica` |

> **Nota de referencias**: el espejo local por binario de GTFOBins **no existe** en este vault.
> Usá el índice [`../vault/indices/Referencias/GTFOBins.md`](../vault/indices/Referencias/GTFOBins.md)
> (lista de binarios y funciones) más las alternativas online documentadas en
> [`03-privesc-linux.md`](03-privesc-linux.md). Ver [`SALUD-DOCUMENTAL`](../_sistema/SALUD-DOCUMENTAL.md).

### 4 — Shell Windows + escalada

| Campo | Contenido |
| --- | --- |
| **Entrada** | Tenés ejecución como usuario común en Windows. No sos Administrator/SYSTEM. |
| **Primeras acciones** | 1. Identificá versión, arquitectura y parches. 2. Listá **privilegios** y **grupos** del usuario: `whoami /priv` y `whoami /groups` deciden la mitad de los caminos. 3. Enumerá servicios, tareas programadas y permisos de escritura. 4. Elegí la familia Potato correcta según la versión, no la primera que recuerdes. |
| **Puntos de decisión** | ¿Tenés `SeImpersonate`/`SeAssignPrimaryToken`? → familia Potato y su matriz de compatibilidad. ¿Servicio con ruta sin comillas o binario escribible? → servicio. ¿Grupo privilegiado (Backup/Server/Account/Print Operators, DnsAdmins)? → la ruta cambia por completo. |
| **Evidencia** | `whoami /all`, lista de privilegios, enumeración local completa, el vector elegido con output y `local.txt`/`proof.txt` con la IP en el mismo cuadro. |
| **Parqueo** | Parqueás cuando la checklist de escalada Windows está recorrida y anotada, incluso sin hallazgo. El reporte necesita ver el recorrido, no solo el éxito. |
| **Enlaces** | [`lpe/LPE-Windows.md`](lpe/LPE-Windows.md) · [`04-privesc-windows.md`](04-privesc-windows.md) · [`../playbooks/windows-privesc.md`](../playbooks/windows-privesc.md) · [`../cheatsheets/potatoes.md`](../cheatsheets/potatoes.md) · [`08-reporte-y-evidencia.md`](08-reporte-y-evidencia.md) |
| **Alcance** | `pendiente-politica` |

### 5 — AD con credenciales

| Campo | Contenido |
| --- | --- |
| **Entrada** | El set de AD arranca en modo *assumed breach*: te dieron usuario y contraseña. Completá el triage de las tres máquinas primero. |
| **Primeras acciones** | 1. Confirmá reloj sincronizado, DNS y `/etc/hosts` **antes** de tocar Kerberos. 2. Enumerá el dominio con las credenciales dadas (usuarios, grupos, sesiones, ACLs, shares). 3. Identificá el camino más corto al Domain Admin y anotalo. 4. Guardá cada credencial nueva en el doc global de credenciales. |
| **Puntos de decisión** | ¿Hay camino de ACL/delegación? → `05-active-directory.md`. ¿Hay plantillas de certificado o una CA? → [`../playbooks/certipy-y-adcs.md`](../playbooks/certipy-y-adcs.md). ¿Hay coerción/relay disponible? → cheatsheet de coerción (la coerción está documentada como prohibida y esa etiqueta **no** está verificada). ¿Ya sos DA? → cerrá evidencia y pasá al siguiente set. |
| **Evidencia** | Credenciales usadas y obtenidas, salida de cada enumeración, tickets/ccache generados, captura de cada máquina comprometida y `local.txt`/`proof.txt` con IP. |
| **Parqueo** | Parqueás cuando el camino al DA elegido está bloqueado y **existe un segundo camino documentado sin explorar**. Los puntos de AD son parciales: cobrá las máquinas que ya cerraste antes de insistir. |
| **Enlaces** | [`../playbooks/ad-desde-credenciales.md`](../playbooks/ad-desde-credenciales.md) · [`../playbooks/certipy-y-adcs.md`](../playbooks/certipy-y-adcs.md) · [`../playbooks/winrm.md`](../playbooks/winrm.md) · [`05-active-directory.md`](05-active-directory.md) · [`walkthroughs/AD-walkthrough.md`](walkthroughs/AD-walkthrough.md) · [`../cheatsheets/nxc.md`](../cheatsheets/nxc.md) · [`../cheatsheets/certipy.md`](../cheatsheets/certipy.md) · [`../cheatsheets/adcs-esc.md`](../cheatsheets/adcs-esc.md) · [`../cheatsheets/ad-avanzado.md`](../cheatsheets/ad-avanzado.md) · [`../cheatsheets/rpc-coercion.md`](../cheatsheets/rpc-coercion.md) · [`../examen/ad-credenciales.md`](../examen/ad-credenciales.md) · [`../examen/ad-dc.md`](../examen/ad-dc.md) |
| **Alcance** | `pendiente-politica` |

### 6 — Hashes, TGT y PFX

| Campo | Contenido |
| --- | --- |
| **Entrada** | Tenés material de credencial reutilizable: hash NTLM, ticket/ccache, certificado PFX/PEM, o credencial en texto claro de otra máquina. |
| **Primeras acciones** | 1. Registrá el material con su origen y en qué hosts ya se probó (`../examen/00-dashboard.md`). 2. Elegí el uso según el **tipo**: hash → pass-the-hash; TGT/ccache → pass-the-ticket; PFX/PEM → autenticación por certificado; texto claro → login normal + spray controlado. 3. Probá **primero** en los hosts donde la credencial ya se usó. 4. Si el material es crackeable y hay tiempo, guardá una copia y seguí con el uso directo. |
| **Puntos de decisión** | ¿El servicio acepta el material directamente (SMB/LDAP/WinRM/RDP)? → usalo, no lo crackees. ¿Falla en todos los hosts? → probablemente no tiene permisos: verificá en el doc global antes de descartar. |
| **Evidencia** | Tipo de material, archivo o valor, origen, hosts probados, resultado por host y captura del acceso obtenido. |
| **Parqueo** | Parqueás cuando el material está registrado y probado en cada host relevante. Un hash probado y fallido **igual** va al reporte como intento documentado. |
| **Enlaces** | [`../playbooks/credenciales-y-movimiento.md`](../playbooks/credenciales-y-movimiento.md) · [`../playbooks/kerberos-y-tickets.md`](../playbooks/kerberos-y-tickets.md) · [`../playbooks/winrm.md`](../playbooks/winrm.md) · [`../cheatsheets/impacket.md`](../cheatsheets/impacket.md) · [`../cheatsheets/nxc.md`](../cheatsheets/nxc.md) · [`05-active-directory.md`](05-active-directory.md) · [`../vault/indices/Referencias/WADComs.md`](../vault/indices/Referencias/WADComs.md) · [`../examen/00-dashboard.md`](../examen/00-dashboard.md) |
| **Alcance** | `pendiente-politica` |

> El índice de WADComs lista recetas, pero **parte de sus notas individuales está en blanco**
> en la capa generada (ver [`SALUD-DOCUMENTAL`](../_sistema/SALUD-DOCUMENTAL.md)). Si un enlace
> del índice abre una nota vacía, no es un problema tuyo: usá los cheatsheets de Impacket y de
> NetExec y seguí.

### 7 — Pivoting

| Campo | Contenido |
| --- | --- |
| **Entrada** | Desde un host comprometido ves interfaces/segmentos que tu Kali no alcanza. |
| **Primeras acciones** | 1. Confirmá tu propia IP y la red interna visible desde el host. 2. Verificá conectividad **saliente** del host hacia tu Kali (es la que decide entre túnel reverso, agente o proxy). 3. Elegí la técnica según la conectividad observada, no al revés. 4. Volvé a correr el triage del [escenario 1](#1--puertos-abiertos-triage) contra la red nueva. |
| **Puntos de decisión** | ¿El host alcanza tu Kali? → túnel/agente. ¿Solo tienes forward de puerto puntual? → port-forward. ¿Hay DNS interno? → resolvé nombres antes de enumerar. ¿Servicios ya vistos en la red nueva? → el precedente del índice aplica. |
| **Evidencia** | Comando de descubrimiento de red, comando del túnel, salida que **prueba** alcanzar la red nueva, y todo lo enumerado detrás del pivot. |
| **Parqueo** | Parqueás cuando la red nueva tiene su propio mapa de puertos y por lo menos una hipótesis por servicio. Perder el túnel sin dejar documentado el comando es perder el pivote. |
| **Enlaces** | [`07-pivoting.md`](07-pivoting.md) · [`06-payloads-shells-transferencia.md`](06-payloads-shells-transferencia.md) · [`../vault/indices/Puertos.md`](../vault/indices/Puertos.md) |
| **Alcance** | `pendiente-politica` |

### 8 — Transferencia y payloads

| Campo | Contenido |
| --- | --- |
| **Entrada** | Necesitás llevar una herramienta o payload al objetivo, o traerte loot. |
| **Primeras acciones** | 1. Verificá qué intérpretes y binarios existen en el objetivo. 2. Elegí el canal (HTTP, SMB, FTP, `nc`, codificado en un one-liner) según lo que el objetivo permite. 3. Prepará el payload para el **sistema y arquitectura** reales. 4. Dejá el servidor de transferencia corriendo y anotá la ruta exacta que sirve. |
| **Puntos de decisión** | ¿Hay salida HTTP saliente? → sirve desde tu máquina. ¿Solo entrada? → usá el canal del propio exploit. ¿Windows con AV? → revisá las alternativas del cheatsheet antes de re-subir el mismo binario. |
| **Evidencia** | Payload usado, hash del archivo, comando de descarga ejecutado, ruta donde quedó y prueba de que se ejecutó. |
| **Parqueo** | Parqueás cuando existe **una** vía de transferencia probada, documentada y repetible. |
| **Enlaces** | [`06-payloads-shells-transferencia.md`](06-payloads-shells-transferencia.md) · [`07-pivoting.md`](07-pivoting.md) · [`../cheatsheets/impacket.md`](../cheatsheets/impacket.md) |
| **Alcance** | `pendiente-politica` |

### 9 — Kerberos y entorno

| Campo | Contenido |
| --- | --- |
| **Entrada** | Kerberos devuelve errores raros y no sabés si es credenciales, reloj, DNS o nombre de dominio. |
| **Primeras acciones** | 1. Descartá el **reloj** primero: es la causa más frecuente y la más barata de arreglar. 2. Verificá DNS y la resolución del nombre del dominio. 3. Usá el FQDN del dominio, no la IP, en los comandos Kerberos. 4. Revisá `krb5.conf` y la variable de realm. |
| **Puntos de decisión** | ¿`KRB_AP_ERR_SKEW` o similar? → reloj. ¿No resuelve el nombre? → DNS/`/etc/hosts`. ¿Funciona con IP pero no con FQDN? → Kerberos no está usando el realm correcto. |
| **Evidencia** | Mensaje de error literal, reloj local vs. del DC, contenido de `krb5.conf` y el comando exacto que falló. |
| **Parqueo** | Parqueás cuando el error está identificado como entorno (no como credencial inválida) y anotado. Un error de reloj documentado te ahorra repetirlo en otra máquina. |
| **Enlaces** | [`../playbooks/kerberos-y-tickets.md`](../playbooks/kerberos-y-tickets.md) · [`Entorno.md`](Entorno.md) · [`05-active-directory.md`](05-active-directory.md) · [`verificado-2026.md`](verificado-2026.md) |
| **Alcance** | `pendiente-politica` |

### 10 — Reporte y evidencia

| Campo | Contenido |
| --- | --- |
| **Entrada** | Conseguiste acceso, o root/SYSTEM, o una flag. Hay que capturarlo bien **ahora**, no al final. |
| **Primeras acciones** | 1. Confirmá identidad y host (`id`/`whoami`, IP) en el mismo cuadro que la flag. 2. Guardá la evidencia en la carpeta de esa máquina. 3. Registrá el comando exacto y su output. 4. Enviá la flag en el panel oficial en cuanto la tengas. |
| **Puntos de decisión** | ¿La captura muestra la flag **y** la IP de la víctima? → sirve. ¿Venís de una webshell? → no sirve, necesitás shell interactiva. ¿Cerrás la máquina? → antes, dejá el doc de la máquina actualizado con pasos y credenciales. |
| **Evidencia** | Captura de flag + IP, comando y output del paso clave, credenciales obtenidas, timeline de la máquina y hash de los archivos de evidencia. |
| **Parqueo** | Nunca parqueás el reporte: es continuo. Parqueás **la máquina** cuando el doc está actualizado y la flag enviada. |
| **Enlaces** | [`08-reporte-y-evidencia.md`](08-reporte-y-evidencia.md) · [`../examen/00-dashboard.md`](../examen/00-dashboard.md) · [`../plantillas/como-usar-plantillas.md`](../plantillas/como-usar-plantillas.md) · [`../plantillas/tarjeta-tecnica.md`](../plantillas/tarjeta-tecnica.md) |
| **Alcance** | `pendiente-politica` |

### 11 — Estoy trabado

| Campo | Contenido |
| --- | --- |
| **Entrada** | Un escenario no avanza y ya invertiste tiempo considerable en el mismo punto. |
| **Primeras acciones** | 1. Escribí en el doc de la máquina **qué probaste y qué resultado dio**. 2. Volvé a la tabla de ruteo y elegí la observación que todavía no atacaste. 3. Cambiá de máquina. 4. Dejá el estado listo para retomar: credenciales, pendientes y la hipótesis abierta. |
| **Puntos de decisión** | ¿El bloqueo es de **enumeración** (no probaste algo) o de **habilidad** (ningún camino conocido aplica)? Enumeración → volvé al escenario correspondiente. Habilidad → parqueá y movete a otra máquina. |
| **Evidencia** | Qué probaste, qué output obtuviste, qué descartaste y por qué. Esto es lo que después justifica el intento en el reporte. |
| **Parqueo** | Parqueo obligatorio al cruzar tu límite de tiempo en el mismo punto. Parquear una máquina no es perder puntos: los puntos de AD se otorgan parcialmente, y las sueltas siguen ahí. |
| **Enlaces** | [`01-metodologia.md`](01-metodologia.md) · [`../examen/00-dashboard.md`](../examen/00-dashboard.md) · [`../plantillas/tarjeta-tecnica.md`](../plantillas/tarjeta-tecnica.md) · [`00-inicio.md`](00-inicio.md) |
| **Alcance** | `pendiente-politica` |

---

## Playbooks de decisión (rebanada AD)

Los playbooks desarrollan el **cómo decidir** de los escenarios de AD con más detalle que la
ficha de una línea. No reemplazan al router: lo profundizan.

| Playbook | Cuándo abrirlo | Escenario |
| --- | --- | --- |
| [`../playbooks/ad-desde-credenciales.md`](../playbooks/ad-desde-credenciales.md) | El set de AD te dio usuario y contraseña | [5](#5--ad-con-credenciales) |
| [`../playbooks/kerberos-y-tickets.md`](../playbooks/kerberos-y-tickets.md) | Aparece un hash o un tique Kerberos, o Kerberos falla | [6](#6--hashes-tgt-y-pfx) · [9](#9--kerberos-y-entorno) |
| [`../playbooks/certipy-y-adcs.md`](../playbooks/certipy-y-adcs.md) | Aparece una CA, una plantilla, un certificado o un `.pfx` | [5](#5--ad-con-credenciales) |
| [`../playbooks/credenciales-y-movimiento.md`](../playbooks/credenciales-y-movimiento.md) | Hay material de credencial y decidís el movimiento | [6](#6--hashes-tgt-y-pfx) |

---

## Playbooks de decisión (rebanada de servicios)

Los playbooks de servicio desarrollan el **cómo decidir** del triage y del objetivo web. No
reemplazan al router: lo profundizan.

| Playbook | Cuándo abrirlo | Escenario |
| --- | --- | --- |
| [`../playbooks/http-web.md`](../playbooks/http-web.md) | Hay superficie HTTP: vhosts, contenido, login o input | [2](#2--objetivo-web) |
| [`../playbooks/smb.md`](../playbooks/smb.md) | SMB responde: sesión anónima, shares o credenciales | [1](#1--puertos-abiertos-triage) |
| [`../playbooks/ldap.md`](../playbooks/ldap.md) | LDAP/LDAPS responde: enumeración del dominio | [1](#1--puertos-abiertos-triage) · [5](#5--ad-con-credenciales) |
| [`../playbooks/nfs.md`](../playbooks/nfs.md) | NFS responde: export, montaje o permisos del share | [1](#1--puertos-abiertos-triage) · [3](#3--shell-linux--escalada) |
| [`../playbooks/mssql.md`](../playbooks/mssql.md) | MSSQL responde: autenticación, rol o ejecución | [1](#1--puertos-abiertos-triage) · [2](#2--objetivo-web) |
| [`../playbooks/winrm.md`](../playbooks/winrm.md) | WinRM responde o valida una credencial | [1](#1--puertos-abiertos-triage) · [5](#5--ad-con-credenciales) · [6](#6--hashes-tgt-y-pfx) |

---

## Plantillas reutilizables

Cuando el escenario es nuevo (un servicio raro, una técnica que no está en el playbook), no
inventes formato: usá las tarjetas.

| Plantilla | Cuándo |
| --- | --- |
| [`../plantillas/como-usar-plantillas.md`](../plantillas/como-usar-plantillas.md) | El contrato de la tarjeta y su etiqueta de alcance. |
| [`../plantillas/tarjeta-servicio.md`](../plantillas/tarjeta-servicio.md) | Un servicio o puerto que estás enumerando. |
| [`../plantillas/tarjeta-tecnica.md`](../plantillas/tarjeta-tecnica.md) | Una técnica o vector de escalada. |

Las tarjetas **no tienen comandos**: son estructura. El comando va en el doc del examen y, si es
reutilizable, termina en la guía o el cheatsheet canónico.

---

## Rutas canónicas — estado, no promesa

Esta sección es la fuente única para **dónde vive cada cosa**. Está marcada explícitamente
porque las rutas **todavía no están conciliadas** entre la documentación y el instalador.

| Qué | Ruta que promete la documentación | Ruta que crea `OSCP-setup` | Estado |
| --- | --- | --- | --- |
| El vault | `~/OSCP` | `${HOME}/Documentos/OSCP` (`VAULT`) | **Divergente.** `~/OSCP` y `~/Documentos/OSCP` no son la misma ruta. |
| Arsenal / toolkits | `~/examen/tools/{linux,win}` | `${HOME}/Documentos/Tools/{linux,win,kali,repos}` | **Divergente.** Nombre y ubicación distintos. |
| Evidencia del examen | `~/examen/evidencia/<maquina>/` | No lo crea el instalador | **Sin origen.** Hay que crearlo a mano. |
| Entradas del generador | `_sistema/datos/` | No existe en el repo | **Ausente.** Ver [`SALUD-DOCUMENTAL`](../_sistema/SALUD-DOCUMENTAL.md). |
| Chequeo de entorno | `~/OSCP/_sistema/herramientas/verificar-entorno.sh` | `OSCP-setup/verify.sh` | **Divergente.** Dos verificadores, dos rutas. |

> **Esto es un estado observado, no un arreglo.** Ninguna de estas divergencias está resuelta:
> el router no afirma que el instalador y la documentación coincidan. La conciliación de rutas
> es trabajo pendiente y afecta también a `verificar-2026` y a los comandos de los cheatsheets
> que escriben en `~/examen/…`.
>
> Mientras siga así: **verificá la ruta real antes de copiar un comando** que dependa de
> `~/OSCP`, `~/examen/tools` o `~/examen/evidencia`. La evidencia de esta observación está en
> [`SALUD-DOCUMENTAL`](../_sistema/SALUD-DOCUMENTAL.md).

---

## Lo que este router NO hace

- **No es política del examen.** No clasifica restricciones ni cita la guía oficial. Eso vive en
  [`00-reglas-examen.md`](00-reglas-examen.md), y su fuente no se pudo recuperar (HTTP 403).
- **No reemplaza las guías.** No contiene comandos de ataque: delega en las guías y cheatsheets.
- **No arregla la capa generada.** Los índices de `../vault/indices/` se conservan tal como
  están; no se regeneran mientras falten sus datos de origen.
- **No valida la salud del vault generado.** Para eso está
  [`../_sistema/herramientas/verificar-enlaces.py`](../_sistema/herramientas/verificar-enlaces.py),
  que comprueba la estructura y los enlaces de las rebanadas `first-slice` y `ad-slice`
  (`--scope`), y **no** la salud de la capa generada.

---

## Alcance

`pendiente-politica` — todo el documento. La evidencia de por qué, y qué haría falta para
subirlo a `verificado-examen`, está en
[`SALUD-DOCUMENTAL`](../_sistema/SALUD-DOCUMENTAL.md).
