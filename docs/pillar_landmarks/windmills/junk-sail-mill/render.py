"""Standalone candidate: `junk-sail-mill` — a South-China vertical-axis mill.
An open lashed-bamboo LATTICE cage tower carrying an upright cylinder of
battened junk sails (a Chinese "revolving-lantern" horizontal windmill), with
a centred vertical shaft, a bronze deck ring, and a finial at the gap.

Colocated EXPLORATION module for the pillar-landmark design loop. It follows
the shipped pagoda idiom (`candidate_*(surf, top_rect, bot_rect, palette,
seed)`, an upright `_draw_one` reused for both rects, the top section a vertical
flip of a temp surface) and borrows the REAL `pillar_pagodas` colour/ornament
helpers so the exploration reads like the game — but it does not import into or
modify any shipped drawing path.

Silhouette identity: the ONLY open see-through bamboo-cage body in the windmill
family, and the ONLY upright-comb mechanism — a fluttering vertical fence of
battened sails around a vertical axis, NOT a radial sail-X (#1), NOT a filled
paper disc (#4), NOT a side water-wheel (#2), NOT a drum stack (#3).

Fill contract (the AD's flagged risk for this concept): an open lattice must
NOT leave a gutter-visible empty band >12 px in the ~58 px collision column. It
is solved by a subtly-shaded SOLID inner back-screen (`_gradient_rect` dim
bamboo) spanning the full cage column, read as the shadowed far side of the
cage seen THROUGH the lattice; the airy front poles + bright X-lashings + a
solid plaster milling-floor band sit lit on top of it, so the cage still reads
open/3-D while every row of the column stays occupied. In the crown, a centred
solid cedar shaft holds the centreline continuously to the finial. Max empty
vertical run in the central band is 0 px at every tested height (see harness).

Run:  python docs/pillar_landmarks/windmills/junk-sail-mill/render.py
Out:  docs/pillar_landmarks/windmills/junk-sail-mill/round_2.png
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
    _draw_plinth_mist,
    _is_dark_sky,
    _is_warming_sky,
    _cap_lit_for_dark_sky,
    _cap_dark_for_dark_sky,
    _cedar,
    _ochre_wood,
    _ochre_wood_lit,
    _ochre_wood_shadow,
    _bronze,
    _plaster,
    _vermilion,
)
from game.pillar_variants import draw_grass_bed
from game.draw import draw_side_shrub


# ── Colour roles (all biome-derived so day→night retints sweep through) ───────
#
# Bamboo culms ride _ochre_wood's warm larch triad; the recessed back-screen is
# the SAME bamboo pushed dark + cooled + value-floored so it reads as the
# shadowed far wall of the cage, never as a solid plaster block. Lashings are
# the warm stone_accent rope with a bright lit spine; the milling floor is
# bright stone_light plaster; the junk sails are a warm reed-matting canvas
# (stone_light) battened with dark ochre ribs and bound with a vermilion leech;
# shaft is cedar; cap ring + finial are patinated bronze.


def _pole_lit(pal):
    return _cap_lit_for_dark_sky(_ochre_wood_lit(pal), pal)


def _pole_mid(pal):
    return _ochre_wood(pal)


def _pole_shadow(pal):
    return _cap_dark_for_dark_sky(_ochre_wood_shadow(pal), pal, floor=62)


def _screen_cool(pal, c):
    # Desaturate + cool the recessed wall so it sheds the warm ochre chroma the
    # FRONT timber keeps — chroma contrast (not just value) is what makes the
    # front lattice advance and the interior read as a hollow behind it.
    return _mix(c, _mix(pal['stone_mid'], (56, 60, 74), 0.6), 0.24)


def _screen_lit(pal):
    # Deep-shadow front of the recessed back-wall — pushed a full stop under the
    # cage poles (and cooled) so the lattice in front always reads as the
    # brighter, warmer, nearer structure, never a co-planar plank.
    return _cap_dark_for_dark_sky(_screen_cool(pal, _shade(_ochre_wood(pal), -52)), pal, floor=54)


def _screen_mid(pal):
    return _cap_dark_for_dark_sky(_screen_cool(pal, _shade(_ochre_wood(pal), -78)), pal, floor=48)


def _screen_shadow(pal):
    return _cap_dark_for_dark_sky(_screen_cool(pal, _shade(_ochre_wood_shadow(pal), -34)), pal, floor=44)


def _lashing(pal):
    return _mix(pal['stone_accent'], (208, 168, 108), 0.58)


def _lashing_core(pal):
    # A bright lit spine down each lath so the 2-px X-weave survives at 58 px
    # over the (now much darker) recessed screen — this is the cue that reads
    # "diagonal trellis," not "speckle on a plank." Capped off pure white.
    return _cap_lit_for_dark_sky(_mix(_lashing(pal), pal['stone_light'], 0.55), pal)


def _edge_rim(pal):
    # Cool 1-px keyline down a shadow-side outline so the airy cage holds its
    # edge against a dark night sky (day palettes never reach this branch).
    return _mix(pal['stone_mid'], pal['stone_light'], 0.5)


def _canvas_lit(pal):
    return _cap_lit_for_dark_sky(_mix(pal['stone_light'], (238, 220, 182), 0.62), pal)


def _canvas_mid(pal):
    return _mix(pal['stone_light'], (214, 192, 150), 0.55)


def _canvas_shadow(pal):
    return _cap_dark_for_dark_sky(_mix(pal['stone_mid'], (150, 122, 84), 0.55), pal, floor=64)


def _batten(pal):
    return _shade(_ochre_wood_shadow(pal), -10)


def _accent(pal):
    return _mix(pal['stone_accent'], (240, 196, 96), 0.6)


# ── The recessed back-screen: the fill spine of the open cage ─────────────────

def _back_screen(surf, cx, top_y, base_y, hw, palette):
    """A dim `_gradient_rect` bamboo screen filling the WHOLE cage column — the
    shadowed far wall of the cage seen through the front lattice. This is what
    guarantees the ~58 px collision column never opens an empty band: it is one
    solid rectangle spanning every row. Left-lit → right-shadow so it reads as a
    curved interior, not a flat plate, and stays a value below the front poles."""
    h = base_y - top_y
    if h < 2 or hw < 2:
        return
    _gradient_rect(surf, pygame.Rect(cx - hw, top_y, hw * 2, h),
                   _screen_lit(palette), _screen_mid(palette),
                   _screen_shadow(palette))
    if _is_dark_sky(palette):
        pygame.draw.line(surf, _edge_rim(palette),
                         (cx + hw - 1, top_y), (cx + hw - 1, base_y - 1), 1)


# ── One bamboo culm (front pole): a lit cylinder with node swellings ──────────

def _culm(surf, x, top_y, base_y, palette, *, w=4, lit_side=True):
    """A vertical bamboo pole as a thin 3-stop cylinder with periodic node ticks
    (the swollen joints). Front poles are lit; a couple of interior poles run
    dimmer so the cage reads with front/back depth."""
    h = base_y - top_y
    if h < 3 or w < 2:
        return
    if lit_side:
        lit, mid, sh = _pole_lit(palette), _pole_mid(palette), _pole_shadow(palette)
    else:
        lit, mid, sh = _pole_mid(palette), _shade(_pole_mid(palette), -18), _pole_shadow(palette)
    _gradient_rect(surf, pygame.Rect(x - w // 2, top_y, w, h), lit, mid, sh)
    # A bright 1-px sun-side keyline on the front corner poles so they pop off
    # the darkened recessed screen and the cage's near verticals stay legible.
    if lit_side:
        pygame.draw.line(surf, _cap_lit_for_dark_sky(_shade(lit, 16), palette),
                         (x - w // 2, top_y), (x - w // 2, base_y - 1), 1)
    # Bamboo node joints — a dark tick with a lit swelling just below, every
    # ~15 px, so the pole reads as segmented culm rather than a plain dowel.
    node = _shade(sh, -14)
    hi = _shade(lit, 12)
    ny = top_y + 8
    while ny < base_y - 3:
        pygame.draw.line(surf, node, (x - w // 2, ny), (x + w // 2 - 1, ny), 1)
        pygame.draw.line(surf, hi, (x - w // 2, ny + 1), (x + w // 2 - 1, ny + 1), 1)
        ny += 15


# ── X-braced lashings between poles ───────────────────────────────────────────

def _lash_bay(surf, xl, xr, y0, y1, palette):
    """One X-brace filling a rectangular bay between two poles, tied with a
    stone_accent lashing knot where the diagonals cross. AA on both diagonals so
    the trellis reads crisp, not jagged."""
    if xr - xl < 6 or y1 - y0 < 6:
        return
    lash = _lashing(palette)
    core = _lashing_core(palette)
    dark = _shade(lash, -46)
    for a, b in (((xl, y0), (xr, y1)), ((xr, y0), (xl, y1))):
        # Each lath is a 2-px lath: a shadow diagonal underneath for round
        # relief, the body lash, then a BRIGHT lit spine one pixel over so the
        # weave survives against the darkened screen at 58 px.
        _aa_polyline(surf, dark, [(a[0], a[1] + 1), (b[0], b[1] + 1)])
        _aa_polyline(surf, lash, [a, b])
        _aa_polyline(surf, core, [(a[0] + 1, a[1]), (b[0] + 1, b[1])])
    mx, my = (xl + xr) // 2, (y0 + y1) // 2
    pygame.draw.circle(surf, dark, (mx, my), 2)
    pygame.draw.circle(surf, core, (mx, my), 1)


# ── The milling-floor band (solid plaster, reinforces the fill) ──────────────

def _floor_band(surf, cx, y, hw, palette, *, seed=0):
    """A bright plaster milling-floor band girdling the cage — a solid
    horizontal volume with a plank shadow line, a bronze rail, and a small lit
    niche so the floor glows warm at night. Also a value anchor that stops the
    airy cage from turning to grey noise against a busy sky."""
    bh = 10 if hw > 18 else 7
    # A bright plaster girdle — lifted well above the cage body value so it
    # reads as a clear light band that breaks the dark block by day, not a dim
    # ledge. Night still capped so the niche/finial carry the silhouette.
    top = _cap_lit_for_dark_sky(_mix(_plaster(palette), palette['stone_light'], 0.5), palette)
    _gradient_rect(surf, pygame.Rect(cx - hw, y - bh, hw * 2, bh),
                   top,
                   _cap_lit_for_dark_sky(_plaster(palette), palette),
                   _cap_dark_for_dark_sky(_shade(palette['stone_mid'], -18), palette, floor=70),
                   vertical=True)
    # Crisp lit top rim so the girdle catches a clean edge highlight by day.
    pygame.draw.line(surf, top, (cx - hw, y - bh + 1), (cx + hw - 1, y - bh + 1), 1)
    # Bronze guard rail along the top lip of the floor + a plank seam beneath.
    pygame.draw.line(surf, _bronze(palette), (cx - hw, y - bh), (cx + hw - 1, y - bh), 1)
    pygame.draw.line(surf, _shade(palette['stone_mid'], -30),
                     (cx - hw + 1, y - 2), (cx + hw - 2, y - 2), 1)
    _tile_hatch(surf, cx - hw + 2, y - bh + 3, cx + hw - 2, y - bh + 3,
                _shade(palette['stone_mid'], -22), step=5)
    if hw > 14:
        _floor_niche(surf, cx, y - bh + 2, max(4, hw // 4), bh - 3, palette)


def _floor_niche(surf, cx, cy, w, h, palette):
    """A warm milling-doorway on the floor band: a dark recess with a thin lit
    rim and a night glow CONTAINED to the recess. The shipped `_lit_niche` fires
    a wide amber halo that clamps to pure white against this brightened plaster,
    so here the warm light is clipped to the dark opening — night floor life,
    no blown highlight leaking onto the plaster."""
    r = pygame.Rect(cx - w, cy, w * 2, h)
    # Dark recess first so the interior sits well below the plaster girdle.
    pygame.draw.rect(surf, _shade(palette['stone_dark'], -8), r)
    if _is_dark_sky(palette) or _is_warming_sky(palette):
        # Warm interior lantern light, clipped to the recess so the additive
        # ramp only ever lands on the DARK opening (never white on plaster).
        prev = surf.get_clip()
        surf.set_clip(r)
        rad = max(2, min(w, h))
        glow = pygame.Surface((rad * 2 + 2, rad * 2 + 2), pygame.SRCALPHA)
        halo = _mix(palette['stone_accent'], (222, 178, 108), 0.66)
        for rr, a in ((rad, 40), (rad * 2 // 3, 70), (rad // 3, 96)):
            pygame.draw.circle(glow, (*halo, a), (rad + 1, rad + 1), max(1, rr))
        surf.blit(glow, (cx - rad - 1, cy + h // 2 - rad - 1),
                  special_flags=pygame.BLEND_RGBA_ADD)
        surf.set_clip(prev)
    # Thin warm rim so the doorway reads at noon and dusk too.
    rim = _mix(palette['stone_accent'], (236, 196, 128), 0.7) if _is_dark_sky(palette) \
        else _mix(palette['stone_mid'], palette['stone_light'], 0.4)
    pygame.draw.rect(surf, rim, r, 1)


# ── One upright battened junk sail ────────────────────────────────────────────

def _junk_sail(surf, x, top_y, bot_y, w, palette, *, near, depth=0.0):
    """A single vertical junk sail: a lit/shadow canvas panel ribbed with full
    horizontal battens (the junk-sail signature), a vermilion leech binding down
    the trailing edge, and reef-stitch texture between battens. `near` sails sit
    brighter; `depth` (0 centre → 1 rim) drags a blade progressively toward the
    canvas shadow so the comb reads as a CURVED bank of blades — the near-front
    centre stays ~204 while the rim blades sink into the ~150s."""
    h = bot_y - top_y
    if h < 6 or w < 3:
        return
    if near:
        lit, mid, sh = _canvas_lit(palette), _canvas_mid(palette), _canvas_shadow(palette)
    else:
        # Far blades are already recessed; `depth` sinks the rim ones further so
        # the value spread near→rim is a full bank, not the ~18 of round 1.
        t = 0.42 + 0.40 * depth
        lit = _mix(_canvas_mid(palette), _canvas_shadow(palette), t)
        mid = _mix(_canvas_mid(palette), _canvas_shadow(palette), min(1.0, t + 0.24))
        sh = _canvas_shadow(palette)
    _gradient_rect(surf, pygame.Rect(x - w // 2, top_y, w, h), lit, mid, sh)
    bat = _batten(palette)
    hi = _shade(lit, 14)
    # Full horizontal battens — the rigid bamboo laths that define a junk sail.
    step = 6 if h > 30 else 5
    by = top_y + step
    while by < bot_y - 1:
        pygame.draw.line(surf, bat, (x - w // 2, by), (x + w // 2 - 1, by), 1)
        pygame.draw.line(surf, hi, (x - w // 2, by - 1), (x + w // 2 - 1, by - 1), 1)
        # Reef-stitch tabling texture just under each batten.
        _tile_hatch(surf, x - w // 2 + 1, by + 1, x + w // 2 - 1, by + 1, bat, step=3)
        by += step
    # Vermilion leech only on the NEAR front blades — a committed hue spark on
    # the crown edge tied to the shipped vermilion; recessed blades drop it so
    # the accent doesn't smear across the whole comb.
    if near:
        pygame.draw.line(surf, _vermilion(palette),
                         (x + w // 2 - 1, top_y), (x + w // 2 - 1, bot_y - 1), 1)
    _aa_polyline(surf, bat, [(x - w // 2, top_y), (x - w // 2, bot_y - 1)])


def _sail_cylinder(surf, cx, top_y, bot_y, hw, palette, n):
    """The upright comb: `n` battened sails fanned as a side-on view of a
    vertical-axis cylinder. Slots are placed by a sine sweep so the edge sails
    foreshorten (narrower + closer + dimmer) toward the rim while the central
    sails stand full and bright — a rotating cylinder of sails, not a flat
    fence. Symmetric about cx (and battens horizontal) so the vertical flip is
    clean. Drawn rim → centre so the near central sails overlap the far ones."""
    half = n // 2
    span_h = bot_y - top_y
    slots = []
    for i in range(-half, half + 1):
        f = i / max(1, half)
        ang = f * math.radians(72)
        x = cx + int(math.sin(ang) * hw)
        fore = math.cos(ang)                     # 1 at centre → foreshorten at rim
        w = max(3, int((hw * 0.34) * fore))
        sh_top = top_y + int((1 - fore) * span_h * 0.16)   # rim sails sit shorter
        sh_bot = bot_y - int((1 - fore) * span_h * 0.10)
        slots.append((abs(i), x, sh_top, sh_bot, w, abs(i) <= 1, abs(f)))
    for _, x, st, sb, w, near, depth in sorted(slots, key=lambda s: -s[0]):
        _junk_sail(surf, x, st, sb, w, palette, near=near, depth=depth)
    # Centred cedar shaft holds the centreline to the finial (the fill spine of
    # the crown) — over the sails so the narrower tower reads IN FRONT of the
    # bladed head, selling the wider-head-on-narrower-tower pivot.
    _gradient_rect(surf, pygame.Rect(cx - 3, top_y, 6, span_h),
                   _mix(_cedar(palette), palette['stone_mid'], 0.35),
                   _cedar(palette), _shade(_cedar(palette), -22))
    # Bronze deck ring the wider sail head rotates on (3-px girdle) + a raised
    # hub boss at cx so the pivot reads as a turning mechanism, not a stack.
    pygame.draw.line(surf, _shade(_bronze(palette), -16), (cx - hw, bot_y + 1), (cx + hw, bot_y + 1), 1)
    pygame.draw.line(surf, _bronze(palette), (cx - hw, bot_y), (cx + hw, bot_y), 1)
    pygame.draw.line(surf, _shade(_bronze(palette), 22), (cx - hw, bot_y - 1), (cx + hw, bot_y - 1), 1)
    pygame.draw.circle(surf, _shade(_bronze(palette), -16), (cx, bot_y - 1), 4)
    pygame.draw.circle(surf, _bronze(palette), (cx, bot_y - 2), 3)
    pygame.draw.circle(surf, _accent(palette), (cx, bot_y - 3), 1)


# ── The candidate ────────────────────────────────────────────────────────────

def _plinth(surf, cx, base_y, hw, palette, *, tiers=3):
    """A 3-layer stone plinth widening downward, each course lit along its top
    edge, so the airy cage lands on a grounded base."""
    widths = [hw + 2, hw + 6, hw + 10][:tiers]
    heights = [3, 3, 4][:tiers]
    y = base_y
    for w, h in zip(widths, heights):
        y0 = y - h
        pygame.draw.rect(surf, _shade(palette['stone_dark'], -12), (cx - w, y0, w * 2, h))
        pygame.draw.line(surf, _cap_lit_for_dark_sky(palette['stone_light'], palette),
                         (cx - w, y0), (cx + w - 1, y0), 1)
        y = y0
    return y


def _draw_one(surf, cx, base_y, top_y, body_w, palette, seed, *, apron=True):
    """One upright junk-sail-mill filling [top_y, base_y]. Height-adaptive:
    short sections drop cage tiers + sail count, but the back-screen + shaft
    always keep the collision column solid."""
    total_h = base_y - top_y
    if total_h < 20:
        return

    cage_hw = max(14, int(body_w * 0.56))        # cage outer poles (fills column)
    crown_hw = int(body_w * 0.72)                # sail cylinder spills to gutters
    TIP_CLEAR = 6                                # keep the finial off the gap rim

    # Atmospheric backlight wedge, then the plinth.
    plinth_widest = cage_hw + 10
    _draw_plinth_mist(surf, cx, base_y, plinth_widest * 2 + 12, palette)

    n_tiers = 3 if total_h > 60 else (2 if total_h > 34 else 1)
    plinth_y = _plinth(surf, cx, base_y, cage_hw, palette, tiers=n_tiers)

    # Crown gets ~40 % of the section (clamped); the cage fills the rest.
    crown_h = int(min(max(total_h * 0.40, 22), 132))
    shoulder_y = top_y + crown_h                 # top of the cage / deck ring
    cage_top = shoulder_y
    cage_base = plinth_y

    # 1) Fill spine: the recessed back-screen across the whole cage column.
    _back_screen(surf, cx, cage_top, cage_base, cage_hw, palette)

    # 2) Front lattice: X-braced lashings tier by tier BETWEEN the poles.
    cage_h = cage_base - cage_top
    n_bays = max(1, min(5, cage_h // 30))
    inner_l, inner_r = cx - cage_hw + 3, cx + cage_hw - 3
    for k in range(n_bays):
        y0 = cage_top + int(cage_h * k / n_bays)
        y1 = cage_top + int(cage_h * (k + 1) / n_bays)
        _lash_bay(surf, inner_l, inner_r, y0 + 1, y1 - 1, palette)
        # An interior vertical brace pole per bay junction gives the trellis a
        # midrib and keeps the front lattice reading dense over the centre.
        pygame.draw.line(surf, _shade(_pole_mid(palette), -8), (cx, y0), (cx, y1), 1)

    # 3) Front poles: two lit corner culms + two dimmer interior culms.
    _culm(surf, cx - cage_hw + 2, cage_top, cage_base, palette, w=4, lit_side=True)
    _culm(surf, cx + cage_hw - 2, cage_top, cage_base, palette, w=4, lit_side=True)
    _culm(surf, cx - cage_hw // 2, cage_top, cage_base, palette, w=3, lit_side=False)
    _culm(surf, cx + cage_hw // 2, cage_top, cage_base, palette, w=3, lit_side=False)

    # 4) Solid plaster milling-floor band low in the cage.
    if cage_h > 22:
        _floor_band(surf, cx, cage_base - int(cage_h * 0.30), cage_hw - 1, palette, seed=seed)

    # 5) The upright junk-sail cylinder crowning the cage.
    n_sails = 7 if crown_h > 74 else (5 if crown_h > 44 else 3)
    sail_top = top_y + TIP_CLEAR + 4
    _sail_cylinder(surf, cx, sail_top, shoulder_y, crown_hw, palette, n_sails)

    # 6) Bronze cap ring + finial with a night halo at the gap tip. The halo is
    # laid FIRST (additive onto the dark sky), then the opaque finial sits over
    # it — so the centre is controlled bronze, not a bronze+halo stack that blew
    # to pure white in round 1. The glow reads as a warm lantern (<~235).
    tip_y = top_y + TIP_CLEAR
    if _is_dark_sky(palette) or _is_warming_sky(palette):
        r = 12 if _is_dark_sky(palette) else 5
        glow = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        halo = _mix(palette['stone_accent'], (232, 202, 140), 0.72)
        # Normal (non-additive) alpha blend: the result can never exceed the
        # halo colour, so the warm point-source stays a capped lantern and can
        # NOT blow to pure white over the bright bronze hub the way an additive
        # ramp did — the restrained halo FIX 5 asked for.
        for rr, a in ((r, 60), (r * 2 // 3, 120), (r // 3, 190)):
            pygame.draw.circle(glow, (*halo, a), (r + 1, r + 1), max(1, rr))
        surf.blit(glow, (cx - r - 1, tip_y - r - 1))
    pygame.draw.circle(surf, _shade(_bronze(palette), -18), (cx, tip_y + 2), 3)
    pygame.draw.circle(surf, _bronze(palette), (cx, tip_y + 1), 2)
    pygame.draw.circle(surf, _accent(palette), (cx, tip_y), 1)

    if apron:
        draw_grass_bed(surf, cx, base_y - 1, plinth_widest * 2, 14, palette, seed=seed)
        draw_side_shrub(surf, cx - plinth_widest - 2, base_y - 1, palette, scale=0.95)
        draw_side_shrub(surf, cx + plinth_widest + 2, base_y - 1, palette, scale=0.85)


def candidate_junk_sail_mill(surf, top_rect, bot_rect, palette, seed):
    bcx = bot_rect.x + bot_rect.width // 2
    tcx = top_rect.x + top_rect.width // 2

    if bot_rect.height > 24:
        _draw_one(surf, bcx, bot_rect.bottom, bot_rect.y,
                  bot_rect.width, palette, seed, apron=True)

    if top_rect.height > 24:
        # Structural mirror: draw upright into a temp, flip vertically, hang from
        # the ceiling. Shaft centred + battens horizontal + symmetric sail sweep
        # → the flipped comb points cleanly into the gap.
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
SEED = 13

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
    candidate_junk_sail_mill(surf, top_rect, bot_rect, pal, SEED)
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


def _measure_clearance(pal):
    surf = _pair_surf(pal)
    cx = MARGIN + PIPE_W // 2
    gutter = lambda x: abs(x - cx) > PIPE_W // 2 + 2
    # Both scan from the gap rim toward each section so we read the SAIL-TIP
    # clearance (the crown sits at the gap end), not the ceiling/ground plinth.
    top_tip = 0
    for y in range(min(TOP_H + 4, GROUND_Y - 1), -1, -1):
        if any(gutter(x) and surf.get_at((x, y))[3] > 50 for x in range(CACHE_W)):
            top_tip = y
            break
    bot_high = GROUND_Y
    for y in range(BOT_TOP - 8, GROUND_Y):
        if any(gutter(x) and surf.get_at((x, y))[3] > 50 for x in range(CACHE_W)):
            bot_high = y
            break
    return TOP_H - top_tip, bot_high - BOT_TOP


def _measure_center_cover(pal):
    """Mirrored-centreline coverage: fraction of the central 8-px band rows (over
    both hung + rising sections) that carry fill — proves the flip reads solid."""
    surf = _pair_surf(pal)
    cx = MARGIN + PIPE_W // 2
    xs = range(cx - 4, cx + 5)
    rows = filled = 0
    for y in list(range(6, TOP_H)) + list(range(BOT_TOP, GROUND_Y - 6)):
        rows += 1
        if any(surf.get_at((x, y))[3] > 50 for x in xs):
            filled += 1
    return filled / max(1, rows)


def _measure_fill(pal, section_h):
    surf = pygame.Surface((CACHE_W, GROUND_Y), pygame.SRCALPHA)
    bot_rect = pygame.Rect(MARGIN, GROUND_Y - section_h, PIPE_W, section_h)
    candidate_junk_sail_mill(surf, pygame.Rect(MARGIN, 0, PIPE_W, 0),
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
    candidate_junk_sail_mill(surf, pygame.Rect(MARGIN, 0, PIPE_W, 0),
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
    candidate_junk_sail_mill(surf, pygame.Rect(MARGIN, 0, PIPE_W, 0),
                             bot_rect, pal, SEED)
    crop_top = GROUND_Y - section_h - 12
    crop = surf.subsurface(pygame.Rect(0, crop_top, CACHE_W, section_h + 12)).copy()
    mask = pygame.mask.from_surface(crop, 60)
    return mask.to_surface(setcolor=(18, 18, 22, 255),
                           unsetcolor=(232, 232, 236, 255))


def _lum(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def _screen_vs_timber_gap(pal):
    """DAY value gap between the recessed back-screen and the lit front timber —
    the number that proves the cage reads as a hollow behind the lattice rather
    than a co-planar plank. Compares the screen mid stop to the lit corner culm
    and the bright lash core (the two brightest front cues)."""
    screen = _lum(_screen_mid(pal))
    pole = _lum(_pole_lit(pal))
    core = _lum(_lashing_core(pal))
    return screen, pole, core


def main():
    pygame.init()
    pygame.display.set_mode((1, 1))
    day = biome.palette_for_phase(PHASE_DAY)
    night = biome.palette_for_phase(PHASE_NIGHT)

    pair_day = _render_pair(day)
    pair_night = _render_pair(night)
    cl_day = _measure_clearance(day)
    cl_night = _measure_clearance(night)
    cover_day = _measure_center_cover(day)
    cover_night = _measure_center_cover(night)

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

    sheet.blit(title.render("junk-sail-mill — round 2", True, (245, 240, 230)), (pad, 12))
    sheet.blit(sub.render("open bamboo LATTICE cage + upright battened junk-sail "
                          "cylinder  ·  mirrored pair, true gap, day + night", True,
                          (170, 172, 182)), (pad, 40))

    for i, (pair, name, cl, cov) in enumerate((
            (pair_day, f"DAY  PHASE={PHASE_DAY}", cl_day, cover_day),
            (pair_night, f"NIGHT  PHASE={PHASE_NIGHT}", cl_night, cover_night))):
        hx = pad + i * (pw + pad)
        hy = title_h
        sheet.blit(pair, (hx, hy))
        pygame.draw.rect(sheet, (60, 62, 72), (hx, hy, pw, ph), 1)
        lab = label.render(name, True, (255, 224, 150))
        sheet.blit(lab, (hx + (pw - lab.get_width()) // 2, hy + ph + 3))
        cl2 = sub.render(f"tip clear top {cl[0]} bot {cl[1]}px  ·  centre cover "
                         f"{cov*100:.0f}%", True, (200, 202, 212))
        sheet.blit(cl2, (hx + (pw - cl2.get_width()) // 2, hy + ph + 21))

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
        lab = label.render(f"{h}px  ·  max empty run {fills[h]}px", True, (210, 212, 222))
        sheet.blit(lab, (fx, fy + ch + 3))
        fy += ch + label_h + pad

    out = _REPO / "docs" / "pillar_landmarks" / "windmills" / "junk-sail-mill" / "round_2.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(sheet, out)
    scr, pole, core = _screen_vs_timber_gap(day)
    print(f"wrote {out}  ({sheet.get_width()}x{sheet.get_height()})")
    print(f"clearance day  top={cl_day[0]}px bot={cl_day[1]}px  centre-cover={cover_day*100:.1f}%")
    print(f"clearance night top={cl_night[0]}px bot={cl_night[1]}px  centre-cover={cover_night*100:.1f}%")
    print(f"max empty run: " + "  ".join(f"{h}px->{fills[h]}px" for h in heights))
    print(f"DAY value gap: back-screen lum={scr:.0f}  front-culm lum={pole:.0f} "
          f"(+{pole-scr:.0f})  lash-core lum={core:.0f} (+{core-scr:.0f})")


if __name__ == "__main__":
    main()
