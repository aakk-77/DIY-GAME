# -*- coding: utf-8 -*-
"""程序化绘制所有图形资源，无需外部图片。
所有 draw_* 函数返回一个带透明通道的 pygame.Surface。"""
import math
import pygame
from . import constants as C


def _new(w, h):
    return pygame.Surface((w, h), pygame.SRCALPHA).convert_alpha()


# ---------- 通用辅助 ----------
def circle(surf, color, pos, r, width=0):
    pygame.draw.circle(surf, color, pos, r, width)


def ell(surf, color, rect, width=0):
    pygame.draw.ellipse(surf, color, rect, width)


# ====================== 植物 ======================
def draw_sunflower():
    s = _new(80, 86)
    # 茎
    pygame.draw.rect(s, (60, 150, 70), (37, 48, 6, 34))
    # 叶
    ell(s, (74, 180, 84), (16, 58, 28, 16))
    ell(s, (74, 180, 84), (38, 64, 28, 16))
    # 花瓣
    cx, cy, R = 40, 30, 16
    for i in range(12):
        a = i * math.pi / 6
        px = cx + math.cos(a) * R
        py = cy + math.sin(a) * R
        circle(s, (255, 200, 40), (int(px), int(py)), 11)
    # 花心
    circle(s, (120, 80, 30), (cx, cy), 14)
    circle(s, (90, 60, 24), (cx, cy), 14, 2)
    # 眼
    circle(s, (40, 30, 20), (cx - 5, cy - 2), 2)
    circle(s, (40, 30, 20), (cx + 5, cy - 2), 2)
    return s


def draw_peashooter():
    s = _new(80, 84)
    pygame.draw.rect(s, (60, 150, 70), (37, 40, 6, 40))
    ell(s, (74, 180, 84), (14, 52, 28, 16))
    ell(s, (74, 180, 84), (40, 60, 28, 16))
    # 头
    circle(s, (80, 200, 90), (40, 28), 20)
    circle(s, (60, 160, 70), (40, 28), 20, 2)
    # 嘴管
    pygame.draw.rect(s, (70, 170, 80), (58, 24, 16, 9))
    pygame.draw.ellipse(s, (50, 130, 60), (70, 22, 12, 13))
    circle(s, (70, 170, 80), (40, 28), 7, 0)
    circle(s, (40, 120, 50), (40, 28), 7, 2)
    circle(s, (30, 24, 20), (52, 24), 2)
    return s


def draw_wallnut():
    s = _new(76, 80)
    ell(s, (180, 120, 70), (8, 8, 60, 64))
    ell(s, (140, 90, 50), (8, 8, 60, 64), 3)
    ell(s, (220, 170, 120), (22, 26, 16, 10))  # 高光
    # 脸
    circle(s, (50, 35, 25), (28, 38), 3)
    circle(s, (50, 35, 25), (48, 38), 3)
    pygame.draw.arc(s, (50, 35, 25), (28, 42, 20, 14), math.pi, 2 * math.pi, 2)
    return s


def draw_snowpea():
    s = _new(80, 84)
    pygame.draw.rect(s, (60, 150, 70), (37, 40, 6, 40))
    ell(s, (74, 180, 84), (14, 52, 28, 16))
    ell(s, (74, 180, 84), (40, 60, 28, 16))
    circle(s, (150, 210, 245), (40, 28), 20)
    circle(s, (90, 160, 200), (40, 28), 20, 2)
    pygame.draw.rect(s, (130, 190, 230), (58, 24, 16, 9))
    pygame.draw.ellipse(s, (90, 150, 190), (70, 22, 12, 13))
    circle(s, (130, 190, 230), (40, 28), 7, 0)
    circle(s, (90, 140, 180), (40, 28), 7, 2)
    circle(s, (40, 30, 30), (52, 24), 2)
    # 冰晶
    for (px, py) in [(28, 14), (50, 12), (60, 36)]:
        pygame.draw.line(s, (220, 240, 255), (px - 3, py), (px + 3, py), 1)
        pygame.draw.line(s, (220, 240, 255), (px, py - 3), (px, py + 3), 1)
    return s


def draw_repeater():
    s = _new(80, 84)
    pygame.draw.rect(s, (60, 150, 70), (37, 40, 6, 40))
    ell(s, (74, 180, 84), (14, 52, 28, 16))
    ell(s, (74, 180, 84), (40, 60, 28, 16))
    circle(s, (70, 170, 80), (40, 28), 20)
    circle(s, (50, 120, 60), (40, 28), 20, 2)
    pygame.draw.rect(s, (60, 150, 70), (58, 20, 16, 8))
    pygame.draw.rect(s, (60, 150, 70), (58, 30, 16, 8))
    pygame.draw.ellipse(s, (44, 110, 54), (70, 18, 12, 11))
    pygame.draw.ellipse(s, (44, 110, 54), (70, 28, 12, 11))
    circle(s, (40, 30, 20), (52, 24), 2)
    return s


