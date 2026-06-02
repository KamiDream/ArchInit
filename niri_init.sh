#!/bin/bash

# Arch Linux initialization script (run as a normal user with sudo privileges)
# Each major step will ask for confirmation before execution.
# Manual edits will pause the script until the editor is closed.

set -euo pipefail

# ---------- Step 1: Core Desktop (Niri + DMS) ----------
echo "========================================="
echo " Step 1: Install Core Desktop Environment (Niri Tiling WM & DMS Shell)"
echo "========================================="
read -p "Run this step? (Y/n): " do_step
if [[ ! "$do_step" =~ ^[Yy]$ ]] && [ -n "$do_step" ]; then
    echo "Skipping Step 1."
else
    echo ">>> Installing Niri and related components..."
    sudo pacman -Syu niri xwayland-satellite xdg-desktop-portal-gnome \
        xdg-desktop-portal-gtk alacritty dms-shell-niri matugen cava \
        qt6-multimedia-ffmpeg sddm power-profiles-daemon kimageformats

    echo ">>> Registering DMS as a user service dependency of Niri..."
    curl -fsSL https://install.danklinux.com | sh
    systemctl --user add-wants niri.service dms
    echo "[Step 1 completed]"
fi
echo ""

# ---------- Step 2: Initialization ----------
echo "========================================="
echo " Step 2: Basic Initialization (install common packages, configure locale, install fonts)"
echo "========================================="
read -p "Run this step? (Y/n): " do_step
if [[ ! "$do_step" =~ ^[Yy]$ ]] && [ -n "$do_step" ]; then
    echo "Skipping Step 2."
else
    echo ">>> Installing base packages..."
    sudo pacman -S --needed fastfetch fcitx5-im fcitx5-rime fuse2 ntfs-3g git quickshell flatseal dolphin kate firefox

    echo ""
    echo ">>> Next, edit /etc/locale.gen with vim"
    echo "    Find and uncomment 'zh_CN.UTF-8' (remove the leading #), then save and exit."
    read -p "Press Enter to open the editor..."
    sudo vim /etc/locale.gen
    read -p "Edit complete. Press Enter to continue..."

    echo ">>> Generating locale..."
    sudo locale-gen
    echo ">>> Setting system locale to zh_CN.UTF-8..."
    sudo localectl set-locale LANG=zh_CN.UTF-8

    echo ">>> Installing Chinese fonts & Nerd fonts..."
    sudo pacman -S --needed wqy-microhei wqy-microhei-lite wqy-bitmapfont wqy-zenhei \
        ttf-arphic-ukai ttf-arphic-uming noto-fonts-cjk ttf-jetbrains-mono-nerd

    echo "[Step 2 completed]"
fi
echo ""


# ---------- Step 3: Enable Display Manager (SDDM) ----------
echo "========================================="
echo " Step 3: Enable Display Manager (SDDM)"
echo "========================================="
read -p "Run this step? (Y/n): " do_step
if [[ ! "$do_step" =~ ^[Yy]$ ]] && [ -n "$do_step" ]; then
    echo "Skipping Step 3."
else
    echo ">>> Enabling SDDM display manager..."
    sudo systemctl enable sddm
    echo ">>> Starting SDDM..."
    sudo systemctl start sddm
    echo "[Step 3 completed]"
fi
echo ""

echo "========================================="
echo " All selected steps completed!"
echo " Please re-login or reboot for changes to take effect."
echo "========================================="
