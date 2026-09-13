"""Promenade PROPS / STREET FIXTURES — varied recurring street furniture.

Sixth family of the sidewalk overhaul, art-director SHIP-READY
(docs/sidewalk_overhaul/props/round_3.png). 15 designs across 5 prop TYPES, each
one shared drawer fed DATA rows (palette + attrs flags), distinct in silhouette at
far-lane size:
  LAMP/LANTERN  — slim-post / paired / stone-shrine
  BANNER/SIGN   — vertical cloth / pennant string / horizontal signboard
  BRAZIER/FIRE  — tripod / coal-basket / temple censer
  BENCH/SEAT    — stone slab / back-rail / stool
  DRESSING      — produce crates / woven baskets / rolled-mat + sacks

Night-cap contract holds (measured hottest lit-prop 145.8 luma, 0 px over the 150
ceiling, gold coin 229.5 the sole brightest): every lit prop is drawn onto its own
SRCALPHA layer whose COMPOSITE (core glow + coals + the single pre-clamped
BLEND_RGB_ADD halo) is hue-preserving-clamped <=146 before blit, so a core+halo
overlap can never sum past the cap. Non-lit materials cool toward (54,64,96) at
night. Pure-Pygame / pygbag-safe (no numpy/gfxdraw/PIL).
"""
from __future__ import annotations

import math

import pygame

from game import foreground_variants as fv


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
# Author every lit night pixel with a comfortable margin under the ceiling rather
# than a 2-point photo-finish — the director's note. Cores cap here; the additive
# halo budget below keeps the COMPOSITE result under this too.
LIT_NIGHT_CEIL = 142


def _cap_to(col, ceil):
    """Hold a lit colour under `ceil` luma WITHOUT flattening hue (scales toward
    black, preserving the warm ratio that keeps the coin the sole brightest)."""
    y = _luma(col)
    if y <= ceil:
        return col
    k = ceil / y
    return (_clamp(col[0] * k), _clamp(col[1] * k), _clamp(col[2] * k))


def _cap150(col):
    return _cap_to(col, NIGHT_GLOW_CAP)


def _retint(col, night):
    """Cool a non-lit material toward the night ground band (matches
    ped_cast._retint_person / greenery_cast._retint). Warm props keep their hue —
    the pull is partial — but anything still over the cap is pushed harder so no
    highlight out-glows the coin at night."""
    if night <= 0.05:
        return col
    out = _mix(col, (54, 64, 96), min(0.55, 0.40 * night + 0.20))
    if _luma(out) > NIGHT_GLOW_CAP:
        over = (_luma(out) - NIGHT_GLOW_CAP) / max(1.0, 255 - NIGHT_GLOW_CAP)
        out = _mix(out, (66, 76, 104), min(0.78, 0.5 + over))
    return out


def _hi(c, d, night):
    """A highlight d above c, clamped under the cap at night so _shade can't push
    a pale rim past the coin."""
    out = _shade(c, d)
    if night > 0.05 and _luma(out) > NIGHT_GLOW_CAP:
        out = _mix(out, (66, 76, 104), 0.65)
    return out


def _night_lift(col, night, frac):
    """Lift a too-dark material toward a cool grey on NIGHT only so a low dark
    crate/iron leg doesn't merge into the retinted ground band."""
    if night <= 0.05:
        return col
    return _mix(col, (104, 112, 132), frac * night)


# ── lit warmth: rising smoke wisp + PRE-CLAMPED additive halo ──────────────────

def _wisp(surf, x, y0, t, *, n=3, rise=18, spread=2.6, speed=0.55, phase=0.0,
          color=(206, 196, 184), peak_a=46, r0=1, sway=2.2):
    """A rising column of `n` translucent puffs reading as RISING MOTION: each
    puff eases up the full `rise` while fattening + drifting, fading over its top
    third so it dissipates at the crest. Thin warm smoke = low alpha (matches
    food_stalls._wisp)."""
    for i in range(n):
        ph = ((t * speed) + phase + i / n) % 1.0
        climb = 1.0 - (1.0 - ph) * (1.0 - ph)
        yy = y0 - climb * rise
        xx = x + math.sin(ph * math.pi * 1.6 + i * 1.3 + t * 0.7) * sway
        if ph < 0.18:
            a = peak_a * (ph / 0.18)
        else:
            a = peak_a * (1.0 - (ph - 0.18) / 0.82) ** 1.4
        if a < 4:
            continue
        rr = int(r0 + ph * spread)
        d = rr * 2 + 2
        layer = pygame.Surface((d, d), pygame.SRCALPHA)
        pygame.draw.circle(layer, (*color, int(a)), (rr + 1, rr + 1), rr)
        pygame.draw.circle(layer, (*color, int(a * 0.5)), (rr + 1, rr + 1), max(1, rr - 1))
        surf.blit(layer, (int(xx) - rr - 1, int(yy) - rr - 1))


# A conservative additive budget: the night ground band sits at ~50 luma, so an
# additive contribution of <=ADD_BUDGET luma lands the COMPOSITE peak comfortably
# under 148 even where the halo overlaps the brightest deck pixel. We render the
# whole halo into ONE temp surface, measure its peak luma, and scale it down to
# this budget BEFORE the single BLEND_RGB_ADD blit — so summed halos can never
# stack past the ceiling.
ADD_BUDGET = 78


