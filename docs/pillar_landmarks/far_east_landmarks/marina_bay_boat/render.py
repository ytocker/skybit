"""marina_bay_boat — high-fidelity Marina Bay Sands (Singapore) pillar candidate.

The TOP-HEAVY pole of the far-east-landmarks family: three pale, curved hotel
legs that splay apart at the base and gather toward the top, carrying ONE long
horizontal boat-shaped SkyPark deck across their crowns — a ship stranded on
stilts. The deck cantilevers past the outermost legs into the eave gutter, tops
a rooftop garden + an infinity-pool sheen, and lights its edge at night. Reads
as nothing else in the set: a wide flat "ship" balanced on splayed legs.

Feasibility is the whole job here. Three splayed legs leave two triangular gaps
that would open a killzone in the 58px collision column, so the legs are drawn
as LIT RELIEF over a dim recessed atrium backing + a solid mall podium that both
span the full band — the column stays solid (max empty run <=12px) while the
legs still read as three towers because the backing recedes dark behind them. A
thin sky "reveal" notch is left just under the boat where the leg-tops poke up,
so the boat-on-legs silhouette still tells in blackout without ever opening a
sub-collision-width band.

Everything is palette-derived (via the shipped pagoda helpers) so the 5-min
biome day->night retint sweeps straight through. Standalone review candidate;
wires nothing into the live game.

Run:  python docs/pillar_landmarks/far_east_landmarks/marina_bay_boat/render.py
Out:  docs/pillar_landmarks/far_east_landmarks/marina_bay_boat/round_2.png
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
    _mix, _shade, _gradient_rect, _aa_polyline, _lit_niche, _tile_hatch,
    _draw_plinth_mist, _is_dark_sky, _is_warming_sky,
    _cap_lit_for_dark_sky, _cap_dark_for_dark_sky,
    _bronze, _gold_bright, _column_grey, _plaster, _pond_aqua,
)
from game.pillar_variants import draw_grass_bed, draw_flower_bed, draw_fern_cluster
from game.draw import draw_side_shrub


MARGIN = 64                       # matches entities.Pipe eave/ornament gutter
CACHE_W = PIPE_W + MARGIN * 2
CACHE_H = GROUND_Y
PHASE_DAY = 0.30                  # midday tan sky — hardest test for pale legs
PHASE_NIGHT = 0.85               # deep night — checks window glow + deck lights

_RIM_AIR = 3                      # px sky sliver so flipped decks don't kiss the gap


# ── Materials ────────────────────────────────────────────────────────────────
#
# Never a raw RGB in the body: each triad is a palette key mixed toward a fixed
# archetype tone, then lit/shadowed, so the biome retint still owns the hue.
# The read hierarchy that carries the landmark: PALE legs + PALE deck platform,
# a DARK heavy boat hull, and a DARKER-STILL recessed atrium behind the legs.

def _leg_triad(palette):
    # Pale concrete-and-glass hotel legs — _plaster, given a hard sun-side
    # specular so each curved slab reads as a 3-D volume, and a floored shadow
    # so the shaded flank never sinks into a dark night sky.
    mid = _plaster(palette)
    lit = _mix(mid, (250, 248, 240), 0.55)
    lit = _cap_lit_for_dark_sky(lit, palette, cap=220)
    sh = _mix(palette['stone_mid'], palette['stone_dark'], 0.42)
    sh = _cap_dark_for_dark_sky(sh, palette, floor=62)
    return lit, mid, sh


def _deck_triad(palette):
    # White SkyPark platform — one beat brighter/cooler than the legs so the
    # long deck plane separates from the leg crowns it rests on.
    mid = _mix(palette['stone_light'], (238, 238, 234), 0.52)
    lit = _shade(mid, 16)
    lit = _cap_lit_for_dark_sky(lit, palette, cap=224)
    sh = _mix(palette['stone_mid'], palette['stone_dark'], 0.34)
    sh = _cap_dark_for_dark_sky(sh, palette, floor=64)
    return lit, mid, sh


def _hull_triad(palette):
    # The boat hull — a cool slate steel (_column_grey) dropped a stop DARKER
    # than the legs so the deck reads as a heavy cap, not a fourth pale storey.
    mid = _shade(_column_grey(palette), -16)
    lit = _shade(mid, 26)
    sh = _shade(mid, -30)
    lit = _cap_lit_for_dark_sky(lit, palette, cap=190)
    sh = _cap_dark_for_dark_sky(sh, palette, floor=46)
    return lit, mid, sh


def _podium_triad(palette):
    # The mall podium + plinth — bare granite (_column_grey) a touch warmer/
    # lighter than the hull so the base reads as stone, distinct from the deck.
    mid = _column_grey(palette)
    lit = _shade(mid, 22)
    lit = _cap_lit_for_dark_sky(lit, palette, cap=206)
    sh = _shade(mid, -30)
    sh = _cap_dark_for_dark_sky(sh, palette, floor=58)
    return lit, mid, sh


def _atrium(palette):
    # The dim recessed body BEHIND the splayed legs — the mall atrium in
    # shadow. Deliberately the darkest surface so the pale legs pop as relief
    # and the inter-leg gaps read as receding shadow, never a see-through hole.
    c = _mix(palette['stone_dark'], palette['stone_mid'], 0.30)
    c = _shade(c, -14)
    return _cap_dark_for_dark_sky(c, palette, floor=48)


# ── Layout ──────────────────────────────────────────────────────────────────

def _layout(h):
    """Height-adaptive vertical budget: plinth / boat crown / mall podium. The
    leg zone is whatever is left, so one building fills any section height."""
    plinth_h = min(13, max(6, int(h * 0.09)))
    boat_h = min(30, max(13, int(h * 0.16)))
    podium_h = min(48, max(12, int(h * 0.20)))
    if h < 130:
        boat_h = max(11, boat_h - 2)
        podium_h = max(10, podium_h - 2)
        plinth_h = max(5, plinth_h - 1)
    return plinth_h, boat_h, podium_h


def _boat_metrics(boat_h):
    """Crown split, re-weighted toward the DECK. The deck is a thick bright bar;
    the hull is thinned ~40% off round_1 so the ship reads as a pale deck FLOATING
    on a shallow keel, not a heavy dark slab. Building + boat share this so the
    reveal line under the deck agrees between the collision layout and the art."""
    deck_th = max(3, int(boat_h * 0.46))
    hull_d = max(4, int(boat_h * 0.40))
    return deck_th, hull_d


# ── Boat SkyPark crown ────────────────────────────────────────────────────

def _hull_hw(half):
    """Hull half-width — a NARROW shallow keel under the deck's centre only, so
    the wide deck's cantilever tips AND the band-edge overhang both keep open SKY
    beneath the deck. This is the fix for round_1's dark slab: the hull no longer
    spans the full deck width, so the boat visibly detaches and floats."""
    return max(9, int(half * 0.56))


def _draw_boat(surf, cx, boat_top, boat_h, palette, rng):
    """One long horizontal SkyPark deck — a clean, unbroken bright BAR — resting
    on a short shallow keel. The deck cantilevers well past the hull and the legs
    into the gutter; open sky shows under both cantilever tips and the outer-third
    overhang, so the pale ship reads as FLOATING on its supports rather than a
    solid dark cap. Bilaterally symmetric about cx for a clean ceiling flip."""
    half = PIPE_W // 2
    dark_sky = _is_dark_sky(palette)
    bw = int(half * 1.62)                  # ~47px wide deck -> ~18px cantilever
    hw = _hull_hw(half)                    # narrow keel -> sky under the wings
    deck_th, hull_d = _boat_metrics(boat_h)
    deck_bot = boat_top + deck_th

    hlit, hmid, hsh = _hull_triad(palette)
    dlit, dmid, dsh = _deck_triad(palette)
    bronze = _bronze(palette)

    # ── Hull — a short shallow keel (lens) under the deck's centre third only.
    # Thinner + narrower than the deck so the ship is a pale deck on a small keel.
    N = 22
    under = []
    for i in range(N + 1):
        t = i / N
        x = cx - hw + 2 * hw * t
        dep = hull_d * (1.0 - (2 * t - 1) ** 2)        # 0 at ends, hull_d centre
        under.append((x, deck_bot + dep))
    pygame.draw.polygon(surf, hmid, [(cx - hw, deck_bot)] +
                        [(int(x), int(y)) for x, y in under] + [(cx + hw, deck_bot)])
    for i in range(N):
        (x0, y0), (x1, y1) = under[i], under[i + 1]
        col = _mix(hlit, hsh, min(1.0, (y0 - deck_bot) / max(1, hull_d)))
        pygame.draw.line(surf, col, (int(x0), int(y0)), (int(x1), int(y1)), 1)
    _aa_polyline(surf, _shade(hsh, -18), [(int(x), int(y)) for x, y in under])

    # ── Deck — one clean UNBROKEN bright horizontal BAR (the SkyPark). ──────
    deck = pygame.Rect(cx - bw, boat_top, 2 * bw, deck_th)
    _gradient_rect(surf, deck, _shade(dlit, 10), dmid, _shade(dmid, -6),
                   vertical=True)
    # Bright top rail + a faint specular streak reinforce the long horizontal
    # axis of the deck against the vertical legs.
    pygame.draw.line(surf, _shade(dlit, 24), (cx - bw, boat_top),
                     (cx + bw, boat_top), 1)
    if deck_th >= 5:
        pygame.draw.line(surf, _mix(dlit, (250, 250, 246), 0.5),
                         (cx - bw + 3, boat_top + 2), (cx + bw - 3, boat_top + 2), 1)
    # Crisp AA rim keeps the ship outline reading at 1x.
    _aa_polyline(surf, _shade(dsh, -16),
                 [(cx - bw, boat_top), (cx - bw, deck_bot),
                  (cx + bw, deck_bot), (cx + bw, boat_top)])
    # A crisp 2px dark shadow line at the deck underside (over the keel span) so
    # the bright deck POPS off the darker hull — the value break that reads "ship".
    pygame.draw.line(surf, _shade(hsh, -20), (cx - hw, deck_bot - 2),
                     (cx + hw, deck_bot - 2), 1)
    pygame.draw.line(surf, _shade(hsh, -30), (cx - hw, deck_bot - 1),
                     (cx + hw, deck_bot - 1), 1)
    # Bronze promenade band on the keel top, just under the shadow.
    pygame.draw.line(surf, bronze, (cx - hw + 2, deck_bot),
                     (cx + hw - 2, deck_bot), 1)

    # ── Infinity-pool glint — one short centred aqua sheen line, kept thin so
    # the deck still reads as a single unbroken bright bar, not a busy platform.
    if deck_th >= 5:
        aqua = _pond_aqua(palette)
        pw = int(bw * 0.5)
        pygame.draw.line(surf, _mix(aqua, (236, 246, 244), 0.5),
                         (cx - pw, boat_top + deck_th // 2),
                         (cx + pw, boat_top + deck_th // 2), 1)

    # ── Rooftop garden — a SINGLE low centred planter, kept ON the deck bar
    # (never above boat_top) so the top edge stays a clean horizontal line and
    # the rim air holds. No symmetric nubs (they read as crenellation at 1x).
    if deck_th >= 4:
        gx = cx
        pygame.draw.circle(surf, palette['foliage_dark'], (gx, boat_top + 2), 2)
        pygame.draw.circle(surf, palette['foliage_mid'], (gx, boat_top + 2), 1)
        surf.set_at((gx, boat_top + 1), palette['foliage_top'])

    # ── Night: a continuous warm deck-edge LINE (not dots) sells the SkyPark
    # promenade at 58px, plus a single restrained observation glow at the keel.
    if dark_sky:
        gold = _mix(palette['stone_accent'], (255, 216, 130), 0.8)
        streak = pygame.Surface((bw * 2, 3), pygame.SRCALPHA)
        pygame.draw.line(streak, (*gold, 135), (2, 1), (bw * 2 - 3, 1), 1)
        pygame.draw.line(streak, (*gold, 55), (2, 0), (bw * 2 - 3, 0), 1)
        surf.blit(streak, (cx - bw, boat_top + 1),
                  special_flags=pygame.BLEND_RGBA_ADD)
        _lit_niche(surf, cx, deck_bot + max(1, hull_d - 3),
                   min(7, hw), max(2, hull_d - 1), palette)


# ── Splayed hotel legs ──────────────────────────────────────────────────────

def _leg_span(surf, y, xl, xr, lit, mid, sh):
    """One row of a leg: horizontal 3-stop gradient, lit LEFT / shadow RIGHT —
    the raking-light model that reads the curved slab as a rounded volume."""
    w = xr - xl
    if w < 1:
        return
    if w == 1:
        surf.set_at((xl, y), mid)
        return
    for i in range(w):
        t = i / (w - 1)
        col = _mix(lit, mid, t * 2) if t < 0.5 else _mix(mid, sh, (t - 0.5) * 2)
        surf.set_at((xl + i, y), col)


def _draw_leg(surf, y_top, y_bot, top_cx, base_cx, top_hw, base_hw,
              palette, dark_sky):
    """One tapering, gently bowed hotel leg from the boat underside (`y_top`,
    gathered) down to the podium (`y_bot`, splayed). Lit specular relief, a fine
    floor-band + window-mullion hatch, and sparse window glow at night."""
    lit, mid, sh = _leg_triad(palette)
    h = max(1, y_bot - y_top)
    left_pts, right_pts = [], []

    def _cx_hw(y):
        t = (y - y_top) / h                          # 0 top -> 1 bottom
        ccx = top_cx + (base_cx - top_cx) * t
        ccx += (base_cx - top_cx) * 0.10 * math.sin(math.pi * t)   # slight bow
        hw = top_hw + (base_hw - top_hw) * t
        return ccx, hw

    for y in range(y_top, y_bot):
        ccx, hw = _cx_hw(y)
        xl = int(round(ccx - hw))
        xr = int(round(ccx + hw))
        _leg_span(surf, y, xl, xr, lit, mid, sh)
        left_pts.append((xl, y))
        right_pts.append((xr, y))

    _aa_polyline(surf, _shade(sh, -18),
                 left_pts + list(reversed(right_pts)), closed=True)
    # Sun-catch specular streak ~30% in from the lit edge.
    spec = [(int(left_pts[i][0] + (right_pts[i][0] - left_pts[i][0]) * 0.3), y)
            for i, y in enumerate(range(y_top, y_bot))]
    _aa_polyline(surf, _shade(lit, 22), spec)

    # Floor bands + window mullions — the strong horizontal storey rhythm of a
    # hotel slab, with a fine vertical hatch for the glazing grid.
    tile = _shade(sh, -12)
    lit_band = _shade(lit, 12)
    step = 5 if h > 30 else 6
    for k, yy in enumerate(range(y_top + 3, y_bot - 1, step)):
        ccx, hw = _cx_hw(yy)
        xl = int(round(ccx - hw))
        xr = int(round(ccx + hw))
        if xr - xl < 3:
            continue
        pygame.draw.line(surf, tile, (xl + 1, yy), (xr - 1, yy), 1)
        pygame.draw.line(surf, lit_band, (xl + 1, yy - 1), (xr - 1, yy - 1), 1)
        _tile_hatch(surf, xl + 1, yy - 1, xr - 1, yy - 1, _shade(mid, -16), step=3)
        if dark_sky and k % 2 == 0 and xr - xl >= 6:
            _lit_niche(surf, int(ccx), yy - 3,
                       min(5, xr - xl - 3), min(4, step - 2), palette)


# ── Recessed body + podium + plinth ─────────────────────────────────────────

def _draw_backing(surf, cx, y_top, y_bot, palette):
    """Dim recessed atrium spanning the full collision band behind the legs so
    the two inter-leg gaps read as receding shadow, never a killzone hole."""
    if y_bot - y_top < 2:
        return
    c = _atrium(palette)
    r = pygame.Rect(cx - PIPE_W // 2, y_top, PIPE_W, y_bot - y_top)
    _gradient_rect(surf, r, _shade(c, 14), c, _shade(c, -16))
    for dx in (-int(PIPE_W * 0.24), int(PIPE_W * 0.24)):
        pygame.draw.line(surf, _shade(c, -12),
                         (cx + dx, y_top), (cx + dx, y_bot - 1), 1)


def _draw_podium(surf, cx, y_top, y_bot, palette, dark_sky):
    """Solid mall podium — full-band granite block that anchors the base and
    fills BEHIND the widest leg splay, with floor slabs + mall-entrance glow."""
    if y_bot - y_top < 2:
        return
    half = PIPE_W // 2
    lit, mid, sh = _podium_triad(palette)
    r = pygame.Rect(cx - PIPE_W // 2, y_top, PIPE_W, y_bot - y_top)
    _gradient_rect(surf, r, lit, mid, sh)
    pygame.draw.line(surf, _shade(lit, 22), (r.x, y_top), (r.right - 1, y_top), 1)
    for yy in range(y_top + 4, y_bot - 1, 5):
        pygame.draw.line(surf, _shade(sh, -10), (r.x + 1, yy), (r.right - 2, yy), 1)
        _tile_hatch(surf, r.x + 2, yy, r.right - 3, yy, _shade(mid, -12), step=3)
    if dark_sky:
        for dx in (-int(half * 0.5), 0, int(half * 0.5)):
            _lit_niche(surf, int(cx + dx), y_bot - 6, 5, 4, palette)


def _draw_plinth(surf, cx, base_y, palette):
    """3-layer stepped granite plinth — the building's footing on the ground."""
    lit, mid, sh = _podium_triad(palette)
    for i in range(3):
        lw = int(PIPE_W * (1.02 + 0.15 * i))
        lh = 4
        ly = base_y - (3 - i) * lh
        rr = pygame.Rect(cx - lw // 2, ly, lw, lh)
        _gradient_rect(surf, rr, lit, mid, sh)
        pygame.draw.line(surf, _shade(sh, -16),
                         (rr.x, rr.bottom - 1), (rr.right - 1, rr.bottom - 1), 1)
        pygame.draw.line(surf, _shade(lit, 14), (rr.x, rr.y), (rr.right - 1, rr.y), 1)


# ── One whole building ──────────────────────────────────────────────────────

def _draw_building(surf, cx, y_top, y_bot, palette, seed):
    rng = random.Random(seed)
    half = PIPE_W // 2
    h = y_bot - y_top
    dark_sky = _is_dark_sky(palette)
    plinth_h, boat_h, podium_h = _layout(h)
    base_y = y_bot

    _draw_plinth_mist(surf, cx, base_y - plinth_h + 2, int(PIPE_W * 1.7), palette)

    boat_top = y_top + _RIM_AIR
    # A real SKY REVEAL is carved directly under the deck: the deck-cap is solid,
    # then `reveal` px of open sky, then the long legs / backing resume. Held to
    # ~4-6px (well under the 12px gate) and — crucially — a solid centre CORE
    # spans the middle so the reveal opens only in the outer-third overhang, never
    # as an inter-leg killzone. In blackout this turns the round_1 slab into a
    # cap floating over its supports with sky beneath.
    deck_th, hull_d = _boat_metrics(boat_h)
    deck_bot = boat_top + deck_th
    reveal = max(4, min(6, int(h * 0.030)))
    backing_top = deck_bot + reveal
    podium_top = base_y - plinth_h - podium_h
    # Legs top out AT the reveal line (just under the sky slot) so the deck reads
    # as floating clear above them; they still run long down to the podium.
    legs_top = deck_bot + reveal
    legs_bot = min(podium_top + 2, base_y - plinth_h - 2)
    if legs_bot <= legs_top + 2:
        legs_bot = legs_top + 2

    # Order: recessed body first, then the solid centre CORE that keeps the band's
    # spine filled up to the deck (the reveal opens only outboard of it), podium
    # over the base, then legs as relief.
    _draw_backing(surf, cx, backing_top, podium_top, palette)
    core_hw = _hull_hw(PIPE_W // 2)
    core = _shade(_atrium(palette), -6)
    pygame.draw.rect(surf, core,
                     (cx - core_hw, deck_bot, core_hw * 2, reveal + 1))
    _draw_podium(surf, cx, podium_top, base_y - plinth_h, palette, dark_sky)

    # Three legs: centre carries the centreline; left/right splay to the base.
    # Their crowns rise to the reveal line under the boat, so the sky slot reads
    # as "a ship resting clear of its splayed legs".
    _draw_leg(surf, legs_top, legs_bot, cx, cx, 4, 6, palette, dark_sky)
    _draw_leg(surf, legs_top, legs_bot,
              cx - int(half * 0.38), cx - int(half * 0.70), 4, 6,
              palette, dark_sky)
    _draw_leg(surf, legs_top, legs_bot,
              cx + int(half * 0.38), cx + int(half * 0.70), 4, 6,
              palette, dark_sky)

    _draw_boat(surf, cx, boat_top, boat_h, palette, rng)
    _draw_plinth(surf, cx, base_y, palette)

    # Ground foliage — the landscaped waterfront apron.
    draw_grass_bed(surf, cx, base_y - 1, PIPE_W + 12, 14, palette, seed=seed)
    draw_flower_bed(surf, cx, base_y - 2, PIPE_W - 4, 6, seed=seed)
    draw_side_shrub(surf, cx - half - 6, base_y - 1, palette, scale=0.9)
    draw_side_shrub(surf, cx + half + 6, base_y - 1, palette, scale=0.8)
    if h > 90:
        draw_fern_cluster(surf, cx - half + 2, base_y - 2, 4, palette, seed=seed + 3)
        draw_fern_cluster(surf, cx + half - 2, base_y - 2, 4, palette, seed=seed + 5)


def candidate_marina_bay_boat(surf, top_rect, bot_rect, palette, seed):
    """Bottom = the building rising from the ground, boat deck at the gap. Top =
    the same building vertical-FLIPPED from the ceiling — a boat hangs under the
    twin, its symmetric deck presenting cleanly at the gap rim."""
    if bot_rect.height > 0:
        _draw_building(surf, bot_rect.centerx, bot_rect.y, bot_rect.bottom,
                       palette, seed)
    if top_rect.height > 0:
        tmp = pygame.Surface((surf.get_width(), top_rect.height), pygame.SRCALPHA)
        _draw_building(tmp, top_rect.centerx, 0, top_rect.height, palette, seed + 1)
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


def _col_runs_at(surf, x, y0, y1):
    worst = run = 0
    for y in range(y0, y1):
        if surf.get_at((x, y))[3] == 0:
            run += 1
            worst = max(worst, run)
        else:
            run = 0
    return worst


def _gap_rim_clearance(surf, x0, x1, gap_y, up=True):
    step = -1 if up else 1
    for d in range(0, 220):
        y = gap_y + step * d
        if y < 0 or y >= surf.get_height():
            return d
        if any(surf.get_at((x, y))[3] > 0 for x in range(x0, x1)):
            return d
    return 220


def _hero(pal, seed):
    gap_y, gap_h = 172, 150
    top_h = int(gap_y - gap_h / 2)
    bot_top = int(gap_y + gap_h / 2)
    full = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    top_rect = pygame.Rect(MARGIN, 0, PIPE_W, top_h)
    bot_rect = pygame.Rect(MARGIN, bot_top, PIPE_W, GROUND_Y - bot_top)
    candidate_marina_bay_boat(full, top_rect, bot_rect, pal, seed=seed)

    tip_y = 2
    base_y = GROUND_Y + 8
    hero_h = base_y - tip_y
    hero = _bg(CACHE_W, hero_h, pal, hero_h - (base_y - GROUND_Y))
    hero.blit(full, (0, -tip_y))
    for ex in (MARGIN, MARGIN + PIPE_W):
        pygame.draw.line(hero, (230, 60, 60), (ex, 0), (ex, hero_h), 1)
    return hero, hero_h


def _closeup(pal, seed, scale=3):
    """Zoom on the boat crown + gathered leg-tops so the deck/pool/hull read."""
    surf = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    br = pygame.Rect(MARGIN, GROUND_Y - 210, PIPE_W, 210)
    tr = pygame.Rect(MARGIN, 0, PIPE_W, 0)
    candidate_marina_bay_boat(surf, tr, br, pal, seed=seed)
    y0 = GROUND_Y - 210
    crop = pygame.Surface((CACHE_W, 96))
    crop.blit(_bg(CACHE_W, 96, pal, 96), (0, 0))
    crop.blit(surf, (0, -y0))
    return pygame.transform.scale(
        crop, (crop.get_width() * scale, crop.get_height() * scale))


def _blackout(pal, section_h, scale):
    """Solid-black silhouette of a hero section — the boat-on-legs read test."""
    surf = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    br = pygame.Rect(MARGIN, GROUND_Y - section_h, PIPE_W, section_h)
    tr = pygame.Rect(MARGIN, 0, PIPE_W, 0)
    candidate_marina_bay_boat(surf, tr, br, pal, seed=7)
    pad_x = 34
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

    # Material proof — day != night on every surface, and the value hierarchy
    # (deck brightest, legs pale, hull dark, atrium darkest) that carries the read.
    def _lum(c):
        return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]
    leg_d = _leg_triad(pal)[1]
    leg_n = _leg_triad(pal_n)[1]
    hull_d = _hull_triad(pal)[1]
    atr_d = _atrium(pal)
    print("MATERIALS — value hierarchy (deck/legs pale > hull > atrium)")
    print(f"  DAY   leg={leg_d} lum={_lum(leg_d):.0f}  hull lum={_lum(hull_d):.0f}  "
          f"atrium lum={_lum(atr_d):.0f}")
    print(f"  legs > hull: {_lum(leg_d) > _lum(hull_d)}   "
          f"hull > atrium: {_lum(hull_d) > _lum(atr_d)}")
    print(f"  day != night (leg mid): {leg_d != leg_n}")

    # Crown geometry — the round_2 re-weight: hull thinned, a real reveal carved.
    print("CROWN GEOMETRY (hull thinned + real sky reveal under the deck)")
    for hh in (118, 355):
        _, boat_h, _ = _layout(hh)
        deck_th, hull_d = _boat_metrics(boat_h)
        reveal = max(4, min(6, int(hh * 0.030)))
        print(f"  section h={hh:3d}  deck={deck_th}px  HULL={hull_d}px  "
              f"REVEAL={reveal}px")

    # Fill gate — max empty vertical run inside the 58px band at 3 heights,
    # plus the specific columns the brief calls out (70 / 210 / 355 offsets).
    print("FILL GATE (max empty vertical run inside the 58px PIPE_W band)")
    strip_heights = [70, 210, 355]
    strips = []
    for h in strip_heights:
        s = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
        br = pygame.Rect(MARGIN, GROUND_Y - h, PIPE_W, h)
        tr = pygame.Rect(MARGIN, 0, PIPE_W, 0)
        candidate_marina_bay_boat(s, tr, br, pal, seed=7)
        run = _max_empty_run(s, MARGIN, MARGIN + PIPE_W, GROUND_Y - h, GROUND_Y)
        crop = pygame.Surface((CACHE_W, h + 8))
        crop.blit(_bg(CACHE_W, h + 8, pal, h), (0, 0))
        crop.blit(s, (0, -(GROUND_Y - h)))
        for ex in (MARGIN, MARGIN + PIPE_W):
            pygame.draw.line(crop, (230, 60, 60), (ex, 0), (ex, h + 8), 1)
        strips.append((h, crop, run))
        print(f"  h={h:3d}  max empty run = {run}px  [{'OK' if run <= 12 else 'FAIL'}]")

    # The three named collision columns (measured relative to the band left edge).
    print("NAMED COLUMNS (empty run at band-x 70/210/355 -> clamped into band)")
    s = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    br = pygame.Rect(MARGIN, 0, PIPE_W, GROUND_Y)
    candidate_marina_bay_boat(s, pygame.Rect(MARGIN, 0, PIPE_W, 0), br, pal, seed=7)
    for probe in (70, 210, 355):
        x = MARGIN + min(PIPE_W - 1, probe % PIPE_W)
        r = _col_runs_at(s, x, 0, GROUND_Y)
        print(f"  probe {probe:3d} -> col x={x}  empty run = {r}px  "
              f"[{'OK' if r <= 12 else 'FAIL'}]")

    hero_day, hd_h = _hero(pal, 7)
    hero_night, hn_h = _hero(pal_n, 7)
    close = _closeup(pal, 7)

    # Mirror clearance — how far each boat deck sits INSIDE its own section from
    # the gap-rim line (positive = a clean sky sliver, no intrusion into the
    # flyable gap). Bottom section content lives below rim 247; the flipped top
    # section content lives above rim 97.
    gap_probe = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    gp_bot = pygame.Rect(MARGIN, 247, PIPE_W, GROUND_Y - 247)
    gp_top = pygame.Rect(MARGIN, 0, PIPE_W, 97)
    candidate_marina_bay_boat(gap_probe, gp_top, gp_bot, pal, seed=7)
    clear_bot = _gap_rim_clearance(gap_probe, MARGIN, MARGIN + PIPE_W, 247, up=False)
    clear_top = _gap_rim_clearance(gap_probe, MARGIN, MARGIN + PIPE_W, 97, up=True)
    print("MIRROR CLEARANCE (deck sits INSIDE its section, no gap intrusion)")
    print(f"  bottom deck air below rim: {clear_bot}px   "
          f"top (flipped) deck air above rim: {clear_top}px")

    bo1 = _blackout(pal, 118, 1)
    bo3 = _blackout(pal, 118, 3)

    # ── compose the sheet ──
    pad = 12
    label_h = 22
    head_h = 84
    title = pygame.font.SysFont(None, 30)
    sub = pygame.font.SysFont(None, 18)
    lab = pygame.font.SysFont(None, 19)

    col_hero = CACHE_W
    strips_total_h = sum(c.get_height() + label_h + pad for _, c, _ in strips)
    body_h = max(hd_h, hn_h, close.get_height(),
                 strips_total_h, bo3.get_height() + 40) + label_h
    sheet_w = pad + col_hero + pad + col_hero + pad + col_hero + pad + \
        close.get_width() + pad + max(bo3.get_width(), bo1.get_width()) + 20 + pad
    sheet_h = head_h + body_h + pad * 2
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((22, 24, 28))

    sheet.blit(title.render(
        "marina_bay_boat — Marina Bay Sands SkyPark on three splayed legs  ·  round_2",
        True, (232, 240, 250)), (pad, 12))
    sheet.blit(sub.render(
        "red edges = PIPE_W (58px) collision band  ·  a thick bright DECK bar on a "
        "thin narrow keel + splayed legs  ·  legs are LIT RELIEF over a dim atrium "
        "+ solid mall podium", True,
        (168, 176, 190)), (pad, 40))
    sheet.blit(sub.render(
        "round_2: a real sky REVEAL is carved under the deck (outer-third overhang) "
        "over a solid centre CORE + full-band backing — the cap floats on its "
        "supports, fill gate still <=12px  ·  symmetric deck -> clean ceiling flip", True,
        (150, 200, 210)), (pad, 58))

    y = head_h
    x = pad
    sheet.blit(hero_day, (x, y))
    pygame.draw.rect(sheet, (56, 60, 66), (x, y, col_hero, hd_h), 1)
    sheet.blit(lab.render("HERO — DAY (0.30)", True, (255, 224, 150)),
               (x, y + hd_h + 4))

    x += col_hero + pad
    sheet.blit(hero_night, (x, y))
    pygame.draw.rect(sheet, (56, 60, 66), (x, y, col_hero, hn_h), 1)
    sheet.blit(lab.render("HERO — NIGHT (0.85)", True, (255, 224, 150)),
               (x, y + hn_h + 4))

    x += col_hero + pad
    sy = head_h
    sheet.blit(lab.render("FILL GATE — bottom section", True, (255, 224, 150)),
               (x, sy - 20))
    for h, crop, run in strips:
        sheet.blit(crop, (x, sy))
        pygame.draw.rect(sheet, (56, 60, 66), (x, sy, col_hero, crop.get_height()), 1)
        ok = "OK" if run <= 12 else "FAIL"
        sheet.blit(lab.render(f"h={h}px  ·  run {run}px  [{ok}]", True,
                              (200, 235, 170) if run <= 12 else (255, 140, 140)),
                   (x, sy + crop.get_height() + 4))
        sy += crop.get_height() + label_h + pad

    x += col_hero + pad
    sheet.blit(close, (x, head_h))
    pygame.draw.rect(sheet, (56, 60, 66),
                     (x, head_h, close.get_width(), close.get_height()), 1)
    sheet.blit(lab.render("CROWN CLOSE-UP 3x — boat deck + pool + legs", True,
                          (255, 224, 150)), (x, head_h + close.get_height() + 4))

    x += close.get_width() + pad
    sheet.blit(lab.render("BLACKOUT (boat-on-legs)", True, (255, 224, 150)),
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
