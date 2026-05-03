"""Hi-res GROW-mode parrot — 5 resolution variants (round 9, picker).

The current grown bird is `pygame.transform.smoothscale(parrot.FRAMES[i],
1.5x)` which upscales a 68×64 procedural sprite to 102×96 — that
upscale is what produces the blur the user reported. The procedural
draw is just polygons and ellipses with literal coordinates; if we
multiply every coordinate by `scale` and draw on a larger surface,
we get a true hi-res render with no upscale.

Each `build_v*` returns a 102×96 sprite ready to drop into the live
draw path in place of the current smoothscaled sprite. v0 reproduces
the current blurry path so the picker can show a side-by-side compare.

Imported by `tools/render_grow_parrot_gameplay.py`. Does NOT modify
any `game/` file.
"""
import math
import pygame

from game.draw import (
    BIRD_RED, BIRD_RED_D, BIRD_WING, BIRD_WING_D, BIRD_TIP,
    BIRD_BELLY, BIRD_BEAK, BIRD_BEAK_D, WHITE, BLACK, NEAR_BLACK,
)

# ── Constants mirrored from game/parrot.py ─────────────────────────────────
SRC_W, SRC_H = 64, 60               # base sprite size (no outline)
WING_BOX     = 50                   # _build_wing uses a 50×50 working surface
GROW_SCALE   = 1.5                  # game/config.py
PAD          = 2                    # _add_outline padding (in source px)
TARGET_W     = int((SRC_W + PAD * 2) * GROW_SCALE)   # 102
TARGET_H     = int((SRC_H + PAD * 2) * GROW_SCALE)   # 96

SHADE_BLACK = (15, 15, 25)
SHADE_FRAME = (255, 200, 50)
SHADE_GLINT = (255, 255, 255)
SHADE_TINT  = (35,  55,  90)


# ── Coordinate-scaling helpers ─────────────────────────────────────────────
def _S(v, s):  return int(round(v * s))
def _sp(p, s): return (_S(p[0], s), _S(p[1], s))
def _spl(pts, s): return [_sp(p, s) for p in pts]


def _aaellipse_scaled(surf, color, center, rx, ry, s):
    cx, cy = center
    rect = pygame.Rect(_S(cx - rx, s), _S(cy - ry, s),
                       _S(rx * 2, s),  _S(ry * 2, s))
    pygame.draw.ellipse(surf, color, rect)


# ── Wing (mirrors parrot._build_wing, scale-aware) ─────────────────────────
def _build_wing_scaled(angle_deg, s, *, extra_detail=False):
    box = _S(WING_BOX, s)
    w = pygame.Surface((box, box), pygame.SRCALPHA)

    pygame.draw.polygon(w, (0, 0, 0, 110), _spl([
        (24, 26), (46, 14), (50, 30), (34, 44), (18, 40),
    ], s))
    pygame.draw.polygon(w, BIRD_WING, _spl([
        (24, 24), (44, 13), (48, 28), (32, 42), (18, 36),
    ], s))
    pygame.draw.polygon(w, BIRD_WING_D, _spl([
        (24, 24), (32, 42), (18, 36),
    ], s))
    pygame.draw.polygon(w, BIRD_TIP, _spl([
        (44, 13), (50, 18), (48, 28),
    ], s))
    pygame.draw.polygon(w, (255, 200, 60), _spl([
        (42, 18), (48, 22), (46, 28), (40, 24),
    ], s))

    div_w = max(1, _S(2, s))
    pygame.draw.line(w, BIRD_WING_D, _sp((26, 25), s), _sp((42, 18), s), div_w)
    pygame.draw.line(w, BIRD_WING_D, _sp((28, 30), s), _sp((44, 25), s), div_w)
    pygame.draw.line(w, BIRD_WING_D, _sp((30, 34), s), _sp((46, 32), s), div_w)
    hi_w = max(1, _S(1, s))
    pygame.draw.line(w, (170, 210, 255),
                     _sp((25, 25), s), _sp((41, 15), s), hi_w)

    if extra_detail:
        # Extra fine feather striations — sub-pixel at base 64×60 so they
        # would dissolve into the smoothscale, but at scale ≥ 3 they read.
        fine_w = max(1, int(round(s * 0.6)))
        for (x1, y1, x2, y2) in ((27, 28, 39, 22),
                                 (28, 32, 40, 27),
                                 (30, 35, 42, 31)):
            pygame.draw.line(w, (190, 220, 255),
                             _sp((x1, y1), s), _sp((x2, y2), s), fine_w)

    return pygame.transform.rotate(w, angle_deg)


