"""bezel-hero — store_card_v2 concept, round 1 headless render.

All disc, no chrome: a large medallion (R=35) that leaves a VISIBLE indigo
body margin on all sides (the key departure from hero-medallion's edge-to-edge
disc), rarity carried entirely by a vivid tier halo on the glass bezel, and a
single slim frosted name band. Draws each variant on the SS=2 author canvas and
tiles them into a labelled review sheet — no smoothscale, so the geometry is
inspected at author resolution.
"""
import os

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import sys

sys.path.insert(0, "/home/user/skybit")

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game.hud import _font
from game.store_cards import (
    vgrad, vgrad_stops, drop_shadow, bevel_rim, top_sheen, contact_shadow,
    plain_text, price_chip, facet_gem, cabochon, cabochon_glass, blit_thumb,
    soft_glow, font, m, SS, CABO_LO, CABO_HI, CARD_T, CARD_B,
    CARD_RING_DEEP, CARD_RING_BRIGHT, CREAM, CARD_RAD, GEM_R,
)

BODY_W = 150      # visible body rect is 150x88 at logical origin (6,6)
PANEL_W = 162 * SS
PANEL_H = 100 * SS


def draw_bezel_hero(big, sid, name, pal, price):
    rad = m(CARD_RAD)
    body_x, body_y = m(6), m(6)
    rect = pygame.Rect(body_x, body_y, PANEL_W - 2 * body_x, PANEL_H - 2 * body_y)

    # Large medallion centred on the body, R=35 leaves ~6-10px of indigo margin
    # around it — the visible card-body edge is the whole point of this concept.
    R = 35
    cx, cy = rect.centerx, rect.y + m(40)

    # DEPTH STACK — same body finish as the live card so the exploration reads
    # like real game art.
    drop_shadow(big, rect, rad, blur=m(8), alpha=160, dy=m(4))
    big.blit(vgrad(rect.w, rect.h, rad, CARD_T, CARD_B, 252, gamma=1.15),
             rect.topleft)
    top_sheen(big, rect, rad, m(30), peak=62)
    contact_shadow(big, rect, rad, m(9), alpha=120)

    # inner tray dark border + faint gold lane
    tray = rect.inflate(-m(7), -m(7))
    trad = rad - m(4)
    pygame.draw.rect(big, (10, 10, 24, 200), tray.inflate(m(2), m(2)),
                     width=max(1, m(1)), border_radius=trad + m(1))
    pygame.draw.rect(big, (*CARD_RING_BRIGHT, 90), tray, width=max(1, m(1)),
                     border_radius=trad)

    # RARITY = the bezel halo. An enhanced soft glow (peak 70, not 30) drawn
    # FIRST so it seats behind the disc and blooms into the visible margin.
    soft_glow(big, cx, cy, m(R + 3), pal["glow"], 70, layers=12)

    # domed glass well -> hero skin -> glass overlay
    cabochon(big, cx, cy, m(R), CABO_LO, CABO_HI, ring=pal["gem"], ring_a=60)
    blit_thumb(big, sid, cx, cy, m(R) * 1.5)
    cabochon_glass(big, cx, cy, m(R), tint=pal["gem"])

    # tier-coloured bezel rings on the glass — the second half of the rarity read
    pygame.draw.circle(big, (*pal["gem"], 100), (cx, cy), m(R) + m(2), width=m(2))
    pygame.draw.circle(big, (*pal["gem"], 40), (cx, cy), m(R) + m(4), width=m(2))

    # ONE slim frosted name band at the disc's lower arc
    name_band = pygame.Surface((m(BODY_W - 16), m(12)), pygame.SRCALPHA)
    name_band.fill((8, 8, 20, 165))
    big.blit(name_band, (body_x + m(8), body_y + m(64)))
    plain_text(big, name, font(12), (cx, body_y + m(70)), CREAM,
               shadow_a=160, weight=m(0.8), keyline=(6, 6, 16), kw=m(0.8))

    # canonical gold price chip, centred, bottom kissing the body edge
    price_chip(big, cx, body_y + m(78), f"{price:,}", m(18), affordable=True)

    # crest gem, top-right corner (unchanged from the live card)
    facet_gem(big, rect.right - m(19), rect.y + m(19), m(GEM_R + 3),
              pal["gem"], pal["deep"])

    # bevel rim + dark keyline LAST so the card edge stays crisp
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 235),
              w=max(1, m(2.0)))


VARIANTS = [
    ("RARE", "skin_lorikeet", "LORIKEET",
     {"gem": (108, 188, 252), "glow": (60, 140, 230), "deep": (18, 44, 90)}, 600),
    ("EPIC", "skin_prism", "PRISM",
     {"gem": (194, 122, 248), "glow": (150, 60, 220), "deep": (44, 10, 80)}, 1400),
    ("LEGENDARY", "skin_kitsune", "KITSUNE",
     {"gem": (255, 202, 104), "glow": (220, 160, 40), "deep": (90, 50, 0)}, 3500),
]

MARGIN, GUTTER, HEADER, FOOTER = 20, 16, 30, 30
SHEET_W = MARGIN * 2 + 3 * PANEL_W + 2 * GUTTER
SHEET_H = MARGIN + HEADER + PANEL_H + FOOTER + MARGIN

sheet = pygame.Surface((SHEET_W, SHEET_H))
sheet.fill((16, 17, 30))

hfont = _font(22, True)
ffont = _font(20, True)
htxt = hfont.render("store_card_v2 — bezel-hero — round 1", True, (236, 232, 214))
sheet.blit(htxt, (MARGIN, MARGIN + (HEADER - htxt.get_height()) // 2))

panels_y = MARGIN + HEADER
for i, (tier, sid, name, pal, price) in enumerate(VARIANTS):
    panel = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    draw_bezel_hero(panel, sid, name, pal, price)
    px = MARGIN + i * (PANEL_W + GUTTER)
    sheet.blit(panel, (px, panels_y))
    ftxt = ffont.render(tier, True, (218, 214, 200))
    sheet.blit(ftxt, (px + (PANEL_W - ftxt.get_width()) // 2,
                      panels_y + PANEL_H + (FOOTER - ftxt.get_height()) // 2))

out = "/home/user/skybit/docs/store_card_v2/bezel-hero/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
