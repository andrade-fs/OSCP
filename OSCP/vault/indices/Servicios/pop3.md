# Servicio: pop3

[[00-inicio|Inicio]] · [[Entorno|Entorno]] · [[Puertos|Puertos]] · [[Servicios|Servicios]] · [[Tecnicas|Tecnicas]] · [[Maquinas|Maquinas]] · [[Referencias|Referencias]]

**7 máquina(s)** exponen `pop3` · **1 en el listado OSCP**

Puertos donde aparece: [[110]]

| Máquina | Puerto | Estado | Qué era realmente | OSCP |
|---|---|---|---|---|
| [[htb-mailing\|Mailing]] | [[110]] | `open` | — | **sí** |
| [[htb-beep\|Beep]] | [[110]] | `open` | — | — |
| [[htb-brainfuck\|Brainfuck]] | [[110]] | `open` | — | — |
| [[htb-chaos\|Chaos]] | [[110]] | `open` | — | — |
| [[htb-solidstate\|SolidState]] | [[110]] | `open` | James Mail Server | — |
| [[htb-tentacle\|Tentacle]] | [[110]] | `closed` | — | — |
| [[htb-university\|University]] | [[110]] | `closed` | — | — |

## Cómo profundizar

```bash
python3 _sistema/herramientas/buscar.py 'pop3' -v
```
