#!/bin/bash

# Arch Linux initialization script — fully automated one-click setup
# Run this script as a normal user with sudo privileges.
# All steps run sequentially after initial privilege escalation.
#
# This variant uses Noctalia desktop shell instead of DMS.
# Noctalia v5: native Wayland desktop shell (bars, widgets, launcher, etc.)
# Website: https://noctalia.dev  |  Docs: https://docs.noctalia.dev/v5/

set -Euo pipefail

# ─── Error handling ──────────────────────────
error_handler() {
    local exit_code=$?
    echo "" >&2
    echo -e "${RED}${BOLD}  ❌ Error at line $1 — exit code $exit_code${RESET}" >&2
    echo -e "${RED}  Please fix the issue and re-run the script.${RESET}" >&2
    echo "" >&2
    exit "$exit_code"
}
trap 'error_handler $LINENO' ERR

cleanup() {
    echo "" >&2
    echo -e "${YELLOW}  ⚠️  Script interrupted by user.${RESET}" >&2
    exit 1
}
trap 'cleanup' INT

# ─── Color definitions ───────────────────────
GREEN='\e[32m'; RED='\e[31m'; YELLOW='\e[33m'
CYAN='\e[36m'; LIGHT_BLUE='\e[94m'; LIGHT_PINK='\e[95m'
RESET='\e[0m'; BOLD='\e[1m'

print_logo() {
    while IFS= read -r line; do
        echo -e "${LIGHT_BLUE}${line:0:48}${LIGHT_PINK}${line:48}${RESET}"
    done << 'LOGO'
88      a8P                                   88  88888888ba,
88    ,88'                                    ""  88      `"8b
88  ,88"                                          88        `8b
88,d88'       ,adPPYYba,  88,dPYba,,adPYba,   88  88         88  8b,dPPYba,   ,adPPYba,  ,adPPYYba,  88,dPYba,,adPYba,
8888"88,      ""     `Y8  88P'   "88"    "8a  88  88         88  88P'   "Y8  a8P_____88  ""     `Y8  88P'   "88"    "8a
88P   Y8b     ,adPPPPP88  88      88      88  88  88         8P  88          8PP"""""""  ,adPPPPP88  88      88      88
88     "88,   88,    ,88  88      88      88  88  88      .a8P   88          "8b,   ,aa  88,    ,88  88      88      88
88       Y8b  `"8bbdP"Y8  88      88      88  88  88888888Y"'    88           `"Ybbd8"'  `"8bbdP"Y8  88      88      88
LOGO
}

# ─────────────────────────────────────────────
# Initial privilege escalation & keep-alive
# ─────────────────────────────────────────────
print_logo
echo "═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════"
echo "  ArchInit — One-Click Setup (Noctalia Edition)"
echo "═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════"
echo ""
echo ">>> Requesting sudo access (password required)..."
sudo -v
while true; do sudo -n true; sleep 60; kill -0 "$$" 2>/dev/null || break; done 2>/dev/null &
echo "    ✅ Sudo privileges acquired."
echo ""

# ─────────────────────────────────────────────
# Step 1: Core Desktop (Niri)
# ─────────────────────────────────────────────
echo "========================================================================================================================="
echo " Step 1: Core Desktop (Niri)"
echo "========================================================================================================================="
echo ">>> Installing Niri and related components..."
sudo pacman -Syu --needed --noconfirm niri xwayland-satellite xdg-desktop-portal-gnome \
    xdg-desktop-portal-gtk kitty matugen cava \
    qt6-multimedia-ffmpeg power-profiles-daemon kimageformats greetd \
    tomlplusplus
echo "[Step 1 completed]"
echo ""

# ─────────────────────────────────────────────
# Step 2: Install AUR Helper & Noctalia Shell
# ─────────────────────────────────────────────
echo "========================================================================================================================="
echo " Step 2: Install AUR Helper & Noctalia Shell"
echo "========================================================================================================================="

echo ">>> Configuring /etc/pacman.conf..."
sudo sed -i '/^#\[multilib\]/,/^#Include/ s/^#//' /etc/pacman.conf
echo "    [multilib] enabled."
if ! grep -q '^\[archlinuxcn\]' /etc/pacman.conf; then
    sudo tee -a /etc/pacman.conf > /dev/null << 'EOF'

[archlinuxcn]
Server = https://mirrors.ustc.edu.cn/archlinuxcn/$arch
Server = https://mirrors.tuna.tsinghua.edu.cn/archlinuxcn/$arch
Server = https://mirrors.hit.edu.cn/archlinuxcn/$arch
Server = https://repo.huaweicloud.com/archlinuxcn/$arch
EOF
    echo "    [archlinuxcn] added."
fi
sudo pacman -Sy --needed --noconfirm archlinuxcn-keyring
sudo pacman -S --needed --noconfirm base-devel yay paru
sudo pacman -Syu --noconfirm
echo "    ✅ AUR helpers (yay, paru) installed."

echo ""
echo ">>> Installing Noctalia shell from AUR (noctalia-git)..."
yay -S --needed --noconfirm noctalia-git
echo "    ✅ Noctalia installed."

# ─────────────────────────────────────────────
# 2c. Deploy Niri config from window_ctrl
# ─────────────────────────────────────────────
echo ""
echo ">>> Deploying Niri config from window_ctrl..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NIRI_CFG_DIR="$HOME/.config/niri"

