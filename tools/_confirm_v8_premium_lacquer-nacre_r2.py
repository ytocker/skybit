#!/usr/bin/env python3
"""lacquer-nacre · confirm_purchase_v8 · premium-v1 · round_2

Four art-director fixes applied to the locked popup geometry:
  1. Branch flourish rebuilt as opaque takamaki-e relief strokes (lum ≥150)
  2. BUY button re-skinned to warm amber-red lacquer gradient so it
     dominates CANCEL unambiguously
  3. Zone A gold keyline thickened to ≥m(1.5) so it holds at 1× downscale
  4. Low-alpha nacre chips lifted to ≥160 (card body) / ≥150 (Zone B)
"""
import os, sys, math

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame
pygame.init()
pygame.display.set_mode((1, 1))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import game.store_cards as sc


# Mandatory gloss_sweep patch — the stock sweep BLEND_ADDs (255,255,255,a),
# which blows the near-black urushi field to white at the crown. This ellipse
# variant keeps the additive amount low and eased so the lacquer stays dark.
def _safe_gloss(surf, rect, radius, peak=46):
    w, h = rect[2], rect[3]
    gsurf = pygame.Surface((w, h), pygame.SRCALPHA)
    gsurf.fill((0, 0, 0, 0))
    steps = 10
    for i in range(steps):
        t = i / (steps - 1)
        alpha = int(peak * (1 - t))
        bar_h = max(1, int(h * 0.45 * (1 - t)))
        pygame.draw.ellipse(gsurf, (255, 255, 255, alpha),
                            (int(w * 0.1), int(h * 0.04 + i * 1.5),
                             int(w * 0.8), bar_h))
    surf.blit(gsurf, (rect[0], rect[1]))
sc.gloss_sweep = _safe_gloss

from game.store_cards import (vgrad_stops, plain_text, m, SS, font,
                              CABO_LO, CABO_HI, CARD_T, CARD_B,
                              CARD_RING_BRIGHT, CARD_RING_DEEP)
from PIL import Image, ImageDraw

# ── palettes ────────────────────────────────────────────────────────────────
PALETTES = {
    "RARE":      {"gem": (108, 188, 252), "deep": (28, 60, 120), "glow": (160, 210, 255)},
    "EPIC":      {"gem": (194, 122, 248), "deep": (72, 28, 120), "glow": (230, 160, 255)},
    "LEGENDARY": {"gem": (255, 202, 104), "deep": (120, 72, 12), "glow": (255, 230, 140)},
}
TIERS = [
    ("RARE", "skin_wizard", "720"),
    ("EPIC", "skin_prism", "1,400"),
    ("LEGENDARY", "skin_astronaut", "2,600"),
]
NAMES = {"RARE": "WIZARD", "EPIC": "PRISM", "LEGENDARY": "ASTRONAUT"}

# LEGENDARY Zone B diverges into an oxblood/vermilion lacquer family so the
# banner reads as a different urushi colourway from the gold Zone A — the two
# lacquer moments never collapse into one warm smear.
LEG_BANNER_PAL = {"gem": (176, 52, 40), "deep": (74, 18, 14), "glow": (214, 96, 72)}

# ── locked geometry ─────────────────────────────────────────────────────────
POP_W, POP_H = 260, 442
CX = 130
CARD_X, CARD_TOP_Y, CARD_W, CARD_H, CARD_RAD = 10, 127, 240, 299, 23
DISC_CY, R_HERO = 135, 53
GEM_L_X, GEM_R_X, GEM_CY, GEM_R = 43, 217, 152, 14
CHIP_CY = 247
Y_BANNER = 402
BOT_GEM_CY = 402
SHELF_X, SHELF_Y, SHELF_W, SHELF_H = 17, 335, 226, 91
BTN_W, BTN_H, BTN_RAD, BTN_CY, BTN_GAP = 99, 31, 12, 360, 10
BUY_CX = CX - (BTN_W + BTN_GAP) // 2
CAN_CX = CX + (BTN_W + BTN_GAP) // 2

# Raden = pale pearl chip with a cool-tint edge. Kept crisp and individually
# readable at 1× so each fleck reads as a discrete glint, never a texture.
PEARL = (224, 232, 236)
PEARL_EDGE = (150, 196, 214, 180)


