# Tarjeta de técnica — `<TECNICA>`

Plantilla para una **técnica o vector de escalada** que estás evaluando durante el examen.
Copiala al documento de la máquina (`../examen/<MAQUINA>.md`) y completá los placeholders.

> Contrato y reglas: [`como-usar-plantillas.md`](como-usar-plantillas.md).
> Esta tarjeta **no lleva comandos**: el detalle está en la guía de escalada y en el cheatsheet.

- Máquina: `<MAQUINA>`
- Contexto (SO / usuario): `<SO>` / `<USUARIO>`
- Fecha/hora: `<YYYY-MM-DD HH:MM>`

---

## Entrada

*Qué observaste que hace aplicable esta técnica (una sola observación).*

- Hallazgo habilitante: `<HALLAZGO>`
- Prerrequisitos que ya confirmé: `<PRERREQUISITOS>`
- Prerrequisitos que **no** están confirmados: `<PENDIENTES>`

## Primeras acciones

1. Confirmar que el prerrequisito real está presente, no supuesto.
2. Identificar el **contexto** de ejecución (`sudo`, `suid`, `capabilities`, servicio, grupo).
3. Elegir la variante de la técnica que corresponde a ese contexto.
4. Registrar el intento con su output antes de pasar al siguiente vector.
5. Dejar el sistema estable: evitar variantes que puedan tumbar la máquina.

## Puntos de decisión

| Condición observada | Siguiente paso |
| --- | --- |
| Prerrequisito confirmado | Aplicar la variante de `<CONTEXTO>` |
| Prerrequisito ausente | Descartar y registrar por qué |
| Variante sin efecto | Revisar contexto y volver a elegir variante |
| Técnica con impacto destructivo | Parquear y evaluar coste/beneficio |

## Evidencia

- Hallazgo habilitante, con el comando y el output que lo prueban.
- Variante usada y su resultado (`éxito` / `sin efecto` / `falló`), con el mensaje literal.
- Prueba de privilegio obtenido (`id` / `whoami`) en el mismo cuadro que la flag.
- Ruta y hash del archivo de evidencia: `<RUTA_EVIDENCIA>`

## Parqueo

*Condición explícita para dejar la técnica y moverte.*

- Variantes del contexto `<CONTEXTO>` agotadas y anotadas.
- Escrito en `<MAQUINA>`: qué probé, qué falló, qué queda pendiente.
- Siguiente vector elegido en `../guia/lpe/LPE-Linux.md` o
  `../guia/lpe/LPE-Windows.md`, o cambio de máquina según
  `../guia/router-escenarios.md`.

## Enlaces

- Guía de la técnica: `<RUTA_GUIA_REAL>`
- Cheatsheet: `<RUTA_CHEATSHEET_REAL>`
- Router: [`../guia/router-escenarios.md`](../guia/router-escenarios.md)

## Alcance

Etiqueta: pendiente-politica

*Cambiala solo si existe una fuente con URL y estado de recuperación observado, registrados
localmente. Ver [`como-usar-plantillas.md`](como-usar-plantillas.md).*
