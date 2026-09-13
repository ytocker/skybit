"""Promenade PLANTS & GREENERY — round 5 candidate-sheet generator.

GREENERY POOL EXPANSION, batch 1 of 4 — REVISION of round 4 on art-director
notes (VERDICT: ITERATE — no drops, all 5 concepts distinct; four read well,
P13 PLUM was the gating fix). The shipped pool is 10 designs
(docs/sidewalk_overhaul/greenery/round_3.png, art-director SHIP-READY); this
batch GROWS it with FIVE genuinely NEW flowering/seasonal species authored to
the EXACT same instructions as those 10 — the SAME crisp native far-lane pixel
pipeline (pure pygame.draw.* on an SRCALPHA surface, NO numpy/gfxdraw/PIL/
smoothscale), the SAME palette banks, the SAME night-cap contract (foliage +
vessels cool toward (54,64,96) <=150 via _retint; every bloom/berry/seasonal
accent held under the hard 132 night ceiling via _accent so nothing out-pops the
~230 gold coin). The existing 10 are UNCHANGED; these become pool indices 10-14.

ROUND-5 CHANGES (art-director punch list, prioritised):
  1. (GATING) P13 PLUM — the blossom must BECOME the silhouette: ~doubled the
     bloom count, concentrated at branch tips/joints as 2x2 pink-white CLUSTERS
     (not single dots), each with one warm-white centre pixel. A viewer reads
     "blossom" before "dead branch" in the day band.
  2. (GATING) P13 PLUM — lifted the ink zig-zag value one step (a lighter
     branch) and thinned the densest low tangle near the vessel so the airy
     angular read survives at far size; the top zig-zags stay the signature.
  3. P15 NARCISSUS — lifted the flowers off invisibility: 4 readable white cups
     with a gold-cup CENTRE dot each; raised the pebble-dish RIM contrast one
     value step so it survives the NIGHT band. Still the most delicate read.
  4. P14 MAPLE — broke the canopy blob: a darker MAROON notch on the canopy
     underside + an amber rim-lit top edge so the crown reads as clustered leaf
     MASSES, not a solid disc; the wooden-tub iron hoops keep trough/urn-level
     rim contrast so it reads as a vessel, not a crate.
  5. P12 CHRYSANTHEMUM — nudged the top rosettes one value brighter so it reads
     "studded with many tiny blooms," not a flat mound; still lower/wider than
     the peony.
  6. P11 PEONY (batch anchor — KEEP) — trimmed ONE row of leaf pixels under the
     heads so the big blooms stay the unambiguous focal. Otherwise unchanged.

This generator IMPORTS the shipped helpers from game.greenery_cast (the
production _retint / _accent / _mix / _shade / _draw_vessel / _foliage / _dome /
_leaf_tuft / draw_greenery + VESSEL_H) so the explorations are drawn by the real
code path, then registers the 5 new _sp_* drawers into the SAME dispatch dict the
production draw_greenery reads. Nothing here mutates production game files.

Sheet layout MIRRORS round 4: true far-lane DAY + NIGHT bands with an adult +
gold-coin yardstick, per-design DAY/NIGHT cells (true far size + 4x nearest zoom
+ vessel/species/attrs note), an on-street composite with shipped siblings, and
the _measure_night_cap() audit footer (PASS only when hottest greenery <=150 and
the coin ~230 stays sole-brightest).
"""
from __future__ import annotations

import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((1, 1))

# Import the SHIPPED production helpers so the new species are drawn by the exact
# same code path / night-cap contract as the existing 10 — no re-implementation.
from game import greenery_cast as gc  # noqa: E402
from game.greenery_cast import (  # noqa: E402
    _retint, _accent, _hi, _mix, _shade, _luma, _dome, _foliage, _leaf_tuft,
    _draw_vessel, _night_lift, draw_greenery, VESSEL_H, NIGHT_GLOW_CAP,
)
from game import foreground_variants as fv  # noqa: E402


# ════════════════════════════════════════════════════════════════════════════
# FIVE NEW SPECIES drawers — same signature as the shipped _sp_* (surf, cx,
# rim_y, v, night, t). Vessel is drawn by the shared _draw_vessel; these draw
# the foliage/blooms above the returned rim. Foliage routes through _foliage/
# _retint; every bloom/berry/seasonal accent routes through _accent (hard 132
# night ceiling). All geometry is integer far-lane scale, pure pygame.draw.*.
# ════════════════════════════════════════════════════════════════════════════

