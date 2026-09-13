"""Promenade STREET-ANIMALS variety — round 2 candidate-sheet generator.

Iterates round 1 (tools/_animals_round1.py) on the art-director's ITERATE notes.
The shared-drawer model + most of the set were approved; this round addresses the
gating fixes and trims to a tighter, silhouette-distinct cast:

  DOGS 6 -> 5 (all clearly SMALLER than an adult; D2 dash is the height ceiling):
    D1 lean tall HOUND      — long legs, deep narrow chest, long low sabre tail, drop ears
    D2 short-legged DASH    — low corgi/dachshund build, long body, stub-up tail, big ears
                              (BENCHMARK — drawer + attrs untouched from round 1)
    D3 fluffy curl SPITZ    — fox build, plumed curl tail, prick ears  (RESCALED ~17% down)
    D4 stocky SHIBA/AKITA   — compact thick build, tight curl tail, prick ears (RESCALED ~17%)
    D5 droopy LONG-EARED PUP — NEW silhouette: low ears hanging BELOW the jawline that
                              break the head outline, a gentle low tail; contrasts D4's
                              perky ears + D1's lean profile.  (rebuilt from round-1 D5/D6)
    (CUT round-1 D6 spotted mutt — spots are interior colour that dies at far-lane shrink.)

  CRITTERS 5 -> 4:
    C1 CAT      — sitting upright, tail curled around the paws; tail-tip FLICK + ear swivel
    C2 HEN      — plump body, comb + wattle + tail fan; PECK down-up cycle
    C3 PIGEONS  — TIGHTER little-bird clump: one larger LEAD bird anchors the read, two
                  smaller followers peck + one HOPS  (so it reads as birds, not grit)
    C4 DUCK     — waddling boat body, flat bill + tail-tuft; side WADDLE + head bob
    (CUT round-1 C4 sparrows — pigeon-vs-sparrow is a size-only read that collapses at 4-6px.)

Round-2 fixes, all addressed here:
  1. D3 + D4 rescaled DOWN ~17% (build/head) so dog height <= D2 ceiling, < adult.
  2. Dogs 6->5: D5 rebuilt droopy long-eared, D6 cut. Distinct-by-SILHOUETTE.
  3. Critters 5->4: sparrows cut; pigeon clump tightened with a LEAD bird.
  4. NIGHT CAP: white coats cool to a warm grey-blue at night; ALL animal pixels land
     <=150 luma (the gold coin at ~230 stays the sole brightest element). Highlights
     derived from a night coat are clamped so _shade can't push a white past the cap.
  5. No speckle markings survive; distinctiveness is pure silhouette.
  6. SHEET: the per-figure zoom inset is wired correctly (round 1's insets blitted EMPTY
     because the figure overran the small native surface — fixed by sizing the native
     canvas to the figure + a measured floor, then nearest-scaling).
  7. D1 tail carriage nudged a touch lower/longer so the clean "default" hound stays
     distinct from the new droopy pup.

CONSTRAINTS (unchanged): pure pygame.draw.* + Surface (SRCALPHA ok), pygbag-safe; no
numpy/gfxdraw/PIL. Dogs ~8-12px (<= D2 height), critters ~4-8px. Authored native size,
drawn CRISP (nearest; no smoothscale). Night cooled, nothing self-lit, <=150 luma; muted
shan-shui palette; nothing out-pops the coin. Expressible as foreground_variants.Variant
rows: palette + attrs over the shared draw_dog / draw_critter drawers.

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


def _luma(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


NIGHT_GLOW_CAP = 150


def _retint(col, night):
    """Cool toward the night ground band — matches ped_cast._retint_person so the
    animals sit in the same value family as the retinted floor and human cast.

    A second, stronger cool is applied to PALE coats: a near-white source would
    otherwise survive the generic retint above the cap (and a +16 highlight on it
    then breaches it), and only the gold coin may be the brightest thing on screen.
    So any retinted colour still above the cap is pulled the rest of the way down
    into the warm grey-blue night band."""
    if night <= 0.05:
        return col
    out = _mix(col, (54, 64, 96), min(0.55, 0.40 * night + 0.20))
    if _luma(out) > NIGHT_GLOW_CAP:
        over = (_luma(out) - NIGHT_GLOW_CAP) / max(1.0, 255 - NIGHT_GLOW_CAP)
        out = _mix(out, (66, 76, 104), min(0.78, 0.5 + over))
    return out


def _hi(c, d, night):
    """A highlight d above c, but never above the night cap — so _shade can't push
    a pale night coat past the gold coin. Day is unconstrained (the coin is brighter
    than any coat in daylight)."""
    out = _shade(c, d)
    if night > 0.05 and _luma(out) > NIGHT_GLOW_CAP:
        out = _mix(out, (66, 76, 104), 0.65)
    return out


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
#   tail    — 'low'|'lowpup'|'plume'|'tightcurl'|'stub'  (shape enum)
#   ear     — 'drop'|'prick'|'bigprick'|'longdrop'  (shape enum)
#   muzzle  — 'long'|'med'|'short'  (snout length)
# palette roles: coat, coat_dk, belly

DOG_H = 12      # shoulder height of a 1.0-build dog (px). ~2/3 of an adult (PED_H 18).


def draw_dog(surf, cx, base_y, v, night, t):
    P, A = v.palette, v.attrs
    pf = lambda c: _retint(c, night)
    coat = pf(P["coat"])
    coat_dk = pf(P.get("coat_dk", _shade(P["coat"], -40)))
    coat_lt = _hi(coat, 16, night)
    belly = pf(P.get("belly", _shade(P["coat"], 22)))
    nose_c = pf((40, 32, 30))

    build = A.get("build", 1.0)
    legf = A.get("leg", 1.0)
    lengthf = A.get("length", 1.0)
    chestf = A.get("chest", 1.0)
    headf = A.get("head", 1.0)
    fluffy = A.get("fluffy", False)
    tail = A.get("tail", "low")
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
    if tail == "low":                 # hound: long sabre sweep down-and-back. The
        # clean DEFAULT — carried a touch lower + longer than round 1 so it stays
        # distinct now that D5 is the droopy pup (also low-tailed but stubbier).
        pygame.draw.lines(surf, tcol, False, [
            (tx - 1, body_cy), (tx + int(sh_h * 0.55), body_cy + int(sh_h * 0.22)),
            (tx + int(sh_h * 0.80), body_cy + int(sh_h * 0.60) + sway)], tw)
        pygame.draw.lines(surf, coat_dk, False, [
            (tx - 1, body_cy), (tx + int(sh_h * 0.55), body_cy + int(sh_h * 0.22)),
            (tx + int(sh_h * 0.80), body_cy + int(sh_h * 0.60) + sway)], 1)
    elif tail == "lowpup":            # droopy pup: short gentle low tail, soft hook
        pygame.draw.lines(surf, tcol, False, [
            (tx - 1, body_cy), (tx + int(sh_h * 0.32), body_cy + int(sh_h * 0.20)),
            (tx + int(sh_h * 0.38), body_cy + sway)], tw)
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
    elif tail == "tightcurl":         # shiba/akita: tight C-ring curl flat on the back
        cxr, cyr = tx - 1, body_top - 1
        rr = max(2, int(sh_h * 0.26))
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
    if fluffy:
        for bxp in range(body_left + 2, body_right - 1, 2):
            pygame.draw.circle(surf, coat_lt, (bxp, body_top + 1), 1)

    # ── NECK + HEAD up front (left). Head sits forward of, and above, the chest.
    hx = body_left - max(1, int(head_r * 0.3))
    hy = body_top + max(1, int(body_h * 0.1)) - max(1, int(sh_h * 0.18))
    pygame.draw.polygon(surf, coat, [
        (body_left + head_r, body_top), (body_left + 1, body_top + body_h - 1),
        (hx, hy + head_r), (hx - 1, hy - head_r // 2)])
    if fluffy:
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
    pygame.draw.circle(surf, nose_c, (mx, hy), 1)
    pygame.draw.circle(surf, (28, 22, 20), (hx - head_r // 3, hy - head_r // 3), 1)

    # ── EARS (the second strongest breed cue) — drawn AFTER the head ──
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
    elif ear == "longdrop":           # VERY long low ears that hang BELOW the jawline,
        # breaking the round head silhouette into a wide droopy outline. A near ear
        # over the cheek and a far ear behind it both fall well past the jaw — this
        # is the whole point of D5's read, so the ear must dominate the head outline.
        sway2 = int(round(gait * 0.8))
        for depth, fx_off, shade in ((2.7, 1, 0), (2.4, -1, -16)):
            ex0 = hx + (head_r // 2 if fx_off > 0 else -head_r // 3)
            tip_y = hy + int(head_r * depth)
            pygame.draw.polygon(surf, _shade(coat_dk, shade), [
                (ex0, hy - head_r + 1),
                (hx + head_r + 1, hy - head_r // 3),
                (hx + (head_r if fx_off > 0 else 1) + sway2, tip_y),
                (ex0 - 1, hy + head_r // 2)])


# ════════════════════════════════════════════════════════════════════════════
# CRITTERS — ONE shared drawer dispatched by `kind`; each its own t-motion.
# Authored feet-on-base_y, facing LEFT, TINY (~4-8px).
# ════════════════════════════════════════════════════════════════════════════

def draw_critter(surf, cx, base_y, v, night, t):
    kind = v.attrs.get("kind", "hen")
    {"cat": _crit_cat, "hen": _crit_hen, "pigeons": _crit_pigeons,
     "duck": _crit_duck}[kind](surf, cx, base_y, v, night, t)


def _crit_cat(surf, cx, base_y, v, night, t):
    """A sitting cat, upright, tail curled around the front paws. Motion: a slow
    tail-tip FLICK + an occasional ear swivel — the universal idle-cat read."""
    pf = lambda c: _retint(c, night)
    P = v.palette
    fur = pf(P.get("body", (120, 112, 104)))
    fur_dk = pf(P.get("body_dk", _shade(P["body"], -34)))
    fur_lt = _hi(fur, 18, night)
    ear_in = pf(P.get("accent", (150, 110, 110)))
    g = int(base_y)
    body_h = 7
    body = pygame.Rect(cx - 3, g - body_h, 6, body_h)
    pygame.draw.ellipse(surf, fur, body)
    pygame.draw.ellipse(surf, fur_dk, body, 1)
    pygame.draw.ellipse(surf, fur, (cx - 4, g - 3, 8, 3))
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
    pygame.draw.circle(surf, (40, 70, 50), (hx - 1, hy), 1)
    pygame.draw.circle(surf, fur_lt, (hx - 2, hy + 1), 1)
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
    body_lt = _hi(body, 16, night)
    comb = pf(P.get("accent", (176, 70, 60)))
    beak = pf((196, 158, 80))
    leg = pf((176, 140, 88))
    g = int(base_y)
    peck = max(0.0, math.sin(t * 3.2))
    bw, bh = 8, 6
    by = g - bh - 1
    pygame.draw.ellipse(surf, body, (cx - bw // 2, by, bw, bh))
    pygame.draw.ellipse(surf, body_dk, (cx - bw // 2, by, bw, bh), 1)
    pygame.draw.arc(surf, body_lt, (cx - bw // 2, by, bw, bh),
                    math.radians(40), math.radians(150), 1)
    pygame.draw.polygon(surf, body_dk, [
        (cx + bw // 2 - 1, by + 1), (cx + bw // 2 + 3, by - 3),
        (cx + bw // 2 + 2, by + 2)])
    pygame.draw.polygon(surf, body, [
        (cx + bw // 2 - 1, by + 1), (cx + bw // 2 + 2, by - 1),
        (cx + bw // 2, by + 3)])
    for lx in (cx - 1, cx + 2):
        pygame.draw.line(surf, leg, (lx, by + bh - 1), (lx, g), 1)
        pygame.draw.line(surf, leg, (lx - 1, g), (lx + 1, g), 1)
    hx0, hy0 = cx - bw // 2, by
    hx = hx0 - 1 - int(peck * 1)
    hy = hy0 - 2 + int(peck * 5)
    pygame.draw.line(surf, body, (hx0, by + 1), (hx, hy), 2)
    pygame.draw.circle(surf, body, (hx, hy), 2)
    pygame.draw.circle(surf, comb, (hx, hy - 2), 1)
    pygame.draw.circle(surf, comb, (hx - 1, hy + 1), 1)
    pygame.draw.polygon(surf, beak, [(hx - 2, hy), (hx - 4, hy), (hx - 2, hy + 1)])
    pygame.draw.circle(surf, (24, 18, 16), (hx - 1, hy - 1), 1)


def _crit_pigeons(surf, cx, base_y, v, night, t):
    """A TIGHT little-bird clump: one slightly larger LEAD bird anchors the group
    read, two smaller followers hug it (so it reads as a flock of birds, not grit).
    Motion: each pecks on its own phase; one follower HOPS on a slow cycle."""
    pf = lambda c: _retint(c, night)
    P = v.palette
    body = pf(P.get("body", (140, 142, 152)))
    body_dk = pf(P.get("body_dk", _shade(P["body"], -34)))
    neck = pf(P.get("accent", (110, 120, 150)))
    beak = pf((120, 110, 110))
    g = int(base_y)
    # (dx, phase, hops, lead) — the lead bird is bigger + front-left, anchoring the
    # clump; the two followers are tucked tight behind it so they read as one group.
    specs = ((-3, 0.0, False, True), (3, 0.6, True, False), (6, 1.1, False, False))
    for dx, ph, hops, lead in specs:
        bx = cx + dx
        peck = max(0.0, math.sin(t * 3.0 + ph * 6))
        hop = max(0.0, math.sin(t * 1.6 + ph * 6)) if hops else 0.0
        lift = int(hop * 4)
        gb = g - lift
        bw, bh = (7, 5) if lead else (5, 4)        # LEAD bird is the bigger anchor
        by = gb - bh - 1
        pygame.draw.ellipse(surf, body, (bx - bw // 2, by, bw, bh))
        pygame.draw.ellipse(surf, body_dk, (bx - bw // 2, by, bw, bh), 1)
        pygame.draw.line(surf, body_dk, (bx + bw // 2 - 1, by + 1),
                         (bx + bw // 2 + 2, by + 2), 1)
        if lift <= 0:
            for lx in (bx - 1, bx + 1):
                pygame.draw.line(surf, beak, (lx, by + bh - 1), (lx, g), 1)
        hr = 2 if lead else 1
        hx = bx - bw // 2 - int(peck * 1)
        hy = by - 1 + int(peck * 3)
        pygame.draw.line(surf, neck, (bx - bw // 2 + 1, by + 1), (hx, hy), 2)
        pygame.draw.circle(surf, body, (hx, hy), hr)
        pygame.draw.polygon(surf, beak, [(hx - hr, hy), (hx - hr - 1, hy), (hx - hr, hy + 1)])
        pygame.draw.circle(surf, (24, 20, 22), (hx - 1, hy - 1), 1)
    # a couple of seed flecks the clump pecks at (kept close so they read as feed)
    for sx in (cx - 2, cx + 4):
        pygame.draw.circle(surf, pf((150, 130, 90)), (sx, g), 1)


def _crit_duck(surf, cx, base_y, v, night, t):
    """A waddling duck — horizontal boat body, flat BILL, up-tucked tail tuft.
    Motion: side-to-side WADDLE (body rocks) + a gentle head bob."""
    pf = lambda c: _retint(c, night)
    P = v.palette
    body = pf(P.get("body", (210, 204, 190)))
    body_dk = pf(P.get("body_dk", _shade(P["body"], -36)))
    body_lt = _hi(body, 16, night)
    head_c = pf(P.get("accent", (96, 120, 96)))
    bill = pf((196, 168, 90))
    foot = pf((200, 150, 80))
    g = int(base_y)
    waddle = math.sin(t * 3.4)
    rock = int(round(waddle * 1))
    bobh = int(round(math.sin(t * 3.4 + 1.2) * 1))
    bw, bh = 9, 4
    by = g - bh - 1
    pygame.draw.ellipse(surf, body, (cx - bw // 2, by, bw, bh))
    pygame.draw.ellipse(surf, body_dk, (cx - bw // 2, by, bw, bh), 1)
    pygame.draw.arc(surf, body_lt, (cx - bw // 2, by, bw, bh),
                    math.radians(30), math.radians(150), 1)
    pygame.draw.polygon(surf, body, [
        (cx + bw // 2 - 1, by + 1), (cx + bw // 2 + 2, by - 2),
        (cx + bw // 2, by + 2)])
    for lx, phase in ((cx - 1, 0), (cx + 2, math.pi)):
        step = int(round(math.sin(t * 3.4 + phase) * 1))
        pygame.draw.line(surf, foot, (lx, by + bh - 1), (lx + step, g), 1)
        pygame.draw.line(surf, foot, (lx + step - 1, g), (lx + step + 1, g), 1)
    hx = cx - bw // 2 - 1 + rock
    hy = by - 3 + bobh
    pygame.draw.line(surf, head_c, (cx - bw // 2 + 1, by + 1), (hx, hy), 2)
    pygame.draw.circle(surf, head_c, (hx, hy), 2)
    pygame.draw.polygon(surf, bill, [(hx - 2, hy), (hx - 4, hy - 1),
                                     (hx - 4, hy + 1), (hx - 2, hy + 1)])
    pygame.draw.circle(surf, (22, 20, 18), (hx - 1, hy - 1), 1)


# ════════════════════════════════════════════════════════════════════════════
# THE POOLS — foreground_variants.Variant rows (data, not bespoke functions)
# ════════════════════════════════════════════════════════════════════════════

class _V:
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
     "build1.05 leg1.15 len1.30 chest0.85 | tail:low(long sabre, carried LOW) ear:drop muzzle:long | tan/sand — clean DEFAULT"),
    ("D2 short-leg DASH", _V(
        dict(coat=(150, 102, 64), coat_dk=(104, 68, 42), belly=(196, 160, 110)),
        attrs=dict(build=0.95, leg=0.52, length=1.45, chest=1.05, head=1.0,
                   tail="stub", ear="bigprick", muzzle="med")),
     "build0.95 leg0.52 len1.45 | tail:stub ear:bigprick | corgi/dachshund low-long, chestnut — BENCHMARK (untouched)"),
    ("D3 fluffy SPITZ", _V(
        dict(coat=(214, 208, 196), coat_dk=(150, 144, 132), belly=(226, 222, 212)),
        attrs=dict(build=0.80, leg=0.92, length=0.98, chest=1.10, head=0.90,
                   fluffy=True, tail="plume", ear="prick", muzzle="med")),
     "RESCALED -17%: build0.96->0.80 head1.05->0.90 | tail:plume(up+back) ear:prick + ruff | cream (night-cooled to grey-blue)"),
    ("D4 stocky SHIBA", _V(
        dict(coat=(196, 130, 74), coat_dk=(140, 86, 46), belly=(228, 206, 172)),
        attrs=dict(build=0.98, leg=0.80, length=1.0, chest=1.12, head=0.92,
                   fluffy=True, tail="tightcurl", ear="prick", muzzle="short")),
     "RESCALED -17%: build1.18->0.98 head1.10->0.92 | tail:tightcurl(C-ring) ear:prick muzzle:short | rust shiba/akita"),
    ("D5 droopy LONG-EAR PUP", _V(
        dict(coat=(150, 124, 96), coat_dk=(104, 84, 64), belly=(186, 166, 142)),
        attrs=dict(build=0.94, leg=0.74, length=1.06, chest=1.02, head=1.10,
                   tail="lowpup", ear="longdrop", muzzle="short")),
     "NEW silhouette: ear:LONGDROP (hangs BELOW jawline, breaks head outline) tail:lowpup(short low hook) head1.10 muzzle:short | warm grey-brown"),
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
     "kind:pigeons | TIGHT clump: 1 larger LEAD bird + 2 followers + feed | MOTION: peck, 1 HOPS | slate-grey"),
    ("C4 DUCK", _V(
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
    for rr, c in ((r, (150, 110, 30)), (r - 1, (235, 190, 60)), (r - 3, (255, 232, 150))):
        pygame.draw.circle(surf, c, (cx, cy), rr)
    pygame.draw.circle(surf, (180, 140, 50), (cx, cy), r, 1)
    surf.blit(_font(9, True).render("$", True, (150, 100, 20)), (cx - 3, cy - 6))


def _adult_ref(surf, cx, base_y, night):
    """A coarse adult-pedestrian stand-in (PED_H~18) so a dog reads CLEARLY
    smaller than a person and a critter reads tiny."""
    pf = lambda c: _retint(c, night)
    coat = pf((96, 104, 140)); coat_dk = _shade(coat, -40)
    skin = pf((222, 178, 132)); hair = pf((52, 42, 34))
    g = int(base_y)
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
    """One annotated cell: TRUE far-lane figure across N anim frames + a WORKING
    zoom inset, on a day or night deck, with the part/palette/attrs note."""
    is_night = night > 0.5
    bg = BG_NIGHT if is_night else BG_DAY
    cell = pygame.Surface((w, h))
    cell.fill(bg)
    deck = _mix(bg, (0, 0, 0), 0.18)
    base = h - 16
    pygame.draw.rect(cell, deck, (0, base, w, h - base))
    pygame.draw.line(cell, _shade(bg, 24), (0, base), (w, base), 1)

    fx0 = 14
    for i in range(n_frames):
        cxp = fx0 + 16 + i * fr_dx
        drawer(cell, cxp, base, v, night, fr_t[i])
        _text(cell, f"t{i}", cxp - 6, base + 2, 8, _shade(bg, 60))
    _text(cell, "TRUE far-lane (anim frames)", fx0, base + 8, 8, _shade(bg, 50))

    # WORKING zoom inset. Round-1 bug: the native canvas was square+small and the
    # figure (drawn at its deck_y) overran it so the visible inset read EMPTY. Fix:
    # size the native canvas to a figure-sized box, seat the figure with clear
    # headroom for tail/ears, then NEAREST-scale (no smooth) so authored pixels stay crisp.
    SC_W, SC_H = 30, 26
    nat = pygame.Surface((SC_W, SC_H), pygame.SRCALPHA)
    deck_y = SC_H - zoom_pad
    nat.fill((*_mix(bg, (0, 0, 0), 0.18), 120), (0, deck_y, SC_W, SC_H - deck_y))
    drawer(nat, SC_W // 2, deck_y, v, night, fr_t[min(1, n_frames - 1)])
    z = 4
    zoom = pygame.transform.scale(nat, (SC_W * z, SC_H * z))   # nearest (no smooth)
    zw, zh = zoom.get_size()
    zx, zy = w - zw - 8, 20
    pygame.draw.rect(cell, _shade(bg, -20), (zx - 2, zy - 2, zw + 4, zh + 4))
    cell.blit(zoom, (zx, zy))
    pygame.draw.rect(cell, _shade(bg, 40), (zx - 2, zy - 2, zw + 4, zh + 4), 1)
    _text(cell, "4x zoom (nearest)", zx, zy - 12, 8, _shade(bg, 60))

    _gold_coin(cell, w - 16, h - 12, r=6)

    _text(cell, name, 6, 4, 13, (240, 236, 226), bold=True)
    fnt = _font(9, False)
    line = ""; yy = 22
    wrap_w = zx - 14
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


def _measure_night_cap():
    """Render every animal onto a night strip exactly as the composite does, then
    scan the RENDERED pixels (not just the source palette) for the hottest animal
    luma. This is what the footer prints — an honest cap measurement on the composite."""
    night = 0.95
    strip = pygame.Surface((1000, 80))
    strip.fill(BG_NIGHT)
    base = 60
    x = 50
    for _nm, v, _n in DOGS:
        for tt in (0.0, 0.5, 1.0):       # sample a few gait phases for highlights
            draw_dog(strip, x, base, v, night, tt)
            x += 28
        x += 14
    for _nm, v, _n in CRITTERS:
        for tt in (0.0, 0.5, 1.0):
            draw_critter(strip, x, base, v, night, tt)
            x += 22
        x += 14
    hottest = 0.0
    over = 0
    bg_l = _luma(BG_NIGHT)
    for px in range(strip.get_width()):
        for py in range(strip.get_height()):
            c = strip.get_at((px, py))[:3]
            l = _luma(c)
            if abs(l - bg_l) < 1.5:
                continue
            if l > hottest:
                hottest = l
            if l > NIGHT_GLOW_CAP:
                over += 1
    return hottest, over


def render():
    cell_w = (WIDTH - PAD * 3) // 2
    dog_cell_h = 128
    crit_cell_h = 124

    title_h = 58
    bandA_h = 22 + 60 + 8 + 22 + 60 + 8
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
    _text(sheet, "SKYBIT PROMENADE — STREET ANIMALS (round 2): 5 DOGS + 4 CRITTERS",
          PAD, y, 17, (250, 246, 236), bold=True)
    y += 22
    _text(sheet, "ITERATE fixes: D3+D4 rescaled -17% (all dogs < adult, <= D2 ceiling) · dogs 6->5 (D5 rebuilt DROOPY long-eared; D6 mutt cut) · "
                 "critters 5->4 (sparrows cut; pigeon clump tightened w/ a LEAD bird) · night cap: pale coats cooled to grey-blue, ALL animal px <=150 (coin sole brightest) · "
                 "no speckle markings · WORKING zoom insets · D1 tail carried lower so the clean DEFAULT stays distinct from D5.",
          PAD, y, 9, (188, 186, 200))
    y += title_h - 22

    y = _true_band(sheet, y, "A1.  DOGS — true far-lane size, coin yardstick (a dog reads CLEARLY smaller than an adult; D2 dash is the height ceiling)",
                   DOGS, draw_dog, 0.0, base_off=2)
    y = _true_band(sheet, y, "A2.  CRITTERS — true far-lane size (pigeons read as a TIGHT little-bird clump anchored by a lead bird, not scattered grit)",
                   CRITTERS, draw_critter, 0.0, base_off=1)

    _text(sheet, "B.  PER-DOG — TRUE far-lane across 2 GAIT frames (amble) · 4x WORKING zoom (nearest) · in-cell coin · attrs/palette note  (DAY then NIGHT)",
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
                      n_frames=2, fr_t=(0.0, 0.52), fr_dx=58, zoom_pad=4)
            y += dog_cell_h + 6
        y += 8

    _text(sheet, "B2.  PER-CRITTER — TRUE far-lane across 3 MOTION frames (peck/hop/flick/waddle) · 4x WORKING zoom · in-cell coin · note  (DAY then NIGHT)",
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

    _text(sheet, "C.  ON-STREET COMPOSITE — 5 dogs + 4 critters ambling among human-cast figures (PED_H~18 scale ref) + the coin",
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
        sw = WIDTH - PAD * 2
        _adult_ref(strip, 40, base, night)
        draw_dog(strip, 92, base, DOGS[0][1], night, 0.6)           # hound
        draw_critter(strip, 150, base, CRITTERS[1][1], night, 0.4)  # hen
        draw_dog(strip, 208, base, DOGS[2][1], night, 1.1)          # spitz
        draw_critter(strip, 266, base, CRITTERS[2][1], night, 0.8)  # pigeons
        _adult_ref(strip, 336, base, night)
        draw_dog(strip, 388, base, DOGS[1][1], night, 0.3)          # dash
        draw_critter(strip, 446, base, CRITTERS[0][1], night, 0.5)  # cat
        draw_dog(strip, 504, base, DOGS[3][1], night, 0.9)          # shiba
        draw_critter(strip, 560, base, CRITTERS[3][1], night, 0.7)  # duck
        draw_dog(strip, 620, base, DOGS[4][1], night, 0.2)          # droopy long-ear pup
        _adult_ref(strip, 690, base, night)
        _gold_coin(strip, sw - 18, 18)
        _text(strip, "coin ref", sw - 44, 30, 8, _shade(bg, 60))
        _text(strip, "NIGHT" if is_night else "DAY", 4, 2, 9,
              (170, 190, 225) if is_night else (60, 50, 40), bold=True)
        sheet.blit(strip, (PAD, y))
        pygame.draw.rect(sheet, (70, 74, 90), (PAD, y, WIDTH - PAD * 2, strip_h), 1)
        y += strip_h + 6

    # ── cap-audit footer: a REAL measurement scanning the rendered night strip ──
    hottest, over = _measure_night_cap()
    coin_l = _luma((255, 232, 150))
    msg = (f"NIGHT-STRIP CAP (measured on RENDERED pixels across gait phases, not source palette): "
           f"hottest ANIMAL px luma = {hottest:.0f}  ·  px over {NIGHT_GLOW_CAP} = {over}  "
           f"·  gold-coin core luma = {coin_l:.0f} (sole brightest). "
           f"{'PASS — all animal px <= cap.' if over == 0 else 'FAIL — '+str(over)+' px breach the cap.'}")
    _text(sheet, msg, PAD, total_h - 16, 9,
          (170, 200, 180) if over == 0 else (220, 140, 130))

    out = "/home/user/skybit/docs/sidewalk_overhaul/animals/round_2.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("saved", out, sheet.get_size())
    print(f"night-strip cap: hottest animal luma={hottest:.1f}  over-cap px={over}  coin={coin_l:.1f}")


if __name__ == "__main__":
    render()
