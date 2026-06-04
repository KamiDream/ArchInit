#!/bin/bash

# Arch Linux initialization script (run as a normal user with sudo privileges)
# Each major step will ask for confirmation before execution.
# Manual edits will pause the script until the editor is closed.

set -euo pipefail

# ---------- Step 1: Core Desktop (Niri) ----------
echo "========================================="
echo " Step 1: Install Core Desktop Environment (Niri Tiling WM)"
echo "========================================="
read -p "Run this step? (Y/n): " do_step
if [[ ! "$do_step" =~ ^[Yy]$ ]] && [ -n "$do_step" ]; then
    echo "Skipping Step 1."
else
    echo ">>> Installing Niri and related components..."
    sudo pacman -Syu niri xwayland-satellite xdg-desktop-portal-gnome \
        xdg-desktop-portal-gtk kitty dms-shell-niri matugen cava \
        qt6-multimedia-ffmpeg lightdm lightdm-gtk-greeter power-profiles-daemon kimageformats

    echo "[Step 1 completed]"
fi
echo ""

# ---------- Step 2: Register DMS Service ----------
echo "========================================="
echo " Step 2: Register DMS as a User Service Dependency of Niri"
echo "========================================="
read -p "Run this step? (Y/n): " do_step
if [[ ! "$do_step" =~ ^[Yy]$ ]] && [ -n "$do_step" ]; then
    echo "Skipping Step 2."
else
    echo ">>> Registering DMS as a user service dependency of Niri..."
    curl -fsSL https://install.danklinux.com | sh
    systemctl --user add-wants niri.service dms

    echo "[Step 2 completed]"
fi
echo ""

# ---------- Step 3: Basic Initialization ----------
echo "========================================="
echo " Step 3: Basic Initialization (install common packages, configure locale, install fonts)"
echo "========================================="
read -p "Run this step? (Y/n): " do_step
if [[ ! "$do_step" =~ ^[Yy]$ ]] && [ -n "$do_step" ]; then
    echo "Skipping Step 3."
else
    echo ">>> Installing base packages..."
    sudo pacman -S --needed fastfetch fcitx5-im fcitx5-rime fuse2 ntfs-3g git quickshell flatseal dolphin kate firefox

    echo ""
    echo ">>> Uncommenting zh_CN.UTF-8 in /etc/locale.gen..."
    sudo sed -i 's/^#zh_CN.UTF-8/zh_CN.UTF-8/' /etc/locale.gen
    echo "    zh_CN.UTF-8 enabled."

    echo ">>> Generating locale..."
    sudo locale-gen
    echo ">>> Setting system locale to zh_CN.UTF-8..."
    sudo localectl set-locale LANG=zh_CN.UTF-8

    echo ">>> Installing Chinese fonts & Nerd fonts..."
    sudo pacman -S --needed wqy-microhei wqy-microhei-lite wqy-bitmapfont wqy-zenhei \
        ttf-arphic-ukai ttf-arphic-uming noto-fonts-cjk ttf-jetbrains-mono-nerd

    echo "[Step 3 completed]"
fi
echo ""

# ---------- Step 4: Enable Display Manager (LightDM) ----------
echo "========================================="
echo " Step 4: Enable Display Manager (LightDM)"
echo "========================================="
read -p "Run this step? (Y/n): " do_step
if [[ ! "$do_step" =~ ^[Yy]$ ]] && [ -n "$do_step" ]; then
    echo "Skipping Step 4."
else
    echo ">>> Enabling LightDM display manager..."
    sudo systemctl enable lightdm
    echo ">>> Starting LightDM..."
    sudo systemctl start lightdm
    echo "[Step 4 completed]"
fi
echo ""

echo "========================================="
echo " All selected steps completed!"
echo " Please re-login or reboot for changes to take effect."
echo "========================================="
