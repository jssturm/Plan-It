#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────────────
# Plan-It — Cross-Platform Install Script
#
# Supports: macOS, Linux (Ubuntu/Debian/Fedora/Arch), WSL, Android (Termux),
#           iOS (iSH)
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/jssturm/Plan-It/main/install.sh | bash
#   bash install.sh --quick   — non-interactive
#   bash install.sh --force   — reinstall
#   bash install.sh --dry-run — validate without installing
#
# What this does:
#   1. Detects the OS and validates baseline requirements (Python 3.12+)
#   2. Creates/extends a Python virtual environment
#   3. Installs the plan-it package from PyPI (with GitHub fallback)
#   4. Bootstraps a .env configuration file
#   5. Registers the 'plan-it' CLI command
#   6. Optionally sets up a systemd/launchd service for auto-start
# ──────────────────────────────────────────────────────────────────────────────

set -euo pipefail

# ── Colour Helpers ───────────────────────────────────────────────────────────
if [ -t 1 ] && command -v tput &>/dev/null && [ "$(tput colors 2>/dev/null || echo 0)" -ge 8 ]; then
  RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
  CYAN='\033[0;36m'; BOLD='\033[1m'; DIM='\033[2m'; NC='\033[0m'
else
  RED=''; GREEN=''; YELLOW=''; CYAN=''; BOLD=''; DIM=''; NC=''
fi

log_info()  { printf "${GREEN}[plan-it]${NC} %s\n" "$*"; }
log_warn()  { printf "${YELLOW}[plan-it]${NC} %s\n" "$*"; }
log_error() { printf "${RED}[plan-it]${NC} %s\n" "$*"; }
log_step()  { printf "${CYAN}→${NC} %s\n" "$*"; }
banner()    { printf "\n${BOLD}%s${NC}\n" "$*"; }
fail()      { log_error "$@"; exit 1; }

# ── Globals ──────────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
VERSION="0.3.0"
GITHUB_REPO="jssturm/Plan-It"
GITHUB_TARBALL="https://github.com/${GITHUB_REPO}/archive/refs/heads/main.tar.gz"
VENV_DIR="${TRAVEL_VENV:-$HOME/.local/share/plan-it/venv}"
CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/plan-it"
INSTALL_MARKER="$CONFIG_DIR/.installed"
TEMP_DIR=""
QUICK_MODE=false; FORCE_MODE=false; INSTALL_FROM_SOURCE=false; DRY_RUN=false
MAX_RETRIES=3; RETRY_DELAY=2

# ── Argument Parsing ─────────────────────────────────────────────────────────
for arg in "$@"; do
  case "$arg" in
    --quick)  QUICK_MODE=true ;;
    --force)  FORCE_MODE=true ;;
    --source) INSTALL_FROM_SOURCE=true ;;
    --dry-run) DRY_RUN=true ;;
    --help|-h)
      echo "Usage: bash install.sh [OPTIONS]"
      echo "  --quick    Non-interactive with defaults"
      echo "  --force    Force re-install even if already configured"
      echo "  --source   Install from local source instead of PyPI"
      echo "  --dry-run  Validate environment without installing"
      exit 0 ;;
  esac
done

# ── Cleanup ───────────────────────────────────────────────────────────────────
cleanup() { [ -n "$TEMP_DIR" ] && [ -d "$TEMP_DIR" ] && rm -rf "$TEMP_DIR" 2>/dev/null || true; }
trap cleanup EXIT

# ── Network retry helper ──────────────────────────────────────────────────────
download_with_retry() {
  local url="$1"; local output="${2:-}"; local attempt=1
  while [ $attempt -le $MAX_RETRIES ]; do
    if [ -n "$output" ]; then
      curl -fsSL --connect-timeout 15 --max-time 60 "$url" -o "$output" 2>/dev/null && return 0
    else
      curl -fsSL --connect-timeout 15 --max-time 60 "$url" 2>/dev/null && return 0
    fi
    log_warn "  Download attempt $attempt/$MAX_RETRIES failed — retrying in ${RETRY_DELAY}s..."
    sleep "$RETRY_DELAY"
    RETRY_DELAY=$((RETRY_DELAY * 2))
    attempt=$((attempt + 1))
  done
  return 1
}

