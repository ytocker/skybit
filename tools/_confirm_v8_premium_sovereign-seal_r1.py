#!/usr/bin/env python3
"""sovereign-seal · confirm_purchase_v8 · premium-v1 · round_1

A royal heraldic warrant finish over the EXISTING confirm-purchase popup. The
structure and positions are untouched — this only enriches the materials: a
warm sovereign-amber price lozenge (Zone A), the hero cabochon gains one crisp
tier ring, the card body carries a whisper-faint tone-on-tone drape, the empty
mid-card band earns a single engraved quatrefoil, and the rarity banner (Zone B)
diverges hard to oxblood-bronze on LEGENDARY so the top tier never reads
gold-on-gold across both zones.

Direct-draw render (not an exec patch of _draw_confirm): the popup geometry is
mirrored here so the premium finish can be authored in isolation before it folds
back into game/store.py.
"""
import os, sys
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame
pygame.init()
pygame.display.set_mode((1, 1))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import game.store_cards as sc
_orig_gloss = sc.gloss_sweep
def _safe_gloss(surf, rect, radius, peak=46):
    # BLEND_ADD gloss on a dark field blows white; ramp the additive amount down
    # the body so the finish stays a sheen, not a slab.
    w, h = rect[2], rect[3]
    gsurf = pygame.Surface((w, h), pygame.SRCALPHA)
    gsurf.fill((0, 0, 0, 0))
    steps = 10
    for i in range(steps):
        t = i / (steps - 1)
        alpha = int(peak * (1 - t))
        bar_h = max(1, int(h * 0.45 * (1 - t)))
        pygame.draw.ellipse(gsurf, (255, 255, 255, alpha),
            (int(w * 0.1), int(h * 0.04 + i * 1.5), int(w * 0.8), bar_h))
    surf.blit(gsurf, (rect[0], rect[1]))
sc.gloss_sweep = _safe_gloss

import math
from game.store_cards import (m, SS, font, vgrad_stops, bevel_rim, top_sheen,
                              coin_glyph, facet_gem, _alpha_aura, plain_text,
                              CABO_LO, CABO_HI, CARD_T, CARD_B, CARD_RING_BRIGHT,
                              CARD_RING_DEEP)
from PIL import Image, ImageDraw

# ── tier palettes ─────────────────────────────────────────────────────────────
PALETTES = {
    "RARE":      {"gem": (108, 188, 252), "deep": (28, 60, 120),  "glow": (160, 210, 255)},
    "EPIC":      {"gem": (194, 122, 248), "deep": (72, 28, 120),  "glow": (230, 160, 255)},
    "LEGENDARY": {"gem": (255, 202, 104), "deep": (120, 72, 12),  "glow": (255, 230, 140)},
}
TIERS = ["RARE", "EPIC", "LEGENDARY"]
SIDS  = {"RARE": "skin_wizard", "EPIC": "skin_prism", "LEGENDARY": "skin_astronaut"}
NAMES = {"RARE": "FROST WING", "EPIC": "PRISM WING", "LEGENDARY": "INFERNO WING"}
PRICES = {"RARE": "720", "EPIC": "1,400", "LEGENDARY": "2,600"}

# Zone B oxblood-bronze for LEGENDARY — a heraldic wax-warrant crimson that reads
# nowhere near the gold sovereign lozenge in Zone A, so the top tier's two zones
# never collapse into one gold read.
OXBLOOD = {"gem": (150, 60, 44), "deep": (70, 22, 16), "glow": (196, 96, 64)}

# ── popup geometry (locked; mirrors game/store.py _draw_confirm) ───────────────
POP_W, POP_H = 260, 442
CX = 130
CARD_X, CARD_TOP, CARD_W, CARD_H, CARD_RAD = 10, 127, 240, 299, 23
R_HERO, DISC_CY = 53, 135
GEM_R, GEM_CY, GEM_L_X, GEM_R_X = 14, 152, 43, 217
NAME_FS, Y_NAME = 45, 213
CHIP_CY = 247
Y_BANNER = 402
BOT_GEM_CY = 402
SHELF_X, SHELF_Y, SHELF_W, SHELF_H = 17, 335, 226, 91
BTN_W, BTN_H, BTN_RAD, BTN_CY, BTN_GAP = 99, 31, 12, 360, 10
BUY_CX = CX - (BTN_W + BTN_GAP) // 2
CAN_CX = CX + (BTN_W + BTN_GAP) // 2

