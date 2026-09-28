# Servicio: tcpwrapped

[[00-inicio|Inicio]] · [[Entorno|Entorno]] · [[Puertos|Puertos]] · [[Servicios|Servicios]] · [[Tecnicas|Tecnicas]] · [[Maquinas|Maquinas]] · [[Referencias|Referencias]]

**2 máquina(s)** exponen `tcpwrapped` · **2 en el listado OSCP**

Puertos donde aparece: [[636]], [[3269]]

| Máquina | Puerto | Estado | Qué era realmente | OSCP |
|---|---|---|---|---|
| [[htb-phantom\|Phantom]] | [[636]] | `open` | — | **sí** |
| [[htb-phantom\|Phantom]] | [[3269]] | `open` | — | **sí** |

## Cómo profundizar

```bash
python3 _sistema/herramientas/buscar.py 'tcpwrapped' -v
```