def _nacre_chip(big, cx, cy, r, fill_a=255, oval=False):
    """One discrete raden chip: a >=2-device-px pale-pearl fill with a single
    cool-tint edge pixel. Ovals sell the shell-cut irregularity of inlay."""
    pad = m(2)
    surf = pygame.Surface((r * 2 + pad * 2, r * 2 + pad * 2), pygame.SRCALPHA)
    c = r + pad
    if oval:
        rect = pygame.Rect(c - r, c - int(r * 0.62), r * 2, int(r * 1.24))
        pygame.draw.ellipse(surf, (*PEARL, fill_a), rect)
        pygame.draw.ellipse(surf, PEARL_EDGE, rect, max(1, m(0.6)))
    else:
        pygame.draw.circle(surf, (*PEARL, fill_a), (c, c), r)
        pygame.draw.circle(surf, PEARL_EDGE, (c, c), r, max(1, m(0.6)))
    big.blit(surf, (cx - c, cy - c))


# ── card body ───────────────────────────────────────────────────────────────

def card_body(big):
    rect = pygame.Rect(m(CARD_X), m(CARD_TOP_Y), m(CARD_W), m(CARD_H))
    rad = m(CARD_RAD)
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

    # One takamaki-e gold hairline crossing the flat lacquer ground on a gentle
    # diagonal — the raised-relief signature of the technique, kept very low
    # contrast so it whispers rather than stripes the card.
    hair = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.line(hair, (86, 50, 8, 30),
                     (m(30), m(70)), (m(210), m(230)), max(1, m(4)))
    big.blit(hair, rect.topleft)

    # Raden scatter at FIXED coords — alpha raised to ≥160 so each fleck is
    # individually readable at 1× downscale rather than vanishing to sub-pixel.
    for lx, ly, rr, a in [
        (80, 280, 1.5, 170), (170, 300, 2.0, 165), (110, 310, 1.5, 160),
        (190, 270, 2.0, 168), (150, 320, 1.5, 162), (90, 265, 2.0, 165),
    ]:
        _nacre_chip(big, m(lx), m(ly), m(rr), fill_a=a)


def corner_gems(big, pal):
    sc.facet_gem(big, m(GEM_L_X), m(GEM_CY), m(GEM_R), pal["gem"], pal["deep"])
    sc.facet_gem(big, m(GEM_R_X), m(GEM_CY), m(GEM_R), pal["gem"], pal["deep"])


def name_text(big, name):
    nfs = 45
    nfnt = font(nfs)
    mw = m(CARD_W - 20)
    while sc._glyph_base(name, nfnt, 0).get_width() > mw and nfs > 24:
        nfs -= 1
        nfnt = font(nfs)
    plain_text(big, name, nfnt, (m(CX), m(213)), (250, 248, 240),
               shadow_a=160, weight=m(0.9), keyline=(6, 6, 16), kw=m(1.0))


# ── Zone A: black urushi price plaque ───────────────────────────────────────

def zone_a_chip(big, price_str):
    """Black lacquer plaque with a gold takamaki-e keyline rim and a sparse row
    of discrete raden chips inlaid along each long edge. The gold keyline is
    explicitly re-stroked at ≥m(1.5) after the _dark_chip_body call so it
    survives the 1× downscale as a continuous line, not a sub-pixel ghost."""
    r = pygame.Rect(m(20), m(CHIP_CY - 20), m(220), m(40))
    radius = m(8)
    # Deep-black urushi fill; rim_dark = burnt gold contact, rim_bright = the
    # bright takamaki-e gold keyline.
    sc._dark_chip_body(big, r, radius,
                       [(0.0, (24, 22, 30)), (1.0, (12, 11, 18))],
                       rim_dark=(70, 52, 14), rim_bright=(255, 240, 190),
                       gloss=14)

    # _dark_chip_body passes w=m(1.5) to bevel_rim which draws the bright inner
    # at w//2 = 1 SS-px — sub-pixel at 1×. Re-stroke just inside the dark outer
    # at m(1.5) width so the gold keyline holds as a continuous line at 1×.
    dk_w = max(1, m(1.6))          # matches _dark_chip_body's dark outer width
    inner_bright = r.inflate(-dk_w * 2, -dk_w * 2)
    pygame.draw.rect(big, (255, 240, 190, 240), inner_bright,
                     width=max(2, m(1.5)),
                     border_radius=max(1, radius - dk_w))

    # Nacre-inlay border: 3 discrete chips per long edge, spaced >=6 logical px,
    # seated just inside the gold keyline. DISCRETE — never a continuous band.
    inset = m(7)
    for xx in (CX - 62, CX, CX + 62):
        _nacre_chip(big, m(xx), r.top + inset, m(2), fill_a=235)
        _nacre_chip(big, m(xx), r.bottom - inset, m(2), fill_a=235)

    # Coin + numeral inline, centred on the plaque.
    txt = price_str
    num_font = font(20)
    coin_r = m(11)
    gap = m(5)
    num_w = num_font.size(txt)[0]
    total = coin_r * 2 + gap + num_w
    left = m(CX) - total // 2
    coin_cx = left + coin_r
    num_cx = left + coin_r * 2 + gap + num_w // 2
    sc.coin_glyph(big, coin_cx, m(CHIP_CY), coin_r)
    plain_text(big, txt, num_font, (num_cx, m(CHIP_CY) + m(1)), (236, 240, 232),
               shadow_a=100, weight=m(1.0), keyline=(8, 6, 18), kw=m(1.2))


