"""hero-medallion store card — round 2 review render.

Concept: the whole card IS the gem. One giant glass cabochon disc under a gold
bevel rim, the item name floated on a frosted glass band clipped to the disc's
lower arc, and the canonical gold price chip below. Rarity is carried by the
disc's tier-TINTED body + a prominent tier bezel ring + the faceted crest gem.

Round-2 director fixes over round 1:
  1. the disc body is now TINTED per tier (a tier-glow overlay after the skin)
     so RARE reads blue, EPIC purple, LEGENDARY gold at the same sample point —
     instead of the byte-identical dark indigo dome of round 1.
  2. disc shrunk R 39 -> 34 so it stops clipping flat on the bevel rim and the
     tier aura halo can breathe around it.
  3. the frosted name band is now genuinely translucent (alpha ~130), so the
     gem/skin reads through the glass instead of an opaque white slab.
  4. one price treatment only: the canonical gold price chip (no on-disc price).
  5. exactly one legible name line at font(14).
  6. the tier bezel ring is fatter + doubled with an outer soft tier ring so
     rarity registers on the rim even blue-on-blue.

Headless (SDL dummy) → a 3-up RARE/EPIC/LEGENDARY review sheet + a 1x strip.
Not wired into the live store; writes docs/store_card_v2/hero-medallion/round_2.png.
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
    vgrad, drop_shadow, bevel_rim, top_sheen, plain_text,
    price_chip, cabochon, cabochon_glass, blit_thumb, facet_gem,
    soft_glow, font, m, SS, CABO_LO, CABO_HI, CARD_T, CARD_B,
    CARD_RING_DEEP, CARD_RING_BRIGHT, CREAM,
)
from game.hud import _font

# LOCKED card constants (from store_cards).
CARD_W, CARD_H = 162, 100
CARD_RAD = 17
_INSET = 6

# hero-medallion disc: R=34 logical (was 39) so the circle keeps a visible
# margin off the bevel rim and the tier aura shows around it. Centred body-
# relative at (75, 41) -> disc spans body-y ~7..75.
R = 34
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

    # 5. cabochon aura — a HOTTER tier glow (peak 55) because on hero-medallion
    #    the disc IS the rarity read; with R=34 the halo now breathes outside it.
    soft_glow(big, cx_ss, cy_ss, m(R + 3), pal["glow"], 55, layers=8)

    # 6. the giant glass cabochon: dome well → skin hero under glass → a tier
    #    TINT so the disc body carries rarity colour → dome overlay + glass.
    cabochon(big, cx_ss, cy_ss, m(R), CABO_LO, CABO_HI, ring=pal["gem"],
             ring_a=50)
    blit_thumb(big, sid, cx_ss, cy_ss, m(R) * 1.5)
    # tier tint: a translucent tier-glow wash over the whole dome so the disc
    # body no longer reads byte-identical indigo across tiers. Kept under the
    # glass overlay so the sheen still pops on top of the coloured body.
    tr = m(R)
    tint = pygame.Surface((tr * 2 + 4, tr * 2 + 4), pygame.SRCALPHA)
    tc = tr + 2
    # radial: deeper toward the rim, glow-bright toward the centre — reads as a
    # coloured dome rather than a flat colour cast, and lifts the tier hue.
    for i in range(tr, 0, -1):
        f = i / tr
        from game.draw import lerp_color
        col = lerp_color(pal["glow"], pal["deep"], f ** 1.3)
        a = int(48 + 42 * f)
        pygame.draw.circle(tint, (*col, a), (tc, tc), i)
    tmask = pygame.Surface(tint.get_size(), pygame.SRCALPHA)
    pygame.draw.circle(tmask, (255, 255, 255, 255), (tc, tc), tr - m(1))
    tint.blit(tmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(tint, (cx_ss - tc, cy_ss - tc))

    cabochon_glass(big, cx_ss, cy_ss, m(R), tint=pal["gem"])

    # 6b. tier bezel ring — fatter + doubled so rarity registers on the rim even
    #     when it's blue-on-blue. Drawn on a temp SRCALPHA surface so the alpha
    #     rings blend over the aura instead of punching flat pixels into it.
    rings = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.circle(rings, (*pal["gem"], 120), (cx_ss, cy_ss),
                       m(R) + m(2), width=m(3))
    pygame.draw.circle(rings, (*pal["gem"], 50), (cx_ss, cy_ss),
                       m(R) + m(6), width=m(3))
    big.blit(rings, (0, 0))

    # 7. frosted name band — a TRANSLUCENT dark glass strip clipped to the disc's
    #    lower arc (BLEND_RGBA_MIN vs a disc mask) so the name floats on the gem,
    #    with the tinted disc reading through the frosted glass.
    band_w, band_h = m(CARD_W - 12), m(14)
    name_band = pygame.Surface((band_w, band_h), pygame.SRCALPHA)
    name_band.fill((10, 10, 24, 130))
    band_left = cx_ss - band_w // 2
    band_top = body_y + m(58) - band_h // 2
    mask = pygame.Surface((band_w, band_h), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255),
                       (cx_ss - band_left, cy_ss - band_top), m(R))
    name_band.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(name_band, (band_left, band_top))
    name = _catalog_name(sid)
    plain_text(big, name, font(14), (cx_ss, body_y + m(58)), CREAM,
               shadow_a=170, weight=m(0.9), keyline=(6, 6, 16), kw=m(1.0))

    # 8. price — the canonical GOLD RAMP-A chip (the ONE price treatment).
    price_chip(big, cx_ss, body_y + m(76), f"{price:,}", m(20), affordable=True)

    # 9. crest gem — faceted tier badge top-right (the cleanest tier signal).
    facet_gem(big, rect.right - m(19), rect.y + m(19), m(11),
              pal["gem"], pal["deep"])

    # 10. bevel rim + dark keyline LAST so the card frame always wins the outline
    #     against the gem that fills the body.
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
STRIP_LABEL_H = 20
STRIP_H = CARD_H                              # real-scale 1x cards (162×100)

sheet_w = MARGIN * 2 + PANEL_W * 3 + GUTTER * 2
sheet_h = (MARGIN + HEADER_H + PANEL_H + FOOTER_H + STRIP_LABEL_H + STRIP_H
           + MARGIN)
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((24, 26, 40))

hfont = _font(22, True)
ffont = _font(20, True)
sfont = _font(16, True)
htxt = hfont.render("store_card_v2 — hero-medallion — round 2", True,
                    (238, 232, 210))
sheet.blit(htxt, (MARGIN, MARGIN + (HEADER_H - htxt.get_height()) // 2))

panel_y = MARGIN + HEADER_H
panels = []
for i, (tier, sid, pal, price) in enumerate(VARIANTS):
    px = MARGIN + i * (PANEL_W + GUTTER)
    panel = render_medallion(sid, pal, price)
    panels.append(panel)
    sheet.blit(panel, (px, panel_y))
    ftxt = ffont.render(tier, True, (222, 224, 236))
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

out = "/home/user/skybit/docs/store_card_v2/hero-medallion/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())

# tier-tint sanity: sample the disc body at a fixed offset per tier so the
# per-tier colour shift is measurable, not just visual.
for (tier, sid, pal, price), panel in zip(VARIANTS, panels):
    sx = m(DISC_CX) + m(8)
    sy = m(DISC_CY) + m(8)
    print(f"disc sample {tier:9s}", panel.get_at((sx, sy))[:3])
