"""分类：终端美化 / Terminal Beautification。"""
import os
import re
import shutil

from ..config import HOME, ROOT_DIR
from ..shell import Shell
from ..style import Style

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


class TerminalSteps:
    @staticmethod
    def zsh():
        print(">>> Installing Zsh...")
        Shell.run("sudo pacman -S --needed --noconfirm zsh zsh-completions")
        print(">>> Listing available shells...")
        Shell.run("chsh -l")
        print(">>> Changing default shell to Zsh (password required)...")
        Shell.run("chsh -s /usr/bin/zsh || true")
        print()
        print(">>> Configuring Kitty terminal...")
        os.makedirs(os.path.join(HOME, ".config/kitty"), exist_ok=True)
        kitty_conf = os.path.join(HOME, ".config/kitty/kitty.conf")
        if "cursor_trail" not in Shell.read_file(kitty_conf):
            Shell.write_file(kitty_conf,
                             "\ncursor_trail 2\n"
                             "cursor_blink_interval 0.5\n"
                             "cursor_stop_blinking_after 0\n",
                             append=True)
            print("    Kitty cursor settings added.")
        else:
            print("    Kitty cursor settings already present, skipping.")
        return True

    @staticmethod
    def antidote():
        if not Shell.which("zsh"):
            print("Warning: Zsh does not appear to be installed.")
            return Shell.prompt("Press Enter to skip")
        print(">>> Cleaning up any previous Antidote configuration...")
        shutil.rmtree(os.path.join(HOME, ".antidote"), ignore_errors=True)
        zshrc = os.path.join(HOME, ".zshrc")
        txt = Shell.read_file(zshrc)
        txt = re.sub(r"^# === Antidote Start ===$.*?^# === Antidote End ===$\n?",
                     "", txt, flags=re.DOTALL | re.MULTILINE)
        Shell.write_file(zshrc, txt)
        print("    Cleanup done.")
        print(">>> Installing Antidote plugin manager...")
        Shell.run('git clone --depth=1 https://github.com/mattmc3/antidote.git ~/.antidote')
        print()
        print(">>> Creating ~/.zsh_plugins.txt with recommended plugins...")
        Shell.write_file(os.path.join(HOME, ".zsh_plugins.txt"),
                         "zsh-users/zsh-completions\n"
                         "zsh-users/zsh-autosuggestions\n"
                         "zdharma-continuum/fast-syntax-highlighting\n")
        print("    Plugins configured.")
        print()
        print(">>> Appending Antidote configuration to ~/.zshrc...")
        Shell.write_file(zshrc, ANTIDOTE_BLOCK, append=True)
        print("    Antidote configuration written to ~/.zshrc.")
        return True

    @staticmethod
    def starship():
        if not Shell.which("zsh"):
            print("Warning: Zsh does not appear to be installed.")
            return Shell.prompt("Press Enter to skip")
        print(">>> Installing Starship prompt...")
        Shell.run("sudo pacman -S --needed --noconfirm starship")
        print()
        print(">>> Copying Starship config to ~/.config/starship.toml...")
        os.makedirs(os.path.join(HOME, ".config"), exist_ok=True)
        src = os.path.join(ROOT_DIR, "starship/starship.toml")
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
        txt = Shell.read_file(zshrc)
        txt = re.sub(r'^eval "\$\(starship init zsh\)"\n?', "", txt, flags=re.MULTILINE)
        Shell.write_file(zshrc, txt)
        Shell.write_file(zshrc, '\n# Starship 提示符\neval "$(starship init zsh)"\n', append=True)
        print("    Starship init written to ~/.zshrc.")
        return True

    @staticmethod
    def fastfetch_config():
        print(">>> Copying fastfetch config to ~/.config/fastfetch...")
        dst = os.path.join(HOME, ".config/fastfetch")
        os.makedirs(dst, exist_ok=True)
        src = os.path.join(ROOT_DIR, "fastfetch")
        if os.path.isdir(src):
            shutil.copytree(src, dst, dirs_exist_ok=True)
        print("    fastfetch config copied successfully.")
        return True

    @staticmethod
    def fastfetch_startup():
        zshrc = os.path.join(HOME, ".zshrc")
        first = ""
        if os.path.isfile(zshrc):
            with open(zshrc, encoding="utf-8") as f:
                first = f.readline().rstrip("\n")
        if re.fullmatch(r"\s?fastfetch", first):
            print(">>> fastfetch 已存在于 ~/.zshrc 第一行，正在移除（关闭自启）...")
            lines = Shell.read_file(zshrc).splitlines(keepends=True)
            if lines:
                lines = lines[1:]
            Shell.write_file(zshrc, "".join(lines))
            print("    fastfetch 已从 .zshrc 第一行移除。")
            print("    ✅ 已关闭 fastfetch 开机自启。")
        else:
            print(">>> fastfetch 不在 ~/.zshrc 第一行，正在添加（开启自启）...")
            if not os.path.isfile(zshrc):
                open(zshrc, "a").close()
            txt = Shell.read_file(zshrc)
            Shell.write_file(zshrc, " fastfetch\n" + txt)
            print("    fastfetch 已添加为 .zshrc 第一行（带前导空格，不记入历史）。")
            print("    ✅ 已开启 fastfetch 开机自启。")
        return True

    @staticmethod
    def kitty_opacity():
        kitty_conf = os.path.join(HOME, ".config/kitty/kitty.conf")
        if not os.path.isfile(kitty_conf):
            print(Style.yellow(f"  ⚠️  Kitty 配置文件不存在 / Kitty config not found at {kitty_conf}"))
            print("    请先执行「启用 Zsh 终端」（含 Kitty 终端配置）/ Please run the Zsh step first.")
            return Shell.prompt("按 Enter 返回菜单 / Press Enter to return")
        conf = Shell.read_file(kitty_conf)
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
                print(Style.yellow("    ⚠️  无效值，使用默认 0.8 / Invalid value, using default 0.8"))
                new_opacity = "0.8"
        else:
            print(Style.yellow("    ⚠️  无效选项，使用默认 0.8 / Invalid option, using default 0.8"))
            new_opacity = "0.8"
        print()
        print(f">>> 设置背景透明度为 {new_opacity} / Setting background opacity to {new_opacity}...")
        if re.search(r"^background_opacity", conf, re.MULTILINE):
            conf = re.sub(r"^background_opacity\s+.*", f"background_opacity {new_opacity}", conf, flags=re.MULTILINE)
            Shell.write_file(kitty_conf, conf)
        else:
            Shell.write_file(kitty_conf, f"background_opacity {new_opacity}\n", append=True)
        print(Style.green_bold(f"    ✅ 已更新 Kitty 背景透明度为 {new_opacity}"))
        print("    重启 Kitty 终端即可生效 / Restart Kitty terminal to apply")
        return True
