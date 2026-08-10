# -*- coding: utf-8 -*-
"""植物大战僵尸·杂交版 —— Kivy 手机版（自包含，不依赖 pygame）。
逻辑与桌面版一致：阳光经济 / 种植 / 多波次 / 经典+杂交植物。
可用 Buildozer 打包为 Android APK。"""
import math
import random
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import (Color, Rectangle, Ellipse, Line, Triangle,
                           PushMatrix, PopMatrix, Rotate, Translate)
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.utils import get_color_from_hex as hx

# ---------- 配置 ----------
W, H = 1280, 720          # 逻辑分辨率（横屏）
COLS, ROWS = 9, 5
LAWN_X, LAWN_Y = 220, 110
CELL_W, CELL_H = 100, 110
FPS = 60

C_SKY = hx("#aedaf6")
C_GRASS_A = hx("#78b24e")
C_GRASS_B = hx("#6ea846")
C_PATH = hx("#bc9e6e")
C_HUD = hx("#3c2c1c")
C_HUD2 = hx("#584028")
C_SUN = hx("#ffde46")
C_WHITE = (1, 1, 1, 1)
C_BLACK = (0.11, 0.11, 0.13, 1)

STARTING_SUN = 150
SUN_DROP_INTERVAL = 8.0
WAVE_TOTAL = 10


# ---------- 植物配置 ----------
PLANTS = {
    "sunflower":   dict(cost=50,  cd=7.5,  hp=100,  name="向日葵"),
    "peashooter":  dict(cost=100, cd=7.5,  hp=100,  name="豌豆射手"),
    "wallnut":     dict(cost=50,  cd=20.0, hp=400,  name="坚果墙"),
    "snowpea":     dict(cost=175, cd=7.5,  hp=100,  name="寒冰射手"),
    "repeater":    dict(cost=200, cd=7.5,  hp=100,  name="双发射手"),
    "cherrybomb":  dict(cost=150, cd=30.0, hp=9999, name="樱桃炸弹"),
    "chomper":     dict(cost=150, cd=7.5,  hp=100,  name="大嘴花"),
    "sunshooter":  dict(cost=175, cd=12.0, hp=120,  name="阳光射手"),
    "frostfire":   dict(cost=325, cd=14.0, hp=120,  name="冰火双生"),
    "gatlingnut":  dict(cost=250, cd=16.0, hp=600,  name="机枪坚果"),
    "bombsunflower": dict(cost=125, cd=20.0, hp=120, name="炸弹葵"),
}
SEED_BAR = ["sunflower", "peashooter", "wallnut", "snowpea", "repeater",
            "sunshooter", "frostfire", "gatlingnut",
            "cherrybomb", "bombsunflower", "chomper"]

SHOOTERS = {"peashooter", "snowpea", "repeater", "sunshooter",
            "frostfire", "gatlingnut"}
SUNMAKERS = {"sunflower", "sunshooter", "bombsunflower"}


