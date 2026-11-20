"""主界面底部的一行状态提示（步骤结果的展示位置，避免直接打印到终端）。"""


class Status:
    message = ""

    @classmethod
    def set(cls, msg):
        cls.message = msg

    @classmethod
    def clear(cls):
        cls.message = ""
