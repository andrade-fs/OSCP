# Como buscar en el corpus

Corpus de writeups publicos de 0xdf, descargados desde el `sitemap.xml` del sitio
y convertidos a markdown. Cada archivo tiene frontmatter con metadatos
(maquina, SO, dificultad, si esta en el listado OSCP, URL original).

## Busqueda por palabra clave (recomendado)

```bash
cd ~/OSCP

# Todas las referencias a una tecnica, agrupadas por maquina
python3 _sistema/herramientas/buscar.py PrintSpoofer

# Con contexto: ver el comando y el output alrededor
python3 _sistema/herramientas/buscar.py PrintSpoofer -v

# Mas contexto todavia
python3 _sistema/herramientas/buscar.py PrintSpoofer -vv

# Solo maquinas del listado OSCP
python3 _sistema/herramientas/buscar.py kerberoasting -v --oscp

# Solo Linux, o solo una dificultad
python3 _sistema/herramientas/buscar.py "sudo -l" -v --os Linux
python3 _sistema/herramientas/buscar.py seimpersonate -v --dificil Hard

# Regex
python3 _sistema/herramientas/buscar.py "GodPotato|JuicyPotato|PrintSpoofer"

# Solo los nombres de maquina (vista rapida)
python3 _sistema/herramientas/buscar.py kerberoasting --nombres

# Que tecnicas conoce el diccionario
python3 _sistema/herramientas/buscar.py --listar-tecnicas
```

## Busqueda cruda (ripgrep)

```bash
# Lista de maquinas que mencionan algo
rg -l 'kerberoast' corpus/ | sort

# Con numero de linea y contexto
rg -n -C 4 'PrintSpoofer' corpus/

# Solo bloques de codigo (comandos)
rg -n -A 6 '^```' corpus/htb/ -g '*.md' | rg -A 6 'impacket'
```

## Indices

| Archivo | Contenido |
|---|---|
| [[maquinas]] | Tabla de las 566 maquinas con SO, dificultad y marca OSCP |
| [[tecnicas]] | Indice inverso: tecnica -> maquinas donde aparece |

## En Obsidian

Apuntalo como vault a `~/OSCP/corpus`. Funcionan:

- **Busqueda global** (`Ctrl+Shift+F`): full-text sobre todo el corpus.
- **Propiedades**: filtrar por `os`, `dificultad`, `en_lista_oscp`.
  Ejemplo de busqueda: `["en_lista_oscp":"true"] seimpersonate`
- **Grafo**: los enlaces `[[maquina]]` de los indices arman la red.
- **Backlinks**: desde una maquina, que tecnicas la referencian.

> Las imagenes de los writeups **no** se descargaron: el markdown conserva los
> enlaces a las originales. El corpus esta pensado para busqueda de TEXTO.
