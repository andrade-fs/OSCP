# Servicio: amqp

[[00-inicio|Inicio]] · [[Entorno|Entorno]] · [[Puertos|Puertos]] · [[Servicios|Servicios]] · [[Tecnicas|Tecnicas]] · [[Maquinas|Maquinas]] · [[Referencias|Referencias]]

**3 máquina(s)** exponen `amqp` · **1 en el listado OSCP**

Puertos donde aparece: [[5672]]

| Máquina | Puerto | Estado | Qué era realmente | OSCP |
|---|---|---|---|---|
| [[htb-broker\|Broker]] | [[5672]] | `open` | — | **sí** |
| [[htb-dyplesher\|Dyplesher]] | [[5672]] | `open` | — | — |
| [[htb-pikatwoo\|PikaTwoo]] | [[5672]] | `open` | — | — |

## Cómo profundizar

```bash
python3 _sistema/herramientas/buscar.py 'amqp' -v
```
