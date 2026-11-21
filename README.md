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
> - **`archinit.py`**：统一交互式安装器（Python 3 + 标准库 `curses`，**零第三方依赖**）。启动后先进**主题风格的启动页**（`ArchInit_KamiDream` 品牌 + `═` 分隔线）：sudo 已缓存则短暂展示后进主菜单，需要密码则**直接在启动页里输**（掩码显示，不切屏）；进去后用 ↑/↓ 选择分类，Enter 进入；分类内再用 ↑/↓ 选择步骤，Enter 执行，q/Esc 返回上一级。执行步骤时会自动退出全屏界面，回到普通终端，`pacman`/`chsh`/`kitten`/`sudo` 等交互均正常。
>   Unified interactive installer (Python 3 + stdlib `curses`, **no third-party dependencies**). It starts with a **branded splash screen** (the `ArchInit_KamiDream` title with `═` rules): if sudo is already cached it lingers briefly and opens the menu, otherwise the sudo password is entered **right on the splash screen** (masked, no screen switching). Then pick a **category** with ↑/↓ + Enter; inside a category, pick a step with ↑/↓ + Enter, q/Esc to go back. When a step runs, it drops out of the full-screen UI back to the normal terminal so `pacman`/`chsh`/`kitten`/`sudo` work interactively.
>
> 步骤结束后的等待提示为**单键响应**：`Enter` 继续、`q` 或 `ESC` 直接返回菜单（无需再按回车）。
> After a step finishes, the wait prompt takes a **single key**: `Enter` continues, `q` or `ESC` returns to the menu immediately.

> sudo 密码只需在启动页输一次：之后所有命令都在**同一个「无 tty」上下文**里以 `sudo -n` 执行（sudo 凭证默认按 tty 记录，换了 tty 就会重新要密码）；命令内部再用 `script` 分配 pty，所以 pacman 的进度条/百分比照样能显示。
> The sudo password is asked only once, on the splash screen: afterwards every command runs with `sudo -n` inside the same **no-tty context** (sudo tickets are per-tty by default, so a different tty would ask again); each command still gets a pty via `script`, so pacman progress bars and percentages keep working.
>
> 步骤的运行提示/错误/结果都显示在界面内（任务面板、选择器顶部的黄色提示行、主界面底部的状态行），不会直接刷到终端上；底部状态行按任意键消失。
> Step hints, errors and results are shown **inside the UI** (task panel, yellow notice line in the picker, status line at the bottom) instead of being printed to the terminal; any key dismisses the status line.
>
> 大部分步骤在**任务面板**里执行（`✅`/`⏳`/`❌` 清单，命令输出不落到终端）；执行中的任务会在清单下方显示一个**进度区（最近几行）**：同一个包的进度原地刷新、不同包依次往上累积，**包含下载百分比、已下载大小与速度**；spinner 与耗时显示在**右下角（双实线下方）**（如 `nvidia-utils  [#####] 45%  68.2 MiB  5.1 MiB/s`）。失败时停在该步并给出原因；只有本身就需要真实终端/全屏交互的步骤（`kitten choose-fonts`、UU 官方安装脚本、DMS 注册脚本）会临时把终端交还给它，结束后自动回到面板；其中 UU 与 DMS 的安装脚本会跑在**独立 pty** 里（自带控制终端，并把键盘/输出转发过来），避免脚本 `open("/dev/tty")` 报“无法打开新 tty”。
> Most steps run inside a **task panel** (a `✅`/`⏳`/`❌` checklist; command output never reaches the terminal). The running task shows a **progress area (last few lines)**: progress bars refresh in place for the same package while different packages stack upwards, including **download percentage, transferred size and speed**; the spinner and elapsed time sit in the **bottom-right corner, under the `═` rule** (e.g. `nvidia-utils  [#####] 45%  68.2 MiB  5.1 MiB/s`). On failure the panel stops on that step with the reason; only steps that need a real terminal or full-screen interaction (`kitten choose-fonts`, the UU installer, the DMS installer) hand the terminal back temporarily; the UU and DMS installers run inside a **dedicated pty** (own controlling terminal, with your keyboard and their output forwarded), so their `open("/dev/tty")` never fails with "unable to open new tty".
>
> 八大分类（原混合安装已拆分为 KVM 安装 / 显卡驱动安装 / 终端美化，步骤完全保留）：
> - **🖥️ 桌面安装 / Desktop Install**：注册 DMS 服务
> - **🧱 基础初始化 / Basic Initialization**：niri 核心组件、系统拓展组件、Kitty 字体、AUR 助手、NTFS 增强工具、雾凇拼音、密钥库
> - **💻 KVM 安装 / KVM Install**：KVM 虚拟化
> - **🎮 显卡驱动安装 / GPU Drivers**：NVIDIA、Intel 核显、AMD 核显
> - **✨ 终端美化 / Terminal Beautification**：Zsh、Antidote、Starship、fastfetch、Kitty 透明度
> - **🔐 登录管理器 / Login Manager**：greetd + ReGreet（安装、配置启用、更换背景图、解锁密钥环）
> - **🩹 修补工具 / Patch Tools**：UU 加速器、XDG 转英文、Fcitx5 环境变量、卸除 LightDM
> - **🔀 应用后端切换 / App Backend Toggle**：选择应用（列表或直接输入命令）并选平台启动
>
> Eight categories (the former "Mix Install" is split into KVM Install / GPU Drivers / Terminal Beautification; steps fully preserved):
> - **Desktop Install**: Register DMS service
> - **Basic Initialization**: Niri core components, system extensions, Kitty font, AUR helper, NTFS tools, Rime-ice, keyring
> - **KVM Install**: KVM virtualization
> - **GPU Drivers**: NVIDIA, Intel iGPU, AMD iGPU
> - **Terminal Beautification**: Zsh, Antidote, Starship, fastfetch, Kitty opacity
> - **Login Manager**: greetd + ReGreet (install, configure & enable, change background, keyring unlock)
> - **Patch Tools**: UU Accelerator, XDG dirs to English, Fcitx5 env vars, remove LightDM
> - **App Backend Toggle**: Pick an app (from the list or by typing a command) and launch it on a chosen backend
>
> 建议顺序：先「桌面安装」→「基础初始化」→「登录管理器」→ 按需 KVM / 显卡驱动 / 终端美化 → 可选「修补工具」「应用后端切换」。
> Suggested order: Desktop Install → Basic Initialization → Login Manager → optional KVM / GPU Drivers / Terminal Beautification → optional Patch Tools / App Backend Toggle.

