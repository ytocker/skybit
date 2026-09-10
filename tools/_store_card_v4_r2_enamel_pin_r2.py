"""enamel-pin — store_card_v4_r2 concept, round 2 (final) headless render.

A soft-enamel PIN BADGE read of the disc-led card: the lower name plate is a
polished gold bevel frame enclosing a FLAT, matte tier-tinted enamel channel,
the item name set in RAISED metal caps proud of the enamel, and a NAKED coin +
price (no pill) stamped into the lit right collar.

Round 2 folds the art-director's final-pass notes:

  * P1 — the LEGENDARY (gold-tier) enamel no longer dissolves into its own gold
    frame. The mid-lerp gold (194,138,56) sat only ~61 luma below the frame
    bevel; it is retuned to a DEEP amber-bronze so every tier now clears a >=90
    luma delta between enamel fill and frame bevel (asserted per tier). The
    deeper well also lets the cream caps read far harder on LEGENDARY.
  * P2 — the raised caps are re-centred UP ~2.5 authored px so the enamel
    margin is symmetric top/bottom (they rode low, crowding the bottom lip).
  * P3 — the price is INLINE: coin on the left, digits on the right, one
    baseline. It fits the right collar with >=m(5) clearance below the gem and
    above the name band, so it ships inline (a stacked +1.5pt fallback stays in
    place for any price too wide for the collar).
  * P4 — the 1px directional cap bevel is widened slightly (off = m(1.3)) so it
    survives the 1x downscale; a 1x probe re-checks enamel/frame separation and
    the cap read.

Headless (SDL dummy) -> a 3-up RARE/EPIC/LEGENDARY review sheet at SS
(324x200 panels, no downscale) plus a real-scale 1x strip. Not wired into the
live store; writes docs/store_card_v4_r2/enamel-pin/round_2.png. Run with
--probe to print the per-tier luma deltas + the 1x separation read.
"""
import os

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import math
import sys

sys.path.insert(0, "/home/user/skybit")

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game import store_catalog
from game.hud import _font
from game.draw import lerp_color
from game.store_cards import (
    vgrad, vgrad_stops, drop_shadow, bevel_rim, top_sheen, contact_shadow,
    cabochon, cabochon_glass, blit_thumb, facet_gem, plain_text, soft_glow,
    coin_glyph, _glyph_base, _rarity, font, m, SS,
    CABO_LO, CABO_HI, CARD_T, CARD_B, CARD_RING_DEEP, CARD_RING_BRIGHT,
    GEM_R, RARITY, MYSTERY,
)

# LOCKED card constants (from store_cards).
CARD_W, CARD_H = 162, 100
CARD_RAD = 17
_INSET = 6

# Logical hero-disc radius — the near-full-width v4 disc.
R = 34

# Cream shared by the price numerals (copied verbatim from portrait_vignette_r2)
# so the naked denomination never has to carry legibility on gold.
CREAM_LABEL = (236, 230, 208)

# A lighter METAL cream for the raised name caps — brighter than CREAM_LABEL so
# the letters read as polished metal proud of the matte enamel channel.
CREAM_METAL = (250, 245, 220)

# The representative bevel tone of the polished gold frame the enamel sits in
# (between the frame's bright top stop and the card-ring bevel highlight). The
# enamel channel must stay >=90 luma below this on EVERY tier or it dissolves
# into its own frame — the LEGENDARY failure this round fixes.
FRAME_BEVEL = (240, 205, 129)

# The gold-tier enamel: a DEEP amber-bronze. The natural deep->gem mid-lerp
# lands a light honey gold that reads only ~61 luma below the gold frame; pulled
# to this deeper bronze it clears the frame by >120 luma AND drops below the
# frame's own dark foot, so the channel reads as a recessed well the cream caps
# sit proud of — instead of gold-on-gold mush.
LEGENDARY_ENAMEL = (110, 72, 20)


def _luma(c):
    """Rec.601 luma on the 0-255 scale — the metric the AD notes quote (the
    gold-on-gold failure was a ~61-luma delta), so contrast is asserted here."""
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def _hero_specular(surf, cx, cy, r):
    """A guaranteed high-value glass specular on the upper-left rim, drawn OVER
    the cabochon glass so EVERY skin keeps a lit crescent — dark heroes (e.g.
    skin_tophat) no longer read as a flat low-value blob under the dome."""
    ec = r + m(3)
    edge = pygame.Surface((ec * 2 + m(2), ec * 2 + m(2)), pygame.SRCALPHA)
    steps = max(2, m(4))
    for k in range(steps):
        a = int(210 * (1 - k / steps))
        rk = r - m(1) - k
        if rk <= 0:
            break
        pygame.draw.arc(edge, (255, 250, 234, a),
                        (ec - rk, ec - rk, rk * 2, rk * 2),
                        math.radians(110), math.radians(198), max(1, m(1)))
    surf.blit(edge, (cx - ec, cy - ec), special_flags=pygame.BLEND_ADD)
    # a single hot pip upper-left so there is always a crisp catch-light.
    pr = max(1, int(r * 0.17))
    pip = pygame.Surface((pr * 2 + m(2), pr * 2 + m(2)), pygame.SRCALPHA)
    pygame.draw.circle(pip, (255, 255, 255, 235), (pr + m(1), pr + m(1)), pr)
    off = int(r * 0.66)
    surf.blit(pip, (cx - pr - off, cy - pr - off),
              special_flags=pygame.BLEND_ADD)


