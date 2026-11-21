"""分类：终端美化 / Terminal Beautification。"""
import os
import re
import shutil

from ..config import HOME, ROOT_DIR
from ..model import CANCELLED
from ..picker import Picker
from ..shell import Shell
from ..status import Status
from ..taskview import TaskView

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
    # ── Zsh + Kitty ──
    @classmethod
    def zsh(cls):
        def set_shell():
            # 用 usermod 代替 chsh，避免在界面里弹出密码提示
            return Shell.sudo('usermod --shell /usr/bin/zsh "$(whoami)"')

        def kitty_cursor():
            os.makedirs(os.path.join(HOME, ".config/kitty"), exist_ok=True)
            kitty_conf = os.path.join(HOME, ".config/kitty/kitty.conf")
            if "cursor_trail" in Shell.read_file(kitty_conf):
                return True
            Shell.write_file(kitty_conf,
                             "\ncursor_trail 2\n"
                             "cursor_blink_interval 0.5\n"
                             "cursor_stop_blinking_after 0\n",
                             append=True)
            return True

        ok = TaskView.run("终端美化 · 启用 Zsh / Enable Zsh Shell", [
            ("安装 zsh + zsh-completions", lambda: Shell.pacman("zsh zsh-completions")),
            ("把默认 shell 改为 zsh / set default shell", set_shell),
            ("写入 Kitty 光标配置 / kitty cursor settings", kitty_cursor),
        ])
        Status.set("✅ Zsh 已启用（重新登录后生效）/ enabled — re-login to apply" if ok
                   else "❌ Zsh 配置失败 / failed")
        return ok

    # ── Antidote ──
    @classmethod
    def antidote(cls):
        def check_zsh():
            if Shell.which("zsh"):
                return True
            return False, "未安装 zsh，请先执行上一步 / zsh not installed"

        def cleanup():
            shutil.rmtree(os.path.join(HOME, ".antidote"), ignore_errors=True)
            zshrc = os.path.join(HOME, ".zshrc")
            txt = Shell.read_file(zshrc)
            txt = re.sub(r"^# === Antidote Start ===$.*?^# === Antidote End ===$\n?",
                         "", txt, flags=re.DOTALL | re.MULTILINE)
            Shell.write_file(zshrc, txt)
            return True

        def clone():
            ok, out = Shell.quiet(
                "git clone --depth=1 https://github.com/mattmc3/antidote.git ~/.antidote")
            return ok, Shell.brief(out)

        def plugins():
            Shell.write_file(os.path.join(HOME, ".zsh_plugins.txt"),
                             "zsh-users/zsh-completions\n"
                             "zsh-users/zsh-autosuggestions\n"
                             "zdharma-continuum/fast-syntax-highlighting\n")
            return True

        def append_block():
            Shell.write_file(os.path.join(HOME, ".zshrc"), ANTIDOTE_BLOCK, append=True)
            return True

        ok = TaskView.run("终端美化 · Antidote 插件管理器 / Antidote", [
            ("检查 zsh / check zsh", check_zsh),
            ("清理旧的 Antidote 配置 / cleanup", cleanup),
            ("克隆 antidote / clone", clone),
            ("写入 ~/.zsh_plugins.txt", plugins),
            ("写入 ~/.zshrc 配置块 / append config", append_block),
        ])
        Status.set("✅ Antidote 已配置，重新打开终端生效 / configured" if ok
                   else "❌ Antidote 配置失败 / failed")
        return ok

    # ── Starship ──
    @classmethod
    def starship(cls):
        def check_zsh():
            if Shell.which("zsh"):
                return True
            return False, "未安装 zsh，请先执行「启用 Zsh 终端」/ zsh not installed"

        def copy_config():
            os.makedirs(os.path.join(HOME, ".config"), exist_ok=True)
            src = os.path.join(ROOT_DIR, "starship/starship.toml")
            if not os.path.isfile(src):
                return False, "缺少 starship/starship.toml"
            shutil.copyfile(src, os.path.join(HOME, ".config/starship.toml"))
            return True

        def add_init():
            zshrc = os.path.join(HOME, ".zshrc")
            txt = Shell.read_file(zshrc)
            txt = re.sub(r'^eval "\$\(starship init zsh\)"\n?', "", txt, flags=re.MULTILINE)
            Shell.write_file(zshrc, txt)
            Shell.write_file(zshrc, '\n# Starship 提示符\neval "$(starship init zsh)"\n', append=True)
            return True

        ok = TaskView.run("终端美化 · Starship 提示符 / Starship Prompt", [
            ("检查 zsh / check zsh", check_zsh),
            ("安装 starship", lambda: Shell.pacman("starship")),
            ("复制 starship.toml / copy config", copy_config),
            ("写入 ~/.zshrc 初始化 / append init", add_init),
        ])
        Status.set("✅ Starship 已配置（󰄛 ❯ Catppuccin Macchiato）/ configured" if ok
                   else "❌ Starship 配置失败 / failed")
        return ok

    # ── fastfetch 配置 ──
    @classmethod
    def fastfetch_config(cls):
        def copy_config():
            dst = os.path.join(HOME, ".config/fastfetch")
            src = os.path.join(ROOT_DIR, "fastfetch")
            if not os.path.isdir(src):
                return False, "缺少 fastfetch 配置目录 / config dir missing"
            os.makedirs(dst, exist_ok=True)
            shutil.copytree(src, dst, dirs_exist_ok=True)
            return True

        ok = TaskView.run("终端美化 · fastfetch 配置 / fastfetch Config", [
            ("复制 fastfetch 配置到 ~/.config/fastfetch", copy_config),
        ])
        Status.set("✅ fastfetch 配置已复制 / config copied" if ok
                   else "❌ fastfetch 配置失败 / failed")
        return ok

    # ── fastfetch 开机显示 ──
    @classmethod
    def fastfetch_startup(cls):
        zshrc = os.path.join(HOME, ".zshrc")
        first = ""
        if os.path.isfile(zshrc):
            with open(zshrc, encoding="utf-8") as f:
                first = f.readline().rstrip("\n")

        if re.fullmatch(r"\s?fastfetch", first):
            lines = Shell.read_file(zshrc).splitlines(keepends=True)[1:]
            Shell.write_file(zshrc, "".join(lines))
            Status.set("✅ 已关闭 fastfetch 开机自启 / startup disabled")
        else:
            if not os.path.isfile(zshrc):
                open(zshrc, "a").close()
            Shell.write_file(zshrc, " fastfetch\n" + Shell.read_file(zshrc))
            Status.set("✅ 已开启 fastfetch 开机自启 / startup enabled")
        return True

    # ── Kitty 背景透明度 ──
    @classmethod
    def kitty_opacity(cls):
        kitty_conf = os.path.join(HOME, ".config/kitty/kitty.conf")
        if not os.path.isfile(kitty_conf):
            Status.set(f"❌ 未找到 {kitty_conf}，请先执行「启用 Zsh 终端」/ run Zsh step first")
            return False

        conf = Shell.read_file(kitty_conf)
        m = re.search(r"^background_opacity\s+([\d.]+)", conf, re.MULTILINE)
        current = m.group(1) if m else "未设置 / not set"

        rows = [
            ("0.6", "更透明 / more transparent"),
            ("0.7", ""),
            ("0.8", "默认 / default"),
            ("0.9", ""),
            ("1.0", "完全不透明 / opaque"),
        ]
        initial = next((i for i, (v, _) in enumerate(rows) if v == current), 2)
        idx = Picker.choose(f"Kitty 背景透明度 / Background opacity（当前 / current: {current}）",
                            rows, initial=initial)
        if not isinstance(idx, int):
            return CANCELLED

        value = rows[idx][0]
        if re.search(r"^background_opacity", conf, re.MULTILINE):
            conf = re.sub(r"^background_opacity\s+.*", f"background_opacity {value}",
                          conf, flags=re.MULTILINE)
            Shell.write_file(kitty_conf, conf)
        else:
            Shell.write_file(kitty_conf, f"background_opacity {value}\n", append=True)
        Status.set(f"✅ Kitty 背景透明度已设为 {value}，重启 Kitty 生效 / restart Kitty to apply")
        return True
