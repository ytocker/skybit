"""Standalone candidate: `pavilion-mill` — a tiered pagoda-pavilion mill whose
tiled eaves shelter a milling floor, throwing four OPEN matting sails as a thin
radial X across the gap.

Colocated EXPLORATION module for the windmill pillar-landmark design loop. It
follows the shipped pagoda idiom (`candidate_*(surf, top_rect, bot_rect,
palette, seed)`, an upright `_draw_pavilion_one` reused for both rects, the top
section a vertical flip of a temp surface) and imports the REAL
`game/pillar_pagodas.py` + foliage helpers so materials, gradients and palette
retint match the shipped pagodas EXACTLY — but it never imports into or mutates
any game/ runtime module.

Silhouette identity (the set-level pin this concept must protect): a stepped
multi-eave pavilion body crossed by a THIN OPEN four-arm sail cross — a saltire
of narrow canvas jibs with clear air between the arms, radiating past the body
into both gutters. It must never fill into a solid disc (that is #4
`shoji-rose-mill`) nor drop to one side-arm (that is #2 `waterwheel-mill`).

Column-fill contract: the collision column (central PIPE_W band) is carried
top-to-bottom by the pavilion tier stack, and the bronze crown spire + sail hub
hold the centreline continuously up to the gap rim — the sail-X itself is pure
gutter overhang laid over that solid core.

Run:  python docs/pillar_landmarks/windmills/pavilion-mill/render.py
Out:  docs/pillar_landmarks/windmills/pavilion-mill/round_2.png
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

import pygame  # noqa: E402

from game.config import GROUND_Y, PIPE_W  # noqa: E402
from game import biome  # noqa: E402
from game.pillar_pagodas import (  # noqa: E402
    _mix,
    _shade,
    _gradient_rect,
    _aa_polyline,
    _lit_niche,
    _tile_hatch,
    _dougong_cluster,
    _eave_tang_curl,
    _draw_entry_door,
    _draw_plinth_mist,
    _draw_sorin_flame_halo,
    _is_dark_sky,
    _fit_floors,
    _tier_bounds,
    _ochre_wood,
    _ochre_wood_lit,
    _ochre_wood_shadow,
    _white_plaster_warm,
    _plaster,
    _vn_tile_red,
    _tile_gloss,
    _bronze,
    _gold_bright,
    _column_grey,
)
from game.pillar_variants import draw_grass_bed, draw_flower_bed  # noqa: E402
from game.draw import draw_side_shrub  # noqa: E402


# ── Material roles (all biome-derived so day→night retints sweep through) ─────
#
# Body timber → stone_dark (ochre larch triad). Panels → stone_light (warm
# plaster). Glazed eave → a stone_dark/accent tile red. Sail canvas → stone_light
# plaster with its own lit/shadow split. Hub + crown → stone_accent bronze/gilt.

def _canvas_lit(pal):
    # Sun-side matting canvas — a half-stop above the plaster mid so the sunward
    # pair of sails reads brighter than the shaded pair (the X gets depth, not
    # four identical sticks).
    return _shade(_plaster(pal), 20)


def _canvas_shadow(pal):
    return _shade(_plaster(pal), -30)


def _batten(pal):
    # Bamboo batten rib laid across each matting sail — a dark timber tick so the
    # sail reads as a battened Chinese jib, not a blank paper leaf.
    return _shade(_ochre_wood_shadow(pal), -8)


def _spar(pal):
    return _shade(_ochre_wood_shadow(pal), -14)


# ── The sail cross ────────────────────────────────────────────────────────────

def _sail_arm(surf, hx, hy, dirx, diry, length, palette, *, sunward,
              width_scale=1.0):
    """One OPEN sail arm: a dark stock spar carrying a single narrow matting
    canvas jib along one edge, with a lit/shadow split, a few bamboo battens and
    a genuinely DARK perimeter. Deliberately a clean solid leaf (not a lattice of
    whiskers) so four arms read as confident sails at PIPE_W=58 instead of
    aliasing to noise — and narrow enough that clear air stays between the arms so
    the cross never fills toward a disc.

    A lit matting leaf sits near the plaster-white value of the bright horizon, so
    a light-toned outline dissolves against it. The perimeter is instead the dark
    ochre-shadow tone, laid by filling the WHOLE leaf dark and then insetting the
    lit canvas inside it — a uniform dark leech border on every side that never
    leaks the light fill at diagonal steps or acute corners, so each sunward arm
    holds its silhouette against a bright sky in BOTH biomes. `width_scale` trims
    the downward pair so their canvas doesn't muddy the crown eave; the upward
    pair stays full so the X still crowns the pavilion."""
    tx, ty = hx + dirx * length, hy + diry * length
    px, py = -diry, dirx                       # unit perpendicular (leaf side)
    # Narrow jib: the canvas trails on ONE side of the stock and widens outboard
    # like a Chinese junk sail, then relaxes at the tip.
    narrow = max(2, length * 0.10 * width_scale)
    wide = max(3, length * 0.20 * width_scale)
    f0, f1 = 0.16, 0.94
    b0x, b0y = hx + dirx * length * f0, hy + diry * length * f0
    b1x, b1y = hx + dirx * length * f1, hy + diry * length * f1
    leaf = [
        (b0x, b0y),
        (b0x + px * narrow, b0y + py * narrow),
        (b1x + px * wide, b1y + py * wide),
        (b1x, b1y),
    ]
    leaf = [(int(x), int(y)) for (x, y) in leaf]
    canvas = _canvas_lit(palette) if sunward else _canvas_shadow(palette)
    edge = _ochre_wood_shadow(palette)
    # Dark leech border: fill the leaf dark, then lay the lit canvas inset toward
    # the leaf centroid so a dark rim survives on every edge.
    pygame.draw.polygon(surf, edge, leaf)
    _aa_polyline(surf, edge, leaf, closed=True)
    cxg = sum(p[0] for p in leaf) / 4.0
    cyg = sum(p[1] for p in leaf) / 4.0
    inner = []
    for vx, vy in leaf:
        dx, dy = cxg - vx, cyg - vy
        d = math.hypot(dx, dy) or 1.0
        step = min(1.6, d * 0.9)
        inner.append((int(round(vx + dx / d * step)),
                      int(round(vy + dy / d * step))))
    pygame.draw.polygon(surf, canvas, inner)
    # Value split down the canvas: a lighter run near the spar, darker at the
    # trailing leech, so even one leaf reads as a curved matting sail.
    pygame.draw.aaline(surf, _shade(canvas, 16),
                       (int(b0x), int(b0y)), (int(b1x), int(b1y)))
    # A few bamboo battens across the canvas (perpendicular to the stock) — the
    # `_tile_hatch` marks run normal to the spar segment, so passing the spar as
    # the segment lays the battens. Coarse step = 3-4 ribs, never a busy ladder.
    _tile_hatch(surf, int(b0x), int(b0y), int(b1x), int(b1y),
                _batten(palette), step=max(4, int(length * 0.24)))
    # Dark stock spar down the arm centreline, hub → tip.
    pygame.draw.line(surf, _spar(palette),
                     (int(hx), int(hy)), (int(tx), int(ty)), 2)
    pygame.draw.aaline(surf, _shade(_spar(palette), 22),
                       (int(hx), int(hy)), (int(tx), int(ty)))


def _sail_cross(surf, cx, hub_y, arm_len, angle_deg, palette):
    """Four arms fanned as a saltire X. The two sunward (left) arms are painted
    a half-stop brighter than the shaded (right) pair. Drawn AFTER the crown
    spire so the spire peeks up between the upper V; the hub boss is laid last so
    it caps the four arm-roots cleanly. Hub is dead-centred so the vertical flip
    keeps a legible symmetric X on the ceiling half."""
    a = math.radians(angle_deg)
    ca, sa = math.cos(a), math.sin(a)
    # Draw the far (shaded) pair first, then the near (sunward) pair over them so
    # the bright arms read as nearer — gives the flat cross a front/back depth.
    # The two DOWNWARD arms (diry > 0) are trimmed so their canvas doesn't muddy
    # the crown eave below the hub; the upward pair stays full so the X reads as
    # crowning the pavilion, not embedded in it.
    for dirx, diry, sun in ((ca, -sa, False), (ca, sa, False),
                            (-ca, -sa, True), (-ca, sa, True)):
        ws = 0.82 if diry > 0 else 1.0
        _sail_arm(surf, cx, hub_y, dirx, diry, arm_len, palette, sunward=sun,
                  width_scale=ws)
    # Hub boss — patinated bronze canister with a gilt eye + 1-px specular.
    bronze = _bronze(palette)
    pygame.draw.circle(surf, _shade(bronze, -40), (cx, hub_y), 5)
    pygame.draw.circle(surf, bronze, (cx, hub_y), 4)
    pygame.draw.circle(surf, _gold_bright(palette), (cx, hub_y), 2)
    surf.set_at((cx - 1, hub_y - 1),
                _mix(_gold_bright(palette), (255, 255, 240), 0.6))


# ── Crown spire ───────────────────────────────────────────────────────────────

def _crown_spire(surf, cx, base_y, tip_y, palette):
    """A slender bronze spire from the top pavilion ridge up to the gap rim,
    poking between the upper V of the sail-X. Centred, so it carries the
    collision column's centreline continuously to the rim AND survives the flip.
    A night halo gates on dark skies (matches the shipped sōrin idiom)."""
    bronze = _bronze(palette)
    h = base_y - tip_y
    if h < 3:
        pygame.draw.line(surf, bronze, (cx, tip_y), (cx, base_y), 2)
        return
    # Tapered spike — 3 px at the ridge narrowing to a 1-px point at the rim.
    spire = [(cx - 1, base_y), (cx + 2, base_y),
             (cx + 1, tip_y + 2), (cx, tip_y)]
    pygame.draw.polygon(surf, _shade(bronze, -45), spire)
    pygame.draw.line(surf, _shade(bronze, 30), (cx, base_y), (cx, tip_y + 1), 1)
    # Twin sacred rings + jewel — the sōrin-style crown termination.
    for ry in (tip_y + max(4, h // 3), tip_y + max(7, h * 2 // 3)):
        if ry < base_y - 1:
            pygame.draw.line(surf, _gold_bright(palette),
                             (cx - 2, ry), (cx + 2, ry), 1)
    if _is_dark_sky(palette):
        _draw_sorin_flame_halo(surf, cx, tip_y, palette)
    pygame.draw.circle(surf, _gold_bright(palette), (cx, tip_y), 2)
    pygame.draw.circle(surf, _mix(_gold_bright(palette), (255, 255, 235), 0.7),
                       (cx, tip_y - 1), 0)


# ── One upright pavilion mill ─────────────────────────────────────────────────

def _draw_pavilion_one(surf, cx, base_y, top_y, body_w, palette, seed, *,
                       foliage=True):
    """One upright pavilion-mill filling [top_y, base_y]. Height-adaptive: the
    storey COUNT is derived from the available span (fewer tiers when short) so
    floors never squash, while the crown spire + sail hub always hold the
    centreline to the gap rim."""
    import random
    rng = random.Random(seed)
    total_h = base_y - top_y
    if total_h < 18:
        return

    wood = _ochre_wood(palette)
    wood_lit = _ochre_wood_lit(palette)
    tile_red = _vn_tile_red(palette)
    tile_col = _shade(palette['stone_dark'], -10)
    fringe_col = _shade(tile_red, -18)
    accent = _bronze(palette)

    # Sail geometry — sized to the section, capped so the X overhangs the gutters
    # boldly without the vertical reach crossing the gap rim after the flip.
    angle_deg = 42.0
    sa = math.sin(math.radians(angle_deg))
    ca = math.cos(math.radians(angle_deg))
    arm_len = int(min(total_h * 0.40, body_w * 1.15))
    arm_len = max(15, arm_len)
    CLEAR = 7                                   # rim clearance for the upper tips
    # The crown zone reserved at the top of the envelope: spire + hub + the
    # upper arms' full vertical reach INCLUDING the canvas leaf, which extends
    # perpendicular to the stock and so pokes higher than the bare spar tip. hub
    # sits at its base; the spire fills the remaining centreline to the rim.
    _leaf_wide = max(3, arm_len * 0.20)
    _max_up = max(arm_len * sa, 0.94 * arm_len * sa + _leaf_wide * ca)
    crown_h = int(math.ceil(_max_up)) + CLEAR

    # ── Plinth (3-layer stone base) + atmospheric mist + foliage ──────────────
    plinth_h = 8 if total_h > 60 else 4
    plinth_w = int(body_w * 1.24)
    if foliage:
        _draw_plinth_mist(surf, cx, base_y, int(body_w * 2.4), palette)
    pygame.draw.rect(surf, _shade(palette['stone_dark'], -12),
                     (cx - plinth_w // 2, base_y - plinth_h, plinth_w, plinth_h))
    pygame.draw.rect(surf, _column_grey(palette),
                     (cx - plinth_w // 2 + 1, base_y - plinth_h + 1,
                      plinth_w - 2, plinth_h - 2))
    pygame.draw.rect(surf, palette['stone_light'],
                     (cx - plinth_w // 2, base_y - plinth_h, plinth_w, 1))

    # ── Tier stack — wedding-cake pavilion, widest at the base ────────────────
    envelope_bot = base_y - plinth_h
    envelope_top = top_y + crown_h
    avail = envelope_bot - envelope_top
    h_floor = 36 + rng.randint(-3, 3)
    tier_count, _ = _fit_floors(avail, h_floor, min_count=1)
    layout = _tier_bounds(envelope_top, envelope_bot, tier_count, taper=0.07)
    base_tier_w = int(body_w * 1.02)
    body_widths = [max(14, int(base_tier_w * (0.90 ** i)))
                   for i in range(tier_count)]

    for i in range(tier_count):
        wall_top, th = layout[i]
        if th < 4:
            continue
        bw = body_widths[i]
        is_top = (i == tier_count - 1)
        _draw_storey(surf, cx, wall_top, bw, th, palette,
                     tier_index=i, top_tier=is_top)
        # Recessed entry door on the lowest storey only.
        if i == 0 and bw >= 12 and th >= 12:
            _draw_entry_door(surf, cx, wall_top + th - 1, palette,
                             w=2, h=4, open_glow=rng.random() < 0.5)
        # Flared glazed eave over every storey (Chinese curl harder low). The
        # crown storey keeps its flare but pulls it in so the hub sits on a clean
        # ridge and the trimmed downward sails don't collide with a wide eave.
        overhang = 8 if is_top else max(11, 15 - i)
        eave_curl = 0.50 if is_top else (0.75 if i < 2 else 0.60)
        _eave_tang_curl(surf, cx, wall_top - 1, bw // 2, overhang, 6,
                        tile_red, _gold_bright(palette), tile_col,
                        curl=eave_curl, fringe=True, fringe_col=fringe_col,
                        drop_shadow=True, skip_corner_hook=False)

    # ── Crown spire + sail-X ──────────────────────────────────────────────────
    # The hub sits at the top storey's ridge; the spire climbs from there to the
    # gap rim; the upper arm tips stop CLEAR px below the rim.
    # The hub sits at the crown ridge (no lift): the pulled-in crown eave and the
    # trimmed downward sails already read the X as crowning the pavilion, and a
    # lift here would eat the symmetric 10/7 rim clearance.
    top_ridge_y = layout[-1][0] if layout else envelope_top
    hub_y = min(top_ridge_y, top_y + crown_h)
    _crown_spire(surf, cx, hub_y, top_y, palette)
    _sail_cross(surf, cx, hub_y, arm_len, angle_deg, palette)

    # ── Ground dressing ───────────────────────────────────────────────────────
    if foliage:
        shrub_j = rng.randint(-2, 2)
        draw_side_shrub(surf, cx - plinth_w // 2 - 2 + shrub_j,
                        base_y - 2, palette, scale=0.9)
        draw_side_shrub(surf, cx + plinth_w // 2 + 2 - shrub_j,
                        base_y - 2, palette, scale=0.9)
        draw_grass_bed(surf, cx, base_y - 1, plinth_w + 10, 16, palette,
                       seed=seed)
        draw_flower_bed(surf, cx, base_y - 2, plinth_w - 6, 6, seed=seed)


def _draw_storey(surf, cx, wall_top, bw, th, palette, *, tier_index=0,
                 top_tier=False):
    """A single pavilion storey: ochre-wood posts framing warm-plaster panels
    with a 3-stop body gradient, a lit niche, and a dougong bracket row under
    the eave. Higher storeys lift toward the lit ochre for atmospheric recession
    (matches the shipped Fogong storey idiom)."""
    if bw < 12 or th < 6:
        # Too short for framing — still fill the column with a graded stub.
        wood = _ochre_wood(palette)
        _gradient_rect(surf, pygame.Rect(cx - bw // 2, wall_top, bw, max(1, th)),
                       _ochre_wood_lit(palette), wood, _ochre_wood_shadow(palette))
        return
    wood = _ochre_wood(palette)
    wood_lit = _ochre_wood_lit(palette)
    wood_dark = _ochre_wood_shadow(palette)
    plaster = _white_plaster_warm(palette)
    plaster_shadow = _shade(plaster, -22)
    if tier_index > 0:
        wood = _mix(wood, wood_lit, min(0.35, tier_index * 0.05))
    x_l = cx - bw // 2
    _gradient_rect(surf, pygame.Rect(x_l, wall_top, bw, th),
                   wood_lit, wood, wood_dark)

    # Plaster panels between the posts, each a recessed graded plane.
    if bw >= 22 and th >= 9:
        panels = 3
        gap = 2
        zone = bw - 6
        pw = max(3, (zone - (panels - 1) * gap) // panels)
        for i in range(panels):
            px0 = x_l + 3 + i * (pw + gap)
            _gradient_rect(surf, pygame.Rect(px0, wall_top + 2, pw, th - 4),
                           _shade(plaster, 18), plaster, plaster_shadow)
            beam_y = wall_top + th // 2
            pygame.draw.line(surf, wood_dark,
                             (px0, beam_y), (px0 + pw - 1, beam_y), 1)

    # Wood posts — left, right + interior so panels read separated.
    posts = [x_l, x_l + bw - 2]
    if bw >= 22:
        third = bw // 3
        posts += [x_l + third - 1, x_l + 2 * third - 1]
    for px in posts:
        pygame.draw.rect(surf, wood_dark, (px, wall_top, 2, th))
        pygame.draw.line(surf, wood_lit,
                         (px, wall_top), (px, wall_top + th - 1), 1)

    # Architrave beam the dougong sits on.
    pygame.draw.rect(surf, wood_dark, (x_l, wall_top, bw, 2))
    pygame.draw.line(surf, wood_lit,
                     (x_l, wall_top + 1), (x_l + bw - 1, wall_top + 1), 1)

    # One centred lit-rim niche — the warm interior-light beat at night.
    if th > 11 and bw > 12:
        nw = max(3, min(bw - 8, 6))
        nh = max(4, min(th - 7, 6))
        _lit_niche(surf, cx, wall_top + 3, nw, nh, palette)

    # Dougong bracket array under the eave (skip on the crown storey so the hub
    # sits on a clean ridge).
    if not top_tier and bw >= 14:
        for i in range(3):
            t = (i + 0.5) / 3
            _dougong_cluster(surf, x_l + int(t * bw), wall_top + 2, palette,
                             w=8, depth=4)


# ── The candidate entry point ─────────────────────────────────────────────────

def candidate_pavilion_mill(surf, top_rect, bot_rect, palette, seed):
    bcx = bot_rect.x + bot_rect.width // 2
    tcx = top_rect.x + top_rect.width // 2

    if bot_rect.height > 22:
        _draw_pavilion_one(surf, bcx, bot_rect.bottom, bot_rect.y,
                           bot_rect.width, palette, seed, foliage=True)

    if top_rect.height > 22:
        # Structural mirror: draw upright into a temp sized to top_rect.height,
        # flip vertically, blit hanging from the ceiling. The centred sail hub +
        # crown spire point at the gap exactly like the bottom section (a legible
        # X either way up), and the wide pavilion base lands on the ceiling.
        w = surf.get_width()
        tmp = pygame.Surface((w, top_rect.height), pygame.SRCALPHA)
        _draw_pavilion_one(tmp, tcx, top_rect.height, 0,
                           top_rect.width, palette, seed, foliage=False)
        flipped = pygame.transform.flip(tmp, False, True)
        surf.blit(flipped, (0, top_rect.y))


# ── Review harness ────────────────────────────────────────────────────────────

MARGIN = 74
CACHE_W = PIPE_W + MARGIN * 2
PHASE_DAY = 0.30
PHASE_NIGHT = 0.85
SEED = 21

GAP_Y, GAP_H = 205, 150
TOP_H = int(GAP_Y - GAP_H / 2)
BOT_TOP = int(GAP_Y + GAP_H / 2)
CROP_TOP, CROP_BOT = 12, 500


def _lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _sky_ground(w, h, pal, ground_h):
    cell = pygame.Surface((w, h))
    sky_h = h - ground_h
    for y in range(sky_h):
        t = y / max(1, sky_h - 1)
        pygame.draw.line(cell, _lerp(pal['sky_top'], pal['horizon'], t),
                         (0, y), (w, y))
    for y in range(sky_h, h):
        t = (y - sky_h) / max(1, h - sky_h)
        pygame.draw.line(cell, _lerp(pal['ground_top'], pal['ground_mid'], t),
                         (0, y), (w, y))
    return cell


def _pair_surf(pal):
    surf = pygame.Surface((CACHE_W, GROUND_Y), pygame.SRCALPHA)
    top_rect = pygame.Rect(MARGIN, 0, PIPE_W, TOP_H)
    bot_rect = pygame.Rect(MARGIN, BOT_TOP, PIPE_W, GROUND_Y - BOT_TOP)
    candidate_pavilion_mill(surf, top_rect, bot_rect, pal, SEED)
    return surf


def _render_pair(pal):
    surf = _pair_surf(pal)
    cell = _sky_ground(CACHE_W, GROUND_Y, pal, 60)
    cell.blit(surf, (0, 0))
    guide = (255, 90, 90)
    for rim in (TOP_H, BOT_TOP):
        for x in range(0, CACHE_W, 8):
            pygame.draw.line(cell, guide, (x, rim), (x + 4, rim), 1)
    return cell.subsurface(
        pygame.Rect(0, CROP_TOP, CACHE_W, CROP_BOT - CROP_TOP)).copy()


def _measure_clearance(pal):
    surf = _pair_surf(pal)
    cx = MARGIN + PIPE_W // 2
    gutter = lambda x: abs(x - cx) > PIPE_W // 2 + 2
    top_low = -1
    for y in range(0, TOP_H + 8):
        if any(gutter(x) and surf.get_at((x, y))[3] > 50
               for x in range(CACHE_W)):
            top_low = y
    bot_high = GROUND_Y
    for y in range(BOT_TOP - 8, GROUND_Y):
        if any(gutter(x) and surf.get_at((x, y))[3] > 50
               for x in range(CACHE_W)):
            bot_high = y
            break
    return TOP_H - top_low, bot_high - BOT_TOP


def _hsl_l(c):
    # AD's L scale — HSL lightness (max+min)/2, on which the day horizon reads
    # ~221 and a lit matting leaf ~238 (the wash-out gap round 1 had to close).
    return (max(c[0], c[1], c[2]) + min(c[0], c[1], c[2])) / 2


def _measure_sail_edge_dl(pal):
    """Sail-edge-vs-horizon ΔL: the sunward (left) upper arm's silhouette edge
    must hold against the bright horizon in BOTH biomes. Scans the left gutter in
    the sky band just below the lower section's gap rim (where the upper arms
    overhang) for the OUTERMOST opaque arm pixel — the worst / lightest edge pixel
    is reported so a pass is conservative — and compares its lightness to the
    horizon sky. Also samples a lit interior pixel to show the depth split kept."""
    surf = _pair_surf(pal)
    cx = MARGIN + PIPE_W // 2
    hor_l = _hsl_l(pal['horizon'])
    edge_worst = None                          # lightest silhouette edge (worst)
    canvas_l = None                            # a lit interior pixel, for depth
    for y in range(BOT_TOP + 1, BOT_TOP + 48):
        for x in range(0, cx - PIPE_W // 2):
            px = surf.get_at((x, y))
            if px[3] > 60:
                edge_worst = (_hsl_l(px) if edge_worst is None
                              else max(edge_worst, _hsl_l(px)))
                ix = min(cx - PIPE_W // 2 - 1, x + 4)
                ip = surf.get_at((ix, y))
                if ip[3] > 60:
                    canvas_l = (_hsl_l(ip) if canvas_l is None
                                else max(canvas_l, _hsl_l(ip)))
                break
    if edge_worst is None:
        return {'edge': hor_l, 'hor': hor_l, 'dl': 0.0, 'canvas': hor_l}
    return {'edge': edge_worst, 'hor': hor_l, 'dl': abs(hor_l - edge_worst),
            'canvas': canvas_l if canvas_l is not None else edge_worst}


def _measure_fill(pal, section_h):
    surf = pygame.Surface((CACHE_W, GROUND_Y), pygame.SRCALPHA)
    bot_rect = pygame.Rect(MARGIN, GROUND_Y - section_h, PIPE_W, section_h)
    candidate_pavilion_mill(surf, pygame.Rect(MARGIN, 0, PIPE_W, 0),
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
    candidate_pavilion_mill(surf, pygame.Rect(MARGIN, 0, PIPE_W, 0),
                            bot_rect, pal, SEED)
    cell = _sky_ground(CACHE_W, cell_h, pal, 10)
    crop_top = GROUND_Y - section_h - head
    cell.blit(surf, (0, 0), pygame.Rect(0, crop_top, CACHE_W, cell_h))
    cx = MARGIN + PIPE_W // 2
    for ex in (cx - PIPE_W // 2, cx + PIPE_W // 2):
        pygame.draw.line(cell, (255, 60, 60), (ex, 0), (ex, cell_h), 1)
    return cell, cell_h


def _render_blackout(pal, section_h=230):
    surf = pygame.Surface((CACHE_W, GROUND_Y), pygame.SRCALPHA)
    bot_rect = pygame.Rect(MARGIN, GROUND_Y - section_h, PIPE_W, section_h)
    candidate_pavilion_mill(surf, pygame.Rect(MARGIN, 0, PIPE_W, 0),
                            bot_rect, pal, SEED)
    crop_top = GROUND_Y - section_h - 12
    crop = surf.subsurface(
        pygame.Rect(0, crop_top, CACHE_W, section_h + 12)).copy()
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
    cl_day = _measure_clearance(day)
    cl_night = _measure_clearance(night)
    dl_day = _measure_sail_edge_dl(day)
    dl_night = _measure_sail_edge_dl(night)

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

    # Three stacked lines under each pair (name + clearance + edge ΔL), so the
    # blackout drops below all of them.
    pair_labels_h = label_h + 20
    bo_w, bo_h = blackout.get_width(), blackout.get_height()
    left_h = title_h + ph + pair_labels_h + pad + bo_h + label_h + pad
    feas_col_h = title_h + sum(ch + label_h + pad for _, ch in feas) + 24
    sheet_h = max(left_h, feas_col_h) + pad

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((24, 25, 30))

    sheet.blit(title.render("pavilion-mill — round 2", True, (245, 240, 230)),
               (pad, 12))
    sheet.blit(sub.render("dark ochre-shadow sail edge holds vs bright sky  ·  "
                          "trimmed downward pair + pulled-in crown eave",
                          True, (170, 172, 182)), (pad, 40))

    for i, (pair, name, cl, dl) in enumerate((
            (pair_day, f"DAY  PHASE={PHASE_DAY}", cl_day, dl_day),
            (pair_night, f"NIGHT  PHASE={PHASE_NIGHT}", cl_night, dl_night))):
        hx = pad + i * (pw + pad)
        hy = title_h
        sheet.blit(pair, (hx, hy))
        pygame.draw.rect(sheet, (60, 62, 72), (hx, hy, pw, ph), 1)
        lab = label.render(name, True, (255, 224, 150))
        sheet.blit(lab, (hx + (pw - lab.get_width()) // 2, hy + ph + 3))
        cl2 = sub.render(f"upper sail-tip clear: top {cl[0]}px  bot {cl[1]}px",
                         True, (200, 202, 212))
        sheet.blit(cl2, (hx + (pw - cl2.get_width()) // 2, hy + ph + 21))
        ok = (0, 220, 120) if dl['dl'] >= 60 else (255, 120, 120)
        dl3 = sub.render(f"sail-edge vs horizon dL {dl['dl']:.0f}  (edge L"
                         f"{dl['edge']:.0f} / hor L{dl['hor']:.0f})", True, ok)
        sheet.blit(dl3, (hx + (pw - dl3.get_width()) // 2, hy + ph + 37))

    bx = pad
    by = title_h + ph + pair_labels_h + pad + 14
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

    out = _REPO / "docs" / "pillar_landmarks" / "windmills" / \
        "pavilion-mill" / "round_2.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(sheet, out)

    # Prove the day→night body retint: sample the ochre-wood body colour.
    day_body = _ochre_wood(day)
    night_body = _ochre_wood(night)
    day_tile = _vn_tile_red(day)
    night_tile = _vn_tile_red(night)
    print(f"wrote {out}  ({sheet.get_width()}x{sheet.get_height()})")
    print(f"clearance day  top={cl_day[0]}px bot={cl_day[1]}px")
    print(f"clearance night top={cl_night[0]}px bot={cl_night[1]}px")
    print(f"sail-edge dL day   edge L{dl_day['edge']:.0f} hor L{dl_day['hor']:.0f}"
          f" -> dL {dl_day['dl']:.0f}  (canvas L{dl_day['canvas']:.0f})")
    print(f"sail-edge dL night edge L{dl_night['edge']:.0f} "
          f"hor L{dl_night['hor']:.0f} -> dL {dl_night['dl']:.0f}  "
          f"(canvas L{dl_night['canvas']:.0f})")
    print("max empty run: " + "  ".join(f"{h}px->{fills[h]}px" for h in heights))
    print(f"body ochre  day={day_body} night={night_body} "
          f"(differ={day_body != night_body})")
    print(f"eave tile   day={day_tile} night={night_tile} "
          f"(differ={day_tile != night_tile})")


if __name__ == "__main__":
    main()
