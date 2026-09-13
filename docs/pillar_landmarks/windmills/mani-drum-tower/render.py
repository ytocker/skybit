"""Standalone candidate: `mani-drum-tower` — a Tibetan wind-driven prayer-wheel
tower whose BODY *is* the mechanism: a fat vertical stack of bulging embossed
copper mani-drums that spin on the wind, crowned by a small bronze cross-vane.

Colocated EXPLORATION module for the pillar-landmark design loop. It follows the
shipped pagoda idiom (`candidate_*(surf, top_rect, bot_rect, palette, seed)`, an
upright `_draw_one` reused for both rects, the top section a vertical flip of a
temp surface) and borrows the real read-only `pillar_pagodas` colour + ornament
helpers so the exploration reads like the real game — but it does NOT import into
or modify any shipped `game/` drawing path.

Silhouette identity (the rounded, body-as-mechanism pole of the windmill set):
the ONLY concept whose blackout is a fat, near-cylindrical STACK OF BULGING
DRUMS — a column of copper barrels wider in the middle, banded by lacquer rings,
threaded on a cedar corner-post frame, with a single small cross-vane on top. No
radial sail-X, no side wheel, no filled paper disc, no lattice cage.

Column-fill contract: the collision column (central PIPE_W band) is carried by
the DRUM BODIES top-to-bottom — each drum pinches to exactly PIPE_W/2 at its
caps and bulges past it at the belly, so the ±29 px core is never uncovered; the
lacquer junction rings bridge every drum-to-drum seam so no empty horizontal run
opens at any section height 70–355 px. The belly bulge, the frame posts and the
cross-vane are pure gutter overhang laid over that solid core.

Run:  python docs/pillar_landmarks/windmills/mani-drum-tower/render.py
Out:  docs/pillar_landmarks/windmills/mani-drum-tower/round_2.png
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

from game.config import GROUND_Y, PIPE_W
from game import biome
from game.pillar_pagodas import (
    _mix,
    _shade,
    _gradient_rect,
    _aa_polyline,
    _lit_niche,
    _tile_hatch,
    _draw_plinth_mist,
    _draw_sorin_flame_halo,
    _is_dark_sky,
    _cap_lit_for_dark_sky,
    _cap_dark_for_dark_sky,
    _bronze,
    _gold_bright,
    _gold_deep,
    _cedar,
    _vermilion,
    _tibet_red,
    _tibet_ochre,
    _saffron,
)
from game.pillar_variants import draw_grass_bed
from game.draw import draw_side_shrub


# ── Material roles (all biome-derived so day → dusk → night retints sweep) ────
#
# Copper drum barrel = stone_accent triad. Prayer-wheel copper is a warm
# red-gold, so the lit face rides _gold_bright, the belly _gold_deep and the
# foot a deep patinated copper anchored in stone_dark. Lit is capped and shadow
# floored at dark skies (same trick the pagodas use) so the barrel holds its
# rounded volume against both a bright noon sky and a deep night one.


def _copper_lit(pal):
    return _cap_lit_for_dark_sky(_mix(pal['stone_accent'], (236, 176, 104), 0.80), pal)


def _copper_mid(pal):
    return _gold_deep(pal)


def _copper_shadow(pal):
    # Deep patinated copper on the shaded third — floored at night so the barrel
    # foot doesn't sink into a dark sky and swallow the drum below it.
    return _cap_dark_for_dark_sky(_mix(pal['stone_dark'], (112, 66, 34), 0.82), pal, floor=60)


def _copper_rim(pal):
    # The bright turned lip on each drum opening — a half-stop over the lit face.
    return _cap_lit_for_dark_sky(_mix(pal['stone_accent'], (248, 206, 132), 0.82), pal)


def _post(pal):
    return _cedar(pal)


def _post_lit(pal):
    return _mix(pal['stone_mid'], pal['stone_light'], 0.42)


def _lacquer(pal):
    # Painted cap-and-base band ringing every drum — Tibetan lacquer red.
    return _vermilion(pal)


def _lacquer_deep(pal):
    return _tibet_red(pal)


def _ochre_trim(pal):
    return _tibet_ochre(pal)


# ── One mani-drum barrel ─────────────────────────────────────────────────────

def _drum(surf, cx, y_top, y_bot, hw_belly, hw_end, palette, seed_phase):
    """A single bulging copper prayer-drum spanning [y_top, y_bot].

    Built as a horizontal 3-stop cylinder gradient (left-lit → belly-mid →
    right-shadow) masked to a bulged barrel silhouette, then overlaid with a
    bright turned rim top+bottom, an engraved mantra band across the belly and a
    1-px sunward specular seam — so the flat rectangle reads as a turning copper
    cylinder at PIPE_W = 58 rather than a painted stripe. `seed_phase` shifts the
    mantra glyphs so stacked drums read as caught mid-rotation, not clones.

    WASM-safe: only `pygame.draw`, one masked blit and `aalines` — no `set_at`
    per pixel, no `surfarray`.
    """
    dh = y_bot - y_top
    if dh < 3:
        return
    lit, mid, shadow = _copper_lit(palette), _copper_mid(palette), _copper_shadow(palette)

    # Barrel silhouette: half-width bulges on a sine so it reads convex, pinching
    # to hw_end at both caps (== PIPE_W/2 so the collision core stays covered).
    def hw_at(i):
        t = i / max(1, dh - 1)
        return hw_end + (hw_belly - hw_end) * math.sin(math.pi * t)

    w = hw_belly * 2 + 2
    tmp = pygame.Surface((w, dh), pygame.SRCALPHA)
    _gradient_rect(tmp, pygame.Rect(0, 0, w, dh), lit, mid, shadow)
    # Carve the barrel: a white mask multiplied in kills everything outside the
    # convex profile while leaving the cylinder gradient untouched inside.
    mask = pygame.Surface((w, dh), pygame.SRCALPHA)
    left, right = [], []
    for i in range(dh):
        hw = hw_at(i)
        left.append((w / 2 - hw, i))
        right.append((w / 2 + hw, i))
    pygame.draw.polygon(mask, (255, 255, 255, 255), left + right[::-1])
    tmp.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(tmp, (cx - w // 2, y_top))

    # Anti-aliased shaded-edge outline so the barrel silhouette stays crisp
    # against a busy sky (the lit left edge stays open, the right edge darkens).
    edge = _shade(shadow, -18)
    _aa_polyline(surf, edge, [(cx + p[0] - w / 2 + cx - cx, p[1] + y_top) for p in
                              [(w / 2 + hw_at(i), i) for i in range(dh)]])
    _aa_polyline(surf, _mix(lit, mid, 0.3),
                 [(cx - hw_at(i), i + y_top) for i in range(dh)])

    hw_belly_i = int(round(hw_belly))

    # Turned copper rim ellipses at the drum's mouth and foot — the visible lip
    # of the cylinder opening. Thin so drums still stack tight.
    for yy, up in ((y_top, True), (y_bot, False)):
        he = 4 if dh > 22 else 2
        rimr = pygame.Rect(cx - hw_end, yy - he, hw_end * 2, he * 2)
        pygame.draw.ellipse(surf, _shade(shadow, -14), rimr, 0)
        pygame.draw.ellipse(surf, _copper_rim(palette), rimr, 1)
        # Bright sunward arc on the lip so the opening catches light.
        pygame.draw.arc(surf, _copper_rim(palette), rimr,
                        math.radians(120), math.radians(210), 1)

    # Engraved mantra band(s) across the belly — Om-mani glyph ticks via the
    # pagoda tile-hatch, phase-shifted per drum for the rotation tell, with a
    # gold specular re-strike on the sunward third so the script glints.
    band_cy = y_top + dh // 2
    engrave = _lacquer_deep(palette)
    glint = _gold_bright(palette)
    # A single mantra band (even on tall drums) — two rows read as noise at 1x,
    # so one belly band with the sunward glint restrike carries the engraving.
    rows = (band_cy,)
    for k, by in enumerate(rows):
        hw = int(hw_at(by - y_top))
        x0 = cx - hw + 3 + (seed_phase + k * 2) % 4
        _tile_hatch(surf, x0, by, cx + hw - 3, by, engrave, step=4)
        # Sunward glint: re-strike the left third of the band a touch brighter.
        _tile_hatch(surf, x0, by, cx - hw // 3, by, glint, step=8)

    # Sunward specular seam — a single soft vertical highlight streak left of
    # centre where a copper cylinder catches the sky, the core rounded cue.
    seam_x = cx - int(hw_belly * 0.34)
    seam = pygame.Surface((3, dh), pygame.SRCALPHA)
    for i in range(dh):
        a = int(120 * math.sin(math.pi * (i / max(1, dh - 1))) ** 0.6)
        seam.fill((*glint, 0))
        pygame.draw.line(seam, (*_copper_rim(palette), a), (1, i), (1, i))
    surf.blit(seam, (seam_x - 1, y_top), special_flags=pygame.BLEND_RGBA_ADD)


def _lacquer_ring(surf, cx, y, hw, palette, *, boss=True):
    """A painted lacquer-red band ringing a drum seam, spanning out to the frame
    posts so it reads as a cross-rung tying the stack together — plus a small
    bronze axle boss + saffron pull-rope tick in the centre (the wind-catch grip
    that says these drums TURN)."""
    lac, deep = _lacquer(palette), _lacquer_deep(palette)
    r = pygame.Rect(cx - hw, y - 2, hw * 2, 5)
    pygame.draw.rect(surf, deep, r)
    pygame.draw.rect(surf, lac, (r.x, r.y, r.w, 2))
    pygame.draw.line(surf, _ochre_trim(palette), (r.x + 1, y), (r.right - 2, y), 1)
    if boss:
        pygame.draw.circle(surf, _bronze(palette), (cx, y), 3)
        pygame.draw.circle(surf, _gold_bright(palette), (cx - 1, y - 1), 1)
        # Saffron pull-rope tick dangling off the boss — the hand/wind grip.
        pygame.draw.line(surf, _saffron(palette), (cx + 3, y), (cx + 5, y + 4), 1)


# ── Frame posts ──────────────────────────────────────────────────────────────

def _frame_posts(surf, cx, y_top, y_bot, hw, palette):
    """Two cedar corner uprights the drums are threaded on — a slim frame that
    contains the barrel stack. Pure gutter overhang (the drums already fill the
    column); it gives the stack an architectural read instead of floating pots."""
    post, lit = _post(palette), _post_lit(palette)
    for sx in (-1, 1):
        px = cx + sx * hw
        pygame.draw.line(surf, _shade(post, -16), (px, y_top), (px, y_bot), 3)
        pygame.draw.line(surf, post, (px, y_top), (px, y_bot), 2)
        pygame.draw.line(surf, lit, (px - sx, y_top), (px - sx, y_bot), 1)


# ── Crown cross-vane (the wind-catch cue) ────────────────────────────────────

def _crown_vane(surf, cx, tip_y, hub_y, palette):
    """A bold bronze wind cross-vane on a short axle above the top drum — four
    diagonal spokes each ending in a cupped anemometer paddle, the sunward pair
    lit brighter for depth, a gilt finial jewel at the tip and a night halo. Made
    deliberately WIDE + unmistakable (per the AD note) so the stack reads as a
    WIND-driven mill, not a rack of pots. Centred so the vertical flip is clean.
    """
    bronze, deep, glint = _bronze(palette), _gold_deep(palette), _gold_bright(palette)
    dark_sky = _is_dark_sky(palette)

    # Short cedar axle from the hub down onto the top drum lid.
    pygame.draw.line(surf, _post(palette), (cx, hub_y), (cx, hub_y + 6), 3)
    pygame.draw.line(surf, _post_lit(palette), (cx - 1, hub_y), (cx - 1, hub_y + 5), 1)

    arm = 18
    ang = math.radians(32)
    ca, sa = math.cos(ang), math.sin(ang)
    # Shaded (right) arms first, then the sunward (left) arms carry the restrike.
    for dirx, diry, sun in ((ca, -sa, False), (ca, sa, False),
                            (-ca, -sa, True), (-ca, sa, True)):
        tx, ty = cx + dirx * arm, hub_y + diry * arm
        # One clean bronze arm: a 3px dark edge, a 2px bronze face, and — only on
        # the lit pair — a single 1px restrike, so it stays legible at 58 px
        # without piling three same-weight strokes on top of each other.
        pygame.draw.line(surf, _shade(bronze, -24), (cx, hub_y), (int(tx), int(ty)), 3)
        pygame.draw.line(surf, bronze, (cx, hub_y), (int(tx), int(ty)), 2)
        if sun:
            pygame.draw.line(surf, glint, (cx, hub_y), (int(tx), int(ty)), 1)
        # Cupped paddle at the tip — an enlarged concave scoop (NOT a flat radial
        # X) so it reads as wind-driven and won't be mistaken for a sail-mill.
        px, py = -diry, dirx
        cup = [(tx, ty),
               (tx + px * 5.5 - dirx * 2.5, ty + py * 5.5 - diry * 2.5),
               (tx + px * 7.0 + dirx * 4.0, ty + py * 7.0 + diry * 4.0),
               (tx + dirx * 5.5, ty + diry * 5.5)]
        cup = [(int(x), int(y)) for x, y in cup]
        pygame.draw.polygon(surf, bronze if not sun else _mix(bronze, glint, 0.5), cup)
        _aa_polyline(surf, _shade(bronze, -26), cup, closed=True)

    # Hub canister.
    pygame.draw.circle(surf, _shade(bronze, -20), (cx, hub_y), 4)
    pygame.draw.circle(surf, bronze, (cx, hub_y), 3)
    pygame.draw.circle(surf, glint, (cx - 1, hub_y - 1), 1)

    # Finial spike + gilt jewel at the very tip, with a night flame-halo.
    pygame.draw.line(surf, deep, (cx, hub_y - 3), (cx, tip_y + 2), 2)
    if dark_sky:
        _draw_sorin_flame_halo(surf, cx, tip_y + 2, palette)
    pygame.draw.circle(surf, glint, (cx, tip_y + 2), 2)
    pygame.draw.circle(surf, _copper_rim(palette), (cx, tip_y + 1), 1)


# ── Plinth ───────────────────────────────────────────────────────────────────

def _plinth(surf, cx, base_y, hw, palette):
    """3-layer stone plinth under the drum tower, over an additive mist wedge
    that lifts the silhouette off the background band."""
    _draw_plinth_mist(surf, cx, base_y, hw * 2 + 16, palette)
    dark = _shade(palette['stone_dark'], -10)
    mid = palette['stone_mid']
    lit = palette['stone_light']
    pygame.draw.rect(surf, dark, (cx - hw - 4, base_y - 6, (hw + 4) * 2, 6))
    pygame.draw.rect(surf, mid, (cx - hw - 2, base_y - 6, (hw + 2) * 2, 3))
    pygame.draw.line(surf, lit, (cx - hw - 4, base_y - 6), (cx + hw + 3, base_y - 6), 1)
    # A low lit shrine niche in the plinth face — warms up amber at night.
    _lit_niche(surf, cx, base_y - 5, 6, 4, palette)


# ── The candidate ────────────────────────────────────────────────────────────

def _draw_one(surf, cx, base_y, top_y, body_w, palette, seed, *, apron=True):
    """One upright mani-drum tower filling [top_y, base_y]. Height-adaptive: the
    drum COUNT scales from 1 fat barrel at ~70 px up to several at ~355 px, but
    the barrel stack always carries the full collision column."""
    total_h = base_y - top_y
    if total_h < 18:
        return

    # The barrel rhythm has to live in the OUTLINE, not just the shading: the
    # belly bulges well past the caps, and BOTH the lacquer rings and the frame
    # posts are pulled in to the cap width so the silhouette pinches at every
    # drum seam instead of being boxed off by outboard hardware. That pinch is
    # what makes the blackout read as stacked barrels rather than one pipe.
    hw_belly = int(body_w * 0.64)          # belly spills ~8 px past the seams
    hw_end = max(8, int(body_w * 0.50) + 1)  # cap == PIPE_W/2 (+1 px cover margin)
    hw_ring = hw_end                        # rings ride the cap so seams pinch
    hw_post = hw_end                        # posts inboard — never widen the outline

    vane_h = max(12, min(int(total_h * 0.14), 24))
    plinth_h = 6 if total_h > 60 else 3

    stack_top = top_y + vane_h
    stack_bot = base_y - plinth_h
    stack_h = stack_bot - stack_top
    if stack_h < 8:
        stack_top = top_y + 2
        stack_h = stack_bot - stack_top

    # Height-adaptive drum count (min 1). ~62 px target keeps each barrel fat.
    n = max(1, round(stack_h / 62))
    drum_h = stack_h / n

    # Frame posts run behind the drums at the cap width, so they only surface at
    # the pinched seams and never push the outline out past the barrel bellies.
    _frame_posts(surf, cx, stack_top, stack_bot, hw_post, palette)

    # Barrels + junction rings from bottom up.
    for k in range(n):
        y0 = int(round(stack_top + k * drum_h))
        y1 = int(round(stack_top + (k + 1) * drum_h))
        _drum(surf, cx, y0, y1, hw_belly, hw_end, palette, (seed + k * 3) % 4)

    # Lacquer rings on every seam (top, between, base) — sized to the cap so they
    # sit at the pinch and bridge the drum joins without opening an empty band.
    for k in range(n + 1):
        y = int(round(stack_top + k * drum_h))
        boss = 0 < k < n or n == 1
        _lacquer_ring(surf, cx, y, hw_ring, palette, boss=boss)

    # Bronze bell-cap where the axle exits the top drum, then the crown vane.
    pygame.draw.ellipse(surf, _shade(_bronze(palette), -16),
                        (cx - hw_end + 2, stack_top - 5, (hw_end - 2) * 2, 8))
    pygame.draw.ellipse(surf, _bronze(palette),
                        (cx - hw_end + 3, stack_top - 5, (hw_end - 3) * 2, 6))
    pygame.draw.arc(surf, _gold_bright(palette),
                    (cx - hw_end + 3, stack_top - 5, (hw_end - 3) * 2, 6),
                    math.radians(120), math.radians(210), 1)
    # Finial tip seated at the section edge so the gilt jewel carries the centre
    # column right to the rim — otherwise the taller crown opens a 2 px gap above
    # the jewel and the collision column would no longer read solid top-to-bottom.
    _crown_vane(surf, cx, top_y, stack_top - 4, palette)

    _plinth(surf, cx, base_y, hw_belly, palette)

    if apron:
        draw_grass_bed(surf, cx, base_y - 1, (hw_belly + 6) * 2, 14, palette, seed=seed)
        draw_side_shrub(surf, cx - hw_belly - 6, base_y - 1, palette, scale=0.9)
        draw_side_shrub(surf, cx + hw_belly + 6, base_y - 1, palette, scale=0.8)


def candidate_mani_drum_tower(surf, top_rect, bot_rect, palette, seed):
    bcx = bot_rect.x + bot_rect.width // 2
    tcx = top_rect.x + top_rect.width // 2

    if bot_rect.height > 20:
        _draw_one(surf, bcx, bot_rect.bottom, bot_rect.y,
                  bot_rect.width, palette, seed, apron=True)

    if top_rect.height > 20:
        # Structural mirror: draw upright into a temp sized to top_rect.height,
        # flip vertically, hang from the ceiling — the vane end then points at
        # the gap exactly like the bottom section (a near-symmetric drum stack,
        # so the flip is clean and the vane stays centred on the channel).
        w = surf.get_width()
        tmp = pygame.Surface((w, top_rect.height), pygame.SRCALPHA)
        _draw_one(tmp, tcx, top_rect.height, 0,
                  top_rect.width, palette, seed, apron=False)
        flipped = pygame.transform.flip(tmp, False, True)
        surf.blit(flipped, (0, top_rect.y))


# ── Review harness ───────────────────────────────────────────────────────────

MARGIN = 64
CACHE_W = PIPE_W + MARGIN * 2
PHASE_DAY = 0.30
PHASE_NIGHT = 0.85
SEED = 7

GAP_Y, GAP_H = 205, 150
TOP_H = int(GAP_Y - GAP_H / 2)
BOT_TOP = int(GAP_Y + GAP_H / 2)
CROP_TOP, CROP_BOT = 18, 486


def _lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _sky_ground(w, h, pal, ground_h):
    cell = pygame.Surface((w, h))
    sky_h = h - ground_h
    for y in range(sky_h):
        t = y / max(1, sky_h - 1)
        pygame.draw.line(cell, _lerp(pal['sky_top'], pal['horizon'], t), (0, y), (w, y))
    for y in range(sky_h, h):
        t = (y - sky_h) / max(1, h - sky_h)
        pygame.draw.line(cell, _lerp(pal['ground_top'], pal['ground_mid'], t),
                         (0, y), (w, y))
    return cell


def _pair_surf(pal):
    surf = pygame.Surface((CACHE_W, GROUND_Y), pygame.SRCALPHA)
    top_rect = pygame.Rect(MARGIN, 0, PIPE_W, TOP_H)
    bot_rect = pygame.Rect(MARGIN, BOT_TOP, PIPE_W, GROUND_Y - BOT_TOP)
    candidate_mani_drum_tower(surf, top_rect, bot_rect, pal, SEED)
    return surf


def _render_pair(pal):
    surf = _pair_surf(pal)
    cell = _sky_ground(CACHE_W, GROUND_Y, pal, 60)
    cell.blit(surf, (0, 0))
    guide = (255, 90, 90)
    for rim in (TOP_H, BOT_TOP):
        for x in range(0, CACHE_W, 8):
            pygame.draw.line(cell, guide, (x, rim), (x + 4, rim), 1)
    win = cell.subsurface(pygame.Rect(0, CROP_TOP, CACHE_W, CROP_BOT - CROP_TOP)).copy()
    return win


def _measure_clearance(pal):
    """Nearest crown-vane pixel of each mirrored section to its gap rim, in the
    centre columns where the vane lives (px)."""
    surf = _pair_surf(pal)
    cx = MARGIN + PIPE_W // 2
    core = lambda x: abs(x - cx) <= PIPE_W // 2 + 6
    top_low = -1
    for y in range(0, TOP_H + 10):
        if any(core(x) and surf.get_at((x, y))[3] > 50 for x in range(CACHE_W)):
            top_low = y
    bot_high = GROUND_Y
    for y in range(BOT_TOP - 10, GROUND_Y):
        if any(core(x) and surf.get_at((x, y))[3] > 50 for x in range(CACHE_W)):
            bot_high = y
            break
    return TOP_H - top_low, bot_high - BOT_TOP


def _measure_fill(pal, section_h):
    """Max vertical run (px) of rows with ZERO fill inside the PIPE_W collision
    column, for a bottom-only section of the given height."""
    surf = pygame.Surface((CACHE_W, GROUND_Y), pygame.SRCALPHA)
    bot_rect = pygame.Rect(MARGIN, GROUND_Y - section_h, PIPE_W, section_h)
    candidate_mani_drum_tower(surf, pygame.Rect(MARGIN, 0, PIPE_W, 0),
                              bot_rect, pal, SEED)
    cx = MARGIN + PIPE_W // 2
    x0, x1 = cx - PIPE_W // 2, cx + PIPE_W // 2
    run = worst = 0
    for y in range(GROUND_Y - section_h, GROUND_Y):
        filled = any(surf.get_at((x, y))[3] > 50 for x in range(x0, x1 + 1))
        run = 0 if filled else run + 1
        worst = max(worst, run)
    return worst


def _measure_scallop(pal, section_h=210):
    """Belly (max) and seam (min) silhouette half-width across the drum stack, in
    px from centre — the numeric proof the outline PINCHES at every seam instead
    of running as a flat pipe. Scans only the barrel band (vane + plinth rows
    excluded, since the plinth flares wider than the barrels)."""
    surf = pygame.Surface((CACHE_W, GROUND_Y), pygame.SRCALPHA)
    cx = MARGIN + PIPE_W // 2
    _draw_one(surf, cx, GROUND_Y, GROUND_Y - section_h, PIPE_W, pal, SEED, apron=False)
    vane_h = max(12, min(int(section_h * 0.14), 24))
    plinth_h = 6 if section_h > 60 else 3
    stack_top = (GROUND_Y - section_h) + vane_h + 2
    stack_bot = GROUND_Y - plinth_h - 2
    belly = seam = -1
    for y in range(stack_top, stack_bot):
        row_max = -1
        for x in range(CACHE_W):
            if surf.get_at((x, y))[3] > 50:
                row_max = max(row_max, abs(x - cx))
        if row_max < 0:
            continue
        belly = max(belly, row_max)
        seam = row_max if seam < 0 else min(seam, row_max)
    return belly, seam


def _render_feas(pal, section_h):
    head = 16
    cell_h = section_h + head + 10
    surf = pygame.Surface((CACHE_W, GROUND_Y), pygame.SRCALPHA)
    bot_rect = pygame.Rect(MARGIN, GROUND_Y - section_h, PIPE_W, section_h)
    candidate_mani_drum_tower(surf, pygame.Rect(MARGIN, 0, PIPE_W, 0),
                              bot_rect, pal, SEED)
    cell = _sky_ground(CACHE_W, cell_h, pal, 10)
    crop_top = GROUND_Y - section_h - head
    cell.blit(surf, (0, 0), pygame.Rect(0, crop_top, CACHE_W, cell_h))
    cx = MARGIN + PIPE_W // 2
    for ex in (cx - PIPE_W // 2, cx + PIPE_W // 2):
        pygame.draw.line(cell, (255, 60, 60), (ex, 0), (ex, cell_h), 1)
    return cell, cell_h


def _render_blackout(pal, section_h=230):
    surf = pygame.Surface((CACHE_W, GROUND_Y), pygame.SRCALPHA)
    bot_rect = pygame.Rect(MARGIN, GROUND_Y - section_h, PIPE_W, section_h)
    candidate_mani_drum_tower(surf, pygame.Rect(MARGIN, 0, PIPE_W, 0),
                              bot_rect, pal, SEED)
    crop_top = GROUND_Y - section_h - 26
    crop = surf.subsurface(pygame.Rect(0, crop_top, CACHE_W, section_h + 26)).copy()
    mask = pygame.mask.from_surface(crop, 60)
    return mask.to_surface(setcolor=(18, 18, 22, 255),
                           unsetcolor=(232, 232, 236, 255))


def main():
    pygame.init()
    pygame.display.set_mode((1, 1))
    day = biome.palette_for_phase(PHASE_DAY)
    night = biome.palette_for_phase(PHASE_NIGHT)

    pair_day = _render_pair(day)
    pair_night = _render_pair(night)
    cl_day = _measure_clearance(day)
    cl_night = _measure_clearance(night)

    heights = [70, 210, 355]
    feas = [_render_feas(day, h) for h in heights]
    fills = {h: _measure_fill(day, h) for h in heights}
    blackout = _render_blackout(day)
    scal_day = _measure_scallop(day)
    scal_night = _measure_scallop(night)

    pad = 14
    label_h = 22
    title_h = 60
    pw, ph = pair_day.get_width(), pair_day.get_height()

    title = pygame.font.SysFont(None, 30)
    sub = pygame.font.SysFont(None, 18)
    label = pygame.font.SysFont(None, 19)

    left_w = pad + pw + pad + pw + pad
    feas_w = max(c.get_width() for c, _ in feas)
    right_w = feas_w + pad * 2
    sheet_w = left_w + right_w

    bo_w, bo_h = blackout.get_width(), blackout.get_height()
    left_h = title_h + ph + label_h + pad + bo_h + label_h + 20 + pad
    feas_col_h = title_h + sum(ch + label_h + pad for _, ch in feas) + 24
    sheet_h = max(left_h, feas_col_h) + pad

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((24, 25, 30))

    sheet.blit(title.render("mani-drum-tower — round 2", True, (245, 240, 230)),
               (pad, 12))
    sheet.blit(sub.render("stacked rotating copper prayer-drums (body IS the "
                          "mechanism) + wind cross-vane  ·  mirrored pair, day + night",
                          True, (170, 172, 182)), (pad, 40))

    for i, (pair, name, cl) in enumerate((
            (pair_day, f"DAY  PHASE={PHASE_DAY}", cl_day),
            (pair_night, f"NIGHT  PHASE={PHASE_NIGHT}", cl_night))):
        hx = pad + i * (pw + pad)
        hy = title_h
        sheet.blit(pair, (hx, hy))
        pygame.draw.rect(sheet, (60, 62, 72), (hx, hy, pw, ph), 1)
        lab = label.render(name, True, (255, 224, 150))
        sheet.blit(lab, (hx + (pw - lab.get_width()) // 2, hy + ph + 3))
        cl2 = sub.render(f"vane clear: top {cl[0]}px  bot {cl[1]}px", True,
                         (200, 202, 212))
        sheet.blit(cl2, (hx + (pw - cl2.get_width()) // 2, hy + ph + 3 + 18))

    bx = pad
    by = title_h + ph + label_h + pad + 14
    sheet.blit(blackout, (bx, by))
    pygame.draw.rect(sheet, (60, 62, 72), (bx, by, bo_w, bo_h), 1)
    lab = label.render("BLACKOUT — 58px silhouette read", True, (255, 224, 150))
    sheet.blit(lab, (bx, by + bo_h + 3))
    scl = sub.render(f"scallop: belly {scal_day[0]}px / seam {scal_day[1]}px  "
                     f"(delta {scal_day[0] - scal_day[1]}px)", True, (200, 202, 212))
    sheet.blit(scl, (bx, by + bo_h + 3 + 18))

    fx = left_w + pad
    fy = title_h
    sheet.blit(sub.render("FEASIBILITY — collision-column fill (red = PIPE_W)",
                          True, (255, 224, 150)), (fx, fy - 22))
    for (cell, ch), h in zip(feas, heights):
        sheet.blit(cell, (fx, fy))
        pygame.draw.rect(sheet, (60, 62, 72), (fx, fy, cell.get_width(), ch), 1)
        lab = label.render(f"{h}px  ·  max empty run {fills[h]}px", True,
                           (210, 212, 222))
        sheet.blit(lab, (fx, fy + ch + 3))
        fy += ch + label_h + pad

    out = _REPO / "docs" / "pillar_landmarks" / "windmills" / "mani-drum-tower" / "round_2.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(sheet, out)
    print(f"wrote {out}  ({sheet.get_width()}x{sheet.get_height()})")
    print(f"vane clearance day  top={cl_day[0]}px bot={cl_day[1]}px")
    print(f"vane clearance night top={cl_night[0]}px bot={cl_night[1]}px")
    print("max empty run: " + "  ".join(f"{h}px->{fills[h]}px" for h in heights))
    print(f"scallop day   belly={scal_day[0]}px seam={scal_day[1]}px "
          f"delta={scal_day[0] - scal_day[1]}px")
    print(f"scallop night belly={scal_night[0]}px seam={scal_night[1]}px "
          f"delta={scal_night[0] - scal_night[1]}px")


if __name__ == "__main__":
    main()
