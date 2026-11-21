"""分类：桌面安装 / Desktop Install。

本分类按“直接输出到终端”的方式执行（不使用任务面板），
命令的进度与输出都留在终端上，方便看清安装脚本在做什么。
"""
from ..shell import Shell
from ..style import Style


class DesktopSteps:
    @staticmethod
    def register_dms():
        print(">>> Registering DMS as a user service dependency of Niri...")
        print("    Running the official installer (needs a real tty)...")
        ok = Shell.run_in_tty("curl -fsSL https://install.danklinux.com | sh")
        if not ok:
            print(Style.yellow("    ⚠️  安装脚本未成功完成 / the installer did not finish"))
        return ok

    @staticmethod
    def lightdm():
        print(">>> Installing LightDM and greeter...")
        rc = Shell.run("sudo pacman -S --needed --noconfirm lightdm lightdm-gtk-greeter")

        print(">>> Enabling LightDM display manager...")
        rc2 = Shell.run("sudo systemctl enable lightdm")

        print(">>> Starting LightDM...")
        rc3 = Shell.run("sudo systemctl start lightdm")

        if rc != 0 or rc2 != 0 or rc3 != 0:
            print(Style.yellow("    ⚠️  有命令执行失败，请检查上方输出 / some commands failed"))
            return False
        return True
