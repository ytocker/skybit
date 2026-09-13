"""Promenade STREET-ANIMALS variety — round 1 candidate-sheet generator.

Fourth family in the sidewalk variety overhaul (after the 50-strong adult
pedestrian pool, the kids/elders/vendors day-cast, and the food-market stalls).
Today the street ships ONE dog (ambient._RunningDog, ambled left via
foreground_promenade._draw_calm_dog) plus a passing bird flock. This sheet
explores the two NEW street-animal families so the deck reads ALIVE with varied
critters, modelled exactly on the shipped families: variety is DATA over ONE
shared drawer per family, registered as foreground_variants rows.

TWO groups, each a variety SET over a shared drawer:

  DOGS (6) — a shared dog drawer parameterised by body PROPORTION (leg length,
    body length, chest depth, head size) + TAIL shape + EAR shape + coat colour/
    markings. The breed read is carried by the OUTLINE (build/tail/ear/stance),
    NOT colour, because the far-lane downscale kills colour + interior detail
    first. Six silhouette-distinct looks:
      D1 lean tall HOUND      — long legs, deep narrow chest, long low tail, drop ears
      D2 short-legged DASH    — low corgi/dachshund build, long body, stub-up tail, big ears
      D3 fluffy curl SPITZ    — fox build, plumed tail curled over the back, prick ears
      D4 stocky SHIBA/AKITA   — compact thick build, tight curl tail, small prick ears
      D5 droopy HOUND-PUP     — medium build, very long drop ears, low gentle tail, soft
      D6 spotted MUTT         — rangy mongrel, patch markings, flag tail, one prick/one drop ear
    All amble facing LEFT (the scroll/travel direction) on the 2-frame gait idiom
    (legs alternate, body bob, tail sway) — shown across 2 frames.

  CRITTERS (5) — a shared small-critter drawer dispatched by `kind`, each with
    its own simple idle/peck/hop motion driven by t (shown over 2-3 frames):
      C1 CAT      — sitting upright, tail curled around the paws, tail-tip FLICK + ear swivel
      C2 HEN      — plump body, comb + wattle + tail fan, PECK down-up cycle
      C3 PIGEONS  — a little cluster of 3 ground pigeons pecking + the odd HOP (one airborne)
      C4 SPARROWS — a tighter cluster of 2-3 tiny sparrows, quick peck + hop, slimmer than pigeons
      C5 DUCK     — a waddling duck, flat bill + tail-tuft, side-to-side WADDLE + head bob

CONSTRAINTS mirrored from the shipped families:
- pure pygame.draw.* + Surface (SRCALPHA ok), pygbag-safe. No numpy/gfxdraw/PIL.
- TINY: dogs ~8-12px tall, critters ~4-8px. Authored at native size, drawn CRISP
  (nearest; no smoothscale). Variety in the OUTLINE.
- Night: cool toward (54,64,96), nothing self-lit, <=150 luma (ped_cast idiom).
- Scaled so a dog reads clearly smaller than an adult (PED_H=18) and a pigeon
  reads as a small ground bird, not a chick-sized blob.

Expressible as foreground_variants.Variant rows: palette + attrs (build/leg/tail/
ear/muzzle scalars+enums) + pose/accessory flags over the shared drawers.

Nothing here touches production game files; review-sheet generator only.
"""
from __future__ import annotations

import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((1, 1))


# ── shared colour helpers (lifted from foreground_props + ped_cast) ────────────

def _clamp(c):
    return max(0, min(255, int(c)))


def _mix(a, b, t):
    t = max(0.0, min(1.0, t))
    return (_clamp(a[0] + (b[0] - a[0]) * t),
            _clamp(a[1] + (b[1] - a[1]) * t),
            _clamp(a[2] + (b[2] - a[2]) * t))


def _shade(c, d):
    return (_clamp(c[0] + d), _clamp(c[1] + d), _clamp(c[2] + d))


def _retint(col, night):
    """Cool toward the night ground band — matches ped_cast._retint_person so the
    animals sit in the same value family as the retinted floor and human cast."""
    if night <= 0.05:
        return col
    return _mix(col, (54, 64, 96), min(0.55, 0.40 * night + 0.20))


