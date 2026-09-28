# 01 — Metodología y gestión de tiempo

## El bucle

No hay atajos ni "trucos". Hay un bucle, y ganás iterándolo rápido:

```text
┌─ 1. RECON ────────────► nmap TCP completo + UDP top, sin interpretar todavía
│
├─ 2. ENUMERAR ─────────► por CADA servicio abierto, en profundidad, antes de explotar
│
├─ 3. FOOTHOLD ─────────► la vulnerabilidad más simple que te dé ejecución
│
├─ 4. SHELL ESTABLE ────► reverse shell real, TTY, sin webshell
│
├─ 5. ENUMERAR LOCAL ───► usuario, grupos, sudo, SUID, servicios, red interna, archivos
│
├─ 6. ESCALAR ──────────► root / Administrator / SYSTEM
│
├─ 7. LOOT ─────────────► flags, credenciales, hashes, tiques, configs
│
└─ 8. DOCUMENTAR ───────► capturas y comandos AL MOMENTO (ver [`08-reporte-y-evidencia.md`](08-reporte-y-evidencia.md))
```

El paso 8 no es el último: es **continuo**. Si lo dejás para el final, perdiste.

> Este bucle es el **patrón**. El recorrido concreto, máquina a máquina, está en los
> walkthroughs: [`AD-walkthrough.md`](walkthroughs/AD-walkthrough.md) y
> [`Standalone-walkthrough.md`](walkthroughs/Standalone-walkthrough.md).

---

## Regla de oro: enumerá antes de explotar

El 90 % de los bloqueos largos son **enumeración incompleta**, no falta de skill.

Antes de tirar el primer exploit:

- ¿Corriste el nmap de **todos** los puertos TCP? (no el default de 1000)
- ¿Corriste UDP en los puertos que importan?
- ¿Miraste **virtual hosts**? Un `Host:` header distinto te da una aplicación distinta.
- ¿Fuzzeaste **directorios y archivos**?
- ¿Miraste el **código fuente** de la web y los archivos de config?
- ¿Probaste **credenciales por defecto y reutilización**?

### Recon inicial — comandos

```bash
# 1) TCP completo, rápido. SIEMPRE todos los puertos.
sudo nmap -p- --min-rate 5000 -T4 -oA nmap/alltcp <IP>

# 2) Servicios y versiones sobre lo que apareció
sudo nmap -sCV -p$(ports comma-separated) -oA nmap/services <IP>

# 3) UDP en lo que importa (lento, no barras todo)
sudo nmap -sU --top-ports 50 -oA nmap/udp <IP>

# 4) Scripts de descubrimiento sobre lo abierto
sudo nmap -sCV --script "default,safe,discovery" -p<ports> -oA nmap/scripts <IP>
```

> `-p-` tarda. Es la diferencia entre encontrar el servicio raro y no encontrarlo. Nunca
> lo saltees, ni siquiera cuando tenés apuro.

### Violencia de descubrimiento web

```bash
# Directorios y archivos
ffuf -u http://<IP>/FUZZ -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt \
     -mc 200,204,301,302,307,401,403 -t 50 -o ffuf-dirs.json

# Virtual hosts — te cambia el juego más seguido de lo que creés
ffuf -u http://<IP>/ -H "Host: FUZZ.<DOMINIO>" \
     -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt \
     -mc 200,301,302,401,403 -fs <tamaño_respuesta_default>

# Extensiones sobre una ruta que ya te interesa
ffuf -u http://<IP>/ruta/FUZZ -w /usr/share/seclists/Discovery/Web-Content/web-extensions.txt
```

---

## Gestión de 23 h 45 min

Es un examen **de resistencia**, no de velocidad. La mayoría no falla por no saber, falla
por administrar mal el reloj y la cabeza.

### Reparto sugerido

