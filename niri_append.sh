#!/bin/bash

# Supplementary script for ArchInit — optional environment setup
# Run after niri_init.sh if you need additional components.
# Interactive menu — use ↑/↓ to navigate, Enter to execute, q to quit.
# Manual edits will pause the script until the editor is closed.

set -uo pipefail
# Note: we do NOT use 'set -e' so that step functions can return 1 gracefully

# ─── Color definitions ───────────────────────
GREEN='\e[32m'
RED='\e[31m'
YELLOW='\e[33m'
CYAN='\e[36m'
RESET='\e[0m'
BOLD='\e[1m'
# ─────────────────────────────────────────────

# ─────────────────────────────────────────────
# Step definitions
# ─────────────────────────────────────────────
STEPS=(
    "Kitty 字体选择 / Kitty Font Selector"
    "KVM 虚拟化 / KVM Virtualization"
    "AUR 助手 / AUR Helper (yay / paru)"
    "NVIDIA 显卡驱动 / NVIDIA Graphics Driver"
    "启用 Zsh 终端 / Enable Zsh Shell"
    "Antidote 插件管理器 / Antidote Plugin Manager"
    "Starship 提示符 / Starship Prompt"
    "fastfetch 配置 / fastfetch Configuration"
    "配置 fastfetch 启动 / Configure fastfetch on startup"
)

# 0 = pending, 1 = completed
COMPLETED=(0 0 0 0 0 0 0 0 0)

CURRENT_STEP=-1   # -1 means at menu, >=0 means inside a step
SELECTED=0

# ─────────────────────────────────────────────
# Helper: wait for Enter or 'q' to go back
# ─────────────────────────────────────────────
prompt_enter_or_quit() {
    local msg="${1:-Press Enter to continue...}"
    local extra="${2:-}"
    if [[ -n "$extra" ]]; then
        echo -e "$extra"
    fi
    echo -e "  [${msg}]  (or press q to return to menu)"
    read -rs input
    if [[ "$input" == "q" ]] || [[ "$input" == "Q" ]]; then
        return 1   # signal quit
    fi
    return 0
}

# ─────────────────────────────────────────────
# Helper: step header
# ─────────────────────────────────────────────
step_header() {
    local num="$1"
    local title="${STEPS[$((num-1))]}"
    echo ""
    echo "========================================="
    echo " Step $num: $title"
    echo "========================================="
}

# ─────────────────────────────────────────────
# Helper: ensure Zsh is installed
# ─────────────────────────────────────────────
check_zsh() {
    if ! command -v zsh >/dev/null 2>&1; then
        echo "Warning: Zsh does not appear to be installed."
        return 1
    fi
    return 0
}

# ─────────────────────────────────────────────
# Step functions — return 0 on success, 1 if user quit
# ─────────────────────────────────────────────

step_1_kitty_font() {
    step_header 1
    echo ">>> Running Kitty font selector, choose JetBrains Mono..."
    prompt_enter_or_quit "Press Enter to launch font selector" || return 1
    kitten choose-fonts
    prompt_enter_or_quit "Font selected. Press Enter to continue" || return 1

    echo "[Step 1 completed]"
    return 0
}

step_2_kvm() {
    step_header 2
    echo ">>> Installing KVM packages..."
    sudo pacman -S --needed --noconfirm qemu-full virt-manager swtpm dnsmasq || return 0

    echo ">>> Enabling and starting libvirtd service..."
    sudo systemctl enable --now libvirtd

    echo ">>> Starting default virtual network..."
    sudo virsh net-start default 2>/dev/null || true
    sudo virsh net-autostart default

    echo ">>> Adding current user to libvirt group..."
    sudo usermod -a -G libvirt "$(whoami)"
    echo "    Note: re-login is required for group changes to take effect."

    echo "[Step 2 completed]"
    return 0
}

