"""分类：应用后端切换 / App Backend Toggle。"""
import os
import shlex
import shutil
import subprocess
import sys

from ..config import HOME
from ..picker import Picker
from ..shell import Shell
from ..style import Style

WAYLAND_ENV = {
    "QT_QPA_PLATFORM": "wayland",
    "GDK_BACKEND": "wayland",
    "SDL_VIDEODRIVER": "wayland",
    "MOZ_ENABLE_WAYLAND": "1",
    "ELECTRON_OZONE_PLATFORM_HINT": "wayland",
}

X11_ENV = {
    "QT_QPA_PLATFORM": "xcb",
    "GDK_BACKEND": "x11",
    "SDL_VIDEODRIVER": "x11",
    "MOZ_ENABLE_WAYLAND": "0",
    "ELECTRON_OZONE_PLATFORM_HINT": "x11",
}

DESKTOP_DIRS = (
    "/usr/share/applications",
    "/usr/local/share/applications",
    os.path.join(HOME, ".local/share/applications"),
)


class BackendSteps:
    # ── 终端输入 ──
    @staticmethod
    def _ask(prompt):
        """读取一行终端输入；stdin 不可用（EOF）时回退到 /dev/tty。"""
        try:
            return input(prompt)
        except EOFError:
            pass
        try:
            with open("/dev/tty", encoding="utf-8", errors="replace") as tty:
                sys.stdout.write(prompt)
                sys.stdout.flush()
                line = tty.readline()
        except OSError:
            return None
        return line if line else None

    # ── .desktop 扫描（用于「不知道命令名」的场景）──
    @staticmethod
    def _desktop_exec(exec_line):
        """把 Desktop Entry 的 Exec 行转成可执行 argv；失败返回 []。"""
        try:
            tokens = shlex.split(exec_line)
        except ValueError:
            return []
        tokens = [t for t in tokens if not t.startswith("%")]
        if tokens and os.path.basename(tokens[0]) == "env":
            tokens = tokens[1:]
            while tokens and "=" in tokens[0] and not tokens[0].startswith("/"):
                tokens = tokens[1:]
        if not tokens:
            return []
        prog = tokens[0]
        if os.path.isabs(prog):
            if not os.path.exists(prog):
                return []
        else:
            found = shutil.which(prog)
            if not found:
                return []
            tokens[0] = found
        return tokens

    @staticmethod
    def _parse_desktop(path):
        """解析单个 .desktop，返回 (显示名, argv, 搜索别名) 或 None。"""
        try:
            with open(path, encoding="utf-8", errors="replace") as f:
                lines = f.read().splitlines()
        except OSError:
            return None
        in_entry = False
        fields = {}
        for line in lines:
            s = line.strip()
            if s.startswith("[") and s.endswith("]"):
                in_entry = s == "[Desktop Entry]"
                continue
            if not in_entry or not s or s.startswith("#") or "=" not in s:
                continue
            key, value = s.split("=", 1)
            fields.setdefault(key.strip(), value.strip())
        if fields.get("Type", "Application") != "Application":
            return None
        if fields.get("NoDisplay", "").lower() == "true":
            return None
        name = fields.get("Name[zh_CN]") or fields.get("Name") or ""
        argv = BackendSteps._desktop_exec(fields.get("Exec", ""))
        if not name or not argv:
            return None
        aliases = [name]
        for key, value in fields.items():
            if value and (key == "Name" or key.startswith("Name[") or key == "GenericName"):
                aliases.append(value)
        aliases.append(os.path.basename(argv[0]))
        return name, argv, aliases

    @staticmethod
    def _installed_apps():
        seen = set()
        apps = []
        for d in DESKTOP_DIRS:
            if not os.path.isdir(d):
                continue
            for root, _dirs, files in os.walk(d):
                for fn in sorted(files):
                    if not fn.endswith(".desktop"):
                        continue
                    parsed = BackendSteps._parse_desktop(os.path.join(root, fn))
                    if not parsed:
                        continue
                    key = (parsed[0], tuple(parsed[1]))
                    if key in seen:
                        continue
                    seen.add(key)
                    apps.append(parsed)
        apps.sort(key=lambda a: a[0].lower())
        return apps

    @classmethod
    def _pick_from_apps(cls):
        """列出全部已安装应用，供方向键上下选择（可直接输入关键字过滤）；返回 (显示名, argv) 或 None。"""
        apps = cls._installed_apps()
        if not apps:
            print(Style.yellow("    ⚠️  未找到已安装应用 / No installed applications found."))
            print("    请改用手动输入命令 / Enter the command manually instead.")
            return None

        rows = [(name, os.path.basename(argv[0])) for name, argv, _aliases in apps]
        print("    正在打开应用列表 / Opening the app list...")
        idx = Picker.choose(
            "从已安装应用中选择 / Pick installed app（输入可过滤 / type to filter）", rows)
        if idx is None:
            return None
        name, argv, _aliases = apps[idx]
        print(f"    ✅ 已选择 / Picked: {name}  ({' '.join(shlex.quote(t) for t in argv)})")
        return name, argv

    # ── 手动输入命令 ──
    @staticmethod
    def _resolve_command():
        """询问应用命令并解析为 (显示名, argv)；返回 None 表示取消。"""
        for _ in range(3):
            raw = BackendSteps._ask("  输入应用命令 / App command (e.g. firefox, virt-manager): ")
            if raw is None:
                print(Style.yellow("    ⚠️  无法读取终端输入 / Cannot read terminal input."))
                print("    请在真实终端中直接运行 ./archinit.py")
                print("    Please run ./archinit.py from a real terminal.")
                return None
            app = raw.strip()
            if not app or app.lower() == "q":
                print("    已取消 / Cancelled.")
                return None
            if "/" in app:
                cand = os.path.expanduser(app)
                if os.path.exists(cand):
                    return os.path.basename(cand), [cand]
            else:
                target = Shell.capture(f"command -v {shlex.quote(app)}").strip()
                if target and os.path.exists(target):
                    return app, [target]
            print(Style.yellow(f"    ⚠️  未找到该命令 / Command not found: {app}"))
            print("    可改用「从已安装应用中选择」/ Try \"pick from installed apps\" instead.")
            print()
        print(Style.red_bold("    ❌ 已放弃 / Giving up after 3 attempts."))
        return None

    @staticmethod
    def _choose_backend():
        """选择启动平台；返回 (平台名, 环境变量字典) 或 None 表示取消。"""
        print()
        print("  选择启动平台 / Choose backend:")
        print("    1) Wayland")
        print("    2) X11 (XWayland)")
        print("    q) 取消 / Cancel")
        print()
        for _ in range(3):
            raw = BackendSteps._ask("  选择 / Choose [1/2/q]: ")
            if raw is None:
                print(Style.yellow("    ⚠️  无法读取终端输入 / Cannot read terminal input."))
                return None
            ans = raw.strip().lower()
            if ans in ("", "q"):
                print("    已取消 / Cancelled.")
                return None
            if ans in ("1", "w", "wl", "wayland"):
                return "Wayland", WAYLAND_ENV
            if ans in ("2", "x", "x11", "xcb"):
                return "X11 (XWayland)", X11_ENV
            print(Style.yellow("    ⚠️  请输入 1 或 2 / Enter 1 or 2."))
        print(Style.red_bold("    ❌ 已放弃 / Giving up after 3 attempts."))
        return None

    @staticmethod
    def _launch(argv, name, label, extra_env):
        env = os.environ.copy()
        env.update(extra_env)
        print()
        print(f">>> 以 {label} 启动 / Launching on {label}...")
        print(f"    {name}: {' '.join(shlex.quote(t) for t in argv)}")
        try:
            proc = subprocess.Popen(
                argv, env=env, start_new_session=True,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
        except OSError as e:
            print(Style.red_bold(f"    ❌ 启动失败 / Failed to launch: {e}"))
            return False
        print(Style.green_bold(f"    ✅ 已启动 / Started (pid {proc.pid})"))
        print()
        print("    提示 / Tip:")
        print("      · 界面可能要几秒后才出现；关闭应用后本工具仍可继续使用。")
        print("      · The window may take a moment; the tool keeps running after you close the app.")
        print("      · 若应用没有出现，可在终端手动运行下面这行排查 / If nothing appears, run this manually:")
        envs = " ".join(f"{k}={v}" for k, v in extra_env.items())
        cmd = " ".join(shlex.quote(t) for t in argv)
        print(f"        env {envs} {cmd}")
        return True

    @classmethod
    def _run(cls, entry):
        """公共尾段：选平台 → 启动 → 等待回车。"""
        picked = cls._choose_backend()
        if picked is None:
            print()
            return False
        label, extra_env = picked
        name, argv = entry
        ok = cls._launch(argv, name, label, extra_env)
        print()
        Shell.prompt("按 Enter 返回菜单 / Press Enter to return")
        return ok

    @classmethod
    def by_command(cls):
        """Step 1：手动输入命令。"""
        print(">>> 输入命令启动 / Launch by command...")
        print("    输入应用命令（如 firefox、virt-manager）→ 选择平台 → 立即启动")
        print("    Type an app command, pick a backend, it launches right away")
        print("    输入 q 可取消 / Enter q to cancel")
        print()

        entry = cls._resolve_command()
        if not entry:
            print()
            return Shell.prompt("按 Enter 返回菜单 / Press Enter to return")
        return cls._run(entry)

    @classmethod
    def from_installed(cls):
        """Step 2：从已安装应用（.desktop）中选择。"""
        print(">>> 从已安装应用中选择 / Pick from installed apps...")
        print("    打开列表后用 ↑/↓ 上下选择（可直接输入关键字过滤），Enter 确定，q/Esc 取消")
        print("    Use ↑/↓ to move (type to filter), Enter to confirm, q/Esc to cancel")
        print("    不知道命令名时用这个（例如 KVM 的「虚拟系统管理器」）/ Use this when you don't know the command name")
        print()

        entry = cls._pick_from_apps()
        if not entry:
            print()
            return Shell.prompt("按 Enter 返回菜单 / Press Enter to return")
        return cls._run(entry)