# ── Sunglasses (mirrors parrot._draw_sunglasses, scale-aware) ──────────────
def _draw_sunglasses_scaled(surf, cx, cy, s, *, extra_detail=False):
    r_outer = 6
    left  = (cx - 4, cy)
    right = (cx + 6, cy - 1)

    pygame.draw.circle(surf, SHADE_FRAME, _sp(left, s),  _S(r_outer + 1, s))
    pygame.draw.circle(surf, SHADE_FRAME, _sp(right, s), _S(r_outer + 1, s))
    pygame.draw.circle(surf, SHADE_BLACK, _sp(left, s),  _S(r_outer, s))
    pygame.draw.circle(surf, SHADE_BLACK, _sp(right, s), _S(r_outer, s))

    # Sky-tint upper half
    tw = _S(r_outer * 2, s)
    th = _S(r_outer, s)
    tint = pygame.Surface((tw, th), pygame.SRCALPHA)
    pygame.draw.ellipse(tint, (*SHADE_TINT, 130), tint.get_rect())
    surf.blit(tint, (_S(left[0]  - r_outer, s), _S(left[1]  - r_outer + 1, s)))
    surf.blit(tint, (_S(right[0] - r_outer, s), _S(right[1] - r_outer + 1, s)))

    # Glints
    pygame.draw.circle(surf, SHADE_GLINT, _sp((left[0]  - 2, left[1]  - 2), s), _S(2, s))
    pygame.draw.circle(surf, SHADE_GLINT, _sp((right[0] - 2, right[1] - 3), s), _S(2, s))
    pygame.draw.circle(surf, (255, 255, 255, 200),
                       _sp((left[0]  + 2, left[1]  + 2), s), max(1, _S(1, s)))
    pygame.draw.circle(surf, (255, 255, 255, 200),
                       _sp((right[0] + 2, right[1] + 1), s), max(1, _S(1, s)))

    if extra_detail:
        # Extra crescent specular sweep along the bottom-right of each lens —
        # fine arc that resolves at high source res and reads as wet-glass.
        arc_w = max(1, int(round(s * 0.6)))
        for centre in (left, right):
            cx_p = _S(centre[0], s)
            cy_p = _S(centre[1], s)
            r_arc = _S(r_outer - 1, s)
            arc_rect = pygame.Rect(cx_p - r_arc, cy_p - r_arc, r_arc * 2, r_arc * 2)
            pygame.draw.arc(surf, (255, 255, 255, 180), arc_rect,
                            math.radians(-50), math.radians(20), arc_w)

    # Bridge + brow bar
    bridge_w = max(1, _S(2, s))
    pygame.draw.line(surf, SHADE_FRAME,
                     _sp((left[0]  + r_outer, left[1]),  s),
                     _sp((right[0] - r_outer, right[1]), s), bridge_w)
    brow_w = max(1, _S(1, s))
    pygame.draw.line(surf, SHADE_FRAME,
                     _sp((left[0]  - r_outer + 1, left[1]  - r_outer + 2), s),
                     _sp((right[0] + r_outer - 1, right[1] - r_outer + 2), s), brow_w)