# ── dead zone: three bold takamaki-e branch strokes ─────────────────────────

def dead_zone_flourish(big):
    """Three bold lacquer-art branch strokes filling the empty band (y~259..335).
    Each stroke is a two-pass relief: an opaque dark base at full alpha gives it
    physical depth, then a bright gold glint on the same path gives it lustre.
    This guarantees lum ≥150 on the branch spine so it ties the blossom chips
    together as a coherent gold-and-pearl flourish rather than a smudge."""
    layer = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)

    # Spine: gently arched main branch
    p0 = (m(CX - 40), m(300))
    p1 = (m(CX), m(292))
    p2 = (m(CX + 42), m(302))
    # Two bold offshoots replace the previous aliased m(1) arcs — drawn as
    # solid line segments so they retain mass at 1× downscale.
    b1_end = (m(CX - 20), m(281))   # left branch rising off the spine
    b2_end = (m(CX + 22), m(282))   # right branch rising off the spine

    base_w = max(2, m(2.5))   # opaque dark relief width — substantial, not hairline
    glint_w = max(1, m(1))    # gold glint sits centred on the relief path

    for pts in [
        [p0, p1, p2],   # main arched spine
        [p1, b1_end],   # left branch from apex
        [p1, b2_end],   # right branch from apex
    ]:
        # Dark base first — full alpha 255 so the stroke has physical opaque mass.
        pygame.draw.lines(layer, (40, 26, 6, 255), False, pts, base_w)
        # Gold glint directly on top — the bright lacquer enamel surface catch.
        pygame.draw.lines(layer, (230, 196, 110, 220), False, pts, glint_w)

    big.blit(layer, (0, 0))

    # Nacre blossom chips at every branch tip — the inlay accent that ties the
    # gold-and-pearl language together. Alpha kept at 210 (art-director: "fine").
    for tip in [p0, p2, b1_end, b2_end]:
        _nacre_chip(big, tip[0], tip[1], m(2), fill_a=210, oval=True)


# ── shelf + buttons ─────────────────────────────────────────────────────────

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
    sc.top_sheen(shelf, shelf.get_rect(), 0, m(20), peak=35)
    pygame.draw.line(shelf, (115, 106, 140), (0, 0), (shelf_rect.w - 1, 0),
                     max(1, m(1)))
    seat = pygame.Surface((shelf_rect.w, m(6)), pygame.SRCALPHA)
    for yy in range(m(6)):
        pygame.draw.line(seat, (0, 0, 0, int(120 * (1 - yy / m(6)))),
                         (0, yy), (shelf_rect.w - 1, yy))
    big.blit(seat, (shelf_rect.x, shelf_rect.y - m(6)))
    big.blit(shelf, shelf_rect.topleft)
    br = m(BTN_RAD)

    # BUY gets a warm amber-red lacquer fill so it reads as the primary action
    # at a glance — warm vs. CANCEL's cool navy creates immediate visual hierarchy.
    # CANCEL fill stays neutral navy; no change to its palette.
    for cx_b, lbl, stops, lab_c, pk, rw in [
        (m(BUY_CX), "BUY",
         [(0.0, (100, 50, 20)), (1.0, (60, 25, 10))],
         (246, 228, 192), 22, m(2.0)),
        (m(CAN_CX), "CANCEL",
         [(0.0, (26, 28, 64)), (1.0, (14, 16, 44))], (150, 155, 200), 14, m(2.2)),
    ]:
        r = pygame.Rect(0, 0, m(BTN_W), m(BTN_H))
        r.center = (cx_b, m(BTN_CY))
        sc.drop_shadow(big, r, br, blur=m(3), alpha=100, dy=m(2))
        big.blit(vgrad_stops(r.w, r.h, br, stops, 255), r.topleft)
        sc.top_sheen(big, r, br, m(12), peak=pk)
        sc.bevel_rim(big, r, br, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 230),
                     w=max(1, rw))
        plain_text(big, lbl, font(14 if lbl == "BUY" else 13), r.center, lab_c,
                   shadow_a=110, weight=m(0.8), keyline=(8, 6, 20), kw=m(0.9))


