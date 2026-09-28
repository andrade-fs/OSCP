# OSCP-setup

Instalador **scripteado**, idempotente y reversible del arsenal para el examen OSCP
sobre Kali ARM64 (Apple Silicon). Un solo comando deja la máquina lista.

## Estructura que gestiona

```
~/Documentos/
├── OSCP/                      # vault de Obsidian (docs/guía)
├── Tools/
│   ├── kali/                  # tools que corren en Kali (pyLAPS, gMSADumper, …)
│   ├── linux/                 # toolkit para víctimas Linux (amd64)
│   ├── win/                   # toolkit para víctimas Windows (x86_64)
│   ├── repos/                 # clones de fuente (SharpCollection)
│   └── plantillas/            # krb5.conf
├── VPN/                       # (lo llenas tú con tu .ovpn)
└── machines/                  # una subcarpeta por máquina
```

## Uso

```bash
cd ~/Documentos/OSCP-setup

./install.sh --dry-run          # 1) ver qué hará, sin tocar nada
./install.sh                    # 2) perfil oscp (base + AD + web + toolkit)
./install.sh --profile full     # 3) arsenal completo (cracking, sniffing, wireless…)
./verify.sh                     # 4) comprobar (exit 0 = todo listo)

./install.sh --only toolkit-win # una fase suelta
./uninstall.sh --dry-run        # ver la desinstalación
./uninstall.sh                  # deshacer (archivos/pipx/go)
./uninstall.sh --apt --all      # deshacer + quitar paquetes apt + vaciar Tools
```

## Fases

| Fase | Qué hace |
|---|---|
| `preflight` | chequea arch, red, **disco (>25 GB)**, **RAM (>1.5 GB)**, sudo |
| `apt` | paquetes Kali por perfil (verifica existencia, omite inexistentes) |
| `pipx` | bloodyAD, ldeep, uploadserver, pywhisker, pwncat-cs |
| `go` | `go install` de kerbrute + ProjectDiscovery + tools Go (~20) |
| `john` | compila **John the Ripper bleeding-jumbo** (2026) en `Tools/repos/john` + wrapper |
| `kali` | descarga pyLAPS, gMSADumper, targetedKerberoast, PetitPotam, ldapsearch-ad |
| `impacket` | symlinks `.py` en `~/.local/bin` para el playbook |
| `toolkit-linux` | linpeas, pspy, chisel, ligolo-agent, lse, deepce, traitor… (amd64) |
| `toolkit-win` | SharpCollection + releases oficiales (winPEAS, mimikatz, potatoes, Rubeus…) |
| `wordlists` | descomprime rockyou, copia best64.rule |
| `config` | proxychains → `socks5 127.0.0.1 1080`, plantilla krb5 |
| `verify` | corre `verify.sh` |

## Perfiles apt

- **base**: compiladores, python, go, mingw, python3-pwntools…
- **oscp**: AD/Kerberos (nxc, evil-winrm, impacket, certipy, bloodhound, krbrelayx,
  coercer, mitm6), pivoting (chisel, ligolo, proxychains, ncat), web, seclists, wordlists.
- **full**: + hashcat, john, hydra, medusa, patator, wireshark, bettercap, ghidra,
  radare2, binwalk, sleuthkit, aircrack-ng, sshuttle…

## Helper de máquinas

```bash
./new-machine.sh pelican --os linux --ip 10.10.10.20 --tags oscp,htb
# crea ~/Documentos/machines/pelican/{notes.md,nmap,evidence,loot,exploits,transfer}
```

## Notas ARM64

- Los binarios del *toolkit* son **amd64/x86_64** a propósito: se ejecutan en las
  **víctimas**, no en tu Kali.
- **kerbrute** no publica binario arm64 → se compila con Go (`go install`). Es el
  único bloqueo ARM64 y queda resuelto.
- `mingw-w64` (cross-compiler) ya está disponible en arm64.

## Journal / reversibilidad

Cada instalación queda registrada en `state/journal.tsv` (tipo, nombre, detalle).
`uninstall.sh` lo usa para revertir con precisión: no borra lo que no instaló.

## Estado

- `john` compilado bleeding-jumbo (2026) con wrapper en `~/.local/bin/john`.
- Verificación final: `./verify.sh`
- El vault trae su propio chequeo de playbook en `~/Documentos/OSCP/_sistema/herramientas/verificar-entorno.sh`.