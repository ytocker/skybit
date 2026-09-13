"""kitsune_inari — high-fidelity white Inari-fox mask totem (candidate).

A porcelain-white shrine-fox stack: smooth planar fox faces with narrow
up-slanted gold-rimmed eyes, vermilion swirl markings, and a tapered black-
nosed muzzle, crowned by TALL near-vertical pointed EARS framing a gold hōju
flame-jewel at the gap rim. The family's cool-colour breaker — the only
white face against the red demon poles.

Re-skin of the winning `moai_ancestor` totem: it REUSES that stack-driver
skeleton verbatim (the height-adaptive head COUNT, the `_hw_at` full-width
core-fill guarantee, the neck-waist seams, `_draw_plinth_mist` + foliage
base, and the vertical-FLIP two-ended mirror). Only the materials, the
`_draw_head` relief, and the crown are swapped: dark volcanic basalt →
porcelain white, and the scoria pukao drum → the fox ear-crown.

The two make-or-breaks are AD-driven:
  1. The EARS must read TALLER and THINNER than any horn in the family, so
     the blackout never twins Oni — they are near-vertical pointed triangles,
     not blunt bull-horns.
  2. Porcelain-white on a bright DAY sky (horizon lum ~220) is a low-contrast
     trap. A firm continuous dark INK keyline rings the whole white face, and
     the vermilion/gold markings + a darker jaw-shadow carry the silhouette so
     it never washes out at gameplay scale.

Standalone review candidate — imports the REAL pagoda helpers so its
materials + lighting match the shipped pillars, but wires nothing into the
live game.

Run:  python docs/pillar_landmarks/japanese_totems/kitsune_inari/render.py
Out:  docs/pillar_landmarks/japanese_totems/kitsune_inari/round_1.png
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
# pillars, so the 5-min day->night biome retint sweeps straight through.
from game.pillar_pagodas import (
    _mix, _shade, _gradient_rect, _aa_polyline, _lit_niche, _tile_hatch,
    _draw_plinth_mist, _is_dark_sky, _is_warming_sky,
    _cap_lit_for_dark_sky, _cap_dark_for_dark_sky, _buddha_eye,
    _porcelain_white, _plaster, _vermilion, _gold_bright, _bronze, _lapis,
)
from game.pillar_variants import draw_grass_bed
from game.draw import draw_side_shrub


MARGIN = 64                       # matches entities.Pipe eave/ornament gutter
CACHE_W = PIPE_W + MARGIN * 2
CACHE_H = GROUND_Y
PHASE_DAY = 0.30                  # midday — brightest horizon, the white-wash test
PHASE_NIGHT = 0.85               # deep night — checks lit rim + socket glow + jewel


# ── Materials ────────────────────────────────────────────────────────────────
#
# The headline re-skin vs the dark-basalt moai: the body is PORCELAIN WHITE
# (Bao'en glaze), the coolest, brightest face in the totem set — the deliberate
# value/hue breaker against the vermilion demon poles. Because porcelain rides
# so close to the pale horizon by day, its own gradient can't carry the read;
# the firm dark keyline + the vermilion/gold markings do. All keys derive from
# palette so the biome retint sweeps through.

def _fox_white_triad(palette):
    base = _porcelain_white(palette)
    lit = _shade(base, 14)
    mid = base
    # A COOL grey shadow (not warm) so the porcelain reads as cold shrine-white,
    # and so the shaded plane gives the face volume against a flat pale sky. Held
    # deep (well under the pale-horizon lum) so the right cheek/jaw is a real dark
    # MASS, not a hairline edge — the white face can't vanish on the day horizon.
    sh = _shade(_mix(base, (140, 150, 170), 0.40), -42)
    # Night: keep the lit from blowing out, and FLOOR the shadow high so the
    # white face stays a legible pale mass instead of sinking into the dark sky.
    lit = _cap_lit_for_dark_sky(lit, palette, cap=214)
    sh = _cap_dark_for_dark_sky(sh, palette, floor=118)
    return lit, mid, sh


def _fox_ink(palette):
    # The AD guard: a firm near-black INK, floored dark in EVERY phase, for the
    # continuous keyline that rings the white face + the nose-dot + mouth. This
    # is what holds the silhouette against the bright day horizon where the
    # porcelain gradient alone would wash out.
    return _mix(palette['stone_dark'], (24, 20, 30), 0.74)


def _muzzle_shadow(palette):
    # A darker cool-porcelain patch for the snout + jaw undercut so the lower
    # face reads as a forward muzzle and anchors a firm dark base value.
    _, mid, _ = _fox_white_triad(palette)
    return _shade(_mix(mid, (140, 150, 168), 0.48), -36)


def _lum(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


# ── Head geometry ──────────────────────────────────────────────────────────
#
# Reused verbatim from moai: the head is a tall near-full-width straight column
# so the 58 px collision band is always solid, with only a shallow neck WAIST
# at each stacked seam. The fox identity lives entirely in the INTERIOR paint
# (slant eyes + vermilion markings + muzzle) plus the EAR crown — the body
# silhouette stays a clean solid porcelain post so neck junctions never open.

_TAPER = 5                        # px of neck-waist ramp at each seam
_WAIST = 5                        # px each side the waist pinches in from the edge
_HEAD_H_FLOOR = 96                # natural head height -> drives adaptive COUNT


def _hw_at(y, y0, y1, half, *, crown, base):
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
    """One row of the head body: a horizontal 3-stop gradient, lit LEFT, shadow
    RIGHT — the raking-light model that gives the flat porcelain post volume."""
    w = xr - xl
    if w < 2:
        return
    for i in range(w):
        t = i / (w - 1)
        col = _mix(lit, mid, t * 2) if t < 0.5 else _mix(mid, sh, (t - 0.5) * 2)
        surf.set_at((xl + i, y), col)


def _fox_eye(surf, cx_e, cy_e, w, h, outward, *, ink, gold, verm, palette):
    """A narrow, up-slanted, sly fox eye. Built over a `_lit_niche` socket so
    it inherits the free amber night-glow (the shrine-fox 'living eye'); a
    gold-rimmed dark almond slants UP toward the temple with a vermilion liner
    flick off the outer corner."""
    _lit_niche(surf, cx_e, cy_e, max(4, w), max(4, h), palette)
    inner = (cx_e - outward * w, cy_e + h // 2 + 1)   # nose-side corner, lower
    outer = (cx_e + outward * w, cy_e - h // 2 - 1)   # temple-side corner, higher
    top = (cx_e, cy_e - h // 2)
    bot = (cx_e, cy_e + h // 2)
    almond = [inner, top, outer, bot]
    pygame.draw.polygon(surf, ink, almond)            # dark eyeball
    _aa_polyline(surf, gold, almond, closed=True)     # gold rim
    # Vermilion liner flicking up-and-out from the temple corner.
    _aa_polyline(surf, verm,
                 [(cx_e, cy_e - 1), outer,
                  (outer[0] + outward * 3, outer[1] - 2)])


# ── One fox mask head ────────────────────────────────────────────────────────

def _draw_head(surf, cx, y0, y1, half, palette, rng, *, crown, base):
    hh = y1 - y0
    lit, mid, sh = _fox_white_triad(palette)
    ink = _fox_ink(palette)
    verm = _vermilion(palette)
    verm_lit = _shade(verm, 40)
    gold = _gold_bright(palette)
    muzzle = _muzzle_shadow(palette)
    dark_sky = _is_dark_sky(palette)

    # Silhouette fill + outline capture (for the keyline + night rim).
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

    # Feature bands (fractions of head height).
    crest_y = y0 + int(hh * 0.11)
    eye_y = y0 + int(hh * 0.40)
    eye_h = max(4, int(hh * 0.11))
    eye_w = max(5, int(half * 0.36))
    eye_dx = int(half * 0.44)
    cheek_y = y0 + int(hh * 0.58)
    muzzle_y = y0 + int(hh * 0.70)
    nose_y = y0 + int(hh * 0.80)
    mouth_y = y0 + int(hh * 0.87)
    jaw_y = y0 + int(hh * 0.93)

    if not thumbnail:
        # 0. One firm dark RIGHT-cheek/jaw plane — a solid shaded half so the
        #    white face carries real MASS (a distinct dark cheek), not just an
        #    ink outline, when the pale porcelain rides the bright day horizon.
        #    The lit LEFT plane stays bright, so the centreline reads as the nose
        #    ridge splitting a lit and a shadow side (the volume the flat post
        #    lacked). Features paint over it, gaining contrast.
        cheek = _shade(_mix(mid, (128, 138, 158), 0.50), -34)
        right_edge = cx + int(half * 0.9)
        pygame.draw.polygon(surf, cheek,
                            [(cx - 1, eye_y - eye_h),
                             (right_edge, eye_y),
                             (right_edge, muzzle_y),
                             (cx + int(half * 0.24), jaw_y + 1),
                             (cx - 1, muzzle_y)])

        # 1. Forehead vermilion FLAME-CREST — the Inari brand mark, a small
        #    upward flame teardrop centred on the brow.
        fw = max(3, int(half * 0.22))
        flame = [(cx, crest_y - int(hh * 0.06)),
                 (cx - fw, crest_y + int(hh * 0.05)),
                 (cx, crest_y + int(hh * 0.02)),
                 (cx + fw, crest_y + int(hh * 0.05))]
        pygame.draw.polygon(surf, verm, flame)
        _aa_polyline(surf, verm_lit,
                     [(cx, crest_y - int(hh * 0.06)), (cx, crest_y)])
        _aa_polyline(surf, ink, flame, closed=True)

        # 2. Cool muzzle patch — a rounded lower-face plane so the snout reads
        #    forward, giving a firm dark base value under the pale cheeks.
        mw = int(half * 0.62)
        mrect = pygame.Rect(cx - mw, muzzle_y, mw * 2, jaw_y - muzzle_y + 2)
        pygame.draw.ellipse(surf, muzzle, mrect)
        pygame.draw.ellipse(surf, _shade(mid, 8), mrect.inflate(-3, -3))

        # 3. Slant fox eyes over lit-niche sockets.
        _fox_eye(surf, cx - eye_dx, eye_y, eye_w, eye_h, -1,
                 ink=ink, gold=gold, verm=verm, palette=palette)
        _fox_eye(surf, cx + eye_dx, eye_y, eye_w, eye_h, +1,
                 ink=ink, gold=gold, verm=verm, palette=palette)

        # 4. Gold brow arcs riding just above each eye — the shrine gilt trim.
        for s in (-1, 1):
            bx = cx + s * eye_dx
            _aa_polyline(surf, gold,
                         [(bx - eye_w, eye_y - eye_h),
                          (bx, eye_y - eye_h - 2),
                          (bx + eye_w, eye_y - eye_h + 1)])

        # 5. Vermilion cheek SWIRLS — a comma/magatama sweep on each cheek.
        for s in (-1, 1):
            cxs = cx + s * int(half * 0.60)
            swirl = [(cxs - s * 3, cheek_y - 3),
                     (cxs + s * 2, cheek_y),
                     (cxs - s * 1, cheek_y + 4),
                     (cxs - s * 5, cheek_y + 3)]
            _aa_polyline(surf, verm, swirl)
            surf.set_at((cxs - s * 4, cheek_y + 2), verm_lit)

        # 6. Black nose-dot at the muzzle tip + delicate closed mouth.
        nr = max(2, int(half * 0.13))
        pygame.draw.polygon(surf, ink,
                            [(cx - nr, nose_y - 1), (cx + nr, nose_y - 1),
                             (cx, nose_y + nr)])
        surf.set_at((cx - 1, nose_y - 1), _shade(mid, 10))   # tiny nose glint
        pygame.draw.line(surf, ink, (cx, nose_y + nr),
                         (cx, mouth_y - 1), 1)                # philtrum
        _aa_polyline(surf, ink,
                     [(cx - int(half * 0.24), mouth_y),
                      (cx, mouth_y + 2),
                      (cx + int(half * 0.24), mouth_y)])

        # 7. Jaw undercut — a firm dark band so the pale face has a grounded
        #    lower edge against a bright sky (AD anti-wash guard).
        pygame.draw.rect(surf, _shade(muzzle, -20),
                         (cx - int(half * 0.5), jaw_y, int(half), 2))

        # 8. Sparse porcelain crackle-glaze speckle — a couple of faint hairline
        #    craze lines, kept off the eyes so the relief stays clean.
        for k in range(2):
            sy = y0 + int(hh * (0.30 + 0.20 * k))
            sx0 = cx - int(half * 0.5)
            pygame.draw.line(surf, _shade(sh, -8),
                             (sx0, sy), (sx0 + int(half * 0.4), sy), 1)
    else:
        # Thumbnail: guarantee the fox reads on 2 slant eye-dashes + vermilion
        # liner + a nose-dot alone at ~40 px face height (the 2-dot fallback).
        for s in (-1, 1):
            ex = cx + s * eye_dx
            pygame.draw.line(surf, ink,
                             (ex - eye_w, eye_y + 1), (ex + eye_w, eye_y - 1), 2)
            surf.set_at((ex + s * eye_w, eye_y - 1), verm)
        pygame.draw.polygon(surf, ink,
                            [(cx - 2, nose_y - 1), (cx + 2, nose_y - 1),
                             (cx, nose_y + 2)])
        surf.set_at((cx, crest_y), verm)

    # 9. Firm continuous dark keyline — rings the WHITE face so the silhouette
    #    holds against the pale day horizon. THE make-or-break AD guard.
    outline = left_pts + list(reversed(right_pts))
    _aa_polyline(surf, ink, outline, closed=True)

    # 10. Night ONLY: a crisp cool rim-light down the LEFT edge so the porcelain
    #     separates from a dark sky. By DAY we deliberately leave the dark ink
    #     keyline untouched on every edge — against the pale horizon a bright rim
    #     would wash the white face out; the dark keyline is what holds it.
    if dark_sky:
        rim = _shade(lit, 40)
        for i in range(0, len(left_pts)):
            x, y = left_pts[i]
            surf.set_at((x, y), rim)


# ── Fox ear-crown (replaces the scoria pukao) ────────────────────────────────

def _draw_crown(surf, cx, y_top, y_bot, half, palette):
    """The fox topper at the gap rim: a broad porcelain forehead-crest filling
    the collision band to within ~10 px of the rim, crowned by TWO tall thin
    near-vertical pointed EARS and a small central gold hōju flame-jewel that sits
    LOW on the plateau. The ears stand INSIDE the 58 px band (taller + thinner
    than any family horn) and own the skyline alone; the forehead-crest is the
    solid gap-rim presenter and the jewel a low interior ornament, not a peak."""
    lit, mid, sh = _fox_white_triad(palette)
    ink = _fox_ink(palette)
    verm = _vermilion(palette)
    verm_lit = _shade(verm, 40)
    gold = _gold_bright(palette)
    dark_sky = _is_dark_sky(palette)

    ch = y_bot - y_top
    # Solid forehead plateau: fill the band from the top head up to within the
    # gate margin of the rim. `notch` is BOTH the plateau-to-rim gap AND the
    # centre empty-run between the ears — pushed to the 12 px cap so the ears
    # stand as TALL as the skeleton allows above the solid head.
    notch = min(12, max(8, int(ch * 0.52)))
    crest_top = y_top + notch
    # The whole plateau top sat at the ear-valley line (= notch, ~12 px of open
    # sky above it), leaving ZERO drift room under the 12 px fill gate. Raise the
    # porcelain fill 2 px ABOVE that line across the full band so no crown column
    # opens more than ~10 px — bought without shortening the ears, whose tips
    # still reach y_top well above this plateau.
    fill_top = crest_top - 2
    for y in range(fill_top, y_bot + 1):
        _grad_hspan(surf, y, int(cx - half), int(cx + half), lit, mid, sh)

    # Central hōju flame-jewel — a SMALL gold teardrop sitting LOW on the plateau
    # between the ears. Its tip is dropped to the plateau line (>=6 px below the
    # ear tips) so the two pointed ears own the skyline alone and the crown never
    # reads as a three-bump ear-jewel-ear at gameplay scale.
    jw = max(3, int(half * 0.16))
    jtip = y_top + max(6, notch - 4)
    mount = [(cx - jw, crest_top + 1), (cx + jw, crest_top + 1),
             (cx + jw - 1, crest_top - 1), (cx - jw + 1, crest_top - 1)]
    pygame.draw.polygon(surf, verm, mount)
    jewel = [(cx, jtip), (cx - jw, crest_top - 1),
             (cx, crest_top + 1), (cx + jw, crest_top - 1)]
    pygame.draw.polygon(surf, gold, jewel)
    _aa_polyline(surf, _shade(gold, 34), [(cx, jtip), (cx, crest_top)])
    _aa_polyline(surf, ink, jewel, closed=True)

    # Two TALL THIN pointed ears. Their BASE sits low on the already-solid
    # forehead (free — that band is filled) so the ear reads TALL to the rim,
    # while the only genuinely-empty region (the notch either side of the jewel)
    # stays <= 12 px. Near-vertical + narrow-based + sharp so the blackout never
    # twins Oni's thick blunt backswept horn.
    ear_base_y = crest_top + int(ch * 0.58)
    ear_h = ear_base_y - y_top
    for s in (-1, 1):
        ear_cx = cx + s * int(half * 0.58)
        hb = max(3, int(half * 0.16))               # ~9 px base -> thin
        # A whisper of outward lean with the very tip toed 1 px back INward, so
        # the flipped ceiling twin never pinches into an hourglass at the gap.
        tip = (ear_cx + s * int(half * 0.08) - s, y_top)
        base_l = (ear_cx - hb, ear_base_y)
        base_r = (ear_cx + hb, ear_base_y)
        # Shallow porcelain fillet rooting the ear into the plateau — the ear
        # reads grown-from the forehead (not stuck on) and the shoulder columns
        # beside it fill a touch higher for extra fill-gate margin.
        pygame.draw.polygon(surf, mid,
                            [(ear_cx - hb - 2, fill_top + 2),
                             (ear_cx, fill_top - 1),
                             (ear_cx + hb + 2, fill_top + 2)])
        ear = [base_l, tip, base_r]
        pygame.draw.polygon(surf, mid, ear)            # porcelain body
        _aa_polyline(surf, lit, [base_l, tip])         # lit outer plane
        # Vermilion inner-ear membrane, a slimmer triangle inside the porcelain.
        im = max(1, hb - 3)
        inner = [(ear_cx - im, ear_base_y - 2),
                 (ear_cx + s * int(half * 0.06), y_top + int(ear_h * 0.34)),
                 (ear_cx + im, ear_base_y - 2)]
        pygame.draw.polygon(surf, verm, inner)
        surf.set_at((ear_cx, ear_base_y - 3), verm_lit)
        # Gold ear-tip stud + firm ink keyline around the whole ear.
        pygame.draw.line(surf, gold, tip, (tip[0] - s, tip[1] + 3), 2)
        _aa_polyline(surf, ink, ear, closed=True)

    # A shadowed neck band on the head just beneath the crest so the bright
    # crown pops as a distinct topper on a slightly sunk post.
    nb_hw = int(half * 0.9)
    for k in range(3):
        t = 1.0 - k / 3.0
        pygame.draw.line(surf, _mix(mid, _shade(sh, -14), t),
                         (cx - nb_hw, y_bot + 1 + k), (cx + nb_hw, y_bot + 1 + k), 1)


# ── 3-layer plinth + foliage (reused from moai) ──────────────────────────────

def _draw_plinth(surf, cx, base_y, half, palette, seed):
    lit, mid, sh = _fox_white_triad(palette)
    layers = 3
    for i in range(layers):
        lw = int(half * 2 * (1.12 + 0.16 * i))
        lh = 5
        ly = base_y - (layers - i) * lh
        r = pygame.Rect(cx - lw // 2, ly, lw, lh)
        _gradient_rect(surf, r, lit, mid, sh)
        # A vermilion trim band on the top plinth ties the base to the markings.
        if i == layers - 1:
            pygame.draw.line(surf, _vermilion(palette),
                             (r.x + 2, r.y + 1), (r.right - 3, r.y + 1), 1)
        pygame.draw.line(surf, _fox_ink(palette),
                         (r.x, r.bottom - 1), (r.right - 1, r.bottom - 1), 1)
        pygame.draw.line(surf, _shade(lit, 12), (r.x, r.y), (r.right - 1, r.y), 1)


def _draw_tower(surf, cx, y_top, y_bot, palette, seed):
    """One upright fox totem: mist -> plinth -> foliage -> adaptive fox-head
    stack -> ear-crown at the gap rim. Height-adaptive COUNT keeps every face
    un-squashed (1 fox at ~70 px, several at 355)."""
    rng = random.Random(seed)
    half = PIPE_W // 2
    section_h = y_bot - y_top

    plinth_h = min(15, max(9, int(section_h * 0.14)))
    crown_h = min(24, max(14, int(section_h * 0.17)))
    if section_h < 100:
        plinth_h = max(7, plinth_h - 2)
        crown_h = max(13, crown_h - 2)
    base_y = y_bot

    _draw_plinth_mist(surf, cx, base_y - plinth_h + 2, int(half * 2 * 1.6), palette)

    stack_bot = base_y - plinth_h
    stack_top = y_top + crown_h
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

    # Ear-crown crowns the top head and reaches the gap rim.
    _draw_crown(surf, cx, y_top, stack_top, half, palette)

    _draw_plinth(surf, cx, base_y, half, palette, seed)
    draw_grass_bed(surf, cx, base_y - 1, PIPE_W + 12, 12, palette, seed=seed)
    draw_side_shrub(surf, cx - half - 6, base_y - 1, palette, scale=0.9)
    draw_side_shrub(surf, cx + half + 6, base_y - 1, palette, scale=0.8)


def candidate_kitsune_inari(surf, top_rect, bot_rect, palette, seed):
    """Bottom = fox totem rising from the ground, ears at the gap. Top = the
    same totem vertical-FLIPPED from the ceiling — a symmetric two-ended totem
    whose ear-crowns meet at the rim (ears symmetric -> clean flip)."""
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
    candidate_kitsune_inari(full, top_rect, bot_rect, pal, seed=seed)

    tip_y = top_h - 6
    base_y = GROUND_Y + 8
    hero_h = base_y - tip_y
    hero = _bg(CACHE_W, hero_h, pal, hero_h - (base_y - GROUND_Y))
    hero.blit(full, (0, -tip_y))
    for ex in (MARGIN, MARGIN + PIPE_W):
        pygame.draw.line(hero, (230, 60, 60), (ex, 0), (ex, hero_h), 1)
    return hero, hero_h


def _closeup(pal, seed, scale=3):
    """Zoom on the top ground head + ear-crown so the fox relief + ears read."""
    surf = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    br = pygame.Rect(MARGIN, GROUND_Y - 150, PIPE_W, 150)
    tr = pygame.Rect(MARGIN, 0, PIPE_W, 0)
    candidate_kitsune_inari(surf, tr, br, pal, seed=seed)
    top = GROUND_Y - 150
    crop = pygame.Surface((CACHE_W, 120))
    crop.blit(_bg(CACHE_W, 120, pal, 120), (0, 0))
    crop.blit(surf, (0, -top))
    return pygame.transform.scale(
        crop, (crop.get_width() * scale, crop.get_height() * scale))


def _blackout(pal, section_h, scale):
    """Solid-black silhouette of a hero section — the TALL-EARS tell test."""
    surf = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    br = pygame.Rect(MARGIN, GROUND_Y - section_h, PIPE_W, section_h)
    tr = pygame.Rect(MARGIN, 0, PIPE_W, 0)
    candidate_kitsune_inari(surf, tr, br, pal, seed=7)
    pad_x = 16                       # margin around the in-band ear tips
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

    # Body-hue proof: porcelain reads PALE + cool, DAY != NIGHT.
    _, mid_d, sh_d = _fox_white_triad(pal)
    _, mid_n, sh_n = _fox_white_triad(pal_n)
    print("PORCELAIN BODY (mid tone)")
    print(f"  DAY   mid={mid_d} lum={_lum(mid_d):.1f}")
    print(f"  NIGHT mid={mid_n} lum={_lum(mid_n):.1f}")
    print(f"  day != night: {mid_d != mid_n}")

    # THE make-or-break: does the dark keyline hold the white face against the
    # brightest part of the day sky (the pale horizon)? ink must be clearly
    # darker than BOTH the porcelain body AND the pale sky.
    ink_d = _fox_ink(pal)
    body_lum = _lum(mid_d)
    ink_lum = _lum(ink_d)
    sky_hi = _lum(pal['horizon'])          # brightest sky band (worst case)
    print("WHITE-FACE SILHOUETTE GUARD (day)")
    print(f"  porcelain lum={body_lum:.1f}  keyline ink lum={ink_lum:.1f}  "
          f"pale-sky lum={sky_hi:.1f}")
    print(f"  ink vs body dL=-{body_lum - ink_lum:.1f}  "
          f"ink vs sky dL=-{sky_hi - ink_lum:.1f}  "
          f"[{'OK' if (body_lum - ink_lum) >= 60 and (sky_hi - ink_lum) >= 60 else 'FAIL'}]")
    vd = _vermilion(pal)
    print(f"  vermilion marking lum={_lum(vd):.1f} (mid-value anchor vs pale)  "
          f"gold trim lum={_lum(_gold_bright(pal)):.1f}")

    # Face-MASS proof: the right cheek/jaw shadow plane must sit well BELOW the
    # pale-horizon lum so the white face carries a dark mass, not just an outline.
    cheek_d = _shade(_mix(mid_d, (128, 138, 158), 0.50), -34)
    muzzle_d = _muzzle_shadow(pal)
    print("DAY FACE-MASS (dark cheek/jaw vs pale sky)")
    print(f"  cheek plane lum={_lum(cheek_d):.1f}  muzzle lum={_lum(muzzle_d):.1f}  "
          f"body-shadow lum={_lum(sh_d):.1f}  vs sky {sky_hi:.1f}  "
          f"[{'OK' if _lum(cheek_d) <= sky_hi - 55 else 'THIN'}]")

    hero_day, hd_h = _hero(pal, 7)
    hero_night, hn_h = _hero(pal_n, 7)
    close_day = _closeup(pal, 7)
    close_night = _closeup(pal_n, 7)

    # Gap-rim clearance (both towers' ear-crowns reaching the gap line).
    gap_probe = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    gp_bot = pygame.Rect(MARGIN, 243, PIPE_W, GROUND_Y - 243)
    gp_top = pygame.Rect(MARGIN, 0, PIPE_W, 93)
    candidate_kitsune_inari(gap_probe, gp_top, gp_bot, pal, seed=7)
    clear_bot = _gap_rim_clearance(gap_probe, MARGIN, MARGIN + PIPE_W, 243, up=True)
    clear_top = _gap_rim_clearance(gap_probe, MARGIN, MARGIN + PIPE_W, 93, up=True)
    print("GAP-RIM CLEARANCE (ear-crown -> gap)")
    print(f"  bottom -> gap: {clear_bot}px   top(flipped) -> gap: {clear_top}px")

    # Feasibility strip: bottom section at three heights + empty-run gate.
    strip_heights = [70, 210, 355]
    strips = []
    print("FILL GATE (max empty vertical run inside the 58px PIPE_W band; "
          "gate<=12, TARGET<=10)")
    for h in strip_heights:
        s = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
        br = pygame.Rect(MARGIN, GROUND_Y - h, PIPE_W, h)
        tr = pygame.Rect(MARGIN, 0, PIPE_W, 0)
        candidate_kitsune_inari(s, tr, br, pal, seed=7)
        run = _max_empty_run(s, MARGIN, MARGIN + PIPE_W, GROUND_Y - h, GROUND_Y)
        crop = pygame.Surface((CACHE_W, h + 8))
        crop.blit(_bg(CACHE_W, h + 8, pal, h), (0, 0))
        crop.blit(s, (0, -(GROUND_Y - h)))
        for ex in (MARGIN, MARGIN + PIPE_W):
            pygame.draw.line(crop, (230, 60, 60), (ex, 0), (ex, h + 8), 1)
        strips.append((h, crop, run))
        mark = 'OK' if run <= 10 else ('gate-ok' if run <= 12 else 'FAIL')
        print(f"  h={h:3d}  max empty run = {run}px  [{mark}]")

    # Blackout: tall-ears tell at native 58px, shown 1x + 3x.
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

    body_h = max(hd_h, hn_h, close_day.get_height() * 2 + label_h * 2,
                 strips_total_h, bo3.get_height() + 40) + label_h
    sheet_w = pad + col_hero + pad + col_hero + pad + col_hero + pad + \
        col_close + pad + col_bo + pad
    sheet_h = head_h + body_h + pad * 2
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((24, 25, 30))

    sheet.blit(title.render(
        "kitsune_inari — white Inari-fox mask totem  ·  round_2",
        True, (245, 240, 230)), (pad, 12))
    sheet.blit(sub.render(
        "red edges = PIPE_W (58px) collision band  ·  PORCELAIN-WHITE face  ·  "
        "slant gold-rim eyes + vermilion swirls + black muzzle  ·  TALL THIN EARS "
        "+ gold hōju jewel  ·  symmetric ceiling flip", True, (170, 172, 182)),
        (pad, 40))
    sheet.blit(sub.render(
        f"AD guards: dark keyline holds white vs pale sky "
        f"(ink lum {ink_lum:.0f} vs body {body_lum:.0f} vs sky {sky_hi:.0f})  ·  "
        "ears TALLER/THINNER than any horn (near-vertical points)",
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

    # face close-ups (day + night)
    x += col_hero + pad
    sheet.blit(close_day, (head_h and x, head_h))
    pygame.draw.rect(sheet, (60, 62, 72),
                     (x, head_h, close_day.get_width(), close_day.get_height()), 1)
    sheet.blit(lab.render("FACE 3x — DAY", True, (255, 224, 150)),
               (x, head_h + close_day.get_height() + 4))
    cy2 = head_h + close_day.get_height() + label_h + 4
    sheet.blit(close_night, (x, cy2))
    pygame.draw.rect(sheet, (60, 62, 72),
                     (x, cy2, close_night.get_width(), close_night.get_height()), 1)
    sheet.blit(lab.render("FACE 3x — NIGHT", True, (255, 224, 150)),
               (x, cy2 + close_night.get_height() + 4))

    # blackout thumbnails
    x += col_close + pad
    sheet.blit(lab.render("BLACKOUT (tall-ears tell)", True, (255, 224, 150)),
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
