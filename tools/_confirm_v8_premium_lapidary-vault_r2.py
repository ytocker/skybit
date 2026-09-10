#!/usr/bin/env python3
"""lapidary-vault · confirm_purchase_v8 · premium-v1 · round_2

All art-director critique notes from round_1 addressed:
1. Dead-zone octagon: 2-3 facet edges in tier gem colour at alpha ~80 ghost the
   octagonal table shape; girdle-glint raised to (140,120,180,150) for a single
   bright catch.
2. Graticule: one concentrated angled band (~5 parallel lines at 20°) + 3
   perpendicular crosshatch lines, all (37,37,78) at alpha ~70.  Rest of body is
   clean dark.
3. Platinum chip: 3-stop blue-steel gradient (86,94,116)→(60,68,88)→(40,46,64);
   b-channel dominant so Zone A reads unambiguously cooler than LEGENDARY amber.
4. Zone A pips: ONE facet_gem per side (2 total) at r=m(5), centred on CHIP_CY.
5. Zone B lozenge end-cap gems at x=m(64)/m(196) removed; big bottom gems at
   x=43/217 are the sole accent at that level.
6. BUY button: steel-blue-to-purple gradient clearly brighter than CANCEL;
   CANCEL stays cool-dark so the purchase action is the visual hero.
"""
import os, sys, math
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame
pygame.init()
pygame.display.set_mode((1, 1))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import game.store_cards as sc


# gloss_sweep on a near-black body via BLEND_ADD blows white unless the additive
# amount follows the falloff curve — draw (a,a,a,255) rather than white-alpha so
# the platinum channel keeps its steel value.
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
            (int(w * 0.1), int(h * 0.04 + i * 1.5), int(w * 0.8), bar_h))
    surf.blit(gsurf, (rect[0], rect[1]))
sc.gloss_sweep = _safe_gloss

from game.store_cards import (m, SS, font, vgrad_stops, plain_text, coin_glyph,
                              facet_gem, cabochon, cabochon_glass, drop_shadow,
                              top_sheen, bevel_rim, blit_thumb, _dark_chip_body,
                              _ribbon_lozenge, _alpha_aura, _glyph_base,
                              _stamp_bold, PRICE_STOPS, CARD_T, CARD_B)
from PIL import Image, ImageDraw


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

# Local lapidary keyline colours (cool indigo lattice) — distinct from the gold
# CARD_RING_* the module uses for bezels; these are the cut-table interior lines.
CARD_RING_DEEP = (22, 24, 56)
CARD_RING_BRIGHT = (104, 96, 168)

POP_W, POP_H = 260, 442
CX = POP_W // 2
CARD_X, CARD_W, CARD_TOP, CARD_H, CARD_RAD = 10, 240, 127, 299, 23
R_HERO, DISC_CY = 53, 135
GEM_R, GEM_CY, GEM_L_X, GEM_R_X = 14, 152, 43, 217
NAME_FS, Y_NAME = 45, 213
CHIP_CY = 247
Y_BANNER, BANNER_W = 402, 146
BOT_GEM_CY = 402
SHELF_X, SHELF_Y, SHELF_W, SHELF_H = 17, 335, 226, 91
BTN_W, BTN_H, BTN_RAD, BTN_CY, BTN_GAP = 99, 31, 12, 360, 10
BUY_CX = CX - (BTN_W + BTN_GAP) // 2
CAN_CX = CX + (BTN_W + BTN_GAP) // 2


