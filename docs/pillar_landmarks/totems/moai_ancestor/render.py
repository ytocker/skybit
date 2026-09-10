"""moai_ancestor — high-fidelity Easter-Island ancestor-head totem (candidate).

A GAUNT dark volcanic-basalt ancestor stack: tall near-straight heads with a
heavy shelf brow casting a hard shadow into deep-set sockets, a long angular
nose ridge (lit left plane, shadowed right plane), a firm lip shelf and a
jutting chin, crowned by a fixed-red scoria PUKAO drum at the gap rim.

Ground-up rebuild of the crude shipped `moai-monolith`. The make-or-break is
that the blackout reads GAUNT (a tall, angular, heavy-browed vertical with a
wide red drum on top) and NOT the bulbous knobbly ovoid stack we already ship.
That is enforced by construction: heads are near-full-width straight columns
(fills the 58 px collision band, so the silhouette is a smooth vertical, never
lobed) with only shallow neck waists as the moai jaw-notch tell.

This is a standalone review candidate. It imports the REAL pagoda helpers so
its materials and lighting match the shipped pillars exactly (dark _basalt
triple for the body, _lit_niche sockets for the free night-glow "living eye",
_draw_plinth_mist + foliage for the base), but it does not wire anything into
the live game.

Run:  python docs/pillar_landmarks/totems/moai_ancestor/render.py
Out:  docs/pillar_landmarks/totems/moai_ancestor/round_2.png
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
    _mix, _shade, _gradient_rect, _aa_polyline, _lit_niche,
    _draw_plinth_mist, _is_dark_sky, _is_warming_sky,
    _cap_lit_for_dark_sky, _cap_dark_for_dark_sky,
    _basalt, _basalt_lit, _basalt_shadow, _buddha_eye, _bronze,
)
from game.pillar_variants import draw_grass_bed
from game.draw import draw_side_shrub


MARGIN = 64                       # matches entities.Pipe eave/ornament gutter
CACHE_W = PIPE_W + MARGIN * 2
CACHE_H = GROUND_Y
PHASE_DAY = 0.30                  # midday tan sky — hardest test for "reads dark"
PHASE_NIGHT = 0.85               # deep night — checks lit rim + socket glow + red drum


# ── Materials ────────────────────────────────────────────────────────────────
#
# The headline fix vs the old flat moai: the body is the REAL Borobudur _basalt
# triple pushed a stop DARKER and nudged toward neutral cool grey, so the
# ancestor reads as dark volcanic tuff instead of the warm mid-sandstone the raw
# triple lands on under the tan day palette. Still fully palette-derived, so the
# 5-min biome day->night retint sweeps straight through it.

def _cool_dark(c):
    return _mix(_shade(c, -34), (84, 90, 100), 0.42)


def _body_triad(palette):
    lit = _cool_dark(_basalt_lit(palette))
    mid = _cool_dark(_basalt(palette))
    sh = _cool_dark(_basalt_shadow(palette))
    # At night, floor the shadow so the dark basalt doesn't sink into the sky as
    # one black mass, and cap the lit so the raking highlight doesn't blow out.
    lit = _cap_lit_for_dark_sky(lit, palette, cap=176)
    sh = _cap_dark_for_dark_sky(sh, palette, floor=44)
    return lit, mid, sh


def _scoria(palette):
    # The ONE deliberately non-palette hue: a fixed volcanic-scoria red for the
    # pukao. Mixed only <=0.10 toward the horizon so the biome nudges it warm at
    # dawn/dusk but it stays unambiguously RED in every phase (the shipped moai's
    # round-1 bug was a horizon-mixed crown melting into the tan sky by day).
    #
    # The base is a BRIGHT terracotta-scoria, not a deep oxblood: the pukao is
    # the crowning focal + the only warm accent, and it has to clear the dark
    # basalt body by VALUE (a deep red sat nearly isoluminant on the basalt, so
    # the crown barely separated). G/R 0.45, B/R 0.30 keeps it firmly RED, never
    # orange/pink, while its luminance rides ~30 above the body mid in every
    # biome phase so the crown reads by value alone.
    return _mix((205, 92, 62), palette['horizon'], 0.10)


def _lum(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


# ── Head geometry ──────────────────────────────────────────────────────────
#
# GAUNT by construction. The head is a tall near-full-width straight column so
# the 58 px collision band is always solid (smooth vertical silhouette, never a
# bulbous lobe). The only silhouette break is a shallow neck WAIST at each
# stacked seam — the moai jaw-notch tell — kept short enough that no outer-column
# empty run ever approaches the 12 px ceiling. Gauntness is carried by the tall
# aspect + the deep carved relief + the pukao, not by a fat taper.

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


# ── One ancestor head ──────────────────────────────────────────────────────

def _draw_head(surf, cx, y0, y1, half, palette, rng, *, crown, base):
    hh = y1 - y0
    lit, mid, sh = _body_triad(palette)
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

    # ── Deep carved relief ───────────────────────────────────────────────
    # Brow pushed up + chin dropped + eyes drawn in tighter so the face region
    # reads ELONGATED (moai gaunt), not a blocky centred cluster.
    brow_y = y0 + int(hh * 0.20)
    brow_h = max(3, int(hh * 0.10))
    eye_y = brow_y + brow_h - 1
    eye_h = max(4, int(hh * 0.13))
    eye_dx = int(half * 0.40)
    eye_w = max(4, int(half * 0.34))
    nose_top = brow_y + brow_h
    nose_bot = y0 + int(hh * 0.72)
    nose_hw = max(2, int(half * 0.26))
    lip_y = y0 + int(hh * 0.78)
    lip_hw = int(half * 0.34)
    chin_y = y0 + int(hh * 0.90)

    brow_dark = _shade(mid, -46)
    brow_lit = _shade(lit, 22)
    ridge_lit = _shade(lit, 34)
    plane_sh = _shade(sh, -30)

    if not thumbnail:
        # 1. Heavy shelf brow — a filled polygon that stands PROUD (lit top edge)
        #    and drops a hard shadow band beneath it into the sockets.
        bl = cx - int(half * 0.80)
        br = cx + int(half * 0.80)
        brow_poly = [(bl, brow_y + brow_h), (bl + 2, brow_y),
                     (cx, brow_y - 1), (br - 2, brow_y),
                     (br, brow_y + brow_h)]
        pygame.draw.polygon(surf, _shade(mid, 8), brow_poly)
        # Lit crest across the top of the shelf.
        _aa_polyline(surf, brow_lit,
                     [(bl + 2, brow_y), (cx, brow_y - 1), (br - 2, brow_y)])
        # Hard cast shadow under the shelf (the recess the sockets sit in).
        pygame.draw.rect(surf, brow_dark, (bl + 2, brow_y + brow_h, br - bl - 4, 2))

    # 2. Deep-set eye sockets — _lit_niche gives socket dark + rim + the free
    #    night-lantern glow (the ancestral "living eye").
    _lit_niche(surf, cx - eye_dx, eye_y, eye_w, eye_h, palette)
    _lit_niche(surf, cx + eye_dx, eye_y, eye_w, eye_h, palette)

    if not thumbnail:
        # 3. Long angular nose wedge — lit LEFT plane, shadow RIGHT plane, meeting
        #    at a bright center ridge (the signature moai nose-ridge).
        left_plane = [(cx, nose_top), (cx - nose_hw, nose_bot), (cx + 1, nose_bot)]
        right_plane = [(cx, nose_top), (cx + nose_hw, nose_bot), (cx - 1, nose_bot)]
        pygame.draw.polygon(surf, plane_sh, right_plane)
        pygame.draw.polygon(surf, _shade(lit, 16), left_plane)
        _aa_polyline(surf, ridge_lit, [(cx, nose_top), (cx, nose_bot)])
        # Nostril shadow flare at the wide base of the wedge.
        pygame.draw.line(surf, brow_dark,
                         (cx - nose_hw + 1, nose_bot), (cx - 1, nose_bot), 1)
        pygame.draw.line(surf, brow_dark,
                         (cx + 1, nose_bot), (cx + nose_hw - 1, nose_bot), 1)

        # 4. Firm lip shelf — a protruding bar, lit top edge, shadow undercut,
        #    with a dark set mouth line.
        pygame.draw.rect(surf, _shade(mid, -14),
                         (cx - lip_hw, lip_y, lip_hw * 2, 3))
        pygame.draw.line(surf, _shade(lit, 20),
                         (cx - lip_hw + 1, lip_y), (cx + lip_hw - 1, lip_y), 1)
        pygame.draw.line(surf, brow_dark,
                         (cx - lip_hw + 2, lip_y + 1), (cx + lip_hw - 2, lip_y + 1), 1)
        pygame.draw.rect(surf, plane_sh, (cx - lip_hw, lip_y + 3, lip_hw * 2, 1))

        # 5. Jutting-chin undercut — a shadow band that reads the heavy jaw.
        pygame.draw.rect(surf, _shade(sh, -18),
                         (cx - int(half * 0.5), chin_y, int(half), 2))

        # 6. Pitted-tuff texture — sparse stipple + a couple of faint striations,
        #    kept off the sockets so the face relief stays clean.
        for _ in range(max(4, hh // 7)):
            px = rng.randint(cx - half + 3, cx + half - 3)
            py = rng.randint(y0 + 2, y1 - 3)
            if abs(py - eye_y) < eye_h and abs(abs(px - cx) - eye_dx) < eye_w:
                continue
            c = brow_dark if rng.random() < 0.6 else _shade(lit, 14)
            surf.set_at((px, py), c)
        for k in range(2):
            sy = y0 + int(hh * (0.5 + 0.16 * k))
            sx0 = cx - int(half * 0.6)
            pygame.draw.line(surf, _shade(mid, -10),
                             (sx0, sy), (sx0 + int(half * 0.5), sy), 1)
    else:
        # Thumbnail relief: guarantee the ancestor reads on brow-shadow + 2
        # socket pits + a short nose ridge alone at ~40 px face height.
        bl = cx - int(half * 0.72)
        br = cx + int(half * 0.72)
        pygame.draw.line(surf, brow_dark, (bl, brow_y + 1), (br, brow_y + 1), 2)
        _aa_polyline(surf, ridge_lit, [(cx, nose_top), (cx, nose_bot)])
        pygame.draw.line(surf, brow_dark,
                         (cx - lip_hw + 1, lip_y), (cx + lip_hw - 1, lip_y), 1)

    # 7. AA silhouette keyline — fixes the old 1-px un-AA'd lobe edges.
    outline = left_pts + list(reversed(right_pts))
    _aa_polyline(surf, _shade(sh, -22), outline, closed=True)

    # 8. Night rim-light down the LEFT edge so the dark basalt holds its
    #    silhouette against a dark sky (a quiet cool edge by day).
    rim = _shade(lit, 46) if dark_sky else _shade(lit, 18)
    step = 1 if dark_sky else 2
    for i in range(0, len(left_pts), step):
        x, y = left_pts[i]
        surf.set_at((x, y), rim)
        if dark_sky and x + 1 < cx:
            surf.set_at((x + 1, y), _mix(rim, mid, 0.5))


# ── Pukao (red scoria topknot) ─────────────────────────────────────────────

def _draw_pukao(surf, cx, y_top, y_bot, half, palette):
    """Fixed-red scoria drum crowning the stack. Sits at the gap rim and
    presents a solid WIDE flat edge there (the tower reaches the gap line with
    the red drum). Near-vertically symmetric so the ceiling flip reads clean."""
    red = _scoria(palette)
    red_lit = _shade(red, 34)
    red_sh = _shade(red, -40)
    # ~1.2x the crown so the blackout reads "gaunt post + distinct wide cap-drum"
    # (the moai tell) instead of a plain menhir bar. The overhang stays inside
    # the eave/ornament MARGIN gutter, so it never widens the collision band.
    pw = int(half * 2 * 1.20)
    dh = y_bot - y_top
    x0 = cx - pw // 2
    # Cylindrical body with a left-lit horizontal gradient.
    for x in range(pw):
        t = x / max(1, pw - 1)
        col = _mix(red_lit, red, t * 2) if t < 0.5 else _mix(red, red_sh, (t - 0.5) * 2)
        pygame.draw.line(surf, col, (x0 + x, y_top + 2), (x0 + x, y_bot), 1)
    # Slightly domed, wide top edge = the solid gap-rim presentation.
    top_rect = pygame.Rect(x0, y_top, pw, 5)
    pygame.draw.ellipse(surf, red, top_rect)
    pygame.draw.ellipse(surf, red_lit, top_rect.inflate(-2, -2))
    # A darker seam where the drum meets the crown.
    pygame.draw.line(surf, red_sh, (x0 + 1, y_bot), (x0 + pw - 2, y_bot), 1)
    # A shadowed neck band on the crown head just beneath the drum: the drum is
    # drawn over the head, so darkening the rows under the seam sinks the neck
    # and makes the bright scoria cap pop as a crown on a darker post.
    _, mid_b, sh_b = _body_triad(palette)
    neck_dark = _shade(sh_b, -16)
    nb_hw = int(half * 0.92)
    for k in range(3):
        t = 1.0 - k / 3.0
        pygame.draw.line(surf, _mix(mid_b, neck_dark, t),
                         (cx - nb_hw, y_bot + 1 + k), (cx + nb_hw, y_bot + 1 + k), 1)
    # Pitted scoria texture on the drum face.
    rng = random.Random(cx * 7 + y_top)
    for _ in range(max(3, pw // 4)):
        px = rng.randint(x0 + 2, x0 + pw - 3)
        py = rng.randint(y_top + 3, y_bot - 1)
        surf.set_at((px, py), red_sh if rng.random() < 0.6 else red_lit)
    _aa_polyline(surf, red_sh,
                 [(x0, y_bot), (x0, y_top + 3), (x0 + pw - 1, y_top + 3),
                  (x0 + pw - 1, y_bot)])


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
    """One upright ancestor tower: mist -> plinth -> foliage -> adaptive head
    stack -> pukao at the gap rim. Height-adaptive head COUNT keeps every head
    un-squashed (1 gaunt head at ~70 px, several at 355)."""
    rng = random.Random(seed)
    half = PIPE_W // 2
    section_h = y_bot - y_top

    plinth_h = min(15, max(9, int(section_h * 0.14)))
    pukao_h = min(18, max(10, int(section_h * 0.16)))
    # A very short section has budget for only ONE head, so the plinth+pukao tax
    # squats it (W/H drifts blocky). Shave a couple px off both at short sections
    # to hand that height back to the lone head and keep it gaunt.
    if section_h < 100:
        plinth_h = max(7, plinth_h - 2)
        pukao_h = max(9, pukao_h - 2)
    base_y = y_bot

    # Atmospheric backlight wedge behind the plinth.
    _draw_plinth_mist(surf, cx, base_y - plinth_h + 2, int(half * 2 * 1.6), palette)

    stack_bot = base_y - plinth_h
    stack_top = y_top + pukao_h
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

    # Pukao crowns the top head and reaches the gap rim.
    _draw_pukao(surf, cx, y_top, stack_top, half, palette)

    # Plinth + foliage last so they sit on top of the head base.
    _draw_plinth(surf, cx, base_y, half, palette, seed)
    draw_grass_bed(surf, cx, base_y - 1, PIPE_W + 12, 12, palette, seed=seed)
    draw_side_shrub(surf, cx - half - 6, base_y - 1, palette, scale=0.9)
    draw_side_shrub(surf, cx + half + 6, base_y - 1, palette, scale=0.8)


def candidate_moai_ancestor(surf, top_rect, bot_rect, palette, seed):
    """Bottom = ancestor tower rising from the ground, pukao at the gap. Top =
    the same tower vertical-FLIPPED from the ceiling — a symmetric two-ended
    totem, its pukao pointing into the gap so both drums meet at the rim."""
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
    """Rows of empty sky between the gap line and the first opaque pixel of the
    tower — how close the pukao reaches the flyable gap edge."""
    step = -1 if up else 1
    for d in range(0, 200):
        y = gap_y + step * d
        if y < 0 or y >= surf.get_height():
            return d
        if any(surf.get_at((x, y))[3] > 0 for x in range(x0, x1)):
            return d
    return 200


def _pukao_measure(pal, seed=7):
    """Pixel-measured pukao value + width, isolated to the pukao BAND at the top
    of the tower so warm non-pukao pixels (plinth mist by day, amber socket halos
    by night) can't contaminate the reading. Body mid is the deterministic
    _body_triad mid (the value the crown must clear), matching how the body is
    specced. Returns (drum mean lum, body mid lum, dL, drum px width, crown px)."""
    section_h = 355
    surf = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    br = pygame.Rect(MARGIN, GROUND_Y - section_h, PIPE_W, section_h)
    tr = pygame.Rect(MARGIN, 0, PIPE_W, 0)
    candidate_moai_ancestor(surf, tr, br, pal, seed=seed)

    # Same budget as _draw_tower -> the drum occupies [y_top+2 .. y_top+pukao_h].
    y_top = GROUND_Y - section_h
    pukao_h = min(18, max(10, int(section_h * 0.16)))
    band_top, band_bot = y_top, y_top + pukao_h + 2

    drum = []
    drum_min_x, drum_max_x = 10 ** 9, -1
    for x in range(CACHE_W):
        for y in range(band_top, band_bot):
            r, g, b, a = surf.get_at((x, y))
            if a == 0 or not (r - g > 28 and r > 120):   # bright scoria red only
                continue
            drum.append(_lum((r, g, b)))
            drum_min_x = min(drum_min_x, x)
            drum_max_x = max(drum_max_x, x)
    drum_lum = sum(drum) / max(1, len(drum))
    body_lum = _lum(_body_triad(pal)[1])
    drum_w = (drum_max_x - drum_min_x + 1) if drum_max_x >= 0 else 0
    return drum_lum, body_lum, drum_lum - body_lum, drum_w, PIPE_W


def _hero(pal, seed):
    gap_y, gap_h = 168, 150
    top_h = int(gap_y - gap_h / 2)
    bot_top = int(gap_y + gap_h / 2)
    full = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    top_rect = pygame.Rect(MARGIN, 0, PIPE_W, top_h)
    bot_rect = pygame.Rect(MARGIN, bot_top, PIPE_W, GROUND_Y - bot_top)
    candidate_moai_ancestor(full, top_rect, bot_rect, pal, seed=seed)

    tip_y = top_h - 6
    base_y = GROUND_Y + 8
    hero_h = base_y - tip_y
    hero = _bg(CACHE_W, hero_h, pal, hero_h - (base_y - GROUND_Y))
    hero.blit(full, (0, -tip_y))
    for ex in (MARGIN, MARGIN + PIPE_W):
        pygame.draw.line(hero, (230, 60, 60), (ex, 0), (ex, hero_h), 1)
    return hero, hero_h


def _closeup(pal, seed, scale=3):
    """Zoom on a single ground head so the carved relief depth is checkable."""
    surf = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    br = pygame.Rect(MARGIN, GROUND_Y - 150, PIPE_W, 150)
    tr = pygame.Rect(MARGIN, 0, PIPE_W, 0)
    candidate_moai_ancestor(surf, tr, br, pal, seed=seed)
    crop = pygame.Surface((CACHE_W, 120))
    crop.blit(_bg(CACHE_W, 120, pal, 120), (0, 0))
    crop.blit(surf, (0, -(GROUND_Y - 150)))
    return pygame.transform.scale(
        crop, (crop.get_width() * scale, crop.get_height() * scale))


def _blackout(pal, section_h, scale):
    """Solid-black silhouette of a hero section — the gaunt-vs-bulbous test."""
    surf = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    br = pygame.Rect(MARGIN, GROUND_Y - section_h, PIPE_W, section_h)
    tr = pygame.Rect(MARGIN, 0, PIPE_W, 0)
    candidate_moai_ancestor(surf, tr, br, pal, seed=7)
    # Crop wide enough to capture the pukao overhang (~1.2x PIPE_W) so the wide
    # cap-drum shows in the blackout, not just the 58px collision post.
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

    # Body-hue proof: must read DARK + near-neutral (not tan) and DAY != NIGHT.
    _, mid_d, _ = _body_triad(pal)
    _, mid_n, _ = _body_triad(pal_n)
    print("BODY BASALT (mid tone)")
    print(f"  DAY   mid={mid_d} lum={_lum(mid_d):.1f}  R-B={mid_d[0]-mid_d[2]}")
    print(f"  NIGHT mid={mid_n} lum={_lum(mid_n):.1f}  R-B={mid_n[0]-mid_n[2]}")
    print(f"  day != night: {mid_d != mid_n}")
    sc_d, sc_n = _scoria(pal), _scoria(pal_n)
    print(f"  SCORIA day={sc_d} night={sc_n}  (R dominant both: "
          f"{sc_d[0] > sc_d[1] and sc_n[0] > sc_n[1]})")

    # Pukao value-contrast + width proof — the round_2 make-or-break.
    dd, bd, dl_d, drum_w, crown_w = _pukao_measure(pal)
    dn, bn, dl_n, _, _ = _pukao_measure(pal_n)
    print("PUKAO vs BODY value contrast (target dL >= +25)")
    print(f"  DAY   drum lum={dd:.1f}  body lum={bd:.1f}  dL=+{dl_d:.1f}  "
          f"[{'OK' if dl_d >= 25 else 'FAIL'}]")
    print(f"  NIGHT drum lum={dn:.1f}  body lum={bn:.1f}  dL=+{dl_n:.1f}  "
          f"[{'OK' if dl_n >= 25 else 'FAIL'}]")
    ratio = drum_w / crown_w
    print(f"PUKAO/CROWN width: drum={drum_w}px crown={crown_w}px  ratio={ratio:.2f}  "
          f"[{'OK' if 1.15 <= ratio <= 1.25 else 'FAIL'}]")

    hero_day, hd_h = _hero(pal, 7)
    hero_night, hn_h = _hero(pal_n, 7)
    close = _closeup(pal, 7)

    # Gap-rim clearance (bottom tower pukao reaching the gap line).
    gap_probe = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    gp_bot = pygame.Rect(MARGIN, 243, PIPE_W, GROUND_Y - 243)
    gp_top = pygame.Rect(MARGIN, 0, PIPE_W, 93)
    candidate_moai_ancestor(gap_probe, gp_top, gp_bot, pal, seed=7)
    clear_bot = _gap_rim_clearance(gap_probe, MARGIN, MARGIN + PIPE_W, 243, up=True)
    clear_top = _gap_rim_clearance(gap_probe, MARGIN, MARGIN + PIPE_W, 93, up=True)
    print("GAP-RIM CLEARANCE")
    print(f"  bottom pukao -> gap: {clear_bot}px   top pukao -> gap: {clear_top}px")

    # Feasibility strip: bottom section at three heights + empty-run gate.
    strip_heights = [70, 210, 355]
    strips = []
    print("FILL GATE (max empty vertical run inside the 58px PIPE_W band)")
    for h in strip_heights:
        s = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
        br = pygame.Rect(MARGIN, GROUND_Y - h, PIPE_W, h)
        tr = pygame.Rect(MARGIN, 0, PIPE_W, 0)
        candidate_moai_ancestor(s, tr, br, pal, seed=7)
        run = _max_empty_run(s, MARGIN, MARGIN + PIPE_W, GROUND_Y - h, GROUND_Y)
        crop = pygame.Surface((CACHE_W, h + 8))
        crop.blit(_bg(CACHE_W, h + 8, pal, h), (0, 0))
        crop.blit(s, (0, -(GROUND_Y - h)))
        for ex in (MARGIN, MARGIN + PIPE_W):
            pygame.draw.line(crop, (230, 60, 60), (ex, 0), (ex, h + 8), 1)
        strips.append((h, crop, run))
        print(f"  h={h:3d}  max empty run = {run}px  [{'OK' if run <= 12 else 'FAIL'}]")

    # Blackout thumbnails: gaunt-read test at native 58px, shown 1x + 3x.
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
    sheet.fill((24, 25, 30))

    sheet.blit(title.render(
        "moai_ancestor — gaunt dark-basalt ancestor totem  ·  round_2",
        True, (245, 240, 230)), (pad, 12))
    sheet.blit(sub.render(
        "red edges = PIPE_W (58px) collision band  ·  dark _basalt body  ·  "
        "shelf-brow + deep-socket + nose-ridge relief  ·  BRIGHT scoria pukao  ·  "
        "symmetric ceiling flip", True, (170, 172, 182)), (pad, 40))
    sheet.blit(sub.render(
        f"FIX: pukao dL day +{dl_d:.0f} / night +{dl_n:.0f} (>=+25)  ·  "
        f"cap-drum {drum_w}px vs {crown_w}px crown = {ratio:.2f}x (1.15-1.25)  ·  "
        "darker neck band under drum", True, (150, 210, 160)), (pad, 56))

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

    # face close-up
    x += col_hero + pad
    sheet.blit(close, (x, head_h))
    pygame.draw.rect(sheet, (60, 62, 72),
                     (x, head_h, close.get_width(), close.get_height()), 1)
    sheet.blit(lab.render("FACE CLOSE-UP 3x — carved relief", True,
                          (255, 224, 150)), (x, head_h + close.get_height() + 4))

    # blackout thumbnails
    x += col_close + pad
    sheet.blit(lab.render("BLACKOUT (gaunt test)", True, (255, 224, 150)),
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
