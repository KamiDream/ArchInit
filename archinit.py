#!/usr/bin/env python3
# ArchInit — 统一 TUI 安装器（Python / curses 重构版）
#
# 由原 0_desktop_install.sh / 1_basic_initialization.sh / 2_mix_install.sh /
# lightdm.sh / patch.sh 融合而来，保留原分类结构：
#   1. 桌面安装   2. 基础初始化   3. 混合安装   4. LightDM 配置   5. 修补工具
#
# 运行：python3 archinit.py（需在 Arch Linux 上，带 sudo 权限）
# 交互：↑/↓ 选择，Enter 执行，q / Esc 返回上一级。

import curses
import locale
import os
import re
import shutil
import subprocess
import sys
import threading
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser("~")

# 减少按 ESC 时的卡顿：ncurses 默认会等 1000ms 判断是否为转义序列开头。
# 设为 25ms，按 ESC / 方向键都能立即响应。需在 curses 初始化前设置。
os.environ.setdefault("ESCDELAY", "25")

# ─────────────────────────────────────────────
# 日志（ASCII 徽标）
# ─────────────────────────────────────────────
LOGO = [
    "88      a8P                                   88  88888888ba,",
    "88    ,88'                                    \"\"  88      `\"8b",
    "88  ,88\"                                          88        `8b",
    "88,d88'       ,adPPYYba,  88,dPYba,,adPYba,   88  88         88  8b,dPPYba,   ,adPPYba,  ,adPPYYba,  88,dPYba,,adPYba,",
    "8888\"88,      \"\"     `Y8  88P'   \"88\"    \"8a  88  88         88  88P'   \"Y8  a8P_____88  \"\"     `Y8  88P'   \"88\"    \"8a",
    "88P   Y8b     ,adPPPPP88  88      88      88  88  88         8P  88          8PP\"\"\"\"\"\"\"  ,adPPPPP88  88      88      88",
    "88     \"88,   88,    ,88  88      88      88  88  88      .a8P   88          \"8b,   ,aa  88,    ,88  88      88      88",
    "88       Y8b  `\"8bbdP\"Y8  88      88      88  88  88888888Y\"'    88           `\"Ybbd8\"'  `\"8bbdP\"Y8  88      88      88",
]

# ─────────────────────────────────────────────
# ANSI 颜色（用于退出 curses 后执行步骤时的普通输出）
# ─────────────────────────────────────────────
def _c(text, code):
    return f"\033[{code}m{text}\033[0m"

def green_bold(t):  return _c(t, "1;32")
def red_bold(t):    return _c(t, "1;31")
def yellow(t):      return _c(t, "33")
def cyan(t):        return _c(t, "36")

# ─────────────────────────────────────────────
# Shell 辅助
# ─────────────────────────────────────────────
def run(cmd):
    """在当前终端（已退出 curses）执行 shell 命令，继承 stdin/stdout。"""
    return subprocess.run(cmd, shell=True, executable="/bin/bash", check=False).returncode

def ok(cmd):
    """执行命令并只返回是否成功（静默）。"""
    return subprocess.run(
        cmd, shell=True, executable="/bin/bash",
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False,
    ).returncode == 0

def capture(cmd):
    """执行命令并捕获 stdout。"""
    return subprocess.run(
        cmd, shell=True, executable="/bin/bash",
        capture_output=True, text=True, check=False,
    ).stdout

def which(name):
    return shutil.which(name) is not None

def installed(pkg):
    return ok(f"pacman -Q {pkg} >/dev/null 2>&1")

def prompt(msg="Press Enter to continue..."):
    """等待 Enter；输入 q 返回 False。"""
    try:
        ans = input(f"  [{msg}]  (or press q to return to menu) ")
    except EOFError:
        return True
    return ans.strip().lower() != "q"

def sudo_write(path, content, append=False):
    args = ["sudo", "tee"] + (["-a"] if append else []) + [path]
    subprocess.run(args, input=content, text=True, stdout=subprocess.DEVNULL, check=False)

def write_file(path, content, append=False):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a" if append else "w", encoding="utf-8") as f:
        f.write(content)

