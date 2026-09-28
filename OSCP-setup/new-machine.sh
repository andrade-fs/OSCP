#!/usr/bin/env bash
# new-machine.sh — crea una subcarpeta estandarizada por máquina en ~/Documentos/machines
#
#   ./new-machine.sh pelican
#   ./new-machine.sh dc01 --os windows --ip 10.10.10.5
#   ./new-machine.sh dev01 --os linux --ip 10.10.10.20 --tags "oscp,htb"
#
# Estructura creada:
#   machines/<nombre>/
#     ├── notes.md          # bitácora (plantilla lista)
#     ├── nmap/             # escaneos y grepeables
#     ├── evidence/         # capturas (screens para el reporte)
#     ├── loot/             # hashes, creds, tickets, flags
#     ├── exploits/         # PoCs y scripts propios
#     └── transfer/         # lo que sirves a la víctima (http/smb)
#
set -euo pipefail

NAME="${1:-}"
[ -z "$NAME" ] && { echo "Uso: $0 <nombre> [--os linux|windows|ad] [--ip IP] [--tags ...]"; exit 1; }
shift || true
OS=""; IP=""; TAGS=""
while [ $# -gt 0 ]; do
  case "$1" in
    --os) OS="$2"; shift ;;
    --ip) IP="$2"; shift ;;
    --tags) TAGS="$2"; shift ;;
    *) echo "Opción desconocida: $1"; exit 1 ;;
  esac
  shift
done

BASE="${HOME}/Documentos/machines/${NAME}"
if [ -d "$BASE" ]; then
  echo "[!] Ya existe: $BASE"
  exit 0
fi

mkdir -p "$BASE"/{nmap,evidence,loot,exploits,transfer}

cat > "$BASE/notes.md" <<EOF
# ${NAME}

- **IP:** ${IP:-<pendiente>}
- **OS:** ${OS:-<pendiente>}
- **Tags:** ${TAGS:-oscp}
- **Fecha inicio:** $(date +%F)
- **Estado:** 🟡 en progreso

---

## 1. Reconocimiento

\`\`\`
# nmap/scan.txt  (guardar salidas aquí)
\`\`\`

## 2. Enumeración por servicio

| Puerto | Servicio | Notas |
|--------|----------|-------|
|        |          |       |

## 3. Foothold

## 4. Escalada de privilegios

## 5. Post-explotación / loot

- [ ] user flag
- [ ] root/SYSTEM flag

## 6. Lecciones / técnicas usadas

\`\`\`
# comando clave 1
\`\`\`
EOF

cat > "$BASE/nmap/README.txt" <<'EOF'
Guarda aquí los escaneos. Convención sugerida:
  scan-inicial.txt      nmap -sC -sV -p- --min-rate 2000 -oN ...
  scan-udp.txt
  grepeable.txt         nmap -oG ...
EOF

cat > "$BASE/loot/.gitkeep" <<'EOF'
EOF
cat > "$BASE/evidence/.gitkeep" <<'EOF'
EOF
cat > "$BASE/exploits/.gitkeep" <<'EOF'
EOF
cat > "$BASE/transfer/.gitkeep" <<'EOF'
EOF

echo "[+] Creada: $BASE"
find "$BASE" -maxdepth 1 -mindepth 1 | sort | sed "s#${HOME}#~#"