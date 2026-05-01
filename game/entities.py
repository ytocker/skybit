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
    BIRD_X, BIRD_R, PIPE_W, COIN_R, POWERUP_R, GROUND_Y,
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
from game.dollar_coin_glyphs import draw_coin_font_bold as _draw_dollar_coin
from game.surprise_box_variants import draw_cross as _draw_surprise_box

# ── SURPRISE power-up gift box (rendered at 2× then smoothscaled, cached) ───
_surprise_sprite: "pygame.Surface | None" = None

def _get_surprise_sprite() -> "pygame.Surface":
    global _surprise_sprite
    if _surprise_sprite is None:
        scratch = pygame.Surface((64, 64), pygame.SRCALPHA)
        _draw_surprise_box(scratch, 32, 32)
        target = 2 * POWERUP_R + 12   # leave the bow + drop-shadow room
        _surprise_sprite = pygame.transform.smoothscale(scratch, (target, target))
    return _surprise_sprite


# ── GROW power-up parrot (scaled in-game sprite, cached) ─────────────────────
_grow_parrot: "pygame.Surface | None" = None

def _get_grow_parrot() -> "pygame.Surface":
    global _grow_parrot
    if _grow_parrot is None:
        src = parrot.FRAMES[1]
        target_w = 26
        ratio = target_w / src.get_width()
        target_h = int(src.get_height() * ratio)
        _grow_parrot = pygame.transform.smoothscale(src, (target_w, target_h))
    return _grow_parrot


# ── KFC logo sprite (lazy-loaded once at first draw) ─────────────────────────
_kfc_sprite: "pygame.Surface | None" = None

