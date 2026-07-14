#!/bin/bash

# Universal toolbox for ArchInit — general-purpose utilities
# Can be run independently or after niri_init.sh.
# Interactive menu — use ↑/↓ to navigate, Enter to execute, q to quit.
#
# Currently includes:
#   - UU Accelerator install for SteamDeck
#   - XDG user dirs migration to English names
#
# For phone users (UU Accelerator):
#   1. Install UU Accelerator console version on your phone first.
#   2. Run this script to install the SteamDeck client.
#   3. Then follow the "SteamDeck installation guide" in the phone app to complete the setup.

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
    "UU 加速器安装 / UU Accelerator Install"
    "XDG 用户目录转英文 / Migrate XDG Dirs to English"
)

# 0 = pending, 1 = completed
COMPLETED=(0 0)

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
# Helper: ensure Zsh is installed
# ─────────────────────────────────────────────
check_pacman() {
    if ! command -v pacman >/dev/null 2>&1; then
        echo "Warning: pacman does not appear to be installed."
        return 1
    fi
    return 0
}

# ─────────────────────────────────────────────
# Step functions — return 0 on success, 1 if user quit
# ─────────────────────────────────────────────

step_1_uu_accelerator() {
    step_header 1
    echo ">>> Installing UU Accelerator..."
    echo "    This will:"
    echo "      • Create /home/deck directory"
    echo "      • Set ownership to current user"
    echo "      • Download and run UU install script from uudeck.com"
    echo ""
    prompt_enter_or_quit "Press Enter to start installation" || return 1

    echo ">>> Creating /home/deck..."
    sudo mkdir /home/deck
    sudo chown "$(whoami)" /home/deck

    echo ">>> Downloading and running UU install script..."
    curl -s uudeck.com | sudo bash

    echo ""
    echo "[Step 1 completed]"
    return 0
}

