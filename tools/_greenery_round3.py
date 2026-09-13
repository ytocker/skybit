"""Promenade PLANTS & GREENERY variety — round 3 candidate-sheet generator.

Fifth sidewalk-overhaul family, sibling to ped_cast / day_cast / food_stalls /
animals_cast. Today the street greenery is just ONE shrub planter + ONE conifer
planter + ONE wish-tree, reused at every slot. This pool explores a VARIETY of
designs built as VESSEL x SPECIES rows over ONE shared draw_greenery drawer —
data rows, not bespoke functions — so the read differs in SILHOUETTE (vessel
shape + canopy shape), not just colour.

Round 3 is a NARROW two-plant fix on the art-director's ITERATE: 8 of 10 plants
PASS and are LOCKED untouched (G1 shrub, G2 conifer, G3 topiary-3, G4 lollipop,
G5 plum-flowering, G7 bamboo, G9 kumquat, G10 wish-tree). Only TWO still failed
at true size, and ONLY these two were reworked:

  G8 VINE/FERN — round 2 still read as SPIDER-LEGS / a broken bracket: 3 strands
    hung as separate parallel verticals with gaps between them. REBUILT as ONE
    CONNECTED CURTAIN: (a) the fern tuft/crown is WIDENED so it is clearly the
    visual anchor; (b) the strands now JOIN into the canopy at the top and FAN /
    taper outward as a connected curtain — the gaps between adjacent ropes are
    FILLED so the drape reads as one continuous skirt, not three legs; (c) the
    silhouette is a continuous draped-skirt spilling over the trough. TEST: at
    1x NIGHT it must read as "plant draping over a trough," never as legs.

  G6 FLOWERING-VINE — round 2 read as magenta STRIPES painted ON the urn, not
    bloom spilling off the plant. FIXED: (a) the blossom strands now visibly
    ORIGINATE from the leafy head and OVERHANG / break the urn's outer
    silhouette (they hang OUTSIDE the urn belly width) so they read as plant,
    not paint; (b) the blossoms are CLUMPED into 2-3 denser fall-points (a
    flower cluster reads as flowers; evenly-spaced pixels read as texture); (c)
    the toned chroma is kept; only the SHAPE changes to unambiguous "bloom
    hanging off the plant." Night cap re-audited so the denser clumps don't
    spike a hot pixel.

The other 8 designs are unchanged from round 2 (approved + LOCKED).

References studied (penjing/courtyard pots, temple wish-trees, CNY plants):
  - Penjing pots span unglazed warm TERRACOTTA (informal), Shiwan/Jingdezhen
    BLUE-WHITE glazed urns, and creatively-shaped vessels; bonsai pots are low +
    muted.  -> VESSELS: terracotta pot / glazed blue-white urn / wooden tub /
    bamboo planter / stone trough — each a distinct OUTLINE (taper, lip, belly).
  - Temple WISH-TREES (Lam Tsuen / Longhua banyan) are dense canopies HUNG with
    red prayer ribbons; here the variant axis is broad WEEPING canopy FORM.
  - CNY luck plants: KUMQUAT (wealth-fruit, orange dots — now an open fruiting
    tree), plum/peach/camellia BLOSSOM (muted seasonal accent), bamboo (tall
    thin canes), clipped topiary balls. Blossoms/fruit are ACCENT dots held well
    under the gold coin.  Trailing/draping greenery (ivy, Boston-fern,
    wisteria/bougainvillea) hangs as a CONNECTED curtain off a wide crown, not
    as separate dangling threads.

CONSTRAINTS (match the shipped families — non-negotiable):
  pure pygame.draw.* + Surface (SRCALPHA ok), pygbag-safe; no numpy/gfxdraw/PIL.
  Foliage = clustered shaded circles/ellipses (matches _draw_planter's bushy
  idiom). Authored native, drawn CRISP (nearest; no smoothscale). Far-lane pots
  ~25-45px tall (a pot reads shorter than a standing adult), trees taller.
  Greenery is beat/weather-NEUTRAL. Night cools toward (54,64,96) <=150 luma
  (study ped_cast._retint_person); blossom/fruit accents are muted, nothing
  self-lit, never rival the coin. Expressible as foreground_variants.Variant
  rows: palette + vessel/species/attrs flags over the shared draw_greenery.

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
    greenery sits in the same value family as the retinted floor + the human cast.
    A second, stronger cool is applied to anything still above the cap so no leaf,
    pot highlight, blossom or fruit dot can ever out-glow the gold coin at night."""
    if night <= 0.05:
        return col
    out = _mix(col, (54, 64, 96), min(0.55, 0.40 * night + 0.20))
    if _luma(out) > NIGHT_GLOW_CAP:
        over = (_luma(out) - NIGHT_GLOW_CAP) / max(1.0, 255 - NIGHT_GLOW_CAP)
        out = _mix(out, (66, 76, 104), min(0.78, 0.5 + over))
    return out


def _hi(c, d, night):
    """A highlight d above c, clamped under the night cap so _shade can't push a
    pale pot rim or leaf top past the coin at night."""
    out = _shade(c, d)
    if night > 0.05 and _luma(out) > NIGHT_GLOW_CAP:
        out = _mix(out, (66, 76, 104), 0.65)
    return out


def _accent(col, night, *, day_ceil=188):
    """A blossom / fruit / ribbon accent dot: muted by design, held WELL under the
    coin (a hard 132 ceiling at night, a softer day ceiling) so the warm pops read
    as seasonal colour without ever becoming the brightest thing on the street.
    `day_ceil` is now per-call so a too-chromatic day accent (the blossom, the
    night ribbon) can be knocked a notch further down without touching others."""
    out = _retint(col, night)
    ceil = 132 if night > 0.05 else day_ceil
    if _luma(out) > ceil:
        out = _mix(out, (70, 60, 64) if night <= 0.05 else (66, 72, 96),
                   min(0.7, (_luma(out) - ceil) / 120.0 + 0.3))
    return out


def _night_lift(col, night, frac):
    """Lift a too-dark vessel toward a cool grey on NIGHT only, so a low granite
    trough doesn't merge into the retinted dark ground band. Stays under the cap
    by construction (target grey luma ~118)."""
    if night <= 0.05:
        return col
    return _mix(col, (104, 112, 132), frac * night)


# ════════════════════════════════════════════════════════════════════════════
# ONE shared drawer.  v.attrs picks a VESSEL outline + a SPECIES canopy; the two
# compose into a silhouette. Authored feet on `base_y`, plant grows UP. A 1.0
# pot stands VESSEL_H px; species canopy sits ABOVE the vessel rim.
#
# attrs (the foreground_variants row, family 'greenery'):
#   vessel  — 'terracotta'|'urn'|'tub'|'bamboo'|'trough'  (pot OUTLINE enum)
#   species — 'shrub'|'conifer'|'topiary'|'flowering'|'bamboo'|'vine'|
#             'flovine'|'kumquat'|'wishtree'               (canopy enum)
#   tiers   — topiary ball count (1|2|3)
#   mass    — canopy mass scale (wish-tree / shrub fullness)
#   day_chroma — accent day-ceiling override (lower = more muted by day)
#   night_chroma — accent night-ceiling-style override knob for ribbon red
#   vlift   — night-only vessel value lift fraction (granite rescue)
# palette roles: vessel, vessel_dk, vessel_lt, glaze (urn pattern), foliage_dark,
#   foliage_mid, foliage_top, trunk, accent (bloom/fruit/ribbon)
# ════════════════════════════════════════════════════════════════════════════

