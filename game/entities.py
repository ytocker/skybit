"""
Game entities: Bird, Pipe, Coin, Mushroom, Particle, FloatText.
All drawing is smooth (gradients, alpha, glows) — no pixel art.

Pipes are sandstone pillars topped with living vegetation, re-tinted by the
active biome palette. Coins are slow-rotating metallic gold discs with
embossed detail.
"""
import math
import random
import pygame

from game.config import (
    W, H, GRAVITY, FLAP_V, MAX_FALL,
    BIRD_X, BIRD_R, PIPE_W, COIN_R, MUSHROOM_R, GROUND_Y,
)
from game.draw import (
    blit_glow, draw_pillar_mist,
    rounded_rect, lerp_color,
    COIN_GOLD, COIN_LIGHT, COIN_DARK,
    MUSH_CAP, MUSH_CAP2, MUSH_SPOT, MUSH_STEM,
    PARTICLE_GOLD, PARTICLE_ORNG, PARTICLE_WHT, PARTICLE_CRIM,
    NEAR_BLACK, WHITE,
)
from game import parrot
from game.pillar_variants import draw_pillar_pair


# Default pillar palette (fallback when no biome provided).
_DEFAULT_PILLAR = {
    'stone_light':     (225, 195, 155),
    'stone_mid':       (175, 140, 105),
    'stone_dark':      (95, 70, 55),
    'stone_accent':    (255, 220, 170),
    'foliage_top':     (140, 220, 110),
    'foliage_mid':     (70, 170, 75),
    'foliage_dark':    (30, 100, 50),
    'foliage_accent':  (255, 240, 120),
}


# ── Bird ─────────────────────────────────────────────────────────────────────

class Bird:
    def __init__(self):
        self.x = BIRD_X
        self.y = H * 0.42
        self.vy = 0.0
        self.alive = True
        self.frame_t = 0.0
        self.flap_boost = 0.0

    @property
    def tilt_deg(self):
        # Clamp the downward dive so a fast-falling bird doesn't read as
        # already crashing (REVIEW.md feedback).
        t = max(-0.5, min(0.75, self.vy / 500.0))
        return -t * 55.0

    def flap(self):
        if self.alive:
            self.vy = FLAP_V
            self.flap_boost = 0.45

    def update(self, dt):
        self.vy = min(self.vy + GRAVITY * dt, MAX_FALL)
        self.y += self.vy * dt

        base_hz = 9.0 + self.flap_boost * 20.0
        if self.vy < -100:
            base_hz += 3.0
        elif self.vy > 200:
            base_hz = max(3.0, base_hz - 4.0)
        self.frame_t = (self.frame_t + dt * base_hz)
        self.flap_boost = max(0.0, self.flap_boost - dt * 1.8)

    def draw(self, surf, shake_x=0, shake_y=0):
        frame_idx = int(self.frame_t) % len(parrot.FRAMES)
        img = parrot.get_parrot(frame_idx, self.tilt_deg)
        r = img.get_rect(center=(self.x + shake_x, self.y + shake_y))
        surf.blit(img, r.topleft)


# ── Pipe (nature pillar) ─────────────────────────────────────────────────────