# ─────────────────────────────────────
step_2_xdg_migrate() {
# ─────────────────────────────────────
    step_header 2

    # ── 1. Ensure xdg-user-dirs is installed ──
    echo ">>> 安装 xdg-user-dirs（如未安装）/ Installing xdg-user-dirs (if not present)..."
    sudo pacman -S --needed --noconfirm xdg-user-dirs

    # ── 2. Backup old config ──
    local user_dirs_conf="$HOME/.config/user-dirs.dirs"
    local user_dirs_bak="$HOME/.config/user-dirs.dirs.bak.$(date +%s)"
    if [[ -f "$user_dirs_conf" ]]; then
        cp "$user_dirs_conf" "$user_dirs_bak"
        echo "    原配置已备份到 / Old config backed up to: ${user_dirs_bak}"
        # Source old config to capture current paths (possibly Chinese names)
        source "$user_dirs_bak"
    else
        echo "    未发现现有配置，将创建全新配置 / No existing config found, creating fresh config."
    fi

    # ── 3. Define English path mapping ──
    # English directory names
    local EN_DESKTOP="$HOME/Desktop"
    local EN_DOWNLOAD="$HOME/Downloads"
    local EN_TEMPLATES="$HOME/Templates"
    local EN_PUBLIC="$HOME/Public"
    local EN_DOCUMENTS="$HOME/Documents"
    local EN_MUSIC="$HOME/Music"
    local EN_PICTURES="$HOME/Pictures"
    local EN_VIDEOS="$HOME/Videos"
    local EN_PROJECTS="$HOME/Projects"

    # ── 4. Write new config file directly with English paths ──
    echo ""
    echo ">>> 直接写入英文路径配置文件..."
    echo "    Writing config file with English paths directly..."

    mkdir -p "$(dirname "$user_dirs_conf")"
    cat > "$user_dirs_conf" << 'USERDIRSEOF'
# This file is written by ArchInit (universal.sh)
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
USERDIRSEOF
    echo "    ✅ 配置文件已写入 / Config written: ${user_dirs_conf}"

    # ── 5. Migrate contents from old Chinese dirs to new English dirs ──
    echo ""
    echo ">>> 迁移目录内容..."
    echo "    Migrating directory contents..."

    local migrated_count=0
    # Map: old variable name -> new path variable
    local migrator
    for migrator in \
        "XDG_DESKTOP_DIR:${EN_DESKTOP}" \
        "XDG_DOWNLOAD_DIR:${EN_DOWNLOAD}" \
        "XDG_TEMPLATES_DIR:${EN_TEMPLATES}" \
        "XDG_PUBLICSHARE_DIR:${EN_PUBLIC}" \
        "XDG_DOCUMENTS_DIR:${EN_DOCUMENTS}" \
        "XDG_MUSIC_DIR:${EN_MUSIC}" \
        "XDG_PICTURES_DIR:${EN_PICTURES}" \
        "XDG_VIDEOS_DIR:${EN_VIDEOS}" \
        "XDG_PROJECTS_DIR:${EN_PROJECTS}"; do

        local var_name="${migrator%%:*}"
        local en_path="${migrator##*:}"
        local old_path="${!var_name:-}"

        # Skip if old path wasn't set, or already same as English path
        if [[ -z "$old_path" || "$old_path" == "$en_path" ]]; then
            continue
        fi

        # Skip if old path doesn't exist on disk
        if [[ ! -d "$old_path" ]]; then
            continue
        fi

        echo ""
        echo "  发现旧目录 / Found old dir: ${old_path}"
        echo "  目标目录 / Target dir: ${en_path}"

        # Create new directory
        mkdir -p "$en_path"

        # Move contents (including hidden files)
        if ls -A "$old_path" &>/dev/null; then
            echo "    迁移内容中 / Migrating contents..."
            shopt -s dotglob
            mv "$old_path"/* "$en_path"/ 2>/dev/null || true
            shopt -u dotglob
            echo "    ✅ 内容已迁移 / Contents migrated."
        else
            echo "    目录为空，无需迁移 / Directory empty, no migration needed."
        fi

        # Remove old directory
        rmdir "$old_path" 2>/dev/null && \
            echo "    ✅ 旧目录已删除 / Old directory removed: ${old_path}" || \
            echo "    ⚠️  旧目录未能删除（可能仍有内容）/ Old dir not removed: ${old_path}"

        ((migrated_count++))
    done

    if [[ $migrated_count -eq 0 ]]; then
        echo "    无需迁移，目录名未改变 / No migration needed — directory names unchanged."
    else
        echo ""
        echo "    ✅ 共迁移 ${migrated_count} 个目录 / Total ${migrated_count} directories migrated."
    fi

    # ── 6. Run xdg-user-dirs-update as a no-op fallback ──
    # The file already exists with our config, so xdg-user-dirs-update
    # will respect it (it doesn't overwrite existing entries)
    echo ""
    echo ">>> 同步 xdg-user-dirs（保留已有配置）..."
    echo "    Syncing xdg-user-dirs (preserving existing config)..."
    xdg-user-dirs-update 2>/dev/null || true
    echo "    ✅ 同步完成 / Sync done."

    # ── 7. Done ──
    echo ""
    echo "    ✅ XDG 用户目录已切换为英文名 / XDG user dirs migrated to English names."
    echo "    系统 locale 仍为中文（zh_CN.UTF-8），不受影响。"
    echo "    System locale remains Chinese (zh_CN.UTF-8); unaffected."
    echo ""
    echo "    请重新登录后检查效果。备份文件可手动删除："
    echo "    Re-login to verify. Backup can be removed manually:"
    echo "      rm \"${user_dirs_bak}\""
    echo "[Step 2 completed]"
    return 0
}

# ─────────────────────────────────────────────
# Menu rendering & navigation
# ─────────────────────────────────────────────

render_menu() {
    clear
    print_logo
    echo ""
    echo "========================================================================================================================="
    echo "                     ArchInit — 其他扩展步骤 / Other Optional Steps"
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
            echo " 已退出 / Exited"
            echo "========================================================================================================================="
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
        1) step_1_uu_accelerator ;;
        2) step_2_xdg_migrate ;;
    esac

    local ret=$?

    # Restore errexit to original state (script starts without -e)
    set +e

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
for cmd in sudo curl pacman; do
    if ! command -v $cmd >/dev/null 2>&1; then
        echo "Error: '$cmd' not found. Please install it first."
        exit 1
    fi
done

# Hide cursor during menu
echo -ne "\e[?25l"

# Start main menu
main_menu

# Show cursor on exit
echo -ne "\e[?25h"
