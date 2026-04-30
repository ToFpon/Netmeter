#!/usr/bin/env bash
# uninstall.sh — NetMeter uninstaller
# Usage: chmod +x uninstall.sh && ./uninstall.sh
# GPLv3

set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

ok()   { echo -e "${GREEN}✔${NC}  $*"; }
info() { echo -e "${CYAN}→${NC}  $*"; }
warn() { echo -e "${YELLOW}⚠${NC}  $*"; }
sep()  { echo -e "${BOLD}────────────────────────────────────────${NC}"; }

BIN_DIR="${HOME}/.local/bin"
APP_DIR="${HOME}/.local/share/applications"
DEST="${BIN_DIR}/netmeter"
DESKTOP_FILE="${APP_DIR}/NetMeter.desktop"

sep
echo -e "${BOLD}  🌐 NetMeter — Uninstall${NC}"
sep

if [[ -f "$DEST" ]]; then
    info "Removing ${DEST}"
    rm -f "$DEST"
    ok "Removed executable."
else
    warn "Executable not found: ${DEST}"
fi

if [[ -f "$DESKTOP_FILE" ]]; then
    info "Removing ${DESKTOP_FILE}"
    rm -f "$DESKTOP_FILE"
    ok "Removed desktop launcher."
else
    warn "Desktop launcher not found: ${DESKTOP_FILE}"
fi

if command -v update-desktop-database &>/dev/null && [[ -d "$APP_DIR" ]]; then
    info "Refreshing desktop database cache..."
    update-desktop-database "$APP_DIR" 2>/dev/null || true
fi

sep
echo -e "${GREEN}${BOLD}  ✔ NetMeter uninstall complete.${NC}"
sep
