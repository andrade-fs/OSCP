# Servicio: redis

[[00-inicio|Inicio]] · [[Entorno|Entorno]] · [[Puertos|Puertos]] · [[Servicios|Servicios]] · [[Tecnicas|Tecnicas]] · [[Maquinas|Maquinas]] · [[Referencias|Referencias]]

**4 máquina(s)** exponen `redis`

Puertos donde aparece: [[6379]]

| Máquina | Puerto | Estado | Qué era realmente | OSCP |
|---|---|---|---|---|
| [[htb-atom\|Atom]] | [[6379]] | `open` | Redis | — |
| [[htb-cybermonday\|CyberMonday]] | [[6379]] | `open` | — | — |
| [[htb-pollution\|Pollution]] | [[6379]] | `open` | Redis | — |
| [[htb-postman\|Postman]] | [[6379]] | `open` | Redis | — |

## Cómo profundizar

```bash
python3 _sistema/herramientas/buscar.py 'redis' -v
```
