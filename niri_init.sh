#!/bin/bash

# Arch Linux initialization script — fully automated one-click setup
# Run this script as a normal user with sudo privileges.
# All steps run sequentially after initial privilege escalation.

set -euo pipefail

# ─── Color definitions ───────────────────────
GREEN='\e[32m'
RED='\e[31m'
YELLOW='\e[33m'
CYAN='\e[36m'
LIGHT_BLUE='\e[94m'
LIGHT_PINK='\e[95m'
RESET='\e[0m'
BOLD='\e[1m'
# ─────────────────────────────────────────────

print_logo() {
    while IFS= read -r line; do
        echo -e "${LIGHT_BLUE}${line:0:45}${LIGHT_PINK}${line:45}${RESET}"
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
echo "  ArchInit — One-Click Setup"
echo "═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════"
echo ""
echo ">>> Requesting sudo access (password required)..."
sudo -v

# Keep sudo session alive in the background
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
    xdg-desktop-portal-gtk kitty dms-shell-niri matugen cava \
    qt6-multimedia-ffmpeg lightdm lightdm-gtk-greeter power-profiles-daemon kimageformats

echo "[Step 1 completed]"
echo ""

# ─────────────────────────────────────────────
# Step 2: Register DMS Service
# ─────────────────────────────────────────────
echo "========================================================================================================================="
echo " Step 2: Register DMS Service"
echo "========================================================================================================================="
echo ">>> Registering DMS as a user service dependency of Niri..."
curl -fsSL https://install.danklinux.com | sh
systemctl --user add-wants niri.service dms

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
    quickshell flatseal dolphin kate firefox

echo ""
echo ">>> Uncommenting zh_CN.UTF-8 in /etc/locale.gen..."
sudo sed -i 's/^#zh_CN.UTF-8/zh_CN.UTF-8/' /etc/locale.gen
echo "    zh_CN.UTF-8 enabled."

echo ">>> Generating locale..."
sudo locale-gen
echo ">>> Setting system locale to zh_CN.UTF-8..."
sudo localectl set-locale LANG=zh_CN.UTF-8

echo ">>> Installing Chinese fonts & Nerd fonts..."
sudo pacman -S --needed --noconfirm wqy-microhei wqy-microhei-lite wqy-bitmapfont wqy-zenhei \
    ttf-arphic-ukai ttf-arphic-uming noto-fonts-cjk ttf-jetbrains-mono-nerd

echo "[Step 3 completed]"
echo ""

# ─────────────────────────────────────────────
# Step 4: Enable Display Manager (LightDM)
# ─────────────────────────────────────────────
echo "========================================================================================================================="
echo " Step 4: Display Manager (LightDM)"
echo "========================================================================================================================="
echo ">>> Enabling LightDM display manager..."
sudo systemctl enable lightdm
echo ">>> Starting LightDM..."
sudo systemctl start lightdm
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
