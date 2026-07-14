#!/bin/bash

# Supplementary script for ArchInit — awww wallpaper daemon setup
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
    "安装 awww + 设置自启 / Install awww + Enable autostart"
    "取消自启（保留服务文件） / Disable autostart (keep service file)"
    "启用自启 / Enable autostart"
    "彻底删除 awww / Completely remove awww"
)

# 0 = pending, 1 = completed
COMPLETED=(0 0 0 0 0 0 0 0 0 0 0)

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
    echo "                     ArchInit — awww 壁纸守护程序 / awww Wallpaper Daemon"
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
    local ret_val=0

    # Temporarily disable exit-on-error for step execution
    set +e

    case $step_num in
        # ─────────────────────────────────────
        1) # 安装 awww + 设置自启 / Install awww + Enable autostart
        # ─────────────────────────────────────
            step_header 1
            echo ">>> 安装 awww / Installing awww..."
            sudo pacman -Syu --noconfirm awww
            echo "    awww 安装完成 / installed."
            echo ""
            echo ">>> 创建用户级 Systemd 服务目录 / Creating user Systemd service directory..."
            mkdir -p ~/.config/systemd/user
            echo ""
            echo ">>> 写入 awww-daemon.service / Writing service file..."
            cat > ~/.config/systemd/user/awww-daemon.service << 'EOF'
[Unit]
Description=awww wallpaper daemon

[Service]
Type=simple
ExecStart=/usr/bin/awww-daemon
Restart=on-failure

[Install]
WantedBy=default.target
EOF
            echo "    服务文件已写入 ~/.config/systemd/user/awww-daemon.service"
            echo "    Service file written successfully."
            echo ""
            echo ">>> 重新加载 Systemd 用户配置 / Reloading Systemd user configuration..."
            systemctl --user daemon-reload
            echo ""
            echo ">>> 启用并启动 awww-daemon 服务 / Enabling and starting awww-daemon service..."
            systemctl --user enable awww-daemon.service
            systemctl --user start awww-daemon.service
            echo ""
            echo -e "${GREEN}    ✅ awww-daemon 服务已启用并启动 / Service enabled and started.${RESET}"
            echo "[Step 1 completed]"
            ;;

        # ─────────────────────────────────────
        2) # 取消自启（保留服务文件） / Disable autostart (keep service file)
        # ─────────────────────────────────────
            step_header 2
            echo ">>> 停止 awww-daemon 服务 / Stopping awww-daemon service..."
            systemctl --user stop awww-daemon.service
            echo "    服务已停止 / Service stopped."
            echo ""
            echo ">>> 禁用 awww-daemon 服务 / Disabling awww-daemon service..."
            systemctl --user disable awww-daemon.service
            echo "    服务已禁用 / Service disabled."
            echo ""
            echo -e "${YELLOW}    服务文件保留在 ~/.config/systemd/user/awww-daemon.service${RESET}"
            echo -e "${YELLOW}    Service file kept for future use.${RESET}"
            echo "[Step 2 completed]"
            ;;

        # ─────────────────────────────────────
        3) # 启用自启 / Enable autostart
        # ─────────────────────────────────────
            step_header 3
            # Check if service file exists
            if [[ ! -f ~/.config/systemd/user/awww-daemon.service ]]; then
                echo -e "${YELLOW}  ⚠️  服务文件不存在 / Service file not found.${RESET}"
                echo "    请先执行 Step 1 安装 awww / Please run Step 1 to install awww first."
                if ! prompt_enter_or_quit "按 Enter 返回菜单 / Press Enter to return"; then
                    ret_val=1
                fi
            else
                echo ">>> 启用并启动 awww-daemon 服务 / Enabling and starting awww-daemon service..."
                systemctl --user enable awww-daemon.service
                systemctl --user start awww-daemon.service
                echo ""
                echo -e "${GREEN}    ✅ awww-daemon 服务已启用并启动 / Service enabled and started.${RESET}"
                echo "[Step 3 completed]"
            fi
            ;;

        # ─────────────────────────────────────
        4) # 彻底删除 awww / Completely remove awww
        # ─────────────────────────────────────
            step_header 4
            echo ">>> 停止并禁用 awww-daemon 服务 / Stopping and disabling awww-daemon service..."
            systemctl --user stop awww-daemon.service 2>/dev/null || true
            systemctl --user disable awww-daemon.service 2>/dev/null || true
            echo "    服务已停止并禁用 / Service stopped and disabled."
            echo ""
            echo ">>> 删除服务文件 / Removing service file..."
            rm ~/.config/systemd/user/awww-daemon.service 2>/dev/null || true
            echo "    服务文件已删除 / Service file removed."
            echo ""
            echo ">>> 重新加载 Systemd 用户配置 / Reloading Systemd user configuration..."
            systemctl --user daemon-reload
            echo ""
            echo ">>> 卸载 awww 软件包 / Removing awww package..."
            sudo pacman -Rns --noconfirm awww
            echo ""
            echo -e "${GREEN}    ✅ awww 已彻底删除 / awww completely removed.${RESET}"
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
for cmd in pacman sudo systemctl; do
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
