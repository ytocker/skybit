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
    BACKFLIP_DURATION, DEATH_FADE_DURATION, RAIL_ABOVE_FINIAL,
    GEYSER_W, GEYSER_H, GEYSER_TELEGRAPH,
    GEYSER_ACTIVE_HOT, GEYSER_ACTIVE_COLD,
    GEYSER_DORMANT_HOT, GEYSER_DORMANT_COLD,
)
from game.draw import (
    blit_glow,
    rounded_rect, lerp_color,
    COIN_GOLD, COIN_DARK,
    MUSH_CAP, MUSH_CAP2, MUSH_SPOT, MUSH_STEM,
    PARTICLE_GOLD, PARTICLE_ORNG, PARTICLE_WHT, PARTICLE_CRIM,
    NEAR_BLACK, WHITE,
)
from game import parrot
from game import snow_fx
from game.store_catalog import CATALOG as _CATALOG
from game.pillar_pagodas import (draw_pillar_pair,
                                 CANDIDATES, VARIANT_KEYS, VARIANT_COUNT)

# Cached filled-circle masks (one per integer radius) for pagoda mask collision.
_CIRCLE_MASKS: dict = {}

def _circle_mask(r):
    r = max(1, int(round(r)))
    m = _CIRCLE_MASKS.get(r)
    if m is None:
        s = pygame.Surface((r * 2 + 1, r * 2 + 1), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 255, 255, 255), (r, r), r)
        m = pygame.mask.from_surface(s, 50)
        _CIRCLE_MASKS[r] = m
    return m
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


# ── GROW power-up icon (velvet witch-hat) ────────────────────────────────────
# Tall conical Liberty-Cap silhouette with a curled scalloped rim, slim
# bulbed ivory stem, cream ornaments. Body is static — built once at 5×
# supersample then smoothscaled and cached. The pulsing halo behind it is
# redrawn each frame.

_GROW_SS = 5                                 # supersample factor
_GROW_CAP_W, _GROW_CAP_H = 22, 24            # cap footprint in display px
_GROW_STEM_W, _GROW_STEM_H = 20, 22          # stem footprint in display px
_GROW_VELVET_OUTLINE = ( 60,  15,  25)
_GROW_VELVET_RIM_HI  = (220, 120, 130)
_GROW_VELVET_SHEEN   = (220, 130, 150, 130)
_GROW_SPOT_HALO      = (195, 165, 110)
_GROW_SPOT_HI        = (255, 250, 220)
_GROW_STEM_OUTLINE   = (150, 120,  90)
_GROW_STEM_HI        = (255, 250, 230)
_GROW_HALO_RGB       = (180,  90, 110)
_GROW_HALO_RADIUS    = 46                    # round-8 V3 pick

# Spot positions as fractions of (CAP_W, CAP_H) — same canonical layout
# the picker rounds used for the witch-hat family.
_GROW_ORNAMENT_SLOTS = (
    (0.50, 0.18),
    (0.62, 0.42),
    (0.40, 0.62),
    (0.70, 0.72),
)

