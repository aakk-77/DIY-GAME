# -*- coding: utf-8 -*-
"""UI：种子栏、阳光计数、波次进度、菜单、结算界面。"""
import pygame
from . import constants as C
from .plants import PLANT_DEFS, SEED_BAR
from . import assets as A


# 种子卡片布局
CARD_W, CARD_H = 78, 96
CARD_X0 = 150
CARD_Y = 2
CARD_GAP = 6


def card_rect(i):
    return pygame.Rect(CARD_X0 + i * (CARD_W + CARD_GAP), CARD_Y,
                       CARD_W, CARD_H)


def shovel_rect():
    return pygame.Rect(CARD_X0 + len(SEED_BAR) * (CARD_W + CARD_GAP) + 8,
                       CARD_Y + 10, 56, 76)


class UI:
    def __init__(self):
        self.font_l = C.get_font(46, True)
        self.font_m = C.get_font(26, True)
        self.font_s = C.get_font(18, True)
        self.font_xs = C.get_font(15)
        self.title_font = C.get_font(64, True)

    # ---------- HUD ----------
    def draw_hud(self, surf, world, mx, my):
        # 阳光计数器
        pygame.draw.rect(surf, (40, 30, 20), (8, 6, 132, 78), border_radius=10)
        pygame.draw.rect(surf, C.SUN_COLOR, (12, 10, 124, 70), border_radius=8)
        surf.blit(A.draw_sun(), (20, 22))
        txt = self.font_l.render(str(world.sun), True, (60, 40, 10))
        surf.blit(txt, (78, 22))
        # 种子卡片
        for i, kind in enumerate(SEED_BAR):
            self._draw_card(surf, i, kind, world, mx, my)
        # 铲子
        self._draw_shovel(surf, world, mx, my)
        # 波次进度条
        self._draw_progress(surf, world)

    def _draw_card(self, surf, i, kind, world, mx, my):
        d = PLANT_DEFS[kind]
        rect = card_rect(i)
        hover = rect.collidepoint(mx, my)
        # 卡片底
        col = (235, 220, 170) if hover else (215, 200, 150)
        pygame.draw.rect(surf, col, rect, border_radius=6)
        pygame.draw.rect(surf, (90, 70, 40), rect, 2, border_radius=6)
        # 图标
        icon = A.get_plant_icon(kind)
        surf.blit(icon, (rect.x + 12, rect.y + 4))
        # 价格
        cost_txt = self.font_s.render(str(d["cost"]), True, (60, 40, 10))
        surf.blit(cost_txt, (rect.x + 6, rect.bottom - 22))
        # 小阳光图标
        pygame.draw.circle(surf, C.SUN_COLOR, (rect.x + 64, rect.bottom - 14),
                           7)
        # 选中高亮
        if world.selected == kind:
            pygame.draw.rect(surf, (255, 240, 120), rect, 3, border_radius=6)
        # 冷却遮罩
        cd = world.cooldowns.get(kind, 0)
        if cd > 0:
            ratio = cd / d["cd"]
            h = int(CARD_H * ratio)
            mask = pygame.Surface((CARD_W, h), pygame.SRCALPHA)
            mask.fill((40, 40, 60, 150))
            surf.blit(mask, (rect.x, rect.y))
        # 阳光不足置灰
        if world.sun < d["cost"]:
            gray = pygame.Surface((CARD_W, CARD_H), pygame.SRCALPHA)
            gray.fill((30, 30, 30, 110))
            surf.blit(gray, rect)
        # 名称
        name = self.font_xs.render(d["name"], True, (50, 35, 20))
        surf.blit(name, (rect.x + 4, rect.y + 60))

    def _draw_shovel(self, surf, world, mx, my):
        rect = shovel_rect()
        col = (230, 220, 170) if rect.collidepoint(mx, my) else (200, 190, 140)
        pygame.draw.rect(surf, col, rect, border_radius=6)
        pygame.draw.rect(surf, (90, 70, 40), rect, 2, border_radius=6)
        # 铲子图形
        pygame.draw.rect(surf, (120, 90, 60), (rect.x + 24, rect.y + 16, 8, 40))
        pygame.draw.polygon(surf, (180, 180, 190),
                            [(rect.x + 14, rect.y + 12),
                             (rect.x + 42, rect.y + 12),
                             (rect.x + 36, rect.y + 26),
                             (rect.x + 20, rect.y + 26)])
        pygame.draw.polygon(surf, (110, 110, 120),
                            [(rect.x + 14, rect.y + 12),
                             (rect.x + 42, rect.y + 12),
                             (rect.x + 36, rect.y + 26),
                             (rect.x + 20, rect.y + 26)], 2)
        if world.shovel:
            pygame.draw.rect(surf, (255, 240, 120), rect, 3, border_radius=6)

    def _draw_progress(self, surf, world):
        x = C.SCREEN_W - 260
        y = 30
        pygame.draw.rect(surf, (40, 30, 20), (x - 6, y - 6, 232, 22),
                         border_radius=6)
        pygame.draw.rect(surf, (80, 60, 40), (x, y, 220, 16), border_radius=4)
        w = int(220 * world.progress)
        pygame.draw.rect(surf, (90, 200, 90), (x, y, w, 16), border_radius=4)
        # 旗子标记
        for i in range(C.WAVE_TOTAL):
            fx = x + int(220 * (i + 1) / C.WAVE_TOTAL)
            col = (240, 60, 60) if (i + 1) <= world.wave else (240, 240, 240)
            pygame.draw.line(surf, (60, 40, 20), (fx, y - 2), (fx, y + 18), 1)
            pygame.draw.polygon(surf, col,
                                [(fx, y - 2), (fx + 10, y + 2), (fx, y + 6)])
        lbl = self.font_s.render(
            f"波次 {world.wave}/{C.WAVE_TOTAL}", True, C.WHITE)
        surf.blit(lbl, (x, y + 18))

    def draw_message(self, surf, world):
        if world.message_t <= 0:
            return
        if world.message_t > 100:
            alpha = 255
        else:
            alpha = int(255 * min(1, world.message_t))
        txt = self.font_m.render(world.message, True, (255, 240, 200))
        txt.set_alpha(alpha)
        bg = pygame.Surface((txt.get_width() + 30, txt.get_height() + 16),
                            pygame.SRCALPHA)
        bg.fill((0, 0, 0, int(alpha * 0.5)))
        r = bg.get_rect(center=(C.SCREEN_W // 2, 120))
        surf.blit(bg, r)
        surf.blit(txt, txt.get_rect(center=r.center))

    def draw_overlay(self, surf, world):
        if world.state == "won":
            self._result_screen(surf, "胜利！", (90, 200, 90), world)
        elif world.state == "lost":
            self._result_screen(surf, "游戏结束", (220, 70, 70), world)

    def _result_screen(self, surf, title, color, world):
        ov = pygame.Surface((C.SCREEN_W, C.SCREEN_H), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 150))
        surf.blit(ov, (0, 0))
        t = self.title_font.render(title, True, color)
        surf.blit(t, t.get_rect(center=(C.SCREEN_W // 2, C.SCREEN_H // 2 - 40)))
        sub = self.font_m.render("按 R 重新开始 · 按 ESC 返回主菜单",
                                 True, C.WHITE)
        surf.blit(sub, sub.get_rect(center=(C.SCREEN_W // 2,
                                            C.SCREEN_H // 2 + 30)))

    # ---------- 菜单 ----------
    def draw_menu(self, surf, mx, my):
        surf.fill((40, 90, 50))
        # 渐变天
        for y in range(0, 360):
            c = (174 - int(y * 0.2), 218 - int(y * 0.3), 250 - int(y * 0.4))
            pygame.draw.line(surf, c, (0, y), (C.SCREEN_W, y))
        # 草地
        pygame.draw.rect(surf, (90, 160, 70), (0, 360, C.SCREEN_W,
                                               C.SCREEN_H - 360))
        # 标题
        t1 = self.title_font.render("植物大战僵尸", True, (255, 240, 120))
        t2 = self.font_l.render("· 杂交版 ·", True, (255, 200, 80))
        surf.blit(t1, t1.get_rect(center=(C.SCREEN_W // 2, 150)))
        surf.blit(t2, t2.get_rect(center=(C.SCREEN_W // 2, 210)))
        # 装饰植物
        for i, k in enumerate(["sunflower", "peashooter", "frostfire",
                               "gatlingnut"]):
            icon = A.get_plant_icon(k)
            surf.blit(icon, (C.SCREEN_W // 2 - 180 + i * 90, 280))
        # 按钮
        self._button(surf, "开始游戏", C.SCREEN_W // 2, 430, mx, my, "play")
        self._button(surf, "玩法说明", C.SCREEN_W // 2, 510, mx, my, "help")
        self._button(surf, "退出", C.SCREEN_W // 2, 590, mx, my, "quit")
        foot = self.font_s.render(
            "经典玩法 + 杂交创新植物 · Python 实现", True, (220, 230, 200))
        surf.blit(foot, foot.get_rect(center=(C.SCREEN_W // 2, 680)))

    def _button(self, surf, label, cx, cy, mx, my, key):
        w, h = 260, 56
        rect = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
        hover = rect.collidepoint(mx, my)
        col = (110, 80, 50) if hover else (80, 60, 40)
        pygame.draw.rect(surf, col, rect, border_radius=12)
        pygame.draw.rect(surf, (200, 170, 110), rect, 3, border_radius=12)
        t = self.font_m.render(label, True, C.WHITE)
        surf.blit(t, t.get_rect(center=rect.center))
        return rect

    def draw_help(self, surf, mx, my):
        surf.fill((30, 50, 30))
        t = self.title_font.render("玩法说明", True, (255, 240, 120))
        surf.blit(t, t.get_rect(center=(C.SCREEN_W // 2, 90)))
        lines = [
            "★ 基本规则（与经典款一致）",
            "  · 收集阳光 → 选择植物卡片 → 点击草地种植",
            "  · 阻挡并消灭所有波次的僵尸即胜利，僵尸到家则失败",
            "  · 向日葵产阳光，豌豆射手攻击，坚果墙防御，樱桃炸弹范围爆破",
            "",
            "★ 杂交创新植物（本作特色）",
            "  · 阳光射手：向日葵+豌豆，边产阳光边射击，性价比之王",
            "  · 冰火双生：左管冰冻减速，右管火焰灼烧持续掉血",
            "  · 机枪坚果：坚果血量 + 三连发，能抗能打的前排堡垒",
            "  · 炸弹葵：产阳光；被僵尸啃毁时自爆，同归于尽",
            "  · 大嘴花：一口吞噬近身僵尸，但咀嚼 30 秒",
            "",
            "★ 操作",
            "  · 鼠标点击卡片选植物，点击空地种植；铲子可移除植物",
            "  · 点击天上的阳光收集；R 重开 · ESC 暂停/返回",
        ]
        y = 170
        for ln in lines:
            f = self.font_m if ln.startswith("★") else self.font_s
            col = (255, 220, 120) if ln.startswith("★") else (220, 230, 210)
            t = f.render(ln, True, col)
            surf.blit(t, (120, y))
            y += 30
        self._button(surf, "返回", C.SCREEN_W // 2, C.SCREEN_H - 60,
                     mx, my, "back")

    def menu_button_hit(self, mx, my):
        for cy, key in [(430, "play"), (510, "help"), (590, "quit")]:
            rect = pygame.Rect(C.SCREEN_W // 2 - 130, cy - 28, 260, 56)
            if rect.collidepoint(mx, my):
                return key
        return None

    def help_button_hit(self, mx, my):
        rect = pygame.Rect(C.SCREEN_W // 2 - 130, C.SCREEN_H - 88, 260, 56)
        return "back" if rect.collidepoint(mx, my) else None
