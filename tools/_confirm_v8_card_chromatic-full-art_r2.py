#!/usr/bin/env python3
"""chromatic-full-art · confirm_purchase_v8 · card-frame-v1 · round_2

A modern full-art holo card: the top of the card body IS a printed art field —
a tier-hued gradient sky, masked to the card's rounded top, carrying an enlarged
rim-lit hero skin and a few procedural ambient motifs. A frosted dark plate
genuinely overlays the lower art and carries the centred coin+price unit. A
tier ribbon + flanking gems ride the midriff, and a wide hue-cycling holographic
rim rides the perimeter, drawn LAST so nothing covers it. On LEGENDARY the art
field cools to teal/violet while the price band stays warm gold — a deliberate
warm/cool tension that is the tier's signature.
"""
import os, sys, math, colorsys
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, "/home/user/skybit")
import pygame; pygame.init(); pygame.display.set_mode((1, 1))
import game.store_cards as sc
from game.store_cards import (m, SS, font, vgrad_stops, bevel_rim, top_sheen,
                              coin_glyph, facet_gem, _alpha_aura, plain_text,
                              lerp_stops, _glyph_base, CABO_LO, CABO_HI,
                              CARD_RING_BRIGHT, CARD_RING_DEEP, PRICE_STOPS)
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
# The art field is the card TOP printed as a full-bleed picture; its lower edge
# is a hard cut where the dark body resumes below the frosted band.
FIELD_BOT_Y = 306
HERO_CY, HERO_R = 200, 70
ZA_CY = 247
BAND_X, BAND_Y, BAND_W, BAND_H, BAND_A = 10, 232, 240, 33, 185
# Ribbon + flanking gems ride the midriff, just below the frosted band.
Y_BANNER, BOT_GEM_CY = 300, 300
GEM_L_X, GEM_R_X, GEM_R = 43, 217, 14
SHELF_X, SHELF_Y, SHELF_W, SHELF_H = 17, 335, 226, 91
BTN_W, BTN_H, BTN_RAD, BTN_CY, BTN_GAP = 99, 31, 12, 360, 10
BUY_CX = CX - (BTN_W + BTN_GAP) // 2; CAN_CX = CX + (BTN_W + BTN_GAP) // 2

# Card body base: a deep indigo — the frame; the printed art field carries the
# colour up top and the holo rim carries it at the edge.
BODY_STOPS = [(0.0, (12, 14, 38)), (1.0, (8, 9, 24))]

# Tier-hued art-field skies. LEGENDARY is intentionally COOL (teal/violet) so it
# reads in tension with the warm-gold price band below.
FIELD_SKY = {
    "RARE":      [(0.0, (20, 60, 130)),  (1.0, (40, 100, 170))],
    "EPIC":      [(0.0, (50, 20, 110)),  (1.0, (90, 50, 170))],
    "LEGENDARY": [(0.0, (30, 80, 140)),  (1.0, (50, 110, 180))],
}

# Zone B on LEGENDARY cools to teal so the rarity read is DELIBERATELY cold
# against the warm-gold price in Zone A — the signature full-art tension.
LEGENDARY_ZB = {"gem": (100, 220, 240), "glow": (50, 160, 200), "deep": (14, 70, 90)}


# ── card body ────────────────────────────────────────────────────────────────
def card_body(big):
    rect = pygame.Rect(m(CARD_X), m(CARD_TOP_Y), m(CARD_W), m(CARD_H)); rad = m(CARD_RAD)
    sc.drop_shadow(big, rect, rad, blur=m(8), alpha=165, dy=m(4))
    big.blit(vgrad_stops(rect.w, rect.h, rad, BODY_STOPS, 255, gamma=1.15), rect.topleft)
    top_sheen(big, rect, rad, m(30), peak=48)
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 200), w=max(1, m(1.9)))
    return rect


