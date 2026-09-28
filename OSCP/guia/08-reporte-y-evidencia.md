# 08 — Reporte y evidencia

> Todo lo de este documento está tomado del *OSCP+ Exam Guide* de OffSec.
> Las citas textuales son **verbatim**. Cuando dudes, volvé al original:
> `help.offsec.com/hc/en-us/articles/360040165632`

---

## Por qué esto es una sección de examen, no un trámite

> "The documentation requirements are very strict and failure to provide sufficient
> documentation will result in **reduced or zero points** being awarded."

Y el detalle que convierte esto en algo crítico:

> "**once your exam report is submitted, your submission is final.** If any screenshots or other
> information is missing, you will not be allowed to send them and we will not request them."

**No hay segunda instancia.** Existe un escenario muy real: comprometés las 6 máquinas, tenés
100 puntos, y te dan menos de 70 porque la documentación no alcanzó. La documentación **es**
parte del examen.

---

## El estándar de calidad exigido

> "You must document all of your attacks including **all steps, commands issued, and console
> output** in the form of a penetration test report. Your documentation should be thorough
> enough that your attacks can be **replicated step-by-step by a technically competent reader**."

### La prueba de fuego

Preguntate, por cada máquina:

> *¿Podría un pentester competente, que nunca vio esta máquina, reproducir exactamente lo que
> hice con solo leer mi reporte, sin adivinar nada?*

Si la respuesta es "casi" o "se sobreentiende", **no alcanza**. "Se sobreentiende" no es
documentación.

### Qué significa en la práctica

| ❌ Insuficiente | ✅ Correcto |
| --- | --- |
| "Exploté la vulnerabilidad de upload" | El request completo, la ruta, el payload subido, y la respuesta del servidor |
| "Corrí linpeas y encontré SUID" | El comando, la línea exacta del output que importa, y qué hiciste con eso |
| "Escalé con un exploit de kernel" | Nombre del CVE, URL del exploit, comando, y output de `whoami` como prueba |
| Captura del `proof.txt` suelto | Captura con `proof.txt` **+ IP de la víctima** en el mismo cuadro |

---

## Capturas: las reglas exactas

### Qué debe mostrar cada captura

Cada `local.txt` y `proof.txt` debe aparecer en una captura que incluya **dos cosas**:

1. El **contenido** del archivo.
2. La **IP de la máquina víctima**, vía `ipconfig`, `ifconfig` o `ip addr`.

Las dos, en la misma captura.

```bash
# Linux — un comando que resuelve las dos cosas
cat /root/proof.txt; ip addr
```

```powershell
# Windows
type C:\Users\Administrator\Desktop\proof.txt; ipconfig
```

### Cómo se puede leer el archivo (y cómo NO)

> "The valid way to provide the contents of the proof files is in an interactive shell on the
> target machine with the `type` or `cat` command **from their original location**."
>
> "Obtaining the contents of the proof files in any other way will result in zero points for the
> target machine; **this includes any type of web-based shell**."

**Prohibido**:

- Copiar el flag a otro directorio y leerlo ahí.
- Leerlo con un script, un `find -exec`, o un one-liner.
- Leerlo desde una **webshell**.

Válido: `cat /root/proof.txt` o `type C:\...\proof.txt` en una shell interactiva, desde la
ubicación original.

### Niveles de shell exigidos

- **Linux**: shell de **root**.
- **Windows**: `SYSTEM`, `Administrator`, o usuario con privilegios de Administrator.

> Leer el archivo sin tener el nivel de shell requerido **no da los puntos**.

### Nombre y ubicación de los archivos

| Archivo | Acceso | Ubicación |
| --- | --- | --- |
| `proof.txt` | root / Administrator | `/root/` o el Desktop del Administrator |
| `local.txt` | usuario sin privilegios | según la máquina |

---

## Código de exploit: qué incluir

La guía distingue dos casos y esto se pasa por alto todo el tiempo.

### Si NO modificaste el exploit

> "If you have not made any modifications to an exploit, you should only provide the **URL** where
> the exploit can be found. Do not include the full unmodified code, especially if it is several
> pages long."

**Solo la URL.** No pegues 300 líneas de código ajeno: no suma y te infla el PDF.

### Si modificaste el exploit

> "If you have modified an exploit, you should include:
> - The modified exploit code
> - The URL to the original exploit code
> - The command used to generate any shellcode (if applicable)
> - Highlighted changes you have made
> - An explanation of why those changes were made"

