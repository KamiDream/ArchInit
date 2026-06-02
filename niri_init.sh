#!/bin/bash

# Arch Linux initialization script (run as a normal user with sudo privileges)
# Each major step will ask for confirmation before execution.
# Manual edits will pause the script until the editor is closed.

set -euo pipefail

# ---------- Step 0: Core Desktop (Niri + DMS) ----------
echo "========================================="
echo " 第 0 步：安装核心桌面环境（Niri 平铺窗口管理器 & DMS Shell）"
echo "========================================="
read -p "是否执行本步骤？(Y/n): " do_step
if [[ ! "$do_step" =~ ^[Yy]$ ]] && [ -n "$do_step" ]; then
    echo "跳过第 0 步。"
else
    echo ">>> 安装 Niri 及周边组件..."
    sudo pacman -Syu niri xwayland-satellite xdg-desktop-portal-gnome \
        xdg-desktop-portal-gtk alacritty dms-shell-niri matugen cava \
        qt6-multimedia-ffmpeg

    echo ">>> 将 DMS 注册为 Niri 的 user service 依赖..."
    systemctl --user add-wants niri.service dms

    echo "[第 0 步完成]"
fi
echo ""

# ---------- Step 1: Initialization ----------
echo "========================================="
echo " 第 1 步：基础初始化（安装常用软件、配置 locale、安装字体）"
echo "========================================="
read -p "是否执行本步骤？(Y/n): " do_step
if [[ ! "$do_step" =~ ^[Yy]$ ]] && [ -n "$do_step" ]; then
    echo "跳过第 1 步。"
else
    echo ">>> 安装基础软件包..."
    sudo pacman -S --needed fastfetch fcitx5-im fcitx5-rime fuse2 ntfs-3g git quickshell flatseal dolphin kate firefox

    echo ""
    echo ">>> 接下来将用 vim 编辑 /etc/locale.gen"
    echo "    请找到 'zh_CN.UTF-8' 行并取消注释（删除前面的 #），然后保存退出。"
    read -p "按回车键打开编辑器..."
    sudo vim /etc/locale.gen
    read -p "编辑完成，按回车继续..."

    echo ">>> 生成 locale..."
    sudo locale-gen
    echo ">>> 设置系统 locale 为 zh_CN.UTF-8..."
    sudo localectl set-locale LANG=zh_CN.UTF-8

    echo ">>> 安装中文字体与 Nerd 字体..."
    sudo pacman -S --needed wqy-microhei wqy-microhei-lite wqy-bitmapfont wqy-zenhei \
        ttf-arphic-ukai ttf-arphic-uming noto-fonts-cjk ttf-jetbrains-mono-nerd

    echo "[第 1 步完成]"
fi
echo ""

# ---------- Step 2: KVM Virtualization ----------
echo "========================================="
echo " 第 2 步：安装并配置 KVM 虚拟化环境"
echo "========================================="
read -p "是否执行本步骤？(Y/n): " do_step
if [[ ! "$do_step" =~ ^[Yy]$ ]] && [ -n "$do_step" ]; then
    echo "跳过第 2 步。"
else
    echo ">>> 安装 KVM 相关软件包..."
    sudo pacman -S --needed qemu-full virt-manager swtpm dnsmasq

    echo ">>> 启用并启动 libvirtd 服务..."
    sudo systemctl enable --now libvirtd

    echo ">>> 启动默认虚拟网络..."
    sudo virsh net-start default
    sudo virsh net-autostart default

    echo ">>> 将当前用户加入 libvirt 组..."
    sudo usermod -a -G libvirt "$(whoami)"
    echo "    注意：需要重新登录才能使组权限生效。"

    echo "[第 2 步完成]"
fi
echo ""

# ---------- Step 3: NVIDIA Driver ----------
echo "========================================="
echo " 第 3 步：配置 NVIDIA 显卡驱动"
echo "========================================="
read -p "是否执行本步骤？(Y/n): " do_step
if [[ ! "$do_step" =~ ^[Yy]$ ]] && [ -n "$do_step" ]; then
    echo "跳过第 3 步。"