class Plant:
    def __init__(self, kind, col, row):
        self.kind = kind
        self.col, self.row = col, row
        d = PLANTS[kind]
        self.hp = self.max_hp = d["hp"]
        self.cost = d["cost"]
        self.name = d["name"]
        self.x = LAWN_X + col * CELL_W + CELL_W // 2
        self.y = LAWN_Y + row * CELL_H + CELL_H // 2 + 8
        self.shoot_cd = 0.0
        self.sun_cd = 6.0 if kind in SUNMAKERS else 0
        self.chew = 0.0
        self.fuse = 0.0
        self.dead = False
        self.bob = (col * 7 + row * 13) % 60

    @property
    def is_shooter(self):
        return self.kind in SHOOTERS

    @property
    def makes_sun(self):
        return self.kind in SUNMAKERS

    def update(self, dt, world):
        self.bob += dt * 60
        if self.hp <= 0:
            self.dead = True
            if self.kind == "bombsunflower":
                world.explode(self.x, self.y, 120, 1800)
            return
        if self.kind == "cherrybomb":
            self.fuse += dt
            if self.fuse >= 1.0:
                world.explode(self.x, self.y, 130, 1800)
                self.dead = True
            return
        if self.kind == "chomper":
            if self.chew > 0:
                self.chew -= dt
                return
            z = world.zombie_near(self.x, self.row, 70)
            if z:
                z.hp = 0
                z.dead = True
                self.chew = 30.0
            return
        if self.is_shooter:
            self.shoot_cd -= dt
            if self.shoot_cd <= 0 and world.row_has_zombie(self.row, self.x):
                self._shoot(world)
                self.shoot_cd = {"peashooter": 1.4, "snowpea": 1.4,
                                 "repeater": 1.4, "sunshooter": 1.5,
                                 "frostfire": 1.6, "gatlingnut": 1.6}[self.kind]
        if self.makes_sun:
            self.sun_cd -= dt
            if self.sun_cd <= 0:
                world.spawn_plant_sun(self.x, self.y - 30)
                self.sun_cd = 14.0 if self.kind == "sunflower" else 18.0

    def _shoot(self, world):
        k = self.kind
        if k == "peashooter":
            world.spawn_pea(self.x + 18, self.y - 4, self.row, "pea")
        elif k == "snowpea":
            world.spawn_pea(self.x + 18, self.y - 4, self.row, "snow")
        elif k == "repeater":
            world.spawn_pea(self.x + 18, self.y - 4, self.row, "pea")
            world.spawn_pea(self.x + 18, self.y - 4, self.row, "pea", 0.18)
        elif k == "sunshooter":
            world.spawn_pea(self.x + 18, self.y - 4, self.row, "pea")
        elif k == "frostfire":
            world.spawn_pea(self.x + 14, self.y - 10, self.row, "snow")
            world.spawn_pea(self.x + 14, self.y + 2, self.row, "fire")
        elif k == "gatlingnut":
            world.spawn_pea(self.x + 18, self.y - 14, self.row, "pea")
            world.spawn_pea(self.x + 18, self.y - 4, self.row, "pea", 0.10)
            world.spawn_pea(self.x + 18, self.y + 6, self.row, "pea", 0.20)


class Zombie:
    def __init__(self, kind, row):
        self.kind = kind
        self.row = row
        defs = {"basic": (200, 1.0), "cone": (560, 1.0),
                "bucket": (1300, 0.95), "flag": (200, 1.25)}
        self.hp = self.max_hp = defs[kind][0]
        self.base_speed = defs[kind][1] * 22
        self.x = W + 30
        self.y = LAWN_Y + row * CELL_H + CELL_H - 6
        self.eating = None
        self.eat_cd = 0.0
        self.slow = 0.0
        self.burn = 0.0
        self.burn_dps = 0.0
        self.dead = False
        self.walk = 0.0
        self.reached = False

    @property
    def speed(self):
        return self.base_speed * (0.5 if self.slow > 0 else 1.0)

    def update(self, dt, world):
        self.walk += dt
        if self.slow > 0:
            self.slow -= dt
        if self.burn > 0:
            self.burn -= dt
            self.hp -= self.burn_dps * dt
            if self.hp <= 0:
                self.dead = True
                return
        if self.eating and not self.eating.dead:
            self.eat_cd -= dt
            if self.eat_cd <= 0:
                self.eating.hp -= 40
                self.eat_cd = 0.5
        else:
            self.eating = world.plant_in_front(self.x, self.row)
            if self.eating:
                self.eat_cd = 0.5
            else:
                self.x -= self.speed * dt
        if self.x < LAWN_X - 10:
            self.reached = True
            self.dead = True
        if self.hp <= 0:
            self.dead = True

    def hit(self, dmg, kind="pea"):
        if kind == "snow":
            self.slow = 4.0
        elif kind == "fire":
            self.burn = 3.0
            self.burn_dps = 50.0
        self.hp -= dmg


