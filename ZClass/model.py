"""步骤与分类的数据模型。"""


class Step:
    def __init__(self, title, func):
        self.title = title
        self.func = func


class Category:
    def __init__(self, title, steps, warning=None, dividers=None):
        self.title = title
        self.steps = steps
        self.warning = warning or []
        self.dividers = dividers or set()
        self.completed = [False] * len(steps)
        self.selected = 0  # 记住本分类上次高亮的步骤位置