mkdir -p "$NIRI_CFG_DIR" "$NIRI_CFG_DIR/dms"

if [[ -f "$SCRIPT_DIR/window_ctrl/config.kdl" ]]; then
    cp "$SCRIPT_DIR/window_ctrl/config.kdl" "$NIRI_CFG_DIR/config.kdl"
    echo "    ✅ Copied config.kdl"
fi

if [[ -d "$SCRIPT_DIR/window_ctrl/dms" ]]; then
    cp "$SCRIPT_DIR/window_ctrl/dms/"*.kdl "$NIRI_CFG_DIR/dms/"
    echo "    ✅ Copied dms/*.kdl"
fi

if ! grep -q 'spawn-at-startup.*noctalia' "$NIRI_CFG_DIR/config.kdl" 2>/dev/null; then
    echo "" >> "$NIRI_CFG_DIR/config.kdl"
    echo "spawn-at-startup \"noctalia\"" >> "$NIRI_CFG_DIR/config.kdl"
    echo "    ✅ Added spawn-at-startup \"noctalia\""
fi

# ─────────────────────────────────────────────
# 2d. Noctalia config + wallpaper dir
# ─────────────────────────────────────────────
echo ""
echo ">>> Creating default Noctalia configuration..."
mkdir -p "$HOME/.config/noctalia"
if [[ ! -f "$HOME/.config/noctalia/config.toml" ]]; then
    cat > "$HOME/.config/noctalia/config.toml" << 'NOCTOML'
[shell]
font_family           = "sans-serif"
corner_radius_scale   = 1.0
time_format           = "{:%H:%M}"
date_format           = "%A, %x"
clipboard_enabled     = true

[shell.panel]
transparency_mode     = "solid"
borders               = true
shadow                = true

[shell.animation]
enabled = true
speed   = 1.0

[wallpaper]
enabled     = true
fill_mode   = "crop"
fill_color  = "#1e1e2e"
directory   = "~/Pictures/Wallpapers"

[theme]
mode    = "dark"
source  = "builtin"
builtin = "Noctalia"
NOCTOML
    echo "    ✅ Default Noctalia config created"
fi

mkdir -p "$HOME/Pictures/Wallpapers"
echo "    ✅ Created ~/Pictures/Wallpapers/"

echo "[Step 2 completed]"
echo ""

# ─────────────────────────────────────────────
# Step 3: Basic Initialization
# ─────────────────────────────────────────────
echo "========================================================================================================================="
echo " Step 3: Basic Initialization"
echo "========================================================================================================================="
echo ">>> Installing base packages..."
sudo pacman -S --needed --noconfirm fastfetch fcitx5-im fcitx5-rime fuse2 ntfs-3g git \
    flatseal dolphin kate firefox

echo ""
echo ">>> Configuring zh_CN.UTF-8 locale..."
sudo sed -i 's/^#zh_CN.UTF-8/zh_CN.UTF-8/' /etc/locale.gen
sudo locale-gen
sudo localectl set-locale LANG=zh_CN.UTF-8

echo ">>> Installing Chinese fonts & Nerd fonts..."
sudo pacman -S --needed --noconfirm wqy-microhei wqy-microhei-lite wqy-bitmapfont wqy-zenhei \
    ttf-arphic-ukai ttf-arphic-uming noto-fonts-cjk ttf-jetbrains-mono-nerd noto-fonts-emoji

echo "[Step 3 completed]"
echo ""

# ─────────────────────────────────────────────
# Step 4: Display Manager (Noctalia Greeter)
# ─────────────────────────────────────────────
echo "========================================================================================================================="
echo " Step 4: Display Manager (Noctalia Greeter)"
echo "========================================================================================================================="

echo ">>> Installing Noctalia Greeter from AUR..."
yay -S --needed --noconfirm noctalia-greeter
echo "    ✅ Noctalia Greeter installed."

GREETER_SESSION="$(command -v noctalia-greeter-session 2>/dev/null)" || GREETER_SESSION=""
if [[ -z "$GREETER_SESSION" ]]; then
    [[ -x /usr/local/bin/noctalia-greeter-session ]] && GREETER_SESSION="/usr/local/bin/noctalia-greeter-session"
    [[ -x /usr/bin/noctalia-greeter-session ]] && GREETER_SESSION="/usr/bin/noctalia-greeter-session"
fi

if [[ -z "$GREETER_SESSION" ]]; then
    echo "    ⚠️  noctalia-greeter-session not found, configure /etc/greetd/config.toml manually."
else
    echo "    Found: $GREETER_SESSION"
    sudo mkdir -p /etc/greetd
    [[ -f /etc/greetd/config.toml ]] && sudo cp /etc/greetd/config.toml /etc/greetd/config.toml.bak
    sudo tee /etc/greetd/config.toml > /dev/null << GREETDEOF
[terminal]
vt = 1

[default_session]
command = "${GREETER_SESSION} -- --session niri"
user = "greeter"
GREETDEOF
    echo "    ✅ greetd configured. Default session: niri"
fi

sudo systemctl enable greetd
sudo systemctl start greetd
echo "[Step 4 completed]"
echo ""

# ─────────────────────────────────────────────
# Done
# ─────────────────────────────────────────────
echo "═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════"
echo "  ✅ All steps completed!"
echo ""
echo "  Please re-login or reboot for changes to take effect."
echo "═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════"
