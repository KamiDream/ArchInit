"""分类：登录管理器 / Login Manager（greetd + ReGreet）。

ReGreet 是 Wayland 的 GTK4 登录器，需要一个合成器承载，这里按上游推荐用 cage。
配置/样式都写在 /etc/greetd 下；坐标与开关都通过任务面板展示。
"""
import os
import re
import shlex
import subprocess

from ..model import CANCELLED
from ..picker import FreeText, Picker
from ..shell import Shell
from ..status import Status
from ..taskview import TaskView

GREETD_DIR = "/etc/greetd"
GREETD_CONF = os.path.join(GREETD_DIR, "config.toml")
REGREET_CONF = os.path.join(GREETD_DIR, "regreet.toml")
REGREET_CSS = os.path.join(GREETD_DIR, "regreet.css")

# 背景图存到 /etc/greetd 下：卸掉 LightDM/主题后登录界面依旧有壁纸。
# 首次配置时从 KamiDream 主题里拷一份，之后就不再依赖 lightdm-webkit 目录。
BACKGROUND = os.path.join(GREETD_DIR, "background.png")
BACKGROUND_SRC = (
    "/usr/local/share/lightdm-webkit/themes/KamiDream_Theme/assets/background.png",
    "/usr/share/lightdm-webkit/themes/KamiDream_Theme/assets/background.png",
)


def ensure_background():
    """把背景图放到 /etc/greetd/background.png（已有则跳过）。

    背景图是可选装饰：找不到源图时不算失败，登录器照样能用，只是没壁纸。
    """
    if os.path.exists(BACKGROUND):
        return True
    for src in BACKGROUND_SRC:
        if os.path.exists(src):
            Shell.sudo(f"cp -f {src} {BACKGROUND}")
            break
    return True


def enable_greetd():
    """启用 greetd，返回 (ok, 说明)。

    /etc/systemd/system/display-manager.service 这张软链全局只能指向一个 DM，
    lightdm 占着它时 `systemctl enable greetd` 会报 "File ... already exists"，
    所以必须先 disable lightdm；启用失败则把 lightdm 启用回去，别让机器开机没登录器。
    """
    if Shell.ok("systemctl is-enabled greetd"):
        return True
    had_lightdm = Shell.ok("systemctl is-enabled lightdm")
    if had_lightdm:
        Shell.sudo("systemctl disable lightdm")
    ok, out = Shell.sudo("systemctl enable greetd")
    if not ok:
        if had_lightdm:
            Shell.sudo("systemctl enable lightdm")
        if "already exists" in out:
            return False, "display-manager.service 被其它登录器占用 / owned by another DM"
        return False, Shell.brief(out)
    return True


def set_background(source):
    """把 source 拷成登录器背景，并让 regreet.toml 指向它。返回 (ok, 说明)。

    以 root 拷贝成 644，所以源图在不在用户家目录都无所谓；greeter 用户读得到。
    """
    ok, out = Shell.sudo(f"install -Dm644 {shlex.quote(source)} {BACKGROUND}")
    if not ok:
        return False, Shell.brief(out)

    ok, cur = Shell.sudo_capture(f"cat {REGREET_CONF}")
    cur = cur if ok else ""
    line = f'path = "{BACKGROUND}"'
    if re.search(r"(?m)^\s*path\s*=", cur):
        new = re.sub(r"(?m)^\s*path\s*=.*$", line, cur)
    elif re.search(r"(?m)^\[background\]\s*$", cur):
        new = re.sub(r"(?m)^(\[background\]\s*)$", r"\1\n" + line, cur, count=1)
    else:
        block = f"[background]\n{line}\nfit = \"Cover\"\n"
        new = block + ("\n" + cur if cur.strip() else "")
    okw, errw = _write(REGREET_CONF, new)
    return okw, Shell.brief(errw)

PAM_GREETD = "/etc/pam.d/greetd"
PAM_BACKUP = "/etc/pam.d/greetd.archinit.bak"
PAM_MODULE = "/usr/lib/security/pam_gnome_keyring.so"

# LightDM 的 /etc/pam.d/lightdm 自带 pam_gnome_keyring，登录时密码会顺手解锁登录密钥环；
# greetd 的 PAM 栈（system-local-login）没有它，所以换成 greetd 后每次重启都要输密钥环密码。
# 这两行要放在 include 之后：session 阶段需要 pam_systemd 先把 /run/user/<uid> 建好。
PAM_KEYRING_LINES = (
    "-auth      optional    pam_gnome_keyring.so\n"
    "-session   optional    pam_gnome_keyring.so auto_start\n"
)

