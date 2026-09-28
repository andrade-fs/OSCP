# Servicio: dhcps

[[00-inicio|Inicio]] · [[Entorno|Entorno]] · [[Puertos|Puertos]] · [[Servicios|Servicios]] · [[Tecnicas|Tecnicas]] · [[Maquinas|Maquinas]] · [[Referencias|Referencias]]

**5 máquina(s)** exponen `dhcps` · **1 en el listado OSCP**

Puertos donde aparece: [[67]]

| Máquina | Puerto | Estado | Qué era realmente | OSCP |
|---|---|---|---|---|
| [[htb-intelligence\|Intelligence]] | [[67]] | `open|filtered` | — | **sí** |
| [[htb-antique\|Antique]] | [[67]] | `closed` | — | — |
| [[htb-conceal\|Conceal]] | [[67]] | `open|filtered` | — | — |
| [[htb-pit\|Pit]] | [[67]] | `filtered` | — | — |
| [[htb-wifinetic\|Wifinetic]] | [[67]] | `open|filtered` | — | — |

## Cómo profundizar

```bash
python3 _sistema/herramientas/buscar.py 'dhcps' -v
```
