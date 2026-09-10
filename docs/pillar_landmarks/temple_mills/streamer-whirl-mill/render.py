"""Standalone candidate: `streamer-whirl-mill` — a little brick mini-pavilion
temple whose rooftop mast flings a WHIRL of fluttering prayer-streamer ribbons,
spun outward from a central bronze boss on the wind.

Colocated EXPLORATION module for the pillar-landmark design loop. It reuses the
shipped pagoda idiom (`candidate_*(surf, top_rect, bot_rect, palette, seed)`, an
upright `_draw_one` reused for both rects, the ceiling twin a vertical flip of a
temp surface) and borrows the brick-temple material kit + masonry helpers from
`game.pillar_pagodas` READ-ONLY, so the exploration reads at the pagoda fidelity
bar without importing into or mutating any game/ module.

Distinctness pin (TEMPLE-MILL family): this is the SOFT / colour / MOTION pole.
Its crown is neither the rigid gilt star, the flat canvas fan, the figural
phoenix, nor the smooth parasol dome — it is an airy SPRAY of tapering cloth
ribbons radiating and curling from a hub, the only actively-fluttering crown in
the set. The mechanism reads as a wind-spun whorl (ribbons flung out + curled
tangentially), never static festival bunting.

Column-fill contract: the ~58 px collision column is carried top-to-bottom by
the BRICK mass — a battered base, the pavilion room, its tiled roof, and above
the roof a bronze mast + finial that hold the centreline to the gap rim. The
streamers are pure crown/gutter overhang laid over that solid masonry core; the
pavilion box + mast must read on their own so the crown never vanishes when the
ribbons thin.

Mirror: the ceiling twin is a true vertical FLIP of an upright draw into a temp
surface. A vertical flip preserves LEFT/RIGHT, so the whirl is laid BALANCED
about the vertical axis (mirrored ribbon pairs, no ribbon straddling the axis)
and reads as a symmetric whorl on both halves. The boss is seated well BELOW the
finial so no ribbon's upward reach comes within 5 px of the gap rim — the soft
cloth never bridges the flyable gap; only the rigid finial touches the rim.

Run:  python docs/pillar_landmarks/temple_mills/streamer-whirl-mill/render.py
Out:  docs/pillar_landmarks/temple_mills/streamer-whirl-mill/round_2.png
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
    _lit_niche,
    _tile_hatch,
    _glazed_tile_checker,        # noqa: F401 — imported per brief material kit
    _draw_plinth_mist,
    _is_dark_sky,
    _is_warming_sky,              # noqa: F401 — imported per brief material kit
    _cap_lit_for_dark_sky,
    _cap_dark_for_dark_sky,
    _terracotta,
    _porcelain_aqua,
    _song_brick,                 # noqa: F401 — imported per brief material kit
    _bronze,
    _gold_bright,
    _vermilion,
    _vermilion_lit,
    _vermilion_shadow,
    _vn_tile_red,
    _brick_mortar,
    _songyue_dwarf_eave,
)
from game.pillar_variants import draw_grass_bed
from game.draw import draw_side_shrub


# ── Material roles (all biome-derived via _mix/_shade so day→night retints) ───
#
# BRICK BASE + PAVILION ROOM → stone_dark / stone_mid (_terracotta): a warm clay
#   shrine mass, the solid silhouette anchor under the soft crown.
# TILED ROOF → stone_dark accent (_vn_tile_red): the pitched pavilion eave,
#   overlaid with tile coursing + a corbel eave-lip.
# MAST + BOSS + FINIAL → stone_accent (_bronze / _gold_bright): the metal spine
#   that carries the centreline to the rim and spins the ribbons; the ONLY night
#   glow source (gated on a dark sky).
# STREAMERS → three warm/cool cloth hues (_vermilion warm, a true teal-jade
#   cool, _gold_bright): matte fluttering cloth, capped so ribbons never flare hot.

def _cap235(c):
    # Cloth + metal on this concept stay matte — a hard channel ceiling keeps any
    # highlight well below the hot-white glow threshold the family forbids.
    return (min(235, c[0]), min(235, c[1]), min(235, c[2]))


def _brick_lit(p):
    return _cap_lit_for_dark_sky(_shade(_terracotta(p), 26), p)


def _brick_mid(p):
    return _terracotta(p)


def _brick_shadow(p):
    return _cap_dark_for_dark_sky(_shade(_terracotta(p), -42), p, floor=58)


def _mortar(p):
    return _shade(_brick_mortar(p), 14)


def _edge_rim(p):
    # Faint cool-lit rim on the shadow-side outline so the brick holds its edge
    # against a dark sky (day palettes never trigger it via the caller's gate).
    return _mix(p['stone_mid'], p['stone_light'], 0.55)


def _streamer_cool(p):
    # A TRUE teal-jade cloth so the whirl carries a genuine warm/cool beat
    # (vermilion + gold + this) in BOTH biomes. Keyed off _porcelain_aqua (a
    # stone_light-derived jade that biome-retints) but pulled hard toward a
    # saturated cyan target so it never washes to warm-grey under a DAY sky —
    # the round-1 horizon key collapsed to grey-green because DAY horizon is warm.
    return _mix(_porcelain_aqua(p), (30, 140, 152), 0.64)


# ── Streamer cloth ────────────────────────────────────────────────────────────

def _streamer(surf, hx, hy, up_deg, length, w0, w1, palette,
              core, lit, shadow, *, curl, ripple, y_min, kink=0.0, steps=13):
    """One tapering prayer-streamer ribbon spun off the hub.

    `up_deg` is measured from straight UP (0 = up, positive sweeps toward the
    +x/right flank). The ribbon walks outward from the hub while its heading
    slowly turns by `curl` per step (a tangential whorl — the "spun from a hub"
    read) with an optional `ripple` flutter. Each short segment is filled by how
    its face turns toward the light, so the cloth shows a lit crest / shaded
    curl-back TWIST rather than a flat painted stripe; a bright saturated core
    line and AA edges keep it reading as a bold ribbon at PIPE_W = 58. Matte —
    every tone capped, never a glow source."""
    if length < 4 or steps < 2:
        return
    # Light from the upper-left (value-based so it reads under any biome/CVD).
    lx, ly = -0.70, -0.72
    ang = math.radians(up_deg - 90.0)            # 0-up → -90° in screen math
    seg = length / steps
    px, py = float(hx), float(hy)
    path = [(px, py)]
    for i in range(steps):
        t = (i + 1) / steps
        ang += curl
        if ripple:
            ang += ripple * math.sin(t * math.pi * 2.2)
        # A single sharp elbow near mid-length — a taut ribbon suddenly kinked
        # by a gust, so staggered pairs read caught mid-spin, not a clean rosette.
        if kink and i == int(steps * 0.55):
            ang += kink
        px += math.cos(ang) * seg
        py += math.sin(ang) * seg
        # Hard apex clamp: the cloth may never climb past `y_min`, so no ribbon
        # ever reaches within the mirror clearance budget of the gap rim.
        path.append((px, max(py, y_min)))

    n = len(path)
    # Per-point widths (taper) and averaged normals for smooth edges.
    def width_at(i):
        t = i / (n - 1)
        return w0 + (w1 - w0) * t

    norms = []
    for i in range(n):
        if i == 0:
            dx, dy = path[1][0] - path[0][0], path[1][1] - path[0][1]
        elif i == n - 1:
            dx, dy = path[-1][0] - path[-2][0], path[-1][1] - path[-2][1]
        else:
            dx = path[i + 1][0] - path[i - 1][0]
            dy = path[i + 1][1] - path[i - 1][1]
        dl = math.hypot(dx, dy) or 1.0
        norms.append((-dy / dl, dx / dl))

    # Segment quads, shaded by facing so the cloth twists lit↔shadow.
    for i in range(n - 1):
        (x0, y0), (x1, y1) = path[i], path[i + 1]
        (nx0, ny0), (nx1, ny1) = norms[i], norms[i + 1]
        wa, wb = width_at(i) * 0.5, width_at(i + 1) * 0.5
        face = max(-1.0, min(1.0, (nx0 + nx1) * 0.5 * lx + (ny0 + ny1) * 0.5 * ly))
        f = 0.5 + 0.5 * face
        col = _cap235(_mix(_mix(shadow, lit, f), core, 0.30))
        quad = [(x0 + nx0 * wa, y0 + ny0 * wa),
                (x1 + nx1 * wb, y1 + ny1 * wb),
                (x1 - nx1 * wb, y1 - ny1 * wb),
                (x0 - nx0 * wa, y0 - ny0 * wa)]
        pygame.draw.polygon(surf, col, [(int(round(x)), int(round(y)))
                                        for x, y in quad])

    # AA cloth edges: lit crest edge one side, shadow-fold edge the other.
    left = [(path[i][0] + norms[i][0] * width_at(i) * 0.5,
             path[i][1] + norms[i][1] * width_at(i) * 0.5) for i in range(n)]
    right = [(path[i][0] - norms[i][0] * width_at(i) * 0.5,
              path[i][1] - norms[i][1] * width_at(i) * 0.5) for i in range(n)]
    # The crest is whichever edge faces the light on average (curl sign).
    lit_edge, dark_edge = (left, right) if curl <= 0 else (right, left)
    _aa_polyline(surf, _cap235(lit), lit_edge)
    _aa_polyline(surf, shadow, dark_edge)
    # Saturated core stripe — the high-contrast ribbon spine. The taper runs to
    # w1 on its own; no stray tip dot, so a thinning tail never leaves a 1-px
    # speck of noise floating in the gutter sky.
    _aa_polyline(surf, _cap235(_shade(core, 16)), path)


def _whirl(surf, cx, boss_y, whirl_r, n_pairs, palette, *, y_limit):
    """The balanced ribbon whorl + its bronze hub. `n_pairs` mirrored L/R ribbon
    pairs radiate from the boss on the up-out / side / down-out arcs — the
    straight-up cone is left to the mast, so no ribbon reaches toward the gap.
    `y_limit` is the highest screen-y any cloth pixel may occupy (below the gap
    rim by the mirror clearance budget); each ribbon's apex is hard-clamped to
    it so the whirl can never bridge the flyable gap."""
    # Per-pair whorl spec: (heading°-off-up, ripple, curl, len_scale, w0, kink).
    # Headings stay ≥50° off-up so the top cone (toward the gap) is cloth-free.
    # The SIDE pair is the long "leader" flung near-horizontal into the gutter;
    # the UPPER pair is held short so its apex keeps the ~17 px rim clearance;
    # the DOWN pair sweeps toward the roof. Curl grows down the list and lengths
    # stagger so the tips land at different radii — real sky-gaps between tails,
    # not one contiguous clump. Some taut, one kinked mid-length → caught spinning.
    full = [(95.0, 0.06, 0.040, 1.55, 6.8, 0.42),    # side — longest leader, kinked
            (52.0, 0.00, 0.110, 0.72, 5.6, 0.00),    # upper-out — taut, rim-safe
            (140.0, 0.05, 0.150, 1.02, 6.2, 0.00)]   # down-out — deepest curl
    specs = {1: [full[0]], 2: [full[0], full[1]]}.get(n_pairs, full)
    cores = [(_streamer_cool(palette),                # leader wears the TRUE cool
              _mix(_streamer_cool(palette), (214, 240, 236), 0.5),
              _shade(_streamer_cool(palette), -46)),
             (_vermilion(palette), _vermilion_lit(palette), _vermilion_shadow(palette)),
             (_gold_bright(palette),
              _mix(_gold_bright(palette), (255, 244, 190), 0.45),
              _shade(_gold_bright(palette), -58))]

    for k, (up, ripple, curl, lscale, w0, kink) in enumerate(specs):
        core, lit, shadow = cores[k % len(cores)]
        base = w0 if whirl_r >= 24 else w0 * 0.72
        w1 = 1.5
        length = whirl_r * lscale
        # The apex clamp sits a half-width above `y_limit` so even the cloth's
        # upper edge stays clear of the rim budget.
        y_min = y_limit + base * 0.5 + 1
        # Right ribbon curls one way, its mirror the other → balanced whorl,
        # but the kink stays same-signed per side so the pair reads as one gust.
        _streamer(surf, cx, boss_y, up, length, base, w1, palette,
                  core, lit, shadow, curl=curl, ripple=ripple, kink=kink, y_min=y_min)
        # Every angular perturbation (curl, ripple, kink) negates on the mirror so
        # the pair stays a true L/R reflection — a balanced whorl, not a lopsided one.
        _streamer(surf, cx, boss_y, -up, length, base, w1, palette,
                  core, lit, shadow, curl=-curl, ripple=-ripple, kink=-kink, y_min=y_min)

    # Bronze hub boss — the spin centre; the sole gated night-glow source. Built
    # as a normal-alpha radial bloom (NOT additive): additive overlap summed the
    # warm rings up to a hot-white core, so the halo is composited with alpha and
    # every ring pre-capped warm-bronze — a soft glow that never blooms to white.
    bronze = _bronze(palette)
    if _is_dark_sky(palette):
        r_glow = 12
        sz = r_glow * 2 + 2
        glow = pygame.Surface((sz, sz), pygame.SRCALPHA)
        halo = _cap235(_mix(bronze, (214, 156, 92), 0.62))   # warm bronze, sub-white
        core_halo = _cap235(_mix(bronze, (228, 176, 110), 0.7))
        for rr, a in ((r_glow, 34), (r_glow - 3, 52), (r_glow - 6, 70), (r_glow - 9, 86)):
            col = halo if rr > r_glow - 6 else core_halo
            pygame.draw.circle(glow, (*col, a), (sz // 2, sz // 2), max(1, rr))
        surf.blit(glow, (cx - sz // 2, boss_y - sz // 2))
    br = 5 if whirl_r >= 20 else 4
    pygame.draw.circle(surf, _shade(bronze, -34), (cx, boss_y), br)
    pygame.draw.circle(surf, bronze, (cx, boss_y), br - 1)
    pygame.draw.circle(surf, _cap235(_gold_bright(palette)), (cx, boss_y), max(1, br - 3))


# ── Pavilion roof + body ──────────────────────────────────────────────────────

def _pavilion_roof(surf, cx, ridge_y, eave_y, hw_eave, palette):
    """A short pitched tiled pavilion roof: a concave temple sweep from a narrow
    ridge down to a flared eave, painted as tile-red scan-lines with coursing +
    a corbel eave-lip and upturned corners so it reads as a shrine roof, not a
    plain triangle."""
    h = eave_y - ridge_y
    if h < 3:
        return
    tile = _vn_tile_red(palette)
    lit = _cap_lit_for_dark_sky(_shade(tile, 30), palette)
    shadow = _cap_dark_for_dark_sky(_shade(tile, -46), palette, floor=52)
    ridge_hw = max(3, hw_eave // 4)
    course = _shade(tile, -30)
    for i in range(h):
        y = ridge_y + i
        t = i / max(1, h - 1)
        hw = int(round(ridge_hw + (hw_eave - ridge_hw) * (t ** 1.45)))
        if hw < 1:
            continue
        for j in range(hw):
            u = j / max(1, hw)
            pygame.draw.line(surf, _mix(lit, tile, u), (cx - hw + j, y), (cx - hw + j, y), 1)
            pygame.draw.line(surf, _mix(tile, shadow, u), (cx + j, y), (cx + j, y), 1)
        # Tile coursing every 3 px reads as stacked pantiles down the pitch.
        if i % 3 == 2:
            pygame.draw.line(surf, course, (cx - hw + 1, y), (cx + hw - 1, y), 1)
    # AA the two sweeping roof edges.
    edge = _shade(shadow, -14)
    _aa_polyline(surf, edge, [(cx - ridge_hw, ridge_y), (cx - hw_eave, eave_y)])
    _aa_polyline(surf, edge, [(cx + ridge_hw, ridge_y), (cx + hw_eave, eave_y)])
    # Tile-end hatch along the eave + a corbel lip with upturned corners.
    _tile_hatch(surf, cx - hw_eave + 2, eave_y - 1, cx + hw_eave - 2, eave_y - 1,
                _mortar(palette), step=4)
    _songyue_dwarf_eave(surf, cx, eave_y, hw_eave, palette, depth=2)
    up = _cap235(_mix(palette['stone_accent'], (240, 200, 120), 0.6))
    for sx in (cx - hw_eave, cx + hw_eave):
        pygame.draw.line(surf, up, (sx, eave_y + 1), (sx, eave_y - 3), 2)
    # Vermilion ridge cap tying the roof to the streamer colour story.
    pygame.draw.line(surf, _vermilion(palette),
                     (cx - ridge_hw, ridge_y + 1), (cx + ridge_hw, ridge_y + 1), 2)


def _brick_column(surf, cx, top_y, base_y, hw_top, hw_base, palette):
    """Battered brick trapezoid as horizontal scan-lines (a left-lit→mid→
    right-shadow ramp per row) with broken mortar coursing, so the flat body
    reads as rounded masonry volume at PIPE_W = 58. WASM-safe 1-px lines only."""
    lit, mid, shadow = _brick_lit(palette), _brick_mid(palette), _brick_shadow(palette)
    mortar = _mortar(palette)
    rim = _edge_rim(palette)
    dark_sky = _is_dark_sky(palette)
    h = base_y - top_y
    if h < 2:
        return
    hw = hw_top
    for i in range(h):
        y = top_y + i
        t = i / (h - 1)
        hw = int(round(hw_top + (hw_base - hw_top) * t))
        if hw < 1:
            continue
        for j in range(hw):
            u = j / max(1, hw)
            pygame.draw.line(surf, _mix(lit, mid, u), (cx - hw + j, y), (cx - hw + j, y), 1)
            pygame.draw.line(surf, _mix(mid, shadow, u), (cx + j, y), (cx + j, y), 1)
        if i % 3 == 2:
            if (i // 3) % 2 == 0:
                pygame.draw.line(surf, mortar, (cx - hw + 1, y), (cx + hw - 1, y), 1)
            else:
                pygame.draw.line(surf, mortar, (cx - hw + 1, y), (cx - 1, y), 1)
                pygame.draw.line(surf, mortar, (cx + 1, y), (cx + hw - 1, y), 1)
        if dark_sky:
            pygame.draw.line(surf, rim, (cx + hw - 1, y), (cx + hw - 1, y), 1)
    edge = _shade(_brick_shadow(palette), -18)
    _aa_polyline(surf, edge, [(cx - hw_top, top_y), (cx - hw_base, base_y)])
    _aa_polyline(surf, edge, [(cx + hw_top, top_y), (cx + hw_base, base_y)])


def _pavilion_room(surf, cx, top_y, bot_y, hw, palette):
    """The square brick shrine room — a gradient brick box with corner pilasters,
    a mortar course band, and a lit shrine-niche door that lanterns at night."""
    if bot_y - top_y < 6:
        return
    _gradient_rect(surf, pygame.Rect(cx - hw, top_y, hw * 2, bot_y - top_y),
                   _brick_lit(palette), _brick_mid(palette), _brick_shadow(palette))
    # Corner pilasters — a darker vertical strap at each edge for relief.
    strap = _shade(_brick_shadow(palette), -10)
    for sx in (cx - hw, cx + hw - 2):
        pygame.draw.rect(surf, strap, (sx, top_y, 2, bot_y - top_y))
    # A single mortar string-course across the wall.
    my = top_y + (bot_y - top_y) // 2
    _tile_hatch(surf, cx - hw + 3, my, cx + hw - 3, my, _mortar(palette), step=5)
    # Shrine door niche (warm interior light at night via _lit_niche).
    door_w = min(11, hw)
    door_h = min(16, (bot_y - top_y) - 4)
    if door_w >= 5 and door_h >= 8:
        _lit_niche(surf, cx, bot_y - door_h - 1, door_w, door_h, palette)


# ── One upright silhouette ───────────────────────────────────────────────────

def _draw_one(surf, cx, base_y, top_y, body_w, palette, seed, *, decor=True):
    """One upright streamer-whirl-mill filling [top_y, base_y]. Height-adaptive:
    the brick mass (base + room + roof) always fills the collision column while
    the mast carries the centreline to the gap rim; short sections get a smaller
    pavilion and fewer/shorter streamers, very short ones drop the whirl to a
    finial pennant while the body still fills."""
    total_h = base_y - top_y
    if total_h < 20:
        return

    # Vertical budget. The crown (mast + whirl above the roof ridge) is a bounded
    # share so the pavilion + base dominate the column; the rest is brick mass.
    plinth_h = 6 if total_h > 60 else 3
    crown_h = max(16, min(int(total_h * 0.30), 74))
    roof_h = max(9, min(int(total_h * 0.11), 20))
    room_h = max(15, min(int(total_h * 0.17), 34))
    base_h = total_h - plinth_h - crown_h - roof_h - room_h
    if base_h < 8:                                # very short → borrow from crown
        crown_h = max(12, crown_h + base_h - 8)
        base_h = 8

    # Half-widths: base fills ≥ PIPE_W/2 top-to-bottom; room a touch narrower;
    # eave overhangs into the gutter. Kept modest so the plinth doesn't bloat.
    hw_base = max(PIPE_W // 2 + 2, int(body_w * 0.53))     # ≥ 31
    hw_room = max(PIPE_W // 2 - 1, hw_base - 4)            # ≥ 28
    hw_eave = hw_room + 6

    # Y stations (top_y = finial tip / gap rim end).
    boss_y = top_y + max(14, int(crown_h * 0.58))
    ridge_y = top_y + crown_h
    eave_y = ridge_y + roof_h
    room_top = eave_y
    room_bot = room_top + room_h
    base_top = room_bot
    base_bot = base_y - plinth_h

    # 3-layer plinth + backlight mist.
    pw0 = hw_base * 2 + 8
    if decor:
        _draw_plinth_mist(surf, cx, base_y, pw0 + 8, palette)
    pygame.draw.rect(surf, _shade(palette['stone_dark'], -16),
                     (cx - pw0 // 2, base_y - plinth_h, pw0, plinth_h))
    pygame.draw.rect(surf, _shade(palette['stone_mid'], -6),
                     (cx - pw0 // 2 + 2, base_y - plinth_h + 1, pw0 - 4, 2))
    pygame.draw.line(surf, palette['stone_light'],
                     (cx - pw0 // 2, base_y - plinth_h),
                     (cx + pw0 // 2, base_y - plinth_h), 1)

    # Brick base (slight batter) → carries the lower collision column.
    _brick_column(surf, cx, base_top, base_bot, hw_room, hw_base, palette)
    # Sparse corbel string-courses banding the base.
    band_h = base_bot - base_top
    for k in range(max(0, min(2, band_h // 44))):
        ht = (k + 1) / (min(2, band_h // 44) + 1)
        y = int(base_top + band_h * (1 - ht))
        hw = int(round(hw_room + (hw_base - hw_room) * (1 - ht)))
        _songyue_dwarf_eave(surf, cx, y, hw, palette, depth=2)

    # Pavilion room + its pitched tiled roof.
    _pavilion_room(surf, cx, room_top, room_bot, hw_room, palette)
    _pavilion_roof(surf, cx, ridge_y, eave_y, hw_eave, palette)

    # Bronze mast from the roof ridge up to the finial at the gap rim — the
    # rigid spine that holds the centreline (never the soft cloth).
    bronze = _bronze(palette)
    # The finial crowns a few px below the rim (not fused to it) so a sliver of
    # air separates the rigid tip from the gap edge — a cleaner read than round 1.
    finial_y = top_y + 4
    pygame.draw.line(surf, _shade(bronze, -30), (cx, ridge_y), (cx, finial_y), 3)
    pygame.draw.line(surf, bronze, (cx, ridge_y), (cx, finial_y), 1)
    for cy in (int(ridge_y - roof_h * 0.4), boss_y + 6):        # collar rings
        if finial_y + 1 < cy < ridge_y:
            pygame.draw.line(surf, _cap235(_gold_bright(palette)),
                             (cx - 2, cy), (cx + 2, cy), 1)
    # Finial: bronze ball + a tiny vermilion pennant near the rim.
    pygame.draw.circle(surf, bronze, (cx, finial_y), 2)
    pygame.draw.circle(surf, _cap235(_gold_bright(palette)), (cx, finial_y), 1)
    # A tiny vermilion masthead pennant, kept inside the ±4 px centreline band so
    # it reads as a rigid finial flag, not a gap-bridging streamer.
    pygame.draw.polygon(surf, _vermilion(palette),
                        [(cx + 1, finial_y + 1), (cx + 4, finial_y + 2), (cx + 1, finial_y + 4)])

    # The whirl (crown/gutter overhang) — fewer/shorter ribbons when short.
    if crown_h >= 30:
        n_pairs = 3 if total_h >= 150 else 2
    else:
        n_pairs = 1
    whirl_r = int(min(crown_h * 0.80, hw_base + 26, 46))
    y_limit = top_y + 6                            # cloth may not climb past here
    if whirl_r >= 6 and boss_y - y_limit >= 4:
        _whirl(surf, cx, boss_y, whirl_r, n_pairs, palette, y_limit=y_limit)

    if decor:
        draw_grass_bed(surf, cx, base_y - 1, pw0 + 6, 14, palette, seed=seed)
        draw_side_shrub(surf, cx - (hw_base - 1), base_y - 1, palette, scale=0.85)
        draw_side_shrub(surf, cx + (hw_base - 1), base_y - 1, palette, scale=0.7)

    # The shipped lit-niche paints a warm ADDITIVE lantern halo at night that can
    # push already-warm brick to a clinical pure white where it overlaps. This
    # family forbids hot-white at night, so clamp any fully-blown pixel down to a
    # warm parchment — keeps the lantern reading warm without a white-hot spike.
    if _is_dark_sky(palette):
        x0 = max(0, cx - hw_base - 24)
        x1 = min(surf.get_width(), cx + hw_base + 25)
        y0 = max(0, top_y)
        y1 = min(surf.get_height(), base_y)
        for y in range(y0, y1):
            for x in range(x0, x1):
                c = surf.get_at((x, y))
                if c[3] > 0 and c[0] >= 250 and c[1] >= 250 and c[2] >= 250:
                    surf.set_at((x, y), (247, 236, 210, c[3]))


def candidate_streamer_whirl_mill(surf, top_rect, bot_rect, palette, seed):
    bcx = bot_rect.x + bot_rect.width // 2
    tcx = top_rect.x + top_rect.width // 2

    if bot_rect.height > 22:
        _draw_one(surf, bcx, bot_rect.bottom, bot_rect.y,
                  bot_rect.width, palette, seed, decor=True)

    if top_rect.height > 22:
        # Structural mirror: draw upright into a temp sized to top_rect.height,
        # flip vertically, hang from the ceiling. A vertical flip keeps the whirl
        # balanced L/R and keeps the finial (not the cloth) at the gap rim.
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
SEED = 7

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
    candidate_streamer_whirl_mill(surf, top_rect, bot_rect, pal, SEED)
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
    """On the top (hung) section, how close does the body centreline reach the
    gap rim (TOP_H)? Returns px gap between the lowest filled pixel at x=cx and
    the rim (0 = the finial touches)."""
    surf = _pair_surf(pal)
    cx = MARGIN + PIPE_W // 2
    low = -1
    for y in range(0, TOP_H + 2):
        if surf.get_at((cx, y))[3] > 50:
            low = y
    return TOP_H - low if low >= 0 else TOP_H


def _measure_ribbon_clearance(pal):
    """On the top (hung) section, how close does the nearest OFF-CENTRE cloth
    (|x-cx| > 4, i.e. a streamer, not the mast) come to the gap rim? Must stay
    ≥ 5 px so the whirl never bridges the flyable gap."""
    surf = _pair_surf(pal)
    cx = MARGIN + PIPE_W // 2
    low = -1
    for y in range(0, TOP_H + 2):
        for x in range(0, CACHE_W):
            if abs(x - cx) > 4 and surf.get_at((x, y))[3] > 50:
                low = max(low, y)
                break
    return TOP_H - low if low >= 0 else TOP_H


def _measure_fill(pal, section_h):
    """Max vertical run (px) of ZERO-fill rows inside the PIPE_W collision
    column for a bottom-only section of the given height."""
    surf = pygame.Surface((CACHE_W, GROUND_Y), pygame.SRCALPHA)
    bot_rect = pygame.Rect(MARGIN, GROUND_Y - section_h, PIPE_W, section_h)
    candidate_streamer_whirl_mill(surf, pygame.Rect(MARGIN, 0, PIPE_W, 0),
                                  bot_rect, pal, SEED)
    cx = MARGIN + PIPE_W // 2
    x0, x1 = cx - PIPE_W // 2, cx + PIPE_W // 2
    run = worst = 0
    for y in range(GROUND_Y - section_h, GROUND_Y):
        filled = any(surf.get_at((x, y))[3] > 50 for x in range(x0, x1 + 1))
        run = 0 if filled else run + 1
        worst = max(worst, run)
    return worst


def _measure_crown(pal, section_h=355):
    """Report the whirl's gutter overhang (max cloth px past the PIPE_W column
    edge) and the sky-gap tail count (separated cloth blobs once the central
    mast/column band is masked out) — the "airy spray of tails" gates."""
    surf = pygame.Surface((CACHE_W, GROUND_Y), pygame.SRCALPHA)
    top_y = GROUND_Y - section_h
    bot_rect = pygame.Rect(MARGIN, top_y, PIPE_W, section_h)
    candidate_streamer_whirl_mill(surf, pygame.Rect(MARGIN, 0, PIPE_W, 0),
                                  bot_rect, pal, SEED)
    cx = MARGIN + PIPE_W // 2
    edge = PIPE_W // 2
    band = pygame.Rect(0, top_y, CACHE_W, min(120, section_h))
    overhang = 0
    for y in range(band.top, band.bottom):
        for x in range(CACHE_W):
            if surf.get_at((x, y))[3] > 50:
                overhang = max(overhang, abs(x - cx) - edge)
    # Zero the central mast/column band, then count separated tail blobs.
    crown = surf.subsurface(band).copy()
    for y in range(crown.get_height()):
        for x in range(cx - 16, cx + 16):
            crown.set_at((x, y), (0, 0, 0, 0))
    mask = pygame.mask.from_surface(crown, 50)
    blobs = [c for c in mask.connected_components() if c.count() >= 6]
    return overhang, len(blobs)


def _render_feas(pal, section_h):
    head = 16
    cell_h = section_h + head + 10
    surf = pygame.Surface((CACHE_W, GROUND_Y), pygame.SRCALPHA)
    bot_rect = pygame.Rect(MARGIN, GROUND_Y - section_h, PIPE_W, section_h)
    candidate_streamer_whirl_mill(surf, pygame.Rect(MARGIN, 0, PIPE_W, 0),
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
    candidate_streamer_whirl_mill(surf, pygame.Rect(MARGIN, 0, PIPE_W, 0),
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
    rc_day = _measure_ribbon_clearance(day)
    rc_night = _measure_ribbon_clearance(night)

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

    sheet.blit(title.render("streamer-whirl-mill — round 2", True, (245, 240, 230)),
               (pad, 12))
    sheet.blit(sub.render("brick mini-pavilion + WHIRL of prayer-streamer ribbons "
                          "spun from a bronze boss  ·  soft/colour/motion pole",
                          True, (170, 172, 182)), (pad, 40))

    for i, (pair, name, cl, rc) in enumerate((
            (pair_day, f"DAY  PHASE={PHASE_DAY}", cl_day, rc_day),
            (pair_night, f"NIGHT  PHASE={PHASE_NIGHT}", cl_night, rc_night))):
        hx = pad + i * (pw + pad)
        hy = title_h
        sheet.blit(pair, (hx, hy))
        pygame.draw.rect(sheet, (60, 62, 72), (hx, hy, pw, ph), 1)
        lab = label.render(name, True, (255, 224, 150))
        sheet.blit(lab, (hx + (pw - lab.get_width()) // 2, hy + ph + 3))
        cl2 = sub.render(f"finial->rim {cl}px  ·  ribbon clr {rc}px", True,
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

    out = _REPO / "docs" / "pillar_landmarks" / "temple_mills" / "streamer-whirl-mill" / "round_2.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(sheet, out)
    print(f"wrote {out}  ({sheet.get_width()}x{sheet.get_height()})")
    print(f"finial centreline->rim gap: day={cl_day}px night={cl_night}px")
    print(f"ribbon clearance below rim: day={rc_day}px night={rc_night}px  (need >=5)")
    print("max empty run: " + "  ".join(f"{h}px->{fills[h]}px" for h in heights))

    # Crown gates: gutter overhang + separated sky-gap tail count (DAY).
    overhang, tails = _measure_crown(day)
    print(f"crown gutter overhang: {overhang}px past column edge")
    print(f"sky-gap separated tail blobs: {tails}")
    # The three DAY ribbon hues — confirm a genuinely COOL middle beat.
    from game.pillar_pagodas import _vermilion as _vm, _gold_bright as _gb
    print(f"DAY ribbon hues: warm={_vm(day)}  cool={_streamer_cool(day)}  gold={_gb(day)}")

    # PIL-sanity (no display): day must differ from night, ribbons must clear the
    # gap, and no cloth/metal pixel may spike to hot white.
    diff = 0
    for yy in range(0, pair_day.get_height(), 3):
        for xx in range(0, pair_day.get_width(), 3):
            if pair_day.get_at((xx, yy))[:3] != pair_night.get_at((xx, yy))[:3]:
                diff += 1
    print(f"day!=night sampled-cell differences: {diff}")
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
