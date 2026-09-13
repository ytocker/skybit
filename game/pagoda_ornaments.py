"""Pagoda ornament layer — drop-in additive decoration for the 11 winners.

The structural pillar drawers in `pillar_pagoda_variants.py` /
`pillar_pagoda_variants_r4.py` stay untouched; this module paints small
human-scale story-beats ON TOP of the already-drawn pillar pair: lanterns
on eaves, vines climbing the bottom shaft, a cat on a plinth, fluttering
prayer flags spanning the gap, etc. The intent is "alive village", not
"more architecture".

# Why a separate module
The pagoda winners were locked after round 10 — restyling them risks
breaking silhouettes the art-director already signed off. Painting
ornaments in a separate pass lets us iterate on village character without
touching the load-bearing pillar code, and lets us share one ornament
across many pagodas (the universal-pool concept).

# Why reuse the live-game pillar helpers
The live-game pillar system (`game/pillar_variants.py` + `game/draw.py`)
already ships 25 battle-tested ornament helpers that read at PIPE_W=58
in production today: prayer flags, paper lanterns, cairns, incense,
bird silhouettes, ribbons, vines, wuling pines, etc. Round-15 reinvented
every ornament at sub-pixel sizes and the user reported "I barely see
anything"; round-16 swaps in the proven helpers so the language matches
the rest of the game and the ornaments READ at game scale.

# Picker rules (AD-set)
Every pagoda has its own allow-list with per-ornament weights. The
picker draws 0/1/2/3 ornaments per pillar (existing 25/50/20/5 weights),
respecting:
  * pillar_index == 0  → 70% n=0, 30% n=1 from a quiet-only subset
  * is_rush == True    → force n=0 (no power-ups, no ornaments)
  * NIGHT_ONLY items   → only when phase is in the strict night window
  * SNOW_ONLY items    → reserved for snowy phase buckets
  * CONFLICTS          → never pick both of a conflict pair
  * universal-pool     → 4 items appear in every allow-list

# Night-luminance contract
Coin gold in `game/draw.py` is `(255, 210, 20)`. The brightest channel is
255, so the night-ornament cap is 153 (0.60 × 255). All ornament glows
on NIGHT_ONLY items are clamped before blit to keep coins reading as the
most important shiny thing on screen.

# Scale ceilings (AD-set)
Living humans render at ≤7 px tall. Statues (lions, lantern figures,
kitsune) render at ≤9 px tall. Encoded in `STATUE_NAMES` so the picker
can sanity-check during dev; the per-ornament draw functions also obey
this directly.

# Cache strategy
Cell-local ornaments pre-render to a tiny SRCALPHA cell per
(name, phase_bucket) the first time they are requested so palette
interpolation for the small glyphs is amortized across all pillars in a
session. The cache key uses `game.biome.PHASE_BUCKETS` for symmetry with
the sky cache, plus enough of the pillar seed to keep two pipes from
sharing a cell that was baked from only one of their seeds.

# Direct-draw ornaments
A small set of ornaments need the actual `top_rect` / `bot_rect` of the
pillar pair because their geometry spans the gap or the full body
(prayer-flag canopy strung between pillar tips, lantern catenary across
the gap, body-length climbing vine). These bypass the cell cache and
draw on the live `surf` directly; the cache cost is negligible because
they are at most one per pillar.
"""
from __future__ import annotations

import math
import random
from collections import OrderedDict
from typing import Callable

import pygame

from game import biome as _biome
from game.config import PIPE_W, GROUND_Y
from game.pillar_variants import (
    draw_climbing_vine, draw_prayer_flags, draw_cairn, draw_darchog_pole,
    draw_incense_smoke, draw_bird_sil, draw_raven, draw_paper_lantern,
    draw_cascading_vine, draw_ribbons_tied,
)


# ── Luminance contract ──────────────────────────────────────────────────────
#
# Coin gold is (255, 210, 20). Cap night-ornament luminance at 60% of the
# coin's brightest channel so coins stay the most luminous thing on screen.

COIN_GOLD = (255, 210, 20)
NIGHT_LUMA_CAP = int(max(COIN_GOLD) * 0.60)  # 153


def _clamp_night(color, alpha=255):
    """Clamp each channel to NIGHT_LUMA_CAP. Used by NIGHT_ONLY ornaments."""
    r, g, b = color[:3]
    cap = NIGHT_LUMA_CAP
    return (min(r, cap), min(g, cap), min(b, cap), alpha)


def _mix(a, b, t):
    return (int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t))


def _shade(c, d):
    return (max(0, min(255, c[0] + d)),
            max(0, min(255, c[1] + d)),
            max(0, min(255, c[2] + d)))


# ── Phase classification ────────────────────────────────────────────────────
#
# Night-only ornaments fire when the biome phase sits in a strict
# nighttime band — no dusk/predawn bleed (AD answer #1).

_NIGHT_BAND = (0.58, 0.92)  # tight night window; sunset 0.51 / dawn 0.95 sit OUTSIDE


def _is_night(phase: float) -> bool:
    p = phase % 1.0
    return _NIGHT_BAND[0] <= p <= _NIGHT_BAND[1]


# ── Anchor zone resolution ──────────────────────────────────────────────────
#
# Each ornament declares where on the pillar pair it belongs; the entry
# function resolves the actual (x,y) using `top_rect` + `bot_rect`. We
# keep zone semantics small so the picker stays readable.

# Zones:
#   BODY_TOP   — climbing surface of the BOTTOM pillar's upper shaft
#                (just below the gap roof line)
#   BODY_BOT   — lower shaft of the BOTTOM pillar near the plinth
#   GAP        — hangs in the gap between the two pillars
#   PLINTH     — sits at the bottom-pillar's groundline
#   FINIAL     — at the bottom-pillar's tip
#   EAVE       — along the bottom edge of the TOP pillar (eave underside)
#   ROOF       — on top of the bottom pillar (small lift above the finial)

ZONE_BODY_TOP = "body_top"
ZONE_BODY_BOT = "body_bot"
ZONE_GAP = "gap"
ZONE_PLINTH = "plinth"
ZONE_FINIAL = "finial"
ZONE_EAVE = "eave"
ZONE_ROOF = "roof"


# ── Ornament draw functions ─────────────────────────────────────────────────
#
# Two flavours of signature exist in this module:
#
#   Cell-local:  _draw_<name>(surf, anchor_xy, palette, seed, **flags)
#                anchor is (_CELL_CX, _CELL_CY) — the centre of a 64×64
#                SRCALPHA cell that is later blitted onto the live surface
#                centred on the anchor zone.
#
#   Direct:      _draw_<name>(surf, top_rect, bot_rect, palette, seed, **flags)
#                writes straight onto the live surface. Used for ornaments
#                whose geometry depends on the actual pillar rects — a
#                catenary across the gap, a body-length climbing vine —
#                where capping geometry to a 64×64 cell would clip the
#                ornament. Listed in `_DIRECT_DRAW` below.


# ── Direct-draw ornaments (use pillar rects) ────────────────────────────────

def _draw_prayer_flags(surf, top_rect, bot_rect, palette, seed, **flags):
    # Headline ornament — Tibetan-style prayer-flag canopy strung tip-to-tip
    # between the two pagodas' finial spires (sōrin / bot pillar, inverted
    # finial / top pillar). The catenary that `draw_prayer_flags` sags
    # naturally reads as a real monastery rope hung between two stupa peaks.
    bcx = bot_rect.centerx
    tcx = top_rect.centerx
    draw_prayer_flags(surf, tcx, top_rect.bottom, bcx, bot_rect.top, n=7)


