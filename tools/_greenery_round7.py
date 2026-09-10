"""Promenade PLANTS & GREENERY — round 7 candidate-sheet generator.

GREENERY POOL EXPANSION, batch 2 of 4 — FIVE genuinely NEW species on a
STRUCTURAL / FOLIAGE / FORM theme (a deliberate contrast to batch 1's flowers).
Batch 1 (peony/chrysanthemum/plum/maple/narcissus, pool indices 10-14) is
integrated + SHIP-READY (docs/sidewalk_overhaul/greenery/round_5.png); the
shipped pool is now 15 designs. This batch GROWS it to 20 with five more,
authored to the EXACT same instructions as the existing 15 — the SAME crisp
native far-lane pixel pipeline (pure pygame.draw.* on an SRCALPHA surface, NO
numpy/gfxdraw/PIL/smoothscale), the SAME palette banks, the SAME night-cap
contract (foliage + vessels cool toward (54,64,96) <=150 via _retint; every
bloom/bright accent held under the hard 132 night ceiling via _accent so nothing
out-pops the ~230 gold coin). The existing 15 are UNCHANGED; these become pool
indices 15-19.

ROUND 7 REVISION (art-director ITERATE on round 6) — batch frozen to two foci:
  P16 LOTUS  — the PADS are now the hero: 3 readable FLAT FLOATING DISCS as the
               dominant horizontal mass (each a flat ellipse with a 1px DARKER
               waterline RIM + a LIGHTER top face + a single radial vein notch,
               so they read as floating discs, not a raft/ground patch). The pink
               is DEMOTED to ONE open cup + ONE small bud as a low accent above
               the padded base (the second tall stem dropped, the remaining stem
               shortened) so it no longer collides with the narcissus's "flowering
               stems" read. The basin's cool-blue WATER inset is pushed wider +
               cooler so the pads visibly sit ON water — the cue that separates
               this from every other vessel and from the narcissus.
  P17 FERN   — re-silhouetted to a clear SHUTTLECOCK FAN: 6 distinct arching
               fronds spreading SYMMETRICALLY up-and-out from the base (a curved-
               rachis FOUNTAIN, no one-sided lean — the round-6 asymmetry read as
               "wilting"). Green value raised ~12%; 3 front fronds carry a pinnae-
               NOTCH rhythm so it reads LACY, not solid fingers. Soft/cool
               COUNTERPART to the cycad (fern = CURVED lines arcing from a base;
               cycad = STRAIGHT lines radiating from a point).
  P18 CYCAD  — the 2-3 OUTERMOST spear-fronds now taper to single-pixel points so
               the hard radial STAR reads crisper + pulls further from the fern.
               Radial density + scaly trunk-knob otherwise unchanged.
  P19 BANANA — FROZEN (ship-ready) carried forward unchanged.
  P20 ROCK   — FROZEN (ship-ready) carried forward unchanged.

This generator IMPORTS the shipped helpers from game.greenery_cast (the
production _retint / _accent / _hi / _mix / _shade / _luma / _draw_vessel /
_foliage / _leaf_tuft / _dome / _night_lift / draw_greenery + VESSEL_H /
NIGHT_GLOW_CAP) so the explorations are drawn by the real code path / night-cap
contract, then patches the 5 new _sp_* drawers + a new 'basin' water-vessel and a
new 'tray' vessel into the SAME dispatch the production draw_greenery reads.
Nothing here mutates production game files — the orchestrator renders + commits.

Sheet layout MIRRORS round 5/6: true far-lane DAY + NIGHT bands with an adult +
gold-coin yardstick, per-design DAY/NIGHT cells (true far size + 4x nearest zoom
+ vessel/species/attrs note), an on-street composite interleaving the 5 NEW with
shipped siblings (incl. the narcissus beside the lotus) + human cast + a stall +
the coin, and the _measure_night_cap() audit footer (PASS only when hottest
greenery <=150 and the coin ~230 stays sole-brightest).
"""
from __future__ import annotations

import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((1, 1))

# Import the SHIPPED production helpers so the new species are drawn by the exact
# same code path / night-cap contract as the existing 15 — no re-implementation.
from game import greenery_cast as gc  # noqa: E402
from game.greenery_cast import (  # noqa: E402
    _retint, _accent, _hi, _mix, _shade, _luma, _dome, _foliage, _leaf_tuft,
    _draw_vessel, _night_lift, draw_greenery, VESSEL_H, NIGHT_GLOW_CAP,
)
from game import foreground_variants as fv  # noqa: E402


# ════════════════════════════════════════════════════════════════════════════
# FIVE NEW SPECIES drawers — same signature as the shipped _sp_* (surf, cx,
# rim_y, v, night, t). Vessel is drawn by the shared _draw_vessel; these draw the
# foliage/blooms above the returned rim. Foliage routes through _foliage/_retint;
# every bloom/bright accent routes through _accent (hard 132 night ceiling). All
# geometry is integer far-lane scale, pure pygame.draw.*.
# ════════════════════════════════════════════════════════════════════════════

