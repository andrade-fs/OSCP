#!/usr/bin/env bash
# lib.sh — utilidades comunes para el setup de OSCP.
# Se carga con: source "$(dirname "$0")/lib.sh"

set -o pipefail

SETUP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOCS="${HOME}/Documentos"
VAULT="${DOCS}/OSCP"
TOOLS="${DOCS}/Tools"
LINUX_DIR="${TOOLS}/linux"
WIN_DIR="${TOOLS}/win"
KALI_DIR="${TOOLS}/kali"
REPOS_DIR="${TOOLS}/repos"
STATE="${SETUP_DIR}/state"
LOGS="${SETUP_DIR}/logs"
JOURNAL="${STATE}/journal.tsv"
mkdir -p "$LINUX_DIR" "$WIN_DIR" "$KALI_DIR" "$REPOS_DIR" "$STATE" "$LOGS"

DRY_RUN="${DRY_RUN:-0}"
FORCE="${FORCE:-0}"
PROFILE="${PROFILE:-oscp}"
ASSUME_YES="${ASSUME_YES:-0}"
FAILED=()
SKIPPED=()

if [ -t 1 ]; then
  C_RED=$'\e[91m'; C_GRN=$'\e[92m'; C_YEL=$'\e[93m'; C_BLU=$'\e[94m'; C_DIM=$'\e[90m'; C_RST=$'\e[0m'
else
  C_RED=; C_GRN=; C_YEL=; C_BLU=; C_DIM=; C_RST=
fi

log()  { printf '%s\n' "$*"; }
info() { printf '%s[*]%s %s\n' "$C_BLU" "$C_RST" "$*"; }
ok()   { printf '%s[+]%s %s\n' "$C_GRN" "$C_RST" "$*"; }
warn() { printf '%s[!]%s %s\n' "$C_YEL" "$C_RST" "$*" >&2; }
err()  { printf '%s[x]%s %s\n' "$C_RED" "$C_RST" "$*" >&2; }
die()  { err "$*"; exit 1; }

have_cmd() { command -v "$1" >/dev/null 2>&1; }

run() {
  if [ "$DRY_RUN" = 1 ]; then log "${C_DIM}[dry-run] $*${C_RST}"; return 0; fi
  "$@"
}

if [ "$(id -u)" = 0 ]; then SUDO=""; else SUDO="sudo"; fi
asroot() { if [ -n "$SUDO" ]; then run sudo "$@"; else run "$@"; fi; }

# journal <type> <name> <detail>   (para desinstalación limpia)
journal() {
  [ "$DRY_RUN" = 1 ] && return 0
  printf '%s\t%s\t%s\n' "$1" "$2" "$3" >> "$JOURNAL"
}

arch() { dpkg --print-architecture 2>/dev/null || uname -m; }

# ---------- red ----------
http_get() { # url out
  local url="$1" out="$2" tmp i
  tmp="$(mktemp)"
  for i in 1 2 3; do
    if curl -fL --retry 2 --connect-timeout 15 --max-time 300 -o "$tmp" "$url" 2>/dev/null; then
      mv "$tmp" "$out"; return 0
    fi
    warn "reintento ($i/3): $url"; sleep 2
  done
  rm -f "$tmp"; return 1
}

# fetch_dl <name> <url> <dest> [mode]
fetch_dl() {
  local name="$1" url="$2" dest="$3" mode="${4:-0644}"
  if [ -s "$dest" ] && [ "$FORCE" != 1 ]; then ok "ya existe: $dest"; return 0; fi
  info "descarga: $name"
  if [ "$DRY_RUN" = 1 ]; then log "${C_DIM}[dry-run] curl -fL -o $dest '$url'${C_RST}"; return 0; fi
  mkdir -p "$(dirname "$dest")"
  if http_get "$url" "$dest"; then
    chmod "$mode" "$dest" 2>/dev/null || true
    ok "ok: $dest"; journal file "$name" "$dest"; return 0
  fi
  err "fallo descarga: $url"; FAILED+=("download:$name"); return 1
}

# Resuelve la URL del asset del último release que case con <regex>.
# gh_latest_url <owner/repo> <regex>
gh_latest_url() {
  local repo="$1" re="$2"
  curl -fsSL --max-time 40 "https://api.github.com/repos/${repo}/releases/latest" 2>/dev/null \
  | python3 -c '
import sys, json, re
try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(1)
pat = re.compile(sys.argv[1])
for a in d.get("assets", []):
    if pat.search(a["name"]):
        print(a["browser_download_url"]); break
' "$re"
}

