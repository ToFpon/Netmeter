#!/usr/bin/env bash
# install.sh — NetMeter installer
# Usage: chmod +x install.sh && ./install.sh
# GPLv3

set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

ok()   { echo -e "${GREEN}✔${NC}  $*"; }
info() { echo -e "${CYAN}→${NC}  $*"; }
warn() { echo -e "${YELLOW}⚠${NC}  $*"; }
fail() { echo -e "${RED}✘${NC}  $*" >&2; exit 1; }
sep()  { echo -e "${BOLD}────────────────────────────────────────${NC}"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NETMETER_SRC="${SCRIPT_DIR}/netmeter.py"
[[ -f "$NETMETER_SRC" ]] || fail "netmeter.py not found in ${SCRIPT_DIR}"

sep
echo -e "${BOLD}  🌐 NetMeter — Installation${NC}"
sep

# ── apt dependencies ──────────────────────────────────────────────────────────
info "Checking system dependencies..."

APT_PKGS=(python3-gi python3-gi-cairo gir1.2-gtk-4.0 python3-psutil wmctrl)
MISSING=()
for pkg in "${APT_PKGS[@]}"; do
    dpkg-query -W -f='${Status}' "$pkg" 2>/dev/null | grep -q "install ok installed" \
        || MISSING+=("$pkg")
done

if [[ ${#MISSING[@]} -gt 0 ]]; then
    warn "Missing packages: ${MISSING[*]}"
    info "Installing via apt..."
    sudo apt-get install -y "${MISSING[@]}" || fail "apt install failed."
    ok "Dependencies installed."
else
    ok "All dependencies already present."
fi

# ── Target directories ────────────────────────────────────────────────────────
BIN_DIR="${HOME}/.local/bin"
APP_DIR="${HOME}/.local/share/applications"
ICON_DIR="${HOME}/.local/share/icons/hicolor/scalable/apps"
mkdir -p "$BIN_DIR" "$APP_DIR" "$ICON_DIR"

# ── Copy script ───────────────────────────────────────────────────────────────
DEST="${BIN_DIR}/netmeter"
info "Copying netmeter.py → ${DEST}"
cp "$NETMETER_SRC" "$DEST"
chmod +x "$DEST"
ok "Script installed in ${DEST}"

# ── SVG icon ──────────────────────────────────────────────────────────────────
ICON_PATH="${ICON_DIR}/netmeter.svg"
info "Creating icon..."
cat > "$ICON_PATH" << 'SVGEOF'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="10" fill="#0d1117"/>
  <rect x="6" y="8" width="52" height="36" rx="4" fill="#161b22" stroke="#21262d" stroke-width="1"/>
  <polyline points="8,40 16,32 22,35 28,20 34,25 40,14 46,18 54,10"
            fill="none" stroke="#3fb950" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>
  <polyline points="8,42 16,38 22,40 28,34 34,36 40,28 46,32 54,22"
            fill="none" stroke="#f78166" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>
  <rect x="8"  y="50" width="8" height="5" rx="1" fill="#3fb950"/>
  <rect x="30" y="50" width="8" height="5" rx="1" fill="#f78166"/>
  <text x="19" y="55" font-family="monospace" font-size="6" fill="#8b949e">DL</text>
  <text x="41" y="55" font-family="monospace" font-size="6" fill="#8b949e">UL</text>
</svg>
SVGEOF
ok "Icon created in ${ICON_PATH}"

# ── .desktop launcher ─────────────────────────────────────────────────────────
DESKTOP_FILE="${APP_DIR}/netmeter.desktop"
info "Creating .desktop launcher..."
cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=NetMeter
GenericName=Network Monitor
Comment=Real-time network bandwidth monitor
Exec=${DEST}
Icon=netmeter
Terminal=false
Categories=Network;Monitor;System;
Keywords=network;bandwidth;monitor;réseau;débit;Netzwerk;
StartupNotify=false
EOF
ok "Launcher created in ${DESKTOP_FILE}"

# ── Icon/desktop cache ────────────────────────────────────────────────────────
command -v gtk-update-icon-cache &>/dev/null \
    && gtk-update-icon-cache -q -t "${HOME}/.local/share/icons/hicolor" 2>/dev/null || true
command -v update-desktop-database &>/dev/null \
    && update-desktop-database "$APP_DIR" 2>/dev/null || true

# ── PATH check ────────────────────────────────────────────────────────────────
sep
if [[ ":${PATH}:" != *":${BIN_DIR}:"* ]]; then
    warn "${BIN_DIR} is not in your PATH."
    echo    "  Add this line to your ~/.bashrc or ~/.profile:"
    echo -e "  ${CYAN}export PATH=\"\$HOME/.local/bin:\$PATH\"${NC}"
    echo    "  then reload your terminal."
else
    ok "${BIN_DIR} is in PATH."
fi

sep
echo -e "${GREEN}${BOLD}  ✔ NetMeter successfully installed!${NC}"
echo
echo -e "  Command line : ${CYAN}netmeter${NC}"
echo -e "  Or via your desktop environment's application menu."
sep
