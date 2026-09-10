"""poster-backdrop — store_card_v3_tl concept, round 1 headless render.

A cinematic "environmental poster" card: a fully procedural tier-themed
backdrop bleeds to every card edge — a vertical sky gradient in the tier
palette with 2–3 silhouetted sandstone pillars staggered at depth and tinted
toward the tier hue. A crisp hero medallion (cabochon + skin) floats centred
over the sky; the gem crest sits top-LEFT, the price rides a small frosted chip
top-RIGHT so it stays legible over the gradient, and the item name lands on a
full-width bottom poster-title band with a tier-gradient fill. Disc tint + gem
crest carry rarity. Zero raster upscaling — every pixel is drawn from code.

Headless (SDL dummy) → a 3-up RARE/EPIC/LEGENDARY review sheet at SS
(324×200, no downscale) + a real-scale 1x strip (162×100). Not wired into the
live store; writes docs/store_card_v3_tl/poster-backdrop/round_1.png.
"""
import os

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import sys

sys.path.insert(0, "/home/user/skybit")

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game.draw import lerp_color
from game.hud import _font
from game.store_cards import (
    vgrad, bevel_rim, top_sheen, contact_shadow,
    cabochon, cabochon_glass, blit_thumb, facet_gem, plain_text,
    font, m, SS, CABO_LO, CABO_HI,
    CARD_RING_DEEP, CARD_RING_BRIGHT, GEM_R,
)

# LOCKED card constants (from store_cards).
CARD_W, CARD_H = 162, 100
CARD_RAD = 17
_INSET = 6
R = 26          # hero medallion radius — smaller than arc-veil-pill so the sky
                # and pillar silhouettes read as a full environment behind it.