def _sp_peony(surf, cx, rim_y, v, night, t):
    """PEONY (mudan) — the King of Flowers: a low broad-leaf clump carrying 2-3
    BIG layered double-blooms. Each head is a ruffled rosette: a dark outer
    petal-ring, a mid body, a lit inner whorl, and a pale petal-base eye — the
    Tang gongbi build (cinnabar-rose over a white base). The big rounded heads
    sitting proud above broad leaves are the silhouette; far bigger + fewer than
    the chrysanthemum's many tiny buttons, so the two flowering pots never read
    alike. Round 5: trimmed ONE row of leaf height so the heads stay the
    unambiguous focal — the leaf mass no longer crowds the bloom undersides."""
    P, A = v.palette, v.attrs
    dark, mid, top = _foliage(P, night)
    base = rim_y
    sway = math.sin(t * 1.3) * 0.6
    # broad low leaf mass — wide flat domes, one row shorter so the blooms sit
    # clearly ABOVE foliage (heads read as the focal, not garnish on a bush)
    for dx, dy, rw, rh in ((-6, 0, 7, 3), (6, 0, 7, 3), (0, -2, 8, 4)):
        _dome(surf, cx + dx, base + dy, rw, rh, dark, mid, top)
    bloom = P.get("accent", (208, 96, 110))
    dc = A.get("day_chroma", 178)
    pet_dk = _accent(_shade(bloom, -40), night, day_ceil=dc)
    pet = _accent(bloom, night, day_ceil=dc)
    pet_lt = _accent(_shade(bloom, 28), night, day_ceil=dc)
    base_pet = _accent(P.get("accent_pale", (236, 206, 200)), night, day_ceil=dc)
    # 3 big ruffled heads (one tall centre, two flanking) — drawn back-to-front
    heads = ((-6, -8, 5), (6, -9, 5), (0, -14, 6))
    for hx, hy, r in heads:
        px = cx + hx + int(sway * (hy < -10))
        py = base + hy
        # ruffled outer ring: a fat dark rosette with bumps (overlapping circles)
        for a in range(6):
            ang = a / 6 * math.tau
            ex = px + int(round(math.cos(ang) * r * 0.82))
            ey = py + int(round(math.sin(ang) * r * 0.82))
            pygame.draw.circle(surf, pet_dk, (ex, ey), 2)
        pygame.draw.circle(surf, pet_dk, (px, py), r)
        pygame.draw.circle(surf, pet, (px, py), r - 1)
        # lit upper whorl + a pale petal-base eye (white-based gongbi petal)
        pygame.draw.circle(surf, pet_lt, (px - 1, py - 1), max(1, r - 3))
        pygame.draw.circle(surf, base_pet, (px, py + 1), 1)
        pygame.draw.circle(surf, pet_dk, (px, py + 1), 1, 1)


def _sp_chrysanthemum(surf, cx, rim_y, v, night, t):
    """CHRYSANTHEMUM cushion mound — a dense LOW pincushion solidly studded with
    MANY small spoon-petal blooms (gold / russet). The read is a tight rounded
    cushion whose whole surface is bloom, not foliage with stray dots — the
    opposite of the peony's few big heads. Each bloom is a tiny spoke-rosette
    (dark base, lit centre) packed across the dome; russet shadow blooms low,
    gold blooms catching light up top. Round 5: nudged the TOP rosettes one
    value brighter so the crown reads as MANY tiny studded blooms, not a flat
    yellow mound — kept clearly lower/wider than the peony."""
    P, A = v.palette, v.attrs
    dark, mid, top = _foliage(P, night)
    base = rim_y
    sway = math.sin(t * 1.5) * 0.5
    # the cushion body — a low broad mound, just enough green to read as a base
    for dx, dy, rw, rh in ((-6, -2, 7, 5), (6, -2, 7, 5), (0, -6, 8, 6)):
        _dome(surf, cx + dx, base + dy, rw, rh, dark, mid)
    bloom = P.get("accent", (220, 162, 56))
    dc = A.get("day_chroma", 182)
    russet = P.get("accent2", (176, 96, 44))
    b_dk = _accent(_shade(bloom, -34), night, day_ceil=dc)
    b = _accent(bloom, night, day_ceil=dc)
    b_lt = _accent(_shade(bloom, 26), night, day_ceil=dc)
    # a brighter top-crown gold for the sunlit blooms (still capped via _accent)
    b_crown = _accent(_shade(bloom, 44), night, day_ceil=dc)
    r_dk = _accent(_shade(russet, -26), night, day_ceil=dc)
    r_mid = _accent(russet, night, day_ceil=dc)
    # a packed scatter of tiny spoon-rosettes covering the whole cushion surface;
    # russet (cooler) low + on the flanks, gold catching light over the crown.
    # crown=1 marks the topmost blooms that get the brighter sunlit centre.
    spots = ((-7, -2, 0, 0), (-4, -6, 1, 0), (-1, -9, 1, 1), (2, -10, 1, 1),
             (5, -7, 1, 0), (7, -3, 0, 0), (-5, -3, 0, 0), (0, -6, 1, 0),
             (3, -6, 1, 0), (-2, -4, 0, 0), (5, -3, 0, 0), (-7, -5, 0, 0),
             (1, -12, 1, 1), (-3, -10, 1, 1), (6, -9, 1, 0))
    for bx, byp, gold, crown in spots:
        px, py = cx + bx + int(sway * (byp < -8)), base + byp
        if gold:
            pygame.draw.circle(surf, b_dk, (px, py), 2)
            pygame.draw.circle(surf, b, (px, py), 1)
            # the crown blooms get a brighter lit centre so the top reads studded
            pygame.draw.circle(surf, b_crown if crown else b_lt, (px, py - 1), 0)
        else:
            pygame.draw.circle(surf, r_dk, (px, py), 2)
            pygame.draw.circle(surf, r_mid, (px, py), 1)


