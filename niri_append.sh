#!/bin/bash

# Supplementary script for ArchInit — optional environment setup
# Run after niri_init.sh if you need additional components.
# Interactive menu — use ↑/↓ to navigate, Enter to execute, q to quit.
# Manual edits will pause the script until the editor is closed.

set -uo pipefail
# Note: we do NOT use 'set -e' so that step functions can return 1 gracefully

# ─────────────────────────────────────────────
# Step definitions
# ─────────────────────────────────────────────
STEPS=(
    "KVM 虚拟化 / KVM Virtualization"
    "AUR 助手 / AUR Helper (yay / paru)"
    "NVIDIA 显卡驱动 / NVIDIA Graphics Driver"
    "终端美化 / Terminal Customization (Zsh & Kitty)"
    "Zinit 插件管理器 / Zinit Plugin Manager"
    "Powerlevel10k 主题 / Powerlevel10k Theme"
    "fastfetch 配置 / fastfetch Configuration"
    "配置 fastfetch 启动 / Configure fastfetch on startup"
)

# 0 = pending, 1 = completed
COMPLETED=(0 0 0 0 0 0 0 0)

CURRENT_STEP=-1   # -1 means at menu, >=0 means inside a step
SELECTED=0
SAVED_STDERR=""   # placeholder

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
    read -rsn1 key
    if [[ "$key" == "q" ]] || [[ "$key" == "Q" ]]; then
        return 1   # signal quit
    fi
    # Flush any leftover input (e.g. \n after \r on some terminals)
    read -rsn1 -t 0.1 flush 2>/dev/null || true
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

step_1_kvm() {
    step_header 1
    echo ">>> Installing KVM packages..."
    sudo pacman -S --needed qemu-full virt-manager swtpm dnsmasq || return 0

    echo ">>> Enabling and starting libvirtd service..."
    sudo systemctl enable --now libvirtd

    echo ">>> Starting default virtual network..."
    sudo virsh net-start default 2>/dev/null || true
    sudo virsh net-autostart default

    echo ">>> Adding current user to libvirt group..."
    sudo usermod -a -G libvirt "$(whoami)"
    echo "    Note: re-login is required for group changes to take effect."

    echo "[Step 1 completed]"
    prompt_enter_or_quit || return 1
    return 0
}

step_2_aur() {
    step_header 2
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
    prompt_enter_or_quit "Press Enter to open the editor" || return 1
    sudo vim /etc/pacman.conf
    prompt_enter_or_quit "Edit complete. Press Enter to continue" || return 1

    echo ">>> Installing archlinuxcn-keyring and updating system..."
    sudo pacman -Sy --needed archlinuxcn-keyring
    sudo pacman -S --needed base-devel yay paru flclash
    sudo pacman -Syu

    echo "[Step 2 completed]"
    prompt_enter_or_quit || return 1
    return 0
}

step_3_nvidia() {
    step_header 3
    echo ">>> Installing kernel headers..."
    sudo pacman -S --needed linux-headers linux-zen-headers

    echo ">>> Installing NVIDIA drivers..."
    sudo pacman -S --needed nvidia-dkms nvidia-utils nvidia-settings

    echo ""
    echo ">>> Next, edit /etc/mkinitcpio.conf, add nvidia modules to MODULES=():"
    echo "    MODULES=(nvidia nvidia_modeset nvidia_uvm nvidia_drm)"
    prompt_enter_or_quit "Press Enter to open the editor" || return 1
    sudo vim /etc/mkinitcpio.conf
    prompt_enter_or_quit "Edit complete. Press Enter to continue" || return 1

    echo ">>> Regenerating initramfs..."
    sudo mkinitcpio -P

    echo "[Step 3 completed]"
    prompt_enter_or_quit || return 1
    return 0
}

step_4_zsh_kitty() {
    step_header 4
    echo ">>> Installing Zsh..."
    sudo pacman -S --needed zsh zsh-completions

    echo ">>> Listing available shells..."
    chsh -l

    echo ">>> Changing default shell to Zsh (password required)..."
    chsh -s /usr/bin/zsh || true

    echo ""
    echo ">>> Next, edit Kitty terminal config ~/.config/kitty/kitty.conf"
    echo "    Content to add:"
    echo "    cursor_trail 2"
    echo "    cursor_blink_interval 0.5"
    echo "    cursor_stop_blinking_after 0"
    prompt_enter_or_quit "Press Enter to open the editor" || return 1
    kate ~/.config/kitty/kitty.conf
    prompt_enter_or_quit "Edit complete. Press Enter to continue" || return 1

    echo "[Step 4 completed]"
    prompt_enter_or_quit || return 1
    return 0
}

