# -*- coding: utf-8 -*-
"""植物大战僵尸·杂交版 —— 桌面主程序"""
import sys
import pygame

sys.path.insert(0, __file__.rsplit("\\", 1)[0])

from game import constants as C
from game import assets as A
from game.world import World
from game.ui import UI, card_rect, shovel_rect
from game.plants import SEED_BAR, PLANT_DEFS


class Game:
    def __init__(self):
        pygame.init()
        flags = pygame.SCALED
        self.screen = pygame.display.set_mode((C.SCREEN_W, C.SCREEN_H),
                                              flags, vsync=1)
        pygame.display.set_caption("植物大战僵尸·杂交版")
        self.clock = pygame.time.Clock()
        self.bg = A.make_background()
        self.ui = UI()
        self.scene = "menu"      # menu / help / playing
        self.world = None
        self.paused = False

    def reset(self):
        self.world = World()
        self.paused = False

    # ---------- 主循环 ----------
    def run(self):
        while True:
            dt = min(self.clock.tick(C.FPS) / 1000.0, 1 / 30)
            mx, my = pygame.mouse.get_pos()
            self.handle_events(mx, my)
            self.update(dt)
            self.draw(mx, my)
            pygame.display.flip()

    def handle_events(self, mx, my):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                self._on_key(e.key)
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                self._on_click(mx, my)

    def _on_key(self, key):
        if key == pygame.K_ESCAPE:
            if self.scene == "playing":
                self.paused = not self.paused
            else:
                self.scene = "menu"
        elif key == pygame.K_r and self.scene == "playing":
            self.reset()

    def _on_click(self, mx, my):
        if self.scene == "menu":
            action = self.ui.menu_button_hit(mx, my)
            if action == "play":
                self.reset()
                self.scene = "playing"
            elif action == "help":
                self.scene = "help"
            elif action == "quit":
                pygame.quit()
                sys.exit()
            return
        if self.scene == "help":
            if self.ui.help_button_hit(mx, my) == "back":
                self.scene = "menu"
            return
        # playing
        if self.world.state != "playing":
            return
        if self.paused:
            return
        # 先尝试收阳光
        if self.world.collect_sun_at(mx, my):
            return
        # 卡片
        for i, kind in enumerate(SEED_BAR):
            if card_rect(i).collidepoint(mx, my):
                d = PLANT_DEFS[kind]
                if self.world.sun >= d["cost"] and \
                        self.world.cooldowns.get(kind, 0) <= 0:
                    self.world.selected = kind
                    self.world.shovel = False
                return
        # 铲子
        if shovel_rect().collidepoint(mx, my):
            self.world.shovel = not self.world.shovel
            self.world.selected = None
            return
        # 草地
        cell = self.world.cell_at(mx, my)
        if cell:
            col, row = cell
            if self.world.shovel:
                self.world.try_shovel(col, row)
            elif self.world.selected:
                self.world.try_plant(col, row)

    def update(self, dt):
        if self.scene == "playing" and not self.paused:
            self.world.update(dt)

    # ---------- 绘制 ----------
    def draw(self, mx, my):
        if self.scene == "menu":
            self.ui.draw_menu(self.screen, mx, my)
            return
        if self.scene == "help":
            self.ui.draw_help(self.screen, mx, my)
            return
        # playing
        self.screen.blit(self.bg, (0, 0))
        self.world.draw_hover(self.screen, mx, my)
        for p in self.world.plants:
            p.draw(self.screen)
        for pea in self.world.peas:
            pea.draw(self.screen)
        for z in self.world.zombies:
            z.draw(self.screen)
        for ex in self.world.explosions:
            ex.draw(self.screen)
        for s in self.world.suns:
            s.draw(self.screen)
        self.ui.draw_hud(self.screen, self.world, mx, my)
        self.ui.draw_message(self.screen, self.world)
        if self.paused:
            self._draw_pause()
        self.ui.draw_overlay(self.screen, self.world)

    def _draw_pause(self):
        ov = pygame.Surface((C.SCREEN_W, C.SCREEN_H), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 140))
        self.screen.blit(ov, (0, 0))
        t = self.ui.title_font.render("已暂停", True, C.WHITE)
        self.screen.blit(t, t.get_rect(
            center=(C.SCREEN_W // 2, C.SCREEN_H // 2)))
        s = self.ui.font_m.render("按 ESC 继续", True, C.WHITE)
        self.screen.blit(s, s.get_rect(
            center=(C.SCREEN_W // 2, C.SCREEN_H // 2 + 60)))


def main():
    Game().run()


if __name__ == "__main__":
    main()