def _sp_plum(surf, cx, rim_y, v, night, t):
    """PLUM-BLOSSOM branch (winter meihua) — dark zig-zag dragon-branches rising
    from a slim vessel, the BLOSSOM clustered at the tips + joints so the FLOWER
    is the silhouette, not garnish on a dead twig. Round 5 (gating fix): the
    blossom count is ~doubled and rendered as 2x2 pink-white CLUSTERS (a tiny
    petal mass with a warm-white centre pip), so the eye reads "blossom" before
    "branch" in the day band. The lower branch is lightened one value step and
    its densest low tangle thinned so the airy angular read survives at far size,
    while the top zig-zags stay the signature dragon-branch outline."""
    P, A = v.palette, v.attrs
    # branch lifted one value step (lighter ink) so the lower wood doesn't read
    # as a dense dead tangle — the blossom mass, not the wood, carries the read.
    branch = _retint(_shade(P.get("trunk", (74, 58, 52)), 14), night)
    br_lt = _hi(branch, 22, night)
    base = rim_y
    sway = int(round(math.sin(t * 1.4) * 1.0))
    # 3 zig-zag dragon-branches: each a poly-line of sharp angular segments.
    # The low starts are pulled inward + the densest near-vessel tangle dropped
    # so the base is airier; the upper zig-zags keep the signature angular fork.
    branches = (
        [(0, 0), (-3, -6), (1, -11), (-2, -17), (sway, -22)],
        [(1, -4), (6, -8), (3, -13), (7, -18)],
        [(0, -6), (-5, -10), (-8, -14)],
    )
    nodes = []
    for seg in branches:
        pts = [(cx + dx, base + dy) for dx, dy in seg]
        pygame.draw.lines(surf, branch, False, pts, 2)
        # a thin lit edge up one side of each branch for the woody ridge
        pygame.draw.lines(surf, br_lt, False, [(x - 1, y) for x, y in pts], 1)
        nodes.extend(pts[1:])               # joints + tips host the blossom
    bloom = P.get("accent", (234, 198, 208))
    dc = A.get("day_chroma", 176)
    pet = _accent(bloom, night, day_ceil=dc)
    pet_dk = _accent(_shade(bloom, -34), night, day_ceil=dc)
    pet_ctr = _accent(_shade(bloom, 30), night, day_ceil=dc)   # warm-white centre
    bud = _accent(P.get("accent2", (208, 122, 140)), night, day_ceil=dc)
    # The blossom BECOMES the silhouette: most joints/tips carry a 2x2 pink-white
    # CLUSTER (a small petal mass, not a single dot) with one warm-white centre
    # pixel; the remaining nodes carry a single warm bud pip. ~Double the round-4
    # bloom count, concentrated where the eye lands (tips read as flower).
    for i, (nx, ny) in enumerate(nodes):
        if i % 3 == 2:
            pygame.draw.circle(surf, bud, (nx, ny), 0)         # unopened bud pip
        else:
            # a 2x2 petal cluster: dark seat + a bright pink quad + warm centre
            pygame.draw.rect(surf, pet_dk, (nx - 1, ny - 1, 4, 4))
            pygame.draw.rect(surf, pet, (nx - 1, ny - 1, 3, 3))
            pygame.draw.circle(surf, pet_ctr, (nx, ny), 0)


