# -*- coding: utf-8 -*-
"""僵尸系统：基础、路障、铁桶、旗手"""
import math
import pygame
from . import assets as A
from . import constants as C


ZOMBIE_DEFS = {
    "basic":  dict(hp=200,  speed=1.0,  name="普通僵尸"),
    "cone":   dict(hp=560,  speed=1.0,  name="路障僵尸"),
    "bucket": dict(hp=1300, speed=0.95, name="铁桶僵尸"),
    "flag":   dict(hp=200,  speed=1.25, name="旗手僵尸"),
}

_DRAWERS = {
    "basic": A.draw_zombie, "cone": A.draw_cone_zombie,
    "bucket": A.draw_bucket_zombie, "flag": A.draw_flag_zombie,
}


class Zombie:
    def __init__(self, kind, row):
        self.kind = kind
        self.row = row
        d = ZOMBIE_DEFS[kind]
        self.hp = d["hp"]
        self.max_hp = d["hp"]
        self.base_speed = d["speed"] * C.ZOMBIE_BASE_SPEED
        self.name = d["name"]
        # 从屏幕右侧外进入
        self.x = C.SCREEN_W + 30
        self.y = C.LAWN_Y + row * C.CELL_H + C.CELL_H - 6
        self.img = _DRAWERS[kind]()
        self.w, self.h = self.img.get_size()
        self.eating = None        # 正在啃的植物
        self.eat_cd = 0.0
        self.slow = 0.0           # 减速剩余时间
        self.burn = 0.0           # 灼烧剩余时间
        self.burn_dps = 0.0
        self.dead = False
        self.walk = 0.0
        self.reached_house = False

    @property
    def speed(self):
        s = self.base_speed
        if self.slow > 0:
            s *= 0.5
        return s

    def update(self, dt, world):
        self.walk += dt
        # 状态效果
        if self.slow > 0:
            self.slow -= dt
        if self.burn > 0:
            self.burn -= dt
            self.hp -= self.burn_dps * dt
            if self.hp <= 0:
                self.dead = True
                return
        # 啃食判定
        if self.eating is not None and not self.eating.dead:
            self.eat_cd -= dt
            if self.eat_cd <= 0:
                self.eating.hp -= 40
                self.eat_cd = 0.5
        else:
            self.eating = world.plant_in_front(self.x, self.row)
            if self.eating is not None:
                self.eat_cd = 0.5
            else:
                self.x -= self.speed * dt
        # 到家判定
        if self.x < C.LAWN_X - 10:
            self.reached_house = True
            self.dead = True
        if self.hp <= 0:
            self.dead = True

    def hit(self, dmg, kind="pea"):
        """被子弹击中"""
        if kind == "snow":
            self.slow = 4.0
        elif kind == "fire":
            self.burn = 3.0
            self.burn_dps = 50.0
        self.hp -= dmg

    def draw(self, surf):
        # 走路摆动
        sway = int(math.sin(self.walk * 8) * 2)
        rect = self.img.get_rect(midbottom=(int(self.x), self.y + sway))
        # 减速泛蓝
        if self.slow > 0:
            tint = pygame.Surface(self.img.get_size(), pygame.SRCALPHA)
            tint.fill((120, 180, 255, 70))
            self.img.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
            surf.blit(self.img, rect)
            tint.fill((0, 0, 0, 70))
            self.img.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
        elif self.burn > 0:
            surf.blit(self.img, rect)
            # 火苗
            for i in range(3):
                fx = rect.x + 12 + i * 14
                fy = rect.y + 20 + int(math.sin(self.walk * 12 + i) * 3)
                pygame.draw.polygon(surf, (255, 180 - i * 30, 40),
                                    [(fx, fy + 14), (fx - 5, fy),
                                     (fx + 5, fy)])
        else:
            surf.blit(self.img, rect)
        # 血条
        if self.hp < self.max_hp:
            w = 40
            x = int(self.x) - w // 2
            y = rect.y - 6
            pygame.draw.rect(surf, (0, 0, 0), (x - 1, y - 1, w + 2, 5))
            ratio = max(0, self.hp / self.max_hp)
            col = (90, 220, 90) if ratio > 0.5 else (230, 90, 60)
            pygame.draw.rect(surf, col, (x, y, int(w * ratio), 3))
