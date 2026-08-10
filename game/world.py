# -*- coding: utf-8 -*-
"""世界：承载所有实体、波次推进、碰撞与胜负判定。"""
import random
import math
import pygame
from . import constants as C
from .plants import Plant, PLANT_DEFS, SEED_BAR
from .zombies import Zombie, ZOMBIE_DEFS
from .projectiles import Pea, Sun


class Explosion:
    def __init__(self, x, y, radius, dmg):
        self.x = x
        self.y = y
        self.radius = radius
        self.dmg = dmg
        self.t = 0.0
        self.duration = 0.45
        self.done = False

    def update(self, dt, world):
        self.t += dt
        if self.t < 0.1:    # 起爆瞬间造成伤害
            for z in world.zombies:
                if z.dead:
                    continue
                if math.hypot(z.x - self.x, (z.y - 40) - (self.y - 40)) \
                        < self.radius:
                    z.hit(self.dmg, "fire")
        if self.t >= self.duration:
            self.done = True

    def draw(self, surf):
        p = self.t / self.duration
        r = int(self.radius * (0.4 + 0.7 * p))
        alpha = int(220 * (1 - p))
        s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 220, 80, alpha), (r, r), r)
        pygame.draw.circle(s, (255, 120, 40, alpha), (r, r), int(r * 0.7))
        surf.blit(s, (self.x - r, self.y - r))


