# Servicio: imap

[[00-inicio|Inicio]] · [[Entorno|Entorno]] · [[Puertos|Puertos]] · [[Servicios|Servicios]] · [[Tecnicas|Tecnicas]] · [[Maquinas|Maquinas]] · [[Referencias|Referencias]]

**6 máquina(s)** exponen `imap` · **1 en el listado OSCP**

Puertos donde aparece: [[143]]

| Máquina | Puerto | Estado | Qué era realmente | OSCP |
|---|---|---|---|---|
| [[htb-mailing\|Mailing]] | [[143]] | `open` | — | **sí** |
| [[htb-beep\|Beep]] | [[143]] | `open` | — | — |
| [[htb-brainfuck\|Brainfuck]] | [[143]] | `open` | — | — |
| [[htb-chaos\|Chaos]] | [[143]] | `open` | — | — |
| [[htb-outdated\|Outdated]] | [[143]] | `open` | — | — |
| [[htb-sneakymailer\|SneakyMailer]] | [[143]] | `open` | — | — |

## Cómo profundizar

```bash
python3 _sistema/herramientas/buscar.py 'imap' -v
```
