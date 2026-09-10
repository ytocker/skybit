"""angkor_lotus — high-fidelity Angkor Wat central-sanctuary tower (candidate).

The SE-Asia HISTORIC pole of the far-east-landmarks family: the central
prasat of Angkor Wat rendered as a single grey-gold sandstone LOTUS BUD — a
tower whose profile SWELLS in its lower third (the bud's shoulder) then curves
in an OGIVAL taper to a pointed lotus finial, its corners REDENTED (stepped
re-entrant angles) so the silhouette is a serrated, scalloped tiered cone, not
a smooth spike. It rises from a broad stepped-square pyramid base with a steep
central stairway.

The make-or-break tell that keeps it OFF the game's Wat Arun prang and off the
pagoda cones: it is NOT the prang's smooth 1.5px-rippled corncob and NOT a
stack of flaring eaves. It is a BULGING lotus-bud whose every false-storey
throws a projecting cornice ledge OUT past the wall — a blocky, stepped,
serrated edge — over a bare-stone (no porcelain, no gilt tiers) body, grounded
on an unmistakably stepped square base. Swap-test proof: paint it white and it
is still a redented lotus-bud cone, never Himeji's gabled pyramid nor a prang.

Every material is `_mix(palette[key], anchor, t)` off the shipped pagoda
helpers with a lit/mid/shadow triad, so the 5-min biome day->night retint
sweeps straight through. Standalone review candidate; wires nothing live.

Run:  python docs/pillar_landmarks/far_east_landmarks/angkor_lotus/render.py
Out:  docs/pillar_landmarks/far_east_landmarks/angkor_lotus/round_2.png
"""
from __future__ import annotations

import math
import os
import pathlib
import random
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

_REPO = pathlib.Path(__file__).resolve().parents[4]
sys.path.insert(0, str(_REPO))

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game.config import GROUND_Y, PIPE_W
from game import biome

# Real pagoda helpers — same materials + lighting language as the shipped
# pillars. `_prang_corncob` is imported as the notched-lobed-spire REFERENCE;
# this candidate shapes a bulging lotus-bud, not the Thai prang.
from game.pillar_pagodas import (
    _mix, _shade, _gradient_rect, _aa_polyline, _lit_niche, _tile_hatch,
    _prang_corncob, _mosaic_lozenges, _draw_plinth_mist,
    _is_dark_sky, _is_warming_sky, _cap_lit_for_dark_sky, _cap_dark_for_dark_sky,
    _korean_granite, _terracotta, _gold_bright, _bronze,
    _gold_deep, _vermilion, _porcelain_aqua,
    _basalt, _basalt_lit, _basalt_shadow,
)
from game.pillar_variants import draw_grass_bed
from game.draw import draw_side_shrub


MARGIN = 64                       # matches entities.Pipe eave/ornament gutter
CACHE_W = PIPE_W + MARGIN * 2
CACHE_H = GROUND_Y
PHASE_DAY = 0.30                  # midday tan sky — hardest test for grey-gold hold
PHASE_NIGHT = 0.85               # deep night — checks night rim + finial gleam


# ── Materials ────────────────────────────────────────────────────────────────
#
# Weathered Khmer sandstone: a warm pale GREY-GOLD. `_korean_granite` (the
# warmest pale stone in the shipped set) warmed a stop toward `_terracotta`'s
# clay so it reads as sun-baked sandstone, NOT the porcelain/gilt of Wat Arun
# nor the bone-white of Himeji/Potala. All three stops are palette-derived so
# the biome retint carries; the fixed anchors only fix the archetype hue.

# ── Colorways ────────────────────────────────────────────────────────────────
#
# The tower's GEOMETRY (silhouette, redent, bud profile, ledges, fill, mirror) is
# shared and frozen; a colorway ONLY swaps the anchors/palette-keys the body triad
# mixes toward. Every triad keeps the `_mix(palette[key], anchor, t)` + lit/mid/
# shadow discipline so each colorway still retints straight through the 5-min
# day->night biome sweep — the fixed RGB anchors pin the stone's ARCHETYPE hue,
# they never freeze it to a raw fill. `_COLORWAY` is set+restored by each wrapper
# candidate below; None keeps the original grey-gold sandstone.

_COLORWAY = None


def _triad_sandstone(palette):
    mid = _mix(_korean_granite(palette), _terracotta(palette), 0.26)   # grey-gold
    lit = _mix(palette['stone_light'], (224, 208, 170), 0.60)          # sunlit face
    sh = _shade(_mix(palette['stone_dark'], (98, 86, 66), 0.80), -4)   # recess
    return lit, mid, sh


def _triad_rose(palette):
    # Banteay Srei pink-red sandstone — the body is warmed off the grey-gold
    # granite toward a clay-rose so it reads as the famous rosy Khmer stone.
    rose = _mix(_terracotta(palette), (200, 118, 110), 0.62)
    mid = _mix(_korean_granite(palette), rose, 0.44)
    lit = _mix(palette['stone_light'], (236, 182, 166), 0.60)
    sh = _shade(_mix(palette['stone_dark'], (124, 66, 60), 0.80), -4)
    return lit, mid, sh


def _triad_basalt(palette):
    # Weathered volcanic basalt — cool near-black andesite off the shipped
    # Borobudur triple, a brooding tower that stays legible against any sky.
    lit = _basalt_lit(palette)
    mid = _basalt(palette)
    sh = _shade(_basalt_shadow(palette), -6)
    return lit, mid, sh


def _triad_jade(palette):
    # Jungle-reclaimed jade-green overgrown stone (Ta Prohm mood) — the body is
    # pulled to a mossy green, lit with a wet porcelain-aqua sheen.
    mid = _mix(palette['stone_mid'], (70, 118, 82), 0.55)
    lit = _mix(_porcelain_aqua(palette), (170, 204, 158), 0.52)
    sh = _shade(_mix(palette['stone_dark'], (36, 72, 48), 0.82), -4)
    return lit, mid, sh


