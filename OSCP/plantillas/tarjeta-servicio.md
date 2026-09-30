# Tarjeta de servicio — `<SERVICIO>` / puerto `<PUERTO>`

Plantilla para un **servicio o puerto** que estás enumerando durante el examen.
Copiala al documento de la máquina (`../examen/<MAQUINA>.md`) y completá los placeholders.

> Contrato y reglas: [`como-usar-plantillas.md`](como-usar-plantillas.md).
> Esta tarjeta **no lleva comandos**: el detalle está en la guía del servicio y en el cheatsheet.

- Máquina: `<MAQUINA>`
- IP: `<IP>`
- Fecha/hora: `<YYYY-MM-DD HH:MM>`

---

## Entrada

*Observación concreta que abre esta tarjeta (una sola).*

- Puertos abiertos observados: `<PUERTOS>`
- Banner real (no la etiqueta del escáner): `<BANNER_REAL>`
- Por qué lo considero prioritario: `<MOTIVO>`

## Primeras acciones

1. Confirmar producto y versión **reales** del servicio.
2. Abrir el cheatsheet de `<SERVICIO>` y recorrer la checklist vector por vector.
3. Anotar la hipótesis antes de intentar explotarla.
4. Verificar `Host:` / nombre resuelto si el servicio responde a nombres.
5. Registrar cada intento aunque falle.

## Puntos de decisión

| Condición observada | Siguiente paso |
| --- | --- |
| Producto y versión identificados | `<DESTINO>` |
| Versión no identificada | Volver a enumerar `<QUE_FALTA>` |
| Vector del cheatsheet pendiente | Probarlo y registrar resultado |
| Todos los vectores probados sin resultado | Parquear |

## Evidencia

- Comando de enumeración y **output crudo**.
- Ruta y hash del archivo de evidencia: `<RUTA_EVIDENCIA>`
- Intento que funcionó, con el request/comando exacto.
- Captura de acceso obtenido, con la **IP de la víctima** en el mismo cuadro.

## Parqueo

*Condición explícita para dejar el servicio y moverte.*

- Cheatsheet de `<SERVICIO>` tildado por completo, con resultado anotado por vector.
- Escrito en `<MAQUINA>`: qué probé, qué falló y qué queda pendiente.
- Siguiente escenario elegido en `../guia/router-escenarios.md`.

## Enlaces

- Guía de enumeración del servicio: `<RUTA_GUIA_REAL>`
- Cheatsheet: `<RUTA_CHEATSHEET_REAL>`
- Router: [`../guia/router-escenarios.md`](../guia/router-escenarios.md)

## Alcance

Etiqueta: pendiente-politica

*Cambiala solo si existe una fuente con URL y estado de recuperación observado, registrados
localmente. Ver [`como-usar-plantillas.md`](como-usar-plantillas.md).*
