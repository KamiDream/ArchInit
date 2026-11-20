"""分类：显卡驱动安装 / GPU Drivers。"""
from ..shell import Shell
from ..style import Style


class GpuSteps:
    @staticmethod
    def nvidia():
        print(">>> Installing kernel headers (detecting installed kernels)...")
        headers = []
        if Shell.installed("linux"):
            headers.append("linux-headers")
            print("    linux kernel detected -> linux-headers")
        if Shell.installed("linux-zen"):
            headers.append("linux-zen-headers")
            print("    linux-zen kernel detected -> linux-zen-headers")
        if not headers:
            print(Style.yellow("    ⚠️  No supported kernel found (linux/linux-zen). "
                               "This step requires at least one kernel installed. Aborting."))
            return False
        Shell.run("sudo pacman -S --needed --noconfirm " + " ".join(headers))
        print(">>> Installing NVIDIA drivers...")
        Shell.run("sudo pacman -S --needed --noconfirm nvidia-dkms nvidia-utils nvidia-settings")
        print()
        print(">>> Adding nvidia modules to /etc/mkinitcpio.conf...")
        Shell.run("sudo sed -i 's/^MODULES=()/MODULES=(nvidia nvidia_modeset nvidia_uvm nvidia_drm)/' /etc/mkinitcpio.conf")
        Shell.run("sudo sed -i 's/^#MODULES=()/MODULES=(nvidia nvidia_modeset nvidia_uvm nvidia_drm)/' /etc/mkinitcpio.conf")
        print("    MODULES=(nvidia nvidia_modeset nvidia_uvm nvidia_drm) set.")
        hooks = Shell.capture("grep '^HOOKS=' /etc/mkinitcpio.conf")
        if hooks and "kms" in hooks:
            print("    Found kms in HOOKS, removing it (conflicts with NVIDIA proprietary driver)...")
            Shell.run("sudo sed -i '/^HOOKS=/ s/ *kms *//' /etc/mkinitcpio.conf")
            print("    kms removed from HOOKS.")
        else:
            print("    kms not found in HOOKS, no change needed.")
        print(">>> Regenerating initramfs...")
        Shell.run("sudo mkinitcpio -P")
        return True

    @staticmethod
    def intel():
        print(">>> Installing Intel integrated graphics drivers...")
        Shell.run("sudo pacman -S --needed --noconfirm mesa vulkan-intel intel-media-driver mesa-utils")
        print("    (mesa: OpenGL/Vulkan 驱动基础; vulkan-intel: Intel Vulkan 驱动;")
        print("     intel-media-driver: 硬件视频编解码; mesa-utils: glxinfo 等诊断工具)")
        print("    --needed 已启用：已安装的包会自动跳过 / --needed skips already-installed packages.")
        return True

    @staticmethod
    def amd():
        print(">>> Installing AMD integrated graphics drivers...")
        Shell.run("sudo pacman -S --needed --noconfirm mesa vulkan-radeon libva-mesa-driver mesa-utils")
        print("    (mesa: OpenGL/Vulkan 驱动基础; vulkan-radeon: AMD Vulkan 驱动(RADV);")
        print("     libva-mesa-driver: VA-API 硬件视频解码; mesa-utils: glxinfo 等诊断工具)")
        print("    --needed 已启用：已安装的包会自动跳过 / --needed skips already-installed packages.")
        return True
