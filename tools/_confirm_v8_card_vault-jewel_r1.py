#!/usr/bin/env python3
"""vault-jewel · confirm_purchase_v8 · card-frame-v1 · round_1

Anime/Gacha SSR armoured vault plate. The distinguishing move vs a bleed-to-edge
chromatic full-art is CONTAINMENT: a dark steel plate holds a circular porthole
hero FIRMLY enclosed by a heavy gold bezel, riveted at the corners. The tier
colour lives in an off-centre nebula behind the plate, the corner rivets, the
inner accent line, and the porthole aura — never spilling past the armour.
"""
import os, sys, math
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, "/home/user/skybit")
import pygame; pygame.init(); pygame.display.set_mode((1, 1))
import game.store_cards as sc
from game.store_cards import (m, SS, font, vgrad_stops, plain_text, PRICE_STOPS,
                              CABO_LO, CABO_HI, CARD_RING_BRIGHT, CARD_RING_DEEP)
from PIL import Image, ImageDraw


# mandatory gloss_sweep patch — BLEND_ADD amount must follow the curve so a
# near-black body isn't blown white.
def _gloss_sweep_fixed(surf, rect, radius, peak=120):
    sweep = pygame.Surface(rect.size, pygame.SRCALPHA)
    h = max(1, rect.h)
    for y in range(h):
        v = int(peak * (1 - y / h) ** 2.4)
        if v <= 0: continue
        pygame.draw.line(sweep, (v, v, v, 255), (0, y), (rect.w, y))
    sm = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(sm, (255, 255, 255, 255), sm.get_rect(), border_radius=radius)
    sweep.blit(sm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(sweep, rect.topleft, special_flags=pygame.BLEND_ADD)
sc.gloss_sweep = _gloss_sweep_fixed


TIERS = [
    ("RARE", "skin_wizard", "720", {"gem": (108, 188, 252), "glow": (60, 140, 220), "deep": (20, 60, 130)}),
    ("EPIC", "skin_prism", "1,400", {"gem": (194, 122, 248), "glow": (140, 60, 220), "deep": (70, 20, 160)}),
    ("LEGENDARY", "skin_astronaut", "2,600", {"gem": (255, 202, 104), "glow": (220, 150, 40), "deep": (140, 80, 10)}),
]
NAMES = {"RARE": "WIZARD", "EPIC": "PRISM", "LEGENDARY": "ASTRONAUT"}

POP_W, POP_H = 260, 442; CX = 130
CARD_X, CARD_TOP, CARD_W, CARD_H, CARD_RAD = 10, 127, 240, 299, 23
DISC_CY, DISC_R = 135, 53
GEM_R = 14
ZA_CY = 247; ZB_CY = 402; GEM_L_X, GEM_R_X = 43, 217
BTN_W, BTN_H, BTN_RAD, BTN_CY, BTN_GAP = 99, 31, 12, 360, 10
BUY_CX = CX - (BTN_W + BTN_GAP) // 2; CAN_CX = CX + (BTN_W + BTN_GAP) // 2

# Fixed scatter so the starfield is deterministic across renders — placed in the
# plate margins, clear of the porthole and the copy lanes.
_STARS = [(45, 160), (72, 235), (32, 300), (56, 372), (208, 165), (226, 250),
          (200, 322), (230, 388), (118, 292), (162, 352), (96, 406), (182, 404)]


# ── plate body ──────────────────────────────────────────────────────────────
def _nebula(big, rect, rad, pal):
    """Off-centre tier haze + starfield, hard-clipped to the plate interior so
    the colour is CONTAINED by the armour rather than glowing past its edge."""
    inner = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    ox, oy = rect.x, rect.y
    sc._alpha_aura(inner, m(CX - 40) - ox, m(180) - oy, m(55), pal["glow"], peak=22, layers=12)
    sc._alpha_aura(inner, m(CX + 30) - ox, m(200) - oy, m(40), pal["glow"], peak=18, layers=10)
    for sx, sy in _STARS:
        pygame.draw.circle(inner, (255, 255, 255, 180), (m(sx) - ox, m(sy) - oy), max(1, m(1)))
    mask = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=rad)
    inner.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(inner, rect.topleft)