def bottom_gems(big, pal):
    for gx in [m(GEM_L_X), m(GEM_R_X)]:
        sc._alpha_aura(big, gx, m(BOT_GEM_CY), m(16), pal["glow"], peak=60, layers=14)
        sc.facet_gem(big, gx, m(BOT_GEM_CY), m(GEM_R), pal["gem"], pal["deep"])


# ── Zone B: rarity ribbon lozenge ───────────────────────────────────────────

def zone_b_banner(big, tier_word, pal):
    banner_pal = LEG_BANNER_PAL if tier_word == "LEGENDARY" else pal
    sc._ribbon_lozenge(big, tier_word, m(CX), m(Y_BANNER), m(146), banner_pal)
    # Discrete raden chips seated along the lozenge's upper edge — raised to
    # alpha ≥150 so they read at 1× alongside the Zone A border chips.
    f = font(8.5)
    tw = sc._glyph_base(tier_word, f, m(1.4)).get_width()
    w = min(m(146), tw + m(14) * 2)
    edge_y = m(Y_BANNER) - m(4)
    for frac in (0.28, 0.5, 0.72):
        xx = m(CX) - w // 2 + int(w * frac)
        _nacre_chip(big, xx, edge_y, m(2), fill_a=155)


# ── hero disc ───────────────────────────────────────────────────────────────

def hero_disc(big, sid, pal):
    cx, cy, r = m(CX), m(DISC_CY), m(R_HERO)
    sc._alpha_aura(big, cx, cy, r + m(55), pal["glow"], peak=95, layers=24)
    sc._alpha_aura(big, cx, cy, r + m(20), pal["glow"], peak=70, layers=12)
    sc.cabochon(big, cx, cy, r, CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    try:
        sc.blit_thumb(big, sid, cx, cy, int(r * 1.5))
    except Exception:
        pygame.draw.circle(big, pal["gem"], (cx, cy), int(r * 0.7))
    sc.cabochon_glass(big, cx, cy, r, tint=pal["gem"])
    # ONE thin tier ring — the gold rim of the cabochon itself is the
    # takamaki-e keyline, so this is a single translucent tier accent, not a
    # second gold ring.
    ring = pygame.Surface((r * 2 + m(6), r * 2 + m(6)), pygame.SRCALPHA)
    rc = r + m(3)
    pygame.draw.circle(ring, (*pal["glow"], 140), (rc, rc), r, max(1, m(1)))
    big.blit(ring, (cx - rc, cy - rc))


# ── render loop ─────────────────────────────────────────────────────────────

def render_popup(tier_word, sid, price_str, pal):
    big = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)
    card_body(big)
    corner_gems(big, pal)
    name_text(big, NAMES[tier_word])
    zone_a_chip(big, price_str)
    dead_zone_flourish(big)
    shelf_and_buttons(big)
    zone_b_banner(big, tier_word, pal)
    bottom_gems(big, pal)
    hero_disc(big, sid, pal)
    return pygame.transform.smoothscale(big, (POP_W, POP_H))


MARGIN, HEAD, GAP = 20, 58, 12
STRIP_W = MARGIN * 2 + len(TIERS) * (POP_W + GAP) - GAP
STRIP_H = HEAD + POP_H + MARGIN
strip = Image.new("RGB", (STRIP_W, STRIP_H), (8, 8, 20))
idr = ImageDraw.Draw(strip)
idr.text((MARGIN, 18), "lacquer-nacre · premium-v1 · round_2  "
         "(branch rebuilt · BUY lacquer fill · rim thickened · nacre alpha lifted)",
         fill=(232, 226, 208))