def _warm_halo(surf, cx, cy, *, radius, peak, color):
    """A small warm ember/lantern halo. The ONLY BLEND_RGB_ADD path, and it never
    touches the deck raw.

    pygame's BLEND_RGB_ADD adds the SOURCE RGB channels directly to the destination
    and IGNORES source alpha (this is exactly what made round-1 clip to 243 — raw
    bright RGB stacked onto the deck). So we compute the additive RGB contribution
    we WANT per pixel in a plain float accumulator (the smooth radial falloff),
    then bake that contribution straight into the temp surface's RGB with alpha=255
    and SCALE the whole surface so its peak added luma is <=ADD_BUDGET. The single
    RGB_ADD blit then contributes at most ADD_BUDGET luma; over the ~47-luma night
    ground that lands the lit composite comfortably <=148."""
    col = _cap_to(color, LIT_NIGHT_CEIL)
    d = radius * 2 + 2
    cxr = cyr = radius + 1
    # accumulate the intended additive contribution per pixel (sum of ring falloff)
    acc = [[0.0, 0.0, 0.0] for _ in range(d * d)]
    for rr in range(radius, 0, -1):
        # the same falloff weight round-1 used, but now interpreted as the ADD
        # amount (not an alpha) so the measurement matches what RGB_ADD applies.
        w = peak * (rr / radius) * (1.0 - rr / radius) * 4.0 / 255.0
        if w <= 0:
            continue
        k = rr / radius
        c = (col[0] * (0.5 + 0.5 * (1 - k)),
             col[1] * (0.5 + 0.5 * (1 - k)),
             col[2] * (0.5 + 0.5 * (1 - k)))
        rr2 = rr * rr
        for py in range(d):
            dy = py - cyr
            for px in range(d):
                dx = px - cxr
                if dx * dx + dy * dy <= rr2:
                    cell = acc[py * d + px]
                    cell[0] += c[0] * w
                    cell[1] += c[1] * w
                    cell[2] += c[2] * w
    # find the hottest accumulated pixel and scale the field so it lands <=budget
    peak_add = 0.0
    for cell in acc:
        peak_add = max(peak_add, _luma(cell))
    scale = (ADD_BUDGET / peak_add) if peak_add > ADD_BUDGET else 1.0
    g = pygame.Surface((d, d), pygame.SRCALPHA)
    for py in range(d):
        for px in range(d):
            cell = acc[py * d + px]
            if cell[0] + cell[1] + cell[2] <= 0:
                continue
            g.set_at((px, py), (_clamp(cell[0] * scale), _clamp(cell[1] * scale),
                                _clamp(cell[2] * scale), 255))
    surf.blit(g, (cx - radius - 1, cy - radius - 1), special_flags=pygame.BLEND_RGB_ADD)


def _smoke_col(night):
    return _mix((202, 192, 180), (118, 120, 132), 0.4 + 0.3 * night)


def _lit_face(base, night, *, ceil_day=190):
    """A lantern/censer-glow lit FACE colour: warm by day (held under a soft day
    ceiling so it never rivals the coin in daylight) and HARD-capped at the
    comfortable LIT_NIGHT_CEIL at night — no 255-channel cores. The single place a
    lantern's painted glow is computed."""
    if night <= 0.05:
        out = base
        if _luma(out) > ceil_day:
            out = _mix(out, (150, 120, 80), (_luma(out) - ceil_day) / 90.0)
        return out
    # at night the lit face is dimmed toward a warm ember and capped with a margin
    dim = _mix(base, (110, 64, 38), min(0.62, 0.72 * night))
    return _cap_to(dim, LIT_NIGHT_CEIL)


def _lit_coal(coal_dk, coal_hot, pulse, night):
    """A pulsing coal pixel — warm by day, capped under LIT_NIGHT_CEIL at night so
    even the hottest pulse beat stays clear of the coin."""
    col = _mix(coal_dk, coal_hot, pulse)
    if night > 0.05:
        col = _cap_to(_mix(col, (104, 58, 34), 0.35 * night), LIT_NIGHT_CEIL)
    return col


# ── COMPOSITE night clamp: the round-3 fix ─────────────────────────────────────
#
# Round 2 clamped the lit core and the additive-halo field SEPARATELY, so where the
# warm halo OVERLAPS the globe/coal core the two summed to ~190 on the deck. The fix
# renders each lit prop onto its OWN layer and clamps that layer's COMPOSITE — which
# already contains core + halo summed — to LIT_COMPOSITE_CEIL before blitting. A
# comfortable margin under the 150 ceiling so the audit passes with room to spare.
LIT_COMPOSITE_CEIL = 146


def _clamp_surface_luma(surf, ceil=LIT_COMPOSITE_CEIL):
    """Per-pixel hue-preserving luma clamp on a lit prop's SRCALPHA layer.

    Two jobs, in one pass, so the layer composites correctly AND under the cap:

      1. The additive _warm_halo blits onto this layer with BLEND_RGB_ADD, which
         leaves halo-only pixels with warm RGB but alpha 0. A plain alpha blit would
         drop those, killing the glow ring. So a pixel with RGB but no alpha is given
         an alpha scaled by its luma — recovering the soft additive falloff as an
         alpha-blended warm glow (the brief's bake-the-halo-into-the-temp model).
      2. Any pixel — core, halo, or the core+halo SUM that produced round-2's 190 —
         whose luma exceeds `ceil` has its rgb scaled by ceil/luma (hue preserved).

    Clamping the layer AFTER the additive halo is summed onto it is exactly what
    captures the overlap that the round-2 separate clamps missed."""
    w, h = surf.get_size()
    for px in range(w):
        for py in range(h):
            r, g, b, a = surf.get_at((px, py))
            if a == 0 and (r or g or b):
                # additive-halo-only pixel: recover a soft glow alpha from its luma
                a = _clamp((0.299 * r + 0.587 * g + 0.114 * b) * 1.6 + 30)
            if a == 0:
                continue
            y = 0.299 * r + 0.587 * g + 0.114 * b
            if y > ceil:
                k = ceil / y
                r, g, b = _clamp(r * k), _clamp(g * k), _clamp(b * k)
            surf.set_at((px, py), (r, g, b, a))


# A generous bounding box around any prop (authored feet-on-base_y, grows UP, with
# halo + smoke margins). Oversizing is safe: clamping skips transparent pixels and
# only scales the rare hotspot, so the layer composites pixel-identical to a direct
# draw everywhere except the over-cap overlap it is there to fix.
_LIT_MARGIN_X = 44
_LIT_MARGIN_UP = 104
_LIT_MARGIN_DOWN = 10


def _night_clamped(drawer):
    """Wrap a per-type drawer so that at NIGHT its whole drawing — core glow faces,
    coals AND the additive _warm_halo — lands on its own SRCALPHA layer, gets the
    composite luma clamp, then blits to the deck. By day it draws straight through,
    so the day appearance is byte-identical to round 2. This is the ONLY behavioural
    change in round 3 and it lives entirely in the night lighting-composite path."""
    def _wrapped(surf, cx, base_y, v, night, t):
        if night <= 0.05:
            return drawer(surf, cx, base_y, v, night, t)
        ox = _LIT_MARGIN_X
        oy = _LIT_MARGIN_UP
        layer = pygame.Surface((_LIT_MARGIN_X * 2, _LIT_MARGIN_UP + _LIT_MARGIN_DOWN),
                               pygame.SRCALPHA)
        # draw the prop into the layer's local frame (its additive halo also lands
        # here, so the clamp below sees the true core+halo composite)
        drawer(layer, ox, oy, v, night, t)
        _clamp_surface_luma(layer)
        surf.blit(layer, (int(cx) - ox, int(base_y) - oy))
    _wrapped.__name__ = getattr(drawer, "__name__", "drawer")
    return _wrapped


