"""struck-denomination — store_card_v3 concept, round 1 headless render.

Reads as a MINTED COIN. The hero disc shrinks to R=30 so the medallion no
longer fills the card — instead it opens two clean lanes the coin metaphor
needs: a thin legend lane ABOVE the disc (the skin name struck as a spaced
coin legend) and a denomination lane BELOW (the price set as coin-edge
lettering on a fat arc that hugs the bottom of the rim). The tier read still
comes from the gutter halo, which — because R=30 leaves ~55px gutters — is
given more reach so the tier colour floods further out.

Layout (162×100, body inset 6, SS=2):
  disc R=30 @ CY=44  → top y=14 (8px legend lane above), bottom y=74 (14px
  denomination lane below). Name centered in the legend lane, tracked out for
  a struck feel; price on a 5-to-7-o'clock arc band beyond the bezel ring.

Headless (SDL dummy) → a 3-up RARE/EPIC/LEGENDARY review sheet at SS (324×200,
no downscale) + a real-scale 1x strip (162×100). Not wired into the live store;
writes docs/store_card_v3/struck-denomination/round_1.png.
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

from game.draw import lerp_color
from game.hud import _font
from game.store_cards import (
    vgrad, drop_shadow, bevel_rim, top_sheen, contact_shadow,
    cabochon, cabochon_glass, blit_thumb, facet_gem, plain_text,
    font, m, SS, CABO_LO, CABO_HI, CARD_T, CARD_B,
    CARD_RING_DEEP, CARD_RING_BRIGHT, GEM_R,
)

# LOCKED card constants (from store_cards).
CARD_W, CARD_H = 162, 100
CARD_RAD = 17
_INSET = 6

# The minted disc: R=30 leaves ~55px gutters left/right AND opens the two coin
# lanes (legend above, denomination below) that carry the metaphor.
R = 30
CY = 44                                          # disc centre, logical y


def _disc_tint(surf, cx, cy, r, color, deep, peak=52, base=16):
    """A tier colour veil INSIDE the disc, clipped to the glass. It warms the
    cool CABO_LO→CABO_HI dome away from the indigo body, and — carrying a modest
    centre alpha — pulls any near-white skin highlight toward the tier hue so the
    hero never reads pure (255,255,255). Rim-biased (deeper toward the edge)
    reads as a coloured dome, not a flat cast."""
    pad = 2
    tint = pygame.Surface((r * 2 + pad * 2, r * 2 + pad * 2), pygame.SRCALPHA)
    c = r + pad
    for i in range(r, 0, -1):
        f = i / r                                   # 1 at rim, 0 at centre
        col = lerp_color(color, deep, f ** 1.3)
        a = int(base + (peak - base) * f ** 1.6)    # base at centre, peak at rim
        pygame.draw.circle(tint, (*col, a), (c, c), i, width=2)
    tmask = pygame.Surface(tint.get_size(), pygame.SRCALPHA)
    pygame.draw.circle(tmask, (255, 255, 255, 255), (c, c), r - m(1))
    tint.blit(tmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(tint, (cx - c, cy - c))


def _gutter_aura(surf, cx, cy, disc_r, glow_r, color, peak=90, layers=18):
    """A feathered tier halo that lives ONLY beyond the disc rim (radius >
    disc_r), so it floods the side gutters with tier colour without touching —
    or blowing out — the hero inside the glass. Normal alpha-carry blits (NOT
    additive) so the colour survives compositing and reads as a tint, not a hot
    white bloom. Brightest at the rim, feathering out into the gutter."""
    for i in range(1, layers + 1):
        r = int(disc_r + (glow_r - disc_r) * i / layers)
        if r <= disc_r:
            continue
        a = int(peak * (1 - (i - 1) / layers) ** 1.6)
        if a <= 0:
            continue
        w = max(2, int((glow_r - disc_r) / layers) + m(1.5))
        g = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(g, (*color, a), (r + 1, r + 1), r, width=w)
        surf.blit(g, (cx - r - 1, cy - r - 1))


def _legend_font(name, max_w):
    """Coin-legend sizing: author at 9.5 logical, auto-shrink to 7.5 if the
    tracked word overruns the legend lane. Tracking is baked into the width
    estimate so a wide name doesn't kiss the card edge."""
    tracking = m(1.0)
    for size in (9.5, 7.5):
        f = font(size)
        w = sum(f.size(ch)[0] for ch in name) + tracking * max(0, len(name) - 1)
        if w <= max_w or size == 7.5:
            return f, tracking
    return font(7.5), tracking