def _sp_maple(surf, cx, rim_y, v, night, t):
    """RED MAPLE (Acer palmatum) — a small palmate-leaf tree: a slim woody trunk
    forking into a broad AUTUMN canopy of clustered shaded leaf masses (the
    canopy is the warm accent, capped). Built like the kumquat tree (trunk lifts
    an open canopy) but the canopy itself is RED/ORANGE foliage in three tones
    (deep maroon shadow / vermilion body / amber lit edge) instead of green with
    fruit dots. Round 5: a darker MAROON notch is carved into the canopy
    underside and an amber rim-lit top edge added, so the crown reads as
    clustered leaf MASSES, not a solid orange disc/lollipop — a little fire-tree
    in a wooden tub whose iron hoops carry vessel-level rim contrast."""
    P, A = v.palette, v.attrs
    trunk = _retint(P.get("trunk", (96, 70, 50)), night)
    base = rim_y
    dc = A.get("day_chroma", 182)
    leaf_dk = _accent(P.get("foliage_dark", (132, 50, 40)), night, day_ceil=dc)
    leaf_mid = _accent(P.get("foliage_mid", (190, 84, 48)), night, day_ceil=dc)
    leaf_lt = _accent(P.get("foliage_top", (224, 150, 64)), night, day_ceil=dc)
    # a deep maroon for the underside shadow-notch that breaks the canopy blob
    leaf_notch = _accent(_shade(P.get("foliage_dark", (132, 50, 40)), -30), night, day_ceil=dc)
    sway = math.sin(t * 1.3) * 0.5
    # slim trunk forking into two limbs — the little-tree armature
    th = 9
    pygame.draw.line(surf, _shade(trunk, -18), (cx + 1, base + 1), (cx + 1, base - th), 2)
    pygame.draw.line(surf, trunk, (cx, base + 1), (cx, base - th), 2)
    pygame.draw.line(surf, trunk, (cx, base - th + 2), (cx - 4, base - th - 2), 1)
    pygame.draw.line(surf, trunk, (cx, base - th + 2), (cx + 4, base - th - 2), 1)
    cy = base - th - 2
    # broad autumn canopy: clustered shaded leaf masses (palmate clumps). Drawn
    # back-to-front: deep-maroon shadow lobes, vermilion body, amber lit caps.
    lobes = ((-6, 1, 5, 4), (6, 1, 5, 4), (0, -4, 6, 5),
             (-4, -3, 4, 4), (4, -3, 4, 4), (0, 2, 5, 4))
    for dx, dy, rw, rh in lobes:
        _dome(surf, cx + dx + int(sway * (dy < -2)), cy + dy, rw, rh,
              leaf_dk, leaf_mid, leaf_lt)
    # a MAROON notch carved into the canopy underside (a dark gap between the two
    # lower lobes) so the crown reads as separate clustered masses, not a disc
    pygame.draw.line(surf, leaf_notch, (cx - 1, cy + 4), (cx + 1, cy + 5), 2)
    pygame.draw.circle(surf, leaf_notch, (cx, cy + 5), 1)
    # an amber rim-lit TOP edge arcing over the crown so the upper masses catch
    # light (the fire-canopy reads lit-over-shadow, not flat)
    pygame.draw.arc(surf, leaf_lt, (cx - 6, cy - 9, 12, 11),
                    math.radians(35), math.radians(150), 1)
    # a few amber lit leaf-points catching the canopy edge (palmate tips)
    for px, py in ((-7, -2), (-2, -7), (3, -6), (7, -1), (0, -8), (-5, 2), (5, 2)):
        pygame.draw.circle(surf, leaf_lt, (cx + px, cy + py), 0)