# 上游 README 推荐的 cage 参数：-s 允许 VT 切换（避免锁死）、-mlast 只用最后接入的显示器、-d 不要客户端装饰
GREETD_TEMPLATE = (
    "[terminal]\n"
    "vt = 1\n"
    "\n"
    "[default_session]\n"
    'command = "dbus-run-session cage -s -mlast -d -- regreet"\n'
    'user = "greeter"\n'
)

REGREET_CSS_TEMPLATE = """/* ArchInit — 对齐 LightDM KamiDream 主题
   白色半透明玻璃 + 白字 + 淡蓝强调色 #4fc3f7（取自 LightDM 主题的 style.css）

   两个 GTK 注意事项（改样式时别踩）：
   1. GTK 自带深色主题用 background-image（渐变/图片）画按钮底，只设 background-color
      会被盖住 —— 每条规则都显式 background-image: none。
   2. 主题里弹层/选中行的选择器更具体（如 popover.menu.background > contents、
      dropdown popover listview > row.activatable:selected），这里用同等具体度的选择器
      才压得住。
   3. GTK4 没有 backdrop-filter，做不出 LightDM 那种毛玻璃；改用更高的不透明度补偿。
*/

window {
    background-color: #161a24;      /* 背景图没加载时的兜底 */
    font-family: "Inter", "Noto Sans CJK SC", "Noto Sans", sans-serif;
}

/* 登录卡片：主题里表单直接浮在背景上，这里只留很淡的一层玻璃 */
frame.background {
    background-image: none;
    background-color: rgba(255, 255, 255, 0.16);
    border: 1px solid rgba(255, 255, 255, 0.14);
    border-radius: 18px;
    min-width: __CARD_W__px;
    padding: __CARD_PAD_Y__px __CARD_PAD_X__px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25);
}

/* 顶部时钟：对应主题的 #status-bar */
frame.widget-clock {
    background-image: none;
    background-color: rgba(255, 255, 255, 0.20);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 8px;
    padding: 6px 16px;
}

/* 文字 */
label { color: #ffffff; }
label.dim-label { color: rgba(255, 255, 255, 0.60); opacity: 1; }
label.error { color: #ef5350; }

/* 这些容器自己不该画底（底由里面的输入框 / 按钮画） */
dropdown, combobox, comboboxtext, menubutton, spinbutton, searchentry,
headerbar, actionbar, toolbar, windowhandle, windowcontrols,
list, listview, row {
    background-color: transparent;
    background-image: none;
    border-color: transparent;
}

/* 用户名 / 密码框：和 User 下拉框一致的长方形 */
entry, passwordentry {
    background-image: none;
    background-color: rgba(255, 255, 255, 0.18);
    border: 1px solid rgba(255, 255, 255, 0.28);
    border-radius: 8px;
    color: #ffffff;
    caret-color: #ffffff;
    min-width: __ENTRY_W__px;
    min-height: __BTN_H__px;
    padding: __BTN_PAD_Y__px __BTN_PAD_X__px;
    font-size: 14px;
}
entry:focus, entry:focus-within, passwordentry:focus, passwordentry:focus-within {
    background-image: none;
    background-color: rgba(255, 255, 255, 0.26);
    border-color: rgba(255, 255, 255, 0.55);
    outline: none;
    box-shadow: 0 0 20px rgba(79, 195, 247, 0.15);
}
entry > text > placeholder, placeholder { color: rgba(255, 255, 255, 0.55); }
entry.error, passwordentry.error {
    background-image: none;
    color: #ffffff;
    border-color: #ef5350;
    box-shadow: 0 0 14px rgba(239, 83, 80, 0.35);
}
entry > text > selection, selection {
    background-image: none;
    background-color: rgba(79, 195, 247, 0.35);
    color: #ffffff;
}

/* 按钮 / 用户名切换 / 会话选择：和密码框同一套玻璃底。
   覆盖 normal / hover / active / checked / flat / disabled，主题在
   每个状态都会重新塞一段 background-image。 */
button, button.flat, button:not(.flat),
menubutton > button, menubutton > button.flat,
dropdown > button, comboboxtext > button, combobox > button,
comboboxtext button, combobox button {
    background-image: none;
    background-color: rgba(255, 255, 255, 0.18);
    border: 1px solid rgba(255, 255, 255, 0.28);
    border-radius: 8px;
    color: #ffffff;
    min-height: __BTN_H__px;
    padding: __BTN_PAD_Y__px __BTN_PAD_X__px;
    font-size: 14px;
}
button:hover, button.flat:hover,
menubutton > button:hover, dropdown > button:hover,
comboboxtext > button:hover, combobox > button:hover,
comboboxtext button:hover, combobox button:hover {
    background-image: none;
    background-color: rgba(255, 255, 255, 0.26);
    border-color: rgba(255, 255, 255, 0.40);
}
button:active, button:checked, button.keyboard-activating,
button.flat:active, button.flat:checked,
menubutton > button:active, menubutton > button:checked,
dropdown > button:active, dropdown > button:checked,
comboboxtext > button:active, comboboxtext > button:checked,
combobox > button:active, combobox > button:checked,
comboboxtext button:active, comboboxtext button:checked,
combobox button:active, combobox button:checked {
    background-image: none;
    background-color: rgba(255, 255, 255, 0.34);
    border-color: rgba(255, 255, 255, 0.45);
}
button:checked:hover, button:checked:active,
dropdown > button:checked:hover, dropdown > button:checked:active,
combobox > button:checked:hover, combobox > button:checked:active {
    background-image: none;
    background-color: rgba(255, 255, 255, 0.40);
    border-color: rgba(255, 255, 255, 0.50);
}
button:focus, button:focus-visible,
dropdown > button:focus, combobox > button:focus {
    background-image: none;
    border-color: rgba(255, 255, 255, 0.55);
    box-shadow: 0 0 20px rgba(79, 195, 247, 0.15);
}
button:disabled, button.flat:disabled,
dropdown > button:disabled, combobox > button:disabled {
    background-image: none;
    background-color: rgba(255, 255, 255, 0.10);
    color: rgba(255, 255, 255, 0.45);
}

/* 强调色按钮：登录 / 重启 / 关机 */
button.suggested-action, button.suggested-action.flat {
    background-image: none;
    background-color: rgba(79, 195, 247, 0.22);
    border-color: rgba(79, 195, 247, 0.45);
}
button.suggested-action, button.suggested-action label { color: #4fc3f7; }
button.suggested-action:hover {
    background-image: none;
    background-color: rgba(79, 195, 247, 0.32);
    border-color: rgba(79, 195, 247, 0.60);
}
button.suggested-action:active, button.suggested-action:checked {
    background-image: none;
    background-color: rgba(79, 195, 247, 0.40);
}
button.destructive-action, button.destructive-action.flat {
    background-image: none;
    background-color: rgba(239, 83, 80, 0.18);
    border-color: rgba(239, 83, 80, 0.45);
}
button.destructive-action, button.destructive-action label { color: #ef5350; }
button.destructive-action:hover {
    background-image: none;
    background-color: rgba(239, 83, 80, 0.28);
    border-color: rgba(239, 83, 80, 0.60);
}
button.destructive-action:active, button.destructive-action:checked {
    background-image: none;
    background-color: rgba(239, 83, 80, 0.36);
}

/* 下拉展开列表：主题用 popover.menu.background > contents 画 #2d2d2d，
   所以这里必须用同等具体度的选择器 */
popover.background {
    background-color: transparent;
    background-image: none;
    font-family: "Inter", "Noto Sans CJK SC", "Noto Sans", sans-serif;
}
popover.background > contents,
popover.menu > contents,
popover.menu.background > contents,
popover.combo > contents,
dropdown > popover > contents {
    background-image: none;
    background-color: rgba(255, 255, 255, 0.30);
    color: #ffffff;
    border: 1px solid rgba(255, 255, 255, 0.16);
    border-radius: 6px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.18);
}
popover listview, popover list, popover scrolledwindow, popover viewport {
    background-image: none;
    background-color: transparent;
    border-color: transparent;
    color: #ffffff;
}
popover row, popover row.activatable,
dropdown popover listview > row, menuitem {
    background-image: none;
    color: rgba(255, 255, 255, 0.80);
    border-radius: 4px;
    padding: 4px 6px;
}
popover row.activatable:hover, popover row:hover,
dropdown popover listview > row.activatable:hover,
menuitem:hover {
    background-image: none;
    background-color: rgba(255, 255, 255, 0.10);
    color: #ffffff;
}
/* 选中行：主题这里是 dropdown popover listview > row.activatable:selected */
dropdown popover listview > row.activatable:selected,
dropdown popover listview > row.activatable:selected:hover,
combobox popover listview > row.activatable:selected,
combobox popover listview > row.activatable:selected:hover,
popover row:selected, popover row:selected:hover {
    background-image: none;
    background-color: rgba(255, 255, 255, 0.14);
    color: #4fc3f7;
    border-radius: 4px;
    font-weight: 500;
}

/* 滚动条：4px 细条，对应主题的 ::-webkit-scrollbar */
scrollbar { background-image: none; background-color: transparent; }
scrollbar slider {
    background-image: none;
    background-color: rgba(255, 255, 255, 0.20);
    border-radius: 2px;
    min-width: 4px;
    min-height: 4px;
}
scrollbar slider:hover { background-image: none; background-color: rgba(255, 255, 255, 0.30); }
"""


