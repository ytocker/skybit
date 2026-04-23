"""
Scene state machine (Menu / Play / NameEntry / GameOver) plus the
top-level App class.
"""
import math
import pygame

from game.config import W, H, FPS, TITLE, GROUND_Y
from game.draw import (
    get_sky_surface_biome, draw_mountains, draw_cloud, draw_ground,
    blit_glow, UI_RED,
)
from game import biome as _biome
from game.world import World
from game.hud import HUD, _font
from game.storage import (
    load_scores, save_scores, qualifies_for_top, insert_score, best_score,
)
from game.nameentry import NameEntry
from game import audio


STATE_MENU = 0
STATE_PLAY = 1
STATE_NAMEENTRY = 2
STATE_GAMEOVER = 3


class App:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(TITLE)
        self.screen = pygame.display.set_mode((W, H))
        self.clock = pygame.time.Clock()
        audio.init()
        self.world = World()
        self.hud = HUD()
        self.scores: list[dict] = load_scores()
        self.state = STATE_MENU
        self.name_entry: NameEntry | None = None
        self.highlight_rank = -1
        self.prev_best_at_death = 0
        self._cloud_phase = 0.0
        self._running = True

    # ── helpers ─────────────────────────────────────────────────────────────

    @property
    def best(self):
        return best_score(self.scores)

    # ── input ────────────────────────────────────────────────────────────────

    def _flap_input(self, pos=None):
        if self.state == STATE_MENU:
            self._start_play()
        elif self.state == STATE_PLAY:
            if pos and self.hud.pause_btn.contains(pos):
                return
            self.world.flap()
        elif self.state == STATE_NAMEENTRY:
            # handled via direct event path
            pass
        elif self.state == STATE_GAMEOVER:
            if self._cooldown_t <= 0:
                self._restart()

    def _start_play(self):
        self.world = World()
        self.state = STATE_PLAY
        self.highlight_rank = -1

    def _restart(self):
        self.world = World()
        self.state = STATE_PLAY
        self.highlight_rank = -1

    # ── run loop ────────────────────────────────────────────────────────────

    def run(self):
        self._cooldown_t = 0.0
        while self._running:
            dt = min(self.clock.tick(FPS) / 1000.0, 1 / 20.0)
            for e in pygame.event.get():
                self._handle_event(e)
            self._update(dt)
            self._render()
            pygame.display.flip()
        pygame.quit()

    def _handle_event(self, e):
        if e.type == pygame.QUIT:
            self._running = False
            return
        if self.state == STATE_NAMEENTRY:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    # quick exit — treat as submit whatever's there
                    self.name_entry.submit()
                else:
                    self.name_entry.handle_key(e)
            elif e.type == pygame.MOUSEBUTTONDOWN:
                self.name_entry.handle_tap(e.pos)
            elif e.type == pygame.FINGERDOWN:
                self.name_entry.handle_tap((int(e.x * W), int(e.y * H)))
            return
        # non name-entry states
        if e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                self._flap_input()
            elif e.key == pygame.K_ESCAPE:
                self._running = False
        elif e.type == pygame.MOUSEBUTTONDOWN:
            self._flap_input(e.pos)
        elif e.type == pygame.FINGERDOWN:
            self._flap_input((int(e.x * W), int(e.y * H)))

    # ── update ──────────────────────────────────────────────────────────────

    def _update(self, dt):
        self._cloud_phase += dt
        if self.state == STATE_MENU:
            self.world.world_idle_tick(dt)
        elif self.state == STATE_PLAY:
            self.world.update(dt)
            if self.world.game_over:
                self._on_death()
        elif self.state == STATE_NAMEENTRY:
            self.world.update(dt)  # let particles settle
            self.name_entry.update(dt)
            if self.name_entry.done:
                self._commit_name()
        elif self.state == STATE_GAMEOVER:
            self.world.update(dt)
            self._cooldown_t = max(0.0, self._cooldown_t - dt)

    def _on_death(self):
        score = self.world.score
        self.prev_best_at_death = self.best
        audio.play_gameover()
        if qualifies_for_top(score, self.scores):
            # insert a preview entry so the user sees the rank, then overwrite name
            preview, rank = insert_score(self.scores, "???", score)
            self.highlight_rank = rank
            self.name_entry = NameEntry(score, rank)
            self.state = STATE_NAMEENTRY
        else:
            self.state = STATE_GAMEOVER
            self._cooldown_t = 0.8

    def _commit_name(self):
        score = self.world.score
        name = self.name_entry.submitted_name or "???"
        new_list, rank = insert_score(self.scores, name, score)
        self.scores = new_list
        self.highlight_rank = rank
        save_scores(self.scores)
        self.name_entry = None
        self.state = STATE_GAMEOVER
        self._cooldown_t = 0.5

    # ── render ──────────────────────────────────────────────────────────────

    def _draw_background(self, surf):
        phase = self.world.biome_phase
        palette = self.world.biome_palette
        bucket = _biome.phase_bucket(phase)
        sky = get_sky_surface_biome(W, H, GROUND_Y, palette, bucket)
        surf.blit(sky, (0, 0))
        scroll = self.world.bg_scroll
        for i, (bx, by, sc, variant) in enumerate((
                (20, 90, 0.9, 0), (180, 140, 1.1, 2),
                (60, 220, 0.8, 3), (230, 60, 0.7, 1),
                (320, 180, 0.9, 4))):
            ox = ((bx - scroll * (0.04 + 0.02 * i)) % (W + 160)) - 80
            draw_cloud(surf, ox,
                       by + math.sin(self._cloud_phase * 0.3 + i) * 3,
                       sc, variant=variant)
        draw_mountains(surf, scroll, GROUND_Y, W, palette['mtn_far'], palette['mtn_near'])
        draw_ground(surf, GROUND_Y, W, H, scroll,
                    palette['ground_top'], palette['ground_mid'], (60, 40, 25))

    def _render(self):
        sx, sy = self.world.shake_offset() if self.state == STATE_PLAY else (0, 0)
        sx, sy = int(sx), int(sy)
        self._draw_background(self.screen)

        pipe_palette = self.world.biome_palette
        for p in self.world.pipes:
            p.draw(self.screen, pipe_palette)
        for c in self.world.coins:
            c.draw(self.screen)
        for m in self.world.mushrooms:
            m.draw(self.screen)

        if self.world.triple_timer > 0 and self.world.bird.alive:
            pulse = 10 + int(math.sin(pygame.time.get_ticks() * 0.01) * 3)
            blit_glow(self.screen, int(self.world.bird.x + sx), int(self.world.bird.y + sy),
                      28 + pulse, (255, 170, 60), 160)

        self.world.bird.draw(self.screen, sx, sy)

        for p in self.world.particles:
            p.draw(self.screen)

        if self.world.hit_flash > 0:
            t = self.world.hit_flash / 0.35
            overlay = pygame.Surface((W, H), pygame.SRCALPHA)
            overlay.fill((*UI_RED, int(120 * t)))
            self.screen.blit(overlay, (0, 0))

        if self.state == STATE_MENU:
            self.hud.draw_menu(self.screen, 1 / 60, self.best)
        elif self.state == STATE_PLAY:
            self.hud.draw_play(self.screen, self.world, self.best)
        elif self.state == STATE_NAMEENTRY:
            self.name_entry.draw(self.screen, _font)
        else:  # GAMEOVER
            new_best = self.world.score > self.prev_best_at_death and self.highlight_rank == 0
            self.hud.draw_gameover(
                self.screen, 1 / 60, self.world.score,
                self.scores, new_best, self.highlight_rank,
            )
