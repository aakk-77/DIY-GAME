# -*- coding: utf-8 -*-
"""飞行物：豌豆（含冰/火）与阳光"""
import math
import pygame
from . import assets as A
from . import constants as C


class Pea:
    def __init__(self, x, y, row, kind="pea", delay=0.0):
        self.x = x
        self.y = y
        self.row = row
        self.kind = kind
        self.speed = 380
        self.delay = delay        # 连发间隔延迟
        self.dead = False
        if kind == "snow":
            self.img = A.draw_pea((150, 210, 245))
            self.dmg = 20
        elif kind == "fire":
            self.img = A.draw_pea((240, 120, 50))
            self.dmg = 30
        else:
            self.img = A.draw_pea((90, 200, 90))
            self.dmg = 20

    def update(self, dt, world):
        if self.delay > 0:
            self.delay -= dt
            return
        self.x += self.speed * dt
        # 碰撞该行僵尸
        for z in world.zombies:
            if z.row != self.row or z.dead:
                continue
            if abs(z.x - self.x) < 26 and self.x < z.x + 10:
                z.hit(self.dmg, self.kind)
                self.dead = True
                return
        if self.x > C.SCREEN_W + 20:
            self.dead = True

    def draw(self, surf):
        if self.delay > 0:
            return
        r = self.img.get_rect(center=(int(self.x), int(self.y)))
        surf.blit(self.img, r)


class Sun:
    """阳光：可从天降或植物产出。点击/被收集时飞向 HUD。"""
    def __init__(self, x, y, value=25, target_y=None, from_sky=True):
        self.x = x
        self.y = y
        self.target_y = target_y if target_y is not None else y
        self.value = value
        self.life = C.SUN_LIFETIME
        self.dead = False
        self.collected = False
        self.collect_t = 0.0
        self.spin = 0.0
        self.img = A.draw_sun()
        self.falling = from_sky and target_y is not None and target_y > y
        self.vy = 0.0

    def update(self, dt, world):
        self.spin += dt * 3
        if self.collected:
            # 飞向阳光计数器
            self.collect_t += dt
            tx, ty = 70, 45
            self.x += (tx - self.x) * min(1, self.collect_t * 6)
            self.y += (ty - self.y) * min(1, self.collect_t * 6)
            if self.collect_t > 0.35:
                world.add_sun(self.value)
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
        if not self.collected:
            self.collected = True

    def hit_test(self, mx, my):
        return (abs(mx - self.x) < C.SUN_COLLECT_RADIUS and
                abs(my - self.y) < C.SUN_COLLECT_RADIUS)

    def draw(self, surf):
        # 即将消失闪烁
        if self.life < 2.0 and int(self.life * 8) % 2 == 0:
            return
        # 自转缩放
        scale = 1.0 + 0.05 * math.sin(self.spin)
        img = pygame.transform.rotozoom(self.img, 0, scale)
        r = img.get_rect(center=(int(self.x), int(self.y)))
        surf.blit(img, r)
