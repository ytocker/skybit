"""bezel-hero — store_card_v2 concept, round 3 headless render.

Round-3 revisions over round 2:
  1. Item name restored as a frosted dark overlay clipped to the bottom arc of
     the disc.  The veil is masked to the circle shape so it follows the dome
     curve; the name sits centred in the lower ~18 logical px of the glass.
  2. Price chip completely rethemed: the amber GOLD-RAMP-A sticker is replaced
     by a tier-tinted dark glass pill — body filled with the tier's deep colour
     at ~85 % alpha, price text in the tier gem colour.  No white.  No amber.
     The chip integrates into the card's palette instead of floating above it.
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
    cabochon, cabochon_glass, blit_thumb, facet_gem,
    plain_text, font, m, SS, CABO_LO, CABO_HI, CARD_T, CARD_B,
    CARD_RING_DEEP, CARD_RING_BRIGHT, GEM_R,
)

CARD_W, CARD_H = 162, 100
CARD_RAD = 17
_INSET = 6

R = 35  # disc radius (logical px)


def _disc_tint(surf, cx, cy, r, color, deep, peak=52, base=16):
    pad = 2
    tint = pygame.Surface((r * 2 + pad * 2, r * 2 + pad * 2), pygame.SRCALPHA)
    c = r + pad
    for i in range(r, 0, -1):
        f = i / r
        col = lerp_color(color, deep, f ** 1.3)
        a = int(base + (peak - base) * f ** 1.6)
        pygame.draw.circle(tint, (*col, a), (c, c), i, width=2)
    tmask = pygame.Surface(tint.get_size(), pygame.SRCALPHA)
    pygame.draw.circle(tmask, (255, 255, 255, 255), (c, c), r - m(1))
    tint.blit(tmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(tint, (cx - c, cy - c))


def _gutter_aura(surf, cx, cy, disc_r, glow_r, color, peak=90, layers=18):
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


def _name_overlay(surf, name, cx, cy, disc_r, strip_h=None, veil_a=145):
    """Frosted name band clipped to the bottom arc of the disc.

    Draws a semi-transparent dark veil, masks it to the circle so the edges
    follow the dome curve, then stamps the name text into the lower portion.
    Blit order: AFTER cabochon_glass, BEFORE the bezel ring."""
    if strip_h is None:
        strip_h = m(18)
    pad = m(2)
    diam = disc_r * 2 + pad * 2

    # Full-disc-sized SRCALPHA canvas — fill with veil, clip to circle.
    overlay = pygame.Surface((diam, diam), pygame.SRCALPHA)
    pygame.draw.circle(overlay, (0, 0, 0, veil_a), (diam // 2, diam // 2), disc_r)
    # Erase everything ABOVE the bottom strip so only the lower arc remains.
    cutoff = diam // 2 + disc_r - strip_h
    overlay.fill((0, 0, 0, 0), pygame.Rect(0, 0, diam, max(0, cutoff)))

    # Name text centred in the strip.
    text_cy = diam // 2 + disc_r - strip_h // 2
    avail_w = int(disc_r * 1.55)  # chord width at that arc depth
    sz = 11.0
    f = font(sz)
    while f.render(name, True, (255, 255, 255)).get_width() > avail_w and sz > 7.5:
        sz -= 0.5
        f = font(sz)
    plain_text(overlay, name, f, (diam // 2, text_cy),
               (246, 240, 216), shadow_a=190, weight=m(0.7),
               keyline=(4, 4, 14), kw=m(1.0))

    surf.blit(overlay, (cx - diam // 2, cy - diam // 2))


def _tier_price_chip(surf, cx, cy, price, pal, affordable=True):
    """Tier-coloured dark glass price pill — no amber, no white.

    Body: tier deep-colour at ~85 % alpha (almost black-tinted tier hue).
    Text: tier gem colour (bright) so it pops on the dark ground.
    A hair-thin rim in a slightly lifted tier tone keeps the pill legible."""
    h = m(16)
    text = f"{price:,}"
    f = font(8.5)
    tw = f.render(text, True, (255, 255, 255)).get_width()
    pad = m(16)
    w = pad + tw + pad
    r = pygame.Rect(cx - w // 2, cy - h // 2, w, h)

    if affordable:
        deep = pal["deep"]
        body_col = (*deep, 218)
        rim_col = (*[min(255, c + 38) for c in pal["gem"]], 75)
        txt_col = pal["gem"]
    else:
        body_col = (34, 36, 58, 205)
        rim_col = (80, 84, 112, 65)
        txt_col = (175, 180, 215)

    pill = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(pill, body_col, (0, 0, w, h), border_radius=h // 2)
    # Subtle gloss sweep at the top quarter of the pill.
    gloss = pygame.Surface((w, h // 2), pygame.SRCALPHA)
    pygame.draw.rect(gloss, (255, 255, 255, 22), (0, 0, w, h // 2),
                     border_radius=h // 2)
    pill.blit(gloss, (0, 0))
    pygame.draw.rect(pill, rim_col, (0, 0, w, h), width=max(1, m(1)),
                     border_radius=h // 2)
    surf.blit(pill, r.topleft)

    plain_text(surf, text, f, r.center, txt_col, shadow_a=0, weight=m(0.7))


ITEM_NAMES = {
    "skin_lorikeet": "Lorikeet",
    "skin_prism": "Prism",
    "skin_kitsune": "Kitsune",
}


def render_bezel_hero(sid, pal, price):
    big = pygame.Surface((CARD_W * SS, CARD_H * SS), pygame.SRCALPHA)
    rect = pygame.Rect(m(_INSET), m(_INSET),
                       CARD_W * SS - 2 * m(_INSET), CARD_H * SS - 2 * m(_INSET))
    rad = m(CARD_RAD)
    body_y = m(_INSET)
    cx, cy = rect.centerx, rect.y + m(40)

    drop_shadow(big, rect, rad, blur=m(8), alpha=160, dy=m(4))
    big.blit(vgrad(rect.w, rect.h, rad, CARD_T, CARD_B, 252, gamma=1.15),
             rect.topleft)
    top_sheen(big, rect, rad, m(30), peak=62)
    contact_shadow(big, rect, rad, m(9), alpha=120)

    tray = rect.inflate(-m(7), -m(7))
    trad = rad - m(4)
    pygame.draw.rect(big, (10, 10, 24, 200), tray.inflate(m(2), m(2)),
                     width=max(1, m(1)), border_radius=trad + m(1))
    pygame.draw.rect(big, (*CARD_RING_BRIGHT, 90), tray, width=max(1, m(1)),
                     border_radius=trad)

    cabochon(big, cx, cy, m(R), CABO_LO, CABO_HI, ring=pal["gem"], ring_a=60)
    blit_thumb(big, sid, cx, cy, m(R) * 1.5)
    _disc_tint(big, cx, cy, m(R), pal["glow"], pal["deep"])
    cabochon_glass(big, cx, cy, m(R), tint=pal["gem"])

    # Name overlaid on the disc bottom arc — sits inside the glass dome.
    name = ITEM_NAMES.get(sid, sid.replace("skin_", "").title())
    _name_overlay(big, name, cx, cy, m(R))

    # ONE tier-coloured bezel ring at R+2.
    pygame.draw.circle(big, (*pal["gem"], 100), (cx, cy), m(R) + m(2), width=m(2))

    # Tier gutter halo.
    _gutter_aura(big, cx, cy, m(R), m(R + 28), pal["glow"], peak=90, layers=18)

    # Tier-tinted dark glass price chip.
    _tier_price_chip(big, cx, body_y + m(78), price, pal, affordable=True)

    facet_gem(big, rect.right - m(19), rect.y + m(19), m(GEM_R + 3),
              pal["gem"], pal["deep"])

    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 235),
              w=max(1, m(2.0)))
    return big, (cx, cy)


VARIANTS = [
    ("RARE",      "skin_lorikeet",
     {"gem": (108, 188, 252), "glow": (60, 140, 230), "deep": (18, 44, 90)},  600),
    ("EPIC",      "skin_prism",
     {"gem": (194, 122, 248), "glow": (140, 40, 230), "deep": (44, 10, 80)}, 1400),
    ("LEGENDARY", "skin_kitsune",
     {"gem": (255, 202, 104), "glow": (220, 160, 40), "deep": (90, 50, 0)},  3500),
]

PANEL_W, PANEL_H = CARD_W * SS, CARD_H * SS
MARGIN = 20
GUTTER = 16
HEADER_H = 30
FOOTER_H = 24
STRIP_LABEL_H = 20
STRIP_H = CARD_H

sheet_w = MARGIN * 2 + PANEL_W * 3 + GUTTER * 2
sheet_h = MARGIN + HEADER_H + PANEL_H + FOOTER_H + STRIP_LABEL_H + STRIP_H + MARGIN
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((16, 17, 30))

hfont = _font(22, True)
ffont = _font(20, True)
sfont = _font(16, True)
htxt = hfont.render("store_card_v2 — bezel-hero — round 3", True, (236, 232, 214))
sheet.blit(htxt, (MARGIN, MARGIN + (HEADER_H - htxt.get_height()) // 2))

panel_y = MARGIN + HEADER_H
panels = []
centers = []
for i, (tier, sid, pal, price) in enumerate(VARIANTS):
    px = MARGIN + i * (PANEL_W + GUTTER)
    panel, ctr = render_bezel_hero(sid, pal, price)
    panels.append(panel)
    centers.append(ctr)
    sheet.blit(panel, (px, panel_y))
    ftxt = ffont.render(tier, True, (218, 214, 200))
    sheet.blit(ftxt, (px + (PANEL_W - ftxt.get_width()) // 2,
                      panel_y + PANEL_H + (FOOTER_H - ftxt.get_height()) // 2))

strip_label_y = panel_y + PANEL_H + FOOTER_H
ltxt = sfont.render("real scale (1×, 162×100):", True, (200, 204, 220))
sheet.blit(ltxt, (MARGIN, strip_label_y + (STRIP_LABEL_H - ltxt.get_height()) // 2))
strip_y = strip_label_y + STRIP_LABEL_H
for i, panel in enumerate(panels):
    px = MARGIN + i * (PANEL_W + GUTTER)
    small = pygame.transform.smoothscale(panel, (CARD_W, CARD_H))
    sheet.blit(small, (px + (PANEL_W - CARD_W) // 2, strip_y))

out = "/home/user/skybit/docs/store_card_v2/bezel-hero/round_3.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())

for (tier, sid, pal, price), panel, (cx, cy) in zip(VARIANTS, panels, centers):
    gx = cx + m(R) + m(15)
    gutter_px = panel.get_at((gx, cy))[:3]
    centre_px = panel.get_at((cx, cy))[:3]
    print(f"{tier:9s}  gutter+15px {gutter_px}   disc-centre {centre_px}")
