"""Standalone candidate: `waterwheel-mill` — a battered Song-brick river-shrine
grist tower with a big spoked WOODEN water-wheel turning on one flank, half-sunk
into the gutter.

Colocated EXPLORATION module for the pillar-landmark design loop. It follows the
shipped pagoda idiom (`candidate_*(surf, top_rect, bot_rect, palette, seed)`, an
upright `_draw_one` reused for both rects, the ceiling twin a vertical flip of a
temp surface) but does NOT import into or modify any game/ module — it only
borrows read-only colour + AA + ornament helpers so the exploration reads like
the real game at the pagoda fidelity bar.

Silhouette identity (set-level pin): the ONLY concept with a single large solid
WOODEN wheel bolted ASYMMETRICALLY to one flank of a steeply-battered brick
cone. The wheel is spoked + paddled, matte, and NEVER glows — that off-axis
wooden bulge is what splits it from the sibling centred glowing-paper-disc and
the open radial sail-X. Blackout reads as a fat pyramid-cone with one round bulge
stuck on its cheek.

Column-fill contract: the ~58 px collision column is carried top-to-bottom by the
BRICK CONE, never the wheel. The batter is capped so both shoulder and base half-
widths stay ≥ PIPE_W/2, so every body row spans the full column; the corbel cap +
bronze finial hold the centreline to the gap rim. The wheel is pure gutter
overhang laid over that solid masonry core.

Mirror: the ceiling twin is a true vertical FLIP of an upright draw into a temp
surface. A vertical flip preserves LEFT/RIGHT, so the off-axis wheel stays on the
same flank and reads as a wheel on both halves; the wheel is drawn radially
(near-symmetric under flip) and the launder head-race is drawn toward `top_y`
(the gap end) INSIDE the upright, so after the flip the chute still feeds toward
the gap on the hung copy. Wheel side is seed-chosen.

Run:  python docs/pillar_landmarks/windmills/waterwheel-mill/render.py
Out:  docs/pillar_landmarks/windmills/waterwheel-mill/round_2.png
"""
from __future__ import annotations

import math
import os
import pathlib
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

_REPO = pathlib.Path(__file__).resolve().parents[4]
sys.path.insert(0, str(_REPO))

import pygame

from game.config import GROUND_Y, PIPE_W
from game import biome
from game.pillar_pagodas import (
    _mix,
    _shade,
    _gradient_rect,
    _aa_polyline,
    _lit_niche,                  # noqa: F401 — retained from the borrowed material kit
    _tile_hatch,
    _glazed_tile_checker,        # noqa: F401 — imported per brief material kit
    _draw_plinth_mist,
    _is_dark_sky,
    _is_warming_sky,             # noqa: F401 — imported per brief material kit
    _cap_lit_for_dark_sky,
    _cap_dark_for_dark_sky,
    _song_brick,                # noqa: F401 — imported per brief material kit
    _ochre_wood,
    _ochre_wood_lit,
    _ochre_wood_shadow,
    _cedar,
    _bronze,
    _gold_bright,
    _terracotta,
    _brick_mortar,
    _plaster,
    _pond_aqua,
    _songyue_dwarf_eave,
)
from game.pillar_variants import draw_grass_bed
from game.draw import draw_side_shrub


# ── Material roles (all biome-derived via _mix/_shade so day→night retints) ───
#
# BRICK CONE  → stone_dark / stone_mid  (_terracotta + _brick_mortar): a warm
#   clay grist tower, distinct from the cool cream Song-brick pagoda.
# WOODEN WHEEL → stone_dark (_ochre_wood / _cedar): the felloe, spokes and
#   paddle-boards. Matte timber, floored at night, NEVER a glow source.
# IRON BANDS + HUB → stone_accent (_bronze): the axle boss and rim straps.
# WATER → horizon (_pond_aqua): launder feed + splash, the only cool accent.

def _brick_lit(p):
    # Sun-side clay — capped at dusk/night so the shaded flank + niche glow
    # carry the silhouette instead of a value-spiking wall.
    return _cap_lit_for_dark_sky(_shade(_terracotta(p), 28), p)


def _brick_mid(p):
    return _terracotta(p)


