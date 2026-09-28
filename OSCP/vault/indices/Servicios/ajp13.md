# Servicio: ajp13

[[00-inicio|Inicio]] · [[Entorno|Entorno]] · [[Puertos|Puertos]] · [[Servicios|Servicios]] · [[Tecnicas|Tecnicas]] · [[Maquinas|Maquinas]] · [[Referencias|Referencias]]

**2 máquina(s)** exponen `ajp13`

Puertos donde aparece: [[8009]]

| Máquina | Puerto | Estado | Qué era realmente | OSCP |
|---|---|---|---|---|
| [[htb-kotarak\|Kotarak]] | [[8009]] | `open` | Tomcat AJP | — |
| [[htb-registrytwo\|RegistryTwo]] | [[8009]] | `open` | — | — |

## Cómo profundizar

```bash
python3 _sistema/herramientas/buscar.py 'ajp13' -v
```
