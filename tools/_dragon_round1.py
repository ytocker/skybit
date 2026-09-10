"""Round-1 exploration sheet for the NIGHT-FESTIVAL DRAGON DANCE near-lane performer.

Five distinct procedural dragons rendered on a night festival deck strip with a
couple of small pole-dancers for scale. Matches the foreground_near_lane idiom:
world-anchored head at near scale (~1.6 equivalent), sine-wave undulating
SEGMENTED body, capped ember/lantern glow so nothing rivals the coin/parrot.

Headless (SDL dummy) -> docs/foreground_redesign/dragon/round_1.png. Not shipped.
"""
from __future__ import annotations

import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

pygame.init()

from game import biome
from game import foreground_near_lane as fl
from game import foreground_props as sp

# Reuse the near-lane night contract so explorations look like the real game.
_cap_lum = fl._cap_lum
_near_glow = fl._near_glow
_is_dark = fl._is_dark
_nightf = fl._nightf
_mix = sp._mix
_shade = sp._shade

from game import foreground_promenade as pr
_retint = pr._retint_person


def _clamp(c):
    return max(0, min(255, int(c)))


# ── shared dragon scaffolding ─────────────────────────────────────────────────
#
# All five share the same skeleton: a sine-wave spine sampled left->right, the
# head at the FRONT (right), a tail fin at the BACK (left), a chain of rounded
# body segments between, and small pole-dancers stepping beneath. Per-version
# knobs change segment count, colourway, head style and dancer arrangement.

NEAR = 1.6  # the near-lane render scale the real performers sit at.


def _spine(bx, ground_y, n, length, amp, t, *, head_rise=14, sag=24):
    """Sample the undulating spine from tail (left) to head (right).

    Returns list of (x, y) centres. The body rides on poles held just above the
    dancers' heads (kept LOW so the costume reads as one ribbon, not balloons on
    sticks); the head end rises a touch and the wave travels along the body. Extra
    interpolated samples keep neighbouring segment discs overlapping for a smooth
    serpentine silhouette."""
    pts = []
    span = max(1, (n - 1) * 2)            # 2x sampling so discs overlap
    for i in range(span + 1):
        tt = i / span
        x = bx - length // 2 + int(tt * length)
        wave = math.sin(t * 3.0 - tt * 5.2) * amp
        float_y = ground_y - sag - int(tt * head_rise)
        pts.append((x, int(float_y + wave)))
    return pts


