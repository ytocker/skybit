"""jade_serpent — an angular, stepped, fanged Mesoamerican feathered-serpent
guardian column, carved in glossy JADE with gold inlay (standalone candidate).

The ANGULAR-STEPPED, glossy-lapidary pole of the TOTEM family: stacked
Kukulkán serpent-jaw masks framed top and bottom by hard-edged Puuc stepped
frets, every edge a crisp 90° step so the blackout reads as a rectilinear
ziggurat profile with a fanged snout — the geometric foil to the smooth moai,
the winged formline pole, the metal kota reliquary and the flat stele.

Distinctness pins:
  * FINISH — the only lapidary material in the set: polished jade with a single
    raking specular gloss band per mask (jade reads wet/glossy, unlike matte
    basalt or painted cedar), gold inlay + obsidian keylines.
  * SILHOUETTE — hard right-angle fret-notch steps (fret bands step OUT past the
    mask bodies) plus a stepped roof-comb crest crown and jutting fang snout.
    No curves carry the outline; it is machine-cut orthogonal.
  * FACE — ringed gold eyes over a fanged bar; the 58px fallback is two
    gold ring-dots above one fang bar.

Column-fill: every jade mask body fills the full PIPE_W (58px) collision band
edge-to-edge; the fret bands step OUT into the gutter (they never substitute for
column fill) and only the fang snout overhangs. So the central band is solid
top-to-bottom at every section height — the stepped tell lives in the gutter.

Mirror read: a symmetric two-ended guardian. Both sections root a 3-layer plinth
at the world edge and cap the gap end with the stepped roof-comb crest + plume
finial; the top section is a true vertical flip. Each serpent-mask unit is built
symmetric about its own centre so the flipped stack still reads as frets +
ring-eyes + fangs rather than an upside-down face.

Standalone review builder: it IMPORTS the real pagoda / pillar draw helpers so
the exploration matches shipped fidelity, but it does not modify any game module.

Run:  python docs/pillar_landmarks/totems/jade_serpent/render.py
Out:  docs/pillar_landmarks/totems/jade_serpent/round_2.png
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

# Real shipped helpers — same fidelity spine as the pagodas + landmarks.
from game.pillar_pagodas import (
    _mix, _shade, _gradient_rect, _aa_polyline, _lit_niche, _tile_hatch,
    _glazed_tile_checker, _draw_plinth_mist, _is_dark_sky, _is_warming_sky,
    _cap_lit_for_dark_sky, _cap_dark_for_dark_sky, _buddha_eye,
    _gold_bright, _gold_deep, _bronze, _lapis, _lacquer_red,
)
from game.pillar_variants import draw_grass_bed, draw_spiral_glow
# draw_side_shrub lives in game.draw (not pillar_variants); imported from its
# real home so the foliage bed matches the shipped pillar bases.
from game.draw import draw_side_shrub

MARGIN = 64                       # matches entities.Pipe eave/ornament gutter
CACHE_W = PIPE_W + MARGIN * 2
CACHE_H = GROUND_Y
PHASE_DAY = 0.30
PHASE_NIGHT = 0.85                # deep-blue extended night — checks glow + gloss

BODY_W = PIPE_W                   # jade mask fills the whole collision band
FRET_W = 70                       # fret bands step OUT past the body (gutter)
SNOUT_W = 76                      # fang snout overhang (gutter only)


# ── jade / gold / obsidian material triad (palette-keyed → biome retint) ──────
def _jade(palette):
    # Glossy jade body — a green mineral anchored in stone_mid so the day→night
    # biome sweep carries it (warm-green day, cool teal-green night). Dropped ~10%
    # off the raw mineral so the mid/lower body sits BELOW the bright day-horizon
    # band and separates by value, not by hue alone (`_jade_lit` is left as-is).
    return _shade(_mix(palette['stone_mid'], (60, 150, 110), 0.60), -13)


def _jade_lit(palette):
    # Specular/lit face of polished jade — the finish tell. Capped at dusk/night
    # so the gloss band lifts the mask without value-spiking against dark sky.
    return _cap_lit_for_dark_sky(
        _mix(palette['stone_light'], (150, 210, 180), 0.55), palette)


def _jade_shadow(palette):
    # Deep carved recess / stepped underside — floored at night so shaded steps
    # don't drop below the sky and swallow the tower into one dark mass.
    return _cap_dark_for_dark_sky(
        _mix(palette['stone_dark'], (28, 74, 60), 0.80), palette)


def _obsidian(palette):
    # Volcanic-glass keyline — the near-black inlay line that crisps every step.
    return _cap_dark_for_dark_sky(
        _mix(palette['stone_dark'], (22, 20, 26), 0.86), palette, floor=30)


def _lum(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


# ── signature primitive: stepped Puuc fret band ──────────────────────────────
def _fret_band(surf, cx, y_top, band_h, palette):
    """A hard-edged Puuc / Greek-key stepped meander band that steps OUT past
    the mask body into the gutter — the concept's orthogonal signature. Drawn as
    filled jade rects with a beveled lit top-edge, a shadow underside and a row
    of square gold inlay studs sitting in obsidian-keyed recesses, so the band
    reads as machine-cut cut-stone, never organic lumps."""
    jade = _jade(palette)
    lit = _jade_lit(palette)
    sh = _jade_shadow(palette)
    obs = _obsidian(palette)
    gold = _cap_lit_for_dark_sky(_gold_bright(palette), palette)
    goldd = _gold_deep(palette)

    x0 = cx - FRET_W // 2
    band = pygame.Rect(x0, y_top, FRET_W, band_h)
    # 3-stop volume across the band so it reads as a projecting stone course.
    _gradient_rect(surf, band, lit, jade, sh, vertical=True)
    # Beveled lit top-edge + shadow underside — the crisp step read.
    pygame.draw.line(surf, _shade(lit, 25), (x0, y_top), (x0 + FRET_W - 1, y_top), 1)
    pygame.draw.line(surf, obs, (x0, y_top + band_h - 1),
                     (x0 + FRET_W - 1, y_top + band_h - 1), 1)
    # Square-step meander: a repeating xicalcoliuhqui — obsidian-keyed L-steps
    # with a gold stud, cadence tuned so individual steps read at PIPE_W.
    period = 12
    mid_y = y_top + band_h // 2
    for sx in range(x0 + 2, x0 + FRET_W - period, period):
        # L-shaped step notch (down-then-right) in obsidian.
        step = [(sx, y_top + 2), (sx + 4, y_top + 2), (sx + 4, mid_y),
                (sx + 8, mid_y), (sx + 8, y_top + band_h - 3)]
        _aa_polyline(surf, obs, step)
        # Gold inlay stud in the notch pocket.
        if band_h >= 8:
            pygame.draw.rect(surf, gold, (sx + 5, mid_y - 1, 2, 2))
            pygame.draw.rect(surf, goldd, (sx + 5, mid_y - 1, 2, 2), 1)
    # Gold pin-stripe capping the course — the inlaid trim line.
    pygame.draw.line(surf, goldd, (x0 + 2, y_top + 1), (x0 + FRET_W - 3, y_top + 1), 1)


# ── signature primitive: ringed serpent eye ──────────────────────────────────
def _serpent_eye(surf, cx, cy, palette, r):
    """A recessed jade socket ringed in gold with an obsidian keyline — follows
    the _buddha_eye pad→brow→iris→keyline layering model retinted to jade+gold.
    At unit scale it seats a small `_buddha_eye` almond gaze inside the gold ring
    (the fierce living stare); below ~5px it collapses to the two-gold-dot
    thumbnail fallback so the face survives the 58px collision column."""
    jade = _jade(palette)
    sh = _jade_shadow(palette)
    obs = _obsidian(palette)
    gold = _cap_lit_for_dark_sky(_gold_bright(palette), palette)
    goldd = _gold_deep(palette)
    # Recessed socket shadow so the eye sits INTO the mask, not on it.
    pygame.draw.circle(surf, sh, (cx, cy), r + 2)
    pygame.draw.circle(surf, _mix(jade, sh, 0.45), (cx, cy), r + 1)
    # Gold rim ring (bright) + deep-gold keyline.
    pygame.draw.circle(surf, gold, (cx, cy), r)
    pygame.draw.circle(surf, goldd, (cx, cy), r, 1)
    if r >= 5:
        # Obsidian iris disc, then a retinted almond gaze inside the ring.
        pygame.draw.circle(surf, obs, (cx, cy), max(2, r - 2))
        _buddha_eye(surf, cx, cy, palette, scale=min(0.7, r / 8.0))
    else:
        # Thumbnail fallback: a solid gold ring-dot (no interior detail).
        pygame.draw.circle(surf, obs, (cx, cy), 1)
    # Outer obsidian keyline crisps the socket against the jade face.
    pygame.draw.circle(surf, obs, (cx, cy), r + 2, 1)


# ── signature primitive: fanged serpent jaw + lit throat ─────────────────────
def _serpent_jaw(surf, cx, y_top, jaw_h, palette):
    """The fanged Kukulkán maw framing an entry recess. An upper lip band with a
    jutting snout, a dark `_lit_niche` throat behind (night = the serpent's lit
    maw), and a row of gold fangs biting DOWN over it. The snout + fangs are the
    only gutter overhang; the lip band still fills the full column."""
    jade = _jade(palette)
    lit = _jade_lit(palette)
    sh = _jade_shadow(palette)
    obs = _obsidian(palette)
    gold = _cap_lit_for_dark_sky(_gold_bright(palette), palette)
    goldd = _gold_deep(palette)

    lip_h = max(4, jaw_h // 3)
    # Upper lip band — full column, gradient volume, obsidian underline.
    lip = pygame.Rect(cx - BODY_W // 2, y_top, BODY_W, lip_h)
    _gradient_rect(surf, lip, lit, jade, sh, vertical=True)
    pygame.draw.line(surf, _shade(lit, 20),
                     (lip.x, y_top), (lip.right - 1, y_top), 1)

    # Jutting snout — a stepped nose block overhanging the gutter with a nostril
    # niche each side (kept angular: a trapezoid, not a curve).
    snout_top = y_top + 1
    snout = [(cx - SNOUT_W // 2, y_top + lip_h),
             (cx - BODY_W // 2 + 4, snout_top),
             (cx + BODY_W // 2 - 4, snout_top),
             (cx + SNOUT_W // 2, y_top + lip_h)]
    pygame.draw.polygon(surf, jade, snout)
    _aa_polyline(surf, obs, snout, closed=False)
    pygame.draw.line(surf, _shade(lit, 15),
                     (cx - BODY_W // 2 + 4, snout_top),
                     (cx + BODY_W // 2 - 4, snout_top), 1)

    # Dark maw + lit throat behind the fangs. Full-width so the mouth keeps the
    # band edges fed (the mask's mouth spans the whole face).
    maw_y = y_top + lip_h
    maw_h = jaw_h - lip_h
    if maw_h >= 4:
        maw = pygame.Rect(cx - BODY_W // 2, maw_y, BODY_W, maw_h)
        pygame.draw.rect(surf, obs, maw)
        pygame.draw.rect(surf, _shade(obs, -8), maw, 1)
        _lit_niche(surf, cx, maw_y + 1, min(16, BODY_W - 12),
                   max(4, maw_h - 2), palette)

    # Gold fangs biting DOWN into the maw — the fang-bar tell. Sized/counted so
    # each triangle reads at PIPE_W; obsidian keyline so they crisp on jade.
    n_fangs = 5
    fang_h = max(4, int(maw_h * 0.7))
    fang_top = maw_y + 1
    slot = (BODY_W - 8) / n_fangs
    for i in range(n_fangs):
        fx = cx - BODY_W // 2 + 4 + int((i + 0.5) * slot)
        tip = fang_top + fang_h
        tri = [(fx - 2, fang_top), (fx + 2, fang_top), (fx, tip)]
        pygame.draw.polygon(surf, gold, tri)
        _aa_polyline(surf, goldd, tri, closed=True)
    # Two outer canine fangs longer + hooked slightly outward (the bite read).
    for sgn in (-1, 1):
        fx = cx + sgn * (BODY_W // 2 - 5)
        tip_y = fang_top + int(fang_h * 1.35)
        tri = [(fx - sgn * 3, fang_top), (fx, fang_top),
               (fx - sgn * 1, min(tip_y, y_top + jaw_h))]
        pygame.draw.polygon(surf, gold, tri)
        _aa_polyline(surf, goldd, tri, closed=True)


# ── gloss: one raking specular band per mask (the lapidary finish tell) ───────
def _gloss_streak(surf, rect, palette):
    """A single diagonal translucent highlight sweeping across a jade mask so it
    reads as WET polished stone, not matte. One band per mask (AD note) — kept
    additive-soft so the jade never goes plasticky or noisy at 1x."""
    if rect.width < 8 or rect.height < 8:
        return
    hi = _jade_lit(palette)
    band = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    # Parallelogram from upper-left toward mid-right — a single raking sweep.
    w, h = rect.width, rect.height
    quad = [(int(w * 0.10), 0), (int(w * 0.30), 0),
            (int(w * 0.66), h), (int(w * 0.46), h)]
    pygame.draw.polygon(band, (*hi, 60), quad)
    # A thin brighter core line down the streak for the crisp glint.
    pygame.draw.line(band, (*_shade(hi, 30), 110),
                     (int(w * 0.24), 1), (int(w * 0.54), h - 1), 1)
    surf.blit(band, (rect.x, rect.y), special_flags=pygame.BLEND_RGBA_ADD)


# ── stepped roof-comb crest crown + plume finial (gap end) ────────────────────
def _draw_crown(surf, cx, y_top, crown_h, palette, *, glow):
    """A full-width Maya roof-comb crest whose TOP edge is cut into a symmetric
    row of stepped feather-tip merlons — peaks pinned to the band edges + centre
    so the collision column stays FILLED to the rim (valleys are a fixed shallow
    notch, never > the fill ceiling), while the crenellated profile still reads as
    an orthogonal plumed crest in blackout. Gold quill-spines rise to each tip and
    the centre carries a night halo via `draw_spiral_glow`."""
    jade = _jade(palette)
    lit = _jade_lit(palette)
    sh = _jade_shadow(palette)
    obs = _obsidian(palette)
    gold = _cap_lit_for_dark_sky(_gold_bright(palette), palette)
    goldd = _gold_deep(palette)

    x0 = cx - BODY_W // 2
    base_y = y_top + crown_h
    # 3px of air above the gap rim so the two crests never kiss across the flyable
    # channel — merlon tops are pulled back off the section end (y_top).
    air = 3
    merlon_top = y_top + air
    # Deep, square crenel floor so the roof-comb reads as a deliberate stepped
    # crest in blackout, while the crenel empty-run (air + depth) stays under the
    # fill ceiling (3 + 6 = 9px < 12).
    crenel_bot = y_top + air + 6

    # Symmetric squared comb — nine alternating segments with merlons pinned to
    # both band edges, so the collision-band corners stay fed right to the crest
    # top and the crenellation is a true square step (vertical walls), never a
    # one-sided slope.
    n_seg = 9
    bounds = [x0 + int(round(k * BODY_W / n_seg)) for k in range(n_seg + 1)]
    top_edge = []
    for k in range(n_seg):
        yk = merlon_top if k % 2 == 0 else crenel_bot
        top_edge.append((bounds[k], yk))
        top_edge.append((bounds[k + 1], yk))
    poly = [(x0, base_y)] + top_edge + [(x0 + BODY_W - 1, base_y)]
    pygame.draw.polygon(surf, jade, poly)
    # 3-stop volume on the solid slab below the crenel floor.
    _gradient_rect(surf, pygame.Rect(x0, crenel_bot, BODY_W, base_y - crenel_bot),
                   lit, jade, sh, vertical=True)
    pygame.draw.line(surf, obs, (x0, base_y - 1), (x0 + BODY_W - 1, base_y - 1), 1)
    pygame.draw.line(surf, obs, (x0, crenel_bot), (x0, base_y - 1), 1)
    pygame.draw.line(surf, obs, (x0 + BODY_W - 1, crenel_bot),
                     (x0 + BODY_W - 1, base_y - 1), 1)
    # Obsidian keyline traces the squared merlons + crenels — the stepped tell.
    _aa_polyline(surf, obs, top_edge)
    # Gold quill-spine rising to each merlon centre + a lit merlon flank so the
    # square steps carry volume as well as silhouette.
    for k in range(0, n_seg, 2):
        mx = (bounds[k] + bounds[k + 1]) // 2
        pygame.draw.line(surf, goldd, (mx, base_y - 2), (mx, merlon_top + 1), 1)
        pygame.draw.line(surf, _shade(lit, 25), (bounds[k], merlon_top + 1),
                         (bounds[k], crenel_bot - 1), 1)
    # Horizontal fret course across the crest slab ties it to the tower language.
    slab_h = base_y - crenel_bot
    if slab_h >= 10:
        _fret_band(surf, cx, base_y - min(10, slab_h - 2),
                   min(9, slab_h - 2), palette)
    # Gilt boss centred on the crest slab.
    pygame.draw.circle(surf, gold, (cx, crenel_bot + 2), 2)
    pygame.draw.circle(surf, goldd, (cx, crenel_bot + 2), 2, 1)
    if glow:
        # Halo seated well INSIDE the crest slab so neither the soft disc nor the
        # spiral bridges the flyable gap after the ceiling-section flip (its reach
        # stays deeper than the 3px crest clearance).
        draw_spiral_glow(surf, cx, crenel_bot + 6, radius=7)


# ── one serpent-mask unit ─────────────────────────────────────────────────────
def _draw_mask_unit(surf, cx, y_top, unit_h, palette, seed):
    """One stacked Kukulkán mask: top fret-band → jade face (scale-hatched, gloss
    streak, ring eyes) → fanged jaw. The jade face fills the full PIPE_W band."""
    jade = _jade(palette)
    lit = _jade_lit(palette)
    sh = _jade_shadow(palette)
    obs = _obsidian(palette)

    fret_h = max(6, min(12, int(unit_h * 0.16)))
    jaw_h = max(8, min(22, int(unit_h * 0.30)))
    face_h = unit_h - fret_h - jaw_h
    if face_h < 8:
        # Very short unit: drop the jaw budget first so the face + fret survive.
        jaw_h = max(6, unit_h - fret_h - 8)
        face_h = unit_h - fret_h - jaw_h

    # Jade face block — full column, 3-stop volume, obsidian side keylines.
    face = pygame.Rect(cx - BODY_W // 2, y_top + fret_h, BODY_W, face_h)
    _gradient_rect(surf, face, lit, jade, sh)
    pygame.draw.line(surf, obs, (face.x, face.y), (face.x, face.bottom - 1), 1)
    pygame.draw.line(surf, obs, (face.right - 1, face.y),
                     (face.right - 1, face.bottom - 1), 1)

    # Carved scale rows — serpent scales via the shared tile-hatch, kept to the
    # cheeks so they don't crowd the eyes.
    if face_h >= 16:
        for hy in range(face.y + 4, face.bottom - 4, 5):
            _tile_hatch(surf, face.x + 3, hy, face.right - 3, hy,
                        _shade(sh, 8), step=4)

    # Single raking gloss band — the lapidary finish tell.
    _gloss_streak(surf, face, palette)

    # Ring eyes — a symmetric pair, sized to the face so they read at scale.
    eye_r = max(3, min(7, face_h // 4))
    eye_y = face.y + max(eye_r + 2, face_h // 3)
    eye_dx = BODY_W // 4
    _serpent_eye(surf, cx - eye_dx, eye_y, palette, eye_r)
    _serpent_eye(surf, cx + eye_dx, eye_y, palette, eye_r)
    # Gold brow ridge across the eyes (angular, stepped) — the fret language
    # echoed on the face.
    if face_h >= 14:
        brow_y = eye_y - eye_r - 2
        goldd = _gold_deep(palette)
        pygame.draw.line(surf, goldd,
                         (cx - eye_dx - eye_r, brow_y),
                         (cx + eye_dx + eye_r, brow_y), 1)
        pygame.draw.line(surf, obs,
                         (cx - eye_dx - eye_r, brow_y + 1),
                         (cx + eye_dx + eye_r, brow_y + 1), 1)

    # Fanged jaw at the base of the unit.
    _serpent_jaw(surf, cx, y_top + fret_h + face_h, jaw_h, palette)

    # Fret band crowning the unit (drawn last so it steps OVER the face top).
    _fret_band(surf, cx, y_top, fret_h, palette)


# ── plinth + foliage bed ──────────────────────────────────────────────────────
def _draw_plinth(surf, cx, base_y, palette, seed):
    """3-layer stepped stone plinth widening downward with a gold trim course,
    an atmospheric mist wedge behind it, and a foliage bed (grass + a flanking
    flowering shrub) creeping up from the ground — matches the shipped bases."""
    jade = _jade(palette)
    lit = _jade_lit(palette)
    sh = _jade_shadow(palette)
    goldd = _gold_deep(palette)

    _draw_plinth_mist(surf, cx, base_y, 96, palette)

    layer_h = 5
    widths = (66, 78, 92)
    for i, w in enumerate(widths):
        ly = base_y - (len(widths) - i) * layer_h
        r = pygame.Rect(cx - w // 2, ly, w, layer_h)
        _gradient_rect(surf, r, lit, jade, sh, vertical=True)
        pygame.draw.line(surf, _shade(lit, 20), (r.x, ly), (r.right - 1, ly), 1)
        pygame.draw.line(surf, _obsidian(palette), (r.x, r.bottom - 1),
                         (r.right - 1, r.bottom - 1), 1)
        # Gold trim course on the middle slab.
        if i == 1:
            pygame.draw.line(surf, goldd, (r.x + 3, ly + 1),
                             (r.right - 4, ly + 1), 1)

    # Foliage: grass tuft bed + a flanking shrub, seeded for variation.
    draw_grass_bed(surf, cx, base_y, 84, 22, palette, seed=seed)
    draw_side_shrub(surf, cx - 44, base_y, palette, scale=0.9)
    draw_side_shrub(surf, cx + 46, base_y, palette, scale=0.8)


# ── full upright tower ────────────────────────────────────────────────────────
def _draw_tower_upright(surf, cx, y_top, y_bottom, palette, seed):
    """Draw the guardian upright: plinth at y_bottom, stacked serpent-mask units,
    stepped crest crown at the gap end (y_top). Callers flip the surface for the
    ceiling-hung top section."""
    sect_h = y_bottom - y_top
    if sect_h < 8:
        return

    plinth_h = max(10, min(18, int(sect_h * 0.06)))
    crown_h = max(16, min(40, int(sect_h * 0.14)))
    if sect_h < 70:
        crown_h = max(12, min(crown_h, sect_h // 4))

    stack_top = y_top + crown_h
    stack_bot = y_bottom - plinth_h
    stack_h = stack_bot - stack_top
    if stack_h < 8:
        stack_top = y_top
        stack_h = stack_bot - stack_top

    # Height-adaptive mask COUNT keyed off a natural unit height (~68px): one
    # hero mask at ~70px sections, a tall stack toward ~355px.
    unit_target = 68
    n = max(1, int(round(stack_h / unit_target)))
    pitch = stack_h / n
    for i in range(n):
        uy = int(stack_top + pitch * i)
        uh = int(stack_top + pitch * (i + 1)) - uy
        _draw_mask_unit(surf, cx, uy, uh, palette, seed + i)

    # Stepped crest crown caps the gap end; night halo on the plume.
    _draw_crown(surf, cx, y_top, crown_h, palette, glow=_is_dark_sky(palette))

    # Guaranteed continuous obsidian side-keylines down both edges of the
    # collision band (drawn last, so no per-unit AA can thin them): the silhouette
    # then reads by VALUE against the bright day horizon even where the darkened
    # jade body goes near-isoluminant with the sky, i.e. it never leans on hue
    # alone. Runs from the crest's merlon top to the plinth (which widens past the
    # band); only the fret/snout gutter overhangs sit outside these lines.
    obs = _obsidian(palette)
    xL = cx - BODY_W // 2
    xR = cx + BODY_W // 2 - 1
    key_top = y_top + 3
    key_bot = y_bottom - plinth_h
    pygame.draw.line(surf, obs, (xL, key_top), (xL, key_bot), 1)
    pygame.draw.line(surf, obs, (xR, key_top), (xR, key_bot), 1)

    # Plinth + foliage root at the world edge.
    _draw_plinth(surf, cx, y_bottom, palette, seed)


def candidate_jade_serpent(surf, top_rect, bot_rect, palette, seed):
    """Bottom: a jade guardian rising from a plinth, stepped crest at the gap.
    Top: the same builder flipped — a symmetric two-ended guardian hung from the
    ceiling, its crest pointing into the gap."""
    if bot_rect.height > 0:
        _draw_tower_upright(surf, bot_rect.centerx, bot_rect.y, bot_rect.bottom,
                            palette, seed)
    if top_rect.height > 0:
        tmp = pygame.Surface((surf.get_width(), top_rect.height), pygame.SRCALPHA)
        _draw_tower_upright(tmp, top_rect.centerx, 0, top_rect.height,
                            palette, seed + 101)
        surf.blit(pygame.transform.flip(tmp, False, True), (0, top_rect.y))


# ── review harness ────────────────────────────────────────────────────────────
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
    the numeric fill-gate check (never viewed as an image)."""
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