step_3_aur() {
    step_header 3

    echo ">>> Configuring /etc/pacman.conf..."
    # Uncomment [multilib] and its Include line
    sudo sed -i '/^#\[multilib\]/,/^#Include/ s/^#//' /etc/pacman.conf
    echo "    [multilib] enabled."

    # Add archlinuxcn repository if not already present
    if ! grep -q '^\[archlinuxcn\]' /etc/pacman.conf; then
        sudo tee -a /etc/pacman.conf > /dev/null << 'EOF'

[archlinuxcn]
Server = https://mirrors.ustc.edu.cn/archlinuxcn/$arch
Server = https://mirrors.tuna.tsinghua.edu.cn/archlinuxcn/$arch
Server = https://mirrors.hit.edu.cn/archlinuxcn/$arch
Server = https://repo.huaweicloud.com/archlinuxcn/$arch
EOF
        echo "    [archlinuxcn] repository added."
    else
        echo "    [archlinuxcn] already present, skipping."
    fi

    echo ">>> Installing archlinuxcn-keyring and updating system..."
    sudo pacman -Sy --needed --noconfirm archlinuxcn-keyring
    sudo pacman -S --needed --noconfirm base-devel yay paru flclash
    sudo pacman -Syu --noconfirm

    echo "[Step 3 completed]"
    return 0
}

step_4_nvidia() {
    step_header 4
    echo ">>> Installing kernel headers..."
    sudo pacman -S --needed --noconfirm linux-headers linux-zen-headers

    echo ">>> Installing NVIDIA drivers..."
    sudo pacman -S --needed --noconfirm nvidia-dkms nvidia-utils nvidia-settings

    echo ""
    echo ">>> Adding nvidia modules to /etc/mkinitcpio.conf..."
    # Replace existing MODULES=() or #MODULES=() with nvidia modules
    sudo sed -i 's/^MODULES=()/MODULES=(nvidia nvidia_modeset nvidia_uvm nvidia_drm)/' /etc/mkinitcpio.conf
    sudo sed -i 's/^#MODULES=()/MODULES=(nvidia nvidia_modeset nvidia_uvm nvidia_drm)/' /etc/mkinitcpio.conf
    echo "    MODULES=(nvidia nvidia_modeset nvidia_uvm nvidia_drm) set."

    # Remove kms from HOOKS if present — kms conflicts with NVIDIA proprietary driver on Wayland
    if grep -q '^HOOKS=' /etc/mkinitcpio.conf && grep '^HOOKS=' /etc/mkinitcpio.conf | grep -q 'kms'; then
        echo "    Found kms in HOOKS, removing it (conflicts with NVIDIA proprietary driver)..."
        sudo sed -i '/^HOOKS=/ s/ *kms *//' /etc/mkinitcpio.conf
        echo "    kms removed from HOOKS."
    else
        echo "    kms not found in HOOKS, no change needed."
    fi

    echo ">>> Regenerating initramfs..."
    sudo mkinitcpio -P

    echo "[Step 4 completed]"
    return 0
}

step_5_zsh_kitty() {
    step_header 5
    echo ">>> Installing Zsh..."
    sudo pacman -S --needed --noconfirm zsh zsh-completions

    echo ">>> Listing available shells..."
    chsh -l

    echo ">>> Changing default shell to Zsh (password required)..."
    chsh -s /usr/bin/zsh || true

    echo ""
    echo ">>> Configuring Kitty terminal..."
    mkdir -p ~/.config/kitty
    # Append cursor settings if not already present
    if ! grep -q 'cursor_trail' ~/.config/kitty/kitty.conf 2>/dev/null; then
        cat >> ~/.config/kitty/kitty.conf << 'EOF'

cursor_trail 2
cursor_blink_interval 0.5
cursor_stop_blinking_after 0
EOF
        echo "    Kitty cursor settings added."
    else
        echo "    Kitty cursor settings already present, skipping."
    fi

    echo "[Step 5 completed]"
    return 0
}