def _disc_tint(surf, cx, cy, r, color, deep, peak=92, base=78):
    """A tier colour veil INSIDE the disc, clipped to the glass. It warms the
    cool CABO_LO→CABO_HI dome away from the sky ground, and — carrying a
    meaningful centre alpha — pulls the LEGENDARY hero's near-white specular
    toward the tier hue so it stops blowing out. The gentler exponent lets the
    hue carry further inward instead of collapsing to nothing at the centre; the
    veil stays rim-biased because peak > base."""
    pad = 2
    tint = pygame.Surface((r * 2 + pad * 2, r * 2 + pad * 2), pygame.SRCALPHA)
    c = r + pad
    for i in range(r, 0, -1):
        f = i / r                                   # 1 at rim, 0 at centre
        col = lerp_color(color, deep, f ** 1.3)
        a = int(base + (peak - base) * f ** 1.3)    # base at centre, peak at rim
        pygame.draw.circle(tint, (*col, a), (c, c), i, width=2)
    tmask = pygame.Surface(tint.get_size(), pygame.SRCALPHA)
    pygame.draw.circle(tmask, (255, 255, 255, 255), (c, c), r - m(1))
    tint.blit(tmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(tint, (cx - c, cy - c))


def _gutter_aura(surf, cx, cy, disc_r, glow_r, color, peak=90, layers=18):
    """A feathered tier halo that lives ONLY beyond the disc rim (radius >
    disc_r), so it floods the surrounding sky with tier colour without touching —
    or blowing out — the hero inside the glass. Normal alpha-carry blits (NOT
    additive) so the colour survives compositing and reads as a tint, not a hot
    white bloom. Brightest at the rim, feathering out into the sky."""
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


def _pillar(surf, clip_rect, x, top_y, w, h, color, alpha):
    """A simple silhouetted sandstone pillar: a tier-tinted vertical slab with a
    slightly lighter cap, alpha-staggered so far pillars sit deeper in the haze.
    Clipped to the card body so a pillar that overruns the bottom never spills
    onto the bevel."""
    psurf = pygame.Surface((w, h), pygame.SRCALPHA)
    psurf.fill((*color, alpha))
    cap_h = max(m(2), h // 8)
    cap_col = tuple(min(255, c + 30) for c in color)
    pygame.draw.rect(psurf, (*cap_col, alpha), (0, 0, w, cap_h))
    prev = surf.get_clip()
    surf.set_clip(clip_rect)
    surf.blit(psurf, (x - w // 2, top_y))
    surf.set_clip(prev)


def render_card(sid, pal, price, name):
    """Draw ONE poster-backdrop card onto a fresh SS panel (324×200) and return
    it. Drawn directly at SS (no smoothscale) so the review sheet inspects the
    geometry at author resolution."""
    big = pygame.Surface((CARD_W * SS, CARD_H * SS), pygame.SRCALPHA)
    rect = pygame.Rect(m(_INSET), m(_INSET),
                       CARD_W * SS - 2 * m(_INSET), CARD_H * SS - 2 * m(_INSET))
    rad = m(CARD_RAD)
    cx, cy = rect.centerx, rect.y + m(38)

    # 1. SKY BACKDROP — the tier-themed vertical gradient that bleeds edge to
    #    edge. Dark sky at the top, warmer toward the horizon so the pillars and
    #    hero read as a lit-from-below environment.
    sky_top = lerp_color(pal["deep"], (6, 8, 24), 0.3)
    sky_bot = lerp_color(pal["glow"], (12, 14, 40), 0.6)
    big.blit(vgrad(rect.w, rect.h, rad, sky_top, sky_bot, 252, gamma=1.2),
             rect.topleft)

    # 2. PILLAR SILHOUETTES — warm sandstone tinted to the tier, staggered at
    #    depth (scale + alpha) so the backdrop has parallax. Far pillars are
    #    fainter; near ones taller and more opaque.
    pillar_col = lerp_color(pal["deep"], (50, 45, 35), 0.4)
    _pillar(big, rect, rect.x + m(20), rect.y + m(18), m(12), m(60), pillar_col, 60)
    _pillar(big, rect, rect.right - m(22), rect.y + m(10), m(14), m(72), pillar_col, 50)
    _pillar(big, rect, rect.x + m(50), rect.y + m(28), m(9), m(48), pillar_col, 40)

    # 3. glossy top sheen, toned down so it lifts the sky without hiding it.
    top_sheen(big, rect, rad, m(20), peak=35)
    # 4. bottom-right contact AO so the card seats on its ground.
    contact_shadow(big, rect, rad, m(8), alpha=100)

    # 5. AMBIENT GLOW behind the medallion so the hero reads as the lit focal
    #    point of the poster, not a sticker dropped on the sky.
    glow_surf = pygame.Surface((m(R * 3), m(R * 3)), pygame.SRCALPHA)
    gc = m(R * 3) // 2
    for gi in range(12, 0, -1):
        gr = int(m(R) * gi / 8)
        ga = int(18 * (12 - gi) / 12)
        pygame.draw.circle(glow_surf, (*pal["glow"], ga), (gc, gc), gr)
    big.blit(glow_surf, (cx - gc, cy - gc))

    # 6. HERO MEDALLION — domed glass well → skin → tier tint → glass dome →
    #    tier bezel ring. Same medallion DNA as the other v3 concepts.
    cabochon(big, cx, cy, m(R), CABO_LO, CABO_HI, ring=pal["gem"], ring_a=80)
    if sid is not None:
        blit_thumb(big, sid, cx, cy, m(R) * 1.5)
    _disc_tint(big, cx, cy, m(R), pal["glow"], pal["deep"], peak=58, base=24)
    cabochon_glass(big, cx, cy, m(R), tint=pal["gem"])
    pygame.draw.circle(big, (*pal["gem"], 110), (cx, cy), m(R) + m(2), width=m(2))

    # 7. gutter halo → floods the sky around the disc with the tier hue so the
    #    rarity read carries beyond the bezel.
    _gutter_aura(big, cx, cy, m(R), m(R + 24), pal["glow"], peak=80, layers=16)

    # 8. BOTTOM POSTER-TITLE BAND — a full-width tier-gradient strip (deep→glow)
    #    with a thin gold keyline, carrying the item name across the base.
    band_h = m(20)
    band_rect = pygame.Rect(rect.x, rect.bottom - band_h, rect.w, band_h)
    band = pygame.Surface((band_rect.w, band_rect.h), pygame.SRCALPHA)
    for bx in range(band_rect.w):
        t = bx / max(1, band_rect.w - 1)
        bc = lerp_color(pal["deep"], pal["glow"], t)
        pygame.draw.line(band, (*bc, 210), (bx, 0), (bx, band_h))
    pygame.draw.line(band, (*CARD_RING_BRIGHT, 160), (0, 0),
                     (band_rect.w, 0), max(1, m(1)))
    big.blit(band, band_rect.topleft)
    plain_text(big, name, font(9.0), band_rect.center, (236, 230, 208),
               shadow_a=160, weight=m(0.7))

    # 9. PRICE FROSTED CHIP (top-right) — a small dark-glass pill so the price
    #    stays legible over the bright sky. Center per the locked spine.
    ph = m(14)
    price_str = f"{price:,}"
    pf = font(8.0)
    ptw = pf.render(price_str, True, (255, 255, 255)).get_width()
    pw = ptw + m(14)
    pcx = rect.right - m(8) - pw // 2
    pcy = rect.y + m(10)
    chip = pygame.Surface((pw, ph), pygame.SRCALPHA)
    pygame.draw.rect(chip, (10, 12, 30, 190), (0, 0, pw, ph), border_radius=ph // 2)
    pygame.draw.rect(chip, (*CARD_RING_BRIGHT, 60), (0, 0, pw, ph),
                     width=max(1, m(1)), border_radius=ph // 2)
    big.blit(chip, (pcx - pw // 2, pcy - ph // 2))
    plain_text(big, price_str, pf, (pcx, pcy), (236, 230, 208),
               shadow_a=0, weight=m(0.7))

    # 10. GEM CREST (top-left) — faceted tier badge per the locked spine.
    facet_gem(big, rect.x + m(19), rect.y + m(19), m(GEM_R + 2),
              pal["gem"], pal["deep"])

    # 11. bevel rim + dark keyline LAST so the card frame stays crisp over the
    #     sky that bleeds to the body edge. No inner tray — the sky reads
    #     edge-to-edge.
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 235),
              w=max(1, m(2.0)))
    return big, (cx, cy)


# ── review sheet ──────────────────────────────────────────────────────────────
VARIANTS = [
    ("RARE",      "skin_lorikeet", {"gem": (108, 188, 252), "glow": (60, 140, 230), "deep": (18, 44, 90)},  600),
    ("EPIC",      "skin_prism",    {"gem": (194, 122, 248), "glow": (140, 40, 230), "deep": (44, 10, 80)},  1400),
    ("LEGENDARY", "skin_kitsune",  {"gem": (255, 202, 104), "glow": (220, 160, 40), "deep": (90, 50, 0)},   3500),
]
ITEM_NAMES = {"skin_lorikeet": "Lorikeet", "skin_prism": "Prism", "skin_kitsune": "Kitsune"}

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
htxt = hfont.render("store_card_v3_tl — poster-backdrop — round 1", True, (236, 232, 214))
sheet.blit(htxt, (MARGIN, MARGIN + (HEADER_H - htxt.get_height()) // 2))

panel_y = MARGIN + HEADER_H
panels = []
for i, (tier, sid, pal, price) in enumerate(VARIANTS):
    px = MARGIN + i * (PANEL_W + GUTTER)
    panel, _ = render_card(sid, pal, price, ITEM_NAMES[sid])
    panels.append(panel)
    sheet.blit(panel, (px, panel_y))
    ftxt = ffont.render(tier, True, (218, 214, 200))
    sheet.blit(ftxt, (px + (PANEL_W - ftxt.get_width()) // 2,
                      panel_y + PANEL_H + (FOOTER_H - ftxt.get_height()) // 2))

# 1x real-scale strip: smoothscale each SS panel down to the live 162×100 card so
# the sheet shows the concept at true store size.
strip_label_y = panel_y + PANEL_H + FOOTER_H
ltxt = sfont.render("real scale (1×, 162×100)", True, (200, 204, 220))
sheet.blit(ltxt, (MARGIN, strip_label_y + (STRIP_LABEL_H - ltxt.get_height()) // 2))
strip_y = strip_label_y + STRIP_LABEL_H
for i, panel in enumerate(panels):
    px = MARGIN + i * (PANEL_W + GUTTER)
    left = px + (PANEL_W - CARD_W) // 2
    small = pygame.transform.smoothscale(panel, (CARD_W, CARD_H))
    sheet.blit(small, (left, strip_y))

out = "/home/user/skybit/docs/store_card_v3_tl/poster-backdrop/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
