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
    COIN_GOLD, COIN_DARK,
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

    def flap(self, gravity_sign=1):
        if self.alive:
            self.vy = FLAP_V * gravity_sign
            self.flap_boost = 0.45

    def update(self, dt, gravity_sign=1):
        new_vy = self.vy + GRAVITY * gravity_sign * dt
        if gravity_sign >= 0:
            self.vy = min(new_vy, MAX_FALL)
        else:
            self.vy = max(new_vy, -MAX_FALL)
        self.y += self.vy * dt

        base_hz = 9.0 + self.flap_boost * 20.0
        if self.vy < -100:
            base_hz += 3.0
        elif self.vy > 200:
            base_hz = max(3.0, base_hz - 4.0)
        self.frame_t = (self.frame_t + dt * base_hz)
        self.flap_boost = max(0.0, self.flap_boost - dt * 1.8)

    def draw(self, surf, shake_x=0, shake_y=0, flipped=False):
        frame_idx = int(self.frame_t) % len(parrot.FRAMES)
        # When flipped (reverse-gravity buff), negate the tilt so a rising
        # bird's head still leads in the direction of motion after the
        # vertical mirror.
        tilt = -self.tilt_deg if flipped else self.tilt_deg
        img = parrot.get_parrot(frame_idx, tilt)
        if flipped:
            img = pygame.transform.flip(img, False, True)
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
        cy = int(self.y + math.sin(self.float_t * 2.2) * 2)
        cos_s = math.cos(self.spin)
        r = COIN_R
        rx = max(1, int(abs(cos_s) * r))

        if abs(cos_s) <= 0.35:
            # Edge-on sliver — a thin gold bar with dark rim, no detail.
            pygame.draw.ellipse(surf, COIN_DARK,
                                (cx - rx - 1, cy - r, (rx + 1) * 2, r * 2))
            pygame.draw.ellipse(surf, COIN_GOLD,
                                (cx - rx, cy - r, rx * 2, r * 2))
            return

        # Face-on: dark rim → gold body. Both are ellipses that share the
        # same horizontal squeeze, so the coin shape IS its silhouette.
        pygame.draw.ellipse(surf, COIN_DARK,
                            (cx - rx - 1, cy - r - 1,
                             (rx + 1) * 2, (r + 1) * 2))
        pygame.draw.ellipse(surf, COIN_GOLD,
                            (cx - rx, cy - r, rx * 2, r * 2))

        # Embossed parrot silhouette — only when mostly face-on so it
        # doesn't smear across a squeezed ellipse.
        if abs(cos_s) > 0.75:
            emboss = (140, 85, 0)
            pygame.draw.ellipse(surf, emboss, (cx - 2, cy - 1, 7, 5))     # body
            pygame.draw.circle(surf, emboss, (cx - 1, cy - 3), 3)         # head
            pygame.draw.polygon(surf, emboss,                              # hooked beak
                                [(cx - 3, cy - 3), (cx - 6, cy - 2), (cx - 3, cy - 1)])
            pygame.draw.circle(surf, COIN_GOLD, (cx, cy - 4), 1)          # eye


# ── PowerUp ──────────────────────────────────────────────────────────────────

# Lazy-initialized high-resolution cache for the "reverse" power-up icon —
# two purple arrows (up on the left, down on the right) on a fully transparent
# background. Rendered once at 4x super-sampling and smoothscaled down so the
# arrow edges read clean at any size. Reused for both the in-world pickup and
# the HUD active-buff badge.
_REVERSE_ICON_CACHE: "dict[int, pygame.Surface]" = {}


