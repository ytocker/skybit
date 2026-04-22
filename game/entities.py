"""
Game entities: Bird, Pipe, Coin, Mushroom, Particle, FloatText.
All drawing is smooth (gradients, alpha, glows) — no pixel art.

Pipes are Zhangjiajie-style sandstone pillars topped with living vegetation,
re-tinted by the active biome palette. Coins are slow-rotating metallic gold
discs with embossed detail.
"""
import math
import random
import pygame

from game.config import (
    W, H, GRAVITY, FLAP_V, MAX_FALL,
    BIRD_X, BIRD_R, PIPE_W, COIN_R, MUSHROOM_R, GROUND_Y,
)
from game.draw import (
    blit_glow, get_stone_pillar_body,
    silhouette_blit, silhouette_top_spire, silhouette_bottom_spire,
    draw_wuling_pine, draw_moss_strand, draw_side_shrub, draw_pillar_mist,
    rounded_rect, lerp_color,
    COIN_GOLD, COIN_LIGHT, COIN_DARK,
    MUSH_CAP, MUSH_CAP2, MUSH_SPOT, MUSH_STEM,
    PARTICLE_GOLD, PARTICLE_ORNG, PARTICLE_WHT, PARTICLE_CRIM,
    WHITE, NEAR_BLACK,
)
from game import parrot


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
        self.trail: list[tuple[float, float]] = []

    @property
    def tilt_deg(self):
        t = max(-0.5, min(1.1, self.vy / 500.0))
        return -t * 55.0

    def flap(self):
        if self.alive:
            self.vy = FLAP_V
            self.flap_boost = 0.45

    def update(self, dt):
        self.vy = min(self.vy + GRAVITY * dt, MAX_FALL)
        self.y += self.vy * dt
        if len(self.trail) == 0 or (self.x - self.trail[-1][0]) ** 2 + (self.y - self.trail[-1][1]) ** 2 > 16:
            self.trail.append((self.x, self.y))
            if len(self.trail) > 8:
                self.trail.pop(0)

        base_hz = 9.0 + self.flap_boost * 20.0
        if self.vy < -100:
            base_hz += 3.0
        elif self.vy > 200:
            base_hz = max(3.0, base_hz - 4.0)
        self.frame_t = (self.frame_t + dt * base_hz)
        self.flap_boost = max(0.0, self.flap_boost - dt * 1.8)

    def draw(self, surf, shake_x=0, shake_y=0):
        for i, (tx, ty) in enumerate(self.trail[:-1]):
            a = int(40 * (i + 1) / len(self.trail))
            if a <= 0:
                continue
            s = pygame.Surface((26, 26), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 90, 90, a), (13, 13), 11)
            surf.blit(s, (tx - 13 + shake_x, ty - 13 + shake_y), special_flags=pygame.BLEND_ADD)

        frame_idx = int(self.frame_t) % len(parrot.FRAMES)
        img = parrot.get_parrot(frame_idx, self.tilt_deg)
        r = img.get_rect(center=(self.x + shake_x, self.y + shake_y))
        surf.blit(img, r.topleft)


# ── Pipe (nature pillar) ─────────────────────────────────────────────────────