---

### 🖥️ 桌面安装 / Desktop Install

> 对应 `archinit.py` 主菜单「桌面安装 / Desktop Install」分类；实现见 [`ZClass/steps/desktop.py`](ZClass/steps/desktop.py)。
> Maps to the "Desktop Install" category in `archinit.py`; implementation in [`ZClass/steps/desktop.py`](ZClass/steps/desktop.py).
>
> 本分类**直接输出到终端**（不走任务面板）：安装脚本的进度、提示与输出都留在终端上，方便确认它到底在做什么。DMS 脚本仍跑在独立 pty 里，保证 `open("/dev/tty")` 可用。
> This category **prints straight to the terminal** (no task panel): the installer's own progress and prompts stay on screen. The DMS script still runs in a dedicated pty so `open("/dev/tty")` works.

#### Step 1: 注册 DMS 服务 / Register DMS Service

| 操作 / Action            | 说明 / Description                                                                                                                                          |
| ------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 🔗 安装 DMS / Install DMS | 通过官方脚本安装 DMS / Install DMS via the official script：`curl -fsSL https://install.danklinux.com \| sh`                                              |

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
| 🎨 调整背景透明度 / Adjust opacity | 弹出光标列表（↑/↓ 选择，当前值预先高亮）：`0.6` / `0.7` / `0.8`（默认）/ `0.9` / `1.0`，Esc 取消；选中后自动更新 `~/.config/kitty/kitty.conf` / Opens a cursor list (↑/↓, current value pre-highlighted): `0.6`/`0.7`/`0.8` (default)/`0.9`/`1.0`, Esc to cancel; updates `~/.config/kitty/kitty.conf` |

---
### 🔐 登录管理器 / Login Manager（greetd + ReGreet）