def _pole_dancers(surf, pts, ground_y, pal, t, *, every=1, robes=None):
    """Small dancers holding poles up to each (or every Nth) body segment. Each
    has a stepping gait + a thin pole reaching to the segment above. Kept short."""
    night = _nightf(pal)
    if robes is None:
        robes = [(150, 60, 55), (120, 90, 150), (70, 120, 90)]
    j = 0
    # The spine is sampled 2x for smooth overlap; dancers stand only under the
    # real segment centres (even indices), thinned further by `every`.
    for i, (px, py) in enumerate(pts):
        if i % 2:
            continue
        if (i // 2) % every:
            continue
        robe = _retint(robes[j % len(robes)], night)
        robe_dk = _shade(robe, -34)
        skin = _retint((232, 192, 150), night)
        j += 1
        feet = ground_y
        bob = int(max(0.0, math.sin(t * 4.0 + i)) * 2)
        body_y = feet - 13 + bob
        # Torso wedge.
        pygame.draw.polygon(surf, robe, [
            (px - 4, body_y), (px + 4, body_y),
            (px + 5, feet), (px - 5, feet)])
        pygame.draw.polygon(surf, robe_dk, [
            (px - 4, body_y), (px + 4, body_y),
            (px + 5, feet), (px - 5, feet)], 1)
        # Head.
        pygame.draw.circle(surf, skin, (px, body_y - 4), 3)
        # Stepping legs (lift-only gait).
        for dx, ph in ((-2, 0.0), (2, math.pi)):
            step = int(max(0.0, math.sin(t * 5.0 + i + ph)) * 3)
            pygame.draw.line(surf, robe_dk, (px + dx, feet - 4),
                             (px + dx + (1 if step else 0), feet - step), 2)
        # The lifting arm + pole reaching to the segment it carries.
        lift = int(max(0.0, math.sin(t * 3.0 + i)) * 2)
        pole_top = (px, py + 4)
        pygame.draw.line(surf, robe, (px, body_y + 2),
                         (px - 2, body_y - 5 - lift), 2)
        pygame.draw.line(surf, _retint((120, 90, 56), night),
                         (px - 2, body_y - 5 - lift), pole_top, 2)


def _belly_body(surf, pts, pal, *, scale_col, scale_dk, belly_col, hi_col,
                seg_r=8, finny=False):
    """Draw the segmented body: an outer dark sheath, the warm scale back, a
    contrasting belly band, a small per-segment highlight, and (optional) finned
    ridge plates along the spine. Drawn tail->head so the head overlaps."""
    # Continuous sheath/back as a fat polyline of overlapping discs gives the
    # smooth serpentine silhouette the silk costume reads as. Drawn over ALL
    # samples (incl. the 2x interpolated ones) so the ribbon has no gaps.
    for (x, y) in pts:
        pygame.draw.circle(surf, scale_dk, (x, y), seg_r + 1)
    for (x, y) in pts:
        pygame.draw.circle(surf, scale_col, (x, y), seg_r)
        # Contrasting belly band along the lower arc — a wide light underside that
        # separates the body from the dark night deck.
        pygame.draw.circle(surf, belly_col, (x, y + seg_r - 2), seg_r - 3)
    # Belly highlight + per-segment ridge bead only on the REAL segment centres
    # (even indices) so they read as discrete plates, not a smear.
    for i in range(0, len(pts), 2):
        x, y = pts[i]
        pygame.draw.circle(surf, hi_col, (x - 2, y - seg_r + 2), 2)
        pygame.draw.circle(surf, _shade(scale_dk, -14),
                           (x - seg_r + 1, y), 1)   # plate seam shadow
    if finny:
        # A dorsal ridge of small fin plates over each segment centre.
        for i in range(0, len(pts), 2):
            mx, my = pts[i][0], pts[i][1] - seg_r
            pygame.draw.polygon(surf, hi_col, [
                (mx - 3, my + 3), (mx + 3, my + 3), (mx, my - 4)])
            pygame.draw.polygon(surf, scale_dk, [
                (mx - 3, my + 3), (mx + 3, my + 3), (mx, my - 4)], 1)


def _tail_fin(surf, pt, pal, *, fin_col, fin_dk, t, flame=False):
    """A flared tail fin at the BACK (left) end — a fan of plates, optionally
    flame-shaped (curled wisps) for the imperial version."""
    x, y = pt
    sway = int(math.sin(t * 3.0) * 3)
    if flame:
        for k, ang in enumerate((-40, -10, 20)):
            rad = math.radians(ang)
            tx = x - 12 + int(math.cos(rad) * -4)
            ty = y + int(math.sin(rad) * 8) + sway
            pygame.draw.polygon(surf, fin_dk, [
                (x - 2, y - 4), (x - 2, y + 4), (tx - 4, ty)])
            pygame.draw.polygon(surf, fin_col, [
                (x - 2, y - 3), (x - 2, y + 3), (tx - 3, ty)])
    else:
        for dy in (-7, 0, 7):
            pygame.draw.polygon(surf, fin_dk, [
                (x, y - 3), (x, y + 3), (x - 13, y + dy + sway)])
            pygame.draw.polygon(surf, fin_col, [
                (x, y - 2), (x, y + 2), (x - 11, y + dy + sway)])


# ── dragon HEAD styles ────────────────────────────────────────────────────────
#
# Each takes the front spine point + a colour kit. All share the dragon-read
# checklist: horns/antlers, big eyes, open jaw + fangs, whiskers, a frilled mane.

def _head_common_whiskers(surf, hx, hy, pal, t, whisk_col, *, length=14):
    """Two long trailing whiskers off the snout, drifting with the dance."""
    drift = math.sin(t * 2.4) * 3
    for dy in (-1, 3):
        pts = [(hx + 9, hy + 2 + dy)]
        for s in range(1, 4):
            wx = hx + 9 + s * (length // 3)
            wy = hy + 2 + dy + int(math.sin(t * 2.4 + s) * 2 + drift)
            pts.append((wx, wy))
        pygame.draw.lines(surf, whisk_col, False, pts, 1)


def head_classic(surf, pt, pal, t, kit):
    """Classic lion-dragon head: broad ivory snout, gold antler-horns, red mane
    frill, big eyes, gaping fanged jaw. The festival workhorse silhouette."""
    hx, hy = pt
    hx += 8  # snout pushes forward of the last segment
    bob = int(max(0.0, math.sin(t * 3.2)) * 2)
    hy -= bob
    face = kit['face']; face_dk = kit['face_dk']
    horn = kit['horn']; horn_dk = kit['horn_dk']
    mane = kit['mane']; gold = kit['gold']; red = kit['red']
    # Mane frill ring behind the head.
    for k, ang in enumerate(range(-150, 151, 26)):
        rad = math.radians(ang)
        mx = hx + int(math.cos(rad) * 12)
        my = hy + int(math.sin(rad) * 12)
        c = (gold, mane, red)[k % 3]
        pygame.draw.polygon(surf, _shade(c, -28), [
            (mx - 3, my + 2), (mx + 3, my + 2),
            (mx + int(math.cos(rad) * 5), my + int(math.sin(rad) * 5))])
        pygame.draw.polygon(surf, c, [
            (mx - 2, my + 1), (mx + 2, my + 1),
            (mx + int(math.cos(rad) * 4), my + int(math.sin(rad) * 4))])
    # Skull.
    pygame.draw.ellipse(surf, face_dk, (hx - 11, hy - 9, 22, 19))
    pygame.draw.ellipse(surf, face, (hx - 10, hy - 8, 20, 16))
    # Antler-horns: branched gold prongs.
    for sgn in (-1, 1):
        bx = hx + sgn * 5
        pygame.draw.line(surf, horn_dk, (bx, hy - 6), (bx + sgn * 3, hy - 16), 3)
        pygame.draw.line(surf, horn, (bx, hy - 6), (bx + sgn * 3, hy - 16), 2)
        pygame.draw.line(surf, horn, (bx + sgn * 2, hy - 11),
                         (bx + sgn * 6, hy - 14), 2)
    # Big eyes.
    for ex in (-5, 5):
        pygame.draw.circle(surf, kit['eye_dk'], (hx + ex, hy - 2), 4)
        pygame.draw.circle(surf, kit['eye'], (hx + ex, hy - 2), 3)
        pygame.draw.circle(surf, (26, 20, 24), (hx + ex + 1, hy - 1), 1)
    # Gaping jaw + fangs + red lip.
    jaw = 3 + int(max(0.0, math.sin(t * 3.2 + 0.4)) * 3)
    pygame.draw.polygon(surf, (24, 16, 20), [
        (hx - 2, hy + 3), (hx + 11, hy + 3),
        (hx + 9, hy + 5 + jaw), (hx - 1, hy + 5 + jaw)])
    pygame.draw.line(surf, red, (hx - 2, hy + 3), (hx + 11, hy + 3), 2)
    for fx in (1, 8):
        pygame.draw.polygon(surf, kit['fang'], [
            (hx + fx - 1, hy + 3), (hx + fx + 1, hy + 3), (hx + fx, hy + 6)])
    pygame.draw.circle(surf, red, (hx + 9, hy + 1), 2)  # nostril nub
    _head_common_whiskers(surf, hx, hy, pal, t, kit['whisk'])
    _near_glow(surf, hx, hy, pal, radius=13, color=(255, 160, 100))


def head_antlered(surf, pt, pal, t, kit):
    """A taller, more REPTILIAN head: a longer snout, tall swept-back antlers, a
    spined crest instead of a round mane, narrow fierce eyes. Imperial read."""
    hx, hy = pt
    hx += 9
    bob = int(max(0.0, math.sin(t * 3.2)) * 2)
    hy -= bob
    face = kit['face']; face_dk = kit['face_dk']
    horn = kit['horn']; horn_dk = kit['horn_dk']; gold = kit['gold']; red = kit['red']
    # Spined crest fanning back over the neck.
    for k in range(5):
        cx = hx - 8 - k * 3
        ch = 9 - k
        pygame.draw.polygon(surf, _shade(gold, -30), [
            (cx - 2, hy - 4), (cx + 2, hy - 4), (cx, hy - 4 - ch)])
        pygame.draw.polygon(surf, gold, [
            (cx - 1, hy - 4), (cx + 1, hy - 4), (cx, hy - 3 - ch)])
    # Longer snout skull.
    pygame.draw.polygon(surf, face_dk, [
        (hx - 9, hy - 8), (hx + 6, hy - 7), (hx + 13, hy - 1),
        (hx + 13, hy + 4), (hx - 9, hy + 7)])
    pygame.draw.polygon(surf, face, [
        (hx - 8, hy - 7), (hx + 5, hy - 6), (hx + 11, hy - 1),
        (hx + 11, hy + 3), (hx - 8, hy + 5)])
    # Tall swept antlers.
    for sgn in (-1, 1):
        bx = hx + sgn * 4
        pygame.draw.line(surf, horn_dk, (bx, hy - 6), (bx - sgn * 2, hy - 18), 3)
        pygame.draw.line(surf, horn, (bx, hy - 6), (bx - sgn * 2, hy - 18), 2)
        pygame.draw.line(surf, horn, (bx - sgn * 1, hy - 12),
                         (bx - sgn * 5, hy - 16), 2)
        pygame.draw.line(surf, horn, (bx - sgn * 1, hy - 15),
                         (bx - sgn * 4, hy - 20), 2)
    # Narrow fierce eyes under a heavy gold brow.
    pygame.draw.line(surf, horn_dk, (hx - 6, hy - 5), (hx + 4, hy - 4), 2)
    for ex in (-3, 4):
        pygame.draw.circle(surf, kit['eye_dk'], (hx + ex, hy - 1), 3)
        pygame.draw.circle(surf, kit['eye'], (hx + ex, hy - 1), 2)
        pygame.draw.circle(surf, (24, 18, 22), (hx + ex, hy - 1), 1)
    # Long open jaw + fangs.
    jaw = 3 + int(max(0.0, math.sin(t * 3.2 + 0.4)) * 3)
    pygame.draw.polygon(surf, (22, 16, 20), [
        (hx + 2, hy + 3), (hx + 13, hy + 2),
        (hx + 11, hy + 4 + jaw), (hx + 1, hy + 5 + jaw)])
    pygame.draw.line(surf, red, (hx + 1, hy + 3), (hx + 13, hy + 2), 2)
    for fx in (4, 10):
        pygame.draw.polygon(surf, kit['fang'], [
            (hx + fx - 1, hy + 3), (hx + fx + 1, hy + 3), (hx + fx, hy + 6)])
    _head_common_whiskers(surf, hx + 2, hy, pal, t, kit['whisk'], length=16)
    _near_glow(surf, hx, hy, pal, radius=13, color=(255, 160, 100))


def head_round_jade(surf, pt, pal, t, kit):
    """A rounder, friendlier festival head: bushy round mane, stubby curled
    horns, huge googly eyes, a wide grin. Reads playful — fits Skybit casual."""
    hx, hy = pt
    hx += 8
    bob = int(max(0.0, math.sin(t * 3.2)) * 2)
    hy -= bob
    face = kit['face']; face_dk = kit['face_dk']
    horn = kit['horn']; gold = kit['gold']; red = kit['red']; mane = kit['mane']
    # Bushy round mane (overlapping puffs).
    for ang in range(0, 360, 40):
        rad = math.radians(ang)
        mx = hx + int(math.cos(rad) * 11)
        my = hy + int(math.sin(rad) * 11)
        c = (mane, gold, red)[(ang // 40) % 3]
        pygame.draw.circle(surf, _shade(c, -26), (mx, my), 4)
        pygame.draw.circle(surf, c, (mx, my), 3)
    pygame.draw.circle(surf, face_dk, (hx, hy), 11)
    pygame.draw.circle(surf, face, (hx, hy), 9)
    # Stubby curled horns.
    for sgn in (-1, 1):
        pygame.draw.circle(surf, horn, (hx + sgn * 6, hy - 8), 3)
        pygame.draw.circle(surf, _shade(horn, -30), (hx + sgn * 6, hy - 8), 3, 1)
    # Huge googly eyes.
    for ex in (-4, 5):
        pygame.draw.circle(surf, kit['eye'], (hx + ex, hy - 3), 4)
        pygame.draw.circle(surf, kit['eye_dk'], (hx + ex, hy - 3), 4, 1)
        pygame.draw.circle(surf, (26, 20, 24), (hx + ex + 1, hy - 2), 2)
    # Wide grin + fangs.
    jaw = 2 + int(max(0.0, math.sin(t * 3.2 + 0.4)) * 2)
    pygame.draw.arc(surf, red, (hx - 7, hy + 1, 15, 9 + jaw),
                    math.radians(200), math.radians(340), 3)
    pygame.draw.polygon(surf, (24, 16, 20), [
        (hx - 5, hy + 5), (hx + 6, hy + 5),
        (hx + 4, hy + 6 + jaw), (hx - 3, hy + 6 + jaw)])
    for fx in (-3, 4):
        pygame.draw.polygon(surf, kit['fang'], [
            (hx + fx - 1, hy + 5), (hx + fx + 1, hy + 5), (hx + fx, hy + 8)])
    pygame.draw.circle(surf, red, (hx, hy + 2), 2)
    _head_common_whiskers(surf, hx, hy, pal, t, kit['whisk'])
    _near_glow(surf, hx, hy, pal, radius=12, color=(255, 160, 100))


# ── colour kits (capped to night) ─────────────────────────────────────────────

def kit_red_gold(pal):
    return dict(
        scale=_cap_lum((200, 64, 52), pal), scale_dk=_cap_lum((140, 40, 38), pal),
        belly=_cap_lum((230, 196, 96), pal), hi=_cap_lum((240, 150, 90), pal),
        fin=_cap_lum((235, 190, 88), pal), fin_dk=_cap_lum((170, 130, 56), pal),
        face=_cap_lum((226, 206, 168), pal), face_dk=_cap_lum((176, 150, 120), pal),
        horn=_cap_lum((236, 200, 92), pal), horn_dk=_cap_lum((180, 142, 58), pal),
        mane=_cap_lum((210, 70, 60), pal), gold=_cap_lum((232, 192, 92), pal),
        red=_cap_lum((212, 72, 60), pal),
        eye=_cap_lum((150, 138, 112), pal), eye_dk=_shade(_cap_lum((150, 138, 112), pal), -50),
        fang=fl._fang_ivory(pal), whisk=_cap_lum((220, 180, 110), pal))


def kit_jade(pal):
    return dict(
        scale=_cap_lum((60, 150, 108), pal), scale_dk=_cap_lum((40, 104, 78), pal),
        belly=_cap_lum((228, 200, 110), pal), hi=_cap_lum((150, 220, 150), pal),
        fin=_cap_lum((232, 196, 96), pal), fin_dk=_cap_lum((168, 132, 60), pal),
        face=_cap_lum((220, 210, 176), pal), face_dk=_cap_lum((168, 156, 124), pal),
        horn=_cap_lum((236, 200, 92), pal), horn_dk=_cap_lum((180, 142, 58), pal),
        mane=_cap_lum((70, 160, 116), pal), gold=_cap_lum((234, 196, 94), pal),
        red=_cap_lum((212, 80, 64), pal),
        eye=_cap_lum((150, 138, 112), pal), eye_dk=_shade(_cap_lum((150, 138, 112), pal), -50),
        fang=fl._fang_ivory(pal), whisk=_cap_lum((210, 200, 120), pal))


def kit_imperial(pal):
    return dict(
        scale=_cap_lum((226, 178, 64), pal), scale_dk=_cap_lum((168, 124, 44), pal),
        belly=_cap_lum((234, 214, 150), pal), hi=_cap_lum((245, 220, 130), pal),
        fin=_cap_lum((212, 72, 56), pal), fin_dk=_cap_lum((150, 46, 40), pal),
        face=_cap_lum((228, 210, 168), pal), face_dk=_cap_lum((176, 152, 116), pal),
        horn=_cap_lum((232, 96, 70), pal), horn_dk=_cap_lum((168, 60, 48), pal),
        mane=_cap_lum((210, 72, 58), pal), gold=_cap_lum((238, 206, 110), pal),
        red=_cap_lum((214, 74, 58), pal),
        eye=_cap_lum((150, 138, 112), pal), eye_dk=_shade(_cap_lum((150, 138, 112), pal), -50),
        fang=fl._fang_ivory(pal), whisk=_cap_lum((232, 200, 120), pal))


# ── the five versions ─────────────────────────────────────────────────────────

def dragon(surf, bx, ground_y, pal, t, *, n, length, amp, kit_fn, head_fn,
           dancer_every=1, finny=True, flame_tail=False):
    kit = kit_fn(pal)
    pts = _spine(bx, ground_y, n, length, amp, t)
    # Dancers first (behind/under the body), then body, then head on top.
    _pole_dancers(surf, pts, ground_y, pal, t, every=dancer_every)
    _tail_fin(surf, pts[0], pal, fin_col=kit['fin'], fin_dk=kit['fin_dk'],
              t=t, flame=flame_tail)
    _belly_body(surf, pts, pal, scale_col=kit['scale'], scale_dk=kit['scale_dk'],
                belly_col=kit['belly'], hi_col=kit['hi'], seg_r=8, finny=finny)
    head_fn(surf, pts[-1], pal, t, kit)


def v1(surf, bx, gy, pal, t):
    # Classic red/gold, mid length (6 seg), classic lion-dragon head, a dancer
    # under every segment, finned dorsal ridge, fanned tail.
    dragon(surf, bx, gy, pal, t, n=6, length=128, amp=8,
           kit_fn=kit_red_gold, head_fn=head_classic, dancer_every=1, finny=True)


def v2(surf, bx, gy, pal, t):
    # Jade-green/gold, LONG (8 seg) sweeping body, reptilian antlered head,
    # dancers every other segment (sparser crew), strong undulation.
    dragon(surf, bx, gy, pal, t, n=8, length=176, amp=11,
           kit_fn=kit_jade, head_fn=head_antlered, dancer_every=2, finny=True)


def v3(surf, bx, gy, pal, t):
    # Imperial yellow/red, mid-long (7 seg), tall antlered head, flame tail,
    # dancer under every segment — the regal, ceremonial take.
    dragon(surf, bx, gy, pal, t, n=7, length=152, amp=9,
           kit_fn=kit_imperial, head_fn=head_antlered, dancer_every=1,
           finny=True, flame_tail=True)


def v4(surf, bx, gy, pal, t):
    # Classic red/gold, SHORT punchy (5 seg), round playful head, dancer under
    # every segment — the casual-arcade friendly read, crisp at small size.
    dragon(surf, bx, gy, pal, t, n=5, length=104, amp=7,
           kit_fn=kit_red_gold, head_fn=head_round_jade, dancer_every=1,
           finny=False)


def v5(surf, bx, gy, pal, t):
    # Jade-green/gold, mid length (6 seg), round playful head, flame tail,
    # dancers every other — a softer green festival variant.
    dragon(surf, bx, gy, pal, t, n=6, length=132, amp=9,
           kit_fn=kit_jade, head_fn=head_round_jade, dancer_every=2,
           finny=True, flame_tail=True)


VERSIONS = [
    ("V1  red/gold · 6seg · classic head", v1),
    ("V2  jade/gold · 8seg · antlered", v2),
    ("V3  imperial · 7seg · antler+flame", v3),
    ("V4  red/gold · 5seg · round head", v4),
    ("V5  jade/gold · 6seg · round+flame", v5),
]


def _deck(surf, x, y, w, h, pal):
    """A short night festival deck strip under the dragon — a paved band cooled to
    night with a warm lantern-lit edge, matching the near-lane floor read."""
    night = _nightf(pal)
    top = _mix(pal.get('ground_top', (49, 71, 92)), (30, 36, 60), 0.3 * night)
    mid = _mix(pal.get('ground_mid', (27, 46, 67)), (18, 24, 44), 0.3 * night)
    pygame.draw.rect(surf, mid, (x, y, w, h))
    pygame.draw.rect(surf, top, (x, y, w, 6))
    pygame.draw.line(surf, _shade(top, 16), (x, y), (x + w, y), 1)


def build():
    biome_pal = biome.palette_for_phase(0.70)  # deep night
    cols, rows = 1, 5
    tile_w, tile_h = 360, 132
    pad_top = 26
    sheet_w = tile_w
    sheet_h = pad_top + rows * tile_h
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((10, 12, 26))

    font = pygame.font.SysFont("dejavusans", 13, bold=True)
    sub = pygame.font.SysFont("dejavusans", 10)
    title = font.render("DRAGON DANCE — night festival · round 1", True, (235, 220, 180))
    sheet.blit(title, (10, 6))

    t = 1.15  # a frozen mid-dance pose (undulation + open jaw + step)
    for i, (label, fn) in enumerate(VERSIONS):
        ty = pad_top + i * tile_h
        tile = pygame.Surface((tile_w, tile_h))
        # Night sky gradient inside the tile so the capped glow reads.
        for yy in range(tile_h):
            f = yy / tile_h
            c = _mix((12, 14, 45), (28, 30, 58), f)
            pygame.draw.line(tile, c, (0, yy), (tile_w, yy))
        deck_y = tile_h - 26
        _deck(tile, 0, deck_y, tile_w, 26, biome_pal)
        # A couple of brazier glows on the deck for festival atmosphere + scale.
        for gx in (40, tile_w - 40):
            pygame.draw.ellipse(tile, _cap_lum((150, 78, 46), biome_pal),
                                (gx - 4, deck_y - 4, 8, 4))
            _near_glow(tile, gx, deck_y - 3, biome_pal, radius=9,
                       color=(255, 150, 90))
        fn(tile, tile_w // 2, deck_y, biome_pal, t)
        sheet.blit(tile, (0, ty))
        # Label bar.
        pygame.draw.rect(sheet, (0, 0, 0), (0, ty, tile_w, 14))
        sheet.blit(sub.render(label, True, (240, 226, 170)), (6, ty + 1))

    out = "/home/user/skybit/docs/foreground_redesign/dragon/round_1.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("saved", out, sheet.get_size())


if __name__ == "__main__":
    build()