class Pipe:
    """Zhangjiajie 'Slender Spire' pillar. Each instance gets a stable
    `seed` so its vegetation arrangement is deterministic across frames."""

    # Vegetation pattern walked along the column body, measured in pixels
    # from the gap-facing tip. Each entry: (offset, side_sign, kind).
    # side_sign: -1 = anchor near sunlit (left) edge, +1 = shadow (right) edge.
    _VEG_PATTERN = (
        (32,   -1, 'pine_med'),
        (62,   +1, 'moss'),
        (92,   -1, 'pine_small'),
        (122,  +1, 'shrub'),
        (152,  -1, 'moss'),
        (185,  +1, 'pine_small'),
        (215,  -1, 'shrub'),
        (248,  +1, 'moss'),
        (282,  -1, 'pine_small'),
        (315,  +1, 'shrub'),
        (348,  -1, 'moss'),
    )

    def __init__(self, x: float, gap_y: float, gap_h: float):
        self.x = x
        self.gap_y = gap_y
        self.gap_h = gap_h
        self.scored = False
        # Per-instance random seed for stable vegetation choices
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

    # ── stone body + silhouette ─────────────────────────────────────────────

    def _paint_stone(self, surf, rect, polygon_fn, palette):
        if rect.height <= 0:
            return
        body = get_stone_pillar_body(
            rect.width, max(1, rect.height),
            palette['stone_light'], palette['stone_mid'],
            palette['stone_dark'],  palette['stone_accent'],
        )
        polygon = polygon_fn(rect.width, rect.height)
        silhouette_blit(surf, body, polygon, rect.topleft, shadow_alpha=110)

    # ── vegetation distributed along the body ───────────────────────────────

    def _veg_anchor(self, side_sign, rect, y, recess=2):
        """Return (x, y) anchored near the left/right edge of the rect at
        height y. side_sign=-1 → sunlit left edge, +1 → shadow right edge."""
        if side_sign < 0:
            return (rect.x + recess, y)
        return (rect.x + rect.width - recess, y)

    def _draw_vegetation_along(self, surf, rect, palette, kind):
        """Walk _VEG_PATTERN from the gap-facing tip downward (bottom pillar)
        or upward (top pillar) and place pines / moss / shrubs."""
        rng = random.Random(self.seed)
        # Tip-relative direction: bottom pillar's tip is at rect.y (top edge),
        # vegetation marches downward (sign +1). Top pillar's tip is at
        # rect.bottom, vegetation marches upward (sign -1).
        if kind == 'bottom':
            tip_y = rect.y
            sign = +1
            grow_dir = 'up'   # pines stand upright
        else:
            tip_y = rect.bottom
            sign = -1
            grow_dir = 'up'   # side pines on the top pillar still stand up
            #                   (they cling to ledges sticking out sideways)

        for offset, side, plant_kind in self._VEG_PATTERN:
            y = tip_y + sign * offset
            # Skip if outside the body or too close to either end
            if not (rect.y + 6 < y < rect.bottom - 6):
                break
            # Tiny rocky ledge under the plant for "growing on the rock" feel
            anchor_x, anchor_y = self._veg_anchor(side, rect, y)
            ledge_w = 12 if plant_kind in ('pine_med', 'shrub') else 9
            ledge_rect = pygame.Rect(anchor_x - (ledge_w if side > 0 else 0),
                                     anchor_y - 2,
                                     ledge_w, 4)
            pygame.draw.ellipse(surf, palette['stone_dark'], ledge_rect.inflate(2, 1))
            pygame.draw.ellipse(surf, palette['stone_light'],
                                ledge_rect.inflate(-2, -1))

            # Variety: bigger wobble + lean jitter so repeating pattern slots
            # don't read as identical copies of each other.
            h_wobble    = rng.randint(-6, 8)
            lean_jitter = rng.randint(-4, 4)
            if plant_kind == 'pine_med':
                draw_wuling_pine(surf, anchor_x, anchor_y - 1,
                                 height=24 + h_wobble, palette=palette,
                                 lean=side * 5 + lean_jitter,
                                 direction=grow_dir, layers=4)
            elif plant_kind == 'pine_small':
                draw_wuling_pine(surf, anchor_x, anchor_y,
                                 height=15 + h_wobble // 2, palette=palette,
                                 lean=side * 3 + lean_jitter,
                                 direction=grow_dir, layers=3)
            elif plant_kind == 'shrub':
                draw_side_shrub(surf, anchor_x, anchor_y - 1, palette,
                                scale=0.85 + rng.random() * 0.45)
            elif plant_kind == 'moss':
                draw_moss_strand(surf, anchor_x, anchor_y,
                                 length=16 + rng.randint(0, 10),
                                 palette=palette, jitter_seed=offset + self.seed)

    # ── orchestration ───────────────────────────────────────────────────────

    def _draw_top_pillar(self, surf, palette):
        rect = self.top_rect
        self._paint_stone(surf, rect, silhouette_top_spire, palette)
        # Hanging pine clinging to the downward fang at the tip
        cx = rect.x + rect.width // 2
        draw_wuling_pine(surf, cx - 4, rect.bottom - 4,
                         height=34, palette=palette,
                         lean=-12, direction='down', layers=4)
        # Vegetation distributed along the body
        self._draw_vegetation_along(surf, rect, palette, kind='top')

    def _draw_bottom_pillar(self, surf, palette):
        rect = self.bot_rect
        self._paint_stone(surf, rect, silhouette_bottom_spire, palette)
        cx = rect.x + rect.width // 2
        # Dramatic Wuling pine on the rocky peak
        draw_wuling_pine(surf, cx + 2, rect.y + 2,
                         height=58, palette=palette,
                         lean=14, direction='up', layers=6)
        # Smaller secondary pine on a ledge just below the peak (left side)
        draw_wuling_pine(surf, rect.x + 6, rect.y + 28,
                         height=26, palette=palette,
                         lean=-5, direction='up', layers=4)
        # Vegetation distributed along the body
        self._draw_vegetation_along(surf, rect, palette, kind='bottom')
        # Mist halo at the base where it meets the ground
        draw_pillar_mist(surf, cx, rect.bottom, rect.width, alpha=110)

    def draw(self, surf, palette=None):
        palette = palette or _DEFAULT_PILLAR
        self._draw_top_pillar(surf, palette)
        self._draw_bottom_pillar(surf, palette)


