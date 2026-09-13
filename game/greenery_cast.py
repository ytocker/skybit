"""Promenade PLANTS & GREENERY — a varied potted-plant / tree pool.

Replaces the single shrub-planter / conifer-planter / wish-tree with a 30-design
pool built as VESSEL × SPECIES over one shared draw_greenery (data rows = palette
+ vessel/species/attrs flags). 19 species across 8 vessels; the original 10
(round_3) plus 20 added in four art-director SHIP-READY rounds
(docs/sidewalk_overhaul/greenery/round_3..round_10.png), sibling to the ped_cast / day_cast
/ food_stalls / animals families.

Variety lives in the OUTLINE (vessel shape + canopy shape): terracotta / glazed
urn / wooden tub / bamboo planter / stone trough × shrub, conifer-cone, clipped
topiary (1 or 3 tier), flowering dome, cascading flowering-vine, bamboo canes,
draping vine/fern, kumquat fruiting-tree, weeping wish-tree. Blossom/fruit/ribbon
accents are muted and held well under the gold coin; night-cooled toward
(54,64,96) ≤150 luma (measured hottest greenery 138.5 vs coin 229.5). Greenery is
beat- and weather-neutral (it persists across the day-arc). Pure-Pygame /
pygbag-safe.
"""
from __future__ import annotations

import math

import pygame

from game.foreground_props import _mix, _shade, _clamp
from game import foreground_variants as fv

NIGHT_GLOW_CAP = 150
VESSEL_H = 14      # height of a 1.0 terracotta pot (px) — shorter than an adult


