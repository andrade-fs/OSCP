# Cómo usar las plantillas

Dos plantillas: una para **servicios** y una para **técnicas**. Sirven para registrar algo
nuevo durante el examen sin inventar formato, y para que la nota sea legible después cuando
escribas el reporte.

- Router del examen: [`../guia/router-escenarios.md`](../guia/router-escenarios.md).
- Plantilla de servicio: [`tarjeta-servicio.md`](tarjeta-servicio.md).
- Plantilla de técnica: [`tarjeta-tecnica.md`](tarjeta-tecnica.md).

---

## Reglas de la tarjeta

1. **Una observación, una tarjeta.** Si aparecen dos servicios o dos vectores, son dos tarjetas.
2. **Sin comandos.** La tarjeta describe decisiones, evidencia y parqueo. El comando va en el
   documento del examen y, si es reutilizable, en la guía o cheatsheet canónico.
3. **Placeholders siempre visibles.** Lo que no completaste queda como `<PLACEHOLDER>`: así se
   ve de un vistazo qué falta, en vez de parecer información real.
4. **Los siete encabezados son obligatorios** y van con el texto exacto del contrato. Sin ellos
   la tarjeta no es válida.
5. **Una sola etiqueta de alcance.** Exactamente una, declarada como `Etiqueta: <valor>`.

---

## Contrato de la tarjeta

| Encabezado | Responde | Regla de calidad |
| --- | --- | --- |
| `## Entrada` | ¿Cuándo abro esta tarjeta? | Una observación concreta y verificable. |
| `## Primeras acciones` | ¿Qué hago en los primeros minutos? | Lista corta y ordenada; sin comandos. |
| `## Puntos de decisión` | ¿Qué bifurca el camino? | Cada punto tiene condición y destino. |
| `## Evidencia` | ¿Qué capturo antes de seguir? | Nombra el artefacto, no "sacar captura". |
| `## Parqueo` | ¿Cuándo la dejo y me muevo? | Condición explícita de parqueo. |
| `## Enlaces` | ¿Dónde está el detalle? | Solo rutas que existen. |
| `## Alcance` | ¿Qué etiqueta le corresponde? | Exactamente una de las cuatro. |

### Etiquetas admitidas

| Etiqueta | Cuándo usarla |
| --- | --- |
| `verificado-examen` | Solo si hay una fuente con URL **y** estado de recuperación observado, registrados localmente. |
| `solo-laboratorio` | Válido para practicar, no para el examen. |
| `prohibido` | La regla vigente lo excluye. |
| `pendiente-politica` | Sin fuente accesible que permita clasificar. |

> **Mientras la *OSCP+ Exam Guide* no se pueda recuperar (HTTP 403), toda tarjeta nueva va con
> `pendiente-politica`.** Motivo y estado: [`../_sistema/SALUD-DOCUMENTAL.md`](../_sistema/SALUD-DOCUMENTAL.md).

---

## Ejemplo mínimo (sin comandos)

```text
## Entrada
Enumeré <SERVICIO> en <PUERTO> y todavía no decidí si vale la pena seguir.

## Primeras acciones
1. Confirmar producto y versión reales, no la etiqueta del escáner.
2. Revisar el cheatsheet del servicio y tildar cada vector probado.
3. Anotar la hipótesis antes de explotarla.

## Puntos de decisión
- ¿Producto y versión identificados? Sí → buscar precedente. No → volver a enumerar.
- ¿Ya probé todos los vectores del cheatsheet? Sí → parquear. No → seguir.

## Evidencia
Banner, versión, salida de enumeración, ruta exacta y hash del archivo de evidencia.

## Parqueo
Cheatsheet completo tildado y anotado, sin vector con condición alcanzable.

## Enlaces
- <RUTA_REAL_AL_CHEATSHEET>

## Alcance
Etiqueta: pendiente-politica
```

---

## Flujo de trabajo

```text
Observación → elegir plantilla → completar los 7 encabezados
            → registrar evidencia → decidir seguir o parquear
            → si el contenido es reutilizable, subirlo a guia/ o cheatsheets/
```

> La tarjeta del examen es **descartable**: el conocimiento reutilizable se promueve a una guía
> o un cheatsheet. Ver [`../guia/08-reporte-y-evidencia.md`](../guia/08-reporte-y-evidencia.md).

---

## Alcance

`pendiente-politica` — este documento describe formato de notas, no técnica de examen. La
restricción activa es que no hay fuente accesible que permita clasificar de otro modo.
