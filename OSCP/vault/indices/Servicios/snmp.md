# Servicio: snmp

[[00-inicio|Inicio]] · [[Entorno|Entorno]] · [[Puertos|Puertos]] · [[Servicios|Servicios]] · [[Tecnicas|Tecnicas]] · [[Maquinas|Maquinas]] · [[Referencias|Referencias]]

**13 máquina(s)** exponen `snmp` · **3 en el listado OSCP**

Puertos donde aparece: [[161]]

| Máquina | Puerto | Estado | Qué era realmente | OSCP |
|---|---|---|---|---|
| [[htb-intelligence\|Intelligence]] | [[161]] | `open|filtered` | — | **sí** |
| [[htb-monitored\|Monitored]] | [[161]] | `open` | — | **sí** |
| [[htb-pandora\|Pandora]] | [[161]] | `open` | — | **sí** |
| [[htb-airtouch\|AirTouch]] | [[161]] | `open` | — | — |
| [[htb-antique\|Antique]] | [[161]] | `open` | — | — |
| [[htb-carrier\|Carrier]] | [[161]] | `open` | — | — |
| [[htb-conceal\|Conceal]] | [[161]] | `open|filtered` | — | — |
| [[htb-intense\|Intense]] | [[161]] | `open` | — | — |
| [[htb-mentor\|Mentor]] | [[161]] | `open` | — | — |
| [[htb-mischief\|Mischief]] | [[161]] | `open` | — | — |
| [[htb-pit\|Pit]] | [[161]] | `open` | — | — |
| [[htb-underpass\|UnderPass]] | [[161]] | `open` | — | — |
| [[htb-wifinetic\|Wifinetic]] | [[161]] | `closed` | — | — |

## Cómo profundizar

```bash
python3 _sistema/herramientas/buscar.py 'snmp' -v
```
