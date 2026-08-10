# -*- coding: utf-8 -*-
"""植物系统：经典植物 + 杂交创新植物。
所有植物共用 Plant 基类，行为由 kind 决定。"""
import pygame
from . import assets as A
from . import constants as C


# 植物配置表：价格、冷却(秒)、血量、描述
PLANT_DEFS = {
    # ---- 经典 ----
    "sunflower": dict(cost=50, cd=7.5, hp=100, name="向日葵",
                      desc="产生阳光"),
    "peashooter": dict(cost=100, cd=7.5, hp=100, name="豌豆射手",
                       desc="射出豌豆"),
    "wallnut": dict(cost=50, cd=20.0, hp=400, name="坚果墙",
                    desc="高血量阻挡"),
    "snowpea": dict(cost=175, cd=7.5, hp=100, name="寒冰射手",
                    desc="减速豌豆"),
    "repeater": dict(cost=200, cd=7.5, hp=100, name="双发射手",
                     desc="连发两颗"),
    "cherrybomb": dict(cost=150, cd=30.0, hp=9999, name="樱桃炸弹",
                       desc="范围爆炸"),
    "chomper": dict(cost=150, cd=7.5, hp=100, name="大嘴花",
                    desc="吞噬僵尸后咀嚼"),
    # ---- 杂交创新 ----
    "sunshooter": dict(cost=175, cd=12.0, hp=120, name="阳光射手",
                       desc="向日葵+豌豆：产阳光且射击"),
    "frostfire": dict(cost=325, cd=14.0, hp=120, name="冰火双生",
                      desc="左冰右火：减速+灼烧伤害"),
    "gatlingnut": dict(cost=250, cd=16.0, hp=600, name="机枪坚果",
                       desc="坚果+三连发：抗打又能输出"),
    "bombsunflower": dict(cost=125, cd=20.0, hp=120, name="炸弹葵",
                          desc="产阳光；被吃掉时自爆"),
}

# 选择栏顺序（同时显示 8 种）
SEED_BAR = ["sunflower", "peashooter", "wallnut", "snowpea",
            "repeater", "sunshooter", "frostfire", "gatlingnut",
            "cherrybomb", "bombsunflower", "chomper"]


_DRAWERS = {
    "sunflower": A.draw_sunflower, "peashooter": A.draw_peashooter,
    "wallnut": A.draw_wallnut, "snowpea": A.draw_snowpea,
    "repeater": A.draw_repeater, "cherrybomb": A.draw_cherrybomb,
    "chomper": A.draw_chomper,
    "sunshooter": A.draw_sunshooter, "frostfire": A.draw_frostfire,
    "gatlingnut": A.draw_gatlingnut, "bombsunflower": A.draw_bombsunflower,
}


