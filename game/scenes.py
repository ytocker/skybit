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
from game import play_log
from game.config import BIRD_X, SCROLL_BASE
from game import intro as _intro

# Pixels of `bg_scroll` covered while the gameplay opener is active. After
# the post-ready grace window, the cottage is fully off-screen-left and the
# overlay shuts itself off.
_OPENER_SCROLL_END = int(World.SPAWN_GRACE * SCROLL_BASE)


def _draw_opener(surf: pygame.Surface, world) -> None:
    """Gameplay opener — cottage drifting off-screen-left + parcel tucked
    beneath Pip. Mirrors the intro's beat-2 ending so the cut from menu →
    play preserves the cinematic's final image. Runs for the first
    ``World.SPAWN_GRACE`` seconds after the ready_t freeze expires."""
    progress = world.bg_scroll / _OPENER_SCROLL_END
    if progress >= 1.0:
        return
    # Fade out over the last 30% so the cottage doesn't snap-disappear.
    fade = 1.0 if progress < 0.7 else max(0.0, 1.0 - (progress - 0.7) / 0.3)
    alpha = int(255 * fade)

    house = _intro.get_sprite("skyhouse_post")
    house_cx = int(W * 0.30) - int(world.bg_scroll)
    house_cy = int(H * 0.42)
    hx = house_cx - house.get_width() // 2
    hy = house_cy - house.get_height() // 2
    if hx + house.get_width() > 0 and alpha > 0:
        if alpha < 255:
            faded = house.copy()
            faded.set_alpha(alpha)
            surf.blit(faded, (hx, hy))
        else:
            surf.blit(house, (hx, hy))
    # The parcel itself is now drawn permanently by Bird.draw, so the
    # opener no longer needs its own parcel pass.