Los cinco puntos. El último — **por qué** cambiaste algo — es el que más se olvida y el que
demuestra que entendés lo que hiciste.

---

## Entrega: el checklist exacto

> "Your exam report is in PDF format"
> "You have used the following format for the PDF file name `OSCP-OS-XXXXX-Exam-Report.pdf`,
> where `OS-XXXXX` is your OSID"
> "Your PDF has been archived into a .7z file (**Please do NOT archive it with a password**)"
> "You have used the following format for the .7z file name `OSCP-OS-XXXXX-Exam-Report.7z`"
> "You have made sure that your archive is not more than 200MB"
> "You have uploaded your .7z file to https://upload.offsec.com"

### Detalles donde la gente se cae

- **El nombre es case-sensitive.** Si no sigue el formato exacto, **el sistema rechaza el archivo**.
  Reemplazá `OS-XXXXX` por tu OSID real. Ejemplo: `OSCP-OS-12345-Exam-Report.pdf`.
- **Sin contraseña en el .7z.** Un archivo protegido no se acepta.
- **Dentro del .7z solo van PDFs.** Scripts y PoCs van **como texto adentro del PDF**:
  > "Please make sure to include all your scripts or any PoCs as text inside the exam report PDF
  > file itself. No other file formats will be accepted within the .7z file other than PDF file format."
- **Si mandás otro formato, no te avisan y no te puntúan.**
  > "If you submit your report in any other file format, we will not request or remind you to
  > send a PDF report archived into a .7z file and **your exam report will not be scored**."

### Empaquetar y verificar

```bash
sudo 7z a OSCP-OS-XXXXX-Exam-Report.7z OSCP-OS-XXXXX-Exam-Report.pdf

# Verificar el tamaño (máximo 200 MB)
ls -lh OSCP-OS-XXXXX-Exam-Report.7z

# Sacar el MD5 para comparar con el que devuelve la web
sudo md5sum OSCP-OS-XXXXX-Exam-Report.7z
```

Después de subir, la web muestra el MD5 del archivo recibido. **Comparalo con el local.**

> "If the values do not match, that means your file did not upload successfully."

Si el archivo pasa de 200 MB, la guía sugiere comprimir las imágenes.

---

## Disciplina durante el examen: cómo se hace en la práctica

El reporte **se escribe durante** el examen, no después. Al terminar tenés 24 h, pero vas a estar
agotado y sin estado de las máquinas para volver a sacar capturas.

### Estructura desde el minuto cero

```bash
mkdir -p ~/examen/{targets,evidencia,nmap}
for t in stand1 stand2 stand3 dc01 dc02 dc03; do
  mkdir -p ~/examen/evidencia/$t
done
```

### Bitácora por máquina

Creá un archivo por máquina y **pegalo todo ahí en el momento**. No confíes en el scrollback
del terminal: se pierde, se cierra, o se llena.

```markdown
# stand1 — 10.10.10.5

## Recon
nmap -p- --min-rate 5000 -T4 10.10.10.5
<pegar output>

## Puertos abiertos
22, 80, 445

## 80/tcp — Apache 2.4.49
CVE-2021-41773 (path traversal)
...
```

### El hábito que salva puntos

Cada vez que conseguís algo, **dos acciones seguidas y en este orden**:

1. **Captura** — `local.txt`/`proof.txt` + IP en el mismo cuadro.
2. **Pegar** el comando y su output en la bitácora.

Después, y solo después, seguí atacando.

Si te olvidás la captura en una máquina que después rompés (o revertís), **esos puntos se
fueron**. No hay forma de recuperarlos.

### Herramientas que ayudan

- **`script`** — graba toda la sesión de terminal, con output incluido:
  ```bash
  script -a ~/examen/evidencia/stand1/sesion.log
  # ... trabajás ...
  exit
  ```
  Después extraés los comandos y outputs que necesitás.
- **Capturas con un atajo de teclado** — configurá uno antes del examen. Buscar el botón de
  captura bajo presión es tiempo perdido.
- **`tmux`** — una ventana por máquina. No mezclás contextos y el scrollback queda separado.

---

## Contingencias: la guía las contempla

> "The total allotted time of 23:45 hours does take life and its situations into consideration:
> You are expected to take rest breaks, eat, drink, and sleep"

Dormir y comer no es debilidad: está **explícitamente** contemplado por OffSec.

