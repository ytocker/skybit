#!/usr/bin/env python3
"""
coin-collar-halo  ·  confirm_purchase_v7  ·  round 1

Couture jewellery as UI: a jewelled collar clasps a large centrepiece coin
below the hero disc. The coin — promoted from a small pendant to the collar's
dominant centrepiece jewel (r=39) — is the HERO of this lower zone; the collar
is a thin, tiny-gem band that FRAMES it and never competes. A large spotlight
aura under the coin bridges up to the disc so the two hero reads feel like one
lit column. The collar is a 240 arc open at the TOP so it wraps under/around
the coin without hiding the disc above.
"""
import os
import math

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import sys
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


# ── mandatory gloss_sweep patch (verbatim from v6 scaffold) ───────────────────
# BLEND_ADD reads RGB directly (source alpha is ignored), so sheen lives in the
# RGB channels of the sweep surface, not alpha — else a near-black enamel body
# blows to white under the additive blit.
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


# ── tier palette (brief-exact) ────────────────────────────────────────────────
TIERS = [
    ("RARE",      "skin_wizard",    "720",
     {"gem": (108, 188, 252), "glow": (60, 140, 230), "deep": (18, 44, 90)}),
    ("EPIC",      "skin_prism",     "1,400",
     {"gem": (194, 122, 248), "glow": (150, 60, 220), "deep": (44, 10, 80)}),
    ("LEGENDARY", "skin_astronaut", "2,600",
     {"gem": (255, 202, 104), "glow": (220, 160, 40), "deep": (90, 50, 0)}),
]
NAMES = {"RARE": "WIZARD", "EPIC": "PRISM", "LEGENDARY": "ASTRONAUT"}


# ── popup metrics (logical px; flow through m()) ──────────────────────────────
POP_W, POP_H = 260, 442
CX = 130

CARD_L, CARD_T_Y = 10, 127
CARD_R, CARD_B_Y = 250, 436
CARD_RAD = 23

DISC_CY, DISC_R = 135, 53

COIN_CY, COIN_R = 230, 39
COLLAR_R = 59          # tiny-gem stud centre radius from coin centre
BAND_R = 58            # gold band the studs sit on

Y_LOZ = 302
Y_NAME = 330
Y_BTN = 392


# ── card body ─────────────────────────────────────────────────────────────────
def card_body(big):
    rect = pygame.Rect(m(CARD_L), m(CARD_T_Y),
                       m(CARD_R - CARD_L), m(CARD_B_Y - CARD_T_Y))
    rad = m(CARD_RAD)
    sc.drop_shadow(big, rect, rad, blur=m(8), alpha=165, dy=m(4))
    big.blit(vgrad_stops(rect.w, rect.h, rad, [(0.0, CARD_T), (1.0, CARD_B)],
                         255, gamma=1.15), rect.topleft)
    sc.top_sheen(big, rect, rad, m(30), peak=56)
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    sc.bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 230),
                 w=max(1, m(1.9)))


