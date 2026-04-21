"""
Scene state machine (Menu / Play / GameOver) plus the top-level App class.
App.run() is async so pygbag can export to WebAssembly.
"""
import asyncio
import math
import pygame

from game.config import W, H, FPS, TITLE, GROUND_Y
from game.draw import (
    get_sky_surface, draw_mountains, draw_cloud, draw_ground,
    blit_glow, UI_RED,
)
from game.world import World
from game.hud import HUD
from game.storage import load_highscore, save_highscore


STATE_MENU = 0
STATE_PLAY = 1
STATE_GAMEOVER = 2


class App:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(TITLE)
        self.screen = pygame.display.set_mode((W, H))
        self.clock = pygame.time.Clock()
        self.world = World()
        self.hud = HUD()
        self.best = load_highscore()
        self.state = STATE_MENU
        self.prev_best_at_death = 0
        self._cloud_phase = 0.0
        self._running = True

    # ── input ────────────────────────────────────────────────────────────────

    def _flap_input(self, pos=None):
        if self.state == STATE_MENU:
            self._start_play()
        elif self.state == STATE_PLAY:
            if pos and self.hud.pause_btn.contains(pos):
                return
            self.world.flap()
        elif self.state == STATE_GAMEOVER:
            if self._cooldown_t <= 0:
                self._restart()

    def _start_play(self):
        self.world = World()
        self.state = STATE_PLAY

    def _restart(self):
        self.world = World()
        self.state = STATE_PLAY

    # ── run loop ────────────────────────────────────────────────────────────

    async def run(self):
        self._cooldown_t = 0.0
        while self._running:
            dt = min(self.clock.tick(FPS) / 1000.0, 1 / 20.0)
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self._running = False
                elif e.type == pygame.KEYDOWN:
                    if e.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                        self._flap_input()
                    elif e.key in (pygame.K_ESCAPE,):
                        self._running = False
                elif e.type == pygame.MOUSEBUTTONDOWN:
                    self._flap_input(e.pos)
                elif e.type == pygame.FINGERDOWN:
                    self._flap_input((int(e.x * W), int(e.y * H)))

            self._update(dt)
            self._render()
            pygame.display.flip()
            await asyncio.sleep(0)
        pygame.quit()

    # ── update ──────────────────────────────────────────────────────────────

    def _update(self, dt):
        self._cloud_phase += dt
        if self.state == STATE_MENU:
            self.world.world_idle_tick(dt)
        elif self.state == STATE_PLAY:
            self.world.update(dt)
            if self.world.game_over:
                self.prev_best_at_death = self.best
                if self.world.score > self.best:
                    self.best = self.world.score
                    save_highscore(self.best)
                self.state = STATE_GAMEOVER
                self._cooldown_t = 0.8
        elif self.state == STATE_GAMEOVER:
            # Let particles and shake continue to settle
            self.world.update(dt)
            self._cooldown_t = max(0.0, self._cooldown_t - dt)

    # ── render ──────────────────────────────────────────────────────────────

    def _draw_background(self, surf):
        # sky
        sky = get_sky_surface(W, H, GROUND_Y)
        surf.blit(sky, (0, 0))
        # clouds (parallax)
        scroll = self.world.bg_scroll
        for i, (bx, by, sc) in enumerate(((20, 90, 0.9), (180, 140, 1.1), (60, 220, 0.8), (230, 60, 0.7))):
            ox = ((bx - scroll * (0.04 + 0.02 * i)) % (W + 120)) - 60
            draw_cloud(surf, ox, by + math.sin(self._cloud_phase * 0.3 + i) * 3, sc)
        # mountains
        draw_mountains(surf, scroll, GROUND_Y, W)
        # ground
        draw_ground(surf, GROUND_Y, W, H, scroll)

    def _render(self):
        sx, sy = self.world.shake_offset() if self.state != STATE_MENU else (0, 0)
        sx, sy = int(sx), int(sy)
        self._draw_background(self.screen)

        # entities
        for p in self.world.pipes:
            p.draw(self.screen)
        for c in self.world.coins:
            c.draw(self.screen)
        for m in self.world.mushrooms:
            m.draw(self.screen)

        # aura while triple is active
        if self.world.triple_timer > 0 and self.world.bird.alive:
            pulse = 10 + int(math.sin(pygame.time.get_ticks() * 0.01) * 3)
            blit_glow(self.screen, int(self.world.bird.x + sx), int(self.world.bird.y + sy),
                      28 + pulse, (255, 170, 60), 160)

        # bird
        self.world.bird.draw(self.screen, sx, sy)

        # particles
        for p in self.world.particles:
            p.draw(self.screen)

        # death flash (red tint, short) — intentional, NOT for coin pickup
        if self.world.hit_flash > 0:
            t = self.world.hit_flash / 0.35
            overlay = pygame.Surface((W, H), pygame.SRCALPHA)
            overlay.fill((*UI_RED, int(120 * t)))
            self.screen.blit(overlay, (0, 0))

        if self.state == STATE_MENU:
            self.hud.draw_menu(self.screen, 1 / 60, self.best)
        elif self.state == STATE_PLAY:
            self.hud.draw_play(self.screen, self.world, self.best)
        else:
            new_best = self.world.score > self.prev_best_at_death
            self.hud.draw_play(self.screen, self.world, self.best)
            self.hud.draw_gameover(self.screen, 1 / 60, self.world.score, self.best, new_best)
