# 🚀 ArchInit

[![GitHub](https://img.shields.io/badge/GitHub-KamiDream/ArchInit-181717?logo=github)](https://github.com/KamiDream/ArchInit)

**EN** — Arch Linux one-click initialization script built around the [Niri](https://github.com/YaLTeR/niri) scrolling tiling window manager.
**ZH** — 基于 [Niri](https://github.com/YaLTeR/niri) 平铺窗口管理器的 Arch Linux 开发环境一键初始化脚本。

适用于新装 Arch Linux 后，快速搭建包含中文输入、虚拟化、NVIDIA 驱动、终端美化等完整开发工作环境。
Designed for a fresh Arch Linux installation to quickly set up a complete development environment.

## 🖥️ 系统要求 / System Requirements

- **Arch Linux**（已安装并正常启动 / installed and booted）（个人习惯是archinstall时桌面不安装）
- 请确保已经安装 git 和 vim，如果没有安装请运行 `sudo pacman -S vim git`
- 需要 **Python 3**（标准库自带 `curses`，Arch 默认已安装 / bundled with Arch, no extra packages needed）
- 已拥有 `sudo` 权限的普通用户（**不要以 root 身份运行** / **do not run as root**）
- 网络连接正常 / Working internet connection

---

> ⚠️ **免责声明 / Disclaimer**
>
> **使用本项目即表示您已接受并同意自行承担一切风险。**
> **By using this project, you acknowledge and agree to assume all risks.**
>
> · 本免责声明以最新版 README 为准。
> · 本项目按"原样"提供，不附带任何明示或暗示的保证。作者不保证本程序能在所有设备上正常运行，也不对因使用本程序造成的任何直接或间接损失、数据丢失、系统损坏或其他后果承担责任。
>
> · This disclaimer is governed by the latest version of this README.
> · This project is provided "as is" without warranty of any kind. The author makes no guarantees that it will work correctly on all devices, and shall not be held liable for any direct or indirect damages, data loss, system damage, or other consequences arising from its use.

---

## 🚀 使用方法 / Usage

### 克隆运行 / Clone & Run

```bash
git clone https://github.com/KamiDream/ArchInit.git
cd ArchInit
python3 archinit.py
```

> ⚠️ **注意 / Note**：
>
> - **`archinit.py`**：统一交互式安装器（Python 3 + 标准库 `curses`，**零第三方依赖**）。启动后进入**主菜单**，用 ↑/↓ 选择分类，Enter 进入；分类内再用 ↑/↓ 选择步骤，Enter 执行，q/Esc 返回上一级。执行步骤时会自动退出全屏界面，回到普通终端，`pacman`/`chsh`/`kitten`/`sudo` 等交互均正常。
>   Unified interactive installer (Python 3 + stdlib `curses`, **no third-party dependencies**). Pick a **category** from the main menu with ↑/↓ + Enter; inside a category, pick a step with ↑/↓ + Enter, q/Esc to go back. When a step runs, it drops out of the full-screen UI back to the normal terminal so `pacman`/`chsh`/`kitten`/`sudo` work interactively.
>
> 八大分类（原混合安装已拆分为 KVM 安装 / 显卡驱动安装 / 终端美化，步骤完全保留）：
> - **🖥️ 桌面安装 / Desktop Install**：注册 DMS 服务、显示管理器（LightDM）
> - **🧱 基础初始化 / Basic Initialization**：niri 核心组件、系统拓展组件、Kitty 字体、AUR 助手、NTFS 增强工具、雾凇拼音、密钥库
> - **💻 KVM 安装 / KVM Install**：KVM 虚拟化
> - **🎮 显卡驱动安装 / GPU Drivers**：NVIDIA、Intel 核显、AMD 核显
> - **✨ 终端美化 / Terminal Beautification**：Zsh、Antidote、Starship、fastfetch、Kitty 透明度
> - **🎨 LightDM 配置 / LightDM WebKit2 Greeter**：WebKit2 Greeter、KamiDream 主题、启用配置、黑屏救急
> - **🩹 修补工具 / Patch Tools**：UU 加速器、XDG 转英文、Fcitx5 环境变量
> - **🔀 应用后端切换 / App Backend Toggle**：生成应用 Wayland/X11 启动器
>
> Eight categories (the former "Mix Install" is split into KVM Install / GPU Drivers / Terminal Beautification; steps fully preserved):
> - **Desktop Install**: Register DMS service, Display Manager (LightDM)
> - **Basic Initialization**: Niri core components, system extensions, Kitty font, AUR helper, NTFS tools, Rime-ice, keyring
> - **KVM Install**: KVM virtualization
> - **GPU Drivers**: NVIDIA, Intel iGPU, AMD iGPU
> - **Terminal Beautification**: Zsh, Antidote, Starship, fastfetch, Kitty opacity
> - **LightDM Configuration**: WebKit2 greeter, KamiDream theme, enable config, black-screen emergency fix
> - **Patch Tools**: UU Accelerator, XDG dirs to English, Fcitx5 env vars
> - **App Backend Toggle**: Generate Wayland/X11 launchers for an app
>
> 建议顺序：先「桌面安装」→「基础初始化」→ 按需 KVM / 显卡驱动 / 终端美化 → 可选「LightDM 配置」「修补工具」「应用后端切换」。
> Suggested order: Desktop Install → Basic Initialization → optional KVM / GPU Drivers / Terminal Beautification → optional LightDM Configuration / Patch Tools / App Backend Toggle.

---

### 🖥️ 桌面安装 / Desktop Install

> 对应 `archinit.py` 主菜单「桌面安装 / Desktop Install」分类；实现见 [`ZClass/steps/desktop.py`](ZClass/steps/desktop.py)。
> Maps to the "Desktop Install" category in `archinit.py`; implementation in [`ZClass/steps/desktop.py`](ZClass/steps/desktop.py).

#### Step 1: 注册 DMS 服务 / Register DMS Service

| 操作 / Action            | 说明 / Description                                                                                                                                          |
| ------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 🔗 安装 DMS / Install DMS | 通过官方脚本安装 DMS / Install DMS via the official script：`curl -fsSL https://install.danklinux.com \| sh`                                              |

#### Step 2: 显示管理器 / Display Manager (LightDM)

| 操作 / Action                     | 说明 / Description                                                      |
| --------------------------------- | ----------------------------------------------------------------------- |
| 📦 安装 LightDM / Install LightDM   | 安装 `lightdm` 与 `lightdm-gtk-greeter` / Install `lightdm` and `lightdm-gtk-greeter` |
| ▶️ 启用 LightDM / Enable LightDM | 设置 LightDM 开机自启 / Enable LightDM to start on boot                 |
| 🚀 启动 LightDM / Start LightDM  | 立即启动 LightDM 显示管理器 / Start LightDM display manager immediately |

---

### 🧱 基础初始化 / Basic Initialization

> 对应 `archinit.py` 主菜单「基础初始化 / Basic Initialization」分类；实现见 [`ZClass/steps/basic.py`](ZClass/steps/basic.py)。
> Maps to the "Basic Initialization" category in `archinit.py`; implementation in [`ZClass/steps/basic.py`](ZClass/steps/basic.py).

#### Step 1: niri 核心组件 / Niri Core Components

| 操作 / Action                        | 说明 / Description                                                              |
| ------------------------------------ | ------------------------------------------------------------------------------- |
| 📦 安装核心组件 / Install core packages | `kimageformats`（KDE 图像格式插件 / KDE image format plugins）、`power-profiles-daemon`（电源管理 / power management）、`cava`（终端音频可视化 / audio visualizer） |

#### Step 2: 系统拓展组件 / System Extensions

| 操作 / Action                                | 说明 / Description                                                                                                                                                                                                                                                                     |
| -------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 📦 安装基础包 / Install base packages           | `fastfetch`, `fcitx5-im`（中文输入法 / Chinese input）、`fcitx5-rime`、`fuse2`、`vim`、`firefox`、`pcmanfm-qt`（轻量 Qt6 文件管理器 / lightweight Qt6 file manager）、`udisks2`（可移动设备挂载 / removable media mounting） |
| 🔧 设置默认文件管理器 / Set default file manager | 将 `pcmanfm-qt` 设为 `inode/directory` 的默认处理程序 / Set `pcmanfm-qt` as the default handler for `inode/directory` |
| 📦 安装归档解压工具 / Install archive tool | 安装 `xarchiver`（图形化归档/解压缩工具）+ `7zip`（解压 .7z 等格式的后端）：没有它时，在 pcmanfm-qt 中双击压缩包无响应 / Install `xarchiver` (graphical archive tool) + `7zip` (backend for .7z etc.); without it, double-clicking an archive in pcmanfm-qt does nothing |
| 🧹 NTFS 工具说明 / NTFS tools note | NTFS 修复/恢复工具集由 `ntfsprogs-plus` 提供（本脚本 Step 5 安装），它与 `ntfs-3g` 冲突、只装其一；可用 `sudo ntfsfix -d /dev/sdXN` 清除 Windows 未安全弹出导致的脏盘标志 / NTFS repair/recovery tools are provided by `ntfsprogs-plus` (installed in Step 5), which conflicts with `ntfs-3g` (install only one); use `sudo ntfsfix -d /dev/sdXN` to clear the dirty flag from an unsafe Windows eject |
| 💾 自动挂载守护进程 / Auto-mount daemon          | 安装 `udiskie` 与 `gvfs`，并注册 systemd user 服务 `/usr/bin/udiskie`（`Restart=on-failure`）实现「插入即自动挂载」。niri 下 pcmanfm-qt 的 `[Volume] MountRemovable=true` 依赖 LXQt 会话而不生效，需由 udiskie 驱动 / Install `udiskie` & `gvfs`, enable a systemd user service for `/usr/bin/udiskie` (WM-independent); under niri pcmanfm-qt's `[Volume] MountRemovable=true` relies on the LXQt session so udiskie drives it instead |
| 🌐 配置 locale / Configure locale               | 自动取消注释 `/etc/locale.gen` 中的 `zh_CN.UTF-8`，运行 `locale-gen`，设置系统 locale / Auto-uncomment `zh_CN.UTF-8` in `/etc/locale.gen`, run `locale-gen`, set system locale |
| 🔤 安装字体 / Install fonts                     | `wqy-microhei`、`wqy-microhei-lite`、`wqy-bitmapfont`、`wqy-zenhei`、`ttf-arphic-ukai`、`ttf-arphic-uming`、`noto-fonts-cjk`、`ttf-jetbrains-mono-nerd`、`ttf-fira-code`、`inter-font` 等中英文与 Nerd 字体 / Chinese & Nerd fonts 、`noto-fonts-emoji` |
| 📁 配置 XDG 用户目录 / Configure XDG user dirs  | 安装 `xdg-user-dirs`，以英文 locale 运行 `xdg-user-dirs-update`，生成英文文件夹名（Desktop、Downloads 等），系统 locale 保持中文 / Install `xdg-user-dirs`, run `xdg-user-dirs-update` with English locale so folder names are English, system locale stays Chinese |

#### Step 3: Kitty 字体选择 / Kitty Font Selector

| 操作 / Action          | 说明 / Description                                                                                                       |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| 🎨 选择字体 / Select font | 使用 `kitten choose-fonts` 交互式选择 `JetBrains Mono` Nerd 字体 / Interactively select `JetBrains Mono` Nerd Font |

#### Step 4: AUR 助手 / AUR Helper (yay / paru)

| 操作 / Action                           | 说明 / Description                                                                                                                                                            |
| --------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ⚙️ 配置 pacman 源 / Configure pacman repos | 启用 `[multilib]`、添加 `[archlinuxcn]` 源（中科大、清华、哈工大、华为云镜像）/ Enable `[multilib]`, add `[archlinuxcn]` source |
| 📦 安装 AUR 助手 / Install AUR helpers     | `base-devel`、`yay`、`paru`、`flclash` |

#### Step 5: NTFS 增强工具 / NTFS Enhanced Tools

| 操作 / Action                            | 说明 / Description |
| ---------------------------------------- | ------------------ |
| 🧹 安装 ntfsprogs-plus / Install toolset  | 通过 AUR 助手安装 `ntfsprogs-plus`（增强版 NTFS 修复/恢复工具集，含 `ntfsfix` 增强、`ntfsundelete`、`ntfsdump` 等）；与 `ntfs-3g` 冲突、只装其一 / Install `ntfsprogs-plus` via the AUR helper; conflicts with `ntfs-3g` (install only one) |

#### Step 6: 雾凇拼音 / Rime-ice Input Method

| 操作 / Action                         | 说明 / Description |
| ------------------------------------- | ------------------ |
| 🀄 安装雾凇拼音 / Install Rime-ice       | 通过 `yay -S rime-ice-pinyin-git` 安装雾凇拼音输入法词库 / Install Rime-ice input method dictionary |
| 📋 复制 Fcitx5 配置 / Copy Fcitx5 config | 将 [`fcitx5/default.custom.yaml`](fcitx5/default.custom.yaml) 复制到 `~/.local/share/fcitx5/rime/default.custom.yaml` / Copy Fcitx5 Rime-ice config |

#### Step 7: 安装密钥库 / Install Keyring

| 操作 / Action                              | 说明 / Description |
| ------------------------------------------ | ------------------ |
| 📦 安装密钥库 / Install keyring packages      | `gnome-keyring`、`libsecret`、`seahorse`（密钥环守护进程、Secret Service API 库、图形化管理工具 / keyring daemon, Secret Service API library, GUI manager） |
| ▶️ 查看服务状态 / Check service status        | `systemctl --user status gnome-keyring-daemon.service` 查看服务运行状态 / Check the service status |

---

### 💻 KVM 安装 / KVM Install

> 对应 `archinit.py` 主菜单「KVM 安装 / KVM Install」分类；实现见 [`ZClass/steps/kvm.py`](ZClass/steps/kvm.py)。
> Maps to the "KVM Install" category in `archinit.py`; implementation in [`ZClass/steps/kvm.py`](ZClass/steps/kvm.py).

#### Step 1: KVM 虚拟化 / KVM Virtualization

| 操作 / Action                        | 说明 / Description                                                                                         |
| ------------------------------------ | ---------------------------------------------------------------------------------------------------------- |
| 💻 安装 KVM 组件 / Install KVM packages | `qemu-full`、`virt-manager`、`swtpm`、`dnsmasq`                                                    |
| ▶️ 启用服务 / Enable service            | 启用并启动 `libvirtd` 服务 / Enable and start `libvirtd`                                               |
| 🌐 配置网络 / Configure network         | 启动并设置 `default` 虚拟网络为自动启动 / Start and autostart the `default` virtual network            |
| 👤 用户权限 / User permissions          | 将当前用户加入 `libvirt` 组（需重新登录生效）/ Add current user to `libvirt` group (re-login required) |

---

### 🎮 显卡驱动安装 / GPU Drivers

> 对应 `archinit.py` 主菜单「显卡驱动安装 / GPU Drivers」分类；实现见 [`ZClass/steps/gpu.py`](ZClass/steps/gpu.py)。
> Maps to the "GPU Drivers" category in `archinit.py`; implementation in [`ZClass/steps/gpu.py`](ZClass/steps/gpu.py).

#### Step 1: NVIDIA 显卡驱动 / NVIDIA Graphics Driver

| 操作 / Action                            | 说明 / Description                                                                                                                                                                                                                                                                                        |
| ---------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 📦 安装内核头文件 / Install kernel headers  | **自动检测**已安装的内核（`linux` / `linux-zen`），按需安装对应的 headers；若未检测到任何内核则跳过并返回菜单 / **Auto-detect** installed kernels (`linux` / `linux-zen`), install matching headers only; skip with menu return if no kernel found |
| 🎮 安装 NVIDIA 驱动 / Install NVIDIA driver | `nvidia-dkms`、`nvidia-utils`、`nvidia-settings`                                                                                                                                                                                                                                                    |
| ⚙️ 配置 initramfs / Configure initramfs     | 在 `/etc/mkinitcpio.conf` 中添加 nvidia 模块，**自动移除 HOOKS 中的 kms**（避免冲突），重新生成 initramfs / Add nvidia modules to `/etc/mkinitcpio.conf`, **auto-remove kms from HOOKS** (avoids conflict), regenerate initramfs          |

#### Step 2: Intel 核显驱动 / Intel Integrated Graphics

| 操作 / Action                          | 说明 / Description                                                                                                                                                                                           |
| -------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 🖥️ 安装 Intel 核显驱动 / Install drivers | `mesa`（OpenGL/Vulkan 驱动基础）、`vulkan-intel`（Intel Vulkan 驱动）、`intel-media-driver`（硬件视频编解码）、`mesa-utils`（`glxinfo` 等诊断工具）；已安装的包会自动跳过 / `mesa`, `vulkan-intel`, `intel-media-driver`, `mesa-utils`; already-installed packages are skipped |

#### Step 3: AMD 核显驱动 / AMD Integrated Graphics

| 操作 / Action                          | 说明 / Description                                                                                                                                                                                           |
| -------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 🖥️ 安装 AMD 核显驱动 / Install drivers | `mesa`（OpenGL/Vulkan 驱动基础）、`vulkan-radeon`（AMD Vulkan 驱动 RADV）、`libva-mesa-driver`（VA-API 硬件视频解码）、`mesa-utils`（`glxinfo` 等诊断工具）；已安装的包会自动跳过 / `mesa`, `vulkan-radeon`, `libva-mesa-driver`, `mesa-utils`; already-installed packages are skipped |

---

### ✨ 终端美化 / Terminal Beautification

> 对应 `archinit.py` 主菜单「终端美化 / Terminal Beautification」分类；实现见 [`ZClass/steps/terminal.py`](ZClass/steps/terminal.py)。
> Maps to the "Terminal Beautification" category in `archinit.py`; implementation in [`ZClass/steps/terminal.py`](ZClass/steps/terminal.py).

#### Step 1: 启用 Zsh 终端 / Enable Zsh Shell

| 操作 / Action                         | 说明 / Description                                                             |
| ------------------------------------- | ------------------------------------------------------------------------------ |
| 📦 安装 Zsh / Install Zsh                | `zsh`、`zsh-completions`                                                   |
| 🔄 更改默认 Shell / Change default shell | 将当前用户的默认 shell 切换为 Zsh / Switch current user's default shell to Zsh |
| 🎨 配置 Kitty / Configure Kitty          | 设置光标尾迹和闪烁效果 / Set cursor trail and blink effects                    |

#### Step 2: Antidote 插件管理器 / Antidote Plugin Manager

| 操作 / Action                          | 说明 / Description                                                                                                                                              |
| -------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 🧹 清理旧配置 / Clean up old config       | 删除 `~/.antidote`（如有），清理 `.zshrc` 中的 Antidote 引用 / Remove `~/.antidote` if exists, clean Antidote references from `.zshrc`                  |
| 📦 安装 Antidote / Install Antidote       | 通过 `git clone` 安装 Antidote 到 `~/.antidote` / Install Antidote via `git clone`                                                                        |
| ⚙️ 配置插件 / Configure plugins           | 创建 `~/.zsh_plugins.txt`，添加 `zsh-completions`、`zsh-autosuggestions`、`fast-syntax-highlighting` / Create plugin list file with recommended plugins |
| ⚙️ 配置 `.zshrc` / Configure `.zshrc` | 添加 `source ~/.antidote/antidote.zsh`、`antidote load` 和 `compinit` / Add Antidote source, load and compinit to `.zshrc`                              |

#### Step 3: Starship 提示符 / Starship Prompt

| 操作 / Action                              | 说明 / Description                                                                                                                                                       |
| ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 📦 安装 Starship / Install Starship           | 通过 pacman 安装 Starship / Install Starship via pacman                                                                                                                  |
| 📋 复制配置 / Copy config                     | 将 `starship/starship.toml` 复制到 `~/.config/starship.toml` / Copy preset config                                                                                    |
| ⚙️ 配置 `~/.zshrc` / Configure `~/.zshrc` | 在 `.zshrc` 末尾追加 `eval "$(starship init zsh)"`（在 Antidote 配置块之后）/ Append `eval "$(starship init zsh)"` at end of `.zshrc` (after the Antidote block) |

> 🎨 Starship 主题源自 [Catppuccin Starship](https://github.com/catppuccin/starship/tree/main) 与 [TaouMou/starship-presets](https://github.com/TaouMou/starship-presets)，本人将这两个按照自己的喜好合并了一下。

#### Step 4: fastfetch 配置 / fastfetch Configuration

| 操作 / Action          | 说明 / Description                                                                                                                                |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| 📋 复制配置 / Copy config | 将仓库中的 `fastfetch/config.jsonc` 复制到 `~/.config/fastfetch/` / Copy `fastfetch/config.jsonc` from the repo to `~/.config/fastfetch/` |

#### Step 5: 切换 fastfetch 开机自启 / Toggle fastfetch on Startup

| 操作 / Action                              | 说明 / Description                                                                                                                                                                                                                                                                                                                                                                                         |
| ------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 🔄 切换 `fastfetch` 自启 / Toggle fastfetch | 若 `.zshrc` 第一行是 `fastfetch`（或 ` fastfetch`）则删除之（关闭）；否则添加 ` fastfetch`（带前导空格，利用 `HIST_IGNORE_SPACE` 避免记入历史）为第一行（开启）/ If `.zshrc` first line is `fastfetch` (or ` fastfetch`), remove it (disable); otherwise prepend ` fastfetch` (with leading space — leverages `HIST_IGNORE_SPACE` to exclude from history) as the first line (enable) |

#### Step 6: Kitty 背景透明度 / Kitty Background Opacity

| 操作 / Action                   | 说明 / Description                                                                                                                                                                                                                           |
| ------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 🎨 调整背景透明度 / Adjust opacity | 显示当前 `background_opacity` 值，提供预设选项（0.6~1.0）或自定义输入，自动更新 `~/.config/kitty/kitty.conf` / Show current `background_opacity`, offer presets (0.6~1.0) or custom input, auto-update `~/.config/kitty/kitty.conf` |

---
### 🎨 LightDM 配置 / LightDM WebKit2 Greeter

> 对应 `archinit.py` 主菜单「LightDM 配置 / LightDM WebKit2 Greeter」分类；实现见 [`ZClass/steps/lightdm.py`](ZClass/steps/lightdm.py)。
> Maps to the "LightDM Configuration" category in `archinit.py`; implementation in [`ZClass/steps/lightdm.py`](ZClass/steps/lightdm.py).

> ⚠️ **单 N 卡独显或开启了独显直连的用户（纯 N 卡用户）请勿使用此配置！**
> **Do NOT use this configuration if you have a single/primary NVIDIA GPU!**
>
> 用于替换默认的 LightDM GTK Greeter，安装 `lightdm-webkit2-greeter` 并启用 KamiDream WebKit2 主题。
> Use this script to replace the default LightDM GTK greeter with `lightdm-webkit2-greeter` and the KamiDream WebKit2 theme.

#### Step 1: 安装 LightDM WebKit2 Greeter / Install LightDM WebKit2 Greeter

| 操作 / Action                                           | 说明 / Description                                                                                   |
| ------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| 📦 安装 lightdm-webkit2-greeter / Install package          | `sudo pacman -S --needed --noconfirm lightdm-webkit2-greeter` / Install lightdm-webkit2-greeter only |

#### Step 2: 安装/更新 KamiDream 主题 / Install / Update KamiDream Theme

| 操作 / Action                                             | 说明 / Description                                                                                                                                                                 |
| --------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 🧹 清理旧主题 / Clean up old theme                          | 若 `/usr/share/lightdm-webkit/themes/KamiDream_Theme` 已存在则删除 / Remove existing theme directory if present                                                                |
| 📥 克隆主题 / Clone theme                                   | `git clone https://github.com/KamiDream/LdmWk2Theme` 到 `~/LdmWk2Theme` 并移动到 `/usr/share/lightdm-webkit/themes/KamiDream_Theme` / Clone to `~/LdmWk2Theme` then move to target |
| 🔄 更新主题 / Update theme                                  | 重复执行 Step 2 即可自动删除旧主题并下载最新版 / Re-run Step 2 to delete the old theme and download the latest version                                                           |
| 🖼️ 替换背景图片 / Replace background image                  | 替换 `/usr/share/lightdm-webkit/themes/KamiDream_Theme/assets/background.png` 为你自己的图片即可 / Replace the image at that path with your own                                |

#### Step 3: 启用 LightDM 配置 / Enable LightDM Configuration

| 操作 / Action                                                      | 说明 / Description                                                                                                             |
| ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------ |
| ⚙️ 配置 `/etc/lightdm/lightdm.conf` / Configure lightdm.conf          | 在 `[Seat:*]` 段设置 `greeter-session=lightdm-webkit2-greeter` / Set greeter session to lightdm-webkit2-greeter              |
| ⚙️ 配置 `/etc/lightdm/lightdm-webkit2-greeter.conf` / Configure conf | 将 `webkit_theme` 设置为 `KamiDream_Theme`（替换原值） / Set `webkit_theme` to `KamiDream_Theme` (replaces existing value) |
| 🔄 重启提示 / Reboot prompt                                         | 配置完成后提示用户重启系统以应用 LightDM / Prompt user to reboot to apply LightDM                                             |

#### Step 4: 黑屏救急 / Black Screen Emergency Fix

> 如果配置 LightDM WebKit2 Greeter 后出现黑屏无法进入图形界面，运行此步骤可快速恢复默认 Greeter。
> If you encounter a black screen after configuring LightDM WebKit2 Greeter, run this step to quickly restore the default greeter.

| 操作 / Action                                                         | 说明 / Description                                                                                          |
| --------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| #️⃣ 注释 WebKit2 Greeter 配置 / Comment out WebKit2 Greeter config       | 在 `/etc/lightdm/lightdm.conf` 中将 `greeter-session=lightdm-webkit2-greeter` 行前加 `#` 注释掉 / Comment out the line |
| 🔄 重启系统 / Reboot system                                           | 重启系统以恢复默认 GTK Greeter / Reboot to restore default greeter                                                 |

---
### 🩹 修补工具 / Patch Tools

> 对应 `archinit.py` 主菜单「修补工具 / Patch Tools」分类；实现见 [`ZClass/steps/patch.py`](ZClass/steps/patch.py)。
> Maps to the "Patch Tools" category in `archinit.py`; implementation in [`ZClass/steps/patch.py`](ZClass/steps/patch.py).

#### Step 1: UU 加速器安装（SteamDeck）/ UU Accelerator Install

> **手机用户注意**：
>
> 1. 先在手机上安装 **UU 加速器主机版**
> 2. 在 SteamDeck 上运行此脚本安装 UU 加速器
> 3. 然后在手机 App 中按 **SteamDeck 安装方法** 指引完成后续配置
>
> **For phone users**:
>
> 1. Install the **UU Accelerator console version** on your phone first.
> 2. Run this script on SteamDeck to install the UU Accelerator client.
> 3. Then follow the **SteamDeck installation guide** in the phone app to complete the setup.

| 操作 / Action                           | 说明 / Description                                                                                                      |
| --------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| 📁 创建 /home/deck 目录 / Create directory | 创建 `/home/deck` 并设置当前用户为所有者 / Create `/home/deck` and set ownership to current user                    |
| 📥 下载安装脚本 / Download install script  | 从 `uudeck.com` 下载并执行 UU 加速器安装脚本 / Download and run the UU Accelerator install script from `uudeck.com` |

#### Step 2: XDG 用户目录转英文 / Migrate XDG Dirs to English

| 操作 / Action                                         | 说明 / Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| ----------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| | 📦 安装 xdg-user-dirs / Install xdg-user-dirs            | 确保 `xdg-user-dirs` 已安装 / Ensure `xdg-user-dirs` is installed                                                                                                                                                                                                                                                                                                                                                                                              |
| | 💾 备份原配置 / Backup old config                        | 将当前 `~/.config/user-dirs.dirs` 备份为 `user-dirs.dirs.bak.<timestamp>` / Backup current `~/.config/user-dirs.dirs` to `user-dirs.dirs.bak.<timestamp>`                                                                                                                                                                                                                                                                                                                 |
| | ✏️ 写入英文配置 / Write English config                   | 直接写入 `~/.config/user-dirs.dirs`，所有路径为英文（Desktop、Downloads、Projects 等），不依赖 locale / Directly write `~/.config/user-dirs.dirs` with all English paths (Desktop, Downloads, Projects, etc.), locale-independent                                                                                                                                                                                                                                                                                              |
| | 📂 迁移目录内容 / Migrate directory contents             | 对比新旧配置，对每个路径变化的目录：创建英文目录 → 移动所有内容（含隐藏文件）→ 删除旧的中文目录 / Compare old vs new config; for each changed directory: create English dir → move all contents (including hidden files) -> remove old Chinese dir                                                                                                                                                                                                       |
| | ✅ 完成提示 / Completion notice                          | 显示迁移统计，告知备份文件位置，提示重新登录生效 / Show migration stats, backup location, re-login hint                                                                                                                                                                                                                                                                                                                                                             |

#### Step 3: Fcitx5 输入法环境变量 / Fcitx5 IM Environment Variables

| 操作 / Action                                   | 说明 / Description                                                                                                                                                                                                                                                                              |
| ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| | 💾 备份原配置 / Backup old config                 | 若 `~/.config/environment.d/fcitx.conf` 已存在则备份为 `fcitx.conf.bak.<timestamp>` / Backup existing `~/.config/environment.d/fcitx.conf` to `fcitx.conf.bak.<timestamp>`                                                                                                            |
| | ✏️ 写入环境变量 / Write environment variables     | 在 `~/.config/environment.d/fcitx.conf` 写入 `XMODIFIERS=@im=fcitx5`、`GTK_IM_MODULE=fcitx5`、`QT_IM_MODULE=fcitx5`、`SDL_IM_MODULE=fcitx5` / Write `XMODIFIERS=@im=fcitx5`, `GTK_IM_MODULE=fcitx5`, `QT_IM_MODULE=fcitx5`, `SDL_IM_MODULE=fcitx5` to `~/.config/environment.d/fcitx.conf` |
| | ✅ 完成提示 / Completion notice                    | 提示重新登录后生效（environment.d 由 systemd 用户会话加载）/ Re-login to take effect (environment.d is loaded by systemd user session)                                                                                                                                                   |

---

### 🔀 应用后端切换 / App Backend Toggle

> 对应 `archinit.py` 主菜单「应用后端切换 / App Backend Toggle」分类；实现见 [`ZClass/steps/backend.py`](ZClass/steps/backend.py)。
> Maps to the "App Backend Toggle" category in `archinit.py`; implementation in [`ZClass/steps/backend.py`](ZClass/steps/backend.py).

#### Step 1: 生成 Wayland/X11 启动器 / Generate Wayland-X11 Launchers

> 为指定应用生成两个启动器，分别在 Wayland 与 X11（XWayland）下运行，运行哪个就切到哪个后端。
> Generate two launchers for a given app to run it under Wayland or X11 (XWayland); run either to switch backend.

| 操作 / Action                        | 说明 / Description |
| ------------------------------------ | ------------------ |
| 🖥️ 输入应用 / Enter app           | 提示输入应用命令（如 `firefox`、`code`），自动解析其可执行文件路径；输入 `q` 取消，命令不存在时最多重试 3 次 / Prompt for an app command, resolving its executable path; enter `q` to cancel, up to 3 retries when the command is not found |
| 🧩 生成启动器 / Generate launchers | 在 `~/.local/bin/` 写入可执行的 `<app>-wayland` 与 `<app>-x11`，分别设置 `QT_QPA_PLATFORM`/`GDK_BACKEND`/`SDL_VIDEODRIVER`/`MOZ_ENABLE_WAYLAND`/`ELECTRON_OZONE_PLATFORM_HINT` 后 `exec` 目标程序 / Write executable `<app>-wayland` and `<app>-x11` wrappers into `~/.local/bin/` that set backend env vars then exec the target |
| 💡 使用 / Usage               | 运行 `<app>-wayland` 或 `<app>-x11` 即在该后端下启动；若 `~/.local/bin` 不在 PATH 中会给出提示 / Run `<app>-wayland` or `<app>-x11` to launch in that backend; a hint is shown when `~/.local/bin` is missing from PATH |

---

## 🔧 自定义与扩展 / Customization

- **选择步骤 / Choose steps**：[`archinit.py`](archinit.py) 提供统一交互式菜单（`curses`）：主菜单选择 8 大分类，分类内用 ↑/↓ 选择步骤，Enter 执行，q/Esc 返回 / [`archinit.py`](archinit.py) provides a unified interactive menu (`curses`): pick one of 8 categories from the main menu, then use ↑/↓ to select a step, Enter to execute, q/Esc to go back.
- **自动配置 / Automated edits**：所有配置修改（locale、pacman.conf、mkinitcpio.conf、.zshrc 等）均由脚本自动完成（`sed` 或 Python 直接读写文件），无需手动编辑 / All configuration changes (locale, pacman.conf, mkinitcpio.conf, .zshrc, etc.) are applied automatically (`sed` or direct file I/O in Python) — no manual editing required.
- **添加自己的包 / Add your own packages**：修改 `ZClass/steps/` 下对应步骤类方法里的 `pacman -S` 列表（如 `basic.py`、`gpu.py`）/ Edit the `pacman -S` lists in the corresponding step class methods under `ZClass/steps/` (e.g. `basic.py`, `gpu.py`).

---

## ❓ 常见问题 / FAQ

### Q：运行脚本后需要做什么？/ What should I do after running?

1. **重新登录或重启系统**，使组权限（libvirt）和 shell 更改生效 / **Re-login or reboot** for group changes (libvirt) and shell changes to take effect.
2. 运行 `fastfetch` 查看系统信息，确认环境正常 / Run `fastfetch` to verify the environment.
3. 若配置了 fcitx5，在桌面环境中添加输入法并启用 Rime / If fcitx5 was configured, add the input method and enable Rime.

### Q：Kitty 字体选择器无法启动？/ Kitty font selector won't launch?

确保已安装 Kitty：`sudo pacman -S kitty`，或在 [`archinit.py`](archinit.py) 的「基础初始化 / Basic Initialization」分类的 **Step 3**（Kitty 字体选择）前手动安装。
Make sure Kitty is installed: `sudo pacman -S kitty`, or install it manually before **Step 3** (Kitty font selector) of the "Basic Initialization" category in [`archinit.py`](archinit.py).

### Q：NVIDIA 驱动安装后黑屏？/ Black screen after NVIDIA driver install?

检查 `/etc/mkinitcpio.conf` 中的 `MODULES` 配置是否正确，重新运行 `sudo mkinitcpio -P` 并重启。
Check the `MODULES` line in `/etc/mkinitcpio.conf`, then run `sudo mkinitcpio -P` and reboot.

### Q：编译 NVIDIA 驱动时出现 LTS 内核报错？/ LTS kernel error when compiling NVIDIA driver?

脚本默认只检测 `linux` 和 `linux-zen` 内核并安装对应 headers，不会自动安装 `linux-lts-headers` 或 `linux-hardened-headers`。如果系统中安装了 LTS 内核，`mkinitcpio -P` 会为**所有**已安装的内核生成 initramfs，缺少 LTS 头文件会导致编译报错。

- **不影响正常使用**：报错仅针对 LTS 内核，而你日常使用的并非 LTS 内核。
- **LTS 内核定位**：仅作为紧急情况下的备用内核，正常情况下不会使用。
- **如果不想看到报错**，按以下步骤操作：
  1. 安装 LTS 头文件：`sudo pacman -S linux-lts-headers`
  2. 重新运行 [`archinit.py`](archinit.py) 的「显卡驱动安装 / GPU Drivers」分类 **Step 1**（NVIDIA 显卡驱动）
  3. 重启系统

This error occurs because the script only auto-detects `linux` and `linux-zen` kernels — it does not install `linux-lts-headers` or `linux-hardened-headers`. If you have the LTS kernel installed, `mkinitcpio -P` builds initramfs for **all** installed kernels, and missing LTS headers cause compilation warnings/errors.

- **No impact on normal use**: The error only affects the LTS kernel, which is not your daily driver.
- **LTS kernel role**: Emergency backup only — not used under normal circumstances.
- **To suppress the error**:
  1. Install LTS headers: `sudo pacman -S linux-lts-headers`
  2. Re-run **Step 1** of the "GPU Drivers" category in [`archinit.py`](archinit.py) (NVIDIA driver step)
  3. Reboot

### Q：locales 未生效？/ Locales not working?

请确保 `/etc/locale.gen` 中 `zh_CN.UTF-8` 已取消注释，并手动运行：
Ensure `zh_CN.UTF-8` is uncommented in `/etc/locale.gen`, then manually run:

```bash
sudo locale-gen
sudo localectl set-locale LANG=zh_CN.UTF-8
```

---

### Q：如何自定义 Starship 提示符？/ How to customize Starship prompt?

Starship 使用 TOML 配置文件 `~/.config/starship.toml`。你可以从预设配置开始：

```bash
mkdir -p ~/.config
starship preset tokyo-night -o ~/.config/starship.toml
```

常用预设：`tokyo-night`、`pastel-powerline`、`gruvbox-rainbow`。完整列表见 [Starship Presets](https://starship.rs/presets/)。

你也可以手动编辑配置文件，参考 [Starship 配置文档](https://starship.rs/config/)。

---

## 📝 许可证 / License

本项目仅供学习和个人使用。造成的损失概不负责
This project is for personal and educational use. We are not responsible for any losses incurred.

---

## 🙏 致谢 / Credits

- [Niri](https://github.com/YaLTeR/niri) — 滚动式平铺窗口管理器 / Scrolling tiling Wayland compositor
- [Antidote](https://github.com/mattmc3/antidote) — Zsh 插件管理器 / Zsh plugin manager
- [Starship](https://starship.rs) — 跨 Shell 提示符 / Cross-shell prompt
- [Kitty](https://sw.kovidgoyal.net/kitty/) — GPU 加速终端 / GPU-accelerated terminal emulator
- [LightDM](https://github.com/canonical/lightdm) — 显示管理器 / Display manager