def _build_reverse_icon(out_diameter: int) -> pygame.Surface:
    """Premium icon: a rounded purple frame around a light-gray panel with
    two clean purple monoline chevrons (up + down). Built at 4x super-
    sampling and smoothscaled down for crisp edges on any background."""
    SS = 4
    size = out_diameter * SS
    surf = pygame.Surface((size, size), pygame.SRCALPHA)

    # ── Palette ─────────────────────────────────────────────────────────
    OUTLINE      = (15, 5, 35)         # outer hairline, definition on any bg
    FRAME        = (140, 60, 215)      # the purple perimeter
    FRAME_HL     = (215, 165, 250)     # tiny top-edge highlight
    PANEL_HI     = (245, 246, 250)     # gray panel — lit top
    PANEL_LO     = (212, 214, 224)     # gray panel — slightly shaded bottom
    INSET_SHADOW = (0, 0, 0, 38)       # soft inner shadow under the frame
    ARROW        = (118, 52, 200)      # purple arrow body
    ARROW_DK     = (62, 22, 130)       # arrow shadow / outline mix

    radius   = SS * 11                # squircle-style corners
    inset    = SS                     # 1-px outer outline gap
    frame_t  = SS * 2                 # frame stroke = 2 final-px (clean & thin)

    panel = pygame.Rect(inset, inset, size - inset * 2, size - inset * 2)

    # 1) Outer 1-px dark outline so the icon reads on any background.
    pygame.draw.rect(surf, OUTLINE, panel, border_radius=radius)

    # 2) Solid purple frame fill (will be partly covered by gray panel).
    pygame.draw.rect(surf, FRAME, panel.inflate(-SS * 2, -SS * 2),
                     border_radius=radius - SS)

    # 3) Light-gray inner panel with a subtle vertical gradient.
    inner = panel.inflate(-(frame_t + SS) * 2, -(frame_t + SS) * 2)
    inner_radius = max(2, radius - frame_t - SS)
    grad_surf = pygame.Surface((size, size), pygame.SRCALPHA)
    g0, g1 = inner.top, inner.bottom
    for y in range(g0, g1 + 1):
        t = (y - g0) / max(1, (g1 - g0))
        col = (
            int(PANEL_HI[0] + (PANEL_LO[0] - PANEL_HI[0]) * t),
            int(PANEL_HI[1] + (PANEL_LO[1] - PANEL_HI[1]) * t),
            int(PANEL_HI[2] + (PANEL_LO[2] - PANEL_HI[2]) * t),
        )
        pygame.draw.line(grad_surf, col, (0, y), (size, y))
    inner_mask = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.rect(inner_mask, (255, 255, 255, 255), inner,
                     border_radius=inner_radius)
    grad_surf.blit(inner_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(grad_surf, (0, 0))

    # 4) Soft inner shadow inside the gray panel — gives the gray a
    #    recessed feel under the frame.
    shadow_surf = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.rect(shadow_surf, INSET_SHADOW, inner,
                     border_radius=inner_radius, width=SS)
    surf.blit(shadow_surf, (0, 0))

    # 5) Tiny lighter highlight along the very top edge of the frame —
    #    sells the "lit from above" depth.
    pygame.draw.line(surf, FRAME_HL,
                     (panel.left + radius, panel.top + SS),
                     (panel.right - radius, panel.top + SS),
                     max(1, SS // 2))

    # ── Arrows: clean purple monoline chevrons ─────────────────────────
    pad_x = max(SS * 5, panel.width // 6)
    pad_y = max(SS * 5, panel.height // 6)
    arrow_area = panel.inflate(-pad_x * 2, -pad_y * 2)

    col_w = arrow_area.width // 2
    lx = arrow_area.left + col_w // 2
    rx = arrow_area.right - col_w // 2
    # Bolder, thicker strokes for a chunkier "icon-set" feel.
    stroke = max(SS * 4, arrow_area.height // 8)
    head_w = max(SS * 5, arrow_area.width // 5)
    head_h = max(SS * 5, arrow_area.height * 30 // 100)

    def _arrow(target, col_x, *, point_up, color, stroke_w):
        if point_up:
            tip  = (col_x, arrow_area.top)
            tail = (col_x, arrow_area.bottom)
            wing_y = arrow_area.top + head_h
        else:
            tip  = (col_x, arrow_area.bottom)
            tail = (col_x, arrow_area.top)
            wing_y = arrow_area.bottom - head_h
        wl = (col_x - head_w, wing_y)
        wr = (col_x + head_w, wing_y)
        pygame.draw.line(target, color, tail, tip, stroke_w)
        pygame.draw.line(target, color, tip, wl, stroke_w)
        pygame.draw.line(target, color, tip, wr, stroke_w)
        # Round caps so the strokes don't look chopped at small sizes.
        for p in (tail, wl, wr, tip):
            pygame.draw.circle(target, color, p, stroke_w // 2)

    # Single bold purple pass — no outline pass, the gray panel provides
    # plenty of contrast and the arrow stays visually "thick" rather than
    # ringed.
    _arrow(surf, lx, point_up=True,  color=ARROW, stroke_w=stroke)
    _arrow(surf, rx, point_up=False, color=ARROW, stroke_w=stroke)

    return pygame.transform.smoothscale(surf, (out_diameter, out_diameter))


def _get_reverse_icon(diameter: int = (MUSHROOM_R + 12) * 2) -> pygame.Surface:
    cached = _REVERSE_ICON_CACHE.get(diameter)
    if cached is None:
        cached = _build_reverse_icon(diameter)
        _REVERSE_ICON_CACHE[diameter] = cached
    return cached


class PowerUp:
    """A collectible buff. `kind` selects visuals and pickup effect:
       triple  — red mushroom, 3x coin value for TRIPLE_DURATION
       magnet  — red horseshoe, pulls coins in for MAGNET_DURATION
       slowmo  — purple hourglass, 0.5x world scroll for SLOWMO_DURATION
       reverse — cyan double-arrow, flips Pip's gravity for REVERSE_DURATION
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
        elif self.kind == "reverse":
            self._draw_reverse(surf)

    # ── sprite variants ─────────────────────────────────────────────────────
    def _draw_mushroom(self, surf):
        cx = int(self.x)
        cy = int(self.y)

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
        # Specular sheen
        sh2 = pygame.Surface((cap_rect.width - 14, 3), pygame.SRCALPHA)
        pygame.draw.ellipse(sh2, (255, 230, 220, 200), sh2.get_rect())
        surf.blit(sh2, (cap_rect.x + 7, cap_rect.y + 3))

        # Spots with a soft ring so they read clearly
        for sx, sy, sr in ((cx - 7, cy - 5, 3),
                           (cx + 6, cy - 7, 4),
                           (cx + 2, cy + 1, 3),
                           (cx - 3, cy + 2, 2)):
            pygame.draw.circle(surf, (220, 190, 200), (sx, sy), sr + 1)
            pygame.draw.circle(surf, MUSH_SPOT,       (sx, sy), sr)

    def _draw_magnet(self, surf):
        cx = int(self.x)
        cy = int(self.y)
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

    def _draw_slowmo(self, surf):
        cx = int(self.x)
        cy = int(self.y)
        # Purple aura
        aura = pygame.Surface((MUSHROOM_R * 3, MUSHROOM_R * 3), pygame.SRCALPHA)
        pygame.draw.circle(aura, (180, 100, 255, 70),
                           (aura.get_width() // 2, aura.get_height() // 2),
                           MUSHROOM_R + 4)
        surf.blit(aura, (cx - aura.get_width() // 2, cy - aura.get_height() // 2),
                  special_flags=pygame.BLEND_ADD)
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
        # Sand — light falling stream in the middle
        pygame.draw.line(surf, (255, 230, 150), (cx, cy - MUSHROOM_R + 4), (cx, cy - 1), 2)
        pygame.draw.line(surf, (255, 230, 150), (cx, cy + 1), (cx, cy + MUSHROOM_R - 4), 2)
        # Wooden end caps
        pygame.draw.rect(surf, (120, 60, 30), (cx - MUSHROOM_R, cy - MUSHROOM_R - 2,
                                                MUSHROOM_R * 2, 4))
        pygame.draw.rect(surf, (120, 60, 30), (cx - MUSHROOM_R, cy + MUSHROOM_R - 2,
                                                MUSHROOM_R * 2, 4))
        pygame.draw.rect(surf, (180, 110, 60), (cx - MUSHROOM_R + 1,
                                                 cy - MUSHROOM_R - 1,
                                                 MUSHROOM_R * 2 - 2, 2))

    def _draw_reverse(self, surf):
        cx = int(self.x)
        cy = int(self.y)
        # Breathing scale gives the pickup life without any background.
        breath = 0.5 + 0.5 * math.sin(self.pulse)
        scale = 1.0 + 0.06 * breath
        icon = _get_reverse_icon()
        if scale != 1.0:
            iw, ih = icon.get_size()
            icon = pygame.transform.smoothscale(
                icon, (int(iw * scale), int(ih * scale)))
        surf.blit(icon, (cx - icon.get_width() // 2,
                         cy - icon.get_height() // 2))


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
