# Servicio: netbios-ns

[[00-inicio|Inicio]] · [[Entorno|Entorno]] · [[Puertos|Puertos]] · [[Servicios|Servicios]] · [[Tecnicas|Tecnicas]] · [[Maquinas|Maquinas]] · [[Referencias|Referencias]]

**9 máquina(s)** exponen `netbios-ns` · **3 en el listado OSCP**

Puertos donde aparece: [[137]]

| Máquina | Puerto | Estado | Qué era realmente | OSCP |
|---|---|---|---|---|
| [[htb-active\|Active]] | [[137]] | `open` | — | **sí** |
| [[htb-expressway\|Expressway]] | [[137]] | `closed` | — | **sí** |
| [[htb-intelligence\|Intelligence]] | [[137]] | `open|filtered` | — | **sí** |
| [[htb-antique\|Antique]] | [[137]] | `closed` | — | — |
| [[htb-conceal\|Conceal]] | [[137]] | `open|filtered` | — | — |
| [[htb-friendzone\|FriendZone]] | [[137]] | `open` | — | — |
| [[htb-legacy\|legacy]] | [[137]] | `open` | — | — |
| [[htb-pit\|Pit]] | [[137]] | `filtered` | — | — |
| [[htb-wifinetic\|Wifinetic]] | [[137]] | `closed` | — | — |

## Cómo profundizar

```bash
python3 _sistema/herramientas/buscar.py 'netbios-ns' -v
```