def _edge_arc_price(surf, cx, cy, price, pal):
    """Coin-edge lettering: a fat denomination band riding the bottom 60° of the
    rim (5-to-7 o'clock), just OUTSIDE the tier bezel ring, with the price value
    struck at 6-o'clock directly under the disc centre. Two stacked arcs — a
    bright tier lip over a deeper shadow arc — give the band relief so it reads
    as milled metal, not a flat stroke. Angles are in pygame's convention (0 at
    3-o'clock, CCW positive → 270° is the bottom), so the bottom 60° spans
    240°→300° and the value sits at the 270° low point."""
    rr = m(R + 7)                                    # band centre radius
    band = pygame.Rect(0, 0, rr * 2, rr * 2)
    band.center = (cx, cy)
    lo = math.radians(240)
    hi = math.radians(300)
    # deeper shadow arc first (slightly wider) so the bright lip seats over it.
    shadow = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.arc(shadow, (*pal["deep"], 190), band, lo, hi, m(9))
    surf.blit(shadow, (0, 0))
    lip = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.arc(lip, (*pal["glow"], 210), band, lo, hi, m(7))
    surf.blit(lip, (0, 0))
    # value struck at the 6-o'clock low point of the band.
    plain_text(surf, f"{price:,}", font(8), (cx, cy + rr), pal["gem"],
               shadow_a=150, keyline=(4, 4, 14), kw=m(1))


def render_card(name, sid, pal, price):
    """Draw ONE struck-denomination card onto a fresh SS panel (324×200) and
    return it. Drawn directly at SS (no smoothscale) so the review sheet
    inspects the geometry at author resolution."""
    big = pygame.Surface((CARD_W * SS, CARD_H * SS), pygame.SRCALPHA)
    rect = pygame.Rect(m(_INSET), m(_INSET),
                       CARD_W * SS - 2 * m(_INSET), CARD_H * SS - 2 * m(_INSET))
    rad = m(CARD_RAD)
    cx, cy = rect.centerx, m(CY)

    # 1. depth: soft multi-layer drop shadow (top-left light → offset down).
    drop_shadow(big, rect, rad, blur=m(8), alpha=160, dy=m(4))
    # 2. body gradient (indigo CARD_T → CARD_B).
    big.blit(vgrad(rect.w, rect.h, rad, CARD_T, CARD_B, 252, gamma=1.15),
             rect.topleft)
    # 3. glossy top sheen.
    top_sheen(big, rect, rad, m(30), peak=62)
    # 4. bottom-right contact AO.
    contact_shadow(big, rect, rad, m(9), alpha=120)
    # 5. inner tray dark border + faint gold lane so the body edge frames the
    #    coin even with the disc shrunk to R=30.
    tray = rect.inflate(-m(7), -m(7))
    trad = rad - m(4)
    pygame.draw.rect(big, (10, 10, 24, 200), tray.inflate(m(2), m(2)),
                     width=max(1, m(1)), border_radius=trad + m(1))
    pygame.draw.rect(big, (*CARD_RING_BRIGHT, 90), tray, width=max(1, m(1)),
                     border_radius=trad)

    # 6. domed glass well → hero skin.
    cabochon(big, cx, cy, m(R), CABO_LO, CABO_HI, ring=pal["gem"], ring_a=60)
    blit_thumb(big, sid, cx, cy, m(R) * 1.5)

    # 7. tier tint INSIDE the disc.
    _disc_tint(big, cx, cy, m(R), pal["glow"], pal["deep"])

    # 8. glass dome overlay (crescent sheen + gold bezel).
    cabochon_glass(big, cx, cy, m(R), tint=pal["gem"])

    # 9. ONE tier-coloured bezel ring at R+2.
    pygame.draw.circle(big, (*pal["gem"], 110), (cx, cy), m(R) + m(2), width=m(2))

    # 10. the tier read: with only R=30 the gutters are wider, so the halo is
    #     pushed to R+30 to keep flooding tier colour to the body edge.
    _gutter_aura(big, cx, cy, m(R), m(R + 30), pal["glow"], peak=94, layers=20)

    # 11. NAME struck as a coin legend in the lane above the disc — cream, tracked
    #     out for a spaced/minted feel, dark keyline so it bites the body ground.
    lf, trk = _legend_font(name.upper(), rect.w - m(14))
    plain_text(big, name.upper(), lf, (cx, rect.y + m(10)), (246, 240, 216),
               shadow_a=140, tracking=trk, keyline=(4, 4, 14), kw=m(1))

    # 12. PRICE as coin-edge lettering on the 5-to-7-o'clock denomination band.
    _edge_arc_price(big, cx, cy, price, pal)

    # 13. crest gem — faceted tier badge, top-right corner.
    facet_gem(big, rect.right - m(19), rect.y + m(19), m(GEM_R + 3),
              pal["gem"], pal["deep"])

    # 14. bevel rim + dark keyline LAST so the card frame stays crisp over the
    #     halo that bleeds to the body edge.
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 235),
              w=max(1, m(2.0)))
    return big, (cx, cy)