class Pipe:
    """Sandstone pillar column. Each instance picks one of 8 visual variants
    (original + 7 sketched picks) deterministically from its seed, so the
    vegetation and ornament arrangement is stable across frames."""

    def __init__(self, x: float, gap_y: float, gap_h: float):
        self.x = x
        self.gap_y = gap_y
        self.gap_h = gap_h
        self.scored = False
        self.is_rush = False
        # Per-instance random seed → chooses variant + stable decoration seed
        self.seed = random.randint(0, 0xFFFFFF)

    @property
    def top_rect(self):
        return pygame.Rect(int(self.x), 0, PIPE_W, int(self.gap_y - self.gap_h / 2))

    @property
    def bot_rect(self):
        top = int(self.gap_y + self.gap_h / 2)
        return pygame.Rect(int(self.x), top, PIPE_W, GROUND_Y - top)

    def off_screen(self):
        return self.x + PIPE_W + 8 < 0

    def collides_circle(self, cx, cy, r):
        return self.top_rect.colliderect(pygame.Rect(cx - r, cy - r, r * 2, r * 2)) or \
               self.bot_rect.colliderect(pygame.Rect(cx - r, cy - r, r * 2, r * 2))

    def draw(self, surf, palette=None):
        palette = palette or _DEFAULT_PILLAR
        draw_pillar_pair(surf, self.top_rect, self.bot_rect, palette, self.seed)
        # Mist halo at the base where the bottom pillar meets the ground
        bot = self.bot_rect
        draw_pillar_mist(surf, bot.x + bot.width // 2, bot.bottom, bot.width, alpha=110)


# ── Coin ─────────────────────────────────────────────────────────────────────

class Coin:
    """Slow-rotating gold parrot medallion, drawn with no halo or glow.

    Every frame the coin is drawn directly onto the target surface as an
    ellipse squeezed horizontally by |cos(spin)|. No cached face, no
    smoothscale blur, no radial aura — the silhouette you see is the
    silhouette you collect (COIN_R governs both).
    """

    SPIN_RATE = 1.1  # ≈ 5.7 seconds per full rotation

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.spin = random.uniform(0, math.tau)
        self.collected = False
        self.float_t = random.uniform(0, math.tau)

    def update(self, dt):
        self.spin = (self.spin + dt * self.SPIN_RATE) % math.tau
        self.float_t += dt

    def draw(self, surf):
        cx = int(self.x)
        cy = int(self.y + math.sin(self.float_t * 2.2) * 2.5)
        cos_s = math.cos(self.spin)
        r = COIN_R
        rx = max(1, int(abs(cos_s) * r))

        # Drop shadow
        sh = pygame.Surface((rx * 2 + 10, 6), pygame.SRCALPHA)
        pygame.draw.ellipse(sh, (0, 0, 0, 55), sh.get_rect())
        surf.blit(sh, (cx - rx - 5, cy + r + 1))

        # Tight warm glow — just enough to lift it off the background
        blit_glow(surf, cx, cy, r + 3, (255, 200, 20), 35)

        if abs(cos_s) <= 0.30:
            pygame.draw.ellipse(surf, COIN_DARK, (cx-rx-1, cy-r, (rx+1)*2, r*2))
            pygame.draw.ellipse(surf, COIN_GOLD,  (cx-rx,   cy-r,  rx*2,    r*2))
            return

        # 1. Dark rim
        pygame.draw.ellipse(surf, COIN_DARK,
                            (cx-rx-1, cy-r-1, (rx+1)*2+2, (r+1)*2))
        # 2. Gold body
        pygame.draw.ellipse(surf, COIN_GOLD, (cx-rx, cy-r, rx*2, r*2))
        # 3. Bright inner zone for 3-D depth
        if rx > 5:
            ir = max(2, rx - 3)
            pygame.draw.ellipse(surf, COIN_LIGHT,
                                (cx-ir, cy-r+3, ir*2, (r-3)*2))

        # Large specular crescent — upper-left, scales with cos_s
        if abs(cos_s) > 0.4 and rx > 4:
            spec_a = min(255, int(180 + 70 * abs(cos_s)))
            spec_w = max(3, int(rx * 0.65))
            spec_h = max(3, int(r * 0.42))
            spec = pygame.Surface((spec_w*2, spec_h*2), pygame.SRCALPHA)
            pygame.draw.ellipse(spec, (255, 255, 240, spec_a), spec.get_rect())
            surf.blit(spec, (cx - spec_w//2 - rx//2 - 1, cy - r + 1))

        # Embossed parrot (face-on only)
        if abs(cos_s) > 0.75:
            em = (145, 88, 0)
            pygame.draw.ellipse(surf, em, (cx-2, cy-1, 7, 5))
            pygame.draw.circle(surf, em, (cx-1, cy-3), 3)
            pygame.draw.polygon(surf, em,
                                [(cx-3,cy-3),(cx-6,cy-2),(cx-3,cy-1)])
            pygame.draw.circle(surf, COIN_GOLD, (cx, cy-4), 1)

        # 4-point sparkle flash at upper-right edge, cycles with float_t
        shimmer_t = (self.float_t * 1.4) % math.tau
        if shimmer_t < 0.85:
            sa = int(230 * math.sin(shimmer_t * math.pi / 0.85))
            spx = cx + int(rx * 0.65)
            spy = cy - int(r * 0.65)
            sp = pygame.Surface((12, 12), pygame.SRCALPHA)
            m = 6
            c4 = (255, 255, 240, sa)
            pygame.draw.line(sp, c4, (m, m-5), (m, m+5), 1)
            pygame.draw.line(sp, c4, (m-5, m), (m+5, m), 1)
            pygame.draw.line(sp, (255,255,255,sa//2), (m-3,m-3),(m+3,m+3), 1)
            pygame.draw.line(sp, (255,255,255,sa//2), (m+3,m-3),(m-3,m+3), 1)
            pygame.draw.circle(sp, (255,255,255,sa), (m,m), 2)
            surf.blit(sp, (spx-m, spy-m))


# ── PowerUp ──────────────────────────────────────────────────────────────────

class PowerUp:
    """A collectible buff. `kind` selects visuals and pickup effect:
       triple  — red mushroom, 3x coin value for TRIPLE_DURATION
       magnet  — red horseshoe, pulls coins in for MAGNET_DURATION
       slowmo  — purple hourglass, 0.5x world scroll for SLOWMO_DURATION
    """
    def __init__(self, x, y, kind="triple"):
        self.x = x
        self.y = y
        self.kind = kind
        self.collected = False
        self.pulse = 0.0

    def update(self, dt):
        self.pulse += dt * 3.5

    def draw(self, surf):
        if self.kind == "triple":
            self._draw_mushroom(surf)
        elif self.kind == "magnet":
            self._draw_magnet(surf)
        elif self.kind == "slowmo":
            self._draw_slowmo(surf)

    # ── sprite variants ─────────────────────────────────────────────────────
    def _draw_mushroom(self, surf):
        cx = int(self.x)
        cy = int(self.y + math.sin(self.pulse * 0.9) * 2.0)
        r = MUSHROOM_R

        # Bottom drop shadow
        sh_w = r * 3
        sh = pygame.Surface((sh_w, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(sh, (0, 0, 0, 80), sh.get_rect())
        surf.blit(sh, (cx - sh_w // 2, cy + r + 4))

        # 3 orbiting pink sparkle dots
        for i in range(3):
            ang = self.pulse * 1.4 + i * (math.tau / 3)
            ox = int(math.cos(ang) * (r + 6))
            oy = int(math.sin(ang) * (r + 3))
            sp_a = max(50, int(155 + 80 * math.sin(ang * 2)))
            sp = pygame.Surface((6, 6), pygame.SRCALPHA)
            pygame.draw.circle(sp, (255, 160, 180, sp_a), (3, 3), 3)
            surf.blit(sp, (cx + ox - 3, cy + oy - 3))

        # Stem
        stem = pygame.Rect(cx - 7, cy + 2, 14, 12)
        rounded_rect(surf, stem, 4, MUSH_STEM, 255)
        pygame.draw.line(surf, (255, 255, 230), (cx - 4, cy + 4), (cx - 4, cy + 12), 2)
        pygame.draw.line(surf, (180, 155, 115), (cx + 3, cy + 4), (cx + 3, cy + 12), 1)

        # Cap: thick dark outline → vivid red body → bright top arc
        cap_rect = pygame.Rect(cx - r - 1, cy - r + 2, (r + 1) * 2, r + 5)
        pygame.draw.ellipse(surf, (80, 4, 8),    cap_rect.inflate(4, 4))  # blackest outer rim
        pygame.draw.ellipse(surf, (160, 10, 18), cap_rect.inflate(2, 2))  # crimson outline
        pygame.draw.ellipse(surf, MUSH_CAP,      cap_rect)                 # vivid red

        # Bright highlight arc at top of cap
        hi = pygame.Rect(cap_rect.x + 2, cap_rect.y + 1, cap_rect.width - 4, 8)
        pygame.draw.ellipse(surf, MUSH_CAP2, hi)

        # Sweeping specular sheen
        sheen_x = int(math.sin(self.pulse * 1.3) * 4)
        sh2_a = min(255, int(150 + 80 * math.sin(self.pulse * 1.3)))
        sh2 = pygame.Surface((cap_rect.width - 12, 4), pygame.SRCALPHA)
        pygame.draw.ellipse(sh2, (255, 240, 220, sh2_a), sh2.get_rect())
        surf.blit(sh2, (cap_rect.x + 6 + sheen_x, cap_rect.y + 3))

        # White spots — larger with pink border and bright center
        for sx, sy, sr in ((cx - 7, cy - 5, 3),
                           (cx + 6, cy - 7, 4),
                           (cx + 2, cy + 1, 3),
                           (cx - 3, cy + 2, 2)):
            pygame.draw.circle(surf, (240, 185, 200), (sx, sy), sr + 2)  # pink border
            pygame.draw.circle(surf, MUSH_SPOT,       (sx, sy), sr + 1)  # white fill
            pygame.draw.circle(surf, (255, 255, 255), (sx, sy), max(1, sr - 1))  # bright center

    def _draw_magnet(self, surf):
        cx = int(self.x)
        cy = int(self.y + math.sin(self.pulse * 1.1) * 2.0)
        r = MUSHROOM_R

        # Bottom drop shadow
        sh_w = r * 3
        sh = pygame.Surface((sh_w, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(sh, (0, 0, 0, 80), sh.get_rect())
        surf.blit(sh, (cx - sh_w // 2, cy + r + 2))

        # 4 orbiting blue-white charged-particle dots (counter-clockwise)
        for i in range(4):
            ang = -self.pulse * 1.6 + i * (math.tau / 4)
            ox = int(math.cos(ang) * (r + 6))
            oy = int(math.sin(ang) * (r + 3))
            sp_a = max(60, int(160 + 80 * math.cos(ang * 2)))
            sp = pygame.Surface((6, 6), pygame.SRCALPHA)
            pygame.draw.circle(sp, (155, 210, 255, sp_a), (3, 3), 3)
            surf.blit(sp, (cx + ox - 3, cy + oy - 3))

        # Horseshoe U — chrome body with classic RED/BLUE pole tips
        body_rect = pygame.Rect(cx - r, cy - r + 2, r * 2, r * 2)

        # Dark shadow behind U
        pygame.draw.arc(surf, (10, 10, 25), body_rect.inflate(6, 6),
                        math.pi, 2 * math.pi, r + 2)
        # Chrome outer ring
        pygame.draw.arc(surf, (140, 148, 165), body_rect.inflate(2, 2),
                        math.pi, 2 * math.pi, r)
        # Bright chrome fill
        pygame.draw.arc(surf, (210, 218, 235), body_rect,
                        math.pi, 2 * math.pi, r - 2)
        # Specular highlight stripe
        inner = body_rect.inflate(-6, -6)
        pygame.draw.arc(surf, (245, 248, 255), inner,
                        math.pi * 1.1, math.pi * 1.9, 2)

        # Legs — chrome rectangles with shadow outline
        leg_y = cy + 2
        leg_h = 11
        for lx in (cx - r, cx + r - 7):
            pygame.draw.rect(surf, (20, 20, 40), (lx - 1, leg_y - 1, 9, leg_h + 2))
            pygame.draw.rect(surf, (210, 218, 235), (lx, leg_y, 7, leg_h))
            pygame.draw.rect(surf, (245, 248, 255), (lx + 1, leg_y + 1, 2, leg_h - 3))

        # Classic magnet pole tips: RED left, BLUE right
        tip_h = 5
        pygame.draw.rect(surf, (220, 22, 22), (cx - r, leg_y + leg_h - tip_h, 7, tip_h))
        pygame.draw.rect(surf, (255, 85, 85), (cx - r + 1, leg_y + leg_h - tip_h + 1, 5, 1))
        pygame.draw.rect(surf, (22, 55, 220), (cx + r - 7, leg_y + leg_h - tip_h, 7, tip_h))
        pygame.draw.rect(surf, (85, 140, 255), (cx + r - 6, leg_y + leg_h - tip_h + 1, 5, 1))

        # Electric arc between tips — animated zigzag
        tip_lx = cx - r + 3
        tip_rx = cx + r - 4
        tip_y  = leg_y + leg_h - 1
        arc_pts = [
            (tip_lx, tip_y),
            (tip_lx + (tip_rx - tip_lx) // 3,
             tip_y - int(5 * math.sin(self.pulse * 9.0))),
            ((tip_lx + tip_rx) // 2,
             tip_y + int(5 * math.sin(self.pulse * 9.0 + 1.0))),
            (tip_lx + 2 * (tip_rx - tip_lx) // 3,
             tip_y - int(5 * math.sin(self.pulse * 9.0 + 2.0))),
            (tip_rx, tip_y),
        ]
        pygame.draw.lines(surf, (60, 130, 255), False, arc_pts, 2)
        pygame.draw.lines(surf, (200, 230, 255), False, arc_pts, 1)

        # Spark blips at tip ends
        for tx, ty in ((tip_lx, tip_y), (tip_rx, tip_y)):
            blip = pygame.Surface((8, 8), pygame.SRCALPHA)
            ba = max(80, min(255, int(130 + 100 * math.sin(self.pulse * 9))))
            pygame.draw.circle(blip, (180, 215, 255, ba), (4, 4), 4)
            surf.blit(blip, (tx - 4, ty - 4))

    def _draw_slowmo(self, surf):
        cx = int(self.x)
        cy = int(self.y + math.sin(self.pulse * 0.8) * 2.0)
        r = MUSHROOM_R

        # Bottom drop shadow
        sh_w = r * 3
        sh = pygame.Surface((sh_w, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(sh, (0, 0, 0, 80), sh.get_rect())
        surf.blit(sh, (cx - sh_w // 2, cy + r + 4))

        # Thin expanding ring pulse — stroke only, not a filled blob
        ring_frac = self.pulse % 1.0
        ring_r = int(r + 3 + 7 * ring_frac)
        ring_a = int(65 * (1.0 - ring_frac))
        ring = pygame.Surface((ring_r * 2 + 4, ring_r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(ring, (170, 90, 255, ring_a),
                           (ring_r + 2, ring_r + 2), ring_r, 2)
        surf.blit(ring, (cx - ring_r - 2, cy - ring_r - 2))

        # Hourglass triangles with shadow offset
        hw = r - 1
        hh = r - 1
        top_tri = [(cx - hw, cy - hh), (cx + hw, cy - hh), (cx, cy)]
        bot_tri = [(cx - hw, cy + hh), (cx + hw, cy + hh), (cx, cy)]

        for tri in (top_tri, bot_tri):
            pygame.draw.polygon(surf, (30, 8, 55), [(p[0]+1, p[1]+1) for p in tri])
        pygame.draw.polygon(surf, (105, 42, 175), top_tri)
        pygame.draw.polygon(surf, (105, 42, 175), bot_tri)

        # Lighter highlight on top face, darker on bottom
        hi_top = [(cx - hw + 4, cy - hh + 2), (cx + hw - 6, cy - hh + 2), (cx - 1, cy - 3)]
        pygame.draw.polygon(surf, (155, 82, 238), hi_top)

        # Crisp outline edges
        pygame.draw.lines(surf, (55, 15, 95), True, top_tri, 1)
        pygame.draw.lines(surf, (55, 15, 95), True, bot_tri, 1)

        # Animated sand dots falling from pinch toward bottom bulge
        sand_phase = (self.pulse * 2.5) % 1.0
        for i in range(4):
            frac = (sand_phase + i * 0.25) % 1.0
            dot_y = int(cy + 2 + frac * (hh - 5))
            dot_a = int(210 * math.sin(frac * math.pi))
            d = pygame.Surface((4, 4), pygame.SRCALPHA)
            pygame.draw.circle(d, (255, 240, 150, dot_a), (2, 2), 2)
            surf.blit(d, (cx - 2, dot_y - 2))

        # Wooden end caps
        cap_w = hw * 2 + 4
        pygame.draw.rect(surf, (80, 40, 15),
                         (cx - hw - 2, cy - hh - 4, cap_w, 6))
        pygame.draw.rect(surf, (150, 88, 42),
                         (cx - hw - 1, cy - hh - 3, cap_w - 2, 3))
        pygame.draw.rect(surf, (80, 40, 15),
                         (cx - hw - 2, cy + hh - 2, cap_w, 6))
        pygame.draw.rect(surf, (150, 88, 42),
                         (cx - hw - 1, cy + hh - 1, cap_w - 2, 3))

        # Clock face on lower glass — small circle with rotating hands
        fc_r = max(4, r // 3)
        fc_x, fc_y = cx, cy + hh // 2
        pygame.draw.circle(surf, (22, 8, 48), (fc_x, fc_y), fc_r)
        pygame.draw.circle(surf, (85, 45, 148), (fc_x, fc_y), fc_r, 1)
        h_ang = self.pulse * 0.4 - math.pi / 2
        m_ang = self.pulse * 2.0 - math.pi / 2
        hl = max(2, fc_r - 2)
        ml = max(3, fc_r - 1)
        pygame.draw.line(surf, (195, 158, 255),
                         (fc_x, fc_y),
                         (fc_x + int(math.cos(h_ang) * hl),
                          fc_y + int(math.sin(h_ang) * hl)), 2)
        pygame.draw.line(surf, (230, 215, 255),
                         (fc_x, fc_y),
                         (fc_x + int(math.cos(m_ang) * ml),
                          fc_y + int(math.sin(m_ang) * ml)), 1)
        pygame.draw.circle(surf, WHITE, (fc_x, fc_y), 2)


# Back-compat alias — some callers (e.g. snapshot/playtest scripts) still say Mushroom.
Mushroom = PowerUp


# ── Particle ─────────────────────────────────────────────────────────────────

class Particle:
    __slots__ = ("x", "y", "vx", "vy", "life", "life_max", "r", "color", "gravity")

    def __init__(self, x, y, vx, vy, life, r, color, gravity=900.0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = life
        self.life_max = life
        self.r = r
        self.color = color
        self.gravity = gravity

    def update(self, dt):
        self.vy += self.gravity * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt

    def alive(self):
        return self.life > 0

    def draw(self, surf):
        t = max(0.0, self.life / self.life_max)
        a = int(255 * t)
        rr = max(1, int(self.r * (0.4 + 0.6 * t)))
        s = pygame.Surface((rr * 2 + 2, rr * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, a), (rr + 1, rr + 1), rr)
        surf.blit(s, (int(self.x - rr - 1), int(self.y - rr - 1)), special_flags=pygame.BLEND_ADD)


# ── FloatText ────────────────────────────────────────────────────────────────

_float_font_cache: dict = {}

import os as _os

_FLOAT_FONT_DIR = _os.path.join(_os.path.dirname(__file__), "assets")
_FLOAT_BOLD = _os.path.join(_FLOAT_FONT_DIR, "LiberationSans-Bold.ttf")
_FLOAT_REG  = _os.path.join(_FLOAT_FONT_DIR, "LiberationSans-Regular.ttf")


def _get_float_font(size, bold=True):
    key = (size, bold)
    f = _float_font_cache.get(key)
    if f is None:
        path = _FLOAT_BOLD if bold else _FLOAT_REG
        f = pygame.font.Font(path, size)
        _float_font_cache[key] = f
    return f


class FloatText:
    __slots__ = ("text", "x", "y", "vy", "life", "life_max", "color", "size")

    def __init__(self, text, x, y, color, size=22, life=1.0, vy=-60):
        self.text = text
        self.x = x
        self.y = y
        self.vy = vy
        self.life = life
        self.life_max = life
        self.color = color
        self.size = size

    def update(self, dt):
        self.y += self.vy * dt
        self.vy += 40.0 * dt
        self.life -= dt

    def alive(self):
        return self.life > 0

    def draw(self, surf):
        t = max(0.0, self.life / self.life_max)
        a = int(255 * min(1.0, t * 2))
        font = _get_float_font(self.size)
        shadow = font.render(self.text, True, NEAR_BLACK)
        text = font.render(self.text, True, self.color)
        shadow.set_alpha(a)
        text.set_alpha(a)
        r = text.get_rect(center=(int(self.x), int(self.y)))
        surf.blit(shadow, (r.x + 2, r.y + 2))
        surf.blit(text, r.topleft)
