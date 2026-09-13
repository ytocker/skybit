#!/usr/bin/env python3
"""
enamel-split-bar  ·  confirm_purchase_v8  ·  round 2

Critical fix from art-director critique:
- The r1 half-clip was a no-op (transparent blit onto SRCALPHA surface).
  Both halves were slate; gold survived only as 4px corner crescents.
- Fixed by using set_clip on destination before each half blit.
- Draw order: fills first → sheen → seam → corner mask → bevel_rim.
- BUY bottom stop lifted (62,40,8)→(84,56,14) for richer gold.
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
CART_CY, CART_W, CART_H = 292, 142, 30
PILL_CY, PILL_W, PILL_H = 368, 216, 58
PILL_X   = CX - PILL_W // 2   # = 22
SEAM_X   = CX                 # seam at popup centre-line


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
                      text_col=(234, 218, 168), text_size=11):
    f   = font(text_size)
    tw  = sc._glyph_base(price_str, f, 0).get_width()
    grp = m(coin_r) * 2 + m(gap) + tw
    coin_cx = cx - grp // 2 + m(coin_r)
    text_cx = coin_cx + m(coin_r) + m(gap) + tw // 2
    sc.coin_glyph(big, coin_cx, cy, m(coin_r))
    plain_text(big, price_str, f, (text_cx, cy), text_col,
               shadow_a=100, weight=m(0.8), keyline=(20, 14, 4), kw=m(0.7))


def price_cartouche(big, price_str, pal):
    """Dark enamel plaque above the split pill — coin+price inline."""
    cx  = m(CX)
    cy  = m(CART_CY)
    w   = m(CART_W)
    h   = m(CART_H)
    rad = m(7)
    x0  = cx - w // 2
    y0  = cy - h // 2
    rect = pygame.Rect(x0, y0, w, h)

    sc.drop_shadow(big, rect, rad, blur=m(4), alpha=100, dy=m(2))
    big.blit(vgrad_stops(w, h, rad,
                         [(0.0, (22, 18, 30)), (1.0, (12, 10, 20))], 255, gamma=1.0),
             rect.topleft)
    sc.top_sheen(big, rect, rad, m(10), peak=20)
    sc.bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 195),
                 w=max(1, m(1.4)))

    coin_price_inline(big, cx, cy, price_str, coin_r=10, gap=5,
                      text_col=(240, 222, 172), text_size=11)


def split_pill(big, pal):
    """Single enamel pill split at seam: BUY (warm gold left) / CANCEL (slate right).

    Uses set_clip on destination to correctly restrict each half blit —
    the r1 transparent-surface clip was a no-op (0-alpha src → dest unchanged).
    Draw order: fills → sheen → seam → corner mask → bevel_rim.
    """
    pill_x = m(PILL_X)
    pill_y = m(PILL_CY) - m(PILL_H) // 2
    pw     = m(PILL_W)
    ph     = m(PILL_H)
    rad    = m(PILL_H // 2)
    seam_x = m(SEAM_X)
    half_w = seam_x - pill_x   # left half width in SS px

    pill_rect = pygame.Rect(pill_x, pill_y, pw, ph)
    sc.drop_shadow(big, pill_rect, rad, blur=m(5), alpha=130, dy=m(4))

    # ── fills — set_clip restricts dest write to each half ──────────────────
    buy_stops = [(0.0, (148, 104, 28)), (0.5, (104, 70, 14)), (1.0, (84, 56, 14))]
    buy_body  = vgrad_stops(pw, ph, rad, buy_stops, 255, gamma=1.1)

    can_stops = [(0.0, (36, 32, 52)), (1.0, (22, 20, 34))]
    can_body  = vgrad_stops(pw, ph, rad, can_stops, 255, gamma=1.0)

    # blit full-pill surfaces, clipped to each half on the destination
    big.set_clip(pygame.Rect(pill_x, pill_y, half_w, ph))
    big.blit(buy_body, pill_rect.topleft)
    big.set_clip(pygame.Rect(seam_x, pill_y, pw - half_w, ph))
    big.blit(can_body, pill_rect.topleft)
    big.set_clip(None)

    # ── asymmetric sheen ─────────────────────────────────────────────────────
    buy_r = pygame.Rect(pill_x, pill_y, half_w, ph)
    can_r = pygame.Rect(seam_x, pill_y, pw - half_w, ph)
    sc.top_sheen(big, buy_r, 0, m(20), peak=52)
    sc.top_sheen(big, can_r, 0, m(16), peak=16)

    # ── gold seam divider ────────────────────────────────────────────────────
    pygame.draw.line(big, (*CARD_RING_BRIGHT, 210),
                     (seam_x, pill_y + m(4)),
                     (seam_x, pill_y + ph - m(4)), max(1, m(1.4)))
    pygame.draw.line(big, (0, 0, 0, 100),
                     (seam_x + 1, pill_y + m(4)),
                     (seam_x + 1, pill_y + ph - m(4)), max(1, m(1)))

    # ── corner mask: restore card bg outside the rounded pill ─────────────────
    out_mask = pygame.Surface((pw, ph), pygame.SRCALPHA)
    out_mask.fill((8, 8, 20, 255))
    pygame.draw.rect(out_mask, (0, 0, 0, 0), out_mask.get_rect(), border_radius=rad)
    big.blit(out_mask, pill_rect.topleft)

    # ── single bevel rim around the whole pill ───────────────────────────────
    sc.bevel_rim(big, pill_rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 230),
                 w=max(1, m(1.8)))

    # ── labels ────────────────────────────────────────────────────────────────
    buy_centre = (pill_x + half_w // 2, pill_y + ph // 2)
    can_centre = (seam_x + (pw - half_w) // 2, pill_y + ph // 2)
    plain_text(big, "BUY",    font(14), buy_centre, (255, 246, 210),
               shadow_a=160, tracking=m(1.4), weight=m(1.1), keyline=(60, 38, 6), kw=m(0.9))
    plain_text(big, "CANCEL", font(11), can_centre, (180, 176, 210),
               shadow_a=100, tracking=m(1.0), weight=m(0.7), keyline=(6, 6, 16), kw=m(0.6))


# ── popup render ──────────────────────────────────────────────────────────────
def render_popup(tier_word, sid, price, pal):
    big = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)
    card_body(big)
    corner_gems(big, pal)
    name_text(big, NAMES[tier_word])
    rarity_banner(big, tier_word, pal)
    price_cartouche(big, price, pal)
    split_pill(big, pal)
    hero_disc(big, sid, pal)
    return pygame.transform.smoothscale(big, (POP_W, POP_H))


# ── 3-tier strip ──────────────────────────────────────────────────────────────
MARGIN, HEAD, GAP = 20, 58, 12
CANVAS_W = MARGIN * 2 + POP_W * 3 + GAP * 2
CANVAS_H = HEAD + POP_H + 40

canvas = pygame.Surface((CANVAS_W, CANVAS_H))
canvas.fill((8, 8, 20))

hdr  = _font(17, True).render("confirm_purchase_v8  ·  enamel-split-bar  ·  round 2", True, (232, 226, 208))
sub1 = _font(10, True).render("set_clip half-split fix · BUY bottom stop lifted · gold seam clear", True, (140, 148, 168))
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

OUT = "/home/user/skybit/docs/confirm_purchase_v8/enamel-split-bar/round_2.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)
out2.save(OUT)
print(f"saved {out2.size[0]}×{out2.size[1]}  →  {OUT}")