def _triad_gilt(palette):
    # Gilded gold-leaf sanctuary — a golden prasat that gleams at night; body is
    # the shipped Shwedagon gilt graded lit-bright -> deep-gold in the recesses.
    lit = _gold_bright(palette)
    mid = _mix(_gold_bright(palette), _gold_deep(palette), 0.50)
    sh = _shade(_gold_deep(palette), -8)
    return lit, mid, sh


def _triad_sunset(palette):
    # Warm laterite at golden hour — red-ochre body off terracotta pushed toward
    # the festival vermilion so the tower glows sunset-warm.
    mid = _mix(_terracotta(palette), _vermilion(palette), 0.42)
    lit = _mix(palette['stone_light'], (238, 166, 108), 0.62)
    sh = _shade(_mix(palette['stone_dark'], (118, 54, 34), 0.82), -4)
    return lit, mid, sh


_TRIADS = {
    None: _triad_sandstone,
    'rose': _triad_rose,
    'basalt': _triad_basalt,
    'jade': _triad_jade,
    'gilt': _triad_gilt,
    'sunset': _triad_sunset,
}


def _sandstone_triad(palette):
    lit, mid, sh = _TRIADS.get(_COLORWAY, _triad_sandstone)(palette)
    # Same dark-sky legibility caps for every colorway so night never blows the
    # lit face out nor sinks the recess to pure black.
    lit = _cap_lit_for_dark_sky(lit, palette, cap=214)
    sh = _cap_dark_for_dark_sky(sh, palette, floor=44)
    return lit, mid, sh


def _moss(palette):
    # Green-black moss/lichen stain that pools in the carved recesses — pulls
    # `foliage_dark` toward `stone_dark` so the stain reads as weathering, not
    # a bright leaf. Per-colorway the stain re-tints to suit the stone.
    if _COLORWAY == 'jade':
        # Jungle-reclaimed: a heavier, greener overgrowth stain.
        return _mix(palette['foliage_dark'], (56, 104, 64), 0.58)
    if _COLORWAY == 'gilt':
        # Bronze relief pooling in the recesses instead of moss.
        return _bronze(palette)
    if _COLORWAY == 'basalt':
        # Cool grey lichen on the near-black stone.
        return _mix(palette['foliage_dark'], palette['stone_mid'], 0.42)
    return _mix(palette['foliage_dark'], palette['stone_dark'], 0.48)