# ── OS Detection ─────────────────────────────────────────────────────────────
detect_os() {
  local os="$(uname -s)"; local arch="$(uname -m)"
  case "$os" in
    Darwin)  DETECTED_OS="macos"  ;;
    Linux)
      if [ -n "${ANDROID_ROOT:-}" ] || [ -d /data/data/com.termux ]; then DETECTED_OS="android"
      elif [ -d /proc/ish ]; then DETECTED_OS="ios"
      elif grep -qi microsoft /proc/version 2>/dev/null; then DETECTED_OS="wsl"
      else DETECTED_OS="linux"; fi ;;
    *)       DETECTED_OS="unknown" ;;
  esac
  DETECTED_ARCH="$arch"
  log_info "Detected: ${DETECTED_OS} (${DETECTED_ARCH})"
}

# ── Validate Environment ─────────────────────────────────────────────────────
validate_env() {
  log_step "Validating environment..."

  # Python 3
  PYTHON_CMD=""
  for cmd in python3.13 python3.12 python3 python; do
    if command -v "$cmd" &>/dev/null; then
      local ver; ver=$("$cmd" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null || echo "0.0")
      local major; major=$(echo "$ver" | cut -d. -f1)
      local minor; minor=$(echo "$ver" | cut -d. -f2)
      if [ "$major" -ge 3 ] && [ "$minor" -ge 12 ]; then PYTHON_CMD="$cmd"; break; fi
    fi
  done

  if [ -z "$PYTHON_CMD" ]; then
    fail "Python 3.12+ is required but was not found."
  fi
  log_info "  ✓ $PYTHON_CMD ($($PYTHON_CMD --version))"

  # pip
  if ! $PYTHON_CMD -m pip --version &>/dev/null; then
    fail "pip is required but not found for $PYTHON_CMD."
  fi
  local pip_ver; pip_ver=$($PYTHON_CMD -m pip --version | awk '{print $2}')
  log_info "  ✓ pip $pip_ver"

  # curl (needed for pip installs and GitHub fallback)
  if ! command -v curl &>/dev/null; then
    log_warn "  ⚠ curl not found — PyPI install will still work, but GitHub fallback won't"
  else
    log_info "  ✓ curl available"
  fi

  # Disk space (at least 200 MB free)
  local free_mb; free_mb=$(df -m "$HOME" 2>/dev/null | awk 'NR==2{print $4}' || echo "0")
  if [ "$free_mb" -lt 200 ] 2>/dev/null; then
    log_warn "  ⚠ Less than 200 MB free disk space ($free_mb MB). Installation may fail."
  else
    log_info "  ✓ Disk space: ~${free_mb} MB free"
  fi

  # Platform-specific
  case "$DETECTED_OS" in
    android) [ ! -d /data/data/com.termux ] && log_warn "Termux not confirmed — install from F-Droid." ;;
    ios) log_info "  ℹ iSH users: server runs locally. Open Safari to http://127.0.0.1:8000" ;;
    wsl) log_info "  ℹ WSL detected. Access from Windows at http://localhost:8000" ;;
  esac
}

# ── Create Virtual Environment ───────────────────────────────────────────────
setup_venv() {
  if [ "$FORCE_MODE" = true ] && [ -d "$VENV_DIR" ]; then
    log_step "Removing existing virtual environment (--force)..."
    rm -rf "$VENV_DIR"
  fi

  if [ -d "$VENV_DIR" ] && [ -f "$VENV_DIR/bin/activate" ]; then
    log_info "  ✓ Virtual environment exists: $VENV_DIR"
  else
    log_step "Creating virtual environment at $VENV_DIR..."
    $PYTHON_CMD -m venv "$VENV_DIR"
    log_info "  ✓ Virtual environment created"
  fi

  # shellcheck disable=SC1090
  source "$VENV_DIR/bin/activate"
  log_info "  ✓ Activated $(python --version)"
  pip install --upgrade pip --quiet
}

