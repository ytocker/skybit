"""
Scene state machine (Menu / Play / GameOver) plus the top-level App class.
"""
import math
import pygame

from game.config import W, H, FPS, TITLE, GROUND_Y
from game.draw import (
    get_sky_surface_biome, draw_mountains, draw_cloud, draw_ground,
    UI_RED,
)
from game import biome as _biome
from game.world import World
from game.hud import HUD, _font
from game import audio


STATE_MENU = 0
STATE_PLAY = 1
STATE_NAMEENTRY = 2
STATE_GAMEOVER = 3
STATE_PAUSE = 4
STATE_STATS = 5
STATE_LEADERBOARD = 6


class App:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(TITLE)
        self.screen = pygame.display.set_mode((W, H))
        self.clock = pygame.time.Clock()
        audio.init()
        self.world = World()
        self.hud = HUD()
        self.session_best = 0
        self._new_best = False
        self.state = STATE_MENU
        self._cloud_phase = 0.0
        self._running = True
        self._stats_t = 0.0
        # Touch dedup: SDL emits both FINGERDOWN and a synthetic MOUSEBUTTONDOWN
        # for one tap on mobile, so naive routing types every key twice. After
        # any FINGERDOWN, suppress mouse events for a 0.5 s window. On pure
        # desktop this never fires (no FINGERDOWN ever arrives).
        self._last_finger_t = -1e9
        self._finger_dedup_window = 0.5
        # Leaderboard state
        self._lb_scores: list = []
        self._lb_loading = False
        self._lb_player_rank = -1
        self._start_name_entry = False
        self._final_score = 0
        self._name_task = None  # strong ref prevents GC killing the task mid-flight
        self._name_input_buf = ""  # native name-entry text buffer

    # ── helpers ─────────────────────────────────────────────────────────────

    @property
    def best(self):
        return self.session_best

    # ── input ────────────────────────────────────────────────────────────────

    def _flap_input(self, pos=None):
        if self.state == STATE_MENU:
            self._start_play()
        elif self.state == STATE_PLAY:
            if pos and self.hud.pause_btn.contains(pos):
                self.state = STATE_PAUSE
                return
            self.world.flap()
        elif self.state == STATE_PAUSE:
            self.state = STATE_PLAY
        elif self.state == STATE_STATS:
            if self._stats_t >= 0.6:
                self._advance_past_stats()
        elif self.state == STATE_NAMEENTRY:
            pass  # JS overlay handles input
        elif self.state == STATE_LEADERBOARD:
            if self._cooldown_t <= 0:
                self.state = STATE_MENU
        elif self.state == STATE_GAMEOVER:
            if self._cooldown_t <= 0:
                self._restart()

    def _toggle_pause(self):
        if self.state == STATE_PLAY:
            self.state = STATE_PAUSE
        elif self.state == STATE_PAUSE:
            self.state = STATE_PLAY

    def _start_play(self):
        self.world = World()
        self.state = STATE_PLAY

    def _restart(self):
        self.world = World()
        self.state = STATE_PLAY

    # ── run loop ────────────────────────────────────────────────────────────

    def run(self):
        # Sync entry point for native execution. Browser builds (pygbag) must
        # call async_run() directly so the page's event loop stays alive.
        import asyncio
        asyncio.run(self.async_run())

    async def async_run(self):
        import asyncio
        self._cooldown_t = 0.0
        self._start_name_entry = False
        while self._running:
            dt = min(self.clock.tick(FPS) / 1000.0, 1 / 20.0)
            for e in pygame.event.get():
                self._handle_event(e)
            self._update(dt)
            self._render()
            pygame.display.flip()
            if self._start_name_entry:
                self._start_name_entry = False
                # create_task keeps the game loop running every frame while the
                # network coroutine makes progress between asyncio.sleep(0) yields.
                # Store strong ref so GC doesn't silently kill the task mid-flight.
                self._name_task = asyncio.create_task(self._on_name_submitted())
            # Yield to the browser's event loop each frame. On native runs
            # this is a zero-cost no-op between ticks.
            await asyncio.sleep(0)
        pygame.quit()

    def _handle_event(self, e):
        if e.type == pygame.QUIT:
            self._running = False
            return
        # Note when a real finger event arrives so we can suppress the
        # synthetic mouse follow-up that SDL fires for the same tap.
        now = pygame.time.get_ticks() / 1000.0
        if e.type == pygame.FINGERDOWN:
            self._last_finger_t = now
        elif e.type == pygame.MOUSEBUTTONDOWN:
            if now - self._last_finger_t < self._finger_dedup_window:
                return  # this MOUSEBUTTONDOWN is a touch echo — ignore
        import sys as _sys
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_p:
                self._toggle_pause()
                return
            if e.key == pygame.K_ESCAPE:
                if self.state in (STATE_PLAY, STATE_PAUSE):
                    self._toggle_pause()
                elif self.state == STATE_NAMEENTRY and _sys.platform != "emscripten":
                    self._submit_name_native("")  # ESC = skip
                else:
                    self._running = False
                return
            # Native name-entry keyboard: intercept before flap routing
            if self.state == STATE_NAMEENTRY and _sys.platform != "emscripten":
                if e.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    self._submit_name_native(self._name_input_buf.strip())
                elif e.key == pygame.K_BACKSPACE:
                    self._name_input_buf = self._name_input_buf[:-1]
                elif e.unicode and e.unicode.isprintable() and len(self._name_input_buf) < 16:
                    self._name_input_buf += e.unicode
                return
            if e.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                self._flap_input()
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
        elif self.state == STATE_PAUSE:
            # World is frozen. Still tick the HUD pulse so the overlay animates.
            self.hud.title_t += dt
        elif self.state == STATE_STATS:
            self.world.update(dt)  # let particles/weather keep going behind
            self._stats_t += dt
            if self._stats_t >= 4.5:
                self._advance_past_stats()
        elif self.state == STATE_NAMEENTRY:
            self.world.update(dt)  # keep world alive behind JS overlay
        elif self.state == STATE_LEADERBOARD:
            self._cooldown_t = max(0.0, self._cooldown_t - dt)
        elif self.state == STATE_GAMEOVER:
            self.world.update(dt)
            self._cooldown_t = max(0.0, self._cooldown_t - dt)

    def _on_death(self):
        score = self.world.score
        self._new_best = score > self.session_best
        if self._new_best:
            self.session_best = score
        audio.play_gameover()
        self.state = STATE_STATS
        self._stats_t = 0.0

    def _advance_past_stats(self):
        import sys
        self._final_score = self.world.score
        self._name_input_buf = ""
        self._stats_t = 0.0
        if sys.platform == "emscripten":
            # Browser: defer the qualification check + (maybe) name entry to
            # the async task — fetching top-10 from Supabase blocks. World
            # keeps ticking visibly until the task transitions us to the
            # leaderboard or opens the JS overlay.
            self.state = STATE_NAMEENTRY
            self._start_name_entry = True
        else:
            # Native: top-10 lives in local JSON, fetch is sync.
            from game import leaderboard
            scores = leaderboard._native_fetch()
            if self._qualifies_for_top10(scores, self._final_score):
                self.state = STATE_NAMEENTRY
            else:
                self._show_leaderboard_native(scores, submitted=False)

    @staticmethod
    def _qualifies_for_top10(scores, score) -> bool:
        if score <= 0:
            return False
        if len(scores) < 10:
            return True
        return score > scores[-1]["score"]

    def _show_leaderboard_native(self, scores, submitted: bool):
        self._lb_scores = scores
        self._lb_loading = False
        if scores and submitted:
            self._lb_player_rank = next(
                (i for i, e in enumerate(scores) if e["score"] == self._final_score),
                -1,
            )
        else:
            self._lb_player_rank = -1
        self.hud.title_t = 0.0
        self.state = STATE_LEADERBOARD
        self._cooldown_t = 1.0

    def _submit_name_native(self, name: str):
        """Finish native name-entry: save to local JSON, show leaderboard."""
        from game import leaderboard
        if name:
            leaderboard._native_submit(name, self._final_score)
        scores = leaderboard._native_fetch()
        self._show_leaderboard_native(scores, submitted=bool(name))

    async def _on_name_submitted(self):
        try:
            from game import leaderboard
            scores = await leaderboard.fetch_top10()
            if self._qualifies_for_top10(scores, self._final_score):
                name = await leaderboard.open_name_entry()
                if name:
                    await leaderboard.submit(name, self._final_score)
                    scores = await leaderboard.fetch_top10()
                    self._lb_player_rank = next(
                        (i for i, e in enumerate(scores) if e["score"] == self._final_score),
                        -1,
                    )
                else:
                    self._lb_player_rank = -1
            else:
                self._lb_player_rank = -1
            self._lb_scores = scores
            self._lb_loading = False
        except Exception:
            self._lb_loading = False
        self.hud.title_t = 0.0
        self.state = STATE_LEADERBOARD
        self._cooldown_t = 1.0

    # ── render ──────────────────────────────────────────────────────────────

    def _draw_background(self, surf):
        phase = self.world.biome_phase
        palette = self.world.biome_palette

        # The sky gradient is cached per phase bucket (see biome.PHASE_BUCKETS).
        # Blending the current bucket with the next one, weighted by how far
        # into the bucket we are, turns the otherwise ~10-second snap into a
        # continuous fade.
        buckets = _biome.PHASE_BUCKETS
        bucket_f = (phase % 1.0) * buckets
        a = int(bucket_f) % buckets
        b = (a + 1) % buckets
        t = bucket_f - int(bucket_f)

        pal_a = _biome.palette_for_phase(a / buckets)
        pal_b = _biome.palette_for_phase(b / buckets)
        sky_a = get_sky_surface_biome(W, H, GROUND_Y, pal_a, a)
        sky_b = get_sky_surface_biome(W, H, GROUND_Y, pal_b, b)

        sky_a.set_alpha(None)
        surf.blit(sky_a, (0, 0))
        if t > 0:
            sky_b.set_alpha(int(t * 255))
            surf.blit(sky_b, (0, 0))
            sky_b.set_alpha(None)

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

        # Weather sits between pillars and collectibles so rain/fog passes
        # behind the coins + bird — same layer a real foreground has.
        self.world.weather.draw(self.screen)

        kfc_active = self.world.bird.kfc_active
        for c in self.world.coins:
            c.draw(self.screen, kfc_active=kfc_active)
        for m in self.world.powerups:
            m.draw(self.screen)

        self.world.bird.draw(self.screen, sx, sy)

        for p in self.world.particles:
            p.draw(self.screen)

        # Slow-mo: subtle violet tint overlay so the player feels the effect
        # even without looking at the HUD.
        if self.world.slowmo_timer > 0:
            tint = pygame.Surface((W, H), pygame.SRCALPHA)
            tint.fill((140, 70, 210, 28))
            self.screen.blit(tint, (0, 0))

        # KFC mode: warm amber tint
        if self.world.kfc_timer > 0:
            tint = pygame.Surface((W, H), pygame.SRCALPHA)
            tint.fill((210, 120, 10, 20))
            self.screen.blit(tint, (0, 0))

        # Ghost mode: cool blue-white screen tint. The ring around the bird
        # was removed — the SPECTRAL parrot palette + breathing-fade alpha
        # already carry the ghost read.
        if self.world.ghost_timer > 0:
            tint = pygame.Surface((W, H), pygame.SRCALPHA)
            tint.fill((140, 180, 255, 18))
            self.screen.blit(tint, (0, 0))

        # Magnet radius — faint red ring around the bird so the pull zone is legible
        if self.world.magnet_timer > 0:
            from game.config import MAGNET_RADIUS
            import math as _math
            pulse = 0.7 + 0.3 * _math.sin(self._cloud_phase * 6.0)
            rad = int(MAGNET_RADIUS * pulse)
            ring = pygame.Surface((rad * 2 + 4, rad * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(ring, (220, 30, 40, 55),
                               (rad + 2, rad + 2), rad, 2)
            self.screen.blit(ring,
                             (self.world.bird.x + sx - rad - 2,
                              self.world.bird.y + sy - rad - 2))

        if self.world.hit_flash > 0:
            t = self.world.hit_flash / 0.35
            overlay = pygame.Surface((W, H), pygame.SRCALPHA)
            overlay.fill((*UI_RED, int(120 * t)))
            self.screen.blit(overlay, (0, 0))

        if self.state == STATE_MENU:
            self.hud.draw_menu(self.screen, 1 / 60, self.best)
        elif self.state == STATE_PLAY:
            self.hud.draw_play(self.screen, self.world, self.best)
        elif self.state == STATE_PAUSE:
            self.hud.draw_play(self.screen, self.world, self.best, paused=True)
            self.hud.draw_pause_overlay(self.screen)
        elif self.state == STATE_STATS:
            self.hud.draw_stats(self.screen, self.world, 1 / 60, self._stats_t)
        elif self.state == STATE_NAMEENTRY:
            import sys as _sys
            if _sys.platform != "emscripten":
                self.hud.draw_name_entry(self.screen, 1 / 60, self._name_input_buf)
        elif self.state == STATE_LEADERBOARD:
            self.hud.draw_leaderboard(
                self.screen, 1 / 60,
                self._lb_scores, self._lb_player_rank,
                self._lb_loading, self._cooldown_t,
            )
        else:  # GAMEOVER
            self.hud.draw_gameover(
                self.screen, 1 / 60, self.world.score, self._new_best,
            )