else
    echo ">>> 安装内核头文件..."
    sudo pacman -S --needed linux-headers linux-zen-headers

    echo ""
    echo ">>> 接下来需要用 vim 编辑 /etc/pacman.conf"
    echo "    请完成以下修改："
    echo "    1) 取消 [multilib] 及其 Include 行的注释"
    echo "    2) 在文件末尾添加 archlinuxcn 源（详见下面内容）"
    echo ""
    echo "    需要添加的内容："
    echo "    [archlinuxcn]"
    echo "    Server = https://mirrors.ustc.edu.cn/archlinuxcn/\$arch"
    echo "    Server = https://mirrors.tuna.tsinghua.edu.cn/archlinuxcn/\$arch"
    echo "    Server = https://mirrors.hit.edu.cn/archlinuxcn/\$arch"
    echo "    Server = https://repo.huaweicloud.com/archlinuxcn/\$arch"
    read -p "按回车键打开编辑器..."
    sudo vim /etc/pacman.conf
    read -p "编辑完成，按回车继续..."

    echo ">>> 安装 archlinuxcn-keyring 并更新系统..."
    sudo pacman -Sy --needed archlinuxcn-keyring
    sudo pacman -S --needed base-devel yay paru flclash
    sudo pacman -Syu

    echo ">>> 安装 NVIDIA 驱动..."
    sudo pacman -S --needed nvidia-dkms nvidia-utils nvidia-settings

    echo ""
    echo ">>> 接下来将编辑 /etc/mkinitcpio.conf，在 MODULES=() 中添加 nvidia 模块："
    echo "    MODULES=(nvidia nvidia_modeset nvidia_uvm nvidia_drm)"
    read -p "按回车键打开编辑器..."
    sudo vim /etc/mkinitcpio.conf
    read -p "编辑完成，按回车继续..."

    echo ">>> 重新生成 initramfs..."
    sudo mkinitcpio -P

    echo "[第 3 步完成]"
fi
echo ""

# ---------- Step 4: DMS (Dank Linux Install) ----------
echo "========================================="
echo " 第 4 步：安装 DMS（Dank Linux）"
echo "========================================="
read -p "是否执行本步骤？(Y/n): " do_step
if [[ ! "$do_step" =~ ^[Yy]$ ]] && [ -n "$do_step" ]; then
    echo "跳过第 4 步。"
else
    echo ">>> 执行 Dank Linux 安装脚本..."
    curl -fsSL https://install.danklinux.com | sh
    echo "[第 4 步完成]"
fi
echo ""

# ---------- Step 5: Terminal Customization (Zsh & Kitty) ----------
echo "========================================="
echo " 第 5 步：终端环境配置（Zsh、Kitty）"
echo "========================================="
read -p "是否执行本步骤？(Y/n): " do_step
if [[ ! "$do_step" =~ ^[Yy]$ ]] && [ -n "$do_step" ]; then
    echo "跳过第 5 步。"
else
    echo ">>> 安装 Zsh 及相关插件..."
    sudo pacman -S --needed zsh zsh-autosuggestions zsh-syntax-highlighting zsh-completions

    echo ">>> 显示可用 Shell 列表..."
    chsh -l

    echo ">>> 将当前用户的默认 Shell 改为 Zsh（需要输入密码）..."
    chsh -s /usr/bin/zsh

    echo ""
    echo ">>> 接下来将用 Kate 编辑 ~/.zshrc，请添加以下内容："
    echo "    fastfetch"
    echo "    source /usr/share/zsh/plugins/zsh-autosuggestions/zsh-autosuggestions.zsh"
    echo "    source /usr/share/zsh/plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh"
    read -p "按回车键打开编辑器..."
    kate ~/.zshrc
    read -p "编辑完成，按回车继续..."

    echo ""
    echo ">>> 接下来将编辑 Kitty 终端配置文件 ~/.config/kitty/kitty.conf"
    echo "    需要添加的内容："
    echo "    cursor_trail 2"
    echo "    cursor_blink_interval 0.5"
    echo "    cursor_stop_blinking_after 0"
    read -p "按回车键打开编辑器..."
    kate ~/.config/kitty/kitty.conf
    read -p "编辑完成，按回车继续..."

    echo ""
    echo ">>> 运行 Kitty 字体选择器，请选择 JetBrains Mono 字体..."
    read -p "按回车键启动字体选择工具..."
    kitten choose-fonts
    read -p "字体选择完成，按回车继续..."

    echo "[第 5 步完成]"
fi
echo ""

# ---------- Step 6: Install Zim Framework & Powerlevel10k ----------
echo "========================================="
echo " 第 6 步：安装 Zim 框架及 Powerlevel10k 主题"
echo "========================================="
read -p "是否执行本步骤？(Y/n): " do_step
if [[ ! "$do_step" =~ ^[Yy]$ ]] && [ -n "$do_step" ]; then
    echo "跳过第 6 步。"
else
    # Check if Zsh is available
    if ! command -v zsh >/dev/null 2>&1; then
        echo "警告：Zsh 似乎未安装，Zim 框架需要 Zsh 环境。"
        read -p "按回车键继续安装，或按 Ctrl+C 取消..."
    fi

    echo ">>> 安装 Zim 框架..."
    curl -fsSL https://raw.githubusercontent.com/zimfw/install/master/install.zsh | zsh

    echo ""
    echo ">>> 接下来将用 Kate 编辑 ~/.zimrc，请添加以下内容："
    echo "    zmodule romkatv/powerlevel10k"
    read -p "按回车键打开编辑器..."
    kate ~/.zimrc
    read -p "编辑完成，按回车继续..."

    echo "[第 6 步完成]"
fi

echo "========================================="
echo " 所有选中步骤执行完毕！"
echo " 请重新登录或重启系统以使更改生效。"
echo "========================================="