> 对应 `archinit.py` 主菜单「登录管理器 / Login Manager（greetd + ReGreet）」分类；实现见 [`ZClass/steps/login_manager.py`](ZClass/steps/login_manager.py)。
> Maps to the "Login Manager" category in `archinit.py`; implementation in [`ZClass/steps/login_manager.py`](ZClass/steps/login_manager.py).
>
> 用 greetd + ReGreet 替代 LightDM：ReGreet 是 GTK4/Wayland 登录器，需要一个合成器承载，这里按上游推荐用 **cage**；会话列表直接读 `/usr/share/wayland-sessions`（你这台机器目前只有 Niri）。整套不依赖 webkit2gtk，主题也不会因为 WebKit 升级而失效。
> Replaces LightDM with greetd + ReGreet: a GTK4/Wayland greeter hosted by **cage** (upstream's recommended setup). Sessions come from `/usr/share/wayland-sessions` (only Niri on this machine). Nothing depends on webkit2gtk anymore.
>
> ⚠️ 换了登录器就可能把自己关在门外：启用前请确认 `regreet` / `cage` 可执行。出问题就在 TTY（`Ctrl+Alt+F2`）里排查：
> `journalctl -u greetd -b -e` 看错误；配置坏了可以 `sudo systemctl disable greetd` 先停用，修好 `/etc/greetd/config.toml` 再启用。LightDM 已不再作为方案，需要装回时用 `sudo pacman -S lightdm lightdm-gtk-greeter`（本工具不再提供回退步骤）。
> ⚠️ Switching the greeter can lock you out: verify `regreet` / `cage` run first. If it breaks, use a TTY (`Ctrl+Alt+F2`): `journalctl -u greetd -b -e`, or `sudo systemctl disable greetd` and fix `/etc/greetd/config.toml`. LightDM is no longer part of this tool; install `lightdm lightdm-gtk-greeter` manually if you ever need it back.

#### Step 1: 安装 greetd + ReGreet / Install

| 操作 / Action | 说明 / Description |
| --- | --- |
| 📦 安装三个包 / Install packages | `greetd greetd-regreet cage`（ReGreet 的 GTK4 / GStreamer / AccountsService 依赖由包自动拉取）/ Installs `greetd greetd-regreet cage` (GTK4/GStreamer/AccountsService deps are pulled automatically) |

#### Step 2: 配置并启用 / Configure & enable

| 操作 / Action | 说明 / Description |
| --- | --- |
| ✅ 检查可执行文件 / Check binaries | `/usr/bin/regreet`、`/usr/bin/cage` 缺失则中止（先跑 Step 1）/ Aborts when either binary is missing |
| ⚙️ `/etc/greetd/config.toml` | 写入 `[terminal] vt = 1` 与 `[default_session] command = "dbus-run-session cage -s -mlast -d -- regreet"`、`user = "greeter"`（`-s` 保留 VT 切换，`-mlast` 只用最后接入的显示器，`-d` 不要客户端装饰）/ Writes the terminal + default session (`cage -s -mlast -d -- regreet`) |
| 🖼️ 准备登录背景 / Prepare background | 把 KamiDream 背景图从 `lightdm-webkit` 主题目录拷到 `/etc/greetd/background.png`（已存在则跳过）；之后卸掉 LightDM 也不会丢壁纸 / Copies the KamiDream background to `/etc/greetd/background.png` (skipped when present), so removing LightDM later won't break the greeter |
| 🖼️ `/etc/greetd/regreet.toml` | 背景指向 `/etc/greetd/background.png`（`fit = "Cover"`），GTK 基底用深色变体（`application_prefer_dark_theme = true`）；背景不存在时只写 GTK 设置 / Points the background at `/etc/greetd/background.png` with `fit = "Cover"` and selects the **dark** GTK base variant; only the GTK settings are written when the image is missing |
| 🎨 `/etc/greetd/regreet.css` | **照 LightDM KamiDream 主题对齐**的 GTK4 样式表：白色半透明玻璃卡片 / 顶栏 / 下拉层、白字 + 淡蓝强调色 `#4fc3f7`（直接取自主题 `css/style.css` 的 `--accent`）、**长方形输入框（与 User 下拉框同尺寸同风格）**、6–18px 圆角、4px 细白滚动条、错误色 `#ef5350`；**用户名切换、会话选择、右侧按钮与密码框同一套玻璃底**（规避 GTK 深色主题的黑底）；**尺寸按主屏逻辑分辨率自动换算**（卡片宽 / 内边距 / 输入框尺寸，以 1645 宽为基准、限制在 0.85–1.35 倍）；已存在的非 ArchInit 样式会被保留以尊重自定义 / GTK4 stylesheet **matching the LightDM KamiDream theme**: white translucent glass card / clock / dropdown, white text with the theme's `#4fc3f7` accent, **rectangular inputs matching the User dropdown (same size and style)**, 6–18px radii, 4px white scrollbar and `#ef5350` error color; the **user switcher, session selector and side buttons share the same glass background as the password field** (so GTK's dark defaults never show through); **sizes are derived from the primary display's logical width** (card width / paddings / input size, based on 1645 wide, clamped to 0.85–1.35×); a pre-existing non-ArchInit stylesheet is left untouched |
| 🔀 切换服务 / Switch services | `systemctl enable greetd`，若 `lightdm` 仍存在则 `systemctl disable lightdm`（已卸载则跳过，不会报错），然后校验 `greetd` 已启用、配置里含 `regreet` / Enables greetd, disables lightdm only when it still exists (skipped otherwise), then verifies |