def _luma(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def _retint(col, night):
    """Cool toward the night ground band (matches ped_cast._retint_person), with a
    stronger pull on anything still above the cap so no leaf/pot/blossom out-glows
    the coin at night."""
    if night <= 0.05:
        return col
    out = _mix(col, (54, 64, 96), min(0.55, 0.40 * night + 0.20))
    if _luma(out) > NIGHT_GLOW_CAP:
        over = (_luma(out) - NIGHT_GLOW_CAP) / max(1.0, 255 - NIGHT_GLOW_CAP)
        out = _mix(out, (66, 76, 104), min(0.78, 0.5 + over))
    return out


def _hi(c, d, night):
    out = _shade(c, d)
    if night > 0.05 and _luma(out) > NIGHT_GLOW_CAP:
        out = _mix(out, (66, 76, 104), 0.65)
    return out


def _accent(col, night, *, day_ceil=188):
    """A blossom/fruit/ribbon accent: muted, held well under the coin (hard 132
    ceiling at night, softer day ceiling) so warm pops read as seasonal colour
    without becoming the brightest thing on the street."""
    out = _retint(col, night)
    ceil = 132 if night > 0.05 else day_ceil
    if _luma(out) > ceil:
        out = _mix(out, (70, 60, 64) if night <= 0.05 else (66, 72, 96),
                   min(0.7, (_luma(out) - ceil) / 120.0 + 0.3))
    return out


def _night_lift(col, night, frac):
    """Lift a too-dark vessel toward a cool grey on NIGHT only, so a low granite
    trough doesn't merge into the dark ground band."""
    if night <= 0.05:
        return col
    return _mix(col, (104, 112, 132), frac * night)


def draw_greenery(surf, cx, base_y, v, night, t):
    A = v.attrs
    sp = A.get("species", "shrub")
    if sp == "rock" and not (surf.get_flags() & pygame.SRCALPHA):
        # The scholar's-rock through-holes can't show real transparency on an
        # opaque target, so sample the painted background just above the rock and
        # hand it in as the hole fill, so the pierces read as the surrounding
        # sky/ground rather than black dots. (On SRCALPHA targets — the near-lane
        # bake scratch — the drawer clears the holes to transparent instead.)
        sy = max(0, int(base_y) - 40)
        try:
            A = dict(A)
            A["hole_bg"] = surf.get_at((min(cx, surf.get_width() - 1), sy))[:3]
            v = fv.Variant(palette=v.palette, attrs=A)
        except Exception:
            pass
    rim_y = _draw_vessel(surf, cx, base_y, v, night, A.get("vessel", "terracotta"))
    {
        "shrub": _sp_shrub, "conifer": _sp_conifer, "topiary": _sp_topiary,
        "flowering": _sp_flowering, "bamboo": _sp_bamboo, "vine": _sp_vine,
        "flovine": _sp_flovine, "kumquat": _sp_kumquat, "wishtree": _sp_wishtree,
        "peony": _sp_peony, "chrysanthemum": _sp_chrysanthemum, "plum": _sp_plum,
        "maple": _sp_maple, "narcissus": _sp_narcissus,
        "lotus": _sp_lotus, "fern": _sp_fern, "cycad": _sp_cycad,
        "banana": _sp_banana, "rock": _sp_rock,
    }[sp](surf, cx, rim_y, v, night, t)


# ── vessels — each a distinct outline; returns the rim y the canopy plants into ─

def _draw_vessel(surf, cx, base_y, v, night, kind):
    P, A = v.palette, v.attrs
    vlift = A.get("vlift", 0.0)
    pf = lambda c: _night_lift(_retint(c, night), night, vlift)
    body = pf(P.get("vessel", (170, 104, 72)))
    dk = pf(P.get("vessel_dk", _shade(P.get("vessel", (170, 104, 72)), -34)))
    lt = _hi(body, 18, night)
    g = int(base_y)

    if kind == "terracotta":
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
        pygame.draw.line(surf, lt, (cx - top_w // 2 + 2, ty + rim_h + 1), (cx - bot_w // 2 + 1, g - 1), 1)
        return ty + 1

    if kind == "urn":
        h = VESSEL_H + 4
        ty = g - h
        belly_w = 19
        glaze = _retint(P.get("glaze", (96, 120, 170)), night)
        pygame.draw.ellipse(surf, dk, (cx - belly_w // 2, ty + 5, belly_w, h - 4))
        pygame.draw.ellipse(surf, body, (cx - belly_w // 2 + 1, ty + 6, belly_w - 2, h - 6))
        pygame.draw.arc(surf, lt, (cx - belly_w // 2 + 1, ty + 6, belly_w - 2, h - 6),
                        math.radians(40), math.radians(150), 1)
        neck_w = 9
        pygame.draw.rect(surf, body, (cx - neck_w // 2, ty + 2, neck_w, 5))
        pygame.draw.rect(surf, dk, (cx - neck_w // 2, ty + 2, neck_w, 5), 1)
        pygame.draw.ellipse(surf, dk, (cx - neck_w // 2, ty, neck_w, 4))
        pygame.draw.ellipse(surf, _shade(body, -8), (cx - neck_w // 2 + 1, ty + 1, neck_w - 2, 2))
        gby = ty + 9
        pygame.draw.line(surf, glaze, (cx - belly_w // 2 + 2, gby), (cx + belly_w // 2 - 2, gby), 1)
        for dxp in range(-belly_w // 2 + 3, belly_w // 2 - 1, 3):
            pygame.draw.circle(surf, glaze, (cx + dxp, gby + 3), 1)
        return ty + 2

    if kind == "tub":
        h = VESSEL_H + 1
        w = 20
        ty = g - h
        pygame.draw.rect(surf, dk, (cx - w // 2, ty, w, h))
        pygame.draw.rect(surf, body, (cx - w // 2 + 1, ty, w - 2, h - 1))
        for sxp in range(cx - w // 2 + 3, cx + w // 2 - 1, 4):
            pygame.draw.line(surf, _shade(body, -20), (sxp, ty + 1), (sxp, g - 2), 1)
        pygame.draw.line(surf, lt, (cx - w // 2 + 1, ty + 1), (cx + w // 2 - 2, ty + 1), 1)
        hoop = pf(P.get("vessel_dk", (90, 70, 50)))
        for hy in (ty + 2, g - 3):
            pygame.draw.rect(surf, _shade(hoop, -18), (cx - w // 2, hy, w, 2))
            pygame.draw.line(surf, _shade(hoop, 26), (cx - w // 2, hy), (cx + w // 2 - 1, hy), 1)
        return ty + 1

    if kind == "bamboo":
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
        for ny in (ty + h // 3, g - 3):
            pygame.draw.line(surf, cane_dk, (cx - w // 2, ny), (cx + w // 2 - 1, ny), 1)
        cord = _retint((150, 120, 70), night)
        pygame.draw.line(surf, cord, (cx - w // 2, ty + 2), (cx + w // 2 - 1, ty + 2), 2)
        return ty

    if kind == "trough":
        h = 9
        w = 22
        ty = g - h
        stone = pf(P.get("vessel", (150, 142, 124)))
        pygame.draw.rect(surf, _shade(stone, -22), (cx - w // 2, ty, w, h))
        pygame.draw.rect(surf, stone, (cx - w // 2 + 1, ty, w - 2, h - 2))
        pygame.draw.rect(surf, _shade(stone, 16), (cx - w // 2 + 1, ty, w - 2, 1))
        pygame.draw.rect(surf, _shade(stone, -14), (cx - w // 2 + 1, ty + 2, w - 2, 1))
        for dxp in (-6, 2, 7):
            pygame.draw.circle(surf, _shade(stone, -18), (cx + dxp, ty + 5), 1)
        return ty

    if kind == "dish":
        # the flattest vessel — a shallow flared porcelain bowl of pebbles for the
        # narcissus; rim lifted one value step so it stays present in the night band.
        h = 6
        top_w, bot_w = 24, 16
        ty = g - h
        pygame.draw.polygon(surf, dk, [
            (cx - top_w // 2, ty), (cx + top_w // 2, ty),
            (cx + bot_w // 2, g), (cx - bot_w // 2, g)])
        pygame.draw.polygon(surf, body, [
            (cx - top_w // 2 + 1, ty + 1), (cx + top_w // 2 - 1, ty + 1),
            (cx + bot_w // 2, g - 1), (cx - bot_w // 2, g - 1)])
        pygame.draw.line(surf, lt, (cx - top_w // 2 + 1, ty + 1), (cx + top_w // 2 - 2, ty + 1), 1)
        pygame.draw.line(surf, lt, (cx - top_w // 2 + 1, ty), (cx + top_w // 2 - 2, ty), 1)
        glaze = _hi(_retint(P.get("glaze", (72, 104, 168)), night), 16, night)
        pygame.draw.line(surf, glaze, (cx - top_w // 2 + 2, ty + 3), (cx + top_w // 2 - 2, ty + 3), 1)
        peb = pf((158, 160, 166))
        for dxp in (-7, -2, 3, 7, 0):
            pygame.draw.circle(surf, peb, (cx + dxp, ty + 1), 1)
        return ty

    if kind == "basin":
        # a wide shallow WATER basin — the flattest/widest vessel; the cool-blue
        # water glaze filling the mouth is the surface the lotus pads float ON.
        h = 7
        top_w, bot_w = 28, 22
        ty = g - h
        pygame.draw.polygon(surf, dk, [
            (cx - top_w // 2, ty), (cx + top_w // 2, ty),
            (cx + bot_w // 2, g), (cx - bot_w // 2, g)])
        pygame.draw.polygon(surf, body, [
            (cx - top_w // 2 + 1, ty + 2), (cx + top_w // 2 - 1, ty + 2),
            (cx + bot_w // 2, g - 1), (cx - bot_w // 2, g - 1)])
        pygame.draw.line(surf, lt, (cx - top_w // 2 + 1, ty), (cx + top_w // 2 - 2, ty), 1)
        water = _hi(_retint(P.get("glaze", (62, 100, 152)), night), 8, night)
        water_lt = _hi(water, 18, night)
        pygame.draw.rect(surf, water, (cx - top_w // 2 + 2, ty + 1, top_w - 4, 3))
        for dxp in (-10, -3, 4, 10):
            pygame.draw.line(surf, water_lt, (cx + dxp, ty + 2), (cx + dxp + 3, ty + 2), 1)
        return ty + 1

    if kind == "tray":
        # a low literati TRAY — a thin dark slab + foot-blocks the rock stands ON,
        # so the scholar's rock reads as MOUNTED, not growing from a pot.
        w = 24
        h = 5
        ty = g - h
        for fx in (cx - w // 2 + 2, cx + w // 2 - 4):
            pygame.draw.rect(surf, dk, (fx, g - 2, 3, 3))
        pygame.draw.rect(surf, dk, (cx - w // 2, ty, w, h - 1))
        pygame.draw.rect(surf, body, (cx - w // 2 + 1, ty, w - 2, h - 3))
        pygame.draw.line(surf, lt, (cx - w // 2 + 1, ty), (cx + w // 2 - 2, ty), 1)
        pygame.draw.line(surf, _shade(dk, -14), (cx - w // 2, g - 3), (cx + w // 2 - 1, g - 3), 1)
        return ty

    return g - VESSEL_H


# ── species — each a distinct canopy shape, planted on rim_y ──────────────────

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


def _leaf_tuft(surf, ox, oy, ang, length, col, *, n=4, spread=0.5):
    for i in range(n):
        a = ang + (i - (n - 1) / 2) * spread / max(1, n - 1)
        ex = ox + int(math.cos(a) * length)
        ey = oy - int(math.sin(a) * length)
        mx = ox + int(math.cos(a) * length * 0.5)
        my = oy - int(math.sin(a) * length * 0.5) - 1
        pygame.draw.lines(surf, col, False, [(ox, oy), (mx, my), (ex, ey)], 1)


def _sp_shrub(surf, cx, rim_y, v, night, t):
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
    P = v.palette
    dark, mid, top = _foliage(P, night)
    base = rim_y
    tiers = ((9, 0, 6), (7, -6, 6), (5, -12, 5), (3, -17, 4), (2, -21, 3))
    for hw, dy, th in tiers:
        ty = base + dy
        pygame.draw.polygon(surf, dark, [(cx - hw, ty), (cx + hw, ty), (cx, ty - th - 1)])
        pygame.draw.polygon(surf, mid, [(cx - hw + 1, ty - 1), (cx + hw - 1, ty - 1), (cx, ty - th)])
    pygame.draw.line(surf, top, (cx - 1, base - 14), (cx, base - 23), 1)


def _sp_topiary(surf, cx, rim_y, v, night, t):
    P, A = v.palette, v.attrs
    dark, mid, top = _foliage(P, night)
    trunk = _retint(P.get("trunk", (110, 84, 56)), night)
    tiers = A.get("tiers", 2)
    base = rim_y
    if tiers == 1:
        ball_r = 7
        stem_h = 15
        cy = base - stem_h - ball_r
        pygame.draw.line(surf, _shade(trunk, -22), (cx + 1, base + 1), (cx + 1, cy + ball_r - 1), 3)
        pygame.draw.line(surf, trunk, (cx, base + 1), (cx, cy + ball_r - 1), 2)
        pygame.draw.line(surf, _shade(trunk, 16), (cx, base + 1), (cx, cy + ball_r - 2), 1)
        pygame.draw.line(surf, dark, (cx - 2, base), (cx + 2, base), 2)
        pygame.draw.circle(surf, dark, (cx, cy), ball_r)
        pygame.draw.circle(surf, mid, (cx, cy), ball_r - 1)
        pygame.draw.circle(surf, top, (cx - ball_r // 3, cy - ball_r // 3), max(1, ball_r // 3))
        return
    radii = {2: (7, 5), 3: (6, 5, 4)}[tiers]
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
    spots = ((-6, -5), (-2, -9), (3, -7), (6, -3), (1, -12), (-5, -10),
             (5, -9), (-1, -4), (4, -11))
    for i, (bx, byp) in enumerate(spots):
        px, py = cx + bx + int(sway * (byp < -8)), base + byp
        col = ac if i % 3 else ac_lt
        pygame.draw.circle(surf, _accent(_shade(bloom, -28), night, day_ceil=dc), (px, py), 2)
        pygame.draw.circle(surf, col, (px, py), 1)


def _sp_bamboo(surf, cx, rim_y, v, night, t):
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


def _sp_vine(surf, cx, rim_y, v, night, t):
    P = v.palette
    dark, mid, top = _foliage(P, night)
    web = _mix(dark, (0, 0, 0), 0.18)
    base = rim_y
    sway = math.sin(t * 1.8)
    _dome(surf, cx - 4, base - 3, 6, 4, dark, mid)
    _dome(surf, cx + 4, base - 3, 6, 4, dark, mid)
    _dome(surf, cx, base - 5, 7, 5, dark, mid, top)
    for ang in (2.5, 2.1, 1.7, 1.3, 0.9, 0.5):
        _leaf_tuft(surf, cx, base - 5, ang, 7, mid, n=2, spread=0.5)
    for ang in (2.3, 1.6, 0.9):
        _leaf_tuft(surf, cx, base - 5, ang, 8, top, n=1, spread=0.0)
    strands = ((-7, 16, -3, 1.4), (-3, 19, -1, 1.8), (1, 20, 1, 2.0), (5, 17, 3, 1.6))
    paths = []
    for hx, ln, fan, swv in strands:
        pts = [(cx + hx, base - 1)]
        for i in range(1, ln + 1):
            tt = i / ln
            px = cx + hx + int(fan * tt * tt) - int(math.sin(tt * 1.6) * (swv * 0.4)) \
                + int(sway * tt * 1.3)
            py = base - 1 + int(tt * (ln + 2))
            pts.append((px, py))
        paths.append(pts)
    for a, b in zip(paths, paths[1:]):
        n = min(len(a), len(b))
        poly = a[:n] + list(reversed(b[:n]))
        if len(poly) >= 3:
            pygame.draw.polygon(surf, web, poly)
    hem = [p[-1] for p in paths]
    hem_full = [paths[0][-3] if len(paths[0]) >= 3 else paths[0][0]] + hem \
        + [paths[-1][-3] if len(paths[-1]) >= 3 else paths[-1][0]]
    pygame.draw.lines(surf, dark, False, hem_full, 2)
    for pts in paths:
        pygame.draw.lines(surf, dark, False, pts, 2)
        pygame.draw.lines(surf, mid, False, pts, 1)
    for k, pts in enumerate(paths):
        ln = len(pts)
        for ni in (max(2, ln // 3), max(3, (2 * ln) // 3), ln - 1):
            if ni >= ln:
                continue
            px, py = pts[ni]
            side = -1 if k < 2 else 1
            pygame.draw.polygon(surf, mid, [(px, py - 1), (px + side * 3, py), (px, py + 2)])
            pygame.draw.polygon(surf, dark, [(px, py - 1), (px + side * 3, py), (px, py + 2)], 1)
        pygame.draw.circle(surf, top, pts[-1], 1)


def _sp_flovine(surf, cx, rim_y, v, night, t):
    P, A = v.palette, v.attrs
    dark, mid, top = _foliage(P, night)
    base = rim_y
    sway = math.sin(t * 1.7)
    _dome(surf, cx - 5, base - 4, 6, 4, dark, mid)
    _dome(surf, cx + 5, base - 4, 6, 4, dark, mid)
    _dome(surf, cx, base - 6, 7, 5, dark, mid, top)
    bloom = P.get("accent", (200, 132, 170))
    dc = A.get("day_chroma", 172)
    ac = _accent(bloom, night, day_ceil=dc)
    ac_dk = _accent(_shade(bloom, -30), night, day_ceil=dc)
    ac_lt = _accent(_shade(bloom, 22), night, day_ceil=dc)
    falls = ((-8, 4, -3, 7, 3), (8, 4, 3, 7, 3), (0, 6, 0, 9, 4))
    for fi, (ox, slen, drift, ch, cw) in enumerate(falls):
        sx = cx + ox
        stem_pts = []
        for i in range(slen + 1):
            tt = i / slen
            px = sx + int(drift * tt) + int(sway * tt * 1.0)
            py = base - 2 + int(tt * slen)
            stem_pts.append((px, py))
        if len(stem_pts) >= 2:
            pygame.draw.lines(surf, dark, False, stem_pts, 1)
        topx, topy = stem_pts[-1]
        for j in range(ch):
            jt = j / max(1, ch - 1)
            half = max(0, int(round(cw * (1 - jt) * 0.5 + 0.5)))
            yy = topy + j + int(sway * jt * 1.2)
            xx = topx + int(drift * jt * 0.4)
            pygame.draw.line(surf, ac_dk, (xx - half, yy), (xx + half, yy), 1)
            if half >= 1:
                pygame.draw.circle(surf, ac, (xx - half, yy), 1 if half >= 2 else 0)
                pygame.draw.circle(surf, ac, (xx + half, yy), 1 if half >= 2 else 0)
            if j == 1:
                pygame.draw.circle(surf, ac_lt, (xx, yy), 0)
        pygame.draw.circle(surf, ac, (topx + int(drift * 0.4), topy + ch), 0)


def _sp_kumquat(surf, cx, rim_y, v, night, t):
    P = v.palette
    dark, mid, top = _foliage(P, night)
    trunk = _retint(P.get("trunk", (120, 88, 56)), night)
    base = rim_y
    th = 8
    pygame.draw.line(surf, _shade(trunk, -18), (cx + 1, base + 1), (cx + 1, base - th), 2)
    pygame.draw.line(surf, trunk, (cx, base + 1), (cx, base - th), 2)
    cy = base - th
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
    P, A = v.palette, v.attrs
    dark, mid, top = _foliage(P, night)
    trunk = _retint(P.get("trunk", (96, 66, 42)), night)
    m = A.get("mass", 1.1)
    nrib = A.get("ribbons", 5)
    base = rim_y
    th = int(13 * m)
    pygame.draw.line(surf, _shade(trunk, -20), (cx, base + 1), (cx - 1, base - th // 2), 3)
    pygame.draw.line(surf, trunk, (cx, base + 1), (cx - 1, base - th // 2), 2)
    pygame.draw.line(surf, trunk, (cx - 1, base - th // 2), (cx + 1, base - th), 2)
    cy = base - th - int(4 * m)
    span = int(11 * m)
    crown = (((-7, 2), 6), ((7, 2), 6), ((0, -3), 8), ((-4, -4), 5), ((5, -4), 5), ((0, 4), 6))
    for (ox, oy), r in crown:
        rr = int(r * m)
        _dome(surf, cx + int(ox * m), cy + oy, rr, int(rr * 0.82), dark, mid)
    pygame.draw.circle(surf, top, (cx - 2, cy - 3), int(2 * m))
    for a in (-1.0, -0.6, -0.2, 0.2, 0.6, 1.0):
        fx = cx + int(a * span)
        fy = cy + int(3 + abs(a) * 3)
        droop = int(round(math.sin(t * 1.6 + a * 2.0) * 1.0))
        pts = [(fx, fy), (fx + droop, fy + 4), (fx + droop, fy + 7)]
        pygame.draw.lines(surf, dark, False, pts, 2)
        pygame.draw.lines(surf, mid, False, pts, 1)
    nc = A.get("night_chroma_drop", 0)
    rib_col = P.get("accent", (200, 60, 56))
    rib = _accent(rib_col, night)
    if night > 0.05 and nc:
        rib = _mix(rib, (66, 72, 96), nc)
    rib_l = _accent(_shade(rib_col, 24), night)
    if night > 0.05 and nc:
        rib_l = _mix(rib_l, (66, 72, 96), nc)
    for i in range(nrib):
        a = (i / max(1, nrib - 1)) * 2 - 1
        rx = cx + int(a * span * 0.8)
        ry = cy + int(4 + abs(a) * 3)
        flut = int(round(math.sin(t * 2.2 + i * 1.3) * 1.5))
        pygame.draw.line(surf, rib, (rx, ry), (rx + flut, ry + 6), 2)
        pygame.draw.line(surf, rib_l, (rx, ry), (rx + flut, ry + 2), 1)


def _sp_peony(surf, cx, rim_y, v, night, t):
    """PEONY (mudan) — a low broad-leaf clump carrying 2-3 BIG layered double-blooms.
    Each head is a ruffled rosette (dark outer ring / mid body / lit whorl / pale
    petal-base eye — the Tang gongbi cinnabar-rose-over-white build). The few big
    heads proud above a trimmed leaf row are the silhouette — far bigger + fewer than
    the chrysanthemum's many tiny buttons, so the two flowering pots never read alike."""
    P, A = v.palette, v.attrs
    dark, mid, top = _foliage(P, night)
    base = rim_y
    sway = math.sin(t * 1.3) * 0.6
    for dx, dy, rw, rh in ((-6, 0, 7, 3), (6, 0, 7, 3), (0, -2, 8, 4)):
        _dome(surf, cx + dx, base + dy, rw, rh, dark, mid, top)
    bloom = P.get("accent", (208, 96, 110))
    dc = A.get("day_chroma", 178)
    pet_dk = _accent(_shade(bloom, -40), night, day_ceil=dc)
    pet = _accent(bloom, night, day_ceil=dc)
    pet_lt = _accent(_shade(bloom, 28), night, day_ceil=dc)
    base_pet = _accent(P.get("accent_pale", (236, 206, 200)), night, day_ceil=dc)
    for hx, hy, r in ((-6, -8, 5), (6, -9, 5), (0, -14, 6)):
        px = cx + hx + int(sway * (hy < -10))
        py = base + hy
        for a in range(6):
            ang = a / 6 * math.tau
            ex = px + int(round(math.cos(ang) * r * 0.82))
            ey = py + int(round(math.sin(ang) * r * 0.82))
            pygame.draw.circle(surf, pet_dk, (ex, ey), 2)
        pygame.draw.circle(surf, pet_dk, (px, py), r)
        pygame.draw.circle(surf, pet, (px, py), r - 1)
        pygame.draw.circle(surf, pet_lt, (px - 1, py - 1), max(1, r - 3))
        pygame.draw.circle(surf, base_pet, (px, py + 1), 1)
        pygame.draw.circle(surf, pet_dk, (px, py + 1), 1, 1)


def _sp_chrysanthemum(surf, cx, rim_y, v, night, t):
    """CHRYSANTHEMUM cushion mound — a dense LOW pincushion solidly studded with many
    small spoon-petal blooms (gold / russet). The whole surface is bloom, not foliage
    with stray dots — the opposite of the peony's few big heads. Russet shadow blooms
    low, gold catching light up top, the topmost crown blooms a value brighter so the
    crown reads MANY-studded, not a flat mound; kept clearly lower/wider than the peony."""
    P, A = v.palette, v.attrs
    dark, mid, top = _foliage(P, night)
    base = rim_y
    sway = math.sin(t * 1.5) * 0.5
    for dx, dy, rw, rh in ((-6, -2, 7, 5), (6, -2, 7, 5), (0, -6, 8, 6)):
        _dome(surf, cx + dx, base + dy, rw, rh, dark, mid)
    bloom = P.get("accent", (220, 162, 56))
    dc = A.get("day_chroma", 182)
    russet = P.get("accent2", (176, 96, 44))
    b_dk = _accent(_shade(bloom, -34), night, day_ceil=dc)
    b = _accent(bloom, night, day_ceil=dc)
    b_lt = _accent(_shade(bloom, 26), night, day_ceil=dc)
    b_crown = _accent(_shade(bloom, 44), night, day_ceil=dc)
    r_dk = _accent(_shade(russet, -26), night, day_ceil=dc)
    r_mid = _accent(russet, night, day_ceil=dc)
    spots = ((-7, -2, 0, 0), (-4, -6, 1, 0), (-1, -9, 1, 1), (2, -10, 1, 1),
             (5, -7, 1, 0), (7, -3, 0, 0), (-5, -3, 0, 0), (0, -6, 1, 0),
             (3, -6, 1, 0), (-2, -4, 0, 0), (5, -3, 0, 0), (-7, -5, 0, 0),
             (1, -12, 1, 1), (-3, -10, 1, 1), (6, -9, 1, 0))
    for bx, byp, gold, crown in spots:
        px, py = cx + bx + int(sway * (byp < -8)), base + byp
        if gold:
            pygame.draw.circle(surf, b_dk, (px, py), 2)
            pygame.draw.circle(surf, b, (px, py), 1)
            pygame.draw.circle(surf, b_crown if crown else b_lt, (px, py - 1), 0)
        else:
            pygame.draw.circle(surf, r_dk, (px, py), 2)
            pygame.draw.circle(surf, r_mid, (px, py), 1)


def _sp_plum(surf, cx, rim_y, v, night, t):
    """PLUM-BLOSSOM branch (winter meihua) — dark zig-zag dragon-branches from a slim
    vessel, the BLOSSOM clustered at tips + joints so the FLOWER is the silhouette,
    not garnish on a dead twig. Most nodes carry a 2x2 pink-white petal cluster with a
    warm-white centre pip; a few carry an unopened bud. The branch ink is lifted one
    value step + the low tangle thinned so the airy angular read survives at far size."""
    P, A = v.palette, v.attrs
    branch = _retint(_shade(P.get("trunk", (74, 58, 52)), 14), night)
    br_lt = _hi(branch, 22, night)
    base = rim_y
    sway = int(round(math.sin(t * 1.4) * 1.0))
    branches = (
        [(0, 0), (-3, -6), (1, -11), (-2, -17), (sway, -22)],
        [(1, -4), (6, -8), (3, -13), (7, -18)],
        [(0, -6), (-5, -10), (-8, -14)],
    )
    nodes = []
    for seg in branches:
        pts = [(cx + dx, base + dy) for dx, dy in seg]
        pygame.draw.lines(surf, branch, False, pts, 2)
        pygame.draw.lines(surf, br_lt, False, [(x - 1, y) for x, y in pts], 1)
        nodes.extend(pts[1:])
    bloom = P.get("accent", (234, 198, 208))
    dc = A.get("day_chroma", 176)
    pet = _accent(bloom, night, day_ceil=dc)
    pet_dk = _accent(_shade(bloom, -34), night, day_ceil=dc)
    pet_ctr = _accent(_shade(bloom, 30), night, day_ceil=dc)
    bud = _accent(P.get("accent2", (208, 122, 140)), night, day_ceil=dc)
    for i, (nx, ny) in enumerate(nodes):
        if i % 3 == 2:
            pygame.draw.circle(surf, bud, (nx, ny), 0)
        else:
            pygame.draw.rect(surf, pet_dk, (nx - 1, ny - 1, 4, 4))
            pygame.draw.rect(surf, pet, (nx - 1, ny - 1, 3, 3))
            pygame.draw.circle(surf, pet_ctr, (nx, ny), 0)


def _sp_maple(surf, cx, rim_y, v, night, t):
    """RED MAPLE (Acer palmatum) — a small palmate-leaf tree: a slim forking trunk
    lifting a broad AUTUMN canopy of clustered shaded leaf masses (the warm canopy
    lives in the foliage_* roles, capped via _accent). A maroon underside notch + an
    amber rim-lit top edge keep the crown reading as clustered masses, not a solid
    disc — a little fire-tree in a wooden tub."""
    P, A = v.palette, v.attrs
    trunk = _retint(P.get("trunk", (96, 70, 50)), night)
    base = rim_y
    dc = A.get("day_chroma", 182)
    leaf_dk = _accent(P.get("foliage_dark", (132, 50, 40)), night, day_ceil=dc)
    leaf_mid = _accent(P.get("foliage_mid", (190, 84, 48)), night, day_ceil=dc)
    leaf_lt = _accent(P.get("foliage_top", (224, 150, 64)), night, day_ceil=dc)
    leaf_notch = _accent(_shade(P.get("foliage_dark", (132, 50, 40)), -30), night, day_ceil=dc)
    sway = math.sin(t * 1.3) * 0.5
    th = 9
    pygame.draw.line(surf, _shade(trunk, -18), (cx + 1, base + 1), (cx + 1, base - th), 2)
    pygame.draw.line(surf, trunk, (cx, base + 1), (cx, base - th), 2)
    pygame.draw.line(surf, trunk, (cx, base - th + 2), (cx - 4, base - th - 2), 1)
    pygame.draw.line(surf, trunk, (cx, base - th + 2), (cx + 4, base - th - 2), 1)
    cy = base - th - 2
    lobes = ((-6, 1, 5, 4), (6, 1, 5, 4), (0, -4, 6, 5),
             (-4, -3, 4, 4), (4, -3, 4, 4), (0, 2, 5, 4))
    for dx, dy, rw, rh in lobes:
        _dome(surf, cx + dx + int(sway * (dy < -2)), cy + dy, rw, rh,
              leaf_dk, leaf_mid, leaf_lt)
    pygame.draw.line(surf, leaf_notch, (cx - 1, cy + 4), (cx + 1, cy + 5), 2)
    pygame.draw.circle(surf, leaf_notch, (cx, cy + 5), 1)
    pygame.draw.arc(surf, leaf_lt, (cx - 6, cy - 9, 12, 11),
                    math.radians(35), math.radians(150), 1)
    for px, py in ((-7, -2), (-2, -7), (3, -6), (7, -1), (0, -8), (-5, 2), (5, 2)):
        pygame.draw.circle(surf, leaf_lt, (cx + px, cy + py), 0)


def _sp_narcissus(surf, cx, rim_y, v, night, t):
    """NARCISSUS / paperwhite (shuixian) — a clump of strappy upright blades fanning
    from a shallow dish, topped with 4 small WHITE cup flowers (a petal ring over a
    dark calyx seat so the cup has body) each with a GOLD centre pip as the warm focal.
    The lowest, most delicate read in the family — delicate but not absent, surviving
    the night band."""
    P, A = v.palette, v.attrs
    dark, mid, top = _foliage(P, night)
    base = rim_y
    sway = math.sin(t * 1.7) * 0.8
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
    for ox, ln in ((-3, 14), (2, 15), (5, 12), (-6, 11)):
        fx = cx + ox + int(sway)
        fy = base - ln
        pygame.draw.circle(surf, pet_dk, (fx, fy), 2)
        for a in range(6):
            ang = a / 6 * math.tau
            ex = fx + int(round(math.cos(ang) * 1.7))
            ey = fy + int(round(math.sin(ang) * 1.7))
            pygame.draw.circle(surf, pet, (ex, ey), 0)
        pygame.draw.circle(surf, pet, (fx, fy), 1)
        pygame.draw.circle(surf, cup_dk, (fx, fy), 1, 1)
        pygame.draw.circle(surf, cup, (fx, fy), 0)


def _sp_lotus(surf, cx, rim_y, v, night, t):
    """LOTUS (lianhua) — the floating PADS are the hero: three flat round lily-pad
    DISCS at water level (the dominant horizontal mass), each a flat ellipse with a
    1px darker waterline rim + a lighter top face + a single radial vein-notch slit,
    so each reads as a top-lit pad floating on water. The pink is a SMALL accent —
    one open petal-cup + one bud on a single short stem just clear of the pads — so
    the bloom doesn't dominate (no collision with the narcissus 'flowering stems')."""
    P, A = v.palette, v.attrs
    dark, mid, top = _foliage(P, night)
    base = rim_y
    ripple = math.sin(t * 1.1) * 0.5
    pads = ((1, -2, 5, 2, +1), (-7, 0, 9, 3, -1), (6, 1, 9, 3, +1))
    for dx, dy, rw, rh, vdir in pads:
        px = cx + dx + int(ripple * (dy < 0))
        py = base + dy
        pygame.draw.ellipse(surf, _shade(dark, -14), (px - rw, py - rh, rw * 2, rh * 2))
        pygame.draw.ellipse(surf, mid, (px - rw + 1, py - rh + 1, rw * 2 - 2, rh * 2 - 1))
        pygame.draw.ellipse(surf, top, (px - rw + 2, py - rh + 1, rw * 2 - 4, max(1, rh)))
        pygame.draw.line(surf, _shade(dark, -10), (px, py), (px + vdir * (rw - 1), py), 1)
    stem = _retint(P.get("stem", (96, 138, 84)), night)
    bloom = P.get("accent", (228, 150, 178))
    dc = A.get("day_chroma", 176)
    pet_dk = _accent(_shade(bloom, -40), night, day_ceil=dc)
    pet = _accent(bloom, night, day_ceil=dc)
    pet_lt = _accent(_shade(bloom, 26), night, day_ceil=dc)
    heart = _accent(P.get("accent2", (232, 206, 120)), night, day_ceil=dc)
    obx = cx - 3
    oby = base - 9 + int(ripple)
    pygame.draw.line(surf, _shade(stem, -16), (obx, base - 2), (obx, oby + 2), 2)
    pygame.draw.line(surf, _shade(stem, 18), (obx, base - 2), (obx, oby + 2), 1)
    pygame.draw.polygon(surf, pet_dk, [
        (obx - 3, oby + 2), (obx, oby - 3), (obx + 3, oby + 2), (obx, oby + 1)])
    for sx, hgt in ((-3, 3), (0, 5), (3, 3)):
        tipx = obx + sx
        pygame.draw.line(surf, pet, (obx, oby + 1), (tipx, oby - hgt), 2)
        pygame.draw.line(surf, pet_lt, (obx, oby + 1), (tipx, oby - hgt + 1), 1)
    pygame.draw.circle(surf, heart, (obx, oby - 1), 1)
    bbx = cx + 5
    bby = base - 7 - int(ripple)
    pygame.draw.line(surf, _shade(stem, -16), (bbx, base - 2), (bbx, bby + 1), 2)
    pygame.draw.line(surf, _shade(stem, 18), (bbx, base - 2), (bbx, bby + 1), 1)
    pygame.draw.polygon(surf, pet_dk, [(bbx - 2, bby + 2), (bbx, bby - 3), (bbx + 2, bby + 2)])
    pygame.draw.polygon(surf, pet, [(bbx - 1, bby + 1), (bbx, bby - 2), (bbx + 1, bby + 1)])
    pygame.draw.circle(surf, pet_lt, (bbx, bby - 1), 0)


def _sp_fern(surf, cx, rim_y, v, night, t):
    """FERN (Boston / sword) — a symmetric SHUTTLECOCK fountain: arching fronds
    spreading evenly up-and-out from a central crown in mirrored pairs. Each frond is
    a curved rachis (bowing outward then dropping at the tip) hung with short pinnae
    notches; the front three carry the notch rhythm so it reads LACY, the low outer
    pair arches + droops to form the fountain rim. Soft/cool ARCHED counterpart to
    the cycad's stiff radial star, and a tight ground rosette unlike the bamboo."""
    P, A = v.palette, v.attrs
    dark, mid, top = _foliage(P, night)
    base = rim_y
    crown_x = cx
    crown_y = base - 1
    sway = math.sin(t * 1.5) * 0.10
    fronds = (
        (1.5708, 18, 0.25, 0, True),
        (1.86, 17, 0.42, 0, True), (1.28, 17, 0.42, 0, True),
        (2.18, 17, 0.66, 1, False), (0.96, 17, 0.66, 1, False),
        (2.50, 16, 0.92, 1, False), (0.64, 16, 0.92, 1, False),
    )
    for ang0, ln, arch, droop, notched in fronds:
        ang0 += sway * (1 if ang0 < 1.5708 else -1)
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
        if notched:
            for s in range(1, steps):
                (x0, y0) = pts[s]
                (x1, y1) = pts[s + 1]
                dxs, dys = x1 - x0, y1 - y0
                blen = max(1, 3 - s // 2)
                nx, ny = -dys, dxs
                nl = math.hypot(nx, ny) or 1.0
                nx, ny = nx / nl, ny / nl
                bx = x0 + int(round(nx * blen))
                by = y0 + int(round(ny * blen))
                pygame.draw.line(surf, dark, (x0, y0), (bx, by), 1)
                pygame.draw.line(surf, dark, (x0, y0),
                                 (x0 - int(round(nx * blen)), y0 - int(round(ny * blen))), 1)
        pygame.draw.circle(surf, top, pts[-1], 0)
    pygame.draw.circle(surf, dark, (crown_x, crown_y), 2)
    pygame.draw.circle(surf, mid, (crown_x, crown_y - 1), 1)


def _sp_cycad(surf, cx, rim_y, v, night, t):
    """CYCAD / sago palm — a stiff symmetric crown of rigid straight spear-fronds
    radiating in a flat STAR from a fat scaly trunk-knob. Each frond is a straight
    rachis (no arch) lined with stiff comb-teeth + a spine tip; the 2 outermost
    spears each side taper to single-pixel needle points so the hard radial star
    reads crisp — the architectural opposite of the fern's soft droop."""
    P, A = v.palette, v.attrs
    dark, mid, top = _foliage(P, night)
    base = rim_y
    knob = _retint(P.get("trunk", (104, 84, 56)), night)
    knob_dk = _shade(knob, -26)
    knob_lt = _hi(knob, 18, night)
    ky = base - 4
    pygame.draw.ellipse(surf, knob_dk, (cx - 6, ky - 1, 12, 9))
    pygame.draw.ellipse(surf, knob, (cx - 5, ky, 10, 7))
    pygame.draw.arc(surf, knob_lt, (cx - 5, ky, 10, 7), math.radians(40), math.radians(150), 1)
    for sx in (-3, 0, 3):
        pygame.draw.line(surf, knob_dk, (cx + sx, ky + 1), (cx + sx, ky + 5), 1)
    for sy in (ky + 2, ky + 4):
        pygame.draw.line(surf, knob_dk, (cx - 4, sy), (cx + 4, sy), 1)
    crown_x = cx
    crown_y = ky - 1
    breathe = math.sin(t * 1.2) * 0.05
    n = 11
    a_lo, a_hi = math.radians(8), math.radians(172)
    for i in range(n):
        frac = i / (n - 1)
        ang = a_lo + (a_hi - a_lo) * frac + breathe * math.cos(frac * math.pi)
        ln = 17 if (0.30 < frac < 0.70) else 14
        ex = crown_x + int(round(math.cos(ang) * ln))
        ey = crown_y - int(round(math.sin(ang) * ln))
        lit = 0.30 < frac < 0.70
        spine = top if lit else mid
        outer = (i <= 1) or (i >= n - 2)
        pygame.draw.line(surf, dark, (crown_x, crown_y), (ex, ey), 2)
        pygame.draw.line(surf, spine, (crown_x, crown_y), (ex, ey), 1)
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
            tipx = crown_x + int(round(ux * (ln + 1)))
            tipy = crown_y + int(round(uy * (ln + 1)))
            pygame.draw.line(surf, dark, (ex, ey), (tipx, tipy), 1)
            pygame.draw.circle(surf, dark, (tipx, tipy), 0)
        else:
            pygame.draw.circle(surf, dark, (ex, ey), 0)
    pygame.draw.circle(surf, top, (crown_x, crown_y - 1), 1)


def _sp_banana(surf, cx, rim_y, v, night, t):
    """BANANA / broadleaf (Musa) — 2 huge paddle leaves (long lozenge blades about a
    bold central midrib, the windward edge cut with the species' tear-notches) +
    one upright furled new-leaf spike, splaying from a short pseudostem. The biggest,
    broadest leaf-mass in the family — tropical, no flowers; the torn edges + heavy
    midrib are the signature, distinct from the cycad's spiky star + the fern's lace."""
    P, A = v.palette, v.attrs
    dark, mid, top = _foliage(P, night)
    base = rim_y
    rib = _retint(P.get("stem", (150, 176, 96)), night)
    sway = math.sin(t * 1.0) * 0.08
    pygame.draw.line(surf, _shade(rib, -22), (cx + 1, base + 1), (cx + 1, base - 4), 3)
    pygame.draw.line(surf, rib, (cx, base + 1), (cx, base - 4), 2)
    cy = base - 4

    def _paddle(ang, ln, half, side, lit):
        ang += sway
        ux, uy = math.cos(ang), -math.sin(ang)
        px, py = -uy, ux
        tip = (cx + ux * ln, cy + uy * ln)
        edge_a, edge_b = [], []
        steps = 7
        for s in range(steps + 1):
            tt = s / steps
            w = half * math.sin(min(1.0, tt * 1.15) * math.pi) ** 0.7
            bx = cx + ux * (ln * tt)
            by = cy + uy * (ln * tt)
            edge_a.append((bx + px * w, by + py * w))
            edge_b.append((bx - px * w, by - py * w))
        poly = [(int(round(x)), int(round(y))) for x, y in edge_a] + \
               [(int(round(x)), int(round(y))) for x, y in reversed(edge_b)]
        pygame.draw.polygon(surf, dark, poly)
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
        pygame.draw.line(surf, _shade(rib, -10), (cx, cy),
                         (int(round(tip[0])), int(round(tip[1]))), 2)
        pygame.draw.line(surf, rib, (cx, cy),
                         (int(round(tip[0])), int(round(tip[1]))), 1)
        if lit:
            le = [edge_a[s] if side > 0 else edge_b[s] for s in range(2, steps)]
            le = [(int(round(x)), int(round(y))) for x, y in le]
            if len(le) >= 2:
                pygame.draw.lines(surf, top, False, le, 1)
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

    _paddle(2.50, 17, 6, +1, True)
    _paddle(0.64, 17, 6, -1, True)
    sp_ang = 1.5708 + sway * 0.5
    sx2 = cx + int(round(math.cos(sp_ang) * 18))
    sy2 = cy - int(round(math.sin(sp_ang) * 18))
    pygame.draw.line(surf, dark, (cx, cy), (sx2, sy2), 3)
    pygame.draw.line(surf, mid, (cx, cy), (sx2, sy2), 1)
    pygame.draw.circle(surf, top, (sx2, sy2), 1)


def _sp_rock(surf, cx, rim_y, v, night, t):
    """SCHOLAR'S ROCK (gongshi / Taihu) — a tall asymmetric pierced grey limestone
    monolith on its tray, with a small moss/fern tuft at the foot: the literati-garden
    OBJECT, the only non-plant silhouette. A craggy vertical fang in three cool greys
    (shadow / body / lit ridge), fluted with erosion grooves and PIERCED with two
    through-holes (the dissolution pockets of Lake Tai stone) that show the background
    through the rock — transparent on an SRCALPHA target, else the sampled hole_bg."""
    P, A = v.palette, v.attrs
    base = rim_y
    stone = _night_lift(_retint(P.get("rock", (150, 152, 158)), night), night, 0.18)
    stone_dk = _night_lift(_retint(P.get("rock_dk", (96, 100, 110)), night), night, 0.12)
    stone_lt = _hi(stone, 22, night)
    body = [
        (cx - 6, base), (cx - 7, base - 7), (cx - 4, base - 13), (cx - 6, base - 19),
        (cx - 3, base - 25), (cx - 4, base - 29), (cx + 1, base - 31), (cx + 4, base - 27),
        (cx + 2, base - 22), (cx + 6, base - 17), (cx + 4, base - 9), (cx + 7, base),
    ]
    pygame.draw.polygon(surf, stone_dk, body)
    inner = [(x - (1 if x > cx else -1), y + (1 if y < base else 0)) for x, y in body]
    pygame.draw.polygon(surf, stone, inner)
    ridge = [(cx - 5, base - 8), (cx - 3, base - 14), (cx - 4, base - 20),
             (cx - 2, base - 26), (cx + 1, base - 30)]
    pygame.draw.lines(surf, stone_lt, False, ridge, 1)
    for gx, gy0, gy1 in ((-2, base - 6, base - 24), (2, base - 4, base - 20),
                         (4, base - 12, base - 25)):
        pygame.draw.line(surf, stone_dk, (cx + gx, gy0), (cx + gx, gy1), 1)
    hole_bg = A.get("hole_bg")
    srcalpha = bool(surf.get_flags() & pygame.SRCALPHA)
    for hx, hy, hr in ((-2, base - 16, 2), (2, base - 23, 1)):
        cxp, cyp = cx + hx, hy
        pygame.draw.circle(surf, stone_dk, (cxp, cyp), hr + 1)
        if srcalpha:
            for ddx in range(-hr, hr + 1):
                for ddy in range(-hr, hr + 1):
                    if ddx * ddx + ddy * ddy <= hr * hr:
                        surf.set_at((cxp + ddx, cyp + ddy), (0, 0, 0, 0))
        elif hole_bg is not None:
            pygame.draw.circle(surf, hole_bg, (cxp, cyp), hr)
        else:
            pygame.draw.circle(surf, _shade(stone_dk, -34), (cxp, cyp), hr)
        pygame.draw.arc(surf, stone_lt, (cxp - hr - 1, cyp - hr - 1, (hr + 1) * 2, (hr + 1) * 2),
                        math.radians(200), math.radians(340), 1)
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


# ── the 30-design pool → foreground_variants rows ─────────────────────────────

_TERRA = dict(vessel=(176, 104, 70), vessel_dk=(120, 64, 42))
_URN = dict(vessel=(228, 230, 234), vessel_dk=(170, 176, 188), glaze=(72, 104, 168))
_TUB = dict(vessel=(140, 100, 62), vessel_dk=(92, 62, 38))
_BAMBOO_V = dict(vessel=(156, 166, 100), vessel_dk=(96, 108, 60))
_STONE = dict(vessel=(156, 148, 130), vessel_dk=(104, 98, 86))
_FOL_LEAFY = dict(foliage_dark=(40, 84, 54), foliage_mid=(62, 116, 74), foliage_top=(104, 158, 100))
_FOL_DARK = dict(foliage_dark=(30, 64, 48), foliage_mid=(44, 88, 62), foliage_top=(74, 122, 86))
_FOL_CLIP = dict(foliage_dark=(46, 86, 56), foliage_mid=(72, 120, 78), foliage_top=(118, 162, 110))
# broad grass-green peony/mum/narcissus leaf bank (Tang gongbi "grass green")
_FOL_BROAD = dict(foliage_dark=(36, 78, 50), foliage_mid=(58, 110, 70), foliage_top=(100, 152, 96))
# maple AUTUMN canopy carried in the foliage roles (warm; capped via _accent)
_FOL_MAPLE = dict(foliage_dark=(132, 50, 40), foliage_mid=(192, 86, 48), foliage_top=(226, 150, 66))
# batch-2 structural foliage banks
_FOL_FERN = dict(foliage_dark=(34, 82, 62), foliage_mid=(56, 118, 84), foliage_top=(110, 166, 124))
_FOL_CYCAD = dict(foliage_dark=(26, 62, 44), foliage_mid=(42, 92, 60), foliage_top=(92, 146, 96))
_FOL_BANANA = dict(foliage_dark=(32, 76, 46), foliage_mid=(54, 112, 66), foliage_top=(108, 164, 96))
_FOL_LOTUS = dict(foliage_dark=(34, 80, 56), foliage_mid=(58, 116, 78), foliage_top=(112, 162, 116))
_FOL_MOSS = dict(foliage_dark=(40, 78, 50), foliage_mid=(64, 110, 70), foliage_top=(108, 152, 100))
# batch-3 combo foliage banks (new palettes over the shipped drawers)
_FOL_LUSH = dict(foliage_dark=(28, 74, 46), foliage_mid=(48, 108, 66), foliage_top=(96, 152, 92))
_FOL_PINE = dict(foliage_dark=(30, 70, 58), foliage_mid=(46, 96, 78), foliage_top=(82, 134, 104))
_FOL_BOX = dict(foliage_dark=(48, 92, 56), foliage_mid=(80, 130, 82), foliage_top=(128, 172, 116))
_FOL_AZALEA = dict(foliage_dark=(40, 82, 52), foliage_mid=(64, 116, 74), foliage_top=(106, 156, 98))
_FOL_DRAPE = dict(foliage_dark=(28, 70, 50), foliage_mid=(46, 100, 68), foliage_top=(90, 144, 100))
# batch-4 combo foliage banks
_FOL_CITRUS = dict(foliage_dark=(26, 66, 50), foliage_mid=(42, 92, 64), foliage_top=(78, 130, 90))
_FOL_YEW = dict(foliage_dark=(30, 62, 42), foliage_mid=(46, 92, 58), foliage_top=(86, 134, 84))
_FOL_GARDENIA = dict(foliage_dark=(34, 74, 58), foliage_mid=(54, 104, 80), foliage_top=(96, 146, 110))
_FOL_WISTERIA = dict(foliage_dark=(38, 80, 52), foliage_mid=(60, 112, 70), foliage_top=(102, 152, 96))
_FOL_EMBER = dict(foliage_dark=(120, 46, 44), foliage_mid=(178, 78, 50), foliage_top=(214, 138, 70))


def _row(*banks, **attrs):
    pal = {}
    for b in banks:
        pal.update(b)
    return fv.Variant(palette=pal, attrs=dict(attrs))


def _build_greenery():
    return [
        _row(_TERRA, _FOL_LEAFY, dict(accent=(206, 120, 138)),
             vessel="terracotta", species="shrub", mass=1.0),
        _row(_STONE, _FOL_DARK, vessel="trough", species="conifer", vlift=0.10),
        _row(_URN, _FOL_CLIP, vessel="urn", species="topiary", tiers=3, trunk=(96, 84, 66)),
        _row(_TERRA, _FOL_CLIP, vessel="terracotta", species="topiary", tiers=1, trunk=(110, 84, 56)),
        _row(_URN, _FOL_DARK, dict(accent=(204, 122, 142)),
             vessel="urn", species="flowering", day_chroma=170),
        _row(_URN, _FOL_LEAFY, dict(accent=(192, 120, 168)),
             vessel="urn", species="flovine", day_chroma=172),
        _row(_BAMBOO_V, _FOL_LEAFY, dict(trunk=(150, 178, 108)), vessel="bamboo", species="bamboo"),
        _row(_STONE, _FOL_LEAFY, dict(vlift=0.10), vessel="trough", species="vine"),
        _row(_TERRA, _FOL_DARK, dict(accent=(222, 142, 52), trunk=(120, 88, 56)),
             vessel="terracotta", species="kumquat"),
        _row(_URN, _FOL_DARK, dict(trunk=(96, 66, 42), accent=(192, 64, 60)),
             vessel="urn", species="wishtree", mass=1.15, ribbons=6, night_chroma_drop=0.22),
        # ── batch 1: flowering / seasonal new species (indices 10-14) ──
        _row(_URN, _FOL_BROAD, dict(accent=(208, 90, 108), accent_pale=(236, 208, 202)),
             vessel="urn", species="peony", day_chroma=178),
        _row(_TERRA, _FOL_BROAD, dict(accent=(222, 164, 56), accent2=(178, 98, 46)),
             vessel="terracotta", species="chrysanthemum", day_chroma=182),
        _row(_BAMBOO_V, dict(trunk=(74, 58, 52), accent=(236, 200, 210), accent2=(210, 124, 142)),
             vessel="bamboo", species="plum", day_chroma=176),
        _row(_TUB, _FOL_MAPLE, dict(trunk=(96, 70, 50)),
             vessel="tub", species="maple", day_chroma=182),
        _row(_URN, _FOL_BROAD, dict(accent=(238, 234, 224), accent2=(230, 180, 58)),
             vessel="dish", species="narcissus", day_chroma=180),
        # ── batch 2: structural / foliage new species (indices 15-19) ──
        _row(_STONE, _FOL_LOTUS, dict(glaze=(62, 100, 152), stem=(96, 138, 84),
                                      accent=(228, 150, 178), accent2=(232, 206, 120)),
             vessel="basin", species="lotus", vlift=0.10, day_chroma=176),
        _row(_STONE, _FOL_FERN, dict(vlift=0.10), vessel="trough", species="fern"),
        _row(_URN, _FOL_CYCAD, dict(trunk=(106, 86, 58)), vessel="urn", species="cycad"),
        _row(_TUB, _FOL_BANANA, dict(stem=(150, 176, 96)), vessel="tub", species="banana"),
        _row(_STONE, _FOL_MOSS, dict(rock=(150, 152, 158), rock_dk=(96, 100, 110),
                                     vessel=(96, 78, 60), vessel_dk=(60, 48, 38)),
             vessel="tray", species="rock", vlift=0.0),
        # ── batch 3: fresh combos of existing species (indices 20-24) ──
        _row(_TUB, _FOL_LUSH, vessel="tub", species="shrub", mass=1.2),
        _row(_TERRA, _FOL_PINE, vessel="terracotta", species="conifer"),
        _row(_BAMBOO_V, _FOL_BOX, dict(trunk=(120, 92, 60)),
             vessel="bamboo", species="topiary", tiers=2),
        _row(_TERRA, _FOL_AZALEA, dict(accent=(238, 158, 120)),
             vessel="terracotta", species="flowering", day_chroma=186),
        _row(_BAMBOO_V, _FOL_DRAPE, vessel="bamboo", species="vine"),
        # ── batch 4: final combos to 30 (indices 25-29) ──
        _row(_URN, _FOL_CITRUS, dict(accent=(224, 150, 56), trunk=(116, 86, 56)),
             vessel="urn", species="kumquat"),
        _row(_TUB, _FOL_YEW, dict(trunk=(104, 78, 52)),
             vessel="tub", species="topiary", tiers=3),
        _row(_STONE, _FOL_GARDENIA, dict(accent=(232, 230, 222)),
             vessel="trough", species="flowering", day_chroma=150, vlift=0.10),
        _row(_TERRA, _FOL_WISTERIA, dict(accent=(158, 130, 196)),
             vessel="terracotta", species="flovine", day_chroma=160),
        _row(_URN, _FOL_EMBER, dict(trunk=(92, 66, 48)),
             vessel="urn", species="maple", day_chroma=178),
    ]


fv.register("greenery", _build_greenery())