# ── Frame (mirrors parrot._build_frame, scale-aware) ───────────────────────
def _build_frame_scaled(wing_angle_deg, s, *, extra_detail=False):
    surf = pygame.Surface((_S(SRC_W, s), _S(SRC_H, s)), pygame.SRCALPHA)

    # Tail layered fan
    tail_colors = [
        (200,  30,  40),
        (240,  95,  40),
        (255, 160,  55),
        (255, 220,  80),
    ]
    for i, c in enumerate(tail_colors):
        pts = [
            (2 + i * 3, 26 + i * 2),
            (14 + i,     24 + i),
            (20 + i,     30 + i * 2),
            (6 + i * 3,  36 + i * 2),
        ]
        pygame.draw.polygon(surf, c, _spl(pts, s))
    div_w = max(1, _S(1, s))
    pygame.draw.line(surf, BIRD_RED_D, _sp((4, 27), s), _sp((18, 31), s), div_w)
    pygame.draw.line(surf, BIRD_RED_D, _sp((6, 33), s), _sp((20, 35), s), div_w)

    # Body shadow + base + chest + belly + sheen
    _aaellipse_scaled(surf, (120, 20, 25), (34, 35), 19, 14, s)
    _aaellipse_scaled(surf, BIRD_RED,      (32, 32), 19, 14, s)
    _aaellipse_scaled(surf, (255, 100, 100),(30, 29), 13,  8, s)
    _aaellipse_scaled(surf, BIRD_BELLY,    (28, 38), 12,  6, s)

    sw = _S(28, s); sh = _S(6, s)
    sheen = pygame.Surface((sw, sh), pygame.SRCALPHA)
    pygame.draw.ellipse(sheen, (255, 230, 230, 160), sheen.get_rect())
    surf.blit(sheen, (_S(22, s), _S(21, s)))

    # Wing — built scaled, blitted at scaled centre
    wing = _build_wing_scaled(wing_angle_deg, s, extra_detail=extra_detail)
    wr = wing.get_rect(center=_sp((34, 28), s))
    surf.blit(wing, wr.topleft)

    # Head
    _aaellipse_scaled(surf, (150, 15, 20), (48, 23), 12, 11, s)
    _aaellipse_scaled(surf, BIRD_RED,      (47, 21), 12, 11, s)
    _aaellipse_scaled(surf, (255, 130, 130),(44, 24),  4,  3, s)
    _aaellipse_scaled(surf, (255, 170, 170),(46, 16),  7,  3, s)

    # Aviator shades
    _draw_sunglasses_scaled(surf, 50, 20, s, extra_detail=extra_detail)

    # Beak — hooked + gloss + split
    beak_pts = [(55, 21), (61, 24), (58, 28), (52, 26)]
    pygame.draw.polygon(surf, BIRD_BEAK,   _spl(beak_pts, s))
    pygame.draw.polygon(surf, BIRD_BEAK_D, _spl(beak_pts, s), max(1, _S(1, s)))
    gloss_w = max(1, _S(1, s))
    pygame.draw.line(surf, (255, 230, 150), _sp((55, 22), s), _sp((59, 24), s), gloss_w)
    pygame.draw.line(surf, BIRD_BEAK_D,     _sp((52, 24), s), _sp((58, 25), s), gloss_w)

    # Feet tucks
    foot_w = max(1, _S(2, s))
    pygame.draw.line(surf, BIRD_BEAK_D, _sp((28, 45), s), _sp((26, 49), s), foot_w)
    pygame.draw.line(surf, BIRD_BEAK_D, _sp((34, 45), s), _sp((36, 49), s), foot_w)

    if extra_detail:
        # Three faint chest-feather V marks — 1-px at scale=1 dissolves but
        # resolves cleanly at scale ≥ 3.
        v_w = max(1, int(round(s * 0.5)))
        for (x, y) in ((26, 35), (29, 38), (32, 41)):
            pygame.draw.line(surf, (200,  40,  50),
                             _sp((x, y), s), _sp((x + 2, y + 1), s), v_w)
            pygame.draw.line(surf, (200,  40,  50),
                             _sp((x + 2, y + 1), s), _sp((x + 4, y), s), v_w)
        # Tiny extra beak highlight pinprick
        pygame.draw.circle(surf, (255, 250, 210),
                           _sp((57, 23), s), max(1, int(round(s * 0.5))))

    return surf


