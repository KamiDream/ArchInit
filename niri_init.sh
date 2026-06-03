#!/bin/bash

# Arch Linux initialization script (run as a normal user with sudo privileges)
# Interactive menu — use ↑/↓ to navigate, Enter to execute, q to quit.
# Manual edits will pause the script until the editor is closed.

set -uo pipefail

# ─────────────────────────────────────────────
# Step definitions
# ─────────────────────────────────────────────
STEPS=(
    "核心桌面环境 / Core Desktop (Niri)"
    "注册 DMS 服务 / Register DMS Service"
    "基础初始化 / Basic Initialization"
    "显示管理器 / Display Manager (LightDM)"
)

# 0 = pending, 1 = completed
COMPLETED=(0 0 0 0)

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
    read -rsn1 key
    if [[ "$key" == "q" ]] || [[ "$key" == "Q" ]]; then
        return 1
    fi
    if [[ "$key" != $'\n' ]] && [[ "$key" != $'\r' ]]; then
        read -r rest 2>/dev/null || true
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
# Step functions — return 0 on success, 1 if user quit
# ─────────────────────────────────────────────

step_1_core_desktop() {
    step_header 1
    echo ">>> Installing Niri and related components..."
    sudo pacman -Syu niri xwayland-satellite xdg-desktop-portal-gnome \
        xdg-desktop-portal-gtk kitty dms-shell-niri matugen cava \
        qt6-multimedia-ffmpeg lightdm lightdm-gtk-greeter power-profiles-daemon kimageformats

    echo "[Step 1 completed]"
    prompt_enter_or_quit || return 1
    return 0
}

step_2_register_dms() {
    step_header 2
    echo ">>> Registering DMS as a user service dependency of Niri..."
    curl -fsSL https://install.danklinux.com | sh
    systemctl --user add-wants niri.service dms

    echo "[Step 2 completed]"
    prompt_enter_or_quit || return 1
    return 0
}

step_3_init() {
    step_header 3
    echo ">>> Installing base packages..."
    sudo pacman -S --needed fastfetch fcitx5-im fcitx5-rime fuse2 ntfs-3g git quickshell flatseal dolphin kate firefox

    echo ""
    echo ">>> Next, edit /etc/locale.gen with vim"
    echo "    Find and uncomment 'zh_CN.UTF-8' (remove the leading #), then save and exit."
    prompt_enter_or_quit "Press Enter to open the editor" || return 1
    sudo vim /etc/locale.gen
    prompt_enter_or_quit "Edit complete. Press Enter to continue" || return 1

    echo ">>> Generating locale..."
    sudo locale-gen
    echo ">>> Setting system locale to zh_CN.UTF-8..."
    sudo localectl set-locale LANG=zh_CN.UTF-8

    echo ">>> Installing Chinese fonts & Nerd fonts..."
    sudo pacman -S --needed wqy-microhei wqy-microhei-lite wqy-bitmapfont wqy-zenhei \
        ttf-arphic-ukai ttf-arphic-uming noto-fonts-cjk ttf-jetbrains-mono-nerd

    echo "[Step 3 completed]"
    prompt_enter_or_quit || return 1
    return 0
}

step_4_lightdm() {
    step_header 4
    echo ">>> Enabling LightDM display manager..."
    sudo systemctl enable lightdm
    echo ">>> Starting LightDM..."
    sudo systemctl start lightdm

    echo "[Step 4 completed]"
    prompt_enter_or_quit || return 1
    return 0
}

# ─────────────────────────────────────────────
# Menu rendering & navigation
# ─────────────────────────────────────────────

render_menu() {
    clear
    echo "════════════════════════════════════════════════════════════════"
    echo "          ArchInit — 核心安装 / Core Setup"
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
    while true; do
        render_menu

        read -rsn1 key
        if [[ "$key" == $'\e' ]]; then
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
            execute_step $SELECTED
        elif [[ "$key" == "q" ]] || [[ "$key" == "Q" ]]; then
            clear
            echo "========================================="
            echo " 已退出 / Exited"
            echo "========================================="
            exit 0
        fi
    done
}

# ─────────────────────────────────────────────
# Execute a step by index
# ─────────────────────────────────────────────

execute_step() {
    local idx=$1
    local step_num=$((idx + 1))

    set +e

    case $step_num in
        1) step_1_core_desktop ;;
        2) step_2_register_dms ;;
        3) step_3_init ;;
        4) step_4_lightdm ;;
    esac

    local ret=$?
    set -e

    if [[ $ret -eq 0 ]]; then
        COMPLETED[$idx]=1
    fi
    sleep 0.3
}

# ─────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────

for cmd in pacman sudo; do
    if ! command -v $cmd >/dev/null 2>&1; then
        echo "Error: '$cmd' not found. This script must be run on Arch Linux."
        exit 1
    fi
done

trap 'echo ""; echo "Interrupted."; exit 1' INT

echo -ne "\e[?25l"

main_menu

echo -ne "\e[?25h"