def _rivets(big, rect):
    """Four seated rivets — the mechanical read that sells the armoured plate."""
    inset = m(15)
    for px, py in [(rect.left + inset, rect.top + inset), (rect.right - inset, rect.top + inset),
                   (rect.left + inset, rect.bottom - inset), (rect.right - inset, rect.bottom - inset)]:
        pygame.draw.circle(big, (0, 0, 0, 150), (px, py), m(5))
        pygame.draw.circle(big, (160, 165, 180), (px, py), m(4))
        pygame.draw.circle(big, (210, 214, 225), (px - m(1), py - m(1)), max(1, m(1)))


def card_body(big, pal):
    rect = pygame.Rect(m(CARD_X), m(CARD_TOP), m(CARD_W), m(CARD_H)); rad = m(CARD_RAD)
    sc.drop_shadow(big, rect, rad, blur=m(8), alpha=165, dy=m(4))
    big.blit(vgrad_stops(rect.w, rect.h, rad,
                         [(0.0, (18, 20, 52)), (0.5, (10, 12, 34)), (1.0, (14, 16, 46))],
                         255, gamma=1.12), rect.topleft)
    sc.top_sheen(big, rect, rad, m(30), peak=40)
    _nebula(big, rect, rad, pal)
    # steel bevel over a crisp dark keyline, then a hairline tier accent inside
    # it so the armour edge is defined but still tier-tinted.
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    sc.bevel_rim(big, rect, rad, (40, 45, 90), (180, 190, 220), w=max(1, m(3)))
    acc = rect.inflate(-m(9), -m(9))
    pygame.draw.rect(big, (*pal["gem"], 150), acc, width=max(1, m(1)), border_radius=rad - m(4))
    _rivets(big, rect)


# ── copy + hero ─────────────────────────────────────────────────────────────
def name_text(big, name):
    fs = 18; nf = font(fs); mw = m(CARD_W - 24)
    while sc._glyph_base(name, nf, 0).get_width() > mw and fs > 12:
        fs -= 1; nf = font(fs)
    plain_text(big, name, nf, (m(CX), m(213)), (250, 248, 240), shadow_a=160,
               weight=m(0.9), keyline=(6, 6, 16), kw=m(1.0))