def draw_cherrybomb():
    s = _new(78, 78)
    pygame.draw.rect(s, (60, 130, 60), (36, 40, 6, 30))
    ell(s, (74, 170, 80), (20, 56, 30, 14))
    circle(s, (210, 50, 60), (26, 34), 17)
    circle(s, (160, 30, 40), (26, 34), 17, 2)
    circle(s, (210, 50, 60), (50, 32), 17)
    circle(s, (160, 30, 40), (50, 32), 17, 2)
    pygame.draw.line(s, (90, 60, 30), (38, 30), (30, 14), 3)
    pygame.draw.line(s, (90, 60, 30), (42, 30), (54, 14), 3)
    ell(s, (90, 180, 80), (24, 8, 20, 10))
    circle(s, (255, 240, 180), (22, 28), 3)
    circle(s, (255, 240, 180), (54, 26), 3)
    return s


def draw_chomper():
    s = _new(90, 84)
    pygame.draw.rect(s, (60, 130, 60), (42, 48, 6, 32))
    ell(s, (74, 160, 80), (20, 60, 28, 14))
    # 头/下颚
    ell(s, (150, 70, 130), (10, 14, 56, 30))
    ell(s, (110, 40, 100), (10, 14, 56, 30), 2)
    ell(s, (180, 90, 160), (8, 30, 60, 24))  # 下嘴
    pygame.draw.polygon(s, (255, 240, 200),
                        [(16, 34), (24, 50), (30, 34)])
    pygame.draw.polygon(s, (255, 240, 200),
                        [(46, 34), (54, 50), (60, 34)])
    circle(s, (40, 20, 20), (24, 22), 3)
    circle(s, (40, 20, 20), (52, 22), 3)
    return s


# ---------- 杂交创新植物 ----------
def draw_sunshooter():
    """阳光射手：向日葵+豌豆 杂交"""
    s = _new(82, 86)
    pygame.draw.rect(s, (60, 150, 70), (39, 46, 6, 36))
    ell(s, (74, 180, 84), (16, 58, 28, 16))
    ell(s, (74, 180, 84), (40, 64, 28, 16))
    cx, cy = 41, 30
    for i in range(12):
        a = i * math.pi / 6
        circle(s, (255, 190, 50),
               (int(cx + math.cos(a) * 15), int(cy + math.sin(a) * 15)), 10)
    circle(s, (90, 200, 95), (cx, cy), 14)
    circle(s, (60, 150, 70), (cx, cy), 14, 2)
    # 豌豆嘴
    pygame.draw.rect(s, (70, 170, 80), (55, 26, 16, 9))
    pygame.draw.ellipse(s, (50, 130, 60), (67, 24, 12, 13))
    circle(s, (40, 30, 20), (cx + 10, cy - 2), 2)
    circle(s, (40, 30, 20), (cx - 4, cy - 2), 2)
    return s


def draw_frostfire():
    """冰火双生：左冰右火 双管"""
    s = _new(86, 84)
    pygame.draw.rect(s, (60, 150, 70), (42, 40, 6, 40))
    ell(s, (74, 180, 84), (16, 52, 28, 16))
    ell(s, (74, 180, 84), (42, 60, 28, 16))
    # 左半冰
    pygame.draw.polygon(s, (150, 210, 245),
                        [(43, 8), (62, 8), (62, 48), (43, 48)])
    circle(s, (150, 210, 245), (43, 28), 20)
    circle(s, (90, 160, 200), (43, 28), 20, 2)
    # 右半火
    circle(s, (235, 110, 50), (60, 28), 20)
    circle(s, (180, 70, 30), (60, 28), 20, 2)
    # 双管
    pygame.draw.rect(s, (130, 190, 230), (24, 24, 14, 8))
    pygame.draw.ellipse(s, (90, 150, 190), (10, 22, 12, 12))
    pygame.draw.rect(s, (235, 110, 50), (66, 24, 14, 8))
    pygame.draw.ellipse(s, (190, 70, 30), (78, 22, 12, 12))
    # 火苗
    pygame.draw.polygon(s, (255, 220, 90), [(64, 8), (60, 18), (68, 18)])
    circle(s, (40, 30, 20), (52, 24), 2)
    return s


