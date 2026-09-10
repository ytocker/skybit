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
    m, mf, font, SS, RARITY, cabochon, cabochon_glass, blit_thumb,
    _ribbon, _name_on, state_chip, price_chip, soft_glow, drop_shadow,
    vgrad_stops, gold_a_fill, plain_text, _glyph_base, gloss_sweep,
    bevel_rim, CARD_RING_BRIGHT, CARD_RING_DEEP, GOLD_A_STOPS,
    GOLD_A_RIM_DARK, GOLD_A_RIM_BRIGHT, R_DISC,
)
from game.draw import lerp_color, NEAR_BLACK, WHITE

SID = "skin_lorikeet"
TIER = "legendary"
NAME = "RAINBOW LORIKEET"

# Logical (1x) screen; author at SS then one smoothscale down for crisp edges.
SCR_W, SCR_H = 360, 640
BG = (8, 6, 16)
SLIP_BG_T = (24, 22, 40)      # slight sheen top
SLIP_BG_B = (18, 16, 30)      # deep navy-obsidian body
pal = RARITY[TIER]

big = pygame.Surface((SCR_W * SS, SCR_H * SS), pygame.SRCALPHA)
big.fill((*BG, 255))

# A soft vignette + a faint tier aura pooling behind the slip so the deep
# obsidian ground doesn't read dead-flat.
soft_glow(big, m(180), m(300), m(210), pal["glow"], 12, layers=10)

# ── slip geometry ──────────────────────────────────────────────────────────
SLIP_W, SLIP_H = 280, 480
slip_cx, slip_cy = 180, 320
sx = slip_cx - SLIP_W // 2
sy = slip_cy - SLIP_H // 2
srect = pygame.Rect(m(sx), m(sy), m(SLIP_W), m(SLIP_H))
RAD = m(18)

# Depth: soft cast shadow so the slip sits above the obsidian.
drop_shadow(big, srect, RAD, blur=m(10), alpha=170, dy=m(6))

# Slip body — slightly lighter than screen, faint vertical sheen.
body = vgrad_stops(srect.w, srect.h, RAD, [(0.0, SLIP_BG_T), (1.0, SLIP_BG_B)],
                   255, gamma=1.1)
big.blit(body, srect.topleft)

# Gold double-bezel border: dark contact keyline under a bright top-left bevel.
pygame.draw.rect(big, (4, 5, 14), srect, width=max(1, m(2)), border_radius=RAD)
bevel_rim(big, srect, RAD, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 235), w=max(1, m(2.2)))
# Fine inner gold hairline = the second bezel lane.
inset = srect.inflate(-m(7), -m(7))
pygame.draw.rect(big, (*CARD_RING_BRIGHT, 95), inset, width=max(1, m(1)),
                 border_radius=RAD - m(4))

# ── perforation tear line — the hero graphic ─────────────────────────────────
# At ~55% of slip height, a clean dashed row of filled circles spanning the
# full slip width, with a faint shadow below + highlight above for depth. The
# perforation reads as the physical divider between item and payment.
perf_y = sy + int(SLIP_H * 0.55)          # logical y of the tear line
py = m(perf_y)
dot_r = m(3)                               # ~6px diameter
spacing = m(12)
x0 = srect.x + m(10)
x1 = srect.right - m(10)
# faint shadow lane 1px below + highlight lane 1px above
pygame.draw.line(big, (0, 0, 0, 60), (x0, py + m(1)), (x1, py + m(1)), max(1, m(1)))
pygame.draw.line(big, (255, 246, 220, 50), (x0, py - m(1)), (x1, py - m(1)), max(1, m(1)))
x = x0 + dot_r
i = 0
while x <= x1 - dot_r:
    a = 200 if (i % 2 == 0) else 120
    dot = pygame.Surface((dot_r * 2 + m(2), dot_r * 2 + m(2)), pygame.SRCALPHA)
    # Punch the perforation as a "hole": a dark core ringed by a thin light lip
    # so it reads as a stamped tear-hole, not just a printed dot.
    pygame.draw.circle(dot, (6, 5, 12, a), (dot_r + m(1), dot_r + m(1)), dot_r)
    pygame.draw.circle(dot, (255, 244, 214, min(255, a)), (dot_r + m(1), dot_r + m(1)),
                       dot_r, max(1, m(0.6)))
    big.blit(dot, (x - dot_r - m(1), py - dot_r - m(1)))
    x += spacing
    i += 1

# ── TOP STUB (item) ──────────────────────────────────────────────────────────
disc_r = R_DISC  # note: card R_DISC is small; we want R≈58 logical, author via m
DISC_R = 58
disc_cx = slip_cx
disc_cy = sy + 80
dcx, dcy = m(disc_cx), m(disc_cy)
# Tier aura behind the cabochon so the legendary skin reads as the hero.
soft_glow(big, dcx, dcy, m(DISC_R + 8), pal["glow"], 44, layers=10)
cabochon(big, dcx, dcy, m(DISC_R), sc.CABO_LO, sc.CABO_HI, ring=pal["gem"], ring_a=50)
blit_thumb(big, SID, dcx, dcy, m(DISC_R) * 1.5)
cabochon_glass(big, dcx, dcy, m(DISC_R), tint=pal["gem"])

# Tier ribbon below the disc, then the item name below the ribbon.
ribbon_cy = disc_cy + DISC_R + 26
_ribbon(big, TIER.upper(), m(slip_cx), m(ribbon_cy), m(SLIP_W - 60), pal)
name_cy = ribbon_cy + 30
_name_on(big, NAME, m(slip_cx), m(name_cy), m(SLIP_W - 44))

# ── BOTTOM STUB (payment + decision) ─────────────────────────────────────────
# A small "TOTAL" caption above the price so the lower stub reads as a receipt
# tally, reinforcing the transaction-slip metaphor.
cap_f = font(9)
plain_text(big, "TOTAL DUE", cap_f, (m(slip_cx), m(perf_y + 30)),
           (170, 176, 200), shadow_a=0, tracking=m(1.6), weight=m(0.6))
price_chip(big, m(slip_cx), m(perf_y + 56), "12,500", m(26))

# Gold BUY pill spanning ~75% slip width, ≥56px tall, ~20px above slip bottom.
buy_w = int(SLIP_W * 0.75)
buy_h = 58
buy_cx = slip_cx
buy_bottom = sy + SLIP_H - 20
# CANCEL sits below BUY, so BUY is stacked above it.
cancel_h = 38
cancel_cy = buy_bottom - cancel_h // 2
buy_cy = cancel_cy - cancel_h // 2 - 10 - buy_h // 2

buy_rect = pygame.Rect(m(buy_cx - buy_w // 2), m(buy_cy - buy_h // 2),
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

# Ghost CANCEL pill — visible keyline, ample hit rect, restrained fill.
cancel_w = int(SLIP_W * 0.5)
cancel_rect = pygame.Rect(m(buy_cx - cancel_w // 2), m(cancel_cy - cancel_h // 2),
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
os.makedirs("/home/user/skybit/docs/confirm_purchase/ticket-stub", exist_ok=True)
path = "/home/user/skybit/docs/confirm_purchase/ticket-stub/round_1.png"
pygame.image.save(out, path)
print("saved", path, out.get_size())
