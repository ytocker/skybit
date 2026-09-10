"""Standalone candidate: `phoenix-vane-mill` — a slender Song-brick shrine
SPIRE (a tall, thin battered needle) crowned by one commanding gilded
weathervane: a spread-winged PHOENIX cast in gilt, wings out to both flanks,
that catches a night halo like a shrine icon.

Colocated EXPLORATION module for the pillar-landmark design loop (TEMPLE-MILL
family). It follows the shipped pagoda idiom
(`candidate_*(surf, top_rect, bot_rect, palette, seed)`, an upright `_draw_one`
reused for both rects, the ceiling twin a vertical flip of a temp surface) but
does NOT import into or modify any game/ module — it only borrows read-only
colour + AA + ornament helpers so the exploration reads like the real game at
the pagoda fidelity bar. It reuses the seed's battered brick-temple material
kit (masonry scan-lines, corbel string-courses, plinth + mist + foliage
harness) and REMOVES the water-wheel + water entirely.

Silhouette identity (set-level pin): the ONLY concept whose crown is a
recognizable CREATURE — a big gilt spread-winged phoenix perched on a needle
spire. Blackout reads as a thin brick spike under one broad figural bird.

Mirror pin (make-or-break): the phoenix is a FRONTAL, SPREAD-WINGED bird —
head/neck/beak dead-centred on `cx`, wings swept UP-AND-OUT to both flanks as
the dominant horizontal mass, a dense rounded HEAD-knob poking above the wing
line, and a single airy TAIL plume streaming below. It is bilaterally symmetric
L/R by construction (so left/right survive trivially), and its two poles are
END TERMINATIONS of different character — a compact solid knob at one end, a
long airy streamer fan at the other — so a vertical FLIP (top↔bottom) still
hangs a legible knob-end + plume-end phoenix on the twin (wings merely sweep
the other way). This is the deliberate resolution of the figural-bird flip
risk: NOT a side-profile bird (which would hang upside-down and break), and NOT
a diving-phoenix gamble.

Column-fill contract: the ~58 px collision column is carried top-to-bottom by
the BRICK SPIRE + corbel cap + bronze staff on the centreline — never the bird.
The spire base grounds the column, the taper stays continuous (centre always
occupied), and the staff + phoenix crest carry the centreline up to the gap
rim. The phoenix wing-spread is pure gutter overhang laid over that masonry.

Run:  python docs/pillar_landmarks/temple_mills/phoenix-vane-mill/render.py
Out:  docs/pillar_landmarks/temple_mills/phoenix-vane-mill/round_2.png
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
    _is_dark_sky,
    _is_warming_sky,                # noqa: F401 — imported per brief material kit
    _cap_lit_for_dark_sky,
    _cap_dark_for_dark_sky,
    _terracotta,
    _song_brick,                    # noqa: F401 — imported per brief material kit
    _bronze,
    _gold_bright,
    _gold_deep,
    _vermilion,
    _brick_mortar,
    _songyue_dwarf_eave,
)
from game.pillar_variants import draw_grass_bed, draw_spiral_glow
from game.draw import draw_side_shrub


# ── Material roles (all biome-derived via _mix/_shade so day→night retints) ───
#
# BRICK SPIRE  → stone_dark / stone_mid (_terracotta + _brick_mortar): a warm
#   clay shrine needle, the slender lead-the-eye body under the crown.
# PHOENIX      → stone_accent (_gold_bright / _gold_deep + _bronze): gilt bird
#   with a bright specular + dark keyline so it reads as gleaming gilt metal.
# CREST + TAIL → horizon-warm (_vermilion): the shu-iro plume accents.
# EYE GLINT / SPECULAR → stone_light: the one cool spark on the gilt.

def _brick_lit(p):
    # Sun-side clay — capped at dusk/night so the shaded flank carries the
    # silhouette instead of a value-spiking wall.
    return _cap_lit_for_dark_sky(_shade(_terracotta(p), 28), p)


def _brick_mid(p):
    return _terracotta(p)


def _brick_shadow(p):
    # Floored at night so the shaded spire edge keeps value over a deep sky and
    # the thin needle doesn't collapse into one black sliver.
    return _cap_dark_for_dark_sky(_shade(_terracotta(p), -42), p, floor=60)


def _mortar(p):
    return _shade(_brick_mortar(p), 16)


def _edge_rim(p):
    # Faint cool-lit rim run down the shadow-side outline at night so the slim
    # spire holds its edge against a dark sky (day palettes never trigger it).
    return _mix(p['stone_mid'], p['stone_light'], 0.55)


# ── Slender brick spire body ─────────────────────────────────────────────────

def _brick_spire(surf, cx, top_y, base_y, hw_top, hw_base, palette):
    """Steeply-battered brick trapezoid painted as horizontal scan-lines, each a
    short left-lit → mid → right-shadow ramp, so the flat needle reads as
    rounded masonry volume at PIPE_W=58. Mortar coursing every 3 px with a
    broken half-cell offset reads brick-bond, not stripes. WASM-safe: only
    pygame.draw 1-px lines. Slimmer taper than the seed cone — the lead-the-eye
    needle under the perched phoenix."""
    lit, mid, shadow = _brick_lit(palette), _brick_mid(palette), _brick_shadow(palette)
    mortar = _mortar(palette)
    rim = _edge_rim(palette)
    dark_sky = _is_dark_sky(palette)
    h = base_y - top_y
    if h < 2:
        return
    for i in range(h):
        y = top_y + i
        t = i / (h - 1)                       # 0 at shoulder, 1 at base
        hw = int(round(hw_top + (hw_base - hw_top) * t))
        if hw < 1:
            continue
        for j in range(hw):
            u = j / max(1, hw)
            pygame.draw.line(surf, _mix(lit, mid, u),
                             (cx - hw + j, y), (cx - hw + j, y), 1)
            pygame.draw.line(surf, _mix(mid, shadow, u),
                             (cx + j, y), (cx + j, y), 1)
        # Brick coursing: mortar row every 3 px, alternate rows broken at the
        # centreline for a bonded-masonry read rather than ledger stripes.
        if i % 3 == 2:
            if (i // 3) % 2 == 0:
                pygame.draw.line(surf, mortar,
                                 (cx - hw + 1, y), (cx + hw - 1, y), 1)
            else:
                pygame.draw.line(surf, mortar,
                                 (cx - hw + 1, y), (cx - 1, y), 1)
                pygame.draw.line(surf, mortar,
                                 (cx + 1, y), (cx + hw - 1, y), 1)
        if dark_sky:
            pygame.draw.line(surf, rim, (cx + hw - 1, y), (cx + hw - 1, y), 1)
    # AA the two sloping silhouette edges so the needle flanks read smooth.
    edge = _shade(_brick_shadow(palette), -18)
    _aa_polyline(surf, edge, [(cx - hw_top, top_y), (cx - hw_base, base_y)])
    _aa_polyline(surf, edge, [(cx + hw_top, top_y), (cx + hw_base, base_y)])


def _corbel_neck(surf, cx, shoulder_y, neck_top_y, hw_cap, palette):
    """A short stack of corbel string-courses stepping in from the slim
    shoulder to the base of the bronze vane-staff. Keeps the centreline
    continuously occupied above the spire so the collision column never breaks
    below the crown."""
    cap_h = shoulder_y - neck_top_y
    if cap_h < 4:
        _songyue_dwarf_eave(surf, cx, shoulder_y, hw_cap, palette, depth=2)
        return
    n = max(2, min(3, cap_h // 5))
    for k in range(n):
        tt = k / max(1, n)
        y = int(shoulder_y - tt * cap_h)
        hw = int(hw_cap * (1.0 - 0.5 * tt))
        band_h = max(2, cap_h // n + 1)
        _gradient_rect(surf, pygame.Rect(cx - hw, y - band_h, hw * 2, band_h),
                       _brick_lit(palette), _brick_mid(palette),
                       _brick_shadow(palette))
        _songyue_dwarf_eave(surf, cx, y - band_h, hw, palette, depth=2)


def _vane_staff(surf, cx, staff_top_y, staff_base_y, palette):
    """Bronze weathervane staff carrying the phoenix above the corbel neck —
    a 2-px shaft with a lit edge and a small bronze collar-boss at the foot,
    holding the centreline between the masonry and the perched bird."""
    bronze = _bronze(palette)
    pygame.draw.line(surf, _shade(bronze, -34),
                     (cx + 1, staff_top_y), (cx + 1, staff_base_y), 2)
    pygame.draw.line(surf, _shade(bronze, 20),
                     (cx - 1, staff_top_y), (cx - 1, staff_base_y), 1)
    pygame.draw.circle(surf, bronze, (cx, staff_base_y), 3)
    pygame.draw.circle(surf, _gold_deep(palette), (cx, staff_base_y), 2)
    pygame.draw.circle(surf, _gold_bright(palette), (cx - 1, staff_base_y - 1), 1)


# ── The gilded phoenix weathervane (frontal spread-winged medallion) ─────────

def _ipts(pts):
    return [(int(round(x)), int(round(y))) for x, y in pts]


def _feather(surf, base, ang, ln, w0, w1, side, fill, lit, dark):
    """One tapered gilt feather quad from a pivot `base` along `ang` (radians,
    0 = straight out to `side`, negative = up, positive = down), length `ln`,
    root/tip half-widths `w0`/`w1`. Filled `fill` with a lit leading edge and a
    dark keyline trailing edge so the plume reads as gleaming gilt in relief.
    Returns the tip point so the caller can key the wing's outer silhouette."""
    ux, uy = math.cos(ang) * side, math.sin(ang)
    tip = (base[0] + ux * ln, base[1] + uy * ln)
    nx, ny = -uy, ux
    root_a = (base[0] + nx * w0, base[1] + ny * w0)
    root_b = (base[0] - nx * w0, base[1] - ny * w0)
    tip_a = (tip[0] + nx * w1, tip[1] + ny * w1)
    tip_b = (tip[0] - nx * w1, tip[1] - ny * w1)
    pygame.draw.polygon(surf, fill, _ipts([root_a, tip_a, tip_b, root_b]))
    _aa_polyline(surf, lit, [root_a, tip_a])
    _aa_polyline(surf, dark, [root_b, tip_b])
    return tip


