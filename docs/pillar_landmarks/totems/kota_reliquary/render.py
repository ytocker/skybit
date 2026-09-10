"""kota_reliquary — the METAL totem: a hammered brass/copper Kota (Bakota)
reliquary guardian, stacked as gleaming ancestor masks (standalone candidate).

The one non-earthen tower in the family. Each mbulu-ngulu unit is a dished
OVAL face plate sheathed in sheet brass, crowned by a half-moon CRESCENT with
lateral cheek-wings, seated on an OPEN LOZENGE (diamond) frame body — the only
concept whose body is an open frame, not a solid pole. The read is "a shining
brass mask on a diamond": oval-and-crescent over a diamond, a rounded T/anchor
silhouette found nowhere else in the set. The metal itself is the distinctness
as much as the shape, so every plate carries a strong hammered SPECULAR (a
bright vertical glint + a dark shadow flank) that reads reflective, not flat
gold, and self-glows as the night landmark without a niche.

Open-frame hollow — SOLVED. An open diamond would leave a killzone in the ~58px
collision column. So a full-height recessed BACK-PLATE (a dark shrine-interior
`_gradient_rect`, the dark wood core the Kota brass is historically tacked onto)
spans the whole PIPE_W band top-to-bottom BEFORE any metal lands; the lozenge
interiors are darkened a second step into true shadow-boxes so the diamond reads
as a window into depth rather than a hole. The brass struts live inside the band;
only the outer diamond points and cheek-wings overhang the gutters. Net result:
the central column is continuous by construction (max empty run 0px) at every
section height, and the frame still reads open because the metal on top is open.

Mirror: a symmetric two-ended reliquary. Both sections root a 3-layer plinth at
the world edge and aim their crescent finial into the gap; the top section is a
true vertical flip. The oval-and-crescent mask is near-vertically-symmetric so
the flip stays a totem, not an upside-down face.

Height-adaptive: fewer stacked masks and dropped lozenge cells as the section
shortens; at ~70px a single crescent+oval hero mask fills the stub (lozenge
dropped first, exactly as the brainstorm proposed).

Standalone review script — it IMPORTS the real pagoda/pillar draw helpers so the
exploration shares the shipped palette + primitive language, but does NOT modify
any game module. (draw_side_shrub lives in game.draw, not pillar_variants, so it
is sourced from its true home; everything else is imported as briefed.)

Run:  python docs/pillar_landmarks/totems/kota_reliquary/render.py
Out:  docs/pillar_landmarks/totems/kota_reliquary/round_2.png
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

# Real pagoda-family primitives — shared shading, niche-glow, plinth mist, and
# the buddha-eye construction the metal eye is derived from.
from game.pillar_pagodas import (
    _mix, _shade, _gradient_rect, _aa_polyline, _lit_niche, _tile_hatch,
    _draw_plinth_mist, _is_dark_sky, _is_warming_sky, _cap_lit_for_dark_sky,
    _cap_dark_for_dark_sky, _buddha_eye, _bronze, _gold_bright, _gold_deep,
)
from game.pillar_variants import draw_grass_bed, draw_spiral_glow
from game.draw import draw_side_shrub

MARGIN = 64                        # matches entities.Pipe eave/ornament gutter
CACHE_W = PIPE_W + MARGIN * 2
CACHE_H = GROUND_Y
PHASE_DAY = 0.30                   # brass reads warm against the tan day sky
PHASE_NIGHT = 0.85                 # NIGHT keyframe — must show the metal glint

_HALF = PIPE_W // 2                # 29 — half the collision band
_FACE_HALF = 25                    # oval face half-width — inside the 58 band
_CHEEK_HALF = 40                   # cheek-wing crescent tip — gutter overhang
_LOZ_HALF = 39                     # lozenge horizontal point — gutter overhang
# The bright crescent finial reads as bridging the flyway if it sits flush on
# the rim, so the ornament (and the metal it caps) starts a few px below it. The
# tiny empty run this leaves at the very rim stays well inside the ≤12px fill
# tolerance — no killzone — while giving the gap edge visible air.
RIM_AIR = 3


# ── metal material palette (all palette-anchored → biome retint sweeps through)
def _materials(palette):
    """Six-plus named metal tones + the recessed back-plate wood core. Brass is
    routed through stone_accent (`_gold_deep`/`_bronze`) so the tower is the
    all-accent night landmark; copper warms toward red; the shadow-box + core
    are deep stone_dark. Lit tones are dusk/night-capped so the glint reads as a
    bright specular instead of a blown-out white slab once the sun sets."""
    brass = _mix(palette['stone_accent'], (198, 164, 86), 0.70)
    brass_lit = _cap_lit_for_dark_sky(_gold_bright(palette), palette, cap=232)
    # The hammered GLINT — a near-white specular so sheet brass reads reflective.
    brass_hi = _cap_lit_for_dark_sky(
        _mix(_gold_bright(palette), (255, 250, 232), 0.42), palette, cap=244)
    brass_deep = _gold_deep(palette)
    brass_shadow = _cap_dark_for_dark_sky(_shade(_bronze(palette), -34), palette)
    copper = _mix(palette['stone_accent'], (176, 104, 66), 0.66)
    copper_lit = _mix(palette['stone_accent'], (214, 148, 96), 0.62)
    bronze = _bronze(palette)
    # Recessed shrine interior + the darker shadow-box inside each lozenge, and
    # the dark wood core peeking behind the brass mask (Kota brass on wood).
    back_mid = _cap_dark_for_dark_sky(_shade(palette['stone_dark'], -22), palette,
                                      floor=26)
    back_dark = _cap_dark_for_dark_sky(_shade(palette['stone_dark'], -40), palette,
                                       floor=18)
    wood_core = _mix(palette['stone_dark'], (78, 48, 32), 0.78)
    return dict(brass=brass, brass_lit=brass_lit, brass_hi=brass_hi,
                brass_deep=brass_deep, brass_shadow=brass_shadow,
                copper=copper, copper_lit=copper_lit, bronze=bronze,
                back_mid=back_mid, back_dark=back_dark, wood_core=wood_core)


def _warm_clamp_night(surf, x0, x1, y0, y1, *, cap=244):
    """Composited-highlight guard for the NIGHT keyframe. The additive amber
    breath-glows (mouth niches, plinth mist, finial spiral) stack over already
    bright brass and blow OUT to neutral (255,255,255) — a cool sparkle-field in
    motion, not warm metal. So every painted pixel in the tower band gets each
    channel pulled to <= cap, and any near-neutral hot pixel is re-biased to
    GOLD (blue then green pulled below red) so the sheen stays warm brass and no
    pixel is ever pure white. Runs once per cached tower, so the per-pixel loop
    is pygbag-safe (no per-frame cost)."""
    x0 = max(0, x0); y0 = max(0, y0)
    x1 = min(surf.get_width(), x1); y1 = min(surf.get_height(), y1)
    for x in range(x0, x1):
        for y in range(y0, y1):
            r, g, b, a = surf.get_at((x, y))
            if a == 0:
                continue
            if max(r, g, b) <= cap and not (min(r, g, b) >= 205):
                continue
            r = min(r, cap); g = min(g, cap); b = min(b, cap)
            if min(r, g, b) >= 205:                # near-neutral hot → force gold
                b = min(b, int(r * 0.62))
                g = min(g, int(r * 0.88))
            surf.set_at((x, y), (r, g, b, a))


def _arc_pts(cx, cy, rw, rh, a0, a1, n=20):
    return [(cx + rw * math.cos(a0 + (a1 - a0) * i / (n - 1)),
             cy + rh * math.sin(a0 + (a1 - a0) * i / (n - 1))) for i in range(n)]


# ── signature primitives ─────────────────────────────────────────────────────
def _dished_oval(surf, cx, cy, rw, rh, m):
    """A convex brass face plate: a radial (center-lit dome) gradient built from
    nested offset ellipses — dark rim → lit crown — then a strong vertical
    specular glint and a dark shadow flank so it reads as a reflective hammered
    sheet, not a flat gold blob. AA keyline on the outer oval."""
    steps = 11
    for i in range(steps):
        t = i / (steps - 1)                         # 0 outer rim → 1 lit crown
        col = _mix(m['brass_shadow'], m['brass_lit'], t)
        ew = max(2, int(rw * 2 * (1 - 0.86 * t)))
        eh = max(2, int(rh * 2 * (1 - 0.86 * t)))
        ox = cx - int(rw * 0.20 * t)                # crown drifts up-left → dome
        oy = cy - int(rh * 0.22 * t)
        pygame.draw.ellipse(surf, col, (ox - ew // 2, oy - eh // 2, ew, eh))
    # Bright vertical specular glint just left of centre — the "hammered sheen".
    gw = max(3, rw // 3)
    pygame.draw.ellipse(surf, m['brass_hi'],
                        (cx - int(rw * 0.30) - gw // 2, cy - int(rh * 0.5),
                         gw, rh))
    # Dark reflective shadow flank down the right cheek.
    pygame.draw.ellipse(surf, m['brass_shadow'],
                        (cx + int(rw * 0.42), cy - int(rh * 0.5),
                         max(2, rw // 4), rh))
    # Redraw the domed crown thinly so the flank doesn't eat the highlight.
    pygame.draw.ellipse(surf, _mix(m['brass'], m['brass_lit'], 0.6),
                        (cx - int(rw * 0.55), cy - int(rh * 0.6),
                         int(rw * 0.7), int(rh * 0.7)))
    _aa_polyline(surf, m['brass_deep'],
                 _arc_pts(cx, cy, rw, rh, 0, 2 * math.pi, 28), closed=True)


def _crescent(surf, cx, cy, rw, rh, m, *, bite=0.82, rivets=0):
    """A hammered half-moon lunette: filled brass ellipse with the lower centre
    carved away by the recessed back tone (this sits over the back-plate, so the
    bite reads as depth). Specular runs the top arc, shadow the underside, an AA
    keyline traces the outer arc, and optional copper tack-rivets stipple it."""
    pygame.draw.ellipse(surf, m['brass_shadow'],
                        (cx - rw - 1, cy - rh - 1, 2 * rw + 2, 2 * rh + 2))
    pygame.draw.ellipse(surf, m['brass'], (cx - rw, cy - rh, 2 * rw, 2 * rh))
    # Specular band hugging the top arc; shadow smear along the lower inner arc.
    pygame.draw.ellipse(surf, m['brass_hi'],
                        (cx - int(rw * 0.78), cy - int(rh * 0.94),
                         int(rw * 1.56), max(2, int(rh * 0.5))))
    # Carve the crescent bite from below.
    br = int(rw * bite)
    bh = int(rh * (bite + 0.06))
    pygame.draw.ellipse(surf, m['back_mid'],
                        (cx - br, cy - bh + int(rh * 0.62), 2 * br, 2 * bh))
    _aa_polyline(surf, m['brass_deep'],
                 _arc_pts(cx, cy, rw, rh, math.pi, 2 * math.pi, 22))
    # Copper tack-rivets — sparse specular sparkle, NOT a texture field.
    for k in range(rivets):
        a = math.pi + (k + 0.5) / rivets * math.pi
        px = int(cx + rw * 0.82 * math.cos(a))
        py = int(cy + rh * 0.82 * math.sin(a))
        pygame.draw.circle(surf, m['copper'], (px, py), 1)
        surf.set_at((px, py - 1), m['brass_hi'])


def _metal_eye(surf, cx, cy, m, scale=1.0):
    """The Kota lozenge eye — the `_buddha_eye` construction retinted to metal:
    a lit brass eye-pad → a copper upper-eyelid brow crescent (the Kota copper
    eyelid) → a dark inset lozenge iris → a bronze keyline. Collapses to a bold
    2-dot fallback below the readable-almond scale so the face still reads at the
    58px column."""
    w = int(7 * scale)
    h = int(4 * scale)
    if w < 4 or h < 3:                              # 58px fallback: 2 dark dots
        pygame.draw.circle(surf, m['back_dark'], (cx, cy), 2)
        surf.set_at((cx - 1, cy - 1), m['brass_hi'])
        return
    pad = pygame.Rect(cx - w, cy - h // 2, w * 2, h)
    pygame.draw.ellipse(surf, _mix(m['brass'], m['brass_lit'], 0.7), pad)   # lit pad
    # Dark inset lozenge iris (Kota eyes are lozenge/coffee-bean, not round).
    iris = [(cx - int(w * 0.7), cy), (cx, cy - h // 2 + 1),
            (cx + int(w * 0.7), cy), (cx, cy + h // 2 - 1)]
    pygame.draw.polygon(surf, m['back_dark'], iris)
    surf.set_at((cx - 1, cy - 1), m['brass_hi'])                            # catch-light
    # Copper upper-eyelid brow crescent above the pad.
    brow = [(cx - w, cy - h // 2), (cx - w + 2, cy - h),
            (cx, cy - h - 1), (cx + w - 2, cy - h), (cx + w, cy - h // 2)]
    pygame.draw.lines(surf, m['copper'], False, brow, 1)
    pygame.draw.aalines(surf, m['bronze'], False,
                        _arc_pts(cx, cy, w, h * 0.9, math.pi, 2 * math.pi, 12))


def _lozenge_cell(surf, cx, y_top, y_bot, m, palette):
    """An OPEN diamond frame linking one mask to the next. The interior is
    darkened to a shadow-box a second step below the back-plate (reads as a
    window into depth); four brass struts trace the diamond with a lit top-left
    edge + dark bottom-right, copper tack-rivets at the mid-joints, and only the
    outer L/R points overhang the gutters — the struts stay inside the band."""
    cyy = (y_top + y_bot) // 2
    hh = (y_bot - y_top) // 2
    if hh < 6:
        return
    outer = [(cx, y_top), (cx + _LOZ_HALF, cyy), (cx, y_bot), (cx - _LOZ_HALF, cyy)]
    inner_h = int(hh * 0.62)
    inner_w = int(_LOZ_HALF * 0.62)
    inner = [(cx, cyy - inner_h), (cx + inner_w, cyy),
             (cx, cyy + inner_h), (cx - inner_w, cyy)]
    # Recessed shadow-box interior (a step darker than the back-plate).
    pygame.draw.polygon(surf, m['back_dark'], inner)
    # A faint domed glimmer at the box centre so it reads as concave depth.
    pygame.draw.polygon(surf, _mix(m['back_dark'], m['brass_shadow'], 0.30),
                        [(cx, cyy - inner_h // 2), (cx + inner_w // 2, cyy),
                         (cx, cyy + inner_h // 2), (cx - inner_w // 2, cyy)])
    # Four brass struts (outer diamond minus inner void), lit/shadow per edge.
    quad = [outer[0], outer[1], inner[1], inner[0]]           # top-right strut
    pygame.draw.polygon(surf, _mix(m['brass'], m['brass_lit'], 0.5), quad)
    pygame.draw.polygon(surf, _mix(m['brass'], m['brass_lit'], 0.75),
                        [outer[3], outer[0], inner[0], inner[3]])  # top-left (lit)
    pygame.draw.polygon(surf, m['brass'],
                        [outer[1], outer[2], inner[2], inner[1]])  # bot-right
    pygame.draw.polygon(surf, m['brass_deep'],
                        [outer[2], outer[3], inner[3], inner[2]])  # bot-left (dark)
    _aa_polyline(surf, m['brass_deep'], outer, closed=True)
    _aa_polyline(surf, m['brass_shadow'], inner, closed=True)
    # Copper tack-rivets at the four cardinal joints — sparse specular.
    for px, py in outer:
        pygame.draw.circle(surf, m['copper'], (int(px), int(py)), 1)


def _draw_mask(surf, cx, u_top, u_bot, m, palette, *, with_lozenge, crown):
    """One reliquary mask cell: crescent coiffure + cheek-wings + dished oval
    face + eyes/nose/mouth, and (when tall enough) an open lozenge body below.
    `crown` adds the wide half-moon lunette that caps the gap end."""
    unit_h = u_bot - u_top
    face_frac = 0.56 if with_lozenge else 0.92
    face_h = int(unit_h * face_frac)
    face_cy = u_top + face_h // 2
    rw = _FACE_HALF
    rh = max(8, int(face_h * 0.46))

    # Cheek-wing crescents flank the face (gutter overhang, curving inward).
    cheek_rw = int(_CHEEK_HALF * 0.5)
    cheek_rh = max(6, int(rh * 0.85))
    for sgn in (-1, 1):
        _crescent(surf, cx + sgn * (rw + cheek_rw - 6), face_cy,
                  cheek_rw, cheek_rh, m, bite=0.7, rivets=1)

    # The wide crown lunette caps the top mask. Non-crown masks DROP the small
    # coiffure crescent so the four brass features (coiffure + 2 cheeks + dish +
    # lunette) never merge into one amorphous blob in a ~58px cell — the cheek
    # wings + dished oval carry the stacked masks, and the crescent read is
    # spent where it counts: the crown and the finial.
    if crown:
        _crescent(surf, cx, u_top + max(6, unit_h // 8),
                  int(_CHEEK_HALF * 1.08), max(9, int(unit_h * 0.13)),
                  m, bite=0.86, rivets=5)

    # The dished brass face — the hero surface.
    _dished_oval(surf, cx, face_cy, rw, rh, m)

    # Eyes (retinted buddha-eye), ridge nose, breath-glow mouth niche.
    eye_scale = rw / 22.0
    ey = face_cy - int(rh * 0.12)
    for sgn in (-1, 1):
        _metal_eye(surf, cx + sgn * int(rw * 0.44), ey, m, scale=eye_scale)
    # Ridge nose — a lit brass wedge with a shadowed right flank.
    if rh >= 12:
        n_top, n_bot = ey + int(rh * 0.18), face_cy + int(rh * 0.5)
        pygame.draw.polygon(surf, m['brass_hi'],
                            [(cx - 2, n_top), (cx + 1, n_top),
                             (cx + 3, n_bot), (cx - 3, n_bot)])
        pygame.draw.polygon(surf, m['brass_shadow'],
                            [(cx + 1, n_top), (cx + 2, n_top),
                             (cx + 3, n_bot), (cx + 1, n_bot)])
    # Mouth — a small lit_niche (free amber breath-glow at dusk/night).
    if rh >= 11:
        _lit_niche(surf, cx, face_cy + int(rh * 0.6),
                   max(5, rw // 2), max(4, rh // 4), palette)
    # Two hammer ticks, CROWN mask only — occasional catch-lights, never a field
    # of stitching that aliases at 1×. The dish rim-light carries "hammered" on
    # the rest of the stack.
    if crown:
        for tk in (-0.28, 0.22):
            tx = int(cx + rw * tk)
            ty = int(face_cy - rh * 0.55)
            pygame.draw.line(surf, m['brass_hi'], (tx, ty), (tx + 1, ty - 1), 1)

    if with_lozenge:
        _lozenge_cell(surf, cx, u_top + face_h, u_bot - 1, m, palette)


def _draw_tower_upright(surf, cx, y_top, y_bottom, palette, seed):
    """Draw the reliquary stack upright, plinth at y_bottom, crescent finial at
    y_top (the gap end). Callers flip the whole surface for the ceiling-hung
    top section."""
    m = _materials(palette)
    sect_h = y_bottom - y_top
    if sect_h < 8:
        return

    plinth_h = max(4, min(11, int(sect_h * 0.06)))
    finial_h = max(10, min(26, int(sect_h * 0.10)))
    rim = y_top + RIM_AIR                          # ornament starts below the rim
    body_top = rim + finial_h
    body_bottom = y_bottom - plinth_h
    body_h = body_bottom - body_top
    if body_h < 10:
        body_top, body_h = rim, body_bottom - rim

    # ── FILL GUARANTEE: a full-height recessed back-plate spans the WHOLE band
    # from just below the gap rim to the plinth BEFORE any metal — so the
    # open-frame lozenge can never leave a killzone. Gradient lit-edges →
    # dark-centre reads as a shrine interior / the wood core the brass is tacked
    # onto, not a flat slab. The RIM_AIR inset keeps a thin rim of air (well
    # within the fill tolerance) so nothing reads as bridging the flyway.
    bp = pygame.Rect(cx - _HALF, rim, PIPE_W, body_bottom - rim)
    _gradient_rect(surf, bp, _mix(m['wood_core'], m['back_mid'], 0.5),
                   m['back_mid'], m['back_dark'])
    _aa_polyline(surf, m['back_dark'],
                 [(bp.x, bp.y), (bp.right - 1, bp.y),
                  (bp.right - 1, bp.bottom - 1), (bp.x, bp.bottom - 1)], closed=True)

    # Height-adaptive mask COUNT keyed off a natural unit (~96px): one hero mask
    # at ~70px, a tall stack toward ~355px. Lozenge is dropped when a unit is too
    # short to carry both a legible face and an open cell.
    unit_target = 96
    n = max(1, int(round(body_h / unit_target)))
    pitch = body_h / n

    for i in range(n):
        u_bot = int(body_bottom - pitch * i)
        u_top = int(body_bottom - pitch * (i + 1))
        with_loz = pitch >= 62                       # drop lozenge on short units
        is_crown = (i == n - 1)                      # topmost = hero + wide crown
        _draw_mask(surf, cx, u_top, u_bot, m, palette,
                   with_lozenge=with_loz, crown=is_crown)
        # Copper seam band between stacked masks.
        if i < n - 1:
            _tile_hatch(surf, cx - _HALF + 4, u_top, cx + _HALF - 4, u_top,
                        m['copper'], step=4)
            pygame.draw.line(surf, m['brass_deep'],
                             (cx - _HALF + 3, u_top), (cx + _HALF - 3, u_top), 1)

    # Crescent finial crown at the gap end + a night glint (draw_spiral_glow).
    # Sized + seated so its top arc sits at/below the back-plate rim (RIM_AIR)
    # regardless of section height — the bright ornament tip always keeps air
    # over the flyway instead of reading as bridging it on short stubs.
    fin_rh = max(5, (finial_h - 3) // 2)
    fin_cy = rim + fin_rh + 2
    if _is_dark_sky(palette):
        draw_spiral_glow(surf, cx, fin_cy, radius=6)   # seated on the finial, below the rim
    _crescent(surf, cx, fin_cy, int(_CHEEK_HALF * 0.62),
              fin_rh, m, bite=0.8, rivets=4)
    # A small bright jewel boss at the finial apex.
    pygame.draw.circle(surf, m['brass_hi'], (cx, fin_cy - 1), 2)
    pygame.draw.circle(surf, m['copper'], (cx, fin_cy - 1), 2, 1)

    # ── 3-layer plinth (footing → mid course → lit cap) rooted at the edge.
    pl_w = 78
    ply = body_bottom
    layers = [(pl_w, m['back_dark']), (pl_w - 8, m['bronze']),
              (pl_w - 16, _mix(m['brass'], m['bronze'], 0.5))]
    step = plinth_h // 3 if plinth_h >= 3 else 1
    for li, (lw, col) in enumerate(layers):
        ly = ply + li * step
        lh = plinth_h - li * step if li == len(layers) - 1 else step
        pygame.draw.rect(surf, col, (cx - lw // 2, ly, lw, max(1, lh)))
    pygame.draw.line(surf, m['brass_lit'],
                     (cx - (pl_w - 16) // 2 + 2, ply),
                     (cx + (pl_w - 16) // 2 - 2, ply), 1)

    # Plinth mist + ground foliage (same atmospheric kit as the pagodas).
    _draw_plinth_mist(surf, cx, body_bottom + plinth_h, pl_w + 10, palette)
    draw_grass_bed(surf, cx, body_bottom + plinth_h + 1, pl_w, 22, palette, seed)
    draw_side_shrub(surf, cx - pl_w // 2 - 2, body_bottom + plinth_h + 2, palette, 0.9)
    draw_side_shrub(surf, cx + pl_w // 2 + 2, body_bottom + plinth_h + 2, palette, 0.9)

    # NIGHT: tame the composited additive glows to a warm capped sheen so the
    # tower never carries a pure-white sparkle-field. Covers the band + gutter
    # overhangs + plinth mist.
    if _is_dark_sky(palette):
        _warm_clamp_night(surf, cx - _LOZ_HALF - 6, cx + _LOZ_HALF + 6,
                          y_top - 3, body_bottom + plinth_h + 8)


def candidate_kota_reliquary(surf, top_rect, bot_rect, palette, seed):
    """Bottom is a reliquary stack rising from the plinth, crescent finial at the
    gap. Top is the same builder vertically flipped — a symmetric two-ended
    guardian hung from the ceiling, its finial pointing into the gap."""
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
    """Longest contiguous vertical run of transparent pixels in the band — the
    numeric fill-gate audit (never viewed as an image)."""
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


def _rim_clearance(surf, x0, x1, y_rim, depth=40):
    """Rows from the gap rim to the first painted pixel in the band — proves the
    body reaches the rim so the flyable gap never reads as bridged/starved."""
    for dy in range(depth):
        for x in range(x0, x1):
            if surf.get_at((x, y_rim + dy))[3] != 0:
                return dy
    return depth


def _hero(pal, seed):
    gap_y, gap_h = 176, 150
    top_h = int(gap_y - gap_h / 2)
    bot_top = int(gap_y + gap_h / 2)
    full = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    top_rect = pygame.Rect(MARGIN, 0, PIPE_W, top_h)
    bot_rect = pygame.Rect(MARGIN, bot_top, PIPE_W, GROUND_Y - bot_top)
    candidate_kota_reliquary(full, top_rect, bot_rect, pal, seed=seed)
    tip_y = bot_top - 14
    base_y = GROUND_Y + 10
    hero_h = base_y - tip_y
    hero = _bg(CACHE_W, hero_h, pal, hero_h - (base_y - GROUND_Y))
    hero.blit(full, (0, -tip_y))
    for ex in (MARGIN, MARGIN + PIPE_W):
        pygame.draw.line(hero, (230, 60, 60), (ex, 0), (ex, hero_h), 1)
    return hero, hero_h


def _faceclose(pal, seed, scale=3):
    """Zoom on a single mask so the repoussé sheen + lozenge eyes are auditable."""
    h = 150
    surf = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    br = pygame.Rect(MARGIN, GROUND_Y - h, PIPE_W, h)
    tr = pygame.Rect(MARGIN, 0, PIPE_W, 0)
    candidate_kota_reliquary(surf, tr, br, pal, seed=seed)
    crop = pygame.Surface((CACHE_W, 92))
    crop.blit(_bg(CACHE_W, 92, pal, 92), (0, 0))
    crop.blit(surf, (0, -(GROUND_Y - h)))
    for ex in (MARGIN, MARGIN + PIPE_W):
        pygame.draw.line(crop, (230, 60, 60), (ex, 0), (ex, 92), 1)
    return pygame.transform.scale(crop, (crop.get_width() * scale, 92 * scale))


def _blackout(pal, seed):
    """The solid-silhouette test at NATIVE game scale (band = 58px). Fills every
    painted pixel black on white across the FULL width so the read is carried by
    the gutter overhangs — the wide crescent crown, cheek-wings and diamond
    points — exactly as it would be judged in play. Column is solid by design;
    the identity is the profile edge, not interior holes."""
    h = 168
    surf = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    br = pygame.Rect(MARGIN, GROUND_Y - h, PIPE_W, h)
    candidate_kota_reliquary(surf, pygame.Rect(MARGIN, 0, PIPE_W, 0), br,
                             pal, seed=seed)
    x0, x1 = MARGIN - 34, MARGIN + PIPE_W + 34      # include gutter overhangs
    sil = pygame.Surface((x1 - x0, h))
    sil.fill((236, 236, 236))
    for x in range(x0, x1):
        for y in range(h):
            if surf.get_at((x, GROUND_Y - h + y))[3] != 0:
                sil.set_at((x - x0, y), (20, 20, 24))
    # Mark the 58px collision band edges so the overhang is legible.
    for ex in (MARGIN - x0, MARGIN + PIPE_W - x0):
        pygame.draw.line(sil, (210, 70, 70), (ex, 0), (ex, h), 1)
    return sil


def main():
    pal = biome.palette_for_phase(PHASE_DAY)
    pal_n = biome.palette_for_phase(PHASE_NIGHT)

    hero_day, hd_h = _hero(pal, 5)
    hero_night, hn_h = _hero(pal_n, 5)
    face_day = _faceclose(pal, 5, scale=3)
    face_night = _faceclose(pal_n, 5, scale=3)
    black = _blackout(pal, 5)

    # ── FILL GATE + RIM CLEARANCE audit at three section heights ──
    strip_heights = [70, 210, 355]
    strips = []
    print("FILL GATE — max empty vertical run inside the 58px PIPE_W band")
    for h in strip_heights:
        s = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
        br = pygame.Rect(MARGIN, GROUND_Y - h, PIPE_W, h)
        tr = pygame.Rect(MARGIN, 0, PIPE_W, 0)
        candidate_kota_reliquary(s, tr, br, pal, seed=5)
        run = _max_empty_run(s, MARGIN, MARGIN + PIPE_W, GROUND_Y - h, GROUND_Y)
        clr = _rim_clearance(s, MARGIN, MARGIN + PIPE_W, GROUND_Y - h)
        crop = pygame.Surface((CACHE_W, h + 8))
        crop.blit(_bg(CACHE_W, h + 8, pal, h), (0, 0))
        crop.blit(s, (0, -(GROUND_Y - h)))
        # Overlay the auditable PIPE_W collision column.
        col = pygame.Surface((PIPE_W, h + 8), pygame.SRCALPHA)
        col.fill((80, 160, 255, 40))
        crop.blit(col, (MARGIN, 0))
        for ex in (MARGIN, MARGIN + PIPE_W):
            pygame.draw.line(crop, (230, 60, 60), (ex, 0), (ex, h + 8), 1)
        strips.append((h, crop, run, clr))
        print(f"  h={h:3d}  max empty run={run}px  rim clearance={clr}px  "
              f"[{'OK' if run <= 12 else 'FAIL'}]")

    # ── day != night pixel proof (a known metal sample point) ──
    sx, sy = MARGIN + PIPE_W // 2, GROUND_Y - 120
    sd = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    sn = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    br = pygame.Rect(MARGIN, GROUND_Y - 210, PIPE_W, 210)
    tr = pygame.Rect(MARGIN, 0, PIPE_W, 0)
    candidate_kota_reliquary(sd, tr, br, pal, seed=5)
    candidate_kota_reliquary(sn, tr, br, pal_n, seed=5)
    print(f"DAY!=NIGHT  brass@({sx},{sy})  day={sd.get_at((sx,sy))[:3]}  "
          f"night={sn.get_at((sx,sy))[:3]}")

    # ── compose the sheet ──
    pad = 12
    head_h = 66
    title = pygame.font.SysFont(None, 32)
    sub = pygame.font.SysFont(None, 18)
    lab = pygame.font.SysFont(None, 20)

    strips_total_h = sum(c.get_height() + 24 + pad for _, c, _, _ in strips)
    right_col_h = (face_day.get_height() + 24 + pad + face_night.get_height()
                   + 24 + pad + black.get_height() + 24)
    col_h = max(hd_h + 24, hn_h + 24, strips_total_h, right_col_h)
    sheet_w = pad + CACHE_W * 3 + face_day.get_width() + pad * 5
    sheet_h = head_h + col_h + pad * 2
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((24, 25, 30))

    sheet.blit(title.render("kota_reliquary — hammered brass guardian totem  ·  round_2",
                            True, (245, 240, 230)), (pad, 12))
    sheet.blit(sub.render("metal totem: dished oval faces + crescent coiffure over an OPEN "
                          "lozenge frame  ·  full-height recessed back-plate keeps the "
                          "column solid  ·  red = PIPE_W(58) band  ·  blue = collision "
                          "column overlay", True, (170, 172, 182)), (pad, 42))

    x, y = pad, head_h
    sheet.blit(hero_day, (x, y))
    pygame.draw.rect(sheet, (60, 62, 72), (x, y, CACHE_W, hd_h), 1)
    sheet.blit(lab.render("HERO — DAY (0.30)", True, (255, 224, 150)), (x, y + hd_h + 3))

    x += CACHE_W + pad
    sheet.blit(hero_night, (x, y))
    pygame.draw.rect(sheet, (60, 62, 72), (x, y, CACHE_W, hn_h), 1)
    sheet.blit(lab.render("HERO — NIGHT (0.85) glint", True, (255, 224, 150)),
               (x, y + hn_h + 3))

    x += CACHE_W + pad
    sy = head_h
    sheet.blit(lab.render("FILL — column overlay", True, (255, 224, 150)), (x, sy - 20))
    for h, crop, run, clr in strips:
        sheet.blit(crop, (x, sy))
        pygame.draw.rect(sheet, (60, 62, 72), (x, sy, CACHE_W, crop.get_height()), 1)
        ok = "OK" if run <= 12 else "FAIL"
        sheet.blit(lab.render(f"h={h}  run{run}px rim{clr}px [{ok}]", True,
                              (200, 235, 170) if run <= 12 else (255, 140, 140)),
                   (x, sy + crop.get_height() + 3))
        sy += crop.get_height() + 24 + pad

    x += CACHE_W + pad
    sheet.blit(face_day, (x, head_h))
    sheet.blit(lab.render("FACE — DAY repoussé sheen", True, (255, 224, 150)),
               (x, head_h + face_day.get_height() + 3))
    fy = head_h + face_day.get_height() + 24 + pad
    sheet.blit(face_night, (x, fy))
    sheet.blit(lab.render("FACE — NIGHT glint", True, (255, 224, 150)),
               (x, fy + face_night.get_height() + 3))
    by = fy + face_night.get_height() + 24 + pad
    sheet.blit(black, (x, by))
    pygame.draw.rect(sheet, (60, 62, 72),
                     (x, by, black.get_width(), black.get_height()), 1)
    sheet.blit(lab.render("58px BLACKOUT", True, (255, 224, 150)),
               (x, by + black.get_height() + 3))

    # ── NIGHT no-pure-white audit (never opens the PNG) ──
    na = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    br_n = pygame.Rect(MARGIN, 0, PIPE_W, 0)
    bot_n = pygame.Rect(MARGIN, 120, PIPE_W, GROUND_Y - 120)
    candidate_kota_reliquary(na, br_n, bot_n, pal_n, seed=5)
    pure_white = 0
    night_max = 0
    for xx in range(CACHE_W):
        for yy in range(CACHE_H):
            c = na.get_at((xx, yy))
            if c[3] == 0:
                continue
            night_max = max(night_max, c[0], c[1], c[2])
            if c[:3] == (255, 255, 255):
                pure_white += 1
    print(f"NIGHT AUDIT  pure-white(255,255,255)={pure_white}  "
          f"max channel={night_max}  [{'OK' if pure_white == 0 else 'FAIL'}]")

    out = pathlib.Path(__file__).resolve().parent / "round_2.png"
    pygame.image.save(sheet, out)
    print(f"wrote {out}  ({sheet.get_width()}x{sheet.get_height()})")


if __name__ == "__main__":
    main()