def read_file(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""

# ═════════════════════════════════════════════
# 步骤实现 —— 每个函数返回 True(成功) / False(失败)
# ═════════════════════════════════════════════

# ── 分类 1：桌面安装 ──────────────────────────
def dms_register():
    print(">>> Registering DMS as a user service dependency of Niri...")
    run("curl -fsSL https://install.danklinux.com | sh")
    return True

def dms_lightdm():
    print(">>> Installing LightDM and greeter...")
    run("sudo pacman -S --needed --noconfirm lightdm lightdm-gtk-greeter")
    print(">>> Enabling LightDM display manager...")
    run("sudo systemctl enable lightdm")
    print(">>> Starting LightDM...")
    run("sudo systemctl start lightdm")
    return True

# ── 分类 2：基础初始化 ────────────────────────
def basic_core():
    print(">>> Installing core desktop packages...")
    run("sudo pacman -S --needed --noconfirm kimageformats power-profiles-daemon cava")
    return True

def basic_extensions():
    print(">>> Installing base packages...")
    run("sudo pacman -S --needed --noconfirm fastfetch fcitx5-im fcitx5-rime fuse2 vim firefox "
        "pcmanfm-qt udisks2")
    print(">>> Setting pcmanfm-qt as default file manager...")
    run("xdg-mime default pcmanfm-qt.desktop inode/directory 2>/dev/null || true")
    print("    pcmanfm-qt set as default for inode/directory.")

    print()
    print(">>> Installing xarchiver (archive extraction tool) + 7zip backend...")
    run("sudo pacman -S --needed --noconfirm xarchiver 7zip")
    print("    (Double-clicking an archive in pcmanfm-qt does nothing without this.)")

    print()
    print(">>> NTFS 工具说明 / NTFS tools note...")
    print("    NTFS 修复与恢复工具集由 ntfsprogs-plus 提供（混合安装 / 基础初始化的 NTFS 步骤）。")
    print("    注意：ntfsprogs-plus 与 ntfs-3g 冲突，二者只装其一。")
    print("    Usage: sudo ntfsfix -d /dev/sdXN")

    print()
    print(">>> [Root Cause 2: missing auto-mount daemon]")
    print("    pcmanfm-qt's [Volume] MountRemovable=true relies on the LXQt session")
    print("    (lxqt-session + pcmanfm-qt desktop mode), which is inactive under niri.")
    print("    Installing udiskie as a lightweight auto-mounter...")
    run("sudo pacman -S --needed --noconfirm udiskie gvfs")
    print("    (gvfs provides the GIO virtual filesystem mounts — trash, network, MTP, etc.)")
    print("    Enabling udiskie as a systemd user service (WM-independent)...")
    os.makedirs(os.path.join(HOME, ".config/systemd/user"), exist_ok=True)
    write_file(os.path.join(HOME, ".config/systemd/user/udiskie.service"),
               "[Unit]\n"
               "Description=udiskie auto-mounter\n"
               "\n"
               "[Service]\n"
               "ExecStart=/usr/bin/udiskie\n"
               "Restart=on-failure\n"
               "\n"
               "[Install]\n"
               "WantedBy=default.target\n")
    run("systemctl --user daemon-reload")
    run("systemctl --user enable --now udiskie.service")
    run("systemctl --user status udiskie --no-pager || true")
    print("    udiskie auto-mount daemon enabled.")

    print()
    print(">>> Uncommenting zh_CN.UTF-8 in /etc/locale.gen...")
    run("sudo sed -i 's/^#zh_CN.UTF-8/zh_CN.UTF-8/' /etc/locale.gen")
    print("    zh_CN.UTF-8 enabled.")

    print(">>> Generating locale...")
    run("sudo locale-gen")
    print(">>> Setting system locale to zh_CN.UTF-8...")
    run("sudo localectl set-locale LANG=zh_CN.UTF-8")

    print(">>> Installing Chinese fonts & Nerd fonts...")
    run("sudo pacman -S --needed --noconfirm wqy-microhei wqy-microhei-lite wqy-bitmapfont "
        "wqy-zenhei ttf-arphic-ukai ttf-arphic-uming noto-fonts-cjk ttf-jetbrains-mono-nerd "
        "noto-fonts-emoji ttf-fira-code inter-font")

    print()
    print(">>> Configuring XDG user directories with English names...")
    run("sudo pacman -S --needed --noconfirm xdg-user-dirs")
    os.makedirs(os.path.join(HOME, ".config"), exist_ok=True)
    write_file(os.path.join(HOME, ".config/user-dirs.dirs"),
               "# This file is written by ArchInit (archinit.py)\n"
               "# XDG user directories with English names\n"
               "# System locale remains Chinese (zh_CN.UTF-8)\n"
               "#\n"
               'XDG_DESKTOP_DIR="$HOME/Desktop"\n'
               'XDG_DOWNLOAD_DIR="$HOME/Downloads"\n'
               'XDG_TEMPLATES_DIR="$HOME/Templates"\n'
               'XDG_PUBLICSHARE_DIR="$HOME/Public"\n'
               'XDG_DOCUMENTS_DIR="$HOME/Documents"\n'
               'XDG_MUSIC_DIR="$HOME/Music"\n'
               'XDG_PICTURES_DIR="$HOME/Pictures"\n'
               'XDG_VIDEOS_DIR="$HOME/Videos"\n'
               'XDG_PROJECTS_DIR="$HOME/Projects"\n')
    for d in ["Desktop", "Downloads", "Templates", "Public", "Documents",
              "Music", "Pictures", "Videos", "Projects"]:
        os.makedirs(os.path.join(HOME, d), exist_ok=True)
    run("xdg-user-dirs-update 2>/dev/null || true")
    print("    XDG user directories configured with English names.")
    print("    (Desktop, Downloads, Documents, Pictures, Music, Videos, Public, Templates, Projects)")
    return True

def basic_kitty_font():
    print(">>> Running Kitty font selector, choose JetBrains Mono...")
    if prompt("Press Enter to launch font selector"):
        run("kitten choose-fonts")
        run("stty sane 2>/dev/null || true")
        prompt("Font selected. Press Enter to continue")
        return True
    return False

def basic_aur():
    print(">>> Configuring /etc/pacman.conf...")
    run("sudo sed -i '/^#\\[multilib\\]/,/^#Include/ s/^#//' /etc/pacman.conf")
    print("    [multilib] enabled.")
    if not ok("grep -q '^\\[archlinuxcn\\]' /etc/pacman.conf"):
        sudo_write("/etc/pacman.conf",
                   "\n[archlinuxcn]\n"
                   "Server = https://mirrors.ustc.edu.cn/archlinuxcn/$arch\n"
                   "Server = https://mirrors.tuna.tsinghua.edu.cn/archlinuxcn/$arch\n"
                   "Server = https://mirrors.hit.edu.cn/archlinuxcn/$arch\n"
                   "Server = https://repo.huaweicloud.com/archlinuxcn/$arch\n",
                   append=True)
        print("    [archlinuxcn] repository added.")
    else:
        print("    [archlinuxcn] already present, skipping.")
    print(">>> Installing archlinuxcn-keyring and updating system...")
    run("sudo pacman -Sy --needed --noconfirm archlinuxcn-keyring")
    run("sudo pacman -S --needed --noconfirm base-devel yay paru flclash")
    run("sudo pacman -Syu --noconfirm")
    return True

def basic_ntfs():
    print(">>> 安装 ntfsprogs-plus（增强版 NTFS 修复/恢复工具）...")
    if which("yay"):
        run("yay -S --noconfirm ntfsprogs-plus")
    elif which("paru"):
        run("paru -S --noconfirm ntfsprogs-plus")
    else:
        print(yellow("    ⚠️ 未检测到 AUR 助手（yay/paru）。请先执行「AUR 助手」步骤。"))
        return False
    print("    ntfsprogs-plus 提供 ntfsfix 增强、ntfsundelete、ntfsdump 等工具。")
    return True

def basic_rime():
    print(">>> 安装雾凇拼音 / Installing Rime-ice input method...")
    run("yay -S --noconfirm rime-ice-pinyin-git")
    print("    rime-ice-pinyin-git 安装完成 / installed.")
    print()
    print(">>> 复制 Fcitx5 雾凇拼音配置 / Copying Fcitx5 Rime-ice config...")
    os.makedirs(os.path.join(HOME, ".local/share/fcitx5/rime"), exist_ok=True)
    src = os.path.join(SCRIPT_DIR, "fcitx5/default.custom.yaml")
    dst = os.path.join(HOME, ".local/share/fcitx5/rime/default.custom.yaml")
    if os.path.isfile(src):
        shutil.copyfile(src, dst)
        print("    配置已复制到 ~/.local/share/fcitx5/rime/default.custom.yaml")
        print("    Config copied successfully.")
    else:
        print("    Warning: fcitx5/default.custom.yaml not found, skipping.")
    print()
    print("    请重新登录或重启 Fcitx5 以加载雾凇拼音")
    print("    如果词库未生效，可尝试在 Fcitx5 中重新部署（右键托盘图标 → 重新部署）")
    print("    Log out and back in, or restart Fcitx5 to load Rime-ice.")
    print("    If the schema does not appear, try re-deploying from Fcitx5 tray.")
    return True

def basic_keyring():
    print(">>> 安装密钥库 / Installing keyring packages...")
    run("sudo pacman -S --needed --noconfirm gnome-keyring libsecret seahorse")
    print("    gnome-keyring libsecret seahorse 安装完成 / installed.")
    print()
    print(">>> 查看 gnome-keyring-daemon 服务状态 / Checking gnome-keyring-daemon service status...")
    run("systemctl --user status gnome-keyring-daemon.service --no-pager || true")
    print()
    print("    提示：如服务未运行，重新登录后 systemd 用户会话会自动启动 gnome-keyring-daemon")
    print("    Tip: if the service is not running, re-login so the systemd user session starts it automatically.")
    return True

# ── 分类 3：混合安装 ──────────────────────────
def mix_kvm():
    print(">>> Installing KVM packages...")
    run("sudo pacman -S --needed --noconfirm qemu-full virt-manager swtpm dnsmasq")
    print(">>> Enabling and starting libvirtd service...")
    run("sudo systemctl enable --now libvirtd")
    print(">>> Starting default virtual network...")
    run("sudo virsh net-start default 2>/dev/null || true")
    run("sudo virsh net-autostart default")
    print(">>> Adding current user to libvirt group...")
    run('sudo usermod -a -G libvirt "$(whoami)"')
    print("    Note: re-login is required for group changes to take effect.")
    return True

def mix_nvidia():
    print(">>> Installing kernel headers (detecting installed kernels)...")
    headers = []
    if installed("linux"):
        headers.append("linux-headers")
        print("    linux kernel detected -> linux-headers")
    if installed("linux-zen"):
        headers.append("linux-zen-headers")
        print("    linux-zen kernel detected -> linux-zen-headers")
    if not headers:
        print(yellow("    ⚠️  No supported kernel found (linux/linux-zen). "
                     "This step requires at least one kernel installed. Aborting."))
        return False
    run("sudo pacman -S --needed --noconfirm " + " ".join(headers))
    print(">>> Installing NVIDIA drivers...")
    run("sudo pacman -S --needed --noconfirm nvidia-dkms nvidia-utils nvidia-settings")
    print()
    print(">>> Adding nvidia modules to /etc/mkinitcpio.conf...")
    run("sudo sed -i 's/^MODULES=()/MODULES=(nvidia nvidia_modeset nvidia_uvm nvidia_drm)/' /etc/mkinitcpio.conf")
    run("sudo sed -i 's/^#MODULES=()/MODULES=(nvidia nvidia_modeset nvidia_uvm nvidia_drm)/' /etc/mkinitcpio.conf")
    print("    MODULES=(nvidia nvidia_modeset nvidia_uvm nvidia_drm) set.")
    hooks = capture("grep '^HOOKS=' /etc/mkinitcpio.conf")
    if hooks and "kms" in hooks:
        print("    Found kms in HOOKS, removing it (conflicts with NVIDIA proprietary driver)...")
        run("sudo sed -i '/^HOOKS=/ s/ *kms *//' /etc/mkinitcpio.conf")
        print("    kms removed from HOOKS.")
    else:
        print("    kms not found in HOOKS, no change needed.")
    print(">>> Regenerating initramfs...")
    run("sudo mkinitcpio -P")
    return True

def mix_intel():
    print(">>> Installing Intel integrated graphics drivers...")
    run("sudo pacman -S --needed --noconfirm mesa vulkan-intel intel-media-driver mesa-utils")
    print("    (mesa: OpenGL/Vulkan 驱动基础; vulkan-intel: Intel Vulkan 驱动;")
    print("     intel-media-driver: 硬件视频编解码; mesa-utils: glxinfo 等诊断工具)")
    print("    --needed 已启用：已安装的包会自动跳过 / --needed skips already-installed packages.")
    return True

def mix_amd():
    print(">>> Installing AMD integrated graphics drivers...")
    run("sudo pacman -S --needed --noconfirm mesa vulkan-radeon libva-mesa-driver mesa-utils")
    print("    (mesa: OpenGL/Vulkan 驱动基础; vulkan-radeon: AMD Vulkan 驱动(RADV);")
    print("     libva-mesa-driver: VA-API 硬件视频解码; mesa-utils: glxinfo 等诊断工具)")
    print("    --needed 已启用：已安装的包会自动跳过 / --needed skips already-installed packages.")
    return True

def mix_zsh():
    print(">>> Installing Zsh...")
    run("sudo pacman -S --needed --noconfirm zsh zsh-completions")
    print(">>> Listing available shells...")
    run("chsh -l")
    print(">>> Changing default shell to Zsh (password required)...")
    run("chsh -s /usr/bin/zsh || true")
    print()
    print(">>> Configuring Kitty terminal...")
    os.makedirs(os.path.join(HOME, ".config/kitty"), exist_ok=True)
    kitty_conf = os.path.join(HOME, ".config/kitty/kitty.conf")
    if "cursor_trail" not in read_file(kitty_conf):
        write_file(kitty_conf,
                   "\ncursor_trail 2\n"
                   "cursor_blink_interval 0.5\n"
                   "cursor_stop_blinking_after 0\n",
                   append=True)
        print("    Kitty cursor settings added.")
    else:
        print("    Kitty cursor settings already present, skipping.")
    return True

ANTIDOTE_BLOCK = """
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
# ("menu select" 是让用户能用方向键导航的关键配置）
zstyle ':completion:*' menu select

# 补全列表颜色
zstyle ':completion:*' list-colors ''
zstyle ':completion:*' list-prompt '%S%l 个匹配项 %s'

# 智能大小写匹配(例:README 输入 readme 也能匹配）
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
"""

def mix_antidote():
    if not which("zsh"):
        print("Warning: Zsh does not appear to be installed.")
        return prompt("Press Enter to skip")
    print(">>> Cleaning up any previous Antidote configuration...")
    shutil.rmtree(os.path.join(HOME, ".antidote"), ignore_errors=True)
    zshrc = os.path.join(HOME, ".zshrc")
    txt = read_file(zshrc)
    txt = re.sub(r"^# === Antidote Start ===$.*?^# === Antidote End ===$\n?",
                 "", txt, flags=re.DOTALL | re.MULTILINE)
    write_file(zshrc, txt)
    print("    Cleanup done.")
    print(">>> Installing Antidote plugin manager...")
    run('git clone --depth=1 https://github.com/mattmc3/antidote.git ~/.antidote')
    print()
    print(">>> Creating ~/.zsh_plugins.txt with recommended plugins...")
    write_file(os.path.join(HOME, ".zsh_plugins.txt"),
               "zsh-users/zsh-completions\n"
               "zsh-users/zsh-autosuggestions\n"
               "zdharma-continuum/fast-syntax-highlighting\n")
    print("    Plugins configured.")
    print()
    print(">>> Appending Antidote configuration to ~/.zshrc...")
    write_file(zshrc, ANTIDOTE_BLOCK, append=True)
    print("    Antidote configuration written to ~/.zshrc.")
    return True

def mix_starship():
    if not which("zsh"):
        print("Warning: Zsh does not appear to be installed.")
        return prompt("Press Enter to skip")
    print(">>> Installing Starship prompt...")
    run("sudo pacman -S --needed --noconfirm starship")
    print()
    print(">>> Copying Starship config to ~/.config/starship.toml...")
    os.makedirs(os.path.join(HOME, ".config"), exist_ok=True)
    src = os.path.join(SCRIPT_DIR, "starship/starship.toml")
    if os.path.isfile(src):
        shutil.copyfile(src, os.path.join(HOME, ".config/starship.toml"))
        print("    Starship config copied successfully.")
        print("    Prompt: 󰄛 ❯  (Catppuccin Macchiato palette)")
        print("    Character: [󰄛](green) ❯  on success, [󰄛](red) ❯  on error")
    else:
        print("    Warning: starship/starship.toml not found, skipping.")
    print()
    print(">>> Adding Starship init to ~/.zshrc...")
    zshrc = os.path.join(HOME, ".zshrc")
    txt = read_file(zshrc)
    txt = re.sub(r'^eval "\$\(starship init zsh\)"\n?', "", txt, flags=re.MULTILINE)
    write_file(zshrc, txt)
    write_file(zshrc, '\n# Starship 提示符\neval "$(starship init zsh)"\n', append=True)
    print("    Starship init written to ~/.zshrc.")
    return True

def mix_fastfetch_config():
    print(">>> Copying fastfetch config to ~/.config/fastfetch...")
    dst = os.path.join(HOME, ".config/fastfetch")
    os.makedirs(dst, exist_ok=True)
    src = os.path.join(SCRIPT_DIR, "fastfetch")
    if os.path.isdir(src):
        shutil.copytree(src, dst, dirs_exist_ok=True)
    print("    fastfetch config copied successfully.")
    return True

def mix_fastfetch_startup():
    zshrc = os.path.join(HOME, ".zshrc")
    first = ""
    if os.path.isfile(zshrc):
        with open(zshrc, encoding="utf-8") as f:
            first = f.readline().rstrip("\n")
    if re.fullmatch(r"\s?fastfetch", first):
        print(">>> fastfetch 已存在于 ~/.zshrc 第一行，正在移除（关闭自启）...")
        lines = read_file(zshrc).splitlines(keepends=True)
        if lines:
            lines = lines[1:]
        write_file(zshrc, "".join(lines))
        print("    fastfetch 已从 .zshrc 第一行移除。")
        print("    ✅ 已关闭 fastfetch 开机自启。")
    else:
        print(">>> fastfetch 不在 ~/.zshrc 第一行，正在添加（开启自启）...")
        if not os.path.isfile(zshrc):
            open(zshrc, "a").close()
        txt = read_file(zshrc)
        write_file(zshrc, " fastfetch\n" + txt)
        print("    fastfetch 已添加为 .zshrc 第一行（带前导空格，不记入历史）。")
        print("    ✅ 已开启 fastfetch 开机自启。")
    return True

def mix_kitty_opacity():
    kitty_conf = os.path.join(HOME, ".config/kitty/kitty.conf")
    if not os.path.isfile(kitty_conf):
        print(yellow(f"  ⚠️  Kitty 配置文件不存在 / Kitty config not found at {kitty_conf}"))
        print("    请先执行「启用 Zsh 终端」（含 Kitty 终端配置）/ Please run the Zsh step first.")
        return prompt("按 Enter 返回菜单 / Press Enter to return")
    conf = read_file(kitty_conf)
    m = re.search(r"^background_opacity\s+([\d.]+)", conf, re.MULTILINE)
    current = m.group(1) if m else "未设置 / not set"
    print()
    print(f">>> 当前 Kitty 背景透明度 / Current Kitty background opacity: {current}")
    print("    (0.0 = 完全透明 / fully transparent, 1.0 = 完全不透明 / fully opaque)")
    print()
    print(">>> 请选择新的透明度 / Select new opacity:")
    print("    1) 0.6")
    print("    2) 0.7")
    print("    3) 0.8  (默认 / default)")
    print("    4) 0.9")
    print("    5) 1.0  (不透明 / opaque)")
    print("    6) 自定义 / Custom value")
    print()
    try:
        choice = input("  输入选项 (1-6) / Enter option (1-6): ").strip()
    except EOFError:
        choice = ""
    presets = {"1": "0.6", "2": "0.7", "3": "0.8", "4": "0.9", "5": "1.0"}
    if choice in presets:
        new_opacity = presets[choice]
    elif choice == "6":
        try:
            new_opacity = input("  输入透明度值 (0.0-1.0) / Enter opacity value (0.0-1.0): ").strip()
        except EOFError:
            new_opacity = ""
        if not re.fullmatch(r"[0-9]+(\.[0-9]+)?", new_opacity or "") or float(new_opacity) > 1.0:
            print(yellow("    ⚠️  无效值，使用默认 0.8 / Invalid value, using default 0.8"))
            new_opacity = "0.8"
    else:
        print(yellow("    ⚠️  无效选项，使用默认 0.8 / Invalid option, using default 0.8"))
        new_opacity = "0.8"
    print()
    print(f">>> 设置背景透明度为 {new_opacity} / Setting background opacity to {new_opacity}...")
    if re.search(r"^background_opacity", conf, re.MULTILINE):
        conf = re.sub(r"^background_opacity\s+.*", f"background_opacity {new_opacity}", conf, flags=re.MULTILINE)
        write_file(kitty_conf, conf)
    else:
        write_file(kitty_conf, f"background_opacity {new_opacity}\n", append=True)
    print(green_bold(f"    ✅ 已更新 Kitty 背景透明度为 {new_opacity}"))
    print("    重启 Kitty 终端即可生效 / Restart Kitty terminal to apply")
    return True

# ── 分类 4：LightDM 配置 ──────────────────────
def ldm_greeter():
    print(">>> 安装 lightdm-webkit2-greeter...")
    print("    Installing lightdm-webkit2-greeter...")
    run("sudo pacman -S --needed --noconfirm lightdm-webkit2-greeter")
    print()
    print(green_bold("    ✅ lightdm-webkit2-greeter 安装完成 / installed successfully."))
    return True

def ldm_theme():
    print(">>> 清理旧主题（如果存在）...")
    print("    Cleaning up old theme (if exists)...")
    target = "/usr/share/lightdm-webkit/themes/KamiDream_Theme"
    if os.path.isdir(target):
        run(f"sudo rm -rf {target}")
        print("    ✅ 旧主题已删除 / Old theme removed.")
    else:
        print("    ⏭️  未发现旧主题，跳过 / No old theme found, skipping.")
    print()
    print(">>> 克隆 KamiDream LightDM WebKit2 主题...")
    print("    Cloning KamiDream LightDM WebKit2 theme...")
    theme_dir = os.path.join(HOME, "LdmWk2Theme")
    if os.path.isdir(theme_dir):
        shutil.rmtree(theme_dir, ignore_errors=True)
    run(f'git clone https://github.com/KamiDream/LdmWk2Theme.git "{theme_dir}"')
    print()
    print(">>> 创建目标目录并移动主题...")
    print("    Creating target directory and moving theme...")
    run("sudo mkdir -p /usr/share/lightdm-webkit/themes/")
    run(f'sudo mv "{theme_dir}" {target}')
    print()
    print(green_bold(f"    ✅ KamiDream 主题已安装/更新到 {target}"))
    print("    Theme installed/updated successfully.")
    print()
    print("    🖼️  如需替换背景图片，请替换以下文件：")
    print("       /usr/share/lightdm-webkit/themes/KamiDream_Theme/assets/background.png")
    print("       To replace the background image, replace the file above with your own.")
    return True

def ldm_enable():
    print(">>> 配置 /etc/lightdm/lightdm.conf...")
    print("    Configuring /etc/lightdm/lightdm.conf...")
    run("sudo mkdir -p /etc/lightdm")
    conf = "/etc/lightdm/lightdm.conf"
    if read_file(conf).find("[Seat:*]") >= 0 or ok(f"grep -q '^\\[Seat:\\*\\]' {conf} 2>/dev/null"):
        if ok(f"grep -q '^greeter-session=' {conf}"):
            run(f"sudo sed -i 's/^greeter-session=.*/greeter-session=lightdm-webkit2-greeter/' {conf}")
        else:
            run(f"sudo sed -i '/^\\[Seat:\\*\\]/a greeter-session=lightdm-webkit2-greeter' {conf}")
    else:
        sudo_write(conf, "[Seat:*]\ngreeter-session=lightdm-webkit2-greeter\n", append=True)
    print("    /etc/lightdm/lightdm.conf 已配置 / configured.")
    print()
    print(">>> 配置 /etc/lightdm/lightdm-webkit2-greeter.conf...")
    print("    Configuring /etc/lightdm/lightdm-webkit2-greeter.conf...")
    wconf = "/etc/lightdm/lightdm-webkit2-greeter.conf"
    if ok(f"grep -q '^webkit_theme' {wconf} 2>/dev/null"):
        run(f"sudo sed -i 's/^webkit_theme\\s*=.*/webkit_theme        = KamiDream_Theme/' {wconf}")
        print("    webkit_theme 已更新为 KamiDream_Theme / updated.")
    else:
        sudo_write(wconf, "[greeter]\nwebkit_theme        = KamiDream_Theme\n", append=True)
        print("    webkit_theme 已添加 / added.")
    print("    /etc/lightdm/lightdm-webkit2-greeter.conf 已配置 / configured.")
    print()
    print(green_bold("    ✅ LightDM 配置完成 / Configuration complete."))
    print()
    print("=" * 121)
    print(yellow("   ⚠️  请重启系统以应用 LightDM 登录管理器 / Please reboot to apply LightDM"))
    print("     重启命令 / Reboot command: sudo reboot")
    print("     或 / Or: sudo systemctl reboot")
    print("=" * 121)
    print()
    return prompt("按 Enter 继续 / Press Enter to continue")

def ldm_emergency():
    print(">>> 注释 /etc/lightdm/lightdm.conf 中的 greeter-session=lightdm-webkit2-greeter...")
    print("    Commenting out greeter-session=lightdm-webkit2-greeter in /etc/lightdm/lightdm.conf...")
    conf = "/etc/lightdm/lightdm.conf"
    if ok(f"grep -q '^greeter-session=lightdm-webkit2-greeter' {conf} 2>/dev/null"):
        run(f"sudo sed -i 's/^greeter-session=lightdm-webkit2-greeter/#greeter-session=lightdm-webkit2-greeter/' {conf}")
        print(green_bold("    ✅ 已注释 greeter-session 行 / Commented out."))
    else:
        print(yellow("    ⏭️  未找到 greeter-session=lightdm-webkit2-greeter，可能已被注释 / Not found, may already be commented."))
    print()
    print("=" * 121)
    print(yellow("   ⚠️  请重启系统以恢复默认 LightDM Greeter / Please reboot to restore default LightDM greeter"))
    print("     重启命令 / Reboot command: sudo reboot")
    print("     或 / Or: sudo systemctl reboot")
    print("=" * 121)
    print()
    return prompt("按 Enter 继续 / Press Enter to continue")

# ── 分类 5：修补工具 ──────────────────────────
def patch_uu():
    print(">>> Installing UU Accelerator...")
    print("    This will:")
    print("      • Create /home/deck directory")
    print("      • Set ownership to current user")
    print("      • Download and run UU install script from uudeck.com")
    print()
    if prompt("Press Enter to start installation"):
        print(">>> Creating /home/deck...")
        run("sudo mkdir /home/deck")
        run('sudo chown "$(whoami)" /home/deck')
        print(">>> Downloading and running UU install script...")
        run("curl -s uudeck.com | sudo bash")
        print()
        return True
    return False

def _parse_xdg_dirs(path):
    d = {}
    for line in read_file(path).splitlines():
        line = line.strip()
        if line.startswith("XDG_") and "=" in line:
            k, v = line.split("=", 1)
            v = v.strip().strip('"').replace("$HOME", HOME)
            d[k.strip()] = v
    return d

def patch_xdg():
    print(">>> 安装 xdg-user-dirs（如未安装）/ Installing xdg-user-dirs (if not present)...")
    run("sudo pacman -S --needed --noconfirm xdg-user-dirs")

    conf = os.path.join(HOME, ".config/user-dirs.dirs")
    bak = conf + ".bak." + str(int(time.time()))
    old = {}
    if os.path.isfile(conf):
        shutil.copyfile(conf, bak)
        print(f"    原配置已备份到 / Old config backed up to: {bak}")
        old = _parse_xdg_dirs(bak)
    else:
        print("    未发现现有配置，将创建全新配置 / No existing config found, creating fresh config.")

    print()
    print(">>> 直接写入英文路径配置文件...")
    print("    Writing config file with English paths directly...")
    write_file(conf,
               "# This file is written by ArchInit (archinit.py)\n"
               "# XDG user directories with English names\n"
               "# System locale remains Chinese (zh_CN.UTF-8)\n"
               "#\n"
               'XDG_DESKTOP_DIR="$HOME/Desktop"\n'
               'XDG_DOWNLOAD_DIR="$HOME/Downloads"\n'
               'XDG_TEMPLATES_DIR="$HOME/Templates"\n'
               'XDG_PUBLICSHARE_DIR="$HOME/Public"\n'
               'XDG_DOCUMENTS_DIR="$HOME/Documents"\n'
               'XDG_MUSIC_DIR="$HOME/Music"\n'
               'XDG_PICTURES_DIR="$HOME/Pictures"\n'
               'XDG_VIDEOS_DIR="$HOME/Videos"\n'
               'XDG_PROJECTS_DIR="$HOME/Projects"\n')
    print(f"    ✅ 配置文件已写入 / Config written: {conf}")

    print()
    print(">>> 迁移目录内容...")
    print("    Migrating directory contents...")
    mapping = [
        ("XDG_DESKTOP_DIR", "Desktop"),
        ("XDG_DOWNLOAD_DIR", "Downloads"),
        ("XDG_TEMPLATES_DIR", "Templates"),
        ("XDG_PUBLICSHARE_DIR", "Public"),
        ("XDG_DOCUMENTS_DIR", "Documents"),
        ("XDG_MUSIC_DIR", "Music"),
        ("XDG_PICTURES_DIR", "Pictures"),
        ("XDG_VIDEOS_DIR", "Videos"),
        ("XDG_PROJECTS_DIR", "Projects"),
    ]
    migrated = 0
    for key, en_name in mapping:
        en_path = os.path.join(HOME, en_name)
        old_path = old.get(key, "")
        if not old_path or old_path == en_path:
            continue
        if not os.path.isdir(old_path):
            continue
        print()
        print(f"  发现旧目录 / Found old dir: {old_path}")
        print(f"  目标目录 / Target dir: {en_path}")
        os.makedirs(en_path, exist_ok=True)
        entries = []
        try:
            entries = os.listdir(old_path)
        except OSError:
            entries = []
        if entries:
            print("    迁移内容中 / Migrating contents...")
            for name in entries:
                try:
                    shutil.move(os.path.join(old_path, name), os.path.join(en_path, name))
                except OSError as e:
                    print(yellow(f"    ⚠️  移动失败 / Failed to move {name}: {e}"))
            print("    ✅ 内容已迁移 / Contents migrated.")
        else:
            print("    目录为空，无需迁移 / Directory empty, no migration needed.")
        try:
            os.rmdir(old_path)
            print(f"    ✅ 旧目录已删除 / Old directory removed: {old_path}")
        except OSError:
            print(f"    ⚠️  旧目录未能删除（可能仍有内容）/ Old dir not removed: {old_path}")
        migrated += 1

    if migrated == 0:
        print("    无需迁移，目录名未改变 / No migration needed — directory names unchanged.")
    else:
        print()
        print(f"    ✅ 共迁移 {migrated} 个目录 / Total {migrated} directories migrated.")

    print()
    print(">>> 同步 xdg-user-dirs（保留已有配置）...")
    print("    Syncing xdg-user-dirs (preserving existing config)...")
    run("xdg-user-dirs-update 2>/dev/null || true")
    print("    ✅ 同步完成 / Sync done.")
    print()
    print("    ✅ XDG 用户目录已切换为英文名 / XDG user dirs migrated to English names.")
    print("    系统 locale 仍为中文（zh_CN.UTF-8），不受影响。")
    print("    System locale remains Chinese (zh_CN.UTF-8); unaffected.")
    print()
    print("    请重新登录后检查效果。备份文件可手动删除：")
    print("    Re-login to verify. Backup can be removed manually:")
    print(f'      rm "{bak}"')
    return True

def patch_fcitx():
    conf_dir = os.path.join(HOME, ".config/environment.d")
    conf = os.path.join(conf_dir, "fcitx.conf")
    print(">>> 写入 Fcitx5 输入法环境变量...")
    print("    Writing Fcitx5 input method environment variables...")
    print(f"    目标文件 / Target file: {conf}")
    print()
    if os.path.isfile(conf):
        shutil.copyfile(conf, conf + ".bak." + str(int(time.time())))
        print(f"    原配置已备份 / Old config backed up: {conf}.bak.*")
    os.makedirs(conf_dir, exist_ok=True)
    write_file(conf,
               "# Fcitx5 input method environment variables\n"
               "XMODIFIERS=@im=fcitx5\n"
               "#GTK_IM_MODULE=fcitx5\n"
               "QT_IM_MODULE=fcitx5\n"
               "SDL_IM_MODULE=fcitx5\n")
    print(f"    ✅ 配置文件已写入 / Config written: {conf}")
    print()
    print("    ✅ Fcitx5 环境变量已配置 / Fcitx5 environment variables configured.")
    print("    重新登录后生效（environment.d 由 systemd 用户会话加载）。")
    print("    Re-login to take effect (environment.d is loaded by systemd user session).")
    return True

# ═════════════════════════════════════════════
# 数据模型
# ═════════════════════════════════════════════
class Step:
    def __init__(self, title, func):
        self.title = title
        self.func = func

class Category:
    def __init__(self, title, steps, warning=None, dividers=None):
        self.title = title
        self.steps = steps
        self.warning = warning or []
        self.dividers = dividers or set()
        self.completed = [False] * len(steps)
        self.selected = 0   # 记住本分类上次高亮的步骤位置

def build_categories():
    return [
        Category("桌面安装 / Desktop Install", [
            Step("注册 DMS 服务 / Register DMS Service", dms_register),
            Step("显示管理器 LightDM / Display Manager", dms_lightdm),
        ]),
        Category("基础初始化 / Basic Initialization", [
            Step("niri 核心组件 / Niri Core Components", basic_core),
            Step("系统拓展组件 / System Extensions", basic_extensions),
            Step("Kitty 字体选择 / Kitty Font Selector", basic_kitty_font),
            Step("AUR 助手 / AUR Helper (yay / paru)", basic_aur),
            Step("NTFS 增强工具 / NTFS Enhanced Tools", basic_ntfs),
            Step("雾凇拼音 / Rime-ice Input Method", basic_rime),
            Step("安装密钥库 / Install Keyring", basic_keyring),
        ]),
        Category("KVM 安装 / KVM Install", [
            Step("KVM 虚拟化 / KVM Virtualization", mix_kvm),
        ]),
        Category("显卡驱动安装 / GPU Drivers", [
            Step("NVIDIA 显卡驱动 / NVIDIA Graphics Driver", mix_nvidia),
            Step("Intel 核显驱动 / Intel Integrated Graphics", mix_intel),
            Step("AMD 核显驱动 / AMD Integrated Graphics", mix_amd),
        ]),
        Category("终端美化 / Terminal Beautification", [
            Step("启用 Zsh 终端 / Enable Zsh Shell", mix_zsh),
            Step("Antidote 插件管理器 / Antidote Plugin Manager", mix_antidote),
            Step("Starship 提示符 / Starship Prompt", mix_starship),
            Step("fastfetch 配置 / fastfetch Configuration", mix_fastfetch_config),
            Step("配置 fastfetch 启动 / Configure fastfetch on startup", mix_fastfetch_startup),
            Step("Kitty 背景透明度 / Kitty Background Opacity", mix_kitty_opacity),
        ]),
        Category("LightDM 配置 / LightDM WebKit2 Greeter", [
            Step("安装 LightDM WebKit2 Greeter / Install Greeter", ldm_greeter),
            Step("安装 KamiDream 主题 / Install KamiDream Theme", ldm_theme),
            Step("启用 LightDM 配置 / Enable LightDM Configuration", ldm_enable),
            Step("黑屏救急 / Black Screen Emergency Fix", ldm_emergency),
        ], warning=[
            "⚠️  警告 / WARNING",
            "单 N 卡独显或开启了独显直连的用户（纯 N 卡用户）请勿使用此配置！",
            "Do NOT use this configuration if you have a single/primary NVIDIA GPU!",
        ]),
        Category("修补工具 / Patch Tools", [
            Step("UU 加速器安装 / UU Accelerator Install", patch_uu),
            Step("XDG 用户目录转英文 / Migrate XDG Dirs to English", patch_xdg),
            Step("Fcitx5 输入法环境变量 / Fcitx5 IM Environment Variables", patch_fcitx),
        ]),
    ]

# ═════════════════════════════════════════════
# curses 界面
# ═════════════════════════════════════════════
BAR = "=" * 121

class UI:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.categories = build_categories()
        self.color = curses.has_colors()
        self.main_sel = 0   # 记住主菜单上次高亮的分类位置

    # ── 颜色 ──
    def init_colors(self):
        if not self.color:
            return
        curses.start_color()
        try:
            curses.use_default_colors()
            bg = -1
        except curses.error:
            bg = curses.COLOR_BLACK
        curses.init_pair(1, curses.COLOR_CYAN, bg)     # logo 左
        curses.init_pair(2, curses.COLOR_MAGENTA, bg)  # logo 右
        curses.init_pair(3, curses.COLOR_YELLOW, bg)   # 警告
        curses.init_pair(4, curses.COLOR_GREEN, bg)    # 完成
        curses.init_pair(5, curses.COLOR_RED, bg)      # 错误

    def attr(self, pair, extra=0):
        if not self.color:
            return extra
        return curses.color_pair(pair) | extra

    # ── 安全写字符 ──
    def put(self, y, x, text, attr=0):
        h, w = self.stdscr.getmaxyx()
        if y < 0 or y >= h or x >= w - 1:
            return
        maxlen = w - 1 - x
        try:
            self.stdscr.addnstr(y, x, text, maxlen, attr)
        except curses.error:
            pass

    def draw_logo(self, y):
        for line in LOGO:
            self.put(y, 0, line[:48], self.attr(1))
            self.put(y, 48, line[48:], self.attr(2))
            y += 1
        return y

    # ── 通用菜单；返回 (最终高亮下标, 选择下标)；q/Esc 选择为 -1 ──
    def menu(self, items, title, warning=None, completed=None, dividers=None, sel=0):
        dividers = dividers or set()
        if items:
            sel = max(0, min(sel, len(items) - 1))
        while True:
            self.stdscr.erase()
            y = self.draw_logo(0)
            y += 1
            self.put(y, 0, BAR); y += 1
            self.put(y, 21, f"ArchInit — {title}"); y += 1
            self.put(y, 0, BAR); y += 1
            if warning:
                y += 1
                for line in warning:
                    self.put(y, 0, "  " + line, self.attr(3, curses.A_BOLD))
                    y += 1
            y += 1
            for i, name in enumerate(items):
                if i in dividers:
                    self.put(y, 2, "─" * 100); y += 1
                mark = " "
                if completed and completed[i]:
                    mark = "✓"
                prefix = ">" if i == sel else " "
                label = f" {prefix} {mark} Step {i+1}: {name}"
                if i == sel:
                    self.put(y, 0, label, self.attr(1, curses.A_BOLD))
                else:
                    self.put(y, 0, label)
                y += 1
            h, _ = self.stdscr.getmaxyx()
            fy = min(h - 2, y + 1)
            self.put(fy, 0, "═" * 121)
            self.put(fy + 1, 21, "↑/↓ 导航 • Enter 执行 • q/Esc 返回")
            self.stdscr.refresh()

            key = self.stdscr.getch()
            if key in (curses.KEY_UP, ord("k")):
                sel = (sel - 1) % len(items)
            elif key in (curses.KEY_DOWN, ord("j")):
                sel = (sel + 1) % len(items)
            elif key in (10, 13, curses.KEY_ENTER):
                return sel, sel
            elif key in (ord("q"), ord("Q"), 27):
                return sel, -1

    # ── 执行单个步骤（退出 curses 回到普通终端）──
    def execute_step(self, cat, si):
        step = cat.steps[si]
        curses.def_prog_mode()
        curses.endwin()
        print()
        print("=" * 121)
        print(f" Step {si+1}: {step.title}")
        print("=" * 121)
        success = False
        try:
            success = bool(step.func())
        except KeyboardInterrupt:
            print("\n  ⚠️  已被用户中断 / Interrupted by user.")
            success = False
        except Exception as e:  # noqa: BLE001
            print(red_bold(f"\n  ❌ 异常 / Exception: {e}"))
            success = False
        print()
        if success:
            cat.completed[si] = True
            print(green_bold(f"  ✅ Step {si+1} completed: {step.title}"))
            print()
            print(yellow("  ⏳ Returning to menu in 3 seconds..."))
            time.sleep(3)
        else:
            print(red_bold(f"  ❌ Step {si+1} failed: {step.title}"))
            print()
            try:
                input(red_bold("  Press Enter to return to menu..."))
            except EOFError:
                pass
        curses.reset_prog_mode()
        self.stdscr.clear()
        self.stdscr.refresh()

    # ── 主循环 ──
    def run(self):
        while True:
            self.main_sel, ci = self.menu(
                [c.title for c in self.categories],
                "主菜单 / Main Menu", sel=self.main_sel)
            if ci < 0:
                return
            cat = self.categories[ci]
            while True:
                cat.selected, si = self.menu(
                    [s.title for s in cat.steps], cat.title,
                    cat.warning, cat.completed, cat.dividers,
                    sel=cat.selected)
                if si < 0:
                    break
                self.execute_step(cat, si)

# ═════════════════════════════════════════════
# 入口
# ═════════════════════════════════════════════
def print_colored_logo():
    for line in LOGO:
        print(cyan(line[:48]) + _c(line[48:], "95"))

def sudo_keepalive():
    while True:
        subprocess.run(["sudo", "-n", "true"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        time.sleep(60)

def main():
    try:
        locale.setlocale(locale.LC_ALL, "")
    except locale.Error:
        pass

    for cmd in ("pacman", "sudo"):
        if not which(cmd):
            print(f"Error: '{cmd}' not found. This script must be run on Arch Linux.")
            return 1

    print_colored_logo()
    print("═" * 121)
    print("  ArchInit — 统一安装器 / Unified Installer")
    print("═" * 121)
    print()
    print(">>> Requesting sudo access (password required)...")
    if subprocess.run(["sudo", "-v"], check=False).returncode != 0:
        print("    ❌ Failed to acquire sudo privileges. Aborting.")
        return 1
    threading.Thread(target=sudo_keepalive, daemon=True).start()
    print("    ✅ Sudo privileges acquired.")
    print()
    time.sleep(1)

    def _curses_main(stdscr):
        curses.curs_set(0)
        try:
            curses.set_escdelay(25)
        except (AttributeError, curses.error):
            pass
        ui = UI(stdscr)
        ui.init_colors()
        ui.run()

    try:
        curses.wrapper(_curses_main)
    except KeyboardInterrupt:
        pass
    print()
    print("已退出 / Exited.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