#### Step 3: 更换登录背景图 / Change Login Background

> 登录器背景就是 `/etc/greetd/background.png`；这一步换成你指定的图片，并保证 `regreet.toml` 指向它。
> The greeter background is just `/etc/greetd/background.png`; this step replaces it with an image you type and keeps `regreet.toml` pointing at it.

| 操作 / Action | 说明 / Description |
| --- | --- |
| ⌨️ 输入图片路径 / Enter image path | 弹出输入框（直接打字），`Tab` 或 `Enter` 确认、`Esc` 取消；支持 `~` 展开 / Type the path, `Tab`/`Enter` to confirm, `Esc` to cancel; `~` is expanded |
| ✅ 校验 / Validate | 路径不是文件时留在输入框并给黄色提示，不会动现有背景 / Stays in the prompt with a notice when the path is not a file |
| 📦 复制并授权 / Copy & set mode | 以 root `install -Dm644` 到 `/etc/greetd/background.png`，`greeter` 用户一定读得到（图片放自己家目录也行）/ Copies as root with mode 644 so the `greeter` user can read it, even from your home |
| ⚙️ `/etc/greetd/regreet.toml` | 只改 `[background] path` 一行；段不存在则补上（`fit = "Cover"`），其余配置原样保留 / Only rewrites the `path` line (adds the section when missing); everything else is kept |

> 生效：**注销**（退出 niri 后 greetd 会重新拉起登录器）或重启。想完整显示整张图就把 `fit` 改成 `Contain`，拉伸填满用 `Fill`。
> Apply by logging out (greetd restarts the greeter) or rebooting. Use `fit = "Contain"` for letterboxing or `"Fill"` to stretch.

#### Step 4: 解锁密钥环 / Unlock Keyring at Login

| 操作 / Action | 说明 / Description |
| --- | --- |
| 🔑 检查依赖 / Check deps | `gnome-keyring` 未安装时自动装；`/usr/lib/security/pam_gnome_keyring.so` 缺失则中止 / Installs `gnome-keyring` when missing, aborts if the PAM module is absent |
| 📝 写入 `/etc/pam.d/greetd` | 追加 `-auth optional pam_gnome_keyring.so` 与 `-session optional pam_gnome_keyring.so auto_start`（放在 `include` 之后，等 `pam_systemd` 建好 `/run/user/<uid>`）；首次写入前备份为 `/etc/pam.d/greetd.archinit.bak`，已含该模块则不重复写 / Appends the two `pam_gnome_keyring` lines after the includes, backs up to `.archinit.bak` once, and skips when already present |
| ✅ 校验 / Verify | 文件中必须出现两次 `pam_gnome_keyring.so`（auth + session）/ The file must mention `pam_gnome_keyring.so` twice |

> 为什么需要这步：LightDM 的 `/etc/pam.d/lightdm` 自带 `pam_gnome_keyring.so`，登录时密码顺手把「登录密钥环」解锁了；`greetd` 的 PAM 栈（`system-local-login`）没有它，所以换成 greetd 后每次开机都会弹「输入密钥环密码」。补上这两行即可恢复开机免输。
> Why this step: LightDM's PAM file ships `pam_gnome_keyring.so`, so the login password also unlocks the *login* keyring; greetd's stack (`system-local-login`) doesn't include it, hence the keyring prompt on every boot. These two lines restore it.

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

#### Step 4: 卸除 LightDM / Remove LightDM

> 顺序说明：先跑「登录管理器 → 安装」+「配置并启用」（后者会自己 `enable greetd` 并停用 lightdm），再来卸除。**不需要先手动停 LightDM** —— 这一步自己会 `systemctl disable lightdm` 后再卸载；如果 greetd 已装好也配好了、只是没启用，这里会顺手帮你启用。greetd 没装或没配置时才中止。
> Order: run Login Manager → Install, then Configure & enable (it enables greetd and disables lightdm itself), then remove. **You never have to stop LightDM manually** — this step disables it right before uninstalling; if greetd is installed and configured but not yet enabled, it enables it here. It only aborts when greetd is missing or not configured.

