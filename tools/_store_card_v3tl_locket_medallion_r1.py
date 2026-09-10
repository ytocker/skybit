"""locket-medallion — store_card_v3_tl concept, round 1 headless render.

An ornate "reliquary locket" card: a small central medallion holds the skin,
orbited by 4 cardinal tier-gems (N/E/S/W) whose glow scales with rarity, all
framed by a SINGLE engraved roundel ring (no radiating spokes). The item name
lands on a straight frosted nameplate at the bottom (crown-peek's plaque form),
a gem crest sits top-LEFT as the "clasp", and the price rides a small engraved
cartouche top-RIGHT. The ornate outer silhouette frames a calm interior — the
ring + orbiting gems ornament the hero rather than compete with it.

Headless (SDL dummy) → a 3-up RARE/EPIC/LEGENDARY review sheet at SS
(324×200, no downscale) + a real-scale 1x strip (162×100). Not wired into the
live store; writes docs/store_card_v3_tl/locket-medallion/round_1.png.
"""
import math
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
    vgrad, drop_shadow, bevel_rim, top_sheen, contact_shadow,
    cabochon, cabochon_glass, blit_thumb, facet_gem, plain_text,
    font, m, SS, CABO_LO, CABO_HI, CARD_T, CARD_B,
    CARD_RING_DEEP, CARD_RING_BRIGHT, GEM_R,
)

# LOCKED card constants (from store_cards).
CARD_W, CARD_H = 162, 100
CARD_RAD = 17
_INSET = 6

# The locket hero is deliberately SMALL (R=16) so the engraved roundel ring and
# the 4 orbiting cardinal gems have room to frame it — ornament surrounds a calm
# centre rather than crowding it.
R = 16
ORBIT_R = 32        # logical radius the 4 cardinal gems ride on
GEM_ORBT = 5        # orbiting gem radius (logical)


def _disc_tint(surf, cx, cy, r, color, deep, peak=60, base=28):
    """A tier colour veil INSIDE the disc, clipped to the glass. It warms the
    cool CABO_LO→CABO_HI dome away from the indigo body, and — carrying a
    meaningful centre alpha — pulls a bright skin highlight toward the tier hue
    so it stops blowing out. The gentle exponent lets the hue carry inward
    instead of collapsing at the centre; the veil stays rim-biased (peak > base)
    so the skin reads through while the surround takes the tier hue."""
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


def _gutter_aura(surf, cx, cy, disc_r, glow_r, color, peak=80, layers=16):
    """A feathered tier halo that lives ONLY beyond a radius (disc_r), so it
    floods the surround with tier colour without touching — or blowing out — the
    hero inside. Normal alpha-carry blits (NOT additive) so the colour survives
    compositing and reads as a tint, not a hot white bloom. Here it fills the
    gutter BETWEEN the roundel ring and the orbit gems so the ring reads as a lit
    frame. Brightest at the rim, feathering out."""
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


