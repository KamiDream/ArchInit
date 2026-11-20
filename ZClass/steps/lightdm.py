"""分类：LightDM 配置 / LightDM WebKit2 Greeter。"""
import os
import shutil

from ..config import HOME
from ..shell import Shell
from ..style import Style


class LightDmSteps:
    @staticmethod
    def greeter():
        print(">>> 安装 lightdm-webkit2-greeter...")
        print("    Installing lightdm-webkit2-greeter...")
        Shell.run("sudo pacman -S --needed --noconfirm lightdm-webkit2-greeter")
        print()
        print(Style.green_bold("    ✅ lightdm-webkit2-greeter 安装完成 / installed successfully."))
        return True

    @staticmethod
    def theme():
        print(">>> 清理旧主题（如果存在）...")
        print("    Cleaning up old theme (if exists)...")
        target = "/usr/share/lightdm-webkit/themes/KamiDream_Theme"
        if os.path.isdir(target):
            Shell.run(f"sudo rm -rf {target}")
            print("    ✅ 旧主题已删除 / Old theme removed.")
        else:
            print("    ⏭️  未发现旧主题，跳过 / No old theme found, skipping.")
        print()
        print(">>> 克隆 KamiDream LightDM WebKit2 主题...")
        print("    Cloning KamiDream LightDM WebKit2 theme...")
        theme_dir = os.path.join(HOME, "LdmWk2Theme")
        if os.path.isdir(theme_dir):
            shutil.rmtree(theme_dir, ignore_errors=True)
        Shell.run(f'git clone https://github.com/KamiDream/LdmWk2Theme.git "{theme_dir}"')
        print()
        print(">>> 创建目标目录并移动主题...")
        print("    Creating target directory and moving theme...")
        Shell.run("sudo mkdir -p /usr/share/lightdm-webkit/themes/")
        Shell.run(f'sudo mv "{theme_dir}" {target}')
        print()
        print(Style.green_bold(f"    ✅ KamiDream 主题已安装/更新到 {target}"))
        print("    Theme installed/updated successfully.")
        print()
        print("    🖼️  如需替换背景图片，请替换以下文件：")
        print("       /usr/share/lightdm-webkit/themes/KamiDream_Theme/assets/background.png")
        print("       To replace the background image, replace the file above with your own.")
        return True

    @staticmethod
    def enable():
        print(">>> 配置 /etc/lightdm/lightdm.conf...")
        print("    Configuring /etc/lightdm/lightdm.conf...")
        Shell.run("sudo mkdir -p /etc/lightdm")
        conf = "/etc/lightdm/lightdm.conf"
        if Shell.read_file(conf).find("[Seat:*]") >= 0 or Shell.ok(f"grep -q '^\\[Seat:\\*\\]' {conf} 2>/dev/null"):
            if Shell.ok(f"grep -q '^greeter-session=' {conf}"):
                Shell.run(f"sudo sed -i 's/^greeter-session=.*/greeter-session=lightdm-webkit2-greeter/' {conf}")
            else:
                Shell.run(f"sudo sed -i '/^\\[Seat:\\*\\]/a greeter-session=lightdm-webkit2-greeter' {conf}")
        else:
            Shell.sudo_write(conf, "[Seat:*]\ngreeter-session=lightdm-webkit2-greeter\n", append=True)
        print("    /etc/lightdm/lightdm.conf 已配置 / configured.")
        print()
        print(">>> 配置 /etc/lightdm/lightdm-webkit2-greeter.conf...")
        print("    Configuring /etc/lightdm/lightdm-webkit2-greeter.conf...")
        wconf = "/etc/lightdm/lightdm-webkit2-greeter.conf"
        if Shell.ok(f"grep -q '^webkit_theme' {wconf} 2>/dev/null"):
            Shell.run(f"sudo sed -i 's/^webkit_theme\\s*=.*/webkit_theme        = KamiDream_Theme/' {wconf}")
            print("    webkit_theme 已更新为 KamiDream_Theme / updated.")
        else:
            Shell.sudo_write(wconf, "[greeter]\nwebkit_theme        = KamiDream_Theme\n", append=True)
            print("    webkit_theme 已添加 / added.")
        print("    /etc/lightdm/lightdm-webkit2-greeter.conf 已配置 / configured.")
        print()
        print(Style.green_bold("    ✅ LightDM 配置完成 / Configuration complete."))
        print()
        print("=" * 121)
        print(Style.yellow("   ⚠️  请重启系统以应用 LightDM 登录管理器 / Please reboot to apply LightDM"))
        print("     重启命令 / Reboot command: sudo reboot")
        print("     或 / Or: sudo systemctl reboot")
        print("=" * 121)
        print()
        return Shell.prompt("按 Enter 继续 / Press Enter to continue")

    @staticmethod
    def emergency():
        print(">>> 注释 /etc/lightdm/lightdm.conf 中的 greeter-session=lightdm-webkit2-greeter...")
        print("    Commenting out greeter-session=lightdm-webkit2-greeter in /etc/lightdm/lightdm.conf...")
        conf = "/etc/lightdm/lightdm.conf"
        if Shell.ok(f"grep -q '^greeter-session=lightdm-webkit2-greeter' {conf} 2>/dev/null"):
            Shell.run(f"sudo sed -i 's/^greeter-session=lightdm-webkit2-greeter/#greeter-session=lightdm-webkit2-greeter/' {conf}")
            print(Style.green_bold("    ✅ 已注释 greeter-session 行 / Commented out."))
        else:
            print(Style.yellow("    ⏭️  未找到 greeter-session=lightdm-webkit2-greeter，可能已被注释 / Not found, may already be commented."))
        print()
        print("=" * 121)
        print(Style.yellow("   ⚠️  请重启系统以恢复默认 LightDM Greeter / Please reboot to restore default LightDM greeter"))
        print("     重启命令 / Reboot command: sudo reboot")
        print("     或 / Or: sudo systemctl reboot")
        print("=" * 121)
        print()
        return Shell.prompt("按 Enter 继续 / Press Enter to continue")