| 操作 / Action | 说明 / Description |
| --- | --- |
| ✅ 确认/启用 greetd / Ensure greetd | 已启用直接过；已装好且写过 ReGreet 配置则顺手 `systemctl enable greetd`；没装或没配置才中止（先跑「登录管理器」）/ Passes when enabled; enables it when greetd is installed and the ReGreet config exists; aborts only when greetd is missing or unconfigured |
| 🖼️ 保留登录背景图 / Keep background | 确认 `/etc/greetd/background.png` 存在（缺了就从 KamiDream 主题目录拷一份），删主题目录后登录界面照样有壁纸 / Ensures `/etc/greetd/background.png` exists so the greeter keeps its wallpaper |
| ⏹️ 停用 lightdm / Disable service | `systemctl disable lightdm`（没装也不报错）/ No-op when not installed |
| 🗑️ 卸载包 / Remove packages | 用 `pacman -Rns` 卸掉已安装的 `lightdm`、`lightdm-gtk-greeter`、`lightdm-webkit2-greeter` / Removes whichever of those packages are installed |
| 🧹 清理目录 / Clean up | 删除 `/usr/share/lightdm-webkit`、`/usr/local/share/lightdm-webkit`、`/etc/lightdm` / Deletes those directories |
| ✅ 校验 / Verify | 确认包已卸载、`lightdm` 不再设为开机启动 / Confirms the packages are gone and lightdm is no longer enabled |

> 卸除后开机直接进 greetd + ReGreet。本工具不再管理 LightDM，需要装回时自己 `sudo pacman -S lightdm lightdm-gtk-greeter`。
> After removal the boot goes straight to greetd + ReGreet. This tool no longer manages LightDM; install `lightdm lightdm-gtk-greeter` manually if you ever need it back.

---

### 🔀 应用后端切换 / App Backend Toggle

> 对应 `archinit.py` 主菜单「应用后端切换 / App Backend Toggle」分类；实现见 [`ZClass/steps/backend.py`](ZClass/steps/backend.py)。
> Maps to the "App Backend Toggle" category in `archinit.py`; implementation in [`ZClass/steps/backend.py`](ZClass/steps/backend.py).

#### Step 1: 选择应用启动 / Pick App & Launch

> 一个步骤搞定：列出全部已安装应用（`.desktop`）用 ↑/↓ 选择；**列表里没有的应用也可以直接输入命令**，按 `Tab`（或无匹配时按 `Enter`）就当命令用。
> One step does it all: lists every installed app (`.desktop`) for ↑/↓ selection; **apps missing from the list can be typed in directly** and used as a command with `Tab` (or `Enter` when nothing matches).

