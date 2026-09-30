# Playbook — NFS (111/2049)

Camino de decisión para cuando **NFS responde** y todavía no sabés qué se exporta, con qué
permiso ni si el montaje habilita una escalada. Ordena el trabajo por **export → montaje →
permisos → archivos → pivote** y fija cuándo conviene parquear. El detalle de comandos y el
payload de escalada viven en las guías canónicas; acá solo se decide el orden.

- Formato de la tarjeta: [`../plantillas/como-usar-plantillas.md`](../plantillas/como-usar-plantillas.md).
- Enumeración del puerto: [`../guia/02-enumeracion-servicios.md`](../guia/02-enumeracion-servicios.md#111--nfs).
- Escalada por NFS: [`../guia/03-privesc-linux.md`](../guia/03-privesc-linux.md#8-nfs-con-no_root_squash).

---

## Entrada

Abrí esta tarjeta con **una** observación concreta:

- El puerto **111** o **2049** está abierto y todavía no listaste los *exports*.
- `showmount -e` o los scripts `nfs-*` de nmap devolvieron una lista de rutas exportadas.
- Tenés una shell en la víctima y querés decidir si el montaje sirve para escalar o solo para
  leer archivos.
- Todavía **no** sabés si el export es de solo lectura, si es escribible ni qué usuario recibís
  al escribir.

Si el puerto no es NFS, no es esta tarjeta: volvé al
[escenario 1](../guia/router-escenarios.md#1--puertos-abiertos-triage).

---

## Primeras acciones

1. **Listar los exports** antes de montar nada. Una lista vacía o filtrada cambia el objetivo.
2. **Montar cada export por separado** en un punto de montaje propio; no mezcles rutas.
3. **Leer los permisos del share ya montado** (`ls -la`): dueño, grupo y bits de escritura son la
   evidencia que decide el siguiente paso.
4. **Revisar el contenido como si fuera un share SMB**: configs, backups, claves SSH, scripts y
   credenciales. Un export de solo lectura igual vale por lo que hay adentro.
5. **Confirmar el comportamiento de `root`**: si el export permite escritura, verificá si el
   montaje conserva `root` (`no_root_squash`) o lo aplasta (`root_squash`) **antes** de intentar
   el SUID. La variante y su receta están en la guía, no las copies de memoria.
6. **Registrar el montaje y su resultado** aunque no encuentres nada: es evidencia del recorrido.

```bash
# Listar exports (guía 02-enumeracion-servicios.md, sección 111)
showmount -e <IP>
nmap -sCV -p111,2049 --script "nfs-showmount,nfs-ls,nfs-statfs" <IP>

# Montar y leer permisos
sudo mkdir -p /mnt/nfs
sudo mount -t nfs <IP>:/export/share /mnt/nfs -o nolock
ls -la /mnt/nfs
```

Detalle, payload y receta de escalada: [`../guia/03-privesc-linux.md#8-nfs-con-no_root_squash`](../guia/03-privesc-linux.md#8-nfs-con-no_root_squash)
y [`../guia/lpe/LPE-Linux.md#37-nfs-con-no_root_squash`](../guia/lpe/LPE-Linux.md#37-nfs-con-no_root_squash). No inventes flags.

---

## Puntos de decisión

Cada fila es una observación con su destino. No saltes de fila sin registrar la evidencia.

| Observación después de enumerar | Ruta | Documento |
| --- | --- | --- |
| Sin exports visibles | Probar el puerto por otro método y parquear si sigue vacío | [`../guia/02-enumeracion-servicios.md`](../guia/02-enumeracion-servicios.md#111--nfs) |
| Export visible pero el montaje falla | Confirmar protocolo/puerto y revisar el error literal | [`../guia/02-enumeracion-servicios.md`](../guia/02-enumeracion-servicios.md#111--nfs) |
| Export de **solo lectura** | Revisar contenido por credenciales y configuración | [`../guia/02-enumeracion-servicios.md`](../guia/02-enumeracion-servicios.md#111--nfs) |
| Export con **escritura** | Confirmar si conserva `root` y evaluar el SUID | [`../guia/03-privesc-linux.md`](../guia/03-privesc-linux.md#8-nfs-con-no_root_squash) |
| Escritura con `no_root_squash` | Escalada local con la receta canónica | [`../guia/lpe/LPE-Linux.md`](../guia/lpe/LPE-Linux.md#37-nfs-con-no_root_squash) |
| Secreto en el contenido montado | Registrar origen y probar reutilización de a un host | [`credenciales-y-movimiento.md`](credenciales-y-movimiento.md) |
| Sos usuario común en la víctima y el share es escribible | Ir al vector NFS del orden de escalada Linux | [`../guia/router-escenarios.md`](../guia/router-escenarios.md#3--shell-linux--escalada) |
| Sin export con permiso útil | Parquear y volver por enumeración | [escenario 1](../guia/router-escenarios.md#1--puertos-abiertos-triage) |

Dos reglas que ordenan el resto:

- **Montar es leer.** Aun sin escalada, un export montado es una fuente de credenciales.
- **La escritura no es la escalada.** Sin `root` conservado, escribir en el share no te da nada:
  confirmá el comportamiento antes de gastar tiempo en el payload.

---

## Evidencia

Capturá evidencia **en cada pivote**, no al final:

- Salida cruda de `showmount -e` y del script nmap, guardada a archivo con su ruta.
- Comando de montaje exacto, punto de montaje usado y el error literal si falló.
- Salida de `ls -la` del share montado, con dueño, grupo y permisos.
- Qué denota el export: solo lectura, escritura y si conserva `root` (`no_root_squash`).
- Archivos con secretos, su ruta exacta dentro del share y el origen de cada credencial.
- Captura de la escalada o del acceso obtenido con la **IP de la víctima** en el mismo cuadro
  ([`../guia/08-reporte-y-evidencia.md`](../guia/08-reporte-y-evidencia.md)).

---

## Parqueo

- **Regla de 45–90 minutos sin progreso verificable**: parqueá la ruta actual, escribí el estado
  y aplicá el [escenario 11](../guia/router-escenarios.md#11--estoy-trabado). Volvés después.
- Parqueás cuando los exports están listados, montados y revisados con su permiso anotado, y no
  queda share con permiso sin leer.
- Antes de parquear, dejá escrito: qué export montaste, con qué permiso, qué buscaste y si
  conservaba `root`.
- Si hay un export repetido en otra interfaz o un share equivalente accesible por otro servicio,
  no estás bloqueado: estás incompleto.

---

## Enlaces

- Router, escenario 1 (triage de puertos): [`../guia/router-escenarios.md#1--puertos-abiertos-triage`](../guia/router-escenarios.md#1--puertos-abiertos-triage)
- Router, escenario 3 (shell Linux + escalada): [`../guia/router-escenarios.md#3--shell-linux--escalada`](../guia/router-escenarios.md#3--shell-linux--escalada)
- Router, escenario 11 (estoy trabado): [`../guia/router-escenarios.md#11--estoy-trabado`](../guia/router-escenarios.md#11--estoy-trabado)
- Enumeración 111/2049: [`../guia/02-enumeracion-servicios.md#111--nfs`](../guia/02-enumeracion-servicios.md#111--nfs)
- Escalada por NFS: [`../guia/03-privesc-linux.md#8-nfs-con-no_root_squash`](../guia/03-privesc-linux.md#8-nfs-con-no_root_squash) · [`../guia/lpe/LPE-Linux.md#37-nfs-con-no_root_squash`](../guia/lpe/LPE-Linux.md#37-nfs-con-no_root_squash)
- Movimiento con credenciales halladas: [`credenciales-y-movimiento.md`](credenciales-y-movimiento.md)
- Otras tarjetas de servicios: [`http-web.md`](http-web.md) · [`smb.md`](smb.md) · [`ldap.md`](ldap.md)

---

## Alcance

Etiqueta: pendiente-politica

La etiqueta de alcance obligatoria es `pendiente-politica` porque no hay, registrada localmente,
una fuente con URL **y** estado de recuperación observado que permita clasificar el alcance de
estas técnicas. Motivo y estado: [`../_sistema/SALUD-DOCUMENTAL.md`](../_sistema/SALUD-DOCUMENTAL.md).