# ── standard hero disc ─────────────────────────────────────────────────────────
def hero_disc(big, sid, pal):
    cx, cy, r = m(CX), m(DISC_CY), m(DISC_R)
    sc._alpha_aura(big, cx, cy, r + m(18), pal["glow"], peak=52, layers=15)
    sc.cabochon(big, cx, cy, r, CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    sc.blit_thumb(big, sid, cx, cy, int(r * 1.5))
    sc.cabochon_glass(big, cx, cy, r, tint=pal["gem"])
    ring_w = max(3, m(3.0))
    pygame.draw.circle(big, pal["gem"], (cx, cy), r + ring_w // 2 + m(1), ring_w)


# ── the centrepiece jewel: the coin, promoted to the collar's dominant stone ────
def centrepiece_coin(big, price, pal):
    cx, cy = m(CX), m(COIN_CY)

    # 1) large spotlight aura matching the disc's glow — the top of this bloom
    #    (coin top ~191) bridges up to the disc bottom (188) so the two heroes
    #    read as one lit column.
    sc._alpha_aura(big, cx, cy, m(COIN_R + 16), pal["glow"], peak=60, layers=16)

    # 2) full gold bevel ring (the disc's glass-bezel language, scaled to r=39):
    #    dark contact ring, warm gold ring, pale inner glint.
    pygame.draw.circle(big, (0, 0, 0, 190), (cx, cy), m(40), m(3))
    pygame.draw.circle(big, (*CARD_RING_BRIGHT, 230), (cx, cy), m(39), m(2))
    pygame.draw.circle(big, (246, 220, 140, 130), (cx, cy), m(37), m(1))

    # 3) the coin face fills inside the bevel
    sc.coin_glyph(big, cx, cy, m(37))

    # 4) top-left specular pip — the freshly-minted coin catches the light
    pr = m(4)
    pip = pygame.Surface((pr * 2 + 2, pr * 2 + 2), pygame.SRCALPHA)
    pygame.draw.circle(pip, (255, 255, 255, 255), (pr + 1, pr + 1), pr)
    big.blit(pip, (m(118) - pr - 1, m(218) - pr - 1),
             special_flags=pygame.BLEND_ADD)

    # 5) struck price numeral, centred slightly below the coin centre
    plain_text(big, price, font(13), (cx, m(234)), CARD_RING_BRIGHT,
               shadow_a=150, weight=m(1.0), keyline=(70, 52, 8), kw=m(0.9))


# ── the collar: a thin tiny-gem band framing the coin (240 arc, open at top) ────
def collar(big, pal):
    cx, cy = m(CX), m(COIN_CY)
    # A 240 sweep from the upper-right (-30), down through the bottom (90), up to
    # the upper-left (210) — the gap sits at the TOP so the collar wraps UNDER
    # the coin without reaching up to veil the disc.
    a0, a1 = -30.0, 210.0

    # thin gold collar band the studs sit on — drawn on a temp surface so its
    # alpha composites over the card face instead of punching through it.
    band = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pts = []
    steps = 96
    for k in range(steps + 1):
        a = math.radians(a0 + (a1 - a0) * k / steps)
        pts.append((cx + m(BAND_R) * math.cos(a), cy + m(BAND_R) * math.sin(a)))
    pygame.draw.lines(band, (*CARD_RING_BRIGHT, 180), False, pts, max(1, m(2)))
    big.blit(band, (0, 0))

    # ~10 tiny faceted studs seated on the band — small so they FRAME, never
    # compete with, the centrepiece coin.
    for i in range(10):
        a = math.radians(a0 + (a1 - a0) * i / 9)
        sx = int(cx + m(COLLAR_R) * math.cos(a))
        sy = int(cy + m(COLLAR_R) * math.sin(a))
        sc.facet_gem(big, sx, sy, m(5), pal["gem"], pal["deep"])


# ── rarity lozenge ──────────────────────────────────────────────────────────────
def rarity_lozenge(big, tier_word, pal):
    cx, cy = m(CX), m(Y_LOZ)
    w, h = m(116), m(26)
    notch = m(6)
    x0, y0 = cx - w // 2, cy - h // 2
    stops = [(0.0, pal["gem"]), (0.5, pal["glow"]), (1.0, pal["deep"])]
    body = vgrad_stops(w, h, 0, stops, 255, gamma=1.08)
    poly = [(notch, 0), (w - notch, 0), (w, h // 2), (w - notch, h),
            (notch, h), (0, h // 2)]
    pmask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(pmask, (255, 255, 255, 255), poly)
    body.blit(pmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    sh = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(sh, (0, 0, 0, 130), poly)
    big.blit(sh, (x0, y0 + m(2)))
    big.blit(body, (x0, y0))
    abspoly = [(x0 + px, y0 + py) for px, py in poly]
    pygame.draw.polygon(big, (6, 6, 16), abspoly, width=max(1, m(1.6)))
    edge_br = lerp_color(pal["gem"], WHITE, 0.5)
    inpoly = [(x0 + px + (1 if px < w / 2 else -1) * m(1.6),
               y0 + py + (1 if py < h / 2 else -1) * m(1.2)) for px, py in poly]
    pygame.draw.polygon(big, (*edge_br, 150), inpoly, width=max(1, m(1)))
    fsz = 12
    f = font(fsz)
    while sc._glyph_base(tier_word, f, m(1.6)).get_width() > w - notch * 2 - m(8) \
            and fsz > 6:
        fsz -= 0.5
        f = font(fsz)
    plain_text(big, tier_word, f, (cx, cy), (250, 248, 240),
               shadow_a=150, tracking=m(1.6), weight=m(1.0),
               keyline=(10, 10, 22), kw=m(0.8))


# ── buttons: 106x46 pill-rect (radius m(12)) ─────────────────────────────────────
def pill_button(big, cx, label, stops, bevel_bright, label_c, gloss):
    w, h = m(106), m(46)
    rad = m(12)
    rect = pygame.Rect(m(cx) - w // 2, m(Y_BTN) - h // 2, w, h)
    body = vgrad_stops(w, h, rad, stops, 255, gamma=1.1)
    sh = pygame.Surface((w, h + m(3)), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 120), (0, m(3), w, h), border_radius=rad)
    big.blit(sh, (rect.x, rect.y))
    big.blit(body, rect.topleft)
    sc.gloss_sweep(big, rect, rad, peak=gloss)
    sc.bevel_rim(big, rect, rad, CARD_RING_DEEP, bevel_bright, w=max(1, m(1.6)))
    plain_text(big, label, font(14), rect.center, label_c,
               shadow_a=170, tracking=m(1.2), weight=m(1.0),
               keyline=(6, 6, 16), kw=m(0.9))


# ── popup ───────────────────────────────────────────────────────────────────────
def render_popup(tier_word, sid, price, pal):
    big = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)
    card_body(big)
    centrepiece_coin(big, price, pal)
    collar(big, pal)
    rarity_lozenge(big, tier_word, pal)
    plain_text(big, NAMES[tier_word], font(15), (m(CX), m(Y_NAME)),
               (250, 248, 240), shadow_a=160, weight=m(0.9),
               keyline=(6, 6, 16), kw=m(1.0))
    pill_button(big, 70, "BUY",
                [(0.0, (55, 45, 12)), (1.0, (30, 24, 6))],
                (*CARD_RING_BRIGHT, 230), (255, 244, 210), gloss=42)
    pill_button(big, 190, "CANCEL",
                [(0.0, (30, 26, 40)), (1.0, (18, 16, 28))],
                (*CARD_RING_BRIGHT, 160), (226, 222, 234), gloss=16)
    # disc drawn last so its overhanging aura crowns the card unclipped
    hero_disc(big, sid, pal)
    return pygame.transform.smoothscale(big, (POP_W, POP_H))


# ── surface -> PIL (RGBA so transparent overhang composites onto the canvas) ────
def surf_to_pil(surf):
    w, h = surf.get_size()
    raw = pygame.image.tostring(surf, "RGBA")
    return Image.frombytes("RGBA", (w, h), raw)


def panel_2x(tier_word, sid, price, pal):
    popup_1x = render_popup(tier_word, sid, price, pal)
    pil = surf_to_pil(popup_1x)
    return pil.resize((POP_W * 2, POP_H * 2), Image.LANCZOS)


# ── three-tier review sheet (canvas 8,8,20 · 12 px gaps, at 2x panel scale) ─────
PW, PH = POP_W * 2, POP_H * 2
GAP = 24
MARGIN = 40
HEAD = 116
LABEL_H = 64
CANVAS_W = MARGIN * 2 + PW * 3 + GAP * 2
CANVAS_H = HEAD + PH + LABEL_H

canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), (8, 8, 20))

title = _font(34, True).render(
    "confirm_purchase_v7  ·  coin-collar-halo  ·  round 1", True, (232, 226, 208))
sub = _font(21, True).render(
    "couture jewellery as UI — coin promoted to the collar's dominant "
    "centrepiece jewel · thin tiny-gem collar frames it · 260x442",
    True, (150, 156, 178))
canvas.paste(surf_to_pil(title), (MARGIN, 30), surf_to_pil(title))
canvas.paste(surf_to_pil(sub), (MARGIN, 76), surf_to_pil(sub))

lab = _font(26, True)
for i, (word, sid, price, pal) in enumerate(TIERS):
    panel = panel_2x(word, sid, price, pal)
    px = MARGIN + i * (PW + GAP)
    py = HEAD
    canvas.paste(panel, (px, py), panel)
    tcol = lerp_color(pal["gem"], WHITE, 0.25)
    tsurf = lab.render(word, True, tcol)
    tpil = surf_to_pil(tsurf)
    tx = px + PW // 2 - tsurf.get_width() // 2
    canvas.paste(tpil, (tx, py + PH + 14), tpil)

OUT = "/home/user/skybit/docs/confirm_purchase_v7/coin-collar-halo/round_1.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)
canvas.save(OUT)
print("saved", OUT, canvas.size)
