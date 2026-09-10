"""oni_kanabo — high-fidelity stacked ONI demon-mask totem (candidate).

The BRUTE-RED pole of the Japanese-totem family: a stack of snarling oni
demon masks in hot cinnabar-vermilion, each skull sprouting a pair of THICK,
blunt, backswept iron horns that rake up-and-out into the gutter like a bull's.
Bulging gold-and-black glare eyes, a heavy overhanging brow boss, a flat pug
snout, and a fanged snarl. Crowned by a studded iron kanabō-club drum + wild
indigo hair at the gap rim.

Re-skin of the winning `moai_ancestor` stacked-head COLUMN skeleton: the same
`_draw_tower` driver, `_hw_at` half-width profile, height-adaptive head COUNT,
hidden full-width core fill, neck-waist seams, plinth, and the review harness
(fill gate / gap-rim clearance / blackout / vertical-flip mirror). Only the
relief (`_draw_head`), the materials (basalt → Japanese lacquer/iron/gold/bone/
indigo) and the crown (pukao drum → backswept horns + kanabō cap) are new.

The make-or-break: the blackout must read as a HORNED BRUTE — a full-width
knuckled post topped by two outswept horns — and OWN THE BRIGHTEST, HIGHEST-SAT
RED of the family so a scroll-run never twins it with tengu's dark oxblood or
daruma's glossy lacquer. Everything stays palette-derived so the 5-min biome
day→night retint sweeps straight through.

Standalone review candidate. Imports the REAL pagoda helpers so materials +
lighting match the shipped pillars exactly; wires nothing into the live game.

Run:  python docs/pillar_landmarks/japanese_totems/oni_kanabo/render.py
Out:  docs/pillar_landmarks/japanese_totems/oni_kanabo/round_1.png
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
    _buddha_eye, _vermilion, _lacquer_red, _gold_bright, _bronze, _iron_brown,
)
from game.pillar_variants import draw_grass_bed
from game.draw import draw_side_shrub


MARGIN = 64                       # matches entities.Pipe eave/ornament gutter
CACHE_W = PIPE_W + MARGIN * 2
CACHE_H = GROUND_Y
PHASE_DAY = 0.30                  # midday tan sky — hardest test for "red holds"
PHASE_NIGHT = 0.85               # deep night — checks lit rim + eye glare glow


# ── Materials ────────────────────────────────────────────────────────────────
#
# The family directive: three reds must ride three distinct value/temperature
# bands (Oni bright vermilion / Tengu dark oxblood / Daruma glossy lacquer).
# Oni owns the BRIGHTEST, HIGHEST-SAT end — `_vermilion` (the festival shu-iro)
# pushed a stop hotter toward a fixed cinnabar target. The push is toward a
# fixed RGB (like moai's scoria) but the base is palette-derived, so the biome
# retint still sweeps through; the fixed target only guarantees the red never
# sinks below tengu/daruma in saturation or value on any phase.

def _skin_triad(palette):
    mid = _mix(_vermilion(palette), (222, 62, 40), 0.42)   # hot cinnabar
    lit = _mix(mid, (255, 150, 96), 0.52)                  # raking sunlit cheek
    # Shadow-side skin deepened so the body holds its edge against the closest-
    # luminance day sky (the tan/blue crossover band) without softening the lit red.
    sh = _shade(_mix(mid, (108, 18, 14), 0.60), -12)       # socket-recess shadow
    # Night: cap the lit so the cinnabar doesn't blow out, floor the shadow so
    # the mask doesn't sink into the dark sky as one black mass.
    lit = _cap_lit_for_dark_sky(lit, palette, cap=214)
    sh = _cap_dark_for_dark_sky(sh, palette, floor=48)
    return lit, mid, sh


def _iron_triad(palette):
    # Cold wrought-iron horns + kanabō drum — `_iron_brown` pulled a touch
    # cooler/darker so the horns read as forged metal against the hot skin.
    mid = _shade(_mix(_iron_brown(palette), (78, 66, 58), 0.30), -4)
    lit = _shade(mid, 40)
    sh = _shade(mid, -30)
    lit = _cap_lit_for_dark_sky(lit, palette, cap=180)
    sh = _cap_dark_for_dark_sky(sh, palette, floor=40)
    return lit, mid, sh


def _bone(palette):
    # Fang + tooth ivory — palette stone_light nudged to a warm bone so the
    # snarl's teeth clear the red without going pure white.
    return _mix(palette['stone_light'], (240, 232, 210), 0.62)


def _hair(palette):
    # Wild demon mane + heavy brows — a near-black indigo (deep _shade toward a
    # cold blue-black) so the tufts frame the red face without muddying it.
    return _shade(_mix(palette['stone_dark'], (38, 42, 70), 0.68), -18)


def _eye_gold(palette):
    return _gold_bright(palette)


def _lum(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


# ── Head geometry ──────────────────────────────────────────────────────────
#
# BRUTE by construction. The head is a near-full-width straight column so the
# 58 px collision band stays solid (the silhouette tell is the horns + relief,
# never a lobed bulge). Only a shallow neck WAIST at each seam breaks the
# outline — kept short enough that no outer-column empty run nears the 12 px
# ceiling. Backswept horns + kanabō cap are pure gutter overhang.

_TAPER = 5                        # px of neck-waist ramp at each seam
_WAIST = 5                        # px each side the waist pinches in from the edge
_HEAD_H_FLOOR = 98                # natural head height -> drives adaptive COUNT
_RIM_AIR = 3                      # px sky sliver so flipped caps don't kiss the gap


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
    # Subtle brute flares proud of the band so the blackout body isn't a pure
    # rectangle: a brow-boss bulge and a heavier jaw shelf (adds mass, never
    # empties the band — the fill gate is untouched).
    hh = y1 - y0
    r = (y - y0) / max(1, hh)
    if 0.16 < r < 0.30:
        hw = max(hw, half + 1.5)
    if 0.80 < r < 0.94:
        hw = max(hw, half + 2.0)
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


def _thick_horn(surf, cx, temple_y, top_y, half, side, palette):
    """One THICK, blunt, BACKSWEPT iron horn springing from a temple at
    `temple_y`, raking up-and-OUTWARD into the gutter with a blunt tip near
    `top_y`. Filled iron wedge, lit inner edge / shadow outer edge, gold blunt
    cap + a couple of ridge ribs. `side` = -1 left / +1 right (mirrored)."""
    lit, mid, sh = _iron_triad(palette)
    gold = _eye_gold(palette)
    th = temple_y - top_y
    s = side
    over = half * 1.02                 # tip overhang out into the eave gutter

    # Hand-crafted boundary so the rake is predictable in the blackout: a WIDE
    # blunt base rooted in the head, a thick shaft, and a BROAD blunt tip raked
    # up-and-OUT into the gutter (bull-V), never upright. Base-in sits deep in
    # the head so horn-and-head read as ONE continuous dark form at 1x; the tip
    # is broad (~0.5*half) so it can't shrink to a detached speck.
    base_in = (cx + s * half * 0.34, temple_y)
    base_out = (cx + s * half * 1.02, temple_y)
    mid_out = (cx + s * (half * 1.50), temple_y - th * 0.42)
    tip_out = (cx + s * (half + over), top_y + int(th * 0.05))
    tip_in = (cx + s * (half + over * 0.50), top_y)
    mid_in = (cx + s * half * 0.82, temple_y - th * 0.55)
    poly = [base_in, base_out, mid_out, tip_out, tip_in, mid_in]

    pygame.draw.polygon(surf, mid, poly)
    # Inner edge catches the raking light; outer edge falls into shadow.
    _aa_polyline(surf, _shade(lit, 18), [base_in, mid_in, tip_in])
    _aa_polyline(surf, sh, [base_out, mid_out, tip_out])
    _aa_polyline(surf, _shade(sh, -20), poly, closed=True)
    # Gold blunt tip cap — the horn's lit crown.
    pygame.draw.polygon(surf, gold, [mid_in, tip_in, tip_out, mid_out])
    pygame.draw.polygon(surf, mid, [mid_in, tip_in, tip_out, mid_out], 1)
    _aa_polyline(surf, _shade(gold, 30), [tip_in, tip_out])
    # Two ridge ribs across the shaft (forged-horn banding).
    for k in (0.32, 0.60):
        ax = cx + s * (half * (0.62 + 0.5 * k))
        ay = temple_y - th * (0.15 + 0.55 * k)
        bx = cx + s * (half * (0.90 + 0.5 * k))
        by = ay - th * 0.06
        pygame.draw.line(surf, sh, (int(ax), int(ay)), (int(bx), int(by)), 1)


# ── Demon eye — the _buddha_eye stack retinted to a gold-and-black glare ──────

def _oni_eye(surf, ex, ey, r, palette, *, thumbnail):
    """A bulging gold iris with a black pupil set in a dark socket boss, with a
    heavy indigo brow crescent — the `_buddha_eye` idiom retinted from serene
    almond to a glaring demon eye. A `_lit_niche` behind it makes the eye a
    warm amber point-source at night (the ancestral 'living eye')."""
    lit, mid, sh = _skin_triad(palette)
    gold = _eye_gold(palette)
    hair = _hair(palette)

    if thumbnail:
        # At ~58 px the fangs + brow collapse to noise — the read must survive
        # on TWO dark-ringed gold dots alone (AD's 2-dot fallback).
        pygame.draw.circle(surf, _shade(sh, -22), (ex, ey), r)
        pygame.draw.circle(surf, gold, (ex, ey), max(1, r - 1))
        pygame.draw.circle(surf, (18, 14, 12), (ex, ey), max(1, r - 2))
        return

    # Socket boss — a recessed shadow the bulging eye sits in.
    pygame.draw.circle(surf, _shade(sh, -16), (ex, ey), r + 2)
    # Night glow lantern behind the iris (quiet by day).
    _lit_niche(surf, ex, ey - r // 2, max(3, r), max(4, r), palette)
    # Reuse the buddha-eye stack for the almond base + heavy brow crescent,
    # retinted so its 'white' eyeball comes through as demon gold.
    eye_pal = dict(palette)
    eye_pal['stone_light'] = gold
    eye_pal['stone_dark'] = hair
    _buddha_eye(surf, ex, ey, eye_pal, scale=max(0.7, r / 5.0))
    # Bulging round gold iris over the almond base — the demon glare.
    pygame.draw.circle(surf, gold, (ex, ey), r)
    pygame.draw.circle(surf, _shade(gold, -70), (ex, ey), r, 1)
    # Black pupil (centred so the ceiling flip stays clean).
    pr = max(1, int(r * 0.5))
    pygame.draw.circle(surf, (16, 12, 12), (ex, ey), pr)
    # A single bright catch-light — the wet, furious glint.
    surf.set_at((ex - max(1, r // 3), ey - max(1, r // 3)), _shade(gold, 55))
    # Heavy overhanging indigo brow just above the socket.
    pygame.draw.line(surf, hair, (ex - r - 1, ey - r), (ex + r + 1, ey - r - 1), 2)


# ── One oni mask ──────────────────────────────────────────────────────────

def _draw_head(surf, cx, y0, y1, half, palette, rng, *, crown, base):
    hh = y1 - y0
    lit, mid, sh = _skin_triad(palette)
    hair = _hair(palette)
    bone = _bone(palette)
    gold = _eye_gold(palette)
    dark_sky = _is_dark_sky(palette)

    # Silhouette outline (used for the AA keyline + the night rim-light).
    left_pts = []
    right_pts = []
    for y in range(y0, y1):
        hw = _hw_at(y, y0, y1, half, crown=crown, base=base)
        xl = int(round(cx - hw))
        xr = int(round(cx + hw))
        _grad_hspan(surf, y, xl, xr, lit, mid, sh)
        left_pts.append((xl, y))
        right_pts.append((xr, y))

    thumbnail = hh < 54

    # ── Relief anatomy — a brute snarl, top-heavy brow, wide jaw ──────────
    brow_y = y0 + int(hh * 0.19)
    brow_h = max(3, int(hh * 0.12))
    eye_y = brow_y + brow_h + max(2, int(hh * 0.04))
    eye_r = max(3, int(half * 0.30))
    eye_dx = int(half * 0.46)
    snout_y = eye_y + eye_r + max(2, int(hh * 0.04))
    snout_bot = y0 + int(hh * 0.70)
    mouth_y = y0 + int(hh * 0.78)
    jaw_y = y0 + int(hh * 0.90)

    brow_dark = hair
    ridge_lit = _shade(lit, 30)
    plane_sh = _shade(sh, -22)

    if not thumbnail:
        # 1. Heavy overhanging BROW BOSS — a fat bulging shelf that stands proud
        #    (lit crest) and drops a hard shadow into the eye sockets. Fattened
        #    vs the moai shelf so the brute reads angry + top-heavy.
        bl = cx - int(half * 0.90)
        br = cx + int(half * 0.90)
        brow_poly = [(bl, brow_y + brow_h), (bl + 2, brow_y - 1),
                     (cx - int(half * 0.30), brow_y - 2), (cx, brow_y + 1),
                     (cx + int(half * 0.30), brow_y - 2), (br - 2, brow_y - 1),
                     (br, brow_y + brow_h)]
        pygame.draw.polygon(surf, _shade(mid, -10), brow_poly)
        _aa_polyline(surf, _shade(lit, 20),
                     [(bl + 2, brow_y - 1), (cx - int(half * 0.30), brow_y - 2),
                      (cx, brow_y + 1), (cx + int(half * 0.30), brow_y - 2),
                      (br - 2, brow_y - 1)])
        # Furious knotted brow-ridge (indigo) + a gold brow stud each side.
        pygame.draw.line(surf, brow_dark, (bl + 1, brow_y + brow_h),
                         (cx, brow_y + brow_h - 3), 2)
        pygame.draw.line(surf, brow_dark, (br - 1, brow_y + brow_h),
                         (cx, brow_y + brow_h - 3), 2)
        pygame.draw.rect(surf, gold, (cx - 1, brow_y + 1, 2, 2))
        # Hard cast shadow band beneath the shelf (the socket recess).
        pygame.draw.rect(surf, plane_sh,
                         (bl + 2, brow_y + brow_h, br - bl - 4, 2))

    # 2. Bulging GLARE eyes (or the 2-dot thumbnail fallback).
    _oni_eye(surf, cx - eye_dx, eye_y + eye_r, eye_r, palette, thumbnail=thumbnail)
    _oni_eye(surf, cx + eye_dx, eye_y + eye_r, eye_r, palette, thumbnail=thumbnail)

    if not thumbnail:
        # 3. Flat pug SNOUT — a short wide muzzle plane (lit top / shadow flanks)
        #    with two dark nostril pits flaring at the base.
        sn_hw = int(half * 0.34)
        snout = pygame.Rect(cx - sn_hw, snout_y, sn_hw * 2, snout_bot - snout_y)
        _gradient_rect(surf, snout, _shade(lit, 12), mid, plane_sh)
        _aa_polyline(surf, ridge_lit,
                     [(cx, snout_y), (cx, snout_bot - 1)])
        pygame.draw.line(surf, brow_dark,
                         (cx - sn_hw + 1, snout_bot - 1),
                         (cx - 1, snout_bot - 1), 1)
        pygame.draw.line(surf, brow_dark,
                         (cx + 1, snout_bot - 1),
                         (cx + sn_hw - 1, snout_bot - 1), 1)
        surf.set_at((cx - int(sn_hw * 0.5), snout_bot - 2), (18, 12, 12))
        surf.set_at((cx + int(sn_hw * 0.5), snout_bot - 2), (18, 12, 12))

        # 4. Wide fanged SNARL — a dark mouth recess with corners pulled UP, a
        #    row of bone teeth along the top and two prominent up-thrust FANGS.
        m_hw = int(half * 0.56)
        m_h = max(3, int(hh * 0.07))
        mouth = [(cx - m_hw, mouth_y - 1), (cx, mouth_y + 1),
                 (cx + m_hw, mouth_y - 1), (cx + m_hw - 1, mouth_y + m_h),
                 (cx, mouth_y + m_h + 1), (cx - m_hw + 1, mouth_y + m_h)]
        pygame.draw.polygon(surf, _shade(hair, -8), mouth)
        # Bone tooth row along the upper lip.
        tx = cx - m_hw + 2
        while tx < cx + m_hw - 2:
            pygame.draw.rect(surf, bone, (tx, mouth_y, 1, 2))
            tx += 3
        # Two up-thrust fangs at the snarl corners (bone triangles).
        for s in (-1, 1):
            fx = cx + s * int(m_hw * 0.74)
            pygame.draw.polygon(surf, bone,
                                [(fx - 2, mouth_y + m_h), (fx + 2, mouth_y + m_h),
                                 (fx, mouth_y - 2)])
            pygame.draw.line(surf, _shade(bone, -40),
                             (fx + s, mouth_y + m_h), (fx, mouth_y - 2), 1)

        # 5. Brute JAW undercut — a heavy shadow bar reading the wide chin.
        pygame.draw.rect(surf, plane_sh,
                         (cx - int(half * 0.6), jaw_y, int(half * 1.2), 2))

        # 6. Sidelock mane tufts framing the temples (indigo), + a couple of
        #    stray cinnabar-skin creases (kept off the eyes so relief stays clean).
        for s in (-1, 1):
            tuft_x = cx + s * int(half * 0.86)
            for k in range(3):
                ty0 = eye_y - eye_r + k * max(2, hh // 12)
                pygame.draw.line(surf, hair, (tuft_x, ty0),
                                 (tuft_x + s * 3, ty0 + max(3, hh // 14)), 1)
        for _ in range(max(3, hh // 12)):
            px = rng.randint(cx - half + 3, cx + half - 3)
            py = rng.randint(snout_y, y1 - 3)
            surf.set_at((px, py), _shade(sh, -14) if rng.random() < 0.6
                        else _shade(lit, 12))
    else:
        # Thumbnail relief: brute reads on brow-bar + 2 gold eye-dots + a single
        # dark mouth-notch alone at ~50 px face height.
        bl = cx - int(half * 0.80)
        br = cx + int(half * 0.80)
        pygame.draw.line(surf, brow_dark, (bl, brow_y + 1), (br, brow_y + 1), 2)
        pygame.draw.line(surf, _shade(hair, -8),
                         (cx - int(half * 0.5), mouth_y),
                         (cx + int(half * 0.5), mouth_y), 2)

    # 7. AA silhouette keyline. By day the body red sits close in luminance to
    #    the tan/blue crossover sky, so thicken the shadow (right) edge to a 2px
    #    dark keyline that anchors the outline; night keeps a crisp 1px line so
    #    the rim-light can carry the left edge instead.
    outline = left_pts + list(reversed(right_pts))
    _aa_polyline(surf, _shade(sh, -20), outline, closed=True)
    if not dark_sky:
        key = _shade(sh, -26)
        for x, y in right_pts:
            if 0 <= x - 1 < surf.get_width():
                surf.set_at((x - 1, y), key)

    # 8. Night rim-light down the LEFT edge so the hot red holds its silhouette
    #    against a dark sky (a quiet warm edge by day).
    rim = _shade(lit, 44) if dark_sky else _shade(lit, 16)
    step = 1 if dark_sky else 2
    for i in range(0, len(left_pts), step):
        x, y = left_pts[i]
        surf.set_at((x, y), rim)
        if dark_sky and x + 1 < cx:
            surf.set_at((x + 1, y), _mix(rim, mid, 0.5))


# ── Topper: backswept horns + studded kanabō cap at the gap rim ──────────────

def _draw_topper(surf, cx, y_top, y_bot, half, palette):
    """Replaces the moai pukao. Two THICK backswept iron horns spring from the
    crown mask's temples out into the gutter; a studded kanabō-club drum with a
    gold band + wild indigo hair-knot presents the solid WIDE flat edge at the
    gap rim. Near-symmetric about the vertical axis so the ceiling flip is clean
    (horns just point the other way, still oni-legible)."""
    lit, mid, sh = _iron_triad(palette)
    gold = _eye_gold(palette)
    hair = _hair(palette)
    # Pull the whole cap down a hair so the two flipped drums leave a clean sky
    # sliver across the flyable gap instead of kissing into one blob.
    y_cap = y_top + _RIM_AIR
    dh = y_bot - y_cap

    # Wild indigo hair-mass under the drum (frames the kanabō, sits on the crown).
    hair_hw = int(half * 0.95)
    for k in range(4):
        t = k / 3.0
        pygame.draw.line(surf, _mix(hair, _shade(hair, 18), t),
                         (cx - hair_hw, y_bot - 1 - k),
                         (cx + hair_hw, y_bot - 1 - k), 1)

    # Studded kanabō drum — narrowed (~1.08x) so the bold horns overhang it as
    # clear wings, not nubs swallowed by an oversized club.
    dw = int(half * 2 * 1.08)
    x0 = cx - dw // 2
    drum = pygame.Rect(x0, y_cap + 3, dw, max(6, dh - 3))
    _gradient_rect(surf, drum, lit, mid, sh)
    # Domed, wide solid top edge = the gap-rim presentation.
    top_rect = pygame.Rect(x0, y_cap, dw, 6)
    pygame.draw.ellipse(surf, mid, top_rect)
    pygame.draw.ellipse(surf, lit, top_rect.inflate(-2, -2))
    # Gold band around the club.
    band_y = y_cap + max(4, dh // 2)
    pygame.draw.rect(surf, gold, (x0 + 1, band_y, dw - 2, 2))
    pygame.draw.line(surf, _shade(gold, -40), (x0 + 1, band_y + 2),
                     (x0 + dw - 2, band_y + 2), 1)
    # Iron studs (the kanabō spikes) — kept INSIDE the rim so the top silhouette
    # stays a clean solid drum, never a frayed row of bumps.
    rng = random.Random(cx * 5 + y_top)
    for _ in range(max(4, dw // 5)):
        px = rng.randint(x0 + 3, x0 + dw - 4)
        py = rng.randint(y_cap + 5, drum.bottom - 2)
        pygame.draw.circle(surf, _shade(lit, 20), (px, py), 1)
        surf.set_at((px, py - 1), _shade(sh, -10))
    _aa_polyline(surf, _shade(sh, -18),
                 [(x0, drum.bottom), (x0, y_cap + 4),
                  (x0 + dw - 1, y_cap + 4), (x0 + dw - 1, drum.bottom)])

    # Horns LAST, rooted BELOW the drum into the crown head, so each horn+head
    # is one continuous dark wedge and the full bold shaft shows over the club.
    root = min(int(half * 0.42), max(6, dh))
    _thick_horn(surf, cx, y_bot + root, y_cap, half, -1, palette)
    _thick_horn(surf, cx, y_bot + root, y_cap, half, +1, palette)


# ── 3-layer plinth + foliage ────────────────────────────────────────────────

def _draw_plinth(surf, cx, base_y, half, palette, seed):
    # Iron-and-stone plinth so the red mask stack lands on a forged base.
    lit, mid, sh = _iron_triad(palette)
    layers = 3
    for i in range(layers):
        lw = int(half * 2 * (1.12 + 0.16 * i))
        lh = 5
        ly = base_y - (layers - i) * lh
        r = pygame.Rect(cx - lw // 2, ly, lw, lh)
        _gradient_rect(surf, r, lit, mid, sh)
        pygame.draw.line(surf, _shade(sh, -18),
                         (r.x, r.bottom - 1), (r.right - 1, r.bottom - 1), 1)
        pygame.draw.line(surf, _shade(lit, 16), (r.x, r.y), (r.right - 1, r.y), 1)


def _draw_tower(surf, cx, y_top, y_bot, palette, seed):
    """One upright oni tower: mist -> plinth -> foliage -> adaptive mask stack
    -> horns + kanabō cap at the gap rim. Height-adaptive head COUNT keeps every
    mask un-squashed (1 big oni at ~70 px, several at 355)."""
    rng = random.Random(seed)
    half = PIPE_W // 2
    section_h = y_bot - y_top

    plinth_h = min(15, max(9, int(section_h * 0.14)))
    topper_h = min(20, max(11, int(section_h * 0.17)))
    if section_h < 100:
        plinth_h = max(7, plinth_h - 2)
        topper_h = max(10, topper_h - 2)
    base_y = y_bot

    _draw_plinth_mist(surf, cx, base_y - plinth_h + 2, int(half * 2 * 1.6), palette)

    stack_bot = base_y - plinth_h
    stack_top = y_top + topper_h
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

    # Horns + kanabō cap crown the top mask and reach the gap rim.
    _draw_topper(surf, cx, y_top, stack_top, half, palette)

    _draw_plinth(surf, cx, base_y, half, palette, seed)
    draw_grass_bed(surf, cx, base_y - 1, PIPE_W + 12, 12, palette, seed=seed)
    draw_side_shrub(surf, cx - half - 6, base_y - 1, palette, scale=0.9)
    draw_side_shrub(surf, cx + half + 6, base_y - 1, palette, scale=0.8)


def candidate_oni_kanabo(surf, top_rect, bot_rect, palette, seed):
    """Bottom = oni tower rising from the ground, horns + kanabō cap at the gap.
    Top = the same tower vertical-FLIPPED from the ceiling — a symmetric two-
    ended totem, its horns pointing into the gap so both caps meet at the rim."""
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
    for x in range(x0, x1):
        run = 0
        for y in range(y0, y1):
            if surf.get_at((x, y))[3] == 0:
                run += 1
                worst = max(worst, run)
            else:
                run = 0
    return worst


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
    gap_y, gap_h = 168, 150
    top_h = int(gap_y - gap_h / 2)
    bot_top = int(gap_y + gap_h / 2)
    full = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    top_rect = pygame.Rect(MARGIN, 0, PIPE_W, top_h)
    bot_rect = pygame.Rect(MARGIN, bot_top, PIPE_W, GROUND_Y - bot_top)
    candidate_oni_kanabo(full, top_rect, bot_rect, pal, seed=seed)

    tip_y = top_h - 6
    base_y = GROUND_Y + 8
    hero_h = base_y - tip_y
    hero = _bg(CACHE_W, hero_h, pal, hero_h - (base_y - GROUND_Y))
    hero.blit(full, (0, -tip_y))
    for ex in (MARGIN, MARGIN + PIPE_W):
        pygame.draw.line(hero, (230, 60, 60), (ex, 0), (ex, hero_h), 1)
    return hero, hero_h


def _closeup(pal, seed, scale=3):
    """Zoom on a single ground oni mask so the carved relief is checkable."""
    surf = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    br = pygame.Rect(MARGIN, GROUND_Y - 150, PIPE_W, 150)
    tr = pygame.Rect(MARGIN, 0, PIPE_W, 0)
    candidate_oni_kanabo(surf, tr, br, pal, seed=seed)
    crop = pygame.Surface((CACHE_W, 128))
    crop.blit(_bg(CACHE_W, 128, pal, 128), (0, 0))
    crop.blit(surf, (0, -(GROUND_Y - 150)))
    return pygame.transform.scale(
        crop, (crop.get_width() * scale, crop.get_height() * scale))


def _blackout(pal, section_h, scale):
    """Solid-black silhouette of a hero section — the horned-brute read test."""
    surf = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    br = pygame.Rect(MARGIN, GROUND_Y - section_h, PIPE_W, section_h)
    tr = pygame.Rect(MARGIN, 0, PIPE_W, 0)
    candidate_oni_kanabo(surf, tr, br, pal, seed=7)
    # Wide crop so the backswept horn overhang shows, not just the 58 px post.
    pad_x = 36
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


def _head_count(section_h):
    half = PIPE_W // 2
    plinth_h = min(15, max(9, int(section_h * 0.14)))
    topper_h = min(20, max(11, int(section_h * 0.17)))
    if section_h < 100:
        plinth_h = max(7, plinth_h - 2)
        topper_h = max(10, topper_h - 2)
    avail = max(24, (section_h - plinth_h) - topper_h)
    return max(1, round(avail / _HEAD_H_FLOOR))


def _horn_metrics(pal, section_h):
    """Quantify the blackout horn read: how far the horns reach past the 58px
    band, how much dark 'wing' mass sits in the gutter, and the horn shaft's
    vertical thickness just outside the drum edge."""
    surf = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    br = pygame.Rect(MARGIN, GROUND_Y - section_h, PIPE_W, section_h)
    tr = pygame.Rect(MARGIN, 0, PIPE_W, 0)
    candidate_oni_kanabo(surf, tr, br, pal, seed=7)
    cx = MARGIN + PIPE_W // 2
    band = PIPE_W // 2
    top = GROUND_Y - section_h
    max_reach = wing_px = 0
    for y in range(top, top + 34):
        for x in range(CACHE_W):
            if surf.get_at((x, y))[3] > 40 and abs(x - cx) > band:
                wing_px += 1
                max_reach = max(max_reach, abs(x - cx))

    def col_thick(xc):
        run = best = 0
        for y in range(top, top + 44):
            if 0 <= xc < CACHE_W and surf.get_at((xc, y))[3] > 40:
                run += 1
                best = max(best, run)
            else:
                run = 0
        return best

    shaft = max(col_thick(cx + 36), col_thick(cx - 36))
    return max_reach - band, wing_px, shaft


def main():
    pal = biome.palette_for_phase(PHASE_DAY)
    pal_n = biome.palette_for_phase(PHASE_NIGHT)

    # Skin-hue proof: must read as the BRIGHTEST, most-saturated red + DAY != NIGHT.
    _, mid_d, _ = _skin_triad(pal)
    _, mid_n, _ = _skin_triad(pal_n)
    lac_d = _lacquer_red(pal)     # tengu's darker oxblood — the twin to beat
    print("ONI SKIN (mid tone) — owns the family's BRIGHTEST/HIGHEST-SAT red")
    print(f"  DAY   mid={mid_d} lum={_lum(mid_d):.1f}  R-G={mid_d[0]-mid_d[1]}  "
          f"R-B={mid_d[0]-mid_d[2]}")
    print(f"  NIGHT mid={mid_n} lum={_lum(mid_n):.1f}  R-G={mid_n[0]-mid_n[1]}")
    print(f"  vs tengu _lacquer_red DAY={lac_d} lum={_lum(lac_d):.1f}  "
          f"-> oni brighter: {_lum(mid_d) > _lum(lac_d)}  "
          f"higher R-G: {mid_d[0]-mid_d[1] > lac_d[0]-lac_d[1]}")
    print(f"  day != night: {mid_d != mid_n}")

    print("HEAD COUNT (adaptive) — 1 big oni short, several tall")
    for h in (70, 210, 355):
        print(f"  h={h:3d}  heads={_head_count(h)}")

    reach, wing, shaft = _horn_metrics(pal, 118)
    print("HORN BOLDNESS (blackout, hero section)")
    print(f"  reach past band = {reach}px   wing mass = {wing}px   "
          f"shaft thickness @±36 = {shaft}px")

    hero_day, hd_h = _hero(pal, 7)
    hero_night, hn_h = _hero(pal_n, 7)
    close = _closeup(pal, 7)

    # Gap-rim clearance (bottom tower cap reaching the gap line + top flipped cap).
    gap_probe = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    gp_bot = pygame.Rect(MARGIN, 243, PIPE_W, GROUND_Y - 243)
    gp_top = pygame.Rect(MARGIN, 0, PIPE_W, 93)
    candidate_oni_kanabo(gap_probe, gp_top, gp_bot, pal, seed=7)
    # The bottom cap now sits BELOW its rim line, so probe DOWN into the gap for
    # the sky sliver; the top (flipped) cap hangs above its rim, so probe UP.
    clear_bot = _gap_rim_clearance(gap_probe, MARGIN, MARGIN + PIPE_W, 243, up=False)
    clear_top = _gap_rim_clearance(gap_probe, MARGIN, MARGIN + PIPE_W, 93, up=True)
    print("GAP-RIM CLEARANCE (sky sliver between cap and its gap-rim line)")
    print(f"  bottom cap air: {clear_bot}px   top (flipped) cap air: {clear_top}px")

    # Feasibility strip: bottom section at three heights + empty-run gate.
    strip_heights = [70, 210, 355]
    strips = []
    print("FILL GATE (max empty vertical run inside the 58px PIPE_W band)")
    for h in strip_heights:
        s = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
        br = pygame.Rect(MARGIN, GROUND_Y - h, PIPE_W, h)
        tr = pygame.Rect(MARGIN, 0, PIPE_W, 0)
        candidate_oni_kanabo(s, tr, br, pal, seed=7)
        run = _max_empty_run(s, MARGIN, MARGIN + PIPE_W, GROUND_Y - h, GROUND_Y)
        crop = pygame.Surface((CACHE_W, h + 8))
        crop.blit(_bg(CACHE_W, h + 8, pal, h), (0, 0))
        crop.blit(s, (0, -(GROUND_Y - h)))
        for ex in (MARGIN, MARGIN + PIPE_W):
            pygame.draw.line(crop, (230, 60, 60), (ex, 0), (ex, h + 8), 1)
        strips.append((h, crop, run))
        print(f"  h={h:3d}  max empty run = {run}px  [{'OK' if run <= 12 else 'FAIL'}]")

    # Blackout thumbnails: horned-brute read at native 58px, shown 1x + 3x.
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
    col_close = close.get_width()
    col_bo = max(bo3.get_width(), bo1.get_width()) + 20
    strips_total_h = sum(c.get_height() + label_h + pad for _, c, _ in strips)

    body_h = max(hd_h, hn_h, close.get_height(),
                 strips_total_h, bo3.get_height() + 40) + label_h
    sheet_w = pad + col_hero + pad + col_hero + pad + col_hero + pad + \
        col_close + pad + col_bo + pad
    sheet_h = head_h + body_h + pad * 2
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((24, 22, 26))

    sheet.blit(title.render(
        "oni_kanabo — stacked horned ONI demon-mask totem  ·  round_2",
        True, (250, 236, 226)), (pad, 12))
    sheet.blit(sub.render(
        "red edges = PIPE_W (58px) collision band  ·  BRIGHT cinnabar-vermilion "
        "skin  ·  brow-boss + gold-glare eyes + fanged snarl  ·  THICK backswept "
        "iron horns + kanabo cap  ·  symmetric ceiling flip", True,
        (172, 170, 180)), (pad, 40))
    sheet.blit(sub.render(
        f"BRUTE-RED pole: oni lum {_lum(mid_d):.0f} > tengu oxblood {_lum(lac_d):.0f}  "
        "·  horns = pure gutter overhang, full-width jaw holds the band  ·  "
        "2-dot eye + mouth-notch fallback at 58px", True,
        (240, 170, 150)), (pad, 56))

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
    for h, crop, run in strips:
        sheet.blit(crop, (x, sy))
        pygame.draw.rect(sheet, (60, 56, 62), (x, sy, col_hero, crop.get_height()), 1)
        ok = "OK" if run <= 12 else "FAIL"
        sheet.blit(lab.render(f"h={h}px  ·  run {run}px  [{ok}]", True,
                              (200, 235, 170) if run <= 12 else (255, 140, 140)),
                   (x, sy + crop.get_height() + 4))
        sy += crop.get_height() + label_h + pad

    x += col_hero + pad
    sheet.blit(close, (x, head_h))
    pygame.draw.rect(sheet, (60, 56, 62),
                     (x, head_h, close.get_width(), close.get_height()), 1)
    sheet.blit(lab.render("FACE CLOSE-UP 3x — carved relief", True,
                          (255, 224, 150)), (x, head_h + close.get_height() + 4))

    x += col_close + pad
    sheet.blit(lab.render("BLACKOUT (horned-brute test)", True, (255, 224, 150)),
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
