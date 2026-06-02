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
        qt6-multimedia-ffmpeg sddm

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

# ---------- Step 3: KVM Virtualization ----------
echo "========================================="
echo " Step 3: Install and Configure KVM Virtualization"
echo "========================================="
read -p "Run this step? (Y/n): " do_step
if [[ ! "$do_step" =~ ^[Yy]$ ]] && [ -n "$do_step" ]; then
    echo "Skipping Step 3."
else
    echo ">>> Installing KVM packages..."
    sudo pacman -S --needed qemu-full virt-manager swtpm dnsmasq

    echo ">>> Enabling and starting libvirtd service..."
    sudo systemctl enable --now libvirtd

    echo ">>> Starting default virtual network..."
    sudo virsh net-start default
    sudo virsh net-autostart default

    echo ">>> Adding current user to libvirt group..."
    sudo usermod -a -G libvirt "$(whoami)"
    echo "    Note: re-login is required for group changes to take effect."

    echo "[Step 3 completed]"
fi
echo ""

# ---------- Step 4: NVIDIA Driver ----------
echo "========================================="
echo " Step 4: Configure NVIDIA Graphics Driver"
echo "========================================="
read -p "Run this step? (Y/n): " do_step
if [[ ! "$do_step" =~ ^[Yy]$ ]] && [ -n "$do_step" ]; then
    echo "Skipping Step 4."
else
    echo ">>> Installing kernel headers..."
    sudo pacman -S --needed linux-headers linux-zen-headers

    echo ""
    echo ">>> Next, edit /etc/pacman.conf with vim"
    echo "    Make the following changes:"
    echo "    1) Uncomment [multilib] and its Include line"
    echo "    2) Add archlinuxcn repository at end of file (see below)"
    echo ""
    echo "    Content to add:"
    echo "    [archlinuxcn]"
    echo "    Server = https://mirrors.ustc.edu.cn/archlinuxcn/\$arch"
    echo "    Server = https://mirrors.tuna.tsinghua.edu.cn/archlinuxcn/\$arch"
    echo "    Server = https://mirrors.hit.edu.cn/archlinuxcn/\$arch"
    echo "    Server = https://repo.huaweicloud.com/archlinuxcn/\$arch"
    read -p "Press Enter to open the editor..."
    sudo vim /etc/pacman.conf
    read -p "Edit complete. Press Enter to continue..."

    echo ">>> Installing archlinuxcn-keyring and updating system..."
    sudo pacman -Sy --needed archlinuxcn-keyring
    sudo pacman -S --needed base-devel yay paru flclash
    sudo pacman -Syu

    echo ">>> Installing NVIDIA drivers..."
    sudo pacman -S --needed nvidia-dkms nvidia-utils nvidia-settings

    echo ""
    echo ">>> Next, edit /etc/mkinitcpio.conf, add nvidia modules to MODULES=():"
    echo "    MODULES=(nvidia nvidia_modeset nvidia_uvm nvidia_drm)"
    read -p "Press Enter to open the editor..."
    sudo vim /etc/mkinitcpio.conf
    read -p "Edit complete. Press Enter to continue..."

    echo ">>> Regenerating initramfs..."
    sudo mkinitcpio -P

    echo "[Step 4 completed]"
fi
echo ""

# ---------- Step 5: Terminal Customization (Zsh & Kitty) ----------
echo "========================================="
echo " Step 5: Terminal Customization (Zsh & Kitty)"
echo "========================================="
read -p "Run this step? (Y/n): " do_step
if [[ ! "$do_step" =~ ^[Yy]$ ]] && [ -n "$do_step" ]; then
    echo "Skipping Step 5."
else
    echo ">>> Installing Zsh and related plugins..."
    sudo pacman -S --needed zsh zsh-autosuggestions zsh-syntax-highlighting zsh-completions

    echo ">>> Listing available shells..."
    chsh -l

    echo ">>> Changing default shell to Zsh (password required)..."
    chsh -s /usr/bin/zsh

    echo ""
    echo ">>> Next, edit ~/.zshrc with Kate, add the following:"
    echo "    fastfetch"
    echo "    source /usr/share/zsh/plugins/zsh-autosuggestions/zsh-autosuggestions.zsh"
    echo "    source /usr/share/zsh/plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh"
    read -p "Press Enter to open the editor..."
    kate ~/.zshrc
    read -p "Edit complete. Press Enter to continue..."

    echo ""
    echo ">>> Next, edit Kitty terminal config ~/.config/kitty/kitty.conf"
    echo "    Content to add:"
    echo "    cursor_trail 2"
    echo "    cursor_blink_interval 0.5"
    echo "    cursor_stop_blinking_after 0"
    read -p "Press Enter to open the editor..."
    kate ~/.config/kitty/kitty.conf
    read -p "Edit complete. Press Enter to continue..."

    echo ""
    echo ">>> Running Kitty font selector, choose JetBrains Mono..."
    read -p "Press Enter to launch font selector..."
    kitten choose-fonts
    read -p "Font selected. Press Enter to continue..."

    echo "[Step 5 completed]"
fi
echo ""

# ---------- Step 6: Install Zim Framework & Powerlevel10k ----------
echo "========================================="
echo " Step 6: Install Zim Framework & Powerlevel10k Theme"
echo "========================================="
read -p "Run this step? (Y/n): " do_step
if [[ ! "$do_step" =~ ^[Yy]$ ]] && [ -n "$do_step" ]; then
    echo "Skipping Step 6."
else
    # Check if Zsh is available
    if ! command -v zsh >/dev/null 2>&1; then
        echo "Warning: Zsh does not appear to be installed. Zim framework requires Zsh."
        read -p "Press Enter to continue, or Ctrl+C to cancel..."
    fi

    echo ">>> Installing Zim framework..."
    curl -fsSL https://raw.githubusercontent.com/zimfw/install/master/install.zsh | zsh

    echo ""
    echo ">>> Next, edit ~/.zimrc with Kate, add the following:"
    echo "    zmodule romkatv/powerlevel10k"
    read -p "Press Enter to open the editor..."
    kate ~/.zimrc
    read -p "Edit complete. Press Enter to continue..."

    echo "[Step 6 completed]"
fi
echo ""

# ---------- Step 7: Enable Display Manager (SDDM) ----------
echo "========================================="
echo " Step 7: Enable Display Manager (SDDM)"
echo "========================================="
read -p "Run this step? (Y/n): " do_step
if [[ ! "$do_step" =~ ^[Yy]$ ]] && [ -n "$do_step" ]; then
    echo "Skipping Step 7."
else
    echo ">>> Enabling SDDM display manager..."
    sudo systemctl enable sddm
    echo ">>> Starting SDDM..."
    sudo systemctl start sddm
    echo "[Step 7 completed]"
fi
echo ""

echo "========================================="
echo " All selected steps completed!"
echo " Please re-login or reboot for changes to take effect."
echo "========================================="
