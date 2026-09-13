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
# Pulled up to 50% of slip height so the item block above the tear no longer
# floats over an empty band; negative space now reads balanced on both stubs.
perf_y = sy + int(SLIP_H * 0.50)          # logical y of the tear line
py = m(perf_y)
dot_r = m(3)                               # ~6px diameter
spacing = m(12)
x0 = srect.x + m(10)
x1 = srect.right - m(10)
# faint shadow lane 1px below + highlight lane 1px above
pygame.draw.line(big, (0, 0, 0, 60), (x0, py + m(1)), (x1, py + m(1)), max(1, m(1)))
pygame.draw.line(big, (255, 246, 220, 55), (x0, py - m(1)), (x1, py - m(1)), max(1, m(1)))
x = x0 + dot_r
i = 0
while x <= x1 - dot_r:
    # Brighter interior dots (~15% lift) so the tear reads crisp against navy.
    a = 230 if (i % 2 == 0) else 150
    dot = pygame.Surface((dot_r * 2 + m(2), dot_r * 2 + m(2)), pygame.SRCALPHA)
    # Punch the perforation as a "hole": a dark core ringed by a thin light lip
    # so it reads as a stamped tear-hole, not just a printed dot.
    pygame.draw.circle(dot, (6, 5, 12, a), (dot_r + m(1), dot_r + m(1)), dot_r)
    pygame.draw.circle(dot, (255, 248, 224, min(255, a)), (dot_r + m(1), dot_r + m(1)),
                       dot_r, max(1, m(0.6)))
    big.blit(dot, (x - dot_r - m(1), py - dot_r - m(1)))
    x += spacing
    i += 1

# Half-circle tear bites carved into the LEFT and RIGHT silhouette edges on the
# perf row, so the outer shape itself shows the affordance to tear the stub.
# Sample the ground just outside each edge and refill the bite with it, so the
# carve reveals the true background (aura + vignette), not a flat black disc.
notch_r = m(8)
for edge_x, arc_lo, arc_hi in ((srect.x, -math.pi / 2, math.pi / 2),
                               (srect.right, math.pi / 2, 3 * math.pi / 2)):
    probe = m(sx - 7) if edge_x == srect.x else m(sx + SLIP_W + 7)
    bgcol = big.get_at((probe, py))
    pygame.draw.circle(big, bgcol, (edge_x, py), notch_r)
    # Dark contact keyline on the inner arc + a faint gold bevel lip catching
    # the same light as the slip border, selling the torn edge.
    rr = pygame.Rect(edge_x - notch_r, py - notch_r, notch_r * 2, notch_r * 2)
    pygame.draw.arc(big, (4, 5, 14), rr, arc_lo, arc_hi, max(1, m(1.6)))
    lip = rr.inflate(-m(1.4), -m(1.4))
    pygame.draw.arc(big, (*CARD_RING_BRIGHT, 150), lip, arc_lo, arc_hi, max(1, m(1)))

# ── TOP STUB (item) ──────────────────────────────────────────────────────────
DISC_R = 58
disc_cx = slip_cx
# Nudged down a touch so the top margin balances against the (now higher) tear.
disc_cy = sy + 86
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
# "TOTAL DUE" tally caption above the price — firmer size + brighter slate so it
# holds as a receipt label rather than dissolving into the body.
cap_f = font(10)
plain_text(big, "TOTAL DUE", cap_f, (m(slip_cx), m(perf_y + 32)),
           (190, 196, 216), shadow_a=0, tracking=m(1.8), weight=m(0.7))
price_chip(big, m(slip_cx), m(perf_y + 60), "12,500", m(26))


def crown_gloss(surf, rect, radius, peak, band=0.34):
    """A restrained specular confined to the top band only, alpha-composited (NOT
    additive) so the sheen TINTS the gold crown rather than saturating every
    channel to pure white — the pill keeps a gold body, never a white slab."""
    sweep = pygame.Surface(rect.size, pygame.SRCALPHA)
    bh = max(1, int(rect.h * band))
    for y in range(rect.h):
        a = int(peak * (1 - y / bh) ** 2.2) if y < bh else 0
        if a > 0:
            pygame.draw.line(sweep, (255, 250, 235, a), (0, y), (rect.w, y))
    mask = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=radius)
    sweep.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(sweep, rect.topleft)


# Gold BUY pill spanning ~75% slip width, ~20px above slip bottom.
buy_w = int(SLIP_W * 0.75)
buy_h = 58
buy_cx = slip_cx
buy_bottom = sy + SLIP_H - 20
# CANCEL raised to a comfortable 46px tall (was 38) so it clears the 44px touch
# floor visually; BUY re-stacked above it with a clear 12px gap.
cancel_h = 46
cancel_cy = buy_bottom - cancel_h // 2
GAP = 12
buy_cy = cancel_cy - cancel_h // 2 - GAP - buy_h // 2

buy_rect = pygame.Rect(m(buy_cx - buy_w // 2), m(buy_cy - buy_h // 2),
                       m(buy_w), m(buy_h))
brad = buy_rect.h // 2
drop_shadow(big, buy_rect, brad, blur=m(5), alpha=120, dy=m(3))
big.blit(gold_a_fill(buy_rect.w, buy_rect.h, brad), buy_rect.topleft)
crown_gloss(big, buy_rect, brad, peak=78, band=0.34)
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
cancel_f = font(15)
plain_text(big, "CANCEL", cancel_f, cancel_rect.center, (206, 212, 232),
           shadow_a=0, tracking=m(1.4), weight=m(0.7))

# ── downscale + save ─────────────────────────────────────────────────────────
out = pygame.transform.smoothscale(big, (SCR_W, SCR_H))
os.makedirs("/home/user/skybit/docs/confirm_purchase/ticket-stub", exist_ok=True)
path = "/home/user/skybit/docs/confirm_purchase/ticket-stub/round_2.png"
pygame.image.save(out, path)
print("saved", path, out.get_size())

# ── verification samples ─────────────────────────────────────────────────────
buy_center_y = buy_cy               # logical center row of the BUY pill
print("BUY center px:", out.get_at((slip_cx, buy_center_y)))
print("BUY body-left px:", out.get_at((slip_cx - buy_w // 4, buy_center_y)))
print("BUY crown px:", out.get_at((slip_cx, buy_cy - buy_h // 2 + 4)))
print("CANCEL visual height px:", cancel_h)