# ── card body + lapidary interior ────────────────────────────────────────────
def card_body(big, pal):
    rect = pygame.Rect(m(CARD_X), m(CARD_TOP), m(CARD_W), m(CARD_H))
    rad = m(CARD_RAD)
    drop_shadow(big, rect, rad, blur=m(8), alpha=165, dy=m(4))
    big.blit(vgrad_stops(rect.w, rect.h, rad, [(0.0, CARD_T), (1.0, CARD_B)],
                         255, gamma=1.15), rect.topleft)
    top_sheen(big, rect, rad, m(30), peak=56)

    # ONE angled facet-plane band concentrated in the mid-card zone — 5 parallel
    # lines at 20° plus 3 perpendicular crosshatch lines at the same alpha so it
    # reads as intentional stone grain, not uniform noise across the full body.
    lat = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    ang = math.radians(20)
    dxb, dyb = math.cos(ang), math.sin(ang)     # direction along band lines
    pxb, pyb = -math.sin(ang), math.cos(ang)    # perpendicular across the band
    band_cx = rect.w * 0.5
    band_cy = rect.h * 0.52                     # centred in the dead-zone band
    ext = max(rect.w, rect.h) * 2.0             # extend past card edges before masking
    grain_col = (37, 37, 78, 70)
    # m(2) = 4 device px → 2 logical px after downscale — the minimum width that
    # survives smoothscale and LANCZOS as a readable line at 1× game resolution.
    grain_w = max(1, m(2))
    for k in range(-2, 3):                      # 5 parallel lines
        ox = band_cx + k * m(9) * pxb
        oy = band_cy + k * m(9) * pyb
        pygame.draw.line(lat, grain_col,
                         (int(ox - dxb * ext), int(oy - dyb * ext)),
                         (int(ox + dxb * ext), int(oy + dyb * ext)),
                         grain_w)
    for k in (-1, 0, 1):                        # 3 crosshatch lines at 90° to band
        ox = band_cx + k * m(20) * dxb
        oy = band_cy + k * m(20) * dyb
        pygame.draw.line(lat, grain_col,
                         (int(ox - pxb * ext), int(oy - pyb * ext)),
                         (int(ox + pxb * ext), int(oy + pyb * ext)),
                         grain_w)
    lmask = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(lmask, (255, 255, 255, 255), lmask.get_rect(), border_radius=rad)
    lat.blit(lmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(lat, rect.topleft)

    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    bevel_rim(big, rect, rad, sc.CARD_RING_DEEP, (*sc.CARD_RING_BRIGHT, 230),
              w=max(1, m(1.9)))
    tray = rect.inflate(-m(8), -m(8))
    pygame.draw.rect(big, (*sc.CARD_RING_BRIGHT, 55), tray,
                     width=max(1, m(1)), border_radius=rad - m(3))


def corner_gems(big, pal):
    facet_gem(big, m(GEM_L_X), m(GEM_CY), m(GEM_R), pal["gem"], pal["deep"])
    facet_gem(big, m(GEM_R_X), m(GEM_CY), m(GEM_R), pal["gem"], pal["deep"])


def name_text(big, name):
    fs = NAME_FS
    nf = font(fs)
    mw = m(CARD_W - 20)
    while _glyph_base(name, nf, 0).get_width() > mw and fs > 24:
        fs -= 1
        nf = font(fs)
    plain_text(big, name, nf, (m(CX), m(Y_NAME)), (250, 248, 240), shadow_a=160,
               weight=m(0.9), keyline=(6, 6, 16), kw=m(1.0))


# ── dead-zone cut-stone ghost motif ──────────────────────────────────────────
def dead_zone(big, pal):
    """Ghosted octagonal table in the empty band between chip and shelf —
    3 scattered facet edges in tier colour at alpha ~80 register the octagonal
    form; a single bright girdle-glint catches the top-left light."""
    dz = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)
    cx, cy = m(CX), m(297)          # centred in the ~259→335 dead band
    rr = m(25)                      # ~50 logical px wide octagon
    rot = -math.pi / 2 - math.pi / 8
    oct8 = [(cx + rr * math.cos(rot + 2 * math.pi * i / 8),
             cy + rr * math.sin(rot + 2 * math.pi * i / 8)) for i in range(8)]
    # faint base polygon so the overall shape has a ghost fill
    pygame.draw.polygon(dz, (*pal["deep"], 30), oct8, width=max(1, m(1)))
    # 3 scattered facet edges in tier colour — together they read as an octagon.
    # m(2) = 4 device px → 2 logical px at 1×, the floor for resolving past
    # anti-aliasing in the smoothscale/LANCZOS pipeline.
    gem = pal["gem"]
    edge_w = max(1, m(2))
    for i, j in ((0, 1), (3, 4), (5, 6)):
        pygame.draw.line(dz, (*gem, 80),
                         (int(oct8[i][0]), int(oct8[i][1])),
                         (int(oct8[j][0]), int(oct8[j][1])),
                         edge_w)
    # ONE bright girdle-glint on the upper-left facet catch — 2 extra device px
    # so the catch survives the downscale as a single legible highlight.
    pygame.draw.line(dz, (140, 120, 180, 150),
                     (int(oct8[6][0]), int(oct8[6][1])),
                     (int(oct8[7][0]), int(oct8[7][1])),
                     max(2, m(2)))
    big.blit(dz, (0, 0))