def draw_gatlingnut():
    """机枪坚果：坚果+连发"""
    s = _new(80, 80)
    ell(s, (180, 120, 70), (8, 8, 60, 64))
    ell(s, (140, 90, 50), (8, 8, 60, 64), 3)
    ell(s, (220, 170, 120), (22, 26, 16, 10))
    # 三根枪管
    pygame.draw.rect(s, (70, 70, 80), (60, 20, 18, 6))
    pygame.draw.rect(s, (70, 70, 80), (60, 32, 18, 6))
    pygame.draw.rect(s, (70, 70, 80), (60, 44, 18, 6))
    pygame.draw.ellipse(s, (50, 50, 60), (74, 18, 10, 10))
    pygame.draw.ellipse(s, (50, 50, 60), (74, 30, 10, 10))
    pygame.draw.ellipse(s, (50, 50, 60), (74, 42, 10, 10))
    circle(s, (50, 35, 25), (26, 36), 3)
    circle(s, (50, 35, 25), (42, 36), 3)
    pygame.draw.arc(s, (50, 35, 25), (24, 40, 22, 16), math.pi, 2 * math.pi, 2)
    return s


def draw_bombsunflower():
    """炸弹向日葵：向日葵+樱桃"""
    s = _new(80, 86)
    pygame.draw.rect(s, (60, 150, 70), (37, 48, 6, 34))
    ell(s, (74, 180, 84), (16, 58, 28, 16))
    ell(s, (74, 180, 84), (40, 64, 28, 16))
    cx, cy, R = 40, 30, 16
    for i in range(12):
        a = i * math.pi / 6
        circle(s, (235, 70, 70),
               (int(cx + math.cos(a) * R), int(cy + math.sin(a) * R)), 11)
    circle(s, (180, 40, 40), (cx, cy), 14)
    circle(s, (130, 20, 20), (cx, cy), 14, 2)
    # 引线
    pygame.draw.line(s, (90, 60, 30), (cx, cy - 14), (cx + 6, cy - 24), 3)
    circle(s, (255, 220, 80), (cx + 7, cy - 25), 3)
    circle(s, (40, 20, 20), (cx - 5, cy - 2), 2)
    circle(s, (40, 20, 20), (cx + 5, cy - 2), 2)
    return s


# ====================== 僵尸 ======================
def _draw_zombie_body(s, skin, shirt, x, y):
    # 腿
    pygame.draw.rect(s, (70, 70, 90), (x + 8, y + 50, 10, 22))
    pygame.draw.rect(s, (70, 70, 90), (x + 24, y + 50, 10, 22))
    # 身体
    pygame.draw.rect(s, shirt, (x + 6, y + 26, 30, 28))
    pygame.draw.rect(s, (40, 40, 60), (x + 6, y + 26, 30, 28), 2)
    # 手臂前伸
    pygame.draw.rect(s, skin, (x + 32, y + 30, 20, 8))
    pygame.draw.rect(s, (40, 40, 60), (x + 32, y + 30, 20, 8), 1)
    pygame.draw.rect(s, skin, (x + 4, y + 30, 10, 8))
    # 头
    circle(s, skin, (x + 21, y + 14), 13)
    circle(s, (90, 110, 70), (x + 21, y + 14), 13, 2)
    # 眼
    circle(s, (30, 20, 20), (x + 17, y + 12), 2)
    circle(s, (30, 20, 20), (x + 25, y + 12), 2)
    # 嘴
    pygame.draw.rect(s, (60, 20, 20), (x + 17, y + 18, 9, 3))


def draw_zombie():
    s = _new(60, 80)
    _draw_zombie_body(s, (170, 200, 150), (110, 90, 130), 8, 0)
    return s


def draw_cone_zombie():
    s = _new(60, 96)
    _draw_zombie_body(s, (170, 200, 150), (110, 90, 130), 8, 16)
    # 路障
    pygame.draw.polygon(s, (240, 150, 60),
                        [(8, 18), (34, 18), (26, 0), (16, 0)])
    pygame.draw.polygon(s, (180, 100, 30),
                        [(8, 18), (34, 18), (26, 0), (16, 0)], 2)
    pygame.draw.line(s, (220, 220, 220), (12, 14), (30, 14), 2)
    pygame.draw.line(s, (220, 220, 220), (14, 9), (28, 9), 2)
    return s


