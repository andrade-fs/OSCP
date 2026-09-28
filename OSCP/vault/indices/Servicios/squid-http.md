# Servicio: squid-http

[[00-inicio|Inicio]] · [[Entorno|Entorno]] · [[Puertos|Puertos]] · [[Servicios|Servicios]] · [[Tecnicas|Tecnicas]] · [[Maquinas|Maquinas]] · [[Referencias|Referencias]]

**7 máquina(s)** exponen `squid-http` · **1 en el listado OSCP**

Puertos donde aparece: [[3128]]

| Máquina | Puerto | Estado | Qué era realmente | OSCP |
|---|---|---|---|---|
| [[htb-bamboo\|Bamboo]] | [[3128]] | `open` | Squid | **sí** |
| [[htb-corporate\|Corporate]] | [[3128]] | `open` | — | — |
| [[htb-flustered\|Flustered]] | [[3128]] | `open` | — | — |
| [[htb-inception\|Inception]] | [[3128]] | `open` | Squid | — |
| [[htb-joker\|Joker]] | [[3128]] | `open` | Squid Proxy w/o Creds | — |
| [[htb-tentacle\|Tentacle]] | [[3128]] | `open` | Squid | — |
| [[htb-unbalanced\|Unbalanced]] | [[3128]] | `open` | Squid | — |

## Cómo profundizar

```bash
python3 _sistema/herramientas/buscar.py 'squid-http' -v
```