def _lum(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


# ── Lotus-bud silhouette maths ───────────────────────────────────────────────
#
# The two tells the AD flagged: (1) a BULGING profile — swells in the lower
# third then OGIVAL-tapers to a point; (2) REDENTED corners — a scalloped,
# stepped OUTLINE, not just surface ribs. `_bud_env` is the smooth bulge; each
# false-storey then throws a projecting cornice ledge OUT past its wall, which
# is what turns the outline serrated/scalloped.

_U_TOP = 0.90                     # bud is drawn to here; finial caps the last 10%
_CORNICE = max(3.0, PIPE_W * 0.5 * 0.18)   # px the storey ledge juts past the wall
_TIER_PX = 12                     # px per false-storey -> readable flat-step cadence

# A real prasat bud WAISTS at the base cornice and BULGES to a fat shoulder in
# its lower third before tucking to a point. `_NECK` seats the bulb on the base;
# `_SHOULDER` is the widest swell; the shoulder sits in the lower third so the
# profile reads bulb-bottomed / pinched-top — a bud you could name cold, never
# a serrated straight cone.
_NECK = 0.80
_SHOULDER = 1.04
_SHOULDER_U = 0.28


def _bud_env(u):
    """Lotus-bud OGIVAL envelope, u=0 at the waisted base neck, u=1 at the
    finial tip. Pinches at the neck, swells (as a rounded rise, not a straight
    ramp) to a fat shoulder in the lower third, then tucks in FIRMLY to a point
    — the bulb/beehive profile no pagoda or prang shares."""
    if u <= 0.0:
        return _NECK                       # waist — the bulb seats on the base
    if u < _SHOULDER_U:
        # Rounded swell neck -> fat shoulder (sine easing bulges, not flares).
        s = math.sin((u / _SHOULDER_U) * (math.pi / 2))
        return _NECK + (_SHOULDER - _NECK) * s
    v = (u - _SHOULDER_U) / (1.0 - _SHOULDER_U)
    # Ogival body: holds full through the shoulder, then a firm high-exponent
    # tuck (steeper than a cone) pinches the outline decisively to the finial.
    return max(0.0, _SHOULDER * (1.0 - v ** 2.4) ** 0.72)


def _redent_hw(u, max_hw, n_tiers):
    """Half-width of the redented silhouette at bud-parameter u. The smooth bud
    envelope, minus a per-storey inward taper, PLUS a projecting cornice ledge
    at the base of each storey — the ledge is what makes the outline step OUT
    then tuck IN (the redented, scalloped edge)."""
    env = _bud_env(u) * max_hw
    seg = u * n_tiers
    u_tier = seg - int(seg)
    # Each false-storey steps IN ~16% from its cornice up to its top course.
    w = env * (1.0 - 0.16 * u_tier)
    # Flat projecting cornice ledge across the lower ~45% of every storey — a
    # chunky RECTANGULAR step (not a soft rib) that holds a readable flat ledge
    # instead of a high-frequency in/out ripple, so the silhouette reads as a
    # stack of blocky redented ledges, never the prang's fine corncob.
    if u_tier < 0.45:
        w += _CORNICE
    return w


def _grad_hspan(surf, y, xl, xr, lit, mid, sh):
    """One body row: horizontal 3-stop gradient, lit on the LEFT / shadow on the
    RIGHT — the raking-light model that reads the tower as a round stone mass."""
    w = xr - xl
    if w < 2:
        if w == 1:
            surf.set_at((xl, y), mid)
        return
    for i in range(w):
        t = i / (w - 1)
        col = _mix(lit, mid, t * 2) if t < 0.5 else _mix(mid, sh, (t - 0.5) * 2)
        surf.set_at((xl + i, y), col)


# ── The bud body ─────────────────────────────────────────────────────────────

def _draw_bud(surf, cx, bud_bot, bud_top, max_hw, palette, rng):
    """The redented lotus-bud tower between bud_bot (widest shoulder region) and
    bud_top (the chunky start of the finial). Per-row sandstone gradient inside
    the redented outline, storey cornices with carved dentil courses, vertical
    redent pilaster grooves, moss in the recesses, an AA keyline + a night rim."""
    lit, mid, sh = _sandstone_triad(palette)
    moss = _moss(palette)
    dark_sky = _is_dark_sky(palette)
    bud_h = bud_bot - bud_top
    if bud_h < 8:
        return
    # One false-storey per ~12 px so a tall tower gets MORE stepped tiers, not a
    # longer smooth cone. Floored so each ledge stays a readable flat step (a
    # ~58px bud lands ~5-6 clean cornices), never a fuzzy high-frequency edge.
    n_tiers = max(4, bud_h // _TIER_PX)

    left_pts = []
    right_pts = []
    tier_seams = []                      # (y, hw) rows where a cornice sits
    for y in range(bud_top, bud_bot):
        u = (bud_bot - y) / bud_h * _U_TOP
        hw = _redent_hw(u, max_hw, n_tiers)
        xl = int(round(cx - hw))
        xr = int(round(cx + hw))
        _grad_hspan(surf, y, xl, xr, lit, mid, sh)
        left_pts.append((xl, y))
        right_pts.append((xr, y))
        seg = u * n_tiers
        u_tier = seg - int(seg)
        if u_tier < (1.0 / bud_h * _U_TOP * n_tiers) + 0.02:
            tier_seams.append((y, hw))

    # ── Redent pilaster grooves: a central projecting bay + a flanking recess
    #    each side, run vertically so the FACE reads redented too (re-entrant
    #    stepped corners), not just the outline. Shadow groove + lit rib edge.
    for frac in (0.30, 0.62):
        for y0, hw in tier_seams:
            gx_l = int(cx - hw * frac)
            gx_r = int(cx + hw * frac)
            # short vertical grooves down from each cornice into the storey
            gl = max(6, int(bud_h / max(1, n_tiers)) - 2)
            for gy in range(y0, min(bud_bot, y0 + gl)):
                if 0 <= gx_l < surf.get_width():
                    surf.set_at((gx_l, gy), _shade(sh, -14))
                    surf.set_at((gx_l + 1, gy), _shade(lit, 8))
                if 0 <= gx_r < surf.get_width():
                    surf.set_at((gx_r, gy), _shade(sh, -14))
                    surf.set_at((gx_r - 1, gy), _shade(lit, 8))
    # Central lit spine — the projecting central bay catches the most light.
    for y0, hw in tier_seams:
        gl = max(6, int(bud_h / max(1, n_tiers)) - 2)
        for gy in range(y0, min(bud_bot, y0 + gl)):
            surf.set_at((cx, gy), _shade(lit, 12))

    # ── Storey cornices: a lit nosing over a shadow ledge, with a carved dentil
    #    course of `_tile_hatch` marks — the horizontal reading of the graduated
    #    tiers. Drawn after the body so they crown each storey.
    for y0, hw in tier_seams:
        x0 = int(cx - hw)
        x1 = int(cx + hw)
        pygame.draw.line(surf, _shade(sh, -16), (x0, y0 + 1), (x1, y0 + 1), 1)
        pygame.draw.line(surf, _shade(lit, 18), (x0, y0), (x1, y0), 1)
        _tile_hatch(surf, x0 + 2, y0, x1 - 2, y0, _shade(sh, -10), step=4)

    # ── Moss/lichen stain pooling low + in the shadow (right) flank.
    for _ in range(max(6, bud_h // 5)):
        my = rng.randint(bud_top + 2, bud_bot - 2)
        u = (bud_bot - my) / bud_h * _U_TOP
        hw = _redent_hw(u, max_hw, n_tiers)
        # bias toward the shaded right flank + the base
        bias = rng.random() * rng.random()
        mx = int(cx + hw * (0.2 + 0.7 * bias))
        low = (bud_bot - my) / bud_h < 0.5
        if 0 <= mx < surf.get_width() and (low or rng.random() < 0.5):
            surf.set_at((mx, my), moss)

    # ── AA silhouette keyline + day/night edge treatment.
    outline = left_pts + list(reversed(right_pts))
    _aa_polyline(surf, _shade(sh, -20), outline, closed=True)
    if not dark_sky:
        # Day: thicken the shadow (right) edge so the grey-gold holds against the
        # tan/blue crossover sky.
        key = _shade(sh, -24)
        for x, y in right_pts:
            if 0 <= x - 1 < surf.get_width():
                surf.set_at((x - 1, y), key)
    else:
        # Night: warm rim down the lit (left) edge so the bud keeps its scalloped
        # silhouette against a dark sky.
        rim = _shade(lit, 40)
        for i in range(0, len(left_pts), 1):
            x, y = left_pts[i]
            if 0 <= x < surf.get_width():
                surf.set_at((x, y), rim)


# ── Lotus finial — chunky, symmetric, presents a solid gap-rim edge ──────────

def _draw_finial(surf, cx, base_y, tip_y, half_at_base, palette):
    """The pointed lotus-bud finial capping the tower. A short stack of lotus
    petals swelling from the bud's chunky top, then a pointed bud + a small
    gilt bead. Kept broad at its base (not a thin spike beside empty air) so
    the gap-rim presentation stays solid; a night gleam is gated on dark sky."""
    lit, mid, sh = _sandstone_triad(palette)
    gold = _gold_bright(palette)
    dark_sky = _is_dark_sky(palette)
    h = base_y - tip_y
    if h < 6:
        return
    hb = max(4, int(half_at_base))
    # Lotus-petal collar: a fat rounded base swelling then pinching — three
    # stacked petal rings so it reads as a bud, not a cone tip.
    collar_top = tip_y + int(h * 0.42)
    left = []
    right = []
    for y in range(base_y, collar_top, -1):
        t = (base_y - y) / max(1, base_y - collar_top)
        # swell out slightly then pull in (petal shoulder)
        env = hb * (1.0 + 0.16 * math.sin(t * math.pi) - 0.55 * t)
        hw = max(1.0, env)
        xl = int(round(cx - hw))
        xr = int(round(cx + hw))
        _grad_hspan(surf, y, xl, xr, lit, mid, sh)
        left.append((xl, y))
        right.append((xr, y))
    # Petal seams — three vertical grooves fanning up the collar.
    for frac in (-0.5, 0.0, 0.5):
        for y in range(collar_top, base_y):
            t = (base_y - y) / max(1, base_y - collar_top)
            env = hb * (1.0 + 0.16 * math.sin(t * math.pi) - 0.55 * t)
            gx = int(cx + env * frac)
            if 0 <= gx < surf.get_width():
                surf.set_at((gx, y), _shade(sh, -12))
    # Pointed bud spike above the collar — a narrow ogive to the tip.
    top_hw = max(2, int(hb * 0.5))
    spike = [(cx - top_hw, collar_top), (cx, tip_y),
             (cx + top_hw, collar_top)]
    pygame.draw.polygon(surf, mid, spike)
    _aa_polyline(surf, _shade(sh, -18),
                 [(cx - top_hw, collar_top), (cx, tip_y),
                  (cx + top_hw, collar_top)])
    pygame.draw.line(surf, _shade(lit, 16), (cx, tip_y),
                     (cx, collar_top - 1), 1)
    # AA keyline on the collar + a gilt bead crown.
    _aa_polyline(surf, _shade(sh, -18), left + list(reversed(right)))
    pygame.draw.circle(surf, gold, (cx, collar_top - 1), 2)
    pygame.draw.circle(surf, _shade(gold, -50), (cx, collar_top - 1), 2, 1)

    if dark_sky:
        # Night gleam — a small additive gold halo on the finial bead.
        g = pygame.Surface((18, 18), pygame.SRCALPHA)
        for rr, a in ((8, 40), (5, 80), (2, 150)):
            pygame.draw.circle(g, (*gold, a), (9, 9), rr)
        surf.blit(g, (cx - 9, collar_top - 1 - 9),
                  special_flags=pygame.BLEND_RGBA_ADD)


# ── Stepped square base + steep central stair ────────────────────────────────

def _draw_base(surf, cx, base_top, base_bot, half, palette, rng):
    """The broad stepped-square pyramid the prasat stands on — three receding
    masonry tiers widening to fill the column bottom, each with a lit cornice
    nosing + carved dentil course, and a steep recessed central stairway. This
    stepped foot is what separates the tower from a bare pagoda cone."""
    lit, mid, sh = _sandstone_triad(palette)
    moss = _moss(palette)
    nb = 3
    bh = base_bot - base_top
    tier_h = max(3, bh // nb)
    for i in range(nb):
        t = i / (nb - 1) if nb > 1 else 0.0
        # Bottom tier widest (spills a touch into the gutter), receding up.
        w = int((half * 2) * (1.06 - 0.12 * t))
        ty = base_bot - (i + 1) * tier_h
        r = pygame.Rect(cx - w // 2, ty, w, tier_h)
        _gradient_rect(surf, r, lit, mid, sh)
        pygame.draw.line(surf, _shade(lit, 18), (r.x, r.y), (r.right - 1, r.y), 1)
        pygame.draw.line(surf, _shade(sh, -16),
                         (r.x, r.bottom - 1), (r.right - 1, r.bottom - 1), 1)
        _tile_hatch(surf, r.x + 2, r.y, r.right - 2, r.y, _shade(sh, -10), step=4)
        _aa_polyline(surf, _shade(sh, -18),
                     [(r.x, r.bottom), (r.x, r.y),
                      (r.right - 1, r.y), (r.right - 1, r.bottom)])
        for _ in range(max(3, w // 6)):
            mx = rng.randint(r.x + 1, r.right - 2)
            my = rng.randint(r.y + 1, r.bottom - 1)
            if rng.random() < 0.5:
                surf.set_at((mx, my), moss)

    # Steep central stairway — a recessed channel with close-set tread nosings.
    sw = max(6, int(half * 0.62))
    sx = cx - sw // 2
    stair_top = base_bot - nb * tier_h
    for sy in range(stair_top + 2, base_bot, 3):
        pygame.draw.line(surf, _shade(sh, -22), (sx, sy), (sx + sw, sy), 1)
        pygame.draw.line(surf, _shade(lit, 10), (sx, sy - 1), (sx + sw, sy - 1), 1)
    pygame.draw.line(surf, _shade(sh, -24), (sx, stair_top), (sx, base_bot), 1)
    pygame.draw.line(surf, _shade(sh, -24),
                     (sx + sw, stair_top), (sx + sw, base_bot), 1)


# ── 3-layer plinth ───────────────────────────────────────────────────────────

def _draw_plinth(surf, cx, base_y, half, palette):
    lit, mid, sh = _sandstone_triad(palette)
    layers = 3
    for i in range(layers):
        lw = int(half * 2 * (1.14 + 0.16 * i))
        lh = 4
        ly = base_y - (layers - i) * lh
        r = pygame.Rect(cx - lw // 2, ly, lw, lh)
        _gradient_rect(surf, r, lit, mid, sh)
        pygame.draw.line(surf, _shade(sh, -18),
                         (r.x, r.bottom - 1), (r.right - 1, r.bottom - 1), 1)
        pygame.draw.line(surf, _shade(lit, 16), (r.x, r.y), (r.right - 1, r.y), 1)


# ── One upright tower ────────────────────────────────────────────────────────

def _draw_tower(surf, cx, y_top, y_bot, palette, seed):
    """mist -> plinth -> foliage -> stepped base -> redented lotus-bud ->
    pointed lotus finial. Height-adaptive: the bud keeps a constant stepped-
    storey cadence so 70/210/355 px sections all read as the same landmark."""
    rng = random.Random(seed)
    half = PIPE_W // 2
    section_h = y_bot - y_top

    plinth_h = min(11, max(6, int(section_h * 0.06)))
    finial_h = min(20, max(11, int(section_h * 0.11)))
    base_h = min(int(section_h * 0.42), max(22, int(section_h * 0.30)))
    base_y = y_bot

    _draw_plinth_mist(surf, cx, base_y - plinth_h + 2,
                      int(half * 2 * 1.6), palette)
    _draw_plinth(surf, cx, base_y, half, palette)

    base_bot = base_y - plinth_h
    base_top = base_bot - base_h
    _draw_base(surf, cx, base_top, base_bot, half, palette, rng)

    max_hw = half - 2
    bud_bot = base_top + 2
    bud_top = y_top + finial_h
    if bud_bot - bud_top < 10:
        bud_top = bud_bot - 10
    _draw_bud(surf, cx, bud_bot, bud_top, max_hw, palette, rng)

    # The finial caps the last stretch; its base half-width matches the bud's
    # chunky top so the join is seamless and the gap-rim edge stays solid.
    top_hw = _redent_hw(_U_TOP, max_hw, max(4, (bud_bot - bud_top) // _TIER_PX))
    _draw_finial(surf, cx, bud_top, y_top + 2, top_hw, palette)

    draw_grass_bed(surf, cx, base_y - 1, PIPE_W + 12, 12, palette, seed=seed)
    draw_side_shrub(surf, cx - half - 6, base_y - 1, palette, scale=0.9)
    draw_side_shrub(surf, cx + half + 6, base_y - 1, palette, scale=0.8)


def candidate_angkor_lotus(surf, top_rect, bot_rect, palette, seed):
    """Bottom = the prasat rising from the ground, lotus finial reaching the
    gap. Top = the same tower vertical-FLIPPED from the ceiling — a near-
    symmetric bud whose finial hangs into the gap, so both tips meet at the rim
    with a clean sky sliver between them."""
    if bot_rect.height > 0:
        _draw_tower(surf, bot_rect.centerx, bot_rect.y, bot_rect.bottom,
                    palette, seed)
    if top_rect.height > 0:
        tmp = pygame.Surface((surf.get_width(), top_rect.height), pygame.SRCALPHA)
        _draw_tower(tmp, top_rect.centerx, 0, top_rect.height, palette, seed + 1)
        surf.blit(pygame.transform.flip(tmp, False, True), (0, top_rect.y))


# ── Colorway wrappers ────────────────────────────────────────────────────────
#
# Each sets the module colorway, draws the SHARED geometry, then restores the
# previous colorway (so nested/interleaved draws never leak a colour). Geometry
# is byte-identical to `candidate_angkor_lotus`; only the material triad changes.

def _draw_colorway(name, surf, top_rect, bot_rect, palette, seed):
    global _COLORWAY
    prev = _COLORWAY
    _COLORWAY = name
    try:
        candidate_angkor_lotus(surf, top_rect, bot_rect, palette, seed)
    finally:
        _COLORWAY = prev


def candidate_angkor_rose(surf, top_rect, bot_rect, palette, seed):
    """Warm ROSE sandstone — the pink-red Khmer stone of Banteay Srei."""
    _draw_colorway('rose', surf, top_rect, bot_rect, palette, seed)


def candidate_angkor_basalt(surf, top_rect, bot_rect, palette, seed):
    """Dark volcanic BASALT — a brooding, near-black weathered-stone tower."""
    _draw_colorway('basalt', surf, top_rect, bot_rect, palette, seed)


def candidate_angkor_jade(surf, top_rect, bot_rect, palette, seed):
    """Mossy JADE-GREEN overgrown stone — the jungle-reclaimed Ta Prohm mood."""
    _draw_colorway('jade', surf, top_rect, bot_rect, palette, seed)


def candidate_angkor_gilt(surf, top_rect, bot_rect, palette, seed):
    """GILDED gold-leaf sanctuary — a golden prasat that gleams at night."""
    _draw_colorway('gilt', surf, top_rect, bot_rect, palette, seed)


def candidate_angkor_sunset(surf, top_rect, bot_rect, palette, seed):
    """Warm laterite SUNSET red-ochre — the tower at golden hour."""
    _draw_colorway('sunset', surf, top_rect, bot_rect, palette, seed)


# ── review harness ─────────────────────────────────────────────────────────

def _bg(w, h, pal, ground_line):
    cell = pygame.Surface((w, h))
    for y in range(min(ground_line, h)):
        t = y / max(1, ground_line - 1)
        pygame.draw.line(cell, _mix(pal["sky_top"], pal["horizon"], t), (0, y), (w, y))
    for y in range(ground_line, h):
        t = (y - ground_line) / max(1, h - ground_line)
        pygame.draw.line(cell, _mix(pal["ground_top"], pal["ground_mid"], t),
                         (0, y), (w, y))
    return cell


def _max_empty_band(surf, x0, x1, y0, y1):
    """Fill gate for a CENTRED tapering silhouette: the worst vertical run of
    rows that are ENTIRELY empty across the 58px band — i.e. a horizontal
    stripe where the tower vanishes (a see-through break). The legitimate outer
    taper gutters are NOT counted; only a hole through the whole width is."""
    worst = run = 0
    for y in range(y0, y1):
        filled = any(surf.get_at((x, y))[3] > 0 for x in range(x0, x1))
        if filled:
            run = 0
        else:
            run += 1
            worst = max(worst, run)
    return worst


def _core_cover(surf, cx, y0, y1):
    """Companion read: the % of rows whose CENTRELINE core is solid — proves the
    bud core carries the centre top-to-bottom."""
    rows = filled = 0
    for y in range(y0, y1):
        rows += 1
        if any(surf.get_at((cx + dx, y))[3] > 0 for dx in range(-3, 4)):
            filled += 1
    return 100.0 * filled / max(1, rows)


def _gap_rim_clearance(surf, x0, x1, gap_y, up=True):
    step = -1 if up else 1
    for d in range(0, 200):
        y = gap_y + step * d
        if y < 0 or y >= surf.get_height():
            return d
        if any(surf.get_at((x, y))[3] > 0 for x in range(x0, x1)):
            return d
    return 200


def _bud_geom(section_h):
    """Replicate _draw_tower's height split so a probe knows where the bud body
    (neck .. shoulder .. finial join) sits in a rendered section."""
    finial_h = min(20, max(11, int(section_h * 0.11)))
    base_h = min(int(section_h * 0.42), max(22, int(section_h * 0.30)))
    plinth_h = min(11, max(6, int(section_h * 0.06)))
    base_bot = section_h - plinth_h
    base_top = base_bot - base_h
    bud_bot = base_top + 2          # y-from-top of the widest bud row
    bud_top = finial_h              # y-from-top of the bud/finial join
    n_tiers = max(4, (bud_bot - bud_top) // _TIER_PX)
    return bud_top, bud_bot, n_tiers


def _bud_swell(pal, section_h, seed=7):
    """Measure the outer silhouette: waisted-neck half-width vs the fat-shoulder
    peak in the lower third — the make-or-break bulge %."""
    s = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    br = pygame.Rect(MARGIN, GROUND_Y - section_h, PIPE_W, section_h)
    tr = pygame.Rect(MARGIN, 0, PIPE_W, 0)
    candidate_angkor_lotus(s, tr, br, pal, seed=seed)
    cx = MARGIN + PIPE_W // 2
    bud_top, bud_bot, _ = _bud_geom(section_h)
    y0 = GROUND_Y - section_h
    hws = []
    for y in range(y0 + bud_top, y0 + bud_bot):
        xs = [x for x in range(CACHE_W) if s.get_at((x, y))[3] > 40]
        if xs:
            hws.append((y, max(abs(xs[0] - cx), abs(xs[-1] - cx))))
    if not hws:
        return 0, 0, 0.0
    bud_h = bud_bot - bud_top
    neck = hws[-1][1]                                    # row nearest the base seam
    lower = [hw for y, hw in hws if (y0 + bud_bot - y) <= bud_h / 3]
    shoulder = max(lower) if lower else max(hw for _, hw in hws)
    swell = 100.0 * (shoulder - neck) / max(1, neck)
    return neck, shoulder, swell


def _hero(pal, seed):
    gap_y, gap_h = 168, 150
    top_h = int(gap_y - gap_h / 2)
    bot_top = int(gap_y + gap_h / 2)
    full = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    top_rect = pygame.Rect(MARGIN, 0, PIPE_W, top_h)
    bot_rect = pygame.Rect(MARGIN, bot_top, PIPE_W, GROUND_Y - bot_top)
    candidate_angkor_lotus(full, top_rect, bot_rect, pal, seed=seed)

    tip_y = top_h - 6
    base_y = GROUND_Y + 8
    hero_h = base_y - tip_y
    hero = _bg(CACHE_W, hero_h, pal, hero_h - (base_y - GROUND_Y))
    hero.blit(full, (0, -tip_y))
    for ex in (MARGIN, MARGIN + PIPE_W):
        pygame.draw.line(hero, (230, 60, 60), (ex, 0), (ex, hero_h), 1)
    return hero, hero_h


def _closeup(pal, seed, scale=3):
    """Zoom on a ground tower's shoulder + stepped base so the redent cornices,
    dentil courses and stair are checkable."""
    surf = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    br = pygame.Rect(MARGIN, GROUND_Y - 175, PIPE_W, 175)
    tr = pygame.Rect(MARGIN, 0, PIPE_W, 0)
    candidate_angkor_lotus(surf, tr, br, pal, seed=seed)
    crop = pygame.Surface((CACHE_W, 140))
    crop.blit(_bg(CACHE_W, 140, pal, 140), (0, 0))
    crop.blit(surf, (0, -(GROUND_Y - 140)))
    return pygame.transform.scale(
        crop, (crop.get_width() * scale, crop.get_height() * scale))


def _blackout(pal, section_h, scale):
    """Solid-black silhouette of a hero section — the redented lotus-bud read
    test: must NOT twin a pagoda cone or the Wat Arun prang."""
    surf = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    br = pygame.Rect(MARGIN, GROUND_Y - section_h, PIPE_W, section_h)
    tr = pygame.Rect(MARGIN, 0, PIPE_W, 0)
    candidate_angkor_lotus(surf, tr, br, pal, seed=7)
    pad_x = 18
    crop = pygame.Surface((PIPE_W + pad_x * 2, section_h + 8), pygame.SRCALPHA)
    crop.fill((238, 238, 240))
    for x in range(CACHE_W):
        for y in range(GROUND_Y - section_h, GROUND_Y):
            if surf.get_at((x, y))[3] > 40:
                bx = x - MARGIN + pad_x
                by = y - (GROUND_Y - section_h) + 4
                if 0 <= bx < crop.get_width() and 0 <= by < crop.get_height():
                    crop.set_at((bx, by), (18, 18, 22))
    return pygame.transform.scale(
        crop, (crop.get_width() * scale, crop.get_height() * scale))


def _hero_fn(pal, seed, cand):
    """`_hero`, but for an arbitrary colorway candidate fn — a mirrored upright
    tower against the phase sky, cropped to the finial tips + a ground sliver."""
    gap_y, gap_h = 168, 150
    top_h = int(gap_y - gap_h / 2)
    bot_top = int(gap_y + gap_h / 2)
    full = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    top_rect = pygame.Rect(MARGIN, 0, PIPE_W, top_h)
    bot_rect = pygame.Rect(MARGIN, bot_top, PIPE_W, GROUND_Y - bot_top)
    cand(full, top_rect, bot_rect, pal, seed=seed)
    tip_y = top_h - 6
    base_y = GROUND_Y + 8
    hero_h = base_y - tip_y
    hero = _bg(CACHE_W, hero_h, pal, hero_h - (base_y - GROUND_Y))
    hero.blit(full, (0, -tip_y))
    return hero, hero_h


def colorways():
    """Labelled colorway strip: the 5 new colorways + the original sandstone for
    reference, each an upright hero tower DAY (0.30) with a small NIGHT (0.85)
    thumbnail beneath to prove every colorway still retints across the biome."""
    pal_d = biome.palette_for_phase(PHASE_DAY)
    pal_n = biome.palette_for_phase(PHASE_NIGHT)

    ways = [
        ("Sandstone", candidate_angkor_lotus),
        ("Rose",      candidate_angkor_rose),
        ("Basalt",    candidate_angkor_basalt),
        ("Jade",      candidate_angkor_jade),
        ("Gilt",      candidate_angkor_gilt),
        ("Sunset",    candidate_angkor_sunset),
    ]

    pad = 12
    head_h = 74
    col_w = CACHE_W
    night_scale = 0.52
    night_w = int(CACHE_W * night_scale)

    day_cells = []
    night_cells = []
    for _, cand in ways:
        hd, hdh = _hero_fn(pal_d, 7, cand)
        hn, hnh = _hero_fn(pal_n, 7, cand)
        hn_s = pygame.transform.smoothscale(
            hn, (night_w, int(hnh * night_scale)))
        day_cells.append((hd, hdh))
        night_cells.append(hn_s)

    day_h = max(h for _, h in day_cells)
    night_h = max(c.get_height() for c in night_cells)
    lab_h = 20
    day_lab_h = 22

    sheet_w = pad + len(ways) * (col_w + pad)
    sheet_h = head_h + day_h + lab_h + pad + night_h + lab_h + pad * 2
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((24, 22, 26))

    title = pygame.font.SysFont(None, 30)
    sub = pygame.font.SysFont(None, 18)
    lab = pygame.font.SysFont(None, 20)
    labn = pygame.font.SysFont(None, 17)

    sheet.blit(title.render(
        "angkor_lotus — 5 material COLORWAYS (identical geometry)  ·  colorways",
        True, (250, 240, 224)), (pad, 12))
    sheet.blit(sub.render(
        "one shared redented lotus-bud silhouette; only the palette-derived body "
        "triad + moss swap  ·  every colorway retints day->night (proof thumbs "
        "below)  ·  DAY (0.30) hero + NIGHT (0.85) thumb",
        True, (172, 170, 180)), (pad, 40))

    x = pad
    for i, (name, _) in enumerate(ways):
        hd, hdh = day_cells[i]
        y = head_h + (day_h - hdh)
        sheet.blit(hd, (x, y))
        pygame.draw.rect(sheet, (60, 56, 62), (x, y, col_w, hdh), 1)
        col = (255, 224, 150) if i > 0 else (170, 200, 230)
        tag = f"{name}" if i > 0 else f"{name} (ref)"
        sheet.blit(lab.render(tag, True, col), (x + 2, head_h + day_h + 2))

        ny = head_h + day_h + day_lab_h + pad
        nc = night_cells[i]
        nx = x + (col_w - nc.get_width()) // 2
        sheet.blit(nc, (nx, ny))
        pygame.draw.rect(sheet, (60, 56, 62),
                         (nx, ny, nc.get_width(), nc.get_height()), 1)
        sheet.blit(labn.render("night 0.85", True, (150, 150, 170)),
                   (nx, ny + nc.get_height() + 2))
        x += col_w + pad

    out = pathlib.Path(__file__).resolve().parent / "colorways.png"
    pygame.image.save(sheet, out)
    print(f"wrote {out}  ({sheet.get_width()}x{sheet.get_height()})")


def main():
    pal = biome.palette_for_phase(PHASE_DAY)
    pal_n = biome.palette_for_phase(PHASE_NIGHT)

    _, mid_d, sh_d = _sandstone_triad(pal)
    _, mid_n, _ = _sandstone_triad(pal_n)
    print("SANDSTONE (mid tone) — grey-gold, biome-swept")
    print(f"  DAY   mid={mid_d} lum={_lum(mid_d):.1f}")
    print(f"  NIGHT mid={mid_n} lum={_lum(mid_n):.1f}")
    print(f"  day != night: {mid_d != mid_n}")

    # Bud-bulge read: neck waist vs fat-shoulder swell + readable cornice count.
    print("BUD PROFILE — waisted neck -> fat shoulder (lower third) -> pinched top")
    print(f"  envelope: neck={_NECK} shoulder={_SHOULDER}  "
          f"(shoulder/neck = {100.0 * (_SHOULDER - _NECK) / _NECK:.0f}% envelope swell)")
    for sh_h in (150, 355):
        neck_px, sh_px, swell = _bud_swell(pal, sh_h)
        _, _, ledges = _bud_geom(sh_h)
        print(f"  section {sh_h:3d}px  neck={neck_px}px  shoulder={sh_px}px  "
              f"swell={swell:.0f}%  cornice-ledges={ledges}")

    # Fill gate + core coverage at three section heights.
    print("FILL GATE (worst vertical run of FULLY-empty rows across the 58px band)"
          "  +  centre-core coverage")
    strip_heights = [70, 210, 355]
    strips = []
    for h in strip_heights:
        s = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
        br = pygame.Rect(MARGIN, GROUND_Y - h, PIPE_W, h)
        tr = pygame.Rect(MARGIN, 0, PIPE_W, 0)
        candidate_angkor_lotus(s, tr, br, pal, seed=7)
        run = _max_empty_band(s, MARGIN, MARGIN + PIPE_W, GROUND_Y - h, GROUND_Y)
        cover = _core_cover(s, MARGIN + PIPE_W // 2, GROUND_Y - h, GROUND_Y)
        crop = pygame.Surface((CACHE_W, h + 8))
        crop.blit(_bg(CACHE_W, h + 8, pal, h), (0, 0))
        crop.blit(s, (0, -(GROUND_Y - h)))
        for ex in (MARGIN, MARGIN + PIPE_W):
            pygame.draw.line(crop, (230, 60, 60), (ex, 0), (ex, h + 8), 1)
        strips.append((h, crop, run, cover))
        print(f"  h={h:3d}  empty-band run = {run}px  [{'OK' if run <= 12 else 'FAIL'}]"
              f"   core cover = {cover:.0f}%")

    # Mirror clearance — bottom finial reaching the gap + top flipped finial.
    gap_probe = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    gp_bot = pygame.Rect(MARGIN, 243, PIPE_W, GROUND_Y - 243)
    gp_top = pygame.Rect(MARGIN, 0, PIPE_W, 93)
    candidate_angkor_lotus(gap_probe, gp_top, gp_bot, pal, seed=7)
    # Bottom finial tip sits just BELOW its 243 rim -> probe DOWN; top flipped
    # finial hangs just ABOVE its 93 rim -> probe UP. Small = solid at the rim.
    clear_bot = _gap_rim_clearance(gap_probe, MARGIN, MARGIN + PIPE_W, 243, up=False)
    clear_top = _gap_rim_clearance(gap_probe, MARGIN, MARGIN + PIPE_W, 93, up=True)
    print("MIRROR / GAP-RIM (finial tip distance from its gap-rim line)")
    print(f"  bottom finial tip {clear_bot}px below rim   "
          f"top (flipped) finial tip {clear_top}px above rim   "
          f"(flyable gap 93..243 stays clear)")

    hero_day, hd_h = _hero(pal, 7)
    hero_night, hn_h = _hero(pal_n, 7)
    close = _closeup(pal, 7)
    bo1 = _blackout(pal, 150, 1)
    bo3 = _blackout(pal, 150, 3)

    # ── compose the sheet ──
    pad = 12
    label_h = 22
    head_h = 82
    title = pygame.font.SysFont(None, 30)
    sub = pygame.font.SysFont(None, 18)
    lab = pygame.font.SysFont(None, 19)

    col_hero = CACHE_W
    col_close = close.get_width()
    col_bo = max(bo3.get_width(), bo1.get_width()) + 20
    strips_total_h = sum(c.get_height() + label_h + pad for _, c, _, _ in strips)

    body_h = max(hd_h, hn_h, close.get_height(),
                 strips_total_h, bo3.get_height() + 60) + label_h
    sheet_w = pad + col_hero + pad + col_hero + pad + col_hero + pad + \
        col_close + pad + col_bo + pad
    sheet_h = head_h + body_h + pad * 2
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((24, 22, 26))

    sheet.blit(title.render(
        "angkor_lotus — Angkor Wat central prasat (redented lotus-bud)  ·  round_2",
        True, (250, 240, 224)), (pad, 12))
    sheet.blit(sub.render(
        "red edges = PIPE_W (58px) collision band  ·  grey-gold sandstone  ·  "
        "BULGING lotus-bud that swells then ogival-tapers  ·  REDENTED corners "
        "(stepped cornice ledges = serrated edge)  ·  stepped base + steep stair",
        True, (172, 170, 180)), (pad, 40))
    sheet.blit(sub.render(
        "DISTINCT FROM WAT ARUN/PAGODAS: bare-stone bud (no porcelain mosaic, no "
        "gilt tiers, no flaring eaves)  ·  blocky stepped redent cornices, not the "
        "prang's 1.5px ripple  ·  pointed lotus finial on a stepped square foot",
        True, (230, 206, 150)), (pad, 56))

    x = pad
    y = head_h
    sheet.blit(hero_day, (x, y))
    pygame.draw.rect(sheet, (60, 56, 62), (x, y, col_hero, hd_h), 1)
    sheet.blit(lab.render("HERO — DAY (0.30)", True, (255, 224, 150)),
               (x, y + hd_h + 4))

    x += col_hero + pad
    sheet.blit(hero_night, (x, y))
    pygame.draw.rect(sheet, (60, 56, 62), (x, y, col_hero, hn_h), 1)
    sheet.blit(lab.render("HERO — NIGHT (0.85)", True, (255, 224, 150)),
               (x, y + hn_h + 4))

    x += col_hero + pad
    sy = head_h
    sheet.blit(lab.render("FILL GATE — bottom section", True, (255, 224, 150)),
               (x, sy - 20))
    for h, crop, run, cover in strips:
        sheet.blit(crop, (x, sy))
        pygame.draw.rect(sheet, (60, 56, 62), (x, sy, col_hero, crop.get_height()), 1)
        ok = "OK" if run <= 12 else "FAIL"
        sheet.blit(lab.render(f"h={h}px  ·  band {run}px [{ok}]  ·  core {cover:.0f}%",
                              True, (200, 235, 170) if run <= 12 else (255, 140, 140)),
                   (x, sy + crop.get_height() + 4))
        sy += crop.get_height() + label_h + pad

    x += col_hero + pad
    sheet.blit(close, (x, head_h))
    pygame.draw.rect(sheet, (60, 56, 62),
                     (x, head_h, close.get_width(), close.get_height()), 1)
    sheet.blit(lab.render("SHOULDER + BASE 3x — carved relief", True,
                          (255, 224, 150)), (x, head_h + close.get_height() + 4))

    x += col_close + pad
    sheet.blit(lab.render("BLACKOUT (lotus-bud test)", True, (255, 224, 150)),
               (x, head_h - 20))
    sheet.blit(bo3, (x, head_h))
    sheet.blit(lab.render("3x", True, (200, 200, 210)),
               (x, head_h + bo3.get_height() + 2))
    sheet.blit(bo1, (x + bo3.get_width() // 2 - bo1.get_width() // 2,
                     head_h + bo3.get_height() + 24))
    sheet.blit(lab.render("1x @ 58px", True, (200, 200, 210)),
               (x, head_h + bo3.get_height() + 24 + bo1.get_height() + 2))

    out = pathlib.Path(__file__).resolve().parent / "round_2.png"
    pygame.image.save(sheet, out)
    print(f"wrote {out}  ({sheet.get_width()}x{sheet.get_height()})")


if __name__ == "__main__":
    main()
    colorways()
