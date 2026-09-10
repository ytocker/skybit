#!/usr/bin/env python3
"""
capped-plate confirm_purchase_v5 round 1 render.

Concept: exactly TWO floating elements per panel.
  1. A small floating tier-cap TILE up top — carries ONLY the tier word, large
     and dominant, on its own drop shadow so it visibly hovers. Tier-tinted with
     a subtle deep -> gem gradient.
  2. One CONNECTED body-plus-foot PLATE below — a single uninterrupted vgrad
     slab carrying the disc in its upper half and the price + confirm chip in
     its lower half.
A single clean transparent gap separates the two; nothing else breaks the card.

Sheet shows the three tiers side by side (RARE / EPIC / LEGENDARY). Only the
cap tint + the disc's two-part rim glow change per tier — the plate structure is
identical across all three.
"""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
import sys
sys.path.insert(0, "/home/user/skybit")

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

import game.store_cards as sc
from game.store_cards import (
    vgrad_stops, drop_shadow, bevel_rim, top_sheen, soft_glow,
    plain_text, price_chip, chip_body_stops,
    cabochon, cabochon_glass, blit_thumb, _glyph_base, font, m, SS,
    CABO_LO, CABO_HI, CARD_T, CARD_B, CARD_RING_DEEP, CARD_RING_BRIGHT,
    GOLD_A_STOPS, GOLD_A_RIM_DARK as GOLD_RIM_DK, GOLD_A_RIM_BRIGHT as GOLD_RIM_BR,
)
from game.hud import _font
from game.draw import lerp_color, NEAR_BLACK, WHITE


