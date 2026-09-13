#!/usr/bin/env python3
"""chromatic-full-art · confirm_purchase_v8 · card-frame-v1 · round_1

A modern full-art holo card: a large art-bleed cabochon crowns the top, a
hue-cycling holographic rainbow rim rides the card EDGE only (4px), and a
frosted dark plate across the lower-mid carries Zone A (coin + price). Zone B is
the notched-hex tier ribbon flanked by bottom gems. No additive holo layer is
co-located with the disc centre — the rim lives at the card perimeter, so the
hero art reads clean under a single glass-dome specular.
"""
import os, sys, math, colorsys
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, "/home/user/skybit")
import pygame; pygame.init(); pygame.display.set_mode((1, 1))
import game.store_cards as sc
from game.store_cards import (m, SS, font, vgrad_stops, bevel_rim, top_sheen,
                              coin_glyph, facet_gem, _alpha_aura, plain_text,
                              lerp_stops, CABO_LO, CABO_HI, CARD_RING_BRIGHT,
                              CARD_RING_DEEP, PRICE_STOPS)
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
    ("RARE",      "skin_wizard",    "WIZARD",    "720",
     {"gem": (108, 188, 252), "glow": (60, 140, 220), "deep": (20, 60, 130)}),
    ("EPIC",      "skin_prism",     "PRISM",     "1,400",
     {"gem": (194, 122, 248), "glow": (140, 60, 220), "deep": (70, 20, 160)}),
    ("LEGENDARY", "skin_astronaut", "ASTRONAUT", "2,600",
     {"gem": (255, 202, 104), "glow": (220, 150, 40), "deep": (140, 80, 10)}),
]

POP_W, POP_H = 260, 442; CX = 130
CARD_X, CARD_TOP_Y, CARD_W, CARD_H, CARD_RAD = 10, 127, 240, 299, 23
DISC_CY, DISC_R = 135, 53
ZA_CY = 247
BAND_X, BAND_Y, BAND_W, BAND_H, BAND_A = 10, 232, 240, 33, 185
Y_BANNER, BOT_GEM_CY = 402, 402
GEM_L_X, GEM_R_X, GEM_R = 43, 217, 14
SHELF_X, SHELF_Y, SHELF_W, SHELF_H = 17, 335, 226, 91
BTN_W, BTN_H, BTN_RAD, BTN_CY, BTN_GAP = 99, 31, 12, 360, 10
BUY_CX = CX - (BTN_W + BTN_GAP) // 2; CAN_CX = CX + (BTN_W + BTN_GAP) // 2

# Card body base: a deep indigo art-field — darker than the CONSTELLATION body
# so the bleed art and the holo rim carry the colour, not the frame.
BODY_STOPS = [(0.0, (12, 14, 38)), (1.0, (8, 9, 24))]

# Zone B on LEGENDARY cools to teal so the rarity read is DELIBERATELY cold
# against the warm-gold price in Zone A — the signature full-art tension.
LEGENDARY_ZB = {"gem": (100, 220, 240), "glow": (50, 160, 200), "deep": (14, 70, 90)}


# ── card body + holo rim ─────────────────────────────────────────────────────
def card_body(big):
    rect = pygame.Rect(m(CARD_X), m(CARD_TOP_Y), m(CARD_W), m(CARD_H)); rad = m(CARD_RAD)
    sc.drop_shadow(big, rect, rad, blur=m(8), alpha=165, dy=m(4))
    big.blit(vgrad_stops(rect.w, rect.h, rad, BODY_STOPS, 255, gamma=1.15), rect.topleft)
    top_sheen(big, rect, rad, m(30), peak=48)
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 200), w=max(1, m(1.9)))
    return rect


def _rr_perimeter(x0, y0, w, h, rad, step=4):
    """Ordered points tracing a rounded-rect outline — edges sampled every
    `step` px, corners every 4°. Consecutive points get a per-position holo hue
    so the whole rim reads as ONE continuous chromatic sweep."""
    X1, Y1 = x0 + w, y0 + h
    R = rad
    pts = []
    for x in range(x0 + R, X1 - R, step): pts.append((x, y0))               # top
    cx, cy = X1 - R, y0 + R                                                 # TR
    for a in range(270, 360, 4): pts.append((cx + R * math.cos(math.radians(a)), cy + R * math.sin(math.radians(a))))
    for y in range(y0 + R, Y1 - R, step): pts.append((X1, y))              # right
    cx, cy = X1 - R, Y1 - R                                                 # BR
    for a in range(0, 90, 4): pts.append((cx + R * math.cos(math.radians(a)), cy + R * math.sin(math.radians(a))))
    for x in range(X1 - R, x0 + R, -step): pts.append((x, Y1))             # bottom
    cx, cy = x0 + R, Y1 - R                                                 # BL
    for a in range(90, 180, 4): pts.append((cx + R * math.cos(math.radians(a)), cy + R * math.sin(math.radians(a))))
    for y in range(Y1 - R, y0 + R, -step): pts.append((x0, y))            # left
    cx, cy = x0 + R, y0 + R                                                 # TL
    for a in range(180, 270, 4): pts.append((cx + R * math.cos(math.radians(a)), cy + R * math.sin(math.radians(a))))
    return pts