# ── Install Package ──────────────────────────────────────────────────────────
install_package() {
  log_step "Installing plan-it v${VERSION}..."

  if [ "$INSTALL_FROM_SOURCE" = true ]; then
    log_info "  Installing from local source: $SCRIPT_DIR"
    pip install "$SCRIPT_DIR" --quiet || fail "Local source install failed."
  else
    # Primary: PyPI
    log_info "  Installing from PyPI..."
    if pip install "plan-it>=${VERSION}" --quiet 2>/dev/null; then
      log_info "  ✓ Installed via PyPI"
    else
      log_warn "  PyPI install failed — falling back to GitHub source..."

      # Fallback 1: local source (if running from repo directory)
      if [ -f "$SCRIPT_DIR/pyproject.toml" ]; then
        log_info "  Installing from local source: $SCRIPT_DIR"
        pip install "$SCRIPT_DIR" --quiet || fail "Local source install failed."
      else
        # Fallback 2: download from GitHub
        if ! command -v curl &>/dev/null; then
          fail "PyPI install failed and curl is not available for GitHub fallback."
        fi
        TEMP_DIR="$(mktemp -d 2>/dev/null || mktemp -d -t 'plan-it-sdk')"
        log_info "  Downloading from GitHub..."
        if ! download_with_retry "$GITHUB_TARBALL" "$TEMP_DIR/plan-it.tar.gz"; then
          fail "Could not download from GitHub after ${MAX_RETRIES} attempts."
        fi
        mkdir -p "$TEMP_DIR/extracted"
        tar -xzf "$TEMP_DIR/plan-it.tar.gz" -C "$TEMP_DIR/extracted" --strip-components=1 2>/dev/null || \
          fail "Could not extract tarball."
        log_info "  Installing from GitHub source..."
        pip install "$TEMP_DIR/extracted" --quiet || fail "GitHub source install failed."
      fi
    fi
  fi

  # Verify CLI is functional
  if command -v plan-it &>/dev/null; then
    log_info "  ✓ plan-it CLI: $(command -v plan-it)"
  elif [ -f "$VENV_DIR/bin/plan-it" ]; then
    log_info "  ✓ plan-it CLI at: $VENV_DIR/bin/plan-it"
  else
    fail "plan-it CLI not found after install. Something went wrong."
  fi

  # Verify it actually runs
  if ! plan-it --help &>/dev/null; then
    if ! "$VENV_DIR/bin/plan-it" --help &>/dev/null; then
      log_warn "  ⚠ plan-it CLI check failed — it may need a virtualenv activation"
    fi
  else
    log_info "  ✓ plan-it CLI verified"
  fi

  # Dev deps (interactive only)
  if [ "$QUICK_MODE" = false ]; then
    read -r -p "  Install development dependencies (pytest, httpx)? [y/N]: " install_dev
    if [[ "$install_dev" =~ ^[Yy]$ ]]; then
      pip install "plan-it[dev]" --quiet 2>/dev/null || pip install pytest pytest-asyncio httpx --quiet
      log_info "  ✓ Dev dependencies installed"
    fi
  fi
}

# ── Bootstrap Configuration ──────────────────────────────────────────────────
bootstrap_config() {
  log_step "Setting up configuration..."
  mkdir -p "$CONFIG_DIR"

  if [ -f "$CONFIG_DIR/.env" ] && [ "$FORCE_MODE" = false ]; then
    log_info "  ✓ Config exists: $CONFIG_DIR/.env"
    return
  fi

  if command -v plan-it &>/dev/null; then
    TRAVEL_ENV_PATH="$CONFIG_DIR/.env" plan-it init
  else
    "$VENV_DIR/bin/plan-it" init
  fi

  export TRAVEL_ENV_PATH="$CONFIG_DIR/.env"
  log_info "  ✓ Config written — no API keys needed, fully self-contained"
}

# ── Shell Integration ────────────────────────────────────────────────────────
setup_shell_integration() {
  log_step "Setting up shell integration..."

  local plan-it_bin="$VENV_DIR/bin"; local profile_file=""
  case "${SHELL##*/}" in
    zsh)  [ -f "$HOME/.zshrc" ] && profile_file="$HOME/.zshrc" || profile_file="$HOME/.zprofile" ;;
    bash) [ -f "$HOME/.bashrc" ] && profile_file="$HOME/.bashrc" || profile_file="$HOME/.bash_profile" ;;
    *)    profile_file="$HOME/.profile" ;;
  esac
  [ -z "$profile_file" ] && profile_file="$HOME/.profile" && touch "$profile_file"

  local marker="# Plan-It PATH"
  local export_line="export PATH=\"$plan-it_bin:\$PATH\""
  local env_line="export TRAVEL_ENV_PATH=\"$CONFIG_DIR/.env\""

  if ! grep -qF "$marker" "$profile_file" 2>/dev/null; then
    { echo ""; echo "$marker"; echo "$export_line"; echo "$env_line"; } >> "$profile_file"
    log_info "  ✓ Added plan-it to PATH in $(basename "$profile_file")"
    log_info "  ℹ Restart your shell or run: source $profile_file"
  else
    log_info "  ✓ Shell integration already configured"
  fi
}

