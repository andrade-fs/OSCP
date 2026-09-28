# Servicio: rsync

[[00-inicio|Inicio]] · [[Entorno|Entorno]] · [[Puertos|Puertos]] · [[Servicios|Servicios]] · [[Tecnicas|Tecnicas]] · [[Maquinas|Maquinas]] · [[Referencias|Referencias]]

**3 máquina(s)** exponen `rsync` · **1 en el listado OSCP**

Puertos donde aparece: [[873]]

| Máquina | Puerto | Estado | Qué era realmente | OSCP |
|---|---|---|---|---|
| [[htb-build\|Build]] | [[873]] | `open` | rsync | **sí** |
| [[htb-reddish\|Reddish]] | [[873]] | `open` | — | — |
| [[htb-unbalanced\|Unbalanced]] | [[873]] | `open` | RSync | — |

## Cómo profundizar

```bash
python3 _sistema/herramientas/buscar.py 'rsync' -v
```
