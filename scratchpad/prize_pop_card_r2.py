import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
import sys
sys.path.insert(0, "/home/user/skybit")
import pygame
import math
pygame.init()
pygame.display.set_mode((1, 1))

from game import store_cards as sc
from game.store_cards import (
    m, font, SS, RARITY, cabochon, cabochon_glass, blit_thumb,
    _ribbon, _name_on, price_chip, soft_glow, drop_shadow,
    vgrad_stops, gold_a_fill, plain_text, gloss_sweep, bevel_rim,
    chip_body, CARD_RING_BRIGHT, CARD_RING_DEEP, GOLD_A_RIM_DARK,
    GOLD_A_RIM_BRIGHT,
)

SID = "skin_lorikeet"
TIER = "legendary"
NAME = "RAINBOW LORIKEET"

# Logical (1x) screen; author at SS then one smoothscale down for crisp edges.
SCR_W, SCR_H = 360, 640
BG = (8, 6, 16)
CARD_BG_T = (24, 22, 40)      # slight sheen top
CARD_BG_B = (18, 16, 30)      # deep navy-obsidian body
pal = RARITY[TIER]

big = pygame.Surface((SCR_W * SS, SCR_H * SS), pygame.SRCALPHA)
big.fill((*BG, 255))

# A soft tier aura pooling behind the card so the deep obsidian ground reads
# alive rather than dead-flat.
soft_glow(big, m(180), m(300), m(210), pal["glow"], 12, layers=10)

# ── card geometry ────────────────────────────────────────────────────────────
# Trimmed to 280px (78% of screen) for a tighter, more premium silhouette than
# the round-1 300px body without cramping the stack inside.
CARD_W, CARD_H = 280, 448
card_cx, card_cy = 180, 310
sx = card_cx - CARD_W // 2
sy = card_cy - CARD_H // 2
crect = pygame.Rect(m(sx), m(sy), m(CARD_W), m(CARD_H))
RAD = m(18)
card_bottom = sy + CARD_H             # outer body bottom
inner_bottom = card_bottom - 7        # inner gold-hairline edge

# Depth: soft cast shadow so the card sits above the obsidian.
drop_shadow(big, crect, RAD, blur=m(10), alpha=170, dy=m(6))

# Card body — slightly lighter than screen, faint vertical sheen.
body = vgrad_stops(crect.w, crect.h, RAD, [(0.0, CARD_BG_T), (1.0, CARD_BG_B)],
                   255, gamma=1.1)
big.blit(body, crect.topleft)

# Gold double-bezel border: dark contact keyline under a bright top-left bevel.
pygame.draw.rect(big, (4, 5, 14), crect, width=max(1, m(2)), border_radius=RAD)
bevel_rim(big, crect, RAD, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 235), w=max(1, m(2.2)))
# Fine inner gold hairline = the second bezel lane.
inset = crect.inflate(-m(7), -m(7))
pygame.draw.rect(big, (*CARD_RING_BRIGHT, 95), inset, width=max(1, m(1)),
                 border_radius=RAD - m(4))

