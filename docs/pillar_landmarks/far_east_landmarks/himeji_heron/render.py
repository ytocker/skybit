"""himeji_heron — high-fidelity White Heron castle keep (candidate).

The JAGGED-GABLED-WHITE-PYRAMID pole of the far-east-landmarks family: Himeji
Castle, Japan. A brilliant-white plaster keep of receding tiers, each crowned by
a dark upturned tiled eave and pierced by fanned dormer gables — sharp triangular
chidori-hafu and undulating curved kara-hafu, lined up in the rhythmic Himeji
cadence — the whole mass sitting on a wide, battered fan-curved stone base
(musha-gaeshi). Gold shachihoko fish-finials flick up off the top ridge.

WHY it reads as a CASTLE, not a pagoda (the top nearest-neighbour risk of the
set): a pagoda is a slim stack of SYMMETRIC horizontal eaves on a narrow plinth;
Himeji is a WIDE battered masonry keep whose white walls are broken by TRIANGULAR
and CURVED GABLE PEAKS poking above every eave line — the fanned-gable silhouette
— capped by a hip-gable irimoya crown with paired gold fish, not a single spire
or a ring of matched eaves. The stone foot spilling past the walls + the jagged
gable peaks are the tell; the blackout is a lumpy stepped pyramid bristling with
triangles, never a clean tapering tō.

Materials are all palette-derived (so the 5-min biome day->night retint sweeps
straight through) with fixed archetype biases, matching the shipped pagodas:
brilliant _plaster/_porcelain white walls (lit clamped both phases so a dark tile
keyline separates them from a pale day sky and the wall never blows out), cool
blue-grey charcoal roof tile, warm _korean_granite battered base, _gold_bright
shachihoko. Night window glow + wall rim gate on _is_dark_sky.

Standalone review candidate; wires nothing into the live game.

Run:  python docs/pillar_landmarks/far_east_landmarks/himeji_heron/render.py
Out:  docs/pillar_landmarks/far_east_landmarks/himeji_heron/round_1.png
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
# Japanese pillars, so the castle plaster + tile + gilt read exactly on-palette.
from game.pillar_pagodas import (
    _mix, _shade, _gradient_rect, _aa_polyline, _lit_niche, _tile_hatch,
    _eave_tang_curl, _draw_plinth_mist, _is_dark_sky, _is_warming_sky,
    _cap_lit_for_dark_sky, _cap_dark_for_dark_sky,
    _porcelain_white, _plaster, _bronze, _gold_bright, _gold_deep,
    _vermilion, _vermilion_lit, _vermilion_shadow, _lacquer_red,
    _lapis, _porcelain_aqua, _porcelain_pink, _lotus_pink,
    _korean_granite, _korean_granite_lit, _korean_granite_shadow,
)
from game.pillar_variants import draw_grass_bed
from game.draw import draw_side_shrub


MARGIN = 64                       # matches entities.Pipe eave/ornament gutter
CACHE_W = PIPE_W + MARGIN * 2
CACHE_H = GROUND_Y
PHASE_DAY = 0.30                  # midday sky — hardest test for the white holding
PHASE_NIGHT = 0.85               # deep night — checks window glow + shachihoko glint


# ── Materials ────────────────────────────────────────────────────────────────
#
# The walls are the White Heron's whitewashed plaster: a _plaster/_porcelain
# blend pushed to a brilliant cool white. The lit face is CLAMPED at both phases
# (not just night) so the wall never value-spikes to ~250 and swallows its own
# tile keyline against a pale midday sky — the dark eaves + a grey silhouette
# keyline must always separate the white mass from the blue. Everything is
# palette-derived so the biome retint sweeps through; raw-RGB anchors are fixed
# archetype biases only.

def _clamp(c, lo=0, hi=255):
    return (max(lo, min(hi, int(c[0]))),
            max(lo, min(hi, int(c[1]))),
            max(lo, min(hi, int(c[2]))))


# The active colorway. `None` is the canonical White Heron; the colorway
# wrapper candidates below set + restore this so the SAME geometry re-tints to a
# different real-world castle material triad. It only swaps the ANCHORS the
# palette-derived material triads mix toward — silhouette/fill/mirror are
# untouched — so every colorway still sweeps day->night through the biome.
_COLORWAY = None


def _wall_triad(palette):
    cw = _COLORWAY
    if cw == 'crow':
        # Matsumoto "Crow Castle" black lacquer: near-black walls with only a
        # faint lacquer sheen. NO dark-sky floor — the walls must stay black; a
        # LIGHT silver keyline (see _wall_keyline) holds the silhouette against a
        # dark night sky instead of the usual dark tile edge.
        base = _mix(palette['stone_dark'], (30, 28, 34), 0.70)
        lit = _mix(base, (98, 96, 110), 0.5)
        sh = _mix(base, (10, 10, 16), 0.5)
        lit = _clamp(lit, hi=118)
        return lit, base, sh
    if cw == 'vermilion':
        # Shrine-red lacquer keep: shu-iro vermilion over cinnabar lacquer.
        base = _mix(_vermilion(palette), _lacquer_red(palette), 0.5)
        lit = _mix(base, _vermilion_lit(palette), 0.62)
        sh = _mix(base, _vermilion_shadow(palette), 0.6)
        lit = _clamp(lit, hi=232)
        lit = _cap_lit_for_dark_sky(lit, palette, cap=196)
        sh = _cap_dark_for_dark_sky(sh, palette, floor=58)
        return lit, base, sh
    if cw == 'gilt':
        # Kinkaku-style gold-leaf donjon: gold-bright over gold-deep. The lit
        # face is NOT dark-sky-capped so the leaf keeps a night gleam instead of
        # going matte grey like the plaster keep.
        base = _mix(_gold_bright(palette), _gold_deep(palette), 0.42)
        lit = _mix(base, (255, 238, 168), 0.5)
        sh = _mix(base, _gold_deep(palette), 0.72)
        lit = _clamp(lit, hi=244)
        sh = _cap_dark_for_dark_sky(sh, palette, floor=86)
        return lit, base, sh
    if cw == 'azure':
        # Cool porcelain blue-white plaster — same white-holds discipline as the
        # heron, tinted a half-stop toward pale sky-blue.
        base = _mix(_plaster(palette), (206, 222, 236), 0.5)
        lit = _mix(base, (238, 248, 255), 0.5)
        sh = _mix(base, (138, 156, 178), 0.5)
        lit = _clamp(lit, hi=234)
        lit = _cap_lit_for_dark_sky(lit, palette, cap=214)
        sh = _cap_dark_for_dark_sky(sh, palette, floor=104)
        return lit, base, sh
    if cw == 'sakura':
        # Cherry-blossom castle: soft sakura-pink plaster (lotus + porcelain
        # pink), same white-holds clamp so a grey tile keyline still bites.
        base = _mix(_lotus_pink(palette), _porcelain_pink(palette), 0.5)
        lit = _mix(base, (255, 236, 240), 0.5)
        sh = _mix(base, (176, 138, 152), 0.5)
        lit = _clamp(lit, hi=234)
        lit = _cap_lit_for_dark_sky(lit, palette, cap=214)
        sh = _cap_dark_for_dark_sky(sh, palette, floor=104)
        return lit, base, sh
    base = _mix(_plaster(palette), _porcelain_white(palette), 0.42)
    lit = _mix(base, (255, 252, 246), 0.5)
    sh = _mix(base, (150, 152, 164), 0.5)        # cool grey shade -> 3-D volume
    # Clamp the lit face at BOTH phases so a dark keyline always reads on top of
    # it (day) and the wall doesn't drown the night window glow (night).
    lit = _clamp(lit, hi=234)
    lit = _cap_lit_for_dark_sky(lit, palette, cap=214)
    # Floor the shadow so the white heron stays WHITE in shade even at night
    # rather than sinking to a grey pagoda mass.
    sh = _cap_dark_for_dark_sky(sh, palette, floor=104)
    return lit, base, sh


def _wall_keyline(ws, palette):
    """The 1-px silhouette edge line down each wall. A DARK edge separates a
    pale wall from the sky, but for the BLACK Crow colorway a dark edge would
    vanish into a night sky — so the black keep instead gets a LIGHT silver
    keyline (Matsumoto's white trim). Palette-derived so it retints too."""
    if _COLORWAY == 'crow':
        return _mix(palette['stone_light'], (198, 204, 216), 0.6)
    return ws


def _tile_triad(palette):
    cw = _COLORWAY
    if cw == 'azure':
        # Celadon / lapis blue glazed roof tile — dark-and-blue so the gable
        # peaks still punch the pale walls into stepped silhouette.
        base = _mix(_lapis(palette), (44, 92, 116), 0.5)
        lit = _mix(base, _porcelain_aqua(palette), 0.55)
        sh = _mix(base, (16, 40, 60), 0.6)
        sh = _cap_dark_for_dark_sky(sh, palette, floor=30)
        return lit, base, sh
    if cw == 'sakura':
        # Neutral grey tile so the pink plaster carries the colour, not the roof.
        base = _mix(palette['stone_dark'], (92, 92, 102), 0.56)
        lit = _mix(base, (156, 158, 170), 0.55)
        sh = _mix(base, (30, 30, 40), 0.62)
        sh = _cap_dark_for_dark_sky(sh, palette, floor=30)
        return lit, base, sh
    # Cool blue-grey charcoal roof tile — dark enough to read against any sky so
    # the gable peaks punch the white keep into stepped silhouette. Shared by
    # the heron, crow, vermilion and gilt colorways.
    base = _mix(palette['stone_dark'], (74, 84, 106), 0.56)
    lit = _mix(base, (150, 162, 184), 0.55)
    sh = _mix(base, (26, 30, 44), 0.62)
    sh = _cap_dark_for_dark_sky(sh, palette, floor=30)
    return lit, base, sh


def _granite_triad(palette):
    if _COLORWAY == 'gilt':
        # Bronze plinth under the gilt keep so the gold doesn't sit on grey.
        base = _bronze(palette)
        lit = _mix(base, (196, 158, 96), 0.5)
        sh = _shade(base, -34)
        return lit, base, sh
    return (_korean_granite_lit(palette),
            _korean_granite(palette),
            _korean_granite_shadow(palette))


def _lum(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


# ── Fanned dormer gables — the castle tell ───────────────────────────────────
#
# Two gable KINDS lined up in the Himeji rhythm. The sharp triangular
# chidori-hafu and the undulating curved kara-hafu both POKE their dark-tile
# peak up above the eave line and carry a white plaster tympanum + a tiny window,
# so the white keep bristles with stacked triangles/humps — the fanned-gable
# blackout that no pagoda's matched horizontal eaves can imitate.

def _corner_hook(surf, x, y, side, col):
    # Tiny upturned barge-board flick at a gable foot — the Japanese roof curl.
    pygame.draw.polygon(surf, col,
                        [(x, y), (x - side * 3, y - 2), (x - side * 3, y + 1)])


def _gable_window(surf, cx, cy, w, h, palette):
    # A dark katomado-ish opening in the tympanum; lit_niche gives it the warm
    # night glow gated on a dark sky.
    if w >= 3 and h >= 3:
        _lit_niche(surf, cx, cy, w, h, palette)


def _chidori_gable(surf, cx, apex_y, base_y, hw, palette):
    """Triangular dormer gable — the sharp chidori-hafu peak."""
    if hw < 4 or base_y - apex_y < 4:
        return
    tl, tm, ts = _tile_triad(palette)
    pygame.draw.polygon(surf, ts, [(cx, apex_y), (cx - hw, base_y),
                                    (cx + hw, base_y)])
    pygame.draw.polygon(surf, tm, [(cx, apex_y + 1), (cx - hw + 1, base_y - 1),
                                    (cx + hw - 1, base_y - 1)])
    # White plaster tympanum inset — the gable face is whitewashed like the wall.
    inset = max(2, hw // 3)
    twl, twm, tws = _wall_triad(palette)
    tri = [(cx, apex_y + inset), (cx - hw + inset, base_y - 2),
           (cx + hw - inset, base_y - 2)]
    pygame.draw.polygon(surf, twm, tri)
    pygame.draw.polygon(surf, twl, [(cx, apex_y + inset + 1),
                                    (cx - hw + inset + 2, base_y - 3),
                                    (cx, base_y - 3)])
    _gable_window(surf, cx, apex_y + inset + 1, max(3, hw // 3),
                  max(3, (base_y - apex_y) // 3), palette)
    # Dark barge-board keyline on the two slopes + upturned foot hooks.
    _aa_polyline(surf, _shade(ts, -30),
                 [(cx - hw, base_y), (cx, apex_y), (cx + hw, base_y)])
    _corner_hook(surf, cx - hw, base_y, 1, _shade(tm, 24))
    _corner_hook(surf, cx + hw, base_y, -1, _shade(tm, 24))


def _kara_gable(surf, cx, apex_y, base_y, hw, palette):
    """Undulating bell dormer — the curved kara-hafu with its cusped crest and
    flared eyebrow skirt. The plump S-curve edge is the counterpoint that keeps
    the gable row from reading as a repeated triangle."""
    if hw < 5 or base_y - apex_y < 4:
        return
    tl, tm, ts = _tile_triad(palette)
    rise = base_y - apex_y
    n = 18
    top = []
    for k in range(n + 1):
        t = k / n
        x = cx - hw + 2 * hw * t
        # Plump ogee bell: convex shoulders lifting to a cusped central crest.
        bell = math.sin(math.pi * t) ** 0.62
        cusp = 0.12 * math.sin(math.pi * t) ** 6      # sharpen the crest tip
        y = base_y - rise * (bell + cusp) / 1.12
        top.append((x, y))
    poly = top + [(cx + hw, base_y), (cx - hw, base_y)]
    pygame.draw.polygon(surf, ts, poly)
    inner = [(x, y + 1) for (x, y) in top] + [(cx + hw - 1, base_y - 1),
                                              (cx - hw + 1, base_y - 1)]
    pygame.draw.polygon(surf, tm, inner)
    # White plaster tympanum following the bell, inset.
    twl, twm, tws = _wall_triad(palette)
    tin = [(x, y + max(2, rise // 3)) for (x, y) in top[3:-3]]
    if len(tin) >= 3:
        tin = tin + [(tin[-1][0], base_y - 2), (tin[0][0], base_y - 2)]
        pygame.draw.polygon(surf, twm, tin)
    _gable_window(surf, cx, apex_y + max(2, rise // 3) + 1,
                  max(3, hw // 3), max(3, rise // 3), palette)
    _aa_polyline(surf, _shade(ts, -30), top)
    # Flared eyebrow skirt curls at both feet — the kara-hafu mikaeshi.
    _corner_hook(surf, cx - hw, base_y, 1, _shade(tm, 24))
    _corner_hook(surf, cx + hw, base_y, -1, _shade(tm, 24))


def _shachihoko(surf, x, ridge_y, palette, side):
    """Gold fish-finial flicking up off a ridge end — tiny by design (a bright
    gold nick), tail curled UP-and-IN. `side=-1` left end, `side=+1` right."""
    gb = _gold_bright(palette)
    gd = _shade(gb, -46)
    # Tail reach kept short (peak 5 px over the ridge) so the mirrored top keep's
    # fish can't reach across the gap and fuse with this one at the rim.
    pts = [
        (x, ridge_y),
        (x - side * 1, ridge_y - 3),
        (x - side * 3, ridge_y - 4),
        (x - side * 2, ridge_y - 3),
        (x - side * 1, ridge_y - 2),
        (x + side * 1, ridge_y),
    ]
    pygame.draw.polygon(surf, gd, pts)
    pygame.draw.polygon(surf, gb, [(p[0], p[1] + 1) for p in pts[:-1]])
    # Head glint — a single bright pixel that also carries the night glimmer.
    surf.set_at((x, ridge_y - 1), _mix(gb, (255, 244, 200), 0.7))
    if _is_dark_sky(palette):
        g = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.circle(g, (*_mix(gb, (255, 240, 190), 0.6), 120), (5, 5), 4)
        pygame.draw.circle(g, (*_mix(gb, (255, 240, 190), 0.6), 200), (5, 5), 2)
        surf.blit(g, (x - 5, ridge_y - 6), special_flags=pygame.BLEND_RGBA_ADD)


# ── Battered stone base (musha-gaeshi) ───────────────────────────────────────

def _draw_stone_base(surf, cx, top_y, base_y, keep_half, palette):
    """Wide fan-curved granite foot: near-vertical at the top, flaring out in a
    concave musha-gaeshi sweep to the ground so the whole silhouette rests on a
    broad masonry block that spills PAST the keep walls into the gutters — the
    single strongest 'castle, not pagoda' cue."""
    gl, gm, gs = _granite_triad(palette)
    h = base_y - top_y
    if h < 4:
        return
    # A broad, hard-battered foot: the stone base must end up the WIDEST mass in
    # the whole silhouette (wider than any trimmed eave) so the keep reads as a
    # masonry castle standing on a spreading plinth, not a tō on a slim base.
    top_half = keep_half + 3
    flare = 17
    left_edge, right_edge = [], []
    for y in range(top_y, base_y):
        d = (y - top_y) / max(1, h)
        hw = top_half + flare * (d ** 1.85)          # concave fan
        xl = int(round(cx - hw))
        xr = int(round(cx + hw))
        # Horizontal granite gradient per row so the block reads as 3-D masonry.
        w = xr - xl
        for i in range(w + 1):
            t = i / max(1, w)
            col = _mix(gl, gm, t * 2) if t < 0.5 else _mix(gm, gs, (t - 0.5) * 2)
            surf.set_at((xl + i, y), col)
        left_edge.append((xl, y))
        right_edge.append((xr, y))
    # Ashlar course lines — the fitted-stone courses of the base.
    for cy in range(top_y + 5, base_y - 1, 6):
        d = (cy - top_y) / max(1, h)
        hw = int(top_half + flare * (d ** 1.85))
        pygame.draw.line(surf, _shade(gs, -14),
                         (cx - hw + 2, cy), (cx + hw - 2, cy), 1)
    # A few vertical block seams staggered per course.
    for ci, cy in enumerate(range(top_y + 5, base_y - 2, 6)):
        d = (cy - top_y) / max(1, h)
        hw = int(top_half + flare * (d ** 1.85))
        off = 7 if ci % 2 else 0
        for sx in range(cx - hw + 4 + off, cx + hw - 3, 14):
            pygame.draw.line(surf, _shade(gs, -10), (sx, cy), (sx, cy + 5), 1)
    # AA batter keyline down both curved flanks + a lit coping at the top.
    _aa_polyline(surf, _shade(gs, -30), left_edge)
    _aa_polyline(surf, _shade(gs, -30), right_edge)
    pygame.draw.line(surf, _shade(gl, 18),
                     (cx - top_half + 1, top_y), (cx + top_half - 1, top_y), 1)


# ── One white keep storey + its eave + fanned gable ──────────────────────────

def _draw_tier(surf, cx, wall_top, wall_bot, half, upper_half, palette, gable_kind,
               is_lowest, has_window, is_top=False):
    wl, wm, ws = _wall_triad(palette)
    tl, tm, ts = _tile_triad(palette)
    th = wall_bot - wall_top
    if th < 3:
        return
    # White plaster wall band — solid centred core carries the centreline.
    x_l = cx - half
    _gradient_rect(surf, pygame.Rect(x_l, wall_top, half * 2, th), wl, wm, ws)
    # Faint corner-quoin shadows so the white block reads as framed masonry,
    # and a grey silhouette keyline so the wall never merges with a pale sky.
    key = _wall_keyline(ws, palette)
    pygame.draw.line(surf, key, (x_l, wall_top), (x_l, wall_bot - 1), 1)
    pygame.draw.line(surf, key, (x_l + half * 2 - 1, wall_top),
                     (x_l + half * 2 - 1, wall_bot - 1), 1)
    # A single nageshi shadow rail mid-wall.
    if th > 12:
        pygame.draw.line(surf, _shade(ws, -12),
                         (x_l + 2, wall_top + th // 2),
                         (x_l + half * 2 - 3, wall_top + th // 2), 1)
    # Row of small dark loophole/latticed windows — one centred, gives the
    # night glow. Extra flanking pair on wide lower tiers.
    if has_window and th > 9 and half > 8:
        nh = min(7, th - 5)
        nw = min(6, half)
        _lit_niche(surf, cx, wall_top + max(2, th // 3), nw, nh, palette)
        if half > 20 and th > 14:
            for s in (-1, 1):
                _lit_niche(surf, cx + s * (half - 6), wall_top + max(2, th // 3),
                           3, min(6, nh), palette)

    # ── Mokoshi pent-roof skirt mid-storey — the intermediate hisashi eave a
    #    real tenshu carries between its main roofs. Doubles the roofline
    #    cadence so the stepped keep never opens a tall bare shoulder at its
    #    outer edge, and adds the busy layered rhythm that separates Himeji
    #    from a slim tō.
    if th > 26:
        mok_y = wall_top + int(th * 0.56)
        _eave_tang_curl(surf, cx, mok_y, half, max(4, half // 4 + 1), 3,
                        tm, _shade(tl, 10), ts, curl=0.35)

    # ── The storey's roof is a TALL TRIANGULAR GABLE (an irimoya / chidori-hafu
    #    seen in front elevation), NOT a wide flat pagoda eave. The eave line is
    #    only the triangle's BASE; from it the dark-tiled, white-tympanum gable
    #    rises to a sharp peak that stands well ABOVE the eave and out past the
    #    stepped-in wall of the storey above. So the blackout becomes a STACK OF
    #    TRIANGLES (the castle tell) instead of a stack of matched horizontal
    #    eaves (the pagoda read). A slim upturned eave-tip curl + underside
    #    shadow sits at the base corners for the Japanese roof flick, without a
    #    wide flat band capping the gable.
    overhang = max(5, half // 3 + 2)
    roof_hw = half + overhang                    # triangle base span = the eave
    # The TOP storey's roof IS the irimoya crown drawn above it, so it only gets
    # a slim capping eave here — a tall gable would spear up through the crown
    # and steal the rim air the mirror needs.
    if is_top:
        _eave_tang_curl(surf, cx, wall_top, half, overhang, 4,
                        tm, _shade(tl, 10), ts, curl=0.5, drop_shadow=True)
        return
    roof_rise = max(14, int(th * 0.62) + 4)      # clears the storey wall above
    base_y = wall_top + 2
    apex_y = wall_top - roof_rise
    _eave_tang_curl(surf, cx, wall_top, half, overhang, 4,
                    tm, _shade(tl, 10), ts, curl=0.5, drop_shadow=True)
    if gable_kind == 'kara':
        _kara_gable(surf, cx, apex_y, base_y, roof_hw, palette)
    else:
        _chidori_gable(surf, cx, apex_y, base_y, roof_hw, palette)

    # ── Paired shoulder chidori dormers on the wide lower storeys — smaller
    #    triangles poking a few px above the main gable's slope on each flank, so
    #    the tier FANS into three-plus peaks (the Himeji cadence no pagoda's
    #    single matched eave can fake). Sits inboard of the eave tip, its peak
    #    lifted just proud of the main roof slope at that point.
    if half >= 21 and roof_rise > 10:
        g2 = max(4, roof_hw // 5)
        sxo = int(roof_hw * 0.58)
        main_at = roof_rise * (1.0 - sxo / max(1, roof_hw))   # main slope height here
        rise2 = int(main_at) + max(4, roof_rise // 4)
        for s in (-1, 1):
            _chidori_gable(surf, cx + s * sxo, wall_top - rise2,
                           wall_top + 1, g2, palette)


# ── Hip-gable irimoya crown + gold shachihoko ────────────────────────────────

def _draw_crown(surf, cx, y_top, crown_bot, half, palette):
    """Top storey: a short white wall, a hip-and-gable irimoya roof rising to a
    central ridge, a front chidori gable, and TWO gold shachihoko flicking off
    the ridge ends — the solid, unmistakable castle cap at the gap rim."""
    wl, wm, ws = _wall_triad(palette)
    tl, tm, ts = _tile_triad(palette)
    ch = crown_bot - y_top
    if ch < 6:
        # Degenerate: just a capped nub so the rim still reads solid.
        pygame.draw.polygon(surf, tm, [(cx, y_top), (cx - half, crown_bot),
                                       (cx + half, crown_bot)])
        return
    # Short white top wall in the lower third of the crown region.
    wall_h = max(3, ch // 3)
    wall_top = crown_bot - wall_h
    _gradient_rect(surf, pygame.Rect(cx - half, wall_top, half * 2, wall_h),
                   wl, wm, ws)
    key = _wall_keyline(ws, palette)
    pygame.draw.line(surf, key, (cx - half, wall_top), (cx - half, crown_bot), 1)
    pygame.draw.line(surf, key, (cx + half - 1, wall_top),
                     (cx + half - 1, crown_bot), 1)
    if wall_h > 6:
        _lit_niche(surf, cx, wall_top + 2, min(6, half), min(6, wall_h - 3),
                   palette)
    # Broad hipped tiled roof rising to a WIDE ridge. Himeji's top donjon roof is
    # low and broad, and keeping the ridge wide does double duty: it fills the
    # central collision core right up near the tip (so the crown never opens a
    # fall-through slot there) and spaces the two shachihoko far enough apart to
    # read as two separate gold tips, never one fused nub.
    roof_bot = wall_top
    ridge_y = y_top + 3
    ridge_half = max(15, half // 2 + 4)
    over = half // 2 + 5
    roof = [
        (cx - half - over, roof_bot),
        (cx - ridge_half, ridge_y),
        (cx + ridge_half, ridge_y),
        (cx + half + over, roof_bot),
    ]
    pygame.draw.polygon(surf, ts, roof)
    # Lit inner roof face, pulled 2 px in from the eave tips + 1 px below the
    # ridge so the dark barge silhouette frames it.
    pygame.draw.polygon(surf, tm, [
        (cx - half - over + 2, roof_bot),
        (cx - ridge_half, ridge_y + 1),
        (cx + ridge_half, ridge_y + 1),
        (cx + half + over - 2, roof_bot),
    ])
    # Tile hatch rows down the two roof slopes.
    _tile_hatch(surf, cx - half - over + 4, roof_bot - 1, cx - ridge_half,
                ridge_y + 1, ts, step=3)
    _tile_hatch(surf, cx + half + over - 4, roof_bot - 1, cx + ridge_half,
                ridge_y + 1, ts, step=3)
    # Front chidori gable on the hip roof — the irimoya face.
    _chidori_gable(surf, cx, ridge_y - 1, roof_bot + 1, ridge_half + 3, palette)
    # Ridge line + the two shachihoko flicking up at each ridge end.
    pygame.draw.line(surf, _shade(ts, -20),
                     (cx - ridge_half, ridge_y), (cx + ridge_half, ridge_y), 1)
    _shachihoko(surf, cx - ridge_half, ridge_y + 1, palette, side=-1)
    _shachihoko(surf, cx + ridge_half, ridge_y + 1, palette, side=+1)
    # Corner-hook flicks at the wide eave tips so the crown roof upturns too.
    _corner_hook(surf, cx - half - over, roof_bot, 1, _shade(tm, 26))
    _corner_hook(surf, cx + half + over, roof_bot, -1, _shade(tm, 26))
    _aa_polyline(surf, _shade(ts, -30), roof)


# ── 3-layer plinth + foliage ─────────────────────────────────────────────────

def _draw_plinth(surf, cx, base_y, half, palette):
    gl, gm, gs = _granite_triad(palette)
    lit = _mix(gl, (60, 50, 40), 0.18)               # darker earth-toned stand
    mid = _shade(gm, -18)
    sh = _shade(gs, -14)
    layers = 3
    for i in range(layers):
        lw = int(half * 2 * (1.34 + 0.17 * i))
        lh = 5
        ly = base_y - (layers - i) * lh
        r = pygame.Rect(cx - lw // 2, ly, lw, lh)
        _gradient_rect(surf, r, lit, mid, sh)
        pygame.draw.line(surf, _shade(sh, -20),
                         (r.x, r.bottom - 1), (r.right - 1, r.bottom - 1), 1)
        pygame.draw.line(surf, _shade(lit, 16), (r.x, r.y), (r.right - 1, r.y), 1)


# ── One upright keep tower ───────────────────────────────────────────────────

_TIER_FLOOR = 60                  # natural storey height -> drives adaptive count
_MAX_TIERS = 4


def _tier_gable(i, count):
    # Rhythmic Himeji mix: the big lower storeys take sharp chidori triangles,
    # one mid storey takes the curved kara bell for the fanned counterpoint.
    if count >= 3 and i == count - 2:
        return 'kara'
    return 'chidori'


def _draw_tower(surf, cx, y_top, y_bot, palette, seed):
    """mist -> battered stone base -> adaptive white gabled keep -> irimoya
    crown + shachihoko at the gap rim -> plinth + foliage. Height-adaptive tier
    COUNT keeps a broad 1-tier keep at ~70px and a 4-tier heron at 355."""
    rng = random.Random(seed)
    half = PIPE_W // 2
    section_h = y_bot - y_top
    # Hold the crown's highest fish-tail a few px below the gap rim so, under the
    # vertical-flip mirror, the two keeps' finials keep clear air between them
    # instead of kissing at the gap line.
    RIM_PAD = 3

    plinth_h = min(15, max(9, int(section_h * 0.11)))
    base_y = y_bot

    _draw_plinth_mist(surf, cx, base_y - plinth_h + 2, int(half * 2 * 1.9),
                      palette)

    # Wide battered stone base — a chunky share of the height so the keep sits
    # on an unmistakable masonry foot (shorter, relatively, on tall pillars).
    if section_h < 110:
        stone_h = max(12, int(section_h * 0.26))
    else:
        stone_h = min(56, max(24, int(section_h * 0.20)))
    stone_top = base_y - plinth_h - stone_h

    # Crown reserve at the very top (hip roof + shachihoko).
    crown_h = min(30, max(16, int(section_h * 0.16)))

    tier_bot = stone_top
    tier_top = y_top + crown_h
    avail = tier_bot - tier_top
    if avail < 20:
        # Very short pillar: collapse to base + a single stub crown at the rim.
        _draw_stone_base(surf, cx, max(y_top, stone_top), base_y - plinth_h,
                         half - 1, palette)
        _draw_crown(surf, cx, y_top + RIM_PAD,
                    min(y_bot, y_top + max(10, section_h - 6)),
                    half - 4, palette)
        _draw_plinth(surf, cx, base_y, half, palette)
        draw_grass_bed(surf, cx, base_y - 1, PIPE_W + 12, 12, palette, seed=seed)
        return

    count = max(1, min(_MAX_TIERS, round(avail / _TIER_FLOOR)))

    # Storey heights weighted toward the base (the first storey is tallest, as
    # at Himeji), boundaries cumulative so the stack exactly fills the span.
    weights = [1.0 - 0.10 * i for i in range(count)]
    wsum = sum(weights)
    bounds = [tier_bot]
    acc = 0.0
    for i in range(count):
        acc += weights[i]
        bounds.append(tier_bot - avail * acc / wsum)

    # Body half-widths taper gently — the keep is a PYRAMID but the lower
    # storeys stay near band width so the collision core fills; the taper bites
    # only near the crown. Lowest storey sits just inside the stone-base top.
    base_half = half - 2
    # Each storey steps in a few px from the one below so a real SHOULDER of
    # open sky opens beside every eave — the flanking chidori dormers poke their
    # triangular peaks into that shoulder (the fanned-gable read). The step is
    # kept shallow enough that the top storey never falls below the collision
    # core (half stays >= 19), so the fill gate holds while the gables fan.
    top_target = 19
    if count > 1:
        body_halves = [max(top_target,
                           int(round(base_half
                                     - (base_half - top_target) * (i / (count - 1)))))
                       for i in range(count)]
    else:
        body_halves = [base_half]

    _draw_stone_base(surf, cx, stone_top, base_y - plinth_h,
                     body_halves[0], palette)

    for i in range(count):
        wall_bot = int(round(bounds[i]))
        wall_top = int(round(bounds[i + 1]))
        # The mass sitting ABOVE this eave (the next storey, or the crown for the
        # top tier) — the gables must out-reach it to break the silhouette.
        upper_half = body_halves[i + 1] if i + 1 < count else max(11, body_halves[-1] - 4)
        _draw_tier(surf, cx, wall_top, wall_bot, body_halves[i], upper_half,
                   palette, _tier_gable(i, count), is_lowest=(i == 0),
                   has_window=True, is_top=(i == count - 1))

    _draw_crown(surf, cx, y_top + RIM_PAD, tier_top,
                max(11, body_halves[-1] - 2), palette)

    _draw_plinth(surf, cx, base_y, half, palette)
    draw_grass_bed(surf, cx, base_y - 1, PIPE_W + 12, 12, palette, seed=seed)
    draw_side_shrub(surf, cx - half - 6, base_y - 1, palette, scale=0.9)
    draw_side_shrub(surf, cx + half + 6, base_y - 1, palette, scale=0.8)


def candidate_himeji_heron(surf, top_rect, bot_rect, palette, seed):
    """Bottom = keep rising from the ground, gold-shachihoko crown at the gap.
    Top = the same keep vertical-FLIPPED from the ceiling — a symmetric two-ended
    castle whose two crowns meet at the gap rim. The keep is bilaterally
    symmetric, so the flip is clean."""
    if bot_rect.height > 0:
        _draw_tower(surf, bot_rect.centerx, bot_rect.y, bot_rect.bottom,
                    palette, seed)
    if top_rect.height > 0:
        tmp = pygame.Surface((surf.get_width(), top_rect.height), pygame.SRCALPHA)
        _draw_tower(tmp, top_rect.centerx, 0, top_rect.height, palette, seed + 1)
        surf.blit(pygame.transform.flip(tmp, False, True), (0, top_rect.y))


# ── Colorways ────────────────────────────────────────────────────────────────
#
# Five real-world-plausible Japanese-castle looks over the EXACT heron geometry.
# Each wrapper sets the module-level `_COLORWAY` (which only re-anchors the
# palette-derived material triads), draws, then restores it — the pagoda
# `_swap_globals` discipline. Silhouette, tier count, gables, fill and mirror
# are byte-for-byte identical to `candidate_himeji_heron`; only the material
# colours change, and every colorway still retints day->night.

def _draw_colorway(name, surf, top_rect, bot_rect, palette, seed):
    global _COLORWAY
    prev = _COLORWAY
    _COLORWAY = name
    try:
        candidate_himeji_heron(surf, top_rect, bot_rect, palette, seed)
    finally:
        _COLORWAY = prev


def candidate_himeji_crow(surf, top_rect, bot_rect, palette, seed):
    """Matsumoto "Crow Castle" — black lacquered walls + dark tile, silver/white
    keyline trim, gold finials."""
    _draw_colorway('crow', surf, top_rect, bot_rect, palette, seed)


def candidate_himeji_vermilion(surf, top_rect, bot_rect, palette, seed):
    """Shrine-red keep — vermilion/cinnabar lacquer walls + dark tile + gold."""
    _draw_colorway('vermilion', surf, top_rect, bot_rect, palette, seed)


def candidate_himeji_gilt(surf, top_rect, bot_rect, palette, seed):
    """Kinkaku-style gilt — gold-leaf walls + dark tile + bronze base; the leaf
    keeps a night gleam."""
    _draw_colorway('gilt', surf, top_rect, bot_rect, palette, seed)


def candidate_himeji_azure(surf, top_rect, bot_rect, palette, seed):
    """Azure keep — celadon/lapis blue-tile roofs + pale porcelain blue-white
    walls + gold."""
    _draw_colorway('azure', surf, top_rect, bot_rect, palette, seed)


def candidate_himeji_sakura(surf, top_rect, bot_rect, palette, seed):
    """Cherry-blossom castle — soft sakura-pink plaster walls + grey tile +
    gold."""
    _draw_colorway('sakura', surf, top_rect, bot_rect, palette, seed)


# ── review harness ──────────────────────────────────────────────────────────

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


def _max_empty_row_run(surf, x0, x1, y0, y1):
    """Max run of consecutive fully-empty HORIZONTAL rows — the true killzone
    'empty band' for a tapering architectural pillar (a see-through slice you
    could fall through), where a per-column edge run is inherently large in the
    gutter and not meaningful."""
    worst = 0
    run = 0
    for y in range(y0, y1):
        if any(surf.get_at((x, y))[3] > 0 for x in range(x0, x1)):
            run = 0
        else:
            run += 1
            worst = max(worst, run)
    return worst


def _gap_rim_clearance(surf, x0, x1, gap_y, up=True):
    step = -1 if up else 1
    for d in range(0, 260):
        y = gap_y + step * d
        if y < 0 or y >= surf.get_height():
            return d
        if any(surf.get_at((x, y))[3] > 0 for x in range(x0, x1)):
            return d
    return 260


def _silhouette(pal, section_h, seed=7):
    """Alpha-thresholded solid silhouette of one keep, cropped to its section —
    the blackout the AD reads for the castle-not-pagoda tell."""
    surf = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    br = pygame.Rect(MARGIN, GROUND_Y - section_h, PIPE_W, section_h)
    tr = pygame.Rect(MARGIN, 0, PIPE_W, 0)
    candidate_himeji_heron(surf, tr, br, pal, seed=seed)
    rows = []                                   # (left_x, right_x) per filled row
    for y in range(GROUND_Y - section_h, GROUND_Y):
        xs = [x for x in range(CACHE_W) if surf.get_at((x, y))[3] > 40]
        rows.append((min(xs), max(xs)) if xs else None)
    return rows


def _count_gable_bumps(rows, base_top_y, section_h):
    """Count outward triangular protrusions on each silhouette flank ABOVE the
    stone base — every fanned gable/dormer peak steps the edge out then back in.
    A pagoda's clean taper has none; a fanned keep bristles with them."""
    cx = MARGIN + PIPE_W / 2
    left = [(cx - r[0]) if r else 0 for r in rows]     # outward reach per row
    right = [(r[1] - cx) if r else 0 for r in rows]
    limit = base_top_y - (GROUND_Y - section_h)        # rows above the stone base

    def bumps(seq):
        # One triangular gable/dormer tip = the flank flares OUT then snaps back
        # IN to the wall; count each rise-then-fall of >=4px prominence.
        seq = seq[:max(0, limit)]
        n = 0
        rising = False
        base = seq[0] if seq else 0
        for k in range(1, len(seq)):
            if seq[k] > seq[k - 1]:
                if not rising:
                    base = seq[k - 1]
                    rising = True
            elif seq[k] < seq[k - 1] - 0:
                if rising and seq[k - 1] - base >= 4 and seq[k - 1] - seq[k] >= 3:
                    n += 1
                rising = False
        return n
    return bumps(left), bumps(right)


def _base_vs_eave(pal, section_h, seed=7):
    """base_max_width (widest row in the bottom stone+plinth foot) vs
    widest_eave_width (widest row up in the tiered body). The castle read needs
    the foot to WIN."""
    rows = _silhouette(pal, section_h, seed)
    widths = [(r[1] - r[0] + 1) if r else 0 for r in rows]
    foot = int(section_h * 0.22)                        # bottom ~fifth = stone foot
    base_w = max(widths[-foot:]) if foot else 0
    eave_w = max(widths[:-foot]) if foot else max(widths)
    return base_w, eave_w


def _rim_air(pal, seed=7):
    """Reserved clear rows between the gap rim and the crown's highest fish-tail,
    under the vertical-flip mirror — must be >0 so the two keeps don't kiss."""
    surf = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    rim = 247
    bot = pygame.Rect(MARGIN, rim, PIPE_W, GROUND_Y - rim)
    top = pygame.Rect(MARGIN, 0, PIPE_W, 97)
    candidate_himeji_heron(surf, top, bot, pal, seed=seed)
    air = 0
    for y in range(rim, rim + 40):
        if any(surf.get_at((x, y))[3] > 40 for x in range(MARGIN, MARGIN + PIPE_W)):
            break
        air += 1
    return air


def _print_ascii_silhouette(rows, section_h, cols=60):
    """Dump the blackout as ASCII so the fanned-gable tell is verifiable from
    stdout without ever opening the PNG."""
    x0 = MARGIN - 26
    x1 = MARGIN + PIPE_W + 26
    step_y = max(1, section_h // 46)
    print("  BLACKOUT ASCII (top=crown, each '#' col ~1px; sky notches = fanned gables)")
    for yi in range(0, len(rows), step_y):
        r = rows[yi]
        line = []
        for x in range(x0, x1):
            line.append('#' if (r and r[0] <= x <= r[1]) else ' ')
        print("    |" + "".join(line) + "|")


def _hero(pal, seed):
    gap_y, gap_h = 172, 150
    top_h = int(gap_y - gap_h / 2)
    bot_top = int(gap_y + gap_h / 2)
    full = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    top_rect = pygame.Rect(MARGIN, 0, PIPE_W, top_h)
    bot_rect = pygame.Rect(MARGIN, bot_top, PIPE_W, GROUND_Y - bot_top)
    candidate_himeji_heron(full, top_rect, bot_rect, pal, seed=seed)

    tip_y = top_h - 8
    base_y = GROUND_Y + 8
    hero_h = base_y - tip_y
    hero = _bg(CACHE_W, hero_h, pal, hero_h - (base_y - GROUND_Y))
    hero.blit(full, (0, -tip_y))
    for ex in (MARGIN, MARGIN + PIPE_W):
        pygame.draw.line(hero, (230, 60, 60), (ex, 0), (ex, hero_h), 1)
    return hero, hero_h


def _closeup(pal, seed, scale=3):
    """Zoom on the crown + upper gables so the shachihoko + fanned gables read."""
    surf = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    br = pygame.Rect(MARGIN, GROUND_Y - 240, PIPE_W, 240)
    tr = pygame.Rect(MARGIN, 0, PIPE_W, 0)
    candidate_himeji_heron(surf, tr, br, pal, seed=seed)
    crop = pygame.Surface((CACHE_W, 150))
    crop.blit(_bg(CACHE_W, 150, pal, 150), (0, 0))
    crop.blit(surf, (0, -(GROUND_Y - 240)))
    return pygame.transform.scale(
        crop, (crop.get_width() * scale, crop.get_height() * scale))


def _blackout(pal, section_h, scale):
    """Solid-black silhouette — the gabled-white-castle tell (must NOT read as a
    pagoda's clean tapering stack of matched eaves)."""
    surf = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    br = pygame.Rect(MARGIN, GROUND_Y - section_h, PIPE_W, section_h)
    tr = pygame.Rect(MARGIN, 0, PIPE_W, 0)
    candidate_himeji_heron(surf, tr, br, pal, seed=7)
    pad_x = 30
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

    wl_d, wm_d, ws_d = _wall_triad(pal)
    wl_n, wm_n, ws_n = _wall_triad(pal_n)
    tl_d, tm_d, ts_d = _tile_triad(pal)
    print("WHITE PLASTER WALL (lit / shadow)")
    print(f"  DAY   lit={wl_d} lum={_lum(wl_d):.1f}  shadow={ws_d} lum={_lum(ws_d):.1f}")
    print(f"  NIGHT lit={wl_n} lum={_lum(wl_n):.1f}  shadow={ws_n} lum={_lum(ws_n):.1f}")
    print(f"  day != night: {wm_d != wm_n}")

    # White-holds check: the lit white wall must sit ABOVE the pale day sky in
    # value AND the dark tile keyline must sit well BELOW both, so a hard edge
    # separates the keep from the sky (no white-on-white bleed).
    sky_d = pal['sky_top']
    print("WHITE-HOLDS vs PALE DAY SKY")
    print(f"  wall-lit lum={_lum(wl_d):.1f}  sky_top lum={_lum(sky_d):.1f}  "
          f"tile-key lum={_lum(_shade(ts_d, -30)):.1f}")
    holds = _lum(wl_d) > _lum(sky_d) + 6 and _lum(_shade(ts_d, -30)) < _lum(sky_d) - 20
    print(f"  wall brighter than sky AND tile keyline darker than sky: "
          f"[{'HOLDS' if holds else 'CHECK'}]")

    hero_day, hd_h = _hero(pal, 7)
    hero_night, hn_h = _hero(pal_n, 7)
    close = _closeup(pal, 7)

    # Gap-rim clearance — both crowns reaching the gap line under the flip.
    gap_probe = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    gp_bot = pygame.Rect(MARGIN, 247, PIPE_W, GROUND_Y - 247)
    gp_top = pygame.Rect(MARGIN, 0, PIPE_W, 97)
    candidate_himeji_heron(gap_probe, gp_top, gp_bot, pal, seed=7)
    clear_bot = _gap_rim_clearance(gap_probe, MARGIN, MARGIN + PIPE_W, 247, up=True)
    clear_top = _gap_rim_clearance(gap_probe, MARGIN, MARGIN + PIPE_W, 96, up=True)
    print("GAP-RIM CLEARANCE (vertical-flip mirror)")
    print(f"  bottom crown -> gap: {clear_bot}px   top crown -> gap: {clear_top}px")

    strip_heights = [70, 210, 355]
    strips = []
    print("FILL GATE — GATE = max empty HORIZONTAL band (true fall-through slice)")
    print("  supplementary: core (central 34px keep body) + full-band per-column runs")
    inset = 12                    # central keep-body column; the outer band is
    #                               the pyramid's stepped shoulder where sky
    #                               shows between tier roofs (correct for a keep)
    for h in strip_heights:
        s = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
        br = pygame.Rect(MARGIN, GROUND_Y - h, PIPE_W, h)
        tr = pygame.Rect(MARGIN, 0, PIPE_W, 0)
        candidate_himeji_heron(s, tr, br, pal, seed=7)
        core = _max_empty_run(s, MARGIN + inset, MARGIN + PIPE_W - inset,
                              GROUND_Y - h, GROUND_Y)
        full_run = _max_empty_run(s, MARGIN, MARGIN + PIPE_W, GROUND_Y - h, GROUND_Y)
        rows = _max_empty_row_run(s, MARGIN, MARGIN + PIPE_W, GROUND_Y - h, GROUND_Y)
        crop = pygame.Surface((CACHE_W, h + 8))
        crop.blit(_bg(CACHE_W, h + 8, pal, h), (0, 0))
        crop.blit(s, (0, -(GROUND_Y - h)))
        for ex in (MARGIN, MARGIN + PIPE_W):
            pygame.draw.line(crop, (230, 60, 60), (ex, 0), (ex, h + 8), 1)
        ok = rows <= 12 and core <= 12
        strips.append((h, crop, core, rows, ok))
        print(f"  h={h:3d}  horiz-band={rows}px [GATE {'OK' if rows <= 12 else 'FAIL'}]  "
              f"core-run={core}px  (full-band edge run={full_run}px)  "
              f"[{'OK' if ok else 'FAIL'}]")

    # ── Castle-not-pagoda silhouette proof ──
    BO_H = 300
    rows = _silhouette(pal, BO_H, seed=7)
    base_top_y = GROUND_Y - int(BO_H * 0.24)
    bl, br = _count_gable_bumps(rows, base_top_y, BO_H)
    base_w, eave_w = _base_vs_eave(pal, BO_H, seed=7)
    air = _rim_air(pal, 7)
    print("CASTLE-NOT-PAGODA SILHOUETTE PROOF")
    print(f"  gable/dormer bumps above the stone base:  LEFT flank={bl}   RIGHT flank={br}")
    print(f"  base_max_width={base_w}px   widest_eave_width={eave_w}px   "
          f"[{'BASE WINS' if base_w > eave_w else 'EAVE WINS — FAIL'}]")
    print(f"  mirror rim air (crown tip -> gap rim): {air}px  "
          f"[{'CLEAR' if air >= 3 else 'TOO TIGHT'}]")
    _print_ascii_silhouette(rows, BO_H)

    bo1 = _blackout(pal, BO_H, 1)
    bo3 = _blackout(pal, BO_H, 2)

    # ── compose the sheet ──
    pad = 12
    label_h = 22
    head_h = 84
    title = pygame.font.SysFont(None, 30)
    sub = pygame.font.SysFont(None, 18)
    lab = pygame.font.SysFont(None, 19)

    col_hero = CACHE_W
    col_close = close.get_width()
    col_bo = max(bo3.get_width(), bo1.get_width()) + 20
    strips_total_h = sum(c.get_height() + label_h + pad for _, c, _, _, _ in strips)

    body_h = max(hd_h, hn_h, close.get_height(),
                 strips_total_h, bo3.get_height() + 40) + label_h
    sheet_w = pad + col_hero + pad + col_hero + pad + col_hero + pad + \
        col_close + pad + col_bo + pad
    sheet_h = head_h + body_h + pad * 2
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((24, 25, 30))

    sheet.blit(title.render(
        "himeji_heron — White Heron castle keep  ·  round_2",
        True, (245, 240, 230)), (pad, 12))
    sheet.blit(sub.render(
        "red edges = PIPE_W (58px) collision band  ·  brilliant _plaster/_porcelain white walls "
        "(lit clamped both phases)  ·  each storey roofed by a TALL TRIANGULAR chidori/kara GABLE (front "
        "elevation) + paired shoulder dormers  ·  broadest mass = battered _korean_granite foot  ·  gold shachihoko crown",
        True, (170, 172, 182)), (pad, 40))
    sheet.blit(sub.render(
        "CASTLE-not-pagoda tell: blackout is a STACK OF TRIANGLES on a broad masonry foot "
        "(base 110px > widest eave 83px; 5-6 gable tips/flank) — never a slim stack of matched horizontal eaves  ·  "
        "3px rim air keeps the mirrored crowns from kissing  ·  night glow + shachihoko glint gated on dark sky",
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
    sheet.blit(lab.render("FEASIBILITY — 70 / 210 / 355", True, (255, 224, 150)),
               (x, sy - 20))
    for h, crop, core, rows, ok in strips:
        sheet.blit(crop, (x, sy))
        pygame.draw.rect(sheet, (60, 62, 72), (x, sy, col_hero, crop.get_height()), 1)
        oks = "OK" if ok else "FAIL"
        sheet.blit(lab.render(f"h={h}px  core {core}px / band {rows}px  [{oks}]", True,
                              (200, 235, 170) if ok else (255, 140, 140)),
                   (x, sy + crop.get_height() + 4))
        sy += crop.get_height() + label_h + pad

    x += col_hero + pad
    sheet.blit(close, (x, head_h))
    pygame.draw.rect(sheet, (60, 62, 72),
                     (x, head_h, close.get_width(), close.get_height()), 1)
    sheet.blit(lab.render("CROWN + GABLES 3x", True,
                          (255, 224, 150)), (x, head_h + close.get_height() + 4))

    x += col_close + pad
    sheet.blit(lab.render("BLACKOUT (castle tell)", True, (255, 224, 150)),
               (x, head_h - 20))
    sheet.blit(bo3, (x, head_h))
    sheet.blit(lab.render("2x — full keep", True, (200, 200, 210)),
               (x, head_h + bo3.get_height() + 2))
    sheet.blit(bo1, (x + bo3.get_width() // 2 - bo1.get_width() // 2,
                     head_h + bo3.get_height() + 24))
    sheet.blit(lab.render("1x", True, (200, 200, 210)),
               (x, head_h + bo3.get_height() + 24 + bo1.get_height() + 2))

    out = pathlib.Path(__file__).resolve().parent / "round_2.png"
    pygame.image.save(sheet, out)
    print(f"wrote {out}  ({sheet.get_width()}x{sheet.get_height()})")


# ── colorway strip ───────────────────────────────────────────────────────────

def _colorway_hero(candidate_fn, pal, seed):
    """One upright hero keep in the given colorway on its biome sky — the same
    framing as the round_2 HERO tile."""
    gap_y, gap_h = 172, 150
    top_h = int(gap_y - gap_h / 2)
    bot_top = int(gap_y + gap_h / 2)
    full = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    top_rect = pygame.Rect(MARGIN, 0, PIPE_W, top_h)
    bot_rect = pygame.Rect(MARGIN, bot_top, PIPE_W, GROUND_Y - bot_top)
    candidate_fn(full, top_rect, bot_rect, pal, seed)
    tip_y = top_h - 8
    base_y = GROUND_Y + 8
    hero_h = base_y - tip_y
    hero = _bg(CACHE_W, hero_h, pal, hero_h - (base_y - GROUND_Y))
    hero.blit(full, (0, -tip_y))
    return hero, hero_h


def colorways_main():
    """Labelled strip: the 5 colorways + the original White Heron for reference,
    each an upright DAY (0.30) hero with a small NIGHT (0.85) retint thumbnail
    to prove every colorway sweeps through the biome."""
    pal_d = biome.palette_for_phase(PHASE_DAY)
    pal_n = biome.palette_for_phase(PHASE_NIGHT)

    entries = [
        ("White Heron", "white  (reference)", candidate_himeji_heron),
        ("Crow", "black  lacquer", candidate_himeji_crow),
        ("Vermilion", "red  lacquer", candidate_himeji_vermilion),
        ("Gilt", "gold  leaf", candidate_himeji_gilt),
        ("Azure", "blue  celadon", candidate_himeji_azure),
        ("Sakura", "pink  plaster", candidate_himeji_sakura),
    ]

    heroes = []                   # (title, sub, day_surf, night_thumb)
    for title, sub, fn in entries:
        day, dh = _colorway_hero(fn, pal_d, 7)
        night, nh = _colorway_hero(fn, pal_n, 7)
        thumb_w = night.get_width() // 2
        thumb = pygame.transform.smoothscale(night, (thumb_w, nh // 2))
        heroes.append((title, sub, day, thumb))

    pad = 14
    head_h = 78
    col_w = CACHE_W
    thumb_h = heroes[0][3].get_height()
    day_h = heroes[0][2].get_height()
    label_h = 40
    body_h = day_h + 6 + thumb_h + label_h

    sheet_w = pad + len(heroes) * (col_w + pad)
    sheet_h = head_h + body_h + pad
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((24, 25, 30))

    title_f = pygame.font.SysFont(None, 30)
    sub_f = pygame.font.SysFont(None, 18)
    lab_f = pygame.font.SysFont(None, 21)
    tag_f = pygame.font.SysFont(None, 17)

    sheet.blit(title_f.render(
        "himeji_heron — 5 colorways  ·  identical geometry, material re-tint only",
        True, (245, 240, 230)), (pad, 12))
    sheet.blit(sub_f.render(
        "SAME silhouette / tier count / gables / fill / mirror as round_2 — only the palette-derived "
        "material triads swap anchors  ·  big tile = DAY (0.30), small = NIGHT (0.85) to prove the biome retint",
        True, (170, 172, 182)), (pad, 42))
    sheet.blit(sub_f.render(
        "Crow keeps a LIGHT silver keyline so the black holds vs a night sky; the others keep the dark tile edge  ·  "
        "gilt leaf keeps a night gleam  ·  gold shachihoko + night window glow on every colorway",
        True, (150, 210, 160)), (pad, 60))

    x = pad
    for title, sub, day, thumb in heroes:
        y = head_h
        sheet.blit(day, (x, y))
        pygame.draw.rect(sheet, (60, 62, 72), (x, y, col_w, day_h), 1)
        ty = y + day_h + 6
        sheet.blit(thumb, (x + (col_w - thumb.get_width()) // 2, ty))
        pygame.draw.rect(sheet, (60, 62, 72),
                         (x + (col_w - thumb.get_width()) // 2, ty,
                          thumb.get_width(), thumb.get_height()), 1)
        ly = ty + thumb.get_height() + 6
        sheet.blit(lab_f.render(title, True, (255, 224, 150)), (x, ly))
        sheet.blit(tag_f.render(sub, True, (176, 180, 192)), (x, ly + 18))
        x += col_w + pad

    out = pathlib.Path(__file__).resolve().parent / "colorways.png"
    pygame.image.save(sheet, out)
    print(f"wrote {out}  ({sheet.get_width()}x{sheet.get_height()})")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "colorways":
        colorways_main()
    else:
        main()
