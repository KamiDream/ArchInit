"""分类：KVM 安装 / KVM Install。"""
from ..shell import Shell
from ..status import Status
from ..taskview import TaskView


class KvmSteps:
    @classmethod
    def install(cls):
        def start_network():
            ok, out = Shell.sudo("virsh net-start default")
            # 网络已在运行时也会返回非 0，这里视为正常
            return True if "already" in out.lower() else (ok, Shell.brief(out))

        def autostart_network():
            ok, out = Shell.sudo("virsh net-autostart default")
            return ok, Shell.brief(out)

        def add_group():
            rc, out = Shell.capture_all('sudo -n usermod -a -G libvirt "$(whoami)"')
            return rc == 0, Shell.brief(out)

        ok = TaskView.run("KVM 安装 · 虚拟化 / Virtualization", [
            ("安装 qemu-full / virt-manager / swtpm / dnsmasq",
             lambda: Shell.pacman("qemu-full virt-manager swtpm dnsmasq")),
            ("启用并启动 libvirtd / enable libvirtd",
             lambda: Shell.sudo("systemctl enable --now libvirtd")),
            ("启动默认虚拟网络 / start default network", start_network),
            ("设置虚拟网络自启 / net-autostart", autostart_network),
            ("将当前用户加入 libvirt 组 / add user to libvirt", add_group),
        ])
        Status.set("✅ KVM 已安装（重新登录后组权限生效）/ installed — re-login for group" if ok
                   else "❌ KVM 安装失败 / failed")
        return ok
