# Servicio: cslistener

[[00-inicio|Inicio]] · [[Entorno|Entorno]] · [[Puertos|Puertos]] · [[Servicios|Servicios]] · [[Tecnicas|Tecnicas]] · [[Maquinas|Maquinas]] · [[Referencias|Referencias]]

**5 máquina(s)** exponen `cslistener`

Puertos donde aparece: [[9000]]

| Máquina | Puerto | Estado | Qué era realmente | OSCP |
|---|---|---|---|---|
| [[htb-barrier\|Barrier]] | [[9000]] | `open` | Authentik | — |
| [[htb-gobox\|Gobox]] | [[9000]] | `filtered` | — | — |
| [[htb-laser\|Laser]] | [[9000]] | `open` | Feed Engine | — |
| [[htb-obscurity\|Obscurity]] | [[9000]] | `closed` | — | — |
| [[htb-oz\|Oz]] | [[9000]] | `open` | — | — |

## Cómo profundizar

```bash
python3 _sistema/herramientas/buscar.py 'cslistener' -v
```
