"""Standalone candidate: `shoji-rose-mill` — a flat plaster-and-timber temple
slab crossed by a single large CENTRED glowing paper (shoji) rosette wind-disc.

Colocated EXPLORATION module for the pillar-landmark design loop. It follows the
shipped pagoda idiom (`candidate_*(surf, top_rect, bot_rect, palette, seed)`,
upright `_draw_one` reused for both rects, the top section a vertical flip of a
temp surface) but does NOT import into or modify any game/ module — it only
borrows read-only colour + ornament helpers so the exploration reads like the
real game.

Silhouette identity — the GLOWING-PAPER-DISC pole of the windmill family:
the ONLY concept with a large, filled, on-axis luminous coin at the gap. Distinct
from #1's thin open sail-X (air between arms) and #2's off-axis wooden wheel — this
is a symmetric filled paper rosette hubbed on the tower axis, and the ONLY
mechanism that emits light: a washi-paper fan on dark bamboo mullions that blooms
amber at dusk/night and reads by day on its rib structure alone.

Column-fill contract: the collision column (central PIPE_W band) is filled by the
solid plaster SLAB, top-to-bottom, at every section height — the disc is a centred
overlay on that solid core, never a hole in it, so no empty vertical run opens.
The amber glow is placed so it never bridges the flyable gap (glow top clears the
gap rim on both mirrored halves).

Run:  python docs/pillar_landmarks/windmills/shoji-rose-mill/render.py
Out:  docs/pillar_landmarks/windmills/shoji-rose-mill/round_1.png
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
    _glazed_tile_checker,
    _draw_plinth_mist,
    _is_dark_sky,
    _is_warming_sky,
    _cap_lit_for_dark_sky,
    _cap_dark_for_dark_sky,
    _plaster,
    _white_plaster_warm,
    _cedar,
    _vermilion,
    _bronze,
    _gold_bright,
)
from game.pillar_variants import draw_grass_bed, draw_fern_cluster


# ── Colour roles (all biome-derived so day→dusk→night retints sweep through) ──
#
# Slab body = warm white-clay plaster (stone_light) so the biome carries cool
# nights and warm dawns through it; the timber frame is cedar (stone_dark); the
# paper leaves are plaster warmed one beat toward washi cream; the mullion ribs +
# rim are cedar; the hub + finial carry the bronze/gold focal (stone_accent).


def _slab_lit(pal):
    # Sunlit plaster face, value-capped at night so the disc glow and the rib
    # structure carry the silhouette instead of a wall that spikes to ~245.
    return _cap_lit_for_dark_sky(_white_plaster_warm(pal), pal)


def _slab_mid(pal):
    return _plaster(pal)


def _slab_shadow(pal):
    # Floored at night so the shaded slab edge keeps value over a deep sky
    # rather than merging into it.
    return _cap_dark_for_dark_sky(_shade(_plaster(pal), -42), pal, floor=64)


def _paper_lit(pal):
    # Washi warmed toward firefly cream — the sunward leaves.
    return _mix(_white_plaster_warm(pal), (255, 238, 206), 0.38)


def _paper_mid(pal):
    return _plaster(pal)


def _paper_shadow(pal):
    return _shade(_plaster(pal), -34)


def _rib(pal):
    # Bamboo/cedar mullion — the dark ribs the washi is stretched over. This is
    # what makes the disc read as PANELS (and read by DAY) rather than a coin.
    return _shade(_cedar(pal), -18)


def _rib_lit(pal):
    return _mix(_cedar(pal), pal['stone_light'], 0.45)


def _amber(pal):
    # Back-glow / lantern emission colour — the identity beat. Warm firefly amber
    # pulled off stone_accent so dusk/night retint it, then blended to a fixed
    # lantern warm so it always reads as light, not as a recolour of the wall.
    return _mix(pal['stone_accent'], (255, 214, 132), 0.82)


# ── The luminous paper rosette ───────────────────────────────────────────────

def _arc_pts(cx, cy, r, a0, a1, steps=5):
    return [(cx + math.cos(a0 + (a1 - a0) * k / steps) * r,
             cy + math.sin(a0 + (a1 - a0) * k / steps) * r)
            for k in range(steps + 1)]


def _disc_glow(disc_r, palette):
    """Cached additive amber halo behind the disc — the light-emitter beat.
    Three-stop bloom keyed to sky brightness (same calibration idiom as
    `_lit_niche`): a strong wide bloom at DUSK/NIGHT, a medium warm pre-glow at
    SUNSET, and a quiet near-nothing cast by DAY so the disc reads as paper, not
    a lamp, under a bright sky. Returns (surface, radius) so the caller can
    centre it and clamp the bloom clear of the gap rim.

    pygbag-safe: SRCALPHA circles + a single BLEND_RGBA_ADD blit, no surfarray.
    """
    dark = _is_dark_sky(palette)
    warm = _is_warming_sky(palette)
    if dark and not warm:
        ext, peak = int(disc_r * 0.52), 168
    elif warm:
        ext, peak = int(disc_r * 0.34), 92
    else:
        ext, peak = int(disc_r * 0.16), 26
    amber = _amber(palette)
    R = disc_r + ext
    sz = R * 2 + 2
    g = pygame.Surface((sz, sz), pygame.SRCALPHA)
    c = sz // 2
    # Outer faint → inner strong so the halo has a soft falloff, brightest at
    # the hub where a back-lit paper fan pools its light.
    rings = 7
    for i in range(rings):
        t = i / (rings - 1)                       # 0 outer, 1 inner
        rr = int(R * (1.0 - t) + disc_r * 0.18 * t)
        a = int(peak * (t ** 1.6))
        if rr >= 1 and a > 0:
            pygame.draw.circle(g, (*amber, a), (c, c), rr)
    return g, R


def _paper_backlight(disc_r, palette):
    """Additive amber pooled INSIDE the paper (radius < disc_r) so the leaves
    read as back-lit washi at dusk/night — the firefly-glow-through-paper cue on
    top of the wide halo. Quiet/None by day."""
    dark = _is_dark_sky(palette)
    warm = _is_warming_sky(palette)
    if not (dark or warm):
        return None
    peak = 120 if (dark and not warm) else 64
    amber = _mix(_amber(palette), (255, 246, 220), 0.35)
    R = int(disc_r * 0.86)
    sz = R * 2 + 2
    g = pygame.Surface((sz, sz), pygame.SRCALPHA)
    c = sz // 2
    rings = 6
    for i in range(rings):
        t = i / (rings - 1)
        rr = int(R * (1.0 - t) + 1)
        a = int(peak * (t ** 1.4))
        if rr >= 1 and a > 0:
            pygame.draw.circle(g, (*amber, a), (c, c), rr)
    return g


def _rosette(surf, cx, cy, core_r, petal_r, palette, seed):
    """The centred, filled, glowing paper wind-ROSETTE. A ring of N swept washi
    petals bulging past the slab sides on a bronze hub; a cached additive halo
    blooms behind it at dusk/night.

    Silhouette identity is carried by the SCALLOPED outer edge (petal tips bulge
    to `petal_r`, dip to `core_r` at the seams) so the pole never reads as a
    coin/lantern-on-a-wall, and by a consistent pinwheel SWEEP on every petal
    spine so it reads as angled paper sails catching wind. The petal phase is
    PINNED (not seeded) so a tip lands on the horizontal axis on both sides —
    the overhang into the two gutters is then symmetric and stays on the tower
    axis, and survives the vertical flip of the ceiling half."""
    if petal_r < 6:
        pygame.draw.circle(surf, _paper_mid(palette), (cx, cy), max(2, petal_r))
        return
    n = 12
    step = 2 * math.pi / n
    p = 0.62                                        # petal-fatness exponent
    peak_f = 0.5 ** (1.0 / p)                       # where the bulge peaks in a petal
    rot = -peak_f * step                            # pin a tip to the horizontal axis
    steps_arc = 6
    amp = petal_r - core_r
    paper_lit = _paper_lit(palette)
    paper_mid = _paper_mid(palette)
    paper_shadow = _paper_shadow(palette)
    rib = _rib(palette)
    # Recessed dark cedar so the disc separates from the plaster by a hard value
    # break at every sky brightness (the day value-moat), not just by hue.
    socket = _shade(_cedar(palette), -40)

    def _petal_rad(f, extra=0.0):
        # Scallop profile: valley (core_r) at the seams, bulge (petal_r) at the
        # tip; the peak sits toward the leading edge so the lobe reads as swept.
        return core_r + amp * math.sin(math.pi * (f ** p)) + extra

    # 1 — wide additive halo BEHIND the paper (blooms at dusk/night, quiet by day).
    glow, gr = _disc_glow(petal_r, palette)
    surf.blit(glow, (cx - gr, cy - gr), special_flags=pygame.BLEND_RGBA_ADD)

    # 2 — recessed dark SCALLOPED socket (petal profile + 2 px): a thin dark moat
    # ringing the whole flower and pooling in the seam valleys, so the rosette
    # separates from the wall by value AND the scallop reads even by day.
    socket_pts = []
    for i in range(n):
        a0 = rot + i * step
        for k in range(steps_arc + 1):
            f = k / steps_arc
            ang = a0 + step * f
            rad = _petal_rad(f, 2.0)
            socket_pts.append((cx + math.cos(ang) * rad, cy + math.sin(ang) * rad))
    pygame.draw.polygon(surf, socket, [(int(x), int(y)) for x, y in socket_pts])

    # 3 — solid paper base coin so no socket/sky peeks through the hub area.
    pygame.draw.circle(surf, paper_mid, (cx, cy), core_r)

    # 4 — the swept washi petals: each a soft 3-band radial (rim → mid →
    # hub-bright) times a directional lit/shadow split so the sunward (upper-left)
    # side sits a half-stop brighter and the fan reads as folded, swept panels.
    lx, ly = -0.7071, -0.7071                       # light from the upper-left
    for i in range(n):
        a0 = rot + i * step
        amid = a0 + step * peak_f
        d = math.cos(amid) * lx + math.sin(amid) * ly
        b = 0.5 + 0.5 * d                           # 0 shadow-side → 1 sun-side
        base = _mix(paper_shadow, paper_lit, 0.30 + 0.55 * b)
        for r_scale, lift in ((1.0, 0.0), (0.62, 0.18), (0.32, 0.32)):
            col = _mix(base, paper_lit, lift)
            poly = [(cx, cy)]
            for k in range(steps_arc + 1):
                f = k / steps_arc
                ang = a0 + step * f
                rad = _petal_rad(f) * r_scale
                poly.append((cx + math.cos(ang) * rad, cy + math.sin(ang) * rad))
            pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in poly])

    # 5 — back-lit wash INSIDE the paper at dusk/night (firefly glow through washi).
    bl = _paper_backlight(core_r, palette)
    if bl is not None:
        r = bl.get_width() // 2
        surf.blit(bl, (cx - r, cy - r), special_flags=pygame.BLEND_RGBA_ADD)

    # 6 — bowed cedar rib along each petal spine, all bowing the SAME way: the
    # pinwheel leading-edge cue. Replaces the old concentric batten ring so the
    # fan no longer reads as a dartboard.
    bow = 0.20
    for i in range(n):
        tang = rot + i * step + step * peak_f       # petal-tip direction
        tx, ty = cx + math.cos(tang) * petal_r * 0.86, cy + math.sin(tang) * petal_r * 0.86
        mang = tang + bow
        mx, my = cx + math.cos(mang) * petal_r * 0.46, cy + math.sin(mang) * petal_r * 0.46
        _aa_polyline(surf, rib, [(cx, cy), (mx, my), (tx, ty)])

    # 7 — bronze hub + gold finial: the on-axis termination that says "wind-disc".
    hub_r = max(3, petal_r // 6)
    pygame.draw.circle(surf, _shade(_bronze(palette), -30), (cx, cy), hub_r + 1)
    pygame.draw.circle(surf, _bronze(palette), (cx, cy), hub_r)
    pygame.draw.circle(surf, _gold_bright(palette), (cx, cy), max(1, hub_r - 2))
    surf.set_at((cx - 1, cy - 1), _mix(_gold_bright(palette), (255, 255, 240), 0.7))


# ── The slab body ────────────────────────────────────────────────────────────

def _draw_one(surf, cx, base_y, top_y, body_w, palette, seed, *, apron=True):
    """One upright shoji-rose-mill silhouette filling [top_y, base_y]. The solid
    plaster slab fills the whole collision column; the luminous rosette is a
    centred overlay pinned near the gap end. Height-adaptive: short sections get
    a smaller disc but the slab still fills the column edge-to-edge."""
    total_h = base_y - top_y
    if total_h < 18:
        return

    hw = body_w // 2                               # slab spans the full PIPE_W
    plinth_h = 6 if total_h > 60 else 3

    # Atmospheric backlight wedge behind the plinth (only where it grounds).
    if apron:
        _draw_plinth_mist(surf, cx, base_y, hw * 2 + 20, palette)

    body_base_y = base_y - (plinth_h if apron else 0)
    slab = pygame.Rect(cx - hw, top_y, hw * 2, body_base_y - top_y)

    # 1 — the flat plaster slab, per-column gradient (lit-left → shadow-right) so
    # the wall reads as a 3-D volume, not a painted rectangle.
    _gradient_rect(surf, slab, _slab_lit(palette), _slab_mid(palette),
                   _slab_shadow(palette))

    # 2 — cedar timber frame: corner posts + top/bottom rails so the slab reads
    # as a framed temple wall. Posts sit INSIDE the column so the fill stays full.
    post_w = 4 if body_w > 30 else 3
    cedar = _cedar(palette)
    cedar_d = _shade(cedar, -26)
    cedar_l = _shade(cedar, 24)
    for px in (cx - hw, cx + hw - post_w):
        pr = pygame.Rect(px, top_y, post_w, slab.height)
        _gradient_rect(surf, pr, cedar_l, cedar, cedar_d)
    rail_h = 3
    for ry in (top_y, body_base_y - rail_h):
        pygame.draw.rect(surf, cedar, (cx - hw, ry, hw * 2, rail_h))
        pygame.draw.line(surf, cedar_l, (cx - hw, ry), (cx + hw, ry), 1)

    # 3 — low glazed hip-cap coping banding the gap-end rail (a tiled temple
    # coping the disc rides against). Kept thin so the disc stays the focal.
    cap_h = 5 if total_h > 50 else 3
    _glazed_tile_checker(surf, cx - hw + post_w, top_y + rail_h,
                         hw * 2 - post_w * 2, cap_h, palette, tile=4)
    _tile_hatch(surf, cx - hw + post_w, top_y + rail_h + cap_h,
                cx + hw - post_w, top_y + rail_h + cap_h,
                _shade(cedar, -34), step=4)

    # 4 — the luminous rosette, CENTRED on the axis and pinned near the gap end.
    # Petal TIPS overhang the slab sides (petal_r > hw) so the silhouette breaks
    # the plain rectangle and reads as a paper flower, not an inset coin; only
    # the tips poke into the gutters — the seam valleys stay inside the column.
    # disc_cy places the whole bloom clear of the gap rim (top_y) so a mirrored
    # pair never bridges the flyable channel.
    petal_r = int(min(hw + 8, total_h * 0.40))     # ~37 at PIPE_W → 8 px overhang
    petal_r = max(6, petal_r)
    core_r = max(4, int(petal_r * 0.72))           # valley radius stays < hw
    glow_ext = int(petal_r * 0.52)                 # matches the night bloom reach
    disc_cy = top_y + cap_h + rail_h + petal_r + glow_ext + 4
    # Keep the disc + bloom inside the body; if the section is too short to seat
    # it near the gap, shrink and centre it on the slab instead.
    lowest = body_base_y - petal_r - 4
    if disc_cy > lowest:
        disc_cy = max(top_y + petal_r + 4, (top_y + rail_h + body_base_y) // 2)
        petal_r = min(petal_r, disc_cy - (top_y + rail_h + 2),
                      body_base_y - disc_cy - 2)
        petal_r = max(5, petal_r)
        core_r = max(3, int(petal_r * 0.72))
    _rosette(surf, cx, disc_cy, core_r, petal_r, palette, seed)

    # 5 — a pair of lit shrine niches low on the slab (warm point-sources at
    # night, quiet shadow by day) so the body isn't dead below the disc.
    niche_top = disc_cy + petal_r + 8
    if body_base_y - niche_top > 12 and hw > 10:
        nw, nh = max(4, hw // 4), min(11, (body_base_y - niche_top) // 2)
        for nx in (cx - hw // 2, cx + hw // 2):
            _lit_niche(surf, nx, niche_top, nw, nh, palette)

    # 6 — 3-layer stone plinth + foliage where the slab grounds.
    if apron:
        pw = hw * 2 + 10
        pygame.draw.rect(surf, _shade(palette['stone_dark'], -16),
                         (cx - pw // 2, base_y - plinth_h, pw, plinth_h))
        pygame.draw.rect(surf, _mix(palette['stone_mid'], palette['stone_light'], 0.35),
                         (cx - pw // 2, base_y - plinth_h, pw, 2))
        pygame.draw.line(surf, palette['stone_light'],
                         (cx - pw // 2, base_y - plinth_h),
                         (cx + pw // 2, base_y - plinth_h), 1)
        draw_grass_bed(surf, cx, base_y - 1, pw + 4, 14, palette, seed=seed)
        draw_fern_cluster(surf, cx - pw // 2 + 4, base_y - 1, 5, palette, seed=seed)
        draw_fern_cluster(surf, cx + pw // 2 - 4, base_y - 1, 5, palette, seed=seed + 3)


def candidate_shoji_rose_mill(surf, top_rect, bot_rect, palette, seed):
    bcx = bot_rect.x + bot_rect.width // 2
    tcx = top_rect.x + top_rect.width // 2

    if bot_rect.height > 20:
        _draw_one(surf, bcx, bot_rect.bottom, bot_rect.y,
                  bot_rect.width, palette, seed, apron=True)

    if top_rect.height > 20:
        # Structural mirror: draw upright into a temp sized to top_rect.height,
        # flip vertically, hang from the ceiling — the disc then sits near the
        # gap on the ceiling half exactly as it does on the floor half, and being
        # on the centre axis the flip stays symmetric.
        w = surf.get_width()
        tmp = pygame.Surface((w, top_rect.height), pygame.SRCALPHA)
        _draw_one(tmp, tcx, top_rect.height, 0,
                  top_rect.width, palette, seed, apron=False)
        flipped = pygame.transform.flip(tmp, False, True)
        surf.blit(flipped, (0, top_rect.y))


# ── Review harness ───────────────────────────────────────────────────────────

MARGIN = 64
CACHE_W = PIPE_W + MARGIN * 2
PHASE_DAY = 0.30
PHASE_NIGHT = 0.85
SEED = 7

GAP_Y, GAP_H = 205, 150
TOP_H = int(GAP_Y - GAP_H / 2)
BOT_TOP = int(GAP_Y + GAP_H / 2)
CROP_TOP, CROP_BOT = 18, 486


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
    candidate_shoji_rose_mill(surf, top_rect, bot_rect, pal, SEED)
    return surf


def _render_pair(pal):
    surf = _pair_surf(pal)
    cell = _sky_ground(CACHE_W, GROUND_Y, pal, 60)
    cell.blit(surf, (0, 0))
    guide = (255, 90, 90)
    for rim in (TOP_H, BOT_TOP):
        for x in range(0, CACHE_W, 8):
            pygame.draw.line(cell, guide, (x, rim), (x + 4, rim), 1)
    return cell.subsurface(pygame.Rect(0, CROP_TOP, CACHE_W, CROP_BOT - CROP_TOP)).copy()


def _measure_glow_bridge(pal):
    """Deepest additive-bloom intrusion into the flyable gap channel (the rows
    strictly between the two rims) across the full width — proves the amber bloom
    does not bridge the gap. 0 = fully contained; a positive number would be the
    intrusion depth in px. The slab bodies legitimately touch each rim, so only
    pixels INSIDE the channel are counted."""
    surf = _pair_surf(pal)
    worst = 0
    for y in range(TOP_H + 1, BOT_TOP):
        lit = any(surf.get_at((x, y))[3] > 20 for x in range(CACHE_W))
        if lit:
            worst = max(worst, min(y - TOP_H, BOT_TOP - y))
    return worst


def _measure_overhang(pal):
    """Max px the painted rosette pokes past the slab side edges (cx ± hw) into
    each gutter, over the whole height — proves the silhouette breaks the plain
    rectangle. Returns (left, right); both should be > 0 and near-equal (on-axis
    symmetric overhang)."""
    surf = _pair_surf(pal)
    cx = MARGIN + PIPE_W // 2
    hw = PIPE_W // 2
    left = right = 0
    for y in range(GROUND_Y):
        for x in range(cx - hw - 40, cx - hw):
            if surf.get_at((x, y))[3] > 40:
                left = max(left, (cx - hw) - x)
                break
        for x in range(min(CACHE_W - 1, cx + hw + 40), cx + hw, -1):
            if surf.get_at((x, y))[3] > 40:
                right = max(right, x - (cx + hw))
                break
    return left, right


def _measure_fill(pal, section_h):
    """Max vertical run (px) of rows with ZERO fill inside the PIPE_W collision
    column, for a bottom-only section of the given height."""
    surf = pygame.Surface((CACHE_W, GROUND_Y), pygame.SRCALPHA)
    bot_rect = pygame.Rect(MARGIN, GROUND_Y - section_h, PIPE_W, section_h)
    candidate_shoji_rose_mill(surf, pygame.Rect(MARGIN, 0, PIPE_W, 0),
                              bot_rect, pal, SEED)
    cx = MARGIN + PIPE_W // 2
    x0, x1 = cx - PIPE_W // 2, cx + PIPE_W // 2
    run = worst = 0
    for y in range(GROUND_Y - section_h, GROUND_Y):
        filled = any(surf.get_at((x, y))[3] > 40 for x in range(x0, x1 + 1))
        run = 0 if filled else run + 1
        worst = max(worst, run)
    return worst


def _render_feas(pal, section_h):
    head = 16
    cell_h = section_h + head + 10
    surf = pygame.Surface((CACHE_W, GROUND_Y), pygame.SRCALPHA)
    bot_rect = pygame.Rect(MARGIN, GROUND_Y - section_h, PIPE_W, section_h)
    candidate_shoji_rose_mill(surf, pygame.Rect(MARGIN, 0, PIPE_W, 0),
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
    candidate_shoji_rose_mill(surf, pygame.Rect(MARGIN, 0, PIPE_W, 0),
                              bot_rect, pal, SEED)
    crop_top = GROUND_Y - section_h - 12
    crop = surf.subsurface(pygame.Rect(0, crop_top, CACHE_W, section_h + 12)).copy()
    mask = pygame.mask.from_surface(crop, 40)
    return mask.to_surface(setcolor=(18, 18, 22, 255),
                           unsetcolor=(232, 232, 236, 255))


def main():
    pygame.init()
    pygame.display.set_mode((1, 1))
    day = biome.palette_for_phase(PHASE_DAY)
    night = biome.palette_for_phase(PHASE_NIGHT)

    pair_day = _render_pair(day)
    pair_night = _render_pair(night)
    br_day = _measure_glow_bridge(day)
    br_night = _measure_glow_bridge(night)
    ov_day = _measure_overhang(day)
    ov_night = _measure_overhang(night)

    heights = [70, 210, 355]
    feas = [_render_feas(day, h) for h in heights]
    fills = {h: _measure_fill(day, h) for h in heights}
    blackout = _render_blackout(day)

    pad = 14
    label_h = 22
    title_h = 60
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

    sheet.blit(title.render("shoji-rose-mill — round 2", True, (245, 240, 230)),
               (pad, 12))
    sheet.blit(sub.render("swept SCALLOPED paper rosette · tips OVERHANG slab "
                          "sides · dark value-moat · mirrored pair, day + night",
                          True, (170, 172, 182)), (pad, 40))

    for i, (pair, name, br, ov) in enumerate((
            (pair_day, f"DAY  PHASE={PHASE_DAY}", br_day, ov_day),
            (pair_night, f"NIGHT  PHASE={PHASE_NIGHT}", br_night, ov_night))):
        hx = pad + i * (pw + pad)
        hy = title_h
        sheet.blit(pair, (hx, hy))
        pygame.draw.rect(sheet, (60, 62, 72), (hx, hy, pw, ph), 1)
        lab = label.render(name, True, (255, 224, 150))
        sheet.blit(lab, (hx + (pw - lab.get_width()) // 2, hy + ph + 3))
        cl2 = sub.render(f"gap bloom intrusion: {br}px  ·  side overhang "
                         f"L{ov[0]}/R{ov[1]}px", True, (200, 202, 212))
        sheet.blit(cl2, (hx + (pw - cl2.get_width()) // 2, hy + ph + 3 + 18))

    bx = pad
    by = title_h + ph + label_h + pad + 14
    sheet.blit(blackout, (bx, by))
    pygame.draw.rect(sheet, (60, 62, 72), (bx, by, bo_w, bo_h), 1)
    lab = label.render("BLACKOUT — 58px silhouette (scallop breaks slab sides)",
                       True, (255, 224, 150))
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

    out = _REPO / "docs" / "pillar_landmarks" / "windmills" / "shoji-rose-mill" / "round_2.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(sheet, out)
    print(f"wrote {out}  ({sheet.get_width()}x{sheet.get_height()})")
    print(f"gap-channel bloom intrusion: day={br_day}px  night={br_night}px")
    print(f"side overhang (px past slab edge): day=L{ov_day[0]}/R{ov_day[1]}  "
          f"night=L{ov_night[0]}/R{ov_night[1]}")
    print(f"max empty run: " + "  ".join(f"{h}px->{fills[h]}px" for h in heights))


if __name__ == "__main__":
    main()
