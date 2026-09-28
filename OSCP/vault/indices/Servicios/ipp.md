# Servicio: ipp

[[00-inicio|Inicio]] · [[Entorno|Entorno]] · [[Puertos|Puertos]] · [[Servicios|Servicios]] · [[Tecnicas|Tecnicas]] · [[Maquinas|Maquinas]] · [[Referencias|Referencias]]

**6 máquina(s)** exponen `ipp` · **1 en el listado OSCP**

Puertos donde aparece: [[631]]

| Máquina | Puerto | Estado | Qué era realmente | OSCP |
|---|---|---|---|---|
| [[htb-intelligence\|Intelligence]] | [[631]] | `open|filtered` | — | **sí** |
| [[htb-antique\|Antique]] | [[631]] | `closed` | — | — |
| [[htb-conceal\|Conceal]] | [[631]] | `open|filtered` | — | — |
| [[htb-evilcups\|EvilCUPS]] | [[631]] | `open` | CUPS | — |
| [[htb-pit\|Pit]] | [[631]] | `filtered` | — | — |
| [[htb-wifinetic\|Wifinetic]] | [[631]] | `closed` | — | — |

## Cómo profundizar

```bash
python3 _sistema/herramientas/buscar.py 'ipp' -v
```