# ── review sheet ──────────────────────────────────────────────────────────────
VARIANTS = [
    ("RARE",      "skin_lorikeet", {"gem": (108, 188, 252), "glow": (60, 140, 230), "deep": (18, 44, 90)},  600,  "Lorikeet"),
    ("EPIC",      "skin_prism",    {"gem": (194, 122, 248), "glow": (140, 40, 230), "deep": (44, 10, 80)}, 1400, "Prism"),
    ("LEGENDARY", "skin_kitsune",  {"gem": (255, 202, 104), "glow": (220, 160, 40), "deep": (90, 50, 0)},  3500, "Kitsune"),
]

PANEL_W, PANEL_H = CARD_W * SS, CARD_H * SS   # 324 × 200 (SS panels, no downscale)
MARGIN = 20
GUTTER = 16
HEADER_H = 30
FOOTER_H = 24
STRIP_LABEL_H = 20
STRIP_H = CARD_H                              # real-scale 1x cards (162×100)

sheet_w = MARGIN * 2 + PANEL_W * 3 + GUTTER * 2
sheet_h = (MARGIN + HEADER_H + PANEL_H + FOOTER_H + STRIP_LABEL_H + STRIP_H
           + MARGIN)
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((16, 17, 30))

hfont = _font(22, True)
ffont = _font(20, True)
sfont = _font(16, True)
htxt = hfont.render("store_card_v3 — struck-denomination — round 1", True,
                    (236, 232, 214))
sheet.blit(htxt, (MARGIN, MARGIN + (HEADER_H - htxt.get_height()) // 2))

panel_y = MARGIN + HEADER_H
panels = []
centers = []
for i, (tier, sid, pal, price, disp) in enumerate(VARIANTS):
    px = MARGIN + i * (PANEL_W + GUTTER)
    panel, ctr = render_card(disp, sid, pal, price)
    panels.append(panel)
    centers.append(ctr)
    sheet.blit(panel, (px, panel_y))
    ftxt = ffont.render(tier, True, (218, 214, 200))
    sheet.blit(ftxt, (px + (PANEL_W - ftxt.get_width()) // 2,
                      panel_y + PANEL_H + (FOOTER_H - ftxt.get_height()) // 2))

# 1x real-scale strip: smoothscale each SS panel down to the live 162×100 card
# so the sheet also shows how the card reads at true size.
strip_label_y = panel_y + PANEL_H + FOOTER_H
ltxt = sfont.render("real scale (1×, 162×100):", True, (200, 204, 220))
sheet.blit(ltxt, (MARGIN, strip_label_y + (STRIP_LABEL_H - ltxt.get_height()) // 2))
strip_y = strip_label_y + STRIP_LABEL_H
for i, panel in enumerate(panels):
    px = MARGIN + i * (PANEL_W + GUTTER)
    small = pygame.transform.smoothscale(panel, (CARD_W, CARD_H))
    sheet.blit(small, (px + (PANEL_W - CARD_W) // 2, strip_y))

out = "/home/user/skybit/docs/store_card_v3/struck-denomination/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())

# lane sanity: the legend lane (above disc) and the denomination band (below)
# must carry ink, and the gutter must be tier-tinted 15px past the disc edge.
for (tier, sid, pal, price, disp), panel, (cx, cy) in zip(VARIANTS, panels, centers):
    gx = cx + m(R) + m(15)
    gutter_px = panel.get_at((min(gx, panel.get_width() - 1), cy))[:3]
    legend_px = panel.get_at((cx, m(_INSET) + m(10)))[:3]
    print(f"{tier:9s} gutter+15px {gutter_px}   legend {legend_px}")
