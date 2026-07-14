#!/bin/bash

# Supplementary script for ArchInit — optional environment setup
# Run after niri_init.sh if you need additional components.
# Interactive menu — use ↑/↓ to navigate, Enter to execute, q to quit.
# Manual edits will pause the script until the editor is closed.

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
    "Kitty 字体选择 / Kitty Font Selector"
    "KVM 虚拟化 / KVM Virtualization"
    "AUR 助手 / AUR Helper (yay / paru)"
    "NVIDIA 显卡驱动 / NVIDIA Graphics Driver"
    "启用 Zsh 终端 / Enable Zsh Shell"
    "Antidote 插件管理器 / Antidote Plugin Manager"
    "Starship 提示符 / Starship Prompt"
    "fastfetch 配置 / fastfetch Configuration"
    "配置 fastfetch 启动 / Configure fastfetch on startup"
    "Kitty 背景透明度 / Kitty Background Opacity"
    "雾凇拼音 / Rime-ice Input Method"
    "XDG 用户目录转英文 / Migrate XDG Dirs to English"
)

# 0 = pending, 1 = completed
COMPLETED=(0 0 0 0 0 0 0 0 0 0 0 0)

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
check_zsh() {
    if ! command -v zsh >/dev/null 2>&1; then
        echo "Warning: Zsh does not appear to be installed."
        return 1
    fi
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
    echo "                     ArchInit — 可选扩展步骤 / Optional Steps"
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
# Execute a step by index — all logic inlined in case statement (like install.sh)
# ─────────────────────────────────────────────

execute_step() {
    local idx=$1
    local step_num=$((idx + 1))
    local step_title="${STEPS[$idx]}"
    local ret_val=0
    local SCRIPT_DIR choice new_opacity kitty_conf current_opacity
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

    # Temporarily disable exit-on-error for step execution
    set +e

    case $step_num in
        # ─────────────────────────────────────
        1) # Kitty 字体选择 / Kitty Font Selector
        # ─────────────────────────────────────
            step_header 1
            echo ">>> Running Kitty font selector, choose JetBrains Mono..."
            if prompt_enter_or_quit "Press Enter to launch font selector"; then
                kitten choose-fonts
                # Restore terminal settings in case kitten choose-fonts left them modified
                stty sane 2>/dev/null || true
                prompt_enter_or_quit "Font selected. Press Enter to continue" || true
                echo "[Step 1 completed]"
            else
                ret_val=1
            fi
            ;;

        # ─────────────────────────────────────
        2) # KVM 虚拟化 / KVM Virtualization
        # ─────────────────────────────────────
            step_header 2
            echo ">>> Installing KVM packages..."
            sudo pacman -S --needed --noconfirm qemu-full virt-manager swtpm dnsmasq
            echo ">>> Enabling and starting libvirtd service..."
            sudo systemctl enable --now libvirtd
            echo ">>> Starting default virtual network..."
            sudo virsh net-start default 2>/dev/null || true
            sudo virsh net-autostart default
            echo ">>> Adding current user to libvirt group..."
            sudo usermod -a -G libvirt "$(whoami)"
            echo "    Note: re-login is required for group changes to take effect."
            echo "[Step 2 completed]"
            ;;

        # ─────────────────────────────────────
        3) # AUR 助手 / AUR Helper (yay / paru)
        # ─────────────────────────────────────
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
            ;;

        # ─────────────────────────────────────
        4) # NVIDIA 显卡驱动 / NVIDIA Graphics Driver
        # ─────────────────────────────────────
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
            ;;

        # ─────────────────────────────────────
        5) # 启用 Zsh 终端 / Enable Zsh Shell
        # ─────────────────────────────────────
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
            ;;

        # ─────────────────────────────────────
        6) # Antidote 插件管理器 / Antidote Plugin Manager
        # ─────────────────────────────────────
            step_header 6
            if ! check_zsh; then
                if ! prompt_enter_or_quit "Press Enter to skip"; then
                    ret_val=1
                fi
            else
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

# ─── 命令历史记录配置（仅记录用户主动输入的命令）────────────
HISTFILE=~/.zsh_history
HISTSIZE=100000
SAVEHIST=100000
setopt SHARE_HISTORY           # 在多个终端会话间实时共享历史
setopt HIST_EXPIRE_DUPS_FIRST  # 历史存满时优先删除重复项
setopt HIST_IGNORE_ALL_DUPS    # 若新命令与历史重复则删除旧条目
setopt HIST_IGNORE_DUPS        # 连续重复的命令只保留一条
setopt HIST_IGNORE_SPACE       # 忽略以空格开头的命令（如自动运行的脚本）
setopt HIST_REDUCE_BLANKS      # 去除命令中多余的空格
setopt HIST_NO_FUNCTIONS       # 不记录函数定义
setopt HIST_NO_STORE           # 不记录 history 命令本身

