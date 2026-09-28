# Servicio: mc-nmf

[[00-inicio|Inicio]] · [[Entorno|Entorno]] · [[Puertos|Puertos]] · [[Servicios|Servicios]] · [[Tecnicas|Tecnicas]] · [[Maquinas|Maquinas]] · [[Referencias|Referencias]]

**2 máquina(s)** exponen `mc-nmf` · **1 en el listado OSCP**

Puertos donde aparece: [[9389]]

| Máquina | Puerto | Estado | Qué era realmente | OSCP |
|---|---|---|---|---|
| [[htb-phantom\|Phantom]] | [[9389]] | `open` | — | **sí** |
| [[htb-escapetwo\|EscapeTwo]] | [[9389]] | `open` | — | — |

## Cómo profundizar

```bash
python3 _sistema/herramientas/buscar.py 'mc-nmf' -v
```
