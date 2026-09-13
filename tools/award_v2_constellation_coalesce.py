"""Award interstitial concept `constellation-coalesce` — a single premium 360x640
still that IMPLIES the inward snap of a drifting starfield into Pip's badge.

Scratch tooling only; nothing here is imported by the game. `game/` is untouched.
The still is frozen NEAR-RESOLVED (~90% coalesced): the gold medallion has
materialised to near-full brightness and is the single brightest, highest-
contrast object in the frame — the hero. The constellation rim is almost
complete and trails IN behind the badge (rim/inbound stars are kept dimmer
than the hero so the hierarchy reads hero-first), only a narrow lower-right
wedge is still open with its last stars STREAKING inward, and the "snap"
shockwave ring is still expanding — so the transform reads in one frozen
frame as "just landing", not "half-built". The assembly is deliberately
off-centre so it can't collapse into a plain centred-medal read.
"""
import os
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import sys
import math
import random

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import pygame
if not pygame.get_init():
    pygame.init()

from tools.unlock_notice_common import demo_ids
from game import achievements as ach
from game.achievement_icons import draw_badge
from game.draw import blit_glow, get_glow, make_gradient_surface, lerp_color
from game.hud import (_font, _outlined_text,
                      _GOLD_BRIGHT, _GOLD_PALE, _GOLD_DEEP, _PANEL_DARK,
                      _PANEL_LIGHTER, _NIGHT_DEEP)
from game.config import W, H

ids = demo_ids(2)
a0 = ach.BY_ID[ids[0]]            # hero badge: First Delivery (pillar glyph)


def _ease_out(t):
    return 1 - (1 - t) ** 3