# ── Outline (mirrors parrot._add_outline, scale-aware) ─────────────────────
def _add_outline_scaled(src, scale, *, outline_color=(20, 12, 18, 220),
                        thin=False):
    """Outline thickness scales with `scale` so that after smoothscale-down
    to the 102×96 display target the outline reads as ~1 px.

    `thin=True` halves the radius — for the variant that wants a crisper
    feature read (less black outline, more detail showing through)."""
    w, h = src.get_size()
    r = max(1, int(round(scale)))
    if thin:
        r = max(1, r // 2)
    pad = r + 1
    out = pygame.Surface((w + pad * 2, h + pad * 2), pygame.SRCALPHA)
    mask = pygame.mask.from_surface(src, threshold=8)
    silhouette = mask.to_surface(setcolor=outline_color, unsetcolor=(0, 0, 0, 0))
    for dx in range(-r, r + 1):
        for dy in range(-r, r + 1):
            if dx == 0 and dy == 0:
                continue
            if max(abs(dx), abs(dy)) > r:
                continue
            out.blit(silhouette, (pad + dx, pad + dy))
    out.blit(src, (pad, pad))
    return out


# ── Variant builders — each returns a 102×96 RGBA surface ──────────────────
_WING_ANGLES = (50, 20, -10, -40)


def build_v0_current(angle_deg):
    """Reference: the current blurry path. Build at scale=1, add the
    1-px outline, then smoothscale-up to 102×96."""
    src = _build_frame_scaled(angle_deg, s=1)
    outlined = _add_outline_scaled(src, scale=1)
    return pygame.transform.smoothscale(outlined, (TARGET_W, TARGET_H))


def build_v1_native_15x(angle_deg):
    """Native 1.5×: every coordinate × 1.5, no upscale step."""
    src = _build_frame_scaled(angle_deg, s=GROW_SCALE)
    outlined = _add_outline_scaled(src, scale=GROW_SCALE)
    # Already at TARGET_W×TARGET_H within rounding tolerance; force exact
    # size so the sprite slot in Bird.draw lines up perfectly.
    if outlined.get_size() != (TARGET_W, TARGET_H):
        outlined = pygame.transform.smoothscale(outlined, (TARGET_W, TARGET_H))
    return outlined


def build_v2_ss2_then_15x(angle_deg):
    """2× supersample → smoothscale-DOWN to 1.5×. Builds at scale=3,
    softens edges via downscale-only (no upscale anywhere)."""
    src = _build_frame_scaled(angle_deg, s=3)
    outlined = _add_outline_scaled(src, scale=3)
    return pygame.transform.smoothscale(outlined, (TARGET_W, TARGET_H))


def build_v3_ss3_then_15x(angle_deg):
    """3× supersample → smoothscale-DOWN to 1.5×. Builds at scale=4.5,
    sharpest curves on the cone / sunglass rims / wing edges."""
    src = _build_frame_scaled(angle_deg, s=4.5)
    outlined = _add_outline_scaled(src, scale=4.5)
    return pygame.transform.smoothscale(outlined, (TARGET_W, TARGET_H))


def build_v4_ss3_thin_outline(angle_deg):
    """v3 but with a thinner outline so the body colours and gold rim
    of the aviators read more brightly. Outline radius halved."""
    src = _build_frame_scaled(angle_deg, s=4.5)
    outlined = _add_outline_scaled(src, scale=4.5, thin=True)
    return pygame.transform.smoothscale(outlined, (TARGET_W, TARGET_H))


def build_v5_ss3_extra_detail(angle_deg):
    """v3 + extra fine detail (feather striations on the wing, chest
    feather V marks, second beak highlight, lens crescent specular)
    that wouldn't have read at the 64×60 base size."""
    src = _build_frame_scaled(angle_deg, s=4.5, extra_detail=True)
    outlined = _add_outline_scaled(src, scale=4.5)
    return pygame.transform.smoothscale(outlined, (TARGET_W, TARGET_H))


def build_frames(builder):
    """Build the 4 wing-angle frames using `builder(angle)`."""
    return [builder(a) for a in _WING_ANGLES]


BUILDERS = {
    0: ("0 — current",       build_v0_current),
    1: ("1 — native 1.5×",   build_v1_native_15x),
    2: ("2 — 2× SS",         build_v2_ss2_then_15x),
    3: ("3 — 3× SS",         build_v3_ss3_then_15x),
    4: ("4 — 3× SS + thin",  build_v4_ss3_thin_outline),
    5: ("5 — 3× SS + detail", build_v5_ss3_extra_detail),
}
