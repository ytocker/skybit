"""Standalone candidate: `vane-star-mill` — a stepped Song-brick ZIGGURAT
altar-tower crowned by a face-on GILDED PINWHEEL STAR, the strongest spin-read
of the temple-mill family.

Colocated EXPLORATION module for the pillar-landmark design loop. It follows
the shipped pagoda idiom (`candidate_*(surf, top_rect, bot_rect, palette,
seed)`, an upright `_draw_one` reused for both rects, the ceiling twin a
vertical flip of a temp surface) but does NOT import into or modify any game/
module — it only borrows read-only colour + AA + ornament helpers so the
exploration reads at the pagoda fidelity bar.

Seeded on the winning `waterwheel-mill` brick-temple material kit: the same
clay-red masonry triad (`_terracotta`/`_brick_mortar`), corbel string-course
lips (`_songyue_dwarf_eave`), matte shrine niche, 3-layer plinth + mist +
foliage, and the candidate-signature / vertical-flip mirror harness. The
water-wheel and all water are REMOVED; the smooth cone body is re-shaped to a
receding STEPPED ZIGGURAT (this concept's body), and the wheel's crown role is
taken by the pinwheel star.

Silhouette identity (set-level pin): the ONLY concept crowned by a POINTED
360° radial GOLD rosette — a face-on pinwheel of bold swept gilt vanes. The
edge signature is POINTED GOLD (vs the sail-fan's flat canvas half-sweep and
the parasol's domed skirt); the star stays a SOLID gilt rosette with air only
as thin curved slots between vanes (a `_vermilion` back-disc peeking through
for the rotation tell) — never four bare canvas arms. Blackout reads as a
receding stair-step pyramid topped by a spiky spinning star.

Column-fill contract: the ~58 px collision column is carried top-to-bottom by
the BRICK ZIGGURAT — every receding step keeps its half-width ≥ PIPE_W/2, so
each body row spans the full column while the steps still read as receding
courses (the recess sits above the column, in the crown). A centred bronze
mast + finial holds the centreline from the top step to the gap rim; the
pinwheel is pure crown/gutter overhang laid over that solid masonry core.

Mirror: the ceiling twin is a true vertical FLIP of an upright draw into a temp
surface. The pinwheel is a CENTRED radial rosette on `cx` (evenly spaced vanes,
a centred mast/finial), so a vertical flip lands it back as a valid spinning
star on the hung twin — chirality reverses but it still reads as a pinwheel.

Run:  python docs/pillar_landmarks/temple_mills/vane-star-mill/render.py
Out:  docs/pillar_landmarks/temple_mills/vane-star-mill/round_1.png
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
    _terracotta,
    _brick_mortar,
    _song_brick,                 # noqa: F401 — imported per brief material kit
    _songyue_dwarf_eave,
    _bronze,
    _gold_bright,
    _gold_deep,
    _vermilion,
    _vermilion_lit,
)
from game.pillar_variants import draw_grass_bed
from game.draw import draw_side_shrub


# ── Material roles (all biome-derived via _mix/_shade so day→night retints) ───
#
# BRICK ZIGGURAT → stone_dark / stone_mid (_terracotta + _brick_mortar): warm
#   clay-red altar courses, the same masonry family as the seed tower.
# PINWHEEL VANES → stone_accent (_gold_bright / _gold_deep): gilt sails, each
#   with a bright specular + a dark leading edge so the star reads as angled
#   metal caught mid-spin, not a flat medallion.
# BOSS + MAST + FINIAL → stone_accent (_bronze): the hub and centreline spine.
# BACK-DISC → horizon (_vermilion): the red that peeks between vanes for the
#   rotation tell.

def _brick_lit(p):
    # Sun-side clay — capped at dusk/night so the shaded flank + niche carry
    # the silhouette instead of a value-spiking wall.
    return _cap_lit_for_dark_sky(_shade(_terracotta(p), 28), p)


def _brick_mid(p):
    return _terracotta(p)


def _brick_shadow(p):
    # Floored at night so the shaded step edge keeps value over a deep sky and
    # the stack doesn't collapse into one black blob.
    return _cap_dark_for_dark_sky(_shade(_terracotta(p), -42), p, floor=60)


def _mortar(p):
    return _shade(_brick_mortar(p), 16)


def _edge_rim(p):
    # Faint cool-lit rim on the shadow-side outline at night so each step holds
    # its edge against a dark sky (day palettes never trigger it).
    return _mix(p['stone_mid'], p['stone_light'], 0.55)


# ── Stepped ziggurat body ─────────────────────────────────────────────────────

def _brick_slab(surf, cx, y_top, y_bot, hw, palette):
    """One receding ziggurat course: a constant-width brick slab painted as a
    left-lit → mid → right-shadow column gradient (the `_gradient_rect` volume
    trick) so the flat course reads as rounded masonry at PIPE_W = 58, with
    mortar coursing every 3 px broken at the centreline for a bonded-brick read
    rather than ledger stripes. WASM-safe: only pygame.draw primitives."""
    h = y_bot - y_top
    if h < 2 or hw < 1:
        return
    lit, mid, shadow = _brick_lit(palette), _brick_mid(palette), _brick_shadow(palette)
    _gradient_rect(surf, pygame.Rect(cx - hw, y_top, hw * 2, h), lit, mid, shadow)
    mortar = _mortar(palette)
    for i in range(h):
        if i % 3 != 2:
            continue
        y = y_top + i
        if (i // 3) % 2 == 0:
            pygame.draw.line(surf, mortar, (cx - hw + 1, y), (cx + hw - 1, y), 1)
        else:
            pygame.draw.line(surf, mortar, (cx - hw + 1, y), (cx - 1, y), 1)
            pygame.draw.line(surf, mortar, (cx + 1, y), (cx + hw - 1, y), 1)
    if _is_dark_sky(palette):
        pygame.draw.line(surf, _edge_rim(palette),
                         (cx + hw - 1, y_top), (cx + hw - 1, y_bot - 1), 1)


def _ziggurat(surf, cx, top_step_y, base_y, hw_top, hw_base, n_steps, palette):
    """A receding stack of `n_steps` brick courses from `hw_base` at the ground
    to `hw_top` at the crown mount. Each step is a `_brick_slab` capped by a
    `_songyue_dwarf_eave` corbel lip (with a tile-hatch tick row) so the
    silhouette reads as stacked altar terraces. Every step half-width stays
    ≥ PIPE_W/2, so the collision column is full at every body row while the
    inward stagger still reads as a ziggurat. Returns the top step's half-width
    so the caller can mount the star on the flat crown."""
    body_h = base_y - top_step_y
    if body_h < 4 or n_steps < 1:
        return hw_top
    edge = _shade(_brick_shadow(palette), -18)
    step_h = body_h / n_steps
    for k in range(n_steps):
        # k = 0 is the ground (widest) course; k = n-1 the crown (narrowest).
        y0 = int(round(base_y - (k + 1) * step_h))
        y1 = int(round(base_y - k * step_h))
        frac = k / max(1, n_steps - 1)           # 0 at ground, 1 at crown
        hw = int(round(hw_base + (hw_top - hw_base) * frac))
        _brick_slab(surf, cx, y0, y1, hw, palette)
        # Vertical silhouette keylines down this course's flanks so each terrace
        # riser reads crisp against its neighbour.
        _aa_polyline(surf, edge, [(cx - hw, y0), (cx - hw, y1)])
        _aa_polyline(surf, edge, [(cx + hw, y0), (cx + hw, y1)])
        # Corbel lip crowning each terrace ledge (skip the top step so the star
        # seats flush on the flat crown).
        if k < n_steps - 1:
            _songyue_dwarf_eave(surf, cx, y0, hw, palette, depth=2)
            _tile_hatch(surf, cx - hw + 3, y0 - 1, cx + hw - 3, y0 - 1,
                        _mortar(palette), step=5)
    return hw_top


# ── The gilded pinwheel star ──────────────────────────────────────────────────

def _cap235(c):
    # Ceiling every channel just below hot-white so even the brightest gilt
    # specular reads as metal, never an emissive flare.
    return (min(232, c[0]), min(232, c[1]), min(232, c[2]))


def _pinwheel_points(cx, cy, r_hub, R, phase, step, k):
    """Curved swept-vane outline for blade `k`: a pointed gilt sail whose
    leading edge bows outward from the hub to a single pointed tip, then a
    straighter trailing edge falls back to the hub. The tip LEANS ahead of the
    root so the blade reads as caught mid-rotation. Returns (points, tip,
    lead_pts) — lead_pts is the advancing edge for the dark keyline."""
    a0 = phase + k * step
    root_a = a0
    root_b = a0 + step * 0.50
    tip_ang = root_b + step * 0.55            # tip leaned ahead → pinwheel sweep
    bow = (R - r_hub) * 0.20
    lead = []
    for i in range(6):
        t = i / 5.0
        ang = root_a + (tip_ang - root_a) * t
        rad = r_hub + (R - r_hub) * t + bow * math.sin(math.pi * t)
        lead.append((cx + math.cos(ang) * rad, cy + math.sin(ang) * rad))
    tip = lead[-1]
    trail = []
    for i in range(1, 5):
        t = i / 4.0
        ang = tip_ang + (root_b - tip_ang) * t
        rad = R + (r_hub - R) * t - bow * 0.35 * math.sin(math.pi * t)
        trail.append((cx + math.cos(ang) * rad, cy + math.sin(ang) * rad))
    return lead + trail, tip, lead


def _pinwheel_star(surf, cx, cy, R, palette, *, seed):
    """A face-on gilt PINWHEEL: 6–8 bold swept vanes from a bronze boss over a
    `_vermilion` back-disc, each vane a lit→shadow gradient with a bright
    specular and a dark leading edge so the whole rosette reads as angled metal
    caught spinning. A global light break (bright on the sun flank, shaded on
    the far flank) carries the 'mid-spin' read edge-to-edge; the pointed tips
    stay crisp gold via an AA silhouette. Solid rosette — air shows only as
    thin curved slots where the red peeks through. A night halo (gated on a
    dark sky) rings the gilt; day palettes never trigger it."""
    if R < 6:
        pygame.draw.circle(surf, _gold_bright(palette), (cx, cy), max(2, R))
        pygame.draw.circle(surf, _bronze(palette), (cx, cy), max(1, R // 3))
        return
    n = 8 if R >= 22 else 6
    step = math.tau / n
    phase = 0.20 + (seed % 5) * 0.06 + step * 0.22   # slight lean off dead-on
    r_hub = max(3, int(R * 0.16))
    gold_lit = _cap235(_gold_bright(palette))
    gold_dark = _gold_deep(palette)
    bronze = _bronze(palette)
    dark_sky = _is_dark_sky(palette)
    light_ang = -2.30                                # sun from upper-left

    # Night halo behind the gilt — additive amber, clamped so it never whites
    # out; only over a dark sky.
    if dark_sky:
        halo = pygame.Surface((R * 4, R * 4), pygame.SRCALPHA)
        hx = hy = R * 2
        for rr in range(int(R * 1.7), int(R * 0.7), -1):
            a = int(46 * (1 - (rr - R * 0.7) / max(1, R)))
            pygame.draw.circle(halo, (150, 116, 44, max(0, a)), (hx, hy), rr)
        surf.blit(halo, (cx - hx, cy - hy), special_flags=pygame.BLEND_ADD)

    # Precompute each blade so the drop-shadow, back-disc and fills share one
    # geometry pass.
    blades = [_pinwheel_points(cx, cy, r_hub, R, phase, step, k) for k in range(n)]

    # Drop-shadow keyline: the pointed silhouette offset down-right, dark, so
    # the star sits off the sky/masonry behind it.
    sil = []
    for pts, tip, _lead in blades:
        sil.append(tip)
        # a valley point in the slot toward the next blade for the star outline
        va = phase + (blades.index((pts, tip, _lead)) + 0.75) * step
        sil.append((cx + math.cos(va) * R * 0.52, cy + math.sin(va) * R * 0.52))
    shadow_pts = [(int(x + 2), int(y + 2)) for x, y in sil]
    _aa_polyline(surf, _shade(bronze, -48), shadow_pts, closed=True)

    # Red back-disc — slightly inside R so the gilt tips overshoot it against
    # the sky; this is the rotation tell peeking through the vane slots.
    pygame.draw.circle(surf, _vermilion(palette), (cx, cy), int(R * 0.74))
    pygame.draw.circle(surf, _shade(_vermilion(palette), -22),
                       (cx, cy), int(R * 0.74), 1)
    # Solid gilt centre so the hub never shows red through the root gaps.
    pygame.draw.circle(surf, gold_dark, (cx, cy), int(R * 0.42))

    for pts, tip, lead in blades:
        am = (lead[3][0] - cx, lead[3][1] - cy)      # mid-blade direction
        mang = math.atan2(am[1], am[0])
        face = 0.5 + 0.5 * math.cos(mang - light_ang)
        fill = _mix(gold_dark, gold_lit, 0.22 + 0.62 * face)
        poly = [(int(x), int(y)) for x, y in pts]
        pygame.draw.polygon(surf, fill, poly)
        # Dark leading (advancing) edge — the shaded metal fold.
        _aa_polyline(surf, _shade(bronze, -26),
                     [(int(x), int(y)) for x, y in lead])
        # Bright specular streak on the sun-lit vanes only (capped, matte metal).
        if face > 0.58:
            spec = _cap235(_mix(gold_lit, palette['stone_light'], 0.45))
            a, b = lead[2], lead[4]
            _aa_polyline(surf, spec, [(int(a[0]), int(a[1])),
                                      (int(b[0]), int(b[1]))])
        # Crisp pointed tip: a 1-px gold spark so the point never rounds off.
        pygame.draw.circle(surf, gold_lit, (int(tip[0]), int(tip[1])), 1)

    # Crisp AA silhouette over the whole pointed rosette so the star edge reads
    # sharp at 58 px.
    _aa_polyline(surf, _shade(gold_dark, -10),
                 [(int(x), int(y)) for x, y in sil], closed=True)

    # Bronze boss + gold glint at the hub.
    pygame.draw.circle(surf, _shade(bronze, -28), (cx, cy), r_hub + 1)
    pygame.draw.circle(surf, bronze, (cx, cy), r_hub)
    pygame.draw.circle(surf, gold_lit, (cx - 1, cy - 1), max(1, r_hub // 2))
    if dark_sky:
        # Capped light rim so the boss holds by value against a deep sky.
        pygame.draw.circle(surf, _cap235(_vermilion_lit(palette)),
                           (cx, cy), r_hub, 1)


def _matte_niche(surf, cx, cy, w, h, palette):
    """A recessed shrine doorway drawn MATTE — dark frame + darker inside + a
    thin warm rim on an alpha blit (never additive), so it reads as a quiet
    shrine mouth without becoming a second glow source competing with the
    gilt star."""
    if w < 3 or h < 4:
        return
    frame = _shade(palette['stone_dark'], -25)
    inside = _shade(palette['stone_dark'], -50)
    pygame.draw.rect(surf, frame, (cx - w // 2, cy, w, h))
    pygame.draw.rect(surf, inside, (cx - w // 2 + 1, cy + 1, w - 2, h - 2))
    rim = _cap235(_mix(palette['stone_accent'], (210, 180, 110), 0.7))
    alpha = 150 if _is_dark_sky(palette) else 90
    rim_layer = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(rim_layer, (*rim, alpha), (0, 0, w, h), 1)
    surf.blit(rim_layer, (cx - w // 2, cy))


# ── One upright silhouette ───────────────────────────────────────────────────

def _draw_one(surf, cx, base_y, top_y, body_w, palette, seed, *, decor=True):
    """One upright vane-star-mill filling [top_y, base_y]. Height-adaptive: the
    stepped ziggurat carries the collision column (every step half-width
    ≥ PIPE_W/2); the star + step count shrink on short sections; a centred
    bronze mast + finial holds the centreline from the top step to the gap
    rim."""
    total_h = base_y - top_y
    if total_h < 20:
        return
    dark_sky = _is_dark_sky(palette)

    # Step half-widths: base overhangs into the gutter, the crown step stays
    # ≥ PIPE_W/2 so even the narrowest terrace still spans the full column.
    hw_base = max(PIPE_W // 2 + 4, int(body_w * 0.80))
    hw_top = max(PIPE_W // 2 + 1, int(body_w * 0.52))

    # Crown budget (star + mast + finial) above the top step.
    crown_h = max(20, min(int(total_h * 0.36), 82))
    shoulder_y = top_y + crown_h

    # 3-layer plinth under the ziggurat.
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
    body_h = body_base_y - shoulder_y
    n_steps = max(2, min(5, body_h // 22))
    _ziggurat(surf, cx, shoulder_y, body_base_y, hw_top, hw_base, n_steps, palette)

    # Shrine doorway niche centred on the widest (ground) course.
    if body_h > 26 and hw_base > 16:
        door_w = min(9, hw_base // 3)
        door_h = min(15, body_h // 3)
        _matte_niche(surf, cx, body_base_y - door_h, door_w, door_h, palette)

    # ── The pinwheel star (crown/gutter overhang) ─────────────────────────────
    star_r = max(9, min((crown_h - 5) // 2 + 6, hw_top + 24, 34))
    if total_h < 30:
        star_r = min(star_r, 12)
    star_cy = top_y + star_r + 4                 # top tip sits near the gap rim

    # Bronze centreline spine: a mast from the boss down onto the top step, and
    # a finial needle from the star's top up to the gap rim, so the collision
    # column is continuously occupied at cx from rim to ground.
    bronze = _bronze(palette)
    pygame.draw.line(surf, _shade(bronze, -30),
                     (cx, star_cy), (cx, shoulder_y + 2), 3)
    pygame.draw.line(surf, bronze, (cx, star_cy), (cx, shoulder_y + 2), 1)
    pygame.draw.line(surf, _shade(bronze, -30),
                     (cx, star_cy - star_r), (cx, top_y + 2), 2)
    pygame.draw.circle(surf, bronze, (cx, top_y + 2), 2)
    pygame.draw.circle(surf, _gold_bright(palette), (cx, top_y + 2), 1)

    _pinwheel_star(surf, cx, star_cy, star_r, palette, seed=seed)

    if decor:
        draw_grass_bed(surf, cx, base_y - 1, pw0 + 6, 14, palette, seed=seed)
        draw_side_shrub(surf, cx - (hw_base - 2), base_y - 1, palette, scale=0.85)
        draw_side_shrub(surf, cx + (hw_base - 2), base_y - 1, palette, scale=0.7)


def candidate_vane_star_mill(surf, top_rect, bot_rect, palette, seed):
    bcx = bot_rect.x + bot_rect.width // 2
    tcx = top_rect.x + top_rect.width // 2

    if bot_rect.height > 22:
        _draw_one(surf, bcx, bot_rect.bottom, bot_rect.y,
                  bot_rect.width, palette, seed, decor=True)

    if top_rect.height > 22:
        # Structural mirror: draw upright into a temp sized to top_rect.height,
        # flip vertically, hang from the ceiling. The centred pinwheel + centred
        # mast/finial survive the flip as a valid spinning star on the hung twin.
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
SEED = 12

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
    candidate_vane_star_mill(surf, top_rect, bot_rect, pal, SEED)
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
    """Mirrored-centreline coverage: on the top (hung) section, how close the
    body centreline reaches the gap rim (TOP_H). 0 = the finial touches."""
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
    candidate_vane_star_mill(surf, pygame.Rect(MARGIN, 0, PIPE_W, 0),
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
    candidate_vane_star_mill(surf, pygame.Rect(MARGIN, 0, PIPE_W, 0),
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
    candidate_vane_star_mill(surf, pygame.Rect(MARGIN, 0, PIPE_W, 0),
                             bot_rect, pal, SEED)
    crop_top = GROUND_Y - section_h - 12
    crop = surf.subsurface(pygame.Rect(0, crop_top, CACHE_W, section_h + 12)).copy()
    mask = pygame.mask.from_surface(crop, 60)
    return mask.to_surface(setcolor=(18, 18, 22, 255),
                           unsetcolor=(232, 232, 236, 255))


def _sample_body(pal):
    """Pick a mid-body brick pixel + a vane pixel for the day≠night check."""
    surf = _pair_surf(pal)
    cx = MARGIN + PIPE_W // 2
    # brick: a row well inside the bottom ziggurat
    brick = surf.get_at((cx, GROUND_Y - 40))
    return (brick[0], brick[1], brick[2])


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

    sheet.blit(title.render("vane-star-mill — round 1", True, (245, 240, 230)),
               (pad, 12))
    sheet.blit(sub.render("stepped brick ZIGGURAT + face-on GILDED PINWHEEL STAR: "
                          "pointed gilt vanes, red back-disc peeking, mid-spin "
                          "value break", True, (170, 172, 182)), (pad, 40))

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

    out = _REPO / "docs" / "pillar_landmarks" / "temple_mills" / "vane-star-mill" / "round_1.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(sheet, out)
    print(f"wrote {out}  ({sheet.get_width()}x{sheet.get_height()})")
    print(f"mirror centreline->rim gap: day={cl_day}px night={cl_night}px")
    print("max empty run: " + "  ".join(f"{h}px->{fills[h]}px" for h in heights))

    # PIL-sanity (no display): body brick colour must differ day vs night
    # (the biome retint is live), and nothing may spike to hot white.
    bd, bn = _sample_body(day), _sample_body(night)
    print(f"body brick day={bd} night={bn}  diff={tuple(bd[i]-bn[i] for i in range(3))}")
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
