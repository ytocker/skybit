"""KFC powerup pillar pool: 3 fast-food-themed pillar designs.

When the KFC powerup is active, every pillar on screen flips from the
normal stone-and-foliage variants to one of the designs below. The
variant is picked deterministically per pillar via `seed % 4` against
the KFC_DRAWERS tuple, in which the bucket is listed twice so the
distribution comes out 50% bucket / 25% hot dog / 25% corn dog. Pipe
seeds are stable for the lifetime of the Pipe instance, so a given
pillar keeps the same look as it scrolls across the screen.

  Hot Dog        side buns + sausage running through the gap +
                 mustard zigzag + ketchup dots                     (25%)
  Bucket Stack   stacked KFC bucket trapezoids (red+white striped)
                 with overflowing chicken pile + a tiny pennant
                 flag planted in the pile                          (50%)
  Corn Dog       golden batter rod with crispy bumps + honey-
                 mustard drips + plain wooden skewer at the gap    (25%)

The corn dog's top pillar renders with flat top corners (no top-radius)
so the rod visually connects to the ceiling instead of floating below
it. Bucket-stack top pillars use vertically flipped trapezoids so the
rim faces the gap and chicken pile hangs DOWN from it toward the gap,
not into the bucket.

A fourth design, `draw_pillar_kfc_sandwich`, is retained in this module
(multi-layer tower of bun/fillet/cheese/lettuce + toothpick skewer)
but is RETIRED from the active rotation - the layered silhouette was
too hard to read at gameplay scale. Re-add it to KFC_DRAWERS to bring
it back.
"""
import math
import random

import pygame


# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------

# Bun
BUN_HI    = (252, 226, 178)
BUN_MID   = (232, 192, 130)
BUN_LO    = (188, 142,  78)

# Sausage / frankfurter
SAUSAGE_HI  = (228, 124,  92)
SAUSAGE_MID = (198,  82,  62)
SAUSAGE_LO  = (146,  46,  36)

# Fried crust
CRUST_HI  = (250, 212, 118)
CRUST_MID = (224, 162,  62)
CRUST_LO  = (148,  84,  20)
CRUMB     = (255, 232, 168)
BONE      = (248, 240, 210)
BONE_SHA  = (190, 175, 140)

# Cheese
CHEESE_HI = (255, 220, 110)
CHEESE    = (252, 184,  60)
CHEESE_LO = (190, 132,  30)

# Lettuce
LETTUCE_HI  = (140, 200,  78)
LETTUCE_MID = ( 86, 158,  64)
LETTUCE_LO  = ( 52, 106,  40)

# KFC bucket
KFC_RED   = (212,  34,  34)
KFC_RED_D = (152,  18,  18)
KFC_WHITE = (250, 245, 235)

# Condiments
MUSTARD     = (252, 206,  56)
MUSTARD_HI  = (255, 234, 130)
KETCHUP     = (210,  44,  40)
KETCHUP_HI  = (244,  92,  72)
HONEY_MID   = (244, 178,  60)
HONEY_HI    = (255, 222, 130)

# Skewer
WOOD_HI = (230, 192, 132)
WOOD_LO = (162, 116,  62)

OUTLINE = ( 38,  22,  10)
SHADOW  = ( 22,  14,   8)


# ---------------------------------------------------------------------------
# Utility primitives
# ---------------------------------------------------------------------------

def _shade(c, d):
    return (max(0, min(255, c[0] + d)),
            max(0, min(255, c[1] + d)),
            max(0, min(255, c[2] + d)))


def _aa_filled_circle(surf, cx, cy, r, color):
    """Filled circle. Named `_aa_*` for historical reasons - the original
    implementation used pygame.gfxdraw for anti-aliasing, but that backend
    raises `pygame.error: Parameter 'renderer' is invalid` on the mobile
    SDL build. The rest of the game uses plain pygame.draw.circle, so we
    match that and accept the slightly-aliased look for KFC pillars."""
    cx, cy, r = int(cx), int(cy), int(r)
    if r < 1:
        return
    pygame.draw.circle(surf, color, (cx, cy), r)


# ---------------------------------------------------------------------------
# Shared food primitives
# ---------------------------------------------------------------------------