# Zone A sovereign amber (warm gold coin metal) + rims.
CHIP_STOPS = [(0.0, (236, 176, 72)), (0.45, (204, 132, 42)), (1.0, (150, 90, 18))]
CHIP_RIM_D, CHIP_RIM_B = (78, 44, 8), (255, 226, 150)

# Dead-zone quatrefoil tone-on-tone indigo (deep engrave + faint inner glint).
Q_DEEP, Q_BRIGHT = (22, 24, 56), (104, 96, 168)


# ── (3) card body: base gradient + faint tone-on-tone drape ────────────────────
def card_body(big):
    rect = pygame.Rect(m(CARD_X), m(CARD_TOP), m(CARD_W), m(CARD_H))
    rad = m(CARD_RAD)
    sc.drop_shadow(big, rect, rad, blur=m(8), alpha=165, dy=m(4))
    big.blit(vgrad_stops(rect.w, rect.h, rad,
                         [(0.0, CARD_T), (1.0, CARD_B)], 255, gamma=1.15),
             rect.topleft)
    # A whisper drape: a second cool-indigo ramp at 6% alpha so the body reads as
    # figured watered-silk in raking light — never a repeating damask (which
    # would mud out at the 1× card scale).
    drape = vgrad_stops(rect.w, rect.h, rad,
                        [(0.0, (66, 70, 128)), (0.5, (30, 32, 78)),
                         (1.0, (16, 18, 52))], 15, gamma=1.25)
    big.blit(drape, rect.topleft)
    top_sheen(big, rect, rad, m(30), peak=56)
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 230),
              w=max(1, m(1.9)))
    tray = rect.inflate(-m(8), -m(8))
    pygame.draw.rect(big, (*CARD_RING_BRIGHT, 55), tray,
                     width=max(1, m(1)), border_radius=rad - m(3))


def corner_gems(big, pal):
    facet_gem(big, m(GEM_L_X), m(GEM_CY), m(GEM_R), pal["gem"], pal["deep"])
    facet_gem(big, m(GEM_R_X), m(GEM_CY), m(GEM_R), pal["gem"], pal["deep"])


# ── name plate (standard) ──────────────────────────────────────────────────────
def name_plate(big, name):
    nfs = NAME_FS
    nfnt = font(nfs)
    mw = m(CARD_W - 20)
    while sc._glyph_base(name, nfnt, 0).get_width() > mw and nfs > 24:
        nfs -= 1
        nfnt = font(nfs)
    plain_text(big, name, nfnt, (m(CX), m(Y_NAME)), (250, 248, 240),
               shadow_a=160, weight=m(0.9), keyline=(6, 6, 16), kw=m(1.0))