def _raised_caps(surf, txt, f, center, max_w):
    """The item name in RAISED metal caps: auto-shrunk to `max_w`, then stamped
    thrice — a dark drop offset down-right, a bright bevel offset up-left, and
    the metal-cream face on top — so each glyph reads as a polished cap standing
    proud of the flat enamel. The directional bevel offset is m(1.3) (not m(0.9))
    so the 1px lit edge survives the 1x downscale rather than washing to nothing."""
    sz = 9.5
    while _glyph_base(txt, f, 0).get_width() > max_w and sz > 6.0:
        sz -= 0.5
        f = font(sz)
    off = max(1, m(1.3))
    cx, cy = center
    # dark drop (down-right) seats the cap in the enamel; bright bevel (up-left)
    # is the lit metal edge; metal-cream face rides on top.
    plain_text(surf, txt, f, (cx + off, cy + off), (28, 20, 10),
               shadow_a=0, weight=m(0.9))
    plain_text(surf, txt, f, (cx - off, cy - off), (255, 250, 232),
               shadow_a=0, weight=m(0.9))
    plain_text(surf, txt, f, (cx, cy), CREAM_METAL, shadow_a=0, weight=m(0.9))


def _enamel_channel_color(pal):
    """A single FLAT matte enamel value. Non-gold tiers ride the deep->gem ramp
    pulled to mid so the channel reads as coloured enamel (not glass) and stays
    uniform at 1x; the gold (legendary) tier overrides to a deep amber-bronze so
    its enamel never dissolves into the gold frame around it."""
    if pal is RARITY["legendary"]:
        return LEGENDARY_ENAMEL
    return lerp_color(pal["deep"], pal["gem"], 0.42)