# ════════════════════════════════════════════════════════════════════════════
# Shared per-TYPE drawers. Each consumes a Variant-style row (palette + attrs)
# and is authored feet-on-`base_y`, prop grows UP. Variety is the attrs enum
# picking a silhouette + the palette roles, never a bespoke per-item function.
#
# attrs families:
#   lamp:    style='post'|'paired'|'shrine'  height  globe='red'|'gold'  finial(bool)
#   banner:  style='cloth'|'pennant'|'signboard'   marks(int)  ncolor pennants
#   fire:    style='tripod'|'basket'|'censer'
#   bench:   style='stone'|'backrail'|'stool'
#   dress:   style='crates'|'baskets'|'jars'|'sacks'
# ════════════════════════════════════════════════════════════════════════════


# ── LAMP / LANTERN ────────────────────────────────────────────────────────────
#
# A slim dark post topped with a lit head. Tall (~62-92px). palette roles:
#   post, post_dk, finial(gold accent), globe_red, globe_gold, stone(shrine).

def _lantern_globe(surf, cx, cy, v, night, *, color, scale=1.0, glow_r=9, glow_peak=42):
    """A hanging paper-lantern globe with a PRE-CLAMPED warm halo at night + a soft
    day glow ceiling. The face is dimmed HARD at night (via _lit_face) so face +
    halo stay under the coin."""
    P = v.palette
    if color == "red":
        dark_base = P.get("globe_red_dk", (170, 40, 42))
        face_base = P.get("globe_red", (228, 92, 70))
        halo = (236, 138, 100)
    else:
        dark_base = P.get("globe_gold_dk", (190, 140, 44))
        face_base = P.get("globe_gold", (244, 206, 104))
        halo = (236, 192, 112)
    dark = _retint(dark_base, night) if night > 0.05 else dark_base
    face = _lit_face(face_base, night)
    lw, lh = max(8, int(14 * scale)), max(10, int(18 * scale))
    cap = max(2, int(3 * scale))
    body = pygame.Rect(cx - lw // 2, cy + cap - 1, lw, lh - 2 * cap + 2)
    fitting = _retint((58, 38, 26), night)
    pygame.draw.rect(surf, fitting, (cx - lw // 2 + 1, cy, lw - 2, cap))
    pygame.draw.rect(surf, fitting, (cx - lw // 2 + 1, cy + lh - cap, lw - 2, cap))
    pygame.draw.ellipse(surf, dark, body)
    pygame.draw.ellipse(surf, face, body.inflate(-max(2, int(3 * scale)), -max(1, int(2 * scale))))
    # a vertical seam rib so it reads as a ribbed paper globe, not a plain blob
    pygame.draw.line(surf, _shade(dark, -10), (cx, body.top + 1), (cx, body.bottom - 1), 1)
    if night > 0.05:
        _warm_halo(surf, cx, cy + lh // 2, radius=glow_r, peak=glow_peak, color=halo)


def draw_lamp(surf, cx, base_y, v, night, t):
    P, A = v.palette, v.attrs
    style = A.get("style", "post")
    height = A.get("height", 88)
    g = int(base_y)
    top_y = g - height
    post = _retint(P.get("post", (54, 48, 46)), night)
    post = _night_lift(post, night, 0.18)
    post_dk = _shade(post, -16)
    post_lt = _hi(post, 18, night)
    pw = 3

    if style == "shrine":
        # Carved STONE pedestal lantern (shrine-style): a stepped stone base, a
        # short shaft, a wide stone cap, and a small lit lantern box under a
        # pagoda-like roof — a stout, grounded silhouette unlike the slim post.
        stone = _night_lift(_retint(P.get("stone", (162, 150, 130)), night), night, 0.10)
        stone_dk = _shade(stone, -26)
        stone_lt = _hi(stone, 16, night)
        bw = 18
        # stepped base
        pygame.draw.rect(surf, stone_dk, (cx - bw // 2, g - 5, bw, 5))
        pygame.draw.rect(surf, stone, (cx - bw // 2 + 1, g - 5, bw - 2, 4))
        pygame.draw.rect(surf, stone_lt, (cx - bw // 2 + 1, g - 5, bw - 2, 1))
        # shaft
        sh_top = top_y + 22
        pygame.draw.rect(surf, stone_dk, (cx - 4, sh_top, 8, g - 5 - sh_top))
        pygame.draw.rect(surf, stone, (cx - 3, sh_top, 6, g - 5 - sh_top))
        pygame.draw.line(surf, stone_lt, (cx - 3, sh_top), (cx - 3, g - 6), 1)
        # mid platform under the light box
        pygame.draw.rect(surf, stone_dk, (cx - 9, top_y + 16, 18, 4))
        pygame.draw.rect(surf, stone, (cx - 8, top_y + 16, 16, 3))
        # the lit light-box (four-pane stone lantern fire-box)
        box = pygame.Rect(cx - 7, top_y + 6, 14, 10)
        face = _lit_face(P.get("globe_gold", (244, 206, 104)), night, ceil_day=176)
        pygame.draw.rect(surf, stone_dk, box)
        pygame.draw.rect(surf, _mix(face, stone, 0.25), box.inflate(-3, -3))
        pygame.draw.line(surf, stone_dk, (cx, box.top), (cx, box.bottom), 1)
        pygame.draw.line(surf, stone_dk, (box.left, box.centery), (box.right, box.centery), 1)
        # flared pagoda cap
        pygame.draw.polygon(surf, stone_dk, [
            (cx - 11, top_y + 6), (cx + 11, top_y + 6), (cx + 6, top_y), (cx - 6, top_y)])
        pygame.draw.polygon(surf, stone, [
            (cx - 10, top_y + 5), (cx + 10, top_y + 5), (cx + 5, top_y + 1), (cx - 5, top_y + 1)])
        pygame.draw.circle(surf, stone_lt, (cx, top_y), 2)
        if night > 0.05:
            _warm_halo(surf, cx, box.centery, radius=10, peak=34, color=(232, 192, 116))
        return

    # slim wrought-iron / lacquer post (the merged single-post lamp).
    pygame.draw.rect(surf, post_dk, (cx - pw, g - 5, pw * 2, 5))   # foot block
    pygame.draw.rect(surf, post_lt, (cx - pw, g - 5, pw * 2, 1))
    pygame.draw.rect(surf, post, (cx - pw // 2, top_y + 6, max(2, pw - 1), g - 5 - (top_y + 6)))
    pygame.draw.line(surf, post_lt, (cx - pw // 2, top_y + 6), (cx - pw // 2, g - 6), 1)

    if style == "paired":
        # a horizontal cross-arm carrying two globes, one each side
        arm_y = top_y + 9
        pygame.draw.line(surf, post, (cx - 11, arm_y), (cx + 11, arm_y), 2)
        pygame.draw.line(surf, post_dk, (cx - 11, arm_y + 1), (cx + 11, arm_y + 1), 1)
        pygame.draw.circle(surf, _hi(post, 12, night), (cx, top_y + 4), 2)
        for sgn in (-1, 1):
            pygame.draw.line(surf, post, (cx + sgn * 11, arm_y), (cx + sgn * 11, arm_y + 3), 1)
            _lantern_globe(surf, cx + sgn * 11, arm_y + 3, v, night,
                           color=A.get("globe", "red"), scale=0.72, glow_r=7, glow_peak=30)
    else:  # 'post' — single slim-post lamp (the DEFAULT, merged from old L1+L3).
        # Default red paper globe on a scroll hook; an optional GOLD finial cap +
        # gold globe folds the old ornate post in as a palette/attrs accent so the
        # two redundant slim posts are now ONE drawer path.
        globe = A.get("globe", "red")
        pygame.draw.arc(surf, post, (cx - 8, top_y + 4, 16, 12),
                        math.radians(20), math.radians(160), 2)
        if A.get("finial"):
            fin = _retint(P.get("finial", (198, 162, 70)), night)
            fin_lt = _hi(fin, 22, night)
            pygame.draw.circle(surf, fin, (cx, top_y + 2), 3)
            pygame.draw.circle(surf, fin_lt, (cx - 1, top_y + 1), 1)
            pygame.draw.line(surf, fin, (cx, top_y - 2), (cx, top_y + 2), 2)
        else:
            pygame.draw.circle(surf, _hi(post, 12, night), (cx, top_y + 3), 2)
        _lantern_globe(surf, cx, top_y + 8, v, night, color=globe,
                       scale=0.82, glow_r=9, glow_peak=38)


# ── BANNER / SIGN ───────────────────────────────────────────────────────────
#
# Hanging shop signage. palette roles: cloth, cloth_dk, ink(marks), pole,
#   pennant_a, pennant_b. Cloth cools toward (54,64,96) at night via _retint.

def draw_banner(surf, cx, base_y, v, night, t):
    P, A = v.palette, v.attrs
    style = A.get("style", "cloth")
    g = int(base_y)
    pole = _retint(P.get("pole", (92, 64, 40)), night)
    pole = _night_lift(pole, night, 0.16)
    pole_dk = _shade(pole, -20)
    sway = math.sin(t * 1.5) * 0.8

    if style == "cloth":
        # Vertical hanging shop-cloth banner: a tall narrow cloth on a top crossbar
        # with abstract vertical calligraphy ink marks. The tall thin silhouette.
        cloth = _retint(P.get("cloth", (188, 70, 62)), night)
        cloth_dk = _shade(cloth, -28)
        cloth_lt = _hi(cloth, 16, night)
        ink = _retint(P.get("ink", (40, 30, 26)), night)
        bw, bh = 13, 46
        top_y = g - bh - 6
        # crossbar + finials
        pygame.draw.line(surf, pole, (cx - bw // 2 - 4, top_y - 2), (cx + bw // 2 + 4, top_y - 2), 2)
        pygame.draw.circle(surf, _hi(pole, 16, night), (cx - bw // 2 - 4, top_y - 2), 2)
        pygame.draw.circle(surf, _hi(pole, 16, night), (cx + bw // 2 + 4, top_y - 2), 2)
        # cloth body — a slight sway at the bottom hem for fabric life
        hem_dx = int(sway * 2)
        body = [(cx - bw // 2, top_y), (cx + bw // 2, top_y),
                (cx + bw // 2 + hem_dx, g), (cx - bw // 2 + hem_dx, g)]
        pygame.draw.polygon(surf, cloth_dk, body)
        inner = [(cx - bw // 2 + 1, top_y + 1), (cx + bw // 2 - 1, top_y + 1),
                 (cx + bw // 2 - 1 + hem_dx, g - 1), (cx - bw // 2 + 1 + hem_dx, g - 1)]
        pygame.draw.polygon(surf, cloth, inner)
        pygame.draw.line(surf, cloth_lt, (cx - bw // 2 + 1, top_y + 1),
                         (cx - bw // 2 + 1 + hem_dx, g - 1), 1)
        # abstract calligraphy: a column of short ink strokes (glyph dabs)
        marks = A.get("marks", 4)
        for m in range(marks):
            my = top_y + 5 + m * (bh - 8) // marks + int(sway * (m / marks))
            mx = cx + int(sway * (m / marks))
            pygame.draw.line(surf, ink, (mx - 3, my), (mx + 3, my), 1)
            pygame.draw.line(surf, ink, (mx, my - 2), (mx, my + 3), 1)
            if m % 2 == 0:
                pygame.draw.line(surf, ink, (mx - 2, my + 3), (mx + 2, my + 3), 1)
        # scalloped hem
        pygame.draw.polygon(surf, cloth_dk, [
            (cx - bw // 2 + hem_dx, g), (cx + bw // 2 + hem_dx, g),
            (cx + bw // 2 - 2 + hem_dx, g + 2), (cx + hem_dx, g),
            (cx - bw // 2 + 2 + hem_dx, g + 2)])

    elif style == "pennant":
        # Triangular PENNANT string: a sagging cord between two short poles strung
        # with alternating colour flags — the festival bunting silhouette.
        pa = _retint(P.get("pennant_a", (196, 80, 66)), night)
        pb = _retint(P.get("pennant_b", (200, 168, 78)), night)
        span = 46
        top_y = g - 40
        # two short poles
        for sgn in (-1, 1):
            px = cx + sgn * span // 2
            pygame.draw.line(surf, pole, (px, g), (px, top_y), 2)
            pygame.draw.line(surf, pole_dk, (px + 1, g), (px + 1, top_y), 1)
            pygame.draw.circle(surf, _hi(pole, 14, night), (px, top_y), 2)
        # sagging cord (quadratic)
        x1, x2 = cx - span // 2, cx + span // 2
        sag = 7
        pts = []
        for i in range(13):
            tt = i / 12
            bx = (1 - tt) ** 2 * x1 + 2 * (1 - tt) * tt * cx + tt * tt * x2
            by = (1 - tt) ** 2 * top_y + 2 * (1 - tt) * tt * (top_y + sag) + tt * tt * top_y
            pts.append((bx, by))
        pygame.draw.lines(surf, _retint((70, 58, 46), night), False,
                          [(int(x), int(y)) for x, y in pts], 1)
        # hang triangular flags along the cord
        nflag = A.get("flags", 6)
        for f in range(nflag):
            tt = (f + 0.5) / nflag
            bx = (1 - tt) ** 2 * x1 + 2 * (1 - tt) * tt * cx + tt * tt * x2
            by = (1 - tt) ** 2 * top_y + 2 * (1 - tt) * tt * (top_y + sag) + tt * tt * top_y
            bx, by = int(bx), int(by)
            flut = int(math.sin(t * 2.4 + f * 1.2) * 1.0)
            col = pa if f % 2 == 0 else pb
            pygame.draw.polygon(surf, _shade(col, -22), [
                (bx - 3, by), (bx + 3, by), (bx + flut, by + 7)])
            pygame.draw.polygon(surf, col, [
                (bx - 2, by + 1), (bx + 2, by + 1), (bx + flut, by + 5)])

    else:  # 'signboard' — horizontal board on two posts
        board = _retint(P.get("cloth", (150, 110, 64)), night)
        board_dk = _shade(board, -26)
        board_lt = _hi(board, 16, night)
        ink = _retint(P.get("ink", (236, 224, 196)), night)
        bw, bh = 40, 13
        top_y = g - 30
        # two posts
        for sgn in (-1, 1):
            px = cx + sgn * (bw // 2 - 3)
            pygame.draw.rect(surf, pole, (px - 1, top_y, 3, g - top_y))
            pygame.draw.line(surf, pole_dk, (px + 1, top_y), (px + 1, g - 1), 1)
        # board
        pygame.draw.rect(surf, board_dk, (cx - bw // 2, top_y - bh, bw, bh))
        pygame.draw.rect(surf, board, (cx - bw // 2 + 1, top_y - bh + 1, bw - 2, bh - 2))
        pygame.draw.rect(surf, board_lt, (cx - bw // 2 + 1, top_y - bh + 1, bw - 2, 1))
        # gilt edge frame
        pygame.draw.rect(surf, _retint(P.get("finial", (198, 162, 70)), night),
                         (cx - bw // 2 + 1, top_y - bh + 1, bw - 2, bh - 2), 1)
        # carved signage: TWO CHUNKY blocks (not a noisy glyph row) — reads as a
        # bold two-character shop sign at 1x rather than scratchy strokes.
        block_w = 9
        gap = 6
        total = 2 * block_w + gap
        bx0 = cx - total // 2
        my = top_y - bh + 3
        bh2 = bh - 6
        for bi in range(2):
            bx = bx0 + bi * (block_w + gap)
            pygame.draw.rect(surf, ink, (bx, my, block_w, bh2))
            # a single notch carved out so the block reads as a character, not a bar
            pygame.draw.line(surf, board, (bx + 2, my + bh2 // 2),
                             (bx + block_w - 3, my + bh2 // 2), 1)
            if bi == 0:
                pygame.draw.line(surf, board, (bx + block_w // 2, my + 1),
                                 (bx + block_w // 2, my + bh2 - 2), 1)


# ── BRAZIER / FIRE ──────────────────────────────────────────────────────────
#
# A warm fire fixture with a small capped ember + a thin rising smoke wisp.
# palette roles: metal, metal_dk, coal, ash, brass(censer). Embers capped.

def draw_fire(surf, cx, base_y, v, night, t):
    P, A = v.palette, v.attrs
    style = A.get("style", "tripod")
    g = int(base_y)
    metal = _night_lift(_retint(P.get("metal", (64, 60, 62)), night), night, 0.16)
    metal_dk = _shade(metal, -18)
    metal_lt = _hi(metal, 16, night)
    coal_hot = P.get("coal", (150, 86, 38))
    coal_dk = _shade(coal_hot, -36)
    smoke = _smoke_col(night)

    if style == "tripod":
        # Tripod brazier: a shallow fire-bowl on three splayed legs — the classic
        # archaic censer/brazier silhouette (three legs read clearly at far size).
        bowl_y = g - 13
        for lx in (-7, 0, 7):
            pygame.draw.line(surf, metal_dk, (cx + lx, g), (cx + (lx // 2 if lx else 0), bowl_y + 2), 2)
            pygame.draw.line(surf, metal, (cx + lx, g - 1), (cx + (lx // 2 if lx else 0), bowl_y + 2), 1)
        bowl = pygame.Rect(cx - 10, bowl_y - 4, 20, 8)
        pygame.draw.ellipse(surf, metal_dk, bowl)
        pygame.draw.ellipse(surf, metal, bowl.inflate(-2, -3))
        pygame.draw.arc(surf, metal_lt, bowl, math.radians(20), math.radians(150), 1)
        rim = pygame.Rect(cx - 8, bowl_y - 4, 16, 4)
        pygame.draw.ellipse(surf, _retint((40, 30, 30), night), rim)
        if night > 0.05:
            _warm_halo(surf, cx, bowl_y - 2, radius=10, peak=46, color=(150, 84, 40))
        for j, kx in enumerate((-4, 0, 4)):
            pulse = 0.55 + 0.45 * math.sin(t * 3.0 + j * 1.9)
            col = _lit_coal(coal_dk, coal_hot, pulse, night)
            pygame.draw.circle(surf, col, (cx + kx, bowl_y - 2), 1)
        _wisp(surf, cx, bowl_y - 3, t, n=3, rise=22, spread=2.4, speed=0.6,
              phase=0.0, peak_a=42, r0=1, sway=2.6, color=smoke)

    elif style == "basket":
        # Low coal BASKET: a wide squat iron cage of vertical bars over a coal bed
        # — the broadest, lowest fire silhouette.
        bw = 22
        top_y = g - 12
        pygame.draw.ellipse(surf, metal_dk, (cx - bw // 2, g - 5, bw, 5))
        pygame.draw.ellipse(surf, metal, (cx - bw // 2 + 1, g - 5, bw - 2, 4))
        for bx in range(cx - bw // 2 + 1, cx + bw // 2, 3):
            pygame.draw.line(surf, metal, (bx, g - 3), (bx + (cx - bx) // 8, top_y), 1)
        pygame.draw.ellipse(surf, metal_dk, (cx - bw // 2 + 2, top_y - 3, bw - 4, 6))
        pygame.draw.ellipse(surf, metal, (cx - bw // 2 + 3, top_y - 3, bw - 6, 5), 1)
        if night > 0.05:
            _warm_halo(surf, cx, top_y, radius=11, peak=48, color=(150, 84, 40))
        for j, kx in enumerate((-5, 0, 5, -2, 3)):
            pulse = 0.5 + 0.5 * math.sin(t * 3.2 + j * 1.5)
            col = _lit_coal(coal_dk, coal_hot, pulse, night)
            pygame.draw.circle(surf, col, (cx + kx, top_y - 1), 1)
        _wisp(surf, cx - 3, top_y - 2, t, n=2, rise=18, spread=2.2, speed=0.62,
              phase=0.0, peak_a=38, r0=1, sway=2.4, color=smoke)
        _wisp(surf, cx + 4, top_y - 2, t, n=2, rise=16, spread=2.0, speed=0.7,
              phase=0.4, peak_a=32, r0=1, sway=2.2, color=smoke)

    else:  # 'censer' — tall temple incense burner
        # Tall bronze CENSER: a footed bowl, a swollen belly, a necked-in lid with
        # a domed knob and side handles — the tallest, most vertical fire prop.
        brass = _night_lift(_retint(P.get("brass", (176, 142, 78)), night), night, 0.12)
        brass_dk = _shade(brass, -34)
        brass_lt = _hi(brass, 22, night)
        pygame.draw.rect(surf, brass_dk, (cx - 5, g - 4, 10, 4))
        pygame.draw.rect(surf, brass, (cx - 4, g - 4, 8, 3))
        pygame.draw.rect(surf, brass, (cx - 2, g - 9, 4, 5))
        belly = pygame.Rect(cx - 9, g - 22, 18, 14)
        pygame.draw.ellipse(surf, brass_dk, belly)
        pygame.draw.ellipse(surf, brass, belly.inflate(-2, -2))
        pygame.draw.arc(surf, brass_lt, belly, math.radians(30), math.radians(110), 1)
        for sgn in (-1, 1):
            pygame.draw.arc(surf, brass_dk, (cx + sgn * 8 - 2, g - 20, 5, 8),
                            math.radians(60 if sgn > 0 else 300),
                            math.radians(300 if sgn > 0 else 60), 1)
        pygame.draw.ellipse(surf, brass_dk, (cx - 8, g - 24, 16, 5))
        pygame.draw.ellipse(surf, brass, (cx - 7, g - 24, 14, 4))
        pygame.draw.ellipse(surf, brass_dk, (cx - 4, g - 28, 8, 5))
        pygame.draw.ellipse(surf, brass, (cx - 3, g - 28, 6, 4))
        pygame.draw.circle(surf, brass_lt, (cx, g - 28), 1)
        if night > 0.05:
            # the round-1 offender: a 255-channel core under a raw additive halo.
            # now a low pre-clamped halo + a capped warm-ember core colour.
            _warm_halo(surf, cx, g - 26, radius=7, peak=26, color=(214, 150, 88))
            pygame.draw.circle(surf, _cap_to((214, 150, 88), LIT_NIGHT_CEIL), (cx, g - 27), 1)
        _wisp(surf, cx, g - 28, t, n=3, rise=24, spread=2.0, speed=0.5,
              phase=0.0, peak_a=44, r0=1, sway=2.8, color=smoke)


# ── BENCH / SEAT ──────────────────────────────────────────────────────────────
#
# A low seat (~12-20px). palette roles: wood, wood_dk, stone(stone bench).
# Day-neutral; cools with the stage at night.

def draw_bench(surf, cx, base_y, v, night, t):
    P, A = v.palette, v.attrs
    style = A.get("style", "stone")
    g = int(base_y)

    if style == "stone":
        # Stone bench: a thick slab seat on two solid stone block legs — the
        # heaviest, blockiest seat.
        stone = _night_lift(_retint(P.get("stone", (158, 148, 130)), night), night, 0.10)
        stone_dk = _shade(stone, -24)
        stone_lt = _hi(stone, 16, night)
        bw = 30
        seat_y = g - 9
        for lx in (-bw // 2 + 2, bw // 2 - 5):
            pygame.draw.rect(surf, stone_dk, (cx + lx, seat_y, 4, 9))
            pygame.draw.rect(surf, stone, (cx + lx, seat_y, 3, 8))
        pygame.draw.rect(surf, stone_dk, (cx - bw // 2, seat_y - 4, bw, 5))
        pygame.draw.rect(surf, stone, (cx - bw // 2 + 1, seat_y - 4, bw - 2, 4))
        pygame.draw.rect(surf, stone_lt, (cx - bw // 2 + 1, seat_y - 4, bw - 2, 1))

    elif style == "backrail":
        # Back-rail bench: a wood plank seat PLUS a slatted back rail — the tallest
        # seat, reads as a proper park bench (now the default plank seat too, since
        # the redundant plain bench was cut).
        wood = _night_lift(_retint(P.get("wood", (120, 84, 46)), night), night, 0.14)
        wood_dk = _shade(wood, -28)
        wood_lt = _hi(wood, 18, night)
        bw = 30
        seat_y = g - 8
        for lx in (-bw // 2 + 3, bw // 2 - 5):
            pygame.draw.rect(surf, wood_dk, (cx + lx, seat_y, 3, 8))
        pygame.draw.rect(surf, wood_dk, (cx - bw // 2, seat_y - 3, bw, 3))
        pygame.draw.rect(surf, wood, (cx - bw // 2 + 1, seat_y - 3, bw - 2, 2))
        back_top = seat_y - 13
        for lx in (-bw // 2 + 3, bw // 2 - 5):
            pygame.draw.rect(surf, wood_dk, (cx + lx, back_top, 2, 10))
        for ry in (back_top + 1, back_top + 5):
            pygame.draw.rect(surf, wood, (cx - bw // 2 + 2, ry, bw - 4, 2))
            pygame.draw.line(surf, wood_lt, (cx - bw // 2 + 2, ry), (cx + bw // 2 - 3, ry), 1)

    else:  # 'stool' — low round drum stool, the smallest seat
        wood = _night_lift(_retint(P.get("wood", (130, 92, 52)), night), night, 0.14)
        wood_dk = _shade(wood, -26)
        wood_lt = _hi(wood, 16, night)
        bw = 12
        seat_y = g - 7
        pygame.draw.rect(surf, wood_dk, (cx - bw // 2, seat_y, bw, 7))
        pygame.draw.rect(surf, wood, (cx - bw // 2 + 1, seat_y, bw - 2, 6))
        pygame.draw.ellipse(surf, wood_dk, (cx - bw // 2, seat_y - 3, bw, 5))
        pygame.draw.ellipse(surf, wood, (cx - bw // 2 + 1, seat_y - 3, bw - 2, 4))
        pygame.draw.arc(surf, wood_lt, (cx - bw // 2 + 1, seat_y - 3, bw - 2, 4),
                        math.radians(20), math.radians(150), 1)


# ── DRESSING PROPS ──────────────────────────────────────────────────────────
#
# Low market clutter (~12-26px) that fills the deck. palette roles: wood,
#   wood_dk, weave(basket), clay(jar), sack, mat. Beat: all-day market.

def draw_dressing(surf, cx, base_y, v, night, t):
    P, A = v.palette, v.attrs
    style = A.get("style", "crates")
    g = int(base_y)

    if style == "crates":
        # Stacked produce CRATES: two slatted wooden crates, the top one offset,
        # with a peek of produce — a boxy, orthogonal stack.
        wood = _night_lift(_retint(P.get("wood", (146, 104, 62)), night), night, 0.14)
        wood_dk = _shade(wood, -28)
        wood_lt = _hi(wood, 16, night)
        prod = _retint(P.get("clay", (176, 120, 70)), night)
        bw, bh = 22, 10
        pygame.draw.rect(surf, wood_dk, (cx - bw // 2, g - bh, bw, bh))
        pygame.draw.rect(surf, wood, (cx - bw // 2 + 1, g - bh + 1, bw - 2, bh - 2))
        for sxp in range(cx - bw // 2 + 3, cx + bw // 2 - 1, 4):
            pygame.draw.line(surf, wood_dk, (sxp, g - bh + 1), (sxp, g - 2), 1)
        pygame.draw.line(surf, wood_lt, (cx - bw // 2 + 1, g - bh + 1), (cx + bw // 2 - 2, g - bh + 1), 1)
        tw, th = 16, 9
        tx = cx - tw // 2 + 4
        ty = g - bh - th
        pygame.draw.rect(surf, wood_dk, (tx, ty, tw, th))
        pygame.draw.rect(surf, wood, (tx + 1, ty + 1, tw - 2, th - 2))
        for sxp in range(tx + 2, tx + tw - 1, 4):
            pygame.draw.line(surf, wood_dk, (sxp, ty + 1), (sxp, ty + th - 2), 1)
        for px in (tx + 4, tx + 9, tx + 12):
            pygame.draw.circle(surf, prod, (px, ty + 1), 1)
            pygame.draw.circle(surf, _shade(prod, 18), (px, ty), 0)

    elif style == "baskets":
        # Woven BASKET cluster: three round bellied baskets of CLEARLY different
        # height, each with a flared woven-RIM notch (a darker lip stepping proud
        # of the body) so they read as open baskets, not generic round blobs.
        weave = _night_lift(_retint(P.get("weave", (172, 138, 86)), night), night, 0.14)
        weave_dk = _shade(weave, -32)
        weave_lt = _hi(weave, 18, night)
        # tall / short / mid — pronounced height variance
        for dx, bw, bh in ((-8, 11, 17), (5, 12, 9), (1, 8, 13)):
            bx = cx + dx
            body = pygame.Rect(bx - bw // 2, g - bh, bw, bh)
            pygame.draw.ellipse(surf, weave_dk, body)
            pygame.draw.ellipse(surf, weave, body.inflate(-2, -2))
            # horizontal weave courses
            for wy in range(g - bh + 3, g - 1, 3):
                pygame.draw.line(surf, weave_dk, (bx - bw // 2 + 1, wy), (bx + bw // 2 - 1, wy), 1)
            pygame.draw.arc(surf, weave_lt, body, math.radians(40), math.radians(120), 1)
            # woven-RIM notch: a flared lip wider than the body + a dark inner mouth
            # so the basket reads as open, with a clear rim step (the director note).
            rim_w = bw + 2
            pygame.draw.ellipse(surf, weave_dk, (bx - rim_w // 2, g - bh - 2, rim_w, 5))
            pygame.draw.ellipse(surf, weave, (bx - rim_w // 2 + 1, g - bh - 2, rim_w - 2, 4))
            pygame.draw.ellipse(surf, _shade(weave_dk, -10), (bx - bw // 2 + 1, g - bh - 1, bw - 2, 3))
            pygame.draw.arc(surf, weave_lt, (bx - rim_w // 2, g - bh - 2, rim_w, 5),
                            math.radians(200), math.radians(340), 1)

    elif style == "jars":
        # Stacked BARREL / urn JAR set: a fat clay jar with a roped neck + a small
        # barrel beside it — a bulbous ceramic clutter.
        clay = _night_lift(_retint(P.get("clay", (158, 116, 80)), night), night, 0.12)
        clay_dk = _shade(clay, -30)
        clay_lt = _hi(clay, 16, night)
        wood = _night_lift(_retint(P.get("wood", (132, 94, 54)), night), night, 0.14)
        wood_dk = _shade(wood, -26)
        jx = cx - 4
        belly = pygame.Rect(jx - 8, g - 18, 16, 18)
        pygame.draw.ellipse(surf, clay_dk, belly)
        pygame.draw.ellipse(surf, clay, belly.inflate(-2, -2))
        pygame.draw.arc(surf, clay_lt, belly, math.radians(40), math.radians(120), 1)
        pygame.draw.rect(surf, clay, (jx - 4, g - 21, 8, 4))
        pygame.draw.ellipse(surf, clay_dk, (jx - 5, g - 22, 10, 4))
        pygame.draw.ellipse(surf, _shade(clay, -8), (jx - 4, g - 21, 8, 2))
        pygame.draw.line(surf, _retint((150, 120, 70), night), (jx - 4, g - 19), (jx + 4, g - 19), 1)
        bx = cx + 9
        bw, bh = 11, 12
        pygame.draw.ellipse(surf, wood_dk, (bx - bw // 2, g - bh, bw, bh))
        pygame.draw.ellipse(surf, wood, (bx - bw // 2 + 1, g - bh, bw - 2, bh - 1))
        for hy in (g - bh + 3, g - 3):
            pygame.draw.arc(surf, _shade(wood, -36), (bx - bw // 2, hy - 3, bw, 6),
                            math.radians(200), math.radians(340), 2)

    else:  # 'sacks' — rolled mat + sack pile
        # Rolled MAT + grain SACK pile: a couple of slumped sacks and a rolled
        # bamboo mat standing beside them. The mat now has a crisp END-CIRCLE on
        # top so it reads unambiguously as a ROLL, not a lump (the director note).
        sack = _night_lift(_retint(P.get("sack", (168, 150, 112)), night), night, 0.14)
        sack_dk = _shade(sack, -28)
        sack_lt = _hi(sack, 14, night)
        mat = _night_lift(_retint(P.get("mat", (176, 148, 92)), night), night, 0.14)
        mat_dk = _shade(mat, -30)
        mat_lt = _hi(mat, 16, night)
        for dx, sw, sh in ((-7, 13, 13), (3, 12, 11)):
            sx = cx + dx
            body = pygame.Rect(sx - sw // 2, g - sh, sw, sh)
            pygame.draw.ellipse(surf, sack_dk, body)
            pygame.draw.ellipse(surf, sack, body.inflate(-2, -2))
            pygame.draw.line(surf, sack_dk, (sx - 2, g - sh), (sx + 2, g - sh - 2), 2)
            pygame.draw.line(surf, sack_dk, (sx + 2, g - sh), (sx - 2, g - sh - 2), 2)
            pygame.draw.arc(surf, sack_lt, body, math.radians(50), math.radians(120), 1)
        # rolled mat standing at the right: a near-vertical cylinder with a crisp
        # flat END-CIRCLE crowning the top + concentric spiral so it reads as a roll.
        mx = cx + 11
        mh = 18
        # cylinder body (a tight tube)
        pygame.draw.rect(surf, mat_dk, (mx - 3, g - mh, 6, mh))
        pygame.draw.rect(surf, mat, (mx - 2, g - mh, 4, mh - 1))
        pygame.draw.line(surf, mat_lt, (mx - 2, g - mh + 1), (mx - 2, g - 2), 1)
        # crisp circular roll-end on top
        end = pygame.Rect(mx - 4, g - mh - 3, 8, 7)
        pygame.draw.ellipse(surf, mat_dk, end)
        pygame.draw.ellipse(surf, mat, end.inflate(-2, -2))
        pygame.draw.ellipse(surf, _shade(mat_dk, -8), (mx - 1, g - mh, 3, 2))
        pygame.draw.arc(surf, mat_lt, end, math.radians(30), math.radians(150), 1)


# Route every type drawer through the NIGHT composite clamp. Day is unchanged; at
# night the whole prop (core glow + coals + additive halo) is clamped as a single
# composite layer so a core+halo overlap can no longer sum past the cap. The data
# rows and the on-street composite below all reference these wrapped names, so the
# clamp covers EVERY lit-prop draw site uniformly.
draw_lamp = _night_clamped(draw_lamp)
draw_banner = _night_clamped(draw_banner)
draw_fire = _night_clamped(draw_fire)
draw_bench = _night_clamped(draw_bench)
draw_dressing = _night_clamped(draw_dressing)


# ── the 15-design pools → foreground_variants rows (palette + attrs) ───────────

_IRON = dict(post=(54, 48, 46))
_LACQUER = dict(post=(120, 40, 40))
_STONE_L = dict(stone=(162, 150, 130))
_GLOBE = dict(globe_red=(228, 92, 70), globe_red_dk=(170, 40, 42),
              globe_gold=(244, 206, 104), globe_gold_dk=(190, 140, 44))
_CLOTH_RED = dict(cloth=(190, 70, 60), ink=(40, 28, 24), pole=(92, 64, 40))
_PENNANT = dict(pennant_a=(196, 80, 66), pennant_b=(202, 170, 80), pole=(96, 70, 44))
_SIGN = dict(cloth=(140, 100, 58), ink=(232, 220, 192), finial=(200, 164, 72), pole=(86, 60, 38))
_BRAZ = dict(metal=(64, 60, 62), coal=(150, 86, 38))
_BRASS = dict(metal=(64, 60, 62), brass=(176, 142, 78), coal=(150, 86, 38))
_STONE_BENCH = dict(stone=(158, 148, 130))
_CRATE = dict(wood=(146, 104, 62), clay=(176, 120, 70))
_BASKET = dict(weave=(172, 138, 86))
_SACKS = dict(sack=(168, 150, 112), mat=(176, 148, 92))


def _row(*banks, **attrs):
    pal = {}
    for b in banks:
        pal.update(b)
    return fv.Variant(palette=pal, attrs=dict(attrs))


# Each prop TYPE is its own pool; the wrapped draw_* above is the family's drawer.
fv.register("prop_lamp", [
    _row(_IRON, _GLOBE, style="post", globe="red", height=92),       # L1 slim-post
    _row(_LACQUER, _GLOBE, style="paired", globe="red", height=84),  # L2 paired
    _row(_STONE_L, _GLOBE, style="shrine", height=62),               # L4 stone shrine
])
fv.register("prop_banner", [
    _row(_CLOTH_RED, style="cloth", marks=4),       # B1 vertical cloth
    _row(_PENNANT, style="pennant", flags=6),       # B2 pennant string
    _row(_SIGN, style="signboard", marks=2),        # B3 horizontal signboard
])
fv.register("prop_fire", [
    _row(_BRAZ, style="tripod"),    # F1 tripod brazier
    _row(_BRAZ, style="basket"),    # F2 low coal basket
    _row(_BRASS, style="censer"),   # F3 tall temple censer
])
fv.register("prop_bench", [
    _row(_STONE_BENCH, style="stone"),                   # S2 stone slab
    _row(dict(wood=(120, 84, 46)), style="backrail"),    # S3 back-rail
    _row(dict(wood=(130, 92, 52)), style="stool"),       # S4 stool
])
fv.register("prop_dress", [
    _row(_CRATE, style="crates"),    # D1 produce crates
    _row(_BASKET, style="baskets"),  # D2 woven baskets
    _row(_SACKS, style="sacks"),     # D4 rolled-mat + sacks
])
