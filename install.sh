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
mkdir -p "$BIN_DIR" "$APP_DIR"

# ── Copy script ───────────────────────────────────────────────────────────────
DEST="${BIN_DIR}/netmeter"
info "Copying netmeter.py → ${DEST}"
cp "$NETMETER_SRC" "$DEST"
chmod +x "$DEST"
ok "Script installed in ${DEST}"

# ── .desktop launcher ─────────────────────────────────────────────────────────
DESKTOP_FILE="${APP_DIR}/NetMeter.desktop"
info "Creating .desktop launcher..."
cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Encoding=UTF-8
Name=NetMeter
Comment=
Exec=python3 ${DEST}
Icon=blackmagicraw-speedtest
Terminal=false
Type=Application
StartupWMClass=netmeter.py
Categories=GNOME;Application;Utility;
EOF
ok "Launcher created in ${DESKTOP_FILE}"

# ── Desktop database cache ────────────────────────────────────────────────────
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
