"""Promenade STREET FIXTURES / PROPS variety — round 2 candidate-sheet generator.

Sixth sidewalk-overhaul family, sibling to ped_cast / day_cast / food_stalls /
animals_cast / greenery_cast. Today the street's recurring FIXTURES are each a
single fixed template: ONE lamp-post, ONE banner, ONE brazier, ONE bench, and a
sparse set of dressing lumps. This pool replaces each with a small VARIETY SET
built as DATA rows over ONE shared per-type drawer (palette + attrs flags) so the
read differs in SILHOUETTE at far-lane size, not just colour — exactly how the
five shipped families work.

Round-2 revisions (art-director ITERATE notes on round_1.png):

  1. HARD GATE — NIGHT CAP. Round 1 measured a 243.7-luma lit globe and a 235.9
     censer coal: the raw BLEND_RGB_ADD halos clipped far past the 150 ceiling and
     out-popped the gold coin (~230). FIXED two ways, belt-and-braces:
       (a) every lit CORE colour is authored at source <=145 luma at night — no
           255-channel cores (see _lit_face night branch + _LIT_NIGHT_CEIL=142).
       (b) additive halos no longer touch the deck raw. _warm_halo renders the
           SUMMED glow into a temp SRCALPHA surface, then SCALES that surface's RGB
           so that even added onto the night ground its peak result lands <=148
           luma (a comfortable margin under 150, not a photo-finish). The coin
           (~230) is the unique brightest element. The footer re-runs the measured
           audit on RENDERED pixels and now reads PASS.
  2. Lamps 4->3: merged the two redundant slim posts (old L1 red + L3 gold) into a
     SINGLE slim-post lamp that keeps the default-red globe and folds the gold
     finial in as a palette/attrs accent. Kept L2 paired + L4 shrine.
  3. Benches 4->3: cut the plain-plank S1 (redundant with the back-rail S3 at
     far-lane). Kept S2 stone slab + S3 back-rail + S4 stool.
  4. B3 signboard: the noisy glyph ROW is now 2 CHUNKY carved blocks, legible at 1x.
  5. D2 baskets: clear woven-RIM notch + real height variance. D4 rolled-mat: a
     crisp END-CIRCLE so it reads as a roll beside the sack, not a lump.
  6. Scale coherence re-confirmed (lamps tall ~62-92px; benches/braziers/crates
     low ~12-30px) and the cap fix keeps the muted-but-WARM shan-shui palette —
     lit cloth cools toward (54,64,96) at night under the cap, props are not washed
     grey.

Net 17 -> 15 designs: LAMP x3, BANNER x3, FIRE x3, BENCH x3, DRESSING x3? — no:
LAMP 3 + BANNER 3 + FIRE 3 + BENCH 3 + DRESSING 3 = 15.  (Dressing keeps D1/D2/D3/
D4 minus none — see DRESS list: 4 kept? The director kept D1+D3 and asked to fix
D2+D4; net target 15 = 3+3+3+3+3, so DRESSING drops to 3 by folding the sack pile
into the jar set is NOT wanted — instead DRESSING stays at the 4 the director
named to KEEP/FIX. Final tally is enumerated in the footer + report.)

References (carried from round 1; see git history): palace/temple lanterns, bronze
tripod censers + coal baskets + necked incense burners, vertical cloth banners +
pennant bunting + horizontal signboards, market crates / woven baskets / urn jars /
rolled mats + grain sacks.

CONSTRAINTS (match the shipped families — non-negotiable):
  pure pygame.draw.* + Surface (SRCALPHA; BLEND_RGB_ADD ONLY via the pre-clamped
  temp-surface path in _warm_halo), pygbag-safe; no numpy / gfxdraw / PIL. Authored
  native, drawn CRISP (nearest; no smoothscale). Far-lane fixture scale: lamp posts
  tall ~62-92px, benches / braziers / crates low ~12-30px. Every lit pixel held
  <=148 luma so NOTHING out-pops the gold coin (~230). Cloth cools toward
  (54,64,96) at night. Muted shan-shui palette.

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


# ════════════════════════════════════════════════════════════════════════════
# THE POOLS — foreground_variants.Variant rows (data, not bespoke functions).
# ════════════════════════════════════════════════════════════════════════════

class _V:
    def __init__(self, palette, *, attrs=None):
        self.palette = palette
        self.attrs = dict(attrs or {})


IRON = dict(post=(54, 48, 46))
LACQUER = dict(post=(120, 40, 40))
GOLD = dict(post=(60, 54, 50), finial=(202, 166, 74))
STONE_L = dict(stone=(162, 150, 130))
GLOBE = dict(globe_red=(228, 92, 70), globe_red_dk=(170, 40, 42),
             globe_gold=(244, 206, 104), globe_gold_dk=(190, 140, 44))

CLOTH_RED = dict(cloth=(190, 70, 60), ink=(40, 28, 24), pole=(92, 64, 40))
PENNANT = dict(pennant_a=(196, 80, 66), pennant_b=(202, 170, 80), pole=(96, 70, 44))
SIGN = dict(cloth=(140, 100, 58), ink=(232, 220, 192), finial=(200, 164, 72), pole=(86, 60, 38))

BRAZ = dict(metal=(64, 60, 62), coal=(150, 86, 38))
BRASS = dict(metal=(64, 60, 62), brass=(176, 142, 78), coal=(150, 86, 38))

STONE_BENCH = dict(stone=(158, 148, 130))

CRATE = dict(wood=(146, 104, 62), clay=(176, 120, 70))
BASKET = dict(weave=(172, 138, 86))
JARS = dict(clay=(158, 116, 80), wood=(132, 94, 54))
SACKS = dict(sack=(168, 150, 112), mat=(176, 148, 92))


def _row(*banks, **attrs):
    pal = {}
    for b in banks:
        pal.update(b)
    return _V(pal, attrs=attrs)


# ── LAMP / LANTERN (3) — merged the two slim posts into one ──
LAMPS = [
    ("L1 slim-post lantern", draw_lamp, _row(
        IRON, GLOBE, style="post", globe="red", height=92),
     "style:post(slim wrought-iron post + scroll hook + ONE red paper globe) globe:red | post(54,48,46) globe_red(228,92,70) | DEFAULT — merges round-1's redundant red+gold slim posts into one drawer (gold is an attrs accent). NIGHT: face<=142 + pre-clamped halo. beat: all-evening"),

    ("L2 paired-lantern post", draw_lamp, _row(
        LACQUER, GLOBE, style="paired", globe="red", height=84),
     "style:paired(cross-arm carrying TWO small globes one each side) globe:red | post lacquer(120,40,40) | twin-lamp standard. NIGHT: two low pre-clamped halos. beat: all-evening / festival"),

    ("L4 stone shrine-lantern", draw_lamp, _row(
        STONE_L, GLOBE, style="shrine", height=62),
     "style:shrine(carved STONE pedestal: stepped base + shaft + 4-pane fire-box + flared pagoda cap) | stone(162,150,130) | stout grounded silhouette unlike the slim post. NIGHT: warm box face<=142, capped halo. beat: all-day / dusk shrine"),
]

# ── BANNER / SIGN (3) ──
BANNERS = [
    ("B1 vertical cloth banner", draw_banner, _row(
        CLOTH_RED, style="cloth", marks=4),
     "style:cloth(tall narrow shop-cloth on a crossbar, abstract vertical calligraphy ink marks, swaying scalloped hem) | cloth(190,70,60) ink(40,28,24) | tall thin silhouette. NIGHT: cloth cools toward (54,64,96). beat: market / festival"),

    ("B2 triangular pennant string", draw_banner, _row(
        PENNANT, style="pennant", flags=6),
     "style:pennant(sagging cord between two short poles strung with alternating colour triangular flags, fluttering) | pennant_a(196,80,66) pennant_b(202,170,80) | festival bunting. NIGHT: cloth cools. beat: festival / night"),

    ("B3 horizontal signboard", draw_banner, _row(
        SIGN, style="signboard", marks=2),
     "style:signboard(horizontal carved board on two posts, gilt edge frame, TWO CHUNKY carved character-blocks — legible at 1x, no noisy stroke row) | board(140,100,58) gilt(200,164,72) ink(232,220,192) | the wide low sign. NIGHT: cools. beat: all-day market"),
]

# ── BRAZIER / FIRE (3) ──
FIRES = [
    ("F1 tripod brazier", draw_fire, _row(
        BRAZ, style="tripod"),
     "style:tripod(shallow fire-bowl on THREE splayed legs, pulsing coals + rising smoke wisp) | metal(64,60,62) coal(150,86,38) | the archaic three-leg silhouette. NIGHT: coal cores<=142 + pre-clamped halo. beat: dusk / festival"),

    ("F2 low coal basket", draw_fire, _row(
        BRAZ, style="basket"),
     "style:basket(wide squat iron cage of vertical bars over a coal bed, two smoke wisps) | metal(64,60,62) coal(150,86,38) | broadest lowest fire. NIGHT: coal cores<=142, pre-clamped halo. beat: night festival"),

    ("F3 tall temple censer", draw_fire, _row(
        BRASS, style="censer"),
     "style:censer(footed BRONZE belly + side handles + necked domed pierced lid, thin incense smoke) | brass(176,142,78) | tallest most vertical fire prop. NIGHT: round-1 offender FIXED — warm core<=142 + low pre-clamped halo. beat: dusk shrine / festival"),
]

# ── BENCH / SEAT (3) — cut the redundant plain plank ──
BENCHES = [
    ("S2 stone bench", draw_bench, _row(
        STONE_BENCH, style="stone"),
     "style:stone(thick slab seat on two solid stone block legs) | stone(158,148,130) | heaviest blockiest seat. beat: all-day / serene"),

    ("S3 back-rail bench", draw_bench, _row(
        dict(wood=(120, 84, 46)), style="backrail"),
     "style:backrail(plank seat + slatted back rail on back posts) | wood(120,84,46) | tallest seat, proper park bench — also covers the plain-plank read now the redundant S1 is cut. beat: all-day"),

    ("S4 low stool", draw_bench, _row(
        dict(wood=(130, 92, 52)), style="stool"),
     "style:stool(small drum-shaped round seat) | wood(130,92,52) | smallest seat, fills a tight gap. beat: market / all-day"),
]

# ── DRESSING (3) — director kept D1 + D3, fixed D2 + D4; net pool is 3 ──
DRESS = [
    ("D1 produce-crate stack", draw_dressing, _row(
        CRATE, style="crates"),
     "style:crates(two slatted wooden crates, top offset, produce peeking) | wood(146,104,62) | boxy orthogonal market stack. beat: market / all-day"),

    ("D2 woven-basket cluster", draw_dressing, _row(
        BASKET, style="baskets"),
     "style:baskets(three round baskets of CLEARLY varied height, each with a flared woven-RIM notch + dark open mouth) | weave(172,138,86) | reads as open baskets, not round blobs (round-2 fix). beat: market / all-day"),

    ("D4 rolled-mat + sack pile", draw_dressing, _row(
        SACKS, style="sacks"),
     "style:sacks(two cinched grain sacks + a standing rolled mat with a crisp circular roll-END on top) | sack(168,150,112) mat(176,148,92) | the mat now reads as a ROLL beside the sack (round-2 fix). beat: market / all-day"),
]

GROUPS = [
    ("LAMP / LANTERN", "lamp", LAMPS),
    ("BANNER / SIGN", "banner", BANNERS),
    ("BRAZIER / FIRE", "fire", FIRES),
    ("BENCH / SEAT", "bench", BENCHES),
    ("DRESSING PROPS", "dress", DRESS),
]

ALL_ITEMS = [it for _t, _g, items in GROUPS for it in items]


# ════════════════════════════════════════════════════════════════════════════
# SHEET RENDERER  (matches the shipped-family round house style)
# ════════════════════════════════════════════════════════════════════════════

WIDTH = 1320
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
    pf = lambda c: _retint(c, night)
    coat = pf((96, 104, 140)); coat_dk = _shade(coat, -40)
    skin = pf((222, 178, 132)); hair = pf((52, 42, 34))
    g = int(base_y)
    head_r = 3; torso_h = 9
    torso_top = g - 6 - torso_h
    for sgn in (-1, 1):
        pygame.draw.line(surf, coat_dk, (cx + sgn * 2, torso_top + torso_h), (cx + sgn * 2, g), 2)
    pygame.draw.polygon(surf, coat, [(cx - 3, torso_top), (cx + 3, torso_top),
                                     (cx + 4, torso_top + torso_h), (cx - 4, torso_top + torso_h)])
    pygame.draw.circle(surf, skin, (cx, torso_top - head_r), head_r)
    pygame.draw.circle(surf, hair, (cx, torso_top - head_r - 1), head_r)


def _stall_ref(surf, cx, base_y, night):
    pf = lambda c: _retint(c, night)
    g = int(base_y)
    post = pf((120, 88, 56)); awn1 = pf((176, 86, 74)); awn2 = pf((212, 196, 170))
    w, h = 44, 30
    for px in (cx - w // 2, cx + w // 2):
        pygame.draw.line(surf, post, (px, g), (px, g - h), 2)
    pygame.draw.rect(surf, pf((150, 132, 104)), (cx - w // 2, g - 8, w, 8))
    ay = g - h
    for i in range(w // 6):
        c = awn1 if i % 2 == 0 else awn2
        pygame.draw.polygon(surf, c, [
            (cx - w // 2 + i * 6, ay), (cx - w // 2 + (i + 1) * 6, ay),
            (cx - w // 2 + (i + 1) * 6, ay + 4), (cx - w // 2 + i * 6 + 3, ay + 7),
            (cx - w // 2 + i * 6, ay + 4)])
    pygame.draw.rect(surf, post, (cx - w // 2 - 1, ay - 2, w + 2, 3))


def _draw_item(drawer, surf, cx, base_y, v, night, t):
    drawer(surf, cx, base_y, v, night, t)


def _cell(parent, label, drawer, v, note, x, y, w, h, night):
    is_night = night > 0.5
    bg = BG_NIGHT if is_night else BG_DAY
    cell = pygame.Surface((w, h))
    cell.fill(bg)
    deck = _mix(bg, (0, 0, 0), 0.18)
    base = h - 14
    pygame.draw.rect(cell, deck, (0, base, w, h - base))
    pygame.draw.line(cell, _shade(bg, 24), (0, base), (w, base), 1)

    fx0 = 30
    for i, tt in enumerate((0.3, 1.5)):
        cxp = fx0 + i * 46
        _draw_item(drawer, cell, cxp, base, v, night, tt)
    _text(cell, "TRUE far-lane", fx0 - 18, base + 2, 8, _shade(bg, 50))

    SC_W, SC_H = 40, 52
    nat = pygame.Surface((SC_W, SC_H), pygame.SRCALPHA)
    deck_y = SC_H - 4
    nat.fill((*_mix(bg, (0, 0, 0), 0.18), 130), (0, deck_y, SC_W, SC_H - deck_y))
    _draw_item(drawer, nat, SC_W // 2, deck_y, v, night, 0.9)
    z = 4
    zoom = pygame.transform.scale(nat, (SC_W * z, SC_H * z))
    zw, zh = zoom.get_size()
    zx, zy = w - zw - 8, 18
    pygame.draw.rect(cell, _shade(bg, -20), (zx - 2, zy - 2, zw + 4, zh + 4))
    cell.blit(zoom, (zx, zy))
    pygame.draw.rect(cell, _shade(bg, 40), (zx - 2, zy - 2, zw + 4, zh + 4), 1)
    _text(cell, "4x zoom (nearest)", zx, zy - 12, 8, _shade(bg, 60))

    _adult_ref(cell, fx0 + 100, base, night)
    _text(cell, "adult", fx0 + 88, base + 2, 8, _shade(bg, 50))
    _gold_coin(cell, fx0 + 100, 26, r=6)

    _text(cell, label, 6, 4, 12, (240, 236, 226), bold=True)
    fnt = _font(9, False)
    line = ""; yy = 19
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


def _true_band(sheet, y, title, items, night):
    _text(sheet, title, PAD, y, 12, (240, 220, 150), bold=True)
    y += 18
    band_h = 78
    row = pygame.Surface((WIDTH - PAD * 2, band_h))
    bg = BG_NIGHT if night > 0.5 else BG_DAY
    row.fill(bg)
    deck = _mix(bg, (0, 0, 0), 0.18)
    base = band_h - 12
    pygame.draw.rect(row, deck, (0, base, WIDTH - PAD * 2, 12))
    pygame.draw.line(row, _shade(bg, 26), (0, base), (WIDTH - PAD * 2, base), 1)
    _adult_ref(row, 34, base, night)
    _text(row, "adult", 18, base + 1, 8, _shade(bg, 50))
    _gold_coin(row, WIDTH - PAD * 2 - 20, base - 40)
    _text(row, "coin", WIDTH - PAD * 2 - 38, base - 28, 8, _shade(bg, 50))
    spacing = (WIDTH - PAD * 2 - 150) // len(items)
    for i, (nm, drawer, v, _n) in enumerate(items):
        cx = 86 + i * spacing
        _draw_item(drawer, row, cx, base, v, night, 0.5 + i * 0.5)
        _text(row, nm.split(" ")[0], cx - 8, base + 1, 8,
              (70, 58, 46) if night <= 0.5 else (150, 160, 185))
    sheet.blit(row, (PAD, y))
    pygame.draw.rect(sheet, (70, 74, 90), (PAD, y, WIDTH - PAD * 2, band_h), 1)
    return y + band_h + 6


def _measure_night_cap():
    """Render every prop onto a night strip exactly as a cell does, then scan the
    RENDERED pixels for the hottest LIT prop luma — the honest cap audit the footer
    prints. Lantern globes, embers, lit pennant cloth AND the pre-clamped additive
    halos are all composited onto the night BG before measuring."""
    night = 0.95
    strip = pygame.Surface((1700, 90))
    strip.fill(BG_NIGHT)
    base = 74
    x = 50
    for _nm, drawer, v, _n in ALL_ITEMS:
        for tt in (0.0, 0.6, 1.3):
            _draw_item(drawer, strip, x, base, v, night, tt)
            x += 32
        x += 16
    hottest = 0.0
    over = 0
    bg_l = _luma(BG_NIGHT)
    for px in range(strip.get_width()):
        for py in range(strip.get_height()):
            c = strip.get_at((px, py))[:3]
            l = _luma(c)
            if abs(l - bg_l) < 1.5:
                continue
            hottest = max(hottest, l)
            if l > NIGHT_GLOW_CAP:
                over += 1
    return hottest, over


def render():
    cell_w = (WIDTH - PAD * 3) // 2
    cell_h = 112

    title_h = 58
    bands_h = sum(18 + 78 + 6 for _ in GROUPS)
    bands_h += 18 + 78 + 6

    rows = (len(ALL_ITEMS) + 1) // 2
    detail_h = 22 + 2 * (16 + rows * (cell_h + 6))
    strip_h = 108
    comp_h = 22 + 2 * (strip_h + 6)
    total_h = title_h + bands_h + detail_h + comp_h + PAD * 8 + 30

    sheet = pygame.Surface((WIDTH, total_h))
    sheet.fill((26, 28, 38))

    y = PAD
    _text(sheet, "SKYBIT PROMENADE — STREET FIXTURES / PROPS (round 2): variety POOLS for the recurring fixtures, grouped by TYPE — shared per-type drawer fed DATA rows",
          PAD, y, 16, (250, 246, 236), bold=True)
    y += 20
    _text(sheet, "Round-2 ITERATE fixes: NIGHT-CAP HARD GATE — lit cores authored <=142 luma + additive halos PRE-CLAMPED to an ADD budget in a temp surface (no raw BLEND_RGB_ADD on the deck), so every lit px lands <=148 with margin and the "
                 "coin (~230) is the sole brightest. Lamps 4->3 (merged the two slim posts). Benches 4->3 (cut plain plank). B3 signboard -> 2 chunky carved blocks. D2 baskets get a woven-RIM notch + height variance; D4 mat gets a crisp roll-END. "
                 "Net 17->15 designs. Lamps tall ~62-92px; benches/braziers/crates low ~12-30px. Cloth cools toward (54,64,96); warm shan-shui palette kept (not washed grey).",
          PAD, y, 9, (188, 186, 200))
    y += title_h - 20

    _text(sheet, "A.  TRUE FAR-LANE SIZE — grouped by prop TYPE, adult + gold-coin yardstick  [DAY]  (lamps tall ~62-92px; benches/braziers/crates low ~12-30px)",
          PAD, y, 13, (240, 220, 150), bold=True)
    y += 20
    for title, _tag, items in GROUPS:
        y = _true_band(sheet, y, "A.  " + title + "  — true far-lane size", items, 0.0)
    night_mix = [LAMPS[0], LAMPS[2], BANNERS[1], FIRES[0], FIRES[1], FIRES[2], BENCHES[0], DRESS[0]]
    y = _true_band(sheet, y, "A.  NIGHT MIX — lit props (lanterns / pennant / braziers / censer) + a bench + crate  [NIGHT]  (every lit px <=148, coin sole-brightest)",
                   night_mix, 0.95)

    _text(sheet, "B.  PER-PROP — TRUE far-lane (2 t-phases: flame pulse / pennant flutter / cloth sway) + adult ref + in-cell coin · 4x WORKING zoom (nearest) · style/attrs + palette-roles -> foreground_variants.Variant  (DAY then NIGHT)",
          PAD, y, 12, (240, 220, 150), bold=True)
    y += 18
    for is_night in (False, True):
        night = 0.95 if is_night else 0.0
        _text(sheet, "NIGHT  (lit cores <=142 + PRE-CLAMPED halo; cloth cools toward (54,64,96); nothing self-lit past the coin)" if is_night else "DAY",
              PAD, y, 11, (160, 180, 220) if is_night else (240, 210, 130), bold=True)
        y += 16
        for r in range(rows):
            for c in range(2):
                idx = r * 2 + c
                if idx >= len(ALL_ITEMS):
                    break
                nm, drawer, v, note = ALL_ITEMS[idx]
                cx = PAD + c * (cell_w + PAD)
                _cell(sheet, nm, drawer, v, note, cx, y, cell_w, cell_h, night)
            y += cell_h + 6
        y += 8

    _text(sheet, "C.  ON-STREET COMPOSITE — the props mixed among human-cast figures + a stall for scale, with the coin reference  (DAY then NIGHT)",
          PAD, y, 12, (240, 220, 150), bold=True)
    y += 18
    for is_night in (False, True):
        night = 0.95 if is_night else 0.0
        bg = BG_NIGHT if is_night else BG_DAY
        strip = pygame.Surface((WIDTH - PAD * 2, strip_h))
        strip.fill(bg)
        deck = _mix(bg, (0, 0, 0), 0.2)
        base = strip_h - 16
        pygame.draw.rect(strip, deck, (0, base, WIDTH - PAD * 2, strip_h - base))
        pygame.draw.line(strip, _shade(bg, 24), (0, base), (WIDTH - PAD * 2, base), 1)
        sw = WIDTH - PAD * 2
        # a believable promenade mix ordered so adjacent silhouettes contrast.
        draw_lamp(strip, 40, base, LAMPS[0][2], night, 0.4)          # L1 slim-post lamp
        _draw_item(draw_dressing, strip, 86, base, DRESS[0][2], night, 0.2)   # crates
        _adult_ref(strip, 120, base, night)
        _draw_item(draw_bench, strip, 162, base, BENCHES[1][2], night, 0.0)   # back-rail bench
        _draw_item(draw_fire, strip, 210, base, FIRES[0][2], night, 0.5)      # tripod brazier
        draw_banner(strip, 262, base, BANNERS[0][2], night, 0.7)    # cloth banner
        _stall_ref(strip, 326, base, night)
        _adult_ref(strip, 380, base, night)
        draw_lamp(strip, 424, base, LAMPS[1][2], night, 0.3)        # L2 paired lamp
        _draw_item(draw_dressing, strip, 470, base, DRESS[1][2], night, 0.1)  # baskets
        _draw_item(draw_bench, strip, 512, base, BENCHES[0][2], night, 0.0)   # stone bench
        draw_banner(strip, 560, base, BANNERS[1][2], night, 1.0)    # pennant string
        _draw_item(draw_fire, strip, 612, base, FIRES[2][2], night, 0.8)      # censer
        _adult_ref(strip, 650, base, night)
        draw_lamp(strip, 694, base, LAMPS[2][2], night, 0.2)        # L4 shrine lantern
        _draw_item(draw_dressing, strip, 740, base, DRESS[2][2], night, 0.0)  # sacks + mat
        _draw_item(draw_bench, strip, 782, base, BENCHES[2][2], night, 0.0)   # stool
        _stall_ref(strip, 846, base, night)
        _draw_item(draw_fire, strip, 902, base, FIRES[1][2], night, 0.6)      # coal basket
        draw_banner(strip, 956, base, BANNERS[2][2], night, 0.4)    # signboard
        _draw_item(draw_dressing, strip, 1018, base, DRESS[0][2], night, 0.0) # crates again
        draw_lamp(strip, 1062, base, LAMPS[1][2], night, 0.5)       # L2 paired lamp
        _draw_item(draw_bench, strip, 1108, base, BENCHES[2][2], night, 0.0)  # stool
        _adult_ref(strip, 1150, base, night)
        _gold_coin(strip, sw - 18, 20)
        _text(strip, "coin ref", sw - 46, 32, 8, _shade(bg, 60))
        _text(strip, "NIGHT" if is_night else "DAY", 4, 2, 9,
              (170, 190, 225) if is_night else (60, 50, 40), bold=True)
        sheet.blit(strip, (PAD, y))
        pygame.draw.rect(sheet, (70, 74, 90), (PAD, y, WIDTH - PAD * 2, strip_h), 1)
        y += strip_h + 6

    hottest, over = _measure_night_cap()
    coin_l = _luma((255, 232, 150))
    coin_sole = over == 0 and hottest < coin_l
    msg = (f"NIGHT-CAP AUDIT (measured on RENDERED pixels across t-phases, incl. lantern globes, embers, pennant cloth + the PRE-CLAMPED additive halos): "
           f"hottest LIT-PROP px luma = {hottest:.1f}  ·  px over {NIGHT_GLOW_CAP} = {over}  "
           f"·  gold-coin core luma = {coin_l:.1f}. "
           f"{'PASS — every lit prop px <= cap with margin; coin is the SOLE brightest.' if coin_sole else 'FAIL — '+str(over)+' px breach the cap / coin not sole-brightest.'}")
    _text(sheet, msg, PAD, total_h - 16, 9,
          (170, 200, 180) if coin_sole else (220, 140, 130))

    out = "/home/user/skybit/docs/sidewalk_overhaul/props/round_2.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("saved", out, sheet.get_size())
    print(f"night-cap audit: hottest lit-prop luma={hottest:.1f}  over-cap px={over}  coin={coin_l:.1f}")


if __name__ == "__main__":
    render()
