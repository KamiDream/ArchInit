"""分类：修补工具 / Patch Tools。"""
import os
import shutil
import time

from ..config import HOME
from ..shell import Shell
from ..status import Status
from ..taskview import TaskView
from .login_manager import GREETD_CONF, enable_greetd, ensure_background

XDG_DIRS = (
    'XDG_DESKTOP_DIR="$HOME/Desktop"\n'
    'XDG_DOWNLOAD_DIR="$HOME/Downloads"\n'
    'XDG_TEMPLATES_DIR="$HOME/Templates"\n'
    'XDG_PUBLICSHARE_DIR="$HOME/Public"\n'
    'XDG_DOCUMENTS_DIR="$HOME/Documents"\n'
    'XDG_MUSIC_DIR="$HOME/Music"\n'
    'XDG_PICTURES_DIR="$HOME/Pictures"\n'
    'XDG_VIDEOS_DIR="$HOME/Videos"\n'
    'XDG_PROJECTS_DIR="$HOME/Projects"\n'
)

NAME_MAP = (
    ("XDG_DESKTOP_DIR", "Desktop"),
    ("XDG_DOWNLOAD_DIR", "Downloads"),
    ("XDG_TEMPLATES_DIR", "Templates"),
    ("XDG_PUBLICSHARE_DIR", "Public"),
    ("XDG_DOCUMENTS_DIR", "Documents"),
    ("XDG_MUSIC_DIR", "Music"),
    ("XDG_PICTURES_DIR", "Pictures"),
    ("XDG_VIDEOS_DIR", "Videos"),
    ("XDG_PROJECTS_DIR", "Projects"),
)


