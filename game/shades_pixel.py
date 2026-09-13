"""PIXEL SHADES — blocky 8-bit "deal-with-it" black sunglasses (round 1).

Three explorations live here; ``draw_shades`` is the chosen one (variant C,
"thug life"). All three share the same idiom: every coordinate is quantized to
a pixel cell sized off ``eye_w`` so the shape reads as deliberate chunky 8-bit
blocks — hard right angles, axis-aligned rects, no anti-aliased curves — at the
product size (eye_w≈96) AND in-game (eye_w=22, where 1 cell ≈ 2px).

Side-profile macaw facing right: the near/front lens sits toward the beak
(+facing), the stepped temple arm marches back toward the ear (-facing).
"""
import pygame

# Meme-black + a single cool white glint cell. Black is lifted off pure-0 so it
# still separates from the near-black store card the way the shipped shades do.
_BLACK = (18, 18, 24)
_GLINT = (235, 240, 250)


def _cell(eye_w):
    """Pixel cell — the grid everything snaps to. eye_w/11 keeps ~2px in-game
    (eye_w=22 → 2) and a chunky ~9px on the product shot (eye_w=96)."""
    return max(1, int(round(eye_w / 11.0)))


def _snap(v, c):
    """Quantize a coordinate to the pixel-cell grid."""
    return int(round(v / c)) * c


# ─────────────────────────────────────────────────────────────────────────────
# A · PURE BLOCK — the bare meme silhouette: two solid stepped lenses joined by
#     a thin bridge bar, one stepped temple arm. No glint. Maximum 8-bit purity.
# ─────────────────────────────────────────────────────────────────────────────
def draw_shades_pure(surf, cx, cy, eye_w, facing=1):
    f = facing
    c = _cell(eye_w)
    cx, cy = _snap(cx, c), _snap(cy, c)

    lens_w = c * 3                              # 3 cells wide per lens
    top_h  = c * 2                              # tall upper row
    bridge = c * 2                              # gap between the two lenses
    near_in = cx + f * (bridge // 2)            # bridge edge toward beak
    far_in  = cx - f * (bridge // 2)

    def lens(inner_x, sign):
        x0 = inner_x if sign > 0 else inner_x - lens_w
        # tall top row + a one-cell-shorter lower row stepped in on the outer
        # side — the signature "deal with it" notched corner.
        surf.fill(_BLACK, (x0, cy - top_h, lens_w, top_h))
        step = x0 + (0 if sign > 0 else c)
        surf.fill(_BLACK, (step, cy, lens_w - c, c))

    lens(near_in, +1)
    lens(far_in, -1)

    # Thin bridge bar bridging the two top rows.
    bx = min(near_in, far_in)
    surf.fill(_BLACK, (bx, cy - top_h, bridge, c))

    # Stepped temple arm toward the ear (two descending cells).
    arm_x = far_in - lens_w
    surf.fill(_BLACK, (arm_x - c * 2, cy - top_h, c * 2, c))
    surf.fill(_BLACK, (arm_x - c * 3, cy - top_h + c, c, c))


# ─────────────────────────────────────────────────────────────────────────────
# B · GLINT ROW — variant A's silhouette with a single bright top-glint cell-row
#     on each lens (the classic CRT specular). Reads "shiny black plastic".
# ─────────────────────────────────────────────────────────────────────────────
def draw_shades_glint(surf, cx, cy, eye_w, facing=1):
    f = facing
    c = _cell(eye_w)
    cx, cy = _snap(cx, c), _snap(cy, c)

    lens_w = c * 3
    top_h  = c * 2
    bridge = c * 2
    near_in = cx + f * (bridge // 2)
    far_in  = cx - f * (bridge // 2)

    def lens(inner_x, sign):
        x0 = inner_x if sign > 0 else inner_x - lens_w
        surf.fill(_BLACK, (x0, cy - top_h, lens_w, top_h))
        step = x0 + (0 if sign > 0 else c)
        surf.fill(_BLACK, (step, cy, lens_w - c, c))
        # one bright glint cell, upper-inner — a single quantized specular.
        gx = x0 + (lens_w - c * 2 if sign > 0 else c)
        surf.fill(_GLINT, (gx, cy - top_h, c, c))

    lens(near_in, +1)
    lens(far_in, -1)

    bx = min(near_in, far_in)
    surf.fill(_BLACK, (bx, cy - top_h, bridge, c))

    arm_x = far_in - lens_w
    surf.fill(_BLACK, (arm_x - c * 2, cy - top_h, c * 2, c))
    surf.fill(_BLACK, (arm_x - c * 3, cy - top_h + c, c, c))


# ─────────────────────────────────────────────────────────────────────────────
# C · THUG LIFE (CHOSEN) — beefier proportion: 4-cell lenses, a 3-cell-tall
#     upper row, and a stepped pyramid temple arm. The single white glint cell
#     stays (it survives the 22px downscale where a soft sheen would mush) but
#     it is on the upper-OUTER corner so it doesn't fight the bridge. The fuller
#     block mass covers the eye more confidently in-game and looks unmistakably
#     8-bit on the product shot.
# ─────────────────────────────────────────────────────────────────────────────
def draw_shades(surf, cx, cy, eye_w, facing=1):
    f = facing
    c = _cell(eye_w)
    cx, cy = _snap(cx, c), _snap(cy, c)

    lens_w = c * 3                              # trimmed so the front block clears the beak
    top_h  = c * 3                              # tall block mass
    bot_h  = c                                  # stepped lower row
    bridge = c * 2
    # Seat the unit on the eye but ride it slightly FORWARD so the near block laps
    # the beak base naturally: drop the lift by one cell so the lower row grazes
    # the beak, and shift the whole pair one cell toward the beak (+facing).
    top_y  = cy - top_h + c
    near_in = cx + f * (bridge // 2)
    far_in  = cx - f * (bridge // 2)

    def lens(inner_x, sign):
        x0 = inner_x if sign > 0 else inner_x - lens_w
        # Main block.
        surf.fill(_BLACK, (x0, top_y, lens_w, top_h))
        # Lower row stepped inward one cell on the outer edge — the meme notch.
        step = x0 + (0 if sign > 0 else c)
        surf.fill(_BLACK, (step, top_y + top_h, lens_w - c, bot_h))
        # One bright glint cell on the upper-outer corner.
        gx = x0 + (c if sign > 0 else lens_w - c * 2)
        surf.fill(_GLINT, (gx, top_y, c, c))

    lens(near_in, +1)
    lens(far_in, -1)

    # Thin bridge bar across the very top, connecting the two blocks.
    bx = min(near_in, far_in)
    surf.fill(_BLACK, (bx, top_y, bridge, c))

    # Stepped pyramid temple arm marching back toward the ear (three cells).
    arm_x = far_in - lens_w
    surf.fill(_BLACK, (arm_x - c * 2, top_y, c * 2, c))
    surf.fill(_BLACK, (arm_x - c * 3, top_y + c, c, c))