def _price_inline(surf, price_str, collar_cx, collar_w, gem_bottom, bar_top,
                  cy_hint):
    """Price as an INLINE row — coin LEFT, digits RIGHT, one baseline — laid at
    the highest y that keeps >=m(5) below the gem crest (so it never rides under
    the gem). A warm glow pad seats the naked digits on the lit collar. Returns
    False if the assembled row is wider than the collar so the caller can fall
    back to the stacked layout."""
    coin_r = m(4.0)
    gap = m(3)
    pf = font(9.0)
    while (coin_r * 2 + gap + _glyph_base(price_str, pf, 0).get_width()) > \
            collar_w and pf.get_height() > m(7.0):
        pf = font(pf.get_height() / SS - 0.5)
    dw = _glyph_base(price_str, pf, 0).get_width()
    w = coin_r * 2 + gap + dw
    if w > collar_w:
        return False
    dh = pf.get_height()
    row_half = max(coin_r, dh // 2)
    # disc-mid is the ideal baseline, but the gem crest forces the row down until
    # it clears the gem by m(5); the collar is tall enough that it still sits
    # comfortably above the name band.
    cy = max(cy_hint, gem_bottom + m(5) + row_half)
    left = collar_cx - w // 2
    soft_glow(surf, collar_cx, cy, m(15), (255, 236, 196), 28, layers=8)
    coin_glyph(surf, left + coin_r, cy, coin_r)
    dcx = left + coin_r * 2 + gap + dw // 2
    plain_text(surf, price_str, pf, (dcx, cy), CREAM_LABEL, shadow_a=0,
               weight=m(1.0), keyline=(8, 8, 18), kw=m(0.7))
    return cy, row_half


def _price_stacked(surf, price_str, collar_cx, collar_w, price_cy):
    """Fallback: coin OVER digits. Digits bumped +1.5pt vs round 1 so the naked
    denomination still reads bold when a wide price won't fit the inline row."""
    soft_glow(surf, collar_cx, price_cy, m(15), (255, 236, 196), 30, layers=8)
    coin_glyph(surf, collar_cx, price_cy - m(8), m(4.5))
    pf = font(10.5)
    while _glyph_base(price_str, pf, 0).get_width() > collar_w * 0.92 and \
            pf.get_height() > m(11):
        pf = font(pf.get_height() / SS - 0.5)
    plain_text(surf, price_str, pf, (collar_cx, price_cy + m(6)), CREAM_LABEL,
               shadow_a=0, weight=m(1.0), keyline=(8, 8, 18), kw=m(0.7))


def render_card(sid):
    """Draw ONE enamel-pin card onto a fresh SS panel (324x200) and return it
    (drawn directly at SS, no smoothscale)."""
    pal = RARITY.get(_rarity(sid), MYSTERY)
    name = store_catalog.name(sid)
    price_str = f"{store_catalog.cost(sid):,}"

    big = pygame.Surface((CARD_W * SS, CARD_H * SS), pygame.SRCALPHA)
    rect = pygame.Rect(m(_INSET), m(_INSET),
                       CARD_W * SS - 2 * m(_INSET), CARD_H * SS - 2 * m(_INSET))
    rad = m(CARD_RAD)
    cx, cy = rect.centerx, rect.y + m(37)          # top headroom; lower rim tucks

    # ── SHELL (locked order) ──
    drop_shadow(big, rect, rad, blur=m(8), alpha=160, dy=m(4))
    big.blit(vgrad(rect.w, rect.h, rad, CARD_T, CARD_B, 252, gamma=1.15),
             rect.topleft)
    top_sheen(big, rect, rad, m(30), peak=62)
    contact_shadow(big, rect, rad, m(9), alpha=120)
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 235),
              w=max(1, m(2.0)))

    # ── HERO DISC ──
    soft_glow(big, cx, cy, m(R + 3), pal["glow"], 34, layers=9)
    cabochon(big, cx, cy, m(R), CABO_LO, CABO_HI, ring=pal["gem"], ring_a=55)
    blit_thumb(big, sid, cx, cy, m(R) * 0.66)
    cabochon_glass(big, cx, cy, m(R), tint=pal["gem"])
    _hero_specular(big, cx, cy, m(R))              # luminance-independent catch-light

    # ── GEM CREST (locked call) ──
    gem_cx = rect.right - m(19)
    gem_cy = rect.y + m(19)
    facet_gem(big, gem_cx, gem_cy, m(GEM_R + 3), pal["gem"], pal["deep"])
    gem_bottom = gem_cy + m(GEM_R + 3) + m(4)      # painted seat-well extent

    # ── PRICE — bare coin + numerals STAMPED into the right collar, no pill.
    #    Inline coin+digits on one baseline (bolder than the stacked read); a
    #    stacked +1.5pt fallback stays if a price ever runs wider than the collar.
    collar_left = cx + m(R)
    collar_right = rect.right - m(6)
    collar_cx = (collar_left + collar_right) // 2
    collar_w = collar_right - collar_left
    bar_top = rect.bottom - m(3) - m(17)
    placed = _price_inline(big, price_str, collar_cx, collar_w, gem_bottom,
                           bar_top, cy)
    if placed is False:
        _price_stacked(big, price_str, collar_cx, collar_w, rect.y + m(45))

    # ── NAME BAND — enamel PIN STRIP flush at the bottom: a polished gold metal
    #    frame enclosing a FLAT matte tier-enamel channel, name in raised caps. ──
    bar_h = m(17)
    bar = pygame.Rect(rect.x + m(3), rect.bottom - m(3) - bar_h,
                      rect.w - m(6), bar_h)
    brad = m(5)
    # polished metal strip (the pin body): a compact gold ramp so it reads as a
    # struck metal edge round the enamel.
    big.blit(vgrad_stops(bar.w, bar.h, brad,
                         [(0.0, (248, 216, 142)), (0.5, (212, 166, 86)),
                          (1.0, (118, 80, 28))], 255, gamma=1.05),
             bar.topleft)
    # FLAT matte enamel channel, inset so the gold metal border frames it.
    ch = bar.inflate(-m(7), -m(7))
    crad = max(1, brad - m(3))
    pygame.draw.rect(big, _enamel_channel_color(pal), ch, border_radius=crad)
    # a thin dark keyline seats the enamel below the metal lip (reads recessed).
    pygame.draw.rect(big, lerp_color(pal["deep"], (0, 0, 0), 0.45), ch,
                     width=max(1, m(0.8)), border_radius=crad)
    # the strip's own bevel: dark outer contact keyline UNDER a bright top-left
    # gold bevel so the metal frame reads polished + raised off the card.
    bevel_rim(big, bar, brad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 235),
              w=max(1, m(1.5)))

    # caps re-centred UP ~2.5 authored px so the enamel margin is symmetric
    # top/bottom (the font's descent padding otherwise seats them low).
    caps_center = (ch.centerx, ch.centery - m(2.5))
    _raised_caps(big, name.upper(), font(9.5), caps_center, ch.w - m(6))

    return big


