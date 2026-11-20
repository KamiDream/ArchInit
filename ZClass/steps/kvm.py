"""分类：KVM 安装 / KVM Install。"""
from ..shell import Shell


class KvmSteps:
    @staticmethod
    def install():
        print(">>> Installing KVM packages...")
        Shell.run("sudo pacman -S --needed --noconfirm qemu-full virt-manager swtpm dnsmasq")
        print(">>> Enabling and starting libvirtd service...")
        Shell.run("sudo systemctl enable --now libvirtd")
        print(">>> Starting default virtual network...")
        Shell.run("sudo virsh net-start default 2>/dev/null || true")
        Shell.run("sudo virsh net-autostart default")
        print(">>> Adding current user to libvirt group...")
        Shell.run('sudo usermod -a -G libvirt "$(whoami)"')
        print("    Note: re-login is required for group changes to take effect.")
        return True