# ── Service Setup (Optional) ─────────────────────────────────────────────────
setup_service() {
  if [ "$QUICK_MODE" = true ]; then return; fi

  echo ""
  read -r -p "  Set up plan-it to start automatically on boot? [y/N]: " setup_svc
  if [[ ! "$setup_svc" =~ ^[Yy]$ ]]; then return; fi

  case "$DETECTED_OS" in
    macos)
      log_step "Setting up launchd service (macOS)..."
      local plist_path="$HOME/Library/LaunchAgents/com.plan-it.app.plist"
      mkdir -p "$HOME/Library/LaunchAgents"
      cat > "$plist_path" << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.plan-it.app</string>
  <key>ProgramArguments</key><array><string>$VENV_DIR/bin/plan-it</string><string>serve</string></array>
  <key>EnvironmentVariables</key><dict><key>TRAVEL_ENV_PATH</key><string>$CONFIG_DIR/.env</string></dict>
  <key>RunAtLoad</key><true/><key>KeepAlive</key><true/>
  <key>StandardOutPath</key><string>$CONFIG_DIR/plan-it.log</string>
  <key>StandardErrorPath</key><string>$CONFIG_DIR/plan-it-error.log</string>
</dict></plist>
PLIST
      launchctl load "$plist_path" 2>/dev/null || true
      log_info "  ✓ launchd service installed" ;;

    linux|wsl)
      log_step "Setting up systemd service (Linux)..."
      local service_path="$HOME/.config/systemd/user/plan-it.service"
      mkdir -p "$HOME/.config/systemd/user"
      cat > "$service_path" << UNIT
[Unit]
Description=Plan-It
After=network.target
[Service]
Type=simple
ExecStart=$VENV_DIR/bin/plan-it serve
Environment=TRAVEL_ENV_PATH=$CONFIG_DIR/.env
Restart=on-failure
RestartSec=10
[Install]
WantedBy=default.target
UNIT
      systemctl --user daemon-reload 2>/dev/null || true
      systemctl --user enable plan-it.service 2>/dev/null || true
      systemctl --user start plan-it.service 2>/dev/null || true
      log_info "  ✓ systemd user service installed" ;;

    android) log_info "  ℹ Termux: add 'plan-it serve' to ~/.bashrc or use Termux:Boot" ;;
    ios)     log_info "  ℹ iSH: auto-start not supported. Run 'plan-it serve' manually." ;;
  esac
}

# ── Install Complete ─────────────────────────────────────────────────────────
finish_install() {
  touch "$INSTALL_MARKER"
  banner "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  banner "  Plan-It v${VERSION} installed!"
  banner "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  echo "  ${BOLD}Next steps:${NC}"
  echo ""
  echo "  1. Start the server:"
  echo "     ${GREEN}plan-it serve${NC}"
  echo ""
  echo "  2. Open the app:"
  echo "     ${GREEN}http://localhost:8000${NC}"
  echo ""
  echo "  ${DIM}No API keys needed — DuckDuckGo provides web research for free.${NC}"
  echo ""
  echo "  ${BOLD}Commands:${NC}"
  echo "    plan-it serve    Start the server"
  echo "    plan-it doctor   Run full diagnostics"
  echo "    plan-it check    Show environment info"
  echo ""
}

# ── Dry Run ───────────────────────────────────────────────────────────────────
do_dry_run() {
  banner "  Plan-It — Dry Run"
  echo ""
  detect_os
  validate_env
  echo ""
  log_info "Dry run passed — environment is ready for install."
  log_info "Run without --dry-run to install."
}

# ── Main ─────────────────────────────────────────────────────────────────────
main() {
  echo ""
  echo "  ╔════════════════════════════════════════════╗"
  echo "  ║   Plan-It — SDK Installer                ║"
  echo "  ║            v${VERSION}                          ║"
  echo "  ╚════════════════════════════════════════════╝"
  echo ""

  if [ "$DRY_RUN" = true ]; then do_dry_run; exit 0; fi

  if [ -f "$INSTALL_MARKER" ] && [ "$FORCE_MODE" = false ]; then
    log_warn "Plan-It is already installed."
    log_warn "Use --force to re-install, or just run 'plan-it serve' to start."
    exit 0
  fi

  detect_os
  validate_env
  setup_venv
  install_package
  bootstrap_config
  setup_shell_integration
  setup_service
  finish_install
}

main
