"""普通终端（非 curses）下的 ANSI 着色。"""


class Style:
    @staticmethod
    def c(text, code):
        return f"\033[{code}m{text}\033[0m"

    @classmethod
    def green_bold(cls, t):
        return cls.c(t, "1;32")

    @classmethod
    def red_bold(cls, t):
        return cls.c(t, "1;31")

    @classmethod
    def yellow(cls, t):
        return cls.c(t, "33")
