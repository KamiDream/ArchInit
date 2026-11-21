#!/usr/bin/env python3
# ArchInit — 统一 TUI 安装器（Python / curses）
#
# 代码已按模块拆分为 ZClass/ 包中的类：
#   ZClass/config.py     路径与品牌常量、ESCDELAY
#   ZClass/style.py      Style（ANSI 着色）
#   ZClass/shell.py      Shell（命令执行 / 文件读写）
#   ZClass/model.py      Step、Category
#   ZClass/steps/*.py    各分类步骤类（Desktop/Basic/Kvm/Gpu/Terminal/LoginManager/Patch/Backend）
#   ZClass/catalog.py    Catalog（组装分类）
#   ZClass/ui.py         UI（curses 两栏界面）
#   ZClass/app.py        App（启动、sudo、进入界面）
#
# 运行：python3 archinit.py（需在 Arch Linux 上，带 sudo 权限）
# 交互：↑/↓ 选择，Enter 执行，q / Esc 返回上一级。

import sys

from ZClass.app import App

if __name__ == "__main__":
    sys.exit(App().run())
