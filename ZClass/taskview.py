"""在 TUI 内执行一组任务并显示进度（命令输出不写到终端）。"""
import contextlib
import curses
import threading
import time
import unicodedata
from collections import deque
from typing import ClassVar


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
    """逐条执行任务并在同主题风格的方框里显示状态：⏳ 进行中 / ✅ 成功 / ❌ 失败。

    任务内部可通过 Shell.quiet()/Shell.pacman() 执行的命令会实时把最新一行输出
    回报到面板底部的「进度行」上（带 spinner 与耗时）。
    """

    BRAND_LEFT = "Kami"
    BRAND_RIGHT = "Dream"
    _shared_stdscr = None  # 主界面调用 bind() 后复用该窗口

    SPINNER = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    LOG_LINES = 5          # 进度区最多保留几行（不同包/阶段）
    _log: ClassVar[deque] = deque(maxlen=LOG_LINES)
    _suspended = False     # 终端交给外部程序（kitten / 安装脚本）期间暂停绘制

    @classmethod
    def clear_log(cls):
        cls._log.clear()

    @classmethod
    def progress(cls, text):
        """由任务内部（通常是 Shell 的输出回调）调用，更新进度区。

        同一个包/阶段的进度刷新（pacman 用 \\r 原地重绘）会替换最后一行，
        不同包则往上追加，这样能同时看到多个下载项而不是只看到一条在跳。
        """
        line = " ".join((text or "").split())
        if not line:
            return
        key = tuple(line.split()[:2])
        if cls._log:
            prev = tuple(cls._log[-1].split()[:2])
            if prev == key or cls._log[-1] == line:
                cls._log[-1] = line
                return
        cls._log.append(line)

    def __init__(self, stdscr, title, items, hold):
        self.stdscr = stdscr
        self.title = title
        self.items = items          # [(label, callable), ...]
        self.hold = hold
        self.results = []
        self.current = None
        self.started = 0.0          # 当前任务开始时间
        self.total_start = 0.0      # 整个面板开始时间
        self.lock = threading.Lock()
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
        """重绘面板（加锁，避免后台 spinner 线程与主线程同时绘制）。"""
        if TaskView._suspended:
            return
        with self.lock:
            try:
                self._draw_impl(state, detail)
            except curses.error:
                pass

    def _draw_impl(self, state, detail=""):
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
        # 任务多时开窗（以当前任务为中心），并给进度区留出几行
        reserve = min(TaskView.LOG_LINES, 4)
        avail = max(1, (h - 3) - y - reserve)
        if len(self.items) > avail:
            focus = self.current if self.current is not None else max(0, len(self.results) - 1)
            start_i = max(0, min(focus - avail // 2, len(self.items) - avail))
            window = list(enumerate(self.items))[start_i:start_i + avail]
        else:
            window = list(enumerate(self.items))

        for i, (label, _func) in window:
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

        # 进度区：最近几条输出（同一包原地刷新，不同包依次累积）
        if state == "running" and self.current is not None:
            lines = list(TaskView._log)
            if not lines:
                lines = ["连接中 … / starting …"]
            room = (h - 3) - (y + 1)
            if room > 0:
                show = lines[-room:]
                start = (h - 3) - len(show)
                for idx, text in enumerate(show):
                    self._put(start + idx, 4, text)

        self._put(h - 2, 0, "═" * (w - 1))
        footer = {
            "running": "执行中 … / running …",
            "done": "✅ 完成 / done",
            "failed": "❌ 失败 / failed · 按任意键返回 / press any key",
        }[state]
        self._put(h - 1, 2, footer)

        # 右下角（双实线下）：spinner + 已耗时 / 总耗时
        if state == "running" and self.current is not None:
            spin = self.SPINNER[int(time.time() * 8) % len(self.SPINNER)]
            elapsed = int(time.time() - self.started) if self.started else 0
            self._put(h - 1, max(0, w - len(f"{spin} {elapsed}s ") - 1), f"{spin} {elapsed}s ",
                      self.attr_sel)
        elif state == "done" and self.total_start:
            total = int(time.time() - self.total_start)
            self._put(h - 1, max(0, w - len(f"✅ {total}s ") - 1), f"✅ {total}s ", self.attr_ok)
        s.refresh()

    # ── 执行 ──
    def _tick(self, stop):
        """后台定时重绘，使 spinner / 进度行 / 耗时保持更新。"""
        with contextlib.suppress(Exception):
            while not stop.wait(0.2):
                self._draw("running")

    def _run(self):
        from .shell import Shell

        self._init_colors()
        try:
            curses.curs_set(0)
        except curses.error:
            pass
        self.results = []
        self.total_start = time.time()
        Shell.progress_hook = self.progress
        try:
            for i, (_label, func) in enumerate(self.items):
                self.current = i
                self.clear_log()
                self.started = time.time()
                self._draw("running")
                stop = threading.Event()
                ticker = threading.Thread(target=self._tick, args=(stop,), daemon=True)
                ticker.start()
                try:
                    res = func()
                except Exception as e:  # noqa: BLE001
                    res = (False, str(e)[:60])
                finally:
                    stop.set()
                    ticker.join(timeout=0.6)
                ok = _ok(res)
                note = res[1] if isinstance(res, tuple) and len(res) > 1 else ""
                self.results.append((ok, note))
                if not ok:
                    break
        finally:
            Shell.progress_hook = None
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
        """临时把终端交还给外部程序（如 kitten / 交互式安装脚本），结束后回到面板。

        期间必须暂停绘制，否则后台 spinner 线程会把面板画到对方的界面上。
        """
        TaskView._suspended = True
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
            TaskView._suspended = False

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
