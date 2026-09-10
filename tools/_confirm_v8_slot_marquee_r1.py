#!/usr/bin/env python3
"""
slot-marquee  ·  confirm_purchase_v8  ·  round 1

Bottom zone concept: a dark recessed LED-credits marquee window holds the
inline coin+price, below it a domed BUY plunger, then a flat CANCEL capsule.
Name zone (cy=213) is completely clear.
"""
import os, sys, math
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

# ── tier palette ──────────────────────────────────────────────────────────────
TIERS = [
    ("RARE",      "skin_wizard",    "720",
     {"gem": (108, 188, 252), "glow": (60, 140, 230), "deep": (18, 44, 90)}),
    ("EPIC",      "skin_prism",     "1,400",
     {"gem": (194, 122, 248), "glow": (150, 60, 220), "deep": (44, 10, 80)}),
    ("LEGENDARY", "skin_astronaut", "2,600",
     {"gem": (255, 202, 104), "glow": (220, 160, 40), "deep": (90, 50, 0)}),
]
NAMES = {"RARE": "WIZARD", "EPIC": "PRISM", "LEGENDARY": "ASTRONAUT"}

# ── popup geometry ────────────────────────────────────────────────────────────
POP_W, POP_H = 260, 442
CX = 130

CARD_X, CARD_TOP_Y, CARD_W, CARD_H, CARD_RAD = 10, 127, 240, 299, 23
DISC_CY, DISC_R = 135, 53
GEM_L_X, GEM_R_X, GEM_CY, GEM_R = 43, 217, 152, 14

# bottom zone layout (all y in logical px)
MARQUEE_CY, MARQUEE_W, MARQUEE_H = 284, 216, 36   # y=266→302
BUY_CY,     BUY_W,     BUY_H     = 342, 154, 46   # y=319→365
CANCEL_CY,  CAN_W,     CAN_H     = 389, 154, 28   # y=375→403


# ── shared chrome helpers ─────────────────────────────────────────────────────
def card_body(big):
    rect = pygame.Rect(m(CARD_X), m(CARD_TOP_Y), m(CARD_W), m(CARD_H))
    rad  = m(CARD_RAD)
    sc.drop_shadow(big, rect, rad, blur=m(8), alpha=165, dy=m(4))
    big.blit(vgrad_stops(rect.w, rect.h, rad,
                         [(0.0, CARD_T), (1.0, CARD_B)], 255, gamma=1.15),
             rect.topleft)
    sc.top_sheen(big, rect, rad, m(30), peak=56)
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    sc.bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 230),
                 w=max(1, m(1.9)))
    tray = rect.inflate(-m(8), -m(8))
    pygame.draw.rect(big, (*CARD_RING_BRIGHT, 55), tray, width=max(1, m(1)),
                     border_radius=rad - m(3))


def corner_gems(big, pal):
    sc.facet_gem(big, m(GEM_L_X), m(GEM_CY), m(GEM_R), pal["gem"], pal["deep"])
    sc.facet_gem(big, m(GEM_R_X), m(GEM_CY), m(GEM_R), pal["gem"], pal["deep"])


def name_text(big, name):
    y_log, min_fs = 213, 24
    nfs  = 45
    nfnt = font(nfs)
    mw   = m(CARD_W - 20)
    while sc._glyph_base(name, nfnt, 0).get_width() > mw and nfs > min_fs:
        nfs -= 1
        nfnt = font(nfs)
    plain_text(big, name, nfnt, (m(CX), m(y_log)), (250, 248, 240),
               shadow_a=160, weight=m(0.9), keyline=(6, 6, 16), kw=m(1.0))


