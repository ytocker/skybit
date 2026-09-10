"""petronas_twins — high-fidelity Petronas Twin Towers pillar (candidate).

The only DOUBLED silhouette in the far-east-landmarks set: two tapered
steel-and-glass shafts rising in stepped ringed setbacks, joined at mid-height
by the iconic two-legged double-decker SKYBRIDGE, each capped by a pyramid
pinnacle, a stacked ring-ball and a slender spire mast. The tell is the
twin-slot — a pair of parallel shafts with a narrow shadowed recess between
them and TWO needle masts on top, not one.

Feasibility (the make-or-break of a twin-tower pillar): two separate towers
would leave a see-through vertical band in the ~58 px collision column — a
fly-in-and-die killzone. This is solved by construction: a DIM recessed
curtain-wall BACKING spans the full collision column behind both shafts, and
the shared podium + skybridge bridge the centre, so the slot reads as a
shadowed recess (value, not a hole) while the alpha column stays solid at
every row. The twin identity is carried by the bright-steel shafts flanking
the dark slot, the two gutter-spilling outer edges, the paired masts and the
skybridge — never by an open gap.

Materials are all palette-derived so the 5-min biome day->night retint sweeps
straight through (raw-RGB anchors are fixed archetype biases only): cool
steel-glass shaft triad with strong vertical specular ribs + horizontal
setback ring-bands, cooler glass spandrels, a step-darker recessed backing,
bronze/gold pinnacle masts + ring-balls + skybridge struts, and a night
curtain-wall window glow + mast beacon halos gated on `_is_dark_sky`.

This is a standalone review candidate; it wires nothing into the live game.

Run:  python docs/pillar_landmarks/far_east_landmarks/petronas_twins/render.py
Out:  docs/pillar_landmarks/far_east_landmarks/petronas_twins/round_2.png
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
# pillars, so the steel, gilt and night glow read exactly on-palette.
from game.pillar_pagodas import (
    _mix, _shade, _gradient_rect, _aa_polyline, _lit_niche, _tile_hatch,
    _draw_plinth_mist, _is_dark_sky, _is_warming_sky,
    _cap_lit_for_dark_sky, _cap_dark_for_dark_sky,
    _bronze, _gold_bright, _column_grey, _plaster, _glazed_tile_checker,
)
from game.pillar_variants import draw_grass_bed
from game.draw import draw_side_shrub


MARGIN = 64                       # matches entities.Pipe eave/ornament gutter
CACHE_W = PIPE_W + MARGIN * 2
CACHE_H = GROUND_Y
PHASE_DAY = 0.30                  # midday sky — hardest test for the cool steel
PHASE_NIGHT = 0.85               # deep night — checks window glow + mast beacons

# ── Twin-tower geometry ─────────────────────────────────────────────────────
#
# The two shafts sit close to the column centre so the slot between their inner
# edges stays a NARROW recess, while their outer edges spill into the eave
# gutter (the twin-shoulder tell). `_HALF` is the collision half-width (29 px);
# the backing is drawn to `_BACK_HALF` (full collision width) so the column is
# solid at every row regardless of the shaft taper.

_HALF = PIPE_W / 2                 # 29 — collision half-width
_TOWER_OFF = 20                    # each shaft centre offset from column centre
_SHAFT_HW = 15                     # shaft half-width at its widest (base) tier
_BACK_HALF = 30                    # recessed backing half-width (>_HALF: fills the
                                   # whole collision band incl. its edge columns)
_TAPER = 0.088                     # per-tier setback: hw shrinks this fraction


def _lum(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


# ── Materials ────────────────────────────────────────────────────────────────
#
# Cool stainless-and-glass steel derived from `_column_grey` (the shipped
# granite slate) biased toward a cool blue-silver. The shaft reads as a curved
# steel cylinder via a left-lit/right-shadow triad; the specular ribs pull a
# hard white streak so the fluted 8-point-star curtain wall catches the sun.

def _steel_triad(palette):
    base = _mix(_column_grey(palette), (196, 206, 220), 0.55)
    lit = _mix(base, (236, 242, 250), 0.52)      # hard steel specular
    sh = _mix(base, (58, 66, 82), 0.55)          # cool blue shadow side
    lit = _cap_lit_for_dark_sky(lit, palette, cap=214)
    sh = _cap_dark_for_dark_sky(sh, palette, floor=48)
    return lit, base, sh


def _glass(palette):
    # Cooler, darker spandrel between the steel mullions — the glazed floor
    # bands. A step down in value from the steel shadow so the horizontal
    # storey lines read against the vertical ribs.
    g = _mix(_column_grey(palette), (52, 70, 92), 0.6)
    return _cap_dark_for_dark_sky(g, palette, floor=40)


def _backing_triad(palette):
    # The dim recessed curtain-wall behind both shafts — a full step darker and
    # cooler than the lit steel so the slot between the towers reads as a
    # shadowed interior recess, never a see-through gap. This is the killzone
    # fix: it fills the whole collision column.
    base = _mix(_column_grey(palette), (74, 84, 100), 0.6)
    lit = _shade(base, 16)
    sh = _cap_dark_for_dark_sky(_shade(base, -34), palette, floor=34)
    return lit, base, sh


def _podium_triad(palette):
    # Wide granite-and-steel podium the twin towers share — grounds the bright
    # shafts and bridges the slot at the base. Bronze-warm so it reads as the
    # stone concourse rather than more curtain wall.
    base = _bronze(palette)
    return _shade(base, 22), _shade(base, -8), _shade(base, -40)


# ── Recessed backing (killzone fix + twin-crown top) ─────────────────────────

# Twin-crown top profile (px, measured DOWN from the gap-rim y_top). The two
# shaft centres are the raised HUMPS, the slot centre is a deeper DIP, the outer
# band edges are dropped SHOULDERS. The humps sit a few px BELOW the mast-tip
# air line so the paired needles protrude above the crown; the dip carves the
# sky gap between the two tops. All offsets only remove material at the gap-rim
# (top) end, so they can only ADD bird clearance — never a killzone. The dip is
# held to the ≤12px fill budget (it IS the central-slot empty run).
_BACK_HUMP = 6                     # tower-top humps — below the 3px mast-tip line
_BACK_DIP = 11                     # central slot dip — sky gap, = central run
_BACK_SHOULDER = 9                 # outer-edge drop past the humps


def _backing_top_offset(dx):
    """Twin-crown top profile: px to drop the backing's top edge at horizontal
    offset `dx` from the column centre. Two peaks over the shaft centres
    (±_TOWER_OFF), a deeper valley between them, and dropped outer shoulders — so
    the blackout reads as TWO tower tops with sky between, not one flat brick."""
    knots = [(-_BACK_HALF, float(_BACK_SHOULDER)),
             (-_TOWER_OFF, float(_BACK_HUMP)),
             (0.0, float(_BACK_DIP)),
             (_TOWER_OFF, float(_BACK_HUMP)),
             (_BACK_HALF, float(_BACK_SHOULDER))]
    if dx <= knots[0][0]:
        return knots[0][1]
    if dx >= knots[-1][0]:
        return knots[-1][1]
    for i in range(len(knots) - 1):
        x0, o0 = knots[i]
        x1, o1 = knots[i + 1]
        if x0 <= dx <= x1:
            t = (dx - x0) / (x1 - x0)
            tc = (1.0 - math.cos(t * math.pi)) / 2.0   # cosine-smoothed crown
            return o0 + (o1 - o0) * tc
    return 0.0


def _draw_backing(surf, cx, y_top, y_bot, palette):
    """Dim recessed curtain-wall spanning the full collision column behind the
    two shafts. Drawn FIRST so the bright steel towers overlay it and the slot
    between them reveals this shadowed panel — the column is solid at every row
    so there is no fly-in killzone. A faint vertical mullion grid keeps it
    reading as a distant glazed wall rather than a flat fill; the TOP edge is
    carved to a twin-crown (two humps + centre dip) so the silhouette doubles."""
    lit, mid, sh = _backing_triad(palette)
    x0 = int(cx - _BACK_HALF)
    w = int(_BACK_HALF * 2)
    h = y_bot - y_top
    if h < 2:
        return
    # Build on a private surface so the twin-crown notch can be carved from the
    # top edge after all the wall detail is laid down.
    temp = pygame.Surface((w, h), pygame.SRCALPHA)
    rect = pygame.Rect(0, 0, w, h)
    # Faint centre-out shading so the recess has depth, darkest at the slot.
    _gradient_rect(temp, rect, sh, mid, sh)
    # Quiet vertical mullion lines — a receding glazed grid.
    for gx in range(4, w - 2, 5):
        pygame.draw.line(temp, _shade(mid, -14), (gx, 0), (gx, h - 1), 1)
    # Sparse horizontal storey lines.
    for gy in range(6, h - 2, 9):
        pygame.draw.line(temp, _shade(sh, -8), (0, gy), (w - 1, gy), 1)
    # Carve the twin-crown top: clear the notch above the profile per column.
    for lx in range(w):
        off = int(round(_backing_top_offset((x0 + lx) - cx)))
        for ly in range(off):
            temp.set_at((lx, ly), (0, 0, 0, 0))
    surf.blit(temp, (x0, y_top))


# ── One steel shaft ─────────────────────────────────────────────────────────

def _shaft_hw(tier, hw_base):
    """Half-width at a given setback tier (0 = widest base)."""
    return hw_base * (1.0 - _TAPER * tier)


def _draw_shaft(surf, tcx, y_top, y_bot, palette, tiers, *, seed_off, dark_sky,
                warming):
    """One tapered steel-glass shaft built as `tiers` stacked setback storeys,
    each a step narrower than the one below (the ringed setback taper). Every
    storey gets a horizontal 3-stop gradient (cylindrical volume), strong
    vertical specular ribs (the fluted 8-point-star mullions), a bronze setback
    ring-band at each shoulder, and — at night — a warm curtain-wall window
    glow. Returns the (cx, y, hw) of the shaft crown for the pinnacle."""
    lit, mid, sh = _steel_triad(palette)
    glass = _glass(palette)
    bronze = _bronze(palette)
    gold = _gold_bright(palette)
    H = y_bot - y_top
    tier_h = H / tiers
    rng = random.Random(1700 + seed_off)

    crown_hw = _SHAFT_HW
    for t in range(tiers):
        hw = _shaft_hw(t, _SHAFT_HW)
        ty1 = int(round(y_bot - t * tier_h))          # storey bottom
        ty0 = int(round(y_bot - (t + 1) * tier_h))    # storey top
        x0 = int(round(tcx - hw))
        x1 = int(round(tcx + hw))
        rect = pygame.Rect(x0, ty0, x1 - x0, ty1 - ty0)
        if rect.width < 3 or rect.height < 2:
            continue
        # Cylindrical body — lit LEFT to shadow RIGHT.
        _gradient_rect(surf, rect, lit, mid, sh)

        # Glass spandrel storey lines — thin cool-dark horizontals so the
        # curtain wall reads as stacked floors under the vertical ribs.
        for gy in range(ty0 + 3, ty1 - 1, 4):
            pygame.draw.line(surf, glass, (x0 + 1, gy), (x1 - 2, gy), 1)

        # Vertical specular ribs — the fluted mullions of the 8-point-star
        # plan. A hard white streak on the lit side + secondary ribs across the
        # face, with a dark groove between each so the flutes read as relief.
        rib_n = max(2, int(rect.width / 6))
        for r in range(rib_n):
            rx = x0 + 2 + int((rect.width - 4) * r / max(1, rib_n - 1))
            groove = _mix(sh, glass, 0.5)
            pygame.draw.line(surf, groove, (rx + 1, ty0 + 1), (rx + 1, ty1 - 1), 1)
            # Brightest rib nearest the lit (left) side; ribs dim rightward.
            rib_t = r / max(1, rib_n - 1)
            rib_col = _mix(lit, mid, rib_t * 0.8)
            pygame.draw.line(surf, rib_col, (rx, ty0 + 1), (rx, ty1 - 1), 1)

        # Setback ring-band at the shoulder (top of every storey) — a bronze
        # bright cap over a shadow under-line + tile-end hatch, the ringed
        # step-back that defines the Petronas taper.
        pygame.draw.line(surf, _shade(sh, -18), (x0, ty0), (x1 - 1, ty0), 1)
        pygame.draw.line(surf, gold, (x0 + 1, ty0 + 1), (x1 - 2, ty0 + 1), 1)
        pygame.draw.line(surf, _shade(bronze, -20), (x0 + 1, ty0 + 2),
                         (x1 - 2, ty0 + 2), 1)
        _tile_hatch(surf, x0 + 1, ty0 + 2, x1 - 2, ty0 + 2,
                    _shade(bronze, -30), step=3)

        # Night curtain-wall glow — a warm window grid gated on the dark sky so
        # the towers light up as the biome rolls into evening.
        if (dark_sky or warming) and rect.width >= 8 and rect.height >= 8:
            _draw_windows(surf, x0, ty0 + 4, x1, ty1 - 2, palette,
                          rng, dark_sky=dark_sky)

        # AA outline down the two shaft edges so the setback steps read crisp.
        _aa_polyline(surf, _shade(sh, -22), [(x0, ty0), (x0, ty1 - 1)])
        _aa_polyline(surf, _mix(lit, (255, 255, 255), 0.2),
                     [(x0 + 1, ty0 + 2), (x0 + 1, ty1 - 1)])
        crown_hw = hw

    crown_y = int(round(y_bot - tiers * tier_h))
    return tcx, crown_y, _shaft_hw(tiers - 1, _SHAFT_HW)


def _draw_windows(surf, x0, y0, x1, y1, palette, rng, *, dark_sky):
    """Additive warm window grid on a storey's glass — the lit curtain wall at
    night/dusk. Alpha ramps with the sky so the towers pre-warm at sunset and
    blaze at night; a scatter of dark (unlit) cells keeps it from reading as a
    printed grid."""
    warm = _mix(palette['stone_accent'], (255, 214, 130), 0.8)
    a_lit = 150 if dark_sky else 70
    step = 3
    for wy in range(y0, y1 - 1, step):
        for wx in range(x0 + 2, x1 - 2, step):
            if rng.random() < 0.34:           # some floors dark
                continue
            g = pygame.Surface((2, 2), pygame.SRCALPHA)
            g.fill((*warm, a_lit))
            surf.blit(g, (wx, wy), special_flags=pygame.BLEND_RGBA_ADD)


# ── Pinnacle: pyramid + ring-ball + spire mast ──────────────────────────────

def _draw_pinnacle(surf, tcx, crown_y, crown_hw, palette, *, dark_sky, warming,
                   y_limit):
    """The Petronas crown: a short steel pyramid steps in from the shaft top to
    a stacked bronze ring-ball, then a slender spire mast needles up. The whole
    stack shares ONE continuous mast spine that runs from the pyramid apex up
    through the ball to the tip, so it never fragments into a detached dot at
    small scale. `y_limit` is the section's gap-rim; the tip is held ~3px short
    of it so the vertical-flip mirror doesn't kiss. At night/dusk the tip
    carries an additive beacon halo (the aircraft warning light). Two of these —
    one per tower — are the paired-needle tell that says twin towers."""
    lit, mid, sh = _steel_triad(palette)
    bronze = _bronze(palette)
    gold = _gold_bright(palette)
    # Cool-dark shadow edge so the thin masts survive against a bright day sky.
    edge = _mix(_column_grey(palette), (36, 46, 66), 0.7)

    # The whole crown must nest inside the headroom above the shaft so nothing
    # (least of all the ball) overshoots the gap rim on a short section. `avail`
    # is that headroom; the mast tip always lands exactly on the 3px air line so
    # the vertical-flip mirror keeps ~3px between paired needles.
    tip_y = y_limit + 3
    avail = max(10, crown_y - tip_y)

    # Pyramid — a stepped taper from the shaft crown to a narrow neck. Capped to
    # <=45% of the headroom so ball + mast always fit above it.
    pyr_h = min(max(6, int(crown_hw * 1.6)), int(avail * 0.45))
    neck_hw = max(2, crown_hw * 0.34)
    steps = 4
    for s in range(steps):
        f0 = s / steps
        f1 = (s + 1) / steps
        hw0 = crown_hw + (neck_hw - crown_hw) * f0
        hw1 = crown_hw + (neck_hw - crown_hw) * f1
        y0 = crown_y - int(pyr_h * f0)
        y1 = crown_y - int(pyr_h * f1)
        poly = [(tcx - hw0, y0), (tcx + hw0, y0),
                (tcx + hw1, y1), (tcx - hw1, y1)]
        pygame.draw.polygon(surf, _mix(mid, sh, f0 * 0.5), poly)
        # Lit left face of each pyramid step.
        _aa_polyline(surf, _mix(lit, (255, 255, 255), 0.25),
                     [(tcx - hw0, y0), (tcx - hw1, y1)])
        _aa_polyline(surf, _shade(sh, -18),
                     [(tcx + hw0, y0), (tcx + hw1, y1)])
    neck_y = crown_y - pyr_h

    # Ring-ball — kept SMALL (so a lone tower can't be mistaken for a beaded
    # spire) and capped to half the leftover headroom so the mast still reads.
    # Its base OVERLAPS the pyramid apex so there is no seam.
    ball_r = max(2, min(int(crown_hw * 0.55), int((avail - pyr_h) * 0.28)))
    ball_h = ball_r * 2
    ball_bot = neck_y + 1              # bite into the pyramid apex — no gap
    ball_top = ball_bot - ball_h

    # Spire mast — a slender needle running from the ball straight to the tip on
    # the 3px air line (the mast simply fills the remaining headroom).
    mast_top = tip_y

    # ONE continuous spine: pyramid-apex → through the ball → tip. Drawn before
    # the ball rings so the stack is a single unbroken needle at any scale.
    pygame.draw.line(surf, edge, (tcx + 1, ball_bot), (tcx + 1, mast_top), 1)
    pygame.draw.line(surf, _shade(bronze, -20), (tcx, ball_bot),
                     (tcx, mast_top), 1)
    pygame.draw.line(surf, gold, (tcx, ball_bot), (tcx, mast_top), 1)

    # Ball rings drawn every row (sin profile: 0 at poles, widest at the waist)
    # so the ball is a solid contiguous bead over the spine, never a dotted gap.
    for ry in range(ball_top, ball_bot + 1):
        f = (ry - ball_top) / max(1, ball_h)
        rw = max(1, int(round(ball_r * math.sin(math.pi * f))))
        col = _shade(bronze, 18) if (ry - ball_top) % 2 == 0 else _shade(bronze, -16)
        pygame.draw.line(surf, col, (tcx - rw, ry), (tcx + rw, ry), 1)
    # Bright gold glint at the ball's waist.
    pygame.draw.line(surf, gold, (tcx - ball_r, ball_top + ball_r),
                     (tcx + ball_r, ball_top + ball_r), 1)

    # A couple of collar rings up the mast.
    m_lo = mast_top + (ball_top - mast_top) // 3
    m_hi = mast_top + 2 * (ball_top - mast_top) // 3
    for cy in (m_lo, m_hi):
        if mast_top < cy < ball_top:
            pygame.draw.line(surf, _shade(bronze, 16), (tcx - 1, cy), (tcx + 1, cy), 1)

    # Night beacon halo at the mast tip.
    if dark_sky or warming:
        r_out = 9 if dark_sky else 4
        beam = _mix(palette['stone_accent'], (255, 226, 150), 0.85)
        sz = r_out * 2 + 2
        halo = pygame.Surface((sz, sz), pygame.SRCALPHA)
        c = sz // 2
        for ring, a in ((1.0, 40), (0.6, 90), (0.3, 150)):
            pygame.draw.circle(halo, (*beam, a), (c, c), max(1, int(r_out * ring)))
        surf.blit(halo, (tcx - c, mast_top - c),
                  special_flags=pygame.BLEND_RGBA_ADD)
        surf.set_at((tcx, mast_top), (255, 240, 200))
    return mast_top


# ── Double-decker skybridge ─────────────────────────────────────────────────

def _draw_skybridge(surf, cx, bridge_y, left_inner, right_inner, palette):
    """The two-legged double-decker skybridge linking the shafts across the
    slot. Two angled bronze struts rise from the tower inboard faces to meet
    under the deck centre (the iconic support arch), carrying a two-storey deck
    that visually bridges the recess. Drawn AFTER the shafts so it crosses the
    slot in front of the recessed backing."""
    bronze = _bronze(palette)
    gold = _gold_bright(palette)
    steel_lit = _mix(_column_grey(palette), (226, 232, 242), 0.5)
    span_l = left_inner
    span_r = right_inner
    if span_r - span_l < 4:
        return
    apex_y = bridge_y + 9

    # Two support legs forming the inverted-V arch under the deck.
    for sx, apex_off in ((span_l, 1), (span_r, -1)):
        pygame.draw.line(surf, _shade(bronze, -18),
                         (sx, apex_y + 8), (cx + apex_off, apex_y), 2)
        pygame.draw.line(surf, gold,
                         (sx, apex_y + 8), (cx + apex_off, apex_y), 1)
    # Vertical drop-post from the apex to the deck.
    pygame.draw.line(surf, _shade(bronze, -18), (cx, apex_y), (cx, bridge_y + 4), 2)

    # Two-storey deck — two horizontal bars spanning the slot.
    for dy in (bridge_y, bridge_y + 3):
        pygame.draw.line(surf, _shade(bronze, -22), (span_l, dy + 1),
                         (span_r, dy + 1), 1)
        pygame.draw.line(surf, steel_lit, (span_l, dy), (span_r, dy), 1)
    # Thin deck floor between the two decks.
    pygame.draw.line(surf, _shade(bronze, -6), (span_l, bridge_y + 2),
                     (span_r, bridge_y + 2), 1)


# ── Shared podium ───────────────────────────────────────────────────────────

def _draw_podium(surf, cx, base_y, palette, seed):
    """Wide 3-layer granite podium the twins share — bridges the slot at the
    base and grounds both shafts. Widest layer spills toward the gutters like
    the real concourse skirt."""
    lit, mid, sh = _podium_triad(palette)
    layers = 3
    for i in range(layers):
        lw = int(PIPE_W * (1.02 + 0.14 * i))
        lh = 5
        ly = base_y - (layers - i) * lh
        r = pygame.Rect(cx - lw // 2, ly, lw, lh)
        _gradient_rect(surf, r, lit, mid, sh)
        pygame.draw.line(surf, _shade(sh, -20),
                         (r.x, r.bottom - 1), (r.right - 1, r.bottom - 1), 1)
        pygame.draw.line(surf, _shade(lit, 18), (r.x, r.y), (r.right - 1, r.y), 1)


# ── One upright twin-tower section ──────────────────────────────────────────

def _tier_count(shaft_h):
    """Height-adaptive setback count — fewer storeys when short so a stubby
    section doesn't cram five squashed tiers."""
    if shaft_h < 60:
        return 2
    if shaft_h < 120:
        return 3
    if shaft_h < 200:
        return 4
    return 5