> "You are also expected to have a contingency plan in the event that there is an issue outside
> your control. (e.g. ensure you have access to a backup Internet connection, Kali Virtual
> Machine, power etc)"

**Armá el plan de contingencia antes:** conexión de internet alternativa, la VM de Kali
respaldada, y energía asegurada. No es paranoia — la guía lo pide.

### Si pasa algo grave

> "If you have a legitimate issue, please send an email with your OSID to
> 'challenges AT offsec DOT com' immediately."

Incluí evidencia: carta de la compañía eléctrica, del ISP, o documentación equivalente.

> "Please note we are only able to extend the exam time if the issues are present on our side"

O sea: un problema de **tu** lado no se extiende. De ahí la importancia del plan B.

### Problemas técnicos, no de contenido

Vía chat de proctoring, `https://chat.offsec.com/`, o `help AT offsec DOT com`.

> "Please note that we will not be able to assist with, or give hints on, any exam objectives and
> will only be available for technical problems during the exam."

**No vas a poder pedir una pista.** Ni sobre un flag, ni sobre si vas bien. Es soporte técnico.

---

## Errores de reporte que cuestan puntos

| Error | Consecuencia |
| --- | --- |
| Documentar al final | Sin estado de las máquinas, capturas irrecuperables |
| Captura sin la IP de la víctima | Puntos no acreditados |
| Leer el flag desde una webshell | **Cero puntos** en esa máquina |
| Copiar el flag a otro directorio | **Cero puntos** |
| Entregar en otro formato que no sea PDF en .7z | **No te puntúan, sin avisar** |
| .7z con contraseña | Rechazado |
| Nombre de archivo mal formado | El sistema rechaza el archivo |
| Pegar código de exploit sin modificar | Ruido; para eso alcanza la URL |
| Modificar un exploit sin explicar por qué | Falta el punto que demuestra comprensión |
| No verificar el MD5 al subir | Reporte no entregado y no lo sabés |

---

## Plantilla de reporte

La guía sugiere usar una plantilla de Microsoft Word o LibreOffice/OpenOffice, y aclara:

> "You may use your own template as long as the information is presented in a structured,
> professional manner and follows all other requirements outlined above."

Estructura que cubre todos los requisitos:

```text
1. Portada
   - Nombre, OSID, fecha
   - Declaración de confidencialidad

2. Resumen ejecutivo
   - Máquinas comprometidas y puntaje obtenido
   - Resultado por máquina (target / puntos)

3. Metodología
   - Alcance, herramientas usadas, enfoque general

4. Hallazgos por máquina
   4.1 Resumen del objetivo (IP, hostname, SO)
   4.2 Enumeración
       - Comandos + output literal
   4.3 Acceso inicial
       - Vulnerabilidad, explotación, evidencia
       - Captura de local.txt + IP
   4.4 Escalada de privilegios
       - Enumeración local, vector, explotación
       - Captura de proof.txt + IP
   4.5 Loot
       - Credenciales, hashes, archivos relevantes

5. Set de Active Directory
   - Credenciales iniciales provistas
   - Enumeración del dominio
   - Camino de ataque por máquina (gráfico o narrado)
   - Capturas de cada local.txt / proof.txt

6. Anexos
   - Scripts y PoCs COMO TEXTO
   - Exploits modificados con los 5 puntos exigidos
```

---

## Checklist final antes de subir

Repasá esto **dos veces**:

- [ ] El PDF incluye **todas** las capturas de `local.txt` y `proof.txt`
- [ ] **Cada** captura muestra el contenido del archivo **y** la IP de la víctima
- [ ] Todas las capturas se sacaron con `cat`/`type` en shell interactiva desde la ubicación original
- [ ] Los niveles de shell eran root / SYSTEM / Administrator
- [ ] Los exploits **no** modificados aparecen solo como URL
- [ ] Los exploits **modificados** tienen los 5 elementos exigidos
- [ ] Los scripts y PoCs están **como texto dentro del PDF**
- [ ] El archivo se llama `OSCP-OS-XXXXX-Exam-Report.pdf` (tu OSID, respetando mayúsculas)
- [ ] El `.7z` se llama `OSCP-OS-XXXXX-Exam-Report.7z` y **no** tiene contraseña
- [ ] El `.7z` pesa menos de 200 MB
- [ ] El PDF abre bien y no tiene errores de formato
- [ ] Verificaste el MD5 contra el que devolvió la web de subida
