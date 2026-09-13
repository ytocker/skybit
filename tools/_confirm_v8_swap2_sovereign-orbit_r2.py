#!/usr/bin/env python3
"""sovereign-orbit · confirm_purchase_v8 · swap-round-2 · round_2

Art-director fixes applied:
  - Aura peaks capped (70→45, 45→28) and layers increased to 18 so the
    falloff is smooth and the core plateaus below 200 luminance instead
    of clipping to 255.
  - Soft-glow bloom halved (peak 25→12) to kill the white hotspot.
  - Tier hue composited into the aura core via a normal-alpha tinted radial
    fill (gem colour at a≈60, r≈35) so tier colour reads at centre without
    additive accumulation.
  - LEGENDARY uses saturated hot-orange (255,138,30) for Zone A aura,
    clearly non-gold; Zone B lozenge stays gold (pal["glow"] = 220,160,40).
  - Sparkle positions re-seated: 4 of 8 moved to r≈60–72 so their white
    cores pop against dark card body instead of vanishing into centre glow.
  - Aura rendered off-screen then stretched 1.2× horizontally before
    blitting so the silhouette reads as a celestial orbit framing the
    coin+numeral pair, not a point-source spotlight.
"""
import os, sys, math
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, "/home/user/skybit")
import pygame; pygame.init(); pygame.display.set_mode((1, 1))
import game.store_cards as sc
from game.store_cards import (m, SS, font, vgrad_stops, bevel_rim, top_sheen,
                              coin_glyph, facet_gem, _alpha_aura,
                              plain_text, lerp_color, CABO_LO, CABO_HI, CARD_T,
                              CARD_B, CARD_RING_BRIGHT, CARD_RING_DEEP)
from PIL import Image, ImageDraw

# BLEND_ADD gloss_sweep fix — draw (v,v,v,255) so the additive amount
# follows the curve on a near-black body instead of blowing it white.
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

TIERS = [
    ("RARE",      "skin_wizard",    "720",   {"gem": (108, 188, 252), "glow": ( 60, 140, 230), "deep": (18,  44,  90)}),
    ("EPIC",      "skin_prism",     "1,400", {"gem": (194, 122, 248), "glow": (150,  60, 220), "deep": (44,  10,  80)}),
    ("LEGENDARY", "skin_astronaut", "2,600", {"gem": (255, 202, 104), "glow": (220, 160,  40), "deep": (90,  50,   0)}),
]
NAMES = {"RARE": "WIZARD", "EPIC": "PRISM", "LEGENDARY": "ASTRONAUT"}

POP_W, POP_H = 260, 442
CX = 130
CARD_X, CARD_TOP_Y, CARD_W, CARD_H, CARD_RAD = 10, 127, 240, 299, 23
DISC_CY, DISC_R = 135, 53
GEM_L_X, GEM_R_X, GEM_CY, GEM_R = 43, 217, 152, 14
ZA_CY = 247
Y_BANNER = 402
BOT_GEM_CY = 402
SHELF_X, SHELF_Y, SHELF_W, SHELF_H = 17, 335, 226, 91
BTN_W, BTN_H, BTN_RAD, BTN_CY, BTN_GAP = 99, 31, 12, 360, 10
BUY_CX = CX - (BTN_W + BTN_GAP) // 2
CAN_CX = CX + (BTN_W + BTN_GAP) // 2

# Hot orange for LEGENDARY Zone A so it reads clearly outside the gold
# hue family; the Zone B lozenge stays gold via pal["glow"].
LEGENDARY_GLOW = (255, 138, 30)


# ── shared structure ─────────────────────────────────────────────────────────

def card_body(big):
    rect = pygame.Rect(m(CARD_X), m(CARD_TOP_Y), m(CARD_W), m(CARD_H))
    rad = m(CARD_RAD)
    sc.drop_shadow(big, rect, rad, blur=m(8), alpha=165, dy=m(4))
    big.blit(vgrad_stops(rect.w, rect.h, rad,
                         [(0.0, CARD_T), (1.0, CARD_B)], 255, gamma=1.15),
             rect.topleft)
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


