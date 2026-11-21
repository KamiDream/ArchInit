"""应用编排：启动页、sudo 提权与保活、进入 curses 界面。"""
import curses
import locale
import subprocess
import threading
import time

from .catalog import Catalog
from .shell import Shell
from .ui import UI


class App:
    @staticmethod
    def _keepalive():
        # 注意：必须跟命令执行用同一个“无 tty”上下文，否则续的是另一张票据
        while True:
            subprocess.run(["sudo", "-n", "true"],
                           stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL, check=False)
            time.sleep(60)

    @staticmethod
    def _missing_tools():
        for cmd in ("pacman", "sudo"):
            if not Shell.which(cmd):
                return cmd
        return ""

    @staticmethod
    def _sudo_cached():
        """检查“无 tty”上下文里的 sudo 票据（与所有 sudo -n 命令一致）。"""
        return subprocess.run(["sudo", "-n", "true"],
                              stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL, check=False).returncode == 0

    @staticmethod
    def _sudo_validate(secret):
        """用 sudo -S 验证密码（密码从 stdin 送入，不经过终端回显）。"""
        try:
            return subprocess.run(["sudo", "-S", "-v"], input=secret + "\n", text=True,
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                  check=False).returncode == 0
        except OSError:
            return False

    def _acquire_sudo(self, ui):
        """已缓存则短暂展示启动页；否则直接在启动页里输密码（不切屏）。"""
        if self._sudo_cached():
            ui.draw_splash("✅ sudo 权限已就绪 / sudo privileges ready")
            time.sleep(0.6)  # 给启动页一个可读的展示时长，避免一闪而过
            return True

        for attempt in range(3):
            if attempt == 0:
                msg = "🔐 需要 sudo 密码 / sudo password required"
            else:
                msg = "❌ 密码错误，请重试 / wrong password, try again"
            secret = ui.ask_sudo(msg, error=attempt > 0)
            if secret is None:
                return False
            if secret and self._sudo_validate(secret):
                return True
        return False

    def _curses_main(self, stdscr):
        curses.curs_set(0)
        try:
            curses.set_escdelay(25)
        except (AttributeError, curses.error):
            pass

        categories = Catalog.build()
        ui = UI(stdscr, categories)
        ui.init_colors()

        missing = self._missing_tools()
        if missing:
            ui.draw_splash(f"❌ 未找到 {missing}，请在 Arch Linux 上运行 / not found, run on Arch Linux",
                           error=True)
            stdscr.getch()
            return 1

        ui.draw_splash("🔐 正在检查 sudo 权限 … / checking sudo access")
        if not self._acquire_sudo(ui):
            ui.draw_splash("❌ 获取 sudo 权限失败 / failed to acquire sudo privileges", error=True)
            stdscr.getch()
            return 1

        threading.Thread(target=self._keepalive, daemon=True).start()

        # 从 sudo 提示回到界面后恢复终端状态
        try:
            stdscr.keypad(True)
            stdscr.timeout(-1)
        except curses.error:
            pass
        ui.run()
        return 0

    def run(self):
        try:
            locale.setlocale(locale.LC_ALL, "")
        except locale.Error:
            pass

        code = 1
        try:
            code = curses.wrapper(self._curses_main)
        except KeyboardInterrupt:
            code = 0
        except curses.error:
            # execute_step 已手动 endwin()，wrapper 末尾再调用会返回 ERR —— 正常情况
            code = 0
        print()
        print("已退出 / Exited.")
        return code
