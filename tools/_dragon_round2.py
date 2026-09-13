"""Round-2 CONVERGENCE sheet for the NIGHT-FESTIVAL DRAGON DANCE near-lane performer.

Round 1 round-head versions read as a festive caterpillar at scrolling scale; only
the head-PROFILE + body-RHYTHM versions read as a DRAGON. This sheet converges on a
single synthesis — V2's PROFILE head + V3's BODY rhythm + V4's RED/GOLD colorway,
7 segments — and explores variations WITHIN it (head expressiveness, whisker length,
antler shape, dancer phasing, one jade alt skin).

The synthesis is built to a fixed dragon-read contract that survives shrinking:

  * HEAD PROFILE — antlered, snout LIFTED and pointing FORWARD into scroll (the snout
    is the forward-most pixel of the whole creature); ONE dominant 3/4 eye, never a
    frontal bug-eye pair; open mouth with a 1-2px lower-jaw depth.
  * WHISKERS — long TRAILING STREAMERS (8-12px) lagging behind the head on the wave,
    a 1px line with a 2px warm highlight tip, so they add motion not stubby antennae.
  * SNOUT-LIFT — the head sits 4-6px ABOVE the neck line so the body reads as a
    rising serpent, not a flat horizontal log.
  * DORSAL SPINE — a CONTINUOUS low sawtooth ridge along the top (not per-segment
    triangles, which read as party hats when small).
  * COLOR — red/gold primary: bright gold belly discs, deep-red dorsal, a 1px darker
    OUTLINE so the silhouette holds on navy night AND day-biome terrain.
  * TAIL — taper to a point / single flame wisp; ONE flame locus only (the head).
  * DANCERS — distinct per-pole colors, each a readable 2-leg silhouette, leg phase
    staggered for marching life; never a merged dark mass.
  * GLOW — ember accents are 1-2px additive on head crest + whisker tips ONLY; no
    body-wide bloom; value raised with base color, capped under the coin.

Renders the synthesis on a night festival deck strip (braziers + dancers) AND a
60%-scale read-test strip so the dragon-vs-caterpillar read is verifiable.

Headless (SDL dummy) -> docs/foreground_redesign/dragon/round_2.png. Not shipped.
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


# ── the serpent spine (V3 body rhythm) ────────────────────────────────────────
#
# A single undulating sine spine sampled tail(left)->head(right). The head end
# RISES (head_rise) so the dragon reads as a climbing serpent; the body sags toward
# the tail. 2x oversampling keeps the back/belly discs overlapping into one ribbon.

def _spine(bx, ground_y, n, length, amp, t, *, head_rise=18, sag=22):
    pts = []
    span = max(1, (n - 1) * 2)
    for i in range(span + 1):
        tt = i / span
        x = bx - length // 2 + int(tt * length)
        # The travelling wave; amplitude eases UP toward the head so the front of
        # the serpent dances more than the dragged tail (V3's lively-front rhythm).
        wave = math.sin(t * 3.0 - tt * 5.6) * amp * (0.55 + 0.45 * tt)
        float_y = ground_y - sag - int(tt * head_rise)
        pts.append((x, int(float_y + wave)))
    return pts


# ── pole dancers — distinct per-pole colors, staggered march, 2 readable legs ──

def _pole_dancers(surf, pts, ground_y, pal, t, *, robes, leg_stagger=1.0):
    """Each real segment centre gets a dancer holding a pole up to the body. Distinct
    robe per pole (festival crowd energy), a clear 2-leg silhouette, and a leg phase
    staggered down the line so the crew reads as MARCHING, not a frozen rank."""
    night = _nightf(pal)
    j = 0
    for i, (px, py) in enumerate(pts):
        if i % 2:                       # dancers stand under REAL centres only
            continue
        robe = _retint(robes[j % len(robes)], night)
        robe_dk = _shade(robe, -36)
        sash = _cap_lum((232, 196, 96), pal)   # a gold sash so each pops off the deck
        skin = _retint((232, 192, 150), night)
        feet = ground_y
        # A per-dancer marching phase that walks down the line (leg_stagger spreads
        # it) so legs lift out of step — the marching-life cue.
        mph = t * 5.0 + (j * leg_stagger)
        bob = int(max(0.0, math.sin(mph)) * 2)
        body_y = feet - 14 + bob
        # Torso wedge + a thin gold sash band so it separates from neighbours.
        pygame.draw.polygon(surf, robe, [
            (px - 4, body_y), (px + 4, body_y), (px + 5, feet - 4), (px - 5, feet - 4)])
        pygame.draw.polygon(surf, robe_dk, [
            (px - 4, body_y), (px + 4, body_y), (px + 5, feet - 4), (px - 5, feet - 4)], 1)
        pygame.draw.line(surf, sash, (px - 4, body_y + 5), (px + 4, body_y + 5), 1)
        pygame.draw.circle(surf, skin, (px, body_y - 4), 3)
        pygame.draw.arc(surf, robe_dk, (px - 3, body_y - 8, 7, 7),
                        math.radians(0), math.radians(180), 2)
        # TWO legs, each lifting on opposite halves of the march phase so a stride
        # reads. Drawn as distinct 2px shins so the silhouette never merges.
        for dx, ph in ((-2, 0.0), (2, math.pi)):
            step = int(max(0.0, math.sin(mph + ph)) * 3)
            pygame.draw.line(surf, robe_dk, (px + dx, feet - 5),
                             (px + dx + (1 if step else -1), feet - step), 2)
        # The lifting arm + a pole up to the body it carries.
        lift = int(max(0.0, math.sin(t * 3.0 + i)) * 2)
        pygame.draw.line(surf, robe, (px, body_y + 1), (px - 2, body_y - 5 - lift), 2)
        pygame.draw.line(surf, _retint((120, 90, 56), night),
                         (px - 2, body_y - 5 - lift), (px, py + 5), 2)
        j += 1


# ── the serpent body: red/gold, gold belly discs, CONTINUOUS sawtooth dorsal ──

def _body(surf, pts, pal, *, kit):
    """Draw tail->head: a 1px darker OUTLINE sheath, the deep-red scaled back, a
    bright gold belly band, a CONTINUOUS low sawtooth dorsal ridge (not separate
    triangles), and a small per-plate bead. The outline holds the silhouette on
    both navy night and day terrain."""
    seg_r = 8
    scale = kit['scale']; scale_dk = kit['scale_dk']
    belly = kit['belly']; belly_dk = kit['belly_dk']; hi = kit['hi']
    outline = kit['outline']
    # The 1px darker outline sheath (a hair wider than the body) — drawn first so it
    # rims the whole ribbon and the silhouette reads against any background.
    for (x, y) in pts:
        pygame.draw.circle(surf, outline, (x, y), seg_r + 1)
    for (x, y) in pts:
        pygame.draw.circle(surf, scale, (x, y), seg_r)
    # Bright GOLD belly discs along the lower arc — the casual-arcade pop + the
    # value lift (raise value with base color, no bloom).
    for (x, y) in pts:
        pygame.draw.circle(surf, belly_dk, (x, y + seg_r - 3), seg_r - 3)
        pygame.draw.circle(surf, belly, (x, y + seg_r - 3), seg_r - 4)
    # CONTINUOUS dorsal SAWTOOTH ridge: one zigzag polyline tracing the top edge of
    # the body tail->head, so it reads as a spine, never as detached party hats.
    top = []
    for i, (x, y) in enumerate(pts):
        top.append((x, y - seg_r))
    ridge = []
    for i in range(0, len(top) - 1):
        x0, y0 = top[i]
        x1, y1 = top[i + 1]
        ridge.append((x0, y0))
        if i % 2 == 0:                  # a low tooth peak between each pair
            ridge.append(((x0 + x1) // 2, (y0 + y1) // 2 - 4))
    ridge.append(top[-1])
    pygame.draw.lines(surf, kit['ridge_dk'], False, ridge, 2)
    pygame.draw.lines(surf, kit['ridge'], False, ridge, 1)
    # A small lit plate bead on each real centre for internal value range.
    for i in range(0, len(pts), 2):
        x, y = pts[i]
        pygame.draw.circle(surf, hi, (x - 2, y - 1), 1)


def _tail(surf, pt, nxt, pal, *, kit, t):
    """Taper to a single point with ONE small trailing wisp — no second flame locus
    (the head holds the only flame). A thin pointed fin that sways with the dance."""
    x, y = pt
    sway = int(math.sin(t * 3.0) * 3)
    # Point the taper away from the body (back/left), following the spine direction.
    dx = x - nxt[0]; dy = y - nxt[1]
    tip = (x + (dx if dx else -10), y + dy + sway)
    pygame.draw.polygon(surf, kit['outline'], [
        (x, y - 6), (x, y + 6), tip])
    pygame.draw.polygon(surf, kit['scale'], [
        (x, y - 5), (x, y + 5), (tip[0] + 1, tip[1])])
    # A single small wisp curl off the tip — a thread, not a flame.
    pygame.draw.line(surf, kit['ridge'], (tip[0], tip[1]),
                     (tip[0] - 4, tip[1] - 3 + sway), 1)


# ── the HEAD (V2 PROFILE, locked archetype) ───────────────────────────────────
#
# A right-facing PROFILE head: forehead/brow, antlers swept BACK over the neck, a
# snout that LIFTS and points forward (its tip is the forward-most pixel), one
# dominant 3/4 eye, an open mouth with a 1-2px lower jaw. Knobs vary expressiveness
# (mouth open amount), antler shape, and whisker length per candidate.

def _head_profile(surf, pt, pal, t, kit, *, mouth='open', antler='branched',
                  whisk_len=11, lift=5):
    hx, hy = pt
    # SNOUT-LIFT: raise the whole head above the neck join so the body rises into it.
    hy -= lift
    bob = int(max(0.0, math.sin(t * 3.2)) * 2)
    hy -= bob
    face = kit['face']; face_dk = kit['face_dk']
    horn = kit['horn']; horn_dk = kit['horn_dk']
    gold = kit['gold']; red = kit['red']; outline = kit['outline']

    # Whiskers — long TRAILING streamers rooted at the SNOUT TIP that arc UP-FORWARD
    # then lag back over the body, so they read as flowing motion lines, not stubs.
    # Drawn after the head so they sit on top of the snout cleanly.

    # A short scalloped neck-mane behind the head (back/left) so the head ties into
    # the body rather than floating — kept low/continuous, not spiky triangles.
    for k, ang in enumerate(range(120, 241, 20)):
        rad = math.radians(ang)
        mx = hx + int(math.cos(rad) * 11)
        my = hy + int(math.sin(rad) * 11)
        c = (gold, red)[k % 2]
        pygame.draw.circle(surf, _shade(c, -26), (mx, my), 3)
        pygame.draw.circle(surf, c, (mx, my), 2)

    # The PROFILE skull: a domed brow at the back, then a LONGER snout that TAPERS
    # FORWARD and lifts UP to a pointed tip — the forward-most pixel of the creature,
    # so the head reads unmistakably as a dragon's, not a bug's round front.
    snout_tip_x = hx + 18
    skull = [
        (hx - 9, hy - 7),               # back-top of skull
        (hx + 3, hy - 8),               # brow ridge
        (hx + 9, hy - 6),               # bridge of snout (steps up)
        (snout_tip_x, hy - 4),          # LIFTED pointed snout tip (forward-most)
        (snout_tip_x - 2, hy + 1),      # snout underside
        (hx + 9, hy + 3),              # upper-lip corner
        (hx - 8, hy + 6),               # jaw hinge / cheek
    ]
    pygame.draw.polygon(surf, outline, [(p[0], p[1]) for p in skull])
    pygame.draw.polygon(surf, face_dk, [(p[0], p[1]) for p in skull])
    pygame.draw.polygon(surf, face, [
        (hx - 8, hy - 6), (hx + 3, hy - 7), (hx + 8, hy - 5),
        (snout_tip_x - 1, hy - 3), (snout_tip_x - 3, hy), (hx + 8, hy + 2),
        (hx - 7, hy + 4)])
    # Brow ridge — a darker band over the eye for the carved profile read.
    pygame.draw.line(surf, face_dk, (hx - 6, hy - 5), (hx + 6, hy - 5), 2)

    # ANTLERS swept BACK over the neck (back/left), gold + dark base. Shape varies.
    _antlers(surf, hx, hy, kit, shape=antler)

    # ONE dominant 3/4 eye, set forward under the brow. A second, much smaller far-
    # eye hint sits deeper so the read is profile (one big eye), not frontal bug.
    ex, ey = hx + 3, hy - 1
    pygame.draw.circle(surf, outline, (ex, ey), 3)
    pygame.draw.circle(surf, kit['eye'], (ex, ey), 2)
    pygame.draw.circle(surf, (24, 18, 22), (ex + 1, ey), 1)
    pygame.draw.circle(surf, _shade(kit['eye'], -40), (hx - 2, hy - 2), 1)  # far-eye hint

    # The OPEN MOUTH with a 1-2px lower jaw. Expressiveness varies: 'closed' = a
    # near-shut line, 'open' = a modest gape, 'roar' = a wide drop-jaw.
    if mouth == 'closed':
        jaw = 1
    elif mouth == 'roar':
        jaw = 3 + int(max(0.0, math.sin(t * 3.2 + 0.4)) * 3)
    else:
        jaw = 2 + int(max(0.0, math.sin(t * 3.2 + 0.4)) * 2)
    mouth_x0, mouth_x1 = hx + 9, snout_tip_x - 2
    # Dark mouth cavity between upper lip and the dropped lower jaw.
    pygame.draw.polygon(surf, (22, 14, 18), [
        (mouth_x0, hy + 2), (mouth_x1, hy + 1),
        (mouth_x1 - 1, hy + 2 + jaw), (mouth_x0, hy + 3 + jaw)])
    pygame.draw.line(surf, red, (mouth_x0, hy + 2), (mouth_x1, hy + 1), 1)
    pygame.draw.line(surf, kit['jaw'], (mouth_x0, hy + 3 + jaw),
                     (mouth_x1 - 1, hy + 2 + jaw), 1)   # lower-jaw lip (1-2px depth)
    if mouth != 'closed':
        # A single ivory fang at the upper lip — one is enough in profile.
        fx = hx + 11
        pygame.draw.polygon(surf, kit['fang'], [
            (fx - 1, hy + 2), (fx + 1, hy + 2), (fx, hy + 5)])
    # A red nostril nub at the snout tip.
    pygame.draw.circle(surf, red, (snout_tip_x - 3, hy), 1)

    # The trailing whisker streamers, rooted at the lifted snout tip.
    _whiskers(surf, snout_tip_x, hy, pal, t, kit, length=whisk_len)

    # GLOW: 1-2px additive ember on the crest + the brightest antler tip ONLY.
    _near_glow(surf, hx + 2, hy - 6, pal, radius=8, color=(255, 160, 100))


def _antlers(surf, hx, hy, kit, *, shape):
    horn = kit['horn']; horn_dk = kit['horn_dk']
    base_x, base_y = hx + 1, hy - 6
    if shape == 'branched':
        # A classic deer-style branched antler swept back.
        pygame.draw.line(surf, horn_dk, (base_x, base_y), (base_x - 7, base_y - 11), 3)
        pygame.draw.line(surf, horn, (base_x, base_y), (base_x - 7, base_y - 11), 2)
        pygame.draw.line(surf, horn, (base_x - 3, base_y - 5), (base_x - 9, base_y - 7), 2)
        pygame.draw.line(surf, horn, (base_x - 5, base_y - 8), (base_x - 11, base_y - 10), 2)
    elif shape == 'tall':
        # Two tall swept-back prongs, regal.
        for off in (0, 3):
            pygame.draw.line(surf, horn_dk, (base_x - off, base_y),
                             (base_x - off - 4, base_y - 14), 3)
            pygame.draw.line(surf, horn, (base_x - off, base_y),
                             (base_x - off - 4, base_y - 14), 2)
    else:  # 'curl' — a stubbier curled ram-style horn
        pygame.draw.line(surf, horn_dk, (base_x, base_y), (base_x - 6, base_y - 7), 3)
        pygame.draw.line(surf, horn, (base_x, base_y), (base_x - 6, base_y - 7), 2)
        pygame.draw.circle(surf, horn, (base_x - 7, base_y - 8), 2)
    # A bright ember tip on the back prong (the one allowed crest glow source).
    pygame.draw.circle(surf, kit['gold'], (base_x - 7, base_y - 11), 1)


def _whiskers(surf, sx, sy, pal, t, kit, *, length=11):
    """Two long TRAILING streamers rooted at the snout tip (sx, sy). Each arcs a touch
    FORWARD/UP off the snout then sweeps BACK over the body, lagging the wave so it
    reads as a flowing motion line. 1px line with a 2px warm highlight tip — the
    second (after the head crest) of the two allowed glow accents."""
    drift = math.sin(t * 2.2) * 3
    whisk = kit['whisk']; tip = kit['whisk_tip']
    # Upper streamer kicks up off the snout; lower streamer drifts down — both then
    # trail BACK (toward -x) over the body, the classic dragon-dance ribbon read.
    for base_dy, kick in ((-1, -4), (3, 1)):
        pts = [(sx, sy + base_dy)]
        # First a short forward/up flick off the snout tip...
        pts.append((sx + 2, sy + base_dy + kick + int(drift)))
        # ...then a long sweep BACK over the head/body, sagging as it trails.
        for s in range(1, 5):
            frac = s / 4.0
            wx = sx + 2 - int(frac * length)
            wy = sy + base_dy + kick + int(frac * 6) + int(math.sin(t * 2.2 + s) * 2 + drift)
            pts.append((wx, wy))
        pygame.draw.lines(surf, whisk, False, pts, 1)
        pygame.draw.circle(surf, tip, pts[-1], 1)     # 2px warm streaming tip
        _near_glow(surf, pts[-1][0], pts[-1][1], pal, radius=5, color=(255, 170, 110))


# ── colour kits (red/gold primary; one jade alt) ──────────────────────────────

def kit_red_gold(pal):
    return dict(
        scale=_cap_lum((196, 58, 50), pal), scale_dk=_cap_lum((140, 38, 36), pal),
        outline=_cap_lum((96, 24, 26), pal),
        belly=_cap_lum((238, 198, 92), pal), belly_dk=_cap_lum((196, 150, 60), pal),
        hi=_cap_lum((250, 170, 110), pal),
        ridge=_cap_lum((236, 196, 90), pal), ridge_dk=_cap_lum((150, 46, 42), pal),
        face=_cap_lum((228, 206, 168), pal), face_dk=_cap_lum((172, 146, 116), pal),
        horn=_cap_lum((238, 202, 96), pal), horn_dk=_cap_lum((176, 138, 56), pal),
        gold=_cap_lum((240, 206, 110), pal), red=_cap_lum((214, 70, 58), pal),
        eye=_cap_lum((250, 196, 70), pal),
        jaw=fl._lip_ivory(pal), fang=fl._fang_ivory(pal),
        whisk=_cap_lum((232, 188, 110), pal), whisk_tip=_cap_lum((252, 210, 130), pal))


def kit_jade(pal):
    return dict(
        scale=_cap_lum((54, 146, 104), pal), scale_dk=_cap_lum((36, 100, 74), pal),
        outline=_cap_lum((22, 64, 50), pal),
        belly=_cap_lum((236, 200, 98), pal), belly_dk=_cap_lum((190, 152, 64), pal),
        hi=_cap_lum((170, 224, 160), pal),
        ridge=_cap_lum((236, 196, 92), pal), ridge_dk=_cap_lum((30, 88, 64), pal),
        face=_cap_lum((222, 210, 174), pal), face_dk=_cap_lum((164, 152, 122), pal),
        horn=_cap_lum((238, 202, 96), pal), horn_dk=_cap_lum((176, 138, 56), pal),
        gold=_cap_lum((240, 206, 110), pal), red=_cap_lum((214, 86, 66), pal),
        eye=_cap_lum((250, 196, 70), pal),
        jaw=fl._lip_ivory(pal), fang=fl._fang_ivory(pal),
        whisk=_cap_lum((220, 206, 120), pal), whisk_tip=_cap_lum((246, 224, 140), pal))


# ── the SYNTHESIS dragon (one assembly; candidates vary its knobs) ────────────

def dragon(surf, bx, ground_y, pal, t, *, kit_fn, mouth='open', antler='branched',
           whisk_len=11, robes, leg_stagger=1.0, lift=5):
    kit = kit_fn(pal)
    pts = _spine(bx, ground_y, 7, 156, amp=10, t=t)   # 7 segments, V3 rhythm
    _pole_dancers(surf, pts, ground_y, pal, t, robes=robes, leg_stagger=leg_stagger)
    _tail(surf, pts[0], pts[1], pal, kit=kit, t=t)
    _body(surf, pts, pal, kit=kit)
    _head_profile(surf, pts[-1], pal, t, kit, mouth=mouth, antler=antler,
                  whisk_len=whisk_len, lift=lift)


# Distinct festival robe palettes for the dancer crew (crowd energy).
_ROBES_A = [(170, 60, 60), (90, 70, 150), (60, 130, 110), (190, 130, 50)]
_ROBES_B = [(60, 110, 160), (180, 70, 120), (70, 140, 90), (200, 150, 60)]


def v1(surf, bx, gy, pal, t):
    # Calmer head (modest open mouth), BRANCHED antlers, mid whiskers, gentle march.
    dragon(surf, bx, gy, pal, t, kit_fn=kit_red_gold, mouth='open',
           antler='branched', whisk_len=10, robes=_ROBES_A, leg_stagger=0.8)


def v2(surf, bx, gy, pal, t):
    # ROARING head (wide drop-jaw), TALL regal antlers, LONG trailing whiskers, a
    # strongly staggered march — the most feral, dynamic read.
    dragon(surf, bx, gy, pal, t, kit_fn=kit_red_gold, mouth='roar',
           antler='tall', whisk_len=12, robes=_ROBES_B, leg_stagger=1.4, lift=6)


def v3(surf, bx, gy, pal, t):
    # CALM closed-ish mouth, CURLED ram horns, short tidy whiskers — a dignified,
    # composed temple dragon; tight in-step march.
    dragon(surf, bx, gy, pal, t, kit_fn=kit_red_gold, mouth='closed',
           antler='curl', whisk_len=9, robes=_ROBES_A, leg_stagger=0.5, lift=4)


def v4(surf, bx, gy, pal, t):
    # Open mouth, BRANCHED antlers, the LONGEST streaming whiskers, big leg stagger
    # — leans hardest into the trailing-motion cue.
    dragon(surf, bx, gy, pal, t, kit_fn=kit_red_gold, mouth='open',
           antler='branched', whisk_len=12, robes=_ROBES_B, leg_stagger=1.6, lift=6)


def v5(surf, bx, gy, pal, t):
    # JADE/gold ALT skin (same profile + rhythm), roaring head, tall antlers — shows
    # the synthesis holds on the secondary colorway.
    dragon(surf, bx, gy, pal, t, kit_fn=kit_jade, mouth='roar',
           antler='tall', whisk_len=11, robes=_ROBES_A, leg_stagger=1.0, lift=5)


VERSIONS = [
    ("V1  red/gold · calm-open · branched antler · mid whisker", v1),
    ("V2  red/gold · ROAR · tall antler · long whisker", v2),
    ("V3  red/gold · calm-closed · curled horn · tidy whisker", v3),
    ("V4  red/gold · open · branched · LONGEST streamers", v4),
    ("V5  JADE alt · roar · tall antler (same profile+rhythm)", v5),
]


def _deck(surf, x, y, w, h, pal):
    night = _nightf(pal)
    top = _mix(pal.get('ground_top', (49, 71, 92)), (30, 36, 60), 0.3 * night)
    mid = _mix(pal.get('ground_mid', (27, 46, 67)), (18, 24, 44), 0.3 * night)
    pygame.draw.rect(surf, mid, (x, y, w, h))
    pygame.draw.rect(surf, top, (x, y, w, 6))
    pygame.draw.line(surf, _shade(top, 16), (x, y), (x + w, y), 1)


def _braziers(surf, deck_y, w, pal, t):
    for gx in (44, w - 44):
        pygame.draw.ellipse(surf, _cap_lum((150, 78, 46), pal), (gx - 4, deck_y - 4, 8, 4))
        _near_glow(surf, gx, deck_y - 3, pal, radius=9, color=(255, 150, 90))


def build():
    biome_pal = biome.palette_for_phase(0.70)         # deep night
    rows = 5
    tile_w, tile_h = 360, 116
    read_h = 150                                       # the 60%-scale read-test strip
    pad_top = 26
    sheet_w = tile_w
    sheet_h = pad_top + rows * tile_h + read_h
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((10, 12, 26))

    font = pygame.font.SysFont("dejavusans", 13, bold=True)
    sub = pygame.font.SysFont("dejavusans", 9, bold=True)
    title = font.render("DRAGON DANCE — convergence · round 2", True, (235, 220, 180))
    sheet.blit(title, (10, 6))

    t = 1.15
    for i, (label, fn) in enumerate(VERSIONS):
        ty = pad_top + i * tile_h
        tile = pygame.Surface((tile_w, tile_h))
        for yy in range(tile_h):
            f = yy / tile_h
            tile.fill(_mix((12, 14, 45), (28, 30, 58), f), (0, yy, tile_w, 1))
        deck_y = tile_h - 24
        _deck(tile, 0, deck_y, tile_w, 24, biome_pal)
        _braziers(tile, deck_y, tile_w, biome_pal, t)
        fn(tile, tile_w // 2, deck_y, biome_pal, t)
        sheet.blit(tile, (0, ty))
        pygame.draw.rect(sheet, (0, 0, 0), (0, ty, tile_w, 13))
        sheet.blit(sub.render(label, True, (240, 226, 170)), (5, ty + 2))

    # ── 60%-scale READ-TEST strip: each dragon shrunk to true scrolling size so the
    # dragon-vs-caterpillar read is verifiable side by side on a night deck.
    ry = pad_top + rows * tile_h
    rtile = pygame.Surface((tile_w, read_h))
    for yy in range(read_h):
        rtile.fill(_mix((10, 12, 40), (24, 26, 52), yy / read_h), (0, yy, tile_w, 1))
    deck_y = read_h - 22
    _deck(rtile, 0, deck_y, tile_w, 22, biome_pal)
    # Render each dragon onto a scratch tile and scale to 60% (NEAREST keeps pixels
    # crisp), lined up across the strip so the small-size read is directly testable.
    # 0.60 is the true near-lane shrink the art-director asked to verify; the cells
    # overlap-pack the five so the small heads sit side by side for direct compare.
    scale = 0.60
    cell = tile_w // rows
    for i, (_label, fn) in enumerate(VERSIONS):
        scratch = pygame.Surface((cell + 80, 110), pygame.SRCALPHA)
        sdeck = 96
        fn(scratch, (cell + 80) // 2, sdeck, biome_pal, t)
        sw = int((cell + 80) * scale); sh = int(110 * scale)
        small = pygame.transform.scale(scratch, (sw, sh))
        cx = i * cell + cell // 2
        feet_in = int(sdeck * scale)
        rtile.blit(small, (cx - sw // 2, deck_y - feet_in))
    _braziers(rtile, deck_y, tile_w, biome_pal, t)
    sheet.blit(rtile, (0, ry))
    pygame.draw.rect(sheet, (0, 0, 0), (0, ry, tile_w, 13))
    sheet.blit(sub.render("60% READ-TEST — true scrolling size (dragon, not caterpillar?)",
                          True, (250, 210, 150)), (5, ry + 2))

    out = "/home/user/skybit/docs/foreground_redesign/dragon/round_2.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("saved", out, sheet.get_size())


if __name__ == "__main__":
    build()