def _holo_col(base_rgb, t):
    """Base tier hue swung ±40° by a full sine cycle around the perimeter, with
    a slight sat/val lift so the rim shimmers vivid rainbow rather than muddy."""
    r, g, b = [c / 255 for c in base_rgb]
    hh, s, v = colorsys.rgb_to_hsv(r, g, b)
    hh = (hh + (40.0 / 360.0) * math.sin(2 * math.pi * t)) % 1.0
    s = min(1.0, s * 1.1 + 0.14); v = min(1.0, v * 1.05 + 0.06)
    r, g, b = colorsys.hsv_to_rgb(hh, s, v)
    return (int(r * 255), int(g * 255), int(b * 255))


def holo_rim(big, rect, gem):
    """A 4px hue-cycling rainbow border hugging the CARD EDGE only. Drawn onto a
    local surface inset one bevel in, then clipped to the rounded card silhouette
    so nothing pokes past the corners — and NOTHING lands at the disc centre."""
    w, h, rad = rect.w, rect.h, m(CARD_RAD)
    holo = pygame.Surface((w, h), pygame.SRCALPHA)
    inset = m(2); rw = max(1, m(4))
    pts = _rr_perimeter(inset, inset, w - inset * 2, h - inset * 2, rad - inset)
    n = len(pts)
    for i in range(n):
        col = _holo_col(gem, i / n)
        a, b = pts[i], pts[(i + 1) % n]
        pygame.draw.line(holo, col, a, b, rw)
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=rad)
    holo.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(holo, rect.topleft)


# ── frosted band + Zone A ────────────────────────────────────────────────────
def frosted_band(big):
    """A semi-transparent dark plate across the lower-mid card, framed by a dark
    keyline top+bottom so it reads as a distinct panel over the bright art. Its
    alpha stays ≥180 so Zone A holds contrast against any worst-case light skin."""
    bx, by = m(BAND_X), m(BAND_Y)
    panel = vgrad_stops(m(BAND_W), m(BAND_H), 0,
                        [(0.0, (20, 22, 50)), (1.0, (14, 16, 40))], BAND_A)
    big.blit(panel, (bx, by))
    bw = max(1, m(1.4))
    pygame.draw.line(big, (4, 5, 16), (bx, by), (bx + m(BAND_W), by), bw)
    pygame.draw.line(big, (4, 5, 16), (bx, by + m(BAND_H)), (bx + m(BAND_W), by + m(BAND_H)), bw)
    # faint upper glint so the plate has a lit lip, not just a flat cut
    pygame.draw.line(big, (70, 74, 110), (bx, by + bw), (bx + m(BAND_W), by + bw), max(1, m(0.8)))


def zone_a(big, price_str):
    """Coin glyph + gold price numeral inline on the frosted plate. The numeral
    carries a light keyline so it reads crisp gold-on-dark at ≥4.5:1."""
    cy = m(ZA_CY)
    coin_glyph(big, m(CX - 46), cy, m(12))
    gold = lerp_stops(PRICE_STOPS, 0.18)
    plain_text(big, price_str, font(20), (m(CX + 30), cy), gold, shadow_a=150,
               weight=m(0.9), keyline=(250, 236, 200), kw=max(1, m(0.8)))


def name_text(big, name):
    plain_text(big, name, font(18), (m(CX), m(213)), (250, 248, 240),
               shadow_a=170, weight=m(0.9), keyline=(6, 6, 16), kw=m(1.0))