# ─── 补全初始化（必须在 antidote load 之后）────────────────
autoload -Uz compinit && compinit -C

# ─── 补全系统配置：启用方向键菜单选择 ─────────────────────
# 核心：按 Tab 后使用 ↑/↓ 方向键自由选择补全项
# （"menu select" 是让用户能用方向键导航的关键配置）
zstyle ':completion:*' menu select

# 补全列表颜色
zstyle ':completion:*' list-colors ''
zstyle ':completion:*' list-prompt '%S%l 个匹配项 %s'

# 智能大小写匹配（例：README 输入 readme 也能匹配）
zstyle ':completion:*' matcher-list 'm:{a-zA-Z}={A-Za-z}' 'r:|=*' 'l:|=* r:|=*'

# 补全描述美化
zstyle ':completion:*:descriptions' format '%U%F{cyan}── %d ──%f%u'
zstyle ':completion:*:messages' format ' %F{red}── %d ──%f'
zstyle ':completion:*:warnings' format ' %F{yellow}── 无匹配结果 ──%f'
zstyle ':completion:*:corrections' format '%U%F{green}── %d ──%f%u'

# 分组显示（先显示普通补全，再显示额外说明）
zstyle ':completion:*' group-name ''
zstyle ':completion:*' verbose yes

# 缓存提升性能
zstyle ':completion:*' use-cache on
zstyle ':completion:*' cache-path ~/.zsh/cache
# === Antidote End ===
EOF
                echo "    Antidote configuration written to ~/.zshrc."
                echo "[Step 6 completed]"
            fi
            ;;

        # ─────────────────────────────────────
        7) # Starship 提示符 / Starship Prompt
        # ─────────────────────────────────────
            step_header 7
            if ! check_zsh; then
                if ! prompt_enter_or_quit "Press Enter to skip"; then
                    ret_val=1
                fi
            else
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
            fi
            ;;

        # ─────────────────────────────────────
        8) # fastfetch 配置 / fastfetch Configuration
        # ─────────────────────────────────────
            step_header 8
            echo ">>> Copying fastfetch config to ~/.config/fastfetch..."
            mkdir -p ~/.config/fastfetch
            cp -r "$SCRIPT_DIR/fastfetch/"* ~/.config/fastfetch/
            echo "    fastfetch config copied successfully."
            echo "[Step 8 completed]"
            ;;

        # ─────────────────────────────────────
        9) # 配置 fastfetch 启动 / Configure fastfetch on startup
        # ─────────────────────────────────────
            step_header 9
            # Check if fastfetch (with or without leading space) is already the first line
            if [[ -f ~/.zshrc ]] && head -1 ~/.zshrc | grep -qE '^\s?fastfetch$'; then
                echo ">>> fastfetch 已存在于 ~/.zshrc 第一行，正在移除（关闭自启）..."
                # Remove the first line (fastfetch or  fastfetch) from .zshrc
                sed -i '1{/^\s\?fastfetch$/d}' ~/.zshrc
                echo "    fastfetch 已从 .zshrc 第一行移除。"
                echo "    ✅ 已关闭 fastfetch 开机自启。"
            else
                echo ">>> fastfetch 不在 ~/.zshrc 第一行，正在添加（开启自启）..."
                # Insert fastfetch 时加前导空格（利用 HIST_IGNORE_SPACE 避免被记入历史）
                if [[ ! -f ~/.zshrc ]]; then
                    touch ~/.zshrc
                fi
                sed -i '1i\ fastfetch' ~/.zshrc
                echo "    fastfetch 已添加为 .zshrc 第一行（带前导空格，不记入历史）。"
                echo "    ✅ 已开启 fastfetch 开机自启。"
            fi
            echo "[Step 9 completed]"
            ;;

        # ─────────────────────────────────────
        10) # Kitty 背景透明度 / Kitty Background Opacity
        # ─────────────────────────────────────
            step_header 10
            kitty_conf="$HOME/.config/kitty/kitty.conf"
            if [[ ! -f "$kitty_conf" ]]; then
                echo -e "${YELLOW}  ⚠️  Kitty 配置文件不存在 / Kitty config not found at ${kitty_conf}${RESET}"
                echo "    请先执行 Step 5 (Kitty 终端配置) / Please run Step 5 first."
                if ! prompt_enter_or_quit "按 Enter 返回菜单 / Press Enter to return"; then
                    ret_val=1
                fi
            else
                # Get current opacity value
                current_opacity=$(grep -oP '^background_opacity\s+\K[\d.]+' "$kitty_conf" 2>/dev/null || echo "未设置 / not set")
                echo ""
                echo ">>> 当前 Kitty 背景透明度 / Current Kitty background opacity: ${current_opacity}"
                echo "    (0.0 = 完全透明 / fully transparent, 1.0 = 完全不透明 / fully opaque)"
                echo ""
                echo ">>> 请选择新的透明度 / Select new opacity:"
                echo "    1) 0.6"
                echo "    2) 0.7"
                echo "    3) 0.8  (默认 / default)"
                echo "    4) 0.9"
                echo "    5) 1.0  (不透明 / opaque)"
                echo "    6) 自定义 / Custom value"
                echo ""
                read -rp "  输入选项 (1-6) / Enter option (1-6): " choice
                case "$choice" in
                    1) new_opacity="0.6" ;;
                    2) new_opacity="0.7" ;;
                    3) new_opacity="0.8" ;;
                    4) new_opacity="0.9" ;;
                    5) new_opacity="1.0" ;;
                    6)
                        read -rp "  输入透明度值 (0.0-1.0) / Enter opacity value (0.0-1.0): " new_opacity
                        # Validate: must be a number between 0 and 1
                        if ! [[ "$new_opacity" =~ ^[0-9]+(\.[0-9]+)?$ ]] || \
                           [[ "${new_opacity%.*}" -gt 1 ]] || \
                           { [[ "$new_opacity" == *.* ]] && [[ "${new_opacity#*.}" -gt 0 ]] && [[ "${new_opacity%.*}" -eq 1 ]]; }; then
                            echo -e "${YELLOW}    ⚠️  无效值，使用默认 0.8 / Invalid value, using default 0.8${RESET}"
                            new_opacity="0.8"
                        fi
                        ;;
                    *)
                        echo -e "${YELLOW}    ⚠️  无效选项，使用默认 0.8 / Invalid option, using default 0.8${RESET}"
                        new_opacity="0.8"
                        ;;
                esac
                echo ""
                echo ">>> 设置背景透明度为 ${new_opacity} / Setting background opacity to ${new_opacity}..."
                # Update kitty.conf — replace existing line or append if absent
                if grep -q '^background_opacity' "$kitty_conf"; then
                    sed -i "s/^background_opacity\s\+.*/background_opacity ${new_opacity}/" "$kitty_conf"
                else
                    echo "background_opacity ${new_opacity}" >> "$kitty_conf"
                fi
                echo -e "${GREEN}    ✅ 已更新 Kitty 背景透明度为 ${new_opacity}${RESET}"
                echo "    重启 Kitty 终端即可生效 / Restart Kitty terminal to apply"
                echo "[Step 10 completed]"
            fi
            ;;

        # ─────────────────────────────────────
        11) # 雾凇拼音 / Rime-ice Input Method
        # ─────────────────────────────────────
            step_header 11
            echo ">>> 安装雾凇拼音 / Installing Rime-ice input method..."
            yay -S --noconfirm rime-ice-pinyin-git
            echo "    rime-ice-pinyin-git 安装完成 / installed."
            echo ""
            echo ">>> 复制 Fcitx5 雾凇拼音配置 / Copying Fcitx5 Rime-ice config..."
            mkdir -p ~/.local/share/fcitx5/rime
            if [[ -f "$SCRIPT_DIR/fcitx5/default.custom.yaml" ]]; then
                cp "$SCRIPT_DIR/fcitx5/default.custom.yaml" ~/.local/share/fcitx5/rime/default.custom.yaml
                echo "    配置已复制到 ~/.local/share/fcitx5/rime/default.custom.yaml"
                echo "    Config copied successfully."
            else
                echo "    Warning: fcitx5/default.custom.yaml not found, skipping."
            fi
            echo ""
            echo "    请重新登录或重启 Fcitx5 以加载雾凇拼音"
            echo "    如果词库未生效，可尝试在 Fcitx5 中重新部署（右键托盘图标 → 重新部署）"
            echo "    Log out and back in, or restart Fcitx5 to load Rime-ice."
            echo "    If the schema does not appear, try re-deploying from Fcitx5 tray."
            echo "[Step 11 completed]"
            ;;

        # ─────────────────────────────────────
        12) # XDG 用户目录转英文 / Migrate XDG Dirs to English
        # ─────────────────────────────────────
            step_header 12

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
# This file is written by ArchInit (niri_append.sh)
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
            echo "[Step 12 completed]"
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
