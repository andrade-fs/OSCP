# Servicio: blackice-icecap

[[00-inicio|Inicio]] · [[Entorno|Entorno]] · [[Puertos|Puertos]] · [[Servicios|Servicios]] · [[Tecnicas|Tecnicas]] · [[Maquinas|Maquinas]] · [[Referencias|Referencias]]

**3 máquina(s)** exponen `blackice-icecap` · **1 en el listado OSCP**

Puertos donde aparece: [[8081]]

| Máquina | Puerto | Estado | Qué era realmente | OSCP |
|---|---|---|---|---|
| [[htb-build\|Build]] | [[8081]] | `filtered` | — | **sí** |
| [[htb-fortune\|Fortune]] | [[8081]] | `open` | pgadmin4 | — |
| [[htb-talkative\|Talkative]] | [[8081]] | `open` | HTTP | — |

## Cómo profundizar

```bash
python3 _sistema/herramientas/buscar.py 'blackice-icecap' -v
```