def _draw_twin(surf, cx, y_top, y_bot, palette, seed):
    """A full twin-tower section rising from the ground: recessed backing ->
    shared podium -> two stepped steel shafts -> skybridge -> two pinnacles ->
    plinth + foliage. Height-adaptive tier count; skybridge omitted at very
    short heights (backing still fills the column)."""
    dark_sky = _is_dark_sky(palette)
    warming = _is_warming_sky(palette)
    section_h = y_bot - y_top

    podium_h = min(15, max(8, int(section_h * 0.09)))
    if section_h < 90:
        podium_h = max(6, podium_h - 2)
    base_y = y_bot

    _draw_plinth_mist(surf, cx, base_y - podium_h + 2, int(PIPE_W * 2.0), palette)

    shaft_bot = base_y - podium_h
    # Reserve headroom for the pinnacle (pyramid + ball + mast) at the crown.
    pinnacle_reserve = min(64, max(22, int(section_h * 0.24)))
    shaft_top = y_top + pinnacle_reserve
    shaft_h = shaft_bot - shaft_top
    if shaft_h < 20:
        shaft_h = 20
        shaft_top = shaft_bot - shaft_h
    tiers = _tier_count(shaft_h)

    # Recessed backing fills the whole column (section top down to the podium)
    # so neither the slot nor the band edges are ever a hole.
    _draw_backing(surf, cx, y_top, shaft_bot, palette)

    # Two shafts flanking the centre.
    lcx = cx - _TOWER_OFF
    rcx = cx + _TOWER_OFF
    lc = _draw_shaft(surf, lcx, shaft_top, shaft_bot, palette, tiers,
                     seed_off=0, dark_sky=dark_sky, warming=warming)
    rc = _draw_shaft(surf, rcx, shaft_top, shaft_bot, palette, tiers,
                     seed_off=101, dark_sky=dark_sky, warming=warming)

    # Skybridge at mid-shaft (omitted when there's no room for a legible arch).
    if shaft_h >= 70:
        bridge_y = shaft_bot - int(shaft_h * 0.5)
        # Inner faces at the bridge height (account for the tier taper there).
        bt = (shaft_bot - bridge_y) / max(1, shaft_h)
        tier_at = min(tiers - 1, int(bt * tiers))
        hw_at = _shaft_hw(tier_at, _SHAFT_HW)
        left_inner = int(lcx + hw_at)
        right_inner = int(rcx - hw_at)
        _draw_skybridge(surf, cx, bridge_y, left_inner, right_inner, palette)

    # Pinnacles — one per tower (the paired needles). Tips held ~3px shy of the
    # section's top rim so the vertical-flip mirror doesn't kiss across the gap.
    _draw_pinnacle(surf, lc[0], lc[1], lc[2], palette,
                   dark_sky=dark_sky, warming=warming, y_limit=y_top)
    _draw_pinnacle(surf, rc[0], rc[1], rc[2], palette,
                   dark_sky=dark_sky, warming=warming, y_limit=y_top)

    # Podium + foliage.
    _draw_podium(surf, cx, base_y, palette, seed)
    draw_grass_bed(surf, cx, base_y - 1, PIPE_W + 12, 12, palette, seed=seed)
    draw_side_shrub(surf, cx - _HALF - 6, base_y - 1, palette, scale=0.9)
    draw_side_shrub(surf, cx + _HALF + 6, base_y - 1, palette, scale=0.8)


