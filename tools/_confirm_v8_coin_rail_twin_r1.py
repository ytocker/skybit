#!/usr/bin/env python3
"""
coin-rail-twin  ·  confirm_purchase_v8  ·  round 1

Bottom zone: a slim rail cartouche holds coin+price inline just below the
rarity banner; two polished gemstone button-plates (BUY warmer/brighter,
CANCEL cooler) sit side-by-side with a minimum 14px gutter.
"""
import os, sys
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

# bottom zone (logical px)
RAIL_CY, RAIL_W, RAIL_H = 276, 164, 26    # slim cartouche, y=263→289
BTN_CY,  BTN_W,  BTN_H  = 368, 104, 46   # gem plates, y=345→391
BTN_GAP  = 14                             # ≥14px gutter enforced
BUY_CX   = CX - (BTN_W + BTN_GAP) // 2  # = 130 - 59 = 71
CAN_CX   = CX + (BTN_W + BTN_GAP) // 2  # = 130 + 59 = 189
assert BTN_GAP >= 14, "gutter must be ≥14px"


# ── shared chrome ─────────────────────────────────────────────────────────────
def card_body(big):
    rect = pygame.Rect(m(CARD_X), m(CARD_TOP_Y), m(CARD_W), m(CARD_H))
    rad  = m(CARD_RAD)
    sc.drop_shadow(big, rect, rad, blur=m(8), alpha=165, dy=m(4))
    big.blit(vgrad_stops(rect.w, rect.h, rad,
                         [(0.0, CARD_T), (1.0, CARD_B)], 255, gamma=1.15), rect.topleft)
    sc.top_sheen(big, rect, rad, m(30), peak=56)
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    sc.bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 230), w=max(1, m(1.9)))
    tray = rect.inflate(-m(8), -m(8))
    pygame.draw.rect(big, (*CARD_RING_BRIGHT, 55), tray, width=max(1, m(1)), border_radius=rad - m(3))


def corner_gems(big, pal):
    sc.facet_gem(big, m(GEM_L_X), m(GEM_CY), m(GEM_R), pal["gem"], pal["deep"])
    sc.facet_gem(big, m(GEM_R_X), m(GEM_CY), m(GEM_R), pal["gem"], pal["deep"])