class Plant:
    def __init__(self, kind, col, row):
        self.kind = kind
        self.col = col
        self.row = row
        d = PLANT_DEFS[kind]
        self.hp = d["hp"]
        self.max_hp = d["hp"]
        self.cost = d["cost"]
        self.name = d["name"]
        self.x = C.LAWN_X + col * C.CELL_W + C.CELL_W // 2
        self.y = C.LAWN_Y + row * C.CELL_H + C.CELL_H // 2 + 8
        self.img = _DRAWERS[kind]()
        self.w, self.h = self.img.get_size()
        # 计时器
        self.shoot_cd = 0.0
        self.sun_cd = 6.0 if kind in ("sunflower", "sunshooter",
                                      "bombsunflower") else 0
        self.chew_time = 0.0   # 大嘴花咀嚼
        self.dead = False
        # 动画
        self.bob = (col * 7 + row * 13) % 60  # 错开摆动相位
        # 樱桃/炸弹葵自爆
        self.fuse = 0.0

    # ---- 行为类型判断 ----
    @property
    def is_shooter(self):
        return self.kind in ("peashooter", "snowpea", "repeater",
                             "sunshooter", "frostfire", "gatlingnut")

    @property
    def makes_sun(self):
        return self.kind in ("sunflower", "sunshooter", "bombsunflower")

    @property
    def is_bomb(self):
        return self.kind == "cherrybomb"

    @property
    def is_chomper(self):
        return self.kind == "chomper"

    # ---- 更新 ----
    def update(self, dt, world):
        self.bob += dt * 60
        if self.hp <= 0:
            self.dead = True
            if self.kind == "bombsunflower":
                world.explode(self.x, self.y, 120, 1800)
            return
        if self.is_bomb:
            self.fuse += dt
            if self.fuse >= 1.0:
                world.explode(self.x, self.y, 130, 1800)
                self.dead = True
            return
        if self.is_chomper:
            self._update_chomper(dt, world)
            return
        if self.is_shooter:
            self.shoot_cd -= dt
            # 该行有僵尸才射击
            if self.shoot_cd <= 0 and world.row_has_zombie(self.row, self.x):
                self._shoot(world)
                self.shoot_cd = self._shoot_interval()
        if self.makes_sun:
            self.sun_cd -= dt
            if self.sun_cd <= 0:
                world.spawn_plant_sun(self.x, self.y - 30)
                self.sun_cd = 14.0 if self.kind == "sunflower" else 18.0

    def _shoot_interval(self):
        return {"peashooter": 1.4, "snowpea": 1.4, "repeater": 1.4,
                "sunshooter": 1.5, "frostfire": 1.6,
                "gatlingnut": 1.6}[self.kind]

    def _shoot(self, world):
        if self.kind == "peashooter":
            world.spawn_pea(self.x + 18, self.y - 4, self.row, "pea")
        elif self.kind == "snowpea":
            world.spawn_pea(self.x + 18, self.y - 4, self.row, "snow")
        elif self.kind == "repeater":
            world.spawn_pea(self.x + 18, self.y - 4, self.row, "pea")
            world.spawn_pea(self.x + 18, self.y - 4, self.row, "pea", 0.18)
        elif self.kind == "sunshooter":
            world.spawn_pea(self.x + 18, self.y - 4, self.row, "pea")
        elif self.kind == "frostfire":
            world.spawn_pea(self.x + 14, self.y - 10, self.row, "snow")
            world.spawn_pea(self.x + 14, self.y + 2, self.row, "fire")
        elif self.kind == "gatlingnut":
            world.spawn_pea(self.x + 18, self.y - 14, self.row, "pea")
            world.spawn_pea(self.x + 18, self.y - 4, self.row, "pea", 0.10)
            world.spawn_pea(self.x + 18, self.y + 6, self.row, "pea", 0.20)

    def _update_chomper(self, dt, world):
        if self.chew_time > 0:
            self.chew_time -= dt
            return
        # 寻找紧邻的前方僵尸吞噬
        z = world.zombie_near(self.x, self.row, 70)
        if z:
            z.hp = 0
            z.dead = True
            self.chew_time = 30.0

    def draw(self, surf):
        # 轻微上下浮动
        dy = int(math_sin(self.bob) * 2) if False else 0
        off = -2 if (int(self.bob) % 90 < 8) else 0  # 偶尔弹一下
        rect = self.img.get_rect(midbottom=(self.x, self.y + off + dy))
        surf.blit(self.img, rect)
        # 血量条（受伤时）
        if self.hp < self.max_hp and self.kind != "cherrybomb":
            w = 44
            x = self.x - w // 2
            y = self.y - self.h - 8
            pygame.draw.rect(surf, (0, 0, 0), (x - 1, y - 1, w + 2, 6))
            ratio = max(0, self.hp / self.max_hp)
            col = (90, 220, 90) if ratio > 0.4 else (230, 90, 60)
            pygame.draw.rect(surf, col, (x, y, int(w * ratio), 4))


def math_sin(v):
    import math
    return math.sin(v / 9.0)