# ── shelf + buttons (standard — not redesigned) ──────────────────────────────
def shelf_and_buttons(big):
    shelf_rect = pygame.Rect(m(SHELF_X), m(SHELF_Y), m(SHELF_W), m(SHELF_H)); sr = m(CARD_RAD)
    shelf = vgrad_stops(shelf_rect.w, shelf_rect.h, 0,
                        [(0.0, (34, 36, 72)), (0.5, (22, 24, 54)), (1.0, (12, 14, 36))], 255).copy()
    smask = pygame.Surface(shelf_rect.size, pygame.SRCALPHA)
    pygame.draw.rect(smask, (255, 255, 255, 255), smask.get_rect(),
                     border_bottom_left_radius=sr, border_bottom_right_radius=sr)
    shelf.blit(smask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    top_sheen(shelf, shelf.get_rect(), 0, m(20), peak=35)
    pygame.draw.line(shelf, (115, 106, 140), (0, 0), (shelf_rect.w - 1, 0), max(1, m(1)))
    seat = pygame.Surface((shelf_rect.w, m(6)), pygame.SRCALPHA)
    for yy in range(m(6)):
        pygame.draw.line(seat, (0, 0, 0, int(120 * (1 - yy / m(6)))), (0, yy), (shelf_rect.w - 1, yy))
    big.blit(seat, (shelf_rect.x, shelf_rect.y - m(6))); big.blit(shelf, shelf_rect.topleft)
    br = m(BTN_RAD)
    for cx_b, lbl, stops, lab_c, pk, rw in [
        (m(BUY_CX), "BUY", [(0.0, (38, 40, 84)), (1.0, (22, 24, 56))], (200, 205, 240), 22, m(2.0)),
        (m(CAN_CX), "CANCEL", [(0.0, (26, 28, 64)), (1.0, (14, 16, 44))], (150, 155, 200), 14, m(2.2)),
    ]:
        r = pygame.Rect(0, 0, m(BTN_W), m(BTN_H)); r.center = (cx_b, m(BTN_CY))
        sc.drop_shadow(big, r, br, blur=m(3), alpha=100, dy=m(2))
        big.blit(vgrad_stops(r.w, r.h, br, stops, 255), r.topleft)
        top_sheen(big, r, br, m(12), peak=pk)
        bevel_rim(big, r, br, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 230), w=max(1, rw))
        plain_text(big, lbl, font(14 if lbl == "BUY" else 13), r.center, lab_c,
                   shadow_a=110, weight=m(0.8), keyline=(8, 6, 20), kw=m(0.9))


def bottom_gems(big, pal):
    for gx in [m(GEM_L_X), m(GEM_R_X)]:
        _alpha_aura(big, gx, m(BOT_GEM_CY), m(16), pal["glow"], peak=60, layers=14)
        facet_gem(big, gx, m(BOT_GEM_CY), m(GEM_R), pal["gem"], pal["deep"])


# ── hero disc — art-bleed cabochon (single glass specular, no centre halo) ────
def hero_disc(big, sid, pal):
    cx, cy, r = m(CX), m(DISC_CY), m(DISC_R)
    # A soft aura at an OFFSET centre (below the disc) so the disc reads seated on
    # the art without stacking an additive halo on the glass specular.
    _alpha_aura(big, cx, m(160), r + m(12), pal["glow"], peak=20, layers=10)
    sc.cabochon(big, cx, cy, r, CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    try:
        sc.blit_thumb(big, sid, cx, cy, int(r * 1.5))
    except Exception:
        pygame.draw.circle(big, pal["gem"], (cx, cy), int(r * 0.7))
    sc.cabochon_glass(big, cx, cy, r, tint=pal["gem"])


# ── render loop ──────────────────────────────────────────────────────────────
def render_popup(tier_word, sid, name, price_str, pal):
    big = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)
    rect = card_body(big)
    holo_rim(big, rect, pal["gem"])
    name_text(big, name)
    frosted_band(big)
    zone_a(big, price_str)
    shelf_and_buttons(big)
    zb = dict(pal, **LEGENDARY_ZB) if tier_word == "LEGENDARY" else pal
    sc._ribbon(big, tier_word, m(CX), m(Y_BANNER), m(146), zb)
    bottom_gems(big, zb)
    hero_disc(big, sid, pal)
    return pygame.transform.smoothscale(big, (POP_W, POP_H))


MARGIN, HEAD, GAP = 20, 58, 12
STRIP_W = MARGIN * 2 + len(TIERS) * (POP_W + GAP) - GAP
STRIP_H = HEAD + POP_H + MARGIN
strip = Image.new("RGB", (STRIP_W, STRIP_H), (8, 8, 20))
idr = ImageDraw.Draw(strip)
idr.text((MARGIN, 18), "chromatic-full-art · card-frame-v1 · round_1", fill=(232, 226, 208))
for i, (tw, sid, nm, ps, pal) in enumerate(TIERS):
    pop = render_popup(tw, sid, nm, ps, pal)
    pil = Image.frombytes("RGB", (POP_W, POP_H), pygame.image.tostring(pop, "RGB"))
    x = MARGIN + i * (POP_W + GAP); strip.paste(pil, (x, HEAD))
    idr.text((x + POP_W // 2, HEAD + POP_H + 6), tw, fill=(180, 176, 210), anchor="mt")
out = strip.resize((STRIP_W * 2, STRIP_H * 2), Image.LANCZOS)
import pathlib
OUTDIR = "/home/user/skybit/docs/confirm_purchase_v8/card-frame-v1/chromatic-full-art"
pathlib.Path(OUTDIR).mkdir(parents=True, exist_ok=True)
OUT = OUTDIR + "/round_1.png"
out.save(OUT); print(f"saved {out.size[0]}x{out.size[1]}  ->  {OUT}")