def name_text(big, name):
    nfs  = 45
    nfnt = font(nfs)
    mw   = m(CARD_W - 20)
    while sc._glyph_base(name, nfnt, 0).get_width() > mw and nfs > 24:
        nfs -= 1
        nfnt = font(nfs)
    plain_text(big, name, nfnt, (m(CX), m(213)), (250, 248, 240),
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
    top  = lerp_color(pal["gem"], WHITE, 0.1)
    bot  = lerp_color(pal["deep"], NEAR_BLACK, 0.05)
    body = vgrad_stops(w, h, 0, [(0.0,top),(0.5,pal["glow"]),(1.0,bot)], 255, gamma=1.08)
    pmask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(pmask, (255,255,255,255), poly)
    body.blit(pmask, (0,0), special_flags=pygame.BLEND_RGBA_MIN)
    sh = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(sh, (0,0,0,120), poly)
    big.blit(sh, (x0, y0 + m(2)))
    big.blit(body, (x0, y0))
    abspoly = [(x0+px, y0+py) for px, py in poly]
    pygame.draw.polygon(big, (4,5,16), abspoly, width=max(1, m(1.4)))
    plain_text(big, tier_word, f, (m(cx), m(cy_log)), (14,12,26),
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
    rw = max(3, m(3.0))
    pygame.draw.circle(big, pal["gem"], (cx, cy), r + rw // 2 + m(1), rw)


# ── concept bottom zone ───────────────────────────────────────────────────────
def coin_price_inline(big, cx, cy, price_str, coin_r=10, gap=5,
                      text_col=(230, 214, 168), text_size=11):
    f   = font(text_size)
    tw  = sc._glyph_base(price_str, f, 0).get_width()
    grp = m(coin_r) * 2 + m(gap) + tw
    coin_cx = cx - grp // 2 + m(coin_r)
    text_cx = coin_cx + m(coin_r) + m(gap) + tw // 2
    sc.coin_glyph(big, coin_cx, cy, m(coin_r))
    plain_text(big, price_str, f, (text_cx, cy), text_col,
               shadow_a=100, weight=m(0.8), keyline=(20, 14, 4), kw=m(0.7))


def rail_cartouche(big, price_str, pal):
    """Slim elongated pill cartouche holding coin+price inline."""
    cx  = m(CX)
    cy  = m(RAIL_CY)
    w   = m(RAIL_W)
    h   = m(RAIL_H)
    rad = m(RAIL_H // 2)
    x0  = cx - w // 2
    y0  = cy - h // 2
    rect = pygame.Rect(x0, y0, w, h)

    # faint tier aura behind the cartouche
    sc._alpha_aura(big, cx, cy, m(RAIL_W // 2 + 14), pal["glow"], peak=28, layers=8)

    sc.drop_shadow(big, rect, rad, blur=m(4), alpha=100, dy=m(2))
    big.blit(vgrad_stops(w, h, rad,
                         [(0.0, (22, 20, 38)), (1.0, (12, 10, 24))], 255, gamma=1.0),
             rect.topleft)
    sc.top_sheen(big, rect, rad, m(10), peak=22)
    sc.bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 200),
                 w=max(1, m(1.4)))

    coin_price_inline(big, cx, cy, price_str, coin_r=10, gap=5,
                      text_col=(240, 220, 168), text_size=11)


def gem_plate(big, cx_log, label, pal, is_buy=True):
    """Polished gem-tinted button plate."""
    cx  = m(cx_log)
    cy  = m(BTN_CY)
    w   = m(BTN_W)
    h   = m(BTN_H)
    rad = m(10)
    x0  = cx - w // 2
    y0  = cy - h // 2
    rect = pygame.Rect(x0, y0, w, h)

    if is_buy:
        gem_c  = pal["gem"]
        top_c  = lerp_color(pal["gem"], (180, 130, 40), 0.3)
        bot_c  = lerp_color(pal["deep"], (30, 20, 8), 0.2)
        lab_c  = (255, 248, 218)
        sheen  = 52
    else:
        gem_c  = lerp_color(pal["gem"], (120, 130, 155), 0.65)
        top_c  = (36, 38, 58)
        bot_c  = (20, 22, 36)
        lab_c  = (186, 188, 214)
        sheen  = 16

    sc.drop_shadow(big, rect, rad, blur=m(4), alpha=120, dy=m(3))
    big.blit(vgrad_stops(w, h, rad, [(0.0, top_c), (1.0, bot_c)], 255, gamma=1.1),
             rect.topleft)
    sc.top_sheen(big, rect, rad, m(18), peak=sheen)
    sc.gloss_sweep(big, rect, rad, peak=sheen // 2)
    sc.bevel_rim(big, rect, rad, CARD_RING_DEEP, (*gem_c, 220 if is_buy else 160),
                 w=max(1, m(1.6)))

    # small accent gem pip at top-centre
    sc.facet_gem(big, cx, cy - m(BTN_H // 2) - m(4), m(5), gem_c, pal["deep"])

    plain_text(big, label, font(13), rect.center, lab_c,
               shadow_a=150, tracking=m(1.2), weight=m(0.9 if is_buy else 0.7),
               keyline=(6, 6, 16), kw=m(0.7))


# ── popup render ──────────────────────────────────────────────────────────────
def render_popup(tier_word, sid, price, pal):
    big = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)
    card_body(big)
    corner_gems(big, pal)
    name_text(big, NAMES[tier_word])
    rarity_banner(big, tier_word, pal)
    rail_cartouche(big, price, pal)
    gem_plate(big, BUY_CX, "BUY", pal, is_buy=True)
    gem_plate(big, CAN_CX, "CANCEL", pal, is_buy=False)
    hero_disc(big, sid, pal)
    return pygame.transform.smoothscale(big, (POP_W, POP_H))


# ── 3-tier strip ──────────────────────────────────────────────────────────────
MARGIN, HEAD, GAP = 20, 58, 12
CANVAS_W = MARGIN * 2 + POP_W * 3 + GAP * 2
CANVAS_H = HEAD + POP_H + 40

canvas = pygame.Surface((CANVAS_W, CANVAS_H))
canvas.fill((8, 8, 20))

hdr  = _font(17, True).render("confirm_purchase_v8  ·  coin-rail-twin  ·  round 1", True, (232, 226, 208))
sub1 = _font(10, True).render("slim rail cartouche (coin+price) · twin gem plates · 14px gutter enforced", True, (140, 148, 168))
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

raw  = pygame.image.tostring(canvas, "RGB")
pil  = Image.frombytes("RGB", (CANVAS_W, CANVAS_H), raw)
out2 = pil.resize((CANVAS_W * 2, CANVAS_H * 2), Image.LANCZOS)

OUT = "/home/user/skybit/docs/confirm_purchase_v8/coin-rail-twin/round_1.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)
out2.save(OUT)
print(f"saved {out2.size[0]}×{out2.size[1]}  →  {OUT}")
