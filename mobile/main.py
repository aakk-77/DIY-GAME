# -*- coding: utf-8 -*-
"""植物大战僵尸·杂交版 —— Kivy App 入口（手机版）。
触屏操作：点卡片选植物 → 点草地种植；点阳光收集；铲子可移除。
依赖：kivy。打包 Android APK 见同级 buildozer.spec 与 ../BUILD_APK.md。"""
import os
import sys
import math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def _bootstrap_dlls():
    """让 kivy_deps 的 SDL2/ANGLE/GLEW DLL 可被加载。
    正常 site-packages 安装时 kivy_deps 会自动处理；此函数兼容 --target 安装。"""
    try:
        import kivy_deps.sdl2 as _sdl2
        import kivy_deps.angle as _angle
        import kivy_deps.glew as _glew
    except Exception:
        return
    for dep in (_sdl2, _angle, _glew):
        for d in getattr(dep, "dep_bins", []):
            if os.path.isdir(d) and hasattr(os, "add_dll_directory"):
                try:
                    os.add_dll_directory(d)
                except Exception:
                    pass
    # 兜底：相对 kivy_deps 包查找 share/*/bin
    try:
        import kivy_deps
        root = os.path.dirname(kivy_deps.__file__)
        for sub in ("../share/sdl2/bin", "../share/angle/bin",
                    "../share/glew/bin"):
            p = os.path.abspath(os.path.join(root, sub))
            if os.path.isdir(p):
                os.environ["PATH"] = p + os.pathsep + os.environ.get("PATH", "")
                if hasattr(os, "add_dll_directory"):
                    os.add_dll_directory(p)
    except Exception:
        pass


_bootstrap_dlls()

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import (Color, Rectangle, Ellipse, Line, Triangle,
                           PushMatrix, PopMatrix, Rotate, Scale)
from kivy.clock import Clock
from kivy.utils import get_color_from_hex as hx

from core import (W, H, COLS, ROWS, LAWN_X, LAWN_Y, CELL_W, CELL_H,
                  C_SKY, C_GRASS_A, C_GRASS_B, C_PATH, C_HUD, C_HUD2, C_SUN,
                  C_WHITE, C_BLACK, PLANTS, SEED_BAR, WAVE_TOTAL, World)

CARD_W, CARD_H = 78, 96
CARD_X0 = 150
CARD_Y = 2
CARD_GAP = 6

# 中文字体：优先使用本地打包字体（APK 内可用），其次桌面系统字体。
# GitHub Actions 打包时会下载 NotoSansSC-Regular.otf 到本目录并重命名为 font.otf。
_HERE = os.path.dirname(os.path.abspath(__file__))
_FONT_CANDIDATES = [
    os.path.join(_HERE, "font.otf"),
    os.path.join(_HERE, "font.ttf"),
    os.path.join(_HERE, "font.ttc"),
    os.path.join(_HERE, "NotoSansSC-Regular.otf"),
    "C:/Windows/Fonts/msyh.ttc",
    "C:/Windows/Fonts/simhei.ttf",
    "/System/Library/Fonts/PingFang.ttc",
    "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
    "DejaVuSans.ttf",
]
CJK_FONT = next((p for p in _FONT_CANDIDATES
                 if os.path.exists(p)), None)


def card_rect(i):
    return (CARD_X0 + i * (CARD_W + CARD_GAP), CARD_Y, CARD_W, CARD_H)


def shovel_rect():
    return (CARD_X0 + len(SEED_BAR) * (CARD_W + CARD_GAP) + 8,
            CARD_Y + 10, 56, 76)