# ── Zone A — cool-platinum channel-set price chip ────────────────────────────
def zone_a(big, price, pal):
    r = pygame.Rect(0, 0, m(160), m(28))
    r.center = (m(CX), m(CHIP_CY))
    # 3-stop blue-steel gradient: higher mids and b-channel dominant so this
    # samples clearly cooler and lighter than LEGENDARY amber at 1×.
    _dark_chip_body(big, r, m(11),
                    [(0.0, (86, 94, 116)), (0.5, (60, 68, 88)), (1.0, (40, 46, 64))],
                    (24, 28, 40), (196, 206, 224))

    # coin + numeral inline at centre
    txt = f"{price}"
    nf = font(20)
    base = _stamp_bold(_glyph_base(txt, nf, 0), m(0.9))
    bw, bh = base.get_size()
    coin_r = m(12)
    gap = m(8)
    total = coin_r * 2 + gap + bw
    left = m(CX) - total // 2
    coin_cx = left + coin_r
    coin_glyph(big, coin_cx, m(CHIP_CY), coin_r)
    num_cx = left + coin_r * 2 + gap + bw // 2
    r2 = base.get_rect(center=(num_cx, m(CHIP_CY)))
    kl = base.copy()
    kl.fill((8, 6, 18, 255), special_flags=pygame.BLEND_RGBA_MULT)
    for ang in range(0, 360, 45):
        dx = int(round(m(1.2) * math.cos(math.radians(ang))))
        dy = int(round(m(1.2) * math.sin(math.radians(ang))))
        big.blit(kl, (r2.x + dx, r2.y + dy))
    fill = vgrad_stops(bw, bh, 0, PRICE_STOPS, 255)
    gold = base.copy()
    gold.blit(fill, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    big.blit(gold, r2)

    # ONE facet_gem per side at r=m(5) so the tier colour registers beyond the
    # specular hotspot — seated well inside the chip, flanking the coin/numeral.
    pip_r = m(5)
    cy_pip = m(CHIP_CY)
    facet_gem(big, m(55), cy_pip, pip_r, pal["gem"], pal["deep"])
    facet_gem(big, m(205), cy_pip, pip_r, pal["gem"], pal["deep"])


# ── shelf + buttons ───────────────────────────────────────────────────────────
def shelf(big):
    shelf_rect = pygame.Rect(m(SHELF_X), m(SHELF_Y), m(SHELF_W), m(SHELF_H))
    shelf_rad = m(CARD_RAD)
    shelf_stops = [(0.0, (34, 36, 72)), (0.5, (22, 24, 54)), (1.0, (12, 14, 36))]
    sh = vgrad_stops(shelf_rect.w, shelf_rect.h, 0, shelf_stops, 255).copy()
    smask = pygame.Surface(shelf_rect.size, pygame.SRCALPHA)
    pygame.draw.rect(smask, (255, 255, 255, 255), smask.get_rect(),
                     border_bottom_left_radius=shelf_rad,
                     border_bottom_right_radius=shelf_rad)
    sh.blit(smask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    top_sheen(sh, sh.get_rect(), 0, m(20), peak=35)
    pygame.draw.line(sh, (115, 106, 140), (0, 0), (shelf_rect.w - 1, 0), max(1, m(1)))
    seat = pygame.Surface((shelf_rect.w, m(6)), pygame.SRCALPHA)
    for yy in range(m(6)):
        a = int(120 * (1 - yy / m(6)))
        pygame.draw.line(seat, (0, 0, 0, a), (0, yy), (shelf_rect.w - 1, yy))
    big.blit(seat, (shelf_rect.x, shelf_rect.y - m(6)))
    big.blit(sh, shelf_rect.topleft)


def buttons(big):
    br = m(BTN_RAD)
    # BUY gets a steel-blue-to-purple gradient at roughly 2.5× the luminance of
    # CANCEL so the purchase action is unmistakably the visual hero.  CANCEL stays
    # at the existing cool dark and recedes.
    for cx_b, lbl, stops, lab_c, pk, rw in [
        (m(BUY_CX), "BUY",
         [(0.0, (76, 82, 168)), (1.0, (52, 48, 128))],
         (225, 218, 252), 32, m(2.0)),
        (m(CAN_CX), "CANCEL",
         [(0.0, (26, 28, 64)), (1.0, (14, 16, 44))],
         (150, 155, 200), 14, m(2.2)),
    ]:
        r = pygame.Rect(0, 0, m(BTN_W), m(BTN_H))
        r.center = (cx_b, m(BTN_CY))
        drop_shadow(big, r, br, blur=m(3), alpha=100, dy=m(2))
        big.blit(vgrad_stops(r.w, r.h, br, stops, 255), r.topleft)
        top_sheen(big, r, br, m(12), peak=pk)
        bevel_rim(big, r, br, sc.CARD_RING_DEEP, (*sc.CARD_RING_BRIGHT, 230),
                  w=max(1, rw))
        plain_text(big, lbl, font(14 if lbl == "BUY" else 13), r.center, lab_c,
                   shadow_a=110, weight=m(0.8), keyline=(8, 6, 20), kw=m(0.9))


# ── Zone B — rarity lozenge, big bottom gems only ────────────────────────────
def zone_b(big, tier_word, pal):
    # bottom gem pair first (they sit under the lozenge ends)
    for gx in [m(GEM_L_X), m(GEM_R_X)]:
        _alpha_aura(big, gx, m(BOT_GEM_CY), m(16), pal["glow"], peak=60, layers=14)
        facet_gem(big, gx, m(BOT_GEM_CY), m(GEM_R), pal["gem"], pal["deep"])
    _ribbon_lozenge(big, tier_word, m(CX), m(Y_BANNER), m(BANNER_W), pal)
    # small end-cap gems removed — the big bottom gems at x=43/217 are the
    # established game DNA and must read as the sole accent at this level.


# ── hero cabochon disc ────────────────────────────────────────────────────────
def hero(big, sid, pal):
    cx, cy, r = m(CX), m(DISC_CY), m(R_HERO)
    _alpha_aura(big, cx, cy, r + m(55), pal["glow"], peak=95, layers=24)
    _alpha_aura(big, cx, cy, r + m(20), pal["glow"], peak=70, layers=12)
    cabochon(big, cx, cy, r, sc.CABO_LO, sc.CABO_HI, ring=pal["gem"], ring_a=50)
    try:
        blit_thumb(big, sid, cx, cy, int(r * 1.5))
    except Exception:
        pygame.draw.circle(big, pal["gem"], (cx, cy), int(r * 0.7))
    cabochon_glass(big, cx, cy, r, tint=pal["gem"])
    # ONE crisp tier ring at the girdle — no stacked halos.
    ring = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)
    pygame.draw.circle(ring, (*pal["gem"], 150), (cx, cy), r, max(1, m(1)))
    big.blit(ring, (0, 0))


def render_popup(tier_word, sid, price):
    pal = PALETTES[tier_word]
    big = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)
    card_body(big, pal)
    corner_gems(big, pal)
    name_text(big, NAMES[tier_word])
    zone_a(big, price, pal)
    dead_zone(big, pal)
    shelf(big)
    buttons(big)
    zone_b(big, tier_word, pal)
    hero(big, sid, pal)
    return pygame.transform.smoothscale(big, (POP_W, POP_H))


