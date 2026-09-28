#!/usr/bin/env bash
# install.sh — instalador del arsenal OSCP. Idempotente y con journal para desinstalar.
#
#   ./install.sh --dry-run                 # muestra todo sin tocar nada
#   ./install.sh                           # perfil oscp (base+oscp)
#   ./install.sh --profile full            # arsenal completo
#   ./install.sh --only apt                # una sola fase
#   ./install.sh --force                   # re-descarga lo existente
#
set -o pipefail
SETUP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
source "${SETUP_DIR}/lib.sh"

ONLY=""
NO_VERIFY=0
usage() {
  cat <<EOF
Uso: ./install.sh [opciones]
  --profile base|oscp|full   Perfil de paquetes apt (def: oscp)
  --only <fase>              Ejecuta solo una fase:
                             preflight apt pipx go john kali impacket toolkit-linux
                             toolkit-win wordlists config verify
  --dry-run                  No ejecuta cambios, solo muestra
  --force                    Re-descarga/reinstala lo ya existente
  -y, --yes                  No preguntar
  --no-verify                No correr verify.sh al final
  -h, --help
Fases disponibles: preflight apt pipx go john kali impacket toolkit-linux toolkit-win wordlists config verify
EOF
}

while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY_RUN=1 ;;
    --force) FORCE=1 ;;
    --profile) PROFILE="$2"; shift ;;
    --profile=*) PROFILE="${1#*=}" ;;
    --only) ONLY="$2"; shift ;;
    --only=*) ONLY="${1#*=}" ;;
    -y|--yes) ASSUME_YES=1 ;;
    --no-verify) NO_VERIFY=1 ;;
    -h|--help) usage; exit 0 ;;
    *) die "Opción desconocida: $1 (usa --help)" ;;
  esac
  shift
done

case "$PROFILE" in base|oscp|full) ;; *) die "perfil inválido: $PROFILE" ;; esac