def _sp_narcissus(surf, cx, rim_y, v, night, t):
    """NARCISSUS / paperwhite (shuixian, the Water Fairy) — a CLUMP of strappy
    upright blades fanning from a shallow dish, topped with small WHITE petals
    around a GOLD cup. The lowest, most delicate read in the family. Round 5:
    the flowers are lifted off invisibility — 4 readable white cups (a petal
    ring + a 2px dark calyx so the cup has body), each with a GOLD-cup CENTRE dot
    for a warm focal against the blue-green blades, so the bloom survives the
    NIGHT band. "Delicate" no longer means "absent.\""""
    P, A = v.palette, v.attrs
    dark, mid, top = _foliage(P, night)
    base = rim_y
    sway = math.sin(t * 1.7) * 0.8
    # a fan of strappy blades — thin near-vertical leaves splaying from the dish
    blades = ((-6, 11, -2), (-3, 14, -1), (0, 16, 0), (3, 14, 1), (6, 12, 2),
              (-1, 13, -1), (1, 15, 1))
    for ox, ln, drift in blades:
        sx = cx + ox
        tipx = sx + drift + int(sway * (ln > 13))
        midx = sx + (drift // 2)
        col = top if (ln >= 15) else mid
        pygame.draw.lines(surf, dark, False,
                          [(sx, base), (midx, base - ln // 2), (tipx, base - ln)], 1)
        pygame.draw.line(surf, col, (sx, base - 1), (midx, base - ln // 2), 1)
    bloom = P.get("accent", (236, 232, 222))
    dc = A.get("day_chroma", 180)
    pet = _accent(bloom, night, day_ceil=dc)
    pet_dk = _accent(_shade(bloom, -40), night, day_ceil=dc)
    cup = _accent(P.get("accent2", (228, 178, 56)), night, day_ceil=dc)
    cup_dk = _accent(_shade(P.get("accent2", (228, 178, 56)), -28), night, day_ceil=dc)
    # 4 readable white cup-flowers nodding at blade tips: a ring of white petals
    # over a dark calyx seat (gives the cup body so it survives night), with a
    # GOLD cup centre as the warm focal against the blue-green blades.
    for ox, ln in ((-3, 14), (2, 15), (5, 12), (-6, 11)):
        fx = cx + ox + int(sway)
        fy = base - ln
        # dark calyx seat so the white petals read as a cup, not stray pixels
        pygame.draw.circle(surf, pet_dk, (fx, fy), 2)
        for a in range(6):
            ang = a / 6 * math.tau
            ex = fx + int(round(math.cos(ang) * 1.7))
            ey = fy + int(round(math.sin(ang) * 1.7))
            pygame.draw.circle(surf, pet, (ex, ey), 0)
        pygame.draw.circle(surf, pet, (fx, fy), 1)
        # gold cup centre — the warm focal pip (dark-rimmed so it reads as a cup)
        pygame.draw.circle(surf, cup_dk, (fx, fy), 1, 1)
        pygame.draw.circle(surf, cup, (fx, fy), 0)


# A new SHALLOW DISH vessel — a low porcelain bowl of pebbles for the narcissus,
# the flattest vessel in the family (returns the rim the blade-fan plants into).
# Round 5: the rim band is lifted one value step (a brighter glaze rim + a lit
# mouth edge) so the dish doesn't vanish into the dark NIGHT ground band.
def _draw_dish(surf, cx, base_y, v, night):
    P, A = v.palette, v.attrs
    vlift = A.get("vlift", 0.0)
    pf = lambda c: _night_lift(_retint(c, night), night, vlift)
    body = pf(P.get("vessel", (224, 226, 232)))
    dk = pf(P.get("vessel_dk", (168, 174, 186)))
    lt = _hi(body, 22, night)
    g = int(base_y)
    h = 6
    top_w, bot_w = 24, 16
    ty = g - h
    # a shallow flared dish — wide mouth, short body
    pygame.draw.polygon(surf, dk, [
        (cx - top_w // 2, ty), (cx + top_w // 2, ty),
        (cx + bot_w // 2, g), (cx - bot_w // 2, g)])
    pygame.draw.polygon(surf, body, [
        (cx - top_w // 2 + 1, ty + 1), (cx + top_w // 2 - 1, ty + 1),
        (cx + bot_w // 2, g - 1), (cx - bot_w // 2, g - 1)])
    # a brighter lit mouth edge so the rim reads against the night ground band
    pygame.draw.line(surf, lt, (cx - top_w // 2 + 1, ty + 1), (cx + top_w // 2 - 2, ty + 1), 1)
    pygame.draw.line(surf, lt, (cx - top_w // 2 + 1, ty), (cx + top_w // 2 - 2, ty), 1)
    # a glaze rim band (raised one value step) + a few grey pebbles bedding bulbs
    glaze = _hi(_retint(P.get("glaze", (72, 104, 168)), night), 16, night)
    pygame.draw.line(surf, glaze, (cx - top_w // 2 + 2, ty + 3), (cx + top_w // 2 - 2, ty + 3), 1)
    peb = pf((158, 160, 166))
    for dxp in (-7, -2, 3, 7, 0):
        pygame.draw.circle(surf, peb, (cx + dxp, ty + 1), 1)
    return ty


# Patch the new species INTO the production dispatch so the shipped
# draw_greenery routes them, and wrap _draw_vessel so 'dish' resolves. This
# mirrors exactly how the folded-in greenery_cast.py will register them.
_orig_vessel = gc._draw_vessel


def _vessel_dispatch(surf, cx, base_y, v, night, kind):
    if kind == "dish":
        return _draw_dish(surf, cx, base_y, v, night)
    return _orig_vessel(surf, cx, base_y, v, night, kind)


gc._draw_vessel = _vessel_dispatch

_orig_draw = gc.draw_greenery


def draw_greenery(surf, cx, base_y, v, night, t):  # noqa: F811
    A = v.attrs
    sp = A.get("species", "shrub")
    new = {
        "peony": _sp_peony, "chrysanthemum": _sp_chrysanthemum, "plum": _sp_plum,
        "maple": _sp_maple, "narcissus": _sp_narcissus,
    }
    if sp in new:
        rim_y = gc._draw_vessel(surf, cx, base_y, v, night, A.get("vessel", "terracotta"))
        new[sp](surf, cx, rim_y, v, night, t)
    else:
        _orig_draw(surf, cx, base_y, v, night, t)


# ════════════════════════════════════════════════════════════════════════════
# THE 5 NEW ROWS — foreground_variants.Variant data (pool indices 10-14).
# Reuse the shipped palette banks (_URN/_TERRA/_TUB/_BAMBOO_V), add seasonal
# accent palettes. A dedicated FOL bank per species where the foliage colour
# matters (maple's red canopy lives in foliage_* roles, capped via _accent).
# ════════════════════════════════════════════════════════════════════════════

_URN = dict(gc._URN)
_TERRA = dict(gc._TERRA)
_TUB = dict(gc._TUB)
_BAMBOO_V = dict(gc._BAMBOO_V)
_FOL_LEAFY = dict(gc._FOL_LEAFY)
_FOL_DARK = dict(gc._FOL_DARK)
# broad grass-green peony/mum/narcissus leaf bank (Tang gongbi "grass green")
_FOL_BROAD = dict(foliage_dark=(36, 78, 50), foliage_mid=(58, 110, 70), foliage_top=(100, 152, 96))
# maple AUTUMN canopy carried in the foliage roles (warm; capped via _accent)
_FOL_MAPLE = dict(foliage_dark=(132, 50, 40), foliage_mid=(192, 86, 48), foliage_top=(226, 150, 66))


def _row(*banks, **attrs):
    pal = {}
    for b in banks:
        pal.update(b)
    return fv.Variant(palette=pal, attrs=dict(attrs))


POOL = [
    ("P11 glazed-urn PEONY (mudan)", _row(
        _URN, _FOL_BROAD, dict(accent=(208, 90, 108), accent_pale=(236, 208, 202)),
        vessel="urn", species="peony", day_chroma=178),
     "vessel:urn(blue-white belly+neck) species:peony accent:cinnabar-rose double-bloom + pale white petal-base | 2-3 BIG layered ruffled heads (King of Flowers) over a TRIMMED grass-green leaf row — heads stay the unambiguous focal, far fewer/bigger than the mum"),

    ("P12 terracotta CHRYSANTHEMUM", _row(
        _TERRA, _FOL_BROAD, dict(accent=(222, 164, 56), accent2=(178, 98, 46)),
        vessel="terracotta", species="chrysanthemum", day_chroma=182),
     "vessel:terracotta species:chrysanthemum accent:gold spoon-bloom + accent2:russet | a DENSE LOW cushion mound SOLIDLY studded with many tiny spoke-rosettes; the TOP crown blooms nudged one value brighter so it reads many-studded, not a flat mound — lower/wider than the peony"),

    ("P13 bamboo-planter PLUM (meihua)", _row(
        _BAMBOO_V, dict(trunk=(74, 58, 52), accent=(236, 200, 210), accent2=(210, 124, 142)),
        vessel="bamboo", species="plum", day_chroma=176),
     "vessel:bamboo(slim lashed-cane cylinder) species:plum trunk:LIFTED ink branch accent:pink-white 2x2 blossom CLUSTERS (warm-white centre) + accent2:bud | BLOSSOM-FIRST read — doubled clusters at tips/joints carry the silhouette over lightened/thinned zig-zag dragon-branches"),

    ("P14 wooden-tub RED MAPLE", _row(
        _TUB, _FOL_MAPLE, dict(trunk=(96, 70, 50)),
        vessel="tub", species="maple", day_chroma=182),
     "vessel:tub(staved wooden barrel, iron hoops at vessel-level rim contrast) species:maple | small palmate-leaf tree: slim forking trunk + AUTUMN canopy (maroon shadow / vermilion body / amber lit edge) with a MAROON underside notch + amber rim-lit top — clustered leaf masses, not a disc"),

    ("P15 dish NARCISSUS (water fairy)", _row(
        _URN, _FOL_BROAD, dict(accent=(238, 234, 224), accent2=(230, 180, 58)),
        vessel="dish", species="narcissus", day_chroma=180),
     "vessel:dish(NEW low porcelain bowl, RIM lifted one value step for night) species:narcissus accent:white cup petals + accent2:gold cup centre | a low FAN of blades topped with 4 READABLE white-and-gold cup flowers (shuixian) — delicate but NOT absent, survives night"),
]

POTS = POOL          # all five are pot/shrub scale (the maple is a little tree
                     # but sits within pot-band height)


# ════════════════════════════════════════════════════════════════════════════
# SHEET RENDERER  (mirrors tools/_greenery_round3.py house style)
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
    person (lifted from the round_3 generator)."""
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


def _shipped_ref(surf, cx, base_y, night, idx, t):
    """Draw one of the SHIPPED 10 designs (via the production registry) as a
    sibling-look reference so the new species sit beside the round_3 family."""
    pool = fv.pool("greenery")
    if idx < len(pool):
        _orig_draw(surf, cx, base_y, pool[idx], night, t)


def _cell(parent, name, v, note, x, y, w, h, night):
    is_night = night > 0.5
    bg = BG_NIGHT if is_night else BG_DAY
    cell = pygame.Surface((w, h))
    cell.fill(bg)
    deck = _mix(bg, (0, 0, 0), 0.18)
    base = h - 16
    pygame.draw.rect(cell, deck, (0, base, w, h - base))
    pygame.draw.line(cell, _shade(bg, 24), (0, base), (w, base), 1)

    fx0 = 26
    for i, tt in enumerate((0.3, 1.4)):
        cxp = fx0 + i * 40
        draw_greenery(cell, cxp, base, v, night, tt)
    _text(cell, "TRUE far-lane", fx0 - 14, base + 4, 8, _shade(bg, 50))

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
    _adult_ref(row, 34, base, night)
    _text(row, "adult", 18, base + 1, 8, _shade(bg, 50))
    _gold_coin(row, WIDTH - PAD * 2 - 20, base - 12)
    _text(row, "coin", WIDTH - PAD * 2 - 38, base + 1, 8, _shade(bg, 50))
    spacing = (WIDTH - PAD * 2 - 220) // len(items)
    for i, (nm, v, _n) in enumerate(items):
        cx = 90 + i * spacing
        draw_greenery(row, cx, base, v, night, 0.5 + i * 0.4)
        _text(row, nm.split(" ")[0], cx - 8, base + 1, 8,
              (70, 58, 46) if night <= 0.5 else (150, 160, 185))
    sheet.blit(row, (PAD, y))
    pygame.draw.rect(sheet, (70, 74, 90), (PAD, y, WIDTH - PAD * 2, band_h), 1)
    return y + band_h + 8


def _measure_night_cap():
    """Render every NEW design onto a night strip exactly as the composite does,
    then scan the RENDERED pixels for the hottest greenery luma — the honest cap
    audit the footer prints. Accent dots (blossom/fruit) are included."""
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
    _text(sheet, "SKYBIT PROMENADE — GREENERY POOL EXPANSION (round 5): batch 1 of 4 — FIVE NEW flowering/seasonal species (pool indices 10-14); the shipped 10 UNCHANGED",
          PAD, y, 17, (250, 246, 236), bold=True)
    y += 22
    _text(sheet, "ROUND-5 REVISION on art-director ITERATE: P13 PLUM now BLOSSOM-FIRST (doubled 2x2 clusters at tips/joints + lightened/thinned zig-zag wood) · P15 NARCISSUS 4 readable white+gold cups + brighter dish rim "
                 "· P14 MAPLE maroon underside notch + amber rim-lit top (clustered masses, not a disc) · P12 CHRYSANTHEMUM brighter top crown (many-studded) · P11 PEONY trimmed one leaf row (heads stay focal). "
                 "Same far-lane pipeline, palette banks + night-cap contract (foliage/vessels <=150 via _retint; every accent <=132 at night via _accent — nothing out-pops the ~230 coin).",
          PAD, y, 9, (188, 186, 200))
    y += title_h - 22

    y = _true_band(sheet, y, "A1.  NEW SPECIES — true far-lane size, adult + coin yardstick (each must read as ITS plant by silhouette)  [DAY]",
                   POTS, 0.0)
    y = _true_band(sheet, y, "A2.  NEW SPECIES — [NIGHT]  (cooled <=150; blossom/seasonal accents held under the coin)",
                   POTS, 0.95)

    _text(sheet, "B.  PER-DESIGN — TRUE far-lane (2 t-phases) + adult ref + in-cell coin · 4x WORKING zoom (nearest) · vessel/species/attrs + palette-roles note  (DAY then NIGHT)",
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

    _text(sheet, "C.  ON-STREET COMPOSITE — the 5 NEW species at true size INTERLEAVED with shipped round_3 siblings (refs) + human cast + a stall, with the coin reference  (DAY then NIGHT)",
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
        # interleave the 5 NEW species with shipped siblings so the new family
        # reads beside round_3 (ref = a shipped design; NEW = a P11..P15 row).
        draw_greenery(strip, 40, base, POOL[0][1], night, 0.4)     # P11 peony
        _shipped_ref(strip, 90, base, night, 0, 0.4)               # ref G1 shrub
        _adult_ref(strip, 134, base, night)
        draw_greenery(strip, 178, base, POOL[1][1], night, 0.6)    # P12 chrysanthemum
        _shipped_ref(strip, 222, base, night, 1, 0.5)              # ref G2 conifer
        _stall_ref(strip, 280, base, night)
        _adult_ref(strip, 334, base, night)
        draw_greenery(strip, 378, base, POOL[2][1], night, 0.9)    # P13 plum
        _shipped_ref(strip, 422, base, night, 6, 1.1)              # ref G7 bamboo
        draw_greenery(strip, 466, base, POOL[3][1], night, 0.7)    # P14 maple
        _adult_ref(strip, 512, base, night)
        _shipped_ref(strip, 556, base, night, 8, 0.8)              # ref G9 kumquat
        draw_greenery(strip, 600, base, POOL[4][1], night, 1.0)    # P15 narcissus
        _shipped_ref(strip, 648, base, night, 4, 0.9)              # ref G5 flowering plum
        _stall_ref(strip, 712, base, night)
        _adult_ref(strip, 770, base, night)
        _shipped_ref(strip, 820, base, night, 9, 0.7)              # ref G10 wish-tree
        _gold_coin(strip, sw - 18, 20)
        _text(strip, "coin ref", sw - 46, 32, 8, _shade(bg, 60))
        _text(strip, "NIGHT" if is_night else "DAY", 4, 2, 9,
              (170, 190, 225) if is_night else (60, 50, 40), bold=True)
        _text(strip, "(P-prefixed = NEW; others = shipped round_3 refs)", 80, 2, 8,
              (170, 190, 225) if is_night else (60, 50, 40))
        sheet.blit(strip, (PAD, y))
        pygame.draw.rect(sheet, (70, 74, 90), (PAD, y, WIDTH - PAD * 2, strip_h), 1)
        y += strip_h + 6

    hottest, over = _measure_night_cap()
    coin_l = _luma((255, 232, 150))
    msg = (f"NIGHT-STRIP CAP (measured on RENDERED pixels across t-phases, incl. blossom/seasonal accents, NEW species only): "
           f"hottest GREENERY px luma = {hottest:.0f}  ·  px over {NIGHT_GLOW_CAP} = {over}  "
           f"·  gold-coin core luma = {coin_l:.0f} (sole brightest). "
           f"{'PASS — all greenery px <= cap.' if over == 0 else 'FAIL — '+str(over)+' px breach the cap.'}")
    _text(sheet, msg, PAD, total_h - 16, 9,
          (170, 200, 180) if over == 0 else (220, 140, 130))

    out = "/home/user/skybit/docs/sidewalk_overhaul/greenery/round_5.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("saved", out, sheet.get_size())
    print(f"night-strip cap: hottest greenery luma={hottest:.1f}  over-cap px={over}  coin={coin_l:.1f}")


if __name__ == "__main__":
    render()
