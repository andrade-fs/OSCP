# Servicio: ppp

[[00-inicio|Inicio]] · [[Entorno|Entorno]] · [[Puertos|Puertos]] · [[Servicios|Servicios]] · [[Tecnicas|Tecnicas]] · [[Maquinas|Maquinas]] · [[Referencias|Referencias]]

**22 máquina(s)** exponen `ppp` · **4 en el listado OSCP**

Puertos donde aparece: [[3000]]

| Máquina | Puerto | Estado | Qué era realmente | OSCP |
|---|---|---|---|---|
| [[htb-build\|Build]] | [[3000]] | `open` | Gitea | **sí** |
| [[htb-data\|Data]] | [[3000]] | `open` | Website | **sí** |
| [[htb-help\|Help]] | [[3000]] | `open` | Web | **sí** |
| [[htb-lock\|Lock]] | [[3000]] | `open` | Gitea | **sí** |
| [[htb-ambassador\|Ambassador]] | [[3000]] | `open` | Grafana | — |
| [[htb-catch\|Catch]] | [[3000]] | `open` | Gitea | — |
| [[htb-codify\|Codify]] | [[3000]] | `open` | Website | — |
| [[htb-compiled\|Compiled]] | [[3000]] | `open` | Gitea | — |
| [[htb-derailed\|Derailed]] | [[3000]] | `open` | Website | — |
| [[htb-drive\|Drive]] | [[3000]] | `filtered` | — | — |
| [[htb-dyplesher\|Dyplesher]] | [[3000]] | `open` | Gogs | — |
| [[htb-format\|Format]] | [[3000]] | `open` | microblog.htb | — |
| [[htb-greenhorn\|GreenHorn]] | [[3000]] | `open` | Gitea | — |
| [[htb-health\|Health]] | [[3000]] | `filtered` | Read | — |
| [[htb-lantern\|Lantern]] | [[3000]] | `open` | Website | — |
| [[htb-luke\|Luke]] | [[3000]] | `open` | Website | — |
| [[htb-node\|Node]] | [[3000]] | `open` | Website | — |
| [[htb-opensource\|OpenSource]] | [[3000]] | `filtered` | — | — |
| [[htb-ouija\|Ouija]] | [[3000]] | `open` | API | — |
| [[htb-secret\|Secret]] | [[3000]] | `open` | Website | — |
| [[htb-sink\|Sink]] | [[3000]] | `open` | Gitea | — |
| [[htb-talkative\|Talkative]] | [[3000]] | `open` | Rocket Chat | — |

## Cómo profundizar

```bash
python3 _sistema/herramientas/buscar.py 'ppp' -v
```
