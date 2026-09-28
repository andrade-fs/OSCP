# Técnica: credenciales en archivos

[[00-inicio|Inicio]] · [[Entorno|Entorno]] · [[Puertos|Puertos]] · [[Servicios|Servicios]] · [[Tecnicas|Tecnicas]] · [[Maquinas|Maquinas]] · [[Referencias|Referencias]]

**0 máquina(s)** mencionan esta técnica.

Alias buscados: `credentials-linux`, `credenciales olvidadas`

> Esta técnica tiene **recetario de comandos**. Está más abajo, después de la lista de máquinas.

## Comandos

> **Placeholders**: `<IP>` · `<USER>`

### Barato de revisar, y da resultado con una frecuencia absurda

Empezá por acá antes de irte a vectores exóticos.

### Historiales

```bash
cat ~/.bash_history ~/.zsh_history ~/.mysql_history ~/.nano_history 2>/dev/null
cat /home/*/.bash_history 2>/dev/null
grep -riE 'pass|passw' ~/.bash_history 2>/dev/null
```

### Configuraciones con contraseñas

```bash
grep -riE "passw|secret|token|api[_-]?key|credential" /var/www /opt /etc /home 2>/dev/null \
  | grep -viE "\.js:|\\.css:|node_modules|\.map:" | head -50

# Archivos de config típicos
find / -name "*.conf" -o -name "*.config" -o -name "*.ini" -o -name "*.env" 2>/dev/null \
  | grep -viE "^/(proc|sys|usr/share|snap)" | head -50

# Web
cat /var/www/html/wp-config.php 2>/dev/null
cat /var/www/html/.env 2>/dev/null
find /var/www -name "*.env*" -o -name "config.php" 2>/dev/null
```

### Claves SSH

```bash
find / -name "id_rsa*" -o -name "id_ed25519*" -o -name "authorized_keys" 2>/dev/null
ls -la /root/.ssh 2>/dev/null
```

Con la clave privada encontrada:
```bash
chmod 600 id_rsa
ssh -i id_rsa <USER>@<IP>
```

### Bases de datos

```bash
# MySQL: si podés leer /var/lib/mysql, sacás los hashes
ls -la /var/lib/mysql/
cat /var/lib/mysql/mysql/user.MYD 2>/dev/null | strings | head

# PostgreSQL
cat ~/.pgpass 2>/dev/null
cat /var/lib/postgresql/.pgpass 2>/dev/null
```

### Archivos de backup y temporales

```bash
find / -name "*.bak" -o -name "*.old" -o -name "*.save" -o -name "*~" 2>/dev/null \
  | grep -viE "^/(proc|sys|usr)" | head -30

ls -la /tmp /var/tmp /dev/shm 2>/dev/null
find /tmp /var/tmp -type f -readable 2>/dev/null | head -30
```

### Lo que dijo `linpeas`

```bash
./linpeas.sh -a 2>/dev/null | grep -iE "password|credential" | head -40
```


---

## Máquinas


## Cómo ver el contexto

```bash
python3 _sistema/herramientas/buscar.py 'credenciales en archivos' -v
python3 _sistema/herramientas/buscar.py 'credenciales en archivos' -v --oscp
```