# ---------- helpers de manifest ----------
apt_packages_for_profile() {
  awk -v want="$1" '
    /^\[/ { gsub(/[\[\]]/,"",$0); sec=$0; next }
    /^[[:space:]]*#/ || /^[[:space:]]*$/ { next }
    {
      if (sec=="base") print;
      else if ((want=="oscp"||want=="full") && sec=="oscp") print;
      else if (want=="full" && sec=="full") print;
    }
  ' "${SETUP_DIR}/manifest/apt.list" | tr '\n' ' '
}

# ---------- fases ----------
phase_preflight() {
  local a; a="$(arch)"
  info "Arquitectura: $a | Perfil: $PROFILE | Dry-run: $DRY_RUN"
  [ "$a" = "arm64" ] && warn "ARM64: kerbrute se compilará con Go; binarios de víctima serán amd64 (correcto)."
  # red
  if ! curl -fsS --max-time 15 -o /dev/null https://api.github.com; then
    die "Sin conectividad a GitHub. Abortando."
  fi
  ok "Conectividad GitHub OK"
  # disco
  local free_gb; free_gb=$(df -Pk / | awk 'NR==2{printf "%d", $4/1024/1024}')
  info "Disco libre: ${free_gb} GB (mínimo exigido: 25 GB)"
  [ "$free_gb" -lt 25 ] && die "Disco insuficiente (<25 GB). Libera espacio."
  # ram
  local avail_mb; avail_mb=$(awk '/MemAvailable/{printf "%d",$2/1024}' /proc/meminfo)
  info "RAM disponible: ${avail_mb} MB (mínimo exigido: 1500 MB)"
  [ "$avail_mb" -lt 1500 ] && die "RAM insuficiente (<1.5 GB). Cierra aplicaciones."
  # sudo
  if [ "$(id -u)" != 0 ]; then
    if sudo -n true 2>/dev/null; then ok "sudo sin contraseña"
    else warn "sudo pedirá contraseña al instalar paquetes."; fi
  fi
  warn "RECOMENDADO: toma un snapshot de la VM antes de continuar."
  ok "Preflight OK"
}

phase_apt() {
  local pkgs; pkgs=$(apt_packages_for_profile "$PROFILE")
  info "apt update"
  asroot env DEBIAN_FRONTEND=noninteractive apt-get update -y || warn "apt update falló"
  # shellcheck disable=SC2086
  apt_ensure $pkgs
}

phase_pipx() {
  local p
  while IFS= read -r p || [ -n "$p" ]; do
    [ -z "$p" ] || [[ "$p" == \#* ]] && continue
    pipx_ensure "$p"
  done < "${SETUP_DIR}/manifest/pipx.list"
  # uploadserver: el playbook usa `python3 -m uploadserver` -> python del usuario
  if python3 -c "import uploadserver" >/dev/null 2>&1; then
    ok "uploadserver (módulo py) ya presente"
  else
    info "pip3 --user uploadserver"
    if [ "$DRY_RUN" = 1 ]; then
      log "${C_DIM}[dry-run] pip3 install --user --break-system-packages uploadserver${C_RST}"
    elif pip3 install --user --break-system-packages uploadserver >/dev/null 2>&1; then
      ok "uploadserver py OK"; journal pip uploadserver uploadserver
    else
      warn "uploadserver py falló"; SKIPPED+=("pip:uploadserver")
    fi
  fi
}

phase_go() {
  local m mods=()
  while IFS= read -r m || [ -n "$m" ]; do
    [ -z "$m" ] || [[ "$m" == \#* ]] && continue
    mods+=("$m")
  done < "${SETUP_DIR}/manifest/go.list"
  # kerbrute es Go puro (resuelve el único bloqueo ARM64)
  go_ensure "${mods[@]}"
  # httpx de ProjectDiscovery: /usr/bin/httpx es el de Python, hay que forzar el de PD
  if have_cmd go && [ -x "${HOME}/.local/bin/httpx" ] && "${HOME}/.local/bin/httpx" -version >/dev/null 2>&1; then
    ok "httpx ProjectDiscovery ya presente"
  else
    info "instalando httpx de ProjectDiscovery (colisiona con el de Python)"
    if [ "$DRY_RUN" = 1 ]; then
      log "${C_DIM}[dry-run] GOBIN=~/.local/bin go install github.com/projectdiscovery/httpx/cmd/httpx@latest${C_RST}"
    elif GOBIN="${HOME}/.local/bin" GOFLAGS=-mod=mod go install github.com/projectdiscovery/httpx/cmd/httpx@latest >/dev/null 2>&1; then
      ok "httpx PD OK"; journal gocmd httpx github.com/projectdiscovery/httpx/cmd/httpx@latest
    else
      warn "httpx PD falló"; SKIPPED+=("go:httpx-pd")
    fi
  fi
}

phase_john() {
  local src="${REPOS_DIR}/john"
  if [ -x "${src}/run/john" ] && [ "$FORCE" != 1 ]; then
    ok "john bleeding-jumbo ya compilado"
    if [ "$DRY_RUN" != 1 ]; then
      printf '#!/bin/sh\nexec %s/run/john "$@"\n' "$src" > "${HOME}/.local/bin/john"
      chmod +x "${HOME}/.local/bin/john"
    fi
    return 0
  fi
  apt_ensure libpcap-dev libbz2-dev libgmp-dev libssl-dev zlib1g-dev
  info "clonando/actualizando John the Ripper bleeding-jumbo"
  if [ "$DRY_RUN" = 1 ]; then
    log "${C_DIM}[dry-run] git clone -b bleeding-jumbo https://github.com/openwall/john ${src}${C_RST}"
    log "${C_DIM}[dry-run] (cd ${src}/src && ./configure && make -sj$(nproc))${C_RST}"
    return 0
  fi
  if [ ! -d "$src/.git" ]; then
    git clone --depth 1 -b bleeding-jumbo https://github.com/openwall/john "$src" >/dev/null 2>&1 \
      || { err "clone john falló"; FAILED+=("john:clone"); return 1; }
  else
    git -C "$src" pull --ff-only >/dev/null 2>&1 || true
  fi
  info "compilando john (puede tardar varios minutos, -j$(nproc))"
  if ( cd "$src/src" && ./configure >/tmp/john-configure.log 2>&1 && make -s clean >/dev/null 2>&1 && make -sj"$(nproc)" >/tmp/john-make.log 2>&1 ); then
    if [ -x "${src}/run/john" ]; then
      printf '#!/bin/sh\nexec %s/run/john "$@"\n' "$src" > "${HOME}/.local/bin/john"
      chmod +x "${HOME}/.local/bin/john"
    fi
    ok "john compilado: $("${HOME}/.local/bin/john" --list=build-info 2>/dev/null | grep -m1 'Version:')"
    journal dir john "$src"; journal file john "${HOME}/.local/bin/john"
  else
    err "compilación de john falló (ver /tmp/john-configure.log, /tmp/john-make.log)"; FAILED+=("john:build")
  fi
}

phase_kali() {
  local line name url dest mode
  while IFS='|' read -r name url dest mode || [ -n "$name" ]; do
    [ -z "$name" ] || [[ "$name" == \#* ]] && continue
    fetch_dl "$name" "$url" "${KALI_DIR}/${dest}" "${mode:-0755}" || true
    if [ "$DRY_RUN" != 1 ]; then
      ln -sf "${KALI_DIR}/${dest}" "${HOME}/.local/bin/${dest}" 2>/dev/null || true
    fi
  done < "${SETUP_DIR}/manifest/github.kali.txt"
}

phase_impacket() {
  info "Symlinks impacket .py -> ~/.local/bin"
  local ex=" /usr/share/doc/python3-impacket/examples"
  [ -d "$ex" ] || ex="/usr/share/doc/python3-impacket/examples"
  if [ ! -d "$ex" ]; then warn "no existe $ex; ¿impacket instalado?"; return 0; fi
  local f b base
  for f in "$ex"/*.py; do
    [ -e "$f" ] || continue
    b="$(basename "$f")"; base="${b%.py}"
    if [ "$DRY_RUN" = 1 ]; then log "${C_DIM}[dry-run] ln -sf $f ~/.local/bin/$b${C_RST}"; continue; fi
    ln -sf "$f" "${HOME}/.local/bin/$b"
    [ -e "${HOME}/.local/bin/$b" ] && journal symlink "$b" "${HOME}/.local/bin/$b"
  done
  ok "impacket links listos"
}

phase_toolkit_linux() {
  local name url dest how mode line
  while IFS='|' read -r name url dest how mode || [ -n "$name" ]; do
    [ -z "$name" ] || [[ "$name" == \#* ]] && continue
    dest="${LINUX_DIR}/${dest}"; mode="${mode:-0755}"
    if [ -s "$dest" ] && [ "$FORCE" != 1 ]; then ok "ya existe: $dest"; continue; fi
    if [[ "$url" == LATEST:* ]]; then
      IFS=':' read -r _ repo re <<< "$url"
      url="$(gh_latest_url "$repo" "$re")"
      [ -z "$url" ] && { err "no asset para $name ($repo / $re)"; FAILED+=("linux:$name"); continue; }
    fi
    info "linux toolkit: $name"
    if [ "$DRY_RUN" = 1 ]; then log "${C_DIM}[dry-run] $name <- $url ($how)${C_RST}"; continue; fi
    case "$how" in
      raw)  fetch_dl "$name" "$url" "$dest" "$mode" || continue ;;
      gz)   local t; t="$(mktemp)"; http_get "$url" "$t" && gunzip_file "$t" "$dest"; rm -f "$t" ;;
      targz:*) local t; t="$(mktemp)"; http_get "$url" "$t" && untargz_file "$t" "${how#targz:}" "$dest"; rm -f "$t" ;;
      *)    warn "how desconocido: $how" ;;
    esac
    [ -s "$dest" ] && chmod "$mode" "$dest" 2>/dev/null
    [ -s "$dest" ] && { ok "ok: $dest"; journal file "$name" "$dest"; } || { err "fallo: $name"; FAILED+=("linux:$name"); }
  done < "${SETUP_DIR}/manifest/github.linux.txt"
}

phase_toolkit_win() {
  # 1) SharpCollection (una sola fuente cubre la mayoría)
  local sc="${REPOS_DIR}/SharpCollection"
  if [ ! -d "$sc/.git" ]; then
    info "clonando SharpCollection"
    if [ "$DRY_RUN" != 1 ]; then
      git clone --depth 1 https://github.com/Flangvik/SharpCollection "$sc" >/dev/null 2>&1 \
        || { err "no se pudo clonar SharpCollection"; FAILED+=("win:SharpCollection"); }
    else log "${C_DIM}[dry-run] git clone SharpCollection${C_RST}"; fi
  else
    run git -C "$sc" pull --ff-only >/dev/null 2>&1 || true
  fi
  if [ -d "$sc/NetFramework_4.7_x64" ]; then
    local f
    while IFS= read -r f || [ -n "$f" ]; do
      [ -z "$f" ] || [[ "$f" == \#* ]] && continue
      if [ "$DRY_RUN" = 1 ]; then continue; fi
      [ -f "$sc/NetFramework_4.7_x64/$f" ] && cp -f "$sc/NetFramework_4.7_x64/$f" "${WIN_DIR}/$f" && ok "win: $f"
    done < "${SETUP_DIR}/manifest/collection.win.txt"
  fi
  # 2) descargas oficiales
  local name url how line
  while IFS='|' read -r name url how || [ -n "$name" ]; do
    [ -z "$name" ] || [[ "$name" == \#* ]] && continue
    local dest="${WIN_DIR}/${name}"
    if [ -s "$dest" ] && [ "$FORCE" != 1 ]; then ok "ya existe: $dest"; continue; fi
    if [[ "$url" == LATEST:* ]]; then
      IFS=':' read -r _ repo re <<< "$url"; url="$(gh_latest_url "$repo" "$re")"
      [ -z "$url" ] && { err "no asset $name"; FAILED+=("win:$name"); continue; }
    fi
    info "win toolkit: $name"
    if [ "$DRY_RUN" = 1 ]; then log "${C_DIM}[dry-run] $name <- $url ($how)${C_RST}"; continue; fi
    local t; t="$(mktemp)"
    case "$how" in
      raw)     fetch_dl "$name" "$url" "$dest" 0644 || true ;;
      zip:any) if http_get "$url" "$t"; then unzip_file "$t" "" "$dest"; fi ;;
      zip:*)   if http_get "$url" "$t"; then unzip_file "$t" "${how#zip:}" "$dest"; fi ;;
      zipdir)  if http_get "$url" "$t"; then run unzip -o -q "$t" -d "${WIN_DIR}/${name}"; fi ;;
    esac
    rm -f "$t"
    if [ -s "$dest" ] 2>/dev/null; then ok "ok: $dest"; journal file "$name" "$dest"
    elif [ "$how" = zipdir ] && [ -d "${WIN_DIR}/${name}" ]; then ok "ok dir: ${WIN_DIR}/${name}"; journal dir "$name" "${WIN_DIR}/${name}"
    else err "fallo: $name"; FAILED+=("win:$name"); fi
  done < "${SETUP_DIR}/manifest/github.win.txt"
}

phase_wordlists() {
  # rockyou descomprimido
  if [ ! -s /usr/share/wordlists/rockyou.txt ] && [ -s /usr/share/wordlists/rockyou.txt.gz ]; then
    info "descomprimiendo rockyou"
    asroot gunzip -kf /usr/share/wordlists/rockyou.txt.gz || warn "gunzip rockyou falló"
  fi
  # best64 para hashcat (viene en john)
  if [ ! -s /usr/share/hashcat/rules/best64.rule ]; then
    local src; src="$(find /usr/share/john /usr/share/hashcat -name 'best64.rule' 2>/dev/null | head -1)"
    if [ -n "$src" ]; then info "copiando best64.rule"; asroot cp -f "$src" /usr/share/hashcat/rules/best64.rule
    else warn "no se encontró best64.rule"; fi
  fi
  ok "wordlists fase lista"
}

phase_config() {
  # proxychains -> SOCKS5 local del túnel
  local cfg=/etc/proxychains4.conf
  if [ -f "$cfg" ]; then
    if grep -qE '^\s*socks5\s+127\.0\.0\.1\s+1080' "$cfg" 2>/dev/null; then
      ok "proxychains ya apunta a socks5 127.0.0.1:1080"
    else
      info "configurando proxychains"
      asroot cp -n "$cfg" "${cfg}.bak-$(date +%Y%m%d)" 2>/dev/null || true
      if grep -q '^\[ProxyList\]' "$cfg"; then
        if [ "$DRY_RUN" != 1 ]; then
          # reemplaza la línea del ProxyList (siguiente a la cabecera) por el socks5
          asroot sed -i '/^\[ProxyList\]/,/^$/ s/^\s*#\?\s*socks[45].*$//' "$cfg" 2>/dev/null || true
          printf 'socks5 127.0.0.1 1080\n' | asroot tee -a "$cfg" >/dev/null
        fi
        ok "proxychains configurado (backup .bak-*)"
      fi
    fi
  fi
  # plantilla krb5 en Tools (NO se toca /etc/krb5.conf: es por dominio)
  if [ "$DRY_RUN" != 1 ]; then
  mkdir -p "${TOOLS}/plantillas"
  cat > "${TOOLS}/plantillas/krb5.conf.plantilla" <<'K'
[libdefaults]
    default_realm = DOMINIO.LOCAL
    dns_lookup_realm = false
    dns_lookup_kdc = false
    rdns = false
    dns_canonicalize_hostname = false
    ticket_lifetime = 24h
    forwardable = true
    udp_preference_limit = 0
[realms]
    DOMINIO.LOCAL = {
        kdc = dc01.dominio.local
        admin_server = dc01.dominio.local
        default_domain = dominio.local
    }
[domain_realm]
    .dominio.local = DOMINIO.LOCAL
    dominio.local = DOMINIO.LOCAL
K
  fi
  ok "plantilla krb5 en ${TOOLS}/plantillas/"
}

phase_verify() {
  [ "$NO_VERIFY" = 1 ] && return 0
  if [ -x "${SETUP_DIR}/verify.sh" ]; then
    info "ejecutando verify.sh"
    bash "${SETUP_DIR}/verify.sh" || warn "verify reportó fallos (revisar arriba)"
  fi
}

# ---------- runner ----------
run_phase() {
  local name="$1" fn="$2"
  if [ -n "$ONLY" ] && [ "$ONLY" != "$name" ]; then return 0; fi
  printf '\n%s========== FASE: %s ==========%s\n' "$C_BLU" "$name" "$C_RST"
  "$fn"
}

mkdir -p "$STATE" "$LOGS"
{
  run_phase preflight   phase_preflight
  run_phase apt         phase_apt
  run_phase pipx        phase_pipx
  run_phase go          phase_go
  run_phase john        phase_john
  run_phase kali        phase_kali
  run_phase impacket    phase_impacket
  run_phase toolkit-linux phase_toolkit_linux
  run_phase toolkit-win phase_toolkit_win
  run_phase wordlists   phase_wordlists
  run_phase config      phase_config
  run_phase verify      phase_verify
} 2>&1 | tee -a "${LOGS}/install-$(date +%Y%m%d-%H%M%S).log"

summary
exit $?