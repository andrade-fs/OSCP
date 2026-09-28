# OSCP

Repositorio de preparación para el examen **OSCP**: documentación (vault de Obsidian)
y un instalador scripteado del arsenal sobre **Kali Linux ARM64**.

> ⚠️ Material de estudio. Contiene writeups/notas de laboratorios (HTB/OSCP) con
> credenciales de *labs*, no de sistemas reales.

## Contenido

| Carpeta | Qué es |
|---|---|
| `OSCP/` | Vault de Obsidian: guía, cheatsheets, índices de puertos/técnicas, corpus de writeups |
| `OSCP-setup/` | Instalador idempotente y reversible del arsenal (apt / pipx / go / GitHub / toolkits / wordlists / config) |

## Puesta en marcha del entorno (Kali ARM64)

```bash
cd OSCP-setup
./install.sh --dry-run          # ver sin tocar
./install.sh                    # perfil oscp
./install.sh --profile full     # arsenal completo
./verify.sh                     # comprobar
./uninstall.sh [--apt --all]    # revertir
```

El instalador crea `~/Documentos/{Tools,VPN,machines}` y deja los toolkits en
`Tools/linux` (amd64) y `Tools/win` (x86_64) para las víctimas.

## Helper de máquinas

```bash
cd OSCP-setup
./new-machine.sh pelican --os linux --ip 10.10.10.20 --tags oscp
```

## Uso del vault en Obsidian

Abre `OSCP/` como vault. Índices: `vault/indices/{Puertos,Tecnicas,Servicios,Referencias}.md`.