def name_text(big, name):
    nfs = 45
    nfnt = font(nfs)
    mw = m(CARD_W - 20)
    while sc._glyph_base(name, nfnt, 0).get_width() > mw and nfs > 24:
        nfs -= 1
        nfnt = font(nfs)
    plain_text(big, name, nfnt, (m(CX), m(213)), (250, 248, 240),
               shadow_a=160, weight=m(0.9), keyline=(6, 6, 16), kw=m(1.0))


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
    for cx_b, lbl, stops, lab_c, pk, rw in [
        (m(BUY_CX), "BUY",
         [(0.0, (38, 40, 84)), (1.0, (22, 24, 56))], (200, 205, 240), 22, m(2.0)),
        (m(CAN_CX), "CANCEL",
         [(0.0, (26, 28, 64)), (1.0, (14, 16, 44))], (150, 155, 200), 14, m(2.2)),
    ]:
        r = pygame.Rect(0, 0, m(BTN_W), m(BTN_H))
        r.center = (cx_b, m(BTN_CY))
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


def hero_disc(big, sid, pal):
    cx, cy, r = m(CX), m(DISC_CY), m(DISC_R)
    _alpha_aura(big, cx, cy, r + m(55), pal["glow"], peak=95, layers=24)
    _alpha_aura(big, cx, cy, r + m(20), pal["glow"], peak=70, layers=12)
    sc.cabochon(big, cx, cy, r, CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    try:
        sc.blit_thumb(big, sid, cx, cy, int(r * 1.5))
    except Exception:
        pygame.draw.circle(big, pal["gem"], (cx, cy), int(r * 0.7))
    sc.cabochon_glass(big, cx, cy, r, tint=pal["gem"])


# ── Zone A — sovereign-orbit ─────────────────────────────────────────────────

def _num_outline(surf, base, color, center, off):
    """Ring-stamp a tinted copy of the numeral mask at 8 compass offsets of
    `off` px so the glyph gains an even keyline of that colour."""
    kl = base.copy()
    kl.fill((*color, 255), special_flags=pygame.BLEND_RGBA_MULT)
    r = kl.get_rect(center=center)
    for ang in range(0, 360, 45):
        dx = int(round(off * math.cos(math.radians(ang))))
        dy = int(round(off * math.sin(math.radians(ang))))
        surf.blit(kl, (r.x + dx, r.y + dy))


def _sparkles(surf, cx, cy, color):
    """4-point sparkle burst — two sizes, irregular radii.  Positions with
    r≈60–72 are in the outer dark ring where white cores visually pop; 4 of
    the 8 are pushed there so they're not swallowed by the (now capped) aura."""
    specs = [
        (18,  66, 7),   # outer — already at dark ring
        (60,  70, 4),   # moved out (was 40) → dark ring
        (104, 58, 6),   # near-outer
        (150, 65, 5),   # moved out (was 34) → dark ring
        (202, 68, 7),   # outer
        (244, 72, 4),   # moved out (was 38) → dark ring
        (292, 60, 6),   # near-outer
        (336, 62, 5),   # moved out (was 46) → dark ring
    ]
    for ang, rad, L in specs:
        px = cx + int(m(rad) * math.cos(math.radians(ang)))
        py = cy + int(m(rad) * math.sin(math.radians(ang)))
        s = m(L)
        c = s + m(1)
        spk = pygame.Surface((s * 2 + m(2), s * 2 + m(2)), pygame.SRCALPHA)
        w = max(1, m(1))
        pygame.draw.line(spk, (*color, 180), (c - s, c), (c + s, c), w)
        pygame.draw.line(spk, (*color, 180), (c, c - s), (c, c + s), w)
        pygame.draw.circle(spk, (255, 255, 255, 200), (c, c), max(1, m(1)))
        surf.blit(spk, (px - c, py - c))


def _aura_orbit(surf, cx, cy, radius, color, peak, layers):
    """Render a circular aura into an off-screen buffer, then stretch it
    1.2× horizontally before blitting so the combined field reads as an
    elliptical orbit encircling the coin+numeral pair, not a point spotlight."""
    diam = radius * 2 + 4
    tmp = pygame.Surface((diam, diam), pygame.SRCALPHA)
    tc = diam // 2
    # render into temp buffer — normal-alpha composite, no additive here
    _alpha_aura(tmp, tc, tc, radius, color, peak=peak, layers=layers)
    new_w = int(diam * 1.2)
    scaled = pygame.transform.smoothscale(tmp, (new_w, diam))
    surf.blit(scaled, (cx - new_w // 2, cy - diam // 2))


def _tier_tint_core(surf, cx, cy, gem_color):
    """Semi-transparent tier-coloured radial fill composited AFTER the aura
    passes so the tier hue saturates the core without any additive blowout.
    Sits under the gloss layer; r≈35 keeps it tight around the coin glyph."""
    r35 = m(35)
    tint = pygame.Surface((r35 * 2 + 2, r35 * 2 + 2), pygame.SRCALPHA)
    pygame.draw.circle(tint, (*gem_color, 60), (r35 + 1, r35 + 1), r35)
    surf.blit(tint, (cx - r35 - 1, cy - r35 - 1))


def zone_a(big, tier_word, price_str, pal):
    """Coin glyph (left) + price numeral (right) float as a matched celestial
    pair in a shared tier aura — no enclosing plate, just dark card body."""
    cx, cy = m(CX), m(ZA_CY)
    # LEGENDARY gets hot orange in Zone A so it's distinct from the gold
    # Zone B lozenge; other tiers use their own glow colour.
    glow_col = LEGENDARY_GLOW if tier_word == "LEGENDARY" else pal["glow"]

    # 1) elliptical orbit aura — peaks reduced (45, 28) and layers raised to
    #    18 so the falloff is smooth and the centre never clips to 255.
    #    soft_glow omitted entirely: BLEND_ADD ignores fill alpha and adds the
    #    full gem-colour value per layer, causing white blowout even at low
    #    peak values.  The tier-tint core below handles centre saturation.
    _aura_orbit(big, cx, cy, m(82), glow_col, peak=45, layers=18)
    _aura_orbit(big, cx, cy, m(50), glow_col, peak=28, layers=18)

    # 2) tier-tinted core — normal-alpha radial fill ensures tier hue dominates
    #    the centre; sits under the coin glyph, not additive.
    _tier_tint_core(big, cx, cy, pal["gem"])

    # 3) hero coin with a tight gem-halo so it reads as a lit body.
    coin_cx, coin_cy = m(CX - 48), cy
    _alpha_aura(big, coin_cx, coin_cy, m(26), pal["gem"], peak=40, layers=6)
    coin_glyph(big, coin_cx, coin_cy, m(22))

    # 4) price numeral: 3-layer edges (outer gem ring → dark keyline →
    #    coin-metal gradient fill).  Numeral lands on dark card body — no
    #    bright hotspot behind it now that centre blowout is fixed.
    nf = font(22)
    base = sc._stamp_bold(sc._glyph_base(price_str, nf, 0), m(0.9))
    bw, bh = base.get_size()
    num_center = (m(CX + 72) - bw // 2, cy)
    _num_outline(big, base, pal["gem"], num_center, m(2.5))
    _num_outline(big, base, (8, 6, 18), num_center, m(1.8))
    fill = vgrad_stops(bw, bh, 0, sc._SOVEREIGN_NUM_STOPS, 255)
    gold = base.copy()
    gold.blit(fill, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    big.blit(gold, gold.get_rect(center=num_center))

    # 5) sparkle burst — positions biased to the outer dark ring.
    _sparkles(big, cx, cy, pal["gem"])


# ── render loop ──────────────────────────────────────────────────────────────

def render_popup(tier_word, sid, price_str, pal):
    big = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)
    card_body(big)
    corner_gems(big, pal)
    name_text(big, NAMES[tier_word])
    zone_a(big, tier_word, price_str, pal)
    shelf_and_buttons(big)
    sc._ribbon(big, tier_word, m(CX), m(Y_BANNER), m(146), pal)
    bottom_gems(big, pal)
    hero_disc(big, sid, pal)
    return pygame.transform.smoothscale(big, (POP_W, POP_H))


MARGIN, HEAD, GAP = 20, 58, 12
STRIP_W = MARGIN * 2 + len(TIERS) * (POP_W + GAP) - GAP
STRIP_H = HEAD + POP_H + MARGIN
strip = Image.new("RGB", (STRIP_W, STRIP_H), (8, 8, 20))
idr = ImageDraw.Draw(strip)
idr.text((MARGIN, 18), "sovereign-orbit · swap-round-2 · round_2",
         fill=(232, 226, 208))
for i, (tw, sid, ps, pal) in enumerate(TIERS):
    pop = render_popup(tw, sid, ps, pal)
    pil = Image.frombytes("RGB", (POP_W, POP_H), pygame.image.tostring(pop, "RGB"))
    x = MARGIN + i * (POP_W + GAP)
    strip.paste(pil, (x, HEAD))
    idr.text((x + POP_W // 2, HEAD + POP_H + 6), tw,
             fill=(180, 176, 210), anchor="mt")

out = strip.resize((STRIP_W * 2, STRIP_H * 2), Image.LANCZOS)

import pathlib
OUTDIR = "/home/user/skybit/docs/confirm_purchase_v8/swap-round-2/sovereign-orbit"
pathlib.Path(OUTDIR).mkdir(parents=True, exist_ok=True)
OUT = OUTDIR + "/round_2.png"

# ── PIL-only verification (never view inline) ─────────────────────────────────
W, H = out.size
assert (W, H) == (1688, 1040), f"size mismatch: {W}x{H}"

# non-blank check
cx_px, cy_px = W // 2, H // 2
centre = out.getpixel((cx_px, cy_px))
assert any(v > 10 for v in centre), "image appears blank"

# EPIC column centre positions in the final 2× image:
#   x_start = (MARGIN + 1*(POP_W+GAP)) * 2 = (20+272)*2 = 584
#   ZA_CY row = (HEAD + ZA_CY) * 2 = (58+247)*2 = 610
EPIC_ZA_X, EPIC_ZA_Y = 844, 610
r, g, b = out.getpixel((EPIC_ZA_X, EPIC_ZA_Y))
lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
print(f"  EPIC Zone A core ({EPIC_ZA_X},{EPIC_ZA_Y}): RGB=({r},{g},{b})  lum={lum:.1f}")
assert lum <= 200, (
    f"EPIC core blowout: lum={lum:.1f} exceeds 200  pixel=({r},{g},{b})")
print(f"    lum ≤ 200  [PASS]")

# EPIC Zone A should be purple-tinted (b or r > g)
assert b > g or r > g, f"EPIC core hue not purple: ({r},{g},{b})"
print(f"    hue purple-family  [PASS]")

# LEGENDARY column positions:
#   x_start = (MARGIN + 2*(POP_W+GAP)) * 2 = (20+544)*2 = 1128
#   centre x = 1128 + POP_W = 1388
LEG_ZA_X, LEG_ZA_Y = 1388, 610
lr, lg, lb = out.getpixel((LEG_ZA_X, LEG_ZA_Y))
leg_lum = 0.2126 * lr + 0.7152 * lg + 0.0722 * lb
print(f"  LEGENDARY Zone A ({LEG_ZA_X},{LEG_ZA_Y}): RGB=({lr},{lg},{lb})  lum={leg_lum:.1f}")
assert lr > lb, (
    f"LEGENDARY Zone A not orange-family: r={lr} < b={lb}  ({lr},{lg},{lb})")
print(f"    hue orange-family (r>b)  [PASS]")

# LEGENDARY Zone B ribbon: Y_BANNER row = (HEAD + Y_BANNER) * 2 = (58+402)*2 = 920
LEG_ZB_X, LEG_ZB_Y = 1388, 920
br2, bg2, bb2 = out.getpixel((LEG_ZB_X, LEG_ZB_Y))
print(f"  LEGENDARY Zone B ({LEG_ZB_X},{LEG_ZB_Y}): RGB=({br2},{bg2},{bb2})")
za_orange = lr > lb and (lr - lb) > 20
zb_hue = "gold/warm" if br2 >= bb2 else "cool"
print(f"    Zone A orange={za_orange}, Zone B={zb_hue}  hue-sep={'OK' if za_orange else 'WARN'}")

# RARE dark-card background sample well away from Zone A (card body mid area)
# y=750 lands in the shelf zone which should be dark indigo regardless of aura
RARE_BODY_X, RARE_BODY_Y = 300, 750
rb, gb2, bb3 = out.getpixel((RARE_BODY_X, RARE_BODY_Y))
body_lum = 0.2126 * rb + 0.7152 * gb2 + 0.0722 * bb3
print(f"  Card body sample ({RARE_BODY_X},{RARE_BODY_Y}): RGB=({rb},{gb2},{bb3})  lum={body_lum:.1f}")

out.save(OUT)
print(f"\nsaved {W}×{H}  →  {OUT}")