# ── (1) Zone A: sovereign amber lozenge price chip ─────────────────────────────
def zone_a_lozenge(big, price_str, pal):
    cy = m(CHIP_CY)
    body_w, body_h = m(64), m(24)
    total_w = m(84)                                   # tips clear SHELF_X 17→243
    body = pygame.Rect(0, 0, body_w, body_h)
    body.center = (m(CX), cy)
    rad = m(9)
    th = body_h // 2
    apex_l = (m(CX) - total_w // 2, cy)
    apex_r = (m(CX) + total_w // 2, cy)
    # Pointed lozenge ends drawn UNDER the rounded body so its rim laps the join.
    for apex, bx in ((apex_l, body.left), (apex_r, body.right)):
        pts = [apex, (bx, cy - th), (bx, cy + th)]
        pygame.draw.polygon(big, (204, 132, 42), pts)
        pygame.draw.polygon(big, CHIP_RIM_D, pts, max(1, m(1)))
    # Dark-corrected chip body so the amber field keeps its gradient (a raw
    # BLEND_ADD gloss would flatten it to a bright slab).
    sc._dark_chip_body(big, body, rad, CHIP_STOPS, CHIP_RIM_D, CHIP_RIM_B,
                       gloss=26, gamma=1.05)
    # Gem pip caps each pointed tip.
    facet_gem(big, apex_l[0], apex_l[1], m(4), pal["gem"], pal["deep"])
    facet_gem(big, apex_r[0], apex_r[1], m(4), pal["gem"], pal["deep"])
    # Coin + price numeral inline, group-centred inside the body.
    fs = 15
    num_font = font(fs)
    coin_r = m(9)
    gap = m(3)
    inner_w = body_w - m(12)
    num_w = num_font.size(price_str)[0]
    while coin_r * 2 + gap + num_w > inner_w and fs > 10:
        fs -= 1
        num_font = font(fs)
        num_w = num_font.size(price_str)[0]
    total = coin_r * 2 + gap + num_w
    left = m(CX) - total // 2
    coin_cx = left + coin_r
    num_cx = left + coin_r * 2 + gap + num_w // 2
    coin_glyph(big, coin_cx, cy, coin_r)
    plain_text(big, price_str, num_font, (num_cx, cy + m(1)), (52, 28, 4),
               shadow_a=0, weight=m(0.7))


# ── (4) dead-zone quatrefoil (the one ornament moment) ─────────────────────────
def dead_zone_quatrefoil(big):
    cx, cy = m(CX), m(297)                            # centred in the 259→335 band
    d, rl = m(13), m(13)
    layer = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    centers = [(cx, cy - d), (cx, cy + d), (cx - d, cy), (cx + d, cy)]
    for lx, ly in centers:
        pygame.draw.circle(layer, (*Q_DEEP, 40), (lx, ly), rl, max(2, m(4)))
    for lx, ly in centers:
        pygame.draw.circle(layer, (*Q_BRIGHT, 55), (lx, ly), rl - m(1),
                           max(1, m(0.5)))
    big.blit(layer, (0, 0))


# ── shelf + BUY/CANCEL (standard) ──────────────────────────────────────────────
def shelf_and_buttons(big):
    shelf_rect = pygame.Rect(m(SHELF_X), m(SHELF_Y), m(SHELF_W), m(SHELF_H))
    sr = m(CARD_RAD)
    shelf = vgrad_stops(shelf_rect.w, shelf_rect.h, 0,
                        [(0.0, (34, 36, 72)), (0.5, (22, 24, 54)),
                         (1.0, (12, 14, 36))], 255).copy()
    smask = pygame.Surface(shelf_rect.size, pygame.SRCALPHA)
    pygame.draw.rect(smask, (255, 255, 255, 255), smask.get_rect(),
                     border_bottom_left_radius=sr, border_bottom_right_radius=sr)
    shelf.blit(smask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    top_sheen(shelf, shelf.get_rect(), 0, m(20), peak=35)
    pygame.draw.line(shelf, (115, 106, 140), (0, 0), (shelf_rect.w - 1, 0),
                     max(1, m(1)))
    seat = pygame.Surface((shelf_rect.w, m(6)), pygame.SRCALPHA)
    for yy in range(m(6)):
        pygame.draw.line(seat, (0, 0, 0, int(120 * (1 - yy / m(6)))),
                         (0, yy), (shelf_rect.w - 1, yy))
    big.blit(seat, (shelf_rect.x, shelf_rect.y - m(6)))
    big.blit(shelf, shelf_rect.topleft)
    br = m(BTN_RAD)
    for cx_b, lbl, stops, lab_c, pk, rw in (
        (m(BUY_CX), "BUY",
         [(0.0, (38, 40, 84)), (1.0, (22, 24, 56))], (200, 205, 240), 22, m(2.0)),
        (m(CAN_CX), "CANCEL",
         [(0.0, (26, 28, 64)), (1.0, (14, 16, 44))], (150, 155, 200), 14, m(2.2)),
    ):
        r = pygame.Rect(0, 0, m(BTN_W), m(BTN_H))
        r.center = (cx_b, m(BTN_CY))
        sc.drop_shadow(big, r, br, blur=m(3), alpha=100, dy=m(2))
        big.blit(vgrad_stops(r.w, r.h, br, stops, 255), r.topleft)
        top_sheen(big, r, br, m(12), peak=pk)
        bevel_rim(big, r, br, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 230),
                  w=max(1, rw))
        plain_text(big, lbl, font(14 if lbl == "BUY" else 13), r.center, lab_c,
                   shadow_a=110, weight=m(0.8), keyline=(8, 6, 20), kw=m(0.9))


# ── (5) Zone B: rarity banner + flanking gems ──────────────────────────────────
def zone_b(big, tier_word, pal):
    zb = OXBLOOD if tier_word == "LEGENDARY" else pal
    for gx in (m(GEM_L_X), m(GEM_R_X)):
        _alpha_aura(big, gx, m(BOT_GEM_CY), m(16), zb["glow"], peak=55, layers=14)
    sc._ribbon_lozenge(big, tier_word, m(CX), m(Y_BANNER), m(146), zb)
    for gx in (m(GEM_L_X), m(GEM_R_X)):
        facet_gem(big, gx, m(BOT_GEM_CY), m(GEM_R), zb["gem"], zb["deep"])


# ── (2) hero disc: existing cabochon + ONE crisp tier ring ─────────────────────
def hero_disc(big, sid, pal):
    cx, cy, r = m(CX), m(DISC_CY), m(R_HERO)
    # The base popup's own spotlight halos — kept exactly, nothing added over.
    _alpha_aura(big, cx, cy, r + m(55), pal["glow"], peak=95, layers=24)
    _alpha_aura(big, cx, cy, r + m(20), pal["glow"], peak=70, layers=12)
    sc.cabochon(big, cx, cy, r, CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    try:
        sc.blit_thumb(big, sid, cx, cy, int(r * 1.5))
    except Exception:
        pygame.draw.circle(big, pal["gem"], (cx, cy), int(r * 0.7))
    sc.cabochon_glass(big, cx, cy, r, tint=pal["gem"])
    # ONE crisp tier ring — the sole added flourish on the hero (no coronet ticks,
    # no extra halo). Alpha-carry stroke so the tier hue reads on the gold bezel.
    pygame.draw.circle(big, (*pal["gem"], 150), (cx, cy), r, max(1, m(1)))


# ── render one popup ───────────────────────────────────────────────────────────
def render_popup(tier_word):
    pal = PALETTES[tier_word]
    big = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)
    card_body(big)
    corner_gems(big, pal)
    name_plate(big, NAMES[tier_word])
    zone_a_lozenge(big, PRICES[tier_word], pal)
    dead_zone_quatrefoil(big)
    shelf_and_buttons(big)
    zone_b(big, tier_word, pal)
    hero_disc(big, SIDS[tier_word], pal)              # last so the disc overhangs
    return pygame.transform.smoothscale(big, (POP_W, POP_H))


# ── strip ──────────────────────────────────────────────────────────────────────
MARGIN, HEAD, GAP = 20, 58, 12
STRIP_W = MARGIN * 2 + len(TIERS) * (POP_W + GAP) - GAP
STRIP_H = HEAD + POP_H + MARGIN
strip = Image.new("RGB", (STRIP_W, STRIP_H), (10, 9, 20))
idr = ImageDraw.Draw(strip)
idr.text((MARGIN, 18), "sovereign-seal · premium-v1 · round_1", fill=(236, 214, 160))
for i, tw in enumerate(TIERS):
    pop = render_popup(tw)
    pil = Image.frombytes("RGB", (POP_W, POP_H), pygame.image.tostring(pop, "RGB"))
    x = MARGIN + i * (POP_W + GAP)
    strip.paste(pil, (x, HEAD))
    idr.text((x + POP_W // 2, HEAD + POP_H + 6), tw, fill=(206, 190, 150), anchor="mt")

out = strip.resize((STRIP_W * 2, STRIP_H * 2), Image.LANCZOS)

import pathlib
OUTDIR = "/home/user/skybit/docs/confirm_purchase_v8/premium-v1/sovereign-seal"
pathlib.Path(OUTDIR).mkdir(parents=True, exist_ok=True)
OUT = OUTDIR + "/round_1.png"

W, H = out.size
assert (W, H) == (1688, 1040), f"size mismatch: {W}x{H}"
out.save(OUT)
print(f"saved {W}x{H}  ->  {OUT}")