class World:
    def __init__(self):
        self.plants = []          # Plant[]
        self.zombies = []         # Zombie[]
        self.peas = []            # Pea[]
        self.suns = []            # Sun[]
        self.explosions = []      # Explosion[]
        self.sun = C.STARTING_SUN
        self.selected = None      # 当前选中卡片 kind
        # 冷却：kind -> 剩余秒
        self.cooldowns = {k: 0.0 for k in SEED_BAR}
        # 波次
        self.wave = 0
        self.wave_timer = 3.0     # 第一波前准备
        self.spawn_queue = []     # 待生成僵尸 [(delay, kind, row)]
        self.in_wave = False
        self.progress = 0.0       # 0~1 总进度
        self.zombies_killed = 0
        self.zombies_total = 0
        # 天降阳光
        self.sky_sun_timer = C.SUN_DROP_INTERVAL
        # 状态
        self.state = "playing"    # playing / won / lost
        self.message = ""
        self.message_t = 0.0
        self.shovel = False       # 铲子模式

    # ---------- 工具 ----------
    def cell_at(self, mx, my):
        if mx < C.LAWN_X or my < C.LAWN_Y:
            return None
        col = (mx - C.LAWN_X) // C.CELL_W
        row = (my - C.LAWN_Y) // C.CELL_H
        if 0 <= col < C.COLS and 0 <= row < C.ROWS:
            return int(col), int(row)
        return None

    def plant_at(self, col, row):
        for p in self.plants:
            if p.col == col and p.row == row and not p.dead:
                return p
        return None

    def row_has_zombie(self, row, x):
        for z in self.zombies:
            if z.row == row and not z.dead and z.x > x - 20:
                return True
        return False

    def plant_in_front(self, x, row):
        """返回僵尸正在啃的位置上的植物"""
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

    # ---------- 种植 ----------
    def try_plant(self, col, row):
        if self.selected is None:
            return False
        if self.plant_at(col, row):
            return False
        d = PLANT_DEFS[self.selected]
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

    # ---------- 生成 ----------
    def spawn_pea(self, x, y, row, kind, delay=0.0):
        self.peas.append(Pea(x, y, row, kind, delay))

    def spawn_plant_sun(self, x, y):
        self.suns.append(Sun(x, y, value=25, from_sky=False))

    def spawn_sky_sun(self):
        x = random.randint(C.LAWN_X + 40,
                           C.LAWN_X + C.COLS * C.CELL_W - 40)
        target_y = random.randint(C.LAWN_Y + 40,
                                  C.LAWN_Y + C.ROWS * C.CELL_H - 40)
        self.suns.append(Sun(x, -20, value=C.SUN_DROP_VALUE,
                             target_y=target_y, from_sky=True))

    def explode(self, x, y, radius, dmg):
        self.explosions.append(Explosion(x, y, radius, dmg))

    def add_sun(self, v):
        self.sun += v

    def collect_sun_at(self, mx, my):
        for s in self.suns:
            if not s.dead and s.hit_test(mx, my):
                s.collect()
                return True
        return False

    # ---------- 波次 ----------
    def _start_wave(self):
        self.wave += 1
        self.in_wave = True
        self.flash(f"第 {self.wave} 波 来袭！" if self.wave < C.WAVE_TOTAL
                   else "最终波！！！")
        n = 3 + self.wave * 2
        kinds = ["basic"]
        if self.wave >= 2:
            kinds += ["basic"]
        if self.wave >= 3:
            kinds.append("cone")
        if self.wave >= 5:
            kinds.append("cone")
        if self.wave >= 6:
            kinds.append("bucket")
        if self.wave == C.WAVE_TOTAL:
            kinds += ["flag", "bucket", "cone"]
        self.zombies_total += n
        # 错峰生成
        for i in range(n):
            delay = i * random.uniform(1.4, 2.8)
            kind = kinds[i % len(kinds)]
            row = random.randint(0, C.ROWS - 1)
            self.spawn_queue.append((delay, kind, row))

    def _update_spawns(self, dt):
        if self.spawn_queue:
            self.spawn_queue[0] = (self.spawn_queue[0][0] - dt,) \
                + self.spawn_queue[0][1:]
            if self.spawn_queue[0][0] <= 0:
                _, kind, row = self.spawn_queue.pop(0)
                self.zombies.append(Zombie(kind, row))

    # ---------- 主更新 ----------
    def update(self, dt):
        if self.state != "playing":
            return
        # 冷却
        for k in self.cooldowns:
            if self.cooldowns[k] > 0:
                self.cooldowns[k] = max(0, self.cooldowns[k] - dt)
        # 提示
        if self.message_t > 0:
            self.message_t -= dt
        # 天降阳光
        self.sky_sun_timer -= dt
        if self.sky_sun_timer <= 0:
            self.spawn_sky_sun()
            self.sky_sun_timer = C.SUN_DROP_INTERVAL
        # 实体
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
        # 波次
        self._update_spawns(dt)
        if not self.in_wave and not self.spawn_queue:
            self.wave_timer -= dt
            if self.wave_timer <= 0:
                self._start_wave()
        if self.in_wave and not self.spawn_queue and \
                not any(not z.dead for z in self.zombies):
            self.in_wave = False
            self.wave_timer = C.WAVE_PREPARE
            if self.wave >= C.WAVE_TOTAL:
                self.state = "won"
                self.message = "胜利！保卫了家园！"
                self.message_t = 999
        # 进度
        if self.zombies_total > 0:
            self.progress = min(1.0, self.zombies_killed / self.zombies_total)
        # 清理死亡
        for z in self.zombies:
            if z.dead and z.hp <= 0 and not z.reached_house:
                self.zombies_killed += 1
        self.plants = [p for p in self.plants if not p.dead]
        self.zombies = [z for z in self.zombies if not z.dead]
        self.peas = [p for p in self.peas if not p.dead]
        self.suns = [s for s in self.suns if not s.dead]
        self.explosions = [e for e in self.explosions if not e.done]
        # 失败：僵尸到家
        if any(z.reached_house for z in self.zombies + []):
            pass
        for z in self.zombies:
            if z.reached_house:
                self.state = "lost"
                self.message = "僵尸吃掉了你的脑子！"
                self.message_t = 999
                break

    def flash(self, msg):
        self.message = msg
        self.message_t = 1.4

    # ---------- 绘制草坪高亮 ----------
    def draw_hover(self, surf, mx, my):
        if self.selected is None and not self.shovel:
            return
        cell = self.cell_at(mx, my)
        if not cell:
            return
        col, row = cell
        rect = (C.LAWN_X + col * C.CELL_W, C.LAWN_Y + row * C.CELL_H,
                C.CELL_W, C.CELL_H)
        overlay = pygame.Surface((C.CELL_W, C.CELL_H), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 60))
        surf.blit(overlay, rect)
        pygame.draw.rect(surf, (255, 255, 255), rect, 2)