step_6_antidote() {
    step_header 6
    check_zsh || { prompt_enter_or_quit "Press Enter to skip" || return 1; return 0; }

    echo ">>> Cleaning up any previous Antidote configuration..."
    rm -rf ~/.antidote 2>/dev/null || true
    # Remove existing Antidote block from .zshrc (between markers)
    sed -i '/^# === Antidote Start ===$/,/^# === Antidote End ===$/d' ~/.zshrc 2>/dev/null || true
    echo "    Cleanup done."

    echo ">>> Installing Antidote plugin manager..."
    git clone --depth=1 https://github.com/mattmc3/antidote.git ~/.antidote

    echo ""
    echo ">>> Creating ~/.zsh_plugins.txt with recommended plugins..."
    cat > ~/.zsh_plugins.txt << 'EOF'
zsh-users/zsh-completions
zsh-users/zsh-autosuggestions
zdharma-continuum/fast-syntax-highlighting
EOF
    echo "    Plugins configured."

    echo ""
    echo ">>> Appending Antidote configuration to ~/.zshrc..."
    cat >> ~/.zshrc << 'EOF'

# === Antidote Start ===
source ~/.antidote/antidote.zsh
antidote load ~/.zsh_plugins.txt

# 补全初始化（必须在 antidote load 之后）
autoload -Uz compinit && compinit -C
# === Antidote End ===
EOF
    echo "    Antidote configuration written to ~/.zshrc."

    echo "[Step 6 completed]"
    return 0
}

step_7_starship() {
    step_header 7
    check_zsh || { prompt_enter_or_quit "Press Enter to skip" || return 1; return 0; }

    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

    echo ">>> Installing Starship prompt..."
    sudo pacman -S --needed --noconfirm starship

    echo ""
    echo ">>> Copying Starship config to ~/.config/starship.toml..."
    mkdir -p ~/.config
    if [[ -f "$SCRIPT_DIR/starship/starship.toml" ]]; then
        cp "$SCRIPT_DIR/starship/starship.toml" ~/.config/starship.toml
        echo "    Starship config copied successfully."
        echo "    Prompt: 󰄛 ❯  (Catppuccin Macchiato palette)"
        echo "    Character: [󰄛](green) ❯  on success, [󰄛](red) ❯  on error"
    else
        echo "    Warning: starship/starship.toml not found, skipping."
    fi

    echo ""
    echo ">>> Adding Starship init to ~/.zshrc..."
    # Remove existing Starship init line to avoid duplicates
    sed -i '/^eval "\$\(starship init zsh\)"$/d' ~/.zshrc 2>/dev/null || true
    # Append after the Antidote block (or at end if Antidote not present)
    cat >> ~/.zshrc << 'EOF'

# Starship 提示符
eval "$(starship init zsh)"
EOF
    echo "    Starship init written to ~/.zshrc."

    echo "[Step 7 completed]"
    return 0
}

step_8_fastfetch() {
    step_header 8
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

    echo ">>> Copying fastfetch config to ~/.config/fastfetch..."
    mkdir -p ~/.config/fastfetch
    cp -r "$SCRIPT_DIR/fastfetch/"* ~/.config/fastfetch/
    echo "    fastfetch config copied successfully."

    echo "[Step 8 completed]"
    return 0
}

step_9_fastfetch_firstline() {
    step_header 9

    # Check if fastfetch is already the first line of ~/.zshrc
    if [[ -f ~/.zshrc ]] && head -1 ~/.zshrc | grep -q '^fastfetch$'; then
        echo ">>> fastfetch 已存在于 ~/.zshrc 第一行，正在移除（关闭自启）..."
        # Remove the first line (fastfetch) from .zshrc
        sed -i '1{/^fastfetch$/d}' ~/.zshrc
        echo "    fastfetch 已从 .zshrc 第一行移除。"
        echo "    ✅ 已关闭 fastfetch 开机自启。"
    else
        echo ">>> fastfetch 不在 ~/.zshrc 第一行，正在添加（开启自启）..."
        # Insert fastfetch as the first line
        if [[ ! -f ~/.zshrc ]]; then
            touch ~/.zshrc
        fi
        sed -i '1i\fastfetch' ~/.zshrc
        echo "    fastfetch 已添加为 .zshrc 第一行。"
        echo "    ✅ 已开启 fastfetch 开机自启。"
    fi

    echo "[Step 9 completed]"
    return 0
}

# ─────────────────────────────────────────────
# Menu rendering & navigation
# ─────────────────────────────────────────────