def _sp_lotus(surf, cx, rim_y, v, night, t):
    """LOTUS (lianhua) — the FLOATING PADS are the hero. A cluster of three flat
    round lily-pad DISCS sitting AT water level on the basin's glaze (the dominant
    HORIZONTAL mass), each a flat ellipse built as: a 1px DARKER waterline RIM,
    a LIGHTER top face, and a single radial VEIN-NOTCH slit cut from centre to the
    edge — so each disc reads as a top-lit pad floating on water, not a raft or a
    ground patch. The pink is a SMALL accent: ONE open petal-cup + ONE tight bud on
    a single short stem rising just clear of the pads — demoted so the bloom no
    longer dominates the way two tall stems did, and so the design no longer
    collides with the narcissus's "flowering stems" read. The basin's cool-blue
    water cue under the pads is what separates it from every other vessel."""
    P, A = v.palette, v.attrs
    dark, mid, top = _foliage(P, night)
    base = rim_y
    ripple = math.sin(t * 1.1) * 0.5
    # THREE big flat floating discs — the dominant mass. Each: dark waterline rim
    # ellipse, a brighter top-face ellipse inset 1px, then a single radial vein
    # notch (a thin dark slit centre->rim) so the round pad reads as a leaf disc.
    # Ordered back-to-front (small rear pad, then the two big front pads) so the
    # front discs overlap + sit proud, reading as floating plates on the water.
    pads = (
        (1, -2, 5, 2, +1),     # small rear pad (sits a touch back/up on the water)
        (-7, 0, 9, 3, -1),     # big left front pad, vein notch points left
        (6, 1, 9, 3, +1),      # big right front pad, vein notch points right
    )
    for dx, dy, rw, rh, vdir in pads:
        px = cx + dx + int(ripple * (dy < 0))
        py = base + dy
        # 1px darker WATERLINE RIM — the disc edge meeting the water
        pygame.draw.ellipse(surf, _shade(dark, -14), (px - rw, py - rh, rw * 2, rh * 2))
        # the LIGHTER top face inset inside the rim (top-lit upper plane)
        pygame.draw.ellipse(surf, mid, (px - rw + 1, py - rh + 1, rw * 2 - 2, rh * 2 - 1))
        pygame.draw.ellipse(surf, top, (px - rw + 2, py - rh + 1, rw * 2 - 4, max(1, rh)))
        # the signature single radial VEIN NOTCH — a thin dark slit centre -> rim
        pygame.draw.line(surf, _shade(dark, -10), (px, py), (px + vdir * (rw - 1), py), 1)
    # ONE short stem lifting a small open bloom just clear of the pads, + one tiny
    # bud beside it — the pink as a low ACCENT, not the dominant vertical mass.
    stem = _retint(P.get("stem", (96, 138, 84)), night)
    bloom = P.get("accent", (228, 150, 178))
    dc = A.get("day_chroma", 176)
    pet_dk = _accent(_shade(bloom, -40), night, day_ceil=dc)
    pet = _accent(bloom, night, day_ceil=dc)
    pet_lt = _accent(_shade(bloom, 26), night, day_ceil=dc)
    heart = _accent(P.get("accent2", (232, 206, 120)), night, day_ceil=dc)  # seed-cup gold
    # OPEN bloom on ONE short stem — sits just above the pad mass (small accent)
    obx = cx - 3
    oby = base - 9 + int(ripple)
    pygame.draw.line(surf, _shade(stem, -16), (obx, base - 2), (obx, oby + 2), 2)
    pygame.draw.line(surf, _shade(stem, 18), (obx, base - 2), (obx, oby + 2), 1)
    # a compact tulip-cup of pink petals: dark seat, three short petal lobes, lit edge
    pygame.draw.polygon(surf, pet_dk, [
        (obx - 3, oby + 2), (obx, oby - 3), (obx + 3, oby + 2), (obx, oby + 1)])
    for sx, hgt in ((-3, 3), (0, 5), (3, 3)):
        tipx = obx + sx
        pygame.draw.line(surf, pet, (obx, oby + 1), (tipx, oby - hgt), 2)
        pygame.draw.line(surf, pet_lt, (obx, oby + 1), (tipx, oby - hgt + 1), 1)
    pygame.draw.circle(surf, heart, (obx, oby - 1), 1)        # gold seed-cup core
    # tight pink BUD on a very short stub beside the open cup (the second accent)
    bbx = cx + 5
    bby = base - 7 - int(ripple)
    pygame.draw.line(surf, _shade(stem, -16), (bbx, base - 2), (bbx, bby + 1), 2)
    pygame.draw.line(surf, _shade(stem, 18), (bbx, base - 2), (bbx, bby + 1), 1)
    pygame.draw.polygon(surf, pet_dk, [(bbx - 2, bby + 2), (bbx, bby - 3), (bbx + 2, bby + 2)])
    pygame.draw.polygon(surf, pet, [(bbx - 1, bby + 1), (bbx, bby - 2), (bbx + 1, bby + 1)])
    pygame.draw.circle(surf, pet_lt, (bbx, bby - 1), 0)


