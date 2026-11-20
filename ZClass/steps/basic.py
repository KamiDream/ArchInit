"""分类：基础初始化 / Basic Initialization。"""
import os
import shutil

from ..config import HOME, ROOT_DIR
from ..shell import Shell
from ..style import Style


class BasicSteps:
    @staticmethod
    def core():
        print(">>> Installing core desktop packages...")
        Shell.run("sudo pacman -S --needed --noconfirm kimageformats power-profiles-daemon cava")
        return True

    @staticmethod
    def extensions():
        print(">>> Installing base packages...")
        Shell.run("sudo pacman -S --needed --noconfirm fastfetch fcitx5-im fcitx5-rime fuse2 vim firefox "
                  "pcmanfm-qt udisks2")
        print(">>> Setting pcmanfm-qt as default file manager...")
        Shell.run("xdg-mime default pcmanfm-qt.desktop inode/directory 2>/dev/null || true")
        print("    pcmanfm-qt set as default for inode/directory.")

        print()
        print(">>> Installing xarchiver (archive extraction tool) + 7zip backend...")
        Shell.run("sudo pacman -S --needed --noconfirm xarchiver 7zip")
        print("    (Double-clicking an archive in pcmanfm-qt does nothing without this.)")

        print()
        print(">>> NTFS 工具说明 / NTFS tools note...")
        print("    NTFS 修复与恢复工具集由 ntfsprogs-plus 提供（基础初始化的 NTFS 步骤）。")
        print("    注意：ntfsprogs-plus 与 ntfs-3g 冲突，二者只装其一。")
        print("    Usage: sudo ntfsfix -d /dev/sdXN")

        print()
        print(">>> [Root Cause 2: missing auto-mount daemon]")
        print("    pcmanfm-qt's [Volume] MountRemovable=true relies on the LXQt session")
        print("    (lxqt-session + pcmanfm-qt desktop mode), which is inactive under niri.")
        print("    Installing udiskie as a lightweight auto-mounter...")
        Shell.run("sudo pacman -S --needed --noconfirm udiskie gvfs")
        print("    (gvfs provides the GIO virtual filesystem mounts — trash, network, MTP, etc.)")
        print("    Enabling udiskie as a systemd user service (WM-independent)...")
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
        Shell.run("systemctl --user daemon-reload")
        Shell.run("systemctl --user enable --now udiskie.service")
        Shell.run("systemctl --user status udiskie --no-pager || true")
        print("    udiskie auto-mount daemon enabled.")

        print()
        print(">>> Uncommenting zh_CN.UTF-8 in /etc/locale.gen...")
        Shell.run("sudo sed -i 's/^#zh_CN.UTF-8/zh_CN.UTF-8/' /etc/locale.gen")
        print("    zh_CN.UTF-8 enabled.")

        print(">>> Generating locale...")
        Shell.run("sudo locale-gen")
        print(">>> Setting system locale to zh_CN.UTF-8...")
        Shell.run("sudo localectl set-locale LANG=zh_CN.UTF-8")

        print(">>> Installing Chinese fonts & Nerd fonts...")
        Shell.run("sudo pacman -S --needed --noconfirm wqy-microhei wqy-microhei-lite wqy-bitmapfont "
                  "wqy-zenhei ttf-arphic-ukai ttf-arphic-uming noto-fonts-cjk ttf-jetbrains-mono-nerd "
                  "noto-fonts-emoji ttf-fira-code inter-font")

        print()
        print(">>> Configuring XDG user directories with English names...")
        Shell.run("sudo pacman -S --needed --noconfirm xdg-user-dirs")
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
        for d in ["Desktop", "Downloads", "Templates", "Public", "Documents",
                  "Music", "Pictures", "Videos", "Projects"]:
            os.makedirs(os.path.join(HOME, d), exist_ok=True)
        Shell.run("xdg-user-dirs-update 2>/dev/null || true")
        print("    XDG user directories configured with English names.")
        print("    (Desktop, Downloads, Documents, Pictures, Music, Videos, Public, Templates, Projects)")
        return True

    @staticmethod
    def kitty_font():
        print(">>> Running Kitty font selector, choose JetBrains Mono...")
        if Shell.prompt("Press Enter to launch font selector"):
            Shell.run("kitten choose-fonts")
            Shell.run("stty sane 2>/dev/null || true")
            Shell.prompt("Font selected. Press Enter to continue")
            return True
        return False

    @staticmethod
    def aur():
        print(">>> Configuring /etc/pacman.conf...")
        Shell.run("sudo sed -i '/^#\\[multilib\\]/,/^#Include/ s/^#//' /etc/pacman.conf")
        print("    [multilib] enabled.")
        if not Shell.ok("grep -q '^\\[archlinuxcn\\]' /etc/pacman.conf"):
            Shell.sudo_write("/etc/pacman.conf",
                             "\n[archlinuxcn]\n"
                             "Server = https://mirrors.ustc.edu.cn/archlinuxcn/$arch\n"
                             "Server = https://mirrors.tuna.tsinghua.edu.cn/archlinuxcn/$arch\n"
                             "Server = https://mirrors.hit.edu.cn/archlinuxcn/$arch\n"
                             "Server = https://repo.huaweicloud.com/archlinuxcn/$arch\n",
                             append=True)
            print("    [archlinuxcn] repository added.")
        else:
            print("    [archlinuxcn] already present, skipping.")
        print(">>> Installing archlinuxcn-keyring and updating system...")
        Shell.run("sudo pacman -Sy --needed --noconfirm archlinuxcn-keyring")
        Shell.run("sudo pacman -S --needed --noconfirm base-devel yay paru flclash")
        Shell.run("sudo pacman -Syu --noconfirm")
        return True

    @staticmethod
    def ntfs():
        print(">>> 安装 ntfsprogs-plus（增强版 NTFS 修复/恢复工具）...")
        if Shell.which("yay"):
            Shell.run("yay -S --noconfirm ntfsprogs-plus")
        elif Shell.which("paru"):
            Shell.run("paru -S --noconfirm ntfsprogs-plus")
        else:
            print(Style.yellow("    ⚠️ 未检测到 AUR 助手（yay/paru）。请先执行「AUR 助手」步骤。"))
            return False
        print("    ntfsprogs-plus 提供 ntfsfix 增强、ntfsundelete、ntfsdump 等工具。")
        return True

    @staticmethod
    def rime():
        print(">>> 安装雾凇拼音 / Installing Rime-ice input method...")
        Shell.run("yay -S --noconfirm rime-ice-pinyin-git")
        print("    rime-ice-pinyin-git 安装完成 / installed.")
        print()
        print(">>> 复制 Fcitx5 雾凇拼音配置 / Copying Fcitx5 Rime-ice config...")
        os.makedirs(os.path.join(HOME, ".local/share/fcitx5/rime"), exist_ok=True)
        src = os.path.join(ROOT_DIR, "fcitx5/default.custom.yaml")
        dst = os.path.join(HOME, ".local/share/fcitx5/rime/default.custom.yaml")
        if os.path.isfile(src):
            shutil.copyfile(src, dst)
            print("    配置已复制到 ~/.local/share/fcitx5/rime/default.custom.yaml")
            print("    Config copied successfully.")
        else:
            print("    Warning: fcitx5/default.custom.yaml not found, skipping.")
        print()
        print("    请重新登录或重启 Fcitx5 以加载雾凇拼音")
        print("    如果词库未生效，可尝试在 Fcitx5 中重新部署（右键托盘图标 → 重新部署）")
        print("    Log out and back in, or restart Fcitx5 to load Rime-ice.")
        print("    If the schema does not appear, try re-deploying from Fcitx5 tray.")
        return True

    @staticmethod
    def keyring():
        print(">>> 安装密钥库 / Installing keyring packages...")
        Shell.run("sudo pacman -S --needed --noconfirm gnome-keyring libsecret seahorse")
        print("    gnome-keyring libsecret seahorse 安装完成 / installed.")
        print()
        print(">>> 查看 gnome-keyring-daemon 服务状态 / Checking gnome-keyring-daemon service status...")
        Shell.run("systemctl --user status gnome-keyring-daemon.service --no-pager || true")
        print()
        print("    提示：如服务未运行，重新登录后 systemd 用户会话会自动启动 gnome-keyring-daemon")
        print("    Tip: if the service is not running, re-login so the systemd user session starts it automatically.")
        return True