def _get_kfc_sprite() -> "pygame.Surface":
    global _kfc_sprite
    if _kfc_sprite is None:
        import os
        r         = POWERUP_R + 2
        logo_size = int(r * 2.4)
        path      = os.path.join(os.path.dirname(__file__), "assets", "kfc_logo.jpg")
        raw = pygame.image.load(path)
        # Crop to square (center crop on the wider axis)
        rw, rh = raw.get_size()
        side = min(rw, rh)
        crop = pygame.Surface((side, side))
        crop.blit(raw, (-(rw - side) // 2, -(rh - side) // 2))
        # Scale 38% larger so the white outer ring is pushed outside the circle mask
        zoomed_size = int(logo_size * 1.38)
        scaled = pygame.transform.smoothscale(crop, (zoomed_size, zoomed_size))
        # Convert to SRCALPHA so the circle mask can punch out corners
        logo = pygame.Surface((logo_size, logo_size), pygame.SRCALPHA)
        offset = (logo_size - zoomed_size) // 2
        logo.blit(scaled, (offset, offset))
        mask = pygame.Surface((logo_size, logo_size), pygame.SRCALPHA)
        pygame.draw.circle(mask, (255, 255, 255, 255),
                           (logo_size // 2, logo_size // 2), logo_size // 2)
        logo.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        _kfc_sprite = logo
    return _kfc_sprite


# ── GHOST power-up sprite (procedural, cached on first draw) ────────────────
# Holographic foil body (diagonal pearl-pink → cyan → mint → ivory) inside a
# 2-px premium navy outline ring + crisp eyes + soft sheen.
_ghost_sprite: "pygame.Surface | None" = None
_GHOST_HEAD_OFFSET_X = 16   # head-circle centre x in the sprite
_GHOST_HEAD_OFFSET_Y = 14   # head-circle centre y in the sprite


def _get_ghost_sprite() -> "pygame.Surface":
    global _ghost_sprite
    if _ghost_sprite is not None:
        return _ghost_sprite

    SS = 8                                    # was 4 — denser super-sample
                                              # for cleaner anti-aliased edges
    PAD = 2
    GW, GH = (28 + PAD * 2), (36 + PAD * 2)   # 32 × 40 final-px
    sw, sh = GW * SS, GH * SS
    big = pygame.Surface((sw, sh), pygame.SRCALPHA)

    # Geometry in supersampled units
    gcx = (14 + PAD) * SS
    gcy = (12 + PAD) * SS
    hr  = 12 * SS
    body_y2 = (26 + PAD) * SS
    body_rect = pygame.Rect((1 + PAD) * SS, gcy,
                            (28 - 2) * SS, body_y2 - gcy)
    # Symmetric 3-bump / 2-indent scallop with uniform-width waves. The
    # 7 control points are mirror-symmetric about the body's vertical
    # centreline and evenly spaced (each segment span/6 wide), so every
    # "wave" along the bottom has the same width.
    bump_y   = (GH - 4) * SS
    indent_y = body_y2 + 4 * SS
    x_left   = (1 + PAD) * SS
    x_right  = (28 - 2 + PAD) * SS
    span_x   = x_right - x_left
    scallop = [
        (x_left + i * span_x // 6,
         body_y2 if i in (0, 6) else (bump_y if i % 2 == 1 else indent_y))
        for i in range(7)
    ]

    OUTLINE_COLOR = (40, 50, 90)
    THICKNESS_PX  = 2

    # 1) Outline ring — stack the silhouette in OUTLINE_COLOR at every
    #    integer offset within a circle of radius `THICKNESS_PX*SS`. The
    #    dense step (1, was SS//2 = 4) keeps the ring perfectly uniform
    #    around the full perimeter — no thin spots at the bump corners.
    sil = pygame.Surface((sw, sh), pygame.SRCALPHA)
    pygame.draw.circle(sil, OUTLINE_COLOR, (gcx, gcy), hr)
    pygame.draw.rect(sil, OUTLINE_COLOR, body_rect)
    pygame.draw.polygon(sil, OUTLINE_COLOR, scallop)
    t_big = THICKNESS_PX * SS
    for dx in range(-t_big, t_big + 1):
        for dy in range(-t_big, t_big + 1):
            if dx * dx + dy * dy <= t_big * t_big:
                big.blit(sil, (dx, dy))

    # 2) Silhouette mask (used to clip the body gradient and the sheen).
    mask = pygame.Surface((sw, sh), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (gcx, gcy), hr)
    pygame.draw.rect(mask, (255, 255, 255, 255), body_rect)
    pygame.draw.polygon(mask, (255, 255, 255, 255), scallop)

    # 3) Holographic foil body — diagonal multi-stop gradient. Build a
    #    1-D gradient strip of length sw+sh once (per-pixel set_at on a
    #    single row, so cheap), then per row blit a sw-wide slice of it
    #    starting at offset y. This produces the 45° diagonal gradient
    #    without per-pixel work over the full sw×sh canvas — important
    #    now that SS=8 means a 256×320 supersampled surface.
    stops = [
        (0.00, (240, 215, 255)),  # pale lavender
        (0.30, (255, 220, 240)),  # pearl pink
        (0.55, (220, 240, 255)),  # cyan
        (0.80, (215, 255, 235)),  # mint
        (1.00, (245, 245, 220)),  # warm ivory
    ]
    diag_len = sw + sh
    strip = pygame.Surface((diag_len, 1), pygame.SRCALPHA)
    for xx in range(diag_len):
        t = xx / max(1, diag_len - 1)
        if t <= stops[0][0]:
            col = stops[0][1]
        elif t >= stops[-1][0]:
            col = stops[-1][1]
        else:
            col = stops[-1][1]
            for i in range(len(stops) - 1):
                a_pos, a_col = stops[i]
                b_pos, b_col = stops[i + 1]
                if a_pos <= t <= b_pos:
                    u = (t - a_pos) / max(1e-6, b_pos - a_pos)
                    col = (
                        int(a_col[0] + (b_col[0] - a_col[0]) * u),
                        int(a_col[1] + (b_col[1] - a_col[1]) * u),
                        int(a_col[2] + (b_col[2] - a_col[2]) * u),
                    )
                    break
        strip.set_at((xx, 0), col + (245,))
    grad = pygame.Surface((sw, sh), pygame.SRCALPHA)
    for yy in range(sh):
        # Slice (yy, 0, sw, 1) of the strip lands on row yy of the gradient.
        slice_rect = pygame.Rect(yy, 0, sw, 1)
        grad.blit(strip, (0, yy), area=slice_rect)
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    big.blit(grad, (0, 0))

    # 4) Soft white sheen on the upper portion for the foil shimmer.
    sheen = pygame.Surface((sw, sh), pygame.SRCALPHA)
    sy0 = gcy - hr
    sy1 = gcy + int(hr * 0.5)
    for yy in range(sy0, sy1):
        t = (yy - sy0) / max(1, sy1 - sy0)
        a = int(150 * (1.0 - t) ** 1.5)
        if a > 0:
            pygame.draw.line(sheen, (255, 255, 255, a), (0, yy), (sw, yy))
    sheen.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    big.blit(sheen, (0, 0))

    # 5) Eyes
    EYE_W    = (252, 254, 255, 255)
    EYE_IRIS = (50, 110, 220, 255)
    EYE_PUP  = (12,  18,  60, 255)
    for ex_off in (-5, 5):
        ex = gcx + ex_off * SS
        ey = gcy - 1 * SS
        pygame.draw.circle(big, EYE_W,    (ex,         ey        ), int(3.5 * SS))
        pygame.draw.circle(big, EYE_IRIS, (ex + SS,    ey + SS    ), int(2.5 * SS))
        pygame.draw.circle(big, EYE_PUP,  (ex + SS,    ey + SS    ), max(1, SS))
        pygame.draw.circle(big, (255, 255, 255, 220),
                           (ex - SS, ey - 2 * SS), max(1, SS // 2))

    _ghost_sprite = pygame.transform.smoothscale(big, (GW, GH))
    return _ghost_sprite


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
        self.kfc_active = False
        self.ghost_active = False
        self.grow_active = False
        self.triple_active = False
        self.ghost_pulse = 0.0    # advances while ghost_active for fade effect

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
        if self.ghost_active:
            self.ghost_pulse += dt * 2.4

    def draw(self, surf, shake_x=0, shake_y=0, flipped=False):
        frame_idx = int(self.frame_t) % len(parrot.FRAMES)
        # When flipped (reverse-gravity buff), negate the tilt so a rising
        # bird's head still leads in the direction of motion after the
        # vertical mirror is applied below.
        tilt = -self.tilt_deg if flipped else self.tilt_deg
        if self.kfc_active:
            img = parrot.get_fried_parrot(frame_idx, tilt)
        elif self.ghost_active:
            img = parrot.get_ghost_parrot(frame_idx, tilt)
        elif self.triple_active:
            img = parrot.get_hat_parrot(frame_idx, tilt)
        else:
            img = parrot.get_parrot(frame_idx, tilt)
        if self.grow_active:
            from game.config import GROW_SCALE
            w, h = img.get_size()
            img = pygame.transform.smoothscale(img, (int(w * GROW_SCALE), int(h * GROW_SCALE)))
        if flipped:
            img = pygame.transform.flip(img, False, True)
        if self.ghost_active:
            # Faded breathing: alpha oscillates ~90..170 over a slow sine,
            # so the ghost reads as clearly translucent and ethereal.
            img = img.copy()
            pulse = 0.5 + 0.5 * math.sin(self.ghost_pulse)
            img.set_alpha(int(90 + pulse * 80))
        r = img.get_rect(center=(self.x + shake_x, self.y + shake_y))
        surf.blit(img, r.topleft)

        # Parcel — Pip's permanent companion. Tucked below his centre with
        # a tilt-aware offset so it banks with him; mode-coloured to match
        # the active palette; alpha-breathes in ghost mode; grow-scaled.
        if self.kfc_active:
            mode = "kfc"
        elif self.ghost_active:
            mode = "ghost"
        elif self.triple_active:
            mode = "triple"
        else:
            mode = "normal"
        parcel = parrot.get_parcel(mode)
        from game.config import GROW_SCALE, PARCEL_Y_OFFSET
        scale = GROW_SCALE if self.grow_active else 1.0
        if scale != 1.0:
            pw, ph = parcel.get_size()
            parcel = pygame.transform.smoothscale(
                parcel, (int(pw * scale), int(ph * scale)))
        # When reverse-gravity is active, the parcel mirrors with Pip:
        # the sprite flips vertically, the y-offset negates so the parcel
        # rides ABOVE Pip's centre, and the tilt direction inverts so the
        # parcel banks the same way as the flipped bird.
        if flipped:
            parcel = pygame.transform.flip(parcel, False, True)
        y_off = -PARCEL_Y_OFFSET * scale if flipped else PARCEL_Y_OFFSET * scale
        parcel_tilt = -self.tilt_deg if flipped else self.tilt_deg
        offset = pygame.math.Vector2(0, y_off)
        offset = offset.rotate(-parcel_tilt)
        # Rotate the parcel sprite to match tilt so the gift bow keeps
        # pointing "up" relative to Pip's local frame.
        parcel_rot = pygame.transform.rotate(parcel, parcel_tilt)
        if self.ghost_active:
            parcel_rot = parcel_rot.copy()
            parcel_rot.set_alpha(int(90 + pulse * 80))
        pr = parcel_rot.get_rect(center=(self.x + shake_x + offset.x,
                                         self.y + shake_y + offset.y))
        surf.blit(parcel_rot, pr.topleft)


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

_COIN_FACE_CACHE: "pygame.Surface | None" = None


def _get_coin_face() -> pygame.Surface:
    """Build the face-on coin sprite once at 4x super-sample. Layers:
    dark-amber outline, a twisted-rope rim (alternating dark/light
    segments around the perimeter), a vertical gold gradient body, an
    embossed parrot silhouette, and a soft upper-left specular highlight.
    Smoothscaled per frame to apply the coin-spin squeeze, so the rope
    rim stays visible across every frame of the rotation animation."""
    global _COIN_FACE_CACHE
    if _COIN_FACE_CACHE is not None:
        return _COIN_FACE_CACHE
    SS = 4
    final_d = COIN_R * 2 + 4
    size = final_d * SS
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx = cy = size // 2
    r_outer = size // 2 - SS
    r_outline = max(SS * 2, r_outer // 6)
    r_body = r_outer - r_outline

    GOLD_HI    = (255, 232, 130)
    GOLD_MID   = (240, 195,  55)
    GOLD_LO    = (190, 130,  20)
    OUTLINE_DK = ( 95,  50,   0)
    OUTLINE_LT = (150,  90,  10)
    EMBOSS     = (130,  80,   0)
    DARK_AMBER = ( 75,  35,   0)
    LITE_AMBER = (210, 165,  50)

    # 1) Bold double-band outline.
    pygame.draw.circle(surf, OUTLINE_DK, (cx, cy), r_outer)
    pygame.draw.circle(surf, OUTLINE_LT, (cx, cy), r_outer - SS)

    # 2) Vertical gradient body, masked to the inner circle.
    body_surf = pygame.Surface((size, size), pygame.SRCALPHA)
    y0, y1 = cy - r_body, cy + r_body
    for yy in range(y0, y1 + 1):
        t = (yy - y0) / max(1, (y1 - y0))
        if t < 0.4:
            u = t / 0.4
            col = (
                int(GOLD_HI[0]  + (GOLD_MID[0] - GOLD_HI[0])  * u),
                int(GOLD_HI[1]  + (GOLD_MID[1] - GOLD_HI[1])  * u),
                int(GOLD_HI[2]  + (GOLD_MID[2] - GOLD_HI[2])  * u),
            )
        else:
            u = (t - 0.4) / 0.6
            col = (
                int(GOLD_MID[0] + (GOLD_LO[0]  - GOLD_MID[0]) * u),
                int(GOLD_MID[1] + (GOLD_LO[1]  - GOLD_MID[1]) * u),
                int(GOLD_MID[2] + (GOLD_LO[2]  - GOLD_MID[2]) * u),
            )
        pygame.draw.line(body_surf, col, (0, yy), (size, yy))
    body_mask = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(body_mask, (255, 255, 255, 255), (cx, cy), r_body)
    body_surf.blit(body_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(body_surf, (0, 0))

    # 3) Twisted-rope rim — alternating dark/light arcs around the perimeter.
    n_segs = 22
    ring_r = r_outer - r_outline // 2
    seg_w = max(SS * 3, r_outline + SS)
    for i in range(n_segs):
        ang = i * (math.tau / n_segs)
        ang_next = (i + 1) * (math.tau / n_segs)
        mid = (ang + ang_next) / 2
        sx = cx + math.cos(mid) * ring_r
        sy = cy + math.sin(mid) * ring_r
        seg_len = int((math.tau / n_segs) * ring_r * 0.95)
        seg = pygame.Surface((seg_len, seg_w), pygame.SRCALPHA)
        col       = DARK_AMBER if i % 2 == 0 else LITE_AMBER
        highlight = LITE_AMBER if i % 2 == 0 else GOLD_HI
        pygame.draw.ellipse(seg, col, seg.get_rect())
        pygame.draw.ellipse(seg, highlight, seg.get_rect().inflate(-SS, -SS))
        rotated = pygame.transform.rotate(seg, -math.degrees(mid))
        r_rect = rotated.get_rect(center=(int(sx), int(sy)))
        surf.blit(rotated, r_rect.topleft)

    # 4) Embossed parrot silhouette inside the rope rim.
    pygame.draw.ellipse(surf, EMBOSS,
                        (cx - 2 * SS, cy - 1 * SS, 7 * SS, 5 * SS))
    pygame.draw.circle(surf, EMBOSS, (cx - 1 * SS, cy - 3 * SS), 3 * SS)
    pygame.draw.polygon(surf, EMBOSS,
                        [(cx - 3 * SS, cy - 3 * SS),
                         (cx - 6 * SS, cy - 2 * SS),
                         (cx - 3 * SS, cy - 1 * SS)])
    pygame.draw.circle(surf, GOLD_HI, (cx, cy - 4 * SS), max(1, SS - 1))

    # 5) Specular highlight crescent on the upper-left, masked to body.
    hl = pygame.Surface((size, size), pygame.SRCALPHA)
    hl_rect = pygame.Rect(cx - r_body + r_body // 5,
                          cy - r_body + r_body // 6,
                          int(r_body * 1.1), int(r_body * 0.5))
    pygame.draw.ellipse(hl, (255, 255, 235, 110), hl_rect)
    hl.blit(body_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(hl, (0, 0))

    _COIN_FACE_CACHE = pygame.transform.smoothscale(surf, (final_d, final_d))
    return _COIN_FACE_CACHE


class Coin:
    """Spinning gold parrot medallion. Built once at 4x super-sample with a
    bold dark outline + vertical gold gradient + embossed parrot + soft
    specular highlight (matches the +1/+3 float-text style guidelines:
    gradient, outline, sparkle). Squeezed horizontally per frame by
    |cos(spin)|. Sparkle twinkles flash near the coin in the spin cycle."""

    SPIN_RATE = 1.1  # ≈ 5.7 seconds per full rotation

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.spin = random.uniform(0, math.tau)
        self.collected = False
        self.float_t = random.uniform(0, math.tau)
        # Random sparkle phase per-coin so they don't all twinkle in sync.
        self._sparkle_phase = random.uniform(0, math.tau)

    def update(self, dt):
        self.spin = (self.spin + dt * self.SPIN_RATE) % math.tau
        self.float_t += dt

    def draw(self, surf, kfc_active=False):
        cx = int(self.x)
        cy = int(self.y + math.sin(self.float_t * 2.2) * 2)

        # During KFC: coins look like a tilted french fry instead of a gold
        # disc. The fry uses the same footprint as the coin so collisions
        # stay aligned, but it doesn't spin (fries don't really spin like
        # a disc — they just bob).
        if kfc_active:
            from game.kfc_fries import draw_tilted
            draw_tilted(surf, cx, cy, t=self.float_t)
            return

        # Spin animation: the cached face is smoothscaled horizontally by
        # |cos(spin)| every frame, so the rope rim, outline, gradient, and
        # embossed parrot are all preserved across every angle of the
        # rotation — including near-edge-on slivers. A small floor on the
        # squeeze (10% width) keeps the edge-on frame readable instead of
        # collapsing to a 1-px line.
        cos_s = math.cos(self.spin)
        r = COIN_R
        squeeze = max(0.10, abs(cos_s))
        face = _get_coin_face()
        fw, fh = face.get_size()
        target_w = max(2, int(fw * squeeze))
        squeezed = pygame.transform.smoothscale(face, (target_w, fh))
        rect = squeezed.get_rect(center=(cx, cy))
        surf.blit(squeezed, rect.topleft)

        # Sparkle twinkles — 2 small white dots near the coin that flash
        # on/off out of phase. Only render when mostly face-on so they
        # don't drift around a flat sliver.
        if abs(cos_s) > 0.6:
            for i, (dx, dy) in enumerate(((-r - 2, -r + 1), (r + 2, r - 1))):
                phase = self._sparkle_phase + i * math.pi
                t = 0.5 + 0.5 * math.sin(self.float_t * 3.0 + phase)
                if t > 0.7:
                    a = int(255 * (t - 0.7) / 0.3)
                    star = pygame.Surface((6, 6), pygame.SRCALPHA)
                    pygame.draw.circle(star, (255, 250, 220, a), (3, 3), 2)
                    pygame.draw.circle(star, (255, 255, 255, a), (3, 3), 1)
                    surf.blit(star, (cx + dx - 3, cy + dy - 3))


# ── PowerUp ──────────────────────────────────────────────────────────────────

# Lazy-initialized high-resolution cache for the "reverse" power-up icon —
# two purple arrows (up on the left, down on the right) on a fully transparent
# background. Rendered once at 4x super-sampling and smoothscaled down so the
# arrow edges read clean at any size. Reused for both the in-world pickup and
# the HUD active-buff badge.
_REVERSE_ICON_CACHE: "dict[int, pygame.Surface]" = {}


def _build_reverse_icon(out_diameter: int) -> pygame.Surface:
    """Premium icon: holographic iridescent panel inside a pearl-violet frame
    with two thick gradient purple chevrons (up + down). Built at 4x super-
    sampling and smoothscaled down for crisp edges on any background."""
    SS = 4
    size = out_diameter * SS
    surf = pygame.Surface((size, size), pygame.SRCALPHA)

    # ── Palette ─────────────────────────────────────────────────────────
    OUTLINE      = (20, 12, 55)         # outer dark indigo hairline
    FRAME        = (195, 175, 240)      # pearl-violet frame stroke
    FRAME_HL     = (255, 255, 255)      # tiny top-edge highlight
    INSET_SHADOW = (0, 0, 0, 38)        # soft inner shadow under the frame
    HOLO_STOPS   = (
        (240, 220, 240),                # top-left: pale pink
        (210, 220, 245),                # mid: lavender-blue
        (215, 240, 240),                # bottom-right: mint cyan
    )
    ARROW_TOP    = (175, 100, 230)
    ARROW_MID    = (130, 55, 200)
    ARROW_BOT    = (75, 25, 145)
    ARROW_OUT    = (35, 10, 70)
    SHEEN        = (255, 255, 255, 80)

    radius   = SS * 11                 # squircle-style corners
    inset    = SS                      # 1-px outer outline gap
    frame_t  = SS * 2                  # frame stroke = 2 final-px

    panel = pygame.Rect(inset, inset, size - inset * 2, size - inset * 2)

    # 1) Outer 1-px dark hairline.
    pygame.draw.rect(surf, OUTLINE, panel, border_radius=radius)
    # 2) Pearl-violet frame fill.
    pygame.draw.rect(surf, FRAME, panel.inflate(-SS * 2, -SS * 2),
                     border_radius=radius - SS)
    # 3) Holographic diagonal gradient panel inside the frame.
    inner = panel.inflate(-(frame_t + SS) * 2, -(frame_t + SS) * 2)
    inner_radius = max(2, radius - frame_t - SS)
    grad = pygame.Surface((size, size), pygame.SRCALPHA)
    for y in range(inner.top, inner.bottom + 1):
        for x in range(inner.left, inner.right + 1):
            t = ((x - inner.left) / max(1, inner.width)
                 + (y - inner.top) / max(1, inner.height)) / 2
            if t < 0.5:
                u = t / 0.5
                col = (
                    int(HOLO_STOPS[0][0] + (HOLO_STOPS[1][0] - HOLO_STOPS[0][0]) * u),
                    int(HOLO_STOPS[0][1] + (HOLO_STOPS[1][1] - HOLO_STOPS[0][1]) * u),
                    int(HOLO_STOPS[0][2] + (HOLO_STOPS[1][2] - HOLO_STOPS[0][2]) * u),
                )
            else:
                u = (t - 0.5) / 0.5
                col = (
                    int(HOLO_STOPS[1][0] + (HOLO_STOPS[2][0] - HOLO_STOPS[1][0]) * u),
                    int(HOLO_STOPS[1][1] + (HOLO_STOPS[2][1] - HOLO_STOPS[1][1]) * u),
                    int(HOLO_STOPS[1][2] + (HOLO_STOPS[2][2] - HOLO_STOPS[1][2]) * u),
                )
            grad.set_at((x, y), col)
    inner_mask = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.rect(inner_mask, (255, 255, 255, 255), inner,
                     border_radius=inner_radius)
    grad.blit(inner_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(grad, (0, 0))

    # 4) Soft inner shadow inside the panel — gives the panel a recessed feel.
    shadow_surf = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.rect(shadow_surf, INSET_SHADOW, inner,
                     border_radius=inner_radius, width=SS)
    surf.blit(shadow_surf, (0, 0))

    # 5) Top-edge highlight on the frame.
    pygame.draw.line(surf, FRAME_HL,
                     (panel.left + radius, panel.top + SS),
                     (panel.right - radius, panel.top + SS),
                     max(1, SS // 2))

    # ── Arrows: thick filled chevrons with vertical gradient + sheen ───
    pad_x = max(SS * 5, panel.width // 6)
    pad_y = max(SS * 5, panel.height // 7)
    area = panel.inflate(-pad_x * 2, -pad_y * 2)

    col_w = area.width // 2
    lx = area.left + col_w // 2
    rx = area.right - col_w // 2
    head_h  = area.height * 42 // 100
    shaft_w = area.width * 17 // 100
    head_w  = shaft_w * 26 // 10

    def silhouette(col_x, *, point_up, expand=0):
        e = expand
        sw = shaft_w + e * 2
        hw = head_w + e * 2
        if point_up:
            tip  = (col_x, area.top - e)
            base = area.bottom + e
            sh_y = area.top + head_h - e // 3
            return [
                tip,
                (col_x + hw // 2, sh_y),
                (col_x + sw // 2, sh_y),
                (col_x + sw // 2, base),
                (col_x - sw // 2, base),
                (col_x - sw // 2, sh_y),
                (col_x - hw // 2, sh_y),
            ]
        else:
            tip  = (col_x, area.bottom + e)
            base = area.top - e
            sh_y = area.bottom - head_h + e // 3
            return [
                tip,
                (col_x - hw // 2, sh_y),
                (col_x - sw // 2, sh_y),
                (col_x - sw // 2, base),
                (col_x + sw // 2, base),
                (col_x + sw // 2, sh_y),
                (col_x + hw // 2, sh_y),
            ]

    def draw_arrow(col_x, *, point_up):
        # Outline.
        pygame.draw.polygon(surf, ARROW_OUT,
                            silhouette(col_x, point_up=point_up, expand=SS))
        # Vertical gradient body, scanline-masked.
        body = silhouette(col_x, point_up=point_up, expand=0)
        body_surf = pygame.Surface((size, size), pygame.SRCALPHA)
        ys = [p[1] for p in body]
        y0, y1 = min(ys), max(ys)
        for y in range(y0, y1 + 1):
            t = (y - y0) / max(1, (y1 - y0))
            if not point_up:
                t = 1.0 - t
            if t < 0.4:
                u = t / 0.4
                col = (
                    int(ARROW_TOP[0] + (ARROW_MID[0] - ARROW_TOP[0]) * u),
                    int(ARROW_TOP[1] + (ARROW_MID[1] - ARROW_TOP[1]) * u),
                    int(ARROW_TOP[2] + (ARROW_MID[2] - ARROW_TOP[2]) * u),
                )
            else:
                u = (t - 0.4) / 0.6
                col = (
                    int(ARROW_MID[0] + (ARROW_BOT[0] - ARROW_MID[0]) * u),
                    int(ARROW_MID[1] + (ARROW_BOT[1] - ARROW_MID[1]) * u),
                    int(ARROW_MID[2] + (ARROW_BOT[2] - ARROW_MID[2]) * u),
                )
            pygame.draw.line(body_surf, col, (0, y), (size, y))
        mask = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.polygon(mask, (255, 255, 255, 255), body)
        body_surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        surf.blit(body_surf, (0, 0))

        # Glossy sheen across the arrow head.
        sheen = pygame.Surface((size, size), pygame.SRCALPHA)
        if point_up:
            sy0, sy1 = area.top, area.top + head_h * 9 // 10
        else:
            sy0, sy1 = area.bottom - head_h * 9 // 10, area.bottom
        for y in range(min(sy0, sy1), max(sy0, sy1) + 1):
            t = (y - sy0) / max(1, (sy1 - sy0))
            if not point_up:
                t = 1.0 - t
            a = int(SHEEN[3] * (1.0 - t) ** 1.4)
            if a > 0:
                pygame.draw.line(sheen, (*SHEEN[:3], a), (0, y), (size, y))
        sheen.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        surf.blit(sheen, (0, 0))

    draw_arrow(lx, point_up=True)
    draw_arrow(rx, point_up=False)

    return pygame.transform.smoothscale(surf, (out_diameter, out_diameter))


def _get_reverse_icon(diameter: int = (POWERUP_R + 8) * 2) -> pygame.Surface:
    cached = _REVERSE_ICON_CACHE.get(diameter)
    if cached is None:
        cached = _build_reverse_icon(diameter)
        _REVERSE_ICON_CACHE[diameter] = cached
    return cached


class PowerUp:
    """A collectible buff. `kind` selects visuals and pickup effect:
       triple   — red mushroom, 3x coin value for TRIPLE_DURATION
       magnet   — red horseshoe, pulls coins in for MAGNET_DURATION
       slowmo   — purple hourglass, 0.5x world scroll for SLOWMO_DURATION
       kfc      — KFC bucket, fried-chicken parrot mode for KFC_DURATION
       ghost    — phantom, phase-through pipes for GHOST_DURATION
       grow     — Mario mushroom, scaled-up parrot for GROW_DURATION
       reverse  — purple double-arrow, flips Pip's gravity for REVERSE_DURATION
       surprise — gold "?" block; resolves at pickup to one of the seven
                  effects above (the matching sound plays, no separate
                  surprise sound).
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
            _draw_dollar_coin(surf, int(self.x), int(self.y), pulse=self.pulse)
        elif self.kind == "magnet":
            self._draw_magnet(surf)
        elif self.kind == "slowmo":
            self._draw_slowmo(surf)
        elif self.kind == "kfc":
            self._draw_kfc(surf)
        elif self.kind == "ghost":
            self._draw_ghost(surf)
        elif self.kind == "grow":
            self._draw_mushroom(surf)    # mushroom icon (Mario super-mushroom feel)
        elif self.kind == "reverse":
            self._draw_reverse(surf)
        elif self.kind == "surprise":
            self._draw_surprise(surf)

    # ── sprite variants ─────────────────────────────────────────────────────
    def _draw_mushroom(self, surf):
        cx = int(self.x)
        cy = int(self.y)

        # Stem with vivid highlight
        stem = pygame.Rect(cx - 7, cy, 14, 13)
        rounded_rect(surf, stem, 5, MUSH_STEM, 255)
        pygame.draw.line(surf, (255, 255, 230), (cx - 4, cy + 2), (cx - 4, cy + 11), 2)
        pygame.draw.line(surf, (200, 180, 145), (cx + 3, cy + 2), (cx + 3, cy + 11), 1)

        cap_rect = pygame.Rect(cx - POWERUP_R - 1, cy - POWERUP_R + 2, (POWERUP_R + 1) * 2, POWERUP_R + 5)

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

    def _draw_surprise(self, surf):
        cx = int(self.x)
        cy = int(self.y + math.sin(self.pulse * 0.7) * 2)
        sprite = _get_surprise_sprite()
        surf.blit(sprite, sprite.get_rect(center=(cx, cy)))

    def _draw_magnet(self, surf):
        cx = int(self.x)
        cy = int(self.y + math.sin(self.pulse * 1.1) * 3)   # float bob

        outer_r = 13
        inner_r = 6
        arch_cy = cy - 3
        leg_bot = cy + 12

        # Build the horseshoe on an SRCALPHA scratch surface so the hollow
        # can be punched cleanly with alpha=0 overdraw.
        sz  = 42
        scx = sz // 2
        scy = outer_r + 4

        scratch = pygame.Surface((sz, sz), pygame.SRCALPHA)

        # Dark shadow rim
        pygame.draw.circle(scratch, (80, 5, 8), (scx, scy), outer_r + 2)
        pygame.draw.rect(scratch, (80, 5, 8),
                         (scx - outer_r - 2, scy,
                          (outer_r + 2) * 2, leg_bot - arch_cy + 4))

        # Vivid crimson body
        RED_HI = (235, 35, 45)
        pygame.draw.circle(scratch, RED_HI, (scx, scy), outer_r + 1)
        pygame.draw.rect(scratch, RED_HI,
                         (scx - outer_r - 1, scy,
                          (outer_r + 1) * 2, leg_bot - arch_cy + 3))

        # Specular sheen across arch top
        sheen = pygame.Surface((outer_r * 2 - 2, outer_r - 1), pygame.SRCALPHA)
        pygame.draw.ellipse(sheen, (255, 160, 165, 140), sheen.get_rect())
        scratch.blit(sheen, (scx - outer_r + 1, 3))

        # Highlight rings
        pygame.draw.circle(scratch, (255, 95, 95), (scx, scy), inner_r + 1, 2)
        pygame.draw.circle(scratch, (255, 85, 85), (scx, scy), outer_r, 2)

        # Punch inner hollow
        pygame.draw.circle(scratch, (0, 0, 0, 0), (scx, scy), inner_r)
        # Punch gap between legs
        pygame.draw.rect(scratch, (0, 0, 0, 0),
                         (scx - inner_r, scy, inner_r * 2, sz - scy))

        surf.blit(scratch, (cx - scx, arch_cy - scy))

        # Chrome pole tips
        left_cx  = cx - inner_r - (outer_r - inner_r) // 2
        right_cx = cx + inner_r + (outer_r - inner_r) // 2
        arm_w    = outer_r - inner_r
        for tip_cx in (left_cx, right_cx):
            pygame.draw.rect(surf, (40, 42, 60),
                             (tip_cx - arm_w // 2 - 1, leg_bot - 4, arm_w + 2, 9),
                             border_radius=4)
            pygame.draw.rect(surf, (195, 210, 232),
                             (tip_cx - arm_w // 2,     leg_bot - 3, arm_w,     7),
                             border_radius=3)
            pygame.draw.rect(surf, (238, 246, 255),
                             (tip_cx - arm_w // 2 + 1, leg_bot - 3, arm_w - 2, 3),
                             border_radius=2)

        # Animated lightning arc between poles
        arc_y0  = leg_bot + 6
        arc_pts = [(left_cx, arc_y0)]
        for i in range(1, 6):
            t = i / 6
            x = int(left_cx + (right_cx - left_cx) * t)
            y = int(arc_y0 + math.sin(self.pulse * 11 + i * 1.7) * 4)
            arc_pts.append((x, y))
        arc_pts.append((right_cx, arc_y0))
        arc_surf = pygame.Surface((right_cx - left_cx + 8, 16), pygame.SRCALPHA)
        shifted = [(p[0] - left_cx + 4, p[1] - arc_y0 + 4) for p in arc_pts]
        if len(shifted) >= 2:
            pygame.draw.lines(arc_surf, (100, 195, 255, 200), False, shifted, 2)
        surf.blit(arc_surf, (left_cx - 4, arc_y0 - 4))

    def _draw_slowmo(self, surf):
        cx = int(self.x)
        cy = int(self.y + math.sin(self.pulse * 0.7) * 3)
        R = POWERUP_R  # 14

        # Clock face on scratch SRCALPHA surface for clean edges
        PAD = 2
        D = (R + PAD) * 2
        g = pygame.Surface((D, D), pygame.SRCALPHA)
        gc = (D // 2, D // 2)

        # Outer shadow ring
        pygame.draw.circle(g, (15, 0, 35, 200), gc, R + 1)
        # Bezel: two rings for a bevelled metallic look
        pygame.draw.circle(g, (195, 135, 255, 255), gc, R)
        pygame.draw.circle(g, (130, 70, 195, 255), gc, R - 1)
        # Deep purple face
        pygame.draw.circle(g, (42, 10, 70, 255), gc, R - 2)
        # Slightly lighter inner face
        pygame.draw.circle(g, (62, 20, 98, 255), gc, R - 4)

        # Top-left specular highlight
        hl = pygame.Surface((D, D), pygame.SRCALPHA)
        pygame.draw.circle(hl, (255, 230, 255, 60), (gc[0] - 2, gc[1] - 3), R - 5)
        g.blit(hl, (0, 0))

        # Tick marks: 4 major (every 3rd) + 8 minor
        for i in range(12):
            ang = math.pi * 2 * i / 12 - math.pi / 2
            major = (i % 3 == 0)
            r_out = R - 2
            r_in  = r_out - (3 if major else 2)
            x1 = gc[0] + math.cos(ang) * r_out
            y1 = gc[1] + math.sin(ang) * r_out
            x2 = gc[0] + math.cos(ang) * r_in
            y2 = gc[1] + math.sin(ang) * r_in
            col = (230, 200, 255, 240) if major else (165, 125, 210, 160)
            pygame.draw.line(g, col, (int(x1), int(y1)), (int(x2), int(y2)),
                             2 if major else 1)

        # Hour hand — short, thick, slow
        hr_ang = self.pulse * 0.15 - math.pi / 2
        hx = int(gc[0] + math.cos(hr_ang) * (R - 7))
        hy = int(gc[1] + math.sin(hr_ang) * (R - 7))
        pygame.draw.line(g, (250, 225, 255, 255), gc, (hx, hy), 3)

        # Minute hand — long, thinner
        min_ang = self.pulse * 1.1 - math.pi / 2
        mx = int(gc[0] + math.cos(min_ang) * (R - 4))
        my = int(gc[1] + math.sin(min_ang) * (R - 4))
        pygame.draw.line(g, (200, 155, 255, 255), gc, (mx, my), 2)

        # Sweep hand — thinnest, amber, fastest (adds drama)
        sec_ang = self.pulse * 3.8 - math.pi / 2
        sx = int(gc[0] + math.cos(sec_ang) * (R - 3))
        sy = int(gc[1] + math.sin(sec_ang) * (R - 3))
        pygame.draw.line(g, (255, 185, 60, 215), gc, (sx, sy), 1)

        # Center pin
        pygame.draw.circle(g, (255, 240, 255, 255), gc, 2)
        pygame.draw.circle(g, (155, 95, 220, 255), gc, 1)

        surf.blit(g, (cx - D // 2, cy - D // 2))


    def _draw_kfc(self, surf):
        cx = int(self.x)
        cy = int(self.y + math.sin(self.pulse * 0.9) * 2.5)
        r  = POWERUP_R + 2

        # KFC logo (real image, pre-scaled & circle-clipped)
        logo = _get_kfc_sprite()
        surf.blit(logo, (cx - logo.get_width() // 2, cy - logo.get_height() // 2))

    def _draw_ghost(self, surf):
        cx = int(self.x)
        # Supernatural wafting bob: two overlaid frequencies
        cy = int(self.y + math.sin(self.pulse * 0.9) * 4
                        + math.sin(self.pulse * 1.8) * 1.5)
        sprite = _get_ghost_sprite()
        # Sprite was built so the head-circle centre sits at sprite-local
        # (_GHOST_HEAD_OFFSET_X, _GHOST_HEAD_OFFSET_Y); align it to (cx, cy).
        surf.blit(sprite,
                  (cx - _GHOST_HEAD_OFFSET_X, cy - _GHOST_HEAD_OFFSET_Y))


    def _draw_grow(self, surf):
        cx = int(self.x)
        cy = int(self.y + math.sin(self.pulse * 1.2) * 2)

        GREEN_HI  = ( 50, 220, 100)
        GREEN_MID = ( 38, 190,  85)
        GREEN_OUT = ( 28, 160,  70)

        # ── Tall green block-arrow as the backdrop ──────────────────────────
        head_w  = 22
        shaft_w = 9
        total_h = 32
        head_h  = int(total_h * 0.42)
        top_y    = cy - total_h // 2
        head_bot = top_y + head_h
        bot_y    = cy + total_h // 2
        pts_out = [
            (cx,                  top_y),
            (cx + head_w // 2,    head_bot),
            (cx + shaft_w // 2,   head_bot),
            (cx + shaft_w // 2,   bot_y),
            (cx - shaft_w // 2,   bot_y),
            (cx - shaft_w // 2,   head_bot),
            (cx - head_w // 2,    head_bot),
        ]
        pygame.draw.polygon(surf, GREEN_OUT, pts_out)
        pts_in = [
            (cx,                      top_y + 2),
            (cx + head_w // 2 - 2,    head_bot - 1),
            (cx + shaft_w // 2 - 1,   head_bot - 1),
            (cx + shaft_w // 2 - 1,   bot_y - 1),
            (cx - shaft_w // 2 + 1,   bot_y - 1),
            (cx - shaft_w // 2 + 1,   head_bot - 1),
            (cx - head_w // 2 + 2,    head_bot - 1),
        ]
        pygame.draw.polygon(surf, GREEN_HI, pts_in)
        # Highlight band on the left edge of the shaft
        pygame.draw.line(surf, GREEN_MID,
                         (cx - shaft_w // 2 + 2, head_bot + 1),
                         (cx - shaft_w // 2 + 2, bot_y - 2), 2)

        # ── Real in-game parrot, scaled down, on top of the arrow ───────────
        bird = _get_grow_parrot()
        surf.blit(bird, (cx - bird.get_width() // 2, cy - bird.get_height() // 2))

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


# ── CloudPuff ────────────────────────────────────────────────────────────────

class CloudPuff:
    """Expanding, fading cloud circle for the transformation poof effect.
    Uses normal alpha blend (not additive) so it looks like white smoke."""
    __slots__ = ("x", "y", "vx", "vy", "life", "life_max", "r_start", "r_end", "color")

    def __init__(self, x, y, vx, vy, life, r_start, r_end, color):
        self.x, self.y   = float(x), float(y)
        self.vx, self.vy = vx, vy
        self.life = self.life_max = life
        self.r_start, self.r_end = r_start, r_end
        self.color = color

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt

    def alive(self):
        return self.life > 0

    def draw(self, surf):
        t = max(0.0, self.life / self.life_max)          # 1→0 as puff dies
        alpha = int(200 * t)
        r = max(1, int(self.r_start + (self.r_end - self.r_start) * (1.0 - t)))
        s = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, alpha), (r + 1, r + 1), r)
        surf.blit(s, (int(self.x - r - 1), int(self.y - r - 1)))


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
    __slots__ = ("text", "x", "y", "vy", "life", "life_max", "color",
                 "size", "style", "_sparkles")

    def __init__(self, text, x, y, color, size=22, life=1.0, vy=-60,
                 style="plain"):
        self.text = text
        self.x = x
        self.y = y
        self.vy = vy
        self.life = life
        self.life_max = life
        self.color = color
        self.size = size
        self.style = style
        # Pre-computed sparkle offsets (relative to the text center) so
        # they stay stable across frames as the text floats up.
        if style == "powerup":
            rng = random.Random(hash((text, int(x), int(y))) & 0xFFFFFFFF)
            self._sparkles = [
                (rng.randint(-int(size * 1.6), int(size * 1.6)),
                 rng.randint(-int(size * 0.7), int(size * 0.7)))
                for _ in range(8)
            ]
        else:
            self._sparkles = ()

    def update(self, dt):
        self.y += self.vy * dt
        self.vy += 40.0 * dt
        self.life -= dt

    def alive(self):
        return self.life > 0

    def draw(self, surf):
        if self.style == "powerup":
            self._draw_powerup(surf)
        else:
            self._draw_plain(surf)

    def _draw_plain(self, surf):
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

    def _draw_powerup(self, surf):
        """Bold gradient fill + thick dark outline + sparkle dots, with the
        gradient derived from `self.color` so each power-up keeps its own
        identity color."""
        life_t = max(0.0, self.life / self.life_max)
        alpha = int(255 * min(1.0, life_t * 2))
        font = _get_float_font(self.size)
        text_surf = font.render(self.text, True, (255, 255, 255))
        bw, bh = text_surf.get_size()
        pad = max(8, self.size // 3)
        comp = pygame.Surface((bw + pad * 2, bh + pad * 2), pygame.SRCALPHA)
        cx = comp.get_width() // 2
        cy = comp.get_height() // 2

        # Drop shadow.
        shadow = font.render(self.text, True, NEAR_BLACK)
        shadow.set_alpha(150)
        comp.blit(shadow, (cx - bw // 2 + 3, cy - bh // 2 + 4))

        # Thick dark outline derived from the base color (lerped toward black).
        col = self.color
        outline_col = (col[0] // 4, col[1] // 4, col[2] // 4)
        outline = font.render(self.text, True, outline_col)
        for ox, oy in ((-3, 0), (3, 0), (0, -3), (0, 3),
                       (-2, -2), (2, -2), (-2, 2), (2, 2)):
            comp.blit(outline, (cx - bw // 2 + ox, cy - bh // 2 + oy))

        # Vertical gradient fill (lighter top → base color bottom),
        # masked to the text shape.
        top_col = (
            int(col[0] + (255 - col[0]) * 0.4),
            int(col[1] + (255 - col[1]) * 0.4),
            int(col[2] + (255 - col[2]) * 0.4),
        )
        grad = pygame.Surface((bw, bh), pygame.SRCALPHA)
        for yy in range(bh):
            t = yy / max(1, bh - 1)
            cc = (
                int(top_col[0] + (col[0] - top_col[0]) * t),
                int(top_col[1] + (col[1] - top_col[1]) * t),
                int(top_col[2] + (col[2] - top_col[2]) * t),
            )
            pygame.draw.line(grad, cc, (0, yy), (bw, yy))
        mask = font.render(self.text, True, (255, 255, 255))
        grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        comp.blit(grad, (cx - bw // 2, cy - bh // 2))

        # Sparkle dots.
        for sx, sy in self._sparkles:
            pygame.draw.circle(comp, (255, 240, 200), (cx + sx, cy + sy), 2)
            pygame.draw.circle(comp, (255, 255, 255), (cx + sx, cy + sy), 1)

        comp.set_alpha(alpha)
        rect = comp.get_rect(center=(int(self.x), int(self.y)))
        surf.blit(comp, rect.topleft)
