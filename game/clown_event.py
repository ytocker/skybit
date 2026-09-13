"""Inline clown-event cinematic for LIVE gameplay (web-safe).

Once per biome day the world (game/world.py) spawns a `ClownEvent` at the clown
phase: the Plum&Lime jester strolls in trailing a floating DIE the player flies
into; the die tumbles and rolls N (10–25, with a small GHOST chance); a reveal
banner pops; and N feeds the warren gauntlet (the slot spawner in
`world._spawn_pipe`, already wired to `_clown_route` / `_clown_slot_remaining`).

This mirrors the standalone `warren_demo` clown beat, but driven by live play
instead of a script: the clown + die scroll with the world at `_current_scroll()`,
play is never paused, and a die that drifts past Pip auto-grabs so the event can
never stall. All art comes from web-safe `game/` modules (clown_art, pillar_staff,
warren_celebration) — no tools/ imports, so it ships on native + pygbag.
"""
import math
import random

import pygame

from game.config import (
    W, GROUND_Y, BIRD_X, BIRD_R, PIPE_W,
    CLOWN_SLOT_PILLARS, CLOWN_WARREN_SPACING, CLOWN_LEADIN_PILLARS,
)
from game.clown_routes import build_clown_route

# ── timing (seconds) ─────────────────────────────────────────────────────────
T_SPIN = 0.9              # die tumble before the rolled number is revealed
CELE_LIFE = 2.2           # reveal-banner life

# ── die / clown placement ────────────────────────────────────────────────────
DICE_Y = 320              # hover line for the floating die (reachable lane)
DICE_PICK_R = 30          # generous pickup radius
CLOWN_DX = 150            # clown trails this far behind (right of) the die
CLOWN_W, CLOWN_H = 240, 360
CLOWN_CX, CLOWN_FEET = 120, 250