def candidate_petronas_twins(surf, top_rect, bot_rect, palette, seed):
    """Bottom = twin towers rising from the ground, masts reaching the gap. Top
    = the same section vertical-FLIPPED from the ceiling — the paired shafts
    are bilaterally symmetric so the flip mirrors cleanly, masts hanging into
    the gap."""
    if bot_rect.height > 0:
        _draw_twin(surf, bot_rect.centerx, bot_rect.y, bot_rect.bottom,
                   palette, seed)
    if top_rect.height > 0:
        tmp = pygame.Surface((surf.get_width(), top_rect.height), pygame.SRCALPHA)
        _draw_twin(tmp, top_rect.centerx, 0, top_rect.height, palette, seed + 1)
        surf.blit(pygame.transform.flip(tmp, False, True), (0, top_rect.y))


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


def _max_empty_run(surf, x0, x1, y0, y1):
    worst = 0
    for x in range(x0, x1):
        run = 0
        for y in range(y0, y1):
            if surf.get_at((x, y))[3] == 0:
                run += 1
                worst = max(worst, run)
            else:
                run = 0
    return worst


def _central_gap(surf, cx, y0, y1, band=8):
    """Worst empty vertical run in the CENTRAL band (the twin slot) — the
    killzone audit. Checks the ±band px column straddling the tower slot."""
    return _max_empty_run(surf, cx - band, cx + band, y0, y1)


