"""分类：应用后端切换 / App Backend Toggle。"""
import os
import shlex
import shutil
import subprocess

from ..config import HOME
from ..model import CANCELLED
from ..picker import FreeText, Picker
from ..shell import Shell
from ..status import Status

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
    # 记住上次的选择，返回/再次进入时恢复
    _last_app_idx: int = 0
    _last_app_query: str = ""
    _last_backend_idx: int = 0

    # ── .desktop 扫描 ──
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

    # ── 输入的命令（不在扫描列表里的应用）──
    @staticmethod
    def _resolve_free(text):
        """把用户输入的文字解析成 (显示名, argv)；找不到返回 None。"""
        app = text.strip()
        if not app:
            return None
        if "/" in app:
            path = os.path.expanduser(app)
            if os.path.exists(path):
                return os.path.basename(path), [path]
            return None
        target = shutil.which(app)
        if target:
            return app, [target]
        found = Shell.capture(f"command -v {shlex.quote(app)}").strip()
        if found and os.path.isabs(found) and os.path.exists(found):
            return app, [found]
        return None

    # ── 选择应用（列表 + 可输入列表外命令）──
    @classmethod
    def _pick_app(cls):
        """返回 (显示名, argv) 或 None（用户取消）。"""
        apps = cls._installed_apps()
        rows = [(name, os.path.basename(argv[0])) for name, argv, _aliases in apps]
        title = "选择应用 / Pick app"
        subtitle = ("选择应用 → 选择平台 → 立即启动 · 输入可过滤 · Tab 或空匹配 Enter 当命令用 / "
                    "pick app → backend → launch · type to filter · Tab uses typed text as a command")
        notice = "" if apps else (
            "⚠️  未找到已安装应用，可直接输入命令后按 Tab / no .desktop apps — type a command and press Tab")

        while True:
            res = Picker.choose(title, rows, initial=cls._last_app_idx,
                                query=cls._last_app_query, allow_free=True,
                                subtitle=subtitle, notice=notice)
            cls._last_app_query = Picker.last_query

            if isinstance(res, FreeText):
                picked = cls._resolve_free(str(res))
                if picked:
                    return picked
                notice = f"⚠️  未找到该命令 / Command not found: {str(res).strip()}"
                continue
            if res is None:
                return None
            if not isinstance(res, int):
                return None
            cls._last_app_idx = res
            name, argv, _aliases = apps[res]
            return name, argv

    # ── 选择平台 ──
    @staticmethod
    def _choose_backend(app_label=""):
        """返回 (平台名, 环境变量字典) 或 None（用户按 Esc 返回选应用）。"""
        rows = [
            ("Wayland", "原生 / native"),
            ("X11 (XWayland)", "兼容模式 / compatibility"),
        ]
        subtitle = f"已选应用 / App: {app_label}" if app_label else ""
        idx = Picker.choose("选择启动平台 / Choose backend", rows,
                            initial=BackendSteps._last_backend_idx, subtitle=subtitle)
        if not isinstance(idx, int):
            return None
        BackendSteps._last_backend_idx = idx
        return ("Wayland", WAYLAND_ENV) if idx == 0 else ("X11 (XWayland)", X11_ENV)

    # ── 启动 ──
    @staticmethod
    def _launch(argv, name, label, extra_env):
        env = os.environ.copy()
        env.update(extra_env)
        try:
            proc = subprocess.Popen(
                argv, env=env, start_new_session=True,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
        except OSError as e:
            Status.set(f"❌ 启动失败 / Failed to launch {name}: {e}")
            return False
        cmd = " ".join(shlex.quote(t) for t in argv)
        Status.set(f"🚀 {label} · {name} (pid {proc.pid}) · {cmd}")
        return True

    # ── 流程：选应用 → 选平台 → 启动 ──
    @classmethod
    def _select_and_launch(cls):
        while True:
            entry = cls._pick_app()
            if not entry:
                return CANCELLED

            name, argv = entry
            picked = cls._choose_backend(f"{name}  ({argv[0]})")
            if picked is None:
                continue

            label, extra_env = picked
            return cls._launch(argv, name, label, extra_env)

    @classmethod
    def app_backend(cls):
        return cls._select_and_launch()
