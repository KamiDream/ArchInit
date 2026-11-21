"""分类：LightDM 配置 / LightDM WebKit2 Greeter。"""
import os
import shutil
import tempfile

from ..shell import Shell
from ..style import Style


class LightDmSteps:
    THEME_NAME = "KamiDream_Theme"
    THEMES_DIR = "/usr/share/lightdm-webkit/themes"
    THEME_REPO = "https://github.com/KamiDream/LdmWk2Theme.git"
    REQUIRED = ("index.html", "js/main.js", "css/style.css")

    @staticmethod
    def greeter():
        print(">>> 安装 lightdm-webkit2-greeter...")
        print("    Installing lightdm-webkit2-greeter...")
        Shell.run("sudo pacman -S --needed --noconfirm lightdm-webkit2-greeter")
        print()
        print(Style.green_bold("    ✅ lightdm-webkit2-greeter 安装完成 / installed successfully."))
        return True

    # ── 主题 ──
    @classmethod
    def theme_path(cls):
        return os.path.join(cls.THEMES_DIR, cls.THEME_NAME)

    @classmethod
    def theme_installed(cls):
        return os.path.isfile(os.path.join(cls.theme_path(), "index.html"))

    @classmethod
    def theme(cls):
        target = cls.theme_path()
        clone = os.path.join(tempfile.gettempdir(), cls.THEME_NAME + ".clone")

        print(">>> 克隆主题到临时目录（失败不会影响已安装的主题）...")
        print("    Cloning into a temp dir (a failure won't break the installed theme)...")
        if not Shell.which("git"):
            print(Style.red_bold("    ❌ 未安装 git，请先安装 / git is required: sudo pacman -S git"))
            return False
        if os.path.isdir(clone):
            shutil.rmtree(clone, ignore_errors=True)
        if Shell.run(f'git clone --depth 1 {cls.THEME_REPO} "{clone}"') != 0:
            print(Style.red_bold("    ❌ 克隆失败，原有主题保持不变 / Clone failed, existing theme kept."))
            return False

        missing = [f for f in cls.REQUIRED if not os.path.isfile(os.path.join(clone, f))]
        if missing:
            print(Style.red_bold(f"    ❌ 主题不完整，缺少 / Incomplete theme, missing: {', '.join(missing)}"))
            print(f"       临时目录 / temp dir: {clone}")
            return False
        shutil.rmtree(os.path.join(clone, ".git"), ignore_errors=True)

        print()
        print(f">>> 安装到 {target} ...")
        print("    Installing...")
        Shell.run(f"sudo mkdir -p {cls.THEMES_DIR}")
        Shell.run(f"sudo rm -rf {target}")
        if Shell.run(f'sudo cp -r "{clone}" "{target}"') != 0:
            print(Style.red_bold("    ❌ 复制失败 / Copy failed."))
            return False
        shutil.rmtree(clone, ignore_errors=True)

        if not cls.theme_installed():
            print(Style.red_bold(f"    ❌ 安装后找不到 {target}/index.html"))
            print("       greeter 会报 “An error was detected in the current theme”")
            return False

        print()
        print(Style.green_bold(f"    ✅ KamiDream 主题已安装/更新到 {target}"))
        print("    Theme installed/updated successfully.")
        print()
        print("    🖼️  如需替换背景图片，请替换以下文件：")
        print(f"       {target}/assets/background.png")
        print("       To replace the background image, replace the file above with your own.")
        return True

    # ── 启用 ──
    @classmethod
    def enable(cls):
        if not cls.theme_installed():
            print(Style.red_bold(f"    ❌ 未找到主题 / Theme not installed: {cls.theme_path()}"))
            print("       先执行「安装 KamiDream 主题」步骤；否则 greeter 会报")
            print("       “An error was detected in the current theme that could interfere")
            print("        with the system login process.”")
            print("       Run the theme step first, otherwise the greeter shows that error.")
            return False

        print(">>> 配置 /etc/lightdm/lightdm.conf...")
        print("    Configuring /etc/lightdm/lightdm.conf...")
        Shell.run("sudo mkdir -p /etc/lightdm")
        conf = "/etc/lightdm/lightdm.conf"
        # 同时处理“已注释”和“已启用”两种写法，避免留下重复行
        if Shell.ok(f"grep -Eq '^#?greeter-session=lightdm-webkit2-greeter' {conf}"):
            Shell.run(f"sudo sed -i 's|^#\\?greeter-session=lightdm-webkit2-greeter.*|"
                      f"greeter-session=lightdm-webkit2-greeter|' {conf}")
        elif Shell.read_file(conf).find("[Seat:*]") >= 0:
            Shell.run(f"sudo sed -i '/^\\[Seat:\\*\\]/a greeter-session=lightdm-webkit2-greeter' {conf}")
        else:
            Shell.sudo_write(conf, "[Seat:*]\ngreeter-session=lightdm-webkit2-greeter\n", append=True)
        print("    /etc/lightdm/lightdm.conf 已配置 / configured.")
        print()
        print(">>> 配置 /etc/lightdm/lightdm-webkit2-greeter.conf...")
        print("    Configuring /etc/lightdm/lightdm-webkit2-greeter.conf...")
        wconf = "/etc/lightdm/lightdm-webkit2-greeter.conf"
        if Shell.ok(f"grep -q '^webkit_theme' {wconf} 2>/dev/null"):
            Shell.run(f"sudo sed -i 's|^webkit_theme\\s*=.*|webkit_theme        = {cls.THEME_NAME}|' {wconf}")
            print(f"    webkit_theme 已更新为 {cls.THEME_NAME} / updated.")
        else:
            Shell.sudo_write(wconf, f"[greeter]\nwebkit_theme        = {cls.THEME_NAME}\n", append=True)
            print("    webkit_theme 已添加 / added.")
        print("    /etc/lightdm/lightdm-webkit2-greeter.conf 已配置 / configured.")
        print()
        print(Style.green_bold("    ✅ LightDM 配置完成 / Configuration complete."))
        print()
        print("=" * 121)
        print(Style.yellow("   ⚠️  请重启系统以应用 LightDM 登录管理器 / Please reboot to apply LightDM"))
        print("     重启命令 / Reboot command: sudo reboot")
        print("     或 / Or: sudo systemctl reboot")
        print("=" * 121)
        print()
        return Shell.prompt("按 Enter 继续 / Press Enter to continue")

    @staticmethod
    def emergency():
        print(">>> 注释 /etc/lightdm/lightdm.conf 中的 greeter-session=lightdm-webkit2-greeter...")
        print("    Commenting out greeter-session=lightdm-webkit2-greeter in /etc/lightdm/lightdm.conf...")
        conf = "/etc/lightdm/lightdm.conf"
        if Shell.ok(f"grep -q '^greeter-session=lightdm-webkit2-greeter' {conf} 2>/dev/null"):
            Shell.run(f"sudo sed -i 's|^greeter-session=lightdm-webkit2-greeter|#greeter-session=lightdm-webkit2-greeter|' {conf}")
            print(Style.green_bold("    ✅ 已注释 greeter-session 行 / Commented out."))
        else:
            print(Style.yellow("    ⏭️  未找到 greeter-session=lightdm-webkit2-greeter，可能已被注释 / Not found, may already be commented."))
        print()
        print("=" * 121)
        print(Style.yellow("   ⚠️  请重启系统以恢复默认 LightDM Greeter / Please reboot to restore default LightDM greeter"))
        print("     重启命令 / Reboot command: sudo reboot")
        print("     或 / Or: sudo systemctl reboot")
        print("=" * 121)
        print()
        return Shell.prompt("按 Enter 继续 / Press Enter to continue")
