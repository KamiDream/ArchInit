"""分类目录：把各步骤类组装成可交互的分类列表。"""
from .model import Category, Step
from .steps.backend import BackendSteps
from .steps.basic import BasicSteps
from .steps.desktop import DesktopSteps
from .steps.gpu import GpuSteps
from .steps.kvm import KvmSteps
from .steps.lightdm import LightDmSteps
from .steps.patch import PatchSteps
from .steps.terminal import TerminalSteps


class Catalog:
    @staticmethod
    def build():
        return [
            Category("桌面安装 / Desktop Install", [
                Step("注册 DMS 服务 / Register DMS Service", DesktopSteps.register_dms),
                Step("显示管理器 LightDM / Display Manager", DesktopSteps.lightdm),
            ]),
            Category("基础初始化 / Basic Initialization", [
                Step("niri 核心组件 / Niri Core Components", BasicSteps.core),
                Step("系统拓展组件 / System Extensions", BasicSteps.extensions),
                Step("Kitty 字体选择 / Kitty Font Selector", BasicSteps.kitty_font),
                Step("AUR 助手 / AUR Helper (yay / paru)", BasicSteps.aur),
                Step("NTFS 增强工具 / NTFS Enhanced Tools", BasicSteps.ntfs),
                Step("雾凇拼音 / Rime-ice Input Method", BasicSteps.rime),
                Step("安装密钥库 / Install Keyring", BasicSteps.keyring),
            ]),
            Category("KVM 安装 / KVM Install", [
                Step("KVM 虚拟化 / KVM Virtualization", KvmSteps.install),
            ]),
            Category("显卡驱动安装 / GPU Drivers", [
                Step("NVIDIA 显卡驱动 / NVIDIA Graphics Driver", GpuSteps.nvidia),
                Step("Intel 核显驱动 / Intel Integrated Graphics", GpuSteps.intel),
                Step("AMD 核显驱动 / AMD Integrated Graphics", GpuSteps.amd),
            ]),
            Category("终端美化 / Terminal Beautification", [
                Step("启用 Zsh 终端 / Enable Zsh Shell", TerminalSteps.zsh),
                Step("Antidote 插件管理器 / Antidote Plugin Manager", TerminalSteps.antidote),
                Step("Starship 提示符 / Starship Prompt", TerminalSteps.starship),
                Step("fastfetch 配置 / fastfetch Configuration", TerminalSteps.fastfetch_config),
                Step("配置 fastfetch 启动 / Configure fastfetch on startup", TerminalSteps.fastfetch_startup),
                Step("Kitty 背景透明度 / Kitty Background Opacity", TerminalSteps.kitty_opacity),
            ]),
            Category("LightDM 配置 / LightDM WebKit2 Greeter", [
                Step("安装 LightDM WebKit2 Greeter / Install Greeter", LightDmSteps.greeter),
                Step("安装 KamiDream 主题 / Install KamiDream Theme", LightDmSteps.theme),
                Step("启用 LightDM 配置 / Enable LightDM Configuration", LightDmSteps.enable),
                Step("黑屏救急 / Black Screen Emergency Fix", LightDmSteps.emergency),
            ], warning=[
                "⚠️  警告 / WARNING",
                "单 N 卡独显或开启了独显直连的用户（纯 N 卡用户）请勿使用此配置！",
                "Do NOT use this configuration if you have a single/primary NVIDIA GPU!",
            ]),
            Category("修补工具 / Patch Tools", [
                Step("UU 加速器安装 / UU Accelerator Install", PatchSteps.uu),
                Step("XDG 用户目录转英文 / Migrate XDG Dirs to English", PatchSteps.xdg),
                Step("Fcitx5 输入法环境变量 / Fcitx5 IM Environment Variables", PatchSteps.fcitx),
            ]),
            Category("应用后端切换 / App Backend Toggle", [
                Step("生成 Wayland/X11 启动器 / Generate Wayland-X11 Launchers",
                     BackendSteps.app_backend),
            ]),
        ]
