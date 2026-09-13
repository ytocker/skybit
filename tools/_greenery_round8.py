"""Promenade PLANTS & GREENERY — round 8 candidate-sheet generator.

GREENERY POOL EXPANSION, batch 3 of 4 — FIVE fresh COMBOS of the EXISTING
shipped species (NO new species drawers, NO new vessels). Batches 1-2 grew the
pool from 10 to 20 with TEN new species (peony/chrysanthemum/plum/maple/
narcissus + lotus/fern/cycad/banana/rock, pool indices 10-19, both integrated
SHIP-READY). This batch + batch 4 add TEN fresh COMBOS — new vessel pairings,
palettes, sizes, tier-counts + seasonal accents of the shipped 19 species — so
NO `_sp_*` drawer is authored here; each combo is a pure DATA Variant row over
the SHIPPED drawers + shipped vessels. This is batch 3: FIVE combos, pool
indices 20-24. The existing 20 are UNCHANGED.

THE 5 COMBOS (each visibly distinct from all 20 shipped AND each other —
different vessel x species x palette x size; all accents via the species'
existing _accent path so they stay <=132 at night and never out-pop the coin):

  P21 wooden-tub LUSH SHRUB    — a big fuller bush (mass 1.2) in the staved
                                 wooden TUB. The shipped shrub (idx0) is a 1.0
                                 mass in terracotta with a pink bloom; tub +
                                 bigger mass + a fresh deep-leafy palette (no
                                 bloom) reads as a fuller, plainer hedge-bush —
                                 a different vessel, size AND palette.
  P22 terracotta DWARF PINE    — a small potted dwarf conifer cone in a warm
                                 TERRACOTTA pot. The shipped conifer (idx1) sits
                                 low + wide in a cool stone trough; lifting it
                                 into a tall terracotta pot + a slightly cooler
                                 blue-green needle bank reads as a potted dwarf
                                 pine, not a trough hedge — new vessel + palette.
  P23 bamboo-planter TOPIARY   — clipped topiary BALLS (tiers=2) in the green
                                 BAMBOO planter. The shipped topiaries are urn
                                 tiers=3 (idx2) + terracotta tiers=1 (idx3); a
                                 2-tier in the bamboo planter is a new tier-count
                                 + a new vessel + a brighter clipped-box palette.
  P24 terracotta PEACH AZALEA  — a warm PEACH / azalea-pink flowering shrub in
                                 TERRACOTTA. The shipped flowering (idx4) is a
                                 muted plum in a glazed urn; a fresh warm-peach
                                 accent + a higher day_chroma in terracotta reads
                                 as a different SEASON + colour + vessel.
  P25 stone-trough KUMQUAT     — a citrus fruiting-tree in the cool stone
                                 TROUGH, carrying a cooler, slightly less orange
                                 fruit over a darker denser canopy. The shipped
                                 kumquat (idx8) is a warm-orange tree in
                                 terracotta; trough + a cooler tangerine fruit +
                                 the dark foliage bank reads new.

This generator IMPORTS the shipped helpers + the SHIPPED draw_greenery from
game.greenery_cast (so the explorations are drawn by the EXACT production code
path / night-cap contract — these combos reuse shipped drawers + vessels, so no
patching of dispatch is needed). It only defines 5 new Variant rows over the
shipped palette banks (+ a few fresh foliage / accent banks for distinctness)
and renders the standard sheet. Nothing here mutates production game files — the
orchestrator renders + commits.

Sheet layout MIRRORS round 7: true far-lane DAY + NIGHT bands with an adult +
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
# the exact same code / night-cap contract as the shipped 20. These rows reuse
# shipped drawers + vessels only, so draw_greenery is used UNMODIFIED.
from game import greenery_cast as gc  # noqa: E402
from game.greenery_cast import (  # noqa: E402
    _retint, _accent, _hi, _mix, _shade, _luma, draw_greenery,
    VESSEL_H, NIGHT_GLOW_CAP,
)
from game import foreground_variants as fv  # noqa: E402


# ════════════════════════════════════════════════════════════════════════════
# THE 5 NEW ROWS — foreground_variants.Variant data (pool indices 20-24).
# Reuse the shipped palette banks (_TERRA/_TUB/_BAMBOO_V/_STONE) + a few fresh
# foliage/accent banks so each combo reads DISTINCT from its shipped sibling.
# Pure DATA — no new drawers, no new vessels.
# ════════════════════════════════════════════════════════════════════════════

_TERRA = dict(gc._TERRA)
_TUB = dict(gc._TUB)
_BAMBOO_V = dict(gc._BAMBOO_V)
_STONE = dict(gc._STONE)

# fresh foliage banks (distinct from the shipped _FOL_LEAFY/_FOL_DARK/_FOL_CLIP):
# a deep LUSH bush green (richer + a touch bluer than _FOL_LEAFY) for the big
# tub shrub, so the fuller bush reads as its own deeper green not the shipped one
_FOL_LUSH = dict(foliage_dark=(28, 74, 46), foliage_mid=(48, 108, 66), foliage_top=(96, 152, 92))
# a cool blue-green DWARF-PINE needle bank — cooler than the shipped conifer's
# _FOL_DARK so the potted pine reads as a frostier alpine dwarf
_FOL_PINE = dict(foliage_dark=(30, 70, 58), foliage_mid=(46, 96, 78), foliage_top=(82, 134, 104))
# a brighter clipped-box green for the bamboo-planter topiary (a value above the
# shipped _FOL_CLIP so the 2-tier reads fresh + crisp beside the urn topiary)
_FOL_BOX = dict(foliage_dark=(48, 92, 56), foliage_mid=(80, 130, 82), foliage_top=(128, 172, 116))
# a soft mid grass-green for the peach azalea (leaf is a backdrop to the warm
# bloom; distinct from the urn flowering's dark bank)
_FOL_AZALEA = dict(foliage_dark=(40, 82, 52), foliage_mid=(64, 116, 74), foliage_top=(106, 156, 98))
# the shipped _FOL_DARK reused for the trough kumquat (the dark dense canopy that
# makes the cooler tangerine fruit pop) — same bank the shipped kumquat uses, but
# the COOLER fruit accent + the STONE trough vessel make the combo distinct.
_FOL_DARK = dict(gc._FOL_DARK)


def _row(*banks, **attrs):
    pal = {}
    for b in banks:
        pal.update(b)
    return fv.Variant(palette=pal, attrs=dict(attrs))


POOL = [
    ("P21 wooden-tub LUSH SHRUB", _row(
        _TUB, _FOL_LUSH,
        vessel="tub", species="shrub", mass=1.2),
     "vessel:tub(shipped staved barrel + iron hoops) species:shrub mass:1.2 (vs shipped 1.0) | a BIG fuller hedge-bush, no bloom, in a deep LUSH green — vs the shipped shrub G1 (terracotta, mass 1.0, pink bloom): bigger + plainer + a different vessel AND a deeper greener palette"),

    ("P22 terracotta DWARF PINE", _row(
        _TERRA, _FOL_PINE,
        vessel="terracotta", species="conifer"),
     "vessel:terracotta(shipped warm flowerpot) species:conifer | a small POTTED dwarf pine cone, cool blue-green needles — vs the shipped conifer G2 (low/wide in a cool STONE TROUGH): lifted into a tall warm terracotta pot + a frostier needle bank, reads as a potted alpine dwarf not a trough hedge"),

    ("P23 bamboo-planter TOPIARY (2-tier)", _row(
        _BAMBOO_V, _FOL_BOX, dict(trunk=(120, 92, 60)),
        vessel="bamboo", species="topiary", tiers=2),
     "vessel:bamboo(shipped green cane planter) species:topiary tiers:2 trunk | clipped box BALLS, 2 tiers (a NEW count — shipped topiaries are urn tiers=3 G3 + terracotta tiers=1 G4) in the bamboo planter (shipped only carries the bamboo SPECIES G7), brighter clipped-box green — new tier-count + vessel + palette"),

    ("P24 terracotta PEACH AZALEA", _row(
        _TERRA, _FOL_AZALEA, dict(accent=(238, 158, 120)),
        vessel="terracotta", species="flowering", day_chroma=186),
     "vessel:terracotta(shipped warm flowerpot) species:flowering accent:warm PEACH/azalea-pink day_chroma:186 | a sunny spring azalea — vs the shipped flowering G5 (muted PLUM in a glazed URN, dc170): a fresh warm-peach accent + higher chroma + a warm terracotta vessel reads as a different SEASON + colour"),

    ("P25 stone-trough KUMQUAT (tangerine)", _row(
        _STONE, _FOL_DARK, dict(accent=(232, 122, 48), trunk=(112, 84, 54), vlift=0.10),
        vessel="trough", species="kumquat"),
     "vessel:trough(shipped cool stone, vlift for night) species:kumquat accent:cooler TANGERINE fruit trunk | a citrus fruiting-tree in the cool STONE trough — vs the shipped kumquat G9 (warm orange in TERRACOTTA): a cooler/redder tangerine fruit over the dark dense _FOL_DARK canopy in a stone trough reads new"),
]

POTS = POOL

# the shipped SIBLING each combo must read distinct FROM, for the composite
# side-by-side check (pool indices into the shipped 20-design registry).
SIBLING = {0: 0, 1: 1, 2: 2, 3: 4, 4: 8}  # P21->shrub G1, P22->conifer G2, P23->topiary G3, P24->flowering G5, P25->kumquat G9


# ════════════════════════════════════════════════════════════════════════════
# SHEET RENDERER  (mirrors tools/_greenery_round7.py house style)
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
    _text(sheet, "SKYBIT PROMENADE — GREENERY POOL EXPANSION (round 8): batch 3 of 4 — FIVE fresh COMBOS of the shipped species (pool indices 20-24); NO new drawers/vessels; the shipped 20 UNCHANGED",
          PAD, y, 17, (250, 246, 236), bold=True)
    y += 22
    _text(sheet, "Pure DATA combos — new vessel x species x palette x size pairings of the SHIPPED 19 species: "
                 "P21 wooden-TUB lush SHRUB (mass 1.2, deep leafy, no bloom) · P22 TERRACOTTA dwarf PINE (potted conifer, cool needles) · "
                 "P23 BAMBOO-planter TOPIARY (tiers=2, a NEW count) · P24 TERRACOTTA peach AZALEA (warm flowering) · P25 stone-TROUGH KUMQUAT (cooler tangerine fruit). "
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

    _text(sheet, "C.  ON-STREET COMPOSITE — each NEW combo at true size placed DIRECTLY BESIDE the shipped sibling it must not duplicate (P21|G1 shrub · P22|G2 conifer · P23|G3 topiary · P24|G5 flowering · P25|G9 kumquat) + human cast + a stall + the coin.  (DAY then NIGHT)",
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
        draw_greenery(strip, 40, base, POOL[0][1], night, 0.4)     # P21 tub lush shrub
        _shipped_ref(strip, 84, base, night, SIBLING[0], 0.4)      # ref G1 shrub (terracotta)
        _adult_ref(strip, 128, base, night)
        draw_greenery(strip, 172, base, POOL[1][1], night, 0.6)    # P22 terracotta dwarf pine
        _shipped_ref(strip, 216, base, night, SIBLING[1], 0.5)     # ref G2 conifer (trough)
        _stall_ref(strip, 274, base, night)
        draw_greenery(strip, 330, base, POOL[2][1], night, 0.9)    # P23 bamboo topiary 2-tier
        _shipped_ref(strip, 374, base, night, SIBLING[2], 1.1)     # ref G3 topiary (urn 3-tier)
        _adult_ref(strip, 420, base, night)
        draw_greenery(strip, 466, base, POOL[3][1], night, 0.7)    # P24 terracotta peach azalea
        _shipped_ref(strip, 510, base, night, SIBLING[3], 0.8)     # ref G5 flowering (urn plum)
        _stall_ref(strip, 568, base, night)
        _adult_ref(strip, 624, base, night)
        draw_greenery(strip, 670, base, POOL[4][1], night, 1.0)    # P25 trough kumquat
        _shipped_ref(strip, 714, base, night, SIBLING[4], 0.9)     # ref G9 kumquat (terracotta)
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

    out = "/home/user/skybit/docs/sidewalk_overhaul/greenery/round_8.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("saved", out, sheet.get_size())
    print(f"night-strip cap: hottest greenery luma={hottest:.1f}  over-cap px={over}  coin={coin_l:.1f}")


if __name__ == "__main__":
    render()
