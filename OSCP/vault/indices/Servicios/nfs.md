# Servicio: nfs

[[00-inicio|Inicio]] · [[Entorno|Entorno]] · [[Puertos|Puertos]] · [[Servicios|Servicios]] · [[Tecnicas|Tecnicas]] · [[Maquinas|Maquinas]] · [[Referencias|Referencias]]

**12 máquina(s)** exponen `nfs` · **1 en el listado OSCP**

Puertos donde aparece: [[2049]]

| Máquina | Puerto | Estado | Qué era realmente | OSCP |
|---|---|---|---|---|
| [[htb-puppy\|Puppy]] | [[2049]] | `open` | — | **sí** |
| [[htb-clicker\|Clicker]] | [[2049]] | `open` | — | — |
| [[htb-corporate\|Corporate]] | [[2049]] | `open` | — | — |
| [[htb-fortune\|Fortune]] | [[2049]] | `open` | nsf | — |
| [[htb-jail\|Jail]] | [[2049]] | `open` | NFS | — |
| [[htb-jobtwo\|JobTwo]] | [[2049]] | `open` | NFS | — |
| [[htb-mirage\|Mirage]] | [[2049]] | `open` | NSF | — |
| [[htb-remote\|Remote]] | [[2049]] | `open` | NSF | — |
| [[htb-scepter\|Scepter]] | [[2049]] | `open` | NFS | — |
| [[htb-slonik\|Slonik]] | [[2049]] | `open` | NFS | — |
| [[htb-squashed\|Squashed]] | [[2049]] | `open` | NFS | — |
| [[htb-vulncicada\|VulnCicada]] | [[2049]] | `open` | — | — |

## Cómo profundizar

```bash
python3 _sistema/herramientas/buscar.py 'nfs' -v
```
