"""hero-medallion store card — round 1 review render.

Concept: the whole card IS the gem. One giant glass cabochon disc under a gold
bevel rim, with the item name floated on a frosted glass band clipped to the
disc's lower arc, and the canonical gold price pill below. No rarity ribbon —
the disc's tier glow + colored bezel ring carry the rarity read on their own.

Headless (SDL dummy) → a 3-up RARE/EPIC/LEGENDARY review sheet. Not wired into
the live store; this only writes docs/store_card_v2/hero-medallion/round_1.png.
"""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
import sys
sys.path.insert(0, "/home/user/skybit")
import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from game.store_cards import (
    vgrad, drop_shadow, bevel_rim, top_sheen, contact_shadow, plain_text,
    price_chip, chip_body, facet_gem, cabochon, cabochon_glass, blit_thumb,
    soft_glow, font, m, SS, CABO_LO, CABO_HI, CARD_T, CARD_B,
    CARD_RING_DEEP, CARD_RING_BRIGHT, CREAM, NEAR_BLACK,
)
from game.hud import _font
from game.draw import lerp_color, WHITE

# LOCKED card constants (from store_cards).
CARD_W, CARD_H = 162, 100
CARD_RAD = 17
_INSET = 6

# hero-medallion disc: R=39 logical, centered body-relative at (75, 41) → the
# disc dominates the whole body, spanning roughly y 2..80 of the body rect.
R = 39
DISC_CX = _INSET + 75          # 81 logical from card left
DISC_CY = _INSET + 41          # 47 logical from card top


def render_medallion(sid, pal, price):
    """Draw ONE hero-medallion card onto a fresh SS panel (324×200) and return
    it. Drawn directly at SS with no smoothscale so the review sheet is legible.
    """
    big = pygame.Surface((CARD_W * SS, CARD_H * SS), pygame.SRCALPHA)
    rect = pygame.Rect(m(_INSET), m(_INSET),
                       CARD_W * SS - 2 * m(_INSET), CARD_H * SS - 2 * m(_INSET))
    rad = m(CARD_RAD)
    body_y = m(_INSET)
    cx_ss, cy_ss = m(DISC_CX), m(DISC_CY)

    # 1. depth: soft multi-layer drop shadow (top-left light → offset down).
    drop_shadow(big, rect, rad, blur=m(8), alpha=160, dy=m(4))
    # 2. body gradient (indigo CARD_T → CARD_B).
    big.blit(vgrad(rect.w, rect.h, rad, CARD_T, CARD_B, 252, gamma=1.15),
             rect.topleft)
    # 3. glossy top sheen.
    top_sheen(big, rect, rad, m(30), peak=62)
    # 4. inner tray (neutral gold hairline) so the body edge reads as a frame
    #    even behind the dominant disc.
    tray = rect.inflate(-m(7), -m(7))
    trad = rad - m(4)
    pygame.draw.rect(big, (10, 10, 24, 200), tray.inflate(m(2), m(2)),
                     width=max(1, m(1)), border_radius=trad + m(1))
    pygame.draw.rect(big, (*CARD_RING_BRIGHT, 90), tray, width=max(1, m(1)),
                     border_radius=trad)

    # 5. cabochon aura — a HOTTER tier glow (peak 55 vs the crest layout's 30)
    #    because on hero-medallion the disc IS the rarity read.
    soft_glow(big, cx_ss, cy_ss, m(R + 3), pal["glow"], 55, layers=8)

    # 6. the giant glass cabochon: dome well → skin hero under glass → dome
    #    overlay, then a tier-coloured bezel ring so rarity registers on the
    #    rim itself, not just the aura.
    cabochon(big, cx_ss, cy_ss, m(R), CABO_LO, CABO_HI, ring=pal["gem"],
             ring_a=50)
    blit_thumb(big, sid, cx_ss, cy_ss, m(R) * 1.5)
    cabochon_glass(big, cx_ss, cy_ss, m(R), tint=pal["gem"])
    pygame.draw.circle(big, (*pal["gem"], 80), (cx_ss, cy_ss),
                       m(R) + m(2), width=m(2))

    # 7. frosted name band — a dark glass strip clipped to the disc's lower arc
    #    (BLEND_RGBA_MIN against a disc mask) so the name floats on the gem, not
    #    on the card body.
    band_w, band_h = m(CARD_W - 12), m(14)
    name_band = pygame.Surface((band_w, band_h), pygame.SRCALPHA)
    name_band.fill((10, 10, 24, 180))
    band_left = cx_ss - band_w // 2
    band_top = body_y + m(60) - band_h // 2
    mask = pygame.Surface((band_w, band_h), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255),
                       (cx_ss - band_left, cy_ss - band_top), m(R))
    name_band.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(name_band, (band_left, band_top))
    name = _catalog_name(sid)
    plain_text(big, name, font(13.5), (cx_ss, body_y + m(60)), CREAM,
               shadow_a=160, weight=m(0.8), keyline=(6, 6, 16), kw=m(1.0))

    # 8. price — the canonical GOLD RAMP-A pill (not a frosted recolour). Its
    #    20px body bottom lands at body-relative y≈86, inside the 88px body.
    price_chip(big, cx_ss, body_y + m(76), f"{price:,}", m(20), affordable=True)

    # 9. crest gem — faceted tier badge top-right.
    facet_gem(big, rect.right - m(19), rect.y + m(19), m(11),
              pal["gem"], pal["deep"])

    # 10. bevel rim + dark keyline LAST, on top of the disc edge, so the card
    #     frame always wins the outline against the gem that fills the body.
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 235),
              w=max(1, m(2.0)))
    return big


