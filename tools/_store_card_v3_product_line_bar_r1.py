"""product-line-bar — store_card_v3 concept, round 1 headless render.

A retail SKU read: the medallion hero rides high (R=35, disc centre raised to
CY=33 so the disc top kisses the body inset and the disc bottom clears a ~20px
footer lane) and a full-width tier-gradient FOOTER BAR seats along the body
bottom, carrying the skin NAME (left) and PRICE (right) like a product shelf
label. The bar itself IS the price chip — no separate chip body — so rarity is
read twice: once in the gutter halo, once in the bar's own tier ramp.

Copied scaffold from _store_card_v2_bezel_hero_r2 (_disc_tint, _gutter_aura,
VARIANTS list, review-sheet stitch); only render_card's layout is concept-new.

Headless (SDL dummy) → a 3-up RARE/EPIC/LEGENDARY review sheet at SS (324×200,
no downscale) + a real-scale 1x strip (162×100). Not wired into the live store;
writes docs/store_card_v3/product-line-bar/round_1.png.
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
    vgrad, drop_shadow, bevel_rim, top_sheen, contact_shadow,
    cabochon, cabochon_glass, blit_thumb, facet_gem, plain_text,
    font, m, SS, CABO_LO, CABO_HI, CARD_T, CARD_B,
    CARD_RING_DEEP, CARD_RING_BRIGHT, GEM_R,
)

# LOCKED card constants (from store_cards).
CARD_W, CARD_H = 162, 100
CARD_RAD = 17
_INSET = 6

# Hero medallion radius: R=35 leaves a ~40px indigo gutter left/right for the
# tier halo, and (raised) clears the footer lane below.
R = 35
# Disc centre raised so the disc top sits at y=4 (just inside the body inset)
# and the disc bottom at y=68 — leaving a clean ~20px footer lane to y=88.
CY = 33


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


def _top_edge_shadow(surf, bar, depth, alpha):
    """A soft AO band hugging the bar's TOP edge only, so the bar reads as
    resting UNDER the disc that overhangs it. contact_shadow hugs bottom+right,
    which is the wrong edge here — this feathers a dark band downward from the
    bar's top lip instead."""
    band = pygame.Surface((bar.w, depth), pygame.SRCALPHA)
    for y in range(depth):
        a = int(alpha * (1 - y / depth) ** 1.4)
        pygame.draw.line(band, (0, 0, 0, a), (0, y), (bar.w - 1, y))
    surf.blit(band, (bar.x, bar.y))


def _fit_font(txt, max_w, hi=10.5, lo=8.0):
    """Auto-shrink the label font from hi→lo (0.5 steps) until it fits max_w, so
    long skin names never spill past the bar's left cell."""
    size = hi
    while size > lo:
        f = font(size)
        if f.size(txt)[0] <= max_w:
            return f
        size -= 0.5
    return font(lo)


