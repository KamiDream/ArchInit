"""分类：修补工具 / Patch Tools。"""
import os
import shutil
import time

from ..config import HOME
from ..shell import Shell
from ..style import Style


class PatchSteps:
    @staticmethod
    def uu():
        print(">>> Installing UU Accelerator...")
        print("    This will:")
        print("      • Create /home/deck directory")
        print("      • Set ownership to current user")
        print("      • Download and run UU install script from uudeck.com")
        print()
        if Shell.prompt("Press Enter to start installation"):
            print(">>> Creating /home/deck...")
            Shell.run("sudo mkdir /home/deck")
            Shell.run('sudo chown "$(whoami)" /home/deck')
            print(">>> Downloading and running UU install script...")
            Shell.run("curl -s uudeck.com | sudo bash")
            print()
            return True
        return False

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
        print(">>> 安装 xdg-user-dirs（如未安装）/ Installing xdg-user-dirs (if not present)...")
        Shell.run("sudo pacman -S --needed --noconfirm xdg-user-dirs")

        conf = os.path.join(HOME, ".config/user-dirs.dirs")
        bak = conf + ".bak." + str(int(time.time()))
        old = {}
        if os.path.isfile(conf):
            shutil.copyfile(conf, bak)
            print(f"    原配置已备份到 / Old config backed up to: {bak}")
            old = cls._parse_xdg_dirs(bak)
        else:
            print("    未发现现有配置，将创建全新配置 / No existing config found, creating fresh config.")

        print()
        print(">>> 直接写入英文路径配置文件...")
        print("    Writing config file with English paths directly...")
        Shell.write_file(conf,
                         "# This file is written by ArchInit (archinit.py)\n"
                         "# XDG user directories with English names\n"
                         "# System locale remains Chinese (zh_CN.UTF-8)\n"
                         "#\n"
                         'XDG_DESKTOP_DIR="$HOME/Desktop"\n'
                         'XDG_DOWNLOAD_DIR="$HOME/Downloads"\n'
                         'XDG_TEMPLATES_DIR="$HOME/Templates"\n'
                         'XDG_PUBLICSHARE_DIR="$HOME/Public"\n'
                         'XDG_DOCUMENTS_DIR="$HOME/Documents"\n'
                         'XDG_MUSIC_DIR="$HOME/Music"\n'
                         'XDG_PICTURES_DIR="$HOME/Pictures"\n'
                         'XDG_VIDEOS_DIR="$HOME/Videos"\n'
                         'XDG_PROJECTS_DIR="$HOME/Projects"\n')
        print(f"    ✅ 配置文件已写入 / Config written: {conf}")

        print()
        print(">>> 迁移目录内容...")
        print("    Migrating directory contents...")
        mapping = [
            ("XDG_DESKTOP_DIR", "Desktop"),
            ("XDG_DOWNLOAD_DIR", "Downloads"),
            ("XDG_TEMPLATES_DIR", "Templates"),
            ("XDG_PUBLICSHARE_DIR", "Public"),
            ("XDG_DOCUMENTS_DIR", "Documents"),
            ("XDG_MUSIC_DIR", "Music"),
            ("XDG_PICTURES_DIR", "Pictures"),
            ("XDG_VIDEOS_DIR", "Videos"),
            ("XDG_PROJECTS_DIR", "Projects"),
        ]
        migrated = 0
        for key, en_name in mapping:
            en_path = os.path.join(HOME, en_name)
            old_path = old.get(key, "")
            if not old_path or old_path == en_path:
                continue
            if not os.path.isdir(old_path):
                continue
            print()
            print(f"  发现旧目录 / Found old dir: {old_path}")
            print(f"  目标目录 / Target dir: {en_path}")
            os.makedirs(en_path, exist_ok=True)
            entries = []
            try:
                entries = os.listdir(old_path)
            except OSError:
                entries = []
            if entries:
                print("    迁移内容中 / Migrating contents...")
                for name in entries:
                    try:
                        shutil.move(os.path.join(old_path, name), os.path.join(en_path, name))
                    except OSError as e:
                        print(Style.yellow(f"    ⚠️  移动失败 / Failed to move {name}: {e}"))
                print("    ✅ 内容已迁移 / Contents migrated.")
            else:
                print("    目录为空，无需迁移 / Directory empty, no migration needed.")
            try:
                os.rmdir(old_path)
                print(f"    ✅ 旧目录已删除 / Old directory removed: {old_path}")
            except OSError:
                print(f"    ⚠️  旧目录未能删除（可能仍有内容）/ Old dir not removed: {old_path}")
            migrated += 1

        if migrated == 0:
            print("    无需迁移，目录名未改变 / No migration needed — directory names unchanged.")
        else:
            print()
            print(f"    ✅ 共迁移 {migrated} 个目录 / Total {migrated} directories migrated.")

        print()
        print(">>> 同步 xdg-user-dirs（保留已有配置）...")
        print("    Syncing xdg-user-dirs (preserving existing config)...")
        Shell.run("xdg-user-dirs-update 2>/dev/null || true")
        print("    ✅ 同步完成 / Sync done.")
        print()
        print("    ✅ XDG 用户目录已切换为英文名 / XDG user dirs migrated to English names.")
        print("    系统 locale 仍为中文（zh_CN.UTF-8），不受影响。")
        print("    System locale remains Chinese (zh_CN.UTF-8); unaffected.")
        print()
        print("    请重新登录后检查效果。备份文件可手动删除：")
        print("    Re-login to verify. Backup can be removed manually:")
        print(f'      rm "{bak}"')
        return True

    @staticmethod
    def fcitx():
        conf_dir = os.path.join(HOME, ".config/environment.d")
        conf = os.path.join(conf_dir, "fcitx.conf")
        print(">>> 写入 Fcitx5 输入法环境变量...")
        print("    Writing Fcitx5 input method environment variables...")
        print(f"    目标文件 / Target file: {conf}")
        print()
        if os.path.isfile(conf):
            shutil.copyfile(conf, conf + ".bak." + str(int(time.time())))
            print(f"    原配置已备份 / Old config backed up: {conf}.bak.*")
        os.makedirs(conf_dir, exist_ok=True)
        Shell.write_file(conf,
                         "# Fcitx5 input method environment variables\n"
                         "XMODIFIERS=@im=fcitx5\n"
                         "#GTK_IM_MODULE=fcitx5\n"
                         "QT_IM_MODULE=fcitx5\n"
                         "SDL_IM_MODULE=fcitx5\n")
        print(f"    ✅ 配置文件已写入 / Config written: {conf}")
        print()
        print("    ✅ Fcitx5 环境变量已配置 / Fcitx5 environment variables configured.")
        print("    重新登录后生效（environment.d 由 systemd 用户会话加载）。")
        print("    Re-login to take effect (environment.d is loaded by systemd user session).")
        return True
