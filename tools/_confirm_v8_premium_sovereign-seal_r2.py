#!/usr/bin/env python3
"""sovereign-seal · confirm_purchase_v8 · premium-v1 · round_2

Round 2 addresses every art-director critique from round 1:

  1. Quatrefoil fill pushed to alpha 120 (was 40), stroke widened to m(6), inner
     catch-light replaced from cold indigo to warm sovereign amber — the ornament
     now drops a clear 20+ value delta against the body and the glint ties it to
     the Zone A amber field.

  2. BUY button graduated to a dark amber CTA gradient so the amber through-line
     (Zone A lozenge → BUY) reads as sovereign warrant design language.  Rim/bevel
     uses GOLD_A_RIM_BRIGHT / GOLD_A_RIM_DARK to echo the lozenge.  CANCEL stays
     muted indigo so it recedes against the CTA.

  3. Card-body drape switched from a whisper 6%-ramp to two crossing diagonal
     families of lines (CARD_T ± 6 value, 12 px spacing, ~14% alpha) — the body
     reads as figured material in raking light, not flat void.

  4. Zone A lozenge tip pips fixed to warm amber/gold on every tier so the chip
     reads as a single sovereign material — tier hue is carried by the hero ring
     and Zone B banner.

  5. LEGENDARY glass hotspot pulled back 20% (sc.CABO_SPEC_A × 0.8) so the warm
     glow ring survives rather than blowing toward near-white; EPIC/RARE unchanged.

  6. _safe_gloss ellipse centring corrected — left edge derived from (w - ellipse_w)//2
     rather than int(w * 0.1) so integer rounding never shifts the highlight off axis.
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
        # Derive left edge from (w - ellipse_w) // 2 so integer rounding never
        # shifts the highlight 1 px left — (w * 0.1) vs (w - w*0.8) / 2 differ
        # by 1 px at small widths and that asymmetry reads on amber.
        ellipse_w = int(w * 0.8)
        ellipse_x = (w - ellipse_w) // 2
        pygame.draw.ellipse(gsurf, (255, 255, 255, alpha),
            (ellipse_x, int(h * 0.04 + i * 1.5), ellipse_w, bar_h))
    surf.blit(gsurf, (rect[0], rect[1]))
sc.gloss_sweep = _safe_gloss

import math
from game.store_cards import (m, SS, font, vgrad_stops, bevel_rim, top_sheen,
                              coin_glyph, facet_gem, _alpha_aura, plain_text,
                              CABO_LO, CABO_HI, CARD_T, CARD_B, CARD_RING_BRIGHT,
                              CARD_RING_DEEP, GOLD_A_RIM_DARK, GOLD_A_RIM_BRIGHT)
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

# Quatrefoil: deep-engrave indigo channel + warm amber catch-light.  The amber
# glint ties the ornament to the Zone A sovereign field rather than the cold body.
Q_DEEP      = (22, 24, 56)
AMBER_GLINT = (200, 165, 90)

# Lozenge tip pips: fixed warm amber/gold on every tier so Zone A reads as a
# single sovereign material.  Tier hue is carried by the hero ring and Zone B.
PIP_GEM  = (220, 170, 60)
PIP_DEEP = (100,  62, 12)


# ── (3) card body: base gradient + diagonal figured-material drape ─────────────
def card_body(big):
    rect = pygame.Rect(m(CARD_X), m(CARD_TOP), m(CARD_W), m(CARD_H))
    rad = m(CARD_RAD)
    sc.drop_shadow(big, rect, rad, blur=m(8), alpha=165, dy=m(4))
    big.blit(vgrad_stops(rect.w, rect.h, rad,
                         [(0.0, CARD_T), (1.0, CARD_B)], 255, gamma=1.15),
             rect.topleft)
    # Two crossing diagonal families at ~14% alpha — CARD_T ± 6 value, 12 px
    # spacing.  A crosshatch weave makes the body feel like figured watered-silk
    # in raking light; a flat gradient alone reads as dead void at this scale.
    drape = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    spacing = 12
    light_col = (34, 36, 76, 35)   # CARD_T + 6 value
    dark_col  = (22, 24, 64, 35)   # CARD_T − 6 value
    dw, dh = rect.w, rect.h
    for off in range(-(dh + spacing), dw + dh + spacing, spacing):
        pygame.draw.line(drape, light_col, (off, 0), (off + dh, dh))
    for off in range(-(dh + spacing), dw + dh + spacing, spacing):
        pygame.draw.line(drape, dark_col, (off, dh), (off + dh, 0))
    dmask = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(dmask, (255, 255, 255, 255), dmask.get_rect(), border_radius=rad)
    drape.blit(dmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
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
    # Fixed warm amber pips on all tiers — the Zone A chip is sovereign material;
    # tier hue is already carried by the hero ring and Zone B banner.
    facet_gem(big, apex_l[0], apex_l[1], m(4), PIP_GEM, PIP_DEEP)
    facet_gem(big, apex_r[0], apex_r[1], m(4), PIP_GEM, PIP_DEEP)
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
    # Alpha 120 + stroke m(6) — the arcs drop a clear 20+ value delta against the
    # indigo body so they register as punched-engraved relief, not a watermark.
    for lx, ly in centers:
        pygame.draw.circle(layer, (*Q_DEEP, 120), (lx, ly), rl, max(2, m(6)))
    # Warm amber inner catch-light binds the ornament to the sovereign amber field
    # of Zone A rather than reading as a cold indigo filigree.
    for lx, ly in centers:
        pygame.draw.circle(layer, (*AMBER_GLINT, 180), (lx, ly), rl - m(1),
                           max(1, m(0.5)))
    big.blit(layer, (0, 0))


# ── shelf + BUY/CANCEL ─────────────────────────────────────────────────────────
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
    # BUY: dark amber gradient + GOLD_A sovereign rim so it echoes the Zone A
    # lozenge — the amber through-line is the sovereign warrant design language.
    # CANCEL: muted indigo stays the same so it clearly recedes against the CTA.
    for cx_b, lbl, stops, lab_c, pk, rw, rim_d, rim_b in (
        (m(BUY_CX), "BUY",
         [(0.0, (120, 75, 18)), (1.0, (80, 45, 8))],
         (255, 248, 220), 28, m(2.0), GOLD_A_RIM_DARK, GOLD_A_RIM_BRIGHT),
        (m(CAN_CX), "CANCEL",
         [(0.0, (26, 28, 64)), (1.0, (14, 16, 44))],
         (150, 155, 200), 14, m(2.2), CARD_RING_DEEP, CARD_RING_BRIGHT),
    ):
        r = pygame.Rect(0, 0, m(BTN_W), m(BTN_H))
        r.center = (cx_b, m(BTN_CY))
        sc.drop_shadow(big, r, br, blur=m(3), alpha=100, dy=m(2))
        big.blit(vgrad_stops(r.w, r.h, br, stops, 255), r.topleft)
        top_sheen(big, r, br, m(12), peak=pk)
        bevel_rim(big, r, br, rim_d, (*rim_b, 235), w=max(1, rw))
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
def hero_disc(big, sid, pal, tier_word="RARE"):
    cx, cy, r = m(CX), m(DISC_CY), m(R_HERO)
    # The base popup's own spotlight halos — kept exactly, nothing added over.
    _alpha_aura(big, cx, cy, r + m(55), pal["glow"], peak=95, layers=24)
    _alpha_aura(big, cx, cy, r + m(20), pal["glow"], peak=70, layers=12)
    sc.cabochon(big, cx, cy, r, CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    try:
        sc.blit_thumb(big, sid, cx, cy, int(r * 1.5))
    except Exception:
        pygame.draw.circle(big, pal["gem"], (cx, cy), int(r * 0.7))
    # Pull back the glass specular hotspot for LEGENDARY so the warm pal["glow"]
    # ring survives — LEGENDARY's amber field can read through at full saturation
    # rather than blowing toward (254,254,254).  EPIC/RARE are fine at full alpha.
    orig_spec_a = sc.CABO_SPEC_A
    if tier_word == "LEGENDARY":
        sc.CABO_SPEC_A = int(orig_spec_a * 0.8)
    sc.cabochon_glass(big, cx, cy, r, tint=pal["gem"])
    sc.CABO_SPEC_A = orig_spec_a
    # ONE crisp tier ring — the sole added flourish on the hero.
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
    hero_disc(big, SIDS[tier_word], pal, tier_word)   # last so disc overhangs
    return pygame.transform.smoothscale(big, (POP_W, POP_H))


# ── strip ──────────────────────────────────────────────────────────────────────
MARGIN, HEAD, GAP = 20, 58, 12
STRIP_W = MARGIN * 2 + len(TIERS) * (POP_W + GAP) - GAP
STRIP_H = HEAD + POP_H + MARGIN
strip = Image.new("RGB", (STRIP_W, STRIP_H), (10, 9, 20))
idr = ImageDraw.Draw(strip)
idr.text((MARGIN, 18), "sovereign-seal · premium-v1 · round_2", fill=(236, 214, 160))
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
OUT = OUTDIR + "/round_2.png"

W, H = out.size
assert (W, H) == (1688, 1040), f"size mismatch: {W}x{H}"
out.save(OUT)
print(f"saved {W}x{H}  ->  {OUT}")