class ClownEvent:
    """Stateful controller for one day's clown beat. Phases:
      enter   — clown + die scroll in; player can grab the die (auto-grab on pass)
      rolling — die tumbles for T_SPIN
      reveal  — banner pops, gauntlet reserved; clown scrolls off
    then `done` flips True and the world drops the controller."""

    def __init__(self):
        self.phase = "enter"
        self.done = False
        self.pulse = 0.0
        # die + clown enter from the right edge; the die leads, clown trails.
        self.dice_x = float(W + 60)
        self.dice_y = float(DICE_Y)
        self.clown_x = self.dice_x + CLOWN_DX
        self.collected = False
        self.roll = None
        self.ghost_run = False
        self.spin_t = 0.0
        self._spin_face = random.randint(10, 25)
        self._spin_face_t = 0.06
        self.die_pop_t = 0.0
        # lazy clown art (built once)
        self._clown_surf = None
        self._clown_ok = True
        self._spec = None
        self._draw_die_face = None
        # reveal-banner cache
        self._cele_base = None
        self._cele_key = None

    # ── update ────────────────────────────────────────────────────────────────
    def update(self, world, dt):
        self.pulse += dt
        scroll = max(1.0, world._current_scroll())

        if self.phase == "enter":
            self.clown_x -= scroll * dt
            self.dice_x -= scroll * dt
            if self._dice_hit(world) or self.dice_x < world.bird.x - 60:
                self._collect(world)
        elif self.phase == "rolling":
            self.clown_x -= scroll * dt
            self.spin_t += dt
            self._spin_face_t -= dt
            if self._spin_face_t <= 0.0:
                # flicker until the last beat, then settle on the real roll
                self._spin_face = (self.roll if self.spin_t >= T_SPIN - 0.18
                                   else random.randint(10, 25))
                self._spin_face_t = 0.06
            if self.spin_t >= T_SPIN:
                self._reveal(world)
        elif self.phase == "reveal":
            self.clown_x -= scroll * dt
            if self.die_pop_t > 0.0:
                self.die_pop_t -= dt
            if self.die_pop_t <= 0.0 and self.clown_x < -CLOWN_DX:
                self.done = True

    # ── interaction ─────────────────────────────────────────────────────────--
    def _dice_hit(self, world):
        b = world.bird
        ddx = self.dice_x - b.x
        ddy = self.dice_y - b.y
        return ddx * ddx + ddy * ddy <= (DICE_PICK_R + BIRD_R) ** 2

    def _collect(self, world):
        # Grab → tumble; the number reveals once the spin settles. One slot in the
        # roll pool is GHOST: the die lands on the minimum and Pip phases the route.
        self.collected = True
        pick = random.choice(list(range(10, 26)) + ["ghost"])
        self.ghost_run = pick == "ghost"
        self.roll = 10 if self.ghost_run else pick
        self.spin_t = 0.0
        self._spin_face = random.randint(10, 25)
        self._spin_face_t = 0.06
        self.phase = "rolling"

    def _reveal(self, world):
        # Spin done — pop the banner and RESERVE the gauntlet: the existing
        # _spawn_pipe slot branch lays N warren towers + (slot-N) regular fill.
        self.die_pop_t = CELE_LIFE
        world._clown_route = build_clown_route(self.roll, random)
        world._clown_slot_remaining = CLOWN_SLOT_PILLARS
        # A short "here it comes" clear-sky gap after the die settles, before the
        # first warren tower (the beat-clear above ended when the phase left
        # "rolling"). Checked ahead of the slot in _spawn_pipe.
        world._clown_leadin_remaining = CLOWN_LEADIN_PILLARS
        if self.ghost_run:
            # Phase Pip through the whole warren: size the ghost window to the N
            # warren pillars scrolling past Pip, with a tail for drift. Drives the
            # HUD bar over the true window via ghost_timer_total.
            v = max(1.0, world._current_scroll())
            total = (self.roll * CLOWN_WARREN_SPACING + (W - BIRD_X)) / v + 2.0
            world.ghost_timer = total
            world.ghost_timer_total = total
        self.phase = "reveal"

    # ── draw ──────────────────────────────────────────────────────────────────
    def draw_world(self, surf, world, sx, sy):
        """Clown + die — drawn BEFORE the pillars so the route occludes the
        strolling clown (matches the demo's layering)."""
        if self.clown_x > -CLOWN_DX:
            cx = int(self.clown_x + sx)
            fy = int(GROUND_Y + sy)
            shadow = pygame.Surface((84, 14), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow, (0, 0, 0, 70), (0, 0, 84, 14))
            surf.blit(shadow, (cx - 42, fy - 6))
            cs = self._clown_surface()
            if cs is not None:
                surf.blit(cs, (cx - CLOWN_CX, fy - CLOWN_FEET))
            else:
                pygame.draw.circle(surf, (150, 90, 200), (cx, fy - 80), 36)

        dx = int(self.dice_x + sx)
        dy = int(self.dice_y + sy)
        if not self.collected:
            self._draw_floating_die(surf, dx, dy)
        elif self.phase == "rolling":
            self._draw_spinning_die(surf, dx, dy)
        # The settled roll pops as a banner (draw_sign), not painted on the cube.

    def draw_sign(self, surf, world, sx, sy):
        """Reveal banner — drawn AFTER the HUD so it floats over the score."""
        self._draw_celebration(surf)

    # ── internals (clown bitmap + die + banner, web-safe art) ──────────────────
    def _clown_surface(self):
        if self._clown_surf is None and self._clown_ok:
            try:
                from game import clown_art
                from game.pillar_staff import draw_chosen_hero
                if self._spec is None:
                    self._spec = dict(clown_art.JESTERS[-1][1])
                    self._spec.pop("no_shadow", None)
                    self._draw_die_face = clown_art._draw_die_face_noshadow
                s = pygame.Surface((CLOWN_W, CLOWN_H), pygame.SRCALPHA)
                draw_chosen_hero(s, CLOWN_CX, CLOWN_FEET,
                                 build_jester=clown_art.build_jester,
                                 spec=self._spec)
                self._clown_surf = s
            except Exception:
                self._clown_ok = False
        return self._clown_surf

    def _ensure_die_fn(self):
        if self._draw_die_face is None:
            from game import clown_art
            self._draw_die_face = clown_art._draw_die_face_noshadow
        return self._draw_die_face

    def _draw_floating_die(self, surf, dx, dy):
        """Bobbing 3D cube with orbiting sparkles — no aura (washes white on
        the pale sky), matching the demo's clean read."""
        cy = int(dy + math.sin(self.pulse * 1.1) * 3)
        try:
            self._ensure_die_fn()(surf, dx, cy, 40, pips=5)
        except Exception:
            pygame.draw.rect(surf, (250, 246, 230), (dx - 16, cy - 16, 32, 32))
            return
        for i in range(4):
            a = i * math.tau / 4 + self.pulse * 0.4
            rr = 30 + 4 * math.sin(self.pulse * 0.9 + i)
            sxp = int(dx + math.cos(a) * rr)
            syp = int(cy + math.sin(a) * rr * 0.85)
            tw = 0.5 + 0.5 * math.sin(self.pulse * 2.0 + i * 1.7)
            al = int(110 + 130 * tw)
            sz = 3 + int(2 * tw)
            spark = pygame.Surface((sz * 4, sz * 4), pygame.SRCALPHA)
            c = (255, 244, 200, al)
            pygame.draw.line(spark, c, (sz * 2, 0), (sz * 2, sz * 4), 1)
            pygame.draw.line(spark, c, (0, sz * 2), (sz * 4, sz * 2), 1)
            pygame.draw.circle(spark, (255, 255, 230, al), (sz * 2, sz * 2), sz)
            surf.blit(spark, (sxp - sz * 2, syp - sz * 2),
                      special_flags=pygame.BLEND_ADD)

    def _draw_spinning_die(self, surf, dx, dy):
        """A short cube tumble before the reveal: spun by an ease-out angle
        settling upright, face flickering through numbers."""
        u = min(1.0, self.spin_t / T_SPIN)
        try:
            sc = pygame.Surface((96, 96), pygame.SRCALPHA)
            self._ensure_die_fn()(sc, 48, 48, 40, number=self._spin_face,
                                  body=(255, 246, 224))
            deg = 360.0 * 3 * (1.0 - (1.0 - u) ** 2)
            rot = pygame.transform.rotate(sc, deg)
            surf.blit(rot, (dx - rot.get_width() // 2, dy - rot.get_height() // 2))
        except Exception:
            pygame.draw.rect(surf, (250, 246, 230), (dx - 16, dy - 16, 32, 32))

    def _draw_celebration(self, surf):
        """The settled roll popped as the jester prize-wheel banner (design E)
        with N as the hero; a GHOST roll re-skins it cyan. Pop-scaled
        ease-out-back over ~0.3s."""
        if self.roll is None or self.die_pop_t <= 0.0:
            return
        age = max(0.0, CELE_LIFE - self.die_pop_t)
        p = min(1.0, age / 0.30)
        s = 1.70158
        e = 1 + (s + 1) * (p - 1) ** 3 + s * (p - 1) ** 2
        scale = 0.35 + 0.65 * e

        key = (self.roll, self.ghost_run)
        if self._cele_base is None or self._cele_key != key:
            try:
                from game import warren_celebration
                canvas, dw, dh = warren_celebration.render(
                    self.roll, self.ghost_run, ss=4, b_hr_ss=24)
                self._cele_base = pygame.transform.smoothscale(canvas, (dw, dh))
                self._cele_key = key
            except Exception:
                self._cele_base = None
        if self._cele_base is None:
            return

        w = max(1, int(self._cele_base.get_width() * scale))
        h = max(1, int(self._cele_base.get_height() * scale))
        out = pygame.transform.smoothscale(self._cele_base, (w, h))
        surf.blit(out, out.get_rect(center=(W // 2, 210)))
