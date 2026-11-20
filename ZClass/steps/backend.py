"""分类：应用后端切换 / App Backend Toggle。"""
import os
import shlex
import subprocess
import sys

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


class BackendSteps:
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

    @staticmethod
    def _resolve_app():
        """询问应用命令并解析为可执行文件路径；返回空串表示取消。"""
        for _ in range(3):
            raw = BackendSteps._ask("  输入应用命令 / App command (e.g. firefox, code): ")
            if raw is None:
                print(Style.yellow("    ⚠️  无法读取终端输入 / Cannot read terminal input."))
                print("    请在真实终端中直接运行 ./archinit.py")
                print("    Please run ./archinit.py from a real terminal.")
                return ""
            app = raw.strip()
            if not app or app.lower() == "q":
                print("    已取消 / Cancelled.")
                return ""
            if "/" in app:
                cand = os.path.expanduser(app)
                if os.path.exists(cand):
                    return cand
            else:
                target = Shell.capture(f"command -v {shlex.quote(app)}").strip()
                if target and os.path.exists(target):
                    return target
            print(Style.yellow(f"    ⚠️  未找到该命令 / Command not found: {app}"))
            print("    请输入已安装应用的命令名（如 firefox、code）/"
                  " Enter an installed command name (e.g. firefox, code).")
            print()
        print(Style.red_bold("    ❌ 已放弃 / Giving up after 3 attempts."))
        return ""

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
    def _launch(target, label, extra_env):
        env = os.environ.copy()
        env.update(extra_env)
        print()
        print(f">>> 以 {label} 启动 / Launching on {label}...")
        print(f"    {target}")
        try:
            proc = subprocess.Popen(
                [target], env=env, start_new_session=True,
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
        print(f"        env {envs} {shlex.quote(target)}")
        return True

    @staticmethod
    def app_backend():
        print(">>> 应用后端切换 / Launch an app on a chosen backend...")
        print("    流程：输入应用命令 → 选择平台 → 立即启动")
        print("    Flow: enter an app command, pick a backend, it launches right away")
        print("    输入 q 可取消 / Enter q to cancel")
        print()

        target = BackendSteps._resolve_app()
        if not target:
            return Shell.prompt("按 Enter 返回菜单 / Press Enter to return")

        picked = BackendSteps._choose_backend()
        if picked is None:
            return Shell.prompt("按 Enter 返回菜单 / Press Enter to return")

        label, extra_env = picked
        ok = BackendSteps._launch(target, label, extra_env)
        print()
        Shell.prompt("按 Enter 返回菜单 / Press Enter to return")
        return ok
