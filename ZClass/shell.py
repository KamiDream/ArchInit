"""Shell 命令执行与文件读写封装。"""
import os
import shutil
import subprocess
import sys
import termios
import tty
from collections.abc import Callable
from typing import ClassVar


class Shell:
    # 任务面板存在时由 TaskView 设置，用于实时回报命令输出（进度行）
    progress_hook: ClassVar[Callable[[str], None] | None] = None

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
    def stream(cmd, on_line=None):
        """逐行读取命令输出（不写终端），返回 (ok, 最后一行)。用于展示进度。

        用二进制原始读取（bufsize=0），否则 read(n) 会阻塞到读满或 EOF，进度就不是实时的
        了；再自己按 \\r / \\n 切分，以兼容 pacman、git --progress 那种回车刷新。
        """
        proc = subprocess.Popen(
            cmd, shell=True, executable="/bin/bash",
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=0,
        )
        tail = ""
        buf = b""
        if proc.stdout is not None:
            while True:
                chunk = proc.stdout.read(4096)
                if not chunk:
                    break
                buf += chunk
                while True:
                    cuts = [i for i in (buf.find(b"\n"), buf.find(b"\r")) if i >= 0]
                    if not cuts:
                        break
                    idx = min(cuts)
                    line = buf[:idx].decode("utf-8", "replace").strip()
                    buf = buf[idx + 1:]
                    if line:
                        tail = line
                        if on_line:
                            on_line(line)
        proc.wait()
        return proc.returncode == 0, tail

    @classmethod
    def quiet(cls, cmd):
        """执行命令返回 (ok, 尾部输出)；任务面板激活时实时回报进度。"""
        hook = cls.progress_hook
        if hook is not None:
            return cls.stream(cmd, hook)
        rc, out = cls.capture_all(cmd)
        return rc == 0, out

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
        return cls.quiet(f"sudo -n {cmd}")

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