VESSEL_H = 14      # height of a 1.0 terracotta pot (px). A pot reads shorter than
                   # an adult (PED_H~18 torso+legs ~26px), a tree taller.


def draw_greenery(surf, cx, base_y, v, night, t):
    A = v.attrs
    vessel = A.get("vessel", "terracotta")
    species = A.get("species", "shrub")
    rim_y = _draw_vessel(surf, cx, base_y, v, night, vessel)
    # The canopy is seated on the rim the vessel returns, so any vessel composes
    # with any species without per-combo geometry.
    {
        "shrub": _sp_shrub, "conifer": _sp_conifer, "topiary": _sp_topiary,
        "flowering": _sp_flowering, "bamboo": _sp_bamboo, "vine": _sp_vine,
        "flovine": _sp_flovine, "kumquat": _sp_kumquat, "wishtree": _sp_wishtree,
    }[species](surf, cx, rim_y, v, night, t)


# ── VESSELS — each a distinct OUTLINE; returns the rim y the canopy plants into ─

def _draw_vessel(surf, cx, base_y, v, night, kind):
    P, A = v.palette, v.attrs
    vlift = A.get("vlift", 0.0)
    pf = lambda c: _night_lift(_retint(c, night), night, vlift)
    body = pf(P.get("vessel", (170, 104, 72)))
    dk = pf(P.get("vessel_dk", _shade(P.get("vessel", (170, 104, 72)), -34)))
    lt = _hi(body, 18, night)
    g = int(base_y)

    if kind == "terracotta":
        # Classic tapered flowerpot: wide flared rim, body narrows to the foot,
        # a banded rim lip. The warm unglazed penjing pot.
        h = VESSEL_H
        top_w, bot_w = 18, 12
        rim_h = 3
        ty = g - h
        pygame.draw.polygon(surf, dk, [
            (cx - top_w // 2, ty + rim_h), (cx + top_w // 2, ty + rim_h),
            (cx + bot_w // 2, g), (cx - bot_w // 2, g)])
        pygame.draw.polygon(surf, body, [
            (cx - top_w // 2 + 1, ty + rim_h), (cx + top_w // 2 - 1, ty + rim_h),
            (cx + bot_w // 2, g - 1), (cx - bot_w // 2, g - 1)])
        pygame.draw.rect(surf, dk, (cx - top_w // 2, ty, top_w, rim_h))
        pygame.draw.rect(surf, body, (cx - top_w // 2 + 1, ty, top_w - 2, rim_h - 1))
        pygame.draw.rect(surf, lt, (cx - top_w // 2 + 1, ty, top_w - 2, 1))
        pygame.draw.line(surf, lt, (cx - top_w // 2 + 2, ty + rim_h + 1),
                         (cx - bot_w // 2 + 1, g - 1), 1)
        return ty + 1

    if kind == "urn":
        # Glazed blue-white ceramic urn: a rounded BELLY that swells then necks in
        # to a small mouth, with a painted glaze band — the porcelain silhouette.
        h = VESSEL_H + 4
        ty = g - h
        belly_w = 19
        glaze = _retint(P.get("glaze", (96, 120, 170)), night)
        # belly (two stacked ellipses for a swollen pot)
        pygame.draw.ellipse(surf, dk, (cx - belly_w // 2, ty + 5, belly_w, h - 4))
        pygame.draw.ellipse(surf, body, (cx - belly_w // 2 + 1, ty + 6, belly_w - 2, h - 6))
        pygame.draw.arc(surf, lt, (cx - belly_w // 2 + 1, ty + 6, belly_w - 2, h - 6),
                        math.radians(40), math.radians(150), 1)
        # neck + small mouth
        neck_w = 9
        pygame.draw.rect(surf, body, (cx - neck_w // 2, ty + 2, neck_w, 5))
        pygame.draw.rect(surf, dk, (cx - neck_w // 2, ty + 2, neck_w, 5), 1)
        pygame.draw.ellipse(surf, dk, (cx - neck_w // 2, ty, neck_w, 4))
        pygame.draw.ellipse(surf, _shade(body, -8), (cx - neck_w // 2 + 1, ty + 1, neck_w - 2, 2))
        # painted blue glaze band — a row of dots + a wavy line, the Shiwan motif
        gby = ty + 9
        pygame.draw.line(surf, glaze, (cx - belly_w // 2 + 2, gby), (cx + belly_w // 2 - 2, gby), 1)
        for dxp in range(-belly_w // 2 + 3, belly_w // 2 - 1, 3):
            pygame.draw.circle(surf, glaze, (cx + dxp, gby + 3), 1)
        return ty + 2

    if kind == "tub":
        # Wooden planter tub: straight-sided staves with two iron hoop bands — a
        # squat barrel cut down to a planter, the chunkiest vessel.
        h = VESSEL_H + 1
        w = 20
        ty = g - h
        pygame.draw.rect(surf, dk, (cx - w // 2, ty, w, h))
        pygame.draw.rect(surf, body, (cx - w // 2 + 1, ty, w - 2, h - 1))
        # vertical stave seams
        for sxp in range(cx - w // 2 + 3, cx + w // 2 - 1, 4):
            pygame.draw.line(surf, _shade(body, -20), (sxp, ty + 1), (sxp, g - 2), 1)
        pygame.draw.line(surf, lt, (cx - w // 2 + 1, ty + 1), (cx + w // 2 - 2, ty + 1), 1)
        hoop = pf(P.get("vessel_dk", (90, 70, 50)))
        for hy in (ty + 2, g - 3):
            pygame.draw.rect(surf, _shade(hoop, -18), (cx - w // 2, hy, w, 2))
            pygame.draw.line(surf, _shade(hoop, 26), (cx - w // 2, hy), (cx + w // 2 - 1, hy), 1)
        return ty + 1

    if kind == "bamboo":
        # Bamboo planter: a low cylinder of lashed bamboo CANES standing in a row,
        # tied with a cord band — a clearly segmented green vessel.
        h = VESSEL_H - 2
        w = 18
        ty = g - h
        cane = pf(P.get("vessel", (150, 160, 96)))
        cane_dk = _shade(cane, -32)
        pygame.draw.rect(surf, _shade(cane, -22), (cx - w // 2, ty, w, h))
        for i, sxp in enumerate(range(cx - w // 2, cx + w // 2 - 1, 3)):
            cc = cane if i % 2 == 0 else _shade(cane, -10)
            pygame.draw.rect(surf, cc, (sxp, ty, 3, h - 1))
            pygame.draw.line(surf, _shade(cc, 22), (sxp, ty), (sxp, g - 1), 1)
            pygame.draw.line(surf, cane_dk, (sxp + 2, ty), (sxp + 2, g - 1), 1)
        # node band lines + a lashing cord
        for ny in (ty + h // 3, g - 3):
            pygame.draw.line(surf, cane_dk, (cx - w // 2, ny), (cx + w // 2 - 1, ny), 1)
        cord = _retint((150, 120, 70), night)
        pygame.draw.line(surf, cord, (cx - w // 2, ty + 2), (cx + w // 2 - 1, ty + 2), 2)
        return ty

    if kind == "trough":
        # Simple stone trough: a long low rectangular basin, heavy + plain — the
        # quietest vessel, reads as carved granite. NIGHT value lifted ~5% (vlift)
        # so it doesn't merge into the dark retinted ground band.
        h = 9
        w = 22
        ty = g - h
        stone = pf(P.get("vessel", (150, 142, 124)))
        pygame.draw.rect(surf, _shade(stone, -22), (cx - w // 2, ty, w, h))
        pygame.draw.rect(surf, stone, (cx - w // 2 + 1, ty, w - 2, h - 2))
        pygame.draw.rect(surf, _shade(stone, 16), (cx - w // 2 + 1, ty, w - 2, 1))
        # a chiselled top lip + a couple of weathering speckles
        pygame.draw.rect(surf, _shade(stone, -14), (cx - w // 2 + 1, ty + 2, w - 2, 1))
        for dxp in (-6, 2, 7):
            pygame.draw.circle(surf, _shade(stone, -18), (cx + dxp, ty + 5), 1)
        return ty

    return g - VESSEL_H


# ── SPECIES — each a distinct canopy SHAPE, planted on rim_y ────────────────────

def _foliage(P, night):
    pf = lambda c: _retint(c, night)
    return (pf(P.get("foliage_dark", (40, 80, 55))),
            pf(P.get("foliage_mid", (60, 110, 75))),
            pf(P.get("foliage_top", (96, 150, 100))))


def _dome(surf, cx, cy, rw, rh, dark, mid, lt=None):
    pygame.draw.ellipse(surf, dark, (cx - rw, cy - rh, rw * 2, rh * 2))
    pygame.draw.ellipse(surf, mid, (cx - rw + 1, cy - rh + 1, rw * 2 - 3, rh * 2 - 2))
    if lt is not None:
        pygame.draw.arc(surf, lt, (cx - rw + 1, cy - rh + 1, rw * 2 - 3, rh * 2 - 2),
                        math.radians(35), math.radians(140), 1)


def _sp_shrub(surf, cx, rim_y, v, night, t):
    """Leafy bushy shrub — overlapping rounded domes, a few muted blossom dots.
    The fullest 'just foliage' read (matches draw_side_shrub's idiom)."""
    P, A = v.palette, v.attrs
    dark, mid, top = _foliage(P, night)
    m = A.get("mass", 1.0)
    sway = math.sin(t * 1.4) * 0.6
    base = rim_y
    for dx, dy, rw, rh in (
            (-int(6 * m), -3, int(7 * m), int(6 * m)),
            (int(6 * m), -4, int(7 * m), int(6 * m)),
            (0, -int(9 * m), int(8 * m), int(7 * m))):
        _dome(surf, cx + dx + int(sway * (dy < -6)), base + dy, rw, rh, dark, mid, top)
    bloom = P.get("accent")
    if bloom:
        ac = _accent(bloom, night)
        for bx, by in ((-5, -6), (4, -8), (0, -12), (6, -4)):
            pygame.draw.circle(surf, ac, (cx + bx, base + by), 1)


def _sp_conifer(surf, cx, rim_y, v, night, t):
    """Dark cypress / conifer cone — a tall narrow stacked-tier triangle. The
    spire silhouette (contrasts the round shrub)."""
    P = v.palette
    dark, mid, top = _foliage(P, night)
    base = rim_y
    # stacked tiers narrowing to a point, each a flattened triangle
    tiers = ((9, 0, 6), (7, -6, 6), (5, -12, 5), (3, -17, 4), (2, -21, 3))
    for hw, dy, th in tiers:
        ty = base + dy
        pygame.draw.polygon(surf, dark, [
            (cx - hw, ty), (cx + hw, ty), (cx, ty - th - 1)])
        pygame.draw.polygon(surf, mid, [
            (cx - hw + 1, ty - 1), (cx + hw - 1, ty - 1), (cx, ty - th)])
    pygame.draw.line(surf, top, (cx - 1, base - 14), (cx, base - 23), 1)


def _sp_topiary(surf, cx, rim_y, v, night, t):
    """Clipped ball topiary — 1/2/3 stacked spheres on a bare stem, the most
    geometric canopy. tiers picks the count.

    For tiers==1 the bare-stem 'lollipop' is EXAGGERATED: a clearly TALL bare
    stem lifts a single ball well clear of the rim, so it can't be mistaken for
    the solid round domes of the shrub/flowering family."""
    P, A = v.palette, v.attrs
    dark, mid, top = _foliage(P, night)
    trunk = _retint(P.get("trunk", (110, 84, 56)), night)
    tiers = A.get("tiers", 2)
    base = rim_y
    if tiers == 1:
        # tall lollipop: long bare stem + one ball floating clear of the rim
        ball_r = 7
        stem_h = 15                       # the read is the BARE gap below the ball
        cy = base - stem_h - ball_r
        pygame.draw.line(surf, _shade(trunk, -22), (cx + 1, base + 1), (cx + 1, cy + ball_r - 1), 3)
        pygame.draw.line(surf, trunk, (cx, base + 1), (cx, cy + ball_r - 1), 2)
        pygame.draw.line(surf, _shade(trunk, 16), (cx, base + 1), (cx, cy + ball_r - 2), 1)
        # a small soil/root collar so the long stem doesn't look like a flag pole
        pygame.draw.line(surf, dark, (cx - 2, base), (cx + 2, base), 2)
        pygame.draw.circle(surf, dark, (cx, cy), ball_r)
        pygame.draw.circle(surf, mid, (cx, cy), ball_r - 1)
        pygame.draw.circle(surf, top, (cx - ball_r // 3, cy - ball_r // 3), max(1, ball_r // 3))
        return
    radii = {2: (7, 5), 3: (6, 5, 4)}[tiers]
    # bare stem connecting the balls
    total_h = sum(r * 2 - 2 for r in radii) + 4
    pygame.draw.line(surf, trunk, (cx, base + 1), (cx, base - total_h), 2)
    pygame.draw.line(surf, _shade(trunk, 16), (cx, base + 1), (cx, base - total_h), 1)
    cy = base - 2
    for i, r in enumerate(radii):
        cy -= r
        pygame.draw.circle(surf, dark, (cx, cy), r)
        pygame.draw.circle(surf, mid, (cx, cy), r - 1)
        pygame.draw.circle(surf, top, (cx - r // 3, cy - r // 3), max(1, r // 3))
        cy -= r - 2


def _sp_flowering(surf, cx, rim_y, v, night, t):
    """Flowering pot — a low rounded crown DENSELY studded with muted seasonal
    blossom (plum/camellia). The blossom mass is the read, not stray dots. Day
    chroma is knocked a notch (`day_chroma`) so the pop doesn't approach focal
    beside the coin in peripheral motion."""
    P, A = v.palette, v.attrs
    dark, mid, top = _foliage(P, night)
    base = rim_y
    sway = math.sin(t * 1.6) * 0.6
    for dx, dy, rw, rh in ((-5, -3, 6, 5), (5, -4, 6, 5), (0, -8, 7, 6)):
        _dome(surf, cx + dx, base + dy, rw, rh, dark, mid)
    bloom = P.get("accent", (210, 130, 150))
    dc = A.get("day_chroma", 188)
    ac = _accent(bloom, night, day_ceil=dc)
    ac_lt = _accent(_shade(bloom, 26), night, day_ceil=dc)
    # a dense scatter of 5-petal rosette blossoms across the crown
    spots = ((-6, -5), (-2, -9), (3, -7), (6, -3), (1, -12), (-5, -10),
             (5, -9), (-1, -4), (4, -11))
    for i, (bx, byp) in enumerate(spots):
        px, py = cx + bx + int(sway * (byp < -8)), base + byp
        col = ac if i % 3 else ac_lt
        pygame.draw.circle(surf, _accent(_shade(bloom, -28), night, day_ceil=dc), (px, py), 2)
        pygame.draw.circle(surf, col, (px, py), 1)


def _sp_bamboo(surf, cx, rim_y, v, night, t):
    """Bamboo clump — tall thin SEGMENTED canes with sparse leaf tufts, no crown.
    The tallest, most vertical, airiest silhouette."""
    P = v.palette
    dark, mid, top = _foliage(P, night)
    cane = _retint(P.get("trunk", (150, 178, 108)), night)
    cane_dk = _shade(cane, -34)
    cane_lt = _shade(cane, 16)
    base = rim_y
    for dx, htop, lean in ((-4, 26, -1), (0, 34, 0), (4, 29, 2), (7, 22, 2)):
        cxp = cx + dx
        segs = 5
        for s in range(segs):
            y0 = base - htop * s // segs
            y1 = base - htop * (s + 1) // segs
            nx0 = cxp + int(lean * (s / segs))
            nx1 = cxp + int(lean * ((s + 1) / segs))
            pygame.draw.line(surf, cane, (nx0, y0), (nx1, y1 + 1), 2)
            pygame.draw.line(surf, cane_lt, (nx0, y0), (nx1, y1 + 1), 1)
            pygame.draw.line(surf, cane_dk, (nx1 - 1, y1), (nx1 + 1, y1), 1)
        tipx = cxp + lean
        _leaf_tuft(surf, tipx, base - htop, 1.6, 7, mid, n=3, spread=0.7)
        _leaf_tuft(surf, tipx, base - htop, 2.0, 6, top, n=2, spread=0.5)
        _leaf_tuft(surf, tipx, base - htop + 4, 1.2, 5, dark, n=2, spread=0.6)


def _leaf_tuft(surf, ox, oy, ang, length, col, *, n=4, spread=0.5):
    for i in range(n):
        a = ang + (i - (n - 1) / 2) * spread / max(1, n - 1)
        ex = ox + int(math.cos(a) * length)
        ey = oy - int(math.sin(a) * length)
        mx = ox + int(math.cos(a) * length * 0.5)
        my = oy - int(math.sin(a) * length * 0.5) - 1
        pygame.draw.lines(surf, col, False, [(ox, oy), (mx, my), (ex, ey)], 1)


def _sp_vine(surf, cx, rim_y, v, night, t):
    """Trailing fern / ivy draping over the trough — drawn as ONE CONNECTED
    CURTAIN, not separate threads.

    Round 2 hung 3 thin ropes as parallel verticals with gaps, so at 1x/night it
    read as spider-legs / a broken bracket. This rebuild fixes the read three
    ways: (a) a WIDE fern crown anchors the top so the eye lands on a plant, not
    on dangling string; (b) every draped strand JOINS into that crown at the top
    and the cascade FANS outward (left ropes lean left, right ropes lean right)
    so it spreads into a skirt instead of dropping straight; (c) the gaps between
    adjacent strands are FILLED with a darker foliage web — the silhouette is one
    continuous draped curtain. The lower edge is a single scalloped hem so the
    bottom reads as a connected skirt, never as three feet.  TEST: at 1x NIGHT it
    must read as "plant draping over a trough," never as legs."""
    P = v.palette
    dark, mid, top = _foliage(P, night)
    web = _mix(dark, (0, 0, 0), 0.18)     # the in-between fill that fuses strands
    base = rim_y
    sway = math.sin(t * 1.8)

    # --- WIDE fern crown: the visual anchor sitting across the whole trough lip,
    #     wider than any single strand so the read starts at "plant".
    _dome(surf, cx - 4, base - 3, 6, 4, dark, mid)
    _dome(surf, cx + 4, base - 3, 6, 4, dark, mid)
    _dome(surf, cx, base - 5, 7, 5, dark, mid, top)
    for ang in (2.5, 2.1, 1.7, 1.3, 0.9, 0.5):
        _leaf_tuft(surf, cx, base - 5, ang, 7, mid, n=2, spread=0.5)
    for ang in (2.3, 1.6, 0.9):
        _leaf_tuft(surf, cx, base - 5, ang, 8, top, n=1, spread=0.0)

    # --- the CURTAIN: strands all start under the crown rim and FAN out, tips
    #     spreading wider than the heads. Build each strand's point list first so
    #     adjacent strands can be web-filled into one connected sheet.
    #     (head_x, length, fan-bias, tail-sway)
    strands = ((-7, 16, -3, 1.4), (-3, 19, -1, 1.8), (1, 20, 1, 2.0),
               (5, 17, 3, 1.6))
    paths = []
    for hx, ln, fan, swv in strands:
        pts = [(cx + hx, base - 1)]
        for i in range(1, ln + 1):
            tt = i / ln
            # fan: tip drifts outward with depth; small breathing sway on the tail
            px = cx + hx + int(fan * tt * tt) - int(math.sin(tt * 1.6) * (swv * 0.4)) \
                + int(sway * tt * 1.3)
            py = base - 1 + int(tt * (ln + 2))
            pts.append((px, py))
        paths.append(pts)

    # FILL the wedges between neighbouring strands so the gaps become foliage,
    # not background — this is what converts 4 ropes into ONE curtain.
    for a, b in zip(paths, paths[1:]):
        n = min(len(a), len(b))
        poly = a[:n] + list(reversed(b[:n]))
        if len(poly) >= 3:
            pygame.draw.polygon(surf, web, poly)

    # a single scalloped HEM tying all the tips into one connected bottom edge
    hem = [p[-1] for p in paths]
    hem_full = [paths[0][-3] if len(paths[0]) >= 3 else paths[0][0]] + hem \
        + [paths[-1][-3] if len(paths[-1]) >= 3 else paths[-1][0]]
    pygame.draw.lines(surf, dark, False, hem_full, 2)

    # the strand cores on top of the web so the curtain still has internal ribs
    for pts in paths:
        pygame.draw.lines(surf, dark, False, pts, 2)
        pygame.draw.lines(surf, mid, False, pts, 1)

    # bold teardrop leaves clinging along the curtain + lit tips, spaced so the
    # texture reads as foliage rather than dots
    for k, pts in enumerate(paths):
        ln = len(pts)
        for ni in (max(2, ln // 3), max(3, (2 * ln) // 3), ln - 1):
            if ni >= ln:
                continue
            px, py = pts[ni]
            side = -1 if k < 2 else 1
            pygame.draw.polygon(surf, mid, [
                (px, py - 1), (px + side * 3, py), (px, py + 2)])
            pygame.draw.polygon(surf, dark, [
                (px, py - 1), (px + side * 3, py), (px, py + 2)], 1)
        pygame.draw.circle(surf, top, pts[-1], 1)


def _sp_flovine(surf, cx, rim_y, v, night, t):
    """Cascading FLOWERING vine (wisteria/bougainvillea idiom) — the 2nd floral,
    a genuinely DIFFERENT FORM from the rounded flowering mound.

    Round 2's blossoms tracked thin strands painted down the urn FACE, so they
    read as magenta STRIPES on the pot, not bloom hanging off a plant. This
    rebuild fixes the read three ways: (a) the blossom falls ORIGINATE from a
    leafy head that sits proud of the urn mouth, and they hang OUTSIDE the urn's
    belly width so they BREAK the vessel silhouette — bloom in front of / past
    the pot edge reads as plant, paint inside the edge reads as glaze; (b) the
    blossoms are CLUMPED into 2-3 dense fall-points (grape-like racemes) instead
    of an even vertical scatter — a clump reads as a flower cluster, evenly
    spaced pixels read as texture; (c) the toned chroma is unchanged.  Night cap
    re-audited so the denser clumps stay under the coin."""
    P, A = v.palette, v.attrs
    dark, mid, top = _foliage(P, night)
    base = rim_y
    sway = math.sin(t * 1.7)

    # a leafy head proud of the urn mouth — wider than the neck so the falls can
    # spring from its OUTER edges and overhang the belly.
    _dome(surf, cx - 5, base - 4, 6, 4, dark, mid)
    _dome(surf, cx + 5, base - 4, 6, 4, dark, mid)
    _dome(surf, cx, base - 6, 7, 5, dark, mid, top)

    bloom = P.get("accent", (200, 132, 170))
    dc = A.get("day_chroma", 172)
    ac = _accent(bloom, night, day_ceil=dc)
    ac_dk = _accent(_shade(bloom, -30), night, day_ceil=dc)
    ac_lt = _accent(_shade(bloom, 22), night, day_ceil=dc)

    # 3 racemes (flower falls). Each springs from the OUTER edge of the head and
    # hangs OUTSIDE the urn belly (belly half-width ~9, so starts x ~ +-7..8 and
    # drapes past +-9) so it overhangs / breaks the vessel outline.  A short green
    # stem connects each cluster to the head, then a CLUMP of blossom fans down.
    #   (origin_x, stem_len, drift, clump_h, clump_w)
    falls = ((-8, 4, -3, 7, 3), (8, 4, 3, 7, 3), (0, 6, 0, 9, 4))
    for fi, (ox, slen, drift, ch, cw) in enumerate(falls):
        sx = cx + ox
        # green connecting stem so the cluster clearly hangs FROM the head
        stem_pts = []
        for i in range(slen + 1):
            tt = i / slen
            px = sx + int(drift * tt) + int(sway * tt * 1.0)
            py = base - 2 + int(tt * slen)
            stem_pts.append((px, py))
        if len(stem_pts) >= 2:
            pygame.draw.lines(surf, dark, False, stem_pts, 1)
        topx, topy = stem_pts[-1]
        # the CLUMP: a dense teardrop raceme of blossom, widest near the top and
        # tapering to a point — grape/wisteria cluster, not an even streak.
        for j in range(ch):
            jt = j / max(1, ch - 1)
            half = max(0, int(round(cw * (1 - jt) * 0.5 + 0.5)))
            yy = topy + j + int(sway * jt * 1.2)
            xx = topx + int(drift * jt * 0.4)
            # dark blossom base across the clump width
            pygame.draw.line(surf, ac_dk, (xx - half, yy), (xx + half, yy), 1)
            # mid blossom dabs at the clump edges (the petals catching colour)
            if half >= 1:
                pygame.draw.circle(surf, ac, (xx - half, yy), 1 if half >= 2 else 0)
                pygame.draw.circle(surf, ac, (xx + half, yy), 1 if half >= 2 else 0)
            # a single lit petal up high in each clump
            if j == 1:
                pygame.draw.circle(surf, ac_lt, (xx, yy), 0)
        # a small tip bud
        pygame.draw.circle(surf, ac, (topx + int(drift * 0.4), topy + ch), 0)


def _sp_kumquat(surf, cx, rim_y, v, night, t):
    """Kumquat fruiting TREE — a short bare trunk lifting a TALL, more-OPEN airy
    canopy studded with small ORANGE fruit dots (CNY wealth plant). Round 1 read
    as 'shrub + orange dots' beside G1; this raises the canopy on a trunk and
    opens it so the silhouette is a little tree, not a dome. Fruit = warm accent
    held under the coin."""
    P = v.palette
    dark, mid, top = _foliage(P, night)
    trunk = _retint(P.get("trunk", (120, 88, 56)), night)
    base = rim_y
    # short bare trunk lifting the canopy clear of the rim
    th = 8
    pygame.draw.line(surf, _shade(trunk, -18), (cx + 1, base + 1), (cx + 1, base - th), 2)
    pygame.draw.line(surf, trunk, (cx, base + 1), (cx, base - th), 2)
    cy = base - th
    # open, slightly taller canopy: spaced domes with gaps that read as airy
    for dx, dy, rw, rh in ((-6, 1, 5, 5), (6, 1, 5, 5), (0, -5, 6, 6), (-3, -3, 4, 4), (4, -4, 4, 4)):
        _dome(surf, cx + dx, cy + dy, rw, rh, dark, mid, top)
    fruit = P.get("accent", (224, 146, 56))
    fc = _accent(fruit, night)
    fc_lt = _accent(_shade(fruit, 26), night)
    for bx, byp in ((-6, 1), (-1, -3), (4, -1), (6, -6), (-4, -6),
                    (1, -8), (7, 1), (-7, -2), (2, -5)):
        px, py = cx + bx, cy + byp
        pygame.draw.circle(surf, _accent(_shade(fruit, -30), night), (px, py), 2)
        pygame.draw.circle(surf, fc, (px, py), 1)
        pygame.draw.circle(surf, fc_lt, (px - 1, py - 1), 0)


def _sp_wishtree(surf, cx, rim_y, v, night, t):
    """Temple WISH-TREE — a gnarled trunk + a broad WEEPING canopy HUNG with
    fluttering red prayer ribbons (Lam Tsuen / Longhua banyan). Differentiated
    from the other trees by canopy FORM: a wide, low, drooping crown whose outer
    fronds weep downward, not a tall compact mass — so the single wish-tree reads
    distinct without leaning on ribbon density (which doesn't survive true size).
    The ribbon RED is knocked a notch at night (`night_chroma`) so it doesn't
    approach focal beside the coin in peripheral motion."""
    P, A = v.palette, v.attrs
    dark, mid, top = _foliage(P, night)
    trunk = _retint(P.get("trunk", (96, 66, 42)), night)
    m = A.get("mass", 1.1)
    nrib = A.get("ribbons", 5)
    base = rim_y
    # gnarled trunk climbing into the canopy
    th = int(13 * m)
    pygame.draw.line(surf, _shade(trunk, -20), (cx, base + 1), (cx - 1, base - th // 2), 3)
    pygame.draw.line(surf, trunk, (cx, base + 1), (cx - 1, base - th // 2), 2)
    pygame.draw.line(surf, trunk, (cx - 1, base - th // 2), (cx + 1, base - th), 2)
    cy = base - th - int(4 * m)
    # BROAD WEEPING canopy: a wide low crown plus drooping outer lobes that hang
    # down past the crown line — the weeping-banyan read.
    span = int(11 * m)
    crown = (((-7, 2), 6), ((7, 2), 6), ((0, -3), 8), ((-4, -4), 5), ((5, -4), 5),
             ((0, 4), 6))
    for (ox, oy), r in crown:
        rr = int(r * m)
        _dome(surf, cx + int(ox * m), cy + oy, rr, int(rr * 0.82), dark, mid)
    pygame.draw.circle(surf, top, (cx - 2, cy - 3), int(2 * m))
    # weeping fronds: short drooping foliage tongues hanging off the canopy edge
    for a in (-1.0, -0.6, -0.2, 0.2, 0.6, 1.0):
        fx = cx + int(a * span)
        fy = cy + int(3 + abs(a) * 3)
        droop = int(round(math.sin(t * 1.6 + a * 2.0) * 1.0))
        pts = [(fx, fy), (fx + droop, fy + 4), (fx + droop, fy + 7)]
        pygame.draw.lines(surf, dark, False, pts, 2)
        pygame.draw.lines(surf, mid, False, pts, 1)
    # fluttering red prayer ribbons hung across the canopy underside
    nc = A.get("night_chroma_drop", 0)   # extra night-only red cool, applied below
    rib_col = P.get("accent", (200, 60, 56))
    rib = _accent(rib_col, night)
    if night > 0.05 and nc:
        rib = _mix(rib, (66, 72, 96), nc)
    rib_l = _accent(_shade(rib_col, 24), night)
    if night > 0.05 and nc:
        rib_l = _mix(rib_l, (66, 72, 96), nc)
    for i in range(nrib):
        a = (i / max(1, nrib - 1)) * 2 - 1            # -1..1 across the canopy
        rx = cx + int(a * span * 0.8)
        ry = cy + int(4 + abs(a) * 3)
        flut = int(round(math.sin(t * 2.2 + i * 1.3) * 1.5))
        pygame.draw.line(surf, rib, (rx, ry), (rx + flut, ry + 6), 2)
        pygame.draw.line(surf, rib_l, (rx, ry), (rx + flut, ry + 2), 1)


# ════════════════════════════════════════════════════════════════════════════
# THE POOL — foreground_variants.Variant rows (data, not bespoke functions)
# 10 distinct silhouettes: VESSEL x SPECIES combinations.  8 of 10 are LOCKED
# from round 2 (approved). Round 3 only reworks G6 (flovine) + G8 (vine).
# ════════════════════════════════════════════════════════════════════════════

class _V:
    def __init__(self, palette, *, attrs=None):
        self.palette = palette
        self.attrs = dict(attrs or {})


# palette role banks reused across rows
TERRA = dict(vessel=(176, 104, 70), vessel_dk=(120, 64, 42))
URN = dict(vessel=(228, 230, 234), vessel_dk=(170, 176, 188), glaze=(72, 104, 168))
TUB = dict(vessel=(140, 100, 62), vessel_dk=(92, 62, 38))
BAMBOO_V = dict(vessel=(156, 166, 100), vessel_dk=(96, 108, 60))
STONE = dict(vessel=(156, 148, 130), vessel_dk=(104, 98, 86))

FOL_LEAFY = dict(foliage_dark=(40, 84, 54), foliage_mid=(62, 116, 74), foliage_top=(104, 158, 100))
FOL_DARK = dict(foliage_dark=(30, 64, 48), foliage_mid=(44, 88, 62), foliage_top=(74, 122, 86))
FOL_CLIP = dict(foliage_dark=(46, 86, 56), foliage_mid=(72, 120, 78), foliage_top=(118, 162, 110))


def _row(*banks, **attrs):
    pal = {}
    for b in banks:
        pal.update(b)
    return _V(pal, attrs=attrs)


POOL = [
    ("G1 terracotta SHRUB", _row(
        TERRA, FOL_LEAFY, dict(accent=(206, 120, 138)),
        vessel="terracotta", species="shrub", mass=1.0),
     "vessel:terracotta(flared tapered pot) species:shrub(round bushy domes) accent:muted-rose dots | warm clay + leafy green — DEFAULT, replaces today's shrub planter [LOCKED: approved]"),

    ("G2 stone-trough CONIFER", _row(
        STONE, FOL_DARK,
        vessel="trough", species="conifer", vlift=0.10),
     "vessel:trough(low granite basin, NIGHT value +5% so it won't merge with dark ground) species:conifer(tall stacked-tier cone) | dark cypress SPIRE — replaces today's conifer planter [LOCKED: approved]"),

    ("G3 glazed-urn TOPIARY-3", _row(
        URN, FOL_CLIP,
        vessel="urn", species="topiary", tiers=3, trunk=(96, 84, 66)),
     "vessel:urn(blue-white belly+neck, painted glaze band) species:topiary tiers:3(stacked clipped balls on a bare stem) | porcelain + geometric balls [LOCKED: approved]"),

    ("G4 terracotta TOPIARY-1 (lollipop)", _row(
        TERRA, FOL_CLIP,
        vessel="terracotta", species="topiary", tiers=1, trunk=(110, 84, 56)),
     "vessel:terracotta species:topiary tiers:1(EXAGGERATED lollipop: long BARE stem + one ball lifted clear of the rim) | unmistakable vs the solid domes [LOCKED: approved]"),

    ("G5 glazed-urn FLOWERING(plum)", _row(
        URN, FOL_DARK, dict(accent=(204, 122, 142)),
        vessel="urn", species="flowering", day_chroma=170),
     "vessel:urn species:flowering accent:muted PLUM blossom (dense 5-petal scatter, DAY chroma knocked down a notch) | white urn separates it from the terracotta crowd [LOCKED: approved]"),

    ("G6 glazed-urn FLOWERING-VINE(cascade)", _row(
        URN, FOL_LEAFY, dict(accent=(192, 120, 168)),
        vessel="urn", species="flovine", day_chroma=172),
     "vessel:urn species:flovine | R3 REBUILD: 3 blossom RACEMES spring from a leafy head proud of the urn mouth and OVERHANG the belly (break the vessel outline) — CLUMPED falls, not even stripes, so it reads as bloom HANGING OFF the plant, not paint on the pot [FIXED]"),

    ("G7 bamboo-planter BAMBOO", _row(
        BAMBOO_V, FOL_LEAFY, dict(trunk=(150, 178, 108)),
        vessel="bamboo", species="bamboo"),
     "vessel:bamboo(lashed cane cylinder) species:bamboo(tall thin segmented canes, sparse leaf tufts, NO crown) | the tallest/airiest vertical silhouette [LOCKED: the standout]"),

    ("G8 stone-trough VINE/FERN", _row(
        STONE, FOL_LEAFY, dict(vlift=0.10),
        vessel="trough", species="vine"),
     "vessel:trough species:vine | R3 REBUILD: WIDE fern crown anchor + a CONNECTED CURTAIN — strands join into the crown, FAN outward, and the gaps between them are FILLED into one draped skirt with a single scalloped hem | reads as plant draping over the trough, never spider-legs [FIXED]"),

    ("G9 terracotta KUMQUAT (fruiting tree)", _row(
        TERRA, FOL_DARK, dict(accent=(222, 142, 52), trunk=(120, 88, 56)),
        vessel="terracotta", species="kumquat"),
     "vessel:terracotta species:kumquat(short bare TRUNK lifting a TALLER, more-OPEN airy canopy of orange fruit — a little tree, not a dome) | distinct vs G1 shrub [LOCKED: approved]"),

    ("G10 WISH-TREE (broad weeping)", _row(
        URN, FOL_DARK, dict(trunk=(96, 66, 42), accent=(192, 64, 60)),
        vessel="urn", species="wishtree", mass=1.15, ribbons=6, night_chroma_drop=0.22),
     "vessel:urn species:wishtree mass:1.15(TALLER than a pot) FORM:broad WEEPING crown with drooping outer fronds + red prayer ribbons (NIGHT red toned a notch) | the single wish-tree, distinct by canopy FORM [LOCKED: approved]"),
]

POTS = POOL[:9]       # true-size 'pots' band (the 9 pot/shrub-scale designs)
TREES = POOL[9:]      # true-size 'trees/large' band (the wish-tree)


# ════════════════════════════════════════════════════════════════════════════
# SHEET RENDERER  (matches the shipped-family round_2 house style)
# ════════════════════════════════════════════════════════════════════════════

WIDTH = 1200
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
    """A coarse adult-pedestrian stand-in so a pot reads CLEARLY shorter than a
    person and a wish-tree reads taller."""
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
    """A coarse food-stall booth stand-in (posts + striped awning) for scale in
    the composite, echoing the food_stalls family."""
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


def _cell(parent, name, v, note, x, y, w, h, night):
    """One annotated cell: TRUE far-lane figure + a WORKING 4x zoom inset, on a
    day or night deck, with the species/vessel/attrs + palette-roles note."""
    is_night = night > 0.5
    bg = BG_NIGHT if is_night else BG_DAY
    cell = pygame.Surface((w, h))
    cell.fill(bg)
    deck = _mix(bg, (0, 0, 0), 0.18)
    base = h - 16
    pygame.draw.rect(cell, deck, (0, base, w, h - base))
    pygame.draw.line(cell, _shade(bg, 24), (0, base), (w, base), 1)

    # TRUE far-lane figure (two t-phases to show ribbon flutter / vine sway)
    fx0 = 26
    for i, tt in enumerate((0.3, 1.4)):
        cxp = fx0 + i * 40
        draw_greenery(cell, cxp, base, v, night, tt)
    _text(cell, "TRUE far-lane", fx0 - 14, base + 4, 8, _shade(bg, 50))

    # WORKING zoom inset — native canvas sized to a plant box, seated with
    # headroom for a wish-tree canopy, then NEAREST-scaled (no smooth) so the
    # authored pixels stay crisp.
    SC_W, SC_H = 36, 44
    nat = pygame.Surface((SC_W, SC_H), pygame.SRCALPHA)
    deck_y = SC_H - 5
    nat.fill((*_mix(bg, (0, 0, 0), 0.18), 130), (0, deck_y, SC_W, SC_H - deck_y))
    draw_greenery(nat, SC_W // 2, deck_y, v, night, 0.9)
    z = 4
    zoom = pygame.transform.scale(nat, (SC_W * z, SC_H * z))
    zw, zh = zoom.get_size()
    zx, zy = w - zw - 8, 20
    pygame.draw.rect(cell, _shade(bg, -20), (zx - 2, zy - 2, zw + 4, zh + 4))
    cell.blit(zoom, (zx, zy))
    pygame.draw.rect(cell, _shade(bg, 40), (zx - 2, zy - 2, zw + 4, zh + 4), 1)
    _text(cell, "4x zoom (nearest)", zx, zy - 12, 8, _shade(bg, 60))

    # an adult stand-in beside the figure so scale reads in-cell
    _adult_ref(cell, fx0 + 96, base, night)
    _text(cell, "adult", fx0 + 84, base + 4, 8, _shade(bg, 50))
    _gold_coin(cell, fx0 + 96, 30, r=6)

    _text(cell, name, 6, 4, 12, (240, 236, 226), bold=True)
    fnt = _font(9, False)
    line = ""; yy = 20
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
    y += 20
    band_h = 64
    row = pygame.Surface((WIDTH - PAD * 2, band_h))
    bg = BG_NIGHT if night > 0.5 else BG_DAY
    row.fill(bg)
    deck = _mix(bg, (0, 0, 0), 0.18)
    base = band_h - 14
    pygame.draw.rect(row, deck, (0, base, WIDTH - PAD * 2, 14))
    pygame.draw.line(row, _shade(bg, 26), (0, base), (WIDTH - PAD * 2, base), 1)
    # adult yardstick at the far left of the band
    _adult_ref(row, 34, base, night)
    _text(row, "adult", 18, base + 1, 8, _shade(bg, 50))
    _gold_coin(row, WIDTH - PAD * 2 - 20, base - 12)
    _text(row, "coin", WIDTH - PAD * 2 - 38, base + 1, 8, _shade(bg, 50))
    spacing = (WIDTH - PAD * 2 - 150) // len(items)
    for i, (nm, v, _n) in enumerate(items):
        cx = 80 + i * spacing
        draw_greenery(row, cx, base, v, night, 0.5 + i * 0.4)
        _text(row, nm.split(" ")[0], cx - 8, base + 1, 8,
              (70, 58, 46) if night <= 0.5 else (150, 160, 185))
    sheet.blit(row, (PAD, y))
    pygame.draw.rect(sheet, (70, 74, 90), (PAD, y, WIDTH - PAD * 2, band_h), 1)
    return y + band_h + 8


def _measure_night_cap():
    """Render every design onto a night strip exactly as the composite does, then
    scan the RENDERED pixels for the hottest greenery luma — the honest cap audit
    the footer prints. Accent dots (blossom/fruit/ribbon) are included."""
    night = 0.95
    strip = pygame.Surface((1400, 90))
    strip.fill(BG_NIGHT)
    base = 70
    x = 50
    for _nm, v, _n in POOL:
        for tt in (0.0, 0.6, 1.3):
            draw_greenery(strip, x, base, v, night, tt)
            x += 30
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
    cell_h = 116

    title_h = 56
    bandA_h = 20 + 64 + 8 + 20 + 64 + 8
    rows = (len(POOL) + 1) // 2
    detail_h = 22 + 2 * (18 + rows * (cell_h + 6))
    strip_h = 104
    comp_h = 22 + 2 * (strip_h + 6)
    total_h = title_h + bandA_h + detail_h + comp_h + PAD * 6 + 26

    sheet = pygame.Surface((WIDTH, total_h))
    sheet.fill((26, 28, 38))

    y = PAD
    _text(sheet, "SKYBIT PROMENADE — PLANTS & GREENERY (round 3): NARROW two-plant fix — G6 flowering-vine + G8 vine/fern rebuilt; the other 8 LOCKED",
          PAD, y, 17, (250, 246, 236), bold=True)
    y += 22
    _text(sheet, "AD ITERATE: 8/10 PASS + LOCKED (G1 shrub, G2 conifer, G3 topiary-3, G4 lollipop, G5 plum, G7 bamboo, G9 kumquat, G10 wish-tree). Only TWO reworked: "
                 "G8 VINE/FERN was spider-legs -> rebuilt as ONE CONNECTED CURTAIN (wide fern crown anchor; strands join the crown + FAN out; gaps web-FILLED into one draped skirt with a scalloped hem). "
                 "G6 FLOWERING-VINE read as stripes painted on the urn -> 3 CLUMPED blossom RACEMES springing from a leafy head, OVERHANGING the urn belly so bloom hangs OFF the plant. Night still <=150.",
          PAD, y, 9, (188, 186, 200))
    y += title_h - 22

    y = _true_band(sheet, y, "A1.  POTS — true far-lane size, adult + coin yardstick (a pot reads CLEARLY shorter than an adult)  [DAY]  — judge G6 + G8 here",
                   POTS, 0.0)
    y = _true_band(sheet, y, "A2.  POTS — [NIGHT]  (cooled <=150, accents held under the coin)  — G8 must read 'draping over a trough', G6 'bloom hanging off the plant'",
                   POTS, 0.95)

    _text(sheet, "B.  PER-DESIGN — TRUE far-lane (2 t-phases: ribbon flutter / vine sway) + adult ref + in-cell coin · 4x WORKING zoom (nearest) · vessel/species/attrs + palette-roles note  (DAY then NIGHT)",
          PAD, y, 12, (240, 220, 150), bold=True)
    y += 18
    for is_night in (False, True):
        night = 0.95 if is_night else 0.0
        _text(sheet, "NIGHT  (cooled <=150, nothing self-lit)" if is_night else "DAY",
              PAD, y, 11, (160, 180, 220) if is_night else (240, 210, 130), bold=True)
        y += 16
        for r in range(rows):
            for c in range(2):
                idx = r * 2 + c
                if idx >= len(POOL):
                    break
                nm, v, note = POOL[idx]
                cx = PAD + c * (cell_w + PAD)
                _cell(sheet, nm, v, note, cx, y, cell_w, cell_h, night)
            y += cell_h + 6
        y += 8

    _text(sheet, "C.  ON-STREET COMPOSITE — the final 10 side by side at true size among human-cast figures + a food stall for scale, with the coin reference  (DAY then NIGHT)  — G6 + G8 sit among the refs",
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
        # a believable promenade mix: the full final 10 flanking a stall + the
        # cast, ordered so neighbouring silhouettes contrast (round vs spire vs
        # vertical vs tree). POOL indices: 0..9 (G1..G10).
        draw_greenery(strip, 40, base, POOL[0][1], night, 0.4)     # G1 terracotta shrub
        _adult_ref(strip, 84, base, night)
        draw_greenery(strip, 124, base, POOL[1][1], night, 0.5)    # G2 trough conifer (spire)
        draw_greenery(strip, 168, base, POOL[8][1], night, 0.8)    # G9 kumquat fruiting tree
        _stall_ref(strip, 230, base, night)
        _adult_ref(strip, 284, base, night)
        draw_greenery(strip, 326, base, POOL[6][1], night, 1.1)    # G7 bamboo (vertical)
        draw_greenery(strip, 368, base, POOL[2][1], night, 0.6)    # G3 urn topiary-3
        draw_greenery(strip, 410, base, POOL[3][1], night, 0.7)    # G4 lollipop topiary-1
        _adult_ref(strip, 456, base, night)
        draw_greenery(strip, 500, base, POOL[4][1], night, 0.9)    # G5 urn flowering plum
        draw_greenery(strip, 544, base, POOL[5][1], night, 1.0)    # G6 cascading flowering-vine
        draw_greenery(strip, 590, base, POOL[7][1], night, 0.5)    # G8 trough vine/fern
        _stall_ref(strip, 654, base, night)
        _adult_ref(strip, 712, base, night)
        draw_greenery(strip, 760, base, POOL[9][1], night, 0.7)    # G10 WISH-TREE (weeping)
        _adult_ref(strip, 822, base, night)
        _gold_coin(strip, sw - 18, 20)
        _text(strip, "coin ref", sw - 46, 32, 8, _shade(bg, 60))
        _text(strip, "NIGHT" if is_night else "DAY", 4, 2, 9,
              (170, 190, 225) if is_night else (60, 50, 40), bold=True)
        sheet.blit(strip, (PAD, y))
        pygame.draw.rect(sheet, (70, 74, 90), (PAD, y, WIDTH - PAD * 2, strip_h), 1)
        y += strip_h + 6

    hottest, over = _measure_night_cap()
    coin_l = _luma((255, 232, 150))
    msg = (f"NIGHT-STRIP CAP (measured on RENDERED pixels across t-phases, incl. blossom/fruit/ribbon accents): "
           f"hottest GREENERY px luma = {hottest:.0f}  ·  px over {NIGHT_GLOW_CAP} = {over}  "
           f"·  gold-coin core luma = {coin_l:.0f} (sole brightest). "
           f"{'PASS — all greenery px <= cap.' if over == 0 else 'FAIL — '+str(over)+' px breach the cap.'}")
    _text(sheet, msg, PAD, total_h - 16, 9,
          (170, 200, 180) if over == 0 else (220, 140, 130))

    out = "/home/user/skybit/docs/sidewalk_overhaul/greenery/round_3.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("saved", out, sheet.get_size())
    print(f"night-strip cap: hottest greenery luma={hottest:.1f}  over-cap px={over}  coin={coin_l:.1f}")


if __name__ == "__main__":
    render()
