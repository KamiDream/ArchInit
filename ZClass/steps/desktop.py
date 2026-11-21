"""分类：桌面安装 / Desktop Install。"""
from ..shell import Shell
from ..status import Status
from ..taskview import TaskView


class DesktopSteps:
    @classmethod
    def register_dms(cls):
        def install():
            ok, out = Shell.quiet("curl -fsSL https://install.danklinux.com | sh")
            return ok, Shell.brief(out)

        ok = TaskView.run("桌面安装 · 注册 DMS 服务 / Register DMS", [
            ("运行 DMS 安装脚本 / run DMS installer", install),
        ])
        Status.set("✅ DMS 服务已注册 / DMS registered" if ok
                   else "❌ DMS 注册失败 / registration failed")
        return ok

    @classmethod
    def lightdm(cls):
        def enable():
            ok, out = Shell.sudo("systemctl enable lightdm")
            return ok, Shell.brief(out)

        def start():
            ok, out = Shell.sudo("systemctl start lightdm")
            return ok, Shell.brief(out)

        ok = TaskView.run("桌面安装 · LightDM / Display Manager", [
            ("安装 lightdm + lightdm-gtk-greeter",
             lambda: Shell.pacman("lightdm lightdm-gtk-greeter")),
            ("启用 lightdm 开机自启 / enable lightdm", enable),
            ("启动 lightdm / start lightdm", start),
        ])
        Status.set("✅ LightDM 已安装并启动 / installed & started" if ok
                   else "❌ LightDM 配置失败 / failed")
        return ok