def draw_drumstick(surf, cx, cy, w, h, *, tilt=0, bone_top=True, seed=0):
    """Cartoon fried drumstick - pear-shape meat blob + bone nub."""
    layer = pygame.Surface((w + 14, h + 14), pygame.SRCALPHA)
    lh = layer.get_height()
    meat_rect = pygame.Rect(7, 9, w, int(h * 0.78))
    pygame.draw.ellipse(layer, OUTLINE, meat_rect.inflate(4, 4))
    pygame.draw.ellipse(layer, CRUST_LO, meat_rect.inflate(2, 2))
    pygame.draw.ellipse(layer, CRUST_MID, meat_rect)
    pygame.draw.ellipse(layer, CRUST_HI,
                        meat_rect.inflate(-int(w * 0.45), -int(h * 0.45))
                                 .move(-int(w * 0.10), -int(h * 0.06)))
    rng = random.Random(seed * 13 + 7)
    for _ in range(8):
        bx = rng.randint(meat_rect.left + 4, meat_rect.right - 4)
        by = rng.randint(meat_rect.top + 4, meat_rect.bottom - 4)
        _aa_filled_circle(layer, bx, by, 1, CRUMB)
    bone_w = max(5, int(w * 0.32))
    bone_h = max(8, int(h * 0.28))
    if bone_top:
        bx, by = 7 + (w - bone_w) // 2, 0
    else:
        bx, by = 7 + (w - bone_w) // 2, lh - bone_h - 4
    bone_rect = pygame.Rect(bx, by, bone_w, bone_h)
    pygame.draw.rect(layer, OUTLINE, bone_rect.inflate(4, 2), border_radius=4)
    pygame.draw.rect(layer, BONE_SHA, bone_rect.inflate(2, 0), border_radius=3)
    pygame.draw.rect(layer, BONE, bone_rect.inflate(-2, -1), border_radius=3)
    knob_y = bone_rect.top + 1 if bone_top else bone_rect.bottom - 1
    _aa_filled_circle(layer, bone_rect.centerx - bone_w // 4, knob_y,
                      max(2, bone_w // 3), BONE)
    _aa_filled_circle(layer, bone_rect.centerx + bone_w // 4, knob_y,
                      max(2, bone_w // 3), BONE)
    if tilt:
        layer = pygame.transform.rotate(layer, tilt)
    rect = layer.get_rect(center=(cx, cy))
    surf.blit(layer, rect.topleft)


def draw_chicken_wing(surf, cx, cy, w, h, *, flip=False):
    """Cartoon fried chicken wing - drumette + wingette + bone tip."""
    big = pygame.Rect(cx - w // 2, cy - h // 2, int(w * 0.65), int(h * 0.85))
    pygame.draw.ellipse(surf, OUTLINE, big.inflate(4, 4))
    pygame.draw.ellipse(surf, CRUST_LO, big.inflate(2, 2))
    pygame.draw.ellipse(surf, CRUST_MID, big)
    pygame.draw.ellipse(surf, CRUST_HI,
                        big.inflate(-int(w * 0.30), -int(h * 0.40)))
    sm = pygame.Rect(0, 0, int(w * 0.55), int(h * 0.55))
    if flip:
        sm.topright = (cx - int(w * 0.08), cy - int(h * 0.10))
    else:
        sm.topleft = (cx + int(w * 0.08), cy - int(h * 0.10))
    pygame.draw.ellipse(surf, OUTLINE, sm.inflate(4, 4))
    pygame.draw.ellipse(surf, CRUST_LO, sm.inflate(2, 2))
    pygame.draw.ellipse(surf, CRUST_MID, sm)
    pygame.draw.ellipse(surf, CRUST_HI,
                        sm.inflate(-int(w * 0.30), -int(h * 0.36)).move(-2, -1))
    bone_x = sm.right + 2 if not flip else sm.left - 6
    pygame.draw.rect(surf, OUTLINE,
                     pygame.Rect(bone_x - 1, cy - 2, 7, 5),
                     border_radius=2)
    pygame.draw.rect(surf, BONE,
                     pygame.Rect(bone_x, cy - 1, 5, 3),
                     border_radius=2)


def draw_chicken_nugget(surf, cx, cy, r, *, jitter_seed=0):
    """Lumpy fried-chicken nugget."""
    rng = random.Random(jitter_seed)
    pts = []
    n = 9
    for i in range(n):
        a = i * 2 * math.pi / n
        rr = r + rng.uniform(-1.4, 1.6)
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr * 0.85))
    pygame.draw.polygon(surf, OUTLINE, pts)
    pygame.draw.polygon(surf, CRUST_LO, [(p[0], p[1] + 1) for p in pts])
    pygame.draw.polygon(surf, CRUST_MID, [(p[0], p[1]) for p in pts])
    pts_i = [(cx + (x - cx) * 0.55, cy + (y - cy) * 0.55 - 1)
             for (x, y) in pts]
    pygame.draw.polygon(surf, CRUST_HI, pts_i)
    for _ in range(3):
        bx = int(cx + rng.uniform(-r * 0.6, r * 0.6))
        by = int(cy + rng.uniform(-r * 0.6, r * 0.6))
        _aa_filled_circle(surf, bx, by, 1, CRUMB)


def draw_popcorn(surf, cx, cy, r=4, *, jitter_seed=0):
    """Tiny popcorn-chicken bite."""
    rng = random.Random(jitter_seed)
    pts = []
    n = 7
    for i in range(n):
        a = i * 2 * math.pi / n
        rr = r + rng.uniform(-0.8, 1.0)
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr * 0.9))
    pygame.draw.polygon(surf, OUTLINE, pts)
    pygame.draw.polygon(surf, CRUST_MID, [(p[0], p[1]) for p in pts])
    pts_i = [(cx + (x - cx) * 0.55, cy + (y - cy) * 0.55 - 1)
             for (x, y) in pts]
    pygame.draw.polygon(surf, CRUST_HI, pts_i)


def draw_drip(surf, x, y, length, *, color, hi=None, width=4):
    """Vertical drip with rounded blob at the bottom."""
    pygame.draw.line(surf, OUTLINE, (x, y), (x, y + length), width + 2)
    pygame.draw.line(surf, _shade(color, -40), (x, y), (x, y + length), width)
    pygame.draw.line(surf, color, (x - 1, y), (x - 1, y + length - 2),
                     max(1, width - 2))
    _aa_filled_circle(surf, x, y + length, max(3, width), OUTLINE)
    _aa_filled_circle(surf, x, y + length, max(2, width - 1), color)
    if hi is not None:
        _aa_filled_circle(surf, x - 1, y + length - 1, max(1, width - 3), hi)


def draw_sesame(surf, rect, n=8, *, seed=0, band='top'):
    """Tear-drop sesame seeds on the top (or bottom) band of a bun."""
    rng = random.Random(seed * 17 + 91)
    for _ in range(n):
        x = rng.randint(rect.x + 4, rect.right - 4)
        if band == 'top':
            y = rng.randint(rect.y + 3, rect.y + max(4, rect.height // 3))
        else:
            y = rng.randint(rect.bottom - max(4, rect.height // 3),
                            rect.bottom - 3)
        pygame.draw.ellipse(surf, OUTLINE,
                            pygame.Rect(x - 2, y - 1, 4, 3))
        pygame.draw.ellipse(surf, (250, 234, 196),
                            pygame.Rect(x - 1, y - 1, 3, 2))


# ===========================================================================
# Variant 0 - Hot Dog (V2-bun1 Classic Side)
# ===========================================================================

_HD_BUN_W = 18
_HD_SAUSAGE_W = 30
_HD_EXTRUDE = 4
_HD_SAUSAGE_PROTRUDE = 8


def _hd_bun_anchor(rect):
    x, w = rect.x, rect.width
    return (x - _HD_EXTRUDE,
            x - _HD_EXTRUDE + _HD_BUN_W,
            x + w + _HD_EXTRUDE - _HD_BUN_W,
            x + w + _HD_EXTRUDE)


def _hd_draw_bun(surf, rect):
    x_lo, _, x_ri, _ = _hd_bun_anchor(rect)
    radius = _HD_BUN_W // 2 + 2
    for outer_x in (x_lo, x_ri):
        bun = pygame.Rect(outer_x, rect.y, _HD_BUN_W, rect.height)
        pygame.draw.rect(surf, OUTLINE, bun.inflate(4, 4),
                         border_radius=radius)
        pygame.draw.rect(surf, BUN_LO, bun.inflate(2, 2),
                         border_radius=radius)
        pygame.draw.rect(surf, BUN_MID, bun, border_radius=radius)
        is_left = (outer_x == x_lo)
        hl_x = bun.x + 3 if is_left else bun.right - 6
        hl = pygame.Rect(hl_x, bun.y + 6, 3, bun.height - 12)
        pygame.draw.rect(surf, BUN_HI, hl, border_radius=2)


def _hd_draw_sausage(surf, rect, *, gap_side):
    """Vertical sausage centered, protrudes past the gap edge.
    Includes mustard zigzag + ketchup dots."""
    x, y, w, h = rect
    sx = x + (w - _HD_SAUSAGE_W) // 2
    if gap_side == 'bottom':
        sy = y
        sh = h + _HD_SAUSAGE_PROTRUDE
    else:
        sy = max(0, y - _HD_SAUSAGE_PROTRUDE)
        sh = h + (y - sy)
    s = pygame.Rect(sx, sy, _HD_SAUSAGE_W, sh)
    radius_s = _HD_SAUSAGE_W // 2 + 2
    pygame.draw.rect(surf, OUTLINE, s.inflate(4, 4), border_radius=radius_s)
    pygame.draw.rect(surf, SAUSAGE_LO, s.inflate(2, 2), border_radius=radius_s)
    pygame.draw.rect(surf, SAUSAGE_MID, s, border_radius=radius_s)
    pygame.draw.rect(surf, SAUSAGE_HI,
                     pygame.Rect(s.x + 4, s.y + 4,
                                 max(2, _HD_SAUSAGE_W // 3),
                                 max(2, sh - 14)),
                     border_radius=_HD_SAUSAGE_W // 4)
    n = max(6, sh // 12)
    amp = max(3, _HD_SAUSAGE_W // 4)
    cx = s.centerx
    pts_m = [(cx + (amp if i % 2 == 0 else -amp),
              s.y + 8 + i * (sh - 16) // max(1, n - 1))
             for i in range(n)]
    pygame.draw.lines(surf, _shade(MUSTARD, -40), False, pts_m, 5)
    pygame.draw.lines(surf, MUSTARD, False, pts_m, 3)
    pygame.draw.lines(surf, MUSTARD_HI, False, pts_m, 1)
    for i in range(0, n, 2):
        bx, by = pts_m[i]
        _aa_filled_circle(surf, int(bx), int(by), 2, KETCHUP)
        _aa_filled_circle(surf, int(bx), int(by), 1, KETCHUP_HI)


def draw_pillar_kfc_hot_dog(surf, top_rect, bot_rect, palette, seed):
    _hd_draw_bun(surf, top_rect)
    _hd_draw_bun(surf, bot_rect)
    _hd_draw_sausage(surf, top_rect, gap_side='bottom')
    _hd_draw_sausage(surf, bot_rect, gap_side='top')


# ===========================================================================
# Variant 1 - Bucket Stack (V3-stack1 Mini Flag)
# ===========================================================================

def _bucket_draw(surf, rect, *, label_text="KFC", n_stripes=4,
                 draw_label=True):
    """Single red+white-striped trapezoid bucket. Returns (rim_rect,
    label_band_rect) so callers can re-draw the upright text after a flip."""
    x, y, w, h = rect
    top_w = w
    bot_w = max(8, int(w * 0.74))
    tl = (x, y + 4)
    tr = (x + top_w, y + 4)
    br = (x + (top_w - bot_w) // 2 + bot_w, y + h)
    bl = (x + (top_w - bot_w) // 2, y + h)
    poly = [tl, tr, br, bl]
    pygame.draw.polygon(surf, OUTLINE, [(px, py + 1) for (px, py) in poly])
    pygame.draw.polygon(surf, KFC_WHITE, poly)
    for i in range(n_stripes):
        u0 = (i + 0.10) / n_stripes
        u1 = (i + 0.55) / n_stripes
        sx0_top = tl[0] + (tr[0] - tl[0]) * u0
        sx1_top = tl[0] + (tr[0] - tl[0]) * u1
        sx0_bot = bl[0] + (br[0] - bl[0]) * u0
        sx1_bot = bl[0] + (br[0] - bl[0]) * u1
        pygame.draw.polygon(surf, KFC_RED,
                            [(sx0_top, tl[1]), (sx1_top, tl[1]),
                             (sx1_bot, br[1]), (sx0_bot, br[1])])
    pygame.draw.polygon(surf, OUTLINE, poly, 2)
    rim = pygame.Rect(tl[0] - 2, tl[1] - 4, top_w + 4, 8)
    pygame.draw.rect(surf, OUTLINE, rim.inflate(2, 2), border_radius=4)
    pygame.draw.rect(surf, KFC_RED_D, rim, border_radius=4)
    pygame.draw.rect(surf, KFC_RED, rim.inflate(-4, -3), border_radius=3)
    label_y = (tl[1] + br[1]) // 2 - 6
    label_w = max(20, top_w - 16)
    label_x = (tl[0] + tr[0]) // 2 - label_w // 2
    font_band = pygame.Rect(label_x, label_y, label_w, 14)
    pygame.draw.rect(surf, OUTLINE, font_band.inflate(2, 2), border_radius=3)
    pygame.draw.rect(surf, KFC_WHITE, font_band, border_radius=3)
    if draw_label:
        try:
            font = pygame.font.SysFont(None, 14, bold=True)
            txt = font.render(label_text, True, KFC_RED)
            surf.blit(txt, (font_band.centerx - txt.get_width() // 2,
                              font_band.centery - txt.get_height() // 2))
        except Exception:
            pass
    return rim, font_band


def _bucket_chicken_pile(surf, rim, seed):
    """V3-stack1 mix: drumstick + wing + 3 nuggets + 2 popcorn."""
    cx = rim.centerx
    base_y = rim.top - 2
    draw_drumstick(surf, cx - 12, base_y - 6, 18, 22,
                   tilt=-22, bone_top=False, seed=seed)
    draw_chicken_wing(surf, cx + 10, base_y - 4, 22, 16, flip=False)
    for i, ux in enumerate((-6, 4, 14)):
        draw_chicken_nugget(surf, cx + ux + (i * 2 - 4),
                            base_y - 12 + (i % 2) * 4, 6,
                            jitter_seed=seed + i * 13)
    draw_popcorn(surf, cx - 4, base_y - 16, jitter_seed=seed + 7)
    draw_popcorn(surf, cx + 8, base_y - 18, jitter_seed=seed + 11)


def _bucket_pennant(surf, base_x, base_y, *, length=16, color=KFC_RED,
                    tilt=0):
    """Triangular pennant on a thin toothpick stuck into the chicken pile."""
    height = 10
    stick_h = 16
    layer = pygame.Surface((length + 8, stick_h + height + 8),
                           pygame.SRCALPHA)
    sx = 4
    sy_bot = stick_h + height + 4
    sy_top = sy_bot - stick_h
    pygame.draw.line(layer, OUTLINE, (sx, sy_top - 1), (sx, sy_bot + 1), 4)
    pygame.draw.line(layer, WOOD_LO, (sx, sy_top), (sx, sy_bot), 2)
    pygame.draw.line(layer, WOOD_HI, (sx, sy_top + 1), (sx, sy_bot - 1), 1)
    pen = [(sx, sy_top + 1),
           (sx + length, sy_top + height // 2 + 1),
           (sx, sy_top + height + 1)]
    pygame.draw.polygon(layer, OUTLINE, [(p[0] + 1, p[1] + 1) for p in pen])
    pygame.draw.polygon(layer, color, pen)
    pygame.draw.line(layer, KFC_WHITE,
                     (sx + 3, sy_top + height // 2 + 1),
                     (sx + length // 2, sy_top + height // 2 + 1), 1)
    if tilt:
        layer = pygame.transform.rotate(layer, tilt)
    out = layer.get_rect(midbottom=(base_x, base_y))
    surf.blit(layer, out.topleft)


def _bucket_flag_v1(surf, rim):
    """V3-stack1 Mini Flag: single small red pennant slightly off-centre."""
    _bucket_pennant(surf, rim.centerx + 4, rim.top - 16, length=16,
                    color=KFC_RED, tilt=0)


def _stack_buckets(surf, rect, *, gap_side, label="KFC", bucket_h=64,
                   seed=0, with_flag=False):
    """Stack flush-against-each-other buckets in `rect`. The gap-facing
    bucket gets the chicken pile; on top pillars (flipped buckets) the
    pile is mirrored vertically so the chicken hangs DOWN out of the
    rim toward the gap, not up into the bucket interior."""
    x, y, w, h = rect
    n = max(1, h // bucket_h)
    rims = []
    for i in range(n):
        if gap_side == 'top':
            rb = pygame.Rect(x - 4, y + h - (i + 1) * bucket_h,
                             w + 8, bucket_h)
        else:
            rb = pygame.Rect(x - 4, y + i * bucket_h, w + 8, bucket_h)
        if rb.bottom > y + h:
            rb.height -= rb.bottom - (y + h)
        if rb.top < y:
            rb.height -= y - rb.top
            rb.top = y
        if rb.height < 18:
            continue
        if gap_side == 'bottom':
            layer = pygame.Surface((rb.width, rb.height), pygame.SRCALPHA)
            inner_rect = pygame.Rect(0, 0, rb.width, rb.height)
            local_rim, local_label = _bucket_draw(
                layer, inner_rect, label_text=label, draw_label=False)
            layer = pygame.transform.flip(layer, False, True)
            surf.blit(layer, rb.topleft)
            lh = layer.get_height()
            real_rim = pygame.Rect(rb.x + local_rim.x,
                                   rb.y + (lh - local_rim.bottom),
                                   local_rim.width, local_rim.height)
            real_label = pygame.Rect(rb.x + local_label.x,
                                     rb.y + (lh - local_label.bottom),
                                     local_label.width, local_label.height)
            rims.append((real_rim, real_label))
        else:
            rim, label_band = _bucket_draw(
                surf, pygame.Rect(rb.x, rb.y, rb.width, rb.height),
                label_text=label)
            rims.append((rim, label_band))

    if gap_side == 'bottom':
        try:
            font = pygame.font.SysFont(None, 14, bold=True)
            txt = font.render(label, True, KFC_RED)
            for _rim, lb in rims:
                surf.blit(txt, (lb.centerx - txt.get_width() // 2,
                                  lb.centery - txt.get_height() // 2))
        except Exception:
            pass

    if rims:
        gap_rim = rims[-1][0]
        if gap_side == 'bottom':
            pile_w = gap_rim.width + 80
            pile_h = 50
            pile_surf = pygame.Surface((pile_w, pile_h), pygame.SRCALPHA)
            local_rim = pygame.Rect(40, pile_h - gap_rim.height,
                                    gap_rim.width, gap_rim.height)
            _bucket_chicken_pile(pile_surf, local_rim, seed + 100)
            pile_surf = pygame.transform.flip(pile_surf, False, True)
            surf.blit(pile_surf, (gap_rim.x - 40,
                                  gap_rim.bottom - gap_rim.height))
        else:
            _bucket_chicken_pile(surf, gap_rim, seed)
            if with_flag:
                _bucket_flag_v1(surf, gap_rim)


def draw_pillar_kfc_bucket(surf, top_rect, bot_rect, palette, seed):
    _stack_buckets(surf, top_rect, gap_side='bottom', bucket_h=64,
                   seed=seed + 100)
    _stack_buckets(surf, bot_rect, gap_side='top', bucket_h=64,
                   seed=seed, with_flag=True)


# ===========================================================================
# Variant 2 - Corn Dog (V4-corn1 Classic Golden)
# ===========================================================================

def _corn_draw_rod(surf, rect, *, flat_top=False):
    x, y, w, h = rect
    rod = pygame.Rect(x - 1, y, w + 2, h)
    radius = max(8, w // 2 + 2)
    if flat_top:
        rad_kwargs = dict(border_top_left_radius=0,
                          border_top_right_radius=0,
                          border_bottom_left_radius=radius,
                          border_bottom_right_radius=radius)
    else:
        rad_kwargs = dict(border_radius=radius)
    pygame.draw.rect(surf, (*SHADOW, 60),
                     rod.inflate(6, 6).move(2, 2), **rad_kwargs)
    pygame.draw.rect(surf, OUTLINE, rod.inflate(4, 4), **rad_kwargs)
    pygame.draw.rect(surf, CRUST_LO, rod.inflate(2, 2), **rad_kwargs)
    pygame.draw.rect(surf, CRUST_MID, rod, **rad_kwargs)
    hl = pygame.Rect(rod.x + 4, rod.y + 4,
                     max(3, rod.width // 3), rod.height - 8)
    pygame.draw.rect(surf, CRUST_HI, hl, border_radius=radius // 2)
    return rod


def _corn_scatter_bumps(surf, rod, *, seed=0):
    rng = random.Random(seed * 19 + 7)
    n = max(28, rod.height // 5)
    for _ in range(n):
        bx = rng.randint(rod.x + 3, rod.right - 3)
        by = rng.randint(rod.y + 4, rod.bottom - 4)
        r = rng.randint(2, 4)
        _aa_filled_circle(surf, bx + 1, by + 1, r, _shade(CRUST_LO, -10))
        _aa_filled_circle(surf, bx, by, r, _shade(CRUST_MID, +18))
        _aa_filled_circle(surf, bx - 1, by - 1, max(1, r - 2), CRUMB)


def _corn_wood_stick(surf, cx, top_y, length):
    """Plain wooden skewer (no ribbon) protruding into the gap."""
    stick_w = 10
    stick = pygame.Rect(cx - stick_w // 2, top_y, stick_w, length)
    pygame.draw.rect(surf, OUTLINE, stick.inflate(2, 2), border_radius=4)
    pygame.draw.rect(surf, WOOD_LO, stick, border_radius=4)
    pygame.draw.rect(surf, WOOD_HI,
                     pygame.Rect(stick.x + 2, stick.y + 2, 3,
                                 stick.height - 4),
                     border_radius=2)
    for i in range(2):
        pygame.draw.line(surf, _shade(WOOD_LO, -40),
                         (stick.x + 2, stick.y + 6 + i * 8),
                         (stick.right - 2, stick.y + 6 + i * 8), 1)


def draw_pillar_kfc_corn_dog(surf, top_rect, bot_rect, palette, seed):
    for r, side in ((top_rect, 'top'), (bot_rect, 'bot')):
        rod = _corn_draw_rod(surf, r, flat_top=(side == 'top'))
        _corn_scatter_bumps(surf, rod,
                            seed=seed + (1 if side == 'top' else 2))
        for i, dx in enumerate((rod.x + 4, rod.right - 6, rod.centerx + 4)):
            dy = rod.y + 18 + i * 22
            if dy + 22 < rod.bottom:
                draw_drip(surf, dx, dy, 22 + (i % 2) * 4,
                          color=HONEY_MID, hi=HONEY_HI, width=4)
    _corn_wood_stick(surf, top_rect.centerx, top_rect.bottom - 2, 26)
    _corn_wood_stick(surf, bot_rect.centerx, bot_rect.top - 26, 26)


# ===========================================================================
# Variant 3 - Sandwich Tower (V5-stack1 Classic Combo)
# ===========================================================================

_LAYER_BUN_TOP = 'bun_top'
_LAYER_BUN_BOT = 'bun_bot'
_LAYER_FILLET  = 'fillet'
_LAYER_CHEESE  = 'cheese'
_LAYER_LETTUCE = 'lettuce'

_LAYER_HEIGHTS = {
    _LAYER_BUN_TOP: 30,
    _LAYER_BUN_BOT: 20,
    _LAYER_FILLET:  28,
    _LAYER_CHEESE:  12,
    _LAYER_LETTUCE: 14,
}

_LAYER_SEQ = (_LAYER_BUN_TOP, _LAYER_FILLET, _LAYER_CHEESE,
              _LAYER_LETTUCE, _LAYER_FILLET, _LAYER_BUN_BOT)


def _sandwich_draw_layer(surf, rect, kind, *, seed=0, flat_top=False):
    x, y, w, h = rect
    if h < 4:
        return
    if kind == _LAYER_BUN_TOP:
        r = pygame.Rect(x - 2, y, w + 4, h)
        if flat_top:
            rad_kwargs = dict(border_top_left_radius=0,
                              border_top_right_radius=0,
                              border_bottom_left_radius=int(h * 0.7),
                              border_bottom_right_radius=int(h * 0.7))
        else:
            rad_kwargs = dict(border_radius=int(h * 0.7))
        pygame.draw.rect(surf, OUTLINE, r.inflate(4, 4), **rad_kwargs)
        pygame.draw.rect(surf, BUN_LO, r.inflate(2, 2), **rad_kwargs)
        pygame.draw.rect(surf, BUN_MID, r, **rad_kwargs)
        hl = pygame.Rect(r.x + 4, r.y + 3, r.width - 8,
                         max(3, int(h * 0.40)))
        pygame.draw.rect(surf, BUN_HI, hl,
                         border_radius=int(hl.height * 0.8))
        if not flat_top:
            draw_sesame(surf, r, n=8, seed=seed + y, band='top')

    elif kind == _LAYER_BUN_BOT:
        r = pygame.Rect(x - 2, y, w + 4, h)
        pygame.draw.rect(surf, OUTLINE, r.inflate(4, 4),
                         border_radius=int(h * 0.6))
        pygame.draw.rect(surf, BUN_LO, r.inflate(2, 2),
                         border_radius=int(h * 0.6))
        pygame.draw.rect(surf, BUN_MID, r, border_radius=int(h * 0.6))

    elif kind == _LAYER_FILLET:
        r = pygame.Rect(x - 6, y, w + 12, h)
        pts = []
        n = 12
        for i in range(n + 1):
            u = i / n
            wave = math.sin(u * math.pi * 3 + seed) * 2
            pts.append((r.x + u * r.width, r.y + wave))
        for i in range(n + 1):
            u = (n - i) / n
            wave = math.sin(u * math.pi * 3 + seed + 1) * 2
            pts.append((r.x + u * r.width, r.bottom - wave))
        pygame.draw.polygon(surf, OUTLINE, pts)
        pygame.draw.polygon(surf, CRUST_LO, [(p[0], p[1] + 1) for p in pts])
        pygame.draw.polygon(surf, CRUST_MID, [(p[0], p[1] + 2) for p in pts])
        rng = random.Random(seed + y * 7)
        for _ in range(int(r.width * h / 18)):
            bx = rng.randint(r.x + 4, r.right - 4)
            by = rng.randint(r.y + 2, r.bottom - 2)
            _aa_filled_circle(surf, bx, by, 1, CRUMB)
        hl = pygame.Rect(r.x + 6, r.y + 2, r.width - 12, max(2, h // 3))
        pygame.draw.rect(surf, CRUST_HI, hl, border_radius=h // 4)

    elif kind == _LAYER_CHEESE:
        r = pygame.Rect(x - 6, y, w + 12, h)
        pygame.draw.rect(surf, OUTLINE, r.inflate(4, 4), border_radius=4)
        pygame.draw.rect(surf, CHEESE_LO, r.inflate(2, 2), border_radius=3)
        pygame.draw.rect(surf, CHEESE, r, border_radius=3)
        for sx in (r.x + 8, r.right - 12):
            pts = [(sx, r.bottom),
                   (sx + 4, r.bottom + 6),
                   (sx + 8, r.bottom)]
            pygame.draw.polygon(surf, OUTLINE,
                                [(p[0], p[1] + 1) for p in pts])
            pygame.draw.polygon(surf, CHEESE, pts)

    elif kind == _LAYER_LETTUCE:
        r = pygame.Rect(x - 8, y - 2, w + 16, h + 4)
        pygame.draw.rect(surf, OUTLINE, r.inflate(2, 2), border_radius=3)
        pygame.draw.rect(surf, LETTUCE_LO, r, border_radius=3)
        n_bumps = max(5, r.width // 7)
        for i in range(n_bumps):
            bx = int(r.x + (i + 0.5) * r.width / n_bumps)
            for by, rr in ((r.y, 4), (r.bottom, 3)):
                _aa_filled_circle(surf, bx, by, rr, OUTLINE)
                _aa_filled_circle(surf, bx, by, max(1, rr - 1), LETTUCE_MID)
                _aa_filled_circle(surf, bx - 1, by - 1, max(1, rr - 2),
                                  LETTUCE_HI)


def _sandwich_stack(surf, rect, *, gap_side, seed=0, flat_top_first=False):
    x, y, w, h = rect
    if gap_side == 'top':
        seq = list(reversed(_LAYER_SEQ))
    else:
        seq = list(_LAYER_SEQ)
    cy = y
    i = 0
    while cy < y + h:
        kind = seq[i % len(seq)]
        lh = _LAYER_HEIGHTS[kind]
        r = pygame.Rect(x, cy, w, min(lh, y + h - cy))
        is_first = (i == 0 and gap_side == 'bottom')
        _sandwich_draw_layer(surf, r, kind, seed=seed,
                             flat_top=(is_first and flat_top_first))
        cy += lh
        i += 1


def _sandwich_skewer(surf, rect):
    pick_x = rect.centerx
    pick_top = rect.top - 18
    pick_bot = rect.top + min(rect.height - 4, 90)
    pygame.draw.line(surf, OUTLINE, (pick_x, pick_top), (pick_x, pick_bot), 4)
    pygame.draw.line(surf, WOOD_HI, (pick_x, pick_top + 1),
                     (pick_x, pick_bot - 1), 2)
    frill = [(pick_x - 7, pick_top - 2),
             (pick_x + 7, pick_top - 6),
             (pick_x, pick_top + 2)]
    pygame.draw.polygon(surf, OUTLINE, [(p[0], p[1] + 1) for p in frill])
    pygame.draw.polygon(surf, KFC_RED, frill)


def draw_pillar_kfc_sandwich(surf, top_rect, bot_rect, palette, seed):
    _sandwich_stack(surf, top_rect, gap_side='bottom', seed=seed,
                    flat_top_first=True)
    _sandwich_stack(surf, bot_rect, gap_side='top', seed=seed)
    _sandwich_skewer(surf, bot_rect)


# ===========================================================================
# Dispatcher
# ===========================================================================

# Active KFC pillar pool. Bucket appears TWICE so its `seed % 4` probability
# is 50% (slots 1 and 3); hot dog and corn dog each get one slot for 25%.
# The sandwich variant (draw_pillar_kfc_sandwich) is kept fully defined
# above but is intentionally NOT listed here - it was hard to read at
# gameplay scale and has been retired from the rotation. Re-add it to
# this tuple to bring it back.
KFC_DRAWERS = (
    draw_pillar_kfc_hot_dog,    # slot 0  → 25%
    draw_pillar_kfc_bucket,     # slot 1  ┐
    draw_pillar_kfc_corn_dog,   # slot 2  │ → 25%
    draw_pillar_kfc_bucket,     # slot 3  ┘ → bucket total 50%
)


def draw_pillar_pair_kfc(surf, top_rect, bot_rect, palette, seed):
    """Route to one of the active KFC pillar designs by `seed % 4`.

    Distribution is 50% bucket / 25% hot dog / 25% corn dog. Pipe seeds
    are stable for the lifetime of the Pipe instance, so a given pillar
    keeps the same look as it scrolls across the screen.
    """
    KFC_DRAWERS[seed % len(KFC_DRAWERS)](surf, top_rect, bot_rect,
                                          palette, seed)
