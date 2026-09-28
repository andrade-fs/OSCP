# Servicio: ncacn_http

[[00-inicio|Inicio]] · [[Entorno|Entorno]] · [[Puertos|Puertos]] · [[Servicios|Servicios]] · [[Tecnicas|Tecnicas]] · [[Maquinas|Maquinas]] · [[Referencias|Referencias]]

**2 máquina(s)** exponen `ncacn_http` · **1 en el listado OSCP**

Puertos donde aparece: [[593]]

| Máquina | Puerto | Estado | Qué era realmente | OSCP |
|---|---|---|---|---|
| [[htb-phantom\|Phantom]] | [[593]] | `open` | — | **sí** |
| [[htb-escapetwo\|EscapeTwo]] | [[593]] | `open` | — | — |

## Cómo profundizar

```bash
python3 _sistema/herramientas/buscar.py 'ncacn_http' -v
```
