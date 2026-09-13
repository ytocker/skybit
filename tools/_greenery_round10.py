"""Promenade PLANTS & GREENERY — round 10 candidate-sheet generator.

GREENERY POOL EXPANSION, batch 4 of 4 — the FINAL FIVE COMBOS of the EXISTING
shipped species (NO new species drawers, NO new vessels), pool indices 25-29.
This completes the family from 25 to 30. The shipped 25 are UNCHANGED.

Each of the 5 uses an UNUSED vessel x species pairing for guaranteed far-size
distinctness, then refines palette / size / accent for charm + maximum
separation from BOTH its closest shipped sibling AND the other 4 new combos.

THE 5 FINAL COMBOS:
  P26 glazed-urn KUMQUAT  — the orange fruiting tree in the BLUE-WHITE GLAZED
                            urn (vs the shipped terracotta kumquat G9): the cool
                            white-porcelain urn value is the polar opposite of
                            G9's warm terracotta, so the two never read alike at
                            far size even though both carry warm orange fruit.
  P27 wooden-tub TOPIARY  — a tall 3-tier clipped topiary in the staved WOODEN
                            TUB (vs urn 3-tier G3 / bamboo 2-tier G23 / terracotta
                            1-tier G4): a NEW vessel for the topiary; the dark
                            warm-wood tub + a deep formal-yew green separate it
                            from the bright white-urn 3-tier.
  P28 stone-trough FLOWERING — a cool near-WHITE gardenia/jasmine flowering shrub
                            in the cool STONE trough (vs urn plum G5 + terracotta
                            peach G24): a cool white accent + low day_chroma + a
                            cool grey vessel reads as a different SEASON/colour;
                            vlift keeps the low trough present at night.
  P29 terracotta FLOVINE  — a cascading-bloom flovine in TERRACOTTA with a cool
                            VIOLET / wisteria accent (vs the urn magenta flovine
                            G6): a warm vessel + a cooler violet bloom + a fresh
                            leaf bank read as a different plant entirely.
  P30 glazed-urn MAPLE    — the autumn fire-canopy maple in the BLUE-WHITE GLAZED
                            urn (vs the wooden-tub maple G14): the cool white
                            porcelain base under the warm canopy is a distinct
                            vessel pairing (chosen option A — the urn proportions
                            sit the slim maple trunk cleanly on the neck; the
                            far-size silhouette stays the little fire-tree but on
                            a bright cool vessel, a clear value flip vs the dark
                            warm tub maple).

This generator IMPORTS the shipped helpers + the SHIPPED draw_greenery from
game.greenery_cast, so the explorations are drawn by the EXACT production code
path / night-cap contract — these combos reuse shipped drawers + vessels, so no
patching of dispatch is needed. It defines only 5 new Variant rows over the
shipped palette banks (+ a few fresh foliage / accent banks for distinctness)
and renders the standard sheet. Nothing here mutates production game files — the
orchestrator renders + commits.

Sheet layout MIRRORS round 9: true far-lane DAY + NIGHT bands with an adult +
gold-coin yardstick, per-design DAY/NIGHT cells (true far size + 4x nearest zoom
+ vessel/species/attrs note), an on-street composite interleaving the 5 NEW
combos with their shipped SIBLINGS (so each combo can be read against the
shipped row it must not duplicate) + human cast + a stall + the coin, and the
_measure_night_cap() audit footer (PASS only when hottest greenery <=150 and the
~230 gold coin stays sole-brightest).
"""
from __future__ import annotations

import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((1, 1))

# Import the SHIPPED production helpers + draw path so the new COMBOS are drawn by
# the exact same code / night-cap contract as the shipped 25. These rows reuse
# shipped drawers + vessels only, so draw_greenery is used UNMODIFIED.
from game import greenery_cast as gc  # noqa: E402
from game.greenery_cast import (  # noqa: E402
    _retint, _accent, _hi, _mix, _shade, _luma, draw_greenery,
    VESSEL_H, NIGHT_GLOW_CAP,
)
from game import foreground_variants as fv  # noqa: E402


# ════════════════════════════════════════════════════════════════════════════
# THE 5 NEW ROWS — foreground_variants.Variant data (pool indices 25-29).
# Reuse the shipped palette banks (_TERRA/_URN/_TUB/_STONE) + a few fresh
# foliage/accent banks so each combo reads DISTINCT from its shipped sibling AND
# from the other 4 new combos. Pure DATA — no new drawers, no new vessels.
# ════════════════════════════════════════════════════════════════════════════

