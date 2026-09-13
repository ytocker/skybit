"""portrait-vignette — store_card_v4 concept, round 1 headless render.

A theatrical, disc-led card. The standard indigo body is overlaid with a
SPOTLIGHT VIGNETTE — a radial falloff that keeps the indigo bright behind the
hero disc's centre and sinks all four corners into shadow, so the eye is thrown
straight at the item. A single large cabochon hero (R=38, centred high) is the
whole card; rarity is carried by the top-right gem crest + the disc's tier aura.
The item name rides ONE clean full-width frosted bar flush at the bottom, with
the bare-numeral coin price sharing that bar on the right.

Headless (SDL dummy) -> a 3-up RARE/EPIC/LEGENDARY review sheet at SS
(324x200, no downscale) + a real-scale 1x strip (162x100). Not wired into the
live store; writes docs/store_card_v4/portrait-vignette/round_1.png.
"""
import os

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import sys

sys.path.insert(0, "/home/user/skybit")

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game import store_catalog
from game.hud import _font
from game.store_cards import (
    vgrad, vgrad_stops, drop_shadow, bevel_rim, top_sheen, contact_shadow,
    cabochon, cabochon_glass, blit_thumb, facet_gem, plain_text, soft_glow,
    coin_glyph, _glyph_base, _rarity, font, m, SS,
    CABO_LO, CABO_HI, CARD_T, CARD_B, CARD_RING_DEEP, CARD_RING_BRIGHT,
    GEM_R, RARITY, MYSTERY, NEAR_BLACK,
)

# LOCKED card constants (from store_cards).
CARD_W, CARD_H = 162, 100
CARD_RAD = 17
_INSET = 6

# Hero disc: R=38 fills nearly the full width, centred high so the frosted
# name/price bar clears its lower rim and the corners can sink to shadow.
R = 38


def _spotlight_vignette(surf, rect, spot, peak=120, reach=None):
    """Lay a radial spotlight over the indigo body: bright at `spot`, darkening
    toward every corner. Built as a uniform NEAR_BLACK veil with a soft light
    disc SUBTRACTED at the spotlight centre — so the centre reads through clean
    while the far corners keep the full veil. Clipped to the rounded body."""
    w, h = rect.w, rect.h
    sx, sy = spot
    if reach is None:
        # Stop short of the far corners so they never get lit back out.
        reach = int(min(w, h) * 0.96)
    vig = pygame.Surface((w, h), pygame.SRCALPHA)
    vig.fill((*NEAR_BLACK, peak))
    light = pygame.Surface((w, h), pygame.SRCALPHA)
    layers = 46
    for i in range(layers, 0, -1):
        r = int(reach * i / layers)
        if r <= 0:
            continue
        a = int(peak * (1 - (i - 1) / layers) ** 1.7)
        if a <= 0:
            continue
        g = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(g, (255, 255, 255, a), (r + 1, r + 1), r)
        light.blit(g, (sx - r - 1, sy - r - 1), special_flags=pygame.BLEND_ADD)
    vig.blit(light, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w, h),
                     border_radius=m(CARD_RAD))
    vig.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(vig, rect.topleft)


def _name_on_bar(surf, name, cx, cy, max_w):
    """Cream item name with a tight dark keyline, auto-shrunk from 9.5pt in 0.5
    steps until it fits `max_w` (the bar minus the reserved price cell)."""
    sz = 9.5
    f = font(sz)
    while _glyph_base(name, f, 0).get_width() > max_w and sz > 6.0:
        sz -= 0.5
        f = font(sz)
    plain_text(surf, name, f, (cx, cy), (236, 230, 208), shadow_a=150,
               weight=m(0.9), keyline=(6, 6, 16), kw=m(0.8))