# ── full-bleed art field: sky + rim-lit hero + ambient motifs ─────────────────
def art_field(big, tier_word, sid, pal):
    """The card's upper half printed as a picture: a tier-hued gradient sky
    masked to the rounded card top, an enlarged rim-lit hero skin (no glass dome
    — it's ART, not a jewel), and a couple of soft ambient motifs off the hero so
    the sky isn't a flat wash. The frosted band later genuinely overlays this."""
    fx, fy = m(CARD_X), m(CARD_TOP_Y)
    fw, fh = m(CARD_W), m(FIELD_BOT_Y - CARD_TOP_Y)
    rad = m(CARD_RAD)
    field = pygame.Surface((fw, fh), pygame.SRCALPHA)
    stops = FIELD_SKY[tier_word]
    for y in range(fh):
        c = lerp_stops(stops, y / max(1, fh - 1))
        pygame.draw.line(field, (*c, 255), (0, y), (fw - 1, y))

    # ambient motifs at off-hero corners — soft alpha auras, no additive blowout
    for ax, ay, ar, col in [
        (m(38), m(30), m(15), pal["glow"]),
        (m(206), m(42), m(12), (235, 240, 255)),
        (m(196), m(146), m(11), pal["glow"]),
    ]:
        _alpha_aura(field, ax, ay, ar, col, peak=15, layers=12)

    # enlarged hero, local to the field. cabochon = the seating well; the skin
    # reads on top; a single gold rim-light rings it — NO cabochon_glass dome.
    hcx, hcy, hr = m(CX) - fx, m(HERO_CY) - fy, m(HERO_R)
    sc.cabochon(field, hcx, hcy, hr, CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    try:
        sc.blit_thumb(field, sid, hcx, hcy, int(hr * 1.5))
    except Exception:
        pygame.draw.circle(field, pal["gem"], (hcx, hcy), int(hr * 0.7))
    pygame.draw.circle(field, CARD_RING_BRIGHT, (hcx, hcy), m(73), width=max(1, m(2)))

    # mask to the card's TOP rounded corners only; the lower edge is a hard cut
    mask = pygame.Surface((fw, fh), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(),
                     border_top_left_radius=rad, border_top_right_radius=rad)
    field.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(field, (fx, fy))


# ── holo rim (drawn LAST) ─────────────────────────────────────────────────────
def _rr_perimeter(x0, y0, w, h, rad, step=4):
    """Ordered points tracing a rounded-rect outline — edges sampled every
    `step` px, corners every 4°. Consecutive points get a per-position holo hue
    so the whole rim reads as ONE continuous chromatic sweep."""
    X1, Y1 = x0 + w, y0 + h
    R = rad
    pts = []
    for x in range(x0 + R, X1 - R, step): pts.append((x, y0))
    cx, cy = X1 - R, y0 + R
    for a in range(270, 360, 4): pts.append((cx + R * math.cos(math.radians(a)), cy + R * math.sin(math.radians(a))))
    for y in range(y0 + R, Y1 - R, step): pts.append((X1, y))
    cx, cy = X1 - R, Y1 - R
    for a in range(0, 90, 4): pts.append((cx + R * math.cos(math.radians(a)), cy + R * math.sin(math.radians(a))))
    for x in range(X1 - R, x0 + R, -step): pts.append((x, Y1))
    cx, cy = x0 + R, Y1 - R
    for a in range(90, 180, 4): pts.append((cx + R * math.cos(math.radians(a)), cy + R * math.sin(math.radians(a))))
    for y in range(Y1 - R, y0 + R, -step): pts.append((x0, y))
    cx, cy = x0 + R, y0 + R
    for a in range(180, 270, 4): pts.append((cx + R * math.cos(math.radians(a)), cy + R * math.sin(math.radians(a))))
    return pts


def _holo_col(base_rgb, t, legendary=False):
    """Base tier hue swung ±120° across TWO full cycles around the perimeter, so
    the rim reads as vivid multi-band rainbow. On LEGENDARY the sweep is biased
    into the cyan→violet arc (≈180°–240°) so the rim stays COOL, echoing the
    cool art field against the warm price band."""
    if legendary:
        hh = (0.58 + (30.0 / 360.0) * math.sin(4 * math.pi * t)) % 1.0
        s, v = 0.72, 0.95
    else:
        r, g, b = [c / 255 for c in base_rgb]
        hh, s, v = colorsys.rgb_to_hsv(r, g, b)
        hh = (hh + (120.0 / 360.0) * math.sin(4 * math.pi * t)) % 1.0
        s = min(1.0, s * 1.1 + 0.14); v = min(1.0, v * 1.05 + 0.06)
    r, g, b = colorsys.hsv_to_rgb(hh, s, v)
    return (int(r * 255), int(g * 255), int(b * 255))


def holo_rim(big, rect, gem, legendary=False):
    """A WIDE hue-cycling rainbow border hugging the CARD EDGE, drawn LAST over
    everything. A bright specular pip bursts at the top-centre. Clipped to the
    rounded card silhouette so it never pokes past the corners."""
    w, h, rad = rect.w, rect.h, m(CARD_RAD)
    holo = pygame.Surface((w, h), pygame.SRCALPHA)
    inset = m(2); rw = max(1, m(6))
    pts = _rr_perimeter(inset, inset, w - inset * 2, h - inset * 2, rad - inset)
    n = len(pts)
    for i in range(n):
        col = _holo_col(gem, i / n, legendary)
        pygame.draw.line(holo, col, pts[i], pts[(i + 1) % n], rw)
    # specular pip: a short bright-white burst rotating once around, parked at
    # top-centre so the rim has a single hot glint like a real foil.
    pipx = w // 2
    glow = pygame.Surface((w, h), pygame.SRCALPHA)
    for i in range(n):
        px, py = pts[i]
        if py <= inset + m(2) and abs(px - pipx) < m(16):
            f = 1 - abs(px - pipx) / m(16)
            c = int(180 + 75 * f)
            pygame.draw.line(holo, (255, 255, 255), pts[i], pts[(i + 1) % n], rw)
            pygame.draw.line(glow, (c, c, c), pts[i], pts[(i + 1) % n], max(1, m(9)))
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=rad)
    holo.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    glow.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(holo, rect.topleft)
    big.blit(glow, rect.topleft, special_flags=pygame.BLEND_ADD)


