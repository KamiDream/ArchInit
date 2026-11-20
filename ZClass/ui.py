"""curses 两栏界面（类似 yazi：左分类导航 / 右步骤内容）。"""
import curses
import unicodedata

from .config import BRAND_LEFT, BRAND_RIGHT
from .model import CANCELLED
from .picker import Picker
from .shell import Shell
from .status import Status
from .style import Style


class UI:
    def __init__(self, stdscr, categories):
        self.stdscr = stdscr
        self.categories = categories
        self.color = curses.has_colors()
        self.bright_brand = True
        self.main_sel = 0  # 记住主菜单上次高亮的分类位置
        Picker.bind(stdscr)  # 步骤内弹出选择器时复用本窗口

    # ── 颜色 ──
    def init_colors(self):
        if not self.color:
            return
        curses.start_color()
        try:
            curses.use_default_colors()
            bg = -1
        except curses.error:
            bg = curses.COLOR_BLACK
        curses.init_pair(1, curses.COLOR_CYAN, bg)     # 选中高亮
        curses.init_pair(2, curses.COLOR_MAGENTA, bg)
        curses.init_pair(3, curses.COLOR_YELLOW, bg)   # 警告
        curses.init_pair(4, curses.COLOR_GREEN, bg)    # 完成
        curses.init_pair(5, curses.COLOR_RED, bg)      # 错误
        # 品牌色：Kami 淡蓝 / Dream 淡粉
        if curses.COLORS >= 256:
            curses.init_pair(6, 12, bg)   # bright blue
            curses.init_pair(7, 13, bg)   # bright magenta
            self.bright_brand = False
        else:
            curses.init_pair(6, curses.COLOR_BLUE, bg)
            curses.init_pair(7, curses.COLOR_MAGENTA, bg)
            self.bright_brand = True

    def attr(self, pair, extra=0):
        if not self.color:
            return extra
        return curses.color_pair(pair) | extra

    def brand_attr(self, pair):
        if not self.color:
            return curses.A_BOLD
        a = curses.color_pair(pair)
        if self.bright_brand:
            a |= curses.A_BOLD
        return a

    # ── 宽字符友好的绘制：按显示宽度截断/写入 ──
    def _trunc(self, s, cells):
        used = 0
        out = []
        for ch in s:
            cw = 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1
            if used + cw > cells:
                break
            out.append(ch)
            used += cw
        return "".join(out), used

    def putw(self, y, x, s, attr=0, maxcells=None):
        h, w = self.stdscr.getmaxyx()
        if y < 0 or y >= h or x >= w - 1:
            return
        avail = w - 1 - x
        if maxcells is not None:
            avail = min(avail, maxcells)
        if avail <= 0:
            return
        s2, _ = self._trunc(s, avail)
        try:
            self.stdscr.addstr(y, x, s2, attr)
        except curses.error:
            pass

    # ── 两栏界面：左分类导航 / 右步骤内容（类似 yazi）──
    def draw_twopane(self, cat_idx, focus):
        self.stdscr.erase()
        h, w = self.stdscr.getmaxyx()
        cats = self.categories
        if h < 10 or w < 42:
            self.putw(0, 0, "窗口太小 / Terminal too small (need >= 42x10)", self.attr(5))
            self.putw(1, 0, "请放大窗口 / please enlarge the window  ·  q 退出 / quit")
            self.stdscr.refresh()
            return
        y = 0
        # logo 上方一条 (=)，下方一条 (=)
        self.putw(y, 0, "=" * (w - 1)); y += 1
        # 标题：ArchInit_KamiDream（Kami 淡蓝 / Dream 淡粉）
        prefix = "ArchInit_"
        self.putw(y, 2, prefix, curses.A_BOLD)
        px = 2 + self._trunc(prefix, 10 ** 6)[1]
        self.putw(y, px, BRAND_LEFT, self.brand_attr(6))
        px += self._trunc(BRAND_LEFT, 10 ** 6)[1]
        self.putw(y, px, BRAND_RIGHT, self.brand_attr(7))
        y += 1
        self.putw(y, 0, "=" * (w - 1)); y += 1
        body_top = y
        footer_y = max(body_top + 1, h - 2)

        # 左栏宽度：按完整标题（含 ▸ ✓ 前缀）自适应，稍宽松，为右栏保留空间
        maxw = 0
        for c in cats:
            _, tw = self._trunc(c.title, 10 ** 6)
            maxw = max(maxw, tw)
        # 标签形如 "▸ ✓ 标题"，前缀宽 4；再加点边距
        L = min(maxw + 4 + 3, max(24, w - 34))
        L = max(20, L)
        ly = body_top
        for i, c in enumerate(cats):
            if ly >= footer_y:
                break
            done = all(c.completed) if c.completed else False
            mark = "✓" if done else " "
            arrow = "▸" if i == cat_idx else " "
            raw = f"{arrow} {mark} {c.title}"
            text, tw = self._trunc(raw, L - 1)
            label = text + " " * max(0, L - 1 - tw)
            if i == cat_idx:
                attr = self.attr(1, curses.A_BOLD)
                if focus == "left":
                    attr |= curses.A_REVERSE
            else:
                attr = 0
            self.putw(ly, 0, label, attr, maxcells=L - 1)
            ly += 1

        for yy in range(body_top, footer_y):
            self.putw(yy, L - 1, "│")

        # 右栏
        cat = cats[cat_idx]
        rx = L
        ry = body_top
        self.putw(ry, rx, f" {cat.title}", self.attr(3, curses.A_BOLD)); ry += 1
        if cat.warning:
            for wl in cat.warning:
                if ry >= footer_y:
                    break
                self.putw(ry, rx, " " + wl, self.attr(3)); ry += 1
        ry += 1
        for si, s in enumerate(cat.steps):
            if ry >= footer_y:
                break
            if si in cat.dividers:
                self.putw(ry, rx, "─" * max(0, w - rx - 1)); ry += 1
                if ry >= footer_y:
                    break
            mark = "✓" if cat.completed[si] else " "
            arrow = "▸" if si == cat.selected else " "
            line = f" {arrow} {mark} Step {si+1}: {s.title}"
            if si == cat.selected:
                attr = self.attr(1, curses.A_BOLD)
                if focus == "right":
                    avail = w - 1 - rx
                    text, tw = self._trunc(line, avail)
                    line = text + " " * max(0, avail - tw)
                    attr |= curses.A_REVERSE
            else:
                attr = 0
            self.putw(ry, rx, line, attr); ry += 1

        self.putw(footer_y, 0, "═" * (w - 1))
        if Status.message:
            self.putw(footer_y + 1, 2, Status.message, self.attr(4, curses.A_BOLD))
        elif focus == "left":
            hint = "↑/↓ 选择分类  •  →/Enter 进入  •  q 退出"
            self.putw(footer_y + 1, 2, hint)
        else:
            hint = "↑/↓ 选择步骤  •  Enter 执行  •  ←/Esc 返回分类  •  q 退出"
            self.putw(footer_y + 1, 2, hint)
        self.stdscr.refresh()

    # ── 执行单个步骤（退出 curses 回到普通终端）──
    def execute_step(self, cat, si):
        step = cat.steps[si]
        curses.def_prog_mode()
        curses.endwin()
        result = False
        try:
            result = step.func()
        except KeyboardInterrupt:
            print("\n  ⚠️  已被用户中断 / Interrupted by user.")
            result = False
        except Exception as e:  # noqa: BLE001
            print(Style.red_bold(f"\n  ❌ 异常 / Exception: {e}"))
            result = False

        if result is CANCELLED:
            # 用户主动取消：直接回菜单，不标记完成、不等待按键
            Status.set(f"↩️  已取消 / Cancelled: {step.title}")
        elif result:
            cat.completed[si] = True
            if not Status.message:
                Status.set(f"✅ 完成 / Done: {step.title}")
        else:
            # 失败需要用户注意，保留终端输出并等待按键
            print()
            print(Style.red_bold(f"  ❌ Step {si+1} failed: {step.title}"))
            print()
            try:
                Shell.wait_key("按 Enter 返回菜单 / Press Enter to return")
            except (EOFError, KeyboardInterrupt):
                pass
        curses.reset_prog_mode()
        # 步骤内部可能嵌入过额外窗口（如 Picker 的 curses.wrapper），
        # 退出时会关掉 keypad、留下非阻塞 timeout，这里恢复主界面状态
        try:
            self.stdscr.keypad(True)
            self.stdscr.timeout(-1)
            curses.curs_set(0)
        except curses.error:
            pass
        self.stdscr.clear()
        self.stdscr.refresh()

    # ── 主循环（两栏交互）──
    def run(self):
        cats = self.categories
        n = len(cats)
        cat_idx = max(0, min(self.main_sel, n - 1))
        focus = "left"
        while True:
            cat = cats[cat_idx]
            if cat.steps:
                cat.selected = max(0, min(cat.selected, len(cat.steps) - 1))
            self.main_sel = cat_idx
            self.draw_twopane(cat_idx, focus)
            key = self.stdscr.getch()
            Status.clear()  # 任意按键后清除底部提示

            # 窗口缩放：刷新行列数并重绘
            if key == curses.KEY_RESIZE:
                try:
                    curses.update_lines_cols()
                except AttributeError:
                    pass
                continue

            if focus == "left":
                if key in (curses.KEY_UP, ord("k")):
                    cat_idx = (cat_idx - 1) % n
                elif key in (curses.KEY_DOWN, ord("j")):
                    cat_idx = (cat_idx + 1) % n
                elif key in (curses.KEY_RIGHT, ord("l"), 10, 13, curses.KEY_ENTER):
                    if cat.steps:
                        focus = "right"
                elif key in (ord("q"), ord("Q"), 27):
                    return
            else:
                steps = cat.steps
                if key in (curses.KEY_UP, ord("k")):
                    cat.selected = (cat.selected - 1) % len(steps)
                elif key in (curses.KEY_DOWN, ord("j")):
                    cat.selected = (cat.selected + 1) % len(steps)
                elif key in (10, 13, curses.KEY_ENTER):
                    self.execute_step(cat, cat.selected)
                elif key in (curses.KEY_LEFT, ord("h"), 27):
                    focus = "left"
                elif key in (ord("q"), ord("Q")):
                    return
