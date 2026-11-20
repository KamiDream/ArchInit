"""项目路径、品牌常量与全局环境设置。"""
import os

# 项目根目录（ZClass/ 的上一级），用于定位 fastfetch/ starship/ fcitx5/ 等配置目录
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOME = os.path.expanduser("~")

# 品牌标识：Kami(淡蓝) + Dream(淡粉)
BRAND_LEFT = "Kami"
BRAND_RIGHT = "Dream"

# 减少按 ESC 时的卡顿：ncurses 默认等待 1000ms 判断是否为转义序列开头。
# 需在 curses 初始化前设置。
os.environ.setdefault("ESCDELAY", "25")