# ── HEADER banner (title) ────────────────────────────────────────────────────
# A slate pill anchored to the card top — the confirm context. Stays put while
# the prize+info stack below nudges down to close the mid-card void.
hdr_cy = 118
hdr_w, hdr_h = 168, 30
hrect = pygame.Rect(m(card_cx - hdr_w // 2), m(hdr_cy - hdr_h // 2),
                    m(hdr_w), m(hdr_h))
chip_body(big, hrect, hrect.h // 2, (86, 84, 100), (52, 50, 66),
          (14, 14, 24), (156, 158, 180), gloss=70)
hdr_f = font(12)
plain_text(big, "CONFIRM", hdr_f, hrect.center, (244, 244, 252),
           shadow_a=0, tracking=m(2.4), weight=m(0.9),
           keyline=(10, 10, 20), kw=m(0.8))

# ── PRIZE + INFO stack (nudged DOWN ~24px vs round 1 to close the void) ───────
# Cabochon hero disc carrying the real skin, then the tier ribbon, item name,
# and price chip — each in its own clear lane, reading top-to-bottom into BUY.
DISC_R = 46
disc_cx = card_cx
disc_cy = 208                          # was ~188 in round 1 → +20 down
dcx, dcy = m(disc_cx), m(disc_cy)
soft_glow(big, dcx, dcy, m(DISC_R + 8), pal["glow"], 44, layers=10)
cabochon(big, dcx, dcy, m(DISC_R), sc.CABO_LO, sc.CABO_HI, ring=pal["gem"], ring_a=50)
blit_thumb(big, SID, dcx, dcy, m(DISC_R) * 1.5)
cabochon_glass(big, dcx, dcy, m(DISC_R), tint=pal["gem"])

ribbon_cy = 286
_ribbon(big, TIER.upper(), m(card_cx), m(ribbon_cy), m(CARD_W - 60), pal)

name_cy = 320
_name_on(big, NAME, m(card_cx), m(name_cy), m(CARD_W - 44))

price_cy = 354
price_chip(big, m(card_cx), m(price_cy), "12,500", m(26))

# ── BUY pill (dominant gold — pulled UP ~16px to tighten price→BUY flow) ──────
# Untouched round-1 gold treatment: Ramp-A fill, gloss sweep, double rim. This
# is the hero action and must stay the brightest, largest control on the card.
buy_w = int(CARD_W * 0.75)
buy_h = 58
buy_cy = 410                           # was ~428 in round 1 → -18 up
buy_rect = pygame.Rect(m(card_cx - buy_w // 2), m(buy_cy - buy_h // 2),
                       m(buy_w), m(buy_h))
brad = buy_rect.h // 2
drop_shadow(big, buy_rect, brad, blur=m(5), alpha=120, dy=m(3))
big.blit(gold_a_fill(buy_rect.w, buy_rect.h, brad), buy_rect.topleft)
gloss_sweep(big, buy_rect, brad, peak=120)
pygame.draw.rect(big, GOLD_A_RIM_DARK, buy_rect, width=max(1, m(1.8)), border_radius=brad)
bevel_rim(big, buy_rect, brad, GOLD_A_RIM_DARK, (*GOLD_A_RIM_BRIGHT, 235), w=max(1, m(1.6)))
buy_f = font(19)
plain_text(big, "BUY", buy_f, buy_rect.center, (52, 28, 4), shadow_a=0,
           tracking=m(2), weight=m(1.1))

# ── CANCEL (ghost pill) ──────────────────────────────────────────────────────
# Raised to 48px tall (≥44 hit constraint) and seated with a ≥24px bottom
# margin inside the card so it no longer kisses the bottom bezel. Keeps the
# restrained ghost fill + visible keyline so it reads clearly subordinate to BUY.
cancel_w = int(CARD_W * 0.52)
cancel_h = 48
cancel_bottom = inner_bottom - 26      # clear ≥24px gap from the inner bezel
cancel_cy = cancel_bottom - cancel_h // 2
cancel_rect = pygame.Rect(m(card_cx - cancel_w // 2), m(cancel_cy - cancel_h // 2),
                          m(cancel_w), m(cancel_h))
crad = cancel_rect.h // 2
ghost = pygame.Surface(cancel_rect.size, pygame.SRCALPHA)
pygame.draw.rect(ghost, (255, 255, 255, 16), ghost.get_rect(), border_radius=crad)
big.blit(ghost, cancel_rect.topleft)
pygame.draw.rect(big, (196, 202, 224, 150), cancel_rect, width=max(1, m(1.4)),
                 border_radius=crad)
cancel_f = font(14)
plain_text(big, "CANCEL", cancel_f, cancel_rect.center, (206, 212, 232),
           shadow_a=0, tracking=m(1.4), weight=m(0.7))

# ── downscale + save ─────────────────────────────────────────────────────────
out = pygame.transform.smoothscale(big, (SCR_W, SCR_H))
outdir = "/home/user/skybit/docs/confirm_purchase/prize-pop-card"
os.makedirs(outdir, exist_ok=True)
path = os.path.join(outdir, "round_2.png")
pygame.image.save(out, path)

# ── verify AD constraints on the FINAL 1x render ─────────────────────────────
px = out
cxpix = card_cx
# CANCEL vertical extent: the visible keyline band around cancel_cy.
def is_keyline(c):
    r, g, b = c[0], c[1], c[2]
    return 120 < r < 230 and 120 < g < 240 and 150 < b < 255 and abs(r - b) < 90
top_e = bot_e = None
for y in range(cancel_cy - 40, cancel_cy + 40):
    # sample near the left keyline of the pill
    xk = card_cx - cancel_w // 2
    if 0 <= xk < SCR_W:
        c = px.get_at((xk, y))
        if is_keyline(c):
            if top_e is None:
                top_e = y
            bot_e = y
print("CANCEL keyline top:", top_e, "bottom:", bot_e,
      "height:", (bot_e - top_e + 1) if top_e else None)
print("authored cancel_h:", cancel_h, "cancel_cy:", cancel_cy,
      "cancel rect top:", cancel_cy - cancel_h // 2,
      "bottom:", cancel_cy + cancel_h // 2)
print("card inner_bottom:", inner_bottom, "outer bottom:", card_bottom)
print("bottom margin (inner):", inner_bottom - (cancel_cy + cancel_h // 2),
      " (outer):", card_bottom - (cancel_cy + cancel_h // 2))
print("price bottom:", price_cy + 13, "BUY top:", buy_cy - buy_h // 2,
      "price->BUY gap:", (buy_cy - buy_h // 2) - (price_cy + 13))
print("BUY bottom:", buy_cy + buy_h // 2, "CANCEL top:", cancel_cy - cancel_h // 2,
      "BUY->CANCEL gap:", (cancel_cy - cancel_h // 2) - (buy_cy + buy_h // 2))
print("saved", path, out.get_size())