def render_card(sid, pal, price, name):
    """Draw ONE product-line-bar card onto a fresh SS panel (324×200) and return
    it. Drawn directly at SS (no smoothscale) so the review sheet inspects the
    geometry at author resolution."""
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
    # 5. inner tray dark border + faint gold lane framing the disc.
    tray = rect.inflate(-m(7), -m(7))
    trad = rad - m(4)
    pygame.draw.rect(big, (10, 10, 24, 200), tray.inflate(m(2), m(2)),
                     width=max(1, m(1)), border_radius=trad + m(1))
    pygame.draw.rect(big, (*CARD_RING_BRIGHT, 90), tray, width=max(1, m(1)),
                     border_radius=trad)

    # 6. domed glass well → hero skin (no under-disc additive glow).
    cabochon(big, cx, cy, m(R), CABO_LO, CABO_HI, ring=pal["gem"], ring_a=60)
    blit_thumb(big, sid, cx, cy, m(R) * 1.5)

    # 7. tier tint INSIDE the disc — warms the glass, tames near-white skins.
    _disc_tint(big, cx, cy, m(R), pal["glow"], pal["deep"])

    # 8. glass dome overlay (crescent sheen + gold bezel) on top of the tint.
    cabochon_glass(big, cx, cy, m(R), tint=pal["gem"])

    # 9. ONE tier-coloured bezel ring at R+2.
    pygame.draw.circle(big, (*pal["gem"], 100), (cx, cy), m(R) + m(2), width=m(2))

    # 10. gutter halo — tighter than bezel-hero (R+22) because the footer bar
    #     below now carries part of the rarity read.
    _gutter_aura(big, cx, cy, m(R), m(R + 22), pal["glow"], peak=90, layers=18)

    # 11. FOOTER BAR — full inner-tray-width tier-gradient shelf label, seated
    #     2px below the disc bottom. The bar IS the price chip: no chip body.
    bar = pygame.Rect(rect.x, cy + m(R) + m(2), rect.w, m(20))
    #     3-stop tier ramp: gem (top) → glow (mid) → deep (bottom) so the dark
    #     end seats at the base and the bar reads as its own lit slab.
    fill = pygame.Surface((bar.w, bar.h), pygame.SRCALPHA)
    for y in range(bar.h):
        t = (y / max(1, bar.h - 1)) ** 1.1
        if t < 0.5:
            c = lerp_color(pal["gem"], pal["glow"], t / 0.5)
        else:
            c = lerp_color(pal["glow"], pal["deep"], (t - 0.5) / 0.5)
        pygame.draw.line(fill, (*c, 255), (0, y), (bar.w - 1, y))
    big.blit(fill, bar.topleft)
    #     top-edge AO so the bar reads as resting below the overhanging disc.
    _top_edge_shadow(big, bar, depth=m(4), alpha=100)
    #     1px bevel to define the bar edges against body + gutter halo.
    bevel_rim(big, bar, 0, CARD_RING_DEEP, CARD_RING_BRIGHT, w=max(1, m(1)))

    # 12. NAME (left cell) — cream, left-aligned, m(8) pad, vertically centred,
    #     auto-shrunk to fit the left half of the bar.
    cream = (246, 240, 216)
    pad = m(8)
    price_txt = f"$ {price:,}"
    pfont = font(10.5)
    price_w = pfont.size(price_txt)[0]
    name_max = bar.w - price_w - pad * 3
    nfont = _fit_font(name, name_max)
    nsurf = nfont.render(name, True, cream)
    # bake a soft shadow for legibility over the tier ramp
    plain_text(big, name, nfont,
               (bar.x + pad + nsurf.get_width() // 2, bar.centery),
               cream, shadow_a=170, keyline=(20, 14, 4), kw=m(0.8))

    # 13. PRICE (right cell) — cream, right-aligned, m(8) pad.
    plain_text(big, price_txt, pfont,
               (bar.right - pad - price_w // 2, bar.centery),
               cream, shadow_a=170, keyline=(20, 14, 4), kw=m(0.8))

    # 14. crest gem — faceted tier badge, top-right corner.
    facet_gem(big, rect.right - m(19), rect.y + m(19), m(GEM_R + 3),
              pal["gem"], pal["deep"])

    # 15. bevel rim + dark keyline LAST so the card frame stays crisp.
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 235),
              w=max(1, m(2.0)))
    return big, (cx, cy)


# ── review sheet ──────────────────────────────────────────────────────────────
VARIANTS = [
    ("RARE", "skin_lorikeet",
     {"gem": (108, 188, 252), "glow": (60, 140, 230), "deep": (18, 44, 90)},
     600, "Lorikeet"),
    ("EPIC", "skin_prism",
     {"gem": (194, 122, 248), "glow": (140, 40, 230), "deep": (44, 10, 80)},
     1400, "Prism"),
    ("LEGENDARY", "skin_kitsune",
     {"gem": (255, 202, 104), "glow": (220, 160, 40), "deep": (90, 50, 0)},
     3500, "Kitsune"),
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
htxt = hfont.render("store_card_v3 — product-line-bar — round 1", True,
                    (236, 232, 214))
sheet.blit(htxt, (MARGIN, MARGIN + (HEADER_H - htxt.get_height()) // 2))

panel_y = MARGIN + HEADER_H
panels = []
centers = []
for i, (tier, sid, pal, price, name) in enumerate(VARIANTS):
    px = MARGIN + i * (PANEL_W + GUTTER)
    panel, ctr = render_card(sid, pal, price, name)
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

out = "/home/user/skybit/docs/store_card_v3/product-line-bar/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())

# footer-bar sanity: sample the bar centre (should read tier-mid), the bar
# bottom (should be the deep end), and the disc centre (must NOT be pure white).
for (tier, sid, pal, price, name), panel, (cx, cy) in zip(VARIANTS, panels, centers):
    bar_top = cy + m(R) + m(2)
    mid_px = panel.get_at((cx, bar_top + m(10)))[:3]
    center_px = panel.get_at((cx, cy))[:3]
    print(f"{tier:9s} bar-mid {mid_px}   disc-centre {center_px}")