def _gap_rim_clearance(surf, x0, x1, gap_y, up=True):
    step = -1 if up else 1
    for d in range(0, 200):
        y = gap_y + step * d
        if y < 0 or y >= surf.get_height():
            return d
        if any(surf.get_at((x, y))[3] > 0 for x in range(x0, x1)):
            return d
    return 200


def _hero(pal, seed):
    gap_y, gap_h = 176, 150
    top_h = int(gap_y - gap_h / 2)
    bot_top = int(gap_y + gap_h / 2)
    full = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    top_rect = pygame.Rect(MARGIN, 0, PIPE_W, top_h)
    bot_rect = pygame.Rect(MARGIN, bot_top, PIPE_W, GROUND_Y - bot_top)
    candidate_petronas_twins(full, top_rect, bot_rect, pal, seed=seed)

    tip_y = 0
    base_y = GROUND_Y + 8
    hero_h = base_y - tip_y
    hero = _bg(CACHE_W, hero_h, pal, hero_h - (base_y - GROUND_Y))
    hero.blit(full, (0, -tip_y))
    for ex in (MARGIN, MARGIN + PIPE_W):
        pygame.draw.line(hero, (230, 60, 60), (ex, 0), (ex, hero_h), 1)
    return hero, hero_h


def _closeup(pal, seed, scale=3):
    """Zoom on the skybridge + upper shafts so the ribs, ring-bands, bridge
    struts and pinnacles are checkable."""
    surf = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    br = pygame.Rect(MARGIN, GROUND_Y - 300, PIPE_W, 300)
    tr = pygame.Rect(MARGIN, 0, PIPE_W, 0)
    candidate_petronas_twins(surf, tr, br, pal, seed=seed)
    crop = pygame.Surface((CACHE_W, 150))
    crop.blit(_bg(CACHE_W, 150, pal, 150), (0, 0))
    crop.blit(surf, (0, -(GROUND_Y - 300)))
    return pygame.transform.scale(
        crop, (crop.get_width() * scale, crop.get_height() * scale))


