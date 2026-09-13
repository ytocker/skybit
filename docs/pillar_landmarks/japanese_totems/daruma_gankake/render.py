"""daruma_gankake — high-fidelity stacked Daruma wish-doll totem (candidate).

The ROUND, non-mask pole of the Japanese-totem family: a beaded column of
squat lacquer-red Daruma dolls, each a glossy convex ovoid with a broad cream
face patch, bold gold-rimmed eyes (one filled per the gankake wish tradition,
one left blank), gold calligraphic crane-brows + turtle-moustache, and a gold
fortune medallion on the belly. A low gold crown-knot caps the stack at the
gap rim.

Seeded on the winner `moai_ancestor`: it REUSES that module's stacked-unit
column skeleton — the height-adaptive unit COUNT, the per-seam waist, the
plinth + foliage base, the vertical-FLIP mirror and the whole review harness
(fill gate, gap-rim clearance, blackout). The make-or-break difference is the
per-unit half-width profile: where moai holds a GAUNT near-straight column,
each Daruma BULGES into the gutters as a round bead with only a shallow waist
pinch between dolls. The round blackout is the whole identity — the counter-
point to the four angular masks — and it is enforced by construction (a wide
sinusoidal belly bulge, never a straight post), read via the flat gold face +
brows, not a carved profile, so it can never be mistaken for the gaunt moai.

Materials are all palette-derived (so the 5-min biome day->night retint sweeps
straight through) with fixed archetype biases, exactly as moai does its
scoria: lacquer-red body triad, cream _plaster face, _gold_bright/_gold_deep
trim, _bronze plinth.

This is a standalone review candidate; it wires nothing into the live game.

Run:  python docs/pillar_landmarks/japanese_totems/daruma_gankake/render.py
Out:  docs/pillar_landmarks/japanese_totems/daruma_gankake/round_1.png
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
# Japanese pillars, so the Daruma lacquer + gilt read exactly on-palette.
from game.pillar_pagodas import (
    _mix, _shade, _gradient_rect, _aa_polyline, _lit_niche,
    _draw_plinth_mist, _is_dark_sky,
    _cap_lit_for_dark_sky, _cap_dark_for_dark_sky,
    _lacquer_red, _vermilion, _gold_bright, _gold_deep, _bronze, _plaster,
)
from game.pillar_variants import draw_grass_bed
from game.draw import draw_side_shrub


MARGIN = 64                       # matches entities.Pipe eave/ornament gutter
CACHE_W = PIPE_W + MARGIN * 2
CACHE_H = GROUND_Y
PHASE_DAY = 0.30                  # midday sky — hardest test for the red holding
PHASE_NIGHT = 0.85               # deep night — checks gold rims + lit eye + rim


# ── Materials ────────────────────────────────────────────────────────────────
#
# The body is the shipped _lacquer_red cinnabar pushed into a glossy convex
# triad: a warm specular highlight on the lit LEFT side, the lacquer mid, and a
# deep oxblood shadow on the RIGHT — the papier-mâché gloss that reads as a
# rounded doll rather than a flat red bead. Distinct from Oni's bright vermilion
# because the identity leans on the CREAM face patch + GOLD medallion (red+gold
# doll), not on the hue alone. Everything palette-derived so the biome retint
# sweeps through; the raw-RGB anchors are fixed archetype biases only, matching
# how moai fixes its scoria.

def _body_triad(palette):
    base = _lacquer_red(palette)
    lit = _mix(base, (255, 170, 112), 0.44)      # glossy warm specular side
    sh = _mix(base, (54, 12, 16), 0.55)          # deep oxblood shadow side
    # At night, floor the shadow so the dark lacquer doesn't sink into the sky
    # as one mass, and cap the specular so the gloss doesn't blow out.
    lit = _cap_lit_for_dark_sky(lit, palette, cap=205)
    sh = _cap_dark_for_dark_sky(sh, palette, floor=46)
    return lit, base, sh


def _cream(palette):
    return _plaster(palette)


def _ink(palette):
    # The gankake wish-eye is painted BLACK ink, not lacquer — crush the warm
    # stone_dark toward near-black so the filled pupil floors well below lum 40
    # and can never be confused with the red body (which shares stone_dark's
    # ~78 lum). A trace of the palette hue survives so the biome retint still
    # sweeps the pupil from cool-night to warm-day black.
    return _mix(palette['stone_dark'], (10, 8, 12), 0.85)


def _plinth_triad(palette):
    # Dark lacquer-and-bronze stand — grounds the bright red doll instead of
    # blurring into it, and reads as the wooden/lacquer base a Daruma sits on.
    base = _bronze(palette)
    return _shade(base, 24), _shade(base, -6), _shade(base, -36)


def _lum(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


# ── Doll geometry ───────────────────────────────────────────────────────────
#
# ROUND by construction — the inverse of moai's gaunt straight column. Each
# doll's half-width follows a sinusoidal BELLY BULGE that swells past PIPE_W/2
# well into the gutter margin (the round tell), pinching only to a shallow
# WAIST at each stacked seam. The waist floor is held just ABOVE PIPE_W/2 so
# the 58 px collision band is solid at EVERY row (the belly overspill lives in
# the eave gutter and never widens the band). The belly peak sits a touch below
# centre for the weighted roly-poly Daruma silhouette.

_BELLY_K = 1.46                   # belly half-width as a multiple of PIPE_W/2
_WAIST_K = 1.05                   # seam-waist half-width (>1 => band always full)
_BELLY_T = 0.58                   # normalized belly-peak position (0 top, 1 bot)
_DOLL_H_FLOOR = 88                # natural doll height -> drives adaptive COUNT


def _hw_at(t):
    """Half-width of the doll silhouette at normalized row t in [0,1] (0 = top
    dome, 1 = bottom foot). A smooth sinusoidal ovoid: pinched to the waist at
    both seams, bulging to the belly just below centre."""
    half = PIPE_W / 2
    waist = half * _WAIST_K
    belly = half * _BELLY_K
    p = _BELLY_T
    if t <= p:
        b = math.sin(0.5 * math.pi * (t / p)) if p > 0 else 1.0
    else:
        b = math.sin(0.5 * math.pi * (1.0 + (t - p) / (1.0 - p)))
    return waist + (belly - waist) * b


def _grad_row(surf, y, xl, xr, lit, mid, sh, vfac):
    """One row of the doll body: a horizontal 3-stop gradient (lit LEFT ->
    shadow RIGHT) darkened by `vfac` toward the top/bottom of the sphere so the
    ovoid reads as a shaded convex volume, not a flat lozenge."""
    w = xr - xl
    if w < 1:
        return
    for i in range(w + 1):
        t = i / w
        col = _mix(lit, mid, t * 2) if t < 0.5 else _mix(mid, sh, (t - 0.5) * 2)
        if vfac:
            col = _mix(col, sh, vfac)
        surf.set_at((xl + i, y), col)


def _gleam(surf, cx, cy, rw, rh, palette):
    """Additive papier-mâché gloss highlight on the upper-left of a doll — the
    single specular that sells the lacquer as glossy and convex."""
    if rw < 3 or rh < 2:
        return
    hi = _mix(palette['stone_light'], (255, 224, 186), 0.6)
    g = pygame.Surface((rw * 2 + 2, rh * 2 + 2), pygame.SRCALPHA)
    for ring, a in ((1.0, 22), (0.62, 40), (0.32, 72)):
        rr = pygame.Rect(rw - int(rw * ring), rh - int(rh * ring),
                         int(rw * 2 * ring) + 1, int(rh * 2 * ring) + 1)
        pygame.draw.ellipse(g, (*hi, a), rr)
    surf.blit(g, (cx - rw, cy - rh), special_flags=pygame.BLEND_RGBA_ADD)


# ── One Daruma eye ──────────────────────────────────────────────────────────

def _draw_eye(surf, cx, cy, r, palette, *, filled, thumb):
    """A big Daruma eye: a BOLD gold rim ring holding either a dark filled pupil
    (the gankake 'wish made' eye) or a blank cream disc (the un-filled eye).
    The gold rim is deliberately fat (>=2 px) so both discs survive the 58 px
    collision scale where a thin ring would vanish."""
    gold = _gold_bright(palette)
    gold_d = _gold_deep(palette)
    ink = _ink(palette)
    cream = _cream(palette)
    rim = max(2, r // 3)
    # Bold gold rim: a deep-gold seat under a bright-gold face reads as a raised
    # metal ring rather than a printed circle. These two eye-RIMS are the only
    # BRIGHT gold on the face (brows/moustache/patch-rim are demoted to deep
    # gold) so the eyes win the focal hierarchy.
    pygame.draw.circle(surf, gold_d, (cx, cy), r + 1)
    pygame.draw.circle(surf, gold, (cx, cy), r)
    inner = max(1, r - rim)
    if filled:
        # Filled pupil = a bold near-black INK disc — the gankake 'wish made'
        # eye. _lit_niche seats the dark core AND leaves an additive amber halo
        # that seeps out past the ink at night (the doll's one 'living' eye),
        # while by day the ink stays a flat black stare that clearly fills the
        # inner ring — the make-or-break asymmetry against the blank eye.
        _lit_niche(surf, cx, cy - inner, max(3, inner), max(4, inner * 2), palette)
        pygame.draw.circle(surf, ink, (cx, cy), inner)
        if not thumb:
            surf.set_at((cx - max(1, inner // 2), cy - max(1, inner // 2)),
                        _mix(cream, gold, 0.4))
    else:
        pygame.draw.circle(surf, cream, (cx, cy), inner)
        # Bold dark keyline (2 px) so the blank disc reads as a DELIBERATELY
        # empty outlined socket paired with the filled ink eye, not a pale blob
        # lost in the cream face patch.
        if inner >= 3:
            pygame.draw.circle(surf, _shade(ink, 20), (cx, cy), inner, 2)
        elif inner >= 2:
            pygame.draw.circle(surf, _shade(ink, 20), (cx, cy), inner, 1)


# ── One Daruma doll ─────────────────────────────────────────────────────────

def _draw_doll(surf, cx, y0, y1, palette, rng, *, fill_left):
    hh = y1 - y0
    lit, mid, sh = _body_triad(palette)
    dark_sky = _is_dark_sky(palette)
    half = PIPE_W // 2

    # Round body — collect the silhouette so the AA keyline + night rim trace
    # the true bulged edge, not a rect.
    left_pts = []
    right_pts = []
    for y in range(y0, y1):
        t = (y - y0) / max(1, hh)
        hw = _hw_at(t)
        xl = int(round(cx - hw))
        xr = int(round(cx + hw))
        vf = min(0.5, abs(t - _BELLY_T) * 0.9)
        _grad_row(surf, y, xl, xr, lit, mid, sh, vf)
        left_pts.append((xl, y))
        right_pts.append((xr, y))

    _gleam(surf, cx - int(half * 0.42), y0 + int(hh * 0.28),
           int(half * 0.5), int(hh * 0.2), palette)

    thumb = hh < 56

    gold = _gold_bright(palette)
    gold_d = _gold_deep(palette)
    cream = _cream(palette)

    # ── Cream face patch — the flat painted oval the red 'hood' wraps around.
    fw = int(half * _BELLY_K * 0.60)
    fh = int(hh * 0.24)
    fcy = y0 + int(hh * 0.33)
    fp = pygame.Rect(cx - fw, fcy - fh, fw * 2, fh * 2)
    pygame.draw.ellipse(surf, _shade(cream, -18), fp)
    pygame.draw.ellipse(surf, cream, fp.inflate(-2, -2))
    pygame.draw.ellipse(surf, _shade(cream, 14),
                        fp.move(-int(fw * 0.14), -1).inflate(-fw, -fh))
    pygame.draw.ellipse(surf, gold_d, fp, 1)     # thin gold calligraphic rim

    # ── Eyes — big gold-rimmed discs, one filled (gankake), one blank.
    eye_dx = int(half * 0.44)
    eye_cy = y0 + int(hh * 0.31)
    eye_r = max(4, int(hh * 0.10))
    _draw_eye(surf, cx - eye_dx, eye_cy, eye_r, palette,
              filled=fill_left, thumb=thumb)
    _draw_eye(surf, cx + eye_dx, eye_cy, eye_r, palette,
              filled=not fill_left, thumb=thumb)

    if not thumb:
        # ── Crane-brows — a bushy up-swept arc over each eye. Painted in DEEP
        #    gold only (a darker seat under a mid-gold face) so they recede
        #    below the bright eye-RIMS and don't tangle with them in the cream
        #    patch — the eyes stay the loudest thing on the face.
        gold_m = _mix(gold_d, gold, 0.35)
        by = eye_cy - eye_r - 1
        for s in (-1, 1):
            ex = cx + s * eye_dx
            brow = [(ex - eye_r - 1, by + 2), (ex - s, by - eye_r + 1),
                    (ex + eye_r + 1, by)]
            _aa_polyline(surf, _shade(gold_d, -14), brow)
            _aa_polyline(surf, gold_m, [(p[0], p[1] - 1) for p in brow])

        # ── Turtle-moustache — twin curls sweeping down-and-out from under the
        #    face centre. Also demoted to deep gold for the same hierarchy.
        my = y0 + int(hh * 0.47)
        mw = int(half * 0.5)
        for s in (-1, 1):
            mous = [(cx, my), (cx + s * int(mw * 0.5), my + 2),
                    (cx + s * mw, my - 1)]
            _aa_polyline(surf, _shade(gold_d, -14), mous)
            _aa_polyline(surf, gold_m, [(p[0], p[1] - 1) for p in mous])
        # Tiny nose knot between the eyes.
        pygame.draw.circle(surf, gold_d, (cx, eye_cy + eye_r + 2), 1)

        # ── Belly medallion — a gold fortune roundel on the lower red belly.
        my2 = y0 + int(hh * 0.73)
        mr = max(4, int(hh * 0.11))
        pygame.draw.circle(surf, gold_d, (cx, my2), mr + 1)
        pygame.draw.circle(surf, gold, (cx, my2), mr)
        pygame.draw.circle(surf, _shade(gold_d, -14), (cx, my2), mr, 1)
        # Stylized dark kanji strokes (a fortune glyph) inside the roundel.
        dark = palette['stone_dark']
        pygame.draw.line(surf, dark, (cx - mr + 2, my2 - mr + 2),
                         (cx + mr - 2, my2 - mr + 2), 1)
        pygame.draw.line(surf, dark, (cx, my2 - mr + 2), (cx, my2 + mr - 2), 1)
        pygame.draw.line(surf, dark, (cx - mr + 3, my2), (cx + mr - 3, my2), 1)
    else:
        # Thumbnail: guarantee the doll still reads on the cream patch + two
        # bold gold-rimmed eyes + a single gold brow bar alone at small scale.
        pygame.draw.line(surf, gold_d,
                         (cx - eye_dx - eye_r, eye_cy - eye_r - 1),
                         (cx + eye_dx + eye_r, eye_cy - eye_r - 1), 1)

    # ── AA silhouette keyline on the bulged edge (deep oxblood).
    outline = left_pts + list(reversed(right_pts))
    _aa_polyline(surf, _shade(sh, -20), outline, closed=True)

    # ── Night rim-light down the LEFT bulge so the lacquer red keeps its round
    #    silhouette against a dark sky (a quiet warm edge by day).
    rim = _mix(lit, (255, 210, 160), 0.5) if dark_sky else _shade(lit, 14)
    step = 1 if dark_sky else 2
    for i in range(0, len(left_pts), step):
        x, y = left_pts[i]
        surf.set_at((x, y), rim)
        if dark_sky and x + 1 < cx:
            surf.set_at((x + 1, y), _mix(rim, mid, 0.5))


# ── Gold crown-knot (topper) ────────────────────────────────────────────────

def _draw_knot(surf, cx, y_top, y_bot, half, palette):
    """A low rounded lacquer knob capped by a gold incense-swirl finial — the
    Daruma's quiet crown. It presents a SOLID band-wide red rim at the gap line
    (so the tower reaches the flyable edge with no side gap) and stays sub-1.2x
    wide so the round read is never spiked. Near-symmetric for the clean flip."""
    lit, mid, sh = _body_triad(palette)
    gold = _gold_bright(palette)
    gold_d = _gold_deep(palette)
    dh = y_bot - y_top
    dw = int(half * 2 * 1.08)
    x0 = cx - dw // 2
    # Band-wide lower body so the collision band is filled to the crown doll.
    body = pygame.Rect(x0, y_top + int(dh * 0.34), dw, dh - int(dh * 0.34) + 1)
    _gradient_rect(surf, body, lit, mid, sh)
    # Domed red top.
    dome = pygame.Rect(x0, y_top + 1, dw, int(dh * 0.9))
    pygame.draw.ellipse(surf, sh, dome)
    pygame.draw.ellipse(surf, mid, dome.inflate(-2, -2))
    pygame.draw.ellipse(surf, lit, dome.move(-1, 0).inflate(-dw // 2, -int(dh * 0.5)))
    # Gold base band where the knot seats on the crown doll.
    pygame.draw.line(surf, gold_d, (x0 + 2, y_bot - 1), (x0 + dw - 3, y_bot - 1), 1)
    pygame.draw.line(surf, gold, (x0 + 3, y_bot - 2), (x0 + dw - 4, y_bot - 2), 1)
    # Gold incense-swirl finial — a small gilt ball with a curl.
    kr = max(2, int(dh * 0.24))
    ky = y_top + kr + 1
    pygame.draw.circle(surf, gold_d, (cx, ky), kr + 1)
    pygame.draw.circle(surf, gold, (cx, ky), kr)
    _aa_polyline(surf, gold_d,
                 [(cx, ky - kr), (cx + kr, ky - kr - 1), (cx + kr, ky)])
    _aa_polyline(surf, _shade(sh, -18),
                 [(x0, y_bot), (x0, y_top + int(dh * 0.34)),
                  (x0 + dw - 1, y_top + int(dh * 0.34)), (x0 + dw - 1, y_bot)])


# ── 3-layer plinth + foliage ────────────────────────────────────────────────

def _draw_plinth(surf, cx, base_y, half, palette, seed):
    lit, mid, sh = _plinth_triad(palette)
    layers = 3
    for i in range(layers):
        lw = int(half * 2 * (1.14 + 0.16 * i))
        lh = 5
        ly = base_y - (layers - i) * lh
        r = pygame.Rect(cx - lw // 2, ly, lw, lh)
        _gradient_rect(surf, r, lit, mid, sh)
        pygame.draw.line(surf, _shade(sh, -20),
                         (r.x, r.bottom - 1), (r.right - 1, r.bottom - 1), 1)
        pygame.draw.line(surf, _shade(lit, 18), (r.x, r.y), (r.right - 1, r.y), 1)


def _draw_tower(surf, cx, y_top, y_bot, palette, seed):
    """One upright Daruma tower: mist -> adaptive doll stack -> gold crown-knot
    at the gap rim -> plinth + foliage. Height-adaptive doll COUNT keeps each
    bead round and un-squashed (1 fat Daruma at ~70 px, several at 355)."""
    rng = random.Random(seed)
    half = PIPE_W // 2
    section_h = y_bot - y_top

    plinth_h = min(15, max(9, int(section_h * 0.14)))
    knot_h = min(16, max(10, int(section_h * 0.15)))
    if section_h < 100:
        plinth_h = max(7, plinth_h - 2)
        knot_h = max(9, knot_h - 2)
    base_y = y_bot

    _draw_plinth_mist(surf, cx, base_y - plinth_h + 2, int(half * 2 * 1.8), palette)

    stack_bot = base_y - plinth_h
    stack_top = y_top + knot_h
    avail = stack_bot - stack_top
    if avail < 24:
        avail = 24
        stack_top = stack_bot - avail
    count = max(1, round(avail / _DOLL_H_FLOOR))
    dh = avail / count

    for i in range(count):
        dy_bot = int(round(stack_bot - i * dh))
        dy_top = int(round(stack_bot - (i + 1) * dh))
        _draw_doll(surf, cx, dy_top, dy_bot, palette, rng, fill_left=(i % 2 == 0))

    _draw_knot(surf, cx, y_top, stack_top, half, palette)

    _draw_plinth(surf, cx, base_y, half, palette, seed)
    draw_grass_bed(surf, cx, base_y - 1, PIPE_W + 12, 12, palette, seed=seed)
    draw_side_shrub(surf, cx - half - 6, base_y - 1, palette, scale=0.9)
    draw_side_shrub(surf, cx + half + 6, base_y - 1, palette, scale=0.8)


def candidate_daruma_gankake(surf, top_rect, bot_rect, palette, seed):
    """Bottom = Daruma tower rising from the ground, crown-knot at the gap. Top
    = the same tower vertical-FLIPPED from the ceiling — a symmetric two-ended
    totem whose two crown-knots meet at the rim. Daruma is bilaterally
    symmetric, so the flip is the cleanest in the family."""
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


def _round_metric(pal, seed=7):
    """Prove the silhouette reads ROUND, not gaunt: measure the belly bulge vs
    the seam waist as a fraction of PIPE_W. A gaunt column would be ~flat
    (ratio ~0); a round bead swings wide (belly >> waist)."""
    section_h = 210
    surf = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    br = pygame.Rect(MARGIN, GROUND_Y - section_h, PIPE_W, section_h)
    tr = pygame.Rect(MARGIN, 0, PIPE_W, 0)
    candidate_daruma_gankake(surf, tr, br, pal, seed=seed)
    widths = []
    for y in range(GROUND_Y - section_h + 20, GROUND_Y - 24):
        xs = [x for x in range(CACHE_W) if surf.get_at((x, y))[3] > 40]
        if xs:
            widths.append(max(xs) - min(xs) + 1)
    belly = max(widths) if widths else 0
    waist = min(widths) if widths else 0
    return belly, waist, PIPE_W


def _hero(pal, seed):
    gap_y, gap_h = 168, 150
    top_h = int(gap_y - gap_h / 2)
    bot_top = int(gap_y + gap_h / 2)
    full = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    top_rect = pygame.Rect(MARGIN, 0, PIPE_W, top_h)
    bot_rect = pygame.Rect(MARGIN, bot_top, PIPE_W, GROUND_Y - bot_top)
    candidate_daruma_gankake(full, top_rect, bot_rect, pal, seed=seed)

    tip_y = top_h - 6
    base_y = GROUND_Y + 8
    hero_h = base_y - tip_y
    hero = _bg(CACHE_W, hero_h, pal, hero_h - (base_y - GROUND_Y))
    hero.blit(full, (0, -tip_y))
    for ex in (MARGIN, MARGIN + PIPE_W):
        pygame.draw.line(hero, (230, 60, 60), (ex, 0), (ex, hero_h), 1)
    return hero, hero_h


def _closeup(pal, seed, scale=3):
    """Zoom on a single ground doll so the face relief + gold rims are checkable."""
    surf = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    br = pygame.Rect(MARGIN, GROUND_Y - 150, PIPE_W, 150)
    tr = pygame.Rect(MARGIN, 0, PIPE_W, 0)
    candidate_daruma_gankake(surf, tr, br, pal, seed=seed)
    crop = pygame.Surface((CACHE_W, 120))
    crop.blit(_bg(CACHE_W, 120, pal, 120), (0, 0))
    crop.blit(surf, (0, -(GROUND_Y - 150)))
    return pygame.transform.scale(
        crop, (crop.get_width() * scale, crop.get_height() * scale))


def _blackout(pal, section_h, scale):
    """Solid-black silhouette of a hero section — the round-vs-gaunt test."""
    surf = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    br = pygame.Rect(MARGIN, GROUND_Y - section_h, PIPE_W, section_h)
    tr = pygame.Rect(MARGIN, 0, PIPE_W, 0)
    candidate_daruma_gankake(surf, tr, br, pal, seed=7)
    pad_x = 30                    # wide enough to capture the round belly overspill
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

    _, mid_d, _ = _body_triad(pal)
    _, mid_n, _ = _body_triad(pal_n)
    print("LACQUER-RED BODY (mid tone)")
    print(f"  DAY   mid={mid_d} lum={_lum(mid_d):.1f}  R-B={mid_d[0]-mid_d[2]}")
    print(f"  NIGHT mid={mid_n} lum={_lum(mid_n):.1f}  R-B={mid_n[0]-mid_n[2]}")
    print(f"  day != night: {mid_d != mid_n}  (R dominant both: "
          f"{mid_d[0] > mid_d[1] and mid_n[0] > mid_n[1]})")

    # FIX 1 proof — the filled gankake pupil must floor well below lum 40 and
    # sit far under the red body so the black stare + one-filled/one-blank gag
    # both read. Compare against the body mid tone (the round-1 collision).
    ink_d, ink_n = _ink(pal), _ink(pal_n)
    print("FILLED PUPIL INK (target lum < 40; << red body ~78)")
    print(f"  DAY   ink={ink_d} lum={_lum(ink_d):.1f}  "
          f"[{'OK' if _lum(ink_d) < 40 else 'FAIL'}]  "
          f"body-lum={_lum(mid_d):.1f}  gap={_lum(mid_d)-_lum(ink_d):.1f}")
    print(f"  NIGHT ink={ink_n} lum={_lum(ink_n):.1f}  "
          f"[{'OK' if _lum(ink_n) < 40 else 'FAIL'}]  "
          f"body-lum={_lum(mid_n):.1f}  gap={_lum(mid_n)-_lum(ink_n):.1f}")

    # FIX 1 asymmetry proof — draw the filled + blank eye side by side at a
    # real doll eye radius and sample each centre: the filled centre must be
    # dark ink, the blank centre must stay cream. If both were gold rings with
    # pale centres (the round-1 bug) these two numbers would collide.
    for label, ph, pp in (("DAY", PHASE_DAY, pal), ("NIGHT", PHASE_NIGHT, pal_n)):
        eye_r = max(4, int((355 / 4) * 0.10))     # a mid-stack doll eye radius
        probe = pygame.Surface((eye_r * 6, eye_r * 4), pygame.SRCALPHA)
        cf, cb = eye_r * 2, eye_r * 4
        cy = eye_r * 2
        _draw_eye(probe, cf, cy, eye_r, pp, filled=True, thumb=False)
        _draw_eye(probe, cb, cy, eye_r, pp, filled=False, thumb=False)
        lf = _lum(probe.get_at((cf, cy))[:3])
        lb = _lum(probe.get_at((cb, cy))[:3])
        ok = lf < 40 and lb > 120 and (lb - lf) > 80
        print(f"EYE ASYMMETRY {label}: filled-centre lum={lf:.1f}  "
              f"blank-centre lum={lb:.1f}  delta={lb-lf:.1f}  "
              f"[{'READS' if ok else 'FAIL'}]")

    belly, waist, band = _round_metric(pal)
    print("ROUND METRIC (belly bulge vs seam waist, PIPE_W=58)")
    print(f"  belly={belly}px  waist={waist}px  band={band}px  "
          f"belly>band: {belly > band}  bulge=+{belly - band}px  "
          f"[{'ROUND' if belly - band >= 16 else 'FLAT'}]")

    hero_day, hd_h = _hero(pal, 7)
    hero_night, hn_h = _hero(pal_n, 7)
    close = _closeup(pal, 7)

    # Gap-rim clearance (crown-knot reaching the gap line, both towers).
    gap_probe = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    gp_bot = pygame.Rect(MARGIN, 243, PIPE_W, GROUND_Y - 243)
    gp_top = pygame.Rect(MARGIN, 0, PIPE_W, 93)
    candidate_daruma_gankake(gap_probe, gp_top, gp_bot, pal, seed=7)
    clear_bot = _gap_rim_clearance(gap_probe, MARGIN, MARGIN + PIPE_W, 243, up=True)
    clear_top = _gap_rim_clearance(gap_probe, MARGIN, MARGIN + PIPE_W, 93, up=True)
    print("GAP-RIM CLEARANCE (vertical-flip mirror)")
    print(f"  bottom knot -> gap: {clear_bot}px   top knot -> gap: {clear_top}px")

    strip_heights = [70, 210, 355]
    strips = []
    print("FILL GATE (max empty vertical run inside the 58px PIPE_W band)")
    for h in strip_heights:
        s = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
        br = pygame.Rect(MARGIN, GROUND_Y - h, PIPE_W, h)
        tr = pygame.Rect(MARGIN, 0, PIPE_W, 0)
        candidate_daruma_gankake(s, tr, br, pal, seed=7)
        run = _max_empty_run(s, MARGIN, MARGIN + PIPE_W, GROUND_Y - h, GROUND_Y)
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
        "daruma_gankake — round lacquer wish-doll totem  ·  round_2",
        True, (245, 240, 230)), (pad, 12))
    sheet.blit(sub.render(
        "red edges = PIPE_W (58px) collision band  ·  glossy _lacquer_red body  ·  "
        "cream patch + BOLD gold-rim eyes: one NEAR-BLACK INK pupil (gankake) / "
        "one blank outlined socket  ·  brows+moustache demoted to deep gold  ·  "
        "symmetric flip",
        True, (170, 172, 182)), (pad, 40))
    sheet.blit(sub.render(
        f"ROUND: belly {belly}px vs {band}px band (+{belly - band}px gutter bulge)  ·  "
        f"crown-knot dL: gap clear {clear_bot}/{clear_top}px  ·  "
        "the round pole vs the four angular masks", True, (150, 210, 160)),
        (pad, 56))

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
    sheet.blit(close, (x, head_h))
    pygame.draw.rect(sheet, (60, 62, 72),
                     (x, head_h, close.get_width(), close.get_height()), 1)
    sheet.blit(lab.render("FACE CLOSE-UP 3x", True,
                          (255, 224, 150)), (x, head_h + close.get_height() + 4))

    x += col_close + pad
    sheet.blit(lab.render("BLACKOUT (round test)", True, (255, 224, 150)),
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