def draw_bucket_zombie():
    s = _new(60, 96)
    _draw_zombie_body(s, (170, 200, 150), (110, 90, 130), 8, 16)
    # 铁桶
    pygame.draw.rect(s, (150, 150, 160), (6, 2, 30, 20))
    pygame.draw.rect(s, (90, 90, 100), (6, 2, 30, 20), 2)
    pygame.draw.rect(s, (180, 180, 190), (9, 6, 24, 4))
    pygame.draw.rect(s, (90, 90, 100), (6, 16, 30, 3))
    return s


def draw_flag_zombie():
    s = _new(72, 80)
    _draw_zombie_body(s, (180, 210, 160), (150, 60, 60), 8, 0)
    # 旗杆+旗
    pygame.draw.line(s, (80, 60, 30), (50, 56), (50, 6), 2)
    pygame.draw.polygon(s, (220, 70, 70),
                        [(50, 6), (70, 12), (50, 20)])
    pygame.draw.polygon(s, (160, 30, 30),
                        [(50, 6), (70, 12), (50, 20)], 1)
    return s


# ====================== 子弹与阳光 ======================
def draw_pea(color=(90, 200, 90)):
    s = _new(20, 20)
    circle(s, color, (10, 10), 8)
    circle(s, (max(0, color[0] - 40), max(0, color[1] - 40),
               max(0, color[2] - 40)), (10, 10), 8, 2)
    circle(s, (255, 255, 255), (7, 7), 2)
    return s


def draw_sun():
    s = _new(46, 46)
    cx, cy = 23, 23
    for i in range(12):
        a = i * math.pi / 6
        px = cx + math.cos(a) * 18
        py = cy + math.sin(a) * 18
        pygame.draw.line(s, (255, 230, 120),
                         (int(px), int(py)),
                         (int(cx + math.cos(a) * 12),
                          int(cy + math.sin(a) * 12)), 2)
    circle(s, (255, 230, 110), (cx, cy), 12)
    circle(s, (255, 250, 200), (cx, cy), 8)
    return s


# ====================== 背景 ======================
def make_background():
    bg = pygame.Surface((C.SCREEN_W, C.SCREEN_H)).convert()
    # 上方天空
    bg.fill(C.SKY, (0, 0, C.SCREEN_W, 90))
    # 草坪渐变行
    for r in range(C.ROWS):
        col = C.LAWN_A if r % 2 == 0 else C.LAWN_B
        rect = (C.LAWN_X, C.LAWN_Y + r * C.CELL_H,
                C.COLS * C.CELL_W, C.CELL_H)
        bg.fill(col, rect)
    # 网格细线
    for r in range(C.ROWS + 1):
        y = C.LAWN_Y + r * C.CELL_H
        pygame.draw.line(bg, (60, 110, 50),
                         (C.LAWN_X, y), (C.LAWN_X + C.COLS * C.CELL_W, y), 1)
    for c in range(C.COLS + 1):
        x = C.LAWN_X + c * C.CELL_W
        pygame.draw.line(bg, (60, 110, 50),
                         (x, C.LAWN_Y), (x, C.LAWN_Y + C.ROWS * C.CELL_H), 1)
    # 左侧房屋区/泥土带
    bg.fill(C.PATH, (0, C.LAWN_Y, C.LAWN_X, C.ROWS * C.CELL_H))
    # 顶部 HUD 底色
    bg.fill(C.HUD_BG, (0, 0, C.SCREEN_W, 90))
    bg.fill(C.HUD_BG2, (0, 86, C.SCREEN_W, 4))
    # 房屋
    pygame.draw.rect(bg, (180, 120, 80), (40, 130, 150, 420))
    pygame.draw.polygon(bg, (130, 70, 50),
                        [(30, 140), (110, 70), (200, 140)])
    pygame.draw.rect(bg, (90, 60, 40), (90, 320, 50, 230))
    pygame.draw.rect(bg, (60, 40, 30), (90, 320, 50, 230), 3)
    return bg


# 卡片缩略图缓存
_CACHE = {}


def get_plant_icon(key):
    if key not in _CACHE:
        _CACHE[key] = _icon_for(key)
    return _CACHE[key]


def _icon_for(key):
    table = {
        "sunflower": draw_sunflower, "peashooter": draw_peashooter,
        "wallnut": draw_wallnut, "snowpea": draw_snowpea,
        "repeater": draw_repeater, "cherrybomb": draw_cherrybomb,
        "chomper": draw_chomper,
        "sunshooter": draw_sunshooter, "frostfire": draw_frostfire,
        "gatlingnut": draw_gatlingnut, "bombsunflower": draw_bombsunflower,
    }
    surf = table[key]()
    return pygame.transform.smoothscale(surf, (54, 54))