def _blackout(pal, section_h, scale):
    """Solid-black silhouette of a hero section — the twin-slot / paired-mast
    test. Backing keeps the alpha column solid (no killzone); the twin read
    comes from the two gutter-spilling shoulders + two masts on top."""
    surf = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    br = pygame.Rect(MARGIN, GROUND_Y - section_h, PIPE_W, section_h)
    tr = pygame.Rect(MARGIN, 0, PIPE_W, 0)
    candidate_petronas_twins(surf, tr, br, pal, seed=7)
    pad_x = 26
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


def main():
    pal = biome.palette_for_phase(PHASE_DAY)
    pal_n = biome.palette_for_phase(PHASE_NIGHT)

    _, mid_d, _ = _steel_triad(pal)
    _, mid_n, _ = _steel_triad(pal_n)
    print("STEEL BODY (mid tone)")
    print(f"  DAY   mid={mid_d} lum={_lum(mid_d):.1f}")
    print(f"  NIGHT mid={mid_n} lum={_lum(mid_n):.1f}")
    print(f"  day != night: {mid_d != mid_n}")

    bl, bm, bs = _backing_triad(pal)
    print("RECESSED BACKING vs STEEL (slot must read darker than shafts)")
    print(f"  DAY  backing-mid lum={_lum(bm):.1f}  steel-mid lum={_lum(mid_d):.1f}"
          f"  delta={_lum(mid_d) - _lum(bm):.1f}  "
          f"[{'RECESS' if _lum(mid_d) - _lum(bm) > 12 else 'FLAT'}]")

    hero_day, hd_h = _hero(pal, 7)
    hero_night, hn_h = _hero(pal_n, 7)
    close = _closeup(pal, 7)

    # Twin-gap + fill-gate audit at 70/210/355.
    strip_heights = [70, 210, 355]
    strips = []
    print("FILL GATE (max empty vertical run inside the 58px PIPE_W band)")
    for h in strip_heights:
        s = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
        br = pygame.Rect(MARGIN, GROUND_Y - h, PIPE_W, h)
        tr = pygame.Rect(MARGIN, 0, PIPE_W, 0)
        candidate_petronas_twins(s, tr, br, pal, seed=7)
        cx = MARGIN + PIPE_W // 2
        run = _max_empty_run(s, MARGIN, MARGIN + PIPE_W, GROUND_Y - h, GROUND_Y)
        cgap = _central_gap(s, cx, GROUND_Y - h, GROUND_Y, band=8)
        crop = pygame.Surface((CACHE_W, h + 8))
        crop.blit(_bg(CACHE_W, h + 8, pal, h), (0, 0))
        crop.blit(s, (0, -(GROUND_Y - h)))
        for ex in (MARGIN, MARGIN + PIPE_W):
            pygame.draw.line(crop, (230, 60, 60), (ex, 0), (ex, h + 8), 1)
        strips.append((h, crop, run, cgap))
        ok = run <= 12 and cgap <= 12
        print(f"  h={h:3d}  band run={run:2d}px  central-slot run={cgap:2d}px  "
              f"[{'OK' if ok else 'FAIL'}]")

    # Mirror clearance — top (flipped) masts reaching the gap line.
    gap_probe = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    gp_bot = pygame.Rect(MARGIN, 251, PIPE_W, GROUND_Y - 251)
    gp_top = pygame.Rect(MARGIN, 0, PIPE_W, 101)
    candidate_petronas_twins(gap_probe, gp_top, gp_bot, pal, seed=7)
    # Bottom pillar rises from the ground: its mast sits just BELOW its top rim
    # (251), so probe DOWN into the section. Top pillar hangs flipped: probe UP.
    clear_bot = _gap_rim_clearance(gap_probe, MARGIN, MARGIN + PIPE_W, 251, up=False)
    clear_top = _gap_rim_clearance(gap_probe, MARGIN, MARGIN + PIPE_W, 100, up=True)
    print("MIRROR CLEARANCE (vertical-flip mirror, gap line)")
    print(f"  bottom mast -> gap: {clear_bot}px   top mast -> gap: {clear_top}px")

    bo1 = _blackout(pal, 130, 1)
    bo3 = _blackout(pal, 130, 3)

    # ── compose the sheet ──
    pad = 12
    label_h = 22
    head_h = 84
    title = pygame.font.SysFont(None, 30)
    sub = pygame.font.SysFont(None, 18)
    lab = pygame.font.SysFont(None, 19)

    col_hero = CACHE_W
    col_close = close.get_width()
    col_bo = max(bo3.get_width(), bo1.get_width()) + 20
    strips_total_h = sum(c.get_height() + label_h + pad for _, c, _, _ in strips)

    body_h = max(hd_h, hn_h, close.get_height(),
                 strips_total_h, bo3.get_height() + 40) + label_h
    sheet_w = pad + col_hero + pad + col_hero + pad + col_hero + pad + \
        col_close + pad + col_bo + pad
    sheet_h = head_h + body_h + pad * 2
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((24, 25, 30))

    sheet.blit(title.render(
        "petronas_twins — twin steel towers + skybridge  ·  round_2",
        True, (245, 240, 230)), (pad, 12))
    sheet.blit(sub.render(
        "red edges = PIPE_W (58px) collision band  ·  cool steel-glass shafts, "
        "vertical specular ribs + bronze setback ring-bands  ·  DIM recessed "
        "backing fills the twin slot (no killzone)  ·  TWIN-CROWN backing top "
        "(two humps + centre dip)  ·  continuous needle-ball-pyramid spine  ·  "
        "double-decker skybridge  ·  symmetric flip",
        True, (170, 172, 182)), (pad, 42))
    sheet.blit(sub.render(
        f"KILLZONE-SAFE: full-column backing -> central-slot run stays <=12px at "
        f"70/210/355  ·  twin-crown dip {_BACK_DIP}px carves sky between the tops "
        f"(top-only, no killzone)  ·  mast->gap clear {clear_bot}/{clear_top}px",
        True, (150, 210, 160)), (pad, 60))

    x = pad
    y = head_h
    sheet.blit(hero_day, (x, y))
    pygame.draw.rect(sheet, (60, 62, 72), (x, y, col_hero, hd_h), 1)
    sheet.blit(lab.render("HERO — DAY (0.30)", True, (255, 224, 150)),
               (x, y + hd_h + 4))

    x += col_hero + pad
    sheet.blit(hero_night, (x, y))
    pygame.draw.rect(sheet, (60, 62, 72), (x, y, col_hero, hn_h), 1)
    sheet.blit(lab.render("HERO — NIGHT (0.85)", True, (255, 224, 150)),
               (x, y + hn_h + 4))

    x += col_hero + pad
    sy = head_h
    sheet.blit(lab.render("FILL GATE — twin-slot audit", True, (255, 224, 150)),
               (x, sy - 20))
    for h, crop, run, cgap in strips:
        sheet.blit(crop, (x, sy))
        pygame.draw.rect(sheet, (60, 62, 72), (x, sy, col_hero, crop.get_height()), 1)
        ok = run <= 12 and cgap <= 12
        sheet.blit(lab.render(f"h={h}  band {run}px  slot {cgap}px  "
                              f"[{'OK' if ok else 'FAIL'}]", True,
                              (200, 235, 170) if ok else (255, 140, 140)),
                   (x, sy + crop.get_height() + 4))
        sy += crop.get_height() + label_h + pad

    x += col_hero + pad
    sheet.blit(close, (x, head_h))
    pygame.draw.rect(sheet, (60, 62, 72),
                     (x, head_h, close.get_width(), close.get_height()), 1)
    sheet.blit(lab.render("SKYBRIDGE + CROWN 3x", True,
                          (255, 224, 150)), (x, head_h + close.get_height() + 4))

    x += col_close + pad
    sheet.blit(lab.render("BLACKOUT — two tops + sky notch", True, (255, 224, 150)),
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