# Patch gloss_sweep so additive intensity lives in RGB MAGNITUDE, not alpha —
# BLEND_ADD ignores source alpha, so an alpha-driven sweep silently blows the
# gold chips to white. Storing the value in RGB keeps the sheen controllable.
def _gloss_sweep_fixed(surf, rect, radius, peak=120):
    sweep = pygame.Surface(rect.size, pygame.SRCALPHA)
    h = max(1, rect.h)
    for y in range(h):
        v = int(peak * (1 - y / h) ** 2.4)
        if v <= 0:
            continue
        pygame.draw.line(sweep, (v, v, v, 255), (0, y), (rect.w, y))
    sm = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(sm, (255, 255, 255, 255), sm.get_rect(), border_radius=radius)
    sweep.blit(sm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(sweep, rect.topleft, special_flags=pygame.BLEND_ADD)
sc.gloss_sweep = _gloss_sweep_fixed


# ── brief palette (per-tier gem / glow / deep) ────────────────────────────────
TIERS = [
    ("RARE",      "skin_wizard",    720,
     {"gem": (108, 188, 252), "glow": (60, 140, 230), "deep": (18, 44, 90)}),
    ("EPIC",      "skin_prism",    1400,
     {"gem": (194, 122, 248), "glow": (150, 60, 220), "deep": (44, 10, 80)}),
    ("LEGENDARY", "skin_astronaut", 2600,
     {"gem": (255, 202, 104), "glow": (220, 160, 40), "deep": (90, 50, 0)}),
]


# ── popup metrics (logical px; flow through m()) ──────────────────────────────
POP_W, POP_H = 236, 278
CX = POP_W // 2

CAP_W, CAP_H = 210, 46          # small floating tier-cap tile
CAP_Y = 6                       # top of the cap tile
CAP_RAD = 12

GAP = 11                        # the ONE clean transparent gap
PLATE_X = 8
PLATE_Y = CAP_Y + CAP_H + GAP   # 63
PLATE_W = POP_W - PLATE_X * 2   # 220
PLATE_H = POP_H - PLATE_Y - 6   # 209
PLATE_RAD = 16

R_DISC = 45                     # disc lives in the plate's UPPER half
CY_DISC = PLATE_Y + 60
Y_PRICE = PLATE_Y + 132         # lower half: price then confirm
Y_CONFIRM = PLATE_Y + 172


def _confirm_chip(surf, cx, cy, h):
    """CONFIRM action button — same chip-body DNA as the price chip so the
    action row reads as one product line."""
    text = "CONFIRM"
    f = font(h * 0.46 / SS)
    nw = _glyph_base(text, f, m(1.4)).get_width()
    r = pygame.Rect(cx - (nw + m(40)) // 2, cy - h // 2, nw + m(40), h)
    chip_body_stops(surf, r, h // 2, GOLD_A_STOPS, GOLD_RIM_DK, GOLD_RIM_BR,
                    gloss=64, gamma=1.04)
    plain_text(surf, text, f, r.center, (54, 30, 4), shadow_a=0,
               tracking=m(1.4), weight=m(1.0))
    return r


def _tier_cap(big, tier_word, pal):
    """The floating tier tile: its OWN drop shadow so it hovers over the gap, a
    subtle deep -> gem tier gradient, and the tier word rendered large + dominant
    in cream with a deep tier keyline."""
    cap = pygame.Rect(m(CX - CAP_W // 2), m(CAP_Y), m(CAP_W), m(CAP_H))
    rad = m(CAP_RAD)
    # own shadow => reads as a separate element floating above the plate
    drop_shadow(big, cap, rad, blur=m(6), alpha=150, dy=m(3))
    # subtle tier gradient: lifted-deep at the crown easing to a muted gem foot
    cap_top = lerp_color(pal["deep"], pal["gem"], 0.24)
    cap_bot = lerp_color(pal["gem"], pal["deep"], 0.18)
    big.blit(vgrad_stops(cap.w, cap.h, rad, [(0.0, cap_top), (1.0, cap_bot)],
                         255, gamma=1.06), cap.topleft)
    top_sheen(big, cap, rad, m(14), peak=54)
    edge_dk = lerp_color(pal["deep"], NEAR_BLACK, 0.45)
    edge_br = lerp_color(pal["gem"], WHITE, 0.5)
    pygame.draw.rect(big, edge_dk, cap, width=max(1, m(1.6)), border_radius=rad)
    bevel_rim(big, cap, rad, edge_dk, (*edge_br, 210), w=max(1, m(1.4)))

    # tier word large + dominant, auto-shrunk to fit the tile width
    sz = 26
    lf = font(sz)
    while _glyph_base(tier_word, lf, m(1.6)).get_width() > cap.w - m(20) and sz > 10:
        sz -= 1
        lf = font(sz)
    plain_text(big, tier_word, lf, cap.center, (250, 248, 240),
               shadow_a=120, tracking=m(1.6), weight=m(1.4),
               keyline=lerp_color(pal["deep"], NEAR_BLACK, 0.35), kw=m(1.0))


def _body_plate(big, sid, price, pal):
    """The single continuous body-plus-foot slab: ONE uninterrupted obsidian
    vgrad carrying the disc up top and the price + confirm chips below. The
    disc's two-part rim glow lives entirely inside this surface, never in the
    gap above."""
    plate = pygame.Rect(m(PLATE_X), m(PLATE_Y), m(PLATE_W), m(PLATE_H))
    rad = m(PLATE_RAD)
    drop_shadow(big, plate, rad, blur=m(8), alpha=165, dy=m(4))
    big.blit(vgrad_stops(plate.w, plate.h, rad, [(0.0, CARD_T), (1.0, CARD_B)],
                         255, gamma=1.15), plate.topleft)
    top_sheen(big, plate, rad, m(30), peak=58)
    pygame.draw.rect(big, (4, 5, 16), plate, width=max(1, m(2)), border_radius=rad)
    bevel_rim(big, plate, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 230),
              w=max(1, m(1.9)))
    tray = plate.inflate(-m(8), -m(8))
    pygame.draw.rect(big, (*CARD_RING_BRIGHT, 60), tray, width=max(1, m(1)),
                     border_radius=rad - m(3))

    cx_dev, cy_dev = m(CX), m(CY_DISC)
    r = m(R_DISC)

    # ── two-part rim glow, PART 1: additive annular bloom in the tier glow.
    # Drawn BEFORE the disc so the disc covers the hot centre and only the outer
    # halo shows in open plate on both sides. BLEND_ADD ignores source alpha, so
    # the colour magnitude is kept LOW to stay a tinted bloom, not a white flare.
    bloom = tuple(int(c * 0.34) for c in pal["glow"])
    soft_glow(big, cx_dev, cy_dev, r + m(9), bloom, 40, layers=8)

    # cabochon dome + rim-lit hero + glass overlay (store-card DNA, tier-tinted)
    cabochon(big, cx_dev, cy_dev, r, CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    blit_thumb(big, sid, cx_dev, cy_dev, int(r * 1.5))
    cabochon_glass(big, cx_dev, cy_dev, r, tint=pal["gem"])

    # ── two-part rim glow, PART 2: crisp gem ring drawn ON TOP of the glass.
    ring_w = max(3, m(3.0))
    pygame.draw.circle(big, pal["gem"], (cx_dev, cy_dev),
                       r + ring_w // 2 + m(1), ring_w)
    pygame.draw.circle(big, lerp_color(pal["deep"], NEAR_BLACK, 0.35),
                       (cx_dev, cy_dev), r - m(1), max(1, m(1)))

    # lower half of the SAME slab: price then confirm
    price_chip(big, cx_dev, m(Y_PRICE), f"{price:,}", m(22), affordable=True)
    _confirm_chip(big, cx_dev, m(Y_CONFIRM), m(24))


def render_popup(tier_word, sid, price, pal):
    big = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)
    _tier_cap(big, tier_word, pal)
    _body_plate(big, sid, price, pal)
    return pygame.transform.smoothscale(big, (POP_W, POP_H))


# =============================================================================
# Review sheet — three tiers side by side over a modal-style scrim
# =============================================================================
GUT = 22
MARGIN = 24
HEAD = 58
CANVAS_W = MARGIN * 2 + POP_W * 3 + GUT * 2
CANVAS_H = HEAD + POP_H + 40

canvas = pygame.Surface((CANVAS_W, CANVAS_H))
# a scrim-ish backdrop so the cards read as the live confirm modal would
for y in range(CANVAS_H):
    t = y / CANVAS_H
    canvas.blit(pygame.Surface((CANVAS_W, 1)), (0, y))
    pygame.draw.line(canvas, lerp_color((10, 11, 26), (5, 5, 14), t),
                     (0, y), (CANVAS_W, y))

title = _font(19, True).render("confirm_purchase_v5 — capped-plate  (round 1)",
                               True, (232, 226, 208))
canvas.blit(title, (MARGIN, 16))
sub = _font(11, True).render(
    "two floating elements: tier-cap tile + connected body-plus-foot plate",
    True, (150, 156, 178))
canvas.blit(sub, (MARGIN, 38))

lab = _font(13, True)
for i, (tier_word, sid, price, pal) in enumerate(TIERS):
    pop = render_popup(tier_word, sid, price, pal)
    px = MARGIN + i * (POP_W + GUT)
    py = HEAD
    canvas.blit(pop, (px, py))
    t = lab.render(tier_word, True, lerp_color(pal["gem"], WHITE, 0.25))
    canvas.blit(t, t.get_rect(center=(px + POP_W // 2, py - 10)))

out = "/home/user/skybit/docs/confirm_purchase_v5/capped-plate/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(canvas, out)
print("saved", out, canvas.get_size())
