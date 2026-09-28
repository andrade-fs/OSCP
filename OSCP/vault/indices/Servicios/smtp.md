# Servicio: smtp

[[00-inicio|Inicio]] · [[Entorno|Entorno]] · [[Puertos|Puertos]] · [[Servicios|Servicios]] · [[Tecnicas|Tecnicas]] · [[Maquinas|Maquinas]] · [[Referencias|Referencias]]

**19 máquina(s)** exponen `smtp` · **2 en el listado OSCP**

Puertos donde aparece: [[25]]

| Máquina | Puerto | Estado | Qué era realmente | OSCP |
|---|---|---|---|---|
| [[htb-job\|Job]] | [[25]] | `open` | SMTP | **sí** |
| [[htb-mailing\|Mailing]] | [[25]] | `open` | — | **sí** |
| [[htb-attended\|Attended]] | [[25]] | `open` | SMTP | — |
| [[htb-axlle\|Axlle]] | [[25]] | `open` | — | — |
| [[htb-beep\|Beep]] | [[25]] | `open` | SMTP | — |
| [[htb-brainfuck\|Brainfuck]] | [[25]] | `open` | — | — |
| [[htb-gofer\|Gofer]] | [[25]] | `filtered` | — | — |
| [[htb-jobtwo\|JobTwo]] | [[25]] | `open` | — | — |
| [[htb-magicgardens\|MagicGardens]] | [[25]] | `filtered` | — | — |
| [[htb-outdated\|Outdated]] | [[25]] | `open` | — | — |
| [[htb-overflow\|Overflow]] | [[25]] | `open` | — | — |
| [[htb-rabbit\|Rabbit]] | [[25]] | `open` | — | — |
| [[htb-reel\|Reel]] | [[25]] | `open` | — | — |
| [[htb-scavenger\|Scavenger]] | [[25]] | `open` | SMTP | — |
| [[htb-sneakymailer\|SneakyMailer]] | [[25]] | `open` | — | — |
| [[htb-solidstate\|SolidState]] | [[25]] | `open` | James Mail Server | — |
| [[htb-tentacle\|Tentacle]] | [[25]] | `closed` | — | — |
| [[htb-trick\|Trick]] | [[25]] | `open` | SMTP | — |
| [[htb-university\|University]] | [[25]] | `closed` | — | — |

## Cómo profundizar

```bash
python3 _sistema/herramientas/buscar.py 'smtp' -v
```
