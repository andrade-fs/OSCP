# Servicio: zabbix-agent

[[00-inicio|Inicio]] · [[Entorno|Entorno]] · [[Puertos|Puertos]] · [[Servicios|Servicios]] · [[Tecnicas|Tecnicas]] · [[Maquinas|Maquinas]] · [[Referencias|Referencias]]

**3 máquina(s)** exponen `zabbix-agent`

Puertos donde aparece: [[10050]]

| Máquina | Puerto | Estado | Qué era realmente | OSCP |
|---|---|---|---|---|
| [[htb-unrested\|Unrested]] | [[10050]] | `open` | — | — |
| [[htb-watcher\|Watcher]] | [[10050]] | `open` | — | — |
| [[htb-zipper\|Zipper]] | [[10050]] | `open` | Zabbix Agent | — |

## Cómo profundizar

```bash
python3 _sistema/herramientas/buscar.py 'zabbix-agent' -v
```
