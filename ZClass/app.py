"""应用编排：启动横幅、sudo 提权与保活、进入 curses 界面。"""
import curses
import locale
import subprocess
import threading
import time

from .catalog import Catalog
from .config import BRAND_LEFT, BRAND_RIGHT
from .shell import Shell
from .style import Style
from .ui import UI


class App:
    @staticmethod
    def _print_banner():
        print(Style.c(BRAND_LEFT, "94") + Style.c(BRAND_RIGHT, "95"))
        print("═" * 121)
        print("  ArchInit — 统一安装器 / Unified Installer")
        print("═" * 121)
        print()

    @staticmethod
    def _keepalive():
        while True:
            subprocess.run(["sudo", "-n", "true"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
            time.sleep(60)

    def run(self):
        try:
            locale.setlocale(locale.LC_ALL, "")
        except locale.Error:
            pass

        for cmd in ("pacman", "sudo"):
            if not Shell.which(cmd):
                print(f"Error: '{cmd}' not found. This script must be run on Arch Linux.")
                return 1

        self._print_banner()
        print(">>> Requesting sudo access (password required)...")
        if subprocess.run(["sudo", "-v"], check=False).returncode != 0:
            print("    ❌ Failed to acquire sudo privileges. Aborting.")
            return 1
        threading.Thread(target=self._keepalive, daemon=True).start()
        print("    ✅ Sudo privileges acquired.")
        print()
        time.sleep(1)

        categories = Catalog.build()

        def _curses_main(stdscr):
            curses.curs_set(0)
            try:
                curses.set_escdelay(25)
            except (AttributeError, curses.error):
                pass
            ui = UI(stdscr, categories)
            ui.init_colors()
            ui.run()

        try:
            curses.wrapper(_curses_main)
        except KeyboardInterrupt:
            pass
        except curses.error:
            # execute_step 已手动 endwin()，wrapper 末尾再调用会返回 ERR —— 正常情况
            pass
        print()
        print("已退出 / Exited.")
        return 0
