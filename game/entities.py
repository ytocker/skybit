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

        # Drop shadow beneath the coin
        sh = pygame.Surface((rx * 2 + 8, 7), pygame.SRCALPHA)
        pygame.draw.ellipse(sh, (0, 0, 0, 70), sh.get_rect())
        surf.blit(sh, (cx - rx - 4, cy + r))

        # Additive gold glow halo — pulses with float phase
        glow_a = int(55 + 20 * math.sin(self.float_t * 2.2))
        blit_glow(surf, cx, cy, r + 7, COIN_GOLD, glow_a)

        if abs(cos_s) <= 0.35:
            # Edge-on sliver — thin gold bar, still glows
            pygame.draw.ellipse(surf, COIN_DARK,
                                (cx - rx - 1, cy - r, (rx + 1) * 2, r * 2))
            pygame.draw.ellipse(surf, COIN_GOLD,
                                (cx - rx, cy - r, rx * 2, r * 2))
            return

        # Dark rim → rich gold body
        pygame.draw.ellipse(surf, COIN_DARK,
                            (cx - rx - 1, cy - r - 1, (rx + 1) * 2, (r + 1) * 2))
        pygame.draw.ellipse(surf, COIN_GOLD,
                            (cx - rx, cy - r, rx * 2, r * 2))

        # Bright inner zone for 3-D depth
        if rx > 5:
            ir = max(2, rx - 4)
            pygame.draw.ellipse(surf, COIN_LIGHT,
                                (cx - ir, cy - r + 3, ir * 2, r * 2 - 6))

        # Specular crescent — upper-left highlight, sweeps with spin phase
        if abs(cos_s) > 0.45 and rx > 4:
            spec_w = max(2, int(rx * 0.55))
            spec_h = max(2, r // 3)
            spec = pygame.Surface((spec_w * 2, spec_h * 2), pygame.SRCALPHA)
            spec_a = int(160 + 80 * abs(cos_s))
            pygame.draw.ellipse(spec, (255, 255, 220, spec_a), spec.get_rect())
            surf.blit(spec, (cx - spec_w // 2 - rx // 3, cy - r + 2))

        # Embossed parrot silhouette — only when mostly face-on
        if abs(cos_s) > 0.75:
            emboss = (140, 85, 0)
            pygame.draw.ellipse(surf, emboss, (cx - 2, cy - 1, 7, 5))
            pygame.draw.circle(surf, emboss, (cx - 1, cy - 3), 3)
            pygame.draw.polygon(surf, emboss,
                                [(cx - 3, cy - 3), (cx - 6, cy - 2), (cx - 3, cy - 1)])
            pygame.draw.circle(surf, COIN_GOLD, (cx, cy - 4), 1)


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

        # Pulsing red glow halo
        glow_a = int(55 + 25 * math.sin(self.pulse))
        blit_glow(surf, cx, cy - MUSHROOM_R // 2, MUSHROOM_R + 9, (220, 30, 40), glow_a)

        # 3 orbiting sparkle dots
        for i in range(3):
            ang = self.pulse * 1.4 + i * (math.tau / 3)
            ox = int(math.cos(ang) * (MUSHROOM_R + 7))
            oy = int(math.sin(ang) * (MUSHROOM_R + 4))
            sp_a = max(60, int(180 + 70 * math.sin(ang * 2)))
            sp = pygame.Surface((6, 6), pygame.SRCALPHA)
            pygame.draw.circle(sp, (255, 210, 210, sp_a), (3, 3), 3)
            surf.blit(sp, (cx + ox - 3, cy + oy - 3))

        # Stem with vivid highlight
        stem = pygame.Rect(cx - 7, cy, 14, 13)
        rounded_rect(surf, stem, 5, MUSH_STEM, 255)
        pygame.draw.line(surf, (255, 255, 230), (cx - 4, cy + 2), (cx - 4, cy + 11), 2)
        pygame.draw.line(surf, (200, 180, 145), (cx + 3, cy + 2), (cx + 3, cy + 11), 1)
        # Stem base shadow
        sh = pygame.Surface((16, 4), pygame.SRCALPHA)
        pygame.draw.ellipse(sh, (0, 0, 0, 120), sh.get_rect())
        surf.blit(sh, (cx - 8, cy + 11))

        # Cap shadow (under)
        cap_rect = pygame.Rect(cx - MUSHROOM_R - 1, cy - MUSHROOM_R + 2, (MUSHROOM_R + 1) * 2, MUSHROOM_R + 5)
        sh = pygame.Surface((cap_rect.width + 8, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(sh, (0, 0, 0, 130), sh.get_rect())
        surf.blit(sh, (cap_rect.x - 4, cy - 2))

        # Cap base (deep crimson outline) then vivid red
        pygame.draw.ellipse(surf, (130, 10, 20), cap_rect.inflate(2, 2))
        pygame.draw.ellipse(surf, MUSH_CAP,     cap_rect)
        # Upper highlight arc (hot pink / orange)
        hi = pygame.Rect(cap_rect.x + 3, cap_rect.y + 2, cap_rect.width - 6, 7)
        pygame.draw.ellipse(surf, MUSH_CAP2, hi)
        # Specular sheen (sweeps left-right with pulse)
        sheen_x_off = int(math.sin(self.pulse * 1.3) * 4)
        sh2 = pygame.Surface((cap_rect.width - 14, 4), pygame.SRCALPHA)
        sh2_a = int(180 + 70 * math.sin(self.pulse * 1.3))
        pygame.draw.ellipse(sh2, (255, 235, 225, sh2_a), sh2.get_rect())
        surf.blit(sh2, (cap_rect.x + 7 + sheen_x_off, cap_rect.y + 3))

        # Spots with a soft ring so they read clearly
        for sx, sy, sr in ((cx - 7, cy - 5, 3),
                           (cx + 6, cy - 7, 4),
                           (cx + 2, cy + 1, 3),
                           (cx - 3, cy + 2, 2)):
            pygame.draw.circle(surf, (220, 190, 200), (sx, sy), sr + 1)
            pygame.draw.circle(surf, MUSH_SPOT,       (sx, sy), sr)

    def _draw_magnet(self, surf):
        cx = int(self.x)
        cy = int(self.y + math.sin(self.pulse * 1.1) * 2.0)

        # Pulsing electric-blue glow
        glow_a = int(60 + 28 * math.sin(self.pulse))
        blit_glow(surf, cx, cy, MUSHROOM_R + 8, (80, 160, 255), glow_a)

        # 4 orbiting charged-particle dots (counter-clockwise)
        for i in range(4):
            ang = -self.pulse * 1.6 + i * (math.tau / 4)
            ox = int(math.cos(ang) * (MUSHROOM_R + 6))
            oy = int(math.sin(ang) * (MUSHROOM_R + 3))
            sp_a = max(80, int(180 + 70 * math.cos(ang * 2)))
            sp = pygame.Surface((5, 5), pygame.SRCALPHA)
            pygame.draw.circle(sp, (180, 220, 255, sp_a), (2, 2), 2)
            surf.blit(sp, (cx + ox - 2, cy + oy - 2))

        # Backing shadow
        sh = pygame.Surface((MUSHROOM_R * 3, 10), pygame.SRCALPHA)
        pygame.draw.ellipse(sh, (0, 0, 0, 130), sh.get_rect())
        surf.blit(sh, (cx - sh.get_width() // 2, cy + MUSHROOM_R - 2))
        # Horseshoe U — draw an outer red arc, inner cutout, then two silver tips
        # Outer red body: two overlapping thick arcs forming a U.
        body_rect = pygame.Rect(cx - MUSHROOM_R, cy - MUSHROOM_R + 2,
                                MUSHROOM_R * 2, MUSHROOM_R * 2)
        # Red outer
        pygame.draw.arc(surf, (160, 10, 20), body_rect.inflate(2, 2),
                        math.pi, 2 * math.pi, MUSHROOM_R)
        pygame.draw.arc(surf, (220, 30, 40), body_rect,
                        math.pi, 2 * math.pi, MUSHROOM_R - 2)
        # Inner white stripe
        inner = body_rect.inflate(-10, -10)
        pygame.draw.arc(surf, WHITE, inner,
                        math.pi, 2 * math.pi, 3)
        # Close off the two legs with short red rectangles so it reads as a U
        leg_y = cy + 2
        pygame.draw.rect(surf, (220, 30, 40), (cx - MUSHROOM_R + 1, leg_y, 5, 10))
        pygame.draw.rect(surf, (220, 30, 40), (cx + MUSHROOM_R - 6, leg_y, 5, 10))
        # Silver tips on each leg end
        pygame.draw.rect(surf, (220, 220, 235), (cx - MUSHROOM_R + 1, leg_y + 6, 5, 5))
        pygame.draw.rect(surf, (220, 220, 235), (cx + MUSHROOM_R - 6, leg_y + 6, 5, 5))
        # Dark rim on silver tips
        pygame.draw.rect(surf, (80, 80, 100), (cx - MUSHROOM_R + 1, leg_y + 6, 5, 5), 1)
        pygame.draw.rect(surf, (80, 80, 100), (cx + MUSHROOM_R - 6, leg_y + 6, 5, 5), 1)

        # Electric arc between the two tips — animated zigzag
        tip_lx = cx - MUSHROOM_R + 3
        tip_rx = cx + MUSHROOM_R - 3
        tip_y  = leg_y + 8
        mid_x  = (tip_lx + tip_rx) // 2
        arc_pts = [
            (tip_lx, tip_y),
            (tip_lx + (tip_rx - tip_lx) // 3,
             tip_y - int(5 * math.sin(self.pulse * 9.0 + 0.0))),
            (mid_x,
             tip_y + int(5 * math.sin(self.pulse * 9.0 + 1.0))),
            (tip_lx + 2 * (tip_rx - tip_lx) // 3,
             tip_y - int(5 * math.sin(self.pulse * 9.0 + 2.0))),
            (tip_rx, tip_y),
        ]
        pygame.draw.lines(surf, (100, 180, 255), False, arc_pts, 2)
        pygame.draw.lines(surf, (220, 240, 255), False, arc_pts, 1)
        # Tip glow blips
        for tx, ty in ((tip_lx, tip_y), (tip_rx, tip_y)):
            blip = pygame.Surface((8, 8), pygame.SRCALPHA)
            pygame.draw.circle(blip, (200, 230, 255, 180), (4, 4), 4)
            surf.blit(blip, (tx - 4, ty - 4), special_flags=pygame.BLEND_ADD)

    def _draw_slowmo(self, surf):
        cx = int(self.x)
        cy = int(self.y + math.sin(self.pulse * 0.8) * 2.0)

        # Pulsing deep-purple glow
        glow_a = int(70 + 35 * math.sin(self.pulse))
        blit_glow(surf, cx, cy, MUSHROOM_R + 10, (150, 70, 255), glow_a)

        # Expanding ring pulse — a faint second ring at larger radius
        ring_r = int(MUSHROOM_R + 6 + 8 * (self.pulse % 1.0))
        ring_a = int(90 * (1.0 - (self.pulse % 1.0)))
        ring = pygame.Surface((ring_r * 2 + 4, ring_r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(ring, (180, 100, 255, ring_a),
                           (ring_r + 2, ring_r + 2), ring_r, 2)
        surf.blit(ring, (cx - ring_r - 2, cy - ring_r - 2))

        # Hourglass body: two triangles joined at a pinch
        top = [(cx - MUSHROOM_R + 2, cy - MUSHROOM_R + 1),
               (cx + MUSHROOM_R - 2, cy - MUSHROOM_R + 1),
               (cx, cy)]
        bot = [(cx - MUSHROOM_R + 2, cy + MUSHROOM_R - 1),
               (cx + MUSHROOM_R - 2, cy + MUSHROOM_R - 1),
               (cx, cy)]
        pygame.draw.polygon(surf, (60, 20, 90), [(p[0] - 1, p[1] - 1) for p in top] + [top[2]])
        pygame.draw.polygon(surf, (140, 70, 210), top)
        pygame.draw.polygon(surf, (60, 20, 90), [(p[0] - 1, p[1] + 1) for p in bot] + [bot[2]])
        pygame.draw.polygon(surf, (140, 70, 210), bot)

        # Inner highlights on hourglass faces
        hi_top = [(cx - MUSHROOM_R + 5, cy - MUSHROOM_R + 3),
                  (cx + MUSHROOM_R - 7, cy - MUSHROOM_R + 3),
                  (cx - 1, cy - 3)]
        pygame.draw.polygon(surf, (180, 110, 255), hi_top)

        # Sand stream — falling dots that animate with pulse
        for dot_y in range(cy - MUSHROOM_R + 5, cy - 1, 4):
            dot_a = int(200 * (1.0 - abs(dot_y - cy) / MUSHROOM_R))
            d = pygame.Surface((3, 3), pygame.SRCALPHA)
            pygame.draw.circle(d, (255, 235, 160, dot_a), (1, 1), 1)
            offset = int(2 * math.sin(self.pulse * 6 + dot_y))
            surf.blit(d, (cx + offset - 1, dot_y))

        # Sparkle at the pinch point
        pinch_a = int(180 + 70 * math.sin(self.pulse * 8))
        p_sp = pygame.Surface((6, 6), pygame.SRCALPHA)
        pygame.draw.circle(p_sp, (255, 255, 200, pinch_a), (3, 3), 3)
        surf.blit(p_sp, (cx - 3, cy - 3), special_flags=pygame.BLEND_ADD)

        # Wooden end caps
        pygame.draw.rect(surf, (120, 60, 30),
                         (cx - MUSHROOM_R, cy - MUSHROOM_R - 2, MUSHROOM_R * 2, 4))
        pygame.draw.rect(surf, (120, 60, 30),
                         (cx - MUSHROOM_R, cy + MUSHROOM_R - 2, MUSHROOM_R * 2, 4))
        pygame.draw.rect(surf, (180, 110, 60),
                         (cx - MUSHROOM_R + 1, cy - MUSHROOM_R - 1, MUSHROOM_R * 2 - 2, 2))

        # Rotating clock hands on the lower glass face
        hand_cx, hand_cy = cx, cy + MUSHROOM_R // 2
        h_ang = self.pulse * 0.5 - math.pi / 2
        m_ang = self.pulse * 2.2 - math.pi / 2
        h_len, m_len = 4, 6
        pygame.draw.line(surf, (210, 180, 255),
                         (hand_cx, hand_cy),
                         (hand_cx + int(math.cos(h_ang) * h_len),
                          hand_cy + int(math.sin(h_ang) * h_len)), 2)
        pygame.draw.line(surf, (240, 220, 255),
                         (hand_cx, hand_cy),
                         (hand_cx + int(math.cos(m_ang) * m_len),
                          hand_cy + int(math.sin(m_ang) * m_len)), 1)
        pygame.draw.circle(surf, WHITE, (hand_cx, hand_cy), 2)


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
