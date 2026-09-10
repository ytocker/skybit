"""tengu_yamabushi — high-fidelity long-nosed mountain-goblin totem (candidate).

A stacked totem of yamabushi Tengu masks: dark OXBLOOD-lacquer faces, each
skewered by one enormous long forward NOSE-SPUR jutting into the gutter, bushy
white ascetic brows + moustache, fierce gold-rimmed glare eyes, crowned by the
small black tokin pillbox cap with a gold pom.

Seeded on the winning `moai_ancestor` skeleton. The reusable stacked-head COLUMN
driver is kept verbatim (`_hw_at` full-width profile + shallow neck waist so the
58 px collision band never lobes, `_draw_tower`'s height-adaptive head COUNT, the
core gradient fill, neck seams, plinth + foliage, the vertical-flip mirror). Only
the RELIEF (`_draw_head`), the CROWN (tokin cap in place of the pukao) and the
MATERIALS are re-skinned into Tengu.

The make-or-break is the blackout: the long NOSE is a horizontal gutter-overhang
spur — the ONE contour break a vertical flip preserves (it does not mirror
left/right) and the ONE tell that never touches the 58 px band, so the fill gate
stays as clean as moai while the silhouette screams "long-nose". Kept ABOVE the
neck-waist seam so it never pinches the collision column. The face is pushed to a
DARK cool oxblood, distinctly lower-value than the oni's bright vermilion, so the
two red poles never twin on hue.

Standalone review candidate — imports the REAL pagoda helpers so materials +
lighting match the shipped pillars, but wires nothing into the live game.

Run:  python docs/pillar_landmarks/japanese_totems/tengu_yamabushi/render.py
Out:  docs/pillar_landmarks/japanese_totems/tengu_yamabushi/round_2.png
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

# Real pagoda helpers — identical materials + lighting language to the shipped
# pillars, so the 5-min biome day->night retint sweeps straight through.
from game.pillar_pagodas import (
    _mix, _shade, _gradient_rect, _aa_polyline, _lit_niche, _tile_hatch,
    _draw_plinth_mist, _is_dark_sky, _is_warming_sky,
    _cap_lit_for_dark_sky, _cap_dark_for_dark_sky,
    _buddha_eye, _vermilion, _lacquer_red, _gold_bright, _bronze,
    _lapis, _iron_brown,
)
from game.pillar_variants import draw_grass_bed
from game.draw import draw_side_shrub


MARGIN = 64                       # matches entities.Pipe eave/ornament gutter
CACHE_W = PIPE_W + MARGIN * 2
CACHE_H = GROUND_Y
PHASE_DAY = 0.30                  # midday tan sky — hardest test for "reads dark"
PHASE_NIGHT = 0.85               # deep night — checks lit rim + socket glow + cap


# ── Materials ────────────────────────────────────────────────────────────────
#
# Tengu face = DARK OXBLOOD lacquer. Anchored a full stop deeper + cooler than
# the shipped `_vermilion`/`_lacquer_red` so this pole reads a low-value cool
# crimson — the primary guard against twinning the bright-vermilion oni. Still
# fully palette-derived (stone_dark/light anchors), so the biome retint carries.

def _oxblood(palette):
    # Deep cool crimson tengu lacquer — the darkest of the family's three reds.
    return _mix(palette['stone_dark'], (118, 30, 34), 0.82)


def _face_triad(palette):
    mid = _oxblood(palette)
    # Lit face keeps its RED identity (mix toward a lit crimson, not toward the
    # orange vermilion highlight) so the raking highlight never drifts to oni.
    # Pulled a stop DARKER + WARMER than the first pass: the old lit plane
    # (lum ~119) twinned the blue day sky (~116) and dissolved into it, leaving
    # only the keyline to save the silhouette. At ~99 the raking plane now reads
    # as crimson face, sitting clearly UNDER the sky luminance.
    lit = _mix(palette['stone_light'], (150, 54, 50), 0.86)
    sh = _mix(palette['stone_dark'], (64, 16, 22), 0.86)
    if _is_dark_sky(palette):
        # Night: the UNLIT mid mass sat only ~17 lum off the deep night sky and
        # merged with it in motion at true 1x. Lift the mid toward a warmer
        # oxblood so the face MASS clears the sky by ~30 lum — the left rim +
        # gold no longer have to carry the whole silhouette alone.
        mid = _mix(mid, (156, 72, 76), 0.34)
    # Night: cap the highlight so the lacquer sheen doesn't blow out and floor
    # the shadow so the dark face doesn't sink into a black mass with the sky.
    lit = _cap_lit_for_dark_sky(lit, palette, cap=168)
    sh = _cap_dark_for_dark_sky(sh, palette, floor=40)
    return lit, mid, sh


def _nose_ridge(palette):
    # Bright crimson catch-light along the top spine of the nose spur — the
    # feature that separates the honker from the face plane. Still unambiguously
    # red (never the vermilion orange) so the hue-guard holds.
    lit = _mix(palette['stone_light'], (206, 96, 78), 0.82)
    return _cap_lit_for_dark_sky(lit, palette, cap=190)


def _bristle_lit(palette):
    # Bushy white ascetic brow + moustache — the value-break against the dark
    # oxblood, biased to stone_light so nights cool it and dawns warm it.
    return _mix(palette['stone_light'], (232, 226, 214), 0.66)


def _bristle_sh(palette):
    return _mix(palette['stone_mid'], (150, 144, 138), 0.60)


def _indigo_cap(palette):
    # Deep-indigo/near-black tokin pillbox — the little yamabushi forehead cap.
    return _shade(_lapis(palette), -18)


def _lum(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


# ── Head geometry ──────────────────────────────────────────────────────────
#
# Column skeleton kept VERBATIM from moai: tall near-full-width straight heads
# so the 58 px band is always solid (smooth vertical, never lobed), with only a
# shallow neck WAIST at each stacked seam. Gauntness/identity is carried by the
# relief + the crown, not a fat taper. The Tengu long-nose lives entirely in the
# gutter overhang, so it never touches this profile or the fill gate.

_TAPER = 5                        # px of neck-waist ramp at each seam
_WAIST = 5                        # px each side the waist pinches in from the edge
_HEAD_H_FLOOR = 92                # natural head height -> drives adaptive COUNT
_NOSE_REACH = 27                  # px the nose spur juts past the right band edge


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


# ── The long nose spur ─────────────────────────────────────────────────────

def _draw_nose(surf, cx, y0, hh, half, palette, *, thumbnail):
    """The hero feature: one long tapering NOSE-SPUR springing from the face
    centre and jutting FORWARD (right) past the band edge into the gutter, tip
    drooping slightly down (the phallic Konoha-tengu honker). Lit top ridge,
    shadowed underside, oxblood body. Horizontal gutter overhang only — it never
    enters the 58 px band and it sits well ABOVE the neck-waist seam."""
    lit, mid, sh = _face_triad(palette)
    root_x = cx - 3
    root_top = y0 + int(hh * 0.36)
    root_bot = y0 + int(hh * 0.58)
    reach = _NOSE_REACH if not thumbnail else int(_NOSE_REACH * 0.72)
    tip_x = cx + half + reach
    tip_y = y0 + int(hh * 0.52)               # droops just below the root centre

    # Solid wedge: bright-lit top edge, mid body, shadow underside.
    top_poly = [(root_x, root_top), (tip_x, tip_y),
                (tip_x - 3, tip_y + 3), (root_x, root_bot)]
    pygame.draw.polygon(surf, mid, top_poly)
    # Underside shadow band along the lower edge (root_bot -> tip).
    _aa_polyline(surf, _shade(sh, -14),
                 [(root_x + 2, root_bot), (tip_x - 2, tip_y + 2)])
    # Lit dorsal ridge along the top edge — the catch-light that lifts the honker
    # off the face plane.
    _aa_polyline(surf, _nose_ridge(palette),
                 [(root_x + 1, root_top + 1), (tip_x - 1, tip_y)])
    if not thumbnail:
        # Rounded fleshy tip.
        pygame.draw.circle(surf, mid, (tip_x - 2, tip_y + 1), 3)
        pygame.draw.circle(surf, _nose_ridge(palette), (tip_x - 3, tip_y), 1)
        # Nostril flare shadow at the wide root.
        pygame.draw.line(surf, _shade(sh, -22),
                         (root_x + 1, root_bot - 1), (root_x + 7, root_bot - 2), 2)
        # A bridge crease up to the brow so the nose reads as rooted in the face.
        _aa_polyline(surf, _shade(sh, -10),
                     [(root_x, root_top), (cx - 1, y0 + int(hh * 0.26))])


# ── One Tengu head ─────────────────────────────────────────────────────────

def _draw_head(surf, cx, y0, y1, half, palette, rng, *, crown, base):
    hh = y1 - y0
    lit, mid, sh = _face_triad(palette)
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

    thumbnail = hh < 50

    # Relief anchors — eyes high + tight, nose rooted below them, moustache +
    # frown beneath, so the face reads ELONGATED and the honker springs clear.
    brow_y = y0 + int(hh * 0.15)
    brow_h = max(3, int(hh * 0.09))
    eye_y = y0 + int(hh * 0.26)
    eye_h = max(4, int(hh * 0.12))
    eye_dx = int(half * 0.44)
    eye_w = max(4, int(half * 0.30))
    stache_y = y0 + int(hh * 0.62)
    mouth_y = y0 + int(hh * 0.72)
    chin_y = y0 + int(hh * 0.88)

    brow_dark = _shade(sh, -20)
    bristle = _bristle_lit(palette)
    bristle_sh = _bristle_sh(palette)
    gold = _gold_bright(palette)

    # 1. Bushy WHITE ascetic brows — two thick tufted sweeps that spill sideways
    #    a few px past the face edge (small blackout bumps), meeting in a scowl
    #    knot over the bridge. The value-break against the oxblood.
    if not thumbnail:
        for sgn in (-1, 1):
            ex = cx + sgn * eye_dx
            inner = cx + sgn * int(half * 0.10)
            outer = cx + sgn * int(half * 1.06)
            pts = [(inner, brow_y + brow_h + 1),
                   (cx + sgn * int(half * 0.5), brow_y - 1),
                   (outer, brow_y + 1),
                   (outer, brow_y + brow_h + 2),
                   (ex, brow_y + brow_h + 3)]
            pygame.draw.polygon(surf, bristle_sh, pts)
            _aa_polyline(surf, bristle,
                         [(inner, brow_y + brow_h), (cx + sgn * int(half * 0.5),
                          brow_y), (outer, brow_y + 1)])
            # A couple of hair striations for the tufted read.
            for k in range(3):
                hx = cx + sgn * int(half * (0.35 + 0.22 * k))
                surf.set_at((hx, brow_y + 1), bristle)
                surf.set_at((hx, brow_y + 3), bristle_sh)
        # Angry knot shadow between the brows, over the bridge.
        pygame.draw.line(surf, brow_dark,
                         (cx, brow_y + 1), (cx, eye_y - 1), 2)
        # Gold brow-jewel at the scowl centre.
        pygame.draw.circle(surf, _shade(gold, -30), (cx, brow_y - 1), 2)
        pygame.draw.circle(surf, gold, (cx - 1, brow_y - 2), 1)
    else:
        pygame.draw.line(surf, bristle_sh,
                         (cx - int(half * 0.9), brow_y + 1),
                         (cx + int(half * 0.9), brow_y + 1), 3)
        _aa_polyline(surf, bristle,
                     [(cx - int(half * 0.8), brow_y),
                      (cx + int(half * 0.8), brow_y)])

    # 2. Fierce gold-rimmed glare eyes — a _lit_niche socket (free night-lantern
    #    glow) ringed in gold with a hard dark pupil. 2-dot fallback at thumbnail.
    for sgn in (-1, 1):
        ex = cx + sgn * eye_dx
        _lit_niche(surf, ex, eye_y, eye_w, eye_h, palette)
        if not thumbnail:
            r = pygame.Rect(ex - eye_w // 2 - 1, eye_y - 1, eye_w + 2, eye_h + 2)
            pygame.draw.ellipse(surf, gold, r, 1)
            # Angry pupil pushed toward the bridge (the inward glare).
            pupil = (ex - sgn, eye_y + eye_h // 2)
            pygame.draw.circle(surf, brow_dark, pupil, 2)
            surf.set_at((pupil[0] - 1, pupil[1] - 1), _shade(gold, 20))
        else:
            pygame.draw.circle(surf, gold, (ex, eye_y + eye_h // 2), 2)
            surf.set_at((ex, eye_y + eye_h // 2), brow_dark)

    # 3. The long forward nose spur — drawn over the face, under the moustache.
    _draw_nose(surf, cx, y0, hh, half, palette, thumbnail=thumbnail)

    if not thumbnail:
        # 4. Bushy WHITE moustache — a broad drooping sweep under the nose root,
        #    spilling a touch past the cheeks; the second value-break.
        m_hw = int(half * 0.86)
        mpts = [(cx - m_hw, stache_y), (cx - int(half * 0.2), stache_y - 2),
                (cx + int(half * 0.2), stache_y - 2), (cx + m_hw, stache_y),
                (cx + int(half * 0.66), stache_y + 5),
                (cx, stache_y + 3),
                (cx - int(half * 0.66), stache_y + 5)]
        pygame.draw.polygon(surf, bristle_sh, mpts)
        _aa_polyline(surf, bristle,
                     [(cx - m_hw, stache_y), (cx, stache_y - 2),
                      (cx + m_hw, stache_y)])
        for k in range(-2, 3):
            hx = cx + int(half * 0.28 * k)
            pygame.draw.line(surf, bristle,
                             (hx, stache_y + 1),
                             (hx + 2, stache_y + 4), 1)
        # One brighter value-break along the moustache crest so the white
        # tuft doesn't flatten into a single grey mass against the oxblood.
        _aa_polyline(surf, _shade(bristle, 22),
                     [(cx - int(half * 0.5), stache_y - 1), (cx, stache_y - 2),
                      (cx + int(half * 0.5), stache_y - 1)])

        # 5. Down-set frown mouth beneath the moustache.
        pygame.draw.line(surf, brow_dark,
                         (cx - int(half * 0.42), mouth_y),
                         (cx, mouth_y + 2), 2)
        pygame.draw.line(surf, brow_dark,
                         (cx, mouth_y + 2),
                         (cx + int(half * 0.42), mouth_y), 2)
        pygame.draw.line(surf, _shade(lit, 12),
                         (cx - int(half * 0.4), mouth_y - 1),
                         (cx + int(half * 0.4), mouth_y - 1), 1)

        # 6. Jaw undercut shadow (the heavy set jaw).
        pygame.draw.rect(surf, _shade(sh, -16),
                         (cx - int(half * 0.5), chin_y, int(half), 2))

        # 7. Sparse lacquer sheen stipple, kept off the sockets.
        for _ in range(max(3, hh // 9)):
            px = rng.randint(cx - half + 3, cx + half - 3)
            py = rng.randint(y0 + 2, y1 - 3)
            if abs(py - eye_y) < eye_h and abs(abs(px - cx) - eye_dx) < eye_w:
                continue
            c = _shade(lit, 16) if rng.random() < 0.5 else _shade(sh, -12)
            surf.set_at((px, py), c)

    # 8. AA silhouette keyline.
    outline = left_pts + list(reversed(right_pts))
    _aa_polyline(surf, _shade(sh, -22), outline, closed=True)

    # 9. Night rim-light down the LEFT edge so the dark oxblood holds its
    #    silhouette against a dark sky (a quiet cool edge by day).
    rim = _shade(lit, 46) if dark_sky else _shade(lit, 18)
    step = 1 if dark_sky else 2
    for i in range(0, len(left_pts), step):
        x, y = left_pts[i]
        surf.set_at((x, y), rim)
        if dark_sky and x + 1 < cx:
            surf.set_at((x + 1, y), _mix(rim, mid, 0.5))
    if dark_sky:
        # Backlight the SHADOW (right) edge too so BOTH silhouette sides hold
        # against a dark sky, not just the lit-left rim. A quiet cool edge —
        # pagoda restraint, not a glow — so the mass read stays honest.
        rrim = _mix(_shade(sh, 42), rim, 0.5)
        for x, y in right_pts:
            surf.set_at((x, y), rrim)


# ── Tokin cap (small black yamabushi pillbox + gold pom) ────────────────────

def _draw_tokin(surf, cx, y_top, y_bot, half, palette):
    """The little black tokin pillbox crowning the stack — a low indigo/near-
    black hexagonal drum with a gold cord tie and a bright gold pom. Deliberately
    SMALL (~1.05x the crown) so the blackout reads 'post + tiny cap + side nose
    spur' — the anti-moai (whose crown is a big wide pukao). Presents a solid
    wide flat edge at the gap rim; near vertically symmetric for a clean flip."""
    cap = _indigo_cap(palette)
    cap_lit = _shade(cap, 30)
    cap_dark = _shade(cap, -16)
    gold = _gold_bright(palette)
    dark_sky = _is_dark_sky(palette)

    cw = int(half * 2 * 1.05)
    x0 = cx - cw // 2
    body_top = y_top + 4
    # Cylindrical drum body — left-lit horizontal gradient.
    r = pygame.Rect(x0, body_top, cw, y_bot - body_top)
    _gradient_rect(surf, r, cap_lit, cap, cap_dark)
    # Solid slightly-domed top = the gap-rim presentation.
    top_rect = pygame.Rect(x0, y_top, cw, 8)
    pygame.draw.ellipse(surf, cap, top_rect)
    pygame.draw.ellipse(surf, cap_lit, top_rect.inflate(-2, -3))
    _aa_polyline(surf, _shade(cap, 40),
                 [(x0 + 2, y_top + 3), (cx, y_top + 1), (x0 + cw - 3, y_top + 3)])
    # Gold cord band around the drum with two short dangling ties.
    cord_y = body_top + (y_bot - body_top) // 2
    pygame.draw.line(surf, gold, (x0 + 1, cord_y), (x0 + cw - 2, cord_y), 2)
    pygame.draw.line(surf, _shade(gold, -34),
                     (x0 + 1, cord_y + 2), (x0 + cw - 2, cord_y + 2), 1)
    for tx in (x0 + 4, x0 + cw - 5):
        pygame.draw.line(surf, gold, (tx, cord_y + 2), (tx, y_bot - 1), 1)
    # The gold pom on top-centre (small bright bobble at the very crown).
    pom = (cx, y_top + 2)
    pygame.draw.circle(surf, _shade(gold, -30), pom, 3)
    pygame.draw.circle(surf, gold, (cx - 1, y_top + 1), 2)
    surf.set_at((cx - 1, y_top), _shade(gold, 40))
    if dark_sky:
        # Faint night halo so the pom reads as the crowning glint.
        glow = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*gold, 70), (5, 5), 4)
        surf.blit(glow, (cx - 5, y_top - 3), special_flags=pygame.BLEND_RGBA_ADD)

    # Darkened neck band on the head just under the cap so the crown pops.
    _, mid_b, sh_b = _face_triad(palette)
    neck_dark = _shade(sh_b, -16)
    nb_hw = int(half * 0.92)
    for k in range(3):
        t = 1.0 - k / 3.0
        pygame.draw.line(surf, _mix(mid_b, neck_dark, t),
                         (cx - nb_hw, y_bot + 1 + k), (cx + nb_hw, y_bot + 1 + k), 1)


# ── 3-layer plinth + foliage ────────────────────────────────────────────────

def _draw_plinth(surf, cx, base_y, half, palette, seed):
    # Lacquered-wood dais — the one iron-brown material so the base reads as a
    # dark shrine plinth distinct from the oxblood mask body.
    lit = _mix(_iron_brown(palette), (150, 96, 58), 0.5)
    mid = _iron_brown(palette)
    sh = _shade(_iron_brown(palette), -24)
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
    """One upright Tengu tower: mist -> plinth -> foliage -> adaptive head stack
    -> tokin cap at the gap rim. Height-adaptive head COUNT keeps every mask
    un-squashed (1 mask at ~70 px, several at 355)."""
    rng = random.Random(seed)
    half = PIPE_W // 2
    section_h = y_bot - y_top

    plinth_h = min(15, max(9, int(section_h * 0.14)))
    tokin_h = min(17, max(10, int(section_h * 0.14)))
    if section_h < 100:
        plinth_h = max(7, plinth_h - 2)
        tokin_h = max(9, tokin_h - 2)
    base_y = y_bot

    _draw_plinth_mist(surf, cx, base_y - plinth_h + 2, int(half * 2 * 1.6), palette)

    stack_bot = base_y - plinth_h
    stack_top = y_top + tokin_h
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

    # Tokin crowns the top head. Inset ~3 px below the gap rim so the two
    # towers' caps don't kiss at gap centre — the flyable channel stays
    # visually open (the head stack below is untouched by the inset).
    _draw_tokin(surf, cx, y_top + 4, stack_top, half, palette)

    _draw_plinth(surf, cx, base_y, half, palette, seed)
    draw_grass_bed(surf, cx, base_y - 1, PIPE_W + 12, 12, palette, seed=seed)
    draw_side_shrub(surf, cx - half - 6, base_y - 1, palette, scale=0.9)
    # Right shrub trimmed so the forward nose spur is the sole mid-column
    # RIGHT overhang in blackout — no base foliage competing with the tell.
    draw_side_shrub(surf, cx + half + 5, base_y - 1, palette, scale=0.55)


def candidate_tengu_yamabushi(surf, top_rect, bot_rect, palette, seed):
    """Bottom = Tengu tower rising from the ground, tokin at the gap. Top = the
    same tower vertical-FLIPPED from the ceiling — a symmetric two-ended totem,
    its tokin pointing into the gap so both caps meet at the rim. The vertical
    flip keeps the forward nose spur pointing the SAME way, so both ends read
    unmistakably Tengu."""
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
    candidate_tengu_yamabushi(full, top_rect, bot_rect, pal, seed=seed)

    tip_y = top_h - 6
    base_y = GROUND_Y + 8
    hero_h = base_y - tip_y
    hero = _bg(CACHE_W, hero_h, pal, hero_h - (base_y - GROUND_Y))
    hero.blit(full, (0, -tip_y))
    for ex in (MARGIN, MARGIN + PIPE_W):
        pygame.draw.line(hero, (230, 60, 60), (ex, 0), (ex, hero_h), 1)
    return hero, hero_h


def _closeup(pal, seed, scale=3):
    """Zoom on a single ground mask so the relief + nose spur is checkable."""
    surf = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    br = pygame.Rect(MARGIN, GROUND_Y - 150, PIPE_W, 150)
    tr = pygame.Rect(MARGIN, 0, PIPE_W, 0)
    candidate_tengu_yamabushi(surf, tr, br, pal, seed=seed)
    crop = pygame.Surface((CACHE_W, 120))
    crop.blit(_bg(CACHE_W, 120, pal, 120), (0, 0))
    crop.blit(surf, (0, -(GROUND_Y - 150)))
    return pygame.transform.scale(
        crop, (crop.get_width() * scale, crop.get_height() * scale))


def _blackout(pal, section_h, scale):
    """Solid-black silhouette of a hero section — the long-nose tell test. The
    crop reaches deep into the RIGHT gutter so the forward nose spur shows."""
    surf = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    br = pygame.Rect(MARGIN, GROUND_Y - section_h, PIPE_W, section_h)
    tr = pygame.Rect(MARGIN, 0, PIPE_W, 0)
    candidate_tengu_yamabushi(surf, tr, br, pal, seed=7)
    pad_l = 12
    pad_r = _NOSE_REACH + 12         # capture the forward nose overhang
    crop = pygame.Surface((PIPE_W + pad_l + pad_r, section_h + 8), pygame.SRCALPHA)
    crop.fill((238, 238, 240))
    for x in range(CACHE_W):
        for y in range(GROUND_Y - section_h, GROUND_Y):
            if surf.get_at((x, y))[3] > 40:
                cx = x - MARGIN + pad_l
                cy = y - (GROUND_Y - section_h) + 4
                if 0 <= cx < crop.get_width() and 0 <= cy < crop.get_height():
                    crop.set_at((cx, cy), (18, 18, 22))
    return pygame.transform.scale(
        crop, (crop.get_width() * scale, crop.get_height() * scale))


def main():
    pal = biome.palette_for_phase(PHASE_DAY)
    pal_n = biome.palette_for_phase(PHASE_NIGHT)

    # Body-hue proof: must read DARK cool oxblood (not tan), RED-dominant, and
    # DAY != NIGHT. Also confirm it is LOWER-value than the bright vermilion oni.
    _, mid_d, _ = _face_triad(pal)
    _, mid_n, _ = _face_triad(pal_n)
    verm_d = _vermilion(pal)
    lit_d, _, _ = _face_triad(pal)
    print("FACE OXBLOOD (mid tone)")
    print(f"  DAY   mid={mid_d} lum={_lum(mid_d):.1f}  R-G={mid_d[0]-mid_d[1]}")
    print(f"  NIGHT mid={mid_n} lum={_lum(mid_n):.1f}  R-G={mid_n[0]-mid_n[1]}")
    print(f"  day != night: {mid_d != mid_n}")
    print(f"  vs bright vermilion (day): oxblood lum={_lum(mid_d):.1f} < "
          f"vermilion lum={_lum(verm_d):.1f}  "
          f"[{'OK darker' if _lum(mid_d) < _lum(verm_d) else 'FAIL'}]")

    # FIX-1 metric: night face MASS must clear the night sky by >= ~28 lum.
    sky_n = _lum(pal_n["sky_top"])
    gap_n = _lum(mid_n) - sky_n
    print("NIGHT FACE-vs-SKY (mid mass vs sky_top)")
    print(f"  face lum={_lum(mid_n):.1f}  sky lum={sky_n:.1f}  gap={gap_n:.1f}"
          f"  [{'OK >=28' if gap_n >= 27.5 else 'FAIL'}]")
    # FIX-3 metric: day lit plane must sit clearly UNDER the day sky luminance.
    sky_d = _lum(pal["sky_top"])
    print("DAY LIT-PLANE vs SKY (raking-light plane must not twin sky)")
    print(f"  lit lum={_lum(lit_d):.1f}  sky lum={sky_d:.1f}  "
          f"sep={sky_d - _lum(lit_d):.1f}  "
          f"[{'OK lit darker than sky' if _lum(lit_d) < sky_d - 8 else 'FAIL'}]")

    hero_day, hd_h = _hero(pal, 7)
    hero_night, hn_h = _hero(pal_n, 7)
    close_d = _closeup(pal, 7)
    close_n = _closeup(pal_n, 7)
    close_d2 = _closeup(pal, 11)

    # Gap-rim clearance (bottom tower tokin reaching the gap line).
    gap_probe = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    gp_bot = pygame.Rect(MARGIN, 243, PIPE_W, GROUND_Y - 243)
    gp_top = pygame.Rect(MARGIN, 0, PIPE_W, 93)
    candidate_tengu_yamabushi(gap_probe, gp_top, gp_bot, pal, seed=7)
    # Bottom tower grows DOWN from the gap edge (243) -> probe down into it to
    # read the air above its cap; top tower is flipped up from 93 -> probe up.
    clear_bot = _gap_rim_clearance(gap_probe, MARGIN, MARGIN + PIPE_W, 243, up=False)
    clear_top = _gap_rim_clearance(gap_probe, MARGIN, MARGIN + PIPE_W, 93, up=True)
    print("GAP-RIM CLEARANCE (tokin -> flyable gap edge)")
    print(f"  bottom cap -> gap: {clear_bot}px   top cap -> gap: {clear_top}px")

    # Feasibility strip: bottom section at three heights + empty-run gate.
    strip_heights = [70, 210, 355]
    strips = []
    print("FILL GATE (max empty vertical run inside the 58px PIPE_W band)")
    for h in strip_heights:
        s = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
        br = pygame.Rect(MARGIN, GROUND_Y - h, PIPE_W, h)
        tr = pygame.Rect(MARGIN, 0, PIPE_W, 0)
        candidate_tengu_yamabushi(s, tr, br, pal, seed=7)
        run = _max_empty_run(s, MARGIN, MARGIN + PIPE_W, GROUND_Y - h, GROUND_Y)
        crop = pygame.Surface((CACHE_W, h + 8))
        crop.blit(_bg(CACHE_W, h + 8, pal, h), (0, 0))
        crop.blit(s, (0, -(GROUND_Y - h)))
        for ex in (MARGIN, MARGIN + PIPE_W):
            pygame.draw.line(crop, (230, 60, 60), (ex, 0), (ex, h + 8), 1)
        strips.append((h, crop, run))
        print(f"  h={h:3d}  max empty run = {run}px  [{'OK' if run <= 12 else 'FAIL'}]")

    # Blackout thumbnails: long-nose-read test at native 58px, shown 1x + 3x.
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
    col_close = close_d.get_width()
    col_bo = max(bo3.get_width(), bo1.get_width()) + 20
    strips_total_h = sum(c.get_height() + label_h + pad for _, c, _ in strips)

    body_h = max(hd_h, hn_h, close_d.get_height() * 2 + label_h,
                 strips_total_h, bo3.get_height() + 40) + label_h
    sheet_w = pad + col_hero + pad + col_hero + pad + col_hero + pad + \
        col_close + pad + col_bo + pad
    sheet_h = head_h + body_h + pad * 2
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((24, 25, 30))

    sheet.blit(title.render(
        "tengu_yamabushi — long-nosed goblin totem  ·  round_2",
        True, (245, 240, 230)), (pad, 12))
    sheet.blit(sub.render(
        "red edges = PIPE_W (58px) collision band  ·  DARK OXBLOOD face  ·  "
        "long forward NOSE-SPUR (gutter overhang)  ·  bushy white brows + "
        "moustache  ·  gold-rim glare eyes  ·  black tokin cap + gold pom",
        True, (170, 172, 182)), (pad, 40))
    sheet.blit(sub.render(
        f"R2 fixes: night face mass lifted (gap vs sky {gap_n:.0f}, was 17) · "
        f"day lit plane pulled off sky ({sky_d - _lum(lit_d):.0f} under) · "
        "gap caps backed ~3px off the rim · both-edge night rim · trimmed R shrub",
        True, (150, 210, 160)), (pad, 56))

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

    # feasibility strips
    x += col_hero + pad
    sy = head_h
    sheet.blit(lab.render("FILL GATE — bottom section", True, (255, 224, 150)),
               (x, sy - 20))
    for h, crop, run in strips:
        sheet.blit(crop, (x, sy))
        pygame.draw.rect(sheet, (60, 62, 72), (x, sy, col_hero, crop.get_height()), 1)
        ok = "OK" if run <= 12 else "FAIL"
        sheet.blit(lab.render(f"h={h}px  ·  run {run}px  [{ok}]", True,
                              (200, 235, 170) if run <= 12 else (255, 140, 140)),
                   (x, sy + crop.get_height() + 4))
        sy += crop.get_height() + label_h + pad

    # face close-ups (day + night + 2nd seed) — 3x
    x += col_hero + pad
    sheet.blit(close_d, (x, head_h))
    pygame.draw.rect(sheet, (60, 62, 72),
                     (x, head_h, close_d.get_width(), close_d.get_height()), 1)
    sheet.blit(lab.render("FACE 3x — DAY", True, (255, 224, 150)),
               (x, head_h + close_d.get_height() + 4))
    yy = head_h + close_d.get_height() + label_h
    sheet.blit(close_n, (x, yy))
    pygame.draw.rect(sheet, (60, 62, 72),
                     (x, yy, close_n.get_width(), close_n.get_height()), 1)
    sheet.blit(lab.render("FACE 3x — NIGHT", True, (255, 224, 150)),
               (x, yy + close_n.get_height() + 4))

    # blackout thumbnails
    x += col_close + pad
    sheet.blit(lab.render("BLACKOUT (long-nose tell)", True, (255, 224, 150)),
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
