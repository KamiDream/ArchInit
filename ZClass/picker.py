"""通用可上下选择的列表控件（curses），供需要交互选择的步骤使用。"""
import curses
import unicodedata
from typing import ClassVar


def _trunc(s, cells):
    """按显示宽度截断字符串，返回 (截断后文本, 实际占用宽度)。"""
    used = 0
    out = []
    for ch in s:
        cw = 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1
        if used + cw > cells:
            break
        out.append(ch)
        used += cw
    return "".join(out), used


class Picker:
    PAIR = 20  # 与主界面配色对错开

    def __init__(self, stdscr, title, items):
        self.stdscr = stdscr
        self.title = title
        self.items = items  # [(主文本, 副文本), ...]
        self.query = ""
        self.sel = 0
        self.offset = 0

    # ── 颜色 ──
    def _init_colors(self):
        if not curses.has_colors():
            return
        try:
            curses.start_color()
            curses.init_pair(self.PAIR, curses.COLOR_CYAN, -1)
            self.attr_sel = curses.color_pair(self.PAIR) | curses.A_REVERSE
        except curses.error:
            self.attr_sel = curses.A_REVERSE

    def _attr_sel(self):
        return getattr(self, "attr_sel", curses.A_REVERSE)

    # ── 过滤 ──
    def _matches(self):
        q = self.query.lower()
        if not q:
            return list(range(len(self.items)))
        out = []
        for i, (label, sub) in enumerate(self.items):
            if q in label.lower() or q in (sub or "").lower():
                out.append(i)
        return out

    # ── 绘制 ──
    def _draw(self, matches):
        s = self.stdscr
        s.erase()
        h, w = s.getmaxyx()
        if h < 8 or w < 30:
            self._put(0, 0, "窗口太小 / Terminal too small (need >= 30x8)", curses.A_BOLD)
            s.refresh()
            return

        self._put(0, 1, self.title, curses.A_BOLD)
        shown = self.query if self.query else ""
        prompt = "过滤 / Filter: "
        self._put(1, 1, prompt + shown + "_")
        count = f"{len(matches)}/{len(self.items)}"
        self._put(1, max(1, w - 2 - len(count)), count)

        body_top = 3
        footer_y = h - 2
        for x in range(w - 1):
            self._put(2, x, "─")
        body_h = max(0, footer_y - body_top)

        if matches and body_h > 0:
            if self.sel < self.offset:
                self.offset = self.sel
            elif self.sel >= self.offset + body_h:
                self.offset = self.sel - body_h + 1
            self.offset = max(0, min(self.offset, max(0, len(matches) - body_h)))
            for row in range(body_h):
                fi = self.offset + row
                if fi >= len(matches):
                    break
                label, sub = self.items[matches[fi]]
                attr = self._attr_sel() if fi == self.sel else 0
                text = f" {label}"
                if sub:
                    text += f"  ({sub})"
                self._put(body_top + row, 0, text, attr, maxcells=w - 1,
                          fill=(fi == self.sel))
        elif body_h > 0:
            self._put(body_top, 1, "无匹配 / no match", curses.A_BOLD)

        if self.offset > 0:
            self._put(body_top, max(0, w - 2), "↑")
        if self.offset + body_h < len(matches):
            self._put(footer_y - 1, max(0, w - 2), "↓")

        self._put(footer_y, 0, "═" * (w - 1))
        self._put(footer_y + 1, 1, "↑/↓ 选择  •  输入过滤  •  Enter 确定  •  q/Esc 取消")
        s.refresh()

    def _put(self, y, x, text, attr=0, maxcells=None, fill=False):
        s = self.stdscr
        h, w = s.getmaxyx()
        if y < 0 or y >= h or x >= w - 1:
            return
        avail = w - 1 - x
        if maxcells is not None:
            avail = min(avail, maxcells)
        if avail <= 0:
            return
        text, used = _trunc(text, avail)
        if fill and used < avail:
            text += " " * (avail - used)
        try:
            s.addstr(y, x, text, attr)
        except curses.error:
            pass

    # ── 按键解析（不依赖 terminfo 的方向键翻译）──
    SEQ: ClassVar[dict] = {
        "[A": "up", "OA": "up",
        "[B": "down", "OB": "down",
        "[5~": "pgup", "[6~": "pgdn",
        "[H": "home", "OH": "home", "[1~": "home", "[7~": "home",
        "[F": "end", "OF": "end", "[4~": "end", "[8~": "end",
    }

    def _read_escape(self):
        """ESC 之后读取并解析方向键序列；返回动作名，单独 ESC 返回 'esc'。"""
        self.stdscr.timeout(15)
        seq = ""
        try:
            while len(seq) < 4:
                try:
                    nxt = self.stdscr.get_wch()
                except curses.error:
                    break
                if isinstance(nxt, int):
                    return {curses.KEY_UP: "up", curses.KEY_DOWN: "down",
                            curses.KEY_PPAGE: "pgup", curses.KEY_NPAGE: "pgdn",
                            curses.KEY_HOME: "home", curses.KEY_END: "end"}.get(nxt)
                seq += nxt
                if seq in self.SEQ:
                    break
        finally:
            self.stdscr.timeout(40)
        if not seq:
            return "esc"
        return self.SEQ.get(seq)

    # ── 主循环 ──
    def run(self):
        try:
            curses.curs_set(0)
        except curses.error:
            pass
        self.stdscr.keypad(True)
        try:
            curses.set_escdelay(25)
        except (AttributeError, curses.error):
            pass
        self._init_colors()
        self.stdscr.timeout(40)

        while True:
            matches = self._matches()
            n = len(matches)
            if n:
                self.sel = max(0, min(self.sel, n - 1))
            else:
                self.sel = 0
            self._draw(matches)

            try:
                ch = self.stdscr.get_wch()
            except curses.error:
                continue

            if isinstance(ch, int):
                action = {curses.KEY_UP: "up", curses.KEY_DOWN: "down",
                          curses.KEY_PPAGE: "pgup", curses.KEY_NPAGE: "pgdn",
                          curses.KEY_HOME: "home", curses.KEY_END: "end",
                          curses.KEY_ENTER: "enter", curses.KEY_BACKSPACE: "back",
                          curses.KEY_DC: "back", curses.KEY_RESIZE: "resize"}.get(ch)
            elif ch == "\x1b":
                action = self._read_escape()
            elif ch in ("\n", "\r"):
                action = "enter"
            elif ch in ("\x7f", "\x08"):
                action = "back"
            elif ch.isprintable():
                self.query += ch
                continue
            else:
                action = None

            if action == "up":
                self.sel -= 1
            elif action == "down":
                self.sel += 1
            elif action == "pgup":
                self.sel -= 10
            elif action == "pgdn":
                self.sel += 10
            elif action == "home":
                self.sel = 0
            elif action == "end":
                self.sel = n - 1 if n else 0
            elif action == "back":
                self.query = self.query[:-1]
            elif action == "resize":
                self.offset = 0
            elif action == "enter":
                if n:
                    return matches[self.sel]
            elif action == "esc":
                return None

    # ── 对外接口 ──
    @staticmethod
    def choose(title, items):
        """弹出列表让用户上下选择；返回选中项在 items 中的下标，取消返回 None。"""
        if not items:
            return None
        try:
            return curses.wrapper(lambda s: Picker(s, title, items).run())
        except (KeyboardInterrupt, curses.error):
            return None
