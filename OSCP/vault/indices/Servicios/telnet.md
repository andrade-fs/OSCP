# Servicio: telnet

[[00-inicio|Inicio]] · [[Entorno|Entorno]] · [[Puertos|Puertos]] · [[Servicios|Servicios]] · [[Tecnicas|Tecnicas]] · [[Maquinas|Maquinas]] · [[Referencias|Referencias]]

**4 máquina(s)** exponen `telnet` · **1 en el listado OSCP**

Puertos donde aparece: [[23]]

| Máquina | Puerto | Estado | Qué era realmente | OSCP |
|---|---|---|---|---|
| [[htb-access\|Access]] | [[23]] | `open` | — | **sí** |
| [[htb-antique\|Antique]] | [[23]] | `open` | Telnet | — |
| [[htb-tentacle\|Tentacle]] | [[23]] | `closed` | — | — |
| [[htb-university\|University]] | [[23]] | `closed` | — | — |

## Cómo profundizar

```bash
python3 _sistema/herramientas/buscar.py 'telnet' -v
```