def _additive_dot(surf, x, y, r, col, a):
    """A soft round star/spark blitted ADDITIVELY so overlaps bloom like light."""
    d = r * 2 + 4
    s = pygame.Surface((d, d), pygame.SRCALPHA)
    pygame.draw.circle(s, (*col, a), (d // 2, d // 2), r)
    if r >= 2:
        pygame.draw.circle(s, (255, 255, 255, min(255, a + 60)), (d // 2, d // 2),
                           max(1, r - 1))
    surf.blit(s, (x - d // 2, y - d // 2), special_flags=pygame.BLEND_ADD)


def _streak(surf, x0, y0, x1, y1, col, a, w):
    """A tapered motion-trail from the star's launch point to its current spot.
    Drawn additively in a few fading segments so the head is bright and the tail
    dissolves into the night — the cue that the star is FLYING, not parked."""
    segs = 8
    for i in range(segs):
        t0 = i / segs
        t1 = (i + 1) / segs
        # tail (t small) is dim, head (t large) is bright
        ax = x0 + (x1 - x0) * t0
        ay = y0 + (y1 - y0) * t0
        bx = x0 + (x1 - x0) * t1
        by = y0 + (y1 - y0) * t1
        seg_a = int(a * (t1 ** 2))
        if seg_a <= 0:
            continue
        d = 4
        line = pygame.Surface((W, H), pygame.SRCALPHA)
        pygame.draw.line(line, (*col, seg_a), (ax, ay), (bx, by),
                         max(1, int(w * t1)))
        surf.blit(line, (0, 0), special_flags=pygame.BLEND_ADD)


def _ring_shockwave(surf, cx, cy, radius, col, thickness, alpha):
    """A single expanding annulus marking the 'snap'. Built as a full ADD glow
    disc with its core punched out, so the leading edge blooms like the rest of
    the celestial light rather than reading as a hard UI ring."""
    R = radius + thickness + 8
    s = pygame.Surface((R * 2, R * 2), pygame.SRCALPHA)
    # bright thin band
    for i in range(thickness):
        t = i / max(1, thickness - 1)
        edge_a = int(alpha * (1 - abs(t - 0.5) * 2) ** 1.5)
        pygame.draw.circle(s, (*col, edge_a), (R, R), radius + i - thickness // 2,
                           2)
    surf.blit(s, (cx - R, cy - R), special_flags=pygame.BLEND_ADD)


# ── canvas: deep-night vertical gradient, the celestial stage ────────────────
surf = pygame.Surface((W, H))
sky = make_gradient_surface(W, H, [
    (0.0, (4, 2, 20)),           # near-black crown
    (0.30, _NIGHT_DEEP),
    (0.70, (16, 10, 46)),        # navy mid
    (1.0, (28, 16, 60)),         # warmer purple toward the horizon glow
])
surf.blit(sky, (0, 0))

# A faint warm updraft glow low-centre so the eye is pulled toward the assembly,
# and a cool zenith vignette so the corners stay quiet for the ghost constells.
glow_layer = pygame.Surface((W, H), pygame.SRCALPHA)
blit_glow(glow_layer, W // 2, int(H * 0.46), 230, (40, 30, 80), 70)
surf.blit(glow_layer, (0, 0))


# ── dense ambient starfield (the field BEFORE it has been recruited) ─────────
rng = random.Random(70714)
for _ in range(150):
    x = rng.randint(0, W)
    y = rng.randint(0, H)
    r = rng.choice([1, 1, 1, 2])
    a = rng.randint(28, 110)              # quiet field so the hero's contrast peaks
    _additive_dot(surf, x, y, r, (210, 220, 255), a)


# ── the hero assembly: off-centre so it never reads as a centred medallion ───
# Badge centre pushed up-left of dead-centre; the snap is happening here.
BCX, BCY = int(W * 0.40), int(H * 0.40)
BR = 78                                   # badge radius on screen
RING_OUTLINE = BR + 14                    # the sparkle-ring radius the stars trace

# Trace points: the constellation rim the stars are SNAPPING onto. Eight cardinal
# anchor stars (the locked sparkle-ring) plus intermediate seats so the outline
# reads as a near-complete circle of light. Formation is ~70% formed: the lower-
# right arc is still missing (those stars are the ones streaking in).
# The outline is a constellation arc, NOT a closed ring: the upper-left ~60% of
# the rim is locked, and a wide lower-right WEDGE is still open with its stars in
# flight. The asymmetry (open wedge + off-centre badge) is what stops the read
# collapsing into a centred medallion.
anchor_n = 30
seats = []
for i in range(anchor_n):
    ang = -math.pi / 2 + i * math.tau / anchor_n
    sx = BCX + math.cos(ang) * RING_OUTLINE
    sy = BCY + math.sin(ang) * RING_OUTLINE
    seats.append((ang, sx, sy))

# Open wedge centred on the lower-right (toward +45deg). NEAR-RESOLVED: the rim
# is ~90% complete, so the wedge is a NARROW lower-right notch — just enough of a
# break for the last inbound stars to still be streaming through it.
WEDGE_CENTER = math.radians(40)
WEDGE_HALF = math.radians(38)
locked = []
inbound = []
for ang, sx, sy in seats:
    da = abs(((ang - WEDGE_CENTER + math.pi) % math.tau) - math.pi)
    if da > WEDGE_HALF:
        locked.append((ang, sx, sy))
    else:
        inbound.append((ang, sx, sy))

# ── the HERO medallion, near-fully resolved INSIDE the forming rim ───────────
# NEAR-RESOLVED: the badge has materialised to near-full brightness so the real
# gold medallion is the single brightest, highest-contrast object in the frame —
# the hero the eye lands on first. The rim/inbound stars trail in BEHIND it.
# A bright warm halo + a tight resolved bloom seat it in its own light so it
# out-glows every star.
halo = pygame.Surface((W, H), pygame.SRCALPHA)
blit_glow(halo, BCX, BCY, int(BR * 1.35), (110, 84, 36), 70)    # contained warm seat
blit_glow(halo, BCX, BCY, int(BR * 1.05), (255, 206, 118), 95)   # tight resolved bloom
surf.blit(halo, (0, 0), special_flags=pygame.BLEND_ADD)

badge_layer = pygame.Surface((W, H), pygame.SRCALPHA)
draw_badge(badge_layer, a0.icon_key,
           pygame.Rect(BCX - BR, BCY - BR, BR * 2, BR * 2), unlocked=True)
badge_layer.set_alpha(246)               # near-fully resolved — the hero, full gold
surf.blit(badge_layer, (0, 0))
# a small gold specular glint on the medallion's upper-left rim crest — kept
# tight so it sharpens contrast without washing out the engraved glyph.
crest = pygame.Surface((W, H), pygame.SRCALPHA)
blit_glow(crest, int(BCX - BR * 0.66), int(BCY - BR * 0.66), int(BR * 0.30),
          (255, 240, 196), 60)
surf.blit(crest, (0, 0), special_flags=pygame.BLEND_ADD)


# ── GOLD constellation lines linking the LOCKED stars into the rim outline ───
# Only the formed arc is wired; the open wedge is left bare so the eye reads it
# as "not yet assembled".
line_layer = pygame.Surface((W, H), pygame.SRCALPHA)
locked_sorted = sorted(locked, key=lambda s: s[0])
for i in range(len(locked_sorted) - 1):
    a_ang, ax, ay = locked_sorted[i]
    b_ang, bx, by = locked_sorted[i + 1]
    # only wire adjacent seats — never bridge across the open wedge, so the gap
    # stays an obvious break in the constellation rather than a closed ring.
    if abs(((b_ang - a_ang + math.pi) % math.tau) - math.pi) > math.tau / anchor_n * 1.8:
        continue
    pygame.draw.aaline(line_layer, (*_GOLD_PALE, 130), (ax, ay), (bx, by))
surf.blit(line_layer, (0, 0))

# locked anchor stars: seated on the rim, but kept DIMMER than the hero badge —
# they are the supporting cast trailing in behind it, never out-glowing the gold.
for ang, sx, sy in locked:
    _additive_dot(surf, int(sx), int(sy), 2, _GOLD_BRIGHT, 150)
    blit_glow(surf, int(sx), int(sy), 5, (220, 178, 96), 55)


# ── STREAKING inbound stars: launched from far out, frozen most-of-the-way in ─
# Each inbound seat has a star caught ~80% along an eased arc toward its seat,
# trailing a motion-streak back toward where it came from. This is the whole
# point of the still — the field is still FLYING.
trail_rng = random.Random(91124)


def _arc_point(seat_ang, swirl, launch_dist, t):
    """Position along an eased inward arc toward a seat at `seat_ang`. The launch
    is offset tangentially (`swirl`) so the path is a sweeping curve, not a
    radial spoke — angle and radius both ease in together."""
    la = seat_ang + swirl
    cur_ang = la + (seat_ang - la) * t
    cur_dist = launch_dist + (RING_OUTLINE - launch_dist) * t
    return (BCX + math.cos(cur_ang) * cur_dist,
            BCY + math.sin(cur_ang) * cur_dist)


def _draw_inbound(seat_ang, prog, launch_mul, swirl, bright, head_r):
    launch_dist = RING_OUTLINE * launch_mul
    t = _ease_out(prog)
    cx, cy = _arc_point(seat_ang, swirl, launch_dist, t)
    # a multi-sample curved trail so the streak follows the ARC, not a straight
    # chord — the cue that the star swept inward.
    pts = []
    n = 7
    for k in range(n + 1):
        bt = max(0.0, t - 0.30) + (t - max(0.0, t - 0.30)) * (k / n)
        pts.append(_arc_point(seat_ang, swirl, launch_dist, bt))
    for k in range(n):
        seg_a = int(bright * ((k + 1) / n) ** 2)
        line = pygame.Surface((W, H), pygame.SRCALPHA)
        pygame.draw.line(line, (255, 224, 150, seg_a), pts[k], pts[k + 1],
                         max(1, int(3 * (k + 1) / n)))
        surf.blit(line, (0, 0), special_flags=pygame.BLEND_ADD)
    _additive_dot(surf, int(cx), int(cy), head_r, _GOLD_PALE, 175)
    blit_glow(surf, int(cx), int(cy), 5, (235, 198, 118), 75)


# the stars that will SEAT on the open wedge — each frozen most-of-the-way in.
# Kept dimmer than the hero: the streaks carry the MOTION, the badge carries the
# brightness, so the eye lands on the medallion first and reads the inflow second.
for ang, sx, sy in inbound:
    _draw_inbound(ang, trail_rng.uniform(0.74, 0.93),
                  trail_rng.uniform(2.8, 4.2), trail_rng.uniform(0.6, 1.2),
                  150, 2)

# extra anonymous field stars also pouring toward the wedge (denser inflow), so
# the inward SWARM still reads — but quietly, behind the resolved hero.
for _ in range(26):
    fa = WEDGE_CENTER + trail_rng.uniform(-WEDGE_HALF * 1.7, WEDGE_HALF * 1.7)
    _draw_inbound(fa, trail_rng.uniform(0.30, 0.72),
                  trail_rng.uniform(3.4, 5.2), trail_rng.uniform(0.7, 1.5),
                  105, 1)


# ── the SNAP shockwave: a single expanding ring at the moment of lock ────────
_ring_shockwave(surf, BCX, BCY, int(RING_OUTLINE * 1.34), (255, 236, 176), 5, 165)


# ── ghosted secondary constellation in a corner (the OTHER commendation) ─────
# One faint, fully-formed ring of dim stars lower-right — a previously earned
# commendation, present but quiet, establishing the multiplicity.
GCX, GCY, GR = int(W * 0.80), int(H * 0.78), 34
for i in range(12):
    ang = i * math.tau / 12
    sx = GCX + math.cos(ang) * GR
    sy = GCY + math.sin(ang) * GR
    _additive_dot(surf, int(sx), int(sy), 1, (180, 175, 210), 110)
ghost_line = pygame.Surface((W, H), pygame.SRCALPHA)
for i in range(12):
    ang = i * math.tau / 12
    nang = (i + 1) * math.tau / 12
    pygame.draw.aaline(ghost_line, (150, 140, 180, 55),
                       (GCX + math.cos(ang) * GR, GCY + math.sin(ang) * GR),
                       (GCX + math.cos(nang) * GR, GCY + math.sin(nang) * GR))
surf.blit(ghost_line, (0, 0))
# a tiny dormant pip of a badge inside it
gbadge = pygame.Surface((W, H), pygame.SRCALPHA)
draw_badge(gbadge, ach.BY_ID[ids[1]].icon_key,
           pygame.Rect(GCX - 22, GCY - 22, 44, 44), unlocked=True)
gbadge.set_alpha(55)
surf.blit(gbadge, (0, 0))


# ── kicker + title materialising below in starlight gold ─────────────────────
# A soft night-scrim under the text block so the title reads cleanly over the
# stray streaks pouring through the lower third (it never reads as a hard panel).
scrim = pygame.Surface((W, int(H * 0.34)), pygame.SRCALPHA)
for yy in range(scrim.get_height()):
    t = yy / max(1, scrim.get_height() - 1)
    a = int(150 * (0.25 + 0.75 * t))
    pygame.draw.line(scrim, (4, 2, 16, a), (0, yy), (W, yy))
surf.blit(scrim, (0, H - scrim.get_height()))

KY = int(H * 0.74)
_outlined_text(surf, "COMMENDATION EARNED", (W // 2, KY), 17,
               fill=_GOLD_PALE, outline=_PANEL_DARK, px=2, shadow_offset=None)
# faint star-dust underline beneath the kicker
for _ in range(26):
    kx = rng.randint(int(W * 0.18), int(W * 0.82))
    ky = KY + 13 + rng.randint(-2, 4)
    _additive_dot(surf, kx, ky, 1, (255, 235, 180), rng.randint(60, 160))

# the big title, glowing as if struck from starlight
title_glow = pygame.Surface((W, H), pygame.SRCALPHA)
blit_glow(title_glow, W // 2, int(H * 0.82), 120, (110, 80, 20), 80)
surf.blit(title_glow, (0, 0))
_outlined_text(surf, a0.title.upper(), (W // 2, int(H * 0.82)), 34,
               fill=_GOLD_BRIGHT, outline=(60, 36, 6), px=3,
               shadow_offset=(2, 4))


# ── faint TAP TO CONTINUE affordance at the very bottom ──────────────────────
tap_f = _font(13)
tap = tap_f.render("TAP TO CONTINUE", True, (200, 200, 220))
tap.set_alpha(120)
surf.blit(tap, tap.get_rect(center=(W // 2, H - 26)))


OUT = os.path.join(_ROOT, "docs", "achievements", "unlock_notice",
                   "award_interstitial_v2", "constellation-coalesce")
os.makedirs(OUT, exist_ok=True)
path = os.path.join(OUT, "round_2.png")
pygame.image.save(surf, path)
print(path)
