# -*- coding: utf-8 -*-
"""植物大战僵尸·杂交版 —— 全局常量与配置"""
import os
import pygame

# 屏幕
SCREEN_W, SCREEN_H = 1280, 720
FPS = 60

# 草坪网格：5 行 x 9 列
COLS, ROWS = 9, 5
LAWN_X = 220          # 第一列左边缘
LAWN_Y = 110          # 第一行上边缘
CELL_W = 100          # 每格宽
CELL_H = 110          # 每格高

# 颜色
BG_TOP = (92, 148, 60)
BG_BOT = (72, 124, 48)
LAWN_A = (120, 178, 78)
LAWN_B = (110, 168, 70)
PATH = (188, 158, 110)
SKY = (174, 218, 250)
WHITE = (255, 255, 255)
BLACK = (28, 28, 32)
SUN_COLOR = (255, 222, 70)
HUD_BG = (60, 44, 28)
HUD_BG2 = (88, 64, 40)
RED = (220, 70, 70)
BLUE = (90, 150, 240)
GREEN = (80, 200, 90)
GRAY = (90, 90, 100)

# 游戏数值
STARTING_SUN = 150
SUN_DROP_INTERVAL = 8.0       # 天降阳光间隔（秒）
SUN_DROP_VALUE = 25
SUN_LIFETIME = 9.0            # 阳光在地上存活秒数
SUN_COLLECT_RADIUS = 36

# 波次
WAVE_TOTAL = 10               # 总波数
WAVE_PREPARE = 6.0            # 每波准备时间
ZOMBIE_BASE_SPEED = 22        # 像素/秒
PROGRESS_TO_WIN = 1.0

# 植物卡片冷却（秒）与价格
# 字典在 plants 模块中定义

# 字体
_FONT_PATHS = [
    "C:/Windows/Fonts/msyhbd.ttc",   # 微软雅黑 Bold
    "C:/Windows/Fonts/msyh.ttc",     # 微软雅黑
    "C:/Windows/Fonts/simhei.ttf",
    "C:/Windows/Fonts/simsun.ttc",
    "/System/Library/Fonts/PingFang.ttc",
    "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
]


def get_font(size, bold=False):
    """统一获取字体，兼容中英文。
    优先直接加载字体文件（绕过部分平台 SysFont 枚举 bug）。"""
    for p in _FONT_PATHS:
        if os.path.exists(p):
            try:
                f = pygame.font.Font(p, size)
                f.set_bold(bold)
                return f
            except Exception:
                continue
    try:
        return pygame.font.SysFont(
            ["microsoftyahei", "simhei", "simsun", "dejavusans", "arial"],
            size, bold=bold)
    except Exception:
        return pygame.font.Font(None, size)