# ── frosted band + Zone A ─────────────────────────────────────────────────────
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
    pygame.draw.line(big, (70, 74, 110), (bx, by + bw), (bx + m(BAND_W), by + bw), max(1, m(0.8)))


def zone_a(big, price_str):
    """Coin glyph + gold price numeral centred on CX as ONE unit: measured
    numeral width + fixed coin + gap, then the whole group is offset to sit
    symmetric about the card centreline."""
    cy = m(ZA_CY)
    nw = _glyph_base(price_str, font(18), 0).get_width()
    coin_d, gap = m(24), m(6)
    total = coin_d + gap + nw
    start = m(CX) - total // 2
    coin_glyph(big, start + m(12), cy, m(12))
    num_left = start + coin_d + gap
    gold = lerp_stops(PRICE_STOPS, 0.18)
    plain_text(big, price_str, font(18), (num_left + nw // 2, cy), gold, shadow_a=150,
               weight=m(0.9), keyline=(250, 236, 200), kw=max(1, m(0.8)))


def name_text(big, name):
    plain_text(big, name, font(18), (m(CX), m(213)), (250, 248, 240),
               shadow_a=170, weight=m(0.9), keyline=(6, 6, 16), kw=m(1.0))


# ── shelf + buttons ───────────────────────────────────────────────────────────
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
    # BUY = primary CTA: warm-gold body + bright gold bevel. CANCEL stays a muted
    # subordinate slate with a dim silver bevel.
    for cx_b, lbl, stops, lab_c, key_c, pk, rw, bright in [
        (m(BUY_CX), "BUY", [(0.0, (200, 165, 70)), (1.0, (180, 140, 50))],
         (255, 248, 232), (60, 38, 8), 30, m(2.0), (*CARD_RING_BRIGHT, 235)),
        (m(CAN_CX), "CANCEL", [(0.0, (26, 28, 64)), (1.0, (14, 16, 44))],
         (150, 155, 200), (8, 6, 20), 14, m(2.2), (120, 124, 150, 200)),
    ]:
        r = pygame.Rect(0, 0, m(BTN_W), m(BTN_H)); r.center = (cx_b, m(BTN_CY))
        sc.drop_shadow(big, r, br, blur=m(3), alpha=100, dy=m(2))
        big.blit(vgrad_stops(r.w, r.h, br, stops, 255), r.topleft)
        top_sheen(big, r, br, m(12), peak=pk)
        bevel_rim(big, r, br, CARD_RING_DEEP, bright, w=max(1, rw))
        plain_text(big, lbl, font(14 if lbl == "BUY" else 13), r.center, lab_c,
                   shadow_a=120, weight=m(0.85 if lbl == "BUY" else 0.8),
                   keyline=key_c, kw=m(0.9))


def bottom_gems(big, pal):
    for gx in [m(GEM_L_X), m(GEM_R_X)]:
        _alpha_aura(big, gx, m(BOT_GEM_CY), m(16), pal["glow"], peak=60, layers=14)
        facet_gem(big, gx, m(BOT_GEM_CY), m(GEM_R), pal["gem"], pal["deep"])


# ── render loop ───────────────────────────────────────────────────────────────
def render_popup(tier_word, sid, name, price_str, pal):
    big = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)
    rect = card_body(big)
    art_field(big, tier_word, sid, pal)
    frosted_band(big)
    name_text(big, name)
    zone_a(big, price_str)
    shelf_and_buttons(big)
    zb = dict(pal, **LEGENDARY_ZB) if tier_word == "LEGENDARY" else pal
    sc._ribbon(big, tier_word, m(CX), m(Y_BANNER), m(146), zb)
    bottom_gems(big, zb)
    holo_rim(big, rect, pal["gem"], legendary=(tier_word == "LEGENDARY"))
    return pygame.transform.smoothscale(big, (POP_W, POP_H))


