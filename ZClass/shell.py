"""Shell 命令执行与文件读写封装。"""
import os
import shutil
import subprocess


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
    def which(name):
        return shutil.which(name) is not None

    @classmethod
    def installed(cls, pkg):
        return cls.ok(f"pacman -Q {pkg} >/dev/null 2>&1")

    @staticmethod
    def prompt(msg="Press Enter to continue..."):
        """等待 Enter；输入 q 返回 False。"""
        try:
            ans = input(f"  [{msg}]  (or press q to return to menu) ")
        except EOFError:
            return True
        return ans.strip().lower() != "q"

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