def _luma(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


NIGHT_GLOW_CAP = 150


# ════════════════════════════════════════════════════════════════════════════
# DOGS — ONE shared drawer; the breed is the OUTLINE (proportion+tail+ear+stance)
# ════════════════════════════════════════════════════════════════════════════
#
# Authoring frame: feet on `base_y`, dog faces LEFT (the scroll direction). A
# 1.0-build dog stands DOG_H px at the shoulder; per-row scalars modulate the
# proportions. The body is a rounded capsule (chest fuller at the front/left),
# four legs on a 2-frame alternating gait, a neck+head wedge up front, ears, a
# muzzle, and a tail whose SHAPE is the strongest far-lane breed cue.
#
# attrs (the foreground_variants row, family 'dog'):
#   build   — overall mass scale (0.8 small .. 1.25 stocky)
#   leg     — leg length factor (0.5 short corgi .. 1.15 tall hound)
#   length  — body length factor (1.0 compact .. 1.45 long dachshund)
#   chest   — chest depth (0.85 narrow whippet .. 1.2 barrel)
#   head    — head size (0.85 fine .. 1.15 blocky)
#   tail    — 'low'|'flag'|'plume'|'curl'|'tightcurl'|'stub'  (shape enum)
#   ear     — 'drop'|'prick'|'bigprick'|'longdrop'|'split'    (shape enum)
#   muzzle  — 'long'|'med'|'short'  (snout length)
# palette roles: coat, coat_dk, belly, marks(optional patch colour)

DOG_H = 12      # shoulder height of a 1.0-build dog (px). ~2/3 of an adult (PED_H 18).


def draw_dog(surf, cx, base_y, v, night, t):
    P, A = v.palette, v.attrs
    pf = lambda c: _retint(c, night)
    coat = pf(P["coat"])
    coat_dk = pf(P.get("coat_dk", _shade(P["coat"], -40)))
    coat_lt = _shade(coat, 16)
    belly = pf(P.get("belly", _shade(P["coat"], 22)))
    marks = pf(P["marks"]) if "marks" in P else None
    nose_c = pf((40, 32, 30))

    build = A.get("build", 1.0)
    legf = A.get("leg", 1.0)
    lengthf = A.get("length", 1.0)
    chestf = A.get("chest", 1.0)
    headf = A.get("head", 1.0)
    fluffy = A.get("fluffy", False)
    tail = A.get("tail", "flag")
    ear = A.get("ear", "drop")
    muzzle = A.get("muzzle", "med")

    sh_h = max(8, int(DOG_H * build))                 # shoulder height (feet→back)
    leg_h = max(2, int(sh_h * 0.40 * legf))           # ground clearance
    body_h = max(5, int((sh_h - leg_h) * 0.92 * chestf))  # capsule thickness
    body_w = max(9, int(sh_h * 1.15 * lengthf))       # capsule length
    head_r = max(3, int(sh_h * 0.27 * headf))

    ground = int(base_y)
    # Dog faces LEFT: HEAD end is left (-x), TAIL end is right (+x).
    body_top0 = ground - leg_h - body_h
    body_left = cx - body_w // 2
    body_right = cx + body_w // 2
    body_cy0 = body_top0 + body_h // 2

    # 2-frame amble: legs swing in anti-phase, body bobs gently with the stride.
    gait = math.sin(t * 6.0)
    bob = int(round(abs(gait) * (sh_h * 0.05)))
    body_top = body_top0 - bob
    body_cy = body_cy0 - bob

    # ── LEGS (behind the body): front pair near the head end, rear near the tail.
    # Anti-phase swing reads as a walk at 2 frames; rear legs angle back slightly.
    leg_col = coat_dk
    paw = _shade(coat_dk, -16)
    fx_front = body_left + max(2, body_w // 5)
    fx_rear = body_right - max(2, body_w // 5)
    swing = gait * max(1.5, body_w * 0.11)
    lw = max(2, sh_h // 6)
    for fx, ph in ((fx_front, 1), (fx_rear, -1)):
        for off, s in ((0, ph), (2, -ph)):          # near + far leg, offset gait
            sw = swing * s
            top_y = body_cy + body_h // 5
            foot_x = int(fx + off + sw)
            pygame.draw.line(surf, leg_col, (fx + off, top_y), (foot_x, ground), lw)
            pygame.draw.line(surf, paw, (foot_x - 1, ground), (foot_x + 1, ground), lw)

    # ── TAIL (the strongest far-lane breed cue) at the RIGHT/rear end ──
    tx = body_right - 1
    sway = int(round(gait * 1.4))
    tcol = coat
    tw = max(2, sh_h // 5)
    if tail == "low":                 # hound: long sabre sweep down-and-back
        pygame.draw.lines(surf, tcol, False, [
            (tx - 1, body_cy), (tx + int(sh_h * 0.5), body_cy + int(sh_h * 0.15)),
            (tx + int(sh_h * 0.7), body_cy + int(sh_h * 0.45) + sway)], tw)
        pygame.draw.lines(surf, coat_dk, False, [
            (tx - 1, body_cy), (tx + int(sh_h * 0.5), body_cy + int(sh_h * 0.15)),
            (tx + int(sh_h * 0.7), body_cy + int(sh_h * 0.45) + sway)], 1)
    elif tail == "flag":              # rangy mutt: raised plume waving behind+up
        pygame.draw.lines(surf, tcol, False, [
            (tx - 1, body_cy - 1), (tx + int(sh_h * 0.4), body_top - 1),
            (tx + int(sh_h * 0.55) + sway, body_top - int(sh_h * 0.45) - sway)], tw)
    elif tail == "plume":             # spitz: thick plume sweeping UP and arching back
        ax, ay = tx - 1, body_cy
        pygame.draw.lines(surf, tcol, False, [
            (ax, ay), (ax + int(sh_h * 0.45), body_top - int(sh_h * 0.1)),
            (ax + int(sh_h * 0.3), body_top - int(sh_h * 0.55)),
            (ax - int(sh_h * 0.1) + sway, body_top - int(sh_h * 0.75))],
            max(3, sh_h // 4))
        pygame.draw.lines(surf, coat_lt, False, [
            (ax + int(sh_h * 0.45), body_top - int(sh_h * 0.1)),
            (ax + int(sh_h * 0.3), body_top - int(sh_h * 0.55))], 1)
    elif tail == "curl":              # loose ring curl arcing over the rump
        cxr, cyr = tx, body_top
        pygame.draw.arc(surf, tcol, (cxr - sh_h // 2, cyr - sh_h // 2, sh_h, sh_h),
                        math.radians(-30), math.radians(220), max(3, sh_h // 4))
    elif tail == "tightcurl":         # shiba/akita: tight C-ring curl flat on the back
        cxr, cyr = tx - 1, body_top - 1
        rr = max(2, int(sh_h * 0.26))
        # draw the ring as a thick arc that doesn't quite close (the curl read)
        pygame.draw.arc(surf, tcol, (cxr - rr, cyr - rr, rr * 2, rr * 2),
                        math.radians(-60), math.radians(250), max(2, sh_h // 5))
        pygame.draw.arc(surf, coat_lt, (cxr - rr, cyr - rr, rr * 2, rr * 2),
                        math.radians(20), math.radians(160), 1)
    elif tail == "stub":              # corgi/dachshund: short stub angled up
        pygame.draw.line(surf, tcol, (tx - 1, body_cy),
                         (tx + 2 + sway, body_top - 1), max(2, sh_h // 4))

    # ── BODY CAPSULE (deep rounded loaf) ──
    body_rect = pygame.Rect(body_left, body_top, body_w, body_h)
    pygame.draw.ellipse(surf, coat, body_rect)
    pygame.draw.ellipse(surf, coat_dk, body_rect, 1)
    pygame.draw.arc(surf, belly, body_rect, math.radians(200), math.radians(340), 1)
    pygame.draw.arc(surf, coat_lt, body_rect, math.radians(35), math.radians(145), 1)
    # fluffy builds get a fuller, slightly bumpy back + a chest ruff
    if fluffy:
        for bxp in range(body_left + 2, body_right - 1, 2):
            pygame.draw.circle(surf, coat_lt, (bxp, body_top + 1), 1)

    # ── PATCH MARKINGS (mutt/spotted) — broken patches over the coat ──
    if marks is not None:
        pygame.draw.ellipse(surf, marks,
                            (body_left + int(body_w * 0.46), body_top + 1,
                             int(body_w * 0.38), body_h - 2))
        pygame.draw.circle(surf, marks, (body_left + 2, body_cy), max(1, body_h // 3))

    # ── NECK + HEAD up front (left). Head sits forward of, and above, the chest.
    hx = body_left - max(1, int(head_r * 0.3))
    hy = body_top + max(1, int(body_h * 0.1)) - max(1, int(sh_h * 0.18))
    # thick neck wedge filling the gap so head joins the chest cleanly (no step)
    pygame.draw.polygon(surf, coat, [
        (body_left + head_r, body_top), (body_left + 1, body_top + body_h - 1),
        (hx, hy + head_r), (hx - 1, hy - head_r // 2)])
    if fluffy:      # spitz/akita chest ruff — a fuller collar where neck meets chest
        pygame.draw.circle(surf, coat_lt, (body_left + 1, body_cy), max(2, head_r - 1))
    pygame.draw.circle(surf, coat, (hx, hy), head_r)
    pygame.draw.circle(surf, coat_dk, (hx, hy), head_r, 1)

    # ── MUZZLE (snout) poking forward-left ──
    if muzzle == "long":
        mlen = int(head_r * 1.4); mh = max(2, head_r - 1)
    elif muzzle == "short":
        mlen = max(2, int(head_r * 0.6)); mh = max(2, head_r)
    else:
        mlen = max(3, int(head_r * 1.0)); mh = max(2, head_r - 1)
    mx = hx - head_r // 2 - mlen
    pygame.draw.polygon(surf, coat, [
        (hx - head_r // 3, hy - mh // 2), (mx, hy - 1),
        (mx, hy + 1), (hx - head_r // 3, hy + mh // 2 + 1)])
    pygame.draw.circle(surf, nose_c, (mx, hy), 1)               # nose (single px)
    pygame.draw.circle(surf, (28, 22, 20), (hx - head_r // 3, hy - head_r // 3), 1)  # eye

    # ── EARS (the second strongest breed cue) ──
    if ear == "prick":                # erect triangle on the crown
        pygame.draw.polygon(surf, coat_dk, [
            (hx + 1, hy - head_r), (hx + head_r + 1, hy - head_r - 2),
            (hx + head_r, hy - head_r // 3)])
    elif ear == "bigprick":           # tall oversized bat-ear
        pygame.draw.polygon(surf, coat_dk, [
            (hx, hy - head_r), (hx + head_r, hy - int(head_r * 2.2)),
            (hx + head_r + 1, hy - head_r // 3)])
        pygame.draw.polygon(surf, _mix(coat, belly, 0.5), [
            (hx + 1, hy - head_r), (hx + head_r - 1, hy - int(head_r * 1.7)),
            (hx + head_r, hy - head_r // 2)])
    elif ear == "drop":               # folded flap hanging at the cheek
        pygame.draw.polygon(surf, coat_dk, [
            (hx + head_r // 2, hy - head_r + 1), (hx + head_r + 1, hy - head_r // 2),
            (hx + head_r - 1, hy + head_r)])
    elif ear == "longdrop":           # very long hound flap below the jaw
        pygame.draw.polygon(surf, coat_dk, [
            (hx + head_r // 2, hy - head_r + 1), (hx + head_r + 1, hy - head_r // 2),
            (hx + head_r, hy + int(head_r * 2.2)), (hx + head_r // 2, hy + head_r)])
        pygame.draw.polygon(surf, _shade(coat_dk, -14), [
            (hx + head_r // 2, hy - head_r + 1), (hx + head_r + 1, hy - head_r // 2),
            (hx + head_r, hy + int(head_r * 2.2)), (hx + head_r // 2, hy + head_r)], 1)
    elif ear == "split":              # one prick + one back-flat (the mongrel cue)
        pygame.draw.polygon(surf, coat_dk, [
            (hx + 1, hy - head_r), (hx + head_r + 1, hy - head_r - 2),
            (hx + head_r, hy - head_r // 3)])                  # prick (near)
        pygame.draw.polygon(surf, _shade(coat_dk, -10), [
            (hx + head_r // 2, hy - head_r + 1), (hx + head_r + 1, hy - head_r // 3),
            (hx + head_r - 1, hy + head_r)])                   # drop (far)


# ════════════════════════════════════════════════════════════════════════════
# CRITTERS — ONE shared drawer dispatched by `kind`; each its own t-motion.
# Authored feet-on-base_y, facing LEFT, TINY (~4-8px).
# ════════════════════════════════════════════════════════════════════════════
#
# attrs (foreground_variants rows, family 'critter'):
#   kind  — 'cat'|'hen'|'pigeons'|'sparrows'|'duck'
#   plus per-kind palette roles (body/body_dk/accent/...).

def draw_critter(surf, cx, base_y, v, night, t):
    kind = v.attrs.get("kind", "hen")
    {"cat": _crit_cat, "hen": _crit_hen, "pigeons": _crit_pigeons,
     "sparrows": _crit_sparrows, "duck": _crit_duck}[kind](surf, cx, base_y, v, night, t)


def _crit_cat(surf, cx, base_y, v, night, t):
    """A sitting cat, upright, tail curled around the front paws. Motion: a slow
    tail-tip FLICK + an occasional ear swivel — the universal idle-cat read."""
    pf = lambda c: _retint(c, night)
    P = v.palette
    fur = pf(P.get("body", (120, 112, 104)))
    fur_dk = pf(P.get("body_dk", _shade(P["body"], -34)))
    fur_lt = _shade(fur, 18)
    ear_in = pf(P.get("accent", (150, 110, 110)))
    g = int(base_y)
    # haunch + upright torso as one tall teardrop (sitting cat silhouette)
    body_h = 7
    body = pygame.Rect(cx - 3, g - body_h, 6, body_h)
    pygame.draw.ellipse(surf, fur, body)
    pygame.draw.ellipse(surf, fur_dk, body, 1)
    # seated haunch bulge at the base
    pygame.draw.ellipse(surf, fur, (cx - 4, g - 3, 8, 3))
    # head as a small circle on top, two triangular prick ears + swivel
    hx, hy = cx - 1, g - body_h - 1
    pygame.draw.circle(surf, fur, (hx, hy), 3)
    pygame.draw.circle(surf, fur_dk, (hx, hy), 3, 1)
    swiv = int(round(math.sin(t * 1.3) * 1))
    for ex in (-2, 2):
        pygame.draw.polygon(surf, fur, [
            (hx + ex, hy - 1), (hx + ex + (1 if ex < 0 else -1), hy - 4 + (swiv if ex > 0 else 0)),
            (hx + ex + (2 if ex < 0 else -2), hy - 1)])
        pygame.draw.line(surf, ear_in, (hx + ex, hy - 1),
                         (hx + ex + (1 if ex < 0 else -1), hy - 3), 1)
    # eyes (face left) + muzzle dot
    pygame.draw.circle(surf, (40, 70, 50), (hx - 1, hy), 1)
    pygame.draw.circle(surf, fur_lt, (hx - 2, hy + 1), 1)
    # TAIL curled forward around the right of the paws, tip FLICKS with t
    flick = int(round(math.sin(t * 2.2) * 2))
    pygame.draw.lines(surf, fur, False, [
        (cx + 3, g - 1), (cx + 5, g - 2), (cx + 5, g - 5),
        (cx + 3 + flick, g - 6 - max(0, flick))], 2)
    pygame.draw.circle(surf, fur_dk, (cx + 3 + flick, g - 6 - max(0, flick)), 1)


def _crit_hen(surf, cx, base_y, v, night, t):
    """A plump hen: round body, small head with COMB + WATTLE, an up-cocked tail
    fan, short legs. Motion: a PECK cycle — head dips to the ground and back up."""
    pf = lambda c: _retint(c, night)
    P = v.palette
    body = pf(P.get("body", (200, 188, 170)))
    body_dk = pf(P.get("body_dk", _shade(P["body"], -38)))
    body_lt = _shade(body, 16)
    comb = pf(P.get("accent", (176, 70, 60)))      # comb + wattle (muted red, capped)
    beak = pf((196, 158, 80))
    leg = pf((176, 140, 88))
    g = int(base_y)
    # peck phase: 0 standing .. 1 head at ground
    peck = max(0.0, math.sin(t * 3.2))
    # plump oval body
    bw, bh = 8, 6
    by = g - bh - 1
    pygame.draw.ellipse(surf, body, (cx - bw // 2, by, bw, bh))
    pygame.draw.ellipse(surf, body_dk, (cx - bw // 2, by, bw, bh), 1)
    pygame.draw.arc(surf, body_lt, (cx - bw // 2, by, bw, bh),
                    math.radians(40), math.radians(150), 1)
    # up-cocked tail fan at the rear (right)
    pygame.draw.polygon(surf, body_dk, [
        (cx + bw // 2 - 1, by + 1), (cx + bw // 2 + 3, by - 3),
        (cx + bw // 2 + 2, by + 2)])
    pygame.draw.polygon(surf, body, [
        (cx + bw // 2 - 1, by + 1), (cx + bw // 2 + 2, by - 1),
        (cx + bw // 2, by + 3)])
    # legs
    for lx in (cx - 1, cx + 2):
        pygame.draw.line(surf, leg, (lx, by + bh - 1), (lx, g), 1)
        pygame.draw.line(surf, leg, (lx - 1, g), (lx + 1, g), 1)
    # NECK + HEAD that dips on the peck. Head at front (left).
    hx0, hy0 = cx - bw // 2, by                  # neck base
    hx = hx0 - 1 - int(peck * 1)
    hy = hy0 - 2 + int(peck * 5)                 # dips toward the ground
    pygame.draw.line(surf, body, (hx0, by + 1), (hx, hy), 2)
    pygame.draw.circle(surf, body, (hx, hy), 2)
    # comb (top) + wattle (under beak) — muted red, never a beacon
    pygame.draw.circle(surf, comb, (hx, hy - 2), 1)
    pygame.draw.circle(surf, comb, (hx - 1, hy + 1), 1)
    # beak (faces left)
    pygame.draw.polygon(surf, beak, [(hx - 2, hy), (hx - 4, hy), (hx - 2, hy + 1)])
    pygame.draw.circle(surf, (24, 18, 16), (hx - 1, hy - 1), 1)   # eye


def _crit_pigeons(surf, cx, base_y, v, night, t):
    """A small CLUSTER of 3 ground pigeons pecking + the odd HOP. A pigeon is a
    plump round-chested ground bird, clearly bigger than a sparrow. Motion: each
    pecks on its own phase; one HOPS (lifts off the deck) on a slow cycle."""
    pf = lambda c: _retint(c, night)
    P = v.palette
    body = pf(P.get("body", (140, 142, 152)))
    body_dk = pf(P.get("body_dk", _shade(P["body"], -34)))
    neck = pf(P.get("accent", (110, 120, 150)))     # faint blue-green nape sheen
    beak = pf((120, 110, 110))
    g = int(base_y)
    # three birds spread across the cluster; the middle one hops.
    specs = ((-6, 0.0, False), (1, 0.6, True), (7, 1.1, False))
    for dx, ph, hops in specs:
        bx = cx + dx
        peck = max(0.0, math.sin(t * 3.0 + ph * 6))
        hop = max(0.0, math.sin(t * 1.6 + ph * 6)) if hops else 0.0
        lift = int(hop * 4)
        gb = g - lift
        # plump body
        bw, bh = 6, 4
        by = gb - bh - 1
        pygame.draw.ellipse(surf, body, (bx - bw // 2, by, bw, bh))
        pygame.draw.ellipse(surf, body_dk, (bx - bw // 2, by, bw, bh), 1)
        # tail nub at rear
        pygame.draw.line(surf, body_dk, (bx + bw // 2 - 1, by + 1),
                         (bx + bw // 2 + 2, by + 2), 1)
        # legs (tucked when hopping)
        if lift <= 0:
            for lx in (bx - 1, bx + 1):
                pygame.draw.line(surf, beak, (lx, by + bh - 1), (lx, g), 1)
        # head + neck dip on the peck
        hx = bx - bw // 2 - int(peck * 1)
        hy = by - 1 + int(peck * 3)
        pygame.draw.line(surf, neck, (bx - bw // 2 + 1, by + 1), (hx, hy), 2)
        pygame.draw.circle(surf, body, (hx, hy), 2)
        pygame.draw.polygon(surf, beak, [(hx - 2, hy), (hx - 3, hy), (hx - 2, hy + 1)])
        pygame.draw.circle(surf, (24, 20, 22), (hx - 1, hy - 1), 1)
        # a couple of seed flecks on the deck the cluster pecks at
    for sx in (cx - 3, cx + 3, cx + 9):
        pygame.draw.circle(surf, pf((150, 130, 90)), (sx, g), 1)


def _crit_sparrows(surf, cx, base_y, v, night, t):
    """A tight cluster of 2-3 tiny sparrows — slimmer + smaller than the pigeons,
    quick peck + frequent HOP. The size + quicker hop is the read vs the pigeons."""
    pf = lambda c: _retint(c, night)
    P = v.palette
    body = pf(P.get("body", (150, 120, 84)))
    body_dk = pf(P.get("body_dk", _shade(P["body"], -36)))
    cap = pf(P.get("accent", (110, 80, 56)))         # brown cap/back
    beak = pf((90, 78, 64))
    g = int(base_y)
    specs = ((-4, 0.0), (2, 0.5), (6, 1.0))
    for dx, ph in specs:
        bx = cx + dx
        peck = max(0.0, math.sin(t * 4.2 + ph * 6))
        hop = max(0.0, math.sin(t * 2.6 + ph * 6))
        lift = int(hop * 3)
        gb = g - lift
        bw, bh = 4, 3
        by = gb - bh - 1
        pygame.draw.ellipse(surf, body, (bx - bw // 2, by, bw, bh))
        pygame.draw.ellipse(surf, body_dk, (bx - bw // 2, by, bw, bh), 1)
        pygame.draw.circle(surf, cap, (bx, by + 1), 1)         # brown cap
        # cocked tail (sparrows hold the tail up)
        pygame.draw.line(surf, body_dk, (bx + bw // 2 - 1, by),
                         (bx + bw // 2 + 1, by - 2), 1)
        if lift <= 0:
            pygame.draw.line(surf, beak, (bx, by + bh - 1), (bx, g), 1)
        hx = bx - bw // 2 - int(peck * 1)
        hy = by + int(peck * 2)
        pygame.draw.circle(surf, body, (hx, hy), 1)
        pygame.draw.circle(surf, (22, 18, 16), (hx, hy), 1, 0)
        pygame.draw.line(surf, beak, (hx - 1, hy), (hx - 2, hy), 1)


def _crit_duck(surf, cx, base_y, v, night, t):
    """A waddling duck — horizontal boat body, flat BILL, up-tucked tail tuft.
    Motion: side-to-side WADDLE (body rocks) + a gentle head bob. The flat bill +
    boat body + waddle separates it from the round pecking birds."""
    pf = lambda c: _retint(c, night)
    P = v.palette
    body = pf(P.get("body", (210, 204, 190)))
    body_dk = pf(P.get("body_dk", _shade(P["body"], -36)))
    body_lt = _shade(body, 16)
    head_c = pf(P.get("accent", (96, 120, 96)))      # muted mallard-green head
    bill = pf((196, 168, 90))
    foot = pf((200, 150, 80))
    g = int(base_y)
    waddle = math.sin(t * 3.4)
    rock = int(round(waddle * 1))
    bobh = int(round(math.sin(t * 3.4 + 1.2) * 1))
    # boat-shaped body, low and long
    bw, bh = 9, 4
    by = g - bh - 1
    pygame.draw.ellipse(surf, body, (cx - bw // 2, by, bw, bh))
    pygame.draw.ellipse(surf, body_dk, (cx - bw // 2, by, bw, bh), 1)
    pygame.draw.arc(surf, body_lt, (cx - bw // 2, by, bw, bh),
                    math.radians(30), math.radians(150), 1)
    # perky up-tucked tail tuft at the rear (right)
    pygame.draw.polygon(surf, body, [
        (cx + bw // 2 - 1, by + 1), (cx + bw // 2 + 2, by - 2),
        (cx + bw // 2, by + 2)])
    # waddling webbed feet
    for lx, phase in ((cx - 1, 0), (cx + 2, math.pi)):
        step = int(round(math.sin(t * 3.4 + phase) * 1))
        pygame.draw.line(surf, foot, (lx, by + bh - 1), (lx + step, g), 1)
        pygame.draw.line(surf, foot, (lx + step - 1, g), (lx + step + 1, g), 1)
    # upright neck + rounded head at the front (left), bobbing
    hx = cx - bw // 2 - 1 + rock
    hy = by - 3 + bobh
    pygame.draw.line(surf, head_c, (cx - bw // 2 + 1, by + 1), (hx, hy), 2)
    pygame.draw.circle(surf, head_c, (hx, hy), 2)
    # flat broad BILL pointing left
    pygame.draw.polygon(surf, bill, [(hx - 2, hy), (hx - 4, hy - 1),
                                     (hx - 4, hy + 1), (hx - 2, hy + 1)])
    pygame.draw.circle(surf, (22, 20, 18), (hx - 1, hy - 1), 1)


# ════════════════════════════════════════════════════════════════════════════
# THE POOLS — foreground_variants.Variant rows (data, not bespoke functions)
# ════════════════════════════════════════════════════════════════════════════

class _V:
    """Stand-in for foreground_variants.Variant (palette + pose/accessory/attrs)
    so the sheet can exercise exactly the row shape the production pools use."""
    def __init__(self, palette, *, pose=(), acc=(), attrs=None):
        self.palette = palette
        self.pose = frozenset(pose)
        self.accessory = frozenset(acc)
        self.attrs = dict(attrs or {})


DOGS = [
    ("D1 lean HOUND", _V(
        dict(coat=(176, 150, 110), coat_dk=(120, 98, 66), belly=(206, 188, 150)),
        attrs=dict(build=1.05, leg=1.15, length=1.30, chest=0.85, head=0.92,
                   tail="low", ear="drop", muzzle="long")),
     "build1.05 leg1.15 len1.30 chest0.85 | tail:low ear:drop muzzle:long | coat tan/sand"),
    ("D2 short-leg DASH", _V(
        dict(coat=(150, 102, 64), coat_dk=(104, 68, 42), belly=(196, 160, 110)),
        attrs=dict(build=0.95, leg=0.52, length=1.45, chest=1.05, head=1.0,
                   tail="stub", ear="bigprick", muzzle="med")),
     "build0.95 leg0.52 len1.45 | tail:stub ear:bigprick | corgi/dachshund low-long, chestnut"),
    ("D3 fluffy SPITZ", _V(
        dict(coat=(230, 224, 212), coat_dk=(172, 164, 150), belly=(246, 242, 234)),
        attrs=dict(build=0.96, leg=0.92, length=0.98, chest=1.12, head=1.05,
                   fluffy=True, tail="plume", ear="prick", muzzle="med")),
     "build0.96 chest1.12 fluffy | tail:plume(sweep up+back) ear:prick + chest ruff | cream/white"),
    ("D4 stocky SHIBA", _V(
        dict(coat=(196, 130, 74), coat_dk=(140, 86, 46), belly=(228, 206, 172)),
        attrs=dict(build=1.18, leg=0.82, length=1.0, chest=1.16, head=1.10,
                   fluffy=True, tail="tightcurl", ear="prick", muzzle="short")),
     "build1.18 chest1.16 fluffy | tail:tightcurl(C-ring) ear:prick muzzle:short | rust shiba/akita"),
    ("D5 droopy PUP", _V(
        dict(coat=(120, 96, 78), coat_dk=(82, 64, 52), belly=(170, 150, 132)),
        attrs=dict(build=0.96, leg=0.82, length=1.10, chest=1.0, head=1.08,
                   tail="low", ear="longdrop", muzzle="med")),
     "build0.96 leg0.82 | tail:low ear:LONGDROP(below jaw) | soft brown hound-pup"),
    ("D6 spotted MUTT", _V(
        dict(coat=(232, 226, 214), coat_dk=(150, 144, 134), belly=(244, 240, 232),
             marks=(96, 84, 76)),
        attrs=dict(build=1.0, leg=1.0, length=1.18, chest=0.95, head=1.0,
                   tail="flag", ear="split", muzzle="med")),
     "build1.0 len1.18 | tail:flag ear:SPLIT(1 prick+1 drop) marks:patches | white+grey mongrel"),
]


CRITTERS = [
    ("C1 CAT", _V(
        dict(body=(120, 112, 104), body_dk=(76, 70, 66), accent=(168, 120, 118)),
        attrs=dict(kind="cat")),
     "kind:cat | sit upright, tail curled fwd | MOTION: tail-tip FLICK + ear swivel | grey tabby"),
    ("C2 HEN", _V(
        dict(body=(204, 190, 170), body_dk=(150, 130, 104), accent=(176, 70, 60)),
        attrs=dict(kind="hen")),
     "kind:hen | plump body, comb+wattle(muted red,capped), tail fan | MOTION: PECK down-up | buff"),
    ("C3 PIGEONS", _V(
        dict(body=(142, 144, 154), body_dk=(96, 98, 108), accent=(108, 120, 152)),
        attrs=dict(kind="pigeons")),
     "kind:pigeons | CLUSTER of 3, round-chested ground birds + seed | MOTION: peck + 1 HOPS | slate-grey"),
    ("C4 SPARROWS", _V(
        dict(body=(150, 120, 84), body_dk=(102, 80, 56), accent=(110, 80, 56)),
        attrs=dict(kind="sparrows")),
     "kind:sparrows | tight cluster of 3 TINY birds (smaller than pigeon) | MOTION: quick peck + HOP | brown"),
    ("C5 DUCK", _V(
        dict(body=(212, 206, 192), body_dk=(150, 140, 120), accent=(96, 120, 96)),
        attrs=dict(kind="duck")),
     "kind:duck | boat body, flat BILL, tail tuft, green head | MOTION: side WADDLE + head bob | mallard"),
]


# ════════════════════════════════════════════════════════════════════════════
# SHEET RENDERER  (matches the shipped-family round_2 house style)
# ════════════════════════════════════════════════════════════════════════════

WIDTH = 1180
PAD = 12
BG_DAY = (150, 140, 118)
BG_NIGHT = (40, 46, 70)


def _font(sz, bold=False):
    return pygame.font.SysFont("dejavusans", sz, bold=bold)


def _text(surf, s, x, y, sz=11, col=(228, 224, 214), bold=False):
    surf.blit(_font(sz, bold).render(s, True, col), (x, y))


def _gold_coin(surf, cx, cy, r=8):
    """The in-game gold-coin brightness/size yardstick — nothing on an animal may
    out-pop this, and a far-lane dog/critter is sized against it."""
    for rr, c in ((r, (150, 110, 30)), (r - 1, (235, 190, 60)), (r - 3, (255, 232, 150))):
        pygame.draw.circle(surf, c, (cx, cy), rr)
    pygame.draw.circle(surf, (180, 140, 50), (cx, cy), r, 1)
    surf.blit(_font(9, True).render("$", True, (150, 100, 20)), (cx - 3, cy - 6))


def _adult_ref(surf, cx, base_y, night):
    """A coarse adult-pedestrian stand-in (PED_H~18) so a dog reads CLEARLY
    smaller than a person and a critter reads tiny. Not the production drawer —
    just a scale yardstick on the composite."""
    pf = lambda c: _retint(c, night)
    coat = pf((96, 104, 140)); coat_dk = _shade(coat, -40)
    skin = pf((222, 178, 132)); hair = pf((52, 42, 34))
    g = int(base_y); total = 18
    head_r = 3; torso_h = 8
    torso_top = g - 5 - torso_h
    for sgn in (-1, 1):
        pygame.draw.line(surf, coat_dk, (cx + sgn * 2, torso_top + torso_h),
                         (cx + sgn * 2, g), 2)
    pygame.draw.polygon(surf, coat, [(cx - 3, torso_top), (cx + 3, torso_top),
                                     (cx + 4, torso_top + torso_h), (cx - 4, torso_top + torso_h)])
    pygame.draw.circle(surf, skin, (cx, torso_top - head_r), head_r)
    pygame.draw.circle(surf, hair, (cx, torso_top - head_r - 1), head_r)


def _cell(parent, name, drawer, v, note, x, y, w, h, night, *, n_frames, fr_t,
          fr_dx, zoom_pad):
    """One annotated cell: TRUE far-lane figure across N anim frames + a zoom
    inset, on a day or night deck, with the part/palette/attrs note."""
    is_night = night > 0.5
    bg = BG_NIGHT if is_night else BG_DAY
    cell = pygame.Surface((w, h))
    cell.fill(bg)
    deck = _mix(bg, (0, 0, 0), 0.18)
    base = h - 16
    pygame.draw.rect(cell, deck, (0, base, w, h - base))
    pygame.draw.line(cell, _shade(bg, 24), (0, base), (w, base), 1)

    # N animation frames at TRUE far-lane size (crisp — no scaling)
    fx0 = 14
    for i in range(n_frames):
        cxp = fx0 + 16 + i * fr_dx
        drawer(cell, cxp, base, v, night, fr_t[i])
        _text(cell, f"t{i}", cxp - 6, base + 2, 8, _shade(bg, 60))
    _text(cell, "TRUE far-lane (anim frames)", fx0, base + 8, 8, _shade(bg, 50))

    # zoom inset (~4x — these are tiny, so a bigger zoom than the stalls) framed
    # at right, NEAREST scaling so the authored pixels stay crisp. Feet are placed
    # well up from the surface bottom so the tail/ears clear the top edge.
    SC = 40
    nat = pygame.Surface((SC, SC), pygame.SRCALPHA)
    # deck line inside the inset so the figure visibly stands on a surface
    deck_y = SC - zoom_pad
    nat.fill((*_mix(bg, (0, 0, 0), 0.18), 90), (0, deck_y, SC, SC - deck_y))
    drawer(nat, SC // 2, deck_y, v, night, fr_t[min(1, n_frames - 1)])
    z = 4
    zoom = pygame.transform.scale(nat, (SC * z, SC * z))   # nearest (no smooth)
    zw, zh = zoom.get_size()
    zx, zy = w - zw - 8, 22
    pygame.draw.rect(cell, _shade(bg, -20), (zx - 2, zy - 2, zw + 4, zh + 4))
    cell.blit(zoom, (zx, zy))
    pygame.draw.rect(cell, _shade(bg, 40), (zx - 2, zy - 2, zw + 4, zh + 4), 1)
    _text(cell, "4x zoom", zx, zy - 12, 8, _shade(bg, 60))

    # an in-cell coin so each figure can be judged against the brightness/size ref
    _gold_coin(cell, w - 16, h - 12, r=6)

    _text(cell, name, 6, 4, 13, (240, 236, 226), bold=True)
    fnt = _font(9, False)
    line = ""; yy = 22
    wrap_w = zx - 12
    for wd in note.split(" "):
        test = (line + " " + wd).strip()
        if fnt.size(test)[0] > wrap_w:
            cell.blit(fnt.render(line, True, (206, 202, 192)), (6, yy)); yy += 11; line = wd
        else:
            line = test
    if line:
        cell.blit(fnt.render(line, True, (206, 202, 192)), (6, yy))

    parent.blit(cell, (x, y))
    pygame.draw.rect(parent, (70, 74, 90), (x, y, w, h), 1)


def _true_band(sheet, y, title, items, drawer, night, *, base_off):
    """A grouped true-size band: all members of one group in a row at far-lane
    size on one deck, with the gold-coin yardstick at the row's right."""
    _text(sheet, title, PAD, y, 13, (240, 220, 150), bold=True)
    y += 22
    band_h = 60
    row = pygame.Surface((WIDTH - PAD * 2, band_h))
    bg = BG_NIGHT if night > 0.5 else BG_DAY
    row.fill(bg)
    deck = _mix(bg, (0, 0, 0), 0.18)
    base = band_h - 14
    pygame.draw.rect(row, deck, (0, base, WIDTH - PAD * 2, 14))
    pygame.draw.line(row, _shade(bg, 26), (0, base), (WIDTH - PAD * 2, base), 1)
    # gold coin yardstick on the deck so figures are sized + brightness-judged
    _gold_coin(row, WIDTH - PAD * 2 - 20, base - 9)
    _text(row, "coin", WIDTH - PAD * 2 - 38, base + 1, 8, _shade(bg, 50))
    spacing = (WIDTH - PAD * 2 - 110) // len(items)
    for i, (nm, v, _n) in enumerate(items):
        cx = 60 + i * spacing
        drawer(row, cx, base, v, night, 0.4 + i * 0.5)
        _text(row, nm.split(" ")[0], cx - 8, base + 1, 8,
              (70, 58, 46) if night <= 0.5 else (150, 160, 185))
    sheet.blit(row, (PAD, y))
    pygame.draw.rect(sheet, (70, 74, 90), (PAD, y, WIDTH - PAD * 2, band_h), 1)
    return y + band_h + 8


def render():
    cell_w = (WIDTH - PAD * 3) // 2
    dog_cell_h = 124
    crit_cell_h = 120

    # Height budget
    title_h = 58
    bandA_h = 22 + 60 + 8 + 22 + 60 + 8        # dogs band + critters band
    dog_rows = (len(DOGS) + 1) // 2
    crit_rows = (len(CRITTERS) + 1) // 2
    detail_h = (22 + 2 * (18 + dog_rows * (dog_cell_h + 6)) +
                14 + 2 * (18 + crit_rows * (crit_cell_h + 6)))
    strip_h = 96
    comp_h = 22 + 2 * (strip_h + 6)
    total_h = title_h + bandA_h + detail_h + comp_h + PAD * 6 + 24

    sheet = pygame.Surface((WIDTH, total_h))
    sheet.fill((26, 28, 38))

    y = PAD
    _text(sheet, "SKYBIT PROMENADE — STREET ANIMALS (round 1): 6 DOGS + 5 CRITTERS",
          PAD, y, 17, (250, 246, 236), bold=True)
    y += 22
    _text(sheet, "Two variety SETS over shared drawers (a dog drawer; a small-critter drawer). Breed/critter read lives in the OUTLINE "
                 "(proportion+tail+ear+stance), since the far-lane shrink kills colour+interior detail first. Authored at native size, drawn CRISP "
                 "(nearest). Night: cooled toward (54,64,96), nothing self-lit, <=150 luma; nothing out-pops the gold coin.",
          PAD, y, 9, (188, 186, 200))
    y += title_h - 22

    # ── A. TRUE-SIZE BANDS (grouped) with the coin yardstick ──
    y = _true_band(sheet, y, "A1.  DOGS — true far-lane size, with the gold-coin yardstick (a dog reads CLEARLY smaller than an adult)",
                   DOGS, draw_dog, 0.0, base_off=2)
    y = _true_band(sheet, y, "A2.  CRITTERS — true far-lane size (a pigeon reads as a small ground bird, not a chick-sized blob)",
                   CRITTERS, draw_critter, 0.0, base_off=1)

    # ── B. PER-DOG detail (day rows then night rows) ──
    _text(sheet, "B.  PER-DOG — TRUE far-lane across 2 GAIT frames (amble) · 4x zoom (nearest) · in-cell coin · attrs/palette note  (DAY then NIGHT)",
          PAD, y, 13, (240, 220, 150), bold=True)
    y += 20
    for is_night in (False, True):
        night = 0.95 if is_night else 0.0
        _text(sheet, "NIGHT  (cooled <=150, nothing self-lit)" if is_night else "DAY",
              PAD, y, 11, (160, 180, 220) if is_night else (240, 210, 130), bold=True)
        y += 16
        for r in range(dog_rows):
            for c in range(2):
                idx = r * 2 + c
                if idx >= len(DOGS):
                    break
                nm, v, note = DOGS[idx]
                cx = PAD + c * (cell_w + PAD)
                _cell(sheet, nm, draw_dog, v, note, cx, y, cell_w, dog_cell_h, night,
                      n_frames=2, fr_t=(0.0, 0.52), fr_dx=58, zoom_pad=6)
            y += dog_cell_h + 6
        y += 8

    # ── B2. PER-CRITTER detail (day rows then night rows) ──
    _text(sheet, "B2.  PER-CRITTER — TRUE far-lane across 3 MOTION frames (peck/hop/flick/waddle) · 4x zoom · in-cell coin · note  (DAY then NIGHT)",
          PAD, y, 13, (240, 220, 150), bold=True)
    y += 20
    for is_night in (False, True):
        night = 0.95 if is_night else 0.0
        _text(sheet, "NIGHT" if is_night else "DAY", PAD, y, 11,
              (160, 180, 220) if is_night else (240, 210, 130), bold=True)
        y += 16
        for r in range(crit_rows):
            for c in range(2):
                idx = r * 2 + c
                if idx >= len(CRITTERS):
                    break
                nm, v, note = CRITTERS[idx]
                cx = PAD + c * (cell_w + PAD)
                _cell(sheet, nm, draw_critter, v, note, cx, y, cell_w, crit_cell_h, night,
                      n_frames=3, fr_t=(0.0, 0.55, 1.15), fr_dx=46, zoom_pad=4)
            y += crit_cell_h + 6
        y += 8

    # ── C. ON-STREET COMPOSITE (day + night) mixing dogs + critters + 2 humans ──
    _text(sheet, "C.  ON-STREET COMPOSITE — dogs + critters ambling among a couple of human-cast figures (PED_H~18 scale ref) + the coin",
          PAD, y, 13, (240, 220, 150), bold=True)
    y += 20
    for is_night in (False, True):
        night = 0.95 if is_night else 0.0
        bg = BG_NIGHT if is_night else BG_DAY
        strip = pygame.Surface((WIDTH - PAD * 2, strip_h))
        strip.fill(bg)
        deck = _mix(bg, (0, 0, 0), 0.2)
        base = strip_h - 14
        pygame.draw.rect(strip, deck, (0, base, WIDTH - PAD * 2, strip_h - base))
        pygame.draw.line(strip, _shade(bg, 24), (0, base), (WIDTH - PAD * 2, base), 1)
        # a mixed parade: adult, dog, critters interleaved, another adult, dog...
        sw = WIDTH - PAD * 2
        _adult_ref(strip, 40, base, night)
        draw_dog(strip, 92, base, DOGS[0][1], night, 0.6)          # hound
        draw_critter(strip, 150, base, CRITTERS[1][1], night, 0.4)  # hen
        draw_dog(strip, 210, base, DOGS[2][1], night, 1.1)          # spitz
        draw_critter(strip, 270, base, CRITTERS[2][1], night, 0.8)  # pigeons
        _adult_ref(strip, 340, base, night)
        draw_dog(strip, 392, base, DOGS[1][1], night, 0.3)          # dash
        draw_critter(strip, 452, base, CRITTERS[0][1], night, 0.5)  # cat
        draw_dog(strip, 510, base, DOGS[3][1], night, 0.9)          # shiba
        draw_critter(strip, 566, base, CRITTERS[4][1], night, 0.7)  # duck
        draw_dog(strip, 626, base, DOGS[4][1], night, 0.2)          # droopy pup
        draw_critter(strip, 686, base, CRITTERS[3][1], night, 1.2)  # sparrows
        draw_dog(strip, 740, base, DOGS[5][1], night, 0.5)          # mutt
        _adult_ref(strip, 800, base, night)
        _gold_coin(strip, sw - 18, 18)
        _text(strip, "coin ref", sw - 44, 30, 8, _shade(bg, 60))
        _text(strip, "NIGHT" if is_night else "DAY", 4, 2, 9,
              (170, 190, 225) if is_night else (60, 50, 40), bold=True)
        sheet.blit(strip, (PAD, y))
        pygame.draw.rect(sheet, (70, 74, 90), (PAD, y, WIDTH - PAD * 2, strip_h), 1)
        y += strip_h + 6

    # ── cap-audit footer: the hottest animal pixels through luma, vs the coin ──
    audits = [
        ("D4 shiba coat (day)", (196, 130, 74)),
        ("C2 hen comb (night)", _retint((176, 70, 60), 0.95)),
        ("C5 duck head (night)", _retint((96, 120, 96), 0.95)),
        ("D3 spitz coat (night)", _retint((228, 222, 210), 0.95)),
        ("coin core (brightest)", (255, 232, 150)),
    ]
    line = "  ·  ".join(f"{nm} luma={_luma(c):.0f}" for nm, c in audits)
    _text(sheet, "CAP AUDIT (night animal pixels <=150; only the coin is brighter):  " + line,
          PAD, total_h - 16, 9, (170, 200, 180))

    out = "/home/user/skybit/docs/sidewalk_overhaul/animals/round_1.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("saved", out, sheet.get_size())
    for nm, c in audits:
        print(f"  {nm:26s} rgb={c} luma={_luma(c):.1f}")


if __name__ == "__main__":
    render()