class Pea:
    def __init__(self, x, y, row, kind="pea", delay=0.0):
        self.x, self.y, self.row, self.kind = x, y, row, kind
        self.speed = 380
        self.delay = delay
        self.dead = False
        self.dmg = {"snow": 20, "fire": 30}.get(kind, 20)

    def update(self, dt, world):
        if self.delay > 0:
            self.delay -= dt
            return
        self.x += self.speed * dt
        for z in world.zombies:
            if z.row != self.row or z.dead:
                continue
            if abs(z.x - self.x) < 26 and self.x < z.x + 10:
                z.hit(self.dmg, self.kind)
                self.dead = True
                return
        if self.x > W + 20:
            self.dead = True


class Sun:
    def __init__(self, x, y, value=25, target_y=None, from_sky=True):
        self.x, self.y = x, y
        self.target_y = target_y if target_y is not None else y
        self.value = value
        self.life = 9.0
        self.dead = False
        self.collected = False
        self.ct = 0.0
        self.spin = 0.0
        self.falling = from_sky and target_y is not None and target_y > y

    def update(self, dt, world):
        self.spin += dt * 3
        if self.collected:
            self.ct += dt
            tx, ty = 70, 45
            self.x += (tx - self.x) * min(1, self.ct * 6)
            self.y += (ty - self.y) * min(1, self.ct * 6)
            if self.ct > 0.35:
                world.sun += self.value
                self.dead = True
            return
        if self.falling:
            self.y += 50 * dt
            if self.y >= self.target_y:
                self.y = self.target_y
                self.falling = False
        self.life -= dt
        if self.life <= 0:
            self.dead = True

    def collect(self):
        self.collected = True

    def hit_test(self, mx, my):
        return abs(mx - self.x) < 36 and abs(my - self.y) < 36


class Explosion:
    def __init__(self, x, y, radius, dmg):
        self.x, self.y, self.radius, self.dmg = x, y, radius, dmg
        self.t = 0.0
        self.duration = 0.45
        self.done = False

    def update(self, dt, world):
        self.t += dt
        if self.t < 0.1:
            for z in world.zombies:
                if z.dead:
                    continue
                if math.hypot(z.x - self.x, (z.y - 40) - (self.y - 40)) \
                        < self.radius:
                    z.hit(self.dmg, "fire")
        if self.t >= self.duration:
            self.done = True


