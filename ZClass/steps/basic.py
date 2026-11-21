"""分类：基础初始化 / Basic Initialization。"""
import os
import shutil

from ..config import HOME, ROOT_DIR
from ..shell import Shell
from ..status import Status
from ..taskview import TaskView


def _aur(pkg):
    """用 yay / paru 安装（静默），返回 (ok, 说明)。"""
    helper = "yay" if Shell.which("yay") else ("paru" if Shell.which("paru") else "")
    if not helper:
        return False, "未检测到 yay/paru / AUR helper missing"
    rc, out = Shell.capture_all(f"{helper} -S --noconfirm {pkg}")
    return rc == 0, Shell.brief(out)


class BasicSteps:
    @classmethod
    def core(cls):
        ok = TaskView.run("基础初始化 · niri 核心组件 / Core Components", [
            ("安装 kimageformats / power-profiles-daemon / cava",
             lambda: Shell.pacman("kimageformats power-profiles-daemon cava")),
        ])
        Status.set("✅ niri 核心组件已安装 / core components installed" if ok
                   else "❌ core 组件安装失败 / install failed")
        return ok

    @classmethod
    def extensions(cls):
        def default_fm():
            rc, out = Shell.capture_all(
                "xdg-mime default pcmanfm-qt.desktop inode/directory 2>/dev/null || true")
            return rc == 0, Shell.brief(out)

        def setup_udiskie():
            ok, out = Shell.pacman("udiskie gvfs")
            if not ok:
                return False, Shell.brief(out)
            os.makedirs(os.path.join(HOME, ".config/systemd/user"), exist_ok=True)
            Shell.write_file(os.path.join(HOME, ".config/systemd/user/udiskie.service"),
                             "[Unit]\n"
                             "Description=udiskie auto-mounter\n"
                             "\n"
                             "[Service]\n"
                             "ExecStart=/usr/bin/udiskie\n"
                             "Restart=on-failure\n"
                             "\n"
                             "[Install]\n"
                             "WantedBy=default.target\n")
            rc1, out1 = Shell.capture_all("systemctl --user daemon-reload")
            rc2, out2 = Shell.capture_all("systemctl --user enable --now udiskie.service")
            return (rc1 == 0 and rc2 == 0), Shell.brief(out1 + out2)

        def set_locale():
            ok, out = Shell.sudo("sed -i 's/^#zh_CN.UTF-8/zh_CN.UTF-8/' /etc/locale.gen")
            if not ok:
                return False, Shell.brief(out)
            ok, out = Shell.sudo("locale-gen")
            if not ok:
                return False, Shell.brief(out)
            return Shell.sudo("localectl set-locale LANG=zh_CN.UTF-8")

        def xdg_dirs():
            ok, out = Shell.pacman("xdg-user-dirs")
            if not ok:
                return False, Shell.brief(out)
            os.makedirs(os.path.join(HOME, ".config"), exist_ok=True)
            Shell.write_file(os.path.join(HOME, ".config/user-dirs.dirs"),
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
            for d in ("Desktop", "Downloads", "Templates", "Public", "Documents",
                      "Music", "Pictures", "Videos", "Projects"):
                os.makedirs(os.path.join(HOME, d), exist_ok=True)
            Shell.capture_all("xdg-user-dirs-update 2>/dev/null || true")
            return True

        ok = TaskView.run("基础初始化 · 系统拓展组件 / System Extensions", [
            ("安装 fastfetch / fcitx5 / fuse2 / vim / firefox / pcmanfm-qt / udisks2",
             lambda: Shell.pacman("fastfetch fcitx5-im fcitx5-rime fuse2 vim firefox "
                                  "pcmanfm-qt udisks2")),
            ("设 pcmanfm-qt 为默认文件管理器 / set default file manager", default_fm),
            ("安装归档工具 xarchiver + 7zip", lambda: Shell.pacman("xarchiver 7zip")),
            ("安装自动挂载 udiskie + gvfs 并启用服务 / auto-mounter", setup_udiskie),
            ("启用中文 locale（zh_CN.UTF-8）/ enable locale", set_locale),
            ("安装中文字体与 Nerd 字体 / CJK + Nerd fonts",
             lambda: Shell.pacman("wqy-microhei wqy-microhei-lite wqy-bitmapfont wqy-zenhei "
                                  "ttf-arphic-ukai ttf-arphic-uming noto-fonts-cjk "
                                  "ttf-jetbrains-mono-nerd noto-fonts-emoji ttf-fira-code "
                                  "inter-font")),
            ("配置 XDG 用户目录为英文名 / English XDG dirs", xdg_dirs),
        ])
        Status.set("✅ 系统拓展组件已就绪 / extensions ready" if ok
                   else "❌ 拓展组件安装失败 / failed")
        return ok

    @classmethod
    def kitty_font(cls):
        def choose_fonts():
            if not Shell.which("kitten"):
                return False, "未找到 kitten，请先安装 kitty / kitten not found"
            with TaskView.terminal():   # kitten 自带全屏界面，需要真实终端
                rc = Shell.run("kitten choose-fonts")
                Shell.run("stty sane 2>/dev/null || true")
            return rc == 0, ""

        ok = TaskView.run("基础初始化 · Kitty 字体 / Kitty Font Selector", [
            ("运行 kitten choose-fonts（选 JetBrains Mono）", choose_fonts),
        ])
        Status.set("✅ Kitty 字体已选择 / font selected" if ok
                   else "❌ 字体选择未完成 / font selection not finished")
        return ok

    @classmethod
    def aur(cls):
        def enable_multilib():
            return Shell.sudo(
                "sed -i '/^#\\[multilib\\]/,/^#Include/ s/^#//' /etc/pacman.conf")

        def add_archlinuxcn():
            if Shell.ok("grep -q '^\\[archlinuxcn\\]' /etc/pacman.conf"):
                return True
            rc, out = Shell.capture_all(
                "sudo -n tee -a /etc/pacman.conf <<'EOF'\n"
                "\n[archlinuxcn]\n"
                "Server = https://mirrors.ustc.edu.cn/archlinuxcn/$arch\n"
                "Server = https://mirrors.tuna.tsinghua.edu.cn/archlinuxcn/$arch\n"
                "Server = https://mirrors.hit.edu.cn/archlinuxcn/$arch\n"
                "Server = https://repo.huaweicloud.com/archlinuxcn/$arch\n"
                "EOF")
            return rc == 0, Shell.brief(out)

        ok = TaskView.run("基础初始化 · AUR 助手 / AUR Helper", [
            ("启用 [multilib] 仓库 / enable multilib", enable_multilib),
            ("添加 [archlinuxcn] 仓库 / add archlinuxcn repo", add_archlinuxcn),
            ("安装 archlinuxcn-keyring",
             lambda: Shell.pacman("archlinuxcn-keyring", "-Sy --needed --noconfirm")),
            ("安装 base-devel / yay / paru / flclash",
             lambda: Shell.pacman("base-devel yay paru flclash")),
            ("系统更新 / system upgrade",
             lambda: Shell.pacman("", "-Syu --noconfirm")),
        ])
        Status.set("✅ AUR 助手已就绪 / AUR helper ready" if ok
                   else "❌ AUR 助手配置失败 / failed")
        return ok

    @classmethod
    def ntfs(cls):
        ok = TaskView.run("基础初始化 · NTFS 增强工具 / NTFS Enhanced Tools", [
            ("安装 ntfsprogs-plus（AUR）", lambda: _aur("ntfsprogs-plus")),
        ])
        Status.set("✅ ntfsprogs-plus 已安装（ntfsfix/ntfsundelete/ntfsdump）" if ok
                   else "❌ 安装失败，请先完成 AUR 助手步骤 / failed — run AUR step first")
        return ok

    @classmethod
    def rime(cls):
        def copy_config():
            os.makedirs(os.path.join(HOME, ".local/share/fcitx5/rime"), exist_ok=True)
            src = os.path.join(ROOT_DIR, "fcitx5/default.custom.yaml")
            if not os.path.isfile(src):
                return False, "缺少 fcitx5/default.custom.yaml / config missing"
            shutil.copyfile(src, os.path.join(HOME, ".local/share/fcitx5/rime/default.custom.yaml"))
            return True

        ok = TaskView.run("基础初始化 · 雾凇拼音 / Rime-ice Input Method", [
            ("安装 rime-ice-pinyin-git（AUR）", lambda: _aur("rime-ice-pinyin-git")),
            ("复制 Fcitx5 雾凇拼音配置 / copy config", copy_config),
        ])
        Status.set("✅ 雾凇拼音已安装，重新登录或部署 Fcitx5 后生效 / re-login to apply" if ok
                   else "❌ 雾凇拼音配置失败 / failed")
        return ok

    @classmethod
    def keyring(cls):
        ok = TaskView.run("基础初始化 · 安装密钥库 / Install Keyring", [
            ("安装 gnome-keyring / libsecret / seahorse",
             lambda: Shell.pacman("gnome-keyring libsecret seahorse")),
        ])
        Status.set("✅ 密钥库已安装，重新登录后 gnome-keyring-daemon 自动启动 / re-login to start"
                   if ok else "❌ 密钥库安装失败 / install failed")
        return ok