def _catalog_name(sid):
    try:
        from game import store_catalog
        if store_catalog.exists(sid):
            return store_catalog.name(sid)
    except Exception:
        pass
    return sid.replace("skin_", "").upper()


# ── review sheet ──────────────────────────────────────────────────────────────
VARIANTS = [
    ("RARE", "skin_lorikeet",
     {"gem": (108, 188, 252), "glow": (60, 140, 230), "deep": (18, 44, 90)}, 600),
    ("EPIC", "skin_prism",
     {"gem": (194, 122, 248), "glow": (150, 60, 220), "deep": (44, 10, 80)}, 1400),
    ("LEGENDARY", "skin_kitsune",
     {"gem": (255, 202, 104), "glow": (220, 160, 40), "deep": (90, 50, 0)}, 3500),
]

PANEL_W, PANEL_H = CARD_W * SS, CARD_H * SS   # 324 × 200 (SS panels, no downscale)
MARGIN = 20
GUTTER = 16
HEADER_H = 30
FOOTER_H = 24

sheet_w = MARGIN * 2 + PANEL_W * 3 + GUTTER * 2
sheet_h = MARGIN + HEADER_H + PANEL_H + FOOTER_H + MARGIN
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((24, 26, 40))

hfont = _font(22, True)
ffont = _font(20, True)
htxt = hfont.render("store_card_v2 — hero-medallion — round 1", True,
                    (238, 232, 210))
sheet.blit(htxt, (MARGIN, MARGIN + (HEADER_H - htxt.get_height()) // 2))

panel_y = MARGIN + HEADER_H
for i, (tier, sid, pal, price) in enumerate(VARIANTS):
    px = MARGIN + i * (PANEL_W + GUTTER)
    sheet.blit(render_medallion(sid, pal, price), (px, panel_y))
    ftxt = ffont.render(tier, True, (222, 224, 236))
    sheet.blit(ftxt, (px + (PANEL_W - ftxt.get_width()) // 2,
                      panel_y + PANEL_H + (FOOTER_H - ftxt.get_height()) // 2))

out = "/home/user/skybit/docs/store_card_v2/hero-medallion/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