def _write(path, content):
    """以 root 写入文件（非交互），返回 (ok, 错误信息)。"""
    r = subprocess.run(["sudo", "-n", "tee", path], input=content, text=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=False)
    return r.returncode == 0, (r.stderr or "").strip()


# 尺寸基准：1645x1028（1.75 缩放的 2880x1800）。尺寸都按主屏逻辑宽度等比换算。
BASE_WIDTH = 1645


def _logical_width():
    """主显示器的逻辑宽度；拿不到时返回 0。

    px 在 GTK 里是逻辑像素（已经跟着缩放走），所以这里只需要跟屏幕宽窄
    等比例缩放“框有多大”。
    """
    rc, out = Shell.capture_all("niri msg outputs 2>/dev/null")
    if rc == 0:
        for line in out.splitlines():
            line = line.strip()
            if line.startswith("Logical size:"):
                try:
                    return int(line.split()[2].split("x")[0])
                except (IndexError, ValueError):
                    pass
    rc, out = Shell.capture_all(
        "cat /sys/class/drm/card*-*/modes 2>/dev/null | head -1")
    try:
        return int(out.split("x")[0])
    except (AttributeError, IndexError, ValueError):
        return 0


def _sizes():
    """按当前屏幕算一套尺寸（GTK4 没有 media query，只能安装时算一次）。"""
    width = _logical_width() or BASE_WIDTH
    k = max(0.85, min(1.35, width / BASE_WIDTH))

    def s(base, low):
        return max(low, round(base * k))

    return {
        "CARD_W": s(520, 380),
        "CARD_PAD_Y": s(32, 22),
        "CARD_PAD_X": s(38, 24),
        "ENTRY_W": s(300, 220),
        "BTN_H": s(36, 30),
        "BTN_PAD_Y": s(8, 6),
        "BTN_PAD_X": s(16, 12),
    }


