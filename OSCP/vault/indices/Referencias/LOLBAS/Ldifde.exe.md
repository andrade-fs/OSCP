# LOLBAS: Ldifde.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Download`

Creates, modifies, and deletes LDAP directory objects.

## Comandos

### Download file from Internet

Download · priv: Administrator · T1105

```cmd
Ldifde -i -f {PATH:.ldf}
```

Import specified .ldf file into LDAP. If the file contains http-based attrval-spec such as `thumbnailPhoto:< http://example.org/somefile.txt`, the file will be downloaded into IE temp folder.