class GameView(Widget):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.world = World()
        self.scene = "menu"
        self.paused = False
        self.bind(size=self._resize, pos=self._resize)
        Clock.schedule_interval(self._tick, 1 / 60)

    def _resize(self, *_):
        self._draw()

    def reset(self):
        self.world = World()
        self.paused = False

    def _tick(self, dt):
        if self.scene == "playing" and not self.paused:
            self.world.update(min(dt, 1 / 30))
        self._draw()

    # ---------- 输入 ----------
    def on_touch_down(self, touch):
        mx, my = self._to_logical(touch.x, touch.y)
        if self.scene == "menu":
            self._menu_click(mx, my)
            return True
        if self.scene == "help":
            if self._hit(mx, my, W // 2 - 130, H - 88, 260, 56):
                self.scene = "menu"
            return True
        # playing
        if self.world.state != "playing" or self.paused:
            # 结算界面：点击重开
            if self.world.state != "playing":
                self.reset()
            return True
        if self.world.collect_sun_at(mx, my):
            return True
        for i, kind in enumerate(SEED_BAR):
            rx, ry, rw, rh = card_rect(i)
            if self._hit(mx, my, rx, ry, rw, rh):
                d = PLANTS[kind]
                if self.world.sun >= d["cost"] and \
                        self.world.cooldowns.get(kind, 0) <= 0:
                    self.world.selected = kind
                    self.world.shovel = False
                return True
        sx, sy, sw, sh = shovel_rect()
        if self._hit(mx, my, sx, sy, sw, sh):
            self.world.shovel = not self.world.shovel
            self.world.selected = None
            return True
        cell = self.world.cell_at(mx, my)
        if cell:
            col, row = cell
            if self.world.shovel:
                self.world.try_shovel(col, row)
            elif self.world.selected:
                self.world.try_plant(col, row)
        return True

    def keyboard_on_key_down(self, _w, key, *_a):
        if key == 27:  # ESC / 返回
            if self.scene == "playing":
                self.paused = not self.paused
            else:
                self.scene = "menu"
        elif key == ord('r') and self.scene == "playing":
            self.reset()
        return True

    def _menu_click(self, mx, my):
        for cy, key in [(430, "play"), (510, "help"), (590, "quit")]:
            if self._hit(mx, my, W // 2 - 130, cy - 28, 260, 56):
                if key == "play":
                    self.reset()
                    self.scene = "playing"
                elif key == "help":
                    self.scene = "help"
                else:
                    App.get_running_app().stop()
                return

    @staticmethod
    def _hit(mx, my, x, y, w, h):
        return x <= mx <= x + w and y <= my <= y + h

    def _to_logical(self, tx, ty):
        """把实际控件坐标映射到逻辑分辨率 W x H。"""
        sx = self.width / W
        sy = self.height / H
        return tx / sx, ty / sy

    # ---------- 绘制 ----------
    def _draw(self):
        c = self.canvas
        c.clear()
        sx = self.width / W
        sy = self.height / H
        with c:
            PushMatrix()
            Scale(sx, sy, 1)
            if self.scene == "menu":
                self._draw_menu()
            elif self.scene == "help":
                self._draw_help()
            else:
                self._draw_game()
            PopMatrix()

    # 草坪背景
    def _bg(self):
        Color(*C_SKY)
        Rectangle(pos=(0, 0), size=(W, 90))
        Color(*C_HUD)
        Rectangle(pos=(0, 0), size=(W, 90))
        Color(*C_HUD2)
        Rectangle(pos=(0, 86), size=(W, 4))
        for r in range(ROWS):
            Color(*[C_GRASS_A if r % 2 == 0 else C_GRASS_B][0])
            Rectangle(pos=(LAWN_X, LAWN_Y + r * CELL_H),
                      size=(COLS * CELL_W, CELL_H))
        Color(*C_PATH)
        Rectangle(pos=(0, LAWN_Y), size=(LAWN_X, ROWS * CELL_H))
        # 网格线
        Color(0.24, 0.43, 0.20, 1)
        for r in range(ROWS + 1):
            y = LAWN_Y + r * CELL_H
            Line(points=[LAWN_X, y, LAWN_X + COLS * CELL_W, y], width=1)
        for cc in range(COLS + 1):
            x = LAWN_X + cc * CELL_W
            Line(points=[x, LAWN_Y, x, LAWN_Y + ROWS * CELL_H], width=1)
        # 房屋
        Color(0.71, 0.47, 0.31)
        Rectangle(pos=(40, 130), size=(150, 420))
        Color(0.51, 0.27, 0.20)
        Triangle((30, 140), (110, 70), (200, 140))
        Color(0.35, 0.24, 0.16)
        Rectangle(pos=(90, 320), size=(50, 230))

    def _draw_game(self):
        self._bg()
        # 实体
        for p in self.world.plants:
            self._draw_plant(p)
        for pea in self.world.peas:
            self._draw_pea(pea)
        for z in self.world.zombies:
            self._draw_zombie(z)
        for ex in self.world.explosions:
            self._draw_explosion(ex)
        for s in self.world.suns:
            self._draw_sun(s)
        self._draw_hud()
        self._draw_message()
        if self.paused:
            Color(0, 0, 0, 0.55)
            Rectangle(pos=(0, 0), size=(W, H))
            self._text(W // 2, H // 2, "已暂停", 64, C_WHITE)
            self._text(W // 2, H // 2 + 60, "点屏幕继续", 26, C_WHITE)
        if self.world.state == "won":
            self._result("胜利！", (0.35, 0.78, 0.35, 1))
        elif self.world.state == "lost":
            self._result("游戏结束", (0.86, 0.27, 0.27, 1))

    def _result(self, title, color):
        Color(0, 0, 0, 0.6)
        Rectangle(pos=(0, 0), size=(W, H))
        self._text(W // 2, H // 2 - 40, title, 80, color)
        self._text(W // 2, H // 2 + 30, "点击屏幕重新开始", 26, C_WHITE)

    def _draw_plant(self, p):
        k = p.kind
        x, y = p.x, p.y
        if k == "sunflower":
            self._stem(x, y)
            self._petals(x, y - 22, (1.0, 0.78, 0.16, 1), 16, 11, 12)
            Color(0.47, 0.31, 0.12)
            Ellipse(pos=(x - 14, y - 36), size=(28, 28))
            self._eyes(x, y - 22, 5)
        elif k == "peashooter":
            self._stem(x, y)
            Color(0.31, 0.78, 0.35)
            Ellipse(pos=(x - 20, y - 48), size=(40, 40))
            Color(0.24, 0.63, 0.27)
            Rectangle(pos=(x + 18, y - 32), size=(24, 14))
            self._eyes(x + 12, y - 22, 5)
        elif k == "wallnut":
            Color(0.71, 0.47, 0.27)
            Ellipse(pos=(x - 30, y - 64), size=(60, 64))
            Color(0.55, 0.35, 0.20)
            Ellipse(pos=(x - 30, y - 64), size=(60, 64), segments=24)
            self._eyes(x, y - 40, 6)
        elif k == "snowpea":
            self._stem(x, y)
            Color(0.59, 0.82, 0.96)
            Ellipse(pos=(x - 20, y - 48), size=(40, 40))
            Color(0.35, 0.59, 0.78)
            Rectangle(pos=(x + 18, y - 32), size=(24, 14))
            self._eyes(x + 12, y - 22, 5)
        elif k == "repeater":
            self._stem(x, y)
            Color(0.27, 0.66, 0.31)
            Ellipse(pos=(x - 20, y - 48), size=(40, 40))
            Color(0.24, 0.59, 0.27)
            Rectangle(pos=(x + 18, y - 36), size=(24, 12))
            Rectangle(pos=(x + 18, y - 22), size=(24, 12))
            self._eyes(x + 12, y - 22, 5)
        elif k == "cherrybomb":
            self._stem(x, y)
            Color(0.82, 0.20, 0.24)
            Ellipse(pos=(x - 24, y - 50), size=(34, 34))
            Ellipse(pos=(x - 6, y - 50), size=(34, 34))
            Color(0.94, 0.94, 0.71)
            Ellipse(pos=(x - 22, y - 34), size=(8, 8))
        elif k == "chomper":
            self._stem(x, y)
            Color(0.59, 0.27, 0.51)
            Ellipse(pos=(x - 28, y - 56), size=(56, 34))
            Color(0.71, 0.35, 0.63)
            Ellipse(pos=(x - 30, y - 50), size=(60, 26))
            Color(1.0, 0.94, 0.78)
            Triangle((x - 22, y - 28), (x - 14, y - 42), (x - 6, y - 28))
            Triangle((x + 2, y - 28), (x + 10, y - 42), (x + 18, y - 28))
            self._eyes(x - 8, y - 42, 4)
        elif k == "sunshooter":
            self._stem(x, y)
            self._petals(x, y - 22, (1.0, 0.75, 0.20, 1), 15, 10, 12)
            Color(0.35, 0.78, 0.37)
            Ellipse(pos=(x - 14, y - 36), size=(28, 28))
            Color(0.24, 0.63, 0.27)
            Rectangle(pos=(x + 14, y - 32), size=(24, 12))
            self._eyes(x + 6, y - 22, 4)
        elif k == "frostfire":
            self._stem(x, y)
            Color(0.59, 0.82, 0.96)
            Ellipse(pos=(x - 20, y - 48), size=(20, 40))
            Color(0.92, 0.43, 0.20)
            Ellipse(pos=(x, y - 48), size=(20, 40))
            Color(0.35, 0.59, 0.78)
            Rectangle(pos=(x - 12, y - 32), size=(16, 10))
            Color(0.92, 0.43, 0.20)
            Rectangle(pos=(x + 18, y - 32), size=(16, 10))
        elif k == "gatlingnut":
            Color(0.71, 0.47, 0.27)
            Ellipse(pos=(x - 30, y - 64), size=(60, 64))
            Color(0.27, 0.27, 0.31)
            Rectangle(pos=(x + 22, y - 50), size=(24, 7))
            Rectangle(pos=(x + 22, y - 38), size=(24, 7))
            Rectangle(pos=(x + 22, y - 26), size=(24, 7))
            self._eyes(x - 4, y - 40, 6)
        elif k == "bombsunflower":
            self._stem(x, y)
            self._petals(x, y - 22, (0.92, 0.27, 0.27, 1), 16, 11, 12)
            Color(0.71, 0.16, 0.16)
            Ellipse(pos=(x - 14, y - 36), size=(28, 28))
            Color(0.94, 0.86, 0.31)
            Ellipse(pos=(x + 4, y - 44), size=(8, 8))
            self._eyes(x, y - 22, 4)
        # 血条
        if p.hp < p.max_hp and k != "cherrybomb":
            self._bar(x - 22, y - 78, 44, p.hp / p.max_hp)

    def _stem(self, x, y):
        Color(0.24, 0.59, 0.27)
        Rectangle(pos=(x - 3, y - 18), size=(6, 26))

    def _petals(self, cx, cy, color, R, pr, n):
        Color(*color)
        for i in range(n):
            a = i * 2 * math.pi / n
            px = cx + math.cos(a) * R
            py = cy + math.sin(a) * R
            Ellipse(pos=(px - pr, py - pr), size=(pr * 2, pr * 2))

    def _eyes(self, x, y, r):
        Color(0.16, 0.12, 0.08)
        Ellipse(pos=(x - r - 2, y - r // 2), size=(r, r))
        Ellipse(pos=(x + 2, y - r // 2), size=(r, r))

    def _draw_zombie(self, z):
        x, y = z.x, z.y
        skin = (0.67, 0.78, 0.59, 1) if z.slow <= 0 else (0.55, 0.75, 0.82, 1)
        sway = math.sin(z.walk * 8) * 2
        Color(0.27, 0.27, 0.35)
        Rectangle(pos=(x + 8, y - 72 + sway), size=(10, 22))
        Rectangle(pos=(x + 24, y - 72 + sway), size=(10, 22))
        Color(0.43, 0.35, 0.51)
        Rectangle(pos=(x + 6, y - 96 + sway), size=(30, 28))
        Color(*skin)
        Rectangle(pos=(x + 32, y - 92 + sway), size=(20, 8))
        Rectangle(pos=(x + 4, y - 92 + sway), size=(10, 8))
        Ellipse(pos=(x + 8, y - 118 + sway), size=(26, 26))
        Color(0.12, 0.08, 0.08)
        Ellipse(pos=(x + 12, y - 108 + sway), size=(4, 4))
        Ellipse(pos=(x + 22, y - 108 + sway), size=(4, 4))
        Color(0.24, 0.08, 0.08)
        Rectangle(pos=(x + 14, y - 118 + sway), size=(9, 3))
        if z.kind == "cone":
            Color(0.94, 0.59, 0.24)
            Triangle((x + 8, y - 118 + sway),
                     (x + 34, y - 118 + sway),
                     (x + 21, y - 142 + sway))
        elif z.kind == "bucket":
            Color(0.59, 0.59, 0.63)
            Rectangle(pos=(x + 6, y - 140 + sway), size=(30, 22))
        elif z.kind == "flag":
            Color(0.31, 0.24, 0.12)
            Line(points=[x + 44, y - 80 + sway, x + 44, y - 140 + sway],
                 width=2)
            Color(0.86, 0.27, 0.27)
            Triangle((x + 44, y - 134 + sway),
                     (x + 64, y - 128 + sway),
                     (x + 44, y - 122 + sway))
        if z.burn > 0:
            Color(1.0, 0.55, 0.16)
            for i in range(3):
                fx = x + 12 + i * 12
                fy = y - 90 + sway + math.sin(z.walk * 12 + i) * 3
                Triangle((fx, fy - 8), (fx - 4, fy), (fx + 4, fy))
        # 血条
        if z.hp < z.max_hp:
            self._bar(x - 20, y - 150, 40, z.hp / z.max_hp)

    def _draw_pea(self, pea):
        if pea.delay > 0:
            return
        col = {"snow": (0.59, 0.82, 0.96, 1),
               "fire": (0.94, 0.47, 0.20, 1)}.get(pea.kind, (0.35, 0.78, 0.35, 1))
        Color(*col)
        Ellipse(pos=(pea.x - 8, pea.y - 8), size=(16, 16))

    def _draw_sun(self, s):
        if s.life < 2.0 and int(s.life * 8) % 2 == 0:
            return
        scale = 1.0 + 0.05 * math.sin(s.spin)
        Color(1.0, 0.90, 0.47)
        R = 18 * scale
        for i in range(12):
            a = i * math.pi / 6
            px = s.x + math.cos(a) * R
            py = s.y + math.sin(a) * R
            Ellipse(pos=(px - 3, py - 3), size=(6, 6))
        Color(1.0, 0.85, 0.31)
        Ellipse(pos=(s.x - 12, s.y - 12), size=(24, 24))
        Color(1.0, 0.98, 0.78)
        Ellipse(pos=(s.x - 8, s.y - 8), size=(16, 16))

    def _draw_explosion(self, ex):
        p = ex.t / ex.duration
        r = ex.radius * (0.4 + 0.7 * p)
        a = 0.86 * (1 - p)
        Color(1.0, 0.86, 0.31, a)
        Ellipse(pos=(ex.x - r, ex.y - r), size=(r * 2, r * 2))
        Color(1.0, 0.47, 0.16, a)
        r2 = r * 0.7
        Ellipse(pos=(ex.x - r2, ex.y - r2), size=(r2 * 2, r2 * 2))

    def _bar(self, x, y, w, ratio):
        Color(0, 0, 0, 1)
        Rectangle(pos=(x - 1, y - 1), size=(w + 2, 6))
        Color(0.35, 0.86, 0.35 if ratio > 0.4 else 0.0,
              0.9 if ratio > 0.4 else 0.0)
        col = (0.35, 0.86, 0.35, 1) if ratio > 0.4 else (0.9, 0.35, 0.24, 1)
        Color(*col)
        Rectangle(pos=(x, y), size=(int(w * ratio), 4))

    def _draw_hud(self):
        # 阳光计数
        Color(0.16, 0.12, 0.08)
        Rectangle(pos=(8, 6), size=(132, 78))
        Color(*C_SUN)
        Rectangle(pos=(12, 10), size=(124, 70))
        self._text(78, 30, str(self.world.sun), 38, (0.24, 0.16, 0.04))
        # 卡片
        for i, kind in enumerate(SEED_BAR):
            self._draw_card(i, kind)
        # 铲子
        sx, sy, sw, sh = shovel_rect()
        Color(0.78, 0.75, 0.55)
        Rectangle(pos=(sx, sy), size=(sw, sh))
        Color(0.35, 0.27, 0.16)
        Line(rectangle=(sx, sy, sw, sh), width=2)
        Color(0.47, 0.35, 0.24)
        Rectangle(pos=(sx + 24, sy + 16), size=(8, 40))
        Color(0.71, 0.71, 0.75)
        Triangle((sx + 14, sy + 60), (sx + 42, sy + 60),
                 (sx + 28, sy + 42))
        if self.world.shovel:
            Color(1.0, 0.94, 0.47)
            Line(rectangle=(sx, sy, sw, sh), width=3)
        # 进度
        px, py = W - 260, 30
        Color(0.16, 0.12, 0.08)
        Rectangle(pos=(px - 6, py - 6), size=(232, 22))
        Color(0.31, 0.24, 0.16)
        Rectangle(pos=(px, py), size=(220, 16))
        Color(0.35, 0.78, 0.35)
        Rectangle(pos=(px, py), size=(int(220 * self.world.progress), 16))
        self._text(px + 110, py + 18,
                   f"波次 {self.world.wave}/{WAVE_TOTAL}", 18, C_WHITE)

    def _draw_card(self, i, kind):
        d = PLANTS[kind]
        rx, ry, rw, rh = card_rect(i)
        Color(0.84, 0.78, 0.59)
        Rectangle(pos=(rx, ry), size=(rw, rh))
        Color(0.35, 0.27, 0.16)
        Line(rectangle=(rx, ry, rw, rh), width=2)
        # 简化图标：色块
        ic = {"sunflower": (1.0, 0.78, 0.16), "peashooter": (0.31, 0.78, 0.35),
              "wallnut": (0.71, 0.47, 0.27), "snowpea": (0.59, 0.82, 0.96),
              "repeater": (0.27, 0.66, 0.31), "cherrybomb": (0.82, 0.20, 0.24),
              "chomper": (0.59, 0.27, 0.51), "sunshooter": (1.0, 0.75, 0.20),
              "frostfire": (0.59, 0.82, 0.96), "gatlingnut": (0.71, 0.47, 0.27),
              "bombsunflower": (0.92, 0.27, 0.27)}[kind]
        Color(*ic)
        Ellipse(pos=(rx + 22, ry + 36), size=(34, 34))
        self._text(rx + rw // 2, ry + 6, str(d["cost"]), 16,
                   (0.24, 0.16, 0.04))
        self._text(rx + rw // 2, ry + 24, d["name"], 13, (0.20, 0.14, 0.08))
        cd = self.world.cooldowns.get(kind, 0)
        if cd > 0:
            h = rh * cd / d["cd"]
            Color(0.16, 0.16, 0.24, 0.6)
            Rectangle(pos=(rx, ry + rh - h), size=(rw, h))
        if self.world.sun < d["cost"]:
            Color(0.12, 0.12, 0.12, 0.43)
            Rectangle(pos=(rx, ry), size=(rw, rh))
        if self.world.selected == kind:
            Color(1.0, 0.94, 0.47)
            Line(rectangle=(rx, ry, rw, rh), width=3)

    def _draw_message(self):
        if self.world.message_t <= 0:
            return
        a = 1.0 if self.world.message_t > 100 else min(1, self.world.message_t)
        self._text(W // 2, 120, self.world.message, 26,
                   (1.0, 0.94, 0.78, a))

    def _draw_menu(self):
        Color(0.16, 0.35, 0.20)
        Rectangle(pos=(0, 0), size=(W, H))
        for y in range(0, 360, 2):
            c = (174 / 255 - y * 0.0008, 218 / 255 - y * 0.0012,
                 250 / 255 - y * 0.0016, 1)
            Color(*c)
            Rectangle(pos=(0, y), size=(W, 2))
        Color(0.35, 0.63, 0.27)
        Rectangle(pos=(0, 360), size=(W, H - 360))
        self._text(W // 2, 150, "植物大战僵尸", 64, (1.0, 0.94, 0.47))
        self._text(W // 2, 210, "· 杂交版 ·", 46, (1.0, 0.78, 0.31))
        for i, col in enumerate([(1.0, 0.78, 0.16), (0.31, 0.78, 0.35),
                                 (0.59, 0.82, 0.96), (0.71, 0.47, 0.27)]):
            Color(*col)
            Ellipse(pos=(W // 2 - 180 + i * 90, 280), size=(40, 40))
        for cy, label in [(430, "开始游戏"), (510, "玩法说明"),
                          (590, "退出")]:
            Color(0.31, 0.24, 0.16)
            Rectangle(pos=(W // 2 - 130, cy - 28), size=(260, 56))
            Color(0.78, 0.67, 0.43)
            Line(rectangle=(W // 2 - 130, cy - 28, 260, 56), width=3)
            self._text(W // 2, cy - 8, label, 26, C_WHITE)
        self._text(W // 2, 680, "经典玩法 + 杂交创新植物 · Kivy 手机版",
                   18, (0.86, 0.90, 0.78))

    def _draw_help(self):
        Color(0.12, 0.20, 0.12)
        Rectangle(pos=(0, 0), size=(W, H))
        self._text(W // 2, 90, "玩法说明", 56, (1.0, 0.94, 0.47))
        lines = [
            ("★ 基本规则（与经典款一致）", True),
            ("  收集阳光 → 选植物卡片 → 点草地种植", False),
            ("  消灭所有波次僵尸即胜利，僵尸到家则失败", False),
            ("  向日葵产阳光，豌豆射手攻击，坚果墙防御", False),
            ("", False),
            ("★ 杂交创新植物（本作特色）", True),
            ("  阳光射手：向日葵+豌豆，边产阳光边射击", False),
            ("  冰火双生：左冰减速，右火灼烧持续掉血", False),
            ("  机枪坚果：坚果血量+三连发，能抗能打", False),
            ("  炸弹葵：产阳光；被啃毁时自爆同归于尽", False),
            ("  大嘴花：一口吞噬近身僵尸，咀嚼30秒", False),
            ("", False),
            ("★ 操作", True),
            ("  触屏点卡片选植物，点草地种植", False),
            ("  点阳光收集，铲子可移除植物", False),
        ]
        y = 170
        for ln, head in lines:
            self._text(120, y, ln, 20 if head else 18,
                       (1.0, 0.86, 0.47) if head else (0.86, 0.90, 0.82))
            y += 30
        Color(0.31, 0.24, 0.16)
        Rectangle(pos=(W // 2 - 130, H - 88), size=(260, 56))
        Color(0.78, 0.67, 0.43)
        Line(rectangle=(W // 2 - 130, H - 88, 260, 56), width=3)
        self._text(W // 2, H - 68, "返回", 26, C_WHITE)

    # 文本缓存：用 Label texture
    _tex_cache = {}

    def _text(self, x, y, s, size, color):
        key = (s, size)
        if key not in self._tex_cache:
            kw = dict(text=s, font_size=size, markup=False,
                      size_hint=(None, None))
            if CJK_FONT:
                kw["font_name"] = CJK_FONT
            lbl = Label(**kw)
            lbl.color = (1, 1, 1, 1)
            lbl.texture_update()
            self._tex_cache[key] = lbl.texture
        tex = self._tex_cache[key]
        tw, th = tex.size
        # 颜色覆盖
        Color(*color)
        Rectangle(pos=(x - tw / 2, y), size=(tw, th), texture=tex)


class PvZApp(App):
    def build(self):
        from kivy.core.window import Window
        Window.clearcolor = (0.16, 0.35, 0.20, 1)
        self.view = GameView(size=Window.size)
        Window.bind(on_key_down=self.view.keyboard_on_key_down)
        return self.view

    def on_pause(self):
        return True


if __name__ == "__main__":
    # 桌面预览：固定逻辑分辨率 1280x720（横屏），自动缩放适配窗口
    from kivy.config import Config
    Config.set("graphics", "width", "1280")
    Config.set("graphics", "height", "720")
    Config.set("graphics", "resizable", "1")
    PvZApp().run()
