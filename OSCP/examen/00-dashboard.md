# 🎯 EXAMEN — panel de control

> **Un documento por máquina.** Anotá aquí los pasos, comandos y output **en el momento**.
> El reporte es final e inapelable: si no lo capturaste, se perdió.

[[00-inicio|Inicio]] · [[01-metodologia|Metodología]] · [[08-reporte-y-evidencia|Reporte]] · [[Entorno|Entorno]]

---

## ⏱️ Plan de tiempo (23 h 45 min)

| Bloque | Horas | Foco | Estado |
| --- | --- | --- | --- |
| Triage | 0:00 – 1:30 | Recon de las 6 máquinas. Solo mapa. | ☐ |
| AD | 1:30 – 6:00 | Set de AD con creds frescas → [[ad-miembro-1]] · [[ad-miembro-2]] · [[ad-dc]] | ☐ |
| Sueltas | 6:00 – 12:00 | [[suelta-112]] · [[suelta-111]] · [[suelta-110]] (de fácil a difícil) | ☐ |
| Descanso | 12:00 – 16:00 | **Dormir.** Documentá el estado antes de irte. | ☐ |
| Cierre | 16:00 – 21:00 | Volver al AD, cerrar, exprimir flags parciales | ☐ |
| Reporte | 21:00 – 23:45 | Ordenar evidencia y escribir | ☐ |

> **Regla 1 h 30 min**: si te trabás más de 90 min en el mismo punto, cambiá de máquina y volvé.

---

## 🖥️ Estado de las máquinas

| Máquina | IP | SO | Tipo | Acceso (10) | Escalada (10/20) | Total | Notas |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [[suelta-112]] | | Linux/Win | Suelta | ☐ | ☐ | 0/20 | |
| [[suelta-111]] | | Linux/Win | Suelta | ☐ | ☐ | 0/20 | |
| [[suelta-110]] | | Linux/Win | Suelta | ☐ | ☐ | 0/20 | |
| [[ad-miembro-1]] | | Windows | AD cliente | ☐ | ☐ | 0/10 | |
| [[ad-miembro-2]] | | Windows | AD cliente | ☐ | ☐ | 0/10 | |
| [[ad-dc]] | | Windows | AD DC | ☐ | ☐ | 0/20 | |

**Total: ☐ / 100** (aprueba con 70)

---

## 🔑 Credenciales GLOBALES (sirven para varias máquinas)

> Lo que encuentres en una máquina suele servir en otra. Volcá aquí **todo** lo reutilizable.
> Credenciales específicas de cada host: en su propio documento.

### Usuarios y contraseñas

| Usuario | Contraseña | Dominio/Host | De dónde salió | Probado en |
| --- | --- | --- | --- | --- |
| | | | | |

### Hashes NTLM

| Usuario | Hash | Host | Probado en |
| --- | --- | --- | --- |
| | | | |

### Tiques / ccache

| Usuario | Fichero | Tipo | Notas |
| --- | --- | --- | --- |
| | | | |

> Credenciales y notas del AD: [[ad-credenciales]].

---

## ✅ Checklist de arranque

- [ ] VPN conectada (`ip a` muestra `tun0`)
- [ ] `/etc/hosts` con el DC y los nombres que aparezcan
- [ ] Reloj sincronizado (`sudo ntpdate <DC_IP>`) antes del AD
- [ ] `~/examen/evidencia/` por máquina
- [ ] Toolkit sirviéndose: `cd ~/examen/tools && python3 -m http.server 8000`
- [ ] `script -a ~/examen/evidencia/<maq>/sesion.log` en cada shell

## 📸 Recordatorio de flags

- `local.txt` → `cat local.txt; ip addr` (Linux) / `type ...; ipconfig` (Windows)
- `proof.txt` → shell de **root** / **SYSTEM/Administrator**
- Captura = **contenido + IP de la víctima** en el mismo cuadro
- **Nunca** desde una webshell
- Enviar los flags en el panel **antes** de que termine el examen
