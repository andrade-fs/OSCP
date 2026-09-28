# Servicio: mqtt

[[00-inicio|Inicio]] · [[Entorno|Entorno]] · [[Puertos|Puertos]] · [[Servicios|Servicios]] · [[Tecnicas|Tecnicas]] · [[Maquinas|Maquinas]] · [[Referencias|Referencias]]

**3 máquina(s)** exponen `mqtt` · **1 en el listado OSCP**

Puertos donde aparece: [[1883]]

| Máquina | Puerto | Estado | Qué era realmente | OSCP |
|---|---|---|---|---|
| [[htb-broker\|Broker]] | [[1883]] | `open` | — | **sí** |
| [[htb-ghostlink\|Ghostlink]] | [[1883]] | `open` | MQTT | — |
| [[htb-playertwo\|PlayerTwo]] | [[1883]] | `open` | — | — |

## Cómo profundizar

```bash
python3 _sistema/herramientas/buscar.py 'mqtt' -v
```
