"""在 TUI 内执行一组任务并显示进度（命令输出不写到终端）。"""
import contextlib
import curses
import time
import unicodedata


def _trunc(s, cells):
    used = 0
    out = []
    for ch in s:
        cw = 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1
        if used + cw > cells:
            break
        out.append(ch)
        used += cw
    return "".join(out), used


def _ok(res):
    if isinstance(res, tuple):
        return bool(res[0])
    return bool(res)


class TaskView:
    """逐条执行任务并在同主题风格的方框里显示状态：⏳ 进行中 / ✅ 成功 / ❌ 失败。"""

    BRAND_LEFT = "Kami"
    BRAND_RIGHT = "Dream"
    _shared_stdscr = None  # 主界面调用 bind() 后复用该窗口

    def __init__(self, stdscr, title, items, hold):
        self.stdscr = stdscr
        self.title = title
        self.items = items          # [(label, callable), ...]
        self.hold = hold
        self.results = []
        self.current = None
        self.attr_ok = curses.A_BOLD
        self.attr_err = curses.A_BOLD
        self.attr_sel = curses.A_BOLD
        self.attr_brand_l = curses.A_BOLD
        self.attr_brand_r = curses.A_BOLD

    # ── 颜色 ──
    def _init_colors(self):
        if not curses.has_colors():
            return
        try:
            curses.start_color()
            curses.init_pair(22, curses.COLOR_GREEN, -1)
            curses.init_pair(23, curses.COLOR_RED, -1)
            curses.init_pair(24, curses.COLOR_YELLOW, -1)
            self.attr_ok = curses.color_pair(22) | curses.A_BOLD
            self.attr_err = curses.color_pair(23) | curses.A_BOLD
            self.attr_sel = curses.color_pair(24) | curses.A_BOLD
        except curses.error:
            pass
        if curses.COLORS >= 256:
            try:
                curses.init_pair(25, 12, -1)
                curses.init_pair(26, 13, -1)
                self.attr_brand_l = curses.color_pair(25)
                self.attr_brand_r = curses.color_pair(26)
            except curses.error:
                pass

    # ── 绘制 ──
    def _put(self, y, x, text, attr=0):
        h, w = self.stdscr.getmaxyx()
        if y < 0 or y >= h or x >= w - 1:
            return
        text, _ = _trunc(text, max(0, w - 1 - x))
        try:
            self.stdscr.addstr(y, x, text, attr)
        except curses.error:
            pass

    def _draw(self, state, detail=""):
        s = self.stdscr
        s.erase()
        h, w = s.getmaxyx()
        if h < 8 or w < 40:
            self._put(0, 0, self.title, curses.A_BOLD)
            s.refresh()
            return

        self._put(0, 0, "=" * (w - 1))
        prefix = "ArchInit_"
        self._put(1, 2, prefix, curses.A_BOLD)
        px = 2 + _trunc(prefix, 10 ** 6)[1]
        self._put(1, px, self.BRAND_LEFT, self.attr_brand_l)
        px += _trunc(self.BRAND_LEFT, 10 ** 6)[1]
        self._put(1, px, self.BRAND_RIGHT, self.attr_brand_r)
        self._put(2, 0, "=" * (w - 1))
        self._put(3, 2, self.title, self.attr_sel)

        y = 5
        for i, (label, _func) in enumerate(self.items):
            if y >= h - 3:
                break
            if i < len(self.results):
                ok, note = self.results[i]
                mark, attr = ("✅", self.attr_ok) if ok else ("❌", self.attr_err)
                self._put(y, 2, f" {mark} {label}", attr)
                if not ok and note:
                    self._put(y, 2 + _trunc(f" {mark} {label}", 10 ** 6)[1] + 2, f"({note})",
                              self.attr_err)
            elif i == self.current:
                self._put(y, 2, f" ⏳ {label}", self.attr_sel)
            else:
                self._put(y, 2, f" ⬜ {label}")
            y += 1

        if detail and y < h - 3:
            self._put(y + 1, 4, detail, self.attr_err)

        self._put(h - 2, 0, "═" * (w - 1))
        footer = {
            "running": "执行中 … / running …",
            "done": "✅ 完成 / done",
            "failed": "❌ 失败 / failed · 按任意键返回 / press any key",
        }[state]
        self._put(h - 1, 2, footer)
        s.refresh()

    # ── 执行 ──
    def _run(self):
        self._init_colors()
        try:
            curses.curs_set(0)
        except curses.error:
            pass
        self.results = []
        for i, (_label, func) in enumerate(self.items):
            self.current = i
            self._draw("running")
            try:
                res = func()
            except Exception as e:  # noqa: BLE001
                res = (False, str(e)[:60])
            ok = _ok(res)
            note = res[1] if isinstance(res, tuple) and len(res) > 1 else ""
            self.results.append((ok, note))
            if not ok:
                break
        self.current = None
        ok = bool(self.results) and all(r[0] for r in self.results)
        self._draw("done" if ok else "failed")
        if ok:
            if self.hold:
                time.sleep(self.hold)
        else:
            try:
                self.stdscr.getch()
            except curses.error:
                pass
        return ok

    # ── 对外接口 ──
    @classmethod
    def bind(cls, stdscr):
        cls._shared_stdscr = stdscr

    @classmethod
    @contextlib.contextmanager
    def terminal(cls):
        """临时把终端交还给外部程序（如 kitten / 交互式安装脚本），结束后回到面板。"""
        try:
            curses.endwin()
        except curses.error:
            pass
        try:
            yield
        finally:
            try:
                curses.reset_prog_mode()
                if cls._shared_stdscr is not None:
                    cls._shared_stdscr.clear()
                    cls._shared_stdscr.refresh()
            except curses.error:
                pass

    @classmethod
    def run(cls, title, items, hold=0.6):
        """逐条执行 items（[(label, callable)]），返回是否全部成功。

        callable 返回 True/False，或 (bool, 失败说明)。
        没有绑定主窗口时（脚本/测试）直接顺序执行，不画界面。
        """
        stdscr = cls._shared_stdscr
        if stdscr is None:
            ok = True
            for _label, func in items:
                res = func()
                if not _ok(res):
                    ok = False
                    break
            return ok

        try:
            curses.reset_prog_mode()
            stdscr.clear()
            stdscr.refresh()
        except curses.error:
            pass
        try:
            return cls(stdscr, title, items, hold)._run()
        finally:
            try:
                stdscr.timeout(-1)
                curses.endwin()
            except curses.error:
                pass