# ── Coin ─────────────────────────────────────────────────────────────────────

def _build_star(r, color):
    """Pre-render a 5-pointed star into an SRCALPHA surface."""
    size = r * 2 + 2
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    cx = cy = r + 1
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        radius = r if i % 2 == 0 else r * 0.45
        pts.append((cx + math.cos(ang) * radius, cy + math.sin(ang) * radius))
    pygame.draw.polygon(s, color, pts)
    return s


_STAR_CACHE: dict = {}


def _get_star(r, color):
    key = (r, color)
    s = _STAR_CACHE.get(key)
    if s is None:
        s = _build_star(r, color)
        _STAR_CACHE[key] = s
    return s


class Coin:
    """Slow-rotating metallic gold disc.

    The coin is drawn as a full circle (its "face") for most of its rotation,
    and only briefly narrows to an edge-on sliver — so the collectable always
    reads as a coin. COIN_R governs both the face radius and the collision
    radius so what you see is what you collect.
    """

    # ≈ 5.7 seconds per full rotation.
    SPIN_RATE = 1.1

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.spin = random.uniform(0, math.tau)
        self.collected = False
        self.float_t = random.uniform(0, math.tau)
        # Independent sweep phase for the animated rim glint
        self.shimmer_t = random.uniform(0, math.tau)

    def update(self, dt):
        self.spin = (self.spin + dt * self.SPIN_RATE) % math.tau
        self.float_t += dt
        self.shimmer_t += dt

    def draw(self, surf):
        cx = int(self.x)
        cy = int(self.y + math.sin(self.float_t * 2.2) * 2)

        # Pulsing outer + inner glow for collect appeal
        pulse = 0.5 + 0.5 * math.sin(self.shimmer_t * 3.0)
        blit_glow(surf, cx, cy, COIN_R + 14, COIN_GOLD, int(150 + 50 * pulse))
        blit_glow(surf, cx, cy, COIN_R + 4,  COIN_LIGHT, int(110 + 30 * pulse))

        cos_s = math.cos(self.spin)
        rx = cos_s * COIN_R
        ry = COIN_R

        if abs(cos_s) > 0.35:
            # ── Face-on: draw the full metallic disc ────────────────────────
            rx_i = max(2, int(abs(rx)))
            # Outer black outline ring for crispness
            pygame.draw.ellipse(surf, NEAR_BLACK, (cx - rx_i - 2, cy - ry - 2,
                                                   (rx_i + 2) * 2, (ry + 2) * 2))
            # Thick metallic rim: bright gold upper-left, dark gold lower-right.
            pygame.draw.ellipse(surf, COIN_LIGHT, (cx - rx_i - 1, cy - ry - 1,
                                                   (rx_i + 1) * 2, (ry + 1) * 2))
            # Mask the bottom-right of the rim to COIN_DARK for depth.
            pygame.draw.ellipse(surf, COIN_DARK, (cx - rx_i, cy - ry + 1,
                                                  rx_i * 2, ry * 2 - 1))
            # Main gold face
            pygame.draw.ellipse(surf, COIN_GOLD, (cx - rx_i + 1, cy - ry + 1,
                                                   (rx_i - 1) * 2, (ry - 1) * 2))
            # Top-left radial highlight
            hi_rx = max(2, int(rx_i * 0.65))
            hi_ry = max(2, int(ry * 0.55))
            pygame.draw.ellipse(surf, COIN_LIGHT, (cx - rx_i + 2, cy - ry + 2,
                                                    hi_rx, hi_ry))

            # Embossed 5-point star stamp
            star_r = max(3, int(ry * 0.55))
            shadow = _get_star(star_r, (*COIN_DARK, 255))
            face   = _get_star(star_r - 1, (*COIN_LIGHT, 255))
            surf.blit(shadow, (cx - star_r + 1, cy - star_r + 1))
            surf.blit(face,   (cx - (star_r - 1), cy - (star_r - 1)))

            # Animated rim glint: a short bright arc that sweeps around the coin
            ang = self.shimmer_t * 1.3
            gx = cx + int(math.cos(ang) * (rx_i - 2))
            gy = cy + int(math.sin(ang) * (ry - 2))
            pygame.draw.circle(surf, WHITE, (gx, gy), 2)
            pygame.draw.circle(surf, (255, 255, 255, 180), (gx, gy), 1)
        else:
            # ── Near edge-on: a slim gold bar (the coin's thickness) ────────
            rx_i = max(2, int(abs(rx)))
            # Dark outline
            pygame.draw.ellipse(surf, NEAR_BLACK, (cx - rx_i - 1, cy - ry,
                                                   (rx_i + 1) * 2, ry * 2))
            # Gold core
            pygame.draw.ellipse(surf, COIN_GOLD, (cx - rx_i, cy - ry,
                                                  rx_i * 2, ry * 2))
            # Thin bright highlight stripe down the middle
            pygame.draw.line(surf, COIN_LIGHT,
                             (cx, cy - ry + 2), (cx, cy + ry - 2), 1)
            # Darker top/bottom caps suggesting the coin's edge curvature
            pygame.draw.line(surf, COIN_DARK,
                             (cx - rx_i, cy - ry + 1), (cx + rx_i, cy - ry + 1), 1)
            pygame.draw.line(surf, COIN_DARK,
                             (cx - rx_i, cy + ry - 1), (cx + rx_i, cy + ry - 1), 1)


# ── Mushroom ─────────────────────────────────────────────────────────────────

class Mushroom:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.collected = False
        self.pulse = 0.0

    def update(self, dt):
        self.pulse += dt * 3.5

    def draw(self, surf):
        cx = int(self.x)
        cy = int(self.y)
        # Double halo: warm outer + magenta inner
        outer_r = MUSHROOM_R + 14 + int(math.sin(self.pulse) * 4)
        inner_r = MUSHROOM_R + 6  + int(math.sin(self.pulse * 1.4) * 2)
        blit_glow(surf, cx, cy - 4, outer_r, (255, 230, 160), 160)
        blit_glow(surf, cx, cy - 4, inner_r, (255,  90, 180), 170)

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


def _get_float_font(size, bold=True):
    key = (size, bold)
    f = _float_font_cache.get(key)
    if f is None:
        f = pygame.font.SysFont("arial", size, bold=bold)
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
