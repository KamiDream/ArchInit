"""分类：LightDM 配置 / LightDM WebKit2 Greeter。

所有步骤都用 TaskView 在界面内执行，命令输出不落到终端；
命令统一加 `sudo -n`：凭证过期时快速失败而不是在无提示的状态下卡住。
"""
import os
import shutil
import subprocess
import tempfile

from ..shell import Shell
from ..status import Status
from ..taskview import TaskView


def _tail(text, limit=64):
    """把命令输出压缩成一行失败说明。"""
    if "password is required" in text or "askpass" in text:
        return "sudo 凭证过期 / sudo expired"
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    return lines[-1][:limit] if lines else ""


def _sudo_write(path, content, append=False):
    """以 root 写文件（非交互），返回 (ok, 错误信息)。"""
    args = ["sudo", "-n", "tee"] + (["-a"] if append else []) + [path]
    r = subprocess.run(args, input=content, text=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=False)
    return r.returncode == 0, _tail(r.stderr or "")


class LightDmSteps:
    THEME_NAME = "KamiDream_Theme"
    THEMES_DIR = "/usr/share/lightdm-webkit/themes"           # greeter 查找路径
    STORE_DIR = "/usr/local/share/lightdm-webkit/themes"      # 真正存放主题（不受包管理影响）
    THEME_REPO = "https://github.com/KamiDream/LdmWk2Theme.git"
    REQUIRED = ("index.html", "js/main.js", "css/style.css")

    @classmethod
    def theme_path(cls):
        return os.path.join(cls.THEMES_DIR, cls.THEME_NAME)

    @classmethod
    def store_path(cls):
        return os.path.join(cls.STORE_DIR, cls.THEME_NAME)

    @classmethod
    def theme_installed(cls):
        """主题可被 greeter 找到（允许上一步留下的软链）。"""
        return os.path.isfile(os.path.join(cls.theme_path(), "index.html"))

    # ── Step 1: 安装 greeter ──
    @classmethod
    def greeter(cls):
        def install():
            rc, out = Shell.capture_all(
                "sudo -n pacman -S --needed --noconfirm lightdm-webkit2-greeter")
            if rc == 0 and Shell.installed("lightdm-webkit2-greeter"):
                return True
            return False, _tail(out) or "安装失败 / install failed"

        ok = TaskView.run("LightDM 配置 · 安装 greeter / Install greeter", [
            ("安装 lightdm-webkit2-greeter", install),
        ])
        Status.set("✅ lightdm-webkit2-greeter 已安装 / installed" if ok
                   else "❌ lightdm-webkit2-greeter 安装失败 / install failed")
        return ok

    # ── Step 2: 安装/更新主题 ──
    @classmethod
    def theme(cls):
        target = cls.theme_path()
        store = cls.store_path()
        staging = store + ".new"
        clone = os.path.join(tempfile.gettempdir(), cls.THEME_NAME + ".clone")

        def prepare():
            if not Shell.which("git"):
                return False, "需要 git / git required"
            if os.path.isdir(clone):
                shutil.rmtree(clone, ignore_errors=True)
            ok, out = Shell.quiet(f'git clone --depth 1 {cls.THEME_REPO} "{clone}"')
            if not ok:
                return False, _tail(out) or "克隆失败 / clone failed"
            missing = [f for f in cls.REQUIRED if not os.path.isfile(os.path.join(clone, f))]
            if missing:
                return False, "缺少 " + ", ".join(missing)
            shutil.rmtree(os.path.join(clone, ".git"), ignore_errors=True)
            return True

        def replace():
            # 主题实体放 /usr/local（包管理不管），在 /usr/share 下只留一个软链：
            # 这样 lightdm-webkit2-greeter 升级/重装都不会影响主题。
            for cmd, why in (
                (f"sudo -n mkdir -p {cls.STORE_DIR}", "创建目录失败 / mkdir failed"),
                (f"sudo -n rm -rf {staging}", "清理暂存目录失败 / staging cleanup failed"),
                (f'sudo -n cp -r "{clone}" "{staging}"', "复制失败 / copy failed"),
                (f"sudo -n rm -rf {store}", "删除旧主题失败 / rm failed"),
                (f"sudo -n mv {staging} {store}", "替换失败 / replace failed"),
                (f"sudo -n mkdir -p {cls.THEMES_DIR}", "创建主题目录失败 / mkdir failed"),
                (f"sudo -n rm -rf {target}", "删除旧链接失败 / rm failed"),
                (f"sudo -n ln -sfn {store} {target}", "创建软链失败 / symlink failed"),
            ):
                rc, out = Shell.capture_all(cmd)
                if rc != 0:
                    return False, _tail(out) or why
            shutil.rmtree(clone, ignore_errors=True)
            return True

        def verify():
            if cls.theme_installed():
                return True
            return False, "找不到 index.html / index.html missing"

        ok = TaskView.run("LightDM 配置 · 安装主题 / Install theme", [
            ("克隆 KamiDream 主题 / clone theme", prepare),
            ("替换已安装主题 / replace theme", replace),
            ("确认安装结果 / verify install", verify),
        ])
        Status.set("✅ KamiDream 主题已更新（实体在 /usr/local，/usr/share 下为软链）/ theme updated" if ok
                   else "❌ 主题未更新 / theme not updated")
        return ok

    # ── Step 3: 启用配置 ──
    @classmethod
    def enable(cls):
        if not cls.theme_installed():
            Status.set("❌ 未找到主题，请先执行 Step 2 / theme missing")
            return False

        conf = "/etc/lightdm/lightdm.conf"
        wconf = "/etc/lightdm/lightdm-webkit2-greeter.conf"

        def lightdm_conf():
            if Shell.ok(f"grep -Eq '^#?greeter-session=lightdm-webkit2-greeter' {conf}"):
                rc, out = Shell.capture_all(
                    "sudo -n sed -i 's|^#\\?greeter-session=lightdm-webkit2-greeter.*|"
                    f"greeter-session=lightdm-webkit2-greeter|' {conf}")
                return (rc == 0), _tail(out)
            if Shell.read_file(conf).find("[Seat:*]") >= 0:
                rc, out = Shell.capture_all(
                    f"sudo -n sed -i '/^\\[Seat:\\*\\]/a greeter-session=lightdm-webkit2-greeter' {conf}")
                return (rc == 0), _tail(out)
            return _sudo_write(conf, "[Seat:*]\ngreeter-session=lightdm-webkit2-greeter\n", append=True)

        def webkit_conf():
            if Shell.ok(f"grep -q '^webkit_theme' {wconf} 2>/dev/null"):
                rc, out = Shell.capture_all(
                    f"sudo -n sed -i 's|^webkit_theme\\s*=.*|webkit_theme        = {cls.THEME_NAME}|' {wconf}")
                return (rc == 0), _tail(out)
            return _sudo_write(wconf, f"[greeter]\nwebkit_theme        = {cls.THEME_NAME}\n", append=True)

        def verify():
            if not Shell.ok(f"grep -q '^greeter-session=lightdm-webkit2-greeter' {conf}"):
                return False, "greeter-session 未写入 / not written"
            if not Shell.ok(f"grep -q 'webkit_theme.*{cls.THEME_NAME}' {wconf}"):
                return False, "webkit_theme 未写入 / not written"
            return True

        ok = TaskView.run("LightDM 配置 · 启用 / Enable", [
            ("写入 lightdm.conf（greeter-session）", lightdm_conf),
            ("写入 lightdm-webkit2-greeter.conf（webkit_theme）", webkit_conf),
            ("校验配置 / verify config", verify),
        ])
        Status.set("✅ LightDM 已配置，重启后生效 / configured — reboot to apply" if ok
                   else "❌ LightDM 配置失败 / configuration failed")
        return ok

    # ── Step 4: 黑屏救急 ──
    @classmethod
    def emergency(cls):
        conf = "/etc/lightdm/lightdm.conf"

        def comment_out():
            if not Shell.ok(f"grep -q '^greeter-session=lightdm-webkit2-greeter' {conf} 2>/dev/null"):
                return True  # 本来就没启用
            rc, out = Shell.capture_all(
                f"sudo -n sed -i 's|^greeter-session=lightdm-webkit2-greeter|"
                f"#greeter-session=lightdm-webkit2-greeter|' {conf}")
            if rc != 0:
                return False, _tail(out)
            if not Shell.ok(f"grep -q '^#greeter-session=lightdm-webkit2-greeter' {conf}"):
                return False, "注释未生效 / not commented"
            return True

        ok = TaskView.run("LightDM 配置 · 黑屏救急 / Emergency revert", [
            ("注释 greeter-session（恢复默认 greeter）", comment_out),
        ])
        Status.set("✅ 已恢复默认 greeter，重启后生效 / reverted — reboot to apply" if ok
                   else "❌ 恢复失败 / failed to revert")
        return ok