# ---------- descompresión ----------
gunzip_file() { # src tmpdst -> dst
  local src="$1" dst="$2" tmp
  if [ "$DRY_RUN" = 1 ]; then log "${C_DIM}[dry-run] gunzip -c $src > $dst${C_RST}"; return 0; fi
  tmp="$(mktemp)"; gzip -dc "$src" > "$tmp" && mv "$tmp" "$dst"
}
unzip_file() { # src zipentry(outname optional) dst
  local src="$1" entry="$2" dst="$3" tmpd
  if [ "$DRY_RUN" = 1 ]; then log "${C_DIM}[dry-run] unzip $src -> $dst${C_RST}"; return 0; fi
  tmpd="$(mktemp -d)"
  unzip -o -q "$src" -d "$tmpd" || { rm -rf "$tmpd"; return 1; }
  if [ -n "$entry" ] && [ -f "$tmpd/$entry" ]; then
    mv "$tmpd/$entry" "$dst"
  else
    # primer archivo regular
    local f; f="$(find "$tmpd" -type f | head -1)"
    [ -n "$f" ] && mv "$f" "$dst"
  fi
  rm -rf "$tmpd"; [ -s "$dst" ]
}
untargz_file() { # src member(internal name or empty) dst
  local src="$1" member="$2" dst="$3" tmpd
  if [ "$DRY_RUN" = 1 ]; then log "${C_DIM}[dry-run] tar xzf $src -> $dst${C_RST}"; return 0; fi
  tmpd="$(mktemp -d)"
  tar -xzf "$src" -C "$tmpd" || { rm -rf "$tmpd"; return 1; }
  local f
  if [ -n "$member" ]; then f="$tmpd/$member"; else f="$(find "$tmpd" -type f | head -1)"; fi
  [ -f "$f" ] && mv "$f" "$dst"
  rm -rf "$tmpd"; [ -s "$dst" ]
}

# ---------- instaladores ----------
apt_ensure() { # pkg...
  local p present=() missing=() skip=()
  for p in "$@"; do
    if have_cmd "$p" || dpkg -s "$p" >/dev/null 2>&1; then present+=("$p"); continue; fi
    if apt-cache show "$p" >/dev/null 2>&1; then missing+=("$p"); else skip+=("$p"); fi
  done
  [ "${#skip[@]}" -gt 0 ] && warn "no existen en apt (omitidos): ${skip[*]}"
  [ "${#missing[@]}" -eq 0 ] && { ok "apt: todo presente"; return 0; }
  info "apt install: ${missing[*]}"
  if [ "$DRY_RUN" = 1 ]; then log "${C_DIM}[dry-run] sudo apt-get install -y ${missing[*]}${C_RST}"; return 0; fi
  asroot env DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends "${missing[@]}" \
    && { for p in "${missing[@]}"; do journal apt "$p" "$p"; done; ok "apt OK"; } \
    || { err "apt falló con: ${missing[*]}"; FAILED+=("apt:${missing[*]}"); return 1; }
}

pipx_ensure() { # pkg...
  have_cmd pipx || { warn "pipx no instalado; salto pipx"; return 1; }
  local p
  for p in "$@"; do
    if pipx list --short 2>/dev/null | grep -q "^${p%%.*}\b"; then ok "pipx ya: $p"; continue; fi
    info "pipx install: $p"
    if [ "$DRY_RUN" = 1 ]; then log "${C_DIM}[dry-run] pipx install $p${C_RST}"; continue; fi
    if pipx install --force "$p" >/dev/null 2>&1; then ok "pipx OK: $p"; journal pipx "$p" "$p"
    else warn "pipx falló: $p"; SKIPPED+=("pipx:$p"); fi
  done
}

go_ensure() { # module@version ...
  have_cmd go || { warn "go no instalado; salto go"; return 1; }
  local m bin
  export GOBIN="${HOME}/.local/bin"
  mkdir -p "$GOBIN"
  for m in "$@"; do
    local full="${m%@*}"
    bin="${full##*/}"
    if [[ "$bin" =~ ^v[0-9]+$ ]]; then bin="${full%/*}"; bin="${bin##*/}"; fi
    if have_cmd "$bin"; then ok "go ya: $bin"; continue; fi
    info "go install: $m"
    if [ "$DRY_RUN" = 1 ]; then log "${C_DIM}[dry-run] GOBIN=$GOBIN go install $m${C_RST}"; continue; fi
    if GOBIN="$GOBIN" GOFLAGS=-mod=mod go install "$m" >/dev/null 2>&1; then
      ok "go OK: $bin"; journal gocmd "$bin" "$m"
    else
      warn "go falló: $m"; SKIPPED+=("go:$m")
    fi
  done
}

summary() {
  printf '\n%s==================== RESUMEN ====================%s\n' "$C_BLU" "$C_RST"
  if [ "${#FAILED[@]}" -gt 0 ]; then
    err "FALLOS (${#FAILED[@]}):"; printf '   - %s\n' "${FAILED[@]}"
  else ok "Sin fallos."; fi
  if [ "${#SKIPPED[@]}" -gt 0 ]; then
    warn "omitidos (${#SKIPPED[@]}):"; printf '   - %s\n' "${SKIPPED[@]}"
  fi
  [ "${#FAILED[@]}" -eq 0 ]
}