def rarity_banner(big, tier_word, pal):
    cx, cy_log, w_log, h_log = CX, 247, 156, 23
    f   = font(h_log * 0.58)
    tw  = sc._glyph_base(tier_word, f, m(1.4)).get_width()
    w   = min(m(w_log), tw + m(16) * 2)
    h   = m(h_log)
    pt  = h // 2
    x0, y0 = m(cx) - w // 2, m(cy_log) - h // 2
    poly = [(0,h//2),(pt,0),(w-pt,0),(w,h//2),(w-pt,h),(pt,h)]
    top = lerp_color(pal["gem"], WHITE, 0.1)
    bot = lerp_color(pal["deep"], NEAR_BLACK, 0.05)
    body = vgrad_stops(w, h, 0, [(0.0,top),(0.5,pal["glow"]),(1.0,bot)], 255, gamma=1.08)
    pmask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(pmask, (255,255,255,255), poly)
    body.blit(pmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    sh = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(sh, (0, 0, 0, 120), poly)
    big.blit(sh, (x0, y0 + m(2)))
    big.blit(body, (x0, y0))
    abspoly = [(x0+px, y0+py) for px, py in poly]
    pygame.draw.polygon(big, (4, 5, 16), abspoly, width=max(1, m(1.4)))
    plain_text(big, tier_word, f, (m(cx), m(cy_log)), (14, 12, 26),
               shadow_a=0, tracking=m(1.4), weight=m(0.7))


def hero_disc(big, sid, pal):
    cx, cy, r = m(CX), m(DISC_CY), m(DISC_R)
    sc._alpha_aura(big, cx, cy, r + m(18), pal["glow"], peak=52, layers=15)
    sc.cabochon(big, cx, cy, r, CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    try:
        sc.blit_thumb(big, sid, cx, cy, int(r * 1.5))
    except Exception:
        pygame.draw.circle(big, pal["gem"], (cx, cy), int(r * 0.7))
    sc.cabochon_glass(big, cx, cy, r, tint=pal["gem"])
    ring_w = max(3, m(3.0))
    pygame.draw.circle(big, pal["gem"], (cx, cy), r + ring_w // 2 + m(1), ring_w)


# ── concept-specific bottom zone ──────────────────────────────────────────────
def coin_price_inline(big, cx, cy, price_str, coin_r=11, gap=5,
                      text_col=(234, 218, 168), text_size=12):
    f   = font(text_size)
    tw  = sc._glyph_base(price_str, f, 0).get_width()
    grp = m(coin_r) * 2 + m(gap) + tw
    coin_cx = cx - grp // 2 + m(coin_r)
    text_cx = coin_cx + m(coin_r) + m(gap) + tw // 2
    sc.coin_glyph(big, coin_cx, cy, m(coin_r))
    plain_text(big, price_str, f, (text_cx, cy), text_col,
               shadow_a=110, weight=m(0.9), keyline=(20, 14, 4), kw=m(0.8))


def marquee_window(big, price_str):
    """Dark recessed LED-credits window holding coin+price inline."""
    cx  = m(CX)
    cy  = m(MARQUEE_CY)
    w   = m(MARQUEE_W)
    h   = m(MARQUEE_H)
    rad = m(7)
    x0  = cx - w // 2
    y0  = cy - h // 2
    rect = pygame.Rect(x0, y0, w, h)

    # deep dark recess body
    big.blit(vgrad_stops(w, h, rad,
                         [(0.0, (10, 8, 4)), (1.0, (22, 17, 8))], 255, gamma=1.0),
             rect.topleft)

    # inset shadow rim (recess reads as sunken)
    inner_shadow = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(inner_shadow, (0, 0, 0, 80), inner_shadow.get_rect(),
                     width=max(1, m(2)), border_radius=rad)
    big.blit(inner_shadow, rect.topleft)

    # warm amber glow leaking from the LED display
    glow_s = pygame.Surface((w + m(16), h + m(16)), pygame.SRCALPHA)
    for i in range(6, 0, -1):
        alpha = int(28 * i / 6)
        pygame.draw.rect(glow_s, (200, 140, 40, alpha),
                         pygame.Rect(m(8) - i, m(8) - i, w + i * 2, h + i * 2),
                         border_radius=rad + i)
    big.blit(glow_s, (x0 - m(8), y0 - m(8)))

    # outer bevel rim (gold edge seating the window)
    sc.bevel_rim(big, rect, rad, (30, 20, 6), (200, 155, 60, 210), w=max(1, m(1.4)))

    # scanline overlay (subtle alternating rows dim every 2nd px)
    scan = pygame.Surface((w, h), pygame.SRCALPHA)
    for row in range(0, h, 2):
        pygame.draw.line(scan, (0, 0, 0, 28), (0, row), (w, row))
    big.blit(scan, rect.topleft)

    # coin + price inline, centred in the window
    coin_price_inline(big, cx, cy, price_str,
                      coin_r=10, gap=6, text_col=(240, 218, 148), text_size=12)


def buy_plunger(big, pal):
    """Domed BUY plunger — warm gold, prominent, with cabochon-style top sheen."""
    cx  = m(CX)
    cy  = m(BUY_CY)
    w   = m(BUY_W)
    h   = m(BUY_H)
    rad = m(BUY_H // 2)   # full pill ends
    x0  = cx - w // 2
    y0  = cy - h // 2
    rect = pygame.Rect(x0, y0, w, h)

    # drop shadow for depth
    sc.drop_shadow(big, rect, rad, blur=m(5), alpha=140, dy=m(4))

    # warm gold gradient body
    big.blit(vgrad_stops(w, h, rad,
                         [(0.0, (175, 128, 38)),
                          (0.4, (130, 90, 22)),
                          (1.0, (72, 48, 10))], 255, gamma=1.1),
             rect.topleft)

    # prominent top sheen (domed highlight)
    sc.top_sheen(big, rect, rad, m(24), peak=72)
    sc.gloss_sweep(big, rect, rad, peak=52)

    # tight bright rim
    sc.bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 235),
                 w=max(1, m(1.8)))

    # BUY label
    plain_text(big, "BUY", font(15), rect.center, (255, 246, 210),
               shadow_a=160, tracking=m(1.4), weight=m(1.2),
               keyline=(60, 38, 6), kw=m(1.0))


def cancel_capsule(big):
    """Flat matte CANCEL capsule — low-key secondary action."""
    cx  = m(CX)
    cy  = m(CANCEL_CY)
    w   = m(CAN_W)
    h   = m(CAN_H)
    rad = m(CAN_H // 2)
    x0  = cx - w // 2
    y0  = cy - h // 2
    rect = pygame.Rect(x0, y0, w, h)

    sc.drop_shadow(big, rect, rad, blur=m(3), alpha=80, dy=m(2))
    big.blit(vgrad_stops(w, h, rad,
                         [(0.0, (28, 26, 44)), (1.0, (18, 16, 30))], 255, gamma=1.0),
             rect.topleft)
    sc.top_sheen(big, rect, rad, m(10), peak=14)
    sc.bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 170),
                 w=max(1, m(1.2)))
    plain_text(big, "CANCEL", font(11), rect.center, (176, 172, 204),
               shadow_a=100, tracking=m(1.2), weight=m(0.8),
               keyline=(6, 6, 16), kw=m(0.6))


# ── popup render ──────────────────────────────────────────────────────────────
def render_popup(tier_word, sid, price, pal):
    big = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)
    card_body(big)
    corner_gems(big, pal)
    name_text(big, NAMES[tier_word])
    rarity_banner(big, tier_word, pal)
    marquee_window(big, price)
    buy_plunger(big, pal)
    cancel_capsule(big)
    hero_disc(big, sid, pal)   # drawn last — crowns the card
    return pygame.transform.smoothscale(big, (POP_W, POP_H))


# ── 3-tier strip ──────────────────────────────────────────────────────────────
MARGIN, HEAD, GAP = 20, 58, 12
CANVAS_W = MARGIN * 2 + POP_W * 3 + GAP * 2
CANVAS_H = HEAD + POP_H + 40

canvas = pygame.Surface((CANVAS_W, CANVAS_H))
canvas.fill((8, 8, 20))

hdr  = _font(17, True).render("confirm_purchase_v8  ·  slot-marquee  ·  round 1", True, (232, 226, 208))
sub1 = _font(10, True).render("LED marquee window (coin+price inline) · domed BUY plunger · flat CANCEL capsule", True, (140, 148, 168))
canvas.blit(hdr,  (MARGIN, 12))
canvas.blit(sub1, (MARGIN, 33))

lab = _font(13, True)
for i, (word, sid, price, pal) in enumerate(TIERS):
    pop = render_popup(word, sid, price, pal)
    px  = MARGIN + i * (POP_W + GAP)
    py  = HEAD
    canvas.blit(pop, (px, py))
    t = lab.render(word, True, lerp_color(pal["gem"], WHITE, 0.25))
    canvas.blit(t, t.get_rect(midtop=(px + POP_W // 2, py + POP_H + 6)))

# PIL 2× LANCZOS for review
raw  = pygame.image.tostring(canvas, "RGB")
pil  = Image.frombytes("RGB", (CANVAS_W, CANVAS_H), raw)
out2 = pil.resize((CANVAS_W * 2, CANVAS_H * 2), Image.LANCZOS)

OUT = "/home/user/skybit/docs/confirm_purchase_v8/slot-marquee/round_1.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)
out2.save(OUT)
print(f"saved {out2.size[0]}×{out2.size[1]}  →  {OUT}")