def render_css():
    """把模板里的 __XXX__ 占位符换成当前屏幕对应的尺寸。"""
    css = REGREET_CSS_TEMPLATE
    for key, value in _sizes().items():
        css = css.replace(f"__{key}__", str(value))
    return css


class LoginManagerSteps:
    @classmethod
    def install(cls):
        ok = TaskView.run("登录管理器 · 安装 greetd + ReGreet / Install", [
            ("安装 greetd / greetd-regreet / cage",
             lambda: Shell.pacman("greetd greetd-regreet cage")),
        ])
        Status.set("✅ greetd + ReGreet 已安装 / installed" if ok
                   else "❌ 安装失败 / install failed")
        return ok

    @classmethod
    def enable(cls):
        def check_bins():
            missing = [b for b in ("/usr/bin/regreet", "/usr/bin/cage")
                       if not os.path.exists(b)]
            if missing:
                return False, "缺少 " + ", ".join(missing) + "（先执行上一步）"
            return True

        def write_greetd():
            ok, err = _write(GREETD_CONF, GREETD_TEMPLATE)
            return ok, Shell.brief(err)

        def write_regreet():
            parts = []
            if os.path.isfile(BACKGROUND):
                parts.append(f'[background]\npath = "{BACKGROUND}"\nfit = "Cover"\n')
            # 白色半透明玻璃元素需要深色 GTK 基底，否则未显式上色的控件会变成深字浅底
            parts.append("[GTK]\napplication_prefer_dark_theme = true\n")
            ok, err = _write(REGREET_CONF, "\n".join(parts))
            return ok, Shell.brief(err)

        def write_css():
            # 已存在且不是 ArchInit 生成的文件时，保留用户自己的样式
            if os.path.exists(REGREET_CSS) and not Shell.ok(f"grep -q ArchInit {REGREET_CSS}"):
                return True, ""
            ok, err = _write(REGREET_CSS, render_css())
            return ok, Shell.brief(err)

        def switch_service():
            return enable_greetd()

        def verify():
            if not Shell.ok(f"grep -q regreet {GREETD_CONF}"):
                return False, "greetd 配置未写入 / config missing"
            if not Shell.ok("systemctl is-enabled greetd"):
                return False, "greetd 未设为开机启动 / not enabled"
            return True

        ok = TaskView.run("登录管理器 · 配置并启用 / Configure & enable", [
            ("检查 regreet / cage 是否可执行", check_bins),
            ("准备登录背景（可选）/ Prepare background", ensure_background),
            (f"写入 {GREETD_CONF}", write_greetd),
            (f"写入 {REGREET_CONF}（背景 + 深色）", write_regreet),
            (f"写入 {REGREET_CSS}", write_css),
            ("启用 greetd、停用 lightdm / switch service", switch_service),
            ("校验配置 / verify", verify),
        ])
        Status.set("✅ 已启用 greetd + ReGreet，重启后生效 / reboot to apply" if ok
                   else "❌ 启用失败 / failed")
        return ok

    @classmethod
    def keyring(cls):
        def ensure_pkg():
            if Shell.installed("gnome-keyring"):
                return True
            ok, out = Shell.pacman("gnome-keyring")
            return ok, Shell.brief(out)

        def patch():
            if not os.path.exists(PAM_MODULE):
                return False, "缺少 pam_gnome_keyring.so（先装 gnome-keyring）"
            # 必须拿完整文件内容；Shell.sudo 在面板里只回最后一行
            ok, cur = Shell.sudo_capture(f"cat {PAM_GREETD}")
            if not ok or not cur.strip():
                return False, "无法读取 /etc/pam.d/greetd"
            if "auth" not in cur or "session" not in cur:
                return False, "PAM 内容读取不完整 / incomplete read"
            if "pam_gnome_keyring" in cur:
                return True  # 已经配过（或用户自己加的），不重复写
            if not Shell.ok(f"test -e {PAM_BACKUP}"):
                okb, errb = Shell.sudo_capture(f"cp -an {PAM_GREETD} {PAM_BACKUP}")
                if not okb:
                    return False, Shell.brief(errb)
            body = cur if cur.endswith("\n") else cur + "\n"
            okw, errw = _write(PAM_GREETD, body + PAM_KEYRING_LINES)
            if not okw:
                return False, Shell.brief(errw)
            # 写完立刻回读：内容不对就回滚，避免把 PAM 写坏导致登录不上
            okr, now = Shell.sudo_capture(f"cat {PAM_GREETD}")
            if (not okr or now.count("pam_gnome_keyring.so") < 2
                    or "auth" not in now or "session" not in now):
                # 备份要么本次刚做，要么之前就有，直接用它回滚
                Shell.sudo(f"cp -f {PAM_BACKUP} {PAM_GREETD}")
                return False, "写入后校验失败，已回滚 / rolled back"
            return True

        def verify():
            ok, cur = Shell.sudo_capture(f"cat {PAM_GREETD}")
            if not ok:
                return False, "无法读取 /etc/pam.d/greetd"
            if cur.count("pam_gnome_keyring.so") < 2:
                return False, "PAM 里缺少 pam_gnome_keyring 行 / lines missing"
            if "auth" not in cur or "session" not in cur:
                return False, "PAM 内容不完整 / incomplete PAM config"
            return True

        ok = TaskView.run("登录管理器 · 解锁密钥环 / Unlock keyring at login", [
            ("确认 gnome-keyring 已安装 / ensure gnome-keyring", ensure_pkg),
            (f"写入 {PAM_GREETD} / patch PAM", patch),
            ("校验 / verify", verify),
        ])
        Status.set("✅ 密钥环将随登录自动解锁，重启后生效 / keyring unlocks at login — reboot to apply"
                   if ok else "❌ 密钥环自动解锁配置失败 / keyring unlock setup failed")
        return ok

    @classmethod
    def background(cls):
        """更换登录背景图：输入路径 → 拷到 /etc/greetd/background.png 并更新配置。"""
        subtitle = ("输入图片完整路径，按 Tab 或 Enter 确认 · Esc 取消 / "
                    "type the image path, Tab or Enter to confirm · Esc to cancel")
        notice = ""
        source = None
        while source is None:
            res = Picker.choose("更换登录背景图 / Change login background", [],
                                allow_free=True, subtitle=subtitle, notice=notice)
            if not isinstance(res, FreeText):
                return CANCELLED
            text = os.path.expanduser(str(res).strip().strip("'\""))
            if not text:
                notice = "⚠️  路径为空 / empty path"
                continue
            if not os.path.isfile(text):
                notice = f"⚠️  找不到这张图 / not a file: {text}"
                continue
            source = text

        ok, msg = set_background(source)
        if ok:
            Status.set(f"✅ 登录背景已换成 {os.path.basename(source)}，注销后生效 / log out to apply")
            return True
        Status.set(f"❌ 登录背景更换失败 / failed: {msg}")
        return False
