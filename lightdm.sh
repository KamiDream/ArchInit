#!/bin/bash

# Supplementary script for ArchInit — LightDM WebKit2 Greeter setup
# Run after niri_init.sh if you need a graphical login manager.
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
    "安装 LightDM WebKit2 Greeter / Install LightDM WebKit2 Greeter"
    "安装 KamiDream 主题 / Install KamiDream Theme"
    "启用 LightDM 配置 / Enable LightDM Configuration"
    "黑屏救急 / Black Screen Emergency Fix"
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
    echo "                     ArchInit — LightDM WebKit2 Greeter 配置"
    echo "========================================================================================================================="
    echo ""
    echo -e "  ${YELLOW}${BOLD}⚠️  警告 / WARNING${RESET}"
    echo -e "  ${YELLOW}  单 N 卡独显或开启了独显直连的用户（纯 N 卡用户）请勿使用此配置！${RESET}"
    echo -e "  ${YELLOW}  Do NOT use this configuration if you have a single/primary NVIDIA GPU!${RESET}"
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
    local ret_val=0
    local SCRIPT_DIR
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

    # Temporarily disable exit-on-error for step execution
    set +e

    case $step_num in
        # ─────────────────────────────────────
        1) # 安装 LightDM WebKit2 Greeter
        # ─────────────────────────────────────
            step_header 1
            echo ">>> 安装 lightdm-webkit2-greeter..."
            echo "    Installing lightdm-webkit2-greeter..."
            sudo pacman -S --needed --noconfirm lightdm-webkit2-greeter
            echo ""
            echo -e "${GREEN}    ✅ lightdm-webkit2-greeter 安装完成 / installed successfully.${RESET}"
            echo "[Step 1 completed]"
            ;;

        # ─────────────────────────────────────
        2) # 安装/更新 KamiDream 主题
        # ─────────────────────────────────────
            step_header 2
            echo ">>> 清理旧主题（如果存在）..."
            echo "    Cleaning up old theme (if exists)..."
            if [[ -d "/usr/share/lightdm-webkit/themes/KamiDream_Theme" ]]; then
                sudo rm -rf /usr/share/lightdm-webkit/themes/KamiDream_Theme
                echo "    ✅ 旧主题已删除 / Old theme removed."
            else
                echo "    ⏭️  未发现旧主题，跳过 / No old theme found, skipping."
            fi
            echo ""
            echo ">>> 克隆 KamiDream LightDM WebKit2 主题..."
            echo "    Cloning KamiDream LightDM WebKit2 theme..."
            local theme_dir="$HOME/LdmWk2Theme"
            if [[ -d "$theme_dir" ]]; then
                rm -rf "$theme_dir"
            fi
            git clone https://github.com/KamiDream/LdmWk2Theme.git "$theme_dir"
            echo ""
            echo ">>> 创建目标目录并移动主题..."
            echo "    Creating target directory and moving theme..."
            sudo mkdir -p /usr/share/lightdm-webkit/themes/
            sudo mv "$theme_dir" /usr/share/lightdm-webkit/themes/KamiDream_Theme
            echo ""
            echo -e "${GREEN}    ✅ KamiDream 主题已安装/更新到 /usr/share/lightdm-webkit/themes/KamiDream_Theme${RESET}"
            echo "    Theme installed/updated successfully."
            echo ""
            echo "    🖼️  如需替换背景图片，请替换以下文件："
            echo "       /usr/share/lightdm-webkit/themes/KamiDream_Theme/assets/background.png"
            echo "       To replace the background image, replace the file above with your own."
            echo "[Step 2 completed]"
            ;;

        # ─────────────────────────────────────
        3) # 启用 LightDM 配置
        # ─────────────────────────────────────
            step_header 3
            echo ">>> 配置 /etc/lightdm/lightdm.conf..."
            echo "    Configuring /etc/lightdm/lightdm.conf..."
            # Ensure the directory exists
            sudo mkdir -p /etc/lightdm
            # Set greeter-session in [Seat:*] section
            if grep -q '^\[Seat:\*\]' /etc/lightdm/lightdm.conf 2>/dev/null; then
                # Section exists — update or add greeter-session line after it
                if grep -q '^greeter-session=' /etc/lightdm/lightdm.conf; then
                    sudo sed -i 's/^greeter-session=.*/greeter-session=lightdm-webkit2-greeter/' /etc/lightdm/lightdm.conf
                else
                    sudo sed -i '/^\[Seat:\*\]/a greeter-session=lightdm-webkit2-greeter' /etc/lightdm/lightdm.conf
                fi
            else
                # Section doesn't exist — append it
                echo -e "[Seat:*]\ngreeter-session=lightdm-webkit2-greeter" | sudo tee -a /etc/lightdm/lightdm.conf > /dev/null
            fi
            echo "    /etc/lightdm/lightdm.conf 已配置 / configured."
            echo ""
            echo ">>> 配置 /etc/lightdm/lightdm-webkit2-greeter.conf..."
            echo "    Configuring /etc/lightdm/lightdm-webkit2-greeter.conf..."
            # Replace existing webkit_theme line (e.g. "webkit_theme        = antergos")
            # with "webkit_theme        = KamiDream_Theme", preserving spacing format
            if grep -q '^webkit_theme' /etc/lightdm/lightdm-webkit2-greeter.conf 2>/dev/null; then
                sudo sed -i 's/^webkit_theme\s*=.*/webkit_theme        = KamiDream_Theme/' /etc/lightdm/lightdm-webkit2-greeter.conf
                echo "    webkit_theme 已更新为 KamiDream_Theme / updated."
            else
                # No webkit_theme line found — append under [greeter] or at end
                echo -e "[greeter]\nwebkit_theme        = KamiDream_Theme" | sudo tee -a /etc/lightdm/lightdm-webkit2-greeter.conf > /dev/null
                echo "    webkit_theme 已添加 / added."
            fi
            echo "    /etc/lightdm/lightdm-webkit2-greeter.conf 已配置 / configured."
            echo ""
            echo -e "${GREEN}    ✅ LightDM 配置完成 / Configuration complete.${RESET}"
            echo ""
            echo "========================================================================================================================="
            echo -e " ${YELLOW}${BOLD}  ⚠️  请重启系统以应用 LightDM 登录管理器 / Please reboot to apply LightDM${RESET}"
            echo "     重启命令 / Reboot command: sudo reboot"
            echo "     或 / Or: sudo systemctl reboot"
            echo "========================================================================================================================="
            echo ""
            if ! prompt_enter_or_quit "按 Enter 继续 / Press Enter to continue"; then
                ret_val=1
            fi
            echo "[Step 3 completed]"
            ;;

        # ─────────────────────────────────────
        4) # 黑屏救急 — 注释 WebKit2 Greeter 配置并重启 LightDM
        # ─────────────────────────────────────
            step_header 4
            echo ">>> 注释 /etc/lightdm/lightdm.conf 中的 greeter-session=lightdm-webkit2-greeter..."
            echo "    Commenting out greeter-session=lightdm-webkit2-greeter in /etc/lightdm/lightdm.conf..."
            if grep -q '^greeter-session=lightdm-webkit2-greeter' /etc/lightdm/lightdm.conf 2>/dev/null; then
                sudo sed -i 's/^greeter-session=lightdm-webkit2-greeter/#greeter-session=lightdm-webkit2-greeter/' /etc/lightdm/lightdm.conf
                echo -e "${GREEN}    ✅ 已注释 greeter-session 行 / Commented out.${RESET}"
            else
                echo -e "${YELLOW}    ⏭️  未找到 greeter-session=lightdm-webkit2-greeter，可能已被注释 / Not found, may already be commented.${RESET}"
            fi
            echo ""
            echo ">>> 重启 LightDM 服务..."
            echo "    Restarting LightDM service..."
            sudo systemctl restart lightdm
            echo ""
            echo -e "${GREEN}    ✅ LightDM 已重启，已恢复默认 Greeter / LightDM restarted, default greeter restored.${RESET}"
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

# Hide cursor during menu
echo -ne "\e[?25l"

# Start main menu
main_menu

# Show cursor on exit
echo -ne "\e[?25h"