def zone_a(big, price):
    """Steel lozenge carrying the coin + PRICE_STOPS gold numeral inline."""
    r = pygame.Rect(0, 0, m(160), m(28)); r.center = (m(CX), m(ZA_CY))
    sc._dark_chip_body(big, r, m(11),
                       [(0.0, (38, 42, 80)), (0.5, (26, 30, 64)), (1.0, (40, 44, 84))],
                       (60, 65, 110), (120, 130, 180))
    coin_x = m(CX - 46)
    sc.coin_glyph(big, coin_x, m(ZA_CY), m(12))
    nf = font(20)
    base = sc._stamp_bold(sc._glyph_base(price, nf, 0), m(0.9))
    bw, bh = base.get_size()
    center = (coin_x + m(12) + m(8) + bw // 2, m(ZA_CY))
    r2 = base.get_rect(center=center)
    # dark keyline for legibility on the steel field
    kl = base.copy(); kl.fill((8, 6, 18, 255), special_flags=pygame.BLEND_RGBA_MULT)
    for ang in range(0, 360, 45):
        dx = int(round(m(1.4) * math.cos(math.radians(ang))))
        dy = int(round(m(1.4) * math.sin(math.radians(ang))))
        big.blit(kl, (r2.x + dx, r2.y + dy))
    fill = vgrad_stops(bw, bh, 0, PRICE_STOPS, 255)
    gold = base.copy(); gold.blit(fill, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    big.blit(gold, r2)


def zone_b(big, tier_word, zb_pal):
    for gx in [m(GEM_L_X), m(GEM_R_X)]:
        sc._alpha_aura(big, gx, m(ZB_CY), m(16), zb_pal["glow"], peak=60, layers=14)
        sc.facet_gem(big, gx, m(ZB_CY), m(GEM_R), zb_pal["gem"], zb_pal["deep"])
    sc._ribbon_lozenge(big, tier_word, m(CX), m(ZB_CY), m(130), zb_pal)


def buttons(big):
    br = m(BTN_RAD)
    for cx_b, lbl, stops, lab_c, pk, rw in [
        (m(BUY_CX), "BUY", [(0.0, (38, 40, 84)), (1.0, (22, 24, 56))], (200, 205, 240), 22, m(2.0)),
        (m(CAN_CX), "CANCEL", [(0.0, (26, 28, 64)), (1.0, (14, 16, 44))], (150, 155, 200), 14, m(2.2)),
    ]:
        r = pygame.Rect(0, 0, m(BTN_W), m(BTN_H)); r.center = (cx_b, m(BTN_CY))
        sc.drop_shadow(big, r, br, blur=m(3), alpha=100, dy=m(2))
        big.blit(vgrad_stops(r.w, r.h, br, stops, 255), r.topleft)
        sc.top_sheen(big, r, br, m(12), peak=pk)
        sc.bevel_rim(big, r, br, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 230), w=max(1, rw))
        plain_text(big, lbl, font(14 if lbl == "BUY" else 13), r.center, lab_c,
                   shadow_a=110, weight=m(0.8), keyline=(8, 6, 20), kw=m(0.9))


def hero(big, sid, pal):
    """Contained porthole: dome + skin, then a heavy TWO-ring gold bezel that
    firmly encloses the window — the containment read. cabochon_glass is the
    ONLY BLEND_ADD source at this centre; no aura stacks here."""
    cx, cy, r = m(CX), m(DISC_CY), m(DISC_R)
    sc.cabochon(big, cx, cy, r, CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    try:
        sc.blit_thumb(big, sid, cx, cy, int(r * 1.5))
    except Exception:
        pygame.draw.circle(big, pal["gem"], (cx, cy), int(r * 0.7))
    pygame.draw.circle(big, (236, 202, 116), (cx, cy), m(56), width=max(1, m(3)))
    pygame.draw.circle(big, (91, 70, 19), (cx, cy), m(59), width=max(1, m(2)))
    sc.cabochon_glass(big, cx, cy, r, tint=pal["gem"])


# ── render loop ─────────────────────────────────────────────────────────────
def render_popup(tier_word, sid, price, pal):
    big = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)
    # LEGENDARY swaps the Zone-B ribbon + flanking gems to oxblood crimson so the
    # rarity read is clearly NOT the gold family the price already owns.
    zb_pal = dict(pal)
    if tier_word == "LEGENDARY":
        zb_pal["gem"] = (200, 50, 50); zb_pal["glow"] = (160, 30, 30); zb_pal["deep"] = (90, 20, 20)
    card_body(big, pal)
    name_text(big, NAMES[tier_word])
    zone_a(big, price)
    buttons(big)
    zone_b(big, tier_word, zb_pal)
    hero(big, sid, pal)
    return pygame.transform.smoothscale(big, (POP_W, POP_H))


MARGIN, HEAD, GAP = 20, 58, 12
canvas_w = MARGIN * 2 + POP_W * 3 + GAP * 2
canvas_h = HEAD + MARGIN * 2 + POP_H
strip = Image.new("RGB", (canvas_w, canvas_h), (8, 8, 20))
idr = ImageDraw.Draw(strip)
idr.text((MARGIN, 20), "vault-jewel  ·  confirm_purchase_v8  ·  card-frame-v1  ·  round_1",
         fill=(232, 226, 208))
for i, (tw, sid, ps, pal) in enumerate(TIERS):
    pop = render_popup(tw, sid, ps, pal)
    pil = Image.frombytes("RGB", (POP_W, POP_H), pygame.image.tostring(pop, "RGB"))
    x = MARGIN + i * (POP_W + GAP)
    strip.paste(pil, (x, HEAD))
    idr.text((x + POP_W // 2, HEAD + POP_H + 6), tw, fill=(180, 176, 210), anchor="mt")
out = strip.resize((canvas_w * 2, canvas_h * 2), Image.LANCZOS)

import pathlib
OUTDIR = "/home/user/skybit/docs/confirm_purchase_v8/card-frame-v1/vault-jewel"
pathlib.Path(OUTDIR).mkdir(parents=True, exist_ok=True)
OUT = OUTDIR + "/round_1.png"
out.save(OUT); print(f"saved {out.size[0]}x{out.size[1]}  ->  {OUT}")