def _hero(pal, seed):
    gap_y, gap_h = 150, 150
    top_h = int(gap_y - gap_h / 2)
    bot_top = int(gap_y + gap_h / 2)
    full = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    top_rect = pygame.Rect(MARGIN, 0, PIPE_W, top_h)
    bot_rect = pygame.Rect(MARGIN, bot_top, PIPE_W, GROUND_Y - bot_top)
    candidate_jade_serpent(full, top_rect, bot_rect, pal, seed=seed)

    tip_y = bot_top - 46
    base_y = GROUND_Y + 8
    hero_h = base_y - tip_y
    hero = _bg(CACHE_W, hero_h, pal, hero_h - (base_y - GROUND_Y))
    hero.blit(full, (0, -tip_y))
    for ex in (MARGIN, MARGIN + PIPE_W):
        pygame.draw.line(hero, (230, 60, 60), (ex, 0), (ex, hero_h), 1)
    return hero, hero_h


def _closeup(pal, seed, scale=3):
    """Zoom on a single mask FACE + maw so eyes / fangs / gloss are checkable."""
    surf = pygame.Surface((CACHE_W, 150), pygame.SRCALPHA)
    _draw_mask_unit(surf, MARGIN + PIPE_W // 2, 6, 128, pal, seed)
    crop = pygame.Surface((CACHE_W, 150))
    crop.blit(_bg(CACHE_W, 150, pal, 150), (0, 0))
    crop.blit(surf, (0, 0))
    for ex in (MARGIN, MARGIN + PIPE_W):
        pygame.draw.line(crop, (230, 60, 60), (ex, 0), (ex, 150), 1)
    return pygame.transform.scale(
        crop, (crop.get_width() * scale, crop.get_height() * scale))


def _blackout(pal, seed):
    """True 58px-wide solid silhouette (any opaque pixel → black) for the
    blackout distinctness test, plus a 3x zoom beside it."""
    h = 300
    surf = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    br = pygame.Rect(MARGIN, GROUND_Y - h, PIPE_W, h)
    tr = pygame.Rect(MARGIN, 0, PIPE_W, 0)
    candidate_jade_serpent(surf, tr, br, pal, seed=seed)
    # Include the gutter overhang so the stepped/fang silhouette reads.
    x0, x1 = MARGIN - 12, MARGIN + PIPE_W + 12
    sil = pygame.Surface((x1 - x0, h))
    sil.fill((235, 235, 235))
    for x in range(x0, x1):
        for y in range(GROUND_Y - h, GROUND_Y):
            if surf.get_at((x, y))[3] > 0:
                sil.set_at((x - x0, y - (GROUND_Y - h)), (15, 15, 18))
    return sil


def main():
    pal = biome.palette_for_phase(PHASE_DAY)
    pal_n = biome.palette_for_phase(PHASE_NIGHT)

    # ── material report: jade vs pagoda sandstone (must read GREEN + distinct) ──
    print("MATERIALS (jade triad vs pagoda stone_mid, day + night)")
    for name, p in (("DAY  ", pal), ("NIGHT", pal_n)):
        j, jl, js = _jade(p), _jade_lit(p), _jade_shadow(p)
        sm = p['stone_mid']
        gminusr = j[1] - j[0]
        print(f"  {name} jade={j} lum={_lum(j):.0f}  jade_lit={jl}  "
              f"jade_shadow={js}  obsidian={_obsidian(p)}")
        print(f"        gold_bright={_gold_bright(p)}  gold_deep={_gold_deep(p)}")
        print(f"        stone_mid={sm}  jade G-R={gminusr:+d} (green tell)  "
              f"jade-vs-stone lumDelta={abs(_lum(j)-_lum(sm)):.0f}")
        # Day body-vs-sky value crossing (AD FIX 2): body midtone must sit under
        # the bright horizon band, and the obsidian side-keyline must guarantee a
        # value edge regardless of the hue-only day separation.
        hz, st, obs = p['horizon'], p['sky_top'], _obsidian(p)
        print(f"        horizon={hz} lum={_lum(hz):.0f}  sky_top={st} "
              f"lum={_lum(st):.0f}  obsidian lum={_lum(obs):.0f}")
        print(f"        body dL vs horizon={_lum(hz)-_lum(j):+.0f}  "
              f"lit dL vs horizon={_lum(hz)-_lum(jl):+.0f}  "
              f"keyline dL vs sky_top={abs(_lum(obs)-_lum(st)):.0f} / "
              f"vs body={abs(_lum(obs)-_lum(j)):.0f} (value edge)")

    hero_day, hd_h = _hero(pal, 4)
    hero_night, hn_h = _hero(pal_n, 4)
    close_day = _closeup(pal, 4, scale=3)
    close_night = _closeup(pal_n, 4, scale=3)
    black = _blackout(pal, 4)
    black_zoom = pygame.transform.scale(
        black, (black.get_width() * 3, black.get_height() * 3))

    # ── FILL GATE: bottom section at three heights ──
    strip_heights = [70, 210, 355]
    strips = []
    print("FILL GATE (max empty vertical run inside the 58px PIPE_W band)")
    for hh in strip_heights:
        s = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
        br = pygame.Rect(MARGIN, GROUND_Y - hh, PIPE_W, hh)
        tr = pygame.Rect(MARGIN, 0, PIPE_W, 0)
        candidate_jade_serpent(s, tr, br, pal, seed=4)
        run, rx = _max_empty_run(s, MARGIN, MARGIN + PIPE_W, GROUND_Y - hh, GROUND_Y)
        crop = pygame.Surface((CACHE_W, hh + 8))
        crop.blit(_bg(CACHE_W, hh + 8, pal, hh), (0, 0))
        crop.blit(s, (0, -(GROUND_Y - hh)))
        for ex in (MARGIN, MARGIN + PIPE_W):
            pygame.draw.line(crop, (230, 60, 60), (ex, 0), (ex, hh + 8), 1)
        strips.append((hh, crop, run))
        print(f"  h={hh:3d}  max empty run = {run}px (x={rx-MARGIN})  "
              f"[{'OK' if run <= 12 else 'FAIL'}]")

    # ── MIRROR / gap-rim clearance report ──
    gap_y, gap_h = 150, 150
    top_h = int(gap_y - gap_h / 2)
    bot_top = int(gap_y + gap_h / 2)
    mtest = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    candidate_jade_serpent(mtest, pygame.Rect(MARGIN, 0, PIPE_W, top_h),
                           pygame.Rect(MARGIN, bot_top, PIPE_W, GROUND_Y - bot_top),
                           pal, seed=4)
    # Lowest opaque pixel of the ceiling section (its crest tip reaching down).
    top_reach = 0
    for y in range(top_h + 40, -1, -1):
        row_hit = any(mtest.get_at((x, y))[3] > 0
                      for x in range(MARGIN - 12, MARGIN + PIPE_W + 12))
        if row_hit:
            top_reach = y
            break
    # Highest opaque pixel of the ground section (its crest tip reaching up).
    bot_reach = GROUND_Y
    for y in range(bot_top - 40, GROUND_Y):
        row_hit = any(mtest.get_at((x, y))[3] > 0
                      for x in range(MARGIN - 12, MARGIN + PIPE_W + 12))
        if row_hit:
            bot_reach = y
            break
    print("MIRROR / gap-rim clearance (gap 75..225, centre 150 — target >=3px)")
    print(f"  ceiling crest reaches down to y={top_reach} (rim 75) -> "
          f"{75 - top_reach}px clearance below rim")
    print(f"  ground crest reaches up to  y={bot_reach} (rim 225) -> "
          f"{bot_reach - 225}px clearance above rim")

    # ── compose sheet ──
    pad = 12
    label_h = 24
    head_h = 62
    title = pygame.font.SysFont(None, 32)
    sub = pygame.font.SysFont(None, 19)
    lab = pygame.font.SysFont(None, 20)

    col_w = CACHE_W
    strips_total_h = sum(c.get_height() + label_h + pad for _, c, _ in strips)
    left_h = max(hd_h, hn_h) + label_h
    mid_h = close_day.get_height() + close_night.get_height() + label_h * 2 + pad
    right_h = max(strips_total_h, black_zoom.get_height() + label_h)

    sheet_w = (pad + col_w + pad + col_w + pad + close_day.get_width() + pad
               + col_w + pad + black_zoom.get_width() + pad)
    sheet_h = head_h + max(left_h, mid_h, right_h) + pad * 2
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((22, 26, 24))

    sheet.blit(title.render(
        "jade_serpent — angular stepped fanged guardian  ·  round_2",
        True, (210, 240, 220)), (pad, 12))
    sheet.blit(sub.render(
        "red edges = PIPE_W (58px) band  ·  glossy jade + gold inlay + obsidian  "
        "·  stepped Puuc frets step OUT to gutter  ·  fang snout overhang  "
        "·  ring eyes + fang-bar", True, (150, 175, 160)), (pad, 40))

    x = pad
    y = head_h
    sheet.blit(hero_day, (x, y))
    pygame.draw.rect(sheet, (60, 70, 64), (x, y, col_w, hd_h), 1)
    sheet.blit(lab.render("HERO — DAY (0.30)", True, (200, 235, 170)),
               (x, y + hd_h + 4))

    x += col_w + pad
    sheet.blit(hero_night, (x, y))
    pygame.draw.rect(sheet, (60, 70, 64), (x, y, col_w, hn_h), 1)
    sheet.blit(lab.render("HERO — NIGHT (0.85, lit maw + plume glow)", True,
                          (200, 235, 170)), (x, y + hn_h + 4))

    x += col_w + pad
    sheet.blit(close_day, (x, y))
    sheet.blit(lab.render("FACE/MAW close-up — DAY (3x)", True, (255, 224, 150)),
               (x, y + close_day.get_height() + 2))
    yy = y + close_day.get_height() + label_h + pad
    sheet.blit(close_night, (x, yy))
    sheet.blit(lab.render("FACE/MAW close-up — NIGHT (3x)", True, (255, 224, 150)),
               (x, yy + close_night.get_height() + 2))

    x += close_day.get_width() + pad
    sy = head_h
    sheet.blit(lab.render("FILL — bottom section", True, (255, 224, 150)),
               (x, sy - 20))
    for hh, crop, run in strips:
        sheet.blit(crop, (x, sy))
        pygame.draw.rect(sheet, (60, 70, 64), (x, sy, col_w, crop.get_height()), 1)
        ok = "OK" if run <= 12 else "FAIL"
        sheet.blit(lab.render(f"h={hh}px  ·  run {run}px  [{ok}]", True,
                              (200, 235, 170) if run <= 12 else (255, 140, 140)),
                   (x, sy + crop.get_height() + 4))
        sy += crop.get_height() + label_h + pad

    x += col_w + pad
    sheet.blit(black_zoom, (x, head_h))
    pygame.draw.rect(sheet, (60, 70, 64),
                     (x, head_h, black_zoom.get_width(), black_zoom.get_height()), 1)
    sheet.blit(lab.render("BLACKOUT silhouette (58px core, 3x)", True,
                          (255, 224, 150)),
               (x, head_h + black_zoom.get_height() + 4))
    # True 1x 58px silhouette tucked beside the zoom for honesty.
    sheet.blit(black, (x + black_zoom.get_width() - black.get_width(),
                       head_h + black_zoom.get_height() + label_h + 4))

    out = pathlib.Path(__file__).resolve().parent / "round_2.png"
    pygame.image.save(sheet, out)
    print(f"wrote {out}  ({sheet.get_width()}x{sheet.get_height()})")


if __name__ == "__main__":
    main()
