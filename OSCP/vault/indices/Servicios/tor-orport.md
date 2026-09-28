# Servicio: tor-orport

[[00-inicio|Inicio]] · [[Entorno|Entorno]] · [[Puertos|Puertos]] · [[Servicios|Servicios]] · [[Tecnicas|Tecnicas]] · [[Maquinas|Maquinas]] · [[Referencias|Referencias]]

**3 máquina(s)** exponen `tor-orport`

Puertos donde aparece: [[9001]]

| Máquina | Puerto | Estado | Qué era realmente | OSCP |
|---|---|---|---|---|
| [[htb-gobox\|Gobox]] | [[9001]] | `filtered` | — | — |
| [[htb-luanne\|Luanne]] | [[9001]] | `open` | Supervisor Process Manager | — |
| [[htb-quick\|Quick]] | [[9001]] | `open` | Website | — |

## Cómo profundizar

```bash
python3 _sistema/herramientas/buscar.py 'tor-orport' -v
```