STATE_MENU = 0
STATE_PLAY = 1
STATE_NAMEENTRY = 2
STATE_GAMEOVER = 3
STATE_PAUSE = 4
STATE_STATS = 5
STATE_LEADERBOARD = 6
STATE_INTRO = 7


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
        # Intro plays once per program launch — start every session in
        # STATE_INTRO. Within the session (consecutive games after death,
        # menu-tap → play → die → menu) the intro is never replayed since
        # the App stays alive and we already moved past STATE_INTRO.
        from game.intro import IntroScene
        self.intro: object | None = IntroScene()
        self.state = STATE_INTRO
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
        self._lb_player_rank = -1
        self._start_name_entry = False
        self._fetch_pending = False
        self._final_score = 0
        self._name_task = None  # strong ref prevents GC killing the task mid-flight
        self._play_log_task = None  # strong ref for the per-run telemetry POST
        self._name_input_buf = ""  # native name-entry text buffer

    # ── helpers ─────────────────────────────────────────────────────────────

    @property
    def best(self):
        return self.session_best

    # ── input ────────────────────────────────────────────────────────────────

    def _flap_input(self, pos=None):
        if self.state == STATE_INTRO:
            # Any tap during the cinematic skips it and lands on the menu —
            # the menu is where SKYBIT + the description + the click-to-start
            # prompt live. The intro is recorded as seen so it never replays.
            self._finish_intro()
            return
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
            if self._stats_t >= 0.6 and not self._fetch_pending:
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
        # The menu IS the start-of-game screen, so the click that brought
        # us here counts as the first flap — drop the ready_t freeze and
        # apply an initial flap so Pip launches immediately. The gameplay
        # opener (post-house drifting off-screen-left) still plays for
        # the first ~2.5 s of bg_scroll.
        self.world = World()
        self.world.ready_t = 0.0
        self.world.flap()
        self.state = STATE_PLAY

    def _finish_intro(self):
        """Hand off to the menu. Called on auto-completion or skip. The
        intro is dropped so this session won't render it again."""
        if self.intro is not None:
            self.intro.skip()
        self.intro = None
        self.state = STATE_MENU

    def _restart(self):
        # Same contract as `_start_play`: the tap that triggered the
        # restart counts as the first flap, no ready freeze.
        self.world = World()
        self.world.ready_t = 0.0
        self.world.flap()
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
                else:
                    self._running = False
                return
            # Native name-entry keyboard: intercept before flap routing.
            # ENTER submits; ESC no longer skips — there's a clickable
            # SKIP button now.
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
            if self._handle_name_entry_click(e.pos):
                return
            self._flap_input(e.pos)
        elif e.type == pygame.FINGERDOWN:
            pos = (int(e.x * W), int(e.y * H))
            if self._handle_name_entry_click(pos):
                return
            self._flap_input(pos)

    def _handle_name_entry_click(self, pos) -> bool:
        """If we're on the native name-entry screen and the click hit the
        SUBMIT or SKIP button, dispatch and return True. Returns False
        otherwise so normal flap routing can proceed."""
        import sys as _sys
        if self.state != STATE_NAMEENTRY or _sys.platform == "emscripten":
            return False
        if self.hud.name_submit_rect.collidepoint(pos):
            if self._name_input_buf.strip():
                self._submit_name_native(self._name_input_buf.strip())
            return True
        if self.hud.name_skip_rect.collidepoint(pos):
            self._submit_name_native("")
            return True
        return False

    # ── update ──────────────────────────────────────────────────────────────

    def _update(self, dt):
        self._cloud_phase += dt
        if self.state == STATE_INTRO:
            if self.intro is None:
                # Defensive: should never happen, but recover gracefully.
                self._finish_intro()
                return
            self.intro.update(dt)
            if self.intro.done:
                self._finish_intro()
            return
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
            # No auto-advance — the screen stays until the player taps
            # (handled in _flap_input).
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
        # Fire-and-forget telemetry: send the run summary to Supabase
        # (browser-only; native is a silent no-op). Strong ref on
        # self prevents GC from killing the task mid-flight.
        import asyncio as _asyncio
        try:
            self._play_log_task = _asyncio.create_task(play_log.log_run(self.world))
        except RuntimeError:
            # No running loop (e.g. headless smoke tests) — skip silently.
            pass
        # Game-over screen no longer plays its own jingle — death.ogg
        # at the moment of impact carries the whole "run ended" cue.
        self.state = STATE_STATS
        self._stats_t = 0.0

    def _advance_past_stats(self):
        import sys
        self._final_score = self.world.score
        self._name_input_buf = ""
        if sys.platform == "emscripten":
            # Browser: stay on the stats screen while an async task fetches
            # the top-10 from Supabase. When the task resolves it switches
            # state to STATE_NAMEENTRY (qualifiers) or STATE_LEADERBOARD
            # (everyone else) — no transitional loading screen.
            self._lb_scores = []
            self._lb_player_rank = -1
            self._fetch_pending = True
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
                # Now we know they qualify — flip to NAMEENTRY so the
                # Python-side render and the JS overlay both come up
                # together. Not before; otherwise non-qualifiers see a
                # name-entry screen flash for the duration of the fetch.
                self.state = STATE_NAMEENTRY
                name = await leaderboard.open_name_entry()
                if name:
                    await leaderboard.submit(name, self.world)
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
        except Exception:
            pass
        self._fetch_pending = False
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
        # Intro renders its own self-contained scene (sky + pillars + cottage
        # + parrot etc.) and bypasses the in-game world draw entirely.
        if self.state == STATE_INTRO and self.intro is not None:
            self.intro.render(self.screen)
            return
        sx, sy = self.world.shake_offset() if self.state == STATE_PLAY else (0, 0)
        sx, sy = int(sx), int(sy)
        self._draw_background(self.screen)

        # Menu scene = the gameplay opener as a static frame: pickup post-
        # house on the left with Pip standing in front of it holding the
        # parcel. No pillars or world entities until the user taps to start.
        if self.state == STATE_MENU:
            house = _intro.get_sprite("skyhouse_post")
            hx = int(W * 0.30) - house.get_width() // 2
            hy = int(H * 0.42) - house.get_height() // 2
            self.screen.blit(house, (hx, hy))
            self.world.bird.draw(self.screen, sx, sy)
            self.hud.draw_menu(self.screen, 1 / 60, self.best)
            return

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

        # Gameplay opener: pickup post-house drifting off-screen-left + the
        # parcel tucked under Pip. Active only during STATE_PLAY's first
        # ~2.5 s, mirroring the intro's beat-2 closing image.
        if self.state == STATE_PLAY:
            _draw_opener(self.screen, self.world)

        self.world.bird.draw(self.screen, sx, sy,
                             flipped=self.world.reverse_timer > 0)

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

        # Magnet force-field — Solar Gold palette: warm amber-gold rings
        # + golden glow with a coherent dramatic breath. All elements
        # (3 rings + inner radial glow) driven by a single pulse factor
        # so the field shrinks and grows as one volume. Pulse rate 5.5
        # ⇒ ~1.14 s cycle (slightly faster than the original 1.57 s).
        if self.world.magnet_timer > 0:
            from game.config import MAGNET_RADIUS
            import math as _math
            t_pulse = self._cloud_phase * 5.5
            rad = MAGNET_RADIUS
            field = pygame.Surface((rad * 2 + 8, rad * 2 + 8),
                                   pygame.SRCALPHA)
            lcx, lcy = rad + 4, rad + 4

            # Outer-ring pulse factor — drives BOTH the rings and the glow
            BREATH = 0.30
            s_outer = _math.sin(t_pulse + 0.0)
            u_outer = (s_outer + 1) / 2
            outer_factor = 1.0 - BREATH * (1.0 - u_outer)
            glow_rad = rad * outer_factor

            # Inner radial glow — bell-curve falloff peaking near the
            # outer edge, gold colour, scaled by the same pulse.
            GLOW_COL = (245, 175, 40)
            for i in range(18, 0, -1):
                r = int(glow_rad * i / 18)
                inner_t = i / 18
                bell = _math.exp(-((inner_t - 0.85) ** 2) / 0.15)
                a = int(72 * bell)
                if a > 0:
                    pygame.draw.circle(field, (*GLOW_COL, a),
                                       (lcx, lcy), r)

            # 3 rings with per-ring gold tints, slightly out of phase.
            AA_COL = (255, 240, 180)
            for rfac, phase, alpha, width, breath_scale, ring_col in (
                    (1.00, 0.0,  180, 3, 1.00, (255, 220, 100)),
                    (0.78, 0.6,  140, 2, 0.85, (255, 195,  60)),
                    (0.55, 1.2,  100, 2, 0.70, (235, 165,  35))):
                amp = BREATH * breath_scale
                s = _math.sin(t_pulse + phase)
                u = (s + 1) / 2
                rr = int(rad * rfac * (1.0 - amp * (1.0 - u)))
                # Anti-alias ring with two ⅓-alpha satellites + main pass
                pygame.draw.circle(field, (*AA_COL, alpha // 3),
                                   (lcx, lcy), rr + 1, width)
                pygame.draw.circle(field, (*AA_COL, alpha // 3),
                                   (lcx, lcy), rr - 1, width)
                pygame.draw.circle(field, (*ring_col, alpha),
                                   (lcx, lcy), rr, width)

            self.screen.blit(field,
                             (int(self.world.bird.x) + sx - lcx,
                              int(self.world.bird.y) + sy - lcy))

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
            self.hud.draw_stats(self.screen, self.world, 1 / 60, self._stats_t,
                                show_prompt=not self._fetch_pending)
        elif self.state == STATE_NAMEENTRY:
            import sys as _sys
            if _sys.platform != "emscripten":
                self.hud.draw_name_entry(self.screen, 1 / 60, self._name_input_buf)
        elif self.state == STATE_LEADERBOARD:
            self.hud.draw_leaderboard(
                self.screen, 1 / 60,
                self._lb_scores, self._lb_player_rank,
                self._cooldown_t,
            )
        else:  # GAMEOVER
            self.hud.draw_gameover(
                self.screen, 1 / 60, self.world.score, self._new_best,
            )
