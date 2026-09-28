# Servicio: ntp

[[00-inicio|Inicio]] · [[Entorno|Entorno]] · [[Puertos|Puertos]] · [[Servicios|Servicios]] · [[Tecnicas|Tecnicas]] · [[Maquinas|Maquinas]] · [[Referencias|Referencias]]

**11 máquina(s)** exponen `ntp` · **4 en el listado OSCP**

Puertos donde aparece: [[123]]

| Máquina | Puerto | Estado | Qué era realmente | OSCP |
|---|---|---|---|---|
| [[htb-active\|Active]] | [[123]] | `open` | — | **sí** |
| [[htb-forest\|Forest]] | [[123]] | `open` | — | **sí** |
| [[htb-intelligence\|Intelligence]] | [[123]] | `open` | — | **sí** |
| [[htb-monitored\|Monitored]] | [[123]] | `open` | — | **sí** |
| [[htb-antique\|Antique]] | [[123]] | `closed` | — | — |
| [[htb-cerberus\|Cerberus]] | [[123]] | `open` | — | — |
| [[htb-conceal\|Conceal]] | [[123]] | `open|filtered` | — | — |
| [[htb-pit\|Pit]] | [[123]] | `filtered` | — | — |
| [[htb-static\|Static]] | [[123]] | `open|filtered` | — | — |
| [[htb-tentacle\|Tentacle]] | [[123]] | `open` | — | — |
| [[htb-wifinetic\|Wifinetic]] | [[123]] | `closed` | — | — |

## Cómo profundizar

```bash
python3 _sistema/herramientas/buscar.py 'ntp' -v
```
