"""kappa_suijin — high-fidelity KAPPA water-imp totem (candidate).

A stacked totem of turtle-beaked river-imp masks. Each moss-jade head wears the
kappa's signature concave sara water-DISH on its crown, has big round wet eyes
and a hard keratin BEAK, with darker-green turtle-shell scutes on the jaw. The
stack is capped at the gap rim by a hero ceremonial dish — a bronze-rimmed
concave bowl holding a still pool that catches a night glint.

Re-skin of the winning `moai_ancestor` stacked-head skeleton: same adaptive
head COUNT driver, `_hw_at` full-width column (so the 58 px collision band stays
solid), neck-waist seams, plinth + foliage base, and the symmetric vertical-flip
mirror. Only the material triad (dark basalt -> moss-jade green), the relief
(carved ancestor face -> beak + dish + wet eyes) and the topper (red scoria drum
-> water dish) change.

The make-or-break is the concave dish. A dish is an inward dip, which risks
opening an empty band in the collision column. It is defeated by construction:
the water is a SHALLOW inset painted on top of a SOLID skull dome, and the dish
RIM stays solid across the full width — the concave read is carried by the
raised side-lips + interior bowl shading, while the silhouette's center dips at
most a few pixels (well under the 12 px fill-gate ceiling). No hole ever opens.

Standalone review candidate. Imports the REAL pagoda helpers so its materials,
lighting and night glow match the shipped pillars exactly; wires nothing into
the live game.

Run:  python docs/pillar_landmarks/japanese_totems/kappa_suijin/render.py
Out:  docs/pillar_landmarks/japanese_totems/kappa_suijin/round_1.png
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

# Real pagoda helpers — same materials + lighting language as the shipped pillars.
from game.pillar_pagodas import (
    _mix, _shade, _gradient_rect, _aa_polyline, _lit_niche, _tile_hatch,
    _draw_plinth_mist, _is_dark_sky, _is_warming_sky,
    _cap_lit_for_dark_sky, _cap_dark_for_dark_sky,
    _buddha_eye, _porcelain_aqua, _pond_aqua, _bronze, _gold_bright,
    _vermilion, _iron_brown,
)
from game.pillar_variants import draw_grass_bed
from game.draw import draw_side_shrub


MARGIN = 64                       # matches entities.Pipe eave/ornament gutter
CACHE_W = PIPE_W + MARGIN * 2
CACHE_H = GROUND_Y
PHASE_DAY = 0.30                  # midday tan sky — hardest test for green-not-sky
PHASE_NIGHT = 0.85               # deep night — checks lit rim + wet-eye glow + dish glint


# ── Materials ────────────────────────────────────────────────────────────────
#
# The headline material swap vs the basalt moai: the body is a MOSS-JADE green
# pulled toward stone_mid so it reads as amphibian river-imp skin, firmly away
# from the cool porcelain tile-blue (so it never twins the white fox or dissolves
# into a day sky). All three stops derive from stone_* so the 5-min biome
# day->night retint sweeps straight through.

def _kappa_green(palette):
    # Green DOMINANT (G > R, G > B) with a faint yellow-moss cast — swamp jade,
    # not sky teal.
    return _mix(palette['stone_mid'], (72, 120, 82), 0.62)


def _kappa_green_lit(palette):
    return _mix(palette['stone_light'], (128, 182, 132), 0.56)


def _kappa_green_shadow(palette):
    return _mix(palette['stone_dark'], (38, 78, 50), 0.80)


def _greenify_night(c, palette):
    # The night biome retint desaturates the jade toward olive-GREY — its G-B
    # collapses to ~11, so at night the body reads neutral and stops earning its
    # cool-green slot beside the red totems. Lift green + sink blue/red to hold a
    # true amphibian moss (G-B >= ~22) without going neon. Gated on _is_dark_sky
    # so the textbook DAY triad passes through completely untouched.
    if not _is_dark_sky(palette):
        return c
    r, g, b = c
    return (max(0, r - 7), min(255, g + 9), max(0, b - 11))


def _body_triad(palette):
    lit = _kappa_green_lit(palette)
    mid = _kappa_green(palette)
    sh = _kappa_green_shadow(palette)
    # At night, cap the lit so the raking highlight doesn't blow out and floor the
    # shadow so the jade body doesn't sink into the sky as one black mass.
    lit = _cap_lit_for_dark_sky(lit, palette, cap=176)
    sh = _cap_dark_for_dark_sky(sh, palette, floor=44)
    # Re-saturate the whole triad at night only — the retint alone leaves it grey.
    lit = _greenify_night(lit, palette)
    mid = _greenify_night(mid, palette)
    sh = _greenify_night(sh, palette)
    return lit, mid, sh


def _shell_green(palette):
    # A darker olive-jade for the turtle-shell scutes on the jaw — one stop below
    # the shadow so the hatch reads as carapace plating, not just noise.
    return _greenify_night(_shade(_kappa_green_shadow(palette), -14), palette)


def _lum(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


# ── Head geometry ──────────────────────────────────────────────────────────
#
# Reused verbatim from moai: a tall near-full-width straight column so the 58 px
# collision band is always solid (smooth vertical silhouette, never a bulbous
# lobe), broken only by a shallow neck WAIST at each stacked seam. Gauntness of
# the ancestor is traded here for the low domed cranium + dished crown read; the
# COLUMN fill guarantee is identical.

_TAPER = 5                        # px of neck-waist ramp at each seam
_WAIST = 5                        # px each side the waist pinches in from the edge
_HEAD_H_FLOOR = 92                # natural head height -> drives adaptive COUNT


def _hw_at(y, y0, y1, half, *, crown, base):
    """Half-width of the head silhouette at row y. Full width through the body;
    a short symmetric ramp into a shallow waist at the top/bottom seams."""
    hw = float(half)
    if not crown:
        d = y - y0
        if d < _TAPER:
            hw = min(hw, (half - _WAIST) + (_WAIST) * (d / _TAPER))
    if not base:
        d = y1 - y
        if d < _TAPER:
            hw = min(hw, (half - _WAIST) + (_WAIST) * (d / _TAPER))
    return hw


def _grad_hspan(surf, y, xl, xr, lit, mid, sh):
    """One row of the head body: a horizontal 3-stop gradient, lit on the LEFT,
    shadow on the RIGHT — the raking-light model that reads the planar mass."""
    w = xr - xl
    if w < 2:
        return
    for i in range(w):
        t = i / (w - 1)
        col = _mix(lit, mid, t * 2) if t < 0.5 else _mix(mid, sh, (t - 0.5) * 2)
        surf.set_at((xl + i, y), col)


# ── One kappa mask ──────────────────────────────────────────────────────────

def _kappa_eye(surf, ex, ey, r, palette, *, thumbnail):
    """A big round WET eye: a _lit_niche socket (free night glow), a bulging
    pale-jade sclera, a bold gold rim ring, a dark wet iris + catch-light. At
    thumbnail scale it collapses to a single dark socket dot (the 2-dot
    fallback)."""
    gold = _gold_bright(palette)
    dark = palette['stone_dark']
    # Socket sized just under the eyeball so the round sclera fully covers the
    # niche rect while the additive night halo still seeps around the wet eye.
    nw = max(4, 2 * r - 2)
    _lit_niche(surf, ex, ey - r + 1, nw, nw, palette)
    if thumbnail:
        pygame.draw.circle(surf, _shade(dark, -18), (ex, ey), max(1, r - 1))
        return
    scler = _mix(_porcelain_aqua(palette), (236, 246, 232), 0.42)
    pygame.draw.circle(surf, scler, (ex, ey), r)
    pygame.draw.circle(surf, gold, (ex, ey), r, 1)          # gold rim
    pygame.draw.circle(surf, _shade(dark, -16), (ex, ey), max(1, r - 2))  # wet iris
    surf.set_at((ex - 1, ey - 1), (238, 248, 242))          # catch-light


def _draw_beak(surf, cx, y0, hh, half, palette, *, thumbnail):
    """The turtle keratin BEAK — a short, hard, DOWN-pointing wedge at the mouth,
    lit gold on its ridge and dropping into a bronze under-hook. Kept SHORT (a
    forward wedge, never a spur) so it never reads as the tengu long-nose."""
    gold = _gold_bright(palette)
    bronze = _bronze(palette)
    bronze_sh = _shade(bronze, -34)
    beak_cy = y0 + int(hh * 0.55)
    beak_hw = max(3, int(half * 0.30))
    beak_h = max(4, int(hh * 0.15))
    tip_y = beak_cy + beak_h
    if thumbnail:
        pygame.draw.line(surf, bronze_sh, (cx - beak_hw, beak_cy),
                         (cx, tip_y), 2)
        pygame.draw.line(surf, bronze_sh, (cx + beak_hw, beak_cy),
                         (cx, tip_y), 2)
        return
    # Upper mandible: a filled down-pointing triangle, lit gold.
    upper = [(cx - beak_hw, beak_cy), (cx + beak_hw, beak_cy), (cx, tip_y)]
    pygame.draw.polygon(surf, gold, upper)
    # Bronze under-hook + shadowed right cheek plane of the wedge.
    pygame.draw.polygon(surf, bronze, [(cx, beak_cy), (cx + beak_hw, beak_cy),
                                       (cx, tip_y)])
    # The mouth-line (lit keratin edge) across the top of the beak.
    _aa_polyline(surf, _shade(gold, 30),
                 [(cx - beak_hw, beak_cy), (cx + beak_hw, beak_cy)])
    # A dark hooked lip at the very tip + the AA silhouette of the wedge.
    surf.set_at((cx, tip_y), bronze_sh)
    _aa_polyline(surf, bronze_sh, [(cx - beak_hw, beak_cy), (cx, tip_y),
                                   (cx + beak_hw, beak_cy)])
    # Two nostril pits at the base of the beak.
    for nx in (cx - beak_hw // 2, cx + beak_hw // 2):
        surf.set_at((nx, beak_cy - 1), bronze_sh)


def _draw_dish_relief(surf, cx, y0, hh, half, palette):
    """The sara water-DISH as INTERIOR relief on one head's crown — a top-down
    bronze-rimmed bowl of still water painted on the already-solid dome (so it
    never breaks the silhouette). The per-head kappa tell that the hero crown
    then echoes at the gap rim."""
    bronze = _bronze(palette)
    bronze_lit = _shade(bronze, 30)
    bronze_sh = _shade(bronze, -34)
    water = _pond_aqua(palette)
    water_lit = _mix(water, (224, 242, 236), 0.55)
    dark_sky = _is_dark_sky(palette)

    dw = max(10, int(half * 1.5))
    dh = max(5, int(hh * 0.15))
    rect = pygame.Rect(cx - dw // 2, y0 + 2, dw, dh)
    # Bronze rim ring (raised lip) around the bowl.
    pygame.draw.ellipse(surf, bronze, rect)
    pygame.draw.ellipse(surf, bronze_lit, rect, 1)
    pygame.draw.arc(surf, bronze_sh, rect, math.pi, math.pi * 2, 1)  # lit far lip
    # Still water pool inset — a smaller ellipse, glossy toward the far edge.
    inner = rect.inflate(-4, -3)
    pygame.draw.ellipse(surf, _shade(water, -22), inner)
    hi = inner.inflate(-2, -inner.height // 2)
    hi.y = inner.y + 1
    pygame.draw.ellipse(surf, water_lit, hi)                # top-lit water sheen
    # Water glint — a single bright dot; a cool star at night.
    gx, gy = cx - dw // 6, y0 + 3
    if dark_sky:
        surf.set_at((gx, gy), (236, 248, 244))
        surf.set_at((gx + 1, gy), (200, 224, 220))
        surf.set_at((gx, gy + 1), (200, 224, 220))
    else:
        surf.set_at((gx, gy), (232, 244, 240))


def _draw_head(surf, cx, y0, y1, half, palette, rng, *, crown, base):
    hh = y1 - y0
    lit, mid, sh = _body_triad(palette)
    dark_sky = _is_dark_sky(palette)

    # Silhouette outline (AA keyline + night rim-light).
    left_pts = []
    right_pts = []
    for y in range(y0, y1):
        hw = _hw_at(y, y0, y1, half, crown=crown, base=base)
        xl = int(round(cx - hw))
        xr = int(round(cx + hw))
        _grad_hspan(surf, y, xl, xr, lit, mid, sh)
        left_pts.append((xl, y))
        right_pts.append((xr, y))

    thumbnail = hh < 50

    brow_dark = _shade(mid, -42)
    ridge_lit = _shade(lit, 30)

    # Eyes: big round wet eyes, set high + wide (amphibian, on the dome front).
    eye_y = y0 + int(hh * 0.34)
    eye_dx = int(half * 0.42)
    eye_r = max(3, int(half * 0.24))
    _kappa_eye(surf, cx - eye_dx, eye_y, eye_r, palette, thumbnail=thumbnail)
    _kappa_eye(surf, cx + eye_dx, eye_y, eye_r, palette, thumbnail=thumbnail)

    # Beak (short down-wedge) at the mouth.
    _draw_beak(surf, cx, y0, hh, half, palette, thumbnail=thumbnail)

    if not thumbnail:
        # Low brow ridge shading the eyes — a soft shadow band, not the moai
        # shelf (kappa cranium is smooth + domed).
        brow_y = eye_y - eye_r - 1
        pygame.draw.line(surf, brow_dark, (cx - int(half * 0.62), brow_y),
                         (cx - eye_dx // 3, brow_y - 1), 1)
        pygame.draw.line(surf, brow_dark, (cx + eye_dx // 3, brow_y - 1),
                         (cx + int(half * 0.62), brow_y), 1)
        # Sunken cheeks flanking the beak (shadow crescents).
        cheek_y = y0 + int(hh * 0.58)
        pygame.draw.line(surf, _shade(sh, -18),
                         (cx - int(half * 0.72), cheek_y - 2),
                         (cx - int(half * 0.42), cheek_y + 3), 1)
        pygame.draw.line(surf, _shade(sh, -18),
                         (cx + int(half * 0.42), cheek_y + 3),
                         (cx + int(half * 0.72), cheek_y - 2), 1)

        # Turtle-shell SCUTES on the lower jaw — a darker-green hatch plate.
        scute_top = y0 + int(hh * 0.76)
        scute_bot = y1 - max(2, int(hh * 0.05))
        shell = _shell_green(palette)
        for sy in range(scute_top, scute_bot, 3):
            _tile_hatch(surf, cx - int(half * 0.66), sy,
                        cx + int(half * 0.66), sy, shell, step=6)
        # A central scute seam + jaw shadow.
        pygame.draw.line(surf, _shade(shell, -14),
                         (cx, scute_top), (cx, scute_bot), 1)
        pygame.draw.line(surf, brow_dark,
                         (cx - int(half * 0.6), scute_top),
                         (cx + int(half * 0.6), scute_top), 1)

        # Per-head sara dish relief on the crown (top head is capped by the hero
        # crown instead, so skip it there to avoid a doubled bowl).
        if not crown:
            _draw_dish_relief(surf, cx, y0, hh, half, palette)
    else:
        # Thumbnail relief: guarantee the kappa reads on 2 socket dots + the
        # beak wedge + a shell hint alone at ~40 px face height.
        shell = _shell_green(palette)
        _tile_hatch(surf, cx - int(half * 0.6), y1 - 4,
                    cx + int(half * 0.6), y1 - 4, shell, step=5)

    # AA silhouette keyline.
    outline = left_pts + list(reversed(right_pts))
    _aa_polyline(surf, _shade(sh, -20), outline, closed=True)

    # Night rim-light down the LEFT edge so the jade holds its silhouette against
    # a dark sky (a quiet cool edge by day).
    rim = _shade(lit, 46) if dark_sky else _shade(lit, 16)
    step = 1 if dark_sky else 2
    # By DAY the lit LEFT rim is near-isoluminant with the mid/upper blue sky
    # (dL ~ -4), so it washes out. Lay a thin dark keyline one pixel OUTSIDE the
    # lit rim (into the eave gutter, clear of the 58 px collision band) so the
    # green→sky boundary always holds — the shadow/right edge already carries its
    # own dark AA keyline.
    if not dark_sky:
        key = _shade(sh, -26)
        for x, y in left_pts:
            if x - 1 >= 0:
                surf.set_at((x - 1, y), key)
    for i in range(0, len(left_pts), step):
        x, y = left_pts[i]
        surf.set_at((x, y), rim)
        if dark_sky and x + 1 < cx:
            surf.set_at((x + 1, y), _mix(rim, mid, 0.5))


# ── Sara crown (the hero water dish at the gap rim) ─────────────────────────

def _draw_sara_crown(surf, cx, y_top, y_bot, half, palette):
    """The ceremonial water DISH crowning the stack at the gap rim. A SOLID
    domed skull-drum whose top silhouette is a SHALLOW concave arc (the raised
    side-lips + a few-pixel center dip = the inward tell), holding a still pool
    with a bright rim and a night glint. Because the drum body is solid all the
    way down and the center dip is only ~6 px, no empty run ever opens under the
    dish — the rim reads solid + WIDE at the gap line."""
    lit, mid, sh = _body_triad(palette)
    bronze = _bronze(palette)
    bronze_lit = _shade(bronze, 32)
    bronze_sh = _shade(bronze, -34)
    water = _pond_aqua(palette)
    water_lit = _mix(water, (226, 244, 238), 0.58)
    water_sh = _shade(water, -30)
    dark_sky = _is_dark_sky(palette)

    # ~1.2x the head so the blackout reads "domed post + distinct wide dish"
    # (the kappa tell); the overhang stays inside the eave/ornament MARGIN gutter
    # so it never widens the 58 px collision band.
    pw = int(half * 2 * 1.20)
    x0 = cx - pw // 2
    # The center trough is the ONLY inward-dome silhouette tell, so push it as deep
    # as the fill gate allows: rim_top+dip is the topmost solid pixel of the center
    # column, so (rim_top - y_top) + dip must stay <= 12. Raise the lips (rim_top =
    # y_top+1) and deepen the center to ~10 px, but clamp to the crown height so a
    # short crown at h=70 never troughs BELOW its own base and opens a hole.
    rim_top = y_top + 1                # raised side-lip height
    dip = min(10, max(5, (y_bot - y_top) - 3))
    hpw = pw / 2.0

    # 1. Solid domed drum: fill every column from its concave top edge down to
    #    the neck. The top edge dips in the CENTER (a bowl), rises at the lips.
    tops = []
    for x in range(pw):
        dx = (x - pw / 2.0) / hpw       # -1 .. 1
        frac = max(0.0, 1.0 - dx * dx)  # 1 at center, 0 at lips
        top_y = rim_top + dip * frac
        tops.append(top_y)
        col_t = x / max(1, pw - 1)
        col = (_mix(lit, mid, col_t * 2) if col_t < 0.5
               else _mix(mid, sh, (col_t - 0.5) * 2))
        pygame.draw.line(surf, col, (x0 + x, int(top_y)), (x0 + x, y_bot), 1)

    # 2. Bronze rim band tracing the concave lip (the solid dish edge).
    rim_pts = [(x0 + x, int(tops[x])) for x in range(0, pw, 2)]
    _aa_polyline(surf, bronze, rim_pts)
    _aa_polyline(surf, bronze_lit, [(px, py + 1) for px, py in rim_pts])
    # Lip end-caps stand proud so the rim reads raised at both sides.
    pygame.draw.line(surf, bronze_lit, (x0, rim_top), (x0 + 2, rim_top + 2), 2)
    pygame.draw.line(surf, bronze_sh, (x0 + pw - 3, rim_top + 2),
                     (x0 + pw - 1, rim_top), 2)

    # 3. Still water pool inset in the concave depression (below the rim).
    inset = 4
    wl_top = rim_top + 3
    wl_bot = rim_top + dip + max(4, int((y_bot - y_top) * 0.30))
    wl_bot = min(wl_bot, y_bot - 2)
    for x in range(inset, pw - inset):
        dx = (x - pw / 2.0) / hpw
        frac = max(0.0, 1.0 - dx * dx)
        wt = wl_top + dip * frac
        for y in range(int(wt), wl_bot):
            # Clamp to [0,1] — int(wt) can truncate below wt on the top row, and
            # an out-of-range t would extrapolate the water color past 255.
            vt = min(1.0, max(0.0, (y - wt) / max(1, wl_bot - wt)))
            col = _mix(water_lit, water, min(1.0, vt * 1.6)) if vt < 0.6 \
                else _mix(water, water_sh, (vt - 0.6) / 0.4)
            surf.set_at((x0 + x, y), col)
    # Bronze inner shadow ring where the water meets the bowl wall.
    inner_rim = [(x0 + x, int(wl_top + dip * max(0.0, 1 - ((x - pw / 2.0) / hpw) ** 2)))
                 for x in range(inset, pw - inset, 2)]
    _aa_polyline(surf, bronze_sh, inner_rim)

    # 4. Water glint — a single bright dot by day; a cool 3-px star at night.
    gx, gy = cx - pw // 6, wl_top + 2
    if dark_sky:
        surf.set_at((gx, gy), (238, 250, 246))
        surf.set_at((gx - 1, gy), (198, 224, 220))
        surf.set_at((gx + 1, gy), (198, 224, 220))
        surf.set_at((gx, gy - 1), (198, 224, 220))
        surf.set_at((gx, gy + 1), (198, 224, 220))
    else:
        surf.set_at((gx, gy), (234, 246, 242))
        surf.set_at((gx + 1, gy), water_lit)

    # 5. Darker neck band on the head just under the drum so the dish pops as a
    #    crown on a darker post (same trick as the moai pukao neck).
    neck_dark = _shade(sh, -16)
    nb_hw = int(half * 0.92)
    for k in range(3):
        t = 1.0 - k / 3.0
        pygame.draw.line(surf, _mix(mid, neck_dark, t),
                         (cx - nb_hw, y_bot + k), (cx + nb_hw, y_bot + k), 1)


# ── 3-layer plinth + foliage ────────────────────────────────────────────────

def _draw_plinth(surf, cx, base_y, half, palette, seed):
    lit, mid, sh = _body_triad(palette)
    layers = 3
    for i in range(layers):
        lw = int(half * 2 * (1.12 + 0.16 * i))
        lh = 5
        ly = base_y - (layers - i) * lh
        r = pygame.Rect(cx - lw // 2, ly, lw, lh)
        _gradient_rect(surf, r, lit, mid, sh)
        pygame.draw.line(surf, _shade(sh, -20),
                         (r.x, r.bottom - 1), (r.right - 1, r.bottom - 1), 1)
        pygame.draw.line(surf, _shade(lit, 18), (r.x, r.y), (r.right - 1, r.y), 1)


def _draw_tower(surf, cx, y_top, y_bot, palette, seed):
    """One upright kappa tower: mist -> plinth -> foliage -> adaptive head stack
    -> sara water dish at the gap rim. Height-adaptive head COUNT keeps every
    head un-squashed (1 big kappa at ~70 px, several at 355)."""
    rng = random.Random(seed)
    half = PIPE_W // 2
    section_h = y_bot - y_top

    plinth_h = min(15, max(9, int(section_h * 0.14)))
    dish_h = min(20, max(11, int(section_h * 0.17)))
    if section_h < 100:
        plinth_h = max(7, plinth_h - 2)
        dish_h = max(10, dish_h - 2)
    base_y = y_bot

    _draw_plinth_mist(surf, cx, base_y - plinth_h + 2, int(half * 2 * 1.6), palette)

    stack_bot = base_y - plinth_h
    stack_top = y_top + dish_h
    avail = stack_bot - stack_top
    if avail < 24:
        avail = 24
        stack_top = stack_bot - avail
    count = max(1, round(avail / _HEAD_H_FLOOR))
    hh = avail / count

    for i in range(count):
        hy_bot = int(round(stack_bot - i * hh))
        hy_top = int(round(stack_bot - (i + 1) * hh))
        _draw_head(surf, cx, hy_top, hy_bot, half, palette, rng,
                   crown=(i == count - 1), base=(i == 0))

    # Sara water dish crowns the top head and reaches the gap rim.
    _draw_sara_crown(surf, cx, y_top, stack_top, half, palette)

    _draw_plinth(surf, cx, base_y, half, palette, seed)
    draw_grass_bed(surf, cx, base_y - 1, PIPE_W + 12, 12, palette, seed=seed)
    draw_side_shrub(surf, cx - half - 6, base_y - 1, palette, scale=0.9)
    draw_side_shrub(surf, cx + half + 6, base_y - 1, palette, scale=0.8)


def candidate_kappa_suijin(surf, top_rect, bot_rect, palette, seed):
    """Bottom = kappa tower rising from the ground, sara dish at the gap. Top =
    the same tower vertical-FLIPPED from the ceiling — a symmetric two-ended
    totem, its dishes meeting at the rim. On the flipped copy the concave dish
    domes UP into the gap, reading as the belly-shell — still a coherent kappa."""
    if bot_rect.height > 0:
        _draw_tower(surf, bot_rect.centerx, bot_rect.y, bot_rect.bottom,
                    palette, seed)
    if top_rect.height > 0:
        tmp = pygame.Surface((surf.get_width(), top_rect.height), pygame.SRCALPHA)
        _draw_tower(tmp, top_rect.centerx, 0, top_rect.height, palette, seed + 1)
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
    worst_x = x0
    for x in range(x0, x1):
        run = 0
        for y in range(y0, y1):
            if surf.get_at((x, y))[3] == 0:
                run += 1
                if run > worst:
                    worst = run
                    worst_x = x
            else:
                run = 0
    return worst, worst_x


def _gap_rim_clearance(surf, x0, x1, gap_y, up=True):
    step = -1 if up else 1
    for d in range(0, 200):
        y = gap_y + step * d
        if y < 0 or y >= surf.get_height():
            return d
        if any(surf.get_at((x, y))[3] > 0 for x in range(x0, x1)):
            return d
    return 200


def _dish_dip_depth(pal, section_h=118, seed=7):
    """Measure the inward-dome tell in the silhouette: the vertical drop from the
    highest dish-lip pixel to the lowest center-trough pixel of the crown's top
    edge. This is what makes the topper read INWARD, not a flat saucer."""
    surf = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    br = pygame.Rect(MARGIN, GROUND_Y - section_h, PIPE_W, section_h)
    tr = pygame.Rect(MARGIN, 0, PIPE_W, 0)
    candidate_kappa_suijin(surf, tr, br, pal, seed=seed)
    y_top = GROUND_Y - section_h
    tops = {}
    for x in range(MARGIN - 12, MARGIN + PIPE_W + 12):
        for y in range(y_top, y_top + 40):
            if surf.get_at((x, y))[3] > 40:
                tops[x] = y
                break
    if not tops:
        return 0
    lip = min(tops.values())          # highest solid pixel (the raised lips)
    trough = max(v for v in tops.values() if v < y_top + 30)  # lowest crown top
    return trough - lip


def _dish_rim_run(pal, section_h=355, seed=7):
    """Prove the concave dish presents a SOLID rim: the max empty vertical run
    across the top-of-dish rows must stay under the 12 px fill-gate ceiling."""
    surf = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    br = pygame.Rect(MARGIN, GROUND_Y - section_h, PIPE_W, section_h)
    tr = pygame.Rect(MARGIN, 0, PIPE_W, 0)
    candidate_kappa_suijin(surf, tr, br, pal, seed=seed)
    y_top = GROUND_Y - section_h
    dish_h = min(20, max(11, int(section_h * 0.17)))
    run, wx = _max_empty_run(surf, MARGIN, MARGIN + PIPE_W, y_top, y_top + dish_h + 6)
    return run


def _hero(pal, seed):
    gap_y, gap_h = 168, 150
    top_h = int(gap_y - gap_h / 2)
    bot_top = int(gap_y + gap_h / 2)
    full = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    top_rect = pygame.Rect(MARGIN, 0, PIPE_W, top_h)
    bot_rect = pygame.Rect(MARGIN, bot_top, PIPE_W, GROUND_Y - bot_top)
    candidate_kappa_suijin(full, top_rect, bot_rect, pal, seed=seed)

    tip_y = top_h - 6
    base_y = GROUND_Y + 8
    hero_h = base_y - tip_y
    hero = _bg(CACHE_W, hero_h, pal, hero_h - (base_y - GROUND_Y))
    hero.blit(full, (0, -tip_y))
    for ex in (MARGIN, MARGIN + PIPE_W):
        pygame.draw.line(hero, (230, 60, 60), (ex, 0), (ex, hero_h), 1)
    return hero, hero_h


def _closeup(pal, seed, scale=3):
    """Zoom on a single ground head so the beak + eyes + dish relief are
    checkable."""
    surf = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    br = pygame.Rect(MARGIN, GROUND_Y - 150, PIPE_W, 150)
    tr = pygame.Rect(MARGIN, 0, PIPE_W, 0)
    candidate_kappa_suijin(surf, tr, br, pal, seed=seed)
    crop = pygame.Surface((CACHE_W, 120))
    crop.blit(_bg(CACHE_W, 120, pal, 120), (0, 0))
    crop.blit(surf, (0, -(GROUND_Y - 150)))
    return pygame.transform.scale(
        crop, (crop.get_width() * scale, crop.get_height() * scale))


def _blackout(pal, section_h, scale):
    """Solid-black silhouette of a hero section — the domed-head + concave-dish
    tell test."""
    surf = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    br = pygame.Rect(MARGIN, GROUND_Y - section_h, PIPE_W, section_h)
    tr = pygame.Rect(MARGIN, 0, PIPE_W, 0)
    candidate_kappa_suijin(surf, tr, br, pal, seed=7)
    pad_x = 12
    crop = pygame.Surface((PIPE_W + pad_x * 2, section_h + 8), pygame.SRCALPHA)
    crop.fill((238, 238, 240))
    for x in range(CACHE_W):
        for y in range(GROUND_Y - section_h, GROUND_Y):
            if surf.get_at((x, y))[3] > 40:
                cx = x - MARGIN + pad_x
                cy = y - (GROUND_Y - section_h) + 4
                if 0 <= cx < crop.get_width() and 0 <= cy < crop.get_height():
                    crop.set_at((cx, cy), (18, 18, 22))
    return pygame.transform.scale(
        crop, (crop.get_width() * scale, crop.get_height() * scale))


def main():
    pal = biome.palette_for_phase(PHASE_DAY)
    pal_n = biome.palette_for_phase(PHASE_NIGHT)

    # Body-hue proof: must read GREEN (G dominant, not sky-blue) and DAY != NIGHT.
    _, mid_d, _ = _body_triad(pal)
    _, mid_n, _ = _body_triad(pal_n)
    print("BODY MOSS-JADE (mid tone)")
    print(f"  DAY   mid={mid_d} lum={_lum(mid_d):.1f}  G-R={mid_d[1]-mid_d[0]} "
          f"G-B={mid_d[1]-mid_d[2]}")
    print(f"  NIGHT mid={mid_n} lum={_lum(mid_n):.1f}  G-R={mid_n[1]-mid_n[0]} "
          f"G-B={mid_n[1]-mid_n[2]}")
    print(f"  green dominant day: {mid_d[1] > mid_d[0] and mid_d[1] > mid_d[2]}  "
          f"night: {mid_n[1] > mid_n[0] and mid_n[1] > mid_n[2]}")
    print(f"  day != night: {mid_d != mid_n}")

    # Dish-rim solidity — the make-or-break: no >12 px empty run under the dish.
    rr_d = _dish_rim_run(pal)
    rr_n = _dish_rim_run(pal_n)
    print("DISH-RIM SOLIDITY (max empty run under the sara dish, target <= 12)")
    print(f"  DAY   run={rr_d}px  [{'OK' if rr_d <= 12 else 'FAIL'}]")
    print(f"  NIGHT run={rr_n}px  [{'OK' if rr_n <= 12 else 'FAIL'}]")

    # Inward-dome tell — the concave trough depth in the 58px blackout silhouette.
    dip_d = _dish_dip_depth(pal)
    print(f"DISH CONCAVITY (silhouette lip->trough drop at 58px, target ~9-10)")
    print(f"  DAY   dip={dip_d}px")

    hero_day, hd_h = _hero(pal, 7)
    hero_night, hn_h = _hero(pal_n, 7)
    close_day = _closeup(pal, 7)
    close_night = _closeup(pal_n, 7)

    # Gap-rim clearance (bottom + top tower dish reaching the gap line).
    gap_probe = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    gp_bot = pygame.Rect(MARGIN, 243, PIPE_W, GROUND_Y - 243)
    gp_top = pygame.Rect(MARGIN, 0, PIPE_W, 93)
    candidate_kappa_suijin(gap_probe, gp_top, gp_bot, pal, seed=7)
    # Bottom crown sits at the top of bot_rect pointing UP into the gap, so scan
    # DOWN from the gap line to find how far the dish rim is recessed; the flipped
    # top crown points DOWN, so scan UP from its gap line.
    clear_bot = _gap_rim_clearance(gap_probe, MARGIN, MARGIN + PIPE_W, 243, up=False)
    clear_top = _gap_rim_clearance(gap_probe, MARGIN, MARGIN + PIPE_W, 93, up=True)
    print("GAP-RIM CLEARANCE")
    print(f"  bottom dish -> gap: {clear_bot}px   top(flipped) dish -> gap: "
          f"{clear_top}px")

    # Feasibility strip: bottom section at three heights + empty-run gate.
    strip_heights = [70, 210, 355]
    strips = []
    print("FILL GATE (max empty vertical run inside the 58px PIPE_W band)")
    for h in strip_heights:
        s = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
        br = pygame.Rect(MARGIN, GROUND_Y - h, PIPE_W, h)
        tr = pygame.Rect(MARGIN, 0, PIPE_W, 0)
        candidate_kappa_suijin(s, tr, br, pal, seed=7)
        run, wx = _max_empty_run(s, MARGIN, MARGIN + PIPE_W, GROUND_Y - h, GROUND_Y)
        crop = pygame.Surface((CACHE_W, h + 8))
        crop.blit(_bg(CACHE_W, h + 8, pal, h), (0, 0))
        crop.blit(s, (0, -(GROUND_Y - h)))
        for ex in (MARGIN, MARGIN + PIPE_W):
            pygame.draw.line(crop, (230, 60, 60), (ex, 0), (ex, h + 8), 1)
        strips.append((h, crop, run))
        print(f"  h={h:3d}  max empty run = {run}px  [{'OK' if run <= 12 else 'FAIL'}]")

    bo1 = _blackout(pal, 118, 1)
    bo3 = _blackout(pal, 118, 3)

    # ── compose the sheet ──
    pad = 12
    label_h = 22
    head_h = 82
    title = pygame.font.SysFont(None, 30)
    sub = pygame.font.SysFont(None, 18)
    lab = pygame.font.SysFont(None, 19)

    col_hero = CACHE_W
    col_close = close_day.get_width()
    col_bo = max(bo3.get_width(), bo1.get_width()) + 20
    strips_total_h = sum(c.get_height() + label_h + pad for _, c, _ in strips)

    body_h = max(hd_h, hn_h, close_day.get_height() * 2 + label_h + pad,
                 strips_total_h, bo3.get_height() + 40) + label_h
    sheet_w = pad + col_hero + pad + col_hero + pad + col_hero + pad + \
        col_close + pad + col_bo + pad
    sheet_h = head_h + body_h + pad * 2
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((22, 27, 24))

    sheet.blit(title.render(
        "kappa_suijin — moss-jade water-imp totem (beak + sara dish)  ·  round_2",
        True, (232, 244, 232)), (pad, 12))
    sheet.blit(sub.render(
        "red edges = PIPE_W (58px) collision band  ·  moss-JADE body (night re-saturated)  ·  "
        "round wet eyes + keratin BEAK + turtle scutes  ·  DEEPENED concave sara DISH  ·  "
        "symmetric ceiling flip", True, (168, 182, 172)), (pad, 40))
    sheet.blit(sub.render(
        f"FIXES: night G-B {mid_n[1]-mid_n[2]} (>=22)  ·  dish trough {dip_d}px (was ~5, inward now)  "
        f"·  dark day keyline outside lit rim  ·  dish rim run day {rr_d}/night {rr_n}px (<=12), "
        f"water is a shallow inset on a SOLID dome — never a hole",
        True, (150, 210, 160)), (pad, 56))

    x = pad
    y = head_h
    sheet.blit(hero_day, (x, y))
    pygame.draw.rect(sheet, (58, 72, 62), (x, y, col_hero, hd_h), 1)
    sheet.blit(lab.render("HERO — DAY (0.30)", True, (170, 232, 180)),
               (x, y + hd_h + 4))

    x += col_hero + pad
    sheet.blit(hero_night, (x, y))
    pygame.draw.rect(sheet, (58, 72, 62), (x, y, col_hero, hn_h), 1)
    sheet.blit(lab.render("HERO — NIGHT (0.85)", True, (170, 232, 180)),
               (x, y + hn_h + 4))

    # feasibility strips
    x += col_hero + pad
    sy = head_h
    sheet.blit(lab.render("FILL GATE — bottom section", True, (170, 232, 180)),
               (x, sy - 20))
    for h, crop, run in strips:
        sheet.blit(crop, (x, sy))
        pygame.draw.rect(sheet, (58, 72, 62), (x, sy, col_hero, crop.get_height()), 1)
        ok = "OK" if run <= 12 else "FAIL"
        sheet.blit(lab.render(f"h={h}px  ·  run {run}px  [{ok}]", True,
                              (200, 235, 170) if run <= 12 else (255, 140, 140)),
                   (x, sy + crop.get_height() + 4))
        sy += crop.get_height() + label_h + pad

    # face close-ups: day over night
    x += col_hero + pad
    sheet.blit(close_day, (x, head_h))
    pygame.draw.rect(sheet, (58, 72, 62),
                     (x, head_h, close_day.get_width(), close_day.get_height()), 1)
    sheet.blit(lab.render("FACE 3x — DAY", True, (170, 232, 180)),
               (x, head_h + close_day.get_height() + 4))
    ny = head_h + close_day.get_height() + label_h + pad
    sheet.blit(close_night, (x, ny))
    pygame.draw.rect(sheet, (58, 72, 62),
                     (x, ny, close_night.get_width(), close_night.get_height()), 1)
    sheet.blit(lab.render("FACE 3x — NIGHT (wet-eye glow + dish glint)", True,
                          (170, 232, 180)), (x, ny + close_night.get_height() + 4))

    # blackout thumbnails
    x += col_close + pad
    sheet.blit(lab.render("BLACKOUT (dish tell)", True, (170, 232, 180)),
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
