# Servicio: netbios-dgm

[[00-inicio|Inicio]] · [[Entorno|Entorno]] · [[Puertos|Puertos]] · [[Servicios|Servicios]] · [[Tecnicas|Tecnicas]] · [[Maquinas|Maquinas]] · [[Referencias|Referencias]]

**5 máquina(s)** exponen `netbios-dgm` · **1 en el listado OSCP**

Puertos donde aparece: [[138]]

| Máquina | Puerto | Estado | Qué era realmente | OSCP |
|---|---|---|---|---|
| [[htb-intelligence\|Intelligence]] | [[138]] | `open|filtered` | — | **sí** |
| [[htb-antique\|Antique]] | [[138]] | `closed` | — | — |
| [[htb-conceal\|Conceal]] | [[138]] | `open|filtered` | — | — |
| [[htb-pit\|Pit]] | [[138]] | `filtered` | — | — |
| [[htb-wifinetic\|Wifinetic]] | [[138]] | `closed` | — | — |

## Cómo profundizar

```bash
python3 _sistema/herramientas/buscar.py 'netbios-dgm' -v
```
