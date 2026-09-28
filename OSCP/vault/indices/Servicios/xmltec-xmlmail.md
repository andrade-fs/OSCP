# Servicio: xmltec-xmlmail

[[00-inicio|Inicio]] · [[Entorno|Entorno]] · [[Puertos|Puertos]] · [[Servicios|Servicios]] · [[Tecnicas|Tecnicas]] · [[Maquinas|Maquinas]] · [[Referencias|Referencias]]

**2 máquina(s)** exponen `xmltec-xmlmail` · **1 en el listado OSCP**

Puertos donde aparece: [[9091]]

| Máquina | Puerto | Estado | Qué era realmente | OSCP |
|---|---|---|---|---|
| [[htb-soccer\|Soccer]] | [[9091]] | `open` | — | **sí** |
| [[htb-tentacle\|Tentacle]] | [[9091]] | `filtered` | — | — |

## Cómo profundizar

```bash
python3 _sistema/herramientas/buscar.py 'xmltec-xmlmail' -v
```
