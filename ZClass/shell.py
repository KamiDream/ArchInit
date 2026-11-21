"""Shell 命令执行与文件读写封装。"""
import os
import shutil
import subprocess
import sys
import termios
import tty


class Shell:
    @staticmethod
    def run(cmd):
        """在当前终端（已退出 curses）执行 shell 命令，继承 stdin/stdout。"""
        return subprocess.run(cmd, shell=True, executable="/bin/bash", check=False).returncode

    @staticmethod
    def ok(cmd):
        """执行命令并只返回是否成功（静默）。"""
        return subprocess.run(
            cmd, shell=True, executable="/bin/bash",
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False,
        ).returncode == 0

    @staticmethod
    def capture(cmd):
        """执行命令并捕获 stdout。"""
        return subprocess.run(
            cmd, shell=True, executable="/bin/bash",
            capture_output=True, text=True, check=False,
        ).stdout

    @staticmethod
    def capture_all(cmd):
        """执行命令并捕获 stdout+stderr，返回 (returncode, 输出文本)。用于不在终端刷屏的场景。"""
        r = subprocess.run(
            cmd, shell=True, executable="/bin/bash",
            capture_output=True, text=True, errors="replace", check=False,
        )
        return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()

    @staticmethod
    def brief(text, limit=60):
        """把命令输出压成一行失败说明（界面里的失败原因）。"""
        if "password is required" in text or "askpass" in text:
            return "sudo 凭证过期 / sudo expired"
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        return lines[-1][:limit] if lines else ""

    @classmethod
    def sudo(cls, cmd):
        """以非交互方式（sudo -n）执行 root 命令，返回 (ok, 输出)。"""
        rc, out = cls.capture_all(f"sudo -n {cmd}")
        return rc == 0, out

    @classmethod
    def pacman(cls, pkgs, action="-S --needed --noconfirm"):
        """pacman 操作（静默），返回 (ok, 输出)。"""
        return cls.sudo(f"pacman {action} {pkgs}")

    @staticmethod
    def which(name):
        return shutil.which(name) is not None

    @classmethod
    def installed(cls, pkg):
        return cls.ok(f"pacman -Q {pkg} >/dev/null 2>&1")

    @staticmethod
    def wait_key(msg="按 Enter 继续 / Press Enter to continue"):
        """单键等待：Enter 继续（True）；q 或 ESC 返回（False）。ESC 即时生效。"""
        label = f"  [{msg}]  Enter 继续 · q/ESC 返回 / Enter=continue, q/ESC=back  "
        fd = -1
        old = None
        try:
            fd = sys.stdin.fileno()
            if not os.isatty(fd):
                raise OSError("stdin is not a tty")
            old = termios.tcgetattr(fd)
            tty.setcbreak(fd)
            mode = termios.tcgetattr(fd)
            mode[3] &= ~termios.ECHO  # 不回显按键（Ctrl-C 仍可中断）
            termios.tcsetattr(fd, termios.TCSADRAIN, mode)
        except (OSError, ValueError, termios.error):
            try:
                input(label)
            except EOFError:
                pass
            return True
        try:
            sys.stdout.write(label)
            sys.stdout.flush()
            while True:
                ch = sys.stdin.read(1)
                if ch in ("", "\n", "\r"):
                    return True
                if ch in ("q", "Q", "\x1b"):
                    return False
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
            sys.stdout.write("\n")
            sys.stdout.flush()

    @staticmethod
    def prompt(msg="按 Enter 继续 / Press Enter to continue"):
        """等待按键：Enter 继续（True）；q 或 ESC 返回（False）。"""
        return Shell.wait_key(msg)

    @staticmethod
    def sudo_write(path, content, append=False):
        args = ["sudo", "tee"] + (["-a"] if append else []) + [path]
        subprocess.run(args, input=content, text=True, stdout=subprocess.DEVNULL, check=False)

    @staticmethod
    def write_file(path, content, append=False):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "a" if append else "w", encoding="utf-8") as f:
            f.write(content)

    @staticmethod
    def read_file(path):
        try:
            with open(path, encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return ""
