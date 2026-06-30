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
| **1** | 🖥️ 核心桌面 / Core Desktop         | 安装 Niri 平铺窗口管理器、Kitty、DMS Shell 等核心组件 / Install Niri tiling WM, Kitty, DMS Shell and other core components                  |
| **2** | 🔗 注册 DMS 服务 / Register DMS      | 将 DMS 注册为 Niri 的 user service 依赖 / Register DMS as a user service dependency of Niri                                                 |
| **3** | 🧰 基础初始化 / Basic Initialization | 安装常用软件、配置中文 locale、安装中英文与 Nerd 字体 / Install common packages, configure zh_CN.UTF-8 locale, install Chinese & Nerd fonts |
| **4** | 🖥️ 显示管理器 / Display Manager    | 启用并启动 LightDM 显示管理器 / Enable and start LightDM display manager                                                                    |

### [`niri_append.sh`](niri_append.sh) — 可选扩展 / Optional Extras

| Step         | Content                                  | Description                                                                                                                                  |
| ------------ | ---------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| **1**  | 🎨 Kitty 字体选择 / Font Selector        | 使用 Kitty 字体选择器交互式选择 JetBrains Mono Nerd 字体 / Interactively select JetBrains Mono Nerd Font via Kitty font selector             |
| **2**  | 💻 KVM 虚拟化 / KVM Virtualization       | 安装 QEMU/virt-manager，启用 libvirtd，配置虚拟网络 / Install QEMU/virt-manager, enable libvirtd, configure virtual network                  |
| **3**  | 📦 AUR 助手 / AUR Helper                 | 配置 archlinuxcn 源，安装 yay / paru 等 AUR 助手 / Configure archlinuxcn repo, install yay/paru AUR helpers                                  |
| **4**  | 🎮 NVIDIA 驱动 / NVIDIA Driver           | 安装 NVIDIA 闭源驱动 (nvidia-dkms) / Install NVIDIA proprietary driver                                                                       |
| **5**  | 🎨 启用 Zsh 终端 / Enable Zsh Shell      | 安装 Zsh、切换默认 Shell、配置 Kitty 终端 / Install Zsh, change default shell, configure Kitty terminal                                      |
| **6**  | ⚡ Antidote 插件管理器 / Antidote Plugin | 安装 Antidote 插件管理器，加载自动建议、语法高亮等插件 / Install Antidote plugin manager, load autosuggestions & syntax highlighting plugins |
| **7**  | 🚀 Starship 提示符 / Starship Prompt     | 安装 Starship 提示符 / Install Starship prompt                                                                                               |
| **8**  | 📁 fastfetch 配置 / fastfetch Config     | 复制 fastfetch 配置文件到 ~/.config/fastfetch / Copy fastfetch config to ~/.config/fastfetch                                                 |
| **9**  | 🚀 fastfetch 自启 / Startup              | 将 fastfetch 设为 .zshrc 第一行，开机显示系统信息 / Add fastetch as the first line in .zshrc for system info on startup                      |
| **10** | 🎨 Kitty 背景透明度 / Background Opacity | 交互式调整 Kitty 终端背景透明度 / Interactively adjust Kitty terminal background opacity                                                     |
| **11** | 🀄 雾凇拼音 / Rime-ice Input Method      | 安装雾凇拼音输入法并复制 Fcitx5 配置 / Install Rime-ice input method and copy Fcitx5 config                                                  |

### [`universal.sh`](universal.sh) — 通用工具 / Universal Tools

| Step        | Content                                               | Description                                                                                                              |
| ----------- | ----------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| **1** | 🎮 UU 加速器安装（SteamDeck）/ UU Accelerator Install | 创建 /home/deck 目录并安装 UU 加速器 SteamDeck 版 / Create /home/deck directory and install UU Accelerator for SteamDeck |

---

## 🖥️ 系统要求 / System Requirements