render_menu() {
    clear
    echo "════════════════════════════════════════════════════════════════"
    echo "          ArchInit — 可选扩展步骤 / Optional Steps"
    echo "════════════════════════════════════════════════════════════════"
    echo ""

    for i in "${!STEPS[@]}"; do
        local sel=" "
        local mark=" "

        if [[ ${COMPLETED[$i]} -eq 1 ]]; then
            mark="✓"
        fi

        if [[ $i -eq $SELECTED ]]; then
            sel=">"
            echo -e " ${sel} ${mark} Step $((i+1)): ${STEPS[$i]}"
        else
            echo -e "   ${mark} Step $((i+1)): ${STEPS[$i]}"
        fi
    done

    echo ""
    echo "════════════════════════════════════════════════════════════════"
    echo "                     ↑/↓ 导航 • Enter 执行 • q 退出"
    echo ""
}

# ─────────────────────────────────────────────
# Main menu loop
# ─────────────────────────────────────────────

main_menu() {
    # Read arrow keys and Enter
    while true; do
        render_menu

        # Read single keypress
        read -rsn1 key
        if [[ "$key" == $'\e' ]]; then
            # Escape sequence (arrow keys)
            read -rsn2 -t 0.1 seq 2>/dev/null || true
            case "$seq" in
                '[A')  # Up
                    ((SELECTED--))
                    if [[ $SELECTED -lt 0 ]]; then
                        SELECTED=$((${#STEPS[@]} - 1))
                    fi
                    ;;
                '[B')  # Down
                    ((SELECTED++))
                    if [[ $SELECTED -ge ${#STEPS[@]} ]]; then
                        SELECTED=0
                    fi
                    ;;
            esac
        elif [[ "$key" == "" ]] || [[ "$key" == $'\n' ]] || [[ "$key" == $'\r' ]]; then
            # Enter — execute selected step
            execute_step $SELECTED
        elif [[ "$key" == "q" ]] || [[ "$key" == "Q" ]]; then
            clear
            echo "========================================="
            echo " 已退出 / Exited"
            echo "========================================="
            exit 0
        fi
        # Ignore other keys
    done
}

# ─────────────────────────────────────────────
# Execute a step by index
# ─────────────────────────────────────────────

execute_step() {
    local idx=$1
    local step_num=$((idx + 1))
    local step_title="${STEPS[$idx]}"

    # Temporarily disable exit-on-error for step execution
    set +e

    case $step_num in
        1) step_1_kitty_font ;;
        2) step_2_kvm ;;
        3) step_3_aur ;;
        4) step_4_nvidia ;;
        5) step_5_zsh_kitty ;;
        6) step_6_antidote ;;
        7) step_7_starship ;;
        8) step_8_fastfetch ;;
        9) step_9_fastfetch_firstline ;;
    esac

    local ret=$?

    # Re-enable
    set -e

    echo ""
    if [[ $ret -eq 0 ]]; then
        # Success — mark as completed, show green, wait 5s, auto-return
        COMPLETED[$idx]=1
        echo -e "${GREEN}${BOLD}  ✅ Step ${step_num} completed: ${step_title}${RESET}"
        echo ""
        echo -e "${YELLOW}  ⏳ Returning to menu in 3 seconds...${RESET}"
        sleep 3
    else
        # Failure — show red, wait for Enter
        echo -e "${RED}${BOLD}  ❌ Step ${step_num} failed: ${step_title}${RESET}"
        echo ""
        echo -e "${RED}  Press Enter to return to menu...${RESET}"
        read -rs
    fi
}

# ─────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────

# Check for required commands
for cmd in pacman sudo; do
    if ! command -v $cmd >/dev/null 2>&1; then
        echo "Error: '$cmd' not found. This script must be run on Arch Linux."
        exit 1
    fi
done

# Trap Ctrl+C to clean up terminal
trap 'echo ""; echo "Interrupted."; exit 1' INT

# Hide cursor during menu
echo -ne "\e[?25l"

# Start main menu
main_menu

# Show cursor on exit
echo -ne "\e[?25h"
