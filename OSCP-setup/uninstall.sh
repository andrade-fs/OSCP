#!/usr/bin/env bash
# uninstall.sh — revierte lo que install.sh registró en state/journal.tsv.
#
#   ./uninstall.sh --dry-run        # muestra qué haría
#   ./uninstall.sh                  # borra archivos, symlinks, pipx y bins go
#   ./uninstall.sh --apt            # además: apt remove de paquetes instalados
#   ./uninstall.sh --all            # además: limpia los directorios de Tools
#   ./uninstall.sh --reset-journal  # vacía el journal al terminar
#
SETUP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
source "${SETUP_DIR}/lib.sh"

ALL=0; WITH_APT=0; RESET=0
while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY_RUN=1 ;;
    --apt) WITH_APT=1 ;;
    --all) ALL=1 ;;
    --reset-journal) RESET=1 ;;
    -h|--help) sed -n '2,12p' "$0"; exit 0 ;;
    *) die "Opción desconocida: $1" ;;
  esac
  shift
done

[ -f "$JOURNAL" ] || { warn "No hay journal ($JOURNAL). Nada que desinstalar."; exit 0; }

info "Desinstalando desde $JOURNAL (dry-run=$DRY_RUN)"
apt_pkgs=(); pipx_pkgs=(); pip_pkgs=(); go_bins=(); paths=()

while IFS=$'\t' read -r type name detail; do
  case "$type" in
    apt)     apt_pkgs+=("$name") ;;
    pipx)    pipx_pkgs+=("$name") ;;
    pip)     pip_pkgs+=("$name") ;;
    gocmd)   go_bins+=("$name") ;;
    file|dir|symlink) paths+=("$detail") ;;
  esac
done < "$JOURNAL"

# dedup de rutas (fetch + fase pueden registrar lo mismo)
if [ "${#paths[@]}" -gt 0 ]; then
  mapfile -t paths < <(printf '%s\n' "${paths[@]}" | sort -u)
fi

# 1) quitar archivos/symlinks/carpetas registradas
for p in "${paths[@]}"; do
  [ -e "$p" ] || [ -L "$p" ] || continue
  info "rm: $p"; run rm -rf "$p"
done

# 2) bins de go
for b in "${go_bins[@]}"; do
  [ -e "${HOME}/.local/bin/$b" ] || continue
  info "rm go bin: $b"; run rm -f "${HOME}/.local/bin/$b"
done

# 3) pipx
if [ "${#pipx_pkgs[@]}" -gt 0 ] && have_cmd pipx; then
  for p in "${pipx_pkgs[@]}"; do
    info "pipx uninstall: $p"; run pipx uninstall "$p" >/dev/null 2>&1 || true
  done
fi

# 3b) pip del usuario
if [ "${#pip_pkgs[@]}" -gt 0 ] && have_cmd pip3; then
  for p in "${pip_pkgs[@]}"; do
    info "pip uninstall: $p"; run pip3 uninstall -y --break-system-packages "$p" >/dev/null 2>&1 || true
  done
fi

# 4) restaurar proxychains
if ls /etc/proxychains4.conf.bak-* >/dev/null 2>&1; then
  lastbak="$(ls -1t /etc/proxychains4.conf.bak-* 2>/dev/null | head -1)"
  info "restaurando proxychains desde $lastbak"; asroot cp -f "$lastbak" /etc/proxychains4.conf
fi

# 5) apt (opt-in)
if [ "$WITH_APT" = 1 ] && [ "${#apt_pkgs[@]}" -gt 0 ]; then
  # dedup
  mapfile -t apt_pkgs < <(printf '%s\n' "${apt_pkgs[@]}" | sort -u)
  warn "Se van a desinstalar paquetes apt: ${apt_pkgs[*]}"
  info "apt remove --purge"; asroot env DEBIAN_FRONTEND=noninteractive apt-get remove -y --purge "${apt_pkgs[@]}" || true
  info "apt autoremove"; asroot env DEBIAN_FRONTEND=noninteractive apt-get autoremove -y || true
fi

# 6) limpiar Tools (opt-in)
if [ "$ALL" = 1 ]; then
  for d in "$KALI_DIR" "$LINUX_DIR" "$WIN_DIR" "$REPOS_DIR"; do
    info "limpiando: $d"; run rm -rf "${d:?}"/* 2>/dev/null || true
  done
fi

# 7) journal
if [ "$RESET" = 1 ]; then
  info "vaciando journal"; [ "$DRY_RUN" = 1 ] || : > "$JOURNAL"
fi

ok "Desinstalación terminada."
[ "$WITH_APT" = 1 ] || info "Los paquetes apt NO se tocaron (usa --apt para quitarlos)."