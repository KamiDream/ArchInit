# 🚀 ArchInit

[![GitHub](https://img.shields.io/badge/GitHub-KamiDream/ArchInit-181717?logo=github)](https://github.com/KamiDream/ArchInit)

**EN** — Arch Linux one-click initialization script built around the [Niri](https://github.com/YaLTeR/niri) scrolling tiling window manager.
**ZH** — 基于 [Niri](https://github.com/YaLTeR/niri) 平铺窗口管理器的 Arch Linux 开发环境一键初始化脚本。

适用于新装 Arch Linux 后，快速搭建包含中文输入、虚拟化、NVIDIA 驱动、终端美化等完整开发工作环境。
Designed for a fresh Arch Linux installation to quickly set up a complete development environment.

---

## 📋 功能概览 / Feature Overview

### [`niri_init.sh`](niri_init.sh) — 核心安装 / Core Setup

| Step        | Content                              | Description                                                                                                                                 |
| ----------- | ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------- |
| **1** | 🖥️ 核心桌面 / Core Desktop         | 安装 Niri 平铺窗口管理器、DMS Shell、Alacritty、Matugen、Cava、SDDM / Install Niri tiling WM, DMS Shell, Alacritty, Matugen, Cava, SDDM     |
| **2** | 🧰 基础初始化 / Basic Initialization | 安装常用软件、配置中文 locale、安装中英文与 Nerd 字体 / Install common packages, configure zh_CN.UTF-8 locale, install Chinese & Nerd fonts |
| **3** | 🖥️ 显示管理器 / Display Manager    | 启用并启动 SDDM 显示管理器 / Enable and start SDDM display manager                                                                          |

### [`niri_append.sh`](niri_append.sh) — 可选扩展 / Optional Extras

| Step        | Content                              | Description                                                                                                                 |
| ----------- | ------------------------------------ | --------------------------------------------------------------------------------------------------------------------------- |
| **1** | 💻 KVM 虚拟化 / KVM Virtualization   | 安装 QEMU/virt-manager，启用 libvirtd，配置虚拟网络 / Install QEMU/virt-manager, enable libvirtd, configure virtual network |
| **2** | 📦 AUR 助手 / AUR Helper             | 配置 archlinuxcn 源，安装 yay / paru 等 AUR 助手 / Configure archlinuxcn repo, install yay/paru AUR helpers                 |
| **3** | 🎮 NVIDIA 驱动 / NVIDIA Driver       | 安装 NVIDIA 闭源驱动 (nvidia-dkms) / Install NVIDIA proprietary driver                                                      |
| **4** | 🎨 终端美化 / Terminal Customization | 安装 Zsh + 插件、配置 Kitty 终端、选择 Nerd 字体 / Install Zsh + plugins, configure Kitty terminal, select Nerd font        |
| **5** | ⚡ Zim + Powerlevel10k               | 安装 Zim 框架与 Powerlevel10k 主题 / Install Zim framework & Powerlevel10k theme                                            |
| **6** | 📁 fastfetch 配置 / fastfetch Config | 复制 fastfetch 配置文件到 ~/.config/fastfetch / Copy fastfetch config to ~/.config/fastfetch                                |

---

## 🖥️ 系统要求 / System Requirements

- **Arch Linux**（已安装并正常启动 / installed and booted）
- 请确保已经安装 git 和 vim，如果没有安装请运行 `sudo pacman -S vim git`
- 已拥有 `sudo` 权限的普通用户（**不要以 root 身份运行** / **do not run as root**）
- 网络连接正常 / Working internet connection

---

## 🚀 使用方法 / Usage

### 克隆运行 / Clone & Run

```bash
git clone https://github.com/KamiDream/ArchInit.git
cd ArchInit
chmod +x niri_init.sh niri_append.sh
./niri_init.sh
```

> ⚠️ **注意 / Note**：脚本采用**交互式**执行，每一步都会询问是否执行（`Y/n`），您可以选择跳过某些步骤。部分步骤会打开 vim/kate 编辑器要求手动修改配置文件，**请按提示完成编辑后保存退出**。
> The script is **interactive** — each step asks for confirmation (`Y/n`) and you can skip any step. Some steps open vim/kate for manual config file edits; **follow the prompts, edit, save, and exit**.
>
> 先运行 `niri_init.sh` 完成核心安装，再根据需要运行 `niri_append.sh` 安装可选组件。
> Run `niri_init.sh` first for the core setup, then run `niri_append.sh` for optional extras as needed.

---

## 📦 各步骤详解 / Step Details

### [`niri_init.sh`](niri_init.sh) — 核心步骤 / Core Steps

#### Step 1: 核心桌面环境 / Core Desktop Environment (Niri + DMS)

| 操作 / Action                                          | 说明 / Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| ------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 安装 Niri 及周边组件 / Install Niri & related packages | `niri`（平铺窗口管理器 / tiling WM）、`xwayland-satellite`（XWayland 支持）、`xdg-desktop-portal-gnome` / `xdg-desktop-portal-gtk`（桌面门户 / desktop portals）、`alacritty`（GPU 加速终端 / GPU-accelerated terminal）、`dms-shell-niri`（DMS Shell）、`matugen`（Material You 配色生成器 / color generator）、`cava`（终端音频可视化 / audio visualizer）、`qt6-multimedia-ffmpeg`（Qt6 多媒体后端 / multimedia backend）、`sddm`（显示管理器 / display manager） |
| 注册 DMS 服务 / Register DMS service                   | 将 DMS 添加为 `niri.service` 的 user service 依赖，实现开机自启 / Add DMS as a user service dependency of `niri.service` for auto-start                                                                                                                                                                                                                                                                                                                                              |

#### Step 2: 基础初始化 / Basic Initialization

| 操作 / Action                      | 说明 / Description                                                                                                                                                              |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 安装基础包 / Install base packages | `fastfetch`, `fcitx5-im`（中文输入法 / Chinese input）、`fcitx5-rime`、`fuse2`、`ntfs-3g`、`git`、`quickshell`、`flatseal`、`dolphin`、`kate`、`firefox`  |
| 配置 locale / Configure locale     | 编辑 `/etc/locale.gen` 启用 `zh_CN.UTF-8`，运行 `locale-gen`，设置系统 locale / Edit `/etc/locale.gen` to enable `zh_CN.UTF-8`, run `locale-gen`, set system locale |
| 安装字体 / Install fonts           | `wqy-microhei`、`wqy-zenhei`、`noto-fonts-cjk`、`ttf-jetbrains-mono-nerd` 等中英文与 Nerd 字体 / Chinese & Nerd fonts                                                   |

#### Step 3: 显示管理器 / Display Manager (SDDM)

| 操作 / Action           | 说明 / Description                                                |
| ----------------------- | ----------------------------------------------------------------- |
| 启用 SDDM / Enable SDDM | 设置 SDDM 开机自启 / Enable SDDM to start on boot                 |
| 启动 SDDM / Start SDDM  | 立即启动 SDDM 显示管理器 / Start SDDM display manager immediately |

---

### [`niri_append.sh`](niri_append.sh) — 可选扩展步骤 / Optional Steps

#### Step 1: KVM 虚拟化 / KVM Virtualization

| 操作 / Action                        | 说明 / Description                                                                                         |
| ------------------------------------ | ---------------------------------------------------------------------------------------------------------- |
| 安装 KVM 组件 / Install KVM packages | `qemu-full`、`virt-manager`、`swtpm`、`dnsmasq`                                                    |
| 启用服务 / Enable service            | 启用并启动 `libvirtd` 服务 / Enable and start `libvirtd`                                               |
| 配置网络 / Configure network         | 启动并设置 `default` 虚拟网络为自动启动 / Start and autostart the `default` virtual network            |
| 用户权限 / User permissions          | 将当前用户加入 `libvirt` 组（需重新登录生效）/ Add current user to `libvirt` group (re-login required) |

#### Step 2: AUR 助手 / AUR Helper (yay / paru)

| 操作 / Action                           | 说明 / Description                                                                                                                                                            |
| --------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 配置 pacman 源 / Configure pacman repos | 启用 `[multilib]`、添加 `[archlinuxcn]` 源（中科大、清华、哈工大、华为云镜像）/ Enable `[multilib]`, add `[archlinuxcn]` (mirrors: USTC, Tsinghua, HIT, Huawei Cloud) |
| 安装 AUR 助手 / Install AUR helpers     | `base-devel`、`yay`、`paru`、`flclash`                                                                                                                                |

#### Step 3: NVIDIA 显卡驱动 / NVIDIA Graphics Driver

| 操作 / Action                            | 说明 / Description                                                                                                                        |
| ---------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| 安装内核头文件 / Install kernel headers  | `linux-headers`、`linux-zen-headers`                                                                                                  |
| 安装 NVIDIA 驱动 / Install NVIDIA driver | `nvidia-dkms`、`nvidia-utils`、`nvidia-settings`                                                                                    |
| 配置 initramfs / Configure initramfs     | 在 `/etc/mkinitcpio.conf` 中添加 nvidia 模块，重新生成 initramfs / Add nvidia modules to `/etc/mkinitcpio.conf`, regenerate initramfs |

#### Step 4: 终端环境配置 / Terminal Customization (Zsh & Kitty)

| 操作 / Action                             | 说明 / Description                                                                                 |
| ----------------------------------------- | -------------------------------------------------------------------------------------------------- |
| 安装 Zsh 及插件 / Install Zsh and plugins | `zsh`、`zsh-autosuggestions`、`zsh-syntax-highlighting`、`zsh-completions`                 |
| 更改默认 Shell / Change default shell     | 将当前用户的默认 shell 切换为 Zsh / Switch current user's default shell to Zsh                     |
| 配置 `.zshrc` / Configure `.zshrc`    | 添加 `fastfetch` 启动信息及 Zsh 插件加载 / Add `fastfetch` startup info and Zsh plugin sources |
| 配置 Kitty / Configure Kitty              | 设置光标尾迹和闪烁效果 / Set cursor trail and blink effects                                        |
| 选择字体 / Select font                    |                                                                                                    |

#### Step 5: Zim 框架 + Powerlevel10k / Zim Framework & Powerlevel10k

| 操作 / Action                          | 说明 / Description                                                                                                                   |
| -------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| 安装 Zim 框架 / Install Zim framework  | 通过官方安装脚本一键安装 / One-click install via the official Zim script                                                             |
| 配置 `.zimrc` / Configure `.zimrc` | 添加 `zmodule romkatv/powerlevel10k` 启用 Powerlevel10k 主题 / Add `zmodule romkatv/powerlevel10k` to enable Powerlevel10k theme |

#### Step 6: fastfetch 配置 / fastfetch Configuration

| 操作 / Action          | 说明 / Description                                                                                                                                |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| 操作 / Action          | 说明 / Description                                                                                                                                |
| --------               | -------------                                                                                                                                     |
| 复制配置 / Copy config | 将仓库中的 `fastfetch/config.jsonc` 复制到 `~/.config/fastfetch/` / Copy `fastfetch/config.jsonc` from the repo to `~/.config/fastfetch/` |
| 选择字体 / Select font | 使用 `kitten choose-fonts` 交互式选择 `JetBrains Mono` Nerd 字体 / Interactively select `JetBrains Mono` Nerd Font                          |

---

## 🔧 自定义与扩展 / Customization

- **跳过步骤 / Skip steps**：每个步骤开始前都会询问，输入 `n` 即可跳过 / Each step asks before running — enter `n` to skip.
- **手动编辑 / Manual edits**：部分配置（locale、pacman.conf、mkinitcpio.conf 等）需要手动编辑，脚本会打开编辑器等待完成 / Some configs require manual editing; the script opens an editor and waits.
- **添加自己的包 / Add your own packages**：可直接修改 `niri_init.sh` 或 `niri_append.sh` 中的 `pacman -S` 列表，增删所需软件包 / Edit the scripts and modify the `pacman -S` lists to suit your needs.

---

## ❓ 常见问题 / FAQ

### Q：运行脚本后需要做什么？/ What should I do after running?

1. **重新登录或重启系统**，使组权限（libvirt）和 shell 更改生效 / **Re-login or reboot** for group changes (libvirt) and shell changes to take effect.
2. 运行 `fastfetch` 查看系统信息，确认环境正常 / Run `fastfetch` to verify the environment.
3. 若配置了 fcitx5，在桌面环境中添加输入法并启用 Rime / If fcitx5 was configured, add the input method and enable Rime.

### Q：Kitty 字体选择器无法启动？/ Kitty font selector won't launch?

确保已安装 Kitty：`sudo pacman -S kitty`，或在 Step 4 前手动安装。
Make sure Kitty is installed: `sudo pacman -S kitty`, or install it manually before Step 4.

### Q：NVIDIA 驱动安装后黑屏？/ Black screen after NVIDIA driver install?

检查 `/etc/mkinitcpio.conf` 中的 `MODULES` 配置是否正确，重新运行 `sudo mkinitcpio -P` 并重启。
Check the `MODULES` line in `/etc/mkinitcpio.conf`, then run `sudo mkinitcpio -P` and reboot.

### Q：locales 未生效？/ Locales not working?

请确保 `/etc/locale.gen` 中 `zh_CN.UTF-8` 已取消注释，并手动运行：
Ensure `zh_CN.UTF-8` is uncommented in `/etc/locale.gen`, then manually run:

```bash
sudo locale-gen
sudo localectl set-locale LANG=zh_CN.UTF-8
```

---

## 📝 许可证 / License

本项目仅供学习和个人使用。如有问题或建议，欢迎提交 Issue 或 PR。
This project is for personal and educational use. Feel free to open issues or PRs.

---

## 🙏 致谢 / Credits

- [Niri](https://github.com/YaLTeR/niri) — 滚动式平铺窗口管理器 / Scrolling tiling Wayland compositor
- [Zim](https://github.com/zimfw/zimfw) — Zsh 插件框架 / Zsh plugin framework
- [Powerlevel10k](https://github.com/romkatv/powerlevel10k) — Zsh 主题 / Zsh theme
- [Kitty](https://sw.kovidgoyal.net/kitty/) — GPU 加速终端 / GPU-accelerated terminal emulator
- [SDDM](https://github.com/sddm/sddm) — 显示管理器 / Display manager
