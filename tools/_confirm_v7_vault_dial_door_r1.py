#!/usr/bin/env python3
"""
vault-dial-door  ·  confirm_purchase_v7  ·  round 1

The lower card body is a vaulted dial plate and the coin IS the combination
dial: concentric gold rings, faceted gem tick studs, and a large coin face make
the price treatment the most physically grandiose in the set. Everything is
built in Skybit's jewelled card vocabulary (faceted gems, bevel_rim gold rings,
_alpha_aura) — no brushed steel, no rivets.
"""
import os
import sys
import math

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

sys.path.insert(0, "/home/user/skybit")

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

import game.store_cards as sc
from game.store_cards import (
    vgrad_stops, plain_text, m, SS, font,
    CABO_LO, CABO_HI, CARD_T, CARD_B, CARD_RING_BRIGHT, CARD_RING_DEEP,
)
from game.hud import _font
from game.draw import lerp_color, NEAR_BLACK, WHITE
from PIL import Image


# ── mandatory gloss_sweep patch ───────────────────────────────────────────────
# BLEND_ADD reads RGB directly (source alpha is ignored), so the sheen amount
# must live in the RGB channels of the sweep surface, not its alpha — otherwise
# a near-black button body blows straight to white.
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


# ── popup metrics ─────────────────────────────────────────────────────────────
POP_W, POP_H = 260, 442
CX = 130

TIERS = [
    ("RARE", "skin_wizard", "720", "WIZARD",
     {"gem": (108, 188, 252), "glow": (60, 140, 230), "deep": (18, 44, 90)}),
    ("EPIC", "skin_prism", "1,400", "PRISM",
     {"gem": (194, 122, 248), "glow": (150, 60, 220), "deep": (44, 10, 80)}),
    ("LEGENDARY", "skin_astronaut", "2,600", "ASTRONAUT",
     {"gem": (255, 202, 104), "glow": (220, 160, 40), "deep": (90, 50, 0)}),
]


# ── hero disc (the item) ──────────────────────────────────────────────────────
def hero_disc(base, sid, gx, gy, r, pal):
    """Standard cabochon hero: aura bed, glass well, rim-lit skin, gold bezel."""
    sc._alpha_aura(base, gx, gy, r + m(14), pal["glow"], peak=40, layers=16)
    sc.cabochon(base, gx, gy, r, CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    sc.blit_thumb(base, sid, gx, gy, int(r * 1.5))
    sc.cabochon_glass(base, gx, gy, r, tint=pal["gem"])
    ring_w = max(3, m(3.0))
    pygame.draw.circle(base, pal["gem"], (gx, gy), r + ring_w // 2 + m(1), ring_w)
    pygame.draw.circle(base, lerp_color(pal["deep"], NEAR_BLACK, 0.35),
                       (gx, gy), r - m(1), max(1, m(1)))


# ── the dial (coin as combination dial) ───────────────────────────────────────
def vault_dial(base, price, pal):
    """The coin seated inside concentric gold rings + faceted gem tick studs —
    the combination dial. Rings and studs speak the card's jewelled vocabulary
    (bevel_rim gold, facet_gem) rather than any brushed-steel mechanical read."""
    cx, cy = m(CX), m(227)

    # 1) glow bed under the whole dial
    sc._alpha_aura(base, cx, cy, m(44 + 18), pal["glow"], peak=55, layers=16)

    # 2) concentric gold rings — the dial structure in card gold
    pygame.draw.circle(base, (4, 5, 16), (cx, cy), m(45), m(3))            # dark contact
    pygame.draw.circle(base, CARD_RING_BRIGHT + (230,), (cx, cy), m(44), m(2))  # bright outer rim
    pygame.draw.circle(base, (8, 10, 26), (cx, cy), m(40), m(3))           # recessed valley
    pygame.draw.circle(base, CARD_RING_BRIGHT + (180,), (cx, cy), m(38), m(1))  # inner gold ring
    pygame.draw.circle(base, (12, 14, 36), (cx, cy), m(36))                # dial face background

    # 3) faceted gem tick studs at the 12 clock positions (jewelled ticks)
    for i in range(12):
        a = math.radians(-90 + 360 * i / 12)
        cx_s = int(cx + m(41) * math.cos(a))
        cy_s = int(cy + m(41) * math.sin(a))
        sc.facet_gem(base, cx_s, cy_s, m(4), pal["gem"], pal["deep"])

    # 4) the real coin face — the dial's centre
    sc.coin_glyph(base, cx, cy, m(26))

    # 5) gold price numeral struck on the dark dial face
    plain_text(base, price, font(12), (m(CX), m(230)), CARD_RING_BRIGHT,
               shadow_a=150, weight=m(1.0), keyline=(6, 6, 16), kw=m(1.0))

    # 6) hot top-left specular pip on the coin so it reads as polished metal
    pr = m(4)
    pip = pygame.Surface((pr * 2 + 2, pr * 2 + 2), pygame.SRCALPHA)
    pygame.draw.circle(pip, (255, 255, 255, 235), (pr + 1, pr + 1), pr)
    base.blit(pip, (cx - m(11) - pr, cy - m(11) - pr), special_flags=pygame.BLEND_ADD)


# ── lever-pill buttons ────────────────────────────────────────────────────────
def lever_button(base, cx, cy, label, stops, bevel_col, bevel_a=255):
    """Full-pill action lever — dark contact keyline under a bright top-left
    bevel, one gloss sweep, and a cream label. The gold BUY vs. dark CANCEL
    split reads as commit vs. dismiss at a glance."""
    w, h = m(106), m(44)
    rad = m(22)
    r = pygame.Rect(cx - w // 2, cy - h // 2, w, h)

    sc.drop_shadow(base, r, rad, blur=m(5), alpha=120, dy=m(2))
    base.blit(vgrad_stops(w, h, rad, stops, 255, gamma=1.05), r.topleft)
    sc.gloss_sweep(base, r, rad, peak=20)
    sc.contact_shadow(base, r, rad, m(3), alpha=80)
    pygame.draw.rect(base, (4, 5, 16), r, width=max(1, m(1.6)), border_radius=rad)
    bev = bevel_col if bevel_a >= 255 else (*bevel_col, bevel_a)
    sc.bevel_rim(base, r, rad, (4, 5, 16), bev, w=max(1, m(1.6)))

    plain_text(base, label, font(14), (cx, cy), (250, 248, 240),
               shadow_a=150, weight=m(1.0), keyline=(6, 6, 16), kw=m(1.0))


# ── popup ─────────────────────────────────────────────────────────────────────
def render_popup(tier_word, sid, price, name, pal):
    big = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)

    # card body — vaulted dial plate
    rad = m(23)
    rect = pygame.Rect(m(10), m(127), m(240), m(309))
    sc.drop_shadow(big, rect, rad, blur=m(9), alpha=160, dy=m(4))
    big.blit(vgrad_stops(rect.w, rect.h, rad, [(0.0, CARD_T), (1.0, CARD_B)],
                         252, gamma=1.15), rect.topleft)
    sc.top_sheen(big, rect, rad, m(34), peak=60)
    sc.contact_shadow(big, rect, rad, m(11), alpha=120)
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    sc.bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 235),
                 w=max(1, m(2.45)))

    # hero disc — overhangs the plate top edge
    hero_disc(big, sid, m(CX), m(135), m(53), pal)

    # the dial (coin combination lock as the price treatment)
    vault_dial(big, price, pal)

    # rarity lozenge -> item name
    sc._ribbon_lozenge(big, tier_word, m(CX), m(300), m(240 - 34), pal)
    plain_text(big, name, font(15), (m(CX), m(328)), (250, 248, 240),
               shadow_a=160, weight=m(0.9), keyline=(6, 6, 16), kw=m(1.0))

    # action levers
    lever_button(big, m(70), m(392), "BUY",
                 [(0, (55, 45, 12)), (1, (30, 24, 6))], CARD_RING_BRIGHT)
    lever_button(big, m(190), m(392), "CANCEL",
                 [(0, (30, 26, 40)), (1, (18, 16, 28))], CARD_RING_BRIGHT, bevel_a=160)

    return pygame.transform.smoothscale(big, (POP_W, POP_H))