def render_card(sid):
    """Draw ONE portrait-vignette card onto a fresh SS panel (324x200) and
    return it (drawn directly at SS, no smoothscale)."""
    pal = RARITY.get(_rarity(sid), MYSTERY)
    name = store_catalog.name(sid)

    big = pygame.Surface((CARD_W * SS, CARD_H * SS), pygame.SRCALPHA)
    rect = pygame.Rect(m(_INSET), m(_INSET),
                       CARD_W * SS - 2 * m(_INSET), CARD_H * SS - 2 * m(_INSET))
    rad = m(CARD_RAD)
    cx, cy = rect.centerx, rect.y + m(40)

    # ── SHELL (locked order) ──
    drop_shadow(big, rect, rad, blur=m(8), alpha=160, dy=m(4))
    big.blit(vgrad(rect.w, rect.h, rad, CARD_T, CARD_B, 252, gamma=1.15),
             rect.topleft)
    top_sheen(big, rect, rad, m(30), peak=62)
    # spotlight over the bright indigo, tracking the disc centre.
    _spotlight_vignette(big, rect, (cx - rect.x, cy - rect.y), peak=120)
    contact_shadow(big, rect, rad, m(9), alpha=120)
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 235),
              w=max(1, m(2.0)))

    # ── HERO DISC ──
    soft_glow(big, cx, cy, m(R + 3), pal["glow"], 34, layers=9)
    cabochon(big, cx, cy, m(R), CABO_LO, CABO_HI, ring=pal["gem"], ring_a=55)
    blit_thumb(big, sid, cx, cy, m(R) * 1.5)
    cabochon_glass(big, cx, cy, m(R), tint=pal["gem"])

    # ── GEM CREST (locked call) ──
    facet_gem(big, rect.right - m(19), rect.y + m(19), m(GEM_R + 3),
              pal["gem"], pal["deep"])

    # ── FROSTED NAME/PRICE BAR — one full-width plate flush at the bottom, in
    #    front of the disc's lower rim like a lit stage ledge. ──
    bar_h = m(16)
    bar_bottom = rect.bottom - m(2)
    bar = pygame.Rect(rect.x + m(2), bar_bottom - bar_h, rect.w - m(4), bar_h)
    frosted = vgrad_stops(bar.w, bar.h, m(6), [(0.0, CABO_LO), (1.0, CABO_HI)],
                          alpha=200)
    big.blit(frosted, bar.topleft)
    # thin gold kiss along the bar's top edge so it reads as frosted glass.
    pygame.draw.line(big, (*CARD_RING_BRIGHT, 140),
                     (bar.x + m(6), bar.top), (bar.right - m(6), bar.top),
                     max(1, m(1)))
    bar_cy = bar.centery

    # price — bare numerals: coin glyph + number, right-anchored on the bar.
    price_str = "480"
    pf = font(9.0)
    num_w = _glyph_base(price_str, pf, 0).get_width()
    coin_r = m(5)
    price_x = bar.right - m(8) - num_w - m(16) + coin_r  # coin cell centre
    coin_glyph(big, price_x, bar_cy, coin_r)
    plain_text(big, price_str, pf, (price_x + m(16), bar_cy), pal["gem"],
               shadow_a=0, weight=m(0.9), keyline=(6, 6, 16), kw=m(0.7))

    # name — cream, auto-fit into the bar minus the reserved price cell.
    max_w = rect.w - m(50)
    name_cx = bar.x + m(8) + max_w // 2
    _name_on_bar(big, name.upper(), name_cx, bar_cy, max_w)

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
STRIP_H = CARD_H                              # real-scale 1x cards (162x100)

sheet_w = MARGIN * 2 + PANEL_W * 3 + GUTTER * 2
sheet_h = (MARGIN + HEADER_H + PANEL_H + FOOTER_H + STRIP_LABEL_H + STRIP_H
           + MARGIN)
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((8, 8, 20))

hfont = _font(22, True)
ffont = _font(18, True)
sfont = _font(15, True)
htxt = hfont.render("store_card_v4 — portrait-vignette — round 1", True,
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

# 1x real-scale strip: smoothscale each SS panel down to the live 162x100 card.
strip_label_y = panel_y + PANEL_H + FOOTER_H
ltxt = sfont.render("real scale (1x, 162x100)", True, (200, 204, 220))
sheet.blit(ltxt, (MARGIN, strip_label_y + (STRIP_LABEL_H - ltxt.get_height()) // 2))
strip_y = strip_label_y + STRIP_LABEL_H
for i, panel in enumerate(panels):
    px = MARGIN + i * (PANEL_W + GUTTER)
    left = px + (PANEL_W - CARD_W) // 2
    small = pygame.transform.smoothscale(panel, (CARD_W, CARD_H))
    sheet.blit(small, (left, strip_y))

out = "/home/user/skybit/docs/store_card_v4/portrait-vignette/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