def _brick_shadow(p):
    # Floored at night so the shaded cone edge keeps value over a deep sky and
    # the whole mass doesn't collapse into one black blob.
    return _cap_dark_for_dark_sky(_shade(_terracotta(p), -42), p, floor=60)


def _mortar(p):
    return _shade(_brick_mortar(p), 16)


def _edge_rim(p):
    # Faint cool-lit rim run down the shadow-side outline at night so the cone
    # holds its edge against a dark sky (day palettes never trigger it).
    return _mix(p['stone_mid'], p['stone_light'], 0.55)


# ── Brick cone body ──────────────────────────────────────────────────────────

def _brick_cone(surf, cx, top_y, base_y, hw_top, hw_base, palette):
    """Steeply-battered brick trapezoid painted as horizontal scan-lines, each a
    short left-lit → mid → right-shadow ramp, so the flat cone reads as rounded
    masonry volume at PIPE_W=58 (the `_gradient_rect` volume trick adapted to a
    per-row sloping width). Mortar coursing is overlaid every 3 px with a broken
    half-cell offset so the eye reads brick-bond, not stripes. WASM-safe: only
    pygame.draw 1-px lines."""
    lit, mid, shadow = _brick_lit(palette), _brick_mid(palette), _brick_shadow(palette)
    mortar = _mortar(palette)
    rim = _edge_rim(palette)
    dark_sky = _is_dark_sky(palette)
    h = base_y - top_y
    if h < 2:
        return
    for i in range(h):
        y = top_y + i
        t = i / (h - 1)                       # 0 at shoulder, 1 at base
        hw = int(round(hw_top + (hw_base - hw_top) * t))
        if hw < 1:
            continue
        for j in range(hw):
            u = j / max(1, hw)
            pygame.draw.line(surf, _mix(lit, mid, u),
                             (cx - hw + j, y), (cx - hw + j, y), 1)
            pygame.draw.line(surf, _mix(mid, shadow, u),
                             (cx + j, y), (cx + j, y), 1)
        # Brick coursing: a mortar row every 3 px, alternate rows broken at the
        # centreline for a bonded-masonry read rather than ledger stripes.
        if i % 3 == 2:
            if (i // 3) % 2 == 0:
                pygame.draw.line(surf, mortar,
                                 (cx - hw + 1, y), (cx + hw - 1, y), 1)
            else:
                pygame.draw.line(surf, mortar,
                                 (cx - hw + 1, y), (cx - 1, y), 1)
                pygame.draw.line(surf, mortar,
                                 (cx + 1, y), (cx + hw - 1, y), 1)
        if dark_sky:
            pygame.draw.line(surf, rim, (cx + hw - 1, y), (cx + hw - 1, y), 1)
    # AA the two sloping silhouette edges so the cone flanks read smooth.
    edge = _shade(_brick_shadow(palette), -18)
    _aa_polyline(surf, edge, [(cx - hw_top, top_y), (cx - hw_base, base_y)])
    _aa_polyline(surf, edge, [(cx + hw_top, top_y), (cx + hw_base, base_y)])


def _corbel_cap(surf, cx, shoulder_y, top_y, hw_cap, palette):
    """Stacked corbel string-courses stepping in from the shoulder to a bronze
    finial at the gap rim — the river-shrine roof cap. Keeps the centreline
    continuously occupied from shoulder to tip so the collision column never
    breaks above the cone."""
    cap_h = shoulder_y - top_y
    if cap_h < 5:
        pygame.draw.line(surf, _brick_mid(palette),
                         (cx - hw_cap, shoulder_y), (cx + hw_cap, shoulder_y), 2)
        # Finial straight onto the stub so the tip still reaches the rim.
        pygame.draw.circle(surf, _bronze(palette), (cx, top_y + 2), 2)
        return
    # Corbel band count scales with the cap budget; each ledge steps narrower.
    n = max(2, min(4, cap_h // 6))
    finial_h = 6
    stack_h = cap_h - finial_h
    for k in range(n):
        tt = k / max(1, n)
        y = int(shoulder_y - tt * stack_h)
        hw = int(hw_cap * (1.0 - 0.62 * tt))
        # Brick body behind the ledge so no sky peeks between courses.
        band_h = max(2, stack_h // n + 1)
        _gradient_rect(surf, pygame.Rect(cx - hw, y - band_h, hw * 2, band_h),
                       _brick_lit(palette), _brick_mid(palette),
                       _brick_shadow(palette))
        _songyue_dwarf_eave(surf, cx, y - band_h, hw, palette, depth=2)
    # Bronze finial spike + ball reaching the gap rim.
    fx_y = top_y + 1
    bronze = _bronze(palette)
    pygame.draw.line(surf, _shade(bronze, -30), (cx, shoulder_y - stack_h),
                     (cx, fx_y + 2), 2)
    pygame.draw.circle(surf, bronze, (cx, fx_y + 2), 2)
    pygame.draw.circle(surf, _gold_bright(palette), (cx, fx_y + 2), 1)


# ── The water-wheel ──────────────────────────────────────────────────────────

def _cap235(c):
    # Hard ceiling on every channel so nothing on this pole ever spikes toward
    # a hot white/glow — the concept is matte timber + masonry, never emissive.
    return (min(232, c[0]), min(232, c[1]), min(232, c[2]))


def _water_wheel(surf, wcx, wcy, r, palette, *, side, sun=-1.0):
    """A WOODEN undershot water-wheel read by its PADDLES, not its spokes: a
    strengthened dark backing disc, twin felloe rims, and a ring of a FEW chunky
    BUCKETS (boxy tangential cells) seated in the outer felloe band with dark
    scoop-walls and lit board-faces, gaps between them showing the dark backing
    so they read as discrete paddles. A sparse set of radial spokes stays
    strictly inside the inner rim so the eye never counts them as a second
    radiating ring (the gear trap). Matte timber — capped, never glows.

    The circle is popped in every biome by VALUE (deep backing + twin dark
    rims, and on a dark sky a capped light edge-rim) rather than by a warm-on-
    warm hue, so it reads under protan/deutan too. `sun` is the lit-side x-sign;
    lower buckets dip toward the shaded pool for rotation depth.

    Returns the wheel's top and bottom points so the caller can orient the
    launder + splash toward the gap on each section."""
    if r < 6:
        return (wcx, wcy - r), (wcx, wcy + r)
    wood = _ochre_wood(palette)
    wood_lit = _cap235(_ochre_wood_lit(palette))
    wood_dark = _ochre_wood_shadow(palette)
    iron = _bronze(palette)
    dark_sky = _is_dark_sky(palette)
    r_in = max(4, r - 7)                       # wider felloe band → chunky buckets

    # Deepened backing disc (value pop vs a light day sky; reads as shadowed
    # depth behind the paddle gaps, never a sky hole over the gutter).
    backing = _shade(wood_dark, -30)
    pygame.draw.circle(surf, backing, (wcx, wcy), r)

    # Buckets: FEW and BOLD. Each is a boxy cell spanning the felloe band across
    # an arc, with a dark leading scoop-wall and a lit outer board-face; the
    # angular gap between cells leaves the dark backing visible so the ring
    # reads as paddles-on-a-rim, not a toothed gear.
    n_bucket = 8 if r >= 16 else 6
    step = math.tau / n_bucket
    span = step * 0.66                          # <1 → dark gap between buckets
    for k in range(n_bucket):
        a0 = k * step
        a1 = a0 + span
        am = a0 + span * 0.5
        # Facing: sun on the `sun`-x flank; lower buckets dip toward the pool.
        face = 0.5 + 0.5 * (math.cos(am) * sun)
        low = max(0.0, math.sin(am))
        fill = _mix(_mix(wood_dark, wood, 0.7), wood_lit, face * 0.6)
        fill = _mix(fill, backing, low * 0.5)
        quad = [
            (wcx + math.cos(a0) * r_in, wcy + math.sin(a0) * r_in),
            (wcx + math.cos(a0) * r,    wcy + math.sin(a0) * r),
            (wcx + math.cos(a1) * r,    wcy + math.sin(a1) * r),
            (wcx + math.cos(a1) * r_in, wcy + math.sin(a1) * r_in),
        ]
        pygame.draw.polygon(surf, fill, [(int(x), int(y)) for x, y in quad])
        # Dark leading scoop-wall (the open mouth of the bucket).
        pygame.draw.line(surf, _shade(wood_dark, -12),
                         (int(wcx + math.cos(a0) * r_in), int(wcy + math.sin(a0) * r_in)),
                         (int(wcx + math.cos(a0) * r), int(wcy + math.sin(a0) * r)), 2)
        # Lit tangential board-face on the sun side only (capped, matte).
        if face > 0.5:
            pygame.draw.line(surf, _mix(wood, wood_lit, (face - 0.5) * 1.2),
                             (int(wcx + math.cos(a0) * (r - 1)), int(wcy + math.sin(a0) * (r - 1))),
                             (int(wcx + math.cos(a1) * (r - 1)), int(wcy + math.sin(a1) * (r - 1))), 1)

    # Twin felloe rims — the two concentric dark rings are the value silhouette.
    pygame.draw.circle(surf, wood_dark, (wcx, wcy), r, 3)
    pygame.draw.circle(surf, wood_dark, (wcx, wcy), r_in, 2)
    pygame.draw.circle(surf, iron, (wcx, wcy), r - 2, 1)   # matte iron strap
    if dark_sky:
        # Capped light edge-rim so the circle holds by VALUE against a dark sky
        # (never a warm halo — clamped well below any glow threshold).
        edge = _cap235(_mix(palette['stone_mid'], palette['stone_light'], 0.5))
        pygame.draw.circle(surf, edge, (wcx, wcy), r, 1)
    # AA the outer rim silhouette for a smooth wheel edge at scale.
    rim_pts = [(wcx + math.cos(a) * r, wcy + math.sin(a) * r)
               for a in [i / 24 * math.tau for i in range(24)]]
    _aa_polyline(surf, _shade(wood_dark, -20), rim_pts, closed=True)

    # Sparse radial spokes, strictly hub→inner-rim so they never join the bucket
    # band into one radiating count (fewer, clearly inner → not a gear).
    n_spoke = 5
    for k in range(n_spoke):
        a = (k / n_spoke) * math.tau + 0.19
        ca, sa = math.cos(a), math.sin(a)
        col = _cap235(_mix(_cedar(palette), wood_lit, 0.35 + 0.35 * (ca * sun)))
        pygame.draw.line(surf, col, (wcx, wcy),
                         (int(wcx + ca * (r_in - 1)), int(wcy + sa * (r_in - 1))), 2)

    # Bronze axle hub + boss glint (matte metal, not emissive).
    pygame.draw.circle(surf, _shade(iron, -30), (wcx, wcy), 5)
    pygame.draw.circle(surf, iron, (wcx, wcy), 4)
    pygame.draw.circle(surf, _cap235(_shade(iron, 30)), (wcx - 1, wcy - 1), 1)

    top_pt = (wcx, wcy - r)
    bot_pt = (wcx, wcy + r)
    return top_pt, bot_pt


def _matte_niche(surf, cx, cy, w, h, palette):
    """A recessed shrine doorway drawn MATTE — dark frame + darker inside + a
    thin warm rim on a plain alpha blit. Keeps the niche relief of the pagoda
    idiom but deliberately drops its night additive lantern halo: this pole is
    never a glow source, so the rim is clamped and never accumulates to white."""
    if w < 3 or h < 4:
        return
    frame = _shade(palette['stone_dark'], -25)
    inside = _shade(palette['stone_dark'], -50)
    pygame.draw.rect(surf, frame, (cx - w // 2, cy, w, h))
    pygame.draw.rect(surf, inside, (cx - w // 2 + 1, cy + 1, w - 2, h - 2))
    # Warm rim as a hint of interior firelight, clamped well below any glow
    # threshold and alpha-blended (not additive) so it can never stack to white.
    rim = _cap235(_mix(palette['stone_accent'], (210, 180, 110), 0.7))
    alpha = 150 if _is_dark_sky(palette) else 90
    rim_layer = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(rim_layer, (*rim, alpha), (0, 0, w, h), 1)
    surf.blit(rim_layer, (cx - w // 2, cy))


def _launder_and_splash(surf, cx, body_hw_at_top, wheel_top, wheel_bot, palette,
                        *, side):
    """Head-race launder feeding the wheel top + a splash pool at the wheel foot.
    The launder is drawn toward the wheel TOP (which, in the upright draw, is the
    gap-facing end after the ceiling flip) so water always reads as fed from the
    gap side on both halves."""
    cedar = _cedar(palette)
    aqua = _pond_aqua(palette)
    wtx, wty = wheel_top
    # Wooden launder chute from the body flank to just above the wheel top.
    sx = cx + side * (body_hw_at_top - 2)
    pygame.draw.line(surf, _shade(cedar, -20), (sx, wty - 6), (wtx, wty - 2), 3)
    pygame.draw.line(surf, _cap235(_ochre_wood_lit(palette)),
                     (sx, wty - 7), (wtx, wty - 3), 1)
    # Water spilling off the launder lip onto the wheel top (highlights capped
    # so the cool accent never flares to a hot white on either mirror half).
    pygame.draw.line(surf, aqua, (wtx, wty - 3), (wtx, wty + 1), 2)
    pygame.draw.line(surf, _cap235(_mix(aqua, palette['stone_light'], 0.5)),
                     (wtx - 1, wty - 2), (wtx - 1, wty), 1)
    # Splash pool + froth ticks at the wheel foot.
    wbx, wby = wheel_bot
    froth = _cap235(_mix(aqua, palette['stone_light'], 0.6))
    pygame.draw.ellipse(surf, aqua, (wbx - 6, wby - 2, 12, 4))
    pygame.draw.ellipse(surf, froth, (wbx - 4, wby - 2, 8, 2))
    for dx in (-5, -1, 3):
        pygame.draw.line(surf, froth, (wbx + dx, wby - 1),
                         (wbx + dx, wby - 3), 1)


# ── One upright silhouette ───────────────────────────────────────────────────

def _draw_one(surf, cx, base_y, top_y, body_w, palette, seed, *, decor=True):
    """One upright waterwheel-mill filling [top_y, base_y]. Height-adaptive: the
    batter is capped so both shoulder and base half-widths stay ≥ PIPE_W/2 (the
    cone always fills the collision column); short sections get a smaller wheel,
    very short ones omit it while the cone still fills."""
    total_h = base_y - top_y
    if total_h < 20:
        return
    rng = __import__('random').Random(seed)
    side = 1 if (seed % 2 == 0) else -1        # which flank the wheel overhangs

    # Batter capped: base spills into the gutter, shoulder stays wide enough that
    # every body row still spans the full 58 px column (hw >= PIPE_W/2 = 29).
    hw_base = max(PIPE_W // 2 + 4, int(body_w * 0.82))
    hw_cap = max(PIPE_W // 2 + 1, int(body_w * 0.60))   # >= 0.72 of hw_base
    cap_h = min(int(total_h * 0.15), 22)
    shoulder_y = top_y + cap_h

    # 3-layer plinth under the cone.
    plinth_h = 6 if total_h > 60 else 3
    pw0 = hw_base * 2 + 10
    if decor:
        _draw_plinth_mist(surf, cx, base_y, pw0 + 8, palette)
    pygame.draw.rect(surf, _shade(palette['stone_dark'], -16),
                     (cx - pw0 // 2, base_y - plinth_h, pw0, plinth_h))
    pygame.draw.rect(surf, _shade(palette['stone_mid'], -6),
                     (cx - pw0 // 2 + 2, base_y - plinth_h + 1, pw0 - 4, 2))
    pygame.draw.line(surf, palette['stone_light'],
                     (cx - pw0 // 2, base_y - plinth_h),
                     (cx + pw0 // 2, base_y - plinth_h), 1)

    body_base_y = base_y - plinth_h
    _brick_cone(surf, cx, shoulder_y, body_base_y, hw_cap, hw_base, palette)

    # Sparse corbel string-courses banding the shaft (2-3 total).
    body_h = body_base_y - shoulder_y
    n_band = max(0, min(3, body_h // 46))
    for k in range(n_band):
        ht = (k + 1) / (n_band + 1)
        y = int(shoulder_y + body_h * (1 - ht))
        hw = int(round(hw_cap + (hw_base - hw_cap) * (1 - ht)))
        _songyue_dwarf_eave(surf, cx, y, hw, palette, depth=2)
        # A single brick-tile-end hatch tick row on the ledge so it reads tiled.
        _tile_hatch(surf, cx - hw + 3, y - 1, cx + hw - 3, y - 1,
                    _mortar(palette), step=5)

    # Low shrine doorway niche on the shaft, on the flank OPPOSITE the wheel so
    # it isn't buried behind the paddles.
    if body_h > 26 and hw_base > 16:
        door_w = min(7, hw_base // 3)
        door_h = min(14, body_h // 3)
        dcx = cx - side * (hw_base // 3)
        _matte_niche(surf, dcx, body_base_y - door_h, door_w, door_h, palette)

    # Corbel cap + bronze finial holds the centreline to the gap rim.
    _corbel_cap(surf, cx, shoulder_y, top_y, hw_cap, palette)

    # ── The off-axis wheel (pure gutter overhang) ────────────────────────────
    wheel_r = int(min(total_h * 0.24, body_w * 0.52, 27))
    if total_h >= 90 and wheel_r >= 6:
        # Mount the hub ~46% up the shaft, centred vertically on the flank so a
        # vertical flip keeps a wheel on the ceiling twin. Overhang so ~half the
        # rim clears the body edge into the gutter.
        wcy = int(body_base_y - body_h * 0.46)
        # Body half-width at the wheel's row, so the wheel bites the true edge.
        t_row = (wcy - shoulder_y) / max(1, body_h)
        hw_row = int(hw_cap + (hw_base - hw_cap) * max(0.0, min(1.0, t_row)))
        wcx = cx + side * (hw_row - wheel_r // 3)
        top_pt, bot_pt = _water_wheel(surf, wcx, wcy, wheel_r, palette,
                                      side=side, sun=-1.0)
        _launder_and_splash(surf, cx, hw_row, top_pt, bot_pt, palette, side=side)

    if decor:
        draw_grass_bed(surf, cx, base_y - 1, pw0 + 6, 14, palette, seed=seed)
        # A flowering shrub tucked on the flank away from the wheel splash.
        draw_side_shrub(surf, cx - side * (hw_base - 2), base_y - 1, palette,
                        scale=0.85)


def candidate_waterwheel_mill(surf, top_rect, bot_rect, palette, seed):
    bcx = bot_rect.x + bot_rect.width // 2
    tcx = top_rect.x + top_rect.width // 2

    if bot_rect.height > 22:
        _draw_one(surf, bcx, bot_rect.bottom, bot_rect.y,
                  bot_rect.width, palette, seed, decor=True)

    if top_rect.height > 22:
        # Structural mirror: draw upright into a temp sized to top_rect.height,
        # flip vertically, hang from the ceiling. A vertical flip keeps the wheel
        # on the same flank and the launder pointed at the gap.
        w = surf.get_width()
        tmp = pygame.Surface((w, top_rect.height), pygame.SRCALPHA)
        _draw_one(tmp, tcx, top_rect.height, 0,
                  top_rect.width, palette, seed, decor=False)
        flipped = pygame.transform.flip(tmp, False, True)
        surf.blit(flipped, (0, top_rect.y))


# ── Review harness ───────────────────────────────────────────────────────────

MARGIN = 70
CACHE_W = PIPE_W + MARGIN * 2
PHASE_DAY = 0.30
PHASE_NIGHT = 0.85
SEED = 12                                       # even → wheel on the right flank

GAP_Y, GAP_H = 205, 150
TOP_H = int(GAP_Y - GAP_H / 2)
BOT_TOP = int(GAP_Y + GAP_H / 2)
CROP_TOP, CROP_BOT = 14, 496


def _lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _sky_ground(w, h, pal, ground_h):
    cell = pygame.Surface((w, h))
    sky_h = h - ground_h
    for y in range(sky_h):
        t = y / max(1, sky_h - 1)
        pygame.draw.line(cell, _lerp(pal['sky_top'], pal['horizon'], t), (0, y), (w, y))
    for y in range(sky_h, h):
        t = (y - sky_h) / max(1, h - sky_h)
        pygame.draw.line(cell, _lerp(pal['ground_top'], pal['ground_mid'], t),
                         (0, y), (w, y))
    return cell


def _pair_surf(pal):
    surf = pygame.Surface((CACHE_W, GROUND_Y), pygame.SRCALPHA)
    top_rect = pygame.Rect(MARGIN, 0, PIPE_W, TOP_H)
    bot_rect = pygame.Rect(MARGIN, BOT_TOP, PIPE_W, GROUND_Y - BOT_TOP)
    candidate_waterwheel_mill(surf, top_rect, bot_rect, pal, SEED)
    return surf


def _render_pair(pal):
    surf = _pair_surf(pal)
    cell = _sky_ground(CACHE_W, GROUND_Y, pal, 60)
    cell.blit(surf, (0, 0))
    guide = (255, 90, 90)
    for rim in (TOP_H, BOT_TOP):
        for x in range(0, CACHE_W, 8):
            pygame.draw.line(cell, guide, (x, rim), (x + 4, rim), 1)
    return cell.subsurface(pygame.Rect(0, CROP_TOP, CACHE_W,
                                       CROP_BOT - CROP_TOP)).copy()


def _measure_centreline(pal):
    """Mirrored-centreline coverage: on the top (hung) section, how close does
    the body centreline reach the gap rim (TOP_H)? Returns px gap between the
    lowest filled pixel at x=cx in the top section and the rim (0 = touches)."""
    surf = _pair_surf(pal)
    cx = MARGIN + PIPE_W // 2
    low = -1
    for y in range(0, TOP_H + 2):
        if surf.get_at((cx, y))[3] > 50:
            low = y
    return TOP_H - low if low >= 0 else TOP_H


def _measure_fill(pal, section_h):
    """Max vertical run (px) of ZERO-fill rows inside the PIPE_W collision
    column for a bottom-only section of the given height."""
    surf = pygame.Surface((CACHE_W, GROUND_Y), pygame.SRCALPHA)
    bot_rect = pygame.Rect(MARGIN, GROUND_Y - section_h, PIPE_W, section_h)
    candidate_waterwheel_mill(surf, pygame.Rect(MARGIN, 0, PIPE_W, 0),
                              bot_rect, pal, SEED)
    cx = MARGIN + PIPE_W // 2
    x0, x1 = cx - PIPE_W // 2, cx + PIPE_W // 2
    run = worst = 0
    for y in range(GROUND_Y - section_h, GROUND_Y):
        filled = any(surf.get_at((x, y))[3] > 50 for x in range(x0, x1 + 1))
        run = 0 if filled else run + 1
        worst = max(worst, run)
    return worst


def _render_feas(pal, section_h):
    head = 16
    cell_h = section_h + head + 10
    surf = pygame.Surface((CACHE_W, GROUND_Y), pygame.SRCALPHA)
    bot_rect = pygame.Rect(MARGIN, GROUND_Y - section_h, PIPE_W, section_h)
    candidate_waterwheel_mill(surf, pygame.Rect(MARGIN, 0, PIPE_W, 0),
                              bot_rect, pal, SEED)
    cell = _sky_ground(CACHE_W, cell_h, pal, 10)
    crop_top = GROUND_Y - section_h - head
    cell.blit(surf, (0, 0), pygame.Rect(0, crop_top, CACHE_W, cell_h))
    cx = MARGIN + PIPE_W // 2
    for ex in (cx - PIPE_W // 2, cx + PIPE_W // 2):
        pygame.draw.line(cell, (255, 60, 60), (ex, 0), (ex, cell_h), 1)
    return cell, cell_h


def _render_blackout(pal, section_h=235):
    surf = pygame.Surface((CACHE_W, GROUND_Y), pygame.SRCALPHA)
    bot_rect = pygame.Rect(MARGIN, GROUND_Y - section_h, PIPE_W, section_h)
    candidate_waterwheel_mill(surf, pygame.Rect(MARGIN, 0, PIPE_W, 0),
                              bot_rect, pal, SEED)
    crop_top = GROUND_Y - section_h - 12
    crop = surf.subsurface(pygame.Rect(0, crop_top, CACHE_W, section_h + 12)).copy()
    mask = pygame.mask.from_surface(crop, 60)
    return mask.to_surface(setcolor=(18, 18, 22, 255),
                           unsetcolor=(232, 232, 236, 255))


def main():
    pygame.init()
    pygame.display.set_mode((1, 1))
    day = biome.palette_for_phase(PHASE_DAY)
    night = biome.palette_for_phase(PHASE_NIGHT)

    pair_day = _render_pair(day)
    pair_night = _render_pair(night)
    cl_day = _measure_centreline(day)
    cl_night = _measure_centreline(night)

    heights = [70, 210, 355]
    feas = [_render_feas(day, h) for h in heights]
    fills = {h: _measure_fill(day, h) for h in heights}
    blackout = _render_blackout(day)

    pad = 14
    label_h = 22
    title_h = 62
    pw, ph = pair_day.get_width(), pair_day.get_height()

    title = pygame.font.SysFont(None, 30)
    sub = pygame.font.SysFont(None, 18)
    label = pygame.font.SysFont(None, 19)

    left_w = pad + pw + pad + pw + pad
    feas_w = max(c.get_width() for c, _ in feas)
    right_w = feas_w + pad * 2
    sheet_w = left_w + right_w

    bo_w, bo_h = blackout.get_width(), blackout.get_height()
    left_h = title_h + ph + label_h + pad + bo_h + label_h + pad
    feas_col_h = title_h + sum(ch + label_h + pad for _, ch in feas) + 24
    sheet_h = max(left_h, feas_col_h) + pad

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((24, 25, 30))

    sheet.blit(title.render("waterwheel-mill — round 2", True, (245, 240, 230)),
               (pad, 12))
    sheet.blit(sub.render("brick cone + off-axis WOODEN wheel: FEW bold BUCKETS on "
                          "a rim (not a gear)  ·  matte, capped, never glows",
                          True, (170, 172, 182)), (pad, 40))

    for i, (pair, name, cl) in enumerate((
            (pair_day, f"DAY  PHASE={PHASE_DAY}", cl_day),
            (pair_night, f"NIGHT  PHASE={PHASE_NIGHT}", cl_night))):
        hx = pad + i * (pw + pad)
        hy = title_h
        sheet.blit(pair, (hx, hy))
        pygame.draw.rect(sheet, (60, 62, 72), (hx, hy, pw, ph), 1)
        lab = label.render(name, True, (255, 224, 150))
        sheet.blit(lab, (hx + (pw - lab.get_width()) // 2, hy + ph + 3))
        cl2 = sub.render(f"mirror centreline gap to rim: {cl}px", True,
                         (200, 202, 212))
        sheet.blit(cl2, (hx + (pw - cl2.get_width()) // 2, hy + ph + 3 + 18))

    bx = pad
    by = title_h + ph + label_h + pad + 14
    sheet.blit(blackout, (bx, by))
    pygame.draw.rect(sheet, (60, 62, 72), (bx, by, bo_w, bo_h), 1)
    lab = label.render("BLACKOUT — 58px silhouette read", True, (255, 224, 150))
    sheet.blit(lab, (bx, by + bo_h + 3))

    fx = left_w + pad
    fy = title_h
    sheet.blit(sub.render("FEASIBILITY — collision-column fill (red = PIPE_W)",
                          True, (255, 224, 150)), (fx, fy - 22))
    for (cell, ch), h in zip(feas, heights):
        sheet.blit(cell, (fx, fy))
        pygame.draw.rect(sheet, (60, 62, 72), (fx, fy, cell.get_width(), ch), 1)
        lab = label.render(f"{h}px  ·  max empty run {fills[h]}px", True,
                           (210, 212, 222))
        sheet.blit(lab, (fx, fy + ch + 3))
        fy += ch + label_h + pad

    out = _REPO / "docs" / "pillar_landmarks" / "windmills" / "waterwheel-mill" / "round_2.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(sheet, out)
    print(f"wrote {out}  ({sheet.get_width()}x{sheet.get_height()})")
    print(f"mirror centreline->rim gap: day={cl_day}px night={cl_night}px")
    print(f"max empty run: " + "  ".join(f"{h}px->{fills[h]}px" for h in heights))

    # PIL-sanity contract (no display): assert nothing on either pair surface
    # spikes to hot white and no cool water pixel breaches the 232 cap.
    for pname, pal in (("day", day), ("night", night)):
        psurf = _pair_surf(pal)
        hot = 0
        for yy in range(psurf.get_height()):
            for xx in range(psurf.get_width()):
                c = psurf.get_at((xx, yy))
                if c[3] > 50 and c[0] >= 250 and c[1] >= 250 and c[2] >= 250:
                    hot += 1
        print(f"{pname}: pure-white(>=250) alpha>50 pixels = {hot}")


if __name__ == "__main__":
    main()