# ── surface -> PIL ────────────────────────────────────────────────────────────
def to_pil(surf):
    data = pygame.image.tostring(surf, "RGBA")
    return Image.frombytes("RGBA", surf.get_size(), data)


# ── three-tier review sheet ───────────────────────────────────────────────────
MARGIN = 44
GAP = 44
HEAD = 108
FOOT = 64
POP2W, POP2H = POP_W * 2, POP_H * 2       # final popup size after LANCZOS 2x

CANVAS_W = MARGIN * 2 + POP2W * 3 + GAP * 2
CANVAS_H = HEAD + POP2H + FOOT

sheet = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 255))
px = sheet.load()
for y in range(CANVAS_H):
    c = lerp_color((11, 12, 27), (5, 5, 14), y / CANVAS_H)
    for x in range(CANVAS_W):
        px[x, y] = (c[0], c[1], c[2], 255)

for i, (word, sid, price, name, pal) in enumerate(TIERS):
    pop = render_popup(word, sid, price, name, pal)
    pil = to_pil(pop).resize((POP2W, POP2H), Image.LANCZOS)
    x = MARGIN + i * (POP2W + GAP)
    sheet.alpha_composite(pil, (x, HEAD))

# headings + per-tier labels via a pygame text strip composited on top
txt = pygame.Surface((CANVAS_W, CANVAS_H), pygame.SRCALPHA)
title = _font(34, True).render(
    "confirm_purchase_v7  ·  vault-dial-door  ·  round 1", True, (232, 226, 208))
txt.blit(title, (MARGIN, 30))
sub = _font(20, True).render(
    "coin IS the combination dial · concentric gold rings + faceted gem tick studs · lever-pill actions",
    True, (150, 156, 178))
txt.blit(sub, (MARGIN, 72))

lab = _font(24, True)
for i, (word, sid, price, name, pal) in enumerate(TIERS):
    x = MARGIN + i * (POP2W + GAP)
    col = lerp_color(pal["gem"], WHITE, 0.25)
    t = lab.render(word, True, col)
    txt.blit(t, t.get_rect(midtop=(x + POP2W // 2, HEAD + POP2H + 16)))

sheet.alpha_composite(to_pil(txt), (0, 0))

OUT = "/home/user/skybit/docs/confirm_purchase_v7/vault-dial-door/round_1.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)
sheet.convert("RGB").save(OUT)
print("saved", OUT, sheet.size)
