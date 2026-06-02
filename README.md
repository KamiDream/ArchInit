# 🚀 Arch Linux 初始化脚本（niri_init）

基于 [Niri](https://github.com/YaLTeR/niri) 平铺窗口管理器的 **Arch Linux 开发环境一键初始化脚本**。  
适用于新装 Arch Linux 后，快速搭建包含中文输入、虚拟化、NVIDIA 驱动、终端美化等完整开发工作环境。

---

## 📋 功能概览

| 步骤 | 内容 | 说明 |
|------|------|------|
| **第 0 步** | 🖥️ 核心桌面环境 | 安装 Niri 平铺窗口管理器、DMS Shell、Alacritty、Matugen、Cava 等 |
| **第 1 步** | 🧰 基础初始化 | 安装常用软件、配置中文 locale、安装中英文 / Nerd 字体 |
| **第 2 步** | 💻 KVM 虚拟化 | 安装 QEMU/virt-manager，启用 libvirtd，配置虚拟网络 |
| **第 3 步** | 🎮 NVIDIA 驱动 | 配置 multilib/archlinuxcn 源，安装 NVIDIA 闭源驱动 (nvidia-dkms) |
| **第 4 步** | 🧪 DMS (Dank Linux) | 安装 Dank Linux 包管理器 |
| **第 5 步** | 🎨 终端美化 | 安装 Zsh + 插件、配置 Kitty 终端、选择 Nerd 字体 |
| **第 6 步** | ⚡ Zim + Powerlevel10k | 安装 Zim 框架与 Powerlevel10k 主题，打造高效 Zsh 环境 |

---

## 🖥️ 系统要求

- **Arch Linux**（已安装并正常启动）
- 已拥有 `sudo` 权限的普通用户（**不要以 root 身份运行**）
- 网络连接正常

---

## 🚀 使用方法

```bash
# 1. 克隆或下载本仓库
git clone https://github.com/your-username/your-repo.git
cd your-repo

# 2. 赋予执行权限
chmod +x niri_init.sh

# 3. 运行脚本（普通用户 + sudo）
./niri_init.sh
```

> ⚠️ **注意**：脚本采用**交互式**执行，每一步都会询问是否执行（`Y/n`），您可以选择跳过某些步骤。  
> 部分步骤会打开 vim/kate 编辑器要求手动修改配置文件，**请按提示完成编辑后保存退出**。

---

## 📦 各步骤详解

### 第 0 步：核心桌面环境（Niri + DMS）

| 操作 | 说明 |
|------|------|
| 安装 Niri 及周边组件 | `niri`（平铺窗口管理器）、`xwayland-satellite`（XWayland 支持）、`xdg-desktop-portal-gnome` / `xdg-desktop-portal-gtk`（桌面门户）、`alacritty`（GPU 加速终端）、`dms-shell-niri`（DMS Shell for Niri）、`matugen`（Material You 配色生成）、`cava`（终端音频可视化）、`qt6-multimedia-ffmpeg`（Qt6 多媒体后端） |
| 注册 DMS 服务 | 将 DMS 添加为 `niri.service` 的 user service 依赖，开机自动启动 DMS |

### 第 1 步：基础初始化

| 操作 | 说明 |
|------|------|
| `pacman` 安装基础包 | `fastfetch`, `fcitx5-im` (中文输入法), `fcitx5-rime`, `fuse2`, `ntfs-3g`, `git`, `quickshell`, `flatseal`, `dolphin`, `kate`, `firefox` |
| 配置 locale | 编辑 `/etc/locale.gen` 启用 `zh_CN.UTF-8`，运行 `locale-gen`，设置系统 locale |
| 安装字体 | `wqy-microhei`, `wqy-zenhei`, `noto-fonts-cjk`, `ttf-jetbrains-mono-nerd` 等中英文 / Nerd 字体 |

### 第 2 步：KVM 虚拟化

| 操作 | 说明 |
|------|------|
| 安装 KVM 组件 | `qemu-full`, `virt-manager`, `swtpm`, `dnsmasq` |
| 启用服务 | `libvirtd` 开机自启并立即启动 |
| 配置网络 | 启动并设置 `default` 虚拟网络为自动启动 |
| 用户权限 | 将当前用户加入 `libvirt` 组（需重新登录生效） |

### 第 3 步：NVIDIA 驱动

| 操作 | 说明 |
|------|------|
| 安装内核头文件 | `linux-headers`, `linux-zen-headers` |
| 配置 pacman 源 | 启用 `[multilib]`、添加 `[archlinuxcn]` 源（中科大、清华、哈工大、华为云镜像） |
| 安装 AUR 助手 | `base-devel`, `yay`, `paru` |
| 安装 NVIDIA 驱动 | `nvidia-dkms`, `nvidia-utils`, `nvidia-settings` |
| 配置 initramfs | 在 `/etc/mkinitcpio.conf` 中添加 `nvidia` 相关模块，重新生成 initramfs |

### 第 4 步：DMS (Dank Linux)

安装 [Dank Linux](https://install.danklinux.com) 包管理工具（用于管理 Flatpak 等应用）。

### 第 5 步：终端环境配置

| 操作 | 说明 |
|------|------|
| 安装 Zsh 及插件 | `zsh`, `zsh-autosuggestions`, `zsh-syntax-highlighting`, `zsh-completions` |
| 更改默认 Shell | 将当前用户默认 shell 切换为 Zsh |
| 配置 `.zshrc` | 添加 `fastfetch` 启动信息及 Zsh 插件加载 |
| 配置 Kitty 终端 | 设置光标尾迹、闪烁效果 |
| 选择字体 | 使用 `kitten choose-fonts` 交互式选择 `JetBrains Mono` Nerd 字体 |

### 第 6 步：Zim 框架 + Powerlevel10k

| 操作 | 说明 |
|------|------|
| 安装 Zim 框架 | 通过官方安装脚本一键安装 |
| 配置 `.zimrc` | 添加 `zmodule romkatv/powerlevel10k` 启用 Powerlevel10k 主题 |

---

## 🔧 自定义与扩展

- **跳过步骤**：每个步骤开始前都会询问，输入 `n` 即可跳过。
- **手动编辑**：部分配置（locale、pacman.conf、mkinitcpio.conf 等）需要手动编辑，脚本会打开编辑器等待完成。
- **添加自己的包**：可直接修改 `niri_init.sh` 中的 `pacman -S` 列表，增删所需软件包。

---

## ❓ 常见问题

### Q：运行脚本后需要做什么？

1. **重新登录或重启系统**，使组权限（libvirt）和 shell 更改生效。
2. 运行 `fastfetch` 查看系统信息，确认环境正常。
3. 若配置了 fcitx5，在桌面环境中添加输入法并启用 Rime。

### Q：Kitty 字体选择器无法启动？

确保已安装 Kitty：`sudo pacman -S kitty`，或在脚本第 5 步前手动安装。

### Q：NVIDIA 驱动安装后黑屏？

检查 `/etc/mkinitcpio.conf` 中的 `MODULES` 配置是否正确，重新运行 `sudo mkinitcpio -P` 并重启。

### Q：locales 未生效？

请确保 `/etc/locale.gen` 中 `zh_CN.UTF-8` 已取消注释，并手动运行：
```bash
sudo locale-gen
sudo localectl set-locale LANG=zh_CN.UTF-8
```

---

## 📝 许可证

本项目仅供学习和个人使用。如有问题或建议，欢迎提交 Issue 或 PR。

---

## 🙏 致谢

- [Niri](https://github.com/YaLTeR/niri) — 滚动式平铺窗口管理器
- [Zim](https://github.com/zimfw/zimfw) — Zsh 插件框架
- [Powerlevel10k](https://github.com/romkatv/powerlevel10k) — Zsh 主题
- [Kitty](https://sw.kovidgoyal.net/kitty/) — GPU 加速终端
- [Dank Linux](https://install.danklinux.com) — 包管理工具
