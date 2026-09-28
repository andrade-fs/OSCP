# Servicio: https-alt

[[00-inicio|Inicio]] · [[Entorno|Entorno]] · [[Puertos|Puertos]] · [[Servicios|Servicios]] · [[Tecnicas|Tecnicas]] · [[Maquinas|Maquinas]] · [[Referencias|Referencias]]

**5 máquina(s)** exponen `https-alt` · **1 en el listado OSCP**

Puertos donde aparece: [[8443]]

| Máquina | Puerto | Estado | Qué era realmente | OSCP |
|---|---|---|---|---|
| [[htb-servmon\|ServMon]] | [[8443]] | `open` | Website | **sí** |
| [[htb-authority\|Authority]] | [[8443]] | `open` | PWM | — |
| [[htb-ghost\|Ghost]] | [[8443]] | `open` | HTTPS | — |
| [[htb-steamcloud\|SteamCloud]] | [[8443]] | `open` | Kubernetes API | — |
| [[htb-unobtainium\|Unobtainium]] | [[8443]] | `open` | HTTPS | — |

## Cómo profundizar

```bash
python3 _sistema/herramientas/buscar.py 'https-alt' -v
```
