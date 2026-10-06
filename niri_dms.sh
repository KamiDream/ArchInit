#!/bin/bash

# Arch Linux initialization script — Niri + DMS one-click setup
# Run this script as a normal user with sudo privileges.
# Interactive menu — use ↑/↓ to navigate, Enter to execute, q to quit.

set -uo pipefail
# Note: we do NOT use 'set -e' so that step functions can return 1 gracefully

# ─── Error handling ──────────────────────────
# Ensure cleanup on Ctrl+C
cleanup() {
    echo "" >&2
    echo -e "${YELLOW}  ⚠️  Script interrupted by user.${RESET}" >&2
    exit 1
}
trap 'cleanup' INT
# ─────────────────────────────────────────────

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
# Step definitions
# ─────────────────────────────────────────────
STEPS=(
    "Core Desktop (Niri)"
    "Register DMS Service"
    "Basic Initialization"
    "Display Manager (LightDM)"
)

# 0 = pending, 1 = completed
COMPLETED=(0 0 0 0)

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
    echo "========================================================================================================================="
    echo " Step $num: $title"
    echo "========================================================================================================================="
}

# ─────────────────────────────────────────────
# Menu rendering & navigation
# ─────────────────────────────────────────────

render_menu() {
    clear
    print_logo
    echo ""
    echo "========================================================================================================================="
    echo "                     ArchInit — Niri DMS Setup"
    echo "========================================================================================================================="
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
    echo "═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════"
    echo "                     ↑/↓ Navigate • Enter Execute • q Quit"
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
            local seq=""
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
            echo "========================================================================================================================="
            echo " Exited"
            echo "========================================================================================================================="
            exit 0
        fi
        # Ignore other keys
    done
}

# ─────────────────────────────────────────────
# Execute a step by index — all logic inlined in case statement
# ─────────────────────────────────────────────

execute_step() {
    local idx=$1
    local step_num=$((idx + 1))
    local step_title="${STEPS[$idx]}"
    local ret_val=0
    local SCRIPT_DIR
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

    # Temporarily disable exit-on-error for step execution
    set +e

    case $step_num in
        # ─────────────────────────────────────
        1) # Core Desktop (Niri)
        # ─────────────────────────────────────
            step_header 1
            echo ">>> Installing Niri and related components..."
            sudo pacman -Syu --needed --noconfirm niri xwayland-satellite xdg-desktop-portal-gnome \
                xdg-desktop-portal-gtk kitty dms-shell matugen cava \
                qt6-multimedia-ffmpeg lightdm lightdm-gtk-greeter kimageformats power-profiles-daemon cups-pk-helper
            echo "[Step 1 completed]"
            ;;

        # ─────────────────────────────────────
        2) # Register DMS Service
        # ─────────────────────────────────────
            step_header 2
            echo ">>> Registering DMS as a user service dependency of Niri..."
            curl -fsSL https://install.danklinux.com | sh
            echo "[Step 2 completed]"
            ;;

        # ─────────────────────────────────────
        3) # Basic Initialization
        # ─────────────────────────────────────
            step_header 3
            echo ">>> Installing base packages..."
            sudo pacman -S --needed --noconfirm fastfetch fcitx5-im fcitx5-rime fuse2 ntfs-3g vim quickshell firefox

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
                ttf-arphic-ukai ttf-arphic-uming noto-fonts-cjk ttf-jetbrains-mono-nerd noto-fonts-emoji \
                ttf-fira-code inter-font

            echo ""
            echo ">>> Configuring XDG user directories with English names..."
            # Install xdg-user-dirs if not already present
            sudo pacman -S --needed --noconfirm xdg-user-dirs
            # Directly write config with English paths — more reliable than LANG override
            mkdir -p ~/.config
            cat > ~/.config/user-dirs.dirs << 'EOF'
# This file is written by ArchInit (niri_dms.sh)
# XDG user directories with English names
# System locale remains Chinese (zh_CN.UTF-8)
#
XDG_DESKTOP_DIR="$HOME/Desktop"
XDG_DOWNLOAD_DIR="$HOME/Downloads"
XDG_TEMPLATES_DIR="$HOME/Templates"
XDG_PUBLICSHARE_DIR="$HOME/Public"
XDG_DOCUMENTS_DIR="$HOME/Documents"
XDG_MUSIC_DIR="$HOME/Music"
XDG_PICTURES_DIR="$HOME/Pictures"
XDG_VIDEOS_DIR="$HOME/Videos"
XDG_PROJECTS_DIR="$HOME/Projects"
EOF
            # Create the English directories if they don't exist
            mkdir -p ~/Desktop ~/Downloads ~/Templates ~/Public ~/Documents ~/Music ~/Pictures ~/Videos ~/Projects
            # Sync with xdg-user-dirs-update (respects existing config)
            xdg-user-dirs-update 2>/dev/null || true
            echo "    XDG user directories configured with English names."
            echo "    (Desktop, Downloads, Documents, Pictures, Music, Videos, Public, Templates, Projects)"

            echo "[Step 3 completed]"
            ;;

        # ─────────────────────────────────────
        4) # Display Manager (LightDM)
        # ─────────────────────────────────────
            step_header 4
            echo ">>> Enabling LightDM display manager..."
            sudo systemctl enable lightdm
            echo ">>> Starting LightDM..."
            sudo systemctl start lightdm
            echo "[Step 4 completed]"
            ;;

    esac

    # Restore errexit to original state (script starts without -e)
    set +e

    echo ""
    if [[ $ret_val -eq 0 ]]; then
        # Success — mark as completed, show green, wait 3s, auto-return
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

# Initial privilege escalation & keep-alive
print_logo
echo "═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════"
echo "  ArchInit — Niri DMS Setup"
echo "═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════"
echo ""
echo ">>> Requesting sudo access (password required)..."
sudo -v

# Keep sudo session alive in the background
while true; do sudo -n true; sleep 60; kill -0 "$$" 2>/dev/null || break; done 2>/dev/null &

echo "    ✅ Sudo privileges acquired."
echo ""
sleep 1

# Hide cursor during menu
echo -ne "\e[?25l"

# Start main menu
main_menu

# Show cursor on exit
echo -ne "\e[?25h"