# Beak apex sits r*_PHOENIX_TOP_REACH above the body centre `cy`; the crown
# placement keys off this so the head-lobe clears the gap rim by ~3 px.
_PHOENIX_TOP_REACH = 1.5


def _phoenix(surf, cx, cy, r, palette, *, sun=-1.0):
    """A frontal, spread-winged gilt PHOENIX weathervane centred on (cx, cy).

    Reads as an UNMISTAKABLE BIRD at 58 px: a dense rounded HEAD-knob on a
    short neck pokes clearly ABOVE the wing line as its own silhouette lobe,
    broad wings sweep UP-AND-OUT to both flanks as the dominant HORIZONTAL mass
    under one clean swept leading edge, and a single airy trailing TAIL plume
    streams below. Head-end (compact solid knob) and tail-end (long airy
    streamer fan) are of DIFFERENT character, so one end is plainly a head —
    yet each end is a plume/knob TERMINATION, so a top↔bottom FLIP still hangs a
    legible knob-end + plume-end phoenix. Bilaterally symmetric L/R by
    construction (head/neck/beak dead on cx, wings mirrored). Feather relief +
    eye glints are close-up reward; gilt sells via a bright specular + dark
    keyline with `_vermilion` crest/tail accents."""
    gold_l = _gold_bright(palette)
    gold_d = _gold_deep(palette)
    bronze = _bronze(palette)
    verm = _vermilion(palette)
    verm_lit = _mix(verm, (236, 108, 84), 0.55)
    key = _shade(bronze, -46)                     # dark keyline for gilt edge
    spec = _mix(gold_l, palette['stone_light'], 0.62)   # bright specular gleam

    # Capped feather count + thick tips → the outer keyline is ONE swept curve
    # at squint, not fraying noise.
    n_feather = 4 if r >= 14 else 3
    body_hw = max(2, r * 0.24)
    wing_span = r * 1.5

    # ── Wings — bold primaries swept UP-AND-OUT to both flanks (no downward
    # fan), the outermost feather flattest + longest so the wing spread is the
    # dominant horizontal mass with a clean swept leading edge. Drawn first so
    # the body + head overlap the roots.
    for s in (1, -1):
        pivot = (cx + s * body_hw * 0.5, cy - r * 0.12)
        tips = []
        for k in range(n_feather):
            f = k / (n_feather - 1)               # 0 outer/flat → 1 inner/steep
            ang = -(0.06 + 0.95 * f)              # all sweep upward — never down
            ln = wing_span * (1.0 - 0.40 * f)     # outermost feather the longest
            face = 0.5 + 0.5 * (math.cos(ang) * (s * -sun)) - 0.18 * f
            fill = _mix(gold_d, gold_l, max(0.0, min(1.0, face)))
            lit = _mix(gold_l, spec, 0.4) if s * -sun > 0 else _mix(gold_d, gold_l, 0.42)
            tip = _feather(surf, pivot, ang, ln,
                           w0=max(1.8, r * 0.14), w1=max(1.2, r * 0.075),
                           side=s, fill=fill, lit=lit, dark=key)
            tips.append(tip)
        # One bold swept keyline over the fanned tips → clean outer silhouette.
        _aa_polyline(surf, key, [pivot] + tips)
        # A short covert row over the wing root for close-up depth (also up-out).
        for k in range(2):
            f = (k + 0.5) / 2
            _feather(surf, (cx + s * body_hw * 0.3, cy - r * 0.06),
                     -(0.15 + 0.7 * f), wing_span * 0.4,
                     max(1.4, r * 0.10), max(0.9, r * 0.05),
                     side=s, fill=_mix(gold_l, gold_d, 0.3),
                     lit=spec, dark=_shade(gold_d, -18))

    # ── Tail — a SINGLE airy trailing plume below (narrow fan, long streamers),
    # deliberately different in character from the wings so the lower half reads
    # as body + one trailing tail, not a second set of wings.
    tail_base = (cx, cy + r * 0.46)
    n_tail = 3 if r >= 12 else 1
    for k in range(n_tail):
        f = (k / (n_tail - 1) - 0.5) if n_tail > 1 else 0.0
        theta = math.pi / 2 + f * 0.5             # narrow downward fan
        ln = r * (1.9 - 1.0 * abs(f))             # long centre streamer — body
        col = verm if k == n_tail // 2 else gold_d
        litc = verm_lit if k == n_tail // 2 else gold_l
        _feather(surf, tail_base, theta, ln,
                 w0=max(1.5, r * 0.11), w1=max(0.7, r * 0.045),
                 side=1, fill=col, lit=litc, dark=key)
        # Phoenix tail eye-spot near each streamer tip (close-up reward).
        if r >= 16:
            ex = int(tail_base[0] + math.cos(theta) * ln * 0.78)
            ey = int(tail_base[1] + math.sin(theta) * ln * 0.78)
            pygame.draw.circle(surf, gold_l, (ex, ey), 2)
            pygame.draw.circle(surf, verm, (ex, ey), 1)

    # ── Body — a compact central gilt spindle on the centreline, joining the
    # neck to the tail root; lit-left / shadow-right for gilt relief.
    b_top = cy - r * 0.5
    b_bot = cy + r * 0.62
    body = [(cx, b_top),
            (cx + body_hw, cy + r * 0.06),
            (cx + body_hw * 0.5, cy + r * 0.5),
            (cx, b_bot),
            (cx - body_hw * 0.5, cy + r * 0.5),
            (cx - body_hw, cy + r * 0.06)]
    pygame.draw.polygon(surf, gold_d, _ipts(body))
    lit_body = [(cx, b_top), (cx, b_bot),
                (cx - body_hw * 0.5, cy + r * 0.5),
                (cx - body_hw, cy + r * 0.06)]
    pygame.draw.polygon(surf, _mix(gold_l, gold_d, 0.25), _ipts(lit_body))
    _aa_polyline(surf, spec, [(cx - 1, b_top + 1), (cx - 1, b_bot - 1)])
    _aa_polyline(surf, key, _ipts(body), closed=True)

    # ── Neck + HEAD — a compact, dense rounded gilt knob on a short neck that
    # pokes clearly ABOVE the wing line as its own silhouette lobe: the single
    # cue that turns the gilt medallion into an unmistakable bird. Drawn LAST so
    # it sits proud over the wing roots.
    hr = max(3, int(r * 0.32))
    hy = int(cy - r * 0.95)
    neck_w = max(2, int(r * 0.16))
    pygame.draw.line(surf, gold_d, (cx, int(b_top)), (cx, hy), neck_w)
    pygame.draw.line(surf, _mix(gold_l, gold_d, 0.3),
                     (cx - 1, int(b_top)), (cx - 1, hy), 1)
    pygame.draw.circle(surf, gold_l, (cx, hy), hr)
    pygame.draw.circle(surf, spec, (cx - max(1, hr // 3), hy - max(1, hr // 3)),
                       max(1, hr // 2))
    pygame.draw.circle(surf, key, (cx, hy), hr, 1)
    # Twin frontal eyes (symmetric) + a small upward gilt beak apex — the beak
    # is the topmost centreline point (keys the ~3 px rim clearance).
    eox = max(1, hr // 2)
    for s in (1, -1):
        pygame.draw.circle(surf, key, (cx + s * eox, hy - max(1, hr // 4)),
                           max(1, hr // 4))
        if hr >= 5:
            pygame.draw.circle(surf, spec, (cx + s * eox, hy - max(1, hr // 4)), 1)
    pygame.draw.polygon(surf, _shade(gold_d, -6),
                        _ipts([(cx - hr * 0.4, hy - hr * 0.7),
                               (cx + hr * 0.4, hy - hr * 0.7),
                               (cx, cy - r * _PHOENIX_TOP_REACH)]))
    # A short twin vermilion crest tuft flanking the beak — phoenix accent kept
    # compact so the solid head-knob still dominates the top lobe.
    if r >= 12:
        for cf in (-0.22, 0.22):
            _feather(surf, (cx, hy - hr * 0.4), -math.pi / 2 + cf, r * 0.36,
                     max(1.0, r * 0.06), max(0.5, r * 0.03),
                     side=1, fill=verm, lit=verm_lit, dark=key)


def _gilt_halo(surf, cx, cy, r, palette):
    """Broad soft gold halo behind the phoenix — additive so the gilt bird
    reads as glowing like a lit shrine icon after dark. Gated by the caller on
    `_is_dark_sky` so day palettes never trigger it."""
    warm = _mix(_gold_bright(palette), (255, 226, 150), 0.7)
    R = max(6, int(r * 2.3))
    g = pygame.Surface((R * 2, R * 2), pygame.SRCALPHA)
    for ring, a in ((1.0, 26), (0.72, 52), (0.48, 92), (0.26, 140)):
        pygame.draw.circle(g, (*warm, a), (R, R), int(R * ring))
    surf.blit(g, (cx - R, cy - R), special_flags=pygame.BLEND_RGBA_ADD)


# ── One upright silhouette ───────────────────────────────────────────────────

def _draw_one(surf, cx, base_y, top_y, body_w, palette, seed, *, decor=True):
    """One upright phoenix-vane-mill filling [top_y, base_y]. Height-adaptive:
    the slim spire batter stays continuous so the centre-column is always
    occupied; the crown budget (staff + phoenix) scales with the phoenix radius
    so short sections get a smaller bird, very short ones just the finial-staff
    while the spire still fills the column."""
    total_h = base_y - top_y
    if total_h < 20:
        return

    # Phoenix radius scales with height (bold at full height, small when short).
    r = int(max(0, min(total_h * 0.15, body_w * 0.92, 30)))
    have_bird = total_h >= 46 and r >= 6

    # Crown budget above the brick shaft: the head-forward phoenix reaches from
    # the beak apex (r*1.5 above centre) down past the tail (~r*2 below), so the
    # crown region spans ~3.6r; a short staff foot anchors it to the neck.
    staff_len = max(6, int(r * 0.5)) if have_bird else max(6, int(total_h * 0.12))
    crown_h = (int(r * 3.6 + staff_len) if have_bird
               else min(int(total_h * 0.2), 26))
    crown_h = min(crown_h, int(total_h * 0.6))
    shoulder_y = top_y + crown_h

    # Slim needle: base grounds the 58px column, taper is continuous to a slim
    # shoulder. The centreline (staff + crest) carries fill to the rim above.
    hw_base = max(PIPE_W // 2 - 2, int(body_w * 0.58))
    hw_cap = max(9, int(hw_base * 0.42))          # slender top

    # 3-layer plinth under the spire.
    plinth_h = 6 if total_h > 60 else 3
    pw0 = hw_base * 2 + 12
    if decor:
        _draw_plinth_mist(surf, cx, base_y, pw0 + 8, palette)
    pygame.draw.rect(surf, _shade(palette['stone_dark'], -16),
                     (cx - pw0 // 2, base_y - plinth_h, pw0, plinth_h))
    pygame.draw.rect(surf, _shade(palette['stone_mid'], -6),
                     (cx - pw0 // 2 + 2, base_y - plinth_h + 1, pw0 - 4, 2))
    pygame.draw.line(surf, palette['stone_light'],
                     (cx - pw0 // 2, base_y - plinth_h),
                     (cx + pw0 // 2, base_y - plinth_h), 1)

    body_base_y = base_y - plinth_h
    _brick_spire(surf, cx, shoulder_y, body_base_y, hw_cap, hw_base, palette)

    # Sparse corbel string-courses banding the shaft (1-3 total).
    body_h = body_base_y - shoulder_y
    n_band = max(0, min(3, body_h // 52))
    for k in range(n_band):
        ht = (k + 1) / (n_band + 1)
        y = int(shoulder_y + body_h * (1 - ht))
        hw = int(round(hw_cap + (hw_base - hw_cap) * (1 - ht)))
        _songyue_dwarf_eave(surf, cx, y, hw, palette, depth=2)
        _tile_hatch(surf, cx - hw + 3, y - 1, cx + hw - 3, y - 1,
                    _mortar(palette), step=5)

    # Low shrine doorway on the shaft — a lit niche that warms at night.
    if body_h > 26 and hw_base > 12:
        door_w = min(7, max(3, hw_base // 2))
        door_h = min(15, body_h // 3)
        _lit_niche(surf, cx, body_base_y - door_h - 2, door_w, door_h, palette)

    # Corbel neck carries the centreline from the slim shoulder to the staff.
    neck_h = max(4, int(crown_h * 0.18))
    _corbel_neck(surf, cx, shoulder_y, shoulder_y - neck_h, hw_cap, palette)

    # ── The gilded phoenix crown (pure gutter overhang; centre on cx) ────────
    if have_bird:
        # Body centre placed so the BEAK APEX (r*1.5 above centre) clears the
        # gap rim by ~3 px and the tail meets the staff foot — the head-lobe
        # carries the centreline to the rim.
        py = top_y + int(r * _PHOENIX_TOP_REACH) + 3
        staff_base_y = py + int(r * 0.5)
        staff_top_y = shoulder_y - neck_h
        _vane_staff(surf, cx, min(staff_top_y, staff_base_y), staff_base_y,
                    palette)
        if _is_dark_sky(palette):
            # Night halo BEHIND the bird so only the outer glow rings show.
            _gilt_halo(surf, cx, py, r, palette)
            draw_spiral_glow(surf, cx, py, radius=max(8, int(r * 0.7)))
        _phoenix(surf, cx, py, r, palette, sun=-1.0)
    else:
        # Short section: finial-staff only; spire fills the column beneath.
        _vane_staff(surf, cx, top_y + 2, shoulder_y - neck_h, palette)

    if decor:
        draw_grass_bed(surf, cx, base_y - 1, pw0 + 6, 14, palette, seed=seed)
        draw_side_shrub(surf, cx - (hw_base + 4), base_y - 1, palette, scale=0.8)
        draw_side_shrub(surf, cx + (hw_base + 4), base_y - 1, palette, scale=0.7)


def candidate_phoenix_vane_mill(surf, top_rect, bot_rect, palette, seed):
    bcx = bot_rect.x + bot_rect.width // 2
    tcx = top_rect.x + top_rect.width // 2

    if bot_rect.height > 22:
        _draw_one(surf, bcx, bot_rect.bottom, bot_rect.y,
                  bot_rect.width, palette, seed, decor=True)

    if top_rect.height > 22:
        # Structural mirror: draw upright into a temp sized to top_rect.height,
        # flip vertically, hang from the ceiling. The frontal spread-winged
        # phoenix is bilaterally symmetric and vertically balanced, so the flip
        # leaves a still-legible phoenix at the gap rim on the hung twin.
        w = surf.get_width()
        tmp = pygame.Surface((w, top_rect.height), pygame.SRCALPHA)
        _draw_one(tmp, tcx, top_rect.height, 0,
                  top_rect.width, palette, seed, decor=False)
        flipped = pygame.transform.flip(tmp, False, True)
        surf.blit(flipped, (0, top_rect.y))


# ── Review harness ───────────────────────────────────────────────────────────

MARGIN = 70
CACHE_W = PIPE_W + MARGIN * 2
PHASE_DAY = 0.30
PHASE_NIGHT = 0.85
SEED = 12

GAP_Y, GAP_H = 205, 150
TOP_H = int(GAP_Y - GAP_H / 2)
BOT_TOP = int(GAP_Y + GAP_H / 2)
CROP_TOP, CROP_BOT = 14, 496


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
    candidate_phoenix_vane_mill(surf, top_rect, bot_rect, pal, SEED)
    return surf


def _render_pair(pal):
    surf = _pair_surf(pal)
    cell = _sky_ground(CACHE_W, GROUND_Y, pal, 60)
    cell.blit(surf, (0, 0))
    guide = (255, 90, 90)
    for rim in (TOP_H, BOT_TOP):
        for x in range(0, CACHE_W, 8):
            pygame.draw.line(cell, guide, (x, rim), (x + 4, rim), 1)
    return cell.subsurface(pygame.Rect(0, CROP_TOP, CACHE_W,
                                       CROP_BOT - CROP_TOP)).copy()


def _measure_centreline(pal):
    """Mirrored-centreline coverage: on the top (hung) section, how close does
    the crown centreline reach the gap rim (TOP_H)? Returns px gap between the
    lowest filled pixel at x=cx in the top section and the rim (0 = touches)."""
    surf = _pair_surf(pal)
    cx = MARGIN + PIPE_W // 2
    low = -1
    for y in range(0, TOP_H + 2):
        if surf.get_at((cx, y))[3] > 50:
            low = y
    return TOP_H - low if low >= 0 else TOP_H


def _measure_fill(pal, section_h):
    """Max vertical run (px) of ZERO-fill rows inside the PIPE_W collision
    column for a bottom-only section of the given height."""
    surf = pygame.Surface((CACHE_W, GROUND_Y), pygame.SRCALPHA)
    bot_rect = pygame.Rect(MARGIN, GROUND_Y - section_h, PIPE_W, section_h)
    candidate_phoenix_vane_mill(surf, pygame.Rect(MARGIN, 0, PIPE_W, 0),
                                bot_rect, pal, SEED)
    cx = MARGIN + PIPE_W // 2
    x0, x1 = cx - PIPE_W // 2, cx + PIPE_W // 2
    run = worst = 0
    for y in range(GROUND_Y - section_h, GROUND_Y):
        filled = any(surf.get_at((x, y))[3] > 50 for x in range(x0, x1 + 1))
        run = 0 if filled else run + 1
        worst = max(worst, run)
    return worst


def _measure_phoenix_symmetry(pal):
    """Flip-safety probe: render the DAY phoenix crown region and report
    (a) left/right mirror match and (b) how balanced the mass is above vs below
    its own mid-line — the two properties that keep the medallion legible after
    the vertical flip. Returns (lr_match_pct, top_frac, bot_frac)."""
    surf = _pair_surf(pal)
    cx = MARGIN + PIPE_W // 2
    # Isolate gilt/vermilion (warm, non-brick) pixels in the crown band.
    ys = [y for y in range(BOT_TOP, BOT_TOP + 90)]
    pts = []
    for y in ys:
        for x in range(cx - 55, cx + 55):
            c = surf.get_at((x, y))
            if c[3] > 60 and c[0] > 120 and c[0] >= c[2] + 25:
                pts.append((x, y))
    if not pts:
        return 0.0, 0.0, 0.0
    xs = [p[0] for p in pts]
    yy = [p[1] for p in pts]
    y_mid = (min(yy) + max(yy)) / 2
    top = sum(1 for _, y in pts if y < y_mid)
    bot = sum(1 for _, y in pts if y >= y_mid)
    n = len(pts)
    pset = set(pts)
    matched = sum(1 for x, y in pts if (2 * cx - x, y) in pset)
    return 100.0 * matched / n, top / n, bot / n


def _render_feas(pal, section_h):
    head = 16
    cell_h = section_h + head + 10
    surf = pygame.Surface((CACHE_W, GROUND_Y), pygame.SRCALPHA)
    bot_rect = pygame.Rect(MARGIN, GROUND_Y - section_h, PIPE_W, section_h)
    candidate_phoenix_vane_mill(surf, pygame.Rect(MARGIN, 0, PIPE_W, 0),
                                bot_rect, pal, SEED)
    cell = _sky_ground(CACHE_W, cell_h, pal, 10)
    crop_top = GROUND_Y - section_h - head
    cell.blit(surf, (0, 0), pygame.Rect(0, crop_top, CACHE_W, cell_h))
    cx = MARGIN + PIPE_W // 2
    for ex in (cx - PIPE_W // 2, cx + PIPE_W // 2):
        pygame.draw.line(cell, (255, 60, 60), (ex, 0), (ex, cell_h), 1)
    return cell, cell_h


def _render_blackout(pal, section_h=235):
    surf = pygame.Surface((CACHE_W, GROUND_Y), pygame.SRCALPHA)
    bot_rect = pygame.Rect(MARGIN, GROUND_Y - section_h, PIPE_W, section_h)
    candidate_phoenix_vane_mill(surf, pygame.Rect(MARGIN, 0, PIPE_W, 0),
                                bot_rect, pal, SEED)
    crop_top = GROUND_Y - section_h - 12
    crop = surf.subsurface(pygame.Rect(0, crop_top, CACHE_W, section_h + 12)).copy()
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
    cl_day = _measure_centreline(day)
    cl_night = _measure_centreline(night)
    sym_lr, sym_top, sym_bot = _measure_phoenix_symmetry(day)

    heights = [70, 210, 355]
    feas = [_render_feas(day, h) for h in heights]
    fills = {h: _measure_fill(day, h) for h in heights}
    blackout = _render_blackout(day)

    pad = 14
    label_h = 22
    title_h = 62
    pw, ph = pair_day.get_width(), pair_day.get_height()

    title = pygame.font.SysFont(None, 30)
    sub = pygame.font.SysFont(None, 18)
    label = pygame.font.SysFont(None, 19)

    left_w = pad + pw + pad + pw + pad
    feas_w = max(c.get_width() for c, _ in feas)
    right_w = feas_w + pad * 2
    sheet_w = left_w + right_w

    bo_w, bo_h = blackout.get_width(), blackout.get_height()
    left_h = title_h + ph + label_h + pad + bo_h + label_h + pad
    feas_col_h = title_h + sum(ch + label_h + pad for _, ch in feas) + 24
    sheet_h = max(left_h, feas_col_h) + pad

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((24, 25, 30))

    sheet.blit(title.render("phoenix-vane-mill — round 2", True, (245, 240, 230)),
               (pad, 12))
    sheet.blit(sub.render("slender brick SPIRE + gilt PHOENIX vane  ·  head-lobe over "
                          "up-swept wings + single tail plume  ·  flip-safe  ·  night halo",
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
        cl2 = sub.render(f"mirror centreline gap to rim: {cl}px", True,
                         (200, 202, 212))
        sheet.blit(cl2, (hx + (pw - cl2.get_width()) // 2, hy + ph + 3 + 18))

    bx = pad
    by = title_h + ph + label_h + pad + 14
    sheet.blit(blackout, (bx, by))
    pygame.draw.rect(sheet, (60, 62, 72), (bx, by, bo_w, bo_h), 1)
    lab = label.render("BLACKOUT — 58px silhouette (bird: head-lobe over wings)",
                       True, (255, 224, 150))
    sheet.blit(lab, (bx, by + bo_h + 3))
    sy = by + bo_h + 3 + 20
    sheet.blit(sub.render(f"phoenix L/R mirror: {sym_lr:.0f}%   mass "
                          f"above/below mid-line: {sym_top*100:.0f}/"
                          f"{sym_bot*100:.0f}%  (flip-safe)",
                          True, (200, 202, 212)), (bx, sy))

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

    out = _REPO / "docs" / "pillar_landmarks" / "temple_mills" / "phoenix-vane-mill" / "round_2.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(sheet, out)
    print(f"wrote {out}  ({sheet.get_width()}x{sheet.get_height()})")
    print(f"mirror centreline->rim gap: day={cl_day}px night={cl_night}px")
    print(f"max empty run: " + "  ".join(f"{h}px->{fills[h]}px" for h in heights))
    print(f"phoenix L/R mirror match: {sym_lr:.1f}%   "
          f"mass above/below mid-line: {sym_top*100:.0f}%/{sym_bot*100:.0f}%")

    # PIL-sanity contract (no display): day and night pairs must differ, and the
    # night pair must carry the additive gilt halo (a warm glow the day lacks).
    dsum = sum(sum(pair_day.get_at((x, y))[:3])
               for y in range(0, ph, 7) for x in range(0, pw, 7))
    nsum = sum(sum(pair_night.get_at((x, y))[:3])
               for y in range(0, ph, 7) for x in range(0, pw, 7))
    print(f"day/night sample-sum: day={dsum} night={nsum} differ={dsum != nsum}")


if __name__ == "__main__":
    main()
