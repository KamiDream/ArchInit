"""分类：显卡驱动安装 / GPU Drivers。"""
from ..shell import Shell
from ..status import Status
from ..taskview import TaskView


class GpuSteps:
    @classmethod
    def nvidia(cls):
        headers = []

        def detect():
            if Shell.installed("linux"):
                headers.append("linux-headers")
            if Shell.installed("linux-zen"):
                headers.append("linux-zen-headers")
            if not headers:
                return False, "未检测到 linux/linux-zen 内核 / no supported kernel"
            return True

        def install_headers():
            return Shell.pacman(" ".join(headers))

        def set_modules():
            cmd = "sed -i 's/^MODULES=()/MODULES=(nvidia nvidia_modeset nvidia_uvm nvidia_drm)/' /etc/mkinitcpio.conf"
            ok1, out1 = Shell.sudo(cmd)
            ok2, out2 = Shell.sudo(
                "sed -i 's/^#MODULES=()/MODULES=(nvidia nvidia_modeset nvidia_uvm nvidia_drm)/' "
                "/etc/mkinitcpio.conf")
            return (ok1 and ok2), Shell.brief(out1 + out2)

        def drop_kms():
            hooks = Shell.capture("grep '^HOOKS=' /etc/mkinitcpio.conf")
            if not hooks or "kms" not in hooks:
                return True
            return Shell.sudo("sed -i '/^HOOKS=/ s/ *kms *//' /etc/mkinitcpio.conf")

        ok = TaskView.run("显卡驱动 · NVIDIA / NVIDIA Graphics Driver", [
            ("检测已安装内核 / detect kernels", detect),
            ("安装内核头文件 / install kernel headers", install_headers),
            ("安装 nvidia-dkms / utils / settings",
             lambda: Shell.pacman("nvidia-dkms nvidia-utils nvidia-settings")),
            ("写入 MODULES=(nvidia …)", set_modules),
            ("从 HOOKS 移除 kms / drop kms", drop_kms),
            ("重新生成 initramfs / mkinitcpio -P", lambda: Shell.sudo("mkinitcpio -P")),
        ])
        Status.set("✅ NVIDIA 驱动已安装，重启后生效 / installed — reboot to apply" if ok
                   else "❌ NVIDIA 驱动安装失败 / install failed")
        return ok

    @classmethod
    def intel(cls):
        ok = TaskView.run("显卡驱动 · Intel 核显 / Intel Integrated Graphics", [
            ("安装 mesa / vulkan-intel / intel-media-driver / mesa-utils",
             lambda: Shell.pacman("mesa vulkan-intel intel-media-driver mesa-utils")),
        ])
        Status.set("✅ Intel 核显驱动已就绪（已装的包自动跳过）/ ready — installed packages skipped" if ok
                   else "❌ Intel 核显驱动安装失败 / install failed")
        return ok

    @classmethod
    def amd(cls):
        ok = TaskView.run("显卡驱动 · AMD 核显 / AMD Integrated Graphics", [
            ("安装 mesa / vulkan-radeon / libva-mesa-driver / mesa-utils",
             lambda: Shell.pacman("mesa vulkan-radeon libva-mesa-driver mesa-utils")),
        ])
        Status.set("✅ AMD 核显驱动已就绪（已装的包自动跳过）/ ready — installed packages skipped" if ok
                   else "❌ AMD 核显驱动安装失败 / install failed")
        return ok