| 操作 / Action                       | 说明 / Description |
| ----------------------------------- | ------------------ |
| 🔎 扫描范围 / Scan scope         | `/usr/share/applications`、`/usr/local/share/applications`、`~/.local/share/applications`（含子目录）；仅保留 `Type=Application` 且非 `NoDisplay=true` 的条目，去重后按名称排序 / Scans the standard `applications` dirs recursively, keeping only `Type=Application` entries with `NoDisplay` unset, deduplicated and sorted |
| 📋 列表界面 / List view          | 每项显示「名称 (可执行名)」，右上角显示 `已过滤/总数`，超出屏幕自动滚动 / Each row shows `Name (executable)` with a `filtered/total` counter and automatic scrolling |
| ↕️ 上下选择 / Move               | `↑`/`↓` 移动，`PgUp`/`PgDn` 每次翻 10 条，`Home`/`End` 到首尾 / `↑`/`↓` to move, `PgUp`/`PgDn` by 10, `Home`/`End` to jump |
| 🏷️ 输入过滤 / Type to filter   | 直接敲字实时过滤（匹配 `Name`、`Name[*]`、`GenericName` 与可执行名，如 `virt` → 「虚拟系统管理器」）；`Backspace` 删除过滤字符 / Type to filter live (matches `Name`, `Name[*]`, `GenericName`, executable); `Backspace` removes characters |
| ⌨️ 列表外的命令 / Command not in list | 输入后按 `Tab` 直接用该文字当命令；若过滤结果为空，直接按 `Enter` 也会当命令。解析失败时在该界面顶部显示黄色提示（不打印到终端），修改输入即自动清除 / Press `Tab` to use the typed text as a command; with no match, `Enter` does the same. A failed lookup shows a yellow notice at the top of the same screen (nothing printed to the terminal), cleared as soon as you edit the input |
| 🎯 选择平台 / Choose backend      | 与选择应用同一个光标列表：`↑`/`↓` 选中 `Wayland`（原生）或 `X11 (XWayland)`（兼容），`Enter` 确定；`Esc` **返回选应用**，再按 `Esc` 则退出步骤。默认高亮上次选过的平台 / Same cursor list: `↑`/`↓` between backends, `Enter` confirms; `Esc` **goes back to app picking**, `Esc` again leaves the step; the last used backend is pre-selected |
| 🚀 启动应用 / Launch             | 用对应的 `QT_QPA_PLATFORM`/`GDK_BACKEND`/`SDL_VIDEODRIVER`/`MOZ_ENABLE_WAYLAND`/`ELECTRON_OZONE_PLATFORM_HINT` 环境变量在后台启动（独立会话，不阻塞本工具）；结果显示在主界面底部状态行：`🚀 <平台> · <应用> (pid …) · <命令>` / Launch detached (own session, non-blocking) with the matching backend env vars; the result appears as a status line in the main view: `🚀 <backend> · <app> (pid …) · <command>` |
| 🧠 选择记忆 / Selection memory | 列表与平台选择都会记住上次的选择：按 `Esc` 返回后重新打开、或再次执行本步骤时，会高亮上次选中的应用（并恢复上次的过滤词）与上次选的平台 / Both lists remember the last choice: after `Esc` or when the step runs again, the previously picked app (and its filter word) and the previously picked backend are highlighted |
| ↩️ 取消行为 / Cancel behaviour  | 列表里 `q` 是**过滤字符**（不是取消键，与 fzf 一致），取消统一用 `Esc`；按 `Esc` 后步骤以「已取消」退出（底部状态行提示），不显示 `failed` / Inside the list `q` is a **filter character** (like fzf), so cancelling is always `Esc`; the step exits as "cancelled" (shown in the status line) rather than "failed" |

> 实现提示：选择器在 [`ZClass/picker.py`](ZClass/picker.py) 中实现，方向键转义序列（`\E[A` / `\EOA` 等）由自身解析，不依赖 terminfo，因此在 kitty、foot、xterm 等不同终端下行为一致；它**复用主界面窗口**（不嵌套 `initscr`/`endwin`），退出后方向键不会失效。`.desktop` 的 `Exec` 行会去掉 field code、剥掉 `env VAR=VAL` 前缀、非绝对路径用 `which` 解析，启动时传入完整 argv。
> Implementation note: the picker lives in [`ZClass/picker.py`](ZClass/picker.py) and decodes arrow-key escape sequences (`\E[A` / `\EOA`, etc.) itself instead of relying on terminfo, so it behaves the same in kitty, foot, xterm, etc. It **reuses the main window** (no nested `initscr`/`endwin`), so arrow keys keep working after it closes. `Exec` lines are sanitized (field codes removed, `env VAR=VAL` prefix stripped, non-absolute program resolved via `which`) and the full argv is launched.

---

## 🔧 自定义与扩展 / Customization

- **选择步骤 / Choose steps**：[`archinit.py`](archinit.py) 提供统一交互式菜单（`curses`）：主菜单选择 9 大分类，分类内用 ↑/↓ 选择步骤，Enter 执行，q/Esc 返回 / [`archinit.py`](archinit.py) provides a unified interactive menu (`curses`): pick one of 9 categories from the main menu, then use ↑/↓ to select a step, Enter to execute, q/Esc to go back.
- **自动配置 / Automated edits**：所有配置修改（locale、pacman.conf、mkinitcpio.conf、.zshrc 等）均由脚本自动完成（`sed` 或 Python 直接读写文件），无需手动编辑 / All configuration changes (locale, pacman.conf, mkinitcpio.conf, .zshrc, etc.) are applied automatically (`sed` or direct file I/O in Python) — no manual editing required.
- **添加自己的包 / Add your own packages**：步骤现在以「任务面板」形式执行，改 `ZClass/steps/` 里对应任务的 `Shell.pacman("…")` 包列表即可（如 `basic.py`、`gpu.py`）；新增的每条任务写成 `(显示名称, callable)`，callable 返回 `True/False` 或 `(bool, 失败原因)` / Steps run as a **task panel**: edit the `Shell.pacman("…")` lists inside the tasks under `ZClass/steps/` (e.g. `basic.py`, `gpu.py`). Each task is `(label, callable)` where the callable returns `True/False` or `(bool, reason)`.

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
