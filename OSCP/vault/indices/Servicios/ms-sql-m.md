# Servicio: ms-sql-m

[[00-inicio|Inicio]] · [[Entorno|Entorno]] · [[Puertos|Puertos]] · [[Servicios|Servicios]] · [[Tecnicas|Tecnicas]] · [[Maquinas|Maquinas]] · [[Referencias|Referencias]]

**5 máquina(s)** exponen `ms-sql-m` · **1 en el listado OSCP**

Puertos donde aparece: [[1434]]

| Máquina | Puerto | Estado | Qué era realmente | OSCP |
|---|---|---|---|---|
| [[htb-intelligence\|Intelligence]] | [[1434]] | `open|filtered` | — | **sí** |
| [[htb-antique\|Antique]] | [[1434]] | `closed` | — | — |
| [[htb-conceal\|Conceal]] | [[1434]] | `open|filtered` | — | — |
| [[htb-pit\|Pit]] | [[1434]] | `filtered` | — | — |
| [[htb-wifinetic\|Wifinetic]] | [[1434]] | `closed` | — | — |

## Cómo profundizar

```bash
python3 _sistema/herramientas/buscar.py 'ms-sql-m' -v
```