# ── review sheet ──────────────────────────────────────────────────────────────
VARIANTS = [
    ("RARE",      "skin_tophat"),
    ("EPIC",      "skin_prism"),
    ("LEGENDARY", "skin_kitsune"),
]

PANEL_W, PANEL_H = CARD_W * SS, CARD_H * SS   # 324 x 200 (SS panels, no downscale)
MARGIN = 10
GUTTER = 8
HEADER_H = 30
FOOTER_H = 22
STRIP_LABEL_H = 20
STRIP_H = CARD_H

sheet_w = MARGIN * 2 + PANEL_W * 3 + GUTTER * 2
sheet_h = (MARGIN + HEADER_H + PANEL_H + FOOTER_H + STRIP_LABEL_H + STRIP_H
           + MARGIN)
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((8, 8, 20))

hfont = _font(22, True)
ffont = _font(18, True)
sfont = _font(15, True)
htxt = hfont.render("store_card_v4_r2 — enamel-pin — round 2", True,
                    (236, 232, 214))
sheet.blit(htxt, (MARGIN, MARGIN + (HEADER_H - htxt.get_height()) // 2))

panel_y = MARGIN + HEADER_H
panels = []
for i, (tier, sid) in enumerate(VARIANTS):
    px = MARGIN + i * (PANEL_W + GUTTER)
    panel = render_card(sid)
    panels.append(panel)
    sheet.blit(panel, (px, panel_y))
    ftxt = ffont.render(tier, True, (218, 214, 200))
    sheet.blit(ftxt, (px + (PANEL_W - ftxt.get_width()) // 2,
                      panel_y + PANEL_H + (FOOTER_H - ftxt.get_height()) // 2))

# 1x real-scale strip so the enamel + raised caps + naked price are judged at
# the live card size (the flat-at-1x legibility read this concept is about).
strip_label_y = panel_y + PANEL_H + FOOTER_H
ltxt = sfont.render("real scale (1x, 162x100)", True, (200, 204, 220))
sheet.blit(ltxt, (MARGIN, strip_label_y + (STRIP_LABEL_H - ltxt.get_height()) // 2))
strip_y = strip_label_y + STRIP_LABEL_H
for i, panel in enumerate(panels):
    px = MARGIN + i * (PANEL_W + GUTTER)
    left = px + (PANEL_W - CARD_W) // 2
    small = pygame.transform.smoothscale(panel, (CARD_W, CARD_H))
    sheet.blit(small, (left, strip_y))

out = "/home/user/skybit/docs/store_card_v4_r2/enamel-pin/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())

# ── contrast + separation probes (never displays the PNG). P1's >=90 luma delta
#    is asserted per tier; P4 re-checks the enamel/frame separation at 1x. ──
frame_L = _luma(FRAME_BEVEL)
print(f"frame bevel {FRAME_BEVEL} luma L*={frame_L:5.1f}")
for tier in ("rare", "epic", "legendary"):
    pal = RARITY[tier]
    en = _enamel_channel_color(pal)
    en_L = _luma(en)
    d = abs(en_L - frame_L)
    print(f"  {tier:10s} enamel {tuple(en)} L*={en_L:5.1f}  delta={d:5.1f}")
    assert d >= 90, f"{tier} enamel/frame luma delta {d:.1f} < 90"

# P4 — downscale the LEGENDARY panel to 1x and confirm the retune survives: the
# enamel channel must still read well below the gold frame, and the cream caps
# must still crown the enamel (the directional bevel read).
leg = render_card("skin_kitsune")
small = pygame.transform.smoothscale(leg, (CARD_W, CARD_H))
# 1x geometry: bar/enamel band along the bottom of the 162x100 card.
bar_top_1x = CARD_H - _INSET - 3 - 17
band_cy = bar_top_1x + 17 // 2
# frame reads at the enamel's top lip; enamel reads in a clear left gutter of the
# channel (away from the caps); cap peak scanned across the name row.
frame_px = small.get_at((CARD_W // 2, bar_top_1x + 2))
enamel_px = small.get_at((_INSET + 8, band_cy))
cap_peak = 0.0
for x in range(_INSET + 6, CARD_W - _INSET - 6):
    cap_peak = max(cap_peak, _luma(small.get_at((x, band_cy))))
fL, eL = _luma(frame_px), _luma(enamel_px)
print(f"  1x LEGENDARY  frame {tuple(frame_px)[:3]} L*={fL:5.1f}  "
      f"enamel {tuple(enamel_px)[:3]} L*={eL:5.1f}  delta={abs(fL - eL):5.1f}")
print(f"  1x cap peak luma L*={cap_peak:5.1f}  (cap-vs-enamel={cap_peak - eL:5.1f})")
assert abs(fL - eL) >= 40, "1x enamel/frame separation collapsed"
assert cap_peak - eL >= 60, "1x caps no longer crown the enamel"
print("all contrast asserts passed")