def render_card(sid, pal, price, name):
    """Draw ONE locket-medallion card onto a fresh SS panel (324×200) and return
    it (drawn directly at SS, no smoothscale) plus the disc centre."""
    big = pygame.Surface((CARD_W * SS, CARD_H * SS), pygame.SRCALPHA)
    rect = pygame.Rect(m(_INSET), m(_INSET),
                       CARD_W * SS - 2 * m(_INSET), CARD_H * SS - 2 * m(_INSET))
    rad = m(CARD_RAD)
    cx, cy = rect.centerx, rect.y + m(38)

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
    #    reliquary interior even at "minimum chrome".
    tray = rect.inflate(-m(7), -m(7))
    trad = rad - m(4)
    pygame.draw.rect(big, (10, 10, 24, 200), tray.inflate(m(2), m(2)),
                     width=max(1, m(1)), border_radius=trad + m(1))
    pygame.draw.rect(big, (*CARD_RING_BRIGHT, 90), tray, width=max(1, m(1)),
                     border_radius=trad)

    # 6. ENGRAVED ROUNDEL RING — one ring, slightly bigger than the orbit circle,
    #    drawn BEFORE the disc so it reads as a frame behind. A dark outer shadow
    #    ring, the main CARD_RING_BRIGHT gold band, and a faint bright inner edge
    #    give the single band an engraved (recessed) read without any spokes.
    roundel_r = m(ORBIT_R + 4)
    pygame.draw.circle(big, (4, 5, 16, 160), (cx, cy),
                       roundel_r + m(2), width=max(1, m(2)))
    pygame.draw.circle(big, (*CARD_RING_BRIGHT, 140), (cx, cy),
                       roundel_r, width=max(1, m(2)))
    pygame.draw.circle(big, (*CARD_RING_BRIGHT, 80), (cx, cy),
                       roundel_r - m(2), width=max(1, m(1)))

    # 7. gutter halo — floods the ring between roundel + orbit gems with tier hue.
    _gutter_aura(big, cx, cy, m(ORBIT_R + 4), m(ORBIT_R + 22), pal["glow"],
                 peak=80, layers=16)

    # 8. LOCKET MEDALLION (centre) — the small domed glass well holding the skin,
    #    tier-tinted, glass overlay, and a tight double gold+tier bezel.
    cabochon(big, cx, cy, m(R), CABO_LO, CABO_HI, ring=pal["gem"], ring_a=80)
    if sid is not None:
        blit_thumb(big, sid, cx, cy, m(R) * 1.5)
    _disc_tint(big, cx, cy, m(R), pal["glow"], pal["deep"], peak=60, base=28)
    cabochon_glass(big, cx, cy, m(R), tint=pal["gem"])
    pygame.draw.circle(big, (*CARD_RING_BRIGHT, 200), (cx, cy),
                       m(R) + m(1), width=max(1, m(1)))
    pygame.draw.circle(big, (*pal["gem"], 120), (cx, cy),
                       m(R) + m(2), width=max(1, m(2)))

    # 9. 4 ORBITING CARDINAL TIER-GEMS at N/E/S/W — faceted brilliants riding the
    #    orbit circle. Their tier glow scales with rarity via the palette.
    for angle_deg in (270, 0, 90, 180):   # N=270°, E=0°, S=90°, W=180°
        angle_rad = math.radians(angle_deg)
        ox = cx + int(m(ORBIT_R) * math.cos(angle_rad))
        oy = cy + int(m(ORBIT_R) * math.sin(angle_rad))
        facet_gem(big, ox, oy, m(GEM_ORBT), pal["gem"], pal["deep"])

    # 10. BOTTOM NAMEPLATE — a straight frosted plaque (crown-peek's plaque form)
    #     carrying the cream item name.
    plaque_cy = rect.bottom - m(22)
    plaque_w = m(80)
    plaque_h = m(16)
    plaque = pygame.Surface((plaque_w, plaque_h), pygame.SRCALPHA)
    pygame.draw.rect(plaque, (22, 24, 55, 200), (0, 0, plaque_w, plaque_h),
                     border_radius=plaque_h // 2)
    pygame.draw.rect(plaque, (*CARD_RING_BRIGHT, 120), (0, 0, plaque_w, plaque_h),
                     width=max(1, m(1)), border_radius=plaque_h // 2)
    big.blit(plaque, (cx - plaque_w // 2, plaque_cy - plaque_h // 2))
    plain_text(big, name, font(8.5), (cx, plaque_cy), (236, 230, 208),
               shadow_a=150, weight=m(0.7))

    # 11. PRICE — a small engraved cartouche top-RIGHT: a dark body with a
    #     debossed top-edge shadow + bright bottom rim so the tier-hued price
    #     reads as struck into the metal.
    price_str = f"{price:,}"
    pf = font(8.5)
    ptw = pf.render(price_str, True, (255, 255, 255)).get_width()
    pw = ptw + m(14)
    ph = m(14)
    pcx = rect.right - m(8) - pw // 2
    pcy = rect.y + m(10)
    cart = pygame.Surface((pw, ph), pygame.SRCALPHA)
    pygame.draw.rect(cart, (8, 9, 22, 220), (0, 0, pw, ph), border_radius=m(3))
    pygame.draw.line(cart, (0, 0, 0, 120), (m(2), m(1)), (pw - m(2), m(1)),
                     max(1, m(1)))
    pygame.draw.line(cart, (*CARD_RING_BRIGHT, 80),
                     (m(2), ph - m(2)), (pw - m(2), ph - m(2)), max(1, m(1)))
    big.blit(cart, (pcx - pw // 2, pcy - ph // 2))
    plain_text(big, price_str, pf, (pcx, pcy), pal["gem"],
               shadow_a=0, weight=m(0.8))

    # 12. GEM CREST ("clasp") — faceted tier badge, top-LEFT corner.
    facet_gem(big, rect.x + m(19), rect.y + m(19), m(GEM_R + 3),
              pal["gem"], pal["deep"])

    # 13. bevel rim + dark keyline LAST so the card frame stays crisp over the
    #     halo that bleeds to the body edge.
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 235),
              w=max(1, m(2.0)))
    return big, (cx, cy)


# ── review sheet ──────────────────────────────────────────────────────────────
VARIANTS = [
    ("RARE",      "skin_lorikeet", {"gem": (108, 188, 252), "glow": (60, 140, 230), "deep": (18, 44, 90)},  600,  "Lorikeet"),
    ("EPIC",      "skin_prism",    {"gem": (194, 122, 248), "glow": (140, 40, 230), "deep": (44, 10, 80)},  1400, "Prism"),
    ("LEGENDARY", "skin_kitsune",  {"gem": (255, 202, 104), "glow": (220, 160, 40), "deep": (90, 50, 0)},   3500, "Kitsune"),
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
htxt = hfont.render("store_card_v3_tl — locket-medallion — round 1", True,
                    (236, 232, 214))
sheet.blit(htxt, (MARGIN, MARGIN + (HEADER_H - htxt.get_height()) // 2))

panel_y = MARGIN + HEADER_H
panels = []
for i, (tier, sid, pal, price, name) in enumerate(VARIANTS):
    px = MARGIN + i * (PANEL_W + GUTTER)
    panel, _ = render_card(sid, pal, price, name)
    panels.append(panel)
    sheet.blit(panel, (px, panel_y))
    ftxt = ffont.render(tier, True, (218, 214, 200))
    sheet.blit(ftxt, (px + (PANEL_W - ftxt.get_width()) // 2,
                      panel_y + PANEL_H + (FOOTER_H - ftxt.get_height()) // 2))

# 1x real-scale strip: smoothscale each SS panel down to the live 162×100 card.
strip_label_y = panel_y + PANEL_H + FOOTER_H
ltxt = sfont.render("real scale (1×, 162×100)", True, (200, 204, 220))
sheet.blit(ltxt, (MARGIN, strip_label_y + (STRIP_LABEL_H - ltxt.get_height()) // 2))
strip_y = strip_label_y + STRIP_LABEL_H
for i, panel in enumerate(panels):
    px = MARGIN + i * (PANEL_W + GUTTER)
    left = px + (PANEL_W - CARD_W) // 2
    small = pygame.transform.smoothscale(panel, (CARD_W, CARD_H))
    sheet.blit(small, (left, strip_y))

out = "/home/user/skybit/docs/store_card_v3_tl/locket-medallion/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