def _draw_paper_lantern_string(surf, top_rect, bot_rect, palette, seed, **flags):
    # Sag-arc of 3 paper lanterns hung along a catenary stretched between
    # the two pagodas' finial-tip centerlines — the same anchor points the
    # prayer-flag rope uses, so the chain reads as a real suspended strand
    # between two spires, not a coin column floating in the gap.
    x1, y1 = top_rect.centerx, top_rect.bottom
    x2, y2 = bot_rect.centerx, bot_rect.top
    sag = 10
    mx, my = (x1 + x2) // 2, max(y1, y2) + sag
    for t in (0.25, 0.50, 0.75):
        # Quadratic Bézier through a sag midpoint between the two finial tips.
        bx = (1 - t) ** 2 * x1 + 2 * (1 - t) * t * mx + t * t * x2
        by = (1 - t) ** 2 * y1 + 2 * (1 - t) * t * my + t * t * y2
        draw_paper_lantern(surf, int(bx), int(by), strand=4, scale=0.55,
                           color='red')


def _draw_climbing_vine(surf, top_rect, bot_rect, palette, seed, **flags):
    # Universal-pool body vine — runs the full bottom-pillar shaft from the
    # plinth up to within reach of the gap. Reusing the live-game helper
    # keeps the foliage language identical to the rest of the world.
    rng = random.Random(seed * 1009 + 31)
    side = -1 if rng.random() < 0.5 else 1
    x = (bot_rect.x + bot_rect.width // 2
         + side * (bot_rect.width // 2 - 4))
    y_top = bot_rect.y + 12
    y_bot = bot_rect.bottom - 4
    draw_climbing_vine(surf, x, y_top, y_bot, palette, seed=seed)


# ── Cell-local ornaments ────────────────────────────────────────────────────


def _draw_cat_companion(surf, anchor, palette, seed, position="PLINTH", **flags):
    # Merged sitting_cat + cat_on_roof. 6 px tall — under the 7 px human
    # cap (cats aren't human but they share the cap conceptually).
    cx, cy = anchor
    rng = random.Random(seed * 17 + 3)
    # Calico body — derive from stone_dark so night/day retints cleanly.
    body = _mix(palette['stone_dark'], (90, 70, 55), 0.55)
    accent = _mix(palette['stone_accent'], (240, 220, 180), 0.60)
    # Sitting cat — small humped silhouette with one ear nick + tail curl.
    pygame.draw.ellipse(surf, body, (cx - 3, cy - 5, 7, 5))
    pygame.draw.ellipse(surf, body, (cx + 1, cy - 7, 4, 4))  # head
    pygame.draw.polygon(surf, body, [(cx + 4, cy - 7), (cx + 5, cy - 9), (cx + 5, cy - 6)])  # ear
    pygame.draw.polygon(surf, body, [(cx + 1, cy - 7), (cx, cy - 9), (cx + 2, cy - 6)])  # ear
    # Tail curls back along the perch.
    pygame.draw.line(surf, body, (cx - 3, cy - 3), (cx - 5, cy - 4), 1)
    if rng.random() < 0.5:
        pygame.draw.line(surf, accent, (cx + 2, cy - 4), (cx + 3, cy - 4), 1)


def _draw_petal_drift(surf, anchor, palette, seed, **flags):
    # 4-6 tiny petals drifting near the gap roof — palette-derived pink/cream
    # so it reads as the season, not a sticker. Round-16: bumped to radius-2
    # so the petals actually READ at game scale.
    cx, cy = anchor
    rng = random.Random(seed * 23 + 7)
    petal = _mix(palette['stone_light'], (250, 200, 210), 0.65)
    petal_d = _mix(palette['stone_mid'], (210, 150, 170), 0.60)
    n = rng.randint(4, 6)
    for _ in range(n):
        dx = rng.randint(-18, 18)
        dy = rng.randint(-12, 12)
        col = petal if rng.random() < 0.6 else petal_d
        # 2-px round dot + a 1-px curl pixel — reads as a tilted petal.
        pygame.draw.circle(surf, col, (cx + dx, cy + dy), 2)
        pygame.draw.rect(surf, _shade(col, -20),
                         (cx + dx + 1, cy + dy - 1, 1, 1))


def _draw_eave_bird(surf, anchor, palette, seed, count=2, **flags):
    # Merged pigeon_pair + crow_on_finial. count=2 → small bird silhouettes
    # on the eave (reuses live-game draw_bird_sil), count=1 → a raven on
    # the finial (reuses draw_raven). Both helpers are battle-tested.
    cx, cy = anchor
    if count >= 2:
        draw_bird_sil(surf, cx - 6, cy, size=5)
        draw_bird_sil(surf, cx + 6, cy, size=5)
    else:
        draw_raven(surf, cx, cy)


def _draw_furin_wind_chime(surf, anchor, palette, seed, **flags):
    # Single fūrin — crimson-lacquer bell with a paper streamer. Body
    # enlarged to 5×6 (round-16) so it reads at game scale. Bell is deep
    # crimson (NOT warm gold) so it can never read as a coin pickup in the
    # flight gap; a 1-px gold rim keeps the chime identity without
    # occupying coin-luma territory.
    cx, cy = anchor
    cord = _mix(palette['stone_dark'], (40, 30, 25), 0.6)
    crimson = _mix(palette['stone_dark'], (170, 35, 35), 0.78)
    crimson_d = _shade(crimson, -25)
    gold_rim = _mix(palette['stone_accent'], (230, 180, 90), 0.70)
    streamer = _mix(palette['stone_accent'], (220, 140, 80), 0.65)
    pygame.draw.line(surf, cord, (cx, cy), (cx, cy + 3), 1)
    # 5×6 crimson lacquer dome with darker shadow band.
    pygame.draw.ellipse(surf, crimson_d, (cx - 3, cy + 3, 6, 7))
    pygame.draw.ellipse(surf, crimson, (cx - 2, cy + 4, 5, 6))
    # 1-px gold rim accent — the chime identity cue, not a luminous orb.
    pygame.draw.line(surf, gold_rim, (cx - 3, cy + 9), (cx + 2, cy + 9), 1)
    pygame.draw.rect(surf, crimson_d, (cx - 1, cy + 9, 2, 1))
    # Paper streamer.
    pygame.draw.line(surf, streamer, (cx, cy + 10), (cx, cy + 15), 1)


def _draw_chochin(surf, anchor, palette, seed, **flags):
    # Two paper lanterns flanking the eave corner (Hōryū-ji festival pair).
    # Reuses the live-game `draw_paper_lantern` so the lantern silhouette,
    # cap bands and glow halo match the rest of the world.
    cx, cy = anchor
    draw_paper_lantern(surf, cx - 8, cy, strand=4, scale=0.85, color='red')
    draw_paper_lantern(surf, cx + 8, cy, strand=4, scale=0.85, color='red')


def _draw_koshi_streamers_on_suien(surf, anchor, palette, seed, **flags):
    # 2 thin streamers hanging from a finial (suien). Reuses the live-game
    # `draw_ribbons_tied` helper so the streamer language matches the rest
    # of the world's cloth-on-pole motifs.
    cx, cy = anchor
    draw_ribbons_tied(surf, cx, cy, n=2, width=10, seed=seed)


def _draw_triangle_bunting(surf, top_rect, bot_rect, palette, seed, **flags):
    # Direct-draw gap-spanner: bunting cord anchored at the two finial-tip
    # centerlines (top pillar's inverted finial down, bottom pillar's sōrin
    # up) with a Bézier sag, then 2-color triangle flags step along the
    # catenary so the strand reads as a real festival rope, not a sticker.
    x1, y1 = top_rect.centerx, top_rect.bottom
    x2, y2 = bot_rect.centerx, bot_rect.top
    sag = 8
    mx, my = (x1 + x2) // 2, max(y1, y2) + sag
    rope = _mix(palette['stone_dark'], (60, 45, 30), 0.7)
    pts = []
    steps = 14
    for i in range(steps + 1):
        t = i / steps
        bx = (1 - t) ** 2 * x1 + 2 * (1 - t) * t * mx + t * t * x2
        by = (1 - t) ** 2 * y1 + 2 * (1 - t) * t * my + t * t * y2
        pts.append((int(bx), int(by)))
    for i in range(len(pts) - 1):
        pygame.draw.line(surf, rope, pts[i], pts[i + 1], 1)
    c1 = _mix(palette['stone_accent'], (235, 110, 90), 0.65)
    c2 = _mix(palette['stone_light'], (245, 240, 220), 0.62)
    # Step over every-other anchor so the flags don't overlap each other.
    for i in range(0, steps, 2):
        x, y = pts[i]
        col = c1 if (i // 2) % 2 == 0 else c2
        pygame.draw.polygon(surf, col, [(x, y), (x + 5, y), (x + 2, y + 5)])


def _draw_calligraphy_banner(surf, anchor, palette, seed, **flags):
    # Tall vertical banner — reuses live-game `draw_darchog_pole` so the
    # banner cloth, gold finial, and trapezoid drape match the lungta-pole
    # ornament that appears on Tibetan pillars in the live game.
    cx, cy = anchor
    accent = palette.get('stone_accent', palette['stone_mid'])
    draw_darchog_pole(surf, cx, cy + 12, height=24, banner_color=accent)


def _draw_wisteria_drape(surf, anchor, palette, seed, **flags):
    # Eave-hanging cascade — reuses the live-game `draw_cascading_vine`
    # helper so the wisteria racemes match the rest of the foliage. The
    # helper uses palette['foliage_*'] for its own colors, which will
    # already read as cool-purple in the rainforest-leaning phases.
    cx, cy = anchor
    draw_cascading_vine(surf, cx, cy, length=20, palette=palette)


def _draw_cherry_blossom_cluster(surf, anchor, palette, seed, **flags):
    # Tight cluster of pink/cream blossoms. Identity hit for Daigo-ji.
    # Round-16: enlarged to ~10 px diameter so it reads as a cluster, not
    # a single sticker.
    cx, cy = anchor
    rng = random.Random(seed * 19 + 13)
    petal_a = _mix(palette['stone_light'], (252, 198, 210), 0.72)
    petal_b = _mix(palette['stone_light'], (248, 232, 225), 0.65)
    branch = _mix(palette['stone_dark'], (90, 60, 45), 0.78)
    pygame.draw.line(surf, branch, (cx - 9, cy + 4), (cx + 9, cy - 2), 1)
    for _ in range(rng.randint(8, 11)):
        bx = cx + rng.randint(-9, 9)
        by = cy + rng.randint(-5, 5)
        col = petal_a if rng.random() < 0.6 else petal_b
        # 4-petal flower: cross of pixels with a centre dot, ≈3 px across.
        pygame.draw.rect(surf, col, (bx - 1, by, 3, 1))
        pygame.draw.rect(surf, col, (bx, by - 1, 1, 3))
        pygame.draw.circle(surf, _mix(col, (220, 140, 100), 0.6), (bx, by), 1)


def _draw_yukimi_stone_lantern(surf, anchor, palette, seed, **flags):
    # SNOW_ONLY. 9 px max (statue). Squat stone lantern with snow cap.
    # Round-16: enlarged to ~9 px so the silhouette reads at game scale.
    cx, cy = anchor
    stone = _mix(palette['stone_mid'], (150, 145, 135), 0.55)
    stone_d = _shade(stone, -25)
    snow = _mix(palette['stone_light'], (248, 248, 252), 0.80)
    # Plinth.
    pygame.draw.rect(surf, stone_d, (cx - 5, cy - 2, 11, 3))
    # Body.
    pygame.draw.rect(surf, stone, (cx - 4, cy - 6, 9, 4))
    # Roof.
    pygame.draw.polygon(surf, stone_d,
                        [(cx - 6, cy - 6), (cx + 6, cy - 6),
                         (cx + 4, cy - 9), (cx - 4, cy - 9)])
    # Snow cap.
    pygame.draw.polygon(surf, snow,
                        [(cx - 6, cy - 8), (cx + 6, cy - 8),
                         (cx + 4, cy - 11), (cx - 4, cy - 11)])


def _draw_twin_lion_stone_lantern(surf, anchor, palette, seed, **flags):
    # 9 px statue cap. MIRRORED poses (AD-mandated, not duplicated).
    # Round-16: enlarged silhouette so the pair reads at game scale.
    cx, cy = anchor
    stone = _mix(palette['stone_mid'], (170, 160, 150), 0.55)
    stone_d = _shade(stone, -30)
    for i, sx in enumerate((-8, 8)):
        # Lion body (sitting): chest forward, tail behind.
        if i == 0:
            pygame.draw.ellipse(surf, stone, (cx + sx - 4, cy - 5, 8, 6))
            pygame.draw.circle(surf, stone, (cx + sx + 3, cy - 6), 3)  # head right
            pygame.draw.polygon(surf, stone_d,
                                [(cx + sx - 4, cy - 1), (cx + sx - 6, cy - 4),
                                 (cx + sx - 5, cy + 2)])  # tail left
        else:
            pygame.draw.ellipse(surf, stone, (cx + sx - 4, cy - 5, 8, 6))
            pygame.draw.circle(surf, stone, (cx + sx - 3, cy - 6), 3)  # head left
            pygame.draw.polygon(surf, stone_d,
                                [(cx + sx + 4, cy - 1), (cx + sx + 6, cy - 4),
                                 (cx + sx + 5, cy + 2)])  # tail right


def _draw_kasuga_stone_lantern(surf, anchor, palette, seed, **flags):
    # 12 px tall. Tall vertical lantern. Bowl/firebox painted crimson
    # lacquer (NOT warm gold) so it can never be confused with a coin when
    # it sits adjacent to the gap; 1-px gold rim retains lantern identity.
    # Round-16: enlarged from ~9 px to ~12 px so the lantern silhouette
    # actually reads at game scale.
    cx, cy = anchor
    stone = _mix(palette['stone_mid'], (165, 155, 140), 0.55)
    stone_d = _shade(stone, -30)
    crimson = _mix(palette['stone_dark'], (165, 35, 35), 0.78)
    gold_rim = _mix(palette['stone_accent'], (230, 180, 90), 0.70)
    # Base + shaft + cap (tall).
    pygame.draw.rect(surf, stone_d, (cx - 4, cy, 9, 2))
    pygame.draw.rect(surf, stone, (cx - 1, cy - 6, 3, 6))
    # Firebox bowl re-hued to crimson lacquer with a 1-px gold rim accent.
    pygame.draw.rect(surf, crimson, (cx - 4, cy - 10, 9, 4))
    pygame.draw.line(surf, gold_rim, (cx - 4, cy - 10), (cx + 4, cy - 10), 1)
    pygame.draw.polygon(surf, stone_d,
                        [(cx - 5, cy - 10), (cx + 5, cy - 10),
                         (cx + 3, cy - 12), (cx - 3, cy - 12)])


def _draw_standing_pilgrim(surf, anchor, palette, seed, **flags):
    # Living human — 7 px cap, muted ochre only. Songyue/Baoen/Muroji only.
    cx, cy = anchor
    robe = _mix(palette['stone_mid'], (170, 130, 80), 0.65)
    robe_d = _shade(robe, -25)
    skin = _mix(palette['stone_light'], (215, 175, 130), 0.60)
    # Robe.
    pygame.draw.rect(surf, robe, (cx - 2, cy - 4, 4, 5))
    pygame.draw.line(surf, robe_d, (cx, cy - 4), (cx, cy + 1), 1)
    # Head — hard cap at 7 px (head sits at cy-5, top at cy-6, hat at cy-7).
    pygame.draw.circle(surf, skin, (cx, cy - 5), 1)
    # Conical pilgrim hat (cy-7 = exactly 7 px above the feet).
    pygame.draw.polygon(surf, robe_d,
                        [(cx - 2, cy - 6), (cx + 2, cy - 6), (cx, cy - 7)])
    # Staff.
    pygame.draw.line(surf, robe_d, (cx + 3, cy - 6), (cx + 3, cy + 1), 1)


def _draw_offering_bowls_trio(surf, anchor, palette, seed, **flags):
    # AD: 2 bowls (not 3). Small bronze offering bowls on a step.
    cx, cy = anchor
    bronze = _mix(palette['stone_accent'], (180, 140, 70), 0.70)
    bronze_d = _shade(bronze, -30)
    for ox in (-4, 4):
        pygame.draw.ellipse(surf, bronze_d, (cx + ox - 2, cy - 2, 5, 3))
        pygame.draw.ellipse(surf, bronze, (cx + ox - 2, cy - 2, 4, 2))


def _draw_prayer_wheel_row(surf, anchor, palette, seed, phase=0.0, **flags):
    # 2 wheels max. Gentle rotation ONLY on day phase — encoded by
    # rotating the spoke seed based on phase bucket.
    cx, cy = anchor
    body = _mix(palette['stone_accent'], (200, 140, 60), 0.70)
    body_d = _shade(body, -30)
    spoke = _mix(palette['stone_dark'], (90, 50, 25), 0.70)
    day = 0.0 <= (phase % 1.0) <= 0.50  # day window
    for i, ox in enumerate((-6, 6)):
        pygame.draw.ellipse(surf, body_d, (cx + ox - 3, cy - 4, 7, 8))
        pygame.draw.ellipse(surf, body, (cx + ox - 2, cy - 3, 5, 6))
        if day:
            # Rotate spoke direction by phase bucket so it visibly steps.
            bucket = _biome.phase_bucket(phase)
            angle = (bucket + i * 7) * 0.6
        else:
            angle = i * 1.1
        sx = math.cos(angle) * 2
        sy = math.sin(angle) * 2
        pygame.draw.line(surf, spoke,
                         (cx + ox - int(sx), cy - int(sy)),
                         (cx + ox + int(sx), cy + int(sy)), 1)


def _draw_mani_stone_cairn(surf, anchor, palette, seed, **flags):
    # Small stack of inscribed stones — reuses live-game `draw_cairn` so
    # the cairn silhouette matches the lungta/cairn pillars in the live
    # game. The cairn grows UPWARD from its base, so anchor the base at
    # the lower part of the cell.
    cx, cy = anchor
    draw_cairn(surf, cx, cy + 8, n=4, pennant=False)


def _draw_suspended_bell_chain(surf, top_rect, bot_rect, palette, seed, **flags):
    # Direct-draw gap-spanner: a single bronze bell hangs at the catenary
    # midpoint between the two finial-tip centerlines, chained up to the
    # top pagoda's inverted spire so the bell reads as suspended FROM the
    # roof, not floating in the middle of the gap.
    tx, ty = top_rect.centerx, top_rect.bottom
    bx_anchor, by_anchor = bot_rect.centerx, bot_rect.top
    cx = (tx + bx_anchor) // 2
    cy = (ty + by_anchor) // 2
    chain = _mix(palette['stone_dark'], (60, 50, 40), 0.7)
    bronze = _mix(palette['stone_accent'], (170, 130, 70), 0.70)
    bronze_d = _shade(bronze, -30)
    # Chain trails up from the bell to the top pillar's inverted finial tip.
    pygame.draw.line(surf, chain, (cx, cy), (tx, ty), 1)
    # Outer (shaded) silhouette ~7 px wide × 7 px tall.
    pygame.draw.polygon(surf, bronze_d,
                        [(cx - 5, cy), (cx + 5, cy),
                         (cx + 4, cy + 7), (cx - 4, cy + 7)])
    # Inner highlight ~5 px wide × 6 px tall.
    pygame.draw.polygon(surf, bronze,
                        [(cx - 4, cy + 1), (cx + 4, cy + 1),
                         (cx + 3, cy + 6), (cx - 3, cy + 6)])
    # Clapper.
    pygame.draw.line(surf, bronze_d, (cx, cy + 6), (cx, cy + 9), 1)


def _draw_roof_smoke_wisp(surf, anchor, palette, seed, **flags):
    # Small incense / kitchen smoke wisp behind the eaves — reuses the
    # live-game `draw_incense_smoke` helper so the smoke trail matches
    # the rest of the world's wisp language. The helper draws UPWARD
    # from (x, y), so anchor at the lower part of the cell.
    cx, cy = anchor
    draw_incense_smoke(surf, cx, cy + 12, length=24)


def _draw_sleeping_dog(surf, anchor, palette, seed, **flags):
    # Quiet first-pillar friendly. ~6 px wide curled silhouette.
    cx, cy = anchor
    body = _mix(palette['stone_dark'], (130, 95, 65), 0.60)
    nose = _shade(body, -25)
    # Curled body — flat comma oval ≈11 px wide × 4 px tall.
    pygame.draw.ellipse(surf, body, (cx - 5, cy - 3, 11, 4))
    pygame.draw.circle(surf, body, (cx + 4, cy - 2), 2)
    pygame.draw.circle(surf, nose, (cx + 5, cy - 1), 1)


def _draw_fairy_light_string(surf, top_rect, bot_rect, palette, seed, **flags):
    # NIGHT_ONLY direct-draw gap-spanner. Warm-amber dots clamped to <=60%
    # of coin luma so the string reads as ambient lights, not a coin column.
    # Cord catenaries between the two finial-tip centerlines, matching the
    # prayer-flag rope so multiple gap ornaments share one visual grammar.
    x1, y1 = top_rect.centerx, top_rect.bottom
    x2, y2 = bot_rect.centerx, bot_rect.top
    sag = 6
    mx, my = (x1 + x2) // 2, max(y1, y2) + sag
    amber = (NIGHT_LUMA_CAP, int(NIGHT_LUMA_CAP * 0.78), int(NIGHT_LUMA_CAP * 0.22))
    cord = _mix(palette['stone_dark'], (40, 30, 25), 0.8)
    pts = []
    steps = 12
    for i in range(steps + 1):
        t = i / steps
        bx = (1 - t) ** 2 * x1 + 2 * (1 - t) * t * mx + t * t * x2
        by = (1 - t) ** 2 * y1 + 2 * (1 - t) * t * my + t * t * y2
        pts.append((int(bx), int(by)))
    for i in range(len(pts) - 1):
        pygame.draw.line(surf, cord, pts[i], pts[i + 1], 1)
    # 9 dots along the catenary → ~5-6 px spacing (>=5 px AD requirement).
    n = 9
    for i in range(n):
        px, py = pts[int((i + 0.5) / n * steps)]
        pygame.draw.circle(surf, amber, (px, py + 1), 2)


def _draw_lit_window_niche(surf, anchor, palette, seed, **flags):
    # NIGHT_ONLY. A small warm window glow on the bottom pillar body.
    # Clamped to the night luma cap. Width ≥3 px and height ≥6 px so the
    # niche reads as a window, not a single bright pixel.
    cx, cy = anchor
    warm = (NIGHT_LUMA_CAP, int(NIGHT_LUMA_CAP * 0.78), int(NIGHT_LUMA_CAP * 0.40))
    frame = _mix(palette['stone_dark'], (40, 30, 20), 0.85)
    pygame.draw.rect(surf, frame, (cx - 2, cy - 4, 5, 8))
    pygame.draw.rect(surf, warm, (cx - 1, cy - 3, 3, 6))
    # Cross mullion so the niche reads as a temple window.
    pygame.draw.line(surf, frame, (cx, cy - 3), (cx, cy + 2), 1)


def _draw_candle_offering_row(surf, anchor, palette, seed, **flags):
    # NIGHT_ONLY. 3 candles fixed-spaced (AD: not randomized). Round-16:
    # bumped flame to a 4-px halo so the candle reads as a flame, not a
    # stray pixel.
    cx, cy = anchor
    flame_core = (NIGHT_LUMA_CAP, int(NIGHT_LUMA_CAP * 0.62), int(NIGHT_LUMA_CAP * 0.15))
    flame_halo = (NIGHT_LUMA_CAP, int(NIGHT_LUMA_CAP * 0.50), int(NIGHT_LUMA_CAP * 0.10), 100)
    wax = _mix(palette['stone_light'], (210, 200, 180), 0.60)
    for ox in (-6, 0, 6):
        pygame.draw.rect(surf, wax, (cx + ox - 1, cy - 3, 2, 3))
        # Soft amber halo (≈4 px) around each flame.
        g = pygame.Surface((8, 8), pygame.SRCALPHA)
        pygame.draw.circle(g, flame_halo, (4, 4), 4)
        surf.blit(g, (cx + ox - 4, cy - 8))
        # Hot core pixel — the actual flame tip.
        pygame.draw.rect(surf, flame_core, (cx + ox, cy - 4, 1, 2))


def _draw_firefly_motes(surf, anchor, palette, seed, **flags):
    # NIGHT_ONLY. Hard cap 4 motes, slow drift, <=60% coin luminance.
    # Round-16: bumped to 2-px dots so the motes actually read at game
    # scale (was single-pixel set_at).
    cx, cy = anchor
    rng = random.Random(seed * 43 + 17)
    glow = (NIGHT_LUMA_CAP, NIGHT_LUMA_CAP, int(NIGHT_LUMA_CAP * 0.55))
    for _ in range(4):
        dx = rng.randint(-18, 18)
        dy = rng.randint(-14, 14)
        pygame.draw.circle(surf, glow, (cx + dx, cy + dy), 2)


# ── Ornament registry ──────────────────────────────────────────────────────

# (zone, draw_fn, default_flags)
_REGISTRY: dict[str, tuple[str, Callable, dict]] = {
    "climbing_vine":           (ZONE_BODY_BOT, _draw_climbing_vine, {}),
    "cat_companion":           (ZONE_PLINTH,   _draw_cat_companion, {"position": "PLINTH"}),
    "petal_drift":             (ZONE_GAP,      _draw_petal_drift, {}),
    "eave_bird":               (ZONE_EAVE,     _draw_eave_bird, {"count": 2}),
    "paper_lantern_string":    (ZONE_EAVE,     _draw_paper_lantern_string, {}),
    "furin_wind_chime":        (ZONE_EAVE,     _draw_furin_wind_chime, {}),
    "chochin":                 (ZONE_EAVE,     _draw_chochin, {}),
    "koshi_streamers_on_suien": (ZONE_FINIAL,  _draw_koshi_streamers_on_suien, {}),
    "prayer_flags":            (ZONE_GAP,      _draw_prayer_flags, {}),
    "triangle_bunting":        (ZONE_GAP,      _draw_triangle_bunting, {}),
    "calligraphy_banner":      (ZONE_EAVE,     _draw_calligraphy_banner, {}),
    "wisteria_drape":          (ZONE_EAVE,     _draw_wisteria_drape, {}),
    "cherry_blossom_cluster":  (ZONE_BODY_TOP, _draw_cherry_blossom_cluster, {}),
    "yukimi_stone_lantern":    (ZONE_PLINTH,   _draw_yukimi_stone_lantern, {}),
    "twin_lion_stone_lantern": (ZONE_PLINTH,   _draw_twin_lion_stone_lantern, {}),
    "kasuga_stone_lantern":    (ZONE_PLINTH,   _draw_kasuga_stone_lantern, {}),
    "standing_pilgrim":        (ZONE_PLINTH,   _draw_standing_pilgrim, {}),
    "offering_bowls_trio":     (ZONE_PLINTH,   _draw_offering_bowls_trio, {}),
    "prayer_wheel_row":        (ZONE_PLINTH,   _draw_prayer_wheel_row, {}),
    "mani_stone_cairn":        (ZONE_PLINTH,   _draw_mani_stone_cairn, {}),
    "suspended_bell_chain":    (ZONE_GAP,      _draw_suspended_bell_chain, {}),
    "roof_smoke_wisp":         (ZONE_ROOF,     _draw_roof_smoke_wisp, {}),
    "sleeping_dog":            (ZONE_PLINTH,   _draw_sleeping_dog, {}),
    "fairy_light_string":      (ZONE_GAP,      _draw_fairy_light_string, {}),
    "lit_window_niche":        (ZONE_BODY_BOT, _draw_lit_window_niche, {}),
    "candle_offering_row":     (ZONE_PLINTH,   _draw_candle_offering_row, {}),
    "firefly_motes":           (ZONE_GAP,      _draw_firefly_motes, {}),
}

# Final pool count target: ~27 ornaments. Confirm:
assert len(_REGISTRY) == 27, f"ornament count drift: {len(_REGISTRY)}"


# Ornaments whose geometry needs the actual pillar rects (gap span, full
# body length) — these bypass the cell cache and draw straight onto the
# live surface. Everything else uses the 64×64 cell cache for cheap
# palette-bucketed reuse across pillars. Every gap-spanning rope ornament
# lives here so the catenary anchors at the two finial-tip centerlines
# (bot_rect.top and top_rect.bottom centered on cx), not at a 64-px cell
# centered on a single picked anchor.
_DIRECT_DRAW: set[str] = {
    "prayer_flags",
    "paper_lantern_string",
    "triangle_bunting",
    "suspended_bell_chain",
    "fairy_light_string",
    "climbing_vine",
}


# ── Classification sets ─────────────────────────────────────────────────────

NIGHT_ONLY: set[str] = {
    "fairy_light_string",
    "lit_window_niche",
    "candle_offering_row",
    "firefly_motes",
}

SNOW_ONLY: set[str] = {
    "yukimi_stone_lantern",
}

# Statues render at <=9 px tall (vs 7 px for living humans). Documented
# here for sanity-check and for any future dev who wants to assert.
STATUE_NAMES: set[str] = {
    "twin_lion_stone_lantern",
    "kasuga_stone_lantern",
    "yukimi_stone_lantern",
}

# Universal pool — appears in every candidate's allow-list (AD-locked).
UNIVERSAL_POOL: tuple[str, ...] = (
    "climbing_vine",
    "cat_companion",
    "petal_drift",
    "eave_bird",
)

# Ornaments that must NEVER anchor to the bottom-facing eave / plinth lip
# that hangs into the flight gap. AD round 15 caught a real coin-confound
# hazard here: a small round ornament dangling at gap height reads as a
# coin pickup at game scale. These items are restricted to SIDE eaves
# (left/right corners of an upper storey) only.
FORBID_BOTTOM_EAVE: set[str] = {
    "furin_wind_chime",
    "kasuga_stone_lantern",
}

# Quiet-only subset for the first-pillar suppression rule. AD: when the
# picker DOES draw on pillar #0 (30% case), pick from this very small set
# so the opening read stays serene.
FIRST_PILLAR_QUIET: tuple[str, ...] = (
    "sleeping_dog",
    "cat_companion",
    "petal_drift",
)


# ── Conflicts ──────────────────────────────────────────────────────────────
#
# Undirected pairs that must NOT both appear on the same pillar. Built
# from the part-2 design doc: two big visual elements in the same zone,
# two birds, two paper-lit objects, etc.

CONFLICTS: set[frozenset[str]] = {
    # Two lantern strings on one eave reads as clutter.
    frozenset({"paper_lantern_string", "chochin"}),
    frozenset({"paper_lantern_string", "fairy_light_string"}),
    frozenset({"chochin", "fairy_light_string"}),
    # Two big drapes / banners on the same eave.
    frozenset({"wisteria_drape", "calligraphy_banner"}),
    frozenset({"wisteria_drape", "paper_lantern_string"}),
    # Two gap-spanning rope ornaments collide visually.
    frozenset({"prayer_flags", "triangle_bunting"}),
    frozenset({"prayer_flags", "fairy_light_string"}),
    frozenset({"triangle_bunting", "fairy_light_string"}),
    frozenset({"prayer_flags", "suspended_bell_chain"}),
    frozenset({"triangle_bunting", "suspended_bell_chain"}),
    # Two living/statue figures on the same tiny plinth.
    frozenset({"standing_pilgrim", "cat_companion"}),
    frozenset({"standing_pilgrim", "sleeping_dog"}),
    frozenset({"cat_companion", "sleeping_dog"}),
    frozenset({"twin_lion_stone_lantern", "kasuga_stone_lantern"}),
    frozenset({"twin_lion_stone_lantern", "yukimi_stone_lantern"}),
    frozenset({"kasuga_stone_lantern", "yukimi_stone_lantern"}),
    frozenset({"twin_lion_stone_lantern", "standing_pilgrim"}),
    frozenset({"twin_lion_stone_lantern", "cat_companion"}),
    # Two plinth objects also collide with a stone lantern.
    frozenset({"offering_bowls_trio", "mani_stone_cairn"}),
    frozenset({"offering_bowls_trio", "prayer_wheel_row"}),
    frozenset({"offering_bowls_trio", "candle_offering_row"}),
    frozenset({"prayer_wheel_row", "mani_stone_cairn"}),
    frozenset({"candle_offering_row", "mani_stone_cairn"}),
    # Two gap items + a chochin hanging into the gap = clutter.
    frozenset({"chochin", "prayer_flags"}),
    frozenset({"chochin", "triangle_bunting"}),
    # Bird + cat at the eave/roof creates a gameplay double-take.
    frozenset({"eave_bird", "roof_smoke_wisp"}),
}


# ── Per-candidate allow-lists (with weights) ───────────────────────────────
#
# Default weight 1.0. AD-specified boosts marked inline. The universal-pool
# items are seeded into every list with weight 1.0 before per-candidate
# overrides apply.

def _with_universal(d: dict[str, float]) -> dict[str, float]:
    out = {name: 1.0 for name in UNIVERSAL_POOL}
    out.update(d)
    return out


ALLOW: dict[str, dict[str, float]] = {
    # Tibetan stupa canopy — prayer flags + wheels are the identity hit.
    "stupa_canopy": _with_universal({
        "prayer_flags":     3.0,    # AD: identity boost
        "prayer_wheel_row": 2.0,    # AD: identity boost
        "mani_stone_cairn": 1.0,
        "offering_bowls_trio": 1.0,
        "suspended_bell_chain": 1.0,
        "candle_offering_row": 1.0,  # night-only
        "lit_window_niche":   2.0,   # AD: night-only ×2.0 boost
        "petal_drift":        1.0,   # AD: ADD
    }),

    # Wat Arun — Thai prang, lanterns + sleeping dog at the temple-grounds.
    "wat_arun": _with_universal({
        "paper_lantern_string": 2.0,  # AD: boost
        "sleeping_dog":         2.0,  # AD: ADD + boost
        "triangle_bunting":     1.0,
        "offering_bowls_trio":  1.0,
        "suspended_bell_chain": 1.0,
        "lit_window_niche":     2.0,   # AD: night-only ×2.0 boost
        "fairy_light_string":   1.0,  # night-only
        # AD: REMOVE wisteria_drape (Japanese-coded).
    }),

    # Songyue sandstone — Chinese, no Japanese-coded items, calligraphy adds in.
    "songyue_sandstone": _with_universal({
        "calligraphy_banner": 2.0,    # AD: ADD + boost
        "eave_bird":          2.0,    # AD: pigeon_pair × 2.0 (merged → eave_bird)
        "standing_pilgrim":   1.0,
        "offering_bowls_trio": 1.0,
        "mani_stone_cairn":   1.0,
        "suspended_bell_chain": 1.0,
        "paper_lantern_string": 1.0,
        "lit_window_niche":   2.0,   # AD: night-only ×2.0 boost
        # AD: furin weight 0.0 (Chinese, not Japanese) → omit.
        # AD: REMOVE kasuga + yukimi (Japanese-coded) → omit.
    }),
    # pigeon_pair × 2.0 (AD): boost eave_bird with count=2 — see picker.

    # Hōryū-ji — OWNS chochin (exclusive vs Tōji). Keep furin + koshi.
    "horyuji": _with_universal({
        "chochin":            1.0,   # AD: OWNS this
        "furin_wind_chime":   1.0,
        "koshi_streamers_on_suien": 1.0,
        "kasuga_stone_lantern": 1.0,
        "roof_smoke_wisp":    1.0,
        "fairy_light_string": 1.0,   # night-only
        "lit_window_niche":   2.0,   # AD: night-only ×2.0 boost
        "candle_offering_row": 1.0,
        # AD: REMOVE pole_flag_on_finial — never added.
    }),

    # Fogong/Yingxian — Liao wooden, Buddhist pilgrim items.
    "fogong": _with_universal({
        "climbing_vine":      1.0,   # AD: explicit ADD (already universal)
        "mani_stone_cairn":   1.0,   # AD: ADD
        "calligraphy_banner": 1.0,
        "paper_lantern_string": 1.0,
        "standing_pilgrim":   1.0,
        "offering_bowls_trio": 1.0,
        "prayer_wheel_row":   1.0,
        "lit_window_niche":   2.0,   # AD: night-only ×2.0 boost
        "candle_offering_row": 1.0,
        # AD: REMOVE any kitsune/Japanese-lion → omit twin_lion + kasuga.
    }),

    # Tō-ji — OWNS koshi_streamers, no chochin (Hōryū-ji's).
    "toji": _with_universal({
        "koshi_streamers_on_suien": 1.0,  # AD: OWNS this
        "furin_wind_chime":   1.0,
        "kasuga_stone_lantern": 1.0,
        "roof_smoke_wisp":    1.0,
        "wisteria_drape":     1.0,
        "fairy_light_string": 1.0,
        "lit_window_niche":   2.0,   # AD: night-only ×2.0 boost
        "candle_offering_row": 1.0,
        # AD: REMOVE chochin.
    }),

    # Daigo-ji — cherry_blossom_cluster is the identity hit (×3.0).
    "daigoji": _with_universal({
        "cherry_blossom_cluster": 3.0,  # AD: identity boost
        # furin_wind_chime dropped to 0.0 on Daigo-ji: the pillar's own
        # vermillion+gold structure already saturates the warm-gold lane,
        # so adding a gap-hanging warm orb made the AD round-15 coin-confound
        # land here first. Lean variation on pink (cherry / petal) + bird.
        "furin_wind_chime":  0.0,
        "kasuga_stone_lantern": 1.0,
        "roof_smoke_wisp":   1.0,
        "lit_window_niche":  2.0,   # AD: night-only ×2.0 boost
        "candle_offering_row": 1.0,
        # AD: REMOVE generic prayer_flags.
    }),

    # Yakushi-ji — Nara bronze, smoke + suien streamers.
    "yakushiji": _with_universal({
        "roof_smoke_wisp":   1.0,   # AD: ADD
        "koshi_streamers_on_suien": 1.0,
        "furin_wind_chime":  1.0,
        "kasuga_stone_lantern": 1.0,
        "calligraphy_banner": 1.0,
        "offering_bowls_trio": 1.0,
        "lit_window_niche":  2.0,   # AD: night-only ×2.0 boost
        "candle_offering_row": 1.0,
    }),

    # Bao'en porcelain — Chinese, calligraphy + prayer wheels.
    "baoen": _with_universal({
        "calligraphy_banner": 1.0,   # AD: ADD
        "prayer_wheel_row":   1.0,   # AD: ADD
        "standing_pilgrim":   1.0,
        "paper_lantern_string": 1.0,
        "offering_bowls_trio": 1.0,
        "mani_stone_cairn":   1.0,
        "suspended_bell_chain": 1.0,
        "lit_window_niche":   2.0,   # AD: night-only ×2.0 boost
        "candle_offering_row": 1.0,
        # AD: REMOVE Japanese-coded items.
    }),

    # Murō-ji — small Japanese, wisteria + petals as the identity.
    "muroji": _with_universal({
        "wisteria_drape":    1.0,    # AD: ADD
        "petal_drift":       1.0,    # AD: ADD (already universal — explicit)
        "standing_pilgrim":  1.0,
        "furin_wind_chime":  1.0,
        "kasuga_stone_lantern": 1.0,
        "roof_smoke_wisp":   1.0,
        "fairy_light_string": 1.0,
        "lit_window_niche":  2.0,   # AD: night-only ×2.0 boost
        "candle_offering_row": 1.0,
    }),

    # Palsangjeon — Korean wooden, twin lions + eave birds.
    "palsangjeon": _with_universal({
        "twin_lion_stone_lantern": 1.0,  # AD: KEEP
        "eave_bird":               1.0,  # AD: ADD (already universal)
        "paper_lantern_string":    1.0,
        "calligraphy_banner":      1.0,
        "offering_bowls_trio":     1.0,
        "roof_smoke_wisp":         1.0,
        "lit_window_niche":        2.0,   # AD: night-only ×2.0 boost
        "candle_offering_row":     1.0,
        # AD: REMOVE wisteria, furin.
    }),
}


# ── Per-(name) flag overrides ──────────────────────────────────────────────
#
# Songyue's eave_bird is biased toward count=2 (pigeons) per the AD's
# "pigeon_pair × 2.0" rule. Encode as a per-candidate flag override so the
# picker hands the right flag to the draw function.

FLAG_OVERRIDES: dict[str, dict[str, dict]] = {
    "songyue_sandstone": {
        "eave_bird": {"count": 2},      # AD: pigeon_pair × 2.0
    },
    # The other candidates roll count 50/50 in the picker — see _pick_flags.
}


# ── Anchor resolution ──────────────────────────────────────────────────────
#
# Compute a deterministic (x, y) for each zone given the pillar pair. The
# bottom pillar is the dominant ornament surface because it's the one the
# bird flies past at body height.

# Storey-row geometry used by the eave anchor resolver. The pagoda envelopes
# in `pillar_pagoda_variants*.py` use finial_h ≈ 36 and tier rows roughly
# 18 px apart; resolving to the actual storey grid would require importing
# the envelope solver here. The approximation is accurate enough for hanging
# ornaments to read as "off the eave corner" rather than "off the rect edge".
_FINIAL_H_APPROX = 36
_STOREY_H_APPROX = 18
_EAVE_OVERHANG = 4  # px the eave-corner sticks out past the rect width


def _anchor_for_zone(zone: str, top_rect: pygame.Rect,
                     bot_rect: pygame.Rect, rng: random.Random,
                     forbid_bottom_eave: bool = False) -> tuple[int, int]:
    bcx = bot_rect.x + bot_rect.width // 2
    tcx = top_rect.x + top_rect.width // 2
    gap_mid_y = (top_rect.bottom + bot_rect.y) // 2

    if zone == ZONE_BODY_BOT:
        # Mid-shaft of the bottom pillar (legible while flying).
        return (bot_rect.x + 4, bot_rect.bottom - 60 + rng.randint(-6, 6))
    if zone == ZONE_BODY_TOP:
        # Just below the gap roof, on the bottom pillar's upper shaft.
        return (bcx + rng.randint(-4, 4), bot_rect.y + 14 + rng.randint(0, 8))
    if zone == ZONE_GAP:
        # Cell-based GAP ornaments are ambient (petal drift, fireflies) — a
        # rough gap-midpoint anchor is correct. Gap-spanning rope ornaments
        # live in _DIRECT_DRAW and use top_rect/bot_rect finial tips
        # explicitly, so they never hit this branch.
        return (bcx + rng.randint(-3, 3), gap_mid_y + rng.randint(-4, 4))
    if zone == ZONE_PLINTH:
        # Plinth ornaments REST on the actual ground line, not float a few
        # px above the bottom-pillar rect. Seed-driven side choice puts the
        # item at the left edge, right edge, or centered on the plinth.
        plinth_inset = 8
        roll = rng.random()
        if roll < 0.34:
            return (bot_rect.x + plinth_inset, GROUND_Y)
        if roll < 0.67:
            return (bot_rect.right - plinth_inset, GROUND_Y)
        return (bcx, GROUND_Y)
    if zone == ZONE_FINIAL:
        # FINIAL zone = bottom pagoda's sōrin tip. Push 2 px INTO the spire
        # so a pole flag / streamers emerge from the top jewel rather than
        # floating above it.
        return (bcx, bot_rect.top - 2)
    if zone == ZONE_EAVE:
        # The TOP pillar is the inverted-hanging pagoda; its eaves point
        # down into the gap and curl UP at the corners. Anchor at one of
        # those eave-corner tips (left or right, seed-picked) on a row
        # measured from the inverted-finial end. Row 0 = the row CLOSEST
        # to the gap; rows 1-2 = progressively further from the gap (up
        # toward the inverted plinth at top_rect.top). FORBID_BOTTOM_EAVE
        # forces row=2 so coin-confound items hang well above the flight
        # corridor against the inverted upper-body silhouette.
        side = -1 if rng.random() < 0.5 else 1
        eave_row = 2 if forbid_bottom_eave else rng.randint(0, 2)
        y_eave = top_rect.bottom - _FINIAL_H_APPROX - eave_row * _STOREY_H_APPROX
        if side < 0:
            return (top_rect.x - _EAVE_OVERHANG, y_eave)
        return (top_rect.right + _EAVE_OVERHANG, y_eave)
    if zone == ZONE_ROOF:
        # Pigeon / cat / smoke wisp sit on the topmost eave centerline,
        # 2 px INTO the spire so the silhouette overlaps the roofline
        # rather than floating above it.
        return (bcx, bot_rect.top + 2)
    return (bcx, GROUND_Y)


# ── Picker ─────────────────────────────────────────────────────────────────

# Existing live-game weights for ornament count. AD: keep 25/50/20/5
# for normal pillars; pillar #0 uses the special 70/30 quiet rule.
_COUNT_WEIGHTS_DEFAULT = ((0, 25), (1, 50), (2, 20), (3, 5))


def _weighted_choice(rng: random.Random,
                     options: list[tuple[str, float]]) -> str | None:
    total = sum(w for _, w in options)
    if total <= 0:
        return None
    r = rng.random() * total
    acc = 0.0
    for name, w in options:
        acc += w
        if r <= acc:
            return name
    return options[-1][0]


def _pick_count(rng: random.Random) -> int:
    total = sum(w for _, w in _COUNT_WEIGHTS_DEFAULT)
    r = rng.random() * total
    acc = 0
    for n, w in _COUNT_WEIGHTS_DEFAULT:
        acc += w
        if r <= acc:
            return n
    return 0


def _eligible(name: str, phase: float) -> bool:
    if name in NIGHT_ONLY and not _is_night(phase):
        return False
    if name in SNOW_ONLY:
        # No snow biome in the live game yet — gate SNOW_ONLY off in the
        # picker so it stays reserved without polluting normal phases.
        return False
    return True


def _pick_flags(candidate_key: str, name: str,
                rng: random.Random, phase: float) -> dict:
    """Compose per-ornament runtime flags (count, position, phase, etc.)."""
    flags: dict = dict(_REGISTRY[name][2])  # start from registry defaults
    # Per-candidate override (e.g. Songyue's pigeon_pair).
    override = FLAG_OVERRIDES.get(candidate_key, {}).get(name)
    if override:
        flags.update(override)
    # General flag rolls.
    if name == "eave_bird" and "count" not in (override or {}):
        flags["count"] = 2 if rng.random() < 0.5 else 1
    if name == "cat_companion":
        flags["position"] = "ROOF" if rng.random() < 0.30 else "PLINTH"
    # Picker hands `phase` down so prayer_wheel_row can decide rotation.
    flags["phase"] = phase
    return flags


def pick_ornaments(rng: random.Random,
                   candidate_key: str,
                   pillar_index: int,
                   phase: float,
                   is_rush: bool) -> tuple[tuple[str, dict], ...]:
    """Return the ornament names + flags to draw on this pillar pair."""
    # Coin rush forces clean pillars (AD-set).
    if is_rush:
        return ()
    allow = ALLOW.get(candidate_key)
    if not allow:
        return ()

    # First-pillar suppression (AD: 70% n=0, 30% one quiet ornament).
    if pillar_index == 0:
        if rng.random() < 0.70:
            return ()
        quiet_opts = [
            (n, allow.get(n, 1.0))
            for n in FIRST_PILLAR_QUIET
            if n in allow and _eligible(n, phase)
        ]
        if not quiet_opts:
            return ()
        name = _weighted_choice(rng, quiet_opts)
        if name is None:
            return ()
        return ((name, _pick_flags(candidate_key, name, rng, phase)),)

    # Normal count roll for pillars beyond the first.
    n = _pick_count(rng)
    if n == 0:
        return ()

    picks: list[tuple[str, dict]] = []
    chosen: set[str] = set()
    for _ in range(n):
        opts: list[tuple[str, float]] = []
        for name, w in allow.items():
            if name in chosen:
                continue
            if not _eligible(name, phase):
                continue
            # Conflict guard: skip if any already-chosen pairs with this one.
            if any(frozenset({name, c}) in CONFLICTS for c in chosen):
                continue
            opts.append((name, w))
        if not opts:
            break
        name = _weighted_choice(rng, opts)
        if name is None:
            break
        chosen.add(name)
        picks.append((name, _pick_flags(candidate_key, name, rng, phase)))
    return tuple(picks)


# ── Cached ornament cells (tiny, palette-bucketed) ─────────────────────────
#
# Each cell-local ornament is drawn into a SRCALPHA cell at most 64×64 keyed
# by (name, phase_bucket, flag_signature). At apply time we blit the cell
# onto the live surface at the resolved anchor — this amortizes the
# palette interpolation maths across all pillars in the session and
# matches the cache pattern used by the sky/glow caches in `game/draw.py`.
# Direct-draw ornaments (gap-spanning, body-length) bypass this cache
# because their geometry depends on per-pillar rects.

_CELL_W = 64
_CELL_H = 64
_CELL_CX = _CELL_W // 2
_CELL_CY = _CELL_H // 2
# Bounded LRU: keyed partly by phase bucket, so a finer PHASE_BUCKETS would let
# this grow ~linearly with the bucket count over a session. Only a few ornament
# kinds are on screen at once (x2 buckets mid-fade), so a cap well above the live
# working set evicts stale bucket variants without thrash. Cells are tiny (64x64).
_CELL_CACHE_MAX = 256
_CELL_CACHE: "OrderedDict[tuple, pygame.Surface]" = OrderedDict()


def _flag_signature(flags: dict) -> tuple:
    return tuple(sorted(
        (k, v) for k, v in flags.items()
        if k != "phase" and isinstance(v, (str, int, float, bool, type(None)))
    ))


def _get_cell(name: str, palette: dict, phase: float,
              seed: int, flags: dict) -> pygame.Surface:
    bucket = _biome.phase_bucket(phase)
    # Seeds are 24-bit, so a narrow modulus collides often — and the cell is
    # baked with the *full* seed, so colliding pipes would silently wear the
    # first pipe's art (and re-bake from a different seed after an eviction).
    key = (name, bucket, seed % 1024, _flag_signature(flags))
    cached = _CELL_CACHE.get(key)
    if cached is not None:
        _CELL_CACHE.move_to_end(key)
        return cached
    cell = pygame.Surface((_CELL_W, _CELL_H), pygame.SRCALPHA)
    _, draw_fn, _ = _REGISTRY[name]
    draw_fn(cell, (_CELL_CX, _CELL_CY), palette, seed, **flags)
    _CELL_CACHE[key] = cell
    if len(_CELL_CACHE) > _CELL_CACHE_MAX:
        _CELL_CACHE.popitem(last=False)
    return cell


# ── Entry point ────────────────────────────────────────────────────────────

def apply_ornaments(surf: pygame.Surface,
                    top_rect: pygame.Rect,
                    bot_rect: pygame.Rect,
                    candidate_key: str,
                    palette: dict,
                    seed: int,
                    phase: float,
                    pillar_index: int = 1,
                    is_rush: bool = False) -> tuple[str, ...]:
    """Paint the ornament layer on top of an already-drawn pillar pair.

    Returns the tuple of ornament names that were applied (for label/debug).
    """
    # The seed must NOT carry `phase`. This rng drives the count, the pick,
    # the per-ornament flags AND the anchor, so any live term in it re-rolls
    # the whole pillar every time it ticks — at CYCLE_SECONDS that was a
    # fresh ornament set ~2.5x/second. Phase still reaches the eligibility
    # gates via pick_ornaments and the palette via _get_cell; it just can't
    # touch the stream. Placement is a pure function of the Pipe's seed.
    rng = random.Random(seed * 1009 + pillar_index * 17)
    picks = pick_ornaments(rng, candidate_key, pillar_index, phase, is_rush)
    if not picks:
        return ()
    applied: list[str] = []
    for name, flags in picks:
        zone, draw_fn, _ = _REGISTRY[name]
        if name in _DIRECT_DRAW:
            # Direct-draw ornaments need the pillar rects to compute their
            # geometry (gap-spanning catenary, body-length vine, etc.) —
            # bypass the cell cache and paint straight onto the surface.
            draw_fn(surf, top_rect, bot_rect, palette, seed, **flags)
        else:
            anchor = _anchor_for_zone(
                zone, top_rect, bot_rect, rng,
                forbid_bottom_eave=(name in FORBID_BOTTOM_EAVE),
            )
            cell = _get_cell(name, palette, phase, seed, flags)
            surf.blit(cell, (anchor[0] - _CELL_CX, anchor[1] - _CELL_CY))
        applied.append(name)
    return tuple(applied)