MARGIN, HEAD, GAP = 20, 58, 12
STRIP_W = MARGIN * 2 + len(TIERS) * (POP_W + GAP) - GAP
STRIP_H = HEAD + POP_H + MARGIN
strip = Image.new("RGB", (STRIP_W, STRIP_H), (8, 8, 20))
idr = ImageDraw.Draw(strip)
idr.text((MARGIN, 18), "chromatic-full-art · card-frame-v1 · round_2", fill=(232, 226, 208))
for i, (tw, sid, nm, ps, pal) in enumerate(TIERS):
    pop = render_popup(tw, sid, nm, ps, pal)
    pil = Image.frombytes("RGB", (POP_W, POP_H), pygame.image.tostring(pop, "RGB"))
    x = MARGIN + i * (POP_W + GAP); strip.paste(pil, (x, HEAD))
    idr.text((x + POP_W // 2, HEAD + POP_H + 6), tw, fill=(180, 176, 210), anchor="mt")
out = strip.resize((STRIP_W * 2, STRIP_H * 2), Image.LANCZOS)
import pathlib
OUTDIR = "/home/user/skybit/docs/confirm_purchase_v8/card-frame-v1/chromatic-full-art"
pathlib.Path(OUTDIR).mkdir(parents=True, exist_ok=True)
OUT = OUTDIR + "/round_2.png"
out.save(OUT); print(f"saved {out.size[0]}x{out.size[1]}  ->  {OUT}")
