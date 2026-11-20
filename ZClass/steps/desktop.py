"""分类：桌面安装 / Desktop Install。"""
from ..shell import Shell


class DesktopSteps:
    @staticmethod
    def register_dms():
        print(">>> Registering DMS as a user service dependency of Niri...")
        Shell.run("curl -fsSL https://install.danklinux.com | sh")
        return True

    @staticmethod
    def lightdm():
        print(">>> Installing LightDM and greeter...")
        Shell.run("sudo pacman -S --needed --noconfirm lightdm lightdm-gtk-greeter")
        print(">>> Enabling LightDM display manager...")
        Shell.run("sudo systemctl enable lightdm")
        print(">>> Starting LightDM...")
        Shell.run("sudo systemctl start lightdm")
        return True