- **Arch Linux**（已安装并正常启动 / installed and booted）（个人习惯是archinstall时桌面不安装）
- 请确保已经安装 git 和 vim，如果没有安装请运行 `sudo pacman -S vim git`
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
chmod +x niri_init.sh niri_append.sh universal.sh
./niri_init.sh
```

> ⚠️ **注意 / Note**：
>
> - **`niri_init.sh`**：**全自动一键安装**。运行后只需输入 sudo 密码，即可依次完成所有步骤。无需任何手动操作。
>   **Fully automated one-click setup** — enter your sudo password and all steps run sequentially.
> - **`niri_append.sh`**：提供**交互式菜单**，使用 ↑/↓ 方向键导航，Enter 执行选中的步骤，q 退出。
>   Provides an **interactive menu** — use ↑/↓ arrows to navigate, Enter to execute, q to quit.
> - **`universal.sh`**：**通用工具合集**，同样提供交互式菜单。目前包含 SteamDeck UU 加速器安装等通用工具。
>   **Universal tool collection**, also with an interactive menu. Currently includes SteamDeck UU Accelerator installation and other general-purpose tools.
>
> 先运行 `niri_init.sh` 完成核心安装，再根据需要运行 `niri_append.sh` 安装可选组件，`universal.sh` 可随时运行。
> Run `niri_init.sh` first for the core setup, then run `niri_append.sh` for optional extras. `universal.sh` can be run at any time.

---

## 📦 各步骤详解 / Step Details

### [`niri_init.sh`](niri_init.sh) — 核心步骤 / Core Steps

#### Step 1: 核心桌面环境 / Core Desktop Environment (Niri)

| 操作 / Action                                          | 说明 / Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| ------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 安装 Niri 及周边组件 / Install Niri & related packages | `niri`（平铺窗口管理器 / tiling WM）、`xwayland-satellite`（XWayland 支持）、`xdg-desktop-portal-gnome` / `xdg-desktop-portal-gtk`（桌面门户 / desktop portals）、`kitty`（GPU 加速终端 / GPU-accelerated terminal）、`dms-shell-niri`（DMS Shell）、`matugen`（Material You 配色生成器 / color generator）、`cava`（终端音频可视化 / audio visualizer）、`qt6-multimedia-ffmpeg`（Qt6 多媒体后端 / multimedia backend）、`lightdm` / `lightdm-gtk-greeter`（显示管理器 / display manager & greeter）、`power-profiles-daemon`（电源管理 / power management）、`kimageformats`（KDE 图像格式插件 / KDE image format plugins） |

#### Step 2: 注册 DMS 服务 / Register DMS Service

| 操作 / Action                        | 说明 / Description                                                                                                                                                                               |
| ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 注册 DMS 服务 / Register DMS service | 通过官方脚本安装 DMS，并将其添加为 `niri.service` 的 user service 依赖，实现开机自启 / Install DMS via official script and add as a user service dependency of `niri.service` for auto-start |

#### Step 3: 基础初始化 / Basic Initialization

| 操作 / Action                      | 说明 / Description                                                                                                                                                                                                                         |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 安装基础包 / Install base packages | `fastfetch`, `fcitx5-im`（中文输入法 / Chinese input）、`fcitx5-rime`、`fuse2`、`ntfs-3g`、`git`、`quickshell`、`flatseal`、`dolphin`、`kate`、`firefox`                                                             |
| 配置 locale / Configure locale     | 自动取消注释 `/etc/locale.gen` 中的 `zh_CN.UTF-8`，运行 `locale-gen`，设置系统 locale / Auto-uncomment `zh_CN.UTF-8` in `/etc/locale.gen`, run `locale-gen`, set system locale                                                 |
| 安装字体 / Install fonts           | `wqy-microhei`、`wqy-microhei-lite`、`wqy-bitmapfont`、`wqy-zenhei`、`ttf-arphic-ukai`、`ttf-arphic-uming`、`noto-fonts-cjk`、`ttf-jetbrains-mono-nerd` 等中英文与 Nerd 字体 / Chinese & Nerd fonts 、`noto-fonts-emoji` |

#### Step 4: 显示管理器 / Display Manager (LightDM)

| 操作 / Action                 | 说明 / Description                                                      |
| ----------------------------- | ----------------------------------------------------------------------- |
| 启用 LightDM / Enable LightDM | 设置 LightDM 开机自启 / Enable LightDM to start on boot                 |
| 启动 LightDM / Start LightDM  | 立即启动 LightDM 显示管理器 / Start LightDM display manager immediately |

---

### [`niri_append.sh`](niri_append.sh) — 可选扩展步骤 / Optional Steps

#### Step 1: Kitty 字体选择 / Kitty Font Selector

| 操作 / Action          | 说明 / Description                                                                                                                                   |
| ---------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| 选择字体 / Select font | 使用 `kitten choose-fonts` 交互式选择 `JetBrains Mono` Nerd 字体 / Interactively select `JetBrains Mono` Nerd Font via `kitten choose-fonts` |

#### Step 2: KVM 虚拟化 / KVM Virtualization

| 操作 / Action                        | 说明 / Description                                                                                         |
| ------------------------------------ | ---------------------------------------------------------------------------------------------------------- |
| 安装 KVM 组件 / Install KVM packages | `qemu-full`、`virt-manager`、`swtpm`、`dnsmasq`                                                    |
| 启用服务 / Enable service            | 启用并启动 `libvirtd` 服务 / Enable and start `libvirtd`                                               |
| 配置网络 / Configure network         | 启动并设置 `default` 虚拟网络为自动启动 / Start and autostart the `default` virtual network            |
| 用户权限 / User permissions          | 将当前用户加入 `libvirt` 组（需重新登录生效）/ Add current user to `libvirt` group (re-login required) |

#### Step 3: AUR 助手 / AUR Helper (yay / paru)

| 操作 / Action                           | 说明 / Description                                                                                                                                                            |
| --------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 配置 pacman 源 / Configure pacman repos | 启用 `[multilib]`、添加 `[archlinuxcn]` 源（中科大、清华、哈工大、华为云镜像）/ Enable `[multilib]`, add `[archlinuxcn]` (mirrors: USTC, Tsinghua, HIT, Huawei Cloud) |
| 安装 AUR 助手 / Install AUR helpers     | `base-devel`、`yay`、`paru`、`flclash`                                                                                                                                |

#### Step 4: NVIDIA 显卡驱动 / NVIDIA Graphics Driver

| 操作 / Action                            | 说明 / Description                                                                                                                                                                                                                               |
| ---------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 安装内核头文件 / Install kernel headers  | `linux-headers`、`linux-zen-headers`                                                                                                                                                                                                         |
| 安装 NVIDIA 驱动 / Install NVIDIA driver | `nvidia-dkms`、`nvidia-utils`、`nvidia-settings`                                                                                                                                                                                           |
| 配置 initramfs / Configure initramfs     | 在 `/etc/mkinitcpio.conf` 中添加 nvidia 模块，**自动移除 HOOKS 中的 kms**（避免冲突），重新生成 initramfs / Add nvidia modules to `/etc/mkinitcpio.conf`, **auto-remove kms from HOOKS** (avoids conflict), regenerate initramfs |

#### Step 5: 启用 Zsh 终端 / Enable Zsh Shell

| 操作 / Action                         | 说明 / Description                                                             |
| ------------------------------------- | ------------------------------------------------------------------------------ |
| 安装 Zsh / Install Zsh                | `zsh`、`zsh-completions`                                                   |
| 更改默认 Shell / Change default shell | 将当前用户的默认 shell 切换为 Zsh / Switch current user's default shell to Zsh |
| 配置 Kitty / Configure Kitty          | 设置光标尾迹和闪烁效果 / Set cursor trail and blink effects                    |

#### Step 6: Antidote 插件管理器 / Antidote Plugin Manager

| 操作 / Action                          | 说明 / Description                                                                                                                                              |
| -------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 清理旧配置 / Clean up old config       | 删除 `~/.antidote`（如有），清理 `.zshrc` 中的 Antidote 引用 / Remove `~/.antidote` if exists, clean Antidote references from `.zshrc`                  |
| 安装 Antidote / Install Antidote       | 通过 `git clone` 安装 Antidote 到 `~/.antidote` / Install Antidote via `git clone`                                                                        |
| 配置插件 / Configure plugins           | 创建 `~/.zsh_plugins.txt`，添加 `zsh-completions`、`zsh-autosuggestions`、`fast-syntax-highlighting` / Create plugin list file with recommended plugins |
| 配置 `.zshrc` / Configure `.zshrc` | 添加 `source ~/.antidote/antidote.zsh`、`antidote load` 和 `compinit` / Add Antidote source, load and compinit to `.zshrc`                              |

#### Step 7: Starship 提示符 / Starship Prompt

| 操作 / Action                              | 说明 / Description                                                                                                                                                       |
| ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 安装 Starship / Install Starship           | 通过 pacman 安装 Starship / Install Starship via pacman                                                                                                                  |
| 复制配置 / Copy config                     | 将 `starship/starship.toml` 复制到 `~/.config/starship.toml` / Copy preset config                                                                                    |
| 配置 `~/.zshrc` / Configure `~/.zshrc` | 在 `.zshrc` 末尾追加 `eval "$(starship init zsh)"`（在 Antidote 配置块之后）/ Append `eval "$(starship init zsh)"` at end of `.zshrc` (after the Antidote block) |

> 🎨 Starship 主题源自 [Catppuccin Starship](https://github.com/catppuccin/starship/tree/main)，默认使用 **Macchiato** 配色。提示符：`󰄛 ❯`（成功绿色，错误红色），目录淡紫色，Git 分支紫色。

#### Step 8: fastfetch 配置 / fastfetch Configuration

| 操作 / Action          | 说明 / Description                                                                                                                                |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| 复制配置 / Copy config | 将仓库中的 `fastfetch/config.jsonc` 复制到 `~/.config/fastfetch/` / Copy `fastfetch/config.jsonc` from the repo to `~/.config/fastfetch/` |

#### Step 9: 切换 fastfetch 开机自启 / Toggle fastfetch on Startup

| 操作 / Action                              | 说明 / Description                                                                                                                                                                                                                                                                                                                                                                                         |
| ------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 切换 `fastfetch` 自启 / Toggle fastfetch | 若 `.zshrc` 第一行是 `fastfetch`（或 ` fastfetch`）则删除之（关闭）；否则添加 ` fastfetch`（带前导空格，利用 `HIST_IGNORE_SPACE` 避免记入历史）为第一行（开启）/ If `.zshrc` first line is `fastfetch` (or ` fastfetch`), remove it (disable); otherwise prepend ` fastfetch` (with leading space — leverages `HIST_IGNORE_SPACE` to exclude from history) as the first line (enable) |

#### Step 10: Kitty 背景透明度 / Kitty Background Opacity

| 操作 / Action                   | 说明 / Description                                                                                                                                                                                                                           |
| ------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 调整背景透明度 / Adjust opacity | 显示当前 `background_opacity` 值，提供预设选项（0.6~1.0）或自定义输入，自动更新 `~/.config/kitty/kitty.conf` / Show current `background_opacity`, offer presets (0.6~1.0) or custom input, auto-update `~/.config/kitty/kitty.conf` |

#### Step 11: 雾凇拼音 / Rime-ice Input Method

| 操作 / Action                         | 说明 / Description                                                                                                                                                                                                                                                                                                                          |
| ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 安装雾凇拼音 / Install Rime-ice       | 通过 `yay -S rime-ice-pinyin-git` 安装雾凇拼音输入法词库 / Install Rime-ice input method dictionary via `yay -S rime-ice-pinyin-git`                                                                                                                                                                                                    |
| 复制 Fcitx5 配置 / Copy Fcitx5 config | 将仓库中的[`fcitx5/default.custom.yaml`](fcitx5/default.custom.yaml) 复制到 `~/.local/share/fcitx5/rime/default.custom.yaml`，配置雾凇拼音为 Fcitx5 Rime 默认方案 / Copy [`fcitx5/default.custom.yaml`](fcitx5/default.custom.yaml) to `~/.local/share/fcitx5/rime/default.custom.yaml` to set Rime-ice as the default Fcitx5 Rime schema |

---

### [`universal.sh`](universal.sh) — 通用工具步骤 / Universal Tool Steps

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
| 创建 /home/deck 目录 / Create directory | 创建 `/home/deck` 并设置当前用户为所有者 / Create `/home/deck` and set ownership to current user                    |
| 下载安装脚本 / Download install script  | 从 `uudeck.com` 下载并执行 UU 加速器安装脚本 / Download and run the UU Accelerator install script from `uudeck.com` |

---

## 🔧 自定义与扩展 / Customization

- **选择步骤 / Choose steps**：[`niri_init.sh`](niri_init.sh) 为全自动一键安装，所有步骤依次执行；[`niri_append.sh`](niri_append.sh) 提供交互式菜单，使用 ↑/↓ 方向键选择步骤，Enter 执行，q 退出 / [`niri_init.sh`](niri_init.sh) runs fully automated; [`niri_append.sh`](niri_append.sh) provides an interactive menu — use ↑/↓ arrows to select, Enter to execute, q to quit.
- **自动配置 / Automated edits**：所有配置修改（locale、pacman.conf、mkinitcpio.conf 等）均由脚本通过 `sed` 自动完成，无需手动编辑 / All configuration changes (locale, pacman.conf, mkinitcpio.conf, etc.) are applied automatically via `sed` — no manual editing required.
- **添加自己的包 / Add your own packages**：可直接修改 `niri_init.sh` 或 `niri_append.sh` 中的 `pacman -S` 列表，增删所需软件包 / Edit the scripts and modify the `pacman -S` lists to suit your needs.

---

## ❓ 常见问题 / FAQ

### Q：运行脚本后需要做什么？/ What should I do after running?

1. **重新登录或重启系统**，使组权限（libvirt）和 shell 更改生效 / **Re-login or reboot** for group changes (libvirt) and shell changes to take effect.
2. 运行 `fastfetch` 查看系统信息，确认环境正常 / Run `fastfetch` to verify the environment.
3. 若配置了 fcitx5，在桌面环境中添加输入法并启用 Rime / If fcitx5 was configured, add the input method and enable Rime.

### Q：Kitty 字体选择器无法启动？/ Kitty font selector won't launch?

确保已安装 Kitty：`sudo pacman -S kitty`，或在 [`niri_append.sh`](niri_append.sh) 的 **Step 1** 前手动安装。
Make sure Kitty is installed: `sudo pacman -S kitty`, or install it manually before **Step 1** of [`niri_append.sh`](niri_append.sh).

### Q：NVIDIA 驱动安装后黑屏？/ Black screen after NVIDIA driver install?

检查 `/etc/mkinitcpio.conf` 中的 `MODULES` 配置是否正确，重新运行 `sudo mkinitcpio -P` 并重启。
Check the `MODULES` line in `/etc/mkinitcpio.conf`, then run `sudo mkinitcpio -P` and reboot.

### Q：编译 NVIDIA 驱动时出现 LTS 内核报错？/ LTS kernel error when compiling NVIDIA driver?

这是因为脚本未安装 `linux-lts-headers`，而 `mkinitcpio -P` 会为系统中**所有**已安装的内核生成 initramfs，缺少 LTS 头文件会导致编译报错。

- **不影响正常使用**：报错仅针对 LTS 内核，而你日常使用的并非 LTS 内核。
- **LTS 内核定位**：仅作为紧急情况下的备用内核，正常情况下不会使用。
- **如果不想看到报错**，按以下步骤操作：
  1. 安装 LTS 头文件：`sudo pacman -S linux-lts-headers`
  2. 重新运行 [`niri_append.sh`](niri_append.sh) 的 **Step 4**（NVIDIA 显卡驱动脚本）
  3. 重启系统

This error occurs because `linux-lts-headers` is not installed, but `mkinitcpio -P` builds initramfs for **all** installed kernels. Missing LTS headers cause compilation warnings/errors.

- **No impact on normal use**: The error only affects the LTS kernel, which is not your daily driver.
- **LTS kernel role**: Emergency backup only — not used under normal circumstances.
- **To suppress the error**:
  1. Install LTS headers: `sudo pacman -S linux-lts-headers`
  2. Re-run **Step 4** of [`niri_append.sh`](niri_append.sh) (NVIDIA driver script)
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

本项目仅供学习和个人使用。如有问题或建议，欢迎提交 Issue 或 PR。
This project is for personal and educational use. Feel free to open issues or PRs.

---

## 🙏 致谢 / Credits

- [Niri](https://github.com/YaLTeR/niri) — 滚动式平铺窗口管理器 / Scrolling tiling Wayland compositor
- [Antidote](https://github.com/mattmc3/antidote) — Zsh 插件管理器 / Zsh plugin manager
- [Starship](https://starship.rs) — 跨 Shell 提示符 / Cross-shell prompt
- [Kitty](https://sw.kovidgoyal.net/kitty/) — GPU 加速终端 / GPU-accelerated terminal emulator
- [LightDM](https://github.com/canonical/lightdm) — 显示管理器 / Display manager
