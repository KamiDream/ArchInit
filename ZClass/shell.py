"""Shell 命令执行与文件读写封装。"""
import os
import pty
import re
import select
import shlex
import shutil
import struct
import subprocess
import sys
import termios
import tty
from collections.abc import Callable
from typing import ClassVar

ANSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")
PTY_COLS = 120


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
    def _feed(buf, chunk, on_line):
        """把新数据拼到 buf 上并按 \\r / \\n 切行回调；返回 (剩余 buf, 最后一行)。"""
        buf += chunk
        tail = ""
        while True:
            cuts = [i for i in (buf.find(b"\n"), buf.find(b"\r")) if i >= 0]
            if not cuts:
                break
            idx = min(cuts)
            line = ANSI.sub("", buf[:idx].decode("utf-8", "replace")).strip()
            buf = buf[idx + 1:]
            if line:
                tail = line
                if on_line:
                    on_line(line)
        return buf, tail

    @classmethod
    def _stream_pipe(cls, cmd, on_line=None):
        """从管道（无 tty）逐行读取，返回 (ok, 最后一行)。"""
        proc = subprocess.Popen(
            cmd, shell=True, executable="/bin/bash", stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=0,
        )
        buf = b""
        tail = ""
        if proc.stdout is not None:
            while True:
                chunk = proc.stdout.read(8192)
                if not chunk:
                    break
                buf, new_tail = cls._feed(buf, chunk, on_line)
                tail = new_tail or tail
        if buf.strip():
            line = ANSI.sub("", buf.decode("utf-8", "replace")).strip()
            if line:
                tail = line
                if on_line:
                    on_line(line)
        proc.wait()
        return proc.returncode == 0, tail

    @staticmethod
    def stream(cmd, on_line=None):
        """逐行读取命令输出（不写终端），返回 (ok, 最后一行)。用于展示进度。

        命令跑在临时 pty 上：pacman / git 只有在 isatty() 为真时才输出
        “进度条 + 百分比 + 已下载大小 + 速度”，所以给它一个假终端，再自己按
        \\r / \\n 切行（进度条是用回车原地刷新的）。
        """
        master, slave = pty.openpty()
        try:
            # 给 pty 一个合理的列数，否则 pacman 认为宽度为 0 而不画进度条
            try:
                import fcntl
                fcntl.ioctl(slave, termios.TIOCSWINSZ,
                            struct.pack("HHHH", 24, PTY_COLS, 0, 0))
            except OSError:
                pass
            proc = subprocess.Popen(
                cmd, shell=True, executable="/bin/bash",
                stdin=subprocess.DEVNULL, stdout=slave, stderr=slave,
                close_fds=True, start_new_session=True,
            )
            os.close(slave)
            slave = -1
            tail = ""
            buf = b""
            while True:
                try:
                    ready, _, _ = select.select([master], [], [], 0.2)
                    if not ready:
                        if proc.poll() is not None:
                            break
                        continue
                    chunk = os.read(master, 8192)
                except OSError:   # EIO：子进程退出，pty 关闭
                    break
                if not chunk:
                    break
                buf, new_tail = Shell._feed(buf, chunk, on_line)
                tail = new_tail or tail
            if buf.strip():
                line = ANSI.sub("", buf.decode("utf-8", "replace")).strip()
                if line:
                    tail = line
                    if on_line:
                        on_line(line)
            proc.wait()
            return proc.returncode == 0, tail
        finally:
            if slave >= 0:
                os.close(slave)
            os.close(master)

    @classmethod
    def quiet(cls, cmd):
        """执行命令返回 (ok, 尾部输出)；任务面板激活时实时回报进度。"""
        hook = cls.progress_hook
        if hook is not None:
            return cls.stream(cmd, hook)
        rc, out = cls.capture_all(cmd)
        return rc == 0, out

    @classmethod
    def run_in_tty(cls, cmd):
        """在独立 pty 中运行命令（保证有控制终端 / /dev/tty），并把输入输出接回当前终端。

        适合那些“自己会开 /dev/tty”或需要真实交互的安装脚本（DMS、UU 等）。
        直接继承父进程 stdio 时，某些环境下子进程拿不到控制终端，脚本就会报
        “无法打开新 tty”。
        """
        stdin_fd = sys.stdin.fileno()
        stdout_fd = sys.stdout.fileno()

        pid, master = pty.fork()
        if pid == 0:  # 子进程：pty 即其控制终端
            os.execvp("/bin/bash", ["/bin/bash", "-c", cmd])
            os._exit(127)

        # 把当前终端尺寸同步给 pty，避免程序按 0 列渲染
        try:
            import fcntl
            winsize = fcntl.ioctl(stdin_fd, termios.TIOCGWINSZ, b"\x00" * 8)
            fcntl.ioctl(master, termios.TIOCSWINSZ, winsize)
        except (OSError, termios.error, ValueError):
            pass

        old = None
        try:
            old = termios.tcgetattr(stdin_fd)
            tty.setraw(stdin_fd)   # 逐键转发，Ctrl-C 交给子进程处理
        except (OSError, termios.error, ValueError):
            old = None

        try:
            while True:
                try:
                    ready, _, _ = select.select([master, stdin_fd], [], [], 0.2)
                except OSError:
                    break
                if master in ready:
                    try:
                        data = os.read(master, 4096)
                    except OSError:   # EIO：子进程退出
                        break
                    if not data:
                        break
                    os.write(stdout_fd, data)
                if stdin_fd in ready:
                    try:
                        data = os.read(stdin_fd, 1024)
                    except OSError:
                        data = b""
                    if data:
                        try:
                            os.write(master, data)
                        except OSError:
                            break
        finally:
            if old is not None:
                try:
                    termios.tcsetattr(stdin_fd, termios.TCSADRAIN, old)
                except (OSError, termios.error):
                    pass
            os.close(master)

        try:
            _, status = os.waitpid(pid, 0)
            return os.waitstatus_to_exitcode(status) == 0
        except ChildProcessError:
            return False

    @staticmethod
    def brief(text, limit=60):
        """把命令输出压成一行失败说明（界面里的失败原因）。"""
        if "password is required" in text or "askpass" in text:
            return "sudo 凭证过期 / sudo expired"
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        return lines[-1][:limit] if lines else ""

    @classmethod
    def sudo(cls, cmd):
        """以 root 执行（非交互），返回 (ok, 输出)。

        sudo 的凭证是按 tty 记的（tty_tickets），而我们给命令分配的 pty 每次都是
        新的 /dev/pts/N，会不断触发“需要密码”。所以外层保持**无 tty**（与启动时
        sudo -S -v 建立的票据一致），再在内部用 script 给命令一个 pty，这样既有
        进度条，又不会要密码。
        """
        if shutil.which("script"):
            full = f"sudo -n script -qec {shlex.quote(cmd)} /dev/null"
        else:
            full = f"sudo -n {cmd}"
        hook = cls.progress_hook
        if hook is not None:
            return cls._stream_pipe(full, hook)
        rc, out = cls.capture_all(full)
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
