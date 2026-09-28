# Servicio: mysql

[[00-inicio|Inicio]] · [[Entorno|Entorno]] · [[Puertos|Puertos]] · [[Servicios|Servicios]] · [[Tecnicas|Tecnicas]] · [[Maquinas|Maquinas]] · [[Referencias|Referencias]]

**15 máquina(s)** exponen `mysql` · **1 en el listado OSCP**

Puertos donde aparece: [[3306]]

| Máquina | Puerto | Estado | Qué era realmente | OSCP |
|---|---|---|---|---|
| [[htb-build\|Build]] | [[3306]] | `filtered` | — | **sí** |
| [[htb-ambassador\|Ambassador]] | [[3306]] | `open` | — | — |
| [[htb-analysis\|Analysis]] | [[3306]] | `open` | — | — |
| [[htb-bankrobber\|Bankrobber]] | [[3306]] | `open` | MySQL | — |
| [[htb-beep\|Beep]] | [[3306]] | `open` | — | — |
| [[htb-breadcrumbs\|Breadcrumbs]] | [[3306]] | `open` | — | — |
| [[htb-carpediem\|CarpeDiem]] | [[3306]] | `open` | — | — |
| [[htb-control\|Control]] | [[3306]] | `open` | MySQL | — |
| [[htb-cybermonday\|CyberMonday]] | [[3306]] | `open` | — | — |
| [[htb-love\|Love]] | [[3306]] | `open` | MySQL | — |
| [[htb-oouch\|Oouch]] | [[3306]] | `open` | — | — |
| [[htb-rabbit\|Rabbit]] | [[3306]] | `open` | — | — |
| [[htb-registrytwo\|RegistryTwo]] | [[3306]] | `open` | — | — |
| [[htb-spectra\|Spectra]] | [[3306]] | `open` | — | — |
| [[htb-toby\|Toby]] | [[3306]] | `open` | — | — |

## Cómo profundizar

```bash
python3 _sistema/herramientas/buscar.py 'mysql' -v
```