class World:
    def __init__(self):
        self.plants, self.zombies, self.peas = [], [], []
        self.suns, self.explosions = [], []
        self.sun = STARTING_SUN
        self.selected = None
        self.cooldowns = {k: 0.0 for k in SEED_BAR}
        self.wave = 0
        self.wave_timer = 3.0
        self.spawn_queue = []
        self.in_wave = False
        self.progress = 0.0
        self.killed = 0
        self.total = 0
        self.sky_sun_timer = SUN_DROP_INTERVAL
        self.state = "playing"
        self.message = ""
        self.message_t = 0.0
        self.shovel = False

    def cell_at(self, mx, my):
        if mx < LAWN_X or my < LAWN_Y:
            return None
        col = int((mx - LAWN_X) // CELL_W)
        row = int((my - LAWN_Y) // CELL_H)
        if 0 <= col < COLS and 0 <= row < ROWS:
            return col, row
        return None

    def plant_at(self, col, row):
        for p in self.plants:
            if p.col == col and p.row == row and not p.dead:
                return p
        return None

    def row_has_zombie(self, row, x):
        return any(z.row == row and not z.dead and z.x > x - 20
                   for z in self.zombies)

    def plant_in_front(self, x, row):
        for p in self.plants:
            if p.row == row and not p.dead and p.kind != "cherrybomb":
                if x - 20 < p.x < x + 40:
                    return p
        return None

    def zombie_near(self, x, row, dist):
        for z in self.zombies:
            if z.row == row and not z.dead and abs(z.x - x) < dist:
                return z
        return None

    def try_plant(self, col, row):
        if self.selected is None or self.plant_at(col, row):
            return False
        d = PLANTS[self.selected]
        if self.sun < d["cost"]:
            self.flash("阳光不足！")
            return False
        if self.cooldowns[self.selected] > 0:
            self.flash("冷却中…")
            return False
        self.sun -= d["cost"]
        self.plants.append(Plant(self.selected, col, row))
        self.cooldowns[self.selected] = d["cd"]
        self.selected = None
        return True

    def try_shovel(self, col, row):
        p = self.plant_at(col, row)
        if p:
            p.dead = True
        self.shovel = False

    def spawn_pea(self, x, y, row, kind, delay=0.0):
        self.peas.append(Pea(x, y, row, kind, delay))

    def spawn_plant_sun(self, x, y):
        self.suns.append(Sun(x, y, value=25, from_sky=False))

    def spawn_sky_sun(self):
        x = random.randint(LAWN_X + 40, LAWN_X + COLS * CELL_W - 40)
        ty = random.randint(LAWN_Y + 40, LAWN_Y + ROWS * CELL_H - 40)
        self.suns.append(Sun(x, -20, value=25, target_y=ty, from_sky=True))

    def explode(self, x, y, radius, dmg):
        self.explosions.append(Explosion(x, y, radius, dmg))

    def collect_sun_at(self, mx, my):
        for s in self.suns:
            if not s.dead and s.hit_test(mx, my):
                s.collect()
                return True
        return False

    def _start_wave(self):
        self.wave += 1
        self.in_wave = True
        self.flash("最终波！！！" if self.wave == WAVE_TOTAL
                   else f"第 {self.wave} 波 来袭！")
        n = 3 + self.wave * 2
        kinds = ["basic", "basic"]
        if self.wave >= 3:
            kinds.append("cone")
        if self.wave >= 5:
            kinds.append("cone")
        if self.wave >= 6:
            kinds.append("bucket")
        if self.wave == WAVE_TOTAL:
            kinds += ["flag", "bucket", "cone"]
        self.total += n
        for i in range(n):
            delay = i * random.uniform(1.4, 2.8)
            kind = kinds[i % len(kinds)]
            row = random.randint(0, ROWS - 1)
            self.spawn_queue.append([delay, kind, row])

    def _update_spawns(self, dt):
        if self.spawn_queue:
            self.spawn_queue[0][0] -= dt
            if self.spawn_queue[0][0] <= 0:
                _, kind, row = self.spawn_queue.pop(0)
                self.zombies.append(Zombie(kind, row))

    def flash(self, msg):
        self.message = msg
        self.message_t = 1.4

    def update(self, dt):
        if self.state != "playing":
            return
        for k in self.cooldowns:
            if self.cooldowns[k] > 0:
                self.cooldowns[k] = max(0, self.cooldowns[k] - dt)
        if self.message_t > 0:
            self.message_t -= dt
        self.sky_sun_timer -= dt
        if self.sky_sun_timer <= 0:
            self.spawn_sky_sun()
            self.sky_sun_timer = SUN_DROP_INTERVAL
        for p in self.plants:
            p.update(dt, self)
        for z in self.zombies:
            z.update(dt, self)
        for pea in self.peas:
            pea.update(dt, self)
        for s in self.suns:
            s.update(dt, self)
        for ex in self.explosions:
            ex.update(dt, self)
        self._update_spawns(dt)
        if not self.in_wave and not self.spawn_queue:
            self.wave_timer -= dt
            if self.wave_timer <= 0:
                self._start_wave()
        if self.in_wave and not self.spawn_queue and \
                not any(not z.dead for z in self.zombies):
            self.in_wave = False
            self.wave_timer = 6.0
            if self.wave >= WAVE_TOTAL:
                self.state = "won"
                self.message = "胜利！保卫了家园！"
                self.message_t = 999
        if self.total > 0:
            self.progress = min(1.0, self.killed / self.total)
        for z in self.zombies:
            if z.dead and z.hp <= 0 and not z.reached:
                self.killed += 1
        self.plants = [p for p in self.plants if not p.dead]
        self.zombies = [z for z in self.zombies if not z.dead]
        self.peas = [p for p in self.peas if not p.dead]
        self.suns = [s for s in self.suns if not s.dead]
        self.explosions = [e for e in self.explosions if not e.done]
        for z in self.zombies:
            if z.reached:
                self.state = "lost"
                self.message = "僵尸吃掉了你的脑子！"
                self.message_t = 999
                break