class PatchSteps:
    # ── UU 加速器 ──
    @classmethod
    def uu(cls):
        def make_dir():
            ok, out = Shell.sudo("mkdir -p /home/deck")
            if not ok:
                return False, Shell.brief(out)
            return Shell.sudo('chown "$(whoami)" /home/deck')

        def install():
            # 官方脚本可能要求交互，放到独立 pty 里跑（保证有控制终端）
            with TaskView.terminal():
                ok = Shell.run_in_tty("curl -s uudeck.com | sudo bash")
            return ok, "安装脚本未成功完成 / installer did not finish"

        ok = TaskView.run("修补工具 · UU 加速器 / UU Accelerator", [
            ("创建 /home/deck 并授权 / create & chown", make_dir),
            ("下载并运行官方安装脚本 / run installer", install),
        ])
        Status.set("✅ UU 加速器已安装 / installed" if ok
                   else "❌ UU 加速器安装未完成 / install not finished")
        return ok

    # ── XDG 用户目录转英文 ──
    @staticmethod
    def _parse_xdg_dirs(path):
        d = {}
        for line in Shell.read_file(path).splitlines():
            line = line.strip()
            if line.startswith("XDG_") and "=" in line:
                k, v = line.split("=", 1)
                v = v.strip().strip('"').replace("$HOME", HOME)
                d[k.strip()] = v
        return d

    @classmethod
    def xdg(cls):
        conf = os.path.join(HOME, ".config/user-dirs.dirs")
        state = {"bak": "", "old": {}, "migrated": 0, "failed": []}

        def backup_and_write():
            if os.path.isfile(conf):
                state["bak"] = conf + ".bak." + str(int(time.time()))
                shutil.copyfile(conf, state["bak"])
                state["old"] = cls._parse_xdg_dirs(state["bak"])
            Shell.write_file(
                conf,
                "# This file is written by ArchInit (archinit.py)\n"
                "# XDG user directories with English names\n"
                "# System locale remains Chinese (zh_CN.UTF-8)\n"
                "#\n" + XDG_DIRS)
            return True

        def migrate():
            for key, en_name in NAME_MAP:
                en_path = os.path.join(HOME, en_name)
                old_path = state["old"].get(key, "")
                if not old_path or old_path == en_path or not os.path.isdir(old_path):
                    continue
                os.makedirs(en_path, exist_ok=True)
                try:
                    entries = os.listdir(old_path)
                except OSError:
                    entries = []
                for name in entries:
                    try:
                        shutil.move(os.path.join(old_path, name), os.path.join(en_path, name))
                    except OSError as e:
                        state["failed"].append(f"{name}: {e}")
                try:
                    os.rmdir(old_path)
                except OSError:
                    pass
                state["migrated"] += 1
            return True

        def sync():
            Shell.capture_all("xdg-user-dirs-update 2>/dev/null || true")
            return True

        ok = TaskView.run("修补工具 · XDG 目录转英文 / Migrate XDG Dirs", [
            ("安装 xdg-user-dirs", lambda: Shell.pacman("xdg-user-dirs")),
            ("备份并写入英文路径配置 / backup & write config", backup_and_write),
            ("迁移旧目录内容 / migrate contents", migrate),
            ("同步 xdg-user-dirs / sync", sync),
        ])
        if ok:
            msg = f"✅ XDG 已转英文名（迁移 {state['migrated']} 个目录）/ migrated {state['migrated']}"
            if state["bak"]:
                msg += f" · 备份 backup: {os.path.basename(state['bak'])}"
            if state["failed"]:
                msg += f" · ⚠️ {len(state['failed'])} 个文件移动失败 / some moves failed"
            Status.set(msg)
        else:
            Status.set("❌ XDG 目录迁移失败 / migration failed")
        return ok

    # ── Fcitx5 环境变量 ──
    @classmethod
    def fcitx(cls):
        conf_dir = os.path.join(HOME, ".config/environment.d")
        conf = os.path.join(conf_dir, "fcitx.conf")

        def write_conf():
            if os.path.isfile(conf):
                shutil.copyfile(conf, conf + ".bak." + str(int(time.time())))
            os.makedirs(conf_dir, exist_ok=True)
            Shell.write_file(conf,
                             "# Fcitx5 input method environment variables\n"
                             "XMODIFIERS=@im=fcitx5\n"
                             "#GTK_IM_MODULE=fcitx5\n"
                             "QT_IM_MODULE=fcitx5\n"
                             "SDL_IM_MODULE=fcitx5\n")
            return True

        ok = TaskView.run("修补工具 · Fcitx5 输入法环境变量 / Fcitx5 IM Env", [
            (f"写入 {conf}", write_conf),
        ])
        Status.set("✅ Fcitx5 环境变量已配置，重新登录后生效 / re-login to apply" if ok
                   else "❌ Fcitx5 环境变量写入失败 / failed")
        return ok

    # ── 卸除 LightDM ──
    LIGHTDM_PKGS = ("lightdm", "lightdm-gtk-greeter", "lightdm-webkit2-greeter")
    LIGHTDM_DIRS = ("/usr/share/lightdm-webkit", "/usr/local/share/lightdm-webkit",
                    "/etc/lightdm")

    @classmethod
    def remove_lightdm(cls):
        """把 LightDM 整套清掉（包 / 服务 / 配置 / WebKit 主题目录）。

        前提是“装完并配好 greetd”：没启用就顺手启用；连 greetd 都没装、
        或者还没写过 ReGreet 配置，就报错提示先去「登录管理器」。
        这样不会出现「要删先启用 greetd、启用又得先停 lightdm」的死结。
        删主题目录之前先把背景图留在 /etc/greetd/background.png。
        """
        def prepare_greetd():
            if Shell.ok("systemctl is-enabled greetd"):
                return True
            if not Shell.installed("greetd"):
                return False, "greetd 没装，先跑「登录管理器 → 安装」/ install greetd first"
            if not Shell.ok(f"grep -q regreet {GREETD_CONF}"):
                return False, "还没配置 ReGreet，先跑「登录管理器 → 配置并启用」/ configure ReGreet first"
            # 装好了也配好了，只是没启用：这步直接帮它启用
            # （内部会先停用 lightdm，让出 display-manager.service）
            return enable_greetd()

        def disable():
            Shell.sudo("systemctl disable lightdm")   # 不存在也无所谓
            return True

        def uninstall():
            pkgs = [p for p in cls.LIGHTDM_PKGS if Shell.installed(p)]
            if not pkgs:
                return True
            ok, out = Shell.pacman(" ".join(pkgs), "-Rns --noconfirm")
            return ok, Shell.brief(out)

        def cleanup():
            for path in cls.LIGHTDM_DIRS:
                Shell.sudo(f"rm -rf {path}")
            return True

        def verify():
            left = [p for p in cls.LIGHTDM_PKGS if Shell.installed(p)]
            if left:
                return False, "仍安装着 " + ", ".join(left)
            if Shell.ok("systemctl is-enabled lightdm"):
                return False, "lightdm 仍设为开机启动 / still enabled"
            return True

        ok = TaskView.run("修补工具 · 卸除 LightDM / Remove LightDM", [
            ("确认/启用 greetd / ensure greetd enabled", prepare_greetd),
            ("保留登录背景图 / keep greeter background", ensure_background),
            ("停用 lightdm 服务 / disable service", disable),
            ("卸载 lightdm 相关包 / remove packages", uninstall),
            ("清理主题与配置目录 / clean up dirs", cleanup),
            ("校验 / verify", verify),
        ])
        Status.set("✅ LightDM 已卸除，开机直接用 greetd / removed" if ok
                   else "❌ 卸除未完成，greetd 需先可用 / not removed")
        return ok
