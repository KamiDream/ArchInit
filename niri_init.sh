#!/bin/bash

# Arch Linux initialization script — fully automated one-click setup
# Run this script as a normal user with sudo privileges.
# All steps run sequentially after initial privilege escalation.

set -euo pipefail

# ─────────────────────────────────────────────
# Initial privilege escalation & keep-alive
# ─────────────────────────────────────────────
echo "══════════════════════════════════════════════════"
echo "  ArchInit — 一键初始化 / One-Click Setup"
echo "══════════════════════════════════════════════════"
echo ""
echo ">>> 正在请求 sudo 权限（需要输入密码）..."
echo ">>> Requesting sudo access (password required)..."
sudo -v

# Keep sudo session alive in the background
while true; do sudo -n true; sleep 60; kill -0 "$$" 2>/dev/null || break; done 2>/dev/null &

echo "    ✅ Sudo 权限已获取 / Privileges acquired."
echo ""

# ─────────────────────────────────────────────
# Step 1: Core Desktop (Niri)
# ─────────────────────────────────────────────
echo "========================================="
echo " Step 1: 核心桌面 / Core Desktop (Niri)"
echo "========================================="
echo ">>> Installing Niri and related components..."
sudo pacman -Syu --noconfirm niri xwayland-satellite xdg-desktop-portal-gnome \
    xdg-desktop-portal-gtk kitty dms-shell-niri matugen cava \
    qt6-multimedia-ffmpeg lightdm lightdm-gtk-greeter power-profiles-daemon kimageformats

echo "[Step 1 completed]"
echo ""

# ─────────────────────────────────────────────
# Step 2: Register DMS Service
# ─────────────────────────────────────────────
echo "========================================="
echo " Step 2: 注册 DMS 服务 / Register DMS Service"
echo "========================================="
echo ">>> Registering DMS as a user service dependency of Niri..."
curl -fsSL https://install.danklinux.com | sh
systemctl --user add-wants niri.service dms

echo "[Step 2 completed]"
echo ""

# ─────────────────────────────────────────────
# Step 3: Basic Initialization
# ─────────────────────────────────────────────
echo "========================================="
echo " Step 3: 基础初始化 / Basic Initialization"
echo "========================================="
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
echo "========================================="
echo " Step 4: 显示管理器 / Display Manager (LightDM)"
echo "========================================="
echo ">>> Enabling LightDM display manager..."
sudo systemctl enable lightdm
echo ">>> Starting LightDM..."
sudo systemctl start lightdm
echo "[Step 4 completed]"
echo ""

# ─────────────────────────────────────────────
# Done
# ─────────────────────────────────────────────
echo "══════════════════════════════════════════════════"
echo "  ✅ 所有步骤已完成 / All steps completed!"
echo ""
echo "  请重新登录或重启系统使更改生效。"
echo "  Please re-login or reboot for changes to take effect."
echo "══════════════════════════════════════════════════"