_TERRA = dict(gc._TERRA)
_URN = dict(gc._URN)
_TUB = dict(gc._TUB)
_STONE = dict(gc._STONE)

# fresh foliage banks (distinct from every shipped bank):
# a colder citrus-leaf bank for the glazed-urn kumquat — a touch bluer + a value
# down from the shipped _FOL_DARK the terracotta kumquat G9 uses, so the canopy
# reads as its own cooler tree, the cool urn echoing into the leaf.
_FOL_CITRUS = dict(foliage_dark=(26, 66, 50), foliage_mid=(42, 92, 64), foliage_top=(78, 130, 90))
# a deep formal YEW green for the wooden-tub topiary — the darkest, most saturated
# clip-green in the family (below the bright box _FOL_CLIP / _FOL_BOX) so the
# tub 3-tier reads as a heavy dark hedge-yew, not the bright white-urn 3-tier.
_FOL_YEW = dict(foliage_dark=(30, 62, 42), foliage_mid=(46, 92, 58), foliage_top=(86, 134, 84))
# a soft cool grey-green gardenia leaf for the stone-trough white flowering — a
# muted blue-leaning leaf so the cool near-white bloom sits as the season's note,
# distinct from the warm azalea / plum leaf banks.
_FOL_GARDENIA = dict(foliage_dark=(34, 74, 58), foliage_mid=(54, 104, 80), foliage_top=(96, 146, 110))
# a soft mid leaf for the terracotta wisteria flovine — a warmer grass-green than
# the urn flovine's _FOL_LEAFY so the violet bloom reads against its own leaf.
_FOL_WISTERIA = dict(foliage_dark=(38, 80, 52), foliage_mid=(60, 112, 70), foliage_top=(102, 152, 96))
# a cooler EMBER maple canopy for the glazed-urn maple — pulled a step cooler +
# down from the shipped tub maple's _FOL_MAPLE so the fire-tree on the bright cool
# urn reads as a later, deeper-autumn canopy, not the same warm tub maple.
_FOL_EMBER = dict(foliage_dark=(120, 46, 44), foliage_mid=(178, 78, 50), foliage_top=(214, 138, 70))


def _row(*banks, **attrs):
    pal = {}
    for b in banks:
        pal.update(b)
    return fv.Variant(palette=pal, attrs=dict(attrs))


POOL = [
    ("P26 glazed-urn KUMQUAT", _row(
        _URN, _FOL_CITRUS, dict(accent=(224, 150, 56), trunk=(116, 86, 56)),
        vessel="urn", species="kumquat"),
     "vessel:urn(shipped blue-white glazed porcelain) species:kumquat accent:warm orange fruit trunk | the orange fruiting citrus in the COOL WHITE glazed urn — vs the shipped kumquat G9 (warm TERRACOTTA, warm orange fruit): same warm fruit, but the bright cool porcelain vessel is the polar opposite vessel value to the warm clay pot, a clear far-size value flip; a cooler citrus leaf bank separates the canopy too"),

    ("P27 wooden-tub TOPIARY (3-tier)", _row(
        _TUB, _FOL_YEW, dict(trunk=(104, 78, 52)),
        vessel="tub", species="topiary", tiers=3),
     "vessel:tub(shipped staved barrel + iron hoops) species:topiary tiers:3 trunk | a tall 3-tier clipped TOPIARY in the wooden TUB — a NEW vessel for topiary (shipped topiaries are urn 3-tier G3 / bamboo 2-tier G23 / terracotta 1-tier G4): the dark warm-wood staved tub + a deep formal-YEW green read as a heavy dark hedge-yew, not the bright WHITE-urn 3-tier — vessel + palette flip at the same tier count"),

    ("P28 stone-trough FLOWERING (white gardenia)", _row(
        _STONE, _FOL_GARDENIA, dict(accent=(232, 230, 222)),
        vessel="trough", species="flowering", day_chroma=150, vlift=0.10),
     "vessel:trough(shipped cool stone) species:flowering accent:cool near-WHITE gardenia day_chroma:150 (low) vlift:0.10 | a cool white gardenia/jasmine bush in the cool STONE trough — vs the urn plum G5 + terracotta peach G24 (both warm/pink): a near-white bloom at a LOW chroma + a cool grey vessel reads as a different season/colour; vlift keeps the low trough present in the night band"),

    ("P29 terracotta FLOVINE (violet wisteria)", _row(
        _TERRA, _FOL_WISTERIA, dict(accent=(158, 130, 196)),
        vessel="terracotta", species="flovine", day_chroma=160),
     "vessel:terracotta(shipped warm flowerpot) species:flovine accent:cool VIOLET/wisteria day_chroma:160 | a cascading wisteria flovine in the warm TERRACOTTA pot — vs the urn flovine G6 (cool white URN, MAGENTA-pink bloom): a warm vessel + a cooler VIOLET bloom (held muted, not candy) + a warmer leaf bank flip both the vessel AND the bloom hue, reads as a different cascading plant"),

    ("P30 glazed-urn MAPLE", _row(
        _URN, _FOL_EMBER, dict(trunk=(92, 66, 48)),
        vessel="urn", species="maple", day_chroma=178),
     "vessel:urn(shipped blue-white glazed porcelain) species:maple accent via warm foliage roles day_chroma:178 | the autumn fire-canopy maple on the COOL WHITE glazed urn — vs the wooden-tub maple G14 (dark warm staved tub): the slim trunk sits cleanly on the urn neck; the bright cool porcelain base under the warm canopy is a clear value flip vs the dark warm tub, and a cooler/deeper EMBER canopy reads as a later autumn (CHOSEN OPTION A — urn-maple proportions read clean)"),
]

