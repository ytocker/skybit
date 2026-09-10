"""Headless review render for the `sash-accent` store-card v2 concept.

Explores the CONSTELLATION card DNA with the rarity read pulled OUT of a
centred ribbon and flown as a full-height coloured sash down the right margin,
so tier stays legible even in peripheral grid scroll. Reuses the locked
store_cards primitives so the exploration matches shipped card fidelity.
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
    vgrad, vgrad_stops, drop_shadow, bevel_rim, top_sheen, contact_shadow,
    plain_text, price_chip, facet_gem, cabochon, cabochon_glass, blit_thumb,
    soft_glow, font, m, SS, CABO_LO, CABO_HI, CARD_T, CARD_B,
    CARD_RING_DEEP, CARD_RING_BRIGHT, CREAM, GEM_R, CARD_RAD, CARD_W, CARD_H,
)

# ── panel geometry (draw the SS canvas directly — no smoothscale) ──────────────
PW, PH = CARD_W * SS, CARD_H * SS        # 324 x 200 author canvas per card


def draw_sash_card(sid, name, pal, price):
    """One sash-accent card onto its own 324x200 SRCALPHA surface."""
    big = pygame.Surface((PW, PH), pygame.SRCALPHA)
    rad = m(CARD_RAD)
    rect = pygame.Rect(m(6), m(6), m(150), m(88))       # visible body 150x88
    body_x, body_y = rect.x, rect.y

    # disc sits slightly left of centre to leave the right margin for the sash
    cx_ss = body_x + m(68)
    cy_ss = body_y + m(40)
    R = 31

    # 1) soft multi-layer drop shadow (top-left light => offset down)
    drop_shadow(big, rect, rad, blur=m(8), alpha=160, dy=m(4))
    # 2) body gradient
    big.blit(vgrad(rect.w, rect.h, rad, CARD_T, CARD_B, 252, gamma=1.15),
             rect.topleft)
    # 3) glossy top sheen
    top_sheen(big, rect, rad, m(30), peak=62)
    # 4) bottom-right contact AO
    contact_shadow(big, rect, rad, m(9), alpha=120)
    # 5) neutral inner tray border (obsidian keyline under a faint gold lane)
    tray = rect.inflate(-m(7), -m(7))
    trad = rad - m(4)
    pygame.draw.rect(big, (10, 10, 24, 200), tray.inflate(m(2), m(2)),
                     width=max(1, m(1)), border_radius=trad + m(1))
    pygame.draw.rect(big, (*CARD_RING_BRIGHT, 90), tray, width=max(1, m(1)),
                     border_radius=trad)

    # 6) full-height tier sash on the right 28px of the body (top gem -> bottom
    #    deep). Blitted flush; its outer corners round naturally under the bevel.
    sash = vgrad_stops(m(28), m(88), 0,
                       [(0.0, pal["gem"]), (0.5, pal["glow"]), (1.0, pal["deep"])],
                       255, gamma=1.0)
    big.blit(sash, (body_x + m(122), body_y))
    # 7) 2px dark keyline where the sash meets the dark well
    pygame.draw.line(big, (4, 4, 14),
                     (body_x + m(122), body_y),
                     (body_x + m(122), body_y + m(88)), max(1, m(1)))
    # 8) tier word set vertically down the sash in cream
    tier = _TIER_FOR[sid]
    ts = font(8).render(tier, True, CREAM)
    ts = pygame.transform.rotate(ts, 90)
    big.blit(ts, ts.get_rect(center=(body_x + m(136), body_y + m(44))))

    # 9) tier aura under the cabochon hero
    soft_glow(big, cx_ss, cy_ss, m(R + 3), pal["glow"], 30, layers=8)
    # 10) cabochon well -> skin thumbnail -> glass dome overlay
    cabochon(big, cx_ss, cy_ss, m(R), CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    blit_thumb(big, sid, cx_ss, cy_ss, m(R) * 1.5)
    cabochon_glass(big, cx_ss, cy_ss, m(R), tint=pal["gem"])

    # 11) item name below the disc, centred in the LEFT zone
    plain_text(big, name, font(12), (cx_ss, body_y + m(66)), CREAM,
               shadow_a=160, weight=m(0.8), keyline=(6, 6, 16), kw=m(0.8))
    # 12) canonical gold price chip, centred in the left zone
    price_chip(big, cx_ss, body_y + m(78), f"{price:,}", m(18), affordable=True)

    # 13) crest gem top-right — crowns where the sash meets the top-right corner
    facet_gem(big, rect.right - m(19), rect.y + m(19), m(GEM_R + 3),
              pal["gem"], pal["deep"])

    # 14) crisp dark keyline UNDER the bright bevel, drawn LAST so the sash's
    #     outer corners clip cleanly into the rounded body edge.
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 235),
              w=max(1, m(2.0)))
    return big


_TIER_FOR = {
    "skin_lorikeet": "RARE",
    "skin_prism": "EPIC",
    "skin_kitsune": "LEGENDARY",
}

CARDS = [
    ("skin_lorikeet", "LORIKEET",
     {"gem": (108, 188, 252), "glow": (60, 140, 230), "deep": (18, 44, 90)}, 600),
    ("skin_prism", "PRISM",
     {"gem": (194, 122, 248), "glow": (150, 60, 220), "deep": (44, 10, 80)}, 1400),
    ("skin_kitsune", "KITSUNE",
     {"gem": (255, 202, 104), "glow": (220, 160, 40), "deep": (90, 50, 0)}, 3500),
]

# ── review sheet ──────────────────────────────────────────────────────────────
MARGIN, GUTTER, HEADER, FOOTER = 20, 16, 30, 26
sheet_w = MARGIN * 2 + PW * 3 + GUTTER * 2
sheet_h = MARGIN + HEADER + PH + FOOTER + MARGIN
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((22, 24, 34))

hf = font(11)
htxt = hf.render("store_card_v2 - sash-accent - round 1", True, (236, 238, 246))
sheet.blit(htxt, (MARGIN, MARGIN + (HEADER - htxt.get_height()) // 2))

ff = font(9)
for i, (sid, name, pal, price) in enumerate(CARDS):
    card = draw_sash_card(sid, name, pal, price)
    px = MARGIN + i * (PW + GUTTER)
    py = MARGIN + HEADER
    sheet.blit(card, (px, py))
    label = _TIER_FOR[sid]
    lt = ff.render(label, True, (214, 218, 230))
    sheet.blit(lt, (px + (PW - lt.get_width()) // 2,
                    py + PH + (FOOTER - lt.get_height()) // 2))

out = "/home/user/skybit/docs/store_card_v2/sash-accent/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
