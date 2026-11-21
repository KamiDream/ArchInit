"""分类：桌面安装 / Desktop Install。"""
from ..shell import Shell
from ..status import Status
from ..taskview import TaskView


class DesktopSteps:
    @classmethod
    def register_dms(cls):
        def install():
            # 官方脚本需要真实 tty（会自己开 /dev/tty，且可能交互），
            # 所以放到独立 pty 里跑，并把键盘/输出转发过来
            with TaskView.terminal():
                ok = Shell.run_in_tty("curl -fsSL https://install.danklinux.com | sh")
            return ok, "安装脚本未成功完成 / installer did not finish"

        ok = TaskView.run("桌面安装 · 注册 DMS 服务 / Register DMS", [
            ("运行 DMS 安装脚本（会临时回到终端）/ run DMS installer", install),
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