| Bloque | Horas | Foco |
| --- | --- | --- |
| **Triage** | 0:00 – 1:30 | Recon de las 6 máquinas. Nada de explotar. Solo mapa. |
| **AD** | 1:30 – 6:00 | Set de AD con credenciales frescas y cabeza despierta → [`AD-walkthrough.md`](walkthroughs/AD-walkthrough.md) |
| **Sueltas** | 6:00 – 12:00 | Las independientes, de más fácil a más difícil → [`Standalone-walkthrough.md`](walkthroughs/Standalone-walkthrough.md) |
| **Descanso** | 12:00 – 16:00 | **Dormir.** Ver abajo. |
| **Cierre** | 16:00 – 21:00 | Volver al AD, cerrar lo empezado, exprimir flags parciales |
| **Reporte** | 21:00 – 23:45 | Ordenar evidencia, escribir, verificar capturas |

> **Cada bloque tiene su recorrido paso a paso:** el set de AD en
> [`AD-walkthrough.md`](walkthroughs/AD-walkthrough.md) y las máquinas sueltas en
> [`Standalone-walkthrough.md`](walkthroughs/Standalone-walkthrough.md). El bucle de arriba es el patrón;
> los walkthroughs son la secuencia concreta con las decisiones en cada bifurcación.

### Dormir es una decisión táctica, no debilidad

23 h 45 min es tiempo de sobra. **No es una carrera de 24 h seguidas.** A la hora 14 tenés
menos capacidad de enumeración fina que a la hora 4, y en este examen la enumeración fina es
todo. Un bloque de 3–4 h de sueño te devuelve más capacidad de la que te saca en tiempo.

Si vas a dormir: **documentá el estado antes de irte**. Una nota de "estaba en X, probé Y,
falló Z, quería probar W" al volver vale oro. Sin eso perdés 40 minutos reconstruyendo el hilo.

### Disciplina anti-rabia

Vas a encontrar una máquina que se te resiste. Es parte del diseño.

- **Marca el tiempo de bloqueo.** Si superás **1 h 30 min** clavado en el mismo punto, cambiá de máquina. Volvés después.
- **Cambiar de máquina no es abandonar.** Es reasignar recurso escaso (tu cabeza).
- **Anotá por qué estás clavado**, no solo qué probaste. "El exploit tira 500 en el paso 3"
  es más útil que "no funciona".
- **Cero puntos por sufrir.** El reloj corre igual.

### Señales de que hay que parar y descansar

- Estás releyendo el mismo output por tercera vez.
- Empezás a tocar la configuración de tu Kali (señal clásica de evitación).
- Copiaste un comando sin mirar los placeholders.

Cualquiera de esas tres: levantate, tomá agua, camina 10 minutos.

---

## Higiene de documentación

El reporte es **final e inapelable**. No hay instancia de corrección.

> "If any screenshots or other information is missing, you will not be allowed to send them
> and we will not request them."

### Estructura de trabajo desde el minuto cero

```bash
mkdir -p ~/examen/{targets,evidencia,nmap}
# Un directorio por máquina, con subcarpetas predecibles
for t in stand1 stand2 stand3 dc01 dc02 dc03; do
  mkdir -p ~/examen/evidencia/$t
done
```

### Una regla que te salva

**Sacá la captura en el momento, no después.** El estado de la máquina no se conserva y
reproducir el camino cuesta tiempo que no tenés.

Cada vez que conseguís algo, dos acciones seguidas:

1. Captura con `local.txt`/`proof.txt` + IP visible en el mismo cuadro.
2. Pegá el comando y su output en la bitácora de esa máquina.

Si te olvidás el paso 1 en una máquina que después rompés, perdiste esos puntos.

Ver `08-reporte-y-evidencia.md` para el flujo completo.

---

## Errores de metodología que cuestan puntos

| Error | Consecuencia |
| --- | --- |
| Explotar antes de enumerar completo | Bloqueos largos y caminos muertos |
| Saltear `-p-` en nmap | No ves el servicio que era la entrada |
| Ignorar virtual hosts | No ves la aplicación vulnerable |
| Webshell como shell de trabajo | **Cero puntos** en esa máquina: los flags exigen shell interactiva |
| Documentar al final | El reporte es final; lo que falta, falta |
| Usar Metasploit en 2+ máquinas | **Cero puntos** en la máquina |
| Revertir por reflejo | Perdés todo tu progreso en esa máquina |
| No dormir | Enumeración degradada en la mitad final del examen |
