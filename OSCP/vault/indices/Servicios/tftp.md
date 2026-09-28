# Servicio: tftp

[[00-inicio|Inicio]] · [[Entorno|Entorno]] · [[Puertos|Puertos]] · [[Servicios|Servicios]] · [[Tecnicas|Tecnicas]] · [[Maquinas|Maquinas]] · [[Referencias|Referencias]]

**3 máquina(s)** exponen `tftp`

Puertos donde aparece: [[69]]

| Máquina | Puerto | Estado | Qué era realmente | OSCP |
|---|---|---|---|---|
| [[htb-conceal\|Conceal]] | [[69]] | `open|filtered` | — | — |
| [[htb-dropzone\|Dropzone]] | [[69]] | `open` | — | — |
| [[htb-joker\|Joker]] | [[69]] | `open|filtered` | — | — |

## Cómo profundizar

```bash
python3 _sistema/herramientas/buscar.py 'tftp' -v
```