MARGIN, HEAD, GAP = 20, 58, 12
canvas_w = MARGIN * 2 + POP_W * 3 + GAP * 2
canvas_h = HEAD + MARGIN + POP_H
strip = Image.new("RGB", (canvas_w, canvas_h), (8, 8, 20))
idr = ImageDraw.Draw(strip)
idr.text((MARGIN, 20), "lapidary-vault  ·  confirm_purchase_v8  ·  premium-v1  ·  round_2",
         fill=(232, 226, 208))
for i, (tw, sid, ps) in enumerate(TIERS):
    pop = render_popup(tw, sid, ps)
    pil = Image.frombytes("RGB", (POP_W, POP_H), pygame.image.tostring(pop, "RGB"))
    x = MARGIN + i * (POP_W + GAP)
    strip.paste(pil, (x, HEAD))
    idr.text((x + POP_W // 2, HEAD + POP_H + 6), tw, fill=(180, 176, 210), anchor="mt")
out = strip.resize((canvas_w * 2, canvas_h * 2), Image.LANCZOS)

import pathlib
OUTDIR = "/home/user/skybit/docs/confirm_purchase_v8/premium-v1/lapidary-vault"
pathlib.Path(OUTDIR).mkdir(parents=True, exist_ok=True)
OUT = OUTDIR + "/round_2.png"
out.save(OUT)
print(f"saved {out.size[0]}x{out.size[1]}  ->  {OUT}")