# Cone polygon vertex helpers (computed at SS resolution).
def _grow_cone_outline_pts():
    SS = _GROW_SS
    W, H = _GROW_CAP_W, _GROW_CAP_H
    return [
        (W // 2 * SS, 0),
        (int(W * 0.86 * SS), int(H * 0.78 * SS)),
        (int(W * 0.95 * SS), int(H * 0.92 * SS)),
        (int(W * 0.05 * SS), int(H * 0.92 * SS)),
        (int(W * 0.14 * SS), int(H * 0.78 * SS)),
    ]

def _grow_cone_body_pts():
    SS = _GROW_SS
    W, H = _GROW_CAP_W, _GROW_CAP_H
    return [
        (W // 2 * SS, 1 * SS),
        (int(W * 0.82 * SS), int(H * 0.78 * SS)),
        (int(W * 0.91 * SS), int(H * 0.90 * SS)),
        (int(W * 0.09 * SS), int(H * 0.90 * SS)),
        (int(W * 0.18 * SS), int(H * 0.78 * SS)),
    ]

def _grow_cone_hi_pts():
    SS = _GROW_SS
    W, H = _GROW_CAP_W, _GROW_CAP_H
    return [
        (W // 2 * SS - 1 * SS,           1 * SS),
        (int(W * 0.32 * SS),             int(H * 0.55 * SS)),
        (int(W * 0.22 * SS),             int(H * 0.85 * SS)),
        (int(W * 0.34 * SS),             int(H * 0.85 * SS)),
        (int(W * 0.42 * SS),             int(H * 0.55 * SS)),
    ]


_grow_body_sprite: "pygame.Surface | None" = None
_grow_body_offset: "tuple[int, int] | None" = None

def _get_grow_body_sprite() -> "tuple[pygame.Surface, int, int]":
    """Build the static witch-hat body sprite (cap + stem + sheen + spots)
    once, return it plus the (dx, dy) offset from the powerup centre to
    the sprite's top-left corner."""
    global _grow_body_sprite, _grow_body_offset
    if _grow_body_sprite is not None and _grow_body_offset is not None:
        return _grow_body_sprite, _grow_body_offset[0], _grow_body_offset[1]

    SS = _GROW_SS
    CAP_W, CAP_H = _GROW_CAP_W, _GROW_CAP_H
    STEM_W, STEM_H = _GROW_STEM_W, _GROW_STEM_H

    # Sprite footprint: cap (22 wide × 24 tall) sits above stem
    # (20 wide × 22 tall). Stem extends below the cap base by a few px.
    # Origin (0,0) of the sprite corresponds to the top-left of the cap.
    sprite_w = max(CAP_W, STEM_W) + 2
    sprite_h = CAP_H + STEM_H + 4
    big = pygame.Surface((sprite_w * SS, sprite_h * SS), pygame.SRCALPHA)

    # Cap origin at (1, 0) in display coords → (1*SS, 0) in big coords.
    cap_ox = 1 * SS
    cap_oy = 0

    # Stem origin at (2, CAP_H + 2) in display coords (centred under cap).
    stem_ox = 2 * SS
    stem_oy = (CAP_H + 2) * SS

    # ── Stem ──────────────────────────────────────────────────────────
    stem_pts = [
        (8 * SS,  0 * SS),
        (12 * SS, 0 * SS),
        (13 * SS, 12 * SS),
        (15 * SS, 18 * SS),
        (10 * SS, 21 * SS),
        ( 5 * SS, 18 * SS),
        ( 7 * SS, 12 * SS),
    ]
    stem_pts_offset = [(p[0] + stem_ox, p[1] + stem_oy) for p in stem_pts]
    pygame.draw.polygon(big, MUSH_STEM,           stem_pts_offset)
    pygame.draw.polygon(big, _GROW_STEM_OUTLINE,  stem_pts_offset, width=SS)
    pygame.draw.line(
        big, _GROW_STEM_HI,
        (9 * SS + stem_ox, 2 * SS + stem_oy),
        (9 * SS + stem_ox, 18 * SS + stem_oy), SS,
    )

    # ── Cap (cone) ────────────────────────────────────────────────────
    def _shift(pts, ox, oy):
        return [(p[0] + ox, p[1] + oy) for p in pts]

    pygame.draw.polygon(big, _GROW_VELVET_OUTLINE,
                        _shift(_grow_cone_outline_pts(), cap_ox, cap_oy))
    pygame.draw.polygon(big, MUSH_CAP,
                        _shift(_grow_cone_body_pts(),    cap_ox, cap_oy))
    pygame.draw.polygon(big, MUSH_CAP2,
                        _shift(_grow_cone_hi_pts(),      cap_ox, cap_oy))

    # Curled scalloped rim
    rim_w = int(CAP_W * 0.86 * SS)
    rim_x = int(CAP_W * 0.07 * SS) + cap_ox
    rim_y = int(CAP_H * 0.93 * SS) + cap_oy
    rim_count = 5
    curl_w = rim_w // rim_count
    for i in range(rim_count):
        center = (rim_x + i * curl_w + curl_w // 2, rim_y)
        pygame.draw.circle(big, MUSH_CAP,             center, curl_w // 2)
        pygame.draw.circle(big, _GROW_VELVET_OUTLINE, center, curl_w // 2, SS)
        pygame.draw.circle(big, _GROW_VELVET_RIM_HI,
                           (center[0] - curl_w // 5, center[1] - curl_w // 5),
                           max(1, curl_w // 4))

    # Velvet inner sheen blob — alpha ellipse masked to the cone shape.
    sheen = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.ellipse(sheen, _GROW_VELVET_SHEEN,
                        pygame.Rect(int(CAP_W * 0.34 * SS) + cap_ox,
                                    int(CAP_H * 0.16 * SS) + cap_oy,
                                    int(CAP_W * 0.20 * SS),
                                    int(CAP_H * 0.42 * SS)))
    cone_mask = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(cone_mask, (255, 255, 255, 255),
                        _shift(_grow_cone_body_pts(), cap_ox, cap_oy))
    sheen.blit(cone_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    big.blit(sheen, (0, 0))

    # Cream-butter spots
    for fx_frac, fy_frac in _GROW_ORNAMENT_SLOTS:
        fx = int(CAP_W * fx_frac * SS) + cap_ox
        fy = int(CAP_H * fy_frac * SS) + cap_oy
        r_body = 2.0
        pygame.draw.circle(big, _GROW_SPOT_HALO, (fx, fy),
                           int((r_body + 0.4) * SS))
        pygame.draw.circle(big, MUSH_SPOT, (fx, fy), int(r_body * SS))
        pygame.draw.circle(big, _GROW_SPOT_HI,
                           (fx - SS // 2, fy - SS // 2), max(1, SS // 2))

    sprite = pygame.transform.smoothscale(big, (sprite_w, sprite_h))

    # Offset from the in-world (cx, cy) anchor to the sprite's top-left.
    # The original mushroom anchor placed the cap at (cx - 15, cy - 12)
    # and the stem at (cx - 7, cy). The new icon centres the cap
    # horizontally on cx and lets the stem hang from there. We want the
    # icon's centre of mass roughly aligned with (cx, cy) so the existing
    # POWERUP_R collision feels right.
    dx = -sprite_w // 2 + 1                              # centre horizontally
    dy = -CAP_H + 2                                       # cap top above cy
    _grow_body_sprite = sprite
    _grow_body_offset = (dx, dy)
    return sprite, dx, dy


def _draw_grow_halo(surf, cx, cy, pulse,
                    color_rgb=_GROW_HALO_RGB,
                    radius=_GROW_HALO_RADIUS,
                    falloff=2.2,
                    peak_y_off=-2):
    """Smooth radial halo (~60 concentric circles, quadratic falloff).
    `pulse` drives the brightness pulse; same curve as the picker rounds."""
    pulse_t = 0.5 + 0.5 * math.sin(pulse * 1.2)
    max_alpha = int(140 + 25 * pulse_t)
    steps = max(60, radius * 2)
    w = radius * 2 + 4
    halo = pygame.Surface((w, w), pygame.SRCALPHA)
    hcx = hcy = w // 2
    for i in range(steps):
        r = max(0, radius - (i * radius) // steps)
        if r <= 0:
            break
        t = i / max(1, steps - 1)
        a = int(max_alpha * (t ** falloff))
        if a > 0:
            pygame.draw.circle(halo, (*color_rgb, a), (hcx, hcy), r)
    surf.blit(halo, (cx - hcx, cy - hcy + peak_y_off))


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
# 0.5-px black hairline outline + crisp eyes + soft sheen.
_ghost_sprite: "pygame.Surface | None" = None
_GHOST_HEAD_OFFSET_X = 16   # head-circle centre x in the sprite
_GHOST_HEAD_OFFSET_Y = 14   # head-circle centre y in the sprite


def _get_ghost_sprite() -> "pygame.Surface":
    global _ghost_sprite
    if _ghost_sprite is not None:
        return _ghost_sprite

    SS = 16                                   # high-res super-sample for
                                              # genuinely smooth perimeter
    PAD = 2
    GW, GH = (28 + PAD * 2), (36 + PAD * 2)   # 32 × 40 final-px
    sw, sh = GW * SS, GH * SS
    big = pygame.Surface((sw, sh), pygame.SRCALPHA)

    # Geometry in supersampled units
    gcx = (14 + PAD) * SS
    gcy = (12 + PAD) * SS
    hr  = 12 * SS
    body_y2 = (26 + PAD) * SS

    # Build the full silhouette as a SINGLE perimeter polygon (head
    # semicircle → right side → angular scallop → left side). This lets
    # us stroke the outline with a fast line+circle pass instead of the
    # offset-stack (which scales O(SS²) and would be ~1 G pixel-ops at
    # SS=16). Same angular V-bumps as before, just rendered cleanly.
    perimeter = []
    n_arc = 64                                # head arc resolution
    for i in range(n_arc + 1):
        theta = math.pi - i * math.pi / n_arc
        x = gcx + hr * math.cos(theta)
        y = gcy - hr * math.sin(theta)
        perimeter.append((int(x), int(y)))
    # Right side down to body bottom
    perimeter.append((gcx + hr, body_y2))
    # Angular scallop — symmetric, uniform-width waves, traced
    # right-to-left through 7 control points.
    bump_y   = (GH - 4) * SS
    indent_y = body_y2 + 4 * SS
    x_left   = (1 + PAD) * SS
    x_right  = (28 - 2 + PAD) * SS
    span_x   = x_right - x_left
    scallop_lr = [
        (x_left + i * span_x // 6,
         body_y2 if i in (0, 6) else (bump_y if i % 2 == 1 else indent_y))
        for i in range(7)
    ]
    perimeter.extend(reversed(scallop_lr))
    # Left side back up to head's leftmost point
    perimeter.append((gcx - hr, gcy))

    OUTLINE_COLOR = (0, 0, 0)
    # 0.5-px hairline. SS=16 means t_big=8 super-pixels = exactly 0.5 final
    # pixels of visible outline (line stroke runs both sides of the
    # perimeter; the inner half is covered by the gradient blit below, so
    # only the outer half is visible).
    THICKNESS_PX  = 0.5
    t_big = int(THICKNESS_PX * SS)

    # 1) Outline ring — stroke each perimeter edge as a thick line, plus a
    #    circle at every vertex so corners join cleanly without gaps. This
    #    is O(N) in perimeter length, not O(SS²) like the offset-stack.
    for i in range(len(perimeter)):
        p1 = perimeter[i]
        p2 = perimeter[(i + 1) % len(perimeter)]
        pygame.draw.line(big, OUTLINE_COLOR, p1, p2, t_big * 2)
    for p in perimeter:
        pygame.draw.circle(big, OUTLINE_COLOR, p, t_big)

    # 2) Silhouette mask — single filled polygon traced from the same
    #    perimeter, so it lines up with the outline ring above to the pixel.
    mask = pygame.Surface((sw, sh), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), perimeter)

    # 3) Holographic foil body — diagonal multi-stop gradient. Build a
    #    1-D gradient strip of length sw+sh once, then per row blit a
    #    sw-wide slice of it starting at offset y. Avoids per-pixel
    #    set_at over the full sw×sh canvas.
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

# Static skateboard-mode sprites — built once, then only transformed per frame.
# The helmet + board base were rebuilt from an 8x/4x supersample EVERY frame
# (twice, via the HUD re-blit) while riding; caching them removes that cost.
_HELMET_SPRITE = None
_HELMET_SCALED: dict = {}    # per grow/shrink scale bucket -> scaled helmet
_SKATE_HAT_SPRITE = None     # skate+3x gold bunny top-hat
_SKATE_HAT_SCALED: dict = {}
_BOARD_BASE = None          # native board sprite, no wheel-spokes
_BOARD_WHEELS = None        # native-space [(wx, wy, wr, sign), ...] for the spokes
_SKATE_ICON_SPRITE = None   # genie skateboard-offer pickup token


class Bird:
    def __init__(self):
        self.x = BIRD_X
        self.y = H * 0.42
        self.vy = 0.0
        self.alive = True
        self.frame_t = 0.0
        # Cosmetic loadout from the coin store (synced per run from store_data);
        # the equipped skin is the base look the power-up cascade draws over,
        # and equipped_parcel swaps the gift Pip carries.
        self.equipped_skin = "skin_base"
        self.equipped_parcel = "parcel_base"
        self._skin_combos_built_for: "str | None" = None
        self.flap_boost = 0.0
        self.kfc_active = False
        self.ghost_active = False
        self.grow_active = False
        self.triple_active = False
        self.ghost_pulse = 0.0    # advances while ghost_active for fade effect
        # Shrink: collision-relevant flag flips at activation; the
        # visible sprite scale eases between 1.0 and SHRINK_SCALE over
        # SHRINK_TRANSITION seconds so the morph reads on screen.
        self.shrink_active = False
        self.shrink_scale = 1.0
        # Cart / rail state. cart_active gates pipe-spawn suppression
        # and the rail-pillar bookkeeping; cart_locked gates the
        # RAIL_SCROLL_MULT scroll boost and means Pip is physically on
        # the cart. Both clear at _end_rail_ride.
        self.cart_active = False
        self.cart_locked = False
        # Local slope of the rail segment Pip is currently riding,
        # written by World._snap_cart_to_rail. Drives the cart sprite
        # rotation in scenes._draw_cart_on_bird so the wagon tilts
        # with the polyline curvature.
        self.cart_tilt_deg = 0.0
        # Secret late-game powerup flags (timer state lives on World).
        self.skateboard_active = False
        self.knight_active = False
        # Poison trap (genie-only). poison_t ramps 0 -> 1 over
        # POISON_DURATION seconds while poison_active; World watches for
        # the terminal 1.0 and fires _die(). Bird.draw cross-fades from
        # the healthy sprite to the dead-Pip-B sprite at alpha = poison_t.
        self.poison_active = False
        self.poison_t = 0.0
        self.umbrella_active = False
        # SKATEBOARD tricks: each is a timed state ticked down in
        # `tick`. The trick palette is resolved by tap-pattern in
        # World._track_skateboard_tricks. The bird-side visual for
        # kickflip / heelflip / pop-shuvit currently piggybacks on the
        # backflip 360° spin; the TrickBubble pop-art badge is what
        # signals which trick landed.
        self.backflip_t = 0.0
        self.backflip_dur = BACKFLIP_DURATION
        self.kickflip_t = 0.0
        self.kickflip_dur = 0.0
        self.heelflip_t = 0.0
        self.heelflip_dur = 0.0
        self.popshuvit_t = 0.0
        self.popshuvit_dur = 0.0
        # Set on landing a grind (nose / tail / None). World latches
        # this on slide-start and clears on slide-end so the trick
        # bubble only fires once per grind, not every frame.
        self.grind_type: str | None = None
        # Death cross-fade: counts up from 0 to DEATH_FADE_DURATION at
        # the collision moment; Bird.draw alpha-blends the dead palette
        # on top of the alive sprite while this is in flight.
        self.death_fade_t = 0.0
        # i-frame flicker synced from World.update: False on the "hidden"
        # half of each LIVES_FLICKER_HZ period while lives_invuln > 0.
        self.lives_flicker_visible = True
        self.on_last_life = False
        self.on_first_hit = False

        # Weather event state (visual-only):
        #   wind_lean       — rightward x-offset under the predawn tailwind
        #   snow_load       — 0..1 windblown snow accumulated on Pip (squall)
        #   skeleton_flash_t — X-Ray Sparks timer set when lightning strikes
        self.wind_lean = 0.0
        self.snow_load = 0.0
        self.skeleton_flash_t = 0.0
        # Rain shiver (visual-only) + flap dampen (real, the "wind pushes
        # me down" cue) under heavy rain. Written by World._apply_weather_effects.
        self.shiver_x = 0.0
        self.shiver_y = 0.0
        self.flap_dampen = 0.0

    @property
    def tilt_deg(self):
        # Clamp the downward dive so a fast-falling bird doesn't read as
        # already crashing (REVIEW.md feedback).
        t = max(-0.5, min(0.75, self.vy / 500.0))
        base = -t * 55.0
        # GRIND lean: while Pip is locked into a nose / tail grind, pitch
        # the whole body so it matches the board's wheel that's on the
        # rail. Nose grind = front wheel down, body pitches forward.
        # Tail grind = back wheel down, body pitches back.
        if self.grind_type == "nose":
            base += -18.0
        elif self.grind_type == "tail":
            base += 18.0
        # During a backflip, ride a full 360° rotation on top of the base
        # tilt. Smootherstep easing (6t⁵−15t⁴+10t³) eases in and out and
        # closes the loop to ~0° at the last frame; the velocity-banked
        # term blends out so Pip lands flat rather than nose-down.
        if self.backflip_t > 0 and self.backflip_dur > 0:
            p = 1.0 - self.backflip_t / self.backflip_dur
            eased = p * p * p * (p * (p * 6.0 - 15.0) + 10.0)
            return base * (1.0 - eased) + eased * 360.0
        return base

    def flap(self, gravity_sign=1):
        # Poison expiry: once the timer is up Pip loses flap control and
        # dives under gravity until he collides with something (ground or
        # pillar) and the normal death pipeline takes over.
        if self.poison_active and self.poison_t >= 1.0:
            return
        if self.alive:
            # Heavy rain dampens lift slightly — the "wind pushing me
            # down" cue (flap_dampen is 0 outside heavy weather).
            self.vy = FLAP_V * gravity_sign * (1.0 - self.flap_dampen)
            self.flap_boost = 0.45

    def rebuild_skin_combos(self) -> None:
        """Pre-bake power-up composites for the currently equipped skin.

        Called once at run-start so tint ops don't spike during gameplay
        (especially critical on WASM where tinting runs 4-8x slower).
        No-ops for skin_base — the bespoke cascade handles the base macaw.
        """
        parrot.build_skin_powerup_composites(self.equipped_skin)
        self._skin_combos_built_for = self.equipped_skin

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
        self.backflip_t = max(0.0, self.backflip_t - dt)
        self.kickflip_t = max(0.0, self.kickflip_t - dt)
        self.heelflip_t = max(0.0, self.heelflip_t - dt)
        self.popshuvit_t = max(0.0, self.popshuvit_t - dt)
        if self.poison_active:
            from game.config import POISON_DURATION
            self.poison_t = min(1.0, self.poison_t + dt / POISON_DURATION)
        if self.ghost_active:
            self.ghost_pulse += dt * 2.4
        # X-Ray Sparks flash decays over its 3.5 s window (set by the
        # storm-jolt lightning strike).
        self.skeleton_flash_t = max(0.0, self.skeleton_flash_t - dt)
        # Ease shrink_scale toward its target (SHRINK_SCALE while active,
        # 1.0 otherwise) over SHRINK_TRANSITION seconds. Collisions snap on
        # frame 1 via World.bird_radius — only the visible sprite eases.
        from game.config import SHRINK_SCALE, SHRINK_TRANSITION
        target = SHRINK_SCALE if self.shrink_active else 1.0
        if self.shrink_scale != target:
            step = (1.0 - SHRINK_SCALE) * dt / SHRINK_TRANSITION
            if self.shrink_scale > target:
                self.shrink_scale = max(target, self.shrink_scale - step)
            else:
                self.shrink_scale = min(target, self.shrink_scale + step)

    def draw(self, surf, shake_x=0, shake_y=0, flipped=False):
        # Weather visual offsets (collision unaffected): tailwind pushes
        # Pip rightward; heavy-rain shiver jitters him.
        shake_x += self.wind_lean + self.shiver_x
        shake_y += self.shiver_y
        frame_idx = int(self.frame_t) % len(parrot.FRAMES)
        # When flipped (reverse-gravity buff), negate the tilt so a rising
        # bird's head still leads in the direction of motion after the
        # vertical mirror is applied below.
        tilt = -self.tilt_deg if flipped else self.tilt_deg
        # X-Ray Sparks (storm-jolt strike): a 3.5 s flash where Pip strobes
        # between his skeleton and his normal sprite — first 0.5 s a solid
        # skeleton hold, then 3.0 s of strobe at 0.30 s per segment.
        skeleton_visible = False
        if self.skeleton_flash_t > 0.0:
            if self.skeleton_flash_t > 3.0:
                skeleton_visible = True
            else:
                bucket = int((3.0 - self.skeleton_flash_t) / 0.30)
                skeleton_visible = (bucket % 2 == 0)
        # While skateboarding the punk helmet owns the head, so suppress the
        # 3x top-hat in the SPRITE pick (otherwise hat + helmet double-stack).
        triple_vis = self.triple_active and not self.skateboard_active
        # Combo-aware sprite cascade. Every reachable stack has a dedicated
        # themed sprite so no powerup is silently lost. KNIGHT is a first-class
        # axis checked BEFORE the coin-buff skins so its armour is never
        # dropped when 3x/KFC/Ghost overlap it (the overlapping buff still
        # reads via its own world FX; bespoke knight+combo skins land in later
        # phases). Cascade order: skeleton > knight > kfc/ghost/triple combos
        # > singles > grow > base, with poison applied as a tint afterward.
        if skeleton_visible:
            img = parrot.get_skeleton_parrot(frame_idx, tilt)
        elif self.knight_active and self.kfc_active and self.ghost_active and triple_vis:
            img = parrot.get_knight_kfc_ghost_hat_parrot(frame_idx, tilt)
        elif self.knight_active and self.kfc_active and self.ghost_active:
            img = parrot.get_knight_kfc_ghost_parrot(frame_idx, tilt)
        elif self.knight_active and self.kfc_active and triple_vis:
            img = parrot.get_knight_kfc_hat_parrot(frame_idx, tilt)
        elif self.knight_active and self.ghost_active and triple_vis:
            img = parrot.get_knight_ghost_hat_parrot(frame_idx, tilt)
        elif self.knight_active and self.kfc_active:
            img = parrot.get_knight_kfc_parrot(frame_idx, tilt)
        elif self.knight_active and self.ghost_active:
            img = parrot.get_knight_ghost_parrot(frame_idx, tilt)
        elif self.knight_active and triple_vis:
            img = parrot.get_knight_hat_parrot(frame_idx, tilt)
        elif self.knight_active:
            img = parrot.get_knight_parrot(frame_idx, tilt)
        elif self.ghost_active and triple_vis and self.on_last_life:
            img = parrot.get_skin_ghost_hat_hurt_frame(self.equipped_skin, frame_idx, tilt)
        elif self.ghost_active and triple_vis and self.on_first_hit:
            img = parrot.get_skin_ghost_hat_first_hit_frame(self.equipped_skin, frame_idx, tilt)
        elif self.ghost_active and self.on_last_life:
            img = parrot.get_skin_ghost_hurt_frame(self.equipped_skin, frame_idx, tilt)
        elif self.ghost_active and self.on_first_hit:
            img = parrot.get_skin_ghost_first_hit_frame(self.equipped_skin, frame_idx, tilt)
        elif triple_vis and self.on_last_life:
            img = parrot.get_skin_hat_hurt_frame(self.equipped_skin, frame_idx, tilt)
        elif triple_vis and self.on_first_hit:
            img = parrot.get_skin_hat_first_hit_frame(self.equipped_skin, frame_idx, tilt)
        elif self.kfc_active or self.ghost_active or triple_vis:
            # Non-knight power-up combo: try the pre-baked composite for the
            # equipped custom skin first; fall back to the bespoke base-macaw
            # sprites when no custom skin is equipped (skin_base path).
            _combo = (
                parrot.get_skin_combo_frame(
                    self.equipped_skin,
                    bool(self.kfc_active), bool(self.ghost_active), bool(triple_vis),
                    frame_idx, tilt,
                )
                if self._skin_combos_built_for == self.equipped_skin
                else None
            )
            if _combo is not None:
                img = _combo
            elif self.kfc_active and self.ghost_active and triple_vis:
                img = parrot.get_kfc_ghost_hat_parrot(frame_idx, tilt)
            elif self.kfc_active and self.ghost_active:
                img = parrot.get_kfc_ghost_parrot(frame_idx, tilt)
            elif self.kfc_active and triple_vis:
                img = parrot.get_kfc_hat_parrot(frame_idx, tilt)
            elif self.ghost_active and triple_vis:
                img = parrot.get_ghost_hat_parrot(frame_idx, tilt)
            elif self.kfc_active:
                img = parrot.get_fried_parrot(frame_idx, tilt)
            elif self.ghost_active:
                img = parrot.get_ghost_parrot(frame_idx, tilt)
            else:
                img = parrot.get_hat_parrot(frame_idx, tilt)
        elif self.grow_active and self.on_last_life:
            img = parrot.get_skin_grow_hurt_frame(self.equipped_skin, frame_idx, tilt)
        elif self.grow_active and self.on_first_hit:
            img = parrot.get_skin_grow_first_hit_frame(self.equipped_skin, frame_idx, tilt)
        elif self.grow_active:
            if self.equipped_skin == "skin_base":
                # Hi-res grow-mode bird: pre-built at full grow display size by
                # `parrot._build_grow_frame` (round-9 v3 = 3× supersample → 1.5×
                # downscale). Skips the smoothscale-up that produced the prior
                # blur. Combo modes (kfc / ghost / triple + grow) still use
                # the legacy upscale below — they pre-empt this branch.
                img = parrot.get_grow_parrot(frame_idx, tilt)
            else:
                # Costume skin: no hi-res grow variant; scale up the skin frame.
                from game.config import GROW_SCALE
                img = parrot.get_skin_frame(self.equipped_skin, frame_idx, tilt)
                iw, ih = img.get_size()
                img = pygame.transform.smoothscale(
                    img, (int(iw * GROW_SCALE), int(ih * GROW_SCALE)))
        elif self.on_last_life:
            img = parrot.get_skin_hurt_frame(self.equipped_skin, frame_idx, tilt)
        elif self.on_first_hit:
            img = parrot.get_skin_first_hit_frame(self.equipped_skin, frame_idx, tilt)
        else:
            # No power-up skin active: draw the equipped COSMETIC skin (the
            # store loadout). Unknown ids degrade to the base parrot inside
            # get_skin_frame, so a stale save never crashes the draw.
            img = parrot.get_skin_frame(self.equipped_skin, frame_idx, tilt)
        # POISON — chartreuse tint while ramping; full dead composite at peak.
        # Costume skins preserve accessories over the P_CHARTREUSE body; all
        # other skins (parrot species, animals, base) use the bespoke dead sprite.
        if self.poison_active and self.poison_t > 0.0:
            if self.poison_t >= 1.0:
                from game import store_skins
                if _CATALOG.get(self.equipped_skin, {}).get("group") == "costume":
                    img = store_skins.get_poisoned_costume_frame(
                        self.equipped_skin, frame_idx, tilt)
                else:
                    img = parrot.get_poisoned_parrot(frame_idx, tilt)
            else:
                img = parrot.tint_copy(img, (180, 225, 75),
                                       min(0.78, 0.78 * self.poison_t))
        if self.grow_active and (self.kfc_active or self.ghost_active
                                  or triple_vis or self.knight_active):
            # Combo + grow: smoothscale-up the variant sprite. No hi-res
            # combo frames yet; this preserves correctness at the cost of
            # the same upscale blur the base bird used to have.
            from game.config import GROW_SCALE
            w, h = img.get_size()
            img = pygame.transform.smoothscale(
                img, (int(w * GROW_SCALE), int(h * GROW_SCALE)))
        # Shrink eases the sprite down on top of whichever combo sprite
        # was chosen. Skipped while grow is animating up (the two buffs
        # don't stack — activator clears the other timer), but still
        # works mid-easing on activation/expiry.
        if self.shrink_scale != 1.0 and not self.grow_active:
            sw, sh = img.get_size()
            img = pygame.transform.smoothscale(
                img,
                (max(1, int(sw * self.shrink_scale)),
                 max(1, int(sh * self.shrink_scale))),
            )
        if flipped:
            img = pygame.transform.flip(img, False, True)
        if self.ghost_active and not skeleton_visible:
            # Faded breathing: alpha oscillates ~90..170 over a slow sine,
            # so the ghost reads as clearly translucent and ethereal.
            # Suppressed during the X-Ray flash so the bones read solid.
            img = img.copy()
            pulse = 0.5 + 0.5 * math.sin(self.ghost_pulse)
            img.set_alpha(int(90 + pulse * 80))
        # i-frame flicker during the post-revive lives grace window.
        if not self.lives_flicker_visible:
            img = img.copy()
            img.set_alpha(0)
        cx_int = int(self.x + shake_x)
        cy_int = int(self.y + shake_y)
        # X-Ray Sparks rim glow — a tight silhouette-edge trim
        # (outer purple → cyan → white core) traced from the sprite's
        # mask outline and drawn BEFORE the sprite so only the outer
        # half shows; pulse-modulated at ~5 Hz.
        if self.skeleton_flash_t > 0.0:
            rim_pulse = 0.5 + 0.5 * math.sin(self.frame_t * 30.0)
            try:
                sil_mask = pygame.mask.from_surface(img, threshold=20)
                outline_pts = sil_mask.outline(every=1)
                if len(outline_pts) >= 2:
                    rect_pre = img.get_rect(center=(cx_int, cy_int))
                    glow = pygame.Surface(img.get_size(), pygame.SRCALPHA)
                    for width, col in (
                        (5, (180, 100, 255)),
                        (3, (140, 220, 255)),
                        (1, (255, 255, 255)),
                    ):
                        pygame.draw.lines(glow, col, True, outline_pts, width)
                    glow.set_alpha(max(0, min(255, int(220 * (0.6 + 0.4 * rim_pulse)))))
                    surf.blit(glow, rect_pre.topleft)
            except (pygame.error, AttributeError):
                pass
        r = img.get_rect(center=(cx_int, cy_int))
        surf.blit(img, r.topleft)
        # UMBRELLA: blitted UPRIGHT (never inherits Pip's tilt) but its
        # position tracks his actual head crown — the head sprite sits offset
        # from the body centre, so a fixed screen-space anchor would drift
        # off the head whenever Pip dives/rises. Purely visual: it is NOT
        # part of the bird's collision hitbox (pillars must hit Pip's circle
        # at (self.x, self.y) with bird_radius() to count as a death).
        if self.umbrella_active:
            from game.umbrella import draw_overlay
            draw_overlay(surf, cx_int, cy_int, tilt)
        # Windblown snow on Pip during the squall — baked W2 overlay matched to
        # the sprite's rotozoom(tilt) + body scale, so it stays glued on. Pass
        # the current frame so the full-cover peak buries the actual wing pose.
        if self.snow_load > 0.04 and not skeleton_visible:
            ov = snow_fx.get_snow_overlay(self.snow_load, frame_idx)
            if ov is not None:
                from game.config import GROW_SCALE as _GS
                bsc = (_GS if self.grow_active else 1.0) * self.shrink_scale
                # Rotate by the SAME 3°-quantised tilt get_parrot uses, so the
                # snow stays glued to the sprite (raw tilt jittered the head).
                q = int(round(tilt / 3.0)) * 3
                ov = pygame.transform.rotozoom(ov, q, bsc)
                if flipped:
                    ov = pygame.transform.flip(ov, False, True)
                rs = ov.get_rect(center=(cx_int, cy_int))
                surf.blit(ov, rs.topleft)
        # X-Ray Sparks arcs — jagged cyan/white mini-bolts discharging
        # outward from Pip's silhouette while the flash is active.
        if self.skeleton_flash_t > 0.0:
            inner_r = 20.0
            for _k in range(5):
                ang = random.uniform(0, math.tau)
                ox = cx_int + math.cos(ang) * inner_r
                oy = cy_int + math.sin(ang) * inner_r
                end_r = inner_r + random.uniform(10, 14)
                ex = cx_int + math.cos(ang) * end_r
                ey = cy_int + math.sin(ang) * end_r
                mid_r = (inner_r + end_r) * 0.5
                perp = ang + math.pi / 2
                jitter = random.uniform(-3.5, 3.5)
                mx = cx_int + math.cos(ang) * mid_r + math.cos(perp) * jitter
                my = cy_int + math.sin(ang) * mid_r + math.sin(perp) * jitter
                pts = ((int(ox), int(oy)), (int(mx), int(my)), (int(ex), int(ey)))
                pygame.draw.lines(surf, (140, 220, 255), False, pts, 3)
                pygame.draw.lines(surf, (255, 255, 255), False, pts, 1)
                pygame.draw.circle(surf, (255, 255, 255), (int(ex), int(ey)), 2)
                pygame.draw.circle(surf, (140, 220, 255), (int(ex), int(ey)), 3, 1)

        # Dead-Pip cross-fade overlay: blit the dead palette on top of the
        # alive sprite at alpha = t so the silhouette stays single and the
        # palette swap reads as the same bird turning, not two layers.
        # Resized to match the current alive img so grow/shrink alignment
        # is preserved without re-running the size cascade.
        if self.death_fade_t > 0:
            t = min(1.0, self.death_fade_t / DEATH_FADE_DURATION)
            dead_raw = parrot.get_dead_parrot(
                frame_idx, tilt,
                palette_key="B", aura_scale=t,
            )
            if dead_raw.get_size() != img.get_size():
                dead_raw = pygame.transform.smoothscale(dead_raw, img.get_size())
            if flipped:
                dead_raw = pygame.transform.flip(dead_raw, False, True)
            dead_overlay = dead_raw.copy()
            dead_overlay.set_alpha(int(255 * t))
            surf.blit(dead_overlay, r.topleft)

        # SKATEBOARD — Pip wears a helmet and the parcel becomes the board
        # under his feet. Drawn instead of the normal parcel.
        if self.skateboard_active:
            hx, hy = self.x + shake_x, self.y + shake_y
            # Head-piece while skating: a knight keeps his armet (no extra
            # helmet); with 3x up Pip wears the gold '$' top-hat in the helmet's
            # bunny-eared style; otherwise the punk skull-bunny helmet.
            if self.knight_active:
                pass
            elif self.triple_active:
                self._draw_skate_hat(surf, hx, hy, flipped)
            else:
                self._draw_helmet(surf, hx, hy, flipped)
            self._draw_skateboard(surf, hx, hy, flipped)
            return

        # Parcel flickers in sync with Pip during the post-revive i-frame window.
        if not self.lives_flicker_visible:
            return

        # Parcel — Pip's permanent companion. Tucked below his centre with
        # a tilt-aware offset so it banks with him; mode-coloured to match
        # the active palette; alpha-breathes in ghost mode; grow-scaled.
        if self.ghost_active:
            mode = "ghost"
        elif self.kfc_active:
            mode = "kfc"
        elif self.triple_active:
            mode = "triple"
        else:
            mode = "normal"
        base_parcel = self.equipped_parcel in (None, "parcel_base")
        parcel = parrot.get_parcel(mode, self.equipped_parcel)
        if self.kfc_active and not base_parcel:
            parcel = parrot.get_crispy_parcel(self.equipped_parcel, parcel)
        if self.ghost_active and not base_parcel and not skeleton_visible:
            parcel = parrot.get_ghost_parcel(self.equipped_parcel)
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
        if self.ghost_active and not skeleton_visible:
            parcel_rot = parcel_rot.copy()
            parcel_rot.set_alpha(int(90 + pulse * 80))
        pr = parcel_rot.get_rect(center=(self.x + shake_x + offset.x,
                                         self.y + shake_y + offset.y))
        surf.blit(parcel_rot, pr.topleft)
        # Snow settles on the parcel too (objects get capped, not the underside)
        # — fades in only at high load, matched to the parcel's transform chain.
        # The cap is shaped for the default kraft box, so it's skipped for an
        # equipped custom parcel rather than draping box-snow over a balloon.
        if base_parcel and self.snow_load > snow_fx.PARCEL_ONSET and not skeleton_visible:
            pov = snow_fx.get_parcel_snow(mode, self.snow_load)
            if pov is not None:
                if scale != 1.0:
                    pw, ph = pov.get_size()
                    pov = pygame.transform.smoothscale(
                        pov, (int(pw * scale), int(ph * scale)))
                if flipped:
                    pov = pygame.transform.flip(pov, False, True)
                pov = pygame.transform.rotate(pov, parcel_tilt)
                ps = pov.get_rect(center=(self.x + shake_x + offset.x,
                                          self.y + shake_y + offset.y))
                surf.blit(pov, ps.topleft)

    def _draw_helmet(self, surf, cx, cy, flipped):
        """Side-view punk skater helmet. The static art is built ONCE and
        cached (_build_helmet_sprite); per frame only the tilt rotation, flip
        and seating offset vary, so the 8x supersample build never runs in the
        draw loop (it used to, twice, via the HUD re-blit)."""
        global _HELMET_SPRITE
        from game.config import GROW_SCALE
        # Track Pip's body scale so the helmet seats + sizes on a grown/shrunk
        # bird instead of staying fixed (which left a tiny helm on a big Pip).
        s = (GROW_SCALE if self.grow_active else 1.0) * self.shrink_scale
        ear_top_n = 18
        if _HELMET_SPRITE is None:
            _HELMET_SPRITE = Bird._build_helmet_sprite()
        helm = _HELMET_SPRITE
        if abs(s - 1.0) > 1e-3:
            key = round(s, 2)
            helm = _HELMET_SCALED.get(key)
            if helm is None:
                hw, hh = _HELMET_SPRITE.get_size()
                helm = pygame.transform.smoothscale(
                    _HELMET_SPRITE, (max(1, int(hw * key)), max(1, int(hh * key))))
                _HELMET_SCALED[key] = helm
        tilt = -self.tilt_deg if flipped else self.tilt_deg
        # Seating fix: the subsurface grew at the TOP by ear_top_n px, so the
        # dome's offset from the subsurface centre shifted by ear_top_n/2.
        # Pulling the blit centre away from the helmet's original-top side
        # keeps the dome at the same on-Pip y as the pre-ear shipped helmet.
        ear_compensation = (ear_top_n * s / 2.0) * (1 if flipped else -1)
        y_off = (10 * s if flipped else -10 * s) + ear_compensation
        offset = pygame.math.Vector2(18 * s, y_off)
        offset = offset.rotate(-tilt)
        rotated = pygame.transform.rotate(helm, tilt)
        if flipped:
            rotated = pygame.transform.flip(rotated, False, True)
        r = rotated.get_rect(center=(int(cx + offset.x),
                                     int(cy + offset.y)))
        surf.blit(rotated, r.topleft)

    @staticmethod
    def _build_helmet_sprite():
        """Static side-view skater helmet — 8x supersample built once."""
        s = 1.0
        SS = 8
        hw_n = int(24 * s)
        hh_n = int(15 * s)
        pad_n = 4
        drop_n = int(28 * s)
        ear_top_n = 18
        hw = hw_n * SS
        hh = hh_n * SS
        pad = pad_n * SS
        drop = drop_n * SS
        ear_top = ear_top_n * SS
        helm = pygame.Surface(
            (hw + pad * 2, hh + pad * 2 + drop + ear_top), pygame.SRCALPHA)

        BONE   = (240, 240, 230)
        DOME   = (10, 10, 18)
        CHROME = (200, 200, 210)
        RED    = (200, 50, 50)
        OUT    = (15, 15, 22)

        def Y(y):
            return y + ear_top

        full = pygame.Surface((hw, hh * 2), pygame.SRCALPHA)
        pygame.draw.ellipse(full, DOME, pygame.Rect(0, 0, hw, hh * 2))
        helm.blit(full, (pad, Y(pad)), area=pygame.Rect(0, 0, hw, hh))
        if hw > 9 * SS and hh > 5 * SS:
            hl_w = hw - 8 * SS
            hl_h = hh - 4 * SS
            hl = pygame.Surface((hl_w, hl_h), pygame.SRCALPHA)
            pygame.draw.ellipse(hl, (50, 50, 60),
                                pygame.Rect(0, 0, hl_w, hl_h))
            helm.blit(hl, (pad + 4 * SS, Y(pad + 1 * SS)),
                      area=pygame.Rect(hl_w // 2, 0,
                                       hl_w // 2, hl_h // 2 + 1))

        fin = [
            (pad + 3 * SS,             Y(pad + 1 * SS)),
            (pad + hw // 2 - 2 * SS,   Y(pad - 3 * SS)),
            (pad + hw // 2 + 3 * SS,   Y(pad - 2 * SS)),
            (pad + hw - 4 * SS,        Y(pad + 2 * SS)),
        ]
        pygame.draw.polygon(helm, BONE, fin)
        pygame.draw.polygon(helm, DOME, fin, SS)
        for sx in (pad + hw // 2 - 3 * SS, pad + hw // 2 + 2 * SS):
            spike = [(sx, Y(pad - 2 * SS)),
                     (sx + 1 * SS, Y(pad - 5 * SS)),
                     (sx + 2 * SS, Y(pad - 2 * SS))]
            pygame.draw.polygon(helm, BONE, spike)
            pygame.draw.polygon(helm, DOME, spike, SS)

        pygame.draw.line(helm, DOME,
                         (pad + hw // 2 - 2 * SS, Y(pad + hh - 3 * SS)),
                         (pad + hw // 2 + 2 * SS, Y(pad + hh - 3 * SS)), SS)
        pygame.draw.rect(helm, CHROME,
                         pygame.Rect(pad - 1 * SS, Y(pad + hh - 1 * SS),
                                     hw + 2 * SS, 2 * SS))

        # H5 punk skull-bunny face — BONE skull stretched to 22×13 native,
        # DOME eye sockets + nose + Jolly Roger mouth, RED bandage cross
        # over the left eye. Sits between the rim line and the chinstrap.
        sk_w_native = 22
        sk_h_native = 13
        sk_w_ss = sk_w_native * SS
        sk_h_ss = sk_h_native * SS
        sk = pygame.Rect(0, 0, sk_w_ss, sk_h_ss)
        sk.center = (pad + hw // 2, Y(pad + int(hh * 0.5)))
        pygame.draw.ellipse(helm, BONE, sk)
        pygame.draw.ellipse(helm, DOME, sk, max(1, int(1.0 * SS)))

        eye_r = max(1, int(sk_w_ss * 0.13))
        eye_x_off = int(sk_w_ss * 0.20)
        eye_y = sk.top + int(sk_h_ss * 0.38)
        for sign in (-1, 1):
            ex = sk.centerx + sign * eye_x_off
            pygame.draw.circle(helm, DOME, (ex, eye_y), eye_r)

        nose_top_y = sk.top + int(sk_h_ss * 0.55)
        nose_bot_y = nose_top_y + int(0.55 * SS)
        wing = max(1, int(sk_w_ss * 0.07))
        pygame.draw.polygon(helm, DOME, [
            (sk.centerx - wing, nose_top_y),
            (sk.centerx + wing, nose_top_y),
            (sk.centerx,        nose_bot_y),
        ])

        mouth_scale = sk_w_native / 23.0
        mouth_stroke = max(1, int(1.0 * SS * mouth_scale))
        teeth_top = sk.bottom - int(5 * SS * mouth_scale)
        teeth_bot = sk.bottom - int(2.5 * SS * mouth_scale)
        if teeth_bot <= teeth_top:
            teeth_bot = teeth_top + max(2, SS // 2)
        divider_dx = max(2, int(2.5 * SS * mouth_scale))
        divider_offsets = (-divider_dx, 0, divider_dx)
        outer_shorten = max(1, int(0.6 * SS * mouth_scale))
        tooth_bottoms = []
        for idx, dx in enumerate(divider_offsets):
            top_y = teeth_top + (outer_shorten if idx != 1 else 0)
            pygame.draw.line(helm, DOME,
                             (sk.centerx + dx, top_y),
                             (sk.centerx + dx, teeth_bot),
                             mouth_stroke)
            tooth_bottoms.append((sk.centerx + dx, teeth_bot))
        dip = max(2, int(1.0 * SS * mouth_scale))
        for (x0p, y0p), (x1p, y1p) in zip(tooth_bottoms, tooth_bottoms[1:]):
            pts = []
            for i in range(7):
                t = i / 6.0
                xp = x0p + (x1p - x0p) * t
                y_base = y0p + (y1p - y0p) * t
                yp = y_base + dip * math.sin(math.pi * t)
                pts.append((xp, yp))
            pygame.draw.lines(helm, DOME, False, pts, mouth_stroke)

        cross_cx = sk.centerx - eye_x_off
        cross_cy = eye_y
        bar_l = max(3, int(5.0 * SS * (sk_w_native / 23.0)))
        bar_t = max(1, int(1.6 * SS * (sk_w_native / 23.0)))
        horiz = pygame.Rect(0, 0, bar_l, bar_t)
        horiz.center = (cross_cx, cross_cy)
        vert = pygame.Rect(0, 0, bar_t, bar_l)
        vert.center = (cross_cx, cross_cy)
        pygame.draw.rect(helm, RED, horiz, border_radius=max(1, SS // 3))
        pygame.draw.rect(helm, RED, vert, border_radius=max(1, SS // 3))
        pygame.draw.rect(helm, DOME, horiz, max(1, SS // 4),
                         border_radius=max(1, SS // 3))
        pygame.draw.rect(helm, DOME, vert, max(1, SS // 4),
                         border_radius=max(1, SS // 3))

        # Chinstrap drawn on top of the face so it reads as the outer layer.
        STRAP   = OUT
        BUCKLE  = RED
        rim_y = Y(pad + hh + 1 * SS)
        front_anchor = (8 * SS, rim_y)
        rear_anchor  = (4 * SS, rim_y)
        junction     = (6 * SS, Y(33 * SS))
        clip_centre  = (14 * SS, Y(40 * SS))
        pygame.draw.line(helm, STRAP, front_anchor, junction, 2 * SS)
        pygame.draw.line(helm, STRAP, rear_anchor,  junction, 2 * SS)
        pygame.draw.line(helm, STRAP, junction, clip_centre, 2 * SS)
        adj = pygame.Rect(junction[0] - 1 * SS, junction[1] - 1 * SS,
                          3 * SS, 2 * SS)
        pygame.draw.rect(helm, (30, 30, 40), adj)
        pygame.draw.rect(helm, CHROME, adj, SS)
        clip = pygame.Rect(clip_centre[0] - 2 * SS,
                           clip_centre[1] - 2 * SS, 5 * SS, 4 * SS)
        pygame.draw.rect(helm, BUCKLE, clip)
        pygame.draw.rect(helm, OUT, clip, SS)
        pygame.draw.line(helm, OUT,
                         (clip.x + 2 * SS, clip.y),
                         (clip.x + 2 * SS, clip.bottom - 1 * SS), SS)
        pygame.draw.line(helm, STRAP, clip_centre, (22 * SS, Y(38 * SS)),
                         2 * SS)

        # G1 ears — icon-style chunky red-tipped bunny ears, 6×18 native,
        # ±12° outward tilt. BONE outer + DOME outline + RED inner.
        ear_w = 6 * SS
        ear_h = 18 * SS
        dome_top_cx = pad + hw // 2
        dome_top_y  = Y(pad)
        for sign in (-1, 1):
            ear_cx = dome_top_cx + sign * 5 * SS
            ear_cy = dome_top_y - 3 * SS
            ear_sub = pygame.Surface(
                (ear_w + 4 * SS, ear_h + 4 * SS), pygame.SRCALPHA)
            local = pygame.Rect(0, 0, ear_w, ear_h)
            local.center = (ear_sub.get_width() // 2,
                            ear_sub.get_height() // 2)
            pygame.draw.ellipse(ear_sub, BONE, local)
            pygame.draw.ellipse(ear_sub, DOME, local, max(1, int(1.2 * SS)))
            inner = local.inflate(-int(2.5 * SS), -int(8 * SS))
            pygame.draw.ellipse(ear_sub, RED, inner)
            ear_ang = -12 * sign
            ear_rot = pygame.transform.rotate(ear_sub, ear_ang)
            ear_rect = ear_rot.get_rect(center=(ear_cx, ear_cy))
            helm.blit(ear_rot, ear_rect.topleft)

        native_size = (hw_n + pad_n * 2,
                       hh_n + pad_n * 2 + drop_n + ear_top_n)
        return pygame.transform.smoothscale(helm, native_size)

    @staticmethod
    def _build_skate_tophat_sprite():
        """Skate + 3x head-piece: the gold '$' top-hat (3x identity) wearing the
        skateboard helmet's red-tipped BUNNY EARS — the 3x hat rendered in the
        helmet's bunny style. Built once at 6x supersample, then scaled/rotated
        per frame exactly like the helmet."""
        SS = 6
        BONE = (240, 240, 230); DARK = (12, 10, 18); RED = (200, 50, 50)
        G_DK = (168, 112, 26); G = (244, 196, 60)
        G_MID = (216, 162, 40); G_LT = (255, 236, 150)
        DOL = (74, 186, 110); DOL_DK = (18, 86, 50); DOL_HI = (220, 255, 232)
        # A tall narrow gold cylinder reads clearly as a top-hat at small scale.
        brim_w, cyl_w, cyl_h, ear_over, pad = 18, 10, 17, 6, 3
        wn = brim_w + pad * 2
        hn = cyl_h + 4 + ear_over + pad * 2
        w, h = wn * SS, hn * SS
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        cx = w // 2
        brim_cy = h - (pad + 2) * SS          # brim sits near the bottom
        cyl_bot = brim_cy
        cyl_top = cyl_bot - cyl_h * SS
        # bunny ears first (behind the cylinder), poking up beside its top
        ew, eh = 5 * SS, (ear_over + 9) * SS
        for sign in (-1, 1):
            ear = pygame.Surface((ew + 4 * SS, eh + 4 * SS), pygame.SRCALPHA)
            er = pygame.Rect(0, 0, ew, eh)
            er.center = (ear.get_width() // 2, ear.get_height() // 2)
            pygame.draw.ellipse(ear, BONE, er)
            pygame.draw.ellipse(ear, DARK, er, max(1, int(1.0 * SS)))
            pygame.draw.ellipse(ear, RED, er.inflate(-int(2.2 * SS), -int(7 * SS)))
            rot = pygame.transform.rotate(ear, -18 * sign)
            rr = rot.get_rect(center=(cx + sign * 4 * SS, cyl_top + 1 * SS))
            surf.blit(rot, rr.topleft)
        # tall gold cylinder (hat body) with a rounded crown
        cyl = pygame.Rect(cx - cyl_w * SS // 2, cyl_top, cyl_w * SS, cyl_h * SS)
        pygame.draw.rect(surf, G_DK, cyl, border_radius=2 * SS)
        pygame.draw.rect(surf, G_MID, cyl.inflate(-1 * SS, -1 * SS), border_radius=2 * SS)
        pygame.draw.rect(surf, G, (cyl.x + 1 * SS, cyl.y + 1 * SS,
                                   cyl.w - 3 * SS, cyl.h - 2 * SS), border_radius=1 * SS)
        pygame.draw.rect(surf, G_LT, (cyl.x + 2 * SS, cyl.y + 2 * SS, 1 * SS, cyl.h - 5 * SS))
        # green $ band across the cylinder face (the 3x identity)
        band = pygame.Rect(cyl.x, cyl.centery - 2 * SS, cyl.w, 5 * SS)
        pygame.draw.rect(surf, DOL_DK, band)
        pygame.draw.rect(surf, DOL, band.inflate(0, -1 * SS))
        gx, gy = cx, band.centery
        pygame.draw.line(surf, DOL_HI, (gx, gy - 2 * SS), (gx, gy + 2 * SS), max(1, SS // 2))
        surf.set_at((gx - SS, gy - 2 * SS), DOL_HI)
        surf.set_at((gx + SS, gy + 2 * SS), DOL_HI)
        # gold brim (ellipse) at the base, in front of the cylinder
        brim = pygame.Rect(cx - brim_w * SS // 2, brim_cy - 2 * SS, brim_w * SS, 5 * SS)
        pygame.draw.ellipse(surf, G_DK, brim)
        pygame.draw.ellipse(surf, G, brim.inflate(-2 * SS, -1 * SS))
        pygame.draw.ellipse(surf, G_LT, (brim.x + 3 * SS, brim.y + 1 * SS, brim.w - 8 * SS, 1 * SS))
        return pygame.transform.smoothscale(surf, (wn, hn))

    def _draw_skate_hat(self, surf, cx, cy, flipped):
        """Gold bunny 3x top-hat on a skating Pip (replaces the punk helmet
        when 3x is up). Same scale/seat machinery as _draw_helmet."""
        global _SKATE_HAT_SPRITE
        from game.config import GROW_SCALE
        s = (GROW_SCALE if self.grow_active else 1.0) * self.shrink_scale
        if _SKATE_HAT_SPRITE is None:
            _SKATE_HAT_SPRITE = Bird._build_skate_tophat_sprite()
        hat = _SKATE_HAT_SPRITE
        if abs(s - 1.0) > 1e-3:
            key = round(s, 2)
            hat = _SKATE_HAT_SCALED.get(key)
            if hat is None:
                hw, hh = _SKATE_HAT_SPRITE.get_size()
                hat = pygame.transform.smoothscale(
                    _SKATE_HAT_SPRITE, (max(1, int(hw * key)), max(1, int(hh * key))))
                _SKATE_HAT_SCALED[key] = hat
        tilt = -self.tilt_deg if flipped else self.tilt_deg
        # The brim seats at Pip's head crown; the cylinder + ears rise above it.
        anchor = pygame.math.Vector2(17 * s, 16 * s if flipped else -16 * s).rotate(-tilt)
        ax, ay = int(cx + anchor.x), int(cy + anchor.y)
        rotated = pygame.transform.rotate(hat, tilt)
        if flipped:
            rotated = pygame.transform.flip(rotated, False, True)
            r = rotated.get_rect(midtop=(ax, ay))
        else:
            r = rotated.get_rect(midbottom=(ax, ay))
        surf.blit(rotated, r.topleft)

    @staticmethod
    def _build_board_base():
        """Static skull-skateboard base (deck + trucks + wheels, NO spokes),
        4x supersample built once. Returns (native_sprite, wheels) where wheels
        is native-space [(wx, wy, r, sign)] for the live spinning spokes."""
        s = 1.0
        SS = 4
        board_w_n = int(48 * s)
        deck_h_n  = max(4, int(7 * s))
        pad_n     = 10
        native_w  = board_w_n + pad_n * 2
        native_h  = deck_h_n * 5 + pad_n * 2
        board_w = board_w_n * SS
        deck_h  = deck_h_n * SS
        pad     = pad_n * SS
        board_surf = pygame.Surface(
            (board_w + pad * 2, deck_h * 5 + pad * 2), pygame.SRCALPHA)
        bsx = board_surf.get_width() // 2
        bsy = board_surf.get_height() // 2 - 2 * SS
        deck = pygame.Rect(0, 0, board_w, deck_h)
        deck.center = (bsx, bsy)
        pygame.draw.rect(board_surf, (200, 200, 210), deck,
                         border_radius=3 * SS)
        pygame.draw.rect(board_surf, (10, 10, 18),
                         deck.inflate(-2 * SS, -2 * SS),
                         border_radius=2 * SS)
        pygame.draw.line(board_surf, (235, 235, 225),
                         (deck.left + 4 * SS, deck.top + 1 * SS),
                         (deck.right - 4 * SS, deck.bottom - 1 * SS), SS)
        pygame.draw.line(board_surf, (235, 235, 225),
                         (deck.left + 4 * SS, deck.bottom - 1 * SS),
                         (deck.right - 4 * SS, deck.top + 1 * SS), SS)
        sk_w = max(5 * SS, int(7 * s * SS))
        sk_h = max(3 * SS, int(5 * s * SS))
        sk_rect = pygame.Rect(0, 0, sk_w, sk_h)
        sk_rect.center = (bsx, deck.centery - 1 * SS)
        pygame.draw.ellipse(board_surf, (240, 240, 230), sk_rect)
        pygame.draw.ellipse(board_surf, (10, 10, 18), sk_rect, SS)
        eye_y = sk_rect.centery - 1 * SS
        pygame.draw.circle(board_surf, (10, 10, 18),
                           (sk_rect.centerx - 1 * SS, eye_y), 1 * SS)
        pygame.draw.circle(board_surf, (10, 10, 18),
                           (sk_rect.centerx + 1 * SS, eye_y), 1 * SS)
        truck_h = max(1 * SS, int(2 * s * SS))
        wheel_r = max(2 * SS, int(3 * s * SS))
        wheels = []
        for sign in (-1, 1):
            tx = bsx + sign * int(board_w * 0.32) - 3 * SS
            pygame.draw.rect(board_surf, (60, 60, 70),
                             (tx, deck.bottom, 6 * SS, truck_h))
            wx = bsx + sign * int(board_w * 0.32)
            wy = deck.bottom + truck_h + wheel_r
            pygame.draw.circle(board_surf, (50, 50, 60), (wx, wy),
                               wheel_r + 1 * SS)
            pygame.draw.circle(board_surf, (245, 240, 230), (wx, wy),
                               wheel_r)
            pygame.draw.circle(board_surf, (200, 50, 50), (wx, wy), 1 * SS)
            wheels.append((wx / SS, wy / SS, wheel_r / SS, sign))
        base = pygame.transform.smoothscale(board_surf, (native_w, native_h))
        return base, wheels

    def _draw_skateboard(self, surf, cx, cy, flipped):
        """Skull skateboard under Pip's feet. The static base (deck/skull/
        trucks/wheels) is built once and cached (_build_board_base); per frame
        we only stamp the two spinning wheel-spokes and apply Pip's tilt +
        kickflip/heelflip/popshuvit + flip — no per-frame supersample rebuild
        (which used to run twice via the HUD re-blit)."""
        global _BOARD_BASE, _BOARD_WHEELS
        from game.config import PARCEL_Y_OFFSET, GROW_SCALE
        # Track Pip's body scale so the board sizes + seats under a grown/shrunk
        # bird instead of staying fixed under a mismatched body.
        s = (GROW_SCALE if self.grow_active else 1.0) * self.shrink_scale
        y_off = -PARCEL_Y_OFFSET * s if flipped else PARCEL_Y_OFFSET * s
        offset = pygame.math.Vector2(0, y_off + 4 * s)
        offset = offset.rotate(-(self.tilt_deg if not flipped else -self.tilt_deg))
        bx = cx + offset.x
        by = cy + offset.y
        if _BOARD_BASE is None:
            _BOARD_BASE, _BOARD_WHEELS = Bird._build_board_base()
        board_surf = _BOARD_BASE.copy()
        spin = self.frame_t * 4.0
        for wx, wy, wr, sign in _BOARD_WHEELS:
            sx_p = wx + math.cos(spin + sign * 1.0) * wr * 0.6
            sy_p = wy + math.sin(spin + sign * 1.0) * wr * 0.6
            pygame.draw.line(board_surf, (180, 50, 50),
                             (int(wx), int(wy)), (int(sx_p), int(sy_p)), 1)
        if abs(s - 1.0) > 1e-3:
            bw, bh = board_surf.get_size()
            board_surf = pygame.transform.smoothscale(
                board_surf, (max(1, int(bw * s)), max(1, int(bh * s))))
        tilt = -self.tilt_deg if flipped else self.tilt_deg
        # KICKFLIP — 360° board-only spin layered on top of Pip's
        # velocity-banked tilt. Pip's posture is unchanged; only the
        # board flips under his feet (smootherstep eases in + out).
        if self.kickflip_t > 0 and self.kickflip_dur > 0:
            p = 1.0 - self.kickflip_t / self.kickflip_dur
            eased = p * p * p * (p * (p * 6.0 - 15.0) + 10.0)
            tilt += eased * 360.0
        # HEELFLIP — mirror of kickflip, board spins −360°.
        if self.heelflip_t > 0 and self.heelflip_dur > 0:
            p = 1.0 - self.heelflip_t / self.heelflip_dur
            eased = p * p * p * (p * (p * 6.0 - 15.0) + 10.0)
            tilt -= eased * 360.0
        rotated = pygame.transform.rotate(board_surf, tilt)
        # POP SHUVIT — horizontal scale-X = cos(p·π) on top of the
        # rotation: board flattens edge-on at p=0.5 then flips and
        # returns to its starting facing. Done AFTER rotation so the
        # squash tracks the (rotated) board's bounding box.
        if self.popshuvit_t > 0 and self.popshuvit_dur > 0:
            p_ps = 1.0 - self.popshuvit_t / self.popshuvit_dur
            scale_x = math.cos(p_ps * math.pi)
            abs_scale = max(abs(scale_x), 0.02)
            rw, rh = rotated.get_size()
            rotated = pygame.transform.scale(
                rotated, (max(1, int(rw * abs_scale)), rh))
            if scale_x < 0:
                rotated = pygame.transform.flip(rotated, True, False)
        if flipped:
            rotated = pygame.transform.flip(rotated, False, True)
        r = rotated.get_rect(center=(int(bx), int(by)))
        surf.blit(rotated, r.topleft)


# ── Pipe (nature pillar) ─────────────────────────────────────────────────────

class Pipe:
    """Pagoda pillar column. Each instance picks one of the 11 variants
    deterministically from its seed, so the vegetation and ornament
    arrangement is stable across frames."""

    def __init__(self, x: float, gap_y: float, gap_h: float):
        self.x = x
        # Set behind the properties: the invalidation setters below read the
        # cache attrs, which don't exist yet this early in __init__.
        self._gap_y = gap_y
        self._gap_h = gap_h
        self.scored = False
        self.is_rush = False
        # Cycle-finale phantom: a non-drawn, non-colliding, non-scoring
        # placeholder. The 5-pillar finale span uses these to consume the
        # right slice of biome time + scroll cadence while leaving the sky
        # completely open for the long coin rush + centred treasure chest.
        # See World._spawn_pipe + World._spawn_finale_long_rush_coins.
        self.is_phantom = False
        # Per-pipe sticky flag: set at spawn (if KFC was active when this pipe
        # was created) or retroactively when the powerup is picked up. Once
        # True it stays True for the rest of the pipe's life and gates the
        # one-time gap_h widening at activation so a second KFC pickup
        # doesn't compound the boost. The KFC *visual* is gated separately
        # on world.kfc_timer > 0 (see Pipe.draw) so the pillar reverts to
        # stone at timer=0 alongside the fries mountain + fried Pip; only
        # the wider gap outlives the timer.
        self.is_kfc = False
        # SKATEBOARD: True when World._maybe_spawn_ramp drops a wooden
        # wedge on top of this pipe's lower-pillar crown. Used by the
        # ramp draw + collision logic in World; the Pipe itself stays
        # unchanged in its own draw (the wedge overpaints the crown).
        self.has_ramp = False
        # Per-instance random seed → chooses variant + stable decoration seed
        self.seed = random.randint(0, 0xFFFFFF)
        # KFC re-skin is deterministic per pipe (seed + gap_y + gap_h all
        # stable for a Pipe's lifetime) and never animates, so we render
        # it once on first KFC frame and blit the bitmap each frame after.
        # Without this every visible KFC pillar was allocating ~8
        # SRCALPHA surfaces + running pygame.transform per frame —
        # the dominant source of KFC-mode lag.
        self._kfc_cache: "pygame.Surface | None" = None
        self._kfc_cache_dx = 0  # x-offset between blit corner and self.x
        # Carousel-Barker staff re-skin (warren demo route): same bake-once
        # bitmap treatment as KFC since the jester-staff art never animates.
        self.is_staff = False
        self._staff_cache: "pygame.Surface | None" = None
        self._staff_cache_dx = 0
        # Skull-King stacked-skull totem re-skin (warren demo's second event): same
        # bake-once bitmap treatment as the staff/KFC caches. `skull_idx` selects
        # which of the 20 column designs this pillar wears (set at spawn).
        self.is_skull_king = False
        self.skull_idx = 0
        self._skull_cache: "pygame.Surface | None" = None
        self._skull_cache_dx = 0
        # Pagoda body + ornaments are far heavier than the retired sandstone
        # silhouette, and their internal draw helpers re-alias curved eaves
        # every call. Bake the pair once into a per-instance bitmap (same
        # pattern as the KFC cache) and blit it at the scrolling x — drawing
        # straight to the screen every frame would blow the 60 FPS budget on
        # WASM and re-roll the ornament layer each frame.
        self._pagoda_cache: "pygame.Surface | None" = None
        self._pagoda_cache_dx = 0
        # Per-pixel collision mask of the whole pagoda STRUCTURE (body + every
        # floor roof/eave incl. overhangs + the crown at the gap edge); ornaments
        # are not in it, so flags/vines/lanterns stay non-lethal. Built with the bake.
        self._collision_mask = None
        self._collision_mask_dx = 0
        # SKATEBOARD ride surfaces (lazy, derived from the mask): the LOWER
        # pagoda's roof crown (highest lethal y Pip rides over) and the UPPER
        # pagoda's underside (lowest lethal y the helmet bonks). The roofs
        # overhang the gap rim, so these are NOT the gap edges.
        self._skate_computed = False
        self._skate_low = None
        self._skate_up = None
        # Ornament density + first-pillar quiet rule key off the spawn order;
        # World sets this at spawn (0 = first pillar of the run).
        self.spawn_index = 0

    # Two power-ups re-cut a pillar's gap AFTER it has already baked: KFC
    # widens every live pipe on pickup (World._activate_kfc) and the genie
    # chamber re-centres and widens one pipe several hundred px ahead
    # (World._retarget_genie_chamber). The bake and the collision mask are
    # both cut to the old gap, so both have to be dropped with it — a stale
    # mask leaves ~50 px of visibly-open sky that still kills.

    @property
    def gap_y(self):
        return self._gap_y

    @gap_y.setter
    def gap_y(self, value):
        if value != self._gap_y:
            self._invalidate_bakes()
        self._gap_y = value

    @property
    def gap_h(self):
        return self._gap_h

    @gap_h.setter
    def gap_h(self, value):
        if value != self._gap_h:
            self._invalidate_bakes()
        self._gap_h = value

    def _invalidate_bakes(self):
        """Drop every geometry-derived bitmap + mask so the next draw and the
        next collision test rebuild against the pillar's current gap."""
        self._pagoda_cache = None
        self._kfc_cache = None
        self._staff_cache = None
        self._skull_cache = None
        self._collision_mask = None
        self._skate_computed = False
        self._skate_low = None
        self._skate_up = None

    @property
    def top_rect(self):
        # Full gap extent. Used as the KFC fallback hitbox; pagoda collision uses
        # the per-pixel structural mask of the whole silhouette.
        return pygame.Rect(int(self.x), 0, PIPE_W, int(self.gap_y - self.gap_h / 2))

    @property
    def bot_rect(self):
        top = int(self.gap_y + self.gap_h / 2)
        return pygame.Rect(int(self.x), top, PIPE_W, GROUND_Y - top)

    @property
    def finial_tip_y(self):
        """Y of the bottom pillar's lethal crown = the kill-zone top the grind
        rail rests on. Every variant's crown is calibrated to the gap edge."""
        return self.gap_y + self.gap_h / 2

    @property
    def rail_y(self):
        """Y of the grind-rail track — RAIL_ABOVE_FINIAL px above the crown, so
        the cart rides on top of the kill zone / just above the roof (short
        support posts connect the rail down to the crown)."""
        return self.gap_y + self.gap_h / 2 - RAIL_ABOVE_FINIAL

    def off_screen(self):
        return self.x + PIPE_W + 8 < 0

    def collides_circle(self, cx, cy, r, *, kfc=False):
        if self.is_phantom:
            return False
        if kfc:
            # Fries re-skin roughly fills the rect and has no antenna — keep the
            # cheap AABB hitbox during the KFC window.
            box = pygame.Rect(cx - r, cy - r, r * 2, r * 2)
            return self.top_rect.colliderect(box) or self.bot_rect.colliderect(box)
        # Pagoda: kill zone == the structural silhouette (body + every floor
        # roof/eave incl. overhangs + the crown at the gap edge). Only the loose
        # ornaments (prayer flags / vines / lanterns) are non-lethal, and those are
        # never in the mask (CANDIDATES draws structure only).
        if self._collision_mask is None:
            self._build_collision_mask()
        offset = (int(cx - r - self.x - self._collision_mask_dx), int(cy - r))
        return self._collision_mask.overlap(_circle_mask(r), offset) is not None

    def draw(self, surf, palette=None, kfc_visual=False, phase=0.0):
        if self.is_phantom:
            return
        palette = palette or _DEFAULT_PILLAR
        if self.is_staff:
            if self._staff_cache is None:
                self._build_staff_cache(palette)
            surf.blit(self._staff_cache, (int(self.x) + self._staff_cache_dx, 0))
            return
        if self.is_skull_king:
            if self._skull_cache is None:
                self._build_skull_cache(palette)
            surf.blit(self._skull_cache, (int(self.x) + self._skull_cache_dx, 0))
            return
        if self.is_kfc and kfc_visual:
            if self._kfc_cache is None:
                self._build_kfc_cache(palette)
            surf.blit(self._kfc_cache,
                      (int(self.x) + self._kfc_cache_dx, 0))
            return
        if self._pagoda_cache is None:
            self._build_pagoda_cache(palette, phase)
        surf.blit(self._pagoda_cache,
                  (int(self.x) + self._pagoda_cache_dx, 0))

    def _build_pagoda_cache(self, palette, phase):
        """Render the pagoda pillar pair + ornament layer onto a per-instance
        SRCALPHA surface once, then blit at the scrolling x each frame. Margin
        covers curled eaves / finials / prayer-flag spans that overhang the
        PIPE_W column. Baking once also freezes the ornament roll for the
        pillar's lifetime (so it doesn't re-randomize per frame); the spawn-time
        palette stays close enough over the few seconds a pillar is on screen."""
        margin = 64
        cache_w = PIPE_W + margin * 2
        cache_h = GROUND_Y
        cache = pygame.Surface((cache_w, cache_h), pygame.SRCALPHA)
        local_top = pygame.Rect(margin, 0,
                                PIPE_W, int(self.gap_y - self.gap_h / 2))
        local_bot_top = int(self.gap_y + self.gap_h / 2)
        local_bot = pygame.Rect(margin, local_bot_top,
                                PIPE_W, GROUND_Y - local_bot_top)
        draw_pillar_pair(cache, local_top, local_bot, palette, self.seed,
                         phase=phase, is_rush=self.is_rush,
                         pillar_index=self.spawn_index)
        self._pagoda_cache = cache
        self._pagoda_cache_dx = -margin
        # Build the collision mask now (first draw, well before the pillar reaches
        # the bird) so there's no collision-time hitch.
        if self._collision_mask is None:
            self._build_collision_mask()

    def _build_collision_mask(self):
        """Per-pixel kill-zone mask = the whole pagoda STRUCTURE (body + all floor
        roofs/eaves incl. overhangs past PIPE_W + the crown). Structure only (no
        ornaments), so prayer flags / vines / lanterns are non-lethal. Each
        variant's lethal top reaches ~the nominal gap edge — the tiered tō present a
        solid wide roofed crown there (no thin spire to sneak past), the spired
        variants their spire — so the effective passable gap is ~gap_h, matching the
        old sandstone-pillar AABB collision. Geometry is palette-independent."""
        from game import biome as _biome
        margin = 64
        surf = pygame.Surface((PIPE_W + margin * 2, GROUND_Y), pygame.SRCALPHA)
        local_top = pygame.Rect(margin, 0,
                                PIPE_W, int(self.gap_y - self.gap_h / 2))
        lbt = int(self.gap_y + self.gap_h / 2)
        local_bot = pygame.Rect(margin, lbt, PIPE_W, GROUND_Y - lbt)
        if self.is_staff:
            from game.pillar_staff import draw_pillar_pair_staff
            draw_pillar_pair_staff(surf, local_top, local_bot,
                                   _biome.palette_for_phase(0.0), self.seed)
        elif self.is_skull_king:
            from game.pillar_skull import draw_pillar_pair_skull
            if not draw_pillar_pair_skull(surf, local_top, local_bot,
                                          _biome.palette_for_phase(0.0),
                                          self.seed, self.skull_idx):
                key = VARIANT_KEYS[self.seed % VARIANT_COUNT]
                CANDIDATES[key](surf, local_top, local_bot,
                                _biome.palette_for_phase(0.0), self.seed)
        else:
            key = VARIANT_KEYS[self.seed % VARIANT_COUNT]
            CANDIDATES[key](surf, local_top, local_bot,
                            _biome.palette_for_phase(0.0), self.seed)
        self._collision_mask = pygame.mask.from_surface(surf, 50)
        self._collision_mask_dx = -margin

    def skate_surfaces(self):
        """SKATEBOARD ride surfaces (lower_crown_top_y, upper_crown_bottom_y),
        read off the structural mask. `lower_crown_top` is the HIGHEST lethal
        pixel of the lower pagoda — the roofline Pip rides over; `upper_crown_bot`
        is the LOWEST lethal pixel of the upper pagoda — where the helmet bonks.
        The pagoda roofs overhang the gap rim (the roof tiers rise above
        gap_bot / hang below gap_top), so these are NOT the gap edges: snapping to
        the gap edge left Pip clipping the roof and dying. Cached per pipe."""
        if self._skate_computed:
            return self._skate_low, self._skate_up
        if self._collision_mask is None:
            self._build_collision_mask()
        low = up = None
        # The gap splits the silhouette into an upper and a lower component; the
        # mask carries no x-offset in y, so rect.top/.bottom are world-y directly.
        for rc in self._collision_mask.get_bounding_rects():
            if rc.centery < self.gap_y:
                up = rc.bottom if up is None else max(up, rc.bottom)
            else:
                low = rc.top if low is None else min(low, rc.top)
        self._skate_low = (float(low) if low is not None
                           else self.gap_y + self.gap_h / 2)
        self._skate_up = (float(up) if up is not None
                          else self.gap_y - self.gap_h / 2)
        self._skate_computed = True
        return self._skate_low, self._skate_up

    def _build_kfc_cache(self, palette):
        """Render the KFC pillar pair onto a per-instance SRCALPHA
        surface once; subsequent frames blit the bitmap at the current
        scrolling x. Margin covers buckets / hot-dog tilts / corn-dog
        rotation that overhang the PIPE_W column."""
        from game.pillar_kfc import draw_pillar_pair_kfc
        margin = 64
        cache_w = PIPE_W + margin * 2
        cache_h = GROUND_Y
        cache = pygame.Surface((cache_w, cache_h), pygame.SRCALPHA)
        local_top = pygame.Rect(margin, 0,
                                PIPE_W, int(self.gap_y - self.gap_h / 2))
        local_bot_top = int(self.gap_y + self.gap_h / 2)
        local_bot = pygame.Rect(margin, local_bot_top,
                                PIPE_W, GROUND_Y - local_bot_top)
        draw_pillar_pair_kfc(cache, local_top, local_bot, palette, self.seed)
        self._kfc_cache = cache
        self._kfc_cache_dx = -margin

    def _build_staff_cache(self, palette):
        """Render the Carousel-Barker staff pillar pair onto a per-instance
        SRCALPHA surface once; later frames blit the bitmap at the scrolling x.
        Margin covers the cap tips / ruff bells that overhang the PIPE_W column."""
        from game.pillar_staff import draw_pillar_pair_staff, staff_collision_mask
        margin = 64
        cache_w = PIPE_W + margin * 2
        cache_h = GROUND_Y
        cache = pygame.Surface((cache_w, cache_h), pygame.SRCALPHA)
        local_top = pygame.Rect(margin, 0,
                                PIPE_W, int(self.gap_y - self.gap_h / 2))
        local_bot_top = int(self.gap_y + self.gap_h / 2)
        local_bot = pygame.Rect(margin, local_bot_top,
                                PIPE_W, GROUND_Y - local_bot_top)
        draw_pillar_pair_staff(cache, local_top, local_bot, palette, self.seed)
        self._staff_cache = cache
        self._staff_cache_dx = -margin
        # Build the matching collision mask by stamping the shared per-bucket
        # obstacle masks at the same offsets — avoids a full-surface
        # mask.from_surface scan per tower, which is a big cost in the warren
        # burst (esp. under WASM). Offsets line up with draw_pillar_pair_staff.
        if self._collision_mask is None:
            self._collision_mask = staff_collision_mask(
                (cache_w, cache_h), local_top, local_bot)
            self._collision_mask_dx = -margin

    def _build_skull_cache(self, palette):
        """Render the Skull-King stacked-skull totem pair once into a per-instance
        SRCALPHA bitmap; later frames blit it at the scrolling x. Same margin +
        bake-once treatment as the staff cache. If the skull engine isn't present in
        this checkout (e.g. a stripped/web build), fall back to a plain pagoda pair
        so the pillar stays visible and lethal instead of vanishing."""
        from game.pillar_skull import draw_pillar_pair_skull
        margin = 64
        cache = pygame.Surface((PIPE_W + margin * 2, GROUND_Y), pygame.SRCALPHA)
        local_top = pygame.Rect(margin, 0,
                                PIPE_W, int(self.gap_y - self.gap_h / 2))
        local_bot_top = int(self.gap_y + self.gap_h / 2)
        local_bot = pygame.Rect(margin, local_bot_top,
                                PIPE_W, GROUND_Y - local_bot_top)
        ok = draw_pillar_pair_skull(cache, local_top, local_bot, palette,
                                    self.seed, self.skull_idx)
        if not ok:
            draw_pillar_pair(cache, local_top, local_bot, palette, self.seed,
                             phase=0.0, is_rush=self.is_rush,
                             pillar_index=self.spawn_index)
        self._skull_cache = cache
        self._skull_cache_dx = -margin
        # Collision mask straight from the rendered cache alpha (same as the staff).
        if self._collision_mask is None:
            self._collision_mask = pygame.mask.from_surface(cache, 50)
            self._collision_mask_dx = -margin



# ── Coin ─────────────────────────────────────────────────────────────────────

_COIN_FACE_CACHE: "pygame.Surface | None" = None
_TRIPLE_COIN_FACE_CACHE: "pygame.Surface | None" = None


def _get_coin_face() -> pygame.Surface:
    """Build the face-on coin sprite once at 8x super-sample. Layers:
    dark-amber outline, a twisted-rope rim (alternating dark/light
    segments around the perimeter), a vertical gold gradient body, an
    embossed parrot silhouette, and a soft upper-left specular highlight.
    Smoothscaled per frame to apply the coin-spin squeeze, so the rope
    rim stays visible across every frame of the rotation animation."""
    global _COIN_FACE_CACHE
    if _COIN_FACE_CACHE is not None:
        return _COIN_FACE_CACHE
    SS = 8
    # Cache at 4x display so the per-frame spin smoothscale is the AA pass.
    DISPLAY_D = COIN_R * 2 + 4
    CACHE_MUL = 4
    final_d = DISPLAY_D * CACHE_MUL
    size = final_d * SS
    # U scales the parrot with the cache; SS stays for 1-px AA margins only.
    U = SS * CACHE_MUL
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
    EMBOSS_DK  = ( 90,  50,   0)
    EMBOSS_HI  = (180, 120,  10)
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
    #    Flying-pose, head pointing left. Body + tail + tucked wing +
    #    head + hooked beak + eye dot. Two emboss tones (mid + dark)
    #    plus a gold highlight give the figure enough volume to read
    #    as a bird at the 26 px coin size, instead of a flat blob.

    # Body — oval, slightly elongated horizontally.
    pygame.draw.ellipse(surf, EMBOSS,
                        (cx - 2 * U, cy - 1 * U, 7 * U, 5 * U))

    # Tail — tapered fan extending right past the body.
    pygame.draw.polygon(surf, EMBOSS,
                        [(cx + 4 * U, cy + 0 * U),
                         (cx + 7 * U, cy + 1 * U),
                         (cx + 6 * U, cy + 3 * U),
                         (cx + 4 * U, cy + 2 * U)])

    # Wing — darker tucked shape on the body (lower-right of body),
    # suggests a folded wing in flight.
    pygame.draw.polygon(surf, EMBOSS_DK,
                        [(cx + 0 * U, cy + 0 * U),
                         (cx + 3 * U, cy + 0 * U),
                         (cx + 4 * U, cy + 2 * U),
                         (cx + 1 * U, cy + 3 * U)])

    # Head — circle, upper-left.
    head_cx, head_cy = cx - 1 * U, cy - 3 * U
    pygame.draw.circle(surf, EMBOSS, (head_cx, head_cy), 3 * U)

    # Beak — main hooked triangle pointing left.
    pygame.draw.polygon(surf, EMBOSS,
                        [(cx - 3 * U, cy - 3 * U),
                         (cx - 6 * U, cy - 2 * U),
                         (cx - 3 * U, cy - 1 * U)])
    # Beak shadow — small darker wedge under the hook for curvature.
    pygame.draw.polygon(surf, EMBOSS_DK,
                        [(cx - 5 * U, cy - 2 * U),
                         (cx - 6 * U, cy - 2 * U),
                         (cx - 4 * U, cy - 1 * U)])

    # Eye — small bright dot on the head (replaces the original
    # floating "highlight" with a positioned eye that gives the bird
    # a face).
    pygame.draw.circle(surf, GOLD_HI,
                       (head_cx + U // 2, head_cy - U // 2),
                       max(1, U // 2))

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


def _get_coin_face_triple() -> pygame.Surface:
    """3X-mode coin face: same rim/body/rope/specular as the standard coin,
    but the embossed parrot is replaced by a large `$` in the original
    EMBOSS amber. Reads as struck into the gold body, same recipe the
    parrot uses (flat amber on gold, no outline, no shadow). Cached
    identically to _get_coin_face."""
    global _TRIPLE_COIN_FACE_CACHE
    if _TRIPLE_COIN_FACE_CACHE is not None:
        return _TRIPLE_COIN_FACE_CACHE
    SS = 8
    DISPLAY_D = COIN_R * 2 + 4
    CACHE_MUL = 4
    final_d = DISPLAY_D * CACHE_MUL
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
    DARK_AMBER = ( 75,  35,   0)
    LITE_AMBER = (210, 165,  50)
    EMBOSS     = (130,  80,   0)

    # Layers 1-3 + 5: rim, gradient body, rope rim, specular highlight —
    # identical to _get_coin_face (parrot section omitted; `$` stamped
    # post-smoothscale at display resolution for crisp Liberation-Sans
    # rendering).
    pygame.draw.circle(surf, OUTLINE_DK, (cx, cy), r_outer)
    pygame.draw.circle(surf, OUTLINE_LT, (cx, cy), r_outer - SS)

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

    hl = pygame.Surface((size, size), pygame.SRCALPHA)
    hl_rect = pygame.Rect(cx - r_body + r_body // 5,
                          cy - r_body + r_body // 6,
                          int(r_body * 1.1), int(r_body * 0.5))
    pygame.draw.ellipse(hl, (255, 255, 235, 110), hl_rect)
    hl.blit(body_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(hl, (0, 0))

    face = pygame.transform.smoothscale(surf, (final_d, final_d))

    # Stamp `$` at display resolution, 3× super-sampled for crisp edges.
    import pathlib as _pl
    glyph_size = 80
    SS_G = 3
    fpath = str(_pl.Path(__file__).parent / "assets" / "LiberationSans-Bold.ttf")
    f = pygame.font.Font(fpath, glyph_size * SS_G)
    big = f.render("$", True, EMBOSS)
    bw, bh = big.get_size()
    glyph = pygame.transform.smoothscale(big, (bw // SS_G, bh // SS_G))
    fcx = fcy = face.get_width() // 2
    face.blit(glyph, glyph.get_rect(center=(fcx, fcy + 1)).topleft)

    _TRIPLE_COIN_FACE_CACHE = face
    return _TRIPLE_COIN_FACE_CACHE


class Ramp:
    """SKATEBOARD ramp — a wooden wedge perched on a lower pillar's
    crown that Pip can skate up while the buff is active. Shape
    ``/|`` : slope rises LEFT→RIGHT and the vertical kicker face is
    on the RIGHT. ``base_y`` is the bottom edge of the wedge — defaults
    to GROUND_Y for legacy floor placement, otherwise set to the host
    pipe's ``gap_y + gap_h / 2``."""

    def __init__(self, x: float, w: float, h: float,
                 base_y: float | None = None):
        from game.config import GROUND_Y as _GY
        self.x = x      # left edge of the wedge (ground side)
        self.w = w      # horizontal extent
        self.h = h      # peak height (top-right corner above base_y)
        self.base_y = _GY if base_y is None else base_y

    def off_screen(self) -> bool:
        return self.x + self.w + 8 < 0

    def surface_y_at(self, px: float) -> float:
        """Top surface y at world x. Outside the wedge footprint
        returns ``base_y``. At ramp.x (left/foot) returns the base;
        at ramp.x + ramp.w (right/kicker) returns the peak."""
        if px < self.x or px > self.x + self.w:
            return self.base_y
        t = (px - self.x) / self.w
        return self.base_y - self.h * t

    def draw(self, surf, palette=None):
        WOOD     = (140, 100, 65)
        WOOD_DK  = (95,  70,  45)
        WOOD_HI  = (200, 165, 105)
        EDGE     = (40,  25,  18)
        x0 = int(self.x)
        x1 = int(self.x + self.w)
        y0 = int(self.base_y)
        y_top = y0 - int(self.h)
        pts = [(x0, y0), (x1, y0), (x1, y_top)]
        pygame.draw.polygon(surf, WOOD, pts)
        pygame.draw.line(surf, WOOD_HI, (x0 + 1, y0 - 1),
                         (x1 - 1, y_top + 1), 2)
        pygame.draw.line(surf, WOOD_DK, (x0, y0), (x1, y0), 2)
        for frac in (0.33, 0.66):
            xp = int(self.x + self.w * frac)
            yp = int(self.base_y - self.h * frac)
            pygame.draw.line(surf, WOOD_DK, (xp, yp + 1), (xp, y0 - 1), 1)
        pygame.draw.polygon(surf, EDGE, pts, 1)
        pygame.draw.line(surf, WOOD_HI, (x1 - 1, y_top + 2),
                         (x1 - 1, y0 - 1), 1)


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
        # Weather: rain shakes coins left-right (visual-only x offset).
        self.weather_dx = 0.0
        self._weather_phase = random.uniform(0, math.tau)

    def update(self, dt):
        self.spin = (self.spin + dt * self.SPIN_RATE) % math.tau
        self.float_t += dt

    def draw(self, surf, kfc_active=False, triple_active=False):
        cx = int(self.x + self.weather_dx)
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
        # embossed parrot/$ are all preserved across every angle of the
        # rotation — including near-edge-on slivers. A small floor on the
        # squeeze (10% width) keeps the edge-on frame readable instead of
        # collapsing to a 1-px line.
        cos_s = math.cos(self.spin)
        r = COIN_R
        squeeze = max(0.10, abs(cos_s))
        face = _get_coin_face_triple() if triple_active else _get_coin_face()
        # Source is 4x display; downsample target is on-screen size, not face size.
        display_h = COIN_R * 2 + 4
        display_w = max(2, int(display_h * squeeze))
        squeezed = pygame.transform.smoothscale(face, (display_w, display_h))
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
       shrink   — red-velvet mushroom; bird scales to SHRINK_SCALE
       rail     — train ticket; cart ride over RAIL_PILLAR_COUNT pillars
       lottery  — scratch card; rolls a tier and applies its coin delta
    """
    def __init__(self, x, y, kind="triple"):
        self.x = x
        self.y = y
        self.kind = kind
        self.collected = False
        self.pulse = 0.0
        # GENIE LAMP — when a genie is picked up, World spawns several
        # alternate powerup pickups with this flag set. Picking up any
        # one cancels the others (see World._cull_genie_offers_except).
        self.is_genie_offer = False
        # Treasure-box post-pickup animation timer. Drained by update();
        # while > 0 the world keeps this PowerUp alive past collection so
        # the open-lid sprite + halo can render to completion.
        self.claimed_anim_t = 0.0

    def update(self, dt):
        self.pulse += dt * 3.5
        if self.claimed_anim_t > 0.0:
            self.claimed_anim_t = max(0.0, self.claimed_anim_t - dt)

    def draw(self, surf):
        if self.kind == "triple":
            _draw_dollar_coin(surf, int(self.x), int(self.y), pulse=self.pulse)
        elif self.kind == "magnet":
            self._draw_magnet(surf)
        elif self.kind == "megamagnet":
            self._draw_megamagnet(surf)
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
        elif self.kind == "shrink":
            self._draw_shrink_mushroom(surf)
        elif self.kind == "rail":
            self._draw_rail_icon(surf)
        elif self.kind == "lottery":
            self._draw_lottery_icon(surf)
        elif self.kind == "skateboard":
            self._draw_skateboard_icon(surf)
        elif self.kind == "knight":
            self._draw_knight_icon(surf)
        elif self.kind == "genie":
            self._draw_genie_icon(surf)
        elif self.kind == "poison":
            self._draw_poison_vial(surf)
        elif self.kind == "umbrella":
            from game.umbrella import draw_pickup_icon
            draw_pickup_icon(surf, int(self.x), int(self.y), self.pulse)
        elif self.kind == "treasure":
            from game.treasure_box import draw_pickup_icon as _tb_closed
            from game.treasure_box import draw_open_sprite as _tb_open
            cx, cy = int(self.x), int(self.y)
            if self.claimed_anim_t > 0.0:
                from game.config import TREASURE_BOX_ANIM_T
                # Combined O3 (starburst) + O4 (spilling coins) — the
                # starburst halo + chest fade are both driven by anim_t
                # inside draw_open_sprite, so no extra glow needed here.
                _tb_open(surf, cx, cy,
                         self.claimed_anim_t, TREASURE_BOX_ANIM_T)
            else:
                _tb_closed(surf, cx, cy, self.pulse)

    # ── sprite variants ─────────────────────────────────────────────────────
    def _draw_mushroom(self, surf):
        cx = int(self.x)
        cy = int(self.y)
        _draw_grow_halo(surf, cx, cy, self.pulse)
        sprite, dx, dy = _get_grow_body_sprite()
        surf.blit(sprite, (cx + dx, cy + dy))

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

        # No upper specular sheen — the body keeps a clean uniform red.

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

        # Extra lightning bolts radiating outward from each pole tip,
        # crackling with self.pulse so the magnet feels actively powered.
        YELLOW = (255, 220,  60)
        WHITE  = (255, 250, 220)

        def _bolt(target, pts, thick_outer, thick_inner):
            if len(pts) < 2:
                return
            pygame.draw.lines(target, YELLOW, False, pts, thick_outer)
            pygame.draw.lines(target, WHITE,  False, pts, max(1, thick_inner))

        for sign, tip_cx in ((-1, left_cx), (+1, right_cx)):
            tip_y = leg_bot + 1
            jitter = math.sin(self.pulse * 9 + (0 if sign < 0 else math.pi / 3))

            # Down-and-outward bolt
            _bolt(surf,
                  [
                      (tip_cx,                 tip_y),
                      (tip_cx + sign * 4,      tip_y + 2),
                      (tip_cx + sign * 1,      tip_y + 4 + int(jitter)),
                      (tip_cx + sign * 5,      tip_y + 6),
                  ],
                  thick_outer=2, thick_inner=1)

            # Sideways crackle
            _bolt(surf,
                  [
                      (tip_cx + sign * 1,      tip_y - 1),
                      (tip_cx + sign * 4,      tip_y),
                      (tip_cx + sign * 2,      tip_y + 2),
                      (tip_cx + sign * 6,      tip_y + 1),
                  ],
                  thick_outer=2, thick_inner=1)

            # Bright dot at the pole tip — discharge origin
            pygame.draw.circle(surf, WHITE,  (tip_cx, tip_y), 2)
            pygame.draw.circle(surf, YELLOW, (tip_cx, tip_y), 1)

    # Megamagnet sprite — the late-game upgrade form of `magnet`.
    # Beefier crimson body (outer_r 13->14, inner_r 6->5, arm width
    # 7->9 px), copper coil wraps down each arm, thick cyan zigzag
    # arc between the pole tips, and glowing yellow-white discharge
    # balls at each pole. Locked-in spec from
    # tools/snapshot_megamagnet_final.py (see
    # docs/screenshots/powerups/megamagnet/icon_final.png).
    def _draw_megamagnet(self, surf):
        cx = int(self.x)
        cy = int(self.y + math.sin(self.pulse * 1.1) * 3)

        OUTER_R, INNER_R = 14, 5
        ARM_W = OUTER_R - INNER_R   # = 9
        # Coil cluster has the legacy 11 px width (HALF_SPAN=5) and is
        # shifted outward asymmetrically — the half-pixel rounding in
        # left_cx puts the legacy tip_cx 0.5 px inside the arm centre,
        # so the left arm wants 1 extra px outward to read centred.
        HALF_SPAN = 5
        LEFT_SHIFT, RIGHT_SHIFT = 2, 1
        BALL_R = 3
        BALL_HALO_R = 7

        arch_cy = cy - 3
        leg_bot = cy + 13

        # Build the horseshoe on an SRCALPHA scratch surface so the
        # hollow can be punched cleanly with alpha=0 overdraw.
        sz = 52
        scx = sz // 2
        scy = OUTER_R + 4

        scratch = pygame.Surface((sz, sz), pygame.SRCALPHA)
        pygame.draw.circle(scratch, (80, 5, 8), (scx, scy), OUTER_R + 2)
        pygame.draw.rect(scratch, (80, 5, 8),
                         (scx - OUTER_R - 2, scy,
                          (OUTER_R + 2) * 2, leg_bot - arch_cy + 4))
        RED_HI = (235, 35, 45)
        pygame.draw.circle(scratch, RED_HI, (scx, scy), OUTER_R + 1)
        pygame.draw.rect(scratch, RED_HI,
                         (scx - OUTER_R - 1, scy,
                          (OUTER_R + 1) * 2, leg_bot - arch_cy + 3))
        pygame.draw.circle(scratch, (255, 95, 95), (scx, scy), INNER_R + 1, 2)
        pygame.draw.circle(scratch, (255, 85, 85), (scx, scy), OUTER_R, 2)
        pygame.draw.circle(scratch, (0, 0, 0, 0), (scx, scy), INNER_R)
        pygame.draw.rect(scratch, (0, 0, 0, 0),
                         (scx - INNER_R, scy, INNER_R * 2, sz - scy))
        surf.blit(scratch, (cx - scx, arch_cy - scy))

        left_cx = cx - INNER_R - ARM_W // 2
        right_cx = cx + INNER_R + ARM_W // 2
        for tip_cx in (left_cx, right_cx):
            pygame.draw.rect(surf, (40, 42, 60),
                             (tip_cx - ARM_W // 2 - 1, leg_bot - 4,
                              ARM_W + 2, 9), border_radius=4)
            pygame.draw.rect(surf, (195, 210, 232),
                             (tip_cx - ARM_W // 2, leg_bot - 3,
                              ARM_W, 7), border_radius=3)
            pygame.draw.rect(surf, (238, 246, 255),
                             (tip_cx - ARM_W // 2 + 1, leg_bot - 3,
                              ARM_W - 2, 3), border_radius=2)

        # Copper coil — 4 wraps per arm with alternating-dip lines.
        COPPER_LO = (110, 55, 14)
        COPPER_HI = (220, 130, 55)
        COPPER_HI_HL = (255, 225, 160)
        for tip_cx, shift in ((left_cx - LEFT_SHIFT, 0),
                              (right_cx + RIGHT_SHIFT, 0)):
            for i in range(4):
                wy = cy + 2 + i * 3
                left_x = tip_cx - HALF_SPAN
                right_x = tip_cx + HALF_SPAN
                mid_x = tip_cx
                dip = 1 if (i % 2 == 0) else -1
                pygame.draw.lines(surf, COPPER_LO, False,
                                  [(left_x, wy + 1),
                                   (mid_x, wy + 1 + dip),
                                   (right_x, wy + 1)], 2)
                pygame.draw.lines(surf, COPPER_HI, False,
                                  [(left_x, wy),
                                   (mid_x, wy + dip),
                                   (right_x, wy)], 1)
                pygame.draw.line(surf, COPPER_HI_HL,
                                 (left_x + 1, wy), (mid_x - 1, wy))

        # Beefy 4 px-thick cyan zigzag arc + yellow-white discharge balls.
        y0 = leg_bot + 7
        arc_pts = [(left_cx, y0)]
        for i in range(1, 6):
            t = i / 6
            ax = int(left_cx + (right_cx - left_cx) * t)
            ay = int(y0 + math.sin(self.pulse * 11 + i * 1.7) * 5)
            arc_pts.append((ax, ay))
        arc_pts.append((right_cx, y0))
        arc_surf = pygame.Surface(
            (right_cx - left_cx + 16, 20), pygame.SRCALPHA)
        shifted = [(p[0] - left_cx + 8, p[1] - y0 + 8) for p in arc_pts]
        pygame.draw.lines(arc_surf, (110, 195, 255, 230), False, shifted, 4)
        pygame.draw.lines(arc_surf, (220, 240, 255, 255), False, shifted, 2)
        surf.blit(arc_surf, (left_cx - 8, y0 - 8))

        for tip_cx in (left_cx, right_cx):
            ball_cy = leg_bot + 2
            glow = pygame.Surface((BALL_HALO_R * 2 + 2, BALL_HALO_R * 2 + 2),
                                  pygame.SRCALPHA)
            gcx = BALL_HALO_R + 1
            for r in range(BALL_HALO_R, 0, -1):
                tt = r / BALL_HALO_R
                a = int(180 * (1 - tt * 0.85))
                pygame.draw.circle(glow, (130, 210, 255, a), (gcx, gcx), r)
            surf.blit(glow, (tip_cx - gcx, ball_cy - gcx))
            pygame.draw.circle(surf, (255, 230, 100),
                               (tip_cx, ball_cy), BALL_R)
            pygame.draw.circle(surf, (255, 255, 240),
                               (tip_cx, ball_cy), max(1, BALL_R - 2))

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

    def _draw_shrink_mushroom(self, surf):
        """Sibling-to-GROW mushroom in red velvet: wide flat parasol disc on
        a flared flat-bottomed stem, cream-butter spots, magenta pulsing
        halo. Reads as the same fungal family as GROW; the silhouette is
        the only thing that distinguishes the two pickups at glance."""
        cx = int(self.x)
        cy = int(self.y + math.sin(self.pulse * 1.1) * 2)
        _draw_grow_halo(surf, cx, cy, self.pulse,
                        color_rgb=_GROW_HALO_RGB, radius=40, peak_y_off=0)
        sprite = _get_shrink_body_sprite()
        surf.blit(sprite, sprite.get_rect(center=(cx, cy)))

    def _draw_rail_icon(self, surf):
        """RAIL pickup — Victorian engraved train ticket (RT2): sepia
        paper card with a thick black outer perimeter, a lighter
        engraved inner border, a small "TRAIN" caption, and a
        detailed steam-locomotive silhouette centred on the card."""
        cx = int(self.x)
        cy = int(self.y + math.sin(self.pulse * 1.0) * 2)

        SS = 6
        NATIVE_W, NATIVE_H = 48, 36
        sw, sh = NATIVE_W * SS, NATIVE_H * SS
        big = pygame.Surface((sw, sh), pygame.SRCALPHA)

        SEPIA      = (228, 210, 170)
        CREAM      = (238, 225, 195)
        NEAR_BLACK = ( 18,  14,  10)
        INK        = ( 30,  25,  20)

        card = pygame.Rect(3 * SS, 3 * SS, sw - 6 * SS, sh - 6 * SS)
        pygame.draw.rect(big, SEPIA, card)
        pygame.draw.rect(big, NEAR_BLACK, card, max(2, int(SS * 1.4)))
        inner = card.inflate(-int(SS * 3.5), -int(SS * 3.5))
        pygame.draw.rect(big, NEAR_BLACK, inner, max(1, int(SS * 0.6)))

        def locomotive(loco_cx, loco_cy, scale=1.0):
            boiler_w = int(SS * 14 * scale)
            boiler_h = int(SS * 6 * scale)
            boiler = pygame.Rect(0, 0, boiler_w, boiler_h)
            boiler.midright = (loco_cx + int(SS * 7 * scale), loco_cy)
            pygame.draw.rect(big, INK, boiler,
                             border_radius=max(1, int(SS * 0.7 * scale)))
            cab_w = int(SS * 5 * scale)
            cab_h = int(SS * 7.5 * scale)
            cab = pygame.Rect(0, 0, cab_w, cab_h)
            cab.midright = (boiler.left, loco_cy)
            pygame.draw.rect(big, INK, cab,
                             border_radius=max(1, int(SS * 0.5 * scale)))
            roof = pygame.Rect(0, 0, cab_w + int(SS * 1.2 * scale),
                                max(1, int(SS * 0.8 * scale)))
            roof.midbottom = (cab.centerx, cab.top + max(1, SS // 3))
            pygame.draw.rect(big, INK, roof)
            stack_w = max(2, int(SS * 1.6 * scale))
            stack_h = max(3, int(SS * 3.2 * scale))
            stack_x = (boiler.right - int(SS * 3.5 * scale) - stack_w // 2)
            stack = pygame.Rect(stack_x, boiler.top - stack_h, stack_w, stack_h)
            pygame.draw.rect(big, INK, stack)
            flare = pygame.Rect(0, 0, int(stack_w * 1.8),
                                 max(1, int(SS * 0.6 * scale)))
            flare.midbottom = (stack.centerx, stack.top)
            pygame.draw.rect(big, INK, flare)
            wheel_r = max(3, int(SS * 2.6 * scale))
            gap = max(1, int(SS * 0.4 * scale))
            wheel_cy = boiler.bottom + wheel_r + gap
            ground_y = wheel_cy + wheel_r
            wheel_xs = (
                boiler.left + int(boiler.width * 0.05),
                boiler.left + int(boiler.width * 0.72),
            )
            cow_top_inner = boiler.bottom - max(1, int(SS * 0.4 * scale))
            cow_outer_x = boiler.right + int(SS * 4 * scale)
            cow_bot_y = ground_y - max(1, int(SS * 0.5 * scale))
            cow_top_outer_y = cow_top_inner + int(SS * 1.5 * scale)
            cow_pts = [
                (boiler.right, cow_top_inner),
                (cow_outer_x, cow_top_outer_y),
                (cow_outer_x, cow_bot_y),
                (boiler.right, cow_bot_y - int(SS * 0.6 * scale)),
            ]
            pygame.draw.polygon(big, INK, cow_pts)
            for f in (0.30, 0.55, 0.80):
                vx = cow_pts[0][0] + int((cow_pts[1][0] - cow_pts[0][0]) * f)
                v_top = cow_top_inner + int(SS * 1 * scale * f)
                v_bot = cow_bot_y - max(1, SS // 3)
                pygame.draw.line(big, CREAM, (vx, v_top), (vx, v_bot),
                                 max(1, SS // 3))
            rod_h = max(2, int(SS * 1.0 * scale))
            rod_y = wheel_cy - int(wheel_r * 0.35) - rod_h // 2
            pygame.draw.rect(big, INK,
                             (wheel_xs[0], rod_y,
                              wheel_xs[1] - wheel_xs[0], rod_h))
            for wx in wheel_xs:
                pygame.draw.circle(big, INK, (wx, wheel_cy), wheel_r)
                for ang_deg in (0, 60, 120, 180, 240, 300):
                    ang = math.radians(ang_deg)
                    x2 = wx + math.cos(ang) * (wheel_r - SS // 2)
                    y2 = wheel_cy + math.sin(ang) * (wheel_r - SS // 2)
                    pygame.draw.line(big, CREAM, (wx, wheel_cy),
                                     (int(x2), int(y2)),
                                     max(1, int(SS * 0.45 * scale)))
                pygame.draw.circle(big, CREAM, (wx, wheel_cy),
                                   max(1, int(SS * 0.7 * scale)))
                pygame.draw.circle(big, INK, (wx, wheel_cy), wheel_r,
                                   max(1, int(SS * 0.35 * scale)))
                pygame.draw.circle(big, CREAM,
                                   (wx, rod_y + rod_h // 2),
                                   max(1, int(SS * 0.6 * scale)))

        f_hdr = _get_float_font(int(SS * 9))
        f_hdr.set_bold(True)
        for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
            hdr = f_hdr.render("TRAIN", True, NEAR_BLACK)
            big.blit(hdr, hdr.get_rect(
                center=(card.centerx + dx,
                         card.top + int(SS * 6.5) + dy)))

        locomotive(card.centerx, card.centery + int(SS * 3.5), scale=1.15)

        tilt = math.sin(self.pulse * 0.7) * 4
        rotated = pygame.transform.rotate(big, tilt)
        rw, rh = rotated.get_size()
        final = pygame.transform.smoothscale(rotated, (rw // SS, rh // SS))
        surf.blit(final, final.get_rect(center=(cx, cy)))

    def _draw_lottery_icon(self, surf):
        """Scratch-off lottery card: gold body with a chrome perimeter,
        a red LUCKY chip riding the top edge, and 3 large silver
        scratch cells each with a single "?"."""
        cx = int(self.x)
        cy = int(self.y + math.sin(self.pulse * 0.8) * 2)

        SS = 6
        NATIVE_W, NATIVE_H = 56, 42
        sw, sh = NATIVE_W * SS, NATIVE_H * SS
        big = pygame.Surface((sw, sh), pygame.SRCALPHA)

        GOLD_HI   = (255, 230, 110)
        GOLD_LO   = (220, 175,  50)
        STROKE    = (110,  75,  10)
        CHROME    = (225, 225, 232)
        SILVER_HI = (245, 245, 252)
        SILVER_LO = (175, 180, 195)
        CREAM     = (255, 245, 200)
        NAVY      = ( 30,  40,  80)
        RED       = (190,  40,  55)
        RED_HI    = (230,  80,  90)

        def vgrad(rect, top_col, bot_col, radius=0):
            tmp = pygame.Surface(rect.size, pygame.SRCALPHA)
            h_ = rect.height
            for y in range(h_):
                t = y / max(1, h_ - 1)
                col = (int(top_col[0] * (1 - t) + bot_col[0] * t),
                       int(top_col[1] * (1 - t) + bot_col[1] * t),
                       int(top_col[2] * (1 - t) + bot_col[2] * t))
                pygame.draw.line(tmp, col, (0, y), (rect.width, y))
            if radius:
                mask = pygame.Surface(rect.size, pygame.SRCALPHA)
                pygame.draw.rect(mask, (255, 255, 255, 255),
                                 mask.get_rect(), border_radius=radius)
                tmp.blit(mask, (0, 0),
                         special_flags=pygame.BLEND_RGBA_MIN)
            big.blit(tmp, rect.topleft)

        def dashed_rect(rect, colour, dash, gap, width):
            def seg(p0, p1):
                x0, y0 = p0
                x1, y1 = p1
                length = math.hypot(x1 - x0, y1 - y0)
                if length <= 0:
                    return
                dx = (x1 - x0) / length
                dy = (y1 - y0) / length
                t = 0.0
                while t < length:
                    t2 = min(t + dash, length)
                    pygame.draw.line(big, colour,
                                     (x0 + dx * t,  y0 + dy * t),
                                     (x0 + dx * t2, y0 + dy * t2),
                                     width)
                    t += dash + gap
            seg((rect.left, rect.top), (rect.right, rect.top))
            seg((rect.right, rect.top), (rect.right, rect.bottom))
            seg((rect.right, rect.bottom), (rect.left, rect.bottom))
            seg((rect.left, rect.bottom), (rect.left, rect.top))

        def silver_cell(rect, radius):
            sub = pygame.Surface(rect.size, pygame.SRCALPHA)
            sub_rect = sub.get_rect()
            tmp = pygame.Surface(rect.size, pygame.SRCALPHA)
            for y in range(rect.height):
                t = y / max(1, rect.height - 1)
                col = (int(SILVER_HI[0] * (1 - t) + SILVER_LO[0] * t),
                       int(SILVER_HI[1] * (1 - t) + SILVER_LO[1] * t),
                       int(SILVER_HI[2] * (1 - t) + SILVER_LO[2] * t))
                pygame.draw.line(tmp, col, (0, y), (rect.width, y))
            mask = pygame.Surface(rect.size, pygame.SRCALPHA)
            pygame.draw.rect(mask, (255, 255, 255, 255),
                             mask.get_rect(), border_radius=radius)
            tmp.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            sub.blit(tmp, (0, 0))
            hatch = pygame.Surface(rect.size, pygame.SRCALPHA)
            for off in range(-rect.height, rect.width,
                              max(8, rect.height // 6)):
                pygame.draw.line(hatch, (180, 185, 200, 90),
                                 (off, 0),
                                 (off + rect.height, rect.height),
                                 max(1, rect.height // 60))
            hatch.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            sub.blit(hatch, (0, 0))
            pygame.draw.rect(sub, NAVY, sub_rect,
                             width=max(1, rect.height // 18),
                             border_radius=radius)
            big.blit(sub, rect.topleft)

        def fit_question_mark(panel, text="?", font_frac=0.95,
                               pad_x_frac=0.18, pad_y_frac=0.18):
            max_w = max(1, panel.width
                        - int(panel.width * pad_x_frac * 2))
            max_h = max(1, panel.height
                        - int(panel.height * pad_y_frac * 2))
            size = max(4, int(panel.height * font_frac))
            while size > 6:
                f = _get_float_font(size)
                w_, h_ = f.size(text)
                if w_ <= max_w and h_ <= max_h:
                    break
                size -= 2
            f = _get_float_font(size)
            sh_ = f.render(text, True, STROKE)
            hl  = f.render(text, True, CREAM)
            tx  = f.render(text, True, NAVY)
            tr = tx.get_rect(center=panel.center)
            big.blit(sh_, sh_.get_rect(center=(tr.centerx + 1,
                                                 tr.centery + 1)))
            big.blit(hl, hl.get_rect(center=(tr.centerx,
                                              tr.centery - 1)))
            big.blit(tx, tr)

        card = pygame.Rect(3 * SS, 3 * SS, sw - 6 * SS, sh - 6 * SS)
        vgrad(card, GOLD_HI, GOLD_LO, radius=4 * SS)
        hi_h = card.height // 3
        hi = pygame.Surface((card.width, hi_h), pygame.SRCALPHA)
        for y in range(hi_h):
            a = int(110 * (1.0 - y / hi_h))
            pygame.draw.line(hi, (255, 250, 220, a),
                             (0, y), (hi.get_width(), y))
        big.blit(hi, (card.x, card.y))
        pygame.draw.rect(big, CHROME, card, width=2 * SS,
                         border_radius=4 * SS)
        inner = card.inflate(-4 * SS, -4 * SS)
        dashed_rect(inner, STROKE, dash=4 * SS, gap=3 * SS,
                    width=max(1, SS // 2))

        chip = pygame.Rect(0, 0, 20 * SS, 5 * SS)
        chip.midtop = (inner.centerx, inner.top + 1)
        vgrad(chip, RED_HI, RED, radius=int(SS * 1.5))
        pygame.draw.rect(big, STROKE, chip, max(1, SS // 2),
                         border_radius=int(SS * 1.5))
        fc = _get_float_font(int(chip.height * 0.88))
        sh_ = fc.render("LUCKY", True, STROKE)
        ct  = fc.render("LUCKY", True, CREAM)
        big.blit(sh_, sh_.get_rect(center=(chip.centerx + 1,
                                             chip.centery + 1)))
        big.blit(ct, ct.get_rect(center=chip.center))

        cell_top = chip.bottom + 2 * SS
        cell_bot = inner.bottom - 2 * SS
        cell_h = cell_bot - cell_top
        gap = 1 * SS
        cell_w = (inner.width - 4 * SS - 2 * gap) // 3
        for i in range(3):
            x0 = inner.left + 2 * SS + i * (cell_w + gap)
            cell = pygame.Rect(x0, cell_top, cell_w, cell_h)
            silver_cell(cell, radius=int(SS * 1.5))
            fit_question_mark(cell)

        tilt = math.sin(self.pulse * 0.7) * 5
        rotated = pygame.transform.rotate(big, tilt)
        rw, rh = rotated.get_size()
        final = pygame.transform.smoothscale(rotated, (rw // SS, rh // SS))
        surf.blit(final, final.get_rect(center=(cx, cy)))

    def _draw_skateboard_icon(self, surf):
        """SKATEBOARD pickup token (punk skull-bunny over crossed decks). The
        art is static and built ONCE (_build_skate_icon); per frame we only
        blit it at the bobbing position, so the 96px/6x supersample rebuild
        (~1.2 ms, ×3 when the genie lays out its offers) no longer runs every
        frame."""
        global _SKATE_ICON_SPRITE
        if _SKATE_ICON_SPRITE is None:
            _SKATE_ICON_SPRITE = PowerUp._build_skate_icon()
        cx = int(self.x)
        cy = int(self.y + math.sin(self.pulse * 1.0) * 2)
        surf.blit(_SKATE_ICON_SPRITE,
                  _SKATE_ICON_SPRITE.get_rect(center=(cx, cy)))

    @staticmethod
    def _build_skate_icon():
        """Build the static skateboard pickup token (6x supersample → 68px)."""

        DOME   = (10, 10, 18)
        CHROME = (200, 200, 210)
        BONE   = (240, 240, 230)
        CREAM  = (245, 240, 230)
        RED    = (200, 50, 50)

        SS = 6
        # AUTHORED_N is the footprint the icon recipe was DESIGNED at —
        # every shape inside this function is sized in absolute SS units
        # (e.g. ear = 7*SS), so shrinking the canvas without preserving
        # the authored scale clips the X boards and inflates the face.
        # DISPLAY_N is the size production actually shows on the playfield.
        # We render at AUTHORED_N to keep the original proportions, then
        # smoothscale once to DISPLAY_N at the end.
        AUTHORED_N = 96
        DISPLAY_N  = 68
        # FACE_SCALE shrinks the skull-bunny face block (ears + skull +
        # eyes + nose + mouth + bandage + bow) while leaving the X-board
        # backdrop at original size. User picked 0.88 from the F1..F5
        # face-scale variant sheet.
        FACE_SCALE = 0.88
        big = pygame.Surface((AUTHORED_N * SS, AUTHORED_N * SS),
                             pygame.SRCALPHA)
        bx = big.get_width() // 2
        by = big.get_height() // 2

        for angle in (35, -35):
            sub_w = 64 * SS
            sub_h = 9 * SS
            sub = pygame.Surface(
                (sub_w + 4 * SS, sub_h + 4 * SS), pygame.SRCALPHA)
            d = pygame.Rect(0, 0, sub_w, sub_h)
            d.center = (sub.get_width() // 2, sub.get_height() // 2)
            pygame.draw.rect(sub, CHROME, d, border_radius=2 * SS)
            pygame.draw.rect(sub, DOME,
                             d.inflate(-2 * SS, -2 * SS),
                             border_radius=SS)
            for sign in (-1, 1):
                wx = d.centerx + sign * (sub_w // 2 - 3 * SS)
                pygame.draw.circle(sub, CREAM, (wx, d.centery),
                                   int(3 * SS))
                pygame.draw.circle(sub, RED, (wx, d.centery),
                                   int(1.4 * SS))
            rotated = pygame.transform.rotate(sub, angle)
            big.blit(rotated, rotated.get_rect(center=(bx, by)))

        FS = FACE_SCALE
        ear_centers = {}
        for sign in (-1, 1):
            er = pygame.Rect(0, 0, int(7 * SS * FS), int(28 * SS * FS))
            er.center = (bx + sign * int(9 * SS * FS),
                         by - int(22 * SS * FS))
            ang = -12 * sign
            ear_sub = pygame.Surface(
                (er.width + 4 * SS, er.height + 4 * SS),
                pygame.SRCALPHA)
            local = pygame.Rect(0, 0, er.width, er.height)
            local.center = (ear_sub.get_width() // 2,
                            ear_sub.get_height() // 2)
            pygame.draw.ellipse(ear_sub, BONE, local)
            pygame.draw.ellipse(ear_sub, DOME, local,
                                max(1, int(1.2 * SS * FS)))
            inner = local.inflate(-int(2.5 * SS * FS), -int(8 * SS * FS))
            pygame.draw.ellipse(ear_sub, RED, inner)
            rot = pygame.transform.rotate(ear_sub, ang)
            big.blit(rot, rot.get_rect(center=er.center))
            ear_centers[sign] = er.center

        SK_W = max(2, int(44 * FS))
        SK_H = max(2, int(38 * FS))
        sk = pygame.Rect(0, 0, SK_W * SS, SK_H * SS)
        sk.center = (bx, by + int(2 * SS * FS))
        pygame.draw.ellipse(big, BONE, sk)
        pygame.draw.ellipse(big, DOME, sk, max(1, int(1.4 * SS * FS)))

        eye_r = max(1, int(SK_W * SS * 0.13))
        eye_x_off = int(SK_W * SS * 0.20)
        eye_y = sk.top + int(SK_H * SS * 0.38)
        for sign in (-1, 1):
            ex = sk.centerx + sign * eye_x_off
            pygame.draw.circle(big, DOME, (ex, eye_y), eye_r)

        cross_cx = sk.centerx - eye_x_off
        cross_cy = eye_y
        bar_l = max(2, int(7 * SS * FS))
        bar_t = max(1, int(2.2 * SS * FS))
        horiz = pygame.Rect(0, 0, bar_l, bar_t)
        horiz.center = (cross_cx, cross_cy)
        vert = pygame.Rect(0, 0, bar_t, bar_l)
        vert.center = (cross_cx, cross_cy)
        rad = max(1, int(0.5 * SS * FS))
        pygame.draw.rect(big, RED, horiz, border_radius=rad)
        pygame.draw.rect(big, RED, vert, border_radius=rad)
        pygame.draw.rect(big, DOME, horiz, max(1, SS // 3),
                         border_radius=rad)
        pygame.draw.rect(big, DOME, vert, max(1, SS // 3),
                         border_radius=rad)

        nose_top_y = sk.top + int(SK_H * SS * 0.55)
        nose_bot_y = nose_top_y + max(1, int(3 * SS * FS))
        nose_w = max(1, int(1.4 * SS * FS))
        pygame.draw.polygon(big, DOME, [
            (sk.centerx - nose_w, nose_top_y),
            (sk.centerx + nose_w, nose_top_y),
            (sk.centerx,          nose_bot_y),
        ])

        # Curly Jolly Roger mouth: 3 vertical teeth (outer two shorter)
        # connected by a sine-arc dip between adjacent pairs. Recipe
        # scales proportional to SK_W from the original S4 base of 23.
        mouth_scale = SK_W / 23.0
        mouth_stroke = max(1, int(1.2 * SS * mouth_scale))
        teeth_top = sk.bottom - int(7 * SS * mouth_scale)
        teeth_bot = sk.bottom - int(4 * SS * mouth_scale)
        divider_offsets = (-int(4 * SS * mouth_scale), 0,
                           int(4 * SS * mouth_scale))
        outer_shorten = max(1, int(1.0 * SS * mouth_scale))
        tooth_bottoms = []
        for idx, dx in enumerate(divider_offsets):
            top_y = teeth_top + (outer_shorten if idx != 1 else 0)
            pygame.draw.line(big, DOME,
                             (sk.centerx + dx, top_y),
                             (sk.centerx + dx, teeth_bot),
                             mouth_stroke)
            tooth_bottoms.append((sk.centerx + dx, teeth_bot))
        dip = max(2, int(1.6 * SS * mouth_scale))
        for (x0, y0), (x1, y1) in zip(tooth_bottoms, tooth_bottoms[1:]):
            pts = []
            for i in range(15):
                t = i / 14
                x = x0 + (x1 - x0) * t
                y_base = y0 + (y1 - y0) * t
                y = y_base + dip * math.sin(math.pi * t)
                pts.append((x, y))
            pygame.draw.lines(big, DOME, False, pts, mouth_stroke)

        knot_cx, knot_cy = ear_centers[-1]
        knot_cy = knot_cy + int(11 * SS * FS)
        knot_cx = knot_cx + int(3 * SS * FS)
        bow_w = max(1, int(5 * SS * FS))
        bow_h = max(1, int(3 * SS * FS))
        bow_left = [
            (knot_cx - bow_w,                knot_cy - bow_h),
            (knot_cx - int(0.5 * SS * FS),   knot_cy),
            (knot_cx - bow_w,                knot_cy + bow_h),
        ]
        bow_right = [
            (knot_cx + bow_w,                knot_cy - bow_h),
            (knot_cx + int(0.5 * SS * FS),   knot_cy),
            (knot_cx + bow_w,                knot_cy + bow_h),
        ]
        pygame.draw.polygon(big, RED, bow_left)
        pygame.draw.polygon(big, RED, bow_right)
        pygame.draw.circle(big, RED, (knot_cx, knot_cy),
                           max(1, int(1.5 * SS * FS)))
        pygame.draw.polygon(big, DOME, bow_left, max(1, SS // 3))
        pygame.draw.polygon(big, DOME, bow_right, max(1, SS // 3))

        return pygame.transform.smoothscale(big, (DISPLAY_N, DISPLAY_N))

    def _draw_knight_icon(self, surf):
        """In-world KNIGHT pickup — the K7 heater shield."""
        from game import knight_skin
        cx = int(self.x)
        cy = int(self.y + math.sin(self.pulse * 0.9) * 2)
        knight_skin.draw_shield_icon(surf, cx, cy, size=44)

    def _draw_genie_icon(self, surf):
        """In-world genie lamp pickup — Amber Crystal cut-glass lamp,
        rendered once at SS=8 and cached in game._lamp_assets; per frame we
        just tilt + bob + blit the cached sprite."""
        from game._lamp_assets import get_lamp_sprite

        cx = int(self.x)
        cy = int(self.y + math.sin(self.pulse * 0.9) * 2)
        sprite = get_lamp_sprite(target_height=72)
        tilt = math.sin(self.pulse * 0.8) * 3
        rotated = pygame.transform.rotate(sprite, tilt)
        surf.blit(rotated, rotated.get_rect(center=(cx, cy)))

    def _draw_poison_vial(self, surf):
        """Poison vial trap — only reachable via the genie offer. Sprite
        machinery lives in game.poison_vial (cached static flask + label;
        breathing yellow-green halo drawn live)."""
        from game import poison_vial

        cx = int(self.x)
        cy = int(self.y + math.sin(self.pulse * 0.9) * 2)
        poison_vial.draw(surf, cx, cy, self.pulse)


# ── Shrink mushroom sprite (sibling to GROW's body sprite) ───────────────────
# Same red velvet palette + cream-butter spots + magenta halo as GROW so
# the two pickups read as one fungal family. Built at supersample then
# smoothscaled and cached.
_SHRINK_SS = 5
_SHRINK_CAP_W,  _SHRINK_CAP_H  = 30, 8
_SHRINK_STEM_W, _SHRINK_STEM_H = 14, 22
_SHRINK_VELVET_OUTLINE = ( 60,  15,  25)
_SHRINK_VELVET_BODY    = MUSH_CAP
_SHRINK_VELVET_HI      = MUSH_CAP2
_SHRINK_SPOT_HALO      = (195, 165, 110)
_SHRINK_STEM_OUTLINE   = (150, 120,  90)
_SHRINK_STEM_HI        = (255, 250, 230)

_SHRINK_ORNAMENT_SLOTS = (
    (0.18, 0.48),
    (0.40, 0.30),
    (0.62, 0.55),
    (0.82, 0.36),
)

_shrink_body_sprite: "pygame.Surface | None" = None

def _get_shrink_body_sprite() -> "pygame.Surface":
    global _shrink_body_sprite
    if _shrink_body_sprite is not None:
        return _shrink_body_sprite
    SS = _SHRINK_SS
    CAP_W, CAP_H = _SHRINK_CAP_W, _SHRINK_CAP_H
    STEM_W, STEM_H = _SHRINK_STEM_W, _SHRINK_STEM_H
    sprite_w = max(CAP_W, STEM_W) + 2
    sprite_h = CAP_H + STEM_H + 4
    big = pygame.Surface((sprite_w * SS, sprite_h * SS), pygame.SRCALPHA)
    cap_ox  = ((sprite_w - CAP_W)  // 2) * SS
    cap_oy  = 0
    stem_ox = ((sprite_w - STEM_W) // 2) * SS
    stem_oy = (CAP_H + 2) * SS

    stem_pts = [
        (int(0.42 * STEM_W * SS), int(0.00 * STEM_H * SS)),
        (int(0.58 * STEM_W * SS), int(0.00 * STEM_H * SS)),
        (int(0.66 * STEM_W * SS), int(0.40 * STEM_H * SS)),
        (int(0.78 * STEM_W * SS), int(0.66 * STEM_H * SS)),
        (int(0.96 * STEM_W * SS), int(0.88 * STEM_H * SS)),
        (int(0.96 * STEM_W * SS), int(1.00 * STEM_H * SS)),
        (int(0.04 * STEM_W * SS), int(1.00 * STEM_H * SS)),
        (int(0.04 * STEM_W * SS), int(0.88 * STEM_H * SS)),
        (int(0.22 * STEM_W * SS), int(0.66 * STEM_H * SS)),
        (int(0.34 * STEM_W * SS), int(0.40 * STEM_H * SS)),
    ]
    stem_pts = [(p[0] + stem_ox, p[1] + stem_oy) for p in stem_pts]
    pygame.draw.polygon(big, MUSH_STEM,            stem_pts)
    pygame.draw.polygon(big, _SHRINK_STEM_OUTLINE, stem_pts, width=SS)
    hi_x = stem_ox + int(0.40 * STEM_W * SS)
    pygame.draw.line(big, _SHRINK_STEM_HI,
                     (hi_x, stem_oy + int(0.10 * STEM_H * SS)),
                     (hi_x, stem_oy + int(0.78 * STEM_H * SS)), SS)

    outer = pygame.Rect(cap_ox, cap_oy, CAP_W * SS, CAP_H * SS)
    inner = outer.inflate(-SS * 2, -SS * 2)
    pygame.draw.ellipse(big, _SHRINK_VELVET_OUTLINE, outer)
    pygame.draw.ellipse(big, _SHRINK_VELVET_BODY,    inner)
    pygame.draw.ellipse(big, _SHRINK_VELVET_HI,
                        pygame.Rect(cap_ox + int(CAP_W * SS * 0.20),
                                    cap_oy + int(CAP_H * SS * 0.10),
                                    int(CAP_W * SS * 0.50),
                                    int(CAP_H * SS * 0.32)))
    pygame.draw.ellipse(big, _SHRINK_VELVET_OUTLINE,
                        pygame.Rect(cap_ox + SS,
                                    cap_oy + int(CAP_H * SS * 0.65),
                                    (CAP_W - 2) * SS,
                                    int(CAP_H * SS * 0.55)))

    for fx_frac, fy_frac in _SHRINK_ORNAMENT_SLOTS:
        fx = cap_ox + int(CAP_W * fx_frac * SS)
        fy = cap_oy + int(CAP_H * fy_frac * SS)
        r_body = 1.7
        pygame.draw.circle(big, _SHRINK_SPOT_HALO, (fx, fy),
                           int((r_body + 0.4) * SS))
        pygame.draw.circle(big, MUSH_SPOT, (fx, fy), int(r_body * SS))
        pygame.draw.circle(big, (255, 250, 220),
                           (fx - SS // 2, fy - SS // 2), max(1, SS // 2))

    _shrink_body_sprite = pygame.transform.smoothscale(big, (sprite_w, sprite_h))
    return _shrink_body_sprite


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


# ── Magic-dust mote + PoofGrain (genie poofs) ─────────────────────────────────

_MOTE_CACHE: dict = {}


def _mote_sprite(size, alpha, color):
    """Cached soft mote: a small disc with a gentle alpha falloff so that
    many overlapping motes blend into a continuous CLOUD rather than reading
    as separate hard specks. Cached by (size, alpha bucket, colour)."""
    size = max(2, int(size))
    ab = max(16, min(255, (int(alpha) // 16) * 16))
    key = (size, ab, color)
    spr = _MOTE_CACHE.get(key)
    if spr is None:
        d = size * 2
        spr = pygame.Surface((d, d), pygame.SRCALPHA)
        c = size
        steps = max(2, size)
        for i in range(steps, 0, -1):
            rr = max(1, int(size * i / steps))
            frac = i / steps                       # 1 rim → ~0 centre
            a = int(ab * (1.0 - 0.85 * frac))      # soft edge, solid core
            pygame.draw.circle(spr, (*color, a), (c, c), rr)
        _MOTE_CACHE[key] = spr
    return spr


class PoofGrain:
    """A single mote of MAGIC DUST — a small soft speck that drifts outward,
    slows like settling dust, twinkles faintly, and fades. Spawned in LARGE,
    DENSE numbers so the burst reads as a continuous cloud, not confetti."""
    __slots__ = ("x", "y", "vx", "vy", "life", "life_max", "size",
                 "color", "_ph")

    def __init__(self, x, y, vx, vy, life, size, color):
        self.x, self.y   = float(x), float(y)
        self.vx, self.vy = vx, vy
        self.life = self.life_max = life
        self.size = size
        self.color = color
        self._ph = random.uniform(0, math.tau)   # per-mote twinkle phase

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        # Ease to a near-stop so the dust hangs and settles.
        self.vx *= 0.90
        self.vy *= 0.90
        self.vy += 18 * dt
        self.life -= dt

    def alive(self):
        return self.life > 0

    def draw(self, surf):
        t = max(0.0, self.life / self.life_max)      # 1→0 as it dies
        age = self.life_max - self.life
        tw = 0.80 + 0.20 * math.sin(self._ph + age * 20.0)
        alpha = int(200 * t * tw)
        if alpha <= 0:
            return
        spr = _mote_sprite(self.size, alpha, self.color)
        surf.blit(spr, (int(self.x - self.size), int(self.y - self.size)))


# ── GenieCharacter (companion actor summoned by the Genie lamp) ───────────────

def _lazy_import_genie_design():
    """Import the consolidated genie-design module (palette, helpers, body-part
    drawing functions) from game/_genie_assets.py. The 5-tuple shape is kept so
    callers `_ref, _legs, _arms, _shines, _carpets = _lazy_import_genie_design()`
    keep working — all five re-bind the same consolidated module."""
    if hasattr(_lazy_import_genie_design, "_cached"):
        return _lazy_import_genie_design._cached
    from game import _genie_assets as _ga
    cache = (_ga, _ga, _ga, _ga, _ga)
    _lazy_import_genie_design._cached = cache
    return cache


class GenieCharacter:
    """Conjured genie that hovers ahead of Pip and casts three Genie offer
    powerups. Procedural sprite drawn from game/_genie_assets.py, translucent
    so it reads as summoned smoke given form.

    Phases driven by ``_t / DURATION``:
      RISE   (0.00–0.85) fade in + scale 0.3→1.0 + smoke trails
      CAST   (at 1.10)   ALL 3 offers POOF into existence simultaneously
      HOLD   (1.10–2.60) genie stays put; ~1.5 s to manoeuvre to an offer
      VANISH (2.60–3.30) collapse into smoke + fade out

    The genie is STATIONARY (vx=0). World owns ``self.genie_actors``; each tick
    calls ``update(dt)`` and ``draw(surf)``; ``alive()`` returns False when the
    vanish phase completes so World sweeps it from the list."""

    DURATION       = 3.30
    RISE_END       = 0.85
    CAST_BEAT      = 1.10        # single moment — all 3 offers poof
    VANISH_START   = 2.60        # ~1.5 s hold after cast for user
    VANISH_END     = 3.30

    def __init__(self, x, y, vx, offers, world):
        # offers: list of (kind, target_y) pairs.
        self.x, self.y = float(x), float(y)
        self.vx = vx
        self.offers = list(offers)
        self.world = world
        self._t = 0.0
        self._fired = False
        self._vanished = False
        self._tail_clock = 0.0
        self._dead = False
        self._native_w = 320
        self._native_h = 460
        self._ss = 6
        self._display_scale = 0.42
        self._palm_dx = 58
        self._palm_dy = -20
        # Render the genie once at 6x supersample for clean edges, then
        # downsample to NATIVE here, once. _blit_sprite re-scales the body
        # to its (always smaller) on-screen size every frame; scaling from
        # this ~320x460 native cache instead of the full ~1920x2760
        # supersample is ~16x less pixel work per frame — the genie is on
        # screen for its whole ~3.3 s life, so smoothscaling 5.3 MP every
        # frame was a real per-frame stutter, badly so on the WASM target.
        self._cached_body = pygame.transform.smoothscale(
            self._render_body_supersample(),
            (self._native_w, self._native_h))
        self._spawn_appear_poof()

    def update(self, dt):
        self.x += self.vx * dt
        self._t += dt
        if (not self._fired) and self._t >= self.CAST_BEAT:
            self._fire_all()
            self._fired = True
        if self._t < self.RISE_END:
            self._tail_clock += dt
            while self._tail_clock >= 0.08:
                self._tail_clock -= 0.08
                self._spawn_tail_wisp()
        if ((not self._vanished) and (not self._dead)
                and self._t >= self.VANISH_START):
            self._spawn_vanish_swirl()
            self._vanished = True

    def alive(self):
        return (not self._dead) and self._t < self.VANISH_END

    def kill(self):
        # Called when the player picks one of the offers before the genie
        # finishes casting — stop spawning anything else.
        self._dead = True

    def palm_world_pos(self, side):
        ds = self._display_scale
        return (self.x + side * self._palm_dx * ds,
                self.y + self._palm_dy * ds)

    def _fire_all(self):
        """Single cast moment — spawn all offer powerups + their reveal poofs
        + one combined chime simultaneously, far ahead of Pip so the player
        has time to manoeuvre to whichever they want."""
        if self._dead:
            return
        import random as _r
        slot_ys = [oy for _, oy in self.offers]
        positions = self._pick_offer_positions(slot_ys)
        for (kind, _slot_y), (ox, oy) in zip(self.offers, positions):
            offer = PowerUp(ox, oy, kind=kind)
            offer.is_genie_offer = True
            self.world.powerups.append(offer)
            self.world._spawn_genie_reveal_poof(ox, oy)
        try:
            from game import audio
            audio._play("coin_triple", 0.95)
        except Exception:
            pass
        gx_centre = int(self.x)
        gy_centre = int(self.y)
        for _ in range(14):
            ang = _r.uniform(0, math.pi * 2)
            sp = _r.uniform(80, 180)
            self.world.particles.append(CloudPuff(
                gx_centre, gy_centre,
                math.cos(ang) * sp, math.sin(ang) * sp - 40,
                _r.uniform(0.30, 0.50),
                6, 16,
                _r.choice([(255, 240, 175), (255, 220, 130),
                           (240, 200, 250), (255, 255, 245)]),
            ))

    def _pick_offer_positions(self, slot_ys):
        """Pick a unique (x, y) per offer: far from Pip (≥ MIN_PARROT_DIST),
        not clustered (≥ MIN_OFFER_DIST apart), not inside a pillar body, with
        varied x and jittered y. Rejection sampling with a deterministic
        fallback after 40 attempts."""
        from game.config import PIPE_W
        import random as _r
        bird_x = self.world.bird.x
        bird_y = self.world.bird.y
        pipe_half = PIPE_W / 2
        offer_half = 18
        clearance = pipe_half + offer_half + 6
        X_MIN_AHEAD, X_MAX_AHEAD = 180, 280
        Y_JITTER = 30
        MIN_PARROT_DIST = 200
        MIN_OFFER_DIST  = 90
        positions = []
        for slot_y in slot_ys:
            picked = None
            for _ in range(40):
                x = bird_x + _r.randint(X_MIN_AHEAD, X_MAX_AHEAD)
                y = slot_y + _r.randint(-Y_JITTER, Y_JITTER)
                dx, dy = x - bird_x, y - bird_y
                if dx * dx + dy * dy < MIN_PARROT_DIST * MIN_PARROT_DIST:
                    continue
                too_close = False
                for px, py in positions:
                    if (x - px) * (x - px) + (y - py) * (y - py) < \
                            MIN_OFFER_DIST * MIN_OFFER_DIST:
                        too_close = True
                        break
                if too_close:
                    continue
                blocked = False
                for p in self.world.pipes:
                    if abs(p.x - x) < clearance:
                        gap_top = p.gap_y - p.gap_h / 2
                        gap_bot = p.gap_y + p.gap_h / 2
                        if not (gap_top <= y <= gap_bot):
                            blocked = True
                            break
                if blocked:
                    continue
                picked = (x, y)
                break
            if picked is None:
                picked = (bird_x + 230, slot_y)
            positions.append(picked)
        return positions

    def _spawn_tail_wisp(self):
        import random as _r
        cx = self.x - 14
        cy = self.y + 38
        for _ in range(2):
            vx = -_r.uniform(20, 50) + self.vx * 0.3
            vy = _r.uniform(10, 30)
            life = _r.uniform(0.35, 0.55)
            color = _r.choice([(230, 220, 250), (215, 200, 240),
                               (200, 180, 230)])
            self.world.particles.append(CloudPuff(
                cx, cy, vx, vy, life, 3, 11, color))

    def _spawn_appear_poof(self):
        ow = self._native_w * self._display_scale
        oh = self._native_h * self._display_scale
        self.world._spawn_grainy_poof(self.x, self.y,
                                      rx=ow * 0.50, ry=oh * 0.48)

    def _spawn_vanish_swirl(self):
        ow = self._native_w * self._display_scale
        oh = self._native_h * self._display_scale
        self.world._spawn_grainy_poof(self.x, self.y,
                                      rx=ow * 0.50, ry=oh * 0.48)

    def draw(self, surf):
        t = self._t
        if t < self.RISE_END:
            k = t / self.RISE_END
            scale = 0.3 + 0.7 * (1 - (1 - k) ** 2)        # ease-out
            alpha = int(210 * k)
            bob   = -10 * (1 - k)
        elif t < self.VANISH_START:
            scale = 1.0
            alpha = 210
            bob   = math.sin(t * 4.5) * 5.0
        else:
            k = (t - self.VANISH_START) / (self.VANISH_END - self.VANISH_START)
            scale = 1.0 - 0.4 * k
            alpha = int(210 * (1 - k))
            bob   = -18 * k
        if alpha <= 2:
            return
        self._blit_sprite(surf, alpha, scale, bob)

    def _blit_sprite(self, surf, alpha, scale, bob):
        eff = scale * self._display_scale
        out_w = max(2, int(self._native_w * eff))
        out_h = max(2, int(self._native_h * eff))
        scaled = pygame.transform.smoothscale(self._cached_body,
                                              (out_w, out_h))
        sway = math.sin(self._t * 1.4) * 3.0
        rotated = pygame.transform.rotate(scaled, sway)
        rotated.set_alpha(alpha)
        rect = rotated.get_rect(center=(int(self.x), int(self.y + bob)))
        surf.blit(rotated, rect.topleft)

    def _render_body_supersample(self):
        """Build the full lotus-genie body into a supersample surface by
        calling the consolidated _genie_assets drawing functions."""
        _ref, _legs, _arms, _shines, _carpets = _lazy_import_genie_design()
        SS = _ref.SS         # 6
        W = _ref.W           # 320
        H = _ref.H           # 460
        big = pygame.Surface((W * SS, H * SS), pygame.SRCALPHA)
        cx = (W * SS) // 2
        _carpets.draw_carpet_royal(big, cx)
        _legs.draw_crossed_legs_ankle_cross(big, cx)
        _ref.draw_torso(big, cx)
        _ref.draw_neck(big, cx)
        head_cy = _ref.s(60)
        head_r = _ref.s(40)
        _ref.draw_head(big, cx, head_cy, head_r)
        _ref.draw_face(big, cx, head_cy)
        _ref.draw_earrings(big, cx, head_cy, head_r)
        _ref.draw_topknot_and_headband(big, cx, head_cy, head_r)
        _ref.draw_sash(big, cx)
        _shines.draw_offering_arms_with_shine(
            big, cx, _shines.shine_1_classic_pixie)
        return big


# ── Geyser (morning-thermal updraft) ──────────────────────────────────────────

from game import geyser_fx


class Geyser:
    """A ground vent that cycles dormant → telegraph → active → dormant.

    While active its hot-air column lifts the bird (the lift force itself is
    applied in World, which owns the bird). Active and dormant durations are
    seeded from the thermal intensity at spawn time, so early-window geysers
    sit mostly dormant and peak-window ones are active often — the
    sparse→frequent build-up. The lift zone is a vertical band that stops at
    the column top (mid-screen), so the updraft can never pin Pip to the
    ceiling."""

    __slots__ = ("x", "intensity", "active_len", "dormant_len", "phase",
                 "t", "active", "active_strength", "_anim_t")

    def __init__(self, x, intensity):
        intensity = max(0.0, min(1.0, intensity))
        self.x = float(x)
        self.intensity = intensity
        # Unused now (kept for slot compatibility) — geysers are always-on.
        self.active_len = 0.0
        self.dormant_len = 0.0
        # ALWAYS erupting: no dormant/telegraph cycle. The hot air is on the
        # whole time the geyser is on screen — a continuous full-height
        # column + continuous updraft.
        self.phase = "active"
        self.t = 0.0
        self.active = True
        self.active_strength = 1.0
        self._anim_t = random.uniform(0.0, 10.0)

    def update(self, dt):
        # Always active — only the steam animation clock advances.
        self._anim_t += dt

    def contains(self, bx, by):
        """True if (bx, by) is inside the lift column. The column spans the
        full screen height, so the air pushes Pip up anywhere within its
        width, all the way to the top."""
        if not self.active:
            return False
        return (abs(bx - self.x) <= GEYSER_W * 0.5
                and (GROUND_Y - GEYSER_H) <= by <= GROUND_Y)

    def off_screen(self):
        return self.x + GEYSER_W < 0

    def draw(self, surf):
        cx = int(self.x)
        base_y = GROUND_Y

        # Sinter-cone vent at the base.
        surf.blit(geyser_fx.get_vent_cone(),
                  (cx - geyser_fx.CONE_W // 2, base_y - geyser_fx.CONE_BASE_ROW))

        # Erupting steam column — only on active geysers. Duds (active=False)
        # show the cone + base ring on the ground but no rising hot air.
        # Pre-baked looping frames; per-geyser _anim_t offset desyncs neighbours.
        if self.active:
            frame = geyser_fx.get_steam_frames()[
                int(self._anim_t * geyser_fx.STEAM_FPS) % geyser_fx.STEAM_N]
            mouth_y = base_y - geyser_fx.MOUTH_DY
            surf.blit(frame, (cx - geyser_fx.STEAM_W // 2, mouth_y - geyser_fx.STEAM_H))


# ── Rock (morning-thermal ground decoration) ─────────────────────────────────


class Rock:
    """A scattered sinter rock that drifts past with the ground during the
    morning-thermal window. Spawn density scales with the thermal intensity
    (sparse buildup → dense → fade). Pure decoration: the world scrolls its x;
    the sprite itself is pre-baked in geyser_fx."""

    __slots__ = ("x", "y", "variant")

    def __init__(self, x, y, variant):
        self.x = float(x)
        self.y = float(y)
        self.variant = variant

    def off_screen(self):
        return self.x + geyser_fx.ROCK_MAX_W < 0

    def draw(self, surf):
        s, ox, oy = geyser_fx.get_rock_variants()[self.variant]
        surf.blit(s, (int(self.x - ox), int(self.y - oy)))


class RockPatch:
    """A whole pillar's scattered-rock cluster pre-baked into ONE surface. The
    thermal field can put 100s of rocks on screen; baking each pillar's scatter
    into a single patch keeps it to one blit per pillar instead of one per rock —
    a big saving on the WASM blit path. Same world-scroll + cull contract as Rock
    (duck-typed: x / off_screen / draw), so World treats the two interchangeably."""

    __slots__ = ("x", "y", "_surf", "_w")

    def __init__(self, x, y, surf):
        self.x = float(x)
        self.y = float(y)
        self._surf = surf
        self._w = surf.get_width()

    def off_screen(self):
        return self.x + self._w < 0

    def draw(self, surf):
        surf.blit(self._surf, (int(self.x), int(self.y)))


# ── FloatText ────────────────────────────────────────────────────────────────

_float_font_cache: dict = {}

import os as _os

_FLOAT_FONT_DIR = _os.path.join(_os.path.dirname(__file__), "assets")
_FLOAT_BOLD = _os.path.join(_FLOAT_FONT_DIR, "LiberationSans-Bold.ttf")
# Regular variant retired; see game/hud.py for the rationale. The
# `bold=False` parameter is kept for source-level call-site
# compatibility but all renders now use the Bold face.


def _get_float_font(size, bold=True):
    key = (size, True)
    f = _float_font_cache.get(key)
    if f is None:
        f = pygame.font.Font(_FLOAT_BOLD, size)
        _float_font_cache[key] = f
    return f


# Per-trick fill + halftone-dot colours for the SKATEBOARD comic
# bubble that replaces the old gradient float-text. Base hues are
# pulled from the existing float-text colours so each trick keeps
# its identity colour; dot colours are a darker variant for
# Lichtenstein contrast inside the burst.
TRICK_BUBBLE_PALETTE = {
    "BACKFLIP!":   ((110, 230, 110), ( 30,  90,  40)),
    "KICKFLIP!":   ((120, 200, 235), ( 30,  70, 130)),
    "HEELFLIP!":   ((170, 140, 230), ( 70,  40, 130)),
    "POP SHUVIT!": ((230, 130, 180), (120,  30,  90)),
    "NOSE GRIND!": ((255, 215, 110), (180, 120,  30)),
    "TAIL GRIND!": ((255, 215, 110), (180, 120,  30)),
}


class TrickBubble:
    """SKATEBOARD trick name rendered as a tilted comic halftone-burst
    bubble. The bubble surface is pre-rendered once on construction
    (label and tilt are immutable) and cached as `_surf`; `draw` just
    blits it with a per-frame alpha derived from the bubble's
    remaining life.

    Lifetime ~1.4 s: snappy POP-IN at full alpha (no fade-in delay)
    + 0.4 s linear fade-out so stacking bubbles appear immediately
    and exit gracefully when their life runs out."""

    __slots__ = ("x", "y", "life", "life_max", "_surf")

    def __init__(self, label, x, y, tilt_deg=0.0, life=1.4):
        from game.skateboard_fx import (
            _halftone_filled_burst, _gradient_text, INK,
        )
        self.x = x
        self.y = y
        self.life = life
        self.life_max = life
        base, dot = TRICK_BUBBLE_PALETTE.get(
            label, ((255, 220, 30), (230, 60, 50)))
        font_size = 16
        font = _get_float_font(font_size)
        tw, _th = font.size(label)
        ro = max(50, tw // 2 + 16)
        ri = max(28, ro - 24)
        sw = sh = ro * 2 + 24
        bsurf = pygame.Surface((sw, sh), pygame.SRCALPHA)
        bcx, bcy = sw // 2, sh // 2
        _halftone_filled_burst(bsurf, bcx, bcy, ro, ri, spikes=10,
                               dot_col=dot, base_col=base)
        txt = _gradient_text(label, font_size,
                             top_col=(255, 250, 240),
                             bot_col=base,
                             outline=INK, outline_w=3)
        bsurf.blit(txt, txt.get_rect(center=(bcx, bcy)))
        if abs(tilt_deg) > 0.5:
            bsurf = pygame.transform.rotate(bsurf, tilt_deg)
        self._surf = bsurf

    def update(self, dt):
        self.life -= dt

    def alive(self):
        return self.life > 0

    def draw(self, surf):
        if self.life > 0.4:
            alpha = 255
        elif self.life > 0:
            alpha = int(255 * (self.life / 0.4))
        else:
            alpha = 0
        self._surf.set_alpha(alpha)
        surf.blit(self._surf, self._surf.get_rect(
            center=(int(self.x), int(self.y))))


class FloatText:
    __slots__ = ("text", "x", "y", "vy", "life", "life_max", "color",
                 "size", "style", "_sparkles", "_baked")

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
        self._baked = None       # lazily-built static composite (powerup style)
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
        identity color. The composite is static once built (text / color / size
        / sparkle offsets are all fixed at construction), so it is baked ONCE and
        reused — only the fade alpha and position change per frame. This matters
        during a Coin Rush, where many "+N" labels are alive at once."""
        if self._baked is None:
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
            self._baked = comp

        alpha = int(255 * min(1.0, max(0.0, self.life / self.life_max) * 2))
        self._baked.set_alpha(alpha)
        rect = self._baked.get_rect(center=(int(self.x), int(self.y)))
        surf.blit(self._baked, rect.topleft)


class TreasureBanner:
    """Cycle-finale celebration ribbon — "DAY N COMPLETE!" overlay.

    A polished gold ribbon with notched forked ends sitting in front of
    a three-burst firework backdrop (dominant centre gold burst + two
    demoted warm side bursts). Drops in from above the chest with a
    micro-bounce + hold + fade-up envelope. Spawned from
    World._activate_treasure_box.

    Lifetime 1.4 s; composite baked once at construction and reused
    with per-frame alpha + position so a fresh banner per cycle-finale
    costs one draw call per frame, not a re-render."""

    LIFE_MAX     = 3.50
    DROP_IN_END  = 0.10       # cubic ease-out drop-in
    BOUNCE_END   = 0.18       # tiny overshoot then settle
    HOLD_END     = 3.05       # static hold (subtle sway) — extended from
                              # 0.92 s to 2.87 s so the cycle-finale beat
                              # reads as a once-per-day celebration.
    FADE_END     = 3.50       # alpha to zero + float up

    BANNER_W = 340
    BANNER_H = 78
    NOTCH    = 20             # depth of the chevron cut at each end
    OUTLINE  = 3
    SHADOW_DX = 4
    SHADOW_DY = 5
    # Composite is wider + taller than the ribbon so the firework bursts
    # can extend ~70 px past each end and a tall centre burst can sit
    # behind the ribbon. Ribbon stays centred inside the composite.
    COMP_PAD_X = 90
    COMP_PAD_Y = 70

    # 4-stop gold gradient — round 2 quality jump. Highlight cream
    # holds 0-15%, hot gold 15-55%, sat gold 55-92%, deep amber 92-100%.
    GOLD_STOPS = (
        (0.00, (255, 244, 188)),   # highlight cream
        (0.15, (255, 220, 110)),   # hot gold
        (0.55, (240, 188,  56)),   # saturated gold
        (0.92, (196, 132,  28)),   # deep amber
        (1.00, (180, 116,  24)),
    )
    GOLD_INK   = ( 72,  48,  12)
    VELVET     = (168,  32,  16)
    VELVET_HI  = (220,  64,  32)   # scarlet rim highlight (1 px on top of velvet)
    STAR_CREAM = (252, 244, 218)
    # Firework palette — round 3 polish: cyan dropped, hot orange in.
    BURST_GOLD   = (255, 220, 110)
    BURST_RED    = (248,  96,  88)
    BURST_ORANGE = (255, 128,  48)
    BURST_GLOW   = (255, 200,  96)
    BEVEL_HI_A   = 78              # ~70% of 255 per critic on the highlight band
    BEVEL_LO_A   = 110

    def __init__(self, day_num: int, x: float, y_chest: float):
        # Banner settles near the TOP of the screen (well above the
        # pillars + chest) so it never overlaps gameplay geometry and
        # reads as a global "achievement notification" instead of a
        # chest-specific overlay. The chest x is ignored — the banner
        # is screen-centered horizontally; the chest x is kept in the
        # signature so callers don't need to change.
        from game.config import W as _SCREEN_W
        del x, y_chest
        self.cx = float(_SCREEN_W) * 0.5
        self.cy_settled = 90.0
        self.day = max(1, int(day_num))
        # Time-since-spawn (counts UP) so the multi-phase envelope is
        # easier to express than a draining life timer.
        self.t = 0.0
        self._baked: "pygame.Surface | None" = None

    def alive(self) -> bool:
        return self.t < TreasureBanner.FADE_END

    def update(self, dt: float):
        self.t += dt

    def _envelope(self) -> tuple[float, int]:
        """Compute (y, alpha) for the current self.t."""
        t = self.t
        y_settle = self.cy_settled
        y_drop_start = y_settle - 60.0
        y_overshoot  = y_settle - 6.0
        y_fade_out   = y_settle - 14.0

        if t < TreasureBanner.DROP_IN_END:
            f = t / TreasureBanner.DROP_IN_END
            ease = 1.0 - (1.0 - f) ** 3
            y = y_drop_start + (y_settle - y_drop_start) * ease
            alpha = int(255 * ease)
        elif t < TreasureBanner.BOUNCE_END:
            f = ((t - TreasureBanner.DROP_IN_END)
                 / (TreasureBanner.BOUNCE_END - TreasureBanner.DROP_IN_END))
            y = y_settle + math.sin(f * math.pi) * (y_overshoot - y_settle)
            alpha = 255
        elif t < TreasureBanner.HOLD_END:
            y = y_settle
            alpha = 255
        elif t < TreasureBanner.FADE_END:
            f = ((t - TreasureBanner.HOLD_END)
                 / (TreasureBanner.FADE_END - TreasureBanner.HOLD_END))
            y = y_settle + (y_fade_out - y_settle) * f
            alpha = int(255 * (1.0 - f))
        else:
            y, alpha = y_fade_out, 0
        return y, max(0, min(255, alpha))

    def draw(self, surf: pygame.Surface):
        if self._baked is None:
            self._baked = self._build()
        y, alpha = self._envelope()
        if alpha <= 0:
            return
        sprite = self._baked
        sprite.set_alpha(alpha)
        # Tiny horizontal sway during HOLD keeps the banner alive.
        sway = 0
        if TreasureBanner.BOUNCE_END <= self.t < TreasureBanner.HOLD_END:
            sway_t = self.t - TreasureBanner.BOUNCE_END
            sway = int(round(math.sin(sway_t * math.tau * 1.5) * 1))
        r = sprite.get_rect(center=(int(self.cx + sway), int(y)))
        surf.blit(sprite, r.topleft)

    def _build(self) -> pygame.Surface:
        """Bake the static banner composite. Called once per instance.

        Renders at 2x supersample to a big surface, then smoothscales
        down — kills outline aliasing on the polygon edges and makes
        the embossed bevel + 1-px text drops crisp at final size."""
        from game.hud import _font

        cls = TreasureBanner
        bw, bh = cls.BANNER_W, cls.BANNER_H
        notch  = cls.NOTCH
        # Composite holds ribbon + firework bursts (extending past ribbon)
        # + drop shadow. Ribbon centred horizontally + vertically inside.
        comp_w = bw + cls.COMP_PAD_X * 2
        comp_h = bh + cls.COMP_PAD_Y * 2
        ss = 2  # supersample factor
        big = pygame.Surface((comp_w * ss, comp_h * ss), pygame.SRCALPHA)

        rx = cls.COMP_PAD_X * ss
        ry = cls.COMP_PAD_Y * ss
        bw_s, bh_s = bw * ss, bh * ss
        notch_s = notch * ss

        ribbon_pts = [
            (rx,                   ry),
            (rx + bw_s,            ry),
            (rx + bw_s - notch_s,  ry + bh_s // 2),
            (rx + bw_s,            ry + bh_s),
            (rx,                   ry + bh_s),
            (rx + notch_s,         ry + bh_s // 2),
        ]
        ribbon_cx = rx + bw_s // 2
        ribbon_cy = ry + bh_s // 2

        # ── Firework backdrop ───────────────────────────────────────────
        # Three procedural starburst explosions live on their own
        # surface so they can be clipped against the inflated ribbon
        # silhouette (no ray crossing the chevron notch — per round-3
        # critic). Centre gold burst dominant (1.6x), outer red + orange
        # bursts at 40% opacity, demoted to background sparks.
        burst_surf = pygame.Surface((comp_w * ss, comp_h * ss), pygame.SRCALPHA)
        self._draw_burst(burst_surf,
                         ribbon_cx, ribbon_cy,
                         radius=int(115 * ss),
                         color=cls.BURST_GOLD,
                         glow=cls.BURST_GLOW,
                         alpha=255,
                         spokes=18, sparkles=22, ss=ss)
        self._draw_burst(burst_surf,
                         ribbon_cx - int(140 * ss), ribbon_cy - int(10 * ss),
                         radius=int(72 * ss),
                         color=cls.BURST_RED,
                         glow=cls.BURST_RED,
                         alpha=102,
                         spokes=14, sparkles=12, ss=ss)
        self._draw_burst(burst_surf,
                         ribbon_cx + int(140 * ss), ribbon_cy - int(10 * ss),
                         radius=int(72 * ss),
                         color=cls.BURST_ORANGE,
                         glow=cls.BURST_ORANGE,
                         alpha=102,
                         spokes=14, sparkles=12, ss=ss)
        # Clip the burst's alpha to OUTSIDE the inflated ribbon silhouette
        # so no spoke crosses the chevron notch. Inflate by 2 ss-px so the
        # outline isn't bisected at sub-pixel edges.
        clip = pygame.Surface((comp_w * ss, comp_h * ss), pygame.SRCALPHA)
        clip.fill((255, 255, 255, 255))
        inflate = 2 * ss
        infl_pts = [
            (rx - inflate,                   ry - inflate),
            (rx + bw_s + inflate,            ry - inflate),
            (rx + bw_s - notch_s + inflate,  ry + bh_s // 2),
            (rx + bw_s + inflate,            ry + bh_s + inflate),
            (rx - inflate,                   ry + bh_s + inflate),
            (rx + notch_s - inflate,         ry + bh_s // 2),
        ]
        pygame.draw.polygon(clip, (0, 0, 0, 0), infl_pts)
        burst_surf.blit(clip, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        big.blit(burst_surf, (0, 0))

        # ── Drop shadow ─────────────────────────────────────────────────
        shadow_dx_s = cls.SHADOW_DX * ss
        shadow_dy_s = cls.SHADOW_DY * ss
        shadow_pts = [(x + shadow_dx_s, y + shadow_dy_s) for (x, y) in ribbon_pts]
        pygame.draw.polygon(big, (0, 0, 0, 170), shadow_pts)

        # ── Ribbon body — 4-stop gold gradient ──────────────────────────
        body = pygame.Surface((bw_s, bh_s), pygame.SRCALPHA)
        for yy in range(bh_s):
            t_grad = yy / max(1, bh_s - 1)
            cc = _interp_stops(cls.GOLD_STOPS, t_grad)
            pygame.draw.line(body, cc, (0, yy), (bw_s, yy))
        local_ribbon = [(x - rx, y - ry) for (x, y) in ribbon_pts]
        mask = pygame.Surface((bw_s, bh_s), pygame.SRCALPHA)
        pygame.draw.polygon(mask, (255, 255, 255, 255), local_ribbon)
        body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        big.blit(body, (rx, ry))

        # ── Embossed bevel ──────────────────────────────────────────────
        # White-alpha 2-px highlight inside the top edge + dark-alpha 2-px
        # shadow inside the bottom edge of the ribbon outline. Reads as
        # polished metal vs. flat paint.
        bevel = pygame.Surface((bw_s, bh_s), pygame.SRCALPHA)
        bw_inset = 2 * ss
        # Top highlight — strip across the top inside the outline, then
        # mask to ribbon silhouette so the notch shape inherits.
        pygame.draw.polygon(
            bevel, (255, 255, 255, cls.BEVEL_HI_A),
            [(0, 0), (bw_s, 0),
             (bw_s, bw_inset), (0, bw_inset)])
        # Bottom shadow — same logic on the underside.
        pygame.draw.polygon(
            bevel, (32, 18, 4, cls.BEVEL_LO_A),
            [(0, bh_s - bw_inset), (bw_s, bh_s - bw_inset),
             (bw_s, bh_s), (0, bh_s)])
        bevel.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        big.blit(bevel, (rx, ry))

        # ── Red velvet bottom rim + scarlet highlight ───────────────────
        rim_h = 8 * ss
        rim = pygame.Surface((bw_s, bh_s), pygame.SRCALPHA)
        pygame.draw.rect(rim, cls.VELVET, (0, bh_s - rim_h, bw_s, rim_h))
        pygame.draw.rect(rim, cls.VELVET_HI, (0, bh_s - rim_h, bw_s, 1 * ss))
        rim.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        big.blit(rim, (rx, ry))

        # ── Dark outline tracing the ribbon polygon ─────────────────────
        pygame.draw.polygon(big, cls.GOLD_INK, ribbon_pts, cls.OUTLINE * ss)

        # ── Text — "DAY N COMPLETE!" with embossed drops ────────────────
        text_str = (f"DAY {self.day} COMPLETE!"
                    if 1 <= self.day <= 99 else "DAY COMPLETE!")
        # Auto-pick a font size that fits the banner width with margin.
        # ss factor folded in so the source render is supersampled too.
        font_size = 34 * ss
        font = _font(font_size, bold=True)
        margin = (notch + 22) * ss
        while font.size(text_str)[0] > bw_s - margin * 2 and font_size > 22 * ss:
            font_size -= 2 * ss
            font = _font(font_size, bold=True)
        text_cream = font.render(text_str, True, cls.STAR_CREAM)
        text_ink   = font.render(text_str, True, cls.GOLD_INK)
        text_hi    = font.render(text_str, True, (255, 255, 255))
        tw, th = text_cream.get_size()
        tx = rx + (bw_s - tw) // 2
        ty = ry + (bh_s - th) // 2 - 3 * ss   # nudge up off the velvet rim
        # 1-px outline ring (was 2 px in round 1 — critic said too heavy).
        d = 1 * ss
        for ox, oy in ((-d, 0), (d, 0), (0, -d), (0, d),
                       (-d, -d), (d, -d), (-d, d), (d, d)):
            big.blit(text_ink, (tx + ox, ty + oy))
        # Embossed text: 1-px white drop on TOP edge + 1-px dark drop on
        # BOTTOM edge BEFORE the cream fill. Letters read as etched.
        hi_surf = text_hi.copy(); hi_surf.set_alpha(140)
        lo_surf = text_ink.copy(); lo_surf.set_alpha(180)
        big.blit(hi_surf, (tx, ty - d))
        big.blit(lo_surf, (tx, ty + d))
        big.blit(text_cream, (tx, ty))

        # Smoothscale the 2x supersample down to final size — kills outline
        # aliasing and crisps the embossed details.
        return pygame.transform.smoothscale(big, (comp_w, comp_h))

    @staticmethod
    def _draw_burst(surf: pygame.Surface,
                    cx: int, cy: int, radius: int,
                    color: tuple, glow: tuple,
                    alpha: int, spokes: int, sparkles: int, ss: int):
        """One procedural starburst — soft additive glow disc + tapered
        spokes + scattered sparkle dots. Same vocabulary as the
        treasure-box halo so the FX family reads as one visual language.

        alpha controls overall opacity (centre burst at 255, outer
        bursts at ~100 per round-3 critic's "demoted to background
        sparks" note)."""
        # Glow disc — cubic falloff so it stays warm haze on the
        # twilight bg, not a bleached spotlight (round-2 fix).
        glow_r = int(radius * 1.05)
        for i in range(glow_r, 0, -2):
            t = i / glow_r
            a = int(alpha * 0.35 * (1.0 - t) ** 3)
            if a > 0:
                pygame.draw.circle(surf, (*glow, a), (cx, cy), i)
        # Spokes — tapered triangles, alternating lengths ±15% so the
        # silhouette breathes (per round-3 critic on the round-1 V1).
        for i in range(spokes):
            ang = (i / spokes) * math.tau
            length_mul = 1.15 if (i % 2 == 0) else 0.85
            length = int(radius * length_mul)
            tip_x = cx + math.cos(ang) * length
            tip_y = cy + math.sin(ang) * length
            base_w = max(3 * ss, int(radius * 0.07))
            perp_x = -math.sin(ang) * base_w
            perp_y =  math.cos(ang) * base_w
            spoke_pts = [
                (cx + perp_x, cy + perp_y),
                (cx - perp_x, cy - perp_y),
                (tip_x,       tip_y),
            ]
            pygame.draw.polygon(surf, (*color, alpha), spoke_pts)
        # Sparkle dots — small pearls scattered along the rays at random
        # radii so the burst has fine grit, not just clean polygons.
        rng = random.Random(cx * 1000 + cy + radius)  # stable per burst
        for _ in range(sparkles):
            ang = rng.uniform(0, math.tau)
            rr = rng.uniform(radius * 0.55, radius * 1.10)
            px = int(cx + math.cos(ang) * rr)
            py = int(cy + math.sin(ang) * rr)
            r = rng.choice((1, 1, 2, 2, 3)) * ss
            pygame.draw.circle(surf, (255, 240, 200, alpha), (px, py), r)


def _interp_stops(stops, t: float) -> tuple:
    """Multi-stop colour gradient interpolation. stops is a tuple of
    (position 0..1, (r, g, b)) pairs in ascending position order."""
    t = max(0.0, min(1.0, t))
    for i in range(len(stops) - 1):
        p0, c0 = stops[i]
        p1, c1 = stops[i + 1]
        if t <= p1:
            span = max(1e-6, p1 - p0)
            f = (t - p0) / span
            return (int(c0[0] + (c1[0] - c0[0]) * f),
                    int(c0[1] + (c1[1] - c0[1]) * f),
                    int(c0[2] + (c1[2] - c0[2]) * f))
    return stops[-1][1]


class CelebrationGarland:
    """World-space festoon strung between two pillars flanking the
    cycle-finale treasure chest. Catenary curve + 8 warm Edison-style
    bulbs with hot-yellow filament cores + soft additive halos.

    Tracks pillar references live so the curve follows them as they
    scroll left. Same 1.4 s lifetime envelope as the banner so they
    fade together. Spawned from World._activate_treasure_box."""

    LIFE_MAX     = 3.50
    DROP_IN_END  = 0.10
    HOLD_END     = 3.05
    FADE_END     = 3.50

    N_BULBS      = 8
    DROOP        = 32          # catenary sag — kept shallow so bulbs
                               # stay in the airspace above the busy
                               # coin-storm zone around the chest.
    THREAD_COL   = ( 48,  32,  12)
    BULB_BODY    = (255, 240, 200)
    BULB_GLOW    = (255, 220, 110)
    BULB_FILAMENT = (255, 236, 128)
    BULB_INK     = ( 64,  48,  16)

    def __init__(self, left_pipe, right_pipe):
        # Pillars are world-space — they scroll left every frame.
        # Storing the refs (vs. snapshotting positions) is what makes
        # the garland TRACK them, not stick to a stale snapshot.
        self.left = left_pipe
        self.right = right_pipe
        self.t = 0.0

    def alive(self) -> bool:
        if self.left is None or self.right is None:
            return False
        return self.t < CelebrationGarland.FADE_END

    def update(self, dt: float):
        self.t += dt

    def _alpha(self) -> int:
        cls = CelebrationGarland
        t = self.t
        if t < cls.DROP_IN_END:
            return int(255 * (t / cls.DROP_IN_END))
        if t < cls.HOLD_END:
            return 255
        if t < cls.FADE_END:
            f = (t - cls.HOLD_END) / (cls.FADE_END - cls.HOLD_END)
            return int(255 * (1.0 - f))
        return 0

    def _anchors(self) -> tuple:
        """Return the two anchor points in world-space — bottom centre
        of each flanking pillar's UPPER pipe segment. Recomputed every
        frame so pillar scroll is tracked."""
        from game.config import PIPE_W
        ax = self.left.x + PIPE_W * 0.5
        ay = self.left.gap_y - self.left.gap_h * 0.5
        bx = self.right.x + PIPE_W * 0.5
        by = self.right.gap_y - self.right.gap_h * 0.5
        return ax, ay, bx, by

    def draw(self, surf: pygame.Surface, sx: int = 0, sy: int = 0):
        alpha = self._alpha()
        if alpha <= 0 or self.left is None or self.right is None:
            return
        ax, ay, bx, by = self._anchors()
        if bx <= ax:
            return  # pillars crossed (shouldn't happen but defensive)
        cls = CelebrationGarland
        droop = cls.DROOP
        samples = 24
        pts = []
        for i in range(samples + 1):
            t = i / samples
            base_y = ay * (1 - t) + by * t
            sag = droop * 4 * t * (1 - t)
            x = ax * (1 - t) + bx * t
            y = base_y + sag
            pts.append((int(x + sx), int(y + sy)))

        # Halo layer — additive blend so the warm glow punches through
        # the busy coin-storm zone instead of being lost in alpha mush.
        halo = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        bulb_positions = []
        for k in range(cls.N_BULBS):
            t = (k + 1) / (cls.N_BULBS + 1)
            base_y = ay * (1 - t) + by * t
            sag = droop * 4 * t * (1 - t)
            bx_p = int(ax * (1 - t) + bx * t + sx)
            by_p = int(base_y + sag + sy)
            bulb_positions.append((bx_p, by_p))
            # Bigger, brighter additive halo — three layers of warm gold
            # so the festoon reads as actual lit bulbs at gameplay scale.
            a_mul = alpha / 255
            for r, a in ((22, int(36 * a_mul)),
                         (16, int(72 * a_mul)),
                         (11, int(140 * a_mul)),
                         ( 7, int(220 * a_mul))):
                if a > 0:
                    pygame.draw.circle(halo, (*cls.BULB_GLOW, a),
                                       (bx_p, by_p), r)
        surf.blit(halo, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

        # Solid layer — thread + bulb bodies. Plain alpha so the bulbs
        # have crisp outlines instead of being additive-washed out.
        solid = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        if len(pts) >= 2:
            pygame.draw.lines(solid, cls.THREAD_COL, False, pts, 3)
        for bx_p, by_p in bulb_positions:
            pygame.draw.circle(solid, cls.BULB_BODY, (bx_p, by_p), 6)
            pygame.draw.circle(solid, cls.BULB_INK,  (bx_p, by_p), 6, 1)
            pygame.draw.circle(solid, cls.BULB_FILAMENT, (bx_p, by_p), 2)
        solid.set_alpha(alpha)
        surf.blit(solid, (0, 0))


class CelebrationBunting:
    """World-space triangular-pennant string tied between the upper-pipe
    tips of the two real pillars flanking the cycle-finale phantom band.
    Sits above the festoon garland so the celebration zone reads as TWO
    layers of party decor.

    Endpoints are stored as raw world-coords (not pillar refs) and
    scroll in lockstep with the world — same scroll rate as the
    pillars, so the rope stays visually tied to the pillar tops
    without holding a stale ref past cull. Each endpoint carries its
    own y so a left/right pillar gap-height mismatch doesn't break the
    rope geometry.
    """

    N_PENNANTS = 14
    PENNANT_W = 16
    PENNANT_H = 22
    DROOP     = 18
    LIFT_Y    = 30            # px above the snapshot gap-top
    THREAD    = ( 40,  28,  10)
    INK       = ( 30,  20,   8)
    COLOURS = (
        (255, 220, 110),
        (220,  64,  32),
        ( 96, 176, 232),
        (252, 244, 218),
    )

    def __init__(self, x_left: float, y_left: float,
                 x_right: float, y_right: float):
        self.x_left = float(x_left)
        self.x_right = float(x_right)
        self.y_left = float(y_left)
        self.y_right = float(y_right)

    def alive(self) -> bool:
        return self.x_right > -50

    def update(self, dt: float, scroll_dx: float = 0.0):
        self.x_left -= scroll_dx
        self.x_right -= scroll_dx

    def draw(self, surf: pygame.Surface, sx: int = 0, sy: int = 0):
        cls = CelebrationBunting
        if self.x_right <= self.x_left:
            return
        samples = 24
        pts = []
        for i in range(samples + 1):
            t = i / samples
            sag = cls.DROOP * 4 * t * (1 - t)
            x = self.x_left * (1 - t) + self.x_right * t
            y = self.y_left * (1 - t) + self.y_right * t
            pts.append((int(x + sx), int(y - cls.LIFT_Y + sag + sy)))
        if len(pts) >= 2:
            pygame.draw.lines(surf, cls.THREAD, False, pts, 2)
        for k in range(cls.N_PENNANTS):
            t = (k + 1) / (cls.N_PENNANTS + 1)
            sag = cls.DROOP * 4 * t * (1 - t)
            cx = int(self.x_left * (1 - t) + self.x_right * t + sx)
            cy_anchor = self.y_left * (1 - t) + self.y_right * t
            cy_top = int(cy_anchor - cls.LIFT_Y + sag + sy)
            col = cls.COLOURS[k % len(cls.COLOURS)]
            pts_tri = [
                (cx - cls.PENNANT_W // 2, cy_top),
                (cx + cls.PENNANT_W // 2, cy_top),
                (cx,                       cy_top + cls.PENNANT_H),
            ]
            pygame.draw.polygon(surf, col, pts_tri)
            pygame.draw.polygon(surf, cls.INK, pts_tri, 1)


class CelebrationBalloonCluster:
    """4 festive paneled balloons spaced across the cycle-finale phantom
    gap. Bobs sinusoidally, drifts up slowly. Reuses the paneled balloon
    sprite cache from game.ambient (`_build_balloon_surface`) so the
    party balloons share the visual language of the ambient ones.

    Uses RAW world-x coords like CelebrationBunting so it can spawn at
    chest DROP and survive past chest pickup."""

    SLOTS = (0.15, 0.35, 0.65, 0.85)
    Y_BASE = 220.0
    BOB_AMP = 8.0
    BOB_HZ  = 0.8
    DRIFT_VY = -8.0
    PALETTE_IDX = (1, 0, 2, 3)

    def __init__(self, x_left: float, x_right: float):
        self.x_left = float(x_left)
        self.x_right = float(x_right)
        from game.ambient import _build_balloon_surface
        self._sprites = []
        for i in range(4):
            surf_, env_cx, env_cy = _build_balloon_surface(1, self.PALETTE_IDX[i])
            self._sprites.append((surf_, env_cx, env_cy))
        self._phase = [i * (math.tau / 4) for i in range(4)]
        self._dy = [0.0, 0.0, 0.0, 0.0]
        self.t = 0.0

    def alive(self) -> bool:
        return self.x_right > -80

    def update(self, dt: float, scroll_dx: float = 0.0):
        self.t += dt
        self.x_left -= scroll_dx
        self.x_right -= scroll_dx
        for i in range(4):
            self._dy[i] += CelebrationBalloonCluster.DRIFT_VY * dt

    def draw(self, surf: pygame.Surface, sx: int = 0, sy: int = 0):
        cls = CelebrationBalloonCluster
        for i, slot_t in enumerate(cls.SLOTS):
            bob = math.sin(self.t * cls.BOB_HZ * math.tau
                           + self._phase[i]) * cls.BOB_AMP
            cx = self.x_left * (1 - slot_t) + self.x_right * slot_t
            cy = cls.Y_BASE + self._dy[i] + bob
            sprite, env_cx, env_cy = self._sprites[i]
            surf.blit(sprite,
                      (int(cx - env_cx + sx), int(cy - env_cy + sy)))


class CelebrationGroundMarker:
    """Vertical white "finish-line" stripe + "{N} Day" white label,
    confined to the GROUND BAND (grass + soil stripes). Marks the
    world-x where the biome cycle finished — directly beneath the
    chest. Reads like a track-race lane marker so the player feels
    they've crossed a milestone.

    Anchored in world space — scrolls left with the rest of the gap
    decor and self-culls when off-screen. Cached composite, per-frame
    cost is a single blit."""

    LINE_W = 4              # vertical stripe width
    LINE_COLOR = (252, 252, 252)
    TEXT_COLOR = (252, 252, 252)
    TEXT_INK   = ( 30,  20,   8)   # very thin shadow for grass legibility
    TEXT_SIZE  = 16
    TEXT_GAP_X = 6          # px between line and text
    # Pad below GROUND_Y so the stripe + label hug the top of the grass
    # band cleanly (the variant draw renders grass blades + flowers
    # there).
    TOP_PAD    = 2
    BOTTOM_PAD = 2

    def __init__(self, world_x: float, day: int):
        self.x = float(world_x)
        self.day = max(1, int(day))
        self._sprite = self._build()

    def alive(self) -> bool:
        return self.x > -200

    def update(self, dt: float, scroll_dx: float = 0.0):
        self.x -= scroll_dx

    def _build(self) -> pygame.Surface:
        from game.hud import _font
        cls = CelebrationGroundMarker
        band_h = (H - GROUND_Y) - cls.TOP_PAD - cls.BOTTOM_PAD
        # Render text once to size the composite.
        text = f"{self.day} Day"
        font = _font(cls.TEXT_SIZE, True)
        face = font.render(text, True, cls.TEXT_COLOR)
        ink  = font.render(text, True, cls.TEXT_INK)
        tw, th = face.get_size()
        comp_w = cls.LINE_W + cls.TEXT_GAP_X + tw + 2
        comp_h = max(band_h, th + 4)
        big = pygame.Surface((comp_w, comp_h), pygame.SRCALPHA)
        # Vertical white stripe — full ground-band height.
        pygame.draw.rect(big, cls.LINE_COLOR,
                         (0, 0, cls.LINE_W, band_h))
        # Subtle 1-px grey shadow on the right edge of the stripe so it
        # reads as a painted-on lane line, not a floating slab.
        pygame.draw.line(big, (200, 200, 200, 200),
                         (cls.LINE_W, 0),
                         (cls.LINE_W, band_h - 1), 1)
        # Text "{N} Day" — white with a 1-px dark drop shadow so it
        # stays legible against the green grass + dark blades.
        text_x = cls.LINE_W + cls.TEXT_GAP_X
        text_y = (band_h - th) // 2
        # 1-px ink shadow on 4 cardinal offsets.
        for ox, oy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            big.blit(ink, (text_x + ox, text_y + oy))
        big.blit(face, (text_x, text_y))
        return big

    def draw(self, surf: pygame.Surface, sx: int = 0, sy: int = 0):
        # Anchor: top of the white stripe sits TOP_PAD below GROUND_Y so
        # the marker lives entirely inside the ground band (grass +
        # soil), centred horizontally on the chest's world-x for the
        # stripe edge.
        cls = CelebrationGroundMarker
        spr = self._sprite
        target_top = GROUND_Y + cls.TOP_PAD
        # Centre the stripe on self.x (stripe is LINE_W wide).
        target_left = int(self.x - cls.LINE_W * 0.5)
        surf.blit(spr, (target_left + sx, int(target_top + sy)))


class CelebrationCrowd:
    """Multi-cluster cheering crowd spanning the cycle-finale phantom
    band. Each of N clusters is a copy of the 7-parrot CROWD_LAYOUT
    (`game.cheering_crowd`), with per-cluster plumage / instrument
    reshuffle so no two clusters look identical.

    Cluster x's are drawn from a triangular distribution peaking at
    ``finish_x``, so the crowd is densest right at the finish-line
    stripe and thins toward the flanking real pillars. One cluster is
    always pinned exactly on the finish line.
    """

    # Per-cluster CROWD_LAYOUT dx range is -130..+140 plus ~20 px; the
    # rightmost cluster's stripe is at x_right (the right-flanking
    # pillar's centre) so cull when even its leftmost parrot has fully
    # scrolled past x=0.
    HALF_SPAN = 160
    N_CLUSTERS = 5

    def __init__(self, x_left: float, x_right: float, finish_x: float):
        cls = CelebrationCrowd
        self.t = 0.0
        # Keep the ENTIRE crowd off-screen at spawn so it scrolls in from
        # the right edge like real scenery, never popping onto the playfield.
        # A cluster's outermost parrots reach ±HALF_SPAN, so clamp the left
        # sampling bound to one HALF_SPAN past the right screen edge — even
        # the leftmost cluster then starts at x = W. finish_x is always well
        # to the right of this, so the triangular mode stays valid.
        x_left = max(x_left, W + cls.HALF_SPAN)
        # Triangular puts the mode at finish_x, so ~half the samples
        # fall within ±(x_right - x_left)/4 of the line — a natural
        # density peak at the finish stripe.
        xs = [random.triangular(x_left, x_right, finish_x)
              for _ in range(cls.N_CLUSTERS - 1)]
        xs.append(finish_x)
        # Per-cluster seed → reshuffled plumages / instrument tints
        # inside draw_crowd so the copies feel like a real crowd
        # rather than a stamped repeat.
        self.cluster_xs = [float(x) for x in xs]
        self.cluster_seeds = [random.randint(1, 1 << 20)
                              for _ in self.cluster_xs]

    def alive(self) -> bool:
        return max(self.cluster_xs) > -CelebrationCrowd.HALF_SPAN

    def update(self, dt: float, scroll_dx: float = 0.0):
        self.t += dt
        if scroll_dx:
            self.cluster_xs = [x - scroll_dx for x in self.cluster_xs]

    def draw(self, surf: pygame.Surface, sx: int = 0, sy: int = 0):
        from game.cheering_crowd import draw_crowd
        for cx, seed in zip(self.cluster_xs, self.cluster_seeds):
            draw_crowd(surf, int(cx + sx), int(GROUND_Y + sy),
                       self.t, seed=seed)


class CelebrationFireworkBurst:
    """One animated firework explosion — expands + sparkles + fades.
    Spawned in clumps from World._activate_treasure_box, staggered
    across the banner's 1.4 s lifetime so multiple bursts pop one
    after another instead of all at once. Drawn additively so the
    flash punches against the twilight sky.

    Each burst owns its own particle list (16 ray particles + central
    flash). The expansion follows a soft cubic ease so the burst flares
    fast then drifts."""

    LIFE_MAX = 2.5
    EASE_END = 0.22          # expansion completes at this fraction of life
                             # (was 0.55 of a 1.0 s burst -> 0.55 s; keep
                             # the absolute expansion at ~0.55 s on the
                             # longer 2.5 s lifetime so the burst still
                             # flares quickly before holding its peak)
    RADIUS_MAX = 95
    N_RAYS = 16
    PALETTE = (
        (255, 220, 110),     # gold
        (248,  96,  88),     # red
        (255, 128,  48),     # hot orange
        (252, 244, 218),     # cream
    )

    def __init__(self, x: float, y: float, ignite_delay: float,
                 color: tuple, radius_mul: float = 1.0):
        self.x = float(x)
        self.y = float(y)
        self.t = -float(ignite_delay)        # negative = pre-ignite
        self.colour = color
        self.radius_max = CelebrationFireworkBurst.RADIUS_MAX * radius_mul
        # Pre-compute the ray endpoints so jitter is stable per burst.
        rng = random.Random(int(x * 1000 + y) ^ int(ignite_delay * 1000))
        self.rays = []
        for i in range(CelebrationFireworkBurst.N_RAYS):
            ang = (i / CelebrationFireworkBurst.N_RAYS) * math.tau
            length_mul = rng.uniform(0.78, 1.18)
            self.rays.append((math.cos(ang), math.sin(ang), length_mul))
        # Sparkle dots — small bright pearls scattered across the ray field.
        self.sparkles = []
        for _ in range(14):
            ang = rng.uniform(0, math.tau)
            rr = rng.uniform(0.45, 1.05)
            self.sparkles.append((math.cos(ang), math.sin(ang), rr))

    def alive(self) -> bool:
        return self.t < CelebrationFireworkBurst.LIFE_MAX

    def update(self, dt: float):
        self.t += dt

    def draw(self, surf: pygame.Surface):
        cls = CelebrationFireworkBurst
        if self.t < 0 or self.t >= cls.LIFE_MAX:
            return
        u = self.t / cls.LIFE_MAX
        # Expansion ease — radius hits RADIUS_MAX at EASE_END then holds.
        if u < cls.EASE_END:
            f = u / cls.EASE_END
            radius = self.radius_max * (1.0 - (1.0 - f) ** 3)
        else:
            radius = self.radius_max
        # Alpha — bright snap on ignite, fades cubic.
        alpha_mul = (1.0 - u) ** 1.4
        layer_size = int(radius * 2 + 24)
        layer = pygame.Surface((layer_size, layer_size), pygame.SRCALPHA)
        lcx = layer_size // 2
        lcy = layer_size // 2
        col = self.colour
        # Rays — bright tip, fading toward centre. Three samples per ray
        # so a single explosion reads as a streak, not a single dot.
        for cx_dir, cy_dir, length_mul in self.rays:
            tip_x = cx_dir * radius * length_mul
            tip_y = cy_dir * radius * length_mul
            for step, base_a in ((1.00, 220), (0.75, 180), (0.50, 130),
                                 (0.30,  90)):
                px = int(lcx + tip_x * step)
                py = int(lcy + tip_y * step)
                a = int(base_a * alpha_mul)
                if a > 4:
                    pygame.draw.circle(layer, (*col, a), (px, py), 2)
        # Sparkle pearls — scattered bright cream dots add fine grit.
        for cx_dir, cy_dir, rr in self.sparkles:
            px = int(lcx + cx_dir * radius * rr)
            py = int(lcy + cy_dir * radius * rr)
            a = int(220 * alpha_mul)
            if a > 4:
                pygame.draw.circle(layer, (255, 244, 200, a), (px, py), 1)
        # Centre flash — bright cream core with coloured halo. Peaks
        # early, fades fast so the eye registers the ignite moment.
        flash_mul = max(0.0, 1.0 - u * 1.8)
        if flash_mul > 0:
            core_a = int(255 * flash_mul)
            halo_a = int(120 * flash_mul)
            pygame.draw.circle(layer, (255, 250, 220, core_a),
                               (lcx, lcy), 4)
            pygame.draw.circle(layer, (*col, halo_a),
                               (lcx, lcy), 8)
        rect = layer.get_rect(center=(int(self.x), int(self.y)))
        surf.blit(layer, rect.topleft, special_flags=pygame.BLEND_RGB_ADD)


class CelebrationConfetti:
    """World-space confetti flake — small rotating rectangle with
    light gravity + horizontal drift. Spawned in clumps from
    World._activate_treasure_box. Rides the world scroll via vx so
    it tracks the chest position as the player flies forward."""

    SIZE    = (3, 5)
    COLOURS = (
        (255, 220, 110),   # gold
        (220,  64,  32),   # scarlet
        (255, 128,  48),   # orange
        (252, 244, 218),   # cream
    )

    def __init__(self, x: float, y: float, vx: float, vy: float,
                 colour: tuple, life: float, spin: float):
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.angle = random.uniform(0, math.tau)
        self.spin = spin
        self.colour = colour
        self.life = float(life)
        self.life_max = float(life)
        self._tile: "pygame.Surface | None" = None

    def alive(self) -> bool:
        return self.life > 0

    def update(self, dt: float):
        self.life -= dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 320 * dt    # light gravity — confetti falls
        self.vx *= 0.985       # horizontal drag
        self.angle += self.spin * dt

    def draw(self, surf: pygame.Surface):
        if self.life <= 0:
            return
        if self._tile is None:
            w, h = CelebrationConfetti.SIZE
            tile = pygame.Surface((w + 2, h + 2), pygame.SRCALPHA)
            pygame.draw.rect(tile, self.colour, (1, 1, w, h))
            self._tile = tile
        rot = pygame.transform.rotate(self._tile, math.degrees(self.angle))
        # Fade in the last 30% of life so flakes don't pop out.
        fade_frac = max(0.0, min(1.0, self.life / max(0.01, self.life_max * 0.3)))
        if fade_frac < 1.0:
            rot.set_alpha(int(255 * fade_frac))
        rect = rot.get_rect(center=(int(self.x), int(self.y)))
        surf.blit(rot, rect.topleft)


class FlyingCoinParticle:
    """Full-detail Coin medallion with particle physics. Used by the
    storm jolt so the coins flying off Pip read as the SAME currency
    he just lost — not the smaller doubloons the treasure box uses.
    Wraps an internal Coin so all the gradient / outline / parrot /
    sparkle work is unchanged; this class only adds motion, gravity,
    life, and alpha fade-out."""

    def __init__(self, x, y, vx, vy, *, life=0.95):
        self._coin = Coin(x, y)
        self._coin.spin = random.uniform(0, math.tau)
        self.vx = vx
        self.vy = vy
        self.life = life
        self.life_max = life

    def update(self, dt):
        # Slightly heavier than TreasureCoinParticle so the arc reads
        # like real coins, not a champagne pop.
        self.vy += 800.0 * dt
        self._coin.x += self.vx * dt
        self._coin.y += self.vy * dt
        # Spin faster than a stationary Coin (flung outward = tumbling).
        self._coin.spin = (self._coin.spin + dt * 9.0) % math.tau
        self._coin.float_t += dt
        self.life -= dt

    def alive(self):
        return self.life > 0

    def draw(self, surf):
        t = max(0.0, self.life / self.life_max)
        if t >= 0.5:
            # Full opacity during the bright half — draw straight to surf.
            self._coin.draw(surf)
            return
        # Fade phase: render to a transparent buffer, then alpha-blit.
        # Buffer is sized generously so the squeeze + sparkles fit.
        BUF = 48
        scratch = pygame.Surface((BUF, BUF), pygame.SRCALPHA)
        # Trick: temporarily override the coin's x/y to the buffer centre
        # so its own draw places it cleanly inside the scratch surface,
        # then restore.
        saved_x, saved_y = self._coin.x, self._coin.y
        self._coin.x, self._coin.y = BUF // 2, BUF // 2
        self._coin.draw(scratch)
        self._coin.x, self._coin.y = saved_x, saved_y
        scratch.set_alpha(int(255 * (t * 2)))
        surf.blit(scratch, (int(saved_x) - BUF // 2,
                            int(saved_y) - BUF // 2))
