# Playbook — Superficie HTTP/web

Camino de decisión para cuando aparece **HTTP o HTTPS** y todavía no sabés cuál es la
vulnerabilidad. Ordena el trabajo por **superficie** (vhosts, contenido, autenticación, input) y
fija cuándo conviene parquear. El detalle de comandos y payloads vive en las guías y cheatsheets
canónicas; acá solo se decide el orden.

- Formato de la tarjeta: [`../plantillas/como-usar-plantillas.md`](../plantillas/como-usar-plantillas.md).
- Guía web: [`../guia/09-web.md`](../guia/09-web.md).
- Enumeración del puerto: [`../guia/02-enumeracion-servicios.md`](../guia/02-enumeracion-servicios.md#80--https).

---

## Entrada

Abrí esta tarjeta con **una** observación concreta:

- `nmap` o `whatweb` muestran un servicio HTTP/HTTPS y todavía no identificaste el producto ni la
  versión exactos.
- Un **vhost** nuevo devuelve un sitio distinto del host por defecto.
- Encontraste una **superficie de entrada**: panel de login, API, formulario de subida o un
  parámetro que recibe una ruta de archivo o un comando.
- Todavía **no** sabés si el camino es contenido, autenticación, input o una app conocida.

Si el puerto responde pero no es web, no es esta tarjeta: volvé al
[escenario 1](../guia/router-escenarios.md#1--puertos-abiertos-triage) y elegí el servicio.

---

## Primeras acciones

1. **Identificar** producto, versión y headers reales antes de tocar nada. No confíes en la
   etiqueta del escáner.
2. **Descubrir en segundo plano**: directorios y vhosts mientras seguís leyendo la app. Un vhost
   nuevo puede ser una aplicación completamente distinta.
3. **Leer la app**: `robots.txt`, `sitemap.xml`, comentarios HTML, `.git/`, `/.env`, `/backup`,
   `/assets/`. Fijate también en el certificado SSL: a veces filtra el vhost.
4. **Clasificar la superficie**: ¿es contenido, autenticación, una entrada de input o una app
   conocida con versión? La clasificación define el vector, no la costumbre.
5. **Elegir un vector y probarlo de a uno**, registrando el resultado. Si la versión es exacta,
   buscá el precedente **antes** de improvisar.

```bash
# Identificar (guía 09-web.md §1)
whatweb -a 3 http://<IP>
curl -sI http://<IP>

# Descubrir en segundo plano
ffuf -u http://<IP>/FUZZ -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt \
     -mc 200,204,301,302,307,401,403 -t 50
ffuf -u http://<IP>/ -H "Host: FUZZ.<dominio>" \
     -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt \
     -mc 200,301,302,401,403 -fs <tamano_default>

# Precedente por versión exacta
searchsploit <app> <version>
```

Sintaxis y payloads completos: [`../cheatsheets/web.md`](../cheatsheets/web.md),
[`../cheatsheets/lfi-rce.md`](../cheatsheets/lfi-rce.md) y
[`../cheatsheets/mssql-injection.md`](../cheatsheets/mssql-injection.md). No inventes flags.

---

## Puntos de decisión

Cada fila es una observación con su destino. No saltes de fila sin registrar la evidencia.

| Observación en la superficie | Ruta | Documento |
| --- | --- | --- |
| Vhost nuevo responde distinto | Tratalo como app aparte: volvé al paso 1 con ese `Host:` | [`../guia/09-web.md`](../guia/09-web.md) §1 |
| Panel de login o área autenticada | Credenciales por defecto → reutilización de credenciales del set → spray controlado **solo** si la política lo permite | [`../guia/09-web.md`](../guia/09-web.md) §3 |
| App conocida con versión exacta | `searchsploit`/CVE y exploit público | [`../guia/09-web.md`](../guia/09-web.md) §4.8 |
| Parámetro `?file=`, `?page=`, `?path=` | LFI / directory traversal (lo más común) | [`../cheatsheets/lfi-rce.md`](../cheatsheets/lfi-rce.md) |
| Formulario de subida | Validación de extensión y reglas de ejecución del directorio destino | [`../cheatsheets/web.md`](../cheatsheets/web.md) §4 |
| Campo que llega al SO (`ping`, `host`…) | Command injection | [`../cheatsheets/web.md`](../cheatsheets/web.md) §5 |
| `'` produce error o login raro | SQLi **manual**; `sqlmap` sin clasificar (`pendiente-politica`) | [`../cheatsheets/mssql-injection.md`](../cheatsheets/mssql-injection.md) |
| Input que pide una URL | SSRF / puertos internos | [`../cheatsheets/web.md`](../cheatsheets/web.md) §7 |
| `/api/`, `/v1/`, JSON | Fuzz de rutas y parámetros de API | [`../guia/09-web.md`](../guia/09-web.md) §4.7 |
| RCE obtenido | Pasar de webshell a **reverse shell interactiva** | [`../guia/09-web.md`](../guia/09-web.md) §5 |
| Sin vector con condición alcanzable | Parquear y volver por enumeración | [escenario 1](../guia/router-escenarios.md#1--puertos-abiertos-triage) |

Dos reglas que ordenan el resto:

- **Leé antes de explotar.** El código fuente y los requests en Burp explican qué input importa.
- **Una webshell no es shell de trabajo.** Si tocás `local.txt`/`proof.txt` desde una webshell,
  esa máquina vale cero: conseguí shell interactiva primero.

---

## Evidencia

Capturá evidencia **en cada pivote**, no al final:

- URL completa y la cabecera `Host:` usada, más el nombre resuelto en `/etc/hosts`.
- Producto y versión detectados, con el comando y la salida cruda.
- Salida cruda del descubrimiento de directorios y vhosts, guardada a archivo con su ruta.
- El **request exacto** que disparó el hallazgo (Burp o `curl`) y su respuesta.
- Cada intento aunque falle: alimenta el reporte y evita repetir.
- Captura del acceso obtenido con la **IP de la víctima** en el mismo cuadro
  ([`../guia/08-reporte-y-evidencia.md`](../guia/08-reporte-y-evidencia.md)).

---

## Parqueo

- **Regla de 45–90 minutos sin progreso verificable**: parqueá la ruta actual, escribí el estado
  y aplicá el [escenario 11](../guia/router-escenarios.md#11--estoy-trabado). Volvés después.
- Parqueás cuando el checklist del cheatsheet web está recorrido y **ningún** vector tiene
  condición de ejecución alcanzable.
- Antes de parquear, dejá escrito: qué probé, qué falló, qué queda pendiente y qué credencial o
  ruta sigue viva.
- Si hay una segunda aplicación o un vhost sin revisar, no estás bloqueado: estás incompleto.

---

## Enlaces

- Router, escenario 2 (objetivo web): [`../guia/router-escenarios.md#2--objetivo-web`](../guia/router-escenarios.md#2--objetivo-web)
- Router, escenario 1 (triage de puertos): [`../guia/router-escenarios.md#1--puertos-abiertos-triage`](../guia/router-escenarios.md#1--puertos-abiertos-triage)
- Guía web: [`../guia/09-web.md`](../guia/09-web.md)
- Enumeración 80/443: [`../guia/02-enumeracion-servicios.md#80--https`](../guia/02-enumeracion-servicios.md#80--https)
- Chuletas: [`../cheatsheets/web.md`](../cheatsheets/web.md) · [`../cheatsheets/lfi-rce.md`](../cheatsheets/lfi-rce.md) · [`../cheatsheets/mssql-injection.md`](../cheatsheets/mssql-injection.md)
- Reporte y evidencia: [`../guia/08-reporte-y-evidencia.md`](../guia/08-reporte-y-evidencia.md)
- Otras tarjetas de servicios: [`smb.md`](smb.md) · [`ldap.md`](ldap.md)

---

## Alcance

Etiqueta: pendiente-politica

La etiqueta de alcance obligatoria es `pendiente-politica` porque no hay, registrada localmente,
una fuente con URL **y** estado de recuperación observado que permita clasificar el alcance de
estas técnicas. Motivo y estado: [`../_sistema/SALUD-DOCUMENTAL.md`](../_sistema/SALUD-DOCUMENTAL.md).
