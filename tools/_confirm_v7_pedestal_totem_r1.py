#!/usr/bin/env python3
"""
pedestal-totem  ·  confirm_purchase_v7  ·  round 1

A vertical totem buy-confirm popup. The hero disc crowns the top; directly
beneath it a milled sovereign-coin medallion stands on a gold plinth. The two
circles rhyme on a single vertical axis but are told apart by construction: the
disc is glass + thumbnail, the coin is a reeded-edge strike carrying the price
numeral on its face. Three tiers rendered side by side for review.
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


# ── mandatory gloss_sweep patch (verbatim from v6 scaffold) ───────────────────
# BLEND_ADD reads RGB directly (source alpha is ignored), so sheen lives in the
# RGB channels of the sweep surface, not alpha.
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


# ── popup metrics (v7: taller totem) ──────────────────────────────────────────
POP_W, POP_H = 260, 442
CX = 130


# ── hero disc (crowns the totem) ──────────────────────────────────────────────
def hero_disc(big, sid, gx, gy, r, pal):
    """Glass cabochon carrying the real skin thumbnail — the totem's crown."""
    sc._alpha_aura(big, gx, gy, r + m(14), pal["glow"], peak=46, layers=15)
    sc.cabochon(big, gx, gy, r, CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    try:
        sc.blit_thumb(big, sid, gx, gy, int(r * 1.5))
    except Exception:
        # Skin surface unavailable → tinted gem stand-in so the disc still reads.
        pygame.draw.circle(big, pal["gem"], (gx, gy), int(r * 0.7))
    sc.cabochon_glass(big, gx, gy, r, tint=pal["gem"])


# ── milled sovereign coin (rhymes with the disc, told apart by construction) ──
def coin_medallion(big, price_str, pal):
    cx, cy = m(CX), m(228)
    r = m(32)

    # 1) the coin's own spotlight
    sc._alpha_aura(big, cx, cy, m(32 + 16), pal["glow"], peak=50, layers=15)

    # 2) reeded / milled edge — short radial ticks distinguish coin from disc
    tw = max(1, m(0.8))
    for i in range(48):
        ang = 2 * math.pi * i / 48
        ca, sa = math.cos(ang), math.sin(ang)
        x0 = cx + int(m(32) * ca)
        y0 = cy + int(m(32) * sa)
        x1 = cx + int(m(35) * ca)
        y1 = cy + int(m(35) * sa)
        col = CARD_RING_BRIGHT if i % 3 != 0 else pal["deep"]
        pygame.draw.line(big, col, (x0, y0), (x1, y1), tw)

    # 3) dark contact ring, 4) gold bezel ring
    pygame.draw.circle(big, (0, 0, 0, 180), (cx, cy), m(32), m(2))
    pygame.draw.circle(big, CARD_RING_BRIGHT + (220,), (cx, cy), m(31), m(2))

    # 5) the real in-game coin face
    sc.coin_glyph(big, cx, cy, m(28))

    # 6) price numeral struck on the coin face
    plain_text(big, price_str, font(13), (cx, m(232)), pal["gem"],
               shadow_a=0, weight=m(1.0), keyline=(10, 7, 3), kw=m(1.1))

    # 7) hot top-left specular pip
    pr = max(1, m(3))
    pip = pygame.Surface((pr * 2 + 2, pr * 2 + 2), pygame.SRCALPHA)
    pygame.draw.circle(pip, (255, 255, 255, 230), (pr + 1, pr + 1), pr)
    off = int(m(32) * 0.52)
    big.blit(pip, (cx - off - pr, cy - off - pr), special_flags=pygame.BLEND_ADD)


# ── gold plinth (the totem base the coin is seated on) ────────────────────────
def gold_plinth(big):
    """A tapering gold podium under the coin. Drawn AFTER the coin so the coin's
    foot tucks behind the podium lip and reads as seated on top."""
    top_y, h = m(252), m(30)
    pw = m(110)                         # bounding = widest (bottom) edge
    body = vgrad_stops(pw, h, 0,
                       [(0.0, (200, 170, 60)), (0.5, (120, 90, 20)),
                        (1.0, (60, 45, 10))], 255, gamma=1.1)
    # trapezoid: 90px top → 110px bottom, centred; local x0 of the plinth = m(75)
    poly = [(m(10), 0), (m(100), 0), (pw, h), (0, h)]
    pmask = pygame.Surface((pw, h), pygame.SRCALPHA)
    pygame.draw.polygon(pmask, (255, 255, 255, 255), poly)
    body.blit(pmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(body, (m(75), top_y))

    # dark elliptical cap along the top edge = the podium's depth
    ew, eh = m(90), m(8)
    cap = pygame.Surface((ew, eh), pygame.SRCALPHA)
    pygame.draw.ellipse(cap, (60, 45, 10, 180), cap.get_rect())
    big.blit(cap, (m(CX) - ew // 2, top_y - eh // 2))
    # bright gold lit lip riding the cap
    lip = pygame.Surface((ew, eh), pygame.SRCALPHA)
    pygame.draw.ellipse(lip, (*CARD_RING_BRIGHT, 220), lip.get_rect(),
                        max(1, m(1.2)))
    big.blit(lip, (m(CX) - ew // 2, top_y - eh // 2))


# ── rarity lozenge ────────────────────────────────────────────────────────────
def rarity_lozenge(big, tier_word, cy, pal):
    cx = m(CX)
    f = font(11)
    trk = m(2)
    tw = sc._glyph_base(tier_word, f, trk).get_width()
    pad = m(16)
    w = tw + pad * 2
    h = m(18)
    pt = h // 2
    x0, y0 = cx - w // 2, cy - h // 2
    poly = [(0, h // 2), (pt, 0), (w - pt, 0), (w, h // 2), (w - pt, h), (pt, h)]
    top = lerp_color(pal["gem"], WHITE, 0.12)
    bot = lerp_color(pal["deep"], NEAR_BLACK, 0.05)
    body = vgrad_stops(w, h, 0, [(0.0, top), (0.5, pal["glow"]), (1.0, bot)],
                       255, gamma=1.08)
    pmask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(pmask, (255, 255, 255, 255), poly)
    body.blit(pmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    sh = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(sh, (0, 0, 0, 120), poly)
    big.blit(sh, (x0, y0 + m(2)))
    big.blit(body, (x0, y0))
    abspoly = [(x0 + px, y0 + py) for px, py in poly]
    pygame.draw.polygon(big, (4, 5, 16), abspoly, width=max(1, m(1.4)))
    plain_text(big, tier_word, f, (cx, cy), (16, 12, 26), shadow_a=0,
               tracking=trk, weight=m(0.8))


# ── buttons ───────────────────────────────────────────────────────────────────
def slab_button(big, cx, cy, label, stops, bevel_alpha, label_col):
    w, h = m(106), m(46)
    r = pygame.Rect(m(cx) - w // 2, m(cy) - h // 2, w, h)
    rad = m(10)
    sc.drop_shadow(big, r, rad, blur=m(4), alpha=120, dy=m(2))
    big.blit(vgrad_stops(w, h, rad, stops, 255, gamma=1.06), r.topleft)
    _gloss_sweep_fixed(big, r, rad, peak=16)          # BLEND_ADD-safe on dark
    sc.contact_shadow(big, r, rad, m(3), alpha=70)
    pygame.draw.rect(big, (4, 5, 16), r, width=max(1, m(1.6)), border_radius=rad)
    sc.bevel_rim(big, r, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, bevel_alpha),
                 w=max(1, m(1.6)))
    plain_text(big, label, font(15), r.center, label_col, shadow_a=130,
               weight=m(1.0), keyline=(6, 6, 16), kw=m(1.0))


# ── one popup ─────────────────────────────────────────────────────────────────
def render_popup(tier_word, sid, price, pal):
    big = pygame.Surface((m(POP_W), m(POP_H)), pygame.SRCALPHA)

    # 1) card body
    rad = m(23)
    rect = pygame.Rect(m(10), m(127), m(240), m(309))
    sc.drop_shadow(big, rect, rad, blur=m(8), alpha=160, dy=m(4))
    big.blit(vgrad_stops(rect.w, rect.h, rad,
                         [(0.0, CARD_T), (1.0, CARD_B)], 252, gamma=1.15),
             rect.topleft)
    sc.top_sheen(big, rect, rad, m(30), peak=50)
    sc.contact_shadow(big, rect, rad, m(9), alpha=120)
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    sc.bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 235),
                 w=max(1, m(2.45)))

    # 2) hero disc crowning the top
    hero_disc(big, sid, m(CX), m(135), m(53), pal)

    # 3) sovereign coin medallion, then 4) the plinth it stands on
    coin_medallion(big, price, pal)
    gold_plinth(big)

    # 5) rarity → 6) name
    rarity_lozenge(big, tier_word, m(300), pal)
    plain_text(big, NAMES[tier_word], font(15), (m(CX), m(328)),
               (250, 248, 240), shadow_a=150, weight=m(0.9),
               keyline=(6, 6, 16), kw=m(1.0))

    # 7) buttons
    slab_button(big, 70, 392, "BUY",
                [(0.0, (55, 45, 12)), (0.5, (38, 30, 8)), (1.0, (24, 18, 4))],
                235, (255, 236, 180))
    slab_button(big, 190, 392, "CANCEL",
                [(0.0, (30, 26, 40)), (1.0, (18, 16, 28))],
                160, (216, 220, 234))

    return pygame.transform.smoothscale(big, (POP_W, POP_H))


# ── three-tier review sheet ───────────────────────────────────────────────────
GAP    = 12
MARGIN = 24
HEAD   = 58
CANVAS_W = MARGIN * 2 + POP_W * 3 + GAP * 2
CANVAS_H = HEAD + POP_H + 44

canvas = pygame.Surface((CANVAS_W, CANVAS_H))
canvas.fill((8, 8, 20))

title = _font(19, True).render(
    "confirm_purchase_v7  ·  pedestal-totem  ·  round 1", True, (232, 226, 208))
canvas.blit(title, (MARGIN, 14))
sub = _font(11, True).render(
    "vertical totem · glass hero disc crowns · milled sovereign coin on a gold plinth",
    True, (150, 156, 178))
canvas.blit(sub, (MARGIN, 38))

lab = _font(13, True)
for i, (word, sid, price, pal) in enumerate(TIERS):
    pop = render_popup(word, sid, price, pal)
    px = MARGIN + i * (POP_W + GAP)
    py = HEAD
    canvas.blit(pop, (px, py))
    t = lab.render(word, True, lerp_color(pal["gem"], WHITE, 0.25))
    canvas.blit(t, t.get_rect(midtop=(px + POP_W // 2, py + POP_H + 8)))

# ── crisp 2x export via PIL LANCZOS ───────────────────────────────────────────
OUT = "/home/user/skybit/docs/confirm_purchase_v7/pedestal-totem/round_1.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)
raw = pygame.image.tostring(canvas, "RGBA")
img = Image.frombytes("RGBA", canvas.get_size(), raw)
img = img.resize((canvas.get_width() * 2, canvas.get_height() * 2), Image.LANCZOS)
img.save(OUT)
print("saved", OUT, img.size)