step_5_zinit() {
    step_header 5
    check_zsh || { prompt_enter_or_quit "Press Enter to skip" || return 1; return 0; }

    echo ">>> Installing Zinit plugin manager..."
    bash -c "$(curl --fail --show-error --silent --location \
        https://raw.githubusercontent.com/zdharma-continuum/zinit/main/scripts/install.sh)"

    echo ""
    echo ">>> Next, edit ~/.zshrc with Kate, add the following content AFTER the line"
    echo "    'source \"\$HOME/.zinit/bin/zinit.zsh\"' (which was added by the installer):"
    echo ""
    echo "    # Load plugins"
    echo "    zinit light zsh-users/zsh-autosuggestions"
    echo "    zinit light zsh-users/zsh-syntax-highlighting"
    echo "    zinit light zsh-users/zsh-history-substring-search"
    echo ""
    echo "    ⚠️  Make sure fastfetch is the first line of ~/.zshrc (will be configured in Step 8)."
    prompt_enter_or_quit "Press Enter to open the editor" || return 1
    kate ~/.zshrc
    prompt_enter_or_quit "Edit complete. Press Enter to continue" || return 1

    echo "[Step 5 completed]"
    prompt_enter_or_quit || return 1
    return 0
}

step_6_p10k() {
    step_header 6
    check_zsh || { prompt_enter_or_quit "Press Enter to skip" || return 1; return 0; }

    echo ""
    echo ">>> Next, edit ~/.zshrc with Kate, add the following lines AFTER the plugin list:"
    echo ""
    echo "    # Load Powerlevel10k theme"
    echo "    zinit ice depth=1"
    echo "    zinit light romkatv/powerlevel10k"
    echo ""
    echo "    ⚠️  Powerlevel10k will prompt for configuration on first shell start."
    echo "       If you see 'instant prompt warning', run Step 8 to add fastetch as the first line."
    prompt_enter_or_quit "Press Enter to open the editor" || return 1
    kate ~/.zshrc
    prompt_enter_or_quit "Edit complete. Press Enter to continue" || return 1

    echo "[Step 6 completed]"
    prompt_enter_or_quit || return 1
    return 0
}

step_7_fastfetch() {
    step_header 7
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

    echo ">>> Copying fastfetch config to ~/.config/fastfetch..."
    mkdir -p ~/.config/fastfetch
    cp -r "$SCRIPT_DIR/fastfetch/"* ~/.config/fastfetch/
    echo "    fastfetch config copied successfully."
    echo ""
    echo ">>> Running Kitty font selector, choose JetBrains Mono..."
    prompt_enter_or_quit "Press Enter to launch font selector" || return 1
    kitten choose-fonts
    prompt_enter_or_quit "Font selected. Press Enter to continue" || return 1

    echo "[Step 7 completed]"
    prompt_enter_or_quit || return 1
    return 0
}

step_8_fastfetch_firstline() {
    step_header 8
    echo ">>> Adding fastfetch as the first line of ~/.zshrc..."
    echo ""
    echo "    Open ~/.zshrc with Kate and add 'fastfetch' as the FIRST line."
    echo "    ⚠️  fastfetch must be the very first line, before any Zinit/Powerlevel10k init code,"
    echo "       otherwise Powerlevel10k's instant prompt will show a warning."
    echo ""
    echo "    Your ~/.zshrc should look like:"
    echo "    ─────────────────────────────────"
    echo "    fastfetch"
    echo "    source \"\$HOME/.zinit/bin/zinit.zsh\""
    echo "    # ... plugins, theme ..."
    echo "    ─────────────────────────────────"
    prompt_enter_or_quit "Press Enter to open the editor" || return 1
    kate ~/.zshrc
    prompt_enter_or_quit "Edit complete. Press Enter to continue" || return 1

    echo "[Step 8 completed]"
    prompt_enter_or_quit || return 1
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

    # Temporarily disable exit-on-error for step execution
    set +e

    case $step_num in
        1) step_1_kvm ;;
        2) step_2_aur ;;
        3) step_3_nvidia ;;
        4) step_4_zsh_kitty ;;
        5) step_5_zinit ;;
        6) step_6_p10k ;;
        7) step_7_fastfetch ;;
        8) step_8_fastfetch_firstline ;;
    esac

    local ret=$?

    # Re-enable
    set -e

    if [[ $ret -eq 0 ]]; then
        COMPLETED[$idx]=1
    fi
    # If ret == 1 (user quit), we simply return to menu without marking completed
    # If ret == 0, we mark completed and return to menu
    # Sleep a tiny bit so the user can see the final message before menu redraws
    sleep 0.3
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
