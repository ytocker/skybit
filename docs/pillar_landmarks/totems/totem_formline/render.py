"""totem_formline — a Pacific-NW painted cedar totem pole (standalone candidate).

The bright anchor of the TOTEM family: a vertical stack of carved + PAINTED
crest beings — a wing-spread THUNDERBIRD crowning the gap end, then BEAR and
RAVEN faces below — drawn in classic Northwest-coast formline (bold black
ovoid eyes, vermilion red, blue-green teal, white teeth, a little gilt) on a
warm cedar body. Its wings-out / beak-out zig-zag is the only winged silhouette
in the set; the FACES are the star and must read as genuinely carved and
painted, not smudges.

Fidelity contract: this file imports the REAL pagoda material + primitive
helpers so the palette retint, the 3-stop body gradient, the AA silhouettes,
the recessed lit-niches (free night glow), the plinth mist and the ground
foliage match the shipped pagodas exactly. It draws standalone and does NOT
modify any game/ runtime module.

Column-fill: a continuous full-height cedar core spans the whole PIPE_W (58 px)
collision band, so no vertical band is ever starved; the crest FACES paint on
top of it and the thunderbird wings / raven beak are gutter OVERHANG only (they
exceed 58 px sideways but never substitute for the centre column). The
thunderbird head caps the gap-end rim solid.

Mirror decision (deliberate): the top (ceiling) section is a TRUE vertical flip
of the upright builder — a stylized symmetric TWO-ENDED totem. A hanging totem's
finial must point into the gap (downward), so forcing the faces upright while the
finial hangs down would be internally contradictory; a genuine mirror is the
coherent read. The thunderbird crown correctly points into the gap from BOTH
ends, and formline bear/raven faces are abstract symmetric ovoid + split-U
compositions (not human faces), so the flipped half reads as decorative Northwest-
coast symmetry rather than an unsettling upside-down face — verified at gameplay
scale by the CEILING close-up + 58 px blackout panels.

Run:  python docs/pillar_landmarks/totems/totem_formline/render.py
Out:  docs/pillar_landmarks/totems/totem_formline/round_2.png
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

# Real pagoda fidelity helpers — imported so palette retint + finish match.
from game.pillar_pagodas import (
    _mix, _shade, _gradient_rect, _aa_polyline, _lit_niche, _tile_hatch,
    _draw_plinth_mist, _is_dark_sky, _is_warming_sky, _cap_lit_for_dark_sky,
    _cap_dark_for_dark_sky, _buddha_eye,
    _cedar, _vermilion, _vermilion_lit, _vermilion_shadow, _lacquer_red,
    _lapis, _bronze, _gold_bright, _stupa_white,
)
from game.draw import draw_side_shrub
from game.pillar_variants import draw_grass_bed

MARGIN = 64                       # matches entities.Pipe eave/ornament gutter
CACHE_W = PIPE_W + MARGIN * 2
CACHE_H = GROUND_Y
PHASE_DAY = 0.30
PHASE_NIGHT = 0.85

_COL_HALF = PIPE_W // 2            # 29 → the load-bearing cedar core half-width


# ── formline paint materials (every one palette-keyed → biome-retinting) ─────
def _cedar_body(palette):
    return _cedar(palette)


def _cedar_lit(palette):
    return _shade(_cedar(palette), 30)


def _cedar_shadow(palette):
    return _shade(_cedar(palette), -34)


def _formline_red(palette):
    # Primary formline red = the temple shu-iro vermilion, anchored in
    # stone_dark so night stays a warm carved-paint red, not cool grey.
    return _vermilion(palette)


def _formline_red_lit(palette):
    return _vermilion_lit(palette)


def _formline_black(palette):
    # The heavy formline black — pushed well below stone_dark so it holds a
    # >=25% VALUE break from the red at every biome phase (colour-blind-safe:
    # the crest reads by value even if red/teal muddy on the night palette).
    return _shade(palette['stone_dark'], -60)


def _formline_teal(palette):
    # Secondary blue-green — the bold THIRD hue. A green-dominant target carries
    # the teal, only lightly warmed by horizon and only lightly diluted by
    # stone_light, so the hue survives the pink/blue night palette instead of
    # collapsing to blue-grey. The green-floor / red-cap guarantees the sample
    # stays g-dominant with real chroma at every biome phase (night included).
    base = _mix((46, 156, 132), palette['horizon'], 0.10)
    c = list(_mix(palette['stone_light'], base, 0.72))
    c[1] = min(255, max(c[1], c[2] + 14))   # green must lead blue → reads teal, not blue-grey
    c[0] = min(c[0], c[1] - 22)             # keep red under green so chroma holds after dark
    return (int(c[0]), int(c[1]), int(c[2]))


def _formline_white(palette):
    return _stupa_white(palette)


def _formline_gilt(palette):
    return _gold_bright(palette)


def _lum(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


# ── geometry helpers ─────────────────────────────────────────────────────────
def _ellipse_pts(rect, n=20):
    cx, cy = rect.centerx, rect.centery
    a, b = rect.w / 2.0, rect.h / 2.0
    return [(cx + a * math.cos(2 * math.pi * i / n),
             cy + b * math.sin(2 * math.pi * i / n)) for i in range(n)]


def _ovoid(surf, rect, fill, outline):
    """The classic Northwest-coast formline ovoid — a fat-topped egg with a
    gently flattened base. Drawn as a filled ellipse squared a touch at the
    bottom, AA-edged so the bold outline reads as a carved paint stroke."""
    pygame.draw.ellipse(surf, fill, rect)
    # Flatten the base so it reads ovoid, not a plain circle.
    pygame.draw.rect(surf, fill,
                     (rect.x + rect.w // 6, rect.centery,
                      rect.w - rect.w // 3, rect.h // 2))
    _aa_polyline(surf, outline, _ellipse_pts(rect), closed=True)


# ── the STAR: one carved + painted formline eye (buddha_eye layered idiom) ───
def _formline_eye(surf, ecx, ecy, ew, eh, palette, *, iris_key='teal'):
    """A bold formline eye built in the exact `_buddha_eye` stacking order —
    white eye-pad → filled ovoid brow → coloured iris → dark keyline — but
    retinted to Northwest-coast paint and wrapped in the fat black ovoid
    socket instead of a stone niche. Lit on the upper-left, shadowed lower-
    right so the painted plane reads as carved relief, not a flat decal."""
    black = _formline_black(palette)
    white = _formline_white(palette)
    dark = palette['stone_dark']
    iris = _formline_teal(palette) if iris_key == 'teal' else _formline_red(palette)

    # Bold black formline ovoid socket (the signature PNW egg) + AA keyline.
    socket = pygame.Rect(ecx - ew // 2, ecy - eh // 2, ew, eh)
    _ovoid(surf, socket, black, _shade(black, -12))

    # White eye-pad inset within the socket.
    pad = socket.inflate(-max(2, ew // 4), -max(2, eh // 4))
    pygame.draw.ellipse(surf, white, pad)
    # Upper-left lit crescent on the pad → the carved highlight.
    pygame.draw.arc(surf, _shade(white, 22), pad.inflate(-1, -1),
                    math.pi * 0.55, math.pi * 1.15, 1)
    # Lower-right cool shadow on the pad.
    pygame.draw.arc(surf, _shade(white, -46), pad.inflate(-1, -1),
                    math.pi * 1.55, math.pi * 1.95, 1)

    # Coloured iris — grown wider (smaller inset) so the hue ring carries the
    # teal, with a pupil shrunk hard so 2–3 px of colour rings it at 1x.
    ir = pad.inflate(-max(2, pad.w // 4), -max(1, pad.h // 5))
    pygame.draw.ellipse(surf, iris, ir)
    # Dark pupil + keyline.
    pygame.draw.ellipse(surf, dark,
                        ir.inflate(-max(3, int(ir.w * 0.62)),
                                   -max(2, int(ir.h * 0.5))))
    _aa_polyline(surf, dark, _ellipse_pts(pad, 16), closed=True)


def _two_dot_eye(surf, ecx, ecy, r, palette):
    """Small-size fallback — the formline eye collapses to a teal dot ringed in
    black so the face still reads as an eye at the 58 px collision column."""
    black = _formline_black(palette)
    teal = _formline_teal(palette)
    pygame.draw.circle(surf, black, (ecx, ecy), r + 1)
    pygame.draw.circle(surf, teal, (ecx, ecy), max(1, r - 1))
    pygame.draw.circle(surf, palette['stone_dark'], (ecx, ecy), max(1, r - 2))


def _formline_brow(surf, ecx, ecy, ew, eh, palette):
    """Heavy black formline brow arch over an eye, inner-lined in red — the
    painted eyebrow that gives the crest its glare."""
    black = _formline_black(palette)
    red = _formline_red(palette)
    top = ecy - eh // 2 - max(2, eh // 3)
    pts = [(ecx - ew // 2 - 1, ecy - eh // 2),
           (ecx - ew // 3, top),
           (ecx + ew // 4, top - 1),
           (ecx + ew // 2 + 1, ecy - eh // 2)]
    pygame.draw.polygon(surf, black, pts)
    _aa_polyline(surf, red, pts[1:3])


def _u_form(surf, cx, y, w, h, palette, col_key='teal'):
    """The formline split-U / crescent used for feathers, ears and joints —
    a filled crescent (outer arc minus inner) drawn as two nested polygons."""
    col = _formline_teal(palette) if col_key == 'teal' else _formline_red(palette)
    black = _formline_black(palette)
    outer = pygame.Rect(cx - w // 2, y, w, h)
    pygame.draw.ellipse(surf, black, outer)
    pygame.draw.ellipse(surf, col, outer.inflate(-3, -3))
    pygame.draw.ellipse(surf, black, (cx - w // 4, y + 2, w // 2, h - 3))


# ── crest-being faces ────────────────────────────────────────────────────────
def _draw_wings(surf, cx, shoulder_y, span, drop, palette):
    """Thunderbird wing-span — two swept paddles flaring into the gutters, each
    ribbed with formline U-feathers and gilt tips. Gutter OVERHANG only: the
    wing roots sit at the column edge, the tips fly past PIPE_W. This is the
    silhouette-tell — the only winged pole in the family."""
    black = _formline_black(palette)
    red = _formline_red(palette)
    gilt = _formline_gilt(palette)
    for sgn in (-1, 1):
        root_x = cx + sgn * (_COL_HALF - 2)
        tip_x = cx + sgn * span
        pts = [(root_x, shoulder_y - drop // 2),
               (root_x, shoulder_y + drop),
               (cx + sgn * int(span * 0.66), shoulder_y + drop - 2),
               (tip_x, shoulder_y - drop),
               (tip_x - sgn * 3, shoulder_y - drop - 4),
               (root_x, shoulder_y - drop // 2 - 3)]
        pygame.draw.polygon(surf, black, pts)
        _aa_polyline(surf, _shade(black, -12), pts, closed=True)
        # Red flight-band + three teal U-feathers stepping to the tip.
        pygame.draw.line(surf, red,
                         (root_x, shoulder_y - 1),
                         (tip_x - sgn * 2, shoulder_y - drop + 3), 2)
        for i in range(3):
            fx = cx + sgn * int(span * (0.42 + i * 0.18))
            fy = shoulder_y - int(drop * (0.1 + i * 0.28))
            _u_form(surf, fx, fy, 8, 6, palette, col_key='teal')
        # Gilt wing-tip.
        pygame.draw.circle(surf, gilt, (tip_x - sgn * 2, shoulder_y - drop), 2)


def _draw_beak(surf, cx, cy, size, palette, *, down=True):
    """A raven/eagle beak — a hooked wedge jutting forward out of the gutter
    (overhang), gilt-lit on the upper ridge with a red nostril and a dark
    hook tip. `down=True` curls it toward the mouth below."""
    black = _formline_black(palette)
    gilt = _formline_gilt(palette)
    red = _formline_red(palette)
    tip = cy + size if down else cy
    pts = [(cx - size // 2, cy - size // 2),
           (cx + size, cy - size // 3),
           (cx + size - 2, cy + size // 3),
           (cx, tip),
           (cx - size // 2, cy + size // 3)]
    pygame.draw.polygon(surf, black, pts)
    _aa_polyline(surf, _shade(black, -12), pts, closed=True)
    # Gilt ridge highlight + red nostril band.
    pygame.draw.line(surf, gilt, (cx - size // 2, cy - size // 2),
                     (cx + size, cy - size // 3), 2)
    pygame.draw.line(surf, red, (cx - size // 3, cy),
                     (cx + size // 2, cy), 1)
    # Dark hook nub at the tip.
    pygame.draw.circle(surf, palette['stone_dark'], (cx, tip), 2)


def _draw_mouth(surf, cx, cy, w, palette, *, teeth=True):
    """A red formline lip band with white teeth (thunderbird/bear) — and a
    recessed `_lit_niche` throat behind it so the maw glows at night."""
    red = _formline_red(palette)
    red_lit = _formline_red_lit(palette)
    white = _formline_white(palette)
    lip = pygame.Rect(cx - w // 2, cy, w, max(4, w // 5))
    # Recessed throat first (free night glow), lips paint over its rim.
    _lit_niche(surf, cx, cy + 1, max(6, w // 2), max(4, w // 4), palette)
    pygame.draw.rect(surf, red, lip)
    pygame.draw.line(surf, red_lit, (lip.x + 1, lip.y),
                     (lip.right - 2, lip.y), 1)
    if teeth and w >= 18:
        n = max(3, w // 7)
        tw = w // (n + 1)
        for i in range(n):
            tx = lip.x + 2 + i * tw
            pygame.draw.rect(surf, white, (tx, lip.y + 1, max(1, tw - 2),
                                           lip.h - 2))


def _draw_nose(surf, cx, cy, w, h, palette):
    """A broad flat formline nose — lit-left / shadow-right relief plane with
    two recessed `_lit_niche` nostrils at the base."""
    black = _formline_black(palette)
    lit = _shade(_cedar(palette), 36)
    shd = _shade(_cedar(palette), -40)
    pts = [(cx - 2, cy - h // 2), (cx + 2, cy - h // 2),
           (cx + w // 2, cy + h // 2), (cx - w // 2, cy + h // 2)]
    pygame.draw.polygon(surf, lit, pts)
    # Right flank shadow.
    pygame.draw.polygon(surf, shd,
                        [(cx + 1, cy - h // 2), (cx + 2, cy - h // 2),
                         (cx + w // 2, cy + h // 2),
                         (cx + w // 2 - 3, cy + h // 2)])
    _aa_polyline(surf, black, pts, closed=True)
    # Recessed nostrils.
    for sgn in (-1, 1):
        _lit_niche(surf, cx + sgn * (w // 4), cy + h // 2 - 3,
                   max(2, w // 6), max(2, h // 4), palette)


def _draw_ears(surf, cx, top_y, palette):
    """Rounded bear ears at the top corners of the face — black formline lobes
    with a teal U-form inner, gutter overhang at the shoulders."""
    for sgn in (-1, 1):
        ex = cx + sgn * (_COL_HALF + 3)
        _u_form(surf, ex, top_y, 12, 12, palette, col_key='teal')


def _draw_crest_face(surf, cx, cy, w, h, palette, kind, idx=0, n=1):
    """One carved + painted crest-being face centred at (cx, cy) inside a band
    w×h. Cedar is the carved wood; formline red/black/teal/white/gilt are the
    paint. Every plane is lit upper-left / shadowed lower-right so the face
    reads as relief. Faces degrade to a 2-dot eye-pair at small pitch. `idx`/`n`
    place the face in the stack so appendage sides alternate and the coloured
    brow band only lands on the terminal crests (no barber-stripe repeat)."""
    black = _formline_black(palette)
    red = _formline_red(palette)
    teal = _formline_teal(palette)

    small = h < 40
    # Painted formline brow band. On a tall stack a full-width red band on EVERY
    # crest reads as barber-stripes, so the coloured band is reserved for the
    # terminal crests (thunderbird crown + the lowest face); interior crests get
    # a darker recessed brow line instead so colour still steps but doesn't repeat.
    band = pygame.Rect(cx - _COL_HALF + 3, cy - h // 2 + 2,
                       (_COL_HALF - 3) * 2, max(3, h // 6))
    terminal = (kind == 'thunderbird') or (idx == 0) or (n <= 3)
    if terminal:
        pygame.draw.rect(surf, red, band)
        pygame.draw.line(surf, _formline_red_lit(palette),
                         (band.x + 1, band.y), (band.right - 2, band.y), 1)
    else:
        pygame.draw.rect(surf, _shade(_cedar(palette), -44),
                         (band.x, band.y + band.h - 2, band.w, 2))
        pygame.draw.line(surf, red, (band.x + 3, band.y + 1),
                         (band.right - 4, band.y + 1), 1)

    ew = max(9, min(20, int(w * 0.34)))
    eh = max(8, int(ew * 0.82))
    eye_y = cy - h // 6
    eye_dx = int(w * 0.24)

    if small:
        # Thumbnail fallback — the two ovoids collapse to a teal-on-black dot
        # pair that still reads as a face at the 58 px column.
        r = max(2, ew // 3)
        _two_dot_eye(surf, cx - eye_dx, eye_y, r, palette)
        _two_dot_eye(surf, cx + eye_dx, eye_y, r, palette)
    else:
        iris = 'teal' if kind != 'raven' else 'red'
        _formline_brow(surf, cx - eye_dx, eye_y, ew, eh, palette)
        _formline_brow(surf, cx + eye_dx, eye_y, ew, eh, palette)
        _formline_eye(surf, cx - eye_dx, eye_y, ew, eh, palette, iris_key=iris)
        _formline_eye(surf, cx + eye_dx, eye_y, ew, eh, palette, iris_key=iris)

    # Kind-specific appendages + lower face.
    if kind == 'thunderbird':
        _draw_wings(surf, cx, cy - h // 2 + max(4, h // 5),
                    _COL_HALF + max(16, int(w * 0.5)),
                    max(10, h // 4), palette)
        if not small:
            _draw_beak(surf, cx, eye_y + eh, max(7, w // 5), palette, down=True)
            _draw_mouth(surf, cx, cy + h // 3, int(w * 0.6), palette, teeth=True)
    elif kind == 'bear':
        _draw_ears(surf, cx, cy - h // 2 + max(4, h // 6), palette)
        if not small:
            _draw_nose(surf, cx, eye_y + eh, max(10, w // 3),
                       max(6, h // 6), palette)
            _draw_mouth(surf, cx, cy + h // 3, int(w * 0.62), palette, teeth=True)
    else:  # raven
        # Long forward beak = gutter overhang; face carries the centre column.
        # Beak side alternates per stack index and reaches well past the column
        # so mid sections cut a stronger stepped silhouette in the blackout.
        if not small:
            side = -1 if idx % 2 == 0 else 1
            _draw_beak(surf, cx + side * (_COL_HALF - 6), eye_y + 2,
                       max(14, int(w * 0.5)), palette, down=True)
            # Folded wing U-forms flanking the face.
            _u_form(surf, cx - eye_dx, cy + h // 4, 10, 8, palette, col_key='teal')
            _u_form(surf, cx + eye_dx, cy + h // 4, 10, 8, palette, col_key='teal')
            _draw_mouth(surf, cx, cy + h // 3, int(w * 0.5), palette, teeth=False)


# ── tower assembly ───────────────────────────────────────────────────────────
def _draw_tower_upright(surf, cx, y_top, y_bottom, palette, seed):
    """Draw the totem upright — plinth at y_bottom, thunderbird crown at the
    gap end (y_top). A continuous cedar core fills the whole PIPE_W column; the
    crest faces + wings paint on top. Callers flip the surface for the ceiling
    section."""
    sect_h = y_bottom - y_top
    if sect_h < 8:
        return

    cedar = _cedar_body(palette)
    c_lit = _cap_lit_for_dark_sky(_cedar_lit(palette), palette)
    c_shd = _cap_dark_for_dark_sky(_cedar_shadow(palette), palette)
    black = _formline_black(palette)
    gilt = _formline_gilt(palette)

    plinth_h = max(5, min(11, int(sect_h * 0.055)))
    body_top = y_top
    body_bottom = y_bottom - plinth_h
    body_h = body_bottom - body_top

    # 1) CONTINUOUS cedar core — the load-bearing full-column fill (left-lit).
    core = pygame.Rect(cx - _COL_HALF, body_top, PIPE_W, body_h)
    _gradient_rect(surf, core, c_lit, cedar, c_shd)
    # Carved edge keylines: lit left, dark right — the pole's rounded volume.
    pygame.draw.line(surf, _shade(c_lit, 18),
                     (core.x, body_top), (core.x, body_bottom), 1)
    pygame.draw.line(surf, black,
                     (core.right - 1, body_top), (core.right - 1, body_bottom), 1)

    # 2) Height-adaptive crest COUNT keyed off a natural face height (~72 px):
    #    one big thunderbird at ~70 px, a tall stack toward ~355 px.
    face_target = 72
    n = max(1, int(round(body_h / face_target)))
    pitch = body_h / n
    kinds_cycle = ['bear', 'raven']

    for i in range(n):
        band_top = body_bottom - pitch * (i + 1)
        band_bot = body_bottom - pitch * i
        fcy = int((band_top + band_bot) / 2)
        # Carved seam between stacked crests — a drop-shadow keyline + lit lip.
        if i < n - 1:
            sy = int(band_top)
            pygame.draw.line(surf, _shade(cedar, -46),
                             (cx - _COL_HALF + 1, sy),
                             (cx + _COL_HALF - 1, sy), 2)
            pygame.draw.line(surf, _shade(c_lit, 12),
                             (cx - _COL_HALF + 1, sy + 2),
                             (cx + _COL_HALF - 1, sy + 2), 1)
        kind = 'thunderbird' if i == n - 1 else kinds_cycle[i % len(kinds_cycle)]
        _draw_crest_face(surf, cx, fcy, PIPE_W, int(pitch), palette, kind,
                         idx=i, n=n)

    # 3) Thunderbird finial crown at the gap-end rim — a solid gilt-tipped
    #    head-plate so the collision column stays filled to the tip, with a
    #    night rim so the crown carries the silhouette after dark.
    crown_h = max(4, min(9, int(sect_h * 0.03)))
    # Full-PIPE_W cap so the gap-end rim is flush corner-to-corner (no
    # transparent gutter notches); the inner red keeps its own black border.
    crown = pygame.Rect(cx - _COL_HALF, body_top - crown_h,
                        PIPE_W, crown_h + 2)
    pygame.draw.rect(surf, black, crown)
    pygame.draw.rect(surf, _formline_red(palette),
                     (crown.x + 2, crown.y + 1, crown.w - 4, crown.h - 2))
    pygame.draw.circle(surf, gilt, (cx, body_top - crown_h + 1), 2)
    if _is_dark_sky(palette):
        rim = pygame.Surface((crown.w + 6, crown.h + 6), pygame.SRCALPHA)
        rimc = _mix(palette['stone_accent'], (255, 215, 120), 0.8)
        pygame.draw.rect(rim, (*rimc, 90), (0, 0, crown.w + 6, crown.h + 6), 2)
        surf.blit(rim, (crown.x - 3, crown.y - 3),
                  special_flags=pygame.BLEND_RGBA_ADD)

    # 4) Three-layer plinth + mist + ground foliage (pagoda idiom).
    _draw_plinth_mist(surf, cx, y_bottom, int(PIPE_W * 2.2), palette)
    pl_w = int(PIPE_W * 1.22)
    ply = y_bottom - plinth_h
    pygame.draw.rect(surf, _shade(palette['stone_dark'], -12),
                     (cx - pl_w // 2, ply, pl_w, plinth_h))
    pygame.draw.rect(surf, _mix(palette['stone_mid'], (150, 142, 130), 0.5),
                     (cx - pl_w // 2 + 1, ply + 1, pl_w - 2, plinth_h - 2))
    pygame.draw.rect(surf, palette['stone_light'],
                     (cx - pl_w // 2, ply, pl_w, 1))
    # A row of formline tile-ends on the plinth face → carved base band.
    _tile_hatch(surf, cx - pl_w // 2 + 3, ply + plinth_h - 2,
                cx + pl_w // 2 - 3, ply + plinth_h - 2,
                _formline_red(palette), step=4)
    if sect_h > 60:
        draw_side_shrub(surf, cx - pl_w // 2 - 2, y_bottom - 2, palette, scale=0.9)
        draw_side_shrub(surf, cx + pl_w // 2 + 2, y_bottom - 2, palette, scale=0.9)
        draw_grass_bed(surf, cx, y_bottom - 1, PIPE_W + 10, 16, palette, seed=seed)


def candidate_totem_formline(surf, top_rect, bot_rect, palette, seed):
    """Bottom totem rises from the ground with the thunderbird crown at the
    gap; the top is the same builder flipped vertically — a symmetric two-ended
    painted pole hung from the ceiling, its thunderbird pointing into the gap."""
    if bot_rect.height > 0:
        _draw_tower_upright(surf, bot_rect.centerx, bot_rect.y, bot_rect.bottom,
                            palette, seed)
    if top_rect.height > 0:
        tmp = pygame.Surface((surf.get_width(), top_rect.height), pygame.SRCALPHA)
        _draw_tower_upright(tmp, top_rect.centerx, 0, top_rect.height,
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


def _hero(pal, seed):
    gap_y, gap_h = 250, 150
    top_h = int(gap_y - gap_h / 2)
    bot_top = int(gap_y + gap_h / 2)
    full = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    top_rect = pygame.Rect(MARGIN, 0, PIPE_W, top_h)
    bot_rect = pygame.Rect(MARGIN, bot_top, PIPE_W, GROUND_Y - bot_top)
    candidate_totem_formline(full, top_rect, bot_rect, pal, seed=seed)
    tip_y = 0
    base_y = GROUND_Y + 8
    hero = _bg(CACHE_W, base_y, pal, GROUND_Y)
    hero.blit(full, (0, 0))
    for ex in (MARGIN, MARGIN + PIPE_W):
        pygame.draw.line(hero, (230, 60, 60), (ex, 0), (ex, base_y), 1)
    return hero, base_y


def _closeup(pal, seed, scale=3):
    """Zoom on a single BEAR/RAVEN crest close-up so the carved painted face is
    judgeable, drawn from the bottom builder at full section height."""
    surf = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    bot_rect = pygame.Rect(MARGIN, 250, PIPE_W, GROUND_Y - 250)
    top_rect = pygame.Rect(MARGIN, 0, PIPE_W, 0)
    candidate_totem_formline(surf, top_rect, bot_rect, pal, seed=seed)
    # Crop the two lowest crest faces (widest, most detailed).
    crop_h = 150
    crop_y = GROUND_Y - 12 - crop_h
    crop = pygame.Surface((CACHE_W, crop_h))
    crop.blit(_bg(CACHE_W, crop_h, pal, crop_h), (0, 0))
    crop.blit(surf, (0, -crop_y))
    for ex in (MARGIN, MARGIN + PIPE_W):
        pygame.draw.line(crop, (230, 60, 60), (ex, 0), (ex, crop_h), 1)
    return pygame.transform.scale(
        crop, (crop.get_width() * scale, crop.get_height() * scale))


def _ceiling_closeup(pal, seed, scale=3):
    """Zoom on the flipped CEILING section so the symmetric two-ended totem's
    upside-down crest is judgeable at scale (FIX 3 non-creepy verification)."""
    surf = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    # A tall ceiling pillar hanging from the top; leave the bottom empty.
    top_rect = pygame.Rect(MARGIN, 0, PIPE_W, 220)
    bot_rect = pygame.Rect(MARGIN, GROUND_Y, PIPE_W, 0)
    candidate_totem_formline(surf, top_rect, bot_rect, pal, seed=seed)
    # Crop the two crests nearest the ceiling anchor (the most flipped detail).
    crop_h = 150
    crop = pygame.Surface((CACHE_W, crop_h))
    crop.blit(_bg(CACHE_W, crop_h, pal, 0), (0, 0))
    crop.blit(surf, (0, -8))
    for ex in (MARGIN, MARGIN + PIPE_W):
        pygame.draw.line(crop, (230, 60, 60), (ex, 0), (ex, crop_h), 1)
    return pygame.transform.scale(
        crop, (crop.get_width() * scale, crop.get_height() * scale))


def _blackout(pal, seed):
    """58 px BLACKOUT thumbnail — solid silhouette at true game scale so the
    winged zig-zag reads apart from every straight-pole concept."""
    surf = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    bot_rect = pygame.Rect(MARGIN, 220, PIPE_W, GROUND_Y - 220)
    top_rect = pygame.Rect(MARGIN, 0, PIPE_W, 0)
    candidate_totem_formline(surf, top_rect, bot_rect, pal, seed=seed)
    w, h = surf.get_width(), GROUND_Y - 210
    out = pygame.Surface((w, h))
    out.fill((232, 232, 236))
    for x in range(w):
        for y in range(h):
            if surf.get_at((x, 210 + y))[3] > 30:
                out.set_at((x, y), (18, 18, 22))
    return out


def main():
    pal = biome.palette_for_phase(PHASE_DAY)
    pal_n = biome.palette_for_phase(PHASE_NIGHT)

    # ── FIX 1 proof: red vs black VALUE separation (>=25%) on both palettes,
    #    plus day != night body colour (proves the palette retint sweeps). ──
    def _chroma(c):
        return max(c[:3]) - min(c[:3])

    def report(name, p):
        red = _formline_red(p)
        blk = _formline_black(p)
        teal = _formline_teal(p)
        cedar = _cedar_body(p)
        dv = abs(_lum(red) - _lum(blk)) / max(1.0, _lum(red)) * 100
        gdom = teal[1] == max(teal[:3])
        print(f"  {name}: red={red} L={_lum(red):.0f}  black={blk} L={_lum(blk):.0f}"
              f"  red-vs-black valDelta={dv:.0f}%  cedar={cedar}")
        print(f"         teal={teal}  chroma={_chroma(teal)}  g-dominant={gdom} "
              f"[{'OK' if (gdom and _chroma(teal) > 25) else 'FAIL'}]")
        return cedar
    print("MATERIAL VALUE / RETINT PROOF")
    cedar_day = report("DAY  ", pal)
    cedar_night = report("NIGHT", pal_n)
    print(f"  day cedar {cedar_day} != night cedar {cedar_night}: "
          f"{cedar_day != cedar_night}")

    # ── EYE PROBE: sample the RENDERED iris ring so the teal is proven on the
    #    painted face (not just in the material fn) for DAY and NIGHT. ──
    print("EYE PROBE — dominant teal actually painted in the iris ring")
    for name, p in (("DAY  ", pal), ("NIGHT", pal_n)):
        probe = pygame.Surface((120, 120), pygame.SRCALPHA)
        _formline_eye(probe, 60, 60, 40, 34, p, iris_key='teal')
        # Sample a ring band around the pupil (between pupil and pad edge).
        samples = []
        for ang in range(0, 360, 10):
            rx = int(60 + 12 * math.cos(math.radians(ang)))
            ry = int(60 + 10 * math.sin(math.radians(ang)))
            px = probe.get_at((rx, ry))
            if px[3] > 0:
                samples.append(px)
        # Most-saturated teal-ish sample (green-dominant, chroma high).
        teals = [s for s in samples if s[1] == max(s[:3])]
        best = max(teals or samples, key=lambda s: _chroma(s))
        gdom = best[1] == max(best[:3])
        print(f"  {name}: iris-ring teal={tuple(best[:3])}  chroma={_chroma(best)}"
              f"  g-dominant={gdom} "
              f"[{'OK' if (gdom and _chroma(best) > 25) else 'FAIL'}]")

    hero_day, hd_h = _hero(pal, 7)
    hero_night, hn_h = _hero(pal_n, 7)
    close = _closeup(pal, 7)
    ceil = _ceiling_closeup(pal, 7)
    black_thumb = _blackout(pal, 7)

    # ── FEASIBILITY strip at 70 / 210 / 355 ──
    strip_heights = [70, 210, 355]
    strips = []
    print("FILL GATE (max empty vertical run inside the 58px PIPE_W band)")
    for h in strip_heights:
        s = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
        br = pygame.Rect(MARGIN, GROUND_Y - h, PIPE_W, h)
        tr = pygame.Rect(MARGIN, 0, PIPE_W, 0)
        candidate_totem_formline(s, tr, br, pal, seed=7)
        run = _max_empty_run(s, MARGIN, MARGIN + PIPE_W, GROUND_Y - h, GROUND_Y)
        crop = pygame.Surface((CACHE_W, h + 8))
        crop.blit(_bg(CACHE_W, h + 8, pal, h), (0, 0))
        crop.blit(s, (0, -(GROUND_Y - h)))
        for ex in (MARGIN, MARGIN + PIPE_W):
            pygame.draw.line(crop, (230, 60, 60), (ex, 0), (ex, h + 8), 1)
        strips.append((h, crop, run))
        print(f"  h={h:3d}  max empty run = {run}px  [{'OK' if run <= 12 else 'FAIL'}]")

    # top-crest clearance: verify solid pixels at the gap-end rim row.
    probe = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    br = pygame.Rect(MARGIN, 250, PIPE_W, GROUND_Y - 250)
    candidate_totem_formline(probe, pygame.Rect(MARGIN, 0, PIPE_W, 0), br, pal, 7)
    rim_solid = sum(1 for x in range(MARGIN, MARGIN + PIPE_W)
                    if probe.get_at((x, 250 - 6))[3] > 0)
    print(f"TOP-CREST rim clearance: {rim_solid}/{PIPE_W} px solid above gap rim")

    # ── compose the sheet ──
    pad, label_h, head_h = 12, 24, 62
    title = pygame.font.SysFont(None, 30)
    sub = pygame.font.SysFont(None, 18)
    lab = pygame.font.SysFont(None, 19)

    col_w = CACHE_W
    strips_total_h = sum(c.get_height() + label_h + pad for _, c, _ in strips)
    col_h = max(hd_h + label_h, hn_h + label_h, strips_total_h,
                close.get_height() + ceil.get_height() + label_h * 2 + pad,
                black_thumb.get_height() + label_h)
    sheet_w = pad + col_w * 3 + close.get_width() + black_thumb.get_width() + pad * 5
    sheet_h = head_h + col_h + pad * 2
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((24, 25, 30))

    sheet.blit(title.render(
        "totem_formline — painted Pacific-NW cedar totem  ·  round_2",
        True, (245, 240, 230)), (pad, 12))
    sheet.blit(sub.render(
        "red edges = PIPE_W (58px) collision band  ·  thunderbird crown + "
        "bear/raven crests  ·  formline red/black/teal on cedar  ·  wings/beaks "
        "= gutter overhang", True, (170, 172, 182)), (pad, 40))

    x, y = pad, head_h
    sheet.blit(hero_day, (x, y))
    pygame.draw.rect(sheet, (60, 62, 72), (x, y, col_w, hd_h), 1)
    sheet.blit(lab.render("HERO — DAY (phase 0.30)", True, (255, 224, 150)),
               (x, y + hd_h + 4))

    x += col_w + pad
    sheet.blit(hero_night, (x, y))
    pygame.draw.rect(sheet, (60, 62, 72), (x, y, col_w, hn_h), 1)
    sheet.blit(lab.render("HERO — NIGHT (phase 0.85)", True, (255, 224, 150)),
               (x, y + hn_h + 4))

    x += col_w + pad
    sy = head_h
    sheet.blit(lab.render("FILL — bottom section", True, (255, 224, 150)),
               (x, sy - 20))
    for h, crop, run in strips:
        sheet.blit(crop, (x, sy))
        pygame.draw.rect(sheet, (60, 62, 72), (x, sy, col_w, crop.get_height()), 1)
        ok = "OK" if run <= 12 else "FAIL"
        sheet.blit(lab.render(f"h={h}px · run {run}px [{ok}]", True,
                              (200, 235, 170) if run <= 12 else (255, 140, 140)),
                   (x, sy + crop.get_height() + 4))
        sy += crop.get_height() + label_h + pad

    x += col_w + pad
    sheet.blit(close, (x, head_h))
    pygame.draw.rect(sheet, (60, 62, 72),
                     (x, head_h, close.get_width(), close.get_height()), 1)
    sheet.blit(lab.render("CLOSE-UP 3x — carved painted faces (upright)", True,
                          (255, 224, 150)), (x, head_h + close.get_height() + 4))
    # Ceiling close-up stacked below → FIX 3 non-creepy verification.
    cy2 = head_h + close.get_height() + label_h + pad
    sheet.blit(ceil, (x, cy2))
    pygame.draw.rect(sheet, (60, 62, 72),
                     (x, cy2, ceil.get_width(), ceil.get_height()), 1)
    sheet.blit(lab.render("CEILING 3x — flipped two-ended crest (FIX 3)", True,
                          (255, 224, 150)), (x, cy2 + ceil.get_height() + 4))

    x += close.get_width() + pad
    sheet.blit(black_thumb, (x, head_h))
    pygame.draw.rect(sheet, (60, 62, 72),
                     (x, head_h, black_thumb.get_width(),
                      black_thumb.get_height()), 1)
    sheet.blit(lab.render("58px BLACKOUT (winged tell)", True, (255, 224, 150)),
               (x, head_h + black_thumb.get_height() + 4))

    out = pathlib.Path(__file__).resolve().parent / "round_2.png"
    pygame.image.save(sheet, out)
    print(f"wrote {out}  ({sheet.get_width()}x{sheet.get_height()})")


if __name__ == "__main__":
    main()
