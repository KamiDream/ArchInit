#!/bin/bash

# Supplementary script for ArchInit — optional environment setup
# Run after niri_init.sh if you need additional components.
# Each major step will ask for confirmation before execution.
# Manual edits will pause the script until the editor is closed.

set -euo pipefail

# ---------- Step 1: KVM Virtualization ----------
echo "========================================="
echo " Step 1: Install and Configure KVM Virtualization"
echo "========================================="
read -p "Run this step? (Y/n): " do_step
if [[ ! "$do_step" =~ ^[Yy]$ ]] && [ -n "$do_step" ]; then
    echo "Skipping Step 1."
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

    echo "[Step 1 completed]"
fi
echo ""

# ---------- Step 2: Install AUR Helper (yay) ----------
echo "========================================="
echo " Step 2: Install AUR Helper (yay / paru)"
echo "========================================="
read -p "Run this step? (Y/n): " do_step
if [[ ! "$do_step" =~ ^[Yy]$ ]] && [ -n "$do_step" ]; then
    echo "Skipping Step 2."
else
    echo ""
    echo ">>> Next, edit /etc/pacman.conf with vim"
    echo "    Make the following changes:"
    echo "    1) Remove the '#' before [multilib]"
    echo "    2) Remove the '#' before 'Include = /etc/pacman.d/mirrorlist'"
    echo "    3) Add archlinuxcn repository at end of file (see below)"
    echo ""
    echo "    Content to add at the end of file:"
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

    echo "[Step 2 completed]"
fi
echo ""

# ---------- Step 3: NVIDIA Driver ----------
echo "========================================="
echo " Step 3: Configure NVIDIA Graphics Driver"
echo "========================================="
read -p "Run this step? (Y/n): " do_step
if [[ ! "$do_step" =~ ^[Yy]$ ]] && [ -n "$do_step" ]; then
    echo "Skipping Step 3."
else
    echo ">>> Installing kernel headers..."
    sudo pacman -S --needed linux-headers linux-zen-headers

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

    echo "[Step 3 completed]"
fi
echo ""

# ---------- Step 4: Terminal Customization (Zsh & Kitty) ----------
echo "========================================="
echo " Step 4: Terminal Customization (Zsh & Kitty)"
echo "========================================="
read -p "Run this step? (Y/n): " do_step
if [[ ! "$do_step" =~ ^[Yy]$ ]] && [ -n "$do_step" ]; then
    echo "Skipping Step 4."
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

    echo "[Step 4 completed]"
fi
echo ""

# ---------- Step 5: Install Zim Framework & Powerlevel10k ----------
echo "========================================="
echo " Step 5: Install Zim Framework & Powerlevel10k Theme"
echo "========================================="
read -p "Run this step? (Y/n): " do_step
if [[ ! "$do_step" =~ ^[Yy]$ ]] && [ -n "$do_step" ]; then
    echo "Skipping Step 5."
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

    echo "[Step 5 completed]"
fi
echo ""

# ---------- Step 6: Copy fastfetch Config ----------
echo "========================================="
echo " Step 6: Copy fastfetch Configuration"
echo "========================================="
read -p "Run this step? (Y/n): " do_step
if [[ ! "$do_step" =~ ^[Yy]$ ]] && [ -n "$do_step" ]; then
    echo "Skipping Step 6."
else
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

    echo ">>> Copying fastfetch config to ~/.config/fastfetch..."
    mkdir -p ~/.config/fastfetch
    cp -r "$SCRIPT_DIR/fastfetch/"* ~/.config/fastfetch/
    echo "    fastfetch config copied successfully."
    echo ""
    echo ">>> Running Kitty font selector, choose JetBrains Mono..."
    read -p "Press Enter to launch font selector..."
    kitten choose-fonts
    read -p "Font selected. Press Enter to continue..."
    
    echo "[Step 6 completed]"
fi
echo ""

echo "========================================="
echo " All selected steps completed!"
echo "========================================="
