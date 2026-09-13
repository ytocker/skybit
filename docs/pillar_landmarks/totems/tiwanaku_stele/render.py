"""tiwanaku_stele — a flat incised Andean andesite SLAB stele (standalone candidate).

The one flat-slab in the totem family: NOT a round pole or a stacked head-tower
but a broad, straight-sided andesite TABLET (a Ponce/Bennett-lineage monolith)
that stands the flyable column on its own. Its whole identity — and the reason it
earns a slot over the far-safer pole shapes — is the single most contrasting
blackout in the set: a wide rectangular plank crowned by a bold radiating ray
halo that BREAKS past the slab edges into the gutters.

Make-or-break read (art-director pin): the slab must LEAD with one big proud
staff-god face + a slab-breaking ray halo, or it collapses into a blank grey
domino at PIPE_W=58. So the upper slab is dominated by a single square weeping-eyed
staff-god (Gateway-of-the-Sun deity) whose rays fan out past the silhouette, and
the lower slab carries incised staff-bearer fret bands. The face is carved in
raking light (deep incision grooves with a lit lower lip), the recesses hold
faded cinnabar ghosts of old paint, and only the rays + staffs catch a sparse
gilt glint — bare grey stone with red memories, the planar opposite of every
carved-wood / stacked-head concept.

Column-fill: the slab IS the column — a full-width gradient-beveled plank fills
the 58px collision band solid top-to-bottom by construction (the most robust fill
in the family). The rays are the ONLY gutter overhang; they never substitute for
column fill. Height-adaptive: short sections lead with the face+halo alone, and
fret bands are added downward as height grows.

Mirror read: a symmetric two-ended idol tablet — both sections cap their gap end
with the staff-god face+halo and root their plinth at the world edge, so the flyer
threads the gap between two glaring rayed faces. The top section is a true vertical
flip; the face is drawn left-right symmetric and the halo is radial, so the hung
copy still reads as a rayed stone face rather than an upside-down portrait.

Standalone: imports the real pagoda-family draw helpers so the material +
foliage language matches the shipped pillars; it does NOT modify any game module.

Run:  python docs/pillar_landmarks/totems/tiwanaku_stele/render.py
Out:  docs/pillar_landmarks/totems/tiwanaku_stele/round_2.png
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

# Real pagoda-family helpers — the same colour/relief/foliage vocabulary the
# shipped stone pillars use, so the stele reads as a peer, not a bolt-on.
from game.pillar_pagodas import (
    _mix, _shade, _gradient_rect, _aa_polyline, _lit_niche, _tile_hatch,
    _draw_plinth_mist, _is_dark_sky, _is_warming_sky,
    _cap_lit_for_dark_sky, _cap_dark_for_dark_sky, _buddha_eye,
    _korean_granite, _bronze, _gold_bright,
)
from game.pillar_variants import draw_grass_bed, draw_spiral_glow
# draw_side_shrub lives in game.draw (pillar_pagodas itself imports it from there).
from game.draw import draw_side_shrub

MARGIN = 64                       # matches entities.Pipe eave/ornament gutter
CACHE_W = PIPE_W + MARGIN * 2
CACHE_H = GROUND_Y
PHASE_DAY = 0.30                  # bare andesite reads warm-grey against tan sky
PHASE_NIGHT = 0.85               # deep night — checks cinnabar + gilt + face glow

# Slab geometry. The tablet slightly OVERHANGS the 58px collision band (half=31
# → 62 wide) so the outer band columns never starve at the bevel; a faint taper
# makes the base read heavier than the crown like a real standing monolith.
_SLAB_HALF_TOP = 30
_SLAB_HALF_BASE = 32


# ── stele materials (palette-keyed so the biome day→night retint sweeps) ──────
def _andesite(p):
    # Lake-district grey andesite body — biased to stone_mid so it reads as bare
    # cool stone, distinct from the moai's warmer basalt and the KFC sandstone.
    return _mix(p['stone_mid'], (128, 124, 116), 0.60)


def _andesite_lit(p):
    # Sun-struck left bevel — gives the flat plank a lit edge so it is a VOLUME,
    # not a cutout, exactly the trap a flat slab must avoid.
    return _mix(p['stone_light'], (196, 192, 182), 0.58)


def _andesite_shadow(p):
    # Shadow right bevel + the dark floor of every incised groove.
    return _mix(p['stone_dark'], (66, 64, 60), 0.80)


def _groove_lip(p):
    # The LIT lower lip of a carved groove — a hair brighter than the body so a
    # 1-px incision reads as a chiselled channel, not a painted line.
    return _mix(p['stone_light'], (210, 206, 196), 0.50)


def _cinnabar(p):
    # Faded cinnabar pigment trapped in the deep recesses — anchored to
    # stone_dark so the one focal hue stays a warm red ghost even at night.
    return _mix(p['stone_dark'], (170, 66, 44), 0.66)


# ── carved-groove primitive ──────────────────────────────────────────────────
def _incise(surf, palette, points, *, closed=False, lip=True):
    """A chiselled incision: a dark groove floor with a 1-px lit lower lip just
    below it, so a carved line reads through raking light instead of as flat
    paint. The lit lip is offset +1px in y (catching the upper light on the
    groove's lower wall) — the canonical relief cue at this scale."""
    _aa_polyline(surf, _andesite_shadow(palette), points, closed=closed)
    if lip and len(points) >= 2:
        lifted = [(x, y + 1) for (x, y) in points]
        _aa_polyline(surf, _groove_lip(palette), lifted, closed=closed)


def _slab_half(u):
    """Half-width of the slab at fractional height u (0 = gap end, 1 = base).
    A faint linear taper — wider at the footing so the tablet reads as standing
    stone, not a floating card."""
    return _SLAB_HALF_TOP + (_SLAB_HALF_BASE - _SLAB_HALF_TOP) * max(0.0, min(1.0, u))


# ── the ray halo (identity beat: it must break the slab silhouette) ───────────
def _draw_ray_halo(surf, cx, cy, r_in, palette, *, seed=0):
    """A bold radiating halo of chiselled rays fanning off the staff-god head —
    the Gateway-of-the-Sun ray-face. Side and up-diagonal rays reach PAST the
    slab edge into the gutter so the BLACKOUT is a rayed tablet, never a bare
    rectangle; downward rays are short and absorbed into the body so the lower
    slab stays free for the fret bands. Long rays alternate a gilt terminal disc
    and a stepped-square head, the two authentic ray terminals. AA throughout."""
    rng = random.Random(seed)
    gold = _gold_bright(palette)
    body = _andesite(palette)
    lit = _andesite_lit(palette)
    # 14 rays around the upper hemisphere + sides. Angles measured from +x, going
    # up and around; the lower ~120° arc is skipped (that is the fret body).
    n = 14
    a0, a1 = math.radians(-24), math.radians(204)   # spans right-low → up → left-low
    for i in range(n):
        t = i / (n - 1)
        ang = a0 + (a1 - a0) * t
        ca, sa = math.cos(ang), -math.sin(ang)      # -sin: screen y grows down
        long_ray = (i % 2 == 0)
        r_out = (r_in + (22 if long_ray else 12)) + rng.randint(-1, 1)
        x0, y0 = cx + ca * r_in, cy + sa * r_in
        x1, y1 = cx + ca * r_out, cy + sa * r_out
        # Wedge ray: two chiselled edges from a wide base to the tip, filled with
        # a lit andesite so the ray has its own tiny volume before the AA edges.
        # Bases are bumped past ~2px half-width so no shaft sub-pixel-blends into
        # a matching (overcast/dusk) andesite-grey sky and drifts back to plank.
        px, py = -sa, ca                            # unit perpendicular
        base = 3.1 if long_ray else 2.2
        poly = [(x0 + px * base, y0 + py * base),
                (x1, y1),
                (x0 - px * base, y0 - py * base)]
        pygame.draw.polygon(surf, body, [(int(x), int(y)) for x, y in poly])
        _aa_polyline(surf, lit, [(x0 + px * base, y0 + py * base), (x1, y1)])
        _aa_polyline(surf, _andesite_shadow(palette),
                     [(x0 - px * base, y0 - py * base), (x1, y1)])
        # EVERY spoke ends in an anchored terminal so the halo can't half-vanish
        # against a matching sky: the tip always carries a value contrast even
        # when the shaft blends. Long rays keep the sparse gilt (disc/square),
        # each ringed in shadow; short rays a smaller lit-andesite bead in a
        # shadow ring — anchoring without spending more gilt.
        tx, ty = int(x1), int(y1)
        if long_ray:
            if i % 4 == 0:
                pygame.draw.circle(surf, _andesite_shadow(palette), (tx, ty), 3)
                pygame.draw.circle(surf, gold, (tx, ty), 2)
                pygame.draw.circle(surf, _shade(gold, 40), (tx, ty), 1)
            else:
                pygame.draw.rect(surf, _andesite_shadow(palette),
                                 (tx - 2, ty - 2, 5, 5))
                pygame.draw.rect(surf, gold, (tx - 1, ty - 1, 3, 3))
        else:
            pygame.draw.circle(surf, _andesite_shadow(palette), (tx, ty), 2)
            pygame.draw.circle(surf, lit, (tx, ty), 1)


# ── the square weeping staff-god eye (rectilinear _buddha_eye variant) ────────
def _staff_god_eye(surf, cx, cy, w, h, palette, *, thumbnail=False):
    """A square Tiwanaku eye: a bright andesite eye-pad, a deep incised square
    socket, a cinnabar square pupil and the signature vertical TEAR-LINES weeping
    down from the lower rim. Rectilinear where every other face in the family is
    almond/round. `thumbnail` collapses it to a single solid dark pit so the eye
    survives as one of the 2 fallback dots at 58px."""
    pad = _andesite_lit(palette)
    floor = _andesite_shadow(palette)
    cin = _cinnabar(palette)
    x0, y0 = cx - w // 2, cy - h // 2
    if thumbnail:
        pygame.draw.rect(surf, floor, (x0, y0, w, h))
        return
    # Raised square eye-pad catching the light.
    pygame.draw.rect(surf, pad, (x0 - 1, y0 - 1, w + 2, h + 2))
    # Deep incised socket.
    pygame.draw.rect(surf, floor, (x0, y0, w, h))
    # Lit lower lip of the socket — the carved-groove cue.
    pygame.draw.line(surf, _groove_lip(palette),
                     (x0, y0 + h - 1), (x0 + w - 1, y0 + h - 1), 1)
    # Square cinnabar pupil, offset to a fixed corner (the divided Tiwanaku eye).
    pw = max(2, w // 2)
    ph = max(2, h // 2)
    pygame.draw.rect(surf, cin, (cx - pw // 2, cy - ph // 2, pw, ph))
    pygame.draw.rect(surf, _shade(cin, 30), (cx - pw // 2, cy - ph // 2, pw, 1))
    # Weeping tear-lines — 2 short chiselled verticals dropping from the lower rim.
    for dx in (-w // 4, w // 4):
        _incise(surf, palette,
                [(cx + dx, y0 + h), (cx + dx, y0 + h + max(3, h // 2))], lip=False)


def _fret_mouth(surf, cx, cy, w, h, palette):
    """A stepped-fret bar mouth — a wide incised rectangle split by vertical
    tooth grooves, cinnabar smouldering in the recess. The bar-shaped mouth is
    the staff-god's, not a niche doorway."""
    floor = _andesite_shadow(palette)
    x0 = cx - w // 2
    pygame.draw.rect(surf, floor, (x0, cy - h // 2, w, h))
    # Cinnabar ghost inside the mouth recess.
    pygame.draw.rect(surf, _cinnabar(palette),
                     (x0 + 1, cy - h // 2 + 1, w - 2, max(1, h - 2)))
    # Tooth grooves — vertical incisions dividing the fret.
    n_teeth = max(3, w // 6)
    for k in range(1, n_teeth):
        tx = x0 + int(w * k / n_teeth)
        pygame.draw.line(surf, floor, (tx, cy - h // 2), (tx, cy + h // 2 - 1), 1)
    # Lit lip along the top + bottom edges so the bar reads as carved-in.
    pygame.draw.line(surf, _groove_lip(palette),
                     (x0, cy + h // 2), (x0 + w - 1, cy + h // 2), 1)


def _draw_face(surf, cx, cy, fw, fh, palette, *, thumbnail=False):
    """The big proud staff-god face that dominates the upper slab. A square head
    framed by an incised border, square weeping eyes, a keeled nose bar and a
    stepped-fret mouth. Kept left-right symmetric so the vertical mirror still
    reads as a rayed stone face."""
    half = fw // 2
    top = cy - fh // 2
    # Incised square head-frame (the carved cartouche around the deity).
    frame = [(cx - half, top), (cx + half, top),
             (cx + half, top + fh), (cx - half, top + fh)]
    _incise(surf, palette, frame, closed=True)
    # Brow ridge — a chiselled horizontal band above the eyes with cinnabar.
    brow_y = top + int(fh * 0.30)
    pygame.draw.rect(surf, _andesite_shadow(palette),
                     (cx - half + 3, brow_y - 2, fw - 6, 3))
    pygame.draw.line(surf, _cinnabar(palette),
                     (cx - half + 4, brow_y - 1), (cx + half - 4, brow_y - 1), 1)
    pygame.draw.line(surf, _groove_lip(palette),
                     (cx - half + 3, brow_y + 1), (cx + half - 3, brow_y + 1), 1)
    # Eyes.
    ew = max(4, int(fw * 0.26))
    eh = max(4, int(fh * 0.22))
    ey = top + int(fh * 0.48)
    ex = int(fw * 0.24)
    _staff_god_eye(surf, cx - ex, ey, ew, eh, palette, thumbnail=thumbnail)
    _staff_god_eye(surf, cx + ex, ey, ew, eh, palette, thumbnail=thumbnail)
    if thumbnail:
        return
    # Keeled nose bar — a 2px lit ridge + a 1px shadow flank so the face has a
    # clear vertical spine at 1x (a single 1px line washed out against the body).
    ny0, ny1 = ey - 1, ey + int(fh * 0.22)
    pygame.draw.line(surf, _andesite_lit(palette), (cx - 1, ny0), (cx - 1, ny1), 1)
    pygame.draw.line(surf, _andesite_lit(palette), (cx, ny0), (cx, ny1), 1)
    pygame.draw.line(surf, _andesite_shadow(palette), (cx + 1, ny0), (cx + 1, ny1), 1)
    pygame.draw.line(surf, _cinnabar(palette), (cx, ny1), (cx, ny1 + 1), 1)
    # Stepped-fret mouth.
    _fret_mouth(surf, cx, top + int(fh * 0.80),
                int(fw * 0.66), max(4, int(fh * 0.16)), palette)


def _draw_fret_band(surf, cx, y, w, h, palette, *, seed=0):
    """A staff-bearer fret band across the lower slab — a stepped Andean meander
    of incised right-angle steps with cinnabar in the recesses and a lone gilt
    staff-glint, textured with a fine tile-hatch so it reads as dense low relief
    rather than an empty stripe."""
    x0 = cx - w // 2
    floor = _andesite_shadow(palette)
    lip = _groove_lip(palette)
    # Recessed band ground with cinnabar traces.
    pygame.draw.rect(surf, _mix(_andesite(palette), floor, 0.35), (x0, y, w, h))
    # Fine chiselled hatch texture across the recess.
    _tile_hatch(surf, x0 + 2, y + 1, x0 + w - 2, y + 1, floor, step=4)
    # Stepped meander: alternating high/low blocks joined into a Greek-key run.
    n = max(3, w // 12)
    bw = w / n
    prev = None
    for k in range(n):
        bx = int(x0 + k * bw)
        step_up = (k % 2 == 0)
        by = y + (1 if step_up else h // 2)
        bh = h // 2 - 1
        pygame.draw.rect(surf, floor, (bx + 1, by, int(bw) - 2, bh))
        pygame.draw.rect(surf, _cinnabar(palette), (bx + 2, by + 1, int(bw) - 4, 1))
        pygame.draw.line(surf, lip, (bx + 1, by + bh - 1),
                         (bx + int(bw) - 2, by + bh - 1), 1)
        cur = (bx + int(bw) // 2, by + bh // 2)
        if prev:
            _incise(surf, palette, [prev, cur], lip=False)
        prev = cur
    # A single gilt staff-glint per band — the sceptre the staff-god bearers hold.
    rng = random.Random(seed)
    gx = x0 + rng.randint(w // 4, 3 * w // 4)
    pygame.draw.line(surf, _gold_bright(palette), (gx, y + 2), (gx, y + h - 2), 1)


def _draw_plinth(surf, cx, y_bottom, palette):
    """A 3-layer footing — a wide granite base slab, a mid course and a top
    string course — rooting the tablet at the world edge like the pagoda plinths."""
    gran = _korean_granite(palette)
    lit = _shade(gran, 26)
    dark = _shade(gran, -46)
    courses = ((78, 6), (68, 5), (58, 4))     # (width, height) bottom → top
    y = y_bottom
    for w, hh in courses:
        y -= hh
        pygame.draw.rect(surf, dark, (cx - w // 2, y, w, hh))
        pygame.draw.rect(surf, gran, (cx - w // 2 + 1, y + 1, w - 2, hh - 2))
        pygame.draw.line(surf, lit, (cx - w // 2 + 2, y), (cx + w // 2 - 3, y), 1)


def _draw_stele_upright(surf, cx, y_top, y_bottom, palette, seed):
    """Draw the slab upright: plinth at y_bottom, staff-god face+halo at the gap
    end (y_top). Callers flip the whole surface for the ceiling-hung section."""
    rng = random.Random(seed)
    sect_h = y_bottom - y_top
    if sect_h < 8:
        return

    plinth_h = 15 if sect_h >= 64 else max(6, sect_h // 6)
    slab_top = y_top
    slab_bot = y_bottom - plinth_h
    slab_h = slab_bot - slab_top
    if slab_h < 8:
        return

    body = _andesite(palette)
    lit = _cap_lit_for_dark_sky(_andesite_lit(palette), palette)
    shadow = _cap_dark_for_dark_sky(_andesite_shadow(palette), palette)

    # ── the SLAB: full-width beveled plank. One horizontal 3-stop gradient over
    # the whole rect gives the lit-left / shadow-right VOLUME and IS the column
    # fill (solid by construction). The base slightly overhangs the 58px band so
    # the outer band columns never starve. A faint taper is chiselled in after by
    # clearing two thin corner wedges at the crown. ──
    _gradient_rect(surf, pygame.Rect(cx - _SLAB_HALF_BASE, slab_top,
                                     _SLAB_HALF_BASE * 2, slab_h),
                   lit, body, shadow)
    taper = _SLAB_HALF_BASE - _SLAB_HALF_TOP
    if taper > 0:
        wedge_h = min(slab_h, 40)
        for i in range(wedge_h):
            cut = int(round(taper * (1 - i / max(1, wedge_h - 1))))
            if cut > 0:
                clr = pygame.Surface((cut, 1), pygame.SRCALPHA)
                surf.blit(clr, (cx - _SLAB_HALF_BASE, slab_top + i),
                          special_flags=pygame.BLEND_RGBA_MULT)
                surf.blit(clr, (cx + _SLAB_HALF_BASE - cut, slab_top + i),
                          special_flags=pygame.BLEND_RGBA_MULT)
    # Crisp chiselled outline down both long edges (the slab's straight-side tell).
    _aa_polyline(surf, _shade(lit, 20),
                 [(cx - _SLAB_HALF_TOP, slab_top), (cx - _SLAB_HALF_BASE, slab_bot)])
    _aa_polyline(surf, shadow,
                 [(cx + _SLAB_HALF_TOP, slab_top), (cx + _SLAB_HALF_BASE, slab_bot)])

    # ── face + halo budget: the face is a fixed proud size; it always leads. ──
    face_w = 42
    face_h = 34
    face_cy = slab_top + 4 + face_h // 2
    # Rays reach past the ±30 slab edge into the gutter — the identity beat.
    r_in = int(face_w * 0.60)

    # Night glow FIRST, behind everything, so the face reads as a lit idol after
    # dark (the free landmark beat this concept otherwise lacks).
    if _is_dark_sky(palette) and not _is_warming_sky(palette):
        draw_spiral_glow(surf, cx, face_cy, radius=int(face_w * 0.7))

    _draw_ray_halo(surf, cx, face_cy, r_in, palette, seed=seed)
    _draw_face(surf, cx, face_cy, face_w, face_h, palette)

    # ── fret bands fill the slab BELOW the face, added downward as height grows.
    bands_top = face_cy + face_h // 2 + 6
    band_h = 14
    gap = 6
    y = bands_top
    bi = 0
    while y + band_h <= slab_bot - 3:
        u = (y + band_h / 2 - slab_top) / max(1, slab_h)
        bw = int(_slab_half(u) * 2) - 8
        _draw_fret_band(surf, cx, y, bw, band_h, palette, seed=seed + bi)
        y += band_h + gap
        bi += 1
    # If a stub of bare slab remains under the last band, incise a lower
    # dedication cartouche — two tiny glyphs (a carved maker's mark, cinnabar in
    # the recess) so no flat panel reads as empty.
    if slab_bot - 3 - y > 6:
        gy = (y + slab_bot) // 2
        for gx, vertical in ((cx - 9, True), (cx + 9, False)):
            pygame.draw.rect(surf, _andesite_shadow(palette), (gx - 3, gy - 3, 6, 6))
            pygame.draw.rect(surf, _cinnabar(palette), (gx - 2, gy - 2, 4, 4))
            if vertical:
                pygame.draw.line(surf, _andesite_shadow(palette),
                                 (gx, gy - 2), (gx, gy + 1), 1)
            else:
                pygame.draw.line(surf, _andesite_shadow(palette),
                                 (gx - 2, gy), (gx + 1, gy), 1)
            pygame.draw.line(surf, _groove_lip(palette),
                             (gx - 3, gy + 3), (gx + 2, gy + 3), 1)

    _draw_plinth(surf, cx, y_bottom, palette)

    # ── foliage + mist at the footing, matching the pagoda language ──
    _draw_plinth_mist(surf, cx, y_bottom, 72, palette)
    draw_grass_bed(surf, cx, y_bottom, 70, 14, palette, seed=seed)
    j = rng.randint(-2, 2)
    draw_side_shrub(surf, cx - 34 + j, y_bottom, palette, scale=1.05)
    draw_side_shrub(surf, cx + 34 - j, y_bottom, palette, scale=0.95)


def candidate_tiwanaku_stele(surf, top_rect, bot_rect, palette, seed):
    """Bottom is the slab rising from the ground, staff-god face at the gap.
    Top is the same builder flipped — a symmetric two-ended rayed tablet hung
    from the ceiling, its face glaring down into the gap."""
    if bot_rect.height > 0:
        _draw_stele_upright(surf, bot_rect.centerx, bot_rect.y, bot_rect.bottom,
                            palette, seed)
    if top_rect.height > 0:
        tmp = pygame.Surface((surf.get_width(), top_rect.height), pygame.SRCALPHA)
        # Hold the hung copy's face+halo (and slab tip) ~4px off the gap so the
        # two facing idols don't kiss across the flyway. Clip only the top rows
        # of tmp — the plinth/foliage at the far end stay untouched — and apply
        # it to the hung copy alone so the ground-rising section still fills the
        # collision band solid to the gap.
        gap_inset = 4
        tmp.set_clip(pygame.Rect(0, gap_inset, tmp.get_width(),
                                 top_rect.height - gap_inset))
        _draw_stele_upright(tmp, top_rect.centerx, 0, top_rect.height,
                            palette, seed + 1)
        tmp.set_clip(None)
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
    """Longest contiguous vertical run of transparent pixels within the band —
    a numeric feasibility check (never viewed as an image)."""
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


def _hero(pal, seed):
    """One upright + ceiling-mirror tablet over a sky, cropped to a hero strip."""
    gap_y, gap_h = 150, 150
    top_h = int(gap_y - gap_h / 2)
    bot_top = int(gap_y + gap_h / 2)
    full = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    top_rect = pygame.Rect(MARGIN, 0, PIPE_W, top_h)
    bot_rect = pygame.Rect(MARGIN, bot_top, PIPE_W, GROUND_Y - bot_top)
    candidate_tiwanaku_stele(full, top_rect, bot_rect, pal, seed=seed)
    tip_y = bot_top - 30           # extra headroom so the gap-end rays show
    base_y = GROUND_Y + 8
    hero_h = base_y - tip_y
    hero = _bg(CACHE_W, hero_h, pal, hero_h - (base_y - GROUND_Y))
    hero.blit(full, (0, -tip_y))
    for ex in (MARGIN, MARGIN + PIPE_W):
        pygame.draw.line(hero, (230, 60, 60), (ex, 0), (ex, hero_h), 1)
    return hero, hero_h


def _closeup(pal, seed, scale=3):
    """Zoom on the bottom-section face so the staff-god relief is checkable."""
    h = 150
    surf = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    bot_rect = pygame.Rect(MARGIN, GROUND_Y - h, PIPE_W, h)
    top_rect = pygame.Rect(MARGIN, 0, PIPE_W, 0)
    candidate_tiwanaku_stele(surf, top_rect, bot_rect, pal, seed=seed)
    crop_h = 70
    crop = pygame.Surface((CACHE_W, crop_h))
    crop.blit(_bg(CACHE_W, crop_h, pal, crop_h), (0, 0))
    crop.blit(surf, (0, -(GROUND_Y - h) + 24))
    return pygame.transform.scale(
        crop, (crop.get_width() * scale, crop.get_height() * scale))


def _blackout(pal, seed, scale=3):
    """Render a short face+halo section and reduce it to a SOLID BLACK silhouette
    on light — the honest 58px blackout test: it must read as a RAYED tablet
    (rays breaking the rectangle), not a blank plank."""
    h = 96
    surf = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    bot_rect = pygame.Rect(MARGIN, GROUND_Y - h, PIPE_W, h)
    top_rect = pygame.Rect(MARGIN, 0, PIPE_W, 0)
    candidate_tiwanaku_stele(surf, top_rect, bot_rect, pal, seed=seed)
    crop_w, crop_h = CACHE_W, h
    crop = pygame.Surface((crop_w, crop_h))
    crop.fill((235, 236, 240))
    for x in range(crop_w):
        for y in range(crop_h):
            if surf.get_at((x, GROUND_Y - h + y))[3] > 0:
                crop.set_at((x, y), (18, 18, 22))
    return pygame.transform.scale(crop, (crop_w * scale, crop_h * scale))


def _lum(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def _measure_min_ray_width(pal, seed):
    """Render the halo alone and measure each spoke's opaque width perpendicular
    to its axis at mid-length — the honest 'no spoke below ~2px' check. Reports
    per-spoke widths + the worst; terminals guarantee a ≥2px anchor at the tip."""
    W = H = 180
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    cx = cy = W // 2
    r_in = int(42 * 0.60)
    _draw_ray_halo(s, cx, cy, r_in, pal, seed=seed)
    n = 14
    a0, a1 = math.radians(-24), math.radians(204)
    widths = []
    for i in range(n):
        t = i / (n - 1)
        ang = a0 + (a1 - a0) * t
        ca, sa = math.cos(ang), -math.sin(ang)
        long_ray = (i % 2 == 0)
        r_out = r_in + (22 if long_ray else 12)
        rr = r_in + (r_out - r_in) * 0.5      # sample the shaft, not hub/terminal
        sx, sy = cx + ca * rr, cy + sa * rr
        px, py = -sa, ca
        w = 0
        for d in range(-7, 8):
            x = int(round(sx + px * d)); y = int(round(sy + py * d))
            if 0 <= x < W and 0 <= y < H and s.get_at((x, y))[3] > 0:
                w += 1
        widths.append((("L" if long_ray else "s"), w))
    worst = min(w for _, w in widths)
    return worst, widths


def main():
    pal_d = biome.palette_for_phase(PHASE_DAY)
    pal_n = biome.palette_for_phase(PHASE_NIGHT)
    seed = 7

    # ── value proof: the incised eye pit must stay dark vs the slab body, and
    # the cinnabar pupil must survive night as a warm focal. ──
    print("EYE / CINNABAR value separation (must survive night)")
    for name, p in (("DAY", pal_d), ("NIGHT", pal_n)):
        b = _andesite(p); pit = _andesite_shadow(p); cin = _cinnabar(p)
        dv = abs(_lum(b) - _lum(pit)) / max(1, _lum(b)) * 100
        print(f"  {name:5s} body_lum={_lum(b):5.1f} pit_lum={_lum(pit):5.1f} "
              f"delta={dv:4.1f}%  cinnabar={cin} R-G={cin[0]-cin[1]}")

    # ── ray-width proof: no spoke should sub-pixel-blend into a matching sky ──
    worst, widths = _measure_min_ray_width(pal_d, seed)
    print("RAY SHAFT widths (perp opaque px at mid-length; terminals anchor tips)")
    print("  " + " ".join(f"{k}{w}" for k, w in widths))
    print(f"  min shaft width = {worst}px  [{'OK' if worst >= 2 else 'THIN'}]")

    hero_d, hd_h = _hero(pal_d, seed)
    hero_n, hn_h = _hero(pal_n, seed)
    close = _closeup(pal_d, seed, scale=3)
    black = _blackout(pal_d, seed, scale=3)

    # ── FEASIBILITY STRIP: bottom section at three heights + fill gate ──
    strip_heights = [70, 210, 355]
    strips = []
    print("FILL GATE (max empty vertical run inside the 58px PIPE_W band)")
    for h in strip_heights:
        s = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
        br = pygame.Rect(MARGIN, GROUND_Y - h, PIPE_W, h)
        tr = pygame.Rect(MARGIN, 0, PIPE_W, 0)
        candidate_tiwanaku_stele(s, tr, br, pal_d, seed=seed)
        run = _max_empty_run(s, MARGIN, MARGIN + PIPE_W, GROUND_Y - h, GROUND_Y)
        crop = pygame.Surface((CACHE_W, h + 8))
        crop.blit(_bg(CACHE_W, h + 8, pal_d, h), (0, 0))
        crop.blit(s, (0, -(GROUND_Y - h)))
        for ex in (MARGIN, MARGIN + PIPE_W):
            pygame.draw.line(crop, (230, 60, 60), (ex, 0), (ex, h + 8), 1)
        strips.append((h, crop, run))
        print(f"  h={h:3d}  max empty run = {run}px  [{'OK' if run <= 12 else 'FAIL'}]")

    # ── mirror gap-rim clearance: how close the flipped top face sits to the gap
    gap_y, gap_h = 150, 150
    top_h = int(gap_y - gap_h / 2)
    ms = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    candidate_tiwanaku_stele(ms, pygame.Rect(MARGIN, 0, PIPE_W, top_h),
                             pygame.Rect(MARGIN, 0, PIPE_W, 0), pal_d, seed=seed)
    rim = 0
    for y in range(top_h - 1, -1, -1):
        if any(ms.get_at((x, y))[3] > 0 for x in range(MARGIN, MARGIN + PIPE_W)):
            rim = y
            break
    print(f"MIRROR: top section height={top_h}px, hung-copy lowest fill y={rim}px "
          f"(gap-rim clearance = {top_h - rim}px below tip)")

    # ── compose the sheet ──
    pad = 12
    label_h = 24
    head_h = 64
    title = pygame.font.SysFont(None, 32)
    sub = pygame.font.SysFont(None, 18)
    lab = pygame.font.SysFont(None, 20)

    col_w = CACHE_W
    strips_total_h = sum(c.get_height() + label_h + pad for _, c, _ in strips)
    right_h = close.get_height() + label_h + pad + black.get_height() + label_h
    col_h = max(hd_h + label_h, hn_h + label_h, strips_total_h, right_h)
    sheet_w = pad + col_w * 3 + close.get_width() + pad * 4
    sheet_h = head_h + col_h + pad * 2
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((24, 25, 30))

    sheet.blit(title.render("tiwanaku_stele — flat incised andesite SLAB  ·  round_2",
                            True, (245, 240, 230)), (pad, 12))
    sheet.blit(sub.render("red edges = PIPE_W (58px) collision band  ·  big staff-god "
                          "face + slab-breaking ray halo  ·  cinnabar in recess  ·  "
                          "gilt ray/staff glints  ·  night face-glow", True,
                          (170, 172, 182)), (pad, 40))

    # col 1: hero day
    x, y = pad, head_h
    sheet.blit(hero_d, (x, y))
    pygame.draw.rect(sheet, (60, 62, 72), (x, y, col_w, hd_h), 1)
    sheet.blit(lab.render("HERO — DAY (0.30)", True, (255, 224, 150)),
               (x, y + hd_h + 4))

    # col 2: hero night
    x += col_w + pad
    sheet.blit(hero_n, (x, y))
    pygame.draw.rect(sheet, (60, 62, 72), (x, y, col_w, hn_h), 1)
    sheet.blit(lab.render("HERO — NIGHT (0.85)", True, (255, 224, 150)),
               (x, y + hn_h + 4))

    # col 3: feasibility strips
    x += col_w + pad
    sy = head_h
    sheet.blit(lab.render("FILL — bottom section", True, (255, 224, 150)),
               (x, sy - 20))
    for h, crop, run in strips:
        sheet.blit(crop, (x, sy))
        pygame.draw.rect(sheet, (60, 62, 72), (x, sy, col_w, crop.get_height()), 1)
        ok = "OK" if run <= 12 else "FAIL"
        sheet.blit(lab.render(f"h={h}px  ·  run {run}px  [{ok}]", True,
                              (200, 235, 170) if run <= 12 else (255, 140, 140)),
                   (x, sy + crop.get_height() + 4))
        sy += crop.get_height() + label_h + pad

    # col 4: face close-up (top) + blackout thumbnail (below)
    x += col_w + pad
    sheet.blit(close, (x, head_h))
    pygame.draw.rect(sheet, (60, 62, 72),
                     (x, head_h, close.get_width(), close.get_height()), 1)
    sheet.blit(lab.render("FACE close-up (3x) — staff-god relief", True,
                          (255, 224, 150)), (x, head_h + close.get_height() + 4))
    by = head_h + close.get_height() + label_h + pad
    sheet.blit(black, (x, by))
    pygame.draw.rect(sheet, (60, 62, 72),
                     (x, by, black.get_width(), black.get_height()), 1)
    sheet.blit(lab.render("58px BLACKOUT — rayed tablet, not a plank", True,
                          (255, 224, 150)), (x, by + black.get_height() + 4))

    out = pathlib.Path(__file__).resolve().parent / "round_2.png"
    pygame.image.save(sheet, out)
    print(f"wrote {out}  ({sheet.get_width()}x{sheet.get_height()})")


if __name__ == "__main__":
    main()