POTS = POOL

# the shipped SIBLING each combo must read distinct FROM, for the composite
# side-by-side check (pool indices into the shipped 25-design registry).
#   P26 glazed-urn kumquat -> shipped terracotta kumquat G9   (idx 8)
#   P27 wooden-tub topiary -> shipped urn 3-tier topiary G3    (idx 2)
#   P28 trough white flowering -> shipped urn plum flowering G5 (idx 4)
#   P29 terracotta violet flovine -> shipped urn magenta flovine G6 (idx 5)
#   P30 glazed-urn maple -> shipped wooden-tub maple G14        (idx 13)
SIBLING = {0: 8, 1: 2, 2: 4, 3: 5, 4: 13}


# ════════════════════════════════════════════════════════════════════════════
# SHEET RENDERER  (mirrors tools/_greenery_round9.py house style)
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
    person (lifted from the round_7 generator)."""
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
    look reference so each NEW combo sits beside the shipped row it must not
    duplicate. Uses the production draw path unmodified."""
    pool = fv.pool("greenery")
    if idx < len(pool):
        draw_greenery(surf, cx, base_y, pool[idx], night, t)


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
    """Render every NEW combo onto a night strip exactly as the composite does,
    then scan the RENDERED pixels for the hottest greenery luma — the honest cap
    audit the footer prints. Accent dots (blooms/fruit) are included. Background
    pixels are skipped so the read is greenery only."""
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
                continue
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
    _text(sheet, "SKYBIT PROMENADE — GREENERY POOL EXPANSION (round 10): batch 4 of 4 — the FINAL FIVE COMBOS of the shipped species (pool indices 25-29) -> 30 designs; NO new drawers/vessels; the shipped 25 UNCHANGED",
          PAD, y, 17, (250, 246, 236), bold=True)
    y += 22
    _text(sheet, "Pure DATA combos — UNUSED vessel x species pairings of the SHIPPED species: "
                 "P26 glazed-URN KUMQUAT (cool white porcelain, warm orange fruit) · P27 wooden-TUB TOPIARY (tiers=3, deep yew) · "
                 "P28 stone-TROUGH FLOWERING (cool near-WHITE gardenia, low chroma, vlift) · P29 TERRACOTTA FLOVINE (cool VIOLET wisteria) · P30 glazed-URN MAPLE (autumn fire-canopy on cool porcelain — chosen option A). "
                 "Drawn by the SHIPPED draw_greenery / vessels unmodified; same night-cap contract (foliage/vessels <=150 via _retint; every fruit/bloom accent <=132 at night via _accent — nothing out-pops the ~230 coin).",
          PAD, y, 9, (188, 186, 200))
    y += title_h - 22

    y = _true_band(sheet, y, "A1.  NEW COMBOS — true far-lane size, adult + coin yardstick (each must read DISTINCT from its shipped sibling by silhouette/colour)  [DAY]",
                   POTS, 0.0)
    y = _true_band(sheet, y, "A2.  NEW COMBOS — [NIGHT]  (cooled <=150; fruit/bloom accents held under the coin)",
                   POTS, 0.95)

    _text(sheet, "B.  PER-COMBO — TRUE far-lane (2 t-phases) + adult ref + in-cell coin · 4x WORKING zoom (nearest) · vessel/species/attrs + why-distinct note  (DAY then NIGHT)",
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

    _text(sheet, "C.  ON-STREET COMPOSITE — each NEW combo at true size placed DIRECTLY BESIDE the shipped sibling it must not duplicate (P26|G9 kumquat · P27|G3 topiary · P28|G5 flowering · P29|G6 flovine · P30|G14 maple) + human cast + a stall + the coin.  (DAY then NIGHT)",
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
        # each NEW combo placed immediately beside its shipped SIBLING so the
        # distinctness (vessel/size/palette) can be read directly; human cast +
        # a stall scattered between for street context + the coin reference.
        draw_greenery(strip, 40, base, POOL[0][1], night, 0.4)     # P26 glazed-urn kumquat
        _shipped_ref(strip, 84, base, night, SIBLING[0], 0.4)      # ref G9 kumquat (terracotta)
        _adult_ref(strip, 128, base, night)
        draw_greenery(strip, 172, base, POOL[1][1], night, 0.6)    # P27 wooden-tub topiary 3-tier
        _shipped_ref(strip, 216, base, night, SIBLING[1], 1.1)     # ref G3 topiary (urn 3-tier)
        _stall_ref(strip, 274, base, night)
        draw_greenery(strip, 330, base, POOL[2][1], night, 0.9)    # P28 trough white flowering
        _shipped_ref(strip, 374, base, night, SIBLING[2], 0.8)     # ref G5 flowering (urn plum)
        _adult_ref(strip, 420, base, night)
        draw_greenery(strip, 466, base, POOL[3][1], night, 0.7)    # P29 terracotta violet flovine
        _shipped_ref(strip, 510, base, night, SIBLING[3], 0.9)     # ref G6 flovine (urn magenta)
        _stall_ref(strip, 568, base, night)
        _adult_ref(strip, 624, base, night)
        draw_greenery(strip, 670, base, POOL[4][1], night, 1.0)    # P30 glazed-urn maple
        _shipped_ref(strip, 714, base, night, SIBLING[4], 0.5)     # ref G14 maple (wooden tub)
        _adult_ref(strip, 766, base, night)
        _gold_coin(strip, sw - 18, 20)
        _text(strip, "coin ref", sw - 46, 32, 8, _shade(bg, 60))
        _text(strip, "NIGHT" if is_night else "DAY", 4, 2, 9,
              (170, 190, 225) if is_night else (60, 50, 40), bold=True)
        _text(strip, "(left of each pair = NEW combo; right = shipped sibling it must read distinct from)", 80, 2, 8,
              (170, 190, 225) if is_night else (60, 50, 40))
        sheet.blit(strip, (PAD, y))
        pygame.draw.rect(sheet, (70, 74, 90), (PAD, y, WIDTH - PAD * 2, strip_h), 1)
        y += strip_h + 6

    hottest, over = _measure_night_cap()
    coin_l = _luma((255, 232, 150))
    msg = (f"NIGHT-STRIP CAP (measured on RENDERED pixels across t-phases, incl. fruit/bloom accents; NEW combos only): "
           f"hottest GREENERY px luma = {hottest:.0f}  ·  px over {NIGHT_GLOW_CAP} = {over}  "
           f"·  gold-coin core luma = {coin_l:.0f} (sole brightest). "
           f"{'PASS — all greenery px <= cap.' if over == 0 else 'FAIL — '+str(over)+' px breach the cap.'}")
    _text(sheet, msg, PAD, total_h - 16, 9,
          (170, 200, 180) if over == 0 else (220, 140, 130))

    out = "/home/user/skybit/docs/sidewalk_overhaul/greenery/round_10.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("saved", out, sheet.get_size())
    print(f"night-strip cap: hottest greenery luma={hottest:.1f}  over-cap px={over}  coin={coin_l:.1f}")


if __name__ == "__main__":
    render()