def _sp_fern(surf, cx, rim_y, v, night, t):
    """FERN (Boston / sword fern) — a clear SYMMETRIC SHUTTLECOCK fountain: six
    arching fronds spreading evenly up-and-out from a central crown in mirrored
    pairs, so the silhouette reads as a balanced fountain (NOT the round-6 one-
    sided lean, which read as wilting). Each frond is a feathery arched blade: a
    curved rachis (a poly-line bowing outward then dropping at the tip) hung with
    short pinnae notches down both sides, so the read is LACY + ARCHED — soft, no
    flowers, no dome. Inner pair stands more upright, outer pair arches lower + the
    tips droop (the fountain rim). Cool deep green raised ~12% in value from round
    6; the 3 front fronds carry the pinnae rhythm so the lace reads at far size.
    Distinct from the cycad (this ARCHES + is feathery) and the bamboo (this is a
    tight ground rosette, not tall canes). Soft/cool counterpart to the cycad."""
    P, A = v.palette, v.attrs
    dark, mid, top = _foliage(P, night)
    base = rim_y
    crown_x = cx
    crown_y = base - 1
    sway = math.sin(t * 1.5) * 0.10
    # SYMMETRIC frond set, mirrored about the vertical: (launch angle, length,
    # arch amount, droop, notched?). Each off-vertical angle has a mirror partner
    # at (pi - angle) so the fountain spreads evenly both ways. Front three (the
    # central spire + the inner pair) carry the pinnae notch rhythm so the lace
    # reads; the low outer pair stays a clean arched blade for silhouette clarity.
    fronds = (
        (1.5708, 18, 0.25, 0, True),                # central spire (front, notched)
        (1.86, 17, 0.42, 0, True), (1.28, 17, 0.42, 0, True),   # inner pair (notched)
        (2.18, 17, 0.66, 1, False), (0.96, 17, 0.66, 1, False),  # mid pair (arch)
        (2.50, 16, 0.92, 1, False), (0.64, 16, 0.92, 1, False),  # low outer pair (big arch + droop)
    )
    for ang0, ln, arch, droop, notched in fronds:
        ang0 += sway * (1 if ang0 < 1.5708 else -1)
        # build the curved rachis as a poly-line: angle eases downward along the
        # frond (arch), and the tip dips a little extra for the droopers.
        pts = []
        steps = 6
        x, y = float(crown_x), float(crown_y)
        ang = ang0
        seg = ln / steps
        for s in range(steps + 1):
            pts.append((int(round(x)), int(round(y))))
            tt = s / steps
            a = ang - arch * tt - (droop * 0.7 * tt * tt)
            x += math.cos(a) * seg
            y -= math.sin(a) * seg
        pygame.draw.lines(surf, dark, False, pts, 2)
        pygame.draw.lines(surf, mid, False, pts, 1)
        # pinnae notches: short barbs alternating down both sides of the rachis so
        # the front fronds read LACY rather than as solid fingers.
        if notched:
            for s in range(1, steps):
                (x0, y0) = pts[s]
                (x1, y1) = pts[s + 1]
                dxs, dys = x1 - x0, y1 - y0
                blen = max(1, 3 - s // 2)         # barbs taper toward the tip
                nx, ny = -dys, dxs
                nl = math.hypot(nx, ny) or 1.0
                nx, ny = nx / nl, ny / nl
                bx = x0 + int(round(nx * blen))
                by = y0 + int(round(ny * blen))
                pygame.draw.line(surf, dark, (x0, y0), (bx, by), 1)
                pygame.draw.line(surf, dark, (x0, y0),
                                 (x0 - int(round(nx * blen)), y0 - int(round(ny * blen))), 1)
        # pale uncurling tip (the new croziers catching light)
        pygame.draw.circle(surf, top, pts[-1], 0)
    # a small dark crown knot at the rosette base
    pygame.draw.circle(surf, dark, (crown_x, crown_y), 2)
    pygame.draw.circle(surf, mid, (crown_x, crown_y - 1), 1)


def _sp_cycad(surf, cx, rim_y, v, night, t):
    """CYCAD / sago palm (Cycas revoluta) — a stiff SYMMETRIC crown of rigid,
    straight spear-fronds radiating in a flat star from a fat scaly trunk-knob.
    Architectural + prehistoric: each frond is a STRAIGHT rachis (no arch) lined
    with stiff comb-teeth (pinnae) and a spine tip, so the read is a hard radial
    STARBURST — the opposite of the fern's soft droop and unlike any dome. The 2-3
    OUTERMOST spears taper to single-pixel points (drawn 1px past the comb-teeth as
    a fine spine) so the star reads crisp + pulls further from the revised fern.
    The fat barrel trunk-knob at the base is cross-hatched with leaf-scar scales.
    Deep glossy green; lit comb-edges catch a cool highlight up top. Sits in a
    glazed urn so the heavy crown reads as borne on a solid vessel."""
    P, A = v.palette, v.attrs
    dark, mid, top = _foliage(P, night)
    base = rim_y
    # fat scaly trunk-knob — a squat barrel cross-hatched with diamond leaf-scars
    knob = _retint(P.get("trunk", (104, 84, 56)), night)
    knob_dk = _shade(knob, -26)
    knob_lt = _hi(knob, 18, night)
    ky = base - 4
    pygame.draw.ellipse(surf, knob_dk, (cx - 6, ky - 1, 12, 9))
    pygame.draw.ellipse(surf, knob, (cx - 5, ky, 10, 7))
    pygame.draw.arc(surf, knob_lt, (cx - 5, ky, 10, 7), math.radians(40), math.radians(150), 1)
    for sx in (-3, 0, 3):                     # diamond leaf-scar scales
        pygame.draw.line(surf, knob_dk, (cx + sx, ky + 1), (cx + sx, ky + 5), 1)
    for sy in (ky + 2, ky + 4):
        pygame.draw.line(surf, knob_dk, (cx - 4, sy), (cx + 4, sy), 1)
    crown_x = cx
    crown_y = ky - 1
    breathe = math.sin(t * 1.2) * 0.05
    # rigid spear-fronds radiating in a near-flat fan (a low symmetric star). Each
    # is a STRAIGHT line with comb-teeth; the topmost catch a lit edge. The two
    # outermost spears each side end in a fine single-pixel spine point.
    n = 11
    a_lo, a_hi = math.radians(8), math.radians(172)
    for i in range(n):
        frac = i / (n - 1)
        ang = a_lo + (a_hi - a_lo) * frac + breathe * math.cos(frac * math.pi)
        ln = 17 if (0.30 < frac < 0.70) else 14  # the central spears longest
        ex = crown_x + int(round(math.cos(ang) * ln))
        ey = crown_y - int(round(math.sin(ang) * ln))
        lit = 0.30 < frac < 0.70
        spine = top if lit else mid
        # the 2 outermost spears each side: a crisp single-pixel needle tip
        outer = (i <= 1) or (i >= n - 2)
        pygame.draw.line(surf, dark, (crown_x, crown_y), (ex, ey), 2)
        pygame.draw.line(surf, spine, (crown_x, crown_y), (ex, ey), 1)
        # stiff comb-teeth (pinnae) along the spear — short perpendicular ticks
        dxs, dys = ex - crown_x, ey - crown_y
        nl = math.hypot(dxs, dys) or 1.0
        ux, uy = dxs / nl, dys / nl
        px, py = -uy, ux
        for k in range(3, ln - 1, 3):
            bx = crown_x + ux * k
            by = crown_y + uy * k
            tlen = 2
            pygame.draw.line(surf, dark,
                             (int(round(bx + px * tlen)), int(round(by + py * tlen))),
                             (int(round(bx - px * tlen)), int(round(by - py * tlen))), 1)
        if outer:
            # a 1px sharpened spine point extended just past the last comb-tooth,
            # so the outermost spears read as crisp needles (hard radial star).
            tipx = crown_x + int(round(ux * (ln + 1)))
            tipy = crown_y + int(round(uy * (ln + 1)))
            pygame.draw.line(surf, dark, (ex, ey), (tipx, tipy), 1)
            pygame.draw.circle(surf, dark, (tipx, tipy), 0)
        else:
            pygame.draw.circle(surf, dark, (ex, ey), 0)  # spine-tipped leaflet
    # a fresh lit flush at the crown centre (new spears unfurling)
    pygame.draw.circle(surf, top, (crown_x, crown_y - 1), 1)


def _sp_banana(surf, cx, rim_y, v, night, t):
    """BANANA / broadleaf (Musa) — FROZEN ship-ready (round 6, art-director). 2-3
    HUGE paddle leaves: big flat blades with a strong central midrib + a torn /
    notched edge, the biggest leaf-mass in the family. Tropical. Each leaf is a
    long lozenge blade (two laminas meeting at a bold midrib), the windward edge
    cut with the species' characteristic tear-notches, splaying from a short trunk.
    One huge leaf leans each way + one upright furled spike (the unfurling new
    leaf) so the read is oversized paddles, not a bush of small leaves. Deep
    tropical green, lit upper lamina; the torn edges + the heavy midrib are the
    signature, distinct from the cycad's spiky star + the fern's lace."""
    P, A = v.palette, v.attrs
    dark, mid, top = _foliage(P, night)
    base = rim_y
    rib = _retint(P.get("stem", (150, 176, 96)), night)
    sway = math.sin(t * 1.0) * 0.08
    # short stout pseudostem
    pygame.draw.line(surf, _shade(rib, -22), (cx + 1, base + 1), (cx + 1, base - 4), 3)
    pygame.draw.line(surf, rib, (cx, base + 1), (cx, base - 4), 2)
    cy = base - 4

    def _paddle(ang, ln, half, side, lit):
        """One big paddle: a blade lozenge about a midrib, with torn edge notches.
        ang = midrib launch angle (rad), ln = blade length, half = max half-width,
        side = which lamina catches light, lit True = sunlit upper leaf."""
        ang += sway
        ux, uy = math.cos(ang), -math.sin(ang)         # along midrib
        px, py = -uy, ux                                # across blade
        tip = (cx + ux * ln, cy + uy * ln)
        # blade outline: base -> one edge (widest at ~0.45) -> tip -> other edge.
        edge_a, edge_b = [], []
        steps = 7
        for s in range(steps + 1):
            tt = s / steps
            # lozenge width profile: narrow base, fat belly, taper to a point
            w = half * math.sin(min(1.0, tt * 1.15) * math.pi) ** 0.7
            bx = cx + ux * (ln * tt)
            by = cy + uy * (ln * tt)
            edge_a.append((bx + px * w, by + py * w))
            edge_b.append((bx - px * w, by - py * w))
        poly = [(int(round(x)), int(round(y))) for x, y in edge_a] + \
               [(int(round(x)), int(round(y))) for x, y in reversed(edge_b)]
        pygame.draw.polygon(surf, dark, poly)
        # inner lamina body (one value up) inset from the dark rim
        inner = []
        for s in range(steps + 1):
            tt = s / steps
            w = max(0.0, half * math.sin(min(1.0, tt * 1.15) * math.pi) ** 0.7 - 1.4)
            bx = cx + ux * (ln * tt)
            by = cy + uy * (ln * tt)
            inner.append((bx + px * w, by + py * w))
        for s in range(steps + 1):
            tt = (steps - s) / steps
            w = max(0.0, half * math.sin(min(1.0, tt * 1.15) * math.pi) ** 0.7 - 1.4)
            bx = cx + ux * (ln * tt)
            by = cy + uy * (ln * tt)
            inner.append((bx - px * w, by - py * w))
        inner = [(int(round(x)), int(round(y))) for x, y in inner]
        if len(inner) >= 3:
            pygame.draw.polygon(surf, mid, inner)
        # the bold central MIDRIB — a thick line base to tip
        pygame.draw.line(surf, _shade(rib, -10), (cx, cy),
                         (int(round(tip[0])), int(round(tip[1]))), 2)
        pygame.draw.line(surf, rib, (cx, cy),
                         (int(round(tip[0])), int(round(tip[1]))), 1)
        # lit upper lamina edge so the paddle reads as a flat catching plane
        if lit:
            le = [edge_a[s] if side > 0 else edge_b[s] for s in range(2, steps)]
            le = [(int(round(x)), int(round(y))) for x, y in le]
            if len(le) >= 2:
                pygame.draw.lines(surf, top, False, le, 1)
        # the signature TORN / NOTCHED windward edge — a few wedge bites cut in
        for s in (2, 4, 6):
            tt = s / steps
            w = half * math.sin(min(1.0, tt * 1.15) * math.pi) ** 0.7
            bx = cx + ux * (ln * tt)
            by = cy + uy * (ln * tt)
            ox, oy = (px, py) if side > 0 else (-px, -py)
            x_e = bx + ox * w
            y_e = by + oy * w
            x_i = bx + ox * (w * 0.45)
            y_i = by + oy * (w * 0.45)
            pygame.draw.line(surf, dark,
                             (int(round(x_e)), int(round(y_e))),
                             (int(round(x_i)), int(round(y_i))), 1)

    # back-to-front: the two big arching paddles, then the upright furled spike
    _paddle(2.50, 17, 6, +1, True)     # leans left, sunlit upper face
    _paddle(0.64, 17, 6, -1, True)     # leans right
    # central furled NEW leaf — a tight upright spike (the unfurling spear)
    sp_ang = 1.5708 + sway * 0.5
    sx2 = cx + int(round(math.cos(sp_ang) * 18))
    sy2 = cy - int(round(math.sin(sp_ang) * 18))
    pygame.draw.line(surf, dark, (cx, cy), (sx2, sy2), 3)
    pygame.draw.line(surf, mid, (cx, cy), (sx2, sy2), 1)
    pygame.draw.circle(surf, top, (sx2, sy2), 1)


def _sp_rock(surf, cx, rim_y, v, night, t):
    """SCHOLAR'S ROCK (gongshi / Taihu stone) — FROZEN ship-ready (round 6, art-
    director). A tall, asymmetric, pierced grey limestone monolith standing in a
    low tray, with a small moss/fern tuft at its base. The literati-garden OBJECT:
    the ROCK is the silhouette, NOT a plant. The stone is a craggy vertical mass
    (an irregular fang leaning slightly, with a knob shoulder), modelled in three
    cool greys (shadow / body / lit ridge), and PIERCED with two clean through-
    holes (the signature swiss-cheese dissolution pockets of Lake Tai limestone)
    that show the background through the rock. A little green moss skirt + a couple
    of tiny fern fronds at the foot ground it as a planting. Distinct from
    everything: a hard inorganic grey vertical, the only non-plant-dominant
    design in the family."""
    P, A = v.palette, v.attrs
    base = rim_y
    # cool limestone greys; lifted a touch at night so a grey rock doesn't merge
    # into the dark ground band (its body is structural, not an accent).
    stone = _night_lift(_retint(P.get("rock", (150, 152, 158)), night), night, 0.18)
    stone_dk = _night_lift(_retint(P.get("rock_dk", (96, 100, 110)), night), night, 0.12)
    stone_lt = _hi(stone, 22, night)
    # the craggy monolith outline — a tall irregular fang, wider low + leaning
    # with a knob shoulder near the top (asymmetric, Taihu silhouette)
    body = [
        (cx - 6, base),            # foot left
        (cx - 7, base - 7),
        (cx - 4, base - 13),
        (cx - 6, base - 19),       # waisted neck
        (cx - 3, base - 25),
        (cx - 4, base - 29),       # peak left
        (cx + 1, base - 31),       # summit
        (cx + 4, base - 27),       # right shoulder knob
        (cx + 2, base - 22),
        (cx + 6, base - 17),       # bulge right
        (cx + 4, base - 9),
        (cx + 7, base),            # foot right
    ]
    pygame.draw.polygon(surf, stone_dk, body)
    # an inset body fill (one value up) so the rim reads as shadowed edge
    inner = [(x - (1 if x > cx else -1), y + (1 if y < base else 0)) for x, y in body]
    pygame.draw.polygon(surf, stone, inner)
    # lit ridge up the windward (left) face + the summit — cool highlight
    ridge = [(cx - 5, base - 8), (cx - 3, base - 14), (cx - 4, base - 20),
             (cx - 2, base - 26), (cx + 1, base - 30)]
    pygame.draw.lines(surf, stone_lt, False, ridge, 1)
    # carved vertical erosion grooves (the fluted Taihu surface) — top y above
    # bottom y (gy0 is the lower end nearer the foot, gy1 the upper end)
    for gx, gy0, gy1 in ((-2, base - 6, base - 24), (2, base - 4, base - 20),
                         (4, base - 12, base - 25)):
        pygame.draw.line(surf, stone_dk, (cx + gx, gy0), (cx + gx, gy1), 1)
    # ── the signature PIERCED through-holes: clean holes that show the BACKGROUND
    # through the rock (the swiss-cheese dissolution pockets of Lake Tai stone).
    # On an SRCALPHA surface (the zoom + cap-audit strip) we clear to transparent
    # so the true background reads through; on an opaque surface (cells / bands /
    # composite) there is no captured background, so the hole is filled with the
    # surface bg colour passed in via attrs["hole_bg"] (the cell/strip bg).
    hole_bg = A.get("hole_bg")
    srcalpha = bool(surf.get_flags() & pygame.SRCALPHA)
    for hx, hy, hr in ((-2, base - 16, 2), (2, base - 23, 1)):
        cxp, cyp = cx + hx, hy
        # a ring of shadowed stone framing the pierce, then the hollow core
        pygame.draw.circle(surf, stone_dk, (cxp, cyp), hr + 1)
        if srcalpha:
            for ddx in range(-hr, hr + 1):
                for ddy in range(-hr, hr + 1):
                    if ddx * ddx + ddy * ddy <= hr * hr:
                        surf.set_at((cxp + ddx, cyp + ddy), (0, 0, 0, 0))
        elif hole_bg is not None:
            pygame.draw.circle(surf, hole_bg, (cxp, cyp), hr)
        else:
            # no bg known: a very dark cavity so the pierce still reads as a hole
            pygame.draw.circle(surf, _shade(stone_dk, -34), (cxp, cyp), hr)
        # a lit lower lip on each pocket so the hole reads as a hollow, not a dot
        pygame.draw.arc(surf, stone_lt, (cxp - hr - 1, cyp - hr - 1, (hr + 1) * 2, (hr + 1) * 2),
                        math.radians(200), math.radians(340), 1)
    # a small green MOSS skirt + a couple of tiny fern fronds at the foot so the
    # rock reads as a literati PLANTING, not just a stone (foliage via _foliage).
    dark, mid, top = _foliage(P, night)
    pygame.draw.ellipse(surf, dark, (cx - 7, base - 2, 16, 4))
    pygame.draw.ellipse(surf, mid, (cx - 6, base - 2, 14, 3))
    sway = math.sin(t * 1.6) * 0.12
    for ox, ang, ln in ((-5, 2.1, 6), (-3, 1.9, 5), (6, 1.1, 6), (8, 1.3, 5)):
        a = ang + sway * (1 if ang < 1.5708 else -1)
        ex = cx + ox + int(round(math.cos(a) * ln))
        ey = base - 1 - int(round(math.sin(a) * ln))
        mx = cx + ox + int(round(math.cos(a) * ln * 0.5))
        my = base - 1 - int(round(math.sin(a) * ln * 0.5))
        pygame.draw.lines(surf, mid, False, [(cx + ox, base - 1), (mx, my), (ex, ey)], 1)
        pygame.draw.circle(surf, top, (ex, ey), 0)


# ── two NEW vessels — a wide shallow water BASIN (lotus) and a low rectangular
# literati TRAY (scholar's rock). Each returns the rim y the design plants into. ─

def _draw_basin(surf, cx, base_y, v, night):
    """A wide shallow WATER basin for the lotus — a low stone/porcelain trough
    whose mouth is filled with a cool water glaze the pads float ON. The flattest,
    widest vessel; the water surface IS the rim the pads sit on. The rim band is
    lifted one value step so the basin survives the NIGHT ground band, and the
    water glaze is pushed WIDER + cooler (held under the pink bloom) so the cool-
    blue water cue clearly separates the lotus from every other vessel."""
    P, A = v.palette, v.attrs
    vlift = A.get("vlift", 0.0)
    pf = lambda c: _night_lift(_retint(c, night), night, vlift)
    body = pf(P.get("vessel", (176, 172, 162)))
    dk = pf(P.get("vessel_dk", (118, 116, 110)))
    lt = _hi(body, 20, night)
    g = int(base_y)
    h = 7
    top_w, bot_w = 28, 22
    ty = g - h
    # the shallow flared basin body
    pygame.draw.polygon(surf, dk, [
        (cx - top_w // 2, ty), (cx + top_w // 2, ty),
        (cx + bot_w // 2, g), (cx - bot_w // 2, g)])
    pygame.draw.polygon(surf, body, [
        (cx - top_w // 2 + 1, ty + 2), (cx + top_w // 2 - 1, ty + 2),
        (cx + bot_w // 2, g - 1), (cx - bot_w // 2, g - 1)])
    # a brighter lit mouth edge so the rim reads against the night ground band
    pygame.draw.line(surf, lt, (cx - top_w // 2 + 1, ty), (cx + top_w // 2 - 2, ty), 1)
    # the WATER glaze filling the mouth — a cool inset surface pushed wider + a
    # touch taller (held low/cool) so the pads visibly sit ON water; pale ripple
    # ticks so it reads as water, not a flat lid.
    water = _hi(_retint(P.get("glaze", (62, 100, 152)), night), 8, night)
    water_lt = _hi(water, 18, night)
    pygame.draw.rect(surf, water, (cx - top_w // 2 + 2, ty + 1, top_w - 4, 3))
    for dxp in (-10, -3, 4, 10):
        pygame.draw.line(surf, water_lt, (cx + dxp, ty + 2), (cx + dxp + 3, ty + 2), 1)
    return ty + 1


def _draw_tray(surf, cx, base_y, v, night):
    """A low literati TRAY (a shallow rectangular display plinth) for the scholar's
    rock — a flat dark-wood / stone slab the rock stands ON. The lowest, simplest
    vessel: a thin plinth with a lit top edge + little foot-blocks, so the rock
    reads as MOUNTED on a stand, not growing from a pot. Rim returned = the plinth
    top the rock foot plants on."""
    P, A = v.palette, v.attrs
    vlift = A.get("vlift", 0.0)
    pf = lambda c: _night_lift(_retint(c, night), night, vlift)
    body = pf(P.get("vessel", (96, 78, 60)))
    dk = pf(P.get("vessel_dk", (60, 48, 38)))
    lt = _hi(body, 18, night)
    g = int(base_y)
    w = 24
    h = 5
    ty = g - h
    # two little foot-blocks under the slab (the literati stand)
    for fx in (cx - w // 2 + 2, cx + w // 2 - 4):
        pygame.draw.rect(surf, dk, (fx, g - 2, 3, 3))
    # the slab plinth
    pygame.draw.rect(surf, dk, (cx - w // 2, ty, w, h - 1))
    pygame.draw.rect(surf, body, (cx - w // 2 + 1, ty, w - 2, h - 3))
    pygame.draw.line(surf, lt, (cx - w // 2 + 1, ty), (cx + w // 2 - 2, ty), 1)
    # a thin shadow line under the slab lip
    pygame.draw.line(surf, _shade(dk, -14), (cx - w // 2, g - 3), (cx + w // 2 - 1, g - 3), 1)
    return ty


# Patch the new species INTO the production dispatch so the shipped draw_greenery
# routes them, and wrap _draw_vessel so 'basin' + 'tray' resolve. This mirrors
# exactly how the folded-in greenery_cast.py will register them.
_orig_vessel = gc._draw_vessel


def _vessel_dispatch(surf, cx, base_y, v, night, kind):
    if kind == "basin":
        return _draw_basin(surf, cx, base_y, v, night)
    if kind == "tray":
        return _draw_tray(surf, cx, base_y, v, night)
    return _orig_vessel(surf, cx, base_y, v, night, kind)


gc._draw_vessel = _vessel_dispatch

_orig_draw = gc.draw_greenery


def draw_greenery(surf, cx, base_y, v, night, t):  # noqa: F811
    A = v.attrs
    sp = A.get("species", "shrub")
    new = {
        "lotus": _sp_lotus, "fern": _sp_fern, "cycad": _sp_cycad,
        "banana": _sp_banana, "rock": _sp_rock,
    }
    if sp == "rock" and not (surf.get_flags() & pygame.SRCALPHA):
        # On an OPAQUE sheet surface the rock's through-holes can't show real
        # transparency, so sample the already-painted background just ABOVE the
        # rock (clear of any deck) and hand it in as the hole fill, so the pierces
        # read as the surrounding sky/ground colour rather than black dots. This
        # auto-adapts to every opaque context (cells / bands / composite) without
        # threading a bg param through each call site.
        sy = max(0, int(base_y) - 40)
        try:
            A = dict(A)
            A["hole_bg"] = surf.get_at((min(cx, surf.get_width() - 1), sy))[:3]
            v = fv.Variant(palette=v.palette, attrs=A)
        except Exception:
            pass
    if sp in new:
        rim_y = gc._draw_vessel(surf, cx, base_y, v, night, A.get("vessel", "terracotta"))
        new[sp](surf, cx, rim_y, v, night, t)
    else:
        _orig_draw(surf, cx, base_y, v, night, t)


# ════════════════════════════════════════════════════════════════════════════
# THE 5 NEW ROWS — foreground_variants.Variant data (pool indices 15-19).
# Reuse the shipped palette banks (_URN/_TUB/_STONE) + add structural banks.
# ════════════════════════════════════════════════════════════════════════════

_URN = dict(gc._URN)
_TUB = dict(gc._TUB)
_STONE = dict(gc._STONE)

# cool deep-green fern bank (shade-loving, blue-green) — raised ~12% in value from
# round 6 so the revised shuttlecock reads fresher / more clearly green, while the
# foliage_top still sits well under the night cap once cooled via _retint.
_FOL_FERN = dict(foliage_dark=(34, 82, 62), foliage_mid=(56, 118, 84), foliage_top=(110, 166, 124))
# glossy deep cycad green (hard, prehistoric)
_FOL_CYCAD = dict(foliage_dark=(26, 62, 44), foliage_mid=(42, 92, 60), foliage_top=(92, 146, 96))
# big tropical banana green (lush, broad)
_FOL_BANANA = dict(foliage_dark=(32, 76, 46), foliage_mid=(54, 112, 66), foliage_top=(108, 164, 96))
# lotus pad green (water-leaf) + a green stem role
_FOL_LOTUS = dict(foliage_dark=(34, 80, 56), foliage_mid=(58, 116, 78), foliage_top=(112, 162, 116))
# the rock's foot moss/fern tuft (kept modest under the grey stone)
_FOL_MOSS = dict(foliage_dark=(40, 78, 50), foliage_mid=(64, 110, 70), foliage_top=(108, 152, 100))


def _row(*banks, **attrs):
    pal = {}
    for b in banks:
        pal.update(b)
    return fv.Variant(palette=pal, attrs=dict(attrs))


POOL = [
    ("P16 water-basin LOTUS (lianhua)", _row(
        _STONE, _FOL_LOTUS, dict(glaze=(62, 100, 152), stem=(96, 138, 84),
                                 accent=(228, 150, 178), accent2=(232, 206, 120)),
        vessel="basin", species="lotus", vlift=0.10, day_chroma=176),
     "vessel:basin(NEW wide shallow WATER trough, WIDER cool inset glaze + ripple ticks, rim lifted for night) species:lotus accent:pink petal-cup + accent2:gold seed-cup | THREE flat round floating PADS are the hero (horizontal mass: 1px darker waterline rim + lighter top face + 1 radial vein notch each) with ONE small open bloom + 1 bud as a LOW accent — pad-led so it no longer collides with the narcissus 'flowering stems'"),

    ("P17 stone-trough FERN (Boston)", _row(
        _STONE, _FOL_FERN, dict(vlift=0.10),
        vessel="trough", species="fern"),
     "vessel:trough(shipped stone) species:fern | a SYMMETRIC SHUTTLECOCK fountain of 6 arching fronds spreading evenly up-and-out (mirrored pairs, no one-sided lean), green value raised ~12%, the 3 FRONT fronds carry a pinnae-NOTCH rhythm so it reads LACY not solid fingers — soft/cool ARCHED counterpart to the cycad's stiff star"),

    ("P18 glazed-urn CYCAD (sago)", _row(
        _URN, _FOL_CYCAD, dict(trunk=(106, 86, 58)),
        vessel="urn", species="cycad"),
     "vessel:urn(blue-white belly+neck) species:cycad trunk:fat scaly leaf-scar KNOB | a stiff SYMMETRIC crown of rigid straight spear-fronds radiating in a flat STAR, hard comb-teeth + the 2 OUTERMOST spears each side sharpened to single-pixel needle points so the radial star reads crisp — the hard radial opposite of the fern's soft arch"),

    ("P19 wooden-tub BANANA (Musa)", _row(
        _TUB, _FOL_BANANA, dict(stem=(150, 176, 96)),
        vessel="tub", species="banana"),
     "vessel:tub(staved barrel, iron hoops) species:banana | FROZEN ship-ready — 2 HUGE arching paddle leaves (lozenge blades, bold central MIDRIB, torn/notched windward edge, lit upper lamina) + 1 upright furled new-leaf spike — the biggest, broadest leaf-mass in the family; tropical, no flowers"),

    ("P20 literati-tray SCHOLAR'S ROCK (gongshi)", _row(
        _STONE, _FOL_MOSS, dict(rock=(150, 152, 158), rock_dk=(96, 100, 110),
                                vessel=(96, 78, 60), vessel_dk=(60, 48, 38)),
        vessel="tray", species="rock", vlift=0.0),
     "vessel:tray(NEW low dark-wood plinth + foot-blocks — rock is MOUNTED, not potted) species:rock | FROZEN ship-ready — a tall asymmetric PIERCED grey Taihu limestone fang (3 cool greys, fluted erosion grooves, 2 clean THROUGH-HOLES showing bg) with a moss skirt + tiny fern fronds at the foot — the literati OBJECT, the only non-plant silhouette"),
]

POTS = POOL


# ════════════════════════════════════════════════════════════════════════════
# SHEET RENDERER  (mirrors tools/_greenery_round6.py house style)
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
    person (lifted from the round_5 generator)."""
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
    """Draw one of the SHIPPED designs (via the production registry) as a sibling-
    look reference so the new species sit beside the shipped family. Uses the
    ORIGINAL production draw path (these indices are all existing species)."""
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

    SC_W, SC_H = 36, 48
    nat = pygame.Surface((SC_W, SC_H), pygame.SRCALPHA)
    deck_y = SC_H - 5
    nat.fill((*_mix(bg, (0, 0, 0), 0.18), 130), (0, deck_y, SC_W, SC_H - deck_y))
    draw_greenery(nat, SC_W // 2, deck_y, v, night, 0.9)
    z = 4
    zoom = pygame.transform.scale(nat, (SC_W * z, SC_H * z))
    zw, zh = zoom.get_size()
    zx, zy = w - zw - 8, 18
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
    audit the footer prints. Accent dots (blooms) are included. Fully transparent
    pixels (the rock's through-holes) are skipped — they are background, not
    greenery."""
    night = 0.95
    strip = pygame.Surface((1400, 100), pygame.SRCALPHA)
    strip.fill(BG_NIGHT)
    base = 78
    x = 50
    for _nm, v, _n in POOL:
        for tt in (0.0, 0.6, 1.3):
            draw_greenery(strip, x, base, v, night, tt)
            x += 32
        x += 16
    hottest = 0.0
    over = 0
    bg_l = _luma(BG_NIGHT)
    for px in range(strip.get_width()):
        for py in range(strip.get_height()):
            r, g, b, a = strip.get_at((px, py))
            if a < 8:
                continue                       # transparent rock-pierce = bg
            c = (r, g, b)
            l = _luma(c)
            if abs(l - bg_l) < 1.5:
                continue
            hottest = max(hottest, l)
            if l > NIGHT_GLOW_CAP:
                over += 1
    return hottest, over


def render():
    cell_w = (WIDTH - PAD * 3) // 2
    cell_h = 118

    title_h = 56
    bandA_h = 20 + 64 + 8 + 20 + 64 + 8
    rows = (len(POOL) + 1) // 2
    detail_h = 22 + 2 * (18 + rows * (cell_h + 6))
    strip_h = 108
    comp_h = 22 + 2 * (strip_h + 6)
    total_h = title_h + bandA_h + detail_h + comp_h + PAD * 6 + 26

    sheet = pygame.Surface((WIDTH, total_h))
    sheet.fill((26, 28, 38))

    y = PAD
    _text(sheet, "SKYBIT PROMENADE — GREENERY POOL EXPANSION (round 7): batch 2 of 4 — FIVE NEW STRUCTURAL / FOLIAGE species (pool indices 15-19); the shipped 15 UNCHANGED",
          PAD, y, 17, (250, 246, 236), bold=True)
    y += 22
    _text(sheet, "Round-7 revision (art-director ITERATE): P16 LOTUS rebuilt PAD-LED (3 flat floating discs w/ waterline rim + vein notch are the hero; pink demoted to 1 small cup + 1 bud; basin water pushed wider/cooler) · P17 FERN re-silhouetted to a SYMMETRIC shuttlecock fountain (6 arching fronds, +12% green, lacy front-frond notches) · "
                 "P18 CYCAD outermost spears sharpened to single-pixel needle points · P19 BANANA + P20 SCHOLAR'S ROCK FROZEN ship-ready, carried forward unchanged. "
                 "Same far-lane pipeline, palette banks + night-cap contract (foliage/vessels <=150 via _retint; every bright accent <=132 at night via _accent — nothing out-pops the ~230 coin).",
          PAD, y, 9, (188, 186, 200))
    y += title_h - 22

    y = _true_band(sheet, y, "A1.  NEW SPECIES — true far-lane size, adult + coin yardstick (each must read as ITS plant/object by silhouette)  [DAY]",
                   POTS, 0.0)
    y = _true_band(sheet, y, "A2.  NEW SPECIES — [NIGHT]  (cooled <=150; pink/bright accents held under the coin)",
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

    _text(sheet, "C.  ON-STREET COMPOSITE — the 5 NEW species at true size INTERLEAVED with shipped siblings (refs) + human cast + a stall, with the coin reference. LOTUS sits NEXT TO the narcissus (ref) to confirm the pad-led read no longer collides with 'flowering stems'.  (DAY then NIGHT)",
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
        # interleave the 5 NEW species with shipped siblings (ref = a shipped
        # design index; NEW = a P16..P20 row). The LOTUS is placed directly beside
        # the narcissus (shipped idx 14) so the revised pad-led read can be
        # compared against the "flowering stems" silhouette it must not collide
        # with. Other siblings span flowers + form so the new structural family
        # reads beside the whole shipped cast.
        draw_greenery(strip, 40, base, POOL[0][1], night, 0.4)     # P16 lotus
        _shipped_ref(strip, 90, base, night, 14, 0.4)              # ref G15 narcissus (collision check)
        _adult_ref(strip, 136, base, night)
        draw_greenery(strip, 182, base, POOL[1][1], night, 0.6)    # P17 fern
        _shipped_ref(strip, 228, base, night, 6, 0.5)              # ref G7 bamboo
        _stall_ref(strip, 288, base, night)
        _adult_ref(strip, 344, base, night)
        draw_greenery(strip, 392, base, POOL[2][1], night, 0.9)    # P18 cycad
        _shipped_ref(strip, 438, base, night, 2, 1.1)              # ref G3 topiary
        draw_greenery(strip, 486, base, POOL[3][1], night, 0.7)    # P19 banana
        _adult_ref(strip, 536, base, night)
        _shipped_ref(strip, 582, base, night, 13, 0.8)             # ref G14 maple
        draw_greenery(strip, 632, base, POOL[4][1], night, 1.0)    # P20 scholar's rock
        _shipped_ref(strip, 682, base, night, 10, 0.9)             # ref G11 peony
        _stall_ref(strip, 742, base, night)
        _adult_ref(strip, 800, base, night)
        _shipped_ref(strip, 848, base, night, 9, 0.7)              # ref G10 wish-tree
        _gold_coin(strip, sw - 18, 20)
        _text(strip, "coin ref", sw - 46, 32, 8, _shade(bg, 60))
        _text(strip, "NIGHT" if is_night else "DAY", 4, 2, 9,
              (170, 190, 225) if is_night else (60, 50, 40), bold=True)
        _text(strip, "(P-prefixed = NEW; others = shipped refs; lotus|narcissus adjacency = collision check)", 80, 2, 8,
              (170, 190, 225) if is_night else (60, 50, 40))
        sheet.blit(strip, (PAD, y))
        pygame.draw.rect(sheet, (70, 74, 90), (PAD, y, WIDTH - PAD * 2, strip_h), 1)
        y += strip_h + 6

    hottest, over = _measure_night_cap()
    coin_l = _luma((255, 232, 150))
    msg = (f"NIGHT-STRIP CAP (measured on RENDERED pixels across t-phases, incl. blooms; rock through-holes = transparent bg, skipped; NEW species only): "
           f"hottest GREENERY px luma = {hottest:.0f}  ·  px over {NIGHT_GLOW_CAP} = {over}  "
           f"·  gold-coin core luma = {coin_l:.0f} (sole brightest). "
           f"{'PASS — all greenery px <= cap.' if over == 0 else 'FAIL — '+str(over)+' px breach the cap.'}")
    _text(sheet, msg, PAD, total_h - 16, 9,
          (170, 200, 180) if over == 0 else (220, 140, 130))

    out = "/home/user/skybit/docs/sidewalk_overhaul/greenery/round_7.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("saved", out, sheet.get_size())
    print(f"night-strip cap: hottest greenery luma={hottest:.1f}  over-cap px={over}  coin={coin_l:.1f}")


if __name__ == "__main__":
    render()