for tw, sid, ps in TIERS:
    pal = PALETTES[tw]
    pop = render_popup(tw, sid, ps, pal)
    col_i = ["RARE", "EPIC", "LEGENDARY"].index(tw)
    pil = Image.frombytes("RGB", (POP_W, POP_H), pygame.image.tostring(pop, "RGB"))
    x = MARGIN + col_i * (POP_W + GAP)
    strip.paste(pil, (x, HEAD))
    idr.text((x + POP_W // 2, HEAD + POP_H + 6), tw, fill=(180, 176, 210),
             anchor="mt")

out = strip.resize((STRIP_W * 2, STRIP_H * 2), Image.LANCZOS)
import pathlib
OUT_DIR = pathlib.Path(
    "/home/user/skybit/docs/confirm_purchase_v8/premium-v1/lacquer-nacre")
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT = str(OUT_DIR / "round_2.png")
out.save(OUT)
print(f"saved {out.size[0]}x{out.size[1]}  ->  {OUT}")

# ── verification (PIL only; never view the image) ───────────────────────────
img = Image.open(OUT).convert("RGB")
W, H = img.size
assert (W, H) == (STRIP_W * 2, STRIP_H * 2), f"size mismatch {W}x{H}"
lums = set()
for sx in range(0, W, 40):
    for sy in range(0, H, 40):
        r, g, b = img.getpixel((sx, sy))
        lums.add(int(0.299 * r + 0.587 * g + 0.114 * b))
assert len(lums) > 30, f"image looks blank: {len(lums)} lum values"
print(f"size {W}x{H}, {len(lums)} distinct sample lum values — OK")

# Spot-check: sample the branch zone to confirm lum >=150 on the gold strokes.
# The branch occupies y~292-310 on the 1x popup (260x442); after 2x strip scale
# the RARE column starts at MARGIN pixels in.
branch_lums = []
bx_lo = int(MARGIN * 2 + (CX - 45) * 2)
bx_hi = int(MARGIN * 2 + (CX + 47) * 2)
by_lo = int((HEAD + 281) * 2)
by_hi = int((HEAD + 310) * 2)
for sx in range(bx_lo, min(bx_hi, W), 2):
    for sy in range(by_lo, min(by_hi, H), 2):
        rr, gg, bb = img.getpixel((sx, sy))
        branch_lums.append(int(0.299 * rr + 0.587 * gg + 0.114 * bb))
max_branch_lum = max(branch_lums) if branch_lums else 0
print(f"branch zone max lum: {max_branch_lum}  (target >=150)")
assert max_branch_lum >= 150, (
    f"branch flourish too dark: max lum {max_branch_lum} < 150")

# Spot-check: BUY button fill should be warmer (higher R channel) than CANCEL.
# Both buttons are in the RARE column (leftmost); BUY is at CX - half button gap.
buy_cx_strip = int((MARGIN + BUY_CX) * 2)
can_cx_strip = int((MARGIN + CAN_CX) * 2)
btn_cy_strip = int((HEAD + BTN_CY) * 2)
buy_r, buy_g, buy_b = img.getpixel((buy_cx_strip, btn_cy_strip))
can_r, can_g, can_b = img.getpixel((can_cx_strip, btn_cy_strip))
buy_lum = int(0.299 * buy_r + 0.587 * buy_g + 0.114 * buy_b)
can_lum = int(0.299 * can_r + 0.587 * can_g + 0.114 * can_b)
print(f"BUY centre RGB {(buy_r,buy_g,buy_b)} lum {buy_lum}")
print(f"CANCEL centre RGB {(can_r,can_g,can_b)} lum {can_lum}")
# Warmth is the red/blue ratio: amber BUY should be red-dominant (R >> B)
# while CANCEL is blue-dominant (B >> R). Comparing ratios is robust to
# sampling text pixels instead of fill — the hue relationship still holds.
buy_warmth = buy_r / max(1, buy_b)
can_warmth = can_r / max(1, can_b)
assert buy_warmth > can_warmth * 1.5, (
    f"BUY not warmer than CANCEL: BUY R/B={buy_warmth:.2f} vs "
    f"CANCEL R/B={can_warmth:.2f}")
print(f"BUY R/B ratio {buy_warmth:.2f} >> CANCEL R/B ratio {can_warmth:.2f} — OK")
print("BUY/CANCEL warmth check — OK")
print("all verifications passed")
