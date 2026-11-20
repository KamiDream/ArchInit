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


class FreeText(str):
    """选择器返回的特殊值：用户想把输入的文字直接当命令用（Tab 或无匹配时 Enter）。"""


class Picker:
    PAIR = 20  # 与主界面配色对错开
    PAIR_WARN = 21
    last_query = ""  # 上一次选择器里的过滤词（供调用方记忆）
    _shared_stdscr = None  # 主界面调用 bind() 后，选择器复用它，不嵌套 initscr/endwin

    def __init__(self, stdscr, title, items, initial=0, query="", allow_free=False,
                 subtitle="", notice=""):
        self.stdscr = stdscr
        self.title = title
        self.items = items  # [(主文本, 副文本), ...]
        self.query = query
        self.sel = 0
        self.offset = 0
        self.want = initial  # 初次显示的条目（items 下标），过滤后重新定位
        self.allow_free = allow_free  # 允许把输入内容当作“列表外的命令”
        self.subtitle = subtitle  # 标题下的一行说明
        self.notice = notice  # 黄色提示行（如“未找到该命令”）

    # ── 颜色 ──
    def _init_colors(self):
        if not curses.has_colors():
            return
        try:
            curses.start_color()
            curses.init_pair(self.PAIR, curses.COLOR_CYAN, -1)
            curses.init_pair(self.PAIR_WARN, curses.COLOR_YELLOW, -1)
            self.attr_sel = curses.color_pair(self.PAIR) | curses.A_REVERSE
            self.attr_warn = curses.color_pair(self.PAIR_WARN) | curses.A_BOLD
        except curses.error:
            self.attr_sel = curses.A_REVERSE
            self.attr_warn = curses.A_BOLD

    def _attr_sel(self):
        return getattr(self, "attr_sel", curses.A_REVERSE)

    def _attr_warn(self):
        return getattr(self, "attr_warn", curses.A_BOLD)

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

        y = 0
        self._put(y, 1, self.title, curses.A_BOLD)
        y += 1
        if self.subtitle:
            self._put(y, 1, self.subtitle)
            y += 1
        prompt = "过滤 / Filter: "
        self._put(y, 1, prompt + self.query + "_")
        count = f"{len(matches)}/{len(self.items)}"
        self._put(y, max(1, w - 2 - len(count)), count)
        y += 1
        for x in range(w - 1):
            self._put(y, x, "─")
        y += 1
        if self.notice:
            self._put(y, 1, self.notice, self._attr_warn())
            y += 1

        body_top = y
        footer_y = h - 2
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
        elif body_h > 0 and not self.notice:
            if self.allow_free and self.query.strip():
                self._put(body_top, 1, f"无匹配，按 Enter/Tab 直接当命令用 / no match — Enter/Tab uses “{self.query.strip()}”",
                          curses.A_BOLD)
                self._put(body_top + 1, 1, "也可输入完整路径（如 /usr/bin/xxx）/ a full path works too")
            else:
                self._put(body_top, 1, "无匹配 / no match", curses.A_BOLD)

        if self.offset > 0:
            self._put(body_top, max(0, w - 2), "↑")
        if self.offset + body_h < len(matches):
            self._put(footer_y - 1, max(0, w - 2), "↓")

        self._put(footer_y, 0, "═" * (w - 1))
        if self.allow_free:
            hint = "↑/↓ 选择  •  输入过滤  •  Tab 当命令用  •  Enter 确定  •  Esc 取消"
        else:
            hint = "↑/↓ 选择  •  输入过滤  •  Enter 确定  •  Esc 取消"
        self._put(footer_y + 1, 1, hint)
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
            if self.want is not None:
                # 首次：把上次选中的条目映射到当前（可能已过滤的）列表位置
                self.sel = matches.index(self.want) if self.want in matches else 0
                self.want = None
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
                          curses.KEY_DC: "back", curses.KEY_RESIZE: "resize",
                          curses.KEY_BTAB: "free"}.get(ch)
            elif ch == "\x1b":
                action = self._read_escape()
            elif ch == "\t":
                action = "free"
            elif ch in ("\n", "\r"):
                action = "enter"
            elif ch in ("\x7f", "\x08"):
                action = "back"
            elif ch.isprintable():
                self.query += ch
                self.notice = ""
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
                self.notice = ""
            elif action == "resize":
                self.offset = 0
            elif action == "enter":
                if n:
                    return matches[self.sel]
                if self.allow_free and self.query.strip():
                    return FreeText(self.query)
            elif action == "free":
                if self.allow_free and self.query.strip():
                    return FreeText(self.query)
            elif action == "esc":
                return None

    # ── 对外接口 ──
    @classmethod
    def bind(cls, stdscr):
        """由主界面调用：让选择器复用主界面的窗口，避免嵌套 initscr/endwin 破坏终端状态。"""
        cls._shared_stdscr = stdscr

    @classmethod
    def choose(cls, title, items, initial=0, query="", allow_free=False,
               subtitle="", notice=""):
        """弹出列表让用户上下选择；返回选中项下标、FreeText（输入内容当命令）或 None（取消）。

        initial:    初次高亮的条目下标（用于「返回时记住上次选择」）
        query:      初始过滤词（同样用于记忆）
        allow_free: 允许按 Tab（或无匹配时 Enter）把输入内容当作列表外的命令
        subtitle:   标题下方的说明行（显示在列表界面里，不直接打印到终端）
        notice:     黄色提示行（如“未找到该命令”）；用户修改输入后自动清除
        调用后可从 Picker.last_query 取到本次的过滤词。
        """
        if cls._shared_stdscr is not None:
            return cls._choose_shared(cls._shared_stdscr, title, items, initial, query,
                                      allow_free, subtitle, notice)
        return cls._choose_standalone(title, items, initial, query, allow_free,
                                      subtitle, notice)

    @classmethod
    def _choose_shared(cls, stdscr, title, items, initial, query, allow_free, subtitle, notice):
        """复用主界面窗口：步骤里已经 endwin 过，这里 reset 进来，结束再 endwin 回去。"""
        try:
            curses.reset_prog_mode()
            stdscr.clear()
            stdscr.refresh()
        except curses.error:
            pass
        p = Picker(stdscr, title, items, initial, query, allow_free, subtitle, notice)
        result = None
        try:
            result = p.run()
        except (KeyboardInterrupt, curses.error):
            result = None
        finally:
            cls.last_query = p.query
            try:
                stdscr.timeout(-1)
                curses.endwin()
            except curses.error:
                pass
        return result

    @classmethod
    def _choose_standalone(cls, title, items, initial, query, allow_free, subtitle, notice):
        """没有主界面时自己开一块屏幕（脚本/测试用）。"""
        holder = {}

        def main(stdscr):
            p = Picker(stdscr, title, items, initial, query, allow_free, subtitle, notice)
            holder["p"] = p
            return p.run()

        try:
            result = curses.wrapper(main)
        except (KeyboardInterrupt, curses.error):
            result = None
        p = holder.get("p")
        cls.last_query = p.query if p is not None else query
        return result
