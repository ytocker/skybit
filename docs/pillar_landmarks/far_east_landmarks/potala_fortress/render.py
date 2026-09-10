"""potala_fortress — high-fidelity Potala Palace pillar (candidate).

The BROAD FLAT-TOPPED MASSIF pole of the far-east-landmarks family: a
solid, inward-BATTERED fortress-palace whose walls lean in as they rise.
The tell that stops it from reading as a generic trapezoid is a TWO-AXIS
colour split, not just a slope:

  * WHITE-below / RED-above  — the whole lower wall is whitewashed
    Potrang Karpo (`_porcelain_white`/`_plaster`); the upper mass is the
    deep iron-oxide Potrang Marpo (`_tibet_red`/`_vermilion`).
  * RED-core-in-WHITE-wings — inside that upper band the deep-red central
    palace is flanked by lower white wings, so a row reads white|RED|white.

Marching up both faces are rows of small dark TRAPEZOID windows (wider at
the top, the Tibetan black surround), recessed and lantern-lit at night.
A dark-maroon BENMA frieze band (`_tibet_ochre` pushed to maroon) caps the
white wall and the red palace, and a cluster of gilt gabled GYAPHIB roofs
(`_gold_bright`) crowns the top, overhanging the gap rim as the crown.

Everything is palette-derived via `_mix`/lit-shadow triads so the 5-min
biome day->night retint sweeps straight through; the raw-RGB anchors are
fixed archetype biases only, exactly as the shipped pagodas do.

Standalone review candidate — wires nothing into the live game.

Run:  python docs/pillar_landmarks/far_east_landmarks/potala_fortress/render.py
Out:  docs/pillar_landmarks/far_east_landmarks/potala_fortress/round_1.png
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

pygame.init()
pygame.display.set_mode((1, 1))

from game.config import GROUND_Y, PIPE_W
from game import biome

# Same materials + lighting language as the shipped Tibetan pillars
# (Kumbum lineage) so the whitewash, iron-oxide red and gilt read on-palette.
from game.pillar_pagodas import (
    _mix, _shade, _gradient_rect, _aa_polyline, _lit_niche, _tile_hatch,
    _draw_plinth_mist, _is_dark_sky, _is_warming_sky,
    _cap_lit_for_dark_sky, _cap_dark_for_dark_sky,
    _porcelain_white, _plaster, _vermilion, _tibet_red, _tibet_ochre,
    _gold_bright, _bronze,
)
from game.pillar_variants import draw_grass_bed
from game.draw import draw_side_shrub


MARGIN = 64                       # matches entities.Pipe eave/ornament gutter
CACHE_W = PIPE_W + MARGIN * 2
CACHE_H = GROUND_Y
PHASE_DAY = 0.30                  # midday — hardest test for the two-tone split
PHASE_NIGHT = 0.85               # deep night — window glow + gold-roof gleam

# ── Massif geometry ──────────────────────────────────────────────────────────
#
# The wall is BATTERED: half-width shrinks from a wide, gutter-spilling foot
# to exactly PIPE_W/2 at the flat top, so every column in the 58 px collision
# band stays solid the whole height (the fill gate is trivially met by the
# solid mass) while the silhouette clearly leans inward. The roof seat is a
# FIXED small clearance below the rim so the flat parapet always sits within
# the 12 px fill budget of the rim and the gilt roofs overhang above it as the
# crown — this holds at h=70 and h=355 alike.

_BASE_HALF_K = 1.16               # foot half-width (spills into the eave gutter)
_TOP_HALF_K = 1.00                # flat-top half-width (== PIPE_W/2, fills band)
_CORE_FRAC = 0.66                 # red-core width as a fraction of wall width
_ROOF_SEAT = 10                   # full-width parapet clearance below the rim


def _lum(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


# ── Material triads (all palette-derived) ────────────────────────────────────

def _white_triad(palette):
    # Whitewashed Potrang Karpo. Lit LEFT (sun-side) -> cool plaster shadow
    # RIGHT so the battered face reads as a lime-washed volume, not flat card.
    base = _porcelain_white(palette)
    lit = _mix(base, (255, 253, 246), 0.5)
    mid = _mix(base, _plaster(palette), 0.5)
    sh = _mix(base, (150, 152, 168), 0.5)          # cool lime shadow
    lit = _cap_lit_for_dark_sky(lit, palette, cap=210)
    sh = _cap_dark_for_dark_sky(sh, palette, floor=64)
    return lit, mid, sh


def _red_triad(palette):
    # Potrang Marpo iron-oxide lacquer. Deep enough to stay clearly RED even
    # after the night retint pulls values together (AD value-separation note).
    base = _tibet_red(palette)
    lit = _mix(base, _vermilion(palette), 0.55)
    sh = _mix(base, (60, 20, 18), 0.5)
    lit = _cap_lit_for_dark_sky(lit, palette, cap=190)
    sh = _cap_dark_for_dark_sky(sh, palette, floor=48)
    return lit, base, sh


def _benma(palette):
    # The tamarisk-twig frieze band that caps Tibetan walls — dark maroon.
    # Built from the ochre band anchor pushed hard toward the iron-oxide red so
    # it reads as a maroon crown stripe, not gilt.
    return _mix(_tibet_ochre(palette), _tibet_red(palette), 0.62)


def _gold_deep(palette):
    return _mix(_gold_bright(palette), _bronze(palette), 0.55)


def _plinth_triad(palette):
    # The great rammed stone base the palace grows from — warm bronze-grey so
    # it grounds the whitewash instead of blurring into it.
    base = _bronze(palette)
    return _shade(base, 22), _shade(base, -8), _shade(base, -38)


# ── Batter profile ───────────────────────────────────────────────────────────

def _half_at(y, y_top, y_bot):
    """Wall half-width at row y — linear batter from the flat top (PIPE_W/2)
    to the wide foot, so the walls lean IN as they rise."""
    half = PIPE_W / 2
    t = (y - y_top) / max(1, y_bot - y_top)         # 0 top, 1 foot
    return (half * _TOP_HALF_K) + (half * (_BASE_HALF_K - _TOP_HALF_K)) * t


def _row(surf, y, xl, xr, lit, mid, sh):
    """One horizontal 3-stop wall row (sun-lit LEFT -> shadow RIGHT)."""
    w = xr - xl
    if w < 1:
        return
    for i in range(w + 1):
        t = i / w
        col = _mix(lit, mid, t * 2) if t < 0.5 else _mix(mid, sh, (t - 0.5) * 2)
        surf.set_at((xl + i, y), col)


# ── One trapezoid window (Tibetan black surround, wider at top) ──────────────

def _window(surf, cx, top_y, w, h, palette, *, lit):
    """Small recessed trapezoid window — the black surround flares WIDER at the
    top (the Tibetan tell). Quiet shadow by day; a warm lantern glow at night
    (and pre-warming at sunset) on the lit ones, so the massif becomes a
    lantern-strung fortress after dark."""
    if w < 4 or h < 5:
        return
    dark_sky = _is_dark_sky(palette)
    warming = _is_warming_sky(palette)
    tw, bw = w, max(2, int(w * 0.76))               # top wider than sill
    top_l = (cx - tw // 2, top_y)
    top_r = (cx + tw // 2, top_y)
    bot_r = (cx + bw // 2, top_y + h)
    bot_l = (cx - bw // 2, top_y + h)

    # White lintel over + ochre sill under — the painted window surround.
    lintel = _mix(_plaster(palette), (255, 255, 255), 0.3)
    pygame.draw.line(surf, lintel, (cx - tw // 2 - 1, top_y - 1),
                     (cx + tw // 2 + 1, top_y - 1), 1)
    pygame.draw.line(surf, _tibet_ochre(palette),
                     (cx - bw // 2, top_y + h), (cx + bw // 2, top_y + h), 1)

    frame = _shade(palette['stone_dark'], -22)
    inside = _shade(palette['stone_dark'], -50)
    if lit and (dark_sky or warming):
        rim = _mix(palette['stone_accent'], (255, 214, 120), 0.8)
        r_out = 7 if (dark_sky and not warming) else 3
        sz = r_out * 2 + 2
        glow = pygame.Surface((sz, sz), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*rim, 95), (sz // 2, sz // 2), r_out)
        pygame.draw.circle(glow, (*rim, 155), (sz // 2, sz // 2), max(1, r_out - 3))
        surf.blit(glow, (cx - sz // 2, top_y + h // 2 - sz // 2),
                  special_flags=pygame.BLEND_RGBA_ADD)
        inside = _mix(inside, rim, 0.6)
    pygame.draw.polygon(surf, frame, [top_l, top_r, bot_r, bot_l])
    pygame.draw.polygon(surf, inside,
                        [(top_l[0] + 1, top_l[1] + 1), (top_r[0] - 1, top_r[1] + 1),
                         (bot_r[0] - 1, bot_r[1] - 1), (bot_l[0] + 1, bot_l[1] - 1)])


def _window_rows(surf, cx, y0, y1, y_top, y_bot, palette, seed, *, cols):
    """March rows of windows down a wall zone [y0,y1], centring `cols` windows
    within the battered face at each row (inset from the leaning edge)."""
    zone_h = y1 - y0
    if zone_h < 12:
        return
    rowstep = 15
    rows = max(1, int(zone_h // rowstep))
    ww, wh = 6, 9
    for ri in range(rows):
        wy = int(y0 + (ri + 0.55) * (zone_h / rows)) - wh // 2
        hw = _half_at(wy + wh / 2, y_top, y_bot) * 0.78
        span = hw - ww
        n = cols if span > cols * (ww + 1) else max(1, cols - 1)
        for ci in range(n):
            fx = 0.0 if n == 1 else (ci / (n - 1) - 0.5) * 2
            wx = int(cx + fx * span)
            lit = ((ri * 7 + ci * 3 + seed) % 5) < 2
            _window(surf, wx, wy, ww, wh, palette, lit=lit)


# ── Maroon benma frieze band ─────────────────────────────────────────────────

def _frieze(surf, cx, y, hw, palette):
    """The dark-maroon benma band with a thin gilt lip — caps a wall storey."""
    band = _benma(palette)
    r = pygame.Rect(int(cx - hw), y, int(hw * 2) + 1, 4)
    _gradient_rect(surf, r, _shade(band, 18), band, _shade(band, -22))
    pygame.draw.line(surf, _gold_deep(palette),
                     (r.x, r.y), (r.right - 1, r.y), 1)
    # Row of tile-end nicks so the frieze reads as woven twig, not a bar.
    _tile_hatch(surf, r.x + 2, r.bottom - 1, r.right - 2, r.bottom - 1,
                _shade(band, -34), step=4)


# ── Gilt gyaphib roof ────────────────────────────────────────────────────────

def _gold_roof(surf, cx, base_y, w, h, palette):
    """A gabled Han-Tibetan gyaphib roof: gilt body, up-swept eave tips, a ridge
    highlight and a bell finial. At night an additive gold gleam + white
    specular so the crown glints; a quiet warm sheen by day."""
    dark_sky = _is_dark_sky(palette)
    gold = _gold_bright(palette)
    gd = _gold_deep(palette)
    ridge_y = base_y - h
    # Roof face — a low trapezoid, ridge narrower than the eave, with the eave
    # tips flaring OUT past the body corners (the upturned Tibetan sweep).
    body = [(cx - w, base_y), (cx - int(w * 0.55), ridge_y),
            (cx + int(w * 0.55), ridge_y), (cx + w, base_y)]
    # Vertical gilt gradient over the face.
    for i in range(h + 1):
        t = i / max(1, h)
        col = _mix(gold, gd, t)
        yy = ridge_y + i
        xw = w * (0.55 + 0.45 * t)
        pygame.draw.line(surf, col, (int(cx - xw), yy), (int(cx + xw), yy), 1)
    # Up-swept eave tips.
    for s in (-1, 1):
        tip = [(cx + s * w, base_y), (cx + s * (w + 3), base_y - 3),
               (cx + s * int(w * 0.7), base_y - 1)]
        pygame.draw.polygon(surf, gd, tip)
    # Ridge line + bright highlight + dark eave fringe.
    pygame.draw.line(surf, gd, (cx - int(w * 0.55), ridge_y),
                     (cx + int(w * 0.55), ridge_y), 1)
    pygame.draw.line(surf, _mix(gold, (255, 248, 210), 0.6),
                     (cx - int(w * 0.4), ridge_y + 1),
                     (cx + int(w * 0.4), ridge_y + 1), 1)
    pygame.draw.line(surf, _shade(gd, -30), (cx - w, base_y),
                     (cx + w, base_y), 1)
    _aa_polyline(surf, _shade(gd, -20), body)
    # Bell-shaped gyaltsen finial on the ridge.
    fr = max(1, h // 5)
    pygame.draw.circle(surf, gd, (cx, ridge_y - fr), fr + 1)
    pygame.draw.circle(surf, gold, (cx, ridge_y - fr), fr)
    pygame.draw.line(surf, gd, (cx, ridge_y - fr * 2), (cx, ridge_y - fr - 1), 1)
    if dark_sky:
        sz = w * 3
        glow = pygame.Surface((sz, sz), pygame.SRCALPHA)
        cgx = sz // 2
        pygame.draw.circle(glow, (255, 220, 130, 55), (cgx, cgx), sz // 2)
        pygame.draw.circle(glow, (255, 232, 170, 90), (cgx, cgx), sz // 3)
        surf.blit(glow, (cx - cgx, ridge_y - fr - cgx),
                  special_flags=pygame.BLEND_RGBA_ADD)
        surf.set_at((cx - int(w * 0.3), ridge_y + 2), (255, 250, 220))


# ── 3-layer plinth + foliage ─────────────────────────────────────────────────

def _draw_plinth(surf, cx, base_y, half, palette):
    lit, mid, sh = _plinth_triad(palette)
    layers = 3
    for i in range(layers):
        lw = int(half * 2 * (1.18 + 0.12 * i))
        lh = 5
        ly = base_y - (layers - i) * lh
        r = pygame.Rect(cx - lw // 2, ly, lw, lh)
        _gradient_rect(surf, r, lit, mid, sh)
        pygame.draw.line(surf, _shade(sh, -20),
                         (r.x, r.bottom - 1), (r.right - 1, r.bottom - 1), 1)
        pygame.draw.line(surf, _shade(lit, 16), (r.x, r.y), (r.right - 1, r.y), 1)


# ── One upright massif ───────────────────────────────────────────────────────

def _draw_massif(surf, cx, y_top, y_bot, palette, seed):
    """Battered white-below / red-above fortress: mist -> plinth -> whitewashed
    Potrang Karpo with window rows + benma -> red Potrang Marpo core in white
    wings with window rows + benma -> gilt gyaphib roof crown at the rim. The
    roof seat is a fixed clearance so the flat parapet always lands inside the
    fill budget; height-adaptive so short sections lead with the red palace."""
    half = PIPE_W // 2
    section_h = y_bot - y_top

    plinth_h = min(16, max(9, int(section_h * 0.13)))
    base_y = y_bot

    _draw_plinth_mist(surf, cx, base_y - plinth_h + 2, int(half * 2 * 1.9), palette)

    y_foot = base_y - plinth_h
    y_wall_top = y_top + _ROOF_SEAT

    # Height-adaptive split: short pillars lead with more red palace + roofs.
    red_frac = 0.42
    if section_h < 150:
        red_frac = min(0.72, 0.42 + (150 - section_h) * 0.0022)
    wall_h = y_foot - y_wall_top
    y_split = y_wall_top + int(wall_h * red_frac)

    white_lit, white_mid, white_sh = _white_triad(palette)
    red_lit, red_mid, red_sh = _red_triad(palette)

    # ── Wall body, row by row (battered edges + red-core-in-white-wings) ──
    left_pts, right_pts = [], []
    for y in range(y_wall_top, y_foot):
        hw = _half_at(y, y_wall_top, y_foot)
        xl = int(round(cx - hw))
        xr = int(round(cx + hw))
        if y < y_split:
            # Upper storey — white wings fill the full width, red core on top.
            _row(surf, y, xl, xr, white_lit, white_mid, white_sh)
            core = hw * _CORE_FRAC
            _row(surf, y, int(round(cx - core)), int(round(cx + core)),
                 red_lit, red_mid, red_sh)
        else:
            _row(surf, y, xl, xr, white_lit, white_mid, white_sh)
        left_pts.append((xl, y))
        right_pts.append((xr, y))

    # ── Window rows ──
    core_top_hw = _half_at(y_wall_top, y_wall_top, y_foot) * _CORE_FRAC
    _window_rows(surf, cx, y_wall_top + 6, y_split - 6, y_wall_top, y_foot,
                 palette, seed + 1, cols=2)             # red core windows
    _window_rows(surf, cx, y_split + 5, y_foot - 8, y_wall_top, y_foot,
                 palette, seed, cols=3)                 # white palace windows

    # ── Benma friezes: capping the white wall, and capping the red palace ──
    _frieze(surf, cx, y_split - 4, _half_at(y_split, y_wall_top, y_foot), palette)
    _frieze(surf, cx, y_wall_top + 1, core_top_hw + 1, palette)

    # ── Flat-roof parapet lip across the full top (the solid rim edge) ──
    top_hw = _half_at(y_wall_top, y_wall_top, y_foot)
    pygame.draw.line(surf, _shade(white_lit, 12),
                     (int(cx - top_hw), y_wall_top),
                     (int(cx + top_hw), y_wall_top), 1)

    # ── Gilt gyaphib roof crown — one large central + two flanking, overhang ──
    roof_base = y_wall_top
    big_h = min(18, max(11, int(section_h * 0.11)))
    _gold_roof(surf, cx, roof_base, min(15, int(core_top_hw * 0.62)), big_h, palette)
    if core_top_hw > 16:
        for s in (-1, 1):
            _gold_roof(surf, cx + s * int(core_top_hw * 0.62), roof_base,
                       max(6, int(core_top_hw * 0.30)), max(8, big_h - 5), palette)
    # Small gilt parapet banners on the white wing tops (also fills the rim).
    for s in (-1, 1):
        bx = cx + s * int(top_hw * 0.82)
        pygame.draw.line(surf, _gold_deep(palette), (bx, y_wall_top),
                         (bx, y_wall_top - 5), 1)
        pygame.draw.circle(surf, _gold_bright(palette), (bx, y_wall_top - 6), 1)

    # ── Silhouette keyline down the battered edges ──
    _aa_polyline(surf, _shade(white_sh, -22),
                 left_pts + list(reversed(right_pts)), closed=False)

    # ── Plinth + foliage ──
    _draw_plinth(surf, cx, base_y, half, palette)
    draw_grass_bed(surf, cx, base_y - 1, PIPE_W + 12, 12, palette, seed=seed)
    draw_side_shrub(surf, cx - half - 6, base_y - 1, palette, scale=0.9)
    draw_side_shrub(surf, cx + half + 6, base_y - 1, palette, scale=0.8)


def candidate_potala_fortress(surf, top_rect, bot_rect, palette, seed):
    """Bottom = the palace rising from the ground, gilt roofs at the gap. Top =
    the SAME massif vertical-FLIPPED from the ceiling.

    FLIP DECISION: kept as a clean vertical mirror — a stylised two-ended
    palace whose two gilt-roofed crowns MEET at the gap (like the shipped
    two-ended totems). The flip inverts the white-below/red-above axis on the
    hung twin, but because BOTH the white AND the red bands are bold and
    high-contrast in every section, the hung twin still reads unmistakably as a
    two-tone battered fortress with a gilt crown at the rim — the read survives
    the inversion rather than depending on which end is white."""
    if bot_rect.height > 0:
        _draw_massif(surf, bot_rect.centerx, bot_rect.y, bot_rect.bottom,
                     palette, seed)
    if top_rect.height > 0:
        # Extra headroom above the rim so the gilt crown's OVERHANG survives
        # the flip and spills into the gap (a bare tmp of exactly top_rect
        # height would clip the roofs flush at the rim).
        head = 18
        tmp = pygame.Surface((surf.get_width(), top_rect.height + head),
                             pygame.SRCALPHA)
        _draw_massif(tmp, top_rect.centerx, head, top_rect.height + head,
                     palette, seed + 1)
        surf.blit(pygame.transform.flip(tmp, False, True), (0, top_rect.y))


# ── review harness ───────────────────────────────────────────────────────────

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
    gap_y, gap_h = 172, 150
    top_h = int(gap_y - gap_h / 2)
    bot_top = int(gap_y + gap_h / 2)
    full = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    top_rect = pygame.Rect(MARGIN, 0, PIPE_W, top_h)
    bot_rect = pygame.Rect(MARGIN, bot_top, PIPE_W, GROUND_Y - bot_top)
    candidate_potala_fortress(full, top_rect, bot_rect, pal, seed=seed)

    tip_y = top_h - 10
    base_y = GROUND_Y + 8
    hero_h = base_y - tip_y
    hero = _bg(CACHE_W, hero_h, pal, hero_h - (base_y - GROUND_Y))
    hero.blit(full, (0, -tip_y))
    for ex in (MARGIN, MARGIN + PIPE_W):
        pygame.draw.line(hero, (230, 60, 60), (ex, 0), (ex, hero_h), 1)
    return hero, hero_h


def _closeup(pal, seed, scale=3):
    """Zoom on the upper massif so the two-tone split + windows + roofs check."""
    surf = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    br = pygame.Rect(MARGIN, GROUND_Y - 210, PIPE_W, 210)
    tr = pygame.Rect(MARGIN, 0, PIPE_W, 0)
    candidate_potala_fortress(surf, tr, br, pal, seed=seed)
    crop = pygame.Surface((CACHE_W, 130))
    crop.blit(_bg(CACHE_W, 130, pal, 130), (0, 0))
    crop.blit(surf, (0, -(GROUND_Y - 210)))
    return pygame.transform.scale(
        crop, (crop.get_width() * scale, crop.get_height() * scale))


def _blackout(pal, section_h, scale):
    surf = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    br = pygame.Rect(MARGIN, GROUND_Y - section_h, PIPE_W, section_h)
    tr = pygame.Rect(MARGIN, 0, PIPE_W, 0)
    candidate_potala_fortress(surf, tr, br, pal, seed=7)
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

    # ── Two-tone value-separation proof (AD note: red vs white must not
    #    converge at night). Report the lum gap in both phases.
    for label, pp in (("DAY", pal), ("NIGHT", pal_n)):
        _, wmid, _ = _white_triad(pp)
        _, rmid, _ = _red_triad(pp)
        gap = _lum(wmid) - _lum(rmid)
        red_dom = rmid[0] > rmid[1] and rmid[0] > rmid[2]
        print(f"TWO-TONE {label}: white-lum={_lum(wmid):.1f} red-lum={_lum(rmid):.1f} "
              f"gap={gap:.1f} [{'SPLITS' if gap > 45 else 'WEAK'}]  "
              f"red-dominant={red_dom}")

    # ── Fill gate at the three feasibility heights ──
    strip_heights = [70, 210, 355]
    strips = []
    print("FILL GATE (max empty vertical run inside the 58px PIPE_W band)")
    for h in strip_heights:
        s = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
        br = pygame.Rect(MARGIN, GROUND_Y - h, PIPE_W, h)
        tr = pygame.Rect(MARGIN, 0, PIPE_W, 0)
        candidate_potala_fortress(s, tr, br, pal, seed=7)
        run = _max_empty_run(s, MARGIN, MARGIN + PIPE_W, GROUND_Y - h, GROUND_Y)
        crop = pygame.Surface((CACHE_W, h + 8))
        crop.blit(_bg(CACHE_W, h + 8, pal, h), (0, 0))
        crop.blit(s, (0, -(GROUND_Y - h)))
        for ex in (MARGIN, MARGIN + PIPE_W):
            pygame.draw.line(crop, (230, 60, 60), (ex, 0), (ex, h + 8), 1)
        strips.append((h, crop, run))
        print(f"  h={h:3d}  max empty run = {run}px  [{'OK' if run <= 12 else 'FAIL'}]")

    # ── Mirror clearance (both crowns must reach the gap rim) ──
    gap_probe = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    gp_bot = pygame.Rect(MARGIN, 247, PIPE_W, GROUND_Y - 247)
    gp_top = pygame.Rect(MARGIN, 0, PIPE_W, 97)
    candidate_potala_fortress(gap_probe, gp_top, gp_bot, pal, seed=7)
    clear_bot = _gap_rim_clearance(gap_probe, MARGIN, MARGIN + PIPE_W, 247, up=True)
    clear_top = _gap_rim_clearance(gap_probe, MARGIN, MARGIN + PIPE_W, 96, up=True)
    print("MIRROR / GAP-RIM CLEARANCE (vertical-flip twin)")
    print(f"  bottom crown -> gap: {clear_bot}px   top crown -> gap: {clear_top}px")

    hero_day, hd_h = _hero(pal, 7)
    hero_night, hn_h = _hero(pal_n, 7)
    close_day = _closeup(pal, 7)
    close_night = _closeup(pal_n, 7)

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
    col_close = close_day.get_width()
    col_bo = max(bo3.get_width(), bo1.get_width()) + 20

    body_h = max(hd_h, hn_h, close_day.get_height() * 2 + label_h,
                 bo3.get_height() + 40) + label_h + 20
    sheet_w = pad + col_hero + pad + col_hero + pad + col_hero + pad + \
        col_close + pad + col_bo + pad
    sheet_h = head_h + body_h + pad * 2
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((24, 25, 30))

    sheet.blit(title.render(
        "potala_fortress — battered red-and-white massif  ·  round_1",
        True, (245, 240, 230)), (pad, 12))
    sheet.blit(sub.render(
        "red edges = PIPE_W (58px) collision band  ·  WHITE-below Potrang Karpo / "
        "RED-above Potrang Marpo, red core in white wings  ·  battered (inward-leaning) "
        "walls  ·  trapezoid window rows (lantern-lit at night)  ·  maroon benma frieze  ·  "
        "gilt gyaphib roof crown", True, (170, 172, 182)), (pad, 40))
    sheet.blit(sub.render(
        "avoids generic-trapezoid via the two-axis colour split + benma band + gilt roofs, "
        "not just a slope  ·  clean vertical-flip mirror (crowns meet at the gap)",
        True, (150, 210, 160)), (pad, 58))

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

    x += col_hero + pad
    sheet.blit(close_day, (x, head_h))
    pygame.draw.rect(sheet, (60, 62, 72),
                     (x, head_h, close_day.get_width(), close_day.get_height()), 1)
    sheet.blit(lab.render("UPPER-MASSIF 3x — DAY", True, (255, 224, 150)),
               (x, head_h + close_day.get_height() + 4))
    cy2 = head_h + close_day.get_height() + label_h
    sheet.blit(close_night, (x, cy2))
    pygame.draw.rect(sheet, (60, 62, 72),
                     (x, cy2, close_night.get_width(), close_night.get_height()), 1)
    sheet.blit(lab.render("UPPER-MASSIF 3x — NIGHT", True, (255, 224, 150)),
               (x, cy2 + close_night.get_height() + 4))

    x += col_close + pad
    sheet.blit(lab.render("BLACKOUT (massif test)", True, (255, 224, 150)),
               (x, head_h - 20))
    sheet.blit(bo3, (x, head_h))
    sheet.blit(lab.render("3x", True, (200, 200, 210)),
               (x, head_h + bo3.get_height() + 2))
    sheet.blit(bo1, (x + bo3.get_width() // 2 - bo1.get_width() // 2,
                     head_h + bo3.get_height() + 24))
    sheet.blit(lab.render("1x @ 58px", True, (200, 200, 210)),
               (x, head_h + bo3.get_height() + 24 + bo1.get_height() + 2))

    out = pathlib.Path(__file__).resolve().parent / "round_1.png"
    pygame.image.save(sheet, out)
    print(f"wrote {out}  ({sheet.get_width()}x{sheet.get_height()})")


if __name__ == "__main__":
    main()
