# Servicio: ms-sql-s

[[00-inicio|Inicio]] · [[Entorno|Entorno]] · [[Puertos|Puertos]] · [[Servicios|Servicios]] · [[Tecnicas|Tecnicas]] · [[Maquinas|Maquinas]] · [[Referencias|Referencias]]

**16 máquina(s)** exponen `ms-sql-s` · **5 en el listado OSCP**

Puertos donde aparece: [[1433]]

| Máquina | Puerto | Estado | Qué era realmente | OSCP |
|---|---|---|---|---|
| [[htb-breach\|Breach]] | [[1433]] | `open` | — | **sí** |
| [[htb-eighteen\|Eighteen]] | [[1433]] | `open` | MSSQL | **sí** |
| [[htb-escape\|Escape]] | [[1433]] | `open` | — | **sí** |
| [[htb-manager\|Manager]] | [[1433]] | `open` | — | **sí** |
| [[htb-signed\|Signed]] | [[1433]] | `open` | MSSQL | **sí** |
| [[htb-blazorized\|Blazorized]] | [[1433]] | `open` | — | — |
| [[htb-darkzero\|DarkZero]] | [[1433]] | `open` | MSSQL | — |
| [[htb-escapetwo\|EscapeTwo]] | [[1433]] | `open` | — | — |
| [[htb-ghost\|Ghost]] | [[1433]] | `open` | — | — |
| [[htb-mantis\|Mantis]] | [[1433]] | `open` | MSSQL | — |
| [[htb-pivotapi\|PivotAPI]] | [[1433]] | `open` | — | — |
| [[htb-querier\|Querier]] | [[1433]] | `open` | — | — |
| [[htb-redelegate\|Redelegate]] | [[1433]] | `open` | — | — |
| [[htb-scrambled-linux\|Scrambled [From Linux]]] | [[1433]] | `open` | — | — |
| [[htb-scrambled-win\|Scrambled [From Windows]]] | [[1433]] | `open` | — | — |
| [[htb-tally\|Tally]] | [[1433]] | `open` | — | — |

## Cómo profundizar

```bash
python3 _sistema/herramientas/buscar.py 'ms-sql-s' -v
```
